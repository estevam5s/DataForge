// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Alertas que param de tocar",
  description: "O alerta de janela dupla: a longa evita o pico de 30 segundos, a curta faz o alerta parar quando o problema passou.",
};

const blocos: Bloco[] = [
  {"p": "Alerta é sobre o que **exige ação agora**. Um que dispara todo dia deixa de ser lido em uma semana — e o que importa passa despercebido junto. O desenho que resolve isso é o de **duas janelas** do livro de SRE do Google: dispara só quando a janela longa **e** a curta queimam acima do limiar."},
  { code: `adopt Arcane.Observar as O

// a última hora e os últimos cinco minutos, com objetivo de 99,9%
incidente := O.alerta_slo(0.999, {"total": 10000, "falhas": 200}, {"total": 800, "falhas": 20})
assert incidente["disparar"]

ja_passou := O.alerta_slo(0.999, {"total": 10000, "falhas": 200}, {"total": 800, "falhas": 1})
assert not ja_passou["disparar"]
out ja_passou["motivo"]

pico := O.alerta_slo(0.999, {"total": 10000, "falhas": 5}, {"total": 800, "falhas": 20})
assert not pico["disparar"]
out pico["motivo"]`, lang: 'df' },
  {"table": {"head": ["Janela longa", "Janela curta", "Alerta", "Porque"], "rows": [["queima", "queima", "**dispara**", "o problema existe e continua"], ["queima", "não queima", "cala", "o problema **passou** — a longa ainda carrega o passado"], ["não queima", "queima", "cala", "um pico curto, que o orçamento absorve"]]}},
  {"h2": "Regras de limite simples"},
  {"p": "Para o que não é SLO — fila acima de um tamanho, disco acima de uma porcentagem —, `O.alertar` confere regras sobre as métricas do painel:"},
  { code: `adopt Arcane.Observar as O

p := O.painel("worker")
O.marcar(p, "fila", 140)
disparados := O.alertar(p, [{"metrica": "fila", "acima": 100, "texto": "fila acumulando"}])
assert disparados[0]["texto"] is "fila acumulando"`, lang: 'df' },
];

const headings = [{ id: 'regras-de-limite-simples', text: "Regras de limite simples", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Alertas que param de tocar"}
      description={"O alerta de janela dupla: a longa evita o pico de 30 segundos, a curta faz o alerta parar quando o problema passou."}
      href={"/docs/observabilidade/alertas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
