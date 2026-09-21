# 369 — onde o estado do chat mora

O armazém padrão é a memória, e isso está **dito**: some quando o
processo reinicia.

## Em arquivo, sobrevive

E a troca é uma linha — `Tg.estado_em_arquivo(pasta)` no lugar do
padrão.

## `ctx.estado` é uma VISTA, e não uma cópia

A primeira versão devolvia `dict(...)`: `ctx.estado["k"] := v`
escrevia num dicionário descartável, a mudança sumia, e a documentação
prometia o contrário. O sintoma era um carrinho que nunca enchia.

## E a foto, para quem quer a cópia

`para_vault()` devolve o instantâneo, e ele não acompanha mais.
