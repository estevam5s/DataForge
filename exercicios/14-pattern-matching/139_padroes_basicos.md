# Exercicio 139 — Padrões básicos

## Enunciado

Compare por literal, capture valores com um nome e use o curinga.

## Conceitos

`match` avalia uma expressão e testa cada `point` **de cima para baixo**. O
primeiro que casa executa, e os demais são ignorados.

### Padrão literal

```dataforge
point 0:
point "sim":
point void:
```

Casa por igualdade exata.

### Alternativas com `or`

```dataforge
point 1 or 2 or 3:
    yield "pequeno"
```

Um só ramo para vários valores.

### Captura

Um nome **em minúscula** casa com qualquer coisa e liga o valor:

```dataforge
point n:
    yield $"outro: {n}"
```

### Curinga

`_` casa com qualquer coisa e **não** liga nome — use quando o valor não
interessa:

```dataforge
point _:
    yield yes
```

## A convenção maiúscula/minúscula

Esta é a regra que organiza tudo:

| Escrita | Significa |
|---------|-----------|
| `point n` | **captura** — casa com tudo, liga a `n` |
| `point Integer` | **tipo** — casa se for um Integer |
| `point Status.Ativo` | **valor** — casa por igualdade |
| `point _` | **curinga** |

Minúscula captura, maiúscula testa o tipo. Sem essa convenção, `point Integer`
seria ambíguo: comparar com uma variável chamada `Integer` ou testar o tipo?

## A ordem é tudo

```dataforge
match n:
    point x:              // captura tudo
        yield "pegou tudo"
    point 5:              // inalcançável
        yield "nunca chega aqui"
```

Uma captura no topo engole todos os casos abaixo. Coloque sempre **do mais
específico para o mais geral** — literais primeiro, tipos depois, captura ou
`default` por último.

## Saída esperada

```
zero
pequeno
afirmativo
vazio
outro: 99
cuidado: uma captura no topo torna os demais inalcancaveis
```

## Experimente

- Inverta os dois `point` de `ordem` e veja o resultado mudar.
- Troque `point n` final por `default:` — qual a diferença prática?
