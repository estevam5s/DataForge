// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/algoritmos.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Algoritmos",
  description: "Os algoritmos clássicos com a complexidade como dado: busca binária, merge sort estável, counting sort, BFS, DFS, ordem topológica que mostra o ciclo, Dijkstra que recusa peso negativo, LCS, Levenshtein, mochila 0/1, KMP e o crivo — cada um conferido contra uma implementação ingênua.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (16)"},
  {"table": {"head": ["Assinatura"], "rows": [["`bfs(grafo, origem)`"], ["`busca_binaria(xs, alvo)`"], ["`caminho(resultado, destino)`"], ["`catalogo()`"], ["`complexidade(nome)`"], ["`crivo(n)`"], ["`dfs(grafo, origem)`"], ["`dijkstra(grafo, origem)`"], ["`kmp(texto, padrao)`"], ["`lcs(a, b)`"], ["`levenshtein(a, b)`"], ["`limite_inferior(xs, alvo)`"], ["`mochila(itens, capacidade)`"], ["`ordem_topologica(grafo)`"], ["`ordenar_contando(xs)`"], ["`ordenar_mesclando(xs, chave=None)`"]]}},
];

const headings = [{ id: 'funcoes-16', text: "Funções (16)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Algoritmos"}
      description={"Os algoritmos clássicos com a complexidade como dado: busca binária, merge sort estável, counting sort, BFS, DFS, ordem topológica que mostra o ciclo, Dijkstra que recusa peso negativo, LCS, Levenshtein, mochila 0/1, KMP e o crivo — cada um conferido contra uma implementação ingênua."}
      href={"/docs/biblioteca/algoritmos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
