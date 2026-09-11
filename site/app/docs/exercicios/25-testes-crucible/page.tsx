// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "25 · Testes crucible",
  description: "4 exercícios: suítes, matchers, fixtures e dublês.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 25`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["209", "**A primeira suite**", "escreva testes que dizem o que quebrou, e nao so que quebrou."], ["210", "**Isolamento entre trials**", "prove que um teste nao contamina o proximo."], ["211", "**Os matchers**", "cobre valores de todas as formas, e leia o que a falha diz."], ["212", "**Dubles e fixtures**", "teste uma regra de negocio sem tocar no banco."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/25-testes-crucible/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/25-testes-crucible/209_primeira_suite.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"25 · Testes crucible"}
      description={"4 exercícios: suítes, matchers, fixtures e dublês."}
      href={"/docs/exercicios/25-testes-crucible"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
