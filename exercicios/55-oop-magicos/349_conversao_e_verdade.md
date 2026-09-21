# 349 — quanto vale, e se é verdade

`__int__`, `__float__` e `__bool__` decidem o que acontece num
`int(x)`, num `float(x)` e num `given x:`.

## `__bool__` é o mais perigoso dos três

Ele muda a verdade de **todo** objeto daquele tipo. Sem ele, zero
graus seria falso — e "não há leitura" e "está zero" viram a mesma
coisa.

## `__len__` NÃO decide a verdade aqui

Em Python, um objeto com `len()` 0 é falso. Aqui não: o interpretador
pergunta `if obj:` sobre instâncias, e um `__len__` mudaria a verdade de
todo objeto que declara tamanho.

## E por isso se pergunta o TAMANHO

`len(x) is 0` é explícito e funciona nas duas linguagens; `not x`
depende do tipo.
