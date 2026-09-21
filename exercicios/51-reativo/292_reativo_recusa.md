# 292 — o que o grafo reativo recusa

Três recusas, e cada uma evita um defeito que não levantaria erro
nenhum — ele só entregaria o valor errado.

## Um derivado que depende de si mesmo

A mensagem traz a **cadeia inteira**: dizer só "há um ciclo" manda
procurar em toda a fórmula, e o ciclo mais curto é o mais fácil de
quebrar.

## Um derivado não pode escrever

A fórmula é lida para descobrir de **que** ela depende. Escrever de
dentro dela faz a propagação correr no meio da própria descoberta: o
grafo muda enquanto está sendo percorrido.

## Mas um EFEITO pode

Ele não tem valor a produzir, e a escrita dele abre a **próxima** onda
— e não reentra na que está correndo.
