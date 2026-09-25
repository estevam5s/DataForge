// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "32 · Microserviços",
  description: "2 exercícios: Arcane.Malha: retry, disjuntor, rastro e saga.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Aplicações** · Arcane.Malha: retry, disjuntor, rastro e saga · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 32`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[230](#230-chamada-entre-servicos-que-nao-mente)", "**Chamada entre servicos que nao mente**", ""], ["[231](#231-saga-nao-existe-transacao-que-atravesse-a-rede)", "**Saga: nao existe transacao que atravesse a rede**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "230 · Chamada entre servicos que nao mente"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 230 — Chamada entre servicos que nao mente
//
//  Uma chamada de acao ou funciona, ou levanta. Uma chamada de REDE
//  tem um terceiro estado: NAO SE SABE. Ela pode ter chegado e a
//  resposta se perdido; pode estar a caminho; pode ter sido
//  processada duas vezes.
//
//  Este exercicio sobe DOIS servicos de verdade e exercita os quatro
//  problemas que separam um cliente que funciona de um que parece.
// ════════════════════════════════════════════════════════════

adopt Arcane.Malha as Malha
adopt Kiln

// ── O servico de baixo: estoque ─────────────────────────────
//
// Ele se comporta mal de proposito: cada rota e um dos casos.

estoque := {"CAF-500": 20, "ACU-1KG": 50}
instavel := {"vezes": 0}
recebidos := []

server servico_estoque on 0:
    route GET "/estoque/:sku":
        recebidos.append(headers["x-request-id"] ?? "")
        sku := params["sku"]
        given sku not in estoque:
            respond 404 json {"erro": "nao existe"}
        respond json {"sku": sku, "quantidade": estoque[sku]}

    route GET "/instavel":
        // Falha duas vezes e passa na terceira — como um servico que
        // esta subindo.
        //
        // O 'check' avisa que 'instavel' e escrito numa rota e vem de
        // fora, e esta certo: o Kiln atende um pedido por thread. Aqui
        // os pedidos sao SEQUENCIAIS — o cliente espera cada resposta
        // antes da proxima —, entao nao ha duas threads na mesma
        // linha. Num servidor de verdade, 'Conc.contador()'.
        // df: permitir escrita-concorrente
        instavel["vezes"] := instavel["vezes"] + 1
        given instavel["vezes"] smaller 3:
            respond 503 json {"erro": "ainda subindo"}
        respond json {"tentativas": instavel["vezes"]}

    route GET "/quebrado":
        respond 500 json {"erro": "quebrado"}

    route POST "/reservas":
        respond 201 json {
            "reservado": yes,
            "chave": headers["idempotency-key"] ?? "",
            "rastro": headers["x-request-id"] ?? ""
        }

porta := Kiln.serve(servico_estoque, 0)

// ── 1. Descoberta: nao cravar a URL no codigo ───────────────

Malha.registrar("estoque", $"http://127.0.0.1:{porta}", {
        "prazo": 2.0,
        "tentativas": 4,
        "recuo": 0.01,
        "disjuntor": {"falhas": 3, "espera": 0.4}
    })

cliente := Malha.de("estoque")

// O MESMO cliente, sempre: o disjuntor e as metricas vivem NELE, e um
// cliente novo por chamada esqueceria que o servico esta caido.
assert Malha.de("estoque") is cliente

// ── 2. A chamada, e o vault que ela devolve ─────────────────

r := cliente.get("/estoque/CAF-500")
assert r["ok"]
assert r["status"] is 200
assert r["body"]["quantidade"] is 20
assert r["tentativas"] is 1
assert r["ms"] bigger 0

// Um erro de rede devolve VAULT, e nao levanta: quem chama um servico
// precisa decidir o que fazer, e um 'monitor' em volta de cada chamada
// seria ruido.
sumido := Malha.cliente("http://127.0.0.1:1", {"tentativas": 1}).get("/x")
assert not sumido["ok"]
assert sumido["status"] is 0  // NAO CHEGOU — o terceiro estado

// ── 3. Retry: so o que e seguro ─────────────────────────────

// Um 503 e repetido: o problema e do outro lado.
r3 := cliente.get("/instavel")
assert r3["ok"]
assert r3["tentativas"] is 3

// Um 404 NAO e repetido: o pedido esta errado, e mandar de novo da o
// mesmo erro com mais latencia.
r4 := cliente.get("/estoque/NAO-EXISTE")
assert r4["status"] is 404
assert r4["tentativas"] is 1

// ── 4. O disjuntor ──────────────────────────────────────────
//
// Sem ele, um servico que cai LEVA os que dependem dele: cada pedido
// espera o prazo inteiro antes de falhar, as threads acabam, e o que
// estava de pe cai tambem.

// Retry e disjuntor SE SOMAM, e e facil errar a conta: o disjuntor
// conta cada TENTATIVA, nao cada chamada. Com 'tentativas := 4' e
// 'falhas := 3', a PRIMEIRA chamada ja abre o disjuntor — ela sozinha
// produziu quatro falhas.
r_quebrado := cliente.get("/quebrado")
assert r_quebrado["status"] is 500
assert r_quebrado["tentativas"] is 4
assert cliente.disjuntor.estado is "aberto"
assert cliente.disjuntor.falhas bigger_eq 3

// Com o disjuntor aberto, a chamada NAO SAI.
antes := len(recebidos)
r5 := cliente.get("/estoque/CAF-500")
assert not r5["ok"]
assert r5["status"] is 0
assert r5["tentativas"] is 0
assert "disjuntor aberto" in r5["erro"]
assert len(recebidos) is antes  // nada chegou do outro lado

// Depois da espera, ele ENTREABRE — deixa UMA passar. Abrir tudo de
// uma vez derrubaria o servico no instante em que ele volta.
wait 500
assert cliente.disjuntor.estado is "entreaberto"

r6 := cliente.get("/estoque/CAF-500")
assert r6["ok"]
assert cliente.disjuntor.estado is "fechado"

// Um 4xx NAO abre o disjuntor: nao e falha do SERVICO, o pedido esta
// errado. Contar isso abriria o disjuntor por um bug de quem chama.
cycle i from 1 to 5:
    cliente.get("/estoque/NAO-EXISTE")
assert cliente.disjuntor.estado is "fechado"

// ── 5. O rastro atravessa a fronteira ───────────────────────
//
// Sem um identificador que viaja com o pedido, investigar um incidente
// em cinco servicos e cruzar horario de log — o que e impossivel
// quando dois pedidos acontecem no mesmo segundo.

Malha.comecar_contexto(void, "pedidos", {"tenant": "acme"})
meu := Malha.rastro()
assert len(meu) bigger 8

cliente.get("/estoque/CAF-500")
assert recebidos[len(recebidos) - 1] is meu

// ── 6. Idempotencia: o que torna o POST seguro de repetir ───

r7 := cliente.post("/reservas", {"sku": "CAF-500", "quantidade": 2},
    chave := $"pedido-{meu[0:8]}")
assert r7["ok"]
assert r7["body"]["chave"] is $"pedido-{meu[0:8]}"
assert r7["body"]["rastro"] is meu

Malha.terminar_contexto()

// ── 7. Propagar: a metade que falta ─────────────────────────
//
// Na BORDA, o servico continua o rastro que chegou. Sem isso, cada
// servico comeca um rastro novo e a corrente se quebra.

fingido := {"headers": {"x-request-id": "veio-de-fora",
        "x-ctx-tenant": "acme"},
    "state": {}}
Malha.propagar(fingido, "estoque")
assert Malha.rastro() is "veio-de-fora"
assert Malha.contexto()["extra"]["tenant"] is "acme"
assert fingido["state"]["rastro"] is "veio-de-fora"
Malha.terminar_contexto()

// ── 8. Observar ─────────────────────────────────────────────

resumo := cliente.resumo()
assert resumo["servico"] is "estoque"
assert resumo["chamadas"] bigger 5
assert resumo["recusadas"] is 1  // so a r5: as 404 nao contam
assert resumo["disjuntor"]["estado"] is "fechado"

// E o que um incidente pergunta primeiro: quais dependencias deste
// servico estao de pe?
saude := Malha.saude()
assert len(saude) bigger_eq 1

Kiln.stop(servico_estoque)
out "227 ok — malha"`, lang: 'df', title: `exercicios/32-microservicos/230_malha.df` },
  {"h3": "O terceiro estado"},
  {"p": "Uma chamada de ação tem dois desfechos: devolve, ou levanta. Uma chamada de **rede** tem três, e o terceiro é o que quebra sistemas:"},
  {"table": {"head": ["Desfecho", "Como se vê"], "rows": [["funcionou", "`ok` é `yes`, `status` 2xx"], ["falhou, e se sabe", "`ok` é `no`, `status` 4xx/5xx"], ["**não se sabe**", "`ok` é `no`, `status` **0**"]]}},
  {"p": "O `status 0` é o caso honesto: o pedido pode ter chegado e a resposta ter se perdido; pode estar a caminho ainda; pode ter sido processado duas vezes. Um cliente que colapsa esse caso em \"falhou\" faz o programa acima dele repetir uma cobrança."},
  {"p": "É por isso que `Malha` devolve um **vault** em vez de levantar. Quem chama um serviço precisa decidir o que fazer com cada um dos três, e um `monitor` em volta de cada chamada não distinguiria os dois últimos."},
  {"h3": "Por que um cliente por serviço, e não por chamada"},
  { code: `Malha.registrar("estoque", "http://estoque:8080", {…})
cliente := Malha.de("estoque")
assert Malha.de("estoque") is cliente     // o MESMO objeto`, lang: 'df' },
  {"p": "O disjuntor e as métricas vivem **no cliente**. Um cliente novo a cada chamada esqueceria que o serviço está caído — o que é exatamente a informação que impede a avalanche."},
  {"h3": "Retry: só o que é seguro"},
  {"p": "`Malha` repete por dois critérios, e os dois importam:"},
  {"table": {"head": ["Repete", "Não repete"], "rows": [["`status 0` (não chegou)", "4xx — o pedido está errado, repetir dá o mesmo erro com mais latência"], ["502, 503, 504", "400, 401, 403, 404, 422"], ["429, respeitando `Retry-After`", "500 sem `Retry-After`? **repete** — pode ser transitório"], ["GET, HEAD, PUT, DELETE (idempotentes)", "POST e PATCH, **a menos que** venha `chave :=`"]]}},
  {"p": "A última linha é a regra que separa um cliente correto de um perigoso. `POST /cobrancas` repetido cobra duas vezes. Com `chave := \"pedido-8f2a\"` o servidor tem como reconhecer o pedido repetido, e só então repetir é seguro:"},
  { code: `cliente.post("/reservas", {"sku": "CAF-500"}, chave := "pedido-8f2a")`, lang: 'df' },
  {"p": "A chave viaja em `Idempotency-Key`. **Quem garante a idempotência é o servidor**, não o cliente — a chave só dá a ele o meio."},
  {"h3": "O disjuntor, e a conta que engana"},
  { code: `    fechado   ────falhas demais────▶  aberto
       ▲                               │
       │                          espera passou
    sucesso                            │
       │                               ▼
       └──────────────────────  entreaberto
                                (deixa UM passar)`, lang: 'text' },
  {"p": "Sem disjuntor, um serviço que cai **leva** os que dependem dele: cada pedido espera o prazo inteiro antes de falhar, as threads acabam, e o que estava de pé cai também. E o serviço caído nunca se recupera, porque nunca para de receber."},
  {"p": "O `entreaberto` existe para a volta: com cem threads esperando, abrir tudo de uma vez derruba o serviço no instante em que ele volta."},
  {"p": "**A conta que engana** — o disjuntor conta cada **tentativa**, não cada chamada:"},
  { code: `cliente := Malha.cliente(base, {"tentativas": 4, "disjuntor": {"falhas": 3}})
r := cliente.get("/quebrado")
assert r["tentativas"] is 4
assert cliente.disjuntor.estado is "aberto"   // a PRIMEIRA chamada abriu`, lang: 'df' },
  {"p": "Quatro tentativas contra um limite de três: uma chamada só já abre. Ao calibrar, o limite precisa ser lido como \"tentativas até desistir\", e `cliente.disjuntor.falhas` mostra o número de verdade."},
  {"p": "**Um 4xx não abre o disjuntor.** Não é falha do serviço — o pedido está errado. Contar isso abriria o disjuntor por um bug de quem chama, e derrubaria uma dependência sadia."},
  {"h3": "O rastro atravessa a fronteira"},
  {"p": "Sem um identificador que viaja com o pedido, investigar um incidente em cinco serviços é cruzar horário de log — o que é impossível quando dois pedidos acontecem no mesmo segundo."},
  { code: `Malha.comecar_contexto(void, "pedidos", {"tenant": "acme"})
cliente.get("/estoque/CAF-500")    // vai com 'X-Request-Id' e 'X-Ctx-Tenant'
Malha.terminar_contexto()`, lang: 'df' },
  {"p": "A metade que se esquece é a **borda**: o serviço que recebe precisa *continuar* o rastro que chegou, e não começar um novo."},
  { code: `action continuar_rastro(req):
    Malha.propagar(req, "estoque")

server api on 8080:
    middleware continuar_rastro

    route GET "/itens":
        respond json buscar()`, lang: 'df' },
  {"p": "O `middleware` do Kiln recebe uma **expressão** — a ação que roda antes de cada rota —, e não um bloco. Um middleware que devolve `void` deixa o pedido seguir, que é o que se quer aqui: `propagar` não responde nada, só continua o rastro."},
  {"p": "Sem isso, cada serviço inicia um rastro próprio e a corrente se quebra exatamente no ponto onde ela serviria."},
  {"h3": "Qual o próximo problema"},
  {"p": "Este exercício cobre o cliente. O que ele **não** resolve está em `228`: duas escritas em serviços diferentes que precisam acontecer juntas — e não podem, porque não há transação que atravesse a rede."},
  {"h2": "231 · Saga: nao existe transacao que atravesse a rede"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 231 — Saga: nao existe transacao que atravesse a rede
//
//  'BEGIN' no servico de estoque nao alcanca o de cobranca. Se o
//  pedido reserva o produto e a cobranca falha, o produto fica preso
//  para sempre — e nao ha 'rollback' que chegue la.
//
//  A unica resposta correta e COMPENSAR: cada passo declara como se
//  desfaz, e uma falha no meio desfaz em ordem inversa o que ja
//  aconteceu.
// ════════════════════════════════════════════════════════════

adopt Arcane.Malha as Malha

// ── Os "servicos", com o estado que eles guardam ────────────

estoque := {"CAF-500": 10}
reservas := {}
cobrancas := {}
despachos := []
chaves_vistas := {}

action reservar(estado, chave):
    sku := estado["sku"]
    given estoque[sku] smaller estado["quantidade"]:
        trigger $"estoque insuficiente de {sku}"
    estoque[sku] := estoque[sku] - estado["quantidade"]
    reservas[chave] := estado["quantidade"]
    yield {"reserva": chave}

action liberar(estado, chave):
    given chave in reservas:
        estoque[estado["sku"]] := estoque[estado["sku"]] + reservas[chave]
        reservas.delete(chave)

action cobrar(estado, chave):
    // A chave de idempotencia faz o trabalho aqui: repetir a saga
    // depois de uma queda NAO cobra duas vezes.
    given chave in chaves_vistas:
        yield {"cobranca": chaves_vistas[chave], "repetida": yes}
    valor := estado["quantidade"] * 32.5
    given valor bigger estado["limite"]:
        trigger $"limite excedido: {valor} bigger {estado['limite']}"
    cobrancas[chave] := valor
    chaves_vistas[chave] := valor
    yield {"cobranca": valor}

action estornar(_estado, chave):
    given chave in cobrancas:
        cobrancas.delete(chave)
        chaves_vistas.delete(chave)

action despachar(estado, chave):
    despachos.append({"sku": estado["sku"], "chave": chave})
    yield {"despacho": len(despachos)}

action cancelar_despacho(_estado, _chave):
    despachos.clear()

// ── 1. O caminho feliz ──────────────────────────────────────

s := Malha.saga("checkout")
s.passo("reservar", reservar, liberar)
s.passo("cobrar", cobrar, estornar)
s.passo("despachar", despachar, cancelar_despacho)

// ANTES de rodar: nenhum passo que escreve pode ficar sem compensacao.
// Um passo assim nao falha em teste feliz — ele so aparece no dia em
// que o passo seguinte falha, e ai ja escreveu.
assert s.conferir() is []

r := s.executar({"sku": "CAF-500", "quantidade": 2, "limite": 100.0})

assert r["ok"]
assert r["concluidos"] is ["reservar", "cobrar", "despachar"]
assert r["desfeitos"] is []
assert r["orfas"] is []
assert estoque["CAF-500"] is 8
assert len(cobrancas) is 1
assert len(despachos) is 1

// O estado ATRAVESSA os passos: 'cobrar' viu o que 'reservar' devolveu.
assert r["estado"]["cobranca"] is 65.0
assert "reserva" in r["estado"]

// ── 2. A falha no meio, e a ordem do desfazimento ───────────

estoque := {"CAF-500": 10}
reservas := {}
cobrancas := {}
chaves_vistas := {}
despachos := []
ordem := []

action reservar2(estado, chave):
    estoque["CAF-500"] := estoque["CAF-500"] - estado["quantidade"]
    reservas[chave] := estado["quantidade"]
    yield void

action liberar2(_estado, chave):
    ordem.append("liberar")
    estoque["CAF-500"] := estoque["CAF-500"] + reservas[chave]
    reservas.delete(chave)

action cobrar2(_estado, chave):
    cobrancas[chave] := 99.0
    yield void

action estornar2(_estado, chave):
    ordem.append("estornar")
    cobrancas.delete(chave)

action despachar2(_estado, _chave):
    trigger "transportadora fora do ar"

s2 := Malha.saga("checkout")
s2.passo("reservar", reservar2, liberar2)
s2.passo("cobrar", cobrar2, estornar2)
s2.passo("despachar", despachar2, cancelar_despacho)

r2 := s2.executar({"sku": "CAF-500", "quantidade": 3})

// Ela NAO levanta: levantar perderia a informacao de quanto conseguiu
// desfazer, que e exatamente o que se precisa saber.
assert not r2["ok"]
assert r2["falhou_em"] is "despachar"
assert "transportadora" in r2["erro"]

// Ordem INVERSA. Estornar a cobranca antes de liberar o estoque
// deixaria uma janela em que o cliente nao tem dinheiro nem produto.
assert r2["desfeitos"] is ["cobrar", "reservar"]
assert ordem is ["estornar", "liberar"]

// E o mundo voltou ao que era.
assert estoque["CAF-500"] is 10
assert len(reservas) is 0
assert len(cobrancas) is 0
assert len(despachos) is 0

// O passo que FALHOU nao e compensado: ele nao concluiu, e desfazer o
// que nao aconteceu e o outro lado do mesmo bug.
assert "despachar" not in r2["desfeitos"]

// ── 3. Uma compensacao que falha nao pode ser engolida ──────
//
// Um estorno que nao passa deixa o sistema inconsistente, e isso
// precisa chegar a um humano.

action estornar_quebrado(_estado, _chave):
    trigger "gateway recusou o estorno"

liberou := {"sim": no}

action liberar3(_estado, _chave):
    liberou["sim"] := yes

s3 := Malha.saga("checkout")
s3.passo("reservar", reservar2, liberar3)
s3.passo("cobrar", cobrar2, estornar_quebrado)
s3.passo("despachar", despachar2, cancelar_despacho)

r3 := s3.executar({"sku": "CAF-500", "quantidade": 1})

assert not r3["ok"]
assert len(r3["orfas"]) is 1
assert r3["orfas"][0]["passo"] is "cobrar"
assert "gateway" in r3["orfas"][0]["erro"]

// A compensacao seguinte AINDA rodou: o estoque preso por um estorno
// que nao passou seria um segundo problema criado pelo primeiro.
assert liberou["sim"]
assert r3["desfeitos"] is ["reservar"]

// ── 4. Idempotencia: repetir a saga nao cobra duas vezes ────
//
// Uma saga que cai no meio precisa poder ser repetida. Sem chave
// estavel, repetir cobra de novo.

estoque := {"CAF-500": 10}
reservas := {}
cobrancas := {}
chaves_vistas := {}
despachos := []

// O MESMO identificador — e o que torna a chave de cada passo estavel
// entre execucoes.
acao := "pedido-4711"

s4 := Malha.saga("checkout", acao)
s4.passo("reservar", reservar, liberar)
s4.passo("cobrar", cobrar, estornar)

assert s4.chave_de("cobrar") is "pedido-4711:cobrar"

a := s4.executar({"sku": "CAF-500", "quantidade": 2, "limite": 100.0})
assert a["ok"]
assert len(cobrancas) is 1

// Repete a saga inteira, como faria quem reprocessa uma fila.
s5 := Malha.saga("checkout", acao)
s5.passo("reservar", reservar, liberar)
s5.passo("cobrar", cobrar, estornar)
b := s5.executar({"sku": "CAF-500", "quantidade": 2, "limite": 100.0})

assert b["ok"]
assert b["estado"]["repetida"]  // 'cobrar' reconheceu a chave
assert len(cobrancas) is 1  // NAO cobrou duas vezes

// A reserva, porem, aconteceu DE NOVO — ela e indexada pela mesma
// chave, mas o estoque foi debitado duas vezes. Idempotencia e uma
// promessa que cada servico faz por si: a saga da a chave, quem honra
// e o outro lado.
assert estoque["CAF-500"] is 6

// ── 5. O passo que escreve sem compensacao ──────────────────

s6 := Malha.saga("risco")
s6.passo("consultar", lambda e, c: {"score": 700}, escreve := no)
s6.passo("marcar", lambda e, c: void)

// 'consultar' e uma leitura e declara isso; 'marcar' escreve e nao
// disse como se desfaz.
assert s6.conferir() is ["marcar"]

// ── 6. O diario: onde isso parou ────────────────────────────

linhas := []

s7 := Malha.saga("checkout", "p-1", lambda linha: linhas.append(linha))
s7.passo("reservar", reservar2, liberar2)
s7.passo("cobrar", cobrar2, estornar2)
s7.passo("despachar", despachar2, cancelar_despacho)
s7.executar({"sku": "CAF-500", "quantidade": 1})

situacoes := [linha["situacao"] cycle linha in linhas]
assert situacoes is ["feito", "feito", "falhou", "desfeito", "desfeito"]
assert linhas[0]["passo"] is "reservar"
assert linhas[2]["passo"] is "despachar"

// O diario e gravado a CADA passo, e nao no fim: uma queda do processo
// no meio da saga perderia o que ja foi feito, e ninguem saberia o que
// compensar.
assert len(linhas) is len(s7.diario)

out "228 ok — saga"`, lang: 'df', title: `exercicios/32-microservicos/231_saga.df` },
  {"h3": "O problema, em uma frase"},
  {"p": "`BEGIN` no serviço de estoque não alcança o de cobrança."},
  { code: `  serviço de estoque          serviço de cobrança
  ┌──────────────────┐        ┌──────────────────┐
  │ BEGIN            │        │                  │
  │   reserva -2     │        │                  │
  │ COMMIT           │        │                  │
  └──────────────────┘        └──────────────────┘
          │                            │
          └──────── e agora? ──────────┘`, lang: 'text' },
  {"p": "Se a reserva passou e a cobrança falhou, o produto fica preso. Não há `rollback` que chegue ao outro banco — e nem deveria: um `BEGIN` distribuído pediria que cada serviço segurasse uma transação aberta esperando os outros, o que transforma a queda de um na queda de todos."},
  {"p": "A resposta correta é **compensar**: cada passo declara como se desfaz."},
  {"h3": "O desenho"},
  { code: `s := Malha.saga("checkout")
s.passo("reservar", reservar, liberar)
s.passo("cobrar",   cobrar,   estornar)
s.passo("despachar", despachar, cancelar_despacho)

r := s.executar({"sku": "CAF-500", "quantidade": 2, "limite": 100.0})`, lang: 'df' },
  { code: `reservar ──▶ cobrar ──▶ despachar
                            │
                          falhou
                            │
            ◀─── estornar ◀─┘
   liberar ◀───`, lang: 'text' },
  {"p": "Cada passo recebe **dois** argumentos: o estado acumulado da saga e a chave de idempotência daquele passo."},
  { code: `action reservar(estado, chave):
    estoque[estado["sku"]] := estoque[estado["sku"]] - estado["quantidade"]
    reservas[chave] := estado["quantidade"]
    yield {"reserva": chave}        // o vault entra no estado`, lang: 'df' },
  {"p": "Um passo que devolve vault **funde** o resultado no estado — é assim que `cobrar` lê o que `reservar` produziu. Um passo que não precisa de um dos argumentos escreve `_estado` ou `_chave`; o linter cobra isso, e com razão: a assinatura é fixa, e o `_` é a declaração de que a omissão é deliberada."},
  {"h3": "Três coisas que a diferenciam de um `monitor` com `ensure`"},
  {"p": "**1. A compensação roda em ordem inversa**"},
  { code: `assert r2["desfeitos"] is ["cobrar", "reservar"]`, lang: 'df' },
  {"p": "Não é detalhe estético. Estornar a cobrança **antes** de liberar o estoque deixa uma janela em que o cliente não tem dinheiro nem produto. A ordem inversa é a única que mantém o sistema num estado defensável em cada instante do desfazimento."},
  {"p": "**O passo que falhou não é compensado.** Ele não concluiu, e desfazer o que não aconteceu é o outro lado do mesmo bug — um estorno de cobrança que nunca existiu devolve dinheiro que nunca foi cobrado."},
  {"p": "**2. Uma compensação que falha não é engolida**"},
  { code: `assert len(r3["orfas"]) is 1
assert r3["orfas"][0]["passo"] is "cobrar"`, lang: 'df' },
  {"p": "Um estorno que não passa deixa o sistema inconsistente, e isso precisa chegar a um humano. `ok` continua `no` mesmo que o resto tenha desfeito."},
  {"p": "E as compensações **seguintes ainda rodam**: o estoque preso por um estorno que não passou seria um segundo problema criado pelo primeiro."},
  {"p": "**3. Cada passo tem chave de idempotência estável**"},
  { code: `s4 := Malha.saga("checkout", "pedido-4711")
assert s4.chave_de("cobrar") is "pedido-4711:cobrar"`, lang: 'df' },
  {"p": "Derivada do id da saga mais o nome do passo — **estável entre execuções**. É o que permite reprocessar uma fila: a saga roda de novo, `cobrar` reconhece a chave e não cobra duas vezes."},
  { code: `action cobrar(estado, chave):
    given chave in chaves_vistas:
        yield {"cobranca": chaves_vistas[chave], "repetida": yes}
    …`, lang: 'df' },
  {"p": "**A saga dá a chave; quem honra é o outro lado.** No exercício, `cobrar` honra e `reservar` não — e o resultado é visível:"},
  { code: `assert len(cobrancas) is 1       // cobrou uma vez
assert estoque["CAF-500"] is 6   // mas debitou DUAS`, lang: 'df' },
  {"p": "Idempotência é uma promessa que cada serviço faz por si. A saga não pode fabricá-la."},
  {"h3": "`conferir()` — antes de executar"},
  { code: `s6 := Malha.saga("risco")
s6.passo("consultar", lambda e, c: {"score": 700}, escreve := no)
s6.passo("marcar", lambda e, c: void)
assert s6.conferir() is ["marcar"]`, lang: 'df' },
  {"p": "Um passo que escreve e não declara compensação não falha em teste feliz. Ele aparece no dia em que o passo seguinte falha — e aí já escreveu. `conferir()` devolve a lista antes de rodar."},
  {"p": "`escreve := no` é a declaração de que o passo não precisa de compensação: uma leitura, um log, uma consulta de score."},
  {"h3": "O diário, e por que a cada passo"},
  { code: `s7 := Malha.saga("checkout", "p-1", lambda linha: linhas.append(linha))
…
assert situacoes is ["feito", "feito", "falhou", "desfeito", "desfeito"]`, lang: 'df' },
  {"p": "O terceiro argumento é onde escrever cada linha — um arquivo, uma tabela, o `Arcane.Logging`. Gravado a **cada passo**, e não no fim: uma queda do processo no meio da saga perderia o que já foi feito, e ninguém saberia o que compensar. Cada linha leva o `rastro` do contexto (exercício 227), o que liga o diário da saga ao log dos serviços que ela chamou."},
  {"p": "Um diário que não grava **não derruba a saga** — ela está no meio de escritas reais em serviços reais, e falhar por causa do log seria trocar um problema pequeno por um grande."},
  {"h3": "O que a saga não faz"},
  {"p": "**Não há isolamento.** Entre `reservar` e `cobrar`, outro pedido vê o estoque já reservado. Uma saga troca atomicidade por disponibilidade, e essa troca é o ponto, não um defeito: quem precisa de isolamento precisa de um banco (módulo 29), não de microserviços."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/32-microservicos/230_malha.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '230-chamada-entre-servicos-que-nao-mente', text: "230 · Chamada entre servicos que nao mente", level: 2 as const }, { id: 'o-terceiro-estado', text: "O terceiro estado", level: 3 as const }, { id: 'por-que-um-cliente-por-servico-e-nao-por-chamada', text: "Por que um cliente por serviço, e não por chamada", level: 3 as const }, { id: 'retry-so-o-que-e-seguro', text: "Retry: só o que é seguro", level: 3 as const }, { id: 'o-disjuntor-e-a-conta-que-engana', text: "O disjuntor, e a conta que engana", level: 3 as const }, { id: 'o-rastro-atravessa-a-fronteira', text: "O rastro atravessa a fronteira", level: 3 as const }, { id: 'qual-o-proximo-problema', text: "Qual o próximo problema", level: 3 as const }, { id: '231-saga-nao-existe-transacao-que-atravesse-a-rede', text: "231 · Saga: nao existe transacao que atravesse a rede", level: 2 as const }, { id: 'o-problema-em-uma-frase', text: "O problema, em uma frase", level: 3 as const }, { id: 'o-desenho', text: "O desenho", level: 3 as const }, { id: 'tres-coisas-que-a-diferenciam-de-um-monitor-com-ensure', text: "Três coisas que a diferenciam de um `monitor` com `ensure`", level: 3 as const }, { id: 'conferir-antes-de-executar', text: "`conferir()` — antes de executar", level: 3 as const }, { id: 'o-diario-e-por-que-a-cada-passo', text: "O diário, e por que a cada passo", level: 3 as const }, { id: 'o-que-a-saga-nao-faz', text: "O que a saga não faz", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"32 · Microserviços"}
      description={"2 exercícios: Arcane.Malha: retry, disjuntor, rastro e saga."}
      href={"/docs/exercicios/32-microservicos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
