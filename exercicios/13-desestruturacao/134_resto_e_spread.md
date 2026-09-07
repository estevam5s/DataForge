# Exercicio 134 — Resto e spread

## Enunciado

Capture o que sobra numa desestruturação com `...resto` e expanda coleções com
`...` na construção e nas chamadas.

## Conceitos

`...` faz dois trabalhos opostos, distinguidos pelo lado em que aparece.

### À esquerda do `:=` — **coleta**

```dataforge
primeiro, ...outros := [1, 2, 3, 4, 5]
// primeiro = 1
// outros   = [2, 3, 4, 5]
```

O resto pode estar em qualquer posição, inclusive no meio:

```dataforge
inicio, ...meio, fim := [1, 2, 3, 4, 5]
// inicio = 1, meio = [2, 3, 4], fim = 5
```

Só é permitido **um** `...resto` por desestruturação — com dois, não haveria como
saber onde um termina e o outro começa.

### À direita — **expande**

```dataforge
juntos := [...a, ...b, 5]
final  := {...padrao, ...usuario}
soma   := somar_tres(...args)
```

## O padrão de configuração

Esta é a aplicação mais comum do spread em vaults:

```dataforge
padrao := {"tema": "claro", "fonte": 14}
usuario := {"tema": "escuro"}
final := {...padrao, ...usuario}       // {tema: escuro, fonte: 14}
```

**O último vence.** As preferências do usuário sobrescrevem o padrão; o que ele
não definiu vem do padrão. Uma linha resolve o que normalmente seriam cinco.

## Cópia rasa

```dataforge
copia := [...original]
```

Isso cria uma lista **nova**. Alterar `copia` não toca em `original`. É "rasa"
porque objetos *dentro* da lista continuam compartilhados — para uma cópia
profunda existe `deep_copy`.

## Comparando

| DataForge | JavaScript | Python |
|-----------|------------|--------|
| `a, ...r := lista` | `const [a, ...r] = lista` | `a, *r = lista` |
| `[...a, ...b]` | `[...a, ...b]` | `[*a, *b]` |
| `{...a, ...b}` | `{...a, ...b}` | `{**a, **b}` |
| `f(...args)` | `f(...args)` | `f(*args)` |

## Saída esperada

```
1 [2, 3, 4, 5]
1 [2, 3, 4] 5
[1, 2, 3, 4, 5]
{tema: escuro, fonte: 14}
60
[1, 2, 3] [1, 2, 3, 4]
```

## Experimente

- Escreva `a, ...m, ...n := [1,2,3]` e leia o erro.
- Use spread para inserir no meio: `[...antes, novo, ...depois]`.
