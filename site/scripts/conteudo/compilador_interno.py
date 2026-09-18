"""A arquitetura interna: pipeline, HIR, MIR, análises — e o mapa da parte 7.

Todo bloco `df` destas páginas RODA (`tests/test_compilador_interno.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/pipeline",
"title": "O caminho de compilação",
"description": "As seis fases que um arquivo .df atravessa, o comando que mostra cada uma — e a fase que não existe, dita com esse nome.",
"blocos": [
 {"p": "Um `.df` não vai direto do texto ao resultado. Ele atravessa seis fases, e cada uma responde a uma pergunta diferente sobre o mesmo programa. `dataforge tokens` e `dataforge ast` mostravam a primeira e a terceira; as do meio não apareciam em lugar nenhum."},
 {"code": """texto
  ↓  lexer.py            tokens, com linha e coluna
  ↓  parser.py           AST — 140 formas de no
  ↓  hir.py              HIR — a arvore depois do acucar
  ↓  typechecker.py      nomes, aridade, tipos, posse
  ↓  mir.py              MIR — bloco basico, aresta, laco, tratador
  ↓  compilador.py       LIR — a arvore vira fechamentos
  ↓  interpreter.py      executa""", "lang": "text", "title": "As seis fases"},
 {"callout": {"tipo": "atencao", "titulo": "Não há fase de código de máquina, e este é o lugar de dizer isso", "texto": "Uma referência de linguagem compilada continua com LLVM IR, passes, registradores e linker. O DataForge é **interpretado**: o backend dele é o compilador de fechamentos (`compilador.py`), e a última fase é chamar fechamento Python. `dataforge ir --fase=lir` é onde isso fica visível — e uma fase chamada `assembly` que devolvesse texto plausível seria a pior coisa que esta documentação poderia ter."}},

 {"h2": "O comando"},
 {"code": """dataforge ir app.df                # o caminho inteiro
dataforge ir app.df --fase=hir     # quanto acucar o arquivo usa
dataforge ir app.df --fase=mir     # o grafo de fluxo
dataforge ir app.df --fase=analises
dataforge ir app.df --fase=lir     # o que compilou, e o que recuou
dataforge ir app.df --fase=mir --acao=classificar
dataforge ir app.df --json         # as mesmas fases como dado""", "lang": "bash", "title": "dataforge ir"},
 {"p": "Uma fase inventada é recusada **com a lista** — inclusive a que muita gente vai tentar primeiro:"},
 {"code": """$ dataforge ir app.df --fase=llvm
Erro: fase 'llvm' nao existe.
  Fases: tokens, ast, hir, mir, analises, lir, tudo
  Nao ha fase de LLVM nem de codigo de maquina: o backend e o
  compilador de fechamentos.""", "lang": "bash", "title": "A fase que não existe"},

 {"h2": "De dentro da linguagem"},
 {"p": "`Arcane.Compilador` entrega as mesmas fases como **dado**. É o que permite a um [plugin do `check`](/docs/metaprogramacao/plugins) perguntar coisas de **fluxo**, e não só de forma — e `Arcane.Macro` sozinho não alcança isso: ele para na árvore."},
 {"code": """adopt Arcane.Compilador as K

fonte := "action f(n):\\n    given n:\\n        yield 1\\n    orif n is 0:\\n        yield 2\\n"

assert K.fases() is ["lexer", "parser", "hir", "mir", "analises", "lir"]
assert K.acucares(fonte) is {"orif-aninhado": 1}
assert K.corpos(fonte) is ["(programa)", "f"]
assert K.lir(fonte)["proporcao"] bigger 0""", "lang": "df"},
 {"table": {"head": ["Símbolo", "A fase"], "rows": [
   ["`K.fases()`", "os nomes, na ordem"],
   ["`K.tokens(fonte)`", "lexer — um vault por token"],
   ["`K.arvore(fonte)`", "parser — a árvore como vault, igual ao `Arcane.Macro`"],
   ["`K.hir` · `K.acucares` · `K.resolucao`", "[HIR](/docs/compilador/hir)"],
   ["`K.mir` · `K.blocos` · `K.corpos`", "[MIR](/docs/compilador/mir)"],
   ["`K.alcance` · `K.constantes` · `K.escapam` · `K.vivas` · `K.talvez_nao_definidas`", "[as análises](/docs/compilador/analises)"],
   ["`K.lir(fonte)`", "o que virou fechamento, e o que recuou"],
   ["`K.texto(fonte, fase)`", "a fase escrita, igual ao `dataforge ir`"]]}},

 {"h2": "Onde o lexer e o parser já estavam documentados"},
 {"p": "As duas primeiras fases têm página própria desde antes: a [gramática formal](/docs/referencia/gramatica) em EBNF, as [palavras reservadas](/docs/referencia/palavras-reservadas) e a [arquitetura](/docs/referencia/arquitetura) do interpretador. O que estas páginas acrescentam é o meio do caminho."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/hir",
"title": "HIR — a árvore sem açúcar",
"description": "O que é açúcar de escrita na linguagem, o que só parece, e a prova de que abrir um não muda o resultado.",
"blocos": [
 {"p": "A árvore que o parser entrega tem cento e quarenta formas de nó. Parte delas é **conveniência de escrita**: `orif` é um `given` deitado, `soma += 1` é `soma := soma + 1`. Cada forma é um caso a mais em todo analisador que percorre a árvore — e é assim que uma análise fica certa num caminho e errada no outro sem ninguém ver."},
 {"p": "O HIR é a mesma árvore com menos formas. Cinco açúcares são abertos:"},
 {"table": {"head": ["Nome", "O que abre"], "rows": [
   ["`orif-aninhado`", "a corrente de `orif` vira `given`/`otherwise` aninhado"],
   ["`composta-simples`", "`x += 1` vira `x := x + 1` — **só** quando o alvo é um nome"],
   ["`pertence-negado`", "`x not in xs` vira `not (x in xs)`"],
   ["`perform-para-persist`", "`perform … persist c` vira a primeira volta mais o laço"],
   ["`sinal-de-literal`", "`-5`, hoje um `UnaryOp` sobre `5`, vira o literal `-5`"]]}},
 {"code": """adopt Arcane.Compilador as K

fonte := "soma := 0\\ncycle i in [1, 2, 3]:\\n    soma += i\\nout -3 not in [1, 2]\\n"

assert K.acucares(fonte) is {"composta-simples": 1, "pertence-negado": 1,
                             "sinal-de-literal": 1}

// e no HIR o 'orif' deixou de existir: virou um 'given' dentro do 'otherwise'
com_orif := "given a:\\n    out 1\\norif b:\\n    out 2\\n"
de_fora := K.hir(com_orif)["corpo"][0]

assert de_fora["tipo"] is "GivenBlock"
assert de_fora["otherwise_body"][0]["tipo"] is "GivenBlock"
assert len(de_fora["orif_blocks"]) is 0""", "lang": "df"},

 {"h2": "A prova não é a forma da árvore: é a saída"},
 {"p": "Um desaçucaramento errado **não levanta erro** — ele muda o resultado. Por isso a garantia é medida do único jeito que vale: exercícios do repositório rodam nas duas formas, e a saída é comparada caractere por caractere."},
 {"code": """n := 0
perform:
    n += 1
persist n smaller 4
assert n is 4""", "lang": "df", "title": "O perform, e o que ele vira"},
 {"code": """m := yes                    // a marca garante a primeira volta
n := 0
persist m or n smaller 4:   // 'or' curto-circuita: na 1a volta 'n' nao e lido
    m := no
    n += 1
assert n is 4""", "lang": "df", "title": "O HIR equivalente, escrito à mão"},
 {"callout": {"tipo": "nota", "titulo": "Por que a marca, e não duplicar o corpo", "texto": "`corpo; persist c: corpo` parece mais simples e está **errado**: um `halt` na primeira cópia não estaria dentro de laço nenhum e escaparia do laço inteiro. A marca mantém o corpo dentro do `persist`, e `halt`, `skip` e `yield` continuam valendo."}},

 {"h2": "O que só PARECE açúcar"},
 {"p": "Esta lista vale mais que a de cima: é o que impede alguém de \"simplificar\" a árvore e mudar a linguagem sem notar. Cada entrada tem o motivo ao lado, e há teste cobrando o motivo."},
 {"table": {"head": ["Forma", "Por que não é açúcar"], "rows": [
   ["`cycle i from 0 to 3`", "`range` **materializa** a lista: um laço de um milhão de voltas viraria uma lista de um milhão de itens, e o laço de contador existe justamente para não pagar isso"],
   ["`a given c otherwise b`", "o ternário é **expressão** e o `given` é **instrução**; trocar um pelo outro exigiria uma temporária, que muda o escopo"],
   ["`a ?? b`", "a forma com ternário avaliaria `a` **duas vezes**, e o lado esquerdo de um `??` costuma ser uma chamada"],
   ["`x?.y`", "o mesmo: `f()?.campo` chamaria `f` duas vezes"],
   ["`$\"{x:.2f}\"`", "o formato depois dos dois-pontos **não existe** como operador na linguagem"],
   ["`[e cycle x in xs]`", "compreensão é expressão com escopo próprio; virar laço exigiria instrução, e o valor teria de sair por uma variável"],
   ["`mark @f`", "`g := f(g)` seria **errado**: um decorador que devolve `void` não substitui o alvo, e é isso que deixa `@Rota(\"/x\")` só anotar"],
   ["`xs >> morph …`", "os estágios são preguiçosos e os verbos de quadro pedem o **quadro**, não a lista"]]}},

 {"h2": "Resolução de nomes"},
 {"p": "A outra metade do HIR: de onde vem cada nome que um corpo menciona — parâmetro, local, livre (vem de fora) ou embutido."},
 {"code": """adopt Arcane.Compilador as K

fonte := "fora := 10\\naction somar(a, b):\\n    local := a + b\\n    yield local + fora + sqrt(4)\\n"

somar := [c cycle c in K.resolucao(fonte) given c["nome"] is "somar"][0]
assert somar["parametros"] is ["a", "b"]
assert somar["locais"] is ["local"]
assert somar["livres"] is ["fora"]
assert somar["embutidos"] is ["sqrt"]""", "lang": "df"},
 {"p": "Um nome **livre** é o que a ação lê e não cria. É a mesma pergunta que a [travessia de processo](/docs/concorrencia/mapa) faz para saber o que levar para outro núcleo, e a que o aviso de [escrita concorrente](/docs/tecnicas/analise-estatica) faz para saber o que uma `thread` alcança."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/mir",
"title": "MIR — o grafo de fluxo",
"description": "Bloco básico, aresta rotulada, laço com aresta de volta e tratador de erro: a representação que responde por onde o programa passa.",
"blocos": [
 {"p": "A árvore diz o que o programa **é**; o grafo diz por onde ele **passa**. São perguntas diferentes, e as que mais interessam a um analisador só a segunda responde: este código é alcançável? este nome está definido em todo caminho que chega aqui? este local escapa do quadro?"},
 {"p": "`construir` devolve um **corpo** por ação — mais um chamado `(programa)` para o nível de topo, e um por rota do Kiln. Cada corpo é uma lista de **blocos básicos**: uma sequência de instruções sem desvio no meio, com arestas rotuladas para os seguintes."},
 {"code": """  classificar(n)   7 bloco(s), 2 inalcancavel(is)
     bloco 0 [entrada] → 1 (sim), 2 (nao)
        linha 5: ComparisonOp bigger
     bloco 1 [sim] ⏹ yield
        linha 6: YieldStatement
     bloco 2 [nao] → 3 (sim), 4 (nao)
        linha 7: ComparisonOp smaller
     bloco 3 [sim] ⏹ yield
        linha 8: YieldStatement
     bloco 4 [nao] ⏹ yield
        linha 10: YieldStatement
   × bloco 5 [juncao] → 6
   × bloco 6 [juncao] ⏹ fim""", "lang": "text", "title": "dataforge ir --fase=mir"},
 {"p": "O `×` marca o bloco **inalcançável**: todos os três ramos encerram com `yield`, então a junção não tem como ser atingida. E os dois blocos de junção, em vez de um, são o `orif` já aberto pelo HIR — o que mostra a normalização pagando o preço dela."},

 {"h2": "Os rótulos de aresta"},
 {"table": {"head": ["Aresta", "Quando"], "rows": [
   ["*(sem rótulo)*", "cai no seguinte"],
   ["`sim` · `nao`", "os dois lados de um `given`, de um laço ou de um `guard`"],
   ["`volta`", "a aresta de trás de um laço — sem ela não é laço"],
   ["`halt` · `skip`", "sai do laço, ou volta para a condição"],
   ["`erro`", "do corpo de um `monitor` para o `handle`"],
   ["`point` · `default`", "os ramos de um `match`"],
   ["`defer`", "o corpo que roda na saída da ação"]]}},
 {"code": """adopt Arcane.Compilador as K

fonte := "n := 3\\npersist n bigger 0:\\n    n -= 1\\nout n\\n"

blocos := K.blocos(fonte, "(programa)")
voltas := [b cycle b in blocos
           given len([s cycle s in b["saidas"] given s["aresta"] is "volta"]) bigger 0]
assert len(voltas) is 1          // um laco tem uma aresta de volta""", "lang": "df"},

 {"h2": "Três decisões que valem lembrar"},
 {"callout": {"tipo": "nota", "titulo": "O MIR é construído a partir do HIR", "texto": "É o que paga a normalização. Sem ela, `orif` e `perform` seriam dois casos a mais no construtor de grafo — e um caso esquecido num construtor de grafo **não dá erro**: produz análise errada com cara de verdade."}},
 {"p": "**A aresta de erro sai da ENTRADA do `monitor`**, e não de cada instrução do corpo. Precisa ser assim para a análise ficar conservadora: o `handle` vê o estado de **antes** do corpo, que é o pior caso honesto. Uma aresta por instrução daria o mesmo resultado com um grafo três vezes maior."},
 {"p": "**O que roda fora da ordem é opaco.** `thread`, `parallel`, `server`, `crucible` e as suas famílias entram como **uma** instrução. Abrir o corpo deles num grafo sequencial afirmaria uma ordem que não existe — e é exatamente sobre concorrência que uma afirmação errada custa."},
 {"code": """adopt Arcane.Compilador as K

fonte := "monitor:\\n    x := 1\\nhandle Error as e:\\n    out e.message\\nensure:\\n    out 2\\n"

rotulos := [b["rotulo"] cycle b in K.blocos(fonte, "(programa)")]
assert "tratador" in rotulos
assert "ensure" in rotulos""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/analises",
"title": "O que o fluxo prova",
"description": "Alcance, vivacidade, definição em todo caminho, propagação de constante e escapatória — e o aviso novo que sai da terceira.",
"blocos": [
 {"p": "Cinco análises sobre o grafo. Uma delas virou diagnóstico do `check`, porque era a única pergunta que ele ainda não sabia responder."},
 {"table": {"head": ["Análise", "Responde", "Direção"], "rows": [
   ["`alcance`", "este bloco pode ser atingido?", "para frente, união"],
   ["`vivas`", "este valor ainda vai ser lido?", "para trás, união"],
   ["`talvez_nao_definidas`", "todo caminho até aqui definiu este nome?", "para frente, **interseção**"],
   ["`constantes`", "todo caminho concorda com este valor?", "para frente, interseção"],
   ["`escapam`", "quem mais pode estar lendo este local?", "estrutural"]]}},

 {"h2": "O aviso novo: `talvez-nao-definida`"},
 {"code": """action classificar(n):
    given n bigger 10:
        rotulo := "alto"
    yield rotulo          // e quando a condicao e falsa?""", "lang": "df", "title": "O que o check passava"},
 {"p": "O analisador **registra** o nome do ramo, e isso está certo: um `given` [compartilha o escopo](/docs/fundamentos/escopo), e é assim que se decide um valor em dois caminhos. O que faltava era contar por **quantos** caminhos ele passa — e essa pergunta só o grafo responde."},
 {"code": """$ dataforge check app.df
aviso[talvez-nao-definida]: 'rotulo' may not be defined here: some path
                            to this line does not assign it
  --> app.df:4:11
  dica: Give 'rotulo' a value before the branch, or add the 'otherwise'
        that covers the other path""", "lang": "bash"},
 {"p": "O laço conta como ramo pelo mesmo motivo — ele pode não rodar nenhuma vez:"},
 {"code": """adopt Arcane.Compilador as K

// o 'otherwise' cobre: silencio
assert K.talvez_nao_definidas(
    "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n") is []

// so um ramo: acusa
assert K.talvez_nao_definidas("given c:\\n    x := 1\\nout x\\n") is ["x"]

// o laco pode nao rodar
assert K.talvez_nao_definidas(
    "cycle x in xs:\\n    ultimo := x\\nout ultimo\\n") is ["ultimo"]""", "lang": "df"},
 {"h3": "O que a faz calar"},
 {"p": "Cada silêncio é um falso alarme que não acontece — e um deles só apareceu **medindo** o repositório."},
 {"table": {"head": ["Cala quando", "Porque"], "rows": [
   ["o corpo tem `monitor`", "o `handle` lê o que o corpo talvez não tenha atribuído, e isso é o uso normal"],
   ["o corpo tem `defer`", "ele roda na saída da ação, fora da ordem do grafo"],
   ["há fechamento no corpo", "um `lambda` pode ligar o nome depois, e o grafo não vê quando ele roda"],
   ["há bloco opaco (`thread`, `parallel`)", "a ordem é outra"],
   ["o nome existe **fora**", "`:=` dentro de uma ação escreve o nome externo quando ele existe — **medido**, e sem esta regra os nove contadores por fechamento do repositório seriam acusados"],
   ["o nome não é escrito neste corpo", "então é global, embutido ou erro — e isso o `check` já responde"]]}},
 {"callout": {"tipo": "atencao", "titulo": "É aviso, e não erro", "texto": "O caminho que não define pode ser o que nunca acontece, e só quem escreveu sabe. Como toda regra, dá para silenciar de propósito: `// df: permitir talvez-nao-definida`."}},

 {"h2": "Propagação de constante"},
 {"p": "Uma atribuição que o grafo prova única. É a interseção que separa esta análise de uma varredura de texto: um nome que dois ramos escrevem com valores diferentes **sai** da tabela."},
 {"code": """adopt Arcane.Compilador as K

assert K.constantes("x := 2\\ny := x + 1\\nout y\\n", "(programa)") is {"x": 2, "y": 3}

// dois ramos discordam: nao ha constante
assert K.constantes("given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n",
                    "(programa)") is {}""", "lang": "df"},

 {"h2": "Escapatória"},
 {"p": "Quais locais saem do quadro, e por qual motivo. Numa linguagem compilada é o primeiro passo da alocação em pilha; aqui ela não move nada de lugar — o coletor do Python continua respondendo por isso — mas responde uma pergunta prática: **o que mais alguém pode estar lendo?** Um nome que escapa para uma `thread` é a metade de todo bug de concorrência."},
 {"code": """adopt Arcane.Compilador as K

fonte := "action f():\\n    preso := 1\\n    solto := 2\\n" +
         "    ler := lambda => preso + 1\\n    yield ler()\\n"

fugas := K.escapam(fonte, "f")
assert fugas["preso"] is "fechamento"      // a closure o le
assert fugas["ler"] is "devolvido"         // sai da acao
assert "solto" not in fugas                // vive e morre no quadro""", "lang": "df"},
 {"table": {"head": ["Motivo", "O que aconteceu"], "rows": [
   ["`devolvido`", "sai da ação por `yield`"],
   ["`fechamento`", "um `lambda` ou uma ação aninhada o lê"],
   ["`concorrente`", "um `thread` ou `parallel` o lê"],
   ["`guardado`", "vai para dentro de um objeto ou coleção"]]}},

 {"h2": "Vivacidade, e o LIR"},
 {"p": "`vivas` diz, na entrada de cada bloco, quais nomes ainda serão lidos. Numa linguagem compilada é a base da alocação de registradores; aqui a pergunta continua útil na hora de olhar um corpo grande."},
 {"p": "E o [LIR](/docs/compilador/pipeline) fecha o caminho com a informação que não existia em lugar nenhum: **o que o compilador de fechamentos compilou, e o que recuou** para o interpretador de árvore."},
 {"code": """$ dataforge ir app.df --fase=lir
  42 de 48 nos viraram fechamento (88%)
  6 recuaram para o interpretador de arvore

  no                          compila   recua
   AssertStatement                  0       3
   ListComprehension                0       2

  1 recuo(s) DENTRO de laco — e onde a diferenca aparece num perfil:
   ListComprehension — linha(s) 31""", "lang": "bash"},
 {"p": "O recuo **dentro de um laço** é o único em que a diferença aparece num perfil, e por isso ele é listado em separado. A conta sai das tabelas do próprio `compilador.py`, e não de uma lista à parte: uma segunda lista divergiria no primeiro nó novo, e o relatório passaria a mentir com confiança."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/mapa",
"title": "O compilador: o mapa",
"description": "Item por item da parte 7 da referência Deep Tech — pipeline, lexer, parser, AST, HIR, MIR, LIR e análise estática — cruzado com o que o DataForge tem.",
"blocos": [
 {"p": "A sétima parte de uma referência Deep Tech abre o compilador: as oito seções vão do pipeline às análises. É a parte em que o DataForge tem **mais** do que parece — ele tem lexer, parser, AST, analisador e backend próprios — e ao mesmo tempo a primeira em que um item é honestamente **não se aplica**."},

 {"h2": "30 · Pipeline de compilação"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["fluxo de fases", "seis fases, e `dataforge ir` mostra cada uma", "[Pipeline](/docs/compilador/pipeline)"],
   ["type checking", "`typechecker.py` — 1752 linhas, entre o HIR e o MIR", "[Análise estática](/docs/tecnicas/analise-estatica)"],
   ["borrow checking", "`Arcane.Posse` mais as checagens de fluxo do `check`", "[Posse](/docs/memoria/posse)"],
   ["LLVM IR, machine code, linker", "**não se aplica**: o DataForge é interpretado. O backend é o compilador de fechamentos, e a última fase é chamar fechamento Python", "[Pipeline](/docs/compilador/pipeline)"]]}},

 {"h2": "31 · Lexer"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["tokenização, identificadores, keywords", "`lexer.py`; 81 palavras reservadas, e as contextuais que **não** são", "[Palavras](/docs/referencia/palavras-reservadas)"],
   ["literais, operadores", "inteiro, real, texto, `yes`/`no`/`void`, tupla; `~/` para divisão inteira", "[Operadores](/docs/operadores)"],
   ["comentários", "`//` é comentário **por padrão**, e vira divisão só quando o que segue confirma", "[Operadores](/docs/operadores)"],
   ["strings, interpolação", "`$\"…{expr}…\"`, com `{x:.2f}`; a string aninhada é copiada verbatim", "[Interpolação](/docs/fundamentos/interpolacao)"],
   ["source spans", "linha, coluna e `span` em todo nó e em todo erro — é o que desenha a seta", "[Erros](/docs/erros)"],
   ["erros léxicos", "`SyncError` para tab na indentação, e a mensagem diz o que fazer", "[Erros](/docs/erros)"],
   ["INDENT/DEDENT", "**além** da lista: o lexer emite os dois, e é deles que sai a profundidade do formatador", "[Arquitetura](/docs/referencia/arquitetura)"]]}},

 {"h2": "32 · Parser"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["recursive descent", "`parser.py`, 1941 linhas, descendente recursivo", "[Arquitetura](/docs/referencia/arquitetura)"],
   ["precedência, associatividade", "por nível de função (`parse_or` → `parse_and` → …)", "[Gramática](/docs/referencia/gramatica)"],
   ["parsing de expressões e declarações", "o conjunto todo, com a EBNF **gerada** do código", "[Gramática](/docs/referencia/gramatica)"],
   ["AST construction", "`ast_nodes.py` — 140 dataclasses", "[AST](/docs/compilador/pipeline)"],
   ["Pratt parser", "**não é** a técnica usada: a precedência é a cascata de funções. Pratt paga quando a tabela de operadores é dinâmica, e aqui ela é fixa", "—"],
   ["recuperação de erros", "**parcial**: o `check` continua depois de um arquivo que não compila (a superfície devolve `aberta = yes`), mas dentro de um arquivo o primeiro erro de sintaxe encerra a leitura", "—"]]}},

 {"h2": "33 · AST"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["nós de expressão e de declaração", "140 classes; `dataforge ast` e `K.arvore(fonte)`", "[Pipeline](/docs/compilador/pipeline)"],
   ["tipos, funções, structs, traits, generics", "`TypeDeclaration`, `ActionDeclaration`, `RecordDeclaration`, `TraitDeclaration`, `type_params`", "[Tipos](/docs/tipos/mapa)"],
   ["pattern matching", "oito classes de padrão, de `WildcardPattern` a `OrPattern`", "[Pattern matching](/docs/fundamentos/pattern-matching)"],
   ["metadados, source locations", "`line`, `column` em toda `ASTNode`; a ação sabe em que **arquivo** nasceu", "[Erros](/docs/erros)"],
   ["a árvore como dado", "**além** da lista: `Arcane.Macro` a entrega como vault, e a volta é conferida", "[Macros](/docs/metaprogramacao/macros)"]]}},

 {"h2": "34 · HIR"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["desugaring", "`hir.normalizar` — cinco açúcares, e oito formas que só parecem", "[HIR](/docs/compilador/hir)"],
   ["resolução de nomes", "`hir.resolucao` — parâmetro, local, livre, embutido, por corpo", "[HIR](/docs/compilador/hir)"],
   ["normalização", "é o mesmo passo: o HIR é a AST restrita ao núcleo", "[HIR](/docs/compilador/hir)"],
   ["expansão de macros", "roda na **carga**, no `comptime` e no decorador de macro — antes desta fase", "[comptime](/docs/metaprogramacao/comptime)"],
   ["representação semântica", "o HIR usa as **mesmas classes** da AST, de propósito: é o que permite provar a equivalência **rodando** os dois", "[HIR](/docs/compilador/hir)"]]}},

 {"h2": "35 · MIR"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["basic blocks, controle de fluxo", "`mir.construir` — um corpo por ação, arestas rotuladas", "[MIR](/docs/compilador/mir)"],
   ["dataflow analysis", "vivacidade, definição em todo caminho, propagação de constante", "[Análises](/docs/compilador/analises)"],
   ["borrow checking", "`posse-movida`, `emprestimo-escapa`, `recurso-vazado` — no `typechecker`, sobre a árvore", "[Posse](/docs/memoria/posse)"],
   ["ownership analysis", "a mesma família, e `escapam` responde quem mais alcança o valor", "[Análises](/docs/compilador/analises)"],
   ["lifetime analysis", "**não há tempo de vida nomeado** (`'a`): o coletor do Python responde pela memória, e um `'a` sem nada para provar seria cerimônia", "—"],
   ["otimizações intermediárias", "**não há**: o MIR é para **analisar**, não para reescrever. O ganho de velocidade vem do compilador de fechamentos, medido em 1,5× a 1,8×", "—"]]}},

 {"h2": "36 · LIR"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["lowering", "a árvore vira fechamentos Python, uma vez", "[LIR](/docs/compilador/analises)"],
   ["operações primitivas", "cada fechamento delega aos **mesmos** auxiliares do interpretador (`_operar`, `_comparar`) — não há segunda semântica", "[Arquitetura](/docs/referencia/arquitetura)"],
   ["preparação para backend", "é o backend: `dataforge ir --fase=lir` diz o que compilou e o que recuou", "[LIR](/docs/compilador/analises)"],
   ["calling conventions, ABI lowering", "existem, mas **só na fronteira com o C**: `Arcane.C` declara a assinatura e o `ctypes` aplica a ABI da plataforma", "[FFI](/docs/ffi/c)"],
   ["representação de memória", "o mesmo: `C.estrutura` dá tamanho, alinhamento e deslocamento de verdade", "[FFI](/docs/ffi/c)"],
   ["registradores, spilling", "**não se aplica**", "—"]]}},

 {"h2": "37 · Análise estática"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["type checking", "`dataforge check`, e ele **atravessa arquivos**: aridade, tipo de parâmetro e de retorno pela fronteira do `adopt`", "[Análise estática](/docs/tecnicas/analise-estatica)"],
   ["dataflow analysis", "as cinco análises do MIR", "[Análises](/docs/compilador/analises)"],
   ["reachability", "`alcancaveis`, mais o `unreachable` depois de `yield`/`halt`/`skip` e o `point-inalcancavel`", "[Análises](/docs/compilador/analises)"],
   ["dead code analysis", "`unused-variable`, `unused-import`, `unused-parameter` no `lint`", "[Lint](/docs/cli/lint)"],
   ["constant propagation", "`constantes`, e o `check` já provava `indice-fora-do-alcance` e `chave-ausente` a partir de literal", "[Análises](/docs/compilador/analises)"],
   ["escape analysis", "`escapam`, com quatro motivos", "[Análises](/docs/compilador/analises)"],
   ["borrow / lifetime analysis", "a família da posse; tempo de vida nomeado não existe", "[Posse](/docs/memoria/posse)"],
   ["static assertions", "`assert` dentro de `comptime` — o `check` o **executa** e acusa `comptime-falhou`", "[comptime](/docs/metaprogramacao/comptime)"],
   ["formal verification hooks", "`expects`, `promises`, `invariant` são contratos **cobrados em execução**, e `--plugin=` deixa acoplar uma regra própria. Prova formal (SMT, refinamento provado) **não existe**", "[Contratos](/docs/oop/contratos)"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das oito seções, seis estão cobertas de ponta a ponta — e duas delas (HIR e MIR) passaram a existir como **representação inspecionável**, não só como código escondido dentro do analisador. O que fica de fora é o que depende de gerar código de máquina: LLVM, registradores, linker. Não é uma lacuna a preencher: é o que a escolha de ser interpretado significa, e o teto dessa técnica já está medido em ~6,5×."},
 {"callout": {"tipo": "nota", "titulo": "O que esta parte entregou de novo à linguagem", "texto": "Um comando (`dataforge ir`), um módulo (`Arcane.Compilador`), duas representações (`hir.py`, `mir.py`), cinco análises de fluxo e **um aviso que o `check` não sabia dar**: o nome que só um ramo define. Zero falso alarme nos 387 arquivos do repositório — e nove casos que o filtro de nome externo cala, todos medidos."}},
]},
]
