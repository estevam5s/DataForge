"""
Driver SQLite — sobre o sqlite3 da stdlib do Python.

E o unico dos cinco que nao fala protocolo: o SQLite roda dentro do
processo, e o Python ja o traz. O que este arquivo faz e dar a ele a
MESMA interface dos outros — 'consultar' devolvendo vaults, 'executar'
devolvendo contagem, erros da linguagem — para que trocar de motor
nao mude uma linha do codigo que usa.

Duas coisas que o sqlite3 cru nao faz e sao necessarias aqui:

  1. **Devolver vaults.** Ele devolve tuplas; um 'linha[0]' que muda de
     significado quando alguem acrescenta uma coluna e um bug esperando
     para acontecer.

  2. **Aceitar outra thread.** Ele recusa a conexao vinda de uma thread
     diferente da que a abriu, e o Kiln atende um pedido por thread. Um
     lock serializa o acesso: sem isso, a primeira consulta de qualquer
     servidor estoura.
"""

import os
import sqlite3
import threading

from ...errors import (ConstraintError, DatabaseError, QueryError, StateError,
                       TransactionError)


class SQLite:
    """Uma conexao SQLite, com a interface comum do Forge."""

    def __init__(self, caminho=":memory:", prazo=10.0, **_):
        self.caminho = caminho
        self.trava = threading.RLock()
        self.em_transacao = False
        self._fechado = False
        self._ultimo_id = 0

        if caminho not in (":memory:", ""):
            pasta = os.path.dirname(os.path.abspath(caminho))
            if pasta:
                os.makedirs(pasta, exist_ok=True)

        self.conexao = sqlite3.connect(
            caminho or ":memory:", check_same_thread=False, timeout=prazo)
        self.conexao.row_factory = sqlite3.Row
        # Chave estrangeira e opcional no SQLite, e vem DESLIGADA. Quem
        # declara uma e espera que ela valha; deixar desligada faz a
        # restricao existir so no papel.
        self.conexao.execute("PRAGMA foreign_keys = ON")
        # WAL deixa leitura e escrita conviverem — sem ele, um leitor
        # bloqueia o escritor e um servidor trava sob carga leve.
        if caminho not in (":memory:", ""):
            try:
                self.conexao.execute("PRAGMA journal_mode = WAL")
            except sqlite3.Error:
                pass

    # ── consultas ───────────────────────────────────────────

    def consultar(self, sql, parametros=None):
        with self.trava:
            self._garantir_aberta()
            try:
                cursor = self.conexao.execute(sql, tuple(parametros or ()))
                return [dict(linha) for linha in cursor.fetchall()]
            except sqlite3.Error as e:
                raise self._erro(e, sql) from None

    def executar(self, sql, parametros=None):
        with self.trava:
            self._garantir_aberta()
            try:
                cursor = self.conexao.execute(sql, tuple(parametros or ()))
                self._ultimo_id = cursor.lastrowid or 0
                if not self.em_transacao:
                    self.conexao.commit()
                return cursor.rowcount if cursor.rowcount >= 0 else 0
            except sqlite3.Error as e:
                raise self._erro(e, sql) from None

    def executar_muitos(self, sql, linhas):
        with self.trava:
            self._garantir_aberta()
            try:
                cursor = self.conexao.executemany(sql, [tuple(l) for l in linhas])
                if not self.em_transacao:
                    self.conexao.commit()
                return cursor.rowcount
            except sqlite3.Error as e:
                raise self._erro(e, sql) from None

    def executar_script(self, sql):
        with self.trava:
            self._garantir_aberta()
            try:
                self.conexao.executescript(sql)
                self.conexao.commit()
                return True
            except sqlite3.Error as e:
                raise self._erro(e, sql) from None

    @staticmethod
    def _erro(e, sql=""):
        texto = str(e)
        baixo = texto.lower()
        if "unique constraint" in baixo or "not null constraint" in baixo \
                or "foreign key constraint" in baixo \
                or "check constraint" in baixo:
            return ConstraintError(
                texto, nota="SQLite constraint",
                dica="check for an existing row before inserting",
                doc="banco-de-dados")
        if "no such table" in baixo:
            return QueryError(
                texto, dica="run the migration first:  modelo.migrar()",
                doc="banco-de-dados")
        if "no such column" in baixo:
            return QueryError(texto, dica="check the column name",
                              doc="banco-de-dados")
        if "syntax error" in baixo:
            return QueryError(texto, nota=sql[:120] if sql else "",
                              doc="banco-de-dados")
        if "database is locked" in baixo:
            return TransactionError(
                texto,
                nota="another connection is holding a write lock",
                dica="keep transactions short, or raise the timeout",
                doc="banco-de-dados")
        return DatabaseError(texto, doc="banco-de-dados")

    # ── transacoes ──────────────────────────────────────────

    def comecar(self, isolamento=""):
        with self.trava:
            self.conexao.execute("BEGIN")
            self.em_transacao = True
        return self

    def confirmar(self):
        with self.trava:
            if not self.em_transacao:
                raise TransactionError(
                    "there is no open transaction to commit.",
                    dica="open one with  db.comecar()  first",
                    doc="banco-de-dados")
            self.conexao.commit()
            self.em_transacao = False

    def desfazer(self):
        with self.trava:
            if not self.em_transacao:
                return
            self.conexao.rollback()
            self.em_transacao = False

    # ── esquema ─────────────────────────────────────────────

    def tabelas(self):
        return [l["name"] for l in self.consultar(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]

    def colunas(self, tabela):
        linhas = self.consultar(f'PRAGMA table_info("{tabela}")')
        return [{"nome": l["name"], "tipo": l["type"],
                 "aceita_nulo": "NO" if l["notnull"] else "YES",
                 "padrao": l["dflt_value"]} for l in linhas]

    def ultimo_id(self):
        return self._ultimo_id

    def ping(self):
        return self.consultar("SELECT 1 AS um")[0]["um"] == 1

    def versao(self):
        return sqlite3.sqlite_version

    def compactar(self):
        """VACUUM — recupera o espaco de linhas apagadas."""
        with self.trava:
            self.conexao.execute("VACUUM")
        return True

    def _garantir_aberta(self):
        if self._fechado:
            raise StateError("this SQLite connection is closed.",
                             dica="open a new one with Forge.conectar(...)",
                             doc="banco-de-dados")

    def fechar(self):
        with self.trava:
            if self._fechado:
                return
            self._fechado = True
            try:
                self.conexao.close()
            except sqlite3.Error:
                pass

    @property
    def dialeto(self):
        return "sqlite"
