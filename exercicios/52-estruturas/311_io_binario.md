# 311 — gravar bytes num arquivo

A linguagem sabia **produzir** bytes — `Bytes`, `Estrutura`, `Crypto`
— e não sabia gravá-los. `IO.write` abre em modo texto com UTF-8.

## O byte que prova o ponto

`0xFF` sozinho não é UTF-8. Passá-lo por `IO.write` o destruiria, e o
arquivo sairia diferente do que entrou.

## Ele aceita o que os módulos devolvem

Bloco, cluster de números, texto ou bytes. Obrigar a lembrar de
`.bytes()` é a forma mais rápida de gravar a **representação em texto**
de um objeto no lugar do conteúdo dele.

## E o que não vira bytes é recusado

Inventar uma codificação ali grava outra coisa, em silêncio.
