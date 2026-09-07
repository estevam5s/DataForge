import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "grafo",
  description: "Grafos: busca, caminho mínimo, ordenação topológica e componentes.",
};

const blocos: Bloco[] = [
  { code: `dataforge add grafo`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "3 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Dirigido por padrão. `ordem_topologica` devolve `void` quando há ciclo, em vez de uma lista incompleta em silêncio — um grafo com ciclo não tem ordem, e dizer isso é melhor que fingir."},
  {"h2": "Uso"},
  { code: `adopt grafo as G

g := G.novo()
g.ligar("a", "b", 4)
g.ligar("b", "c", 2)
out g.caminho_minimo("a", "c")   // {distancia: 6, caminho: [a, b, c]}`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 3 símbolos:"},
  { code: `blueprint Grafo
novo(dirigido := yes)
de_arestas(lista, dirigido := yes)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add grafo
dataforge add grafo@1.0.0
dataforge add grafo@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"grafo"}
      description={"Grafos: busca, caminho mínimo, ordenação topológica e componentes."}
      href={"/docs/pacotes/grafo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
