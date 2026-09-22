// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que é público",
  description: "Sem relay, tudo do topo sai — inclusive o que começa com _. Só o relay esconde.",
};

const blocos: Bloco[] = [
  {"p": "Uma pergunta que quem vem do Python faz: *“o `_` no começo do nome esconde?”*. **Não.** Sem `relay`, tudo o que o módulo define no topo sai pelo `adopt` — `_interno` inclusive. O `_` é convenção para quem lê; quem esconde é o `relay`."},
  {"table": {"head": ["O módulo tem", "Sai pelo `adopt`"], "rows": [["nenhum `relay`", "**tudo** do topo, com ou sem `_`"], ["algum `relay`", "**só** o que está listado"], ["`relay a as b`", "`b` — e `a` fica interno"]]}},
  { code: `// contador.df, sem relay:
//     _interno := 42
//     action mais(): ...
//
// main.df:
//     adopt ./contador as C
//     out C._interno        // 42 — o '_' nao escondeu
//
// Com 'relay mais' no fim de contador.df, C._interno vira erro:
//     o modulo './contador' nao tem '_interno'

out "so o relay decide o que e publico"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Sem relay, todo nome do topo é contrato", "texto": "Quem adotou o seu módulo pode estar usando qualquer nome do topo — inclusive o auxiliar que você pretendia renomear amanhã. Uma biblioteca deveria sempre ter `relay`: é ele que separa o que você promete do que é detalhe, e é o que o `dataforge abi` compara."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O que é público"}
      description={"Sem relay, tudo do topo sai — inclusive o que começa com _. Só o relay esconde."}
      href={"/docs/modulos/visibilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
