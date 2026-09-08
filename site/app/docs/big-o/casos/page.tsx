import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Melhor, médio e pior caso",
  description: "E a análise amortizada, que explica por que 'append' é O(1).",
};

const blocos: Bloco[] = [
  {"p": "Big-O sozinho é ambíguo: o quicksort é O(n²) e O(n log n) ao mesmo tempo, dependendo de qual caso se fala."},
  {"h2": "Os três casos"},
  { code: `action procurar(xs, alvo):
    cycle i, x in enumerate(xs):
        given x is alvo:
            yield i
    yield -1`, lang: 'df' },
  {"table": {"head": ["Caso", "Quando", "Custo"], "rows": [["melhor", "o alvo é o primeiro item", "O(1)"], ["médio", "o alvo está em posição qualquer", "O(n/2) = O(n)"], ["pior", "o alvo não existe", "O(n)"]]}},
  {"p": "Por convenção, **Big-O sem qualificação significa pior caso**. É o que dá garantia: o programa nunca vai custar mais que isso."},
  {"h2": "Quando o médio é o que importa"},
  {"table": {"head": ["Algoritmo", "Melhor", "Médio", "Pior"], "rows": [["busca linear", "O(1)", "O(n)", "O(n)"], ["busca binária", "O(1)", "O(log n)", "O(log n)"], ["quicksort", "O(n log n)", "O(n log n)", "**O(n²)**"], ["merge sort", "O(n log n)", "O(n log n)", "O(n log n)"], ["busca em vault", "O(1)", "O(1)", "**O(n)**"], ["bubble sort", "O(n)", "O(n²)", "O(n²)"]]}},
  {"p": "O quicksort é usado na prática apesar do pior caso O(n²), porque o médio é O(n log n) e a constante é menor que a do merge sort. O pior caso só aparece com entrada já ordenada e pivô mal escolhido."},
  {"p": "O vault é O(n) no pior caso — quando todas as chaves colidem. Na prática nunca acontece com uma função de espalhamento decente, e por isso se fala em O(1)."},
  {"h2": "Análise amortizada"},
  {"p": "`xs.append(x)` é O(1), mas nem sempre: quando o cluster enche, ele realoca e copia tudo, o que é O(n). Por que dizemos O(1)?"},
  {"p": "Porque a realocação **dobra** a capacidade. Partindo de 1, para chegar a n itens houve realocações em 1, 2, 4, 8, …, n — que somam menos de 2n cópias. Espalhando esse custo pelas n inserções, dá menos de 2 por inserção: **O(1) amortizado**."},
  { code: `// n appends custam O(n) no total, não O(n²)
action montar(n):
    saida := []
    cycle i from 1 to n:
        saida.append(i)
    yield saida

assert len(montar(1000)) is 1000`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Amortizado ≠ médio", "texto": "Médio é sobre a distribuição das entradas. Amortizado é uma garantia sobre uma *sequência* de operações, e vale mesmo no pior caso — não depende de sorte."}},
  {"h2": "Onde isso muda a decisão"},
  {"list": ["**Sistema de tempo real**: o pior caso é o que conta. Um O(1) amortizado com picos O(n) pode estourar o prazo.", "**Serviço web**: o percentil 95 é o que o usuário sente. Por isso `Crucible.benchmark` reporta p95, não só a média.", "**Processamento em lote**: o médio domina; picos ocasionais se diluem."]},
  {"p": "Ver [Crucible: benchmark](/docs/crucible/relatorios) para medir isso no seu código."},
];

const headings = [{ id: 'os-tres-casos', text: "Os três casos", level: 2 as const }, { id: 'quando-o-medio-e-o-que-importa', text: "Quando o médio é o que importa", level: 2 as const }, { id: 'analise-amortizada', text: "Análise amortizada", level: 2 as const }, { id: 'onde-isso-muda-a-decisao', text: "Onde isso muda a decisão", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Melhor, médio e pior caso"}
      description={"E a análise amortizada, que explica por que 'append' é O(1)."}
      href={"/docs/big-o/casos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
