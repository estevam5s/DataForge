# 315 — a troca que CALCULA

`sub` só troca por texto. Mascarar um CPF, dobrar um número ou virar a
caixa de uma palavra exigia sair do módulo — e quem sai escreve um laço
que se esquece de um caso.

## A ação recebe o mesmo vault de `search`

Com `value`, `groups`, `named` e `span`. Passar o objeto de casamento
do Python obrigaria a escrever `m.group(1)`, que é vocabulário de outra
linguagem.

## Devolver `void` NÃO troca

É o que deixa a ação escolher o que **não** mexer, sem reconstruir o
texto.

## E `replace_map` deixa o que não está na tabela

Uma tabela sem padrão transformaria o desconhecido em vazio, e o texto
sairia com buracos.
