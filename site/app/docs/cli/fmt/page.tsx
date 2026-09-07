import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge fmt",
  description: "Formatar o código",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge fmt arquivo.df
dataforge fmt src/
dataforge fmt . --check      # só verifica, para CI`, lang: 'bash' },
  {"h2": "As regras"},
  {"p": "4 espaços por nível, um espaço em volta de operadores binários, nada depois de `(` ou antes de `)`, sem espaço em branco no fim da linha."},
  {"h2": "Idempotente"},
  {"p": "Formatar duas vezes dá o mesmo resultado que formatar uma. Há teste para isso sobre os 225 arquivos do repositório."},
  {"h2": "~/ em vez de //"},
  {"p": "A divisão inteira é sempre reimpressa como `~/`. Reimprimir `//` faria a linha virar comentário na passagem seguinte."},
  {"p": "Detalhes em [Formatação](/docs/tecnicas/formatacao)."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'as-regras', text: "As regras", level: 2 as const }, { id: 'idempotente', text: "Idempotente", level: 2 as const }, { id: 'em-vez-de', text: "~/ em vez de //", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge fmt"}
      description={"Formatar o código"}
      href={"/docs/cli/fmt"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
