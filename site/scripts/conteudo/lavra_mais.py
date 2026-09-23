# -*- coding: utf-8 -*-
"""Lavra — oito páginas novas: mutação, paginação, erro parcial, cache,
escalar próprio, introspecção, teste e a migração a partir do REST.

Todo bloco roda: o esquema é montado, a consulta é executada e o
resultado é conferido com `assert`.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/mutacoes",
"title": "Mudanças",
"description": "Escrever pelo Lavra — e as quatro regras que separam uma mudança de um GET com efeito colateral.",
"blocos": [
 {"p": "Uma **busca** pode ser repetida, cacheada e feita em paralelo. Uma **mudança** não: ela é a única parte do Lavra que altera o mundo, e por isso as regras são outras — inclusive a ordem de execução."},
 {"code": '''adopt Arcane.Lavra as Lavra

record Tarefa:
    id: Integer
    titulo: String
    feita: Boolean

BANCO := {"proximo": 1, "itens": []}

action criar(raiz, args, ctx):
    id := BANCO["proximo"]
    BANCO["proximo"] := id + 1
    t := Tarefa(id, args["titulo"], no)
    BANCO["itens"].append(t)
    yield t

esq := Lavra.esquema("tarefas")
Lavra.tipo(esq, Tarefa)
// Todo esquema precisa de ao menos uma BUSCA — 'conferir' recusa um
// esquema só de mudanças, porque um cliente não teria como ler nada.
Lavra.busca(esq, "tarefas", "[Tarefa!]!",
    resolve := lambda r, a, c => BANCO["itens"])
Lavra.mudanca(esq, "criarTarefa", "Tarefa!",
    args := {"titulo": "String!"}, resolve := criar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
mudanca:
    criarTarefa(titulo: "comprar café"):
        id
        titulo
        feita
""")
assert r["dados"]["criarTarefa"]["id"] is 1
assert r["dados"]["criarTarefa"]["feita"] is no
out r["dados"]''', "lang": "df"},
 {"h2": "As quatro regras"},
 {"table": {
   "head": ["Regra", "Sem ela"],
   "rows": [
     ["as mudanças de uma requisição rodam **em série**", "duas escritas na mesma linha competem, e o resultado depende do escalonador"],
     ["a mudança **devolve o que mudou**", "o cliente precisa de uma segunda ida à rede para ver o resultado"],
     ["o argumento de entrada é um **tipo de entrada**", "quinze argumentos soltos, e nenhum lugar para validar o conjunto"],
     ["a falha de uma mudança é **erro**, não `void` no campo", "o cliente grava um estado que não aconteceu"]]}},
 {"h2": "O tipo de entrada"},
 {"p": "Um formulário de dez campos como dez argumentos é ilegível, e não tem onde declarar o que é obrigatório junto. `Lavra.entrada` dá nome ao conjunto:"},
 {"code": '''adopt Arcane.Lavra as Lavra

record Cliente:
    id: Integer
    nome: String
    email: String

record NovoCliente:
    nome: String
    email: String

esq := Lavra.esquema("crm")
Lavra.tipo(esq, Cliente)
// Entrada e saída são tipos DIFERENTES de propósito: o 'Cliente' que
// sai tem 'id'; o que entra, não. Usar o mesmo tipo nos dois lados
// obrigaria a marcar metade dos campos como opcionais — e aí nenhum
// deles seria conferido.
Lavra.entrada(esq, NovoCliente)
Lavra.campo(esq, "NovoCliente", "nome", "String!")
Lavra.campo(esq, "NovoCliente", "email", "String!")

action criar(raiz, args, ctx):
    dados := args["dados"]
    given "@" not in dados["email"]:
        trigger Lavra.erro("e-mail inválido", "validacao", {"campo": "email"})
    yield Cliente(1, dados["nome"], dados["email"])

Lavra.busca(esq, "clientes", "[Cliente!]!", resolve := lambda r, a, c => [])
Lavra.mudanca(esq, "criarCliente", "Cliente!",
    args := {"dados": "NovoCliente!"}, resolve := criar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
mudanca:
    criarCliente(dados: {nome: "Ana", email: "ana@ex.com"}):
        id
        nome
""")
assert r["dados"]["criarCliente"]["nome"] is "Ana"

// e o e-mail errado vira ERRO, com código e campo
ruim := Lavra.executar(esq, """
mudanca:
    criarCliente(dados: {nome: "Ana", email: "sem-arroba"}):
        id
""")
assert len(ruim["erros"]) is 1
out ruim["erros"][0]''', "lang": "df"},
 {"h2": "O erro tem código, e o código é o contrato"},
 {"p": "`\"e-mail inválido\"` é para a pessoa; `\"validacao\"` é para o programa. Um cliente que decide pelo **texto** da mensagem quebra na primeira tradução — e essa é a razão de o erro carregar um código e um vault de extras."},
 {"code": '''adopt Arcane.Lavra as Lavra

// Os três desfechos que um resolvedor tem, e o que cada um significa:
action nao_achei(r, a, c):
    yield void                                     // ausência

action negado(r, a, c):
    trigger Lavra.recusar("sem permissão")         // autorização

action quebrado(r, a, c):
    trigger Lavra.erro("o banco caiu", "indisponivel")   // falha

esq := Lavra.esquema("x")
Lavra.busca(esq, "vazio", "String", resolve := nao_achei)
Lavra.busca(esq, "negado", "String", resolve := negado)
Lavra.busca(esq, "quebrado", "String", resolve := quebrado)
Lavra.conferir(esq)

assert Lavra.executar(esq, "busca:\\n    vazio")["dados"]["vazio"] is void
assert len(Lavra.executar(esq, "busca:\\n    negado")["erros"]) is 1
assert len(Lavra.executar(esq, "busca:\\n    quebrado")["erros"]) is 1
out "void é ausência; erro é falha — e o cliente trata os dois de formas diferentes"''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Idempotência não vem de graça", "texto": "Repetir `criarTarefa` cria duas tarefas — como um POST. Se o cliente pode repetir (e ele pode: rede cai no meio), a mudança precisa de uma **chave de idempotência** vinda do cliente, e o servidor é quem a honra. É a mesma regra da `Arcane.Malha`: quem fabrica idempotência é o outro lado."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/paginacao",
"title": "Paginação por cursor",
"description": "Por que `pagina=3` mente, e o que o cursor promete no lugar.",
"blocos": [
 {"p": "Paginar por número (`?pagina=3&por=20`) é a forma mais comum, e ela **pula e repete linhas** em qualquer lista que muda: alguém insere na página 1, e o item que era o 20 vira o 21 — quem pede a página 2 nunca o vê."},
 {"table": {
   "head": ["", "Por número", "Por cursor"],
   "rows": [
     ["\"me dê a página 3\"", "`OFFSET 40` — o banco varre 40 linhas e joga fora", "`WHERE id > 'abc'` — usa o índice"],
     ["alguém insere no meio", "linha pulada ou repetida", "estável: o cursor aponta para uma linha"],
     ["\"ir para a página 50\"", "funciona", "**não existe**, e é o preço"],
     ["custo em 1 milhão de linhas", "cresce com o deslocamento", "constante"]]}},
 {"code": '''adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String

TODOS := [Produto(i, $"produto {i}") cycle i in range(1, 31)]

action listar(raiz, args, ctx):
    // 'pagina' fatia sozinha: ela recebe a coleção INTEIRA, quantos
    // itens e o cursor — e devolve o recorte com as bordas e a info.
    // E o '??' não é opcional: uma chave que não veio não está no
    // vault, e indexá-la levanta.
    yield Lavra.pagina(TODOS, args["primeiros"] ?? 10,
                       args["depois"] ?? void, len(TODOS))

esq := Lavra.esquema("catalogo")
Lavra.tipo(esq, Produto)
Lavra.tipo_pagina(esq, "Produto")
Lavra.busca(esq, "produtos", "PaginaProduto!",
    args := {"primeiros": {"tipo": "Integer", "padrao": 10},
             "depois": "String"},
    resolve := listar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
busca:
    produtos(primeiros: 3):
        total
        info:
            tem_proxima
            cursor_fim
        itens:
            id
            nome
""")
pagina := r["dados"]["produtos"]
assert len(pagina["itens"]) is 3
assert pagina["total"] is 30
assert pagina["info"]["tem_proxima"] is yes
out pagina''', "lang": "df"},
 {"h2": "A segunda página"},
 {"code": '''adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer

TODOS := [Produto(i) cycle i in range(1, 11)]

action listar(raiz, args, ctx):
    yield Lavra.pagina(TODOS, args["primeiros"] ?? 3,
                       args["depois"] ?? void, len(TODOS))

esq := Lavra.esquema("c")
Lavra.tipo(esq, Produto)
Lavra.tipo_pagina(esq, "Produto")
Lavra.busca(esq, "produtos", "PaginaProduto!",
    args := {"primeiros": "Integer", "depois": "String"}, resolve := listar)
Lavra.conferir(esq)

primeira := Lavra.executar(esq,
    "busca:\\n    produtos(primeiros: 3):\\n        info:\\n            cursor_fim\\n        itens:\\n            id")
cursor := primeira["dados"]["produtos"]["info"]["cursor_fim"]

segunda := Lavra.executar(esq,
    $"busca:\\n    produtos(primeiros: 3, depois: \\"{cursor}\\"):\\n        itens:\\n            id")
assert segunda["dados"]["produtos"]["itens"][0]["id"] is 4
out $"a segunda página começa no {segunda['dados']['produtos']['itens'][0]['id']}"''', "lang": "df"},
 {"h2": "O cursor é opaco, de propósito"},
 {"p": "Um cursor que é visivelmente o `id` convida o cliente a construí-lo, e aí a implementação **não pode mais mudar**: trocar de offset para keyset quebraria todo mundo. Codificá-lo (base64, ou assinado) é o que mantém a liberdade — e é o mesmo motivo de `Kiln.cursor` existir do lado REST."},
 {"callout": {"tipo": "nota", "titulo": "O teto vem ligado", "texto": "`primeiros` precisa de um padrão **e** de um máximo. Sem o máximo, `primeiros: 1000000` é um jeito educado de derrubar o servidor — e é a primeira coisa que um scanner tenta. `Lavra.limites(esq, itens := 100)` cobra isso no esquema inteiro."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/lote",
"title": "N+1 e o lote",
"description": "Cem produtos, cem consultas ao banco — e como isso vira duas.",
"blocos": [
 {"p": "O N+1 é o defeito que toda camada de consulta tipada produz por construção: uma busca traz 100 produtos, o campo `categoria` de cada um chama o resolvedor, e são **101** idas ao banco. O código parece certo, e a página leva três segundos."},
 {"code": '''adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String
    categoria_id: Integer

record Categoria:
    id: Integer
    nome: String

CATEGORIAS := {1: Categoria(1, "bebidas"), 2: Categoria(2, "acessórios")}
PRODUTOS := [Produto(1, "café", 1), Produto(2, "chá", 1), Produto(3, "filtro", 2)]
IDAS := {"n": 0}

action buscar_categorias(chaves):
    // UMA ida, com todas as chaves de uma vez.
    IDAS["n"] := IDAS["n"] + 1
    yield {k: CATEGORIAS[k] cycle k in chaves}

action todos(raiz, args, ctx):
    yield PRODUTOS

action categoria_de(produto, args, ctx):
    // 'pedir' NÃO vai ao banco: ele registra a chave e devolve uma
    // promessa. O Lavra junta as chaves do nível inteiro e chama
    // 'buscar_categorias' UMA vez.
    Lavra.lote(ctx, "categorias", buscar_categorias)
    yield Lavra.pedir(ctx, "categorias", produto.categoria_id)

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.tipo(esq, Categoria)
Lavra.campo(esq, "Produto", "categoria", "Categoria", resolve := categoria_de)
Lavra.busca(esq, "produtos", "[Produto!]!", resolve := todos)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
busca:
    produtos:
        nome
        categoria:
            nome
""")
assert len(r["dados"]["produtos"]) is 3
assert r["dados"]["produtos"][0]["categoria"]["nome"] is "bebidas"

// três produtos, duas categorias distintas — e UMA ida
assert IDAS["n"] is 1
out $"3 produtos, {IDAS['n']} consulta de categoria"''', "lang": "df"},
 {"h2": "Por que isto não é cache"},
 {"table": {
   "head": ["", "Lote", "Cache"],
   "rows": [
     ["vive", "uma requisição", "entre requisições"],
     ["resolve", "N chamadas viram uma", "a segunda chamada não acontece"],
     ["pode devolver dado velho", "**não**", "sim, e é o ponto dele"],
     ["precisa de invalidação", "não", "sim — e é a parte difícil"]]}},
 {"p": "Os dois se somam: o lote tira o N+1 de **dentro** da requisição; o cache tira a requisição inteira. Um cache sem lote continua com N+1 na primeira visita, que é a que o usuário novo vê."},
 {"h2": "O campo que custa caro declara o custo"},
 {"code": '''adopt Arcane.Lavra as Lavra

record Usuario:
    id: Integer

esq := Lavra.esquema("rede")
Lavra.tipo(esq, Usuario)
// 'custo' diz quanto este campo pesa; o limite de complexidade soma
// o custo da consulta ANTES de executar qualquer resolvedor.
Lavra.campo(esq, "Usuario", "amigos", "[Usuario!]!",
    resolve := lambda r, a, c => [], custo := 10)
Lavra.busca(esq, "usuario", "Usuario", resolve := lambda r, a, c => Usuario(1))
Lavra.limites(esq, profundidade := 5, complexidade := 50)
Lavra.conferir(esq)

// Uma consulta funda demais é recusada sem tocar no banco.
r := Lavra.executar(esq, """
busca:
    usuario:
        amigos:
            amigos:
                amigos:
                    amigos:
                        id
""")
assert len(r["erros"]) is 1
out r["erros"][0]["mensagem"]''', "lang": "df"},
 {"p": "Recusar **antes** de executar é o ponto: um limite conferido no meio já pagou metade do custo, e é exatamente essa metade que derruba o banco."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/escalares",
"title": "Escalares próprios",
"description": "Data, dinheiro e CPF como tipo — validados na fronteira, uma vez.",
"blocos": [
 {"p": "Um campo `String` que na verdade é uma data acaba validado em quinze lugares — e em catorze deles com uma regra ligeiramente diferente. Um **escalar próprio** move a validação para a fronteira, onde ela acontece uma vez."},
 {"code": '''adopt Arcane.Lavra as Lavra
adopt Arcane.Time as T

action data_para_texto(valor):
    yield str(valor)

action data_de_texto(texto):
    partes := texto.split("-")
    given len(partes) is not 3:
        trigger "uma Data é 'AAAA-MM-DD'"
    yield texto

esq := Lavra.esquema("agenda")
Lavra.escalar(esq, "Data", data_para_texto, data_de_texto,
              "uma data no formato AAAA-MM-DD")

record Evento:
    id: Integer
    quando: String

Lavra.tipo(esq, Evento)
Lavra.campo(esq, "Evento", "quando", "Data!")
Lavra.busca(esq, "evento", "Evento",
    resolve := lambda r, a, c => Evento(1, "2026-09-22"))
Lavra.conferir(esq)

r := Lavra.executar(esq, "busca:\\n    evento:\\n        quando")
assert r["dados"]["evento"]["quando"] is "2026-09-22"
out r["dados"]''', "lang": "df"},
 {"h2": "A validação acontece na entrada, e a recusa é clara"},
 {"code": '''adopt Arcane.Lavra as Lavra

action de_texto(texto):
    given len(texto.split("-")) is not 3:
        // 'Lavra.erro' vira um erro da RESPOSTA, com código; um
        // 'trigger' de texto vira falha do servidor, e o cliente
        // recebe 500 onde devia receber "o argumento está errado".
        trigger Lavra.erro("uma Data é 'AAAA-MM-DD'", "argumento")
    yield texto

esq := Lavra.esquema("a")
Lavra.escalar(esq, "Data", lambda v => str(v), de_texto)
Lavra.busca(esq, "quando", "String",
    args := {"dia": "Data!"}, resolve := lambda r, a, c => a["dia"])
Lavra.conferir(esq)

bom := Lavra.executar(esq, 'busca:\\n    quando(dia: "2026-01-01")')
assert bom["dados"]["quando"] is "2026-01-01"

ruim := Lavra.executar(esq, 'busca:\\n    quando(dia: "ontem")')
assert len(ruim["erros"]) is 1
out ruim["erros"][0]["mensagem"]''', "lang": "df"},
 {"h2": "Os quatro que quase todo esquema quer"},
 {"table": {
   "head": ["Escalar", "Por que não `String`"],
   "rows": [
     ["`Data`, `DataHora`", "fuso, formato e ordenação — e um `String` não ordena como data"],
     ["`Dinheiro`", "`Float` **não serve**: 0,1 + 0,2 não é 0,3. Use `Decimal`, e transporte como texto"],
     ["`Email`, `Cpf`", "a validação passa a existir num lugar só, e o tipo documenta"],
     ["`URL`", "recusar `javascript:` na fronteira é mais barato que em cada tela"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Dinheiro em `Float` é o defeito que ninguém vê", "texto": "Ele funciona em todos os testes com valores pequenos, e aparece no fechamento do mês com um centavo de diferença. A linguagem tem `19.99d` e `Arcane.Decimal`, e recusa misturar `Decimal` com `Float` de propósito — justamente para a falha aparecer na fronteira, e não no relatório."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/testar",
"title": "Testar um esquema",
"description": "Sem HTTP, sem servidor — e o teste que pega a quebra de contrato antes do cliente.",
"blocos": [
 {"p": "Um esquema se testa **sem rede**: `Lavra.executar` recebe o texto da consulta e devolve o resultado. O servidor é outra camada, e ela tem os próprios testes."},
 {"code": '''adopt Arcane.Lavra as Lavra
adopt Arcane.Crucible as Crucible

record Produto:
    id: Integer
    nome: String
    preco: Float

action montar():
    esq := Lavra.esquema("loja")
    Lavra.tipo(esq, Produto)
    Lavra.busca(esq, "produto", "Produto",
        args := {"id": "Integer!"},
        resolve := lambda r, a, c => (
            Produto(1, "café", 32.9) given a["id"] is 1 otherwise void))
    Lavra.conferir(esq)
    yield esq

crucible "o esquema da loja":

    trial "devolve o produto que existe":
        r := Lavra.executar(montar(), "busca:\\n    produto(id: 1):\\n        nome")
        expect r["dados"]["produto"]["nome"] is "café"

    trial "o que nao existe e VOID, e nao erro":
        r := Lavra.executar(montar(), "busca:\\n    produto(id: 99):\\n        nome")
        expect r["dados"]["produto"] is void
        expect len(r["erros"]) is 0

    trial "um campo que nao existe e recusado ANTES de executar":
        r := Lavra.executar(montar(), "busca:\\n    produto(id: 1):\\n        naoExiste")
        expect len(r["erros"]) is 1

    trial "o argumento obrigatorio que falta e recusado":
        r := Lavra.executar(montar(), "busca:\\n    produto:\\n        nome")
        expect len(r["erros"]) is 1

Crucible.run()''', "lang": "df"},
 {"h2": "Validar sem executar"},
 {"p": "`Lavra.validar` responde \"esta consulta é legal neste esquema?\" sem chamar resolvedor nenhum. É o que permite guardar as consultas do aplicativo no repositório e conferir **todas** num teste — a quebra aparece no CI, e não no aplicativo de quem já atualizou."},
 {"code": '''adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.busca(esq, "produto", "Produto",
    args := {"id": "Integer!"}, resolve := lambda r, a, c => void)
Lavra.conferir(esq)

// as consultas que o aplicativo usa, guardadas no repositório
CONSULTAS := {
    "tela_produto": "busca:\\n    produto(id: 1):\\n        nome",
    "tela_antiga": "busca:\\n    produto(id: 1):\\n        descricao",
}

quebradas := []
cycle nome in sorted(keys(CONSULTAS)):
    erros := Lavra.validar(esq, CONSULTAS[nome])
    given len(erros) > 0:
        quebradas.append(nome)

assert quebradas is ["tela_antiga"]
out $"quebrada(s) pelo esquema atual: {quebradas}"''', "lang": "df"},
 {"h2": "O esquema como texto, num instantâneo"},
 {"p": "`texto_do_esquema` devolve a superfície inteira. Guardá-la num instantâneo faz **qualquer** mudança de contrato aparecer no diff do commit — inclusive a que ninguém pretendia:"},
 {"code": '''adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.busca(esq, "produtos", "[Produto!]!", resolve := lambda r, a, c => [])
Lavra.conferir(esq)

texto := Lavra.texto_do_esquema(esq)
assert "busca:" in texto and "tipo Produto:" in texto
out texto''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "`conferir` antes de subir", "texto": "Ele acha o campo que aponta para um tipo que não existe, o resolvedor faltando e o ciclo — **antes** da primeira requisição. Sem ele, o erro aparece na consulta de alguém, e o rastro fala do campo, não da declaração."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/do-rest",
"title": "Do REST para o Lavra",
"description": "O que muda, o que não muda, e o caminho de migração que não exige parar.",
"blocos": [
 {"p": "A migração que funciona **não** é reescrever a API: é pôr o Lavra ao lado do REST, sobre os mesmos casos de uso, e mover tela por tela. As duas convivem no mesmo servidor."},
 {"table": {
   "head": ["No REST", "No Lavra", "O que muda de verdade"],
   "rows": [
     ["`GET /produtos`", "`busca: produtos`", "o cliente escolhe os campos"],
     ["`GET /produtos/1`", "`busca: produto(id: 1)`", "nada, exceto a forma"],
     ["`POST /produtos`", "`mudanca: criarProduto`", "o retorno traz o objeto criado"],
     ["`GET /produtos/1/categoria`", "campo `categoria` dentro de `produto`", "some a segunda ida à rede"],
     ["`?campos=nome,preco`", "a própria consulta", "deixa de ser convenção e passa a ser tipo"],
     ["404", "`void` no campo", "**ausência não é erro**, e o cliente trata diferente"],
     ["`Cache-Control`", "não há", "o cache volta a ser problema do cliente e do resolvedor"]]}},
 {"h2": "Os dois no mesmo servidor"},
 {"code": '''adopt Arcane.Lavra as Lavra
adopt Arcane.Kiln as Kiln

record Produto:
    id: Integer
    nome: String

PRODUTOS := [Produto(1, "café"), Produto(2, "filtro")]

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.busca(esq, "produtos", "[Produto!]!",
    resolve := lambda r, a, c => PRODUTOS)
Lavra.conferir(esq)

// O REST continua, e o Lavra entra ao lado dele.
action listar_rest(req):
    yield Kiln.json([{"id": p.id, "nome": p.nome} cycle p in PRODUTOS])

app := Kiln.app()
Kiln.get(app, "/api/produtos", listar_rest)
Lavra.montar(app, esq, "/lavra")

// e os dois respondem
rest := Kiln.test(app, "GET", "/api/produtos")
assert rest["status"] is 200
grafo := Lavra.executar(esq, "busca:\\n    produtos:\\n        nome")
assert len(grafo["dados"]["produtos"]) is 2
out "REST em /api/produtos e Lavra em /lavra, no mesmo app"''', "lang": "df"},
 {"h2": "O que o Lavra NÃO resolve"},
 {"list": [
   "**Cache de HTTP.** Uma consulta é um POST com corpo; nenhum CDN a cacheia sozinho. Quem quer cache de borda continua no REST, ou usa consulta guardada com GET.",
   "**Upload de arquivo.** Há convenções (multipart com um mapa de variáveis), e todas são mais complicadas que um `POST /upload`.",
   "**Autorização.** Ela continua sendo sua — e agora por **campo**, não por rota, o que é mais trabalho e mais preciso.",
   "**O N+1.** Ele piora: o cliente é quem decide a profundidade. Sem lote, a primeira tela de alguém derruba o banco.",
   "**Versionamento.** \"Não precisa versionar\" só vale enquanto ninguém remove campo — e `Lavra` marca `obsoleto` justamente porque remover é inevitável."]},
 {"h2": "O campo que vai sumir avisa antes"},
 {"code": '''adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String
    titulo: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.campo(esq, "Produto", "titulo", "String",
    resolve := lambda p, a, c => p.nome,
    obsoleto := "use 'nome'; 'titulo' sai na 3.0")
Lavra.busca(esq, "produto", "Produto",
    resolve := lambda r, a, c => Produto(1, "café", "café"))
Lavra.conferir(esq)

// Ele continua RESPONDENDO — quebrar no dia do aviso não é aviso.
r := Lavra.executar(esq, "busca:\\n    produto:\\n        titulo")
assert r["dados"]["produto"]["titulo"] is "café"
assert len(r["erros"]) is 0

// …e o aviso viaja em 'extensoes.avisos', que é onde um cliente
// procura o que vai quebrar depois.
avisos := r["extensoes"]["avisos"]
assert len(avisos) is 1
out avisos[0]["mensagem"]

// E o esquema diz que ele está de saída.
assert "obsoleto" in Lavra.texto_do_esquema(esq)''', "lang": "df"},
 {"p": "Um campo obsoleto que **para de funcionar** no dia do aviso não é um aviso, é uma quebra com aviso prévio de zero. O valor do marcador está em ele continuar respondendo enquanto a ferramenta do cliente já reclama."},
]},
]
