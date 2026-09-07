import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Database",
  description: "SQLite: tabelas, consultas, transações e migrações.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Database as DB

conn := DB.memory()
DB.execute(conn, "CREATE TABLE alunos (nome TEXT, nota REAL)")
DB.execute(conn, "INSERT INTO alunos VALUES (?, ?)", ["Ana", 9.5])

cycle linha in DB.query(conn, "SELECT nome, nota FROM alunos"):
    out $"{linha["nome"]}: {linha["nota"]}"

DB.close(conn)`, title: `exemplo` },
  {"callout": {"tipo": "perigo", "titulo": "Sempre use parâmetros", "texto": "Nunca monte SQL com interpolação. Com `?`, o valor é enviado separado do comando e nunca é interpretado como SQL. Veja [Banco de dados](/tecnicas/banco-de-dados)."}},
  {"p": "Guia com contexto e boas práticas: [Database](/tecnicas/banco-de-dados)."},
  {"h2": "Funções (39)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Model(db, table, schema=None)`"], ["`QueryBuilder(db, table)`"], ["`add_column(db, table, name, col_type='TEXT')`"], ["`backup(db, dest_path)`"], ["`begin(db)`"], ["`builder(db, table)`"], ["`close(db)`"], ["`columns(db, table)`"], ["`commit(db)`"], ["`connect(path)`"], ["`count(db, table, where=None)`"], ["`create_index(db, table, columns, unique=False, name=None)`"], ["`create_model(db, table, schema)`"], ["`create_table(db, name, schema)`"], ["`database_size(db)`"], ["`delete(db, table, where=None)`"], ["`drop_table(db, name)`"], ["`execute(db, sql, params=None)`"], ["`execute_many(db, sql, params_list)`"], ["`execute_script(db, script)`"], ["`exists(db, table, where)`"], ["`export_csv(db, table, path)`"], ["`export_json(db, table, path)`"], ["`import_csv(db, table, path, has_header=True)`"], ["`import_json(db, table, path)`"], ["`insert(db, table, data)`"], ["`insert_many(db, table, records)`"], ["`memory()`"], ["`migrate(db, migrations)`"], ["`query(db, sql, params=None)`"], ["`query_one(db, sql, params=None)`"], ["`rollback(db)`"], ["`seed(db, table, records)`"], ["`select(db, table, where=None, order_by=None, limit=None, columns=None)`"], ["`table_exists(db, name)`"], ["`table_info(db, table)`"], ["`tables(db)`"], ["`update(db, table, data, where)`"], ["`vacuum(db)`"]]}},
];

const headings = [{ id: 'funcoes-39', text: "Funções (39)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Database"}
      description={"SQLite: tabelas, consultas, transações e migrações."}
      href={"/biblioteca/database"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
