// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_laco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O runtime: o mapa",
  description: "Item por item da parte 12 da referência Deep Tech — scheduler assíncrono, green threads e event loop — cruzado com o que o DataForge tem.",
};

const blocos: Bloco[] = [
  {"p": "A décima segunda parte de uma referência Deep Tech é sobre a arquitetura do runtime. Foi a parte que escolhi fazer depois da 8 por um motivo: das que restavam, era **a única que muda o que a linguagem consegue fazer**, e não só o que ela documenta."},
  {"h2": "55 · Scheduler assíncrono"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["event loop", "`Arcane.Laco` — poller do sistema, fila de prazos, fila de prontas", "[O laço](/docs/runtime/laco)"], ["task scheduler, work queues", "`agendar`, `apos`, `a_cada`, com ordem FIFO e prazos num heap", "[Escalonador](/docs/runtime/escalonador)"], ["executors", "`L.executar` — o que bloqueia vai para um pool e volta pela fila", "[Escalonador](/docs/runtime/escalonador)"], ["cooperative scheduling", "as fibras: cada `emit` devolve o controle", "[Fibras](/docs/runtime/fibras)"], ["context switching", "o quadro do gerador; sem pilha própria e sem registrador a salvar", "[Fibras](/docs/runtime/fibras)"], ["cancellation", "`L.cancelar` vale para tarefa e para fibra; fechar o gerador roda os `defer`", "[Fibras](/docs/runtime/fibras)"], ["backpressure", "`L.novo(teto)` — a fila recusa em vez de crescer sem limite", "[Escalonador](/docs/runtime/escalonador)"], ["task stealing", "**não existe**: cada laço é uma thread, e com o GIL o ganho some antes de aparecer", "—"]]}},
  {"h2": "56 · Green threads"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["fibers", "existem, e são reais: um `stream action` dirigido pelo escalonador", "[Fibras](/docs/runtime/fibras)"], ["user-space scheduling", "o escalonador é o do módulo; o SO não sabe que há fibras", "[Fibras](/docs/runtime/fibras)"], ["context switching", "`next()` no gerador — o mais barato que há sem sair do Python", "[Fibras](/docs/runtime/fibras)"], ["scheduler integration", "a fibra diz o que espera, e o laço a registra no poller ou no heap", "[Fibras](/docs/runtime/fibras)"], ["stack management, register preservation", "**não existe**, e é a diferença entre *fibra* e *green thread*: a corrotina é **sem pilha**, e um `emit` dentro de uma ação chamada não suspende", "[Fibras](/docs/runtime/fibras)"], ["assembly-level switching", "**não se aplica** — exigiria assembly ou extensão em C, e a linguagem não tem dependência externa", "—"]]}},
  {"h2": "57 · Event loop"},
  {"table": {"head": ["Componente", "No DataForge", "Onde"], "rows": [["I/O Poller", "`selectors.DefaultSelector` — o melhor que o sistema oferece", "[O laço](/docs/runtime/laco)"], ["Timer Queue", "heap de prazos, com desempate estável", "[Escalonador](/docs/runtime/escalonador)"], ["Task Queue", "fila FIFO com teto opcional", "[Escalonador](/docs/runtime/escalonador)"], ["Executor", "pool de threads para o que bloqueia", "[Escalonador](/docs/runtime/escalonador)"], ["Reactor, Scheduler", "são o mesmo objeto: `Laco`", "[O laço](/docs/runtime/laco)"], ["**epoll**", "no Linux, automaticamente", "[O laço](/docs/runtime/laco)"], ["**kqueue**", "no macOS e no BSD, automaticamente", "[O laço](/docs/runtime/laco)"], ["IOCP", "**não**: no Windows o `selectors` usa `select`, com teto de 512 descritores. É o limite desta forma, e está dito em vez de escondido", "—"], ["io_uring", "**não existe**: só Linux, e pelo CPython exigiria extensão em C", "—"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das três seções, **duas estão inteiras** (§55 e §57, menos *work stealing*, IOCP e `io_uring`) e a terceira está pela metade — pela metade **certa**: as fibras existem e funcionam, e o que falta delas (pilha própria) é exatamente o que exigiria sair do Python."},
  {"callout": {"tipo": "nota", "titulo": "O que esta parte entregou à linguagem", "texto": "Um módulo (`Arcane.Laco`), um modelo de concorrência que o `async/await` não cobria, fibras de verdade sobre uma máquina que **já existia** no interpretador — e um número: **2000 conexões numa thread, com +0 MB**, contra 2000 threads e +36 MB. A parte 8 tinha entregado a lição oposta (a otimização que rendeu 1,01×); esta rendeu, e a diferença entre as duas é que aqui o modelo mudou, não a constante."}},
];

const headings = [{ id: '55-scheduler-assincrono', text: "55 · Scheduler assíncrono", level: 2 as const }, { id: '56-green-threads', text: "56 · Green threads", level: 2 as const }, { id: '57-event-loop', text: "57 · Event loop", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O runtime: o mapa"}
      description={"Item por item da parte 12 da referência Deep Tech — scheduler assíncrono, green threads e event loop — cruzado com o que o DataForge tem."}
      href={"/docs/runtime/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
