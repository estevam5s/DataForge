// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Hardware",
  description: "SIMD, cache, bare-metal e assembly — e por que, numa linguagem interpretada, a resposta honesta é quase sempre 'não se aplica'.",
};

const blocos: Bloco[] = [
  {"p": "Otimização de hardware — vetorização, localidade de cache, instruções específicas — acontece **abaixo** do interpretador. Numa linguagem interpretada sobre o CPython, o custo de despachar cada nó da árvore domina qualquer efeito de cache em três ordens de grandeza. Fingir o contrário seria documentar o que não acontece."},
  {"table": {"head": ["Quer", "Aqui", "Página"], "rows": [["SIMD, conta vetorizada", "a ponte para o `numpy`, que **é** vetorizado", "[A ponte](/docs/tecnicas/ponte)"], ["chamar código nativo", "`Arcane.C`", "[FFI](/docs/ffi)"], ["layout de memória exato", "`Arcane.Estrutura`", "[Estruturas](/docs/estruturas)"], ["vários núcleos", "`P.map_processos`", "[Concorrência](/docs/concorrencia)"], ["bare-metal, kernel, assembly", "não se aplica", "[O mapa](/docs/hardware/mapa)"]]}},
  { code: `adopt Arcane.C as C

assert C.endianness() in ["little", "big"]
assert C.tamanho_de("ponteiro") in [4, 8]      // 32 ou 64 bits`, lang: 'df' },
  {"cards": [{"href": "/docs/hardware/mapa", "title": "Hardware: o mapa", "desc": "cada item da referência, com a resposta e o que existe no lugar"}, {"href": "/docs/alvos/portabilidade", "title": "Onde este programa roda", "desc": "os alvos, lidos dos adopt"}]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Hardware"}
      description={"SIMD, cache, bare-metal e assembly — e por que, numa linguagem interpretada, a resposta honesta é quase sempre 'não se aplica'."}
      href={"/docs/hardware"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
