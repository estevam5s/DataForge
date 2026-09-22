// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Alinhamento e enchimento",
  description: "Por que u8 + u32 + u16 ocupa 12 bytes e não 7, como reduzir, e quando empacotar.",
};

const blocos: Bloco[] = [
  {"p": "O processador lê um `u32` mais depressa — e em algumas arquiteturas, **só** consegue lê-lo — quando ele começa num endereço múltiplo de 4. O compilador de C insere bytes vazios entre os campos para garantir isso, e também no fim do registro, para um vetor deles continuar alinhado. Esses bytes são o **enchimento**."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.C as C

campos := [["a", "u8"], ["b", "u32"], ["c", "u16"]]
alinhado := Est.definir("S", campos, "intel")
out alinhado.mapa()

assert alinhado.tamanho is 12                  // u8, três vazios, u32, u16, dois vazios
assert alinhado.enchimento() is 5
assert alinhado.tamanho is C.estrutura(campos).tamanho()   // o mesmo que o C faria

empacotado := Est.definir("S", campos, "intel", yes)
assert empacotado.tamanho is 7                 // o '#pragma pack(1)' do C`, lang: 'df' },
  {"h2": "Reordenar custa zero e economiza"},
  {"p": "Os mesmos campos, do maior para o menor, deixam de precisar de enchimento no meio. Num vetor de um milhão de registros, isso é um terço da memória:"},
  { code: `adopt Arcane.Estrutura as Est

bagunçado := Est.definir("A", [["a", "u8"], ["b", "u32"], ["c", "u16"]], "intel")
ordenado := Est.definir("B", [["b", "u32"], ["c", "u16"], ["a", "u8"]], "intel")
assert bagunçado.tamanho is 12 and ordenado.tamanho is 8`, lang: 'df' },
  {"table": {"head": ["Modo", "Use quando"], "rows": [["alinhado (padrão)", "o registro vai para uma `struct` do C, ou vive na memória em vetor"], ["empacotado (`yes`)", "o formato de arquivo ou protocolo foi definido **sem** enchimento — quase todos"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Formato de arquivo quase nunca é alinhado", "texto": "PNG, WAV, ZIP e o cabeçalho IP foram desenhados byte a byte. Ler um deles com o molde alinhado desloca todo campo depois do primeiro enchimento — e os números lidos são plausíveis, que é o pior jeito de estar errado."}},
];

const headings = [{ id: 'reordenar-custa-zero-e-economiza', text: "Reordenar custa zero e economiza", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Alinhamento e enchimento"}
      description={"Por que u8 + u32 + u16 ocupa 12 bytes e não 7, como reduzir, e quando empacotar."}
      href={"/docs/estruturas/alinhamento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
