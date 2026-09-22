# -*- coding: utf-8 -*-
"""Dados — mais dez páginas: janelas, séries, junção, pivô, limpeza,
estatística, amostragem, exportação, volume e o caminho até o gráfico.

As janelas (média móvel, acumulado, defasagem, variação, posição) são o
acréscimo à linguagem desta leva. Os resultados que as páginas afirmam
foram conferidos rodando — inclusive um que merece aviso: o `pivotar`
com `soma` põe 0, e não `void`, na célula sem dado.
"""

_VENDAS = '''adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"dia": "2026-09-01", "loja": "centro", "valor": 120},
    {"dia": "2026-09-02", "loja": "centro", "valor": 150},
    {"dia": "2026-09-03", "loja": "centro", "valor": void},
    {"dia": "2026-09-04", "loja": "centro", "valor": 90},
    {"dia": "2026-09-05", "loja": "centro", "valor": 200},
    {"dia": "2026-09-01", "loja": "norte", "valor": 80},
    {"dia": "2026-09-02", "loja": "norte", "valor": 60}])
'''

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/janelas",
"title": "Janelas",
"description": "Média móvel, acumulado, defasagem, variação e posição — os cinco verbos de janela do Quadro.",
"blocos": [
 {"p": "As cinco perguntas de toda série: *a média dos últimos dias*, *o total até agora*, *o valor de ontem*, *quanto variou*, *qual a posição*. São cinco verbos do `Quadro`, e cada um devolve um quadro novo com uma coluna a mais."},
 {"code": _VENDAS + '''
centro := vendas.onde(lambda l: l["loja"] is "centro").ordenar("dia")
q := centro
    .janela("valor", 2)
    .acumulado("valor")
    .defasar("valor")
    .variacao("valor")
    .ranquear("valor")
out q.pegar("dia", "valor", "valor_media_2", "valor_soma_acumulado", "valor_variacao", "valor_posicao").texto()

assert q.coluna("valor_soma_acumulado") is [120, 270, 270, 360, 560]
assert q.coluna("valor_antes_1") is [void, 120, 150, void, 90]
assert q.coluna("valor_posicao") is [3, 2, void, 4, 1]''', "lang": "df"},
 {"table": {"head": ["Verbo", "Responde", "A ponta"], "rows": [
   ["`janela(col, n, agregacao)`", "a média (ou soma, máximo…) dos últimos `n`", "`void` até haver `n` valores válidos"],
   ["`acumulado(col, agregacao)`", "o total (ou máximo…) até a linha", "a ausência é pulada, não zera"],
   ["`defasar(col, n)`", "o valor de `n` linhas atrás (`-n`: à frente)", "`void` fora do quadro"],
   ["`variacao(col)`", "a razão em relação à linha anterior", "`void` se a anterior for 0 ou ausente"],
   ["`ranquear(col)`", "a posição, 1 é o maior", "a ausência não entra e sai `void`"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Ordene antes", "texto": "Todas as janelas seguem a **ordem das linhas**. Uma média móvel sobre linhas fora de ordem calcula a média de dias que não são vizinhos — e nada denuncia. `ordenar(\"dia\")` antes de qualquer janela."}},
 {"callout": {"tipo": "dica", "titulo": "Por que `void` nas primeiras linhas", "texto": "A média móvel de 7 dias no dia 2 não existe: há só 2 dias. Devolver a média desses 2 fingiria ser uma média de 7, e o gráfico mostraria uma subida que é só a janela enchendo. Com `minimo := 1` você pede, de propósito, a média do que houver."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/series-temporais",
"title": "Séries temporais",
"description": "Por loja, por dia: agrupar, ordenar e aplicar a janela em cada grupo — e a lacuna no calendário.",
"blocos": [
 {"p": "Uma série temporal quase nunca é uma só: é uma por loja, por produto, por cliente. A janela precisa ser calculada **dentro** de cada série — senão a média móvel do norte usa o último dia do centro."},
 {"code": _VENDAS + '''
partes := []
cycle chave in unique(vendas.coluna("loja")):
    serie := vendas.onde(lambda l: l["loja"] is chave).ordenar("dia")
    partes.append(serie.acumulado("valor").variacao("valor"))

resultado := partes[0]
cycle p in partes[1:]:
    resultado := resultado.empilhar(p)

norte := resultado.onde(lambda l: l["loja"] is "norte")
assert norte.coluna("valor_soma_acumulado") is [80, 140]
assert norte.coluna("valor_variacao") is [void, -0.25]
out resultado.pegar("loja", "dia", "valor_soma_acumulado").texto()''', "lang": "df"},
 {"h2": "A lacuna no calendário"},
 {"p": "Se não houve venda no dia 3, a linha do dia 3 **não existe** — e `defasar` devolve o dia 2 como *“ontem”* do dia 4. Para uma série diária de verdade, complete o calendário antes, com `void` nos dias sem registro:"},
 {"code": '''adopt Arcane.Quadro as Q

registros := {"2026-09-01": 10, "2026-09-02": 12, "2026-09-04": 9}
dias := ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"]
serie := Q.de_vaults(dias >> morph d: {"dia": d, "valor": registros[d] ?? void})

assert serie.coluna("valor") is [10, 12, void, 9]
assert serie.defasar("valor").coluna("valor_antes_1")[3] is void    // o dia 3, e nao o 2''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/juntar",
"title": "Juntar quadros",
"description": "Os quatro JOIN — dentro, esquerda, direita, fora — e as linhas que somem ou se multiplicam.",
"blocos": [
 {"p": "`juntar` cruza dois quadros por uma coluna em comum, como o `JOIN` do SQL. O tipo decide o que acontece com as linhas que **não** casam — e é aí que moram os erros."},
 {"code": '''adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"loja": "A", "valor": 10}, {"loja": "A", "valor": 20},
    {"loja": "B", "valor": 5}, {"loja": "B", "valor": 5}])
lojas := Q.de_vaults([{"loja": "A", "cidade": "Recife"}, {"loja": "C", "cidade": "Natal"}])

assert vendas.juntar(lojas, "loja").altura() is 2             // so o que casa
assert vendas.juntar(lojas, "loja", "esquerda").altura() is 4 // toda venda
assert vendas.juntar(lojas, "loja", "fora").altura() is 5     // tudo, dos dois lados

esq := vendas.juntar(lojas, "loja", "esquerda")
assert esq.onde(lambda l: l["loja"] is "B").coluna("cidade") is [void, void]
out esq.texto()''', "lang": "df"},
 {"table": {"head": ["Tipo", "Mantém", "Uso típico"], "rows": [
   ["`dentro`", "só as linhas que casam nos dois", "vendas com cadastro válido"],
   ["`esquerda`", "toda linha da esquerda; a direita vira `void` onde falta", "**o mais comum**: enriquecer sem perder venda"],
   ["`direita`", "toda linha da direita", "lojas, com ou sem venda"],
   ["`fora`", "tudo dos dois lados", "conciliar duas fontes"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A chave repetida multiplica linhas", "texto": "Se o quadro da direita tiver a loja `A` duas vezes (um cadastro duplicado), cada venda de `A` sai **duas** vezes — e a soma dobra, calada. Antes de juntar, confira `lojas.duplicadas(\"loja\").altura() is 0`."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/pivotar",
"title": "Pivotar e despivotar",
"description": "Linhas viram colunas (a tabela dinâmica) e voltam — e a célula sem dado que sai 0.",
"blocos": [
 {"p": "`pivotar` transforma valores de uma coluna em colunas — a tabela dinâmica da planilha. `despivotar` faz o caminho de volta. Os dois existem porque cada forma serve a uma coisa: a larga para ler, a longa para calcular."},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "A", "mes": "jan", "valor": 10}, {"loja": "A", "mes": "fev", "valor": 20},
    {"loja": "B", "mes": "jan", "valor": 5}, {"loja": "B", "mes": "jan", "valor": 5}])

larga := v.pivotar("loja", "mes", "valor")      // soma por padrao
out larga.texto()
assert larga.onde(lambda l: l["loja"] is "B").coluna("jan") is [10]

longa := larga.despivotar(["loja"], "mes", "valor")
assert longa.altura() is 4''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Com `soma`, a célula sem dado sai 0", "texto": "A loja B não vendeu em fevereiro, e a célula `B/fev` sai **0**, e não `void`. Para uma soma isso é defensável — nada vendido soma zero —, mas uma média de uma célula 0 não é a média de nada. Se a diferença entre *“vendeu zero”* e *“não há registro”* importa, faça a contagem ao lado: `v.tabela_cruzada(\"loja\", \"mes\")`."}},
 {"code": '''adopt Arcane.Quadro as Q

v := Q.de_vaults([{"loja": "A", "mes": "jan"}, {"loja": "B", "mes": "jan"}, {"loja": "B", "mes": "jan"}])
t := v.tabela_cruzada("loja", "mes")
assert t.onde(lambda l: l["loja"] is "B").coluna("jan") is [2]
out t.texto()''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/limpeza",
"title": "Limpar dados",
"description": "Perfil primeiro, depois ausência, tipos, duplicatas e valores fora da curva — nessa ordem.",
"blocos": [
 {"p": "Limpar sem olhar é adivinhar. O primeiro passo é o **perfil**: por coluna, o tipo inferido, quantos faltam, quantos distintos, mínimo e máximo. Ele diz onde está o problema antes de você mexer em qualquer coisa."},
 {"code": '''adopt Arcane.Quadro as Q

bruto := Q.de_vaults([
    {"id": 1, "idade": "34", "cidade": "Recife"},
    {"id": 2, "idade": "", "cidade": "recife "},
    {"id": 2, "idade": "", "cidade": "recife "},
    {"id": 3, "idade": "trinta", "cidade": "Natal"},
    {"id": 4, "idade": "290", "cidade": "Natal"}])

out bruto.perfil().texto()

limpo := bruto
    .sem_duplicadas()
    .converter({"idade": "Integer"})                         // 'trinta' vira void
    .mapear("cidade", lambda c: (c ?? "").trim().capitalize())

assert limpo.altura() is 4
assert limpo.coluna("idade") is [34, void, void, 290]
assert limpo.coluna("cidade") is ["Recife", "Recife", "Natal", "Natal"]''', "lang": "df"},
 {"table": {"head": ["Ordem", "Passo", "Verbo"], "rows": [
   ["1", "olhar", "`perfil()`"],
   ["2", "tirar a linha repetida", "`sem_duplicadas(por)`"],
   ["3", "converter os tipos", "`converter({…})` — o que falha vira `void`, contado no perfil"],
   ["4", "padronizar o texto", "`mapear` com `trim`, `lower`, `capitalize`"],
   ["5", "decidir a ausência", "`preencher(\"media\")`, `sem_nulos()`, ou deixar"],
   ["6", "olhar o que sobrou fora da curva", "`fora_da_curva(col)` — **olhar**, não apagar"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Fora da curva não é erro", "texto": "Uma idade de 290 é erro de digitação; uma venda 30 vezes maior que a média pode ser o maior cliente do ano. `fora_da_curva` devolve as linhas para você **olhar** — apagar automaticamente o que é raro é apagar exatamente o que mais importa."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/estatistica",
"title": "Estatística descritiva",
"description": "descrever, correlação, discretizar e contar valores — e a média que mente com a cauda.",
"blocos": [
 {"p": "`descrever` responde as perguntas de sempre de uma vez — contagem, média, desvio, mínimo, quartis, máximo — por coluna numérica. É o primeiro número a olhar depois do perfil."},
 {"code": '''adopt Arcane.Quadro as Q

salarios := Q.de_colunas({"salario": [2000, 2100, 2200, 2300, 2400, 50000]})
out salarios.descrever().texto()

// A media diz 10.166; a mediana, 2.250. Um salario puxa a media para cima.
assert mean(salarios.coluna("salario")) bigger 10000
assert median(salarios.coluna("salario")) is 2250''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A média esconde a cauda", "texto": "Seis salários, cinco perto de 2.200 e um de 50.000: a média é 10.166 — um salário que ninguém ganha. Com cauda longa (renda, tempo de resposta, preço de imóvel), reporte a **mediana** e os percentis. É a mesma razão por que o `Arcane.Perfil` mede P50/P95/P99 e não a média."}},
 {"code": '''adopt Arcane.Quadro as Q

q := Q.de_vaults([
    {"horas": 1, "nota": 5}, {"horas": 2, "nota": 6},
    {"horas": 3, "nota": 7}, {"horas": 4, "nota": 9}])
c := q.correlacao()
out c.texto()

faixas := Q.de_colunas({"idade": [15, 22, 37, 41, 68]}).discretizar("idade", 3)
out faixas.texto()

cores := Q.de_colunas({"cor": ["azul", "verde", "azul", "azul"]}).contar_valores("cor")
out cores.texto()''', "lang": "df"},
 {"p": "Correlação não é causa: horas de estudo e nota andam juntas aqui, e isso não diz qual puxa qual — nem se um terceiro fator puxa as duas."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/amostragem",
"title": "Amostrar",
"description": "amostra com semente, e por que a amostra reproduzível é a única que serve.",
"blocos": [
 {"p": "Trabalhar com uma amostra é o que torna possível explorar um arquivo de dez milhões de linhas — e só serve se a mesma análise, rodada amanhã, escolher **as mesmas** linhas. Por isso a amostra aceita uma semente."},
 {"code": '''adopt Arcane.Quadro as Q

clientes := Q.de_colunas({"id": range(1, 1001)})
a := clientes.amostra(5, 42)
b := clientes.amostra(5, 42)
assert a.coluna("id") is b.coluna("id")           // mesma semente, mesmas linhas
assert a.altura() is 5
out a.coluna("id")''', "lang": "df"},
 {"table": {"head": ["Quero", "Faça"], "rows": [
   ["explorar rápido", "`amostra(1000, semente)`"],
   ["um relatório que outra pessoa refaz", "a **mesma** semente, escrita no relatório"],
   ["treinar e testar um modelo", "`Cortex.dividir(dados, 0.2, semente, alvo)` — estratificado pela classe"],
   ["as primeiras linhas para olhar a forma", "`topo(5)` — e não confundir com amostra"]]}},
 {"callout": {"tipo": "atencao", "titulo": "`topo` não é amostra", "texto": "As primeiras linhas de um arquivo costumam ser as mais antigas, de um único dia, de um único lote. Um padrão que aparece no topo pode não existir no resto. Para olhar a forma, `topo`; para tirar conclusão, `amostra`."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/exportar",
"title": "Exportar",
"description": "CSV, JSON, planilha e banco — e o formato que cada destino espera.",
"blocos": [
 {"p": "O fim de todo pipeline de dados é um arquivo que outra ferramenta vai ler. Cada destino tem uma expectativa, e errar a expectativa produz o erro mais irritante que existe: o arquivo abre, e está errado."},
 {"code": '''adopt Arcane.Quadro as Q
adopt Arcane.IO as IO
adopt Arcane.OS as OS

q := Q.de_vaults([{"produto": "Cafe", "preco": 18.5}, {"produto": "=SOMA(A1)", "preco": 1}])
pasta := $"{OS.temp_dir()}/df-exp-{randint(100000, 999999)}"
IO.mkdir(pasta)

q.para_csv($"{pasta}/produtos.csv")
q.para_csv($"{pasta}/produtos-br.csv", ";")       // o Excel em portugues espera ';'
texto := IO.read($"{pasta}/produtos.csv")
out texto
assert "Cafe" in texto

volta := Q.de_csv($"{pasta}/produtos.csv")
assert volta.altura() is 2
IO.remove_tree(pasta)''', "lang": "df"},
 {"table": {"head": ["Destino", "Use", "O detalhe que quebra"], "rows": [
   ["Excel em português", "`para_csv(caminho, \";\")`", "com `,` ele junta tudo numa coluna"],
   ["outra API", "`para_json()`", "datas como texto ISO; `void` vira `null`"],
   ["planilha de verdade", "`Arcane.Excel`", "tipos e várias abas; fórmula é gravada, não calculada"],
   ["banco", "`Database.upsert_many`", "o CSV que chega de novo duplica — use upsert"]]}},
 {"callout": {"tipo": "perigo", "titulo": "Uma célula que começa com `=` é executada", "texto": "O Excel executa a célula que começa com `=`, `+`, `-` ou `@` — um nome de produto `=HYPERLINK(...)` vira link ativo na planilha de quem abriu. Para CSV que alguém vai abrir no Excel, passe o texto por `Seguranca.escapar_csv` — ver [Entrada e saída](/docs/seguranca/entrada)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/volume",
"title": "Muitos dados",
"description": "Quando o arquivo não cabe: ler em pedaços, agregar sem guardar, e quando passar para um banco.",
"blocos": [
 {"p": "Um `Quadro` guarda tudo em memória. Para um arquivo de alguns milhões de linhas, isso ainda funciona; para dezenas de gigabytes, não. Três estratégias, em ordem de esforço."},
 {"table": {"head": ["Estratégia", "Quando", "Com"], "rows": [
   ["**agregar enquanto lê**", "a pergunta é uma soma, uma contagem, uma média", "um `cycle` sobre as linhas, sem guardar"],
   ["**ler em pedaços**", "cada pedaço é processado sozinho", "`stream action` que emite lotes"],
   ["**passar para um banco**", "a pergunta muda a cada dia", "SQLite com índice — `Arcane.Database`"]]}},
 {"code": '''// Agregar enquanto le: memoria constante, qualquer tamanho.
stream action linhas_de(texto):
    cycle linha in texto.lines()[1:]:
        emit linha.split(",")

csv := "loja,valor\\nA,10\\nB,5\\nA,20\\nB,7"
total := {}
cycle campos in linhas_de(csv):
    loja := campos[0]
    total[loja] := (total[loja] ?? 0) + int(campos[1])

assert total is {"A": 30, "B": 12}''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Meça antes de mudar de estratégia", "texto": "`dataforge profile` diz onde o tempo vai. Na maioria dos casos o gargalo não é o tamanho: é um `in` numa lista dentro do laço (O(n²)) — ver [Escolher a estrutura](/docs/big-o/escolher). Trocar a lista por um `set` resolve antes de qualquer banco."}},
 {"p": "Para volume de verdade: [Lago de dados](/docs/tecnicas/lago) e [Parquet](/docs/tecnicas/parquet)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dados/visualizar",
"title": "Do quadro ao gráfico",
"description": "Levar um Quadro para um painel da Vitrine — a janela vira linha, o pivô vira barra.",
"blocos": [
 {"p": "Um número numa tabela diz o valor; um gráfico diz a **forma** — a tendência, a sazonalidade, o ponto fora. A Vitrine desenha a partir de uma lista de vaults, que é exatamente o que um `Quadro` devolve com `para_vaults()`."},
 {"code": '''adopt Arcane.Quadro as Q
adopt Arcane.Vitrine as V

vendas := Q.de_vaults([
    {"dia": "01", "valor": 120}, {"dia": "02", "valor": 150},
    {"dia": "03", "valor": 90}, {"dia": "04", "valor": 200}])
    .janela("valor", 2, "media", "media_movel", 1)

action painel():
    V.titulo("Vendas")
    V.grafico_linha(vendas.para_vaults(), x := "dia", y := ["valor", "media_movel"])

t := V.testar(painel)
assert not t.falhou()
assert t.existe("grafico")''', "lang": "df"},
 {"table": {"head": ["Pergunta", "Verbo do Quadro", "Gráfico"], "rows": [
   ["como evolui?", "`janela` / `acumulado`", "linha"],
   ["qual é maior?", "`agrupar(...).resumir(...)`", "barra"],
   ["quanto de cada um?", "`pivotar`", "barra empilhada"],
   ["como se distribui?", "`discretizar`", "histograma (barra)"],
   ["anda junto?", "`correlacao`", "dispersão"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Barra começa no zero; linha não precisa", "texto": "Numa barra, o que significa é o comprimento, e cortar o eixo faz 3% parecer o dobro. Numa linha, o que significa é a posição — forçar o zero achata a variação que o gráfico existe para mostrar. A Vitrine já decide assim; ver [Gráficos](/docs/vitrine/graficos)."}},
]},
]
