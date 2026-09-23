// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar uma ferramenta de terminal",
  description: "Sem subprocesso onde não precisa, e com subprocesso onde só ele prova.",
};

const blocos: Bloco[] = [
  {"p": "Uma CLI tem duas metades, e elas se testam de formas diferentes: a **leitura dos argumentos** é função pura, e a **execução** é um processo com código de saída, `stdout` e `stderr`."},
  {"h2": "A metade pura: `ler`, nunca `rodar`"},
  { code: `adopt Arcane.Cli as Cli
adopt Arcane.Crucible as Crucible

action montar():
    cmd := Cli.comando("relatorio", "")
    cmd.posicional("entrada", "")
    cmd.opcao("limite", "inteiro", "n", 10, "")
    yield cmd

crucible "os argumentos":

    trial "o padrao vale quando a flag nao vem":
        args := montar().ler(["a.csv"])
        expect args["limite"] is 10

    trial "a forma curta e a longa sao a mesma coisa":
        expect montar().ler(["a.csv", "-n", "5"])["limite"] is 5
        expect montar().ler(["a.csv", "--limite=5"])["limite"] is 5

    trial "o inteiro chega como INTEIRO":
        expect montar().ler(["a.csv", "-n", "7"])["limite"] is 7

Crucible.run()`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`rodar` mata o corredor de testes", "texto": "Ele imprime e chama `OS.exit`. Um teste que o chama derruba o próprio processo do teste — e o relatório some junto. `ler` levanta, que é o que um teste quer."}},
  {"h2": "A metade impura: o processo de verdade"},
  {"p": "O que só o subprocesso prova é o que acontece **na fronteira**: o código de saída, o que foi para cada canal, e o que o shell vê."},
  { code: `adopt Arcane.Process as P

// O próprio interpretador serve de cobaia: ele é uma CLI.
r := P.run(["python3", "-m", "dataforge", "--versao"])
assert r["exit_code"] is 0 and r["ok"] is yes
assert len(r["stdout"]) > 0
out r["stdout"]

// 'capture' e o atalho para quando so o stdout importa
assert len(P.capture(["python3", "-m", "dataforge", "--versao"])) > 0`, lang: 'df' },
  { code: `adopt Arcane.Process as P

// Um comando que não existe: o código de saída é o que prova.
r := P.run(["python3", "-m", "dataforge", "nao-existe-esse-comando"])
assert r["failed"] is yes
out $"saiu com {r['exit_code']}"`, lang: 'df' },
  {"h2": "A entrada canalizada"},
  { code: `adopt Arcane.Process as P
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-cli-t-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

IO.write($"{pasta}/soma.df", """persist yes:
    linha := input()
    given linha is void:
        halt
    out int(linha) * 2
""")

r := P.run(["python3", "-m", "dataforge", "run", $"{pasta}/soma.df"],
           no, void, void, void, "5\\n7\\n")
assert r["exit_code"] is 0
assert "10" in r["stdout"] and "14" in r["stdout"]
out r["stdout"]`, lang: 'df' },
  {"h2": "O que testar, em ordem de retorno"},
  {"list": ["**O código de saída** em cada caminho — é o que um `&&` no shell lê, e o que um CI usa para reprovar.", "**A ajuda cita cada opção** — um teste de três linhas que impede a ajuda de envelhecer.", "**A mensagem de erro de uso** — ela é lida por quem está travado, e é a única documentação que essa pessoa vai ler.", "**A saída canalizada não tem cor** — o `| grep` de alguém depende disso.", "**O temporário some** — rode duas vezes e confira que nada ficou para trás."]},
];

const headings = [{ id: 'a-metade-pura-ler-nunca-rodar', text: "A metade pura: `ler`, nunca `rodar`", level: 2 as const }, { id: 'a-metade-impura-o-processo-de-verdade', text: "A metade impura: o processo de verdade", level: 2 as const }, { id: 'a-entrada-canalizada', text: "A entrada canalizada", level: 2 as const }, { id: 'o-que-testar-em-ordem-de-retorno', text: "O que testar, em ordem de retorno", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar uma ferramenta de terminal"}
      description={"Sem subprocesso onde não precisa, e com subprocesso onde só ele prova."}
      href={"/docs/receitas/cli/testar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
