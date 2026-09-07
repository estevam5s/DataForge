# Exercicio 198 — Gravar e ler uma planilha

## Enunciado

Transforme uma lista de vaults num `.xlsx` e leia de volta.

## Conceitos

Um `.xlsx` é um ZIP de arquivos XML. O `Arcane.Excel` escreve e lê esse formato
**sem nenhuma dependência externa** — o arquivo abre no Excel, no LibreOffice e
no Google Sheets, e é lido de volta por openpyxl e pandas.

```dataforge
adopt Arcane.Excel as Xls

Xls.quick("/tmp/vendas.xlsx", vendas, "Vendas")
livro := Xls.read("/tmp/vendas.xlsx")
```

| Função | Devolve |
|--------|---------|
| `Xls.rows(livro, aba)` | lista de listas, com `void` nos buracos |
| `Xls.records(livro, aba)` | lista de vaults, usando a linha de cabeçalho |
| `Xls.column(livro, aba, "qtd")` | uma coluna, pelo título ou pela letra |
| `Xls.dims(livro, aba)` | linhas, colunas e células ocupadas |

## O que observar

**Dados em vault viram tabela sozinhos.** O cabeçalho sai das chaves, em
negrito, com a primeira linha congelada e a largura ajustada ao conteúdo — sem
isso a planilha abre com colunas de `####`.

**Os tipos sobrevivem.** `12` volta inteiro, `89.9` volta real, `yes` volta
booleano, uma data volta data. Um número que chega como texto abre a planilha
com tudo alinhado à esquerda e nada soma.

**A planilha é esparsa.** Escrever em `Z100` não materializa 100 linhas vazias:
ficam duas células ocupadas, e o arquivo reflete isso.

**Título vence letra de coluna.** Numa planilha com uma coluna chamada `B`,
pedir `"B"` traz essa coluna — não a segunda.

## Erros comuns

- Esperar que `records` pule uma linha de totais. Para ele, é uma linha como
  qualquer outra.
- Usar `frame` como nome de variável. É palavra reservada; use outro nome.
