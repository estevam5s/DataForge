# 312 — um formato completo, do zero ao disco

Molde, alinhamento, janela, ponteiro, arquivo e conferência de
integridade — o desenho de um índice de banco de dados simples.

## Conferir a integridade ANTES de confiar

Tamanho, magia, versão e soma. Um leitor que confia primeiro e
confere depois já leu lixo.

## Busca binária direto no bloco

As chaves estão em ordem: dá para bisseccionar sem materializar
nada.

## E o arquivo corrompido é RECUSADO

Um byte trocado no corpo muda a soma. Sem ela, a busca devolveria um
valor plausível — que é pior que falhar.
