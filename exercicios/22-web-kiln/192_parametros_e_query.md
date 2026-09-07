# Exercicio 192 — Parâmetros de caminho e query string

## Enunciado

Leia `:id` do caminho e `?campo=` da query string.

## Conceitos

Um padrão de rota tem duas formas de capturar:

| Padrão | Casa | Resultado |
|--------|------|-----------|
| `/users/:id` | `/users/42` | `params["id"]` é `"42"` |
| `/files/*caminho` | `/files/a/b.txt` | `params["caminho"]` é `"a/b.txt"` |

`:nome` para um trecho, `*nome` para tudo o que sobrar — barras inclusive.

Dentro de uma rota você já tem seis nomes prontos:

```dataforge
route GET "/usuarios/:id":
    respond json {"id": params["id"], "formato": query["f"] ?? "curto"}
```

| Nome | É |
|------|---|
| `req` | a requisição inteira |
| `params` | os parâmetros do caminho |
| `query` | a query string |
| `body` | o corpo já interpretado |
| `headers` | os cabeçalhos, em minúsculas |
| `session` | a sessão do visitante |

## O que observar

**Parâmetro é sempre texto.** `/usuarios/42` dá `"42"`, não `42` — HTTP não
tem tipos. Converta com `int()` quando precisar.

**A query decide sozinha entre texto e lista.** `?nome=x` dá `"x"`;
`?tag=a&tag=b` dá `["a", "b"]`. Obrigar a indexar `[0]` sempre seria ruído em
95% dos casos.

**`??` combina bem com query ausente.** `query["f"] ?? "curto"` cobre o caso de
o visitante não ter passado o campo.

## Erros comuns

- Comparar `params["id"] is 42`. É `"42"`, texto. Use `int(params["id"])`.
- Esperar que `query["tag"]` seja sempre lista. Com um valor só, é texto.
