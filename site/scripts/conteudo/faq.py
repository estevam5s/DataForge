# -*- coding: utf-8 -*-
"""As perguntas que chegam — e que a FAQ de seis paginas nao respondia.

Ela tinha comparacao com Python e com JavaScript, erros comuns,
desempenho e migracao. Faltava o resto: quando NAO usar, o que fazer
para pôr em producao, as perguntas de concorrencia (que sao as que mais
custam), o sistema de tipos, o editor, a placa, e o vocabulario.

A regra desta secao e a do repositorio: **nao se inventa que existe**.
Onde a resposta e "nao ha", ela vem com o motivo — uma FAQ que promete
o que nao tem manda alguem construir em cima do vazio, e a descoberta
vem no incidente.
"""

PAGINAS = [

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/quando-nao-usar",
 "title": "Quando NÃO usar DataForge",
 "description": "A pergunta honesta, respondida com a medida: onde a linguagem serve, onde ela custa caro e onde ela simplesmente não é a ferramenta.",
 "blocos": [
 {"p": "Toda linguagem tem uma resposta pronta para *por que me escolher*. Esta página é a outra. Ela existe porque a recomendação errada custa mais que a falta de recomendação — e porque quem descobre o limite em produção não volta."},

 {"h2": "Não use quando o trabalho é de CPU e o prazo é curto"},
 {"p": "DataForge é um **interpretador de árvore** escrito em Python, com compilação para fechamentos. Medido, de 1,5× a 1,8× mais rápido que a travessia de árvore pura — e ainda assim mais lento que o CPython, que já é mais lento que quase tudo."},
 {"table": {"head": ["Trabalho", "Resposta"], "rows": [
   ["laço numérico apertado", "não — ou `adopt Python.numpy`, que roda vetorizado de verdade"],
   ["muitos núcleos, trabalho de CPU", "`P.map_processos` — medido 3,45× em 10 núcleos"],
   ["muitos núcleos, com `thread`", "**não**: o GIL continua no caminho, e a medida foi 0,97×"],
   ["rede, disco, banco", "sim — `async`/`await` sobrepõe de verdade"]]}},
 {"callout": {"tipo": "atencao", "titulo": "0,97× não é um número ruim, é o número certo", "texto": "Oito blocos de CPU em dez núcleos: série 1607 ms, threads 1654 ms. Threads **perderam** da série, porque o GIL serializa o trabalho e ainda cobra a troca de contexto. Quem espera ganho de `thread` em CPU vai medir isso mesmo."}},

 {"h2": "Não use como servidor público sem algo na frente"},
 {"p": "O Kiln roda sobre o `http.server` do Python. Ele **não tem TLS e não tem HTTP/2** — e isso não é uma pendência de roadmap, é uma decisão: refazer TLS em Python puro seria a pior escolha de segurança possível. Em produção pública, ponha um nginx ou um Caddy na frente."},
 {"p": "E ele atende **um pedido por thread**, sem sincronizar nada por você. Uma rota que lê, decide e escreve num estado em memória perde atualizações — medido: seis pedidos simultâneos entregaram **1 de 6**. O `check` avisa (`escrita-concorrente`), e a resposta é `Arcane.Concurrent`."},

 {"h2": "Não use onde o ecossistema é o produto"},
 {"p": "A biblioteca padrão tem 87 módulos e 2323 símbolos, sem uma única dependência externa. Isso cobre muito — e não cobre o PyTorch, o Kubernetes client, o driver do seu ERP. A ponte para o Python existe (`adopt Python.pandas as pd`) e é real, mas se **a maior parte** do seu sistema vai ser Python chamado de dentro, escreva em Python."},

 {"h2": "Não use se você precisa de um destes"},
 {"list": [
   "**Binário nativo** — não há backend LLVM, e não haverá: amarrar o LLVM tiraria a única propriedade inegociável do projeto, que é zero dependência externa.",
   "**Bare-metal / microcontrolador rodando a linguagem** — `Arcane.IoT` fala *com* a placa pela serial; a linguagem não roda *dentro* dela.",
   "**Aplicativo Android empacotado** — há PWA (`dataforge mobile pwa`), não há APK.",
   "**Alocador próprio** — o alocador é o do CPython. Há controle do **coletor** (`Arcane.Memoria`), que é outra coisa, e o projeto prefere nomear a diferença."]},

 {"h2": "Onde ela é uma boa escolha"},
 {"list": [
   "**Ferramenta interna** — CLI, script de dados, automação. `dataforge new` sai com testes, CI e `forge.toml`.",
   "**Painel de dados** — a Vitrine desenha o gráfico no servidor, em SVG, sem uma linha de CDN. É o que funciona em rede fechada.",
   "**Ensino** — a análise estática acusa antes de rodar, e as mensagens dizem o que fazer.",
   "**Prototipagem com hardware** — a placa vira periférico e o laço de trabalho passa a ser o do computador.",
   "**Sistema modular de verdade** — o `check` atravessa arquivos: `P.criar(1, 2, 3)` é acusado antes de rodar, mesmo vindo de outro `.df`."]},

 {"callout": {"tipo": "nota", "titulo": "A lista de ausências é conferida, não escrita", "texto": "`Arcane.Ecossistema.o_que_nao_existe()` responde em execução, e é **comparada com o disco** por um teste. Uma página que promete o que não existe reprova a suíte — foi assim que esta seção nasceu."}},
 {"cards": [
   {"href": "/docs/faq/producao", "title": "Pôr em produção", "desc": "o que falta, e o que pôr na frente"},
   {"href": "/docs/faq/concorrencia", "title": "Concorrência", "desc": "thread, parallel, async e processos"},
   {"href": "/docs/roadmap", "title": "Roadmap", "desc": "o mapa, com o que não existe"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/concorrencia",
 "title": "Concorrência: qual das quatro",
 "description": "thread, parallel, async/await e processos — o que cada um resolve, o que nenhum resolve, e as medidas.",
 "blocos": [
 {"p": "A pergunta chega sempre na mesma forma: *\"quero que isto rode junto\"*. Há quatro respostas na linguagem, e escolher a errada não dá erro — dá um programa que fica **mais lento**, ou que perde dado em silêncio."},

 {"h2": "A tabela de decisão"},
 {"table": {"head": ["O trabalho é", "Use", "Medido"], "rows": [
   ["rede, disco, banco, `sleep`", "`async` / `await`", "sobrepõe de verdade"],
   ["várias tarefas de I/O, esperando todas", "`parallel`", "espera todas e propaga o erro"],
   ["disparar e não esperar", "`thread:`", "não espera — e o erro sai na hora"],
   ["CPU, em vários núcleos", "`P.map_processos`", "**3,45×** em 10 núcleos"],
   ["CPU, com `thread`", "— **não faça**", "**0,97×**: perdeu da série"],
   ["milhares de conexões", "`Arcane.Laco`", "2000 conexões em **1 thread**, +0 MB"]]}},

 {"h2": "A linguagem não sincroniza sozinha"},
 {"p": "Duas threads escrevendo na mesma variável perdem atualizações. Medido: **40.425 de 80.000**. Sem erro, sem aviso do runtime."},
 {"code": '''adopt Arcane.Concurrent as C

trava := C.mutex()
total := 0

action somar(quanto):
    action juntar():
        total := total + quanto
    // 'com_trava' toma, roda e SOLTA — inclusive quando a acao falha.
    C.com_trava(trava, juntar)

parallel:
    somar(10)
    somar(20)
    somar(30)

assert total is 60

// E para o caso mais comum — um numero que so cresce — nem precisa de
// trava: o contador ja e indivisivel.
c := C.contador()
parallel:
    c.somar(1)
    c.somar(1)
    c.somar(1)
assert c.valor() is 3
out $"total {total}, contador {c.valor()}"''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A rota do Kiln é o caso que mais engana", "texto": "O Kiln usa `ThreadingHTTPServer`: cada pedido roda numa thread, e ali a concorrência é **invisível** — quem escreve a rota não vê thread nenhuma. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**. O `check` avisa com `escrita-concorrente`."}},

 {"h2": "O que o `check` pega, e o que ele não pega"},
 {"p": "O aviso dispara quando um `thread`, um `parallel` **ou uma `route`** escreve num nome que vem de fora — inclusive na forma `v[\"n\"] := …`, que é a que mais engana. A lista de métodos que disparam foi **medida, não presumida**:"},
 {"table": {"head": ["Operação", "Medido", "Avisa?"], "rows": [
   ["`append` de 4 threads, 5 mil vezes", "20.000 de 20.000", "**não** — o GIL protege a operação inteira"],
   ["`v[\"n\"] := v[\"n\"] + 1`", "33.740 de 40.000", "sim"],
   ["`remove`, `pop`, `insert`, `sort`", "lê para decidir o que escrever", "sim"]]}},
 {"p": "A análise **para na fronteira da ação**: seguir chamada exigiria um grafo, e um aviso que depende disso seria impreciso nos dois sentidos. E é aviso, não erro — um acumulador protegido por mutex passa por aqui igual, e recusá-lo proibiria o uso correto."},

 {"h2": "`parallel` espera; `thread` não"},
 {"code": '''// parallel: espera TODAS, e levanta na linha do bloco
monitor:
    parallel:
        out "a"
        out "b"
handle Error as e:
    out "alguma falhou:", e.message

out "aqui so chega depois das duas"''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Isto já saiu com código 0 e metade do trabalho perdida", "texto": "Até a correção, os dois faziam `except Exception` e imprimiam uma linha: o programa seguia, saía com **0**, e nenhum `handle` via o erro. Um CI passava verde. O `parallel` também abandonava as threads depois de 30 s, calado."}},

 {"h2": "Processos: o único caminho para mais de um núcleo"},
 {"code": '''adopt Arcane.Concurrent as P

action pesado(n):
    total := 0
    cycle i from 1 to n:
        total := total + (i * i)
    yield total

resultados := P.map_processos(pesado, [200000, 200000, 200000, 200000])
assert len(resultados) is 4
out $"{len(resultados)} blocos, cada um num nucleo"''', "lang": "df"},
 {"p": "A ação atravessa por **declaração**, e não por fechamento: a árvore do corpo, os parâmetros e o que ela lê sem criar. Do outro lado, um interpretador novo remonta tudo. É o que faz um `record` devolvido de lá ser o **mesmo tipo** daqui — se fosse cópia, o `with` recusaria o próprio resultado."},
 {"callout": {"tipo": "nota", "titulo": "Um pool que sobrevive entre chamadas", "texto": "Iniciar um processo custa mais de cem milissegundos, e num servidor isso acontece *por pedido*. `P.pool_processos()` paga uma vez — medido: 180 ms na primeira chamada, **82 ms na segunda**. O `fechar()` é explícito porque o contrário deixa processos ociosos."}},

 {"h2": "O laço de eventos, e a fibra"},
 {"p": "`Arcane.Laco` é **uma** thread dormindo no `selectors` do sistema. Medido, servidor de linha:"},
 {"table": {"head": ["Conexões", "Laço", "Thread por conexão"], "rows": [
   ["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"],
   ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
 {"p": "O tempo quase empata, e esse é o número honesto. O que muda é a forma da conta: plano contra linear. E a fibra é **sem pilha** — um `emit` dentro de uma ação *chamada* não suspende. É por isso que a documentação diz fibra, e não *green thread*."},
 {"cards": [
   {"href": "/docs/concorrencia", "title": "Concorrência", "desc": "o guia inteiro"},
   {"href": "/docs/biblioteca/concurrent", "title": "Arcane.Concurrent", "desc": "mutex, semáforo, canal, processos"},
   {"href": "/docs/biblioteca/laco", "title": "Arcane.Laco", "desc": "o reator e as fibras"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/tipos",
 "title": "Tipos: o que é conferido, e quando",
 "description": "Anotar é opcional, e o que muda quando você anota. União, refinamento, opaco, genéricos — e onde o analisador cala de propósito.",
 "blocos": [
 {"p": "A dúvida mais comum sobre tipos aqui não é *como escrever* — é **quem confere, e quando**. Há duas metades, e elas respondem em momentos diferentes: o `dataforge check` responde antes de rodar, o interpretador responde na fronteira. Saber qual está falando economiza muito tempo."},

 {"h2": "Anotar é opcional; conferir não é"},
 {"code": """// sem anotacao: roda, e o check cala sobre o tipo
x := 10

// com anotacao: o check prova o que der para provar, e a execucao
// confere na fronteira
idade: Integer := 30

action dobro(n: Integer) -> Integer:
    yield n * 2

assert dobro(idade) is 60
out "o tipo declarado vale na entrada e na saida"
""", "lang": "df"},

 {"h2": "`type`: uma declaração, seis formas"},
 {"p": "O que muda é o que vem depois do `:=`."},
 {"code": """type Id := Integer                              // alias
type Numero := Integer | Float                  // uniao
type Positivo := Integer where valor bigger 0   // refinamento

action guardar(p: Positivo) -> Integer:
    yield p

assert guardar(7) is 7
out "o refinamento vale em TODA fronteira, nao so na criacao"
""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Transparente confere; opaco embrulha", "texto": "Um alias que mudasse o valor quebraria tudo que já aceita um `Integer`. Um opaco que **não** mudasse não protegeria de nada — `cadastrar(senha)` passaria. Por isso `opaque type Cpf := String where …` devolve um valor que **não é** um texto, e delega por protocolo: comparação, ordem, `len` e índice continuam funcionando sem que ninguém saiba o que é um tipo opaco."}},

 {"h2": "`<T>` solto não é conferido; `<T extends X>` é"},
 {"code": """// sem limite: documenta a relacao, e aceita qualquer valor
action eco<T>(x: T) -> T:
    yield x

// com limite: cobrado nas duas metades — o check na chamada, a
// execucao no valor. E dentro do corpo, um 'T extends Number' E um
// Number para o analisador: e o que deixa escrever 'a bigger b'.
action maior<T extends Number>(a: T, b: T) -> T:
    yield a given a bigger b otherwise b

assert eco("oi") is "oi"
assert maior(3, 9) is 9
out "o limite atravessa o adopt tambem"
""", "lang": "df"},

 {"h2": "O que o `check` prova a partir de um literal"},
 {"table": {"head": ["Acusa", "Código"], "rows": [
   ["`xs[10]` num cluster de três", "`indice-fora-do-alcance`"],
   ["`v[\"cidad\"]` num vault sem a chave, com sugestão", "`chave-ausente`"],
   ["`cycle i from 5 to 1` — nunca roda; `step 0` — nunca termina", "`cycle-vazio`"],
   ["`1 is \"1\"` — sempre `no`", "`igualdade-impossivel`"],
   ["`p.clientte` num record, com sugestão", "membro inexistente"],
   ["`P.criar(1, 2, 3)` vindo de **outro arquivo**", "aridade entre módulos"]]}},

 {"h2": "E o que ele cala, de propósito"},
 {"p": "O silêncio é tão projetado quanto o alarme. Um falso alarme ensina a ignorar mensagens — e depois a desligar a verificação inteira."},
 {"list": [
   "**`v[\"k\"] ?? padrao` não é acusado.** O `??` é exatamente o que a dica daquele erro recomenda: um analisador que acusa o conserto que ele próprio sugere é um analisador que se desliga.",
   "**Um parâmetro de tipo não é um tipo.** Sem isso, a trilha ganhava dois alarmes no capítulo que *ensina* genéricos.",
   "**O tipo declarado de uma ação decorada não vale.** Não há como saber qual decorador substitui, e diante de duas respostas ele cala.",
   "**`xs[-1]` continua livre** — tratar todo negativo como fora do alcance acusaria a forma normal de pegar o último item."]},

 {"h2": "Silenciar uma regra, de propósito"},
 {"code": """cores := ["azul", "verde"]

// A regra tem de ser NOMEADA: um 'permitir' solto esconderia o erro
// seguinte, que ninguem pediu para esconder.
match cores:
    point c:                        // df: permitir point-inalcancavel
        out $"casou com {len(c)} cores"

out "a regra vale na linha, ou na de cima"
""", "lang": "df"},
 {"cards": [
   {"href": "/docs/tipos", "title": "O sistema de tipos", "desc": "o guia inteiro"},
   {"href": "/docs/faq/typescript", "title": "Comparação com TypeScript", "desc": "o que cada um confere"},
   {"href": "/docs/erros", "title": "Códigos de erro", "desc": "o catálogo"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/producao",
 "title": "Dá para pôr em produção?",
 "description": "A resposta é \"depende de quê\", e as condições são concretas: o que falta no Kiln, o que o DevOps gera, e o que precisa vir de fora.",
 "blocos": [
 {"p": "A resposta curta: **para ferramenta interna, painel e serviço atrás de um proxy, sim**. Para um serviço público exposto direto na internet, **não sem um servidor na frente**. As condições abaixo são todas concretas."},

 {"h2": "O que o Kiln não tem, e por quê"},
 {"table": {"head": ["Falta", "Motivo", "O que fazer"], "rows": [
   ["**TLS**", "refazer TLS em Python puro seria a pior escolha de segurança possível", "nginx, Caddy ou o proxy da nuvem"],
   ["**HTTP/2**", "ele roda sobre o `http.server` do Python", "o mesmo proxy resolve"],
   ["**sincronização automática**", "a linguagem não aplica trava por você", "`Arcane.Concurrent`, e leia o aviso do `check`"]]}},
 {"p": "O que **tem**, e costuma surpreender: WebSocket com o RFC 6455 falado à mão, Server-Sent Events, streaming de resposta, upload multipart com nome e extensão conferidos, CSRF, cabeçalhos de segurança e limite de corpo como middleware."},

 {"h2": "O que o `devops` gera"},
 {"code": """$ dataforge devops dockerfile
$ dataforge devops compose
$ dataforge devops ci github
$ dataforge devops k8s
$ dataforge devops doctor""", "lang": "bash"},
 {"p": "Ele **gera texto e sai da frente**. Um `deploy` que falasse com Docker e Kubernetes por dentro esconderia o que a imagem é, e no dia em que alguém precisa mudar uma camada não haveria onde mexer."},
 {"table": {"head": ["No artefato", "Sem ele"], "rows": [
   ["`USER forge`", "um escape de contêiner vira root no host"],
   ["o manifesto copiado antes do código", "um commit numa linha reinstala tudo (8 s → 2 min)"],
   ["`.env` no `.dockerignore`", "o segredo fica na camada, e `docker history` o mostra"],
   ["`resources` + as duas sondas no Deployment", "um pod come o nó; o Service manda tráfego antes da hora"],
   ["`depends_on: service_healthy`", "a app falha na primeira consulta, de forma intermitente"]]}},
 {"callout": {"tipo": "perigo", "titulo": "`--host=0.0.0.0` dentro de um contêiner", "texto": "O padrão é `127.0.0.1`, que de dentro significa o próprio contêiner. O sintoma engana: o log diz \"no ar\" e o `curl` de fora não recebe nada. Vale para a Vitrine e para o `ignite` do Kiln (`at \"0.0.0.0\"`)."}},

 {"h2": "O banco sobe depois da aplicação"},
 {"p": "`Forge.esperar(url)` espera o banco **aceitar** conexão e devolve a conexão aberta. O recurso dela é o que ela **não** repete: só erro passageiro entra na retentativa; **credencial errada levanta na hora**. Repetir uma senha errada por quarenta segundos troca um erro claro por um travamento, e o programa não fica mais certo por esperar."},
 {"p": "Medido: 0,51 s contra um contêiner recém-subido, **4 ms** para recusar uma senha errada."},

 {"h2": "Antes de dizer que está no ar"},
 {"list": [
   "`dataforge check .` limpo, e `dataforge test --cobertura --minimo=…` no CI.",
   "`dataforge seguranca` — ele varre o **projeto**, e não só os `.df`: um segredo vaza do arquivo de configuração muito mais do que do código.",
   "`dataforge abi` entre a versão publicada e a nova — é o que decide o número, em vez de escolhê-lo a olho.",
   "Um smoke-test de verdade: site 200, rota protegida 401, admin 403, webhook 400."]},
 {"cards": [
   {"href": "/docs/devops", "title": "DevOps", "desc": "os geradores, um a um"},
   {"href": "/docs/kiln", "title": "Kiln", "desc": "o framework web"},
   {"href": "/docs/faq/quando-nao-usar", "title": "Quando não usar", "desc": "os limites, com medida"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/typescript",
 "title": "Comparação com TypeScript",
 "description": "Dois sistemas de tipos com filosofias diferentes: um apaga na compilação, o outro confere também em execução.",
 "blocos": [
 {"p": "A comparação certa não é de sintaxe — é de **onde o tipo vive**. O TypeScript apaga tudo antes de rodar: o tipo é um contrato entre quem escreve e quem lê, e no `JSON.parse` ele acaba. Em DataForge o tipo declarado é conferido **também na fronteira em execução**, e é por isso que ele pega o que um `any` mal colocado deixa passar."},

 {"h2": "A tabela"},
 {"table": {"head": ["TypeScript", "DataForge", "Nota"], "rows": [
   ["`type Id = number`", "`type Id := Integer`", "alias nos dois"],
   ["`type N = number \\| string`", "`type N := Integer \\| String`", "união nos dois"],
   ["`A & B`", "`A & B`", "interseção nos dois"],
   ["*branded type* por convenção", "`opaque type Cpf := String`", "aqui é **mecanismo**, não convenção"],
   ["— (não existe)", "`Integer where valor bigger 0`", "refinamento **conferido**"],
   ["`function f<T>(x: T): T`", "`action f<T>(x: T) -> T`", "sem limite, nenhum dos dois cobra"],
   ["`<T extends number>`", "`<T extends Number>`", "cobrado nas duas metades"],
   ["`interface`", "`trait`", ""],
   ["`readonly` / `as const`", "`record`", "imutável por construção"],
   ["`enum`", "`enum`", "com método, aqui"],
   ["`x?.y` / `x ?? y`", "`x?.y` / `x ?? y`", "iguais"],
   ["`tsc --noEmit`", "`dataforge check`", "embutido, sem instalar nada"],
   ["`as any`", "não anotar", "o analisador cala, e isso é dito"]]}},

 {"h2": "A diferença que mais aparece"},
 {"code": """type Positivo := Integer where valor bigger 0

action cobrar(v: Positivo) -> Integer:
    yield v * 100

// Isto passa: 7 satisfaz a regra.
assert cobrar(7) is 700

// E isto e RECUSADO em execucao, nao so no editor — que e o que um
// 'as any' do TypeScript nao impede.
recusou := no
monitor:
    cobrar(0 - 5)
handle Error as e:
    recusou := yes
assert recusou
out "o refinamento vale onde o dado chega de fora"
""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "A prova roda num avaliador puro", "texto": "A regra de um `where` é código de quem escreveu, e o analisador **não pode executar código arbitrário** para decidir se acusa. Por isso ela é avaliada numa lista fechada de funções: o que sai dessa lista faz o `check` calar, e a conferência acontece em execução."}},

 {"h2": "O que o TypeScript tem e DataForge não"},
 {"list": [
   "**Tipos condicionais e mapeados** — `T extends U ? A : B`, `Partial<T>`, `Record<K,V>`.",
   "**Inferência de fluxo tão fina quanto** — o *narrowing* do TS por `typeof` e `in` é mais completo.",
   "**Tipos literais de template** — `` `on${Capitalize<E>}` ``.",
   "**Ecossistema de tipos** — o DefinitelyTyped não tem equivalente aqui."]},

 {"h2": "O que DataForge tem e o TypeScript não"},
 {"list": [
   "**Refinamento conferido** (`where`) — no TS é convenção e uma função guarda.",
   "**Tipo opaco de verdade** — o *branded type* do TS some na compilação.",
   "**O tipo atravessa `adopt`** — a aridade **e** os tipos dos parâmetros são conferidos entre arquivos, antes de rodar.",
   "**A conferência em execução** — o tipo não desaparece quando o dado vem de um JSON."]},
 {"cards": [
   {"href": "/docs/faq/tipos", "title": "Tipos", "desc": "o que é conferido, e quando"},
   {"href": "/docs/tipos", "title": "O sistema de tipos", "desc": "o guia"},
   {"href": "/docs/faq/javascript", "title": "Comparação com JavaScript", "desc": "a sintaxe, lado a lado"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/instalacao",
 "title": "Instalação: o que dá errado",
 "description": "Os três lugares onde a linguagem pode estar instalada, a cópia velha no PATH, e o erro que não existe no repositório.",
 "blocos": [
 {"p": "A instalação funciona de primeira quase sempre. O que custa tempo é o caso em que ela funcionou **duas vezes**, em lugares diferentes, e o `PATH` escolhe a errada."},

 {"h2": "As formas"},
 {"table": {"head": ["Como", "Onde põe", "Para quem"], "rows": [
   ["`pip install dataforge-lang`", "no Python que rodou o `pip`", "quem já tem Python"],
   ["`scripts/instalar.sh`", "uma venv em `~/.dataforge`", "macOS e Linux, sem sudo"],
   ["`scripts/instalar.ps1`", "idem", "Windows"],
   ["binário do release", "onde você puser", "sem Python nenhum"],
   ["`pip install -e .`", "aponta para o repositório", "quem desenvolve a linguagem"]]}},

 {"h2": "O erro que não existe no seu arquivo"},
 {"callout": {"tipo": "perigo", "titulo": "Cuidado com instalação velha no PATH", "texto": "Há **três** lugares onde a linguagem pode estar: uma venv do projeto, `~/.dataforge` e o Python do sistema. Uma cópia antiga produz erros que não existem no seu código — foi assim que um `LexError: Unexpected character: '$'` apareceu num arquivo que usa interpolação normalmente. A interpolação existe há versões; o que estava velho era o binário."}},
 {"code": """$ which -a dataforge df
$ dataforge --version
$ python3 -c "import dataforge; print(dataforge.__file__)\"""", "lang": "bash"},
 {"p": "Se as três respostas não concordarem, é isso. Num checkout de desenvolvimento, a venv deve estar em modo editável (`pip install -e .`), que aponta para o repositório e nunca envelhece."},

 {"h2": "O pino do projeto pode trocar a versão por baixo"},
 {"p": "O `forge.toml` declara `dataforge = \">=1.1\"`, e o pino **é cobrado**: `dataforge run` troca por `os.execve` quando a versão pedida está instalada, e **recusa** quando não está. Um pino que não é cobrado é um comentário com sintaxe."},
 {"table": {"head": ["Variável", "O que faz"], "rows": [
   ["`DATAFORGE_SEM_TROCA=1`", "ignora o pino"],
   ["`DATAFORGE_RAIZ`", "troca a raiz das instalações"],
   ["`DF_IDIOMA=en`", "as mensagens voltam ao inglês"],
   ["`NO_COLOR=1`", "sem cor, em toda a CLI"]]}},

 {"h2": "A ponte para o Python instala noutro lugar"},
 {"p": "`adopt Python.numpy as np` procura o numpy **no Python que está rodando a linguagem**. O instalador cria uma venv em `~/.dataforge`, e um `pip install numpy` no terminal costuma instalar em outro. A mensagem de ausência nomeia o Python exato — e no executável único, onde não há `pip` nenhum, ela aponta `pip install dataforge-lang` em vez de um comando que nunca funcionaria."},
 {"cards": [
   {"href": "/docs/instalacao", "title": "Instalação", "desc": "o guia inteiro"},
   {"href": "/docs/faq/editor", "title": "Editor", "desc": "VS Code, LSP e depurador"},
   {"href": "/download", "title": "Download", "desc": "os binários por plataforma"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/editor",
 "title": "Editor: cores, autocompletar e depurador",
 "description": "O que a extensão faz, o que o LSP responde, e como parar o programa numa linha — inclusive por ssh.",
 "blocos": [
 {"p": "A pergunta costuma vir como *\"tem plugin?\"*. Tem, e ele é instalado pela própria CLI — a gramática de cores é **gerada** do `tokens.py`, então ela não pode discordar do lexer."},

 {"h2": "Instalar"},
 {"code": """$ dataforge editor""", "lang": "bash"},
 {"p": "Ele instala no VS Code e nos derivados (Cursor, VSCodium, Windsurf). A coloração, os snippets, o ícone do `.df`, o cliente do LSP e o adaptador de depuração vão juntos."},
 {"callout": {"tipo": "atencao", "titulo": "Instalado por `pip`, a extensão precisa estar compilada", "texto": "`editor/vscode/out/` é gerado por `tsc` e não é versionado. Um wheel construído sem ele sai com o manifesto e **zero JavaScript**: o VS Code carrega a extensão e nada acontece. Há teste que constrói o wheel e olha dentro — conferir o texto do `pyproject.toml` não diz o que o build produz."}},

 {"h2": "O que o LSP responde"},
 {"table": {"head": ["Recurso", "O que faz"], "rows": [
   ["hover", "o tipo e a doc do que está sob o cursor"],
   ["ir-para-definição", "inclusive atravessando `adopt`"],
   ["completar", "**olha o contexto**: depois de `p.`, os membros de `p`"],
   ["diagnósticos", "os mesmos do `dataforge check`, enquanto você digita"],
   ["`// df: permitir <regra>`", "silencia ali, lido do **texto do editor**"]]}},
 {"p": "Os nomes do **próprio arquivo** vêm antes dos 2323 símbolos da biblioteca — é o que se procura em nove de cada dez vezes. E o comentário que silencia uma regra é lido do buffer, não do disco: num arquivo não salvo, ler do disco silenciaria a regra errada — ou nenhuma."},

 {"h2": "Depurar"},
 {"code": """$ dataforge debug programa.df      # no terminal, e serve por ssh
$ dataforge dap                    # o mesmo no painel do editor (F5)""", "lang": "bash"},
 {"table": {"head": ["Comando", "Faz"], "rows": [
   ["`n`", "a próxima linha, sem entrar"],
   ["`s`", "entra na ação"],
   ["`c`", "segue até a próxima parada"],
   ["`w saldo`", "para quando `saldo` **mudar**"],
   ["`r saldo`", "para quando `saldo` for **lido**"]]}},
 {"callout": {"tipo": "nota", "titulo": "Vigiar leitura é outro mecanismo, não uma opção", "texto": "`w` responde *quem mudou isto?* e compara uma foto estrutural depois de cada instrução. `r` responde *quem está consultando isto?* — e uma leitura não muda nada, então não há foto a comparar: ela intercepta os dois caminhos que leem. Custo zero quando não há nenhuma vigia."}},
 {"p": "O depurador **desliga a compilação para fechamentos**: ele para em cada linha sombreando `execute`, e o corpo compilado passaria por fora. Um depurador que enxerga metade das instruções é pior que um interpretador mais lento."},
 {"cards": [
   {"href": "/docs/editor", "title": "Editor", "desc": "a extensão em detalhe"},
   {"href": "/docs/tecnicas/lsp", "title": "O servidor de linguagem", "desc": "como ele responde"},
   {"href": "/docs/cli/debug", "title": "Depurador", "desc": "parar, ver e andar"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/dados",
 "title": "Dados: e o pandas?",
 "description": "Arcane.Quadro, os seis verbos, e quando chamar o pandas de dentro — com a fronteira dita sem rodeio.",
 "blocos": [
 {"p": "Há duas respostas, e escolher entre elas é uma decisão de tamanho, não de gosto."},

 {"h2": "A tabela de dados da linguagem"},
 {"code": """adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"loja": "centro", "mes": "jan", "valor": 1200},
    {"loja": "centro", "mes": "fev", "valor": 1500},
    {"loja": "praia",  "mes": "jan", "valor": 900},
    {"loja": "praia",  "mes": "fev", "valor": 1100}])

// A forma e {coluna: agregacao}. Com mais de uma, a coluna de saida
// vira 'coluna_agregacao' — e a lista de agregacoes e FECHADA: um nome
// desconhecido e recusado com a lista do que existe, porque ele pode
// vir de um '?agregar=' de uma tela.
resumo := vendas
    >> onde valor bigger 1000
    >> agrupar "loja"
    >> resumir {"valor": ["soma", "contagem"]}

assert len(resumo) is 2
cycle linha in resumo:
    out $"{linha["loja"]}: {linha["valor_soma"]} em {linha["valor_contagem"]} mes(es)"
""", "lang": "df"},
 {"p": "`onde`, `pegar`, `sem`, `ordenar`, `agrupar` e `resumir` são operações do `>>` — e **não** são palavras reservadas: `agrupar` e `ordenar` são nomes bons demais para tirar de quem escreve. O parser as reconhece só logo depois de um `>>`."},

 {"h2": "Cinco decisões que explicam o resto"},
 {"table": {"head": ["Decisão", "Porque"], "rows": [
   ["a linha é um **vault**", "é o que `IO.read_csv(c, yes)` e `Database.query` já devolvem"],
   ["por dentro é **colunar**", "`descrever` e `correlacao` viram uma passada por coluna"],
   ["todo verbo devolve um quadro **novo**", "o pipeline fica reexecutável, como `record`/`with`"],
   ["a ausência tem **um nome só**", "`void`, texto vazio e NaN são a mesma coisa — separá-los é metade do bug de limpeza"],
   ["coluna que não existe é **erro, com sugestão**", "devolver coluna vazia calada é o jeito mais rápido de um relatório sair errado"]]}},
 {"callout": {"tipo": "nota", "titulo": "`onde` usa a lógica de três valores do SQL", "texto": "Comparar com `void` não faz a linha passar, em vez de levantar. A outra escolha é a que a linguagem faz em toda expressão comum e está certa lá; aqui tornaria o verbo inutilizável, porque todo conjunto real tem ausência. E só essa falha é engolida — reconhecida por uma **marca no objeto de erro**, nunca comparando o texto da mensagem, que quebraria na primeira tradução."}},

 {"h2": "Quando chamar o pandas"},
 {"p": "`adopt Python.pandas as pd` traz a biblioteca inteira, e a ponte **não converte**: um `DataFrame` continua um `DataFrame`, e `df[\"b\"].sum()` é o código do pandas rodando — não um laço daqui. Isso funciona porque o interpretador trata objeto estranho por **protocolo**: membro, método, índice, `len`, iteração, aritmética e verdade já passavam assim."},
 {"p": "O exemplo abaixo usa um módulo da biblioteca do próprio Python, que existe em toda instalação — com o pandas seria idêntico, e este bloco **roda** na verificação da documentação:"},
 {"code": """adopt Python.statistics as st

notas := [7.0, 8.5, 6.0, 9.5]
assert st.mean(notas) is 7.75
out $"media {st.mean(notas)}, mediana {st.median(notas)}"
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O pacote tem de estar no Python que roda a linguagem", "texto": "O instalador cria uma venv em `~/.dataforge`, e um `pip install pandas` no terminal costuma instalar em outro lugar. A mensagem de ausência nomeia o Python exato por causa disso."}},
 {"table": {"head": ["Use o `Quadro` quando", "Use o pandas quando"], "rows": [
   ["o dado cabe na memória com folga", "são milhões de linhas e você precisa de vetorização"],
   ["você quer zero dependência", "o ambiente já tem a pilha científica"],
   ["o resultado vai para a Vitrine ou para um relatório", "você vai encadear com scikit-learn, statsmodels…"],
   ["o programa roda em rede fechada", "há espaço para instalar"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Havia duas tabelas de dados, e elas divergiam", "texto": "`Arcane.Analytics.DataFrame` e `Arcane.Data.Frame` eram classes independentes com `group_by`, `describe`, `normalize`, `merge` e `pivot` implementados **duas vezes** — e `describe` devolvia chaves diferentes conforme o módulo adotado. As duas continuam funcionando (quebrar código que existe seria pior), e `Arcane.Quadro` é a resposta única."}},
 {"cards": [
   {"href": "/docs/biblioteca/quadro", "title": "Arcane.Quadro", "desc": "a referência"},
   {"href": "/docs/vitrine", "title": "Vitrine", "desc": "o painel, com gráfico em SVG"},
   {"href": "/docs/bibliotecas/ponte", "title": "A ponte para o Python", "desc": "como ela não converte"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/hardware",
 "title": "Hardware: a placa responde?",
 "description": "O que funciona com Arduino e ESP32, o que foi medido com a placa na mesa, e o que a linguagem não faz.",
 "blocos": [
 {"p": "Responde — e esta página foi escrita com duas placas ligadas. A distinção que importa vem primeiro: **a linguagem fala *com* a placa, e não roda *dentro* dela.**"},

 {"h2": "O modelo"},
 {"p": "Você grava um firmware na placa uma vez. A partir daí ela deixa de ter um programa e passa a ter um **protocolo**: obedece. Quem decide é o computador, e o laço de trabalho passa a ser o dele — sem recompilar, sem regravar, sem esperar o upload."},
 {"code": """$ dataforge iot portas
$ dataforge iot sketch firmata --em=/tmp/fw
$ dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:renesas_uno:unor4wifi
$ dataforge iot piscar --pino=13 --vezes=5""", "lang": "bash"},

 {"h2": "O que foi medido, com a placa na mesa"},
 {"table": {"head": ["Placa", "Pinos", "Analógicos", "Provado"], "rows": [
   ["Arduino UNO R4 WiFi", "20", "6", "LED no 13, PWM no 9, A0 lendo ruído"],
   ["ESP32-D0WD-V3", "40", "14", "LED no GPIO2, mapa de ADC completo"],
   ["`arduino:avr:uno`", "20", "6", "compilação"],
   ["`arduino:avr:mega`", "70", "16", "compilação"]]}},
 {"callout": {"tipo": "nota", "titulo": "O firmware não usa a biblioteca Firmata", "texto": "O `Firmata.h` traz um `Boards.h` com a tabela de pinos de cada placa, escrita à mão, e ela para em 2018: num UNO R4 e num ESP32 o compilador responde `#error \"Please edit Boards.h\"`. As duas placas mais vendidas de hoje. O firmware que a linguagem escreve fala o protocolo direto e **pergunta o mapa de pinos ao core** — `NUM_DIGITAL_PINS`, `digitalPinHasPWM`, `analogInputToDigitalPin` são macros que todo core define."}},

 {"h2": "Nada de tabela de pinos"},
 {"p": "`modo(13, \"pwm\")` é recusado porque a **placa** disse que aquele pino não faz PWM — ela responde a pergunta de capacidade no handshake. Uma tabela escrita na linguagem envelheceria na primeira placa nova, e UNO, Mega e ESP32 têm mapas diferentes."},

 {"h2": "As duas armadilhas que mais custam tempo"},
 {"list": [
   "**Sem `relatar_analogico(canal)` a leitura é zero, calada.** A placa envia sozinha, ela não responde perguntas — sem ligar o relatório, `analogico(0)` devolve o valor inicial para sempre.",
   "**`escala` limita por padrão.** O `map()` do C não limita, e um ADC que devolve 1024 por ruído vira 101% num painel."]},

 {"h2": "Sem placa, com o simulador"},
 {"p": "`IoT.conectar_simulada(\"uno\")` devolve uma placa que fala os **mesmos bytes**. Ela não é um dublê da API: é um dispositivo do outro lado do cabo, e por isso exercita o parser, a partição em sete bits e o sysex — que é onde estão os erros."},
 {"code": """adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, 1)
assert placa.ler(13) is 1
assert placa.info()["firmware"]["nome"] is "DataForge"
out $"{placa.info()["pinos"]} pinos, sem placa nenhuma"
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O que o simulador NÃO prova", "texto": "O cabo, o driver USB-serial, o bootloader e o gravador. Um teste que finge hardware e se anuncia como prova de hardware dá confiança sem dar garantia — por isso o teste com placa real só roda com `DATAFORGE_ARDUINO=/dev/…` apontando uma porta de verdade."}},
 {"cards": [
   {"href": "/docs/iot", "title": "IoT", "desc": "o guia inteiro"},
   {"href": "/docs/iot/firmata", "title": "O protocolo", "desc": "o Firmata, byte a byte"},
   {"href": "/docs/iot/sem-placa", "title": "Sem placa", "desc": "o simulador"}]},
]},

# ═══════════════════════════════════════════════════════════
{"href": "/docs/faq/glossario",
 "title": "Glossário: por que esta palavra",
 "description": "O vocabulário inteiro, com a palavra que cada uma substitui — e o motivo de sete terem sido removidas.",
 "blocos": [
 {"p": "A objeção mais comum à linguagem é o vocabulário: *por que `given` e não `if`?* A resposta honesta é que a escolha foi deliberada e tem custo — e que o projeto já **removeu sete palavras reservadas** por serem caras sem entregar nada."},

 {"h2": "O mapa"},
 {"table": {"head": ["Onde você diria", "Aqui", "Nota"], "rows": [
   ["`=`", "`:=`", "`=` sozinho não existe — `given x = 5` é erro de sintaxe, não um bug calado"],
   ["`const`", "`steady`", ""],
   ["`print`", "`out`", "aceita vários, separados por vírgula"],
   ["`if`/`elif`/`else`", "`given`/`orif`/`otherwise`", "o nome atribuído num ramo **existe depois** do bloco"],
   ["ternário", "`a given cond otherwise b`", "a mesma ordem do `if`"],
   ["`switch`", "`match` / `point` / `when` / `default`", "`when` é a guarda"],
   ["`for x in xs`", "`cycle x in xs`", "o corpo tem escopo próprio, de propósito"],
   ["`for i in range(1,6)`", "`cycle i from 1 to 5`", "**inclusivo nos dois extremos**"],
   ["`while`", "`persist`", ""],
   ["`do..while`", "`perform … persist`", ""],
   ["`break` / `continue`", "`halt` / `skip`", "atravessam `monitor`"],
   ["`def` / `return`", "`action` / `yield`", "`yield` **encerra** a ação"],
   ["gerador", "`stream action` / `emit`", "separados de propósito"],
   ["`class` / `new`", "`blueprint` / `spawn`", ""],
   ["`self` / `super`", "`self` / `root`", ""],
   ["`interface`", "`trait`", ""],
   ["`@dataclass(frozen=True)`", "`record`", "imutável, igualdade estrutural"],
   ["`import` / `export`", "`adopt` / `relay`", "`relay` é real, não convenção"],
   ["`try`/`catch`/`finally`", "`monitor`/`handle`/`ensure`", ""],
   ["`throw`", "`trigger`", "levanta `TriggerError`, **não** `RuntimeError`"],
   ["`true`/`false`/`null`", "`yes`/`no`/`void`", ""],
   ["`//` (divisão inteira)", "`~/`", "aqui `//` é comentário"],
   ["`filter`/`map`/`reduce`", "`>> sift`/`morph`/`distill`", "sintaxe, não função"]]}},

 {"h2": "As que mais pegam quem escreve em português"},
 {"p": "Estas são palavras reservadas, e por isso não podem ser nomes de variável: `no`, `in`, `is`, `to`, `from`, `as`, `step`, `point`, `default`, `frame`, `stream`, `emit`, `forge`, `record`, `enum`, `when`. Já `range`, `cluster` e `vault` **são funções**, e continuam livres."},
 {"callout": {"tipo": "nota", "titulo": "Trinta e duas palavras são contextuais, e nenhuma é reservada", "texto": "As onze do Kiln (`server`, `route`, `render`…), as seis do Quadro (`onde`, `agrupar`, `ordenar`…) e as treze de OOP (`readonly`, `final`…) só valem onde o que vem depois confirma. `route := \"/pedidos\"` continua sendo uma variável chamada `route`, e há um bloco na documentação que **demonstra** isso rodando."}},

 {"h2": "Por que sete foram removidas"},
 {"p": "Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de acrescentar uma, o projeto confere se o parser realmente a consome:"},
 {"code": """$ grep -c "TokenType.NOVA\\b" dataforge/parser.py   # precisa ser > 0""", "lang": "bash"},
 {"p": "Se for zero, ela só quebra código de usuário sem entregar nada. Foi o caso de sete — e o mesmo raciocínio recusou `covariant` e `contravariant`, que seriam palavras que não decidem nada: a conferência de variância já está certa sem declaração, e há teste registrando essa decisão."},
 {"cards": [
   {"href": "/docs/referencia/arquitetura", "title": "Referência", "desc": "a gramática e as palavras"},
   {"href": "/docs/referencia/palavras-reservadas", "title": "As palavras", "desc": "um exemplo que roda para cada"},
   {"href": "/docs/faq/python", "title": "Vindo do Python", "desc": "a tabela lado a lado"}]},
]},
]
