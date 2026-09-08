# Exercício 215 — A estrutura certa

## Enunciado

Escolha entre cluster e vault pela operação que você faz.

## Conceitos

Escolher a estrutura costuma render mais que otimizar o algoritmo. A tabela que
decide cabe em três linhas:

| Você quer | Use | Custo |
|-----------|-----|-------|
| procurar por posição | `Cluster` | O(1) |
| procurar por chave | `Vault` | O(1) |
| procurar por valor | `Cluster` | **O(n)** |

É na terceira linha que se perde.

## O que observar

**O vault é a estrutura mais subutilizada da linguagem.** Quase todo O(n²)
acidental some ao trocar uma busca linear por uma consulta de vault.

**`tally` e `group_by` fazem uma passada.** Contar ocorrências com
`xs.count(x)` dentro de um laço é O(n²) para um problema O(n).

**`pop(0)` desloca todos os outros.** Num laço, isso vira O(n²). Para uma fila,
inverta a lista e use `pop()`, que é O(1).

## Armadilhas

- Construir o índice custa O(n) e ocupa O(n) de memória. Para **uma** consulta,
  a busca linear é mais barata; a partir da segunda, o índice ganha.
- Chave de vault precisa ser imutável: texto, número ou record. Um cluster como
  chave é recusado — ele mudaria depois de guardado, e a busca deixaria de
  encontrá-lo.

## Relacionados

- [213 — Medir o crescimento](213_medir_o_crescimento.md)
- [Custo das estruturas](https://dataforge-lang.vercel.app/docs/big-o/estruturas)
