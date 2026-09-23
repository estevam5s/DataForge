# 388 — a primeira placa

Acender um LED é o "olá mundo" do hardware. Aqui ele roda **sem placa**:
`IoT.conectar_simulada` põe do outro lado do cabo um simulador que fala
o mesmo Firmata, com o mapa de pinos de uma placa de verdade.

## Não é um dublê da API

O simulador recebe os **bytes** do protocolo e responde com os bytes que
a placa responderia. O parser, a máquina de estados e a partição em sete
bits são exercitados — que é onde os erros moram. Um dublê de
`escrever(pino, valor)` não provaria nada disso.

## `fechar` desliga as saídas

Um programa que termina deixando um relé ligado é o defeito mais caro
desta área: o resto do sistema continua, sem ninguém olhando. E `fechar`
é idempotente — chamá-lo num `defer` e de novo no fim não é erro.

## Para experimentar

Troque `"uno"` por `"mega"` e confira `info()["pinos"]`: são 70.
