// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Completar com Tab",
  description: "bash, zsh e fish — gerados do catálogo, e não escritos à mão.",
};

const blocos: Bloco[] = [
  {"p": "Completar com Tab é a diferença entre uma ferramenta que se usa de cabeça e uma que exige `--ajuda` a cada vez. O script de completação é gerado **do catálogo de comandos** — escrito à mão, ele envelheceria na primeira flag nova."},
  { code: `$ dataforge completar bash > ~/.dataforge-completar.bash
$ echo 'source ~/.dataforge-completar.bash' >> ~/.bashrc

$ dataforge completar zsh  > ~/.zsh/completions/_dataforge
$ dataforge completar fish > ~/.config/fish/completions/dataforge.fish`, lang: 'bash' },
  {"h2": "Para a sua ferramenta"},
  {"p": "O mesmo princípio: a declaração do comando já sabe quais são as opções e os subcomandos, então o script sai dela."},
  { code: `adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "")
app.subcomando("criar", "cria")
app.subcomando("listar", "lista")

action script_bash(nome, verbos):
    palavras := join(" ", verbos)
    corpo := $"  COMPREPLY=($(compgen -W \\"{palavras}\\" -- \\"$" + "{COMP_WORDS[1]}\\"))"
    linhas := [$"_{nome}() {{", corpo, "}", $"complete -F _{nome} {nome}"]
    yield join("\\n", linhas)

texto := script_bash("tarefa", ["criar", "listar"])
assert "complete -F _tarefa tarefa" in texto
out texto`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Testado com Tab de verdade", "texto": "O completar do `dataforge` é conferido com um Tab **simulado no bash**, e não lendo o script: um script de completação com erro de sintaxe é aceito pelo shell em silêncio, e o Tab simplesmente não faz nada — que é indistinguível de não ter instalado."}},
  {"h2": "O que completar, em ordem de utilidade"},
  {"list": ["**Os subcomandos** — é o primeiro Tab de toda sessão.", "**As flags do subcomando atual**, e não as do programa inteiro.", "**As escolhas de uma opção** (`--formato=` → `tabela json csv`).", "**Caminhos**, quando o posicional é um arquivo — o shell já faz isso, desde que o script não o atrapalhe."]},
];

const headings = [{ id: 'para-a-sua-ferramenta', text: "Para a sua ferramenta", level: 2 as const }, { id: 'o-que-completar-em-ordem-de-utilidade', text: "O que completar, em ordem de utilidade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Completar com Tab"}
      description={"bash, zsh e fish — gerados do catálogo, e não escritos à mão."}
      href={"/docs/receitas/cli/completar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
