import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge doc",
  description: "Gerar documentação Markdown",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge doc lib.df                    # imprime no terminal
dataforge doc src/ --out=doc/API.md`, lang: 'bash' },
  {"h2": "A convenção"},
  {"p": "O comentário **imediatamente acima** de uma declaração é a sua documentação. Os comentários do topo do arquivo viram a descrição do módulo."},
  { code: `// Calcula a area de um circulo.
// O raio precisa ser positivo.
action area_circulo(raio: Number) -> Float:
    yield PI * raio ** 2` },
  {"p": "Detalhes em [Documentação](/tecnicas/documentacao)."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'a-convencao', text: "A convenção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge doc"}
      description={"Gerar documentação Markdown"}
      href={"/cli/doc"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
