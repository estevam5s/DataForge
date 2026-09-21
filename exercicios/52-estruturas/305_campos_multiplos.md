# 305 — um campo com várias posições

`rgba` é quatro bytes, e não quatro campos. Declarar a quantidade é o
que faz o molde saber o tamanho do registro sem contar à mão.

## Ler devolve um cluster

E a quantidade errada na escrita é recusada — um `rgba` com dois
valores sairia com dois bytes de lixo.

## Uma imagem de três pixels

As janelas percorrem, e a inversão escreve no lugar.

## E campos de tipos diferentes convivem

Bytes e `f32` no mesmo registro, cada um com a sua quantidade.
