// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Varint e zigzag",
  description: "O inteiro de tamanho variável do Protocol Buffers e do WebAssembly: 7 bits por byte, e o truque para os negativos.",
};

const blocos: Bloco[] = [
  {"p": "A maioria dos números de uma mensagem é pequena — ids, contagens, tamanhos. Gastar 8 bytes num `u64` para guardar um 3 é desperdício, e o **varint** (LEB128) resolve: 7 bits de dado por byte, e o bit alto diz \"ainda tem mais\". Um número menor que 128 ocupa **um** byte."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

assert Bytes.hex(Est.varint(1)) is "01"
assert Bytes.hex(Est.varint(150)) is "9601"         // o exemplo da doc do protobuf
assert Bytes.hex(Est.varint(300)) is "ac02"

lido := Est.ler_varint(Bytes.de_hex("ff9601ff"), 1)  // começando no byte 1
assert lido is {"valor": 150, "tamanho": 2}`, lang: 'df' },
  {"h2": "Negativos: zigzag"},
  {"p": "Em varint sem sinal, −1 é o maior número de 64 bits: **dez** bytes. O zigzag intercala os sinais — 0, −1, 1, −2, 2 viram 0, 1, 2, 3, 4 — e um −1 volta a caber em um byte. É o que o protobuf faz com `sint64`."},
  { code: `adopt Arcane.Estrutura as Est

assert [Est.zigzag(n) cycle n in [0, -1, 1, -2, 2]] is [0, 1, 2, 3, 4]
assert len(Est.varint(Est.zigzag(-1))) is 1
cycle n in [-1000, -1, 0, 7, 123456]:
    assert Est.desfazer_zigzag(Est.zigzag(n)) is n

recusou := no
monitor:
    Est.varint(-1)                    // sem zigzag, recusado — com a dica
handle LayoutError:
    recusou := yes
assert recusou`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O varint que não termina", "texto": "Dados cortados no meio de um varint têm o bit alto ligado no último byte. `ler_varint` levanta dizendo em que byte o número começou e quantos leu — em vez de ler o que vem depois como parte do número."}},
];

const headings = [{ id: 'negativos-zigzag', text: "Negativos: zigzag", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Varint e zigzag"}
      description={"O inteiro de tamanho variável do Protocol Buffers e do WebAssembly: 7 bits por byte, e o truque para os negativos."}
      href={"/docs/estruturas/varint"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
