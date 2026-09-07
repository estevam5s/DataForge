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

            # ── Schema / DDL ────────────────────────────────
            "create_table": cls._create_table,
            "drop_table": cls._drop_table,
            "table_exists": cls._table_exists,
            "tables": cls._tables,
            "columns": cls._columns,
            "add_column": cls._add_column,
            "create_index": cls._create_index,

            # ── Query Builder ───────────────────────────────
            "QueryBuilder": QueryBuilder,
            "builder": cls._builder,

            # ── Migrações ───────────────────────────────────
            "migrate": cls._migrate,
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
            db["_conn"].commit()
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
            db["_conn"].commit()
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
        db["_conn"].commit()
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
        db["_conn"].commit()
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
        db["_conn"].commit()
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
        db["_conn"].commit()
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
        if db.get("_in_transaction"):
            raise RuntimeError("já existe uma transação aberta nesta conexão")
        db["_conn"].execute("BEGIN")
        db["_in_transaction"] = True
        return True

    @staticmethod
    def _commit(db):
        db["_conn"].commit()
        db["_in_transaction"] = False
        return True

    @staticmethod
    def _rollback(db):
        db["_conn"].rollback()
        db["_in_transaction"] = False
        return True

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
        db["_conn"].commit()
        return True

    @staticmethod
    def _drop_table(db, name):
        db["_conn"].execute(f"DROP TABLE IF EXISTS {name}")
        db["_conn"].commit()
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
        db["_conn"].commit()
        return True

    @staticmethod
    def _create_index(db, table, columns, unique=False, name=None):
        idx_name = name or f"idx_{table}_{'_'.join(columns)}"
        u = "UNIQUE " if unique else ""
        cols = ", ".join(columns)
        db["_conn"].execute(f"CREATE {u}INDEX IF NOT EXISTS {idx_name} ON {table} ({cols})")
        db["_conn"].commit()
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
    def _seed(db, table, records):
        return ArcaneDatabase._insert_many(db, table, records)

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
        self._db["_conn"].commit()
        return cursor.rowcount

    def delete(self):
        sql = f"DELETE FROM {self._table}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        cursor = self._db["_conn"].execute(sql, self._params)
        self._db["_conn"].commit()
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
