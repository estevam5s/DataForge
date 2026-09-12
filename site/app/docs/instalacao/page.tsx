import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Instalação",
  description: "Guia completo: requisitos, ambiente virtual, Windows, editor e solução de problemas.",
};

const blocos: Bloco[] = [
  {"p": "A forma mais rápida é o instalador: um comando, e o `dataforge` fica pronto. Ele não mexe no Python do sistema — cria um ambiente próprio em `~/.dataforge`."},

  {"h2": "Instalação em um comando"},
  {"h3": "macOS e Linux"},
  { code: `curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh`, lang: 'bash' },
  {"p": "Com `wget`, se preferir:"},
  { code: `wget -qO- https://dataforge-lang.vercel.app/instalar.sh | sh`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "Ler antes de executar", "texto": "Canalizar um script da internet direto para o `sh` pede confiança na origem. Para conferir o que ele faz antes: `curl -fsSL https://dataforge-lang.vercel.app/instalar.sh -o instalar.sh`, leia, e então `sh instalar.sh`."}},

  {"h3": "Windows (PowerShell)"},
  { code: `irm https://dataforge-lang.vercel.app/instalar.ps1 | iex`, lang: 'powershell' },
  {"p": "O instalador acrescenta o DataForge ao PATH do usuário. Abra um terminal novo depois."},

  {"h2": "Sem Python na máquina"},
  {"p": "O instalador acima cria um ambiente com o Python que encontrar. Se não houver Python 3.10 ou mais novo, ele passa sozinho para o **executável** — um arquivo único que já traz o interpretador dentro. Para pedir esse caminho de propósito:"},
  { code: `curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | DATAFORGE_BINARIO=1 sh`, lang: 'bash' },
  {"p": "Ou pegue o arquivo à mão em [releases](https://github.com/estevam5s/DataForge/releases): há um para Linux x64, macOS Intel, macOS Apple Silicon e Windows x64, com `SHA256SUMS.txt` ao lado para conferir."},
  {"table": {"head": ["", "executável", "Python + pip"], "rows": [
    ["precisa de Python", "**não**", "3.10+"],
    ["download", "~12 MB comprimido, ~28 MB em disco", "~2 MB"],
    ["`dataforge run` de um \"olá\"", "80 ms", "67 ms"],
    ["extensão do VS Code com LSP", "**vem junto**", "precisa de `npm install`"],
    ["`pip install` de pacote Python", "não", "sim"],
    ["mexer no interpretador", "não", "sim"]]}},
  {"callout": {"tipo": "nota", "titulo": "Por que é uma pasta e não um arquivo só", "texto": "Um arquivo único é mais bonito de baixar e inutilizável de usar: ele descompacta o pacote inteiro num diretório temporário **a cada chamada**, e o mesmo `dataforge run` passa de 80 ms para 3,5 segundos. Os dois números são medidos."}},
  {"callout": {"tipo": "dica", "texto": "Use o **executável** para escrever programas em DataForge; use o **Python** para contribuir com a linguagem. Os dois rodam exatamente o mesmo interpretador — os 231 exercícios e os 44 exemplos passam pelos dois."}},

  {"h3": "Ajustar a instalação"},
  {"table": {"head": ["Variável", "Padrão", "Para que serve"], "rows": [["`DATAFORGE_PREFIX`", "`~/.dataforge`", "onde instalar"], ["`DATAFORGE_VERSION`", "`1.0.0`", "qual versão"], ["`DATAFORGE_SITE`", "o site oficial", "de onde baixar"], ["`DATAFORGE_BINARIO`", "`0`", "`1` força o executável, sem Python"]]}},
  { code: `# instalar em outro lugar
DATAFORGE_PREFIX=/opt/dataforge curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh

# desinstalar é apagar a pasta
rm -rf ~/.dataforge`, lang: 'bash' },

  {"h2": "O editor, junto"},
  {"p": "O instalador também instala a **coloração de sintaxe** no VS Code, Insiders, Cursor, VSCodium e Windsurf — todos os que encontrar. Reinicie o editor e todo `.df` abre com as palavras reservadas coloridas, 23 snippets e a indentação de 4 espaços que a linguagem exige."},
  { code: `dataforge editor           # refaz a instalação
dataforge editor status    # mostra onde está
DATAFORGE_SEM_EDITOR=1 …   # pula a etapa`, lang: 'bash' },
  {"p": "Detalhes em [Editor e cores](/docs/editor)."},
  {"h2": "Docker"},
  {"p": "Sem instalar nada no seu sistema — nem Python:"},
  { code: `# console interativo
docker run --rm -it estevan5s/dataforge repl

# rodar um arquivo da pasta atual
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df

# a suíte de testes de um projeto
docker run --rm -v "$PWD:/app" estevan5s/dataforge test tests/`, lang: 'bash' },
  {"p": "Um apelido no shell deixa o uso igual ao nativo:"},
  { code: `alias dataforge='docker run --rm -it -v "$PWD:/app" estevan5s/dataforge'
dataforge run main.df`, lang: 'bash' },
  {"h3": "Construir a imagem você mesmo"},
  { code: `docker build -t estevan5s/dataforge:1.0.0 .
docker compose run --rm repl`, lang: 'bash' },
  {"p": "A imagem é multi-estágio e roda como usuário sem privilégio. Cerca de 217 MB, a maior parte sendo o Python."},

  {"h2": "Baixar o tarball direto"},
  {"p": "Se você prefere controlar cada passo:"},
  { code: `curl -fsSL -O https://dataforge-lang.vercel.app/dist/dataforge-1.0.0.tar.gz
curl -fsSL -O https://dataforge-lang.vercel.app/dist/dataforge-1.0.0.tar.gz.sha256
shasum -a 256 -c dataforge-1.0.0.tar.gz.sha256

tar -xzf dataforge-1.0.0.tar.gz
cd dataforge-1.0.0
pip install .`, lang: 'bash' },

  {"h2": "A partir do código-fonte"},
  {"h3": "Requisitos"},
  {"table": {"head": ["Item", "Versão mínima", "Como conferir"], "rows": [["Python", "3.10", "`python3 --version`"], ["pip", "qualquer recente", "`python3 -m pip --version`"], ["git", "opcional", "`git --version`"]]}},
  {"p": "DataForge é um interpretador escrito em Python puro. **Não há dependências externas obrigatórias** — nada de compilar, nada de toolchain."},
  {"h3": "Se você ainda não tem Python"},
  { code: `# macOS
brew install python@3.12

# Ubuntu / Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-venv`, lang: 'bash' },
  {"p": "No **Windows**, baixe em [python.org/downloads](https://www.python.org/downloads/) e marque **\"Add Python to PATH\"** durante a instalação."},
  {"h3": "Clonar e instalar"},
  { code: `git clone https://github.com/estevam5s/DataForge.git
cd DataForge
pip install -e .`, lang: 'bash' },
  {"p": "O `-e` instala em modo editável: mudanças no código valem na hora, sem reinstalar. É como você trabalha se for [contribuir](/docs/contribuir)."},

  {"h2": "Ambiente virtual"},
  {"p": "O ambiente virtual isola o DataForge do Python do sistema. É opcional, mas evita conflitos."},
  { code: `# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\\Scripts\\Activate.ps1`, lang: 'bash' },
  {"p": "O prompt passa a exibir `(.venv)`. Para sair depois: `deactivate`."},
  {"h2": "Instalar"},
  { code: `pip install .              # instalação normal
pip install -e ".[dev]"    # editável, com pytest — para mexer no interpretador`, lang: 'bash' },
  {"p": "O modo editável faz suas alterações em `dataforge/*.py` valerem imediatamente, sem reinstalar."},
  {"callout": {"tipo": "dica", "titulo": "Rodar sem instalar", "texto": "Dentro da pasta do projeto, `python3 -m dataforge run arquivo.df` funciona sem nenhuma instalação."}},
  {"h2": "Editor"},
  {"p": "A gramática TextMate para realce de sintaxe está em `editor/vscode/`:"},
  { code: `mkdir -p ~/.vscode/extensions/dataforge
cp -r editor/vscode/* ~/.vscode/extensions/dataforge/`, lang: 'bash' },
  {"p": "Reinicie o VS Code. Arquivos `.df` passam a ter realce."},
  {"h2": "Verificar a instalação"},
  { code: `dataforge version
python3 -m pytest tests/ -q          # 272 testes
python3 exercicios/run_all.py        # 231 exercícios`, lang: 'bash' },
  {"h2": "Problemas comuns"},
  {"h3": "`command not found: dataforge`"},
  {"p": "O ambiente virtual não está ativo, ou o `pip install` não rodou. A alternativa que sempre funciona dentro da pasta do projeto é `python3 -m dataforge run arquivo.df`."},
  {"h3": "`No module named dataforge`"},
  {"p": "Você está fora da pasta do projeto e não instalou o pacote. Instale com `pip install .` ou volte para a raiz do repositório."},
  {"h3": "`SyncError: Tab character detected`"},
  {"p": "DataForge exige **espaços**, nunca tabs. No VS Code: paleta de comandos → \"Convert Indentation to Spaces\"."},
  {"h3": "`SyncError: Indentation mismatch`"},
  {"p": "Um bloco tem recuo inconsistente. Use sempre 4 espaços por nível."},
  {"h3": "Erro de build no `pip install`"},
  { code: `pip install --upgrade pip setuptools wheel`, lang: 'bash' },
  {"h2": "Desinstalar"},
  { code: `pip uninstall dataforge-lang`, lang: 'bash' },
  {"p": "Se usou ambiente virtual, apagar a pasta `.venv` também resolve."},
];

const headings = [{ id: 'instalacao-em-um-comando', text: "Instalação em um comando", level: 2 as const }, { id: 'macos-e-linux', text: "macOS e Linux", level: 3 as const }, { id: 'windows-powershell', text: "Windows (PowerShell)", level: 3 as const }, { id: 'sem-python-na-maquina', text: "Sem Python na máquina", level: 2 as const }, { id: 'ajustar-a-instalacao', text: "Ajustar a instalação", level: 3 as const }, { id: 'o-editor-junto', text: "O editor, junto", level: 2 as const }, { id: 'docker', text: "Docker", level: 2 as const }, { id: 'construir-a-imagem-voce-mesmo', text: "Construir a imagem você mesmo", level: 3 as const }, { id: 'baixar-o-tarball-direto', text: "Baixar o tarball direto", level: 2 as const }, { id: 'a-partir-do-codigo-fonte', text: "A partir do código-fonte", level: 2 as const }, { id: 'requisitos', text: "Requisitos", level: 3 as const }, { id: 'se-voce-ainda-nao-tem-python', text: "Se você ainda não tem Python", level: 3 as const }, { id: 'clonar-e-instalar', text: "Clonar e instalar", level: 3 as const }, { id: 'ambiente-virtual', text: "Ambiente virtual", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }, { id: 'editor', text: "Editor", level: 2 as const }, { id: 'verificar-a-instalacao', text: "Verificar a instalação", level: 2 as const }, { id: 'problemas-comuns', text: "Problemas comuns", level: 2 as const }, { id: 'command-not-found-dataforge', text: "`command not found: dataforge`", level: 3 as const }, { id: 'no-module-named-dataforge', text: "`No module named dataforge`", level: 3 as const }, { id: 'syncerror-tab-character-detected', text: "`SyncError: Tab character detected`", level: 3 as const }, { id: 'syncerror-indentation-mismatch', text: "`SyncError: Indentation mismatch`", level: 3 as const }, { id: 'erro-de-build-no-pip-install', text: "Erro de build no `pip install`", level: 3 as const }, { id: 'desinstalar', text: "Desinstalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Instalação"}
      description={"Guia completo: requisitos, ambiente virtual, Windows, editor e solução de problemas."}
      href={"/docs/instalacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
