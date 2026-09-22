# -*- coding: utf-8 -*-
"""Domínio — nove páginas: fonte de eventos, concorrência otimista,
projeções, CQRS, processos, serviços, anticorrupção, testes e modelagem.

As peças `D.armazem`, `D.reconstituir` e `D.projecao` e o erro
`AggregateVersionError` (DF1610) entraram nesta leva. Todo bloco roda.
"""

_CONTA = '''adopt Arcane.Dominio as D

// evoluir: o estado depois de um fato. Pura, e nunca recusa nada.
aplicar := {
    "ContaAberta": lambda s, d: {"titular": d["titular"], "saldo": 0, "aberta": yes},
    "Depositado": lambda s, d: {...s, "saldo": s["saldo"] + d["valor"]},
    "Sacado": lambda s, d: {...s, "saldo": s["saldo"] - d["valor"]},
    "ContaEncerrada": lambda s, d: {...s, "aberta": no}
}

// decidir: os fatos que um comando produz — ou o motivo da recusa.
action decidir(estado, comando):
    tipo := comando["tipo"]
    given tipo is "abrir":
        yield [{"nome": "ContaAberta", "dados": {"titular": comando["titular"]}}]
    given not (estado["aberta"] ?? no):
        trigger "a conta não está aberta"
    given tipo is "depositar":
        yield [{"nome": "Depositado", "dados": {"valor": comando["valor"]}}]
    given tipo is "sacar":
        given comando["valor"] bigger estado["saldo"]:
            trigger $"saldo {estado["saldo"]} não cobre {comando["valor"]}"
        yield [{"nome": "Sacado", "dados": {"valor": comando["valor"]}}]
    trigger $"comando desconhecido: {tipo}"
'''

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/fonte-de-eventos",
"title": "Fonte de eventos",
"description": "O estado não é guardado: é derivado dos fatos. O armazém, as duas funções puras e o que isso compra.",
"blocos": [
 {"p": "Num modelo comum, a tabela guarda o **estado de agora**: o saldo é 70. Numa fonte de eventos, guarda-se **o que aconteceu** — aberta, depositou 100, sacou 30 — e o saldo é uma conta feita sobre isso. A pergunta \"qual era o saldo em março?\" passa a ter resposta, e \"por que o saldo é 70?\" também."},
 {"p": "O modelo inteiro cabe em duas funções **puras**:"},
 {"table": {"head": ["Função", "Recebe", "Devolve", "Pode recusar?"], "rows": [
   ["`decidir`", "o estado e um comando", "os eventos que ele produz", "**sim** — é aqui que mora a regra"],
   ["`aplicar`", "o estado e um evento", "o estado seguinte", "**nunca** — o fato já aconteceu"]]}},
 {"code": _CONTA + '''
armazem := D.armazem()

action executar(conta, comando):
    historia := armazem.ler(conta)
    estado := D.reconstituir(historia, aplicar)
    novos := decidir(estado, comando)
    armazem.anexar(conta, novos, len(historia))
    yield D.reconstituir(historia + novos, aplicar)

executar("conta-1", {"tipo": "abrir", "titular": "Ana"})
executar("conta-1", {"tipo": "depositar", "valor": 100})
final := executar("conta-1", {"tipo": "sacar", "valor": 30})
assert final["saldo"] is 70

// a história inteira continua ali
assert [e["nome"] cycle e in armazem.ler("conta-1")] is ["ContaAberta", "Depositado", "Sacado"]

// e o passado tem resposta: o saldo depois do segundo fato
assert D.reconstituir(armazem.ler("conta-1")[0:2], aplicar)["saldo"] is 100''', "lang": "df"},
 {"h2": "Por que `aplicar` nunca recusa"},
 {"p": "Um evento é um fato no passado. Se `aplicar` pudesse recusar `Sacado`, reconstituir uma conta antiga falharia no dia em que a regra de saque mudasse — e o histórico, que é a fonte da verdade, deixaria de ser legível. A regra vive em `decidir`, que só olha o **presente**."},
 {"callout": {"tipo": "atencao", "titulo": "`reconstituir` é estrito", "texto": "Um evento sem aplicador é **erro** (`EventError`). Ignorá-lo chegaria a um estado que a conta nunca teve. A [projeção](/docs/dominio/projecoes), ao contrário, ignora de propósito o que não lhe interessa."}},
 {"table": {"head": ["Compra", "Custa"], "rows": [
   ["auditoria completa, de graça", "reconstituir a cada comando (ou um instantâneo)"],
   ["responder sobre o passado", "evento nunca muda: um erro vira um evento de correção"],
   ["novos modelos de leitura a partir do histórico", "projeções a manter"],
   ["depurar reproduzindo a sequência exata", "um armazém que nunca apaga"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/concorrencia-otimista",
"title": "Concorrência otimista",
"description": "Dois comandos decididos sobre a mesma versão: um grava, o outro recebe AggregateVersionError — e tenta de novo.",
"blocos": [
 {"p": "Dois saques de 60 chegam juntos numa conta com saldo 100. Os dois leem saldo 100, os dois decidem que podem, os dois gravam — e a conta fica com −20, embora `decidir` recuse saldo insuficiente. A regra estava certa; o problema é que as duas decisões foram tomadas sobre **o mesmo estado**."},
 {"p": "`anexar(fluxo, eventos, versao_esperada)` fecha isso: grava só se o fluxo ainda está na versão que foi lida. O segundo recebe `AggregateVersionError`, relê, e decide de novo — agora vendo o saldo 40."},
 {"code": _CONTA + '''
armazem := D.armazem()
armazem.anexar("c", [{"nome": "ContaAberta", "dados": {"titular": "Ana"}},
                     {"nome": "Depositado", "dados": {"valor": 100}}])

// os dois leram a MESMA versão
lido := armazem.versao("c")
estado := D.reconstituir(armazem.ler("c"), aplicar)
saque_a := decidir(estado, {"tipo": "sacar", "valor": 60})
saque_b := decidir(estado, {"tipo": "sacar", "valor": 60})

armazem.anexar("c", saque_a, lido)             // o primeiro grava
recusado := no
monitor:
    armazem.anexar("c", saque_b, lido)         // o segundo, não
handle AggregateVersionError:
    recusado := yes
assert recusado
assert D.reconstituir(armazem.ler("c"), aplicar)["saldo"] is 40''', "lang": "df"},
 {"h2": "Tentar de novo — com teto"},
 {"code": _CONTA + '''
armazem := D.armazem()
armazem.anexar("c", [{"nome": "ContaAberta", "dados": {"titular": "Ana"}}])

action com_retentativa(conta, comando, tentativas := 3):
    cycle i from 1 to tentativas:
        historia := armazem.ler(conta)
        novos := decidir(D.reconstituir(historia, aplicar), comando)
        monitor:
            yield armazem.anexar(conta, novos, len(historia))
        handle AggregateVersionError:
            skip
    trigger $"'{conta}' mudou {tentativas} vezes seguidas; desisti"

assert com_retentativa("c", {"tipo": "depositar", "valor": 10}) is 2''', "lang": "df"},
 {"list": [
   "**Releia e decida de novo.** Regravar os mesmos eventos ignoraria o que mudou — é exatamente o erro que o conflito existe para impedir.",
   "**Tenha teto.** Um fluxo disputado demais é sinal de agregado grande demais; retentar para sempre esconde isso.",
   "**Otimista, porque conflito é raro.** Travar a conta a cada leitura seria pagar sempre por algo que quase nunca acontece."]},
 {"p": "É o mesmo mecanismo do `If-Match` numa API: ver [Edição concorrente](/docs/api/precondicoes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/projecoes",
"title": "Projeções",
"description": "Modelos de leitura montados dos eventos: idempotentes, reconstruíveis, e cada um do tamanho da sua pergunta.",
"blocos": [
 {"p": "Reconstituir o agregado responde a perguntas sobre **uma** conta. \"Quanto entrou hoje em todas as contas?\" exigiria reconstituir todas. A projeção é a resposta pronta: um estado pequeno, atualizado a cada evento que interessa a ela, e que ignora o resto."},
 {"code": '''adopt Arcane.Dominio as D

armazem := D.armazem()
depositos := D.projecao({
    "Depositado": lambda s, d: {"total": s["total"] + d["valor"], "quantos": s["quantos"] + 1}
}, {"total": 0, "quantos": 0})
armazem.assinar(depositos.aplicar)

armazem.anexar("a", [{"nome": "ContaAberta", "dados": {}}, {"nome": "Depositado", "dados": {"valor": 50}}])
armazem.anexar("b", [{"nome": "Depositado", "dados": {"valor": 30}}])

assert depositos.estado() is {"total": 80, "quantos": 2}   // ContaAberta foi ignorado''', "lang": "df"},
 {"h2": "Idempotente pela posição"},
 {"p": "Todo registro do armazém tem uma `posicao` global. A projeção guarda a última aplicada e **não conta de novo** o que já viu — e reentrega acontece: na recuperação de uma falha, ao reler o histórico, ao receber o mesmo evento de dois caminhos."},
 {"code": '''adopt Arcane.Dominio as D

armazem := D.armazem()
armazem.anexar("a", [{"nome": "Depositado", "dados": {"valor": 50}}])
p := D.projecao({"Depositado": lambda s, d: {"total": s["total"] + d["valor"]}}, {"total": 0})

cycle r in armazem.todos() + armazem.todos():     // o mesmo registro, duas vezes
    p.aplicar(r)
assert p.estado()["total"] is 50

// um bug na projeção? conserte o aplicador e reconstrua do histórico
assert p.reconstruir(armazem.todos())["total"] is 50''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Uma projeção por pergunta", "texto": "\"Total do dia\", \"clientes com saldo negativo\" e \"extrato da conta\" são três projeções, e não uma tabela com três usos. Cada uma é pequena, e jogar uma fora e reconstruir do histórico custa só tempo."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/cqrs",
"title": "CQRS",
"description": "O lado que decide e o lado que responde, separados: quando isso simplifica, e quando é peso morto.",
"blocos": [
 {"p": "CQRS separa **comando** (muda o estado, e pode ser recusado) de **consulta** (lê, e nunca muda). No lado do comando, o modelo existe para proteger invariantes; no da consulta, para responder rápido. Tentar que um modelo só faça as duas coisas é de onde vem a tabela com quarenta colunas e três índices que brigam entre si."},
 {"code": _CONTA + '''
armazem := D.armazem()

// ── lado da consulta: um vault pronto para a tela ──
saldos := {}
action ao_gravar(r):
    given r["nome"] is "ContaAberta":
        saldos[r["fluxo"]] := 0
    orif r["nome"] is "Depositado":
        saldos[r["fluxo"]] += r["dados"]["valor"]
    orif r["nome"] is "Sacado":
        saldos[r["fluxo"]] -= r["dados"]["valor"]
armazem.assinar(ao_gravar)

// ── lado do comando: decide, e grava ──
action comandar(conta, comando):
    historia := armazem.ler(conta)
    armazem.anexar(conta, decidir(D.reconstituir(historia, aplicar), comando), len(historia))

comandar("a", {"tipo": "abrir", "titular": "Ana"})
comandar("a", {"tipo": "depositar", "valor": 90})
comandar("b", {"tipo": "abrir", "titular": "Bia"})
assert saldos is {"a": 90, "b": 0}      // a leitura não reconstitui nada''', "lang": "df"},
 {"table": {"head": ["Vale a pena quando", "É peso morto quando"], "rows": [
   ["as leituras são muito mais numerosas e diferentes das escritas", "a tela mostra exatamente o que se grava"],
   ["o modelo de escrita tem invariantes que a tela não precisa ver", "é um CRUD"],
   ["a leitura pode estar um pouco atrasada", "a leitura precisa ver a escrita no mesmo instante"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Consistência eventual", "texto": "Com a projeção atualizada por assinatura, no mesmo processo, ela está em dia quando `anexar` volta. Numa fila entre os dois lados, não: a tela pode mostrar o saldo de antes por alguns milissegundos. Diga isso a quem desenha a tela — \"acabei de depositar e o saldo não mudou\" vira chamado de suporte."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/processos",
"title": "Processos e sagas",
"description": "Quando um fato de um agregado precisa virar comando em outro: o gerente de processo, e a compensação.",
"blocos": [
 {"p": "Um agregado protege a **própria** consistência, e só ela. \"Quando o pagamento for confirmado, reservar o estoque\" atravessa dois agregados — e não cabe dentro de nenhum. Quem liga os dois é um **processo**: ele escuta fatos e emite comandos."},
 {"code": '''adopt Arcane.Dominio as D

armazem := D.armazem()
estoque := {"cafe": 1}
log := []

action processo_de_pedido(r):
    given r["nome"] is "PagamentoConfirmado":
        item := r["dados"]["item"]
        given estoque[item] bigger 0:
            estoque[item] -= 1
            armazem.anexar(r["fluxo"], [{"nome": "EstoqueReservado", "dados": {"item": item}}])
        otherwise:
            // não há como reservar: compensar o que já aconteceu
            armazem.anexar(r["fluxo"], [{"nome": "PagamentoEstornado", "dados": {"motivo": "sem estoque"}}])
    given r["nome"] in ["EstoqueReservado", "PagamentoEstornado"]:
        log.append(r["nome"])

armazem.assinar(processo_de_pedido)
armazem.anexar("pedido-1", [{"nome": "PagamentoConfirmado", "dados": {"item": "cafe"}}])
armazem.anexar("pedido-2", [{"nome": "PagamentoConfirmado", "dados": {"item": "cafe"}}])

assert log is ["EstoqueReservado", "PagamentoEstornado"]''', "lang": "df"},
 {"h2": "Compensar não é desfazer"},
 {"p": "O pagamento do pedido 2 **aconteceu**: o dinheiro saiu da conta de alguém. Não existe apagar esse fato; existe um fato novo — `PagamentoEstornado` — que o compensa. É o que dá à fonte de eventos o histórico honesto: quem lê vê que houve pagamento e estorno, e por quê."},
 {"p": "Quando os passos atravessam **serviços** por rede, e não agregados no mesmo processo, a peça é a `Saga` do [`Arcane.Malha`](/docs/tecnicas/microservicos): ela compensa em ordem inversa e anota a compensação que falhou."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/servicos",
"title": "Serviços de domínio",
"description": "A regra que não pertence a nenhuma entidade — e por que ela não é um 'Manager' com tudo dentro.",
"blocos": [
 {"p": "Transferir dinheiro entre duas contas: a regra é de qual das duas? Nenhuma — e forçá-la dentro de `Conta` faz uma conta mexer na outra, que é exatamente o que o agregado existe para impedir. Uma operação do domínio que **envolve várias** entidades, e não é de nenhuma, é um **serviço de domínio**."},
 {"code": '''adopt Arcane.Dominio as D

action conta(id, saldo):
    c := D.agregado("Conta", id, saldo := saldo)
    c.invariante("saldo não negativo", lambda x => x.ler("saldo") bigger_eq 0)
    mark @c.comando("debitar")
    action debitar(x, v):
        x.mudar(saldo := x.ler("saldo") - v)
    mark @c.comando("creditar")
    action creditar(x, v):
        x.mudar(saldo := x.ler("saldo") + v)
    yield c

// o serviço: coordena, e deixa cada conta cuidar das próprias regras
action transferir(origem, destino, valor, limite_diario := 1000):
    given valor bigger limite_diario:
        trigger $"transferência acima do limite diário de {limite_diario}"
    origem.debitar(valor)         // se falhar aqui, nada mudou
    destino.creditar(valor)

a := conta("A", 100)
b := conta("B", 0)
transferir(a, b, 70)
assert a.ler("saldo") is 30 and b.ler("saldo") is 70

falhou := no
monitor:
    transferir(a, b, 50)          // a invariante de A recusa
handle Error:
    falhou := yes
assert falhou and a.ler("saldo") is 30 and b.ler("saldo") is 70''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "E se o crédito falhar depois do débito?", "texto": "No exemplo, o débito vem primeiro porque é ele que pode ser recusado. Se o crédito também pudesse falhar, o débito já estaria feito — e os dois precisam de uma [unidade de trabalho](/docs/dominio/eventos) que confirme os dois juntos, ou de um [processo com compensação](/docs/dominio/processos)."}},
 {"p": "O cheiro do serviço mal usado é o **`GerenciadorDeContas`** com trinta métodos: a regra saiu das entidades e elas viraram sacos de dados. Serviço é a exceção, para o que não tem dono — não o lugar padrão de toda regra."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/anticorrupcao",
"title": "Camada anticorrupção",
"description": "O modelo de um sistema externo não entra inteiro: é traduzido na fronteira, num lugar só.",
"blocos": [
 {"p": "O ERP da empresa chama cliente de `PARCEIRO_NEGOCIO`, com o CPF em `CD_DOC` sem pontuação e o nome em maiúsculas. Se esse formato entra no seu domínio, cada regra passa a saber do ERP — e no dia em que o ERP muda, muda o seu sistema inteiro. A camada anticorrupção é o tradutor na fronteira, e o **único** lugar que conhece o modelo de fora."},
 {"code": '''adopt Arcane.Dominio as D

steady Cliente := D.valor("Cliente", ["nome", "cpf"],
    regra := lambda c => len(c["cpf"]) is 11, motivo := "CPF com 11 dígitos")

// a tradução: o único lugar que sabe como o ERP escreve
action do_erp(registro):
    yield Cliente(registro["NM_PARCEIRO"].title(),
                  registro["CD_DOC"].replace(".", "").replace("-", ""))

externo := {"NM_PARCEIRO": "ANA SOUZA", "CD_DOC": "123.456.789-01", "FL_ATIVO": "S"}
ana := do_erp(externo)
assert ana.nome is "Ana Souza" and ana.cpf is "12345678901"''', "lang": "df"},
 {"p": "Entre dois **contextos** do próprio sistema vale o mesmo, e `D.contexto` cobra: um contexto recusa receber um modelo de outro sem uma tradução registrada. Ver [Regras e contextos](/docs/dominio/contextos)."},
 {"list": [
   "**O campo que você não usa não entra** — `FL_ATIVO` fica do lado de fora até alguém precisar dele.",
   "**A validação é do seu modelo**, na tradução: um CPF malformado do ERP é recusado na fronteira, e não três camadas adiante.",
   "**A tradução tem teste próprio**, com registros reais do sistema de fora. É o teste que quebra quando o outro lado muda — e é bom que quebre ali."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/testes",
"title": "Testar o domínio",
"description": "Dado estes fatos, quando este comando, então estes fatos — ou esta recusa.",
"blocos": [
 {"p": "Com `decidir` puro, o teste do domínio não precisa de banco, de agregado montado nem de dublê: **dado** o histórico, **quando** o comando chega, **então** saem estes eventos — ou esta recusa. O teste lê como a regra, e a regra é o que ele confere."},
 {"code": _CONTA + '''
action dado_quando_entao(historia, comando):
    yield decidir(D.reconstituir(historia, aplicar), comando)

aberta := [{"nome": "ContaAberta", "dados": {"titular": "Ana"}},
           {"nome": "Depositado", "dados": {"valor": 50}}]

// então: o fato certo
assert dado_quando_entao(aberta, {"tipo": "sacar", "valor": 20}) is
    [{"nome": "Sacado", "dados": {"valor": 20}}]

// então: a recusa certa, com o motivo
motivo := void
monitor:
    dado_quando_entao(aberta, {"tipo": "sacar", "valor": 80})
handle Error as e:
    motivo := e.message
assert motivo.contains("não cobre")

// então: nada acontece numa conta encerrada
encerrada := aberta + [{"nome": "ContaEncerrada", "dados": {}}]
monitor:
    dado_quando_entao(encerrada, {"tipo": "depositar", "valor": 1})
    assert no
handle Error as e:
    assert e.message.contains("não está aberta")''', "lang": "df"},
 {"p": "E as invariantes de um agregado se testam pelo lado de fora: tentar o comando que as violaria, e conferir que o estado e a `versao()` não mudaram. Para o formato dado/quando/então com relatório por passo, [`Crucible.cenario`](/docs/testes/bdd)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/modelagem",
"title": "Modelar o domínio",
"description": "Linguagem ubíqua, event storming e onde traçar a fronteira de um agregado.",
"blocos": [
 {"p": "O código de domínio é tão bom quanto as palavras que ele usa. Se o negócio diz \"o pedido foi **faturado**\" e o código diz `status = 3`, cada conversa entre as duas pontas precisa de tradução — e a tradução é onde os requisitos se perdem."},
 {"h2": "Event storming, em três passos"},
 {"list": [
   "**Os fatos, no passado.** Numa parede (ou num documento), todo mundo escreve o que acontece no negócio: `PedidoFeito`, `PagamentoConfirmado`, `PedidoEnviado`. Discutir o nome de um fato é discutir o negócio.",
   "**O que os causa.** Antes de cada fato, o comando que o provoca (`Pagar`) e quem o dá (o cliente, um sistema, o relógio).",
   "**O que precisa ser consistente junto.** Os fatos que não podem divergir entre si formam um agregado. O resto se comunica por evento."]},
 {"h2": "A fronteira do agregado"},
 {"table": {"head": ["Sinal", "O que ele diz"], "rows": [
   ["dois comandos do mesmo agregado raramente disputam", "o tamanho está bom"],
   ["[`AggregateVersionError`](/docs/dominio/concorrencia-otimista) frequente", "o agregado junta coisas que mudam por motivos diferentes — divida"],
   ["uma invariante precisa de dois agregados", "ou eles são um só, ou a regra é eventual e vira [processo](/docs/dominio/processos)"],
   ["o agregado carrega mil itens para mudar um", "a coleção deveria ser outro agregado, ligado por id"]]}},
 {"code": '''adopt Arcane.Dominio as D

// a linguagem do negócio, e não a do banco
steady Dinheiro := D.valor("Dinheiro", ["centavos", "moeda"],
    regra := lambda v => v["centavos"] bigger_eq 0, motivo := "dinheiro não é negativo")

pedido := D.agregado("Pedido", D.novo_id(), situacao := "aberto", total := Dinheiro(0, "BRL"))
mark @pedido.comando("faturar")
action faturar(p):
    given p.ler("situacao") is not "aberto":
        trigger "só um pedido aberto é faturado"
    p.mudar(situacao := "faturado")
    p.aconteceu("PedidoFaturado")

pedido.faturar()
assert pedido.ler("situacao") is "faturado"
assert pedido.eventos()[0].nome is "PedidoFaturado"''', "lang": "df"},
]},
]
