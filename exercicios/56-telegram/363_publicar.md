# 363 — long polling, webhook e o `doctor`

Um bot que roda na sua máquina usa long polling; um que roda num
servidor usa webhook. Os dois **não podem estar ligados ao mesmo
tempo**.

## O token vem do ambiente

Ele vai para o Git, e do Git para qualquer um — e o @BotFather não
avisa quando alguém o usa: o bot só começa a mandar spam.

## O `doctor` pergunta o que costuma faltar

Inclusive as duas que o código não decide: se o bot entra em grupos e
se ele lê todas as mensagens.

## E `deploy` não existe, de propósito

Um `deploy` que falasse com o servidor por dentro esconderia o que a
máquina é — e no dia em que alguém precisa mudar uma linha, não haveria
onde mexer.
