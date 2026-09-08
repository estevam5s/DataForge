"""
Driver PostgreSQL — protocolo de mensagens v3, falado direto.

O protocolo e uma sequencia de mensagens, cada uma com um byte de tipo,
um tamanho de 32 bits e o corpo. Duas fases:

    startup     apresentacao e autenticacao
    consulta    Query simples, ou Parse/Bind/Execute para parametrizada

O driver usa a **parametrizada** para tudo que leve valores. Nao e
preferencia de estilo: e o que impede injecao de SQL. Concatenar valor
em texto de consulta e o bug mais explorado da historia do software, e
um driver que facilita isso e um driver que colabora com ele.

─── Autenticacao ───────────────────────────────────────────

Suporta SCRAM-SHA-256 (o padrao desde a versao 14), MD5 e 'trust'. O
SCRAM esta em 'protocolo.py' porque o Mongo usa o mesmo.
"""

import hashlib

from .protocolo import (Canal, Scram, cstr, i16, i32, des_i16, des_i32,
                        ler_cstr, _b64d, _b64e)
from ...errors import (AuthenticationError, ConnectionError_, ConstraintError,
                       DatabaseError, QueryError, StateError,
                       TransactionError)


#: Codigo SQLSTATE -> classe de erro da linguagem. O que nao esta aqui
#: vira QueryError, que e o pai da familia.
SQLSTATE = {
    "23505": ConstraintError,   # unique_violation
    "23503": ConstraintError,   # foreign_key_violation
    "23502": ConstraintError,   # not_null_violation
    "23514": ConstraintError,   # check_violation
    "28P01": AuthenticationError,
    "28000": AuthenticationError,
    "3D000": DatabaseError,     # invalid_catalog_name
    "42601": QueryError,        # syntax_error
    "42P01": QueryError,        # undefined_table
    "42703": QueryError,        # undefined_column
    "25P02": TransactionError,  # in_failed_sql_transaction
    "40001": TransactionError,  # serialization_failure
    "40P01": TransactionError,  # deadlock_detected
}

#: OID do tipo -> como converter. O PostgreSQL manda tudo como texto no
#: formato 0; converter aqui e o que faz 'linha["idade"] + 1' funcionar
#: em vez de concatenar texto.
def _bool(v):
    return v == "t"


def _json(v):
    import json
    return json.loads(v)


def _cluster(v):
    """Um array do PostgreSQL: '{1,2,3}' -> [1, 2, 3]."""
    interno = v.strip()
    if not interno.startswith("{"):
        return v
    interno = interno[1:-1]
    if not interno:
        return []
    saida, atual, aspas, escapa = [], "", False, False
    for c in interno:
        if escapa:
            atual += c
            escapa = False
        elif c == "\\":
            escapa = True
        elif c == '"':
            aspas = not aspas
        elif c == "," and not aspas:
            saida.append(atual)
            atual = ""
        else:
            atual += c
    saida.append(atual)
    return [None if s == "NULL" else s for s in saida]


CONVERSORES = {
    16: _bool,                                       # bool
    20: int, 21: int, 23: int, 26: int,              # int8, int2, int4, oid
    700: float, 701: float, 1700: float,             # float4, float8, numeric
    114: _json, 3802: _json,                         # json, jsonb
    1000: _cluster, 1007: _cluster, 1016: _cluster,  # arrays
    1009: _cluster, 1015: _cluster,
}


class Postgres:
    """Uma conexao PostgreSQL."""

    def __init__(self, host="localhost", porta=5432, usuario="postgres",
                 senha="", banco="postgres", tls=False, prazo=10.0,
                 opcoes=None):
        self.host = host
        self.porta = porta
        self.usuario = usuario
        self.banco = banco
        self.canal = Canal(host, porta, prazo, tls=tls)
        self.parametros = {}
        self.pid = 0
        self.em_transacao = False
        self._fechado = False
        self._preparadas = {}
        self._contador = 0

        self._apresentar(senha, opcoes or {})

    # ── mensagens ───────────────────────────────────────────

    def _enviar(self, tipo, corpo=b""):
        """Uma mensagem: tipo, tamanho (que se inclui), corpo."""
        cabecalho = (tipo.encode() if tipo else b"") + i32(len(corpo) + 4)
        self.canal.escrever(cabecalho + corpo)

    def _receber(self):
        """(tipo, corpo) da proxima mensagem."""
        tipo = self.canal.ler(1).decode("latin-1")
        tamanho = des_i32(self.canal.ler(4))
        corpo = self.canal.ler(tamanho - 4) if tamanho > 4 else b""
        return tipo, corpo

    # ── apresentacao ────────────────────────────────────────

    def _apresentar(self, senha, opcoes):
        corpo = i32(196608)                          # versao 3.0
        corpo += cstr("user") + cstr(self.usuario)
        corpo += cstr("database") + cstr(self.banco)
        corpo += cstr("client_encoding") + cstr("UTF8")
        # 'application_name' aparece em pg_stat_activity: quando uma
        # consulta trava a producao, saber de onde ela veio poupa horas.
        corpo += cstr("application_name") + cstr(
            opcoes.get("app", "dataforge"))
        for chave, valor in opcoes.items():
            if chave != "app":
                corpo += cstr(chave) + cstr(str(valor))
        corpo += b"\x00"
        self._enviar("", corpo)                      # startup nao tem tipo

        while True:
            tipo, dados = self._receber()

            if tipo == "R":                          # autenticacao
                self._autenticar(dados, senha)
            elif tipo == "S":                        # parametro do servidor
                chave, i = ler_cstr(dados)
                valor, _ = ler_cstr(dados, i)
                self.parametros[chave] = valor
            elif tipo == "K":                        # chave de cancelamento
                self.pid = des_i32(dados)
            elif tipo == "Z":                        # pronto
                return
            elif tipo == "E":
                raise self._erro(dados)
            elif tipo == "N":                        # aviso; segue
                continue

    def _autenticar(self, dados, senha):
        codigo = des_i32(dados)

        if codigo == 0:                              # ok
            return
        if codigo == 3:                              # senha em texto
            self._enviar("p", cstr(senha))
        elif codigo == 5:                            # MD5
            sal = dados[4:8]
            interno = hashlib.md5(
                (senha + self.usuario).encode()).hexdigest()
            final = hashlib.md5(interno.encode() + sal).hexdigest()
            self._enviar("p", cstr("md5" + final))
        elif codigo == 10:                           # SASL: qual mecanismo
            mecanismos = []
            i = 4
            while i < len(dados) and dados[i] != 0:
                nome, i = ler_cstr(dados, i)
                mecanismos.append(nome)
            escolhido = ("SCRAM-SHA-256" if "SCRAM-SHA-256" in mecanismos
                         else (mecanismos[0] if mecanismos else ""))
            if not escolhido.startswith("SCRAM"):
                raise AuthenticationError(
                    f"the server asked for {mecanismos}, which the Forge "
                    f"does not speak.",
                    nota="it understands SCRAM-SHA-256, MD5 and trust",
                    doc="banco-de-dados")
            self._scram = Scram(self.usuario, senha, escolhido)
            primeira = self._scram.primeiro().encode()
            self._enviar("p", cstr(escolhido) + i32(len(primeira)) + primeira)
        elif codigo == 11:                           # SASL continua
            resposta = self._scram.final(dados[4:].decode())
            self._enviar("p", resposta.encode())
        elif codigo == 12:                           # SASL termina
            self._scram.conferir(dados[4:].decode())
        else:
            raise AuthenticationError(
                f"authentication method {codigo} is not supported.",
                nota="the Forge speaks SCRAM-SHA-256, MD5 and trust",
                doc="banco-de-dados")

    # ── erros ───────────────────────────────────────────────

    def _erro(self, dados):
        """A mensagem de erro do PostgreSQL, tipada e legivel.

        Ela vem em campos etiquetados; os que importam sao a mensagem,
        o codigo SQLSTATE (que da o tipo), o detalhe e a sugestao — que
        o proprio PostgreSQL costuma trazer, e que quase nenhum driver
        mostra.
        """
        campos = {}
        i = 0
        while i < len(dados) and dados[i] != 0:
            etiqueta = chr(dados[i])
            valor, i = ler_cstr(dados, i + 1)
            campos[etiqueta] = valor

        codigo = campos.get("C", "")
        classe = SQLSTATE.get(codigo, QueryError)
        mensagem = campos.get("M", "the database rejected the command")

        nota = campos.get("D", "")
        if campos.get("n"):                          # nome da restricao
            nota = (nota + f" (constraint: {campos['n']})").strip()
        if campos.get("P"):                          # posicao no SQL
            nota = (nota + f" at character {campos['P']}").strip()

        return classe(f"{mensagem}", nota=nota,
                      dica=campos.get("H", ""), doc="banco-de-dados")

    # ── consultas ───────────────────────────────────────────

    def consultar(self, sql, parametros=None):
        """SELECT — devolve uma lista de vaults, um por linha."""
        colunas, linhas, _ = self._executar(sql, parametros)
        return [dict(zip(colunas, linha)) for linha in linhas]

    def executar(self, sql, parametros=None):
        """INSERT/UPDATE/DELETE/DDL — devolve quantas linhas mudaram."""
        colunas, linhas, afetadas = self._executar(sql, parametros)
        if colunas:                                  # tinha RETURNING
            return [dict(zip(colunas, linha)) for linha in linhas]
        return afetadas

    def _executar(self, sql, parametros=None):
        self._garantir_aberta()

        if not parametros:
            return self._consulta_simples(sql)
        return self._consulta_parametrizada(sql, parametros)

    def _consulta_simples(self, sql):
        self._enviar("Q", cstr(sql))
        return self._colher()

    def _consulta_parametrizada(self, sql, parametros):
        """Parse/Bind/Describe/Execute/Sync — o caminho seguro.

        O valor nunca entra no texto da consulta: vai separado, e o
        servidor o trata como dado. Injecao de SQL deixa de ser
        possivel por construcao, e nao por disciplina de quem escreve.
        """
        sql = self._numerar(sql, len(parametros))
        nome = b""                                   # instrucao sem nome

        # Parse: o SQL, sem tipos declarados (o servidor infere).
        self._enviar("P", nome + b"\x00" + cstr(sql) + i16(0))

        # Bind: os valores, todos como texto.
        corpo = nome + b"\x00" + nome + b"\x00"
        corpo += i16(0)                              # formatos de entrada
        corpo += i16(len(parametros))
        for p in parametros:
            if p is None:
                corpo += i32(-1)
            else:
                bruto = self._para_texto(p)
                corpo += i32(len(bruto)) + bruto
        corpo += i16(0)                              # formatos de saida
        self._enviar("B", corpo)

        self._enviar("D", b"P" + nome + b"\x00")     # Describe
        self._enviar("E", nome + b"\x00" + i32(0))   # Execute, sem limite
        self._enviar("S")                            # Sync
        return self._colher()

    @staticmethod
    def _numerar(sql, quantos):
        """Troca '?' por '$1', '$2'… — o PostgreSQL so entende assim.

        Aceitar '?' e o que permite a mesma consulta rodar em SQLite,
        MySQL e PostgreSQL sem reescrita. Um '?' dentro de literal de
        texto e deixado em paz.
        """
        if "?" not in sql:
            return sql
        saida, n, aspas = [], 0, None
        for c in sql:
            if aspas:
                saida.append(c)
                if c == aspas:
                    aspas = None
                continue
            if c in "'\"":
                aspas = c
                saida.append(c)
            elif c == "?":
                n += 1
                saida.append(f"${n}")
            else:
                saida.append(c)
        return "".join(saida)

    @staticmethod
    def _para_texto(valor):
        import json
        if isinstance(valor, bool):
            return b"true" if valor else b"false"
        if isinstance(valor, bytes):
            return b"\\x" + valor.hex().encode()
        if isinstance(valor, (list, tuple)):
            itens = ",".join(
                "NULL" if v is None else f'"{str(v)}"' for v in valor)
            return ("{" + itens + "}").encode("utf-8")
        if isinstance(valor, dict):
            return json.dumps(valor, ensure_ascii=False).encode("utf-8")
        return str(valor).encode("utf-8")

    def _colher(self):
        """Le ate 'ReadyForQuery' e devolve (colunas, linhas, afetadas)."""
        colunas, tipos, linhas, afetadas = [], [], [], 0
        erro = None

        while True:
            tipo, dados = self._receber()

            if tipo == "T":                          # descricao das colunas
                colunas, tipos = self._ler_colunas(dados)
            elif tipo == "D":                        # uma linha
                linhas.append(self._ler_linha(dados, tipos))
            elif tipo == "C":                        # comando terminou
                marca, _ = ler_cstr(dados)
                partes = marca.split()
                if partes and partes[-1].isdigit():
                    afetadas = int(partes[-1])
            elif tipo == "E":
                erro = self._erro(dados)
            elif tipo == "Z":                        # pronto para a proxima
                self.em_transacao = dados[:1] in (b"T", b"E")
                if erro:
                    raise erro
                return colunas, linhas, afetadas
            elif tipo == "N":                        # aviso
                continue
            elif tipo in ("1", "2", "3", "n", "s", "I"):
                continue                             # confirmacoes sem dado

    @staticmethod
    def _ler_colunas(dados):
        n = des_i16(dados)
        nomes, tipos, i = [], [], 2
        for _ in range(n):
            nome, i = ler_cstr(dados, i)
            # tabela(4) coluna(2) tipo(4) tamanho(2) modificador(4) formato(2)
            oid = des_i32(dados, i + 6)
            nomes.append(nome)
            tipos.append(oid)
            i += 18
        return nomes, tipos

    @staticmethod
    def _ler_linha(dados, tipos):
        n = des_i16(dados)
        valores, i = [], 2
        for coluna in range(n):
            tamanho = des_i32(dados, i)
            i += 4
            if tamanho == -1:
                valores.append(None)
                continue
            bruto = dados[i:i + tamanho].decode("utf-8", "replace")
            i += tamanho
            conversor = CONVERSORES.get(
                tipos[coluna] if coluna < len(tipos) else 0)
            if conversor:
                try:
                    bruto = conversor(bruto)
                except (ValueError, TypeError):
                    pass                             # fica como texto
            valores.append(bruto)
        return valores

    # ── transacoes ──────────────────────────────────────────

    def comecar(self, isolamento=""):
        nivel = f" ISOLATION LEVEL {isolamento}" if isolamento else ""
        self.executar(f"BEGIN{nivel}")
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

    def _garantir_aberta(self):
        if self._fechado:
            raise StateError(
                "this PostgreSQL connection is closed.",
                dica="open a new one with Forge.conectar(...)",
                doc="banco-de-dados")

    def ping(self):
        return self.consultar("select 1 as um")[0]["um"] == 1

    def versao(self):
        return self.parametros.get("server_version", "")

    def tabelas(self, esquema="public"):
        linhas = self.consultar(
            "select tablename from pg_tables where schemaname = ? "
            "order by tablename", [esquema])
        return [l["tablename"] for l in linhas]

    def colunas(self, tabela):
        return self.consultar(
            "select column_name as nome, data_type as tipo, "
            "is_nullable as aceita_nulo, column_default as padrao "
            "from information_schema.columns where table_name = ? "
            "order by ordinal_position", [tabela])

    def fechar(self):
        if self._fechado:
            return
        self._fechado = True
        try:
            self._enviar("X")                        # Terminate
        except Exception:                            # noqa: BLE001
            pass
        self.canal.fechar()

    @property
    def dialeto(self):
        return "postgres"
