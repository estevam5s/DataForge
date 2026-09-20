"""STM, atômicos, estruturas sem trava e o mapa da parte 4.

Todo bloco `df` destas páginas RODA e passa pelo `check`
(`tests/test_stm_e_atomicos.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/stm",
"title": "Memória transacional",
"description": "Escritas que acontecem juntas ou não acontecem: variável transacional, atomicamente, retentar e ou_entao — a composição que o mutex não tem.",
"blocos": [
 {"p": "O problema está medido neste repositório: duas threads somando na mesma variável entregaram **40.425 de 80.000**, em silêncio. As respostas que existiam eram `mutex` — e a disciplina de lembrar dele em todo lugar — e `contador`, que só serve para contar."},
 {"p": "O que nenhuma das duas resolve é **compor**. Transferir de uma conta para outra são duas escritas que precisam acontecer juntas ou não acontecer. Com mutex isso vira ordem de aquisição, e ordem errada é impasse — uma regra que ninguém consegue verificar."},

 {"h2": "A transação"},
 {"code": """adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

total := T.variavel(0)

action somar(i):
    cycle _ in range(0, 200):
        T.atomicamente(lambda => T.escrever(total, T.ler(total) + 1))

// 'para_cada' COLETA os erros em vez de levantar — e por isso eles
// tem de ser conferidos. Uma acao que morre no meio deixa parte dos
// incrementos para tras, e o total sai plausivel e errado.
r := C.para_cada(somar, [i cycle i in range(1, 41)])
assert len(r["erros"]) is 0, "nenhuma thread pode ter falhado"
assert T.valor(total) is 8000          // 40 threads, 200 somas, nada perdido""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Confira os erros de `para_cada`", "texto": "Ele **coleta** as falhas em vez de levantar na primeira — é o contrato certo para trabalho em lote, onde parar no primeiro e-mail que falha é pior que seguir e relatar. O preço: uma ação que morre no meio deixa parte do trabalho feito, e o número final fica **plausível e errado**. Este teste já reprovou no CI mostrando `3504` em vez de `8000`, e não havia como saber por quê."}},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`T.variavel(v)`", "cria a variável transacional"],
   ["`T.atomicamente(acao)`", "roda a ação como transação: tudo, ou nada"],
   ["`T.ler(v)` · `T.escrever(v, x)`", "só valem **dentro** de uma transação"],
   ["`T.modificar(v, f)`", "`escrever(v, f(ler(v)))` — a forma que não esquece o ler"],
   ["`T.valor(v)`", "uma **foto**, fora de transação, sem promessa nenhuma"],
   ["`T.retentar()`", "desiste e **espera** alguma variável lida mudar"],
   ["`T.ou_entao(a, b)`", "tenta a primeira; se ela pedir para esperar, tenta a segunda"],
   ["`T.estatisticas()`", "confirmadas, conflitos, retentativas, esperas"]]}},

 {"h2": "Atomicidade: metade escrita não existe"},
 {"code": """adopt Arcane.Stm as T

a := T.variavel(10)
b := T.variavel(10)

action quebrar():
    T.escrever(a, 999)
    trigger "no meio"

monitor:
    T.atomicamente(quebrar)
handle Error as e:
    assert e.message is "no meio"

assert T.valor(a) is 10 and T.valor(b) is 10      // nada foi publicado""", "lang": "df"},
 {"p": "O erro **não é engolido**: a transação desfaz o rascunho e o erro sobe para quem chamou decidir. Engoli-lo transformaria uma falha num silêncio, que é o oposto do que atomicidade significa."},

 {"h2": "Isolamento: a transação vê a própria escrita"},
 {"code": """adopt Arcane.Stm as T

x := T.variavel(1)

action dentro():
    primeiro := T.ler(x)
    T.escrever(x, 5)
    yield [primeiro, T.ler(x)]        // lê o que ela mesma escreveu

assert T.atomicamente(dentro) is [1, 5]
assert T.valor(x) is 5""", "lang": "df"},

 {"h2": "Composição: duas transações viram uma"},
 {"p": "É o que o mutex não dá. Duas operações que já são transacionais podem ser chamadas dentro de uma terceira, e aí elas são **uma só** transação — aninhar é achatar."},
 {"code": """adopt Arcane.Stm as T

a := T.variavel(1)
b := T.variavel(1)

action dobrar_a():
    T.escrever(a, T.ler(a) * 2)

action dobrar_b():
    T.escrever(b, T.ler(b) * 2)

action as_duas():
    dobrar_a()
    dobrar_b()

T.atomicamente(as_duas)               // uma transação, duas escritas
assert T.valor(a) is 2 and T.valor(b) is 2""", "lang": "df"},

 {"h2": "Esperar sem girar: retentar e ou_entao"},
 {"p": "`T.retentar()` diz \"não dá para seguir com o que existe agora\". A transação é abandonada e **dorme** até alguma variável que ela leu mudar — um `persist` girando gastaria um núcleo para não fazer nada."},
 {"code": """adopt Arcane.Stm as T

fila := T.variavel([])
reserva := T.variavel(["de reserva"])

action da_fila():
    itens := T.ler(fila)
    given len(itens) is 0:
        T.retentar()                  // vazia: espera
    yield itens[0]

action da_reserva():
    yield T.ler(reserva)[0]

// ou_entao: a primeira pediu para esperar, então vai a segunda
assert T.atomicamente(lambda => T.ou_entao(da_fila, da_reserva)) is "de reserva" """, "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Ler fora de uma transação é recusado", "texto": "`T.ler(v)` e `T.escrever(v, x)` sem transação levantam, dizendo por quê: um valor lido solto não teria garantia nenhuma — com cara de garantia. Para a foto existe `T.valor(v)`, que diz no nome o que é."}},

 {"h2": "Como funciona, e o que custa"},
 {"p": "Otimismo com validação, no modelo clássico: a transação lê e escreve num **rascunho**; no fim, sob uma trava curta, confere se alguma variável lida mudou de versão; se mudou, descarta tudo e tenta de novo; se não, publica as escritas de uma vez e acorda quem espera."},
 {"table": {"head": ["Custo", "Quando aparece"], "rows": [
   ["trabalho repetido", "quando duas transações escrevem na **mesma** variável ao mesmo tempo — o conflito custa repetição, e não dado errado"],
   ["a trava do commit", "curta de propósito: protege a validação e a publicação, não o corpo. Se protegesse o corpo, isto seria um mutex global com outro nome"],
   ["memória do rascunho", "proporcional ao que a transação leu e escreveu"]]}},
 {"code": """adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

x := T.variavel(0)

action somar(i):
    cycle _ in range(0, 50):
        T.atomicamente(lambda => T.escrever(x, T.ler(x) + 1))

C.para_cada(somar, [i cycle i in range(1, 9)])

estat := T.estatisticas()
assert T.valor(x) is 400
assert estat["confirmadas"] bigger_eq 400
assert estat["conflitos"] bigger_eq 0     // o preço do otimismo, medido""", "lang": "df"},

 {"h2": "Quando usar cada peça"},
 {"table": {"head": ["Situação", "A peça"], "rows": [
   ["contar", "`C.contador()` ou `C.atomico(0).somar(1)`"],
   ["uma escrita só, condicional", "`C.atomico(v).comparar_e_trocar(…)`"],
   ["**duas ou mais escritas que andam juntas**", "`T.atomicamente(…)`"],
   ["esperar por uma condição de dado", "`T.retentar()` dentro da transação"],
   ["proteger uma seção crítica com E/S", "`C.mutex()` — transação repete, e repetir um `out` imprimiria duas vezes"],
   ["passar trabalho entre threads", "`C.canal()`"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Não faça E/S dentro de uma transação", "texto": "A transação pode ser **repetida**, e o que já saiu não volta: um `out`, um `IO.write` ou um `Http.post` lá dentro aconteceria duas vezes. Junte o resultado dentro da transação e faça a E/S depois dela."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/sem-trava",
"title": "Atômicos e estruturas sem trava",
"description": "CAS, fetch-add, fila e pilha sem trava, ring buffer, executor e promessa — e o que o GIL garante de verdade.",
"blocos": [
 {"p": "O `Contador` resolve contar. O que faltava era a peça geral: um valor que troca **só se ainda for o que você leu** — o *compare-and-swap*. É com ele que se escreve um contador sem trava, uma pilha sem trava e metade de uma STM."},

 {"h2": "CAS: a troca condicional"},
 {"code": """adopt Arcane.Concurrent as C

a := C.atomico(10)

assert a.pegar() is 10
assert a.comparar_e_trocar(10, 20)       // ainda era 10: trocou
assert a.pegar() is 20
assert not a.comparar_e_trocar(10, 30)   // já não é 10: não trocou
assert a.trocar(99) is 20                // devolve o ANTERIOR
assert a.pegar() is 99""", "lang": "df"},
 {"p": "O laço clássico — leia, calcule, troque se ninguém mexeu — é a forma de escrever qualquer atualização sem trava:"},
 {"code": """adopt Arcane.Concurrent as C

a := C.atomico(0)

action incrementar_sem_trava():
    persist yes:
        atual := a.pegar()
        given a.comparar_e_trocar(atual, atual + 1):
            halt

action trabalhar(i):
    cycle _ in range(0, 200):
        incrementar_sem_trava()

C.para_cada(trabalhar, [i cycle i in range(1, 11)])
assert a.pegar() is 2000""", "lang": "df"},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`a.pegar()` · `a.definir(x)`", "leitura e escrita indivisíveis"],
   ["`a.trocar(x)`", "escreve e devolve o **anterior**"],
   ["`a.comparar_e_trocar(esperado, novo)`", "troca só se o valor ainda for o esperado; devolve se trocou"],
   ["`a.somar(n)`", "soma e devolve o **novo** (fetch-add com a ordem certa)"],
   ["`a.pegar_e_somar(n)`", "soma e devolve o **anterior**"],
   ["`a.atualizar(f)`", "aplica `f`, repetindo enquanto alguém trocar"]]}},

 {"h2": "Fila, pilha e anel"},
 {"code": """adopt Arcane.Concurrent as C

fila := C.fila_sem_trava()
fila.por(1)
fila.por(2)
assert fila.tirar() is 1 and fila.tamanho() is 1

pilha := C.pilha_sem_trava()
pilha.por(1)
pilha.por(2)
assert pilha.tirar() is 2            // do topo
assert pilha.tirar() is 1
assert pilha.tirar() is void         // vazia: void, e não erro

anel := C.anel(3)
cycle i from 1 to 5:
    anel.por(i)
assert anel.tudo() is [3, 4, 5]      // o mais velho sai quando enche
assert anel.cheio()""", "lang": "df"},
 {"p": "O **anel** é a estrutura de uma janela de métricas, de um log em memória e de um produtor rápido com consumidor lento — onde perder o mais velho é melhor que parar o produtor."},

 {"h2": "O que o GIL garante — e o que não"},
 {"callout": {"tipo": "atencao", "titulo": "\"Sem trava\" aqui quer dizer uma coisa específica", "texto": "`append` e `popleft` de um `deque` acontecem **inteiros** em C, sem janela entre ler e escrever: é indivisível de verdade, e está medido no repositório — quatro threads com 5 mil `append` cada entregaram 20.000 de 20.000. O que **não** é indivisível é qualquer sequência escrita em DataForge: `v[\"n\"] := v[\"n\"] + 1` perde atualização, e ali a resposta é `atomico`, `mutex` ou transação."}},
 {"table": {"head": ["Item da literatura", "Aqui"], "rows": [
   ["compare-and-swap", "`atomico.comparar_e_trocar` — existe, e é a base do resto"],
   ["fetch-add, atomic load/store", "`somar`, `pegar_e_somar`, `pegar`, `definir`"],
   ["acquire, release, relaxed, seq-cst, fences", "**não se aplicam**: não há reordenação observável a ordenar — o GIL já dá consistência sequencial entre operações Python"],
   ["wait-free", "**não existe** como garantia: o laço de CAS é *lock-free*, não *wait-free* — uma thread azarada pode repetir"],
   ["ABA problem", "acontece, e a saída é a mesma: guarde um selo junto do valor (`(valor, versão)`) em vez do valor cru"],
   ["hazard pointers, epoch reclamation", "**não se aplicam**: o coletor cuida da liberação, que é o problema que essas técnicas resolvem"]]}},

 {"h2": "Executor e promessa"},
 {"p": "`C.rodar` abre uma thread por chamada; num servidor isso acontece por pedido. O **executor** paga a partida uma vez. A **promessa** é o resultado que ainda não existe e que alguém — um evento, uma resposta de rede — vai cumprir."},
 {"code": """adopt Arcane.Concurrent as C

executor := C.executor(4)

action dobro(x):
    yield x * 2

tarefas := [executor.submeter(dobro, i) cycle i in range(1, 4)]
assert [C.esperar(t) cycle t in tarefas] is [2, 4, 6]
assert executor.mapear(dobro, [10, 20]) is [20, 40]
executor.fechar()
assert not executor.aberto()

p := C.promessa()

action cumprir(i):
    p.cumprir("pronto")

C.rodar(cumprir, 1)
assert p.esperar(3000) is "pronto" """, "lang": "df"},
 {"p": "Uma promessa que falha leva a falha a quem espera — e não um valor vazio:"},
 {"code": """adopt Arcane.Concurrent as C

p := C.promessa()
p.falhar("deu ruim")

monitor:
    p.esperar(1000)
    assert no
handle Error as e:
    assert "deu ruim" in e.message""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/concorrencia/mapa",
"title": "Concorrência e paralelismo: o mapa",
"description": "Item por item da parte 4 da referência Deep Tech — concorrência, STM, lock-free, atomics e paralelismo — cruzado com o que o DataForge tem.",
"blocos": [
 {"p": "A quarta parte de uma referência Deep Tech cobre concorrência, memória transacional, estruturas sem trava, atômicos com ordenação de memória e paralelismo. Abaixo, item por item, com o que existe aqui e o que **não** existe — com o motivo."},

 {"h2": "17 · Concorrência"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["threads", "`thread:` e `parallel:`, com erro que sobe em vez de sumir", "[Concorrência](/docs/tecnicas/concorrencia)"],
   ["tasks, futures", "`C.rodar` devolve tarefa; `C.esperar`, `esperar_todas`, `esperar_primeira`", "[Concorrência](/docs/tecnicas/concorrencia)"],
   ["async/await", "`async action` + `await` — concorrência de E/S de verdade", "[Concorrência](/docs/tecnicas/concorrencia)"],
   ["promises", "`C.promessa()`: cumprir, falhar, esperar", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["executors, thread pools", "`C.executor(n)` com `submeter`, `mapear`, `fechar`", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["event loops", "**não existe** um laço de eventos próprio: `async` roda sobre threads, e a E/S bloqueante se sobrepõe de fato", "—"],
   ["channels, message passing", "`C.canal(capacidade)` — `receber` espera; `receive` sem prazo não", "[Concorrência](/docs/tecnicas/concorrencia)"],
   ["shared state", "existe, e **não** é protegido sozinho: o `check` avisa (`escrita-concorrente`)", "[Análise estática](/docs/tecnicas/analise-estatica)"],
   ["locks, mutex, RwLock, semáforos, barriers", "`mutex`, `com_trava`, `trava_leitura_escrita`, `semaforo`, `barreira`, `evento`, `condicao`", "[Concorrência](/docs/tecnicas/concorrencia)"]]}},

 {"h2": "18 · Memória transacional"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["STM, transações", "`Arcane.Stm`: `variavel` e `atomicamente`", "[STM](/docs/concorrencia/stm)"],
   ["atomicidade, rollback", "erro no meio desfaz o rascunho e sobe — nada é publicado", "[STM](/docs/concorrencia/stm)"],
   ["isolamento, consistência", "a transação lê a própria escrita e valida as versões no commit", "[STM](/docs/concorrencia/stm)"],
   ["composição de transações", "aninhar é achatar: duas transacionais dentro de uma terceira são uma só", "[STM](/docs/concorrencia/stm)"],
   ["controle de conflitos", "otimista: conflito custa repetição, e as estatísticas dizem quanto", "[STM](/docs/concorrencia/stm)"],
   ["concorrência sem locks tradicionais", "sim — a trava existe só no commit, e é curta", "[STM](/docs/concorrencia/stm)"]]}},

 {"h2": "19 · Lock-free e wait-free"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["CAS", "`C.atomico(v).comparar_e_trocar(esperado, novo)`", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["operações atômicas", "`pegar`, `definir`, `trocar`, `somar`, `pegar_e_somar`, `atualizar`", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["filas e pilhas lock-free", "`C.fila_sem_trava()`, `C.pilha_sem_trava()` — `append`/`pop` são indivisíveis em C", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["ring buffers", "`C.anel(n)`: o mais velho sai quando enche", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["wait-free", "**não existe** como garantia: o laço de CAS é lock-free, não wait-free", "—"],
   ["ABA problem", "acontece; a saída é guardar um selo junto do valor", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["hazard pointers, epoch reclamation", "**não se aplicam**: o coletor resolve a liberação que elas endereçam", "—"]]}},

 {"h2": "20 · Atomics e memory ordering"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["atomic load/store, CAS, fetch-add", "todos, em `C.atomico`", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["acquire, release, relaxed, seq-cst", "**não se aplicam**: o GIL já serializa as operações Python, e não há ordenação a escolher"],
   ["memory fences, barriers de memória", "**não existem** como instrução; `C.barreira(n)` é outra coisa — sincroniza threads, não memória"],
   ["modelo de memória da CPU, reordenação", "**não é observável** daqui: a reordenação existe no processador, e o runtime não a expõe"]]}},

 {"h2": "21 · Paralelismo"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["parallel loops, data parallelism", "`C.map`, `C.para_cada`, `C.lotes`; e `C.map_processos` para CPU", "[Paralelismo](/docs/exercicios/35-paralelismo)"],
   ["thread pools, task scheduling", "`C.executor(n)`, `C.pool_processos()`, `C.grupo()`", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["pipeline parallelism", "`Arcane.Pipeline` — etapas com dependência, ordem topológica e histórico", "[Pipelines](/docs/tecnicas/pipeline)"],
   ["work stealing", "**não existe**: o pool distribui, e não rouba — a diferença só aparece com tarefas muito desiguais"],
   ["SIMD", "**não existe** na linguagem; a vetorização vem pela ponte (`adopt Python.numpy`), sem cópia na fronteira", "[Ponte](/docs/tecnicas/ponte)"],
   ["GPU computing", "**não existe**: o caminho é a ponte para uma biblioteca que já fale com a GPU"],
   ["NUMA awareness", "**não existe**: o runtime não escolhe nó de memória"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das cinco seções, **três e meia** têm resposta aqui: concorrência (completa), STM (nova), lock-free no que o GIL permite garantir de verdade, e paralelismo de dados com processos. O que não existe divide-se em duas classes — o que o **GIL torna sem sentido** (ordenação de memória, fences) e o que exige **descer ao hardware** (SIMD, GPU, NUMA), que é justamente onde a ponte para o Python entra."},
 {"callout": {"tipo": "nota", "titulo": "A regra que vale para tudo isto", "texto": "A linguagem **não sincroniza sozinha**. O `dataforge check` avisa quando um `thread`, `parallel` ou `route` escreve num nome que vem de fora (`escrita-concorrente`) — inclusive na forma `v[\"n\"] := …`, que é a que mais engana. É aviso, e não erro: um acumulador protegido por mutex passa por ali igual."}},
]},
]
