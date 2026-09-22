// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Observabilidade",
  description: "Métricas, rastreamento, logs, linhagem e SLO: responder sobre o sistema sem abrir o código.",
};

const blocos: Bloco[] = [
  {"p": "Observabilidade é conseguir responder, sem abrir o código e sem reproduzir o problema: **executou? quanto demorou? quantos registros? quantos falharam? em qual etapa? quando? em qual versão?** Log sozinho responde a primeira e a sexta; as outras cinco exigem **número**."},
  { code: `adopt Arcane.Observar as O

painel := O.painel("importacao", "2.1.0")
O.contar(painel, "linhas_lidas", 40000)
O.contar(painel, "linhas_recusadas", 12)
O.medir(painel, "duracao_ms", 830.0)
assert O.valor(painel, "linhas_recusadas") is 12`, lang: 'df' },
  {"table": {"head": ["Pergunta", "Ferramenta", "Página"], "rows": [["quanto? quantos?", "contador, medida, marcador", "[Métricas](/docs/observabilidade/metricas)"], ["onde o tempo foi?", "trechos com pai e filho", "[Rastreamento](/docs/observabilidade/rastreamento)"], ["o que aconteceu com ESTE pedido?", "log em JSON, com o id", "[Logs](/docs/observabilidade/logs)"], ["de onde veio este dado?", "linhagem", "[Linhagem](/docs/observabilidade/linhagem)"], ["estamos dentro do combinado?", "SLO e orçamento de erro", "[SLO](/docs/observabilidade/slo)"], ["alguém precisa agir agora?", "alerta de janela dupla", "[Alertas](/docs/observabilidade/alertas)"], ["a cauda, e não a média", "percentis", "[Percentis](/docs/observabilidade/perfil)"]]}},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/observabilidade/metricas", "title": "Métricas", "desc": "contador, medida e marcador — e o formato do Prometheus"}, {"href": "/docs/observabilidade/rastreamento", "title": "Rastreamento", "desc": "trechos aninhados: onde o tempo foi"}, {"href": "/docs/observabilidade/logs", "title": "Logs estruturados", "desc": "JSON por linha, com os campos para filtrar"}, {"href": "/docs/observabilidade/linhagem", "title": "Linhagem", "desc": "de onde veio o dado, e o que muda se a fonte mudar"}, {"href": "/docs/observabilidade/slo", "title": "SLO e orçamento de erro", "desc": "a conta que decide se dá para arriscar o deploy"}, {"href": "/docs/observabilidade/alertas", "title": "Alertas", "desc": "a taxa de queima em duas janelas"}, {"href": "/docs/observabilidade/perfil", "title": "Percentis, e a cauda", "desc": "P50, P95, P99 — e por que não a média"}, {"href": "/docs/observabilidade/comparar", "title": "A diferença é real?", "desc": "Mann-Whitney, e o empate honesto"}, {"href": "/docs/observabilidade/chamadas", "title": "Flame graph e pausas", "desc": "o tempo próprio de cada ação"}, {"href": "/docs/memoria", "title": "Memória", "desc": "o coletor, o layout e a posse"}]},
];

const headings = [{ id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Observabilidade"}
      description={"Métricas, rastreamento, logs, linhagem e SLO: responder sobre o sistema sem abrir o código."}
      href={"/docs/observabilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
