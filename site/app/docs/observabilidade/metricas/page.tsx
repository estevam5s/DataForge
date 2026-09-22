// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Métricas",
  description: "Contador que só sobe, medida que vira percentil, marcador que é o valor de agora — e o texto que o Prometheus lê.",
};

const blocos: Bloco[] = [
  {"p": "Três formas de número, e escolher errado dá gráfico errado:"},
  {"table": {"head": ["Tipo", "Função", "Exemplo", "Pergunta que responde"], "rows": [["contador", "`O.contar`", "pedidos atendidos, erros", "quantos, desde o começo? (e a taxa, derivando)"], ["medida", "`O.medir`", "duração de cada pedido", "qual a distribuição? — P50, P95, P99"], ["marcador", "`O.marcar`", "tamanho da fila agora", "quanto vale neste instante?"]]}},
  { code: `adopt Arcane.Observar as O

p := O.painel("api")
O.contar(p, "pedidos", 3)
O.contar(p, "pedidos", 2)
O.medir(p, "latencia_ms", 12.0)
O.medir(p, "latencia_ms", 48.0)
O.marcar(p, "fila", 7)
O.marcar(p, "fila", 4)                  // o marcador guarda o último

assert O.valor(p, "pedidos") is 5
assert O.valor(p, "fila") is 4

texto := O.prometheus(p)
out texto
assert texto.contains("# TYPE api_pedidos counter")
assert texto.contains("api_fila 4")`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Contador nunca desce", "texto": "Um contador que desce (\"usuários online\") quebra toda conta de taxa: o Prometheus interpreta a queda como reinício do processo. O que sobe e desce é **marcador**."}},
  {"callout": {"tipo": "dica", "titulo": "Nome com unidade", "texto": "`latencia_ms`, `tamanho_bytes`, `duracao_s`. Um painel que mostra `latencia: 0.048` deixa a pessoa adivinhando se é segundo ou milissegundo — e ela adivinha errado no meio de um incidente."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Métricas"}
      description={"Contador que só sobe, medida que vira percentil, marcador que é o valor de agora — e o texto que o Prometheus lê."}
      href={"/docs/observabilidade/metricas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
