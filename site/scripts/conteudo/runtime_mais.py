# -*- coding: utf-8 -*-
"""Runtime — a página-raiz (que respondia 404) e seis páginas: canais
entre fibras, prazos, o executor, contrapressão, falhas e a escolha
entre laço, thread, async e processo.

O canal entre fibras (`L.canal`, `L.enviar`, `L.receber`) entrou nesta
leva. `sleep` e os prazos do laço são em milissegundos.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime",
"title": "O runtime",
"description": "O laço de eventos, as fibras e o executor: muita espera numa thread só.",
"blocos": [
 {"p": "`Arcane.Laco` é um **reator**: uma thread dormindo no `selectors` do sistema até haver algo a fazer — um soquete pronto, um prazo vencido, uma tarefa na fila. É a forma de atender mil conexões com **uma** thread, em vez de mil."},
 {"code": '''adopt Arcane.Laco as L

laco := L.novo()
ordem := []
L.apos(laco, 20, lambda => ordem.append("depois"))
L.agendar(laco, lambda => ordem.append("agora"))
L.apos(laco, 40, lambda => L.parar(laco))
L.rodar(laco)
assert ordem is ["agora", "depois"]''', "lang": "df"},
 {"table": {"head": ["Peça", "Faz"], "rows": [
   ["o laço", "a fila de prontas, a fila de prazos e o seletor de E/S"],
   ["as fibras", "`stream action` que cede o controle em cada `emit`"],
   ["o canal", "fibras que conversam sem trava"],
   ["o executor", "o trabalho que bloqueia vai para um pool, e o resultado volta pela fila"]]}},
 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/runtime/laco", "title": "O laço de eventos", "desc": "o reator, e por que ele dorme em vez de girar"},
   {"href": "/docs/runtime/escalonador", "title": "O escalonador", "desc": "a ordem de execução e a justiça"},
   {"href": "/docs/runtime/fibras", "title": "Fibras", "desc": "stream action como corrotina — e o limite do stackless"},
   {"href": "/docs/runtime/canais", "title": "Canais entre fibras", "desc": "o chan do Go, com contrapressão de graça"},
   {"href": "/docs/runtime/prazos", "title": "Prazos e relógios", "desc": "apos, a_cada e cancelar"},
   {"href": "/docs/runtime/executor", "title": "O executor", "desc": "o trabalho que bloqueia, fora do laço"},
   {"href": "/docs/runtime/contrapressao", "title": "Contrapressão", "desc": "o teto da fila, e a falha visível"},
   {"href": "/docs/runtime/falhas", "title": "Quando algo falha", "desc": "uma conexão ruim não derruba o servidor"},
   {"href": "/docs/runtime/escolher", "title": "Laço, thread, async ou processo", "desc": "qual modelo para qual trabalho"},
   {"href": "/docs/runtime/mapa", "title": "O runtime: o mapa", "desc": "o que existe, e o que não"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/canais",
"title": "Canais entre fibras",
"description": "L.canal: o chan do Go dentro de um laço — encontro com capacidade 0, fila com N, e fechar que termina o consumidor.",
"blocos": [
 {"p": "Duas fibras que dividem uma lista precisam combinar quem mexe quando. O **canal** é a combinação pronta: uma fibra envia, a outra recebe, e o laço suspende quem precisa esperar. Nada é compartilhado além do próprio canal."},
 {"code": '''adopt Arcane.Laco as L

laco := L.novo()
pedidos := L.canal(2)
log := []

stream action produtor():
    cycle i from 1 to 5:
        log.append($"envia {i}")
        emit L.enviar(pedidos, i)          // espera se já há 2 na fila
    pedidos.fechar()

stream action consumidor():
    caixa := {}
    persist yes:
        emit L.receber(pedidos, caixa, "v")
        given caixa["v"] is void:          // fechado e vazio: acabou
            halt
        log.append($"trata {caixa["v"]}")
        emit L.dormir(1)                   // o consumidor é mais lento

L.fibra(laco, produtor)
L.fibra(laco, consumidor)
L.rodar(laco)

tratados := [x cycle x in log given x.starts_with("trata")]
assert tratados is ["trata 1", "trata 2", "trata 3", "trata 4", "trata 5"]''', "lang": "df"},
 {"h2": "Capacidade decide o ritmo"},
 {"table": {"head": ["Capacidade", "Quem envia", "Uso"], "rows": [
   ["0 (padrão)", "espera até alguém receber — um **encontro**", "entregar em mão: sincronizar duas fibras"],
   ["N", "segue até haver N esperando", "absorver rajadas, sem deixar a fila crescer sem fim"]]}},
 {"p": "É a **contrapressão** de graça: um produtor mais rápido que o consumidor para no `enviar`, em vez de encher a memória. Com o canal de capacidade 2 acima, o produtor nunca fica mais de três itens à frente."},
 {"h2": "Fechar"},
 {"list": [
   "**Quem produz fecha.** `pedidos.fechar()` diz \"não vem mais nada\"; o consumidor recebe `void` depois de esvaziar a fila, e sai do laço.",
   "**Enviar num canal fechado é erro** — anotado em `L.falhas(laco)`, e a fibra que enviou termina. Ninguém ia ler.",
   "**Receber pela caixa.** `emit` é instrução, e não expressão: o valor volta escrito no vault que a fibra passou. Explícito, e melhor que fingir que `emit` devolve algo."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/prazos",
"title": "Prazos e relógios",
"description": "apos, a_cada e cancelar — sem uma thread por relógio.",
"blocos": [
 {"p": "Um relógio por thread é o jeito ingênuo: mil temporizadores, mil threads dormindo. O laço guarda todos os prazos num **heap** e dorme até o mais próximo — mil temporizadores custam uma thread."},
 {"code": '''adopt Arcane.Laco as L

laco := L.novo()
batidas := []
relogio := L.a_cada(laco, 10, lambda => batidas.append("tique"))
L.apos(laco, 35, lambda => L.cancelar(relogio))     // para o relógio
L.apos(laco, 60, lambda => L.parar(laco))
L.rodar(laco)

// cancelado aos 35 ms: no máximo 3 batidas de 10 ms — e ao menos uma.
// Num computador carregado podem ser menos; nunca mais.
assert len(batidas) bigger_eq 1 and len(batidas) smaller_eq 3
assert L.cancelada(relogio)''', "lang": "df"},
 {"table": {"head": ["Função", "Faz"], "rows": [
   ["`L.agendar(laco, acao)`", "na próxima volta"],
   ["`L.apos(laco, ms, acao)`", "uma vez, depois de `ms`"],
   ["`L.a_cada(laco, ms, acao)`", "a cada `ms`, até ser cancelado"],
   ["`L.cancelar(tarefa)`", "desmarca — vale para tarefa e para fibra"]]}},
 {"callout": {"tipo": "atencao", "titulo": "O prazo é um mínimo, não uma promessa", "texto": "`apos(laco, 10, f)` roda `f` **não antes** de 10 ms. Se o laço estiver ocupado com uma tarefa lenta, roda depois dela. `L.estatisticas(laco)[\"maior_atraso_ms\"]` mostra quanto o pior prazo atrasou — e um número alto ali quer dizer que alguma tarefa está bloqueando o laço."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/executor",
"title": "O executor",
"description": "O trabalho que bloqueia vai para um pool de threads, e o resultado volta pela fila do laço.",
"blocos": [
 {"p": "Um laço tem **uma** thread. Uma tarefa que bloqueia — ler um arquivo grande, consultar um banco sem driver assíncrono, uma conta pesada — trava **tudo**: nenhum prazo vence, nenhuma conexão é atendida. `L.executar` manda o trabalho para um pool, e entrega o resultado de volta ao laço quando fica pronto."},
 {"code": '''adopt Arcane.Laco as L

laco := L.novo()
log := []

action consulta_lenta():
    sleep(30)                         // um banco sem driver assíncrono
    yield 42

action pronto(r):                     // roda NO LAÇO, quando o pool termina
    log.append($"resultado {r}")
    L.parar(laco)

L.executar(laco, consulta_lenta, pronto)
L.a_cada(laco, 5, lambda => log.append("laço vivo"))
L.rodar(laco)

assert log.contains("resultado 42")
assert log.contains("laço vivo")      // o laço seguiu girando durante a consulta''', "lang": "df"},
 {"list": [
   "**O `depois` roda no laço**, e não no pool: ali ele pode mexer no estado do laço sem trava.",
   "**A conta de trabalhos no pool segura o laço vivo.** Sem ela, `rodar` terminaria antes de o resultado voltar, e `executar` seria uma forma elaborada de jogar trabalho fora.",
   "**Trabalho de CPU não fica mais rápido** num pool de threads: o GIL continua no caminho. Para isso, processos — ver [Laço, thread, async ou processo](/docs/runtime/escolher)."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/contrapressao",
"title": "Contrapressão",
"description": "Uma fonte mais rápida que o consumo: sem teto, a memória cresce até o processo morrer. Com teto, a falha é visível.",
"blocos": [
 {"p": "Quando pedidos chegam mais depressa do que o laço atende, eles se acumulam na fila de prontas. Sem limite, a fila cresce até o processo ser morto por falta de memória — horas depois, e sem mensagem que aponte a causa. O **teto** troca essa morte lenta por uma recusa imediata."},
 {"code": '''adopt Arcane.Laco as L

laco := L.novo(2)                              // no máximo 2 esperando
aceitos := [L.agendar(laco, lambda => void) cycle i in range(5)]
assert aceitos is [yes, yes, no, no, no]
assert L.estatisticas(laco)["recusadas"] is 3''', "lang": "df"},
 {"table": {"head": ["Quem recebe o `no`", "Faz"], "rows": [
   ["um servidor", "responde 503 com `Retry-After` — o cliente tenta depois"],
   ["um leitor de fila", "para de ler da fonte até a fila baixar"],
   ["um produtor de fibras", "usa um [canal](/docs/runtime/canais), que espera em vez de recusar"]]}},
 {"callout": {"tipo": "dica", "titulo": "Recusar é melhor que atrasar", "texto": "Um servidor que aceita tudo e responde em 30 s está mais quebrado que um que recusa metade e responde o resto em 50 ms: o cliente do primeiro já desistiu, e o trabalho foi feito para ninguém."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/falhas",
"title": "Quando algo falha no laço",
"description": "Um erro num retorno de chamada é contado, e não propagado: uma conexão ruim não derruba o servidor.",
"blocos": [
 {"p": "Num reator, todas as conexões dividem a mesma thread. Se um erro no tratamento de **uma** conexão subisse até o laço, derrubaria todas as outras. Por isso o erro é **anotado** e o laço segue — e as falhas ficam disponíveis para o log e para o teste."},
 {"code": '''adopt Arcane.Laco as L

laco := L.novo()
L.agendar(laco, lambda => 1 / 0)
atendidos := []
L.agendar(laco, lambda => atendidos.append("a outra conexão"))
L.apos(laco, 10, lambda => L.parar(laco))
L.rodar(laco)

assert atendidos is ["a outra conexão"]            // seguiu atendendo
f := L.falhas(laco)
assert len(f) is 1
out f[0]["erro"], f[0]["onde"]''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Contada, não esquecida", "texto": "Engolir o erro em silêncio seria o outro extremo. `L.falhas(laco)` guarda cada um, com onde aconteceu e o tipo; `estatisticas()[\"erros\"]` conta. Um teste que roda o laço e não confere `falhas` está conferindo metade."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/escolher",
"title": "Laço, thread, async ou processo",
"description": "Quatro modelos de concorrência, o que cada um resolve, e o GIL que decide metade da escolha.",
"blocos": [
 {"p": "A pergunta que decide o modelo não é \"quero paralelismo?\", e sim **\"o trabalho espera ou calcula?\"**. Esperar (rede, disco, banco) sobrepõe bem em uma thread; calcular exige núcleos de verdade, e no CPython isso quer dizer processos."},
 {"table": {"head": ["Modelo", "Serve para", "Custo", "Não serve para"], "rows": [
   ["`Arcane.Laco`", "milhares de conexões esperando", "1 thread, ~1 MB", "conta pesada (trava o laço)"],
   ["`thread:` / `parallel:`", "poucas esperas simultâneas, código simples", "~36 MB para mil threads", "milhares de conexões; conta pesada (GIL)"],
   ["`async` / `await`", "E/S concorrente com código sequencial", "uma thread por tarefa", "conta pesada (GIL)"],
   ["`P.map_processos`", "conta pesada em vários núcleos", "~50 ms de partida por processo", "trabalho pequeno (a partida domina)"],
   ["[ator](/docs/concorrencia/atores)", "estado que várias threads alteram", "1 thread por ator", "—"]]}},
 {"h2": "Medido"},
 {"table": {"head": ["Conexões", "Laço", "Thread por conexão"], "rows": [
   ["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"],
   ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
 {"p": "O tempo quase empata — e esse é o número honesto. O que muda é a **forma** da conta: a memória e as threads do laço ficam planas, e as do modelo por conexão crescem em linha reta até algo quebrar."},
 {"callout": {"tipo": "dica", "titulo": "Comece simples", "texto": "Um serviço com dezenas de pedidos por segundo roda bem no Kiln, uma thread por pedido. O laço vale quando as conexões ficam **abertas** e são muitas: WebSocket, chat, um coletor de telemetria."}},
]},
]
