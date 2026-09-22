// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "4. Decidir",
  description: "given, orif e otherwise — e as comparações que decidem.",
};

const blocos: Bloco[] = [
  {"p": "Decidir é fazer uma coisa **ou** outra dependendo de uma condição. Em DataForge: `given` (*se*), `orif` (*senão, se*) e `otherwise` (*senão*). O que está recuado embaixo de cada um só roda quando ele é escolhido."},
  { code: `nota := 7.5

given nota bigger_eq 9:
    conceito := "A"
orif nota bigger_eq 7:
    conceito := "B"
orif nota bigger_eq 5:
    conceito := "C"
otherwise:
    conceito := "D"

out $"nota {nota}: conceito {conceito}"
assert conceito is "B"`, lang: 'df' },
  {"h2": "As comparações"},
  {"table": {"head": ["Escreva", "Pergunta"], "rows": [["`a is b`", "são iguais?"], ["`a isnt b`", "são diferentes?"], ["`a bigger b` / `a smaller b`", "maior? menor?"], ["`a bigger_eq b` / `a smaller_eq b`", "maior ou igual? menor ou igual?"], ["`x in lista`", "está dentro?"], ["`c1 and c2` / `c1 or c2` / `not c`", "as duas? alguma? o contrário?"]]}},
  {"callout": {"tipo": "dica", "titulo": "A ordem dos `orif` importa", "texto": "O primeiro que for verdadeiro ganha, e os outros nem são olhados. Por isso a nota 9,5 cai em `A` e não em `B` — mesmo sendo, também, maior ou igual a 7."}},
  {"h2": "Numa linha só"},
  { code: `idade := 20
situacao := "maior" given idade bigger_eq 18 otherwise "menor"
assert situacao is "maior"`, lang: 'df' },
  {"p": "Próximo: [5. Repetir](/docs/primeiros-passos/repeticao)."},
];

const headings = [{ id: 'as-comparacoes', text: "As comparações", level: 2 as const }, { id: 'numa-linha-so', text: "Numa linha só", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"4. Decidir"}
      description={"given, orif e otherwise — e as comparações que decidem."}
      href={"/docs/primeiros-passos/decisoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
