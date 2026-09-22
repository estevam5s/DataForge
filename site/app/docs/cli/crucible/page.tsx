// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge crucible",
  description: "Filtro, tags, ordem aleatória, repetição, prazo e relatórios para o CI.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge test` descobre e roda os testes do projeto, com cobertura. `dataforge crucible` é o corredor do framework com **todas** as alavancas: escolher o que roda, mudar a ordem, repetir, e o formato do relatório."},
  { code: `dataforge crucible                             # tudo, em tests/, testes/ e *_crucible.df
dataforge crucible --filtro=desconto           # so os trials com 'desconto' no nome
dataforge crucible --tag=rapido                # so os marcados
dataforge crucible --sem-tag=lento             # pula os marcados
dataforge crucible --aleatorio                 # embaralha: a dependencia de ordem aparece
dataforge crucible --aleatorio --semente=4217  # repete aquele embaralhamento
dataforge crucible --repetir=50                # o teste instavel se denuncia
dataforge crucible --prazo=200                 # falha o que passar de 200 ms
dataforge crucible --formato=junit --out=r.xml # para o CI
dataforge crucible --matchers                  # tudo o que se pode cobrar`, lang: 'bash' },
  {"table": {"head": ["Alavanca", "O defeito que ela expõe"], "rows": [["`--aleatorio`", "o teste que só passa depois de outro — estado compartilhado"], ["`--semente`", "reproduzir a ordem que falhou, em vez de torcer para ela voltar"], ["`--repetir`", "o teste instável, que passa uma vez em vinte"], ["`--prazo`", "o teste que ficou lento sem ninguém notar"], ["`--formato=junit`", "o CI lista o teste que falhou, em vez de só *“job vermelho”*"]]}},
  {"p": "Continue em [Testes instáveis](/docs/testes/instaveis) e [Relatórios e CI](/docs/crucible/relatorios)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge crucible"}
      description={"Filtro, tags, ordem aleatória, repetição, prazo e relatórios para o CI."}
      href={"/docs/cli/crucible"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
