# Exercicio 126 — Tipagem gradual com `Any`

## Enunciado

Use `Any` onde o tipo depende do uso, e estreite-o dentro da ação com pattern
matching.

## Conceitos

DataForge tem **tipagem gradual**: você anota o que sabe e deixa o resto livre.
`Any` é a forma de dizer isso explicitamente.

```dataforge
action envolver(valor: Any) -> Vault:
    yield {"tipo": typeof(valor), "valor": valor}
```

Isso é diferente de **não anotar**:

| Forma | Significado |
|-------|-------------|
| `action f(x):` | não pensei sobre o tipo |
| `action f(x: Any):` | pensei, e qualquer tipo serve |

A segunda comunica intenção. Numa base de código grande, essa diferença é o que
separa "falta anotar" de "está anotado como flexível".

## Estreitando o tipo

Aceitar `Any` não significa tratar tudo igual. O padrão é estreitar logo na
entrada:

```dataforge
match v:
    point Integer as n:
        yield $"inteiro {n}"
    point String as s:
        yield $"texto de {len(s)} letras"
```

Cada `point Tipo as nome` faz duas coisas ao mesmo tempo: **testa** o tipo e
**liga** o valor a um nome já com aquele tipo garantido. É o equivalente
DataForge do *type narrowing* do TypeScript.

## A ordem dos `point` importa

Padrões são testados de cima para baixo, e o primeiro que casa vence. Coloque os
específicos antes dos gerais:

```dataforge
point Integer as n when n bigger 100:    // específico
    ...
point Integer:                           // geral
    ...
```

Invertido, o segundo nunca rodaria.

## Saída esperada

```
{tipo: Integer, valor: 42}
{tipo: String, valor: texto}
{tipo: Cluster, valor: [1, 2]}
inteiro 7
decimal 2.5
texto de 3 letras
lista com 3 itens
dicionario
nada
```

## Experimente

- Remova `point Void` e veja `void` cair no `default`.
- Adicione `point Integer when n bigger 100` **depois** de `point Integer` e
  confirme que ele nunca é alcançado.
