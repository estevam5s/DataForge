# 252 — Tipos nomeados

`type` dá nome a um tipo. Cinco formas, uma declaração só: o que muda é o
que vem depois do `:=`.

| Forma | Escreve-se | O que promete |
|---|---|---|
| alias | `type Id := Integer` | um nome para o mesmo tipo |
| alias genérico | `type Par<T> := Cluster<T>` | uma função de tipo |
| união | `type Json := String \| Integer` | um destes, e nada mais |
| interseção | `type Auditavel := Serial & Ordenavel` | todos ao mesmo tempo |
| refinamento | `type Positivo := Integer where valor bigger 0` | o tipo, com uma regra |
| opaco | `opaque type Cpf := String where len(valor) is 11` | só nasce validado |

## Transparente confere, opaco embrulha

Um tipo transparente é uma **conferência**: `x: Positivo := 5` guarda o
número 5, e `typeof(x)` responde `Integer`. Nada muda de forma, e por isso
nada quebra — o valor continua sendo aceito onde um `Integer` é aceito.

Um tipo opaco é um **valor**: `Cpf("12345678901")` devolve um objeto que
sabe o próprio nome. É o que torna o tipo **nominal**, e é o ponto todo —
um texto com onze dígitos não é um `Cpf`:

```dataforge
action cadastrar(quem: Cpf) -> String:
    yield quem.valor

cadastrar("12345678901")     // recusado: texto não é Cpf
cadastrar(Cpf("12345678901")) // aceito
```

Se o opaco fosse só uma conferência de formato, `cadastrar(senha)`
passaria sem reclamar — e aí o tipo não protegeria de nada.

## A regra roda na fronteira

`where valor bigger 0` é uma expressão comum, com `valor` ligado ao que
está entrando. Ela é conferida na declaração, no parâmetro, no **retorno**
e no campo. É por isso que `desconto(100, 200)` falha: a conta daria
`-100`, e o retorno promete `Positivo`.

A **base vem antes da regra**, sempre. `type Nome := String where
len(valor) bigger 2` recebendo um número recusa por tipo — rodar `len`
sobre um número daria uma mensagem sobre `len`, e não sobre o tipo que
você escreveu.

## O que o `check` prova antes de rodar

Sobre um **literal**, o analisador decide: `x: Positivo := -1` é acusado
com `tipo-refinado` antes de a primeira linha rodar. Sobre um valor que
vem de uma chamada, de um arquivo ou da rede, ele **cala** — um falso
alarme ensina a desligar o analisador.

Dentro de um `monitor` os erros viram avisos, que é o que você vê ao rodar
o `check` neste exercício: as falhas aqui são de propósito.
