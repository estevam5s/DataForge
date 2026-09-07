import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ferramenta de linha de comando",
  description: "Analisar uma pasta e imprimir um relatório — o tipo de utilitário que se usa todo dia.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `175_cli_arquivos.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.IO as IO
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
out "  (pasta temporaria removida)"`, title: `175_cli_arquivos.df` },
  {"h2": "O que ela faz"},
  {"list": ["Lê cada arquivo da pasta", "Extrai nome, extensão, tamanho e contagem de linhas", "Agrupa por extensão com um histograma", "Encontra o maior e o menor", "Busca um termo em todos os arquivos"]},
  {"h2": "Decisões que valem notar"},
  {"h3": "Modelo primeiro"},
  {"p": "Converter os dados brutos num `record` logo na entrada faz o resto do programa trabalhar com `a.bytes` em vez de chamar `IO.size` repetidamente."},
  {"h3": "Formatação legível"},
  {"p": "\"1.4 KB\" comunica; \"1433\" não. Numa ferramenta de terminal, esse detalhe é a diferença entre útil e irritante."},
  {"h3": "Colunas alinhadas"},
  {"p": "`pad_end` para texto (alinha à esquerda), `pad_start` para número (à direita). É como toda tabela de terminal se lê melhor."},
  {"h3": "Proteção nas bordas"},
  {"p": "`max(1, soma * 20 ~/ max(total, 1))` — dois `max` evitam barra de comprimento zero e divisão por zero numa pasta vazia. Vale escrever mesmo quando \"não vai acontecer\"."},
];

const headings = [{ id: 'o-que-ela-faz', text: "O que ela faz", level: 2 as const }, { id: 'decisoes-que-valem-notar', text: "Decisões que valem notar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ferramenta de linha de comando"}
      description={"Analisar uma pasta e imprimir um relatório — o tipo de utilitário que se usa todo dia."}
      href={"/docs/receitas/cli"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
