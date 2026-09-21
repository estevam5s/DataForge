# 354 — o que não se usa não pode custar

Contratos, sobrecarga, invariantes, metaclasses e `lazy` não podem
custar nada a quem não os usa. A prova não é uma afirmação: é medir.

## A propriedade CHAMA uma ação por leitura

Ela não pode empatar com o acesso a campo — e o que se cobra é um
**fator** com folga, porque `assert a bigger b` entre dois números
medidos é um sorteio.

## A invariante ACUSA, e não DESFAZ

O objeto fica no estado inválido, e quem trata decide o que fazer com
ele. Quem precisa do desfazer usa um agregado.

## E o atalho mora no blueprint

`leitura_simples` e `escrita_simples` dizem que não há propriedade,
descritor nem gancho. Quem acrescenta um jeito novo de interceptar
acesso precisa derrubá-lo — senão o recurso novo não roda para os
blueprints "simples", e nada avisa.
