# 335 — a falha como VALOR

Um erro interrompe; um resultado não. Quando a falha é **esperada** —
um CEP que não existe, um arquivo que pode faltar — levantar obriga quem
chama a montar um `monitor` em volta de cada chamada, e o código some
dentro do tratamento.

## A falha atravessa a cadeia sem um `given` sequer

`entao` só chama o próximo quando o anterior deu certo.

## E a hora de voltar para o mundo dos erros

Na fronteira do programa, `exigir()` transforma o resultado em erro —
porque ali não há mais quem trate. E `tentar` é a ponte no outro
sentido.

## `Talvez`, para onde `void` é ambíguo

`void` não distingue "não achei" de "achei, e o valor é `void`".

## Quando usar cada um

Falha **esperada**: `Resultado`. Falha **excepcional** (disco cheio,
bug): `trigger`.
