# Exercicio 135 — Desestruturar records e vaults

## Enunciado

Extraia campos nomeados de um record ou de um dicionário sem depender da ordem
em que foram declarados.

## Conceitos

Com chaves, a desestruturação passa a ser **por nome**:

```dataforge
{nome, cidade} := u
```

A ordem não importa — `{cidade, nome}` daria o mesmo resultado. Isso é o oposto
da forma com colchetes, onde a posição é tudo.

| Forma | Casa por | Fonte |
|-------|----------|-------|
| `a, b := …` | posição | lista, record |
| `{a, b} := …` | nome | vault, record, instância |

## Chave ausente falha

```dataforge
{inexistente} := config
// erro: Vault has no key 'inexistente' to destructure. Keys: host, porta, debug
```

A mensagem lista as chaves que existem — quase sempre o erro é um nome digitado
errado, e ver a lista resolve na hora.

## Resto nomeado

```dataforge
{nome, ...resto} := u
// nome  = "Ana"
// resto = {idade: 30, cidade: "Floripa"}
```

Útil para "pegue esses dois campos e passe o resto adiante" — um padrão comum ao
tratar requisições HTTP.

## O padrão de desempacotar no início

```dataforge
action apresentar(pessoa):
    {nome, idade} := pessoa
    yield $"{nome}, {idade} anos"
```

Duas vantagens sobre usar `pessoa.nome` no corpo inteiro:

1. A primeira linha **documenta** o que a ação consome.
2. O resto do corpo fica mais curto e legível.

## E no pattern matching

Dentro de um `point`, a mesma ideia aparece com `campo := padrao`:

```dataforge
point Usuario(nome := n, idade := i) when i smaller 18:
    yield $"oi, {n}"
```

Isso casa pelo tipo, extrai dois campos **por nome** e ainda aplica uma guarda.

## Saída esperada

```
Ana mora em Floripa
localhost:8080
Vault has no key 'inexistente' to destructure. Keys: host, porta, debug
{idade: 30, cidade: Floripa}
Ana, 30 anos
Bruno, 25 anos
bom dia, Ana oi, Kid
```

## Experimente

- Desestruture um vault aninhado em dois passos.
- Escreva uma ação que recebe `{...opcoes}` e mescla com um padrão.
