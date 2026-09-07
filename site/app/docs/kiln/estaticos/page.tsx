import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arquivos estáticos",
  description: "CSS, imagens, downloads e a travessia de diretório que o Kiln recusa.",
};

const blocos: Bloco[] = [
  {"h2": "Servir uma pasta"},
  { code: `server site on 8080:
    assets "/static" from "./www"

    route GET "/":
        respond html "<link rel=stylesheet href=/static/estilo.css>…"` },
  {"p": "`/static/estilo.css` passa a servir `./www/estilo.css`. Uma pasta responde com o `index.html` de dentro dela, e o `Content-Type` sai do nome do arquivo."},
  {"h2": "`../` não escapa"},
  { code: `GET /static/estilo.css              → 200
GET /static/../../../etc/passwd     → 403
GET /static/%2e%2e/%2e%2e/etc/passwd → 403` },
  {"p": "O caminho é resolvido e comparado com a pasta declarada **antes** de qualquer arquivo ser aberto. Essa é a falha clássica de servidor de arquivos, e vale saber que ela está fechada."},
  {"p": "Ainda assim: sirva só o que é público. O `.git` e o `.env` moram no mesmo disco, e uma pasta declarada larga demais entrega os dois de forma perfeitamente legítima."},
  {"h2": "Caminho relativo a quê?"},
  { code: `adopt Arcane.OS as OS

// relativo a de onde o usuário chamou — frágil
assets "/static" from "./www"

// relativo ao programa — sempre certo
assets "/static" from OS.beside("../www")` },
  {"p": "`OS.beside` resolve a partir do arquivo `.df` em execução. Sem isso, rodar `dataforge run src/main.df` de duas pastas diferentes carrega — ou não carrega — arquivos diferentes, e o erro só aparece na máquina de outra pessoa."},
  {"h2": "Um arquivo específico"},
  { code: `route GET "/manual.pdf":
    respond file "./docs/manual.pdf"

// forçando o download, com outro nome
route GET "/dados":
    respond Kiln.file("/tmp/export.csv", void, "dados-2026.csv")` },
  {"h2": "Gerado na hora"},
  { code: `route GET "/relatorio.xlsx":
    livro := Xls.new()
    Xls.sheet(livro, "Estoque", produtos_agora())
    Xls.save(livro, "/tmp/r.xlsx")
    respond file "/tmp/r.xlsx"` },
  {"p": "O arquivo não precisa existir antes do pedido. É assim que a [loja-web](/docs/projetos) entrega uma planilha com os dados do momento, fórmulas inclusive."},
  {"h2": "Cache"},
  {"p": "Arquivos estáticos saem com `Cache-Control: public, max-age=3600`. Uma hora é curta o bastante para não atrapalhar durante o desenvolvimento e longa o bastante para valer a pena. Se você versiona os nomes (`estilo.a1b2.css`), sirva com um `Kiln.header` mais generoso."},
  {"h2": "Limite de corpo"},
  { code: `Kiln.config(app, "limite_corpo", 5 * 1024 * 1024)   // 5 MB` },
  {"p": "O padrão é 10 MB, e um corpo maior é recusado com **413 antes de ser lido inteiro na memória**. Sem esse limite, um POST de 2 GB derruba o processo — e ninguém precisa de permissão para tentar."},
];

const headings = [{ id: 'servir-uma-pasta', text: "Servir uma pasta", level: 2 as const }, { id: 'nao-escapa', text: "`../` não escapa", level: 2 as const }, { id: 'caminho-relativo-a-que', text: "Caminho relativo a quê?", level: 2 as const }, { id: 'um-arquivo-especifico', text: "Um arquivo específico", level: 2 as const }, { id: 'gerado-na-hora', text: "Gerado na hora", level: 2 as const }, { id: 'cache', text: "Cache", level: 2 as const }, { id: 'limite-de-corpo', text: "Limite de corpo", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Arquivos estáticos"}
      description={"CSS, imagens, downloads e a travessia de diretório que o Kiln recusa."}
      href={"/docs/kiln/estaticos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
