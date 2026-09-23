# 391 — o relé que não bate

Uma leitura pura treme: 512, 509, 514, 511. Num gráfico isso é grama;
num controle, é o relé chaveando dezenas de vezes por minuto — e é assim
que um contato se queima.

## Média móvel: a resposta mais barata

Ela **esquece**: numa janela de 3, a quarta leitura empurra a primeira
para fora. Janela grande suaviza mais e responde mais devagar; é uma
troca, e não uma melhoria.

## Histerese: duas soleiras, não uma

Ligar acima de 30 e desligar abaixo de 30 faz o relé chavear a cada
tremor quando a temperatura fica **em** 30. Medido no exercício: as
mesmas seis leituras dão **5 chaveamentos** com uma soleira e **1** com
duas.

No meio da faixa ela **segura o estado** — e é isso que a torna um
controle, e não um comparador.

## Invertendo, ela liga abaixo

`IoT.histerese(40, 50)` liga abaixo de 40 e só desliga em 50: é o
umidificador, o aquecedor, a bomba. Duas soleiras iguais são recusadas,
porque isso é uma soleira só com outro nome.
