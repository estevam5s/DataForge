# Exercicio 146 — Sequências infinitas

## Enunciado

Escreva um generator sem fim e consuma apenas o que precisa.

## Conceitos

Um `persist yes:` dentro de um `stream action` não trava o programa:

```dataforge
stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1

out naturais().take(6)     // [0, 1, 2, 3, 4, 5]
```

## Por que isso funciona

O corpo de um `stream action` **não roda na chamada**. `naturais()` devolve um
`Stream` sem executar nada. A execução acontece sob demanda: cada `emit` roda
quando alguém pede o próximo item, e **pausa** logo depois.

`take(6)` pede seis itens, recebe seis, e para de pedir. O laço infinito
simplesmente nunca chega à sétima volta.

É a mesma ideia de `itertools.count()` em Python ou de listas preguiçosas em
Haskell — a sequência é uma *receita*, não um dado.

## O que isso permite

Descrever a sequência pelo que ela **é**, não por quantos itens você vai querer:

```dataforge
stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b
```

Essa definição é completa e não menciona limite algum. Quem chama decide:
`take(10)`, `take(1000)`, ou um `cycle` com `halt` na condição que importar.

Repare no `a, b := b, a + b` — a desestruturação faz a troca simultânea que em
outras linguagens exigiria uma variável temporária.

## Parando por dentro

Quando o próprio generator sabe onde parar, use `halt`:

```dataforge
stream action ate_passar(limite):
    n := 1
    persist yes:
        given n bigger limite:
            halt
        emit n
        n *= 3
```

Agora `to_cluster()` é seguro: a sequência termina sozinha.

## Cuidado

`to_cluster()` num generator **realmente** infinito trava o programa — ele tenta
materializar itens para sempre. Use `take(n)` ou garanta um `halt`.

## Saída esperada

```
[0, 1, 2, 3, 4, 5]
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
[1, 2, 4, 8, 16, 32, 64, 128]
[a, b, c, a, b, c, a]
[1, 3, 9, 27, 81]
0 1 2
```

## Experimente

- Escreva um generator de números primos e pegue os 20 primeiros.
- Faça `repetir` aceitar um limite opcional de voltas.
