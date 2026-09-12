# Exercicio 219 — Um CRUD completo, com o banco fazendo o trabalho

## Enunciado

Uma livraria: cadastro, listagem paginada, edição e exclusão. Ponha a
regra **no banco**, e não na memória do processo.

## Conceitos

```dataforge
adopt Arcane.Database as Banco

Banco.upsert(db, "livros", dados, "isbn")     // insere ou atualiza
Banco.insert_or_ignore(db, "autores", dados)  // não reclama se já existe
Banco.paginate(db, "livros", 2, 20, order_by := "titulo")
Banco.update(db, "livros", {"preco": 89.9}, {"isbn": "978-1"})
Banco.delete(db, "livros", {"isbn": "978-3"})
```

## Por que a regra vai no banco

| Na memória | No banco |
|---|---|
| `SELECT` e depois `INSERT` | `UNIQUE` + `upsert` |
| conferir estoque e subtrair | `estoque = estoque - ?` |
| verificar se o autor tem livro | `REFERENCES autores(id)` |
| validar preço ≥ 0 no código | `CHECK (preco >= 0)` |

A coluna da esquerda funciona até dois processos rodarem ao mesmo
tempo. Entre o `SELECT` e o `INSERT` outra thread pode inserir a mesma
chave, e o código "confere e depois grava" **perde a corrida** sem nada
denunciando — o resultado é uma linha duplicada que ninguém sabe
explicar.

A da direita é o banco decidindo, sob a trava dele.

## `UNIQUE` não é enfeite

É o que permite o `upsert`: sem um índice único no ISBN, o
`ON CONFLICT` não tem em que se apoiar. Toda escrita idempotente
começa por declarar qual é a identidade da linha.

## Paginação

`Banco.paginate` devolve o que a tela precisa, e não só a fatia:

```dataforge
{
    "itens": [...],       "pagina": 2,      "por_pagina": 20,
    "total": 143,         "paginas": 8,
    "tem_anterior": yes,  "tem_proxima": yes
}
```

Sem `total` e `paginas` a tela não sabe desenhar a paginação, e
calcular isso à mão é a mesma consulta escrita duas vezes.

`por_pagina` tem teto de 500: o número vem de fora numa rota, e
`?por_pagina=1000000` é como se derruba um servidor sem exploit.

## O que este exercício mostra

| Parte | Ideia |
|---|---|
| 1 | o schema com `UNIQUE`, `REFERENCES` e `CHECK` |
| 2 | `upsert` — cadastrar duas vezes atualiza, não duplica |
| 3 | leitura paginada, e a junção que traz o nome do autor |
| 4 | `update` com condição |
| 5 | `delete`, e a chave estrangeira recusando apagar um autor com livro |
| 6 | o `CHECK` recusando preço negativo |

## Continua em

[220 — PDV e transações](220_pdv_e_transacoes.df), onde três escritas
precisam valer juntas.
