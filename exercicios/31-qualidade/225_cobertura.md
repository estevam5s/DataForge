# Exercicio 225 — Cobertura: o que os testes NÃO exercitaram

## Enunciado

Descubra o que a sua suíte não toca.

## O problema

Uma suíte verde não diz nada sobre o que ela não exercita. Num sistema
de 200 arquivos, o código que ninguém tocou é exatamente onde o bug
mora — e `13 passaram` não distingue "o sistema está testado" de "os
treze caminhos fáceis estão testados".

## Como se pede

```bash
dataforge test --cobertura
dataforge test --cobertura --linhas     # as linhas, em faixas
dataforge test --minimo=80              # reprova abaixo disso (saída 1)
dataforge crucible --cobertura
```

```
  src/main.df         ░░░░░░░░░░░░░░░░░░░░   0.0%  0/94
                      sem teste: montar_cli, mostrar, principal
  src/repositorio.df  ████████████████████ 100.0%  38/38
  src/tarefa.df       ████████████████████ 100.0%  14/14

  total  35.6%  52 de 146 linhas executáveis
```

`--minimo` aceita `80`, `80%` e `0.8`. A fronteira é em 1 **inclusive**:
`--minimo=1` é um por cento, porque ninguém exige cobertura total
digitando `1`.

## O que faz o número significar algo

Os dois lados da fração têm um jeito próprio de mentir:

| Metade | De onde vem | Como mentiria |
|---|---|---|
| denominador | o parser: quais linhas são **executáveis** | contar comentário e linha vazia dá um número sempre pessimista, que ninguém olha duas vezes |
| numerador | a execução, instrumentada | com a compilação de corpos ligada, toda ação daria 0% |

E duas escolhas que mudam o que se lê:

**A linha do `action` não conta; o corpo conta.** Assim uma ação nunca
chamada aparece com **0%**, e não com 20%.

**Um arquivo que nenhum teste toca aparece com 0%**, em vez de sumir do
relatório. Sumir é o que faz uma cobertura de 95% conviver com metade do
sistema sem teste.

## A informação que resolve

`58% coberto` não diz o que fazer. `sem teste: nunca_chamada` diz.

Por isso o relatório lista, para cada arquivo, **os nomes das ações**
cujo corpo nunca rodou — e com `--linhas`, as linhas em faixas
(`3-5, 9, 11-12`), porque uma lista de setenta números é ilegível.

## O que ela NÃO mede

É de **linha**, e não de ramo: `given a and b` conta como coberta mesmo
que `b` nunca tenha sido avaliado. Medir ramo exigiria instrumentar a
avaliação de expressão, o que dobraria o custo — e cobertura de linha já
responde a pergunta que importa, que é "existe código que ninguém
testou".

## Uma advertência

Cobertura alta não é qualidade. Um teste que chama tudo e não verifica
nada dá 100%. O número serve para achar o que está a **zero**, e é aí
que ele vale quase tudo o que custa.
