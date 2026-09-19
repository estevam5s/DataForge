"""A partida, a pilha, a capacidade — e o mapa das partes 13, 15, 9, 14 e 16.

Todo bloco `df` destas páginas RODA (`tests/test_inicio_e_cofre.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/partida/inicio",
"title": "Antes da primeira linha",
"description": "As sete fases que rodam antes da sua primeira instrução — e quanto cada adopt custou na partida.",
"blocos": [
 {"p": "Um programa não começa na primeira linha. Antes dela o [`comptime`](/docs/metaprogramacao/comptime) rodou numa caixa sem E/S, os `adopt` carregaram módulos e as declarações de topo foram içadas."},
 {"p": "Nada disso era **visível** — e \"por que a partida demora 400 ms?\" não tinha como ser respondido sem cronometrar à mão."},
 {"code": """adopt Arcane.Inicio as I

fases := I.fases()
assert [f["fase"] cycle f in fases] is
       ["lexer", "parser", "comptime", "hoisting", "adopt", "programa", "defer"]""", "lang": "df"},
 {"table": {"head": ["Fase", "O que acontece"], "rows": [
   ["`lexer`", "o texto vira tokens, com linha e coluna em cada um"],
   ["`parser`", "os tokens viram a árvore; um erro de sintaxe para aqui"],
   ["`comptime`", "os blocos rodam numa **caixa sem E/S**, e o que decidem vira constante antes de o programa existir"],
   ["`hoisting`", "as declarações de topo são içadas: uma ação pode ser chamada antes da linha em que foi escrita"],
   ["`adopt`", "cada módulo é resolvido e carregado, na ordem do arquivo — **é aqui que a partida costuma ser gasta**"],
   ["`programa`", "a primeira instrução de topo finalmente roda"],
   ["`defer`", "os `defer` de topo rodam no fim, na ordem inversa"]]}},

 {"h2": "Onde a partida foi gasta"},
 {"code": """adopt Arcane.Inicio as I
adopt Arcane.Math as M

// cada adopt e cronometrado — e a pergunta aparece quando alguem
// NAO desconfiava, entao a medida e sempre ligada
assert len(I.adocoes()) bigger_eq 2
assert I.relatorio()["adocoes"] bigger_eq 2
assert "mais_caro" in I.relatorio()""", "lang": "df"},
 {"code": """  4 modulo(s) carregado(s) em 38.42 ms

   Arcane.Cortex                  24.108 ms   62.7%
   Arcane.Database                 9.902 ms   25.8%
   Arcane.Math                     2.914 ms    7.6%
   Arcane.Text                     1.496 ms    3.9%""", "lang": "text", "title": "I.texto_do_relatorio()"},
 {"callout": {"tipo": "nota", "titulo": "Por que a medida é sempre ligada", "texto": "São dois floats por import, num lugar que roda **uma vez**. Ligá-la por opção faria a medida existir só para quem já desconfiava — e a pergunta \"por que demora a começar?\" aparece justamente quando ninguém desconfiava."}},

 {"h2": "Globais, e a ordem"},
 {"p": "`steady` declara constante; a ordem de inicialização é a do **arquivo**, e os `adopt` acontecem onde estão escritos. O [ciclo de import é erro do `check`](/docs/modulos/carga), e não estouro em execução — a busca é em largura, para achar o ciclo mais curto."},
 {"p": "E a destruição existe: um `defer` no nível de topo roda no **fim do programa**, na ordem inversa. É como se fecha um arquivo ou uma conexão sem depender de ninguém lembrar."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/partida/por-thread",
"title": "Uma variável por thread",
"description": "Inicialização declarada por thread e finalizador quando ela acaba — o que o armazém sozinho não dá.",
"blocos": [
 {"p": "Um armazém por thread resolve metade do problema. A outra metade é o que costuma faltar: **a inicialização declarada num lugar só**, e o **finalizador** quando a thread acaba."},
 {"p": "Sem finalizador, uma conexão aberta por thread fica aberta depois que ela morre — e o sintoma aparece no servidor, não no código."},
 {"code": """adopt Arcane.Inicio as I

// a inicializacao roda UMA VEZ POR THREAD, e cada uma ve a sua
contador := I.local(lambda => {"n": 0})

caixa := I.meu(contador)
caixa["n"] := caixa["n"] + 1

assert I.meu(contador)["n"] is 1
assert I.threads_com_valor(contador) bigger_eq 1""", "lang": "df"},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`I.local(inicial, ao_terminar?)`", "cria a variável; `inicial` é uma **ação que constrói** o valor"],
   ["`I.meu(local)`", "o valor desta thread, criando-o na primeira vez"],
   ["`I.definir(local, v)`", "troca o valor desta thread"],
   ["`I.limpar(local)`", "esquece; o próximo `meu` nasce de novo"],
   ["`I.threads_com_valor(local)`", "quantas threads têm valor guardado"]]}},

 {"h2": "Três decisões"},
 {"p": "**`inicial` é uma ação, e não um valor.** Um valor seria compartilhado por todas as threads — que é exatamente o que a variável por thread existe para evitar. Passar um valor é recusado, com esse motivo na mensagem."},
 {"p": "**A inicialização roda fora da trava.** Ela é código de quem chamou, pode demorar, e segurar a trava ali faria uma thread lenta parar todas as outras."},
 {"callout": {"tipo": "atencao", "titulo": "O finalizador roda quando a thread é COLETADA", "texto": "Não no instante em que ela termina. É o que `weakref.finalize` garante, e prometer precisão maior seria prometer um gancho que o Python não tem. Para liberar num instante exato, use [`Arcane.Posse`](/docs/memoria/posse): lá a liberação é por **escopo**, e determinística."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/partida/pilha",
"title": "A pilha",
"description": "Profundidade, teto e quadros — a pilha tinha limite e não tinha como ser perguntada.",
"blocos": [
 {"p": "O teto de quadros é **mil**, e recursão legítima o atinge: uma travessia de árvore de cinco mil nós não tem nada de infinita. Quem a escreve precisa saber de quanto é o teto **antes** de bater nele."},
 {"code": """adopt Arcane.Inicio as I

action folha():
    yield I.pilha()

action tronco():
    yield folha()

p := tronco()
assert p["profundidade"] bigger_eq 2
assert p["restante"] is p["limite"] - p["profundidade"]""", "lang": "df"},
 {"code": """adopt Arcane.Inicio as I

action quem():
    yield [q["acao"] cycle q in I.quadros()]

assert "quem" in quem()""", "lang": "df"},

 {"h2": "Ajustar o teto"},
 {"code": """adopt Arcane.Inicio as I

antes := I.limite_da_pilha()
I.limite_da_pilha(300)
assert I.pilha()["limite"] is 300
I.limite_da_pilha(antes)""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Subir demais é recusado, e o motivo é concreto", "texto": "Cada chamada desta linguagem gasta **vários** quadros do CPython. Um teto alto demais troca uma mensagem clara (\"a recursão passou de mil quadros, e aqui estão as duas saídas\") por um `RecursionError` cru do Python — que não fala desta linguagem e não diz o que fazer."}},
 {"p": "As duas saídas que a mensagem do erro traz continuam sendo as certas: `yield f(…)` como retorno **inteiro** vira salto e **não tem teto** (testado com 200 mil), ou um `cycle` com pilha explícita."},
 {"table": {"head": ["Item da literatura", "Aqui"], "rows": [
   ["stack frames", "`I.quadros()` — ação, linha e arquivo de cada um"],
   ["stack overflow detection", "o teto de quadros, com mensagem que diz as duas saídas"],
   ["coroutine / fiber stacks", "as [fibras](/docs/runtime/fibras) são **sem pilha**: o contexto é o quadro do gerador"],
   ["stack probes, stack guards, stack growth", "**não se aplica**: quem gerencia a pilha é o CPython"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/capacidade",
"title": "Fronteira de capacidade",
"description": "Rodar uma ação com os poderes que ela pode alcançar — e a lista honesta do que isto não é.",
"blocos": [
 {"p": "O [`comptime`](/docs/metaprogramacao/comptime) já recusava `out`, `adopt`, `thread` e `parallel`: é uma fronteira de capacidade escrita à mão, para um caso só. E o [`--plugin=`](/docs/metaprogramacao/plugins) roda um `.df` arbitrário do projeto com **todos** os poderes — uma regra de lint que pode abrir soquete."},
 {"code": """adopt Arcane.Capacidade as Cap

// a formula do usuario calcula, e so
action formula():
    adopt Arcane.Math as M
    yield M.sqrt(16) + len("abc")

assert Cap.executar(formula, []) is 7.0""", "lang": "df"},
 {"code": """adopt Arcane.Capacidade as Cap

action ler_disco():
    adopt Arcane.IO as IO
    yield IO.exists(".")

// sem permissao, o adopt e recusado pelo NOME da capacidade
monitor:
    Cap.executar(ler_disco, [])
    assert no
handle Error as e:
    assert "arquivos" in e.message
    assert "Arcane.IO" in e.message

// com ela, o mesmo codigo passa
assert Cap.executar(ler_disco, ["arquivos"])""", "lang": "df"},

 {"h2": "As capacidades"},
 {"table": {"head": ["Capacidade", "O que libera"], "rows": [
   ["`arquivos`", "`Arcane.IO`, `Archive`, `Excel`, `ArquivoSeguro`, `Lago`"],
   ["`rede`", "`Http`, `Rede`, `Web`, `Email`, `Malha`, `Kiln`, `Vitrine`"],
   ["`processo`", "`OS` e `Process` — o sistema e outros processos"],
   ["`banco`", "`Database`, `Forge`, e o que persiste"],
   ["`threads`", "`Concurrent`, `Async`, `Laco`, `Stm`"],
   ["`nativo`", "`Arcane.C` — memória sem rede de proteção, a fronteira mais insegura que existe aqui"],
   ["`python`", "a ponte, que alcança **tudo** o que o Python alcança"],
   ["`ambiente`", "variáveis de ambiente e argumentos"]]}},
 {"p": "Um nome inventado é **recusado com a lista**: um erro de digitação concederia silenciosamente nada, e a fronteira pareceria mais aberta do que é."},
 {"code": """adopt Arcane.Capacidade as Cap

// descobrir de que uma acao precisa: rode sem nada e leia os negados
action tenta():
    monitor:
        adopt Arcane.OS as OS
        yield OS.name()
    handle Error:
        yield "negado"

r := Cap.observar(tenta, [])
assert r["negados"][0]["capacidade"] is "processo"
assert Cap.exige("Arcane.OS") is "processo"
assert Cap.exige("Arcane.Math") is void      // inofensivo""", "lang": "df"},

 {"h2": "O que isto NÃO é"},
 {"callout": {"tipo": "atencao", "titulo": "Não é uma caixa contra programa hostil", "texto": "Escrito assim de propósito: um módulo chamado *Sandbox* que prometesse contenção seria usado onde não pode ser usado, e a descoberta viria por incidente. `Cap.limites()` devolve esta lista em tempo de execução, para quem for ler pelo código."}},
 {"table": {"head": ["Limite", "Por quê"], "rows": [
   ["**não tira o que foi ENTREGUE**", "passar o módulo é passar o poder junto. **Isso é o modelo**, não um defeito: numa linguagem de capacidade, poder é o que se passa, não o que está no ar — e é por isso que bloquear o `adopt` é a fronteira certa"],
   ["a ponte para o Python é capacidade **própria**", "ela alcança tudo o que o Python alcança; deixá-la junto de outra faria o resto da lista virar enfeite"],
   ["a lista de módulos é escrita à mão", "um erro nela é um furo. Contra código **que você escreveu e revisou** — plugin, fórmula de usuário, `comptime` — isto vale"],
   ["contra código malicioso, não use isto", "use processo separado, contêiner, ou o sistema operacional"]]}},
 {"code": """adopt Arcane.Capacidade as Cap
adopt Arcane.IO as IO

// IO foi ENTREGUE por quem chamou: o cofre nao o retira
action com_o_que_recebeu(ferramenta):
    yield ferramenta.exists(".")

assert Cap.executar(com_o_que_recebeu, [], [IO])""", "lang": "df"},
 {"p": "E a fronteira **se desfaz sempre** — inclusive quando o corpo falha. Uma fronteira que não se desfizesse travaria o programa inteiro, e é o `finally` que garante isso."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/partida/mapa",
"title": "Partida e segurança: o mapa",
"description": "Item por item das partes 13 e 15 da referência Deep Tech — bootstrapping, TLS, pilha, globais, modelo de segurança e unsafe.",
"blocos": [
 {"h2": "58 · Antes do `main()` (parte 13)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["runtime initialization", "as sete fases, nomeadas e em ordem", "[A partida](/docs/partida/inicio)"],
   ["static constructors", "`comptime` — roda na carga, numa caixa sem E/S", "[comptime](/docs/metaprogramacao/comptime)"],
   ["global variables", "`steady`, e o hoisting das declarações de topo", "[A partida](/docs/partida/inicio)"],
   ["runtime services", "os `adopt`, **cronometrados** um a um", "[A partida](/docs/partida/inicio)"],
   ["boot / loader, stack setup, stack probes", "**não se aplica**: quem faz o boot é o CPython", "—"]]}},

 {"h2": "59 · Thread Local Storage (parte 13)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["thread-local variables", "`I.local` / `I.meu`", "[Por thread](/docs/partida/por-thread)"],
   ["**TLS initialization**", "uma ação que **constrói** o valor, uma vez por thread", "[Por thread](/docs/partida/por-thread)"],
   ["**TLS destructors**", "`ao_terminar`, quando a thread é coletada", "[Por thread](/docs/partida/por-thread)"],
   ["runtime thread state", "`_por_thread` no interpretador: pilha e profundidade já eram por thread", "[Pilha](/docs/partida/pilha)"],
   ["thread-local allocators", "**não se aplica**: quem aloca é o CPython", "—"]]}},

 {"h2": "60 · Stack (parte 13)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["stack frames", "`I.quadros()` — ação, linha e arquivo", "[Pilha](/docs/partida/pilha)"],
   ["stack overflow detection", "teto de mil quadros, com as duas saídas na mensagem", "[Pilha](/docs/partida/pilha)"],
   ["coroutine / fiber stacks", "as [fibras](/docs/runtime/fibras) são **sem pilha**", "[Fibras](/docs/runtime/fibras)"],
   ["stack allocation, probes, guards, growth", "**não se aplica**: a pilha é a do CPython", "—"]]}},

 {"h2": "61 · Variáveis globais (parte 13)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["static/constant initialization", "`steady`, e `comptime` para o que é calculado", "[comptime](/docs/metaprogramacao/comptime)"],
   ["lazy initialization", "o modificador `lazy` em campo de blueprint", "[Modificadores](/docs/oop/modificadores)"],
   ["initialization ordering", "a ordem do arquivo; **ciclo é erro do `check`**, com a cadeia inteira na mensagem", "[Carga](/docs/modulos/carga)"],
   ["destruction", "`defer` de topo roda no fim, na ordem inversa", "[A partida](/docs/partida/inicio)"],
   ["global constructors (C++)", "**não se aplica**", "—"]]}},

 {"h2": "65 · Modelo de segurança (parte 15)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["memory safety", "**por construção**: não há ponteiro na linguagem, e o coletor responde pela memória. A exceção é [`Arcane.C`](/docs/ffi/c), e ela é declarada", "[FFI](/docs/ffi/c)"],
   ["type safety", "`dataforge check`, que **atravessa arquivos**", "[Análise](/docs/tecnicas/analise-estatica)"],
   ["thread safety", "**não automática, e medida**: duas threads escrevendo no mesmo nome perderam 40.425 de 80.000. O `check` avisa (`escrita-concorrente`), e `Arcane.Stm` dá escritas que acontecem juntas", "[STM](/docs/concorrencia/stm)"],
   ["bounds checking", "em execução sempre, e antes de rodar quando se prova (`indice-fora-do-alcance`)", "[Análises](/docs/compilador/analises)"],
   ["null safety", "`??`, `?.`, e o `talvez-nao-definida` do fluxo", "[Análises](/docs/compilador/analises)"],
   ["**integer overflow policies**", "**não há overflow**: o inteiro é de precisão arbitrária. Uma classe inteira de bug não existe aqui — e o preço é a conta ser mais lenta que uma de 64 bits", "[Tipos](/docs/tipos)"],
   ["resource safety", "[`Arcane.Posse`](/docs/memoria/posse): liberação determinística, e o `check` cobra o recurso não solto", "[Posse](/docs/memoria/posse)"],
   ["**capability boundaries**", "`Arcane.Capacidade`", "[Capacidade](/docs/seguranca/capacidade)"]]}},

 {"h2": "66 · `unsafe` (parte 15)"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["raw pointers, manual allocation", "`Arcane.C`: `ponteiro`, `alocar`, `liberar`", "[Ponteiros](/docs/ffi/ponteiros)"],
   ["FFI", "o módulo inteiro **é** a região insegura", "[FFI](/docs/ffi/c)"],
   ["minimizar regiões `unsafe`", "não há bloco `unsafe` a marcar: **o módulo é a fronteira**, e a documentação diz isso em vez de espalhar uma palavra pelo código", "[FFI](/docs/ffi/mapa)"],
   ["validar entradas", "a assinatura é **declarada** e a lista de tipos é fechada; o ponteiro nulo é conferido", "[Chamar C](/docs/ffi/c)"],
   ["encapsular APIs inseguras", "`P.com(P.dono(C.alocar(n), …))` — o bloco sai no fim do escopo, inclusive no caminho de erro", "[Ponteiros](/docs/ffi/ponteiros)"],
   ["documentar precondições", "`expects` / `promises` / `invariant`, cobrados em execução", "[Contratos](/docs/oop/contratos)"],
   ["assembly, SIMD, MMIO, kernel", "**não se aplica** — ver [o mapa de hardware](/docs/hardware/mapa)", "—"]]}},

 {"h2": "O resumo honesto"},
 {"p": "A **parte 13 rendeu** o que dependia do runtime da linguagem (fases visíveis, TLS com finalizador, a pilha que se pergunta) e deixou de fora o que é do CPython (boot, stack probes, guards). A **parte 15 já estava quase toda pronta** — segurança de memória é por construção, e a ausência de *overflow* de inteiro elimina uma classe de bug inteira —, e o que faltava era a **fronteira de capacidade**, que agora existe com os limites escritos em voz alta."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/hardware/mapa",
"title": "Hardware, bare-metal e assembly: o mapa",
"description": "As partes 9, 14 e 16 da referência Deep Tech — e por que nenhuma delas se aplica a uma linguagem interpretada.",
"blocos": [
 {"p": "Três partes de uma referência Deep Tech tratam do que está **abaixo** de uma linguagem interpretada: SIMD e cache, bare-metal e kernel, assembly e microarquitetura."},
 {"p": "A resposta honesta para quase tudo aqui é **não se aplica** — e esta página existe porque um silêncio seria lido como \"ainda não fizemos\", quando o certo é \"isto não é uma lacuna: é o que a escolha de ser interpretada significa\"."},

 {"h2": "42–46 · Otimização de hardware (parte 9)"},
 {"table": {"head": ["Item", "Resposta", "O que existe no lugar"], "rows": [
   ["SIMD, AVX2, AVX-512, ARM Neon", "**não se aplica**: não há registrador vetorial alcançável do CPython", "[a ponte](/docs/tecnicas/ponte) para o `numpy`, que **é** vetorizado — `a * 2` ali é a conta do numpy, não um laço"],
   ["auto-vectorization", "**não se aplica**", "—"],
   ["cache L1/L2/L3, locality, prefetch", "**não se aplica**: o custo de um interpretador de árvore domina qualquer efeito de cache em três ordens de grandeza", "o que **paga** é tirar despacho do caminho quente — e isso está [medido](/docs/compilador/otimizacao)"],
   ["false sharing, cache-line padding", "**não se aplica**", "—"],
   ["AoS vs SoA", "**não se aplica** à memória, mas a **ideia** transfere: o [`Quadro`](/docs/dados/quadro) é colunar por dentro, e é o que torna `descrever` e `correlacao` uma passada por coluna", "[Quadro](/docs/dados/quadro)"],
   ["branch prediction, branchless, pipeline stalls", "**não se aplica**: quem prevê desvio é a CPU rodando o laço do CPython, não o seu `given`", "—"],
   ["**bit manipulation, popcount, rotate, byteswap**", "**parcial**: `Arcane.Bytes` faz `bits`, `de_bits`, `ou_exclusivo`, `inverter` e empacotamento com endianness", "[Bytes](/docs/biblioteca)"],
   ["fences, atomic primitives", "existem, e são de verdade: `C.atomico` com CAS", "[Sem trava](/docs/concorrencia/sem-trava)"],
   ["cycle counters, hardware performance counters", "**não se aplica**: o CPython não os expõe", "[percentis e pausas](/docs/observabilidade/perfil)"]]}},

 {"h2": "62–64 · Bare-metal e embarcados (parte 14)"},
 {"table": {"head": ["Item", "Resposta"], "rows": [
   ["ausência de sistema operacional, entry points, linker scripts", "**não se aplica**: o DataForge precisa de um Python, e um Python precisa de um sistema operacional"],
   ["memory maps, interrupt vectors, MMIO, volatile", "**não se aplica**"],
   ["kernel entry, page tables, syscalls, context switching", "**não se aplica**. A única troca de contexto aqui é a das [fibras](/docs/runtime/fibras), e ela é um quadro de gerador"],
   ["microcontroladores, ARM Cortex-M, RISC-V MCU, RTOS", "**não se aplica**. Existe MicroPython para essa faixa, e ele não é esta linguagem"],
   ["device drivers, DMA, low-power", "**não se aplica** — mas falar com uma biblioteca C que fale com o dispositivo, sim: é [`Arcane.C`](/docs/ffi/c)"]]}},

 {"h2": "67–68 · Assembly e microarquitetura (parte 16)"},
 {"table": {"head": ["Item", "Resposta"], "rows": [
   ["inline assembly, external assembly, registers, CPU flags", "**não se aplica**"],
   ["**calling conventions, ABI, stack frames**", "existem, e são reais — mas **só na fronteira com o C**: [`Arcane.C`](/docs/ffi/c) declara a assinatura e o `ctypes` aplica a ABI da plataforma, com tamanho, alinhamento e padding de verdade"],
   ["atomic instructions", "`C.atomico` (CAS), sobre as primitivas do Python"],
   ["pipeline, superscalar, out-of-order, register renaming", "**não se aplica**: isso acontece na CPU, abaixo do CPython, abaixo do interpretador"],
   ["TLB, memory ordering, hardware prefetching", "**não se aplica**"],
   ["speculative execution", "**não se aplica** — e vale notar que a ausência de ponteiro cru na linguagem tira o DataForge da superfície de ataque de Spectre por construção"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das três partes, **nenhuma tem implementação a fazer**, e duas coisas transferiram: a **ideia** de layout colunar (que o `Quadro` já usa) e as **convenções de chamada**, que são reais na fronteira com o C."},
 {"callout": {"tipo": "nota", "titulo": "Por que escrever um mapa de coisas que não existem", "texto": "Porque a pergunta aparece, e um silêncio é lido como \"ainda não\". Dizer **não se aplica, e aqui está o porquê** custa uma página e evita que alguém procure por semanas uma opção que não pode existir. O teto da compilação para fechamentos está [medido em ~6,5×](/docs/compilador/backend): passar disso exige sair do Python, e aí não é mais esta linguagem."}},
]},
]
