# CLAUDE.md — DataForge

Contexto operacional para o Claude Code trabalhar neste repositório. Leia antes
de editar qualquer coisa.

---

## O que é este projeto

**DataForge** é uma linguagem de programação interpretada, de propósito geral,
implementada em Python 3.10+ **sem dependências externas no runtime**. Não é um
DSL nem um transpilador: tem lexer, parser recursivo descendente, AST tipada,
analisador estático e interpretador de árvore próprios.

- Versão atual: **4.0.0**
- Extensão dos arquivos: `.df`
- Entrypoints: `dataforge` e `df` (mesmo `main`)
- Licença: MIT

### Verificação rápida — rode antes e depois de mexer

```bash
python3 -m pytest tests/ -q                          # 240 testes
python3 exercicios/run_all.py                        # 180 exercícios
for f in examples/*.df; do python3 -m dataforge run "$f" >/dev/null || echo "FALHOU $f"; done
```

O estado esperado é **tudo verde**. Se algo falhar antes da sua mudança, diga
isso ao usuário em vez de assumir que foi você.

---

## Mapa do código

```
dataforge/
  tokens.py        305   TokenType (enum) + KEYWORDS (81 palavras reservadas)
  lexer.py         556   texto → tokens. INDENT/DEDENT, interpolação, '//' vs '~/'
  parser.py       1941   recursivo descendente: tokens → AST
  ast_nodes.py     706   dataclasses dos nós
  interpreter.py  2703   interpretador de árvore — quase toda a semântica
  typechecker.py  1193   análise estática: nomes, aridade, tipos, alcance
  formatter.py     280   dataforge fmt
  linter.py        394   dataforge lint
  testrunner.py    194   dataforge test
  docgen.py        218   dataforge doc
  project.py       184   forge.toml
  environment.py    91   cadeia de escopos
  errors.py        167   hierarquia de erros, sinais de controle, stack traces
  builtins.py     1224   225 funções globais, sem import
  repl.py          409   console interativo
  cli.py          1055   CLI + templates de projeto
  stdlib/         7282   20 módulos Arcane.* (674 símbolos)

doc/               INSTALACAO, TUTORIAL, REFERENCIA, BIBLIOTECA_PADRAO,
                   ANALISE_E_ROADMAP (todos em pt-BR)
examples/          42 programas de demonstração
exercicios/        180 exercícios em 20 módulos + run_all.py
                   (os módulos 11-20 têm um .md explicativo por exercício)
tests/             test_dataforge.py (legado), test_regressoes.py, test_dataforge4.py
tools/             gerar_doc_stdlib.py
editor/vscode/     gramática TextMate
```

### Fluxo de execução

```
arquivo.df → tokenize() → parse() → [check_program()] → Interpreter().run(ast)
             lexer.py     parser.py  typechecker.py     interpreter.py
```

O interpretador despacha por nome de classe: um nó `GivenBlock` procura
`exec_GivenBlock`; uma expressão `BinaryOp` procura `eval_BinaryOp`.

**Para adicionar um recurso à linguagem, você mexe em cinco lugares**:
`tokens.py` (se houver palavra/símbolo novo) → `lexer.py` → `ast_nodes.py` +
`parser.py` → `interpreter.py` → `typechecker.py`.

---

## A linguagem em 90 segundos

```dataforge
// atribuição, constante, tipo opcional, saída
x := 10
steady PI := 3.14159
idade: Integer := 30
out $"x vale {x}, o dobro é {x * 2}"

// condicional e ternário
given x bigger 5:
    out "grande"
orif x is 5:
    out "cinco"
otherwise:
    out "pequeno"
rotulo := "par" given x % 2 is 0 otherwise "impar"

// laços
cycle i from 1 to 5 step 2:
    out i
cycle item in [1, 2, 3]:
    out item
persist x bigger 0:
    x -= 1

// coleções, compreensões, fatiamento, spread
nums := [1, 2, 3, 4, 5]
out [n * n cycle n in nums given n % 2 is 0]
out nums[1:3], nums[::-1]
out [...nums, 6]
primeiro, ...resto := nums

// ação com tipos
action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

// record: imutável, igualdade estrutural
record Ponto:
    x: Integer
    y: Integer
    action norma():
        yield sqrt(self.x ** 2 + self.y ** 2)

p := Ponto(3, 4)
p2 := p with {"y": 0}

// enum
enum Status:
    Ativo
    Inativo := "off"

// blueprint: mutável, herança, traits
blueprint Forma:
    action area():
        yield 0

blueprint Quadrado(lado) extends Forma:
    action area():
        yield self.lado ** 2

// pattern matching
match valor:
    point Integer as n when n bigger 100:
        yield "grande"
    point [a, b]:
        yield "par"
    point Ponto(x, y):
        yield "ponto"
    point {"tipo": t}:
        yield "vault"
    point Status.Ativo:
        yield "ligado"
    default:
        yield "outro"

// erros
monitor:
    trigger "falhou"
handle RuntimeError as e:
    out e.type, e.message
ensure:
    out "sempre roda"

// pipeline
out [1, 2, 3, 4, 5, 6]
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0

// generator preguiçoso
stream action fib():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b
out fib().take(8)

// módulos
adopt Arcane.Math as Math
adopt Arcane.Math.{sqrt, floor}
adopt {sqrt as raiz} from Arcane.Math
relay somar, Ponto
```

### Tabela de tradução

| Conceito | DataForge |
|----------|-----------|
| `=` | `:=` |
| `const` | `steady` |
| `print` | `out` |
| f-string | `$"texto {expr}"` |
| `if/elif/else` | `given/orif/otherwise` |
| ternário | `a given cond otherwise b` |
| `switch`/`match` | `match` / `point` / `when` / `default` |
| `for` | `cycle … from … to` / `cycle … in` |
| `while` | `persist` |
| `do..while` | `perform … persist` |
| `break`/`continue` | `halt`/`skip` |
| `def`/`return` | `action`/`yield` |
| generator | `stream action` / `emit` |
| `class`/`new` | `blueprint`/`spawn` |
| `@dataclass(frozen)` | `record` |
| `enum` | `enum` |
| `self`/`super` | `self`/`root` |
| `interface` | `trait` |
| `import`/`export` | `adopt`/`relay` |
| `try/catch/finally` | `monitor/handle/ensure` |
| `throw` | `trigger` |
| `true/false/null` | `yes/no/void` |
| `??` / `?.` | iguais |
| `in` / `not in` | iguais |
| spread `...` | igual |
| list comprehension | `[expr cycle x in fonte given cond]` |
| `filter/map/reduce` | `>> sift` / `>> morph` / `>> distill` |
| lambda | `lambda x: expr` ou `lambda a, b => expr` |
| decorator | `mark @nome` |
| `//` (div. inteira) | **`~/`** |

---

## Armadilhas — leia antes de escrever `.df`

Estas são as que mais custam tempo:

1. **`yield` retorna, `emit` produz.** `yield` encerra a ação. Para uma
   sequência, use `stream action` + `emit`.

2. **Divisão inteira: use `~/`.** `//` é **comentário por padrão** desde o 4.0.
   Só vira divisão quando seguido de dígito, `(`, ou chamada/índice/membro.
   `x // 2` é divisão; `x // nota` é comentário.

3. **Só espaços na indentação.** Tab é `SyncError`. 4 espaços por nível.

4. **`monitor` sem `handle` não engole o erro.** Ele só garante o `ensure`.

5. **`halt`, `skip` e `yield` atravessam `monitor`.** São `ControlSignal`
   (derivam de `BaseException`). Nunca capture `BaseException` no interpretador.

6. **Palavras reservadas não podem ser nomes.** As que mais pegam em português:
   `no`, `in`, `is`, `to`, `from`, `as`, `step`, `point`, `default`, `frame`,
   `stream`, `emit`, `forge`, `record`, `enum`, `when`. Já `range`, `cluster` e
   `vault` **são funções**, não reservadas.

7. **`self` dentro de métodos, sempre.** Escrever `x` em vez de `self.x` lê a
   variável do escopo externo.

8. **Records são imutáveis.** `p.x := 1` é erro; use `p with {"x": 1}`.

9. **Padrão de sequência não casa com vault**, e vice-versa. `[a, b]` só casa com
   `Cluster`; `{"k": v}` casa com `Vault`, record ou instância.

10. **A ordem dos `point` importa.** Do específico ao geral. Uma captura
    (`point n`) no topo torna tudo abaixo inalcançável.

11. **String simples não cruza linhas.** Para SQL multilinha, use `"""..."""`.

12. **`cycle from … to` é inclusivo** nos dois extremos.

13. **Generator infinito + `to_cluster()` trava.** Use `take(n)` ou garanta um
    `halt`.

14. **Sem sincronização entre threads.** Duas threads escrevendo na mesma
    variável perdem atualizações. Use `channel`.

---

## Convenções ao mexer no interpretador

### Estilo

- Comentários e docstrings do runtime em **inglês** nos arquivos antigos,
  **português** nos módulos 4.0 (`typechecker`, `formatter`, `linter`,
  `testrunner`, `docgen`, `project`, e os `arcane_*` novos). Siga o arquivo.
- Documentação em `doc/`, exercícios e mensagens ao usuário final em
  **português**.
- Sem dependências externas em `dataforge/`. A stdlib usa apenas a stdlib do
  Python.
- Mensagens de erro devem dizer **o que fazer**. Compare:
  `"Invalid assignment target"` (ruim) com `"'no' is a reserved keyword and
  cannot be assigned to. Pick another name."` (bom). Quando houver um nome
  parecido, sugira: o `typechecker` usa `difflib` para isso.

### Ao adicionar um recurso à linguagem

1. `tokens.py` — o `TokenType` e, se for palavra, a entrada em `KEYWORDS`.
2. `lexer.py` — reconhecer o símbolo (operadores de 2 chars vão no
   `two_char_map`; de 3, antes dele).
3. `ast_nodes.py` — o nó, como `@dataclass` com defaults.
4. `parser.py` — o método `parse_*`, ligado em `parse_statement` ou
   `parse_primary`.
5. `interpreter.py` — `exec_<Nó>` para instrução, `eval_<Nó>` para expressão.
6. `typechecker.py` — `st_<Nó>` ou `ex_<Nó>`, senão o analisador ignora o
   recurso novo.
7. **Teste em `tests/test_dataforge4.py`** e um exercício em `exercicios/`.
8. Atualize `doc/REFERENCIA.md` — inclusive a §1.6 e a gramática EBNF.

### Ao mexer em `KEYWORDS`

Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de adicionar
uma, confirme que o parser realmente a consome:

```bash
grep -c "TokenType.NOVA\b" dataforge/parser.py    # precisa ser > 0
```

Se for 0, ela só quebra código de usuário sem entregar nada. Sete palavras já
foram removidas por esse motivo.

Depois, sincronize `doc/REFERENCIA.md` §1.6 — **há um teste que compara as duas**
(`test_referencia_lista_exatamente_as_palavras_reservadas`).

### Ao mexer na stdlib

Os módulos são dicionários criados em `__new__`. Cuidado: dentro de um
`@staticmethod` referenciado por outro método da classe, use o nome da classe
(`ArcaneCortex._softmax`), **nunca `cls`** — `cls` não existe ali e o módulo
inteiro deixa de carregar.

Funções que recebem "um campo" devem aceitar **vault, record e instância**. Há
um helper para isso em `arcane_collections.py` (`_campo_de`). Esse foi um bug
real: `sort_by_field` devolvia `None` para todos os records.

Confirme que todos carregam e regenere a doc:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from dataforge.stdlib import get_module, list_modules
for m in sorted(set(list_modules())): assert get_module(m) is not None, m
print('ok')"

python3 tools/gerar_doc_stdlib.py
```

Ao criar um módulo novo, adicione-o em `stdlib/__init__.py` **e** no dicionário
`DESCRICOES` de `tools/gerar_doc_stdlib.py`.

---

## As ferramentas

| Comando | Arquivo | Faz |
|---------|---------|-----|
| `dataforge check` | `typechecker.py` | nomes, aridade, tipos, alcance (aceita arquivo, pasta ou padrão) |
| `dataforge test` | `testrunner.py` | descobre `*_test.df`, `tests/` |
| `dataforge fmt` | `formatter.py` | formata (`--check` só verifica) |
| `dataforge lint` | `linter.py` | estilo e higiene |
| `dataforge doc` | `docgen.py` | Markdown a partir dos comentários |
| `dataforge init` | `project.py` | cria `forge.toml` e esqueleto |
| `dataforge info` | `project.py` | mostra o manifesto |
| `dataforge repl` | `repl.py` | console com `:type`, `:ast`, `:load` |

### As ferramentas não podem morrer no meio da pasta

`check`, `fmt` e `lint` aceitam arquivo, pasta ou padrão, e resolvem a lista
com `_expandir()`. A leitura passa por `_ler()`, que devolve `(fonte, None)`
ou `(None, motivo)`: um `.df` fora de UTF-8 é reportado e os demais seguem.
Antes disso, um único arquivo mal codificado derrubava `fmt .` inteiro com um
`UnicodeDecodeError` cru — e `check` numa pasta estourava `IsADirectoryError`.

Há teste para os dois casos em `tests/test_regressoes.py`, mais um que proíbe
qualquer `.df` fora de UTF-8 no repositório.

### O analisador estático é otimista de propósito

Quando não consegue **provar** que algo está errado, fica calado. Um falso alarme
ensina o usuário a ignorar mensagens. Dentro de `monitor`/`retry`, erros são
rebaixados a aviso — provocar falha ali é legítimo.

Calibragem atual: **0 erros** em 222 arquivos conhecidamente bons.

### O formatador precisa ser idempotente

`format_source(format_source(x)) == format_source(x)`. Há teste para isso. A
profundidade vem do INDENT/DEDENT do lexer, nunca da contagem de espaços do
original.

---

## Testes

| Arquivo | Como roda | Cobre |
|---------|-----------|-------|
| `tests/test_dataforge4.py` | `pytest` | recursos 4.0: interpolação, ternário, records, enums, padrões, generators, stack traces, checker, stdlib nova, ferramentas |
| `tests/test_regressoes.py` | `pytest` | bugs já corrigidos + sincronia da doc |
| `tests/test_dataforge.py` | `pytest` **e** script | 69 verificações da suíte original |
| `exercicios/run_all.py` | script | 180 exercícios, cada um com `assert` |
| `examples/*.df` | manual | 42 programas maiores |

**Ao corrigir um bug, escreva primeiro o teste que falha.** Todos os bugs
corrigidos no 3.1 e no 4.0 têm teste correspondente.

`tests/test_dataforge.py` roda nas duas formas — o `sys.exit` só dispara sob
`__main__`. Não renomeie `verificar()` para `test()`: o pytest tentaria coletá-la.

---

## Estado conhecido e limitações

O que **funciona e está testado**: tudo do 3.1 mais tipos verificados, análise
estática com sugestões, stack traces, interpolação, ternário, `??`, `?.`, `in`,
spread/rest, desestruturação, compreensões, records imutáveis com `with`, enums
com valores, pattern matching estrutural completo, generators preguiçosos
(inclusive infinitos), imports seletivos, `relay` real, detecção de ciclos,
`forge.toml`, e as seis ferramentas de linha de comando.

O que **ainda não existe** (não invente que existe):

- **Generics** — `Cluster<T>`, ações genéricas.
- **Exaustividade** — o `match` não avisa se um membro de enum ficou fora.
- **Contrato de trait** — não se verifica se o blueprint implementou tudo.
- **LSP e debugger** — a gramática TextMate só colore.
- **Gerenciador de pacotes** — `forge.toml` tem a seção `[dependencies]`, mas
  nada a resolve.
- **Bytecode** — é interpretador de árvore, sem otimização.
- **Sincronização entre threads** — sem mutex/semáforo; use `channel`.
- **`receive` bloqueante** — devolve `void` na hora se a fila está vazia.
- **`parallel`** roda **cada instrução** numa thread, não um bloco por thread.
- **`frame`, `train`, `predict`** são marcadores sintáticos: devolvem um vault
  com `__type__` e nada acontece.
- **`async/await`** resolve de forma síncrona; não há paralelismo real ali.

O roadmap completo está em `doc/ANALISE_E_ROADMAP.md`.

---

## Ao responder sobre o projeto

- **Não afirme sem rodar.** O interpretador está aqui; execute o `.df` antes de
  dizer o que ele faz.
- **Não invente sintaxe.** Se não está em `doc/REFERENCIA.md` ou nos exercícios
  que rodam, provavelmente não existe. `=>` só em lambda; `end` não existe; `->`
  só em tipo de retorno; `when` só em guarda de padrão.
- **Prefira citar um exercício** a inventar um exemplo: os 180 são verificados a
  cada execução, e os dos módulos 11-20 têm `.md` explicativo ao lado.
- Ao criar exemplos novos, termine com `assert` verificando o resultado.

---

## Comandos úteis

```bash
dataforge run arquivo.df --time      # com tempo de execução
dataforge run arquivo.df --debug     # tokens + AST + traceback
dataforge check src/ --strict        # avisos como erros
dataforge test tests/ -v --fail-fast
dataforge fmt . --check
dataforge lint src/
dataforge doc src/ --out=doc/API.md
dataforge repl

python3 exercicios/run_all.py 14     # só o módulo 14
python3 tools/gerar_doc_stdlib.py    # regenera BIBLIOTECA_PADRAO.md
```

Depurar o lexer numa linha específica:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from dataforge.lexer import tokenize
for t in tokenize('x := 7 ~/ 2'): print(t)"
```

Rodar o analisador sobre tudo:

```bash
python3 -c "
import sys, glob; sys.path.insert(0,'.')
from dataforge.lexer import tokenize
from dataforge.parser import parse
from dataforge.typechecker import check_program
for f in glob.glob('examples/*.df') + glob.glob('exercicios/*/*.df'):
    for d in check_program(parse(tokenize(open(f,encoding='utf-8').read()), f), f):
        if d.severity == 'error': print(d.format(f, color=False))"
```
