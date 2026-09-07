import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge bench",
  description: "Mede o tempo de execução, repetindo.",
};

const blocos: Bloco[] = [
  { code: `dataforge bench algoritmo.df
dataforge bench algoritmo.df --runs=50`, lang: 'bash' },
  { code: `medindo bench.df — 6 repeticoes

  mediana   23.36 ms
  minimo    22.57 ms
  maximo    23.43 ms
  desvio    0.34 ms  (1.5%)

  1 execucao(oes) de aquecimento descartada(s)`, lang: 'bash' },
  {"h2": "Por que mediana, não média"},
  {"p": "Uma execução lenta por causa do sistema operacional puxa a média e não diz nada sobre o código. A mediana ignora o extremo."},
  {"h2": "Aquecimento"},
  {"p": "As primeiras execuções aquecem cache e alocador. Medi-las distorce o resultado para cima, então são descartadas — um quinto das repetições, no mínimo uma."},
  {"h2": "O desvio importa"},
  {"p": "Um desvio de 1,5% diz que a medida é confiável. Um de 40% diz que algo mais está acontecendo — outro processo, coleta de lixo, I/O — e o número não descreve o código."},
];

const headings = [{ id: 'por-que-mediana-nao-media', text: "Por que mediana, não média", level: 2 as const }, { id: 'aquecimento', text: "Aquecimento", level: 2 as const }, { id: 'o-desvio-importa', text: "O desvio importa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge bench"}
      description={"Mede o tempo de execução, repetindo."}
      href={"/docs/cli/bench"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
