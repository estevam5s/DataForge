# 284 — a dependência é DESCOBERTA

Não há lista para escrever: o derivado roda, e todo sinal lido durante
a execução entra. Uma lista à mão envelhece na primeira condição nova
dentro da fórmula — e o sintoma é um valor que **para de atualizar**.

## O ramo tomado decide a dependência

Abaixo de 100 o frete lê o cupom, e mexer no cupom o invalida. Acima
de 100 a fórmula toma o outro ramo e não lê mais.

## As fontes que sumiram param de notificar

Sem isso, a fórmula acumularia as dependências dos **dois** ramos e
recalcularia por mudanças que ela nem lê mais.

## E voltando, a dependência volta

Ela é refeita a cada execução: não há estado antigo a limpar.
