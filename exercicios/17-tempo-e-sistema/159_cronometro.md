# Exercicio 159 — Cronometragem e desempenho

## Enunciado

Meça quanto tempo o código leva, e compare implementações com números em vez de
palpite.

## `measure` — a forma direta

```dataforge
medida := Time.measure(trabalho_pesado)
out medida.result      // o que a ação devolveu
out medida.ms          // quanto levou, em milissegundos
```

Recebe uma ação sem argumentos e devolve resultado **e** tempo. Para medir algo
com argumentos, envolva numa lambda:

```dataforge
Time.measure(lambda: com_laco(100000))
```

## `stopwatch` — controle manual

Quando você precisa de tempos parciais:

```dataforge
crono := Time.stopwatch()
crono.start()
// ... primeira parte
parcial := crono.elapsed_ms()
// ... segunda parte
crono.stop()
total := crono.elapsed_ms()
```

| Método | Faz |
|--------|-----|
| `start()` | começa ou retoma |
| `stop()` | pausa e devolve o acumulado |
| `elapsed()` | segundos até agora |
| `elapsed_ms()` | milissegundos |
| `reset()` | zera |

`start` depois de `stop` **retoma** — o acumulado não se perde. Isso permite medir
só as partes que interessam, ignorando o meio.

## Medir para decidir

```dataforge
action com_laco(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

action com_formula(n):
    yield n * (n + 1) ~/ 2
```

As duas dão o mesmo resultado. A segunda é O(1) contra O(n) da primeira, e o
cronômetro mostra isso em números.

Essa é a disciplina que vale levar: **meça antes de otimizar**. A intuição sobre
o que é lento erra com frequência, e otimizar o lugar errado gasta tempo sem
efeito.

## Medir várias vezes

```dataforge
tempos := []
cycle _ in [1, 2, 3, 4, 5]:
    tempos.append(Time.measure(lambda: com_laco(20000)).ms)

out $"media {mean(tempos)}, minimo {min(tempos)}"
```

Uma medição isolada é ruído: o sistema operacional interrompe, o cache esquenta.
O **mínimo** costuma ser mais informativo que a média — é a execução em que menos
coisa atrapalhou.

Repare no `cycle _ in ...`: o `_` diz que o valor da iteração não interessa.

## Saída esperada

```
resultado: 20000100000
levou: 42.31 ms

parcial: 11.2 ms
total:   19.8 ms

laco:    21.4 ms -> 5000050000
formula: 0.002 ms -> 5000050000

5 execucoes: media 4.3 ms, minimo 4.1 ms

cronometro zerado
```

(os tempos variam a cada máquina)

## Experimente

- Compare busca linear com `Arcane.Collections.binary_search` numa lista grande.
- Meça um pipeline contra o laço equivalente.
- Use `stopwatch` para medir só a parte de I/O de um programa.
