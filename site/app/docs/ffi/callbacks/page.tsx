// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_c.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Callbacks: o C chamando você",
  description: "Uma ação DataForge vista pelo C como ponteiro de função — com tempo de vida explícito, porque um callback coletado derruba o processo.",
};

const blocos: Bloco[] = [
  {"p": "Metade das bibliotecas C úteis pede um **ponteiro de função**: `qsort` pede o comparador, a libcurl pede o recebedor, a libz pede o alocador. `C.retorno_de_chamada` transforma uma ação da linguagem nisso."},
  { code: `adopt Arcane.C as C

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
C.liberar(bloco)`, lang: 'df' },
  {"p": "O `qsort` do C chamou uma ação escrita em DataForge, quatro a seis vezes, e ordenou memória crua com o resultado."},
  {"h2": "Tempo de vida: o detalhe que derruba processo"},
  {"p": "O callback precisa continuar vivo enquanto o C puder chamá-lo. Um callback coletado no meio de um `qsort` derruba o processo — e a pilha não fala do DataForge. Por isso ele é um **objeto que se segura**, e que responde se ainda vale."},
  { code: `adopt Arcane.C as C

action dobro(x):
    yield x * 2

cb := C.retorno_de_chamada(dobro, ["i32"], "i32")

assert cb.vivo()
assert cb.chamar(21) is 42           // chama pela ponte do C
assert cb.endereco() bigger 0        // é um ponteiro de função de verdade

cb.soltar()
assert not cb.vivo()`, lang: 'df' },
  {"table": {"head": ["Item da literatura", "Aqui"], "rows": [["function pointer", "`cb.endereco()` — e o próprio `cb` passa como `ponteiro`"], ["closure como callback", "a ação leva o fechamento dela; o C não sabe disso, e não precisa"], ["context pointer (`void* user_data`)", "declare um `ponteiro` a mais na assinatura e leia-o dentro da ação"], ["static trampoline", "é o que o `ctypes` monta por baixo — não há o que escrever"], ["callback lifecycle", "explícito: `vivo()` e `soltar()`"], ["ABI-safe", "a assinatura é declarada; errar o tipo aqui é o mesmo desastre de errar no C"]]}},
];

const headings = [{ id: 'tempo-de-vida-o-detalhe-que-derruba-processo', text: "Tempo de vida: o detalhe que derruba processo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Callbacks: o C chamando você"}
      description={"Uma ação DataForge vista pelo C como ponteiro de função — com tempo de vida explícito, porque um callback coletado derruba o processo."}
      href={"/docs/ffi/callbacks"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
