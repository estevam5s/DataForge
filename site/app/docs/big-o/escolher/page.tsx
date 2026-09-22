// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escolher a estrutura",
  description: "Uma tabela de decisão: a pergunta que o código faz mais vezes decide a estrutura.",
};

const blocos: Bloco[] = [
  {"p": "A estrutura certa não é a *“mais rápida”*: é a que responde barato **a pergunta que o código faz mais vezes**. Um vault é ótimo para *“quanto vale esta chave?”* e péssimo para *“qual é o menor?”*."},
  {"table": {"head": ["A pergunta frequente", "Estrutura", "Custo"], "rows": [["*está aqui?*", "`Set`", "O(1)"], ["*quanto vale esta chave?*", "`Vault`", "O(1)"], ["*qual é o i-ésimo?*", "`Cluster`", "O(1)"], ["*qual é o menor agora?* (e tirar)", "heap — `Collections.heap_*`", "O(log n)"], ["*o primeiro que chegou?*", "fila — `Collections.deque`", "O(1) nas duas pontas"], ["*em que posição entraria?* (ordenado)", "`Cluster` ordenado + `limite_inferior`", "O(log n)"], ["*estes dois estão no mesmo grupo?*", "`Collections.union_find`", "≈ O(1)"], ["*qual o caminho entre dois pontos?*", "grafo (vault de listas)", "O((V + E) log V)"]]}},
  { code: `adopt Arcane.Collections as C

// O menor, repetidas vezes: heap.
fila := C.heap([5, 1, 9, 3])       // devolve a fila; nao muda a lista
assert C.heap_pop(fila) is 1
assert C.heap_pop(fila) is 3

// Duplicatas: set.
vistos := set()
duplicados := []
cycle email in ["a@x", "b@x", "a@x"]:
    given email in vistos:
        duplicados.append(email)
    vistos.add(email)
assert duplicados is ["a@x"]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`in` numa lista dentro de um laço", "texto": "É o O(n²) mais comum que existe: `cycle x in a: given x in b:` com `b` lista percorre `b` inteira a cada volta. Trocar `b` por `set(b)` — uma linha — muda a classe para O(n)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Escolher a estrutura"}
      description={"Uma tabela de decisão: a pergunta que o código faz mais vezes decide a estrutura."}
      href={"/docs/big-o/escolher"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
