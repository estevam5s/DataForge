# Exercicio 157 — Datas e horas

## Enunciado

Crie, formate e compare datas com `Arcane.Time`.

## Conceitos

`Arcane.Time` trabalha com datas como vaults marcados com `__type__: "DateTime"`.
Isso as faz circular pelo runtime como qualquer valor — dá para guardar numa
lista, passar por pipeline, serializar.

### Construir

```dataforge
Time.now()                        // agora, com hora
Time.today()                      // hoje à meia-noite
Time.date(2026, 12, 25)           // uma data
Time.datetime(2026, 3, 15, 14, 30, 0)
Time.from_timestamp(1767000000)
Time.parse("2026-06-15")          // interpreta vários formatos
```

`parse` tenta ISO, brasileiro e as variantes com hora — sem você precisar dizer
qual é.

### Formatar

| Chamada | Resultado |
|---------|-----------|
| `to_date_string(d)` | `25/12/2026` |
| `to_time_string(d)` | `14:30:00` |
| `to_br(d)` | `25/12/2026 14:30:00` |
| `to_iso(d)` | `2026-12-25T00:00:00` |
| `format(d, "%d/%m")` | livre, com códigos strftime |

### Componentes

```dataforge
Time.year(d)  Time.month(d)  Time.day(d)
Time.hour(d)  Time.minute(d)  Time.second(d)
Time.weekday(d)          // 0 = segunda
Time.weekday_name(d)     // "sexta-feira"
Time.month_name(d)       // "dezembro"
Time.quarter(d)          // 1..4
Time.day_of_year(d)      // 1..366
Time.week_of_year(d)
```

Os nomes vêm **em português** — é a língua do módulo, e evita ter que traduzir
`"Friday"` em cada relatório.

## Comparação

```dataforge
Time.is_before(a, b)
Time.is_after(a, b)
Time.is_same_day(a, b)
Time.is_weekend(d)
Time.is_leap_year(2024)
```

`is_same_day` existe porque comparar dois `DateTime` diretamente compararia
também a hora — duas coisas no mesmo dia, mas às 9h e às 15h, não são iguais.

## Saída esperada

```
25/12/2026
15/03/2026 14:30:00
2026-12-25T00:00:00
25/12/2026 cai numa sexta-feira
mes: dezembro
15/03/2026 as 14:30
15/06/2026
trimestre: 4  dia do ano: 359
```

## Experimente

- Descubra em que dia da semana você nasceu.
- Liste todas as sextas-feiras 13 de um ano.
