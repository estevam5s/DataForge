# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de excel.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{"p": "Um `.xlsx` é um ZIP de arquivos XML. O `Arcane.Excel` escreve e lê esse formato usando só a biblioteca padrão do Python — o arquivo abre no Excel, no LibreOffice e no Google Sheets, e é lido de volta por openpyxl e pandas."}''',
    r'''{"h2": "O caminho curto"}''',
    r'''{ code: `adopt Arcane.Excel as Xls

vendas := [
    {"produto": "Martelo", "qtd": 12, "preco": 89.9},
    {"produto": "Bigorna", "qtd": 3,  "preco": 450.0}
]

Xls.quick("vendas.xlsx", vendas, "Vendas")` }''',
    r'''{"p": "Quando os dados são vaults, o cabeçalho sai das chaves — em negrito, com a primeira linha congelada e a largura ajustada ao conteúdo. Sem isso, a planilha abre com colunas de `####`."}''',
    r'''{"h2": "Ler"}''',
    r'''{ code: `livro := Xls.read("vendas.xlsx")

Xls.sheets(livro)                    // ["Vendas"]
Xls.dims(livro, "Vendas")            // {linhas: 3, colunas: 3, celulas: 9}
Xls.rows(livro, "Vendas")            // lista de listas
Xls.records(livro, "Vendas")         // lista de vaults, pelo cabeçalho
Xls.column(livro, "Vendas", "qtd")   // [12, 3]
Xls.get(Xls.sheet(livro, "Vendas"), "B2")   // 12` }''',
    r'''{"p": "`column` aceita o **título** ou a letra. O título vence: numa planilha com uma coluna chamada `B`, pedir `\"B\"` traz essa coluna, não a segunda."}''',
    r'''{"h2": "Os tipos sobrevivem"}''',
    r'''{"table": {"head": ["Grava", "Volta como"], "rows": [
    ["`42`", "`Integer`"],
    ["`89.9`", "`Float`"],
    ["`yes` / `no`", "`Boolean`"],
    ["uma data", "data (o formato do Excel é um número; o módulo reconhece)"],
    ["texto", "`String`"],
    ["`void`", "célula vazia — e ela não ocupa espaço"]
  ]}}''',
    r'''{"p": "Um número que chega como texto abre a planilha com tudo alinhado à esquerda e nada soma. Por isso `from_csv` converte o que parece número."}''',
    r'''{"h2": "Montar com cuidado"}''',
    r'''{ code: `livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", vendas)

Xls.set(aba, "D1", "total")
cycle i from 2 to 3:
    Xls.formula(aba, $"D{i}", $"B{i}*C{i}")

Xls.set(aba, "A4", "SOMA")
Xls.formula(aba, "D4", "SUM(D2:D3)")
Xls.bold_row(aba, 3)
Xls.freeze(aba, "A2")
Xls.width(aba, "A", 28)

Xls.save(livro, "relatorio.xlsx")` }''',
    r'''{"h2": "Fórmulas"}''',
    r'''{"p": "Uma fórmula **não é calculada aqui**: é gravada, e o Excel a resolve ao abrir. É o que se quer num relatório — quem receber pode mexer nos números e ver o total mudar sozinho. Um valor calculado em DataForge seria um número morto."}''',
    r'''{ code: `Xls.get_formula(aba, "D4")     // "SUM(D2:D3)"
Xls.formulas(aba)              // {"D2": "B2*C2", "D4": "SUM(D2:D3)"}` }''',
    r'''{"p": "Por isso a coluna de fórmulas volta vazia em `rows`: não há valor gravado, e isso não é um bug."}''',
    r'''{"h2": "Converter"}''',
    r'''{ code: `Xls.from_csv("dados.csv")           // CSV  → livro
Xls.to_csv(livro, "saida.csv")      // livro → CSV
Xls.to_frame(livro, "Vendas")       // livro → frame do Analytics
Xls.from_frame(tabela, "Dados")     // frame → livro` }''',
    r'''{"p": "`to_frame` é a ponte para o `Arcane.Analytics`: a planilha vira uma tabela que `describe`, `correlation` e `group_by` entendem."}''',
    r'''{"h2": "Planilha esparsa"}''',
    r'''{ code: `aba := Xls.sheet(livro, "T")
Xls.set(aba, "A1", "canto")
Xls.set(aba, "Z100", "outro canto")
// duas células ocupadas, não 2.600` }''',
    r'''{"p": "As células ficam num mapa esparso. Escrever em `Z100` não materializa 100 linhas vazias — nem no programa, nem no arquivo."}''',
    r'''{"h2": "Endereços"}''',
    r'''{ code: `Xls.addr(0, 0)          // "A1"
Xls.addr(6, 1)          // "B7"
Xls.parse_addr("B7")    // {linha: 6, coluna: 1}
Xls.col_letter(26)      // "AA"` }''',
    r'''{"p": "Nos endereços em texto (`\"B7\"`) a contagem começa em 1, como no Excel. Em `Xls.cell(aba, linha, coluna)` começa em 0, como no resto da linguagem."}''',
    r'''{"h2": "As 29 funções"}''',
    r'''{"table": {"head": ["Grupo", "Funções"], "rows": [
    ["livro", "`new`, `read`, `save`, `sheets`, `sheet`, `drop_sheet`, `quick`"],
    ["células", "`get`, `set`, `cell`, `formula`, `get_formula`, `formulas`, `append`"],
    ["leitura", "`rows`, `records`, `column`, `dims`"],
    ["formatação", "`width`, `bold_row`, `freeze`, `autofit`"],
    ["conversão", "`from_csv`, `to_csv`, `to_frame`, `from_frame`"],
    ["endereços", "`addr`, `parse_addr`, `col_letter`"]
  ]}}''',
    r'''{"h2": "O que ele não faz"}''',
    r'''{"p": "Não calcula fórmulas, não desenha gráficos, não lê `.xls` antigo (o formato binário anterior a 2007) e não faz tabela dinâmica. Cores e bordas se limitam ao negrito do cabeçalho. Para o que ele faz — levar dados para dentro e para fora de uma planilha — está completo."}''',
]
