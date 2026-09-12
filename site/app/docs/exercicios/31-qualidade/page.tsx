// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "31 · Qualidade",
  description: "2 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 31`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["225", "**Cobertura: o que os testes NAO exercitaram**", ""], ["226", "**Instantaneo, banco isolado e teste instavel**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/31-qualidade/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/31-qualidade/225_cobertura.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"31 · Qualidade"}
      description={"2 exercícios: ."}
      href={"/docs/exercicios/31-qualidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
