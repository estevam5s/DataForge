# 275 — a invariante quebrada é um bug DELA

Uma condição que estoura ao ser avaliada não quer dizer que o estado é
inválido. Dizer "violou" ali mandaria a pessoa procurar no agregado, e o
defeito está na condição.

## As duas mensagens orientam lugares diferentes

`estourou` manda olhar a condição; `violou` manda olhar o comando. São
correções em arquivos diferentes, e uma mensagem que junta as duas custa
a tarde de quem lê.

## E o estado volta nos dois casos

O comando é desfeito por inteiro, tenha ele falhado pela condição ou
por um erro dentro dela.
