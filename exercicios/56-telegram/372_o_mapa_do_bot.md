# 372 — o mapa, e as cinco decisões

As sete formas de casar um update, a ordem que importa, e as decisões
que o módulo toma por você — com o motivo de cada uma.

## `qualquer` vai por ÚLTIMO, e isso é cobrado

Ela casa com tudo: uma rota registrada depois nunca seria alcançada, e
o sintoma é o bot responder "não entendi" a um comando que existe.
Registrar nessa ordem é **recusado**, na partida.

## O caminho inteiro, em cinco linhas

`new`, o token do @BotFather, `doctor`, `run` e `webhook`.

## E o que testar onde

Lógica na sonda; ambiente no `doctor`; formato da mensagem só o
Telegram de verdade responde.
