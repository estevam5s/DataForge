// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Onde a leitura engana",
  description: "As seis construções que o parser lê de um jeito e quem escreve lê de outro.",
};

const blocos: Bloco[] = [
  {"p": "Uma gramática sem ambiguidade para o parser ainda pode ser ambígua para quem lê. Estas são as seis que mais custam tempo — cada uma com a forma certa, que roda."},
  {"table": {"head": ["Parece", "O parser lê", "Escreva"], "rows": [["`x // nota`", "comentário", "`x ~/ 2` para dividir"], ["`lambda => xs >> morph x: x * 2`", "o pipeline aplicado ao **lambda**", "`lambda => (xs >> morph x: x * 2)`"], ["`morph n: n given c otherwise 0`", "o `given` abre uma instrução", "`morph n: (n given c otherwise 0)`"], ["`distill a, v: a + v 0 / len(x)`", "o inicial é `0 / len(x)`", "divida **depois**: `(xs >> distill a, v: a + v 0) / len(x)`"], ["`spawn B().f()`", "`(spawn B()).f()`", "é o que se quer — e era o contrário antes"], ["`$\"{v[\\\"id\\\"]}\"`", "interpolação que não termina", "`$\"{v[\"id\"]}\"` — aspas normais dentro de `{}`"]]}},
  { code: `xs := [1, 2, 3]
dobro := lambda => (xs >> morph x: x * 2)
assert dobro() is [2, 4, 6]

sinais := xs >> morph n: (n given n bigger 1 otherwise 0)
assert sinais is [0, 2, 3]

media := (xs >> distill a, v: a + v 0) / len(xs)
assert media is 2.0

v := {"id": 7}
assert $"item {v["id"]}" is "item 7"
assert 7 ~/ 2 is 3
out "as seis formas certas rodam"`, lang: 'df' },
  {"p": "Quando a dúvida é *como isto foi lido*, `dataforge tokens` e `dataforge ast` respondem na hora — ver [tokens, ast, ir](/docs/cli/internos)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Onde a leitura engana"}
      description={"As seis construções que o parser lê de um jeito e quem escreve lê de outro."}
      href={"/docs/referencia/gramatica/ambiguidades"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
