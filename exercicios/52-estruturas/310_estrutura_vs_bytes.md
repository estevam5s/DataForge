# 310 — quando usar cada um dos três

`Arcane.Bytes` empacota por formato, `Arcane.Estrutura` por nome, e
`Arcane.C` fala com biblioteca nativa. Escolher o errado não dá erro —
dá código que ninguém consegue ler depois.

## A diferença está na LEITURA

Os mesmos oito bytes: `lista[1]` não diz o que é; `vault["versao"]`
diz.

## O formato não conhece alinhamento

`u8 u32` empacotado tem 5 bytes nos dois. Mas o C escreve 8, e é o
molde alinhado que reproduz isso.

## E a regra, em uma frase

Formato: um punhado de campos lidos em sequência. Molde: um registro
com nome, que se repete num arquivo. FFI: quando o layout é de **outro
programa**, em C.
