# 373 — o programa de cima para baixo que vira página

O modelo da Vitrine é o que dispensa callback e diffing: o programa
**inteiro** roda de novo a cada interação, e o estado da sessão
sobrevive.

## Digitar reexecuta o programa

Nenhum callback: o valor novo entra, e a página é montada de novo do
começo.

## E o estado da sessão sobrevive

É o que torna o modelo utilizável: sem ele, um contador voltaria a
zero a cada clique.

## O botão é verdadeiro UMA vez

Ele não é um callback: é um valor que vale `yes` na execução em que
foi clicado, e `no` em todas as outras — inclusive nas reexecuções por
outro motivo.

---

E é isso que torna `V.cache` obrigatório, e não opcional.
