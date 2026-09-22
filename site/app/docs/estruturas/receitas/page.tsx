// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Receitas binárias",
  description: "Hexdump, cor RGBA num u32, deslocamento de bits sem molde, e um vetor de registros ordenado no lugar.",
};

const blocos: Bloco[] = [
  {"h2": "Olhar os bytes"},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

P := Est.definir("P", [["id", "u16"], ["nome", "char", 6]], "rede", yes)
out Bytes.despejo(P({"id": 258, "nome": "ana"}).bytes())
assert Bytes.hex(P({"id": 258, "nome": "ana"}).bytes()).starts_with("0102616e61")`, lang: 'df' },
  {"h2": "Uma cor RGBA num u32"},
  { code: `adopt Arcane.Estrutura as Est

Rgba := Est.campos_de_bits("Rgba", [["r", 8], ["g", 8], ["b", 8], ["a", 8]], 32)
laranja := Rgba.juntar({"r": 255, "g": 165, "b": 0, "a": 255})
assert laranja is 0xFFA500FF
assert Rgba.ler(laranja)["g"] is 165`, lang: 'df' },
  {"h2": "Ordenar registros no lugar"},
  { code: `adopt Arcane.Estrutura as Est

Nota := Est.definir("Nota", [["aluno", "u16"], ["nota", "u8"]], "rede", yes)
bloco := Est.bloco(Nota.tamanho * 3)
dados := [[1, 7], [2, 10], [3, 4]]
cycle i in range(3):
    Nota.escrever(bloco, {"aluno": dados[i][0], "nota": dados[i][1]}, i * Nota.tamanho)

// lê, ordena os VALORES, e regrava — o bloco continua o mesmo
lidos := [Nota.ler(bloco, i * Nota.tamanho) cycle i in range(3)]
ordenados := sorted(lidos, lambda n: -n["nota"])
cycle i in range(3):
    Nota.escrever(bloco, ordenados[i], i * Nota.tamanho)
assert [j["aluno"] cycle j in Est.janelas(bloco, Nota)] is [2, 1, 3]`, lang: 'df' },
];

const headings = [{ id: 'olhar-os-bytes', text: "Olhar os bytes", level: 2 as const }, { id: 'uma-cor-rgba-num-u32', text: "Uma cor RGBA num u32", level: 2 as const }, { id: 'ordenar-registros-no-lugar', text: "Ordenar registros no lugar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Receitas binárias"}
      description={"Hexdump, cor RGBA num u32, deslocamento de bits sem molde, e um vetor de registros ordenado no lugar."}
      href={"/docs/estruturas/receitas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
