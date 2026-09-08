"""
Driver MongoDB — OP_MSG sobre BSON, falado direto.

Desde a versao 3.6 o Mongo tem um comando so: OP_MSG. Um cabecalho de
16 bytes, uma bandeira de 4, e um documento BSON que E o comando. Achar
um documento, criar um indice, autenticar — tudo e um documento com um
nome de comando na primeira chave.

Essa uniformidade e o que faz este driver caber em 400 linhas: nao ha
um formato por operacao, ha um formato.

─── Autenticacao ───────────────────────────────────────────

SCRAM-SHA-256, o mesmo de 'protocolo.py' que o PostgreSQL usa. O Mongo
o embrulha em comandos ('saslStart', 'saslContinue') em vez de
mensagens proprias, mas o algoritmo e identico.

Uma diferenca que morde: no Mongo o SCRAM-SHA-1 usa a senha
pre-processada como MD5(usuario:mongo:senha), heranca do MONGODB-CR
que veio antes. O SHA-256 usa a senha direta. Trocar os dois faz a
autenticacao falhar com "authentication failed" e nenhuma pista.
"""

import hashlib
import struct

from . import bson
from .bson import ObjectId
from .protocolo import Canal, Scram, _b64d, _b64e
from ...errors import (AuthenticationError, ConnectionError_, ConstraintError,
                       DatabaseError, QueryError, StateError,
                       RecordNotFoundError)


OP_MSG = 2013

#: Codigo do erro -> classe da linguagem.
CODIGOS = {
    11000: ConstraintError,   # chave duplicada
    11001: ConstraintError,
    13: AuthenticationError,  # nao autorizado
    18: AuthenticationError,  # falha de autenticacao
    26: QueryError,           # namespace nao existe
    2: QueryError,            # argumento invalido
    9: QueryError,            # comando mal formado
}


class Mongo:
    """Uma conexao MongoDB."""

    def __init__(self, host="localhost", porta=27017, usuario="", senha="",
                 banco="admin", tls=False, prazo=10.0, autenticar_em=""):
        self.host = host
        self.porta = porta
        self.banco = banco or "admin"
        self.canal = Canal(host, porta, prazo, tls=tls)
        self.pedido = 0
        self.versao_servidor = ""
        self._fechado = False

        self._apresentar()
        if usuario:
            self._autenticar(usuario, senha, autenticar_em or self.banco)

    # ── mensagens ───────────────────────────────────────────

    def _enviar(self, documento, banco=None):
        """OP_MSG: cabecalho, bandeiras, e o documento como corpo."""
        documento = dict(documento)
        documento.setdefault("$db", banco or self.banco)
        corpo = b"\x00\x00\x00\x00" + b"\x00" + bson.codificar(documento)

        self.pedido += 1
        cabecalho = struct.pack("<iiii", len(corpo) + 16, self.pedido, 0, OP_MSG)
        self.canal.escrever(cabecalho + corpo)

    def _receber(self):
        cabecalho = self.canal.ler(16)
        tamanho, _, _, codigo = struct.unpack("<iiii", cabecalho)
        corpo = self.canal.ler(tamanho - 16)

        if codigo != OP_MSG:
            raise DatabaseError(
                f"the server answered with opcode {codigo}, not OP_MSG.",
                nota="MongoDB before 3.6 spoke a different protocol",
                doc="banco-de-dados")

        i = 4                                        # bandeiras
        secoes = {}
        while i < len(corpo):
            tipo = corpo[i]
            i += 1
            if tipo == 0:                            # o documento principal
                n = struct.unpack_from("<i", corpo, i)[0]
                secoes = bson.decodificar(corpo[i:i + n])
                i += n
            elif tipo == 1:                          # sequencia de documentos
                n = struct.unpack_from("<i", corpo, i)[0]
                i += n
            else:
                break
        return secoes

    def comando(self, documento, banco=None):
        """Manda um comando e devolve a resposta, ja conferida."""
        if self._fechado:
            raise StateError("this MongoDB connection is closed.",
                             dica="open a new one with Forge.conectar(...)",
                             doc="banco-de-dados")
        self._enviar(documento, banco)
        resposta = self._receber()
        self._conferir(resposta, documento)
        return resposta

    @staticmethod
    def _conferir(resposta, enviado):
        """'ok: 0' e como o Mongo diz que falhou."""
        if resposta.get("ok") in (1, 1.0, True):
            # Uma escrita pode ter 'ok: 1' e ainda ter falhado por
            # item: e assim que um insertMany parcial se reporta.
            erros = resposta.get("writeErrors") or []
            if erros:
                primeiro = erros[0]
                codigo = primeiro.get("code", 0)
                classe = CODIGOS.get(codigo, QueryError)
                raise classe(
                    primeiro.get("errmsg", "the write was rejected"),
                    nota=(f"MongoDB code {codigo}"
                          + (f"; {len(erros)} of the documents failed"
                             if len(erros) > 1 else "")),
                    doc="banco-de-dados")
            return

        codigo = resposta.get("code", 0)
        classe = CODIGOS.get(codigo, QueryError)
        nome = next(iter(enviado), "command")
        raise classe(
            resposta.get("errmsg", f"'{nome}' failed"),
            nota=f"MongoDB code {codigo}" if codigo else "",
            doc="banco-de-dados")

    # ── apresentacao ────────────────────────────────────────

    def _apresentar(self):
        resposta = self.comando({"hello": 1, "client": {
            "driver": {"name": "dataforge-forge", "version": "1.0.0"},
            "os": {"type": "any"},
        }}, banco="admin")
        self.wire = resposta.get("maxWireVersion", 0)
        detalhe = self.comando({"buildInfo": 1}, banco="admin")
        self.versao_servidor = detalhe.get("version", "")

    def _autenticar(self, usuario, senha, banco):
        scram = Scram(usuario, senha, "SCRAM-SHA-256")
        primeira = scram.primeiro().encode()

        try:
            inicio = self.comando({
                "saslStart": 1,
                "mechanism": "SCRAM-SHA-256",
                "payload": primeira,
                "options": {"skipEmptyExchange": True},
            }, banco=banco)
        except (AuthenticationError, QueryError):
            return self._autenticar_sha1(usuario, senha, banco)

        desafio = inicio["payload"].decode()
        final = scram.final(desafio).encode()
        continua = self.comando({
            "saslContinue": 1,
            "conversationId": inicio["conversationId"],
            "payload": final,
        }, banco=banco)

        if not continua.get("done"):
            resposta = continua["payload"].decode()
            scram.conferir(resposta)
            self.comando({
                "saslContinue": 1,
                "conversationId": inicio["conversationId"],
                "payload": b"",
            }, banco=banco)
        else:
            scram.conferir(continua["payload"].decode())

    def _autenticar_sha1(self, usuario, senha, banco):
        """SCRAM-SHA-1, para servidor antigo.

        A senha aqui nao e a senha: e MD5('usuario:mongo:senha'),
        heranca do MONGODB-CR. Usar a senha direta faz a autenticacao
        falhar sem dizer por que.
        """
        digerida = hashlib.md5(
            f"{usuario}:mongo:{senha}".encode("utf-8")).hexdigest()
        scram = Scram(usuario, digerida, "SCRAM-SHA-1")
        inicio = self.comando({
            "saslStart": 1, "mechanism": "SCRAM-SHA-1",
            "payload": scram.primeiro().encode(),
        }, banco=banco)
        final = scram.final(inicio["payload"].decode()).encode()
        continua = self.comando({
            "saslContinue": 1,
            "conversationId": inicio["conversationId"],
            "payload": final,
        }, banco=banco)
        if not continua.get("done"):
            scram.conferir(continua["payload"].decode())
            self.comando({"saslContinue": 1,
                          "conversationId": inicio["conversationId"],
                          "payload": b""}, banco=banco)

    # ── operacoes ───────────────────────────────────────────

    def inserir(self, colecao, documentos):
        """Insere um ou varios; devolve os _id gerados."""
        if isinstance(documentos, dict):
            documentos = [documentos]
        documentos = [dict(d) for d in documentos]
        for d in documentos:
            d.setdefault("_id", ObjectId())

        resposta = self.comando({
            "insert": colecao,
            "documents": documentos,
            "ordered": True,
        })
        return {"inseridos": resposta.get("n", 0),
                "ids": [str(d["_id"]) for d in documentos]}

    def achar(self, colecao, filtro=None, projecao=None, ordem=None,
              limite=0, pular=0):
        """Encontra documentos. Devolve uma lista de vaults."""
        comando = {"find": colecao, "filter": self._preparar(filtro or {})}
        if projecao:
            comando["projection"] = projecao
        if ordem:
            comando["sort"] = ordem
        if limite:
            comando["limit"] = int(limite)
        if pular:
            comando["skip"] = int(pular)

        resposta = self.comando(comando)
        cursor = resposta.get("cursor", {})
        lote = list(cursor.get("firstBatch", []))

        # Um cursor com id != 0 tem mais lotes. Ignorar isso devolve so
        # os primeiros 101 documentos — o tamanho do lote inicial — e o
        # bug so aparece quando a colecao cresce.
        id_cursor = cursor.get("id", 0)
        while id_cursor:
            proximo = self.comando({
                "getMore": id_cursor, "collection": colecao})
            interno = proximo.get("cursor", {})
            lote.extend(interno.get("nextBatch", []))
            id_cursor = interno.get("id", 0)
            if limite and len(lote) >= limite:
                break

        return [bson.para_json(d) for d in lote]

    def achar_um(self, colecao, filtro=None, projecao=None):
        achados = self.achar(colecao, filtro, projecao, limite=1)
        return achados[0] if achados else None

    def atualizar(self, colecao, filtro, mudancas, varios=False,
                  criar_se_faltar=False):
        # Sem um operador ('$set', '$inc'), o Mongo SUBSTITUI o
        # documento inteiro — e apaga os campos que nao vieram. Quase
        # ninguem quer isso, entao envolvemos em '$set'.
        if not any(str(k).startswith("$") for k in mudancas):
            mudancas = {"$set": mudancas}

        resposta = self.comando({
            "update": colecao,
            "updates": [{
                "q": self._preparar(filtro),
                "u": mudancas,
                "multi": bool(varios),
                "upsert": bool(criar_se_faltar),
            }],
        })
        return {"encontrados": resposta.get("n", 0),
                "alterados": resposta.get("nModified", 0)}

    def remover(self, colecao, filtro, varios=False):
        resposta = self.comando({
            "delete": colecao,
            "deletes": [{"q": self._preparar(filtro),
                         "limit": 0 if varios else 1}],
        })
        return resposta.get("n", 0)

    def contar(self, colecao, filtro=None):
        resposta = self.comando({
            "count": colecao, "query": self._preparar(filtro or {})})
        return resposta.get("n", 0)

    def agregar(self, colecao, etapas, tamanho_lote=101):
        resposta = self.comando({
            "aggregate": colecao,
            "pipeline": list(etapas),
            "cursor": {"batchSize": tamanho_lote},
        })
        cursor = resposta.get("cursor", {})
        lote = list(cursor.get("firstBatch", []))
        id_cursor = cursor.get("id", 0)
        while id_cursor:
            proximo = self.comando({"getMore": id_cursor,
                                    "collection": colecao})
            interno = proximo.get("cursor", {})
            lote.extend(interno.get("nextBatch", []))
            id_cursor = interno.get("id", 0)
        return [bson.para_json(d) for d in lote]

    def distintos(self, colecao, campo, filtro=None):
        resposta = self.comando({
            "distinct": colecao, "key": campo,
            "query": self._preparar(filtro or {})})
        return bson.para_json(resposta.get("values", []))

    # ── esquema ─────────────────────────────────────────────

    def colecoes(self):
        resposta = self.comando({"listCollections": 1, "nameOnly": True})
        return [d["name"] for d in resposta.get("cursor", {}).get(
            "firstBatch", [])]

    def criar_indice(self, colecao, campos, unico=False, nome=""):
        chaves = ({campos: 1} if isinstance(campos, str)
                  else dict(campos) if isinstance(campos, dict)
                  else {c: 1 for c in campos})
        indice = {"key": chaves,
                  "name": nome or "_".join(f"{k}_{v}" for k, v in chaves.items())}
        if unico:
            indice["unique"] = True
        self.comando({"createIndexes": colecao, "indexes": [indice]})
        return indice["name"]

    def indices(self, colecao):
        resposta = self.comando({"listIndexes": colecao})
        return [bson.para_json(d)
                for d in resposta.get("cursor", {}).get("firstBatch", [])]

    def apagar_colecao(self, colecao):
        try:
            self.comando({"drop": colecao})
            return True
        except QueryError:
            return False                             # nao existia

    # ── utilidades ──────────────────────────────────────────

    @staticmethod
    def _preparar(filtro):
        """Converte o que o DataForge escreve para o que o BSON aceita.

        O caso que sempre aparece: '{"_id": "6a9f..."}'. O usuario tem
        o id como texto, porque foi assim que ele saiu; o Mongo so
        encontra por ObjectId. Sem esta conversao, a busca por id nunca
        acha nada — e nao ha erro, so um resultado vazio.
        """
        if not isinstance(filtro, dict):
            return filtro
        saida = {}
        for chave, valor in filtro.items():
            if chave == "_id" and isinstance(valor, str) and len(valor) == 24:
                try:
                    saida[chave] = ObjectId(valor)
                    continue
                except Exception:                    # noqa: BLE001
                    pass
            if isinstance(valor, dict):
                saida[chave] = Mongo._preparar(valor)
            elif isinstance(valor, list):
                saida[chave] = [Mongo._preparar(v) if isinstance(v, dict)
                                else v for v in valor]
            else:
                saida[chave] = valor
        return saida

    def ping(self):
        return self.comando({"ping": 1}, banco="admin").get("ok") in (1, 1.0)

    def versao(self):
        return self.versao_servidor

    def estatisticas(self):
        return bson.para_json(self.comando({"dbStats": 1}))

    def fechar(self):
        if self._fechado:
            return
        self._fechado = True
        self.canal.fechar()

    # ── a interface comum ───────────────────────────────────
    #
    # Mongo nao tem SQL. 'consultar' aceita o documento de comando
    # direto, para o codigo generico nao quebrar ao trocar de motor.

    def consultar(self, comando, parametros=None):
        if isinstance(comando, str):
            return self.achar(comando, parametros or {})
        return [bson.para_json(self.comando(comando))]

    def executar(self, comando, parametros=None):
        return self.consultar(comando, parametros)

    @property
    def dialeto(self):
        return "mongo"
