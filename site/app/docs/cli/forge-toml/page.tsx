import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "forge.toml",
  description: "O manifesto do projeto: metadados, scripts e configuração.",
};

const blocos: Bloco[] = [
  {"h2": "O arquivo"},
  { code: `[project]
name = "meu-app"
version = "0.1.0"
description = "Um exemplo"
authors = ["voce"]
license = "MIT"
entry = "src/main.df"
dataforge = ">=4.0"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"
check = "check ."
fmt = "fmt ."

[build]
out = "dist"
include = ["src"]

[lint]
strict = false
ignore = ["magic-number"]`, lang: 'toml', title: `forge.toml` },
  {"h2": "O que ele habilita"},
  {"h3": "Entrada padrão"},
  { code: `dataforge run        # sem argumento: usa project.entry`, lang: 'bash' },
  {"h3": "Scripts nomeados"},
  {"p": "Qualquer chave em `[scripts]` vira um comando:"},
  { code: `dataforge start      # roda "run src/main.df"
dataforge test       # roda "test tests/"`, lang: 'bash' },
  {"p": "Isso guarda o comando certo no repositório, em vez de num README que ninguém lê."},
  {"h3": "Raiz do projeto"},
  {"p": "Comandos rodam a partir da pasta do `forge.toml`, não de onde você está. Rodar `dataforge test` de dentro de `src/` funciona igual."},
  {"h3": "Versão mínima"},
  { code: `dataforge info`, lang: 'bash' },
  {"p": "Avisa se o `dataforge = \">=4.0\"` não bate com a versão instalada — antes de você descobrir isso por um erro de sintaxe estranho."},
  {"h2": "A seção [dependencies]"},
  {"callout": {"tipo": "atencao", "texto": "A seção existe e é lida, mas **nada a resolve ainda**. O gerenciador de pacotes está no [roadmap](/docs/roadmap)."}},
  {"h2": "Criar"},
  { code: `dataforge init`, lang: 'bash' },
];

const headings = [{ id: 'o-arquivo', text: "O arquivo", level: 2 as const }, { id: 'o-que-ele-habilita', text: "O que ele habilita", level: 2 as const }, { id: 'entrada-padrao', text: "Entrada padrão", level: 3 as const }, { id: 'scripts-nomeados', text: "Scripts nomeados", level: 3 as const }, { id: 'raiz-do-projeto', text: "Raiz do projeto", level: 3 as const }, { id: 'versao-minima', text: "Versão mínima", level: 3 as const }, { id: 'a-secao-dependencies', text: "A seção [dependencies]", level: 2 as const }, { id: 'criar', text: "Criar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"forge.toml"}
      description={"O manifesto do projeto: metadados, scripts e configuração."}
      href={"/docs/cli/forge-toml"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
