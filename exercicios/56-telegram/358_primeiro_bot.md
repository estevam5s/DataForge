# 358 — um bot inteiro, testado sem token e sem rede

Um bot que só pode ser testado conversando com ele no celular não tem
teste nenhum. A sonda injeta updates e lê o que o bot mandou — e é ela
que faz um bot caber numa suíte.

## O despacho para no PRIMEIRO que casa

Entregar a todos parece mais flexível e produz o bug mais confuso que
um bot tem: duas respostas para uma mensagem, e ninguém sabe de onde
veio a segunda.

## O token nunca aparece

Ele está na URL de **toda** chamada, e a URL entra em todo traceback.
Um token num log de CI é um bot sequestrado.

## E nenhum socket foi aberto

O teste roda na suíte como qualquer outro.
