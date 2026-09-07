# Exercicio 131 — Enums com valores

## Enunciado

Associe um dado a cada membro do enum e converta entre valor e membro nas duas
direções.

## Conceitos

Um membro pode carregar um valor:

```dataforge
enum Prioridade:
    Baixa := 1
    Media := 5
    Alta := 10
    Critica := 100
```

Sem `:=`, o valor é o próprio nome. Com `:=`, é o que você escrever — número,
texto, qualquer coisa.

## Por que isso importa: a fronteira do sistema

Dentro do seu programa você quer `Moeda.Real`. Mas o banco de dados guarda
`"BRL"`, a API devolve `"BRL"`, o CSV tem `"BRL"`. O valor é a **ponte** entre os
dois mundos:

```dataforge
vinda_do_banco := "EUR"
moeda := Moeda.from_value(vinda_do_banco)     // Moeda.Euro
```

E `from_value` devolve `void` para um valor desconhecido, em vez de inventar um
membro. Combinado com `??`, isso vira um padrão limpo:

```dataforge
moeda := Moeda.from_value(entrada) ?? Moeda.Real
```

## Valores numéricos como ordem

Quando o valor é um número, ele carrega significado de ordenação:

```dataforge
sorted(tarefas >> morph t: t["prio"].value)     // [1, 5, 100]
```

Isso é mais expressivo do que depender de `.index`: o `.index` reflete a ordem de
declaração, o `.value` reflete a ordem de *negócio*. Se amanhã você inserir
`Urgente := 50` no meio da lista, os índices mudam mas os pesos não.

## Comparando com outras linguagens

Em TypeScript, `enum Prioridade { Baixa = 1 }` gera um mapeamento bidirecional
implícito e `Prioridade[1]` funciona. Em DataForge a conversão é explícita
(`from_value`), o que evita a ambiguidade de um enum cujos valores colidem com
seus índices.

## Saída esperada

```
10
BRL
EUR -> Euro
[1, 5, 100]
soma dos pesos: 116
largar tudo hoje ainda quando der
```

## Experimente

- Acrescente `Urgente := 50` e confirme que a ordenação por `.value` continua certa.
- Escreva `action de_texto(t)` usando `from_value(t) ?? Prioridade.Media`.
