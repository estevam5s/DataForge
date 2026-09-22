// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Busca",
  description: "Linear, binária e por hash — as três respostas para 'está aqui?', e o que cada uma exige.",
};

const blocos: Bloco[] = [
  {"p": "Procurar é a operação mais comum que existe, e há três formas com custos muito diferentes. A escolha depende de uma pergunta: **o que você sabe sobre os dados antes de procurar?**"},
  {"table": {"head": ["Forma", "Custo", "Exige"], "rows": [["percorrer (`x in lista`)", "O(n)", "nada"], ["binária (`busca_binaria`)", "O(log n)", "a lista **ordenada**"], ["hash (`x in set` / vault)", "O(1)", "valores imutáveis; memória extra"]]}},
  { code: `adopt Arcane.Algoritmos as Alg

ordenada := [2, 3, 5, 7, 11, 13, 17, 19, 23]
assert Alg.busca_binaria(ordenada, 13) is 5
assert Alg.busca_binaria(ordenada, 4) is -1
assert Alg.limite_inferior(ordenada, 4) is 2      // onde o 4 entraria

// Um milhao de itens: a binaria olha no maximo ~20.
xs := range(0, 1000000)
assert Alg.busca_binaria(xs, 765432) is 765432
out $"log2(1.000.000) = {round(log2(1000000), 1)} passos, no pior caso"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Binária numa lista desordenada responde errado — calada", "texto": "A busca binária não confere se a lista está ordenada: conferir custaria O(n), e ela existe para não gastar isso. Numa lista fora de ordem ela devolve `-1` para um valor que está lá. Ordene uma vez; procure muitas."}},
  {"h2": "Quando ordenar vale a pena"},
  {"p": "Ordenar custa O(n log n). Se você vai procurar **uma** vez, percorrer (O(n)) é mais barato. Se vai procurar **k** vezes, ordenar e usar binária custa O(n log n + k log n) contra O(k·n) — e para k grande, a diferença é de horas. E se não precisa de ordem, um `set` responde em O(1) sem ordenar nada."},
];

const headings = [{ id: 'quando-ordenar-vale-a-pena', text: "Quando ordenar vale a pena", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Busca"}
      description={"Linear, binária e por hash — as três respostas para 'está aqui?', e o que cada uma exige."}
      href={"/docs/big-o/busca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
