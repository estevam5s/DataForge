# 346 — ordenar objetos

`__lt__` é o único que `sorted` precisa. Os outros três existem para o
código **ler** melhor.

## Por que a comparação não pode ser por texto

`"1.10.0"` vem antes de `"1.2.0"` em ordem alfabética. Ordenar versão
por texto é o defeito mais comum de um gerenciador de pacotes caseiro.

## E um objeto sem `__lt__` não ordena

A saída sem declarar mágico nenhum é ordenar por uma **chave** — e é
a que serve quando o critério muda de lugar para lugar.
