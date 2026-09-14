# Exercicio 238 — Vários núcleos, de verdade

## Enunciado

Meça a diferença entre thread e processo em trabalho de CPU, e prove qual dos
dois usa a máquina inteira.

## A pergunta que decide tudo

O trabalho **espera** ou **calcula**?

| O trabalho | Use | Por quê |
|---|---|---|
| espera (rede, disco, banco, `sleep`) | `P.map` — threads | a thread solta o GIL enquanto espera, e dez downloads acontecem juntos |
| calcula (números, imagem, parsing) | `P.map_processos` — processos | duas threads do Python nunca executam bytecode ao mesmo tempo |

O GIL — *Global Interpreter Lock* — é a razão. Ele é do CPython, não do
DataForge: `async`, `thread` e `parallel` são threads do Python, e por isso
nenhum dos três usa mais de um núcleo para contas.

## O que este exercício mede

Quatro blocos de 150 mil multiplicações, pelos três caminhos:

```dataforge
serie := cronometrar(lambda => [cpu(b) cycle b in BLOCOS])
threads := cronometrar(lambda => P.map(cpu, BLOCOS))
processos := cronometrar(lambda => P.map_processos(cpu, BLOCOS))
```

Numa máquina de 10 núcleos:

| Como | Tempo | Ganho |
|---|---|---|
| em série | 598 ms | — |
| `P.map` — threads | 610 ms | **0,97x** |
| `P.map_processos` — processos | 302 ms | **1,98x** |

As threads não só deixaram de ganhar: ficaram um pouco **mais lentas** que a
série. É o custo de trocar de contexto sem nada a ganhar em troca — e é o
resultado esperado, não um defeito.

## Por que a comparação é com a série, e não com um número

```dataforge
assert ganho_processos bigger 1.2      // certo
assert processos["ms"] < 200           // errado
```

Um limite absoluto mede a **máquina**, e não o paralelismo: num runner de CI
ocupado, quatro processos perfeitamente paralelos levam mais de 200 ms. A
razão contra a série medida na mesma máquina, no mesmo instante, é o que
significa alguma coisa.

E a razão é cobrada **com fator** (`bigger 1.2`), não com `bigger 1`: o segundo
passa por acidente metade das vezes.

## O que o exercício não afirma

O `assert` só roda quando há **quatro núcleos ou mais**:

```dataforge
given P.nucleos() >= 4:
    assert ganho_processos bigger 1.2, …
```

Numa máquina de um núcleo, `map_processos` é mais lento que a série — e está
certo. Cobrar ganho ali seria cobrar o impossível.

## Onde isso continua

- [`239_o_que_atravessa.df`](239_o_que_atravessa.df) — o que viaja junto com a
  ação, e o que fica para trás
- [`240_pipeline_em_blocos.df`](240_pipeline_em_blocos.df) — dividir, calcular
  em paralelo, juntar, e conferir contra a resposta fechada
