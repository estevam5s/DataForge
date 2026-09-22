// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge profile e fix",
  description: "Onde o tempo foi gasto, ação por ação — e o que se conserta sozinho.",
};

const blocos: Bloco[] = [
  {"p": "Um `bench` diz **que** está lento; um `profile` diz **onde**. Ele mede cada ação — chamadas, tempo **próprio** e por chamada — e ordena pelo que mais custa."},
  { code: `dataforge profile src/main.df
dataforge bench src/main.df          # o tempo total, repetindo`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Tempo próprio, e não acumulado", "texto": "O acumulado de `main` inclui tudo o que ela chama, e a soma de todos passaria de 100%. O tempo **próprio** é o que a ação gasta nela mesma — é o número que aponta o gargalo. A ação que você acha que é o gargalo quase nunca é."}},
  {"h2": "fix"},
  {"p": "`dataforge fix` roda o formatador e, em seguida, o linter: arruma o que dá para arrumar sozinho e **lista** o resto. O que exige julgamento não é consertado — uma ferramenta que muda código precisa ser previsível."},
  { code: `dataforge fix              # formata e lista
dataforge fix --dry-run    # so o relatorio, sem escrever`, lang: 'bash' },
  {"p": "Continue em [Medir](/docs/cli/bench) e [Prometer desempenho](/docs/bibliotecas/desempenho)."},
];

const headings = [{ id: 'fix', text: "fix", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge profile e fix"}
      description={"Onde o tempo foi gasto, ação por ação — e o que se conserta sozinho."}
      href={"/docs/cli/profile"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
