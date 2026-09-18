"""FFI com C: bibliotecas, ponteiros, callbacks — e o mapa da parte 6.

Todo bloco `df` destas páginas RODA (`tests/test_ffi_c.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/c",
"title": "Chamar C",
"description": "Arcane.C: abrir uma biblioteca nativa, declarar a assinatura, ler o layout de uma struct e chamar função — sobre ctypes, sem dependência.",
"blocos": [
 {"p": "A [ponte para o Python](/docs/tecnicas/ponte) resolve \"preciso de uma biblioteca que alguém já escreveu **em Python**\". Faltava o degrau de baixo: chamar uma função de uma biblioteca **C** — a `libm`, a `libz`, o `.so` que a empresa mantém há quinze anos — sem escrever módulo de extensão."},
 {"code": """adopt Arcane.C as C

libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
potencia := libm.funcao("pow", ["f64", "f64"], "f64")

assert raiz(16.0) is 4.0
assert potencia(2.0, 10.0) is 1024.0""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Zero dependência continua valendo", "texto": "Isto roda sobre o `ctypes`, que é da biblioteca padrão do Python. Nada é instalado, nada é compilado, e o módulo funciona no mesmo lugar em que o DataForge já funciona."}},

 {"h2": "A assinatura é declarada"},
 {"p": "`funcao(nome, [argumentos], retorno)` obriga a dizer os tipos. Adivinhar erra fora do caso comum: um `i32` onde o C espera `i64` passa em quase toda chamada e corrompe memória no resto — em silêncio, e longe da linha que causou."},
 {"table": {"head": ["Tipo", "No C"], "rows": [
   ["`i8` `i16` `i32` `i64`", "`int8_t` … `int64_t`"],
   ["`u8` `u16` `u32` `u64`", "`uint8_t` … `uint64_t`"],
   ["`f32` `f64`", "`float`, `double`"],
   ["`bool` `char`", "`bool`, `char`"],
   ["`texto`", "`const char*` (vai e volta como texto UTF-8)"],
   ["`bytes`", "`const char*` cru, sem conversão"],
   ["`ponteiro`", "`void*` — qualquer endereço"],
   ["`tamanho`", "`size_t`"],
   ["`void`", "só como retorno"]]}},
 {"code": """adopt Arcane.C as C

libc := C.padrao()
tamanho := libc.funcao("strlen", ["texto"], "tamanho")
absoluto := libc.funcao("abs", ["i32"], "i32")

assert tamanho("dataforge") is 9
assert absoluto(-42) is 42

assert libc.tem("strlen")
assert not libc.tem("nao_existe_mesmo")""", "lang": "df"},

 {"h2": "Quando não dá, a mensagem diz o que fazer"},
 {"p": "Biblioteca que não abre e símbolo que não existe são os dois erros mais comuns de FFI — e os dois chegam do sistema ilegíveis. Aqui eles dizem o nome, onde foi procurado e o caminho de saída, por sistema operacional."},
 {"code": """adopt Arcane.C as C

monitor:
    C.carregar("libnaoexisteaqui")
    assert no
handle RuntimeError as e:
    assert "libnaoexisteaqui" in e.message""", "lang": "df"},

 {"h2": "Struct: o layout de verdade"},
 {"p": "Tamanho, alinhamento e deslocamento vêm da ABI da plataforma — é a parte que ninguém acerta de cabeça, e a que quebra quando a struct do C muda."},
 {"code": """adopt Arcane.C as C

Ponto := C.estrutura([["x", "f64"], ["y", "f64"]])
assert Ponto.tamanho() is 16
assert Ponto.deslocamentos() is {"x": 0, "y": 8}

// o padding aparece: um i8 antes de um i32 não ocupa 5 bytes
Mista := C.estrutura([["flag", "i8"], ["valor", "i32"]])
assert Mista.tamanho() is 8
assert Mista.deslocamentos()["valor"] is 4
assert Mista.alinhamento() is 4""", "lang": "df"},
 {"code": """adopt Arcane.C as C

Ponto := C.estrutura([["x", "i32"], ["y", "i32"]])
p := Ponto.criar({"x": 3, "y": 4})

assert p.ler("x") is 3
p.escrever("x", 30)
assert p.tudo() is {"x": 30, "y": 4}

// a união ocupa o maior campo
U := C.uniao([["i", "i32"], ["f", "f64"]])
assert U.tamanho() is C.tamanho_de("f64")""", "lang": "df"},
 {"p": "Um `enum` do C é inteiro com nome, e aqui ele é um vault — `C.enumeracao({\"VERMELHO\": 0, \"VERDE\": 1})`. Não há tipo novo a criar: o que atravessa a fronteira é o número, e um embrulho só esconderia isso."},

 {"h2": "O que o sistema responde"},
 {"code": """adopt Arcane.C as C

assert C.tamanho_de("i8") is 1
assert C.tamanho_de("i32") is 4
assert C.tamanho_de("f64") is 8
assert C.tamanho_de("ponteiro") in [4, 8]
assert C.endianness() in ["little", "big"]
assert "i32" in C.tipos()""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/ponteiros",
"title": "Ponteiros e memória crua",
"description": "Endereço com tipo, aritmética de ponteiro, memória alocada à mão e o nulo que se reconhece antes de derrubar o processo.",
"blocos": [
 {"p": "Um ponteiro aqui é um **endereço com tipo**. O tipo não é decoração: é ele que diz quanto `deslocar(1)` anda e como `ler()` interpreta os bytes."},
 {"code": """adopt Arcane.C as C

bloco := C.alocar(4 * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")

cycle i from 0 to 3:
    p.deslocar(i).escrever(i * 10)

assert p.ler() is 0
assert p.deslocar(2).ler() is 20
assert [p.deslocar(i).ler() cycle i in range(0, 4)] is [0, 10, 20, 30]

C.liberar(bloco)""", "lang": "df"},
 {"table": {"head": ["Símbolo", "O que faz"], "rows": [
   ["`C.ponteiro(alvo, tipo)`", "ponteiro a partir de endereço, bloco ou struct"],
   ["`p.ler()` · `p.escrever(v)`", "lê e escreve **no tipo declarado**"],
   ["`p.deslocar(n)`", "anda `n` **itens** — a aritmética de ponteiro"],
   ["`p.deslocar_bytes(n)`", "anda `n` bytes, quando o passo não é o tipo"],
   ["`p.como(tipo)`", "o mesmo endereço lido como outro tipo — o cast"],
   ["`p.bytes(n)` · `p.texto()`", "lê memória crua, ou uma string terminada em zero"],
   ["`p.endereco()` · `p.e_nulo()`", "o número, e a pergunta que evita o desastre"]]}},

 {"h2": "O nulo é conferido"},
 {"p": "Ler um endereço nulo derruba o processo, e a pilha não fala do DataForge. Essa é a única conferência que **vale** o custo — o resto da segurança de memória, em FFI, é de quem chama."},
 {"code": """adopt Arcane.C as C

nulo := C.nulo()
assert nulo.e_nulo() and nulo.endereco() is 0

monitor:
    nulo.ler()
    assert no
handle RuntimeError as e:
    assert "nulo" in e.message""", "lang": "df"},

 {"h2": "Memória alocada à mão"},
 {"code": """adopt Arcane.C as C
adopt Arcane.Bytes as B

dados := C.de_bytes("dataforge")
assert B.para_texto(C.para_bytes(dados, 9)) is "dataforge"
assert dados.tamanho() is 10          // o zero do fim conta

outro := C.alocar(16)
C.copiar(outro, dados, 9)
assert B.para_texto(C.para_bytes(outro, 9)) is "dataforge"

C.liberar(dados)
C.liberar(outro)""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Usar memória liberada é o defeito que mais derruba processo em C", "texto": "`liberar` é idempotente, e um bloco já liberado recusa com o motivo em vez de entregar lixo. Para não depender de disciplina, guarde o bloco num [`P.dono`](/docs/memoria/posse) e deixe `P.com(…)` liberar — inclusive no caminho de erro."}},
 {"code": """adopt Arcane.C as C
adopt Arcane.Posse as P

// o bloco sai junto com o escopo, mesmo se o corpo falhar
valor := P.com(P.dono(C.alocar(32), lambda b => C.liberar(b)),
               lambda bloco => bloco.tamanho())

assert valor is 32""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/callbacks",
"title": "Callbacks: o C chamando você",
"description": "Uma ação DataForge vista pelo C como ponteiro de função — com tempo de vida explícito, porque um callback coletado derruba o processo.",
"blocos": [
 {"p": "Metade das bibliotecas C úteis pede um **ponteiro de função**: `qsort` pede o comparador, a libcurl pede o recebedor, a libz pede o alocador. `C.retorno_de_chamada` transforma uma ação da linguagem nisso."},
 {"code": """adopt Arcane.C as C

libc := C.padrao()
qsort := libc.funcao("qsort",
                     ["ponteiro", "tamanho", "tamanho", "ponteiro"], "void")

numeros := [42, 7, 19, 3]
bloco := C.alocar(len(numeros) * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")
cycle i in range(0, len(numeros)):
    p.deslocar(i).escrever(numeros[i])

action comparar(a, b):
    yield C.ponteiro(a, "i32").ler() - C.ponteiro(b, "i32").ler()

comparador := C.retorno_de_chamada(comparar, ["ponteiro", "ponteiro"], "i32")
qsort(bloco, 4, C.tamanho_de("i32"), comparador)

assert [p.deslocar(i).ler() cycle i in range(0, 4)] is [3, 7, 19, 42]
C.liberar(bloco)""", "lang": "df"},
 {"p": "O `qsort` do C chamou uma ação escrita em DataForge, quatro a seis vezes, e ordenou memória crua com o resultado."},

 {"h2": "Tempo de vida: o detalhe que derruba processo"},
 {"p": "O callback precisa continuar vivo enquanto o C puder chamá-lo. Um callback coletado no meio de um `qsort` derruba o processo — e a pilha não fala do DataForge. Por isso ele é um **objeto que se segura**, e que responde se ainda vale."},
 {"code": """adopt Arcane.C as C

action dobro(x):
    yield x * 2

cb := C.retorno_de_chamada(dobro, ["i32"], "i32")

assert cb.vivo()
assert cb.chamar(21) is 42           // chama pela ponte do C
assert cb.endereco() bigger 0        // é um ponteiro de função de verdade

cb.soltar()
assert not cb.vivo()""", "lang": "df"},
 {"table": {"head": ["Item da literatura", "Aqui"], "rows": [
   ["function pointer", "`cb.endereco()` — e o próprio `cb` passa como `ponteiro`"],
   ["closure como callback", "a ação leva o fechamento dela; o C não sabe disso, e não precisa"],
   ["context pointer (`void* user_data`)", "declare um `ponteiro` a mais na assinatura e leia-o dentro da ação"],
   ["static trampoline", "é o que o `ctypes` monta por baixo — não há o que escrever"],
   ["callback lifecycle", "explícito: `vivo()` e `soltar()`"],
   ["ABI-safe", "a assinatura é declarada; errar o tipo aqui é o mesmo desastre de errar no C"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/mapa",
"title": "FFI: o mapa",
"description": "Item por item da parte 6 da referência Deep Tech — C/C++, ponteiros crus, callbacks e bibliotecas dinâmicas — cruzado com o que o DataForge tem.",
"blocos": [
 {"p": "A sexta parte de uma referência Deep Tech cobre interoperabilidade com C/C++, ponteiros crus, callbacks e bibliotecas dinâmicas. Quase tudo isso existe aqui — porque FFI é sobre **protocolo de chamada**, e isso não depende de a linguagem ser compilada."},

 {"h2": "26 · Interoperabilidade C/C++"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["FFI, C function calls", "`C.carregar(…)` e `lib.funcao(nome, [tipos], retorno)`", "[Chamar C](/docs/ffi/c)"],
   ["C structs, unions", "`C.estrutura`, `C.uniao` — com tamanho, alinhamento e deslocamentos", "[Chamar C](/docs/ffi/c)"],
   ["C enums", "`C.enumeracao({…})`: inteiro com nome, que é o que atravessa", "[Chamar C](/docs/ffi/c)"],
   ["data layout, ABI compatibility", "vem do `ctypes`, que segue a ABI da plataforma", "[Chamar C](/docs/ffi/c)"],
   ["calling conventions", "a padrão (`cdecl`) é a que o `ctypes` usa; `stdcall` do Windows **não** está exposto", "—"],
   ["C++ interoperability, name mangling", "**só via `extern \"C\"`**: o nome decorado do C++ não é estável entre compiladores, e resolvê-lo seria adivinhar", "[Chamar C](/docs/ffi/c)"],
   ["headers, bindings automáticos", "**não existem**: não há leitor de `.h`. A assinatura é declarada à mão — e declarar é o que impede o erro silencioso", "—"]]}},

 {"h2": "27 · Ponteiros crus"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["`*mut T` / `*const T`", "`C.ponteiro(alvo, tipo)` — um só, sem distinção de mutabilidade", "[Ponteiros](/docs/ffi/ponteiros)"],
   ["pointer arithmetic", "`p.deslocar(n)` (itens) e `p.deslocar_bytes(n)`", "[Ponteiros](/docs/ffi/ponteiros)"],
   ["dereference", "`p.ler()` e `p.escrever(v)`, no tipo declarado", "[Ponteiros](/docs/ffi/ponteiros)"],
   ["raw memory, manual allocation/deallocation", "`C.alocar`, `C.liberar`, `C.copiar`, `C.de_bytes`, `C.para_bytes`", "[Ponteiros](/docs/ffi/ponteiros)"],
   ["memory alignment", "`C.alinhamento_de(tipo)` e `Molde.alinhamento()`", "[Chamar C](/docs/ffi/c)"],
   ["`unsafe` blocks", "**não existem**: não há bloco a marcar. O módulo inteiro é a fronteira insegura, e a documentação diz isso em vez de espalhar uma palavra", "—"]]}},

 {"h2": "28 · Callbacks cross-language"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["funções como callbacks", "`C.retorno_de_chamada(acao, [tipos], retorno)`", "[Callbacks](/docs/ffi/callbacks)"],
   ["closures", "a ação leva o fechamento; o C não sabe, e não precisa saber", "[Callbacks](/docs/ffi/callbacks)"],
   ["function pointers", "`cb.endereco()`, e o próprio `cb` passa como `ponteiro`", "[Callbacks](/docs/ffi/callbacks)"],
   ["context pointers", "declare um `ponteiro` a mais na assinatura", "[Callbacks](/docs/ffi/callbacks)"],
   ["callback lifecycle", "explícito: `vivo()` / `soltar()` — um callback coletado derruba o processo", "[Callbacks](/docs/ffi/callbacks)"],
   ["static trampolines", "o `ctypes` monta; não há o que escrever", "—"]]}},

 {"h2": "29 · Bibliotecas dinâmicas"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["`dlopen`, runtime loading", "`C.carregar(nome_ou_caminho)`", "[Chamar C](/docs/ffi/c)"],
   ["`dlsym`, symbol resolution", "`lib.tem(nome)` e `lib.funcao(nome, …)`, com erro que nomeia o símbolo", "[Chamar C](/docs/ffi/c)"],
   [".so, .dylib, .dll", "os três, pelo mesmo `carregar`; a busca usa o mecanismo do sistema", "[Chamar C](/docs/ffi/c)"],
   ["símbolos do próprio processo", "`C.do_processo()` — o `dlopen(NULL)`", "[Chamar C](/docs/ffi/c)"],
   ["static linking", "**não se aplica**: não há binário a ligar — o DataForge é interpretado", "—"],
   ["plugin architectures", "duas formas: `.so` carregado com `C.carregar`, e [plugin do `check`](/docs/metaprogramacao/plugins) escrito em DataForge", "[Plugins](/docs/metaprogramacao/plugins)"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Esta é a parte com a **maior cobertura** de todas até aqui: das quatro seções, três estão quase inteiras, e a quarta (C/C++) só deixa de fora o que depende de ler cabeçalho ou de decodificar nome de C++ — duas coisas que, feitas por adivinhação, produziriam exatamente o tipo de erro que FFI já tem demais."},
 {"callout": {"tipo": "atencao", "titulo": "A regra que vale para o módulo inteiro", "texto": "Nada aqui é seguro, e o módulo não finge. Ponteiro cru, aritmética de endereço e `liberar` são ferramentas de quem sabe o que está fazendo. O que dá para conferir sem custo — ponteiro nulo, tipo desconhecido, símbolo ausente, aridade errada — é conferido; o resto é responsabilidade de quem chama. Para não depender de disciplina, junte com [`Arcane.Posse`](/docs/memoria/posse): o bloco sai no fim do escopo, inclusive quando o corpo falha."}},
]},
]
