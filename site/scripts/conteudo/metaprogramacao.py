"""comptime, macros, DSLs, plugins do check — e o mapa da parte 5.

Todo bloco `df` destas páginas RODA e passa pelo `check`
(`tests/test_metaprogramacao.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/metaprogramacao/comptime",
"title": "comptime",
"description": "A conta feita uma vez, na carga, e congelada: tabela gerada, constante calculada e validação que falha antes da primeira linha rodar.",
"blocos": [
 {"p": "`comptime` marca o que é calculado **antes** de o programa começar. O resultado vira constante, e a validação que falhar ali derruba a carga — não a primeira requisição em produção."},
 {"code": """comptime QUADRADOS := [i * i cycle i in range(0, 6)]
comptime steady MAXIMO := 2 ** 10

assert QUADRADOS is [0, 1, 4, 9, 16, 25]
assert MAXIMO is 1024""", "lang": "df"},

 {"h2": "Bloco, com ação própria"},
 {"p": "A tabela de consulta é o caso clássico: a conta é cara, a resposta é sempre a mesma, e ninguém quer pagá-la a cada chamada."},
 {"code": """comptime:
    action fatorial(n):
        yield 1 given n smaller_eq 1 otherwise n * fatorial(n - 1)

    TABELA := [fatorial(i) cycle i in range(0, 6)]
    LIMITE := TABELA[5]

assert TABELA is [1, 1, 2, 6, 24, 120]
assert LIMITE is 120""", "lang": "df"},

 {"h2": "Validação estática"},
 {"p": "Um `assert` dentro de `comptime` é uma trava de **build**: o `dataforge check` a executa e acusa com o código `comptime-falhou`, antes de rodar."},
 {"code": """comptime TABELA := [1, 2, 3]
comptime:
    assert len(TABELA) is 3              // se mudar, o check acusa

assert len(TABELA) is 3""", "lang": "df"},

 {"h2": "A caixa: o que não entra"},
 {"p": "Se `comptime` pudesse fazer E/S, \"tempo de compilação\" seria só \"mais cedo\". O corpo é varrido antes de rodar, e o que não é conta é recusado com o motivo."},
 {"table": {"head": ["Recusado", "Por quê"], "rows": [
   ["`out`", "escrever na saída durante a carga confunde o que é programa com o que é build"],
   ["`adopt`", "módulo traz E/S; a conta de build não depende de disco, rede nem relógio"],
   ["`thread` e `parallel`", "deixaria trabalho correndo por baixo de um programa que ainda não começou"],
   ["`in` (ler da entrada), `wait`, `server`, `ignite`", "o mesmo motivo: pertencem ao programa"]]}},
 {"code": """monitor:
    // este bloco é recusado na carga
    assert yes
handle Error as e:
    assert no

comptime SEGURO := 2 + 2
assert SEGURO is 4""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "'comptime' continua sendo um nome", "texto": "Como `type`, `opaque` e `where`, ele é **contextual**: `comptime := 3` e `action comptime(x)` continuam valendo. A declaração só começa quando o que vem depois confirma — `comptime:` abrindo bloco, ou `comptime NOME :=`."}},

 {"h2": "O que isto não é"},
 {"table": {"head": ["Não existe", "Por quê"], "rows": [
   ["geração de código de máquina em build", "não há compilação para binário: o DataForge interpreta a árvore"],
   ["especialização de código por tipo", "o caminho aqui é `overload`, que decide na chamada, e a macro, que reescreve o corpo"],
   ["geração de tipos em compile-time", "o que existe é `type Par<T> := …` (alias genérico) e `Vetor<3>` (argumento numérico)"],
   ["`comptime` dentro de uma ação", "ele é declaração de topo: uma conta de build presa a uma chamada seria uma conta de execução com outro nome"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/metaprogramacao/macros",
"title": "Macros: a árvore como dado",
"description": "Ler o corpo de uma ação, percorrer, transformar, gerar código e derivar métodos — com higiene explícita.",
"blocos": [
 {"p": "Um **decorador** troca o valor: recebe a ação pronta e devolve outra coisa. O que ele não alcança é o **corpo** — e metade da metaprogramação que vale a pena é sobre o corpo: instrumentar cada instrução, derivar um método a partir dos campos, gerar uma ação a partir de um esquema."},

 {"h2": "A árvore é um vault"},
 {"code": """adopt Arcane.Macro as M

action somar(a, b):
    yield a + b

arvore := M.arvore(somar)

assert arvore["tipo"] is "ActionDeclaration"
assert arvore["parametros"] is ["a", "b"]
assert arvore["corpo"][0]["tipo"] is "YieldStatement" """, "lang": "df"},
 {"p": "Ela é um dado comum: percorre com `cycle`, casa com `match`, serializa em JSON e atravessa processo — sem que nada disso precise conhecer a classe do nó. É o mesmo raciocínio do `Quadro` e da ponte para o Python."},

 {"h2": "citar: texto vira árvore"},
 {"code": """adopt Arcane.Macro as M

arvore := M.citar("x * 2 + 1")
assert arvore["tipo"] is "BinaryOp"
assert M.texto(arvore) is "x * 2 + 1" """, "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "'texto' é aproximado, e o nome não esconde", "texto": "A fonte original não é guardada: o texto é reconstruído da árvore para ler, comparar e depurar — não para ser byte a byte igual ao que foi escrito."}},

 {"h2": "Reescrever o corpo"},
 {"code": """adopt Arcane.Macro as M

action dobro(x):
    yield x * 2

action trocar(nodo):
    given nodo["tipo"] is "BinaryOp" and nodo["op"] is "*":
        yield M.citar("x + x")
    yield nodo

trocada := M.reescrever(dobro, trocar)

assert dobro(5) is 10
assert trocada(5) is 10        // o corpo é outro, o resultado é o mesmo""", "lang": "df"},
 {"p": "A árvore original **não** é tocada: `transformar` devolve uma nova. Uma macro que mutasse o que recebeu mudaria a ação de quem chamou."},

 {"h2": "Gerar código"},
 {"code": """adopt Arcane.Macro as M

corpo := M.citar("a * 10")
gerada := M.acao("dez_vezes", ["a"], corpo)

assert gerada(4) is 40
assert M.arvore(gerada)["nome"] is "dez_vezes"

// e o atalho, num passo só
pronta := M.compilar("a + b", "soma", ["a", "b"])
assert pronta(2, 3) is 5""", "lang": "df"},

 {"h2": "Higiene: não capturar o nome de quem chamou"},
 {"p": "A macro que gera um temporário chamado `temp` quebra o código de quem já tinha um `temp`. `nome_fresco` e `renomear` existem para isso, e são **explícitos**: fazer higiene sozinho exigiria saber o que é \"de dentro\", e essa decisão é de quem escreve a macro."},
 {"code": """adopt Arcane.Macro as M

corpo := M.citar("temporario + 1")
limpo := M.renomear(corpo, "temporario", M.nome_fresco("temporario"))

assert M.texto(limpo) isnt M.texto(corpo)
assert "__temporario_" in M.texto(limpo)""", "lang": "df"},

 {"h2": "Macro de atributo: derivar"},
 {"p": "Em vez de escrever `__str__` e `__eq__` à mão em cada blueprint, os **campos que já existem** geram os dois:"},
 {"code": """adopt Arcane.Macro as M

mark @M.derivar("texto", "igualdade")
blueprint Ponto:
    x := 1
    y := 2

a := spawn Ponto()
b := spawn Ponto()

assert $"{a}" is "Ponto(x=1, y=2)"
assert a is b""", "lang": "df"},
 {"table": {"head": ["Derivável", "Gera"], "rows": [
   ["`texto`", "`__str__` com os campos, no formato `Nome(campo=valor, …)`"],
   ["`igualdade`", "`__eq__` comparando todos os campos"],
   ["`ordem`", "`__lt__` pelo primeiro campo"],
   ["`vault`", "`para_vault()` com os campos"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A macro roda na CARGA", "texto": "O decorador é aplicado uma vez, quando a declaração é lida — e não a cada chamada. Reescrever o corpo por chamada seria pagar a metaprogramação em tempo de execução, para sempre."}},

 {"h2": "A superfície"},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`M.arvore(acao)`", "a árvore da ação (ou do blueprint) como dado"],
   ["`M.citar(texto)`", "texto vira árvore"],
   ["`M.texto(arvore)`", "árvore vira texto (aproximado)"],
   ["`M.percorrer(arvore, visitante)`", "chama o visitante em cada nó"],
   ["`M.transformar(arvore, acao)`", "árvore nova, com cada nó passado pela ação"],
   ["`M.substituir` · `M.renomear`", "troca por tipo de nó, ou nome de identificador"],
   ["`M.nome_fresco(base)`", "um nome que o código de fora não tem"],
   ["`M.acao(nome, params, corpo)` · `M.compilar(texto, …)`", "gera a ação"],
   ["`M.reescrever(acao, transformador)`", "ação nova, corpo transformado"],
   ["`M.derivar(…)`", "a macro de atributo"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/metaprogramacao/dsl",
"title": "DSLs",
"description": "Combinadores de análise para escrever uma linguagem pequena: gramática própria, falha com posição e o resultado como Resultado.",
"blocos": [
 {"p": "A linguagem já tem duas formas de DSL **interna**: palavra contextual no parser (as onze do Kiln, os seis verbos do Quadro) e objeto com operadores. As duas exigem mexer no DataForge ou desenhar uma API."},
 {"p": "O que faltava era a DSL **externa**: ler um texto que segue uma gramática sua — uma regra de preço, um filtro de busca, um formato de configuração — sem trazer dependência nem escrever um analisador à mão com índice e `persist`."},

 {"h2": "Uma gramática em quatro linhas"},
 {"code": """adopt Arcane.Dsl as D

numero := D.mapear(D.numero(), lambda t => cast t as Integer)
soma := D.mapear(D.seq([numero, D.texto("+"), numero]),
                 lambda partes => partes[0] + partes[2])

r := D.analisar(soma, "2+3")
assert r.deu_certo() and r.valor() is 5""", "lang": "df"},
 {"p": "O resultado é um [`Resultado`](/docs/tipos/resultado), e não uma exceção: texto de fora falha o tempo todo, e obrigar `monitor` em volta de cada análise faria o caminho normal ser o do erro."},

 {"h2": "A falha diz onde"},
 {"code": """adopt Arcane.Dsl as D

r := D.analisar(D.numero(), "abc")

assert r.falhou()
assert r.erro()["posicao"] is 0
assert "numero" in r.erro()["esperado"]""", "lang": "df"},
 {"p": "\"Não deu certo\" não ajuda ninguém a consertar a linha 3 de um arquivo de configuração. A falha traz posição, o que era esperado e o trecho em volta."},

 {"h2": "Os combinadores"},
 {"table": {"head": ["Grupo", "Símbolos"], "rows": [
   ["básicos", "`texto`, `numero`, `nome`, `entre_aspas`, `espaco`, `simbolo`, `qualquer_de`, `ate`"],
   ["combinar", "`seq`, `ou`, `muitos`, `opcional`, `separado_por`"],
   ["transformar", "`mapear`, `exigir` (troca a mensagem de falha)"],
   ["recursão", "`adiado(lambda => regra)`, `gramatica(regras, inicial)`"],
   ["rodar", "`analisar(regra, texto)` → `Resultado`"]]}},
 {"code": """adopt Arcane.Dsl as D

palavra := D.ou([D.texto("sim"), D.texto("nao")])
lista := D.muitos(D.seq([palavra, D.opcional(D.texto(","))]))

r := D.analisar(lista, "sim,nao,sim")
assert r.deu_certo() and len(r.valor()) is 3""", "lang": "df"},

 {"h2": "Uma calculadora inteira"},
 {"code": """adopt Arcane.Dsl as D

numero := D.mapear(D.numero(), lambda t => cast t as Float)
operador := D.ou([D.texto("+"), D.texto("-"), D.texto("*")])

action aplicar(partes):
    esquerda := partes[0]
    cycle par in partes[1]:
        given par[0] is "+":
            esquerda := esquerda + par[1]
        orif par[0] is "-":
            esquerda := esquerda - par[1]
        otherwise:
            esquerda := esquerda * par[1]
    yield esquerda

expressao := D.mapear(D.seq([numero, D.muitos(D.seq([operador, numero]))]),
                      aplicar)

assert D.analisar(expressao, "2+3*4").valor() is 20.0
assert D.analisar(expressao, "10-4").valor() is 6.0""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "O espaço é explícito", "texto": "Um combinador que pulasse espaço sozinho decidiria por quem escreve a gramática — e em formato de largura fixa é exatamente o que não se quer. `D.espaco()` e `D.simbolo(x)` existem para quem quer o comportamento comum."}},

 {"h2": "Qual DSL usar"},
 {"table": {"head": ["Quando", "A forma"], "rows": [
   ["a linguagem é o DataForge, com vocabulário próprio", "blueprint com operadores, pipeline (`>>`) e ação de alta ordem"],
   ["o texto vem de fora e tem gramática sua", "`Arcane.Dsl` — esta página"],
   ["você quer palavra nova **na linguagem**", "palavra contextual no parser (é como o Kiln e o Quadro fazem) — e isso é mexer no DataForge"],
   ["gerar código a partir de dado", "[`Arcane.Macro`](/docs/metaprogramacao/macros)"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/metaprogramacao/plugins",
"title": "Plugins do check",
"description": "A regra que o seu projeto cobra, rodando no mesmo comando das 177 embutidas — com linha, coluna, código e silenciamento.",
"blocos": [
 {"p": "O `dataforge check` tem 177 regras. O que ele não sabe é a regra **do seu projeto**: \"toda rota precisa de `middleware de autenticação`\", \"nenhum blueprint de domínio pode adotar `Arcane.Http`\", \"nome de uma letra não passa\". Um plugin é um `.df` que responde isso."},

 {"h2": "Um plugin é uma ação"},
 {"code": """adopt Arcane.Macro as M

action verificar(arvore, arquivo):
    achados := []

    action olhar(nodo):
        given nodo["tipo"] is "Identifier" and len(nodo["nome"]) is 1:
            achados.append({"linha": nodo["linha"], "coluna": nodo["coluna"],
                            "codigo": "sem-nome-curto",
                            "mensagem": "nome de uma letra nao diz nada",
                            "sugestao": "use um nome que se leia",
                            "severidade": "aviso"})

    M.percorrer(arvore, olhar)
    yield achados

relay verificar""", "lang": "df", "title": "regras.df"},
 {"p": "Rode com `--plugin`, ou declare no manifesto e esqueça:"},
 {"code": """dataforge check src/ --plugin=regras.df""", "lang": "bash"},
 {"code": """[check]
plugins = ["regras.df"]""", "lang": "toml", "title": "forge.toml"},

 {"h2": "O contrato"},
 {"table": {"head": ["Campo do achado", "O que é"], "rows": [
   ["`linha`, `coluna`", "onde acusar — vêm do nó (`nodo[\"linha\"]`)"],
   ["`codigo`", "o nome da regra; aparece na mensagem e serve para silenciar"],
   ["`mensagem`", "o que está errado"],
   ["`sugestao`", "o que fazer — a parte que faz a diferença"],
   ["`severidade`", "`\"erro\"` (padrão) ou `\"aviso\"`; erro reprova o comando"]]}},
 {"p": "A ação recebe a **árvore** (o mesmo dado de [`M.arvore`](/docs/metaprogramacao/macros)) e o caminho do arquivo, e devolve um cluster de achados. Nada mais."},

 {"h2": "Silenciar uma regra de plugin"},
 {"p": "O mesmo escape das regras embutidas vale aqui — e vale porque, sem ele, a única saída de quem discorda seria desligar o plugin inteiro:"},
 {"code": """x := 1    // df: permitir sem-nome-curto""", "lang": "df"},

 {"h2": "Um plugin quebrado não derruba o check"},
 {"p": "Se o plugin não carrega, ou falha no meio, isso vira **diagnóstico** — com o nome do arquivo e o motivo. Quem roda o `check` quer o relatório do código dele, e não a pilha do analisador."},
 {"code": """// saída quando o plugin falha:
//
//   alvo.df:1:1: erro: o plugin 'ruim.df' falhou: quebrei
//       sugestão: conserte o plugin, ou tire-o da lista
out "veja o bloco acima" """, "lang": "df"},

 {"h2": "O que um plugin alcança"},
 {"table": {"head": ["Dá para fazer", "Como"], "rows": [
   ["lint próprio", "percorrer a árvore e acusar o que a equipe combinou"],
   ["análise de fluxo simples", "seguir a ordem das instruções dentro de uma ação"],
   ["convenção de arquitetura", "olhar `adopt` e acusar dependência proibida entre camadas"],
   ["verificação de esquema", "ler um `.json` do projeto e conferir contra o que o código declara"]]}},
 {"table": {"head": ["Não dá", "Por quê"], "rows": [
   ["transformar a árvore antes de rodar", "o plugin do `check` **analisa**; reescrever é trabalho de macro, que roda na carga do arquivo"],
   ["adicionar palavra à linguagem", "isso é o parser, e mexe no DataForge"],
   ["rodar a cada tecla no editor", "o LSP usa as regras embutidas; o plugin roda no comando"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/metaprogramacao/mapa",
"title": "Metaprogramação: o mapa",
"description": "Item por item da parte 5 da referência Deep Tech — comptime, macros, DSLs e compiler plugins — cruzado com o que o DataForge tem.",
"blocos": [
 {"p": "A quinta parte de uma referência Deep Tech cobre computação em tempo de compilação, macros, DSLs e plugins do compilador. Boa parte dela pressupõe um **compilador** com fases separadas. Aqui a \"compilação\" é `parse` + `check` + carga — e é nessas três que as peças abaixo se encaixam."},

 {"h2": "22 · Computação em tempo de compilação"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["`comptime`", "existe: roda na carga, numa caixa sem E/S, e congela o resultado", "[comptime](/docs/metaprogramacao/comptime)"],
   ["const evaluation", "`comptime steady NOME := …` — constante calculada", "[comptime](/docs/metaprogramacao/comptime)"],
   ["funções executadas no build", "ações declaradas **dentro** do bloco `comptime`", "[comptime](/docs/metaprogramacao/comptime)"],
   ["geração de constantes, lookup tables", "o caso central: a tabela é calculada uma vez", "[comptime](/docs/metaprogramacao/comptime)"],
   ["validações estáticas", "`assert` dentro de `comptime`; o `check` acusa (`comptime-falhou`)", "[comptime](/docs/metaprogramacao/comptime)"],
   ["cálculos matemáticos em compile-time", "sim — é conta pura, que é o que a caixa permite", "[comptime](/docs/metaprogramacao/comptime)"],
   ["especialização de código", "**não existe** em build: o caminho é `overload` (decide na chamada) e a macro (reescreve o corpo)", "[Sobrecarga](/docs/oop/sobrecarga)"],
   ["geração de tipos", "**parcial**: alias genérico (`type Par<T> := …`) e argumento numérico (`Vetor<3>`)", "[Generics](/docs/tipos/genericos)"]]}},

 {"h2": "23 · Macros"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["macros procedurais", "`Arcane.Macro`: a árvore como dado, transformada por código comum", "[Macros](/docs/metaprogramacao/macros)"],
   ["AST manipulation e transformation", "`arvore`, `percorrer`, `transformar`, `substituir`, `reescrever`", "[Macros](/docs/metaprogramacao/macros)"],
   ["expansão de macros", "acontece na **carga**, quando o decorador é aplicado", "[Macros](/docs/metaprogramacao/macros)"],
   ["macros de atributo", "`mark @M.derivar(…)` sobre um blueprint", "[Macros](/docs/metaprogramacao/macros)"],
   ["macros derivadas", "`texto`, `igualdade`, `ordem`, `vault` a partir dos campos", "[Macros](/docs/metaprogramacao/macros)"],
   ["higiene de macros", "**explícita**: `nome_fresco` e `renomear` — automática exigiria saber o que é \"de dentro\"", "[Macros](/docs/metaprogramacao/macros)"],
   ["macros declarativas (padrão → substituição)", "**não existem** como forma própria: o mesmo se escreve com `transformar` e um `given`", "—"],
   ["token streams", "**não se expõem**: a macro trabalha sobre a árvore, que é o nível em que o significado já está resolvido", "—"]]}},

 {"h2": "24 · DSLs"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["DSLs internas", "blueprint com operadores, pipeline `>>`, ação de alta ordem — e as palavras contextuais do Kiln e do Quadro", "[Kiln](/docs/kiln)"],
   ["DSLs externas", "`Arcane.Dsl`: combinadores de análise, com falha que diz a posição", "[DSLs](/docs/metaprogramacao/dsl)"],
   ["parser extensions", "**não existem** como plugin: palavra nova na linguagem é mexer no parser — foi assim com as onze do Kiln e os seis verbos do Quadro", "—"],
   ["AST híbrida", "a árvore de `M.citar` e a do arquivo são **a mesma**, e é isso que deixa gerar código que roda", "[Macros](/docs/metaprogramacao/macros)"],
   ["geração de código, templates", "`M.compilar(texto, …)` e `M.acao(…)`; para texto puro, `$\"{}\"` e `Arcane.Text`", "[Macros](/docs/metaprogramacao/macros)"]]}},

 {"h2": "25 · Compiler plugins"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["plugins do compilador", "plugins do `check`: um `.df` com `verificar(arvore, arquivo)`", "[Plugins](/docs/metaprogramacao/plugins)"],
   ["custom lints", "é exatamente o caso de uso, com código próprio e silenciamento", "[Plugins](/docs/metaprogramacao/plugins)"],
   ["analisadores estáticos", "a árvore inteira é entregue; o que o plugin prova, ele acusa", "[Plugins](/docs/metaprogramacao/plugins)"],
   ["hooks", "um hook só: `verificar`. Mais hooks sem caso de uso viram superfície para manter", "[Plugins](/docs/metaprogramacao/plugins)"],
   ["análise de fluxo", "possível dentro do plugin (a ordem das instruções está na árvore); o que **não** existe é um grafo de fluxo pronto", "—"],
   ["transformações de AST no compilador", "**não existem** por plugin: transformar é trabalho de macro, na carga do arquivo — um plugin do `check` que reescrevesse código faria `check` e `run` discordarem", "—"],
   ["verificação formal", "**não existe**: o refinamento é verificado, não provado", "[Tipos nomeados](/docs/tipos-nomeados)"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das quatro seções, **três** têm resposta direta: `comptime`, macros sobre a árvore e plugins do `check`. A quarta — DSLs — tem duas respostas: a interna, que sempre existiu, e a externa, agora com combinadores."},
 {"p": "O que não existe tem um padrão: tudo o que exige **mexer no parser em tempo de execução** (parser extensions, token streams, macros declarativas com sintaxe nova). Isso é decisão de linguagem, e as vezes em que valeu a pena — as onze palavras do Kiln, os seis verbos do Quadro, as treze de OOP — foram feitas no parser, com o custo explicado em cada uma."},
]},
]
