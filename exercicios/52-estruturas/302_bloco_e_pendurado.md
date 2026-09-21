# 302 — o ponteiro que não aponta para nada

Há duas formas de um ponteiro não valer nada, e elas são diferentes.

## O NULO tem endereço zero

Lê-lo seria a falha de segmentação clássica. E ele não é o `void` da
linguagem: `NullReferenceError` fala de um `void`; aqui o endereço
existe.

## O PENDURADO aponta para um bloco liberado

O endereço continua na mão de alguém, e o espaço pode já ser de outra
pessoa.

## `liberar` é idempotente

Um `liberar` no `defer` e no caminho de erro não pode virar erro: a
disciplina atrapalharia em vez de ajudar.

## E o ponteiro SEGURA o bloco

Com referência fraca, `Est.ponteiro(Est.bloco(8), "u32")` nasceria
pendurado — o bloco temporário morreria assim que a chamada voltasse.
Um ponteiro cuja validade depende de a expressão ter sido guardada numa
variável é uma armadilha.
