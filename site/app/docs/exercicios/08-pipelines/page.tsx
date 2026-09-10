import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "08 · Pipelines",
  description: "12 exercícios: sift, morph, distill e composição.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 08`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["087", "**sift (filtro)**", "filtre numeros e registros com o operador >>."], ["088", "**morph (transformacao)**", "transforme cada elemento de um cluster."], ["089", "**distill (reducao)**", "reduza um cluster a um unico valor."], ["090", "**Pipeline encadeado**", "combine sift, morph e distill em uma unica expressao."], ["091", "**Pipeline com acao nomeada**", "reutilize acoes declaradas dentro do pipeline."], ["092", "**map, filter e reduce como metodos**", "a mesma logica do pipeline, com metodos de cluster."], ["093", "**Composicao de funcoes**", "combine acoes pequenas em uma maior."], ["094", "**Aplicacao parcial e curry**", "fixe argumentos e gere novas acoes."], ["095", "**Arcane.Functional**", "use utilitarios funcionais da biblioteca padrao."], ["096", "**Streams reativos**", "observe os itens de um stream conforme chegam."], ["097", "**Relatorio com pipelines**", "gere um resumo de vendas por vendedor."], ["098", "**Pipeline de limpeza de dados**", "normalize uma lista suja de emails."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/08-pipelines/087_sift.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"08 · Pipelines"}
      description={"12 exercícios: sift, morph, distill e composição."}
      href={"/docs/exercicios/08-pipelines"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
