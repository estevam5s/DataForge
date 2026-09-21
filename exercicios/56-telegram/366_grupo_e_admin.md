# 366 — o mesmo bot, em privado e em grupo

Num grupo o bot vê só os comandos, a menos que o modo de privacidade
esteja desligado — e isso se configura no @BotFather, e **não** no
código.

## O sintoma de esquecer

O bot "não responde" a nada que não comece com barra.

## O que o @BotFather decide

Entrar em grupos, ler todas as mensagens e a lista de comandos do
menu — três coisas que o código não pode mudar.

## E um comando com `@` é para o bot certo

Num grupo com dois bots, `/start` é ambíguo: o Telegram entrega
`/start@meubot`, e o módulo tira o sufixo antes de casar.
