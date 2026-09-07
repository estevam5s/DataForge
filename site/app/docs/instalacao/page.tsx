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

  {"h3": "Ajustar a instalação"},
  {"table": {"head": ["Variável", "Padrão", "Para que serve"], "rows": [["`DATAFORGE_PREFIX`", "`~/.dataforge`", "onde instalar"], ["`DATAFORGE_VERSION`", "`4.0.0`", "qual versão"], ["`DATAFORGE_SITE`", "o site oficial", "de onde baixar"]]}},
  { code: `# instalar em outro lugar
DATAFORGE_PREFIX=/opt/dataforge curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh

# desinstalar é apagar a pasta
rm -rf ~/.dataforge`, lang: 'bash' },

  {"h2": "Docker"},
  {"p": "Sem instalar nada no seu sistema — nem Python:"},
  { code: `# console interativo
docker run --rm -it dataforge/dataforge repl

# rodar um arquivo da pasta atual
docker run --rm -v "$PWD:/app" dataforge/dataforge run main.df

# a suíte de testes de um projeto
docker run --rm -v "$PWD:/app" dataforge/dataforge test tests/`, lang: 'bash' },
  {"p": "Um apelido no shell deixa o uso igual ao nativo:"},
  { code: `alias dataforge='docker run --rm -it -v "$PWD:/app" dataforge/dataforge'
dataforge run main.df`, lang: 'bash' },
  {"h3": "Construir a imagem você mesmo"},
  { code: `docker build -t dataforge/dataforge:4.0.0 .
docker compose run --rm repl`, lang: 'bash' },
  {"p": "A imagem é multi-estágio e roda como usuário sem privilégio. Cerca de 217 MB, a maior parte sendo o Python."},

  {"h2": "Baixar o tarball direto"},
  {"p": "Se você prefere controlar cada passo:"},
  { code: `curl -fsSL -O https://dataforge-lang.vercel.app/dist/dataforge-4.0.0.tar.gz
curl -fsSL -O https://dataforge-lang.vercel.app/dist/dataforge-4.0.0.tar.gz.sha256
shasum -a 256 -c dataforge-4.0.0.tar.gz.sha256

tar -xzf dataforge-4.0.0.tar.gz
cd dataforge-4.0.0
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
python3 exercicios/run_all.py        # 180 exercícios`, lang: 'bash' },
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

const headings = [{ id: 'requisitos', text: "Requisitos", level: 2 as const }, { id: 'obter-o-dataforge', text: "Obter o DataForge", level: 2 as const }, { id: 'ambiente-virtual', text: "Ambiente virtual", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }, { id: 'editor', text: "Editor", level: 2 as const }, { id: 'verificar-a-instalacao', text: "Verificar a instalação", level: 2 as const }, { id: 'problemas-comuns', text: "Problemas comuns", level: 2 as const }, { id: 'desinstalar', text: "Desinstalar", level: 2 as const }];

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
