// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Expressões",
  description: "14 produções: operadores, chamadas, coleções, pipeline. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "Uma expressão produz um valor. A ordem em que os operadores ligam está na [tabela de precedência](/docs/referencia/gramatica/precedencia), e cada nível ali é conferido pela forma da árvore."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`ternario`", "`TernaryExpression`"], ["`coalesce`", "`CoalesceOp`"], ["`comparacao`", "`ComparisonOp`"], ["`aritmetica`", "`BinaryOp`, `UnaryOp`"], ["`lambda`", "`LambdaExpression`"], ["`pipeline`", "`PipelineExpression`, `SiftOperation`, `MorphOperation`, `DistillOperation`"], ["`compreensao`", "`ListComprehension`"], ["`colecoes`", "`ListLiteral`, `SpreadElement`, `DictLiteral`, `TupleLiteral`"], ["`conjunto`", "`SetLiteral`, `SetComprehension`"], ["`acesso`", "`SliceAccess`, `SafeMemberAccess`"], ["`with`", "`WithExpression`"], ["`spawn`", "`SpawnExpression`"], ["`logico`", "`LogicalOp`, `NotOp`, `BooleanLiteral`"], ["`tipos_em_execucao`", "`CastExpression`, `TypeofExpression`"]]}},
  {"h2": "ternario"},
  { code: `ternario      = coalesce [ "given" expressao "otherwise" expressao ] ;`, lang: 'text' },
  { code: `r := "par" given 4 % 2 is 0 otherwise "impar"`, lang: 'df' },
  {"h2": "coalesce"},
  { code: `coalesce      = logico_ou { "??" logico_ou } ;`, lang: 'text' },
  { code: `v := {}
x := v["k"] ?? 0`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "O lado esquerdo de um `??` é lido com indulgência: a chave ausente não levanta."}},
  {"h2": "comparacao"},
  { code: `comparacao    = soma [ ( "is" | "isnt" | "bigger" | "smaller" | "bigger_eq"
                      | "smaller_eq" | "in" | "not" "in" ) soma ] ;`, lang: 'text' },
  { code: `x := 3 bigger_eq 2`, lang: 'df' },
  {"h2": "aritmetica"},
  { code: `soma          = produto { ( "+" | "-" ) produto } ;
produto       = unario { ( "*" | "/" | "%" | "~/" ) unario } ;
unario        = ( "-" | "+" ) unario | potencia ;
potencia      = posfixo [ "**" unario ] ;`, lang: 'text' },
  { code: `x := -2 ** 2 + 7 ~/ 2`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`-2 ** 2` é `-(2 ** 2)`: a potência liga mais forte que o sinal."}},
  {"h2": "lambda"},
  { code: `lambda        = "lambda" [ parametros ] ( ":" | "=>" ) expressao ;`, lang: 'text' },
  { code: `f := lambda x: x * 2
g := lambda a, b => a + b`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Um pipeline dentro do corpo precisa de parênteses: `lambda => (xs >> morph x: x * 2)`."}},
  {"h2": "pipeline"},
  { code: `pipeline      = ternario { ">>" operacao } ;
operacao      = "sift" nome ":" expressao | "morph" nome ":" expressao
              | "distill" nome "," nome ":" expressao expressao
              | verbo_de_quadro ;`, lang: 'text' },
  { code: `t := [1, 2, 3] >> sift n: n bigger 1 >> morph n: n * 10 >> distill a, v: a + v 0`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "O valor inicial do `distill` vem **depois** do corpo. E um ternário no corpo de `morph`/`sift` precisa de parênteses: `morph n: (n given n bigger 0 otherwise 0)` — sem eles, `given` abre uma instrução."}},
  {"h2": "compreensao"},
  { code: `compreensao   = "[" expressao "cycle" nome "in" expressao [ "given" expressao ] "]" ;`, lang: 'text' },
  { code: `q := [n * n cycle n in [1, 2, 3] given n bigger 1]`, lang: 'df' },
  {"h2": "colecoes"},
  { code: `cluster       = "[" [ item { "," item } ] "]" ;
vault         = "{" [ chave ":" expressao { "," chave ":" expressao } ] "}" ;
tupla         = "(" expressao "," [ expressao { "," expressao } ] ")" ;
item          = [ "..." ] expressao ;`, lang: 'text' },
  { code: `xs := [1, 2]
ys := [...xs, 3]
v := {"a": 1}
t := (1, "a")`, lang: 'df' },
  {"h2": "conjunto"},
  { code: `conjunto      = "{" item { "," item } [ "," ] "}"
              | "{" expressao "cycle" nome "in" expressao [ "given" expressao ] "}" ;
vazio         = "set" "(" [ expressao ] ")" ;`, lang: 'text' },
  { code: `cores := {"azul", "verde", "azul"}
pares := {n * n cycle n in [1, 2, 3]}
nenhum := set()`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "O primeiro item decide: seguido de `:` é vault, seguido de `,` ou `}` é conjunto. O vazio se escreve `set()`, porque `{}` já era o vault vazio."}},
  {"h2": "acesso"},
  { code: `posfixo       = primario { "." nome | "?." nome | "(" argumentos ")"
                         | "[" indice "]" } ;
indice        = expressao | [ expressao ] ":" [ expressao ] [ ":" [ expressao ] ] ;`, lang: 'text' },
  { code: `xs := [1, 2, 3]
out xs[1:3], xs[::-1]
o := void
out o?.nome`, lang: 'df' },
  {"h2": "with"},
  { code: `copia         = expressao "with" vault ;`, lang: 'text' },
  { code: `record P:
    x: Integer
p := P(1)
q := p with {"x": 2}`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Record é imutável: `p.x := 2` é erro; `with` devolve outro."}},
  {"h2": "spawn"},
  { code: `spawn         = ( "spawn" | "forge" ) nome "(" [ argumentos ] ")" ;`, lang: 'text' },
  { code: `blueprint B:
    x := 1
b := spawn B()
c := forge B()`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`spawn` leva o nome e os argumentos, e para ali: `spawn B().f()` chama `f` na instância."}},
  {"h2": "logico"},
  { code: `logico_ou     = logico_e { "or" logico_e } ;
logico_e      = negacao { "and" negacao } ;
negacao       = "not" negacao | comparacao ;
booleano      = "yes" | "no" | "void" ;`, lang: 'text' },
  { code: `out yes and "segundo", 0 and 9, not no`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`and` e `or` devolvem o **valor** que decidiu, e não um booleano: `yes and \"segundo\"` é `\"segundo\"`."}},
  {"h2": "tipos_em_execucao"},
  { code: `conversao     = "cast" expressao "as" tipo ;
tipo_de       = "typeof" "(" expressao ")" ;`, lang: 'text' },
  { code: `out cast "42" as Integer, typeof([1])`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`typeof` responde no vocabulário da linguagem — `Cluster`, e não `list`."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica expressoes`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'ternario', text: "ternario", level: 2 as const }, { id: 'coalesce', text: "coalesce", level: 2 as const }, { id: 'comparacao', text: "comparacao", level: 2 as const }, { id: 'aritmetica', text: "aritmetica", level: 2 as const }, { id: 'lambda', text: "lambda", level: 2 as const }, { id: 'pipeline', text: "pipeline", level: 2 as const }, { id: 'compreensao', text: "compreensao", level: 2 as const }, { id: 'colecoes', text: "colecoes", level: 2 as const }, { id: 'conjunto', text: "conjunto", level: 2 as const }, { id: 'acesso', text: "acesso", level: 2 as const }, { id: 'with', text: "with", level: 2 as const }, { id: 'spawn', text: "spawn", level: 2 as const }, { id: 'logico', text: "logico", level: 2 as const }, { id: 'tiposemexecucao', text: "tipos_em_execucao", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Expressões"}
      description={"14 produções: operadores, chamadas, coleções, pipeline. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/expressoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
