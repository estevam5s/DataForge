import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "20 · Projetos finais",
  description: "6 exercícios: CLI, análise de dados, interpretador e revisão.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 20`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["175", "**Projeto: ferramenta de linha de comando**", "escreva um utilitario que analisa arquivos e imprime um relatorio."], ["176", "**Projeto: analise de dados**", "carregue, limpe, agregue e visualize um conjunto de dados."], ["177", "**Projeto: mini linguagem**", "escreva um interpretador de expressoes dentro do DataForge."], ["178", "**Projeto: sistema de biblioteca**", "integre records, enums, banco, validacao e relatorios."], ["179", "**Revisao: todos os conceitos**", "um programa que exercita cada recurso da linguagem."], ["180", "**Encerramento e proximos passos**", "o que voce aprendeu, o que a linguagem ainda nao faz e para onde ir."]]}},
  {"h2": "175 · Projeto: ferramenta de linha de comando"},
  {"p": "Escreva um utilitario que analisa arquivos e imprime um relatorio."},
  { code: `// Exercicio 175 — Projeto: ferramenta de linha de comando
// Enunciado: escreva um utilitario que analisa arquivos e imprime um relatorio.

adopt Arcane.IO as IO
adopt Arcane.Text as Text
adopt Arcane.Collections as Col
adopt Arcane.Time as Time

// ═══ MODELO ═══

record Arquivo:
    nome: String
    extensao: String
    bytes: Integer
    linhas: Integer

// ═══ ANALISE ═══

action analisar(caminho: String) -> Arquivo:
    conteudo := IO.read(caminho)
    yield Arquivo(
        IO.basename(caminho),
        IO.ext(caminho) ?? "(sem)",
        IO.size(caminho),
        len(conteudo.lines())
    )

action formatar_bytes(n: Number) -> String:
    given n smaller 1024:
        yield $"{n} B"
    orif n smaller 1048576:
        yield $"{round(n / 1024, 1)} KB"
    yield $"{round(n / 1048576, 2)} MB"

// ═══ PREPARO: uma pasta de exemplo ═══

pasta := "_projeto_175"
IO.mkdir(pasta)

exemplos := {
    "notas.txt": "linha 1\\nlinha 2\\nlinha 3",
    "config.json": "{\\"tema\\": \\"escuro\\", \\"fonte\\": 14}",
    "dados.csv": "nome,valor\\nA,1\\nB,2\\nC,3\\nD,4",
    "leiame.md": "# Titulo\\n\\nUm paragrafo.",
    "script.df": "action f():\\n    yield 1\\nout f()"
}
cycle nome in exemplos.keys():
    IO.write(IO.join(pasta, nome), exemplos[nome])

// ═══ RELATORIO ═══

arquivos := IO.list_dir(pasta) >> morph nome: analisar(IO.join(pasta, nome))

out Text.box("Analise de Arquivos")
out ""
out $"  {"ARQUIVO".pad_end(14)}{"EXT".pad_end(8)}{"TAMANHO".pad_start(10)}{"LINHAS".pad_start(8)}"
out $"  {"-".repeat(40)}"

cycle a in Col.sort_by_field(arquivos, "bytes", yes):
    out $"  {a.nome.pad_end(14)}{a.extensao.pad_end(8)}{formatar_bytes(a.bytes).pad_start(10)}{str(a.linhas).pad_start(8)}"

assert len(arquivos) is 5, "cinco arquivos"

// ── totais ──
total_bytes := arquivos >> morph a: a.bytes >> distill acc, b: acc + b 0
total_linhas := arquivos >> morph a: a.linhas >> distill acc, l: acc + l 0

out ""
out $"  total: {len(arquivos)} arquivos, {formatar_bytes(total_bytes)}, {total_linhas} linhas"
assert total_linhas is 15, "soma das linhas"

// ── por extensao ──
out ""
out "  ── por extensao ──"
por_ext := Col.group_by(arquivos, "extensao")
cycle ext in sorted(por_ext.keys()):
    grupo := por_ext[ext]
    soma := grupo >> morph a: a.bytes >> distill acc, b: acc + b 0
    barra := "#".repeat(max(1, soma * 20 ~/ max(total_bytes, 1)))
    out $"  {ext.pad_end(8)}{str(len(grupo)).pad_start(3)}  {barra} {formatar_bytes(soma)}"

assert len(por_ext.keys()) is 5, "cinco extensoes distintas"

// ── o maior e o menor ──
maior := Col.sort_by_field(arquivos, "bytes", yes)[0]
menor := Col.sort_by_field(arquivos, "bytes")[0]
out ""
out $"  maior: {maior.nome} ({formatar_bytes(maior.bytes)})"
out $"  menor: {menor.nome} ({formatar_bytes(menor.bytes)})"

// ── busca por conteudo ──
out ""
out "  ── procurando por 'linha' ──"
achados := []
cycle nome in IO.list_dir(pasta):
    caminho := IO.join(pasta, nome)
    conteudo := IO.read(caminho)
    numero := 0
    cycle l in conteudo.lines():
        numero += 1
        given "linha" in l.lower():
            achados.append($"{nome}:{numero}: {l.trim()}")

cycle a in achados:
    out $"    {a}"
assert len(achados) is 3, "tres ocorrencias"

// ═══ LIMPEZA ═══
cycle nome in IO.list_dir(pasta):
    IO.delete(IO.join(pasta, nome))
IO.delete(pasta)
out ""
out "  (pasta temporaria removida)"
`, title: `175_cli_arquivos.df` },
  {"h2": "176 · Projeto: analise de dados"},
  {"p": "Carregue, limpe, agregue e visualize um conjunto de dados."},
  { code: `// Exercicio 176 — Projeto: analise de dados
// Enunciado: carregue, limpe, agregue e visualize um conjunto de dados.

adopt Arcane.Analytics as An
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
assert crescimento bigger 0, "houve crescimento"
`, title: `176_analise_dados.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/20-projetos-finais/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '175--projeto-ferramenta-de-linha-de-comando', text: "175 · Projeto: ferramenta de linha de comando", level: 2 as const }, { id: '176--projeto-analise-de-dados', text: "176 · Projeto: analise de dados", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"20 · Projetos finais"}
      description={"6 exercícios: CLI, análise de dados, interpretador e revisão."}
      href={"/exercicios/20-projetos-finais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
