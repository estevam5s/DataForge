# 279 — regras que se combinam em árvore

`e`, `ou` e `nao` devolvem regras, e uma regra composta se combina de
novo. É o que permite montar a política em pedaços **nomeados**, em vez
de um `given` de cinco linhas.

## A árvore inteira tem descrição

`(grande E cheio) OU estreante E nacional` — e a descrição sai da
composição, e não de uma segunda string escrita à mão.

## O motivo segue o caminho que falhou

Num `ou`, nenhum dos dois basta, e a explicação diz isso. Num `e`, ela
aponta a parte.

## E a mesma árvore filtra a lista

Os que passam e os que não passam somam o total: é a prova de que a
negação é a complementar.
