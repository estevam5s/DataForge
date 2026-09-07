# Exercicio 190 — Polimorfismo

## Enunciado

Trate tipos diferentes pela interface comum, e acrescente um tipo novo sem tocar
em quem usa.

## Conceitos

```dataforge
formatos := [spawn ComoJson(dados), spawn ComoCsv(dados), spawn ComoTexto(dados)]

cycle f in formatos:
    out f.exportar()      // não sabe qual formato é
```

O ganho do polimorfismo **não é evitar `given`**. É que o laço acima não muda
quando chega um quarto formato. Compare com o alternativo:

```dataforge
given tipo is "json":
    ...
orif tipo is "csv":
    ...              // toda vez que chega um formato, este bloco cresce
```

| Linguagem | Equivalente |
|-----------|-------------|
| Python | duck typing / `Protocol` |
| TypeScript | `interface` |
| Java | `interface` + `implements` |
| Rust | `dyn Trait` |

## O que observar

**O trait é o que garante.** Sem ele, um formato que esqueceu `exportar` só
falharia quando o laço chegasse nele. Com trait, falha na declaração.

**Acrescentar um tipo é uma adição, não uma edição.** `ComoMarkdown` entrou no
fim do exercício, e nenhuma linha anterior mudou. É essa propriedade que faz o
código envelhecer bem.

## Armadilhas

- Polimorfismo com dois casos que nunca vão crescer é cerimônia: um `given`
  resolve, e se lê melhor.
- Se cada implementação precisa de um parâmetro diferente, a interface comum não
  existe de verdade — e forçá-la produz assinaturas com argumentos que metade
  ignora.

## Relacionados

- [186 — Abstratos e traits](186_abstratos_e_traits.md)
- [188 — Composição](188_composicao.md)
