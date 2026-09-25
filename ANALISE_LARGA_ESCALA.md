# DataForge 1.1.1: análise completa e prontidão para larga escala

Data: 2026-09-25. Tudo aqui foi **medido ou reproduzido** nesta máquina
(macOS, Python 3.13.9, `.venv` em modo editável apontando para o repositório).
Cada bug traz a reprodução mínima, a causa com `arquivo:linha` e a correção
sugerida.

**Atualização (mesmo dia): B1, B2, B3, B4, B11 e D1 foram corrigidos**, cada
um com teste que falha sem a correção. Ver a nota "Corrigido" em cada seção,
a §7 e a §8.

---

## 0. Resumo

**O estado de base é verde.** `pytest`: 5921 passaram, 16 pulados (5 min 56 s).
Os 399 exercícios, os 18 capítulos da trilha, os 44 exemplos e o `check` nas
cinco pastas também passam, com zero erros.

**Achei 12 defeitos.** Um é crítico: **módulos não são isolados**. Uma ação
de uma biblioteca lê e **sobrescreve** variáveis globais do programa que a
importou. Outro é alto: **o tipo declarado não vale na reatribuição**. Os
demais são de diagnóstico e de acabamento.

**Está pronta para larga escala?** Para projetos **médios** (até algumas
dezenas de milhares de linhas, time pequeno, carga de I/O), está: o
ferramental é o ponto forte e já está maduro. Para **grande escala** ainda
não, por três motivos:

1. ~~**O bug de isolamento de módulos.**~~ **Corrigido nesta sessão** (§7).
   Antes, num projeto de 200 arquivos, qualquer ação que usasse como nome
   local o nome de uma global de outro arquivo corrompia aquela global, sem erro.
2. **O sistema de tipos tem furos.** A anotação é conferida na declaração, e
   não depois dela (§2, B2). Refatorar com segurança depende disso.
3. **O desempenho é de 13 a 150 vezes o do CPython.** Isso limita serviços com
   carga de CPU, não os de I/O (§4.1).

---

## 1. O que foi verificado

| Verificação | Resultado |
|---|---|
| `python3 -m pytest tests/ -q` | **5921 passaram, 16 pulados**, 5 min 56 s |
| `exercicios/run_all.py` | 399/399 |
| `trilha/run_all.py` | 18/18 |
| `examples/*.df` | 44/44 rodam |
| `dataforge check` em examples, exercicios, projetos, packages e trilha | 0 erros (3 + 51 + 0 + 1 + 4 avisos) |
| `dataforge test` nos 5 projetos e 20 pacotes | todos verdes, exceto `packages/documento` sem `dataforge install` antes (ver B10) |
| Projeto sintético de **300 arquivos** encadeados por `adopt` | `check` em 0,44 s, `run` em 0,21 s; erros entre módulos acusados (tipo de parâmetro, campo de record, membro inexistente, aridade) |
| ~25 programas de sondagem sobre semântica, stdlib, concorrência, web e dados | os achados estão abaixo |

Tamanho da implementação: 142 mil linhas de Python em `dataforge/`
(`interpreter.py` com 10.309, `parser.py` com 4.503, `typechecker.py` com 5.374),
62 mil linhas de testes e 570 arquivos `.df` no repositório.

---

## 2. Bugs encontrados

A gravidade é pensada para um projeto grande.

### B1: CRÍTICO. Módulos não são isolados: uma biblioteca lê e escreve as globais de quem a importa

> **Corrigido.** `Interpreter._escopo_de_modulo` cria o escopo do módulo só
> com as embutidas **originais** (guardadas em `_embutidas_originais` na
> partida), levando junto a marca `embutidas`. Testes em
> `tests/test_resolucao.py`: escrita isolada, leitura recusada, o `count`
> embutido chegando ao módulo mesmo com o main tendo redefinido `count`, e
> o `len := 1` de uma ação que não apaga o `len` do módulo, nos dois modos
> de compilação. A descrição abaixo é o estado **antes** da correção.

```dataforge
// lib2.df
action le():
    yield segredo            // nome que NÃO existe em lib2.df
action escreve():
    config := "SOBRESCRITO"  // a intenção é uma variável local
relay le, escreve
```

```dataforge
// main.df
segredo := "do main"
config := "original"
adopt ./lib2 as L
out L.le()       // "do main": a biblioteca leu a global de quem importou
L.escreve()
out config       // "SOBRESCRITO": a global do main foi trocada
```

O caso realista é pior: `lib.df` tem `action soma(xs): total := 0 …`, e o
`main.df` tem uma global `total`. Cada chamada a `L.soma` **zera e reescreve**
o `total` do main. Reproduzido: `total := 7` no main, e depois de
`L.soma([1,2])` o `total` do main vale `3`. Vale também com o `adopt` antes da
atribuição, e com a compilação de fechamentos desligada.

O `check` **acusa** `Undefined name 'segredo'` em `lib2.df`, e a execução
aceita. As duas metades discordam, e é a execução que está errada.

**Causa.** `dataforge/interpreter.py:10288`:

```python
mod_env = self.global_env.child(f"<module {module_name}>")
```

O escopo do módulo é filho do escopo global do **programa principal**, e esse
escopo guarda duas coisas: os 231 embutidos (`global_env.embutidas`) e as
variáveis de topo de quem importou. Somado à regra de que `:=` dentro de uma
ação escreve no nome de fora quando ele existe (armadilha já documentada),
o resultado é escopo dinâmico entre arquivos.

**Por que é crítico em larga escala.** O bug depende de **coincidência de
nomes** entre arquivos que ninguém lê juntos. Nomes como `total`, `config`,
`itens`, `resultado`, `conexao`, `i` e `n` aparecem em qualquer projeto. O
sintoma aparece longe da causa, só na ordem de execução certa, e sem erro
nenhum. É o mesmo tipo de defeito que torna `var` global do JavaScript antigo
impraticável em base grande.

**Correção prototipada, 5 linhas.** O módulo passa a nascer de um escopo só
com os embutidos:

```python
mod_env = Environment(name=f"<module {module_name}>")
_g = self.global_env
for _n in getattr(_g, 'embutidas', ()) or ():
    if _n in _g.variables:
        mod_env.set_local(_n, _g.variables[_n])
```

Resultado do protótipo, rodado numa cópia do repositório:

| Conjunto | Com a correção |
|---|---|
| 399 exercícios | 399/399 |
| 44 exemplos | 44/44 |
| `check` nas 5 pastas | 0 erros, os mesmos avisos |
| 5 projetos + 20 pacotes (`dataforge test`) | todos verdes (o `documento` com a mesma ressalva de B10) |
| `pytest` | ver §2.1 abaixo |

Nenhum programa do repositório dependia do vazamento. Uma implementação mais
limpa que a do protótipo é separar `builtins_env` de `global_env` no
`__init__` (hoje os dois são o mesmo objeto, `interpreter.py:2205` e o laço de
`get_builtins()` logo abaixo) e pendurar os módulos em `builtins_env`. Merece
um teste em `tests/test_resolucao.py` com os dois casos acima: leitura e escrita.

#### 2.1 Resultado do pytest sobre o protótipo

`5913 passaram, 4 falharam, 20 pulados`. Cada falha foi atribuída rodando o
mesmo teste na cópia **com** e **sem** a correção:

| Teste | Causa |
|---|---|
| `test_empacotamento.py` (2 testes) | falham também **sem** a correção: a cópia não tem a extensão compilada. É ambiente, não a correção |
| `test_paginas_novas_rodam.py::…[concorrencia/medir#9]` | passou na segunda rodada: oscilação de tempo |
| `test_conclusao.py::test_a_pagina_e_o_que_o_gerador_produz` | causada pela correção, mas **não é regressão**: `doc/conclusao.html` conta as linhas da implementação, e o protótipo acrescentou 4 (142.268 → 142.272). Resolve rodando `tools/gerar_conclusao.py` |

**Conclusão: nenhuma regressão de semântica.** A correção pode entrar junto
com um teste novo e a página regenerada.

### B2: ALTO. O tipo declarado não vale depois da declaração

> **Corrigido** (§8). O tipo mora em `Environment.tipos`, e `set` o confere
> em toda escrita. Parâmetro, campo do cabeçalho, campo do corpo (e o padrão
> dele) e campo herdado também. O `check` acusa antes (`tipo-na-reatribuicao`,
> `tipo-do-campo`). A descrição abaixo é o estado **antes** da correção.

```dataforge
x: Integer := 1
x := "a"                    // aceito: check calado, execução calada
out x                       // a

action f(a: Integer):
    a := "s"                // aceito
    yield a

xs: Cluster<Integer> := [1]
xs := ["a"]                 // aceito
xs.append("x")              // ESTE é recusado, pelo check e pela execução

blueprint B(n: Integer):
    action f():
        yield 1
b := spawn B(1)
b.n := "texto"              // aceito: o campo tipado do cabeçalho não confere a escrita
```

A referência (`doc/REFERENCIA.md` §3.2) diz que as anotações são "verificadas
em tempo de execução", e quem lê entende que a variável **tem** aquele tipo.
Hoje o contrato vale só no instante da declaração. A incoerência é interna à
linguagem: o conteúdo de um `Cluster<Integer>` é protegido no `append`, mas a
variável não é protegida na reatribuição. Num `record`, o campo tipado é
conferido; no campo do cabeçalho de um `blueprint`, não.

**Por que importa em larga escala.** A anotação é o que permite refatorar com
confiança. Se ela só vale na primeira linha, o leitor não pode confiar nela
no resto da ação.

**Correção sugerida.** Guardar o tipo declarado no `Environment`, ao lado do
valor, como já é feito com `steady`. Conferir em `Assignment` (interpretador,
compilador de fechamentos e `typechecker`, os três). Para o campo do
cabeçalho, aplicar em `_escrever_membro` a mesma conferência de
`tipos_do_cabecalho` que o `spawn` já faz. O caminho quente não pode pagar
por isso: só nomes anotados carregam o tipo (o padrão `None` que o projeto já
usa em `DFAction.extras`).

### B3: MÉDIO. Na pilha de chamadas, o quadro de uma chamada entre módulos sai com linha 0

> **Corrigido.** A causa exata era outra: o nó não chegava nulo. A chamada
> `L.f()` passava por `_invocar`, que chamava a ação como função Python, e
> `DFAction.__call__` inventava um `_FakeNode` de linha 0. Agora
> `_chamar_metodo_cru` chama `_call_action` direto, com o nó da chamada,
> quando o membro é uma `DFAction`. Teste nos dois modos de compilação.

```
em falha               mf.df:0      ← deveria ser mf.df:4
```

Dentro do mesmo arquivo a linha sai certa (`loc.df:4`, `loc.df:6`). **Causa:**
`interpreter.py:9304-9309`: quando `node` é `None`, o quadro é empilhado com
`linha = coluna = 0`, e a chamada `L.falha()` a um membro de módulo chega por
esse caminho. Em projeto grande quase toda chamada atravessa módulo, então é
justamente a pilha que se lê para depurar que perde a informação. A correção é
passar o nó da `MethodCall` até `_corpo_da_acao` no ramo de membro de módulo.

### B4: MÉDIO. Um erro léxico dentro de `$"{…}"` aponta para a linha 1

> **Corrigido.** `_parse_sub_expression` captura `LexError` e o relança com
> a posição da string, mantendo a classe (e o código DF0102). Teste em
> `tests/test_regressoes.py`.

```dataforge
a := 1
b := 2
c := 3
out $"valor {a ? b}"
```

```
erro[DF0102]: Unexpected character: '?'
  ┌─ q.df:1:3          ← a linha certa é 4
```

Erros **sintáticos** (`{a + }`) e de **nome** saem com a linha certa. Só o
**léxico** escapa. **Causa:** `parser.py`, em `_parse_sub_expression`: o
`except ParseError` não captura `LexError`, e o erro sobe com a posição
relativa ao trecho. **Correção:** `except (ParseError, LexError)`, com a
mesma reposição que o ramo de `ParseError` já faz, e um teste.

### B5: MÉDIO. Mensagens de erro vazam o Python, e a camada de idioma cobre cerca de metade

Numa bateria de 20 erros comuns, rodada no idioma padrão (`pt`), **11 saíram
em inglês** e 5 citavam termos ou tipos do Python:

| Chamada | Mensagem |
|---|---|
| `from_json("{x")` | tipo `ValueError`, e o texto do `json` do Python: `Expecting property name enclosed in double quotes: line 1 column 2 (char 1)` |
| `int(void)` | `int() argument must be a string, a bytes-like object or a real number, not 'Void'` |
| `[].pop()` | `pop: pop from empty list` (o `list` que a regra do projeto proíbe) |
| `range(1, 5, 0)` | `range() arg 3 must not be zero` |
| `format(1.5, 2)` | `'Float' object has no attribute 'format'` |
| `{"a": 1}` alterado durante um `cycle` | `dictionary changed size during iteration` |
| `max([])`, `10 % 0`, `"a".split("")` | em inglês: `This collection is empty.`, `Remainder by zero.`, `The separator is empty.` |
| `1 + void` | título em inglês, **nota em português, dica em inglês**, no mesmo erro |
| erro de sintaxe | `Era esperado COLON, got OUT ('out')`: meio traduzido, com nome de token interno |
| módulo não achado | `Module 'texto' not found … next to main.df`, em inglês e citando o arquivo errado |

`dataforge idioma` informa **"pt 100%"**. O número mede a cobertura do
**catálogo** (53 inteiras e 62 pedaços), e não a das mensagens que a linguagem
emite. É o tipo de medida que esconde o buraco, o que o próprio `CLAUDE.md`
alerta em "o fallback certo é também o que esconde o buraco".

**Correção sugerida:**
- (a) Envolver as funções embutidas num tradutor de exceção: `json.JSONDecodeError`
  vira um `ParseError` da linguagem, `ValueError` e `TypeError` do CPython viram
  `ConversionError` e `TypeError_` com texto próprio.
- (b) Uma trava de teste que rode uma bateria de erros como a acima e exija que
  nenhuma mensagem contenha `list`, `dict`, `int()`, `argument`, `object has no
  attribute` ou `NoneType`.
- (c) Fazer `dataforge idioma` informar a cobertura sobre as mensagens
  **emitidas** por essa bateria, e não sobre o catálogo.

### B6: BAIXO. "Membro inexistente" não usa a categoria que existe para ele

O catálogo tem `UndefinedMemberError` (DF0402, subclasse de `NameError`)
exatamente para membro inexistente. Mas `"abc".index("z")`, `[1].nada()`,
`R(1).b` num record, `3.nada` e `void.x` levantam todos o `NameError`
genérico. Só o `AttributeError` vindo de **dentro** de uma embutida (por
exemplo `format(1.5, 2)`) sai como `UndefinedMemberError`. Resultado: um
`handle UndefinedMemberError` **não pega** o caso comum, `obj.naoExiste()`.
`handle NameError` pega os dois, então nada quebra calado, mas a categoria
específica fica praticamente inalcançável. Ligado a isso: o
nome é `index_of` em String e `index` em Cluster; `pop` existe como método de
Cluster, mas não de Vault (em Vault é a embutida `pop(v, k)`).

### B7: BAIXO. Lambda literal entre parênteses não pode ser chamado na hora

```dataforge
out (lambda a: a)(1)     // erro de sintaxe: "Unexpected LPAREN after a complete statement"
```

`(f)(3)`, `mk()(1)` e `(xs)[0]` funcionam. **Causa:** `parser.py:3751`: a
chamada pós-fixa só é aceita depois de `Identifier`, `FunctionCall`,
`MethodCall`, `IndexAccess` ou `MemberAccess`, e `LambdaExpression` não está na
lista. Dentro de outro lambda (`lambda => (lambda a: a)(1, 2)`) a leitura muda
e sai `'(1, 2)' is not callable`, que confunde ainda mais.

### B8: BAIXO. Aviso que cita um `otherwise` inexistente

```dataforge
action g() -> Integer:
    given yes:
        yield 1
```

```
aviso: this condition is always yes: the 'otherwise' body never runs
```

Não há `otherwise` nesse código. Além disso, o aviso sai em inglês.

### B9: BAIXO. Dez linhas de `adopt` deformadas nos projetos de referência

```
projetos/analise-vendas/src/main.df:11:        adopt./ leitor as L
projetos/analise-vendas/tests/leitor_test.df:4: adopt../ src / leitor as L
projetos/api-links/src/main.df:11:             adopt./ encurtador as E
…  (10 linhas em 4 projetos)
```

É resíduo do defeito do `fmt` corrigido em `e97c6a6`: o formatador atual
**não** deforma mais (conferido, e é idempotente). Mas as linhas ficaram, e o
parser as **aceita**. Isso mostra que o caminho de um `adopt` tolera espaço
em volta de `/`, e um código de referência ensina a forma errada. A correção é
reescrever as 10 linhas. Vale considerar recusar espaço dentro do caminho,
como já é feito com o hífen (`_segmento_de_caminho`).

### B10: BAIXO. `dataforge test` não diz que as dependências não estão instaladas

`packages/documento` declara `texto = "^1.0.0"` e, sem `forge_modules/`,
`dataforge test` responde `1 falharam` com `Module 'texto' not found`. Depois
de `dataforge install`, passa. O corredor poderia conferir o `forge.toml`
contra `forge_modules/` e dizer "rode `dataforge install`" em vez de reprovar.

### B11: BAIXO. O mapa de código do `CLAUDE.md` está defasado

> **Corrigido.** Os três tamanhos foram atualizados.

O `CLAUDE.md` diz `interpreter.py 2703`, `parser.py 1941` e `typechecker.py
1752`. Hoje são 10.309, 4.503 e 5.374 linhas. Não afeta a linguagem, mas o
mapa existe para orientar quem mexe no código, e ele subestima o tamanho do
núcleo em 3 a 4 vezes.

### B12: BAIXO. Rodar a suíte altera um arquivo versionado

Depois de `python3 -m pytest tests/`, o `git status` mostrou
`packaging/windows/winget/EstevamSouza.DataForge/EstevamSouza.DataForge.installer.yaml`
modificado: só o `ReleaseDate` mudou para a data de hoje. Um teste (ou um
gerador chamado por `tests/test_windows.py` ou `tests/test_api_e_marca.py`)
escreve na árvore de trabalho. Pode entrar num commit por engano, e faz um
repositório limpo parecer sujo. O gerador deveria escrever numa pasta
temporária no modo de teste, ou tirar a data do release, e não do relógio.
(Revertido com `git checkout` depois desta análise.)

**E não é o único.** A suíte também reescreve páginas geradas em
`site/app/docs/exercicios/` quando um exercício muda. O conteúdo que ela
escreve é o certo, mas um teste não deveria editar a árvore de trabalho.

---

## 3. Decisões de desenho que custam caro em larga escala

Isto não é bug: é comportamento documentado ou intencional. Mas cada item é
uma fonte provável de defeito num projeto com muitas pessoas e muitos arquivos.

| # | Comportamento (medido) | Risco | Sugestão |
|---|---|---|---|
| D1 (**corrigido**, §8) | Dentro de uma ação, `total := 0` **reescreve** a global `total` do arquivo, se ela existir | é a metade "dentro do arquivo" de B1; o `check` e o `lint` ficam calados | um aviso do `lint`, `atribuicao-escreve-global`, quando uma ação atribui com `:=` a um nome de topo sem nunca lê-lo antes. Hoje a saída é `shadow`, e ninguém lembra de usá-la |
| D2 | `match` sem ramo que case devolve `void` calado (só avisa quando é enum) | valor inesperado vira `void` e explode três chamadas depois | um `MatchError` quando nada casa e não há `default`, ou pelo menos um aviso do `check` para `match` sem `default` em ação com `-> Tipo` |
| D3 | `1 + "a"` dá `"1a"`, `yes + 1` dá `2`; o `check` não avisa | concatenação acidental de número com texto em relatório e em SQL | aviso `concatenacao-implicita` no `check` quando um lado é `Integer`/`Float` literal ou tipado; recomendar interpolação |
| D4 | `sleep` recebe **milissegundos**, e `time()` devolve **segundos** | `sleep(0.2)` esperando 200 ms espera 0,2 ms; aconteceu nesta análise | aceitar uma duração com unidade (`sleep(ms := 200)`), ou avisar no `check` quando o argumento literal for menor que 1 |
| D5 | `round(0.5)` dá `0.0` e `round(2.675, 2)` dá `2.67` (arredondamento bancário do Python), e o resultado é `Float` | linguagem voltada a pt-BR e a dinheiro: quem espera o arredondamento escolar erra centavos | documentar em destaque, oferecer `arredondar(x, casas, "meio-para-cima")`, e recomendar `19.99d` para dinheiro |
| D6 | Teto de 1000 quadros de recursão (fora da chamada de cauda) | percorrer uma árvore de 5 mil nós falha | já documentado; considerar subir o teto quando o `sys.setrecursionlimit` permitir |
| D7 | `defer` num laço acumula até a saída da **ação** | abrir mil arquivos num laço segura mil descritores | é a semântica do Go; um aviso do `lint` para `defer` dentro de `cycle` ajudaria |
| D8 | `out [1, "1"]` imprime `[1, 1]` | na depuração, texto e número ficam iguais na tela | fazer o `str` de coleção usar `repr` nos itens, como Python e JS fazem |
| D9 | Nomes: `every`/`some` em vez de `all`/`any`; sem `hex`, `bin`, `divmod`; `char` em vez de `chr` | atrito para quem vem de outra linguagem | apelidos (a linguagem já aceita sinônimos de tipo) |
| D10 | Módulos com o mesmo papel: testes em `Crucible`, `Arcane.Test` e `trial`; dados em `Arcane.Data`, `Arcane.Analytics` e `Arcane.Quadro`; banco em `Arcane.Database` e `Arcane.Forge`; HTTP em `Arcane.Http` e `Kiln` | num time grande, cada pessoa escolhe um, e o projeto passa a ter três | marcar os antigos como obsoletos com `Arcane.Evolucao`, e indicar **um** caminho oficial por necessidade no `/docs` |
| D11 | Corrida de dados em escrita concorrente | quatro `parallel` somando num vault: **60.087 de 80.000** | já documentado. O `check` avisa em `route` (confirmado), mas **não** quando a escrita está numa ação chamada de dentro do `parallel`, que é a forma mais comum |

---

## 4. Prontidão para larga escala, por dimensão

### 4.1 Desempenho (medido)

| Carga | DataForge | CPython 3.13 | Razão |
|---|---|---|---|
| `fib(25)` recursivo | 0,66 s | 0,0045 s | ~150× |
| laço de 1 milhão com soma | 0,42 s | 0,033 s | ~13× |
| 200 mil incrementos num vault | 0,47 s | n/d | |
| 200 mil `record` criados | 0,91 s | n/d | 4,5 µs cada |
| 200 mil `spawn` + 200 mil chamadas de método | 0,38 s + 0,46 s | n/d | |
| Quadro com **1 milhão de linhas**: montar | 1,5 s | n/d | 170 MB de RAM |
| Quadro com 1 milhão: `onde` + `agrupar` + `resumir` | 1,06 s | n/d | |
| Kiln, rota trivial, 50 clientes, 2000 pedidos | **~1.800 req/s**, 2000/2000 com 200 | n/d | |
| `async`: 5 tarefas de 200 ms | 0,2 s no total | n/d | o I/O se sobrepõe de fato |
| `map_processos` | funciona | n/d | a saída real para CPU |

**Leitura:**
- **Serviço de I/O** (API, integração, bot, ETL que espera banco e rede) cabe
  bem. 1.800 req/s por processo atende a maior parte dos sistemas internos, e
  dá para escalar horizontalmente atrás de nginx.
- **Carga de CPU** (cálculo pesado, milhões de objetos por pedido) fica de 13 a
  150 vezes atrás do Python. A saída hoje é a ponte (`adopt Python.numpy`),
  `map_processos`, ou escrever o trecho quente em Python.
- **Dados:** 1 milhão de linhas em cerca de 2,5 s atende relatório, mas não é
  analítico interativo. O pedido do `TODO.md` ("1 milhão com alta
  performance") exige um backend colunar nativo: numpy/arrow pela ponte, ou
  Polars.

### 4.2 Sistema de módulos

**Forte:** `relay` explícito, apelidos, import seletivo, ciclo detectado no
`check`, resolução centralizada em `resolucao.py`, e o `check` atravessando
arquivos com tipos de parâmetro e de retorno.

**Fraco:** B1. É o item número um desta lista.

### 4.3 Tipos

**Forte:** tipagem gradual com conferência em execução, genéricos com limite,
tipos nomeados, uniões, refinamentos, opacos, literais, `Decimal` exato, e
exaustividade de enum, inclusive aninhada.

**Fraco:**
- B2: a reatribuição não é conferida.
- O `check` é otimista de propósito. Nesta análise ele **deixou passar**
  `len(3)`, `v["a"].upper()` com `v := {"a": 1}` literal, e `k(3)` numa ação que
  faz `v.upper()`. Isso é coerente com a filosofia de "zero falso alarme",
  mas significa que, para um projeto grande, o `check` não substitui testes.
- Falta um modo **estrito por arquivo** (`// df: estrito`) em que parâmetros
  sem tipo sejam erro e `Any` seja explícito. É o caminho que TypeScript e mypy
  seguiram para bases grandes.

### 4.4 Concorrência

**Forte:** threads, `parallel` com erro propagado, `async/await` real para
I/O, processos com travessia de declaração, laço de eventos com fibras, STM e
canais.

**Fraco:**
- Não há sincronização automática (D11).
- O Kiln atende com uma thread por pedido e não tem HTTP/2 nem TLS
  (documentado; pede proxy na frente).
- O aviso de escrita concorrente para na fronteira da ação.

### 4.5 Ferramental

É o ponto mais maduro do projeto: `check`, `lint`, `fmt` (idempotente),
`test` com cobertura e mínimo, depurador de terminal e DAP, LSP, `profile`,
`big-o`, `oop`, `abi` (semver pela superfície), `devops` (Dockerfile, k8s e CI
gerados), gerenciador de pacotes com lock e sha256, registro estático, e
binários para 4 plataformas.

Faltam três coisas para uso em grande escala:
- **`check` incremental ou em modo daemon.** Hoje são 0,44 s para 300
  arquivos pequenos. Com 3 mil arquivos reais o editor vai sentir.
- **Monorepo:** `workspace` só lê e não instala. Instalação compartilhada e
  execução de testes afetados pelo diff ainda não existem.
- **Um relatório único de qualidade para CI** (`dataforge ci`) que junte
  `check --strict`, `lint`, `fmt --check`, `test --minimo` e `abi` com saída
  SARIF ou GitHub.

### 4.6 Ecossistema

São 20 pacotes no registro, todos escritos pelo projeto. A ponte para o Python
é o multiplicador real: tudo do PyPI fica acessível. O que falta é
**comunidade**: exemplos de projeto grande (mais de 50 arquivos, com camadas),
guia de arquitetura e, principalmente, o registro aceitando publicação de
terceiros com revisão.

### 4.7 A própria implementação

`interpreter.py` com 10.309 linhas num arquivo é um risco de manutenção para
a linguagem. Toda correção de semântica passa por três lugares
(interpretador, compilador e typechecker), e o `CLAUDE.md` registra vários
casos em que um deles ficou para trás. Dividir `interpreter.py` por área
(expressões, instruções, chamadas, OOP, módulos, erros) reduziria o custo de
cada correção futura.

### 4.8 Veredito

| Cenário | Pronta? |
|---|---|
| Scripts, automação, ETL, bots, ferramentas internas | **sim** |
| API ou sistema web de porte médio (até ~50 arquivos, time de 1 a 5 pessoas) | **sim**, com nginx na frente e cuidado com estado entre rotas |
| Dashboards e apps de dados (Vitrine) | **sim** para até ~1 milhão de linhas |
| Sistema grande (centenas de arquivos, vários times) | **ainda não**: B1 já foi corrigido; falta B2, e depois o modo estrito |
| Serviço com carga de CPU e muitas requisições por segundo | **não**: é limite do modelo interpretado sobre Python |
| Frontend, mobile ou WASM nativo | **não existe** (ver §5, P3) |

---

## 5. O que falta para a linguagem ser "completa", por prioridade

### P0: corrigir antes de recomendar para projeto grande
1. ~~**B1:** isolar módulos.~~ **Feito.**
2. ~~**B2:** o tipo declarado vale em toda reatribuição, em variável, parâmetro
   e campo do cabeçalho.~~ **Feito.**
3. ~~**B3 e B4:** linha certa na pilha entre módulos e no erro léxico da
   interpolação.~~ **Feito.**
4. ~~**D1:** aviso para `:=` em ação que escreve uma global sem lê-la.~~ **Feito.**

### P1: confiança em base grande
5. **B5:** tradutor de exceções nas embutidas, trava contra termos do Python, e
   `dataforge idioma` medindo mensagens emitidas.
6. **Modo estrito por arquivo ou por projeto** (`[check] estrito = true` no
   `forge.toml`): parâmetro sem tipo vira erro, e `match` sem `default` vira
   erro.
7. **D2:** `MatchError` quando nada casa.
8. **D11:** o aviso de escrita concorrente seguindo uma chamada de um nível
   (a ação chamada diretamente de um `parallel` ou `thread`).
9. **D10:** um caminho oficial por necessidade, com os módulos duplicados
   marcados como obsoletos.

### P2: escala de equipe e de código
10. `check` incremental ou em daemon, reaproveitando o `cache.py`.
11. `dataforge ci` com saída SARIF.
12. Monorepo: instalação compartilhada no `workspace`, e testes afetados
    pelo diff.
13. Um projeto de referência grande (mais de 50 arquivos, com camadas de
    domínio, aplicação e infraestrutura, e testes) em `projetos/`, rodando no
    CI.
14. Dividir `interpreter.py`.
15. Registro com publicação de terceiros, revisão e assinatura.

### P3: o que o `TODO.md` pede (visão de longo prazo)

Sobre as ambições registradas no `TODO.md`, uma leitura honesta:

- **AOT, binário "ultrarrápido" e milhões de req/s:** o binário único já
  existe (PyInstaller), mas ele carrega o CPython junto e não fica mais rápido.
  Chegar perto de Go ou Rust exige um **backend novo**: bytecode numa VM em
  Rust, ou compilação para LLVM ou Cranelift. É um projeto do tamanho da
  linguagem inteira. Um passo intermediário realista é compilar o HIR para
  Python (`.py` gerado), o que tira o custo do interpretador de árvore e deve
  render de 3 a 6 vezes, dentro do teto que o próprio `CLAUDE.md` estima.
- **FFI com C, C++ e Rust:** **já existe** (`Arcane.C`, com `qsort` do C
  chamando uma ação). O que falta é empacotamento: um pacote do registro poder
  trazer uma `.so`/`.dll` por plataforma.
- **WASM e frontend:** rodar no navegador pelo Pyodide é viável hoje e daria
  um playground na doc. Compilar para WASM depende do backend novo do item
  acima.
- **Mobile:** fora de alcance sem backend nativo. O caminho pragmático é a
  Vitrine ou o Kiln servindo PWA.
- **Plataforma tipo LeetCode e editor online no painel:** é produto do site,
  não da linguagem. O LSP e o Pyodide são as peças técnicas, e as duas já
  existem ou são viáveis.

---

## 6. Como reproduzir

Os programas de sondagem desta análise ficaram na pasta temporária da sessão.
Os casos essenciais estão escritos acima e são autocontidos. Para cada bug:

```bash
# B1: salve os dois arquivos da seção B1 em uma pasta e rode
dataforge run main.df            # imprime "do main" e "SOBRESCRITO"

# B2
printf 'x: Integer := 1\nx := "a"\nout x\n' > b2.df && dataforge run b2.df

# B4
printf 'a := 1\nb := 2\nc := 3\nout $"valor {a ? b}"\n' > b4.df && dataforge run b4.df

# B7
echo 'out (lambda a: a)(1)' > b7.df && dataforge run b7.df

# B9
grep -rn -E "adopt ?\.\.?/ " --include='*.df' projetos/
```

A verificação completa continua sendo `bash scripts/verificar_tudo.sh`.

---

## 7. O que foi corrigido nesta sessão

| Bug | Arquivo | Teste (falha sem a correção, passa com ela) |
|---|---|---|
| B1 módulos não isolados | `dataforge/interpreter.py`: `_escopo_de_modulo` e `_embutidas_originais` | `tests/test_resolucao.py`: 4 testes, 6 casos com os dois modos de compilação |
| B3 linha 0 na pilha | `dataforge/interpreter.py`, `_chamar_metodo_cru` | `tests/test_resolucao.py::test_a_pilha_de_uma_chamada_entre_modulos_tem_a_linha_da_chamada` (2 modos) |
| B4 erro léxico na interpolação | `dataforge/parser.py`, `_parse_sub_expression` | `tests/test_regressoes.py::test_erro_do_lexer_dentro_da_interpolacao_aponta_a_linha_certa` |

`doc/conclusao.html` foi regenerado, porque conta as linhas da implementação.

Verificação depois das correções:

| Conjunto | Resultado |
|---|---|
| `pytest tests/` | **5930 passaram**, 16 pulados, 0 falhas (os 5921 de antes mais os 9 novos) |
| exercícios · trilha · exemplos | 399/399 · 18/18 · 44/44 |
| `check` nas 5 pastas | 0 erros, os mesmos avisos de antes |
| `dataforge test` em 5 projetos + 20 pacotes | verdes |

O P0 inteiro foi fechado na §8.

---

## 8. B2, D1, os exercícios e a página `/docs/exercicios`

### B2: o tipo declarado vale depois da declaração

| O quê | Onde |
|---|---|
| o tipo fica no escopo onde o nome mora, e `set`/`set_local` o conferem | `dataforge/environment.py` (`tipos`, `declarar_tipo`, `esquecer_tipo`) |
| o conferidor, com atalho para os tipos embutidos | `interpreter.py`: `_conferidor`, `_conferidores_de`, `_ACEITOS_POR_TIPO` |
| parâmetro tipado dentro do corpo | `_corpo_da_acao` e `_ligar_parametros` (cada chamada recebe uma **cópia**) |
| campo tipado, do cabeçalho, do corpo e herdado; `void` passa | `DFBlueprint.campos_tipados` e `_escrever_membro` |
| o padrão de um campo do corpo, conferido na declaração, na linha do campo | declaração de blueprint |
| `xs := [2]` volta a ser `Cluster<Integer>` | o sinal "valor novo" no interpretador e em `compilador.py` |
| o `check` acusa antes | `typechecker.py`: `Scope.declarados`, `tipo-na-reatribuicao`, `tipo-do-campo` |

**Custo, medido:** código sem anotação não mudou. Sem o atalho, um laço sobre
variável tipada ficava **4× mais lento** (0,12 s → 0,51 s). Com ele o custo cai
para +15% (0,14 s). A escrita em campo tipado fica em +8%, e a chamada com
parâmetro tipado dentro do ruído.

**Dois achados no caminho, os dois corrigidos:**
- **O analisador nunca via os campos tipados do cabeçalho.** Ele lia
  `stmt.tipos_do_cabecalho`, mas no nó o atributo se chama
  `constructor_types`. O `getattr` com padrão devolvia `{}`, calado. Isso
  também deixava de fora o campo genérico do cabeçalho
  (`Caixa<T>(v: T)`), que agora é acusado.
- **`n: Integer := "a"` no corpo de um blueprint passava**, e todo objeto
  nascia com um campo que contradizia a declaração.

Testes: `tests/test_tipo_declarado.py`, com 35 casos, os dois modos de
compilação, e a trava que compara o atalho com o `_check_type`.

### D1: o aviso para `:=` que sobrescreve uma global

`atribuicao-escreve-global` (`typechecker.py`, `_avisar_escrita_em_global`)
acusa uma ação ou método que faz `:=` num nome do topo do arquivo **sem tê-lo
lido antes**. A ordem vem de `travessia.nomes_livres`, a mesma varredura do
`map_processos`.

Ficam calados: quem lê antes (`x := x + 1`, `x += 1`), parâmetros, `shadow`,
`_` e o `// df: permitir`.

**Na primeira rodada ele disparou 20 vezes no repositório, e as 20 eram
reais.** O caso mais claro é `172_canais.df`, que ensina a evitar corrida: três
threads rodam `trabalho_pesado`, que faz `total := 0`. Funcionava só porque a
global `total` nasce depois das threads; chamada depois dela, as três
escreveriam a mesma global. Os 20 locais foram renomeados. Hoje o repositório
tem **zero**, e `tests/test_escrita_global.py` (12 testes) trava isso.

### Os 399 exercícios de `executar-exercicios.md`

Os 399 comandos rodaram um a um: **399 passaram**. Mas "passar" é sair com
código 0, e o `check` mostrou três exercícios com `??` sem parênteses
(armadilha 34):

| Exercício | O defeito |
|---|---|
| `54-erros/331` | `assert v["nome"] ?? "sem nome" is "Ana"` é lido como `v["nome"] ?? ("sem nome" is "Ana")`, e o `assert` **passava com qualquer nome**. Conferido depois da correção: com o nome errado, sai com 1 |
| `30-tempo-real/225` (2 linhas) | `p["arquivo"] ?? "" is not ""` funcionava por coincidência |

Mais os 20 renomes do D1, em 12 exercícios e 8 exemplos. Dois exercícios
ganharam conteúdo sobre o comportamento novo:
- o **121** (anotações) prova que a anotação vale na reatribuição, com a
  "saída esperada" do `.md` atualizada;
- o **061** (escopo) mostra o contador que atualiza a global, o acumulador
  que a sobrescreve e o `shadow` que a protege.

### A página `/docs/exercicios`

No ar, os módulos 35 a 59 (25 de 59) tinham a coluna "Assunto" **vazia**, e a
descrição de cada página saía `"1 exercícios: ."`: é o texto do resultado de
busca e do cartão de compartilhamento. Agora:

- **assunto** para todos os 59 módulos, e o plural certo;
- **"Como praticar"**: tentar antes, rodar, quebrar um `assert` de propósito,
  passar o `check`, e fazer o "Experimente";
- **"Por onde começar"**: dez trilhas por objetivo (API, dados, sistema
  grande, vários núcleos, Telegram, Arduino…), com link para cada módulo;
- **os módulos agrupados em cinco níveis**, com o total de cada um (120 + 71
  + 90 + 108 + 10 = 399), em vez de uma tabela de 59 linhas;
- cada página de módulo diz em que nível está.

Níveis e trilhas moram em **um arquivo só**, `exercicios/trilhas.json`, lido
pelo gerador do site e pelo do README. O `exercicios/README.md` dizia **"397
exercícios em 58 módulos"**, e o `--check` passava porque só olhava a parte
gerada. Agora o gerador mantém esses números e a tabela de trilhas, que parava
no módulo 20. A trava nova é
`test_todo_modulo_de_exercicio_tem_assunto_e_nivel`.

Só as 60 páginas de exercícios foram regeneradas, chamando `escrever`
diretamente. O gerador inteiro também teria reescrito páginas das suas
alterações não commitadas (`big_o.py`, `lsp.py`, `ecossistema_mais.py`).
O `tsc --noEmit` do site passa.

### Verificação final

| Conjunto | Resultado |
|---|---|
| `pytest tests/` | **5977 passaram**, 16 pulados. A única falha (`test_todo_script_que_desenha_prepara_a_saida`, causada por mim no gerador do README) foi corrigida e passa |
| `executar-exercicios.md`, comando a comando | 399/399 |
| trilha · exemplos | 18/18 · 44/44 |
| `check` nas 5 pastas | 0 erros; os avisos dos exercícios caíram de 51 para 49 |
| `dataforge test` em 5 projetos + 20 pacotes | verdes (o `documento` depois de `install`) |
| blocos da documentação | 2.414 compilam |
| idiomas | pt e es em 100%, com as mensagens novas e o sufixo `declared as … but got …` traduzido |

