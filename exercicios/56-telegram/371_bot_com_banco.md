# 371 — o bot que guarda no banco

O estado do chat serve para o que é **da conversa** — o passo atual, o
carrinho. O que é do **negócio** vai para o banco.

## O pedido existe FORA da conversa

`ctx.estado` morre com o chat; a linha no banco é consultável por
quem não é o chat.

## O argumento do comando já vem separado

`ctx.args` — sem um `split` à mão que esquece o espaço duplo.

## E a rota do bot roda numa thread

Como no Kiln: o banco serializa o acesso; um vault solto compartilhado
entre tratadores **não** é protegido.
