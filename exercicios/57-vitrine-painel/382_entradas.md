# 382 — os campos, e o que `mudou` responde

Toda entrada devolve o valor de agora. O que faltava era saber se ele
**mudou** nesta execução — sem isso, uma consulta cara roda a cada
redesenho, mesmo quando nada relevante mexeu.

## Ele pergunta pela CHAVE, e não pelo rótulo

O rótulo é o que a pessoa lê, e pode mudar com a tradução.

## É o `on_change` deste framework

E é uma **pergunta** em vez de um retorno de chamada: o programa roda
inteiro a cada interação, então a linha que reage à mudança pode estar
onde ela é lida.

## E a chave separa dois campos com o mesmo rótulo

Sem ela, os dois dividiriam o mesmo estado — e um sobrescreveria o
outro, calado.
