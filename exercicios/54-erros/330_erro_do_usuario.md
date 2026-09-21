# 330 — o erro que o programa inventa

Não há hierarquia de exceção do usuário, e o que substitui é melhor
para quem trata: um **record** com os campos do problema. Uma classe
vazia só carrega o nome; o record leva o saldo, o valor pedido e a
diferença.

## E `handle <Nome>` o captura pelo nome

Isso não funcionava: `_error_matches` consultava `tipo_usuario` e
**nada** o escrevia. O ramo existia, tinha docstring, e era
inalcançável — quem levantava um record só podia capturá-lo com
`handle Error` e um `match`.

## O valor original viaja em `e.value`

Os campos, e não o texto. Extrair por regex o que o programa já tinha
como dado é o que isso evita.

## E um texto levantado NÃO ganha nome

Senão `handle String` capturaria todo `trigger "…"` do programa.
