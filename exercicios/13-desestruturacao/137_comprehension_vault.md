# Exercicio 137 — Compreensão de vaults

## Enunciado

Construa dicionários com a mesma sintaxe das listas, produzindo um par
chave-valor a cada iteração.

## Conceitos

A única diferença para a compreensão de lista é que a expressão vira um par:

```
{ <chave>: <valor>  cycle <nome> in <fonte>  [given <condição>] }
```

```dataforge
quadrados := {n: n * n cycle n in nums}
// {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

## Percorrendo um vault

`cycle k in umVault` percorre as **chaves**, não os pares. Para chegar ao valor,
indexe:

```dataforge
invertido := {originais[k]: k cycle k in originais.keys()}
```

Isso é consistente com `"chave" in vault`, que também testa chaves.

## Três aplicações que valem memorizar

### Indexar por um campo

Transformar uma lista num índice de acesso direto:

```dataforge
por_id := {p["id"]: p["nome"] cycle p in pessoas}
out por_id[20]        // "Bruno" — sem varrer a lista
```

De busca linear para acesso direto, numa linha.

### Contar ocorrências

```dataforge
distintas := unique(palavras)
contagem := {p: palavras.count(p) cycle p in distintas}
```

Para listas grandes prefira `Arcane.Collections.counter`, que percorre uma vez só
em vez de uma vez por item distinto.

### Normalizar chaves

```dataforge
limpo := {k.trim().lower(): bruto[k] cycle k in bruto.keys()}
```

Dados de fora chegam com espaços e caixa inconsistentes. Normalizar na fronteira
evita ter que lembrar disso no resto do programa.

## Chaves repetidas

Se duas iterações produzem a mesma chave, **a última vence** — mesma regra do
spread. Isso é silencioso, então cuidado ao usar como chave algo que pode se
repetir.

## Saída esperada

```
{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
{2: 4, 4: 16}
{1: a, 2: b, 3: c}
{10: Ana, 20: Bruno}
{sol: 3, lua: 2, mar: 1}
{nome: Ana, idade: 30}
```

## Experimente

- Agrupe as pessoas por faixa etária em vez de indexar por id.
- Compare a contagem manual com `Arcane.Collections.counter`.
