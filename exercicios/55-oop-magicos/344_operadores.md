# 344 — o objeto que entra numa conta

Sobrecarregar operador é o que faz um tipo de domínio parecer um
número.

## Eles compõem

`(a + b) * 2 - a` — e é a composição que justifica a sobrecarga: um
método com nome não compõe assim.

## Um tipo sem o operador recusa

Com uma mensagem que nomeia os dois lados.

## E a regra de quando NÃO sobrecarregar

Só quando a operação **tem** o significado do símbolo. Um `+` que
envia e-mail é pior que um método com nome ruim: o nome ruim pelo menos
pode ser lido.
