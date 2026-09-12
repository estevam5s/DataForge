// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "27 · Ponte python",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 27`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["217", "**A ponte para o Python**", "use uma biblioteca Python de dentro do DataForge, e faca"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/27-ponte-python/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/27-ponte-python/217_ponte_python.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"27 · Ponte python"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/27-ponte-python"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
