// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Instruções",
  description: "11 produções: atribuição, saída, controle de fluxo e laços. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "Uma instrução faz algo e não produz valor. As que abrem bloco terminam em `:` e o corpo vem indentado."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`atribuicao`", "`Assignment`"], ["`constante`", "`SteadyDeclaration`"], ["`desestruturacao`", "`DestructuringAssignment`"], ["`saida`", "`OutStatement`"], ["`given`", "`GivenBlock`"], ["`cycle`", "`CycleFromTo`, `CycleIn`"], ["`persist`", "`PersistBlock`, `PerformBlock`"], ["`halt_skip`", "`HaltStatement`, `SkipStatement`"], ["`instrucoes_de_vault`", "`DeleteStatement`, `InspectStatement`"], ["`guard`", "`GuardStatement`"], ["`observe`", "`ObserveBlock`"]]}},
  {"h2": "atribuicao"},
  { code: `atribuicao    = alvo [ ":" tipo ] ":=" expressao
              | alvo ( "+=" | "-=" | "*=" | "/=" | "%=" ) expressao ;`, lang: 'text' },
  { code: `idade: Integer := 30
idade += 1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`:=` atribui; `=` só existe dentro de `lambda … =>`."}},
  {"h2": "constante"},
  { code: `constante     = "steady" nome [ ":" tipo ] ":=" expressao ;`, lang: 'text' },
  { code: `steady PI := 3.14159`, lang: 'df' },
  {"h2": "desestruturacao"},
  { code: `desestruturar = alvo_d { "," alvo_d } ":=" expressao ;
alvo_d        = [ "..." ] nome ;`, lang: 'text' },
  { code: `primeiro, ...resto := [1, 2, 3]`, lang: 'df' },
  {"h2": "saida"},
  { code: `saida         = "out" expressao { "," expressao } ;`, lang: 'text' },
  { code: `out "ola", 42`, lang: 'df' },
  {"h2": "given"},
  { code: `condicional   = "given" expressao bloco { "orif" expressao bloco }
                [ "otherwise" bloco ] ;`, lang: 'text' },
  { code: `x := 5
given x bigger 5:
    out 1
orif x is 5:
    out 0
otherwise:
    out -1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Um nome atribuído num ramo existe depois do bloco; o corpo de um `cycle` tem escopo próprio."}},
  {"h2": "cycle"},
  { code: `laco_faixa    = "cycle" nome "from" expressao "to" expressao [ "step" expressao ] bloco ;
laco_itens    = "cycle" nome "in" expressao bloco ;`, lang: 'text' },
  { code: `cycle i from 1 to 5 step 2:
    out i
cycle v in [1, 2]:
    out v`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`from … to` é inclusivo nos dois extremos."}},
  {"h2": "persist"},
  { code: `enquanto      = "persist" expressao bloco ;
repita        = "perform" bloco "persist" expressao ;`, lang: 'text' },
  { code: `n := 3
persist n bigger 0:
    n -= 1
perform:
    n += 1
persist n smaller 3`, lang: 'df' },
  {"h2": "halt_skip"},
  { code: `interromper   = "halt" ;
continuar     = "skip" ;`, lang: 'text' },
  { code: `cycle i in [1, 2, 3]:
    given i is 2:
        skip
    given i is 3:
        halt`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`halt`, `skip` e `yield` atravessam `monitor`: são sinais de controle, não erros."}},
  {"h2": "instrucoes_de_vault"},
  { code: `apagar        = "delete" alvo_de_indice ;
inspecionar   = "inspect" expressao ;`, lang: 'text' },
  { code: `v := {"a": 1, "b": 2}
delete v["a"]
inspect v`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`inspect` imprime o valor **com o tipo** — para depurar."}},
  {"h2": "guard"},
  { code: `guarda        = "guard" expressao "otherwise" bloco ;`, lang: 'text' },
  { code: `action dividir(a, b):
    guard b isnt 0 otherwise:
        yield void
    yield a / b`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Sai cedo quando a condição **não** vale — o `otherwise` precisa sair (`yield`, `trigger`, `halt`)."}},
  {"h2": "observe"},
  { code: `observar      = "observe" nome "in" expressao bloco ;`, lang: 'text' },
  { code: `observe x in [1, 2, 3]:
    out x`, lang: 'df' },
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica instrucoes`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'atribuicao', text: "atribuicao", level: 2 as const }, { id: 'constante', text: "constante", level: 2 as const }, { id: 'desestruturacao', text: "desestruturacao", level: 2 as const }, { id: 'saida', text: "saida", level: 2 as const }, { id: 'given', text: "given", level: 2 as const }, { id: 'cycle', text: "cycle", level: 2 as const }, { id: 'persist', text: "persist", level: 2 as const }, { id: 'haltskip', text: "halt_skip", level: 2 as const }, { id: 'instrucoesdevault', text: "instrucoes_de_vault", level: 2 as const }, { id: 'guard', text: "guard", level: 2 as const }, { id: 'observe', text: "observe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Instruções"}
      description={"11 produções: atribuição, saída, controle de fluxo e laços. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/instrucoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
