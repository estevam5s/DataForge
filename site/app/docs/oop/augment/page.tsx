// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "augment",
  description: "Acrescentar membros a um blueprint que já existe — sem substituir nada, sem atravessar final nem sealed.",
};

const blocos: Bloco[] = [
  {"p": "`augment` é a extensão de um tipo sem herança: métodos, propriedades, operadores e estáticos novos num blueprint que já existe — e nos objetos que já foram criados. É o que outras linguagens chamam de método de extensão ou classe parcial."},
  { code: `blueprint Dinheiro(centavos):
    action reais():
        yield self.centavos / 100

carteira := spawn Dinheiro(1250)

augment Dinheiro:
    get texto():
        yield $"R$ {self.reais():.2f}"
    operator + (outro):
        yield spawn Dinheiro(self.centavos + outro.centavos)

assert carteira.texto is "R$ 12.50"               // o objeto de antes ganhou
assert (carteira + spawn Dinheiro(50)).centavos is 1300`, lang: 'df' },
  {"h2": "O que augment recusa"},
  {"table": {"head": ["Tentativa", "Por quê"], "rows": [["substituir um membro que existe", "substituir é o papel da herança; um augment que troca comportamento de longe é impossível de depurar"], ["augment de `final blueprint`", "final promete que o tipo está completo"], ["augment de `sealed` de outro arquivo", "sealed promete que a família é conhecida"], ["acrescentar campo de instância", "os objetos que já existem não o teriam"], ["ver `private` de outro arquivo", "augment não pode ser a porta dos fundos para o que o autor fechou"]]}},
];

const headings = [{ id: 'o-que-augment-recusa', text: "O que augment recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"augment"}
      description={"Acrescentar membros a um blueprint que já existe — sem substituir nada, sem atravessar final nem sealed."}
      href={"/docs/oop/augment"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
