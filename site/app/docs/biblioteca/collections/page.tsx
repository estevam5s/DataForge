// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/collections.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Collections",
  description: "Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca.",
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
  {"h2": "Funções (63)"},
  {"table": {"head": ["Assinatura"], "rows": [["`add(conjunto, item)`"], ["`batched(itens, n)`"], ["`binary_search(ordenado, alvo)`"], ["`bottom_n(itens, n, chave=None)`"], ["`cartesian(a, b)`"], ["`chain_vaults(*vaults)`"], ["`chunk_evenly(itens, partes)`"], ["`counter(itens=None)`"], ["`deep_merge(a, b)`"], ["`default_vault(padrao=None)`"], ["`deque(itens=None, maximo=0)`"], ["`difference(a, b)`"], ["`discard(conjunto, item)`"], ["`elements(contagem)`"], ["`extend_left(fila, itens)`"], ["`first_key(v)`"], ["`flatten_deep(itens, profundidade=-1)`"], ["`frozen(itens)`"], ["`graph(dirigido=False)`"], ["`group(itens, chave)`"], ["`group_by(itens, chave)`"], ["`heap(itens=None)`"], ["`heap_peek(h)`"], ["`heap_pop(h)`"], ["`heap_push(h, item)`"], ["`index_by(itens, chave)`"], ["`intersection(a, b)`"], ["`is_disjoint(a, b)`"], ["`is_subset(a, b)`"], ["`is_superset(a, b)`"], ["`last_key(v)`"], ["`merge_sorted(a, b)`"], ["`most_common(fonte, n=0)`"], ["`move_to_end(v, chave, para_o_fim=True)`"], ["`n_largest(itens, n, chave=None)`"], ["`n_smallest(itens, n, chave=None)`"], ["`named(nome, campos, valores)`"], ["`ordered(pares=None)`"], ["`ordered_vault(pares=None)`"], ["`pairwise(itens)`"], ["`partition(itens, predicado)`"], ["`peek(fila)`"], ["`peek_left(fila)`"], ["`pop(fila)`"], ["`pop_left(fila)`"], ["`priority_queue()`"], ["`push(fila, item)`"], ["`push_left(fila, item)`"], ["`queue(itens=None)`"], ["`rotate(colecao, n=1)`"], ["`set(itens=None)`"], ["`sliding_window(itens, tamanho)`"], ["`sort_by(itens, chave)`"], ["`sort_by_field(itens, campo, reverso=False)`"], ["`stack(itens=None)`"], ["`subtract(a, b)`"], ["`symmetric_difference(a, b)`"], ["`top_n(itens, n, chave=None)`"], ["`total(contagem)`"], ["`union(a, b)`"], ["`union_find(itens=None)`"], ["`unique_by(itens, chave)`"], ["`zip_longest(a, b, preencher=None)`"]]}},
];

const headings = [{ id: 'funcoes-63', text: "Funções (63)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Collections"}
      description={"Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca."}
      href={"/docs/biblioteca/collections"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
