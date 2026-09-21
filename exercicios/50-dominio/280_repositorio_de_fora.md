# 280 — o mesmo contrato sobre outro armazém

`D.repositorio` guarda em memória; `D.repositorio_de` recebe as ações
de ler e gravar. O contrato é o mesmo, e é ele que importa.

## Quem chama não sabe onde o dado mora

A mesma ação recebe os dois e responde igual. É o teste de que a
abstração vale alguma coisa.

## E a ausência responde igual

`por_id` devolve `void` e `exigir` levanta nos dois — senão trocar o
armazém mudaria o comportamento do código que o usa.
