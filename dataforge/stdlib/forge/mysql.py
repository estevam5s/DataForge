"""
Driver MySQL e MariaDB — protocolo cliente/servidor, falado direto.

O protocolo do MySQL e uma sequencia de pacotes: tres bytes de tamanho
(little-endian), um de numero de sequencia, e o corpo. Sobre isso,
duas fases: o aperto de mao com autenticacao, e depois comandos.

MariaDB nasceu de um fork do MySQL e manteve o protocolo compativel; o
mesmo driver serve os dois. O que muda e o metodo de autenticacao
padrao — e e ai que mora a dificuldade.

─── Autenticacao ───────────────────────────────────────────

    mysql_native_password   SHA1 triplo, com o desafio do servidor
    caching_sha2_password   o padrao do MySQL 8

O 'caching_sha2' tem dois caminhos: o rapido, quando o servidor ja tem
a senha em cache, e o completo, que exige canal seguro — TLS, ou troca
de chave RSA. O driver faz o rapido e o completo por RSA; sem isso,
conectar no MySQL 8 recem-instalado simplesmente nao funciona, que e
onde a maioria dos drivers caseiros para.
"""

import hashlib
import os
import struct

from .protocolo import Canal, des_le32
from ...errors import (AuthenticationError, ConnectionError_, ConstraintError,
                       DatabaseError, QueryError, StateError,
                       TransactionError)


#: Bandeiras que o cliente declara. Cada uma muda o formato do que vem
#: depois, entao pedir o que nao se sabe ler quebra o driver.
CLIENT_LONG_PASSWORD = 0x00000001
CLIENT_FOUND_ROWS = 0x00000002
CLIENT_LONG_FLAG = 0x00000004
CLIENT_CONNECT_WITH_DB = 0x00000008
CLIENT_LOCAL_FILES = 0x00000080
CLIENT_PROTOCOL_41 = 0x00000200
CLIENT_INTERACTIVE = 0x00000400
CLIENT_SSL = 0x00000800
CLIENT_TRANSACTIONS = 0x00002000
CLIENT_SECURE_CONNECTION = 0x00008000
CLIENT_MULTI_STATEMENTS = 0x00010000
CLIENT_MULTI_RESULTS = 0x00020000
CLIENT_PLUGIN_AUTH = 0x00080000
CLIENT_CONNECT_ATTRS = 0x00100000
CLIENT_PLUGIN_AUTH_LENENC_DATA = 0x00200000
CLIENT_DEPRECATE_EOF = 0x01000000

#: Numero do erro -> classe da linguagem.
ERROS = {
    1062: ConstraintError,   # duplicate entry
    1451: ConstraintError,   # foreign key: linha referenciada
    1452: ConstraintError,   # foreign key: sem destino
    1048: ConstraintError,   # coluna nao aceita nulo
    1045: AuthenticationError,
    1044: AuthenticationError,
    1049: DatabaseError,     # banco desconhecido
    1146: QueryError,        # tabela nao existe
    1054: QueryError,        # coluna nao existe
    1064: QueryError,        # erro de sintaxe
    1213: TransactionError,  # deadlock
    1205: TransactionError,  # timeout esperando lock
}

#: Tipo da coluna -> conversor. Sem isto, 'idade' volta como texto e
#: 'idade + 1' concatena em vez de somar.
TIPOS_INTEIROS = {1, 2, 3, 8, 9, 13}          # tiny, short, long, longlong…
TIPOS_REAIS = {4, 5, 0, 246}                  # float, double, decimal, newdecimal
TIPOS_BINARIOS = {249, 250, 251, 252}         # os blobs
TIPO_JSON = 245
TIPO_BIT = 16


class MySQL:
    """Uma conexao MySQL ou MariaDB."""

    def __init__(self, host="localhost", porta=3306, usuario="root",
                 senha="", banco="", tls=False, prazo=10.0, sabor="mysql"):
        self.host = host
        self.porta = porta
        self.usuario = usuario
        self.banco = banco
        self.sabor = sabor
        self.canal = Canal(host, porta, prazo)
        self.sequencia = 0
        self.versao_servidor = ""
        self.em_transacao = False
        self._fechado = False
        self._ultimo_id = 0

        self._apresentar(senha, tls)

    # ── pacotes ─────────────────────────────────────────────

    def _enviar(self, corpo):
        cabecalho = struct.pack("<I", len(corpo))[:3] + bytes([self.sequencia])
        self.canal.escrever(cabecalho + corpo)
        self.sequencia = (self.sequencia + 1) % 256

    def _receber(self):
        cabecalho = self.canal.ler(4)
        tamanho = cabecalho[0] | (cabecalho[1] << 8) | (cabecalho[2] << 16)
        self.sequencia = (cabecalho[3] + 1) % 256
        corpo = self.canal.ler(tamanho)
        # Um pacote de 16MB tem continuacao: o protocolo quebra o que
        # nao cabe em 0xFFFFFF, e quem ignora isso perde dados grandes
        # em silencio.
        while tamanho == 0xFFFFFF:
            cabecalho = self.canal.ler(4)
            tamanho = cabecalho[0] | (cabecalho[1] << 8) | (cabecalho[2] << 16)
            self.sequencia = (cabecalho[3] + 1) % 256
            corpo += self.canal.ler(tamanho)
        return corpo

    # ── apresentacao ────────────────────────────────────────

    def _apresentar(self, senha, tls):
        saudacao = self._receber()
        if saudacao[:1] == b"\xff":
            raise self._erro(saudacao)

        i = 1                                        # versao do protocolo
        fim = saudacao.index(b"\x00", i)
        self.versao_servidor = saudacao[i:fim].decode("utf-8", "replace")
        i = fim + 1
        i += 4                                       # id da conexao
        desafio = saudacao[i:i + 8]
        i += 8 + 1                                   # e o zero de enchimento
        capacidades = saudacao[i] | (saudacao[i + 1] << 8)
        i += 2

        plugin = "mysql_native_password"
        if len(saudacao) > i:
            i += 1                                   # charset
            i += 2                                   # status
            capacidades |= (saudacao[i] | (saudacao[i + 1] << 8)) << 16
            i += 2
            tamanho_desafio = saudacao[i]
            i += 1
            i += 10                                  # reservado
            resto = max(13, tamanho_desafio - 8)
            desafio += saudacao[i:i + resto - 1]
            i += resto
            if len(saudacao) > i:
                fim = saudacao.find(b"\x00", i)
                plugin = saudacao[i:fim if fim > 0 else len(saudacao)].decode(
                    "utf-8", "replace")

        bandeiras = (CLIENT_PROTOCOL_41 | CLIENT_LONG_PASSWORD
                     | CLIENT_LONG_FLAG | CLIENT_SECURE_CONNECTION
                     | CLIENT_TRANSACTIONS | CLIENT_PLUGIN_AUTH
                     | CLIENT_MULTI_RESULTS | CLIENT_DEPRECATE_EOF)
        if self.banco:
            bandeiras |= CLIENT_CONNECT_WITH_DB

        resposta = self._provar(plugin, senha, desafio)

        corpo = struct.pack("<IIB", bandeiras, 16 * 1024 * 1024, 45)
        corpo += b"\x00" * 23
        corpo += self.usuario.encode("utf-8") + b"\x00"
        corpo += bytes([len(resposta)]) + resposta
        if self.banco:
            corpo += self.banco.encode("utf-8") + b"\x00"
        corpo += plugin.encode("utf-8") + b"\x00"
        self._enviar(corpo)

        self._terminar_autenticacao(senha, desafio)

    def _terminar_autenticacao(self, senha, desafio):
        """O vaivem que pode vir depois da primeira resposta."""
        for _ in range(6):                           # nunca passa de tres
            pacote = self._receber()
            marca = pacote[:1]

            if marca == b"\x00":                     # OK
                return
            if marca == b"\xff":
                raise self._erro(pacote)

            if marca == b"\x01":                     # caching_sha2 respondeu
                estado = pacote[1:2]
                if estado == b"\x03":                # cache acertou: pronto
                    continue
                if estado == b"\x04":                # cache errou: caminho completo
                    self._sha2_completo(senha, desafio)
                    continue
                # o resto e a chave publica RSA
                self._enviar(self._rsa(senha, desafio, pacote[1:]))
                continue

            if marca == b"\xfe":                     # trocar de metodo
                fim = pacote.find(b"\x00", 1)
                plugin = pacote[1:fim].decode("utf-8", "replace")
                novo_desafio = pacote[fim + 1:].rstrip(b"\x00")
                self._enviar(self._provar(plugin, senha, novo_desafio or desafio))
                desafio = novo_desafio or desafio
                continue

            return

        raise AuthenticationError(
            "the authentication handshake did not settle.",
            nota="the server kept asking for a different method",
            doc="banco-de-dados")

    def _sha2_completo(self, senha, desafio):
        """Sem TLS, a senha so viaja cifrada com a chave publica do servidor."""
        self._enviar(b"\x02")                        # pede a chave publica
        pacote = self._receber()
        if pacote[:1] == b"\xff":
            raise self._erro(pacote)
        self._enviar(self._rsa(senha, desafio, pacote[1:]))

    def _rsa(self, senha, desafio, chave_pem):
        """A senha cifrada com a chave publica do servidor.

        O MySQL 8 pede isto quando o cache dele nao tem a senha e o
        canal nao e TLS: a senha (com um zero no fim), XOR do desafio,
        cifrada em RSA-OAEP.

        O XOR antes de cifrar e o que impede reenvio: cada conexao tem
        desafio diferente, entao o mesmo texto cifrado nunca serve
        duas vezes.
        """
        from .rsa import cifrar

        bruta = senha.encode("utf-8") + b"\x00"
        semente = desafio[:20]
        mascarada = bytes(c ^ semente[i % len(semente)]
                          for i, c in enumerate(bruta))
        return cifrar(mascarada, chave_pem)

    @staticmethod
    def _provar(plugin, senha, desafio):
        """A prova de que sabemos a senha, no formato que o plugin pede."""
        if not senha:
            return b""

        bruta = senha.encode("utf-8")

        if plugin == "caching_sha2_password":
            # XOR(SHA256(senha), SHA256(SHA256(SHA256(senha)) + desafio))
            um = hashlib.sha256(bruta).digest()
            dois = hashlib.sha256(um).digest()
            tres = hashlib.sha256(dois + desafio[:20]).digest()
            return bytes(a ^ b for a, b in zip(um, tres))

        # mysql_native_password:
        # XOR(SHA1(senha), SHA1(desafio + SHA1(SHA1(senha))))
        um = hashlib.sha1(bruta).digest()
        dois = hashlib.sha1(um).digest()
        tres = hashlib.sha1(desafio[:20] + dois).digest()
        return bytes(a ^ b for a, b in zip(um, tres))

    # ── erros ───────────────────────────────────────────────

    def _erro(self, pacote):
        numero = pacote[1] | (pacote[2] << 8)
        corpo = pacote[3:]
        estado = ""
        if corpo[:1] == b"#":
            estado = corpo[1:6].decode("utf-8", "replace")
            corpo = corpo[6:]
        mensagem = corpo.decode("utf-8", "replace")

        classe = ERROS.get(numero, QueryError)
        nota = f"MySQL error {numero}" + (f", SQLSTATE {estado}" if estado else "")
        dica = ""
        if numero == 1045:
            dica = "check the user and password in the URL"
        elif numero == 1049:
            dica = "create the database first, or fix the name in the URL"
        elif numero == 1062:
            dica = "check for an existing row before inserting"
        return classe(mensagem, nota=nota, dica=dica, doc="banco-de-dados")

    # ── inteiros de tamanho variavel ────────────────────────

    @staticmethod
    def _ler_lenenc(dados, i):
        """O inteiro de tamanho variavel do MySQL."""
        primeiro = dados[i]
        if primeiro < 0xFB:
            return primeiro, i + 1
        if primeiro == 0xFB:
            return None, i + 1                       # NULL
        if primeiro == 0xFC:
            return dados[i + 1] | (dados[i + 2] << 8), i + 3
        if primeiro == 0xFD:
            return (dados[i + 1] | (dados[i + 2] << 8)
                    | (dados[i + 3] << 16)), i + 4
        return struct.unpack_from("<Q", dados, i + 1)[0], i + 9

    @classmethod
    def _ler_texto(cls, dados, i):
        tamanho, i = cls._ler_lenenc(dados, i)
        if tamanho is None:
            return None, i
        return dados[i:i + tamanho], i + tamanho

    # ── consultas ───────────────────────────────────────────

    def consultar(self, sql, parametros=None):
        colunas, linhas, _ = self._executar(sql, parametros)
        return [dict(zip(colunas, linha)) for linha in linhas]

    def executar(self, sql, parametros=None):
        _, _, afetadas = self._executar(sql, parametros)
        return afetadas

    def _executar(self, sql, parametros=None):
        if self._fechado:
            raise StateError("this MySQL connection is closed.",
                             dica="open a new one with Forge.conectar(...)",
                             doc="banco-de-dados")

        if parametros:
            sql = self._interpolar(sql, parametros)

        self.sequencia = 0
        self._enviar(b"\x03" + sql.encode("utf-8"))
        return self._colher()

    def _interpolar(self, sql, parametros):
        """Escapa os valores e os poe no lugar dos '?'.

        O ideal seria a instrucao preparada (COM_STMT_PREPARE), que
        manda valor e consulta separados. Ela custa duas idas ao
        servidor por consulta, e o protocolo binario de resposta e
        outro parser inteiro.
        
        O escape aqui e o do proprio MySQL, aplicado a TODOS os
        caracteres perigosos — inclusive os que so importam em
        conjuntos multibyte. Um '?' dentro de literal de texto e
        respeitado, entao 'where nome = "a?b"' nao vira parametro.
        """
        pedacos, i, restantes = [], 0, list(parametros)
        aspas = None
        for c in sql:
            if aspas:
                pedacos.append(c)
                if c == aspas:
                    aspas = None
                continue
            if c in "'\"`":
                aspas = c
                pedacos.append(c)
            elif c == "?":
                if not restantes:
                    raise QueryError(
                        "there are more '?' in the SQL than values given.",
                        dica="count the placeholders against the list",
                        doc="banco-de-dados")
                pedacos.append(self._literal(restantes.pop(0)))
            else:
                pedacos.append(c)

        if restantes:
            raise QueryError(
                f"{len(restantes)} value(s) left over: the SQL has fewer '?'.",
                doc="banco-de-dados")
        return "".join(pedacos)

    @staticmethod
    def _literal(valor):
        import json
        if valor is None:
            return "NULL"
        if isinstance(valor, bool):
            return "1" if valor else "0"
        if isinstance(valor, (int, float)):
            return repr(valor)
        if isinstance(valor, bytes):
            return "X'" + valor.hex() + "'"
        if isinstance(valor, (list, dict, tuple)):
            valor = json.dumps(valor, ensure_ascii=False)

        texto = str(valor)
        saida = []
        for c in texto:
            if c == "\x00":
                saida.append("\\0")
            elif c == "\n":
                saida.append("\\n")
            elif c == "\r":
                saida.append("\\r")
            elif c == "\x1a":
                saida.append("\\Z")
            elif c in ("'", '"', "\\"):
                saida.append("\\" + c)
            else:
                saida.append(c)
        return "'" + "".join(saida) + "'"

    def _colher(self):
        pacote = self._receber()
        marca = pacote[:1]

        if marca == b"\xff":
            raise self._erro(pacote)

        if marca == b"\x00" or marca == b"\xfe":     # OK, sem resultado
            afetadas, i = self._ler_lenenc(pacote, 1)
            self._ultimo_id, _ = self._ler_lenenc(pacote, i)
            return [], [], afetadas or 0

        # Ha colunas: o primeiro pacote diz quantas.
        n_colunas, _ = self._ler_lenenc(pacote, 0)
        colunas, tipos = [], []
        for _ in range(n_colunas):
            nome, tipo = self._ler_definicao(self._receber())
            colunas.append(nome)
            tipos.append(tipo)

        linhas = []
        while True:
            pacote = self._receber()
            if pacote[:1] == b"\xff":
                raise self._erro(pacote)
            # Com DEPRECATE_EOF, o fim vem como OK comecando em 0xFE.
            if pacote[:1] == b"\xfe" and len(pacote) < 9:
                break
            linhas.append(self._ler_linha(pacote, tipos))

        return colunas, linhas, len(linhas)

    @classmethod
    def _ler_definicao(cls, pacote):
        """Do pacote de definicao, o nome e o tipo da coluna."""
        # Sao SEIS textos, nesta ordem: catalogo, banco, tabela, tabela
        # original, nome, nome original. Ler um a mais desalinha o
        # resto do pacote e o tipo sai de onde nao ha byte nenhum.
        i = 0
        for _ in range(4):                           # catalogo, banco, tabela, tabela original
            _, i = cls._ler_texto(pacote, i)
        nome, i = cls._ler_texto(pacote, i)          # o nome que interessa
        _, i = cls._ler_texto(pacote, i)             # nome original da coluna
        i += 1                                       # tamanho dos campos fixos (sempre 0x0c)
        i += 2                                       # charset
        i += 4                                       # tamanho da coluna
        tipo = pacote[i]
        return nome.decode("utf-8", "replace"), tipo

    @classmethod
    def _ler_linha(cls, pacote, tipos):
        valores, i = [], 0
        for coluna in range(len(tipos)):
            bruto, i = cls._ler_texto(pacote, i)
            valores.append(cls._converter(bruto, tipos[coluna]))
        return valores

    @staticmethod
    def _converter(bruto, tipo):
        if bruto is None:
            return None
        if tipo in TIPOS_BINARIOS and tipo != 252:
            return bruto
        texto = bruto.decode("utf-8", "replace")
        try:
            if tipo in TIPOS_INTEIROS:
                return int(texto)
            if tipo in TIPOS_REAIS:
                return float(texto)
            if tipo == TIPO_JSON:
                import json
                return json.loads(texto)
            if tipo == TIPO_BIT:
                return bool(bruto and bruto[0])
        except (ValueError, TypeError):
            pass
        return texto

    # ── transacoes ──────────────────────────────────────────

    def comecar(self, isolamento=""):
        if isolamento:
            self.executar(f"SET TRANSACTION ISOLATION LEVEL {isolamento}")
        self.executar("START TRANSACTION")
        self.em_transacao = True
        return self

    def confirmar(self):
        if not self.em_transacao:
            raise TransactionError(
                "there is no open transaction to commit.",
                dica="open one with  db.comecar()  first",
                doc="banco-de-dados")
        self.executar("COMMIT")
        self.em_transacao = False

    def desfazer(self):
        if not self.em_transacao:
            return
        self.executar("ROLLBACK")
        self.em_transacao = False

    # ── ciclo de vida ───────────────────────────────────────

    def ping(self):
        return self.consultar("select 1 as um")[0]["um"] == 1

    def versao(self):
        return self.versao_servidor

    def ultimo_id(self):
        """O id gerado pelo ultimo INSERT com auto_increment."""
        return self._ultimo_id

    def tabelas(self):
        linhas = self.consultar("show tables")
        return [list(l.values())[0] for l in linhas]

    def colunas(self, tabela):
        return self.consultar(
            "select column_name as nome, data_type as tipo, "
            "is_nullable as aceita_nulo, column_default as padrao "
            "from information_schema.columns "
            "where table_schema = database() and table_name = ? "
            "order by ordinal_position", [tabela])

    def fechar(self):
        if self._fechado:
            return
        self._fechado = True
        try:
            self.sequencia = 0
            self._enviar(b"\x01")                    # COM_QUIT
        except Exception:                            # noqa: BLE001
            pass
        self.canal.fechar()

    @property
    def dialeto(self):
        return self.sabor
