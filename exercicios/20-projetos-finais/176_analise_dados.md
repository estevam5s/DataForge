# Exercicio 176 — Projeto: análise de dados

## Enunciado

Carregue, limpe, agregue e visualize um conjunto de dados — o fluxo completo de
uma análise.

## As cinco etapas

```
1. MODELAR      record Venda
2. DESCREVER    média, mediana, desvio, quartis
3. AGREGAR      por vendedor, por região, por mês
4. VISUALIZAR   histogramas em texto
5. PROJETAR     correlação, regressão, previsão
```

## Modelar antes de analisar

```dataforge
vendas := bruto >> morph l: Venda(l[0], l[1], l[2], l[3])
```

Uma linha converte listas anônimas em records tipados. Depois disso, `v.valor` em
vez de `l[3]` — e um erro de índice vira um erro de campo, que o `dataforge check`
encontra.

## Média e mediana contam histórias diferentes

```dataforge
Math.mean(valores)      // sensível a extremos
Math.median(valores)    // resistente
```

Quando as duas divergem muito, a distribuição é assimétrica — geralmente por
causa de poucos valores muito altos ou baixos. Olhar as duas é mais informativo
que olhar só a média.

## Quartis e outliers

```dataforge
q := An.quartiles(valores)      // q1, q2, q3
An.iqr(valores)                 // Q3 - Q1
An.outliers(valores)            // fora de 1.5 × IQR
```

O critério de 1,5 × IQR é o mesmo do boxplot. Um outlier não é necessariamente
um erro — pode ser a venda excepcional que você quer entender.

## Histograma proporcional

```dataforge
barra := "#".repeat(r["total"] * 30 ~/ max(sum(valores), 1))
```

O `~/` (divisão inteira) dá o número de blocos; `max(..., 1)` evita divisão por
zero. Trinta caracteres cabem em qualquer terminal.

## Correlação e regressão

```dataforge
An.correlation(meses, serie)          // -1 a 1
An.linear_regression(meses, serie)    // slope e intercept
An.r_squared(meses, serie)            // qualidade do ajuste
An.predict_linear(modelo, 5)          // extrapola
```

| R² | Significa |
|----|-----------|
| perto de 1 | a reta explica bem os dados |
| perto de 0 | a reta não explica nada |

**Cuidado com extrapolação.** Prever o mês 5 a partir de 4 meses é razoável;
prever o mês 50 não é. A reta descreve o passado observado, não garante o futuro.

## Média móvel

```dataforge
An.moving_average(serie, 2)
```

Suaviza a variação de curto prazo. Numa série ruidosa, é o que deixa a tendência
visível.

## Saída esperada

```
┌───────────────────┐
│ Analise de Vendas │
└───────────────────┘

── resumo ──
  registros:     12
  total:         R$ 155700
  media:         R$ 12975.0
  mediana:       R$ 12750.0
  ...

── por vendedor ──
  Carla   R$   63500  ############
  Ana     R$   55700  ##########
  Bruno   R$   36500  #######

── evolucao mensal ──
  mes 1: ████████████████████████ R$ 35500
  ...

── tendencia ──
  correlacao mes x total: 0.8834
  previsao para o mes 5: R$ 47660.0
```

## Experimente

- Acrescente uma coluna de custo e calcule a margem.
- Compare o crescimento de cada vendedor separadamente.
- Exporte o relatório como CSV com `Serde.records_to_csv`.
