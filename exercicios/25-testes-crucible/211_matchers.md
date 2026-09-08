# Exercício 211 — Os matchers

## Enunciado

Cobre valores de todas as formas, e leia o que a falha diz.

## Conceitos

São 59 matchers, em nove grupos: igualdade, verdade, tipos, números, texto,
coleções, erros, desempenho e saída. `dataforge crucible --matchers` lista
todos.

Duas formas, e as duas viram a mesma cobrança:

```dataforge
expect 2 + 2 is 4                 // curta
expect(2 + 2).to_be(4)            // encadeada
```

## O que observar

**Nunca `to_be` com float.** `0.1 + 0.2` não dá `0.3` em nenhuma linguagem com
IEEE 754. Cobrar igualdade exata de ponto flutuante é escrever um teste que
falha por motivo errado. `to_be_close_to` existe para isso.

**A mensagem mostra a diferença, não os dois valores.** Comparar dois vaults de
dez chaves lendo os dois inteiros não se faz — o Crucible aponta a chave que
difere.

**`nao()` inverte só o próximo.** Um estado invertido pendurado faria a segunda
cobrança da cadeia sair ao contrário.

**A família serve em `to_raise`.** `to_raise(RuntimeError)` aceita
`DivisionByZeroError`, como o `handle` da linguagem.

## Armadilhas

- `to_have_field` serve para vault, record e instância — o teste não deveria
  precisar saber qual dos três o valor é.
- `to_raise` precisa de uma **ação**, não de um valor: `expect(lambda => …)`.

## Relacionados

- [209 — A primeira suíte](209_primeira_suite.md)
