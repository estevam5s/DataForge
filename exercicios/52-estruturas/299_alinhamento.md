# 299 — o enchimento que o C insere

Um `u32` começa num múltiplo de 4; um `u64`, num múltiplo de 8.
Ignorar isso é o que faz o mesmo `.struct` sair com 12 bytes de um lado
e 16 do outro — e o arquivo ser lido errado do byte 1 em diante, sem
nenhum erro.

## Alinhado × empacotado

`empacotado := yes` recusa o enchimento e cobra os deslocamentos.
`enchimento()` diz quantos bytes são só alinhamento.

## O REGISTRO INTEIRO também é alinhado

Ao maior campo. Sem isso, um cluster deles sai torto a partir do
segundo — e o segundo registro é lido metade num, metade no outro.

## E a lista de tipos é a mesma do `Arcane.Bytes`

Duas listas divergiriam, e o mesmo `u32` teria dois tamanhos.
