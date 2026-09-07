import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Contribuir",
  description: "Como propor mudanças, e o que cada recurso novo exige.",
};

const blocos: Bloco[] = [
  {"h2": "Começar"},
  { code: `git clone https://github.com/estevam5s/DataForge.git
cd DataForge

python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python3 -m pytest tests/ -q          # 272 testes
python3 exercicios/run_all.py        # 190 exercícios`, lang: 'bash' },
  {"p": "O estado esperado é **tudo verde**. Se algo falhar antes da sua mudança, isso é em si um achado que vale reportar."},
  {"h2": "Por onde começar"},
  {"p": "Os itens mais acessíveis do [roadmap](/docs/roadmap):"},
  {"list": ["**Verificação de exaustividade** em `match` sobre enum — o analisador já conhece os membros", "**Contrato de trait** no analisador estático", "**Funções novas** nos módulos `Arcane.*`", "**Mais exercícios**, especialmente nos módulos 11–20", "**Correções na documentação** — se algo aqui está errado ou confuso"]},
  {"h2": "Adicionar um recurso à linguagem"},
  {"p": "Um recurso novo toca seis arquivos, nesta ordem:"},
  {"table": {"head": ["#", "Arquivo", "O que fazer"], "rows": [["1", "`dataforge/tokens.py`", "o `TokenType` e, se for palavra, a entrada em `KEYWORDS`"], ["2", "`dataforge/lexer.py`", "reconhecer o símbolo"], ["3", "`dataforge/ast_nodes.py`", "o nó, como `@dataclass` com defaults"], ["4", "`dataforge/parser.py`", "o método `parse_*`"], ["5", "`dataforge/interpreter.py`", "`exec_<Nó>` ou `eval_<Nó>`"], ["6", "`dataforge/typechecker.py`", "`st_<Nó>` ou `ex_<Nó>` — senão o analisador ignora"]]}},
  {"h2": "O que cada recurso exige"},
  {"list": ["Sintaxe documentada em `doc/REFERENCIA.md`, incluindo a gramática EBNF", "Teste de regressão em `tests/test_dataforge4.py`", "Um exercício didático em `exercicios/`, se o recurso for ensinável", "A suíte existente continuando verde"]},
  {"callout": {"tipo": "dica", "titulo": "Ao corrigir um bug", "texto": "Escreva **primeiro** o teste que falha, depois corrija. Todos os bugs corrigidos no 3.1 e no 4.0 têm teste correspondente — é o que impede a regressão voltar."}},
  {"h2": "Cuidado com KEYWORDS"},
  {"p": "Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de adicionar uma, confirme que o parser realmente a consome:"},
  { code: `grep -c "TokenType.NOVA\\b" dataforge/parser.py    # precisa ser > 0`, lang: 'bash' },
  {"p": "Se for 0, ela só quebra código de usuário sem entregar nada. Sete palavras já foram removidas por esse motivo."},
  {"p": "Depois, sincronize `doc/REFERENCIA.md` §1.6 — **há um teste que compara as duas listas**."},
  {"h2": "Mensagens de erro"},
  {"p": "Uma mensagem deve dizer **o que fazer**, não só o que houve:"},
  { code: `# ruim
"Invalid assignment target"

# bom
"'no' is a reserved keyword and cannot be assigned to. Pick another name."` },
  {"p": "Quando houver um nome parecido, sugira: o analisador usa `difflib` para isso."},
  {"h2": "Estilo"},
  {"list": ["Sem dependências externas em `dataforge/` — a stdlib usa apenas a do Python", "Documentação, exercícios e mensagens ao usuário final em **português**", "Comentários do runtime seguem o arquivo: inglês nos antigos, português nos módulos 4.0"]},
  {"h2": "Antes de abrir o PR"},
  { code: `python3 -m pytest tests/ -q
python3 exercicios/run_all.py
dataforge fmt . --check
dataforge check .`, lang: 'bash' },
];

const headings = [{ id: 'comecar', text: "Começar", level: 2 as const }, { id: 'por-onde-comecar', text: "Por onde começar", level: 2 as const }, { id: 'adicionar-um-recurso-a-linguagem', text: "Adicionar um recurso à linguagem", level: 2 as const }, { id: 'o-que-cada-recurso-exige', text: "O que cada recurso exige", level: 2 as const }, { id: 'cuidado-com-keywords', text: "Cuidado com KEYWORDS", level: 2 as const }, { id: 'mensagens-de-erro', text: "Mensagens de erro", level: 2 as const }, { id: 'estilo', text: "Estilo", level: 2 as const }, { id: 'antes-de-abrir-o-pr', text: "Antes de abrir o PR", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Contribuir"}
      description={"Como propor mudanças, e o que cada recurso novo exige."}
      href={"/docs/contribuir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
