# -*- coding: utf-8 -*-
"""APIs — dez páginas sobre o que toda API HTTP acaba precisando decidir.

Quatro delas usam peças que entraram na linguagem nesta leva
(`Kiln.problema`, `negociar`, `precondicao`, `etiqueta`, `cursor`,
`ler_cursor`, `links`). Todo bloco roda, e a resposta que ele afirma foi
conferida executando.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/problemas",
"title": "Erros que um programa lê",
"description": "application/problem+json (RFC 9457): o tipo, o título, o detalhe — e por que texto de erro não é contrato.",
"blocos": [
 {"p": "Todo cliente de uma API acaba precisando decidir o que fazer com um erro: tentar de novo, pedir outro dado, mostrar uma mensagem. Se o erro é só um texto — `{\"erro\": \"saldo insuficiente\"}` —, o cliente decide **comparando texto**, e a primeira revisão de ortografia no servidor quebra todos eles."},
 {"p": "A RFC 9457 resolve isso com cinco campos, e `Kiln.problema` os monta:"},
 {"table": {"head": ["Campo", "O que é", "Quem lê"], "rows": [
   ["`type`", "uma URI que identifica o **tipo** do problema", "o programa: é por ele que se decide"],
   ["`title`", "o resumo do tipo, igual em toda ocorrência", "a pessoa, num log"],
   ["`status`", "o mesmo código da resposta HTTP", "quem só tem o corpo em mãos"],
   ["`detail`", "o que aconteceu **desta vez**", "a pessoa, na tela"],
   ["`instance`", "qual pedido falhou", "o suporte, cruzando com o log"]]}},
 {"code": '''adopt Arcane.Kiln as Kiln

saldos := {"ana": 30}
app := Kiln.app()

action comprar(req):
    quem := req["params"]["quem"]
    preco := req["body"]["preco"]
    given (saldos[quem] ?? void) is void:
        yield Kiln.problema(404, "Conta não encontrada", $"não há conta '{quem}'")
    given preco bigger saldos[quem]:
        yield Kiln.problema(422, "Saldo insuficiente",
            $"o saldo é {saldos[quem]} e a compra custa {preco}",
            "https://loja.exemplo/erros/saldo-insuficiente",
            {"saldo": saldos[quem], "preco": preco})
    saldos[quem] -= preco
    yield Kiln.json({"saldo": saldos[quem]})

Kiln.post(app, "/contas/:quem/compras", comprar)

r := Kiln.test(app, "POST", "/contas/ana/compras", {"preco": 50})
assert r["status"] is 422
assert r["body"]["type"] is "https://loja.exemplo/erros/saldo-insuficiente"
assert r["body"]["saldo"] is 30
assert Kiln.test(app, "POST", "/contas/bia/compras", {"preco": 1})["status"] is 404''', "lang": "df"},
 {"h2": "Três decisões que a peça cobra"},
 {"list": [
   "**Problema é erro.** `Kiln.problema(200, …)` é recusado: um corpo de problema num 200 faz o cliente que olha o status seguir adiante com um erro na mão.",
   "**Os campos da RFC não vêm em `extras`.** Um `extras` com `status` sobrescreveria o status real no corpo e deixaria corpo e cabeçalho dizendo coisas diferentes.",
   "**`about:blank` é o tipo padrão**, e ele quer dizer \"o status HTTP já diz tudo\". Assim que um cliente precisar distinguir dois 422, dê a cada um o seu `type`."]},
 {"callout": {"tipo": "perigo", "titulo": "O detalhe vai para fora", "texto": "`detail` chega ao cliente. Nunca ponha ali a mensagem do banco, o caminho de um arquivo ou a pilha: isso conta a estrutura interna para quem perguntar. O erro inteiro vai para o **log**, com o mesmo `instance`, e o `detail` diz o que a pessoa pode fazer."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/negociacao",
"title": "Negociação de conteúdo",
"description": "JSON ou CSV no mesmo endereço: o cabeçalho Accept, o q, o curinga — e quando responder 406.",
"blocos": [
 {"p": "O mesmo recurso pode ter mais de uma representação: a lista de pedidos em JSON para um programa, em CSV para uma planilha. O cliente diz o que aceita no `Accept`, com um peso `q` de 0 a 1, e o servidor escolhe. `Kiln.negociar` faz a escolha como a RFC 9110 manda."},
 {"code": '''adopt Arcane.Kiln as Kiln

pedidos := [{"id": 1, "total": 50}, {"id": 2, "total": 70}]
app := Kiln.app()

action listar(req):
    tipo := Kiln.negociar(req, ["application/json", "text/csv"])
    given tipo is void:
        yield Kiln.problema(406, "Formato não disponível",
            "esta rota responde application/json ou text/csv")
    given tipo is "text/csv":
        linhas := ["id,total"] + [$"{p["id"]},{p["total"]}" cycle p in pedidos]
        yield Kiln.text(linhas.join("\\n"), 200, {"Content-Type": "text/csv; charset=utf-8", "Vary": "Accept"})
    yield Kiln.json(pedidos, 200, {"Vary": "Accept"})

Kiln.get(app, "/pedidos", listar)

assert Kiln.test(app, "GET", "/pedidos")["body"][0]["id"] is 1
csv := Kiln.test(app, "GET", "/pedidos", void, {"Accept": "text/csv"})
assert csv["body"].starts_with("id,total")
assert Kiln.test(app, "GET", "/pedidos", void, {"Accept": "image/png"})["status"] is 406''', "lang": "df"},
 {"h2": "As regras, na ordem em que decidem"},
 {"table": {"head": ["Accept", "Escolhe", "Por quê"], "rows": [
   ["(nenhum)", "o primeiro oferecido", "o cliente não pediu nada"],
   ["`text/csv;q=0.5, application/json`", "JSON", "q maior vence"],
   ["`text/*`", "o primeiro `text/…` oferecido", "curinga de subtipo"],
   ["`*/*, text/csv;q=0`", "nunca CSV", "`q=0` é recusa explícita, e a faixa mais específica decide"],
   ["`image/png`", "`void` → 406", "nada que você oferece serve"]]}},
 {"callout": {"tipo": "atencao", "titulo": "`Vary: Accept`", "texto": "Quando a mesma URL responde formatos diferentes, um cache no caminho (CDN, proxy, navegador) precisa saber que a resposta **depende** do `Accept`. Sem o `Vary`, o primeiro CSV guardado é entregue a quem pediu JSON."}},
 {"callout": {"tipo": "dica", "titulo": "No empate, vale a sua ordem", "texto": "Com `Accept: */*`, qualquer oferecido serve com q=1. A escolha cai no **primeiro da sua lista** — então ponha nela primeiro o formato que você prefere servir."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/precondicoes",
"title": "Edição concorrente: ETag e If-Match",
"description": "Duas pessoas editam o mesmo recurso. Sem pré-condição, a segunda apaga a mudança da primeira — calada. Com ela, recebe 412.",
"blocos": [
 {"p": "Ana abre o pedido 7 e começa a editar. Bia abre o mesmo pedido, muda o endereço e salva. Ana salva em seguida — e o endereço da Bia some. Nenhum erro, nenhum aviso: é a **atualização perdida**, e ela acontece em toda API que aceita `PUT` sem pré-condição."},
 {"p": "A saída é o controle de concorrência **otimista**: cada leitura devolve uma etiqueta (`ETag`) da versão lida; a escrita manda a etiqueta de volta em `If-Match`; se o recurso mudou nesse meio-tempo, o servidor responde **412** em vez de sobrescrever."},
 {"code": '''adopt Arcane.Kiln as Kiln

pedidos := {"7": {"endereco": "Rua A", "versao": 1}}
app := Kiln.app()

action ler(req):
    p := pedidos[req["params"]["id"]]
    yield Kiln.json(p, 200, {"ETag": Kiln.etiqueta(p["versao"])})

action salvar(req):
    p := pedidos[req["params"]["id"]] ?? void
    atual := void given p is void otherwise Kiln.etiqueta(p["versao"])
    falha := Kiln.precondicao(req, atual, yes)
    given falha is not void:
        yield falha
    p["endereco"] := req["body"]["endereco"]
    p["versao"] += 1
    yield Kiln.json(p, 200, {"ETag": Kiln.etiqueta(p["versao"])})

Kiln.get(app, "/pedidos/:id", ler)
Kiln.put(app, "/pedidos/:id", salvar)

etiqueta_da_ana := Kiln.test(app, "GET", "/pedidos/7")["headers"]["ETag"]
etiqueta_da_bia := Kiln.test(app, "GET", "/pedidos/7")["headers"]["ETag"]

bia := Kiln.test(app, "PUT", "/pedidos/7", {"endereco": "Rua B"}, {"If-Match": etiqueta_da_bia})
assert bia["status"] is 200

ana := Kiln.test(app, "PUT", "/pedidos/7", {"endereco": "Rua C"}, {"If-Match": etiqueta_da_ana})
assert ana["status"] is 412                      // a mudança da Bia não some
assert pedidos["7"]["endereco"] is "Rua B"

sem := Kiln.test(app, "PUT", "/pedidos/7", {"endereco": "Rua D"})
assert sem["status"] is 428                      // exigir := yes''', "lang": "df"},
 {"h2": "Os quatro casos"},
 {"table": {"head": ["Pedido", "Resposta", "Uso"], "rows": [
   ["`If-Match` com a etiqueta atual", "segue", "a edição normal"],
   ["`If-Match` com outra etiqueta", "**412**", "alguém mudou no meio: leia de novo"],
   ["`If-None-Match: *`", "412 se já existe", "criar com `PUT` sem sobrescrever"],
   ["sem cabeçalho, com `exigir := yes`", "**428**", "a API não aceita escrita às cegas"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Etiqueta fraca nunca casa em `If-Match`", "texto": "Pela RFC 9110, `If-Match` usa comparação **forte**, e uma etiqueta `W/\"…\"` não casa nunca. O `Kiln.cache` gera etiquetas fracas, que servem para o 304 de uma leitura. Para escrita, use `Kiln.etiqueta(versao)`, que é forte."}},
 {"p": "É a mesma ideia do `versao_esperada` de um [armazém de eventos](/docs/dominio/concorrencia-otimista), só que atravessando HTTP."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/paginacao",
"title": "Paginação: página, cursor e Link",
"description": "Por que ?pagina=3 pula e repete itens numa lista que muda, como um cursor opaco resolve, e o cabeçalho Link.",
"blocos": [
 {"p": "`Kiln.paginar` corta por número de página, e isso é certo para uma lista que **não muda** enquanto alguém a percorre. Numa lista viva — um feed, uma fila de pedidos —, um item novo no topo empurra todos uma posição: quem pede a página 2 vê de novo o último item da página 1, e um item some entre as duas."},
 {"p": "O **cursor** diz *onde parou*, e não *em que posição*: \"depois do pedido 1042\" não se move quando chega o 1043. `Kiln.cursor` o empacota opaco, e com um segredo, assinado — o cliente não monta um à mão, e não consegue forjar."},
 {"code": '''adopt Arcane.Kiln as Kiln

steady SEGREDO := "troque-isto"
pedidos := [{"id": i} cycle i in range(1, 26)]
app := Kiln.app()

action listar(req):
    c := req["query"]["cursor"] ?? void
    depois_de := 0
    given c is not void:
        lido := Kiln.ler_cursor(c, SEGREDO)
        given lido is void:
            yield Kiln.problema(400, "Cursor inválido")
        depois_de := lido["depois_de"]
    pagina := [p cycle p in pedidos given p["id"] bigger depois_de][0:10]
    proximo := void
    given len(pagina) is 10:
        proximo := Kiln.cursor({"depois_de": pagina[-1]["id"]}, SEGREDO)
    yield Kiln.json({"itens": pagina, "proximo": proximo})

Kiln.get(app, "/pedidos", listar)

p1 := Kiln.test(app, "GET", "/pedidos")["body"]
pedidos.insert(0, {"id": 0})                   // chegou um novo no topo
p2 := Kiln.test(app, "GET", $"/pedidos?cursor={p1["proximo"]}")["body"]
assert p1["itens"][-1]["id"] is 10
assert p2["itens"][0]["id"] is 11                // nem repetiu, nem pulou
assert Kiln.test(app, "GET", "/pedidos?cursor=forjado")["status"] is 400''', "lang": "df"},
 {"h2": "O cabeçalho Link"},
 {"p": "O cliente não deveria montar URL de página: se a API trocar de página para cursor, todo cliente que monta URL quebra. O `Link` (RFC 8288) entrega os endereços prontos:"},
 {"code": '''adopt Arcane.Kiln as Kiln

link := Kiln.links("/pedidos?ordem=data", 2, 5)
out link
assert link.contains('</pedidos?ordem=data&pagina=3>; rel="next"')
assert link.contains('rel="prev"')''', "lang": "df"},
 {"table": {"head": ["Use", "Quando"], "rows": [
   ["`Kiln.paginar`", "lista estável, e o cliente precisa pular para a página 7"],
   ["cursor", "lista que muda, feed, rolagem infinita, exportação"],
   ["`Kiln.links`", "sempre que houver próxima página — com qualquer dos dois"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/versionamento",
"title": "Versionar uma API",
"description": "Na URL ou no cabeçalho, o que obriga a subir a versão, e como aposentar uma com Deprecation e Sunset.",
"blocos": [
 {"p": "Uma API publicada é um contrato com gente que você não conhece. O que **quebra** esse contrato: remover um campo, renomear, mudar o tipo, tornar obrigatório o que era opcional, mudar o significado de um status. O que **não** quebra: acrescentar campo na resposta, acrescentar rota, aceitar um parâmetro opcional novo."},
 {"table": {"head": ["Onde a versão mora", "A favor", "Contra"], "rows": [
   ["na URL: `/v2/pedidos`", "visível, fácil de testar no navegador, cacheável", "a URL do recurso muda"],
   ["num cabeçalho: `Api-Version: 2`", "a URL é o recurso", "invisível num link; cache precisa de `Vary`"],
   ["no tipo: `application/vnd.loja.v2+json`", "é o que a negociação faz", "o mais difícil de usar à mão"]]}},
 {"p": "Na dúvida, a URL: é a que dá menos surpresa a quem integra. E a versão velha não some de uma vez — ela avisa antes, com dois cabeçalhos padronizados:"},
 {"code": '''adopt Arcane.Kiln as Kiln

app := Kiln.app()

action v1(req):
    yield Kiln.json({"nome": "Ana Souza"}, 200, {
        "Deprecation": "@1767225600",                     // RFC 9745: desde quando
        "Sunset": "Wed, 01 Jul 2026 00:00:00 GMT",         // RFC 8594: até quando
        "Link": '</v2/clientes/1>; rel="successor-version"'})

action v2(req):
    yield Kiln.json({"nome": {"primeiro": "Ana", "ultimo": "Souza"}})

Kiln.get(app, "/v1/clientes/:id", v1)
Kiln.get(app, "/v2/clientes/:id", v2)

velha := Kiln.test(app, "GET", "/v1/clientes/1")
assert velha["headers"]["Sunset"].contains("2026")
assert Kiln.test(app, "GET", "/v2/clientes/1")["body"]["nome"]["primeiro"] is "Ana"''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Calcule, não escolha", "texto": "Para uma **biblioteca** em DataForge, a versão sai da superfície: `Abi.proxima_versao(\"1.4.2\", antes, depois)` compara os dois arquivos e diz se é 2.0.0, 1.5.0 ou 1.4.3. Ver [A próxima versão](/docs/abi/versao)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/idempotencia",
"title": "Idempotência",
"description": "A resposta se perde na rede e o cliente reenvia. Sem chave de idempotência, a cobrança acontece duas vezes.",
"blocos": [
 {"p": "`GET`, `PUT` e `DELETE` são idempotentes por definição: repetir dá o mesmo estado final. `POST` não é — cada um cria algo. E o problema real é de rede: o servidor cobrou, a resposta se perdeu, o cliente **não sabe** se deu certo, e reenvia."},
 {"p": "O cliente sozinho não resolve: ele não tem como saber. Quem resolve é o servidor, reconhecendo o reenvio por uma chave que o cliente gera **uma vez por intenção** e manda em `Idempotency-Key`:"},
 {"code": '''adopt Arcane.Kiln as Kiln

cobrancas := []
app := Kiln.app()
Kiln.use(app, Kiln.idempotente())

action cobrar(req):
    cobrancas.append(req["body"]["valor"])
    yield Kiln.json({"cobranca": len(cobrancas)}, 201)

Kiln.post(app, "/cobrancas", cobrar)

chave := {"Idempotency-Key": "pedido-77-tentativa"}
primeira := Kiln.test(app, "POST", "/cobrancas", {"valor": 50}, chave)
reenvio := Kiln.test(app, "POST", "/cobrancas", {"valor": 50}, chave)

assert len(cobrancas) is 1                        // cobrou uma vez só
assert reenvio["body"] is primeira["body"]
assert reenvio["headers"]["Idempotent-Replay"] is "true"''', "lang": "df"},
 {"list": [
   "**A chave é por intenção, não por tentativa.** Gerar uma nova a cada reenvio desliga a proteção.",
   "**Só resposta de sucesso fica guardada.** Um 500 guardado faria o reenvio devolver o erro para sempre, quando o reenvio existe justamente para tentar de novo.",
   "**Fica em memória.** Um processo reiniciado esquece as chaves, e várias réplicas não se enxergam. Para valer em produção, a chave vai para o banco — com restrição de unicidade."]},
 {"p": "Do lado de quem chama, `Arcane.Malha` já não repete `POST` sem chave: ver [Chamadas entre serviços](/docs/tecnicas/microservicos)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/autenticacao",
"title": "Autenticação numa API",
"description": "Bearer token, 401 contra 403, o middleware que falha fechado, e o token assinado do próprio Kiln.",
"blocos": [
 {"p": "Autenticar é saber **quem** pede; autorizar é saber se ele **pode**. São dois códigos diferentes, e confundi-los esconde um incidente:"},
 {"table": {"head": ["Status", "Quer dizer", "O cliente deve"], "rows": [
   ["401", "não sei quem você é (sem credencial, ou inválida)", "autenticar de novo"],
   ["403", "sei quem você é, e você não pode", "não tentar de novo — pedir permissão"]]}},
 {"code": '''adopt Arcane.Kiln as Kiln

steady SEGREDO := "troque-isto"
app := Kiln.app()

action quem_e(token):
    dados := Kiln.unsign(token, SEGREDO)
    yield void given dados is void otherwise dados["usuario"]

Kiln.use(app, Kiln.auth(quem_e))
Kiln.get(app, "/eu", lambda req: Kiln.json({"usuario": req["state"]["user"]}))
action apagar(req):
    given req["state"]["user"] is not "admin":
        yield Kiln.problema(403, "Sem permissão", "só o administrador apaga pedidos")
    yield Kiln.status(204)

Kiln.delete(app, "/pedidos/:id", apagar)

token := Kiln.sign({"usuario": "ana"}, SEGREDO)
cab := {"Authorization": $"Bearer {token}"}

assert Kiln.test(app, "GET", "/eu")["status"] is 401
assert Kiln.test(app, "GET", "/eu", void, {"Authorization": "Bearer forjado"})["status"] is 401
assert Kiln.test(app, "GET", "/eu", void, cab)["body"]["usuario"] is "ana"
assert Kiln.test(app, "DELETE", "/pedidos/1", void, cab)["status"] is 403''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O middleware falha fechado", "texto": "Se o verificador levanta ou devolve `void`, a rota **não roda**. Um middleware de autenticação que, ao falhar, deixa passar é pior que nenhum: ele dá a sensação de proteção."}},
 {"callout": {"tipo": "atencao", "titulo": "`x ?? void is void` não compara nada", "texto": "O `??` tem a precedência mais baixa da linguagem: `saldos[quem] ?? void is void` é lido como `saldos[quem] ?? (void is void)`, e o `given` nunca vê o `void`. Escreva `(saldos[quem] ?? void) is void` — o `dataforge check` avisa (`coalescencia-engole-comparacao`)."}},
 {"p": "Para autorização além de um `given` na rota — papéis, dono do recurso, negação explícita —, use [`Arcane.Politica`](/docs/seguranca/autorizacao). Para JWT de outro emissor, `Crypto.jwt_verificar`."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/limites",
"title": "Limite de taxa",
"description": "429, Retry-After e a janela deslizante — e por que o limite é por cliente, não global.",
"blocos": [
 {"p": "Sem limite, um cliente com um laço errado derruba o serviço para todos os outros. `Kiln.rate_limit(maximo, janela)` conta pedidos por IP numa janela **deslizante** e responde 429 com `Retry-After`:"},
 {"code": '''adopt Arcane.Kiln as Kiln

app := Kiln.app()
Kiln.use(app, Kiln.rate_limit(3, 60))
Kiln.get(app, "/busca", lambda req: Kiln.json({"ok": yes}))

status := [Kiln.test(app, "GET", "/busca")["status"] cycle i in range(5)]
assert status is [200, 200, 200, 429, 429]

bloqueado := Kiln.test(app, "GET", "/busca")
assert int(bloqueado["headers"]["Retry-After"]) bigger 0''', "lang": "df"},
 {"h2": "Janela deslizante, e não fixa"},
 {"p": "Com janela **fixa** de um minuto, um cliente manda 60 pedidos às 12:00:59 e mais 60 às 12:01:00 — 120 em um segundo, os dois dentro do limite. A janela deslizante olha sempre os últimos 60 segundos, e esse pico não passa."},
 {"table": {"head": ["Cliente", "Faz", "Ao receber 429"], "rows": [
   ["bem escrito", "respeita o `Retry-After`", "espera o que o servidor mandou"],
   ["com recuo exponencial", "dobra a espera a cada falha, com sorteio", "não sincroniza com os outros"],
   ["mal escrito", "repete na hora", "fica bloqueado — que é o ponto"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Atrás de um proxy, todo mundo tem o mesmo IP", "texto": "O limite é por `req[\"ip\"]`. Atrás de um nginx ou de um balanceador, esse IP é o do proxy, e um cliente abusivo bloqueia todos. Configure o proxy para passar o IP real, e limite por chave de API quando houver uma."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/contrato",
"title": "O contrato: OpenAPI",
"description": "O documento que Swagger, Postman e gerador de cliente leem — gerado das rotas, e conferido num teste.",
"blocos": [
 {"p": "`API.openapi` lê as rotas registradas e escreve o documento OpenAPI 3.1 — o formato que o Swagger UI desenha, que o Postman importa e que gera cliente em vinte linguagens. Ele sai **das rotas**, e não de um arquivo escrito à mão: um documento escrito à mão descreve a API que alguém lembrou de descrever."},
 {"code": '''adopt Arcane.Kiln as Kiln
adopt Arcane.API as API

app := Kiln.app()
Kiln.get(app, "/pedidos/:id", lambda req: Kiln.json({"id": 1}))
Kiln.post(app, "/pedidos", lambda req: Kiln.json({"id": 2}, 201))

out API.rotas(app)
doc := from_json(API.openapi(app, {"titulo": "Loja", "versao": "1.0.0"}))
assert doc["info"]["title"] is "Loja"
assert "/pedidos/{id}" in doc["paths"]            // ':id' vira '{id}'
assert "post" in doc["paths"]["/pedidos"]''', "lang": "df"},
 {"h2": "O teste de contrato"},
 {"p": "O documento é um contrato, e contrato se confere. Um teste que compara as rotas de hoje com a lista publicada falha no dia em que alguém remove uma rota sem avisar — antes do cliente descobrir em produção:"},
 {"code": '''adopt Arcane.Kiln as Kiln
adopt Arcane.API as API

app := Kiln.app()
Kiln.get(app, "/pedidos", lambda req: Kiln.json([]))
Kiln.get(app, "/pedidos/:id", lambda req: Kiln.json({}))

steady PUBLICADAS := ["GET /pedidos", "GET /pedidos/:id"]
hoje := [$"{r["method"]} {r["path"]}" cycle r in API.rotas(app)]
sumiram := [r cycle r in PUBLICADAS given r not in hoje]
assert sumiram is []''', "lang": "df"},
 {"p": "Para exportar para as ferramentas: `API.postman(app)`, `API.insomnia(app)`, `API.curl(app)` e `API.markdown(app)`. A referência completa está em [a API do site](/api), que é gerada do mesmo jeito."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/api/checklist",
"title": "Checklist de uma API",
"description": "Vinte perguntas antes de publicar — cada uma com a página que a responde.",
"blocos": [
 {"p": "Uma API pronta responde a estas perguntas. As que ficam sem resposta viram incidente ou e-mail de suporte, e quase sempre as duas coisas."},
 {"table": {"head": ["Pergunta", "Onde"], "rows": [
   ["o erro tem `type` que um programa lê?", "[Problemas](/docs/api/problemas)"],
   ["o 500 esconde a mensagem interna?", "[Problemas](/docs/api/problemas)"],
   ["o que acontece com `Accept` que você não serve?", "[Negociação](/docs/api/negociacao)"],
   ["duas edições simultâneas apagam uma à outra?", "[Pré-condições](/docs/api/precondicoes)"],
   ["a listagem tem teto de itens por página?", "[Paginação](/docs/api/paginacao)"],
   ["a listagem de algo que muda usa cursor?", "[Paginação](/docs/api/paginacao)"],
   ["remover um campo sobe a versão?", "[Versionamento](/docs/api/versionamento)"],
   ["a versão velha avisa quando vai sumir?", "[Versionamento](/docs/api/versionamento)"],
   ["um POST reenviado cobra duas vezes?", "[Idempotência](/docs/api/idempotencia)"],
   ["401 e 403 estão nos lugares certos?", "[Autenticação](/docs/api/autenticacao)"],
   ["um cliente com laço derruba os outros?", "[Limites](/docs/api/limites)"],
   ["o contrato publicado confere com as rotas?", "[Contrato](/docs/api/contrato)"],
   ["toda entrada de fora é validada?", "`Kiln.validar` — [Kiln](/docs/kiln/rotas)"],
   ["CORS libera só as origens certas?", "[Middleware](/docs/kiln/middleware)"],
   ["as rotas têm teste sem socket, e um com socket?", "[Testes de API](/docs/testes)"],
   ["duas rotas escrevem no mesmo estado sem trava?", "`dataforge check` avisa: `escrita-concorrente`"],
   ["o log tem o id do pedido?", "`Kiln.request_id` — [Observabilidade](/docs/observabilidade)"],
   ["há um SLO, e um alerta que para quando o problema passa?", "[SLO](/docs/observabilidade/slo)"],
   ["o processo termina limpo no `docker stop`?", "[Encerrar](/docs/partida/encerrar)"],
   ["há TLS na frente?", "o Kiln não tem: [Produção](/docs/kiln/producao)"]]}},
]},
]
