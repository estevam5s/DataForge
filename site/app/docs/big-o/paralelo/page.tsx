// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Complexidade em paralelo",
  description: "Trabalho e profundidade, o teto de Amdahl, e por que dez núcleos não dividem o tempo por dez.",
};

const blocos: Bloco[] = [
  {"p": "Com mais de um núcleo, um número só não descreve o custo. São **dois**, e a distância entre eles é o quanto o problema aceita ser dividido."},
  {"table": {"head": ["Medida", "Símbolo", "O que é"], "rows": [["**trabalho**", "`T₁`", "o total de operações — o custo com **um** processador"], ["**profundidade**", "`T∞`", "a cadeia mais longa de dependências — o custo com **infinitos** processadores"]]}},
  {"p": "O tempo com `p` processadores fica entre os dois, e nunca abaixo da profundidade: `T_p ≥ max(T₁/p, T∞)`. O **paralelismo** do algoritmo é `T₁/T∞` — quantos processadores adiantam antes de sobrar."},
  {"h2": "Somar um milhão de números"},
  {"table": {"head": ["Forma", "Trabalho `T₁`", "Profundidade `T∞`", "Paralelismo"], "rows": [["laço sequencial", "`O(n)`", "`O(n)`", "**1** — não divide"], ["soma em árvore", "`O(n)`", "`O(log n)`", "`n / log n`"]]}},
  {"p": "O mesmo trabalho, profundidades diferentes. O laço obriga cada soma a esperar a anterior; a árvore soma pares independentes e depois pares de pares. É por isso que `>> distill` é sequencial por definição e uma redução por partes não é."},
  {"h2": "O teto de Amdahl"},
  {"p": "Se uma fração `s` do programa é **inerentemente** sequencial, o ganho máximo é `1 / s`, não importa quantos núcleos existam:"},
  {"table": {"head": ["Parte sequencial", "Ganho máximo", "Com 10 núcleos"], "rows": [["0%", "∞", "10,0x"], ["5%", "20x", "6,9x"], ["10%", "10x", "5,3x"], ["25%", "4x", "3,1x"], ["50%", "2x", "1,8x"]]}},
  {"p": "Dez por cento de código sequencial já corta o ganho de dez núcleos quase pela metade. Ler o arquivo, montar a lista e imprimir o resultado contam nesses dez por cento."},
  {"h2": "O que se mede de verdade"},
  {"p": "Oito blocos de CPU numa máquina de 10 núcleos, comparando a série com processos de verdade:"},
  { code: `adopt Arcane.Concurrent as P
adopt Arcane.Time as T

action pesado(semente):
    total := 0
    cycle i from 1 to 400000:
        total += (i * semente) % 7
    yield total

lotes := [1, 2, 3, 4, 5, 6, 7, 8]

inicio := T.monotonic()
serie := [pesado(s) cycle s in lotes]
ms_serie := (T.monotonic() - inicio) * 1000

inicio := T.monotonic()
processos := P.map_processos(pesado, lotes)
ms_proc := (T.monotonic() - inicio) * 1000

out $"serie:     {round(ms_serie, 0)} ms"
out $"processos: {round(ms_proc, 0)} ms   ({round(ms_serie / ms_proc, 2)}x)"
out $"igual: {serie is processos}"
`, lang: 'df' },
  { code: `serie:     4069 ms
processos: 864 ms   (4.71x)
igual: yes
`, lang: 'text', title: `saída (macOS, 10 núcleos)` },
  {"p": "**4,71x** com 8 tarefas em 10 núcleos — e não 8x. O que falta foi para a partida dos processos, a cópia dos dados e a coleta dos resultados. É a diferença entre o modelo e a máquina, e ela é sempre nessa direção."},
  {"h2": "Threads não dividem trabalho de CPU"},
  {"p": "O mesmo teste com `thread` em vez de processos dá **0,97x** — ligeiramente pior que a série. O GIL do Python deixa uma thread por vez executar bytecode: para CPU, thread não é paralelismo."},
  {"table": {"head": ["Ferramenta", "Serve para", "Ganho em CPU"], "rows": [["`thread:` / `parallel:`", "rede, disco, banco, espera", "**nenhum** — o GIL serializa"], ["`async` / `await`", "entrada e saída sobreposta", "**nenhum** em CPU, muito em I/O"], ["`P.map_processos`", "trabalho de CPU", "medido: **4,71x** em 10 núcleos"], ["`P.pool_processos()`", "CPU, muitas vezes seguidas", "evita os ~100 ms de partida por chamada"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A partida também tem custo", "texto": "Iniciar um processo custa mais de cem milissegundos. Medido: 180 ms na primeira chamada de um pool, 82 ms na segunda. Se o trabalho dura menos que isso, a versão paralela perde — e é por isso que um teste de paralelismo precisa de carga suficiente para o tempo de partida sumir na conta."}},
  {"h2": "Complexidade de comunicação"},
  {"p": "Num processo separado, o dado precisa **atravessar**. Isso é custo que a versão sequencial não tem, e ele entra na conta:"},
  {"list": ["**O que atravessa é copiado.** Mandar um record de trinta campos junto de cada lote copia trinta campos por lote.", "**Por isso o pacote vai uma vez por processo**, no início, e o que cada lote leva é um índice.", "**Lote grande demais** desequilibra: um processo termina e fica ocioso enquanto o outro ainda trabalha.", "**Lote pequeno demais** paga comunicação mais vezes do que trabalha."]},
  {"p": "A regra prática: divida em algumas vezes mais lotes do que núcleos — o suficiente para equilibrar, longe o bastante de comunicar a cada item."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que o modelo e a máquina discordam"}, {"href": "/docs/tecnicas/concorrencia", "title": "Concorrência", "desc": "thread, parallel, canais e o que não é protegido sozinho"}, {"href": "/docs/big-o/espaco", "title": "Complexidade de espaço", "desc": "trocar tempo por memória, e quando vale"}]},
];

const headings = [{ id: 'somar-um-milhao-de-numeros', text: "Somar um milhão de números", level: 2 as const }, { id: 'o-teto-de-amdahl', text: "O teto de Amdahl", level: 2 as const }, { id: 'o-que-se-mede-de-verdade', text: "O que se mede de verdade", level: 2 as const }, { id: 'threads-nao-dividem-trabalho-de-cpu', text: "Threads não dividem trabalho de CPU", level: 2 as const }, { id: 'complexidade-de-comunicacao', text: "Complexidade de comunicação", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Complexidade em paralelo"}
      description={"Trabalho e profundidade, o teto de Amdahl, e por que dez núcleos não dividem o tempo por dez."}
      href={"/docs/big-o/paralelo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
