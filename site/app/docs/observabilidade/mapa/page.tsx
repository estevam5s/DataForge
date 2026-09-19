// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Observabilidade, memória e build: o mapa",
  description: "Item por item das partes 17, 10 e 11 da referência Deep Tech — profiling, benchmarking, allocators, GC opcional, PGO e tooling.",
};

const blocos: Bloco[] = [
  {"p": "Três partes de uma referência Deep Tech, cruzadas com o que a linguagem tem. Elas vão juntas porque se respondem: a parte 17 **mede** o que a parte 10 **controla**, e a parte 11 é quase toda ferramenta que já existia."},
  {"h2": "69 · Profiling (parte 17)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["CPU profiling", "`dataforge profile` e `P.perfilar` — tempo **próprio** por ação", "[Chamadas](/docs/observabilidade/chamadas)"], ["**flame graphs**", "`P.chama_svg` (SVG sem nada de fora) e `P.chama_texto` (formato dobrado)", "[Chamadas](/docs/observabilidade/chamadas)"], ["memory profiling", "`Mem.tamanho`, `Mem.layout`, `Mem.vivos` por blueprint", "[Coletor](/docs/memoria/coletor)"], ["**GC pauses**", "`P.gc_pausas` — medido em `gc.callbacks`, na fonte", "[Chamadas](/docs/observabilidade/chamadas)"], ["**lock contention**", "`P.trava` — a thread bloqueada não gasta CPU, e não aparece num perfil", "[Chamadas](/docs/observabilidade/chamadas)"], ["async task profiling", "`L.estatisticas` do laço: voltas, prazos, E/S e **maior atraso**", "[Escalonador](/docs/runtime/escalonador)"], ["hardware counters, cache/branch miss", "**não se aplica**: o CPython não expõe contador de hardware, e a conta de cache de um interpretador de árvore diria pouco", "—"]]}},
  {"h2": "70 · Benchmarking (parte 17)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["micro e macrobenchmarks", "`Arcane.Bench` (curva, classe, comparar) e `P.medir`", "[Perfil](/docs/observabilidade/perfil)"], ["**P50, P95, P99**", "`P.medir` e `P.resumir`, por posto e sem interpolar", "[Perfil](/docs/observabilidade/perfil)"], ["**tail latency**", "é o ponto da página: a média esconde exatamente isso", "[Perfil](/docs/observabilidade/perfil)"], ["**warm-up**", "separado e declarado em `aquecimento`", "[Perfil](/docs/observabilidade/perfil)"], ["**statistical significance**", "Mann-Whitney com correção de empates — e não teste t, porque tempo não é normal", "[Comparar](/docs/observabilidade/comparar)"], ["**regression benchmarks**", "`P.guardar` e `P.conferir` contra linha de base, com tolerância", "[Comparar](/docs/observabilidade/comparar)"], ["throughput", "`vazao` na medida, a partir da mediana", "[Perfil](/docs/observabilidade/perfil)"]]}},
  {"h2": "71 · Diagnóstico (parte 17)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["hotspot identification", "o flame graph, por tempo próprio", "[Chamadas](/docs/observabilidade/chamadas)"], ["GC pauses", "`P.gc_pausas`, com percentis e por geração", "[Chamadas](/docs/observabilidade/chamadas)"], ["lock contention", "`P.trava`, com a taxa de disputa", "[Chamadas](/docs/observabilidade/chamadas)"], ["scheduler overhead", "`maior_atraso_ms` no laço de eventos", "[Escalonador](/docs/runtime/escalonador)"], ["I/O bottlenecks", "[`Arcane.Observar`](/docs/tecnicas/observar) — painel, alerta e Prometheus", "[Observar](/docs/tecnicas/observar)"], ["compilation overhead", "[`dataforge ir --fase=lir`](/docs/compilador/otimizacao)", "[Otimização](/docs/compilador/otimizacao)"], ["allocation hotspots, cache/branch misses", "**não existe**: exigiria instrumentar o alocador do CPython", "—"]]}},
  {"h2": "47–48 · Allocators e estratégias (parte 10)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["object pooling, memory reuse", "`Mem.arena`, e o `pool` de [`Arcane.Padroes`](/docs/oop/padroes)", "[Coletor](/docs/memoria/coletor)"], ["arena lifetime", "`Mem.limpar` — o lote inteiro numa chamada", "[Coletor](/docs/memoria/coletor)"], ["alignment control", "existe, e é real — mas só na fronteira com o C: `C.alinhamento_de`", "[FFI](/docs/ffi/c)"], ["global/system/bump/slab/stack allocator", "**não se aplica**: quem aloca é o CPython, e não há como trocá-lo por dentro. Um \"allocator\" em Python puro seria uma camada **sobre** o alocador real — mais lenta, e chamada de allocator por engano", "—"], ["stack vs heap allocation", "**não se aplica**: todo objeto vive no heap do Python", "—"]]}},
  {"h2": "49–51 · Zero-cost, bypass e GC (parte 10)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["**desativação local do GC**", "`Mem.sem_gc`, que religa **mesmo se o corpo falhar**", "[Coletor](/docs/memoria/coletor)"], ["**pause times**", "`P.gc_pausas`, com P50/P95/P99", "[Chamadas](/docs/observabilidade/chamadas)"], ["**allocation thresholds**", "`Mem.gc_limiares` — os três, lidos e ajustados", "[Coletor](/docs/memoria/coletor)"], ["generational GC", "as três gerações do CPython, com a conta por geração", "[Coletor](/docs/memoria/coletor)"], ["**interação entre GC e ownership**", "[`Arcane.Posse`](/docs/memoria/posse) libera por escopo, sem esperar coletor", "[Posse](/docs/memoria/posse)"], ["escape analysis, dead code elimination", "existem, e são do [analisador](/docs/compilador/analises)", "[Análises](/docs/compilador/analises)"], ["mark-and-sweep, concurrent/parallel GC, thread-local GC", "**não se aplica**: o coletor é o do CPython, e trocá-lo não é uma decisão desta linguagem", "—"], ["monomorfização, static dispatch, inline expansion", "**não existe**: a linguagem é dinâmica, e uma ação pode ser substituída em execução", "—"], ["`#[no_std]`, bypass do runtime", "**não se aplica**: o runtime é o CPython", "—"]]}},
  {"h2": "52–54 · Build (parte 11)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["**compiler tooling**", "já existia **inteiro**: `check`, `fmt`, `lint`, `test`, `bench`, `profile`, `debug`, `dap`, `lsp`, `doc`, cobertura, `--plugin=`", "[CLI](/docs/cli)"], ["`dfpm` (gerenciador)", "`dataforge add/install/pack/publish`, com semver e lockfile", "[Pacotes](/docs/cli/pacotes)"], ["code coverage", "`dataforge test --cobertura --minimo=80`", "[Cobertura](/docs/tecnicas/cobertura)"], ["compiler plugins", "`--plugin=`, escrito em DataForge, vendo MIR e SSA", "[Plugins](/docs/metaprogramacao/plugins)"], ["**PGO**", "**não se aplica, e há número**: a [parte 8](/docs/compilador/otimizacao) mediu que compilar mais nós rende **1,01×** em código real. Um PGO que decidisse *o que* compilar otimizaria a constante errada", "[Otimização](/docs/compilador/otimizacao)"], ["LTO, ThinLTO, cross-module inlining", "**não se aplica**: não há passo de ligação", "—"]]}},
  {"h2": "O resumo honesto"},
  {"p": "A **parte 17 rendeu inteira** — percentis, significância, regressão, flame graph, pausas do coletor e contenção eram todos buracos reais, e todos transferem sem hardware. A **parte 10 rendeu pela metade**: o coletor e a arena sim; allocator, `no_std` e monomorfização não, porque quem aloca é o CPython. A **parte 11 já estava quase toda pronta** — §54 existia por inteiro —, e o que sobrava (PGO, LTO) é onde a parte 8 já tinha dado a resposta com número."},
  {"callout": {"tipo": "nota", "titulo": "O teste que mais importa deste conjunto", "texto": "Não é nenhum dos números: é o que compara **uma ação com ela mesma** e exige a resposta \"empate\". Uma ferramenta de benchmark que responde \"3% mais rápida\" a isso é pior que nenhuma ferramenta — porque é assim que se escolhe a implementação errada com convicção."}},
];

const headings = [{ id: '69-profiling-parte-17', text: "69 · Profiling (parte 17)", level: 2 as const }, { id: '70-benchmarking-parte-17', text: "70 · Benchmarking (parte 17)", level: 2 as const }, { id: '71-diagnostico-parte-17', text: "71 · Diagnóstico (parte 17)", level: 2 as const }, { id: '4748-allocators-e-estrategias-parte-10', text: "47–48 · Allocators e estratégias (parte 10)", level: 2 as const }, { id: '4951-zero-cost-bypass-e-gc-parte-10', text: "49–51 · Zero-cost, bypass e GC (parte 10)", level: 2 as const }, { id: '5254-build-parte-11', text: "52–54 · Build (parte 11)", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Observabilidade, memória e build: o mapa"}
      description={"Item por item das partes 17, 10 e 11 da referência Deep Tech — profiling, benchmarking, allocators, GC opcional, PGO e tooling."}
      href={"/docs/observabilidade/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
