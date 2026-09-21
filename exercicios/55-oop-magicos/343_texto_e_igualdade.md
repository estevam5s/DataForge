# 343 — como um objeto se mostra e se compara

Os três mais usados. `__str__` é para quem **lê**, `__repr__` é para
quem **depura**, e `__eq__` sem `__hash__` faz o objeto sumir de um
vault — e o Python não avisa.

## `repr` era inalcançável

`__repr__` estava na lista de mágicos, na referência e na doc, e a
linguagem não tinha como pedi-lo: não havia `repr`, e um cluster de
objetos imprime com `__str__`. Ele só era alcançado como **reserva**,
quando não havia `__str__` — ou seja, exatamente quando não se queria a
distinção.

## O par eq/hash nunca se separa

Sem `__hash__`, dois objetos iguais teriam hashes diferentes — e o
segundo não acharia o primeiro num vault.

## E sem os dois, o objeto só é igual a si mesmo

O que é o padrão certo: identidade é o que um blueprint tem por
natureza.
