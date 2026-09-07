# Exercicio 123 — `typeof` e conversão

## Enunciado

Descubra o tipo de qualquer valor e converta entre tipos, incluindo o caso em
que a conversão é impossível.

## Conceitos

### `typeof`

`typeof x` devolve **o mesmo nome que você usaria numa anotação**. Isso não é
detalhe: significa que estas duas linhas falam a mesma língua.

```dataforge
idade: Integer := 30
out typeof(idade)        // Integer
```

Para tipos que você define, `typeof` devolve o nome que você deu:

| Valor | `typeof` |
|-------|----------|
| `Ponto(1, 2)` | `"Ponto"` |
| `Cor.Verde` | `"Cor"` (o enum, não o membro) |
| `contador()` | `"Stream"` |

### `cast`

`cast valor as Tipo` converte explicitamente.

```dataforge
cast "42" as Integer     // 42
cast 3.9 as Integer      // 3     — trunca, não arredonda
cast "abc" as Integer    // erro
```

Note que `cast 3.9 as Integer` dá `3`, não `4`. Truncar é a regra; para
arredondar use `round(3.9)`.

## Passo a passo

1. O `cycle` percorre um valor de cada tipo e imprime seu nome.
2. Os `assert` fixam o contrato de `typeof` para todos os tipos.
3. A última parte confirma que uma conversão impossível dispara erro em vez de
   devolver lixo silenciosamente.

## Saída esperada

```
Integer
Float
String
Boolean
Void
Cluster
Vault
Ponto
Cor
conversoes verificadas
```

## Experimente

- `out typeof(typeof(1))` — o que sai, e por quê?
- Compare `cast 3.9 as Integer` com `round(3.9)`.
