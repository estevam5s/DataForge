// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Imutabilidade",
  description: "steady, record, freeze e tupla — o que muda, o que não muda, e por que isso importa.",
};

const blocos: Bloco[] = [
  {"p": "Um valor que não muda pode ser passado para qualquer lugar sem medo: ninguém o altera pelas suas costas. A linguagem tem quatro formas de dizer *“isto não muda”*, e cada uma vale para uma coisa."},
  {"table": {"head": ["Forma", "O que não muda"], "rows": [["`steady NOME := …`", "o **nome**: não recebe outro valor"], ["`record`", "os **campos**: `p.x := 1` é erro; `p with {…}` devolve outro"], ["`freeze(xs)`", "a **lista**: vira uma sequência que não aceita `append`"], ["`(1, \"a\")`", "a **tupla**: uma forma fixa, com um tipo por posição"]]}},
  { code: `record Pedido:
    id: Integer
    total: Float

p := Pedido(1, 100.0)
p2 := p with {"total": 90.0}
assert p.total is 100.0 and p2.total is 90.0      // o original ficou

monitor:
    p.total := 0.0
    assert no
handle Error as e:
    out "record e imutavel:", e.type

congelada := freeze([1, 2, 3])
monitor:
    congelada.append(4)
    assert no
handle Error:
    out "a lista congelada nao aceita append"
assert thaw(congelada) is [1, 2, 3]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`steady` protege o nome, não o conteúdo", "texto": "`steady XS := [1, 2]` impede `XS := outra`, mas **não** impede `XS.append(3)`: a lista continua mutável. Para uma constante que não muda de verdade, `steady XS := freeze([1, 2])`."}},
  {"p": "Continue em [Records](/docs/fundamentos/records) e [Tuplas](/docs/tipos/tuplas)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Imutabilidade"}
      description={"steady, record, freeze e tupla — o que muda, o que não muda, e por que isso importa."}
      href={"/docs/fundamentos/imutabilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
