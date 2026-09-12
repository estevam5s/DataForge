# Exercicio 220 — Um PDV: a venda inteira, ou nenhuma

## Enunciado

Registre uma venda: gravar o cabeçalho, gravar os itens e baixar o
estoque de cada um. Faça as três valerem **juntas**.

## O problema

Sem transação, um erro no meio deixa a venda registrada com o estoque
intacto — ou o estoque baixado sem venda nenhuma. Ninguém descobre até
o inventário, e aí não há como saber quais vendas foram afetadas.

```
       grava a venda   ✓
       grava o item 1  ✓
       baixa estoque 1 ✓
       grava o item 2  ✗  ← sem estoque
       ────────────────────
       sem transação:   a venda existe, com um item, e o estoque do
                        primeiro item foi baixado
       com transação:   nada aconteceu
```

## Conceitos

```dataforge
Banco.transacao(db, corpo)        // erro DESFAZ tudo
Banco.savepoint(db, "item", acao) // desfaz só uma parte
Banco.increment(db, "produtos", "estoque", -2, {"id": 7})
```

`Banco.transacao` devolve o que o corpo devolveu, e desfaz em **qualquer**
saída que não seja normal — inclusive num `halt` ou num `yield` que
atravesse o bloco. Deixar commitado o que já foi escrito seria a pior
das duas opções.

## Por que `increment` e não ler-somar-escrever

```dataforge
// errado, e o erro é silencioso
p := Banco.query_one(db, "SELECT estoque FROM produtos WHERE id = ?", [7])
Banco.update(db, "produtos", {"estoque": p["estoque"] - 1}, {"id": 7})

// certo: a soma é do banco, sob a trava da linha
Banco.increment(db, "produtos", "estoque", -1, {"id": 7})
```

Dois caixas vendendo o mesmo item ao mesmo tempo leem 10, ambos
escrevem 9, e uma unidade desaparece do controle sem nenhum erro
aparecer. Foi medido: em quatro threads fazendo 200 incrementos cada, a
forma ingênua perde cerca de um terço.

## `savepoint`: quando a regra é "vende o que tem"

Um item sem estoque não precisa derrubar a venda inteira. O savepoint é
uma transação **dentro** da transação: ele desfaz só a parte dele.

```dataforge
monitor:
    total += Banco.savepoint(db, "item", tentar_item)
handle Error as e:
    recusados.append(item["sku"])
```

O SQLite não aninha `BEGIN`, mas aninha savepoint —
`Banco.transacao` dentro de outra vira savepoint sozinho.

## O que este exercício mostra

| Parte | Ideia |
|---|---|
| 1 | a venda como uma unidade, dentro de `transacao` |
| 2 | uma venda que dá certo |
| 3 | uma que falha **no meio**, e não deixa rastro |
| 4 | `savepoint` para recusar um item sem perder a venda |

## Armadilha

Todo `insert` e `update` deste módulo confirma sozinho — **exceto**
dentro de uma transação. Foi um bug real: o primeiro `insert` de dentro
confirmava a transação inteira, e o `rollback` depois não tinha o que
desfazer. A venda ficava gravada com o estoque intacto, que é
exatamente o que a transação existe para evitar.
