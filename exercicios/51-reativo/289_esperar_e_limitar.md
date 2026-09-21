# 289 — o tempo dentro do fluxo

`esperar` é o *debounce* — só emite quando o fluxo fica quieto;
`limitar` é o *throttle* — deixa passar no máximo um por intervalo.

## A diferença, em uma frase

`esperar` responde no **fim** da rajada; `limitar` responde no
**começo**.

## E os dois existem pelo mesmo motivo

Um campo de busca que consulta a cada tecla manda vinte consultas para
escrever "cafeteira".

## O teste espera por CONDIÇÃO

Um `sleep` fixo mede a máquina, e o mesmo exercício reprova numa
esteira carregada sem que nada tenha mudado no código.
