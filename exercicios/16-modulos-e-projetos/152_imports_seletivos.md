# Exercicio 152 — Imports seletivos e apelidos

## Enunciado

Traga apenas os símbolos que você usa, com o nome que preferir.

## Conceitos

Três formas de importar, todas equivalentes em poder:

```dataforge
adopt geometria as geo                        // o módulo inteiro
adopt geometria.{area_circulo, PI}            // seletivo, forma compacta
adopt {realcar as destacar} from textos       // seletivo, com apelido
```

## Quando usar cada uma

| Forma | Boa para |
|-------|----------|
| `as geo` | módulo com muitos símbolos; o prefixo documenta a origem |
| `.{a, b}` | dois ou três símbolos usados o tempo todo |
| `{a as b} from` | resolver conflito de nomes |

O prefixo não é burocracia: `Math.sqrt(x)` diz de onde `sqrt` veio. Num arquivo
que importa cinco módulos, isso é o que evita a pergunta "onde é que isso está
definido?".

Use o seletivo quando a origem é óbvia pelo contexto e o prefixo só atrapalha.

## Apelidos resolvem colisões

```dataforge
adopt {realcar as destacar, linha} from textos
```

Se dois módulos exportam `formatar`, você não precisa renomear nada na origem —
resolve no ponto de importação:

```dataforge
adopt {formatar as formatar_data} from datas
adopt {formatar as formatar_moeda} from dinheiro
```

## Erro que ajuda

Pedir algo que o módulo não exporta:

```
Module 'geometria' does not export: nao_existe.
It exports: PI, area_circulo, perimetro_circulo, area_retangulo
```

A mensagem lista o que existe. Quase sempre o problema é um nome digitado errado,
e ver a lista resolve na hora — sem abrir o outro arquivo.

## As formas convivem

Importar o módulo inteiro **e** símbolos soltos do mesmo módulo funciona. O
arquivo só é executado uma vez (fica em cache), então `geo.PI` e `PI` são
literalmente o mesmo valor.

## Saída esperada

```
PI = 3.14159265
area = 3.1416
[titulo]
========================
sqrt(81) = 9.0  5! = 120
erro: Module 'geometria' does not export: nao_existe. It exports: PI, area_circulo, perimetro_circulo, area_retangulo
os dois estilos coexistem
```

## Experimente

- Importe `sqrt` de `Arcane.Math` com o apelido `raiz`.
- Crie dois módulos que exportam o mesmo nome e resolva o conflito com apelidos.
