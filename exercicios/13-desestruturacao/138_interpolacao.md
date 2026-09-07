# Exercicio 138 — Interpolação de strings

## Enunciado

Monte textos com valores embutidos, sem concatenar manualmente.

## Conceitos

Uma string prefixada por `$` interpreta `{…}` como expressão:

```dataforge
out $"Ola, {nome}!"
```

Compare com a alternativa:

```dataforge
"Ola, " + nome + "! Voce tem " + str(idade) + " anos."
$"Ola, {nome}! Voce tem {idade} anos."
```

A segunda tem menos ruído, menos `+` e nenhum `str()` — a conversão é automática.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `f"Ola, {nome}"` |
| JavaScript | `` `Ola, ${nome}` `` |
| C# | `$"Ola, {nome}"` |
| Kotlin | `"Ola, $nome"` |

## Por que o `$` é obrigatório

Strings comuns **não** interpolam:

```dataforge
out "{nome}"      // sai literalmente: {nome}
out $"{nome}"     // sai: Ana
```

Isso preserva o código existente e permite escrever JSON, regex e templates de
outros sistemas sem escapar nada.

## O que cabe dentro das chaves

Qualquer expressão:

```dataforge
$"{idade + 1}"                    // aritmética
$"{moeda(saldo)}"                 // chamada de ação
$"{usuario["tags"][0]}"           // índices e chaves
$"{"par" given n % 2 is 0 otherwise "impar"}"    // ternário
```

Inclusive strings com aspas duplas dentro — o lexer acompanha o aninhamento.

## Formatação segue a linguagem

Os valores são convertidos com as mesmas regras de `out`:

```dataforge
$"{yes} {no} {void}"     // "yes no void", não "True False None"
```

Um record com `toString` usa o seu `toString`. Uma lista sai como `[1, 2, 3]`.

## Chaves literais

Para uma chave de verdade no texto, dobre:

```dataforge
$"{{isso e literal}}"     // {isso e literal}
```

## Saída esperada

```
Ola, Ana!
Ana tem 30 anos e fara 31 no proximo aniversario
metade do saldo: 617.25
saldo formatado: R$ 1234.5
Bruno e admin
ativo=yes vazio=void
{isso e literal} e Ana e interpolado
Ola, Ana! Voce tem 30 anos.
Ola, Ana! Voce tem 30 anos.
Mouse       2x  R$ 160.0
```

## Experimente

- Use `pad_end` e `pad_start` dentro da interpolação para alinhar colunas.
- Escreva `$"{}"` e leia o erro do lexer.
