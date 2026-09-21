# 281 — um caso de uso inteiro

As sete peças num fluxo só: reservar estoque e cobrar, com as duas
pontas numa unidade de trabalho, e o faturamento reagindo ao evento
**depois** da confirmação.

## O evento espera

Entre `pedido.pagar()` e `u.confirmar()` o faturamento não rodou. É a
janela em que a transação ainda podia ser desfeita.

## Pagar duas vezes é recusado

E a recusa mora no comando, que é onde a regra pode ser cobrada.

## E a consulta usa a regra da decisão

`pedidos.que(pagos)` — a mesma regra que decide é a que lista.
