# 353 — `root` com três níveis

`root` é o pai de **quem declarou o método**, e não o pai da classe da
instância. Com dois níveis a conta dá certo dos dois jeitos — e por isso
o defeito sobreviveu: toda herança de um repositório pequeno tem dois
níveis.

## Com três, era laço infinito

Dentro de `B.cadeia`, o `self` ainda é um `C`: `root` voltava a ser
`B`, e `B.cadeia` chamava a si mesmo.

## O diamante resolve por C3

Como o `super()` do Python — e a ordem é a mesma.

## E o método chamado é o do OBJETO

Uma ação que recebe "qualquer coisa que desenha" funciona com os dois
tipos, sem saber de nenhum.
