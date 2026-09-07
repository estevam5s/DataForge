import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Precedência",
  description: "A ordem de avaliação dos operadores, do mais forte ao mais fraco.",
};

const blocos: Bloco[] = [
  {"table": {"head": ["Nível", "Operadores", "Associatividade"], "rows": [["1", "`()` `[]` `.` `?.` `with`", "esquerda"], ["2", "`**`", "**direita**"], ["3", "`-` `+` `not` (unários)", "direita"], ["4", "`*` `/` `%` `~/` `//`", "esquerda"], ["5", "`+` `-`", "esquerda"], ["6", "comparações, `in`, `not in`", "encadeável"], ["7", "`not`", "direita"], ["8", "`and`", "esquerda"], ["9", "`or`", "esquerda"], ["10", "`??`", "esquerda"], ["11", "`given … otherwise` (ternário)", "direita"], ["12", "`>>`", "esquerda"]]}},
  {"h2": "As consequências que surpreendem"},
  { code: `out 2 ** 3 ** 2    # 512, e não 64 — potência associa à direita
out -2 ** 2        # -4, e não 4 — o sinal aplica depois da potência
out 2 + 3 * 4      # 14` },
  {"h2": "Por que ** associa à direita"},
  {"p": "É a convenção matemática: 2³² significa 2^(3²) = 2⁹ = 512, não (2³)² = 64. Python, Ruby e Haskell fazem o mesmo."},
  {"h2": "Por que o unário vem depois"},
  {"p": "`-2 ** 2` é lido como `-(2 ** 2)`. Isso também segue a matemática: −2² é −4. Para elevar o negativo, use parênteses: `(-2) ** 2` dá 4."},
  {"h2": "O pipeline é o mais fraco"},
  {"p": "Por isso `nums >> sift n: n % 2 is 0` funciona sem parênteses: a expressão inteira `n % 2 is 0` é avaliada antes que o `>>` entre em ação."},
];

const headings = [{ id: 'as-consequencias-que-surpreendem', text: "As consequências que surpreendem", level: 2 as const }, { id: 'por-que--associa-a-direita', text: "Por que ** associa à direita", level: 2 as const }, { id: 'por-que-o-unario-vem-depois', text: "Por que o unário vem depois", level: 2 as const }, { id: 'o-pipeline-e-o-mais-fraco', text: "O pipeline é o mais fraco", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Precedência"}
      description={"A ordem de avaliação dos operadores, do mais forte ao mais fraco."}
      href={"/docs/referencia/precedencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
