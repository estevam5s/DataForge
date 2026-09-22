// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge completar",
  description: "O Tab do terminal em bash, zsh e fish — gerado do mesmo catálogo do help.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge completar <shell>` imprime o script de autocompletar. Ele sai do **catálogo de comandos**: um comando novo aparece no Tab no dia em que entra na linguagem, e uma opção removida some."},
  { code: `# bash
dataforge completar bash > ~/.local/share/bash-completion/completions/dataforge

# zsh
dataforge completar zsh > "\${fpath[1]}/_dataforge"

# fish
dataforge completar fish > ~/.config/fish/completions/dataforge.fish`, lang: 'bash' },
  { code: `$ dataforge ch<Tab>
check
$ dataforge check --<Tab>
--formato  --strict  --syntax-only  --help
$ dataforge run sr<Tab>
src/`, lang: 'text' },
  {"h2": "Três decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["as opções são **por comando**", "`check --<Tab>` ofereceria as sessenta opções de todos os comandos"], ["depois de `run`, `check`, `fmt`… completa **arquivo**", "o Tab oferece subcomando onde se digita `src/main.df`"], ["o script é texto puro, sem chamar o `dataforge`", "cada Tab custaria ~100 ms de interpretador — o bastante para desligar"]]}},
  {"callout": {"tipo": "dica", "titulo": "E o `df`", "texto": "O script registra o completar para `dataforge` **e** para `df` — os dois são o mesmo programa."}},
];

const headings = [{ id: 'tres-decisoes', text: "Três decisões", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge completar"}
      description={"O Tab do terminal em bash, zsh e fish — gerado do mesmo catálogo do help."}
      href={"/docs/cli/completar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
