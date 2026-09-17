# 244 — De quem é o erro?

## O que se pratica

`expects`, `promises` com `before(…)` e `outcome`, e `invariant` —
e a família `ContractError`, que pega os três.

## O que este exercício ensina que não é óbvio

**1. A cláusula diz de quem é a culpa.** Um `assert` diz *que* algo deu
errado. `expects` diz que **quem chamou** errou; `promises` diz que **a
ação** errou; `invariant` diz que **a operação** deixou o objeto
inconsistente. Num sistema de duzentos arquivos, é a diferença entre
abrir o arquivo certo e abrir três.

**2. `promises` roda na saída, mesmo escrito no topo.** Ele é tirado do
corpo pelo parser e conferido quando a ação devolve. `before(expr)`
guarda o valor da entrada — sem ele, uma pós-condição não conseguiria
falar de *mudança*, só de estado final.

**3. A invariante é conferida quando a chamada mais de fora termina.**
Dentro de um método o objeto passa por estados intermediários — tirar de
um lugar e pôr em outro são duas escritas. Cobrar a invariante entre elas
recusaria todo método correto.

**4. `quantidade` é chamada dentro de `promises` e da invariante.** Uma
chamada de dentro do próprio objeto não dispara a conferência de novo:
ela é passo da operação, não operação.

## Para ir além

- Remova o `expects` de `sair` e veja o `sair(…, -1)` aparecer como
  **invariante** quebrada — o erro certo, mas agora culpando a operação
  em vez de quem chamou.
