# 340 — o que `monitor` NÃO pega

`halt`, `skip` e `yield` atravessam um `monitor`. Eles derivam de um
sinal de controle, e não de erro.

## Capturar um `yield` faria a ação devolver o tratamento

Em vez do valor. E o `ensure` **ainda** roda — a saída é garantida
sem que o sinal seja engolido.

## Num interpretador que capturasse tudo

O `halt` viraria uma mensagem de erro e o laço continuaria — o defeito
mais confuso que existe, porque o código **lê** certo.

## E `monitor` sem `handle` não engole nada

Ele só garante o `ensure`.
