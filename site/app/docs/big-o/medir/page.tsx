// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Medir a curva",
  description: "Bench.curva e Bench.classe — a classe MEDIDA, com a honestidade de dizer quando a medida não separa duas.",
};

const blocos: Bloco[] = [
  {"p": "A análise diz a classe **esperada**; a medida diz a **real**. Dobrar o `n` e ver quanto o tempo cresce responde qual curva descreve o código — um fator ~2 é linear, ~4 é quadrático, pouco mais que 2 é n log n."},
  { code: `adopt Arcane.Bench as B

r := B.curva(lambda n: sum(range(0, n)), [20000, 40000, 80000])
cycle p in r["pontos"]:
    out $"n = {p['n']}: {p['ms']} ms"
out $"fator ao dobrar: {r['fator']}"

c := B.classe(lambda xs: sorted(xs), [4000, 8000, 16000],
    lambda n: range(n, 0, -1))
out $"classe medida: {c['classe']} ({c['certeza']}, candidatas {c['classes']})"
assert c["classe"] in ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A medida pode não separar duas classes — e diz isso", "texto": "O(n) e O(n log n) dão fatores parecidos ao dobrar o n (2,0 contra ~2,1). Quando a amostra cabe nas duas, `classe` devolve as duas em `classes` e `certeza` *“entre duas”*: dizer `O(n)` sobre uma medida que também cabe em `O(n log n)` seria inventar precisão."}},
  {"table": {"head": ["Regra da medida", "Porque"], "rows": [["compare **fatores**, nunca milissegundos", "o número absoluto mede a máquina"], ["use tamanhos grandes o bastante", "com n pequeno, o custo fixo do interpretador domina tudo"], ["prepare a entrada fora do cronômetro", "`preparar` gera os dados; senão mede-se a geração"], ["repita e fique com o menor", "o `Bench` já faz: o menor tempo é o menos perturbado"]]}},
  { code: `dataforge big-o src/ -v          # a classe estimada, sem rodar
dataforge big-o src/ --medir     # e a medida, lado a lado`, lang: 'bash' },
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Medir a curva"}
      description={"Bench.curva e Bench.classe — a classe MEDIDA, com a honestidade de dizer quando a medida não separa duas."}
      href={"/docs/big-o/medir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
