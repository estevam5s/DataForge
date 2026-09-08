# Exercício 214 — Trocar tempo exponencial por memória linear

## Enunciado

Faça `fib(35)` responder, sem esperar.

## Conceitos

Fibonacci ingênuo é O(2ⁿ): cada chamada gera duas, e quase todas recalculam o
que já foi calculado. `fib(40)` faz mais de um bilhão de chamadas.

Guardar o resultado derruba para O(n):

```dataforge
cache := {}

action fib(n):
    given n smaller 2:
        yield n
    chave := str(n)
    given cache.has(chave):
        yield cache[chave]
    resultado := fib(n - 1) + fib(n - 2)
    cache[chave] := resultado
    yield resultado
```

## O que observar

**A conta que decide a troca:**

| | tempo | memória |
|---|---|---|
| `fib(50)` ingênuo | ~10¹⁵ chamadas (semanas) | O(n) de pilha |
| `fib(50)` memoizado | ~50 chamadas (µs) | 50 valores |

**O snippet `memo`** no VS Code escreve esse padrão.

**O analisador reconhece os dois.** Ele distingue divisão e conquista
(O(n log n)) de recursão exponencial (O(2ⁿ)) olhando o argumento da chamada
recursiva — metade contra n−1.

## Armadilhas

- O cache cresce sem limite. Para entrada ilimitada, use um cache com teto (LRU)
  — ou o programa troca tempo por vazamento de memória.
- A chave precisa ser única. `str(n)` serve para um argumento; com dois, junte
  os dois.

## Relacionados

- [213 — Medir o crescimento](213_medir_o_crescimento.md)
- [216 — Complexidade de espaço](216_espaco.md)
