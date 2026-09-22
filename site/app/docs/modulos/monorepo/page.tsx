// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Workspace e monorepo",
  description: "Vários pacotes numa árvore só — e a checagem de faixas que acusa antes de instalar.",
};

const blocos: Bloco[] = [
  {"p": "Um projeto com uma aplicação e quatro bibliotecas internas não deveria publicar as quatro para poder usá-las. O workspace é a árvore inteira vista de uma vez."},
  { code: `minha-empresa/
  forge.toml            [workspace] members = ["apps/*", "libs/*"]
  apps/
    loja/forge.toml
    admin/forge.toml
  libs/
    validacao/forge.toml
    relatorios/forge.toml`, lang: 'text' },
  { code: `dataforge workspace          # o grafo, e os conflitos de faixa
dataforge workspace --json   # para o CI ler`, lang: 'bash' },
  {"h2": "O que ele acusa, e o que ele cala"},
  {"p": "A interseção de faixas sai da **mesma classe `Requisito`** que o `resolver` usa. Uma segunda noção de *“estas faixas se cruzam?”* divergiria da instalação — e o relatório aprovaria o que o `add` recusa."},
  {"table": {"head": ["Acusa", "Cala"], "rows": [["um pino exato recusado pelo outro lado", "faixas que se cruzam, mesmo sem serem iguais"], ["duas faixas sem interseção", "o que ele não consegue provar"], ["ciclo entre membros", "—"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Ele lê, e NÃO instala", "texto": "`workspace` é um relatório. Ele não mexe em `forge_modules/`, não reescreve o lock e não baixa nada — o que o torna seguro de rodar no CI de todo *pull request*. E ele só acusa o que **prova**: um falso conflito faria o comando ser ignorado, e aí o conflito de verdade passa junto."}},
  {"h2": "O pino por projeto"},
  {"p": "`project.dataforge` no `forge.toml` diz de que versão da linguagem aquele projeto precisa — e ele é **cobrado**, não apenas mostrado."},
  { code: `[project]
nome = "loja"
dataforge = ">=1.1"

# 'dataforge run' troca para a versao pinada quando ela esta
# instalada, e RECUSA quando nao esta. Um pino que nao e cobrado e
# um comentario com sintaxe — e era exatamente o que ele era: o
# unico lugar que o lia era o 'dataforge info', para mostrar na
# tela.`, lang: 'toml' },
  {"p": "Continue em [Versões lado a lado](/docs/cli/versoes) e [Workspace](/docs/cli/workspace)."},
];

const headings = [{ id: 'o-que-ele-acusa-e-o-que-ele-cala', text: "O que ele acusa, e o que ele cala", level: 2 as const }, { id: 'o-pino-por-projeto', text: "O pino por projeto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Workspace e monorepo"}
      description={"Vários pacotes numa árvore só — e a checagem de faixas que acusa antes de instalar."}
      href={"/docs/modulos/monorepo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
