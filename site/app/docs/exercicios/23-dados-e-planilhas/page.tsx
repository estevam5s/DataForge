// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "23 · Dados e planilhas",
  description: "3 exercícios: frames, agregação e .xlsx.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Aplicações** · frames, agregação e .xlsx · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 23`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[200](#200-gravar-e-ler-uma-planilha)", "**Gravar e ler uma planilha**", "transforme uma lista de vaults num .xlsx e leia de volta."], ["[201](#201-relatorio-com-varias-abas-e-formulas)", "**Relatorio com varias abas e formulas**", "monte um relatorio com formulas que o Excel calcula ao abrir."], ["[202](#202-do-banco-para-a-planilha-passando-pela-analise)", "**Do banco para a planilha, passando pela analise**", "consulte o banco, analise os numeros e exporte a planilha."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "200 · Gravar e ler uma planilha"},
  {"p": "**Enunciado.** transforme uma lista de vaults num .xlsx e leia de volta."},
  { code: `// Um .xlsx e um ZIP de arquivos XML. O Arcane.Excel escreve e le esse
// formato sem nenhuma dependencia externa — o arquivo abre no Excel, no
// LibreOffice e no Google Sheets.

adopt Arcane.Excel as Xls
adopt Arcane.OS as OS
adopt Arcane.IO as IO

vendas := [
    {"produto": "Martelo", "qtd": 12, "preco": 89.9},
    {"produto": "Bigorna", "qtd": 3, "preco": 450.0},
    {"produto": "Tenaz", "qtd": 27, "preco": 65.5}
]

// Quando os dados sao vaults, o cabecalho sai das chaves — em negrito,
// com a primeira linha congelada e a largura ajustada ao conteudo.
Xls.quick(IO.join(OS.temp_dir(), "vendas.xlsx"), vendas, "Vendas")
out "planilha gravada"

livro := Xls.read(IO.join(OS.temp_dir(), "vendas.xlsx"))
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
assert Xls.column(livro, "Vendas", "qtd") is [12, 3, 27], "coluna pelo nome"`, lang: 'df', title: `exercicios/23-dados-e-planilhas/200_primeira_planilha.df` },
  {"h3": "Conceitos"},
  {"p": "Um `.xlsx` é um ZIP de arquivos XML. O `Arcane.Excel` escreve e lê esse formato **sem nenhuma dependência externa** — o arquivo abre no Excel, no LibreOffice e no Google Sheets, e é lido de volta por openpyxl e pandas."},
  { code: `adopt Arcane.Excel as Xls

Xls.quick("/tmp/vendas.xlsx", vendas, "Vendas")
livro := Xls.read("/tmp/vendas.xlsx")`, lang: 'df' },
  {"table": {"head": ["Função", "Devolve"], "rows": [["`Xls.rows(livro, aba)`", "lista de listas, com `void` nos buracos"], ["`Xls.records(livro, aba)`", "lista de vaults, usando a linha de cabeçalho"], ["`Xls.column(livro, aba, \"qtd\")`", "uma coluna, pelo título ou pela letra"], ["`Xls.dims(livro, aba)`", "linhas, colunas e células ocupadas"]]}},
  {"h3": "O que observar"},
  {"p": "**Dados em vault viram tabela sozinhos.** O cabeçalho sai das chaves, em negrito, com a primeira linha congelada e a largura ajustada ao conteúdo — sem isso a planilha abre com colunas de `####`."},
  {"p": "**Os tipos sobrevivem.** `12` volta inteiro, `89.9` volta real, `yes` volta booleano, uma data volta data. Um número que chega como texto abre a planilha com tudo alinhado à esquerda e nada soma."},
  {"p": "**A planilha é esparsa.** Escrever em `Z100` não materializa 100 linhas vazias: ficam duas células ocupadas, e o arquivo reflete isso."},
  {"p": "**Título vence letra de coluna.** Numa planilha com uma coluna chamada `B`, pedir `\"B\"` traz essa coluna — não a segunda."},
  {"h3": "Erros comuns"},
  {"list": ["Esperar que `records` pule uma linha de totais. Para ele, é uma linha como"]},
  {"p": "qualquer outra."},
  {"list": ["Usar `frame` como nome de variável. É palavra reservada; use outro nome."]},
  {"h2": "201 · Relatorio com varias abas e formulas"},
  {"p": "**Enunciado.** monte um relatorio com formulas que o Excel calcula ao abrir."},
  { code: `// Formulas nao sao calculadas aqui: sao gravadas no arquivo e o Excel as
// resolve ao abrir. Isso e o que se quer num relatorio — quem receber
// pode mexer nos numeros e ver o total mudar sozinho.

adopt Arcane.Excel as Xls
adopt Arcane.OS as OS
adopt Arcane.IO as IO

itens := [
    {"produto": "Martelo", "qtd": 12, "preco": 89.9},
    {"produto": "Bigorna", "qtd": 3, "preco": 450.0},
    {"produto": "Tenaz", "qtd": 27, "preco": 65.5}
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
        ["unidades", [i["qtd"] cycle i in itens] >> distill a, v:a + v 0]
    ])

Xls.save(livro, IO.join(OS.temp_dir(), "relatorio.xlsx"))
out "relatorio com", len(Xls.sheets(livro)), "abas"

lido := Xls.read(IO.join(OS.temp_dir(), "relatorio.xlsx"))
vendas := Xls.sheet(lido, "Vendas")

out "abas:", Xls.sheets(lido)
out "formula da linha 2:", Xls.get_formula(vendas, "D2")
out "todas as formulas:", Xls.formulas(vendas)

assert Xls.sheets(lido) is ["Vendas", "Resumo"], "as duas abas, na ordem"
assert Xls.get_formula(vendas, "D5") is "SUM(D2:D4)", "a formula sobreviveu"
assert Xls.get_formula(vendas, "A1") is void, "celula sem formula devolve void"

resumo := Xls.records(lido, "Resumo")
out "resumo:", resumo
assert resumo[1]["valor"] is 42, "12 + 3 + 27 unidades"`, lang: 'df', title: `exercicios/23-dados-e-planilhas/201_relatorio_com_formulas.df` },
  {"h3": "Conceitos"},
  { code: `Xls.formula(aba, "D5", "SUM(D2:D4)")
Xls.bold_row(aba, 4)
Xls.freeze(aba, "A2")`, lang: 'df' },
  {"table": {"head": ["Função", "Faz"], "rows": [["`Xls.formula(aba, ref, expr)`", "grava uma fórmula"], ["`Xls.get_formula(aba, ref)`", "lê de volta, ou `void`"], ["`Xls.formulas(aba)`", "todas, por endereço"], ["`Xls.bold_row` / `freeze` / `width` / `autofit`", "formatação"]]}},
  {"h3": "O que observar"},
  {"p": "**Fórmula não é calculada aqui.** Ela é gravada no arquivo, e o Excel a resolve ao abrir. É o que se quer num relatório: quem receber pode mexer nos números e ver o total mudar sozinho. Um valor calculado em DataForge seria um número morto."},
  {"p": "**Por isso a coluna de fórmulas volta vazia na leitura.** `Xls.rows` mostra `void` onde há fórmula sem valor gravado — não há bug ali."},
  {"p": "**O `=` inicial é opcional.** `\"=SUM(A1:A9)\"` e `\"SUM(A1:A9)\"` gravam a mesma coisa."},
  {"h3": "Erros comuns"},
  {"list": ["Escrever a fórmula como texto com `Xls.set`. Vira uma célula de texto que"]},
  {"p": "mostra `=SUM(...)` em vez de calcular."},
  {"list": ["Contar as linhas errado. `D5` é a quinta linha; em `Xls.cell(aba, 4, 3)` os"]},
  {"p": "índices começam em zero."},
  {"h2": "202 · Do banco para a planilha, passando pela analise"},
  {"p": "**Enunciado.** consulte o banco, analise os numeros e exporte a planilha."},
  { code: `// Este e o caminho completo de um trabalho de dados: os dados moram no
// banco, a analise responde a pergunta, e a planilha e o que se manda
// para quem decide. As tres pecas conversam.

adopt Arcane.Database as DB
adopt Arcane.Analytics as An
adopt Arcane.Excel as Xls
adopt Arcane.OS as OS
adopt Arcane.IO as IO

// ── 1. o banco ──
banco := DB.connect(":memory:")
DB.execute(banco, """CREATE TABLE vendas (
    produto TEXT, regiao TEXT, qtd INTEGER, preco REAL)""")

cycle linha in [
    ["Martelo", "Sul", 12, 89.9],
    ["Bigorna", "Sul", 3, 450.0],
    ["Tenaz", "Norte", 27, 65.5],
    ["Fole", "Norte", 8, 320.0],
    ["Marreta", "Sul", 15, 110.0]
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

Xls.save(livro, IO.join(OS.temp_dir(), "analise.xlsx"))
out "planilha com", len(Xls.sheets(livro)), "abas gravada"

// e a prova de que tudo chegou inteiro
conferencia := Xls.read(IO.join(OS.temp_dir(), "analise.xlsx"))
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

DB.close(banco)`, lang: 'df', title: `exercicios/23-dados-e-planilhas/202_planilha_banco_e_analise.df` },
  {"h3": "Conceitos"},
  {"p": "Este é o caminho completo de um trabalho de dados, e as três peças conversam:"},
  { code: `registros := DB.query(banco, "SELECT * FROM vendas")
tabela    := An.from_records(registros)     // vira frame de análise
Xls.sheet(livro, "Vendas", registros)       // vira planilha`, lang: 'df' },
  {"table": {"head": ["Módulo", "Para"], "rows": [["`Arcane.Database`", "SQLite: consultas, migrações, transações, modelos"], ["`Arcane.Analytics`", "média, desvio, correlação, regressão, `describe`"], ["`Arcane.Excel`", "ler e gravar `.xlsx`"], ["`Arcane.IO`", "ler e gravar arquivos, CSV, JSON"]]}},
  {"p": "`Xls.to_frame(livro, aba)` faz o caminho inverso: planilha → frame."},
  {"h3": "O que observar"},
  {"p": "**`describe` sobre um frame descreve cada coluna.** Sobre uma lista, descreve a lista. Colunas de texto aparecem marcadas como `non-numeric` em vez de zerarem o resultado inteiro — silenciosamente, que era o comportamento antigo."},
  {"p": "**Booleano não é número aqui.** Em Python `True` vale 1; numa coluna de dados isso é ruído, e `describe` os ignora."},
  {"p": "**Correlação negativa forte** entre quantidade e preço (`-0,825` no exercício) diz que o caro vende pouco. É o tipo de resposta que justifica o trabalho todo."},
  {"p": "**A planilha é o entregável.** O banco é onde os dados moram, a análise responde a pergunta, e a planilha é o que se manda para quem decide."},
  {"h3": "Erros comuns"},
  {"list": ["Analisar a planilha em vez do banco. A planilha tem linha de total e"]},
  {"p": "cabeçalho; o banco tem só os dados."},
  {"list": ["Esquecer `DB.close`. Com `:memory:` não faz diferença; com arquivo, faz."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/23-dados-e-planilhas/200_primeira_planilha.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '200-gravar-e-ler-uma-planilha', text: "200 · Gravar e ler uma planilha", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '201-relatorio-com-varias-abas-e-formulas', text: "201 · Relatorio com varias abas e formulas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '202-do-banco-para-a-planilha-passando-pela-analise', text: "202 · Do banco para a planilha, passando pela analise", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"23 · Dados e planilhas"}
      description={"3 exercícios: frames, agregação e .xlsx."}
      href={"/docs/exercicios/23-dados-e-planilhas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
