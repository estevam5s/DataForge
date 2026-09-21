# 329 — o que se lê de um erro capturado

Um erro não é só uma mensagem: ele carrega o tipo, a linha, a nota, a
dica e o código. É isso que faz a diferença entre um log que ajuda e um
que só diz que algo deu errado.

## Relançar preservando o original

Embrulhar é a norma; sem a causa, a mensagem de fora diz **o quê**
falhou e perde o **porquê**.

## `ensure` roda sempre

Nos dois caminhos, e depois do `handle`.

## E `monitor` SEM `handle` não engole

Ele só garante o `ensure`. O erro continua viajando.
