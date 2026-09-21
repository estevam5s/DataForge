# 351 — copiar sem levar o que não se quer

A cópia **rasa** compartilha o que está dentro. Mudar a lista da cópia
muda a do original — e o defeito aparece longe, numa outra instância que
ninguém tocou.

## Sem `__copy__`, a lista é a MESMA lista

E com cópia funda, não. Os dois mágicos existem para o objeto decidir
o que atravessa.

## Congelar recusa a escrita

Com uma mensagem que nomeia o campo.

## E a serialização só reconstrói o AUTORIZADO

Um desserializador que aceita qualquer tipo é uma porta de entrada: o
**dado** escolheria a classe a instanciar.
