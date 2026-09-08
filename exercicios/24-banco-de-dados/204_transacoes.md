# Exercício 204 — Transações

## Enunciado

Transfira saldo entre contas, e garanta que não suma dinheiro.

## Conceitos

Uma transferência são duas escritas: tirar de uma conta, pôr na outra. Se a
segunda falhar depois da primeira, o dinheiro desaparece.

A transação garante que as duas aconteçam, ou nenhuma:

```dataforge
Forge.transacao(db, lambda c => transferir(c, 1, 2, 30.0))
```

Se o corpo falhar, tudo é desfeito.

## O que observar

**Use a forma com bloco.** `comecar()` com um `confirmar()` esquecido segura
locks até a conexão cair — é o motivo mais comum de um banco travar em
produção. `Forge.transacao` confirma no fim e desfaz na falha, sempre.

**`incrementar` soma no banco.** Ler, somar e gravar perde atualizações quando
duas conexões fazem isso ao mesmo tempo:

```
conexão A lê 100    conexão B lê 100
A soma 10 → 110     B soma 20 → 120
A grava 110         B grava 120     ← os 10 de A sumiram
```

`incrementar` manda `saldo = saldo + ?` para o banco, e o banco resolve.

## Armadilhas

- Uma transação aberta segura locks. Mantenha-as curtas: fazer uma chamada HTTP
  no meio de uma transação é o jeito mais fácil de travar um banco.
- Com `SERIALIZABLE`, prepare-se para `TransactionError` por falha de
  serialização — e para tentar de novo. É o preço da garantia.

## Relacionados

- [201 — Conectar e consultar](201_conectar.md)
- [208 — Pool de conexões](208_pool_e_conexoes.md)
