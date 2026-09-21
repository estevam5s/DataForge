# 365 — foto, documento e o que chega junto

O Telegram não manda o arquivo no update — ele manda um `file_id`.

## A legenda vem em `ctx.texto`

Numa mensagem de mídia não há `text`: o que existe é `caption`. Quem
escreve o bot não deveria precisar saber disso.

## Mandar de volta usa o `file_id`

Baixar o arquivo só para reenviá-lo gasta banda duas vezes por nada.
E o `file_id` é válido **por bot**: o de outro bot não serve.

## E salvar um upload recusa o que não deve

Nome com `/` ou `..`, tamanho acima do limite e extensão fora da
lista. O nome final leva prefixo aleatório, porque dois usuários mandam
`foto.jpg` no mesmo minuto.
