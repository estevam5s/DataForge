// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "tokens, ast, ir e percurso",
  description: "O que o lexer, o parser e o compilador viram — quando o código é lido de outro jeito.",
};

const blocos: Bloco[] = [
  {"p": "Quatro comandos que mostram o programa **como a linguagem o vê**. São os primeiros a usar quando o código não faz o que parece — e a suspeita é de que ele está sendo lido de outro jeito."},
  { code: `dataforge tokens app.df              # o que o lexer viu
dataforge ast app.df                 # a arvore que o parser montou
dataforge ir app.df                  # HIR, MIR, analises, SSA, LIR
dataforge ir app.df --fase=mir --acao=total   # o grafo de fluxo de uma acao
dataforge percurso app.df            # todas as fases, em ordem, medidas
dataforge percurso app.df --desenho  # o caminho desenhado, com as ausencias`, lang: 'bash' },
  {"h2": "O caso clássico: `//`"},
  {"p": "`//` é comentário por padrão, e só vira divisão inteira seguido de dígito, `(`, ou chamada/índice/membro. `x // 2` é divisão; `x // nota` é comentário. `dataforge tokens` mostra na hora qual das duas o lexer escolheu — e `~/` é a divisão inteira sem ambiguidade."},
  {"table": {"head": ["Fase", "O que ela mostra"], "rows": [["`hir`", "a árvore depois do açúcar — e quanto dele o arquivo usa"], ["`mir`", "o grafo de fluxo: bloco básico, aresta, laço, tratador"], ["`analises`", "alcance, constantes, escapatória, nome talvez não definido"], ["`ssa`", "uma definição por nome, com os nós φ das junções"], ["`lir`", "o que o compilador de fechamentos compilou — e o que recuou"]]}},
  {"callout": {"tipo": "nota", "titulo": "O percurso não executa", "texto": "`percurso` vai do lexer ao LIR e para. A décima fase — executar — é nomeada e marcada como não percorrida: um arquivo de verdade abre soquete e escreve em disco, e medir não pode ter efeito."}},
  {"p": "Continue em [Arquitetura](/docs/referencia/arquitetura) e [Gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'o-caso-classico', text: "O caso clássico: `//`", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"tokens, ast, ir e percurso"}
      description={"O que o lexer, o parser e o compilador viram — quando o código é lido de outro jeito."}
      href={"/docs/cli/internos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
