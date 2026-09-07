# Exercicio 199 — Relatório com várias abas e fórmulas

## Enunciado

Monte um relatório com fórmulas que o Excel calcula ao abrir.

## Conceitos

```dataforge
Xls.formula(aba, "D5", "SUM(D2:D4)")
Xls.bold_row(aba, 4)
Xls.freeze(aba, "A2")
```

| Função | Faz |
|--------|-----|
| `Xls.formula(aba, ref, expr)` | grava uma fórmula |
| `Xls.get_formula(aba, ref)` | lê de volta, ou `void` |
| `Xls.formulas(aba)` | todas, por endereço |
| `Xls.bold_row` / `freeze` / `width` / `autofit` | formatação |

## O que observar

**Fórmula não é calculada aqui.** Ela é gravada no arquivo, e o Excel a resolve
ao abrir. É o que se quer num relatório: quem receber pode mexer nos números e
ver o total mudar sozinho. Um valor calculado em DataForge seria um número morto.

**Por isso a coluna de fórmulas volta vazia na leitura.** `Xls.rows` mostra
`void` onde há fórmula sem valor gravado — não há bug ali.

**O `=` inicial é opcional.** `"=SUM(A1:A9)"` e `"SUM(A1:A9)"` gravam a mesma
coisa.

## Erros comuns

- Escrever a fórmula como texto com `Xls.set`. Vira uma célula de texto que
  mostra `=SUM(...)` em vez de calcular.
- Contar as linhas errado. `D5` é a quinta linha; em `Xls.cell(aba, 4, 3)` os
  índices começam em zero.
