// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Impasse",
  description: "Duas threads, duas travas, em ordens diferentes: cada uma segura o que a outra espera. A ordem fixa, e o prazo.",
};

const blocos: Bloco[] = [
  {"p": "A thread 1 toma a trava do estoque e espera a do caixa; a thread 2 tomou a do caixa e espera a do estoque. As duas ficam paradas **para sempre**, vivas e caladas — é o **impasse** (*deadlock*). O processo não cai, não levanta, não escreve no log: simplesmente para de responder."},
  {"h2": "A cura: sempre a mesma ordem"},
  {"p": "O impasse precisa de duas threads pedindo travas em ordens **diferentes**. Se toda thread toma as travas na mesma ordem — por exemplo, sempre a do estoque antes da do caixa —, o ciclo não tem como se formar:"},
  { code: `adopt Arcane.Concurrent as P

estoque := P.mutex()
caixa := P.mutex()
vendas := []

// A regra do programa: estoque ANTES de caixa, em todo lugar
action vender(item):
    P.com_trava(estoque, lambda => P.com_trava(caixa, lambda => vendas.append(item)))

parallel:
    vender("café")
    vender("chá")
assert len(vendas) is 2`, lang: 'df' },
  {"h2": "O prazo, para não travar calado"},
  { code: `adopt Arcane.Concurrent as P

esgotou := no
monitor:
    P.com_prazo(lambda => sleep(500), 0.05)       // quem chama não fica preso
handle Error as e:
    esgotou := yes
assert esgotou`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O prazo não interrompe", "texto": "`com_prazo` garante que **quem chamou** volta; a ação continua rodando em segundo plano, porque o Python não mata uma thread de fora sem arriscar deixar estado pela metade. Serve para não travar o chamador — e o log do prazo esgotado é o que aponta o impasse."}},
  {"p": "Com um [ator](/docs/concorrencia/atores) não há travas para ordenar, e com [STM](/docs/concorrencia/stm) o conflito vira nova tentativa — as duas formas evitam o impasse por construção."},
];

const headings = [{ id: 'a-cura-sempre-a-mesma-ordem', text: "A cura: sempre a mesma ordem", level: 2 as const }, { id: 'o-prazo-para-nao-travar-calado', text: "O prazo, para não travar calado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Impasse"}
      description={"Duas threads, duas travas, em ordens diferentes: cada uma segura o que a outra espera. A ordem fixa, e o prazo."}
      href={"/docs/concorrencia/impasse"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
