// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "22 · Web com Kiln",
  description: "8 exercícios: rotas, respostas, templates e estáticos.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 22`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[192](#192-o-primeiro-servidor)", "**O primeiro servidor**", "declare um servidor com duas rotas e responda texto e HTML."], ["[193](#193-parametros-de-caminho-e-query-string)", "**Parametros de caminho e query string**", "leia :id do caminho e ?campo= da query."], ["[194](#194-uma-api-restful-completa)", "**Uma API RESTful completa**", "os cinco verbos sobre um mesmo recurso, com os status certos."], ["[195](#195-paginas-html-com-template)", "**Paginas HTML com template**", "renderize uma pagina a partir de um template com laco."], ["[196](#196-middleware-autenticacao-e-limite-de-taxa)", "**Middleware, autenticacao e limite de taxa**", "proteja rotas e limite pedidos por IP."], ["[197](#197-paginas-de-erro-redirecionamento-e-arquivos-estaticos)", "**Paginas de erro, redirecionamento e arquivos estaticos**", "personalize o 404, redirecione uma rota antiga e sirva CSS."], ["[198](#198-subir-o-servidor-de-verdade)", "**Subir o servidor de verdade**", "acenda o forno, faca um pedido pela rede e apague."], ["[199](#199-a-api-vista-de-fora-openapi-insomnia-e-curl)", "**A API vista de fora: OpenAPI, Insomnia e curl**", "exporte as rotas de um servidor Kiln para as ferramentas"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "192 · O primeiro servidor"},
  {"p": "**Enunciado.** declare um servidor com duas rotas e responda texto e HTML."},
  { code: `// 'server' declara a aplicacao; 'route' declara uma rota; 'respond'
// envia a resposta e encerra a rota, como 'yield' encerra uma acao.
// Nada sobe ainda: quem acende o forno e 'ignite'. Essa separacao e o
// que permite testar uma rota sem abrir socket nenhum.

adopt Kiln

server ola on 8080:
    route GET "/":
        respond html "<h1>Ola do Kiln</h1>"

    route GET "/ping":
        respond text "pong"

// Kiln.test executa o pedido direto na aplicacao, sem rede.
inicio := Kiln.test(ola, "GET", "/")
out "GET / ->", inicio["status"]
out inicio["body"]

pong := Kiln.test(ola, "GET", "/ping")
out "GET /ping ->", pong["body"]

assert inicio["status"] is 200, "a raiz responde 200"
assert pong["body"] is "pong", "o texto chega inteiro"
assert len(Kiln.routes(ola)) is 2, "duas rotas registradas"

// Um caminho que nao existe da 404 — sem precisar escrever isso.
assert Kiln.test(ola, "GET", "/nada")["status"] is 404, "404 automatico"`, lang: 'df', title: `exercicios/22-web-kiln/192_primeiro_servidor.df` },
  {"h3": "Conceitos"},
  {"p": "O **Kiln** é o framework web do DataForge. O nome vem do forno onde a peça ganha a forma final: a requisição entra crua e sai como resposta."},
  {"p": "Três palavras novas, todas contextuais — fora de um bloco `server` elas continuam sendo nomes livres:"},
  { code: `server ola on 8080:
    route GET "/":
        respond html "<h1>Ola do Kiln</h1>"`, lang: 'df' },
  {"table": {"head": ["Palavra", "Faz"], "rows": [["`server nome on porta:`", "declara a aplicação e liga ao nome"], ["`route VERBO \"caminho\":`", "registra uma rota"], ["`respond [status] [tipo] valor`", "envia a resposta e **encerra a rota**"], ["`ignite nome`", "acende o forno: sobe o servidor e bloqueia"]]}},
  {"table": {"head": ["Framework", "Equivalente"], "rows": [["Flask", "`@app.route(\"/\")` + `return`"], ["Express", "`app.get(\"/\", (req, res) => res.send(...))`"], ["FastAPI", "`@app.get(\"/\")`"], ["Fastify", "`fastify.get(\"/\", handler)`"]]}},
  {"h3": "O que observar"},
  {"p": "**`server` não sobe nada.** Ele monta a aplicação e liga ao nome. Quem acende o forno é `ignite` — ou `Kiln.serve`, que sobe em segundo plano. Essa separação é o que permite testar uma rota sem abrir socket nenhum:"},
  { code: `Kiln.test(ola, "GET", "/")   // executa a rota, sem rede`, lang: 'df' },
  {"p": "Testar uma rota fica tão barato quanto testar uma função — que é o que faz alguém realmente escrever esses testes."},
  {"p": "**`respond` encerra a rota**, exatamente como `yield` encerra uma ação. O que vier depois não roda."},
  {"p": "**O 404 é de graça.** Um caminho não registrado responde 404 sem você escrever nada. E se o caminho existe mas o verbo não, a resposta é **405** com o cabeçalho `Allow` — distinguir os dois poupa depuração."},
  {"h3": "Erros comuns"},
  {"list": ["Escrever `route` fora de um bloco `server`. Fora dali, `route` é só um nome"]},
  {"p": "de variável — o parser não vai reconhecer a rota."},
  {"list": ["Esquecer o `ignite`. O programa monta o servidor, não sobe nada e termina.", "Usar `yield` no corpo de uma rota. Funciona, mas `respond` já monta a"]},
  {"p": "resposta com o status e o tipo certos."},
  {"h2": "193 · Parametros de caminho e query string"},
  {"p": "**Enunciado.** leia :id do caminho e ?campo= da query."},
  { code: `// Dentro de uma rota voce ja tem seis nomes prontos: 'req', 'params',
// 'query', 'body', 'headers' e 'session'. Escrever
// req["params"]["id"] toda vez cansa; os atalhos existem por isso.

adopt Kiln

server api on 0:
    // ':id' casa um trecho; '*resto' casa o que sobrar, barras inclusive
    route GET "/usuarios/:id":
        respond json {"id": params["id"], "formato": query["f"] ?? "curto"}

    route GET "/arquivos/*caminho":
        respond json {"caminho": params["caminho"]}

curto := Kiln.test(api, "GET", "/usuarios/42")
out "sem query:", curto["body"]
assert curto["body"]["id"] is "42", "o parametro chega como texto"
assert curto["body"]["formato"] is "curto", "?? cobre a query ausente"

longo := Kiln.test(api, "GET", "/usuarios/42?f=longo")
out "com query:", longo["body"]["formato"]
assert longo["body"]["formato"] is "longo", "a query e lida"

fundo := Kiln.test(api, "GET", "/arquivos/notas/2026/marco.txt")
out "curinga:", fundo["body"]["caminho"]
assert fundo["body"]["caminho"] is "notas/2026/marco.txt", "'*' pega tudo"`, lang: 'df', title: `exercicios/22-web-kiln/193_parametros_e_query.df` },
  {"h3": "Conceitos"},
  {"p": "Um padrão de rota tem duas formas de capturar:"},
  {"table": {"head": ["Padrão", "Casa", "Resultado"], "rows": [["`/users/:id`", "`/users/42`", "`params[\"id\"]` é `\"42\"`"], ["`/files/*caminho`", "`/files/a/b.txt`", "`params[\"caminho\"]` é `\"a/b.txt\"`"]]}},
  {"p": "`:nome` para um trecho, `*nome` para tudo o que sobrar — barras inclusive."},
  {"p": "Dentro de uma rota você já tem seis nomes prontos:"},
  { code: `route GET "/usuarios/:id":
    respond json {"id": params["id"], "formato": query["f"] ?? "curto"}`, lang: 'df' },
  {"table": {"head": ["Nome", "É"], "rows": [["`req`", "a requisição inteira"], ["`params`", "os parâmetros do caminho"], ["`query`", "a query string"], ["`body`", "o corpo já interpretado"], ["`headers`", "os cabeçalhos, em minúsculas"], ["`session`", "a sessão do visitante"]]}},
  {"h3": "O que observar"},
  {"p": "**Parâmetro é sempre texto.** `/usuarios/42` dá `\"42\"`, não `42` — HTTP não tem tipos. Converta com `int()` quando precisar."},
  {"p": "**A query decide sozinha entre texto e lista.** `?nome=x` dá `\"x\"`; `?tag=a&tag=b` dá `[\"a\", \"b\"]`. Obrigar a indexar `[0]` sempre seria ruído em 95% dos casos."},
  {"p": "**`??` combina bem com query ausente.** `query[\"f\"] ?? \"curto\"` cobre o caso de o visitante não ter passado o campo."},
  {"h3": "Erros comuns"},
  {"list": ["Comparar `params[\"id\"] is 42`. É `\"42\"`, texto. Use `int(params[\"id\"])`.", "Esperar que `query[\"tag\"]` seja sempre lista. Com um valor só, é texto."]},
  {"h2": "194 · Uma API RESTful completa"},
  {"p": "**Enunciado.** os cinco verbos sobre um mesmo recurso, com os status certos."},
  { code: `// REST nao e so usar POST e GET: cada situacao tem seu status. 201 para
// criado, 204 para apagado sem corpo, 404 para inexistente, 405 quando
// o caminho existe mas o verbo nao. O Kiln entrega 404 e 405 sozinho;
// os outros sao decisao sua.

adopt Kiln
adopt Arcane.Concurrent as Conc

itens := [
    {"id": 1, "nome": "Martelo", "preco": 89.9},
    {"id": 2, "nome": "Bigorna", "preco": 450.0}
]

// A TRAVA que falta em quase todo CRUD em memoria.
//
// O Kiln atende um pedido por thread. Duas escritas simultanEas na
// mesma lista se atropelam: um PUT que le o indice 3 e escreve nele
// depois de um DELETE ter tirado o item 2 escreve no lugar errado.
//
// O 'check' avisa ('escrita-concorrente'), e a resposta e segurar a
// trava em volta da escrita — nao da leitura, que nao muda nada.
//
// 'mutex()' tem 'acquire' e 'release'; 'defer' garante o release mesmo
// se o corpo levantar, que e o unico jeito de nao deixar a trava presa.
trava := Conc.mutex()

action criar(dados):
    // 'len' e 'append' juntos: dois POST simultaneos leriam o mesmo
    // tamanho e dariam o mesmo id. A trava cobre os dois.
    trava.acquire()
    defer:
        trava.release()
    novo := {"id": len(itens) + 1, "nome": dados["nome"],
        "preco": dados["preco"]}
    itens.append(novo)
    yield novo

action trocar(i, novo):
    trava.acquire()
    defer:
        trava.release()
    itens[i] := novo

action apagar(i):
    trava.acquire()
    defer:
        trava.release()
    itens.pop(i)

action indice_de(id):
    cycle i from 0 to len(itens) - 1:
        given itens[i]["id"] is int(id):
            yield i
    yield -1

server loja on 0:
    route GET "/itens":
        respond json {"itens": itens, "total": len(itens)}

    route GET "/itens/:id":
        pedido := params["id"]
        i := indice_de(pedido)
        given i is -1:
            respond 404 json {"erro": $"item {pedido} nao existe"}
        respond json itens[i]

    route POST "/itens":
        // 'len' e 'append' juntos: dois POST simultaneos leriam o
        // mesmo tamanho e dariam o mesmo id. A trava cobre os dois.
        novo := criar(body)
        respond 201 json novo

    route PUT "/itens/:id":
        i := indice_de(params["id"])
        given i is -1:
            respond 404 json {"erro": "nao existe"}
        novo := {"id": int(params["id"]), "nome": body["nome"],
            "preco": body["preco"]}
        trocar(i, novo)
        respond json novo

    route DELETE "/itens/:id":
        i := indice_de(params["id"])
        given i is -1:
            respond 404 json {"erro": "nao existe"}
        apagar(i)
        respond 204

out "lista:", Kiln.test(loja, "GET", "/itens")["body"]["total"]

criado := Kiln.test(loja, "POST", "/itens", {"nome": "Tenaz", "preco": 65.5})
out "criado:", criado["status"], criado["body"]["nome"]
assert criado["status"] is 201, "criar devolve 201"

trocado := Kiln.test(loja, "PUT", "/itens/1", {"nome": "Marreta", "preco": 120})
out "trocado:", trocado["body"]["nome"]
assert trocado["body"]["nome"] is "Marreta", "PUT substitui"

apagado := Kiln.test(loja, "DELETE", "/itens/2")
out "apagado:", apagado["status"]
assert apagado["status"] is 204, "apagar nao devolve corpo"

assert Kiln.test(loja, "GET", "/itens/999")["status"] is 404, "404 do recurso"

// O caminho existe, o verbo nao: 405, com a lista do que e aceito.
recusa := Kiln.test(loja, "PATCH", "/itens/1")
out "verbo errado:", recusa["status"], recusa["headers"]["Allow"]
assert recusa["status"] is 405, "405, nao 404 — o caminho existe"`, lang: 'df', title: `exercicios/22-web-kiln/194_crud_restful.df` },
  {"h3": "Conceitos"},
  {"p": "REST não é só usar `POST` e `GET`. Cada situação tem seu status, e usar o certo é o que faz a API ser previsível para quem a consome:"},
  {"table": {"head": ["Situação", "Status", "Quem decide"], "rows": [["leitura com sucesso", "200", "você"], ["criado", "**201**", "você"], ["apagado, sem corpo", "**204**", "você"], ["recurso inexistente", "404", "o Kiln, se a rota não casar"], ["caminho existe, verbo não", "**405** + `Allow`", "o Kiln"]]}},
  { code: `route POST "/itens":
    novo := {"id": len(itens) + 1, "nome": body["nome"]}
    itens.append(novo)
    respond 201 json novo

route DELETE "/itens/:id":
    respond 204`, lang: 'df' },
  {"p": "`respond 204` sozinho é válido: status sem corpo."},
  {"h3": "O que observar"},
  {"p": "**404 e 405 são coisas diferentes.** Se o caminho `/itens/1` existe mas só aceita `GET`, `PUT` e `DELETE`, um `PATCH` recebe **405** com `Allow: DELETE, GET, PUT`. Devolver 404 ali mandaria o cliente procurar um bug que não existe."},
  {"p": "**O corpo chega interpretado.** Com `Content-Type: application/json`, `body` já é um vault. JSON quebrado **não** vira erro 500: chega como texto, e a rota decide se responde 400 — porque JSON inválido é problema do cliente, não falha do servidor."},
  {"p": "**Um erro na rota não derruba o servidor.** Vira 500, o detalhe sai no terminal, e o próximo pedido é atendido normalmente."},
  {"h3": "Erros comuns"},
  {"list": ["Devolver 200 em tudo. O cliente não tem como distinguir \"criei\" de \"já"]},
  {"p": "existia\"."},
  {"list": ["Devolver corpo no 204. Por definição, 204 é \"sem conteúdo\".", "Confiar em `body` sem conferir. Se o cliente mandou texto onde você esperava"]},
  {"p": "um vault, `body[\"nome\"]` falha — e vira 500."},
  {"h2": "195 · Paginas HTML com template"},
  {"p": "**Enunciado.** renderize uma pagina a partir de um template com laco."},
  { code: `// 'render' le um arquivo da pasta declarada em 'views' e devolve HTML.
// A sintaxe do template e pequena de proposito: {{nome}} escreve,
// {{#lista}}…{{/lista}} repete, {{^lista}}…{{/lista}} cobre o vazio e
// {{&bruto}} nao escapa. Template que vira linguagem e codigo escondido
// onde ninguem procura.

adopt Kiln
adopt Arcane.IO as IO
adopt Arcane.OS as OS

// escreve o template no disco para o exercicio ser auto-contido
pasta := IO.join(OS.temp_dir(), "kilnviews")
IO.mkdir(pasta)  // sem isto, so roda se a pasta ja existir
IO.write_file(pasta + "/lista.html", """<!doctype html>
<title>{{titulo}}</title>
<h1>{{titulo}}</h1>
{{#produtos}}<article><h2>{{nome}}</h2><p>R$ {{preco}}</p></article>
{{/produtos}}
{{^produtos}}<p>Nada na forja.</p>{{/produtos}}""")

produtos := [
    {"nome": "Martelo", "preco": 89.9},
    {"nome": "Bigorna <de aco>", "preco": 450.0}
]

server site on 0:
    views pasta

    route GET "/":
        render "lista.html" with {"titulo": "Forja", "produtos": produtos}

    route GET "/vazio":
        render "lista.html" with {"titulo": "Vazio", "produtos": []}

pagina := Kiln.test(site, "GET", "/")
out pagina["body"]

assert "Martelo" in pagina["body"], "o laco do template repetiu"
// O escape e automatico: '<de aco>' nao vira tag.
assert "&lt;de aco&gt;" in pagina["body"], "HTML e escapado por padrao"
assert "<article>" in pagina["body"], "as tags do template ficam"

vazio := Kiln.test(site, "GET", "/vazio")
assert "Nada na forja" in vazio["body"], "{{^}} cobre a lista vazia"
assert "article" not in vazio["body"], "sem itens, sem artigos"`, lang: 'df', title: `exercicios/22-web-kiln/195_paginas_html.df` },
  {"h3": "Conceitos"},
  {"p": "`views` diz onde ficam os templates; `render` lê um deles e devolve HTML:"},
  { code: `server site on 8080:
    views "./paginas"

    route GET "/":
        render "lista.html" with {"titulo": "Forja", "produtos": produtos}`, lang: 'df' },
  {"p": "A sintaxe do template é pequena de propósito:"},
  {"table": {"head": ["Marca", "Faz"], "rows": [["`{{nome}}`", "escreve o valor, **escapando HTML**"], ["`{{&nome}}`", "escreve sem escapar"], ["`{{#lista}}…{{/lista}}`", "repete para cada item"], ["`{{^lista}}…{{/lista}}`", "mostra quando a lista está vazia"], ["`{{.}}`", "o item atual, numa lista de valores simples"]]}},
  {"p": "Template que vira linguagem é código escondido onde ninguém procura. Lógica de verdade fica no `.df`."},
  {"h3": "O que observar"},
  {"p": "**O escape é o padrão, não a opção.** Um produto chamado `Bigorna <de aço>` sai como `Bigorna &lt;de aço&gt;`. Isso fecha a porta para XSS por acidente — a falha mais comum em página gerada por servidor. Para escrever HTML de propósito, `{{&campo}}`, e a diferença de um caractere é o que torna a decisão visível na revisão."},
  {"p": "**`{{^lista}}` existe porque lista vazia é caso normal.** Sem ele, a página vazia sai em branco e ninguém sabe se quebrou."},
  {"p": "**`render` também encerra a rota**, como `respond`."},
  {"h3": "Erros comuns"},
  {"list": ["Bloco aberto e nunca fechado (`{{#itens}}` sem `{{/itens}}`). O Kiln reclama"]},
  {"p": "com o nome do bloco em vez de renderizar metade da página."},
  {"list": ["Esquecer o `views`. Sem a pasta declarada, `render` diz exatamente isso.", "Usar `{{&campo}}` com texto vindo do usuário. É abrir a porta que o escape"]},
  {"p": "fecha."},
  {"h2": "196 · Middleware, autenticacao e limite de taxa"},
  {"p": "**Enunciado.** proteja rotas e limite pedidos por IP."},
  { code: `// Middleware roda antes de toda rota. Se ele devolve uma resposta, a
// cadeia para ali — e assim que autenticacao e limite de taxa cortam o
// pedido antes de ele custar qualquer coisa. Se devolve void, o pedido
// segue, e o que ele guardou em req["state"] chega na rota.

adopt Kiln

usuarios := {"tk-ana": "Ana", "tk-bia": "Bia"}

action conferir(token):
    yield usuarios[token] ?? void

// A ordem importa. O limite vem primeiro: um pedido barrado pelo 'auth'
// nunca chegaria a ser contado, e quem esta martelando a porta com
// credenciais invalidas e justamente quem voce quer limitar.
server privado on 0:
    middleware Kiln.rate_limit(3, 60)
    middleware Kiln.auth(conferir)

    route GET "/eu":
        respond json {"usuario": req["state"]["user"]}

sem_token := Kiln.test(privado, "GET", "/eu")
out "sem credencial:", sem_token["status"], sem_token["headers"]["WWW-Authenticate"]
assert sem_token["status"] is 401, "sem token, 401"

errado := Kiln.test(privado, "GET", "/eu", void, {"Authorization": "Bearer nao-existe"})
out "token invalido:", errado["status"]
assert errado["status"] is 401, "token desconhecido tambem e 401"

certo := Kiln.test(privado, "GET", "/eu", void, {"Authorization": "Bearer tk-ana"})
out "autenticado:", certo["body"]["usuario"]
assert certo["body"]["usuario"] is "Ana", "o middleware passou o usuario adiante"

// O limite ja contou tres pedidos deste IP — inclusive os dois que o
// 'auth' recusou. O quarto nao passa, mesmo com credencial boa.
excedido := Kiln.test(privado, "GET", "/eu", void, {"Authorization": "Bearer tk-bia"})
out "quarto pedido:", excedido["status"]
assert excedido["status"] is 429, "o quarto pedido no minuto e recusado"
assert "Retry-After" in excedido["headers"], "e o cliente sabe quando voltar"`, lang: 'df', title: `exercicios/22-web-kiln/196_middleware_e_auth.df` },
  {"h3": "Conceitos"},
  {"p": "Middleware roda **antes** de toda rota do servidor:"},
  { code: `server privado on 8080:
    middleware Kiln.rate_limit(3, 60)
    middleware Kiln.auth(conferir)`, lang: 'df' },
  {"p": "A regra é uma só: **se o middleware devolve uma resposta, a cadeia para ali.** Se devolve `void`, o pedido segue, e o que ele guardou em `req[\"state\"]` chega na rota."},
  {"table": {"head": ["Pronto", "Faz"], "rows": [["`Kiln.cors(origens)`", "responde o preflight e libera origens"], ["`Kiln.logger()`", "uma linha por pedido no terminal"], ["`Kiln.rate_limit(max, janela)`", "429 + `Retry-After` ao estourar"], ["`Kiln.auth(verificador)`", "401 sem credencial; põe o usuário em `state`"], ["`Kiln.guard(condicao, status)`", "middleware a partir de qualquer condição"]]}},
  {"h3": "O que observar"},
  {"p": "**A ordem importa, e não é detalhe.** No exercício, `rate_limit` vem antes de `auth`. Se fosse o contrário, um pedido barrado pelo `auth` nunca seria contado — e quem está martelando a porta com credenciais inválidas é justamente quem você quer limitar."},
  {"p": "**Autenticação é uma função sua.** `Kiln.auth` cuida do protocolo (ler o cabeçalho, devolver 401 com `WWW-Authenticate`); quem decide se o token vale é a ação que você passa. O Kiln não escolhe seu banco nem seu formato de token."},
  {"p": "**O 429 diz quando voltar.** `Retry-After` no cabeçalho é a diferença entre um cliente que espera e um que fica tentando."},
  {"h3": "Erros comuns"},
  {"list": ["Pôr autenticação antes do limite de taxa.", "Middleware que devolve algo sem querer. Só devolva quando for para **cortar**"]},
  {"p": "o pedido."},
  {"list": ["Confiar no `rate_limit` em produção com vários processos: a contagem é por"]},
  {"p": "processo, em memória."},
  {"h2": "197 · Paginas de erro, redirecionamento e arquivos estaticos"},
  {"p": "**Enunciado.** personalize o 404, redirecione uma rota antiga e sirva CSS."},
  { code: `// Um 404 em JSON serve para uma API; para um site, o visitante merece
// uma pagina. Kiln.on_error troca a resposta de um status inteiro.

adopt Kiln
adopt Arcane.IO as IO
adopt Arcane.OS as OS

IO.mkdir(IO.join(OS.temp_dir(), "kilnviews"))  // sem isto, so roda se a pasta ja existir
IO.write_file(IO.join(OS.temp_dir(), "kilnviews", "estilo.css"), "body {font: 16px system-ui}")

server site on 0:
    assets "/static" from IO.join(OS.temp_dir(), "kilnviews")

    route GET "/":
        respond html "<h1>Inicio</h1>"

    route GET "/antigo":
        redirect "/"

Kiln.on_error(site, 404, lambda req => Kiln.html(
        "<h1>404</h1><p>Nao achei essa pagina.</p>", 404))

assert Kiln.test(site, "GET", "/")["status"] is 200, "a raiz responde"

perdido := Kiln.test(site, "GET", "/nao-existe")
out "404 personalizado:", perdido["status"]
out perdido["body"]
assert perdido["status"] is 404, "o status continua 404"
assert "Nao achei" in perdido["body"], "mas o corpo agora e uma pagina"

mudou := Kiln.test(site, "GET", "/antigo")
out "redirect:", mudou["status"], "->", mudou["headers"]["Location"]
assert mudou["status"] is 302, "redirect padrao e 302"
assert mudou["headers"]["Location"] is "/", "e diz para onde ir"

css := Kiln.test(site, "GET", "/static/estilo.css")
out "css:", css["status"]
assert css["status"] is 200, "o arquivo do disco e servido"

// Um '../' no caminho nao escapa da pasta declarada. Esta e a falha
// classica de servidor de arquivos, e o Kiln recusa antes de abrir.
fuga := Kiln.test(site, "GET", "/static/../../../etc/passwd")
out "travessia de diretorio:", fuga["status"]
assert fuga["status"] is 403, "sair da pasta e proibido"`, lang: 'df', title: `exercicios/22-web-kiln/197_erros_e_estaticos.df` },
  {"h3": "Conceitos"},
  { code: `server site on 8080:
    assets "/static" from "./www"

    route GET "/antigo":
        redirect "/"

Kiln.on_error(site, 404, minha_pagina_404)`, lang: 'df' },
  {"table": {"head": ["Palavra", "Faz"], "rows": [["`assets \"/prefixo\" from \"pasta\"`", "serve arquivos do disco"], ["`redirect \"/destino\"`", "302 com `Location` (use `status 301` para permanente)"], ["`Kiln.on_error(app, status, handler)`", "troca a resposta de um status"]]}},
  {"h3": "O que observar"},
  {"p": "**404 em JSON serve para uma API; um site merece uma página.** `on_error` troca o corpo mantendo o status — o status é o que os buscadores e os clientes leem, e ele não muda."},
  {"p": "**`../` não escapa da pasta servida.** Um pedido a `/static/../../../etc/passwd` recebe **403**, e a checagem acontece antes de qualquer arquivo ser aberto. Essa é a falha clássica de servidor de arquivos, e vale saber que ela está fechada."},
  {"p": "**302 é temporário, 301 é permanente.** O 301 fica no cache do navegador praticamente para sempre; use só quando o endereço mudou de verdade."},
  {"h3": "Erros comuns"},
  {"list": ["Trocar o status junto com o corpo no `on_error`. Se você responde 200 numa"]},
  {"p": "página de erro, buscadores indexam a página de erro."},
  {"list": ["Servir a pasta do projeto inteiro em `assets`. Sirva só o que é público —"]},
  {"p": "o `.git` e o `.env` moram no mesmo disco."},
  {"h2": "198 · Subir o servidor de verdade"},
  {"p": "**Enunciado.** acenda o forno, faca um pedido pela rede e apague."},
  { code: `// Ate aqui usamos Kiln.test, que executa a rota sem abrir socket. Agora
// o servidor de verdade: 'Kiln.serve' sobe em segundo plano e devolve a
// porta na hora (porta 0 deixa o sistema escolher uma livre — util em
// teste, onde uma porta fixa daria conflito). Em producao voce usa
// 'ignite', que bloqueia ate o Ctrl-C.

adopt Kiln
adopt Arcane.Web as Web
adopt Arcane.Concurrent as Conc

// Um CONTADOR ATOMICO, e nao uma variavel solta.
//
// O Kiln usa 'ThreadingHTTPServer': cada pedido roda numa thread. Dois
// pedidos ao mesmo tempo em 'visitas += 1' leem o mesmo valor e
// escrevem o mesmo — um incremento se perde.
//
// Medido: seis pedidos simultaneos numa rota que le, espera e escreve
// entregaram 1 de 6. O 'check' avisa isto ('escrita-concorrente'), e a
// resposta e uma linha.
visitas := Conc.contador()

server contador on 0:
    route GET "/":
        respond html "<h1>Forja</h1>"

    route GET "/contar":
        // 'somar' devolve o valor novo, dentro da trava: nao ha janela
        // entre ler e escrever.
        respond json {"visitas": visitas.somar(1)}

porta := Kiln.serve(contador, 0)
out "no ar na porta", porta

pagina := Web.get($"http://127.0.0.1:{porta}/")
out "pela rede:", pagina["status"], pagina["body"]
assert pagina["status"] is 200, "o servidor respondeu de verdade"
assert "Forja" in pagina["body"], "o HTML chegou inteiro"

Web.get($"http://127.0.0.1:{porta}/contar")
Web.get($"http://127.0.0.1:{porta}/contar")
terceira := Web.get($"http://127.0.0.1:{porta}/contar")
out "tres pedidos:", terceira["body"]
assert visitas.valor() is 3, "o estado do programa sobrevive entre pedidos"

numeros := Kiln.stats(contador)
out "estatisticas:", numeros["pedidos"], "pedidos,", numeros["rotas"], "rotas"
assert numeros["pedidos"] is 4, "quatro pedidos contados"
assert numeros["erros"] is 0, "nenhum erro"

Kiln.stop(contador)
out "forno apagado"

// Em um programa de verdade, a ultima linha seria:
//     ignite contador on 8080
// que sobe e fica servindo ate voce apertar Ctrl-C.`, lang: 'df', title: `exercicios/22-web-kiln/198_servidor_de_verdade.df` },
  {"h3": "Conceitos"},
  {"p": "Três formas de rodar, para três momentos:"},
  {"table": {"head": ["Forma", "Faz", "Quando"], "rows": [["`Kiln.test(app, verbo, caminho)`", "executa a rota, sem socket", "teste"], ["`Kiln.serve(app, porta)`", "sobe em segundo plano, devolve a porta", "script, teste de integração"], ["`ignite app on 8080`", "sobe e bloqueia até Ctrl-C", "produção"]]}},
  { code: `porta := Kiln.serve(contador, 0)     // 0 = o sistema escolhe uma livre
// … faz pedidos …
Kiln.stop(contador)`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**Porta 0 deixa o sistema escolher.** Numa suíte de testes, porta fixa dá conflito quando dois testes rodam juntos — ou quando você esqueceu um servidor no ar. `Kiln.serve` devolve a porta que saiu."},
  {"p": "**O estado do programa sobrevive entre pedidos.** A variável `visitas` é do programa, não do pedido: três chamadas a `/contar` dão 3. Isso vale para qualquer estado em memória — e some quando o processo reinicia."},
  {"p": "**`Kiln.stats` conta o que aconteceu**: pedidos, erros, rotas e tempo no ar."},
  {"p": "**Cada pedido roda numa thread.** Dois pedidos simultâneos que escrevem na mesma variável podem perder atualizações — a linguagem não sincroniza threads."},
  {"h3": "Erros comuns"},
  {"list": ["Usar `ignite` num teste. Ele bloqueia, e o teste nunca termina.", "Esquecer `Kiln.stop`. A porta fica ocupada até o processo morrer.", "Guardar sessão em memória e rodar vários processos. Cada um tem a sua, e o"]},
  {"p": "visitante desloga a cada pedido."},
  {"h2": "199 · A API vista de fora: OpenAPI, Insomnia e curl"},
  {"p": "**Enunciado.** exporte as rotas de um servidor Kiln para as ferramentas"},
  { code: `// que quem consome a API de fato usa.

adopt Kiln
adopt Arcane.API as API

// ── Um servidor REST de verdade ──
//
// Os cinco metodos que um recurso REST tem. Repare que nada aqui e
// declarado DUAS vezes: nao ha um arquivo de documentacao ao lado
// dizendo o que as rotas sao. As rotas sao a fonte da verdade.

server Loja on 8080:
    route GET "/produtos":
        respond json {"produtos": [], "total": 0}

    route POST "/produtos":
        respond json {"criado": yes}

    route GET "/produtos/:id":
        respond json {"id": params["id"]}

    route PATCH "/produtos/:id":
        respond json {"alterado": params["id"]}

    route DELETE "/produtos/:id":
        respond json {"removido": params["id"]}

steady CONF := {
    "titulo": "API da Loja",
    "versao": "2.0.0",
    "base": "https://api.loja.com"
}

// ── 1. O que existe ──

resumo := API.resumo(Loja)
out $"rotas: {resumo["rotas"]}"
out $"metodos: {resumo["metodos"]}"
out $"com parametro: {resumo["com_parametro"]}"

assert resumo["rotas"] is 5, "cinco rotas"
assert resumo["com_parametro"] is 3, "tres usam:id"

// ── 2. OpenAPI, para o Swagger e para gerar cliente ──

adopt Arcane.Serialization as Serde

texto := API.openapi(Loja, CONF)
documento := Serde.from_json(texto)

out ""
out $"openapi: {documento["openapi"]}"
out $"titulo:  {documento["info"]["title"]}"
out $"caminhos: {documento["paths"].keys()}"

assert documento["openapi"] is "3.1.0", "OpenAPI 3.1"
assert "/produtos/{id}" in documento["paths"].keys(), "o:id virou {id}"

// O parametro de caminho e DECLARADO. Sem isso, o Swagger trata ':id'
// como parte literal do caminho, e o cliente gerado bate numa URL que
// nao existe.
parametro := documento["paths"]["/produtos/{id}"]["get"]["parameters"][0]
out $"parametro: {parametro["name"]} em {parametro["in"]}"
assert parametro["name"] is "id", "o parametro se chama id"

// ── 3. Insomnia, para testar a mao ──

colecao := Serde.from_json(API.insomnia(Loja, CONF))
pedidos := colecao["resources"] >> sift r: (r["_type"] ?? "") is "request"

out ""
out $"requisicoes: {len(pedidos)}"
out $"primeira: {pedidos[0]["method"]} {pedidos[0]["url"]}"

assert len(pedidos) is 5, "uma requisicao por rota"

// '{{ id }}' e o que o Insomnia reconhece como variavel. Deixar ':id'
// cru daria uma requisicao que bate literalmente em '/produtos/:id'.
com_variavel := pedidos >> sift p: "{{ id }}" in p["url"]
assert len(com_variavel) is 3, "as tres rotas com :id viraram variavel"

// ── 4. curl, para o README ──

comandos := API.curl(Loja, CONF)
out ""
out comandos.lines()[0]
out comandos.lines()[1]

assert comandos.count("curl ") is 5, "um curl por rota"
assert "https://api.loja.com" in comandos, "a base configurada"

// ── 5. Markdown, para a documentacao do projeto ──

tabela := API.markdown(Loja, CONF)
assert "| \`GET\` | \`/produtos\` |" in tabela, "a tabela de rotas"
assert "# API da Loja" in tabela, "o titulo"

out ""
out "ok"`, lang: 'df', title: `exercicios/22-web-kiln/199_api_rest_export.df` },
  {"h3": "Conceitos"},
  { code: `adopt Arcane.API as API

out API.openapi(servidor, {"titulo": "Minha API"})
out API.insomnia(servidor)
out API.curl(servidor)`, lang: 'df' },
  {"p": "E na linha de comando, que é como se usa na prática:"},
  { code: `dataforge api src/app.df --openapi  -o=openapi.json
dataforge api src/app.df --insomnia -o=insomnia.json
dataforge api src/app.df --curl`, lang: 'bash' },
  {"h3": "Por que não escrever a documentação à mão"},
  {"p": "Ela resolve por uma semana. Depois alguém acrescenta uma rota e esquece de atualizar, e a documentação passa a mentir — o que é **pior que não ter**, porque quem a lê não tem como saber."},
  {"p": "Aqui ela é derivada das rotas registradas. O servidor é a fonte da verdade, e isto é uma projeção dele: acrescentar uma rota e reexportar são a mesma ação."},
  {"h3": "Aponte para o `app.df`, não para o `main.df`"},
  {"p": "O arquivo é **executado** para que as rotas se registrem — é assim que um servidor Kiln se declara. O `main.df` chama `ignite` e nunca voltaria."},
  {"p": "É a mesma separação que `projetos/loja-web` já usava para poder testar rotas sem abrir socket. Agora ela tem uma segunda razão de existir."},
  {"h3": "As traduções que importam"},
  {"table": {"head": ["No Kiln", "No formato", "Por quê"], "rows": [["`/produtos/:id`", "OpenAPI: `/produtos/{id}`", "o Swagger trataria `:id` como parte literal, e o cliente gerado bateria numa URL que não existe"], ["`/produtos/:id`", "Insomnia: `{{ id }}`", "`{{ }}` é o que o Insomnia reconhece como variável"], ["a porta do `server`", "ambiente `base`", "trocar de máquina passa a ser editar um campo"], ["`POST`/`PUT`/`PATCH`", "corpo JSON vazio", "pronto para preencher; `GET` não ganha corpo"]]}},
  {"h3": "O que ele **não** infere"},
  {"p": "O Kiln não declara tipos de corpo nem de resposta: `respond json {…}` monta o vault na hora. Então o **esquema** de entrada e saída não aparece — só a rota, o método e os parâmetros de caminho."},
  {"p": "Inventar um esquema a partir de um exemplo daria uma documentação com *aparência* de completa e conteúdo adivinhado. Isso é especialmente perigoso aqui: alguém vai gerar um cliente a partir desse arquivo."},
  {"p": "Uma documentação menor e verdadeira é mais útil que uma grande e inventada."},
  {"h3": "Saída esperada"},
  { code: `rotas: 5
metodos: {GET: 2, POST: 1, PATCH: 1, DELETE: 1}
com parametro: 3

openapi: 3.1.0
titulo:  API da Loja
caminhos: [/produtos, /produtos/{id}]
parametro: id em path

requisicoes: 5
primeira: GET {{ base }}/produtos

# Lista produtos
curl https://api.loja.com/produtos

ok`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente uma rota `PUT` e reexporte: repare que não há um segundo"]},
  {"p": "lugar para atualizar."},
  {"list": ["Importe o `insomnia.json` no Insomnia e dispare as cinco requisições.", "Rode `dataforge api` num dos projetos de `projetos/` e compare o que"]},
  {"p": "sai com o que o código faz."},
  {"list": ["Gere o OpenAPI e cole em `editor.swagger.io`."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/22-web-kiln/192_primeiro_servidor.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '192-o-primeiro-servidor', text: "192 · O primeiro servidor", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '193-parametros-de-caminho-e-query-string', text: "193 · Parametros de caminho e query string", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '194-uma-api-restful-completa', text: "194 · Uma API RESTful completa", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '195-paginas-html-com-template', text: "195 · Paginas HTML com template", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '196-middleware-autenticacao-e-limite-de-taxa', text: "196 · Middleware, autenticacao e limite de taxa", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '197-paginas-de-erro-redirecionamento-e-arquivos-estaticos', text: "197 · Paginas de erro, redirecionamento e arquivos estaticos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '198-subir-o-servidor-de-verdade', text: "198 · Subir o servidor de verdade", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'erros-comuns', text: "Erros comuns", level: 3 as const }, { id: '199-a-api-vista-de-fora-openapi-insomnia-e-curl', text: "199 · A API vista de fora: OpenAPI, Insomnia e curl", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-nao-escrever-a-documentacao-a-mao', text: "Por que não escrever a documentação à mão", level: 3 as const }, { id: 'aponte-para-o-appdf-nao-para-o-maindf', text: "Aponte para o `app.df`, não para o `main.df`", level: 3 as const }, { id: 'as-traducoes-que-importam', text: "As traduções que importam", level: 3 as const }, { id: 'o-que-ele-nao-infere', text: "O que ele **não** infere", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"22 · Web com Kiln"}
      description={"8 exercícios: rotas, respostas, templates e estáticos."}
      href={"/docs/exercicios/22-web-kiln"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
