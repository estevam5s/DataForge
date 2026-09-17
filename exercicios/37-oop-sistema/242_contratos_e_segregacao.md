# 242 — Contratos pequenos, e quem depende de qual

## O que se pratica

Declarar `contract`, estender contratos, adotar com `with`, usar o
contrato como tipo de parâmetro, e ver as duas recusas da declaração.

## O que este exercício ensina que não é óbvio

**1. O contrato não tem corpo, e isso é o que o separa do trait.** Um
`trait` pode trazer implementação padrão; um `contract` só declara. A
diferença parece pequena até o dia em que um contrato "com um método
padrão só" arrasta uma dependência para todo mundo que o implementa.

**2. Segregar é depender do menor contrato que serve.** `exibir` recebe
uma `Leitura`, e não um `Armazem`. Um cache, um arquivo remoto ou um
dublê de teste servem ali sem implementar `salvar` e `apagar` — é o
Princípio da Segregação de Interface escrito no tipo do parâmetro.

**3. A assinatura é conferida, e não só o nome.** `salvar(id)` com o nome
certo e um argumento a menos quebra todo código escrito contra o
contrato. O nome certo é o que faria a quebra passar despercebida até a
primeira chamada — por isso a recusa é na **declaração**
(`SignatureMismatchError`), e o `check` acusa antes de rodar.

**4. Uma propriedade exigida aceita campo.** `get total() -> Integer`
é cumprido por um `get total()` ou por um campo `total`. Quem lê não sabe
a diferença, e não deveria saber.

## Para ir além

- Acrescente um `contract Buscavel extends Leitura` com `procurar(termo)`
  e veja o `check` cobrar a implementação.
- Troque `fonte: Leitura` por `fonte: Armazem` em `exibir` e responda:
  que blueprint de teste ficou mais caro de escrever?
