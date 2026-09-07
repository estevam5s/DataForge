import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Instalação",
  description: "Guia completo: requisitos, ambiente virtual, Windows, editor e solução de problemas.",
};

const blocos: Bloco[] = [
  {"h2": "Requisitos"},
  {"table": {"head": ["Item", "Versão mínima", "Como conferir"], "rows": [["Python", "3.10", "`python3 --version`"], ["pip", "qualquer recente", "`python3 -m pip --version`"], ["git", "opcional", "`git --version`"]]}},
  {"p": "DataForge é um interpretador escrito em Python puro. **Não há dependências externas obrigatórias** — nada de compilar, nada de toolchain."},
  {"h3": "Se você ainda não tem Python"},
  { code: `# macOS
brew install python@3.12

# Ubuntu / Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-venv`, lang: 'bash' },
  {"p": "No **Windows**, baixe em [python.org/downloads](https://www.python.org/downloads/) e marque **\"Add Python to PATH\"** durante a instalação."},
  {"h2": "Obter o DataForge"},
  { code: `git clone https://github.com/estevam5s/DataForge.git
cd DataForge`, lang: 'bash' },
  {"p": "Sem git, baixe o ZIP pelo botão **Code → Download ZIP** no GitHub e extraia."},
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
python3 -m pytest tests/ -q          # 240 testes
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
