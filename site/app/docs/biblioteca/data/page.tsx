import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Data",
  description: "DataFrames, séries e transformações.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Data as Data

registros := [
    {"nome": "Ana", "setor": "TI"},
    {"nome": "Bruno", "setor": "RH"}
]

out Data.group_by(registros, "setor").keys()`, title: `exemplo` },
  {"h2": "Funções (13)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Frame(data=None, columns=None)`"], ["`correlate(x, y)`"], ["`describe(data)`"], ["`group_by(data, key_func)`"], ["`merge(left, right, on)`"], ["`normalize(data, min_val=0, max_val=1)`"], ["`one_hot(labels)`"], ["`pivot(data, index_col, value_col, agg='sum')`"], ["`read_csv(path, header=True)`"], ["`read_json(path)`"], ["`series(data, name='series')`"], ["`split(data, ratio=0.8)`"], ["`standardize(data)`"]]}},
];

const headings = [{ id: 'funcoes-13', text: "Funções (13)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Data"}
      description={"DataFrames, séries e transformações."}
      href={"/docs/biblioteca/data"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
