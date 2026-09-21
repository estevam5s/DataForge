# 367 — o bot que responde sem estar no chat

A consulta inline é o que faz `@meubot pizza` funcionar em **qualquer**
conversa, sem o bot ser membro dela.

## Cada item precisa de um id ÚNICO

Ids repetidos fazem o Telegram descartar a lista inteira, sem mensagem
de erro — o usuário vê "sem resultados".

## `ctx.responder_consulta` preenche o id sozinho

Era a única resposta que caía no bot cru: todas as outras são
`ctx.responder*`, e esta obrigava a escrever
`ctx.bot.responder_inline(ctx.consulta["id"], …)` — com o id à mão, que
é exatamente o que se esquece.

## E ela não tem `ctx.chat`

Porque não há chat: o bot não está lá.
