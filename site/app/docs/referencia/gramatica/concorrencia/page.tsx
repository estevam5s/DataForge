// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Concorrência",
  description: "4 produções: thread, parallel, async. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem não sincroniza sozinha. Estas formas criam concorrência; proteger o estado compartilhado é escolha de quem escreve."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`thread`", "`ThreadBlock`"], ["`parallel`", "`ParallelBlock`"], ["`await`", "`AwaitExpression`"], ["`canais`", "`ChannelDeclaration`, `PulseStatement`, `WaitStatement`"]]}},
  {"h2": "thread"},
  { code: `thread        = "thread" bloco ;`, lang: 'text' },
  { code: `thread:
    out 1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`thread` não espera; o erro do corpo é desenhado na hora."}},
  {"h2": "parallel"},
  { code: `paralelo      = "parallel" bloco ;`, lang: 'text' },
  { code: `parallel:
    out 1
    out 2`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`parallel` espera todas, e levanta na linha do bloco se alguma falhou."}},
  {"h2": "await"},
  { code: `esperar       = "await" expressao ;`, lang: 'text' },
  { code: `async action dobro(n):
    yield n * 2
out await dobro(21)`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Chamar uma ação `async` começa o trabalho e devolve a tarefa; `await` espera."}},
  {"h2": "canais"},
  { code: `canal         = "channel" nome ;
evento        = "pulse" expressao [ "," expressao ] ;
dormir        = "wait" expressao ;`, lang: 'text' },
  { code: `channel fila
fila.send("oi")
pulse "pedido.criado", {"id": 7}
wait 1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`receive()` sem prazo **não espera**: devolve `void` na hora se a fila está vazia. Para esperar, `receive(ms)`."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica concorrencia`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'thread', text: "thread", level: 2 as const }, { id: 'parallel', text: "parallel", level: 2 as const }, { id: 'await', text: "await", level: 2 as const }, { id: 'canais', text: "canais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Concorrência"}
      description={"4 produções: thread, parallel, async. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
