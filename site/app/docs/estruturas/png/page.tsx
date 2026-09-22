// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ler um PNG de verdade",
  description: "Assinatura, chunks, tamanho em big-endian e o CRC de cada um — o formato inteiro, sem biblioteca de imagem.",
};

const blocos: Bloco[] = [
  {"p": "Um PNG é uma assinatura de 8 bytes seguida de **chunks**: tamanho (`u32`, big-endian), tipo (4 letras), dados, e um CRC-32 do tipo mais os dados. O primeiro chunk é sempre `IHDR`, com largura, altura e profundidade de cor. Montamos um cabeçalho de verdade e o lemos de volta, conferindo o CRC:"},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

steady ASSINATURA := Bytes.de_hex("89504e470d0a1a0a")
Ihdr := Est.definir("Ihdr", [["largura", "u32"], ["altura", "u32"], ["profundidade", "u8"],
    ["cor", "u8"], ["compressao", "u8"], ["filtro", "u8"], ["entrelace", "u8"]], "rede", yes)

action chunk(tipo, dados):
    corpo := Bytes.concatenar(Bytes.de_texto(tipo), dados)
    yield Bytes.escrever(">").escrever("u32", len(dados)).escrever_bytes(corpo).escrever("u32", Est.crc32(corpo)).finalizar()

dados := Ihdr({"largura": 640, "altura": 480, "profundidade": 8, "cor": 6}).bytes()
png := Bytes.concatenar(ASSINATURA, chunk("IHDR", dados))

// ── ler ──
assert Bytes.fatiar(png, 0, 8) is ASSINATURA
l := Bytes.ler(Bytes.fatiar(png, 8), ">")
tamanho := l.ler("u32")
tipo := l.ler_texto(4)
corpo := l.ler_bytes(tamanho)
crc := l.ler("u32")
assert tipo is "IHDR" and tamanho is 13
assert crc is Est.crc32(corpo, Est.crc32(Bytes.de_texto(tipo)))   // CRC em duas partes
assert Ihdr.ler(corpo)["largura"] is 640`, lang: 'df' },
  {"list": ["**A assinatura primeiro.** Ela tem um `\\r\\n` e um `\\n` de propósito: um arquivo que passou por conversão de fim de linha tem a assinatura estragada, e o erro aparece aqui — e não como uma imagem corrompida.", "**O CRC antes de confiar.** Um chunk com CRC errado é recusado antes de os dados serem interpretados.", "**`crc32(dados, inicial)` continua uma conta.** O CRC do PNG é do tipo **mais** os dados; calcular em duas partes evita concatenar os dois só para conferir."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Ler um PNG de verdade"}
      description={"Assinatura, chunks, tamanho em big-endian e o CRC de cada um — o formato inteiro, sem biblioteca de imagem."}
      href={"/docs/estruturas/png"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
