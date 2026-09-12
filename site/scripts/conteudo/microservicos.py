# -*- coding: utf-8 -*-
"""Microserviços, OpenAPI e WebSockets."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/microservicos",
"title": "Microserviços",
"description": "O que muda quando a chamada atravessa a rede: prazo, retry seguro, disjuntor, descoberta e propagação do rastro.",
"blocos": [
 {"p": "Uma chamada de função ou funciona, ou levanta. Uma chamada de **rede** tem um terceiro estado: **não se sabe**. Ela pode ter chegado e a resposta se perdido; pode estar a caminho; pode ter sido processada duas vezes."},
 {"p": "Quase todo bug de microserviço vem de tratar o terceiro estado como um dos dois primeiros:"},
 {"table": {"head": ["O que se faz", "O que acontece"], "rows": [
   ["tentar de novo, sem cuidado", "o pedido é processado duas vezes"],
   ["esperar sem prazo", "uma thread presa por serviço, para sempre"],
   ["insistir num serviço caído", "ele nunca se recupera, porque nunca para de receber"],
   ["propagar só o dado", "o rastro se perde na primeira fronteira"]]}},
 {"p": "`Arcane.Malha` trata os quatro."},

 {"h2": "Uma chamada"},
 {"code": """adopt Arcane.Malha as Malha

cliente := Malha.cliente("https://estoque.interno", {
    "prazo": 3.0,
    "tentativas": 3,
    "disjuntor": {"falhas": 5, "espera": 30}
})

r := cliente.get("/estoque/CAF-500")

given r["ok"]:
    out r["body"]["quantidade"]
otherwise:
    out $"nao deu: {r["erro"]} (status {r["status"]})\"""", "lang": "df"},
 {"p": "A resposta é um vault com `ok`, `status`, `body`, `headers`, `tentativas`, `ms` e — quando algo deu errado — `erro`."},
 {"callout": {"tipo": "nota", "titulo": "Um erro de rede devolve vault, não levanta", "texto": "Quem chama um serviço precisa **decidir** o que fazer: seguir com um valor padrão, tentar outro, ou falhar. Um `monitor` em volta de cada chamada seria ruído — e a maioria das pessoas escreveria `handle` vazio."}},

 {"h3": "`status: 0` é o terceiro estado"},
 {"code": """status  500  →  chegou, o servidor quebrou
status  404  →  chegou, o pedido está errado
status    0  →  NÃO CHEGOU (ou a resposta se perdeu)""", "lang": "text"},
 {"p": "A diferença importa: um 500 **foi processado**, e um 0 talvez não. Para uma operação que cobra dinheiro, o 0 é o caso que exige a chave de idempotência."},

 {"h2": "Retry: só o que é seguro"},
 {"table": {"head": ["Situação", "Repete?"], "rows": [
   ["`GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`", "sim — não mudam estado, ou são idempotentes"],
   ["`POST` ou `PATCH` **sem** chave", "**não** — um pagamento repetido cobra duas vezes"],
   ["`POST` **com** `Idempotency-Key`", "sim — é o servidor que garante o efeito único"],
   ["5xx, 429, 408, 425", "sim — o problema é do outro lado"],
   ["outro 4xx", "**não** — o pedido está errado; repetir dá o mesmo erro com mais latência"],
   ["`status: 0`", "sim — não chegou, vale tentar"]]}},
 {"code": """// repetido sem risco
cliente.get("/estoque/CAF-500")

// NÃO é repetido
cliente.post("/pagamentos", {"valor": 100.0})

// repetido, porque o servidor garante
cliente.post("/pagamentos", {"valor": 100.0}, chave := uuid())""", "lang": "df"},

 {"h3": "Recuo exponencial, com tremor"},
 {"code": """tentativa 1  →  espera até 0,2 s
tentativa 2  →  espera até 0,4 s
tentativa 3  →  espera até 0,8 s
tentativa 4  →  espera até 1,6 s      (teto: 10 s)""", "lang": "text"},
 {"p": "O **tremor** não é refinamento. Sem ele, cem clientes que falharam junto tentam de novo junto — e a rajada derruba o serviço que estava se recuperando. É a diferença entre uma recuperação e um laço de queda."},
 {"callout": {"tipo": "dica", "titulo": "`Retry-After` vence o cálculo", "texto": "Quando o servidor manda o cabeçalho, ele sabe quando vai estar pronto — e ignorar isso é insistir contra quem pediu para esperar. Inclusive `Retry-After: 0`, que significa “tente agora”: tratá-lo como ausente faria o cliente esperar os segundos que o servidor acabou de dizer que não eram necessários."}},

 {"h2": "Disjuntor"},
 {"p": "Sem ele, um serviço que cai **leva os que dependem dele**: cada pedido espera o prazo inteiro antes de falhar, as threads acabam, e o que estava de pé cai também. E o serviço caído nunca se recupera, porque nunca para de receber."},
 {"code": """    fechado   ────falhas demais────▶  aberto
       ▲                                 │
       │                            espera passou
    sucesso                              │
       │                                 ▼
       └──────────────────────────  entreaberto
                                   (deixa UM passar)""", "lang": "text"},
 {"code": """cliente := Malha.cliente(base, {
    "disjuntor": {"falhas": 5, "espera": 30}
})

// depois de 5 falhas, a chamada NÃO SAI:
r := cliente.get("/x")
// {"ok": no, "status": 0, "erro": "disjuntor aberto para 'estoque'",
//  "tentativas": 0, "espera_restante": 27.4}""", "lang": "df"},
 {"p": "O **entreaberto** é o que evita a avalanche na volta: com cem threads esperando, abrir tudo de uma vez derruba o serviço no instante em que ele volta. Uma passa; se der certo, fecha; se falhar, abre de novo e o relógio **reinicia** — sem reiniciar, uma fila de threads sondaria em rajada."},
 {"callout": {"tipo": "atencao", "titulo": "4xx não abre o disjuntor", "texto": "Um 404 ou um 422 não é falha do **serviço**: o pedido está errado. Contar isso abriria o disjuntor por causa de um bug de quem chama — e aí um erro de validação derrubaria a integração inteira."}},
 {"code": """Malha.disjuntor(falhas := 3, espera := 10)   // um, avulso
cliente.disjuntor.estado                     // "fechado" | "aberto" | "entreaberto"
cliente.disjuntor.resumo()""", "lang": "df"},

 {"h2": "Descoberta"},
 {"p": "Não cravar `http://localhost:8080` no código, sem precisar de um registro distribuído:"},
 {"code": """Malha.registrar("estoque", "http://estoque:8080", {"prazo": 2.0})
Malha.registrar("pagamentos", "http://pagamentos:8080")

cliente := Malha.de("estoque")      // o MESMO cliente, sempre""", "lang": "df"},
 {"p": "Sem registro explícito, ele procura a variável de ambiente — `ESTOQUE_URL` ou `ESTOQUE_HOST` —, que é a convenção que o Docker Compose e o Kubernetes já produzem:"},
 {"code": """services:
  pedidos:
    environment:
      ESTOQUE_URL: http://estoque:8080""", "lang": "yaml"},
 {"callout": {"tipo": "nota", "titulo": "O cliente é reaproveitado", "texto": "O disjuntor e as métricas vivem **no** cliente. Um cliente novo por chamada esqueceria que o serviço está caído — o que anula o disjuntor inteiro. `Malha.de(nome)` devolve sempre o mesmo."}},
 {"p": "Quando o serviço não é conhecido, a mensagem diz o que fazer:"},
 {"code": """erro: nao sei onde esta o servico 'estoque'.
  nota: procurei no registro e na variavel ESTOQUE_URL
  dica: Malha.registrar("estoque", "http://estoque:8080"),
        ou defina ESTOQUE_URL""", "lang": "text"},

 {"h2": "O rastro do pedido"},
 {"p": "Sem um identificador que viaja com o pedido, investigar um incidente em cinco serviços é **cruzar horário de log** — o que é impossível quando dois pedidos acontecem no mesmo segundo."},
 {"code": """adopt Kiln
adopt Arcane.Malha as Malha

server pedidos on 8080:
    // Na borda: continua o rastro que chegou, ou começa um.
    middleware lambda req: Malha.propagar(req, "pedidos")

    route POST "/pedidos":
        // A chamada de saída leva o rastro sozinha.
        r := Malha.de("estoque").get($"/estoque/{req["body"]["sku"]}")
        given not r["ok"]:
            respond 503 json {"erro": "estoque indisponível"}
        respond 201 json criar(req["body"])""", "lang": "df"},
 {"p": "A propagação é **automática** na saída: um cliente que obrigasse a passar o id em cada chamada o perderia na primeira vez que alguém esquecesse — e esquecer é o caso normal."},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`Malha.propagar(req, origem)`", "continua o rastro que chegou, ou começa um"],
   ["`Malha.rastro()`", "o id de agora — para pôr no log"],
   ["`Malha.contexto()`", "o vault inteiro: rastro, origem, extra"],
   ["`Malha.comecar_contexto(id, origem, extra)`", "à mão, fora de uma rota"],
   ["`Malha.cabecalhos_de_contexto()`", "o que vai nas chamadas de saída"]]}},
 {"code": """// o 'extra' também viaja — o inquilino, a versão do cliente
Malha.comecar_contexto(void, "web", {"tenant": "acme"})
// vira X-Ctx-Tenant: acme em toda chamada de saída""", "lang": "df"},
 {"p": "O contexto vive numa `threading.local`: duas requisições ao mesmo tempo não misturam rastro. E o rastro também entra em `req[\"state\"][\"rastro\"]`, para o log do Kiln o alcançar sem passar pelo contexto."},

 {"h2": "Observar"},
 {"code": """cliente.resumo()
// {"servico": "estoque", "chamadas": 1204, "erros": 7,
//  "retentativas": 12, "recusadas": 0, "media_ms": 34.2,
//  "disjuntor": {"estado": "fechado", "falhas": 0, …}}

Malha.saude()      // o resumo de TODOS os clientes ativos""", "lang": "df"},
 {"p": "`Malha.saude()` é o que se põe numa rota de diagnóstico: ela responde *quais dependências deste serviço estão de pé*, que é a primeira pergunta num incidente."},
 {"code": """route GET "/saude/dependencias":
    respond json {"servicos": Malha.saude()}""", "lang": "df"},

 {"h2": "Um sistema em três serviços"},
 {"p": "O caminho completo, com tudo junto:"},
 {"code": """// ── pedidos/src/main.df ──
adopt Kiln
adopt Arcane.Malha as Malha
adopt Arcane.Database as Banco

db := Banco.connect("pedidos.db")

// As opções valem para todo cliente criado daqui para frente.
Malha.padrao({"prazo": 3.0, "tentativas": 3,
              "disjuntor": {"falhas": 5, "espera": 30}})

server pedidos on 8080:
    middleware lambda req: Malha.propagar(req, "pedidos")
    middleware Kiln.logger()

    route POST "/pedidos":
        item := req["body"]

        // 1. o estoque tem?
        e := Malha.de("estoque").get($"/estoque/{item["sku"]}")
        given not e["ok"]:
            respond 503 json {
                "erro": "não deu para confirmar o estoque",
                "rastro": Malha.rastro()
            }
        given e["body"]["quantidade"] smaller item["quantidade"]:
            respond 409 json {"erro": "estoque insuficiente"}

        // 2. grava o pedido e reserva, numa transação
        action corpo():
            id := Banco.insert(db, "pedidos", {
                "sku": item["sku"],
                "quantidade": item["quantidade"],
                "status": "reservando"
            })
            // A chave de idempotência é o id do pedido: se a resposta
            // se perder e o cliente repetir, o estoque não baixa duas
            // vezes.
            r := Malha.de("estoque").post("/reservas", {
                "sku": item["sku"], "quantidade": item["quantidade"]
            }, chave := $"pedido-{id}")
            given not r["ok"]:
                trigger $"reserva recusada: {r["erro"] ?? r["status"]}"
            Banco.update(db, "pedidos", {"status": "reservado"}, {"id": id})
            yield id

        monitor:
            id := Banco.transacao(db, corpo)
            respond 201 json {"id": id, "rastro": Malha.rastro()}
        handle Error as erro:
            respond 502 json {"erro": erro.message,
                              "rastro": Malha.rastro()}

    route GET "/saude":
        respond json {"estado": "ok"}

    route GET "/saude/dependencias":
        respond json {"servicos": Malha.saude()}

ignite pedidos on 8080 at "0.0.0.0\"""", "lang": "df"},
 {"p": "Quatro coisas acontecem aí que não aconteceriam com um cliente HTTP cru:"},
 {"table": {"head": ["", "O quê"], "rows": [
   ["1", "o estoque fora do ar devolve **503**, e não uma exceção que vira 500 — a diferença muda o que o balanceador faz"],
   ["2", "a reserva leva `chave := \"pedido-N\"`: se a resposta se perder e o cliente repetir, o estoque não baixa duas vezes"],
   ["3", "o pedido só fica `reservado` se a reserva **confirmou** — a transação desfaz o resto"],
   ["4", "o `rastro` volta na resposta de erro: quem recebeu o 502 pode dizer qual foi, e o log dos três serviços é pesquisável por ele"]]}},

 {"h2": "Saga: escritas que precisam acontecer juntas"},
 {"p": "Não existe transação que atravesse a rede. `BEGIN` no serviço de estoque não alcança o de cobrança, e nem deveria: um `BEGIN` distribuído pediria que cada serviço segurasse uma transação aberta esperando os outros, o que transforma a queda de um na queda de todos."},
 {"p": "A resposta correta é **compensar** — cada passo declara como se desfaz, e uma falha no meio desfaz em ordem inversa o que já aconteceu."},

 {"code": """reservar ──▶ cobrar ──▶ despachar
                            │
                          falhou
                            │
            ◀─── estornar ◀─┘
   liberar ◀───""", "lang": "text"},

 {"code": """adopt Arcane.Malha as Malha

action reservar(estado, chave):
    r := Malha.de("estoque").post("/reservas", {
        "sku": estado["sku"], "quantidade": estado["quantidade"]
    }, chave := chave)
    given not r["ok"]:
        trigger $"reserva recusada: {r["erro"] ?? r["status"]}"
    yield {"reserva": r["body"]["id"]}

action liberar(estado, chave):
    Malha.de("estoque").post($"/reservas/{estado["reserva"]}/liberar",
                             void, chave := chave)

action cobrar(estado, chave):
    r := Malha.de("cobranca").post("/cobrancas", {
        "valor": estado["valor"]
    }, chave := chave)
    given not r["ok"]:
        trigger $"cobranca recusada: {r["status"]}"
    yield {"cobranca": r["body"]["id"]}

action estornar(estado, chave):
    Malha.de("cobranca").post($"/cobrancas/{estado["cobranca"]}/estorno",
                              void, chave := chave)

// O id da saga e o do pedido: e o que torna a chave de cada passo
// estavel entre execucoes.
s := Malha.saga("checkout", $"pedido-{id}")
s.passo("reservar", reservar, liberar)
s.passo("cobrar", cobrar, estornar)
s.passo("despachar", despachar, cancelar_despacho)

// ANTES de executar: nenhum passo que escreve sem compensacao.
given s.conferir() is not []:
    trigger $"passos sem compensacao: {s.conferir()}"

r := s.executar({"sku": "CAF-500", "quantidade": 2, "valor": 65.0})

given r["ok"]:
    out $"pedido fechado em {r["ms"]}ms"
otherwise:
    out $"parou em {r["falhou_em"]}: {r["erro"]}"
    out $"desfeitos: {r["desfeitos"]}"
    given r["orfas"] is not []:
        // Isto precisa chegar a um humano.
        out $"COMPENSACAO FALHOU: {r["orfas"]}\"""", "lang": "df"},

 {"h3": "Três coisas que a diferenciam de um `monitor` com `ensure`"},
 {"table": {"head": ["", "O quê", "Por quê"], "rows": [
   ["1", "a compensação roda em **ordem inversa**", "estornar a cobrança antes de liberar o estoque deixa uma janela em que o cliente não tem dinheiro nem produto"],
   ["2", "uma compensação que falha **não é engolida**", "um estorno que não passa deixa o sistema inconsistente, e isso precisa chegar a um humano — `ok` continua `no` mesmo que o resto tenha desfeito"],
   ["3", "cada passo tem **chave de idempotência estável**", "derivada do id da saga mais o nome do passo: reprocessar uma fila não cobra duas vezes"]]}},

 {"p": "O passo que **falhou** não é compensado. Ele não concluiu, e desfazer o que não aconteceu é o outro lado do mesmo bug — um estorno de cobrança que nunca existiu devolve dinheiro que nunca foi cobrado."},

 {"callout": {"tipo": "atencao", "titulo": "A saga dá a chave; quem honra é o outro lado", "texto": "Idempotência é uma promessa que cada serviço faz por si. `Malha` põe a chave em `Idempotency-Key` e a mantém estável entre execuções, mas se o serviço de cobrança não a guardar, repetir cobra duas vezes. **O exercício 228 mostra isso acontecendo**: `cobrar` honra a chave, `reservar` não, e o estoque é debitado duas vezes enquanto a cobrança acontece uma."}},

 {"h3": "`conferir()` roda antes de executar"},
 {"p": "Um passo que escreve e não declara compensação não falha em teste feliz. Ele aparece no dia em que o passo seguinte falha — e aí já escreveu."},
 {"code": """s := Malha.saga("risco")
s.passo("consultar", consultar_score, escreve := no)
s.passo("marcar", marcar_cliente)

assert s.conferir() is ["marcar"]""", "lang": "df"},
 {"p": "`escreve := no` é a declaração de que o passo não precisa de compensação: uma leitura, um log, uma consulta de score."},

 {"h3": "O diário, e por que a cada passo"},
 {"code": """// O terceiro argumento e onde escrever cada linha.
s := Malha.saga("checkout", $"pedido-{id}",
                lambda linha: Banco.insert(db, "saga_log", linha))""", "lang": "df"},
 {"p": "Gravado a **cada passo**, e não no fim: uma queda do processo no meio da saga perderia o que já foi feito, e ninguém saberia o que compensar. Cada linha leva o `rastro` do contexto, o que liga o diário da saga ao log dos serviços que ela chamou."},
 {"p": "Um diário que não grava **não derruba a saga** — ela está no meio de escritas reais em serviços reais, e falhar por causa do log seria trocar um problema pequeno por um grande."},

 {"callout": {"tipo": "atencao", "titulo": "Saga não dá isolamento", "texto": "Entre `reservar` e `cobrar`, outro pedido vê o estoque já reservado. Uma saga troca atomicidade por disponibilidade, e essa troca é o ponto, não um defeito: quem precisa de isolamento precisa de um banco, não de microserviços."}},

 {"h2": "O que este módulo NÃO é"},
 {"p": "Ele não é um *service mesh*. Não há sidecar, não há plano de controle, não há mTLS nem roteamento por peso. Isso é trabalho de infraestrutura — Istio, Linkerd, ou o balanceador do seu provedor — e reimplementá-lo em Python daria um subconjunto pior amarrado à linguagem."},
 {"p": "O que ele é: **o que uma chamada entre serviços precisa para não mentir**, escrito sobre o `urllib` da biblioteca padrão, sem dependência."},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/tecnicas/api", "title": "OpenAPI", "meta": "do código para o contrato", "desc": "OpenAPI, Insomnia, Postman e curl, gerados das rotas."},
   {"href": "/docs/kiln/tempo-real", "title": "WebSocket e SSE", "desc": "Quando o servidor precisa falar primeiro."},
   {"href": "/docs/tecnicas/observar", "title": "Observabilidade", "desc": "Métrica, traço e linhagem."},
   {"href": "/docs/devops", "title": "DevOps", "desc": "Os artefatos que levam os serviços ao ar."},
   {"href": "/docs/exercicios/32-microservicos", "title": "Os exercícios", "meta": "227 e 228", "desc": "Dois serviços de verdade sobre sockets, e uma saga que compensa."}]},
]},
]
