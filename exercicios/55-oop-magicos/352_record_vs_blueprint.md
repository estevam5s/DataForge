# 352 — quando o record basta

Um `record` já traz `__eq__`, `__hash__` e a imutabilidade de graça.
Escrever um blueprint com esses três mágicos à mão é refazer o que a
linguagem faz — e errar num deles.

## O `with` confere as CHAVES

Um campo que não existe seria um erro de digitação gravando em lugar
nenhum.

## Quando o blueprint é o certo

Identidade, estado que muda, herança. Um contador **não** é um
record.

## E o record no `match`

A desestruturação por posição é o que faz o `match` ler como a
declaração.
