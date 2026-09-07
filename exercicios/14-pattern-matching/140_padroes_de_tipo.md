# Exercicio 140 — Padrões de tipo

## Enunciado

Case pelo tipo do valor e ligue o resultado a um nome já com o tipo garantido.

## Conceitos

Um nome **em maiúscula** num `point` testa o tipo:

```dataforge
point Integer as n:
    yield $"inteiro {n}"
```

Isso faz duas coisas de uma vez: **testa** que `v` é um Integer e **liga** `n` ao
valor. É o *type narrowing* que TypeScript faz com `typeof x === "number"`, aqui
como sintaxe de primeira classe.

## Tipos aceitos

Todos os que valem numa anotação:

`Integer` · `Float` · `Number` · `String` · `Boolean` · `Cluster` · `Vault` ·
`Void` · `Action` · `Stream` · `Any` · e o nome de qualquer record, blueprint ou
enum que você definiu.

## `Number` e `Any`

Dois casos especiais que valem entender:

```dataforge
point Number:     // casa com Integer OU Float
point Any:        // casa com tudo, inclusive void
```

`point Any` é equivalente a `point _` — use `_` quando não precisar do valor,
`Any` quando quiser deixar explícito que aceita qualquer tipo.

## Guardas com `when`

Um `when` acrescenta uma condição que roda **depois** de o padrão casar:

```dataforge
point Integer as n when n smaller 0:
    yield $"inteiro negativo ({n})"
point Integer as n:
    yield $"inteiro {n}"
```

Se a guarda falha, o `match` **continua** para o próximo `point`. Por isso o par
acima funciona: negativos param no primeiro, o resto cai no segundo.

Isso torna a ordem ainda mais importante: o específico (com guarda) vem antes do
geral.

## Por que `when` e não `given`

`given` já é o ternário (`a given c otherwise b`). Usar a mesma palavra numa
guarda criaria ambiguidade real no parser: em `point n given x` o parser não
saberia se `given` abre uma guarda ou um ternário. `when` resolve isso sem
ambiguidade.

## Saída esperada

```
inteiro 7
inteiro negativo (-3)
decimal 2.5
texto de 3 letras
booleano
lista com 2 itens
dicionario
ponto (3, 4)
nada
```

## Experimente

- Remova `point Void` e veja `void` cair no `default`.
- Adicione `point Integer as n when n % 2 is 0` e escolha onde colocá-lo.
