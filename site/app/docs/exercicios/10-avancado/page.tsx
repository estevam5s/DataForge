import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "10 · Avancado",
  description: "10 exercícios: decoradores, generators, threads e canais.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 10`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["111", "**async / await**", "declare acoes assincronas e aguarde o resultado."], ["112", "**thread**", "dispare trabalho em segundo plano e espere terminar."], ["113", "**channel**", "passe valores entre partes do programa por um canal."], ["114", "**parallel**", "rode varias tarefas ao mesmo tempo."], ["115", "**defer com recursos reais**", "garanta que o arquivo seja apagado mesmo apos erro."], ["116", "**Lista ligada com blueprints**", "implemente uma lista ligada simples."], ["117", "**Arvore binaria de busca**", "insira valores e percorra em ordem."], ["118", "**Maquina de estados**", "modele o ciclo de vida de um pedido."], ["119", "**Sistema de inventario**", "junte blueprints, pipelines, erros e relatorio."], ["120", "**Avaliador de expressoes em notacao polonesa reversa**", "escreva um mini interpretador dentro do DataForge."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/10-avancado/111_async_await.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"10 · Avancado"}
      description={"10 exercícios: decoradores, generators, threads e canais."}
      href={"/docs/exercicios/10-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
