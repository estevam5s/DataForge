<div align="center">

# DataForge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-3.1.0-green.svg)](https://github.com/estevam5s/DataForge)
[![Tests](https://img.shields.io/badge/testes-77%20passando-brightgreen.svg)](tests/)
[![Exercises](https://img.shields.io/badge/exerc%C3%ADcios-120%2F120-brightgreen.svg)](exercicios/)

**Uma linguagem de programação interpretada, com vocabulário próprio, pipelines
nativos e biblioteca padrão de 454 símbolos — escrita em Python puro, sem
dependências.**

[Instalação](#instalação) • [Tutorial](doc/TUTORIAL.md) • [Referência](doc/REFERENCIA.md) • [Exercícios](exercicios/) • [Biblioteca](doc/BIBLIOTECA_PADRAO.md)

</div>

---

```dataforge
// Sistema de estoque em 20 linhas de DataForge
adopt Arcane.Text as Text

blueprint Produto(nome, preco, quantidade):
    action valor_total():
        yield self.preco * self.quantidade

    action baixa(qtd):
        guard qtd smaller_eq self.quantidade, "estoque insuficiente"
        self.quantidade := self.quantidade - qtd
        yield self.quantidade

estoque := [
    spawn Produto("Mouse", 80.0, 15),
    spawn Produto("Teclado", 200.0, 4)
]

patrimonio := estoque
    >> morph p: p.valor_total()
    >> distill acc, v: acc + v 0

out Text.box("Inventario")
out "patrimonio: R$", patrimonio
out "criticos:", estoque >> sift p: p.quantidade smaller 5 >> morph p: p.nome
```

```
┌────────────┐
│ Inventario │
└────────────┘
patrimonio: R$ 2000.0
criticos: [Teclado]
```

---

## Por que DataForge

| | |
|---|---|
| **Vocabulário que descreve intenção** | `given`/`orif`/`otherwise`, `cycle`, `blueprint`, `monitor`/`handle`/`ensure` — as palavras dizem o que o código faz, não como a máquina executa |
| **Pipelines são sintaxe** | `>> sift`, `>> morph`, `>> distill` fazem parte da gramática, não de uma biblioteca |
| **Tipos quando você quiser** | `action media(n: Cluster) -> Float:` — opcional, verificado em tempo de execução |
| **Erros de primeira classe** | `handle` tipado, `retry`, `guard`, `validate`, `defer`, `propagate` |
| **Bateria inclusa** | 13 módulos `Arcane.*`: estatística, SQLite, servidor HTTP, regex, testes |
| **Zero dependências** | Python 3.10+ e nada mais |

---

## Instalação

```bash
git clone https://github.com/estevam5s/DataForge.git
cd DataForge

python3 -m venv .venv && source .venv/bin/activate
pip install .

dataforge version
```

Guia detalhado, com Windows e solução de problemas:
[`doc/INSTALACAO.md`](doc/INSTALACAO.md).

### Primeiro programa

```bash
echo 'out "Ola, DataForge!"' > ola.df
dataforge run ola.df
```

---

## A linguagem em um minuto

```dataforge
// Variáveis e constantes
nome := "DataForge"
steady VERSAO := "3.1.0"
idade: Integer := 30              // tipo opcional, verificado

// Condicionais
given idade bigger_eq 18:
    out "adulto"
orif idade bigger_eq 12:
    out "adolescente"
otherwise:
    out "crianca"

// Laços
cycle i from 1 to 5 step 2:
    out i
cycle item in ["a", "b"]:
    out item

// Ações
action fatorial(n: Integer) -> Integer:
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

out fatorial(6)

// Blueprints
blueprint Ponto(x, y):
    action norma():
        yield sqrt(self.x ** 2 + self.y ** 2)
    action toString():
        yield "(" + str(self.x) + ", " + str(self.y) + ")"

out spawn Ponto(3, 4)

// Erros
monitor:
    x := 10 / 0
handle RuntimeError as e:
    out "capturado:", e.message
ensure:
    out "sempre roda"

// Pipelines
out [1, 2, 3, 4, 5, 6]
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0

// Módulos
adopt Arcane.Math as Math
out Math.sqrt(16), Math.is_prime(97)
```

### Tabela de tradução

Se você já programa em outra linguagem:

| Conceito | DataForge | | Conceito | DataForge |
|----------|-----------|---|----------|-----------|
| `=` | `:=` | | `class` / `new` | `blueprint` / `spawn` |
| `const` | `steady` | | `self` / `super` | `self` / `root` |
| `print` | `out` | | `interface` | `trait` |
| `if/elif/else` | `given/orif/otherwise` | | `import` / `export` | `adopt` / `relay` |
| `switch/case` | `match/point` | | `try/catch/finally` | `monitor/handle/ensure` |
| `for` | `cycle` | | `throw` | `trigger` |
| `while` | `persist` | | `true/false/null` | `yes/no/void` |
| `break/continue` | `halt/skip` | | `filter/map/reduce` | `>> sift/morph/distill` |
| `def` / `return` | `action` / `yield` | | `//` (div. inteira) | `~/` |

---

## Comandos

```bash
dataforge run programa.df        # executa
dataforge run programa.df --time # com tempo de execução
dataforge check programa.df      # só verifica a sintaxe
dataforge repl                   # console interativo
dataforge new                    # cria projeto de um template
dataforge tokens programa.df     # inspeciona o lexer
dataforge ast programa.df        # inspeciona o parser
```

`df` é um atalho para `dataforge`.

### Templates de projeto

`dataforge new` gera um projeto pronto e executável:

| Template | O que traz |
|----------|-----------|
| **CLI Tool** | Ferramenta de linha de comando |
| **Data Analytics** | Estatística e pipelines sobre dados |
| **Orientado a Objetos** | Blueprints, herança e traits |
| **Suíte de Testes** | Módulo com `relay` + testes |
| **API REST** | Servidor HTTP com CRUD completo |
| **Web App** | Servidor com HTML e estáticos |

---

## Biblioteca padrão

13 módulos, 454 símbolos. Importe com `adopt`:

| Módulo | Símbolos | Para quê |
|--------|----------|----------|
| `Arcane.Analytics` | 65 | regressão, correlação, clustering, gráficos ASCII |
| `Arcane.Text` | 58 | formatação, tabelas, caixas, conversão de caixa |
| `Arcane.Functional` | 56 | composição, lentes, Maybe/Either, transdutores |
| `Arcane.Math` | 51 | matemática, álgebra linear, estatística |
| `Arcane.Async` | 46 | promessas, filas, agendamento |
| `Arcane.Database` | 39 | SQLite: tabelas, queries, migrações |
| `Arcane.Test` | 34 | asserções e suítes |
| `Arcane.Regex` | 32 | regex e validadores BR (CPF, CNPJ) |
| `Arcane.IO` | 27 | arquivos, JSON, CSV, shell |
| `Arcane.Http` | 17 | servidor HTTP com rotas e middleware |
| `Arcane.Data` | 13 | DataFrames e transformações |
| `Arcane.Web` | 11 | cliente HTTP, URL, JSON |
| `Arcane.Cortex` | 5 | blocos de rede neural e NLP |

Mais 225 funções globais disponíveis sem import. Referência completa:
[`doc/BIBLIOTECA_PADRAO.md`](doc/BIBLIOTECA_PADRAO.md).

### Um servidor HTTP de verdade

```dataforge
adopt Arcane.Http as Http

app := Http.create("Minha API")
Http.cors(app)

itens := [{"id": 1, "nome": "Primeiro"}]

action listar(req, res):
    res.json(itens)

Http.get(app, "/api/itens", listar)
Http.listen(app, 3000)
```

---

## Aprendendo

| Recurso | O que é |
|---------|---------|
| [**doc/TUTORIAL.md**](doc/TUTORIAL.md) | A linguagem inteira, do zero, com exemplos que rodam |
| [**doc/REFERENCIA.md**](doc/REFERENCIA.md) | Gramática EBNF, palavras-chave, precedência, semântica |
| [**doc/BIBLIOTECA_PADRAO.md**](doc/BIBLIOTECA_PADRAO.md) | Assinaturas de todos os módulos `Arcane.*` |
| [**doc/INSTALACAO.md**](doc/INSTALACAO.md) | Instalação passo a passo e solução de problemas |
| [**exercicios/**](exercicios/) | 120 exercícios comentados, cada um verifica o próprio resultado |
| [**examples/**](examples/) | 42 programas maiores: banco, loja, jogos, calculadora |
| [**doc/ANALISE_E_ROADMAP.md**](doc/ANALISE_E_ROADMAP.md) | Estado técnico e o que falta implementar |

### Os 120 exercícios

```bash
python3 exercicios/run_all.py        # roda todos
python3 exercicios/run_all.py 05     # só o módulo 05
```

| Módulo | N | Tema |
|--------|---|------|
| 01 | 12 | fundamentos: tipos, operadores, precedência, conversão |
| 02 | 12 | controle de fluxo: condicionais e os quatro laços |
| 03 | 14 | coleções: clusters, fatiamento, vaults, busca, ordenação |
| 04 | 10 | strings: métodos, regex, templates, cifra de César |
| 05 | 14 | ações: aridade, recursão, closures, lambdas, decoradores |
| 06 | 14 | blueprints: herança, traits, polimorfismo, padrões de projeto |
| 07 | 10 | erros: `monitor`, `handle` tipado, `guard`, `retry` |
| 08 | 12 | pipelines: `sift`/`morph`/`distill`, composição, streams |
| 09 | 12 | módulos: import local, Math, Analytics, IO, SQLite |
| 10 | 10 | avançado: async, threads, árvore binária, interpretador RPN |

---

## Desenvolvimento

```bash
pip install -e ".[dev]"

python3 -m pytest tests/ -q       # 77 testes
python3 exercicios/run_all.py     # 120 exercícios
```

Contexto para trabalhar no interpretador: [`CLAUDE.md`](CLAUDE.md).

### Arquitetura

```
arquivo.df → tokenize() → parse() → Interpreter().run(ast)
             lexer.py     parser.py   interpreter.py
```

| Arquivo | Responsabilidade |
|---------|------------------|
| `dataforge/tokens.py` | TokenType e as 78 palavras reservadas |
| `dataforge/lexer.py` | texto → tokens, com INDENT/DEDENT |
| `dataforge/parser.py` | recursivo descendente: tokens → AST |
| `dataforge/ast_nodes.py` | nós da AST como dataclasses |
| `dataforge/interpreter.py` | interpretador de árvore: a semântica |
| `dataforge/environment.py` | cadeia de escopos |
| `dataforge/builtins.py` | 225 funções globais |
| `dataforge/stdlib/` | os 13 módulos `Arcane.*` |

---

## Estado do projeto

| Verificação | Resultado |
|-------------|-----------|
| Testes unitários | 77 passando |
| Exercícios | 120/120 |
| Exemplos | 42/42 |
| Templates de projeto | 8/8 arquivos válidos |
| Módulos da stdlib | 30/30 carregam |
| Instalação via pip | funciona |

O que ainda falta — análise estática, rastreamento de pilha, sistema de módulos
com escopo real, gerenciador de pacotes — está detalhado em
[`doc/ANALISE_E_ROADMAP.md`](doc/ANALISE_E_ROADMAP.md).

---

## Licença

MIT — veja [LICENSE](LICENSE).
