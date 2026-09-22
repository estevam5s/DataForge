# -*- coding: utf-8 -*-
"""A rota de testes e a de API REST."""

PAGINAS = [
{
"href": "/docs/testes",
"title": "Testes",
"description": "Tudo sobre testar em DataForge: o corredor, os matchers, dublês, propriedades, cobertura e CI.",
"blocos": [
 {"p": "Testar não é uma biblioteca que se instala: `crucible`, `trial` e `expect` são **palavras da linguagem**, e `dataforge test` já está no executável. Não há dependência, não há configuração, e o arquivo de teste é um `.df` comum."},
 {"code": """adopt Arcane.Crucible as C

action somar(a, b):
    yield a + b

crucible "soma":
    trial "soma dois numeros":
        expect somar(2, 3) is 5

    trial "aceita decimais":
        expect somar(0.5, 0.25) is 0.75

C.run()
""", "lang": "df", "title": "tests/soma_test.df"},
 {"code": """$ dataforge test tests/

✓ tests/soma_test.df (2/2)

2 passaram em 1 arquivo(s) — 0.03s
Tudo verde.
""", "lang": "bash"},

 {"h2": "O caminho inteiro"},
 {"cards": [
   {"href": "/docs/crucible", "title": "Crucible", "desc": "o corredor: crucible, trial, expect e como ele descobre os arquivos"},
   {"href": "/docs/crucible/matchers", "title": "Os matchers", "desc": "is, contains, matches, throws — e o que cada um relata ao falhar"},
   {"href": "/docs/crucible/fixtures", "title": "Fixtures e ganchos", "desc": "antes, depois, e o estado que não pode vazar entre testes"},
   {"href": "/docs/crucible/dubles", "title": "Dublês", "desc": "substituir o que é lento, caro ou de fora"},
   {"href": "/docs/crucible/propriedades", "title": "Teste por propriedade", "desc": "milhares de entradas, e a menor que quebra"},
   {"href": "/docs/crucible/relatorios", "title": "Relatórios e CI", "desc": "JUnit, cobertura mínima e o código de saída"},
   {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "os dois jeitos de o número mentir"},
   {"href": "/docs/tecnicas/instantaneos", "title": "Instantâneos", "desc": "saída grande, e banco isolado por teste"},
   {"href": "/docs/bibliotecas/testes", "title": "Testar uma biblioteca", "desc": "importar pelo nome público, e não pelo caminho"}]},

 {"h2": "A prática"},
 {"p": "A ferramenta está acima; abaixo, como se usa. Cada página tem exemplos que rodam, e é conferida a cada build."},
 {"cards": [
    {"href": "/docs/testes/tdd", "title": "TDD", "desc": "vermelho, verde, refatorar — passo a passo"},
    {"href": "/docs/testes/unitarios", "title": "Testes unitários", "desc": "preparar, agir, conferir; uma razão para falhar"},
    {"href": "/docs/testes/parametrizados", "title": "Parametrizados", "desc": "uma tabela de casos, um corpo só"},
    {"href": "/docs/testes/bdd", "title": "Cenários (BDD)", "desc": "dado, quando, então — e o passo que quebrou"},
    {"href": "/docs/testes/integracao", "title": "Integração", "desc": "o banco de verdade e a rota inteira"},
    {"href": "/docs/testes/ponta-a-ponta", "title": "Ponta a ponta", "desc": "subprocesso, código de saída, socket"},
    {"href": "/docs/testes/erros", "title": "Testar erros", "desc": "o tipo, o valor e o que não ficou pela metade"},
    {"href": "/docs/testes/regressao", "title": "Regressão", "desc": "todo bug vira teste; o instantâneo"},
    {"href": "/docs/testes/piramide", "title": "A pirâmide", "desc": "quantos de cada, e o que não testar"},
    {"href": "/docs/testes/instaveis", "title": "Testes instáveis", "desc": "as cinco causas, e por que repetir não corrige"}]},

 {"h2": "Onde os testes moram"},
 {"table": {"head": ["Padrão", "Encontrado por"], "rows": [
   ["`tests/`", "`dataforge test`"],
   ["`*_test.df` em qualquer lugar", "`dataforge test`"],
   ["`[scripts] test = …` no `forge.toml`", "`dataforge test` sem argumento"],
   ["`forge_modules/`", "**ignorado** de propósito"]]}},
 {"p": "A última linha é uma correção: um projeto com 13 testes relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca que ninguém daquele projeto escreveu."},

 {"h2": "As quatro perguntas que um teste responde"},
 {"table": {"head": ["Pergunta", "Forma"], "rows": [
   ["dá o valor certo?", "`expect f(x) is esperado`"],
   ["falha quando deve?", "`expect f(ruim) throws ValidationError`"],
   ["mudou o que não devia?", "`expect saida matches snapshot`"],
   ["vale para **qualquer** entrada?", "teste por propriedade"]]}},
 {"p": "A segunda é a mais esquecida, e a que mais rende: um código que só é testado no caminho feliz costuma ter a mensagem de erro errada — ou nenhuma."},

 {"h2": "Um teste que reprova de verdade"},
 {"callout": {"tipo": "atencao", "titulo": "\"Tudo verde\" com um trial reprovado", "texto": "Um arquivo com `crucible`/`trial` **registra** as suítes; quem as roda é `C.run()`. O corredor caía no caso \"sem ações `test_`, o próprio arquivo é o caso\" e contava o arquivo como **um teste que passou** — dez `trial` com um quebrado saíam com código 0. Um teste que falha reportando \"Tudo verde\" é a pior falha possível num corredor: a suíte fica vermelha e o CI passa."}},
 {"p": "Hoje há um resultado por **trial**, e não por arquivo: \"1 de 2 falhou\" sem dizer qual não serve para nada."},

 {"h2": "Estado entre testes"},
 {"code": """crucible "carrinho":
    setup:
        carrinho := []            // roda antes de CADA trial

    trial "comeca vazio":
        expect len(carrinho) is 0

    trial "aceita um item":
        carrinho.append("cafe")
        expect len(carrinho) is 1
""", "lang": "df"},
 {"p": "Se o segundo `trial` visse o carrinho do primeiro, a ordem dos testes passaria a importar — e um teste cuja aprovação depende da ordem não prova nada."},

 {"h2": "No CI"},
 {"code": """dataforge check .
dataforge test tests/ --cobertura --minimo=80
dataforge lint src/
dataforge fmt . --check
""", "lang": "bash"},
 {"p": "Os quatro saem com código diferente de zero quando acham algo — é o que o CI lê. E `--minimo` é o que impede a cobertura de cair devagar até virar decoração."},

 {"h2": "O que testar, e o que não"},
 {"table": {"head": ["Vale o teste", "Não vale"], "rows": [
   ["a regra de negócio", "o que a linguagem já garante"],
   ["a borda (vazio, zero, negativo, `void`)", "que um `+` soma"],
   ["o **tipo** do erro levantado", "o texto exato da mensagem"],
   ["o que já quebrou uma vez", "código que só repassa valor"],
   ["o contrato de um módulo público", "a ordem interna das chamadas"]]}},
 {"p": "A linha mais importante é a quarta: **todo bug corrigido merece um teste que falha sem a correção**. É a única forma de ele não voltar — e é a regra que este repositório segue para as centenas de correções que carrega."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/crucible", "title": "Crucible, em detalhe", "desc": "o próximo passo"},
   {"href": "/docs/cli/test", "title": "dataforge test", "desc": "as opções do comando"},
   {"href": "/docs/exercicios/25-testes-crucible", "title": "Exercícios", "desc": "praticar com casos que se verificam sozinhos"}]},
]},

{
"href": "/docs/api",
"title": "APIs: REST e RESTful",
"description": "O que REST significa de verdade, como escrever uma API em DataForge, e onde as decisões doem.",
"blocos": [
 {"p": "\"API REST\" virou sinônimo de \"JSON sobre HTTP\", e não é a mesma coisa. A diferença importa porque as regras de REST existem para resolver problemas concretos — cache, repetição, evolução — e ignorá-las custa exatamente esses três."},

 {"h2": "Os seis princípios, e o que cada um compra"},
 {"table": {"head": ["Princípio", "O que ele compra"], "rows": [
   ["**cliente-servidor**", "as duas metades evoluem separadas"],
   ["**sem estado**", "qualquer servidor atende qualquer pedido — é o que permite escalar"],
   ["**cacheável**", "a resposta diz se pode ser guardada, e por quanto tempo"],
   ["**interface uniforme**", "recursos, verbos e representações iguais em todo lugar"],
   ["**em camadas**", "proxy, cache e balanceador entram sem o cliente saber"],
   ["**código sob demanda** (opcional)", "raramente usado"]]}},
 {"callout": {"tipo": "nota", "titulo": "O que quase ninguém faz, e tudo bem", "texto": "O nível mais alto de REST pede que a resposta traga os **links** para o que fazer a seguir (HATEOAS). Quase nenhuma API pública faz isso, e a razão é honesta: o custo é alto e o ganho aparece só em sistemas muito longevos. Dizer \"nossa API é RESTful\" sem HATEOAS é o normal — e saber o que se está deixando de fora é a diferença."}},

 {"h2": "Recurso é substantivo; o verbo é do HTTP"},
 {"code": """GET    /pedidos           lista
POST   /pedidos           cria
GET    /pedidos/42        lê um
PUT    /pedidos/42        substitui inteiro
PATCH  /pedidos/42        muda parte
DELETE /pedidos/42        apaga
GET    /pedidos/42/itens  o que pertence a ele
""", "lang": "text"},
 {"p": "O erro clássico é pôr o verbo no caminho — `/criarPedido`, `/pedidoDelete`. Quando isso acontece, cada endpoint vira um caso particular, e nada do que HTTP já sabe fazer (cache, repetição segura, código de status) se aplica sozinho."},

 {"h2": "Uma API em DataForge"},
 {"code": """adopt Arcane.Database as DB

db := DB.memory()
DB.create_table(db, "pedidos", {"id": "INTEGER PRIMARY KEY",
                                "cliente": "TEXT", "total": "REAL"})

server api at "0.0.0.0" on 8000:

    route GET "/pedidos":
        pagina := int(query["pagina"] ?? "1")
        respond DB.paginate(db, "pedidos", pagina, 20)

    route GET "/pedidos/:id":
        pedido := DB.query_one(db, "SELECT * FROM pedidos WHERE id = ?",
                               [params["id"]])
        given pedido is void:
            respond 404 json {"erro": "pedido nao encontrado"}
        respond pedido

    route POST "/pedidos":
        cliente := body["cliente"] ?? ""
        given cliente is "":
            respond 400 json {"erro": "cliente e obrigatorio"}
        id := DB.insert(db, "pedidos", {"cliente": cliente,
                                        "total": body["total"] ?? 0.0})
        respond 201 json {"id": id}

    route DELETE "/pedidos/:id":
        DB.delete(db, "pedidos", {"id": params["id"]})
        respond 204 json {}

ignite api
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`query[\"x\"]` sem `??` dá 500", "texto": "A query, o corpo e os cabeçalhos vêm de fora: a chave pode não vir, e indexar um vault sem a chave é erro. `params` é a exceção — se a rota casou, o parâmetro existe."}},

 {"h2": "O código de status é parte da resposta"},
 {"table": {"head": ["Código", "Quando"], "rows": [
   ["**200**", "deu certo, e há corpo"],
   ["**201**", "criou — e o cabeçalho `Location` aponta o novo recurso"],
   ["**204**", "deu certo, e não há corpo (um `DELETE`)"],
   ["**400**", "o pedido está malformado"],
   ["**401**", "não sei quem é você"],
   ["**403**", "sei quem é você, e não pode"],
   ["**404**", "não existe"],
   ["**409**", "conflito — já existe, ou o estado mudou"],
   ["**422**", "entendi o formato, os **valores** é que não servem"],
   ["**429**", "devagar"],
   ["**500**", "o erro é meu"]]}},
 {"p": "Responder `200` com `{\"erro\": …}` dentro é o antipadrão mais comum: o cliente, o proxy e o monitoramento acham que deu certo, e só quem lê o corpo descobre que não."},

 {"h2": "Repetir sem estragar"},
 {"table": {"head": ["Verbo", "Repetir é seguro?", "Muda dado?"], "rows": [
   ["`GET`", "sim", "não"],
   ["`PUT`", "sim — o resultado final é o mesmo", "sim"],
   ["`DELETE`", "sim — apagar duas vezes é apagar", "sim"],
   ["`POST`", "**não**", "sim"]]}},
 {"p": "É por isso que um cliente que repete pedidos automaticamente **não** repete `POST` — repetir uma cobrança cobra duas vezes. Quando a repetição é necessária, a saída é a chave de idempotência:"},
 {"code": """route POST "/pedidos":
    chave := headers["Idempotency-Key"] ?? ""
    given chave isnt "":
        ja := DB.query_one(db, "SELECT * FROM pedidos WHERE chave = ?", [chave])
        given ja isnt void:
            respond 200 json ja
    // … cria, guardando a chave junto
""", "lang": "df"},
 {"p": "Quem honra a chave é **o servidor**: o cliente só consegue oferecer o meio de reconhecer a repetição."},

 {"h2": "Erros com forma"},
 {"p": "Um erro de API precisa ser processável por máquina **e** legível por pessoa. Um texto solto não é nem um nem outro:"},
 {"code": """action erro(codigo, mensagem, campos := {}):
    yield {"erro": {"codigo": codigo,
                    "mensagem": mensagem,
                    "campos": campos}}

route POST "/pedidos":
    problemas := {}
    given (body["cliente"] ?? "") is "":
        problemas["cliente"] := "obrigatorio"
    given (body["total"] ?? 0.0) <= 0.0:
        problemas["total"] := "precisa ser maior que zero"
    given len(keys(problemas)) > 0:
        respond 422 json erro("validacao", "confira os campos", problemas)
""", "lang": "df"},
 {"p": "O `codigo` é o que o cliente compara; a `mensagem` é o que a pessoa lê; os `campos` são o que o formulário marca em vermelho. Os três têm públicos diferentes."},

 {"h2": "Paginar"},
 {"code": """// por página: simples, e caro nas páginas altas
respond DB.paginate(db, "pedidos", pagina, 20)

// por cursor: cada página custa o mesmo
respond DB.query(db,
    "SELECT * FROM pedidos WHERE id > ? ORDER BY id LIMIT 20",
    [int(query["depois_de"] ?? "0")])
""", "lang": "df"},
 {"p": "`LIMIT 20 OFFSET 100000` parece constante e não é: o banco produz e descarta as cem mil primeiras linhas. Ver [complexidade em dados](/docs/big-o/dados)."},

 {"h2": "Versionar"},
 {"table": {"head": ["Forma", "Prós e contras"], "rows": [
   ["`/v1/pedidos`", "visível e simples; duplica rota na virada"],
   ["cabeçalho `Accept`", "\"mais REST\"; difícil de testar no navegador"],
   ["**não versionar, só acrescentar**", "o melhor, quando dá: campo novo não quebra ninguém"]]}},
 {"p": "A terceira linha é a que mais vale tentar primeiro. Um cliente bem escrito ignora campo que não conhece; quebrar só é inevitável quando algo **sai** ou **muda de significado**."},

 {"h2": "Segurança, no mínimo"},
 {"list": [
   "**Autenticação** — JWT com `Arcane.Crypto`, ou sessão. O middleware falha **fechado**: se ele erra, o handler não roda.",
   "**Autorização é outra coisa** — saber quem é (401) não é poder fazer (403).",
   "**Limite de taxa** — sem ele, um cliente com laço derruba o serviço.",
   "**Validar tudo o que vem de fora** — corpo, query, cabeçalho e caminho.",
   "**Nunca o erro interno no corpo** — a mensagem do banco conta a estrutura da tabela para quem perguntar."]},
 {"code": """adopt Kiln
adopt Arcane.Crypto as Cr

steady SEGREDO := "troque-isto"

// O middleware recebe o pedido. Devolver uma resposta ENCERRA a cadeia;
// devolver 'void' deixa seguir, e o que ele guardou em req["state"]
// chega na rota.
action exigir_token(token):
    dados := Cr.jwt_verificar(token, SEGREDO)
    yield dados["carga"]["usuario"] given dados["valido"] otherwise void

server api on 0:
    middleware Kiln.rate_limit(60, 60)
    middleware Kiln.auth(exigir_token)

    route GET "/eu":
        respond json {"usuario": req["state"]["user"]}
""", "lang": "df"},

 {"h2": "Documentar, e testar"},
 {"code": """adopt Arcane.API as API

API.openapi(api, {"titulo": "API de Pedidos", "versao": "1.0.0"})
""", "lang": "df"},
 {"p": "Isso publica `/openapi.json`, que Insomnia, Postman e gerador de cliente leem. E o teste de rota não precisa de socket:"},
 {"code": """adopt Arcane.Crucible as C
adopt Arcane.Kiln as Kiln

crucible "api":
    trial "GET /pedidos/999 devolve 404":
        r := Kiln.test(api, "GET", "/pedidos/999")
        expect r["status"] is 404

    trial "POST sem cliente devolve 422":
        r := Kiln.test(api, "POST", "/pedidos", {"total": 10.0})
        expect r["status"] is 422

C.run()
""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "O que o `Kiln.test` não pega", "texto": "Ele roda tudo na **mesma thread**. Bug de concorrência — e o de sessão por cookie — só aparece subindo o servidor de verdade. Tenha ao menos um teste que use socket."}},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/kiln", "title": "Kiln", "desc": "o framework web inteiro"},
   {"href": "/docs/tecnicas/api", "title": "OpenAPI, Insomnia e Postman", "desc": "documentar e importar"},
   {"href": "/docs/receitas/api-rest", "title": "Receita: API REST", "desc": "um exemplo completo, do zero"},
   {"href": "/docs/lavra", "title": "Lavra", "desc": "quando a consulta do cliente é que decide o formato"},
   {"href": "/docs/seguranca", "title": "Segurança", "desc": "o que verificar antes de publicar"}]},
]},
]
