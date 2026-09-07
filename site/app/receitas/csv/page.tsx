import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Processamento de CSV",
  description: "Ler, limpar, validar e agregar dados tabulares.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `105_dados_tabulares.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Analytics as An

registros := [
    {"setor": "TI", "salario": 8000},
    {"setor": "RH", "salario": 5000},
    {"setor": "TI", "salario": 9500},
    {"setor": "RH", "salario": 5500},
    {"setor": "TI", "salario": 7000}
]

grupos := An.group_by(registros, "setor")
out "setores:", grupos.keys()

cycle setor in grupos.keys():
    salarios := grupos[setor] >> morph r: r["salario"]
    out "  " + setor.pad_end(4) + "n=" + str(len(salarios)) + " media=" + str(round(mean(salarios), 2))

assert len(grupos.keys()) is 2, "dois setores"
assert len(grupos["TI"]) is 3, "3 registros de TI"

contagem := An.value_counts(registros >> morph r: r["setor"])
out "contagem:", contagem
assert contagem["TI"] is 3, "TI aparece 3x"`, title: `105_dados_tabulares.df` },
  {"h2": "O fluxo"},
  {"p": "Ler o CSV, converter cada linha num record tipado, validar, agregar e reportar. Para arquivos grandes, o mesmo desenho vira um [pipeline de streams](/tecnicas/streams)."},
  {"h2": "Serialização"},
  { code: `adopt Arcane.Serialization as Serde

registros := Serde.csv_to_records(IO.read("dados.csv"))
IO.write("saida.csv", Serde.records_to_csv(processados))` },
  {"p": "`csv_to_records` assume que a primeira linha é cabeçalho e transforma cada linha num vault — o formato natural para dados tabulares."},
];

const headings = [{ id: 'o-fluxo', text: "O fluxo", level: 2 as const }, { id: 'serializacao', text: "Serialização", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Processamento de CSV"}
      description={"Ler, limpar, validar e agregar dados tabulares."}
      href={"/receitas/csv"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
