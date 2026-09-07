# Exercicio 200 — Do banco para a planilha, passando pela análise

## Enunciado

Consulte o banco, analise os números e exporte a planilha.

## Conceitos

Este é o caminho completo de um trabalho de dados, e as três peças conversam:

```dataforge
registros := DB.query(banco, "SELECT * FROM vendas")
tabela    := An.from_records(registros)     // vira frame de análise
Xls.sheet(livro, "Vendas", registros)       // vira planilha
```

| Módulo | Para |
|--------|------|
| `Arcane.Database` | SQLite: consultas, migrações, transações, modelos |
| `Arcane.Analytics` | média, desvio, correlação, regressão, `describe` |
| `Arcane.Excel` | ler e gravar `.xlsx` |
| `Arcane.IO` | ler e gravar arquivos, CSV, JSON |

`Xls.to_frame(livro, aba)` faz o caminho inverso: planilha → frame.

## O que observar

**`describe` sobre um frame descreve cada coluna.** Sobre uma lista, descreve a
lista. Colunas de texto aparecem marcadas como `non-numeric` em vez de
zerarem o resultado inteiro — silenciosamente, que era o comportamento antigo.

**Booleano não é número aqui.** Em Python `True` vale 1; numa coluna de dados
isso é ruído, e `describe` os ignora.

**Correlação negativa forte** entre quantidade e preço (`-0,825` no exercício)
diz que o caro vende pouco. É o tipo de resposta que justifica o trabalho todo.

**A planilha é o entregável.** O banco é onde os dados moram, a análise responde
a pergunta, e a planilha é o que se manda para quem decide.

## Erros comuns

- Analisar a planilha em vez do banco. A planilha tem linha de total e
  cabeçalho; o banco tem só os dados.
- Esquecer `DB.close`. Com `:memory:` não faz diferença; com arquivo, faz.
