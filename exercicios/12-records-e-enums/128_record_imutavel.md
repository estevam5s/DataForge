# Exercicio 128 — Imutabilidade e `with`

## Enunciado

Comprove que um record não pode ser alterado, e use `with` para derivar cópias
modificadas.

## Conceitos

Um record é **imutável**. Isso não é uma restrição arbitrária: é o que permite a
igualdade estrutural funcionar de forma confiável e o que elimina uma classe
inteira de bugs — o valor que você guardou não muda debaixo dos seus pés.

```dataforge
original.saldo := 2000
// erro: Record 'Conta' is immutable: cannot assign to 'saldo'.
```

## O operador `with`

Para "mudar" um record você deriva um novo:

```dataforge
depositado := original with {"saldo": original.saldo + 500}
```

Leia como: *"o mesmo que `original`, mas com `saldo` valendo outra coisa"*.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `dataclasses.replace(obj, saldo=…)` |
| JavaScript | `{...obj, saldo: …}` |
| Rust | `Conta { saldo: …, ..original }` |
| Elixir | `%{original \| saldo: …}` |

O `with` também **valida os nomes**: pedir um campo que não existe é erro, não
silêncio. Compare com o spread de JavaScript, onde `{...obj, sldo: 1}` cria
alegremente um campo novo com o nome digitado errado.

## Transformações encadeadas

Como cada operação devolve um record novo, elas compõem naturalmente:

```dataforge
final := sacar(depositar(depositar(original, 200), 300), 100)
```

Nenhuma das chamadas tocou em `original`. Se algo der errado no meio, você ainda
tem o estado anterior intacto — que é exatamente o que se quer numa transação.

## Um detalhe de leitura

Chamadas aninhadas se leem de dentro para fora, o que cansa. Com pipelines fica
mais direto:

```dataforge
final := [original]
    >> morph c: depositar(c, 200)
    >> morph c: depositar(c, 300)
```

## Saída esperada

```
Record 'Conta' is immutable: cannot assign to 'saldo'. Build a changed copy with "registro with {'saldo': valor}".
Conta(titular: Ana, saldo: 1000)
Conta(titular: Ana, saldo: 1500)
Conta(titular: Ana, saldo: 1400)
Record 'Conta' has no field(s): limite
```

## Experimente

- Faça `sacar` retirar mais do que o saldo e veja o `guard` agir.
- Guarde cada estado intermediário numa lista para ter o histórico completo.
