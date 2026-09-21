# 362 — o que roda antes, o que roda depois, e quando cai

Um bot sem tratador de erro morre calado no primeiro dado inesperado —
e quem está do outro lado vê a mensagem sumir no vazio.

## O erro NÃO derruba o bot

O tratador responde, e o próximo update é atendido normalmente.

## Sem ele, a mensagem some no vazio

A sonda registra a falha, e o usuário não recebeu nada.

## E o middleware é onde mora o que é de TODOS

Autenticação, limite de taxa e registro — sem repetir em cada
tratador.
