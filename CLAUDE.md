# CLAUDE.md — DataForge

Contexto operacional para o Claude Code trabalhar neste repositório. Leia antes
de editar qualquer coisa.

---

## O que é este projeto

**DataForge** é uma linguagem de programação interpretada, de propósito geral,
implementada em Python 3.10+ **sem dependências externas no runtime**. Não é um
DSL nem um transpilador: tem lexer, parser recursivo descendente, AST tipada,
analisador estático e interpretador de árvore próprios.

- Versão atual: **1.0.0**
- Extensão dos arquivos: `.df`
- Entrypoints: `dataforge` e `df` (mesmo `main`)
- Licença: MIT

### Verificação rápida — rode antes e depois de mexer

```bash
python3 -m pytest tests/ -q                          # 600 testes
python3 exercicios/run_all.py                        # 216 exercícios
python3 tools/verificar_docs.py                      # os códigos do site compilam
for f in examples/*.df; do python3 -m dataforge run "$f" >/dev/null || echo "FALHOU $f"; done
```

**Cuidado com instalação velha no PATH.** Há três lugares onde o
DataForge pode estar instalado (`.venv/`, `~/.dataforge/`, o Python do
sistema), e uma cópia antiga produz erros que não existem no repositório
— foi assim que um `LexError: Unexpected character: '$'` apareceu num
arquivo que usava interpolação normalmente. O `.venv` deve estar em modo
editável (`pip install -e .`), que aponta para o repo e nunca envelhece.

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
  stdlib/                29 módulos (1016 símbolos), incluindo:
    catalogo.py          o nome, o apelido e o "para quê" de cada módulo
    kiln.py              Kiln — o framework web (46 símbolos)
    arcane_excel.py      planilhas .xlsx, sem dependência externa (29)
    arcane_arquivo_seguro.py  cofre de arquivo + zip/tar seguro (56)
    cifra.py             ChaCha20-Poly1305 puro (RFC 8439)

doc/               INSTALACAO, TUTORIAL, REFERENCIA, BIBLIOTECA_PADRAO,
                   KILN, ANALISE_E_ROADMAP (todos em pt-BR)
examples/          42 programas de demonstração
exercicios/        216 exercícios em 26 módulos + run_all.py
                   (os módulos 11-23 têm um .md explicativo por exercício)
projetos/          4 programas completos com forge.toml e testes
tools/             gerar_doc_stdlib, gerar_gramatica, gerar_ref_kiln
tests/             test_dataforge.py (legado), test_regressoes.py, test_dataforge4.py
tools/             gerar_doc_stdlib.py
editor/vscode/     extensão do VS Code — gramática **gerada** de tokens.py,
                   snippets, ícone. Instalada por 'dataforge editor'.
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
    variável perdem atualizações. Use `channel`. Isso vale para o Kiln, que
    atende **um pedido por thread**.

15. **Dentro de `$"{…}"`, aspas normais.** `$"item {v["id"]}"` funciona;
    `$"item {v[\"id\"]}"` não — o lexer copia strings aninhadas verbatim, e o
    escape quebra a leitura. A mensagem ("Unterminated interpolation") não
    aponta para a causa.

16. **`query["x"]` sem `??` dá 500 numa rota.** A query, o corpo e os
    cabeçalhos vêm de fora: a chave pode não vir, e indexar um vault sem a
    chave é erro. `params` é a exceção — se a rota casou, o parâmetro existe.

17. **O valor inicial do `distill` vem depois do corpo.**
    `>> distill a, v: a + v 0 / len(x)` divide o **zero**, não a soma. O
    resultado fica errado sem nada denunciar.

18. **`trigger` levanta `TriggerError`, não `RuntimeError`.**
    `handle RuntimeError` não pega um `trigger`. Para pegar qualquer
    coisa, `handle Error`.

19. **Campo declarado com padrão mutável é copiado no `spawn`.**
    `itens: Cluster := []` dá uma lista nova por instância — o literal é
    avaliado uma vez, na declaração, e sem a cópia todas compartilhariam
    a mesma. Padrões imutáveis (número, texto) não são copiados.

20. **`<T>` não é verificado em execução.** O parâmetro de tipo é aceito
    pelo analisador e documenta a relação entre entrada e saída, mas a
    linguagem é dinâmica: `action eco<T>(x: T) -> T` aceita qualquer
    valor. Um tipo **concreto** continua sendo cobrado.

21. **Um decorador que devolve `void` não substitui o alvo.** É o que
    permite `@Rota("/x")` só anotar. Se ele devolvesse `void` e isso
    virasse o novo valor, a ação decorada sumiria.

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

### Otimizar: meça antes

Três gargalos já foram medidos e resolvidos (`cProfile`, não intuição):
despacho por string (virou tabela por classe), alocação de escopo por
volta de laço (reaproveitado quando o corpo não captura) e construção
de AST em tempo de execução (`x += 1` montava dois nós por volta).

A carga de referência está em `tests/test_desempenho.py`; use
`dataforge profile` num programa real antes de mexer em qualquer coisa.

**O reaproveitamento de escopo é a otimização mais perigosa do
interpretador.** Se o corpo do laço captura o escopo — uma ação, um
`lambda`, um `blueprint`, um `thread`, um `defer` — cada volta precisa
do seu, senão todas as closures veem o último valor.
`_corpo_captura_escopo` varre a árvore inteira, e não só as instruções:
um `lambda` vive dentro de uma expressão.

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

Ao criar um módulo novo, registre-o em `stdlib/__init__.py` **e** descreva-o no
`DESCRICOES` de `stdlib/catalogo.py` — daí saem a doc em Markdown, os dados do
site e a tabela de `/docs/biblioteca`. A tabela já esteve escrita em três lugares,
e os três divergiram.

Os apelidos (`Zip`, `Cor`, `Banco`) são traduzidos para o nome oficial por
`_CANONICO` antes do carimbo de `__name__`: o mesmo módulo precisa se chamar
`Arcane.Archive` venha por `Zip`, por `Archive` ou pelo nome inteiro.

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
| `dataforge editor` | `cli.py` | instala a coloração no VS Code e derivados |
| `dataforge new` | `modelos.py` + `scaffold.py` | 8 modelos; todo projeto criado passa nos próprios testes |
| `dataforge stats` | `cli.py` | inventário: ações, blueprints, o arquivo e a ação mais longos |
| `dataforge profile` | `cli.py` | tempo **próprio** por ação (o acumulado somaria mais de 100%) |
| `dataforge fix` | `cli.py` | formata e aponta o que exige julgamento |
| `dataforge add/remove` | `packages.py` | instala e desinstala dependências |
| `dataforge install` | `packages.py` | resolve o `forge.toml` inteiro |
| `dataforge search` | `packages.py` | procura no registro |
| `dataforge pack/publish` | `packages.py` | empacota e publica |

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

## O gerenciador de pacotes

`dataforge add` resolve, baixa e instala; `adopt` encontra o resultado. As
três peças:

| Onde | O quê |
|------|-------|
| `dataforge/packages.py` | `Versao`, `Requisito` (semver `^` `~` `>=`), `Registro`, `Dependencia`, `Lock`, `resolver()`, `instalar_pacote()`, `empacotar()` |
| `dataforge/cli.py` | `add_command`, `remove_command`, `install_command`, `list_command`, `search_command`, `pack_command`, `publish_command` |
| `dataforge/interpreter.py` | `_procurar_em_pacotes()` — o `adopt` olha `forge_modules/`, subindo até achar um `forge.toml` |

Layout de um projeto com dependências:

```
forge.toml          o que você pediu      (versionado)
forge.lock          o que foi instalado   (versionado)
forge_modules/      os pacotes            (NÃO versionado)
~/.dataforge/cache/ tarballs, entre projetos
```

**O registro é estático**: uma pasta com `index.json` e `pacotes/*.tar.gz`,
servida por qualquer host. Não há servidor a manter. O do projeto vive em
`site/public/registry/` e vai ao ar junto com o site.

Três decisões que valem lembrar:

1. **Conflito de versão é erro, não aviso.** Se dois pacotes pedem faixas
   incompatíveis do mesmo terceiro, `resolver()` falha dizendo quem pediu o
   quê. Instalar duas cópias em versões diferentes gera bug irreproduzível.
2. **O tarball é reprodutível** — `mtime=0`, uid/gid zerados. Sem isso o
   sha256 mudaria a cada empacotamento e a verificação de integridade não
   significaria nada.
3. **A extração recusa `../` e links simbólicos.** Um pacote não pode
   escrever fora da sua pasta.

### Os pacotes deste repositório

`packages/` tem quatro bibliotecas escritas em DataForge, publicadas no
registro do site: `validador` (CPF/CNPJ/e-mail e esquema de formulário),
`tabela` (saída para terminal), `datas` (datas em pt-BR com feriados) e
`cofre` (configuração em camadas). Somam 46 testes.

Elas servem de referência para quem for escrever um pacote — e de prova de
que o gerenciador funciona ponta a ponta.

```bash
cd packages/validador && dataforge pack
dataforge publish --registry=../../site/public/registry
```

## Kiln — o framework web

`dataforge/stdlib/kiln.py` é o runtime; as dez palavras da linguagem
(`server`, `route`, `respond`, `render`, `redirect`, `middleware`, `mount`,
`assets`, `views`, `ignite`) atravessam os cinco lugares de sempre e estão em
`CONTEXTUAIS_KILN`, não em `KEYWORDS`.

**Elas são contextuais pelo mesmo motivo de `get`/`set`/`final`**: `route`,
`render` e `server` são nomes bons demais para tirar de quem escreve. O parser
as reconhece pelo texto, e só onde fazem sentido — `_em_server` e `_em_rota`
controlam isso. `server` só abre bloco quando o que vem depois confirma
(`_abre_server`): um nome seguido de `:`, de `on` ou de `at`.

Três decisões que valem lembrar:

1. **`server` monta, `ignite` sobe.** Sem essa separação, um teste que
   importasse o módulo subiria o servidor e nunca terminaria. É por isso que
   `projetos/loja-web` tem `app.df` e `main.df` separados.
2. **`respond` e `render` levantam `YieldSignal`.** Encerram a rota como
   `yield` encerra uma ação — e o `typechecker` marca isso devolvendo `True`,
   senão o analisador acusaria "código inalcançável" logo abaixo.
3. **`Kiln.test` executa a rota sem socket.** É o que torna teste de rota
   barato. Mas ele roda tudo na mesma thread: bug de concorrência (como o do
   SQLite) **só aparece subindo o servidor de verdade**.

O `parse_render` precisa de `_no_with`: sem essa guarda,
`render "x" with {…}` seria lido como a expressão `record with {…}` e o
template comeria os dados.

## O que é gerado — não edite à mão

| Arquivo | Gerador | Guardado por |
|---------|---------|--------------|
| `editor/vscode/syntaxes/dataforge.tmLanguage.json` | `tools/gerar_gramatica.py` | `tests/test_editor.py` |
| `site/app/docs/kiln/referencia/page.tsx` | `tools/gerar_ref_kiln.py` | — |
| `doc/BIBLIOTECA_PADRAO.md` | `tools/gerar_doc_stdlib.py` | — |
| `site/lib/dados-gerados.json` | `site/scripts/gerar_dados.py` | — |
| `site/public/dist/*.tar.gz` | `scripts/gerar_tarball.py` | `tests/test_regressoes.py` |
| `site/lib/marca.ts`, favicon, ícones | `tools/vetorizar_logo.py` | `tests/test_api_e_marca.py` |
| `site/public/api/*.json` | `scripts/gerar_api.py` | `tests/test_api_e_marca.py` |
| `dataforge/marca.py` (arte ASCII) | `tools/vetorizar_logo.py` | — |

A gramática do editor tem **duas** travas: o gerador recusa rodar se uma
palavra de `KEYWORDS` não estiver em nenhum grupo de cor, e um teste falha se o
arquivo versionado divergir do que o gerador produz. A versão anterior era
escrita à mão e por isso não conhecia `record` nem `enum` — exatamente o
problema que isso resolve.

O mesmo vale para `site/lib/highlight.ts`: há teste comparando com `tokens.py`.

## Instaladores

| Arquivo | Para |
|---------|------|
| `scripts/instalar.sh` | macOS e Linux, POSIX sh (roda em dash e busybox) |
| `scripts/instalar.ps1` | Windows, PowerShell |
| `Dockerfile` | imagem multi-estágio, usuário sem privilégio |

Ambos criam uma venv em `~/.dataforge` — não tocam no Python do sistema e
não pedem sudo. A origem do download é o site (`/dist/dataforge-X.tar.gz`),
com o GitHub apenas como alternativa.

Ao mudar a versão, regenere o tarball que o site serve:

```bash
python3 scripts/gerar_tarball.py
```

## Testes

| Arquivo | Como roda | Cobre |
|---------|-----------|-------|
| `tests/test_dataforge4.py` | `pytest` | recursos 4.0: interpolação, ternário, records, enums, padrões, generators, stack traces, checker, stdlib nova, ferramentas |
| `tests/test_regressoes.py` | `pytest` | bugs já corrigidos + sincronia da doc |
| `tests/test_dataforge.py` | `pytest` **e** script | 69 verificações da suíte original |
| `tests/test_kiln.py` | `pytest` | o framework web: rotas, respostas, templates, segurança, a sintaxe da linguagem e as palavras que continuam livres |
| `tests/test_excel.py` | `pytest` | `.xlsx`: o arquivo gerado é um ZIP válido, os tipos sobrevivem à ida e volta, `describe(frame)` |
| `tests/test_editor.py` | `pytest` | a gramática do VS Code está em dia com `tokens.py`; os snippets são DataForge válido |
| `exercicios/run_all.py` | script | 216 exercícios, cada um com `assert` |
| `projetos/*/tests/` | `dataforge test` | 61 testes nos 4 projetos completos |
| `examples/*.df` | manual | 42 programas maiores |

**Ao corrigir um bug, escreva primeiro o teste que falha.** Todos os bugs
corrigidos no 3.1 e no 4.0 têm teste correspondente.

`tests/test_dataforge.py` roda nas duas formas — o `sys.exit` só dispara sob
`__main__`. Não renomeie `verificar()` para `test()`: o pytest tentaria coletá-la.

---

## Estado conhecido e limitações

O que **funciona e está testado**: tudo do 3.1 mais gerenciador de pacotes
(`add`, `install`, `remove`, `list`, `search`, `pack`, `publish`, com semver,
lockfile e verificação de integridade), tipos verificados, análise
estática com sugestões, stack traces, interpolação, ternário, `??`, `?.`, `in`,
spread/rest, desestruturação, compreensões, records imutáveis com `with`, enums
com valores, pattern matching estrutural completo, generators preguiçosos
(inclusive infinitos), imports seletivos, `relay` real, detecção de ciclos,
`forge.toml`, e as seis ferramentas de linha de comando.

O que **ainda não existe** (não invente que existe):

- **Generics com restrição** — `<T>` existe e o analisador o aceita,
  mas não há `<T extends Comparable>`: o parâmetro de tipo documenta a
  relação entre entrada e saída, e não é verificado em execução.
- **Exaustividade** — o `match` não avisa se um membro de enum ficou fora.
- **Contrato de trait** — não se verifica se o blueprint implementou tudo.
- **LSP e debugger** — a gramática TextMate só colore. `dataforge editor` a
  instala automaticamente (o instalador já faz isso), mas não há autocompletar
  sensível a contexto nem erro sublinhado enquanto se digita.
- **Bytecode** — é interpretador de árvore, sem otimização.
- **Sincronização entre threads** — sem mutex/semáforo; use `channel`. O Kiln
  atende um pedido por thread: o `Arcane.Database` serializa o acesso à
  conexão (sem isso, a primeira consulta de qualquer servidor estoura), mas
  estado em memória compartilhado entre rotas não é protegido.
- **WebSocket, HTTP/2 e streaming de resposta** — o Kiln não tem. Ele roda
  sobre o `http.server` do Python; em produção pública, ponha um nginx ou
  Caddy na frente.
- **Cálculo de fórmula em planilha** — o `Arcane.Excel` grava a fórmula e o
  Excel a resolve ao abrir. Também não lê o `.xls` binário antigo.
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
