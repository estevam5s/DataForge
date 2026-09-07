import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Planilhas",
  description: "Do banco à planilha, passando pela análise.",
};

const blocos: Bloco[] = [
  {"p": "Este é o caminho completo de um trabalho de dados: os dados moram no banco, a análise responde à pergunta, e a planilha é o que se manda para quem decide. As três peças conversam."},
  {"h2": "As quatro peças"},
  {"table": {"head": ["Módulo", "Para"], "rows": [
    ["[`Arcane.Database`](/docs/biblioteca/database)", "SQLite: consultas, migrações, transações, modelos"],
    ["[`Arcane.Analytics`](/docs/biblioteca/analytics)", "média, desvio, correlação, regressão, `describe`"],
    ["[`Arcane.Excel`](/docs/biblioteca/excel)", "ler e gravar `.xlsx`"],
    ["[`Arcane.IO`](/docs/biblioteca/io)", "arquivos, CSV, JSON"]
  ]}},
  {"h2": "Do banco à planilha"},
  { code: `adopt Arcane.Database as DB
adopt Arcane.Analytics as An
adopt Arcane.Excel as Xls

// 1. os dados
banco := DB.connect("vendas.db")
registros := DB.query(banco, "SELECT * FROM vendas ORDER BY qtd DESC")

// 2. a pergunta
tabela := An.from_records(registros)
descricao := An.describe(tabela)
correlacao := An.correlation(
    [r["qtd"] cycle r in registros],
    [r["preco"] cycle r in registros])

// 3. o entregável
livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", registros)
Xls.set(aba, "E1", "receita")
cycle i from 2 to len(registros) + 1:
    Xls.formula(aba, $"E{i}", $"C{i}*D{i}")

Xls.sheet(livro, "Estatísticas", [
    ["métrica", "valor"],
    ["vendas", len(registros)],
    ["correlação", round(correlacao, 3)]
])
Xls.save(livro, "relatorio.xlsx")` },
  {"h2": "`describe` sobre um frame"},
  {"p": "Sobre uma lista, descreve a lista. Sobre um frame, descreve **cada coluna**:"},
  { code: `An.describe(tabela)
// {
//   "qtd":     {count: 5, mean: 13.0, std: 9.6, min: 3, max: 27, …},
//   "produto": {count: 0, type: "non-numeric"}
// }` },
  {"p": "Colunas de texto aparecem marcadas em vez de zerarem o resultado inteiro. Booleanos são ignorados: em Python `yes` vale 1, e numa coluna de dados isso é ruído."},
  {"h2": "Escrever arquivos"},
  {"table": {"head": ["Quer", "Use"], "rows": [
    ["texto, JSON, CSV", "`IO.write_file`, `IO.write_json`, `IO.write_csv`"],
    ["planilha", "`Xls.save`, `Xls.quick`"],
    ["banco", "`DB.execute` — e `DB.close` quando terminar"],
    ["um caminho ao lado do programa", "`OS.beside(\"dados\", \"x.json\")`"]
  ]}},
  {"p": "`OS.beside` resolve a partir do arquivo `.df` em execução, não de onde o usuário chamou o programa. Sem isso, rodar de duas pastas diferentes lê — ou não lê — arquivos diferentes."},
  {"h2": "Servir a planilha por HTTP"},
  { code: `route GET "/relatorio.xlsx":
    livro := montar(consultar_agora())
    Xls.save(livro, "/tmp/r.xlsx")
    respond file "/tmp/r.xlsx"` },
  {"p": "O arquivo não precisa existir antes do pedido. O projeto [loja-web](/docs/projetos) faz exatamente isso, com fórmulas que o Excel resolve ao abrir."},
  {"h2": "Uma armadilha de precedência"},
  { code: `// errado: divide o ZERO, não a soma
media := precos >> distill a, v: a + v 0 / len(precos)

// certo
soma := precos >> distill a, v: a + v 0
media := soma / len(precos)` },
  {"p": "O valor inicial do `distill` vem depois do corpo. O relatório mostra a soma no lugar da média, e nada na tela denuncia — o número simplesmente está errado."},
];

const headings = [{ id: 'as-quatro-pecas', text: "As quatro peças", level: 2 as const }, { id: 'do-banco-a-planilha', text: "Do banco à planilha", level: 2 as const }, { id: 'describe-sobre-um-frame', text: "`describe` sobre um frame", level: 2 as const }, { id: 'escrever-arquivos', text: "Escrever arquivos", level: 2 as const }, { id: 'servir-a-planilha-por-http', text: "Servir a planilha por HTTP", level: 2 as const }, { id: 'uma-armadilha-de-precedencia', text: "Uma armadilha de precedência", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Planilhas"}
      description={"Do banco à planilha, passando pela análise."}
      href={"/docs/tecnicas/planilhas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
