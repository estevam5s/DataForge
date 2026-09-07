# Exercicio 129 — Records com métodos

## Enunciado

Adicione comportamento a um record sem abrir mão da imutabilidade.

## Conceitos

Um record pode ter métodos. A regra é simples e não tem exceção: **um método
pode ler `self`, nunca escrever**.

```dataforge
record Retangulo:
    largura: Number
    altura: Number

    action area():
        yield self.largura * self.altura
```

## Métodos que "modificam"

Quando um método precisaria mudar o estado, ele devolve um record novo:

```dataforge
action escalar(fator):
    yield Retangulo(self.largura * fator, self.altura * fator)
```

Chamar `r.escalar(2)` não altera `r` — devolve outro retângulo. Esse é o mesmo
padrão de `"abc".upper()` em qualquer linguagem: a string original continua lá.

## `toString`

O método `toString` é especial: o runtime o chama em `out` e em `str()`.

```dataforge
action toString():
    yield $"{self.largura}x{self.altura}"
```

Sem ele, `out r` mostraria `Retangulo(largura: 3, altura: 4)`. Com ele, `3x4`.

## Records em pattern matching

Records se desmontam em padrões, e é aí que o desenho todo se paga:

```dataforge
match fig:
    point Retangulo(l, a) when l is a:
        yield "quadrado"
    point Retangulo:
        yield "retangulo"
```

`point Retangulo(l, a)` faz três coisas de uma vez: verifica o tipo, extrai os
campos por posição e liga cada um a um nome. O `when` acrescenta uma condição.

## Saída esperada

```
3x4
area: 12  perimetro: 14
quadrado? no
dobrado: 6x8 com area 48
quadrado retangulo outra forma
```

## Experimente

- Adicione `action diagonal()` usando `sqrt`.
- Faça `escalar` recusar fator zero ou negativo com `guard`.
- Acrescente `point Retangulo(l, a) when l bigger a: yield "deitado"` e veja onde
  colocá-lo para que seja alcançado.
