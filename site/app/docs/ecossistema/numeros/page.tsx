// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os números",
  description: "Módulos, símbolos, comandos, componentes — contados do código a cada vez, e nunca escritos à mão.",
};

const blocos: Bloco[] = [
  {"p": "Um número escrito à mão numa documentação envelhece no primeiro módulo novo, e ninguém lê a mesma página duas vezes para notar. Os números desta página saem de `Ecossistema.numeros()`, que os **conta** do código."},
  { code: `adopt Arcane.Ecossistema as E

n := E.numeros()
out n
assert n["modulos"] bigger 80
assert n["simbolos"] bigger 2000
assert n["comandos"] bigger 50`, lang: 'df' },
  {"table": {"head": ["Campo", "Conta"], "rows": [["`modulos`", "módulos da biblioteca padrão, sem os apelidos"], ["`simbolos`", "funções, classes e constantes exportadas por eles"], ["`comandos`", "comandos da CLI, lidos do catálogo que despacha"], ["`componentes`", "as peças do mapa, e quantas existem, equivalem ou não existem"], ["`alvos`", "os perfis de onde um programa roda"]]}},
  {"p": "Os números do site — na página inicial, na API pública, no README — têm uma trava: um teste compara cada um com a contagem real, e reprova quando divergem. Foi ela que achou o `.deb` dizendo 38 módulos quando eram 39."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Os números"}
      description={"Módulos, símbolos, comandos, componentes — contados do código a cada vez, e nunca escritos à mão."}
      href={"/docs/ecossistema/numeros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
