# 374 — a área de layout é um OBJETO

A linguagem não tem `with`, e inventar uma palavra reservada para o
layout de um módulo seria caro demais.

## Ele aninha sem indentação

`colunas[0].metrica(…)` lê melhor que um bloco de contexto, e não
consome um nível a cada camada.

## E pode ser PASSADO ADIANTE

Uma ação que recebe uma área desenha nela. Um bloco de contexto não
atravessa a chamada.

## `arvore()` devolve os nós de TOPO

Os filhos moram dentro deles — a contagem de topo não é a contagem de
componentes.
