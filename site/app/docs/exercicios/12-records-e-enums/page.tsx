import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "12 · Records e enums",
  description: "6 exercícios: imutabilidade, 'with' e enums com valor.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 12`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["127", "**Records**", "declare um record, construa instancias e comprove a igualdade estrutural."], ["128", "**Imutabilidade e with**", "comprove que um record nao muda, e crie copias alteradas com with."], ["129", "**Records com metodos**", "adicione comportamento a um record sem abrir mao da imutabilidade."], ["130", "**Enums**", "declare um conjunto fechado de valores e use seus membros com seguranca."], ["131", "**Enums com valores**", "associe dados a cada membro e converta de ida e volta."], ["132", "**Enums com match**", "use pattern matching para tratar cada membro e garantir cobertura."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/12-records-e-enums/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/12-records-e-enums/127_record_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"12 · Records e enums"}
      description={"6 exercícios: imutabilidade, 'with' e enums com valor."}
      href={"/docs/exercicios/12-records-e-enums"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
