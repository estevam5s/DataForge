# 316 — partir sem perder o separador

`split` descarta os separadores. Reconstruir o texto depois de
transformar os pedaços exige saber o que havia entre eles — e adivinhar
ali é como um `join(" ")` transforma tabulação em espaço sem ninguém
ver.

## E é por isso que ele reconstrói

`join("", pedacos)` devolve o texto inteiro, byte a byte.

## `between` recorta entre marcas

E uma abertura sem fecho não entrega meio pedaço.
