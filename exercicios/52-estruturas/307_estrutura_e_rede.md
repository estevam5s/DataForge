# 307 — um protocolo de linha

Quase todo protocolo binário tem a mesma forma: cabeçalho de tamanho
fixo dizendo o tipo e o comprimento, e um corpo de tamanho variável logo
depois.

## O cabeçalho é empacotado

Três bytes, sem enchimento: num protocolo de rede o alinhamento não
ajuda, e cada byte a mais é banda.

## Ler quadros em sequência

O laço anda pelo bloco lendo cabeçalho e corpo, e para quando não há
mais um cabeçalho inteiro.

## E um quadro cortado no meio não é entregue

É o defeito clássico de quem trata um `recv` curto como a mensagem
inteira: o próximo quadro sai corrompido, e o sintoma é uma conexão que
funciona e de repente para.
