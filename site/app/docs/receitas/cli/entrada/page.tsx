// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Entrada: teclado, cano e arquivo",
  description: "Perguntar quando há alguém do outro lado — e ler do `stdin` quando não há.",
};

const blocos: Bloco[] = [
  {"p": "Uma ferramenta de terminal recebe dado de três lugares, e confundi-los é o que faz um programa travar dentro de um script: **o teclado**, **o cano** (`cat x | prog`) e **o arquivo** passado como argumento."},
  { code: `adopt Arcane.OS as OS
adopt Arcane.Cli as Cli

// A pergunta só faz sentido com alguém do outro lado.
given Cli.tem_terminal():
    out "aqui eu poderia perguntar"
otherwise:
    out "sem terminal: leio do cano, e não pergunto"`, lang: 'df' },
  {"h2": "Ler o que vier pelo cano"},
  {"p": "`input()` devolve `void` no fim da entrada, e **não levanta**: um programa canalizado termina a entrada, e isso não é erro. É o que torna o laço abaixo o idioma da linguagem:"},
  { code: `linhas := []
persist yes:
    linha := input()
    given linha is void:
        halt
    linhas.append(linha)

out $"{len(linhas)} linha(s) pelo cano"`, lang: 'df' },
  {"h2": "O padrão que cobre os três casos"},
  { code: `adopt Arcane.IO as IO
adopt Arcane.Cli as Cli

action ler_tudo(caminho):
    // Um '-' como caminho quer dizer "a entrada padrão", e é
    // convenção de quase toda ferramenta Unix.
    given caminho is void or caminho is "-":
        pedacos := []
        persist yes:
            linha := input()
            given linha is void:
                halt
            pedacos.append(linha)
        yield join("\\n", pedacos)
    yield IO.read(caminho)

// com o arquivo:
adopt Arcane.OS as OS
pasta := $"{OS.temp_dir()}/df-cli-{randint(100000, 999999)}"
IO.mkdir(pasta)
IO.write($"{pasta}/a.txt", "uma linha")
assert ler_tudo($"{pasta}/a.txt") is "uma linha"
IO.remove_tree(pasta)`, lang: 'df' },
  {"h2": "Perguntar, escolher, confirmar"},
  { code: `adopt Arcane.Cli as Cli

// Num terminal, estes três param e esperam. Num script, eles
// precisam de um padrão — senão a automação trava sem dizer por quê.
action nome_do_projeto(args):
    given args["nome"] is not void:
        yield args["nome"]
    given not Cli.tem_terminal():
        trigger "sem terminal: passe --nome"
    yield Cli.perguntar("nome do projeto", "meu-app")

assert nome_do_projeto({"nome": "loja"}) is "loja"

monitor:
    nome_do_projeto({"nome": void})
handle Error as e:
    out e.message`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Nunca peça segredo quando não há terminal", "texto": "`Cli.segredo(\"senha\")` esconde o que se digita. Sem terminal, ele não tem como esconder — e uma senha lida de um cano acaba no log de quem chamou. Prefira uma variável de ambiente, e diga isso na mensagem."}},
  {"h2": "Validar na entrada"},
  { code: `adopt Arcane.Cli as Cli

// 'valida' é uma ação que devolve yes/no; a pergunta se repete.
action e_email(texto):
    yield "@" in texto and "." in texto

assert e_email("a@b.co") is yes
assert e_email("nada") is no`, lang: 'df' },
];

const headings = [{ id: 'ler-o-que-vier-pelo-cano', text: "Ler o que vier pelo cano", level: 2 as const }, { id: 'o-padrao-que-cobre-os-tres-casos', text: "O padrão que cobre os três casos", level: 2 as const }, { id: 'perguntar-escolher-confirmar', text: "Perguntar, escolher, confirmar", level: 2 as const }, { id: 'validar-na-entrada', text: "Validar na entrada", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Entrada: teclado, cano e arquivo"}
      description={"Perguntar quando há alguém do outro lado — e ler do `stdin` quando não há."}
      href={"/docs/receitas/cli/entrada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
