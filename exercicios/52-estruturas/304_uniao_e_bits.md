# 304 — os mesmos bytes, dois nomes

Numa união todos os campos moram no deslocamento zero, e o tamanho é o
do maior.

## Escrever um, ler o outro

`1.0` em IEEE 754 de 32 bits é `0x3F800000` — e ler como `u32` devolve
exatamente isso. É o ponto da união, e também o que a torna perigosa
quando o tipo escrito não é registrado em lugar nenhum.

## Ler bits de um campo

Oito booleanos num byte: o que um campo de flags é, em todo protocolo
binário.

## E os dois módulos falam dos mesmos bytes

`Arcane.Bytes` por formato, `Arcane.Estrutura` por nome.
