# 392 — o meio-termo que não existe

Um pino digital só tem dois valores. "Meio brilho" é o pino ligando e
desligando rápido o bastante para o olho — ou o motor — não notar. É o
PWM, de 0 a 255.

## O modo é declarado, nunca adivinhado

Declarar por conta própria seria conveniente e **errado**: um pino em
`saida` recebendo PWM acende no talo, e quem lê o programa não veria
onde o modo mudou. Por isso `pwm` e `servo` exigem o modo já declarado.

## Quem diz o que o pino faz é a placa

Num UNO, só 3, 5, 6, 9, 10 e 11 fazem PWM — e essa lista vem da
**resposta de capacidade** da placa, não de uma tabela escrita na
linguagem. Uma tabela envelheceria na primeira placa nova, e UNO, Mega e
ESP32 têm mapas diferentes.

## Servo é posição

`servo(3, 90)` não é "gire até 90"; é "fique em 90". E cada servo tem os
seus microssegundos de fim de curso: quando o braço treme numa ponta, é
`configurar_servo` que resolve.
