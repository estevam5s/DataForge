# 288 — a fonte fria liga preguiçoso

`de_cluster` só começa quando alguém escuta. Se o operador se ligasse
à fonte na **construção**, os valores sairiam antes de o assinante final
existir — e o resultado seria uma lista vazia, sem erro nenhum.

## A cadeia inteira chega

Porque cada operador só se conecta à sua fonte ao receber o primeiro
inscrito.

## Sem ninguém escutando, nada corre

A prova é um efeito colateral dentro do `morph`: ele não aconteceu.

## E os recortes

`primeiros`, `pular`, `blocos` e `distill` — o `blocos` não emite o
resto incompleto, porque um bloco pela metade não é um bloco.
