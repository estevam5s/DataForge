// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quando algo falha no laço",
  description: "Um erro num retorno de chamada é contado, e não propagado: uma conexão ruim não derruba o servidor.",
};

const blocos: Bloco[] = [
  {"p": "Num reator, todas as conexões dividem a mesma thread. Se um erro no tratamento de **uma** conexão subisse até o laço, derrubaria todas as outras. Por isso o erro é **anotado** e o laço segue — e as falhas ficam disponíveis para o log e para o teste."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
L.agendar(laco, lambda => 1 / 0)
atendidos := []
L.agendar(laco, lambda => atendidos.append("a outra conexão"))
L.apos(laco, 10, lambda => L.parar(laco))
L.rodar(laco)

assert atendidos is ["a outra conexão"]            // seguiu atendendo
f := L.falhas(laco)
assert len(f) is 1
out f[0]["erro"], f[0]["onde"]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Contada, não esquecida", "texto": "Engolir o erro em silêncio seria o outro extremo. `L.falhas(laco)` guarda cada um, com onde aconteceu e o tipo; `estatisticas()[\"erros\"]` conta. Um teste que roda o laço e não confere `falhas` está conferindo metade."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Quando algo falha no laço"}
      description={"Um erro num retorno de chamada é contado, e não propagado: uma conexão ruim não derruba o servidor."}
      href={"/docs/runtime/falhas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
