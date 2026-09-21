# 348 — interceptar a leitura e a escrita

`__getattr__` responde pelo que **não** existe; `__getattribute__`
responde por **tudo** — e é a diferença entre um objeto flexível e uma
recursão infinita.

## O campo interno precisa existir antes

Um depósito criado no `setup` faria a primeira escrita entrar no
próprio `__setattr__` antes de haver onde guardar. Um campo
**declarado** com padrão mutável ganha uma cópia por instância, e já
existe quando o mágico roda.

## Escrita por ÍNDICE não passa pelo mágico de membro

É o que permite guardar sem recursão.

## E a propriedade, para UM campo

Quando só um campo precisa de lógica, ela é melhor que interceptar
tudo: ela diz na declaração o que faz. E ela é só leitura até alguém
escrever o `set`.
