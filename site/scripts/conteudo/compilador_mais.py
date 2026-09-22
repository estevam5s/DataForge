# -*- coding: utf-8 -*-
"""Dentro do compilador — a página-raiz (que respondia 404) e oito
páginas: lexer, parser, dominância, o grafo desenhado, variáveis vivas,
o analisador, a chamada de cauda e o cache de árvores.

`Comp.dominancia` e `Comp.dot` entraram nesta leva, e o parser passou a
recusar duas instruções na mesma linha — defeito achado escrevendo a
página de estruturas.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador",
"title": "Dentro do compilador",
"description": "Do texto ao que roda: as oito fases, o que cada uma entrega, e como ver cada uma de dentro da linguagem.",
"blocos": [
 {"p": "Um arquivo `.df` atravessa oito fases antes de rodar, e **todas** podem ser vistas de dentro da linguagem, pelo `Arcane.Compilador`, ou da linha de comando, por `dataforge ir`. Nenhuma é caixa-preta: o que o analisador conclui, o grafo em que ele concluiu e o que o backend compilou são dados que um programa lê."},
 {"code": '''adopt Arcane.Compilador as Comp

assert Comp.fases() is ["lexer", "parser", "hir", "mir", "analises", "ssa", "otimizado", "lir"]
out Comp.tokens("x := 1 + 2")[0]''', "lang": "df"},
 {"table": {"head": ["Fase", "Recebe", "Entrega", "Página"], "rows": [
   ["lexer", "o texto", "tokens com linha e coluna", "[Lexer](/docs/compilador/lexer)"],
   ["parser", "tokens", "a árvore sintática", "[Parser](/docs/compilador/parser)"],
   ["analisador", "a árvore", "erros e avisos, antes de rodar", "[O analisador](/docs/compilador/analisador)"],
   ["HIR", "a árvore", "a árvore sem açúcar", "[HIR](/docs/compilador/hir)"],
   ["MIR", "o HIR", "blocos básicos e arestas", "[MIR](/docs/compilador/mir)"],
   ["análises", "o MIR", "vivas, constantes, alcance", "[O que o fluxo prova](/docs/compilador/analises)"],
   ["SSA", "o MIR", "uma definição por nome, com φ", "[SSA](/docs/compilador/ssa)"],
   ["LIR", "a árvore", "o que o compilador de fechamentos cobriu", "[Backend](/docs/compilador/backend)"]]}},
 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/compilador/pipeline", "title": "O caminho de compilação", "desc": "as fases em sequência, com o custo de cada uma"},
   {"href": "/docs/compilador/lexer", "title": "Lexer", "desc": "INDENT, DEDENT, e por que // às vezes é divisão"},
   {"href": "/docs/compilador/parser", "title": "Parser", "desc": "descida recursiva, precedência e a recuperação de erro"},
   {"href": "/docs/compilador/analisador", "title": "O analisador", "desc": "o que ele prova, e por que cala quando não prova"},
   {"href": "/docs/compilador/dominancia", "title": "Dominância", "desc": "por onde todo caminho passa, e onde vão os φ"},
   {"href": "/docs/compilador/visualizar", "title": "Desenhar o grafo", "desc": "o fluxo em DOT, para o Graphviz"},
   {"href": "/docs/compilador/vivas", "title": "Variáveis vivas", "desc": "o valor que ainda vai ser lido"},
   {"href": "/docs/compilador/cauda", "title": "Chamada de cauda", "desc": "a recursão sem teto, e as quatro recusas"},
   {"href": "/docs/compilador/cache", "title": "O cache de árvores", "desc": "93% do parse, e a chave que impede o desastre"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/lexer",
"title": "O lexer",
"description": "Texto em tokens: indentação vira INDENT e DEDENT, a interpolação vira partes, e // decide entre comentário e divisão.",
"blocos": [
 {"p": "O lexer lê o texto caractere por caractere e entrega **tokens**: cada um com tipo, valor, linha e coluna. É a linha e a coluna que fazem todo erro posterior apontar o lugar certo — um token sem posição produziria um erro sem seta."},
 {"code": '''adopt Arcane.Compilador as Comp

tipos := [t["tipo"] cycle t in Comp.tokens("given x bigger 1:\\n    out x\\n")]
assert tipos.contains("INDENT") and tipos.contains("DEDENT")
assert Comp.tokens("total := 7")[2] is {"tipo": "INTEGER", "valor": 7, "linha": 1, "coluna": 10}''', "lang": "df"},
 {"h2": "A indentação vira token"},
 {"p": "A linguagem marca bloco por recuo, e o parser não conta espaços: o lexer mantém uma pilha de recuos e emite `INDENT` quando o recuo cresce e um `DEDENT` para **cada nível** que fecha. Tabulação é recusada (`SyncError`) — dois editores mostram um tab com larguras diferentes, e um bloco pareceria certo em um e errado no outro."},
 {"h2": "`//`: comentário ou divisão?"},
 {"p": "`//` é **comentário** por padrão, e vira divisão inteira só quando o que vem depois é um número, `(`, ou uma chamada/índice/membro. É por isso que `total // 2` divide e `total // nota` comenta — e é a regra que exige cuidado com comentário que começa com número:"},
 {"code": '''adopt Arcane.Compilador as Comp

divide := [t["tipo"] cycle t in Comp.tokens("x := a // 2")]
comenta := [t["tipo"] cycle t in Comp.tokens("x := a // metade")]
assert divide.contains("FLOOR_DIV")
assert not comenta.contains("FLOOR_DIV")''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Comentário que começa com número", "texto": "`total := 12   // 3 parcelas` divide 12 por 3, e `parcelas` vira uma segunda instrução na mesma linha. Desde esta versão o parser recusa isso com uma dica sobre o `//`. Comece o comentário com uma palavra, ou use `#`. A forma recomendada para dividir é `~/`, que nunca é comentário."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/parser",
"title": "O parser",
"description": "Descida recursiva: uma função por nível de precedência, a recuperação que junta vários erros, e o fim de linha exigido.",
"blocos": [
 {"p": "O parser é **descendente recursivo**: uma função por construção da gramática, e uma por nível de precedência. `1 + 2 * 3` vira `+` na raiz porque a função da soma chama a da multiplicação para ler cada lado — a precedência está na **ordem das chamadas**, e não numa tabela."},
 {"code": '''adopt Arcane.Compilador as Comp

raiz := Comp.arvore("x := 1 + 2 * 3")["corpo"][0]["valor"]
assert raiz["op"] is "+"
assert raiz["direita"]["op"] is "*"               // o * ficou mais fundo: liga mais forte''', "lang": "df"},
 {"table": {"head": ["Do mais fraco", "ao mais forte"], "rows": [
   ["`>>` (pipeline)", "a mais fraca de todas"],
   ["`a given c otherwise b`", "o ternário"],
   ["`??`", "abaixo de `or` — `x ?? 0 is 0` é `x ?? (0 is 0)`: o `check` avisa"],
   ["`or` · `and` · `not`", ""],
   ["`is`, `bigger`, `smaller`…", "encadeiam: `1 smaller x smaller 9`"],
   ["`+ -` · `* / ~/ %` · `**`", "`**` associa à direita"],
   ["unário, chamada, índice, membro", "o mais forte"]]}},
 {"h2": "Vários erros de uma vez"},
 {"p": "Um parser que para no primeiro erro obriga a corrigir, compilar e corrigir uma vez por erro. Este registra o erro, **ressincroniza** no começo da próxima instrução e continua: quem lê recebe os quatro erros do arquivo de uma vez. O erro que viaja continua sendo um só, e os demais vão em `outros`."},
 {"h2": "Uma instrução por linha"},
 {"p": "Depois de uma instrução completa, a linha tem de acabar. `x := 1 vazios` era aceito como duas instruções — `x := 1` e `vazios` —, e o caso que custou caro foi o comentário começando com número, que virava uma divisão seguida de uma instrução solta. Dezessete blocos desta documentação só \"compilavam\" por isso; hoje todos compilam de verdade."},
 {"code": '''adopt Arcane.Compilador as Comp

recusado := no
monitor:
    Comp.arvore("x := 1 vazios")
handle Error as e:
    recusado := e.message.contains("same line")
assert recusado''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/analisador",
"title": "O analisador estático",
"description": "Nomes, aridade, tipos, alcance, membros atravessando arquivos — e a regra de só falar quando consegue provar.",
"blocos": [
 {"p": "`dataforge check` roda o analisador sobre a árvore, sem executar nada. Ele pega o erro que num arquivo pequeno aparece na primeira execução — e que num sistema de duzentos arquivos aparece em produção."},
 {"table": {"head": ["Pega", "Exemplo"], "rows": [
   ["nome não definido, com sugestão", "`totl` → \"você quis dizer 'total'?\""],
   ["aridade", "`somar(1)` numa ação de dois parâmetros"],
   ["tipo de parâmetro e de retorno", "`dobro(\"x\")` com `n: Integer`"],
   ["membro que não existe", "`p.clientte` num record — também atravessando `adopt`"],
   ["código inalcançável", "depois de `yield`, ou `point` depois de uma captura"],
   ["ciclo de import", "com a cadeia inteira: `a.df → b.df → a.df`"],
   ["escrita concorrente", "uma rota escrevendo num nome de fora"],
   ["`??` que engole comparação", "`v[k] ?? void is void`"]]}},
 {"h2": "Otimista de propósito"},
 {"p": "Quando não consegue **provar** que algo está errado, ele cala. Um falso alarme ensina a ignorar mensagens — e aí o alarme verdadeiro é ignorado junto. Por isso ele se cala sobre o membro de um blueprint que herda de algo não visto, sobre o tipo depois de uma ação decorada, e sobre a chave de um vault que alguém escreveu em outro lugar."},
 {"code": '''adopt Arcane.Compilador as Comp

// o analisador vê o fluxo: 'y' só existe num dos caminhos
aviso := Comp.onde_talvez_nao_definidas("action f(x):\\n    given x bigger 0:\\n        y := 1\\n    yield y\\n")
out aviso''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Silenciar uma regra, nomeando-a", "texto": "`// df: permitir <regra>` na linha, ou na de cima. A regra tem de ser nomeada: um `permitir` solto esconderia o próximo erro, que ninguém pediu para esconder."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/dominancia",
"title": "Dominância",
"description": "Um bloco domina outro quando todo caminho passa por ele — e a fronteira da dominância é onde os φ vão.",
"blocos": [
 {"p": "No grafo de fluxo, o bloco A **domina** B quando todo caminho da entrada até B passa por A. Alcançar é poder chegar; dominar é não haver como chegar por outro lado. A distinção decide onde duas definições de um nome se encontram — e portanto onde o SSA põe um φ."},
 {"code": '''adopt Arcane.Compilador as Comp

fonte := "action f(x):\\n    given x bigger 0:\\n        y := 1\\n    otherwise:\\n        y := 2\\n    yield y\\n"
d := Comp.dominancia(fonte, "f")

assert d["dominadores"]["1"] is [0, 1]      // o ramo 'sim' só é dominado pela entrada e por si
assert d["imediato"]["3"] is 0              // a junção: nenhum dos ramos a domina
assert d["fronteira"]["1"] is [3]           // a dominância do ramo acaba na junção
assert d["fronteira"]["2"] is [3]           // e a do outro também: ali vai o φ de 'y' ''', "lang": "df"},
 {"table": {"head": ["Pergunta", "Campo"], "rows": [
   ["por quais blocos todo caminho até B passa?", "`dominadores`"],
   ["qual é o mais próximo deles?", "`imediato` — a árvore de dominância"],
   ["onde a dominância de B acaba?", "`fronteira` — onde os φ vão"]]}},
 {"p": "As três respostas saem do **mesmo** cálculo que o SSA usa. Duas contas independentes poderiam discordar, e aí o que esta página mostra e o que o compilador faz seriam coisas diferentes. Ver [SSA e o nó φ](/docs/compilador/ssa)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/visualizar",
"title": "Desenhar o grafo",
"description": "O grafo de fluxo em DOT: blocos, arestas rotuladas, e o código que nunca roda tracejado.",
"blocos": [
 {"p": "Um grafo de fluxo lido como texto é difícil de acompanhar a partir de dez blocos. `Comp.dot` o escreve no formato do **Graphviz**, e o desenho mostra de uma vez o que o texto espalha: os ramos, o laço voltando, e o que nunca roda."},
 {"code": '''adopt Arcane.Compilador as Comp

fonte := "action f(n):\\n    total := 0\\n    cycle i from 1 to n:\\n        total += i\\n    yield total\\n    out \\"nunca\\"\\n"
dot := Comp.dot(fonte, "f")
out dot

assert dot.starts_with("digraph fluxo {")
assert dot.contains('[label="volta"]')            // a aresta que fecha o laço
assert dot.contains("style=dashed")                // o 'out' depois do yield''', "lang": "df"},
 {"code": '''IO.write("fluxo.dot", Comp.dot(IO.read("pedido.df")))
// no terminal:  dot -Tsvg fluxo.dot -o fluxo.svg''', "lang": "text"},
 {"table": {"head": ["No desenho", "Quer dizer"], "rows": [
   ["uma caixa", "um bloco básico: instruções que rodam sempre juntas"],
   ["`sim` / `nao`", "os dois lados de uma condição"],
   ["`volta`", "a aresta que fecha um laço"],
   ["`erro`", "o caminho de um `monitor` para o `handle`"],
   ["caixa tracejada e cinza", "bloco que nenhum caminho alcança"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/vivas",
"title": "Variáveis vivas",
"description": "Um valor está vivo enquanto ainda vai ser lido: a análise que acha o parâmetro esquecido e a conta inútil.",
"blocos": [
 {"p": "Uma variável está **viva** num ponto do programa quando o valor dela ainda vai ser lido por algum caminho a partir dali. É a análise que diz qual cálculo é inútil (o resultado nunca é lido) e qual parâmetro sobrou (nunca é lido em caminho nenhum)."},
 {"code": '''adopt Arcane.Compilador as Comp

fonte := "action preco(base, desconto, taxa):\\n    final := base * 1.1\\n    yield final\\n"
vivas := Comp.vivas(fonte, "preco")
out vivas
assert vivas["0"] is ["base"]           // 'desconto' e 'taxa' nunca são lidos''', "lang": "df"},
 {"p": "A análise corre **para trás**: sai do fim de cada bloco e sobe, porque é o futuro de um ponto que decide se o valor ainda serve. E junta os caminhos — num `given`, uma variável lida em qualquer dos ramos está viva antes dele."},
 {"table": {"head": ["Resultado", "Quer dizer"], "rows": [
   ["parâmetro nunca vivo", "ele sobrou — ou a ação esqueceu de usá-lo"],
   ["atribuição cujo nome não está vivo depois", "a conta é jogada fora"],
   ["nome vivo na entrada que não é parâmetro", "ele é lido antes de ser escrito: vem de fora, ou é erro"]]}},
 {"p": "É a mesma família de análise que produz o aviso `talvez-nao-definida`: ver [O que o fluxo prova](/docs/compilador/analises)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/cauda",
"title": "Chamada de cauda",
"description": "yield f(…) vira salto, e a recursão perde o teto — com as quatro recusas que mantêm isso correto.",
"blocos": [
 {"p": "Cada chamada de ação ocupa um quadro, e o teto é de mil quadros: uma recursão de cinco mil níveis estoura, mesmo sem nada de infinito. Mas quando a chamada é o **retorno inteiro** — `yield f(…)` —, não há nada a fazer depois dela, e o quadro só existiria para repassar o resultado. O compilador troca a chamada por um **salto**, reaproveitando o quadro."},
 {"code": '''action contar(n, acc := 0):
    given n is 0:
        yield acc
    yield contar(n - 1, acc + 1)           // cauda: nada depois dela

assert contar(200000) is 200000             // sem teto

action ingenua(n):
    given n is 0:
        yield 0
    yield 1 + ingenua(n - 1)               // NÃO é cauda: ainda falta somar 1

estourou := no
monitor:
    ingenua(5000)
handle StackOverflowError:
    estourou := yes
assert estourou''', "lang": "df"},
 {"h2": "As quatro recusas"},
 {"table": {"head": ["Não vira salto quando", "Porque"], "rows": [
   ["há `defer` na ação", "ele roda na saída do quadro, e o salto reusa o quadro"],
   ["o `yield` está dentro de `monitor`", "o `handle` precisa ver o que a chamada levanta"],
   ["a recursão é indireta (`f` → `g` → `f`)", "a análise olha uma ação por vez"],
   ["**todo** `yield` da ação é cauda", "ela nunca devolveria: virar laço infinito calado seria pior que o erro"]]}},
 {"p": "A última é a mais importante: sem ela, `action r(n): yield r(n + 1)` deixaria de dar `StackOverflowError` e passaria a travar para sempre."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/cache",
"title": "O cache de árvores",
"description": "A árvore guardada entre execuções: 93% do parse — e a chave que impede de rodar a árvore de outro arquivo.",
"blocos": [
 {"p": "Ler e analisar sintaticamente um arquivo custa tempo toda vez que ele roda. O cache guarda a **árvore** — e não código compilado, que não atravessa processo — e a devolve enquanto o arquivo não muda."},
 {"table": {"head": ["Medida", "Sem cache", "Com"], "rows": [
   ["o parse de 269 arquivos", "258,7 ms", "**17,9 ms**"],
   ["`dataforge check exercicios`", "0,918 s", "**0,524 s**"],
   ["`dataforge run` de um arquivo de 383 linhas", "131,8 ms", "4,4% menos"]]}},
 {"p": "A terceira linha é a honesta: num arquivo só, a maior parte do tempo é o `import` do próprio Python. O cache vale onde há muitos arquivos — o `check` de um projeto, a suíte de testes."},
 {"h2": "A chave"},
 {"p": "Um cache que devolve a árvore errada é pior que nenhum: o programa roda, e roda **outra coisa**. A chave carrega o caminho, o instante de modificação em nanossegundos, o tamanho, a versão da linguagem, e um resumo do próprio lexer e parser — mexer no parser sem subir a versão não pode deixar árvores velhas valendo."},
 {"code": '''DATAFORGE_SEM_CACHE=1 dataforge run programa.df     # desliga, para medir''', "lang": "bash"},
 {"p": "Toda falha do cache cai no caminho normal, e a gravação é feita ao lado e trocada de uma vez: um processo interrompido não deixa arquivo pela metade."},
]},
]
