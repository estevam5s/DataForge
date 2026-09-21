# 273 — ele guarda agregados INTEIROS

Um repositório que devolve meio agregado devolve um objeto cujas
invariantes ninguém pode garantir. Por isso ele não tem
`atualizar_campo` nem consulta por coluna.

## As duas perguntas existem

`por_id` devolve `void`; `exigir` levanta. Uma só obrigaria metade das
chamadas a tratar um `void` que nunca acontece.

## A consulta usa a MESMA regra da decisão

`pedidos.que(grande)` — e não um segundo filtro escrito à mão.

## E um objeto de VALOR não entra

Ele não tem identidade, e não tem porque dois iguais são o mesmo. Se a
sua peça precisa distinguir duas instâncias iguais, ela é uma
**entidade** — e o módulo diz isso em vez de deixar passar.
