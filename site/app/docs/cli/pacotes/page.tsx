import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge add",
  description: "add, remove, install, list, search, pack e publish — o gerenciador de pacotes.",
};

const blocos: Bloco[] = [
  {"p": "A referência completa do gerenciador está em [Pacotes](/docs/pacotes). Esta página é o resumo dos comandos."},
  {"h2": "add"},
  { code: `dataforge add validador              # a versão mais recente, gravada como ^
dataforge add validador@1.2.0        # exata
dataforge add validador@^2.0         # faixa
dataforge add tabela datas cofre     # vários
dataforge add ../lib-interna         # pasta local
dataforge add git+https://github.com/voce/lib.git`, lang: 'bash' },
  {"p": "Resolve, baixa, instala em `forge_modules/`, grava no `forge.toml` e atualiza o `forge.lock`."},
  {"h2": "remove"},
  { code: `dataforge remove tabela
dataforge rm tabela          # o mesmo`, lang: 'bash' },
  {"h2": "install"},
  { code: `dataforge install            # tudo o que o forge.toml declara
dataforge install --dry-run  # o plano, sem baixar
dataforge install --offline  # só com o cache local`, lang: 'bash' },
  {"p": "É o comando que se roda depois de clonar um projeto, e na esteira de CI."},
  {"h2": "list"},
  { code: `dataforge list`, lang: 'bash' },
  { code: `meu-app 0.1.0
  ✓ datas@1.0.0
  ✓ tabela@1.0.0  (transitiva)
  ✓ validador@1.0.0`, lang: 'bash' },
  {"p": "Um `✗` marca o que está no lock mas sumiu do disco — nesse caso, `dataforge install` reconstrói."},
  {"h2": "search"},
  { code: `dataforge search cpf
dataforge search ""          # lista tudo`, lang: 'bash' },
  {"p": "Procura no nome, na descrição e nas tags."},
  {"h2": "pack"},
  { code: `dataforge pack`, lang: 'bash' },
  {"p": "Gera `dist/<nome>-<versao>.tar.gz` com o sha256. Reprodutível: mesma fonte, mesmo hash."},
  {"h2": "publish"},
  { code: `dataforge publish --registry=/caminho/do/registro`, lang: 'bash' },
  {"p": "Veja [Publicar um pacote](/docs/pacotes/publicar)."},
  {"h2": "Variáveis de ambiente"},
  {"table": {"head": ["Variável", "Para que serve"], "rows": [["`DATAFORGE_REGISTRY`", "o índice a consultar"], ["`DATAFORGE_REGISTRY_DIR`", "a pasta padrão do `publish`"]]}},
];

const headings = [{ id: 'add', text: "add", level: 2 as const }, { id: 'remove', text: "remove", level: 2 as const }, { id: 'install', text: "install", level: 2 as const }, { id: 'list', text: "list", level: 2 as const }, { id: 'search', text: "search", level: 2 as const }, { id: 'pack', text: "pack", level: 2 as const }, { id: 'publish', text: "publish", level: 2 as const }, { id: 'variaveis-de-ambiente', text: "Variáveis de ambiente", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge add"}
      description={"add, remove, install, list, search, pack e publish — o gerenciador de pacotes."}
      href={"/docs/cli/pacotes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
