# 389 — o erro número 1 do Firmata

A placa **não responde perguntas** sobre o analógico: ela envia sozinha,
de tempos em tempos, os canais que você mandou relatar. Sem
`relatar_analogico(canal)`, o pino está certo, o sensor está certo, e a
leitura é **zero** — sem nenhum erro.

É o defeito que mais custa tempo a quem começa, porque não há nada para
depurar: o programa está correto do ponto de vista de qualquer leitura.

## A amostragem é uma troca

| Muito baixa | Muito alta |
|---|---|
| enche a serial e **atrasa as ordens que você manda** | o gráfico perde detalhe |
| o LED demora a responder ao clique | um botão lido por relatório parece que "não pegou" |

Para temperatura, 500 ms é generoso. Para um potenciômetro que move um
servo, 20 ms.

## O digital é por mudança

Ele não vem periodicamente: a placa avisa quando o pino muda de estado.
`placa.observar(acao)` recebe esses eventos; `placa.ler(pino)` devolve o
**último** valor relatado, e não uma pergunta ao vivo.
