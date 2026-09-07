# Exercicio 183 — Propriedades com get e set

## Enunciado

Exponha um valor calculado como se fosse campo, e valide o que entra na
atribuição.

## Conceitos

Uma propriedade é **lida e escrita como campo, mas roda código**:

```dataforge
blueprint Retangulo:
    get area():
        yield self._largura * self._altura

    set largura(v):
        given v smaller_eq 0:
            trigger "largura precisa ser positiva"
        self._largura := v
```

Quem usa escreve `r.area` e `r.largura := 4` — não `r.obter_area()`. A diferença
importa: você pode transformar um campo em propriedade depois, sem quebrar quem
já usava.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `@property` / `@x.setter` |
| TypeScript | `get x()` / `set x(v)` |
| C# | `public int X { get; set; }` |
| Kotlin | `val x get() = …` |

## O que observar

**Propriedade só de leitura recusa escrita**, dizendo o que falta:

```
erro[DF0301]: 'Retangulo.area' is read-only: it has a 'get' but no 'set'.
    Add one:  set area(valor): …
```

**O setter é o lugar da validação.** Um campo público aceita qualquer coisa; uma
propriedade decide o que é válido no momento da escrita, e não depois.

**Propriedades são herdadas**, e o `get` do pai enxerga os campos do filho.

## Armadilhas

- O campo de apoio precisa ter outro nome (`_largura`), senão o setter chama a si
  mesmo — recursão infinita.
- Uma propriedade que faz trabalho pesado engana: quem lê `obj.x` espera um custo
  de leitura. Se a conta é cara, um método com nome é mais honesto.

## Relacionados

- [184 — Visibilidade](184_visibilidade.md)
- [182 — Métodos estáticos](182_metodos_estaticos.md)
