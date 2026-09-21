# 323 — compilar uma vez, usar muitas

Um padrão usado num laço é recompilado a cada volta — e o Python tem
um cache interno, então a diferença é pequena.

## O compilado tem TODAS as operações

Ele tinha cinco, na forma que a doc recomenda para um laço: quem
compilava perdia `finditer`, os grupos nomeados e `fullmatch` — e
voltava a chamar a versão por texto, que é o contrário do motivo de
compilar.

## A medida compara um FATOR

`assert a bigger b` entre dois números de microssegundos é um
sorteio. E o que se **afirma** é o que se mede: o compilado não é mais
lento — e não "é muito mais rápido", que seria inventar.

## O que muda de verdade é a LEITURA

O padrão ganha um nome, num lugar só.
