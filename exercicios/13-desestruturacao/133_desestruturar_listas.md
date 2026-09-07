# Exercicio 133 — Desestruturação de listas

## Enunciado

Extraia vários valores de uma lista numa única atribuição.

## Conceitos

```dataforge
a, b := [1, 2]
```

Uma atribuição, dois nomes. O lado direito é percorrido e cada elemento vai para
o nome correspondente.

## A troca sem temporária

```dataforge
p, q := q, p
```

O lado direito é avaliado **inteiro antes** de qualquer atribuição acontecer. Por
isso não há variável temporária nem risco de sobrescrever `p` antes de ler.

Comparando: em C você escreveria três linhas com um `tmp`. Aqui é uma.

## Quantidade errada falha

```dataforge
m, n := [1, 2, 3]
// erro: Cannot unpack 3 value(s) into 2 name(s)
```

Isso é deliberado. Um `[1, 2, 3]` chegando onde se esperavam dois valores quase
sempre significa que a suposição sobre os dados estava errada — e falhar alto é
melhor que descartar o `3` em silêncio.

Quando a sobra é esperada, existe `...resto` (próximo exercício).

## Retornando vários valores

DataForge não tem tuplas separadas de listas. Devolver vários valores é devolver
uma lista, e quem chama desestrutura:

```dataforge
action divide_com_resto(a, b):
    yield [a ~/ b, a % b]

quociente, resto := divide_com_resto(17, 5)
```

Isso lê melhor que `resultado[0]` e `resultado[1]` espalhados pelo código.

## Saída esperada

```
1 2
segundo primeiro
Cannot unpack 3 value(s) into 2 name(s)
1 = um
2 = dois
3 = tres
17 / 5 = 3 resto 2
```

## Experimente

- Desestruture direto no cabeçalho: `cycle` ainda não aceita, mas `numero,
  palavra := par` na primeira linha resolve.
- Escreva `action min_max(lista)` devolvendo os dois extremos.
