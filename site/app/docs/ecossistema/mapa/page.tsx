// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ecossistema e design: o mapa",
  description: "As partes 20, 21 e 22 da referência Deep Tech, item por item: o que virou código, o que virou página, e o que não existe — com o motivo.",
};

const blocos: Bloco[] = [
  {"p": "As três partes que fecham a referência são as de **síntese**, e é exatamente aí que um documento começa a mentir: um desenho não roda, e uma lista de princípios nunca reprova."},
  {"p": "A resposta aqui foi fazer as três **derivadas do código e conferidas contra ele**. Este mapa é o índice do resultado, item por item."},
  {"h2": "Parte 20 — arquitetura do ecossistema"},
  {"table": {"head": ["Item do desenho", "Estado", "Onde"], "rows": [["`dfc` — Lexer, Parser, AST, HIR", "`existe`", "`lexer.py`, `parser.py`, `ast_nodes.py`, `hir.py`"], ["`dfc` — Type Checker", "`existe`", "`typechecker.py` + `superficie.py` + `resolucao.py`"], ["`dfc` — Borrow Checker", "`equivale`", "`Arcane.Posse` + 3 códigos do `check`"], ["`dfc` — MIR, Dataflow, LIR", "`existe`", "`mir.py`, `ssa.py`, `lir.py`"], ["`dfc` — LLVM Backend", "**`nao-existe`**", "`compilador.py` — fechamentos, 1,5× a 1,8×"], ["`dfc` — Code Generator", "**`nao-existe`**", "não há código de máquina"], ["`dfup` — Version Manager", "**`nao-existe`**", "os instaladores; trocar versão é reinstalar"], ["`dfpm` — Package Manager, Resolver", "`existe`", "`packages.py`, registro estático"], ["`dfpm` — Build System", "`equivale`", "`forge.toml` + `dataforge devops`"], ["`dfpm` — Workspace Manager", "**`nao-existe`**", "um `forge.toml` por pacote"], ["Runtime — Allocator", "**`nao-existe`**", "`Arcane.Memoria`: arena e controle do coletor"], ["Runtime — Scheduler, Event Loop, Async", "`existe`", "`arcane_laco.py`"], ["Runtime — Thread Runtime", "`existe`", "`travessia.py` — 3,45× em 10 núcleos"], ["Runtime — Error Runtime", "`existe`", "`errors.py`, 177 códigos, `idioma.py`"], ["Runtime — Bare-Metal", "**`nao-existe`**", "o runtime é o CPython"], ["Tooling — os sete", "`existe`", "LSP, fmt, lint, test, bench, profile, doc"], ["*(ausente)* Debugger", "`existe`", "`depurador.py` + `dap.py`"], ["*(ausente)* Execution Engine", "`existe`", "`interpreter.py` — o centro"], ["Targets — Linux, macOS, Windows, ARM", "`existe`", "4 plataformas construídas a cada tag"], ["Targets — RISC-V", "`equivale`", "onde há CPython roda; **não testado**"], ["Targets — WASM", "`equivale`", "rodar em, pelo Pyodide; compilar para, não"], ["Targets — Bare-Metal", "**`nao-existe`**", "`Arcane.Alvo` descreve o que falta"]]}},
  {"p": "O módulo: [`Arcane.Ecossistema`](/docs/ecossistema/componentes) · o comando: `dataforge ecossistema` · a conferência: `conferir()`, nas duas direções."},
  {"h2": "Parte 21 — princípios de design"},
  {"table": {"head": ["Princípio", "Veredito", "O que a prova mediu"], "rows": [["segurança por padrão", "`parcial`", "8 capacidades; a escrita concorrente sai como **aviso**"], ["custo zero", "`nao-se-aplica`", "3 de 3 sentinelas em `None`, 2 de 2 atalhos ligados"], ["controle explícito de recursos", "`cumprido`", "`Posse` com 16 símbolos, `Memoria` com 24, `defer` na linguagem"], ["compile-time first", "`parcial`", "**4 de 4** erros de execução acusados antes de rodar"], ["interoperabilidade", "`cumprido`", "`Arcane.C` com 23 símbolos; a ponte resolve"], ["portabilidade", "`parcial`", "6 alvos; 1 sem capacidade nenhuma"], ["performance observável", "`cumprido`", "8 de 8 comandos de medição presentes"], ["extensibilidade", "`cumprido`", "81 reservadas contra **52 contextuais**"], ["runtime modular", "`cumprido`", "**0** módulos carregados, **0** dependências externas"], ["escalabilidade técnica", "`parcial`", "7 componentes ausentes, nomeados"]]}},
  {"p": "E as **nove tensões**, que são o conteúdo que uma lista de princípios nunca tem: [onde dois se contradizem](/docs/ecossistema/tensoes), qual venceu, o custo aceito e o arquivo onde a decisão mora."},
  {"p": "O módulo: [`Arcane.Principios`](/docs/ecossistema/principios) · o comando: `dataforge principios` · `--tensoes` para só as nove."},
  {"h2": "Parte 22 — visão de implementação"},
  {"table": {"head": ["Item", "O que virou", "Onde"], "rows": [["o desenho do pipeline", "as 10 fases como dado, na ordem", "`Arcane.Percurso.fases()`"], ["o caminho de um arquivo", "as fases **medidas**, com o que cada uma produziu", "`percorrer()` · `dataforge percurso`"], ["o desenho em si", "impresso, com as ausências no lugar delas", "`desenho()` · `--desenho`"], ["onde o real difere do desenho", "5 divergências, com o motivo de cada", "`divergencias()`"], ["`Application / Server`", "o interpretador, e os dois frameworks web", "[Kiln](/docs/kiln) · [Vitrine](/docs/vitrine)"], ["`Bare-Metal / Kernel / MCU`", "**não existe**", "[as ausências](/docs/ecossistema/ausencias)"]]}},
  {"h2": "O que estas três partes ensinaram"},
  {"table": {"head": ["Lição", "Como apareceu"], "rows": [["um mapa escrito à mão mente sem avisar", "`conferir()` pegou dois caminhos errados meus **antes** do primeiro teste existir: o arquivo se chama `arcane_paralelo.py`, e só a classe se chama `ArcaneConcurrent`"], ["uma ferramenta que aponta a fase errada é pior que nenhuma", "o `lir` marcava 93,8% num arquivo de 12 tokens: era o custo do `import`, não da fase. O total caiu de 7,3 ms para **0,5 ms** e a resposta mudou de fase"], ["um princípio que não se aplica é informação", "\"zero-cost abstractions\" não tem como valer sem compilação nativa. Redefini-lo em silêncio seria pior que marcá-lo `nao-se-aplica` e escrever a leitura que vale"], ["a ausência precisa de lugar no mapa", "`Machine Code` e `execucao` continuam nos desenhos, marcados. Apagá-los faria o desenho parecer completo"]]}},
  {"p": "As 22 partes da referência estão cobertas. O que existe está medido; o que não existe está nomeado, com o motivo — que é a única forma de um documento técnico continuar verdadeiro depois de publicado."},
];

const headings = [{ id: 'parte-20-arquitetura-do-ecossistema', text: "Parte 20 — arquitetura do ecossistema", level: 2 as const }, { id: 'parte-21-principios-de-design', text: "Parte 21 — princípios de design", level: 2 as const }, { id: 'parte-22-visao-de-implementacao', text: "Parte 22 — visão de implementação", level: 2 as const }, { id: 'o-que-estas-tres-partes-ensinaram', text: "O que estas três partes ensinaram", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ecossistema e design: o mapa"}
      description={"As partes 20, 21 e 22 da referência Deep Tech, item por item: o que virou código, o que virou página, e o que não existe — com o motivo."}
      href={"/docs/ecossistema/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
