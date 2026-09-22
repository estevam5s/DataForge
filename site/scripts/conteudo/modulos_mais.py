# -*- coding: utf-8 -*-
"""Módulos — mais nove páginas: renomear, fachada, ciclo, visibilidade,
a biblioteca padrão, o estado de um módulo, o ponto de entrada, a ponte
e como dividir um arquivo grande.

Dois fatos que estas páginas afirmam foram conferidos rodando: um
módulo carrega UMA vez (dois 'adopt' do mesmo arquivo dividem o mesmo
estado), e o '_' no começo de um nome NÃO o esconde — só o 'relay'
esconde.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/renomear",
"title": "Renomear sem quebrar",
"description": "relay novo as antigo — o nome novo e o velho, o mesmo objeto, e o abi dizendo que é compatível.",
"blocos": [
 {"p": "Renomear uma ação pública quebra todo programa que chama o nome antigo — no dia em que ele atualiza. `relay novo as antigo` exporta **o mesmo objeto** com os dois nomes: quem usa o antigo continua funcionando, e o código novo já usa o nome certo."},
 {"code": """// precos.df — a versao 2
action total_com_imposto(valor):
    yield valor * 1.1

// Os dois nomes saem; o antigo e so um apelido.
relay total_com_imposto, total_com_imposto as total""", "lang": "text", "title": "precos.df"},
 {"code": """adopt ./precos as P
assert P.total is P.total_com_imposto        // o MESMO objeto
out P.total(100)""", "lang": "df", "title": "main.df"},
 {"h2": "O `abi` concorda"},
 {"code": """$ dataforge abi v1/precos.df v2/precos.df
  + total_com_imposto  [simbolo-novo]
  veredito: versao MENOR — so acrescimos compativeis

$ # sem o apelido, o mesmo rename:
  - total              [simbolo-removido]
  veredito: versao MAIOR""", "lang": "text"},
 {"table": {"head": ["Forma", "Efeito"], "rows": [
   ["`relay a`", "`a` sai com o próprio nome"],
   ["`relay a as b`", "só `b` sai — `a` fica interno"],
   ["`relay a, a as b`", "os dois saem, e são o mesmo objeto"],
   ["`relay a as b, c as b`", "**recusado**: um nome exportado duas vezes"]]}},
 {"callout": {"tipo": "dica", "titulo": "Quer que o nome velho também avise?", "texto": "`relay` apenas mantém o nome funcionando. Para que ele avise quem o usa, `Arcane.Evolucao.renomeada(nova, \"antigo\", \"2.0\")` — ver [Obsolescência](/docs/bibliotecas/obsolescencia)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/fachada",
"title": "A fachada: um index.df",
"description": "relay from ./x — reunir vários módulos internos numa API só, e esconder o resto.",
"blocos": [
 {"p": "Quando uma biblioteca cresce, ela vira vários arquivos. Quem a usa não deveria precisar saber em qual arquivo mora cada ação. Uma **fachada** reúne o que é público num ponto só."},
 {"code": """lib/
  index.df        a fachada: o unico arquivo que quem usa adota
  precos.df       total, desconto
  frete.df        calcular_frete
  _cache.df       interno — nao aparece na fachada""", "lang": "text"},
 {"code": """// index.df
relay from ./precos      // tudo o que precos.df exporta
relay from ./frete
// _cache.df nao e citado: continua interno""", "lang": "text", "title": "lib/index.df"},
 {"code": """adopt ./lib/index as Loja
out Loja.total(100), Loja.calcular_frete("SC")""", "lang": "text", "title": "main.df"},
 {"table": {"head": ["Decisão", "Porque"], "rows": [
   ["o nome local **vence** o re-exportado", "um `relay from` não sobrescreve o que a fachada definiu"],
   ["o `check` abre a superfície de um `relay from`", "seguir até o outro arquivo é possível, mas por ora ele cala em vez de adivinhar"],
   ["mover uma ação entre arquivos internos não muda nada para fora", "é o ponto: a fachada é o contrato, os arquivos são detalhe"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/ciclos",
"title": "Ciclos de import",
"description": "Por que A → B → A não sobe, como o check mostra a cadeia, e as três formas de quebrá-la.",
"blocos": [
 {"p": "Um ciclo de import é `a.df` adotando `b.df`, que adota `a.df`. Para carregar `a`, é preciso `b`; para carregar `b`, é preciso `a`. O `check` acusa antes de rodar, e mostra a cadeia **mais curta** — a mais fácil de quebrar."},
 {"code": """$ dataforge check src/
src/pedidos.df:1:1: erro: import cycle: pedidos.df → clientes.df → pedidos.df
    sugestao: move what both need into a third module""", "lang": "text"},
 {"h2": "As três saídas"},
 {"table": {"head": ["Saída", "Quando"], "rows": [
   ["**um terceiro módulo** com o que os dois precisam", "quase sempre: o ciclo é um tipo compartilhado morando no lugar errado"],
   ["**passar como argumento** em vez de adotar", "quando só uma ação de `b` precisa de algo de `a`"],
   ["**juntar os dois**", "quando eles são, na verdade, um módulo só"]]}},
 {"code": """// ANTES: pedidos.df adota clientes.df, e clientes.df adota pedidos.df
//         porque os dois usam o record Endereco.
//
// DEPOIS:
//   endereco.df   record Endereco            (nao adota ninguem)
//   clientes.df   adopt ./endereco
//   pedidos.df    adopt ./endereco, adopt ./clientes
//
// O grafo virou uma arvore: endereco <- clientes <- pedidos.

record Endereco:
    rua: String
    cidade: String

e := Endereco("Rua A", "Recife")
assert e.cidade is "Recife\"""", "lang": "df"},
 {"code": """dataforge deps              # o grafo de imports
dataforge check src/        # o ciclo, com a cadeia""", "lang": "bash"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/visibilidade",
"title": "O que é público",
"description": "Sem relay, tudo do topo sai — inclusive o que começa com _. Só o relay esconde.",
"blocos": [
 {"p": "Uma pergunta que quem vem do Python faz: *“o `_` no começo do nome esconde?”*. **Não.** Sem `relay`, tudo o que o módulo define no topo sai pelo `adopt` — `_interno` inclusive. O `_` é convenção para quem lê; quem esconde é o `relay`."},
 {"table": {"head": ["O módulo tem", "Sai pelo `adopt`"], "rows": [
   ["nenhum `relay`", "**tudo** do topo, com ou sem `_`"],
   ["algum `relay`", "**só** o que está listado"],
   ["`relay a as b`", "`b` — e `a` fica interno"]]}},
 {"code": """// contador.df, sem relay:
//     _interno := 42
//     action mais(): ...
//
// main.df:
//     adopt ./contador as C
//     out C._interno        // 42 — o '_' nao escondeu
//
// Com 'relay mais' no fim de contador.df, C._interno vira erro:
//     o modulo './contador' nao tem '_interno'

out "so o relay decide o que e publico\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Sem relay, todo nome do topo é contrato", "texto": "Quem adotou o seu módulo pode estar usando qualquer nome do topo — inclusive o auxiliar que você pretendia renomear amanhã. Uma biblioteca deveria sempre ter `relay`: é ele que separa o que você promete do que é detalhe, e é o que o `dataforge abi` compara."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/biblioteca-padrao",
"title": "Achar na biblioteca padrão",
"description": "Os módulos Arcane, os apelidos, e como descobrir o que existe sem sair do terminal.",
"blocos": [
 {"p": "A biblioteca padrão vem junto com a linguagem, sem instalar nada. Cada módulo tem um nome oficial (`Arcane.Algoritmos`) e apelidos curtos (`Algoritmos`, `Algorithms`) — os três chegam ao **mesmo** módulo."},
 {"code": """adopt Arcane.Algoritmos as A
adopt Algoritmos as B
assert A.crivo(10) is B.crivo(10)
out A.__name__           // Arcane.Algoritmos, venha por onde vier""", "lang": "df"},
 {"code": """dataforge repl
> :modules                # a lista de modulos
> :doc Arcane.Quadro      # os simbolos de um

dataforge custo src/      # o que cada 'adopt' traz junto""", "lang": "bash"},
 {"table": {"head": ["Preciso de…", "Módulo"], "rows": [
   ["tabela de dados", "`Arcane.Quadro`"],
   ["banco de dados", "`Arcane.Database`, `Forge`"],
   ["HTTP (cliente)", "`Arcane.Http`; entre serviços, `Arcane.Malha`"],
   ["site ou API", "`Kiln`"],
   ["algoritmo clássico", "`Arcane.Algoritmos`"],
   ["dinheiro exato", "`Arcane.Decimal`"],
   ["segurança, LGPD, integridade", "`Arcane.Seguranca`, `Arcane.Privacidade`, `Arcane.Integridade`"],
   ["GitHub", "`Arcane.GitHub`"]]}},
 {"p": "Todos os módulos, com as assinaturas: [Biblioteca Arcane](/docs/biblioteca)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/estado",
"title": "O estado de um módulo",
"description": "Um módulo carrega uma vez, e o que ele guarda é compartilhado por todos que o adotam.",
"blocos": [
 {"p": "Um módulo é executado **uma vez**, no primeiro `adopt`. Os `adopt` seguintes do mesmo arquivo recebem o mesmo objeto — e com ele o mesmo estado. Um contador num módulo é um contador **do programa**, e não de quem o adotou."},
 {"code": """// contador.df
//     out "carregando"
//     contagem := {"n": 0}
//     action mais():
//         contagem["n"] += 1
//         yield contagem["n"]
//
// main.df
//     adopt ./contador as A
//     adopt ./contador as B
//     A.mais()
//     out B.mais()          // 2 — e "carregando" saiu UMA vez

out "o modulo carrega uma vez, e o estado e um so\"""", "lang": "df"},
 {"table": {"head": ["Isso é bom para", "Isso é perigoso para"], "rows": [
   ["uma conexão aberta uma vez", "um valor que cada teste espera ver zerado"],
   ["um cache", "duas threads escrevendo no mesmo vault (ver `escrita-concorrente`)"],
   ["uma configuração lida no começo", "esconder dependência: a ação lê algo que ninguém passou"]]}},
 {"callout": {"tipo": "dica", "titulo": "Prefira passar a guardar", "texto": "Uma ação que recebe o que precisa como argumento se testa sozinha. Uma que lê um vault do módulo depende da ordem em que os testes rodaram — é a origem do teste que passa sozinho e falha na suíte."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/entrada",
"title": "O ponto de entrada",
"description": "app.df monta, main.df sobe — e por que importar um módulo não pode ter efeito.",
"blocos": [
 {"p": "Todo código no topo de um módulo roda no `adopt`. Por isso um módulo que **sobe um servidor** no topo trava qualquer teste que o importe: o teste nunca termina. A regra é separar quem **monta** de quem **roda**."},
 {"code": """projeto/
  forge.toml       entry = "src/main.df"
  src/
    app.df         monta: rotas, regras — sem efeito no topo
    main.df        roda: le o ambiente, 'ignite', 'OS.exit'
  tests/
    app_test.df    adopt ../src/app — e nada sobe""", "lang": "text"},
 {"code": """// app.df — so declara
adopt Kiln
server api on 0:
    route GET "/":
        respond json {"ok": yes}

// main.df — o unico com efeito
//     adopt ./app as App
//     ignite App.api at "0.0.0.0"

r := Kiln.test(api, "GET", "/")
assert r["status"] is 200""", "lang": "df"},
 {"table": {"head": ["No topo de um módulo", "Pode?"], "rows": [
   ["declarar ações, records, constantes", "sim"],
   ["abrir uma conexão **preguiçosa**", "sim — uma ação que abre no primeiro uso"],
   ["subir servidor, ler `input`, `OS.exit`", "**não** — só no ponto de entrada"],
   ["imprimir", "evite: aparece em todo teste que importar"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/python",
"title": "Adotar do Python",
"description": "adopt Python.x — o que atravessa, o que não converte, e o custo para quem instala.",
"blocos": [
 {"p": "`adopt Python.statistics as st` traz qualquer módulo do Python. A ponte **não converte**: o objeto do Python chega como está, e a linguagem conversa com ele por protocolo — membro, método, índice, `len`, iteração, conta."},
 {"code": """adopt Python.statistics as st
adopt Python.fractions as fr

assert st.median([3, 1, 2]) is 2
um_terco := fr.Fraction(1, 3)
assert um_terco + um_terco + um_terco is 1     // exato: nenhum float no caminho
out typeof(um_terco)     // 'Float' — o typeof responde pela familia numerica\"""", "lang": "df"},
 {"table": {"head": ["Vale", "Não vale"], "rows": [
   ["o módulo é da biblioteca padrão do Python (sem instalar)", "existe o mesmo em `Arcane.*`"],
   ["uma biblioteca madura para um formato binário complexo", "*“pode ser mais rápido”* sem medir"],
   ["cálculo numérico pesado (numpy)", "num pacote publicado, sem declarar a dependência"]]}},
 {"callout": {"tipo": "atencao", "titulo": "`Python` é espaço reservado", "texto": "`adopt Python.x` é resolvido **antes** da biblioteca e dos arquivos vizinhos: um `Python.df` no disco não sequestra o import. E um módulo que não está instalado recebe uma mensagem com o Python exato onde instalar — a venv do DataForge não é a do terminal."}},
 {"p": "Continue em [A ponte](/docs/tecnicas/ponte)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/dividir",
"title": "Dividir um arquivo grande",
"description": "Quando partir, por onde partir, e como fazer isso sem quebrar quem já adota o arquivo.",
"blocos": [
 {"p": "Um arquivo com mil linhas ainda funciona; o problema é que ninguém mais acha nada nele, e toda mudança conflita com outra. Partir é mecânico **se** for feito na ordem certa."},
 {"h2": "Quando"},
 {"table": {"head": ["Sinal", "Medido por"], "rows": [
   ["o arquivo passou de 400 linhas", "`dataforge stats`"],
   ["dois assuntos que não se chamam", "`dataforge deps`"],
   ["um blueprint com baixa coesão", "`dataforge oop` (LCOM alto)"]]}},
 {"h2": "Como, sem quebrar ninguém"},
 {"list": [
   "Crie os arquivos novos e **mova** o código para eles.",
   "No arquivo original, troque o conteúdo por uma fachada: `relay from ./parte1`, `relay from ./parte2`.",
   "Rode `dataforge abi antigo.df novo.df`: o veredito precisa ser `correcao` — a superfície não mudou.",
   "Só depois, se quiser, migre quem adota o arquivo original para os novos.",
 ], "ordered": True},
 {"code": """dataforge stats src/loja.df
dataforge abi git-show-antigo/loja.df src/loja.df   # precisa dar 'correcao'
dataforge check src/                                 # nenhum ciclo novo""", "lang": "bash"},
 {"code": """// O que o 'abi' confere, em miniatura: a mesma superficie antes e depois.
action total(v):
    yield v * 1.1
action frete(uf):
    yield 20 given uf is "SP" otherwise 35
assert total(100) bigger 109 and frete("SP") is 20""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Parta por assunto, não por tipo", "texto": "`pedidos/`, `clientes/`, `estoque/` — e não `modelos/`, `servicos/`, `rotas/`. Uma mudança de regra deveria tocar uma pasta. Ver [Organizar um projeto grande](/docs/modulos/organizar)."}},
]},
]
