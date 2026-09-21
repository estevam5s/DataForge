# 341 — afirmar que algo FALHA

Um teste que só confere o caminho feliz não prova nada sobre o
tratamento. E afirmar a falha **errada** é pior que não afirmar.

## `to_raise` sozinho aprova um teste que deveria falhar

Uma ação com erro de digitação levanta mesmo — de `NameError`. O
teste passa, e a regra que ele deveria cobrir nunca foi exercitada.

## Conferir o tipo é o que separa os dois

E o motivo errado costuma ser um erro de digitação no próprio
teste.

## E um caso de borda por vez

A tabela de casos diz o esperado ao lado do entrado, e a mensagem do
`assert` diz qual linha falhou.
