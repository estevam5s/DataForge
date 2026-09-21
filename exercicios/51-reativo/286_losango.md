# 286 — o valor que nunca existiu

Num losango — `c` lê `a` e `b`, e `b` lê `a` — marcar e avisar numa
fase só entrega um número **errado**, que aparece e some sozinho.

## O 7 nunca foi verdade

Com `a = 5`, o certo é 15. O 7 era `5 + o b antigo`: `b` ainda estava
limpo quando `c` recalculou. E a lista de dependentes é um **conjunto**,
então qual caminho vem primeiro não é escolhido por ninguém — o defeito
ia e vinha conforme a ordem de hash.

## A marcação percorre o grafo inteiro primeiro

Só depois os efeitos e ouvintes rodam. Quando eles rodam, todo
derivado alcançado já sabe que está sujo.

## E o efeito alcançado por dois caminhos roda uma vez

Deduplicado pelo próprio objeto — e não por `id()`, que só é único
entre objetos **vivos**.

---

Não é uma notificação a mais: é um valor errado na tela. Um defeito
que produz o número certo *depois* é mais difícil de achar que um que
estoura.
