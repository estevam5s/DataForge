# 345 — o objeto que se comporta como coleção

`__len__`, `__getitem__`, `__setitem__`, `__contains__` e `__iter__`
são o que fazem `len(x)`, `x[0]`, `k in x` e `cycle i in x` funcionarem
**sem que nenhum deles saiba o que é o seu tipo**.

## É o mesmo protocolo da ponte para o Python

Um `ndarray` continua um `ndarray` porque o interpretador trata objeto
estranho por protocolo, e não por tipo.

## A compreensão e o pipeline também

`[i["preco"] cycle i in c]` e `c >> morph … >> distill …` — nenhum dos
dois sabe o que é um carrinho.

## E trocar protocolo por `isinstance` quebraria tudo junto

O quadro, a tupla e a ponte entram pela mesma porta.
