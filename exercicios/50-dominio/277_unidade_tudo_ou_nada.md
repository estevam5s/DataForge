# 277 — todas as invariantes antes de qualquer gravação

Se a segunda gravação falhasse por invariante, a primeira já estaria no
banco — e a transação de domínio teria vazado pela metade. A ordem das
duas fases é o recurso.

## As duas pontas de uma transferência

Origem e destino confirmam juntas, ou nenhuma das duas.

## A unidade que terminou não recebe mais

Nem registra, nem confirma de novo. Um objeto que aceita operações
depois de terminado é um objeto sem estado.

## E `eventos_pendentes` mostra sem publicar

Para quem quer conferir antes de confirmar — e sem tirar os eventos do
agregado.
