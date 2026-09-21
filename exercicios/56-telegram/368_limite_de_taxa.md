# 368 — o 429 que vem no CORPO

O Telegram responde 429 com `retry_after` **no corpo** da resposta, e
não num cabeçalho. Quem escreve o cliente à mão trata 429 como "erro" e
desiste — e o bot para de responder num horário de pico, sem nada no log
dizendo por quê.

## O limitador segura, e não descarta

Um limitador que joga fora a mensagem excedente é pior que nenhum: o
usuário não recebe, e o bot acha que mandou.

## O recuo com tremor

Sem ele, todos os clientes que tomaram 429 juntos voltam juntos.

## E o módulo não pode inventar idempotência

Se a mensagem já saiu e o 429 veio depois, reenviar manda duas. A
retentativa vale para **leitura**, e não para escrita cega.
