import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Excel",
  description: "Ler e gravar planilhas .xlsx sem dependência externa.",
};

const blocos: Bloco[] = [
  {"p": "Um `.xlsx` é um ZIP de arquivos XML. O `Arcane.Excel` escreve e lê esse formato usando só a biblioteca padrão do Python — o arquivo abre no Excel, no LibreOffice e no Google Sheets, e é lido de volta por openpyxl e pandas."},
  {"h2": "O caminho curto"},
  { code: `adopt Arcane.Excel as Xls

vendas := [
    {"produto": "Martelo", "qtd": 12, "preco": 89.9},
    {"produto": "Bigorna", "qtd": 3,  "preco": 450.0}
]

Xls.quick("vendas.xlsx", vendas, "Vendas")` },
  {"p": "Quando os dados são vaults, o cabeçalho sai das chaves — em negrito, com a primeira linha congelada e a largura ajustada ao conteúdo. Sem isso, a planilha abre com colunas de `####`."},
  {"h2": "Ler"},
  { code: `livro := Xls.read("vendas.xlsx")

Xls.sheets(livro)                    // ["Vendas"]
Xls.dims(livro, "Vendas")            // {linhas: 3, colunas: 3, celulas: 9}
Xls.rows(livro, "Vendas")            // lista de listas
Xls.records(livro, "Vendas")         // lista de vaults, pelo cabeçalho
Xls.column(livro, "Vendas", "qtd")   // [12, 3]
Xls.get(Xls.sheet(livro, "Vendas"), "B2")   // 12` },
  {"p": "`column` aceita o **título** ou a letra. O título vence: numa planilha com uma coluna chamada `B`, pedir `\"B\"` traz essa coluna, não a segunda."},
  {"h2": "Os tipos sobrevivem"},
  {"table": {"head": ["Grava", "Volta como"], "rows": [
    ["`42`", "`Integer`"],
    ["`89.9`", "`Float`"],
    ["`yes` / `no`", "`Boolean`"],
    ["uma data", "data (o formato do Excel é um número; o módulo reconhece)"],
    ["texto", "`String`"],
    ["`void`", "célula vazia — e ela não ocupa espaço"]
  ]}},
  {"p": "Um número que chega como texto abre a planilha com tudo alinhado à esquerda e nada soma. Por isso `from_csv` converte o que parece número."},
  {"h2": "Montar com cuidado"},
  { code: `livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", vendas)

Xls.set(aba, "D1", "total")
cycle i from 2 to 3:
    Xls.formula(aba, $"D{i}", $"B{i}*C{i}")

Xls.set(aba, "A4", "SOMA")
Xls.formula(aba, "D4", "SUM(D2:D3)")
Xls.bold_row(aba, 3)
Xls.freeze(aba, "A2")
Xls.width(aba, "A", 28)

Xls.save(livro, "relatorio.xlsx")` },
  {"h2": "Fórmulas"},
  {"p": "Uma fórmula **não é calculada aqui**: é gravada, e o Excel a resolve ao abrir. É o que se quer num relatório — quem receber pode mexer nos números e ver o total mudar sozinho. Um valor calculado em DataForge seria um número morto."},
  { code: `Xls.get_formula(aba, "D4")     // "SUM(D2:D3)"
Xls.formulas(aba)              // {"D2": "B2*C2", "D4": "SUM(D2:D3)"}` },
  {"p": "Por isso a coluna de fórmulas volta vazia em `rows`: não há valor gravado, e isso não é um bug."},
  {"h2": "Converter"},
  { code: `Xls.from_csv("dados.csv")           // CSV  → livro
Xls.to_csv(livro, "saida.csv")      // livro → CSV
Xls.to_frame(livro, "Vendas")       // livro → frame do Analytics
Xls.from_frame(tabela, "Dados")     // frame → livro` },
  {"p": "`to_frame` é a ponte para o `Arcane.Analytics`: a planilha vira uma tabela que `describe`, `correlation` e `group_by` entendem."},
  {"h2": "Planilha esparsa"},
  { code: `aba := Xls.sheet(livro, "T")
Xls.set(aba, "A1", "canto")
Xls.set(aba, "Z100", "outro canto")
// duas células ocupadas, não 2.600` },
  {"p": "As células ficam num mapa esparso. Escrever em `Z100` não materializa 100 linhas vazias — nem no programa, nem no arquivo."},
  {"h2": "Endereços"},
  { code: `Xls.addr(0, 0)          // "A1"
Xls.addr(6, 1)          // "B7"
Xls.parse_addr("B7")    // {linha: 6, coluna: 1}
Xls.col_letter(26)      // "AA"` },
  {"p": "Nos endereços em texto (`\"B7\"`) a contagem começa em 1, como no Excel. Em `Xls.cell(aba, linha, coluna)` começa em 0, como no resto da linguagem."},
  {"h2": "As 29 funções"},
  {"table": {"head": ["Grupo", "Funções"], "rows": [
    ["livro", "`new`, `read`, `save`, `sheets`, `sheet`, `drop_sheet`, `quick`"],
    ["células", "`get`, `set`, `cell`, `formula`, `get_formula`, `formulas`, `append`"],
    ["leitura", "`rows`, `records`, `column`, `dims`"],
    ["formatação", "`width`, `bold_row`, `freeze`, `autofit`"],
    ["conversão", "`from_csv`, `to_csv`, `to_frame`, `from_frame`"],
    ["endereços", "`addr`, `parse_addr`, `col_letter`"]
  ]}},
  {"h2": "O que ele não faz"},
  {"p": "Não calcula fórmulas, não desenha gráficos, não lê `.xls` antigo (o formato binário anterior a 2007) e não faz tabela dinâmica. Cores e bordas se limitam ao negrito do cabeçalho. Para o que ele faz — levar dados para dentro e para fora de uma planilha — está completo."},
];

const headings = [{ id: 'o-caminho-curto', text: "O caminho curto", level: 2 as const }, { id: 'ler', text: "Ler", level: 2 as const }, { id: 'os-tipos-sobrevivem', text: "Os tipos sobrevivem", level: 2 as const }, { id: 'montar-com-cuidado', text: "Montar com cuidado", level: 2 as const }, { id: 'formulas', text: "Fórmulas", level: 2 as const }, { id: 'converter', text: "Converter", level: 2 as const }, { id: 'planilha-esparsa', text: "Planilha esparsa", level: 2 as const }, { id: 'enderecos', text: "Endereços", level: 2 as const }, { id: 'as-29-funcoes', text: "As 29 funções", level: 2 as const }, { id: 'o-que-ele-nao-faz', text: "O que ele não faz", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Arcane.Excel"}
      description={"Ler e gravar planilhas .xlsx sem dependência externa."}
      href={"/docs/biblioteca/excel"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
