// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Programação reativa",
  description: "Sinal, derivado e efeito: um valor que outros valores acompanham — com as dependências descobertas na execução.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem já tinha três formas de lidar com mudança, e nenhuma resolvia o mesmo problema: `Arcane.Eventos` é um emissor, `Arcane.Stream` são tópicos com offset (Kafka, e não RxJS), e `stream action` é um gerador preguiçoso. O que faltava é a quarta — um **valor** que outros valores acompanham."},
  {"p": "É a diferença entre *\"me avise quando algo acontecer\"* e *\"este total é sempre a soma daqueles três\"*."},
  { code: `adopt Arcane.Reativo as R

preco := R.sinal(10.0)
quantidade := R.sinal(3)
total := R.derivado(lambda => preco.ler() * quantidade.ler())

out total.ler()          // 30.0
quantidade.escrever(5)
out total.ler()          // 50.0 — ninguem recalculou a mao`, lang: 'df' },
  {"h2": "Sinal é valor; observável é fluxo"},
  {"p": "**Sinal** tem um estado agora, e quem pergunta recebe o valor de agora. **Observável** não tem estado: quem se inscreve recebe o que vier daqui para a frente. Um clique é um fluxo; um saldo é um valor."},
  {"callout": {"tipo": "nota", "titulo": "Por que a distinção é mantida", "texto": "Frameworks reativos costumam ter os dois e chamar os dois de \"stream\" — e aí a pergunta \"qual é o valor atual?\" passa a não ter resposta."}},
  {"h2": "As peças"},
  {"table": {"head": ["", "O que é"], "rows": [["`R.sinal(v)`", "um valor com estado: `ler`, `escrever`, `atualizar`, `observar`"], ["`R.derivado(f)`", "calculado de outros — preguiçoso e memorizado"], ["`R.efeito(f)`", "o que acontece quando muda; roda uma vez ao nascer"], ["`R.lote(f)`", "várias escritas, uma notificação"], ["`R.observavel()`", "um fluxo no tempo, com `morph`, `sift`, `distill`…"], ["`R.de_cluster` · `R.intervalo`", "fontes frias: só começam quando alguém escuta"], ["`R.juntar` · `R.combinar`", "dois fluxos num só"]]}},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/reativo/sinais", "title": "Sinais e derivados", "desc": "A preguiça, a memória e as dependências descobertas."}, {"href": "/docs/reativo/efeitos", "title": "Efeitos e propagação", "desc": "O losango, e por que a marcação vem antes do aviso."}, {"href": "/docs/reativo/observaveis", "title": "Observáveis", "desc": "Fluxos, operadores e a fonte fria."}]},
];

const headings = [{ id: 'sinal-e-valor-observavel-e-fluxo', text: "Sinal é valor; observável é fluxo", level: 2 as const }, { id: 'as-pecas', text: "As peças", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Programação reativa"}
      description={"Sinal, derivado e efeito: um valor que outros valores acompanham — com as dependências descobertas na execução."}
      href={"/docs/reativo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
