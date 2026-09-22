// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Padrões",
  description: "1 produções: o match e o que cada point casa. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "O `match` compara a forma de um valor com uma lista de padrões, do mais específico ao mais geral."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`match`", "`MatchBlock`"]]}},
  {"h2": "match"},
  { code: `selecao       = "match" expressao ":" NEWLINE INDENT
                { "point" padrao [ "when" expressao ] bloco }
                [ "default" bloco ] DEDENT ;
padrao        = literal | nome | tipo [ "as" nome ] | "[" padroes "]"
              | "{" chave ":" padrao { "," … } "}" | nome "(" padroes ")"
              | nome "." membro ;`, lang: 'text' },
  { code: `match 5:
    point Integer as n when n bigger 3:
        out "grande"
    point [a, b]:
        out "par"
    default:
        out "outro"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "A ordem importa: uma captura sem guarda no topo torna tudo abaixo inalcançável — e o `check` acusa."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica padroes`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'match', text: "match", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Padrões"}
      description={"1 produções: o match e o que cada point casa. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/padroes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
