// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "43 · Backend e otimização",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 43`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[261](#261-ssa-o-no-phi-e-a-otimizacao-que-foi-medida)", "**SSA, o no phi, e a otimizacao que foi MEDIDA**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "261 · SSA, o no phi, e a otimizacao que foi MEDIDA"},
  { code: `// A parte 8 de uma referencia Deep Tech e sobre backend LLVM. Aqui a
// resposta honesta e em boa medida "nao se aplica": o DataForge e
// interpretado, e nao ha codigo de maquina. O que transfere e teoria de
// compilador, nao de LLVM — e e o que este exercicio exercita.

adopt Arcane.Compilador as K

// ── as fases, agora oito ──
assert K.fases() is ["lexer", "parser", "hir", "mir", "analises",
    "ssa", "otimizado", "lir"]

// ── SSA: uma definicao por nome ──
diamante := "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n"
forma := K.ssa(diamante)[0]

// onde os dois caminhos se juntam aparece um phi, dizendo de onde vem
fis := [f cycle b in forma["blocos"] cycle f in b["fis"]]
assert len(fis) is 1
assert fis[0]["nome"] is "x"
assert len(fis[0]["fontes"]) is 2

// um nome com uma definicao so nao precisa de phi
assert K.ssa("x := 1\\nout x\\n")[0]["blocos"][0]["fis"] is []

// o laco tem phi na cabeca: o nome volta pela aresta de tras
comLaco := K.ssa("t := 0\\ncycle i in [1, 2]:\\n    t := t + i\\nout t\\n")[0]
cabeca := [b cycle b in comLaco["blocos"] given b["rotulo"] is "condicao"][0]
assert len([f cycle f in cabeca["fis"] given f["nome"] is "t"]) is 1

// cada leitura diz QUAL versao esta lendo — e e essa a pergunta que o
// MIR sozinho nao responde
sequencia := K.ssa("x := 1\\nx := 2\\nout x\\n")[0]
escritas := [i["escreve"]["versao"] cycle b in sequencia["blocos"]
    cycle i in b["instrucoes"] given i["escreve"] isnt void]
lidas := [i["le"]["x"] cycle b in sequencia["blocos"]
    cycle i in b["instrucoes"] given "x" in i["le"]]
assert escritas is [1, 2]
assert lidas is [2]  // o 'out' le a segunda

// ── por que SSA paga: a propagacao fica CONDICIONAL ──
morto := "x := 1\\n" +
"given x bigger 5:\\n" +
'    y := "nunca"\\n' +
"otherwise:\\n" +
'    y := "sempre"\\n' +
"out y\\n"

// o ramo que nunca roda e nomeado, com o bloco e o rotulo
mortos := K.ramos_mortos(morto)
assert len(mortos) is 1
assert mortos[0]["rotulo"] is "sim"

// e por isso o valor de 'y' SE CONCLUI: a juncao tem um caminho vivo so
assert "sempre" in values(K.provadas(morto, "(programa)"))

// uma condicao que nao se prova nao mata nada — e esse e o caso de
// quase todo codigo, e o silencio certo
assert K.ramos_mortos("given entrada:\\n    y := 1\\notherwise:\\n    y := 2\\n") is []

// 'persist yes:' com 'halt' e o laco infinito legitimo: a saida fica
// "morta" no grafo e nao ha nada de errado nisso
infinito := "n := 0\\npersist yes:\\n    n += 1\\n    given n bigger 2:\\n        halt\\n"
assert len([m cycle m in K.ramos_mortos(infinito) given m["rotulo"] is "corpo"]) is 0

// ── os passes de otimizacao ──
assert len(keys(K.passes())) is 3
assert "ramo-morto" in K.passes()
assert "inalcancavel" in K.passes()

// duas dobras: '3 * 4' vira 12, e depois '2 + 12' vira 14
assert K.otimizar("x := 2 + 3 * 4\\n")["dobra-de-constante"] is 2
assert K.otimizar(morto)["ramo-morto"] bigger 0

// o que vem depois de um 'yield' sai do corpo
depois_do_yield := 'action f():\\n    yield 1\\n    out "nunca"\\n'
assert K.otimizar(depois_do_yield)["inalcancavel"] bigger 0

// ── nada que possa falhar e dobrado ──
// '1 / 0' dobrado moveria o erro para a CARGA, longe da linha que o
// causa. Sem dobrar, ele estoura onde esta escrito:
monitor:
    _x := 1 / 0  // df: permitir division-by-zero
    assert no
handle Error as e:
    assert e.type is "DivisionByZeroError"
    assert e.line is 84

// e texto com numero nao dobra: mudaria a mensagem de erro
assert K.otimizar('x := "a" + 1\\n')["dobra-de-constante"] is 0

// ── LIR: o que o backend REALMENTE compila ──
// Nao ha codigo de maquina. O backend e compilador.py, e a descida dele
// e PARCIAL: o que nao esta nas tabelas recua para a arvore.
inventario := K.lir(morto)
assert inventario["total"] is inventario["compiladas"] + inventario["recuadas"]
assert inventario["proporcao"] bigger 50

// ── a fase que nao existe, e que muita gente tenta primeiro ──
monitor:
    K.texto(morto, "llvm")
    assert no
handle RuntimeError as e:
    assert "llvm" in e.message
    assert "backend" in e.message

out "261 ok"`, lang: 'df', title: `exercicios/43-backend/261_ssa_e_otimizacao.df` },
  {"p": "A parte 8 de uma referência Deep Tech é sobre o backend do LLVM. É a primeira em que a resposta honesta é em boa medida **não se aplica**: o DataForge é interpretado, e não há código de máquina, target triple nem passe em C++."},
  {"p": "O que transfere é **teoria de compilador**, não de LLVM — e é o que este exercício exercita."},
  {"h3": "SSA: uma definição por nome"},
  {"p": "O [MIR](../../site/app/docs/compilador/mir) diz por onde o programa passa. O que ele **não** diz é *qual* atribuição uma leitura vê."},
  {"p": "SSA responde isso por construção: cada nome é numerado, cada versão tem exatamente uma definição, e onde dois caminhos trazem versões diferentes aparece um nó **φ** que diz de onde cada uma vem."},
  { code: `given c:                 bloco 1 [sim]      x₁ := 1
    x := 1               bloco 2 [nao]      x₂ := 2
otherwise:               bloco 3 [juncao]   x₃ := φ(1: x₁, 2: x₂)
    x := 2                                  out  le x₃
out x`, lang: 'text' },
  {"p": "**Dominar não é alcançar.** Alcançar é poder chegar; dominar é não haver como chegar por outro lado. É essa diferença que decide onde um φ é necessário: um ramo não domina a junção — dá para chegar lá pelo outro ramo —, então a junção precisa de φ."},
  {"h3": "Por que SSA paga: a propagação fica condicional"},
  {"p": "A propagação de constante sobre o MIR junta os ramos por **interseção**, e por isso perde o que só um ramo decide. Ela está certa em perder."},
  {"p": "Com SSA a análise pode ir além: ela **não avalia** o ramo cuja condição prova falsa."},
  { code: `x := 1
given x bigger 5:        // provado falso: este ramo nao roda
    y := "nunca"
otherwise:
    y := "sempre"
out y                    // 'sempre' — e a propagacao sobre o MIR nao sabia`, lang: 'df' },
  {"p": "A junção passa a ter um predecessor vivo só, o φ tem uma fonte só, e o valor **se conclui**. Há teste rodando as duas análises sobre o mesmo programa: sem essa comparação, \"mais forte\" seria só uma afirmação."},
  {"p": "Daí sai o diagnóstico `ramo-morto`. E daí saem também os dois silêncios que **foram medidos**:"},
  {"list": ["**`persist yes:` com `halt` dentro** é o laço infinito legítimo, e todo"]},
  {"p": "`stream action` vive disso. A saída do laço fica \"morta\" no grafo e não há nada de errado. Sem essa exceção: 29 acusações no repositório, todas em generator infinito."},
  {"list": ["**um `match` sobre valor constante** não diz qual `point` casa. Matar a"]},
  {"p": "saída dali seria afirmar que um dos padrões casa, e isso exigiria avaliar **padrão**, não valor."},
  {"h3": "Os passes, e nada que possa falhar"},
  {"p": "Três passes: `dobra-de-constante`, `ramo-morto` e `inalcancavel`."},
  {"p": "A regra que mais recusa é a segunda: **nada que possa falhar é dobrado**. `1 / 0` dobrado moveria o erro para a **carga**, longe da linha que o causa; `\"a\" + 1` mudaria a mensagem; `2 ** 1000000` montaria meio milhão de dígitos no carregamento. Diante de qualquer dúvida, o passe não mexe."},
  {"h3": "O número, e ele é desconfortável"},
  {"p": "A escolha do que compilar não foi intuição: saiu do inventário do LIR, que conta, por classe de nó, o que recua para o interpretador de árvore — e separa os recuos **dentro de laço**. Dez nós ganharam construtor no compilador de fechamentos."},
  {"table": {"head": ["Carga", "Antes", "Depois", "Ganho"], "rows": [["feita **dos nós que o inventário aponta**", "507 ms", "382 ms", "**1,33×**"], ["59 exercícios **reais** do repositório", "1150 ms", "1143 ms", "**1,01× — nada**"]]}},
  {"p": "E o motivo é instrutivo: o que recua é dominado por nós que rodam **uma vez** (declaração, `adopt`, `assert` de topo). Os que rodam dentro de laço são poucos por volta, e o trabalho da volta **já estava compilado**: leitura de nome, conta binária, chamada, leitura por índice. Otimizar o que sobra é otimizar 3% de 3%."},
  {"p": "Por isso os passes ficam **desligados por padrão**. A conta honesta é a informação — não a promessa de velocidade."},
  {"h3": "O que NÃO existe, com o motivo"},
  {"list": ["**emitir LLVM IR**: emitir o texto é fácil; usá-lo exigiria `llc` ou"]},
  {"p": "`clang` instalado, e a linguagem passaria a **depender de um compilador C para rodar**."},
  {"list": ["**`llvmlite` ou qualquer backend em pacote**: recusado por regra —"]},
  {"p": "`dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar."},
  {"list": ["**inlining**: numa linguagem em que uma ação pode ser substituída em"]},
  {"p": "tempo de execução (`f := outra`, método sobrescrito na filha), embutir o corpo exigiria provar identidade. É a mesma conferência que a chamada de cauda faz **na hora**, em vez de assumir."},
  {"list": ["**vetorização, análise de alias**: não há registrador SIMD nem ponteiro"]},
  {"p": "a desambiguar."},
  {"list": ["**otimização sobre o MIR**: ele é para **analisar**, não para"]},
  {"p": "reescrever."},
  {"list": ["**target triple, cross compiler, RISC-V, WebAssembly, bare-metal**: não"]},
  {"p": "há código de máquina a produzir para alvo nenhum. O que atravessa plataforma é o interpretador, e ele atravessa por ser Python — o release constrói nas quatro."},
  {"list": ["**passes LLVM em C++**: não há IR para um passe transformar. O análogo"]},
  {"p": "honesto é `--plugin=`, escrito em DataForge, que agora vê o MIR e o SSA."},
  {"p": "O teto da compilação para fechamentos está **medido**: 1,5× a 1,8× conforme a carga, com teto de ~6,5× para a técnica — o mesmo de uma VM de bytecode escrita em Python. Passar disso exige sair do Python, e aí não é mais esta linguagem."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/43-backend/261_ssa_e_otimizacao.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '261-ssa-o-no-phi-e-a-otimizacao-que-foi-medida', text: "261 · SSA, o no phi, e a otimizacao que foi MEDIDA", level: 2 as const }, { id: 'ssa-uma-definicao-por-nome', text: "SSA: uma definição por nome", level: 3 as const }, { id: 'por-que-ssa-paga-a-propagacao-fica-condicional', text: "Por que SSA paga: a propagação fica condicional", level: 3 as const }, { id: 'os-passes-e-nada-que-possa-falhar', text: "Os passes, e nada que possa falhar", level: 3 as const }, { id: 'o-numero-e-ele-e-desconfortavel', text: "O número, e ele é desconfortável", level: 3 as const }, { id: 'o-que-nao-existe-com-o-motivo', text: "O que NÃO existe, com o motivo", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"43 · Backend e otimização"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/43-backend"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
