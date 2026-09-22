// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ambiente de desenvolvimento",
  description: "Devcontainer para Codespaces e VS Code, e os ganchos do pre-commit que rodam o CI antes do commit.",
};

const blocos: Bloco[] = [
  {"p": "O defeito mais caro de um projeto novo é o *“na minha máquina funciona”*. Duas peças o reduzem: um contêiner de desenvolvimento, igual para todos, e ganchos que rodam o que o CI roda **antes** do commit — onde consertar custa segundos, e não um ciclo inteiro de revisão."},
  {"h2": "Devcontainer"},
  { code: `dataforge devops devcontainer
# .devcontainer/devcontainer.json — abra no VS Code ("Reopen in Container")
# ou num Codespace, e a linguagem, a extensao e as dependencias ja estao la`, lang: 'bash' },
  { code: `{
  "name": "loja",
  "image": "mcr.microsoft.com/devcontainers/python:3.13",
  "postCreateCommand": "pip install dataforge-lang && dataforge editor && dataforge install",
  "forwardPorts": [8080]
}`, lang: 'json' },
  {"p": "A extensão é instalada por `dataforge editor`, e não por id do marketplace: ela vem **no pacote**, na mesma versão da linguagem. Um id do marketplace instalaria a última, que pode não concordar com a linguagem instalada."},
  {"h2": "pre-commit"},
  { code: `dataforge devops pre-commit
pip install pre-commit
pre-commit install          # a partir daqui, todo commit roda os ganchos`, lang: 'bash' },
  {"table": {"head": ["Gancho", "O que para"], "rows": [["`dataforge fmt`", "o diff de formatação no meio do diff de lógica"], ["`dataforge check --strict`", "o nome errado que só apareceria no CI, dez minutos depois"], ["`dataforge seguranca`", "o token colado no código — o único erro que não se desfaz com outro commit"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Um segredo commitado é um segredo vazado", "texto": "Apagar o arquivo no commit seguinte não o tira do histórico, e um repositório público é espelhado em minutos. O gancho de segurança é o único que roda **antes** — depois, a única resposta é rotacionar a credencial."}},
  {"p": "Continue em [Numa VM](/docs/devops/vm)."},
];

const headings = [{ id: 'devcontainer', text: "Devcontainer", level: 2 as const }, { id: 'pre-commit', text: "pre-commit", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ambiente de desenvolvimento"}
      description={"Devcontainer para Codespaces e VS Code, e os ganchos do pre-commit que rodam o CI antes do commit."}
      href={"/docs/devops/ambiente-de-dev"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
