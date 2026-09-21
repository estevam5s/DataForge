# 317 — depurar um padrão

Um padrão que devolve a lista errada quase sempre casa num lugar que
não se esperava — e uma lista de resultados não diz **onde**.

## `highlight` marca

E é assim que se vê o padrão ganancioso: `.*` come tudo até o último
fecho; `.*?` para no primeiro.

## `positions` responde em linha e coluna

A posição em bytes de um `span` não serve para apontar num arquivo:
quem lê um erro procura linha e coluna. E a coluna começa em **um**.
