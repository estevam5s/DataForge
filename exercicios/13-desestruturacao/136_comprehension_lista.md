# Exercicio 136 — Compreensão de listas

## Enunciado

Construa listas transformando e filtrando numa única expressão.

## Conceitos

A forma geral:

```
[ <expressão>  cycle <nome> in <fonte>  [given <condição>] ]
```

Lê-se: *"a expressão, para cada nome na fonte, dado que a condição vale"*.

```dataforge
quadrados := [n * n cycle n in nums]
pares     := [n cycle n in nums given n % 2 is 0]
```

Repare que a compreensão **reutiliza palavras que você já conhece** — `cycle` e
`given` são as mesmas dos laços e condicionais. Não há sintaxe nova para
memorizar.

## Comparando com o laço equivalente

```dataforge
// laço
quadrados := []
cycle n in nums:
    quadrados.append(n * n)

// compreensão
quadrados := [n * n cycle n in nums]
```

A compreensão diz **o que** você quer; o laço diz **como** obter. Para
transformações simples, a primeira é mais direta. Para lógica com vários passos,
o laço continua sendo a escolha certa — não force tudo numa linha.

## Compreensão ou pipeline?

DataForge tem as duas:

```dataforge
[n * 2 cycle n in nums given n % 2 is 1]
nums >> sift n: n % 2 is 1 >> morph n: n * 2
```

Quando escolher cada uma:

| Situação | Prefira |
|----------|---------|
| um filtro e uma transformação | compreensão |
| vários estágios encadeados | pipeline |
| duas fontes combinadas | compreensão |
| terminar com uma redução | pipeline (`distill`) |

## Múltiplas fontes

```dataforge
[$"{a}x{b}" cycle a in [2, 3] cycle b in [1, 2, 3]]
```

O `cycle` da direita gira mais rápido — é o laço interno. O resultado tem
`2 × 3 = 6` itens.

## Escopo

A variável do `cycle` **não vaza**:

```dataforge
_ := [i cycle i in [1, 2]]
out i        // erro: Undefined name 'i'
```

Isso evita o bug clássico de reaproveitar sem querer o `i` de uma compreensão
anterior.

## Saída esperada

```
[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
[2, 4, 6, 8, 10]
[2, 6, 10, 14, 18]
DTFORGE
[2x1=2, 2x2=4, 2x3=6, 3x1=3, 3x2=6, 3x3=9]
[Ana, Carla]
```

## Experimente

- Reescreva `dobro_dos_impares` como pipeline e compare.
- Gere os pares `[a, b]` com `a smaller b` a partir de `[1,2,3]`.
