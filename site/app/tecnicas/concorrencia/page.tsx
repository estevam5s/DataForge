import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Concorrência",
  description: "async/await, threads, canais e o que ainda não existe.",
};

const blocos: Bloco[] = [
  {"h2": "async / await"},
  { code: `async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}"}

usuario := await buscar_usuario(7)
out usuario` },
  {"callout": {"tipo": "atencao", "texto": "Em DataForge 4.0, `await` resolve a corrotina de forma **síncrona**. A estrutura do código já está correta para quando o agendamento paralelo chegar, mas hoje não há ganho de desempenho em `await` sequenciais. Use `async` onde a semântica é de espera, não esperando aceleração."}},
  {"h2": "thread"},
  { code: `resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append($"A{i}")

wait 200        # espera as threads
out len(resultados)` },
  {"p": "O bloco roda numa thread daemon: o programa **não espera** por ela. Se terminar antes, a thread é interrompida no meio."},
  {"h2": "A condição de corrida"},
  {"p": "Este é o ponto mais importante desta página:"},
  { code: `contador := {"valor": 0}

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

wait 400
out contador["valor"]     # deveria ser 2000. Frequentemente é menos.` },
  {"p": "`contador[\"valor\"] + 1` são três passos — ler, somar, escrever. Se as duas threads leem 5 ao mesmo tempo, ambas escrevem 6. Um incremento se perdeu."},
  {"p": "Rode várias vezes: o número muda. É o tipo de bug que passa em teste e quebra em produção sob carga."},
  {"h2": "channel — a via segura"},
  {"p": "DataForge 4.0 **não tem mutex nem lock**. A solução não é sincronizar o acesso — é não compartilhar:"},
  { code: `channel parciais

thread:
    soma := 0                  # variável local desta thread
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)        # reporta uma vez, no fim

thread:
    soma := 0
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)

wait 400

total := 0
persist yes:
    parcial := parciais.receive()
    given parcial is void:
        halt
    total += parcial

out total     # 2000, sempre` },
  {"p": "Cada thread trabalha no próprio escopo. Ninguém escreve onde outro lê. Essa ideia tem nome — *\"não comunique compartilhando memória; compartilhe memória comunicando\"* — e é o lema de Go."},
  {"h2": "Regra prática"},
  {"table": {"head": ["Situação", "Seguro?"], "rows": [["threads só leem dados compartilhados", "sim"], ["cada thread escreve numa variável própria", "sim"], ["threads enviam por `channel`", "sim"], ["duas threads escrevem na mesma variável", "**não**"], ["`lista.append` de duas threads", "**não**"]]}},
  {"h2": "parallel"},
  { code: `parallel:
    saidas.append(tarefa_a())
    saidas.append(tarefa_b())` },
  {"p": "**Cada instrução** do bloco vai para uma thread — não uma thread para o bloco inteiro. É uma limitação conhecida; enquanto isso, mantenha cada linha autossuficiente."},
  {"h2": "O que ainda não existe"},
  {"list": ["`Mutex`, `Semaphore`, `Atomic`", "`receive` bloqueante — hoje devolve `void` na hora se a fila estiver vazia", "`TaskGroup` e cancelamento", "`parallel` tratando blocos em vez de instruções"]},
  {"p": "Tudo isso está no [roadmap](/roadmap)."},
];

const headings = [{ id: 'async--await', text: "async / await", level: 2 as const }, { id: 'thread', text: "thread", level: 2 as const }, { id: 'a-condicao-de-corrida', text: "A condição de corrida", level: 2 as const }, { id: 'channel--a-via-segura', text: "channel — a via segura", level: 2 as const }, { id: 'regra-pratica', text: "Regra prática", level: 2 as const }, { id: 'parallel', text: "parallel", level: 2 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Concorrência"}
      description={"async/await, threads, canais e o que ainda não existe."}
      href={"/tecnicas/concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
