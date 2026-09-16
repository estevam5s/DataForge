// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise amortizada",
  description: "Por que 'append' é O(1) mesmo custando O(n) de vez em quando — e as três formas de provar isso.",
};

const blocos: Bloco[] = [
  {"p": "`xs.append(x)` é `O(1)`. Só que de vez em quando ele **copia a lista inteira**, o que é `O(n)`. As duas frases são verdadeiras, e a análise amortizada é o que as concilia."},
  {"p": "A pergunta certa não é *quanto custa esta operação*, e sim **quanto custam n operações, divididas por n**. É a diferença entre a conta do mês e a conta do café."},
  {"h2": "O que acontece por dentro"},
  {"p": "Um cluster guarda um bloco de memória com espaço sobrando. Quando o espaço acaba, ele aloca um bloco **maior** — tipicamente o dobro — e copia o que havia. Essa cópia é a operação cara."},
  { code: `capacidade:  4        8              16                      32
append:      ····     ····****       ····****········        …
                 ↑            ↑                     ↑
              copia 4      copia 8              copia 16`, lang: 'text' },
  {"p": "A cópia acontece cada vez mais raramente, e é exatamente por isso que ela some na média."},
  {"h2": "A prova pela agregação"},
  {"p": "Some o custo de `n` appends. As cópias acontecem em 1, 2, 4, 8, …, até `n` — uma série geométrica:"},
  { code: `1 + 2 + 4 + 8 + … + n  <  2n`, lang: 'text' },
  {"p": "O total das cópias é **menor que `2n`**, e somado aos `n` appends dá menos de `3n`. Dividido por `n`: uma constante. Cada `append` custa `O(1)` **amortizado**."},
  {"h2": "A prova pela medição"},
  {"p": "A conta acima é verificável sem confiar em ninguém: se o total de `n` appends é linear, dobrar `n` tem de dobrar o tempo. Dobre quatro vezes e olhe a razão."},
  { code: `adopt Arcane.Time as T

action tempo_de_n_appends(n):
    inicio := T.monotonic()
    xs := []
    cycle i from 1 to n:
        xs.append(i)
    yield (T.monotonic() - inicio) * 1000

anterior := 0.0
cycle n in [100000, 200000, 400000, 800000]:
    ms := tempo_de_n_appends(n)
    razao := "—" given anterior is 0.0 otherwise $"{round(ms / anterior, 2)}x"
    out $"{str(n).pad_start(7)} appends  {str(round(ms, 1)).pad_start(7)} ms   {razao}"
    anterior := ms`, lang: 'df' },
  { code: ` 100000 appends     88.2 ms   —
 200000 appends    178.2 ms   2.02x
 400000 appends    360.1 ms   2.02x
 800000 appends    724.4 ms   2.01x`, lang: 'text', title: `saída (macOS, 10 núcleos)` },
  {"p": "**2,02x** três vezes seguidas. Se cada `append` fosse `O(n)`, dobrar `n` daria 4x; se as cópias não amortizassem, a razão subiria a cada linha. Ela não sobe."},
  {"callout": {"tipo": "dica", "titulo": "A razão, e não o tempo", "texto": "O número absoluto mede a sua máquina; a **razão entre dois tamanhos** mede o algoritmo. É por isso que os testes de complexidade deste repositório cobram fator, nunca milissegundos."}},
  {"h2": "As outras duas provas"},
  {"p": "A agregação responde \"quanto custa o total\". As outras duas respondem \"por que nunca falta\", e são o que se usa quando a estrutura é mais complicada que uma lista:"},
  {"table": {"head": ["Método", "A ideia", "Aplicado ao `append`"], "rows": [["**agregação**", "some tudo e divida por n", "menos de 3n para n appends"], ["**contábil**", "cobre a mais em cada operação barata e guarde o crédito", "cada append paga 3: um por si, dois guardados para a cópia futura"], ["**potencial**", "defina uma função Φ do estado; o custo amortizado é o real mais a variação de Φ", "Φ = 2 × (itens além da metade da capacidade)"]]}},
  {"p": "As três dão o mesmo resultado. A contábil é a mais fácil de explicar: quando o bloco de capacidade `k` enche, os `k` itens copiados já pagaram, cada um, os dois créditos que a cópia consome."},
  {"h2": "Amortizado não é o mesmo que médio"},
  {"table": {"head": ["", "Sobre o quê", "Quem garante"], "rows": [["**caso médio**", "uma distribuição de **entradas**", "a estatística — pode dar azar"], ["**amortizado**", "uma **sequência** de operações", "a álgebra — não tem azar"]]}},
  {"p": "O quicksort é `O(n log n)` no caso **médio** e `O(n²)` no pior: uma entrada infeliz custa caro. O `append` é `O(1)` **amortizado**: não existe sequência de appends que fuja disso. Ver [melhor, médio e pior](/docs/big-o/casos)."},
  {"h2": "Onde isso muda a decisão"},
  {"list": ["**Construir uma lista com `append` num laço é linear**, e não quadrático. A alternativa \"esperta\" — `saida := [...saida, x]` — **é** quadrática, porque copia a cada volta.", "**Num sistema de tempo real, o amortizado não basta.** A cópia acontece de verdade, e naquela volta o prazo estoura. Ali se pré-aloca.", "**Um vault tem a mesma história**, com um detalhe a mais: ele também cresce por realocação, e uma colisão ruim de chaves degrada a busca."]},
  { code: `// linear: cada append é O(1) amortizado
saida := []
cycle x in fonte:
    saida.append(x)

// quadrático: cada volta copia a lista inteira
saida := []
cycle x in fonte:
    saida := [...saida, x]`, lang: 'df' },
  {"p": "O `dataforge big-o` acusa o segundo — é o [padrão 4](/docs/big-o/padroes) da lista de armadilhas."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/estruturas", "title": "Custo das estruturas", "desc": "o que cada operação de cluster, vault e string custa"}, {"href": "/docs/big-o/casos", "title": "Melhor, médio e pior", "desc": "e por que o médio é o que se observa"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "quando o algoritmo pior no papel ganha na máquina"}]},
];

const headings = [{ id: 'o-que-acontece-por-dentro', text: "O que acontece por dentro", level: 2 as const }, { id: 'a-prova-pela-agregacao', text: "A prova pela agregação", level: 2 as const }, { id: 'a-prova-pela-medicao', text: "A prova pela medição", level: 2 as const }, { id: 'as-outras-duas-provas', text: "As outras duas provas", level: 2 as const }, { id: 'amortizado-nao-e-o-mesmo-que-medio', text: "Amortizado não é o mesmo que médio", level: 2 as const }, { id: 'onde-isso-muda-a-decisao', text: "Onde isso muda a decisão", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise amortizada"}
      description={"Por que 'append' é O(1) mesmo custando O(n) de vez em quando — e as três formas de provar isso."}
      href={"/docs/big-o/amortizada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
