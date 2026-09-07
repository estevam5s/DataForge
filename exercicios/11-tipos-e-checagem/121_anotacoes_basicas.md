# Exercicio 121 — Anotações de tipo

## Enunciado

Declare variáveis com tipo explícito e comprove que atribuir o tipo errado é
recusado em tempo de execução.

## Conceitos

Uma anotação em DataForge tem a forma `nome: Tipo := valor`. Ela é **opcional** —
o código funciona sem ela — mas quando presente é **verificada**: tanto pelo
analisador estático (`dataforge check`) quanto no momento da atribuição.

| Tipo | Aceita |
|------|--------|
| `Integer` | inteiros |
| `Float` | decimais **e** inteiros |
| `Number` | inteiros ou decimais |
| `String` | textos |
| `Boolean` | `yes` / `no` |
| `Cluster` | listas |
| `Vault` | dicionários |
| `Void` | apenas `void` |
| `Any` | qualquer coisa (desliga a checagem) |
| *nome de record/blueprint/enum* | instâncias daquele tipo |

## A regra de conversão

Há uma única flexibilização, e ela existe porque é matematicamente segura:

```dataforge
media: Float := 8        // ok: todo inteiro é um decimal válido
quantidade: Integer := 3.5   // erro: 3.5 não é inteiro
```

Um `Integer` entra onde se espera `Float`. O contrário perderia informação, e
por isso é recusado.

## Passo a passo

1. Cada declaração associa um tipo ao nome.
2. `media: Float := 8` passa pela regra de alargamento acima.
3. O bloco `monitor` captura a violação para que o programa siga.
4. Os `assert` confirmam o comportamento nos dois sentidos.

## Saída esperada

```
30 Ana 1.72 yes
[8, 9, 10] {tema: escuro}
recusado: variable 'quantidade' declared as Integer but got Float
```

## Experimente

- Troque `notas: Cluster := [8, 9, 10]` por `notas: Vault := [8, 9, 10]`.
- Rode `dataforge check` neste arquivo: o erro aparece **antes** de executar.
- Anote com `Any` e veja a checagem desaparecer.
