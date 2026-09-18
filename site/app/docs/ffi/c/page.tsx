// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_c.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Chamar C",
  description: "Arcane.C: abrir uma biblioteca nativa, declarar a assinatura, ler o layout de uma struct e chamar função — sobre ctypes, sem dependência.",
};

const blocos: Bloco[] = [
  {"p": "A [ponte para o Python](/docs/tecnicas/ponte) resolve \"preciso de uma biblioteca que alguém já escreveu **em Python**\". Faltava o degrau de baixo: chamar uma função de uma biblioteca **C** — a `libm`, a `libz`, o `.so` que a empresa mantém há quinze anos — sem escrever módulo de extensão."},
  { code: `adopt Arcane.C as C

libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
potencia := libm.funcao("pow", ["f64", "f64"], "f64")

assert raiz(16.0) is 4.0
assert potencia(2.0, 10.0) is 1024.0`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Zero dependência continua valendo", "texto": "Isto roda sobre o `ctypes`, que é da biblioteca padrão do Python. Nada é instalado, nada é compilado, e o módulo funciona no mesmo lugar em que o DataForge já funciona."}},
  {"h2": "A assinatura é declarada"},
  {"p": "`funcao(nome, [argumentos], retorno)` obriga a dizer os tipos. Adivinhar erra fora do caso comum: um `i32` onde o C espera `i64` passa em quase toda chamada e corrompe memória no resto — em silêncio, e longe da linha que causou."},
  {"table": {"head": ["Tipo", "No C"], "rows": [["`i8` `i16` `i32` `i64`", "`int8_t` … `int64_t`"], ["`u8` `u16` `u32` `u64`", "`uint8_t` … `uint64_t`"], ["`f32` `f64`", "`float`, `double`"], ["`bool` `char`", "`bool`, `char`"], ["`texto`", "`const char*` (vai e volta como texto UTF-8)"], ["`bytes`", "`const char*` cru, sem conversão"], ["`ponteiro`", "`void*` — qualquer endereço"], ["`tamanho`", "`size_t`"], ["`void`", "só como retorno"]]}},
  { code: `adopt Arcane.C as C

libc := C.padrao()
tamanho := libc.funcao("strlen", ["texto"], "tamanho")
absoluto := libc.funcao("abs", ["i32"], "i32")

assert tamanho("dataforge") is 9
assert absoluto(-42) is 42

assert libc.tem("strlen")
assert not libc.tem("nao_existe_mesmo")`, lang: 'df' },
  {"h2": "Quando não dá, a mensagem diz o que fazer"},
  {"p": "Biblioteca que não abre e símbolo que não existe são os dois erros mais comuns de FFI — e os dois chegam do sistema ilegíveis. Aqui eles dizem o nome, onde foi procurado e o caminho de saída, por sistema operacional."},
  { code: `adopt Arcane.C as C

monitor:
    C.carregar("libnaoexisteaqui")
    assert no
handle RuntimeError as e:
    assert "libnaoexisteaqui" in e.message`, lang: 'df' },
  {"h2": "Struct: o layout de verdade"},
  {"p": "Tamanho, alinhamento e deslocamento vêm da ABI da plataforma — é a parte que ninguém acerta de cabeça, e a que quebra quando a struct do C muda."},
  { code: `adopt Arcane.C as C

Ponto := C.estrutura([["x", "f64"], ["y", "f64"]])
assert Ponto.tamanho() is 16
assert Ponto.deslocamentos() is {"x": 0, "y": 8}

// o padding aparece: um i8 antes de um i32 não ocupa 5 bytes
Mista := C.estrutura([["flag", "i8"], ["valor", "i32"]])
assert Mista.tamanho() is 8
assert Mista.deslocamentos()["valor"] is 4
assert Mista.alinhamento() is 4`, lang: 'df' },
  { code: `adopt Arcane.C as C

Ponto := C.estrutura([["x", "i32"], ["y", "i32"]])
p := Ponto.criar({"x": 3, "y": 4})

assert p.ler("x") is 3
p.escrever("x", 30)
assert p.tudo() is {"x": 30, "y": 4}

// a união ocupa o maior campo
U := C.uniao([["i", "i32"], ["f", "f64"]])
assert U.tamanho() is C.tamanho_de("f64")`, lang: 'df' },
  {"p": "Um `enum` do C é inteiro com nome, e aqui ele é um vault — `C.enumeracao({\"VERMELHO\": 0, \"VERDE\": 1})`. Não há tipo novo a criar: o que atravessa a fronteira é o número, e um embrulho só esconderia isso."},
  {"h2": "O que o sistema responde"},
  { code: `adopt Arcane.C as C

assert C.tamanho_de("i8") is 1
assert C.tamanho_de("i32") is 4
assert C.tamanho_de("f64") is 8
assert C.tamanho_de("ponteiro") in [4, 8]
assert C.endianness() in ["little", "big"]
assert "i32" in C.tipos()`, lang: 'df' },
];

const headings = [{ id: 'a-assinatura-e-declarada', text: "A assinatura é declarada", level: 2 as const }, { id: 'quando-nao-da-a-mensagem-diz-o-que-fazer', text: "Quando não dá, a mensagem diz o que fazer", level: 2 as const }, { id: 'struct-o-layout-de-verdade', text: "Struct: o layout de verdade", level: 2 as const }, { id: 'o-que-o-sistema-responde', text: "O que o sistema responde", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Chamar C"}
      description={"Arcane.C: abrir uma biblioteca nativa, declarar a assinatura, ler o layout de uma struct e chamar função — sobre ctypes, sem dependência."}
      href={"/docs/ffi/c"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
