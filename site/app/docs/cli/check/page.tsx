import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge check",
  description: "Análise estática antes de executar",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge check arquivo.df
dataforge check src/              # a pasta inteira
dataforge check . --strict        # avisos também falham
dataforge check x.df --syntax-only`, lang: 'bash' },
  {"h2": "O que encontra"},
  {"p": "Nomes indefinidos com sugestão, aridade errada, tipos incompatíveis, campos de record, membros de enum, constantes reatribuídas, código inalcançável e retorno ausente."},
  { code: `app.df:9:11: erro: Parameter 'a' of 'somar' expects Integer but got String
    sugestão: Pass a Integer
app.df:10:5: erro: Undefined action 'sommar'
    sugestão: Did you mean 'somar'?

✗ 2 erro(s), 0 aviso(s)`, lang: 'text' },
  {"h2": "Otimista de propósito"},
  {"p": "Quando não consegue **provar** que algo está errado, fica calado. Zero falsos positivos em 225 arquivos conhecidamente bons."},
  {"p": "Guia completo em [Análise estática](/docs/tecnicas/analise-estatica)."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'o-que-encontra', text: "O que encontra", level: 2 as const }, { id: 'otimista-de-proposito', text: "Otimista de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge check"}
      description={"Análise estática antes de executar"}
      href={"/docs/cli/check"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
