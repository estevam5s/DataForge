// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_stm.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Concorrência e paralelismo: o mapa",
  description: "Item por item da parte 4 da referência Deep Tech — concorrência, STM, lock-free, atomics e paralelismo — cruzado com o que o DataForge tem.",
};

const blocos: Bloco[] = [
  {"p": "A quarta parte de uma referência Deep Tech cobre concorrência, memória transacional, estruturas sem trava, atômicos com ordenação de memória e paralelismo. Abaixo, item por item, com o que existe aqui e o que **não** existe — com o motivo."},
  {"h2": "17 · Concorrência"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["threads", "`thread:` e `parallel:`, com erro que sobe em vez de sumir", "[Concorrência](/docs/tecnicas/concorrencia)"], ["tasks, futures", "`C.rodar` devolve tarefa; `C.esperar`, `esperar_todas`, `esperar_primeira`", "[Concorrência](/docs/tecnicas/concorrencia)"], ["async/await", "`async action` + `await` — concorrência de E/S de verdade", "[Concorrência](/docs/tecnicas/concorrencia)"], ["promises", "`C.promessa()`: cumprir, falhar, esperar", "[Sem trava](/docs/concorrencia/sem-trava)"], ["executors, thread pools", "`C.executor(n)` com `submeter`, `mapear`, `fechar`", "[Sem trava](/docs/concorrencia/sem-trava)"], ["event loops", "**não existe** um laço de eventos próprio: `async` roda sobre threads, e a E/S bloqueante se sobrepõe de fato", "—"], ["channels, message passing", "`C.canal(capacidade)` — `receber` espera; `receive` sem prazo não", "[Concorrência](/docs/tecnicas/concorrencia)"], ["shared state", "existe, e **não** é protegido sozinho: o `check` avisa (`escrita-concorrente`)", "[Análise estática](/docs/tecnicas/analise-estatica)"], ["locks, mutex, RwLock, semáforos, barriers", "`mutex`, `com_trava`, `trava_leitura_escrita`, `semaforo`, `barreira`, `evento`, `condicao`", "[Concorrência](/docs/tecnicas/concorrencia)"]]}},
  {"h2": "18 · Memória transacional"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["STM, transações", "`Arcane.Stm`: `variavel` e `atomicamente`", "[STM](/docs/concorrencia/stm)"], ["atomicidade, rollback", "erro no meio desfaz o rascunho e sobe — nada é publicado", "[STM](/docs/concorrencia/stm)"], ["isolamento, consistência", "a transação lê a própria escrita e valida as versões no commit", "[STM](/docs/concorrencia/stm)"], ["composição de transações", "aninhar é achatar: duas transacionais dentro de uma terceira são uma só", "[STM](/docs/concorrencia/stm)"], ["controle de conflitos", "otimista: conflito custa repetição, e as estatísticas dizem quanto", "[STM](/docs/concorrencia/stm)"], ["concorrência sem locks tradicionais", "sim — a trava existe só no commit, e é curta", "[STM](/docs/concorrencia/stm)"]]}},
  {"h2": "19 · Lock-free e wait-free"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["CAS", "`C.atomico(v).comparar_e_trocar(esperado, novo)`", "[Sem trava](/docs/concorrencia/sem-trava)"], ["operações atômicas", "`pegar`, `definir`, `trocar`, `somar`, `pegar_e_somar`, `atualizar`", "[Sem trava](/docs/concorrencia/sem-trava)"], ["filas e pilhas lock-free", "`C.fila_sem_trava()`, `C.pilha_sem_trava()` — `append`/`pop` são indivisíveis em C", "[Sem trava](/docs/concorrencia/sem-trava)"], ["ring buffers", "`C.anel(n)`: o mais velho sai quando enche", "[Sem trava](/docs/concorrencia/sem-trava)"], ["wait-free", "**não existe** como garantia: o laço de CAS é lock-free, não wait-free", "—"], ["ABA problem", "acontece; a saída é guardar um selo junto do valor", "[Sem trava](/docs/concorrencia/sem-trava)"], ["hazard pointers, epoch reclamation", "**não se aplicam**: o coletor resolve a liberação que elas endereçam", "—"]]}},
  {"h2": "20 · Atomics e memory ordering"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["atomic load/store, CAS, fetch-add", "todos, em `C.atomico`", "[Sem trava](/docs/concorrencia/sem-trava)"], ["acquire, release, relaxed, seq-cst", "**não se aplicam**: o GIL já serializa as operações Python, e não há ordenação a escolher"], ["memory fences, barriers de memória", "**não existem** como instrução; `C.barreira(n)` é outra coisa — sincroniza threads, não memória"], ["modelo de memória da CPU, reordenação", "**não é observável** daqui: a reordenação existe no processador, e o runtime não a expõe"]]}},
  {"h2": "21 · Paralelismo"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["parallel loops, data parallelism", "`C.map`, `C.para_cada`, `C.lotes`; e `C.map_processos` para CPU", "[Paralelismo](/docs/exercicios/35-paralelismo)"], ["thread pools, task scheduling", "`C.executor(n)`, `C.pool_processos()`, `C.grupo()`", "[Sem trava](/docs/concorrencia/sem-trava)"], ["pipeline parallelism", "`Arcane.Pipeline` — etapas com dependência, ordem topológica e histórico", "[Pipelines](/docs/tecnicas/pipeline)"], ["work stealing", "**não existe**: o pool distribui, e não rouba — a diferença só aparece com tarefas muito desiguais"], ["SIMD", "**não existe** na linguagem; a vetorização vem pela ponte (`adopt Python.numpy`), sem cópia na fronteira", "[Ponte](/docs/tecnicas/ponte)"], ["GPU computing", "**não existe**: o caminho é a ponte para uma biblioteca que já fale com a GPU"], ["NUMA awareness", "**não existe**: o runtime não escolhe nó de memória"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das cinco seções, **três e meia** têm resposta aqui: concorrência (completa), STM (nova), lock-free no que o GIL permite garantir de verdade, e paralelismo de dados com processos. O que não existe divide-se em duas classes — o que o **GIL torna sem sentido** (ordenação de memória, fences) e o que exige **descer ao hardware** (SIMD, GPU, NUMA), que é justamente onde a ponte para o Python entra."},
  {"callout": {"tipo": "nota", "titulo": "A regra que vale para tudo isto", "texto": "A linguagem **não sincroniza sozinha**. O `dataforge check` avisa quando um `thread`, `parallel` ou `route` escreve num nome que vem de fora (`escrita-concorrente`) — inclusive na forma `v[\"n\"] := …`, que é a que mais engana. É aviso, e não erro: um acumulador protegido por mutex passa por ali igual."}},
];

const headings = [{ id: '17-concorrencia', text: "17 · Concorrência", level: 2 as const }, { id: '18-memoria-transacional', text: "18 · Memória transacional", level: 2 as const }, { id: '19-lock-free-e-wait-free', text: "19 · Lock-free e wait-free", level: 2 as const }, { id: '20-atomics-e-memory-ordering', text: "20 · Atomics e memory ordering", level: 2 as const }, { id: '21-paralelismo', text: "21 · Paralelismo", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Concorrência e paralelismo: o mapa"}
      description={"Item por item da parte 4 da referência Deep Tech — concorrência, STM, lock-free, atomics e paralelismo — cruzado com o que o DataForge tem."}
      href={"/docs/concorrencia/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
