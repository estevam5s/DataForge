// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dentro do compilador",
  description: "Do texto ao que roda: as oito fases, o que cada uma entrega, e como ver cada uma de dentro da linguagem.",
};

const blocos: Bloco[] = [
  {"p": "Um arquivo `.df` atravessa oito fases antes de rodar, e **todas** podem ser vistas de dentro da linguagem, pelo `Arcane.Compilador`, ou da linha de comando, por `dataforge ir`. Nenhuma é caixa-preta: o que o analisador conclui, o grafo em que ele concluiu e o que o backend compilou são dados que um programa lê."},
  { code: `adopt Arcane.Compilador as Comp

assert Comp.fases() is ["lexer", "parser", "hir", "mir", "analises", "ssa", "otimizado", "lir"]
out Comp.tokens("x := 1 + 2")[0]`, lang: 'df' },
  {"table": {"head": ["Fase", "Recebe", "Entrega", "Página"], "rows": [["lexer", "o texto", "tokens com linha e coluna", "[Lexer](/docs/compilador/lexer)"], ["parser", "tokens", "a árvore sintática", "[Parser](/docs/compilador/parser)"], ["analisador", "a árvore", "erros e avisos, antes de rodar", "[O analisador](/docs/compilador/analisador)"], ["HIR", "a árvore", "a árvore sem açúcar", "[HIR](/docs/compilador/hir)"], ["MIR", "o HIR", "blocos básicos e arestas", "[MIR](/docs/compilador/mir)"], ["análises", "o MIR", "vivas, constantes, alcance", "[O que o fluxo prova](/docs/compilador/analises)"], ["SSA", "o MIR", "uma definição por nome, com φ", "[SSA](/docs/compilador/ssa)"], ["LIR", "a árvore", "o que o compilador de fechamentos cobriu", "[Backend](/docs/compilador/backend)"]]}},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/compilador/pipeline", "title": "O caminho de compilação", "desc": "as fases em sequência, com o custo de cada uma"}, {"href": "/docs/compilador/lexer", "title": "Lexer", "desc": "INDENT, DEDENT, e por que // às vezes é divisão"}, {"href": "/docs/compilador/parser", "title": "Parser", "desc": "descida recursiva, precedência e a recuperação de erro"}, {"href": "/docs/compilador/analisador", "title": "O analisador", "desc": "o que ele prova, e por que cala quando não prova"}, {"href": "/docs/compilador/dominancia", "title": "Dominância", "desc": "por onde todo caminho passa, e onde vão os φ"}, {"href": "/docs/compilador/visualizar", "title": "Desenhar o grafo", "desc": "o fluxo em DOT, para o Graphviz"}, {"href": "/docs/compilador/vivas", "title": "Variáveis vivas", "desc": "o valor que ainda vai ser lido"}, {"href": "/docs/compilador/cauda", "title": "Chamada de cauda", "desc": "a recursão sem teto, e as quatro recusas"}, {"href": "/docs/compilador/cache", "title": "O cache de árvores", "desc": "93% do parse, e a chave que impede o desastre"}]},
];

const headings = [{ id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Dentro do compilador"}
      description={"Do texto ao que roda: as oito fases, o que cada uma entrega, e como ver cada uma de dentro da linguagem."}
      href={"/docs/compilador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
