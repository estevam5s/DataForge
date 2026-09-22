// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Linhagem de dados",
  description: "De onde veio este número, e o que muda se a fonte mudar: o grafo de derivação, para trás e para a frente.",
};

const blocos: Bloco[] = [
  {"p": "O relatório mostra um faturamento estranho. De onde veio esse número? A **linhagem** registra, a cada transformação, o que entrou e o que saiu — e responde nas duas direções: a **origem** de um dado e o **impacto** de mexer numa fonte."},
  { code: `adopt Arcane.Observar as O

p := O.painel("etl")
O.derivar(p, "vendas_limpas", ["vendas.csv"], "remove duplicadas")
O.derivar(p, "faturamento", ["vendas_limpas", "precos.db"], "soma por mês")
O.derivar(p, "painel_diretoria", ["faturamento"], "gráfico")

de_onde := [a["de"] cycle a in O.origem(p, "faturamento")]
assert de_onde.contains("vendas.csv") and de_onde.contains("precos.db")

afetados := O.impacto(p, "precos.db")
assert afetados.contains("painel_diretoria")     // mexer nos preços muda o painel`, lang: 'df' },
  {"table": {"head": ["Pergunta", "Função"], "rows": [["de onde veio?", "`O.origem(p, dado)` — para trás, com o nível"], ["o que quebra se eu mudar?", "`O.impacto(p, fonte)` — para a frente"], ["o grafo inteiro", "`O.grafo(p)`"]]}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Linhagem de dados"}
      description={"De onde veio este número, e o que muda se a fonte mudar: o grafo de derivação, para trás e para a frente."}
      href={"/docs/observabilidade/linhagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
