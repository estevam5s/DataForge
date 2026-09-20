"""Medir com rigor, o coletor sob controle, e os mapas das partes 17, 10 e 11.

Todo bloco `df` destas páginas RODA (`tests/test_perfil.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/perfil",
"title": "Percentis, e a cauda",
"description": "A média esconde o que o usuário sente. P50, P95 e P99 com aquecimento separado — e por que o percentil sai da amostra, sem interpolar.",
"blocos": [
 {"p": "[`Arcane.Bench`](/docs/tecnicas/bench) responde \"quanto tempo leva\" com uma **média**. É o que quase toda ferramenta de benchmark faz, e é onde quase toda decisão de performance erra."},
 {"p": "Cem requisições de 10 ms e uma de 1000 ms dão média **20 ms**. A pessoa que pegou a última esperou **um segundo** — e nenhum relatório baseado em média vai contar isso."},
 {"code": """adopt Arcane.Perfil as P

action consulta():
    yield sum(range(400))

m := P.medir(consulta, {"amostras": 50, "aquecimento": 5})

assert m["amostras"] is 50
assert m["aquecimento"] is 5
assert m["p50"] smaller_eq m["p95"] and m["p95"] smaller_eq m["p99"]""", "lang": "df"},
 {"code": """adopt Arcane.Perfil as P

// quatro medidas normais e um pico: a media mal se move, o p99 salta
resumo := P.resumir([10.0, 10.0, 10.0, 10.0, 1000.0])

assert resumo["media"] smaller resumo["p99"]
assert resumo["max"] is 1000.0""", "lang": "df"},

 {"h2": "Duas decisões que mudam o número"},
 {"table": {"head": ["Decisão", "Por quê"], "rows": [
   ["o **aquecimento** é separado e declarado", "as primeiras execuções medem cache frio, import preguiçoso e alocação inicial. Misturá-las com o resto não é medir o programa: é medir a **partida**"],
   ["o percentil sai da amostra **por posto**, sem interpolar", "interpolar inventa um valor que não aconteceu. Num P99 de latência o que se quer é uma medida que **existiu**"]]}},
 {"table": {"head": ["Número", "Responde"], "rows": [
   ["`p50`", "o caso comum"],
   ["`p95`, `p99`, `p999`", "o que o usuário reclama"],
   ["`media` e `desvio`", "a forma da distribuição — e o aviso quando a média está bem acima da mediana"],
   ["`vazao`", "operações por segundo, a partir da mediana"],
   ["`min`, `max`", "o piso e o pior caso visto"]]}},
 {"callout": {"tipo": "nota", "titulo": "O relatório avisa quando há cauda", "texto": "`P.relatorio(medida)` escreve a distribuição e, se a média estiver mais de 30% acima da mediana, acrescenta uma linha dizendo que há cauda e que é ela que o usuário sente. Um relatório que só imprime números deixa a leitura para quem já sabia o que procurar."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/comparar",
"title": "A diferença é real, ou é ruído?",
"description": "Mann-Whitney sobre as amostras: o teste que impede a ferramenta de inventar ganho — e por que não é o teste t.",
"blocos": [
 {"p": "**Comparar uma ação com ela mesma não pode dar \"3% mais rápida\".** É o que separa medição de superstição, e é o primeiro teste do arquivo de testes."},
 {"code": """adopt Arcane.Perfil as P

action consulta():
    yield sum(range(400))

// a MESMA acao dos dois lados: a diferenca e ruido, e a ferramenta
// tem de dizer isso
v := P.comparar(consulta, consulta,
                {"amostras": 40, "efeito_minimo": 0.20})
assert v["mais_rapido"] is "empate"
assert not v["significativo"]

// e o efeito MEDIDO continua visivel, significativo ou nao
assert v["efeito"] smaller 0.20""", "lang": "df"},
 {"code": """adopt Arcane.Perfil as P

action rapida():
    yield sum(range(400))

action lenta():
    yield sum(range(9000))

d := P.comparar(rapida, lenta, {"amostras": 30})
assert d["significativo"]
assert d["mais_rapido"] is "a"
assert d["fator"] bigger 2
assert d["p_valor"] smaller 0.05""", "lang": "df"},

 {"h2": "Por que Mann-Whitney, e não o teste t"},
 {"p": "Tempo de execução **não é normal**: tem cauda longa à direita, piso duro à esquerda (nada roda em tempo negativo) e picos de escalonamento do sistema. Um teste t supõe normalidade e responde com confiança sobre uma suposição falsa."},
 {"p": "O U de Mann-Whitney não supõe nada sobre a forma — ele compara **ordens**. E a correção de empates importa quando o relógio tem resolução grossa e muitas amostras dão o mesmo valor."},
 {"table": {"head": ["Campo", "O que diz"], "rows": [
   ["`p_valor`", "a chance de ver esta diferença se as duas fossem iguais"],
   ["`efeito`", "**quanto** mudou na mediana, medido — significativo ou não"],
   ["`efeito_minimo`", "o piso abaixo do qual a resposta é empate (padrão 1%)"],
   ["`significativo`", "`p_valor` abaixo de `alfa` **e** efeito acima do piso"],
   ["`sobreposicao`", "a chance de um sorteio de A ser menor que um de B"],
   ["`fator`", "quantas vezes, na mediana — e só quando é significativo"],
   ["`a`, `b`", "a distribuição completa de cada lado"]]}},
 {"h2": "Por que o p-valor sozinho não serve"},
 {"p": "**Alfa de 0,05 significa que uma em vinte comparações de coisas iguais cruza o limiar.** Não é defeito do teste: é a definição dele. Uma ferramenta que decide só pelo `p` chama de diferença real uma diferença de zero por cento, uma vez a cada vinte — e quem lê o relatório não tem como saber qual das vinte é."},
 {"p": "Medido nesta implementação, comparando uma ação com ela mesma com quatro threads queimando CPU: **2 em 40** deram `p < 0,05`, e nas duas a razão das medianas era **1,0000**. Por isso a resposta exige as duas perguntas — *a ordem das amostras é acidente?* e *e daí?* — e o piso do efeito é o que responde a segunda."},
 {"callout": {"tipo": "atencao", "titulo": "As duas medições são intercaladas, e a ordem alterna", "texto": "Medir A inteiro e depois B inteiro faz uma queda de clock no meio da sessão virar \"B é mais lenta\". Mas intercalar sempre na mesma ordem põe outro viés no lugar: quem vai primeiro paga a entrada da volta — cache, preditor de desvio, o próprio despertar do processo — e quem vem depois aproveita. É um viés **sistemático**, então não desaparece com mais amostras: fica mais significativo. Medido, sem alternar: uma rodada em quarenta acusava 10% de diferença entre uma ação e ela mesma."}},

 {"h2": "Regressão: piorou desde a semana passada?"},
 {"p": "Um número sozinho não responde isso. A linha de base fica num arquivo, e o `conferir` compara."},
 {"code": """adopt Arcane.Perfil as P
adopt Arcane.IO as IO
adopt Arcane.OS as OS

base := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}.json"
P.guardar("consulta", {"p95": 1.0, "p50": 1.0, "media": 1.0}, base)

// tres vezes mais lento: regrediu
ruim := P.conferir("consulta", {"p95": 3.0, "p50": 3.0, "media": 3.0},
                   {"arquivo": base, "tolerancia": 0.2})
assert ruim["regrediu"] and ruim["fator"] is 3.0

// 5% mais lento, com 20% de tolerancia: e ruido de maquina
ok := P.conferir("consulta", {"p95": 1.05, "p50": 1.05, "media": 1.05},
                 {"arquivo": base, "tolerancia": 0.2})
assert not ok["regrediu"]

// a PRIMEIRA medida nunca reprova: sem base nao ha regressao
nova := P.conferir("nunca-medida", {"p95": 1.0}, {"arquivo": base})
assert not nova["conhecida"] and not nova["regrediu"]

IO.delete(base)""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Duas escolhas que mantêm o CI utilizável", "texto": "**A primeira medida nunca reprova** — reprovar ali faria todo CI novo nascer vermelho, e a primeira coisa que se faz com um CI vermelho por desenho é desligá-lo. E **a tolerância é obrigatória**: sem ela, todo CI fica vermelho por ruído de máquina, o que dá no mesmo."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/chamadas",
"title": "Flame graph, pausas e contenção",
"description": "Onde o tempo foi — por ação da linguagem, não por quadro do Python. Mais as pausas do coletor e a contenção que nenhum perfil de CPU mostra.",
"blocos": [
 {"p": "Um *benchmark* diz que está lento; um **perfil** diz onde. `P.comecar_perfil` sombreia o mesmo gancho que o [`dataforge profile`](/docs/cli) usa, e conta o tempo **próprio** de cada ação — o total menos o que as chamadas internas gastaram."},
 {"callout": {"tipo": "nota", "titulo": "Por que tempo próprio, e não acumulado", "texto": "Somar o acumulado daria mais de 100%: numa recursão, o tempo das chamadas internas está dentro do próprio. Um flame graph que soma 207% não é um flame graph. O tempo próprio é o que responde **onde mexer**, que é a pergunta."}},
 {"code": """dataforge profile src/main.df      # o resumo, por acao""", "lang": "bash"},
 {"p": "E de dentro da linguagem, com o gráfico:"},
 {"code": """// perfil := P.perfilar(minha_acao)
// IO.write("perfil.svg", P.chama_svg(perfil["perfil"]))
// IO.write("perfil.folded", P.chama_texto(perfil["perfil"]))""", "lang": "df", "title": "O flame graph, gravado"},
 {"table": {"head": ["Saída", "Para que serve"], "rows": [
   ["`P.chama_svg(perfil)`", "o gráfico, **sem nada de fora**: sem CDN, sem script e sem fonte remota — a mesma regra da [Vitrine](/docs/vitrine), porque perfil costuma ser aberto em rede fechada"],
   ["`P.chama_texto(perfil)`", "o formato **dobrado** (`a;b;c 1234`), que o `flamegraph.pl` e os visualizadores de navegador consomem"]]}},
 {"p": "O formato dobrado foi escolhido por isso: um formato próprio obrigaria a escrever o visualizador junto."},

 {"h2": "Pausas do coletor"},
 {"p": "A pausa do coletor é o que transforma um P50 bom num P99 ruim, e ela **não aparece** em medida nenhuma que olhe só o tempo total. `gc.callbacks` entrega o começo e o fim de cada coleta — é a medida na fonte."},
 {"code": """adopt Arcane.Perfil as P

action trabalho():
    total := 0
    cycle i from 1 to 50:
        total += i
    yield total

r := P.gc_pausas(trabalho)

assert r["resultado"] is 1275
assert "p95" in r and "por_geracao" in r
assert r["total_ms"] smaller 50""", "lang": "df"},

 {"h2": "Contenção de trava"},
 {"p": "Contenção **não aparece num perfil de CPU**: a thread bloqueada não gasta CPU nenhuma. Ela aparece como latência que ninguém explica — e a única forma de vê-la é medir na própria trava."},
 {"code": """adopt Arcane.Perfil as P

trava := P.trava()
P.com_trava(trava, lambda => 1 + 1)
P.com_trava(trava, lambda => 2 + 2)

e := P.estatisticas_da_trava(trava)
assert e["aquisicoes"] is 2
assert e["esperas"] is 0          // sem disputa, ninguem esperou""", "lang": "df"},
 {"p": "A distinção é feita por uma tentativa **sem bloqueio** antes da aquisição real: sem ela, toda aquisição contaria como espera, e a métrica diria que há contenção em programa de uma thread só."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/coletor",
"title": "O coletor sob controle",
"description": "Desligar o coletor não vaza memória — a distinção que quase todo mundo erra. Mais congelar, limiares e a arena.",
"blocos": [
 {"callout": {"tipo": "atencao", "titulo": "A distinção que quase todo mundo erra", "texto": "No CPython, quem libera é a **contagem de referência**, e ela roda na hora. O **coletor** existe só para o **ciclo** — `a` apontando para `b` que aponta para `a`. Desligar o coletor **não vaza memória em geral**: só deixa o ciclo para trás. É por isso que desligá-lo num trecho curto e sensível a latência é uma técnica segura, e não uma gambiarra."}},
 {"code": """adopt Arcane.Memoria as Mem

action critico():
    total := 0
    cycle i from 1 to 100:
        total += i
    yield total

assert Mem.gc_ligado()

// sem coletor no trecho sensivel — e ele volta depois, SEMPRE
assert Mem.sem_gc(critico) is 5050
assert Mem.gc_ligado()""", "lang": "df"},
 {"p": "O `finally` do `sem_gc` não é detalhe: deixar o coletor desligado por causa de um erro é muito pior que a pausa que se queria evitar — e o programa seguiria assim até terminar, sem nada denunciando. Há teste cobrando isso com um corpo que falha."},

 {"h2": "A medida, e não a promessa"},
 {"p": "A frase \"desligar o coletor reduz pausa\" seria fé sem número. O teste mede a **mesma** carga dos dois jeitos, e o que ele mede é o tempo que o coletor passou parando o programa:"},
 {"code": """com o coletor ligado    pausas: 3    total: 1,84 ms
com o coletor desligado pausas: 0    total: 0,00 ms""", "lang": "text", "title": "6000 ciclos alocados"},

 {"h2": "Congelar, e os limiares"},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`Mem.gc_congelar()`", "tira o que **já vive** das varreduras, para sempre — o que um servidor faz depois da carga e antes do primeiro pedido"],
   ["`Mem.gc_limiares()`", "lê os três; com três argumentos, ajusta"],
   ["`Mem.gc_geracoes()`", "quantas coletas houve em cada geração, e quanto cada uma rendeu"],
   ["`Mem.coletar(geracao)`", "força uma coleta agora"]]}},
 {"code": """adopt Arcane.Memoria as Mem

assert len(Mem.gc_limiares()) is 3
assert len(Mem.gc_geracoes()) is 3

antes := Mem.gc_congelados()
Mem.gc_congelar()
assert Mem.gc_congelados() bigger antes
Mem.gc_descongelar()""", "lang": "df"},

 {"h2": "Arena"},
 {"p": "**Não é um allocator**: quem aloca continua sendo o Python, e não há como trocá-lo por dentro. O que a arena troca é o **padrão de uso** — em vez de criar e descartar por volta, um lote é preparado, emprestado e devolvido."},
 {"code": """adopt Arcane.Memoria as Mem

arena := Mem.arena(3, lambda => {"n": 0})
a := Mem.pegar(arena)
Mem.devolver(arena, a)
b := Mem.pegar(arena)         // o MESMO objeto volta

e := Mem.arena_estatisticas(arena)
assert e["criados"] is 3       // o lote, preparado de uma vez
assert e["reaproveitados"] is 1
assert e["em_uso"] is 1""", "lang": "df"},
 {"table": {"head": ["Decisão", "Por quê"], "rows": [
   ["a arena **cresce** quando acaba, e **conta** que cresceu", "travar seria pior; crescer calado esconderia que ela foi dimensionada errada"],
   ["devolver o que não veio dela é **recusado**", "o lote cresceria com estranhos, e o próximo `pegar` entregaria um deles"],
   ["`limpar` solta o lote inteiro numa chamada", "é o tempo de vida de arena da literatura, e a operação que ela existe para ter"]]}},
 {"callout": {"tipo": "nota", "titulo": "O ganho aparece quando o objeto é caro de montar", "texto": "Não quando ele é um vault de três chaves. Uma arena de dicionários vazios troca alocação por indireção e não ganha nada — meça antes, com [`Arcane.Perfil`](/docs/observabilidade/comparar), e só mantenha se o `comparar` disser que a diferença é **significativa**."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/observabilidade/mapa",
"title": "Observabilidade, memória e build: o mapa",
"description": "Item por item das partes 17, 10 e 11 da referência Deep Tech — profiling, benchmarking, allocators, GC opcional, PGO e tooling.",
"blocos": [
 {"p": "Três partes de uma referência Deep Tech, cruzadas com o que a linguagem tem. Elas vão juntas porque se respondem: a parte 17 **mede** o que a parte 10 **controla**, e a parte 11 é quase toda ferramenta que já existia."},

 {"h2": "69 · Profiling (parte 17)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["CPU profiling", "`dataforge profile` e `P.perfilar` — tempo **próprio** por ação", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["**flame graphs**", "`P.chama_svg` (SVG sem nada de fora) e `P.chama_texto` (formato dobrado)", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["memory profiling", "`Mem.tamanho`, `Mem.layout`, `Mem.vivos` por blueprint", "[Coletor](/docs/memoria/coletor)"],
   ["**GC pauses**", "`P.gc_pausas` — medido em `gc.callbacks`, na fonte", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["**lock contention**", "`P.trava` — a thread bloqueada não gasta CPU, e não aparece num perfil", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["async task profiling", "`L.estatisticas` do laço: voltas, prazos, E/S e **maior atraso**", "[Escalonador](/docs/runtime/escalonador)"],
   ["hardware counters, cache/branch miss", "**não se aplica**: o CPython não expõe contador de hardware, e a conta de cache de um interpretador de árvore diria pouco", "—"]]}},

 {"h2": "70 · Benchmarking (parte 17)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["micro e macrobenchmarks", "`Arcane.Bench` (curva, classe, comparar) e `P.medir`", "[Perfil](/docs/observabilidade/perfil)"],
   ["**P50, P95, P99**", "`P.medir` e `P.resumir`, por posto e sem interpolar", "[Perfil](/docs/observabilidade/perfil)"],
   ["**tail latency**", "é o ponto da página: a média esconde exatamente isso", "[Perfil](/docs/observabilidade/perfil)"],
   ["**warm-up**", "separado e declarado em `aquecimento`", "[Perfil](/docs/observabilidade/perfil)"],
   ["**statistical significance**", "Mann-Whitney com correção de empates — e não teste t, porque tempo não é normal", "[Comparar](/docs/observabilidade/comparar)"],
   ["**regression benchmarks**", "`P.guardar` e `P.conferir` contra linha de base, com tolerância", "[Comparar](/docs/observabilidade/comparar)"],
   ["throughput", "`vazao` na medida, a partir da mediana", "[Perfil](/docs/observabilidade/perfil)"]]}},

 {"h2": "71 · Diagnóstico (parte 17)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["hotspot identification", "o flame graph, por tempo próprio", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["GC pauses", "`P.gc_pausas`, com percentis e por geração", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["lock contention", "`P.trava`, com a taxa de disputa", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["scheduler overhead", "`maior_atraso_ms` no laço de eventos", "[Escalonador](/docs/runtime/escalonador)"],
   ["I/O bottlenecks", "[`Arcane.Observar`](/docs/tecnicas/observar) — painel, alerta e Prometheus", "[Observar](/docs/tecnicas/observar)"],
   ["compilation overhead", "[`dataforge ir --fase=lir`](/docs/compilador/otimizacao)", "[Otimização](/docs/compilador/otimizacao)"],
   ["allocation hotspots, cache/branch misses", "**não existe**: exigiria instrumentar o alocador do CPython", "—"]]}},

 {"h2": "47–48 · Allocators e estratégias (parte 10)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["object pooling, memory reuse", "`Mem.arena`, e o `pool` de [`Arcane.Padroes`](/docs/oop/padroes)", "[Coletor](/docs/memoria/coletor)"],
   ["arena lifetime", "`Mem.limpar` — o lote inteiro numa chamada", "[Coletor](/docs/memoria/coletor)"],
   ["alignment control", "existe, e é real — mas só na fronteira com o C: `C.alinhamento_de`", "[FFI](/docs/ffi/c)"],
   ["global/system/bump/slab/stack allocator", "**não se aplica**: quem aloca é o CPython, e não há como trocá-lo por dentro. Um \"allocator\" em Python puro seria uma camada **sobre** o alocador real — mais lenta, e chamada de allocator por engano", "—"],
   ["stack vs heap allocation", "**não se aplica**: todo objeto vive no heap do Python", "—"]]}},

 {"h2": "49–51 · Zero-cost, bypass e GC (parte 10)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["**desativação local do GC**", "`Mem.sem_gc`, que religa **mesmo se o corpo falhar**", "[Coletor](/docs/memoria/coletor)"],
   ["**pause times**", "`P.gc_pausas`, com P50/P95/P99", "[Chamadas](/docs/observabilidade/chamadas)"],
   ["**allocation thresholds**", "`Mem.gc_limiares` — os três, lidos e ajustados", "[Coletor](/docs/memoria/coletor)"],
   ["generational GC", "as três gerações do CPython, com a conta por geração", "[Coletor](/docs/memoria/coletor)"],
   ["**interação entre GC e ownership**", "[`Arcane.Posse`](/docs/memoria/posse) libera por escopo, sem esperar coletor", "[Posse](/docs/memoria/posse)"],
   ["escape analysis, dead code elimination", "existem, e são do [analisador](/docs/compilador/analises)", "[Análises](/docs/compilador/analises)"],
   ["mark-and-sweep, concurrent/parallel GC, thread-local GC", "**não se aplica**: o coletor é o do CPython, e trocá-lo não é uma decisão desta linguagem", "—"],
   ["monomorfização, static dispatch, inline expansion", "**não existe**: a linguagem é dinâmica, e uma ação pode ser substituída em execução", "—"],
   ["`#[no_std]`, bypass do runtime", "**não se aplica**: o runtime é o CPython", "—"]]}},

 {"h2": "52–54 · Build (parte 11)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["**compiler tooling**", "já existia **inteiro**: `check`, `fmt`, `lint`, `test`, `bench`, `profile`, `debug`, `dap`, `lsp`, `doc`, cobertura, `--plugin=`", "[CLI](/docs/cli)"],
   ["`dfpm` (gerenciador)", "`dataforge add/install/pack/publish`, com semver e lockfile", "[Pacotes](/docs/cli/pacotes)"],
   ["code coverage", "`dataforge test --cobertura --minimo=80`", "[Cobertura](/docs/tecnicas/cobertura)"],
   ["compiler plugins", "`--plugin=`, escrito em DataForge, vendo MIR e SSA", "[Plugins](/docs/metaprogramacao/plugins)"],
   ["**PGO**", "**não se aplica, e há número**: a [parte 8](/docs/compilador/otimizacao) mediu que compilar mais nós rende **1,01×** em código real. Um PGO que decidisse *o que* compilar otimizaria a constante errada", "[Otimização](/docs/compilador/otimizacao)"],
   ["LTO, ThinLTO, cross-module inlining", "**não se aplica**: não há passo de ligação", "—"]]}},

 {"h2": "O resumo honesto"},
 {"p": "A **parte 17 rendeu inteira** — percentis, significância, regressão, flame graph, pausas do coletor e contenção eram todos buracos reais, e todos transferem sem hardware. A **parte 10 rendeu pela metade**: o coletor e a arena sim; allocator, `no_std` e monomorfização não, porque quem aloca é o CPython. A **parte 11 já estava quase toda pronta** — §54 existia por inteiro —, e o que sobrava (PGO, LTO) é onde a parte 8 já tinha dado a resposta com número."},
 {"callout": {"tipo": "nota", "titulo": "O teste que mais importa deste conjunto", "texto": "Não é nenhum dos números: é o que compara **uma ação com ela mesma** e exige a resposta \"empate\". Uma ferramenta de benchmark que responde \"3% mais rápida\" a isso é pior que nenhuma ferramenta — porque é assim que se escolhe a implementação errada com convicção."}},
]},
]
