import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "22 · Web com Kiln",
  description: "Servidor, rotas, páginas HTML, middleware, sessão e produção.",
};

const blocos: Bloco[] = [
  {"p": "Sete exercícios sobre o [Kiln](/docs/kiln): do primeiro `respond` a um servidor de verdade atendendo pela rede."},
  { code: `python3 exercicios/run_all.py 22`, lang: 'bash' },
  {"p": "Cada um tem um `.md` ao lado explicando o conceito, comparando com outras linguagens e listando as armadilhas."},
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "O que ensina"], "rows": [["191", "**O primeiro servidor**", "Declare um servidor com duas rotas e responda texto e html"], ["192", "**Parametros de caminho e query string**", "Leia :id do caminho e ?campo= da query"], ["193", "**Uma API RESTful completa**", "Os cinco verbos sobre um mesmo recurso, com os status certos"], ["194", "**Paginas HTML com template**", "Renderize uma pagina a partir de um template com laco"], ["195", "**Middleware, autenticacao e limite de taxa**", "Proteja rotas e limite pedidos por ip"], ["196", "**Paginas de erro, redirecionamento e arquivos estaticos**", "Personalize o 404, redirecione uma rota antiga e sirva css"], ["197", "**Subir o servidor de verdade**", "Acenda o forno, faca um pedido pela rede e apague"]]}},
  {"callout": {"tipo": "nota", "titulo": "Teste antes de subir", "texto": "Seis dos sete exercícios usam `Kiln.test`, que executa a rota sem abrir socket. Só o último sobe o servidor de fato — e é lá que aparecem os problemas que nenhum teste na mesma thread pega."}},
  {"h2": "191 · O primeiro servidor"},
  {"p": "Declare um servidor com duas rotas e responda texto e html."},
  { code: `// Exercicio 191 — O primeiro servidor
// Enunciado: declare um servidor com duas rotas e responda texto e HTML.

// 'server' declara a aplicacao; 'route' declara uma rota; 'respond'
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
assert Kiln.test(ola, "GET", "/nada")["status"] is 404, "404 automatico"
` },
  {"h2": "192 · Parametros de caminho e query string"},
  {"p": "Leia :id do caminho e ?campo= da query."},
  { code: `// Exercicio 192 — Parametros de caminho e query string
// Enunciado: leia :id do caminho e ?campo= da query.

// Dentro de uma rota voce ja tem seis nomes prontos: 'req', 'params',
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
assert fundo["body"]["caminho"] is "notas/2026/marco.txt", "'*' pega tudo"
` },
  {"h2": "193 · Uma API RESTful completa"},
  {"p": "Os cinco verbos sobre um mesmo recurso, com os status certos."},
  { code: `// Exercicio 193 — Uma API RESTful completa
// Enunciado: os cinco verbos sobre um mesmo recurso, com os status certos.

// REST nao e so usar POST e GET: cada situacao tem seu status. 201 para
// criado, 204 para apagado sem corpo, 404 para inexistente, 405 quando
// o caminho existe mas o verbo nao. O Kiln entrega 404 e 405 sozinho;
// os outros sao decisao sua.

adopt Kiln

itens := [
    {"id": 1, "nome": "Martelo", "preco": 89.9},
    {"id": 2, "nome": "Bigorna", "preco": 450.0}
]

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
        novo := {"id": len(itens) + 1, "nome": body["nome"], "preco": body["preco"]}
        itens.append(novo)
        respond 201 json novo

    route PUT "/itens/:id":
        i := indice_de(params["id"])
        given i is -1:
            respond 404 json {"erro": "nao existe"}
        itens[i] := {"id": int(params["id"]), "nome": body["nome"], "preco": body["preco"]}
        respond json itens[i]

    route DELETE "/itens/:id":
        i := indice_de(params["id"])
        given i is -1:
            respond 404 json {"erro": "nao existe"}
        itens.pop(i)
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
assert recusa["status"] is 405, "405, nao 404 — o caminho existe"
` },
  {"h2": "194 · Paginas HTML com template"},
  {"p": "Renderize uma pagina a partir de um template com laco."},
  { code: `// Exercicio 194 — Paginas HTML com template
// Enunciado: renderize uma pagina a partir de um template com laco.

// 'render' le um arquivo da pasta declarada em 'views' e devolve HTML.
// A sintaxe do template e pequena de proposito: {{nome}} escreve,
// {{#lista}}…{{/lista}} repete, {{^lista}}…{{/lista}} cobre o vazio e
// {{&bruto}} nao escapa. Template que vira linguagem e codigo escondido
// onde ninguem procura.

adopt Kiln
adopt Arcane.IO as IO

// escreve o template no disco para o exercicio ser auto-contido
pasta := "/tmp/kilnviews"
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
assert "article" not in vazio["body"], "sem itens, sem artigos"
` },
  {"h2": "195 · Middleware, autenticacao e limite de taxa"},
  {"p": "Proteja rotas e limite pedidos por ip."},
  { code: `// Exercicio 195 — Middleware, autenticacao e limite de taxa
// Enunciado: proteja rotas e limite pedidos por IP.

// Middleware roda antes de toda rota. Se ele devolve uma resposta, a
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
assert "Retry-After" in excedido["headers"], "e o cliente sabe quando voltar"
` },
  {"h2": "196 · Paginas de erro, redirecionamento e arquivos estaticos"},
  {"p": "Personalize o 404, redirecione uma rota antiga e sirva css."},
  { code: `// Exercicio 196 — Paginas de erro, redirecionamento e arquivos estaticos
// Enunciado: personalize o 404, redirecione uma rota antiga e sirva CSS.

// Um 404 em JSON serve para uma API; para um site, o visitante merece
// uma pagina. Kiln.on_error troca a resposta de um status inteiro.

adopt Kiln
adopt Arcane.IO as IO

IO.write_file("/tmp/kilnviews/estilo.css", "body { font: 16px system-ui }")

server site on 0:
    assets "/static" from "/tmp/kilnviews"

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
assert fuga["status"] is 403, "sair da pasta e proibido"
` },
  {"h2": "197 · Subir o servidor de verdade"},
  {"p": "Acenda o forno, faca um pedido pela rede e apague."},
  { code: `// Exercicio 197 — Subir o servidor de verdade
// Enunciado: acenda o forno, faca um pedido pela rede e apague.

// Ate aqui usamos Kiln.test, que executa a rota sem abrir socket. Agora
// o servidor de verdade: 'Kiln.serve' sobe em segundo plano e devolve a
// porta na hora (porta 0 deixa o sistema escolher uma livre — util em
// teste, onde uma porta fixa daria conflito). Em producao voce usa
// 'ignite', que bloqueia ate o Ctrl-C.

adopt Kiln
adopt Arcane.Web as Web

visitas := 0

server contador on 0:
    route GET "/":
        respond html "<h1>Forja</h1>"

    route GET "/contar":
        visitas += 1
        respond json {"visitas": visitas}

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
assert visitas is 3, "o estado do programa sobrevive entre pedidos"

numeros := Kiln.stats(contador)
out "estatisticas:", numeros["pedidos"], "pedidos,", numeros["rotas"], "rotas"
assert numeros["pedidos"] is 4, "quatro pedidos contados"
assert numeros["erros"] is 0, "nenhum erro"

Kiln.stop(contador)
out "forno apagado"

// Em um programa de verdade, a ultima linha seria:
//     ignite contador on 8080
// que sobe e fica servindo ate voce apertar Ctrl-C.
` },
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '191--o-primeiro-servidor', text: "191 · O primeiro servidor", level: 2 as const }, { id: '192--parametros-de-caminho-e-query-string', text: "192 · Parametros de caminho e query string", level: 2 as const }, { id: '193--uma-api-restful-completa', text: "193 · Uma API RESTful completa", level: 2 as const }, { id: '194--paginas-html-com-template', text: "194 · Paginas HTML com template", level: 2 as const }, { id: '195--middleware-autenticacao-e-limite-de-taxa', text: "195 · Middleware, autenticacao e limite de taxa", level: 2 as const }, { id: '196--paginas-de-erro-redirecionamento-e-arquivos-estaticos', text: "196 · Paginas de erro, redirecionamento e arquivos estaticos", level: 2 as const }, { id: '197--subir-o-servidor-de-verdade', text: "197 · Subir o servidor de verdade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"22 · Web com Kiln"}
      description={"Servidor, rotas, páginas HTML, middleware, sessão e produção."}
      href={"/docs/exercicios/22-web-kiln"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
