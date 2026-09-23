// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Subcomandos",
  description: "git-style: um programa, vários verbos — e a ajuda de cada um.",
};

const blocos: Bloco[] = [
  {"p": "`git commit`, `docker run`, `dataforge check`. Quando a ferramenta cresce, o verbo vira o primeiro argumento, e cada verbo tem as suas opções."},
  { code: `adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "Gerenciador de tarefas", "2.0.0")

criar := app.subcomando("criar", "cria uma tarefa")
criar.posicional("titulo", "o título")
criar.opcao("prazo", "texto", "p", "", "quando vence")

listar := app.subcomando("listar", "lista as tarefas")
listar.opcao("todas", "sim_nao", "a", no, "inclusive as concluídas")

args := app.ler(["criar", "comprar café", "--prazo=amanhã"])
assert args["__comando__"] is "criar"
assert args["titulo"] is "comprar café"
assert args["prazo"] is "amanhã"

args := app.ler(["listar", "-a"])
assert args["__comando__"] is "listar"
assert args["todas"] is yes`, lang: 'df' },
  {"h2": "Despachar"},
  {"p": "Um vault de ações é melhor que uma escada de `given`: acrescentar um verbo passa a ser acrescentar uma entrada, e a lista de verbos vira dado — dá para listá-la, testá-la e conferi-la."},
  { code: `adopt Arcane.Cli as Cli

action criar(args):
    yield $"criada: {args['titulo']}"

action listar(args):
    yield "3 tarefas"

VERBOS := {"criar": criar, "listar": listar}

app := Cli.comando("tarefa", "")
c := app.subcomando("criar", "")
c.posicional("titulo", "")
app.subcomando("listar", "")

args := app.ler(["criar", "café"])
acao := VERBOS[args["__comando__"]]
assert acao(args) is "criada: café"

// e a lista de verbos é DADO: dá para conferir que nenhum ficou sem ação
assert sorted(keys(VERBOS)) is ["criar", "listar"]`, lang: 'df' },
  {"h2": "A ajuda do programa lista os verbos"},
  { code: `adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "Gerenciador de tarefas")
app.subcomando("criar", "cria uma tarefa")
app.subcomando("listar", "lista as tarefas")

texto := app.ajuda()
assert "criar" in texto and "cria uma tarefa" in texto
out texto`, lang: 'df' },
  {"h2": "Um verbo que não existe"},
  { code: `adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "")
app.subcomando("criar", "")
app.subcomando("listar", "")

monitor:
    app.ler(["crear", "x"])       // erro de digitação
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"p": "Uma sugestão (\"você quis dizer `criar`?\") é o que transforma um erro de digitação em um segundo de perda, em vez de uma ida à documentação."},
];

const headings = [{ id: 'despachar', text: "Despachar", level: 2 as const }, { id: 'a-ajuda-do-programa-lista-os-verbos', text: "A ajuda do programa lista os verbos", level: 2 as const }, { id: 'um-verbo-que-nao-existe', text: "Um verbo que não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Subcomandos"}
      description={"git-style: um programa, vários verbos — e a ajuda de cada um."}
      href={"/docs/receitas/cli/subcomandos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
