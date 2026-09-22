# CLAUDE.md — DataForge

Contexto operacional para o Claude Code trabalhar neste repositório. Leia antes
de editar qualquer coisa.

---

## O que é este projeto

**DataForge** é uma linguagem de programação interpretada, de propósito geral,
implementada em Python 3.10+ **sem dependências externas no runtime**. Não é um
DSL nem um transpilador: tem lexer, parser recursivo descendente, AST tipada,
analisador estático e interpretador de árvore próprios.

- Versão atual: **1.1.1**
- Extensão dos arquivos: `.df`
- Entrypoints: `dataforge` e `df` (mesmo `main`)
- Licença: MIT

### Verificação rápida — rode antes e depois de mexer

```bash
python3 -m pytest tests/ -q                          # mais de 2700 testes
python3 exercicios/run_all.py                        # 387 exercícios
python3 trilha/run_all.py                            # 18 capítulos da trilha
python3 tools/verificar_docs.py                      # os códigos do site compilam
for f in examples/*.df; do python3 -m dataforge run "$f" >/dev/null || echo "FALHOU $f"; done
for d in examples exercicios projetos packages trilha; do dataforge check "$d"; done
```

O portão completo é `bash scripts/verificar_tudo.sh`: ele roda o acima,
**regera tudo e confere o diff**, compila o site e a extensão, e pede cada
arquivo do release para ver se ele baixa de verdade.

Duas destas linhas faltavam nesta lista e o buraco era real: a `trilha/`
tem 18 capítulos com `assert` e um `run_all.py` próprio, e o `check` sobre
`projetos/` já deixou passar um traceback do analisador por meses — ver
"Um analisador que morre com traceback do Python", abaixo.

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
  compilador.py    330   a árvore vira fechamentos, uma vez (1,5× a 1,8×)
  ponte.py         290   'adopt Python.numpy' — a ponte para o Python
  cauda.py         170   'yield f(…)' vira salto, e a recursão deixa de ter teto
  travessia.py     964   o que uma ação leva consigo para outro núcleo
  typechecker.py  1752   análise estática: nomes, aridade, tipos, alcance
  resolucao.py     190   onde mora o módulo de um 'adopt' — a única cópia
  cache.py         200   a árvore guardada entre execuções — 93% do parse
  versoes.py       340   versões lado a lado, o pino do projeto, o workspace
  hir.py           430   a arvore depois do acucar, e de onde vem cada nome
  mir.py           900   o grafo de fluxo, e as cinco analises sobre ele
  lir.py           170   o que o compilador de fechamentos compilou
  ssa.py           520   uma definicao por nome, no phi, propagacao condicional
  otimizar.py      300   tres passes sobre o HIR — medidos, e por isso desligados
  tipos_nomeados.py 340  'type': alias, uniao, intersecao, refinamento, opaco
  idioma.py        330   o idioma das mensagens — pt-BR, e 'DF_IDIOMA=en'
  docs_links.py    220   onde mora a doc de cada palavra, módulo e comando
  objetos.py       330   OOP fora do caminho quente: sobrecarga, vigias, estado por objeto
  oop_analise.py   560   dataforge oop — métricas CK e cheiros de SOLID
  lsp.py          1100   o servidor de linguagem: hover, completar, ir-para
  exemplos_palavras.py   um exemplo que RODA para cada uma das 100 palavras
  superficie.py    300   o que um .df oferece, sem executá-lo
  formatter.py     280   dataforge fmt
  linter.py        394   dataforge lint
  testrunner.py    380   dataforge test, com cobertura de linha
  cobertura.py     170   quais linhas os testes executaram
  depurador.py     390   'dataforge debug' — para, mostra e anda
  dap.py           700   o mesmo, falando o protocolo do editor
  docgen.py        218   dataforge doc
  project.py       184   forge.toml
  environment.py    91   cadeia de escopos
  errors.py        167   hierarquia de erros, sinais de controle, stack traces
  builtins.py     1224   225 funções globais, sem import
  repl.py          409   console interativo
  cli.py          1055   CLI + templates de projeto
  stdlib/                79 módulos (2156 símbolos), incluindo:
    catalogo.py          o nome, o apelido e o "para quê" de cada módulo
    kiln.py              Kiln — o framework web (73 símbolos)
    kiln_tempo_real.py   upload multipart, SSE e WebSocket (RFC 6455)
    vitrine/             Vitrine — dashboards e data apps (213 símbolos)
    arcane_dominio.py    DDD: valor, entidade, agregado, evento, regra,
                         repositório, unidade de trabalho, contexto
    arcane_reativo.py    sinal, derivado, efeito, observável — e a onda
                         de duas fases que mata o glitch do losango
    arcane_estrutura.py  layout binário com NOME, janela sem cópia, ponteiro
    arcane_regex_extra.py  grupos nomeados, fullmatch, troca que calcula,
                         explicação em pt-BR e a leitura de risco
    arcane_reflexo.py    reflexão que respeita a visibilidade, diagrama Mermaid
    arcane_objetos.py    cópia, congelar, serialização que só aceita tipos listados
    arcane_injecao.py    contêiner: único, transitório, por escopo; ciclo e cativo
    arcane_padroes.py    os padrões que pedem mecanismo (comandos, máquina, pool…)
    arcane_memoria.py    referência fraca, mapa fraco, coletor
    arcane_c.py          FFI: biblioteca nativa, ponteiro cru, struct, callback
    arcane_laco.py       laco de eventos, escalonador e fibras — UMA thread
    arcane_perfil.py     percentis, significancia (Mann-Whitney), flame graph
    arcane_inicio.py     as fases da partida, TLS com finalizador, a pilha
    arcane_capacidade.py a fronteira de autoridade — e o que ela NAO e
    arcane_abi.py        a superficie e o contrato: o que quebra, e que bump exige
    arcane_alvo.py       onde este programa roda, lido dos 'adopt'
    arcane_ecossistema.py o inventario da implementacao, CONFERIDO contra ela
    arcane_principios.py  os dez principios com prova que roda, e as 9 tensoes
    arcane_percurso.py    as fases de um arquivo, medidas — e a que NAO roda
    arcane_macro.py      a arvore como dado: citar, transformar, gerar, derivar
    arcane_dsl.py        combinadores para uma linguagem externa propria
    arcane_stm.py        memoria transacional: escritas que acontecem juntas
    arcane_posse.py      posse exclusiva, emprestimo com escopo, contagem
                         deterministica e referencia fraca
    arcane_resultado.py  a falha como VALOR ('ok'/'falha'), e 'Talvez' para
                         onde 'void' é ambíguo
    arcane_tipos.py      reflexão de tipos: metadados de um 'type', 'satisfaz'
                         sem levantar, a forma estrutural de um valor
    arcane_eventos.py    emissor, contexto por thread, fila em memória e
                         fila_persistente (SQLite: reserva com prazo, recuo,
                         agendamento, carta morta)
    arcane_excel.py      planilhas .xlsx, sem dependência externa (29)
    arcane_arquivo_seguro.py  cofre de arquivo + zip/tar seguro (56)
    arcane_seguranca.py  escape por destino, TOTP, token com prazo,
                         varredura de segredo, SSRF, auditoria encadeada
    cifra.py             ChaCha20-Poly1305 puro (RFC 8439)

doc/               INSTALACAO, TUTORIAL, REFERENCIA, BIBLIOTECA_PADRAO,
                   KILN, ANALISE_E_ROADMAP (todos em pt-BR)
examples/          44 programas de demonstração
exercicios/        387 exercícios em 57 módulos + run_all.py
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
| chamar biblioteca Python | `adopt Python.numpy as np` |
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
| tupla | `(1, "a")` · tipo `Tuple<Integer, String>` |
| alias / união / refinamento | `type Id := Integer` · `A \| B` · `where valor bigger 0` |
| `newtype` / tipo opaco | `opaque type Cpf := String where …` |
| `//` (div. inteira) | **`~/`** |
| `Decimal` exato | `adopt Arcane.Decimal as Dec` · `Dec.de("0.1")` |

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
   **`defer` roda na saída da AÇÃO, onde quer que esteja escrito** — dentro
   de um `cycle`, de um `persist`, no topo do programa (no fim dele), ou numa
   `thread`/tarefa de `parallel` (ao fim daquele trabalho). Ele se registrava
   no escopo em que aparece, e só o da ação era consultado: um `defer` num
   laço **nunca rodava**, calado, e fechar arquivo por volta é o uso mais
   óbvio que existe.
   **Nem `defer` engole:** um erro dentro dele viaja. Se a ação já estava
   falhando, viaja o erro **original** e o do `defer` vai em `e.outros` —
   é o modelo do try-with-resources. Até a correção era descartado nos dois
   casos, e isso estava escrito na trilha como decisão; foi revertido porque
   um arquivo não fechado terminava o programa com código 0.

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
    (`point n`) no topo torna tudo abaixo inalcançável — e agora o
    `check` acusa isso (`point-inalcancavel`). Com **guarda** é
    legítimo: `point n when n bigger 100:` deixa passar o que não
    satisfaz a condição.

11. **String simples não cruza linhas.** Para SQL multilinha, use `"""..."""`.

12. **`cycle from … to` é inclusivo** nos dois extremos.

13. **Generator infinito + `to_cluster()` trava.** Use `take(n)` ou garanta um
    `halt`.

14. **A linguagem não sincroniza sozinha.** Duas threads escrevendo na
    mesma variável perdem atualizações — **medido: 40.425 de 80.000**,
    em silêncio. `Arcane.Concurrent` tem `mutex`, `semaforo`, `contador`
    e canal bloqueante, mas usá-los é escolha de quem escreve. Vale para
    o Kiln, que atende **um pedido por thread**.
    O `check` agora **avisa** (`escrita-concorrente`) quando um `thread`,
    `parallel` **ou `route`** escreve num nome que vem de fora —
    inclusive na forma `v["n"] := …`, que é a que mais engana. Era o
    único bug caro que nem o `check` nem o `lint` mencionavam.
    **A rota é o caso que mais importa**: o Kiln usa
    `ThreadingHTTPServer`, cada pedido roda numa thread, e ali a
    concorrência é **invisível** — quem escreve a rota não vê thread
    nenhuma. Medido: seis pedidos simultâneos numa rota que lê, espera e
    escreve entregaram **1 de 6**.
    A lista de métodos que disparam o aviso foi **medida, não
    presumida**: `append` de quatro threads, 5 mil vezes cada, entregou
    20.000 de 20.000 — o GIL protege a operação inteira, e avisar sobre
    ele seria falso alarme em código que funciona. O que perde é
    ler-modificar-escrever (`v["n"] := v["n"] + 1` deu 33.740 de 40.000)
    e o que **lê para decidir o que escrever** (`remove`, `pop`,
    `insert`, `sort`). Um módulo não é coleção: `Xls.set(aba, …)` casava
    com `set` e deu o único falso alarme do repositório.
    A análise **para na fronteira da ação**: seguir chamada exigiria um
    grafo, e um aviso que depende disso seria impreciso nos dois
    sentidos. É aviso, e não erro: um acumulador protegido por mutex
    passa por aqui igual, e recusá-lo proibiria o uso correto.

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

20. **`<T>` solto não é verificado; `<T extends X>` é.** O parâmetro de
    tipo sem limite documenta a relação entre entrada e saída, e
    `action eco<T>(x: T) -> T` aceita qualquer valor. Com limite, ele é
    cobrado nas duas metades: o `check` confere o argumento na chamada
    (`generic-bound`), e a execução confere o valor. Dentro do corpo, um
    `T extends Number` **é** um `Number` para o analisador — é o que deixa
    escrever `a bigger b`. O limite pode ser tipo embutido, blueprint,
    trait ou record, e atravessa `adopt`.

21. **Um decorador que devolve `void` não substitui o alvo.** É o que
    permite `@Rota("/x")` só anotar. Se ele devolvesse `void` e isso
    virasse o novo valor, a ação decorada sumiria.

22. **Um pipeline dentro de `lambda` precisa de parênteses.** O corpo
    do lambda liga mais forte que `>>`, então
    `lambda => xs >> morph x: x * 2` canaliza o **lambda**, não `xs`.
    A forma certa é `lambda => (xs >> morph x: x * 2)`. A mensagem
    antiga (`'DFAction' object is not iterable`) falava de uma classe
    do Python; hoje ela mostra a linha com os parênteses.

23. **O teto de quadros é mil, e recursão legítima o atinge.** Uma
    travessia de árvore de cinco mil nós não tem nada de infinita. As
    duas saídas: `yield f(…)` como retorno **inteiro** vira salto e
    não tem teto (testado com 200 mil), ou um `cycle` com pilha
    explícita. A mensagem do erro traz as duas.

24. **`given` compartilha o escopo; `cycle` não.** Um nome atribuído
    num ramo de `given`/`orif`/`otherwise` existe depois do bloco — é
    como se decide um valor em dois caminhos, e o `monitor` sempre
    funcionou assim. O corpo de um `cycle` tem escopo próprio, e isso é
    **de propósito**: é o que dá a cada volta o seu `i`, e faz um
    `lambda` criado no corpo lembrar o valor da volta em que nasceu.
    Sem isso as três closures de um laço de três voltas veriam todas o
    último valor — o clássico que o Python tem e que aqui não acontece.

25. **`remove` e `pop` mudam de sentido conforme a coleção.** Num
    `Cluster` o segundo argumento é o **valor**; num `Vault`, a
    **chave**. `remove` apaga **no lugar** e é silencioso quando não
    acha; `pop` devolve o valor e por isso **levanta** — devolver `void`
    calado esconderia a diferença entre "a chave valia `void`" e "a
    chave não estava lá". `omit` devolve **cópia** e não mexe no
    original.

26. **Uma declaração que se contradiz agora é recusada na leitura.**
    Quatro formas passavam limpas e não tinham leitura possível:
    `action f(a, a)` (o primeiro `a` era inalcançável, e `f(1, 2)` dava
    2), `action f(a := 1, b)` (o padrão nunca podia ser usado), dois
    métodos com o mesmo nome num blueprint, e um método com o nome de um
    campo do cabeçalho — nesse último o **campo vence**, e o método
    existe no arquivo sem nunca rodar. Duas declarações de topo com o
    mesmo nome no mesmo arquivo viraram **aviso** (`declaracao-repetida`):
    o Python aceita calado, mas a primeira não tem como ser alcançada.

27. **`spawn` leva o nome e os argumentos, e para ali.** Ele chamava
    `parse_postfix`, então `spawn B().f()` era `spawn (B().f())` e a
    mensagem culpava a ação (`'<action f>' is not a blueprint`). Hoje o
    `spawn` devolve a instância de dentro de `parse_primary`, e o
    pós-fixo de quem chamou aplica `.f()` sobre ela. `_alvo_de_spawn`
    devolve `None` quando o que vem depois não é um nome, e aí o caminho
    antigo assume — nada que funcionava deixou de funcionar.

28. **`promises` sai do corpo.** O parser tira todo `promises` do topo
    da ação e o guarda em `postconditions`: ele roda na SAÍDA, com
    `outcome` e com `before(expr)` avaliado na entrada. Um `promises`
    dentro de um `given` não tem saída única e é recusado.

29. **A invariante só é cobrada quando a chamada mais de fora termina.**
    `estado.profundidade` conta as chamadas abertas no objeto; conferir
    invariante e promessa também soma 1 — sem isso, `invariant
    self.area() bigger_eq 0` chamava `area`, que conferia a invariante,
    que chamava `area`. Método `private` não dispara a conferência.

30. **`Objetos.de_vault` exige a lista de tipos**, e não roda `setup`.
    O dado nunca escolhe o blueprint; as invariantes são conferidas na
    chegada.

31. **Treze palavras de OOP são contextuais**, e nenhuma é reservada:
    `readonly := 3` é variável. Cada uma só vale onde o que vem depois
    confirma (`_e_modificador`, `_abre_condicao`,
    `_modificadores_antes_de_blueprint`).

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
- **Nenhuma mensagem cita tipo do Python.** `int`, `str`, `list`, `dict` e
  `NoneType` não existem nesta linguagem, e uma mensagem nesses termos manda
  a pessoa procurar na documentação errada — ela não tem como saber que
  `list` é `Cluster`. Para nomear um tipo, `self._nome_do_tipo(valor)`; para
  limpar um texto que veio do Python, `_traduzir_tipos`. Há teste sobre o
  **código** de `interpreter.py` proibindo `type(x).__name__` dentro de
  f-string de mensagem — foi assim que cinco delas chegaram lá, e a trava
  achou outras três que eu não tinha visto.
  A tradução troca só o nome **entre aspas**, que é como o CPython o escreve:
  trocar a palavra solta estragaria um texto legítimo, como uma mensagem
  sobre um arquivo chamado `list`.

### O compilador de fechamentos

`compilador.py` percorre a árvore **uma vez** e devolve, para cada nó, um
fechamento que faz o que aquele nó faz. Executar passa a ser chamar
fechamentos: sem tabela de despacho, sem `isinstance`, sem `node.campo`.

Três regras ao mexer nele:

1. **Cada construtor espelha um `eval_`/`exec_`, e delega aos mesmos
   auxiliares.** A semântica não é reimplementada — `_operar`, `_comparar`,
   `_chamar_metodo`, `_ler_membro` e `_escrever_membro` são os mesmos. Quando
   um `eval_X` avalia as partes e depois decide, extraia a decisão para um
   auxiliar que receba os valores prontos, como foi feito nos cinco acima.

2. **O que não estiver nas tabelas recua** para `interp.evaluate`/`execute`,
   que é o comportamento de hoje byte por byte. Um recurso novo na linguagem
   continua funcionando sem tocar aqui; só não fica mais rápido. Devolver
   `None` de um construtor também recua — é como os casos difíceis
   (`f(...xs)`, `v["k"] += 1`) ficam de fora sem duplicar regra.

3. **O depurador desliga tudo** (`interp.compilar_corpos = False`). Ele para
   em cada linha sombreando `execute`, e o corpo compilado passa por fora —
   um depurador que enxerga metade das instruções é pior que um interpretador
   mais lento.

`tests/test_desempenho.py` roda uma amostra dos exercícios com a compilação
ligada e desligada e compara a saída caractere por caractere. É esse teste que
pega um fechamento que divergiu do método que ele espelha.

### Comparar dois tempos medidos exige margem

`assert a_ms bigger b_ms` é um sorteio quando os dois lados são
microssegundos. O exercício 215 comparava uma busca O(n) num cluster de
**3 mil** itens com uma O(1) num vault, e a razão era ~2x — uma volta em
cinco dava 1,3x. Reprovou a CI num macOS carregado.

**A causa não era a medição**: o `in` de um cluster é um laço em C,
rápido o bastante para o custo de despacho do interpretador dominar os
dois lados e mascarar a diferença assintótica. Medido: 2,7x com 3 mil,
9x com 20 mil, **43x com 100 mil**, 127x com 300 mil.

A correção é medir onde a diferença aparece e cobrar um **fator**:
`razao bigger 5` é verdadeiro com folga e falha alto se a busca no vault
virar O(n) por acidente. `bigger` sozinho passa por acidente.

`test_nenhum_exercicio_compara_dois_tempos_sem_margem` proíbe o padrão
voltar, e há uma trava irmã para os testes de paralelismo
(`test_nenhum_teste_de_paralelismo_usa_limite_absoluto`): um limite fixo
mede a **máquina**, não o paralelismo.

**E a razão não basta, se o trabalho for pequeno.**
`test_map_roda_junto_e_nao_em_serie` comparava razão — o padrão que a
trava recomenda — e falhou no Windows com **1,47**: o paralelo levou
0,44 s contra 0,30 s da série. O paralelismo estava certo; o que dominou
foi o **custo de criar cinco threads**, que no Windows passa de 60 ms de
trabalho. Subir a espera de 0,06 s para 0,25 s resolveu: a série vira
~1,25 s e o tempo de partida deixa de aparecer na conta.

### Otimizar: meça antes

Sete gargalos já foram medidos e resolvidos (`cProfile`, não intuição):
despacho por string (virou tabela por classe), alocação de escopo por
volta de laço (reaproveitado quando o corpo não captura), construção
de AST em tempo de execução (`x += 1` montava dois nós por volta), e
quatro na máquina de chamada e no acesso a membro:

| O que era | Medido |
|---|---|
| as tabelas de método de texto, vault e cluster eram **literais dentro de `_ler_membro_cru`**: 146 lambdas construídos a cada `xs.append(i)` ou `"a".upper()` | 200 mil `append`: **0,77 s → 0,33 s** |
| o pipeline não era compilado: escopo novo e `evaluate` pela árvore por elemento | com o resto, o mesmo laço em **0,27 s** |
| `_check_arity` rodava três compreensões em toda chamada, inclusive na posicional exata | `fib(24)`: 0,48 s → 0,42 s |
| `Environment` alocava **dois sets vazios** por escopo, e `f"<action {nome}>"` era montado por chamada | idem |

E uma armadilha achada medindo: `getattr(obj, "x", None)` num **slot
nunca atribuído** custa 7× mais que num atributo presente, porque levanta
e captura um `AttributeError` por dentro. Foi o que a primeira versão do
`if call_env._deferred` fez, e o ganho da otimização anterior foi embora
nisso. O slot passou a nascer com `None`.

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

**Vault de opções: use `opcoes.ler`.** Ler as chaves soltas com
`opcoes.get(nome, padrao)` engole erro de digitação — `{"tentativa": 9}`
deixava o cliente com as 3 tentativas do padrão, e o 9 não chegava a lugar
nenhum. Pior: `API.openapi(app, {"title": "Loja"})` — em inglês, como o
próprio OpenAPI escreve o campo — saía com o título padrão, e quem escreve
isso **publica um contrato com o nome errado** sem nada denunciar.

```python
from .opcoes import ler as _ler_opcoes

CONFIG = {"titulo": "API DataForge", "versao": "1.0.0"}
config = _ler_opcoes(config, CONFIG, "API.openapi")
```

A lista fica num lugar só, e ela também é a documentação. Recusar, e não
avisar: um aviso impresso não para nada, e o programa segue com o padrão —
exatamente o estado que se queria evitar. Chave começando com `_` passa.

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
| `dataforge test` | `testrunner.py` | descobre `*_test.df`, `tests/`; `--cobertura` e `--minimo=80` |
| `dataforge fmt` | `formatter.py` | formata (`--check` só verifica) |
| `dataforge lint` | `linter.py` | estilo e higiene |
| `dataforge doc` | `docgen.py` | Markdown a partir dos comentários |
| `dataforge init` | `project.py` | cria `forge.toml` e esqueleto |
| `dataforge info` | `project.py` | mostra o manifesto |
| `dataforge repl` | `repl.py` | console com `:type`, `:ast`, `:load` |
| `dataforge editor` | `cli.py` | instala a coloração no VS Code e derivados |
| `dataforge debug` | `depurador.py` | para, mostra o que vale e anda — serve por ssh |
| `dataforge dap` | `dap.py` | o mesmo no painel do editor (F5) |
| `dataforge new` | `modelos.py` + `scaffold.py` | 9 modelos; todo projeto criado passa nos próprios testes |
| `dataforge devops` | `devops_cli.py` | Dockerfile, compose, CI, k8s, Helm, nginx, SBOM, `doctor` |
| `dataforge vitrine` | `vitrine_cli.py` | `run`, `dev` (hot reload), `doctor`, `new`. Sem `build` nem `deploy` — e os dois explicam por quê |
| `dataforge stats` | `cli.py` | inventário: ações, blueprints, o arquivo e a ação mais longos |
| `dataforge oop` | `oop_analise.py` | WMC, DIT, NOC, CBO, RFC, LCOM, instabilidade, MI; cheiros com o princípio SOLID; `--diagrama`, `--hierarquia` |
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

### `dataforge test` roda os `trial`, e reprova quando um cai

Um arquivo com `crucible`/`trial` **registra** as suites e não as roda:
quem as roda é `Crucible.run()`. O corredor caía no caso "sem ações
`test_`, o próprio arquivo é o caso" e contava o arquivo como **um
teste que passou**.

Um teste que falha reportando "Tudo verde" é a pior falha possível num
corredor de testes: a suíte fica vermelha e o CI passa. Um arquivo com
dez `trial`, um deles quebrado, saía com **código 0** — e
`dataforge crucible`, sobre a mesma suíte, saía com 1. Os dois comandos
discordavam, e o nome mais óbvio era o que mentia.

Achado gerando um projeto de 281 arquivos: 30 arquivos com 2 `trial`
cada relatavam "30 passaram" onde eram 60.

Três detalhes da correção:

| O quê | Porque |
|---|---|
| um `Resultado` por **trial**, não por arquivo | "1 de 2 falhou" sem dizer qual não serve para nada |
| os nomes vêm de `crucible.Resultado` (`estado`, `caminho`, `motivo`) | adivinhar não daria erro: `getattr` com padrão devolvia `"pass"` para tudo, e um trial quebrado aparecia verde — foi o primeiro jeito que escrevi |
| o estado `skip` no corredor | `trial … pending` é quem escreveu dizendo "ainda não"; sem esse estado ele caía em "tudo que não passou falhou" |

### Cobertura de linha

`dataforge test --cobertura` diz quais linhas rodaram, e
`--minimo=80` reprova no CI. Os dois números têm um jeito próprio de
mentir, e o arquivo `cobertura.py` existe para que nenhum deles minta:

| Metade | De onde vem | Como mentiria |
|---|---|---|
| denominador | o parser: quais linhas são **executáveis** | contar comentário e linha vazia dá um número sempre pessimista |
| numerador | `execute` sombreado, como o depurador faz | com `compilar_corpos` ligado, o corpo das ações passa por fora e toda ação dá 0% |

**A definição de "instrução" é a existência de `exec_<Nó>` no
interpretador**, e não uma lista. A primeira versão era uma lista e
apodreceu antes de ser commitada: tinha `CycleLoop`, e o nó se chama
`CycleFromTo` — o laço inteiro ficava fora do denominador, e a cobertura
saía **otimista**, que é o pior defeito possível numa métrica.

A linha da declaração de `action` não conta; o corpo conta. Assim uma
ação nunca chamada aparece com **0%** e não 20%. E um arquivo que
nenhum teste toca aparece com 0% em vez de sumir do relatório — sumir é
o que faz uma cobertura de 95% conviver com metade do sistema sem teste.

`forge_modules/` ficou fora da descoberta: um projeto com 13 testes
relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca
que ninguém escreveu.

### Toda ação sabe em que arquivo nasceu

`DFAction.arquivo` é carimbado no **construtor**, e `_corpo_da_acao`
troca `self.filename` enquanto o corpo roda. Duas coisas dependiam
disso e as duas estavam erradas:

1. Um `1 / 0` na linha 5 de `lib.df` era reportado como `main.df:5`,
   **com o trecho do outro arquivo desenhado embaixo da seta**. Em
   projeto grande isso manda a pessoa depurar o arquivo errado.
2. A cobertura de um módulo importado era contada no arquivo de teste.

O carimbo é no `__init__` porque há **nove** lugares que criam uma
`DFAction` — método de blueprint, de record, propriedade, operador,
lambda, método mágico. Carimbar em cada um deixaria de fora os que
vierem depois, e a falta não dá erro: só faz o arquivo errado aparecer.

`Error.render` também passou a **ler do disco o arquivo que ela nomeia**
quando o que recebeu não é dele.

### O analisador atravessa arquivos

`P.naoExiste()` e `P.criar(1, 2, 3)` são acusados **antes de rodar**,
mesmo quando `P` vem de outro `.df`. É a checagem que mais importa em
sistema grande: num arquivo de 40 linhas o erro aparece na primeira
execução; num de 200 arquivos, a maioria das chamadas é entre módulos, e
todas elas eram invisíveis.

Três arquivos sustentam isso:

| Onde | O quê |
|---|---|
| `resolucao.py` | onde mora o módulo que um `adopt` pede — **a única cópia** |
| `superficie.py` | o que um `.df` oferece, lido com lexer e parser, **sem executar** |
| `typechecker.py` | `st_AdoptStatement` guarda a superfície; `ex_MemberAccess` e `_conferir_chamada_de_modulo` cobram |

**O tipo de retorno atravessa a fronteira.** `Membro.retorno` guarda o
`-> Tipo`, e `_conferir_chamada_de_modulo` o devolve em vez de `UNKNOWN`.
Sem isso o tipo se perdia no `adopt`: uma ação que declara `-> Pedido`
virava um valor sem tipo, e `P.criar(1, "Ana").clientte` — o campo
errado, com o nome quase certo — **passava no `check`**. No mesmo
arquivo esse campo é acusado com sugestão.

Num sistema de 200 arquivos a maioria das chamadas atravessa módulo, e
era justamente ali que a conferência calava.

O nome é traduzido para o vocabulário de quem chama (`-> Pedido` no
outro arquivo é `P.Pedido` aqui): devolver o nome nu faria o analisador
procurar um record que este arquivo não declara. Um tipo embutido
atravessa como está, e um tipo que o outro módulo **não exporta** volta
a calar.

**E os tipos dos parâmetros também.** `Membro.parametros` e
`Membro.tipos` levam o `n: Integer` pela fronteira, e
`_conferir_tipos_do_modulo` cobra. A aridade era conferida e o tipo
não: a superfície sabia *quantos* argumentos, e não *o que cada um devia
ser* — então `D.valor_de("texto")` passava no `check` e estourava na
primeira conta.

Os dois lados precisam da mesma tradução. A primeira versão comparava o
`Pedido` declarado lá com o `P.Pedido` que chega daqui e acusava
**o código certo**:

```
Parameter 'p' of 'P.com_total' expects Pedido but got P.Pedido
```

Um falso alarme no caminho mais comum de um projeto modular ensinaria a
desligar a verificação inteira. `_esperado_do_modulo` traduz, e devolve
`None` — calando — quando não dá para concluir.

**E a inferência usa o escopo de QUEM CHAMA.** `self.global_scope` não
vê parâmetro de ação nem variável de bloco: `D.valor_de(n)` dentro de
`action f(n)` virou **"Undefined name 'n'"** — **649 falsos alarmes** no
projeto gerado de 252 arquivos, um por uso de parâmetro numa chamada
entre módulos.

E a suíte passava. Os primeiros testes que escrevi chamavam no nível de
topo, onde o escopo global é o certo; o bug só aparecia dentro de uma
ação, que é onde quase todo código vive. Quem pegou foi rodar o `check`
no projeto grande — a mesma lição de sempre: comparar contra uma fonte
de verdade, não reler o código.

A superfície lê só o que `relay` exporta, quando há `relay` — um módulo
que declara o que exporta está dizendo que o resto é interno. Ela é
**conservadora**: devolve `aberta = yes`, e o analisador volta a calar,
quando o outro arquivo não compila, quando há ciclo de import, quando a
profundidade (4) acaba, ou quando o `relay` nomeia algo que só existe em
execução. Um falso alarme é pior que um silêncio.

O cache é por `(caminho, mtime)`. Sem ele, 200 arquivos importando três
vizinhos cada levariam o `check` de 0,7 s a mais de um minuto.

**A resolução de caminho estava escrita em dois lugares, e divergiu.**
O analisador fazia `nome.replace('.', os.sep)`, o que transforma
`'./mod'` em `'//mod'`: todo `adopt` relativo de todo projeto gerava um
aviso "Module not found" falso — 62 no repositório, e **795 de 795** num
projeto de 21 mil linhas. Cada aviso que o `check` emitia ali era
mentira, o que é pior que não avisar nada.

E um pacote não sabia se importar pelo **próprio nome**. O teste de uma
biblioteca escreve `adopt validador`, não `adopt ../src/main`, porque
precisa exercitá-la pelo caminho que um usuário usaria: as suítes dos
**vinte** pacotes do repositório falhavam, e a CI não apanhava — ela não
rodava `dataforge test` dentro de `packages/`.
E `dataforge deps` tinha a **terceira** cópia da regra — uma expressão
regular que começava em `[A-Za-z_]`, então `./vizinho` nunca casava. O
comando cuja única função é mostrar o grafo de imports dizia "0 arquivos
com imports próprios" em todo projeto do repositório, e a detecção de
ciclo nunca disparava. Hoje ele usa o parser e o `resolucao.py`.

**Hífen num caminho relativo não compilava.** `adopt ./minha-lib as L`
falhava: o lexer entrega o hífen como `MINUS`, o loop de segmento parava
ali, e o parser reclamava de um `as` inesperado. `_segmento_de_caminho`
cola `-`, `.` e dígitos ao nome, exigindo **adjacência de coluna** — sem
essa guarda, `a - b` viraria um arquivo chamado `a-b`.

`tests/test_resolucao.py` cobre os quatro, e proíbe a cópia voltar. O
exercício 157 demonstra as quatro conferências e os quatro silêncios,
rodando o `check` de dentro de um `.df`.

**`OS.unset_env` existe agora.** A linguagem sabia definir variável de
ambiente e não sabia remover, e a falta aparecia como poluição entre
execuções: o exercício 160 imprimia 77 variáveis na primeira execução e
78 na segunda. O ambiente é do **processo**, e `dataforge test` cria um
interpretador por arquivo. Ela devolve `yes`/`no` em vez de levantar —
remover é pedir um estado final, e nesse ponto já não importa se estava
lá.

**`OS.temp_dir()` é a pasta do sistema.** Um teste ou exercício que
escreve nela deixa lixo, e `IO.remove_tree(OS.temp_dir())` destrói o
temporário de todo processo da máquina — o exercício 157 fazia isso na
primeira versão. Sempre uma subpasta própria:
`$"{OS.temp_dir()}/df-157-{randint(100000, 999999)}"`.

**Um analisador que morre com traceback do Python é pior que um que
erra**: não diz nada sobre o código, e o usuário não sabe se o problema
é dele. `superficie.py` lia os membros de um `enum` como dicionário, mas
o parser os guarda como pares `(nome, valor)` — e um par com valor
carrega um nó da árvore, que não é hashável. `set(campos)` estourava em
cinco arquivos de `projetos/gestor-tarefas`, os únicos do repositório
com import relativo entre arquivos, que é o caminho que chega lá.

Passou meses invisível porque `scripts/verificar_tudo.sh` rodava `check`
em `exercicios/`, `examples/` e `packages/` — **não em `projetos/`**.
Hoje roda, e `test_nenhuma_ferramenta_estoura_traceback_em_arquivo_do_repositorio`
passa `check`, `lint` e `fmt` sobre as cinco pastas procurando a palavra
`Traceback`.

**Ciclo de import agora é erro do `check`.** Ele estourava só em
execução, no primeiro `adopt`, e o `check` passava limpo num projeto que
não sobe. `superficie.ciclo_a_partir_de` faz busca em **largura**, para
achar o ciclo mais curto — o mais fácil de quebrar — e a mensagem mostra
a cadeia inteira (`a.df → b.df → c.df → a.df`), porque um ciclo de
quatro arquivos é impossível de quebrar sem saber por onde ele passa.

### O analisador vê dentro dos objetos

`p.clientte` é acusado antes de rodar, com sugestão. É a checagem que
mais importa em projeto grande: num arquivo de 40 linhas o erro aparece
na primeira execução; num sistema de 200 arquivos, aparece em produção.

Ela só acusa quando consegue **provar**, e o que a faz calar é tão
importante quanto o que a faz falar:

| Cala quando | Porque |
|---|---|
| o membro vem da mãe ou de um trait | herdado é tão legítimo quanto declarado |
| o blueprint herda de algo não visto | ele pode ganhar qualquer membro |
| o campo nasceu de `self.x := …` | é como a maioria do código cria estado — **inclusive solto no corpo do blueprint**, que é o construtor inline |
| alguém fez `obj.x := …` de fora | quem faz isso abre mão da conferência ali |
| o nome começa com `__` | método mágico é chamado pelo runtime |

A primeira versão olhava `self.x := …` só dentro de métodos, e deu **32
falsos alarmes** num exemplo que funciona há meses. `test_membros_de_instancia.py`
roda o `check` sobre os 320 arquivos do repositório justamente por isso.

**A conferência vale para as duas formas, e nos dois tipos.** `p.campo` e
`p.metodo()` são o mesmo erro, e por muito tempo só a primeira era
conferida em `record`: `p.naoExiste()` passava no `check` e estourava em
execução. A mesma raiz dava o defeito inverso — `self.records[nome]`
guarda só os **campos**, então `f := p.norma` era acusado de não existir.
Os métodos moram em `self.record_methods`, separados **de propósito**: no
mesmo dicionário, `Ponto(norma := 1)` e `p with {"norma": 1}` passariam,
porque é `self.records` que governa a aridade do construtor e as chaves
do `with`. Trocar um falso alarme por um silêncio é a pior das trocas.

E o erro dessa chamada **tem posição**. `_chamar_metodo` é uma casca em
volta de `_chamar_metodo_cru` cujo único propósito é a linha, como a de
`_ler_membro`: quem decide que o nome não existe é o objeto
(`DFRecordInstance.get`, `DFInstance.get`), e ele não conhece o arquivo.
Sem a casca, `o.semCampo` saía na linha certa e `o.semMetodo()` em `0:0`
— sem linha, sem coluna e sem o trecho desenhado, em `record` e em
`blueprint`. O compilador de fechamentos liga em `_chamar_metodo` e por
isso herda a casca; há teste nos dois modos.

### O idioma das mensagens

**O runtime fala português, e `DF_IDIOMA=en` volta ao inglês.** Medido
antes: `interpreter.py` tinha 234 mensagens em inglês contra 55 em
português, e `cli.py` o inverso — 200 contra 15. Quem escreve em pt-BR
recebia `dataforge check` em português e o erro de execução em inglês, na
mesma sessão e sobre o mesmo arquivo.

`idioma.py` resolve isso **sem reescrever as 530 strings**. O texto nasce
em inglês onde sempre nasceu e é traduzido na hora de desenhar, por um
catálogo de moldes com grupos nomeados.

| Decisão | Porque |
|---|---|
| a tradução é no **desenho**, não em `error.message` | `e.message` é o que um `handle` compara e o que 2600 testes comparam; traduzir ali muda o comportamento de programa já escrito, e o que interessa a um programa é a identidade do erro |
| o que não tem tradução **sai em inglês** | ninguém traduz 530 mensagens numa tacada, e um erro é mais útil legível em inglês que ilegível em português |
| **a suíte roda em inglês** (`tests/conftest.py`) | um teste que afirma "Division by zero" checa a *estrutura* do relatório; deixar o idioma solto o faria reprovar a cada tradução nova, o que ensinaria a não traduzir |
| há um **piso de cobertura** (`test_idioma.py`) | sem medida a camada fica pela metade sem ninguém ver, porque o que falta sai em inglês legível — o fallback certo é também o que esconde o buraco |

Duas armadilhas que só apareceram medindo:

1. **As variantes entre módulos são molde próprio.** A aridade local diz
   `takes N but M were given`; a que atravessa um `adopt` diz
   `takes N, got M`. Traduzir uma e esquecer a outra deixa em inglês
   justamente a metade que mais aparece num sistema modular.
2. **O rótulo da seta é traduzido nu.** Ele é composto com um espaço à
   frente (`f" {self.rotulo}"`), e a âncora `^` do catálogo não casaria
   depois disso.

E foi um teste desta camada que achou um vazamento que o passo anterior
não pegou: `non-int`, em `can't multiply sequence by non-int`. O CPython
cola o nome do tipo num prefixo, o hífen é fronteira de palavra, e a
moldura de `, not X` não chega ali.

### Silenciar uma regra, de propósito

`// df: permitir <regra>` na linha, ou na de cima, silencia aquela
regra ali. A regra tem de ser **nomeada**: um `permitir` solto
esconderia o erro seguinte, que ninguém pediu para esconder.

Um analisador sem escape obriga quem escreve a escolher entre conviver
com um alarme e desligar a verificação inteira — e a segunda é o que
acontece. O caso que provou a necessidade está no repositório: o
exercício 139 **demonstra** a armadilha de um `point` inalcançável, com
um `assert` provando o comportamento. O analisador estava certo, e o
exercício também.

Os códigos vêm do campo `code` do diagnóstico, que já existia. O LSP
lê o comentário do **texto do editor**, e não do disco: num arquivo não
salvo, ler do disco silenciaria a regra errada — ou nenhuma.

### O que ele prova a partir de um literal

Quatro checagens que existiam como erro de **execução** e passaram a
aparecer antes de rodar. Medido numa bateria de dez erros que um analisador
maduro pega, o `check` pegava três; hoje pega nove, e o `lint` o décimo.

| Acusa | Código |
|---|---|
| `xs[10]` num cluster de três | `indice-fora-do-alcance` |
| `v["cidad"]` num vault sem a chave, com sugestão | `chave-ausente` |
| `cycle i from 5 to 1` — nunca roda; `step 0` — nunca termina | `cycle-vazio` |
| `1 is "1"` — sempre `no` | `igualdade-impossivel` |

As duas primeiras dependem de `_recolher_literais_fixos`, e **a prudência
dela é o recurso**. O nome perde a garantia se em qualquer lugar do arquivo
ele recebe valor duas vezes, é passado como argumento, tem um método que
muda o tamanho chamado nele, tem um índice ou chave escritos, ou é nome de
parâmetro ou de variável de laço. A coleta é por NOME e vale para o arquivo
inteiro — conservador na direção certa.

`_MUDAM_O_TAMANHO` é uma lista **própria**, e não a `_MUTAM` do aviso de
concorrência: aquela exclui `append` de propósito, porque o GIL protege a
operação inteira. Aqui `append` importa, porque muda o tamanho. As duas
respondem perguntas diferentes, e fundi-las estragaria uma.

Três silêncios que só apareceram rodando o `check` no repositório, e cada
um seria um falso alarme no caminho mais comum:

1. **`v["k"] ?? padrao` não é acusado.** O interpretador trata o lado
   esquerdo de um `??` com indulgência, e `??` é exatamente o que a dica
   daquele erro recomenda. Um analisador que acusa o conserto que ele
   próprio sugere é um analisador que se desliga.
2. **Um parâmetro de tipo não é um tipo.** O `T` de
   `action primeiro<T>(…) -> T` chega com cara de tipo, e
   `primeiro([1,2,3]) is 1` é verdadeiro. Sem `_e_concreto`, a trilha
   ganhava dois alarmes no capítulo que **ensina** generics.
3. **O tipo declarado de uma ação decorada não vale.** `mark @repetir(3)`
   sobre `action eco(x) -> String` faz a chamada devolver um `Cluster`, e
   `eco("oi") is ["oi","oi","oi"]` **passa** em execução. Não há como saber
   qual decorador substitui — um que devolve `void` não substitui nada —,
   e diante de duas respostas o analisador cala.

E `xs[-1]` continua livre: tratar todo negativo como fora do alcance
acusaria a forma normal de pegar o último item.

### OOP como sistema — o custo zero, e onde ele mora

Contratos, sobrecarga, invariantes, metaclasses, `exclusive` e `lazy`
não podem custar nada a quem não os usa. Três `None` garantem isso, e são
a primeira coisa a conferir ao mexer ali:

| Leitura | Quando não é `None` |
|---|---|
| `DFAction.extras` | `overload`, `promises`, `exclusive` |
| `DFBlueprint.vigias` | invariante na linhagem, ou metaclasse com gancho |
| `DFInstance._estado` | objeto congelado, travado, com `lazy`, ou construindo com `readonly` |

E dois atalhos por blueprint, recalculados por `recalcular_acesso()`:
`leitura_simples` e `escrita_simples` dizem que não há propriedade,
descritor, gancho nem `__getattribute__`/`__setattr__`. Com eles o acesso
a campo **ficou mais rápido que antes dos recursos** (4,47 s → cerca de 3,8 s na
carga de método/campo/`spawn`). Quem acrescenta um jeito novo de
interceptar acesso precisa derrubar o atalho ali — senão o recurso novo
não roda para os blueprints "simples", e nada avisa.

`augment` e `Reflexo.definir_metodo` mudam o blueprint depois de pronto:
os dois chamam `esquecer_caches()`, que recalcula o atalho e o cache de
métodos mágicos **das filhas também**.

Quatro decisões que valem lembrar:

1. **Um caminho de construção só.** `spawn`, `Nome(…)`, DI e reflexão
   passam por `_instanciar`. Eram dois, e `Nome()` nascia sem os padrões
   dos campos que `spawn Nome()` tinha.
2. **A instância responde aos protocolos do Python** (`__int__`,
   `__hash__`, `__eq__`, `__lt__`, `__copy__`…) delegando aos métodos
   mágicos. É o que fez metade dos 95 mágicos da doc passar a rodar sem
   adaptar embutido nenhum. **Não** há `__len__`, `__bool__` nem
   `__iter__` ali: o interpretador pergunta `if obj:` sobre instâncias,
   e um `__len__` mudaria a verdade de todo objeto que declara tamanho.
3. **`DFInstanceFinal` só para quem tem `teardown`/`__del__`.** O coletor
   trata objeto com finalizador de outro jeito, e um milhão de objetos
   sem finalizador não paga por isso. `type(obj) is DFInstance` no caminho
   rápido deixa a subclasse no caminho completo — correto, só mais lento.
4. **O `check` registra blueprint declarado dentro de bloco.** O hoisting
   só olha o topo e o corpo de ações; um `blueprint` dentro de `monitor`
   ficava sem linhagem, e `override` e contrato acusavam o que existe.
   `st_BlueprintDeclaration` chama `_hoist([node])` quando não o conhece.

A travessia de processo leva `extras`, `nao_publicos`, `somente_leitura`
e `constantes`: sem isso um grupo de `overload` chegava ao filho como uma
ação de corpo vazio, e `private` deixava de valer lá.

### Posse: a disciplina de recurso, e o que ela NÃO é

`arcane_posse.py` traz dono exclusivo, empréstimo com escopo, contagem
determinística e referência fraca. Num mundo com coletor, o que se
protege é o **protocolo** — soltar uma vez, não usar depois, não
escrever no meio da leitura —, e não a integridade da memória: essa
nunca esteve em risco.

Quatro decisões, e o que cada uma evita:

| Decisão | Sem ela |
|---|---|
| `soltar` idempotente | um `close()` no `defer` e no caminho de erro viraria erro — a disciplina atrapalharia |
| o de fora solta o que possuía (*drop glue*) | soltar o dono externo deixaria o interno aberto, que é o vazamento que a peça existe para evitar |
| o `check` só olha nome que **nasceu** de `Arcane.Posse` | o exercício 118 tem um `mover()` de máquina de estados, e a primeira versão o acusou: dois erros num arquivo que roda |
| perguntar o estado (`movido`, `vivo`, `contar`) vale sempre | `assert a.movido()` depois do `mover` é justamente o que se escreve, e seria acusado |

Os códigos: `posse-movida` (erro), `recurso-vazado` e
`emprestimo-escapa` (avisos — a análise vê um arquivo só, e o recurso
pode ser solto por um caminho que ele não enxerga).

### Tuplas — a forma, ao lado da lista

`(1, "a")` é uma `Tupla` (subclasse de `tuple`, em
`colecoes_tipadas.py`), e **não** a `tuple` crua: essa já tinha dono —
`freeze([1, 2])` devolve uma, e a linguagem a chama de `Frozen`. São
promessas diferentes: `Frozen` é um cluster que não muda, `Tuple` é uma
forma com um tipo por casa. Confundir as duas faria `typeof` mentir para
os dois lados.

Três detalhes: a fatia de uma tupla volta `Tupla` (senão o tipo mudava
no meio de uma expressão); em `Tuple<A, B>` a **aridade é livre**, porque
ela é o tamanho (`COLECOES["Tuple"] is None`); e `_COLECOES_TIPADAS` do
lexer precisou conhecer `Tuple`, senão o campo de um record terminado em
`>` engolia a linha seguinte.

### `type` — o tipo que a linguagem não tinha

`tipos_nomeados.py` traz alias, alias genérico, união, interseção,
refinamento (`where`) e tipo opaco. Uma declaração só; o que muda é o que
vem depois do `:=`. Cinco decisões que valem lembrar:

| Decisão | Porque |
|---|---|
| transparente **confere**, opaco **embrulha** | um alias que mudasse o valor quebraria tudo que já aceita um `Integer`; um opaco que não mudasse não protegeria de nada — `cadastrar(senha)` passaria |
| a base é conferida **antes** da regra | `len(valor)` sobre um número daria uma mensagem sobre `len`, e não sobre o tipo que a pessoa escreveu |
| a regra vale em **toda fronteira** | declaração, parâmetro, retorno e campo. Um refinamento que só valesse na criação é uma sugestão, não um tipo |
| `Opaco` delega por **protocolo** | texto, igualdade, ordem, hash, conta, tamanho e índice continuam funcionando sem que ninguém saiba o que é um tipo opaco — a mesma escolha da ponte para o Python |
| `type`, `opaque` e `where` são **contextuais** | `type := 3` e uma coluna chamada `where` continuam valendo; a declaração só começa quando a linha confirma (`_abre_tipo`) |

O `check` prova o que um **literal** permite (`tipo-refinado`,
`tipo-uniao`, `tipo-intersecao`, `tipo-opaco`, `tipo-circular`) e cala no
resto. A prova roda num avaliador **puro** com lista fechada de funções
(`_PURAS`): a regra é código de quem escreveu, e o analisador não pode
executar código arbitrário para decidir se acusa.

Três armadilhas que apareceram escrevendo a documentação — e que só
apareceram porque **todo bloco da doc roda**:

1. `_compativel("Id", "Id")` precisa ser verdadeiro antes de resolver o
   alias, senão um parâmetro `id: Id` recebendo um `Id` é acusado;
2. `Positivo + Positivo` precisa contar como `Integer + Integer`
   (`_para_a_base`), senão vira "Cannot add Positivo and Positivo";
3. dois opacos do mesmo tipo se comparam pela base (`_ordenavel`).

### As representações do meio, e o que elas provam

`hir.py`, `mir.py` e `lir.py` existem porque o repositório tinha lexer,
parser, AST, analisador e um backend — e **nenhuma forma de ver** o que
havia entre eles. `dataforge ir` mostra as seis fases; `Arcane.Compilador`
as entrega como dado.

**HIR = a AST restrita ao núcleo.** Ele usa as **mesmas classes** da
árvore, de propósito: é o que permite provar a equivalência **rodando** as
duas formas e comparando a saída caractere por caractere. Um
desaçucaramento errado não levanta erro — ele muda o resultado, e nenhum
teste de forma pega isso.

Cinco açúcares são abertos. O que mais importa é a lista do que **não**
é açúcar, com o motivo, porque é ela que impede alguém de "simplificar"
a árvore e mudar a linguagem sem notar:

| Parece açúcar | E não é, porque |
|---|---|
| `cycle i from 0 to 3` | `range` **materializa** a lista; um laço de um milhão viraria uma lista de um milhão |
| `a ?? b`, `x?.y` | a forma com ternário avalia o lado esquerdo **duas vezes**, e ali costuma haver chamada |
| ternário | é expressão, e `given` é instrução: precisaria de temporária, que muda o escopo |
| `mark @f` | `g := f(g)` é errado — um decorador que devolve `void` **não** substitui o alvo |

E `x += 1` só abre quando o alvo é um **nome**: com índice ou membro, o
alvo seria avaliado duas vezes, e `v[sortear()] += 1` consumiria dois
sorteios. É a mesma razão por que `Assignment.value` guarda só o lado
direito.

O `perform` vira marca + `persist`, e **não** corpo duplicado: um `halt`
na cópia de fora não estaria dentro de laço nenhum e escaparia do laço
inteiro.

**MIR = bloco básico com aresta rotulada.** Três decisões:

| Decisão | Sem ela |
|---|---|
| é construído **a partir do HIR** | `orif` e `perform` seriam dois casos a mais aqui, e um caso esquecido num construtor de grafo não dá erro: produz análise errada com cara de verdade |
| a aresta de erro sai da **entrada** do `monitor` | o `handle` veria um estado que talvez não tenha acontecido; da entrada ele vê o pior caso honesto, e com um grafo três vezes menor |
| `thread`, `parallel`, `server` são **opacos** | abrir o corpo num grafo sequencial afirmaria uma ordem que não existe — e é sobre concorrência que uma afirmação errada custa |

**`talvez-nao-definida` é o único diagnóstico novo**, e o que o faz calar
custou mais que o que o faz falar. Sem o filtro de nome **externo** ele
acusaria os nove contadores por fechamento do repositório: `:=` dentro de
uma ação escreve o nome de fora quando ele existe — medido. E `lidos()`
precisou aprender que o `p` de `[p * 2 cycle p in xs]`, o parâmetro de um
`lambda`, o `v` de um `>> morph v:` e o **nome de coluna** de um
`>> onde valor bigger 50` não são leituras do escopo. Sem isso, toda
compreensão do repositório seria acusada.

**LIR = o backend que existe.** Não há código de máquina; há
`compilador.py`, e a descida dele é **parcial**. O que não existia era
saber *o que* recuou — e o inventário separa os recuos **dentro de laço**,
os únicos que aparecem num perfil. A conta sai das tabelas do próprio
compilador: uma segunda lista divergiria no primeiro nó novo, e o
relatório passaria a mentir com confiança.

### SSA, e a otimização que NÃO rendeu

`ssa.py` numera os nomes e põe o nó **φ** nas junções. O ganho concreto
não é elegância: é que a propagação de constante fica **condicional** —
ela não avalia o ramo cuja condição prova falsa, e aí a junção conclui o
que a propagação sobre o MIR perde. Há teste comparando as duas no mesmo
programa; sem ele, "mais forte" seria só uma afirmação.

Daí saiu `ramo-morto`, e os dois silêncios dele foram **medidos**:

| Cala sobre | Porque |
|---|---|
| a cabeça de um laço (rótulo `condicao`) | `persist yes:` com `halt` é o laço infinito legítimo, e todo `stream action` vive disso. **29 acusações** no repositório sem esta linha, todas em generator infinito |
| um `match` | a última instrução é a expressão casada, não uma condição: `match 1:` tem valor provável e isso não diz qual `point` casa |
| condição que lê nome de fora | `:=` numa ação escreve o de fora, e o valor não é deste corpo |

**Dois defeitos meus, nesta ordem, e os dois calados.** A condição da
fronteira de dominância saiu **invertida** — perguntava "`b` domina
`atual`?" onde a pergunta é "`atual` é o dominador imediato de `b`?" — e
o resultado foi um φ em todo bloco de todo laço, para nomes que nem se
juntavam ali. E `lir.py` não contava **compreensão** nem **pipeline** como
laço, o que escondia os recuos que mais custam do relatório que existe
para achá-los. Um grafo errado não dá erro: produz análise com cara de
verdade.

**E o resultado da otimização é o achado desta parte.** O inventário do
LIR apontou dez nós que recuavam dentro de laço; todos ganharam
construtor, com a semântica **extraída** para auxiliares
(`_aplicar_unario`, `_pertence`, `_escrever_indice`) em vez de copiada.
Medido:

| Carga | Ganho |
|---|---|
| feita **dos nós que o inventário aponta** | 1,33× |
| 59 exercícios **reais** do repositório | **1,01× — nada** |

O que recua é dominado por nós que rodam **uma vez** (declaração,
`adopt`, `assert` de topo). Os que rodam em laço são poucos por volta, e
o trabalho da volta já estava compilado: leitura de nome, conta binária,
chamada, leitura por índice. Otimizar o que sobra é otimizar 3% de 3%.

Por isso os três passes de `otimizar.py` ficam **desligados por padrão**.
Eles valem pela informação (`dataforge ir --fase=otimizado`), não pela
velocidade — e a regra que mais recusa é "nada que possa falhar é
dobrado": `1 / 0` dobrado moveria o erro para a **carga**, longe da linha
que o causa.

### O laço de eventos, e por que a fibra não é green thread

`Arcane.Laco` é o reator: **uma** thread dormindo no `selectors` do
sistema. Ele existe porque `async/await` é thread por tarefa e o Kiln é
thread por pedido — os dois servem, e nenhum dos dois escala.

Medido, servidor de linha, uma requisição por conexão:

| Conexões | Laço | Thread por conexão |
|---|---|---|
| 1000 | 73 ms · **1 thread** · +1 MB | 83 ms · 1000 threads · +36 MB |
| 2000 | 151 ms · **1 thread** · +0 MB | 161 ms · 2000 threads · +36 MB |

**O tempo quase empata, e esse é o número honesto.** O que muda é a forma
da conta: plano contra linear. Publicar só o caso em que o outro modelo
já quebrou seria escolher a medida.

**A fibra é real, e sai de máquina que já existia.** `_lazy_stmt` no
interpretador já é um gerador Python que suspende o corpo de um
`stream action` em cada `emit` — o escalonador só precisa dirigi-lo. Mas
ela é **sem pilha**: um `emit` dentro de uma ação **chamada** não
suspende. É a limitação de toda corrotina *stackless*, e é por isso que
a doc diz **fibra** e não *green thread*: pilha própria exigiria
assembly ou extensão em C.

Quatro decisões, e o que cada uma evita:

| Decisão | Sem ela |
|---|---|
| a conta de trabalhos no pool segura o laço vivo | `rodar` terminava ANTES de o resultado voltar, e `executar` era uma forma elaborada de jogar trabalho fora — foi o primeiro teste a falhar |
| autocano (*socketpair*) registrado no seletor | `agendar` de outra thread ficava na fila até o próximo prazo, que pode não existir: um seletor acorda por **descritor** |
| erro num retorno de chamada é contado, não propagado | um reator que morre no primeiro erro derruba o servidor inteiro por causa de **uma** conexão |
| teto opcional na fila de prontas | sem teto, fonte mais rápida que o consumo troca falha visível por morte por memória |

E a trava do repositório pegou o meu teste: `test_agendar_de_outra_thread`
comparava tempo com número fixo. A prova certa não é o relógio — é a
**rede de segurança**: se o laço só parar por causa dela, é porque dormiu
e ninguém o acordou.

### Medir sem inventar ganho

`Arcane.Perfil` existe porque `Bench` responde com **média**, e a média
esconde a cauda — que é o que o usuário sente. Três coisas valem lembrar
ao mexer ali:

1. **O teste que mais importa não é nenhum número: é o que compara uma
   ação COM ELA MESMA e exige "empate".** Uma ferramenta que responde
   "3% mais rápida" a isso é pior que nenhuma ferramenta, porque é assim
   que se escolhe a implementação errada com convicção.

2. **Mann-Whitney, e não teste t.** Tempo de execução não é normal: cauda
   longa à direita, piso duro à esquerda, picos de escalonamento. Um
   teste que supõe normalidade responde com confiança sobre uma suposição
   falsa. E a correção de empates importa: com relógio de resolução
   grossa, metade da amostra empata.

3. **As duas medições são intercaladas.** Medir A inteiro e depois B
   inteiro faz uma queda de clock no meio virar "B é mais lenta" — o
   erro mede o **momento**, não a implementação.

E duas escolhas que mantêm o CI utilizável: **a primeira medida nunca
reprova** (um CI que nasce vermelho por desenho é desligado no mesmo dia)
e a **tolerância é obrigatória** (sem ela, todo CI fica vermelho por
ruído de máquina, o que dá no mesmo).

O percentil sai da amostra **por posto**: interpolar inventa um valor que
não aconteceu, e num P99 o que se quer é uma medida que existiu.

### O coletor, e a distinção que quase todo mundo erra

No CPython quem libera é a **contagem de referência**, e ela roda na
hora. O **coletor** existe só para o **ciclo**. Por isso `Mem.sem_gc`
não vaza memória em geral — só deixa o ciclo para trás —, e é o que
torna a técnica segura num trecho curto sensível a latência.

O `finally` que religa **não é detalhe**: deixar o coletor desligado por
causa de um erro é pior que a pausa que se queria evitar, e o programa
seguiria assim até terminar sem nada denunciando. Há teste com um corpo
que falha.

**Medido**, 6000 ciclos alocados: 3 pausas e 1,84 ms com o coletor
ligado, **0 pausas** com ele desligado. Sem essa medida a frase seria fé.

E `Mem.arena` **não é um allocator**: quem aloca continua sendo o Python.
O que ela troca é o **padrão de uso**, e o ganho só aparece quando o
objeto é caro de montar — meça com `P.comparar` antes de manter.

### A fronteira de capacidade, e um nome que tinha dono

`Arcane.Capacidade` bloqueia a **autoridade ambiente**: o `adopt` de um
módulo fora da lista é recusado pelo nome da capacidade que falta. É a
generalização do que o `comptime` já fazia à mão.

**Ela não tira o que foi ENTREGUE, e isso é o modelo.** Numa linguagem
de capacidade, poder é o que se **passa**, não o que está no ar — e é
por isso que bloquear o `adopt` é a fronteira certa. `limites()` devolve
essa lista em execução, porque um módulo chamado *Sandbox* que
prometesse contenção seria usado onde não pode, e a descoberta viria por
incidente.

**E um erro meu que vale lembrar**: o módulo nasceu chamado `Cofre`, e
`from .arcane_cofre import ArcaneCofre` **sombreou** a classe
`ArcaneCofre` que `arcane_arquivo_seguro` já exportava — a que responde
por `Arcane.Crypto`. O sintoma não foi um erro de import: foi
`examples/42` parando de compilar com "module 'Cofre' has no
'cifrar_pasta'", três camadas longe da causa.

Duas lições. Ao criar um módulo, **confira o nome da classe também**, e
não só a chave do registro:

```bash
grep -rn "class ArcaneNOVO\b" dataforge/stdlib/
```

E o que pegou foi o `check` sobre `examples/` — a mesma lição de sempre:
comparar contra uma fonte de verdade, e não reler o código.

### A superfície como contrato, e o terceiro balde

`Arcane.Abi` responde "esta versão quebra a anterior?". O gerenciador de
pacotes já tinha semver, lockfile e integridade — **faltava o que decide
o número**, e o bump era escolhido a olho.

A conta sai de `superficie.py`, o **mesmo** módulo que o `check` usa para
atravessar arquivos. Uma segunda leitura divergiria da primeira, e aí as
duas ferramentas passariam a discordar sobre o que um módulo oferece —
que é o pior resultado possível para duas respostas da mesma pergunta.

Três decisões, e cada uma tem um caso concreto atrás:

| Decisão | Porque |
|---|---|
| **renomear parâmetro é quebra** | a chamada com nome existe aqui (`somar(a := 1)`), então o nome é contrato e não só a posição — uma ferramenta feita para C não teria esta regra |
| **superfície que não compila não julga** (`desconhecido`) | um falso alarme reprova um release correto, e a segunda vez que isso acontece a conferência inteira é desligada |
| **terceiro balde** para `campo-novo-em-record` | a superfície não carrega valor padrão, então ela **não sabe** se quebra. Acusar reprovaria o correto; calar deixaria passar o que quebra. `--estrito` decide para quem quer o alarme |

E num `record` o **campo é a aridade**: comparar os dois contaria a mesma
mudança duas vezes, com nomes diferentes — foi o que a primeira versão
fez, e o relatório mostrava `Ponto` como quebra *e* como acréscimo
compatível na mesma tela.

### Alvo: o mesmo vocabulário, do outro lado

`Arcane.Alvo` usa **as capacidades do `Arcane.Capacidade`**. Lá elas são
cobradas em execução; aqui são lidas dos `adopt`, antes de rodar. Dois
vocabulários divergiriam no primeiro módulo novo, e as duas respostas
passariam a discordar.

A leitura é **estática e de um arquivo**, e `limites()` diz isso em
execução: um módulo alcançado indiretamente não aparece, e um `roda`
quer dizer "não achei impedimento por esta via".

E sobre WebAssembly, a distinção que a página faz e que vale repetir:
**compilar para** WASM não existe; **rodar em** WASM funciona, pelo
Pyodide, e é rodar o CPython em WebAssembly — com o interpretador
inteiro junto. Emitir um `.wasm` parcial só para marcar a caixa não
rodaria programa nenhum do repositório.

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

### O lockfile era escrito e nunca lido

`forge.lock` é versionado, carrega o sha256 de cada pacote — e **nenhum
caminho de instalação o consultava**. `_sincronizar` sempre resolvia as
faixas do zero e reescrevia o arquivo: duas pessoas clonando o mesmo
projeto em dias diferentes recebiam árvores diferentes, e a
"verificação de integridade" conferia um download contra ele mesmo.

Um lockfile que ninguém lê não trava nada. Hoje:

| Comando | O que faz |
|---|---|
| `install` | instala **o que o lock fixa**, enquanto couber na faixa do `forge.toml` |
| `update` | resolve de novo dentro das faixas e **reescreve** o lock; com nomes, move só eles |
| `add` | move só o que está sendo adicionado — o resto continua travado |
| `outdated` | separa o que sobe com `update` do que exige mudar o `forge.toml` |

Duas regras decidem os empates:

1. **A faixa do `forge.toml` vence o lock.** O manifesto é a intenção; o
   lock é a memória da última resolução. Quem sobe o requisito está
   pedindo outra versão.
2. **O sha256 do lock é comparado com o que chegou.** Um tarball trocado
   numa versão já publicada para a instalação, com a mensagem dizendo o
   que fazer — é o ataque que um lockfile existe para impedir, e ele
   passava batido.

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

`dataforge/stdlib/kiln.py` é o runtime; as onze palavras da linguagem
(`server`, `route`, `respond`, `render`, `redirect`, `middleware`, `after`,
`mount`, `assets`, `views`, `ignite`) atravessam os cinco lugares de sempre e estão em
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

## Vitrine — dashboards e aplicações de dados

`dataforge/stdlib/vitrine/` é o segundo framework web, e ele resolve um
problema diferente do Kiln. **Nenhuma palavra reservada nova**: tudo é
chamada de ação num módulo da biblioteca.

| Arquivo | O quê |
|---|---|
| `nucleo.py` | `No` (componente), `Sessao`, `Contexto` (a pilha de montagem **e a de largura**) |
| `componentes.py` | os 40 componentes base; cada um põe um nó **e devolve um valor** |
| `conteudo.py` | `escrever`, selo, fórmula, 48 ícones em SVG, mídia, toast, status, conversa |
| `entradas.py` | hora, período, faixa, pílulas, segmentado, nota, etiquetas, câmera, `mudou` |
| `dados.py` | a **grade** (pagina e ordena no servidor), o editor, o indicador, os formatos pt-BR |
| `layout.py` | `Area` — coluna, aba, cartão, **malha, painel, diálogo, popover, fragmento** |
| `graficos.py` | a classe `Grafico` e os oito primeiros tipos |
| `graficos_avancados.py` | os 19 que vieram com o painel: combo, cascata, funil, sankey, gantt… |
| `render.py` | a árvore vira HTML; os SVG base e os ~6 KB de cliente moram aqui |
| `render_graficos.py` | o desenho dos 19 tipos novos |
| `render_extra.py` | o desenho dos componentes novos, mais o CSS e o cliente deles |
| `estado.py` | `V.estado` (sessão), `V.geral` (processo), `V.cache` (TTL + LRU), `V.recurso` (objeto) |
| `conexoes.py` | `V.conexao` (uma por processo, com consulta em cache) e `V.segredos` |
| `sessoes.py` | onde a sessão mora: memória, SQLite, arquivos ou um blueprint |
| `runtime.py` | `Aplicacao` — sessões, ciclo do pedido, **resposta parcial por fragmento** |
| `teste.py` | a `Sonda`: clica, digita e pergunta, sem navegador |
| `extras.py` | validação de campo, tradução por sessão, componentes por nome |
| `tema.py` | seis temas prontos, três densidades e o vault de variáveis CSS |
| `api.py` | o dicionário que o `adopt` entrega |

Quatorze decisões que valem lembrar:

1. **O programa inteiro roda de novo a cada interação**, e o estado da
   sessão sobrevive. É o que dispensa callback e diffing — e o que
   torna `V.cache` obrigatório, não opcional.

2. **A área de layout é um objeto, não um bloco de contexto.** A
   linguagem não tem `with`, e inventar uma palavra reservada para o
   layout de um módulo seria caro demais. `colunas[0].metrica(…)` lê
   melhor, aninha sem indentação e pode ser passado adiante.

3. **`_Parar`, `_Navegar` e `_Reexecutar` derivam de `BaseException`**,
   como `halt` e `skip`. O interpretador embrulha toda `Exception` que
   sai de função Python num `RuntimeError_` — com `Exception`,
   `V.exigir_login()` virava a mensagem "exigir_login: _Parar" no meio
   da página em vez de parar coisa alguma.

4. **O cookie de sessão é uma STRING.** O Kiln guarda cookie como a
   linha `Set-Cookie` pronta, não como vault. Passar um dicionário faz
   o navegador descartar o cookie e cada pedido abrir sessão nova — o
   sintoma é um contador que nunca passa de 1 e um login que nunca
   "pega", sem nenhum erro. `Kiln.test` **não devolve cookies**, então
   esse bug só aparece com socket de verdade.

5. **O login reexecuta a página do começo.** Continuar de onde parou
   deixaria a tela vazia para quem escreveu `given V.autenticado(): …`
   — esse teste já passou com a resposta antiga.

6. **O cache indexa o depósito por identidade, não por nome.** Duas
   ações `carregar` em arquivos diferentes dividiriam o mesmo cache, e
   o `teto` da primeira venceria calado sobre o da segunda.
   **Mas `id()` não é identidade ao longo do tempo**: é único apenas
   entre objetos **vivos**, e o CPython reaproveita o endereço de um
   objeto coletado de forma agressiva — cinco mil funções criadas e
   liberadas em sequência dão **um** id distinto. Uma ação nova caía na
   chave de uma ação morta e herdava o depósito dela: o `teto` da outra,
   as entradas da outra e **o valor da outra** — uma função devolvendo
   o resultado cacheado de outra função, calada. Por isso `_por_alvo`
   guarda a ação junto do depósito: enquanto o depósito existir, aquele
   id não pode ser de mais ninguém. Não é vazamento novo — o depósito já
   vivia para sempre.
   Apareceu em **um** dos sete ambientes da CI (macOS, 3.10), num teste
   que pedia `teto=2` e via seis itens. Um bug de cache que depende do
   alocador é a pior classe: some quando se procura.

7. **Acessibilidade é como os componentes são desenhados**, não uma
   camada por cima: `<fieldset>`/`<legend>` nos grupos, `role="alert"`
   no erro de campo com `aria-describedby` ligando ao campo, setas nas
   abas com só a ativa no Tab, e a variação da métrica com a palavra
   ("aumento de") ao lado da seta marcada `aria-hidden`. A primária do
   tema claro é `#B28600` e não o amarelo da marca — amarelo sobre
   branco dá contraste 1,3:1 onde a WCAG pede 4,5:1.

8. **O que não casa com página nenhuma cai no tratador de 404 do Kiln**,
   e não numa rota curinga. Uma curinga é casada na ORDEM do registro,
   então ela engolia toda rota acrescentada depois do `V.montar()` — que
   é exatamente o que se faz para servir uma API ao lado do painel. E a
   página de "não achei" responde **404**, não 200 com "404" no corpo.

9. **Zero dependência também no navegador.** O gráfico é SVG escrito no
   servidor; o cliente são ~4 KB sem build e sem CDN. Uma biblioteca de
   CDN quebra qualquer app em rede fechada — que é onde painel de dados
   costuma rodar. Há teste proibindo `http://`, `https://` e `cdn` no
   CSS e no JS.

**A sessão pode morar fora do processo** (`sessoes.py`). A página
continua falando com um dicionário: o armazém abre a sessão no começo do
pedido e `Aplicacao._confirmar` grava no fim de `executar`, **só o que
mudou** — cada valor é codificado e comparado com a foto tirada ao
abrir. Gravar no `definir` perderia `itens.append(x)`, que não passa por
ele. A gravação é por chave, e um valor que não atravessa processo
(record, instância) vira falha **na página**, sem impedir o resto de ser
gravado. Três armadilhas que custaram:

| O quê | Sem isso |
|---|---|
| `PRAGMA journal_mode=WAL` com retentativa (`_insistir`) | trocar para WAL ignora o `timeout`: dois processos subindo juntos — o caso de uso — davam `database is locked` na hora |
| id desconhecido vira sessão **nova** | o id plantado no cookie virava sessão (fixação), e agora ela sobrevive ao processo |
| só id de 32 hexadecimais chega ao armazém | em `EmArquivos` o id é nome de arquivo, e `../x` escreveria fora da pasta |

`encerrar_sessao` marca `sessao.encerrada`: sem isso, a gravação do fim
do pedido recriava a sessão que acabou de ser apagada.

10. **O layout diz ao gráfico a largura em que ele vai aparecer.**
    O desenho é feito num sistema de 800 unidades e o CSS o encolhe
    para caber no container. Num painel de um terço da tela o fator é
    0,45, e um rótulo de 11px chega ao olho com **5px** — ilegível,
    sem nada que denuncie, porque de longe o gráfico continua bonito.
    `Contexto.larguras` é uma pilha que cada `Area` empurra; o nó do
    gráfico grava `largura_css` **na montagem** (no desenho o contexto
    já acabou), e `_moldura` devolve a escala em `--v-fs`. O teto de
    2,6× existe porque compensar por inteiro num container muito
    estreito faria o rótulo ocupar metade do gráfico. Três desenhos
    precisam dela em **geometria**, e não só em fonte: a margem do
    rótulo deitado, quantas marcas de eixo não se sobrepõem, e o
    tamanho que cabe dentro do buraco de uma rosca.

11. **`void` numa série é um VÃO, não um zero.** O caminho antigo
    convertia ausência para `0.0`, e a linha de um acumulado despencava
    ao chegar no mês que ainda não aconteceu — um gráfico que mostra
    uma queda de um milhão onde só falta o dado. `_tracado` parte o
    caminho em trechos: ligar os dois lados de um vão desenharia uma
    reta entre dois meses que não se tocam, que é a mesma mentira com
    outra forma.

12. **A barra é ancorada no zero; a linha, não.** Não é estética. Numa
    barra o que significa é o COMPRIMENTO, e cortar o eixo faz uma
    barra 3% maior parecer o dobro — o gráfico enganoso clássico. Numa
    linha o que significa é a POSIÇÃO: forçar o zero num patrimônio
    que vai de 1,02 a 1,13 milhão desenha uma reta horizontal, e a
    variação que o gráfico existe para mostrar some. A **área** volta
    a ser ancorada, porque o preenchimento afirma magnitude.

13. **A grade ordena, filtra e pagina NO SERVIDOR; a `V.frame`, no
    navegador.** A diferença não é de tamanho, é de onde a decisão
    mora: a `frame` ordena o que já está na tela, e num conjunto de
    cem mil linhas isso é mentira. A grade é o componente de uma
    listagem de verdade, e por isso a paginação vem ligada — uma
    listagem sem teto é a forma mais comum de um painel travar.

14. **O fragmento redesenha um pedaço, e a dúvida cai sempre para a
    página inteira.** `_fragmento_da_resposta` devolve vazio quando há
    falha (o erro é desenhado fora do fragmento e ficaria invisível),
    quando mais de um campo mudou (não há como saber de quem é a
    mudança), e quando o fragmento sumiu da árvore. Responder a página
    inteira sem precisar custa desempenho; responder um pedaço sem
    poder custa correção.

`site/app/docs/vitrine/referencia/page.tsx` é **gerado** por
`tools/gerar_ref_vitrine.py`, que recusa rodar se um símbolo do módulo
ficar de fora — a mesma trava da gramática do editor. São **213
símbolos em 15 grupos**, e `graficos.TIPOS` tem uma trava irmã em
`tests/test_vitrine.py`: um tipo declarado sem desenho em `render._SVG`
não dá erro — `_svg_linha` assume, e quem pediu um funil vê uma linha.

## Kiln — upload, SSE e WebSocket

`kiln_tempo_real.py` traz as três coisas que o framework não tinha.

**Upload.** O corpo era interpretado como JSON ou formulário simples; um
`<input type="file">` chegava como texto ilegível. Agora os campos vão
para `req["body"]` e os arquivos para `req["files"]` — separados, para
que um `cycle` sobre `body` não tope com bytes onde espera texto.
`salvar_upload` **recusa** nome com `/` ou `..`, tamanho acima do limite
e extensão fora da lista, e o nome final leva prefixo aleatório.

**SSE.** `Kiln.sse(gerador)` marca a resposta como fluxo; o handler
chama o gerador com um `Fluxo` em vez de serializar um corpo.
`fluxo.aberto` vira `no` quando o cliente fecha a aba — sem conferir
isso no laço, um painel fechado deixa uma thread empurrando dado para
sempre. `Kiln.stream` é o mesmo mecanismo sem o formato de evento.

**WebSocket.** O handshake é HTTP com `Upgrade`, e `_atender_ws` o faz
antes de qualquer leitura de corpo. Depois dele, `self.connection` é o
socket. Ping, pong, máscara, continuação e quadro de 64 bits são
tratados dentro do `Soquete`.

Três decisões:

1. **A rota usa o método `WS`**, que não existe em HTTP. Assim ela não é
   alcançável por um GET comum, e um `GET /ws` continua livre para
   servir a página que abre a conexão.
2. **`_ler_exato` insiste até completar.** `recv` devolve menos do que
   se pediu com frequência num quadro que atravessa pacotes, e tratar o
   retorno curto como o quadro inteiro corrompe a mensagem seguinte — o
   sintoma é uma conexão que funciona e de repente para.
3. **`Sala.transmitir` remove o soquete morto** em vez de levantar: um
   cliente que fechou a aba não pode derrubar a mensagem dos outros.

## Arcane.Database — o que um CRUD exige

63 símbolos. O que foi acrescentado, e o problema de cada um:

| Símbolo | Sem ele |
|---|---|
| `transacao` · `savepoint` | a venda é gravada e o estoque não baixa |
| `upsert` · `upsert_many` · `insert_or_ignore` | o catálogo que chega por CSV duplica |
| `increment` | duas vendas ao mesmo tempo perdem uma baixa |
| `paginate` | a tela não sabe desenhar a paginação |
| `aggregate` · `group_count` | todo relatório é SQL escrito à mão |
| `create_search` · `search` | `LIKE %termo%` varre a tabela inteira |
| `explain` · `indexes` · `stats` | ninguém descobre o índice que falta |
| `rollback_migration` | desfazer exige editar o banco à mão |

**Toda escrita confirmava sozinha**, e por isso `transacao` era inútil:
o primeiro `insert` de dentro commitava, e o `rollback` não tinha o que
desfazer. `_confirmar(db)` respeita a profundidade da transação.

**Nome de coluna vai cru para o SQL** — o SQLite não aceita nome por
parâmetro. `_identificador`, `_conferir_colunas` e `_ordem_segura`
recusam o que não parece um nome; a lista de agregações é fechada pelo
mesmo motivo. Isso importa porque o `order_by` de uma listagem chega de
fora (`?ordenar=nome`).

Dois bugs que a busca textual custou, ambos silenciosos:

1. `"livr*"` — o `*` **dentro** das aspas é literal; a sintaxe de
   prefixo do FTS5 é `"livr"*`. A busca devolvia lista vazia, calada.
2. `apelido MATCH ?` é recusado pelo SQLite, e o nome da tabela junto de
   um apelido devolvia vazio — também sem erro. A consulta virou
   subconsulta, que também aplica o `LIMIT` antes do `JOIN`.

## Crucible — instantâneo, banco isolado, instável

`snapshot` usa a infraestrutura que **já existia e não estava ligada a
nada** (`_caminho_snapshot`, `carregar_snapshots`, `gravar_snapshots`,
`REGISTRO.snapshots`). Um JSON por arquivo de teste, ao lado dele.
Na primeira vez grava e passa; `DF_ATUALIZAR_SNAPSHOT=1` aceita a
mudança. Atualizar por padrão seria pior que não ter instantâneo.

`Crucible.banco(db)` abre transação e a desfaz no fim do trial. O
desfazer entra em `alvo.limpezas`, e **não** em `depois_de_cada`: essa
lista roda a cada teste, e acrescentar a ela dentro de um `before` a
faria crescer um item por teste.

`flaky` devolve o número de tentativas: um teste que precisa de três
toda vez não é instável, está quebrado.

## Arcane.Malha — chamada entre serviços, e saga

Uma chamada de ação tem dois desfechos; uma de **rede** tem três, e o
terceiro é o que quebra sistemas: **não se sabe**. Por isso `Malha`
devolve **vault** em vez de levantar — `status 0` é o caso honesto, e
colapsá-lo em "falhou" faz o programa acima repetir uma cobrança.

| Peça | O problema dela |
|---|---|
| `cliente` · `registrar` · `de` | o disjuntor e as métricas vivem **no cliente**; um por chamada esqueceria que o serviço caiu |
| `recuo` | retentativa sem jitter sincroniza os clientes e o serviço volta a cair |
| `Disjuntor` | um serviço caído leva os que dependem dele, e nunca se recupera porque nunca para de receber |
| `Contexto` · `propagar` | sem id que atravessa a fronteira, investigar incidente é cruzar horário de log |
| `Saga` | não existe transação que atravesse a rede |

Cinco decisões que valem lembrar:

1. **POST e PATCH não são repetidos** — a menos que venha `chave :=`.
   Repetir um POST cobra duas vezes; a chave em `Idempotency-Key` dá ao
   servidor o meio de reconhecer a repetição. **Quem honra é o outro
   lado**: a `Malha` não pode fabricar idempotência.

2. **4xx não abre o disjuntor.** Não é falha do serviço — o pedido está
   errado, e contar isso derrubaria uma dependência sadia por um bug de
   quem chama.

3. **O disjuntor conta cada TENTATIVA**, não cada chamada. Com
   `tentativas := 4` e `falhas := 3`, a **primeira** chamada já abre —
   é a conta que mais engana ao calibrar, e `cliente.disjuntor.falhas`
   mostra o número de verdade.

4. **`Retry-After: 0` significa "tente agora".** `pedida or recuo(…)`
   fazia o zero cair no recuo, porque `0.0` é falso em Python. É
   `is not None`.

5. **A saga compensa em ordem INVERSA, e uma compensação que falha vira
   órfã** — `ok` continua `no`, e as compensações seguintes ainda rodam.
   O passo que **falhou** não é compensado: desfazer o que não aconteceu
   é o outro lado do mesmo bug. `conferir()` acusa, antes de executar,
   o passo que escreve sem declarar compensação.

Saga **não dá isolamento**: entre `reservar` e `cobrar`, outro pedido vê
o estoque já reservado. É a troca de atomicidade por disponibilidade, e
ela é o ponto — quem precisa de isolamento precisa de um banco.

Ela **não é um service mesh**: não há sidecar, plano de controle, mTLS
nem roteamento por peso. Isso é infraestrutura, e reimplementá-la em
Python daria um subconjunto pior amarrado à linguagem.

`tests/test_malha.py` são 56 testes contra um servidor de verdade, com
socket — um cliente HTTP testado só com dublê não prova nada sobre o que
acontece quando o outro lado demora, fecha a conexão ou devolve
`Retry-After`. Os exercícios 227 e 228 sobem dois serviços.

## Quadro — a tabela de dados, e os seis verbos

`arcane_quadro.py` é a resposta única a "tabela de dados". Havia **duas**
antes — `Arcane.Analytics.DataFrame` e `Arcane.Data.Frame`, classes
independentes com `group_by`, `describe`, `normalize`, `merge` e `pivot`
implementados duas vezes —, e elas **divergiam**: `describe` devolvia
chaves diferentes conforme o módulo adotado (`25%`/`50%`/`75%` numa,
`median` na outra). As duas continuam funcionando; quebrar código que
existe seria pior.

Cinco decisões que valem lembrar:

| Decisão | Porque |
|---|---|
| a linha é um **vault** | é o que `IO.read_csv(c, yes)` e `Database.query` já devolvem, e o que o `>>` já percorre |
| por dentro é **colunar** | `descrever`, `normalizar` e `correlacao` viram uma passada por coluna |
| todo verbo devolve um quadro **novo** | como `record`/`with`: o pipeline fica reexecutável |
| a ausência tem **um nome só** | `void`, texto vazio e NaN são a mesma coisa; separá-los é de onde vem metade do bug de limpeza |
| coluna que não existe é **erro, com sugestão** | devolver coluna vazia calada é o jeito mais rápido de um relatório sair errado |

`__iter__`, `__len__` e `__getitem__` são o que fazem `cycle`, `len`,
`>>` e a indexação funcionarem **sem que nenhum deles saiba o que é um
quadro** — o mesmo protocolo da ponte para o Python. Trocar protocolo por
`isinstance` em qualquer um desses quebraria o quadro inteiro.

### Os seis verbos

`onde`, `pegar`, `sem`, `ordenar`, `agrupar` e `resumir` são operações do
`>>`, e atravessam os cinco lugares de sempre mais o compilador. Eles
**não** entram em `KEYWORDS`: são contextuais, como as onze do Kiln,
reconhecidos só logo depois de um `>>` (`Parser.VERBOS_DE_QUADRO`).
`agrupar` e `ordenar` são nomes bons demais para tirar de quem escreve, e
o repositório já removeu sete palavras reservadas por serem caras sem
entregar nada.

Três detalhes que custaram, e que vão se perder se não estiverem aqui:

1. **A conversão do pipeline virou preguiçosa.** `eval_PipelineExpression`
   convertia a fonte em lista na entrada; um verbo de quadro precisa do
   **quadro** (`agrupar` precisa das colunas). Hoje cada estágio pede a
   forma de que precisa, e é isso que deixa
   `>> onde … >> morph l: …` conviverem no mesmo pipeline.

2. **`resumir` é tratado ANTES de converter para quadro.** Ele é o único
   que aceita um agrupamento — converter antes de olhar o verbo recusava
   justamente o par `agrupar` + `resumir`, que é o caso central.

3. **`onde` usa a lógica de três valores do SQL.** Comparar com `void`
   não faz a linha passar, em vez de levantar. A outra escolha é a que a
   linguagem faz em toda expressão comum e está certa lá; aqui tornaria o
   verbo inutilizável, porque todo conjunto real tem ausência. Só essa
   falha é engolida, e ela é reconhecida por uma **marca no objeto de
   erro** (`erro.ordem_sem_resposta`), nunca comparando o texto da
   mensagem — que quebraria na primeira tradução.

O analisador **não** infere a expressão de um `onde` no escopo de fora:
os nomes dela são colunas, e ele não sabe quais colunas um quadro tem.
Inferir ali acusaria `onde valor bigger 50` com "'valor' is not defined"
— um falso alarme no caminho mais comum do verbo.

## O analisador de complexidade

`complexidade.py` responde `dataforge big-o`: ele lê a árvore e conta
estrutura — laços aninhados, se o contador dobra ou soma, quantas vezes
uma ação chama a si mesma, e o custo de cada embutido que aparece.

**Errar a classe é pior que não ter a ferramenta**, porque ela erra com
confiança e o relatório é curto o bastante para ser lido como verdade.
Quatro erros de classificação foram medidos e corrigidos, e os quatro
tinham a mesma raiz: contar **forma** sem olhar **fluxo**.

| Era | Devia ser | A causa |
|---|---|---|
| merge sort `O(n log^2 n)` | `O(n log n)` | `ordenar` está na tabela de custos dos embutidos, e a ação do usuário com esse nome era cobrada pelo preço dela — depois multiplicado de novo pela regra da divisão e conquista |
| busca binária recursiva `O(2^n)` | `O(log n)` | as duas chamadas estão em ramos **mutuamente exclusivos**, e eram somadas; e a bisseção mora em `meio := (baixo + alto) ~/ 2`, não no argumento da chamada |
| fibonacci **memoizado** `O(2^n)` | `O(n)` | o aviso do `O(2^n)` manda memoizar, e quem seguia o conselho recebia o mesmo aviso de volta |
| percorrer árvore `O(2^n)` | `O(n)` | `f(no.esq)` e `f(no.dir)` descem por partes **diferentes**: cada nó é visitado uma vez |

Três regras saíram disso, e elas valem ao mexer ali:

1. **O que o arquivo declara vence a tabela dos embutidos.** `ordenar`,
   `unique`, `count`, `join` e `index` são nomes que qualquer um escreve.
2. **Chamada recursiva se conta por caminho, não por subárvore.**
   `_chamadas_no_caminho` soma numa sequência, pega o **maior** entre os
   ramos de um `given`, e trata um ramo que encerra como exclusivo do que
   vem depois. Nunca subestima um caminho que existe: o fibonacci
   ingênuo, cujas duas chamadas estão na mesma expressão, continua dando 2.
3. **Duas chamadas não são exponenciais por si só.** São exponenciais
   quando repetem o mesmo trabalho. Cache e partes distintas quebram isso,
   e os dois são reconhecíveis na árvore.

`tests/test_complexidade.py` confere algoritmos **conhecidos**, cuja
classe não está em disputa — é a única defesa contra um analisador que
concorda consigo mesmo.

## O depurador, e o DAP

`depurador.py` é a máquina: onde parar, como andar, e em que
profundidade de chamada estávamos quando o comando foi dado — é ela que
distingue "entrar na ação" de "passar por cima dela". `dap.py` troca a
interface: em vez de `input()` no terminal, mensagens JSON no stdio, o
que põe os breakpoints na margem do editor.

**Custo zero quando desligado.** `execute` roda uma vez por instrução —
mais de um milhão de vezes num programa médio. Um `if self.depurando:`
ali custaria em TODA execução. Por isso o depurador não é um campo
consultado: ele **substitui** o método, criando um atributo de
instância que sombreia o da classe.

`desligar` faz `del`, e **não** `interp.execute = original`: reatribuir
criaria de novo um atributo de instância com o método ligado, e o
interpretador sairia da depuração carregando uma indireção que não
tinha antes.

Quatro coisas que o DAP precisou resolver, e o sintoma de cada uma:

| Decisão | Sem ela |
|---|---|
| a foto da pilha é tirada na thread do PROGRAMA | `_call_stack` é por thread; lida do laço do protocolo vem **vazia**, e o painel mostra um quadro só chamado "(programa)" mesmo parado dentro de uma ação |
| a parada bloqueia num `threading.Event` | girando num `sleep`, o interpretador continua andando e o valor no painel é de um instante que já passou |
| o laço do protocolo vive em outra thread | um adaptador que só responde quando já está parado não atende `pause` — e pausar é a única saída de um laço infinito |
| `_Encerrar` deriva de `BaseException` | o interpretador embrulha toda `Exception` num `RuntimeError_`, e `disconnect` viraria uma mensagem de erro no meio do programa |

**A vigia (watchpoint) é conferida DEPOIS de cada instrução**, e só
enquanto houver alguma: sem vigia, o `executar` sombreado não avalia
nada. Três decisões, e o que cada uma evita:

| Decisão | Sem ela |
|---|---|
| a comparação é por **foto estrutural** (`impressao`), não por referência nem por texto | `xs.append(1)` não troca a referência, e uma instância sem `__str__` imprime o mesmo texto com qualquer saldo — nada pararia |
| a parada mostra a linha que **acabou de rodar** | a pergunta é "quem mudou isto?"; a linha seguinte manda procurar no lugar errado |
| a vigia criada numa ação só é conferida **dentro** daquele escopo (`_dentro_de`) | o escopo de uma ação que já voltou é reaproveitado, e `acc := 200` lá fora parava como se fosse o `acc` da ação |

No DAP, `dataBreakpointInfo` resolve a leitura **na hora** — o número do
painel morre na próxima parada — e guarda sob o `dataId`;
`setDataBreakpoints` troca todas as vigias do editor de uma vez, porque o
protocolo manda a lista inteira. O motivo da parada é `data breakpoint`,
com "de quanto para quanto" em `description`.

Uma parada em linha não executável é **movida** para a próxima, e a
pergunta "o que é linha executável" é respondida por
`cobertura.linhas_executaveis` — a mesma função. Duas definições
divergiriam, e a parada cairia onde a cobertura não conta.

`tests/test_dap.py` sobe `dataforge dap` como subprocesso e escreve
`Content-Length` na entrada dele, como o VS Code faz. Um adaptador
testado por chamada de função prova que os métodos existem; o que
quebra na prática é a ordem das mensagens.

## DevOps — geradores, e não orquestrador

`dataforge devops` gera Dockerfile, compose, CI, manifestos do
Kubernetes, Helm, Terraform, nginx, Prometheus, SBOM — e **sai da
frente**. Um `deploy` que falasse com Docker e Kubernetes por dentro
esconderia o que a imagem é, e no dia em que alguém precisa mudar uma
camada não haveria onde mexer.

`devops.py` produz **texto**; `devops_cli.py` escreve **arquivo**. A
separação deixa os geradores testáveis sem tocar em disco, e põe a
política de "o que fazer quando o arquivo já existe" num lugar só — e a
política é: **nunca sobrescrever em silêncio**.

Cinco decisões que os artefatos carregam, e o problema de cada uma:

| No artefato | Sem ele |
|---|---|
| `USER forge` | um escape de container vira root no host |
| o manifesto copiado antes do código | um commit numa linha reinstala tudo (8 s → 2 min) |
| `.env` no `.dockerignore` | o segredo fica na camada, e `docker history` o mostra |
| `resources` + as duas sondas no Deployment | um pod come o nó; o Service manda tráfego antes da hora |
| `depends_on: service_healthy` | a app falha na primeira consulta, de forma intermitente |

O `Projeto` lê as fontes com **varredura de texto**, e não com o
parser: o `devops doctor` precisa funcionar num projeto que não
compila — e é aí que ele é mais útil.

O YAML é escrito à mão. `_escalar` cita `yes`, `no` e `null`: em YAML
1.1 eles são booleanos, e um valor assim sem aspas muda de tipo
sozinho.

**`--host=0.0.0.0` é obrigatório dentro de um container** — na Vitrine
e no `ignite` do Kiln (`at "0.0.0.0"`). O padrão é `127.0.0.1`, que de
dentro significa o próprio container, e o sintoma é enganoso: o log diz
"no ar" e o `curl` de fora não recebe nada.

## O empacotamento mente sem dar erro

A extensão do VS Code **não entrava no wheel**. Os globs de
`package-data` viviam sob a chave `dataforge` e eram relativos à pasta
do pacote — `dataforge/editor/vscode/*`, que não existe; a extensão mora
em `editor/vscode/` na raiz.

O resultado era silencioso e total: zero arquivo da extensão no wheel, e
`dataforge editor` instalado por pip respondia "os arquivos da extensao
nao foram encontrados". Cores, snippets, LSP, depurador, os 60 comandos
— nada chegava a quem instalasse pela forma recomendada.

Dois testes *conferiam o texto do `pyproject.toml`* e **passavam**.
Conferir o texto de um arquivo de build não diz o que o build produz:
`tests/test_empacotamento.py` constrói o wheel e olha dentro.

A lista de pacotes é explícita (`[tool.setuptools] packages = [...]`),
e não `find`, porque `dataforge.editor` mora fora da pasta do pacote e
`find` só acha o que tem `__init__.py`. O preço de uma lista explícita é
envelhecer, e há teste comparando-a com o disco.

## A API pública do site, e o sitemap

`site/public/api/*.json` são sete endpoints com a linguagem inteira —
sintaxe, 2156 símbolos, 60 comandos, 177 códigos de erro, o inventário
— servidos com `Access-Control-Allow-Origin: *`. Saem de
`scripts/gerar_api.py`, que lê o mesmo código que o interpretador
executa.

Eles estavam no ar e **não havia uma linha documentando que existem**.
Uma API sem referência é uma API que ninguém usa: `/api` é a página que
faltava, com o contrato, a forma de cada objeto e três exemplos que
rodam (DataForge, `jq` e `fetch`).

A página `/api` e os JSONs coexistem: o export estático gera
`out/api/index.html` ao lado de `out/api/index.json`.

**Não havia sitemap** — `/sitemap.xml` dava 404 — com 96 páginas de
doc, as mais fundas a quatro saltos da home. `site/app/sitemap.ts` sai
de `nav.ts`, a mesma fonte da barra lateral: uma segunda lista
divergiria, e um sitemap que aponta para página removida é pior que
nenhum. Ambos precisam de `export const dynamic = 'force-static'`,
senão o `next build` com `output: 'export'` falha.

E o `metadataBase` apontava para `dataforge-lang.dev`, que **não
responde** — era o único lugar do repositório que citava esse domínio.
Todo canônico e todo Open Graph iam para um endereço inexistente.

## Genéricos de blueprint — três defeitos atrás de uma anotação

`Caixa<Integer>` era **erro de sintaxe**, e isso escondia três coisas.
Ao mexer em genérico, são as três a conferir:

**1. `parse_blueprint` não registrava os parâmetros de tipo.** `type`,
`record`, `enum` e `trait` fazem `self._tipos_genericos[nome] = len(...)`;
o blueprint **lia** os dele e jogava fora. O efeito era uma assimetria
sem explicação — `Par<Integer, String>` num record anotava e
`Caixa<Integer>` num blueprint respondia "não é um tipo de coleção",
sugerindo `type Caixa<T> := …`, que é o caminho errado. Quem acrescentar
uma declaração que aceite `<T>` precisa registrar ali.

**2. O ramo de blueprint da conferência era CÓDIGO MORTO.**
`_conferir_generico_do_usuario` lia `alvo.tipos_dos_campos` — atributo
que nunca existiu. Os nomes reais são `tipos_do_cabecalho` (parâmetros do
cabeçalho) e `fields_decl` (campos do corpo). `getattr` com padrão
devolvia `{}`, o laço não conferia nada, e o parâmetro de tipo virava
comentário. **A falta não dava erro em lugar nenhum**, que é o que a fez
sobreviver: a única forma de notá-la era anotar um blueprint genérico, e
isso era erro de sintaxe. É o mesmo padrão já registrado aqui — `getattr`
com padrão devolvendo `"pass"` para tudo no corredor de testes.

`_tipos_de_campo_do_molde` junta os dois e percorre a linhagem. **A ordem
importa**: o ancestral entra primeiro e o molde por último, para a filha
vencer. A primeira versão empilhava e a mãe sobrescrevia a filha — o
`campo: T` da filha virava o `campo: String` da mãe, e a conferência
passava a falar do tipo errado.

**E `void` não pode dar falso alarme.** Campo ainda sem valor é `void`, e
recusá-lo proibiria `spawn Caixa()` — a forma mais comum de criar um. A
primeira versão acusava "declared as Integer but got Void" em **todo**
blueprint genérico anotado. O preço, nomeado: um campo que guarda `void`
de propósito passa sem conferência.

**3. Escrever o argumento de tipo DESLIGAVA a conferência de membro.**
A busca é `alvo in self.records` / `self.blueprints`, e com os argumentos
a chave vira `'Par<Integer, String>'`: nenhum ramo casava, e
`ex_MemberAccess`/`ex_MethodCall` caíam no `return UNKNOWN`. Então
`p: Par<Integer, String>` e depois `p.naoExiste` passava limpo.

> Escrever **mais** informação de tipo comprava **menos** verificação, em
> silêncio. Este já valia para `record` desde que ele aceitou a anotação.

`_molde_do_tipo` tira os argumentos **só quando a base é um molde
conhecido**: uma `Cluster<Integer>` precisa deles, e é o ramo que confere
`xs.append("x")` que os lê.

### O `check` acusa a linha que causa

Um parâmetro de `T` **sem limite** não é conferido em execução: o campo
recebia o texto calado e a queixa saía na leitura seguinte — *"a variável
'n' declared as Integer but got String"*, uma linha depois e sobre outro
nome. Quem lê vai depurar o `n`, que está certo.

`_conferir_argumento_generico` resolve `T` pelo argumento da anotação e
cobra o literal (`generic-argument`). Ele **cala** sem anotação (não há
vínculo) e quando a aridade não fecha (casar listas de tamanhos
diferentes pareia o argumento errado com o parâmetro errado — e o parser
já acusa a aridade).

### Variância declarada não se aplica — medido

A conferência é **estrutural sobre os valores reais** em cada fronteira.
Medido: `Caixa<Integer>` numa anotação `Caixa<Number>` **passa** (um
Integer é um Number) e numa `Caixa<String>` é **recusada**. A resposta de
assignability já está certa sem declaração nenhuma.

`covariant`/`contravariant` seriam palavras que não decidem nada — e o
repositório já removeu sete reservadas por serem caras sem entregar nada.
`test_nao_ha_palavra_de_variancia_na_linguagem` registra a decisão.

O preço da escolha estrutural, nomeado: ela custa uma passada pelos
campos em cada atribuição anotada, e não decide nada antes de rodar para
um valor que o analisador não vê.

### Um comando que não está no catálogo não existe

Fora do tema, achado na mesma passada: **quatro** comandos eram
despachados em `main` e não tinham entrada em `GRUPOS` — `login`,
`logout`, `whoami` (a publicação autenticada no registro da comunidade,
que fala com um serviço de verdade) e `palavras` (as 113 palavras da
linguagem, com um exemplo que roda para cada). Mais seis apelidos não
declarados (`bigo`, `complexidade`, `cost`, `cr`, `errors`,
`metricas-oop`).

Eles funcionavam e não apareciam em `dataforge help`, nem em
`dataforge help login`, nem em `/api/comandos.json` — e a contagem de
comandos do site estava errada. `test_veja_tambem_so_cita_comando_que_existe`
confere a direção contrária (que o catálogo não **invente** comando);
`test_todo_comando_DESPACHADO_esta_no_catalogo` confere que ele não
**esqueça** nenhum, lendo os `elif command ==` do próprio `cli.py`.

## Os seis últimos itens, e o que cada um ensinou

### O literal decimal: `19.99d`

`19.99` é `Float`, e quem escreve preço não era avisado do arredondamento
binário. O sufixo constrói um `Decimal` a partir do **texto** — é a
diferença entre `Decimal("0.1")` e `Decimal(0.1)`, e o segundo já carrega
o erro do float.

Ele atravessou os cinco lugares mais três: `tokens.py` (um
`TokenType.DECIMAL`, porque um `FLOAT` com um `Decimal` dentro seria um
token que mente), `lexer.py`, `ast_nodes.py`, `parser.py` (quatro sítios:
`parse_primary`, o padrão literal, o número negativo num padrão e
`_COMECA_CONDICAO`), `interpreter.py`, `typechecker.py`, **`compilador.py`**
e **`formatter.py`**.

Três detalhes que custariam:

| O quê | Sem isso |
|---|---|
| o `d` só conta quando **termina** o número | `19.99dias` viraria um decimal mais um `ias` do nada |
| o formatador tem ramo próprio | ele reconstruía do valor e **transformava um Decimal exato num Float**, em silêncio |
| `Decimal` entrou em `ALIASES` | o literal tinha tipo e não podia ser **anotado**: `x: Decimal` dizia "Unknown type" |

E `Decimal` **não é um `Number`**, de propósito: é a mesma decisão que
recusa misturar Decimal com Float. Um `Number` que o aceitasse faria a
falha aparecer dentro da ação, longe de quem passou o valor.

A coloração também: a gramática do editor e `highlight.ts` precisaram do
sufixo, senão a cor contradiz o lexer — que emite **um** token. E o
`gerar_tema.py` recusou gerar até o escopo novo ter cor, que é a trava
funcionando.

### Exaustividade em padrão aninhado

`point [Cor.A, x]` não avisava sobre o `Cor.B`, e o motivo é arquitetural:
a conferência de enum olha o padrão **inteiro**, e um `SequencePattern`
não é membro de enum — ela devolve `False`. A de sequência **reivindica**
o match e se cala, porque `Cor.A` não é irrefutável e o ramo não conta
como cobertura de tamanho. Silêncio total.

`_exaustividade_aninhada` entra **antes** da de sequência e cobra o
produto cartesiano dos eixos de enum, por posição. Ela devolve `False` —
e deixa a outra seguir — quando não conclui: tamanhos diferentes ou
`...resto` (ali a pergunta é de tamanho), uma posição com literal
(`[Cor.A, 0]` não cobre `[Cor.A, *]`), dois enums no mesmo eixo, ou mais
de 64 combinações (um aviso que lista duzentas é ruído).

Uma posição **irrefutável** cobre todos os membros daquele eixo — é o que
faz `point [Cor.A, x]` mais `point [c, x]` ser completo.

### A vigia de LEITURA é outro mecanismo, não uma opção

`w`/`--vigiar` responde *quem mudou isto?*: conferida **depois** de cada
instrução, comparando uma foto estrutural. `r`/`--vigiar-leitura` responde
*quem está consultando isto?* — e uma leitura não muda nada, então **não
há foto a comparar**. Ela intercepta os dois caminhos que leem:
`eval_Identifier` (um nome) e `_ler_membro` (`obj.campo`).

Custo zero quando não há nenhuma: as sombras só existem enquanto
`self.acessos` tem item, e saem com `del` — nunca por reatribuição, pelo
mesmo motivo do `execute`.

Cuidado ao mexer: `vigiar_leitura` **já existia** e é outra coisa — uma
vigia de mudança que lê por função, para o DAP. A nova é `vigiar_acesso`.
No protocolo, `accessTypes` passou a anunciar `["write", "read"]`.

### O banco em contêiner, e o que `esperar` NÃO repete

`Forge.esperar(url)` espera o banco **aceitar** conexão e devolve a
conexão aberta — é a peça que faltava para um `docker compose up` de
verdade, onde a aplicação sobe antes do banco estar pronto.

O recurso dela é a lista do que ela **não** repete. Só erro passageiro
(conexão recusada, reset, `the database system is starting up`) entra na
retentativa; **credencial errada levanta na hora**. Repetir uma senha
errada por quarenta segundos troca um erro claro por um travamento, e o
programa não fica mais certo por esperar. Medido: 0,51 s contra um
contêiner recém-subido, 4 ms para recusar uma senha errada.

`Forge.de_ambiente()` lê `DATABASE_URL`, `DB_URL` ou `FORGE_DATABASE_URL`,
nessa ordem; `Forge.compose(url)` devolve o serviço, o volume e a **URL
de dentro da rede** — o host muda de `localhost` para o nome do serviço,
e é esse o erro que mais custa tempo num compose.

`tests/test_forge_docker.py` sobe Postgres 16 e MySQL 8 de verdade e
**pula sozinho** onde não há Docker, com o nome e a porta derivados do
PID para dois jobs não colidirem.

### O cache de árvores — e o nome importa

**Não** é um cache de fechamentos: função Python não atravessa processo,
não há o que guardar. O que se guarda é a **árvore**.

Medido, e os dois números são o número:

| Medida | Sem | Com |
|---|---|---|
| a fase de parse, 269 arquivos | 258,7 ms | **17,9 ms** (93% menos) |
| `dataforge check exercicios` real | 0,918 s | **0,524 s** (43% menos) |
| `dataforge run` num arquivo de 383 linhas | 131,8 ms | **4,4% menos** |

A terceira linha é a desconfortável: 76 ms dos 132 ms daquele comando são
o `import` do próprio Python. O cache vale onde há muitos arquivos.

**A chave é o que impede o desastre.** Um cache que devolve a árvore
errada é pior que nenhum: o programa roda, e roda outra coisa. Ela carrega
caminho, `mtime_ns`, tamanho, versão, formato **e um resumo de
`lexer.py`, `parser.py`, `ast_nodes.py`, `tokens.py` e
`tipos_nomeados.py`** — sem o último, mexer no parser sem subir a versão
deixaria árvores velhas no cache, e nada acusaria.

Toda falha cai no caminho normal: uma otimização nunca pode ser motivo de
erro. A gravação é `escreve ao lado` + `os.replace`, para um processo
interrompido não deixar arquivo pela metade.

### Versões lado a lado — e o pino tem de ser COBRADO

`project.dataforge` já existia no `forge.toml`, e `Manifest.requires()` já
sabia ler `>=`, `^` e `~`. **O único lugar que os usava era o
`dataforge info`, para mostrar na tela.** Um pino que não é cobrado é um
comentário com sintaxe.

`dataforge run` agora honra o pino: troca por `os.execve` quando a versão
está instalada, **recusa** quando não está. Sem a troca, `use` escreveria
num arquivo e nada aconteceria — e um comando que finge é pior que um
comando que falta.

Três guardas: `DATAFORGE_SEM_TROCA=1` ignora o pino; `DATAFORGE_RAIZ`
troca a raiz (é o que torna isto testável sem mexer na instalação de quem
roda os testes); e uma marca no ambiente impede a troca de acontecer duas
vezes — um laço na partida é o defeito mais difícil de interromper.

`use` reescreve o `forge.toml` **linha a linha**: serializar o TOML de
novo apagaria comentários e reordenaria campos, e um comando que mexe num
arquivo de configuração não pode reformatá-lo por baixo. O campo entra
depois da última linha **com conteúdo** da seção — inserir depois da linha
em branco o punha visualmente na seção seguinte.

`dataforge workspace` lê a árvore e **não instala**. A interseção de
faixas sai da mesma classe `Requisito` que o `resolver` usa: uma segunda
noção de "estas faixas se cruzam?" divergiria da instalação, e o
relatório aprovaria o que o `add` recusa. Ela só acusa o que **prova** —
um pino exato recusado pelo outro lado — e cala no resto, porque um falso
conflito faria o comando ser ignorado.

> E a trava de ontem pegou o trabalho de hoje: `cache.py` e `versoes.py`
> nasceram fora do mapa do ecossistema, e
> `test_todo_modulo_novo_do_nucleo_precisa_entrar_no_mapa` reprovou. Mais
> que isso — **dois componentes marcados `nao-existe` passaram a existir**,
> e o mapa teve de mudar de veredito. É para isso que ele é conferido.

## Três famílias de erro novas

O catálogo é a **única** fonte de verdade sobre erros: dele saem as
classes de `errors.py` e o texto de `dataforge explain`. Três famílias
entraram, e cada uma existe porque a alternativa era `RuntimeError` em
tudo — o que faz a distinção morrer na fronteira do `handle`:

    16xx  dominio               DDD: valor, agregado, evento, regra
    17xx  reativo               sinal, derivado, efeito, observavel
    18xx  memoria estruturada   layout binario, ponteiro, janela

Cada base (`DomainError`, `ReactiveError`, `LayoutError`) pega a
família inteira, e cada peça levanta a sua — há teste cobrando as duas
direções: que a base pegue todas, e que **não** pegue um erro de fora,
senão `handle DomainError` viraria um `handle` sem tipo.

E `NullPointerError` (DF1804) é diferente de `NullReferenceError`: a
segunda fala de um `void` da linguagem; na primeira o endereço existe e
vale zero.

## Domínio — DDD com as distinções COBRADAS

`arcane_dominio.py` traz valor, entidade, agregado, evento, regra,
repositório, unidade de trabalho e contexto delimitado. DDD é um
conjunto de **distinções**, e o valor delas está em serem cobradas —
não em serem nomeadas. Um `blueprint` chamado `Pedido` com um
comentário `// agregado` não impede ninguém de mexer nos itens por
fora.

Quatro decisões, e o defeito que cada uma evita:

| Decisão | Sem ela |
|---|---|
| a invariante é cobrada na **saída** de cada comando | cobrar na entrada deixa o objeto quebrado quando o comando falha no meio |
| o comando recusado é **desfeito por inteiro** | metade da mudança fica aplicada, e a próxima leitura vê um agregado que nunca deveria existir — inclusive um **evento** de um comando que não aconteceu |
| o evento só é publicado quando a unidade **confirma** | o mundo reage a um fato que a transação ainda pode desfazer: o e-mail sai, e o pedido não existe |
| a unidade confere **todas** as invariantes antes de gravar **qualquer** uma | a segunda gravação falha por invariante, e a primeira já está no banco |

E o `por_que_nao` de uma regra composta aponta **a parte** que falhou,
e não a frase inteira: *"maior de idade E mora no Brasil"* não diz qual
das duas a pessoa precisa resolver — e essa frase é o que vai para a
tela.

**A classe do erro é o contrato.** Levantar `RuntimeError_` em tudo faz
a distinção morrer na fronteira: para quem escreve o `handle`, violar
uma invariante e dividir por zero viram a mesma coisa. Cada peça
levanta a sua (família `DF16xx`), e `handle DomainError` continua
pegando as nove.

## Reativo — e o valor que nunca existiu

`arcane_reativo.py` tem sinal (valor com estado), derivado (calculado,
preguiçoso e memorizado), efeito e observável (fluxo). A distinção
entre **valor** e **fluxo** é mantida de propósito: frameworks que
chamam os dois de "stream" fazem a pergunta *"qual é o valor agora?"*
deixar de ter resposta.

**A propagação tem duas fases, e essa é a correção inteira.** Num
losango — `c` lê `a` e `b`, e `b` lê `a` — marcar e avisar numa fase só
entrega um número **errado**:

```
a.escrever(5)
antes:  [3, 7, 15]     <- o 7 nunca foi verdade (5 + o 'b' velho)
agora:  [3, 15]
```

Não é uma notificação a mais: é um valor que aparece e some sozinho na
tela. E `_derivados` é um **conjunto**, então qual caminho vem primeiro
não é escolhido por ninguém — o defeito ia e vinha conforme a ordem de
hash. Daí saem quatro regras:

| Regra | Sem ela |
|---|---|
| o aviso pertence à **propagação**, e não ao recálculo | uma simples **leitura** disparava efeito de terceiros |
| o efeito alcançado por dois caminhos roda **uma** vez | a tela redesenhava duas vezes por mudança |
| a dedup é pelo **objeto**, e não por `id()` | `id()` só é único entre objetos **vivos** — é o bug do cache da Vitrine |
| uma escrita dentro de um efeito abre a **próxima** onda | a fila cresceria enquanto é percorrida |

Três defeitos irmãos, todos calados: **`lote` montava uma lista de
adiados que ninguém lia** (o gancho era escrito e nenhum caminho de
escrita o consultava — três escritas davam três notificações, como sem
ele); **`observar` num derivado nunca lido** registrava a ação num
objeto que jamais seria avisado, porque as dependências nascem da
execução; e **um derivado podia escrever**, o que faz a propagação
correr no meio da própria descoberta (hoje é `ReactiveWriteError`; um
**efeito** escrevendo continua legítimo).

## Estruturas — o layout que tem NOME

`arcane_estrutura.py` fica entre dois módulos que já existiam.
`Arcane.Bytes` empacota por **formato** (`'>i32 u16'`) e o resultado é
posicional — `dados[3]` três meses depois não diz nada. `Arcane.C` tem
`estrutura` e `ponteiro` de verdade, e exige **FFI**: ler o cabeçalho
de um PNG não deveria precisar de `ctypes`.

Cinco decisões:

| Decisão | Porque |
|---|---|
| a **ordem dos bytes** é obrigatória | sem ela o mesmo arquivo lido em duas máquinas dá dois valores, e nenhuma falha |
| o **alinhamento** é declarado e conferido | adivinhar é o que faz o mesmo `.struct` ter 12 bytes de um lado e 16 do outro; o **registro inteiro** também é alinhado, senão um cluster deles sai torto a partir do segundo |
| a **janela não copia** | copiar um registro de 4 KB para ler um campo de 2 bytes é o que faz um parser de arquivo grande levar minutos |
| a faixa vem do **tipo declarado** | `um u8 vai de 0 a 255`, e não `'B' format requires 0 <= number <= 255` — quem escreveu `u8` não tem como ligar uma coisa à outra |
| o ponteiro **segura** o bloco | a referência fraca fazia `Est.ponteiro(Est.bloco(8), "u32")` nascer pendurado. Num mundo com coletor a memória nunca esteve em risco; o que se protege é o **protocolo**, e ele tem um ponto só: `liberar()` |

E `IO.write_bytes`/`read_bytes`/`append_bytes` existem agora: a
linguagem sabia **produzir** bytes — `Bytes`, `Estrutura`, `Crypto` — e
não sabia gravá-los. `IO.write` abre em modo texto com UTF-8; passar
bytes levanta, e passar o texto de um `para_texto` **corrompe** o que
não for texto válido.

## Regex — quatro recursos que eram inalcançáveis

O módulo tinha as operações, os validadores brasileiros e um catálogo
de padrões. O que faltava tornava inalcançável um recurso que a
expressão regular **já tem**:

| Faltava | O efeito |
|---|---|
| grupo nomeado no resultado | `(?P<ano>…)` compilava e o valor vinha **por posição** — ninguém escreve isso para depois ler `groups[2]` |
| `fullmatch` | `match` ancora só no começo: validar com ele aceita lixo no fim, calado |
| `sub` com uma **ação** | mascarar um CPF ou dobrar um número exigia sair do módulo |
| a leitura de **risco** | `(a+)+$` trava o processo em trinta caracteres, e nada dizia isso |

`risk` é uma leitura de **forma**, e a honestidade é o recurso: ela
reconhece os quatro desenhos clássicos e **cala no resto**. E
`safe_search` recusa **antes** de rodar, porque não há como interromper
uma busca já começada: o motor do Python não solta o GIL, então um
prazo numa thread não para nada.

**O objeto de `compile` tinha cinco operações**, na forma que a doc
recomenda para um laço: quem compilava perdia `finditer`, os grupos
nomeados, `fullmatch`, `split` e a contagem — e voltava a chamar a
versão por texto, que é o contrário do motivo de compilar. A lista sai
do módulo (`_COM_PADRAO_E_TEXTO`), e há teste comparando as duas.

## Cinco defeitos do interpretador achados escrevendo exercício

Nenhum deles levantava erro. Os cinco produziam o valor errado, ou
tornavam inalcançável um recurso documentado.

**1. Um receptor chamável virava a chamada.** O ramo
`elif hasattr(obj, '__call__')` ignorava `node.method` e invocava o
próprio objeto: `molde.mapa` devolvia a ação certa e `molde.mapa()`
devolvia um `Bloco` — porque chamava o molde. O recuo continua (sem o
membro, o objeto é chamado como antes), e o teste roda nos dois modos
de compilação.

**2. Um objeto de fora não podia responder à escrita de membro.**
`valor.campo := x` dava `Cannot set a member on a Valor` — verdade, e
sem nenhuma saída. A leitura já era por protocolo; a escrita era a
metade que faltava. A porta é estreita: só delega quem **define**
`__setattr__`.

**3. `tipo_usuario` era lido e nunca escrito.** `_error_matches` tinha
o ramo, com docstring explicando que servia a `trigger MinhaFalha(…)`,
e era **inalcançável**: quem levantava um record de domínio — a forma
que a trilha ensina — só podia capturá-lo com `handle Error` e um
`match`, embora o cabeçalho do erro imprimisse o nome do record. Um
**texto** levantado continua sem nome, senão `handle String` capturaria
todo `trigger "…"`.

**4. `__repr__` não tinha como ser pedido.** Ele estava na lista de
mágicos, na referência e na doc de OOP, e a linguagem não tinha `repr`
— um cluster de objetos imprime com `__str__`. Ele só era alcançado
como **reserva**, quando não havia `__str__`: exatamente quando não se
queria a distinção.

**5. O `check` não conhecia o mágico unário.** `-obj` num blueprint com
`__neg__` era acusado, e roda. Um falso alarme sobre um recurso que a
própria referência documenta ensina a ignorar o analisador — e ele cala
quando a linhagem tem ancestral não visto, que pode trazer o mágico.

E duas imprecisões do **lint**: o marcador `TODO` passou a exigir o
dois-pontos (este repositório escreve palavra em MAIÚSCULA para
enfatizar, e *"TODO objeto que declara tamanho"* virava pendência) e
deixou de olhar dentro de um literal de texto — o exercício que
**demonstra** um lint de brinquedo era acusado pelo próprio lint.

## Duas superfícies para o mesmo conceito

`ctx.estado` do Telegram e `V.estado` da Vitrine são a mesma ideia, e
respondiam de formas diferentes. As duas foram corrigidas na mesma
direção:

- **`ctx.estado` devolvia uma cópia.** `ctx.estado["k"] := v` escrevia
  num dicionário descartável e a mudança sumia — sem erro, sem aviso, e
  com a documentação prometendo *"sobrevive entre mensagens"*. O
  sintoma era um carrinho que nunca enchia. A cópia não era descuido:
  `EmArquivo` **lê do disco**, e ali não há dicionário vivo para
  entregar. Por isso a **vista**, que lê e grava através do armazém.
- **`V.estado["n"] := 1` era erro** (*"A estado cannot be indexed"*):
  o objeto tinha `obter` e `definir` e nenhuma das duas formas naturais
  — indexar e perguntar com `in`. Hoje os dois têm a forma de vault, e
  os nomes de sempre continuam (`somar` não tem forma de índice, e é
  ele que evita a corrida do ler-somar-escrever).

E o **dublê do Telegram era mais estreito que o original**:
`BotFalso.responder_inline` aceitava `**kw` — por **nome**, e não por
**posição**. Uma chamada posicional funcionava em produção e estourava
no teste. Um dublê que diverge aprova o que quebra, ou reprova o que
funciona; há teste comparando as assinaturas uma a uma.

## O mapa do ecossistema, os princípios e o percurso

As três últimas partes da referência Deep Tech são as de **síntese** — e
são as que mais facilmente viram prosa que envelhece calada. Três
decisões ao mexer em `arcane_ecossistema.py`, `arcane_principios.py` e
`arcane_percurso.py`:

**1. `conferir()` cobra as duas direções, e a segunda é a que importa.**
`faltando` acusa caminho citado que sumiu do disco; `orfaos` acusa módulo
de `dataforge/` que não aparece em componente nenhum. Sem a segunda, um
módulo novo nasce **fora** do mapa e o inventário fica incompleto em
silêncio. Ela pagou por si antes do primeiro teste existir: o mapa citava
`arcane_concurrent.py`, e o arquivo se chama `arcane_paralelo.py` — só a
classe se chama `ArcaneConcurrent`. É a mesma lição já registrada aqui
(conferir o **nome do arquivo**, não a memória), agora com trava.

Ao criar um módulo no núcleo, ele entra em `ARVORE` **ou** em
`NAO_E_COMPONENTE`. O `dataforge ecossistema` sai com 1 se não entrar.

**2. Um princípio que não se aplica é informação, não um problema.**
`custo-zero` é `nao-se-aplica`: a frase do documento — *abstrações
compilam para código equivalente ao manual* — não tem como valer sem
backend nativo, e forçá-la a valer seria redefini-la em silêncio. O campo
`aqui` escreve a leitura que vale ("custa zero para quem não usa"), e a
prova a mede nos três sentinelas. Os `VEREDITOS` são três e a lista é
fechada: um quarto valor seria onde "mais ou menos" se esconderia.

E o veredito **não é dez de dez** (5 cumpridos, 4 parciais, 1 que não se
aplica). Um relatório que aprovasse os dez seria a prova de que ninguém o
leu — há teste cobrando que exista pelo menos um parcial.

**3. O percurso não executa o programa, e o import não pode ser cobrado
da fase que o toca.**

`percorrer()` vai do lexer ao LIR e para. A décima fase é nomeada, medida
em zero e marcada `percorrida = False`: executar é o que o programa faz,
e um arquivo de verdade abre soquete e escreve em disco. O teste prova
isso pelo efeito — o programa medido escreve num arquivo, e o arquivo não
pode existir depois.

E os imports lentos são aquecidos **antes** de qualquer cronômetro.
Medido: `lir` importa `compilador` e abre um interpretador por dentro, e
num arquivo de 12 tokens aparecia com **6,8 ms e 93,8%** do total contra
0,05 ms de trabalho real. O total caiu de 7,3 ms para **0,5 ms** e a fase
apontada mudou de `lir` para `tipos`.

> Uma ferramenta que responde "onde o tempo vai" e aponta a fase errada é
> **pior que nenhuma**: a pessoa vai otimizar o lugar que ela indicou.

A trava (`test_o_import_nao_e_cobrado_da_fase_que_o_toca`) é estrutural,
e não um limite de tempo: o `lir` de um arquivo minúsculo não pode ser a
fase dominante. Um limite absoluto mediria a máquina.

**E o verificador de documentação aprendeu uma palavra contextual.**
`tools/verificar_docs.py` envolvia num `server` todo bloco que começasse
com `route `, e por isso reprovava o trecho que **demonstra** que `route`
é um nome livre (`route := "/pedidos"`). Hoje `_e_palavra_kiln` recusa a
leitura quando vem `:=` ou `=` logo depois. Ele recebe o texto **com o
recuo**: tirar o recuo ali fez uma linha indentada abrir um `server` novo
e quebrou 27 blocos que funcionavam.

## As páginas da biblioteca eram uma cópia à mão

As páginas de `/docs/biblioteca/<modulo>` traziam a lista de símbolos
**copiada à mão**, e nenhum gerador as mantinha. A de `Arcane.Regex`
anunciava *"Funções (28)"* onde havia 44 — e a contagem estava no
**título** da seção, que é o que se lê antes da lista.

E havia o outro lado: **32 dos 79 módulos não tinham página nenhuma**.
`Arcane.Quadro`, `Arcane.Malha`, `Arcane.Posse` e `Arcane.Reflexo`
existem, e a única forma de ver a assinatura de um deles era abrir o
código.

`tools/gerar_paginas_biblioteca.py` resolve os dois: a tabela sai do
**próprio módulo** (assinatura lida por `inspect`), e o que foi escrito
à mão — exemplo, aviso, link para o guia — mora em
`site/scripts/conteudo_biblioteca/<curto>.py`.

Três decisões:

| Decisão | Porque |
|---|---|
| o prólogo mora **fora** do `.tsx` | deixá-lo dentro de um arquivo marcado `GERADO` é o convite para editá-lo ali — e a correção some na próxima geração |
| ele **cede** aos treze que `gerar_conteudo.py` escreve | duas ferramentas escrevendo o mesmo arquivo fazem o resultado depender da **ordem** em que rodam, que é o defeito que as duas `slugify` já causaram aqui |
| a barra lateral sai da **mesma** lista | era ela a razão de 32 páginas não serem alcançáveis: uma página que o menu não cita é uma página que ninguém encontra |

## Segurança — e o que a varredura CALA

`arcane_seguranca.py` (52 símbolos) é **o que se faz com a entrada de
fora**. `Arcane.Crypto` tem as primitivas e este módulo as **chama**:
há teste proibindo um nome repetido entre os dois, porque duas contas
iguais escritas duas vezes divergem — e no dia em que divergirem será a
de segurança que estará errada. O `Kiln` já responde CSRF, cabeçalhos e
limite de corpo como **middleware**; aqui é o resto do programa.

**Escapar é por destino, nunca "em geral".** O que protege uma página
HTML não protege uma linha de shell, e o que protege shell estraga um
CSV. Três que quase ninguém lembra:

| Função | O que ela fecha |
|---|---|
| `escapar_csv` | o Excel **executa** a célula que começa com `=`, `+`, `-` ou `@`. Um nome `=HYPERLINK(...)` vira link ativo na planilha de quem exportou |
| `escapar_log` | um `\n` num campo acrescenta uma **linha inteira** ao log, e a investigação seguinte lê um evento que nunca aconteceu |
| `escapar_atributo` | `<a href=x onclick=mau()>` não tem aspas, e ali o espaço é o fim do valor — escapar só `<`, `>` e `&` deixa esse caso passar |

**A lista do que a varredura de segredo NÃO acusa custou mais que a do
que ela acusa.** Sem os três silêncios ela apontava **19 vezes** no
repositório, e as 19 eram falso alarme — inclusive os exercícios que
*ensinam* a não escrever token no arquivo. Uma varredura assim é
desligada no mesmo dia, e junto com ela vão os achados de verdade.

| Cala sobre | Porque |
|---|---|
| valor que se **anuncia** como exemplo | `"123456:AAHexemplo"`, `"sua-senha-aqui"`, `AKIA…EXAMPLE` |
| **JWT com papel `anon`** | a chave `anon` do Supabase vai no pacote do navegador **de propósito** — quem protege a linha é o RLS. A `service_role` ignora o RLS e é comprometimento total. As duas têm o mesmo formato, e só o conteúdo as separa: `_papel_do_jwt` lê o `role` de dentro |
| credencial de `localhost` | `postgres://forge:forge@localhost` num teste é um teste normal; os domínios da RFC 2606 entram pela mesma porta |
| `// df: permitir segredo-no-codigo` | e ele vale em **qualquer** arquivo, não só num `.df` — um segredo de brinquedo mora tanto num teste em Python quanto num exemplo em Markdown |

E a regra `caminho-de-fora` teve de ser **estreitada**: a versão ampla
("`IO.algo` com interpolação") deu 16 das 19 acusações, e todas eram
`$"{pasta}/nome-fixo"` com `pasta` criada duas linhas acima. O que torna
um caminho perigoso não é a interpolação: é a **origem** do que se
interpola.

Quatro decisões que valem lembrar:

1. **`opcoes.ler` valida e NÃO aplica padrão.** Quem chama faz o merge —
   é o que a docstring dela pede, para o padrão não morar em dois
   lugares. A primeira versão deste módulo indexou o resultado direto e
   estourou `KeyError` em toda função com opções.
2. **`vazada` fala com a rede, e isso está no nome.** Manda os cinco
   primeiros caracteres do SHA-1 (k-anonimato do HIBP) e devolve **-1**
   em vez de levantar quando a rede falha: uma política de senha que
   para de funcionar porque um serviço de terceiro caiu impede cadastro
   por um motivo que não é de segurança.
3. **`url_segura` resolve o nome antes de responder.** Bloquear por
   texto não funciona — `localtest.me` resolve para `127.0.0.1`, e quem
   ataca controla o DNS do domínio dele. Ela devolve o `ip` resolvido
   para quem precisar fechar a corrida entre a conferência e a busca.
4. **O `Segredo` não protege da memória.** Ele transforma um vazamento
   acidental (o vault inteiro impresso para depurar) numa linha
   explícita — `revelar()` — que aparece na revisão de código. E
   `__hash__` levanta: o resumo dele acabaria numa chave de cache.

`dataforge seguranca` roda as duas varreduras sobre o projeto, e não só
sobre os `.df`: um segredo vaza do arquivo de configuração muito mais do
que do código.

## Os três módulos de segurança que faltavam

`DATAFORGE_CYBER_SECURITY.md` (na raiz) lista 61 frentes. A maioria já
tinha resposta; três buracos eram reais e viraram módulo. Os três
seguem a mesma regra: **o padrão é o seguro**, e o erro é barulhento.

### `Arcane.Politica` — autorização

Autorização escrita como `given usuario["papel"] is "admin":` espalha a
decisão por cinquenta arquivos, e **o que fica para trás não dá erro:
fica permitindo**.

Sete camadas, nesta ordem, e **a ordem é contrato**: `tenant` →
`negacao` → `acl` → `regra` → `papel` → `delegacao` → `padrao`. A ACL
existe para dizer "neste objeto, não", e se o papel viesse antes ela
nunca seria alcançada.

| Garantia | Sem ela |
|---|---|
| o padrão é **negar** | uma ação nova nasce permitida para todo mundo |
| **negar vence permitir** | a exceção "este usuário não" é apagada por um papel |
| ninguém **delega o que não tem** | a cadeia de delegações cria autoridade do nada |
| a decisão **diz quem decidiu** | o incidente pergunta *por que ele conseguiu* |

Quatro detalhes que custaram:

1. **A aridade da regra é PERGUNTADA, não adivinhada.** A primeira
   versão chamava a condição com quatro argumentos e recuava no
   `TypeError`. Uma `DFAction` levanta `TypeError_` **da linguagem**,
   que não é o do Python: o erro caía no `except Exception` e virava
   "a regra falhou" — ou seja, uma **negação**. Uma regra correta era
   recusada porque o motor errou a chamada, e o sintoma era uma
   permissão que nunca vinha.
2. **Uma regra que falha NEGA.** Tratar a exceção como "não opino"
   faria um bug virar autorização.
3. **`void` da regra é "não opino".** Uma regra que só soubesse dizer
   não bloquearia tudo que ela não entende.
4. **O motivo nomeia o papel que REALMENTE tem a permissão.** Com
   `admin → editor → leitor`, dizer "o papel 'admin' permite
   'pedido:ler'" manda quem audita procurar num papel onde ela não está.

O construtor chama-se **`motor`**, e não `politica`:
`Arcane.Seguranca.politica` já existe e responde outra pergunta (se uma
**senha** atende à política). Há teste proibindo a colisão entre os
módulos de segurança — foi ele que achou esta e mais duas.

### `Arcane.Chaves` — o ciclo de vida

`Crypto` gera bytes e cifra com eles; o que faltava era o resto. Sem
ciclo de vida, o que acontece é sempre o mesmo: uma chave nasce numa
variável de ambiente, é usada para tudo, e **nunca é trocada** —
porque trocá-la tornaria ilegível o que já foi cifrado.

| Decisão | Sem ela |
|---|---|
| a chave tem **propósito** | a que assina token também decifra arquivo |
| a rotação **mantém as antigas** | trocar a chave torna ilegível o passado |
| o dado carrega o **`kid`** | não se sabe qual das cinco chaves usar |
| o material **não aparece em texto** | alguém imprime o objeto para depurar |

**Envelope** (DEK/KEK) porque cifrar um terabyte com a chave mestra faz
rotacioná-la ser reescrever o terabyte. E **`precisa_rotacionar`**
porque uma chave que vence sem ninguém saber derruba o sistema numa
madrugada.

> **`cifra.abrir` devolve `None` quando a etiqueta não fecha, e não
> levanta.** Defensável na primitiva — ela é a primitiva, e quem chama
> decide — mas deixar passar seria o pior defeito possível: um
> `desenvelopar` que devolve `void` faz o programa acima gravar nada
> onde havia um dado. `_abrir` converte isso em erro. A falha de
> integridade é o assunto todo do AEAD, e ela tem de ser barulhenta.

### `Arcane.Deteccao` — a regra e o alerta

Gravar log é quase inútil sozinho: ninguém lê dez milhões de linhas.

| Decisão | Sem ela |
|---|---|
| correlação por **chave** | cinco falhas de cinco pessoas viram "força bruta" |
| janela **deslizante** | 5 falhas às 23h59 e 5 às 00h01 não disparam nada |
| o alerta traz os **eventos** | "força bruta detectada" não é investigável |
| **supressão** | mil alertas por minuto é ruído, e ruído faz desligar |
| a regra que falha é **contada** | um motor que morre deixa de detectar o resto |

A janela é **zerada no alerta**: sem isso o sexto evento dispara de
novo, e o sétimo também.

E o que ele **não** é: não é SIEM (isso é coleta, índice e retenção em
escala), não é SOAR, e `varrer` **não é YARA** — ela cobre as *strings*
e a condição, e não tem módulo PE nem operador de *offset*.

### Ao acrescentar um módulo de segurança

`test_nenhum_nome_se_repete_entre_os_modulos_de_seguranca` compara
`Seguranca`, `Politica`, `Chaves`, `Deteccao` e `Crypto` dois a dois.
Ele achou três colisões reais — `politica`, `analisar` e `motor` — e as
duas primeiras eram a **mesma pergunta respondida duas vezes**. A
terceira não era: `motor` nomeia o objeto principal de dois módulos, e
ninguém o chama sem o prefixo. Ela está em `COLISOES_DELIBERADAS`, que
é **nomeada** de propósito: uma exceção genérica desligaria a trava.

## A seção de segurança da informação

Onze páginas em `site/scripts/conteudo/seguranca_informacao.py`, e a
regra que as governa é a do repositório inteiro: **não se inventa que
existe**. Cada conceito do currículo aparece explicado como um
profissional o usa, e logo abaixo vem o veredito — com código que roda,
ou com "não existe aqui" e o motivo.

Uma página de segurança que promete WebAuthn e não tem é pior que uma
que diz que não tem: a primeira manda alguém construir autenticação em
cima de algo que não está lá, e a descoberta vem no incidente.

**A rota `/docs/seguranca` já tinha dono** (`conteudo/versoes.py`, com
injeção de SQL, XSS nos templates, cadeia de pacotes e TLS). Duas
ferramentas escrevendo o mesmo arquivo fazem o resultado depender da
**ordem** em que rodam — o defeito que as duas `slugify` já causaram
aqui. Por isso o mapa desta seção é `/docs/seguranca/mapa`, seguindo a
convenção de `/docs/partida/mapa` e `/docs/hardware/mapa`, e as duas
páginas se citam.

**Os 30 blocos `.df` da seção rodam**, e não só compilam. Cinco
falharam na primeira passada, e os cinco eram erro meu e não da
documentação:

| O que eu escrevi | O que é |
|---|---|
| `Crypto.cifrar(...)` comparado com texto | ele devolve **Bytes**; a comparação é com `Bytes.para_texto`, e a busca no `hex_encode` |
| `Crypto.jwt_verificar(...)["sub"]` | ele devolve `{valido, carga, motivo}` e **não levanta** com chave errada |
| `adopt` no **fim** do bloco | em dois blocos; o `adopt` precisa vir antes do uso |
| `skip` dentro de um `handle` | `skip` é de laço; num `handle`, deixe o bloco vazio |
| `IO.remove` | o nome é `IO.delete` |

A trava é o `tools/verificar_docs.py` (compila) mais a extração e
execução dos blocos. Compilar não basta: um `assert` errado compila.

**Duas primitivas nasceram desta seção**, porque documentar exige que a
página não seja oca:

1. **`Crypto.hash_password` passou a usar scrypt** por padrão. PBKDF2 só
   encadeia hash e é barato de acelerar em GPU; o scrypt é
   *memory-hard* e exige ~32 MB por tentativa. `verify_password`
   **continua aceitando o formato antigo** — se não aceitasse, o dia da
   atualização seria o dia em que ninguém entra. E `precisa_rehash`
   existe porque o login bem-sucedido é o **único** momento em que a
   senha em claro está disponível para regravar.
2. **`Seg.pkce`, `conferir_pkce` e `estado_de_oauth`** — as peças
   **locais** do OAuth 2.0. O fluxo inteiro é integração, não primitiva;
   o que cabe numa biblioteca é a parte criptográfica, que é justamente
   onde as implementações erram. Só `S256`: o `plain` manda o
   verificador como desafio e não protege de nada.

O que a seção declara como **ausente**, com o motivo: WebAuthn/passkeys
(protocolo com CBOR, COSE e atestação), SAML e LDAP (protocolos
externos), Argon2id e bcrypt (em Python puro seriam piores que o scrypt
do `hashlib`), assinatura assimétrica (e por isso **HMAC não é
não-repúdio** — quem confere também consegue forjar), e TLS no Kiln.

## A página /roadmap

Três mapas em Three.js sobre dados **gerados**
(`site/scripts/gerar_roadmap.py`, de `Arcane.Percurso.fases()` e
`Arcane.Ecossistema.componentes()`). Cinco decisões:

| Decisão | Sem ela |
|---|---|
| a posição de cada nó é **determinística** | uma constelação que muda de forma a cada recarregamento não é um mapa, é um protetor de tela |
| o rótulo é **HTML projetado**, não `TextGeometry` | um carregador de fonte, um `.json` de ~300 KB, e texto sem hinting ilegível abaixo de 14px |
| a página mostra **o que não existe** | um roadmap que só lista conquistas é propaganda; e escrita à mão, essa lista envelheceria no dia em que alguém implementasse um item |
| sem WebGL, sai a **lista** | um mapa que vira retângulo vazio some com o conteúdo junto |
| o desmonte percorre uma lista de `dispose()` | trocar de mapa três vezes deixaria três cenas vivas na GPU — o vazamento clássico de Three em React |

A rota fica no **topo**, e não em `nav.ts` — `tests/test_roadmap.py`
cobra as duas direções, porque quem a acrescentar à barra lateral "para
facilitar" não vai lembrar que ela foi deixada de fora de propósito. No
celular o topo some (`hidden lg:block`), então o menu ganhou a fila das
rotas de topo: sem ela, `/roadmap` e `/download` seriam inalcançáveis
num telefone. E ela entra no sitemap por `AVULSAS`, já que o sitemap sai
do `nav.ts`.

**As trilhas são escritas à mão, e os destinos conferidos.** A ordem em
que vale a pena aprender é julgamento, não dado — mas escrevendo-as,
**8 de 36** rotas que eu "sabia" não existiam: `/docs/controle` e
`/docs/pipeline` soam certas, e as páginas se chamam
`/docs/condicionais` e `/docs/pipelines`. Sem a trava, oito passos de
sete trilhas levariam a 404.

## O número da versão mora num lugar só

O teste chamava-se `test_versao_e_1_0_0` e afirmava o número exato em
três pontos. **O nome de um teste não pode conter o número que ele
confere**: subir de versão obrigava a renomear a função, e renomear é o
que se esquece — o teste passa a reprovar o release correto, e a saída
mais rápida é apagá-lo.

Hoje ele deriva de `__version__`, e `MOLDES_DE_VERSAO` é uma lista de
**moldes** (`'version = "{v}"'`), não de textos prontos. Ao subir a
versão, mude `dataforge/__init__.py` e `pyproject.toml` e rode a suíte:
ela aponta cada arquivo que ficou para trás. Os que precisam de mão são
`editor/vscode/package.json`, `Dockerfile`, os três instaladores,
`packaging/windows/dataforge.iss` (**escrito à mão** — o gerador não o
escreve), `packaging/windows/scoop/dataforge.json`, `docker/README.md`,
`DOCKER.md` e o `dataforge = ">=X.Y"` dos modelos em `modelos.py`.
Depois, `python3 scripts/gerar_tarball.py` e
`python3 packaging/gerar_pacotes.py`.

## Publicar no PyPI

A linguagem está no PyPI como **`dataforge-lang`** — `pip install
dataforge-lang`. O fluxo, e o que conferir antes:

```bash
cd editor/vscode && npx tsc -p .     # SEM isto o wheel sai sem JavaScript
cd ../.. && python3 -m build
python3 -m twine check dist/*.whl dist/*.tar.gz
```

Três armadilhas:

1. **`dist/` também guarda o `.deb`** (`dist/pacotes/`), e
   `twine upload dist/*` morre com "Unknown distribution format". Suba
   os dois arquivos **nomeados**.
2. **A extensão precisa estar compilada.** `editor/vscode/out/` é
   gitignored; sem `tsc -p .` o wheel sai com o manifesto e zero
   JavaScript, e `dataforge editor` instala uma extensão que não faz
   nada. `tests/test_empacotamento.py` constrói o wheel e olha dentro.
3. **Uma versão publicada não pode ser reusada.** `v1.0.0` já existia
   como release no GitHub, então publicar um 1.0.0 diferente no PyPI
   faria o mesmo número nomear dois artefatos — é o ataque que o
   lockfile do `dataforge` existe para impedir. Daí a 1.1.0.

O token vai **só por variável de ambiente**, nunca em arquivo:

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD='pypi-…' \
  python3 -m twine upload --non-interactive \
  dist/dataforge_lang-X.Y.Z-py3-none-any.whl dist/dataforge_lang-X.Y.Z.tar.gz
```

A prova de que funcionou não é a saída do `twine`: é instalar do PyPI
num ambiente limpo e rodar um `.df`.

## O que é gerado — não edite à mão

| Arquivo | Gerador | Guardado por |
|---------|---------|--------------|
| `editor/vscode/syntaxes/dataforge.tmLanguage.json` | `tools/gerar_gramatica.py` | `tests/test_editor.py` |
| `site/app/docs/kiln/referencia/page.tsx` | `tools/gerar_ref_kiln.py` | — |
| `site/app/docs/vitrine/referencia/page.tsx` | `tools/gerar_ref_vitrine.py` | `tests/test_vitrine.py` |
| `site/app/docs/biblioteca/page.tsx` | `tools/gerar_pagina_biblioteca.py` | `tests/test_regressoes.py` |
| **60 páginas** de `site/app/docs/biblioteca/<mod>/` | `tools/gerar_paginas_biblioteca.py` | `tests/test_api_e_marca.py` |
| `doc/BIBLIOTECA_PADRAO.md` | `tools/gerar_doc_stdlib.py` | — |
| `site/lib/dados-gerados.json` | `site/scripts/gerar_dados.py` | — |
| o `const headings` de cada `site/app/docs/**/page.tsx` | `site/scripts/gerar_indices.py` | `tests/test_api_e_marca.py` |
| **67 páginas** de `site/app/docs/` | `site/scripts/gerar_conteudo.py`, de `site/scripts/conteudo/*.py` | o job `gerado` do CI |
| `site/public/dist/*.tar.gz` | `scripts/gerar_tarball.py` | `tests/test_regressoes.py` |
| `site/lib/marca.ts`, favicon, ícones | `tools/vetorizar_logo.py` | `tests/test_api_e_marca.py` |
| `site/public/api/*.json` | `scripts/gerar_api.py` | `tests/test_api_e_marca.py` |
| `site/app/sitemap.ts` e `robots.ts` | saem de `nav.ts` em tempo de build | `tests/test_api_e_marca.py` |
| `github.com/dataforge-df/docs` | `scripts/sincronizar_docs_org.py` | `verificar_tudo.sh` |
| `dataforge/marca.py` (arte ASCII) | `tools/vetorizar_logo.py` | — |

**Sessenta e sete das páginas de `/docs` são geradas.** Elas trazem o aviso na
primeira linha, com o caminho do arquivo de conteúdo que as origina — editar o
`.tsx` funciona até alguém rodar o gerador, e aí a correção some sem nada
explicando. Foi assim que uma contagem de símbolos voltou a ficar errada depois
de corrigida.

O índice lateral dessas páginas sai da **mesma** `slugify` do
`gerar_indices.py`. Já foram duas implementações, e elas se sobrescreviam a cada
geração: o estado final dependia da ordem em que os dois geradores rodassem.

A gramática do editor tem **duas** travas: o gerador recusa rodar se uma
palavra de `KEYWORDS` não estiver em nenhum grupo de cor, e um teste falha se o
arquivo versionado divergir do que o gerador produz. A versão anterior era
escrita à mão e por isso não conhecia `record` nem `enum` — exatamente o
problema que isso resolve.

O mesmo vale para `site/lib/highlight.ts`: há teste comparando com `tokens.py`.

## O que só quebra fora desta máquina

A suíte local **não é o que o CI roda**, e a diferença não é detalhe: o
CI ficou vermelho em todas as execuções por dias enquanto eu relatava
"tudo verde". Três coisas causam isso, e todas têm o mesmo formato —
uma decisão do ambiente que o repositório não contém.

**As anotações do CI são legíveis sem autenticação**, e é por onde
começar quando `gh` não está logado:

```bash
curl -s "https://api.github.com/repos/estevam5s/DataForge/commits/<sha>/check-runs" \
  | python3 -c "…"      # cada check-run tem /annotations com o resumo do job
```

O `ci.yml` emite `::error title=…::` com a cauda do log justamente para
isso: saber que algo divergiu sem saber **o quê** é metade de um
diagnóstico.

### O resumo do pytest não mostra ERRO, e a mensagem vive numa linha

Duas limitações do relatório, e as duas escondiam defeito real:

| O quê | O efeito |
|---|---|
| `pytest -rf` lista o que **falhou**, não o que deu **erro** | 11 erros de `test_empacotamento.py` em todo job, por meses, invisíveis no resumo. O `ci.yml` não achava linha nenhuma e caía no ramo "processo morto", que anuncia um teste **que passou**. Hoje é `-rfE` |
| o resumo corta no primeiro `\n` | a anotação do job é montada do resumo, então o motivo tem de caber numa linha. Três reprovações do Windows chegaram dizendo `packaging\arch\PKGBUILD` — a primeira linha de um stdout de **sucesso** |

Quando um teste roda um subprocesso, a mensagem junta `stdout` e `stderr`
numa linha com `⏎` e guarda a **cauda** (`_uma_linha`). Foi assim que o
traceback do Windows finalmente apareceu — e ele dizia
`ValueError: path is on mount 'C:', start on mount 'D:'`: o runner clona
o repositório em `D:`, o `tmp_path` do pytest fica em `C:`, e
`os.path.relpath` entre unidades **levanta**. O `.deb` estava pronto; quem
estourava era a linha que o anuncia.

### O que é gerado fora do repositório não existe no CI

`editor/vscode/out/` é gitignored, e o único `tsc` dos dois workflows
tinha `--noEmit` — que confere tipos e **não escreve nada**. Resultado:
nenhum job compilava a extensão, e todo pacote feito em máquina limpa
(wheel, sdist, `.deb`, binário) saía com o manifesto da extensão e zero
JavaScript. `dataforge editor` instala, o VS Code carrega, e nada
acontece.

Aqui passava porque esta cópia de trabalho tem o `out/` de meses atrás —
a mesma forma do defeito do tarball: **o layout que só funciona de
dentro**. Hoje o job `extensao` compila e constrói o wheel em cima
(é o único lugar do CI onde node e Python se encontram), o `release.yml`
compila antes do PyInstaller e do `.deb`, e `gerar_tarball.py` **recusa**
gerar sem os três `.js`.

### Insistir não desfaz um impasse

`PRAGMA journal_mode=WAL` pede a trava exclusiva e não respeita o
`timeout` do driver, e por isso a troca já vivia dentro de um laço de
retentativa. Dois processos subindo juntos — o caso de uso — ficavam
**vivos e calados** pelos 30 s do prazo, cada um segurando o que o outro
precisa. O sintoma foi um servidor que "não subiu" no macOS do CI, morto
pelo `kill` do próprio teste.

Retentativa repete; o que desfaz é a pergunta que faltava: **o modo já é
WAL?** Quem trocou foi o primeiro processo, uma vez, e o arquivo guarda
isso — a pergunta é refeita **dentro** da retentativa, senão a corrida
volta pela janela entre a leitura e a troca.

### Medida que mede a máquina

Três reprovaram assim de uma vez, e cada uma ensina uma forma
diferente do mesmo erro:

| O que reprovou | O que estava sendo medido |
|---|---|
| `processos nao ganharam da serie: 1.02x` | a **partida** dos processos, não o paralelismo |
| `parallel` com 1,47x no macOS | a criação de duas threads, num runner de três núcleos |
| "o construtor virou quadrático" | o **texto** do rótulo: a faixa *"entre O(n log n) e O(n²)"* contém `n²` para dizer que ficou **abaixo** dele |

A saída nunca é afrouxar o limite — é dar à medida um numerador maior
(quatro tarefas em vez de duas; blocos de 300 mil em vez de 150 mil) ou
cobrar a grandeza certa (o **fator** de crescimento, que já é uma razão:
dobrando o n, linear dá ~2 e quadrático ~4).

E quando nem isso basta, há o **ponto de calibração**: um algoritmo
conhecidamente linear, medido no mesmo instante. Se ele não dá ~2, a
máquina não está medindo, e o teste diz isso e pula. Medido, com seis
threads queimando CPU: o linear foi de 1,98 para 3,30–4,90 e o
quadrático de 4,17 para 9,66–14,26 — mais repetições não salvam, porque
o `Bench` já usa o **menor** tempo de N e a disputa sustentada atinge
todas. A calibração não deixa de proteger nada: se o código virasse
quadrático, a referência continuaria em 2.

**E o `p` sozinho reprova por desenho.** Alfa de 0,05 *significa* que
uma em vinte comparações de coisas iguais cruza o limiar: o teste que
compara uma ação com ela mesma falharia 5% das vezes por definição.
`Arcane.Perfil.comparar` passou a exigir as duas perguntas — *a ordem
das amostras é acidente?* (o p) e *e daí?* (o efeito, com piso) — e a
**alternar a ordem dentro da volta**, porque quem mede primeiro paga a
entrada dela: é viés sistemático, e por isso não desaparece com mais
amostras.

### O `spawn` cobra o `if __name__`, e o `forkserver` é o meio-termo

`map_processos` não pode usar `fork`: o filho herdaria a memória do pai,
e com ela uma conexão SQLite que chega "funcionando" sem passar por
`travessia.py` — a linguagem respondia **duas coisas** conforme o
sistema. Mas trocar por `spawn` cobra dois preços que só aparecem
instalado:

1. **o filho IMPORTA o módulo principal.** O que o `pip` gera tem a
   guarda; o lançador do `.deb` e a entrada do `.exe` são escritos à
   mão aqui e não tinham. Sem ela, cada trabalhador reexecuta a CLI, e
   a mensagem fala de *bootstrapping phase* — vocabulário do
   multiprocessing, três camadas longe de quem chamou `dataforge run`.
   No executável congelado a guarda não basta: é preciso
   `multiprocessing.freeze_support()` **antes** de `main()`.
2. **todo trabalhador importa o interpretador inteiro.** Medido, partida
   de 4: spawn 59/54/60 ms, `forkserver` 52/16/18 ms. O `forkserver`
   nasce limpo (é isso que o separa do `fork`), faz o import **uma** vez
   pelo `set_forkserver_preload`, e cada trabalhador sai de um fork
   dele. O Windows fica com `spawn`, que é o único método que ele tem.

### Otimismo não garante progresso

O STM valida-e-repete: ninguém escreve errado. **Terminar é outra
promessa.** Uma transação longa que disputa a mesma variável com
transações curtas perde toda corrida, e repete para sempre — inanição,
que não aparece em máquina com núcleo sobrando e aparece com 40 threads
em runner pequeno (*"não fechou em 1000 tentativas"*, nos quatro Pythons
do Linux).

Depois de `_PESSIMISTA` corridas perdidas a transação passa a rodar
**segurando a trava do commit**: é a transação irrevogável, e a
validação não tem como falhar. A prova não depende de relógio — uma
transação que dorme 5 ms dentro do corpo contra quatro que confirmam sem
parar: sem o plano B estoura o teto, com ele termina.

### Windows: cinco coisas que não existem aqui

| Sintoma | Causa |
|---|---|
| `[Errno 22] Invalid argument` com o caminho mutilado | `"C:\temp"` numa string: `\t` é tabulação, `\r` é retorno de carro. Em macOS e Linux é **pior** — o nome é válido, e o arquivo nasce em outro lugar sem erro nenhum |
| traceback depois de o pacote estar pronto | `subprocess.run(["which", …])` — `which` é do Unix; use `shutil.which`, que também conhece `PATHEXT` |
| `WSAEINVAL (10022)` | `getsockname` num socket UDP ainda **não ligado**; no Unix devolve 0 |
| a conexão "expira" onde devia ser recusada | o firewall do Windows **descarta** o SYN de uma porta fechada em vez de recusá-la. A espera ali é a verdade |
| credencial legível por outras contas | `os.chmod` no Windows só liga o somente-leitura. A restrição é ACL: `icacls /inheritance:r /grant:r <dono>:F` |

E a saída de um programa do Windows não é UTF-8: todo `subprocess` com
`text=True` declara `encoding` — há trava sobre isso
(`test_nenhum_subprocess_decide_a_codificacao_pelo_sistema`), e ela
pegou as duas chamadas novas ao `icacls` no mesmo dia.

### O host também é configuração, e nenhum teste o lê

A página publica `irm https://…/diagnostico.ps1 | iex`, e o
`site/vercel.json` declarava o `Content-Type` do `instalar.ps1` e **não**
o do `diagnostico.ps1`. O `Invoke-RestMethod` decide pelo tipo: com
texto devolve a string, com `application/octet-stream` devolve os
**bytes** — e o `iex` recebe um `Byte[]`, não tem o que executar e
**não dá erro**.

Foi assim que o harness da máquina virtual falhou calado (o
`http.server` do Python serve `.ps1` como octet-stream), e eu corrigi o
harness sem olhar o `vercel.json`. Todo script que a página manda
canalizar precisa do tipo declarado ali — há trava em
`tests/test_windows.py`.

## Instaladores

| Arquivo | Para |
|---------|------|
| `scripts/instalar.sh` | macOS e Linux, POSIX sh (roda em dash e busybox) |
| `scripts/instalar.ps1` | Windows, PowerShell |
| `Dockerfile` | imagem multi-estágio, usuário sem privilégio |

Ambos criam uma venv em `~/.dataforge` — não tocam no Python do sistema e
não pedem sudo. A origem do download é o site (`/dist/dataforge-X.tar.gz`),
com o GitHub apenas como alternativa.

### Os binários: a tag publica, e o site serve

`release.yml` é disparado por uma tag `v*` e constrói **nas quatro
plataformas** (Linux, macOS Intel, macOS ARM, Windows), roda os
exemplos e os exercícios *pelo binário*, monta o instalador do Windows
com o Inno Setup, gera o `.deb` e o PKGBUILD, e anexa tudo ao release
com um `SHA256SUMS.txt`.

**Um runner que não existe não dá erro: ele nunca começa.** A primeira
tag ficou meia hora com o job do macOS Intel em `queued` enquanto os
outros três terminavam — sem mensagem, sem falha, sem prazo. `macos-13`
foi **retirado** pelo GitHub; as imagens mantidas são `macos-14`,
`macos-15` e `macos-26`, e só as duas últimas têm variante x64. Era o
primeiro release do repositório, então não havia histórico dizendo que
aquele runner nunca tinha funcionado.
`test_todo_runner_dos_workflows_e_uma_imagem_que_existe` compara os
rótulos usados com os que o GitHub mantém. A lista envelhece — é o
preço de conferir algo que vive fora do repositório — mas envelhece com
uma mensagem clara.

**E a descrição do `.deb` dizia "38 modulos" quando eram 39.** Um
número escrito à mão no modelo de um pacote envelhece sem ninguém ver:
o `.deb` é gerado no release, e ninguém lê a descrição dele duas vezes.
Hoje o modelo tem `{MODULOS}` e `{SIMBOLOS}`, e há teste que constrói o
pacote e olha o `control` dentro dele.

**A página `/download` anunciava sete arquivos e nenhum existia.** Não
havia release no repositório — a tag nunca foi criada — e cada botão
levava à página 404 do GitHub.

E havia teste sobre isso, e ele passava: conferia que os nomes na
página batiam com o que o `release.yml` constrói. A coerência entre
dois arquivos do repositório, e nada sobre o que está publicado. Uma
trava que valida o mapa e não o território.

`scripts/verificar_downloads.py` vai ao território: pede cada arquivo e
confere código, tamanho e tipo. O tamanho mínimo importa — **o 404 do
GitHub responde 200 em alguns caminhos** e devolve HTML de ~10 KB, que
passaria por um teste que só olha o status.

O download sai pelo **domínio do site**: `/baixar/<arquivo>` é um
`rewrite` no `site/vercel.json` que a edge resolve contra o release.
Quem instala não sai da página, e um ambiente que bloqueia o GitHub não
fica sem instalar. O padrão é `:arquivo` — um segmento só, para não
haver como montar caminho para fora do release.

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
| `tests/test_resolucao.py` | `pytest` | onde mora o módulo de um `adopt`; ciclo no `check`; os 20 pacotes rodam; a cópia não volta |
| `tests/test_cobertura.py` | `pytest` | o denominador e o numerador da cobertura; a linha vai para o arquivo certo |
| `tests/test_devops.py` | `pytest` | os artefatos: compose validado pelo `docker compose config`, manifestos conferidos como dado, a sonda do HEALTHCHECK executada, e o README do Hub |
| `tests/test_banco.py` | `pytest` | transação que desfaz, `upsert`, `increment` sob 4 threads, FTS5, `explain`, migração com `down`, e o nome de coluna recusado |
| `tests/test_kiln_tempo_real.py` | `pytest` | multipart, SSE e WebSocket — o protocolo falado à mão, para pegar erro de enquadramento |
| `tests/test_dap.py` | `pytest` | o depurador do editor, falado por um cano: ordem das mensagens, a parada que bloqueia de fato, `pause` num laço infinito, e a extensão concordando com o adaptador |
| `tests/test_empacotamento.py` | `pytest` | **constrói o wheel** e olha dentro — a extensão, o `out/`, o cliente LSP e todo módulo de `dataforge/` |
| `tests/test_malha.py` | `pytest` | chamada entre serviços contra um servidor que se comporta mal de propósito: retry, disjuntor nos três estados, `Retry-After`, propagação de rastro, e a saga compensando |
| `tests/test_vitrine.py` | `pytest` | a Vitrine: árvore, interação, estado, cache, autenticação, gráficos, escape, HTTP — e um ciclo completo por socket |
| `tests/test_excel.py` | `pytest` | `.xlsx`: o arquivo gerado é um ZIP válido, os tipos sobrevivem à ida e volta, `describe(frame)` |
| `tests/test_editor.py` | `pytest` | a gramática do VS Code está em dia com `tokens.py`; os snippets são DataForge válido |
| `tests/test_oop_avancada.py` | `pytest` | contratos, modificadores, sobrecarga, metaclasses, reflexão, DI, padrões, memória, métricas, LSP — e **executa cada bloco `df`** das páginas de `/docs/oop` e da §7 da referência |
| `tests/test_abi_e_alvos.py` | `pytest` | as onze regras de compatibilidade uma a uma, o terceiro balde do `record`, o mapa de simbolos achando o nome sem dono, e os seis perfis de alvo |
| `tests/test_inicio_e_capacidade.py` | `pytest` | as fases da partida, o finalizador de thread, o teto da pilha que vale de verdade — e o teste que prova o **limite** da fronteira de capacidade |
| `tests/test_perfil.py` | `pytest` | percentis, o flame graph das acoes, pausas do coletor — e o teste que **compara uma acao com ela mesma** e exige "empate" |
| `tests/test_memoria_e_gc.py` | `pytest` | o coletor ligado e desligado, `sem_gc` religando mesmo com erro, congelar, arena — e a **medida** que prova a reducao de pausa |
| `tests/test_laco.py` | `pytest` | o reator: que ele **dorme** em vez de girar, prazo em ordem, contrapressao, o erro que nao o derruba, fibras intercaladas — e **120 conexoes numa thread**, com a identidade da thread conferida dentro do retorno de chamada |
| `tests/test_ssa_e_otimizacao.py` | `pytest` | dominancia, no phi, a propagacao condicional **comparada** com a do MIR, os tres passes provados pela saida, e o repositorio sem falso alarme |
| `tests/test_compilador_interno.py` | `pytest` | HIR, MIR, LIR e as analises — inclusive a **equivalencia** do HIR rodando exercicios do repositorio nas duas formas e comparando a saida |
| `tests/test_dominio.py` | `pytest` | as sete peças de DDD e o que cada uma **recusa** — e a classe do erro, que é o contrato |
| `tests/test_reativo.py` | `pytest` | preguiça, memória, dependência descoberta — e o **losango**, que entregava um valor que nunca existiu |
| `tests/test_estrutura.py` | `pytest` | o layout conferido contra o `struct` do Python, o alinhamento, a janela que escreve no bloco e as duas formas de um ponteiro não valer nada |
| `tests/test_regex_extra.py` | `pytest` | grupos nomeados, ancoramento nas duas pontas, troca que calcula, a explicação e os quatro desenhos de risco |
| `tests/test_ffi_c.py` | `pytest` | `Arcane.C`: a libm e a libc de verdade, o layout de uma struct conferido contra a ABI, aritmética de ponteiro, o nulo recusado, e o **`qsort` do C chamando uma ação DataForge** |
| `exercicios/run_all.py` | script | 387 exercícios em 57 módulos, cada um com `assert` |
| `projetos/*/tests/` | `dataforge test` | 61 testes nos 4 projetos completos |
| `examples/*.df` | manual | 44 programas maiores |

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

- **Um *shim* de versão no PATH** — versões lado a lado, pino por projeto
  e `workspace` existem (ver "Os seis últimos itens"). O que não há é um
  atalho no PATH que resolva a versão antes de o Python subir: o
  `dataforge` que se chama é o que está instalado, e é ele que
  redireciona. A lista a consultar antes de afirmar que algo existe é
  `Arcane.Ecossistema.o_que_nao_existe()`, porque ela é **conferida**
  contra o disco.
- **Alocador próprio** — o alocador é o do CPython, e trocá-lo exigiria
  estar fora dele. O que existe é controle do **coletor**
  (`Arcane.Memoria`: ligar, desligar, limiares, congelar, arena) e
  medição da pausa dele (`Arcane.Perfil.gc_pausas`). "Controlar memória"
  e "controlar o coletor" são coisas diferentes, e o projeto prefere
  nomear a diferença.
- **O vínculo genérico é carregado pelo objeto, e cobrado nas duas
  metades.** `c.guardado := "texto"` num `Caixa<Integer>` é recusado em
  **execução** (a instância guarda o vínculo em `DFInstance._tipos`) e
  acusado pelo **`check`** na linha que causa (`generic-field`), com a
  mesma resposta nos dois — inclusive num campo herdado, onde cada
  metade lê uma tabela diferente (`tipos_de_campo` no analisador,
  `tipos_do_cabecalho`/`fields_decl` no interpretador) e a concordância
  é coisa a provar, não a supor. O que continua fora: um campo que é
  `Cluster<T>` em vez de `T` puro (descer na coleção seria impreciso), e
  um objeto sem anotação — sem ela não há vínculo, e é assim que a
  maioria do código cria instância. **Variância declarada não se
  aplica** — ver abaixo, com a medida.
- **Herdar com argumento de tipo** (`blueprint Filha<T> extends Caixa<T>`)
  é erro de sintaxe: o `extends` aceita o nome, não a instanciação. O
  campo genérico herdado funciona porque o parâmetro da filha resolve o
  da mãe pelo **nome**; com nomes diferentes (`Caixa<U>`), o analisador
  cala em vez de adivinhar.
- **Exaustividade além do produto de enums** — o `match` avisa em cinco
  formas, inclusive no padrão **aninhado** (`[Cor.A, x]` sem o `Cor.B`).
  O que fica de fora: uma posição com literal faz a regra calar
  (`[Cor.A, 0]` não cobre `[Cor.A, *]`), e um ramo com **guarda** nunca
  conta como cobertura.
- **Vigia de leitura por EXPRESSÃO** — parar quando um valor é lido
  existe (`r saldo`, `--vigiar-leitura=saldo`, data breakpoint de leitura
  no editor), e ela casa por **nome** ou por nome de campo. O que não há é
  vigiar a leitura de uma expressão composta (`v["k"].campo`). No
  **terminal** as paradas de threads diferentes se enfileiram: um terminal
  é uma conversa só.
- **Bytecode** — continua sendo interpretador de árvore. O que existe é
  **compilação para fechamentos** (`compilador.py`): a árvore é percorrida
  uma vez e vira funções Python, o que tira o despacho do caminho quente.
  Medido: 1,5× a 1,8× conforme a carga. O teto dessa técnica, e o de uma VM
  de bytecode escrita em Python, é ~6,5× — o resto exigiria sair do Python.
- **Sincronização automática** — `Arcane.Concurrent` tem mutex, semáforo,
  barreira, contador atômico e canal bloqueante, mas nada é aplicado sozinho.
  O Kiln atende um pedido por thread: o `Arcane.Database` serializa o acesso
  à conexão (sem isso, a primeira consulta de qualquer servidor estoura), mas
  estado em memória compartilhado entre rotas não é protegido.
- **HTTP/2 e TLS** — o Kiln não tem. Ele roda sobre o `http.server` do
  Python; em produção pública, ponha um nginx ou Caddy na frente.
  **WebSocket e streaming de resposta existem** desde o
  `kiln_tempo_real.py` (`Kiln.ws`, `Kiln.sse`, `Kiln.stream`, `Kiln.sala`),
  com o RFC 6455 falado à mão — esta linha dizia que não, e era a própria
  documentação mentindo sobre a linguagem.
  A Vitrine, porém, não os usa: o "tempo real" dela é
  `V.atualizar_a_cada(n)`, que é por pergunta e não por empurrão.
- **`V.estado.somar` não é atômico entre processos.** A sessão da
  Vitrine pode morar num armazém comum (`sessoes_em :=
  V.sessoes_em_banco(…)`), gravado por chave no fim do pedido: na mesma
  chave, vence a última gravação. A sessão do **Kiln** continua na
  memória do processo.
- **Literal decimal: existe, e é `19.99d`.** O sufixo constrói o valor a
  partir do **texto**, sem passar por float nenhum. `19.99` sem sufixo
  continua sendo `Float` — mudar isso quebraria todo cálculo científico já
  escrito. Misturar `Decimal` com `Float` numa conta é **recusado** de
  propósito, e é por isso que `Decimal` não é um `Number`.
- **Cálculo de fórmula em planilha** — o `Arcane.Excel` grava a fórmula e o
  Excel a resolve ao abrir. Também não lê o `.xls` binário antigo.
- **`receive` sem prazo não espera** — devolve `void` na hora se a fila está
  vazia, e isso é contrato (dois exercícios o afirmam). Para esperar:
  `receive(ms)` ou `receive(void)`. Trocar o padrão não daria erro em
  programa nenhum, daria travamento.
- **`parallel`** roda cada **tarefa** numa thread: uma instrução solta é uma
  tarefa, e um `thread:` aninhado agrupa várias numa tarefa que roda em ordem.
  Ele **espera todas** e, se alguma falhou, levanta o erro **na linha do
  bloco**, com os demais em `.outros` — então `monitor/handle` o pega.
  `thread:` não espera: o erro do corpo é **desenhado na hora** na saída de
  erro, e o programa termina com código diferente de zero.
  Até esta correção os dois faziam `except Exception` e imprimiam uma linha:
  o programa seguia, saía com **0**, e nenhum `handle` via o erro — um CI
  passava verde com metade do trabalho perdida. O `parallel` também
  abandonava as threads depois de 30 s, calado.
- **`frame`, `train`, `predict`** são **açúcar fino** sobre `Arcane.Analytics`
  e `Arcane.Cortex` — não reimplementam nada. `frame` devolve o
  `AnalyticsFrame` de verdade; `train "floresta" using {…}` chama o treinador
  do Cortex com o vault de argumentos nomeados; `predict` chama
  `Cortex.prever`, ou a sua ação. Quem precisa de controle chama o Cortex
  direto e vê todos os parâmetros.
- **`async/await` é concorrente de verdade, mas só para entrada e saída.**
  Chamar uma ação `async` começa o trabalho numa thread e devolve uma
  tarefa; `await` espera. Rede, disco, banco e `sleep` se sobrepõem de
  fato. Trabalho de CPU não: o GIL continua no caminho, e a resposta ali
  é `P.map_processos`, que usa processos de verdade — ver "A travessia
  de processo", abaixo. Até ela ser consertada, essa frase apontava
  para algo que não funcionava.

### Quatro defeitos que só um projeto grande mostra

Achados gerando um projeto de 60 domínios com herança, records, enums,
traits, pipelines e testes — nenhum deles aparece num arquivo de 40
linhas, e os quatro passavam na suíte inteira.

**1. `dataforge test` dizia "Tudo verde" com um `trial` reprovado.**
`crucible` e `trial` são palavras da **linguagem**: um arquivo de teste
normal nunca escreve `adopt Arcane.Crucible`. O corredor procurava
`Crucible.run` em `interp.modules` — vazio nesse caso —, desistia, e o
arquivo caía no ramo "sem ações `test_`, o próprio arquivo é o caso":

```
✓ tests/a_test.df (1/1)
1 passaram em 1 arquivo(s)
Tudo verde.                       código de saída 0
```

`dataforge crucible`, sobre o mesmo arquivo, saía com 1. O repositório
inteiro passava **por acidente**: todas as suítes daqui escrevem o
`adopt`, que era o único caminho em que a busca antiga funcionava. O
projeto de 60 domínios relatava 60 testes onde havia 180.

**2. `root` entrava em laço infinito com três níveis de herança.** Ele
era o pai da classe da **instância**, e não de quem declarou o método:
dentro de `B.v`, o `self` ainda é a instância de `C`, então `root`
voltava a ser `B` e `B.v` chamava a si mesmo. Com dois níveis a conta
dava certo — e **toda herança do repositório tem dois níveis**. Hoje
`_RootProxy` guarda uma fatia da MRO cortada depois de `__dono__`, o
blueprint que declarou o método em execução; com isso o diamante
resolve por C3, como o `super()` do Python.

**3. Um método declarado num `enum` não podia ser chamado.** O parser
aceitava, o interpretador guardava em `DFEnum.methods`, e
`Cor.Verde.hex()` respondia "has no member 'hex'. Use .name, .value or
.index". Código que se escreve, que passa no `check`, e que nunca roda —
pior que um recurso que não existe. O membro não conhecia o enum a que
pertence (ele nasce **antes** dele); hoje conhece, e o `self` do método
é o membro, que é quem tem `.value`.

**4. `given` não publicava o nome, e `monitor` publicava.** O padrão
mais comum que existe não funcionava:

```dataforge
given n % 2 is 0:
    rotulo := "par"
otherwise:
    rotulo := "impar"
out rotulo          // 'rotulo' is not defined
```

A decisão já estava tomada e escrita na docstring de
`exec_MonitorBlock` — "em Python, Java e JavaScript, `try` não cria
escopo" —, e o `given` ficou de fora.

A correção tem duas metades, e as duas importam. O **nome** sai do ramo;
o **tipo** não. Os ramos são mutuamente exclusivos, e herdar o tipo de
um no seguinte acusa código certo — `packages/modelo` tem exatamente
esse caso, e virou "Cannot index a value of type Void" num `otherwise`
que nunca roda depois do ramo anterior. O tipo que volta é `UNKNOWN`,
que é o que o analisador sabe de verdade.

E ela precisou de **três** arquivos: `interpreter.py`, `typechecker.py`
e `compilador.py`. Esquecer o terceiro fez o `check` aprovar e a
execução falhar — o construtor compilado espelha `exec_GivenBlock`, e
divergir dele faz a linguagem responder duas coisas conforme a
compilação de fechamentos esteja ligada. O teste roda os dois modos.

### A travessia de processo — o único caminho para mais de um núcleo

`map_processos` era a única forma de usar mais de um núcleo, e ela
**falhava sempre**. A mensagem culpava quem escreveu:

```
erro[DF1001]: this action cannot cross into another process: Can't get
              local object 'ArcaneConcurrent.__new__.<locals>.<lambda>'
  dica: declare a ação no topo do arquivo
```

A ação estava no topo do arquivo. O objeto que o `pickle` não copiava
era **um lambda da própria biblioteca**, alcançado pela cadeia de
escopos: uma `DFAction` guarda o fechamento, no topo o fechamento é o
global, e o global tem os 228 embutidos e os módulos já adotados.

`travessia.py` não copia o fechamento: copia a **declaração**.

| Vai | Como |
|---|---|
| a ação | a árvore do corpo, os parâmetros, os padrões |
| o que ela lê e não cria | `nomes_livres` varre o corpo **em ordem** |
| record, enum, blueprint, outras ações | tabela de declarações, por índice |
| um módulo da stdlib | **pelo nome** — o filho o carrega de novo |
| os dados | pela mesma tabela: mil pedidos levam um índice, não mil cópias do tipo |

Do outro lado, um interpretador novo remonta tudo num escopo próprio.
Medido, 8 blocos de CPU em 10 núcleos: série 1607 ms, threads 1654 ms
(**0,97x** — o GIL), processos 466 ms (**3,45x**).

Quatro decisões que valem lembrar:

1. **O pacote vai uma vez por processo**, no `initializer` do pool, e o
   que o pool mapeia é só a **marca**. Mandado junto de cada lote, um
   record de trinta campos seria copiado tantas vezes quantos forem os
   lotes — mais dado atravessando do que trabalho sendo feito.

2. **A varredura de nomes livres captura de mais, de propósito**, e por
   isso um nome que não atravessa **não levanta na hora**: o motivo
   fica guardado, e só vira erro quando o filho reclama daquele nome.
   Levantar cedo faria um banco aberto no arquivo impedir uma ação que
   nem o menciona de usar os outros núcleos.

3. **A ordem é o que a torna precisa.** `total := 0` antes de
   `total + x` liga o nome, e dali em diante ele é local. Uma
   atribuição **composta** (`total += x`) lê antes de ligar, e por isso
   conta como leitura — sem essa distinção, um acumulador de fora
   viraria "'total' is not defined" dentro do processo filho.

4. **O tipo que volta é o MESMO deste processo.** O empacotador guarda
   o objeto original junto do índice, e o resultado é decodificado com
   ele. Se o filho devolvesse uma cópia do `record`, `with` — que
   confere os campos contra o tipo — recusaria o próprio resultado.
   Guardar o objeto também é o que impede `id()` de ser reaproveitado
   por outro depois de uma coleta, que é o bug do cache da Vitrine.

O erro que acontece lá dentro volta como erro daqui, com `nota`
dizendo que aconteceu em outro processo — a pilha e a linha não
sobrevivem à cópia, e sem essa nota o erro parece ter acontecido na
linha do `map_processos`, a única que este processo executou.

**E há um pool que sobrevive entre chamadas.** `map_processos` abre,
usa e fecha; iniciar um processo custa mais de cem milissegundos, o
que num servidor acontece *por pedido*. `P.pool_processos()` paga uma
vez — medido: 180 ms na primeira chamada, **82 ms na segunda**. O
`fechar()` é explícito porque o contrário deixa processos ociosos, e
`P.processo(acao, …)` é a chamada avulsa: o `thread` da linguagem, num
núcleo de verdade.

O pool reaproveitado é o único que manda o pacote **junto do lote**, e
não pelo `initializer`: quando a próxima ação aparece, os processos já
estão de pé, e `initializer` não roda de novo. O filho ainda o abre
uma vez só — `_ABERTOS` é por marca.

`tests/test_travessia.py` são 30 testes, e dois **medem**: cobram razão
contra a série da mesma máquina, e o do paralelismo só com quatro
núcleos ou mais. Os exercícios 238–240 demonstram os três lados.

### Chamada de cauda

`yield` em DataForge **devolve e encerra**, então `yield f(…)` não tem
nada depois dele: o quadro existe só para repassar o resultado. `cauda.py`
marca esses `yield`, e `_corpo_com_salto` reusa **um** quadro em vez de
empilhar mil.

É um caminho **separado** de `_corpo_da_acao`, e não uma mudança nele: a
esmagadora maioria das ações não tem recursão de cauda e não pode pagar
por um laço, um `try` a mais e um estado por thread que nunca vai usar.

Quatro recusas, todas por análise, antes de rodar:

| Recusa quando | Porque |
|---|---|
| há `defer` na ação | ele roda na saída do quadro, e o salto reusa o quadro |
| o `yield` está dentro de `monitor` | um `handle` acima precisa ver o que a chamada levanta |
| a recursão é indireta (`f`→`g`→`f`) | a análise olha uma ação por vez |
| **todo** `yield` da ação é cauda | a ação nunca devolve; virar laço mudo seria pior que o `StackOverflowError` |

A última é a menos óbvia e a mais importante: sem ela,
`action r(n): yield r(n + 1)` deixaria de dar erro e passaria a travar.

A marca é por **nome**, e a identidade é conferida na hora — `f := outra`
dentro do corpo, ou um método substituído na filha, fariam o salto reusar
o quadro errado.

### A ponte para o Python

`adopt Python.numpy as np` traz qualquer biblioteca do Python. Quatro
coisas que valem lembrar antes de mexer em `ponte.py`:

1. **`Python` é espaço de nomes reservado**, resolvido em
   `_resolver_modulo` **antes** da stdlib e dos arquivos vizinhos. Um
   `Python.df` no disco não pode sequestrar o import.

2. **A ponte não converte.** Um `ndarray` continua um `ndarray` — é o
   que faz `a * 2` ser a conta vetorizada do numpy em vez de um laço
   sobre um milhão de posições. Isso só funciona porque o interpretador
   trata objeto estranho por **protocolo**, e não por tipo: membro,
   método, índice, `len`, iteração, aritmética, texto e verdade já
   passavam assim. Se alguém um dia trocar protocolo por `isinstance`,
   a ponte quebra inteira — `test_o_objeto_do_python_funciona_por_protocolo`
   existe para denunciar.

3. **Número é a exceção do `typeof`.** `np.int64` não é subclasse de
   `int`, mas faz conta de inteiro, então `_type_of` responde `Integer`
   por `numbers.Integral`. Não há nada de numpy no interpretador —
   `Fraction` e `Decimal` entram pela mesma porta.

4. **A mensagem de ausência nomeia o Python exato.** O instalador cria
   uma venv em `~/.dataforge`, e `pip install` no terminal instala em
   outro. E no executável único não há `pip` nenhum: ali a mensagem
   aponta `pip install dataforge-lang`, e não um comando que nunca
   funcionaria.

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
