# 249 — Portas, adaptadores e o contêiner

## O que se pratica

`contract` como porta, blueprint `with` como adaptador, `Arcane.Injecao`
com `unico`, `transitorio`, `por_escopo`, `conferir` e `grafo`.

## O que este exercício ensina que não é óbvio

**1. O caso de uso não adota nada de fora.** `Cadastro` conhece dois
contratos e zero implementações. Trocar SQLite por PostgreSQL, ou SMTP
por uma fila, não muda uma linha dele — é a arquitetura hexagonal, e é o
Princípio da Inversão de Dependência escrito em tipos.

**2. O contêiner lê o que já estava escrito.** `usuarios: Usuarios` no
cabeçalho é a dependência declarada; não há anotação `@Inject` nova. O
contêiner resolve pelo tipo.

**3. A composição mora num lugar só.** As quatro linhas de registro são
o único ponto do programa que sabe quais adaptadores existem. No teste,
são essas quatro linhas que mudam — e só elas.

**4. `conferir()` no teste pega o registro que falta.** Um contêiner que
só descobre a dependência sem registro quando a rota é chamada descobre
em produção.

**5. Por escopo é por pedido.** Uma transação por pedido HTTP, fechada no
fim. Pedir uma dependência `por_escopo` ao contêiner raiz é recusado: ali
ela viraria um único calado, e duas requisições dividiriam a transação.

## Para ir além

- Registre `Usuarios` como `por_escopo` e `Cadastro` como `unico`, e leia
  a mensagem sobre dependência cativa.
