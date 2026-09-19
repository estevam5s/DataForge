// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_backend.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Backend: o mapa",
  description: "Item por item da parte 8 da referência Deep Tech — LLVM IR, pipeline de otimização, passes customizados e cross compilation — cruzado com o que o DataForge tem.",
};

const blocos: Bloco[] = [
  {"p": "A oitava parte de uma referência Deep Tech é sobre o backend do LLVM. É a **primeira** em que a resposta honesta é em boa medida *não se aplica* — e a parte em que essa resposta é mais útil que qualquer aproximação, porque cada item aqui pressupõe gerar código de máquina."},
  {"h2": "38 · LLVM IR"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["**SSA**", "existe de verdade: `ssa.py`, com dominância, fronteira de dominância e nó φ", "[SSA](/docs/compilador/ssa)"], ["**basic blocks**", "`mir.py` — um corpo por ação, arestas rotuladas", "[MIR](/docs/compilador/mir)"], ["instructions", "as instruções continuam sendo **nós da árvore**; a versão SSA é anexada, não reescrita em três endereços", "[SSA](/docs/compilador/ssa)"], ["metadata, source locations", "`line`/`column` em todo nó, e a ação sabe em que arquivo nasceu", "[Erros](/docs/erros)"], ["debug information", "existe, mas é a da linguagem: o [DAP](/docs/tecnicas/editor), com vigia e ponto de parada", "[Editor](/docs/tecnicas/editor)"], ["emissão de LLVM IR, tipos LLVM", "**não existe**: emitir o texto é fácil, mas usá-lo exigiria `llc`/`clang` instalado, e a linguagem passaria a depender de um compilador C para rodar", "[Backend](/docs/compilador/backend)"], ["intrinsics", "**não se aplica**", "—"], ["calling conventions", "só na fronteira com o C, onde são reais", "[FFI](/docs/ffi/c)"]]}},
  {"h2": "39 · Pipeline de otimização"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["constant folding", "`dobra-de-constante`, e nada que possa falhar é dobrado", "[Otimização](/docs/compilador/otimizacao)"], ["dead code elimination", "`ramo-morto` (com prova do SSA) e `inalcancavel`; mais `unused-*` no `lint`", "[Otimização](/docs/compilador/otimizacao)"], ["o pipeline em si", "`compilador.py`: a árvore vira fechamentos, com cobertura **medida** — 90,9% dos nós do repositório", "[Otimização](/docs/compilador/otimizacao)"], ["loop optimization", "**parcial, e pelo outro lado**: o escopo de uma volta é reaproveitado quando o corpo não captura — medido, e a otimização mais perigosa do interpretador", "[Arquitetura](/docs/referencia/arquitetura)"], ["inlining", "**não existe**. Numa linguagem em que uma ação pode ser substituída em tempo de execução (`f := outra`, método sobrescrito na filha), embutir o corpo exigiria provar identidade — e é a mesma conferência que a [chamada de cauda](/docs/referencia/arquitetura) faz na hora, em vez de assumir", "—"], ["vectorization, alias analysis", "**não se aplica**: não há registrador SIMD nem ponteiro a desambiguar", "—"], ["interprocedural / whole-program", "**não existe** no otimizador. O que atravessa fronteira é a **análise**: aridade, tipo de parâmetro e de retorno pelo `adopt`", "[Análise estática](/docs/tecnicas/analise-estatica)"], ["global optimization", "**não existe**, e há número dizendo por quê: os passes rendem 1,01× em código real", "[Otimização](/docs/compilador/otimizacao)"]]}},
  {"h2": "40 · Passes customizados"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["custom optimization passes", "`--plugin=` — uma regra escrita **em DataForge**, que vê o MIR e o SSA por `Arcane.Compilador`", "[Backend](/docs/compilador/backend)"], ["static analysis", "é o uso que paga: `ramo-morto` e `talvez-nao-definida` nasceram exatamente assim", "[Análises](/docs/compilador/analises)"], ["instrumentation", "`Arcane.Macro.reescrever` troca o corpo de uma ação na carga", "[Macros](/docs/metaprogramacao/macros)"], ["IR transformation", "os três passes de `otimizar.py`, sobre o HIR", "[Otimização](/docs/compilador/otimizacao)"], ["backend hooks", "**parcial**: o que dá para ligar é análise e reescrita de árvore, não a geração de código — porque ela não existe", "[Backend](/docs/compilador/backend)"], ["plugins C++, LLVM passes", "**não se aplica**: não há IR do LLVM para transformar", "—"]]}},
  {"h2": "41 · Cross compilation"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["Linux, Windows, macOS", "o `release.yml` constrói nas **quatro** plataformas e roda os exercícios *pelo binário* em cada uma", "[Download](/download)"], ["ARM64 e x86_64", "os dois, no macOS; o Linux sai como `.deb` e PKGBUILD", "[Instalação](/docs/instalacao)"], ["contêiner para outra arquitetura", "`dataforge devops` gera Dockerfile e manifesto do Kubernetes", "[DevOps](/docs/devops)"], ["target triples, cross compiler", "**não existe**: não há código de máquina a produzir, então não há alvo a nomear. O que atravessa plataforma é o **interpretador**, e ele atravessa por ser Python"], ["RISC-V, WebAssembly, bare-metal, embarcados", "**não existe**. Rodar em WebAssembly seria rodar o CPython em WebAssembly — o que funciona, e não é uma porta desta linguagem"], ["targets personalizados", "**não se aplica**"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das quatro seções, **uma** (§38) transferiu substancialmente — SSA, blocos básicos e dominância são teoria de compilador, não de LLVM, e valem igual num interpretador. Uma segunda (§40) transferiu pelo análogo: o passe customizado existe, escrito na linguagem, e é a forma como os dois diagnósticos novos nasceram. A §39 transferiu **e foi medida**, com o resultado contrariando a expectativa. A §41 não se aplica, e o que ocupa o lugar dela — construir para quatro plataformas — já existia."},
  {"callout": {"tipo": "atencao", "titulo": "O número que esta parte entrega", "texto": "**1,33×** numa carga feita dos nós que o inventário aponta, e **1,01×** em 59 exercícios reais. Dez nós novos compilam, a cobertura subiu, e o relógio não se moveu — porque o trabalho da volta já estava compilado. Este é o tipo de resultado que se publica, não que se esconde: sem ele, a próxima pessoa gastaria a mesma semana."}},
];

const headings = [{ id: '38-llvm-ir', text: "38 · LLVM IR", level: 2 as const }, { id: '39-pipeline-de-otimizacao', text: "39 · Pipeline de otimização", level: 2 as const }, { id: '40-passes-customizados', text: "40 · Passes customizados", level: 2 as const }, { id: '41-cross-compilation', text: "41 · Cross compilation", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Backend: o mapa"}
      description={"Item por item da parte 8 da referência Deep Tech — LLVM IR, pipeline de otimização, passes customizados e cross compilation — cruzado com o que o DataForge tem."}
      href={"/docs/compilador/mapa-backend"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
