# Exercicio 130 — Enums

## Enunciado

Declare um conjunto fechado de valores nomeados e use seus membros com garantia
de que não existe um valor fora da lista.

## Conceitos

Um **enum** define um conjunto fechado. Comparando:

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `class Status(Enum)` |
| TypeScript | `enum Status { … }` |
| Rust | `enum Status { … }` (sem payload, por ora) |
| Java | `enum Status { … }` |

```dataforge
enum Status:
    Rascunho
    Publicado
    Arquivado
```

## O problema que ele resolve

Sem enum, estados viram texto solto:

```dataforge
pedido := {"status": "publicado"}
given pedido["status"] is "Publicado":     // nunca entra: caixa diferente
```

Um erro de digitação vira um `no` silencioso. Com enum, `Status.Publicad` é erro
na hora — e o `dataforge check` acha antes mesmo de rodar.

## Cada membro carrega três coisas

```dataforge
Status.Publicado.name     // "Publicado"  — o identificador
Status.Publicado.value    // "Publicado"  — o valor (padrão = nome)
Status.Publicado.index    // 1            — a posição na declaração
```

O `.index` segue a ordem em que você escreveu, o que o torna útil para ordenar:
`Rascunho` vem antes de `Publicado`, que vem antes de `Arquivado`.

## Utilitários

| Chamada | Devolve |
|---------|---------|
| `Status.names()` | `["Rascunho", "Publicado", "Arquivado"]` |
| `Status.values()` | os valores |
| `Status.members()` | os membros, para percorrer |
| `Status.count()` | `3` |
| `Status.has("X")` | `yes` / `no` |
| `Status.from_name("X")` | o membro, ou `void` |
| `Status.from_value(v)` | o membro com aquele valor, ou `void` |

## Saída esperada

```
Status.Rascunho
Publicado Publicado 1
yes
no
[Rascunho, Publicado, Arquivado]
3
yes no
Enum 'Status' has no member 'Removido'. Members: Rascunho, Publicado, Arquivado
  0: Rascunho
  1: Publicado
  2: Arquivado
```

## Experimente

- Ordene uma lista de status por `.index`.
- Escreva `action proximo(s)` que avança para o próximo membro.
