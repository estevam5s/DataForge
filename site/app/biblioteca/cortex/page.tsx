import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Cortex",
  description: "Blocos de rede neural, visão e NLP.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Cortex as Cortex

// Blocos simplificados de rede neural
out Cortex.neural.relu(-5), Cortex.neural.relu(3)
out Cortex.neural.softmax([1.0, 2.0, 3.0])`, title: `exemplo` },
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`neural`", "`{'Sequential': <class 'dataforge.stdlib.arcane…`"], ["`nlp`", "`{'tokenize': <function ArcaneCortex._nlp.<loca…`"], ["`vision`", "`{'load_image': <function ArcaneCortex._vision.…`"]]}},
  {"h2": "Funções (2)"},
  {"table": {"head": ["Assinatura"], "rows": [["`accuracy(predictions, labels)`"], ["`evaluate(model, test_data)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-2', text: "Funções (2)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Cortex"}
      description={"Blocos de rede neural, visão e NLP."}
      href={"/biblioteca/cortex"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
