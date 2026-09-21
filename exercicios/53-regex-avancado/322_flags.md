# 322 — as três flags

`IGNORECASE`, `MULTILINE` e `DOTALL` mudam o significado do **mesmo**
padrão. Escolher a errada não dá erro — dá uma lista com resultados a
mais ou a menos, e ninguém confere.

## `MULTILINE` muda o que `^` e `$` querem dizer

Sem ela, do **texto**; com ela, de cada **linha**.

## `DOTALL` faz o `.` atravessar a quebra

E aí o erro clássico: `.*` com `DOTALL` num HTML engole tudo até o
último fecho. O `?` é o que separa 1 de 2.

## E a flag vale nas funções novas também

`is_exactly`, `named` e `findnamed` a recebem como as antigas.
