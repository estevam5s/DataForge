# 297 — quatro formas de lidar com mudança

A linguagem tem `Arcane.Eventos` (um emissor), `Arcane.Stream`
(tópicos com offset), `stream action` (um gerador preguiçoso) e o
reativo. Elas não resolvem o mesmo problema, e escolher a errada é de
onde vem metade da complicação.

## O emissor não guarda estado

A pergunta *"qual foi o último pedido pago?"* não tem resposta nele.

## O gerador é puxado; o observável é empurrado

No primeiro, quem manda é quem consome. No segundo, quem produz.

## E o derivado é o que nenhum dos outros dá

*"Este total é sempre a soma daqueles três"* — sem callback, sem
assinatura, sem recalcular à mão.

## As duas pontes

`para_sinal` leva o fluxo para o mundo dos valores; `observar` leva o
valor para o mundo dos fluxos.
