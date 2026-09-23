# -*- coding: utf-8 -*-
"""Concorrência — seis páginas novas: contrapressão, prazo e cancelamento,
paralelismo de dados, o que da biblioteca dá para compartilhar, medir sem
inventar ganho, e depurar uma corrida.

Todo bloco roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/contrapressao",
"title": "Contrapressão",
"description": "Quando o produtor é mais rápido que o consumidor — e por que uma fila sem teto é uma falha adiada.",
"blocos": [
 {"p": "Todo sistema com produtor e consumidor tem uma pergunta que precisa de resposta: **o que acontece quando o produtor é mais rápido?** Há três respostas possíveis, e escolher por omissão significa escolher a pior."},
 {"table": {
   "head": ["Resposta", "O que custa", "Quando serve"],
   "rows": [
     ["a fila cresce sem teto", "**morte por memória**, horas depois", "nunca — é a escolha por omissão"],
     ["o produtor **espera**", "a lentidão sobe para quem produz", "quase sempre: é a contrapressão"],
     ["descarta o mais velho", "perde dado, de propósito e visivelmente", "telemetria, métrica, quadro de vídeo"]]}},
 {"code": '''adopt Arcane.Concurrent as C

// Um canal com TETO: o 'enviar' espera quando ele está cheio, e é
// isso que faz a lentidão do consumidor chegar ao produtor.
canal := C.canal(3)

produzidos := []
action produtor():
    cycle i from 1 to 5:
        canal.enviar(i)
        produzidos.append(i)
    canal.fechar()

action consumidor():
    recebidos := []
    cycle item in canal:
        recebidos.append(item)
        sleep(10)
    yield recebidos

resultado := void
parallel:
    produtor()
    thread:
        resultado := consumidor()

assert resultado is [1, 2, 3, 4, 5]
out $"produziu {len(produzidos)}, consumiu {len(resultado)} — sem perder nada"''', "lang": "df"},
 {"h2": "A fila sem teto é uma falha adiada"},
 {"p": "Ela não dá erro: ela funciona em todos os testes, porque num teste o consumidor acompanha. Em produção, a fila cresce nas horas de pico, a memória acaba de madrugada, e o processo é morto pelo sistema — sem mensagem, e longe da causa."},
 {"code": '''adopt Arcane.Concurrent as C

// Um teto pequeno, de propósito, para a espera aparecer:
canal := C.canal(1)
canal.enviar("a")
assert canal.cheio() is yes

// 'tentar_enviar' NÃO espera: ele devolve no quando não cabe. É o que
// permite ao produtor decidir — esperar, descartar ou contar.
assert canal.tentar_enviar("b") is no

descartados := 0
given not canal.tentar_enviar("c"):
    descartados += 1
assert descartados is 1
out "cheio: o produtor decide o que fazer, em vez de a memória decidir"''', "lang": "df"},
 {"h2": "Descartar, quando descartar é a resposta certa"},
 {"p": "Para telemetria, a leitura de trinta segundos atrás **não tem valor**: mandar a mais nova e perder a velha é melhor que atrasar as duas. O importante é que isso seja uma decisão escrita, e **contada**:"},
 {"code": '''adopt Arcane.Concurrent as C

blueprint Telemetria:
    action setup(teto):
        self.canal := C.canal(teto)
        self.descartados := 0

    action medir(valor):
        given not self.canal.tentar_enviar(valor):
            // Contar o descarte é o que separa "escolha" de "defeito":
            // sem o número, ninguém sabe que está perdendo dado.
            self.descartados := self.descartados + 1
            yield no
        yield yes

t := spawn Telemetria(2)
assert t.medir(1) is yes
assert t.medir(2) is yes
assert t.medir(3) is no
assert t.descartados is 1
out $"descartados: {t.descartados} — e o número aparece no painel"''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O canal do laço de eventos tem o mesmo teto", "texto": "`Arcane.Laco` aceita um teto na fila de prontas pelo mesmo motivo: sem ele, uma fonte mais rápida que o consumo troca uma falha visível por morte por memória. A escolha é sempre entre falhar cedo e falhar tarde."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/prazo",
"title": "Prazo e cancelamento",
"description": "Esperar para sempre é o defeito mais comum de código concorrente — e cancelar é mais difícil do que parece.",
"blocos": [
 {"p": "Uma espera sem prazo não dá erro: ela **trava**. E um travamento não tem linha, não tem mensagem e não aparece em log — só um processo que consome zero CPU e não responde."},
 {"code": '''adopt Arcane.Concurrent as C

// 'com_prazo' recebe SEGUNDOS, e LEVANTA quando o tempo acaba —
// um prazo que devolvesse void calado seria indistinguível de um
// trabalho que devolveu void.
action demorado():
    sleep(300)
    yield "pronto"

monitor:
    C.com_prazo(demorado, 0.05)
    assert no
handle Error as e:
    out e.message

action rapido():
    yield "pronto"

assert C.com_prazo(rapido, 2) is "pronto"
out "o prazo transforma um travamento numa decisão"''', "lang": "df"},
 {"h2": "O `receive` sem prazo NÃO espera"},
 {"p": "É contrato da linguagem, e o contrário do que quase todo mundo supõe: sem argumento, ele devolve `void` na hora se a fila está vazia. Trocar o padrão não daria erro em programa nenhum — daria **travamento**:"},
 {"code": '''adopt Arcane.Concurrent as C

canal := C.canal(4)

// vazio, e sem prazo: volta na hora
assert canal.tentar_receber() is void

canal.enviar("x")
assert canal.receber() is "x"
out "sem prazo, ele não espera — e é isso que evita o travamento calado"''', "lang": "df"},
 {"h2": "Cancelar é cooperativo"},
 {"p": "Não há como matar uma thread por fora sem deixar o estado pela metade — um `kill` no meio de uma escrita é como desligar a máquina no meio de um `write`. O que existe é **pedir**, e o trabalho conferir:"},
 {"code": '''adopt Arcane.Concurrent as C

blueprint Trabalho:
    action setup():
        self.cancelado := no
        self.feitos := 0

    action cancelar():
        self.cancelado := yes

    action rodar(quantos):
        cycle i from 1 to quantos:
            // A conferência é do TRABALHO, e ela acontece entre as
            // unidades — nunca no meio de uma.
            given self.cancelado:
                yield "cancelado"
            self.feitos := self.feitos + 1
        yield "terminou"

t := spawn Trabalho()
t.cancelar()
assert t.rodar(1000) is "cancelado"
assert t.feitos is 0
out "cancelar é pedir, e o trabalho confere entre as unidades"''', "lang": "df"},
 {"h2": "Os quatro pontos onde conferir o cancelamento"},
 {"list": [
   "**Entre itens de um laço** — o mais comum, e o mais barato.",
   "**Antes de começar** uma unidade cara: começar para cancelar depois é desperdício puro.",
   "**Depois de uma espera** — quem esperou dez segundos pode ter sido cancelado no meio deles.",
   "**Nunca no meio de uma escrita** — uma transação pela metade é pior que um trabalho a mais."]},
 {"h2": "O prazo de quem espera, e o prazo de quem faz"},
 {"p": "São dois prazos diferentes, e confundi-los custa caro: quem **espera** desiste e segue a vida; quem **faz** continua fazendo. Sem cancelamento, um prazo de cliente só troca um travamento por um vazamento — o trabalho continua, ninguém lê o resultado, e o recurso fica preso."},
 {"code": '''adopt Arcane.Concurrent as C

estado := {"terminou": no}

action trabalho():
    sleep(120)
    estado["terminou"] := yes
    yield "pronto"

// Quem espera desiste em 30 ms…
monitor:
    C.com_prazo(trabalho, 0.03)
handle Error:
    out "desisti de esperar"

// …e o trabalho CONTINUA rodando: o prazo é de quem espera.
sleep(250)
assert estado["terminou"] is yes
out "o prazo não cancela o trabalho — quem cancela é o cancelamento"''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/dados",
"title": "Paralelismo de dados",
"description": "Dividir a coleção, e o tamanho do bloco que decide se vale a pena.",
"blocos": [
 {"p": "O caso mais comum de concorrência não é um servidor: é **uma coleção grande e a mesma conta para cada item**. Aqui o modelo importa mais que em qualquer outro lugar, porque a resposta muda conforme o trabalho é de E/S ou de CPU."},
 {"table": {
   "head": ["O trabalho é", "Use", "Porque"],
   "rows": [
     ["rede, disco, banco", "`C.map` (threads)", "o GIL é solto na espera — a sobreposição é real"],
     ["conta pura", "`C.map_processos`", "o GIL serializa threads; processos usam núcleos"],
     ["mistura", "meça os dois", "a intuição erra aqui mais que em qualquer outra parte"],
     ["menos de ~10 ms por item", "nenhum dos dois", "a partida custa mais que o trabalho"]]}},
 {"code": '''adopt Arcane.Concurrent as C

action dobrar(x):
    yield x * 2

// 'map' roda a ação sobre a coleção em threads, e devolve NA ORDEM
// da entrada — o resultado não depende de quem terminou primeiro.
assert C.map(dobrar, [1, 2, 3, 4, 5]) is [2, 4, 6, 8, 10]

// E a ordem se mantém mesmo quando os itens terminam fora de ordem:
action devagar_se_par(x):
    given x % 2 is 0:
        sleep(20)
    yield x

assert C.map(devagar_se_par, [1, 2, 3, 4]) is [1, 2, 3, 4]
out "a ordem da saída é a da entrada, e isso não é acidente"''', "lang": "df"},
 {"h2": "O tamanho do bloco"},
 {"p": "Mandar um item por vez para outro processo faz o **transporte** dominar: cada item atravessa a fronteira, e a conta de um item é mais barata que a cópia dele. Blocos resolvem isso:"},
 {"code": '''adopt Arcane.Concurrent as C

action somar_bloco(bloco):
    // A ação recebe uma LISTA por vez, e não um item.
    yield bloco >> distill a, v: a + v 0

// 'lotes' faz as duas coisas: quebra em blocos do tamanho pedido e
// roda a ação sobre cada bloco. Um trabalho por BLOCO, e não por
// item — é o que impede o transporte de dominar a conta.
parciais := C.lotes(somar_bloco, [i cycle i in range(1, 11)], 4)
assert len(parciais) is 3
assert (parciais >> distill a, v: a + v 0) is 55
out $"{len(parciais)} blocos, soma {parciais >> distill a, v: a + v 0}"''', "lang": "df"},
 {"h2": "Quando não vale a pena"},
 {"code": '''adopt Arcane.Bench as B

action trivial(x):
    yield x + 1

// A regra prática: se o item custa menos que a partida, a série
// ganha. Medir é a única forma de saber de que lado você está.
action duzentos():
    yield [trivial(i) cycle i in range(0, 200)]

serie := B.medir(duzentos)
assert serie["ms"] >= 0
out $"200 itens triviais em série: {round(serie['ms'], 2)} ms"
out "com threads isso ficaria MAIS lento — a partida domina"''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O erro de medida que mais engana", "texto": "Comparar paralelo com série medindo **tempo absoluto** mede a máquina, não o paralelismo — e um runner de três núcleos reprova um código correto. A trava deste repositório cobra um **fator**, e quando nem isso basta há o ponto de calibração: um algoritmo conhecidamente linear medido no mesmo instante."}},
 {"h2": "Espalhar e juntar, com falha"},
 {"code": '''adopt Arcane.Concurrent as C

action pode_falhar(x):
    given x is 3:
        trigger $"o item {x} falhou"
    yield x * 10

// 'esperar_todas' junta os resultados; a falha de um item vira erro
// do conjunto, e não um buraco silencioso no meio da lista.
monitor:
    C.map(pode_falhar, [1, 2, 3, 4])
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"p": "Um `map` que devolvesse `void` no lugar do item que falhou parece conveniente e é a origem do pior tipo de defeito: o resultado tem o tamanho certo, a soma está errada, e não há erro em lugar nenhum."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/biblioteca",
"title": "O que dá para compartilhar",
"description": "Quais peças da biblioteca aguentam duas threads — e quais não, com o número medido.",
"blocos": [
 {"p": "A pergunta prática de todo programa concorrente: **isto aqui pode ser tocado por duas threads?** A resposta não é uniforme, e supor que é dá os dois erros — travar o que não precisa, e compartilhar o que não pode."},
 {"table": {
   "head": ["Peça", "Compartilhar?", "Observação"],
   "rows": [
     ["`Cluster.append`", "**sim**", "medido: 20.000 de 20.000 com quatro threads — o GIL protege a operação inteira"],
     ["`v[\"n\"] := v[\"n\"] + 1`", "**não**", "medido: 33.740 de 40.000 — ler-modificar-escrever não é atômico"],
     ["`remove`, `pop`, `insert`, `sort`", "**não**", "elas **leem para decidir** o que escrever"],
     ["`Arcane.Database`", "sim", "o módulo serializa o acesso à conexão"],
     ["uma conexão de banco crua", "**não**", "e ela não atravessa processo — ver a travessia"],
     ["`Arcane.Stm`", "sim", "é o ponto dele"],
     ["um `record`", "sim", "imutável"],
     ["uma instância de `blueprint`", "**não**", "estado mutável sem trava"]]}},
 {"code": '''adopt Arcane.Concurrent as C

// 'append' de quatro threads: o GIL protege a operação inteira.
lista := []
action empilhar():
    cycle i from 1 to 2000:
        lista.append(i)

parallel:
    empilhar()
    empilhar()
    empilhar()
    empilhar()

assert len(lista) is 8000
out $"append: {len(lista)} de 8000 — nenhum perdido"''', "lang": "df"},
 {"h2": "E o que o `check` avisa"},
 {"p": "O analisador **avisa** (`escrita-concorrente`) quando um `thread`, um `parallel` ou uma `route` escreve num nome que vem de fora — inclusive na forma `v[\"n\"] := …`, que é a que mais engana. A lista de métodos que disparam o aviso foi **medida**, e não presumida: `append` ficou de fora de propósito, porque avisar sobre ele seria falso alarme em código que funciona."},
 {"code": '''adopt Arcane.Concurrent as C

// A forma protegida passa pelo aviso igual — e está certa. O aviso é
// aviso, e não erro: recusar proibiria o uso correto com mutex.
trava := C.mutex()
contador := {"n": 0}

action somar_um():
    contador["n"] := contador["n"] + 1
    yield yes

action muitas():
    cycle i from 1 to 2000:
        C.com_trava(trava, somar_um)

parallel:
    muitas()
    muitas()
    muitas()
    muitas()

assert contador["n"] is 8000
out $"com mutex: {contador['n']} de 8000"''', "lang": "df"},
 {"h2": "A rota é o caso que mais importa"},
 {"p": "O Kiln atende **um pedido por thread**, e ali a concorrência é **invisível**: quem escreve a rota não vê thread nenhuma. Medido neste repositório: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."},
 {"code": '''adopt Arcane.Concurrent as C
adopt Arcane.Kiln as Kiln

// O estado de uma rota, protegido — porque duas rotas rodam juntas.
trava := C.mutex()
visitas := {"n": 0}

action contar():
    visitas["n"] := visitas["n"] + 1
    yield visitas["n"]

action rota_home(req):
    yield Kiln.json({"visitas": C.com_trava(trava, contar)})

app := Kiln.app()
Kiln.get(app, "/", rota_home)

primeira := Kiln.test(app, "GET", "/")
assert primeira["status"] is 200
out "o estado da rota mora fora dela, e a trava é de quem escreve"''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "A análise para na fronteira da ação", "texto": "Seguir a chamada exigiria um grafo, e um aviso que depende disso seria impreciso nos dois sentidos. Por isso ele olha o corpo do `thread`/`parallel`/`route` e para ali — e por isso é aviso."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/medir",
"title": "Medir sem inventar ganho",
"description": "As três formas de um teste de concorrência medir a máquina em vez do código.",
"blocos": [
 {"p": "Concorrência é a área onde a medida engana mais, e onde um número errado é mais convincente. Três erros aparecem sempre, e os três já reprovaram o CI deste repositório."},
 {"h2": "1. Limite absoluto mede a máquina"},
 {"p": "`assert ms < 500` responde sobre o runner, e não sobre o algoritmo. Ele passa no seu computador e reprova num CI de três núcleos — e a reação natural (afrouxar o limite) tira o pouco que ele tinha de valor."},
 {"code": '''adopt Arcane.Bench as B

action trabalho():
    total := 0
    cycle i in range(0, 20000):
        total += i
    yield total

// Medir é fácil; o difícil é o que se COBRA da medida.
// O segundo parâmetro é o ARGUMENTO da ação, e o terceiro as
// repetições — trocar os dois é o erro mais comum aqui. Sem
// argumento, a ação é chamada sem nenhum.
r := B.medir(trabalho)
assert r["ms"] >= 0
assert r["por_segundo"] > 0
out $"{round(r['ms'], 2)} ms — e este número não serve de limite"''', "lang": "df"},
 {"h2": "2. A razão precisa de trabalho suficiente"},
 {"p": "Um teste de paralelismo comparou razão — o padrão certo — e falhou no Windows com **1,47**: o paralelo levou 0,44 s contra 0,30 s da série. O paralelismo estava certo; o que dominou foi o **custo de criar cinco threads**, que no Windows passa de 60 ms de trabalho. A correção não foi afrouxar: foi dar à medida um numerador maior."},
 {"code": '''adopt Arcane.Concurrent as C
adopt Arcane.Bench as B

action com_espera(x):
    sleep(40)          // E/S de mentira: o GIL é solto aqui
    yield x

action em_serie():
    yield [com_espera(i) cycle i in range(0, 4)]

action em_paralelo():
    yield C.map(com_espera, [0, 1, 2, 3])

serie := B.medir(em_serie)
junto := B.medir(em_paralelo)

razao := serie["ms"] / max(junto["ms"], 0.001)
// A cobrança é um FATOR, e com folga: quatro esperas de 40 ms em
// série são ~160 ms, e juntas são ~40 ms.
assert razao > 1.5
out $"{round(razao, 2)}× — e o limite cobrado é um fator, não um prazo"''', "lang": "df"},
 {"h2": "3. O `p` sozinho reprova por desenho"},
 {"p": "Alfa de 0,05 **significa** que uma em vinte comparações de coisas iguais cruza o limiar. Um teste que compara uma ação com ela mesma e só olha o `p` falha 5% das vezes — por definição, e não por defeito."},
 {"code": '''adopt Arcane.Perfil as P

action trabalho():
    total := 0
    cycle i in range(0, 3000):
        total += i
    yield total

// 'comparar' exige as DUAS perguntas: a ordem das amostras é
// acidente (o p), e daí? (o efeito, com piso). E ele alterna a ordem
// dentro da volta, porque quem mede primeiro paga a entrada dela.
r := P.comparar(trabalho, trabalho, {"amostras": 15})
out $"comparando uma ação com ela mesma: {r['mais_rapido']}"
out $"  fator {r['fator']}, p = {r['p_valor']}, significativo: {r['significativo']}"
assert r["mais_rapido"] is "empate"''', "lang": "df"},
 {"p": "Uma ferramenta que responde \"3% mais rápida\" a isso é **pior que nenhuma ferramenta**: é assim que se escolhe a implementação errada com convicção."},
 {"h2": "O ponto de calibração"},
 {"p": "Quando nem o fator basta — porque a máquina está disputada —, a saída é medir, **no mesmo instante**, um algoritmo cujo comportamento não está em dúvida. Se ele não der o esperado, a máquina não está medindo, e o teste diz isso e pula. Medido aqui, com seis threads queimando CPU: o linear foi de 1,98 para 3,30–4,90."},
 {"callout": {"tipo": "nota", "titulo": "A primeira medida nunca reprova", "texto": "Um CI que nasce vermelho por desenho é desligado no mesmo dia. `Arcane.Perfil` grava a primeira medida como referência e só compara a partir da segunda — e a tolerância é obrigatória, porque sem ela todo CI fica vermelho por ruído, o que dá no mesmo."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/depurar",
"title": "Depurar uma corrida",
"description": "O defeito que some quando você olha — e as quatro técnicas que funcionam mesmo assim.",
"blocos": [
 {"p": "Uma condição de corrida tem a pior propriedade possível para depuração: **ela some quando se olha**. Acrescentar um `out` muda o tempo, o depurador serializa as threads, e o defeito não reproduz — o que leva à conclusão errada de que ele foi corrigido."},
 {"h2": "1. Aumentar a janela, de propósito"},
 {"p": "Se você suspeita de um ler-modificar-escrever, **alargue** o intervalo entre ler e escrever. Um defeito que acontece em 1 de 10 mil passa a acontecer em 9 de 10:"},
 {"code": '''adopt Arcane.Concurrent as C

estado := {"n": 0}

action somar_com_janela():
    cycle i from 1 to 50:
        lido := estado["n"]
        sleep(1)                  // a janela, alargada de propósito
        estado["n"] := lido + 1

parallel:
    somar_com_janela()
    somar_com_janela()

// Com a janela aberta, a perda aparece quase sempre.
out $"esperado 100, obtido {estado['n']}"
assert estado["n"] <= 100''', "lang": "df"},
 {"p": "Isto é uma técnica de **investigação**, e não um teste: o teste que fica é o que usa a trava, e ele precisa passar sempre."},
 {"h2": "2. Contar, em vez de olhar"},
 {"code": '''adopt Arcane.Concurrent as C

// Um contador atômico não perde, e por isso serve de RÉGUA: ele diz
// quantas vezes o trecho rodou de verdade.
feitas := C.contador(0)
estado := {"n": 0}

action trabalho():
    cycle i from 1 to 500:
        feitas.somar(1)
        estado["n"] := estado["n"] + 1

parallel:
    trabalho()
    trabalho()

out $"rodou {feitas.valor()} vezes, e o estado marcou {estado['n']}"
assert feitas.valor() is 1000''', "lang": "df"},
 {"p": "A régua é o que transforma \"acho que perdeu atualização\" em \"rodou mil vezes e o estado marcou 987\" — e a segunda frase aponta para a linha."},
 {"h2": "3. Repetir muitas vezes, e olhar a distribuição"},
 {"code": '''adopt Arcane.Concurrent as C

action rodada():
    estado := {"n": 0}
    action somar():
        cycle i from 1 to 300:
            estado["n"] := estado["n"] + 1
    parallel:
        somar()
        somar()
    yield estado["n"]

resultados := [rodada() cycle i in range(0, 5)]
distintos := len(set(resultados))
out $"5 rodadas, {distintos} resultado(s) distinto(s): {sorted(resultados)}"

// Um resultado que MUDA entre rodadas idênticas é a assinatura de
// uma corrida — e um que não muda não prova ausência.
assert distintos >= 1''', "lang": "df"},
 {"h2": "4. O depurador, com a ressalva"},
 {"table": {
   "head": ["Ferramenta", "Serve para", "Não serve para"],
   "rows": [
     ["`dataforge debug`", "ver o estado de **uma** thread parada", "reproduzir a corrida — ele a serializa"],
     ["vigia (`w saldo`)", "descobrir **quem** mudou o valor", "o mesmo: a parada muda o tempo"],
     ["`C.contador`", "contar sem perder", "dizer onde"],
     ["um `out` com id da thread", "ver a **ordem** que aconteceu", "casos raros: o `out` tem trava por dentro"]]}},
 {"code": '''adopt Arcane.Concurrent as C

// O id da thread no registro é o que deixa reconstruir a ordem.
linhas := []
action trabalho(nome):
    cycle i from 1 to 3:
        linhas.append($"{nome}:{i}")

parallel:
    trabalho("a")
    trabalho("b")

assert len(linhas) is 6
out linhas''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A correção não é 'pôr um sleep'", "texto": "Um `sleep` que faz o defeito sumir **não corrigiu nada** — ele mudou a probabilidade. O defeito volta numa máquina mais rápida, com mais carga, ou num dia em que o disco está lento. A correção é uma trava, um atômico, uma transação, ou um desenho em que o estado tem um dono só."}},
 {"h2": "Onde procurar primeiro"},
 {"list": [
   "**`v[\"n\"] := v[\"n\"] + 1`** em qualquer lugar alcançado por duas threads — é o caso nº 1, e o `check` avisa.",
   "**Uma rota do Kiln** que escreve em estado de fora: a concorrência ali é invisível.",
   "**`remove`, `pop`, `insert`, `sort`** — eles leem para decidir o que escrever.",
   "**Duas travas em ordens diferentes** — não é perda de atualização, é impasse, e o sintoma é um travamento.",
   "**Um recurso compartilhado sem dono claro** — se você não consegue dizer quem é o dono, provavelmente não há um."]},
]},
]
