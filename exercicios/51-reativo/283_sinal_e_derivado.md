# 283 — um valor que outros valores acompanham

A diferença entre *"me avise quando algo acontecer"* e *"este total é
sempre a soma daqueles três"*. Contar as vezes que a fórmula roda é o
único jeito de **provar** a preguiça e a memória.

## Ele só calcula quando alguém lê

Recalcular na escrita faria uma cadeia de dez derivados rodar dez
vezes por mudança, e a maioria deles nunca é lida.

## E o valor fica memorizado

Três leituras, uma conta. O contador é a prova; sem ele isso seria uma
afirmação.

## Escrever o mesmo valor não invalida

Senão a cadeia recalcularia por nada, e um efeito de rede dispararia
duas vezes pelo mesmo estado.

## E `.valor()` lê sem depender

É o `untracked` dos outros frameworks: sem ele, um derivado que lê um
contador de depuração passaria a recalcular a cada incremento dele.
