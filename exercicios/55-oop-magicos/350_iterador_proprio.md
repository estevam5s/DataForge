# 350 — um iterador com estado

`__iter__` devolvendo uma lista é o caminho simples. `__next__` é o
caminho que não materializa nada — e a diferença aparece num milhão de
itens.

## `void` encerra

Não há `StopIteration` aqui: sinalizar o fim com um erro obrigaria a
linguagem a ter uma exceção que não é erro nenhum — e a confundir com um
`handle Error` de verdade.

## O generator faz o mesmo, sem blueprint

E é preguiçoso de verdade: um `stream action` infinito só termina
porque quem consome para.

## E a ORDEM importa

O pipeline converte a fonte em lista: canalizar um generator infinito
direto **trava** o programa. Recorta primeiro, canaliza depois.
