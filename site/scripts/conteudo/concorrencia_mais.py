# -*- coding: utf-8 -*-
"""Concorrência — a página-raiz (que respondia 404) e sete páginas:
atores, canais entre threads, travas, condição de corrida, impasse,
processos e os padrões que juntam tudo.

`P.ator` entrou nesta leva. Os números de corrida vêm do CLAUDE.md, e
foram medidos: 40.425 de 80.000 sem trava, 20.000 de 20.000 com ator.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia",
"title": "Concorrência",
"description": "Threads, atores, canais, travas, STM e processos — e a regra que decide qual: quem pode escrever neste estado?",
"blocos": [
 {"p": "A linguagem **não sincroniza sozinha**. Duas threads escrevendo na mesma variável perdem atualizações — medido: 40.425 de 80.000, calado. Toda ferramenta desta seção responde de um jeito à mesma pergunta: **quem pode escrever neste estado, e quando?**"},
 {"code": '''adopt Arcane.Concurrent as P

// um ator: o estado mora numa thread, e as outras só enviam
contador := P.ator(lambda n, m: n + m, 0)
action somar_muito():
    cycle i from 1 to 500:
        contador.enviar(1)
parallel:
    somar_muito()
    somar_muito()
assert contador.parar() is 1000          // nenhuma atualização perdida''', "lang": "df"},
 {"table": {"head": ["Resposta", "Ferramenta", "Página"], "rows": [
   ["ninguém: cada um tem o seu", "variável por thread", "[Uma por thread](/docs/partida/por-thread)"],
   ["só um dono, por mensagem", "**ator**", "[Atores](/docs/concorrencia/atores)"],
   ["passa de mão em mão", "canal", "[Canais](/docs/concorrencia/canais)"],
   ["qualquer um, um de cada vez", "mutex, semáforo", "[Travas](/docs/concorrencia/travas)"],
   ["qualquer um, junto ou nada", "STM", "[Memória transacional](/docs/concorrencia/stm)"],
   ["ninguém compartilha memória", "processos", "[Processos](/docs/concorrencia/processos)"]]}},
 {"cards": [
   {"href": "/docs/concorrencia/atores", "title": "Atores", "desc": "estado com dono, alcançado por mensagem"},
   {"href": "/docs/concorrencia/canais", "title": "Canais entre threads", "desc": "o produtor que espera, e o fechar"},
   {"href": "/docs/concorrencia/travas", "title": "Travas", "desc": "mutex, semáforo, leitura e escrita"},
   {"href": "/docs/concorrencia/corridas", "title": "Condição de corrida", "desc": "o ler-somar-escrever, medido"},
   {"href": "/docs/concorrencia/impasse", "title": "Impasse", "desc": "duas travas em ordens diferentes"},
   {"href": "/docs/concorrencia/processos", "title": "Processos", "desc": "o único caminho para mais de um núcleo"},
   {"href": "/docs/concorrencia/padroes", "title": "Padrões", "desc": "produtor-consumidor, pool, espalhar e juntar"},
   {"href": "/docs/concorrencia/stm", "title": "Memória transacional", "desc": "escritas que acontecem juntas"},
   {"href": "/docs/concorrencia/sem-trava", "title": "Atômicos e sem trava", "desc": "contador, anel e pilha"},
   {"href": "/docs/runtime/escolher", "title": "Laço, thread, async ou processo", "desc": "qual modelo para qual trabalho"},
   {"href": "/docs/concorrencia/mapa", "title": "Concorrência: o mapa", "desc": "o que existe, e o que não"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/atores",
"title": "Atores",
"description": "P.ator: o estado mora numa thread, as mensagens chegam numa fila, e o erro de uma mensagem não derruba o ator.",
"blocos": [
 {"p": "A trava protege o estado **se** todo mundo lembrar de tomá-la. O ator tira a escolha: o estado mora numa thread própria, e as outras não têm como tocá-lo — só **enviar** uma mensagem. As mensagens entram numa fila e são tratadas uma de cada vez, na ordem de chegada. O ler-modificar-escrever que perde atualização não tem como acontecer."},
 {"code": '''adopt Arcane.Concurrent as P

action conta(saldo, msg):
    given msg["tipo"] is "sacar" and msg["valor"] bigger saldo:
        trigger "saldo insuficiente"
    yield saldo + msg["valor"] given msg["tipo"] is "depositar" otherwise saldo - msg["valor"]

caixa := P.ator(conta, 100, "caixa")
caixa.enviar({"tipo": "depositar", "valor": 50})
caixa.enviar({"tipo": "sacar", "valor": 500})          // recusado — o ator segue
caixa.enviar({"tipo": "sacar", "valor": 30})

assert caixa.consultar(lambda saldo: saldo) is 120
assert len(caixa.falhas()) is 1
out caixa.falhas()[0]["erro"]''', "lang": "df"},
 {"table": {"head": ["Método", "Faz"], "rows": [
   ["`enviar(msg)`", "põe na fila e volta na hora — não espera o tratamento"],
   ["`consultar(acao, prazo)`", "roda `acao(estado)` **dentro** do ator, na fila, e devolve o resultado"],
   ["`parar()`", "trata o que já está na fila, para, e devolve o estado final"],
   ["`falhas()`", "as mensagens que levantaram, com o erro"],
   ["`pendentes()` · `processadas()` · `vivo()`", "o estado da fila"]]}},
 {"h2": "A consulta entra na fila"},
 {"p": "`consultar` não lê o estado de fora — isso seria a corrida de volta. Ela entra na **mesma** fila das mensagens, e por isso vê o estado depois de tudo que foi enviado antes dela, e nunca no meio de uma mensagem."},
 {"h2": "O erro não derruba o ator"},
 {"p": "Uma mensagem que levanta é anotada, e o ator **segue com o estado de antes** — a estratégia \"retomar\" dos supervisores do Erlang e do Akka. Um ator que morresse na primeira mensagem ruim derrubaria tudo que depende dele por causa de uma mensagem. Para reagir à falha, `P.ator(comportamento, estado, nome, ao_falhar)`."},
 {"callout": {"tipo": "atencao", "titulo": "Uma thread por ator", "texto": "Cada ator é uma thread do sistema. Dezenas de atores, tudo bem; um por usuário de um sistema com cem mil usuários, não. Para muitas entidades pequenas, um ator por **partição** (por exemplo, por hash do id) com um vault dentro."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/canais",
"title": "Canais entre threads",
"description": "P.canal: receber espera, o produtor rápido para quando a fila enche, e fechar termina o consumidor.",
"blocos": [
 {"p": "Um canal é uma fila entre threads com duas garantias: quem **recebe** espera até chegar algo, e — com capacidade — quem **envia** espera quando a fila enche. A segunda é a que protege a memória: um produtor mais rápido que o consumidor para no `enviar`, em vez de acumular um milhão de itens."},
 {"code": '''adopt Arcane.Concurrent as P

tarefas := P.canal(2)
feitas := []

action produzir():
    cycle i from 1 to 5:
        tarefas.enviar(i)
    tarefas.fechar()

action consumir():
    persist yes:
        t := tarefas.receber()
        given t is void:                  // fechado e vazio
            halt
        feitas.append(t * 10)

parallel:
    produzir()
    consumir()
assert feitas is [10, 20, 30, 40, 50]''', "lang": "df"},
 {"list": [
   "**`receber(prazo)`** desiste depois do prazo, em vez de esperar para sempre por um produtor que morreu.",
   "**`tentar_receber()`** não espera: `void` se estiver vazio.",
   "**Entre fibras de um laço**, o canal é outro — o que suspende a fibra, e não a thread: ver [Canais entre fibras](/docs/runtime/canais)."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/travas",
"title": "Travas",
"description": "Mutex para um de cada vez, semáforo para N de cada vez, e com_trava para não esquecer de soltar.",
"blocos": [
 {"p": "Uma trava transforma um trecho em **seção crítica**: só uma thread por vez passa. É a ferramenta mais direta — e a que mais depende de disciplina: toda escrita no estado protegido precisa estar dentro dela, em todo lugar do programa."},
 {"code": '''adopt Arcane.Concurrent as P

trava := P.mutex()
total := {"n": 0}

action somar_muito():
    cycle i from 1 to 1000:
        P.com_trava(trava, lambda => incrementar())

action incrementar():
    total["n"] := total["n"] + 1

parallel:
    somar_muito()
    somar_muito()
assert total["n"] is 2000''', "lang": "df"},
 {"table": {"head": ["Trava", "Deixa passar", "Uso"], "rows": [
   ["`P.mutex()`", "uma thread por vez (reentrante)", "proteger um estado compartilhado"],
   ["`P.semaforo(n)`", "até N ao mesmo tempo", "limitar conexões a um serviço externo"],
   ["`P.trava_leitura_escrita()`", "muitos leitores, **ou** um escritor", "cache lido o tempo todo e escrito raramente"],
   ["`P.com_trava(trava, acao)`", "—", "toma, roda, e **solta mesmo com erro**"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Tomar e soltar à mão", "texto": "Funciona até o corpo levantar: a trava fica tomada, e a próxima thread espera para sempre. `com_trava` solta no `finally`. Se você se pegar tomando uma trava à mão, é o momento de usar `com_trava` — ou um [ator](/docs/concorrencia/atores), que não tem trava para esquecer."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/corridas",
"title": "Condição de corrida",
"description": "Ler, somar e escrever não é uma operação — e duas threads fazendo isso perdem metade das somas, caladas.",
"blocos": [
 {"p": "`v[\"n\"] := v[\"n\"] + 1` parece uma operação e são três: **ler**, somar, **escrever**. Entre o ler e o escrever de uma thread, outra thread lê o mesmo valor velho — e as duas escrevem o mesmo resultado. Uma soma some, sem erro nenhum."},
 {"table": {"head": ["Operação, 4 threads", "Esperado", "Medido"], "rows": [
   ["`v[\"n\"] := v[\"n\"] + 1` sem trava", "40.000", "**33.740**"],
   ["`xs.append(i)` sem trava", "20.000", "20.000 — o GIL protege a operação inteira"],
   ["com `P.mutex` ou `P.ator`", "20.000", "20.000"]]}},
 {"p": "O `append` sozinho não perde porque é **uma** operação do interpretador, protegida pelo GIL. O que perde é o que **lê para decidir o que escrever**: `+= 1`, `pop`, `remove`, `insert`, `sort`. É essa a lista que o `check` usa."},
 {"h2": "O check avisa"},
 {"code": '''adopt Arcane.Process as Proc
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-corrida-{randint(100000, 999999)}"
IO.mkdir(pasta)
arquivo := $"{pasta}/corrida.df"
IO.write(arquivo, "total := {\\"n\\": 0}\\nparallel:\\n    total[\\"n\\"] := total[\\"n\\"] + 1\\n    total[\\"n\\"] := total[\\"n\\"] + 1\\n")

// o 'check' do mesmo Python que roda este programa — e não um do PATH
r := Proc.run([OS.executable(), "-m", "dataforge", "check", arquivo])
saida := r["stdout"] + r["stderr"]
assert saida.contains("corrida.df:3") and saida.contains("'total'")   // o aviso, na linha certa
IO.remove_tree(pasta)''', "lang": "df"},
 {"p": "`dataforge check` num arquivo assim avisa `escrita-concorrente`: um `thread`, `parallel` ou **`route`** escrevendo num nome que vem de fora. A rota é o caso que mais importa, porque o Kiln atende cada pedido numa thread, e ali a concorrência é **invisível** — quem escreve a rota não vê thread nenhuma. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram 1 de 6."},
 {"callout": {"tipo": "dica", "titulo": "É aviso, e não erro", "texto": "Um acumulador protegido por mutex passa pelo aviso igual — a análise não segue a chamada até o `com_trava`. Recusar proibiria o uso correto; avisar deixa quem escreveu decidir, com `// df: permitir escrita-concorrente` quando a proteção existe."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/impasse",
"title": "Impasse",
"description": "Duas threads, duas travas, em ordens diferentes: cada uma segura o que a outra espera. A ordem fixa, e o prazo.",
"blocos": [
 {"p": "A thread 1 toma a trava do estoque e espera a do caixa; a thread 2 tomou a do caixa e espera a do estoque. As duas ficam paradas **para sempre**, vivas e caladas — é o **impasse** (*deadlock*). O processo não cai, não levanta, não escreve no log: simplesmente para de responder."},
 {"h2": "A cura: sempre a mesma ordem"},
 {"p": "O impasse precisa de duas threads pedindo travas em ordens **diferentes**. Se toda thread toma as travas na mesma ordem — por exemplo, sempre a do estoque antes da do caixa —, o ciclo não tem como se formar:"},
 {"code": '''adopt Arcane.Concurrent as P

estoque := P.mutex()
caixa := P.mutex()
vendas := []

// A regra do programa: estoque ANTES de caixa, em todo lugar
action vender(item):
    P.com_trava(estoque, lambda => P.com_trava(caixa, lambda => vendas.append(item)))

parallel:
    vender("café")
    vender("chá")
assert len(vendas) is 2''', "lang": "df"},
 {"h2": "O prazo, para não travar calado"},
 {"code": '''adopt Arcane.Concurrent as P

esgotou := no
monitor:
    P.com_prazo(lambda => sleep(500), 0.05)       // quem chama não fica preso
handle Error as e:
    esgotou := yes
assert esgotou''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O prazo não interrompe", "texto": "`com_prazo` garante que **quem chamou** volta; a ação continua rodando em segundo plano, porque o Python não mata uma thread de fora sem arriscar deixar estado pela metade. Serve para não travar o chamador — e o log do prazo esgotado é o que aponta o impasse."}},
 {"p": "Com um [ator](/docs/concorrencia/atores) não há travas para ordenar, e com [STM](/docs/concorrencia/stm) o conflito vira nova tentativa — as duas formas evitam o impasse por construção."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/processos",
"title": "Processos",
"description": "O único caminho para mais de um núcleo no CPython — o que atravessa, o que custa, e o pool que paga a partida uma vez.",
"blocos": [
 {"p": "Duas threads do CPython nunca executam código Python ao mesmo tempo — o **GIL** alterna entre elas. Para conta pesada, threads não ajudam: 8 blocos de CPU em 10 núcleos levaram 1607 ms em série e 1654 ms em threads. Em **processos**, 466 ms: 3,45× mais rápido."},
 {"code": '''adopt Arcane.Concurrent as P

action pesado(n):
    total := 0
    cycle i from 1 to n:
        total += i * i
    yield total

resultados := P.map_processos(pesado, [1000, 2000, 3000])
assert resultados[0] is 333833500                  // na ordem da entrada''', "lang": "df"},
 {"h2": "O que atravessa"},
 {"p": "Um processo não vê a memória do outro. O que vai é a **declaração** da ação — a árvore, os parâmetros, os records e blueprints que ela usa — e os dados, copiados. Uma conexão de banco ou um arquivo aberto não atravessam: abra do lado de lá."},
 {"table": {"head": ["Use", "Quando"], "rows": [
   ["`P.map`", "trabalho que **espera** (rede, disco): threads bastam"],
   ["`P.map_processos`", "conta pesada, uma vez"],
   ["`P.pool_processos()`", "conta pesada **repetida**: a partida (~100 ms) é paga uma vez"],
   ["nada disso", "trabalho pequeno: a partida de um processo custa mais que a conta"]]}},
 {"p": "O detalhe completo — o que é copiado, a nota de erro que diz que ele aconteceu no outro processo, o `forkserver` — está em [Paralelismo](/docs/tecnicas/processos)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/padroes",
"title": "Padrões de concorrência",
"description": "Produtor-consumidor, pool de trabalhadores, espalhar e juntar — montados com as peças da biblioteca.",
"blocos": [
 {"h2": "Pool de trabalhadores"},
 {"p": "N trabalhadores tirando tarefas de um canal: o número de trabalhadores limita quantas rodam ao mesmo tempo — o que protege o serviço externo que eles chamam."},
 {"code": '''adopt Arcane.Concurrent as P

fila := P.canal()
resultados := P.ator(lambda acc, r: acc + [r], [])

action trabalhador():
    persist yes:
        t := fila.receber()
        given t is void:
            halt
        resultados.enviar(t * t)

action alimentar():
    cycle i from 1 to 6:
        fila.enviar(i)
    fila.fechar()

parallel:
    alimentar()
    trabalhador()
    trabalhador()
    trabalhador()
assert sorted(resultados.parar()) is [1, 4, 9, 16, 25, 36]''', "lang": "df"},
 {"h2": "Espalhar e juntar"},
 {"p": "Muitas chamadas independentes ao mesmo tempo, e o resultado de todas na ordem da entrada — `P.map` faz os dois, com um teto de trabalhadores:"},
 {"code": '''adopt Arcane.Concurrent as P

action buscar_preco(item):
    sleep(10)                         // a rede
    yield len(item) * 10

precos := P.map(buscar_preco, ["café", "chá", "açúcar"], 3)
assert precos is [40, 30, 60]         // na ordem da entrada, não da chegada''', "lang": "df"},
 {"table": {"head": ["Padrão", "Peças"], "rows": [
   ["produtor-consumidor", "`P.canal(n)` — a capacidade é a contrapressão"],
   ["pool de trabalhadores", "canal + N threads + um ator para os resultados"],
   ["espalhar e juntar", "`P.map(acao, itens, trabalhadores)`"],
   ["estado disputado", "`P.ator`"],
   ["várias escritas que andam juntas", "`Arcane.Stm`"]]}},
]},
]
