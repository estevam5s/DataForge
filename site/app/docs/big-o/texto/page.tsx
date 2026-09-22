// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Texto e números",
  description: "KMP acha um padrão em O(n + m); o crivo acha os primos em O(n log log n).",
};

const blocos: Bloco[] = [
  {"p": "Procurar um padrão num texto parece O(n·m) — para cada posição, comparar o padrão inteiro. O KMP não volta atrás no texto: ele pré-calcula, a partir do padrão, onde recomeçar quando a comparação falha."},
  { code: `adopt Arcane.Algoritmos as Alg

dna := "ACGTACGTTACGTACGA"
assert Alg.kmp(dna, "ACGTA") is [0, 9]          // todas as posicoes
assert Alg.kmp("aaaa", "aa") is [0, 1, 2]       // sobrepostas tambem

// O crivo de Eratostenes: riscar os multiplos em vez de testar cada numero.
primos := Alg.crivo(50)
assert primos is [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
assert len(Alg.crivo(100000)) is 9592`, lang: 'df' },
  {"table": {"head": ["Tarefa", "Ingênuo", "Com o algoritmo"], "rows": [["achar um padrão de m letras num texto de n", "O(n·m)", "O(n + m) — `kmp`"], ["os primos até n", "O(n·√n) testando cada um", "O(n log log n) — `crivo`"]]}},
  {"callout": {"tipo": "dica", "titulo": "E o `in` do texto?", "texto": "`\"ACGTA\" in dna` usa o algoritmo do próprio Python, rápido na prática. O KMP vale quando se quer **todas** as posições, ou quando o padrão é longo e repetitivo — o pior caso do ingênuo."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Texto e números"}
      description={"KMP acha um padrão em O(n + m); o crivo acha os primos em O(n log log n)."}
      href={"/docs/big-o/texto"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
