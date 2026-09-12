// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_sqlite.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Banco de dados",
  description: "SQLite com CRUD, transações que desfazem, upsert, paginação, relatório agrupado, busca textual e plano de consulta — 63 símbolos, sem dependência.",
};

const blocos: Bloco[] = [
  {"p": "`Arcane.Database` é o SQLite, que vem com o Python. Um arquivo, transação real, chave estrangeira, índice, busca textual — e nada a instalar."},
  { code: `adopt Arcane.Database as Banco

db := Banco.connect("loja.db")      // ou Banco.memory(), para teste

Banco.create_table(db, "produtos", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "sku": "TEXT NOT NULL UNIQUE",
    "nome": "TEXT NOT NULL",
    "preco": "REAL NOT NULL CHECK (preco >= 0)",
    "estoque": "INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)"
})

Banco.upsert(db, "produtos", {"sku": "CAF-500", "nome": "Café 500g",
                              "preco": 32.9, "estoque": 20}, "sku")

out Banco.count(db, "produtos")`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Forge, para os outros cinco motores", "texto": "Este módulo é só SQLite. Para PostgreSQL, MySQL, MariaDB, MongoDB e Redis pela mesma interface, [`Arcane.Forge`](/docs/banco-de-dados) — também sem dependência, com um driver por protocolo."}},
  {"h2": "Projetos completos"},
  {"p": "As rotas abaixo não explicam funções: elas constroem um sistema, do schema ao relatório."},
  {"cards": [{"href": "/docs/tecnicas/banco-de-dados/crud", "title": "CRUD completo", "meta": "livraria, biblioteca, PDV, estoque", "desc": "Cinco sistemas com o mesmo esqueleto, e o que muda entre eles."}, {"href": "/docs/tecnicas/banco-de-dados/relatorios", "title": "Relatórios e busca", "meta": "agregação, FTS5, plano", "desc": "O que toda tela de gestão pede, e a versão que aguenta cem mil linhas."}, {"href": "/docs/tecnicas/banco-de-dados/migracoes", "title": "Migrações", "meta": "ida, volta e histórico", "desc": "Mudar o schema de um banco que tem dado dentro."}]},
  {"h2": "Parâmetros, sempre"},
  { code: `// certo
Banco.query(db, "SELECT * FROM produtos WHERE sku = ?", [sku])

// errado, e é assim que um banco é apagado
Banco.query(db, $"SELECT * FROM produtos WHERE sku = '{sku}'")`, lang: 'df' },
  {"p": "Toda função deste módulo que aceita valor o passa por `?`. Nome de **coluna**, de tabela e de índice não pode ir por parâmetro — o SQLite não aceita — e por isso vai concatenado; para esses, o módulo **recusa** o que não parece um nome:"},
  { code: `Banco.aggregate(db, "vendas", {"n": ["count", "*"]},
                order_by := "valor; DROP TABLE vendas")
// erro: 'valor; DROP TABLE vendas' nao e um nome valido de tabela ou coluna`, lang: 'df' },
  {"p": "Isso importa porque o `order_by` de uma listagem vem de fora — `?ordenar=nome`."},
  {"h2": "CRUD"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`Banco.insert(db, tabela, vault)`", "insere; devolve o `id`"], ["`Banco.insert_many(db, tabela, cluster)`", "insere muitos"], ["`Banco.insert_or_ignore(db, tabela, vault)`", "não reclama se a chave existe; devolve `0`"], ["`Banco.upsert(db, tabela, vault, chaves)`", "insere **ou** atualiza; devolve `\"inserido\"`/`\"atualizado\"`"], ["`Banco.upsert_many(db, tabela, cluster, chaves)`", "o mesmo, numa transação só"], ["`Banco.select(db, tabela, where, order_by, limit)`", "lê"], ["`Banco.query(db, sql, params)`", "SQL livre, como cluster de vaults"], ["`Banco.query_one(db, sql, params)`", "a primeira linha, ou `void`"], ["`Banco.update(db, tabela, vault, where)`", "altera; devolve quantas linhas"], ["`Banco.increment(db, tabela, coluna, delta, where)`", "`coluna = coluna + ?`, no banco"], ["`Banco.delete(db, tabela, where)`", "apaga"], ["`Banco.count(db, tabela, where)`", "conta"], ["`Banco.exists(db, tabela, where)`", "`yes`/`no`"], ["`Banco.paginate(db, tabela, pagina, por_pagina, …)`", "uma fatia, com o total e o número de páginas"]]}},
  {"h3": "A condição"},
  { code: `{"id": 7}                       // id = 7
{"id": [1, 2, 3]}               // id IN (1, 2, 3)
{"preco": {"gte": 10}}          // preco >= 10
{"nome": {"like": "caf%"}}      // nome LIKE 'caf%'
{"nota": void}                  // nota IS NULL`, lang: 'text' },
  {"p": "Operadores: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `like`. Um cluster **vazio** não casa com nada — `IN ()` é erro de sintaxe no SQLite, e a resposta certa para \"nenhum dos valores\" é não casar com nada."},
  {"callout": {"tipo": "nota", "titulo": "`void` vira `IS NULL`", "texto": "`coluna = NULL` nunca é verdadeiro em SQL, nem quando a coluna é nula. Quem escreve `void` quer dizer \"está vazio\", e é isso que o módulo gera."}},
  {"h2": "Escrita que não duplica"},
  {"p": "O catálogo que chega por CSV toda noite, o cliente que se cadastra duas vezes, o produto que dois caixas lançam ao mesmo tempo:"},
  { code: `Banco.upsert(db, "produtos", dados, "sku")      // "inserido" ou "atualizado"

r := Banco.upsert_many(db, "produtos", lote, "sku")
out $"{r["inseridos"]} novos, {r["atualizados"]} atualizados"`, lang: 'df' },
  {"p": "As chaves de conflito precisam ter índice **UNIQUE** — é o SQLite que decide, não um `SELECT` antes do `INSERT`. A diferença importa: entre o `SELECT` e o `INSERT`, outra thread pode inserir a mesma chave, e o código \"confere e depois grava\" **perde a corrida** sem nada denunciando."},
  {"h2": "Transações"},
  { code: `action vender(sku, quantos):
    action corpo():
        p := Banco.query_one(db, "SELECT * FROM produtos WHERE sku = ?", [sku])
        given p["estoque"] smaller quantos:
            trigger $"estoque insuficiente de {p["nome"]}"
        Banco.insert(db, "vendas", {"produto_id": p["id"],
                                    "quantidade": quantos,
                                    "valor": p["preco"] * quantos})
        Banco.increment(db, "produtos", "estoque", -quantos, {"id": p["id"]})
        yield p["preco"] * quantos

    yield Banco.transacao(db, corpo)`, lang: 'df' },
  {"p": "Erro **desfaz tudo**. É a peça que falta num PDV: gravar a venda, baixar o estoque e lançar o pagamento são três escritas que precisam valer juntas."},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`Banco.transacao(db, acao)`", "roda a ação; erro desfaz; devolve o que ela devolveu"], ["`Banco.savepoint(db, nome, acao)`", "uma transação **dentro** de outra"], ["`Banco.in_transaction(db)`", "estamos dentro de uma agora?"], ["`Banco.begin` · `commit` · `rollback`", "à mão — prefira `transacao`"]]}},
  {"p": "Uma `transacao` dentro de outra vira savepoint sozinha: o SQLite não aninha `BEGIN`, mas aninha savepoint. O savepoint desfaz **só a parte dele** — um item sem estoque não precisa derrubar a venda inteira."},
  {"callout": {"tipo": "atencao", "titulo": "Por que não `begin` à mão", "texto": "`begin` obriga a não esquecer o `rollback` em **nenhum** caminho de saída, inclusive no que dispara. Esquecer deixa a conexão travada para as outras threads — e o sintoma é um servidor que fica lento sem motivo aparente."}},
  {"h3": "`increment`, e não ler-somar-escrever"},
  { code: `// errado, e o erro é silencioso
p := Banco.query_one(db, "SELECT estoque FROM produtos WHERE id = ?", [7])
Banco.update(db, "produtos", {"estoque": p["estoque"] - 1}, {"id": 7})

// certo: a soma é do banco, sob a trava da linha
Banco.increment(db, "produtos", "estoque", -1, {"id": 7})`, lang: 'df' },
  {"p": "Dois caixas vendendo o mesmo item ao mesmo tempo leem 10, os dois escrevem 9, e uma unidade desaparece do controle **sem nenhum erro aparecer**. Foi medido: quatro threads fazendo 200 incrementos cada perdem cerca de um terço na forma ingênua."},
  {"h2": "Schema"},
  { code: `Banco.create_table(db, nome, esquema)
Banco.drop_table(db, nome)
Banco.table_exists(db, nome)      Banco.tables(db)
Banco.columns(db, tabela)         Banco.table_info(db, tabela)
Banco.add_column(db, tabela, nome, tipo)
Banco.create_index(db, tabela, colunas, unique := yes, name := "idx_x")
Banco.drop_index(db, nome)
Banco.schema_sql(db)              // o CREATE como o SQLite o guarda
Banco.foreign_keys(db, tabela)    // as chaves, legíveis
Banco.check_foreign_keys(db)      // as linhas que apontam para o nada`, lang: 'df' },
  {"p": "`PRAGMA foreign_keys=ON` já vem ligado na conexão. Ele impede **novas** violações, mas não conserta as que entraram antes — um banco importado de CSV costuma ter várias, e `check_foreign_keys` é o que as encontra."},
  {"h2": "Construtor de consultas"},
  { code: `Banco.builder(db, "vendas")
    .select("vendedor", "valor")
    .where("valor", ">", 100)
    .and_where("mes", "=", "2026-03")
    .order_by("valor", "DESC")
    .limit(20)
    .get()`, lang: 'df' },
  {"p": "E `where_in`, `where_null`, `where_between`, `where_like`, `join`, `left_join`, `group_by`, `having`, `offset`. Os terminais: `get`, `first`, `count`, `sum`, `avg`, `max`, `min`, `insert`, `update`, `delete` — e `to_sql`, que mostra o SQL sem executar."},
  {"h2": "Diagnóstico"},
  { code: `Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": yes, "aviso": "le a tabela inteira: SCAN vendas", …}

Banco.indexes(db, "vendas")     // com as colunas de cada um
Banco.stats(db)                 // tabelas, linhas, índices, bytes
Banco.integrity(db)             // o 'integrity_check' do SQLite`, lang: 'df' },
  {"p": "A linha que importa no `explain` é a que diz **SCAN** em vez de SEARCH: SCAN lê a tabela inteira, e num cadastro de 200 mil linhas é a diferença entre 2 ms e 2 s. A resposta quase sempre é um índice."},
  {"h2": "Entrada e saída"},
  { code: `Banco.export_csv(db, "vendas", "vendas.csv")
Banco.export_json(db, "vendas", "vendas.json")
Banco.import_csv(db, "vendas", "vendas.csv")
Banco.import_json(db, "vendas", "vendas.json")
Banco.backup(db, "copia.db")      // cópia consistente, com o banco em uso
Banco.vacuum(db)                  // devolve o espaço das linhas apagadas`, lang: 'df' },
  {"h2": "Concorrência"},
  {"p": "A conexão é utilizável de **várias threads** — o acesso é serializado por uma trava, e o modo `WAL` fica ligado. Sem isso, a primeira consulta de qualquer servidor estoura com `SQLite objects created in a thread can only be used in that same thread`."},
  {"p": "O que a trava **não** protege é a lógica de quem lê-e-depois-escreve. Para isso, `increment`, `upsert` e `transacao`."},
  {"h2": "Testar"},
  { code: `db := Banco.memory()     // em memória, some ao terminar`, lang: 'df' },
  {"p": "E, para que um teste que grava não seja visto pelo seguinte, [`Crucible.banco(db)`](/docs/tecnicas/instantaneos) abre uma transação e a desfaz no fim de cada trial."},
];

const headings = [{ id: 'projetos-completos', text: "Projetos completos", level: 2 as const }, { id: 'parametros-sempre', text: "Parâmetros, sempre", level: 2 as const }, { id: 'crud', text: "CRUD", level: 2 as const }, { id: 'a-condicao', text: "A condição", level: 3 as const }, { id: 'escrita-que-nao-duplica', text: "Escrita que não duplica", level: 2 as const }, { id: 'transacoes', text: "Transações", level: 2 as const }, { id: 'increment-e-nao-ler-somar-escrever', text: "`increment`, e não ler-somar-escrever", level: 3 as const }, { id: 'schema', text: "Schema", level: 2 as const }, { id: 'construtor-de-consultas', text: "Construtor de consultas", level: 2 as const }, { id: 'diagnostico', text: "Diagnóstico", level: 2 as const }, { id: 'entrada-e-saida', text: "Entrada e saída", level: 2 as const }, { id: 'concorrencia', text: "Concorrência", level: 2 as const }, { id: 'testar', text: "Testar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Banco de dados"}
      description={"SQLite com CRUD, transações que desfazem, upsert, paginação, relatório agrupado, busca textual e plano de consulta — 63 símbolos, sem dependência."}
      href={"/docs/tecnicas/banco-de-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
