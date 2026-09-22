// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Erros e recursos",
  description: "5 produções: monitor, trigger, defer, assert. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "O caminho de erro tem sintaxe própria, e a regra que mais importa é que `halt`, `skip` e `yield` **não são erros**: eles atravessam o `monitor`."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`monitor`", "`MonitorBlock`"], ["`trigger`", "`TriggerStatement`"], ["`defer`", "`DeferStatement`"], ["`assert`", "`AssertStatement`"], ["`resiliencia`", "`RetryBlock`, `ValidateStatement`, `PropagateStatement`"]]}},
  {"h2": "monitor"},
  { code: `tratamento    = "monitor" bloco { "handle" [ tipo ] [ "as" nome ] bloco }
                [ "ensure" bloco ] ;`, lang: 'text' },
  { code: `monitor:
    trigger "x"
handle Error as e:
    out e.message
ensure:
    out "fim"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`trigger` levanta `TriggerError`, e não `RuntimeError`: para pegar qualquer coisa, `handle Error`."}},
  {"h2": "trigger"},
  { code: `levantar      = "trigger" expressao ;`, lang: 'text' },
  { code: `action g():
    trigger "falhou"`, lang: 'df' },
  {"h2": "defer"},
  { code: `adiar         = "defer" bloco ;`, lang: 'text' },
  { code: `action f():
    defer:
        out 1
    yield 2`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Roda na saída da **ação**, onde quer que esteja escrito."}},
  {"h2": "assert"},
  { code: `afirmar       = "assert" expressao [ "," expressao ] ;`, lang: 'text' },
  { code: `assert 1 is 1, "um e um"`, lang: 'df' },
  {"h2": "resiliencia"},
  { code: `repetir       = "retry" expressao bloco [ "recover" [ nome ] bloco ] ;
repassar      = "propagate" nome ;
validar       = "validate" expressao [ "," expressao ] ;`, lang: 'text' },
  { code: `n := 0
action instavel():
    n += 1
    trigger "ainda nao"
retry 3:
    instavel()
recover e:
    out e.message
validate n bigger 0, "n precisa ser positivo"
action f():
    monitor:
        trigger "x"
    handle e:
        propagate e`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`validate` é o `assert` do dado de entrada: a mensagem é para quem mandou o dado, e não para quem escreveu o código."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica erros`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'monitor', text: "monitor", level: 2 as const }, { id: 'trigger', text: "trigger", level: 2 as const }, { id: 'defer', text: "defer", level: 2 as const }, { id: 'assert', text: "assert", level: 2 as const }, { id: 'resiliencia', text: "resiliencia", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Erros e recursos"}
      description={"5 produções: monitor, trigger, defer, assert. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
