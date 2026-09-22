// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escrever um WAV",
  description: "O cabeçalho RIFF de 44 bytes, em little-endian, e um segundo de onda senoidal escrito amostra por amostra.",
};

const blocos: Bloco[] = [
  {"p": "O WAV é o formato de áudio mais simples que existe: 44 bytes de cabeçalho **little-endian** e depois as amostras. É um bom exercício justamente por ser little-endian — ler com o molde padrão (big-endian) dá números absurdos e nenhum erro."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes
adopt Arcane.Math as M

Wav := Est.definir("Wav", [
    ["riff", "char", 4], ["tamanho", "u32"], ["wave", "char", 4],
    ["fmt", "char", 4], ["fmt_tamanho", "u32"], ["formato", "u16"], ["canais", "u16"],
    ["taxa", "u32"], ["bytes_por_segundo", "u32"], ["alinhamento", "u16"], ["bits", "u16"],
    ["data", "char", 4], ["data_tamanho", "u32"]], "intel", yes)
assert Wav.tamanho is 44

taxa := 8000
amostras := [int(M.sin(2 * M.PI * 440 * i / taxa) * 8000) cycle i in range(taxa)]
corpo := Bytes.escrever("<")
cycle a in amostras:
    corpo.escrever("i16", a)
audio := corpo.finalizar()

cab := Wav({"riff": "RIFF", "tamanho": 36 + len(audio), "wave": "WAVE", "fmt": "fmt ",
    "fmt_tamanho": 16, "formato": 1, "canais": 1, "taxa": taxa,
    "bytes_por_segundo": taxa * 2, "alinhamento": 2, "bits": 16,
    "data": "data", "data_tamanho": len(audio)})
arquivo := Bytes.concatenar(cab.bytes(), audio)

lido := Wav.ler(arquivo)
assert lido["riff"] is "RIFF" and lido["taxa"] is 8000
assert lido["data_tamanho"] is 16000                  // um segundo de 16 bits mono
assert len(arquivo) is 16044`, lang: 'df' },
  {"p": "Grave com `IO.write_bytes(\"la.wav\", arquivo)` e qualquer tocador reproduz um lá de 440 Hz. `IO.write` não serve: ele abre em modo texto, e bytes de áudio não são texto."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Escrever um WAV"}
      description={"O cabeçalho RIFF de 44 bytes, em little-endian, e um segundo de onda senoidal escrito amostra por amostra."}
      href={"/docs/estruturas/wav"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
