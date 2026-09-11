import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Banco de dados",
  description: "SQLite com Arcane.Database: consultas parametrizadas, transações e modelos.",
};

const blocos: Bloco[] = [
  {"h2": "Conectar"},
  { code: `adopt Arcane.Database as DB

conn := DB.memory()                  # em memória: some ao terminar
conn := DB.connect("dados.db")       # arquivo SQLite` },
  {"p": "`memory()` é ideal para teste: cada execução começa limpa, e nada fica no disco."},
  {"h2": "Parâmetros, sempre"},
  { code: `DB.query(conn, "SELECT nome FROM produtos WHERE preco < ?", [100])` },
  {"callout": {"tipo": "perigo", "titulo": "Nunca monte SQL com interpolação", "texto": "`DB.query(conn, $\"SELECT * FROM users WHERE nome = '{entrada}'\")` é injeção esperando para acontecer. Se `entrada` for `'; DROP TABLE users; --`, você acabou de perder a tabela. Com `?`, o valor é enviado separado do comando e nunca é interpretado como SQL."}},
  {"h2": "As operações"},
  {"table": {"head": ["Chamada", "Para"], "rows": [["`execute(conn, sql, params)`", "INSERT, UPDATE, DELETE, CREATE"], ["`execute_many(conn, sql, lista)`", "vários INSERT de uma vez"], ["`query(conn, sql, params)`", "várias linhas, como lista de vaults"], ["`query_one(conn, sql, params)`", "uma linha, ou `void`"], ["`count(conn, tabela)`", "atalho para `COUNT(*)`"]]}},
  { code: `DB.execute(conn, """CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL
)""")

DB.execute(conn, "INSERT INTO produtos (nome, preco) VALUES (?, ?)", ["Mouse", 80.0])

DB.execute_many(conn, "INSERT INTO produtos (nome, preco) VALUES (?, ?)", [
    ["Teclado", 200.0],
    ["Monitor", 1200.0]
])` },
  {"callout": {"tipo": "nota", "texto": "SQL multilinha precisa das aspas triplas `\"\"\"…\"\"\"` — uma string de aspas simples não cruza linhas."}},
  {"h3": "execute_many"},
  {"p": "Uma ida ao banco em vez de N. Para inserção em lote, a diferença de desempenho é grande."},
  {"h2": "Consultar"},
  { code: `todos := DB.query(conn, "SELECT nome, preco FROM produtos ORDER BY preco DESC")
cycle p in todos:
    out $"{p["nome"].pad_end(10)} R$ {p["preco"]}"

caro := DB.query_one(conn, "SELECT nome FROM produtos ORDER BY preco DESC LIMIT 1")` },
  {"p": "`query` devolve vaults com os nomes das colunas como chaves — dá para usar `p[\"nome\"]` direto, sem índices."},
  {"h2": "Transações"},
  { code: `DB.begin(conn)
DB.execute(conn, "UPDATE contas SET saldo = saldo - 100 WHERE id = 1")
DB.execute(conn, "UPDATE contas SET saldo = saldo + 100 WHERE id = 2")
DB.commit(conn)     # ou DB.rollback(conn)` },
  {"p": "As duas operações acontecem **juntas ou nenhuma**. Sem transação, uma falha entre elas deixaria dinheiro sumido."},
  {"p": "O padrão seguro combina com `monitor`:"},
  { code: `DB.begin(conn)
monitor:
    transferir(de, para, valor)
    DB.commit(conn)
handle e:
    DB.rollback(conn)
    propagate e.message` },
  {"h2": "Converter na fronteira"},
  { code: `record Produto:
    id: Integer
    nome: String
    preco: Number

action buscar_todos():
    linhas := DB.query(conn, "SELECT id, nome, preco FROM produtos")
    yield linhas >> morph l: Produto(l["id"], l["nome"], l["preco"])` },
  {"p": "Linhas do banco entram; records tipados saem. A partir dali, `p.nome` com verificação, não `l[\"nome\"]` com risco de digitar errado."},
  {"h2": "Regra de negócio no banco"},
  { code: `action emprestar(livro_id, leitor):
    ja := DB.query_one(conn, "SELECT id FROM emprestimos WHERE livro_id = ?", [livro_id])
    given ja isnt void:
        yield {"ok": no, "erros": ["livro ja emprestado"]}
    ...` },
  {"p": "\"Um livro só pode estar emprestado uma vez\" depende do estado atual — não dá para validar sem consultar. Por isso essa checagem fica na camada de persistência, não nas [regras puras](/docs/tecnicas/projeto)."},
  {"h2": "Introspecção"},
  { code: `DB.tables(conn)                  # as tabelas
DB.columns(conn, "produtos")     # as colunas
DB.table_exists(conn, "x")
DB.table_info(conn, "produtos")  # tipos e restrições
DB.close(conn)` },
];

const headings = [{ id: 'conectar', text: "Conectar", level: 2 as const }, { id: 'parametros-sempre', text: "Parâmetros, sempre", level: 2 as const }, { id: 'as-operacoes', text: "As operações", level: 2 as const }, { id: 'executemany', text: "execute_many", level: 3 as const }, { id: 'consultar', text: "Consultar", level: 2 as const }, { id: 'transacoes', text: "Transações", level: 2 as const }, { id: 'converter-na-fronteira', text: "Converter na fronteira", level: 2 as const }, { id: 'regra-de-negocio-no-banco', text: "Regra de negócio no banco", level: 2 as const }, { id: 'introspeccao', text: "Introspecção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Banco de dados"}
      description={"SQLite com Arcane.Database: consultas parametrizadas, transações e modelos."}
      href={"/docs/tecnicas/banco-de-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
