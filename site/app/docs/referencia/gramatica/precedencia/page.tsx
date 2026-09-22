// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Precedência, provada",
  description: "Da mais fraca para a mais forte — e cada nível conferido pela forma da árvore.",
};

const blocos: Bloco[] = [
  {"p": "Uma tabela de precedência que ninguém confere é uma opinião. Esta sai de `dataforge/gramatica.py`, e cada afirmação embaixo dela é uma expressão em que a ordem **decide o resultado** — o teste parseia e confere qual nó fica na raiz."},
  {"table": {"head": ["Nível", "Nome", "Operadores", "Associa"], "rows": [["1", "`pipeline`", "`>>`", "esquerda"], ["2", "`ternario`", "`given … otherwise`", "direita"], ["3", "`coalesce`", "`??`", "esquerda"], ["4", "`ou`", "`or`", "esquerda"], ["5", "`e`", "`and`", "esquerda"], ["6", "`nao`", "`not`", "prefixo"], ["7", "`comparacao`", "`is` `isnt` `bigger` `smaller` `bigger_eq` `smaller_eq` `in` `not in`", "encadeia"], ["8", "`soma`", "`+` `-`", "esquerda"], ["9", "`produto`", "`*` `/` `%` `~/`", "esquerda"], ["10", "`unario`", "`-x` `+x`", "prefixo"], ["11", "`potencia`", "`**`", "direita"], ["12", "`posfixo`", "`a.b` `a?.b` `a(…)` `a[…]`", "esquerda"]]}},
  {"h2": "O que fica na raiz"},
  {"table": {"head": ["Expressão", "Raiz"], "rows": [["`1 + 2 * 3`", "`BinaryOp` `+`"], ["`2 * 3 ** 2`", "`BinaryOp` `*`"], ["`-2 ** 2`", "`UnaryOp` `-`"], ["`1 + 2 bigger 2`", "`ComparisonOp` `bigger`"], ["`not a and b`", "`LogicalOp` `and`"], ["`a or b and c`", "`LogicalOp` `or`"], ["`a ?? b or c`", "`CoalesceOp`"], ["`1 given a otherwise b ?? 2`", "`TernaryExpression`"], ["`xs >> morph n: (n given n bigger 0 otherwise 0)`", "`PipelineExpression`"], ["`xs >> sift n: n bigger 1 >> morph n: n * 2`", "`PipelineExpression`"], ["`7 - 3 - 1`", "`BinaryOp` `-`"]]}},
  {"h2": "Para que lado associa"},
  {"table": {"head": ["Expressão", "O lado que guarda o resto"], "rows": [["`7 - 3 - 1`", "`left` é `BinaryOp`"], ["`8 / 4 / 2`", "`left` é `BinaryOp`"], ["`2 ** 3 ** 2`", "`right` é `BinaryOp`"], ["`a ?? b ?? c`", "`left` é `CoalesceOp`"], ["`a or b or c`", "`left` é `LogicalOp`"], ["`1 given a otherwise 2 given b otherwise 3`", "`else_value` é `TernaryExpression`"], ["`1 smaller 2 smaller 3`", "`left` é `ComparisonOp`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A comparação encadeia", "texto": "`1 smaller 5 smaller 3` é `1 smaller 5 and 5 smaller 3` — e dá `no`. Não é `(1 smaller 5) smaller 3`, que compararia um booleano com um número."}},
  { code: `assert (1 smaller 2 smaller 3) is yes
assert (1 smaller 5 smaller 3) is no
assert -2 ** 2 is -4
assert 2 ** 3 ** 2 is 512
assert 7 - 3 - 1 is 3
out "a precedencia confere executando, e nao so na arvore"`, lang: 'df' },
  {"p": "No terminal: `dataforge gramatica --precedencia`. Veja também [Precedência](/docs/referencia/precedencia)."},
];

const headings = [{ id: 'o-que-fica-na-raiz', text: "O que fica na raiz", level: 2 as const }, { id: 'para-que-lado-associa', text: "Para que lado associa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Precedência, provada"}
      description={"Da mais fraca para a mais forte — e cada nível conferido pela forma da árvore."}
      href={"/docs/referencia/gramatica/precedencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
