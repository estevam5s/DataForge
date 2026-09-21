# 287 — sinal é valor; observável é fluxo

Um clique é fluxo — perguntar *"qual o valor do clique agora?"* não
tem resposta. Um saldo é valor. Frameworks que chamam os dois de
"stream" fazem a pergunta *"qual é o valor atual?"* deixar de ter
resposta.

## Quem se inscreve recebe o que vier daqui para a frente

O que foi emitido antes não volta. É a definição de fluxo.

## Os operadores têm os nomes do pipeline

`morph`, `sift`, `distill` — os mesmos do `>>` da linguagem, e não um
segundo vocabulário.

## O fluxo vira valor quando a pergunta muda

`para_sinal` é a ponte: a partir dali, "qual é o último?" tem
resposta.

## E encerrar é definitivo

Emitir depois disso levanta. Devolver `no` calado fazia o valor sumir
sem nada no log.
