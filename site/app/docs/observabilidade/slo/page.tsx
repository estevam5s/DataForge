// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "SLO e orçamento de erro",
  description: "99,9% é uma promessa com uma sobra: as falhas que ela permite. O orçamento transforma 'dá para arriscar?' em conta.",
};

const blocos: Bloco[] = [
  {"p": "Um **SLO** (objetivo de nível de serviço) diz quanto do tempo o serviço precisa estar certo — 99,9% dos pedidos respondidos com sucesso, por exemplo. O que sobra, 0,1%, é o **orçamento de erro**: as falhas que o objetivo permite. Com um milhão de pedidos, mil podem falhar."},
  { code: `adopt Arcane.Observar as O

o := O.orcamento(0.999, 1000000, 400)
assert o["permitidas"] is 1000.0
assert o["consumido"] is 0.4            // quarenta por cento já foi
assert o["restante"] is 0.6
assert not o["esgotado"]

apertado := O.orcamento(0.999, 1000000, 1200)
assert apertado["esgotado"]             // passou do combinado`, lang: 'df' },
  {"h2": "O que o orçamento decide"},
  {"table": {"head": ["Restante", "O time"], "rows": [["muito", "pode arriscar: deploy na sexta, migração, experimento"], ["pouco", "desacelera: só correção, com mais revisão"], ["esgotado", "congela o que não é confiabilidade, até o orçamento voltar"]]}},
  {"p": "É isso que o torna útil: a discussão \"este deploy é seguro?\" deixa de ser opinião contra opinião e passa a ser uma conta que os dois lados aceitaram antes."},
  {"h2": "A taxa de queima"},
  {"p": "O orçamento diz **quanto** foi gasto; a **taxa de queima** diz **a que velocidade**. Queima 1 é gastar o orçamento exatamente no fim da janela do SLO. Queima 14,4 numa hora é gastar 2% de um orçamento de 30 dias em uma hora:"},
  { code: `adopt Arcane.Observar as O

assert O.queima(0.999, 10000, 10) is 1.0      // o ritmo sustentável
assert O.queima(0.999, 10000, 144) is 14.4    // o limiar clássico: 1,44% de erro
assert O.queima(0.999, 0, 0) is 0.0           // sem tráfego, sem queima`, lang: 'df' },
];

const headings = [{ id: 'o-que-o-orcamento-decide', text: "O que o orçamento decide", level: 2 as const }, { id: 'a-taxa-de-queima', text: "A taxa de queima", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"SLO e orçamento de erro"}
      description={"99,9% é uma promessa com uma sobra: as falhas que ela permite. O orçamento transforma 'dá para arriscar?' em conta."}
      href={"/docs/observabilidade/slo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
