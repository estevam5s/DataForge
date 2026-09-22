# -*- coding: utf-8 -*-
"""A gramática da linguagem como DADO — e conferida contra o parser.

A EBNF vivia como texto em dois lugares (a §12 de `doc/REFERENCIA.md` e
a página `/docs/referencia/gramatica`), e nenhum deles era conferido:
uma produção podia descrever uma sintaxe que o parser já não aceita, e
nada acusaria. Aqui cada produção carrega um **exemplo**, e
`tests/test_gramatica.py` o passa pelo lexer e pelo parser de verdade,
exigindo que a árvore contenha o nó que a produção promete.

A precedência é tratada do mesmo jeito: `PRECEDENCIA` diz a ordem, e
`CONFERENCIAS_DE_PRECEDENCIA` são expressões em que a ordem decide o
resultado — cada uma afirma **qual operador fica na raiz**. Uma tabela
de precedência que ninguém confere é uma opinião.

Daqui saem `Arcane.Gramatica` (para programas), `dataforge gramatica`
(para o terminal) e as páginas de `/docs/referencia/gramatica/*`.
"""

import dataclasses

# ═══════════════════════════════════════════════════════════
#  As produções
# ═══════════════════════════════════════════════════════════

#: Os grupos, na ordem em que a documentação os apresenta.
GRUPOS = [
    ("lexico", "Léxico", "tokens, literais, comentários e indentação"),
    ("expressoes", "Expressões", "operadores, chamadas, coleções, pipeline"),
    ("instrucoes", "Instruções", "atribuição, saída, controle de fluxo e laços"),
    ("declaracoes", "Declarações", "ação, record, enum, blueprint, trait, type"),
    ("padroes", "Padrões", "o match e o que cada point casa"),
    ("modulos", "Módulos", "adopt, relay e mark"),
    ("erros", "Erros e recursos", "monitor, trigger, defer, assert"),
    ("concorrencia", "Concorrência", "thread, parallel, async"),
    ("dominios", "Blocos de domínio", "crucible, server e as palavras contextuais"),
]


def _p(nome, grupo, ebnf, exemplo, contem, nota=""):
    return {"nome": nome, "grupo": grupo, "ebnf": ebnf.strip("\n"),
            "exemplo": exemplo.strip("\n"), "contem": list(contem),
            "nota": nota}


PRODUCOES = [
    # ── léxico ──────────────────────────────────────────────
    _p("inteiro", "lexico",
       'inteiro       = digito { digito | "_" } ;',
       "x := 1_000_000", ["IntegerLiteral"],
       "O `_` separa milhares e é ignorado."),
    _p("decimal", "lexico",
       'decimal       = digito { digito } "." digito { digito } "d" ;',
       "preco := 19.99d", ["DecimalLiteral"],
       "O `d` constrói o valor a partir do **texto**, sem passar por float. "
       "Só conta quando termina o número: `19.99dias` não é decimal."),
    _p("texto", "lexico",
       'texto         = \'"\' { caractere } \'"\' | \'"""\' { caractere | NEWLINE } \'"""\' ;',
       'sql := """SELECT *\nFROM t"""', ["StringLiteral"],
       "O texto simples não cruza linhas; o de três aspas cruza."),
    _p("interpolacao", "lexico",
       'interpolado   = "$" \'"\' { caractere | "{" expressao "}" } \'"\' ;',
       'n := 2\nout $"n vale {n * 2}"', ["InterpolatedString"],
       "Dentro de `{…}`, aspas normais: `$\"{v[\"id\"]}\"`. O escape `\\\"` "
       "quebra a leitura."),
    _p("comentario", "lexico",
       'comentario    = "//" { caractere } NEWLINE ;',
       "x := 7 // um comentario\ny := x ~/ 2", ["Assignment"],
       "`//` é comentário por padrão. Só vira divisão inteira seguido de "
       "dígito, `(` ou chamada/índice/membro — use `~/`, que não é ambíguo."),
    _p("indentacao", "lexico",
       'bloco         = ":" NEWLINE INDENT { instrucao } DEDENT ;',
       "given yes:\n    out 1", ["GivenBlock"],
       "Só espaços, quatro por nível. Um tab é `SyncError`."),

    # ── expressões ──────────────────────────────────────────
    _p("ternario", "expressoes",
       'ternario      = coalesce [ "given" expressao "otherwise" expressao ] ;',
       'r := "par" given 4 % 2 is 0 otherwise "impar"', ["TernaryExpression"]),
    _p("coalesce", "expressoes",
       'coalesce      = logico_ou { "??" logico_ou } ;',
       'v := {}\nx := v["k"] ?? 0', ["CoalesceOp"],
       "O lado esquerdo de um `??` é lido com indulgência: a chave ausente "
       "não levanta."),
    _p("comparacao", "expressoes",
       'comparacao    = soma [ ( "is" | "isnt" | "bigger" | "smaller" | "bigger_eq"\n'
       '                      | "smaller_eq" | "in" | "not" "in" ) soma ] ;',
       "x := 3 bigger_eq 2", ["ComparisonOp"]),
    _p("aritmetica", "expressoes",
       'soma          = produto { ( "+" | "-" ) produto } ;\n'
       'produto       = unario { ( "*" | "/" | "%" | "~/" ) unario } ;\n'
       'unario        = ( "-" | "+" ) unario | potencia ;\n'
       'potencia      = posfixo [ "**" unario ] ;',
       "x := -2 ** 2 + 7 ~/ 2", ["BinaryOp", "UnaryOp"],
       "`-2 ** 2` é `-(2 ** 2)`: a potência liga mais forte que o sinal."),
    _p("lambda", "expressoes",
       'lambda        = "lambda" [ parametros ] ( ":" | "=>" ) expressao ;',
       "f := lambda x: x * 2\ng := lambda a, b => a + b", ["LambdaExpression"],
       "Um pipeline dentro do corpo precisa de parênteses: "
       "`lambda => (xs >> morph x: x * 2)`."),
    _p("pipeline", "expressoes",
       'pipeline      = ternario { ">>" operacao } ;\n'
       'operacao      = "sift" nome ":" expressao | "morph" nome ":" expressao\n'
       '              | "distill" nome "," nome ":" expressao expressao\n'
       '              | verbo_de_quadro ;',
       "t := [1, 2, 3] >> sift n: n bigger 1 >> morph n: n * 10 >> distill a, v: a + v 0",
       ["PipelineExpression", "SiftOperation", "MorphOperation", "DistillOperation"],
       "O valor inicial do `distill` vem **depois** do corpo. E um ternário "
       "no corpo de `morph`/`sift` precisa de parênteses: "
       "`morph n: (n given n bigger 0 otherwise 0)` — sem eles, `given` "
       "abre uma instrução."),
    _p("compreensao", "expressoes",
       'compreensao   = "[" expressao "cycle" nome "in" expressao [ "given" expressao ] "]" ;',
       "q := [n * n cycle n in [1, 2, 3] given n bigger 1]", ["ListComprehension"]),
    _p("colecoes", "expressoes",
       'cluster       = "[" [ item { "," item } ] "]" ;\n'
       'vault         = "{" [ chave ":" expressao { "," chave ":" expressao } ] "}" ;\n'
       'tupla         = "(" expressao "," [ expressao { "," expressao } ] ")" ;\n'
       'item          = [ "..." ] expressao ;',
       'xs := [1, 2]\nys := [...xs, 3]\nv := {"a": 1}\nt := (1, "a")',
       ["ListLiteral", "SpreadElement", "DictLiteral", "TupleLiteral"]),
    _p("acesso", "expressoes",
       'posfixo       = primario { "." nome | "?." nome | "(" argumentos ")"\n'
       '                         | "[" indice "]" } ;\n'
       'indice        = expressao | [ expressao ] ":" [ expressao ] [ ":" [ expressao ] ] ;',
       'xs := [1, 2, 3]\nout xs[1:3], xs[::-1]\no := void\nout o?.nome',
       ["SliceAccess", "SafeMemberAccess"]),
    _p("with", "expressoes",
       'copia         = expressao "with" vault ;',
       'record P:\n    x: Integer\np := P(1)\nq := p with {"x": 2}', ["WithExpression"],
       "Record é imutável: `p.x := 2` é erro; `with` devolve outro."),
    _p("spawn", "expressoes",
       'spawn         = ( "spawn" | "forge" ) nome "(" [ argumentos ] ")" ;',
       "blueprint B:\n    x := 1\nb := spawn B()\nc := forge B()", ["SpawnExpression"],
       "`spawn` leva o nome e os argumentos, e para ali: `spawn B().f()` "
       "chama `f` na instância."),

    # ── instruções ──────────────────────────────────────────
    _p("atribuicao", "instrucoes",
       'atribuicao    = alvo [ ":" tipo ] ":=" expressao\n'
       '              | alvo ( "+=" | "-=" | "*=" | "/=" | "%=" ) expressao ;',
       "idade: Integer := 30\nidade += 1", ["Assignment"],
       "`:=` atribui; `=` só existe dentro de `lambda … =>`."),
    _p("constante", "instrucoes",
       'constante     = "steady" nome [ ":" tipo ] ":=" expressao ;',
       "steady PI := 3.14159", ["SteadyDeclaration"]),
    _p("desestruturacao", "instrucoes",
       'desestruturar = alvo_d { "," alvo_d } ":=" expressao ;\n'
       'alvo_d        = [ "..." ] nome ;',
       "primeiro, ...resto := [1, 2, 3]", ["DestructuringAssignment"]),
    _p("saida", "instrucoes",
       'saida         = "out" expressao { "," expressao } ;',
       'out "ola", 42', ["OutStatement"]),
    _p("given", "instrucoes",
       'condicional   = "given" expressao bloco { "orif" expressao bloco }\n'
       '                [ "otherwise" bloco ] ;',
       "x := 5\ngiven x bigger 5:\n    out 1\norif x is 5:\n    out 0\notherwise:\n    out -1",
       ["GivenBlock"],
       "Um nome atribuído num ramo existe depois do bloco; o corpo de um "
       "`cycle` tem escopo próprio."),
    _p("cycle", "instrucoes",
       'laco_faixa    = "cycle" nome "from" expressao "to" expressao [ "step" expressao ] bloco ;\n'
       'laco_itens    = "cycle" nome "in" expressao bloco ;',
       "cycle i from 1 to 5 step 2:\n    out i\ncycle v in [1, 2]:\n    out v",
       ["CycleFromTo", "CycleIn"],
       "`from … to` é inclusivo nos dois extremos."),
    _p("persist", "instrucoes",
       'enquanto      = "persist" expressao bloco ;\n'
       'repita        = "perform" bloco "persist" expressao ;',
       "n := 3\npersist n bigger 0:\n    n -= 1\nperform:\n    n += 1\npersist n smaller 3",
       ["PersistBlock", "PerformBlock"]),
    _p("halt_skip", "instrucoes",
       'interromper   = "halt" ;\ncontinuar     = "skip" ;',
       "cycle i in [1, 2, 3]:\n    given i is 2:\n        skip\n    given i is 3:\n        halt",
       ["HaltStatement", "SkipStatement"],
       "`halt`, `skip` e `yield` atravessam `monitor`: são sinais de controle, "
       "não erros."),

    # ── declarações ─────────────────────────────────────────
    _p("action", "declaracoes",
       'acao          = [ "async" | "stream" ] "action" nome [ genericos ]\n'
       '                "(" [ parametros ] ")" [ "->" tipo ] ":" bloco ;\n'
       'parametro     = nome [ ":" tipo ] [ ":=" expressao ] ;',
       "action somar(a: Integer, b := 1) -> Integer:\n    yield a + b",
       ["ActionDeclaration", "YieldStatement"],
       "`yield` devolve e **encerra**; para uma sequência, `stream action` + `emit`."),
    _p("stream", "declaracoes",
       'produzir      = "emit" expressao ;',
       "stream action nat():\n    n := 0\n    persist yes:\n        emit n\n        n += 1",
       ["EmitStatement"]),
    _p("record", "declaracoes",
       'record        = "record" nome [ genericos ] ":" NEWLINE INDENT\n'
       '                { campo | acao } DEDENT ;\n'
       'campo         = nome ":" tipo [ ":=" expressao ] NEWLINE ;',
       "record Ponto:\n    x: Integer\n    y: Integer", ["RecordDeclaration"]),
    _p("enum", "declaracoes",
       'enum          = "enum" nome ":" NEWLINE INDENT { membro | acao } DEDENT ;\n'
       'membro        = nome [ ":=" expressao ] NEWLINE ;',
       'enum Cor:\n    Verde\n    Azul := "a"', ["EnumDeclaration"]),
    _p("blueprint", "declaracoes",
       'blueprint     = { modificador } "blueprint" nome [ genericos ] [ "(" campos ")" ]\n'
       '                [ "extends" nome ] [ "with" nome { "," nome } ] ":" bloco ;',
       "blueprint Forma:\n    action area():\n        yield 0\n\n"
       "blueprint Quadrado(lado) extends Forma:\n    action area():\n        yield self.lado ** 2",
       ["BlueprintDeclaration"],
       "`self` sempre: `x` sem `self.` lê a variável de fora."),
    _p("trait", "declaracoes",
       'trait         = "trait" nome ":" NEWLINE INDENT { assinatura | acao } DEDENT ;',
       "trait Mede:\n    action medir()", ["TraitDeclaration"]),
    _p("type", "declaracoes",
       'tipo_nomeado  = [ "opaque" ] "type" nome [ genericos ] ":=" tipo\n'
       '                [ "where" expressao ] ;',
       "type Id := Integer\ntype Positivo := Integer where valor bigger 0\n"
       "opaque type Cpf := String where len(valor) is 11",
       ["TypeDeclaration"],
       "`type`, `opaque` e `where` são contextuais: `type := 3` continua valendo."),

    # ── padrões ─────────────────────────────────────────────
    _p("match", "padroes",
       'selecao       = "match" expressao ":" NEWLINE INDENT\n'
       '                { "point" padrao [ "when" expressao ] bloco }\n'
       '                [ "default" bloco ] DEDENT ;\n'
       'padrao        = literal | nome | tipo [ "as" nome ] | "[" padroes "]"\n'
       '              | "{" chave ":" padrao { "," … } "}" | nome "(" padroes ")"\n'
       '              | nome "." membro ;',
       'match 5:\n    point Integer as n when n bigger 3:\n        out "grande"\n'
       '    point [a, b]:\n        out "par"\n    default:\n        out "outro"',
       ["MatchBlock"],
       "A ordem importa: uma captura sem guarda no topo torna tudo abaixo "
       "inalcançável — e o `check` acusa."),

    # ── módulos ─────────────────────────────────────────────
    _p("adopt", "modulos",
       'adocao        = "adopt" caminho [ "as" nome ]\n'
       '              | "adopt" caminho "." "{" nome { "," nome } "}"\n'
       '              | "adopt" "{" nome "as" nome { "," … } "}" "from" caminho ;\n'
       'caminho       = nome { "." nome } | ( "./" | "../" ) segmento { "/" segmento } ;',
       "adopt Arcane.Math as M\nadopt Arcane.Math.{sqrt, floor}\n"
       "adopt {sqrt as raiz} from Arcane.Math",
       ["AdoptStatement"]),
    _p("relay", "modulos",
       'exportacao    = "relay" nome { "," nome } ;',
       "action a():\n    yield 1\nrelay a", ["RelayStatement"],
       "Com `relay`, só o que está listado sai do módulo."),
    _p("mark", "modulos",
       'decorador     = "mark" "@" expressao NEWLINE ( acao | blueprint ) ;',
       "action dec(f):\n    yield f\nmark @dec\naction h():\n    yield 1",
       ["MarkDecorator"],
       "Um decorador que devolve `void` não substitui o alvo."),

    # ── erros e recursos ────────────────────────────────────
    _p("monitor", "erros",
       'tratamento    = "monitor" bloco { "handle" [ tipo ] [ "as" nome ] bloco }\n'
       '                [ "ensure" bloco ] ;',
       'monitor:\n    trigger "x"\nhandle Error as e:\n    out e.message\nensure:\n    out "fim"',
       ["MonitorBlock"],
       "`trigger` levanta `TriggerError`, e não `RuntimeError`: para pegar "
       "qualquer coisa, `handle Error`."),
    _p("trigger", "erros",
       'levantar      = "trigger" expressao ;',
       'action g():\n    trigger "falhou"', ["TriggerStatement"]),
    _p("defer", "erros",
       'adiar         = "defer" bloco ;',
       "action f():\n    defer:\n        out 1\n    yield 2", ["DeferStatement"],
       "Roda na saída da **ação**, onde quer que esteja escrito."),
    _p("assert", "erros",
       'afirmar       = "assert" expressao [ "," expressao ] ;',
       'assert 1 is 1, "um e um"', ["AssertStatement"]),

    # ── concorrência ────────────────────────────────────────
    _p("thread", "concorrencia",
       'thread        = "thread" bloco ;',
       "thread:\n    out 1", ["ThreadBlock"],
       "`thread` não espera; o erro do corpo é desenhado na hora."),
    _p("parallel", "concorrencia",
       'paralelo      = "parallel" bloco ;',
       "parallel:\n    out 1\n    out 2", ["ParallelBlock"],
       "`parallel` espera todas, e levanta na linha do bloco se alguma falhou."),

    # ── domínios ────────────────────────────────────────────
    _p("crucible", "dominios",
       'suite         = "crucible" texto ":" NEWLINE INDENT\n'
       '                { "trial" texto [ "pending" ] bloco | fixture | gancho } DEDENT ;\n'
       'cobranca      = "expect" expressao ;',
       'crucible "s":\n    trial "t":\n        expect 1 is 1', ["CrucibleBlock"]),
    _p("server", "dominios",
       'servidor      = "server" nome [ "on" expressao ] [ "at" expressao ] ":" NEWLINE INDENT\n'
       '                { "route" verbo texto bloco | middleware | mount | assets } DEDENT ;\n'
       'resposta      = "respond" [ inteiro ] [ "json" | "html" | "text" ] expressao ;',
       'server api on 0:\n    route GET "/":\n        respond json {"ok": yes}',
       ["ServerBlock"],
       "As onze palavras do Kiln são contextuais: `route := \"/x\"` continua "
       "valendo fora de um `server`."),
    # ── cobertura: as palavras que faltavam ─────────────────
    _p("logico", "expressoes",
       'logico_ou     = logico_e { "or" logico_e } ;\n'
       'logico_e      = negacao { "and" negacao } ;\n'
       'negacao       = "not" negacao | comparacao ;\n'
       'booleano      = "yes" | "no" | "void" ;',
       'out yes and "segundo", 0 and 9, not no', ["LogicalOp", "NotOp", "BooleanLiteral"],
       "`and` e `or` devolvem o **valor** que decidiu, e não um booleano: "
       "`yes and \"segundo\"` é `\"segundo\"`."),
    _p("tipos_em_execucao", "expressoes",
       'conversao     = "cast" expressao "as" tipo ;\n'
       'tipo_de       = "typeof" "(" expressao ")" ;',
       'out cast "42" as Integer, typeof([1])', ["CastExpression", "TypeofExpression"],
       "`typeof` responde no vocabulário da linguagem — `Cluster`, e não `list`."),
    _p("instrucoes_de_vault", "instrucoes",
       'apagar        = "delete" alvo_de_indice ;\n'
       'inspecionar   = "inspect" expressao ;',
       'v := {"a": 1, "b": 2}\ndelete v["a"]\ninspect v', ["DeleteStatement", "InspectStatement"],
       "`inspect` imprime o valor **com o tipo** — para depurar."),
    _p("guard", "instrucoes",
       'guarda        = "guard" expressao "otherwise" bloco ;',
       "action dividir(a, b):\n    guard b isnt 0 otherwise:\n        yield void\n    yield a / b",
       ["GuardStatement"],
       "Sai cedo quando a condição **não** vale — o `otherwise` precisa sair "
       "(`yield`, `trigger`, `halt`)."),
    _p("observe", "instrucoes",
       'observar      = "observe" nome "in" expressao bloco ;',
       "observe x in [1, 2, 3]:\n    out x", ["ObserveBlock"]),
    _p("shadow_static", "declaracoes",
       'sombra        = "shadow" nome ":=" expressao ;\n'
       'estatico      = "static" nome ":=" expressao ;',
       'x := 1\naction f():\n    shadow x := 99\n    yield x\nblueprint Config:\n    static padrao := "claro"',
       ["ShadowDeclaration", "StaticDeclaration"],
       "Dentro de uma ação, `:=` escreve o nome de fora quando ele existe; "
       "`shadow` declara uma cópia local de propósito."),
    _p("root", "declaracoes",
       'mae           = "root" "." nome "(" [ argumentos ] ")" ;',
       'blueprint Base:\n    action nome():\n        yield "base"\n\n'
       'blueprint Filha extends Base:\n    action nome():\n        yield root.nome() + "+filha"',
       ["BlueprintDeclaration"],
       "`root` segue a MRO a partir de quem **declarou** o método — com três "
       "níveis de herança, o pai da instância entraria em laço."),
    _p("resiliencia", "erros",
       'repetir       = "retry" expressao bloco [ "recover" [ nome ] bloco ] ;\n'
       'repassar      = "propagate" nome ;\n'
       'validar       = "validate" expressao [ "," expressao ] ;',
       'n := 0\naction instavel():\n    n += 1\n    trigger "ainda nao"\nretry 3:\n    instavel()\n'
       'recover e:\n    out e.message\nvalidate n bigger 0, "n precisa ser positivo"\n'
       'action f():\n    monitor:\n        trigger "x"\n    handle e:\n        propagate e',
       ["RetryBlock", "ValidateStatement", "PropagateStatement"],
       "`validate` é o `assert` do dado de entrada: a mensagem é para quem "
       "mandou o dado, e não para quem escreveu o código."),
    _p("await", "concorrencia",
       'esperar       = "await" expressao ;',
       "async action dobro(n):\n    yield n * 2\nout await dobro(21)", ["AwaitExpression"],
       "Chamar uma ação `async` começa o trabalho e devolve a tarefa; `await` espera."),
    _p("canais", "concorrencia",
       'canal         = "channel" nome ;\n'
       'evento        = "pulse" expressao [ "," expressao ] ;\n'
       'dormir        = "wait" expressao ;',
       'channel fila\nfila.send("oi")\npulse "pedido.criado", {"id": 7}\nwait 1',
       ["ChannelDeclaration", "PulseStatement", "WaitStatement"],
       "`receive()` sem prazo **não espera**: devolve `void` na hora se a fila "
       "está vazia. Para esperar, `receive(ms)`."),
    _p("dados", "dominios",
       'quadro        = "frame" expressao ;\n'
       'treinar       = "train" texto "using" expressao ;\n'
       'prever        = "predict" expressao "using" expressao ;',
       't := frame [{"a": 1}, {"a": 3}]\n'
       'dados := [{"x": 1.0, "y": 2.0}, {"x": 2.0, "y": 4.0}]\n'
       'm := train "linear" using {"linhas": dados, "alvo": "y", "colunas": ["x"]}\n'
       'out predict m using [{"x": 3.0}]',
       ["FrameExpression", "TrainExpression", "PredictExpression"],
       "São açúcar fino sobre `Arcane.Analytics` e `Arcane.Cortex` — não "
       "reimplementam nada."),
]


# ═══════════════════════════════════════════════════════════
#  A precedência — da mais fraca para a mais forte
# ═══════════════════════════════════════════════════════════

PRECEDENCIA = [
    {"nivel": 1, "nome": "pipeline", "operadores": [">>"], "associa": "esquerda"},
    {"nivel": 2, "nome": "ternario", "operadores": ["given … otherwise"], "associa": "direita"},
    {"nivel": 3, "nome": "coalesce", "operadores": ["??"], "associa": "esquerda"},
    {"nivel": 4, "nome": "ou", "operadores": ["or"], "associa": "esquerda"},
    {"nivel": 5, "nome": "e", "operadores": ["and"], "associa": "esquerda"},
    {"nivel": 6, "nome": "nao", "operadores": ["not"], "associa": "prefixo"},
    {"nivel": 7, "nome": "comparacao", "operadores":
        ["is", "isnt", "bigger", "smaller", "bigger_eq", "smaller_eq", "in", "not in"],
     "associa": "encadeia"},
    {"nivel": 8, "nome": "soma", "operadores": ["+", "-"], "associa": "esquerda"},
    {"nivel": 9, "nome": "produto", "operadores": ["*", "/", "%", "~/"], "associa": "esquerda"},
    {"nivel": 10, "nome": "unario", "operadores": ["-x", "+x"], "associa": "prefixo"},
    {"nivel": 11, "nome": "potencia", "operadores": ["**"], "associa": "direita"},
    {"nivel": 12, "nome": "posfixo", "operadores": ["a.b", "a?.b", "a(…)", "a[…]"],
     "associa": "esquerda"},
]

#: Expressões em que a precedência DECIDE o resultado, e o que fica na raiz.
#: `(classe, operador)` — o operador é `None` quando o nó não tem um.
CONFERENCIAS_DE_PRECEDENCIA = [
    ("1 + 2 * 3", ("BinaryOp", "+")),
    ("2 * 3 ** 2", ("BinaryOp", "*")),
    ("-2 ** 2", ("UnaryOp", "-")),
    ("1 + 2 bigger 2", ("ComparisonOp", "bigger")),
    ("not a and b", ("LogicalOp", "and")),
    ("a or b and c", ("LogicalOp", "or")),
    ("a ?? b or c", ("CoalesceOp", None)),
    ("1 given a otherwise b ?? 2", ("TernaryExpression", None)),
    # O corpo de um 'morph' NAO absorve um ternario sem parenteses: sem
    # eles, 'given' abre uma instrucao. Com eles, o pipeline fica na raiz.
    ("xs >> morph n: (n given n bigger 0 otherwise 0)", ("PipelineExpression", None)),
    ("xs >> sift n: n bigger 1 >> morph n: n * 2", ("PipelineExpression", None)),
    ("7 - 3 - 1", ("BinaryOp", "-")),
]

#: A associatividade, conferida pela FORMA da árvore: qual lado da raiz
#: guarda o resto. `(expressao, lado, classe_do_lado)`.
CONFERENCIAS_DE_ASSOCIACAO = [
    ("7 - 3 - 1", "left", "BinaryOp"),              # (7 - 3) - 1
    ("8 / 4 / 2", "left", "BinaryOp"),
    ("2 ** 3 ** 2", "right", "BinaryOp"),           # 2 ** (3 ** 2)
    ("a ?? b ?? c", "left", "CoalesceOp"),
    ("a or b or c", "left", "LogicalOp"),
    ("1 given a otherwise 2 given b otherwise 3", "else_value", "TernaryExpression"),
    # A comparacao ENCADEIA, como na matematica: 'a smaller b smaller c'
    # e 'a smaller b and b smaller c', e nao '(a smaller b) smaller c'.
    ("1 smaller 2 smaller 3", "left", "ComparisonOp"),
]


# ═══════════════════════════════════════════════════════════
#  Consultas — o que Arcane.Gramatica e a CLI usam
# ═══════════════════════════════════════════════════════════

def producao(nome):
    for p in PRODUCOES:
        if p["nome"] == nome:
            return p
    return None


def do_grupo(grupo):
    return [p for p in PRODUCOES if p["grupo"] == grupo]


def _arvore(texto, arquivo="<gramatica>"):
    from .lexer import tokenize
    from .parser import parse
    fonte = texto if texto.endswith("\n") else texto + "\n"
    return parse(tokenize(fonte, arquivo), arquivo)


def classes_em(no, acumulado=None):
    """Todas as classes de nó que aparecem na árvore."""
    acc = set() if acumulado is None else acumulado
    if isinstance(no, (list, tuple)):
        for x in no:
            classes_em(x, acc)
    elif isinstance(no, dict):
        for x in no.values():
            classes_em(x, acc)
    elif dataclasses.is_dataclass(no) and not isinstance(no, type):
        acc.add(type(no).__name__)
        for campo in dataclasses.fields(no):
            classes_em(getattr(no, campo.name), acc)
    return acc


def conferir_producao(p):
    """`None` quando o exemplo produz o que a produção promete; o motivo, senão."""
    try:
        arvore = _arvore(p["exemplo"])
    except Exception as e:      # noqa: BLE001 — o motivo vira o relatório
        return f"o parser recusou o exemplo: {e}"
    achadas = classes_em(arvore.body)
    faltando = [c for c in p["contem"] if c not in achadas]
    if faltando:
        return f"a árvore não tem {', '.join(faltando)}"
    return None


def raiz_da_expressao(texto):
    """`(classe, operador)` do nó na raiz de uma expressão."""
    v = _arvore(f"__x := {texto}").body[0].value
    return (type(v).__name__, getattr(v, "op", None))


def validar(texto):
    """`{ok, erros}` — só lexer e parser, sem executar e sem analisar tipos."""
    from .errors import DataForgeError
    try:
        arvore = _arvore(texto)
    except DataForgeError as e:
        erros = [e] + list(getattr(e, "outros", ()))
        return {"ok": False, "instrucoes": 0, "erros": [
            {"linha": getattr(x, "line", 0), "coluna": getattr(x, "column", 0),
             "mensagem": getattr(x, "message", str(x)),
             "tipo": type(x).__name__} for x in erros]}
    return {"ok": True, "instrucoes": len(arvore.body), "erros": []}


def instrucoes(texto):
    """A classe de cada instrução de topo — o que o parser entendeu."""
    return [type(n).__name__ for n in _arvore(texto).body]


def tokens(texto):
    from .lexer import tokenize
    fonte = texto if texto.endswith("\n") else texto + "\n"
    return [{"tipo": t.type.name, "valor": t.value, "linha": t.line,
             "coluna": t.column} for t in tokenize(fonte, "<gramatica>")
            if t.type.name not in ("EOF",)]


def palavras():
    """As reservadas (não podem ser nome) e as contextuais (só onde confirmam)."""
    from .tokens import KEYWORDS
    reservadas = sorted(KEYWORDS)
    try:
        from .exemplos_palavras import PALAVRAS     # nome -> (descricao, exemplo)
        todas = list(PALAVRAS)
    except Exception:           # noqa: BLE001
        todas = []
    contextuais = sorted(set(t for t in todas if t) - set(reservadas))
    return {"reservadas": reservadas, "contextuais": contextuais}


def ebnf(grupo=""):
    """O texto EBNF de um grupo, ou da gramática inteira."""
    ps = do_grupo(grupo) if grupo else PRODUCOES
    return "\n\n".join(p["ebnf"] for p in ps) + "\n"


# ═══════════════════════════════════════════════════════════
#  dataforge gramatica
# ═══════════════════════════════════════════════════════════

def executar(args, flags):
    """`dataforge gramatica [producao|grupo]` — devolve o código de saída."""
    import json as _json
    from .cli import color

    if "--precedencia" in flags:
        if "--json" in flags:
            print(_json.dumps(PRECEDENCIA, ensure_ascii=False, indent=2))
            return 0
        print(color("  Precedencia — da mais fraca para a mais forte", "1;36"))
        print()
        for n in PRECEDENCIA:
            print(f"  {n['nivel']:>2}  {n['nome']:<11} {'  '.join(n['operadores'])}"
                  + color(f"   ({n['associa']})", "0;90"))
        print()
        print(color("  Cada nivel e conferido contra o parser: "
                    "tests/test_gramatica.py", "0;90"))
        return 0

    alvo = args[0] if args else ""
    grupos = {g[0]: g for g in GRUPOS}
    if alvo and alvo not in grupos and producao(alvo) is None:
        import difflib
        nomes = [p["nome"] for p in PRODUCOES] + list(grupos)
        perto = difflib.get_close_matches(alvo, nomes, 1)
        print(color(f"  nao ha producao nem grupo '{alvo}'.", "1;31")
              + (f" Voce quis dizer '{perto[0]}'?" if perto else ""))
        print("  'dataforge gramatica' lista os grupos.")
        return 1

    if alvo in grupos:
        escolhidas = do_grupo(alvo)
    elif alvo:
        escolhidas = [producao(alvo)]
    else:
        escolhidas = []

    if "--json" in flags:
        print(_json.dumps(escolhidas or PRODUCOES, ensure_ascii=False, indent=2))
        return 0
    if "--ebnf" in flags:
        print(ebnf(alvo if alvo in grupos else ""), end="")
        return 0

    if not alvo:
        print(color(f"  A gramatica: {len(PRODUCOES)} producoes em {len(GRUPOS)} grupos", "1;36"))
        print()
        for gid, nome, resumo in GRUPOS:
            ps = do_grupo(gid)
            print(f"  {gid:<13} {nome:<20}" + color(f" {len(ps):>2}  {resumo}", "0;90"))
            print(color("                " + ", ".join(p["nome"] for p in ps), "0;90"))
        print()
        print("  dataforge gramatica <grupo|producao>   o EBNF, o exemplo e a nota")
        print("  dataforge gramatica --ebnf             a gramatica inteira, so o EBNF")
        print("  dataforge gramatica --precedencia      a tabela, da mais fraca a mais forte")
        return 0

    for p in escolhidas:
        print(color(f"  {p['nome']}", "1;37") + color(f"  ({p['grupo']})", "0;90"))
        print()
        for linha in p["ebnf"].splitlines():
            print(f"    {linha}")
        print()
        print(color("    exemplo — aceito pelo parser, com "
                    + ", ".join(p["contem"]), "0;90"))
        for linha in p["exemplo"].splitlines():
            print(f"      {linha}")
        if p["nota"]:
            print()
            print(f"    {p['nota']}")
        print()
    return 0
