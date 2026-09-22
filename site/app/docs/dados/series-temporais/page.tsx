// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Séries temporais",
  description: "Por loja, por dia: agrupar, ordenar e aplicar a janela em cada grupo — e a lacuna no calendário.",
};

const blocos: Bloco[] = [
  {"p": "Uma série temporal quase nunca é uma só: é uma por loja, por produto, por cliente. A janela precisa ser calculada **dentro** de cada série — senão a média móvel do norte usa o último dia do centro."},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"dia": "2026-09-01", "loja": "centro", "valor": 120},
    {"dia": "2026-09-02", "loja": "centro", "valor": 150},
    {"dia": "2026-09-03", "loja": "centro", "valor": void},
    {"dia": "2026-09-04", "loja": "centro", "valor": 90},
    {"dia": "2026-09-05", "loja": "centro", "valor": 200},
    {"dia": "2026-09-01", "loja": "norte", "valor": 80},
    {"dia": "2026-09-02", "loja": "norte", "valor": 60}])

partes := []
cycle chave in unique(vendas.coluna("loja")):
    serie := vendas.onde(lambda l: l["loja"] is chave).ordenar("dia")
    partes.append(serie.acumulado("valor").variacao("valor"))

resultado := partes[0]
cycle p in partes[1:]:
    resultado := resultado.empilhar(p)

norte := resultado.onde(lambda l: l["loja"] is "norte")
assert norte.coluna("valor_soma_acumulado") is [80, 140]
assert norte.coluna("valor_variacao") is [void, -0.25]
out resultado.pegar("loja", "dia", "valor_soma_acumulado").texto()`, lang: 'df' },
  {"h2": "A lacuna no calendário"},
  {"p": "Se não houve venda no dia 3, a linha do dia 3 **não existe** — e `defasar` devolve o dia 2 como *“ontem”* do dia 4. Para uma série diária de verdade, complete o calendário antes, com `void` nos dias sem registro:"},
  { code: `adopt Arcane.Quadro as Q

registros := {"2026-09-01": 10, "2026-09-02": 12, "2026-09-04": 9}
dias := ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"]
serie := Q.de_vaults(dias >> morph d: {"dia": d, "valor": registros[d] ?? void})

assert serie.coluna("valor") is [10, 12, void, 9]
assert serie.defasar("valor").coluna("valor_antes_1")[3] is void    // o dia 3, e nao o 2`, lang: 'df' },
];

const headings = [{ id: 'a-lacuna-no-calendario', text: "A lacuna no calendário", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Séries temporais"}
      description={"Por loja, por dia: agrupar, ordenar e aplicar a janela em cada grupo — e a lacuna no calendário."}
      href={"/docs/dados/series-temporais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
