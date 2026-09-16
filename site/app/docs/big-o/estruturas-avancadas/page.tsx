// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Estruturas avançadas",
  description: "Heap, união-busca, deque e contador — o que cada uma custa, e o problema que só ela resolve bem.",
};

const blocos: Bloco[] = [
  {"p": "Cluster e vault resolvem quase tudo. As quatro estruturas desta página existem para os casos em que eles obrigam a pagar `O(n)` por algo que podia ser `O(log n)` ou `O(1)` — e todas já vêm em [`Arcane.Collections`](/docs/biblioteca/collections)."},
  {"h2": "Heap — o menor primeiro, em `O(log n)`"},
  {"p": "Uma fila de prioridade. O que ela dá, e o cluster não: inserir e tirar o menor mantendo a ordem **sem ordenar a lista inteira**."},
  { code: `adopt Arcane.Collections as C

h := C.heap([5, 1, 9, 3])
C.heap_push(h, 2)
out C.heap_peek(h)     // 1  — o menor, sem remover
out C.heap_pop(h)      // 1
out C.heap_pop(h)      // 2`, lang: 'df' },
  {"table": {"head": ["Operação", "Heap", "Cluster ordenado", "Cluster solto"], "rows": [["ver o menor", "`O(1)`", "`O(1)`", "`O(n)`"], ["tirar o menor", "`O(log n)`", "`O(n)` (desloca)", "`O(n)`"], ["inserir", "`O(log n)`", "`O(n)` (desloca)", "`O(1)`"], ["montar de uma lista", "`O(n)`", "`O(n log n)`", "`O(1)`"]]}},
  {"h3": "Onde isso decide: os k maiores"},
  {"p": "Ordenar tudo para pegar 10 é `O(n log n)`. Um heap de tamanho 10 é `O(n log k)` — e com k pequeno, `log k` é praticamente uma constante:"},
  { code: `adopt Arcane.Collections as C
adopt Arcane.Time as T

dados := [randint(1, 1000000) cycle i in range(0, 300000)]

inicio := T.monotonic()
maiores_a := sorted(dados)[len(dados) - 10:]
ms_sort := (T.monotonic() - inicio) * 1000

inicio := T.monotonic()
maiores_b := C.top_n(dados, 10)
ms_heap := (T.monotonic() - inicio) * 1000

out $"ordenar tudo e cortar 10:  {round(ms_sort, 1)} ms"
out $"top_n com heap de 10:      {round(ms_heap, 1)} ms"
`, lang: 'df' },
  { code: `ordenar tudo e cortar 10:  25.7 ms
top_n com heap de 10:      1.7 ms`, lang: 'text', title: `saída (300 mil itens)` },
  {"p": "**15x**, e a distância cresce com `n`. `C.top_n` e `C.bottom_n` fazem isso; `C.priority_queue` é o mesmo mecanismo com prioridade explícita, que é como se escreve um Dijkstra ou um escalonador."},
  {"h2": "União-busca — \"estes dois estão no mesmo grupo?\""},
  {"p": "O problema: juntar elementos em grupos e perguntar se dois estão juntos. Com listas, cada pergunta varre tudo; a união-busca responde em tempo **quase constante**."},
  { code: `adopt Arcane.Collections as C

uf := C.union_find(["a", "b", "c", "d"])
uf.union("a", "b")
uf.union("c", "d")
out uf.connected("a", "b")     // yes
out uf.connected("a", "c")     // no
out uf.count()                 // 2 grupos`, lang: 'df' },
  {"table": {"head": ["Operação", "Custo"], "rows": [["`union(a, b)`", "`O(log n)` amortizado"], ["`connected(a, b)`", "`O(log n)` amortizado"], ["`count()`", "`O(n)`"], ["`groups()`", "`O(n)`"]]}},
  {"p": "A compressão de caminho é o que dá o amortizado: cada busca **achata** a árvore que percorreu, e a próxima passa direto. É o mesmo raciocínio da [análise amortizada](/docs/big-o/amortizada) do `append` — a operação cara paga pelas baratas que vêm depois."},
  {"p": "Serve para componentes conexos de um grafo, para detectar ciclo ao montar uma árvore geradora mínima, e para agrupar duplicatas — \"este e-mail e este telefone são da mesma pessoa\"."},
  {"h2": "Deque — as duas pontas em `O(1)`"},
  {"p": "Um cluster é `O(1)` no fim e `O(n)` no começo: inserir na posição 0 empurra todo o resto. O deque é `O(1)` nas duas pontas."},
  { code: `adopt Arcane.Collections as C

d := C.deque([1, 2, 3])
C.push_left(d, 0)
out C.pop_left(d)     // 0
out C.pop(d)          // 3
out len(d)            // 2`, lang: 'df' },
  {"table": {"head": ["Operação", "Deque", "Cluster"], "rows": [["no fim (push/pop)", "`O(1)`", "`O(1)`"], ["no começo (push/pop)", "`O(1)`", "**`O(n)`**"], ["por índice, no meio", "`O(n)`", "`O(1)`"]]}},
  {"p": "A troca é clara: o deque ganha nas pontas e perde no acesso indexado. Use-o para fila (BFS, produtor-consumidor) e janela deslizante; para acesso aleatório, cluster."},
  {"h2": "Contador — contar sem laço aninhado"},
  {"p": "Contar ocorrências percorrendo e comparando é `O(n²)`. Com um vault de contagem é `O(n)`, e o `counter` é isso pronto:"},
  { code: `adopt Arcane.Collections as C

palavras := ["a", "b", "a", "c", "a"]
out C.counter(palavras)                  // {a: 3, b: 1, c: 1}
out C.most_common(palavras, 2)           // [[a, 3], [b, 1]]`, lang: 'df' },
  {"p": "`most_common(n)` usa heap por dentro: `O(n log k)`, não `O(n log n)`. As duas ideias desta página juntas."},
  {"h2": "Escolhendo em trinta segundos"},
  {"table": {"head": ["A pergunta que você faz muitas vezes", "A estrutura"], "rows": [["\"este item está aqui?\"", "**vault** — `O(1)`"], ["\"qual é o menor/maior agora?\"", "**heap** — `O(log n)`"], ["\"os k maiores de muitos\"", "**heap** (`top_n`) — `O(n log k)`"], ["\"estes dois estão no mesmo grupo?\"", "**união-busca** — quase `O(1)`"], ["\"o primeiro da fila\"", "**deque** — `O(1)`"], ["\"quantas vezes cada um aparece?\"", "**counter** — `O(n)`"], ["\"o item da posição i\"", "**cluster** — `O(1)`"], ["\"está ordenado? onde entra este?\"", "**cluster ordenado** + `binary_search` — `O(log n)`"]]}},
  {"callout": {"tipo": "dica", "titulo": "A troca é sempre a mesma", "texto": "Toda estrutura desta página acelera **uma** pergunta e desacelera outra. Escolher bem é saber qual pergunta o seu código faz num laço — e essa é a que o `dataforge big-o` aponta."}},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/estruturas", "title": "Custo das estruturas", "desc": "cluster, vault e string, operação por operação"}, {"href": "/docs/big-o/amortizada", "title": "Análise amortizada", "desc": "de onde vem o 'amortizado' da união-busca"}, {"href": "/docs/biblioteca/collections", "title": "Arcane.Collections", "desc": "a referência completa do módulo"}]},
];

const headings = [{ id: 'heap-o-menor-primeiro-em-olog-n', text: "Heap — o menor primeiro, em `O(log n)`", level: 2 as const }, { id: 'onde-isso-decide-os-k-maiores', text: "Onde isso decide: os k maiores", level: 3 as const }, { id: 'uniao-busca-estes-dois-estao-no-mesmo-grupo', text: "União-busca — \"estes dois estão no mesmo grupo?\"", level: 2 as const }, { id: 'deque-as-duas-pontas-em-o1', text: "Deque — as duas pontas em `O(1)`", level: 2 as const }, { id: 'contador-contar-sem-laco-aninhado', text: "Contador — contar sem laço aninhado", level: 2 as const }, { id: 'escolhendo-em-trinta-segundos', text: "Escolhendo em trinta segundos", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Estruturas avançadas"}
      description={"Heap, união-busca, deque e contador — o que cada uma custa, e o problema que só ela resolve bem."}
      href={"/docs/big-o/estruturas-avancadas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
