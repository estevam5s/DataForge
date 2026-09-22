// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os clássicos, prontos",
  description: "Arcane.Algoritmos — catorze algoritmos com a complexidade declarada, e conferidos contra a versão ingênua.",
};

const blocos: Bloco[] = [
  {"p": "Entender por que um Dijkstra é O((V + E) log V) é uma coisa; escrevê-lo certo às três da manhã é outra. `Arcane.Algoritmos` traz os clássicos prontos, e cada um responde a sua complexidade **como dado** — e é testado contra a versão óbvia e lenta, em centenas de entradas sorteadas."},
  { code: `adopt Arcane.Algoritmos as Alg

cycle a in Alg.catalogo():
    out $"{a['nome'].pad_end(18)} {a['tempo'].pad_end(16)} {a['nota']}"

assert Alg.complexidade("dijkstra")["tempo"] is "O((V + E) log V)"
assert len(Alg.catalogo()) is 14`, lang: 'df' },
  {"table": {"head": ["Família", "Algoritmos", "Página"], "rows": [["busca", "`busca_binaria`, `limite_inferior`", "[Busca](/docs/big-o/busca)"], ["ordenação", "`ordenar_mesclando`, `ordenar_contando`", "[Ordenação](/docs/big-o/ordenacao)"], ["grafos", "`bfs`, `dfs`, `ordem_topologica`, `dijkstra`, `caminho`", "[Grafos](/docs/big-o/grafos)"], ["programação dinâmica", "`lcs`, `levenshtein`, `mochila`", "[Programação dinâmica](/docs/big-o/programacao-dinamica)"], ["texto e números", "`kmp`, `crivo`", "[Texto](/docs/big-o/texto)"]]}},
  {"callout": {"tipo": "dica", "titulo": "Por que conferido contra a versão ingênua", "texto": "Testar um algoritmo com os exemplos que o autor escolheu prova pouco: são os casos em que ele pensou. Cada um aqui é comparado com a forma óbvia (Floyd-Warshall para o Dijkstra, força bruta para a mochila, recursão para o Levenshtein) sobre entradas sorteadas com semente fixa — ver `tests/test_algoritmos.py`."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Os clássicos, prontos"}
      description={"Arcane.Algoritmos — catorze algoritmos com a complexidade declarada, e conferidos contra a versão ingênua."}
      href={"/docs/big-o/algoritmos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
