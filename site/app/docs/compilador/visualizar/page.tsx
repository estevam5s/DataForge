// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Desenhar o grafo",
  description: "O grafo de fluxo em DOT: blocos, arestas rotuladas, e o código que nunca roda tracejado.",
};

const blocos: Bloco[] = [
  {"p": "Um grafo de fluxo lido como texto é difícil de acompanhar a partir de dez blocos. `Comp.dot` o escreve no formato do **Graphviz**, e o desenho mostra de uma vez o que o texto espalha: os ramos, o laço voltando, e o que nunca roda."},
  { code: `adopt Arcane.Compilador as Comp

fonte := "action f(n):\\n    total := 0\\n    cycle i from 1 to n:\\n        total += i\\n    yield total\\n    out \\"nunca\\"\\n"
dot := Comp.dot(fonte, "f")
out dot

assert dot.starts_with("digraph fluxo {")
assert dot.contains('[label="volta"]')            // a aresta que fecha o laço
assert dot.contains("style=dashed")                // o 'out' depois do yield`, lang: 'df' },
  { code: `IO.write("fluxo.dot", Comp.dot(IO.read("pedido.df")))
// no terminal:  dot -Tsvg fluxo.dot -o fluxo.svg`, lang: 'text' },
  {"table": {"head": ["No desenho", "Quer dizer"], "rows": [["uma caixa", "um bloco básico: instruções que rodam sempre juntas"], ["`sim` / `nao`", "os dois lados de uma condição"], ["`volta`", "a aresta que fecha um laço"], ["`erro`", "o caminho de um `monitor` para o `handle`"], ["caixa tracejada e cinza", "bloco que nenhum caminho alcança"]]}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Desenhar o grafo"}
      description={"O grafo de fluxo em DOT: blocos, arestas rotuladas, e o código que nunca roda tracejado."}
      href={"/docs/compilador/visualizar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
