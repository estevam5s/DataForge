// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Laço, thread, async ou processo",
  description: "Quatro modelos de concorrência, o que cada um resolve, e o GIL que decide metade da escolha.",
};

const blocos: Bloco[] = [
  {"p": "A pergunta que decide o modelo não é \"quero paralelismo?\", e sim **\"o trabalho espera ou calcula?\"**. Esperar (rede, disco, banco) sobrepõe bem em uma thread; calcular exige núcleos de verdade, e no CPython isso quer dizer processos."},
  {"table": {"head": ["Modelo", "Serve para", "Custo", "Não serve para"], "rows": [["`Arcane.Laco`", "milhares de conexões esperando", "1 thread, ~1 MB", "conta pesada (trava o laço)"], ["`thread:` / `parallel:`", "poucas esperas simultâneas, código simples", "~36 MB para mil threads", "milhares de conexões; conta pesada (GIL)"], ["`async` / `await`", "E/S concorrente com código sequencial", "uma thread por tarefa", "conta pesada (GIL)"], ["`P.map_processos`", "conta pesada em vários núcleos", "~50 ms de partida por processo", "trabalho pequeno (a partida domina)"], ["[ator](/docs/concorrencia/atores)", "estado que várias threads alteram", "1 thread por ator", "—"]]}},
  {"h2": "Medido"},
  {"table": {"head": ["Conexões", "Laço", "Thread por conexão"], "rows": [["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"], ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
  {"p": "O tempo quase empata — e esse é o número honesto. O que muda é a **forma** da conta: a memória e as threads do laço ficam planas, e as do modelo por conexão crescem em linha reta até algo quebrar."},
  {"callout": {"tipo": "dica", "titulo": "Comece simples", "texto": "Um serviço com dezenas de pedidos por segundo roda bem no Kiln, uma thread por pedido. O laço vale quando as conexões ficam **abertas** e são muitas: WebSocket, chat, um coletor de telemetria."}},
];

const headings = [{ id: 'medido', text: "Medido", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Laço, thread, async ou processo"}
      description={"Quatro modelos de concorrência, o que cada um resolve, e o GIL que decide metade da escolha."}
      href={"/docs/runtime/escolher"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
