# 347 — o objeto que se chama, e o que se abre

`__call__` faz um objeto virar ação — útil quando ele tem **estado**
entre chamadas.

## Por que isso não é só uma closure

O estado fica visível e nomeado: `dobro.total` e `dobro.passo` podem
ser lidos, testados e serializados. Uma closure esconde os dois.

## E ele passa onde uma ação passa

Numa compreensão, num argumento — o protocolo é o mesmo.

## O bloco com entrada e saída

Não há `with` em DataForge: quem garante a saída é o `defer`, e ele
roda em **todos** os caminhos.
