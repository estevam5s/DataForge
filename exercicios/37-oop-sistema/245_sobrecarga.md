# 245 — Sobrecarga que diz o que aceita

## O que se pratica

`overload action` no topo e em construtor, a escolha por aridade e por
tipo, e as recusas `OverloadResolutionError` e `AmbiguousOverloadError`.

## O que este exercício ensina que não é óbvio

**1. Numa linguagem dinâmica, sobrecarga é documentação que se cumpre.**
Um `given typeof(valor)` faria o mesmo — e aceitaria qualquer coisa,
falhando lá dentro. As variantes declaram as formas, e a chamada fora
delas é recusada **com a lista das que existem** na nota.

**2. O tipo exato vence o compatível.** Um `Integer` serve onde se pede
`Float`. Sem essa regra `formatar(3)` empataria entre as duas primeiras
variantes; com ela, vence a de `Integer`, que é a que quem escreveu quis.

**3. Empate é erro, e não sorteio.** `juntar(1, 2)` cabe nas duas
variantes com a mesma precisão. Escolher a primeira escrita faria mover
uma variante de lugar mudar o resultado de um programa que não a chama.
`juntar(1, "x")` não empata: só a primeira aceita texto em `b`.

**4. Toda variante é marcada.** Misturar `action f` com `overload action
f` é recusado — não há leitura em que as duas convivam.

## Para ir além

- Acrescente `overload action formatar(valor: Integer, casas: Integer)`
  e descubra qual chamada existente passa a empatar.
