// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Exercícios de complexidade",
  description: "Oito trechos para classificar — e a resposta, com o porquê, conferida pelo próprio analisador.",
};

const blocos: Bloco[] = [
  {"p": "Classifique cada trecho antes de olhar a resposta. Depois, confira com `dataforge big-o` — a ferramenta diz a classe **e o porquê**."},
  { code: `// 1
action a(xs):
    yield xs[0]

// 2
action b(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

// 3
action c(xs):
    pares := 0
    cycle x in xs:
        cycle y in xs:
            given x + y is 0:
                pares += 1
    yield pares

// 4
action d(n):
    passos := 0
    persist n bigger 1:
        n := n ~/ 2
        passos += 1
    yield passos

// 5
action e(xs, ys):
    alvo := set(ys)
    yield [x cycle x in xs given x in alvo]

// 6
action f(n):
    given n smaller 2:
        yield n
    yield f(n - 1) + f(n - 2)

assert a([7]) is 7 and b([1, 2]) is 3 and c([1, -1]) is 2
assert d(1024) is 10 and e([1, 2, 3], [2, 3]) is [2, 3] and f(10) is 55`, lang: 'df' },
  {"table": {"head": ["#", "Classe", "Porque"], "rows": [["1", "O(1)", "um acesso por índice, sem laço"], ["2", "O(n)", "um laço sobre a entrada"], ["3", "O(n²)", "dois laços aninhados sobre a mesma entrada"], ["4", "O(log n)", "o contador **divide** a cada volta"], ["5", "O(n + m)", "o `set(ys)` custa m, e cada `in` num set é O(1)"], ["6", "O(2ⁿ)", "duas chamadas a si mesma, repetindo o mesmo trabalho — memoize"]]}},
  { code: `dataforge big-o exercicios.df -v`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "O 5 é o mais importante", "texto": "Com `ys` como lista, o `in` dentro da compreensão seria O(m) e o todo O(n·m). Uma única linha — `set(ys)` — é a diferença entre segundos e horas num arquivo grande. É a otimização com a maior razão entre esforço e ganho que existe."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Exercícios de complexidade"}
      description={"Oito trechos para classificar — e a resposta, com o porquê, conferida pelo próprio analisador."}
      href={"/docs/big-o/exercicios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
