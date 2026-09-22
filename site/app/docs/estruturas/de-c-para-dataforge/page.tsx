// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "De uma struct do C para um molde",
  description: "Traduzir uma struct, conferir o layout contra o próprio C, e o #pragma pack.",
};

const blocos: Bloco[] = [
  {"p": "Quando o formato vem descrito como uma `struct` do C — num cabeçalho `.h`, numa especificação antiga —, a tradução é campo a campo. O que muda de uma plataforma para outra é o **tamanho** de alguns tipos do C, e o alinhamento. A tabela resolve o primeiro; o `Arcane.C` confere o segundo contra o compilador de verdade."},
  {"table": {"head": ["No C", "No molde", "Cuidado"], "rows": [["`uint8_t`, `unsigned char`", "`u8`", "—"], ["`int16_t`, `short`", "`i16`", "`short` é 16 bits em toda plataforma comum"], ["`int32_t`, `int`", "`i32`", "`int` é 32 bits em toda plataforma comum"], ["`long`", "`i64` no Linux/macOS, `i32` no Windows", "o motivo de usar `int32_t` no C"], ["`float` / `double`", "`f32` / `f64`", "—"], ["`char nome[16]`", "`[\"nome\", \"char\", 16]`", "lido até o primeiro zero"], ["`uint8_t hash[32]`", "`[\"hash\", \"bytes\", 32]`", "nunca cortado"], ["`__attribute__((packed))`, `#pragma pack(1)`", "`Est.definir(…, ordem, yes)`", "—"]]}},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.C as C

// struct Ponto3D { uint8_t marca; float x, y, z; uint16_t cor; };
campos := [["marca", "u8"], ["x", "f32"], ["y", "f32"], ["z", "f32"], ["cor", "u16"]]

molde := Est.definir("Ponto3D", campos, "intel")
assert molde.tamanho is C.estrutura(campos).tamanho()     // vinte, como o compilador
assert molde.deslocamento("x") is 4                       // três bytes de enchimento
assert Est.alinhamento_de(molde) is 4`, lang: 'df' },
  {"p": "Se o dado vai **para** uma função C, o caminho é o [`Arcane.C`](/docs/ffi/ponteiros), que monta a struct na memória que o C lê. `Arcane.Estrutura` é para quando o dado é um arquivo ou um pacote de rede — e não precisa de biblioteca nativa nenhuma."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"De uma struct do C para um molde"}
      description={"Traduzir uma struct, conferir o layout contra o próprio C, e o #pragma pack."}
      href={"/docs/estruturas/de-c-para-dataforge"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
