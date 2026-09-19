// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_laco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O laço de eventos",
  description: "Uma thread dormindo no seletor do sistema em vez de uma thread por conexão — com o número medido: 2000 conexões, 1 thread, +0 MB.",
};

const blocos: Bloco[] = [
  {"p": "O [`async/await`](/docs/tecnicas/concorrencia) desta linguagem é **uma thread por tarefa**. Serve para o que foi feito — sobrepor entrada e saída — e não escala: mil conexões simultâneas são mil threads do sistema. O [Kiln](/docs/kiln) atende **um pedido por thread** pelo mesmo motivo."},
  {"p": "O outro modelo é o **reator**: uma thread que dorme num seletor do sistema — `epoll` no Linux, `kqueue` no macOS e no BSD, `select` no Windows — e acorda quando algum descritor tem trabalho."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
ordem := []

L.agendar(laco, lambda => ordem.append("agora"))
L.apos(laco, 30, lambda => ordem.append("depois"))
L.apos(laco, 10, lambda => ordem.append("antes"))
L.rodar(laco)

assert ordem is ["agora", "antes", "depois"]
assert L.mecanismo(laco) in ["epoll", "kqueue", "select", "poll"]`, lang: 'df' },
  {"p": "Quem foi agendado **depois** mas vence **antes** roda antes: a fila de prazos é um heap, não uma lista percorrida."},
  {"h2": "O número"},
  {"p": "Um servidor de linha, uma requisição por conexão, medido nesta máquina contra o mesmo servidor com uma thread por conexão:"},
  {"table": {"head": ["Conexões", "Laço de eventos", "Thread por conexão"], "rows": [["400", "33 ms · **1 thread** · +0 MB", "43 ms · 400 threads · +14 MB"], ["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"], ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O tempo quase empata — e a memória é que conta a história", "texto": "Nesta máquina, duas mil threads ainda funcionam, e a diferença de tempo fica em ~1,1×. O que muda é a **forma da conta**: o custo do laço é plano (+0 MB), o do modelo de threads é linear (+36 MB, ~36 KB por thread). Num contêiner com limite de threads, ou com trabalho de verdade por conexão, um falha onde o outro nem percebe. Publicar o 1,1× é mais honesto que publicar só o caso em que o outro modelo já quebrou."}},
  {"h2": "Ele não gira em vão"},
  {"p": "É a diferença entre um reator e uma espera ocupada, e ela é **testada**: com um único temporizador a 200 ms, o laço dá menos de 50 voltas. Um laço de espera ocupada daria milhões, e queimaria um núcleo sem fazer nada."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
L.apos(laco, 60, lambda => void)
L.rodar(laco)

// dormiu no seletor em vez de girar
assert L.estatisticas(laco)["voltas"] smaller 50`, lang: 'df' },
  {"h2": "Entrada e saída"},
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`L.novo(teto?)`", "um laço; com `teto`, a fila de prontas recusa quando enche"], ["`L.rodar(laco)`", "gira até acabar o trabalho, ou até alguém chamar `parar`"], ["`L.agendar(laco, acao)`", "põe na fila; devolve `no` quando o teto recusa"], ["`L.apos(laco, ms, acao)`", "uma vez, depois do prazo"], ["`L.a_cada(laco, ms, acao)`", "repete até ser cancelado"], ["`L.quando_ler(laco, soquete, acao)`", "chama quando houver o que ler"], ["`L.quando_escrever(…)` · `L.esquecer(…)`", "o outro lado, e a saída do laço"], ["`L.executar(laco, trabalho, depois)`", "manda o que bloqueia para o pool"], ["`L.cancelar(t)` · `L.cancelada(t)`", "vale para tarefa e para fibra"], ["`L.mecanismo(laco)`", "`epoll`, `kqueue` ou `select` — o do sistema"], ["`L.estatisticas(laco)` · `L.falhas(laco)`", "voltas, tarefas, prazos, E/S, erros"]]}},
  {"h2": "Quando usar qual"},
  {"table": {"head": ["Precisa de", "Use"], "rows": [["sobrepor duas ou três chamadas de rede", "[`async`/`await`](/docs/tecnicas/concorrencia) — mais simples, e o custo não aparece"], ["milhares de conexões abertas ao mesmo tempo", "**este módulo**"], ["usar mais de um núcleo de CPU", "[`P.map_processos`](/docs/concorrencia/mapa) — o laço é uma thread só, e o GIL continua no caminho"], ["servir HTTP com rota e template", "[Kiln](/docs/kiln) — ele é thread por pedido, e para a maioria dos casos isso basta"]]}},
];

const headings = [{ id: 'o-numero', text: "O número", level: 2 as const }, { id: 'ele-nao-gira-em-vao', text: "Ele não gira em vão", level: 2 as const }, { id: 'entrada-e-saida', text: "Entrada e saída", level: 2 as const }, { id: 'quando-usar-qual', text: "Quando usar qual", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O laço de eventos"}
      description={"Uma thread dormindo no seletor do sistema em vez de uma thread por conexão — com o número medido: 2000 conexões, 1 thread, +0 MB."}
      href={"/docs/runtime/laco"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
