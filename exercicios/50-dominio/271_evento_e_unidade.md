# 271 — o fato espera a confirmação

Publicar um evento na hora faz o mundo reagir a um fato que a
transação ainda pode desfazer: o e-mail sai, e o pedido não existe.

## O evento não muda

Ele já aconteceu. Mudá-lo é reescrever a história — quem já reagiu a
ele reagiu ao que estava escrito antes. E o nome no passado não é
estilo: um evento chamado `CriarPedido` é um comando disfarçado, e quem
o recebe acha que pode recusá-lo.

## Ele fica guardado até a confirmação

O agregado anota; a unidade publica. Entre os dois há a janela em que
a transação pode ser desfeita.

## A unidade desfeita não publica nada

E descarta os eventos junto: eles nunca aconteceram.

## E não dá para desfazer o confirmado

Os eventos já saíram, e quem reagiu não tem como voltar atrás. A saída
é a **compensação** — a mesma que a `Saga` do `Arcane.Malha` implementa
quando a transação atravessa a rede.
