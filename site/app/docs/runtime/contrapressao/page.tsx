// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Contrapressão",
  description: "Uma fonte mais rápida que o consumo: sem teto, a memória cresce até o processo morrer. Com teto, a falha é visível.",
};

const blocos: Bloco[] = [
  {"p": "Quando pedidos chegam mais depressa do que o laço atende, eles se acumulam na fila de prontas. Sem limite, a fila cresce até o processo ser morto por falta de memória — horas depois, e sem mensagem que aponte a causa. O **teto** troca essa morte lenta por uma recusa imediata."},
  { code: `adopt Arcane.Laco as L

laco := L.novo(2)                              // no máximo 2 esperando
aceitos := [L.agendar(laco, lambda => void) cycle i in range(5)]
assert aceitos is [yes, yes, no, no, no]
assert L.estatisticas(laco)["recusadas"] is 3`, lang: 'df' },
  {"table": {"head": ["Quem recebe o `no`", "Faz"], "rows": [["um servidor", "responde 503 com `Retry-After` — o cliente tenta depois"], ["um leitor de fila", "para de ler da fonte até a fila baixar"], ["um produtor de fibras", "usa um [canal](/docs/runtime/canais), que espera em vez de recusar"]]}},
  {"callout": {"tipo": "dica", "titulo": "Recusar é melhor que atrasar", "texto": "Um servidor que aceita tudo e responde em 30 s está mais quebrado que um que recusa metade e responde o resto em 50 ms: o cliente do primeiro já desistiu, e o trabalho foi feito para ninguém."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Contrapressão"}
      description={"Uma fonte mais rápida que o consumo: sem teto, a memória cresce até o processo morrer. Com teto, a falha é visível."}
      href={"/docs/runtime/contrapressao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
