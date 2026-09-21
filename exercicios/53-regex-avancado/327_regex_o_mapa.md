# 327 — o mapa, e o que ele não faz

Fechar o módulo dizendo onde cada peça serve, e sendo explícito sobre
os limites. Uma ferramenta que não nomeia o que **não** faz é usada onde
não deve.

## As quatro perguntas

"casa?", "casa inteiro?", "o que casou?" e "todos os que casaram?" —
e uma função para cada.

## O que o módulo NÃO faz

Não valida documento (`is_cpf` é formato), não interrompe uma busca em
andamento, `risk` é forma e não prova, e não casa estrutura aninhada.

## E quando NÃO usar regex

Procurar um texto literal não precisa dela — e com ela o ponto do
`ana.souza` vira "qualquer caractere". `in` para literal; regex para
**forma**.
