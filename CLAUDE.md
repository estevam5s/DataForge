# CLAUDE.md — DataForge

Contexto operacional para o Claude Code trabalhar neste repositório. Leia antes
de editar qualquer coisa.

---

## O que é este projeto

**DataForge** é uma linguagem de programação interpretada, de propósito geral,
implementada em Python 3.10+ sem dependências externas. Não é um DSL nem um
transpilador: tem lexer, parser recursivo descendente, AST tipada e um
interpretador de árvore próprios.

- Versão atual: **3.1.0**
- Extensão dos arquivos: `.df`
- Entrypoints: `dataforge` e `df` (mesmo `main`)
- Licença: MIT

### Verificação rápida (rode antes e depois de mexer)

```bash
python3 -m pytest tests/ -q                          # 77 testes
python3 exercicios/run_all.py                        # 120 exercícios
for f in examples/*.df; do python3 -m dataforge run "$f" >/dev/null || echo "FALHOU $f"; done
```

O estado esperado é **tudo verde**. Se algo falhar antes da sua mudança, diga
isso ao usuário em vez de assumir que foi você.

---

## Mapa do código

```
dataforge/
  tokens.py        TokenType (enum) + KEYWORDS (78 palavras reservadas)
  lexer.py         Lexer: texto → tokens. Gera INDENT/DEDENT.
  parser.py        Parser recursivo descendente: tokens → AST
  ast_nodes.py     Dataclasses dos nós da AST
  interpreter.py   Interpretador de árvore. Aqui mora quase toda a semântica.
  environment.py   Cadeia de escopos (get/set/steady/shadow)
  errors.py        Hierarquia de erros + sinais de controle
  builtins.py      225 funções globais, sem import
  repl.py          Console interativo
  cli.py           CLI + 6 templates de projeto
  stdlib/          13 módulos Arcane.*

doc/               INSTALACAO, TUTORIAL, REFERENCIA, BIBLIOTECA_PADRAO (pt-BR)
examples/          42 programas de demonstração
exercicios/        120 exercícios em 10 módulos + run_all.py
tests/             test_dataforge.py (suíte legada) + test_regressoes.py (pytest)
editor/vscode/     gramática TextMate
```

### Fluxo de execução

```
arquivo.df → tokenize() → parse() → Interpreter().run(ast)
             lexer.py     parser.py   interpreter.py
```

O interpretador despacha por nome de classe: um nó `GivenBlock` procura
`exec_GivenBlock`; uma expressão `BinaryOp` procura `eval_BinaryOp`. **Para
adicionar um recurso, você precisa mexer em quatro lugares**: `tokens.py`
(se houver palavra/símbolo novo) → `lexer.py` → `ast_nodes.py` + `parser.py` →
`interpreter.py`.

---

## A linguagem em 60 segundos

```dataforge
// atribuição, constante, saída
x := 10
steady PI := 3.14159
out "valor:", x

// condicional
given x bigger 5:
    out "grande"
orif x is 5:
    out "cinco"
otherwise:
    out "pequeno"

// laços
cycle i from 1 to 5 step 2:
    out i
cycle item in [1, 2, 3]:
    out item
persist x bigger 0:
    x -= 1

// ação
action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

// classe
blueprint Ponto(x, y):
    action norma():
        yield sqrt(self.x ** 2 + self.y ** 2)
    action toString():
        yield "(" + str(self.x) + ", " + str(self.y) + ")"

p := spawn Ponto(3, 4)

// erros
monitor:
    trigger "falhou"
handle e:
    out e.type, e.message
ensure:
    out "sempre roda"

// pipeline
out [1,2,3,4,5,6]
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0

// módulo
adopt Arcane.Math as Math
out Math.sqrt(16)
```

### Tabela de tradução

| Conceito | DataForge |
|----------|-----------|
| `=` | `:=` |
| `const` | `steady` |
| `print` | `out` |
| `if/elif/else` | `given/orif/otherwise` |
| `switch/case/default` | `match/point/default` |
| `for` | `cycle ... from ... to` / `cycle ... in` |
| `while` | `persist` |
| `do..while` | `perform ... persist` |
| `break/continue` | `halt/skip` |
| `def`/`return` | `action`/`yield` |
| `class`/`new` | `blueprint`/`spawn` |
| `self`/`super` | `self`/`root` |
| `interface` | `trait` |
| `import`/`export` | `adopt`/`relay` |
| `try/catch/finally` | `monitor/handle/ensure` |
| `throw` | `trigger` |
| `true/false/null` | `yes/no/void` |
| `filter/map/reduce` | `>> sift` / `>> morph` / `>> distill` |
| lambda | `lambda x: expr` ou `lambda a, b => expr` |
| decorator | `mark @nome` |

---

## Armadilhas — leia antes de escrever `.df`

Estas são as que mais custam tempo:

1. **`yield` retorna, não gera.** Não existe gerador na linguagem. `yield`
   encerra a ação imediatamente.

2. **Divisão inteira: use `~/`.** O `//` também funciona, mas colide com
   comentário e depende de heurística no lexer. Em código novo, sempre `~/`.

3. **Só espaços na indentação.** Tab é `SyncError`. 4 espaços por nível.

4. **`monitor` sem `handle` não engole o erro.** Ele só garante o `ensure`.
   Isso é intencional.

5. **`halt`, `skip` e `yield` atravessam `monitor`.** São `ControlSignal`
   (derivam de `BaseException`), não erros. Nunca capture `BaseException` num
   `except` do interpretador.

6. **Palavras reservadas não podem ser nomes.** As que mais pegam em código
   escrito em português: `no`, `in`, `is`, `to`, `from`, `as`, `step`, `point`,
   `default`, `frame`, `stream`, `emit`, `forge`. Já `range`, `cluster` e
   `vault` **são funções embutidas**, não palavras reservadas — pode usá-las
   como nome (e chamá-las).

7. **`self` dentro de métodos, sempre.** Escrever `x` em vez de `self.x` lê a
   variável do escopo externo, não o campo.

8. **`out` recebe uma lista separada por vírgulas**, e imprime tudo separado por
   espaço: `out "a:", x, "b:", y`.

9. **`str()` respeita `toString()`** de blueprints e imprime `yes`/`no`/`void` —
   igual a `out`.

10. **`cycle from ... to` é inclusivo** nos dois extremos.

---

## Convenções ao mexer no interpretador

### Estilo

- Comentários e docstrings do runtime em **inglês** (é o padrão do arquivo).
- Documentação em `doc/`, exercícios e mensagens ao usuário final em
  **português**.
- Sem dependências externas em `dataforge/`. A stdlib usa apenas a stdlib do
  Python.
- Mensagens de erro devem dizer **o que fazer**, não só o que houve. Compare:
  `"Invalid assignment target"` (ruim) com
  `"'no' is a reserved keyword and cannot be assigned to. Pick another name."`
  (bom).

### Ao adicionar um recurso à linguagem

1. `tokens.py` — o `TokenType` e, se for palavra, a entrada em `KEYWORDS`.
2. `lexer.py` — reconhecer o símbolo (operadores de 2 caracteres vão no
   `two_char_map`).
3. `ast_nodes.py` — o nó, como `@dataclass` com defaults.
4. `parser.py` — o método `parse_*`, ligado em `parse_statement` ou
   `parse_primary`.
5. `interpreter.py` — `exec_<Nó>` para instrução, `eval_<Nó>` para expressão.
6. **Teste em `tests/test_regressoes.py`** e, se o recurso for didático, um
   exercício em `exercicios/`.
7. Atualize `doc/REFERENCIA.md` — inclusive a contagem de palavras reservadas.

### Ao mexer em `KEYWORDS`

Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de adicionar
uma, confirme que o parser realmente a consome:

```bash
grep -c "TokenType.NOVA\b" dataforge/parser.py    # precisa ser > 0
```

Se for 0, ela só quebra código de usuário sem entregar nada. Três palavras
(`cluster`, `vault`, `range`) já foram removidas por esse motivo — eram
funções embutidas que ninguém conseguia chamar.

Depois, sincronize a lista em `doc/REFERENCIA.md` §1.6.

### Ao mexer na stdlib

Os módulos são dicionários criados em `__new__`. Cuidado: dentro de um
`@staticmethod` referenciado por outro método da classe, use o nome da classe
(`ArcaneCortex._softmax`), **nunca `cls`** — `cls` não existe ali e o módulo
inteiro deixa de carregar.

Confirme que todos carregam:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from dataforge.stdlib import get_module, list_modules
for m in sorted(set(list_modules())): get_module(m)
print('todos os modulos carregam')"
```

Depois regenere a doc a partir do código:

```bash
python3 tools/gerar_doc_stdlib.py     # reescreve doc/BIBLIOTECA_PADRAO.md
```

---

## Testes

| Arquivo | Como roda | Cobre |
|---------|-----------|-------|
| `tests/test_regressoes.py` | `pytest` | 77 testes: sinais de controle, precedência, tipos, aridade, `//`, imports, blueprints |
| `tests/test_dataforge.py` | `pytest` **e** `python3 tests/...` | 69 verificações da suíte original |
| `exercicios/run_all.py` | script | 120 exercícios, cada um com `assert` próprio |
| `examples/*.df` | manual | 42 programas maiores |

**Ao corrigir um bug, escreva primeiro o teste em `test_regressoes.py`** que
falha, depois corrija.

`tests/test_dataforge.py` roda nas duas formas — o `sys.exit` só dispara sob
`__main__`. Não renomeie `verificar()` para `test()`: o pytest tentaria coletá-la
como teste e falharia por fixtures.

---

## Estado conhecido e limitações

O que **funciona e está testado**: tipos primitivos, coleções com fatiamento,
todas as estruturas de controle, ações (padrões, nomeados, tipados, aridade,
closures, lambdas, decoradores, `defer`), blueprints (herança, traits,
polimorfismo, estáticos, sobrecarga de operadores, introspecção), erros
(`monitor/handle/ensure`, `handle` tipado, `guard`, `validate`, `retry`,
`propagate`), pipelines, 13 módulos da stdlib, servidor HTTP real, SQLite,
`async/await`, threads e canais.

O que **ainda não existe** (não invente que existe):

- Sem verificação estática: `dataforge check` valida só a sintaxe.
- Sem geradores, sem `list comprehension`, sem desestruturação
  (`a, b := lista`), sem operador ternário.
- Sem `import` seletivo (`adopt X.{a, b}`), sem pacotes/namespaces aninhados.
- Sem gerenciador de pacotes.
- Sem sincronização de variáveis entre threads (use `channel`).
- `frame`, `train` e `predict` são marcadores sintáticos: devolvem um vault com
  `__type__`, sem implementação de ML por trás.
- `relay` documenta a intenção de exportar, mas todas as variáveis de topo do
  módulo ficam visíveis de qualquer forma.
- Traits não verificam se o blueprint implementou o contrato.
- `parallel` roda **cada instrução** do bloco em uma thread — não é um bloco por
  thread.

---

## Ao responder sobre o projeto

- **Não afirme sem rodar.** O interpretador está aqui; execute o `.df` antes de
  dizer o que ele faz.
- **Não invente sintaxe.** Se não está em `doc/REFERENCIA.md` ou nos exemplos que
  rodam, provavelmente não existe. `=>` só existe em lambda; `end` não existe;
  `->` só em tipo de retorno.
- **Prefira citar um exercício** a inventar um exemplo: os 120 em `exercicios/`
  são verificados a cada execução.
- Ao criar exemplos novos, termine com `assert` verificando o resultado — é o
  padrão da casa e evita exemplo que não roda.

---

## Comandos úteis

```bash
dataforge run arquivo.df --time      # com tempo de execução
dataforge run arquivo.df --debug     # tokens + AST + traceback completo
dataforge check arquivo.df           # só sintaxe
dataforge tokens arquivo.df          # inspecionar o lexer
dataforge ast arquivo.df             # inspecionar o parser
dataforge repl                       # console interativo
dataforge new                        # gerar projeto de template

python3 exercicios/run_all.py 03     # rodar só o módulo 03
```

Para depurar o lexer numa linha específica:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from dataforge.lexer import tokenize
for t in tokenize('x := 7 ~/ 2'): print(t)"
```
