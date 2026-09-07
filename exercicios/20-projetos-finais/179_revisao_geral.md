# Exercicio 179 — Revisão: todos os conceitos

## Enunciado

Um único programa que exercita cada recurso da linguagem — use como referência
rápida e como teste de que você domina o conjunto.

## O roteiro

| # | Tema | Recursos |
|---|------|----------|
| 1 | Tipos | anotações, `steady`, `typeof` |
| 2 | Operadores | `~/`, `**`, encadeamento, `in`, `??` |
| 3 | Fluxo | ternário, `cycle`, `skip` |
| 4 | Coleções | compreensões, fatiamento |
| 5 | Desestruturação | `...resto`, spread |
| 6 | Ações | alta ordem, lambda, padrões |
| 7 | Records/enums | métodos, `with` |
| 8 | Blueprints | herança, polimorfismo |
| 9 | Pattern matching | tipo, sequência, record, vault, guarda |
| 10 | Erros | `guard`, `defer`, `monitor`, `ensure` |
| 11 | Pipelines | `sift`, `morph`, `distill` |
| 12 | Generators | `stream action`, `emit`, infinito |
| 13 | Stdlib | `Arcane.Collections` |
| 14 | Concorrência | `thread`, `channel` |

## Combinações que valem notar

### Ternário com enum

```dataforge
q := Quadrante.Primeiro given p.x bigger 0 and p.y bigger 0 otherwise Quadrante.Outro
```

### Fatiamento encadeado

```dataforge
nums[::-1][0:3]        // inverte, depois pega os três primeiros
```

### `guard` + `defer` juntos

```dataforge
action arriscado(n):
    guard n isnt 0, "divisor nao pode ser zero"
    defer:
        out "(defer limpou)"
    yield 100 / n
```

O `guard` vem **antes** do `defer` de propósito: se a pré-condição falhar, não há
recurso adquirido para limpar.

### Pipeline multilinha

```dataforge
total := nums
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0
```

Uma linha que começa com `>>` continua a expressão anterior.

### Generator infinito consumido parcialmente

```dataforge
stream action fib():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

fib().take(8)
```

O `persist yes` não trava porque `take(8)` para de pedir. E o `a, b := b, a + b`
faz a troca simultânea sem temporária.

## Autoavaliação

Se você consegue **explicar cada bloco** deste arquivo, cobriu a linguagem. Os
pontos onde titubear indicam qual módulo revisar:

| Titubeou em | Volte para |
|-------------|------------|
| tipos, `typeof` | módulo 11 |
| records, enums | módulo 12 |
| desestruturação, spread | módulo 13 |
| `match` com padrões | módulo 14 |
| `stream action` | módulo 15 |
| `adopt`, `relay` | módulo 16 |

## Experimente

- Comente um bloco e preveja o que quebra nos `assert`.
- Reescreva o pipeline como compreensão, e vice-versa.
- Acrescente um bloco 15 usando um recurso que faltou.
