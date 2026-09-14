# Exercicio 240 — Um pipeline que usa a máquina inteira

## Enunciado

Divida um trabalho grande, calcule os pedaços em paralelo, junte — e prove que
o resultado bate com a resposta fechada.

## O desenho

```
dividir  ->  map_processos  ->  juntar
```

Cada bloco tem de ser **autossuficiente**: ele atravessa para outro processo,
faz a conta lá, e volta.

## A decisão que mais importa: o que volta

```dataforge
action resumir(bloco):
    soma := 0
    primos := 0
    cycle n from bloco["de"] to bloco["ate"]:
        …
    yield {"soma": soma, "primos": primos}
```

O bloco vira um **resumo**, e não uma lista. Mandar dez mil números e receber
dois de volta é barato; mandar dez mil e receber dez mil paga a travessia duas
vezes, e aí os processos perdem para a série.

É a mesma conta do `map_processos` em geral: ele vale a partir de **alguns
milissegundos de trabalho por item**.

## A conferência

Um pipeline paralelo que não é conferido contra uma resposta fechada é um
gerador de números plausíveis. Aqui há duas âncoras:

```dataforge
esperado := TOTAL * (TOTAL + 1) ~/ 2
assert soma is esperado
assert primos is 6057        // π(60000), que é uma constante conhecida
```

A primeira é uma fórmula; a segunda, um valor tabelado. Nenhuma das duas vem do
próprio programa — que é o ponto.

## A ordem

```dataforge
assert resumos[0]["soma"] < resumos[BLOCOS - 1]["soma"]
```

`map_processos` devolve **na ordem da entrada**, e não na ordem em que os
processos terminaram. Sem essa garantia, quem chama teria de reassociar bloco e
resumo — e é aí que se erra.

## Medido

Seis blocos de dez mil, numa máquina de 10 núcleos: **426% de CPU**. O programa
usou quatro núcleos e um pouco, que é o que seis blocos permitem quando cada um
custa o mesmo.

## Onde isso continua

- [`238_varios_nucleos.df`](238_varios_nucleos.df) — a medida do ganho
- [`239_o_que_atravessa.df`](239_o_que_atravessa.df) — o que viaja e o que fica
