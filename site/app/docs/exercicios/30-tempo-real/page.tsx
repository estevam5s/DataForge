// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "30 · Tempo real",
  description: "2 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 30`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["223", "**Receber arquivo**", ""], ["224", "**O servidor empurra: SSE e WebSocket**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/30-tempo-real/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/30-tempo-real/223_upload.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"30 · Tempo real"}
      description={"2 exercícios: ."}
      href={"/docs/exercicios/30-tempo-real"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
