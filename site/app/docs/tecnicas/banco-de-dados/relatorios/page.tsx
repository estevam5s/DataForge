// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_sqlite.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Relatórios e busca",
  description: "Agregação sem escrever SQL, busca textual com FTS5 e o plano de consulta que mostra o índice que falta.",
};

const blocos: Bloco[] = [
  {"p": "Três coisas que toda tela de gestão pede. As três têm uma versão ingênua que funciona com cem linhas e morre com cem mil."},
  {"h2": "Relatório agrupado"},
  { code: `adopt Arcane.Database as Banco

por_vendedor := Banco.aggregate(db, "vendas", {
    "receita": ["sum", "valor"],
    "vendas":  ["count", "*"],
    "ticket":  ["avg", "valor"]
}, group_by := "vendedor", order_by := "receita DESC")`, lang: 'df' },
  { code: `[{"vendedor": "ana",   "receita": 4820.0, "vendas": 30, "ticket": 160.6},
 {"vendedor": "bruno", "receita": 3910.0, "vendas": 27, "ticket": 144.8}]`, lang: 'text' },
  {"p": "As colunas do `group_by` saem **junto** com os agregados — que é o que um gráfico precisa. Dois grupos ao mesmo tempo também:"},
  { code: `Banco.aggregate(db, "vendas", {"receita": ["sum", "valor"]},
                group_by := ["categoria", "vendedor"])

// com filtro
Banco.aggregate(db, "vendas", {"total": ["sum", "valor"]},
                where := {"mes": "2026-03", "valor": {"gte": 50}})

// o atalho que mais se pede
Banco.group_count(db, "vendas", "categoria")
// [{"categoria": "bebida", "quantidade": 30}, …]`, lang: 'df' },
  {"p": "Aceita `count`, `sum`, `avg`, `min`, `max` e `total`. A lista é fechada **de propósito**: o nome da função vai cru para o SQL, e aceitar qualquer texto ali seria injeção pela porta da frente. Para outra agregação, escreva o SQL com `Banco.query` — e aí a responsabilidade é de quem escreveu."},
  {"callout": {"tipo": "atencao", "titulo": "O `order_by` vem de fora", "texto": "Numa listagem, `?ordenar=nome` chega do cliente, e nome de coluna não pode ir por parâmetro. `Banco.aggregate` confere pedaço por pedaço e recusa `\"valor; DROP TABLE vendas\"`; a direção também — só `ASC` e `DESC`."}},
  {"h2": "Busca textual"},
  { code: `-- o que quase todo mundo escreve
SELECT * FROM produtos WHERE nome LIKE '%cafe%'`, lang: 'sql' },
  {"p": "`LIKE` com `%` na frente **não usa índice nenhum**: ele lê a tabela inteira, sempre. O FTS5 do SQLite usa índice invertido e ordena por relevância."},
  { code: `Banco.create_search(db, "produtos", ["nome", "categoria"])

Banco.search(db, "produtos", "merce")        // acha "mercearia"
Banco.search(db, "produtos", "cafe 500", limit := 10)`, lang: 'df' },
  {"table": {"head": ["Detalhe", "Por quê"], "rows": [["prefixo na **última** palavra", "quem digita `livr` espera achar `livro` antes de terminar de escrever"], ["o índice se mantém em dia, por gatilhos", "sem eles ele envelhece em silêncio e a busca deixa de achar o que foi cadastrado depois — o pior defeito possível numa busca"], ["devolve a linha da tabela **original**", "quem busca quer o produto, não o índice"], ["o termo é escapado", "`MATCH` tem sintaxe própria: um termo com aspas ou `AND` quebraria a consulta ou mudaria o que ela procura"], ["o `LIMIT` é aplicado antes do `JOIN`", "com um milhão de linhas, junta-se vinte e não um milhão"]]}},
  {"callout": {"tipo": "nota", "titulo": "Um bug que valeu a lição", "texto": "A primeira versão montava a consulta como `\"livr*\"` — com o `*` **dentro** das aspas, onde ele é um caractere literal. A sintaxe de prefixo do FTS5 é `\"livr\"*`. A busca devolvia lista vazia, calada, e nenhum erro apareceu em lugar nenhum."}},
  {"p": "As quatro tabelas-sombra que o FTS5 cria para si (`_data`, `_idx`, `_docsize`, `_config`) não aparecem em `Banco.stats` — contá-las faria um banco de duas tabelas parecer ter dez."},
  {"h2": "O plano da consulta"},
  { code: `sem := Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": yes,
//  "aviso": "le a tabela inteira: SCAN vendas",
//  "passos": ["SCAN vendas"]}

Banco.create_index(db, "vendas", ["vendedor"])

com := Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": no, "aviso": "", "passos": ["SEARCH vendas USING INDEX …"]}`, lang: 'df' },
  {"p": "A linha que importa é a que diz **SCAN** em vez de SEARCH. SCAN lê a tabela inteira; num cadastro de 200 mil linhas é a diferença entre 2 ms e 2 s, e a resposta quase sempre é um índice."},
  { code: `indices := Banco.indexes(db, "vendas")
// [{"nome": "idx_vendas_vendedor", "tabela": "vendas",
//   "colunas": ["vendedor"], "automatico": no}, …]`, lang: 'df' },
  {"p": "`automatico: yes` é o índice que o SQLite criou sozinho para um `UNIQUE` ou `PRIMARY KEY` — ele existe, e não foi você que pediu."},
  {"h3": "Onde pôr índice"},
  {"table": {"head": ["Situação", "Índice"], "rows": [["toda chave estrangeira", "sempre — o SQLite **não** cria"], ["a coluna do `WHERE` de uma tela de listagem", "sim"], ["a coluna do `ORDER BY` de uma listagem grande", "sim; ele evita a ordenação"], ["as duas juntas, na mesma consulta", "um índice **composto**, na ordem `WHERE` → `ORDER BY`"], ["uma coluna com três valores possíveis", "não — o índice não separa nada"], ["uma tabela de cem linhas", "não — varrer é mais rápido"]]}},
  {"callout": {"tipo": "dica", "titulo": "Índice custa escrita", "texto": "Cada índice é uma árvore a atualizar em todo `INSERT` e `UPDATE`. Numa tabela de log com dez índices, gravar fica mais lento que ler. Meça com `explain` antes de acrescentar, e apague o que não aparece em nenhum plano."}},
  {"h2": "Um retrato do banco"},
  { code: `e := Banco.stats(db)
// {"caminho": "loja.db", "bytes": 4915200, "total_de_linhas": 182044,
//  "tabelas": [{"tabela": "vendas", "linhas": 180000,
//               "colunas": 7, "indices": 3}, …]}

Banco.integrity(db)          // {"ok": yes, "problemas": []}
Banco.check_foreign_keys(db) // as linhas que apontam para o nada`, lang: 'df' },
  {"p": "`check_foreign_keys` importa num banco que recebeu importação: `PRAGMA foreign_keys=ON` impede novas violações, mas não conserta as que entraram antes — e elas só aparecem quando alguém tenta usar o dado."},
  {"h2": "Ligando num painel"},
  { code: `adopt Arcane.Vitrine as V

mark @V.cache(validade := 60)
action receita_por_mes():
    yield Banco.aggregate(db, "vendas", {"receita": ["sum", "valor"]},
                          group_by := "mes", order_by := "mes")

action painel():
    V.titulo("Vendas")
    V.grafico_barras(receita_por_mes(), x := "mes", y := "receita")
    V.frame(Banco.group_count(db, "vendas", "vendedor"))`, lang: 'df' },
  {"p": "O `mark @V.cache` não é opcional aqui: o programa de um painel roda inteiro a cada clique, e sem cache mover um deslizante refaz a agregação. Ver [o projeto completo](/docs/vitrine/projeto)."},
];

const headings = [{ id: 'relatorio-agrupado', text: "Relatório agrupado", level: 2 as const }, { id: 'busca-textual', text: "Busca textual", level: 2 as const }, { id: 'o-plano-da-consulta', text: "O plano da consulta", level: 2 as const }, { id: 'onde-por-indice', text: "Onde pôr índice", level: 3 as const }, { id: 'um-retrato-do-banco', text: "Um retrato do banco", level: 2 as const }, { id: 'ligando-num-painel', text: "Ligando num painel", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Relatórios e busca"}
      description={"Agregação sem escrever SQL, busca textual com FTS5 e o plano de consulta que mostra o índice que falta."}
      href={"/docs/tecnicas/banco-de-dados/relatorios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
