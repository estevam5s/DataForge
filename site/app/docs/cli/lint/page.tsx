import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge lint",
  description: "Apontar problemas de estilo",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge lint src/
dataforge lint . --strict`, lang: 'bash' },
  {"h2": "As 13 regras"},
  {"p": "Variável e import sem uso, parâmetro nunca lido, bloco vazio, número mágico repetido, ação longa, aninhamento profundo, convenção de nomes, `otherwise` redundante, dupla negação, comparação com booleano e comentários TODO."},
  {"h2": "Silenciar de propósito"},
  { code: `cycle _ in range(0, 3):        # o '_' diz que o valor não interessa
action f(dados, _contexto):    # parâmetro exigido pela interface` },
  {"p": "A lista completa está em [Lint](/docs/tecnicas/lint)."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'as-13-regras', text: "As 13 regras", level: 2 as const }, { id: 'silenciar-de-proposito', text: "Silenciar de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge lint"}
      description={"Apontar problemas de estilo"}
      href={"/docs/cli/lint"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
