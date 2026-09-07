# Exercicio 143 — Guardas e ligação com `as`

## Enunciado

Combine condições (`when`) e apelidos (`as`) para expressar casos precisos.

## Conceitos

### `when` — a guarda

Roda **depois** que o padrão casou. Se for falsa, o `match` continua para o
próximo `point`:

```dataforge
point Integer as v when v smaller 0:
    yield "negativo"
point Integer as v when v smaller_eq 9:
    yield "unidade"
```

O primeiro casa o tipo, liga `v`, testa a condição. Falhou? Tenta o próximo.

Isso permite escrever faixas de forma direta, sem repetir o teste de tipo em cada
ramo.

### `as` — o apelido

Liga o valor **que casou**, não uma parte dele:

```dataforge
point [a, b] as tudo when a is b:
    yield $"par repetido {tudo}"
```

Aqui `a` e `b` são os elementos e `tudo` é a lista inteira. Sem `as`, você teria
que remontar `[a, b]` para exibi-la.

## A guarda enxerga o que o padrão ligou

Este é o ponto que dá poder à combinação:

```dataforge
point Pedido(itens := i, total := t) when len(i) is 0 and t bigger 0:
    yield "inconsistente: total sem itens"
```

O padrão extrai `itens` e `total`; a guarda os relaciona. Você acabou de
expressar uma **regra de negócio** — "não pode haver total sem itens" — como um
único caso do `match`.

## Ordenar por especificidade

Com guardas, a ordem passa a codificar a lógica:

```dataforge
point Pedido(itens := i, total := t) when len(i) is 0 and t bigger 0:   // 2 condições
point Pedido(itens := i) when len(i) is 0:                             // 1 condição
point Pedido(total := t) when t bigger 1000:                           // 1 condição
point Pedido:                                                          // nenhuma
```

Do mais restrito ao mais amplo. Invertida, a ordem faria os casos específicos
nunca serem alcançados — e nenhum erro apareceria, só o comportamento errado.

## Saída esperada

```
-5 -> negativo
0 -> zero
7 -> unidade
42 -> dezena
1000 -> grande
x -> nao e inteiro
par repetido [3, 3]
par distinto [1, 2]
inconsistente: total sem itens
pedido vazio
pedido grande
pedido normal
```

## Experimente

- Mova `point Integer:` (sem guarda) para o topo e veja tudo virar "grande".
- Acrescente uma faixa de milhares entre "dezena" e "grande".
