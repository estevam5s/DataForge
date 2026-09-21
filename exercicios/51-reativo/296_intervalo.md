# 296 — o fluxo que bate sozinho

`intervalo` é uma fonte fria com relógio: a forma de um painel se
atualizar.

## Ele não começa sem ninguém escutando

Um temporizador que roda sem assinante é trabalho jogado fora — e numa
thread que ninguém observa.

## Com teto, ele termina sozinho

E avisa o fim. A contagem começa em **zero**, como o `interval` de
todo framework reativo: o número é "quantas já passaram", e não "a
quantidade".

## Sem teto, quem para é o cancelamento

E ele para de verdade: a prova é o número não andar mais depois de uma
espera maior que várias batidas.
