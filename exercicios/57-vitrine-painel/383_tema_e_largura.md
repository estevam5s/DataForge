# 383 — o layout diz ao gráfico a largura

O desenho é feito num sistema de 800 unidades e o CSS o encolhe para
caber. Num painel de um terço da tela o fator é 0,45, e um rótulo de
11px chega ao olho com **cinco** — ilegível, sem nada que denuncie,
porque de longe o gráfico continua bonito.

## A largura é gravada na MONTAGEM

No desenho o contexto já acabou. `Contexto.larguras` é uma pilha que
cada área empurra.

## E o teto de 2,6× existe por um motivo

Compensar por inteiro num container muito estreito faria o rótulo
ocupar metade do gráfico.

## A primária do tema claro NÃO é o amarelo da marca

Amarelo sobre branco dá contraste 1,3:1 onde a WCAG pede 4,5:1.
Acessibilidade é como os componentes são desenhados, e não uma camada
por cima.
