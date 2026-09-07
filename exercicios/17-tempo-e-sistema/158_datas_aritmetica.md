# Exercicio 158 — Aritmética com datas

## Enunciado

Some e subtraia períodos, e calcule diferenças entre datas.

## Somar períodos

```dataforge
Time.add_days(d, 10)
Time.add_weeks(d, 2)
Time.add_months(d, 1)
Time.add_years(d, 1)
Time.add_hours(d, 3)
Time.add_minutes(d, 45)
```

Todas devolvem uma **data nova** — a original não muda. Para subtrair, passe um
número negativo.

## O caso difícil: `add_months`

O que é "31 de janeiro mais um mês"? Não existe 31 de fevereiro.

```dataforge
Time.add_months(Time.date(2026, 1, 31), 1)     // 28/02/2026
```

A regra adotada é **grampear no último dia válido** do mês de destino. É o que
Java (`java.time`), C# e a maioria das bibliotecas fazem.

Consequência a ter em mente: a operação **não é reversível**. Somar um mês e
subtrair um mês pode não voltar ao dia original (31/01 → 28/02 → 28/01). Se a
reversibilidade importa, trabalhe em dias.

## Diferenças

```dataforge
d := Time.diff(inicio, fim)
```

O resultado é uma **Duration** com vários formatos prontos:

| Campo | Exemplo |
|-------|---------|
| `d.days` | `364` |
| `d.total_hours` | `8736.0` |
| `d.total_seconds` | `31449600.0` |
| `d.human` | `"364d 0h"` |

Ter todos calculados evita a conta de conversão espalhada pelo código.

## Humanizar

```dataforge
Time.humanize(45)       // "45s"
Time.humanize(90)       // "1min 30s"
Time.humanize(3725)     // "1h 2min"
Time.humanize(90000)    // "1d 1h"
```

A função escolhe a unidade sozinha — é o que você quer numa interface, onde
"31449600 segundos" não diz nada a ninguém.

## Limites de período

```dataforge
Time.start_of_day(d)     Time.end_of_day(d)
Time.start_of_month(d)   Time.end_of_month(d)
Time.days_in_month(2024, 2)     // 29
```

`start_of_day` e `end_of_day` são o que você usa para filtrar "tudo de hoje" numa
consulta — sem eles, comparar com `Time.today()` deixa de fora tudo que aconteceu
depois da meia-noite.

## Saída esperada

```
base: 31/01/2026
+10 dias:   10/02/2026
+2 semanas: 14/02/2026
+1 mes:     28/02/2026
+1 ano:     31/01/2027
31/01 + 1 mes = 28/02/2026
de 01/01 a 31/12: 364 dias
...
1 dia, 2h30: 1d 2h = 95400.0 segundos
```

## Experimente

- Calcule quantos dias úteis há entre duas datas (pule `is_weekend`).
- Gere as datas de vencimento de 12 parcelas mensais.
