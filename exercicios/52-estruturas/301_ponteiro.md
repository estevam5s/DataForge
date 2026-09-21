# 301 — andar por ELEMENTO, e não por byte

`p + 1` num `u32*` do C anda **quatro** bytes. Andar um byte é um
índice, não um ponteiro.

## O passo é o tamanho do tipo

E `distancia` responde na mesma unidade. Entre tipos diferentes ela é
recusada: a conta é em elementos, e dois tipos têm tamanhos
diferentes.

## O cast reinterpreta o MESMO endereço

Os mesmos quatro bytes, três leituras — é o que uma união faz, com
outra sintaxe.

## E a faixa vem do TIPO declarado

*"um u8 vai de 0 a 255"*, e não `'B' format requires 0 <= number <=
255`: quem escreveu `u8` não tem como ligar uma coisa à outra.
