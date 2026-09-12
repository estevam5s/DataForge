// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "28 · Vitrine",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 28`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["218", "**Uma aplicacao de dados com a Vitrine**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/28-vitrine/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/28-vitrine/218_vitrine.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"28 · Vitrine"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/28-vitrine"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
