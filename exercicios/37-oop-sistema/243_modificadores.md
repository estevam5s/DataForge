# 243 — O que cada modificador promete

## O que se pratica

`readonly`, `static steady`, `private`, `protected`, `internal`,
`abstract`, `final` (em ação e em blueprint), `sealed` e `override` —
cada um com a recusa que o torna real.

## O que este exercício ensina que não é óbvio

**1. Um modificador que ninguém confere é um comentário.** Cada linha do
exercício termina num erro com nome próprio (`ReadOnlyFieldError`,
`FinalBlueprintError`, `OverrideTargetError`…), e é esse nome que um
`handle` pega. É a diferença entre uma convenção e uma regra.

**2. `readonly` é sobre o nascimento, não sobre o arquivo.** O `setup`
escreve `numero`; depois, ninguém escreve — nem um método da própria
conta. O `check` acusa um método comum que tente, antes de rodar.

**3. `internal` fala de ARQUIVO; `private` e `protected` falam de
LINHAGEM.** A auditoria é visível para todo o código deste arquivo, e
invisível para quem adota o arquivo. É a visibilidade de um módulo.

**4. `abstract sealed` fecha a família.** `Corrente` e `Poupanca` são as
únicas contas possíveis — outra só num `.df` diferente, que o `sealed`
recusa. `final` em `Poupanca` fecha ainda mais: nem aqui ela tem filhas.

**5. `override` pega o erro de digitação.** Sem ele, `tarifaa` seria um
método novo, a `tarifa` abstrata continuaria pendente, e a mensagem
falaria de método faltando — longe da causa. Com ele, a mensagem diz
"did you mean 'tarifa'?".

## Para ir além

- Rode `dataforge check` neste arquivo sem os `monitor`: cada recusa vira
  erro antes de rodar.
- Mova `Corrente` para outro arquivo e veja o `SealedBlueprintError`.
