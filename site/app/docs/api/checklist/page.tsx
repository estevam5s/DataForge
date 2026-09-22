// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Checklist de uma API",
  description: "Vinte perguntas antes de publicar — cada uma com a página que a responde.",
};

const blocos: Bloco[] = [
  {"p": "Uma API pronta responde a estas perguntas. As que ficam sem resposta viram incidente ou e-mail de suporte, e quase sempre as duas coisas."},
  {"table": {"head": ["Pergunta", "Onde"], "rows": [["o erro tem `type` que um programa lê?", "[Problemas](/docs/api/problemas)"], ["o 500 esconde a mensagem interna?", "[Problemas](/docs/api/problemas)"], ["o que acontece com `Accept` que você não serve?", "[Negociação](/docs/api/negociacao)"], ["duas edições simultâneas apagam uma à outra?", "[Pré-condições](/docs/api/precondicoes)"], ["a listagem tem teto de itens por página?", "[Paginação](/docs/api/paginacao)"], ["a listagem de algo que muda usa cursor?", "[Paginação](/docs/api/paginacao)"], ["remover um campo sobe a versão?", "[Versionamento](/docs/api/versionamento)"], ["a versão velha avisa quando vai sumir?", "[Versionamento](/docs/api/versionamento)"], ["um POST reenviado cobra duas vezes?", "[Idempotência](/docs/api/idempotencia)"], ["401 e 403 estão nos lugares certos?", "[Autenticação](/docs/api/autenticacao)"], ["um cliente com laço derruba os outros?", "[Limites](/docs/api/limites)"], ["o contrato publicado confere com as rotas?", "[Contrato](/docs/api/contrato)"], ["toda entrada de fora é validada?", "`Kiln.validar` — [Kiln](/docs/kiln/rotas)"], ["CORS libera só as origens certas?", "[Middleware](/docs/kiln/middleware)"], ["as rotas têm teste sem socket, e um com socket?", "[Testes de API](/docs/testes)"], ["duas rotas escrevem no mesmo estado sem trava?", "`dataforge check` avisa: `escrita-concorrente`"], ["o log tem o id do pedido?", "`Kiln.request_id` — [Observabilidade](/docs/observabilidade)"], ["há um SLO, e um alerta que para quando o problema passa?", "[SLO](/docs/observabilidade/slo)"], ["o processo termina limpo no `docker stop`?", "[Encerrar](/docs/partida/encerrar)"], ["há TLS na frente?", "o Kiln não tem: [Produção](/docs/kiln/producao)"]]}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Checklist de uma API"}
      description={"Vinte perguntas antes de publicar — cada uma com a página que a responde."}
      href={"/docs/api/checklist"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
