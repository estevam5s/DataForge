# 326 — extrair uma tabela de um texto

O caso mais comum de regex num trabalho de dados: transformar texto
semiestruturado em linhas com colunas, e daí em diante deixar o quadro
trabalhar.

## Os números em pt-BR viram números

`1.250,00` — o ponto é milhar e a vírgula é decimal. Passar isso por
um `float()` direto dá `1.25`, e o extrato fecha errado por mil.

## E daí em diante é um quadro

`Q.de_vaults` e os verbos: `onde`, `agrupar`, `resumir`.

## A linha que não casou continua visível

Um parser que descarta em silêncio esconde o dia em que o formato
mudou.
