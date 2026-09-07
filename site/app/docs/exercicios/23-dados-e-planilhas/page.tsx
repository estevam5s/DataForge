import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "23 · Dados e planilhas",
  description: "Gravar e ler .xlsx, fórmulas, e o caminho do banco à planilha.",
};

const blocos: Bloco[] = [
  {"p": "Três exercícios sobre [`Arcane.Excel`](/docs/biblioteca/excel) e a ponte entre banco, análise e planilha."},
  { code: `python3 exercicios/run_all.py 23`, lang: 'bash' },
  {"p": "Cada um tem um `.md` ao lado explicando o conceito, comparando com outras linguagens e listando as armadilhas."},
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "O que ensina"], "rows": [["198", "**Gravar e ler uma planilha**", "Transforme uma lista de vaults num .xlsx e leia de volta"], ["199", "**Relatorio com varias abas e formulas**", "Monte um relatorio com formulas que o excel calcula ao abrir"], ["200", "**Do banco para a planilha, passando pela analise**", "Consulte o banco, analise os numeros e exporte a planilha"]]}},
  {"callout": {"tipo": "nota", "titulo": "O entregável é a planilha", "texto": "O banco é onde os dados moram, a análise responde à pergunta, e a planilha é o que se manda para quem decide. O exercício 200 percorre os três."}},
  {"h2": "198 · Gravar e ler uma planilha"},
  {"p": "Transforme uma lista de vaults num .xlsx e leia de volta."},
  { code: `// Exercicio 198 — Gravar e ler uma planilha
// Enunciado: transforme uma lista de vaults num .xlsx e leia de volta.

// Um .xlsx e um ZIP de arquivos XML. O Arcane.Excel escreve e le esse
// formato sem nenhuma dependencia externa — o arquivo abre no Excel, no
// LibreOffice e no Google Sheets.

adopt Arcane.Excel as Xls

vendas := [
    {"produto": "Martelo", "qtd": 12, "preco": 89.9},
    {"produto": "Bigorna", "qtd": 3,  "preco": 450.0},
    {"produto": "Tenaz",   "qtd": 27, "preco": 65.5}
]

// Quando os dados sao vaults, o cabecalho sai das chaves — em negrito,
// com a primeira linha congelada e a largura ajustada ao conteudo.
Xls.quick("/tmp/vendas.xlsx", vendas, "Vendas")
out "planilha gravada"

livro := Xls.read("/tmp/vendas.xlsx")
out "abas:", Xls.sheets(livro)
out "tamanho:", Xls.dims(livro, "Vendas")

linhas := Xls.rows(livro, "Vendas")
out "cabecalho:", linhas[0]
out "primeira linha:", linhas[1]

assert linhas[0] is ["produto", "qtd", "preco"], "o cabecalho veio das chaves"
assert linhas[1][1] is 12, "o numero voltou numero, nao texto"

// 'records' devolve vaults de novo, usando a linha de cabecalho.
de_volta := Xls.records(livro, "Vendas")
assert len(de_volta) is 3, "tres registros"
assert de_volta[0]["produto"] is "Martelo", "ida e volta sem perda"

// Uma coluna inteira, pelo titulo.
assert Xls.column(livro, "Vendas", "qtd") is [12, 3, 27], "coluna pelo nome"
` },
  {"h2": "199 · Relatorio com varias abas e formulas"},
  {"p": "Monte um relatorio com formulas que o excel calcula ao abrir."},
  { code: `// Exercicio 199 — Relatorio com varias abas e formulas
// Enunciado: monte um relatorio com formulas que o Excel calcula ao abrir.

// Formulas nao sao calculadas aqui: sao gravadas no arquivo e o Excel as
// resolve ao abrir. Isso e o que se quer num relatorio — quem receber
// pode mexer nos numeros e ver o total mudar sozinho.

adopt Arcane.Excel as Xls

itens := [
    {"produto": "Martelo", "qtd": 12, "preco": 89.9},
    {"produto": "Bigorna", "qtd": 3,  "preco": 450.0},
    {"produto": "Tenaz",   "qtd": 27, "preco": 65.5}
]

livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", itens)

// coluna de total: quantidade x preco, linha a linha
Xls.set(aba, "D1", "total")
cycle i from 2 to 4:
    Xls.formula(aba, $"D{i}", $"B{i}*C{i}")

// e a soma de tudo, uma linha abaixo
Xls.set(aba, "A5", "SOMA")
Xls.formula(aba, "D5", "SUM(D2:D4)")
Xls.bold_row(aba, 4)

// segunda aba, com o resumo
Xls.sheet(livro, "Resumo", [
    ["metrica", "valor"],
    ["itens", len(itens)],
    ["unidades", [i["qtd"] cycle i in itens] >> distill a, v: a + v 0]
])

Xls.save(livro, "/tmp/relatorio.xlsx")
out "relatorio com", len(Xls.sheets(livro)), "abas"

lido := Xls.read("/tmp/relatorio.xlsx")
vendas := Xls.sheet(lido, "Vendas")

out "abas:", Xls.sheets(lido)
out "formula da linha 2:", Xls.get_formula(vendas, "D2")
out "todas as formulas:", Xls.formulas(vendas)

assert Xls.sheets(lido) is ["Vendas", "Resumo"], "as duas abas, na ordem"
assert Xls.get_formula(vendas, "D5") is "SUM(D2:D4)", "a formula sobreviveu"
assert Xls.get_formula(vendas, "A1") is void, "celula sem formula devolve void"

resumo := Xls.records(lido, "Resumo")
out "resumo:", resumo
assert resumo[1]["valor"] is 42, "12 + 3 + 27 unidades"
` },
  {"h2": "200 · Do banco para a planilha, passando pela analise"},
  {"p": "Consulte o banco, analise os numeros e exporte a planilha."},
  { code: `// Exercicio 200 — Do banco para a planilha, passando pela analise
// Enunciado: consulte o banco, analise os numeros e exporte a planilha.

// Este e o caminho completo de um trabalho de dados: os dados moram no
// banco, a analise responde a pergunta, e a planilha e o que se manda
// para quem decide. As tres pecas conversam.

adopt Arcane.Database as DB
adopt Arcane.Analytics as An
adopt Arcane.Excel as Xls

// ── 1. o banco ──
banco := DB.connect(":memory:")
DB.execute(banco, """CREATE TABLE vendas (
    produto TEXT, regiao TEXT, qtd INTEGER, preco REAL)""")

cycle linha in [
    ["Martelo", "Sul",   12, 89.9],
    ["Bigorna", "Sul",    3, 450.0],
    ["Tenaz",   "Norte", 27, 65.5],
    ["Fole",    "Norte",  8, 320.0],
    ["Marreta", "Sul",   15, 110.0]
]:
    DB.execute(banco, "INSERT INTO vendas VALUES (?, ?, ?, ?)", linha)

registros := DB.query(banco, "SELECT * FROM vendas ORDER BY qtd DESC")
out "no banco:", len(registros), "vendas"
assert len(registros) is 5, "cinco linhas inseridas"

// ── 2. a analise ──
quantidades := [r["qtd"] cycle r in registros]
precos := [r["preco"] cycle r in registros]

out "media de unidades:", An.mean(quantidades)
out "desvio dos precos:", round(An.stdev(precos), 2)

// Preco e quantidade andam juntos? Correlacao negativa forte diria que
// o que e caro vende pouco.
correlacao := An.correlation(quantidades, precos)
out "correlacao qtd x preco:", round(correlacao, 3)
assert correlacao smaller 0, "quanto mais caro, menos unidades"

// describe() sobre um frame descreve cada coluna de uma vez
tabela := An.from_records(registros)
descricao := An.describe(tabela)
out "resumo da coluna qtd:", descricao["qtd"]["count"], "valores, media",
    descricao["qtd"]["mean"]
assert descricao["qtd"]["count"] is 5, "cinco valores numericos"
assert descricao["produto"]["type"] is "non-numeric", "texto e marcado como tal"

// ── 3. a planilha ──
livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", registros)

Xls.set(aba, "E1", "receita")
cycle i from 2 to 6:
    Xls.formula(aba, $"E{i}", $"C{i}*D{i}")
Xls.set(aba, "A7", "TOTAL")
Xls.formula(aba, "E7", "SUM(E2:E6)")
Xls.bold_row(aba, 6)

Xls.sheet(livro, "Estatisticas", [
    ["metrica", "valor"],
    ["vendas", len(registros)],
    ["media_qtd", An.mean(quantidades)],
    ["correlacao", round(correlacao, 3)]
])

Xls.save(livro, "/tmp/analise.xlsx")
out "planilha com", len(Xls.sheets(livro)), "abas gravada"

// e a prova de que tudo chegou inteiro
conferencia := Xls.read("/tmp/analise.xlsx")
assert Xls.sheets(conferencia) is ["Vendas", "Estatisticas"], "as duas abas"
// Seis registros, nao cinco: a linha TOTAL tambem e uma linha. Uma
// planilha para humanos e uma tabela para maquinas nao sao a mesma
// coisa, e vale saber disso antes de alimentar um script com ela.
de_volta := Xls.records(conferencia, "Vendas")
assert len(de_volta) is 6, "cinco vendas mais a linha de total"
assert de_volta[5]["produto"] is "TOTAL", "a ultima linha e o rodape"

// A coluna 'receita' volta vazia: e formula, e quem calcula e o Excel
// ao abrir o arquivo — nao nos.
assert de_volta[0]["receita"] is void, "formula nao tem valor gravado"
assert Xls.get_formula(Xls.sheet(conferencia, "Vendas"), "E7") is "SUM(E2:E6)",
    "a formula do total"

DB.close(banco)
` },
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '198--gravar-e-ler-uma-planilha', text: "198 · Gravar e ler uma planilha", level: 2 as const }, { id: '199--relatorio-com-varias-abas-e-formulas', text: "199 · Relatorio com varias abas e formulas", level: 2 as const }, { id: '200--do-banco-para-a-planilha-passando-pela-analise', text: "200 · Do banco para a planilha, passando pela analise", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"23 · Dados e planilhas"}
      description={"Gravar e ler .xlsx, fórmulas, e o caminho do banco à planilha."}
      href={"/docs/exercicios/23-dados-e-planilhas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
