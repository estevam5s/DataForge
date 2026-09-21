# 291 — a falha ENCERRA o fluxo

Num fluxo, um erro não pode derrubar o programa — quem escuta está num
retorno de chamada, longe de qualquer `monitor`.

## Falhar avisa E encerra

Um fluxo que continuasse depois de falhar deixaria quem escuta sem
saber se o próximo valor veio de uma fonte que ainda funciona. O aviso
de fim sai junto.

## `ao_falhar` transforma o erro em VALOR

E não desfaz o encerramento: ele traduz a falha, e o fluxo continua
fechado.

## E um SINAL não tem erro

Ele tem um valor agora; *"o saldo falhou"* não é um estado de saldo.
Quem precisa disso guarda um `Arcane.Resultado` dentro do sinal.
