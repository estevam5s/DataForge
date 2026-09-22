// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A ordem dos bytes",
  description: "Big-endian, little-endian, a ordem da rede, e o bswap — com o mesmo número lido dos dois jeitos.",
};

const blocos: Bloco[] = [
  {"p": "O número `0x12345678` ocupa quatro bytes, e há duas ordens para escrevê-los: o byte mais significativo primeiro (**big-endian**, `12 34 56 78`) ou o menos significativo primeiro (**little-endian**, `78 56 34 12`). Os processadores x86 e ARM usam little; os protocolos de rede e a maioria dos formatos de arquivo, big — por isso \"rede\" é o padrão aqui."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

N := Est.definir("N", [["v", "u32"]])                 // "rede" = big-endian
I := Est.definir("I", [["v", "u32"]], "intel")        // little-endian

assert Bytes.hex(N({"v": 0x12345678}).bytes()) is "12345678"
assert Bytes.hex(I({"v": 0x12345678}).bytes()) is "78563412"

// os MESMOS bytes, lidos na ordem errada, são outro número — sem erro nenhum
crus := N({"v": 1}).bytes()
assert I.ler(crus)["v"] is 16777216
assert Est.trocar_ordem(16777216, "u32") is 1`, lang: 'df' },
  {"table": {"head": ["Formato", "Ordem"], "rows": [["TCP/IP, DNS, PNG, JPEG, Java class", "big-endian (rede)"], ["WAV, BMP, ZIP, executável do Windows", "little-endian"], ["TIFF", "está no próprio arquivo (`II` ou `MM`)"], ["Protocol Buffers", "varint — não tem ordem de palavra: ver [Varint](/docs/estruturas/varint)"]]}},
  {"callout": {"tipo": "dica", "titulo": "Qual é a desta máquina?", "texto": "`C.endianness()` responde — e a resposta quase nunca importa: o molde declara a ordem do **formato**, e ela vale em qualquer máquina. É exatamente por isso que a ordem é obrigatória."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"A ordem dos bytes"}
      description={"Big-endian, little-endian, a ordem da rede, e o bswap — com o mesmo número lido dos dois jeitos."}
      href={"/docs/estruturas/ordem-dos-bytes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
