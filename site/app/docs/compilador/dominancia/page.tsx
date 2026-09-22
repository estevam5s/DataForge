// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dominância",
  description: "Um bloco domina outro quando todo caminho passa por ele — e a fronteira da dominância é onde os φ vão.",
};

const blocos: Bloco[] = [
  {"p": "No grafo de fluxo, o bloco A **domina** B quando todo caminho da entrada até B passa por A. Alcançar é poder chegar; dominar é não haver como chegar por outro lado. A distinção decide onde duas definições de um nome se encontram — e portanto onde o SSA põe um φ."},
  { code: `adopt Arcane.Compilador as Comp

fonte := "action f(x):\\n    given x bigger 0:\\n        y := 1\\n    otherwise:\\n        y := 2\\n    yield y\\n"
d := Comp.dominancia(fonte, "f")

assert d["dominadores"]["1"] is [0, 1]      // o ramo 'sim' só é dominado pela entrada e por si
assert d["imediato"]["3"] is 0              // a junção: nenhum dos ramos a domina
assert d["fronteira"]["1"] is [3]           // a dominância do ramo acaba na junção
assert d["fronteira"]["2"] is [3]           // e a do outro também: ali vai o φ de 'y' `, lang: 'df' },
  {"table": {"head": ["Pergunta", "Campo"], "rows": [["por quais blocos todo caminho até B passa?", "`dominadores`"], ["qual é o mais próximo deles?", "`imediato` — a árvore de dominância"], ["onde a dominância de B acaba?", "`fronteira` — onde os φ vão"]]}},
  {"p": "As três respostas saem do **mesmo** cálculo que o SSA usa. Duas contas independentes poderiam discordar, e aí o que esta página mostra e o que o compilador faz seriam coisas diferentes. Ver [SSA e o nó φ](/docs/compilador/ssa)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Dominância"}
      description={"Um bloco domina outro quando todo caminho passa por ele — e a fronteira da dominância é onde os φ vão."}
      href={"/docs/compilador/dominancia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
