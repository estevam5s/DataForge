# 328 — capturar por FAMÍLIA, e não por nome

São mais de duzentos códigos. Comparar nomes exatos obrigaria a listar
cada um; a herança deixa `handle RuntimeError` pegar os vinte da
família, e quem precisa distinguir ainda nomeia o específico.

## A ORDEM dos `handle` importa

O primeiro que casa vence. Com `Error` no topo, nada abaixo dele seria
alcançado — do específico ao geral, sempre.

## `trigger` levanta `TriggerError`, e não `RuntimeError`

É a armadilha mais cara do capítulo: `handle RuntimeError` **não** pega
um `trigger`, e o sintoma é "o tratamento não funcionou" sem nenhuma
pista.

## E `handle` sem tipo pega tudo

Inclusive o que você não queria. Ele serve para o topo do programa, e
não para o meio.
