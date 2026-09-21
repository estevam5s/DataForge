# 319 — o padrão que trava o processo

`(a+)+$` contra trinta caracteres que não casam leva **anos**: o motor
tenta todas as formas de dividir a entrada entre os dois
quantificadores, e são 2ⁿ.

## Os quatro desenhos clássicos

Quantificador dentro de outro, repetição aberta dentro de outra,
alternância que casa a mesma coisa, classe repetida dentro de grupo
repetido.

## E o padrão comum NÃO é acusado

Um falso alarme aqui ensinaria a desligar a conferência inteira.

## A análise DIZ que é forma, e não prova

Prometer mais do que ela entrega é o defeito de uma ferramenta assim:
ela reconhece quatro desenhos e **cala no resto**.

## E `safe_search` recusa ANTES de rodar

Não há como interromper uma busca já começada: o motor do Python não
solta o GIL, então um prazo numa thread não para nada — ela só deixaria
de esperar enquanto o processo inteiro continua travado.
