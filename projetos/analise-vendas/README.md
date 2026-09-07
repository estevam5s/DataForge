# analise-vendas

Lê um CSV de vendas e produz um relatório com estatística e gráficos de terminal.

```bash
dataforge install
dataforge run src/main.df -- dados/vendas.csv
```

```
┌───────────────┬──────────────┐
│ Indicador     │ Valor        │
├───────────────┼──────────────┤
│ Total         │ R$ 35.300,00 │
│ Ticket médio  │ R$ 2.353,33  │
│ Mediana       │ R$ 1.200,00  │
│ Desvio padrão │ R$ 1.991,27  │
└───────────────┴──────────────┘

  ⚠ dispersão alta: o ticket médio não representa bem as vendas.

Evolução mensal
  ▄▁█
Tendência: subindo R$ 345,00 por mês (r² = 0.269)
  (ajuste fraco — a tendência não é confiável com estes dados)
```

## Decisões

**Valores em centavos inteiros.** O CSV traz `4500.00`; a leitura converte para
450000 centavos. Somar quinze floats acumula erro; somar inteiros não.

**Converter na entrada, falhar cedo.** Uma linha com valor inválido aborta a
leitura dizendo o número da linha — melhor que um `void` chegar a uma soma e
produzir um total errado em silêncio.

**O relatório desconfia de si mesmo.** Quando o desvio passa de metade da média,
ele avisa que o ticket médio não descreve as vendas. Quando o r² da tendência é
baixo, avisa que a tendência não é confiável. Um relatório que só apresenta
números convida a conclusões que os dados não sustentam.
