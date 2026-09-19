// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Percentis, e a cauda",
  description: "A média esconde o que o usuário sente. P50, P95 e P99 com aquecimento separado — e por que o percentil sai da amostra, sem interpolar.",
};

const blocos: Bloco[] = [
  {"p": "[`Arcane.Bench`](/docs/tecnicas/bench) responde \"quanto tempo leva\" com uma **média**. É o que quase toda ferramenta de benchmark faz, e é onde quase toda decisão de performance erra."},
  {"p": "Cem requisições de 10 ms e uma de 1000 ms dão média **20 ms**. A pessoa que pegou a última esperou **um segundo** — e nenhum relatório baseado em média vai contar isso."},
  { code: `adopt Arcane.Perfil as P

action consulta():
    yield sum(range(400))

m := P.medir(consulta, {"amostras": 50, "aquecimento": 5})

assert m["amostras"] is 50
assert m["aquecimento"] is 5
assert m["p50"] smaller_eq m["p95"] and m["p95"] smaller_eq m["p99"]`, lang: 'df' },
  { code: `adopt Arcane.Perfil as P

// quatro medidas normais e um pico: a media mal se move, o p99 salta
resumo := P.resumir([10.0, 10.0, 10.0, 10.0, 1000.0])

assert resumo["media"] smaller resumo["p99"]
assert resumo["max"] is 1000.0`, lang: 'df' },
  {"h2": "Duas decisões que mudam o número"},
  {"table": {"head": ["Decisão", "Por quê"], "rows": [["o **aquecimento** é separado e declarado", "as primeiras execuções medem cache frio, import preguiçoso e alocação inicial. Misturá-las com o resto não é medir o programa: é medir a **partida**"], ["o percentil sai da amostra **por posto**, sem interpolar", "interpolar inventa um valor que não aconteceu. Num P99 de latência o que se quer é uma medida que **existiu**"]]}},
  {"table": {"head": ["Número", "Responde"], "rows": [["`p50`", "o caso comum"], ["`p95`, `p99`, `p999`", "o que o usuário reclama"], ["`media` e `desvio`", "a forma da distribuição — e o aviso quando a média está bem acima da mediana"], ["`vazao`", "operações por segundo, a partir da mediana"], ["`min`, `max`", "o piso e o pior caso visto"]]}},
  {"callout": {"tipo": "nota", "titulo": "O relatório avisa quando há cauda", "texto": "`P.relatorio(medida)` escreve a distribuição e, se a média estiver mais de 30% acima da mediana, acrescenta uma linha dizendo que há cauda e que é ela que o usuário sente. Um relatório que só imprime números deixa a leitura para quem já sabia o que procurar."}},
];

const headings = [{ id: 'duas-decisoes-que-mudam-o-numero', text: "Duas decisões que mudam o número", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Percentis, e a cauda"}
      description={"A média esconde o que o usuário sente. P50, P95 e P99 com aquecimento separado — e por que o percentil sai da amostra, sem interpolar."}
      href={"/docs/observabilidade/perfil"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
