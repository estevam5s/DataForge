# 390 — do número cru ao valor

Um pino analógico devolve 0 a 1023. Ele não é temperatura, nem luz: é o
quanto da tensão de referência chegou ali. Transformar isso em grandeza
é a parte que todo projeto refaz — e onde os mesmos erros acontecem.

## `escala` limita por padrão

O `map()` do Arduino **não** limita, e ruído faz um ADC de 10 bits
devolver 1024 de vez em quando: no painel isso vira 101%, e num controle
de motor vira um valor fora da faixa do PWM. Aqui o padrão é limitar, e
`limitar := no` é escolha explícita de quem quer extrapolar.

## A tensão depende da placa

| Placa | Bits | Referência |
|---|---|---|
| UNO, Nano, Mega | 10 (0–1023) | 5 V |
| ESP32 | 12 (0–4095) | 3,3 V |

A mesma leitura nas duas é uma tensão diferente — e ligar um sensor de
5 V direto num ESP32 costuma matar o pino.

## A ponta da escala não é temperatura

Com a leitura em 0 ou 1023, a equação do termistor divide por zero ou
tira log de zero, e o que sai é um número absurdo **com cara de
temperatura**. Um termostato que vê −273 °C liga o aquecedor e não
desliga mais. Por isso `ntc` recusa as pontas: ali não é frio nem calor,
é fio solto ou curto.
