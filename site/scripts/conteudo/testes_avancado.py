# -*- coding: utf-8 -*-
"""Testes — as dez páginas de prática.

O que já havia descrevia a **ferramenta** (o Crucible, os matchers, os
dublês, as propriedades). O que faltava era a **prática**: o ciclo do
TDD, o que é uma unidade, onde termina um teste de integração, como se
escreve um cenário, o que fazer com um teste instável.

Todo bloco `df` destas páginas roda — `tests/test_paginas_de_testes.py`
os extrai e executa. Uma página sobre testes com um exemplo que não
passa seria a pior forma de ensinar o assunto.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/tdd",
"title": "TDD — vermelho, verde, refatorar",
"description": "O ciclo, passo a passo, construindo um carrinho de compras — e o que cada fase protege.",
"blocos": [
 {"p": "TDD não é escrever teste antes. É escrever **um** teste, vê-lo falhar pelo motivo certo, fazer o mínimo para ele passar, e só então melhorar o código — com o teste segurando o comportamento enquanto a forma muda."},

 {"table": {"head": ["Fase", "O que se faz", "O que ela protege"], "rows": [
   ["**vermelho**", "um teste que falha", "que o teste consegue falhar — um teste que nunca falhou não prova nada"],
   ["**verde**", "o mínimo para passar", "que o código existe por causa de um comportamento pedido"],
   ["**refatorar**", "melhorar a forma, sem mudar o comportamento", "que a limpeza não quebrou nada"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Veja o vermelho pelo motivo certo", "texto": "Um teste que falha com *“'total' não está definido”* não está vermelho: está quebrado. O vermelho útil é o que falha com *“devia ser 30, e veio 0”* — é ele que prova que o teste mede o que você acha que ele mede."}},

 {"h2": "1. Vermelho: o primeiro comportamento"},
 {"code": """// O teste vem primeiro, e a acao existe so o bastante para compilar.
action total(itens):
    yield 0

assert total([]) is 0
// O proximo teste e o que vai falhar:
//   assert total([{"preco": 10, "qtd": 3}]) is 30
out "passo 1: o caso vazio passa; o proximo vai falhar pelo motivo certo\"""", "lang": "df"},

 {"h2": "2. Verde: o mínimo"},
 {"code": """action total(itens):
    soma := 0
    cycle i in itens:
        soma += i["preco"] * i["qtd"]
    yield soma

assert total([]) is 0
assert total([{"preco": 10, "qtd": 3}]) is 30
assert total([{"preco": 10, "qtd": 3}, {"preco": 5, "qtd": 2}]) is 40
out "passo 2: verde\"""", "lang": "df"},

 {"h2": "3. O próximo comportamento puxa o próximo teste"},
 {"p": "A regra nova — *cupom de 10% acima de 100* — entra do mesmo jeito: primeiro o teste, depois o código."},
 {"code": """action subtotal(itens):
    yield sum(itens >> morph i: i["preco"] * i["qtd"])

action total(itens, cupom := ""):
    s := subtotal(itens)
    given cupom is "DEZ" and s bigger 100:
        yield round(s * 0.9, 2)
    yield s

// Os testes antigos continuam — e sao eles que autorizam a refatoracao.
assert total([]) is 0
assert total([{"preco": 10, "qtd": 3}]) is 30
assert total([{"preco": 60, "qtd": 2}], "DEZ") is 108.0
assert total([{"preco": 60, "qtd": 1}], "DEZ") is 60
out "passo 3: a regra nova, e as antigas seguraram a mudanca\"""", "lang": "df"},

 {"h2": "Refatorar: o que pode e o que não pode"},
 {"table": {"head": ["Pode", "Não pode"], "rows": [
   ["extrair `subtotal` de `total`", "mudar o que `total` devolve"],
   ["trocar o laço por pipeline", "acrescentar comportamento *“já que estou aqui”*"],
   ["renomear o que é interno", "mudar teste e código no mesmo passo"]]}},

 {"callout": {"tipo": "dica", "titulo": "Passos pequenos", "texto": "Se o verde demora mais de alguns minutos, o teste pediu demais. Volte, escreva um teste menor. O TDD funciona porque cada passo é pequeno o bastante para que, quando algo quebra, só haja um lugar onde procurar."}},

 {"p": "Continue em [Testes unitários](/docs/testes/unitarios) e [Regressão](/docs/testes/regressao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/unitarios",
"title": "Testes unitários",
"description": "O que é uma unidade, a forma preparar-agir-conferir, e um teste por razão de falhar.",
"blocos": [
 {"p": "Uma unidade é o menor pedaço de comportamento que faz sentido sozinho — quase sempre uma ação ou um método. O teste unitário a exercita **sem** o que é lento, caro ou de fora: sem rede, sem disco, sem relógio de verdade."},

 {"h2": "Preparar, agir, conferir"},
 {"code": """adopt Arcane.Crucible

action desconto(total, cliente):
    given cliente["vip"]:
        yield total * 0.1
    given total bigger_eq 200:
        yield total * 0.05
    yield 0

crucible "desconto":
    trial "vip ganha 10% em qualquer valor":
        // preparar
        cliente := {"vip": yes}
        // agir
        d := desconto(50, cliente)
        // conferir
        expect d is 5.0

    trial "comum ganha 5% a partir de 200":
        expect desconto(200, {"vip": no}) is 10.0

    trial "comum abaixo de 200 nao ganha nada":
        expect desconto(199.99, {"vip": no}) is 0

r := Crucible.run()
assert r["falhou"] is 0 and r["passou"] is 3""", "lang": "df"},

 {"h2": "As cinco regras"},
 {"table": {"head": ["Regra", "Sem ela"], "rows": [
   ["**uma razão para falhar** por teste", "o teste cai e não se sabe qual das quatro coisas quebrou"],
   ["o **nome** diz o comportamento", "`teste_desconto_3` falha, e é preciso ler o corpo para saber o quê"],
   ["**sem lógica** no teste (sem `given`, sem laço)", "o teste passa a precisar de teste"],
   ["**independente** da ordem", "o teste 7 só passa depois do 6, e rodar sozinho falha"],
   ["**rápido** (milissegundos)", "ninguém roda a suíte antes do commit, e ela para de proteger"]]}},

 {"h2": "Os limites valem mais que o meio"},
 {"p": "O bug mora na fronteira: `199.99` e `200` dizem mais sobre `desconto` que `150` e `500`. Para cada `bigger_eq`, teste o valor exato e o imediatamente abaixo."},

 {"callout": {"tipo": "atencao", "titulo": "Não teste a implementação", "texto": "Um teste que confere que `desconto` chamou `round` duas vezes quebra na primeira refatoração que não mudou nada. Confira o **que** sai, não **como** saiu — dublês de interação são para fronteiras (rede, banco), não para o miolo."}},

 {"p": "Continue em [Parametrizados](/docs/testes/parametrizados) e [Dublês](/docs/crucible/dubles)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/parametrizados",
"title": "Testes parametrizados",
"description": "Uma tabela de casos, um corpo só — e o caso que falhou aparece pelo nome.",
"blocos": [
 {"p": "Quando dez testes têm o mesmo corpo e mudam só os dados, eles são uma tabela. `Crucible.table` roda um trial por linha: o corpo é escrito uma vez, e a falha diz **qual linha** quebrou."},

 {"code": """adopt Arcane.Crucible

action categoria(idade):
    given idade smaller 0:
        trigger "idade negativa"
    given idade smaller 12:
        yield "crianca"
    given idade smaller 18:
        yield "adolescente"
    given idade smaller 60:
        yield "adulto"
    yield "idoso"

crucible "categoria por idade":
    Crucible.table("limites", [
        {"idade": 0, "esperado": "crianca"},
        {"idade": 11, "esperado": "crianca"},
        {"idade": 12, "esperado": "adolescente"},
        {"idade": 17, "esperado": "adolescente"},
        {"idade": 18, "esperado": "adulto"},
        {"idade": 59, "esperado": "adulto"},
        {"idade": 60, "esperado": "idoso"}
    ], lambda caso: Crucible.expect(categoria(caso["idade"])).to_be(caso["esperado"]))

    trial "idade negativa e recusada":
        expect(lambda => categoria(-1)).to_raise()

r := Crucible.run()
assert r["falhou"] is 0
assert r["passou"] is 8""", "lang": "df"},

 {"h2": "Quando usar tabela, e quando não"},
 {"table": {"head": ["Tabela", "Trials separados"], "rows": [
   ["o corpo é **o mesmo** e só os dados mudam", "cada caso confere uma coisa diferente"],
   ["os limites de uma regra", "caminhos diferentes (sucesso, erro, vazio)"],
   ["a tabela da lei, linha por linha", "o caso precisa de preparo próprio"]]}},

 {"callout": {"tipo": "dica", "titulo": "A tabela como especificação", "texto": "Uma tabela de limites é o que o analista de negócio consegue ler e conferir. Mantenha as colunas com nome (`idade`, `esperado`) e não com posição — `[0, \"crianca\"]` exige saber a ordem para ler."}},

 {"p": "Para **milhares** de entradas geradas, e não uma tabela escrita: [Teste por propriedade](/docs/crucible/propriedades)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/bdd",
"title": "Cenários — dado, quando, então",
"description": "Comportamento escrito como frase, e a falha que diz em qual frase quebrou.",
"blocos": [
 {"p": "`Crucible.cenario` escreve o teste como o comportamento é descrito: *dado* o estado, *quando* algo acontece, *então* o resultado. O ganho não é a sintaxe — é que a falha passa a dizer **em qual frase** quebrou, e essa frase é a que o negócio escreveu."},

 {"code": """adopt Arcane.Crucible as C

c := C.cenario("saque acima do saldo")
c.dado("uma conta com R$ 100", lambda m: m.set("saldo", 100))
c.e("um limite de R$ 50", lambda m: m.set("limite", 50))
c.quando("tento sacar R$ 120", lambda m: m.set("ok", 120 smaller_eq m["saldo"] + m["limite"]))
c.entao("o saque e aceito", lambda m: m["ok"])
c.e("o saldo seria negativo", lambda m: m["saldo"] - 120 smaller 0)

out c.texto()
r := c.rodar()
assert r["ok"] and len(r["passos"]) is 5""", "lang": "df"},

 {"h2": "A falha nomeia o passo"},
 {"code": """adopt Arcane.Crucible as C

c := C.cenario("frete gratis")
c.dado("um carrinho de R$ 180", lambda m: m.set("total", 180))
c.quando("calculo o frete", lambda m: m.set("frete", 0 given m["total"] bigger_eq 200 otherwise 15))
c.entao("o frete e zero", lambda m: m["frete"] is 0)

monitor:
    c.rodar()
    assert no
handle Error as e:
    out e.message
    assert "passo 3" in e.message and "o frete e zero" in e.message""", "lang": "df"},

 {"h2": "As três regras que ele cobra"},
 {"table": {"head": ["Regra", "Porque"], "rows": [
   ["a ordem é **dado → quando → então**", "um preparo depois da ação faz o cenário testar duas coisas, e a falha não diz qual — um `dado` depois de `quando` é recusado na montagem"],
   ["**sem `entao` não há cenário**", "um cenário que só prepara e age não confere nada, e passaria sempre"],
   ["os passos dividem **um `mundo`**", "variável solta entre passos esconde de onde veio o valor que o `entao` confere"]]}},

 {"callout": {"tipo": "nota", "titulo": "Não é Gherkin, e não é Cucumber", "texto": "Não há arquivo `.feature` separado nem casamento de frase por expressão regular. A frase e a ação moram juntas, no mesmo arquivo — o que se perde em separação ganha-se em não haver dois lugares que precisam concordar."}},

 {"p": "Continue em [Testes de integração](/docs/testes/integracao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/integracao",
"title": "Testes de integração",
"description": "O banco de verdade, a rota inteira — e onde termina a unidade.",
"blocos": [
 {"p": "O teste unitário prova que cada peça funciona. O de integração prova que **elas se encaixam**: o SQL que a regra monta é aceito pelo banco, a rota traduz o JSON que o cliente manda. É o teste que pega o erro que só existe entre duas peças."},

 {"h2": "Com o banco de verdade"},
 {"code": """adopt Arcane.Crucible
adopt Arcane.Database as DB

action criar_esquema(db):
    DB.execute(db, "CREATE TABLE contas (id INTEGER PRIMARY KEY, dono TEXT UNIQUE, saldo REAL CHECK (saldo >= 0))")

action abrir(db, dono):
    DB.execute(db, "INSERT INTO contas (dono, saldo) VALUES (?, 0)", [dono])

action depositar(db, dono, valor):
    DB.execute(db, "UPDATE contas SET saldo = saldo + ? WHERE dono = ?", [valor, dono])

action saldo(db, dono):
    yield DB.query(db, "SELECT saldo FROM contas WHERE dono = ?", [dono])[0]["saldo"]

crucible "contas no banco":
    trial "deposito aparece no saldo":
        db := DB.memory()
        criar_esquema(db)
        abrir(db, "ana")
        depositar(db, "ana", 50)
        expect saldo(db, "ana") is 50.0

    trial "o banco recusa dono repetido":
        db := DB.memory()
        criar_esquema(db)
        abrir(db, "ana")
        expect(lambda => abrir(db, "ana")).to_raise()

    trial "o CHECK do banco segura o saldo negativo":
        db := DB.memory()
        criar_esquema(db)
        abrir(db, "bia")
        expect(lambda => depositar(db, "bia", -10)).to_raise()

r := Crucible.run()
assert r["falhou"] is 0 and r["passou"] is 3""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "Um banco novo por teste", "texto": "`DB.memory()` dentro do trial dá a cada teste um banco limpo, em microssegundos. Um banco compartilhado entre testes faz o resultado depender da ordem — e `Crucible.banco(db)` desfaz a transação no fim do trial quando o banco precisa ser o mesmo."}},

 {"h2": "Com a rota inteira"},
 {"code": """adopt Kiln
adopt Arcane.Crucible

server api on 0:
    route POST "/somar":
        given not is_number(body["a"] ?? void) or not is_number(body["b"] ?? void):
            respond 400 json {"erro": "a e b precisam ser numeros"}
        respond json {"resultado": body["a"] + body["b"]}

crucible "rota /somar":
    trial "soma o que chega":
        r := Kiln.test(api, "POST", "/somar", {"a": 2, "b": 3})
        expect r["status"] is 200
        expect r["body"]["resultado"] is 5

    trial "texto no lugar de numero e 400, e nao 500":
        expect Kiln.test(api, "POST", "/somar", {"a": "2", "b": 3})["status"] is 400

r := Crucible.run()
assert r["falhou"] is 0""", "lang": "df"},

 {"h2": "Onde termina a unidade"},
 {"table": {"head": ["Unitário", "Integração", "Ponta a ponta"], "rows": [
   ["a regra, sem banco", "a regra **com** o banco", "o sistema subido"],
   ["milissegundos", "dezenas de ms", "segundos"],
   ["centenas", "dezenas", "poucos"],
   ["diz **qual** peça", "diz **qual encaixe**", "diz que **algo** quebrou"]]}},

 {"p": "Continue em [Ponta a ponta](/docs/testes/ponta-a-ponta) e [A pirâmide](/docs/testes/piramide)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/ponta-a-ponta",
"title": "Testes ponta a ponta",
"description": "O programa rodando como o usuário o roda — subprocesso, código de saída e o que só aparece com socket.",
"blocos": [
 {"p": "O teste ponta a ponta executa o programa **como ele é executado**: `dataforge run`, argumentos, saída no terminal, código de saída. Ele é lento e diz pouco sobre onde está o defeito — e pega o que nenhum outro pega: o `main.df` que não liga as peças, a variável de ambiente que falta, o código de saída zero numa falha."},

 {"h2": "A CLI inteira, por subprocesso"},
 {"code": """adopt Arcane.Crucible
adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Process as P

pasta := $"{OS.temp_dir()}/df-e2e-{randint(100000, 999999)}"
IO.mkdir(pasta)
programa := $"{pasta}/somar.df"
IO.write(programa, \"\"\"adopt Arcane.OS as OS
args := OS.argv()
given len(args) is not 2:
    out "uso: somar A B"
    OS.exit(2)
out int(args[0]) + int(args[1])
\"\"\")

crucible "somar, de fora":
    trial "imprime a soma e sai com 0":
        r := P.run(["dataforge", "run", programa, "--", "2", "40"])
        expect r["code"] is 0
        expect r["stdout"].trim() is "42"

    trial "sem argumentos, sai com 2 e diz o uso":
        r := P.run(["dataforge", "run", programa])
        expect r["code"] is 2
        expect "uso" in r["stdout"]

r := Crucible.run()
IO.remove_tree(pasta)
assert r["falhou"] is 0""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Confira o código de saída", "texto": "É o que o CI lê. Uma CLI que imprime *“erro”* e sai com 0 passa em todo pipeline, e o deploy segue com o passo que falhou. O teste ponta a ponta é o único lugar onde isso é conferido."}},

 {"h2": "O que só aparece com socket"},
 {"p": "`Kiln.test` roda a rota **na mesma thread**, sem socket. Três classes de defeito ficam de fora e só aparecem subindo o servidor de verdade:"},
 {"table": {"head": ["Defeito", "Porque o `Kiln.test` não vê"], "rows": [
   ["corrida entre pedidos", "tudo roda numa thread só — ver o aviso `escrita-concorrente`"],
   ["cookie que o navegador descarta", "`Kiln.test` não devolve cookies"],
   ["`--host=0.0.0.0` esquecido no contêiner", "não há rede"]]}},

 {"callout": {"tipo": "dica", "titulo": "Poucos, e sobre o caminho feliz", "texto": "Cada teste ponta a ponta custa segundos e quebra por motivos que não são o código (porta ocupada, disco cheio). Tenha um por fluxo que **tem** de funcionar — login, compra, exportação — e deixe as variações para os testes de baixo."}},

 {"p": "Continue em [A pirâmide](/docs/testes/piramide)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/erros",
"title": "Testar erros e exceções",
"description": "Que ele falha, com que tipo, com que mensagem — e que não falhou pela metade.",
"blocos": [
 {"p": "O caminho de erro é o menos testado e o que mais aparece em produção. Três perguntas por falha: **ela acontece?**, **com o tipo certo?**, **deixou tudo como estava?** A terceira é a que quase ninguém escreve."},

 {"code": """adopt Arcane.Crucible

record SaldoInsuficiente:
    pedido: Float
    disponivel: Float

contas := {"ana": 100.0, "bia": 0.0}

action transferir(de, para, valor):
    given valor smaller_eq 0:
        trigger "valor precisa ser positivo"
    given contas[de] smaller valor:
        trigger SaldoInsuficiente(valor, contas[de])
    contas[de] -= valor
    contas[para] += valor

crucible "transferir":
    trial "falha com o tipo do dominio":
        monitor:
            transferir("bia", "ana", 10.0)
            Crucible.fail("devia ter levantado")
        handle SaldoInsuficiente as e:
            expect e.value.disponivel is 0.0

    trial "a mensagem diz o que fazer":
        expect(lambda => transferir("ana", "bia", -5)).to_raise()

    trial "a falha nao deixa nada pela metade":
        antes := {"ana": contas["ana"], "bia": contas["bia"]}
        monitor:
            transferir("ana", "bia", 1000.0)
        handle Error:
            antes := antes
        expect contas["ana"] is antes["ana"]
        expect contas["bia"] is antes["bia"]

r := Crucible.run()
assert r["falhou"] is 0 and r["passou"] is 3""", "lang": "df"},

 {"h2": "O que conferir numa falha"},
 {"table": {"head": ["Pergunta", "Como", "Porque"], "rows": [
   ["ela acontece?", "`expect(lambda => …).to_raise()`", "o `lambda` adia a chamada — sem ele o erro estoura antes do `expect`"],
   ["com o tipo certo?", "`handle SeuTipo as e`", "`handle Error` pega também o `1 / 0` do seu próprio bug"],
   ["com o valor certo?", "`e.value` num record levantado", "o chamador decide pelo campo, não pelo texto"],
   ["nada ficou pela metade?", "comparar o estado antes e depois", "o débito aconteceu e o crédito não"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Não compare o texto da mensagem", "texto": "Um teste que confere `e.message is \"saldo insuficiente\"` quebra na primeira correção de vírgula e na primeira tradução. Compare o **tipo** e os **campos** — o texto é para humanos."}},

 {"p": "Continue em [Regressão](/docs/testes/regressao) e [Erros](/docs/erros)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/regressao",
"title": "Testes de regressão",
"description": "O teste que falha antes do conserto, o instantâneo — e por que todo bug vira teste.",
"blocos": [
 {"p": "Um bug corrigido sem teste volta. Não por descuido: a correção é feita na pressa, e três meses depois alguém *“simplifica”* aquela linha estranha. O teste de regressão é o que explica, para sempre, por que a linha é estranha."},

 {"h2": "A ordem é o método"},
 {"list": [
   "**Reproduza** o bug num teste. Ele precisa falhar — pelo motivo do bug.",
   "**Corrija** o código. O teste passa.",
   "**Deixe o teste** com o nome do comportamento, e o número do chamado num comentário.",
 ], "ordered": True},

 {"code": """adopt Arcane.Crucible

// Chamado #318: "Joao da Silva" virava "Joao Da Silva" na nota fiscal.
action titulo_de_nome(nome):
    miudas := ["da", "de", "do", "das", "dos", "e"]
    partes := []
    cycle p in nome.lower().split(" "):
        given p in miudas and len(partes) bigger 0:
            partes.append(p)
        otherwise:
            partes.append(capitalize(p))
    yield " ".join(partes)

crucible "nome na nota fiscal":
    // #318 — a preposicao ficava maiuscula
    trial "preposicao no meio fica minuscula":
        expect titulo_de_nome("JOAO DA SILVA") is "Joao da Silva"

    trial "mas no comeco e maiuscula":
        expect titulo_de_nome("de souza") is "De Souza"

r := Crucible.run()
assert r["falhou"] is 0""", "lang": "df"},

 {"h2": "O instantâneo, para o que é grande"},
 {"p": "Para uma saída de trinta linhas — um relatório, um HTML, um JSON — escrever o esperado à mão dá um teste que ninguém mantém. `Crucible.snapshot` grava na primeira vez e compara depois; `DF_ATUALIZAR_SNAPSHOT=1` aceita uma mudança **intencional**."},

 {"table": {"head": ["Instantâneo serve para", "Não serve para"], "rows": [
   ["uma saída grande e estável", "um valor com data, hora ou id aleatório"],
   ["pegar a mudança **não pedida**", "descobrir se a saída está **certa** — na primeira vez ele aprova qualquer coisa"],
   ["HTML, relatório, JSON de rota", "o que cabe num `expect … is …`"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Revise o diff do instantâneo", "texto": "Atualizar todos os instantâneos sem ler o diff transforma a regressão em aprovação automática. O arquivo vai para o controle de versão justamente para que a mudança apareça na revisão."}},

 {"p": "Continue em [Instantâneos](/docs/tecnicas/instantaneos) e [Mutação](/docs/crucible/mutacao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/piramide",
"title": "A pirâmide, e o que não testar",
"description": "Quantos de cada tipo, onde o custo mora — e as quatro coisas que não merecem teste.",
"blocos": [
 {"p": "A pirâmide não é uma regra de proporção: é uma consequência de custo. Um teste unitário roda em milissegundos e aponta a linha; um ponta a ponta leva segundos e diz *“algo quebrou”*. Por isso a base é larga e o topo é estreito — e uma suíte de cabeça para baixo é lenta, instável e não diz onde procurar."},

 {"code": """          ▲  ponta a ponta   poucos · segundos · "algo quebrou"
         ▲▲▲  integracao      dezenas · dezenas de ms · "qual encaixe"
      ▲▲▲▲▲▲▲  unitarios      centenas · milissegundos · "qual linha\"""", "lang": "text"},

 {"h2": "Onde cada tipo de defeito aparece"},
 {"table": {"head": ["Defeito", "Onde ele é pego"], "rows": [
   ["a conta de desconto errada", "unitário"],
   ["o SQL que o banco recusa", "integração"],
   ["o JSON que a rota não entende", "integração (`Kiln.test`)"],
   ["o `main.df` que não liga as peças", "ponta a ponta"],
   ["a corrida entre dois pedidos", "ponta a ponta, com servidor de verdade"],
   ["o teste que não testa", "mutação — [Crucible.mutar](/docs/crucible/mutacao)"]]}},

 {"h2": "O que não testar"},
 {"table": {"head": ["Não teste", "Porque"], "rows": [
   ["a biblioteca dos outros", "`sorted` já é testado; teste o **seu** uso dele"],
   ["o código gerado", "teste o gerador — ou compare com a saída esperada"],
   ["o que não tem lógica (um `record` só com campos)", "o teste repete a declaração"],
   ["detalhes privados", "o teste quebra a cada refatoração que não mudou nada"]]}},

 {"h2": "Cobertura: um piso, não uma meta"},
 {"p": "`dataforge test --cobertura --minimo=80` reprova quando a cobertura cai — e é para isso que serve. Como meta ela mente: 100% de linhas executadas não diz que alguma coisa foi **conferida**. Um teste sem `expect` cobre tudo e não prova nada."},

 {"code": """dataforge test tests/ --cobertura            # quais linhas rodaram
dataforge test tests/ --cobertura --minimo=80 # reprova abaixo de 80%
dataforge crucible tests/ --mutar src/regras.df  # o teste pega a mudanca?""", "lang": "bash"},

 {"p": "Continue em [Cobertura](/docs/tecnicas/cobertura) e [Testes instáveis](/docs/testes/instaveis)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/testes/instaveis",
"title": "Testes instáveis",
"description": "O teste que passa e falha sem mudar nada — as cinco causas, e por que repetir não é a correção.",
"blocos": [
 {"p": "Um teste instável é pior que nenhum: ele ensina o time a rodar o CI de novo em vez de ler a falha. E no dia em que a falha é real, ela é tratada como ruído. Toda instabilidade tem uma causa, e a causa quase sempre é uma destas cinco."},

 {"table": {"head": ["Causa", "Sintoma", "Correção"], "rows": [
   ["**tempo**", "falha perto da meia-noite, ou numa máquina lenta", "relógio falso: `Crucible.com_relogio` / `freeze_time`"],
   ["**ordem**", "passa sozinho, falha na suíte", "estado compartilhado — um banco novo por teste"],
   ["**aleatoriedade**", "falha uma vez em vinte", "semente fixa, ou teste por propriedade com a semente no relatório"],
   ["**concorrência**", "falha só no CI, que tem outro número de núcleos", "sincronizar de verdade; medir com `Crucible.corrida`"],
   ["**medida absoluta**", "*“devia levar menos de 50 ms”*", "comparar uma **razão** contra a mesma máquina"]]}},

 {"h2": "Tempo: o relógio que você controla"},
 {"code": """adopt Arcane.Crucible

action vencido(prazo, agora):
    yield agora bigger prazo

crucible "prazo":
    trial "vence depois do prazo, e nao antes":
        expect vencido(1000, 999) is no
        expect vencido(1000, 1000) is no
        expect vencido(1000, 1001) is yes

r := Crucible.run()
assert r["falhou"] is 0

// A regra recebe 'agora' como argumento. Uma acao que chama time()
// por dentro so e testavel na hora certa do dia.""", "lang": "df"},

 {"h2": "Repetir não é corrigir"},
 {"p": "`Crucible.flaky(acao, tentativas)` existe, e devolve **quantas tentativas** foram precisas — um teste que precisa de três toda vez não é instável, está quebrado. Use-o como diagnóstico, nunca como correção permanente."},

 {"callout": {"tipo": "atencao", "titulo": "Medida absoluta mede a máquina", "texto": "`assert tempo smaller 50` passa no seu notebook e falha num runner do CI carregado. Este repositório já reprovou três vezes assim. A saída é cobrar um **fator** contra uma referência medida no mesmo instante — ver [Prometer desempenho](/docs/bibliotecas/desempenho)."}},

 {"p": "Continue em [Cenários de concorrência e relógio](/docs/crucible/cenarios)."},
]},
]
