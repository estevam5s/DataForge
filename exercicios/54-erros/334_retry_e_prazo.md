# 334 — insistir, e saber quando parar

Uma falha de rede é diferente de uma falha de lógica. A primeira
costuma passar na segunda tentativa; a segunda passa a vida inteira
falhando — e insistir nela esconde o bug.

## O recuo com TREMOR

Sem *jitter*, todos os clientes que falharam juntos voltam juntos — e
o serviço cai de novo no mesmo instante.

## O que NÃO se repete

Um erro de lógica repete idêntico. Três tentativas, três vezes o mesmo
erro.

## E um prazo total, além do número de tentativas

Cinco tentativas de dez segundos são cinquenta segundos de espera para
quem está do outro lado.
