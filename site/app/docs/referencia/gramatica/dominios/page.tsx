// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Blocos de domínio",
  description: "3 produções: crucible, server e as palavras contextuais. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "Palavras que só valem dentro do bloco que as abre — por isso não roubam nomes de quem escreve."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`crucible`", "`CrucibleBlock`"], ["`server`", "`ServerBlock`"], ["`dados`", "`FrameExpression`, `TrainExpression`, `PredictExpression`"]]}},
  {"h2": "crucible"},
  { code: `suite         = "crucible" texto ":" NEWLINE INDENT
                { "trial" texto [ "pending" ] bloco | fixture | gancho } DEDENT ;
cobranca      = "expect" expressao ;`, lang: 'text' },
  { code: `crucible "s":
    trial "t":
        expect 1 is 1`, lang: 'df' },
  {"h2": "server"},
  { code: `servidor      = "server" nome [ "on" expressao ] [ "at" expressao ] ":" NEWLINE INDENT
                { "route" verbo texto bloco | middleware | mount | assets } DEDENT ;
resposta      = "respond" [ inteiro ] [ "json" | "html" | "text" ] expressao ;`, lang: 'text' },
  { code: `server api on 0:
    route GET "/":
        respond json {"ok": yes}`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "As onze palavras do Kiln são contextuais: `route := \"/x\"` continua valendo fora de um `server`."}},
  {"h2": "dados"},
  { code: `quadro        = "frame" expressao ;
treinar       = "train" texto "using" expressao ;
prever        = "predict" expressao "using" expressao ;`, lang: 'text' },
  { code: `t := frame [{"a": 1}, {"a": 3}]
dados := [{"x": 1.0, "y": 2.0}, {"x": 2.0, "y": 4.0}]
m := train "linear" using {"linhas": dados, "alvo": "y", "colunas": ["x"]}
out predict m using [{"x": 3.0}]`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "São açúcar fino sobre `Arcane.Analytics` e `Arcane.Cortex` — não reimplementam nada."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica dominios`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'crucible', text: "crucible", level: 2 as const }, { id: 'server', text: "server", level: 2 as const }, { id: 'dados', text: "dados", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Blocos de domínio"}
      description={"3 produções: crucible, server e as palavras contextuais. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/dominios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
