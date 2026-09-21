# 313 — o grupo nomeado que não chegava ao resultado

`(?P<ano>\d{4})` sempre compilou, e o nome **não** vinha no
resultado — ele chegava por posição. E ninguém escreve `(?P<ano>…)`
para depois ler `groups[2]`.

## O nome chega junto

`achado["named"]` é um vault. A posição continua em `groups`: havia
código lendo dali, e tirá-la seria quebrar o que funciona.

## `findnamed` lê um log linha a linha

Um vault por casamento — e daí em diante é filtrar e agrupar como
qualquer lista.

## E `named` vem vazio quando não há nomes

Ler `["named"]` não pode depender de o padrão ter nomes, senão toda
leitura viraria um `??`.
