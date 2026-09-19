"""O laço de eventos, o escalonador, as fibras — e o mapa da parte 12.

Todo bloco `df` destas páginas RODA (`tests/test_laco.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/laco",
"title": "O laço de eventos",
"description": "Uma thread dormindo no seletor do sistema em vez de uma thread por conexão — com o número medido: 2000 conexões, 1 thread, +0 MB.",
"blocos": [
 {"p": "O [`async/await`](/docs/tecnicas/concorrencia) desta linguagem é **uma thread por tarefa**. Serve para o que foi feito — sobrepor entrada e saída — e não escala: mil conexões simultâneas são mil threads do sistema. O [Kiln](/docs/kiln) atende **um pedido por thread** pelo mesmo motivo."},
 {"p": "O outro modelo é o **reator**: uma thread que dorme num seletor do sistema — `epoll` no Linux, `kqueue` no macOS e no BSD, `select` no Windows — e acorda quando algum descritor tem trabalho."},
 {"code": """adopt Arcane.Laco as L

laco := L.novo()
ordem := []

L.agendar(laco, lambda => ordem.append("agora"))
L.apos(laco, 30, lambda => ordem.append("depois"))
L.apos(laco, 10, lambda => ordem.append("antes"))
L.rodar(laco)

assert ordem is ["agora", "antes", "depois"]
assert L.mecanismo(laco) in ["epoll", "kqueue", "select", "poll"]""", "lang": "df"},
 {"p": "Quem foi agendado **depois** mas vence **antes** roda antes: a fila de prazos é um heap, não uma lista percorrida."},

 {"h2": "O número"},
 {"p": "Um servidor de linha, uma requisição por conexão, medido nesta máquina contra o mesmo servidor com uma thread por conexão:"},
 {"table": {"head": ["Conexões", "Laço de eventos", "Thread por conexão"], "rows": [
   ["400", "33 ms · **1 thread** · +0 MB", "43 ms · 400 threads · +14 MB"],
   ["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"],
   ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
 {"callout": {"tipo": "atencao", "titulo": "O tempo quase empata — e a memória é que conta a história", "texto": "Nesta máquina, duas mil threads ainda funcionam, e a diferença de tempo fica em ~1,1×. O que muda é a **forma da conta**: o custo do laço é plano (+0 MB), o do modelo de threads é linear (+36 MB, ~36 KB por thread). Num contêiner com limite de threads, ou com trabalho de verdade por conexão, um falha onde o outro nem percebe. Publicar o 1,1× é mais honesto que publicar só o caso em que o outro modelo já quebrou."}},

 {"h2": "Ele não gira em vão"},
 {"p": "É a diferença entre um reator e uma espera ocupada, e ela é **testada**: com um único temporizador a 200 ms, o laço dá menos de 50 voltas. Um laço de espera ocupada daria milhões, e queimaria um núcleo sem fazer nada."},
 {"code": """adopt Arcane.Laco as L

laco := L.novo()
L.apos(laco, 60, lambda => void)
L.rodar(laco)

// dormiu no seletor em vez de girar
assert L.estatisticas(laco)["voltas"] smaller 50""", "lang": "df"},

 {"h2": "Entrada e saída"},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`L.novo(teto?)`", "um laço; com `teto`, a fila de prontas recusa quando enche"],
   ["`L.rodar(laco)`", "gira até acabar o trabalho, ou até alguém chamar `parar`"],
   ["`L.agendar(laco, acao)`", "põe na fila; devolve `no` quando o teto recusa"],
   ["`L.apos(laco, ms, acao)`", "uma vez, depois do prazo"],
   ["`L.a_cada(laco, ms, acao)`", "repete até ser cancelado"],
   ["`L.quando_ler(laco, soquete, acao)`", "chama quando houver o que ler"],
   ["`L.quando_escrever(…)` · `L.esquecer(…)`", "o outro lado, e a saída do laço"],
   ["`L.executar(laco, trabalho, depois)`", "manda o que bloqueia para o pool"],
   ["`L.cancelar(t)` · `L.cancelada(t)`", "vale para tarefa e para fibra"],
   ["`L.mecanismo(laco)`", "`epoll`, `kqueue` ou `select` — o do sistema"],
   ["`L.estatisticas(laco)` · `L.falhas(laco)`", "voltas, tarefas, prazos, E/S, erros"]]}},

 {"h2": "Quando usar qual"},
 {"table": {"head": ["Precisa de", "Use"], "rows": [
   ["sobrepor duas ou três chamadas de rede", "[`async`/`await`](/docs/tecnicas/concorrencia) — mais simples, e o custo não aparece"],
   ["milhares de conexões abertas ao mesmo tempo", "**este módulo**"],
   ["usar mais de um núcleo de CPU", "[`P.map_processos`](/docs/concorrencia/mapa) — o laço é uma thread só, e o GIL continua no caminho"],
   ["servir HTTP com rota e template", "[Kiln](/docs/kiln) — ele é thread por pedido, e para a maioria dos casos isso basta"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/escalonador",
"title": "O escalonador",
"description": "Ordem, prazo, cancelamento, contrapressão, o executor para o que bloqueia — e o erro que não pode derrubar o servidor inteiro.",
"blocos": [
 {"p": "O laço tem três filas, e cada uma resolve um problema diferente."},
 {"table": {"head": ["Fila", "O que resolve"], "rows": [
   ["**poller** (`selectors`)", "dormir até haver E/S, em vez de girar"],
   ["**prazos** (heap)", "`apos` e `a_cada` sem uma thread por relógio"],
   ["**prontas**", "a ordem de execução, e onde a contrapressão mora"]]}},

 {"h2": "Contrapressão"},
 {"p": "Uma fila sem teto troca **falha visível** por **morte por memória** — que é muito pior de diagnosticar, porque acontece longe da causa. Com teto, `agendar` devolve `no` e quem chama decide o que fazer."},
 {"code": """adopt Arcane.Laco as L

laco := L.novo(2)                // teto de duas tarefas na fila

assert L.agendar(laco, lambda => void)
assert L.agendar(laco, lambda => void)
assert not L.agendar(laco, lambda => void)     // recusada, e diz que recusou
assert L.estatisticas(laco)["recusadas"] is 1""", "lang": "df"},

 {"h2": "Um erro não derruba o laço"},
 {"p": "Um reator que morre no primeiro erro derruba o servidor inteiro — e o erro costuma ser de **uma** conexão. Aqui ele é contado, guardado com o tipo e o texto, e o laço segue."},
 {"code": """adopt Arcane.Laco as L

laco := L.novo()
visto := []

L.agendar(laco, lambda => 1 / 0)
L.agendar(laco, lambda => visto.append("segui"))
L.rodar(laco)

assert visto is ["segui"]
assert L.estatisticas(laco)["erros"] is 1
assert L.falhas(laco)[0]["tipo"] is "DivisionByZeroError\"""", "lang": "df"},

 {"h2": "O que bloqueia vai para o pool"},
 {"p": "Esta é a peça que mais falta num reator escrito à mão. Um trabalho que bloqueia **dentro** do laço trava tudo — não só aquela tarefa, mas toda conexão aberta. `L.executar` manda para um pool de threads e devolve o resultado pela fila."},
 {"code": """adopt Arcane.Laco as L
adopt Arcane.Time as T

laco := L.novo()
marcas := []

action pesado():
    T.sleep(0.05)
    yield "pronto"

L.executar(laco, pesado, lambda r => marcas.append(r))
L.apos(laco, 10, lambda => marcas.append("tique"))
L.rodar(laco)

// o tique rodou ENQUANTO o trabalho pesado corria
assert marcas is ["tique", "pronto"]""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Agendar de outra thread acorda o laço", "texto": "É o que faz o `executar` funcionar, e é o truque clássico: um par de soquetes (*socketpair*) registrado no seletor. Sem ele o laço dorme e a tarefa fica na fila até o próximo temporizador — que pode não existir. Um seletor acorda por **descritor**, e uma fila em memória não é um descritor."}},

 {"h2": "O que NÃO existe"},
 {"table": {"head": ["Item", "Por quê"], "rows": [
   ["*work stealing* entre laços", "cada laço é uma thread; roubar tarefa entre eles exigiria fila sem trava e afinidade — e o GIL come o ganho antes de ele aparecer"],
   ["`io_uring`", "só Linux, e pelo CPython exigiria uma extensão em C — fora de uma linguagem sem dependência externa"],
   ["IOCP no Windows", "o `selectors` usa `select` ali, que tem teto de 512 descritores. É o limite do Windows nesta forma, e está dito"],
   ["prioridade por tarefa", "a fila é FIFO. Prioridade sem inversão de prioridade é mais difícil do que parece, e ninguém pediu ainda"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/fibras",
"title": "Fibras",
"description": "Um `stream action` suspenso em cada `emit` — corrotina de verdade, com a limitação sem pilha dita com esse nome.",
"blocos": [
 {"p": "Uma fibra aqui **não é aproximação**. Um `stream action` da linguagem já é um gerador do Python, e o interpretador suspende o corpo dele em cada `emit`. O escalonador dirige esse gerador: o valor emitido diz **o que a fibra está esperando**, e a troca de contexto é o quadro do gerador."},
 {"code": """adopt Arcane.Laco as L

stream action trabalhador(nome, diario):
    cycle i from 1 to 3:
        diario.append($"{nome}{i}")
        emit L.ceder()

laco := L.novo()
diario := []
L.fibra(laco, trabalhador, ["A", diario])
L.fibra(laco, trabalhador, ["B", diario])

assert L.fibras(laco) is 2
L.rodar(laco)

// intercaladas: e isto que prova o escalonamento cooperativo
assert diario is ["A1", "B1", "A2", "B2", "A3", "B3"]
assert L.fibras(laco) is 0""", "lang": "df"},
 {"p": "Se fossem sequenciais o diário seria `A1 A2 A3 B1 B2 B3`. Elas se intercalam porque cada `emit` devolve o controle ao escalonador, que escolhe a próxima."},

 {"h2": "O que uma fibra pode esperar"},
 {"table": {"head": ["Pedido", "Retoma quando"], "rows": [
   ["`L.ceder()`", "na próxima volta — cede sem esperar nada"],
   ["`L.dormir(ms)`", "passado o prazo, **sem prender thread nenhuma**"],
   ["`L.depois_de(ms, caixa, chave, valor)`", "passado o prazo, com o valor já na caixa"],
   ["`L.ler(soquete, caixa, chave)`", "houver o que ler; o dado chega pela caixa"],
   ["`L.escrever(soquete)`", "der para escrever sem bloquear"],
   ["`L.esperar(outra)`", "a outra fibra terminar"]]}},
 {"p": "A lista é **fechada**: um vault qualquer emitido por engano vira erro com a lista, e não uma fibra parada para sempre esperando algo que ninguém registrou."},

 {"h2": "A caixa, e por que ela existe"},
 {"p": "`emit` é **instrução**, não expressão: ele não devolve valor para a fibra. Então o laço entrega por um vault que a fibra passou — a **caixa**. Ser explícito aqui é melhor que fingir o contrário."},
 {"code": """adopt Arcane.Laco as L

stream action espera(caixa):
    emit L.depois_de(20, caixa, "resposta", "chegou")
    caixa["visto"] := caixa["resposta"]

laco := L.novo()
caixa := {"resposta": void, "visto": void}
L.fibra(laco, espera, [caixa])
L.rodar(laco)

assert caixa["visto"] is "chegou\"""", "lang": "df"},

 {"h2": "Sem pilha — e isso tem nome"},
 {"callout": {"tipo": "atencao", "titulo": "Um `emit` dentro de uma ação chamada NÃO suspende a fibra", "texto": "Só o `emit` do corpo da própria fibra suspende. É a limitação de toda corrotina **sem pilha** (*stackless*) — a mesma dos iteradores do C# e do `yield` do Python. Suspender dentro de uma chamada exige pilha própria, e isso quer dizer troca de contexto em assembly ou uma extensão em C: as duas fora de uma linguagem sem dependência externa. É por isso que esta página diz **fibra** e não *green thread*."}},

 {"h2": "Cancelar"},
 {"code": """adopt Arcane.Laco as L

stream action longa(diario):
    diario.append("comecei")
    emit L.dormir(50)
    diario.append("nao chega aqui")

laco := L.novo()
diario := []
f := L.fibra(laco, longa, [diario])
L.apos(laco, 5, lambda => L.cancelar(f))
L.rodar(laco)

assert diario is ["comecei"]
assert L.cancelada(f)""", "lang": "df"},
 {"p": "Cancelar uma fibra fecha o gerador — o que roda os `defer` do corpo, como um `halt` faria. Uma thread do sistema não se cancela assim: é a vantagem concreta de a fibra ser um objeto e não um recurso do SO."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/runtime/mapa",
"title": "O runtime: o mapa",
"description": "Item por item da parte 12 da referência Deep Tech — scheduler assíncrono, green threads e event loop — cruzado com o que o DataForge tem.",
"blocos": [
 {"p": "A décima segunda parte de uma referência Deep Tech é sobre a arquitetura do runtime. Foi a parte que escolhi fazer depois da 8 por um motivo: das que restavam, era **a única que muda o que a linguagem consegue fazer**, e não só o que ela documenta."},

 {"h2": "55 · Scheduler assíncrono"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["event loop", "`Arcane.Laco` — poller do sistema, fila de prazos, fila de prontas", "[O laço](/docs/runtime/laco)"],
   ["task scheduler, work queues", "`agendar`, `apos`, `a_cada`, com ordem FIFO e prazos num heap", "[Escalonador](/docs/runtime/escalonador)"],
   ["executors", "`L.executar` — o que bloqueia vai para um pool e volta pela fila", "[Escalonador](/docs/runtime/escalonador)"],
   ["cooperative scheduling", "as fibras: cada `emit` devolve o controle", "[Fibras](/docs/runtime/fibras)"],
   ["context switching", "o quadro do gerador; sem pilha própria e sem registrador a salvar", "[Fibras](/docs/runtime/fibras)"],
   ["cancellation", "`L.cancelar` vale para tarefa e para fibra; fechar o gerador roda os `defer`", "[Fibras](/docs/runtime/fibras)"],
   ["backpressure", "`L.novo(teto)` — a fila recusa em vez de crescer sem limite", "[Escalonador](/docs/runtime/escalonador)"],
   ["task stealing", "**não existe**: cada laço é uma thread, e com o GIL o ganho some antes de aparecer", "—"]]}},

 {"h2": "56 · Green threads"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["fibers", "existem, e são reais: um `stream action` dirigido pelo escalonador", "[Fibras](/docs/runtime/fibras)"],
   ["user-space scheduling", "o escalonador é o do módulo; o SO não sabe que há fibras", "[Fibras](/docs/runtime/fibras)"],
   ["context switching", "`next()` no gerador — o mais barato que há sem sair do Python", "[Fibras](/docs/runtime/fibras)"],
   ["scheduler integration", "a fibra diz o que espera, e o laço a registra no poller ou no heap", "[Fibras](/docs/runtime/fibras)"],
   ["stack management, register preservation", "**não existe**, e é a diferença entre *fibra* e *green thread*: a corrotina é **sem pilha**, e um `emit` dentro de uma ação chamada não suspende", "[Fibras](/docs/runtime/fibras)"],
   ["assembly-level switching", "**não se aplica** — exigiria assembly ou extensão em C, e a linguagem não tem dependência externa", "—"]]}},

 {"h2": "57 · Event loop"},
 {"table": {"head": ["Componente", "No DataForge", "Onde"], "rows": [
   ["I/O Poller", "`selectors.DefaultSelector` — o melhor que o sistema oferece", "[O laço](/docs/runtime/laco)"],
   ["Timer Queue", "heap de prazos, com desempate estável", "[Escalonador](/docs/runtime/escalonador)"],
   ["Task Queue", "fila FIFO com teto opcional", "[Escalonador](/docs/runtime/escalonador)"],
   ["Executor", "pool de threads para o que bloqueia", "[Escalonador](/docs/runtime/escalonador)"],
   ["Reactor, Scheduler", "são o mesmo objeto: `Laco`", "[O laço](/docs/runtime/laco)"],
   ["**epoll**", "no Linux, automaticamente", "[O laço](/docs/runtime/laco)"],
   ["**kqueue**", "no macOS e no BSD, automaticamente", "[O laço](/docs/runtime/laco)"],
   ["IOCP", "**não**: no Windows o `selectors` usa `select`, com teto de 512 descritores. É o limite desta forma, e está dito em vez de escondido", "—"],
   ["io_uring", "**não existe**: só Linux, e pelo CPython exigiria extensão em C", "—"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das três seções, **duas estão inteiras** (§55 e §57, menos *work stealing*, IOCP e `io_uring`) e a terceira está pela metade — pela metade **certa**: as fibras existem e funcionam, e o que falta delas (pilha própria) é exatamente o que exigiria sair do Python."},
 {"callout": {"tipo": "nota", "titulo": "O que esta parte entregou à linguagem", "texto": "Um módulo (`Arcane.Laco`), um modelo de concorrência que o `async/await` não cobria, fibras de verdade sobre uma máquina que **já existia** no interpretador — e um número: **2000 conexões numa thread, com +0 MB**, contra 2000 threads e +36 MB. A parte 8 tinha entregado a lição oposta (a otimização que rendeu 1,01×); esta rendeu, e a diferença entre as duas é que aqui o modelo mudou, não a constante."}},
]},
]
