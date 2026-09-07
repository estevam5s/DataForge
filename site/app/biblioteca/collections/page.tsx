import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Collections",
  description: "Pilha, fila, heap, grafo, união-busca e algoritmos.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Collections as Col

g := Col.graph()
g.add_edge("casa", "mercado", 3)
g.add_edge("mercado", "trabalho", 4)
g.add_edge("casa", "trabalho", 10)
out g.shortest_path("casa", "trabalho")

fila := Col.priority_queue()
fila.push("rotina", 5)
fila.push("urgente", 1)
out fila.pop()`, title: `exemplo` },
  {"p": "As estruturas são objetos com métodos próprios (`push`, `pop`, `add_edge`…), não vaults. Chame-os diretamente: `fila.push(x)`."},
  {"h2": "Funções (35)"},
  {"table": {"head": ["Assinatura"], "rows": [["`batched(itens, n)`"], ["`binary_search(ordenado, alvo)`"], ["`bottom_n(itens, n, chave=None)`"], ["`cartesian(a, b)`"], ["`chunk_evenly(itens, partes)`"], ["`counter(itens)`"], ["`deep_merge(a, b)`"], ["`default_vault(padrao=0)`"], ["`deque(itens=None, limite=None)`"], ["`difference(a, b)`"], ["`flatten_deep(itens, profundidade=-1)`"], ["`graph(dirigido=False)`"], ["`group_by(itens, chave)`"], ["`index_by(itens, chave)`"], ["`intersection(a, b)`"], ["`is_subset(a, b)`"], ["`merge_sorted(a, b)`"], ["`most_common(itens, n=1)`"], ["`ordered_vault(pares=None)`"], ["`pairwise(itens)`"], ["`partition(itens, predicado)`"], ["`priority_queue()`"], ["`queue(itens=None)`"], ["`rotate(itens, n)`"], ["`set(itens=None)`"], ["`sliding_window(itens, tamanho)`"], ["`sort_by(itens, chave)`"], ["`sort_by_field(itens, campo, reverso=False)`"], ["`stack(itens=None)`"], ["`symmetric_difference(a, b)`"], ["`top_n(itens, n, chave=None)`"], ["`union(a, b)`"], ["`union_find(itens=None)`"], ["`unique_by(itens, chave)`"], ["`zip_longest(a, b, preencher=None)`"]]}},
];

const headings = [{ id: 'funcoes-35', text: "Funções (35)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Collections"}
      description={"Pilha, fila, heap, grafo, união-busca e algoritmos."}
      href={"/biblioteca/collections"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
