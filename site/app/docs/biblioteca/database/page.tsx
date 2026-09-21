// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/database.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Database",
  description: "Banco de dados SQLite: tabelas, consultas, migrações e importação.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Database as DB

conn := DB.memory()
DB.execute(conn, "CREATE TABLE alunos (nome TEXT, nota REAL)")
DB.execute(conn, "INSERT INTO alunos VALUES (?, ?)", ["Ana", 9.5])

cycle linha in DB.query(conn, "SELECT nome, nota FROM alunos"):
    out $"{linha["nome"]}: {linha["nota"]}"

DB.close(conn)`, title: `exemplo` },
  {"callout": {"tipo": "perigo", "titulo": "Sempre use parâmetros", "texto": "Nunca monte SQL com interpolação. Com `?`, o valor é enviado separado do comando e nunca é interpretado como SQL. Veja [Banco de dados](/docs/tecnicas/banco-de-dados)."}},
  {"p": "Guia com contexto e boas práticas: [Database](/docs/tecnicas/banco-de-dados)."},
  {"h2": "Funções (64)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Model(db, table, schema=None)`"], ["`QueryBuilder(db, table)`"], ["`add_column(db, table, name, col_type='TEXT')`"], ["`aggregate(db, table, agregados, group_by=None, where=None, order_by=None, limit=None)`"], ["`backup(db, dest_path)`"], ["`begin(db)`"], ["`builder(db, table)`"], ["`check_foreign_keys(db)`"], ["`close(db)`"], ["`columns(db, table)`"], ["`commit(db)`"], ["`connect(path)`"], ["`count(db, table, where=None)`"], ["`create_index(db, table, columns, unique=False, name=None)`"], ["`create_model(db, table, schema)`"], ["`create_search(db, table, columns, nome=None)`"], ["`create_table(db, name, schema)`"], ["`database_size(db)`"], ["`delete(db, table, where=None)`"], ["`drop_index(db, nome)`"], ["`drop_table(db, name)`"], ["`execute(db, sql, params=None)`"], ["`execute_many(db, sql, params_list)`"], ["`execute_script(db, script)`"], ["`exists(db, table, where)`"], ["`explain(db, sql, params=None)`"], ["`export_csv(db, table, path)`"], ["`export_json(db, table, path)`"], ["`foreign_keys(db, table)`"], ["`group_count(db, table, column, where=None, order_by='quantidade DESC', limit=None)`"], ["`import_csv(db, table, path, has_header=True)`"], ["`import_json(db, table, path)`"], ["`in_transaction(db)`"], ["`increment(db, table, column, delta=1, where=None)`"], ["`indexes(db, table=None)`"], ["`insert(db, table, data)`"], ["`insert_many(db, table, records)`"], ["`insert_or_ignore(db, table, data)`"], ["`integrity(db)`"], ["`memory()`"], ["`migrate(db, migrations)`"], ["`migrations_applied(db)`"], ["`paginate(db, table, pagina=1, por_pagina=20, where=None, order_by=None, columns=None)`"], ["`query(db, sql, params=None)`"], ["`query_one(db, sql, params=None)`"], ["`rollback(db)`"], ["`rollback_migration(db, migrations, ate=None)`"], ["`savepoint(db, nome, acao)`"], ["`schema_sql(db, table=None)`"], ["`search(db, table, termo, limit=20, nome=None, columns=None)`"], ["`seed(db, table, records)`"], ["`select(db, table, where=None, order_by=None, limit=None, columns=None)`"], ["`slow_log(db)`"], ["`stats(db)`"], ["`table_exists(db, name)`"], ["`table_info(db, table)`"], ["`tables(db)`"], ["`transacao(db, acao)`"], ["`transaction(db, acao)`"], ["`update(db, table, data, where)`"], ["`upsert(db, table, data, chaves)`"], ["`upsert_many(db, table, records, chaves)`"], ["`vacuum(db)`"], ["`watch_slow(db, acima_de_ms=50)`"]]}},
];

const headings = [{ id: 'funcoes-64', text: "Funções (64)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Database"}
      description={"Banco de dados SQLite: tabelas, consultas, migrações e importação."}
      href={"/docs/biblioteca/database"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
