# 393 — quem conhece a placa é a placa

Cada placa tem um mapa diferente: quantos pinos digitais, quais fazem
PWM, quantos canais analógicos, qual a tensão e quantos bits o conversor
tem. Escrever esse mapa na linguagem seria errar na primeira placa nova.

Com a placa ligada, quem responde é ela — pela **resposta de
capacidade** do Firmata, que o cliente pede logo depois de conectar.

## Três números que mudam com a placa

| | UNO, Nano, Mega | ESP32 |
|---|---|---|
| tensão | 5 V | **3,3 V** |
| conversor | 10 bits (0–1023) | **12 bits (0–4095)** |
| FQBN | `arduino:avr:uno` | `esp32:esp32:esp32` |

Ligar um sensor de 5 V direto num ESP32 costuma matar o pino — e a
leitura dele vai a 4095, não a 1023. Os dois erros aparecem como número
errado, não como falha.

## Duas mensagens diferentes

Um pino que **não existe** e um pino que **não faz aquilo** são erros
distintos, e a mensagem de cada um diz o que fazer: a primeira mostra a
faixa da placa, a segunda lista o que aquele pino aceita.
