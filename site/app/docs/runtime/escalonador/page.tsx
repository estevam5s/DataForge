// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_laco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O escalonador",
  description: "Ordem, prazo, cancelamento, contrapressão, o executor para o que bloqueia — e o erro que não pode derrubar o servidor inteiro.",
};

const blocos: Bloco[] = [
  {"p": "O laço tem três filas, e cada uma resolve um problema diferente."},
  {"table": {"head": ["Fila", "O que resolve"], "rows": [["**poller** (`selectors`)", "dormir até haver E/S, em vez de girar"], ["**prazos** (heap)", "`apos` e `a_cada` sem uma thread por relógio"], ["**prontas**", "a ordem de execução, e onde a contrapressão mora"]]}},
  {"h2": "Contrapressão"},
  {"p": "Uma fila sem teto troca **falha visível** por **morte por memória** — que é muito pior de diagnosticar, porque acontece longe da causa. Com teto, `agendar` devolve `no` e quem chama decide o que fazer."},
  { code: `adopt Arcane.Laco as L

laco := L.novo(2)                // teto de duas tarefas na fila

assert L.agendar(laco, lambda => void)
assert L.agendar(laco, lambda => void)
assert not L.agendar(laco, lambda => void)     // recusada, e diz que recusou
assert L.estatisticas(laco)["recusadas"] is 1`, lang: 'df' },
  {"h2": "Um erro não derruba o laço"},
  {"p": "Um reator que morre no primeiro erro derruba o servidor inteiro — e o erro costuma ser de **uma** conexão. Aqui ele é contado, guardado com o tipo e o texto, e o laço segue."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
visto := []

L.agendar(laco, lambda => 1 / 0)
L.agendar(laco, lambda => visto.append("segui"))
L.rodar(laco)

assert visto is ["segui"]
assert L.estatisticas(laco)["erros"] is 1
assert L.falhas(laco)[0]["tipo"] is "DivisionByZeroError"`, lang: 'df' },
  {"h2": "O que bloqueia vai para o pool"},
  {"p": "Esta é a peça que mais falta num reator escrito à mão. Um trabalho que bloqueia **dentro** do laço trava tudo — não só aquela tarefa, mas toda conexão aberta. `L.executar` manda para um pool de threads e devolve o resultado pela fila."},
  { code: `adopt Arcane.Laco as L
adopt Arcane.Time as T

laco := L.novo()
marcas := []

action pesado():
    T.sleep(0.05)
    yield "pronto"

L.executar(laco, pesado, lambda r => marcas.append(r))
L.apos(laco, 10, lambda => marcas.append("tique"))
L.rodar(laco)

// o tique rodou ENQUANTO o trabalho pesado corria
assert marcas is ["tique", "pronto"]`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Agendar de outra thread acorda o laço", "texto": "É o que faz o `executar` funcionar, e é o truque clássico: um par de soquetes (*socketpair*) registrado no seletor. Sem ele o laço dorme e a tarefa fica na fila até o próximo temporizador — que pode não existir. Um seletor acorda por **descritor**, e uma fila em memória não é um descritor."}},
  {"h2": "O que NÃO existe"},
  {"table": {"head": ["Item", "Por quê"], "rows": [["*work stealing* entre laços", "cada laço é uma thread; roubar tarefa entre eles exigiria fila sem trava e afinidade — e o GIL come o ganho antes de ele aparecer"], ["`io_uring`", "só Linux, e pelo CPython exigiria uma extensão em C — fora de uma linguagem sem dependência externa"], ["IOCP no Windows", "o `selectors` usa `select` ali, que tem teto de 512 descritores. É o limite do Windows nesta forma, e está dito"], ["prioridade por tarefa", "a fila é FIFO. Prioridade sem inversão de prioridade é mais difícil do que parece, e ninguém pediu ainda"]]}},
];

const headings = [{ id: 'contrapressao', text: "Contrapressão", level: 2 as const }, { id: 'um-erro-nao-derruba-o-laco', text: "Um erro não derruba o laço", level: 2 as const }, { id: 'o-que-bloqueia-vai-para-o-pool', text: "O que bloqueia vai para o pool", level: 2 as const }, { id: 'o-que-nao-existe', text: "O que NÃO existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O escalonador"}
      description={"Ordem, prazo, cancelamento, contrapressão, o executor para o que bloqueia — e o erro que não pode derrubar o servidor inteiro."}
      href={"/docs/runtime/escalonador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
