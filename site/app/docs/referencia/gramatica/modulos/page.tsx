// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Módulos",
  description: "3 produções: adopt, relay e mark. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "Três palavras ligam arquivos: `adopt` traz, `relay` declara o que sai, e `mark` aplica um decorador."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`adopt`", "`AdoptStatement`"], ["`relay`", "`RelayStatement`"], ["`mark`", "`MarkDecorator`"]]}},
  {"h2": "adopt"},
  { code: `adocao        = "adopt" caminho [ "as" nome ]
              | "adopt" caminho "." "{" nome { "," nome } "}"
              | "adopt" "{" nome "as" nome { "," … } "}" "from" caminho ;
caminho       = nome { "." nome } | ( "./" | "../" ) segmento { "/" segmento } ;`, lang: 'text' },
  { code: `adopt Arcane.Math as M
adopt Arcane.Math.{sqrt, floor}
adopt {sqrt as raiz} from Arcane.Math`, lang: 'df' },
  {"h2": "relay"},
  { code: `exportacao    = "relay" nome { "," nome } ;`, lang: 'text' },
  { code: `action a():
    yield 1
relay a`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Com `relay`, só o que está listado sai do módulo."}},
  {"h2": "mark"},
  { code: `decorador     = "mark" "@" expressao NEWLINE ( acao | blueprint ) ;`, lang: 'text' },
  { code: `action dec(f):
    yield f
mark @dec
action h():
    yield 1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Um decorador que devolve `void` não substitui o alvo."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica modulos`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'adopt', text: "adopt", level: 2 as const }, { id: 'relay', text: "relay", level: 2 as const }, { id: 'mark', text: "mark", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Módulos"}
      description={"3 produções: adopt, relay e mark. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/modulos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
