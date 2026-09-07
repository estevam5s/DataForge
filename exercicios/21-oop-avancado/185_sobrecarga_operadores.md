# Exercicio 185 — Sobrecarga de operadores

## Enunciado

Faça `+`, `-`, `*` e `==` funcionarem no seu próprio tipo.

## Conceitos

```dataforge
blueprint Vetor:
    operator + (o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)

    operator == (o):
        yield self.x is o.x and self.y is o.y
```

Sobrecarregar operador só vale quando a operação é **óbvia**: somar dois vetores,
comparar dois valores monetários. Se alguém precisa ler a documentação para saber
o que `+` faz no seu tipo, um método com nome é melhor.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `__add__`, `__eq__` |
| C++ | `operator+` |
| Rust | `impl Add for T` |
| Kotlin | `operator fun plus` |

## O que observar

**`isnt` sai de `==` negado.** Declarar `operator ==` já faz `isnt` funcionar —
não é preciso declarar os dois.

**Operadores são herdados.** Um filho ganha os do pai sem redeclarar.

**Nem todo símbolo pode ser sobrecarregado.** A mensagem lista quais:

```
erro[DF0103]: '@' cannot be overloaded. You can overload: !=, %, *, **, +, -, /, <, <=, ==, >, >=
```

## Armadilhas

- `+` deve **devolver um valor novo**, não alterar `self`. `a + b` que muda `a`
  surpreende quem lê.
- Operadores não comutativos (`-`, `/`, `<`) só são tentados no lado esquerdo.
  `2 * vetor` não funciona se só `Vetor` define `*`; escreva `vetor * 2`.

## Relacionados

- [189 — Records vs blueprints](189_records_vs_blueprints.md)
- [186 — Abstratos e traits](186_abstratos_e_traits.md)
