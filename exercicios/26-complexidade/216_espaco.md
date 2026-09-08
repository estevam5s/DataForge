# Exercício 216 — Complexidade de espaço

## Enunciado

Processe mais dados do que cabem na memória.

## Conceitos

Tempo não é o único recurso. Um algoritmo O(n log n) que aloca uma cópia pode
perder para um O(n²) que trabalha no lugar, quando a memória é o gargalo.

```dataforge
stream action pares(xs):
    cycle x in xs:
        given x % 2 is 0:
            emit x

out pares(range(1000000)).take(3)     // O(1) de espaço
```

O `range` de um milhão nunca existe inteiro na memória — só os três primeiros
pares são calculados.

## O que observar

**A pilha também é memória.** Cada chamada recursiva ocupa um quadro. Uma
recursão de profundidade n custa O(n) de espaço mesmo sem alocar nada — e
estoura por volta de mil níveis.

**Preguiça é uma estratégia de memória.** `stream action` + `take(n)` processa
mais dados do que cabem na RAM. A compreensão é mais legível e materializa tudo:
use a segunda até ela não caber, e então troque.

**Só a memória adicional conta.** A entrada não entra na conta — ela já existia.

## Armadilhas

- Um generator infinito materializado (`to_cluster()`) trava. Use `take(n)`.
- Trocar tempo por memória quase sempre vale — exceto quando a memória é o
  gargalo. Num contêiner com limite apertado, estourar derruba o processo,
  enquanto ser lento só irrita.

## Relacionados

- [214 — Memoização](214_memoizacao.md)
- [Complexidade de espaço](https://dataforge-lang.vercel.app/docs/big-o/espaco)
