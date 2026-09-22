// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Planejador de rotas",
  description: "Menor caminho com Dijkstra, o caminho reconstruído e o bairro inalcançável tratado.",
};

const blocos: Bloco[] = [
  {"p": "Grafo é o modelo de tudo que se conecta: ruas, dependências, redes. O planejador de rotas é o exemplo clássico porque tem as três armadilhas de todo algoritmo de grafo — o nó sem saída, o caminho que precisa ser reconstruído e não só medido, e o peso que não pode ser negativo."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["vault de listas", "o grafo como lista de adjacência"], ["Dijkstra", "menor distância a partir de uma origem"], ["`anterior`", "reconstruir o caminho, e não só o custo"], ["`void`", "o destino que não se alcança"]]}},
  {"h2": "Estrutura"},
  { code: `rotas/
  src/
    grafo.df       ligar, vizinhos
    dijkstra.df    menor_caminho
  tests/`, lang: 'text' },
  { code: `[project]
name = "rotas"
version = "0.1.0"
description = "Planejador de rotas"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `MAPA := {
    "centro": [["norte", 4], ["sul", 2]],
    "sul": [["norte", 1], ["leste", 7]],
    "norte": [["leste", 3]],
    "leste": [],
    "ilha": []
}

action menor_caminho(grafo, origem, destino):
    dist := {}
    anterior := {}
    visitados := []
    cycle n in grafo.keys():
        dist[n] := INF
    dist[origem] := 0
    persist yes:
        atual := void
        cycle n in grafo.keys():
            given n not in visitados and dist[n] isnt INF:
                given atual is void or dist[n] smaller dist[atual]:
                    atual := n
        given atual is void or atual is destino:
            halt
        visitados.append(atual)
        cycle aresta in grafo[atual]:
            vizinho, peso := aresta
            given peso smaller 0:
                trigger "Dijkstra nao aceita peso negativo"
            given dist[atual] + peso smaller dist[vizinho]:
                dist[vizinho] := dist[atual] + peso
                anterior[vizinho] := atual
    given dist[destino] is INF:
        yield void
    caminho := [destino]
    persist caminho[0] is not origem:
        caminho := [anterior[caminho[0]], ...caminho]
    yield {"custo": dist[destino], "caminho": caminho}

r := menor_caminho(MAPA, "centro", "leste")
out r
assert r["custo"] is 6
assert r["caminho"] is ["centro", "sul", "norte", "leste"]
assert menor_caminho(MAPA, "centro", "ilha") is void`, lang: 'df', title: `src/dijkstra.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/dijkstra as D

crucible "rotas":
    trial "a origem chega nela mesma com custo zero":
        expect D.menor_caminho(D.MAPA, "sul", "sul")["custo"] is 0`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["guardar `anterior`", "o programa diz *“6 km”* e não diz por onde"], ["`void` para o inalcançável", "o custo sai `INF` e alguém soma isso a um preço"], ["recusar peso negativo", "Dijkstra devolve um caminho errado com toda a confiança"], ["o grafo é dado", "trocar o mapa exige mexer no algoritmo"]]}},
  {"h2": "Para ir além"},
  {"list": ["Com milhares de nós, troque a busca linear do menor por uma fila de prioridade.", "Peso negativo exige Bellman-Ford.", "Meça a classe: `dataforge big-o src/dijkstra.df`."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Planejador de rotas"}
      description={"Menor caminho com Dijkstra, o caminho reconstruído e o bairro inalcançável tratado."}
      href={"/docs/projetos/rotas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
