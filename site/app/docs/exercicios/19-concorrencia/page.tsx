import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "19 · Concorrencia",
  description: "6 exercícios: threads, canais, tarefas e paralelismo.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 19`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["169", "**Acoes assincronas**", "declare acoes async e aguarde o resultado com await."], ["170", "**Threads e paralelismo**", "execute trabalho em segundo plano."], ["171", "**Canais entre threads**", "passe valores entre threads com seguranca."], ["172", "**Liberacao garantida**", "garanta limpeza mesmo quando algo falha."], ["173", "**Erros e retentativas**", "trate falhas temporarias com retry e propagacao controlada."], ["174", "**Projeto: fila de trabalho**", "monte um sistema de tarefas com fila, trabalhadores e relatorio."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/19-concorrencia/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/19-concorrencia/169_async_await.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"19 · Concorrencia"}
      description={"6 exercícios: threads, canais, tarefas e paralelismo."}
      href={"/docs/exercicios/19-concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
