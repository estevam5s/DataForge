// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A arquitetura em arquivos",
  description: "Onde mora cada fase: do lexer ao interpretador, e as ferramentas que leem as mesmas estruturas.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem inteira mora em `dataforge/`, em Python, sem dependência externa em tempo de execução. Cada fase é um arquivo, e as ferramentas leem as **mesmas** estruturas que o interpretador — uma segunda leitura divergiria da primeira, e aí duas respostas para a mesma pergunta passariam a discordar."},
  {"table": {"head": ["Fase", "Arquivo", "Entrega"], "rows": [["lexer", "`lexer.py`, `tokens.py`", "tokens com linha e coluna"], ["parser", "`parser.py`, `ast_nodes.py`", "a árvore"], ["analisador", "`typechecker.py`", "erros e avisos antes de rodar"], ["onde mora um `adopt`", "`resolucao.py`", "o caminho — a **única** cópia da regra"], ["o que um arquivo oferece", "`superficie.py`", "a superfície, sem executar — usada pelo `check` e pela ABI"], ["execução", "`interpreter.py`", "a semântica"], ["compilação", "`compilador.py`", "a árvore vira fechamentos, uma vez"], ["representações do meio", "`hir.py`, `mir.py`, `ssa.py`, `lir.py`", "o que o compilador vê"], ["biblioteca", "`stdlib/`", "87 módulos"], ["ferramentas", "`formatter.py`, `linter.py`, `testrunner.py`, `lsp.py`, `dap.py`", "fmt, lint, test, editor, depurador"]]}},
  { code: `adopt Arcane.Ecossistema as E

conferido := E.conferir()
assert conferido["ok"]                       // nenhum caminho citado sumiu
assert len(conferido["orfaos"]) is 0         // nenhum arquivo ficou fora do mapa`, lang: 'df' },
  {"p": "O fluxo de um arquivo: `texto → tokenize → parse → [check] → Interpreter.run`. O interpretador despacha por nome de classe — um nó `GivenBlock` procura `exec_GivenBlock` —, e por isso acrescentar um recurso à linguagem é mexer em cinco lugares: tokens, lexer, nós e parser, interpretador, analisador. O guia está em [Contribuir](/docs/contribuir)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"A arquitetura em arquivos"}
      description={"Onde mora cada fase: do lexer ao interpretador, e as ferramentas que leem as mesmas estruturas."}
      href={"/docs/ecossistema/arquitetura"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
