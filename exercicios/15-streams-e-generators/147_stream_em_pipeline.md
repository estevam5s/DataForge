# Exercicio 147 — Streams com pipelines

## Enunciado

Combine generators com `sift`, `morph`, `distill` e compreensões.

## Conceitos

Streams e pipelines resolvem o mesmo problema por caminhos diferentes:

| | Streams | Pipelines |
|---|---------|-----------|
| Avaliação | preguiçosa, item a item | ansiosa, lista inteira |
| Fonte infinita | sim | não |
| Sintaxe | `stream action` + `emit` | `>> sift` / `>> morph` |

Os pipelines operam sobre listas. Para usá-los com um stream, materialize antes:

```dataforge
primeiros := naturais().take(20)
out primeiros >> sift n: n % 3 is 0
```

## Métodos diretos no stream

Para filtrar e transformar sem escrever a materialização:

```dataforge
ate(10).filter(lambda n: n % 2 is 0)
ate(5).map(lambda n: n * n)
```

Ambos devolvem uma **lista** — consomem o stream inteiro. Num stream infinito,
use `take` primeiro.

## Compreensões consomem streams

```dataforge
[c.upper() cycle c in letras() given c isnt "a"]
```

O `cycle in` de uma compreensão aceita um stream como fonte, igual ao `cycle` de
laço.

## Encadear generators

Aqui está o padrão que dá poder à ideia: um generator que consome outro.

```dataforge
stream action dobrar(fonte):
    cycle v in fonte:
        emit v * 2

cadeia := dobrar(so_pares(naturais()))
out cadeia.take(5)          // [4, 8, 12, 16, 20]
```

`naturais()` é infinito. `so_pares` filtra, `dobrar` transforma — e **nada roda**
até o `take(5)`. Cada item atravessa a cadeia inteira sob demanda; a memória usada
não depende do tamanho da fonte.

É o mesmo desenho dos pipes do Unix: `yes | grep ... | sed ...` não trava porque
cada estágio consome o anterior aos poucos.

## Quando escolher cada um

- **Pipeline** para dados que já estão na memória e cabem nela.
- **Stream** para fonte infinita, arquivo grande, ou quando você só precisa dos
  primeiros resultados.

## Saída esperada

```
[3, 6, 9, 12, 15, 18]
DTFORGE
[2, 4, 6, 8, 10]
[1, 4, 9, 16, 25]
[2, 4, 6, 8, 10]
[4, 8, 12, 16, 20]
soma de 1 a 100: 5050
```

## Experimente

- Acrescente um terceiro estágio à cadeia e confirme que continua preguiçoso.
- Meça com `Arcane.Time.stopwatch` a diferença entre filtrar 1 milhão de itens
  materializados e pegar os 5 primeiros de um stream.
