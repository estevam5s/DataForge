# 396 — quando o programa precisa rodar na placa

Firmata cobre o protótipo. O que precisa rodar **sem computador** — um
sensor a bateria, um controle com resposta em microssegundos — é sketch:
C++ na placa. A linguagem escreve o sketch, e o `arduino-cli` compila e
grava.

## O arquivo tem o nome da pasta

Um `.ino` solto não compila, e o erro do `arduino-cli` não diz por quê.
`gravar_sketch("/tmp/fw", "sensor")` cria `/tmp/fw/sensor/sensor.ino` —
a pasta e o arquivo com o mesmo nome, que é o que o Arduino exige.

## Uma opção que não existe é recusada

`opcoes.ler` de novo: um `--lde=7` que passasse calado gravaria o sketch
com o LED errado, e a pessoa iria procurar o defeito no fio.

## 57600, e não 9600

É a velocidade do `StandardFirmata`. Um sketch de Firmata com
`Serial.begin(9600)` compila, grava, e **não conversa** com ninguém.

## O que a linguagem não faz

`IoT.compilar` e `IoT.carregar` chamam o `arduino-cli`. Compilar C++ para
AVR, resolver bibliotecas e falar com o bootloader é o que ele faz, e
bem; reimplementar isso seria refazer o GCC e o avrdude. O projeto
prefere dizer que depende dele a fingir que não.
