// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O percurso, e onde o tempo vai",
  description: "As nove fases de compilação em ordem, com o que cada uma produziu e quanto levou — e por que o comando não executa o programa.",
};

const blocos: Bloco[] = [
  {"p": "[`dataforge ir`](/docs/compilador/pipeline) mostra **cada** fase: o HIR, o MIR, as análises, a SSA, o LIR. O que não havia era a visão de cima — as fases **em ordem**, o que cada uma produziu e quanto tempo levou."},
  {"p": "Que é a pergunta que aparece quando um arquivo demora a abrir no editor: *onde o tempo vai?*"},
  { code: `dataforge percurso app.df              # a tabela de fases
dataforge percurso app.df --sem-tipos  # pula a analise estatica
dataforge percurso --desenho           # o caminho, com as ausencias
dataforge percurso app.df --json       # como dado`, lang: 'bash' },
  { code: `  app.df  —  0.526 ms no total

  fase              ms      %   o que saiu
  lexer          0.064   12.2   12 tokens
  parser         0.034    6.4   5 nos, 2 no topo
  hir            0.007    1.2   0 acucares em 0 formas
  tipos          0.143   27.2   0 erro(s), 0 aviso(s)
  mir            0.050    9.5   1 corpo(s), 1 bloco(s)
  analises       0.040    7.6   0 morto(s), 0 talvez nao definido(s)
  ssa            0.033    6.3   0 no(s) phi
  otimizar       0.092   17.4   0 oportunidade(s) em 0 passe(s)
  lir            0.064   12.2   4 de 4 nos viraram fechamento (100%)
  execucao           —          nao percorrida: executar e o que o programa faz

  a fase mais cara deste arquivo: tipos`, lang: 'text', title: `dataforge percurso — a saída` },
  {"h2": "Ele não executa o programa, e isso é deliberado"},
  {"p": "O percurso vai do lexer ao compilador de fechamentos e **para ali**. A última fase é nomeada, medida em zero e marcada como não percorrida, com o motivo escrito."},
  {"callout": {"tipo": "atencao", "titulo": "Um comando que mostra fases não pode ter efeito no mundo", "texto": "Executar é o que o programa faz — e um arquivo de verdade abre soquete, escreve em disco e manda e-mail. Um `dataforge percurso` que executasse seria usado **uma vez**. A fase continua no mapa para que a ausência tenha lugar, do mesmo modo que `Machine Code` continua no desenho do ecossistema."}},
  { code: `adopt Arcane.Percurso as Perc

fs := Perc.fases()
assert len(fs) is 10
assert fs[0]["fase"] is "lexer"
assert fs[9]["fase"] is "execucao"     // nomeada, e NAO percorrida

d := Perc.divergencias()
assert len(d) bigger_eq 5
out $"{len(fs)} fases, {len(d)} divergencias do desenho"`, lang: 'df' },
  {"h2": "A armadilha que inverteu a resposta"},
  {"p": "A primeira versão deste comando apontava a fase errada — e apontava com confiança, que é o pior jeito de errar."},
  {"table": {"head": ["Arquivo de 12 tokens", "Antes", "Depois"], "rows": [["fase apontada como mais cara", "`lir`, com **93,8%**", "`tipos`, com 27,2%"], ["total", "7,266 ms", "**0,526 ms**"], ["trabalho real do `lir`", "0,05 ms", "0,064 ms"]]}},
  {"p": "A causa: `lir` importa `compilador` e abre um interpretador **por dentro**. A primeira fase que toca um módulo paga o `import` dele, e o cronômetro atribui esse custo a ela."},
  {"callout": {"tipo": "perigo", "titulo": "Uma ferramenta que aponta a fase errada é pior que nenhuma", "texto": "A pessoa vai otimizar o lugar que a ferramenta indicou. Hoje os imports lentos acontecem **antes** de qualquer cronômetro, e o módulo diz isso num comentário ao lado da linha que os aquece — para que ninguém os remova por parecerem inúteis."}},
  {"h2": "O tempo é uma medida, não um benchmark"},
  {"p": "Cada fase é cronometrada **uma** vez, nesta máquina, com esta carga. Serve para comparar as fases **entre si** — que é a pergunta — e não para comparar máquinas nem para afirmar que uma mudança melhorou algo."},
  {"p": "Para isso há [`Arcane.Bench`](/docs/observabilidade/comparar), que repete, tira **mediana** (e não média: uma pausa do coletor no meio da amostra a carrega para sempre) e sabe dizer, por Mann-Whitney, se a diferença é real."},
  { code: `adopt Arcane.Percurso as Perc
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-percurso-{randint(100000, 999999)}"
IO.mkdir(pasta)
alvo := $"{pasta}/exemplo.df"
IO.write(alvo, "action dobrar(n):\\n    yield n * 2\\nout dobrar(21)\\n")

r := Perc.percorrer(alvo)
assert len(r["fases"]) is 10
assert r["ms"] bigger 0

// a ultima fase existe no mapa e NAO foi percorrida
ultima := r["fases"][9]
assert ultima["fase"] is "execucao"
assert ultima["percorrida"] is no

out $"a fase mais cara: {r['mais_cara']}"
IO.remove_tree(pasta)`, lang: 'df' },
  {"h2": "O que cada fase entrega"},
  {"table": {"head": ["Fase", "Arquivo", "O que sai"], "rows": [["`lexer`", "`lexer.py`", "tokens, com INDENT/DEDENT e interpolação"], ["`parser`", "`parser.py`", "a árvore — e quantos nós ela tem"], ["`hir`", "`hir.py`", "quantos açúcares o arquivo usa, de 5 formas; e **8 construções que não são açúcar**, cada uma com o motivo"], ["`tipos`", "`typechecker.py`", "erros e avisos — e esta fase **atravessa** os `adopt`"], ["`mir`", "`mir.py`", "corpos e blocos básicos, com arestas rotuladas"], ["`analises`", "`mir.py`", "bloco morto, nome talvez não definido, constante provada"], ["`ssa`", "`ssa.py`", "nós φ das junções"], ["`otimizar`", "`otimizar.py`", "oportunidades de dobra, ramo morto e inalcançável"], ["`lir`", "`lir.py`", "quantos nós desceram para fechamento, e **quantos recuaram**"], ["`execucao`", "`interpreter.py`", "— não percorrida"]]}},
  {"callout": {"tipo": "dica", "titulo": "A fase `tipos` é a mais cara num projeto de verdade", "texto": "Ela lê a **superfície** dos arquivos vizinhos para conferir aridade, tipo de parâmetro e tipo de retorno através do `adopt`. O cache é por `(caminho, mtime)`: sem ele, 200 arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto. `--sem-tipos` a pula, quando a pergunta é sobre as outras."}},
  {"h2": "O que a medida mostrou, e não era o esperado"},
  {"p": "No maior exemplo do repositório — 2.233 tokens, 1.161 nós — a fase mais cara **não** é o verificador de tipos nem a construção do grafo:"},
  {"table": {"head": ["Fase", "Fatia", "O que ela achou"], "rows": [["`otimizar`", "**35,3%**", "8 oportunidades, em 2 dos 3 passes"], ["`mir`", "15,4%", "21 corpos, 66 blocos"], ["`tipos`", "11,7%", "0 erros, 1 aviso"], ["`ssa`", "10,9%", "10 nós φ"], ["`lir`", "3,9%", "1.113 de 1.153 nós compilados (97%)"]]}},
  {"p": "**O passe que acha menos é o que custa mais.** `relatorio_de` reescreve a árvore inteira para contar, e num arquivo que já está bem escrito ele encontra oito dobras de constante e nada mais."},
  {"callout": {"tipo": "nota", "titulo": "E isso é coerente com o que já estava medido", "texto": "Os passes de otimização deste repositório rendem **1,01×** na execução. Um ganho de 1% que custa um terço do tempo de análise é exatamente o tipo de número que costuma não ser publicado — e é o que decide se vale ligá-los por padrão. Eles não são ligados: `dataforge ir --fase=otimizado` mostra o que eles conseguiriam, e fica a cargo de quem lê."}},
  {"h2": "O caminho real, e onde ele difere do desenho"},
  {"p": "`dataforge percurso --desenho` imprime o caminho com as ausências no lugar delas. As cinco divergências em relação ao desenho da referência:"},
  {"table": {"head": ["No desenho", "Aqui", "Por quê"], "rows": [["`Borrow + Dataflow Checker`", "o Dataflow existe; o Borrow, não", "num mundo com coletor, o que se protege é o protocolo — e quem o protege é `Arcane.Posse` mais três códigos do `check`"], ["`LLVM Backend`", "`compilador.py` — fechamentos", "o LLVM tiraria a zero dependência. Medido: 1,5× a 1,8×, com teto ~6,5×"], ["`Machine Code / WASM`", "não há; o artefato é a árvore compilada", "rodar **em** WASM funciona pelo Pyodide, e isso é outra frase"], ["`Bare-Metal Runtime`", "não há", "o runtime é o CPython"], ["*(ausente no desenho)* `Execution Engine`", "`interpreter.py` — o centro", "o desenho supõe compilação antecipada, e por isso não tem onde pôr o interpretador"]]}},
];

const headings = [{ id: 'ele-nao-executa-o-programa-e-isso-e-deliberado', text: "Ele não executa o programa, e isso é deliberado", level: 2 as const }, { id: 'a-armadilha-que-inverteu-a-resposta', text: "A armadilha que inverteu a resposta", level: 2 as const }, { id: 'o-tempo-e-uma-medida-nao-um-benchmark', text: "O tempo é uma medida, não um benchmark", level: 2 as const }, { id: 'o-que-cada-fase-entrega', text: "O que cada fase entrega", level: 2 as const }, { id: 'o-que-a-medida-mostrou-e-nao-era-o-esperado', text: "O que a medida mostrou, e não era o esperado", level: 2 as const }, { id: 'o-caminho-real-e-onde-ele-difere-do-desenho', text: "O caminho real, e onde ele difere do desenho", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O percurso, e onde o tempo vai"}
      description={"As nove fases de compilação em ordem, com o que cada uma produziu e quanto levou — e por que o comando não executa o programa."}
      href={"/docs/ecossistema/percurso"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
