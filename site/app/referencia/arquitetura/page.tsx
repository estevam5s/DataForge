import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arquitetura do runtime",
  description: "Como o interpretador funciona por dentro.",
};

const blocos: Bloco[] = [
  {"h2": "O fluxo"},
  { code: `arquivo.df → tokenize() → parse() → check_program() → Interpreter().run(ast)
             lexer.py     parser.py  typechecker.py   interpreter.py`, lang: 'text' },
  {"h2": "Os componentes"},
  {"table": {"head": ["Arquivo", "Responsabilidade", "Linhas"], "rows": [["`tokens.py`", "TokenType e as 81 palavras reservadas", "305"], ["`lexer.py`", "texto → tokens, INDENT/DEDENT, interpolação", "556"], ["`parser.py`", "recursivo descendente: tokens → AST", "1941"], ["`ast_nodes.py`", "nós da AST como dataclasses", "706"], ["`interpreter.py`", "interpretador de árvore — a semântica", "2703"], ["`typechecker.py`", "análise estática", "1193"], ["`formatter.py`", "`dataforge fmt`", "280"], ["`linter.py`", "`dataforge lint`", "394"], ["`testrunner.py`", "`dataforge test`", "194"], ["`docgen.py`", "`dataforge doc`", "218"], ["`project.py`", "`forge.toml`", "184"], ["`environment.py`", "cadeia de escopos", "91"], ["`errors.py`", "erros, sinais de controle, stack traces", "167"], ["`builtins.py`", "225 funções globais", "1224"], ["`repl.py`", "console interativo", "409"], ["`cli.py`", "a linha de comando", "1055"], ["`stdlib/`", "os 20 módulos `Arcane.*`", "7282"]]}},
  {"h2": "Despacho por nome de classe"},
  {"p": "O interpretador não usa `match` nem tabela: ele monta o nome do método a partir do tipo do nó."},
  { code: `# um nó GivenBlock procura exec_GivenBlock
# uma expressão BinaryOp procura eval_BinaryOp`, lang: 'text' },
  {"p": "Isso significa que adicionar um recurso à linguagem toca cinco lugares: `tokens.py` (se houver palavra nova), `lexer.py`, `ast_nodes.py` + `parser.py`, `interpreter.py` e `typechecker.py`."},
  {"h2": "O executor preguiçoso"},
  {"p": "Generators precisam entregar cada valor no instante em que `emit` o produz — inclusive dentro de um laço infinito. Um interpretador de árvore comum não consegue pausar no meio."},
  {"p": "A solução é um **executor paralelo** (`_lazy_block`) que percorre o corpo de um `stream action` como gerador Python: ele desce nas estruturas onde `emit` pode aparecer e delega o resto ao `execute()` normal."},
  { code: `stream action fib():
    a := 0
    b := 1
    persist yes:           # não trava: cada emit pausa
        emit a
        a, b := b, a + b` },
  {"h2": "Escopos"},
  {"p": "Cada bloco cria um `Environment` filho. Buscar um nome sobe a cadeia até o global. `steady` marca o nome no conjunto de constantes daquele escopo; `shadow` força a criação local."},
  {"h2": "Sem dependências"},
  {"p": "O runtime usa apenas a biblioteca padrão do Python. Isso é uma restrição de projeto, não uma limitação temporária: garante que um programa DataForge roda em qualquer máquina com Python 3.10+."},
  {"h2": "O que ainda não existe"},
  {"p": "É um **interpretador de árvore**, sem bytecode e sem otimização. Uma IR e uma VM de pilha estão no [roadmap](/roadmap), mas nenhum usuário reclamou de desempenho ainda — e medir antes de otimizar é a regra."},
];

const headings = [{ id: 'o-fluxo', text: "O fluxo", level: 2 as const }, { id: 'os-componentes', text: "Os componentes", level: 2 as const }, { id: 'despacho-por-nome-de-classe', text: "Despacho por nome de classe", level: 2 as const }, { id: 'o-executor-preguicoso', text: "O executor preguiçoso", level: 2 as const }, { id: 'escopos', text: "Escopos", level: 2 as const }, { id: 'sem-dependencias', text: "Sem dependências", level: 2 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arquitetura do runtime"}
      description={"Como o interpretador funciona por dentro."}
      href={"/referencia/arquitetura"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
