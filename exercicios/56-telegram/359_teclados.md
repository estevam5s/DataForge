# 359 — botões, e o relógio que não para

Um botão inline manda um `dados` de volta, e o Telegram mostra um
relógio girando até alguém responder à consulta.

## Esquecer de responder deixa o relógio girando

Para sempre — e o usuário acha que travou. `ctx.avisar` é o que o
para.

## O `dados` tem limite de 64 bytes

E é por isso que se manda um **id**: o objeto fica no estado.

## E o teclado do celular é outro

`Tg.botoes` monta o inline (aparece **na** mensagem); `Tg.teclado`
substitui o teclado de digitar, e volta como **texto** — casado por
`@app.texto`, e não por `@app.botao`.
