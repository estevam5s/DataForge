# 308 — o bloco, e o que ele promete

`liberar()` não devolve memória ao sistema — quem faz isso é o
CPython. O que ele faz é **marcar**.

## A fatia é um bloco NOVO

Mexer nela não mexe no original: é cópia, e não janela.

## O bloco liberado responde

E a janela sobre ele também. Num mundo com coletor, a memória nunca
esteve em risco; o que se protege é o **protocolo**.

## E os dois módulos conversam

`Est.de_bytes(By.empacotar(...))` — o mesmo dado, duas formas de
nomeá-lo.
