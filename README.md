<div align="center">

# DataForge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/estevam5s/DataForge)
[![Tests](https://img.shields.io/badge/testes-240%20passando-brightgreen.svg)](tests/)
[![Exercises](https://img.shields.io/badge/exerc%C3%ADcios-180%2F180-brightgreen.svg)](exercicios/)

**Uma linguagem de programação com vocabulário próprio, tipos verificados,
pattern matching estrutural, pipelines nativos, um framework web próprio
e 22 módulos de biblioteca
padrão — escrita em Python puro, sem dependências.**

[Instalação](#instalação) • [Tutorial](doc/TUTORIAL.md) • [Referência](doc/REFERENCIA.md) • [216 exercícios](exercicios/) • [Biblioteca](doc/BIBLIOTECA_PADRAO.md) • [Roadmap](doc/ANALISE_E_ROADMAP.md)

</div>

---

```dataforge
adopt Arcane.Collections as Col

record Produto:
    nome: String
    preco: Number
    estoque: Integer

enum Situacao:
    EmFalta
    Critico
    Normal

action situacao_de(p: Produto) -> Situacao:
    match p:
        point Produto(estoque := 0):
            yield Situacao.EmFalta
        point Produto(estoque := e) when e smaller 5:
            yield Situacao.Critico
        default:
            yield Situacao.Normal

estoque := [
    Produto("Mouse", 80.0, 15),
    Produto("Teclado", 200.0, 3),
    Produto("Monitor", 1200.0, 0)
]

patrimonio := estoque
    >> morph p: p.preco * p.estoque
    >> distill acc, v: acc + v 0

cycle p in Col.sort_by_field(estoque, "preco", yes):
    out $"{p.nome.pad_end(10)} {situacao_de(p).name.pad_end(10)} R$ {p.preco * p.estoque}"

out $"\npatrimônio: R$ {patrimonio}"
out $"repor: {[p.nome cycle p in estoque given situacao_de(p) isnt Situacao.Normal]}"
```

```
Monitor    EmFalta    R$ 0.0
Teclado    Critico    R$ 600.0
Mouse      Normal     R$ 1200.0

patrimônio: R$ 1800.0
repor: [Teclado, Monitor]
```

---

## Por que DataForge

| | |
|---|---|
| **Vocabulário que descreve intenção** | `given`/`orif`/`otherwise`, `cycle`, `blueprint`, `monitor`/`handle`/`ensure` — as palavras dizem o que o código faz |
| **Tipos quando você quiser** | anotações opcionais, verificadas em tempo de execução **e** por análise estática |
| **Erros que ensinam** | `dataforge check` aponta linha, coluna e sugere a correção antes de executar |
| **Pattern matching estrutural** | por tipo, sequência, record, vault, enum — com guardas |
| **Pipelines são sintaxe** | `>> sift`, `>> morph`, `>> distill` fazem parte da gramática |
| **Generators preguiçosos** | `stream action` + `emit`, inclusive sequências infinitas |
| **Ferramentas oficiais** | `check`, `test`, `fmt`, `lint`, `doc`, `repl`, `init` |
| **Bateria inclusa** | 22 módulos com 753 símbolos + 225 funções globais |
| **Zero dependências** | Python 3.10+ e nada mais |

---

## Instalação

**macOS e Linux** — um comando:

```bash
curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
```

Com `wget`, se preferir:

```bash
wget -qO- https://dataforge-lang.vercel.app/instalar.sh | sh
```

**Windows** (PowerShell):

```powershell
irm https://dataforge-lang.vercel.app/instalar.ps1 | iex
```

O instalador cria um ambiente próprio em `~/.dataforge`. Não mexe no Python
do sistema, não pede sudo, e desinstalar é apagar a pasta.

Ele também instala a **coloração de sintaxe** no VS Code, Insiders, Cursor,
VSCodium e Windsurf — todos os que encontrar. Reinicie o editor e todo `.df`
abre com as palavras reservadas coloridas, 23 snippets e a indentação de 4
espaços que a linguagem exige. Para refazer isso depois: `dataforge editor`.

**Docker** — sem instalar nada, nem Python:

```bash
docker run --rm -it estevan5s/dataforge repl
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
```

**Do código-fonte**:

```bash
git clone https://github.com/estevam5s/DataForge.git
cd DataForge
pip install -e .
```

Guia completo, com solução de problemas:
[`doc/INSTALACAO.md`](doc/INSTALACAO.md) ou
[dataforge-lang.vercel.app/docs/instalacao](https://dataforge-lang.vercel.app/docs/instalacao).

### Primeiro projeto

```bash
dataforge init meu-app
cd meu-app
dataforge run
dataforge test
```

### Pacotes

O gerenciador vem junto — não há binário separado:

```bash
dataforge add validador       # instala e grava no forge.toml
dataforge add tabela datas
dataforge install             # instala o que o forge.toml declara
dataforge search cpf          # procura no registro
dataforge list                # o que está instalado
```

```dataforge
adopt validador as V
adopt tabela as Tb

out V.cpf("529.982.247-25")                        // yes
out Tb.render([["Ana", 30]], ["Nome", "Idade"])
```

Semver (`^1.2.3`, `~1.2`, `>=1.0 <2.0`), lockfile com sha256, dependências
de registro, pasta local, git ou URL. Detalhes em
[Pacotes](https://dataforge-lang.vercel.app/docs/pacotes).

---

## A linguagem

### Fundamentos

```dataforge
nome := "DataForge"
steady VERSAO := "4.0.0"
idade: Integer := 30                 // tipo opcional, verificado

out $"Ola {nome}, versão {VERSAO}"   // interpolação
out 7 ~/ 2, 2 ** 10, 0 <= 5 <= 10    // operadores
out "a" in "casa", void ?? "padrão"  // pertinência, coalescência
```

### Controle de fluxo

```dataforge
idade := 30

given idade bigger_eq 18:
    out "adulto"
orif idade bigger_eq 12:
    out "adolescente"
otherwise:
    out "criança"

rotulo := "par" given idade % 2 is 0 otherwise "impar"    # ternário

cycle i from 1 to 5 step 2:
    out i

persist idade bigger 0:
    idade -= 10
```

### Coleções

```dataforge
nums := [1, 2, 3, 4, 5, 6]

out [n * n cycle n in nums given n % 2 is 0]    // compreensão
out {n: n * 2 cycle n in nums}                  // compreensão de vault
out nums[1:4], nums[::-1]                       // fatiamento
out [...nums, 7]                                // spread

primeiro, ...resto := nums                      // desestruturação
{nome, idade} := {"nome": "Ana", "idade": 30}
```

### Ações

```dataforge
action somar(a: Integer, b: Integer := 0) -> Integer:
    yield a + b

dobro := lambda x: x * 2

action registrar(fn):                  # um decorador é uma ação que envolve outra
    action envolvida(dados):
        out $"processando {len(dados)} item(ns)"
        yield fn(dados)
    yield envolvida

mark @registrar
action processar(dados):
    defer:
        out "limpou"                   # roda em qualquer caminho de saída
    yield dados >> morph d: d * 2

out somar(2), dobro(21), processar([1, 2, 3])
```

### Records e enums

```dataforge
record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"

    action maior_de_idade():
        yield self.idade bigger_eq 18

u := Usuario("Ana", 30)
u2 := u with {"idade": 31}          // cópia; records são imutáveis
out Usuario("Ana", 30) is u          // yes — igualdade estrutural

enum Status:
    Ativo
    Inativo := "off"

out Status.Ativo.name, Status.from_value("off").name
```

### Pattern matching

```dataforge
action descrever(valor):
    match valor:
        point 0:
            yield "zero"
        point Integer as n when n bigger 100:
            yield "grande"
        point [primeiro, ...resto]:
            yield $"lista de {len(resto) + 1}"
        point Usuario(nome := n, idade := i) when i smaller 18:
            yield $"{n} é menor"
        point {"tipo": t}:
            yield $"vault {t}"
        point Status.Ativo:
            yield "ligado"
        default:
            yield "outro"

out descrever(0), descrever(500), descrever([1, 2, 3])
out descrever(Usuario("Kid", 12)), descrever(Status.Ativo)
```

### Erros

```dataforge
record Conta:
    titular: String
    saldo: Number

action sacar(conta, valor):
    guard valor bigger 0, "valor precisa ser positivo"
    guard valor smaller_eq conta.saldo, "saldo insuficiente"
    yield conta with {"saldo": conta.saldo - valor}

conta := Conta("Ana", 100)
out sacar(conta, 30)

monitor:
    sacar(conta, 9999)
handle e:
    out $"{e.type}: {e.message}"
ensure:
    out "sempre roda"

tentativas := {"n": 0}
retry 3:
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] smaller 3:
        trigger "instabilidade"
    out $"conseguiu na tentativa {tentativas["n"]}"
handle e:
    out $"desistiu: {e}"
```

Erros trazem a pilha de chamadas:

```
RuntimeError: Division by zero
  em calculadora.df:12:15

    12 |     yield total / divisor
       |           ^

  Pilha de chamadas (mais recente primeiro):
    em media                  calculadora.df:12
    em relatorio              calculadora.df:28
    em main                   calculadora.df:45
```

### Pipelines e generators

```dataforge
record Venda:
    cliente: String
    valor: Number

vendas := [Venda("Ana", 250), Venda("Bruno", 80), Venda("Carla", 400)]

out vendas
    >> sift v: v.valor bigger 100
    >> morph v: v.valor * 1.1
    >> distill acc, v: acc + v 0

stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

out fibonacci().take(10)      // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Módulos

```dataforge
adopt Arcane.Math as Math              # o módulo inteiro
adopt Arcane.Math.{sqrt, floor}        # seletivo
adopt {sqrt as raiz} from Arcane.Math  # com apelido

out Math.factorial(5), sqrt(16), raiz(25)

action somar(a, b):
    yield a + b

relay somar                            # controla o que este módulo exporta
```

---

## Tabela de tradução

| Conceito | DataForge | | Conceito | DataForge |
|----------|-----------|---|----------|-----------|
| `=` | `:=` | | `class` / `new` | `blueprint` / `spawn` |
| `const` | `steady` | | `@dataclass(frozen)` | `record` |
| `print` | `out` | | `enum` | `enum` |
| f-string | `$"{x}"` | | `self` / `super` | `self` / `root` |
| `if/elif/else` | `given/orif/otherwise` | | `interface` | `trait` |
| ternário | `a given c otherwise b` | | `import` / `export` | `adopt` / `relay` |
| `match/case` | `match` / `point` / `when` | | `try/catch/finally` | `monitor/handle/ensure` |
| `for` | `cycle` | | `throw` | `trigger` |
| `while` | `persist` | | `true/false/null` | `yes/no/void` |
| `break`/`continue` | `halt`/`skip` | | `??` / `?.` / `in` | iguais |
| `def` / `return` | `action` / `yield` | | spread `...` | igual |
| generator | `stream action` / `emit` | | `filter/map/reduce` | `>> sift/morph/distill` |
| list comprehension | `[e cycle x in f given c]` | | `//` (div. inteira) | **`~/`** |

---

## Ferramentas

```bash
dataforge init [pasta]        # cria forge.toml e o esqueleto
dataforge run [arquivo.df]    # executa (sem argumento usa a entrada do manifesto)
dataforge check <alvo>        # análise estática: nomes, aridade, tipos
dataforge test [alvo] -v      # descobre e roda *_test.df e tests/
dataforge fmt <alvo> --check  # formata
dataforge lint <alvo>         # estilo e higiene
dataforge doc <alvo> --out=…  # documentação Markdown
dataforge repl                # console interativo
dataforge info                # mostra o manifesto
```

### `dataforge check` — o que ele encontra

```
src/main.df:9:11: erro: Parameter 'a' of 'somar' expects Integer but got String
    sugestão: Pass a Integer
src/main.df:10:5: erro: Undefined action 'sommar'
    sugestão: Did you mean 'somar'?
src/main.df:23:1: aviso: Action 'processar' declares '-> Integer' but can end without a 'yield'
    sugestão: Add a 'yield' at the end, or drop the return type
```

Nomes indefinidos, aridade errada, tipos incompatíveis, campos de record, membros
de enum, constantes reatribuídas, código inalcançável, retorno ausente — tudo
antes de executar uma linha.

### `forge.toml`

```toml
[project]
name = "meu-app"
version = "0.1.0"
entry = "src/main.df"
dataforge = ">=4.0"

[scripts]
start = "run src/main.df"
test = "test tests/"
```

Qualquer chave em `[scripts]` vira um comando: `dataforge start`.

### Em integração contínua

```bash
dataforge fmt . --check && dataforge check . && dataforge test
```

---

## Biblioteca padrão

22 módulos, 753 símbolos, mais 225 funções globais sem import.

| Módulo | Símbolos | Para quê |
|--------|----------|----------|
| `Arcane.Analytics` | 65 | regressão, correlação, clustering, gráficos ASCII |
| `Arcane.Text` | 58 | formatação, tabelas, caixas, conversão de caixa |
| `Arcane.Functional` | 56 | composição, lentes, Maybe/Either, transdutores |
| `Arcane.Time` | 54 | datas, durações, cronômetro, idade |
| `Arcane.Math` | 51 | matemática, álgebra linear, estatística |
| `Arcane.Async` | 46 | promessas, filas, agendamento |
| `Arcane.Database` | 39 | SQLite: tabelas, consultas, transações |
| `Arcane.Crypto` | 38 | hashes, HMAC, senhas, base64, aleatoriedade segura |
| `Arcane.OS` | 38 | sistema, ambiente, disco, processo |
| `Arcane.Collections` | 35 | pilha, fila, heap, grafo, união-busca |
| `Arcane.Test` | 34 | asserções e suítes |
| `Arcane.Regex` | 32 | regex e validadores BR (CPF, CNPJ) |
| `Arcane.IO` | 27 | arquivos, JSON, CSV, diretórios |
| `Arcane.Serialization` | 26 | JSON, CSV, INI, TOML, XML |
| `Arcane.Http` | 17 | servidor HTTP com rotas e middleware |
| `Arcane.Process` | 15 | processos externos, stdout, exit code |
| `Arcane.Logging` | 14 | níveis, campos estruturados, arquivo, JSON |
| `Arcane.Data` | 13 | DataFrames e transformações |
| `Arcane.Web` | 11 | cliente HTTP, URL, JSON |
| `Arcane.Cortex` | 5 | blocos de rede neural e NLP |

Referência completa: [`doc/BIBLIOTECA_PADRAO.md`](doc/BIBLIOTECA_PADRAO.md)
(gerada a partir do código com `tools/gerar_doc_stdlib.py`).

---

## Kiln — o framework web

O DataForge tem um framework web próprio, com **sintaxe na linguagem**. Não é
um módulo com `lambda` dentro: uma rota se lê como uma rota.

```dataforge
adopt Kiln

server loja on 8080:
    middleware Kiln.logger()
    views "./paginas"

    route GET "/":
        render "catalogo.html" with {"produtos": produtos}

    route GET "/api/produtos/:id":
        p := achar(int(params["id"]))
        given p is void:
            respond 404 json {"erro": "não achei"}
        respond json p

    route POST "/api/produtos":
        respond 201 json criar(body)

ignite loja
```

Roteamento com `:param` e `*curinga`, middleware, CORS, limite de taxa,
autenticação, sessão com cookie, templates com escape automático, arquivos
estáticos e páginas de erro. **Zero dependências** — `http.server` e mais nada.

E dá para testar sem abrir socket:

```dataforge
r := Kiln.test(loja, "GET", "/api/produtos/2")
assert r["status"] is 200
```

O 404 e o **405 com `Allow`** vêm de graça; um erro na rota vira 500 sem
derrubar o servidor; `../` num caminho estático é recusado antes de o arquivo
ser aberto.

O projeto [`projetos/loja-web`](projetos/loja-web/) é um site completo —
catálogo, ficha, relatório, login e um `/relatorio.xlsx` gerado no pedido —
com 29 testes que rodam em 0,06 s.

Documentação: [doc/KILN.md](doc/KILN.md) ou
[dataforge-lang.vercel.app/docs/kiln](https://dataforge-lang.vercel.app/docs/kiln).

---

## Dados: banco, análise e planilhas

```dataforge
adopt Arcane.Database as DB
adopt Arcane.Analytics as An
adopt Arcane.Excel as Xls

registros := DB.query(banco, "SELECT * FROM vendas")
An.describe(An.from_records(registros))     # descreve cada coluna

livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", registros)
Xls.formula(aba, "E7", "SUM(E2:E6)")        # o Excel calcula ao abrir
Xls.save(livro, "relatorio.xlsx")
```

O `.xlsx` é escrito e lido sem dependência externa — o arquivo abre no Excel,
no LibreOffice e no Google Sheets, e é lido de volta por openpyxl e pandas.

---

## Aprendendo

| Recurso | O que é |
|---------|---------|
| [**doc/TUTORIAL.md**](doc/TUTORIAL.md) | a linguagem do zero, com exemplos que rodam |
| [**doc/REFERENCIA.md**](doc/REFERENCIA.md) | gramática EBNF, palavras-chave, precedência, semântica |
| [**doc/BIBLIOTECA_PADRAO.md**](doc/BIBLIOTECA_PADRAO.md) | assinaturas dos 22 módulos |
| [**doc/INSTALACAO.md**](doc/INSTALACAO.md) | instalação passo a passo |
| [**doc/ANALISE_E_ROADMAP.md**](doc/ANALISE_E_ROADMAP.md) | estado técnico e o que falta |
| [**exercicios/**](exercicios/) | 216 exercícios; os módulos 11-26 com `.md` explicativo |
| [**examples/**](examples/) | 42 programas maiores |

### Os 216 exercícios

```bash
python3 exercicios/run_all.py        # todos
python3 exercicios/run_all.py 14     # só o módulo 14
```

Cada exercício **verifica o próprio resultado com `assert`**. Os módulos 11–20
trazem um `.md` ao lado de cada `.df`, com enunciado, conceitos, saída esperada e
sugestões.

| Módulo | N | Tema |
|--------|---|------|
| 01 | 12 | fundamentos: tipos, operadores, precedência |
| 02 | 12 | controle de fluxo: condicionais e os quatro laços |
| 03 | 14 | coleções: clusters, fatiamento, vaults, busca |
| 04 | 10 | strings: métodos, regex, templates |
| 05 | 14 | ações: aridade, recursão, closures, lambdas, decoradores |
| 06 | 14 | blueprints: herança, traits, polimorfismo |
| 07 | 10 | erros: `monitor`, `handle` tipado, `guard`, `retry` |
| 08 | 12 | pipelines: `sift`/`morph`/`distill`, composição |
| 09 | 12 | módulos: `adopt`, Math, Analytics, IO, SQLite |
| 10 | 10 | avançado: async, threads, árvore binária, RPN |
| **11** | 6 | **tipos e checagem estática** |
| **12** | 6 | **records e enums** |
| **13** | 6 | **desestruturação, spread, compreensões, interpolação** |
| **14** | 6 | **pattern matching estrutural** |
| **15** | 6 | **streams e generators** |
| **16** | 6 | **módulos, testes, biblioteca publicável** |
| **17** | 6 | **tempo, sistema, processos, logging** |
| **18** | 6 | **serialização, arquivos, SQLite, HTTP** |
| **19** | 6 | **concorrência: async, threads, canais, retry** |
| **20** | 6 | **projetos finais: CLI, análise de dados, interpretador** |

---

## Desenvolvimento

```bash
pip install -e ".[dev]"

python3 -m pytest tests/ -q       # 240 testes
python3 exercicios/run_all.py     # 216 exercícios
```

Contexto para trabalhar no interpretador: [`CLAUDE.md`](CLAUDE.md).

### Arquitetura

```
arquivo.df → tokenize() → parse() → check_program() → Interpreter().run(ast)
             lexer.py     parser.py  typechecker.py   interpreter.py
```

| Arquivo | Responsabilidade | Linhas |
|---------|------------------|--------|
| `dataforge/tokens.py` | TokenType e as 81 palavras reservadas | 305 |
| `dataforge/lexer.py` | texto → tokens, INDENT/DEDENT, interpolação | 556 |
| `dataforge/parser.py` | recursivo descendente: tokens → AST | 1941 |
| `dataforge/ast_nodes.py` | nós da AST como dataclasses | 706 |
| `dataforge/interpreter.py` | interpretador de árvore: a semântica | 2703 |
| `dataforge/typechecker.py` | análise estática | 1193 |
| `dataforge/formatter.py` | `dataforge fmt` | 280 |
| `dataforge/linter.py` | `dataforge lint` | 394 |
| `dataforge/testrunner.py` | `dataforge test` | 194 |
| `dataforge/docgen.py` | `dataforge doc` | 218 |
| `dataforge/project.py` | `forge.toml` | 184 |
| `dataforge/builtins.py` | 225 funções globais | 1224 |
| `dataforge/stdlib/` | os 22 módulos, incluindo o Kiln | 8200 |

---

## Estado do projeto

| Verificação | Resultado |
|-------------|-----------|
| Testes unitários | 272 passando |
| Exercícios | 180/180 |
| Exemplos | 42/42 |
| Módulos da stdlib | 20/20 carregam |
| Pacotes do registro | 4, com 46 testes |
| Análise estática sobre o repositório | 0 erros em 233 arquivos |
| Instalação via pip, curl e Docker | funciona |

### O que ainda não existe

Generics, verificação de exaustividade em `match`, contrato de trait, LSP,
debugger, VM de bytecode e sincronização entre threads.
Detalhado em [`doc/ANALISE_E_ROADMAP.md`](doc/ANALISE_E_ROADMAP.md).

---

## Licença

MIT — veja [LICENSE](LICENSE).
