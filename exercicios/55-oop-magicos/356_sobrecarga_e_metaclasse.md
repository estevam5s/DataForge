# 356 — despacho por forma, e a classe que nasce mudada

`overload` escolhe o método pelo **tipo** dos argumentos, e uma
metaclasse roda quando o blueprint é criado. Os dois existem para tirar
um `match` de dentro do código de negócio.

## Sem sobrecarga, isso seria um `match` no começo

Funciona — e cresce a cada forma nova, num lugar que não é a
declaração.

## A metaclasse substitui um registro à mão

Sem ela, cada comando novo exige lembrar de uma linha de registro em
outro arquivo — e a linha que se esquece é a do comando que ninguém
testa.

## E o cache é esquecido junto

`augment` e `Reflexo.definir_metodo` chamam `esquecer_caches()`, que
recalcula o atalho de acesso e os mágicos **das filhas** também.
