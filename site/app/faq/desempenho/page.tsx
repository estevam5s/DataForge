import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Desempenho",
  description: "O que é lento, por quê, e o que fazer a respeito.",
};

const blocos: Bloco[] = [
  {"h2": "O que esperar"},
  {"p": "DataForge é um **interpretador de árvore** escrito em Python, sem otimização. Cada nó da AST é visitado por uma chamada de método. Isso o torna mais lento que Python — que já é lento comparado a linguagens compiladas."},
  {"p": "Para scripts, ferramentas de terminal e processamento de alguns milhares de registros, isso não aparece. Para laços de milhões de iterações, aparece."},
  {"h2": "Meça antes de otimizar"},
  { code: `adopt Arcane.Time as Time

medida := Time.measure(trabalho_pesado)
out $"{medida.result} em {round(medida.ms, 2)} ms"` },
  {"p": "A intuição sobre o que é lento erra com frequência. Uma medição isolada também é ruído — o **mínimo** de várias execuções é mais informativo que a média."},
  {"h2": "Escolher o algoritmo certo"},
  {"p": "Vale mais que qualquer micro-otimização:"},
  { code: `action com_laco(n):          # O(n)
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

action com_formula(n):       # O(1)
    yield n * (n + 1) ~/ 2` },
  {"p": "As duas dão o mesmo resultado. Para `n = 100000`, a segunda é milhares de vezes mais rápida."},
  {"h2": "Streams para dados grandes"},
  {"p": "A diferença não é de velocidade, é de **memória** — e às vezes de trabalho evitado:"},
  { code: `# carrega tudo três vezes
linhas := IO.read("app.log").lines()
registros := linhas >> morph interpretar
erros := registros >> sift e: e["nivel"] is "ERROR"

# lê até o primeiro erro e para
apenas(interpretar(linhas_do_log()), "ERROR").first()` },
  {"p": "Veja [Streams](/tecnicas/streams)."},
  {"h2": "Índice em vez de busca linear"},
  { code: `# O(n) a cada consulta
achado := pessoas >> sift p: p["id"] is 20

# O(n) uma vez, O(1) depois
por_id := {p["id"]: p cycle p in pessoas}
achado := por_id[20]` },
  {"h2": "Banco: execute_many e índices"},
  { code: `DB.execute_many(conn, "INSERT INTO t VALUES (?, ?)", lote)  # uma ida
DB.execute(conn, "CREATE INDEX idx_nome ON produtos(nome)")` },
  {"h2": "Recursão tem limite"},
  {"p": "O interpretador aborta em **1000 quadros** com `StackOverflowError_`. Recursão sobre listas grandes deve virar `>> distill` ou um laço."},
  {"h2": "O que está no roadmap"},
  {"list": ["Cachear a resolução de nomes por nó da AST", "Uma IR e uma VM de bytecode com máquina de pilha", "Cache de compilação entre execuções"]},
  {"p": "Nada disso é urgente enquanto ninguém tiver um caso real onde o desempenho impede o uso. Se você tiver, [abra uma issue](/contribuir) com o código — é a melhor forma de priorizar."},
];

const headings = [{ id: 'o-que-esperar', text: "O que esperar", level: 2 as const }, { id: 'meca-antes-de-otimizar', text: "Meça antes de otimizar", level: 2 as const }, { id: 'escolher-o-algoritmo-certo', text: "Escolher o algoritmo certo", level: 2 as const }, { id: 'streams-para-dados-grandes', text: "Streams para dados grandes", level: 2 as const }, { id: 'indice-em-vez-de-busca-linear', text: "Índice em vez de busca linear", level: 2 as const }, { id: 'banco-executemany-e-indices', text: "Banco: execute_many e índices", level: 2 as const }, { id: 'recursao-tem-limite', text: "Recursão tem limite", level: 2 as const }, { id: 'o-que-esta-no-roadmap', text: "O que está no roadmap", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Desempenho"}
      description={"O que é lento, por quê, e o que fazer a respeito."}
      href={"/faq/desempenho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
