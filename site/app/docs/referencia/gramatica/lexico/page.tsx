// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Léxico",
  description: "6 produções: tokens, literais, comentários e indentação. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "Antes do parser, o lexer corta o texto em tokens. É aqui que moram as decisões que mais enganam: o `//` que é comentário, o `d` que faz um decimal, a indentação que vira `INDENT`/`DEDENT`."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`inteiro`", "`IntegerLiteral`"], ["`decimal`", "`DecimalLiteral`"], ["`texto`", "`StringLiteral`"], ["`interpolacao`", "`InterpolatedString`"], ["`comentario`", "`Assignment`"], ["`indentacao`", "`GivenBlock`"]]}},
  {"h2": "inteiro"},
  { code: `inteiro       = digito { digito | "_" } ;`, lang: 'text' },
  { code: `x := 1_000_000`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "O `_` separa milhares e é ignorado."}},
  {"h2": "decimal"},
  { code: `decimal       = digito { digito } "." digito { digito } "d" ;`, lang: 'text' },
  { code: `preco := 19.99d`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "O `d` constrói o valor a partir do **texto**, sem passar por float. Só conta quando termina o número: `19.99dias` não é decimal."}},
  {"h2": "texto"},
  { code: `texto         = '"' { caractere } '"' | '"""' { caractere | NEWLINE } '"""' ;`, lang: 'text' },
  { code: `sql := """SELECT *
FROM t"""`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "O texto simples não cruza linhas; o de três aspas cruza."}},
  {"h2": "interpolacao"},
  { code: `interpolado   = "$" '"' { caractere | "{" expressao "}" } '"' ;`, lang: 'text' },
  { code: `n := 2
out $"n vale {n * 2}"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Dentro de `{…}`, aspas normais: `$\"{v[\"id\"]}\"`. O escape `\\\"` quebra a leitura."}},
  {"h2": "comentario"},
  { code: `comentario    = "//" { caractere } NEWLINE ;`, lang: 'text' },
  { code: `x := 7 // um comentario
y := x ~/ 2`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`//` é comentário por padrão. Só vira divisão inteira seguido de dígito, `(` ou chamada/índice/membro — use `~/`, que não é ambíguo."}},
  {"h2": "indentacao"},
  { code: `bloco         = ":" NEWLINE INDENT { instrucao } DEDENT ;`, lang: 'text' },
  { code: `given yes:
    out 1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Só espaços, quatro por nível. Um tab é `SyncError`."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica lexico`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'inteiro', text: "inteiro", level: 2 as const }, { id: 'decimal', text: "decimal", level: 2 as const }, { id: 'texto', text: "texto", level: 2 as const }, { id: 'interpolacao', text: "interpolacao", level: 2 as const }, { id: 'comentario', text: "comentario", level: 2 as const }, { id: 'indentacao', text: "indentacao", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Léxico"}
      description={"6 produções: tokens, literais, comentários e indentação. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/lexico"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
