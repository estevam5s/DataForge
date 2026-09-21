# 384 — redesenhar só um pedaço

O fragmento economiza o que vai pela **rede**, e não a execução: o
modelo continua sendo "roda tudo de novo".

## A ordem IMPORTA

Trate a interação **antes** de desenhar. Com o botão tratado depois, a
tela fica um passo atrás e o estado está certo — o defeito mais confuso
deste modelo, porque o número "quase" bate.

## A dúvida cai SEMPRE para a página inteira

Houve falha, mais de um campo mudou, ou o fragmento sumiu da árvore.
Responder a página inteira sem precisar custa desempenho; responder um
pedaço sem poder custa **correção**.

## E a atualização periódica é por PERGUNTA

`V.atualizar_a_cada(n)`: o navegador pergunta de novo. Não há
WebSocket nem SSE aqui — o Kiln tem, e a Vitrine não os usa.
