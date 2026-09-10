import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "15 · Streams e generators",
  description: "6 exercícios: stream action, emit, take e sequências infinitas.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 15`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["145", "**Generators com stream action**", "produza valores um a um com emit, em vez de montar a lista inteira."], ["146", "**Sequencias infinitas**", "escreva um generator sem fim e consuma so o que precisa."], ["147", "**Streams com pipelines**", "combine generators com sift, morph e distill."], ["148", "**Processamento incremental**", "use streams para tratar dados grandes sem carregar tudo na memoria."], ["149", "**observe e eventos**", "reaja a valores conforme eles chegam."], ["150", "**Projeto: ETL com streams**", "monte um pipeline de extracao, transformacao e carga usando generators."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/15-streams-e-generators/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/15-streams-e-generators/145_generator_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"15 · Streams e generators"}
      description={"6 exercícios: stream action, emit, take e sequências infinitas."}
      href={"/docs/exercicios/15-streams-e-generators"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
