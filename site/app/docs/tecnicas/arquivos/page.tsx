import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arquivos",
  description: "Ler, escrever e organizar arquivos com Arcane.IO.",
};

const blocos: Bloco[] = [
  {"h2": "Texto"},
  { code: `adopt Arcane.IO as IO

IO.write(caminho, texto)      # cria ou substitui
IO.append(caminho, texto)     # acrescenta ao fim
IO.read(caminho)              # devolve o conteúdo

cycle linha in IO.read("dados.txt").lines():
    processar(linha)` },
  {"callout": {"tipo": "atencao", "texto": "`IO.read` carrega o arquivo inteiro na memória. Para arquivos grandes, prefira um [`stream action`](/docs/tecnicas/streams) que emite linha por linha."}},
  {"h2": "Formatos estruturados"},
  { code: `IO.write_json(caminho, vault)     IO.read_json(caminho)
IO.write_csv(caminho, linhas)     IO.read_csv(caminho)` },
  {"p": "Fazem a serialização e a escrita numa chamada só."},
  {"h2": "Caminhos"},
  { code: `IO.join(pasta, "arquivo.txt")     # monta com o separador certo
IO.basename(caminho)              # "notas.txt"
IO.dirname(caminho)               # a pasta
IO.ext(caminho)                   # ".txt"
IO.abs(caminho)                   # caminho absoluto` },
  {"callout": {"tipo": "dica", "texto": "**Sempre use `IO.join`** em vez de concatenar com `\"/\"`. O separador muda entre sistemas, e concatenar à mão é a forma mais rápida de escrever código que só funciona na sua máquina."}},
  {"h2": "Diretórios"},
  { code: `IO.mkdir(pasta)          # cria, inclusive os níveis intermediários
IO.list_dir(pasta)       # os nomes dentro dela
IO.exists(caminho)       # arquivo ou pasta
IO.file_exists(caminho)  # só arquivo
IO.size(caminho)         # bytes` },
  {"h2": "Copiar, mover, apagar"},
  { code: `IO.copy(origem, destino)
IO.rename(antigo, novo)     # também move entre pastas
IO.delete(caminho)` },
  {"h2": "Filtrar por extensão"},
  { code: `textos := IO.list_dir(pasta) >> sift nome: nome.endswith(".txt")` },
  {"p": "`list_dir` devolve uma lista comum, então todo o pipeline funciona sobre ela."},
  {"h2": "Limpeza garantida"},
  {"p": "Use `defer` para garantir a limpeza mesmo se algo falhar no meio:"},
  { code: `action processar():
    IO.write(temp, "dados")
    defer:
        given IO.exists(temp):
            IO.delete(temp)
    # ... o defer roda mesmo se isto disparar
    yield resultado` },
  {"p": "Detalhes em [Tratamento de erros](/docs/erros)."},
  {"h2": "Um relatório de pasta"},
  { code: `action formatar_bytes(n) -> String:
    given n smaller 1024:
        yield $"{n} B"
    orif n smaller 1048576:
        yield $"{round(n / 1024, 1)} KB"
    yield $"{round(n / 1048576, 2)} MB"

cycle nome in IO.list_dir("."):
    caminho := IO.join(".", nome)
    given IO.file_exists(caminho):
        out $"{nome.pad_end(24)}{formatar_bytes(IO.size(caminho)).pad_start(10)}"` },
];

const headings = [{ id: 'texto', text: "Texto", level: 2 as const }, { id: 'formatos-estruturados', text: "Formatos estruturados", level: 2 as const }, { id: 'caminhos', text: "Caminhos", level: 2 as const }, { id: 'diretorios', text: "Diretórios", level: 2 as const }, { id: 'copiar-mover-apagar', text: "Copiar, mover, apagar", level: 2 as const }, { id: 'filtrar-por-extensao', text: "Filtrar por extensão", level: 2 as const }, { id: 'limpeza-garantida', text: "Limpeza garantida", level: 2 as const }, { id: 'um-relatorio-de-pasta', text: "Um relatório de pasta", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arquivos"}
      description={"Ler, escrever e organizar arquivos com Arcane.IO."}
      href={"/docs/tecnicas/arquivos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
