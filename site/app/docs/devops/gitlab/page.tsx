// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "GitLab CI",
  description: "O mesmo pipeline no GitLab, com o relatório JUnit na página do merge request.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge devops ci gitlab` escreve `.gitlab-ci.yml`. Os comandos são os mesmos do GitHub — a ordem do custo não muda de plataforma —, e o relatório JUnit do Crucible vai em `artifacts.reports.junit`, que é o que faz o GitLab listar os testes que falharam **na página do merge request**."},
  { code: `dataforge devops ci gitlab
git add .gitlab-ci.yml && git commit -m "CI no GitLab"`, lang: 'bash' },
  { code: `verificar:
  stage: verificar
  script:
    - pip install dataforge-lang
    - dataforge fmt . --check
    - dataforge check . --strict
    - dataforge lint .
    - dataforge test --minimo=70
    - dataforge crucible --formato=junit --saida=relatorio.xml || true
  artifacts:
    when: always
    reports:
      junit: relatorio.xml`, lang: 'yaml' },
  {"table": {"head": ["No arquivo", "Sem ele"], "rows": [["`when: always` nos artefatos", "o relatório só é guardado quando tudo passa — e é quando falha que ele importa"], ["cache de `pip` e `forge_modules`", "cada job baixa tudo de novo"], ["`|| true` no JUnit", "o `crucible` reprovado impediria o relatório de ser publicado; quem reprova é o `test` acima"]]}},
  {"callout": {"tipo": "nota", "titulo": "E os outros CIs", "texto": "Jenkins, CircleCI, Azure Pipelines e Bitbucket rodam os mesmos cinco comandos. `dataforge devops ci <outro>` imprime a lista, em vez de gerar um arquivo que ninguém aqui conferiu — um artefato não testado para uma plataforma é pior que nenhum."}},
  {"p": "Continue em [Ambiente de desenvolvimento](/docs/devops/ambiente-de-dev)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"GitLab CI"}
      description={"O mesmo pipeline no GitLab, com o relatório JUnit na página do merge request."}
      href={"/docs/devops/gitlab"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
