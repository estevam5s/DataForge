# 258 — comptime, macros, DSL e plugin do check

A linguagem já tinha decorador, metaclasse e `augment` — tudo em
**execução**. Esta é a outra metade: o que acontece **antes** de o
programa rodar, e o que permite gerar código a partir de dado.

## comptime: a conta feita uma vez

`comptime` roda na **carga**, antes da primeira linha do programa, numa
caixa sem E/S. O resultado vira constante.

Se ele pudesse fazer E/S, "tempo de compilação" seria só "mais cedo" —
por isso `out`, `adopt`, `thread` e `parallel` são recusados ali, com o
motivo na mensagem.

Três usos que pagam o recurso:

- **tabela de consulta** calculada uma vez;
- **constante derivada** (`2 ** 16`) escrita como conta, e não como
  número mágico;
- **validação estática**: um `assert` dentro de `comptime` é uma trava de
  build, e o `dataforge check` a executa (`comptime-falhou`).

## Macro: a árvore como dado

O decorador troca o **valor**; a macro troca o **corpo**.

`M.arvore(acao)` devolve um vault comum — que percorre com `cycle`, casa
com `match` e serializa em JSON, sem que nada disso conheça a classe do
nó. `M.citar(texto)` faz o caminho inverso, e é a mesma árvore do
arquivo: é isso que permite gerar código que **roda**.

`M.transformar` devolve uma árvore **nova**. Uma macro que mutasse o que
recebeu mudaria a ação de quem chamou.

### Higiene é explícita

Uma macro que gera um temporário chamado `temp` quebra quem já tinha um
`temp`. `M.nome_fresco` e `M.renomear` existem para isso — e são
explícitos, porque fazer higiene sozinho exigiria saber o que é "de
dentro", e essa decisão é de quem escreve a macro.

### Derivar

`mark @M.derivar("texto", "igualdade", "vault")` gera `__str__`, `__eq__`
e `para_vault()` **a partir dos campos que já existem**. É a macro
derivada, e roda na carga — não a cada chamada.

## DSL externa

`Arcane.Dsl` são combinadores: `texto`, `numero`, `nome`, `seq`, `ou`,
`muitos`, `opcional`, `separado_por`, `mapear`. `D.analisar` devolve um
`Resultado` — texto de fora falha o tempo todo, e obrigar `monitor` em
volta faria o caminho normal ser o do erro.

A falha diz **posição**, o que era esperado e o trecho em volta: "não deu
certo" não ajuda a consertar a linha 3 de um arquivo de configuração.

## Plugin do check

Um `.df` que exporta `verificar(arvore, arquivo)` e devolve achados com
`linha`, `coluna`, `codigo`, `mensagem`, `sugestao` e `severidade`. Rode
com `--plugin=regras.df`, ou declare em `forge.toml`:

```toml
[check]
plugins = ["regras.df"]
```

O código aparece na mensagem, e `// df: permitir <codigo>` silencia a
regra na linha — sem isso, quem discordasse de uma regra teria de
desligar o plugin inteiro.

Um plugin quebrado vira **diagnóstico**, e não traceback: quem roda o
`check` quer o relatório do código dele.
