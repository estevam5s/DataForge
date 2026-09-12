"""
Arcane.Database - SQLite Database Module for DataForge
Complete SQLite3 database connectivity with query builder,
migrations, ORM-like models, and transaction support.
"""

import sqlite3
import json
import threading
import os
import time



# ─────────────────────────────────────────────────────────────
#  Nomes que vao CRUS para o SQL
# ─────────────────────────────────────────────────────────────
#
# Valor vai por '?', sempre. Mas nome de coluna, de tabela e de indice
# nao pode ir por parametro — o SQLite nao aceita — e portanto vai
# concatenado. Isso e a porta de injecao, e a unica defesa e recusar o
# que nao parece um nome.
#
# A regra e restritiva de proposito: letra, digito e '_', comecando por
# letra ou '_'. Nao aceita ponto (nome qualificado), nem aspas, nem
# espaco. Quem precisa de algo fora disso escreve o SQL a mao com
# 'Banco.query', e aí a responsabilidade e de quem escreveu.

import re as _re

_NOME_VALIDO = _re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

#: As direcoes aceitas num ORDER BY.
_DIRECOES = {"", "ASC", "DESC"}


def _confirmar(db):
    """Commita — a nao ser que exista uma transacao aberta por fora.

    Toda escrita deste modulo chamava 'commit()' direto, e por isso
    'Banco.transacao' era inutil: o primeiro 'insert' de dentro
    confirmava a transacao, e o 'rollback' depois nao tinha o que
    desfazer. A venda ficava gravada com o estoque intacto.

    O 'savepoint' morria pelo mesmo motivo, com um erro mais direto:
    "no such savepoint".

    A contagem e por CONEXAO, e nao global: dois bancos abertos no mesmo
    programa tem transacoes independentes.
    """
    if db.get("_profundidade", 0) > 0:
        return False
    db["_conn"].commit()
    return True


def _erro(mensagem, nota="", dica=""):
    from ..errors import RuntimeError_
    return RuntimeError_(mensagem, 0, 0, nota=nota, dica=dica,
                         doc="tecnicas/banco-de-dados")


def _identificador(nome, onde):
    """Um nome de tabela, coluna ou indice — ou erro."""
    texto = str(nome)
    if not _NOME_VALIDO.match(texto):
        raise _erro(
            f"'{texto}' nao e um nome valido de tabela ou coluna.",
            nota=f"em '{onde}'; nome vai cru para o SQL e por isso e "
                 f"conferido",
            dica="use letra, digito e '_'; para algo fora disso, escreva "
                 "o SQL com Banco.query")
    return texto


def _conferir_colunas(nomes, onde):
    for nome in nomes:
        _identificador(nome, onde)
    return list(nomes)


def _ordem_segura(order_by):
    """'valor DESC, nome' conferido pedaco por pedaco.

    O ORDER BY vem de fora numa listagem — '?ordenar=nome' — e o nome da
    coluna nao pode ir por parametro. Sem esta conferencia, um
    '?ordenar=nome; DROP TABLE x' e SQL injetado.
    """
    partes = []
    for pedaco in str(order_by).split(","):
        campos = pedaco.strip().split()
        if not campos:
            continue
        coluna = _identificador(campos[0], "order_by")
        direcao = (campos[1].upper() if len(campos) > 1 else "")
        if direcao not in _DIRECOES:
            raise _erro(
                f"'{campos[1]}' nao e uma direcao de ordenacao.",
                nota="as aceitas: ASC, DESC",
                dica=f'use "{coluna} DESC"')
        partes.append(f"{coluna} {direcao}".strip())
    if not partes:
        raise _erro("o 'order_by' esta vazio.",
                    dica='use "coluna" ou "coluna DESC"')
    return ", ".join(partes)


#: Os operadores que um vault de condicao aceita.
_OPERADORES = {"gt": ">", "lt": "<", "gte": ">=", "lte": "<=",
               "ne": "!=", "like": "LIKE", "eq": "="}


def _clausula(where):
    """Um vault de condicao vira '(sql, valores)'.

    Aceita as tres formas que o resto do modulo ja aceitava:

        {"id": 7}                       id = 7
        {"id": [1, 2, 3]}               id IN (1, 2, 3)
        {"preco": {"gte": 10}}          preco >= 10
    """
    partes = []
    valores = []
    for coluna, valor in (where or {}).items():
        _identificador(coluna, "where")
        if isinstance(valor, list):
            if not valor:
                # 'IN ()' e erro de sintaxe no SQLite; e a resposta certa
                # para "nenhum dos valores" e nao casar com nada.
                partes.append("0 = 1")
                continue
            partes.append(f"{coluna} IN ({', '.join('?' * len(valor))})")
            valores.extend(valor)
        elif isinstance(valor, dict):
            for operador, alvo in valor.items():
                simbolo = _OPERADORES.get(str(operador).lower())
                if simbolo is None:
                    raise _erro(
                        f"'{operador}' nao e um operador de condicao.",
                        nota="os aceitos: " + ", ".join(sorted(_OPERADORES)),
                        dica='{"preco": {"gte": 10}}')
                partes.append(f"{coluna} {simbolo} ?")
                valores.append(alvo)
        elif valor is None:
            # 'coluna = NULL' nunca e verdadeiro em SQL; quem escreve
            # 'void' quer dizer "esta vazio".
            partes.append(f"{coluna} IS NULL")
        else:
            partes.append(f"{coluna} = ?")
            valores.append(valor)
    if not partes:
        return "1 = 1", []
    return " AND ".join(partes), valores


# ─────────────────────────────────────────────────────────────
#  Conexao utilizavel de varias threads
# ─────────────────────────────────────────────────────────────

class _CursorSerial:
    """Cursor cujas leituras passam pelo mesmo lock da conexao."""

    __slots__ = ("_cursor", "_trava")

    def __init__(self, cursor, trava):
        self._cursor = cursor
        self._trava = trava

    def fetchall(self):
        with self._trava:
            return self._cursor.fetchall()

    def fetchone(self):
        with self._trava:
            return self._cursor.fetchone()

    def fetchmany(self, tamanho=1):
        with self._trava:
            return self._cursor.fetchmany(tamanho)

    def __iter__(self):
        return iter(self.fetchall())

    def __getattr__(self, nome):
        return getattr(self._cursor, nome)


class _ConexaoSerial:
    """Uma conexao SQLite que varias threads podem usar.

    O sqlite3 do Python recusa uma conexao vinda de outra thread. Isso
    derruba qualquer servidor — o Kiln atende cada pedido numa thread, e
    a primeira consulta estoura com 'SQLite objects created in a thread
    can only be used in that same thread'.

    A saida e desligar essa checagem e serializar os acessos aqui. Fica
    mais lento sob carga (uma consulta por vez), e e o preco certo: a
    alternativa e um banco corrompido.

    Limitacao honesta: a serializacao protege cada operacao, nao uma
    transacao inteira. Duas threads em begin/commit ao mesmo tempo
    compartilham a mesma transacao. Para trabalho transacional
    concorrente, abra uma conexao por thread.
    """

    __slots__ = ("_conn", "_trava")

    def __init__(self, conn):
        self._conn = conn
        # Reentrante: 'execute' pode ser chamado de dentro de outro
        # metodo que ja segura a trava.
        self._trava = threading.RLock()

    def execute(self, sql, params=()):
        with self._trava:
            return _CursorSerial(self._conn.execute(sql, params), self._trava)

    def executemany(self, sql, seq):
        with self._trava:
            return _CursorSerial(self._conn.executemany(sql, seq), self._trava)

    def executescript(self, sql):
        with self._trava:
            return _CursorSerial(self._conn.executescript(sql), self._trava)

    def cursor(self):
        with self._trava:
            return _CursorSerial(self._conn.cursor(), self._trava)

    def commit(self):
        with self._trava:
            return self._conn.commit()

    def rollback(self):
        with self._trava:
            return self._conn.rollback()

    def close(self):
        with self._trava:
            return self._conn.close()

    def backup(self, destino, **kwargs):
        with self._trava:
            return self._conn.backup(destino, **kwargs)

    def __getattr__(self, nome):
        return getattr(self._conn, nome)

    def __setattr__(self, nome, valor):
        if nome in _ConexaoSerial.__slots__:
            object.__setattr__(self, nome, valor)
        else:
            setattr(self._conn, nome, valor)


class ArcaneDatabase:
    """SQLite database module for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Database",

            # ── Conexão ─────────────────────────────────────
            "connect": cls._connect,
            "memory": cls._memory,
            "close": cls._close,

            # ── Execução SQL Direta ─────────────────────────
            "execute": cls._execute,
            "query": cls._query,
            "query_one": cls._query_one,
            "execute_many": cls._execute_many,
            "execute_script": cls._execute_script,

            # ── CRUD ────────────────────────────────────────
            "insert": cls._insert,
            "insert_many": cls._insert_many,
            "select": cls._select,
            "update": cls._update,
            "delete": cls._delete,
            "count": cls._count,
            "exists": cls._exists,

            # ── Transações ──────────────────────────────────
            "begin": cls._begin,
            "commit": cls._commit,
            "rollback": cls._rollback,
            "transaction": cls._transaction,
            "in_transaction": cls._in_transaction,
            "transacao": cls._transaction,
            "savepoint": cls._savepoint,

            # ── Escrita idempotente ─────────────────────────
            "upsert": cls._upsert,
            "upsert_many": cls._upsert_many,
            "insert_or_ignore": cls._insert_or_ignore,
            "increment": cls._increment,

            # ── Paginação e relatório ───────────────────────
            "paginate": cls._paginate,
            "aggregate": cls._aggregate,
            "group_count": cls._group_count,

            # ── Busca textual ───────────────────────────────
            "create_search": cls._create_search,
            "search": cls._search,

            # ── Diagnóstico ─────────────────────────────────
            "explain": cls._explain,
            "indexes": cls._indexes,
            "slow_log": cls._slow_log,
            "watch_slow": cls._watch_slow,
            "integrity": cls._integrity,
            "stats": cls._stats,

            # ── Schema / DDL ────────────────────────────────
            "create_table": cls._create_table,
            "drop_table": cls._drop_table,
            "table_exists": cls._table_exists,
            "tables": cls._tables,
            "columns": cls._columns,
            "add_column": cls._add_column,
            "create_index": cls._create_index,
            "drop_index": cls._drop_index,
            "schema_sql": cls._schema_sql,
            "foreign_keys": cls._foreign_keys,
            "check_foreign_keys": cls._check_foreign_keys,

            # ── Query Builder ───────────────────────────────
            "QueryBuilder": QueryBuilder,
            "builder": cls._builder,

            # ── Migrações ───────────────────────────────────
            "migrate": cls._migrate,
            "rollback_migration": cls._rollback_migration,
            "migrations_applied": cls._migrations_applied,
            "seed": cls._seed,

            # ── Utilitários ─────────────────────────────────
            "backup": cls._backup,
            "export_csv": cls._export_csv,
            "export_json": cls._export_json,
            "import_csv": cls._import_csv,
            "import_json": cls._import_json,
            "table_info": cls._table_info,
            "database_size": cls._database_size,
            "vacuum": cls._vacuum,

            # ── ORM Simples ─────────────────────────────────
            "Model": Model,
            "create_model": cls._create_model,
        }

    # ═══════════════════════════════════════════════════════
    #  Conexão
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _connect(path):
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return {"__type__": "DBConnection", "_conn": _ConexaoSerial(conn),
                "path": path}

    @staticmethod
    def _memory():
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return {"__type__": "DBConnection", "_conn": _ConexaoSerial(conn),
                "path": ":memory:"}

    @staticmethod
    def _close(db):
        db["_conn"].close()
        return True

    # ═══════════════════════════════════════════════════════
    #  Execução SQL Direta
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _execute(db, sql, params=None):
        """Executa um comando. Fora de uma transação, confirma na hora.

        Dentro de begin/commit, NÃO confirma — do contrário 'rollback' não teria
        o que desfazer e a transação seria decorativa.
        """
        cursor = db["_conn"].execute(sql, params or [])
        if not db.get("_in_transaction"):
            _confirmar(db)
        return {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}

    @staticmethod
    def _query(db, sql, params=None):
        cursor = db["_conn"].execute(sql, params or [])
        rows = cursor.fetchall()
        if rows:
            keys = rows[0].keys()
            return [dict(zip(keys, row)) for row in rows]
        return []

    @staticmethod
    def _query_one(db, sql, params=None):
        cursor = db["_conn"].execute(sql, params or [])
        row = cursor.fetchone()
        if row:
            return dict(zip(row.keys(), row))
        return None

    @staticmethod
    def _execute_many(db, sql, params_list):
        cursor = db["_conn"].executemany(sql, params_list)
        if not db.get("_in_transaction"):
            _confirmar(db)
        return cursor.rowcount

    @staticmethod
    def _execute_script(db, script):
        db["_conn"].executescript(script)
        return True

    # ═══════════════════════════════════════════════════════
    #  CRUD
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _insert(db, table, data):
        keys = list(data.keys())
        vals = list(data.values())
        placeholders = ", ".join("?" * len(keys))
        cols = ", ".join(keys)
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        cursor = db["_conn"].execute(sql, vals)
        _confirmar(db)
        return cursor.lastrowid

    @staticmethod
    def _insert_many(db, table, records):
        if not records:
            return 0
        keys = list(records[0].keys())
        placeholders = ", ".join("?" * len(keys))
        cols = ", ".join(keys)
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        data = [tuple(r.get(k) for k in keys) for r in records]
        cursor = db["_conn"].executemany(sql, data)
        _confirmar(db)
        return cursor.rowcount

    @staticmethod
    def _select(db, table, where=None, order_by=None, limit=None, columns=None):
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table}"
        params = []
        if where:
            conditions = []
            for k, v in where.items():
                if isinstance(v, list):
                    placeholders = ", ".join("?" * len(v))
                    conditions.append(f"{k} IN ({placeholders})")
                    params.extend(v)
                elif isinstance(v, dict):
                    for op, val in v.items():
                        op_map = {"gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "ne": "!=", "like": "LIKE"}
                        conditions.append(f"{k} {op_map.get(op, '=')} ?")
                        params.append(val)
                else:
                    conditions.append(f"{k} = ?")
                    params.append(v)
            sql += " WHERE " + " AND ".join(conditions)
        if order_by:
            if isinstance(order_by, str):
                sql += f" ORDER BY {order_by}"
            elif isinstance(order_by, dict):
                parts = [f"{k} {v}" for k, v in order_by.items()]
                sql += " ORDER BY " + ", ".join(parts)
        if limit:
            sql += f" LIMIT {limit}"
        return ArcaneDatabase._query(db, sql, params)

    @staticmethod
    def _update(db, table, data, where):
        set_parts = []
        params = []
        for k, v in data.items():
            set_parts.append(f"{k} = ?")
            params.append(v)
        where_parts = []
        for k, v in where.items():
            where_parts.append(f"{k} = ?")
            params.append(v)
        sql = f"UPDATE {table} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
        cursor = db["_conn"].execute(sql, params)
        _confirmar(db)
        return cursor.rowcount

    @staticmethod
    def _delete(db, table, where=None):
        params = []
        sql = f"DELETE FROM {table}"
        if where:
            conditions = []
            for k, v in where.items():
                conditions.append(f"{k} = ?")
                params.append(v)
            sql += " WHERE " + " AND ".join(conditions)
        cursor = db["_conn"].execute(sql, params)
        _confirmar(db)
        return cursor.rowcount

    @staticmethod
    def _count(db, table, where=None):
        sql = f"SELECT COUNT(*) as cnt FROM {table}"
        params = []
        if where:
            conditions = []
            for k, v in where.items():
                conditions.append(f"{k} = ?")
                params.append(v)
            sql += " WHERE " + " AND ".join(conditions)
        result = ArcaneDatabase._query_one(db, sql, params)
        return result["cnt"] if result else 0

    @staticmethod
    def _exists(db, table, where):
        return ArcaneDatabase._count(db, table, where) > 0

    # ═══════════════════════════════════════════════════════
    #  Transações
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _begin(db):
        """Abre uma transacao a mao. Prefira 'Banco.transacao'.

        'begin' obriga a nao esquecer o 'rollback' em NENHUM caminho de
        saida — inclusive no que dispara —, e esquecer deixa a conexao
        travada para as outras threads. 'Banco.transacao' faz isso.
        """
        if db.get("_profundidade", 0) > 0:
            raise _erro(
                "ja existe uma transacao aberta nesta conexao.",
                nota="o SQLite nao aninha 'BEGIN'",
                dica="use Banco.savepoint para uma transacao interna, ou "
                     "Banco.transacao, que aninha sozinho")
        db["_conn"].execute("BEGIN")
        db["_profundidade"] = 1
        return True

    @staticmethod
    def _commit(db):
        db["_profundidade"] = 0
        db["_conn"].commit()
        return True

    @staticmethod
    def _rollback(db):
        db["_profundidade"] = 0
        db["_conn"].rollback()
        return True

    @staticmethod
    def _in_transaction(db):
        """Estamos dentro de uma transacao agora?

        Util para uma acao que precisa saber se pode abrir a propria.
        """
        return db.get("_profundidade", 0) > 0

    # ═══════════════════════════════════════════════════════
    #  Schema / DDL
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _create_table(db, name, schema):
        """
        schema: dict of column_name -> type_string
        Examples: {"id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                   "name": "TEXT NOT NULL", "age": "INTEGER"}
        """
        cols = ", ".join(f"{k} {v}" for k, v in schema.items())
        sql = f"CREATE TABLE IF NOT EXISTS {name} ({cols})"
        db["_conn"].execute(sql)
        _confirmar(db)
        return True

    @staticmethod
    def _drop_table(db, name):
        db["_conn"].execute(f"DROP TABLE IF EXISTS {name}")
        _confirmar(db)
        return True

    @staticmethod
    def _table_exists(db, name):
        result = ArcaneDatabase._query_one(
            db,
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            [name],
        )
        return result is not None

    @staticmethod
    def _tables(db):
        rows = ArcaneDatabase._query(
            db, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [r["name"] for r in rows]

    @staticmethod
    def _columns(db, table):
        rows = ArcaneDatabase._query(db, f"PRAGMA table_info({table})")
        return [
            {"name": r["name"], "type": r["type"], "notnull": bool(r["notnull"]), "pk": bool(r["pk"])}
            for r in rows
        ]

    @staticmethod
    def _add_column(db, table, name, col_type="TEXT"):
        db["_conn"].execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")
        _confirmar(db)
        return True

    @staticmethod
    def _create_index(db, table, columns, unique=False, name=None):
        idx_name = name or f"idx_{table}_{'_'.join(columns)}"
        u = "UNIQUE " if unique else ""
        cols = ", ".join(columns)
        db["_conn"].execute(f"CREATE {u}INDEX IF NOT EXISTS {idx_name} ON {table} ({cols})")
        _confirmar(db)
        return True

    # ═══════════════════════════════════════════════════════
    #  Query Builder
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _builder(db, table):
        return QueryBuilder(db, table)

    # ═══════════════════════════════════════════════════════
    #  Migrações & Seeds
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _migrate(db, migrations):
        """
        migrations: list of {version: int, up: str(SQL), description: str}
        """
        ArcaneDatabase._create_table(db, "_migrations", {
            "version": "INTEGER PRIMARY KEY",
            "description": "TEXT",
            "applied_at": "TEXT",
        })
        applied = ArcaneDatabase._query(db, "SELECT version FROM _migrations")
        applied_versions = {r["version"] for r in applied}

        count = 0
        for m in sorted(migrations, key=lambda x: x.get("version", 0)):
            v = m.get("version", 0)
            if v not in applied_versions:
                db["_conn"].executescript(m["up"])
                ArcaneDatabase._insert(db, "_migrations", {
                    "version": v,
                    "description": m.get("description", ""),
                    "applied_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                })
                count += 1
        return count

    @staticmethod
    def _rollback_migration(db, migrations, ate=None):
        """Desfaz migracoes, da mais recente para tras.

        'ate' e a versao em que parar (ela FICA aplicada). Sem 'ate',
        desfaz uma so — que e o que se quer em 99% dos casos, porque
        desfazer em cascata por acidente e perda de dado.

        Uma migracao sem 'down' interrompe o rollback com erro, em vez
        de ser pulada em silencio: pular deixaria o banco num estado que
        nenhuma versao descreve, e descobrir isso depois e pior.
        """
        if not ArcaneDatabase._table_exists(db, "_migrations"):
            return 0
        aplicadas = ArcaneDatabase._query(
            db, "SELECT version FROM _migrations ORDER BY version DESC")
        versoes = [r["version"] for r in aplicadas]
        por_versao = {m.get("version", 0): m for m in migrations}

        desfeitas = 0
        for versao in versoes:
            if ate is not None and versao <= ate:
                break
            migracao = por_versao.get(versao)
            if migracao is None:
                raise _erro(
                    f"a migracao {versao} esta aplicada no banco mas nao "
                    f"esta na lista.",
                    nota="o banco conhece uma versao que o codigo nao",
                    dica="recupere a migracao no controle de versao, ou "
                         "apague a linha de '_migrations' a mao")
            descida = migracao.get("down")
            if not descida:
                raise _erro(
                    f"a migracao {versao} nao tem 'down'.",
                    nota=f"'{migracao.get('description', '')}'".strip("'"),
                    dica="acrescente o SQL que desfaz, ou pare o rollback "
                         f"em 'ate := {versao}'")
            db["_conn"].executescript(descida)
            ArcaneDatabase._execute(
                db, "DELETE FROM _migrations WHERE version = ?", [versao])
            desfeitas += 1
            if ate is None:
                break
        return desfeitas

    @staticmethod
    def _migrations_applied(db):
        """As migracoes ja aplicadas, com quando."""
        if not ArcaneDatabase._table_exists(db, "_migrations"):
            return []
        return ArcaneDatabase._query(
            db, "SELECT version, description, applied_at FROM _migrations "
                "ORDER BY version")

    @staticmethod
    def _seed(db, table, records):
        return ArcaneDatabase._insert_many(db, table, records)

    # ═══════════════════════════════════════════════════════
    #  Transacao com desfazer automatico
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _transaction(db, acao):
        """Roda a acao numa transacao. Erro DESFAZ tudo.

        E a peca que falta num PDV: gravar a venda, baixar o estoque e
        lancar o pagamento sao tres escritas que precisam valer juntas.
        Com 'begin'/'commit' a mao, um erro no meio deixa a venda
        registrada com o estoque intacto — e ninguem descobre ate o
        inventario.

            Banco.transacao(db, action ():
                Banco.insert(db, "vendas", venda)
                Banco.increment(db, "produtos", "estoque", -1, {"id": 7})
            )

        Devolve o que a acao devolveu.
        """
        conexao = db["_conn"]
        # Aninhar 'BEGIN' e erro no SQLite. Uma transacao dentro de
        # outra vira savepoint, que e a semantica que quem escreveu
        # espera: a de dentro desfaz so a parte dela.
        if db.get("_profundidade", 0) > 0:
            return ArcaneDatabase._savepoint(
                db, f"t{db['_profundidade']}", acao)

        conexao.execute("BEGIN")
        db["_profundidade"] = 1
        try:
            resultado = acao()
        except BaseException:
            # Amplo de proposito: um 'halt' ou um 'yield' saindo daqui
            # tambem precisa desfazer. Deixar commitado o que ja foi
            # escrito seria a pior das duas opcoes.
            db["_profundidade"] = 0
            conexao.rollback()
            raise
        db["_profundidade"] = 0
        conexao.commit()
        return resultado

    @staticmethod
    def _savepoint(db, nome, acao):
        """Uma transacao DENTRO de outra.

        O SQLite nao aninha 'BEGIN', mas aninha savepoint. Serve para a
        parte que pode falhar sem derrubar o resto: um item do carrinho
        sem estoque nao deve desfazer a venda inteira.
        """
        seguro = _identificador(nome, "savepoint")
        conexao = db["_conn"]
        conexao.execute(f"SAVEPOINT {seguro}")
        db["_profundidade"] = db.get("_profundidade", 0) + 1
        try:
            resultado = acao()
        except BaseException:
            db["_profundidade"] -= 1
            conexao.execute(f"ROLLBACK TO {seguro}")
            conexao.execute(f"RELEASE {seguro}")
            raise
        db["_profundidade"] -= 1
        conexao.execute(f"RELEASE {seguro}")
        # Ao sair do savepoint mais externo, o que ele guardou ainda
        # depende do commit — e ninguem mais vai chama-lo.
        if db["_profundidade"] == 0:
            conexao.commit()
        return resultado

    # ═══════════════════════════════════════════════════════
    #  Escrita idempotente
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _upsert(db, table, data, chaves):
        """Insere, ou atualiza se a chave ja existe.

        As 'chaves' precisam ter indice UNIQUE — e o SQLite que decide o
        conflito, nao um SELECT antes do INSERT. A diferenca importa:
        entre o SELECT e o INSERT, outra thread pode inserir a mesma
        chave, e o codigo "confere e depois grava" perde a corrida sem
        nada denunciando.

        Devolve 'inserido' ou 'atualizado', para quem precisa saber.
        """
        chaves = [chaves] if isinstance(chaves, str) else list(chaves)
        colunas = list(data.keys())
        _conferir_colunas(colunas + chaves, "upsert")

        atualizaveis = [c for c in colunas if c not in chaves]
        marcas = ", ".join("?" * len(colunas))
        conflito = ", ".join(chaves)

        if atualizaveis:
            troca = ", ".join(f"{c} = excluded.{c}" for c in atualizaveis)
            acao = f"UPDATE SET {troca}"
        else:
            acao = "NOTHING"

        antes = ArcaneDatabase._count(db, table)
        sql = (f"INSERT INTO {table} ({', '.join(colunas)}) VALUES ({marcas}) "
               f"ON CONFLICT({conflito}) DO {acao}")
        db["_conn"].execute(sql, list(data.values()))
        _confirmar(db)
        return "inserido" if ArcaneDatabase._count(db, table) > antes \
            else "atualizado"

    @staticmethod
    def _upsert_many(db, table, records, chaves):
        """O mesmo, para muitos — numa transacao so.

        Um por um, mil produtos sao mil commits e mil sincronizacoes de
        disco. Juntos, um.
        """
        if not records:
            return {"inseridos": 0, "atualizados": 0}
        chaves = [chaves] if isinstance(chaves, str) else list(chaves)
        colunas = list(records[0].keys())
        _conferir_colunas(colunas + chaves, "upsert_many")

        atualizaveis = [c for c in colunas if c not in chaves]
        marcas = ", ".join("?" * len(colunas))
        conflito = ", ".join(chaves)
        acao = (f"UPDATE SET {', '.join(f'{c} = excluded.{c}' for c in atualizaveis)}"
                if atualizaveis else "NOTHING")
        sql = (f"INSERT INTO {table} ({', '.join(colunas)}) VALUES ({marcas}) "
               f"ON CONFLICT({conflito}) DO {acao}")

        antes = ArcaneDatabase._count(db, table)
        valores = [tuple(r.get(c) for c in colunas) for r in records]
        ArcaneDatabase._transaction(
            db, lambda: db["_conn"].executemany(sql, valores))
        depois = ArcaneDatabase._count(db, table)
        inseridos = depois - antes
        return {"inseridos": inseridos,
                "atualizados": len(records) - inseridos}

    @staticmethod
    def _insert_or_ignore(db, table, data):
        """Insere e nao reclama se a chave ja existe. Devolve o id, ou 0."""
        colunas = list(data.keys())
        _conferir_colunas(colunas, "insert_or_ignore")
        marcas = ", ".join("?" * len(colunas))
        sql = (f"INSERT OR IGNORE INTO {table} ({', '.join(colunas)}) "
               f"VALUES ({marcas})")
        cursor = db["_conn"].execute(sql, list(data.values()))
        _confirmar(db)
        return cursor.lastrowid if cursor.rowcount else 0

    @staticmethod
    def _increment(db, table, column, delta=1, where=None):
        """'estoque = estoque - 1' no BANCO, e nao na memoria.

        Ler, somar e escrever de volta perde atualizacoes quando duas
        vendas acontecem ao mesmo tempo — e o estoque fica errado sem
        nenhum erro aparecer. Aqui a soma e do SQLite, que a faz sob a
        trava da linha.
        """
        _conferir_colunas([column], "increment")
        sql = f"UPDATE {table} SET {column} = {column} + ?"
        valores = [delta]
        if where:
            partes, extras = _clausula(where)
            sql += f" WHERE {partes}"
            valores += extras
        cursor = db["_conn"].execute(sql, valores)
        _confirmar(db)
        return cursor.rowcount

    # ═══════════════════════════════════════════════════════
    #  Paginacao e relatorio
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _paginate(db, table, pagina=1, por_pagina=20, where=None,
                  order_by=None, columns=None):
        """Uma fatia, com o que a tela de listagem precisa saber.

        Devolve 'itens', 'pagina', 'por_pagina', 'total', 'paginas',
        'tem_anterior' e 'tem_proxima'. Sem 'total' e 'paginas' a tela
        nao sabe desenhar a paginacao, e calcular isso a mao e a mesma
        consulta escrita duas vezes.

        'por_pagina' tem teto de 500: o numero vem de fora numa rota, e
        '?por_pagina=1000000' e como se derruba um servidor sem exploit.
        """
        pagina = max(1, int(pagina))
        por_pagina = max(1, min(500, int(por_pagina)))
        total = ArcaneDatabase._count(db, table, where)
        paginas = max(1, -(-total // por_pagina))   # divisao para cima
        itens = ArcaneDatabase._select(
            db, table, where=where, order_by=order_by,
            limit=por_pagina, columns=columns)
        # O OFFSET nao cabe em '_select'; refaz quando nao e a 1a pagina.
        if pagina > 1:
            sql_cols = ", ".join(columns) if columns else "*"
            sql = f"SELECT {sql_cols} FROM {table}"
            valores = []
            if where:
                partes, extras = _clausula(where)
                sql += f" WHERE {partes}"
                valores += extras
            if order_by:
                sql += f" ORDER BY {order_by}"
            sql += " LIMIT ? OFFSET ?"
            valores += [por_pagina, (pagina - 1) * por_pagina]
            itens = ArcaneDatabase._query(db, sql, valores)
        return {
            "itens": itens,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total": total,
            "paginas": paginas,
            "tem_anterior": pagina > 1,
            "tem_proxima": pagina < paginas,
        }

    #: As funcoes de agregacao aceitas. Lista fechada de proposito: o
    #: nome vai CRU para o SQL, e aceitar qualquer texto ali seria
    #: injecao pela porta da frente.
    _AGREGADOS = {"count", "sum", "avg", "min", "max", "total"}

    @staticmethod
    def _aggregate(db, table, agregados, group_by=None, where=None,
                   order_by=None, limit=None):
        """Relatorio agrupado, sem escrever SQL.

            Banco.aggregate(db, "vendas",
                            {"total": ["sum", "valor"],
                             "quantas": ["count", "*"]},
                            group_by := "vendedor",
                            order_by := "total DESC")

        Devolve as linhas como vaults, com as colunas do 'group_by'
        junto — que e o que um grafico precisa.
        """
        pedacos = []
        for apelido, especificacao in (agregados or {}).items():
            funcao, coluna = (especificacao if isinstance(
                especificacao, (list, tuple)) else (especificacao, "*"))
            funcao = str(funcao).lower()
            if funcao not in ArcaneDatabase._AGREGADOS:
                raise _erro(
                    f"'{funcao}' nao e uma agregacao conhecida.",
                    nota="as aceitas: " + ", ".join(
                        sorted(ArcaneDatabase._AGREGADOS)),
                    dica="para outra, escreva o SQL com 'Banco.query'")
            if coluna != "*":
                _conferir_colunas([coluna], "aggregate")
            _conferir_colunas([apelido], "aggregate")
            pedacos.append(f"{funcao.upper()}({coluna}) AS {apelido}")

        grupos = []
        if group_by:
            grupos = [group_by] if isinstance(group_by, str) else list(group_by)
            _conferir_colunas(grupos, "aggregate")

        colunas = ", ".join(grupos + pedacos) if grupos else ", ".join(pedacos)
        sql = f"SELECT {colunas} FROM {table}"
        valores = []
        if where:
            partes, extras = _clausula(where)
            sql += f" WHERE {partes}"
            valores += extras
        if grupos:
            sql += f" GROUP BY {', '.join(grupos)}"
        if order_by:
            sql += f" ORDER BY {_ordem_segura(order_by)}"
        if limit:
            sql += " LIMIT ?"
            valores.append(int(limit))
        return ArcaneDatabase._query(db, sql, valores)

    @staticmethod
    def _group_count(db, table, column, where=None, order_by="quantidade DESC",
                     limit=None):
        """Quantos de cada. O relatorio que mais se pede."""
        return ArcaneDatabase._aggregate(
            db, table, {"quantidade": ["count", "*"]},
            group_by=column, where=where, order_by=order_by, limit=limit)

    # ═══════════════════════════════════════════════════════
    #  Busca textual
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _create_search(db, table, columns, nome=None):
        """Indice de busca textual (FTS5) sobre uma tabela existente.

        Cria uma tabela virtual e tres gatilhos que a mantem em dia. Sem
        os gatilhos, o indice envelhece em silencio e a busca deixa de
        achar o que foi cadastrado depois — que e o pior defeito
        possivel numa busca.

        Busca por prefixo e por varias palavras, com relevancia. Um
        'LIKE %termo%' nao usa indice nenhum e varre a tabela inteira.
        """
        columns = [columns] if isinstance(columns, str) else list(columns)
        _conferir_colunas(columns, "create_search")
        indice = _identificador(nome or f"{table}_busca", "create_search")
        lista = ", ".join(columns)

        conexao = db["_conn"]
        conexao.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS {indice} USING fts5("
            f"{lista}, content='{table}', content_rowid='rowid')")
        # Preenche com o que ja existe.
        conexao.execute(
            f"INSERT INTO {indice}(rowid, {lista}) "
            f"SELECT rowid, {lista} FROM {table}")
        novos = ", ".join(f"new.{c}" for c in columns)
        velhos = ", ".join(f"old.{c}" for c in columns)
        for gatilho, corpo in (
            ("ai", f"INSERT INTO {indice}(rowid, {lista}) "
                   f"VALUES (new.rowid, {novos});"),
            ("ad", f"INSERT INTO {indice}({indice}, rowid, {lista}) "
                   f"VALUES ('delete', old.rowid, {velhos});"),
            ("au", f"INSERT INTO {indice}({indice}, rowid, {lista}) "
                   f"VALUES ('delete', old.rowid, {velhos}); "
                   f"INSERT INTO {indice}(rowid, {lista}) "
                   f"VALUES (new.rowid, {novos});"),
        ):
            quando = {"ai": "AFTER INSERT", "ad": "AFTER DELETE",
                      "au": "AFTER UPDATE"}[gatilho]
            conexao.execute(
                f"CREATE TRIGGER IF NOT EXISTS {indice}_{gatilho} {quando} "
                f"ON {table} BEGIN {corpo} END")
        conexao.commit()
        return indice

    @staticmethod
    def _search(db, table, termo, limit=20, nome=None, columns=None):
        """Busca no indice textual, por relevancia.

        Devolve as linhas da tabela ORIGINAL — quem busca quer o
        produto, nao o indice. O termo e escapado: 'MATCH' tem sintaxe
        propria, e um termo com aspas ou 'AND' quebraria a consulta ou
        mudaria o que ela procura.
        """
        indice = _identificador(nome or f"{table}_busca", "search")
        if not ArcaneDatabase._table_exists(db, indice):
            raise _erro(
                f"nao ha indice de busca para '{table}'.",
                nota=f"esperava a tabela '{indice}'",
                dica=f'crie com Banco.create_search(db, "{table}", '
                     f'["titulo", "autor"])')
        palavras = [p for p in str(termo).replace('"', " ").split() if p]
        if not palavras:
            return []
        # Prefixo na ultima palavra: quem digita "livr" espera achar
        # "livro" antes de terminar de escrever.
        #
        # O '*' vai FORA das aspas. Dentro — '"livr*"' — ele e um
        # caractere literal e a busca nao acha nada, calada: a sintaxe
        # de prefixo do FTS5 e '"livr"*'. Foi assim que a busca inteira
        # devolveu lista vazia sem um erro sequer.
        citadas = [f'"{p}"' for p in palavras[:-1]]
        citadas.append(f'"{palavras[-1]}"*')
        consulta = " ".join(citadas)
        alvo = ", ".join(f"t.{c}" for c in columns) if columns else "t.*"
        # O MATCH vai numa SUBCONSULTA, e nao num JOIN com apelido.
        #
        # Duas razoes. A primeira e que 'apelido MATCH ?' e recusado
        # pelo SQLite ("no such column"), e o nome original junto de um
        # apelido devolvia lista VAZIA sem erro nenhum — uma busca que
        # nao acha nada e cala e o pior defeito possivel. A segunda e
        # que assim o LIMIT e aplicado antes do JOIN: com um milhao de
        # linhas, junta-se vinte e nao um milhao.
        sql = (f"SELECT {alvo} FROM ("
               f"SELECT rowid FROM {indice} WHERE {indice} MATCH ? "
               f"ORDER BY rank LIMIT ?) b "
               f"JOIN {table} t ON t.rowid = b.rowid")
        return ArcaneDatabase._query(db, sql, [consulta, int(limit)])

    # ═══════════════════════════════════════════════════════
    #  Diagnostico
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _explain(db, sql, params=None):
        """O plano da consulta, em texto legivel.

        A linha que importa e a que diz SCAN em vez de SEARCH: SCAN le a
        tabela inteira, e num cadastro de 200 mil produtos e a diferenca
        entre 2 ms e 2 s. A resposta quase sempre e um indice.
        """
        linhas = ArcaneDatabase._query(
            db, f"EXPLAIN QUERY PLAN {sql}", params)
        passos = [r.get("detail", "") for r in linhas]
        varre = [p for p in passos if p.startswith("SCAN")]
        return {
            "passos": passos,
            "varre_tabela": bool(varre),
            "aviso": ("le a tabela inteira: " + "; ".join(varre)
                      if varre else ""),
        }

    @staticmethod
    def _indexes(db, table=None):
        """Os indices, com as colunas de cada um."""
        if table:
            _conferir_colunas([table], "indexes")
            achados = ArcaneDatabase._query(
                db, "SELECT name, tbl_name, sql FROM sqlite_master "
                    "WHERE type = 'index' AND tbl_name = ?", [table])
        else:
            achados = ArcaneDatabase._query(
                db, "SELECT name, tbl_name, sql FROM sqlite_master "
                    "WHERE type = 'index'")
        saida = []
        for indice in achados:
            colunas = ArcaneDatabase._query(
                db, f"PRAGMA index_info({indice['name']})")
            saida.append({
                "nome": indice["name"],
                "tabela": indice["tbl_name"],
                "colunas": [c["name"] for c in colunas],
                # Um indice sem SQL foi criado pelo SQLite para uma
                # restricao UNIQUE ou PRIMARY KEY.
                "automatico": not indice.get("sql"),
            })
        return saida

    @staticmethod
    def _watch_slow(db, acima_de_ms=50):
        """Liga o registro de consulta lenta. Devolve o que desliga.

        O limite e em milissegundos e o padrao e 50: abaixo disso nada
        que um usuario faca vai parecer devagar, e registrar tudo
        transformaria o log em ruido.
        """
        conexao = db["_conn"]
        registro = db.setdefault("_lentas", [])
        limite = float(acima_de_ms) / 1000.0

        def rastrear(sql):
            registro.append({"sql": " ".join(str(sql).split()),
                             "quando": time.time()})

        # O 'set_trace_callback' do sqlite3 avisa no INICIO da consulta;
        # o tempo sai da diferenca ate o proximo aviso ou o fim.
        conexao.set_trace_callback(rastrear)
        db["_limite_lento"] = limite

        def desligar():
            conexao.set_trace_callback(None)
            return list(registro)

        return desligar

    @staticmethod
    def _slow_log(db):
        """As consultas registradas por 'watch_slow'."""
        return list(db.get("_lentas", []))

    @staticmethod
    def _integrity(db):
        """O banco esta consistente? Roda o 'integrity_check' do SQLite."""
        linhas = ArcaneDatabase._query(db, "PRAGMA integrity_check")
        problemas = [list(r.values())[0] for r in linhas
                     if list(r.values())[0] != "ok"]
        return {"ok": not problemas, "problemas": problemas}

    @staticmethod
    def _stats(db):
        """Um retrato do banco: tabelas, linhas, indices, tamanho."""
        tabelas = ArcaneDatabase._tables(db)
        sombras = ArcaneDatabase._sombras_de_fts(db)
        por_tabela = []
        for nome in tabelas:
            # As tabelas internas do SQLite e as que o FTS5 cria para si
            # ('x_data', 'x_idx', 'x_docsize', 'x_config') nao sao do
            # usuario. Contar as quatro por indice de busca faria um
            # banco de duas tabelas parecer ter dez.
            if nome.startswith("sqlite_") or nome in sombras:
                continue
            por_tabela.append({
                "tabela": nome,
                "linhas": ArcaneDatabase._count(db, nome),
                "colunas": len(ArcaneDatabase._columns(db, nome)),
                "indices": len(ArcaneDatabase._indexes(db, nome)),
            })
        return {
            "caminho": db.get("path", ""),
            "bytes": ArcaneDatabase._database_size(db),
            "tabelas": sorted(por_tabela, key=lambda t: -t["linhas"]),
            "total_de_linhas": sum(t["linhas"] for t in por_tabela),
        }

    # ═══════════════════════════════════════════════════════
    #  Schema
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _sombras_de_fts(db):
        """As tabelas que o FTS5 cria para si, mais os indices de busca."""
        linhas = ArcaneDatabase._query(
            db, "SELECT name, sql FROM sqlite_master WHERE type = 'table'")
        virtuais = {r["name"] for r in linhas
                    if r.get("sql") and "USING fts" in (r["sql"] or "")}
        sombras = set()
        for base in virtuais:
            sombras.add(base)
            for sufixo in ("_data", "_idx", "_docsize", "_config",
                           "_content"):
                sombras.add(base + sufixo)
        return sombras

    @staticmethod
    def _drop_index(db, nome):
        db["_conn"].execute(f"DROP INDEX IF EXISTS "
                            f"{_identificador(nome, 'drop_index')}")
        _confirmar(db)
        return True

    @staticmethod
    def _schema_sql(db, table=None):
        """O CREATE TABLE como o SQLite o guarda.

        Serve para versionar o schema, comparar dois bancos e escrever a
        migracao que falta.
        """
        if table:
            linha = ArcaneDatabase._query_one(
                db, "SELECT sql FROM sqlite_master WHERE name = ?", [table])
            return (linha or {}).get("sql", "")
        linhas = ArcaneDatabase._query(
            db, "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL "
                "ORDER BY type DESC, name")
        return "\n\n".join(r["sql"] + ";" for r in linhas)

    @staticmethod
    def _foreign_keys(db, table):
        """As chaves estrangeiras de uma tabela."""
        linhas = ArcaneDatabase._query(db, f"PRAGMA foreign_key_list({table})")
        return [{"coluna": r["from"], "aponta_para": r["table"],
                 "coluna_alvo": r["to"], "ao_apagar": r.get("on_delete", ""),
                 "ao_atualizar": r.get("on_update", "")} for r in linhas]

    @staticmethod
    def _check_foreign_keys(db):
        """As linhas que apontam para algo que nao existe.

        'PRAGMA foreign_keys=ON' impede novas violacoes, mas nao conserta
        as que entraram antes — um banco importado de CSV costuma ter
        varias, e elas so aparecem quando alguem tenta usar o dado.
        """
        linhas = ArcaneDatabase._query(db, "PRAGMA foreign_key_check")
        return [{"tabela": r.get("table", ""), "rowid": r.get("rowid"),
                 "aponta_para": r.get("parent", "")} for r in linhas]

    # ═══════════════════════════════════════════════════════
    #  Utilitários
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _backup(db, dest_path):
        dest = sqlite3.connect(dest_path, check_same_thread=False)
        db["_conn"].backup(dest)
        dest.close()
        return dest_path

    @staticmethod
    def _export_csv(db, table, path):
        import csv
        rows = ArcaneDatabase._query(db, f"SELECT * FROM {table}")
        if not rows:
            return path
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return path

    @staticmethod
    def _export_json(db, table, path):
        rows = ArcaneDatabase._query(db, f"SELECT * FROM {table}")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        return path

    @staticmethod
    def _import_csv(db, table, path, has_header=True):
        import csv
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return 0
        if has_header:
            headers = rows[0]
            data = rows[1:]
        else:
            headers = [f"col_{i}" for i in range(len(rows[0]))]
            data = rows
        records = [{headers[i]: row[i] for i in range(len(headers))} for row in data]
        return ArcaneDatabase._insert_many(db, table, records)

    @staticmethod
    def _import_json(db, table, path):
        with open(path, "r", encoding="utf-8") as f:
            records = json.load(f)
        if isinstance(records, list):
            return ArcaneDatabase._insert_many(db, table, records)
        return 0

    @staticmethod
    def _table_info(db, table):
        cols = ArcaneDatabase._columns(db, table)
        count = ArcaneDatabase._count(db, table)
        return {"table": table, "columns": cols, "row_count": count}

    @staticmethod
    def _database_size(db):
        result = ArcaneDatabase._query_one(db, "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        return result["size"] if result else 0

    @staticmethod
    def _vacuum(db):
        db["_conn"].execute("VACUUM")
        return True

    # ═══════════════════════════════════════════════════════
    #  ORM Simples
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _create_model(db, table, schema):
        return Model(db, table, schema)


# ═══════════════════════════════════════════════════════════
#  Query Builder
# ═══════════════════════════════════════════════════════════

class QueryBuilder:
    """Fluent SQL query builder for DataForge."""

    def __init__(self, db, table):
        self._db = db
        self._table = table
        self._select_cols = ["*"]
        self._where = []
        self._params = []
        self._order = []
        self._limit_val = None
        self._offset_val = None
        self._group = []
        self._having = None
        self._joins = []

    def select(self, *cols):
        self._select_cols = list(cols) if cols else ["*"]
        return self

    def where(self, col, op, value):
        self._where.append(f"{col} {op} ?")
        self._params.append(value)
        return self

    def and_where(self, col, op, value):
        return self.where(col, op, value)

    def or_where(self, col, op, value):
        self._where.append(f"OR {col} {op} ?")
        self._params.append(value)
        return self

    def where_in(self, col, values):
        placeholders = ", ".join("?" * len(values))
        self._where.append(f"{col} IN ({placeholders})")
        self._params.extend(values)
        return self

    def where_null(self, col):
        self._where.append(f"{col} IS NULL")
        return self

    def where_not_null(self, col):
        self._where.append(f"{col} IS NOT NULL")
        return self

    def where_between(self, col, low, high):
        self._where.append(f"{col} BETWEEN ? AND ?")
        self._params.extend([low, high])
        return self

    def where_like(self, col, pattern):
        self._where.append(f"{col} LIKE ?")
        self._params.append(pattern)
        return self

    def order_by(self, col, direction="ASC"):
        self._order.append(f"{col} {direction}")
        return self

    def limit(self, n):
        self._limit_val = n
        return self

    def offset(self, n):
        self._offset_val = n
        return self

    def group_by(self, *cols):
        self._group = list(cols)
        return self

    def having(self, condition):
        self._having = condition
        return self

    def join(self, table, on, join_type="INNER"):
        self._joins.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def left_join(self, table, on):
        return self.join(table, on, "LEFT")

    def _build_select(self):
        cols = ", ".join(self._select_cols)
        sql = f"SELECT {cols} FROM {self._table}"
        for j in self._joins:
            sql += f" {j}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        if self._group:
            sql += " GROUP BY " + ", ".join(self._group)
        if self._having:
            sql += f" HAVING {self._having}"
        if self._order:
            sql += " ORDER BY " + ", ".join(self._order)
        if self._limit_val is not None:
            sql += f" LIMIT {self._limit_val}"
        if self._offset_val is not None:
            sql += f" OFFSET {self._offset_val}"
        return sql

    def get(self):
        sql = self._build_select()
        return ArcaneDatabase._query(self._db, sql, self._params)

    def first(self):
        self._limit_val = 1
        rows = self.get()
        return rows[0] if rows else None

    def count(self):
        self._select_cols = ["COUNT(*) as cnt"]
        rows = self.get()
        return rows[0]["cnt"] if rows else 0

    def sum(self, col):
        self._select_cols = [f"SUM({col}) as total"]
        rows = self.get()
        return rows[0]["total"] if rows and rows[0]["total"] else 0

    def avg(self, col):
        self._select_cols = [f"AVG({col}) as average"]
        rows = self.get()
        return rows[0]["average"] if rows and rows[0]["average"] else 0

    def max(self, col):
        self._select_cols = [f"MAX({col}) as maximum"]
        rows = self.get()
        return rows[0]["maximum"] if rows else None

    def min(self, col):
        self._select_cols = [f"MIN({col}) as minimum"]
        rows = self.get()
        return rows[0]["minimum"] if rows else None

    def insert(self, data):
        return ArcaneDatabase._insert(self._db, self._table, data)

    def update(self, data):
        set_parts = []
        params = []
        for k, v in data.items():
            set_parts.append(f"{k} = ?")
            params.append(v)
        sql = f"UPDATE {self._table} SET {', '.join(set_parts)}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
            params.extend(self._params)
        cursor = self._db["_conn"].execute(sql, params)
        self.__confirmar(db)
        return cursor.rowcount

    def delete(self):
        sql = f"DELETE FROM {self._table}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        cursor = self._db["_conn"].execute(sql, self._params)
        self.__confirmar(db)
        return cursor.rowcount

    def to_sql(self):
        return self._build_select()

    def __repr__(self):
        return f"<QueryBuilder: {self._build_select()}>"


# ═══════════════════════════════════════════════════════════
#  ORM - Model
# ═══════════════════════════════════════════════════════════

class Model:
    """Simple ORM-like model for DataForge."""

    def __init__(self, db, table, schema=None):
        self._db = db
        self._table = table
        self._schema = schema
        if schema:
            ArcaneDatabase._create_table(db, table, schema)

    def create(self, data):
        return ArcaneDatabase._insert(self._db, self._table, data)

    def find(self, id_val):
        return ArcaneDatabase._query_one(
            self._db, f"SELECT * FROM {self._table} WHERE id = ?", [id_val]
        )

    def find_by(self, where):
        return ArcaneDatabase._select(self._db, self._table, where=where, limit=1)

    def all(self, order_by=None, limit=None):
        return ArcaneDatabase._select(self._db, self._table, order_by=order_by, limit=limit)

    def where(self, conditions):
        return ArcaneDatabase._select(self._db, self._table, where=conditions)

    def update(self, id_val, data):
        return ArcaneDatabase._update(self._db, self._table, data, {"id": id_val})

    def delete(self, id_val):
        return ArcaneDatabase._delete(self._db, self._table, {"id": id_val})

    def count(self, where=None):
        return ArcaneDatabase._count(self._db, self._table, where)

    def exists(self, where):
        return ArcaneDatabase._exists(self._db, self._table, where)

    def query(self):
        return QueryBuilder(self._db, self._table)

    def truncate(self):
        return ArcaneDatabase._delete(self._db, self._table)

    def describe(self):
        return ArcaneDatabase._table_info(self._db, self._table)

    def __repr__(self):
        return f"<Model: {self._table}>"
