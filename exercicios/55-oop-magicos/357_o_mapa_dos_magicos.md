# 357 — o mapa, e os três que NÃO existem

Fechar o módulo com a lista do que cada mágico responde, e com a lista
do que a linguagem **deliberadamente** não delega. A segunda é a que
evita procurar um recurso que não existe.

## Não há `__len__`, `__bool__` nem `__iter__` na tabela de protocolos

Eles existem como mágicos chamáveis, e não decidem a verdade nem a
iteração por baixo: o interpretador pergunta `if obj:` sobre
instâncias.

## A regra de quando declarar

`__str__` sempre que o objeto aparece num log. `__eq__` quando dois
objetos iguais **devem** ser o mesmo. `__hash__` sempre junto com
`__eq__`.

## E o record já dá os três de graça

Igualdade, hash e imutabilidade, sem escrever nada.
