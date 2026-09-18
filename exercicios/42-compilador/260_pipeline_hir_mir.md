# 260 — dentro do compilador: HIR, MIR e o que o fluxo prova

A linguagem já tinha lexer, parser, AST, analisador estático e um
compilador de fechamentos. O que faltava era **ver** as representações do
meio: `dataforge tokens` mostrava a primeira fase, `dataforge ast` a
terceira, e as outras quatro não apareciam em lugar nenhum.

```
texto → lexer → AST → HIR → typechecker → MIR → LIR → executa
```

`dataforge ir <arquivo> --fase=…` mostra cada uma, e
`Arcane.Compilador` as entrega como **dado** — o que permite a um plugin
do `check` perguntar coisas de **fluxo**, e não só de forma.

## HIR: o açúcar, e o que só parece

Cinco formas de escrita são abertas: a corrente de `orif` vira `given`
aninhado, `x += 1` vira `x := x + 1` **quando o alvo é um nome**,
`x not in xs` vira `not (x in xs)`, `perform` vira o laço com a primeira
volta garantida, e `-5` vira o literal `-5` em vez de uma operação sobre
`5`.

**A prova não é a forma da árvore: é a saída.** Um desaçucaramento errado
não levanta erro — ele muda o resultado. Por isso a garantia é medida
rodando exercícios do repositório nas duas formas e comparando
caractere por caractere.

A outra lista vale mais: oito formas que **parecem** açúcar e não são,
com o motivo ao lado. `cycle i from 0 to 3` não vira `cycle i in
range(0, 4)` porque `range` **materializa** a lista, e um laço de um
milhão de voltas criaria uma lista de um milhão de itens. `a ?? b` não
vira ternário porque avaliaria `a` duas vezes. `mark @f` não vira
`g := f(g)` porque um decorador que devolve `void` **não** substitui o
alvo — e é isso que deixa `@Rota("/x")` só anotar.

## MIR: o grafo, e por que cada decisão

A árvore diz o que o programa **é**; o grafo diz por onde ele **passa**.
Um corpo por ação, mais `(programa)` no topo, cada um com blocos básicos
e arestas rotuladas: `sim`, `nao`, `volta`, `halt`, `skip`, `erro`,
`point`, `default`, `defer`.

Três decisões:

1. **O MIR sai do HIR**, e é isso que paga a normalização: sem ela,
   `orif` e `perform` seriam dois casos a mais no construtor de grafo —
   e um caso esquecido ali não dá erro, produz análise errada com cara
   de verdade.
2. **A aresta de erro sai da ENTRADA do `monitor`**, não de cada
   instrução. O `handle` vê o estado de **antes** do corpo, que é o pior
   caso honesto; uma aresta por instrução daria o mesmo resultado com um
   grafo três vezes maior.
3. **O que roda fora da ordem é opaco.** `thread`, `parallel`, `server`
   entram como **uma** instrução: abrir o corpo deles num grafo
   sequencial afirmaria uma ordem que não existe.

## O aviso que o check não sabia dar

```dataforge
given n bigger 10:
    rotulo := "alto"
yield rotulo          // e quando a condicao e falsa?
```

O analisador **registra** o nome do ramo, e isso está certo: um `given`
compartilha o escopo, e é assim que se decide um valor em dois caminhos.
O que faltava era contar por **quantos** caminhos ele passa — e essa
pergunta só o grafo responde (`talvez-nao-definida`).

O laço conta como ramo pelo mesmo motivo: ele pode não rodar nenhuma vez.

**Cada silêncio é um falso alarme que não acontece.** Ela cala quando o
corpo tem `monitor` (o `handle` lê o que o corpo talvez não tenha
atribuído, e isso é o uso normal), quando tem `defer`, quando há
fechamento ou bloco opaco, e — o que só apareceu **medindo** — quando o
nome existe **fora**: `:=` dentro de uma ação escreve o nome externo
quando ele existe. Sem essa última regra, os nove contadores por
fechamento do repositório seriam todos acusados.

## Constante, e escapatória

A propagação de constante usa **interseção**: um nome que dois ramos
escrevem com valores diferentes sai da tabela. É isso que a separa de
uma varredura de texto.

A escapatória responde "o que mais alguém pode estar lendo?" com quatro
motivos: `devolvido`, `fechamento`, `concorrente`, `guardado`. Numa
linguagem compilada ela decide o que vive na pilha; aqui o coletor do
Python continua respondendo pela memória, mas a pergunta segue prática —
um nome que escapa para uma `thread` é a metade de todo bug de
concorrência.

## LIR: o backend que existe

Não há código de máquina, e o módulo não finge. O backend do DataForge é
`compilador.py`: a árvore vira fechamentos Python, uma vez. E essa
descida é **parcial** — o que não está nas tabelas recua para o
interpretador de árvore, e continua correto, só não fica mais rápido.

O que não existia em lugar nenhum era saber **o que** recuou. O inventário
diz, por classe de nó, e separa os recuos que acontecem **dentro de um
laço** — os únicos em que a diferença aparece num perfil.

A conta sai das tabelas do próprio `compilador.py`, e não de uma lista à
parte: uma segunda lista divergiria no primeiro nó novo, e o relatório
passaria a mentir com confiança.

## O que NÃO existe

- **LLVM, registradores, linker**: não é lacuna, é o que a escolha de ser
  interpretado significa. O teto da técnica já está medido em ~6,5×.
- **Otimização sobre o MIR**: ele é para **analisar**, não para
  reescrever.
- **Tempo de vida nomeado** (`'a`): o coletor responde pela memória, e um
  `'a` sem nada para provar seria cerimônia.
- **Pratt parser**: a precedência é a cascata de funções. Pratt paga
  quando a tabela de operadores é dinâmica, e aqui ela é fixa.
- **Recuperação de erro dentro de um arquivo**: o primeiro erro de
  sintaxe encerra a leitura daquele arquivo (entre arquivos o `check`
  continua).
- **Prova formal** (SMT, refinamento provado): há contrato cobrado em
  execução e `--plugin=` para acoplar regra própria, e é onde isso para.
