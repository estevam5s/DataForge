# 282 — a família de erros do domínio

Levantar `RuntimeError` em tudo faria a distinção morrer na fronteira:
para quem escreve o `handle`, violar uma invariante e dividir por zero
viram a mesma coisa.

## Sete peças, sete classes

E cada uma diz de quem é a culpa: `ValueObjectError` é do valor,
`AggregateError` é da regra de negócio, `RepositoryError` é da consulta.

## A base pega todas

`handle DomainError` sem listar as nove.

## E ela NÃO pega um erro de fora

Senão `handle DomainError` viraria um `handle` sem tipo — e o
tratamento de domínio engoliria um bug de divisão por zero.
