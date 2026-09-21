# 387 — o mapa, e as decisões

Fechar a trilha com o que a Vitrine resolve, o que ela **não** resolve,
e por que cada escolha foi feita. A última parte é a que evita usá-la
onde o Kiln é a resposta.

## O modelo, em uma frase

O programa inteiro roda de novo a cada interação, e o estado da sessão
sobrevive.

## As consequências diretas

Não há callback nem diffing — e não precisa haver. `V.cache` é
obrigatório. A ordem importa: trate a interação antes de desenhar. E o
botão é um **valor** verdadeiro uma vez, não um evento.

## O que ela não tem

WebSocket/SSE (o Kiln tem; aqui é por **pergunta**), `build`, `deploy`
e CDN.

## E quando usar o Kiln

Vitrine: painel, ferramenta interna, app de dados. Kiln: API, site
público, rota com contrato, WebSocket.
