// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pivotar e despivotar",
  description: "Linhas viram colunas (a tabela dinâmica) e voltam — e a célula sem dado que sai 0.",
};

const blocos: Bloco[] = [
  {"p": "`pivotar` transforma valores de uma coluna em colunas — a tabela dinâmica da planilha. `despivotar` faz o caminho de volta. Os dois existem porque cada forma serve a uma coisa: a larga para ler, a longa para calcular."},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "A", "mes": "jan", "valor": 10}, {"loja": "A", "mes": "fev", "valor": 20},
    {"loja": "B", "mes": "jan", "valor": 5}, {"loja": "B", "mes": "jan", "valor": 5}])

larga := v.pivotar("loja", "mes", "valor")      // soma por padrao
out larga.texto()
assert larga.onde(lambda l: l["loja"] is "B").coluna("jan") is [10]

longa := larga.despivotar(["loja"], "mes", "valor")
assert longa.altura() is 4`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Com `soma`, a célula sem dado sai 0", "texto": "A loja B não vendeu em fevereiro, e a célula `B/fev` sai **0**, e não `void`. Para uma soma isso é defensável — nada vendido soma zero —, mas uma média de uma célula 0 não é a média de nada. Se a diferença entre *“vendeu zero”* e *“não há registro”* importa, faça a contagem ao lado: `v.tabela_cruzada(\"loja\", \"mes\")`."}},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([{"loja": "A", "mes": "jan"}, {"loja": "B", "mes": "jan"}, {"loja": "B", "mes": "jan"}])
t := v.tabela_cruzada("loja", "mes")
assert t.onde(lambda l: l["loja"] is "B").coluna("jan") is [2]
out t.texto()`, lang: 'df' },
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Pivotar e despivotar"}
      description={"Linhas viram colunas (a tabela dinâmica) e voltam — e a célula sem dado que sai 0."}
      href={"/docs/dados/pivotar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
