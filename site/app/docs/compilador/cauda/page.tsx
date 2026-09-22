// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Chamada de cauda",
  description: "yield f(…) vira salto, e a recursão perde o teto — com as quatro recusas que mantêm isso correto.",
};

const blocos: Bloco[] = [
  {"p": "Cada chamada de ação ocupa um quadro, e o teto é de mil quadros: uma recursão de cinco mil níveis estoura, mesmo sem nada de infinito. Mas quando a chamada é o **retorno inteiro** — `yield f(…)` —, não há nada a fazer depois dela, e o quadro só existiria para repassar o resultado. O compilador troca a chamada por um **salto**, reaproveitando o quadro."},
  { code: `action contar(n, acc := 0):
    given n is 0:
        yield acc
    yield contar(n - 1, acc + 1)           // cauda: nada depois dela

assert contar(200000) is 200000             // sem teto

action ingenua(n):
    given n is 0:
        yield 0
    yield 1 + ingenua(n - 1)               // NÃO é cauda: ainda falta somar 1

estourou := no
monitor:
    ingenua(5000)
handle StackOverflowError:
    estourou := yes
assert estourou`, lang: 'df' },
  {"h2": "As quatro recusas"},
  {"table": {"head": ["Não vira salto quando", "Porque"], "rows": [["há `defer` na ação", "ele roda na saída do quadro, e o salto reusa o quadro"], ["o `yield` está dentro de `monitor`", "o `handle` precisa ver o que a chamada levanta"], ["a recursão é indireta (`f` → `g` → `f`)", "a análise olha uma ação por vez"], ["**todo** `yield` da ação é cauda", "ela nunca devolveria: virar laço infinito calado seria pior que o erro"]]}},
  {"p": "A última é a mais importante: sem ela, `action r(n): yield r(n + 1)` deixaria de dar `StackOverflowError` e passaria a travar para sempre."},
];

const headings = [{ id: 'as-quatro-recusas', text: "As quatro recusas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Chamada de cauda"}
      description={"yield f(…) vira salto, e a recursão perde o teto — com as quatro recusas que mantêm isso correto."}
      href={"/docs/compilador/cauda"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
