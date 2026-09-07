import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise de vendas",
  description: "Lê CSV e produz relatório com estatística e gráficos de terminal.",
};

const blocos: Bloco[] = [
  { code: `dataforge run src/main.df -- dados/vendas.csv`, lang: 'bash' },
  { code: `┌───────────────┬──────────────┐
│ Indicador     │ Valor        │
├───────────────┼──────────────┤
│ Total         │ R$ 35.300,00 │
│ Ticket médio  │ R$ 2.353,33  │
│ Mediana       │ R$ 1.200,00  │
│ Desvio padrão │ R$ 1.991,27  │
└───────────────┴──────────────┘

  ⚠ dispersão alta: o ticket médio não representa bem as vendas.

Por região
  Nordeste   █████████░░░░░░░░░░░░░ R$ 7.200,00
  Sudeste    ██████████████████████ R$ 17.240,00
  Sul        ██████████████░░░░░░░░ R$ 10.860,00

Evolução mensal
  ▄▁█
Tendência: subindo R$ 345,00 por mês (r² = 0.269)
  (ajuste fraco — a tendência não é confiável com estes dados)`, lang: 'bash' },
  {"h2": "Centavos inteiros"},
  {"p": "O CSV traz `4500.00`; a leitura converte para 450000 centavos. Somar quinze floats acumula erro; somar inteiros não."},
  {"h2": "Falhar cedo"},
  { code: `    vendas := []
    numero := 1
    cycle linha in linhas[1:]:
        numero += 1
        given linha.trim() is "":
            skip
        campos := linha.split(",")
        given len(campos) isnt len(cabecalho):
            trigger $"linha {numero}: esperava {len(cabecalho)} colunas, veio {len(campos)}"

        monitor:
            vendas.append(Venda(
                campos[0].trim(), campos[1].trim(), campos[2].trim(),
                campos[3].trim(), M.de_texto(campos[4]).centavos))
        handle e:
            trigger $"linha {numero}: valor invalido ({campos[4]})"`, lang: 'df' },
  {"p": "Uma linha com valor inválido aborta a leitura dizendo o número da linha — melhor que um `void` chegar a uma soma e produzir um total errado em silêncio."},
  {"h2": "O relatório desconfia de si mesmo"},
  {"p": "Quando o desvio passa de metade da média, avisa que o ticket médio não descreve as vendas. Quando o r² é baixo, avisa que a tendência não é confiável."},
  {"p": "Um relatório que só apresenta números convida a conclusões que os dados não sustentam. Dizer onde a estatística é fraca faz parte de apresentá-la."},
];

const headings = [{ id: 'centavos-inteiros', text: "Centavos inteiros", level: 2 as const }, { id: 'falhar-cedo', text: "Falhar cedo", level: 2 as const }, { id: 'o-relatorio-desconfia-de-si-mesmo', text: "O relatório desconfia de si mesmo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise de vendas"}
      description={"Lê CSV e produz relatório com estatística e gráficos de terminal."}
      href={"/docs/projetos/analise-vendas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
