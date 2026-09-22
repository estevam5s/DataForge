# -*- coding: utf-8 -*-
"""Observabilidade — as páginas-raiz de /docs/observabilidade e de
/docs/memoria (que respondiam 404) e seis páginas: métricas,
rastreamento, logs estruturados, linhagem, SLO e alertas.

`O.orcamento`, `O.queima` e `O.alerta_slo` entraram nesta leva, e
`O.alertar` passou a aceitar a lista de regras — antes, só o vault, e a
lista estourava com um nome do Python.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade",
"title": "Observabilidade",
"description": "Métricas, rastreamento, logs, linhagem e SLO: responder sobre o sistema sem abrir o código.",
"blocos": [
 {"p": "Observabilidade é conseguir responder, sem abrir o código e sem reproduzir o problema: **executou? quanto demorou? quantos registros? quantos falharam? em qual etapa? quando? em qual versão?** Log sozinho responde a primeira e a sexta; as outras cinco exigem **número**."},
 {"code": '''adopt Arcane.Observar as O

painel := O.painel("importacao", "2.1.0")
O.contar(painel, "linhas_lidas", 40000)
O.contar(painel, "linhas_recusadas", 12)
O.medir(painel, "duracao_ms", 830.0)
assert O.valor(painel, "linhas_recusadas") is 12''', "lang": "df"},
 {"table": {"head": ["Pergunta", "Ferramenta", "Página"], "rows": [
   ["quanto? quantos?", "contador, medida, marcador", "[Métricas](/docs/observabilidade/metricas)"],
   ["onde o tempo foi?", "trechos com pai e filho", "[Rastreamento](/docs/observabilidade/rastreamento)"],
   ["o que aconteceu com ESTE pedido?", "log em JSON, com o id", "[Logs](/docs/observabilidade/logs)"],
   ["de onde veio este dado?", "linhagem", "[Linhagem](/docs/observabilidade/linhagem)"],
   ["estamos dentro do combinado?", "SLO e orçamento de erro", "[SLO](/docs/observabilidade/slo)"],
   ["alguém precisa agir agora?", "alerta de janela dupla", "[Alertas](/docs/observabilidade/alertas)"],
   ["a cauda, e não a média", "percentis", "[Percentis](/docs/observabilidade/perfil)"]]}},
 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/observabilidade/metricas", "title": "Métricas", "desc": "contador, medida e marcador — e o formato do Prometheus"},
   {"href": "/docs/observabilidade/rastreamento", "title": "Rastreamento", "desc": "trechos aninhados: onde o tempo foi"},
   {"href": "/docs/observabilidade/logs", "title": "Logs estruturados", "desc": "JSON por linha, com os campos para filtrar"},
   {"href": "/docs/observabilidade/linhagem", "title": "Linhagem", "desc": "de onde veio o dado, e o que muda se a fonte mudar"},
   {"href": "/docs/observabilidade/slo", "title": "SLO e orçamento de erro", "desc": "a conta que decide se dá para arriscar o deploy"},
   {"href": "/docs/observabilidade/alertas", "title": "Alertas", "desc": "a taxa de queima em duas janelas"},
   {"href": "/docs/observabilidade/perfil", "title": "Percentis, e a cauda", "desc": "P50, P95, P99 — e por que não a média"},
   {"href": "/docs/observabilidade/comparar", "title": "A diferença é real?", "desc": "Mann-Whitney, e o empate honesto"},
   {"href": "/docs/observabilidade/chamadas", "title": "Flame graph e pausas", "desc": "o tempo próprio de cada ação"},
   {"href": "/docs/memoria", "title": "Memória", "desc": "o coletor, o layout e a posse"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/metricas",
"title": "Métricas",
"description": "Contador que só sobe, medida que vira percentil, marcador que é o valor de agora — e o texto que o Prometheus lê.",
"blocos": [
 {"p": "Três formas de número, e escolher errado dá gráfico errado:"},
 {"table": {"head": ["Tipo", "Função", "Exemplo", "Pergunta que responde"], "rows": [
   ["contador", "`O.contar`", "pedidos atendidos, erros", "quantos, desde o começo? (e a taxa, derivando)"],
   ["medida", "`O.medir`", "duração de cada pedido", "qual a distribuição? — P50, P95, P99"],
   ["marcador", "`O.marcar`", "tamanho da fila agora", "quanto vale neste instante?"]]}},
 {"code": '''adopt Arcane.Observar as O

p := O.painel("api")
O.contar(p, "pedidos", 3)
O.contar(p, "pedidos", 2)
O.medir(p, "latencia_ms", 12.0)
O.medir(p, "latencia_ms", 48.0)
O.marcar(p, "fila", 7)
O.marcar(p, "fila", 4)                  // o marcador guarda o último

assert O.valor(p, "pedidos") is 5
assert O.valor(p, "fila") is 4

texto := O.prometheus(p)
out texto
assert texto.contains("# TYPE api_pedidos counter")
assert texto.contains("api_fila 4")''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Contador nunca desce", "texto": "Um contador que desce (\"usuários online\") quebra toda conta de taxa: o Prometheus interpreta a queda como reinício do processo. O que sobe e desce é **marcador**."}},
 {"callout": {"tipo": "dica", "titulo": "Nome com unidade", "texto": "`latencia_ms`, `tamanho_bytes`, `duracao_s`. Um painel que mostra `latencia: 0.048` deixa a pessoa adivinhando se é segundo ou milissegundo — e ela adivinha errado no meio de um incidente."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/rastreamento",
"title": "Rastreamento",
"description": "Trechos com pai e filho: a árvore de onde o tempo de um pedido foi gasto, e em qual etapa ele falhou.",
"blocos": [
 {"p": "A métrica diz que o pedido levou 800 ms; o **rastreamento** diz em quê. Cada etapa abre um trecho, com o trecho de fora como pai, e fecha com o estado. A árvore resultante mostra onde o tempo foi — e qual trecho falhou."},
 {"code": '''adopt Arcane.Observar as O

p := O.painel("importacao")
tudo := O.abrir(p, "importar")
baixar := O.abrir(p, "baixar", tudo)
O.fechar(p, baixar)
validar := O.abrir(p, "validar", tudo)
O.fechar(p, validar, "falhou", "linha 812: CPF inválido")
O.fechar(p, tudo, "falhou")

trechos := O.trechos(p)
falhou := [t cycle t in trechos given t["estado"] is "falhou" and t["pai"] is not void]
assert falhou[0]["nome"] is "validar"
assert falhou[0]["detalhe"].contains("linha 812")''', "lang": "df"},
 {"h2": "Fechar sempre, até no erro"},
 {"p": "Um trecho aberto que nunca fecha some do relatório — justamente o da etapa que falhou. `O.cronometrar` abre, roda e fecha com o estado certo, mesmo quando a ação levanta:"},
 {"code": '''adopt Arcane.Observar as O

p := O.painel("job")
monitor:
    O.cronometrar(p, "calcular", lambda => 1 / 0)
handle Error:
    out "falhou — e o trecho foi fechado assim mesmo"
assert O.trechos(p)[0]["estado"] is "falhou"''', "lang": "df"},
 {"p": "Entre serviços, o id do rastreamento atravessa a rede no cabeçalho: ver [`Arcane.Malha`](/docs/tecnicas/microservicos) e `Contexto.propagar`."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/logs",
"title": "Logs estruturados",
"description": "Uma linha de JSON por evento, com os campos para filtrar — e o que nunca vai para o log.",
"blocos": [
 {"p": "`\"pedido 7 criado por ana em 3,2 s\"` é legível para uma pessoa e inútil para uma busca: achar todos os pedidos lentos exige uma expressão regular por formato de frase. Em JSON, cada informação é um **campo**, e a busca é uma consulta."},
 {"code": '''adopt Arcane.Logging as Log

log := Log.logger("pedidos")
log.as_json()
log.info("pedido criado", {"pedido": 7, "usuario": "ana", "duracao_s": 3.2})''', "lang": "df"},
 {"code": '''{"time": "2026-09-22T10:55:14", "level": "INFO", "logger": "pedidos",
 "message": "pedido criado", "pedido": 7, "usuario": "ana", "duracao_s": 3.2}''', "lang": "text"},
 {"table": {"head": ["Nível", "Quando"], "rows": [
   ["`debug`", "detalhe para quem está depurando — desligado em produção"],
   ["`info`", "o que aconteceu e alguém pode querer contar depois"],
   ["`warn`", "algo inesperado que o programa contornou"],
   ["`error`", "falhou, e alguém vai precisar olhar"],
   ["`fatal`", "o processo não tem como seguir"]]}},
 {"callout": {"tipo": "perigo", "titulo": "O que nunca entra no log", "texto": "Senha, token, número de cartão, CPF inteiro, o corpo inteiro de um pedido. O log é lido por mais gente que o banco, fica guardado por mais tempo, e vaza por lugares que ninguém protege. `Seguranca.escapar_log` fecha a injeção de linha; `Privacidade.pseudonimizar` troca o identificador por um que não se desfaz sem chave."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/linhagem",
"title": "Linhagem de dados",
"description": "De onde veio este número, e o que muda se a fonte mudar: o grafo de derivação, para trás e para a frente.",
"blocos": [
 {"p": "O relatório mostra um faturamento estranho. De onde veio esse número? A **linhagem** registra, a cada transformação, o que entrou e o que saiu — e responde nas duas direções: a **origem** de um dado e o **impacto** de mexer numa fonte."},
 {"code": '''adopt Arcane.Observar as O

p := O.painel("etl")
O.derivar(p, "vendas_limpas", ["vendas.csv"], "remove duplicadas")
O.derivar(p, "faturamento", ["vendas_limpas", "precos.db"], "soma por mês")
O.derivar(p, "painel_diretoria", ["faturamento"], "gráfico")

de_onde := [a["de"] cycle a in O.origem(p, "faturamento")]
assert de_onde.contains("vendas.csv") and de_onde.contains("precos.db")

afetados := O.impacto(p, "precos.db")
assert afetados.contains("painel_diretoria")     // mexer nos preços muda o painel''', "lang": "df"},
 {"table": {"head": ["Pergunta", "Função"], "rows": [
   ["de onde veio?", "`O.origem(p, dado)` — para trás, com o nível"],
   ["o que quebra se eu mudar?", "`O.impacto(p, fonte)` — para a frente"],
   ["o grafo inteiro", "`O.grafo(p)`"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/slo",
"title": "SLO e orçamento de erro",
"description": "99,9% é uma promessa com uma sobra: as falhas que ela permite. O orçamento transforma 'dá para arriscar?' em conta.",
"blocos": [
 {"p": "Um **SLO** (objetivo de nível de serviço) diz quanto do tempo o serviço precisa estar certo — 99,9% dos pedidos respondidos com sucesso, por exemplo. O que sobra, 0,1%, é o **orçamento de erro**: as falhas que o objetivo permite. Com um milhão de pedidos, mil podem falhar."},
 {"code": '''adopt Arcane.Observar as O

o := O.orcamento(0.999, 1000000, 400)
assert o["permitidas"] is 1000.0
assert o["consumido"] is 0.4            // quarenta por cento já foi
assert o["restante"] is 0.6
assert not o["esgotado"]

apertado := O.orcamento(0.999, 1000000, 1200)
assert apertado["esgotado"]             // passou do combinado''', "lang": "df"},
 {"h2": "O que o orçamento decide"},
 {"table": {"head": ["Restante", "O time"], "rows": [
   ["muito", "pode arriscar: deploy na sexta, migração, experimento"],
   ["pouco", "desacelera: só correção, com mais revisão"],
   ["esgotado", "congela o que não é confiabilidade, até o orçamento voltar"]]}},
 {"p": "É isso que o torna útil: a discussão \"este deploy é seguro?\" deixa de ser opinião contra opinião e passa a ser uma conta que os dois lados aceitaram antes."},
 {"h2": "A taxa de queima"},
 {"p": "O orçamento diz **quanto** foi gasto; a **taxa de queima** diz **a que velocidade**. Queima 1 é gastar o orçamento exatamente no fim da janela do SLO. Queima 14,4 numa hora é gastar 2% de um orçamento de 30 dias em uma hora:"},
 {"code": '''adopt Arcane.Observar as O

assert O.queima(0.999, 10000, 10) is 1.0      // o ritmo sustentável
assert O.queima(0.999, 10000, 144) is 14.4    // o limiar clássico: 1,44% de erro
assert O.queima(0.999, 0, 0) is 0.0           // sem tráfego, sem queima''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/alertas",
"title": "Alertas que param de tocar",
"description": "O alerta de janela dupla: a longa evita o pico de 30 segundos, a curta faz o alerta parar quando o problema passou.",
"blocos": [
 {"p": "Alerta é sobre o que **exige ação agora**. Um que dispara todo dia deixa de ser lido em uma semana — e o que importa passa despercebido junto. O desenho que resolve isso é o de **duas janelas** do livro de SRE do Google: dispara só quando a janela longa **e** a curta queimam acima do limiar."},
 {"code": '''adopt Arcane.Observar as O

// a última hora e os últimos cinco minutos, com objetivo de 99,9%
incidente := O.alerta_slo(0.999, {"total": 10000, "falhas": 200}, {"total": 800, "falhas": 20})
assert incidente["disparar"]

ja_passou := O.alerta_slo(0.999, {"total": 10000, "falhas": 200}, {"total": 800, "falhas": 1})
assert not ja_passou["disparar"]
out ja_passou["motivo"]

pico := O.alerta_slo(0.999, {"total": 10000, "falhas": 5}, {"total": 800, "falhas": 20})
assert not pico["disparar"]
out pico["motivo"]''', "lang": "df"},
 {"table": {"head": ["Janela longa", "Janela curta", "Alerta", "Porque"], "rows": [
   ["queima", "queima", "**dispara**", "o problema existe e continua"],
   ["queima", "não queima", "cala", "o problema **passou** — a longa ainda carrega o passado"],
   ["não queima", "queima", "cala", "um pico curto, que o orçamento absorve"]]}},
 {"h2": "Regras de limite simples"},
 {"p": "Para o que não é SLO — fila acima de um tamanho, disco acima de uma porcentagem —, `O.alertar` confere regras sobre as métricas do painel:"},
 {"code": '''adopt Arcane.Observar as O

p := O.painel("worker")
O.marcar(p, "fila", 140)
disparados := O.alertar(p, [{"metrica": "fila", "acima": 100, "texto": "fila acumulando"}])
assert disparados[0]["texto"] is "fila acumulando"''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria",
"title": "Memória",
"description": "O coletor sob controle, o layout de um objeto, o escopo e a posse — num runtime que gerencia a memória por você.",
"blocos": [
 {"p": "DataForge roda sobre o CPython, e a memória é gerenciada: ninguém chama `free`. O que se controla é o **coletor** — quando ele roda, e o que ele deixa para trás — e o **protocolo** de um recurso: quem é dono, quem empresta, quem solta."},
 {"code": '''adopt Arcane.Memoria as Mem

assert Mem.gc_ligado()
Mem.sem_gc(lambda => [i * 2 cycle i in range(1000)])   // um trecho sem pausas do coletor
assert Mem.gc_ligado()                                  // religado, mesmo se a ação falhasse''', "lang": "df"},
 {"cards": [
   {"href": "/docs/memoria/coletor", "title": "O coletor sob controle", "desc": "ligar, desligar, congelar — e a pausa medida"},
   {"href": "/docs/memoria/layout", "title": "O layout de um objeto", "desc": "quanto ocupa, e onde"},
   {"href": "/docs/memoria/escopo", "title": "Escopo e tempo de vida", "desc": "quando um valor deixa de existir"},
   {"href": "/docs/memoria/posse", "title": "Posse", "desc": "dono exclusivo, empréstimo, contagem"},
   {"href": "/docs/memoria/mapa", "title": "Memória: o mapa", "desc": "o que existe, e o que não"},
   {"href": "/docs/estruturas", "title": "Estruturas binárias", "desc": "bloco, janela e ponteiro sem FFI"}]},
 {"callout": {"tipo": "nota", "titulo": "Controlar o coletor não é controlar a memória", "texto": "No CPython quem libera é a **contagem de referências**, e ela roda na hora. O coletor existe só para os ciclos. Desligá-lo num trecho curto não vaza memória em geral — só deixa o ciclo para trás, que é o que torna a técnica segura."}},
]},
]
