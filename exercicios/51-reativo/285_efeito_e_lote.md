# 285 — o efeito roda ao nascer, e o lote agrupa

Um efeito que não rodasse na criação deixaria a tela sem o estado
inicial — e quem escreve teria de chamá-lo à mão, o que se esquece
exatamente uma vez.

## Ele já rodou

E roda de novo a cada mudança de qualquer dependência.

## O lote agrupa várias escritas numa notificação

Sem ele, três escritas mostram dois estados intermediários que nunca
deveriam aparecer na tela. E ele **já existiu sem agrupar nada**:
montava uma lista de adiados que ninguém lia.

## Parar é definitivo

O derivado continua certo; o que parou foi o efeito. São coisas
diferentes, e confundi-las faz alguém "desligar" o cálculo achando que
desligou o desenho.

## E um efeito sem dependência roda uma vez só

Sem sinal lido, nada tem como acordá-lo.
