# -*- coding: utf-8 -*-
"""FFI — a página-raiz (que respondia 404) e sete páginas sobre chamar C.

`C.errno` e `C.zerar_errno` entraram nesta leva: toda biblioteca passa a
ser aberta com `use_errno`, e o erro de uma chamada C chega com o nome
(`ENOENT`) e a mensagem do sistema.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi",
"title": "FFI: chamar C",
"description": "Quando uma biblioteca nativa é o único caminho — e o que custa atravessar a fronteira.",
"blocos": [
 {"p": "`Arcane.C` chama funções de bibliotecas nativas — a `libc`, a `libm`, um `.so`/`.dylib`/`.dll` qualquer — sem compilar nada: roda sobre o `ctypes` da biblioteca padrão do Python. É a porta para o que só existe em C: um driver, uma biblioteca de áudio, o código legado da empresa."},
 {"code": '''adopt Arcane.C as C

libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
assert raiz(2.0) bigger 1.414 and raiz(2.0) smaller 1.415''', "lang": "df"},
 {"table": {"head": ["Precisa de", "Use", "Não FFI"], "rows": [
   ["uma biblioteca Python (numpy, pandas)", "—", "[`adopt Python.numpy`](/docs/tecnicas/ponte)"],
   ["um programa de linha de comando", "—", "`Arcane.Process`"],
   ["ler um formato binário", "—", "[`Arcane.Estrutura`](/docs/estruturas)"],
   ["uma função que só existe em C", "**`Arcane.C`**", ""]]}},
 {"callout": {"tipo": "perigo", "titulo": "A fronteira não tem rede", "texto": "Do lado de cá, todo acesso é conferido. Do lado do C, não: uma assinatura errada, um ponteiro solto ou um tamanho trocado corrompem memória, e o processo pode morrer sem mensagem nenhuma. Tudo nesta seção é sobre reduzir esse risco — e ele nunca vai a zero."}},
 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/ffi/c", "title": "Chamar C", "desc": "carregar, declarar a assinatura, chamar"},
   {"href": "/docs/ffi/tipos", "title": "Os tipos do C", "desc": "qual tipo daqui para qual de lá, e o long que muda de tamanho"},
   {"href": "/docs/ffi/textos", "title": "Textos e char*", "desc": "codificação, NULL e quem libera"},
   {"href": "/docs/ffi/erros", "title": "Erros e errno", "desc": "o -1, o NULL e o ENOENT"},
   {"href": "/docs/ffi/ponteiros", "title": "Ponteiros e memória crua", "desc": "alocar, andar e liberar"},
   {"href": "/docs/ffi/callbacks", "title": "Callbacks", "desc": "o C chamando uma ação DataForge"},
   {"href": "/docs/ffi/bibliotecas", "title": "Achar a biblioteca", "desc": "Linux, macOS e Windows"},
   {"href": "/docs/ffi/seguranca", "title": "Segurança na fronteira", "desc": "o que corrompe memória, e como evitar"},
   {"href": "/docs/ffi/desempenho", "title": "Custo de uma chamada", "desc": "quando vale atravessar, e quando não"},
   {"href": "/docs/ffi/mapa", "title": "FFI: o mapa", "desc": "tudo o que existe, e o que não"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/tipos",
"title": "Os tipos do C",
"description": "Qual tipo declarar para cada tipo do C — e os três que mudam de tamanho conforme a plataforma.",
"blocos": [
 {"p": "A assinatura declarada é a única coisa que o `ctypes` sabe sobre a função. Um `i32` onde o C espera `i64` passa em quase toda chamada — e corrompe o resto da pilha na que não passa. O tipo precisa ser o **do C**, e não o do valor que você tem."},
 {"table": {"head": ["No C", "Declare", "Cuidado"], "rows": [
   ["`int`, `int32_t`", "`i32`", "—"],
   ["`unsigned int`, `uint32_t`", "`u32`", "—"],
   ["`long`", "`i64` no Linux/macOS 64 bits, `i32` no Windows", "o motivo de existir `int64_t`"],
   ["`long long`, `int64_t`", "`i64`", "—"],
   ["`size_t`", "`tamanho`", "4 ou 8 bytes conforme a plataforma"],
   ["`double` / `float`", "`f64` / `f32`", "passar `f32` onde o C quer `double` dá lixo"],
   ["`char*` (texto)", "`texto`", "ver [Textos](/docs/ffi/textos)"],
   ["`void*`, qualquer ponteiro", "`ponteiro`", "o tipo do alvo você carrega à parte"],
   ["`char` (um caractere)", "`char`", "—"],
   ["nada (`void`)", "`void`", "só como retorno"]]}},
 {"code": '''adopt Arcane.C as C

assert C.tamanho_de("i32") is 4
assert C.tamanho_de("f64") is 8
assert C.tamanho_de("tamanho") in [4, 8]          // size_t acompanha a plataforma
assert C.tamanho_de("ponteiro") is C.tamanho_de("tamanho")
out C.tipos()''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Olhe o cabeçalho, não a documentação", "texto": "A assinatura certa está no `.h` da biblioteca. `man 3 strlen` diz `size_t strlen(const char *s)` — então `[\"texto\"]` e retorno `\"tamanho\"`, e não `i32`, mesmo que o número caiba."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/textos",
"title": "Textos e char*",
"description": "UTF-8 na ida, o NULL que vira void na volta, e o texto que o C alocou e alguém precisa liberar.",
"blocos": [
 {"p": "No C, texto é um ponteiro para bytes terminados em zero — sem codificação declarada e sem tamanho. Declarado como `texto`, o parâmetro vai em **UTF-8** com o zero no fim, e o retorno volta como texto da linguagem, lido até o primeiro zero."},
 {"code": '''adopt Arcane.C as C

libc := C.padrao()
tamanho := libc.funcao("strlen", ["texto"], "tamanho")
comparar := libc.funcao("strcmp", ["texto", "texto"], "i32")
ambiente := libc.funcao("getenv", ["texto"], "texto")

assert tamanho("café") is 5                       // BYTES em UTF-8, não letras
assert comparar("abc", "abd") smaller 0
assert ambiente("NAO_EXISTE_DE_JEITO_NENHUM") is void   // o NULL do C''', "lang": "df"},
 {"h2": "Três armadilhas"},
 {"table": {"head": ["Armadilha", "O que acontece"], "rows": [
   ["o C conta **bytes**", "`strlen(\"café\")` é 5: o `é` ocupa dois"],
   ["um zero no meio", "o C para ali: `\"a\\x00b\"` chega como `\"a\"`"],
   ["texto alocado pelo C", "`strdup`, `getline`: quem recebe **libera** — do lado de cá, com a função de liberar da própria biblioteca"]]}},
 {"callout": {"tipo": "atencao", "titulo": "O texto de retorno é uma cópia", "texto": "O retorno `texto` é **copiado** para um texto da linguagem na hora. Se a função devolveu memória que ela alocou (`strdup`), essa memória continua lá — a cópia não a libera. Declare o retorno como `ponteiro`, leia com `ponteiro.texto()`, e chame o `free` da biblioteca."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/erros",
"title": "Erros e errno",
"description": "O C não levanta: devolve -1 ou NULL, e deixa o motivo em errno. C.errno lê o motivo com nome e mensagem.",
"blocos": [
 {"p": "Uma função C não tem exceção. Ela avisa que falhou pelo **retorno** — `-1`, `NULL`, zero — e deixa o motivo numa variável global chamada `errno`: `ENOENT` (não existe), `EACCES` (sem permissão), `EINTR` (interrompida por sinal)…"},
 {"code": '''adopt Arcane.C as C

libc := C.padrao()
abrir := libc.funcao("open", ["texto", "i32"], "i32")

C.zerar_errno()
fd := abrir("/este/caminho/nao/existe", 0)
assert fd is -1                              // o retorno diz QUE falhou

erro := C.errno()                            // o errno diz POR QUE
assert erro["nome"] is "ENOENT"
out erro["mensagem"]''', "lang": "df"},
 {"h2": "As regras do errno"},
 {"list": [
   "**Só leia depois de uma falha.** Numa chamada que deu certo, o errno pode ter qualquer valor — a norma do C não manda zerá-lo. Ler o errno de um sucesso é ler o erro de outra chamada.",
   "**Leia logo.** Toda biblioteca aqui é aberta com `use_errno`: o ctypes guarda uma cópia **por thread**, logo depois de cada chamada. Sem isso, o errno seria sobrescrito pela próxima coisa que o próprio Python fizesse.",
   "**`zerar_errno` antes, quando o retorno é ambíguo.** `strtol` devolve 0 tanto para \"0\" quanto para erro: zerar antes e olhar depois é o único jeito de distinguir."]},
 {"code": '''adopt Arcane.C as C

libc := C.padrao()
abrir := libc.funcao("open", ["texto", "i32"], "i32")

action abrir_ou_explicar(caminho):
    C.zerar_errno()
    fd := abrir(caminho, 0)
    given fd is -1:
        e := C.errno()
        trigger $"não abri '{caminho}': {e["mensagem"]} ({e["nome"]})"
    yield fd

motivo := void
monitor:
    abrir_ou_explicar("/nao/existe")
handle Error as e:
    motivo := e.message
assert motivo.contains("ENOENT")''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Por que não levantar sozinho", "texto": "O `ctypes` não sabe qual retorno de cada função significa falha: `-1` é erro no `open`, e um resultado válido numa função de temperatura. Quem sabe é a documentação da função — por isso a conferência fica na sua ação, como acima."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/bibliotecas",
"title": "Achar a biblioteca",
"description": "O nome do arquivo em cada sistema, onde ele é procurado, e o que fazer quando não acha.",
"blocos": [
 {"p": "A mesma biblioteca tem três nomes: `libz.so.1` no Linux, `libz.dylib` no macOS, `zlib1.dll` no Windows. `C.carregar(\"z\")` procura pelo nome curto no lugar em que o sistema procura, e aceita também o caminho completo."},
 {"code": '''adopt Arcane.C as C

libc := C.padrao()                  // libc, ou msvcrt no Windows
assert libc.tem("strlen")
assert not libc.tem("funcao_que_nao_existe")

falhou := no
monitor:
    C.carregar("biblioteca_que_nao_existe_aqui")
handle RuntimeError as e:
    falhou := yes
    out e.message
assert falhou''', "lang": "df"},
 {"table": {"head": ["Sistema", "Arquivo", "Onde procura", "Se não achar"], "rows": [
   ["Linux", "`libNOME.so`", "`/usr/lib`, `/lib`, `LD_LIBRARY_PATH`", "instale o pacote `-dev`"],
   ["macOS", "`libNOME.dylib`", "`/usr/lib`, Homebrew, `DYLD_LIBRARY_PATH`", "`brew install NOME`, ou o caminho completo"],
   ["Windows", "`NOME.dll`", "a pasta do programa, `PATH`", "ponha a pasta da DLL no `PATH`"]]}},
 {"callout": {"tipo": "atencao", "titulo": "`tem` antes de `funcao`", "texto": "A mesma biblioteca muda entre versões: uma função nova numa versão, removida em outra. `libc.tem(\"nome\")` pergunta sem levantar, e deixa o programa escolher outro caminho em vez de morrer na primeira chamada."}},
 {"p": "`C.do_processo()` abre os símbolos do próprio processo — o `dlopen(NULL)` —, e `C.matematica()` resolve a `libm`, que no macOS mora dentro da `libSystem`."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/seguranca",
"title": "Segurança na fronteira",
"description": "As cinco formas de corromper memória chamando C, e a conferência que cada uma pede.",
"blocos": [
 {"p": "Do lado do DataForge, todo índice é conferido e nenhum ponteiro solto existe. Do lado do C, nada disso vale. Os defeitos abaixo não dão erro na linha que os causa: aparecem depois, em outro lugar, ou derrubam o processo sem mensagem."},
 {"table": {"head": ["Defeito", "Como acontece", "A conferência"], "rows": [
   ["assinatura errada", "`i32` onde o C quer `i64`, `f32` onde quer `double`", "copie do `.h`, nunca de memória"],
   ["buffer pequeno", "passar 16 bytes para uma função que escreve 64", "alocar o que a documentação pede, com folga"],
   ["uso depois de liberar", "guardar um ponteiro de um bloco já liberado", "`C.liberar` num lugar só, e nada guarda o ponteiro depois"],
   ["callback coletado", "o C guarda a função e chama depois que o lado de cá a soltou", "manter a referência viva enquanto o C puder chamar"],
   ["thread errada", "biblioteca que não é thread-safe chamada de duas threads", "um `mutex` em volta de toda chamada a ela"]]}},
 {"code": '''adopt Arcane.C as C

bloco := C.alocar(4 * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")
p.escrever(7)
assert p.ler() is 7
C.liberar(bloco)

recusado := no
monitor:
    C.ponteiro(C.nulo(), "i32").ler()      // o nulo é recusado, e não lido
handle Error:
    recusado := yes
assert recusado''', "lang": "df"},
 {"callout": {"tipo": "perigo", "titulo": "Nunca com entrada de fora sem conferir", "texto": "Um tamanho que vem de um arquivo ou de um pedido HTTP e vai direto para uma função C é o estouro de buffer clássico, agora no seu programa. Confira o tamanho do lado de cá — onde a conferência existe — antes de atravessar."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ffi/desempenho",
"title": "O custo de uma chamada",
"description": "Atravessar a fronteira custa microssegundos: um milhão de chamadas pequenas perde para um laço daqui.",
"blocos": [
 {"p": "Chamar C não é de graça: cada chamada converte os argumentos, atravessa o `ctypes` e converte o retorno — alguns **microssegundos**. Para uma função que trabalha milissegundos (comprimir, decodificar, resolver um sistema), isso some. Para `abs(x)` num laço de um milhão, isso **é** o tempo."},
 {"code": '''adopt Arcane.C as C

libc := C.padrao()
abs_c := libc.funcao("abs", ["i32"], "i32")

// correto, mas cada chamada atravessa a fronteira
soma := 0
cycle i in range(-500, 500):
    soma += abs_c(i)
assert soma is 250000

// o mesmo, sem atravessar nada
assert ([abs(i) cycle i in range(-500, 500)] >> distill a, v: a + v 0) is 250000''', "lang": "df"},
 {"table": {"head": ["Vale atravessar", "Não vale"], "rows": [
   ["uma chamada que faz muito trabalho", "muitas chamadas que fazem pouco"],
   ["passar um bloco inteiro de uma vez", "passar item a item"],
   ["a função só existe em C", "a mesma conta existe na linguagem"]]}},
 {"p": "A regra de ouro: **atravesse com lotes**. Uma função C que recebe um ponteiro e um tamanho processa um milhão de itens numa chamada só — o `qsort` no exemplo de [Callbacks](/docs/ffi/callbacks) é o modelo. E meça antes de concluir: [`dataforge profile`](/docs/cli/analise) mostra onde o tempo vai."},
]},
]
