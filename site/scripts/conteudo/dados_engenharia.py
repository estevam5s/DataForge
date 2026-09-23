# -*- coding: utf-8 -*-
"""Engenharia de dados — sete páginas.

As três peças novas desta leva (partição nas janelas, cardinalidade na
junção e deriva de esquema) nasceram aqui: cada uma foi achada
escrevendo a página, rodando o exemplo e vendo o número errado sair
sem erro nenhum.

Todo bloco roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/engenharia",
"title": "Engenharia de dados",
"description": "O que separa uma análise que roda de um pipeline que se pode confiar — e as três formas de errar em silêncio.",
"blocos": [
 {"p": "Uma análise erra e alguém percebe: o gráfico fica estranho. Um **pipeline** erra e ninguém percebe — o número é plausível, o processo termina com código zero, e a conclusão errada vira decisão. Esta seção é sobre as formas de errar que **não dão erro**."},
 {"table": {
   "head": ["O erro", "Como ele aparece", "A defesa"],
   "rows": [
     ["janela sem partição", "média móvel \"por loja\" atravessa as lojas", "`por := \"loja\"`"],
     ["junção que multiplica", "o total sobe, e as linhas também", "`cardinalidade := \"muitos_para_um\"`"],
     ["deriva de esquema", "o `id` chega como texto, e o `join` para de casar", "`Qualidade.exigir_esquema`"],
     ["reprocessar sem idempotência", "o mesmo dia contado duas vezes", "marca d'água, e partição sobrescrita"],
     ["ausência virando zero", "a soma cai, e a média sobe", "`void` é vão, e não zero"]]}},
 {"cards": [
   {"title": "Janelas por grupo", "desc": "média móvel, acumulado e ranking dentro da partição.", "href": "/docs/dados/particao"},
   {"title": "Junções que não inflam", "desc": "declarar a cardinalidade, e o total que subiu de 30 para 40.", "href": "/docs/dados/cardinalidade"},
   {"title": "Deriva de esquema", "desc": "o que mudou no que chega, e se isso quebra.", "href": "/docs/dados/deriva"},
   {"title": "Carga incremental", "desc": "marca d'água, reprocessamento e idempotência.", "href": "/docs/dados/incremental"}]},
 {"h2": "O caminho inteiro, num programa"},
 {"code": '''adopt Arcane.Quadro as Q
adopt Arcane.Qualidade as Qual

// ── 1. o que chegou ────────────────────────────────────────
bruto := [
    {"dia": "2026-01-05", "loja": "sul",   "produto": "cafe",   "valor": 98.7},
    {"dia": "2026-01-05", "loja": "norte", "produto": "cafe",   "valor": 32.9},
    {"dia": "2026-01-06", "loja": "sul",   "produto": "filtro", "valor": 42.5},
    {"dia": "2026-01-06", "loja": "norte", "produto": "cafe",   "valor": 65.8},
    {"dia": "2026-01-07", "loja": "sul",   "produto": "cafe",   "valor": 51.0},
]

// ── 2. o esquema esperado, e a conferência ────────────────
esperado := Qual.esquema_de(bruto)
relato := Qual.exigir_esquema(bruto, esperado)
assert relato["ok"] is yes

// ── 3. o quadro, e a janela POR LOJA ──────────────────────
vendas := Q.de_vaults(bruto).ordenar("dia")
com_media := vendas.janela("valor", 2, "media", "media_2", void, "loja")
assert com_media.altura() is 5

// ── 4. o apoio, com a cardinalidade declarada ─────────────
lojas := Q.de_vaults([
    {"loja": "sul", "regiao": "SE"},
    {"loja": "norte", "regiao": "N"},
])
junto := com_media.juntar(lojas, "loja", "dentro", "muitos_para_um")
assert junto.altura() is 5          // não inflou

// ── 5. a resposta ─────────────────────────────────────────
por_regiao := junto >> agrupar "regiao" >> resumir {"valor": "soma"}
out por_regiao.texto()''', "lang": "df"},
 {"p": "Cinco passos, e quatro deles são sobre **não errar em silêncio**. É a proporção certa: o trabalho de um pipeline é quase todo em garantir que o número final significa o que ele diz significar."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/particao",
"title": "Janelas por grupo",
"description": "Média móvel por loja, ranking por categoria, variação em relação ao dia anterior do mesmo produto.",
"blocos": [
 {"p": "Toda função de janela sem partição responde à pergunta errada no caso mais comum que existe. \"Média móvel de sete dias **por loja**\" atravessava a fronteira das lojas: a primeira venda da loja B entrava com as três últimas da loja A."},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "sul",   "dia": 1, "valor": 10},
    {"loja": "norte", "dia": 1, "valor": 100},
    {"loja": "sul",   "dia": 2, "valor": 20},
    {"loja": "norte", "dia": 2, "valor": 200},
    {"loja": "sul",   "dia": 3, "valor": 30},
])

// SEM partição: o acumulado soma as duas lojas juntas.
sem := v.acumulado("valor")
assert sem.coluna("valor_soma_acumulado") is [10, 110, 130, 330, 360]

// COM partição: cada loja tem o seu.
com := v.acumulado("valor", "soma", void, "loja")
assert com.coluna("valor_soma_acumulado") is [10, 100, 30, 300, 60]
out com.texto()''', "lang": "df"},
 {"p": "O primeiro resultado não é um erro visível: é um número plausível. Num painel de vendas ele apareceria como \"acumulado da loja sul: 360\", e ninguém tem como desconfiar olhando."},
 {"h2": "As cinco que aceitam `por`"},
 {"table": {
   "head": ["Função", "Responde", "Com `por`"],
   "rows": [
     ["`janela`", "a média dos últimos N", "dos últimos N **daquele grupo**"],
     ["`acumulado`", "o total corrido", "o total corrido **do grupo**"],
     ["`defasar`", "o valor de N linhas atrás", "da linha anterior **do mesmo grupo**"],
     ["`variacao`", "quanto mudou", "em relação ao anterior **do grupo**"],
     ["`ranquear`", "a posição geral", "a posição **dentro do grupo**"]]}},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"cat": "bebida", "produto": "cafe",   "vendas": 300},
    {"cat": "bebida", "produto": "cha",    "vendas": 120},
    {"cat": "acessorio", "produto": "filtro", "vendas": 90},
    {"cat": "acessorio", "produto": "caneca", "vendas": 150},
])

// Um ranking GLOBAL responde "quem vendeu mais no total".
global_ := v.ranquear("vendas", "posicao_geral")
assert global_.coluna("posicao_geral") is [1, 3, 4, 2]

// O que quase sempre se quer é "quem é o primeiro DA SUA categoria".
na_cat := global_.ranquear("vendas", "posicao_na_cat", yes, "minimo", "cat")
assert na_cat.coluna("posicao_na_cat") is [1, 2, 2, 1]
out na_cat.texto()''', "lang": "df"},
 {"h2": "A ordem das linhas é preservada"},
 {"p": "A coluna nova volta na posição **original**, e não agrupada. Um quadro reordenado pela janela quebraria o `com`, que casa por posição — e faria a linha 3 do resultado não corresponder à linha 3 da entrada, que é o tipo de defeito que só aparece três junções depois."},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"g": "a", "i": 1, "x": 10},
    {"g": "b", "i": 2, "x": 100},
    {"g": "a", "i": 3, "x": 20},
])
r := v.acumulado("x", "soma", void, "g")
assert r.coluna("i") is [1, 2, 3]           // a ordem é a de entrada
assert r.coluna("x_soma_acumulado") is [10, 100, 30]''', "lang": "df"},
 {"h2": "Partição por várias colunas"},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "sul", "produto": "cafe", "v": 1},
    {"loja": "sul", "produto": "cafe", "v": 2},
    {"loja": "sul", "produto": "cha",  "v": 10},
    {"loja": "norte", "produto": "cafe", "v": 100},
])
r := v.acumulado("v", "soma", void, ["loja", "produto"])
assert r.coluna("v_soma_acumulado") is [1, 3, 10, 100]''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Ordene antes", "texto": "Uma janela lê as linhas **na ordem em que elas estão**. Para \"os últimos sete dias\", ordene por data antes — senão a janela junta o que estiver perto no arquivo, e não no tempo. Ordenar depois da janela não conserta: o valor já foi calculado."}},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "sul", "dia": 3, "x": 30},
    {"loja": "sul", "dia": 1, "x": 10},
    {"loja": "sul", "dia": 2, "x": 20},
])

// Fora de ordem, a "variação em relação a ontem" é ficção.
errado := v.variacao("x", "delta", no)
assert errado.coluna("delta") is [void, 0 - 20, 10]

// Ordenar primeiro é o que a torna verdade.
certo := v.ordenar("dia").variacao("x", "delta", no)
assert certo.coluna("delta") is [void, 10, 10]''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/cardinalidade",
"title": "Junções que não inflam",
"description": "Uma chave duplicada na tabela de apoio multiplica o fato — e o total sobe sem nada acusar.",
"blocos": [
 {"p": "É o desastre mais caro da engenharia de dados, e ele cabe em quatro linhas: a tabela de apoio ganhou uma linha duplicada, a junção multiplicou o fato, e o total do relatório subiu."},
 {"code": '''adopt Arcane.Quadro as Q

vendas := Q.de_vaults([{"cli": "a", "v": 10}, {"cli": "b", "v": 20}])

// A tabela de apoio com a chave DUPLICADA — quase sempre por um
// carregamento repetido, ou por um cadastro que virou dois.
clientes := Q.de_vaults([
    {"cli": "a", "nome": "Ana"},
    {"cli": "a", "nome": "Ana (duplicada)"},
    {"cli": "b", "nome": "Bia"},
])

junto := vendas.juntar(clientes, "cli")
assert junto.altura() is 3                              // eram 2 vendas
assert (junto.coluna("v") >> distill a, x: a + x 0) is 40   // era 30
out "duas vendas de 30 viraram três linhas de 40 — sem erro nenhum"''', "lang": "df"},
 {"h2": "Declarar fecha a porta"},
 {"code": '''adopt Arcane.Quadro as Q

vendas := Q.de_vaults([{"cli": "a", "v": 10}, {"cli": "b", "v": 20}])
clientes := Q.de_vaults([
    {"cli": "a", "nome": "Ana"},
    {"cli": "a", "nome": "Ana (duplicada)"},
    {"cli": "b", "nome": "Bia"},
])

monitor:
    vendas.juntar(clientes, "cli", "dentro", "muitos_para_um")
    assert no
handle Error as e:
    out e.message
    out $"  {e.dica}"''', "lang": "df"},
 {"table": {
   "head": ["Cardinalidade", "Promete", "Quando"],
   "rows": [
     ["`muitos_para_um`", "a chave é única **do outro lado**", "a busca numa tabela de apoio — o caso mais comum"],
     ["`um_para_muitos`", "única **deste lado**", "um pedido e seus itens"],
     ["`um_para_um`", "única nos dois", "duas visões da mesma entidade"],
     ["`muitos_para_muitos`", "nada", "a permissiva **declarada** — e é o padrão"]]}},
 {"p": "O padrão continua sendo **não conferir**: mudá-lo reprovaria código que já existe e pode estar certo. O que muda é ser possível declarar — e um `muitos_para_um` numa junção de apoio custa uma palavra."},
 {"h2": "Declarar a explosão é diferente de não dizer nada"},
 {"code": '''adopt Arcane.Quadro as Q

pedidos := Q.de_vaults([{"id": 1}, {"id": 2}])
itens := Q.de_vaults([
    {"id": 1, "produto": "cafe"},
    {"id": 1, "produto": "filtro"},
    {"id": 2, "produto": "cha"},
])

// Aqui a multiplicação é o PONTO: um pedido tem vários itens.
// Declará-la diz a quem lê que alguém pensou nisso.
junto := pedidos.juntar(itens, "id", "dentro", "um_para_muitos")
assert junto.altura() is 3
out junto.texto()''', "lang": "df"},
 {"h2": "Antes de declarar, olhe"},
 {"code": '''adopt Arcane.Quadro as Q

clientes := Q.de_vaults([
    {"cli": "a", "nome": "Ana"},
    {"cli": "a", "nome": "Ana 2"},
    {"cli": "b", "nome": "Bia"},
])

// 'duplicadas' responde quais chaves se repetem, e quantas vezes.
repetidas := clientes.duplicadas(["cli"])
assert repetidas.altura() > 0
out repetidas.texto()

// E 'sem_duplicadas' mantém a PRIMEIRA de cada chave.
limpo := clientes.sem_duplicadas(["cli"])
assert limpo.altura() is 2''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A junção que não casa nada também é silenciosa", "texto": "Com `tipo := \"dentro\"`, uma chave que mudou de tipo (o `id` inteiro virou texto) não casa com **nada** — e o resultado é um quadro vazio, sem erro. Confira a altura depois de juntar: `assert junto.altura() > 0` é a asserção mais barata de um pipeline."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/deriva",
"title": "Deriva de esquema",
"description": "Alguém a montante acrescentou uma coluna, renomeou outra e passou a mandar o id como texto.",
"blocos": [
 {"p": "É a falha que mais derruba pipeline em produção, e ela não chega como erro: o programa continua rodando, e o número sai errado. `Qualidade.esquema_de` lê o esquema **do dado** — ele não é declarado, e é isso que permite comparar o lote de hoje com o de ontem sem ninguém ter escrito o contrato antes."},
 {"code": '''adopt Arcane.Qualidade as Qual

ontem := [{"id": 1, "nome": "Ana", "valor": 10.5},
          {"id": 2, "nome": "Bia", "valor": 20.0}]

esquema := Qual.esquema_de(ontem)
assert esquema["id"]["tipo"] is "inteiro"
assert esquema["nome"]["nulavel"] is no
out esquema''', "lang": "df"},
 {"h2": "Os três baldes"},
 {"p": "São os do `Arcane.Abi`, pela mesma razão: há mudança que quebra, mudança que não quebra, e mudança sobre a qual **não dá para saber**."},
 {"table": {
   "head": ["Balde", "O que é"],
   "rows": [
     ["`quebra`", "campo que sumiu, tipo que mudou, campo que passou a vir vazio"],
     ["`compativel`", "campo novo — quem não o lê não vê diferença"],
     ["`desconhecido`", "o campo existe dos dois lados e um deles nunca viu valor"]]}},
 {"code": '''adopt Arcane.Qualidade as Qual

ontem := [{"id": 1, "nome": "Ana", "valor": 10.5},
          {"id": 2, "nome": "Bia", "valor": 20.0}]
hoje := [{"id": "3", "nome": "Cau", "valor": 30.0, "canal": "web"},
         {"id": "4", "nome": void,  "valor": 1.0,  "canal": "app"}]

d := Qual.deriva(Qual.esquema_de(ontem), Qual.esquema_de(hoje))
out d["resumo"]
cycle q in d["quebra"]:
    out $"  QUEBRA  {q['campo']}: {q['o_que']} ({q['antes']} → {q['agora']})"
cycle c in d["compativel"]:
    out $"  ok      {c['campo']}: {c['o_que']}"

assert d["ok"] is no
assert len(d["compativel"]) is 1''', "lang": "df"},
 {"h2": "Presença e vazios são contas diferentes"},
 {"p": "Um campo que vem **sempre**, com metade em branco, tem presença 1,0 e vazios 0,5 — e é o segundo número que quebra quem lê. Confundir os dois foi o primeiro defeito desta peça:"},
 {"code": '''adopt Arcane.Qualidade as Qual

e := Qual.esquema_de([{"a": "x"}, {"a": void}])
assert e["a"]["presenca"] is 1.0      // a chave veio nas duas linhas
assert e["a"]["vazios"] is 0.5        // e metade estava vazia
assert e["a"]["nulavel"] is yes''', "lang": "df"},
 {"h2": "Na entrada do pipeline"},
 {"code": '''adopt Arcane.Qualidade as Qual

CONTRATO := {
    "id": {"tipo": "inteiro", "nulavel": no},
    "nome": {"tipo": "texto", "nulavel": no},
    "valor": {"tipo": "numero", "nulavel": no},
}

bom := [{"id": 1, "nome": "Ana", "valor": 10.0}]
relato := Qual.exigir_esquema(bom, CONTRATO)
assert relato["ok"] is yes

// E o lote que mudou de tipo é RECUSADO, com o que mudou na mensagem.
ruim := [{"id": "1", "nome": "Ana", "valor": 10.0}]
monitor:
    Qual.exigir_esquema(ruim, CONTRATO)
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"p": "Falhar aqui custa **uma execução**; deixar passar custa um relatório errado que ninguém desconfia. É a mesma conta do `Forge.esperar`, que recusa uma senha errada na hora em vez de insistir por quarenta segundos."},
 {"h2": "O terceiro balde, e por que ele existe"},
 {"code": '''adopt Arcane.Qualidade as Qual

// 'b' veio só como vazio ontem, e como texto hoje. Acusar reprovaria
// o correto; calar deixaria passar o que quebra. Ele vai para o
// balde que diz "não dá para saber".
antes := Qual.esquema_de([{"a": 1, "b": void}])
depois := Qual.esquema_de([{"a": 2, "b": "texto"}])

d := Qual.deriva(antes, depois)
assert d["quebra"] is []
assert d["desconhecido"][0]["campo"] is "b"
out d["desconhecido"][0]''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/incremental",
"title": "Carga incremental",
"description": "Marca d'água, reprocessamento e a idempotência que separa um pipeline de um script.",
"blocos": [
 {"p": "Ler tudo toda vez funciona até o dado crescer. A partir daí, o pipeline precisa saber **até onde já leu** — e precisa aguentar rodar duas vezes sem contar o mesmo dia duas vezes."},
 {"code": '''adopt Arcane.Pipeline as Pipe
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-inc-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

// Um fluxo com ESTADO lembra entre execuções.
fluxo := Pipe.fluxo("vendas", $"{pasta}/estado.json")

// Na primeira execução, a marca é void — e isso é o "carregue tudo".
assert Pipe.marca(fluxo, "ultima_venda") is void

TODAS := [
    {"id": 1, "dia": "2026-01-05"},
    {"id": 2, "dia": "2026-01-06"},
    {"id": 3, "dia": "2026-01-07"},
]

action carregar(ctx):
    desde := Pipe.marca(fluxo, "ultima_venda") ?? ""
    novas := [v cycle v in TODAS given v["dia"] > desde]
    given len(novas) > 0:
        // A marca só vai ao disco no FIM da execução: se a etapa
        // seguinte falhar, o próximo run relê o mesmo lote.
        Pipe.marcar(fluxo, "ultima_venda", novas[len(novas) - 1]["dia"])
    yield len(novas)

Pipe.etapa(fluxo, "carregar", carregar)
r := Pipe.rodar(fluxo)
assert r["ok"] is yes
out $"primeira execução: {r['resultados']['carregar']} linha(s)"

// A segunda execução não relê nada.
r2 := Pipe.rodar(fluxo)
out $"segunda execução: {r2['resultados']['carregar']} linha(s)"
assert r2["resultados"]["carregar"] is 0''', "lang": "df"},
 {"h2": "A marca só vale se ela for gravada DEPOIS"},
 {"p": "Gravar a marca antes de a etapa seguinte terminar é o defeito clássico: a carga vai até o dia 7, a transformação falha, e o próximo run começa do dia 8 — o dia 7 **nunca** é processado, e ninguém descobre. Por isso ela só vai ao disco no fim da execução."},
 {"h2": "Reprocessar é um comando, e não um acidente"},
 {"code": '''adopt Arcane.Pipeline as Pipe
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-inc2-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

fluxo := Pipe.fluxo("vendas", $"{pasta}/estado.json")
Pipe.etapa(fluxo, "ler", lambda ctx => 1)
Pipe.marcar(fluxo, "ate", "2026-01-07")
Pipe.rodar(fluxo)
assert Pipe.marca(fluxo, "ate") is "2026-01-07"

// 'esquecer_marca' é o botão de reprocessar — explícito, e não um
// efeito colateral de apagar um arquivo.
Pipe.esquecer_marca(fluxo, "ate")
assert Pipe.marca(fluxo, "ate") is void
out "a próxima execução relê tudo"''', "lang": "df"},
 {"h2": "Idempotência: a partição inteira, e não o acréscimo"},
 {"p": "A forma que funciona para reprocessar um dia é **apagar a partição daquele dia e gravar de novo**, e não acrescentar. Acrescentar duplica; sobrescrever a partição é idempotente por construção:"},
 {"code": '''adopt Arcane.Lago as Lago
adopt Arcane.OS as OS
adopt Arcane.IO as IO

raiz := $"{OS.temp_dir()}/df-lago-{randint(100000, 999999)}"
IO.mkdir(raiz)
defer:
    IO.remove_tree(raiz)

lago := Lago.lago(raiz)

action gravar_dia(dia, linhas):
    // Apagar a partição ANTES é o que torna o reprocessamento
    // idempotente: rodar duas vezes dá o mesmo resultado.
    Lago.remover_particao(lago, "vendas", {"dia": dia})
    Lago.acrescentar(lago, "vendas", linhas, ["dia"])
    yield len(linhas)

gravar_dia("2026-01-05", [{"dia": "2026-01-05", "v": 10}])
gravar_dia("2026-01-05", [{"dia": "2026-01-05", "v": 10}])   // de novo

lidas := Lago.ler(lago, "vendas", {"dia": "2026-01-05"})
assert len(lidas) is 1
out "rodou duas vezes, e há uma linha"''', "lang": "df"},
 {"table": {
   "head": ["Estratégia", "Reprocessar é", "Quando"],
   "rows": [
     ["acrescentar", "**duplicar**", "só para evento imutável com id próprio"],
     ["sobrescrever a partição", "idempotente", "o padrão para dado por período"],
     ["`upsert` por chave", "idempotente", "quando a linha muda de valor depois"],
     ["truncar e recarregar", "idempotente, e caro", "tabela pequena de apoio"]]}},
 {"callout": {"tipo": "nota", "titulo": "A marca d'água não é a data de hoje", "texto": "Ela é o maior valor **do que foi lido**. Usar a data do relógio faz o pipeline perder tudo o que chegou atrasado — e dado atrasado é a regra, não a exceção: um evento de ontem que só chegou hoje de manhã some para sempre."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/contratos",
"title": "Contratos de dados",
"description": "O acordo entre quem produz e quem consome — escrito, versionado e cobrado.",
"blocos": [
 {"p": "Um contrato de dados é a mesma ideia do `Arcane.Abi` aplicada a uma tabela: **o que este conjunto promete**, e o que conta como quebra. Sem ele, quem produz não sabe o que pode mudar, e quem consome descobre no incidente."},
 {"code": '''adopt Arcane.Qualidade as Qual

// O contrato é DADO: dá para versioná-lo, difundi-lo e testá-lo.
CONTRATO := {
    "esquema": {
        "id": {"tipo": "inteiro", "nulavel": no},
        "cliente": {"tipo": "texto", "nulavel": no},
        "valor": {"tipo": "numero", "nulavel": no},
    },
    // As regras são um vault POR CAMPO — a mesma forma do 'perfil'.
    "regras": {
        "valor": {"minimo": 0},
        "id": {"unico": yes},
    },
    "frescor_dias": 1,
}

lote := [{"id": 1, "cliente": "Ana", "valor": 10.0},
         {"id": 2, "cliente": "Bia", "valor": 20.0}]

// 1. o esquema
assert Qual.exigir_esquema(lote, CONTRATO["esquema"])["ok"] is yes

// 2. as regras
r := Qual.conferir(lote, CONTRATO["regras"])
assert r["ok"] is yes
assert r["taxa_boa"] is 1.0
out Qual.relatorio(r)''', "lang": "df"},
 {"h2": "O que um contrato precisa dizer"},
 {"table": {
   "head": ["Parte", "Pergunta que ela responde"],
   "rows": [
     ["esquema", "quais campos, de que tipo, e quais podem faltar"],
     ["chave", "o que identifica uma linha — e se ela é única"],
     ["regras de valor", "faixa, formato, lista fechada"],
     ["frescor", "quão velho o dado pode estar"],
     ["volume esperado", "quantas linhas por dia são normais"],
     ["quem responde", "a pessoa ou o time — sem isso, o contrato não tem dono"]]}},
 {"h2": "Volume também é contrato"},
 {"p": "Um lote que chega com 3 linhas onde chegam 30 mil **não quebra nenhuma regra de esquema**: cada linha está perfeita. E é uma das falhas mais comuns — a origem filtrou errado, e o relatório do dia sai com um centésimo do faturamento."},
 {"code": '''adopt Arcane.Qualidade as Qual

action conferir_volume(lote, esperado, tolerancia):
    quantas := len(lote)
    piso := esperado * (1 - tolerancia)
    teto := esperado * (1 + tolerancia)
    given quantas < piso or quantas > teto:
        trigger $"o lote tem {quantas} linha(s), e o esperado é ~{esperado} (±{round(tolerancia * 100)}%)"
    yield quantas

assert conferir_volume([1, 2, 3, 4, 5], 5, 0.5) is 5

monitor:
    conferir_volume([1], 100, 0.2)
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"h2": "E frescor"},
 {"code": '''adopt Arcane.Qualidade as Qual
adopt Arcane.Time as T

agora := T.now()
lote := [{"id": 1, "quando": agora}]

// 'atualidade' conta quantas linhas são mais velhas que o limite.
velhas := Qual.atualidade(lote, "quando", 1)
out velhas
assert velhas["velhas"] is 0
assert velhas["proporcao"] is 0.0''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um contrato sem dono não é contrato", "texto": "Ele precisa nomear quem responde quando quebra. Um arquivo de regras que ninguém mantém vira ruído no CI em três meses — e a reação é desligar a verificação, que é pior que nunca tê-la escrito."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/observar-pipeline",
"title": "Observar um pipeline",
"description": "O que medir para saber que ele está certo — e não só que ele terminou.",
"blocos": [
 {"p": "Um pipeline que termina com código zero **não** está necessariamente certo. As quatro perguntas que um painel de pipeline precisa responder são outras:"},
 {"table": {
   "head": ["Pergunta", "Métrica", "Alerta quando"],
   "rows": [
     ["rodou?", "última execução bem-sucedida", "passou do intervalo esperado"],
     ["trouxe dado?", "linhas por execução", "cai fora da faixa histórica"],
     ["o dado presta?", "taxa de linhas válidas", "abaixo do mínimo do contrato"],
     ["está fresco?", "idade do dado mais novo", "mais velho que o acordado"]]}},
 {"code": '''adopt Arcane.Pipeline as Pipe
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-obs-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

fluxo := Pipe.fluxo("diario", $"{pasta}/estado.json")
Pipe.etapa(fluxo, "extrair", lambda ctx => [1, 2, 3])
Pipe.etapa(fluxo, "transformar", lambda ctx => 3, ["extrair"])

r := Pipe.rodar(fluxo)
out $"ok: {r['ok']}   etapas: {sorted(keys(r['resultados']))}"
assert r["ok"] is yes

// O histórico é o que responde "quando foi a última vez que deu certo".
h := Pipe.historico(fluxo, 5)
assert len(h) >= 1
out $"execuções registradas: {len(h)}"''', "lang": "df"},
 {"h2": "A falha de uma etapa não pode virar sucesso do fluxo"},
 {"code": '''adopt Arcane.Pipeline as Pipe

fluxo := Pipe.fluxo("t")
Pipe.etapa(fluxo, "boa", lambda ctx => 1)
Pipe.etapa(fluxo, "ruim", lambda ctx => 1 / 0, ["boa"])
Pipe.etapa(fluxo, "depois", lambda ctx => 2, ["ruim"])

r := Pipe.rodar(fluxo)
assert r["ok"] is no
out $"ok: {r['ok']}"
// E o que dependia da etapa quebrada NÃO rodou: rodar com a entrada
// pela metade é o que produz o relatório errado.
out $"etapas que rodaram: {sorted(keys(r['resultados']))}"''', "lang": "df"},
 {"h2": "Etapa opcional é uma decisão, e ela é declarada"},
 {"code": '''adopt Arcane.Pipeline as Pipe

fluxo := Pipe.fluxo("t")
Pipe.etapa(fluxo, "principal", lambda ctx => 1)
// 'opcional' diz que a falha dela não derruba o fluxo — é para o
// que é enriquecimento, e nunca para o que é o dado.
Pipe.etapa(fluxo, "enriquecer", lambda ctx => 1 / 0, ["principal"],
           1, 0, void, yes)

r := Pipe.rodar(fluxo)
assert r["ok"] is yes
out "o enriquecimento falhou, e o fluxo seguiu — porque alguém declarou isso"''', "lang": "df"},
 {"h2": "Tentar de novo, com espera"},
 {"code": '''adopt Arcane.Pipeline as Pipe

tentativas := {"n": 0}

action instavel(ctx):
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] < 3:
        trigger "a rede caiu"
    yield "pronto"

fluxo := Pipe.fluxo("t")
Pipe.etapa(fluxo, "buscar", instavel, void, 3, 0)

r := Pipe.rodar(fluxo)
assert r["ok"] is yes
assert tentativas["n"] is 3
out $"precisou de {tentativas['n']} tentativas"''', "lang": "df"},
 {"p": "Repetir só serve para falha **passageira**. Repetir uma credencial errada por quarenta segundos troca um erro claro por um travamento — é a mesma regra do `Forge.esperar`, e ela vale aqui: o que não vai melhorar com o tempo não entra na retentativa."},
]},
]
