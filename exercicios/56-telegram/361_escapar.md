# 361 — o caractere que derruba a mensagem inteira

MarkdownV2 tem **dezoito** caracteres reservados. Um ponto solto num
preço faz o Telegram **recusar** a mensagem inteira — não é que o
negrito sai errado: a mensagem não chega.

## O que engana é o ponto

Quase todo texto de sistema tem um: preço, versão, hora, fim de
frase.

## E o `$` NÃO está entre eles

Ele parece perigoso e não é — escapar demais também estraga o texto,
com barras aparecendo na tela.

## O cuidado ao juntar os dois

O texto do usuário é escapado; a **marcação**, não. Escapar tudo
transformaria o asterisco do negrito em asterisco literal.
