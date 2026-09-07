import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge init",
  description: "Criar um projeto novo",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge init            # na pasta atual
dataforge init meu-app`, lang: 'bash' },
  {"h2": "O que gera"},
  { code: `meu-app/
  forge.toml                 manifesto
  src/main.df                o programa
  tests/principal_test.df    os testes`, lang: 'text' },
  {"p": "O comando pergunta nome, descrição e autor. Depois:"},
  { code: `cd meu-app
dataforge run      # usa a entrada do manifesto
dataforge test`, lang: 'bash' },
  {"h2": "init ou new?"},
  {"p": "`init` cria o esqueleto mínimo. `dataforge new` oferece templates completos — CLI, análise de dados, orientado a objetos, suíte de testes, API REST e web app."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'o-que-gera', text: "O que gera", level: 2 as const }, { id: 'init-ou-new', text: "init ou new?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge init"}
      description={"Criar um projeto novo"}
      href={"/docs/cli/init"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
