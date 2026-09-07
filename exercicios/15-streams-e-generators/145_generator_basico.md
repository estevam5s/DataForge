# Exercicio 145 — Generators com `stream action`

## Enunciado

Produza valores um a um com `emit`, em vez de montar a lista inteira de uma vez.

## Conceitos

Um `stream action` é uma ação que **produz uma sequência**:

```dataforge
stream action contar(ate):
    cycle i from 1 to ate:
        emit i
```

Duas palavras fazem a diferença:

| Palavra | Efeito |
|---------|--------|
| `stream action` | a chamada devolve um `Stream`, não um valor |
| `emit` | produz um item e **continua** de onde parou |

## `emit` e `yield` são coisas diferentes

Esta é a distinção central, e ela é deliberada:

```dataforge
action f():
    yield 1        // devolve 1 e ENCERRA a ação

stream action g():
    emit 1         // produz 1 e CONTINUA
    emit 2
```

Em Python as duas ideias dividem a mesma palavra (`yield`), o que é uma fonte
conhecida de confusão — uma função vira geradora só por conter um `yield`, sem
nada no cabeçalho anunciando isso. DataForge separa: `stream action` no cabeçalho
diz o que a ação é, `emit` diz o que ela faz.

Dentro de um `stream action`, `yield` continua servindo para encerrar a produção
antes do fim.

## Consumindo um stream

| Chamada | Devolve |
|---------|---------|
| `s.to_cluster()` | tudo, como lista |
| `s.take(n)` | os `n` primeiros |
| `s.next()` | o próximo item (ou `void`) |
| `s.count()` | quantos itens ao todo |
| `s.first()` | o primeiro (ou `void`) |
| `cycle v in s:` | percorre item a item |

## Saída esperada

```
Stream
[1, 2, 3, 4, 5]
[1, 2, 3]
recebi 1
recebi 2
recebi 3
data forge lang
isso imprime, nao produz
pares ate 10: [0, 2, 4, 6, 8, 10]
```

## Experimente

- Troque `emit i` por `yield i` e veja o stream terminar no primeiro item.
- Escreva um generator que emite os quadrados perfeitos até um limite.
