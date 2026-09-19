"""SSA, otimização medida, o backend que existe — e o mapa da parte 8.

Todo bloco `df` destas páginas RODA (`tests/test_ssa_e_otimizacao.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/ssa",
"title": "SSA e o nó φ",
"description": "Uma definição por nome, dominância, fronteira de dominância — e a propagação de constante que fica estritamente mais forte por causa disso.",
"blocos": [
 {"p": "O [MIR](/docs/compilador/mir) diz por onde o programa passa. O que ele **não** diz é *qual* atribuição uma leitura vê. Num corpo com três `x := …`, a pergunta \"de onde vem este `x`?\" precisa ser reconstruída a cada análise — e cada análise que a reconstrói é uma chance de reconstruí-la diferente."},
 {"p": "SSA responde isso por construção: cada nome é **numerado**, cada versão tem **exatamente uma** definição, e onde dois caminhos trazem versões diferentes aparece um nó **φ** que diz de onde cada uma vem."},
 {"code": """given c:                 bloco 0 [entrada] → 1 (sim), 2 (nao)
    x := 1               bloco 1 [sim]      x₁ := 1
otherwise:               bloco 2 [nao]      x₂ := 2
    x := 2               bloco 3 [juncao]   x₃ := φ(1: x₁, 2: x₂)
out x                                       out  le x₃""", "lang": "text", "title": "dataforge ir --fase=ssa"},

 {"h2": "Dominar não é alcançar"},
 {"p": "**Alcançar** é poder chegar; **dominar** é não haver como chegar por outro lado. É essa diferença que decide onde um φ é necessário: um ramo não domina a junção — dá para chegar lá pelo outro ramo —, então a junção precisa de φ. E é a **fronteira de dominância** que diz exatamente onde: o ponto em que a dominância de um bloco acaba."},
 {"code": """adopt Arcane.Compilador as K

fonte := "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n"
forma := K.ssa(fonte)[0]

fis := [f cycle b in forma["blocos"] cycle f in b["fis"]]
assert len(fis) is 1
assert fis[0]["nome"] is "x"
assert len(fis[0]["fontes"]) is 2      // vem dos dois ramos""", "lang": "df"},
 {"code": """adopt Arcane.Compilador as K

// um nome com uma definicao so nao precisa de φ
assert K.ssa("x := 1\\nout x\\n")[0]["blocos"][0]["fis"] is []

// e o laco tem φ na cabeca: o nome volta pela aresta de tras
comLaco := K.ssa("t := 0\\ncycle i in [1, 2]:\\n    t := t + i\\nout t\\n")[0]
cabeca := [b cycle b in comLaco["blocos"] given b["rotulo"] is "condicao"][0]
assert len([f cycle f in cabeca["fis"] given f["nome"] is "t"]) is 1""", "lang": "df"},

 {"h2": "O que ela paga: a propagação fica condicional"},
 {"p": "A [propagação sobre o MIR](/docs/compilador/analises) junta os ramos por **interseção**, e por isso perde o que só um ramo decide. Ela está certa em perder — sem saber qual ramo roda, não há o que concluir."},
 {"p": "Com SSA a análise pode ir além: ela **não avalia** o ramo cuja condição prova falsa. Aí a junção tem um predecessor vivo só, o φ tem uma fonte só, e o valor **se conclui**."},
 {"code": """adopt Arcane.Compilador as K

fonte := "x := 1\\ngiven x bigger 5:\\n    y := \\"nunca\\"\\n" +
         "otherwise:\\n    y := \\"sempre\\"\\nout y\\n"

// o ramo que nao roda e nomeado, com o bloco e a linha
mortos := K.ramos_mortos(fonte)
assert len(mortos) bigger 0
assert mortos[0]["rotulo"] is "sim"

// e o valor de 'y' se conclui — a propagacao sobre o MIR nao sabia
provadas := K.provadas(fonte, "(programa)")
assert "sempre" in values(provadas)""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "É estritamente mais forte, e há teste provando", "texto": "`tests/test_ssa_e_otimizacao.py` roda as duas análises sobre o **mesmo** programa: a do MIR não conclui o `y`, a condicional conclui. Sem essa comparação, \"mais forte\" seria só uma afirmação."}},

 {"h2": "Três decisões"},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["**as instruções não são reescritas** — a versão é *anexada* (`le`, `escreve`)", "um SSA de livro vira três endereços (`t1 := a + b`), e isso cria uma **segunda semântica** para manter em sincronia com o interpretador — o risco que `compilador.py` evita ao delegar aos mesmos auxiliares"],
   ["a dominância sai de um **ponto fixo**, e não de Lengauer-Tarjan", "três vezes mais código para ganhar microssegundos num lugar que roda uma vez por corpo; os corpos desta linguagem têm dezenas de blocos, não milhares"],
   ["o que **não é alcançável** não entra", "um bloco morto teria φ com fonte de lugar nenhum, e a análise passaria a concluir a partir de código que não roda"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A condição da fronteira é fácil de escrever ao contrário", "texto": "A primeira versão perguntava \"`b` domina `atual`?\" onde a pergunta é \"`atual` é o dominador imediato de `b`?\". O resultado: um φ em **todo** bloco de **todo** laço, para nomes que nem se juntavam ali — três φ onde havia um. Um grafo errado não dá erro; ele produz análise com cara de verdade."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/otimizacao",
"title": "O pipeline de otimização, medido",
"description": "Os três passes que existem, o que cada um tira — e o número honesto: 1,33× numa carga feita para eles, 1,01× em código real.",
"blocos": [
 {"p": "Uma referência de linguagem compilada descreve o pipeline do LLVM: inlining, vetorização, análise de alias, otimização de programa inteiro. **Nada disso existe aqui**, e escrever uma função chamada `vetorizar` que não vetoriza seria pior que não ter nenhuma."},
 {"p": "O pipeline desta linguagem é o [compilador de fechamentos](/docs/compilador/analises): a árvore vira funções Python, uma vez. Acima dele há três passes que tiram trabalho **antes** de o fechamento ser construído."},
 {"table": {"head": ["Passe", "O que faz"], "rows": [
   ["`dobra-de-constante`", "`2 + 3 * 4` vira `14`, na carga e não por volta"],
   ["`ramo-morto`", "o ramo cuja condição a [propagação condicional](/docs/compilador/ssa) prova falsa sai da árvore, com o corpo"],
   ["`inalcancavel`", "o que vem depois de um `yield`, `halt` ou `trigger` sai do corpo"]]}},
 {"code": """adopt Arcane.Compilador as K

// duas dobras: '3 * 4' vira 12, e depois '2 + 12' vira 14
assert K.otimizar("x := 2 + 3 * 4\\n")["dobra-de-constante"] is 2

// o ramo provado falso sai inteiro
fonte := "x := 1\\ngiven x bigger 5:\\n    out 1\\notherwise:\\n    out 2\\n"
assert K.otimizar(fonte)["ramo-morto"] bigger 0

// e os passes estao nomeados, com o que cada um faz
assert len(keys(K.passes())) is 3
assert "na carga" in K.passes()["dobra-de-constante"]""", "lang": "df"},

 {"h2": "O número"},
 {"p": "Esta é a parte que interessa, e ela é **desconfortável**. A escolha do que compilar não foi intuição: saiu do [inventário do LIR](/docs/compilador/analises), que conta, por classe de nó, o que recua para o interpretador de árvore — e separa os recuos **dentro de laço**."},
 {"code": """no                           recuos   em laco
Assignment                      229        92     ← v["k"] := x
MorphOperation                   59        59
SkipStatement                    48        46
MembershipOp                    277        23     ← x in xs
TernaryExpression                85        23
CoalesceOp                       90        19     ← a ?? b
UnaryOp                         116        18
TypeofExpression                123        12
SliceAccess                      44         7""", "lang": "text", "title": "O inventário, sobre 388 arquivos do repositório"},
 {"p": "Dez desses nós ganharam construtor no compilador de fechamentos. E o resultado medido:"},
 {"table": {"head": ["Carga", "Antes", "Depois", "Ganho"], "rows": [
   ["feita **dos nós que o inventário aponta**", "507 ms", "382 ms", "**1,33×**"],
   ["59 exercícios **reais** do repositório", "1150 ms", "1143 ms", "**1,01× — nada**"]]}},
 {"callout": {"tipo": "atencao", "titulo": "E o motivo é instrutivo", "texto": "O que recua é dominado por nós que rodam **uma vez** (declaração, `adopt`, `assert` de topo). Os que rodam dentro de laço são poucos por volta, e o trabalho da volta **já estava compilado**: leitura de nome, conta binária, chamada, leitura por índice. Otimizar o que sobra é otimizar 3% de 3%."}},
 {"p": "Por isso os três passes ficam **desligados por padrão**. Eles existem para serem medidos, para `dataforge ir --fase=otimizado` mostrar o que dá para tirar, e porque a conta honesta é a informação — não a promessa de velocidade."},

 {"h2": "Duas regras ao mexer nos passes"},
 {"p": "**A prova é a saída.** Um passe errado não levanta erro: ele muda o resultado. Os testes rodam exercícios do repositório nas duas formas e comparam caractere por caractere — a mesma trava do [HIR](/docs/compilador/hir), pelo mesmo motivo."},
 {"p": "**Nada que possa falhar é dobrado.** É a regra que mais recusa:"},
 {"code": """// '1 / 0' dobrado moveria o erro para a CARGA, longe da linha
// que o causa. Sem dobrar, ele estoura onde esta escrito:
monitor:
    x := 1 / 0
handle Error as e:
    assert e.type is "DivisionByZeroError"
    assert e.line is 4""", "lang": "df"},
 {"table": {"head": ["Não dobra", "Porque"], "rows": [
   ["`1 / 0`, `5 % 0`", "moveria o erro para a carga"],
   ["`\"a\" + 1`", "mudaria a mensagem de erro"],
   ["`2 ** 1000000`", "meio milhão de dígitos montados no carregamento"],
   ["`a + b` com nome", "o valor pode não ser o que parece; quem prova isso é o SSA, não a dobra"],
   ["`yes + 1`", "booleano somando é um acidente, não uma conta"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/backend",
"title": "O backend, e o que ele não é",
"description": "Não há LLVM, não há código de máquina e não há target triple. O que existe no lugar, e por que a troca é essa.",
"blocos": [
 {"p": "Esta página existe porque a pergunta aparece, e porque a resposta certa é um **não** com o motivo — não um silêncio."},
 {"h2": "O que não existe"},
 {"table": {"head": ["Pedido", "Resposta"], "rows": [
   ["emitir LLVM IR", "**não existe**. Emitir texto de IR é fácil; o que vem depois não é — seria preciso `llc` ou `clang` instalado, e aí a linguagem passaria a **depender** de um compilador C para rodar"],
   ["`llvmlite`, `cffi`, qualquer backend em pacote", "**recusado por regra**: `dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar"],
   ["passes LLVM em C++", "**não se aplica**: não há IR para um passe transformar"],
   ["target triple, cross compiler, RISC-V, WebAssembly, bare-metal", "**não existe**. Não há código de máquina a produzir para alvo nenhum"],
   ["debug info (DWARF), intrinsics", "**não se aplica**. A informação de depuração existe, mas é a da linguagem: linha, coluna e o [DAP](/docs/tecnicas/editor)"]]}},
 {"callout": {"tipo": "nota", "titulo": "O teto está medido", "texto": "A compilação para fechamentos rende **1,5× a 1,8×** conforme a carga, e o teto da técnica — o mesmo de uma VM de bytecode escrita em Python — é **~6,5×**. Passar disso exige sair do Python, e aí não é mais esta linguagem. O número está medido, não estimado: `tests/test_desempenho.py`."}},

 {"h2": "O que existe no lugar"},
 {"table": {"head": ["Em vez de", "O DataForge tem"], "rows": [
   ["backend de código de máquina", "`compilador.py` — a árvore vira fechamentos Python, uma vez, com a cobertura **medida** pelo [LIR](/docs/compilador/analises)"],
   ["passes customizados em C++", "[plugins do `check`](/docs/metaprogramacao/plugins) escritos **em DataForge**, que agora veem o MIR e o SSA por `Arcane.Compilador`"],
   ["calling convention e ABI lowering", "existem, e são de verdade — mas só na fronteira com o C: [`Arcane.C`](/docs/ffi/c) declara a assinatura e o `ctypes` aplica a ABI da plataforma"],
   ["cross compilation", "o **release** constrói nas quatro plataformas (Linux, macOS Intel, macOS ARM, Windows), com `.deb`, PKGBUILD e instalador do Windows; e `dataforge devops` gera Dockerfile e manifesto para outra arquitetura"],
   ["instrumentação", "o [MIR](/docs/compilador/mir) e o [SSA](/docs/compilador/ssa) como dado, e `Arcane.Macro` para reescrever corpo de ação"]]}},

 {"h2": "Um passe próprio, escrito na linguagem"},
 {"p": "É o análogo honesto de \"custom pass\": não um `.so` carregado no otimizador, mas uma regra que lê as mesmas representações e devolve diagnóstico."},
 {"code": """adopt Arcane.Compilador as K

// A regra: acusar ramo que nunca roda, com o corpo e a linha.
action verificar(fonte):
    achados := []
    cycle morto in K.ramos_mortos(fonte):
        achados.append($"{morto["corpo"]}:{morto["linha"]} ramo {morto["rotulo"]} nao roda")
    yield achados

suspeito := "x := 1\\ngiven x bigger 5:\\n    out 1\\notherwise:\\n    out 2\\n"
assert len(verificar(suspeito)) bigger 0
assert len(verificar("given entrada:\\n    out 1\\n")) is 0""", "lang": "df"},
 {"p": "A diferença entre isso e um passe do LLVM é real e vale dizer: um passe do LLVM **transforma** o IR que vai gerar código; isto **relata**. Transformar a árvore também é possível — é o que os [passes de otimização](/docs/compilador/otimizacao) fazem —, mas o ganho medido ali é 1,01×, e essa é a razão pela qual a instrumentação é o uso que paga."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/compilador/mapa-backend",
"title": "Backend: o mapa",
"description": "Item por item da parte 8 da referência Deep Tech — LLVM IR, pipeline de otimização, passes customizados e cross compilation — cruzado com o que o DataForge tem.",
"blocos": [
 {"p": "A oitava parte de uma referência Deep Tech é sobre o backend do LLVM. É a **primeira** em que a resposta honesta é em boa medida *não se aplica* — e a parte em que essa resposta é mais útil que qualquer aproximação, porque cada item aqui pressupõe gerar código de máquina."},

 {"h2": "38 · LLVM IR"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["**SSA**", "existe de verdade: `ssa.py`, com dominância, fronteira de dominância e nó φ", "[SSA](/docs/compilador/ssa)"],
   ["**basic blocks**", "`mir.py` — um corpo por ação, arestas rotuladas", "[MIR](/docs/compilador/mir)"],
   ["instructions", "as instruções continuam sendo **nós da árvore**; a versão SSA é anexada, não reescrita em três endereços", "[SSA](/docs/compilador/ssa)"],
   ["metadata, source locations", "`line`/`column` em todo nó, e a ação sabe em que arquivo nasceu", "[Erros](/docs/erros)"],
   ["debug information", "existe, mas é a da linguagem: o [DAP](/docs/tecnicas/editor), com vigia e ponto de parada", "[Editor](/docs/tecnicas/editor)"],
   ["emissão de LLVM IR, tipos LLVM", "**não existe**: emitir o texto é fácil, mas usá-lo exigiria `llc`/`clang` instalado, e a linguagem passaria a depender de um compilador C para rodar", "[Backend](/docs/compilador/backend)"],
   ["intrinsics", "**não se aplica**", "—"],
   ["calling conventions", "só na fronteira com o C, onde são reais", "[FFI](/docs/ffi/c)"]]}},

 {"h2": "39 · Pipeline de otimização"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["constant folding", "`dobra-de-constante`, e nada que possa falhar é dobrado", "[Otimização](/docs/compilador/otimizacao)"],
   ["dead code elimination", "`ramo-morto` (com prova do SSA) e `inalcancavel`; mais `unused-*` no `lint`", "[Otimização](/docs/compilador/otimizacao)"],
   ["o pipeline em si", "`compilador.py`: a árvore vira fechamentos, com cobertura **medida** — 90,9% dos nós do repositório", "[Otimização](/docs/compilador/otimizacao)"],
   ["loop optimization", "**parcial, e pelo outro lado**: o escopo de uma volta é reaproveitado quando o corpo não captura — medido, e a otimização mais perigosa do interpretador", "[Arquitetura](/docs/referencia/arquitetura)"],
   ["inlining", "**não existe**. Numa linguagem em que uma ação pode ser substituída em tempo de execução (`f := outra`, método sobrescrito na filha), embutir o corpo exigiria provar identidade — e é a mesma conferência que a [chamada de cauda](/docs/referencia/arquitetura) faz na hora, em vez de assumir", "—"],
   ["vectorization, alias analysis", "**não se aplica**: não há registrador SIMD nem ponteiro a desambiguar", "—"],
   ["interprocedural / whole-program", "**não existe** no otimizador. O que atravessa fronteira é a **análise**: aridade, tipo de parâmetro e de retorno pelo `adopt`", "[Análise estática](/docs/tecnicas/analise-estatica)"],
   ["global optimization", "**não existe**, e há número dizendo por quê: os passes rendem 1,01× em código real", "[Otimização](/docs/compilador/otimizacao)"]]}},

 {"h2": "40 · Passes customizados"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["custom optimization passes", "`--plugin=` — uma regra escrita **em DataForge**, que vê o MIR e o SSA por `Arcane.Compilador`", "[Backend](/docs/compilador/backend)"],
   ["static analysis", "é o uso que paga: `ramo-morto` e `talvez-nao-definida` nasceram exatamente assim", "[Análises](/docs/compilador/analises)"],
   ["instrumentation", "`Arcane.Macro.reescrever` troca o corpo de uma ação na carga", "[Macros](/docs/metaprogramacao/macros)"],
   ["IR transformation", "os três passes de `otimizar.py`, sobre o HIR", "[Otimização](/docs/compilador/otimizacao)"],
   ["backend hooks", "**parcial**: o que dá para ligar é análise e reescrita de árvore, não a geração de código — porque ela não existe", "[Backend](/docs/compilador/backend)"],
   ["plugins C++, LLVM passes", "**não se aplica**: não há IR do LLVM para transformar", "—"]]}},

 {"h2": "41 · Cross compilation"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["Linux, Windows, macOS", "o `release.yml` constrói nas **quatro** plataformas e roda os exercícios *pelo binário* em cada uma", "[Download](/download)"],
   ["ARM64 e x86_64", "os dois, no macOS; o Linux sai como `.deb` e PKGBUILD", "[Instalação](/docs/instalacao)"],
   ["contêiner para outra arquitetura", "`dataforge devops` gera Dockerfile e manifesto do Kubernetes", "[DevOps](/docs/devops)"],
   ["target triples, cross compiler", "**não existe**: não há código de máquina a produzir, então não há alvo a nomear. O que atravessa plataforma é o **interpretador**, e ele atravessa por ser Python"],
   ["RISC-V, WebAssembly, bare-metal, embarcados", "**não existe**. Rodar em WebAssembly seria rodar o CPython em WebAssembly — o que funciona, e não é uma porta desta linguagem"],
   ["targets personalizados", "**não se aplica**"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das quatro seções, **uma** (§38) transferiu substancialmente — SSA, blocos básicos e dominância são teoria de compilador, não de LLVM, e valem igual num interpretador. Uma segunda (§40) transferiu pelo análogo: o passe customizado existe, escrito na linguagem, e é a forma como os dois diagnósticos novos nasceram. A §39 transferiu **e foi medida**, com o resultado contrariando a expectativa. A §41 não se aplica, e o que ocupa o lugar dela — construir para quatro plataformas — já existia."},
 {"callout": {"tipo": "atencao", "titulo": "O número que esta parte entrega", "texto": "**1,33×** numa carga feita dos nós que o inventário aponta, e **1,01×** em 59 exercícios reais. Dez nós novos compilam, a cobertura subiu, e o relógio não se moveu — porque o trabalho da volta já estava compilado. Este é o tipo de resultado que se publica, não que se esconde: sem ele, a próxima pessoa gastaria a mesma semana."}},
]},
]
