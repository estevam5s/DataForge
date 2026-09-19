# 261 — SSA, o nó φ, e a otimização que foi medida

A parte 8 de uma referência Deep Tech é sobre o backend do LLVM. É a
primeira em que a resposta honesta é em boa medida **não se aplica**: o
DataForge é interpretado, e não há código de máquina, target triple nem
passe em C++.

O que transfere é **teoria de compilador**, não de LLVM — e é o que este
exercício exercita.

## SSA: uma definição por nome

O [MIR](../../site/app/docs/compilador/mir) diz por onde o programa
passa. O que ele **não** diz é *qual* atribuição uma leitura vê.

SSA responde isso por construção: cada nome é numerado, cada versão tem
exatamente uma definição, e onde dois caminhos trazem versões diferentes
aparece um nó **φ** que diz de onde cada uma vem.

```
given c:                 bloco 1 [sim]      x₁ := 1
    x := 1               bloco 2 [nao]      x₂ := 2
otherwise:               bloco 3 [juncao]   x₃ := φ(1: x₁, 2: x₂)
    x := 2                                  out  le x₃
out x
```

**Dominar não é alcançar.** Alcançar é poder chegar; dominar é não haver
como chegar por outro lado. É essa diferença que decide onde um φ é
necessário: um ramo não domina a junção — dá para chegar lá pelo outro
ramo —, então a junção precisa de φ.

## Por que SSA paga: a propagação fica condicional

A propagação de constante sobre o MIR junta os ramos por **interseção**,
e por isso perde o que só um ramo decide. Ela está certa em perder.

Com SSA a análise pode ir além: ela **não avalia** o ramo cuja condição
prova falsa.

```dataforge
x := 1
given x bigger 5:        // provado falso: este ramo nao roda
    y := "nunca"
otherwise:
    y := "sempre"
out y                    // 'sempre' — e a propagacao sobre o MIR nao sabia
```

A junção passa a ter um predecessor vivo só, o φ tem uma fonte só, e o
valor **se conclui**. Há teste rodando as duas análises sobre o mesmo
programa: sem essa comparação, "mais forte" seria só uma afirmação.

Daí sai o diagnóstico `ramo-morto`. E daí saem também os dois silêncios
que **foram medidos**:

- **`persist yes:` com `halt` dentro** é o laço infinito legítimo, e todo
  `stream action` vive disso. A saída do laço fica "morta" no grafo e não
  há nada de errado. Sem essa exceção: 29 acusações no repositório, todas
  em generator infinito.
- **um `match` sobre valor constante** não diz qual `point` casa. Matar a
  saída dali seria afirmar que um dos padrões casa, e isso exigiria
  avaliar **padrão**, não valor.

## Os passes, e nada que possa falhar

Três passes: `dobra-de-constante`, `ramo-morto` e `inalcancavel`.

A regra que mais recusa é a segunda: **nada que possa falhar é dobrado**.
`1 / 0` dobrado moveria o erro para a **carga**, longe da linha que o
causa; `"a" + 1` mudaria a mensagem; `2 ** 1000000` montaria meio milhão
de dígitos no carregamento. Diante de qualquer dúvida, o passe não mexe.

## O número, e ele é desconfortável

A escolha do que compilar não foi intuição: saiu do inventário do LIR,
que conta, por classe de nó, o que recua para o interpretador de árvore —
e separa os recuos **dentro de laço**. Dez nós ganharam construtor no
compilador de fechamentos.

| Carga | Antes | Depois | Ganho |
|---|---|---|---|
| feita **dos nós que o inventário aponta** | 507 ms | 382 ms | **1,33×** |
| 59 exercícios **reais** do repositório | 1150 ms | 1143 ms | **1,01× — nada** |

E o motivo é instrutivo: o que recua é dominado por nós que rodam **uma
vez** (declaração, `adopt`, `assert` de topo). Os que rodam dentro de
laço são poucos por volta, e o trabalho da volta **já estava compilado**:
leitura de nome, conta binária, chamada, leitura por índice. Otimizar o
que sobra é otimizar 3% de 3%.

Por isso os passes ficam **desligados por padrão**. A conta honesta é a
informação — não a promessa de velocidade.

## O que NÃO existe, com o motivo

- **emitir LLVM IR**: emitir o texto é fácil; usá-lo exigiria `llc` ou
  `clang` instalado, e a linguagem passaria a **depender de um compilador
  C para rodar**.
- **`llvmlite` ou qualquer backend em pacote**: recusado por regra —
  `dataforge/` não tem dependência externa, e é isso que faz
  `pip install dataforge-lang` bastar.
- **inlining**: numa linguagem em que uma ação pode ser substituída em
  tempo de execução (`f := outra`, método sobrescrito na filha), embutir
  o corpo exigiria provar identidade. É a mesma conferência que a chamada
  de cauda faz **na hora**, em vez de assumir.
- **vetorização, análise de alias**: não há registrador SIMD nem ponteiro
  a desambiguar.
- **otimização sobre o MIR**: ele é para **analisar**, não para
  reescrever.
- **target triple, cross compiler, RISC-V, WebAssembly, bare-metal**: não
  há código de máquina a produzir para alvo nenhum. O que atravessa
  plataforma é o interpretador, e ele atravessa por ser Python — o
  release constrói nas quatro.
- **passes LLVM em C++**: não há IR para um passe transformar. O análogo
  honesto é `--plugin=`, escrito em DataForge, que agora vê o MIR e o SSA.

O teto da compilação para fechamentos está **medido**: 1,5× a 1,8×
conforme a carga, com teto de ~6,5× para a técnica — o mesmo de uma VM de
bytecode escrita em Python. Passar disso exige sair do Python, e aí não é
mais esta linguagem.
