// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "41 · FFI e nativo",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 41`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[259](#259-chamar-c-bibliotecas-ponteiros-e-callbacks)", "**chamar C: bibliotecas, ponteiros e callbacks**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "259 · chamar C: bibliotecas, ponteiros e callbacks"},
  { code: `// A ponte para o Python resolve "preciso de algo que alguem escreveu em
// Python". Este e o degrau de baixo: chamar funcao de biblioteca C — a
// libm, a libz, o .so que a empresa mantem ha quinze anos — sem escrever
// modulo de extensao e sem trazer dependencia.

adopt Arcane.C as C
adopt Arcane.Bytes as B
adopt Arcane.Posse as P

// ── abrir e chamar, com a assinatura declarada ──
libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
potencia := libm.funcao("pow", ["f64", "f64"], "f64")

assert raiz(16.0) is 4.0
assert potencia(2.0, 10.0) is 1024.0

libc := C.padrao()
tamanho := libc.funcao("strlen", ["texto"], "tamanho")
absoluto := libc.funcao("abs", ["i32"], "i32")

assert tamanho("dataforge") is 9
assert absoluto(-42) is 42

// a biblioteca diz o que ela tem, antes de tentar
assert libc.tem("strlen")
assert not libc.tem("nao_existe_mesmo")

// declarar o tipo e o que impede o erro silencioso: um i32 onde o C
// espera i64 passa em quase toda chamada e corrompe memoria no resto
monitor:
    C.tamanho_de("inteirao")
    assert no
handle RuntimeError as e:
    assert "inteirao" in e.message

// os dois erros mais comuns de FFI dizem o nome e o caminho de saida
monitor:
    C.carregar("libnaoexisteaqui")
    assert no
handle RuntimeError as e:
    assert "libnaoexisteaqui" in e.message

monitor:
    libc.funcao("funcao_que_nao_existe", [], "i32")
    assert no
handle RuntimeError as e:
    assert "funcao_que_nao_existe" in e.message

// ── o layout de verdade: tamanho, alinhamento, deslocamento ──
assert C.tamanho_de("i8") is 1
assert C.tamanho_de("i32") is 4
assert C.tamanho_de("ponteiro") in [4, 8]
assert C.endianness() in ["little", "big"]

Ponto := C.estrutura([["x", "f64"], ["y", "f64"]])
assert Ponto.tamanho() is 16
assert Ponto.deslocamentos() is {"x": 0, "y": 8}

// o padding aparece: um i8 antes de um i32 nao ocupa 5 bytes
Mista := C.estrutura([["flag", "i8"], ["valor", "i32"]])
assert Mista.tamanho() is 8
assert Mista.deslocamentos()["valor"] is 4
assert Mista.alinhamento() is 4

Par := C.estrutura([["x", "i32"], ["y", "i32"]])
par := Par.criar({"x": 3, "y": 4})
assert par.ler("x") is 3
par.escrever("x", 30)
assert par.tudo() is {"x": 30, "y": 4}

// a uniao ocupa o maior campo
U := C.uniao([["i", "i32"], ["f", "f64"]])
assert U.tamanho() is C.tamanho_de("f64")

// um enum do C e inteiro com nome, e e o numero que atravessa
Cor := C.enumeracao({"VERMELHO": 0, "VERDE": 1})
assert Cor["VERDE"] is 1

// ── ponteiro cru: um endereco COM TIPO ──
bloco := C.alocar(4 * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")

cycle i from 0 to 3:
    p.deslocar(i).escrever(i * 10)

assert p.ler() is 0
assert p.deslocar(2).ler() is 20
assert [p.deslocar(i).ler() cycle i in range(0, 4)] is [0, 10, 20, 30]
C.liberar(bloco)

// o nulo e a unica conferencia que vale o custo: ler um endereco nulo
// derruba o processo, e a pilha nao fala do DataForge
nulo := C.nulo()
assert nulo.e_nulo() and nulo.endereco() is 0

monitor:
    nulo.ler()
    assert no
handle RuntimeError as e:
    assert "nulo" in e.message

// bytes vao e voltam
dados := C.de_bytes("dataforge")
assert B.para_texto(C.para_bytes(dados, 9)) is "dataforge"
assert dados.tamanho() is 10  // o zero do fim conta
C.liberar(dados)

// para nao depender de disciplina: o bloco sai com o escopo, inclusive
// quando o corpo falha
medido := P.com(P.dono(C.alocar(32), lambda b => C.liberar(b)),
    lambda b => b.tamanho())
assert medido is 32

// ── callback: o C chamando uma acao do DataForge ──
qsort := libc.funcao("qsort",
    ["ponteiro", "tamanho", "tamanho", "ponteiro"], "void")

numeros := [42, 7, 19, 3]
area := C.alocar(len(numeros) * C.tamanho_de("i32"))
q := C.ponteiro(area, "i32")
cycle i in range(0, len(numeros)):
    q.deslocar(i).escrever(numeros[i])

action comparar(a, b):
    yield C.ponteiro(a, "i32").ler() - C.ponteiro(b, "i32").ler()

comparador := C.retorno_de_chamada(comparar, ["ponteiro", "ponteiro"], "i32")
qsort(area, 4, C.tamanho_de("i32"), comparador)

assert [q.deslocar(i).ler() cycle i in range(0, 4)] is [3, 7, 19, 42]
C.liberar(area)

// o tempo de vida e explicito: um callback coletado no meio de um qsort
// derruba o processo
action dobro(x):
    yield x * 2

cb := C.retorno_de_chamada(dobro, ["i32"], "i32")
assert cb.vivo()
assert cb.chamar(21) is 42
assert cb.endereco() bigger 0
cb.soltar()
assert not cb.vivo()

out "259 ok"`, lang: 'df', title: `exercicios/41-ffi-nativo/259_ffi_com_c.df` },
  {"p": "`adopt Python.numpy` resolve \"preciso de uma biblioteca que alguém já escreveu **em Python**\". Faltava o degrau de baixo: chamar uma função de uma biblioteca **C** — a `libm`, a `libz`, o `.so` que a empresa mantém há quinze anos — sem escrever módulo de extensão e sem trazer dependência. `Arcane.C` roda sobre o `ctypes`, que é da biblioteca padrão do Python: nada é instalado e nada é compilado."},
  {"h3": "A assinatura é declarada, e isso é o recurso"},
  { code: `libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
assert raiz(16.0) is 4.0`, lang: 'df' },
  {"p": "Adivinhar o tipo erra fora do caso comum, e erra **calado**: um `i32` onde o C espera `i64` passa em quase toda chamada e corrompe memória no resto — longe da linha que causou. Declarar é o que impede isso."},
  {"p": "A lista é fechada (`i8`…`i64`, `u8`…`u64`, `f32`, `f64`, `bool`, `char`, `texto`, `bytes`, `ponteiro`, `tamanho`, `void`), e um tipo inventado é recusado **com a lista**, em vez de virar um endereço qualquer."},
  {"h3": "Os dois erros que FFI sempre tem"},
  {"p": "Biblioteca que não abre e símbolo que não existe. Os dois chegam do sistema ilegíveis (`OSError: dlopen(…) no such file`), e aqui os dois dizem o nome, onde foi procurado e o caminho de saída — por sistema operacional. `lib.tem(nome)` deixa perguntar antes de tentar."},
  {"h3": "O layout é a parte que ninguém acerta de cabeça"},
  { code: `Mista := C.estrutura([["flag", "i8"], ["valor", "i32"]])
assert Mista.tamanho() is 8              // e nao 5
assert Mista.deslocamentos()["valor"] is 4`, lang: 'df' },
  {"p": "Tamanho, alinhamento e deslocamento vêm da ABI da plataforma. É o que quebra quando a struct do C muda de campo — e o que não dá para conferir lendo o cabeçalho de cabeça."},
  {"h3": "Ponteiro é um endereço COM TIPO"},
  {"p": "O tipo não é decoração: é ele que diz quanto `deslocar(1)` anda e como `ler()` interpreta os bytes. `deslocar_bytes(n)` existe para quando o passo não é o tipo, e `como(tipo)` é o cast."},
  {"p": "Só uma conferência é feita, e ela é a que vale o custo: **ponteiro nulo**. Ler um endereço nulo derruba o processo, e a pilha que sobra não fala do DataForge. O resto da segurança de memória, em FFI, é de quem chama — e o módulo não finge o contrário."},
  {"p": "Para não depender de disciplina, junte com `Arcane.Posse`:"},
  { code: `P.com(P.dono(C.alocar(32), lambda b => C.liberar(b)),
      lambda bloco => bloco.tamanho())`, lang: 'df' },
  {"p": "O bloco sai no fim do escopo, **inclusive quando o corpo falha**."},
  {"h3": "O C chamando uma ação sua"},
  {"p": "Metade das bibliotecas C úteis pede um ponteiro de função: `qsort` pede o comparador, a libcurl pede o recebedor, a libz pede o alocador."},
  { code: `comparador := C.retorno_de_chamada(comparar, ["ponteiro", "ponteiro"], "i32")
qsort(area, 4, C.tamanho_de("i32"), comparador)`, lang: 'df' },
  {"p": "O `qsort` do C chama uma ação escrita em DataForge e ordena memória crua com o resultado."},
  {"p": "O **tempo de vida** é explícito (`vivo()`, `soltar()`) por um motivo concreto: um callback coletado no meio de um `qsort` derruba o processo. Um objeto que se segura é o que impede isso, e `vivo()` é o que permite perguntar em vez de descobrir."},
  {"h3": "O que NÃO existe — e por quê"},
  {"list": ["**binding automático a partir de `.h`**: não há leitor de cabeçalho. A"]},
  {"p": "assinatura é escrita à mão, e essa é a conferência."},
  {"list": ["**C++ com nome decorado**: o *name mangling* não é estável entre"]},
  {"p": "compiladores. Só `extern \"C\"`."},
  {"list": ["**`stdcall` do Windows**: só a convenção padrão.", "**bloco `unsafe`**: não há bloco a marcar — o módulo inteiro é a"]},
  {"p": "fronteira insegura, e a documentação diz isso em vez de espalhar uma palavra pelo código."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/41-ffi-nativo/259_ffi_com_c.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '259-chamar-c-bibliotecas-ponteiros-e-callbacks', text: "259 · chamar C: bibliotecas, ponteiros e callbacks", level: 2 as const }, { id: 'a-assinatura-e-declarada-e-isso-e-o-recurso', text: "A assinatura é declarada, e isso é o recurso", level: 3 as const }, { id: 'os-dois-erros-que-ffi-sempre-tem', text: "Os dois erros que FFI sempre tem", level: 3 as const }, { id: 'o-layout-e-a-parte-que-ninguem-acerta-de-cabeca', text: "O layout é a parte que ninguém acerta de cabeça", level: 3 as const }, { id: 'ponteiro-e-um-endereco-com-tipo', text: "Ponteiro é um endereço COM TIPO", level: 3 as const }, { id: 'o-c-chamando-uma-acao-sua', text: "O C chamando uma ação sua", level: 3 as const }, { id: 'o-que-nao-existe-e-por-que', text: "O que NÃO existe — e por quê", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"41 · FFI e nativo"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/41-ffi-nativo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
