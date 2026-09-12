# Exercicio 221 — Relatório, busca e o índice que falta

## Enunciado

Três coisas que toda tela de gestão pede. As três têm uma versão
ingênua que funciona com cem linhas e morre com cem mil.

## Conceitos

```dataforge
Banco.aggregate(db, "vendas",
                {"receita": ["sum", "valor"], "vendas": ["count", "*"]},
                group_by := "vendedor", order_by := "receita DESC")

Banco.group_count(db, "vendas", "categoria")

Banco.create_search(db, "produtos", ["nome", "sku"])
Banco.search(db, "produtos", "cafe")

Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
Banco.indexes(db, "vendas")
Banco.stats(db)
```

## Relatório sem escrever SQL

As colunas do `group_by` saem junto com os agregados — que é o que um
gráfico precisa:

```
[{"vendedor": "ana", "receita": 4820.0, "vendas": 30, "ticket": 160.6},
 {"vendedor": "bruno", "receita": 3910.0, ...}]
```

Aceita `count`, `sum`, `avg`, `min`, `max` e `total`. A lista é fechada
**de propósito**: o nome da função vai cru para o SQL, e aceitar
qualquer texto ali seria injeção pela porta da frente. Para outra
agregação, escreva o SQL com `Banco.query` — e aí a responsabilidade é
de quem escreveu.

## O nome de coluna é conferido

Valor vai por `?`, sempre. Mas nome de coluna, de tabela e de índice
**não pode ir por parâmetro** — o SQLite não aceita — e portanto vai
concatenado. É a porta de injeção, e a única defesa é recusar o que não
parece um nome:

```dataforge
Banco.aggregate(db, "vendas", {"n": ["count", "*"]},
                order_by := "valor; DROP TABLE vendas")
// erro: 'valor; DROP TABLE vendas' nao e um nome valido
```

Isso importa porque o `order_by` de uma listagem vem de fora
(`?ordenar=nome`).

## Busca textual contra `LIKE`

```sql
WHERE produto LIKE '%cafe%'     -- lê a tabela inteira, sempre
```

`LIKE` com `%` na frente não usa índice nenhum. O FTS5 usa índice
invertido e ordena por relevância:

```dataforge
Banco.create_search(db, "produtos", ["nome", "categoria"])
Banco.search(db, "produtos", "merce")     // acha "mercearia"
```

Três detalhes que fazem a diferença:

- **Prefixo na última palavra.** Quem digita `livr` espera achar
  `livro` antes de terminar de escrever.
- **O índice se mantém em dia**, por gatilhos. Sem eles ele envelhece
  em silêncio e a busca deixa de achar o que foi cadastrado depois — o
  pior defeito possível numa busca.
- **Devolve a linha da tabela original.** Quem busca quer o produto,
  não o índice.

## O plano da consulta

A linha que importa é a que diz `SCAN` em vez de `SEARCH`:

```dataforge
Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": yes, "aviso": "le a tabela inteira: SCAN vendas"}

Banco.create_index(db, "vendas", ["vendedor"])
// {"varre_tabela": no, "aviso": ""}
```

`SCAN` lê a tabela inteira. Num cadastro de 200 mil linhas é a
diferença entre 2 ms e 2 s, e a resposta quase sempre é um índice.

## Armadilha

`Banco.stats` **não** conta as tabelas-sombra do FTS5 (`_data`, `_idx`,
`_docsize`, `_config`). Contá-las faria um banco de duas tabelas
parecer ter dez — e foi o que acontecia.
