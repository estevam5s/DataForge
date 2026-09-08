# Exercício 202 — Construtor de consultas

## Enunciado

Monte consultas encadeando chamadas, sem escrever SQL.

## Conceitos

Escrever SQL à mão continua valendo. O construtor resolve três coisas que o SQL
à mão não resolve:

1. **Dialeto.** `?` no SQLite e MySQL, `$1` no PostgreSQL. A mesma consulta roda
   nos dois.
2. **Condição opcional.** Um filtro que só existe quando o usuário preencheu o
   campo — o código mais chato e mais propenso a erro que existe.
3. **Identificador citado.** Uma coluna chamada `order` quebraria a consulta.

```dataforge
Forge.de(db, "usuarios")
    .onde("idade", ">=", 18)
    .onde_em("cidade", ["Floripa", "Recife"])
    .ordenar("nome")
    .limite(20)
    .buscar()
```

## O que observar

**A lista vazia não gera `in ()`.** Isso é erro de sintaxe em quase todo banco.
`onde_em("x", [])` vira uma condição sempre falsa, que é o que a lista vazia
significa.

**A página 1 é a primeira.** Off-by-one em paginação é clássico: quem chama
pensa em "página 1", e o banco pensa em "pule 0".

**`quando` evita o `if` em volta da consulta.** Sem ele, um filtro opcional
vira concatenação de texto com `and` na hora certa.

## Armadilhas

- `paginar` faz **duas** consultas: uma para contar, outra para trazer. Se o
  total não importa, `.pagina(n, 20).buscar()` faz uma só.
- `.buscar()` traz tudo. Numa tabela grande sem `.limite()`, isso carrega a
  tabela inteira na memória.

## Relacionados

- [201 — Conectar e consultar](201_conectar.md)
- [203 — Injeção de SQL](203_injecao_de_sql.md)
