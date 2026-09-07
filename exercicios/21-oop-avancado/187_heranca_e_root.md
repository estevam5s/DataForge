# Exercicio 187 — Herança e `root`

## Enunciado

Estenda o comportamento do pai sem reescrevê-lo.

## Conceitos

```dataforge
blueprint Artigo extends Documento:
    action cabecalho():
        yield root.cabecalho() + $"\npor {self.autor}"
```

`root` chama a versão do pai. É o que distingue **estender** de
**reimplementar**: o filho acrescenta, e continua acompanhando as mudanças do
pai.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `super()` |
| TypeScript / Java | `super` |
| Rust | não tem herança; usa composição |

## O que observar

**Polimorfismo sem esforço.** O método `render` foi herdado sem mudança e chama
`self.cabecalho()` — que resolve para a versão do filho. Um método do pai
enxerga as sobrescritas do filho.

**`final` impede sobrescrita.** Um método marcado `final` não pode ser trocado
pelo herdeiro, e a tentativa falha na declaração:

```
erro[DF0301]: 'Filho.identidade' cannot override 'Base.identidade',
              which is declared final
```

Use `final` no que o resto da hierarquia depende para funcionar.

## Armadilhas

- Herança amarra o filho ao pai **para sempre**. Antes de estender, pergunte se
  não é composição — veja o [188](188_composicao.md).
- Uma cadeia de herança com mais de dois ou três níveis costuma ser sinal de que
  a modelagem foi longe demais.

## Relacionados

- [188 — Composição](188_composicao.md)
- [184 — Visibilidade](184_visibilidade.md)
