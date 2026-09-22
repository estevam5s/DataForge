// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os tipos do C",
  description: "Qual tipo declarar para cada tipo do C — e os três que mudam de tamanho conforme a plataforma.",
};

const blocos: Bloco[] = [
  {"p": "A assinatura declarada é a única coisa que o `ctypes` sabe sobre a função. Um `i32` onde o C espera `i64` passa em quase toda chamada — e corrompe o resto da pilha na que não passa. O tipo precisa ser o **do C**, e não o do valor que você tem."},
  {"table": {"head": ["No C", "Declare", "Cuidado"], "rows": [["`int`, `int32_t`", "`i32`", "—"], ["`unsigned int`, `uint32_t`", "`u32`", "—"], ["`long`", "`i64` no Linux/macOS 64 bits, `i32` no Windows", "o motivo de existir `int64_t`"], ["`long long`, `int64_t`", "`i64`", "—"], ["`size_t`", "`tamanho`", "4 ou 8 bytes conforme a plataforma"], ["`double` / `float`", "`f64` / `f32`", "passar `f32` onde o C quer `double` dá lixo"], ["`char*` (texto)", "`texto`", "ver [Textos](/docs/ffi/textos)"], ["`void*`, qualquer ponteiro", "`ponteiro`", "o tipo do alvo você carrega à parte"], ["`char` (um caractere)", "`char`", "—"], ["nada (`void`)", "`void`", "só como retorno"]]}},
  { code: `adopt Arcane.C as C

assert C.tamanho_de("i32") is 4
assert C.tamanho_de("f64") is 8
assert C.tamanho_de("tamanho") in [4, 8]          // size_t acompanha a plataforma
assert C.tamanho_de("ponteiro") is C.tamanho_de("tamanho")
out C.tipos()`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Olhe o cabeçalho, não a documentação", "texto": "A assinatura certa está no `.h` da biblioteca. `man 3 strlen` diz `size_t strlen(const char *s)` — então `[\"texto\"]` e retorno `\"tamanho\"`, e não `i32`, mesmo que o número caiba."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Os tipos do C"}
      description={"Qual tipo declarar para cada tipo do C — e os três que mudam de tamanho conforme a plataforma."}
      href={"/docs/ffi/tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
