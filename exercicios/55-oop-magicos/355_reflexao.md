# 355 — perguntar ao objeto o que ele tem

Reflexão é o que faz uma biblioteca funcionar com um tipo que ela
nunca viu.

## Ela respeita a VISIBILIDADE

Uma reflexão que lê campo privado transforma `private` em
comentário.

## `campos` devolve a DESCRIÇÃO de cada um

Nome, tipo, visibilidade, somente-leitura e anotações. Um cluster de
nomes bastaria para imprimir, e não para decidir o que serializar.

## E é isso que faz um serializador genérico funcionar

Sem saber que tipo é — só perguntando.
