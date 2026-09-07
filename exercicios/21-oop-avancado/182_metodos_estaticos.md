# Exercicio 182 — Métodos estáticos

## Enunciado

Crie métodos que pertencem ao blueprint, não a uma instância: construtores
alternativos e constantes da família.

## Conceitos

Um método estático não recebe `self`. Ele é chamado no blueprint:

```dataforge
blueprint Temperatura:
    static action de_fahrenheit(f):
        t := spawn Temperatura()
        t.celsius := (f - 32) * 5 / 9
        yield t

gelo := Temperatura.de_fahrenheit(32)
```

O uso mais comum é o **construtor alternativo** — uma segunda forma de criar o
objeto, com nome que diz o que ela faz. `Temperatura.de_fahrenheit(32)` é mais
claro que um `setup` com um parâmetro `escala`.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `@staticmethod` / `@classmethod` |
| TypeScript | `static metodo()` |
| Java | `public static` |
| Rust | função associada, `impl` sem `self` |

## O que observar

**Chamar um método de instância no blueprint dá erro útil.** A mensagem mostra
o `spawn` que falta, em vez de estourar `Undefined name: 'self'` lá dentro:

```
erro[DF0301]: 'Temperatura.em_fahrenheit()' is an instance method and needs an object.
    Spawn one first:
        obj := spawn Temperatura(…)
        obj.em_fahrenheit(…)
    Or declare it as 'static action em_fahrenheit(…)' if it does not use 'self'.
```

## Armadilhas

- Um método estático **não enxerga `self`**. Se precisar do estado do objeto,
  ele não deveria ser estático.
- `static x := valor` (sem `action`) declara um valor compartilhado por todas as
  instâncias — e mudá-lo muda para todas.

## Relacionados

- [181 — Campos declarados](181_campos_declarados.md)
- [183 — Propriedades](183_propriedades.md)
