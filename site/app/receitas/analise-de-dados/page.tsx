import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise de dados",
  description: "Carregar, descrever, agregar e projetar — o fluxo completo de uma análise.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `176_analise_dados.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Analytics as An
adopt Arcane.Math as Math
adopt Arcane.Text as Text
adopt Arcane.Collections as Col

// ═══ DADOS ═══

record Venda:
    mes: Integer
    vendedor: String
    regiao: String
    valor: Number

bruto := [
    [1, "Ana", "sul", 12000], [1, "Bruno", "norte", 8500],
    [1, "Carla", "sul", 15000], [2, "Ana", "sul", 13500],
    [2, "Bruno", "norte", 9200], [2, "Carla", "sul", 11000],
    [3, "Ana", "sul", 16000], [3, "Bruno", "norte", 7800],
    [3, "Carla", "sul", 18500], [4, "Ana", "sul", 14200],
    [4, "Bruno", "norte", 11000], [4, "Carla", "sul", 19000]
]

vendas := bruto >> morph l: Venda(l[0], l[1], l[2], l[3])
valores := vendas >> morph v: v.valor

out Text.box("Analise de Vendas")

// ═══ ESTATISTICA DESCRITIVA ═══

out ""
out "── resumo ──"
out $"  registros:     {len(vendas)}"
out $"  total:         R$ {sum(valores)}"
out $"  media:         R$ {round(Math.mean(valores), 2)}"
out $"  mediana:       R$ {Math.median(valores)}"
out $"  desvio padrao: R$ {round(Math.stdev(valores), 2)}"
out $"  minimo:        R$ {min(valores)}"
out $"  maximo:        R$ {max(valores)}"

assert len(vendas) is 12, "doze registros"
assert sum(valores) is 155700, "total"

// ═══ QUARTIS E OUTLIERS ═══

q := An.quartiles(valores)
out ""
out "── distribuicao ──"
out $"  Q1: R$ {q["Q1"]}   Q2: R$ {q["Q2"]}   Q3: R$ {q["Q3"]}"
out $"  amplitude interquartil: R$ {An.iqr(valores)}"

outliers := An.outliers(valores)
out $"  outliers: {outliers}"

// ═══ AGREGACAO ═══

out ""
out "── por vendedor ──"
por_vendedor := Col.group_by(vendas, "vendedor")
resumos := []
cycle nome in sorted(por_vendedor.keys()):
    v := por_vendedor[nome] >> morph x: x.valor
    resumos.append({"nome": nome, "total": sum(v), "media": round(Math.mean(v), 2)})

cycle r in Col.sort_by_field(resumos, "total", yes):
    barra := "#".repeat(r["total"] * 30 ~/ max(sum(valores), 1))
    out $"  {r["nome"].pad_end(8)}R$ {str(r["total"]).pad_start(7)}  {barra}"

assert len(resumos) is 3, "tres vendedores"

out ""
out "── por regiao ──"
por_regiao := Col.group_by(vendas, "regiao")
cycle regiao in sorted(por_regiao.keys()):
    v := por_regiao[regiao] >> morph x: x.valor
    fatia := round(sum(v) * 100 / sum(valores), 1)
    out $"  {regiao.pad_end(8)}R$ {str(sum(v)).pad_start(7)}  ({fatia}%)"

// ═══ SERIE TEMPORAL ═══

out ""
out "── evolucao mensal ──"
por_mes := {}
cycle v in vendas:
    por_mes[v.mes] := por_mes.get(v.mes, 0) + v.valor

meses := sorted(por_mes.keys())
serie := meses >> morph m: por_mes[m]
maximo := max(serie)

cycle m in meses:
    total := por_mes[m]
    barra := "█".repeat(max(1, total * 30 ~/ maximo))
    out $"  mes {m}: {barra} R$ {total}"

assert len(meses) is 4, "quatro meses"

// ═══ TENDENCIA ═══

correlacao := An.correlation(meses, serie)
modelo := An.linear_regression(meses, serie)
previsao := An.predict_linear(modelo, 5)

out ""
out "── tendencia ──"
out $"  correlacao mes x total: {round(correlacao, 4)}"
out $"  reta: y = {round(modelo["slope"], 2)}x + {round(modelo["intercept"], 2)}"
out $"  ajuste (R2): {round(An.r_squared(meses, serie), 4)}"
out $"  previsao para o mes 5: R$ {round(previsao, 2)}"

assert correlacao bigger 0, "vendas crescendo"
assert previsao bigger serie[len(serie) - 1], "previsao acima do ultimo mes"

// ═══ MEDIA MOVEL ═══

out ""
out "── media movel (2 meses) ──"
movel := An.moving_average(serie, 2)
cycle i from 0 to len(movel) - 1:
    out $"  janela {i + 1}: R$ {round(movel[i], 2)}"

// ═══ CONCLUSAO ═══

melhor := Col.sort_by_field(resumos, "total", yes)[0]
crescimento := round((serie[len(serie) - 1] - serie[0]) * 100 / serie[0], 1)

out ""
out Text.box("Conclusao")
out $"  melhor vendedor: {melhor["nome"]} (R$ {melhor["total"]})"
out $"  crescimento no periodo: {crescimento}%"
out $"  ticket medio: R$ {round(Math.mean(valores), 2)}"

assert melhor["nome"] is "Carla", "Carla vendeu mais"
assert crescimento bigger 0, "houve crescimento"`, title: `176_analise_dados.df` },
  {"h2": "As cinco etapas"},
  {"table": {"head": ["Etapa", "Faz"], "rows": [["**Modelar**", "converte listas anônimas em records tipados"], ["**Descrever**", "média, mediana, desvio, quartis"], ["**Agregar**", "por vendedor, por região, por mês"], ["**Visualizar**", "histogramas em texto"], ["**Projetar**", "correlação, regressão, previsão"]]}},
  {"h2": "Média e mediana contam histórias diferentes"},
  {"p": "Quando as duas divergem muito, a distribuição é assimétrica — geralmente por causa de poucos valores muito altos ou baixos. Olhar as duas é mais informativo que olhar só a média."},
  {"h2": "Cuidado com extrapolação"},
  {"p": "Prever o mês 5 a partir de 4 meses é razoável; prever o mês 50 não é. A reta descreve o passado observado, não garante o futuro."},
  {"p": "As funções estão em [Arcane.Analytics](/biblioteca/analytics)."},
];

const headings = [{ id: 'as-cinco-etapas', text: "As cinco etapas", level: 2 as const }, { id: 'media-e-mediana-contam-historias-diferentes', text: "Média e mediana contam histórias diferentes", level: 2 as const }, { id: 'cuidado-com-extrapolacao', text: "Cuidado com extrapolação", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise de dados"}
      description={"Carregar, descrever, agregar e projetar — o fluxo completo de uma análise."}
      href={"/receitas/analise-de-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
