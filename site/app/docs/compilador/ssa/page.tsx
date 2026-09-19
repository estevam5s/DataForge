// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_backend.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "SSA e o nó φ",
  description: "Uma definição por nome, dominância, fronteira de dominância — e a propagação de constante que fica estritamente mais forte por causa disso.",
};

const blocos: Bloco[] = [
  {"p": "O [MIR](/docs/compilador/mir) diz por onde o programa passa. O que ele **não** diz é *qual* atribuição uma leitura vê. Num corpo com três `x := …`, a pergunta \"de onde vem este `x`?\" precisa ser reconstruída a cada análise — e cada análise que a reconstrói é uma chance de reconstruí-la diferente."},
  {"p": "SSA responde isso por construção: cada nome é **numerado**, cada versão tem **exatamente uma** definição, e onde dois caminhos trazem versões diferentes aparece um nó **φ** que diz de onde cada uma vem."},
  { code: `given c:                 bloco 0 [entrada] → 1 (sim), 2 (nao)
    x := 1               bloco 1 [sim]      x₁ := 1
otherwise:               bloco 2 [nao]      x₂ := 2
    x := 2               bloco 3 [juncao]   x₃ := φ(1: x₁, 2: x₂)
out x                                       out  le x₃`, lang: 'text', title: `dataforge ir --fase=ssa` },
  {"h2": "Dominar não é alcançar"},
  {"p": "**Alcançar** é poder chegar; **dominar** é não haver como chegar por outro lado. É essa diferença que decide onde um φ é necessário: um ramo não domina a junção — dá para chegar lá pelo outro ramo —, então a junção precisa de φ. E é a **fronteira de dominância** que diz exatamente onde: o ponto em que a dominância de um bloco acaba."},
  { code: `adopt Arcane.Compilador as K

fonte := "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n"
forma := K.ssa(fonte)[0]

fis := [f cycle b in forma["blocos"] cycle f in b["fis"]]
assert len(fis) is 1
assert fis[0]["nome"] is "x"
assert len(fis[0]["fontes"]) is 2      // vem dos dois ramos`, lang: 'df' },
  { code: `adopt Arcane.Compilador as K

// um nome com uma definicao so nao precisa de φ
assert K.ssa("x := 1\\nout x\\n")[0]["blocos"][0]["fis"] is []

// e o laco tem φ na cabeca: o nome volta pela aresta de tras
comLaco := K.ssa("t := 0\\ncycle i in [1, 2]:\\n    t := t + i\\nout t\\n")[0]
cabeca := [b cycle b in comLaco["blocos"] given b["rotulo"] is "condicao"][0]
assert len([f cycle f in cabeca["fis"] given f["nome"] is "t"]) is 1`, lang: 'df' },
  {"h2": "O que ela paga: a propagação fica condicional"},
  {"p": "A [propagação sobre o MIR](/docs/compilador/analises) junta os ramos por **interseção**, e por isso perde o que só um ramo decide. Ela está certa em perder — sem saber qual ramo roda, não há o que concluir."},
  {"p": "Com SSA a análise pode ir além: ela **não avalia** o ramo cuja condição prova falsa. Aí a junção tem um predecessor vivo só, o φ tem uma fonte só, e o valor **se conclui**."},
  { code: `adopt Arcane.Compilador as K

fonte := "x := 1\\ngiven x bigger 5:\\n    y := \\"nunca\\"\\n" +
         "otherwise:\\n    y := \\"sempre\\"\\nout y\\n"

// o ramo que nao roda e nomeado, com o bloco e a linha
mortos := K.ramos_mortos(fonte)
assert len(mortos) bigger 0
assert mortos[0]["rotulo"] is "sim"

// e o valor de 'y' se conclui — a propagacao sobre o MIR nao sabia
provadas := K.provadas(fonte, "(programa)")
assert "sempre" in values(provadas)`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "É estritamente mais forte, e há teste provando", "texto": "`tests/test_ssa_e_otimizacao.py` roda as duas análises sobre o **mesmo** programa: a do MIR não conclui o `y`, a condicional conclui. Sem essa comparação, \"mais forte\" seria só uma afirmação."}},
  {"h2": "Três decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["**as instruções não são reescritas** — a versão é *anexada* (`le`, `escreve`)", "um SSA de livro vira três endereços (`t1 := a + b`), e isso cria uma **segunda semântica** para manter em sincronia com o interpretador — o risco que `compilador.py` evita ao delegar aos mesmos auxiliares"], ["a dominância sai de um **ponto fixo**, e não de Lengauer-Tarjan", "três vezes mais código para ganhar microssegundos num lugar que roda uma vez por corpo; os corpos desta linguagem têm dezenas de blocos, não milhares"], ["o que **não é alcançável** não entra", "um bloco morto teria φ com fonte de lugar nenhum, e a análise passaria a concluir a partir de código que não roda"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A condição da fronteira é fácil de escrever ao contrário", "texto": "A primeira versão perguntava \"`b` domina `atual`?\" onde a pergunta é \"`atual` é o dominador imediato de `b`?\". O resultado: um φ em **todo** bloco de **todo** laço, para nomes que nem se juntavam ali — três φ onde havia um. Um grafo errado não dá erro; ele produz análise com cara de verdade."}},
];

const headings = [{ id: 'dominar-nao-e-alcancar', text: "Dominar não é alcançar", level: 2 as const }, { id: 'o-que-ela-paga-a-propagacao-fica-condicional', text: "O que ela paga: a propagação fica condicional", level: 2 as const }, { id: 'tres-decisoes', text: "Três decisões", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"SSA e o nó φ"}
      description={"Uma definição por nome, dominância, fronteira de dominância — e a propagação de constante que fica estritamente mais forte por causa disso."}
      href={"/docs/compilador/ssa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
