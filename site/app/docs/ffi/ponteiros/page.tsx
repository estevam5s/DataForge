// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_c.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ponteiros e memória crua",
  description: "Endereço com tipo, aritmética de ponteiro, memória alocada à mão e o nulo que se reconhece antes de derrubar o processo.",
};

const blocos: Bloco[] = [
  {"p": "Um ponteiro aqui é um **endereço com tipo**. O tipo não é decoração: é ele que diz quanto `deslocar(1)` anda e como `ler()` interpreta os bytes."},
  { code: `adopt Arcane.C as C

bloco := C.alocar(4 * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")

cycle i from 0 to 3:
    p.deslocar(i).escrever(i * 10)

assert p.ler() is 0
assert p.deslocar(2).ler() is 20
assert [p.deslocar(i).ler() cycle i in range(0, 4)] is [0, 10, 20, 30]

C.liberar(bloco)`, lang: 'df' },
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`C.ponteiro(alvo, tipo)`", "ponteiro a partir de endereço, bloco ou struct"], ["`p.ler()` · `p.escrever(v)`", "lê e escreve **no tipo declarado**"], ["`p.deslocar(n)`", "anda `n` **itens** — a aritmética de ponteiro"], ["`p.deslocar_bytes(n)`", "anda `n` bytes, quando o passo não é o tipo"], ["`p.como(tipo)`", "o mesmo endereço lido como outro tipo — o cast"], ["`p.bytes(n)` · `p.texto()`", "lê memória crua, ou uma string terminada em zero"], ["`p.endereco()` · `p.e_nulo()`", "o número, e a pergunta que evita o desastre"]]}},
  {"h2": "O nulo é conferido"},
  {"p": "Ler um endereço nulo derruba o processo, e a pilha não fala do DataForge. Essa é a única conferência que **vale** o custo — o resto da segurança de memória, em FFI, é de quem chama."},
  { code: `adopt Arcane.C as C

nulo := C.nulo()
assert nulo.e_nulo() and nulo.endereco() is 0

monitor:
    nulo.ler()
    assert no
handle RuntimeError as e:
    assert "nulo" in e.message`, lang: 'df' },
  {"h2": "Memória alocada à mão"},
  { code: `adopt Arcane.C as C
adopt Arcane.Bytes as B

dados := C.de_bytes("dataforge")
assert B.para_texto(C.para_bytes(dados, 9)) is "dataforge"
assert dados.tamanho() is 10          // o zero do fim conta

outro := C.alocar(16)
C.copiar(outro, dados, 9)
assert B.para_texto(C.para_bytes(outro, 9)) is "dataforge"

C.liberar(dados)
C.liberar(outro)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Usar memória liberada é o defeito que mais derruba processo em C", "texto": "`liberar` é idempotente, e um bloco já liberado recusa com o motivo em vez de entregar lixo. Para não depender de disciplina, guarde o bloco num [`P.dono`](/docs/memoria/posse) e deixe `P.com(…)` liberar — inclusive no caminho de erro."}},
  { code: `adopt Arcane.C as C
adopt Arcane.Posse as P

// o bloco sai junto com o escopo, mesmo se o corpo falhar
valor := P.com(P.dono(C.alocar(32), lambda b => C.liberar(b)),
               lambda bloco => bloco.tamanho())

assert valor is 32`, lang: 'df' },
];

const headings = [{ id: 'o-nulo-e-conferido', text: "O nulo é conferido", level: 2 as const }, { id: 'memoria-alocada-a-mao', text: "Memória alocada à mão", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ponteiros e memória crua"}
      description={"Endereço com tipo, aritmética de ponteiro, memória alocada à mão e o nulo que se reconhece antes de derrubar o processo."}
      href={"/docs/ffi/ponteiros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
