// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Grafos",
  description: "BFS, DFS, ordem topológica e Dijkstra — O(V + E) e O((V + E) log V), e o que cada um responde.",
};

const blocos: Bloco[] = [
  {"p": "Um grafo é qualquer coisa que se conecta: ruas, dependências, amizades, tarefas. Quatro algoritmos respondem quase toda pergunta sobre eles, e o formato é o que um JSON já traz — um vault de listas."},
  { code: `adopt Arcane.Algoritmos as Alg

// Sem peso: quem depende de quem.
tarefas := {
    "cafe": ["xicara", "agua"],
    "agua": ["ferver"],
    "xicara": [],
    "ferver": []}
ordem := Alg.ordem_topologica(tarefas)
assert ordem[0] is "cafe"

amigos := {"ana": ["bia"], "bia": ["caio"], "caio": ["davi"], "eva": []}
assert Alg.bfs(amigos, "ana")["davi"] is 3       // tres apertos de mao
assert Alg.dfs(amigos, "ana") is ["ana", "bia", "caio", "davi"]

// Com peso: o menor caminho.
mapa := {"centro": [["norte", 4], ["sul", 2]], "sul": [["norte", 1]], "norte": []}
r := Alg.dijkstra(mapa, "centro")
assert r["distancia"]["norte"] is 3
assert Alg.caminho(r, "norte") is ["centro", "sul", "norte"]
assert Alg.caminho(r, "lugar-nenhum") is void`, lang: 'df' },
  {"table": {"head": ["Pergunta", "Algoritmo", "Custo"], "rows": [["a menor distância em **passos**", "`bfs`", "O(V + E)"], ["tudo que se alcança", "`dfs`", "O(V + E)"], ["uma ordem que respeite as dependências", "`ordem_topologica`", "O(V + E)"], ["o menor caminho com **peso**", "`dijkstra` + `caminho`", "O((V + E) log V)"]]}},
  {"h2": "Os dois erros que ele recusa"},
  { code: `adopt Arcane.Algoritmos as Alg

monitor:
    Alg.ordem_topologica({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert no
handle Error as e:
    out e.message                 // mostra o ciclo: a → b → c → a

monitor:
    Alg.dijkstra({"a": [["b", -2]]}, "a")
    assert no
handle Error as e:
    out e.message                 // Dijkstra nao aceita peso negativo`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Peso negativo não dá erro no Dijkstra ingênuo — dá resposta errada", "texto": "O algoritmo assume que um caminho nunca fica mais barato ao ficar mais longo. Com peso negativo isso é falso, e ele devolve um caminho que não é o menor, com toda a confiança. Aqui ele recusa antes; para peso negativo, o algoritmo é Bellman-Ford."}},
];

const headings = [{ id: 'os-dois-erros-que-ele-recusa', text: "Os dois erros que ele recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Grafos"}
      description={"BFS, DFS, ordem topológica e Dijkstra — O(V + E) e O((V + E) log V), e o que cada um responde."}
      href={"/docs/big-o/grafos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
