# 266 — o mapa que não pode mentir, e o princípio que se mede

As três últimas partes da referência Deep Tech são as de **síntese**: o
desenho do ecossistema, os dez princípios de design e a visão de
implementação.

São as três coisas que um projeto costuma escrever como prosa — e prosa
não roda, não reprova e envelhece calada. Este exercício mostra as três
feitas de outro jeito: **derivadas do código e conferidas contra ele**.

## 1. A conferência nas duas direções

`Arcane.Ecossistema.conferir()` cobra duas coisas, e a segunda é a que
importa:

| Direção | O que cobra | O que impede |
|---|---|---|
| `faltando` | todo caminho citado existe no disco | a peça foi renomeada e o mapa aponta para o nome antigo |
| `orfaos` | todo módulo do núcleo aparece em algum componente | um módulo novo nasce **fora** do mapa, e o inventário fica incompleto em silêncio |

**Foi a segunda que pegou o primeiro erro deste módulo.** O mapa citava
`dataforge/stdlib/arcane_concurrent.py` em dois componentes. O arquivo se
chama `arcane_paralelo.py` — só a *classe* se chama `ArcaneConcurrent`.
`conferir()` acusou os dois antes de o primeiro teste existir.

Sem essa direção, o mapa teria nascido mentindo em dois pontos, e ninguém
teria como saber.

## 2. As três marcas, e por que a terceira é a que vale

| Marca | Estado | Quer dizer |
|---|---|---|
| `[+]` | `existe` | a peça está aqui, com esse papel |
| `[~]` | `equivale` | há **outra** peça que responde a mesma pergunta, nomeada |
| `[-]` | `nao-existe` | não há, e o motivo está escrito |

A lista é fechada de propósito. Um quarto estado seria o lugar onde "mais
ou menos" se esconderia — e é exatamente o que não se quer num
inventário.

Sete componentes do desenho estão marcados `nao-existe`, e o exercício
cobra que **cada um tenha motivo escrito**. Um mapa que marca tudo como
pronto não é um mapa, é publicidade: quem o lê descobre a ausência ao
tentar, no pior momento, e depois de ter escolhido a linguagem por causa
dele.

## 3. A prova que roda

`Arcane.Principios` não repete o texto do princípio. Três das dez provas
executam o analisador ou o interpretador:

| Princípio | O que a prova faz | Mediu |
|---|---|---|
| `compile-time-first` | roda o `check` sobre quatro trechos com defeito conhecido | **4 de 4** antes de rodar |
| `custo-zero` | cria um blueprint sem contrato nem invariante e olha o que ele carrega | **3 de 3** sentinelas em `None` |
| `seguranca-por-padrao` | roda o `check` num `thread` que escreve de fora e olha a severidade | sai como `warning` |

E o veredito **não é dez de dez**: cinco cumpridos, quatro parciais, um
que não se aplica. Um relatório que aprovasse os dez seria a prova de que
ninguém o leu.

`custo-zero` é `nao-se-aplica` porque a frase do documento — *abstrações
devem compilar para código equivalente a implementações manuais* — não
tem como valer sem compilação nativa. Forçá-la a valer seria redefini-la
em silêncio. O que vale, e é cobrado, é outra leitura: **uma abstração
custa zero para quem não a usa.**

## 4. A tensão é o conteúdo

Um princípio isolado não informa nada. Todo mundo é a favor de segurança,
e todo mundo é a favor de velocidade.

O que informa é **onde dois princípios se contradizem e qual venceu** — e
essa decisão, nesta linguagem, está sempre num arquivo. O exercício cobra
que cada uma das nove tensões tenha **custo declarado** e **arquivo**.

Exemplo: segurança por padrão × verificação antes de rodar. A escrita
concorrente é **aviso**, não erro, porque um acumulador protegido por
mutex passa pelo mesmo caminho de um sem proteção — e recusá-lo proibiria
o uso correto. Custo aceito, escrito: um programa com bug de
concorrência passa pelo `check`.

## 5. A fase que não roda

`Arcane.Percurso` leva o arquivo por nove fases e mede cada uma. A
décima — `execucao` — é **nomeada, medida em zero e marcada como não
percorrida**.

Executar é o que o programa faz. Um arquivo de verdade abre soquete,
escreve em disco e manda e-mail: um comando cuja função é *mostrar as
fases* não pode ter efeito no mundo, e um que tivesse seria usado uma
vez.

E ela **fica no mapa**. Apagá-la faria o desenho parecer completo — a
mesma razão por que `Machine Code` continua no desenho do ecossistema,
marcado como ausente.

## A armadilha que inverteu a resposta

A primeira versão do percurso apontava a fase errada, **com confiança**:

| Arquivo de 12 tokens | Antes | Depois |
|---|---|---|
| fase mais cara | `lir`, com **93,8%** | `tipos`, com 27,2% |
| total | 7,266 ms | **0,526 ms** |
| trabalho real do `lir` | 0,05 ms | 0,064 ms |

A causa: `lir` importa `compilador` e abre um interpretador por dentro. A
primeira fase que toca um módulo paga o `import` dele, e o cronômetro
atribui esse custo a ela.

**Uma ferramenta que aponta a fase errada é pior que nenhuma**, porque a
pessoa vai otimizar o lugar que a ferramenta indicou. Hoje os imports
lentos acontecem antes de qualquer cronômetro, e há um comentário ao lado
da linha que os aquece — para que ninguém os remova por parecerem
inúteis.

## O que levar

- Um mapa escrito à mão mente sem avisar; um mapa **conferido** reprova.
- Nomear a ausência **com o motivo** vale mais que marcar tudo como
  pronto.
- Um princípio que não se aplica é informação, não um problema a
  esconder.
- A medida precisa ser honesta sobre o que ela é: uma vez, nesta máquina,
  para comparar as fases **entre si**. Para comparar mudanças, há
  `Arcane.Bench`.
