// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Código de saída, erro e Ctrl-C",
  description: "O que o shell lê, o que vai para o stderr, e como terminar sem deixar sujeira.",
};

const blocos: Bloco[] = [
  {"p": "Um programa de terminal conversa com o shell por três canais, e dois deles são invisíveis para quem só olha a tela: o **código de saída**, o **stderr** e os **sinais**."},
  {"h2": "O código de saída é a resposta que o script lê"},
  {"table": {"head": ["Código", "Convenção"], "rows": [["`0`", "deu certo — e **só** isso"], ["`1`", "falhou por um motivo do programa"], ["`2`", "uso errado: argumento faltando, flag desconhecida"], ["`130`", "interrompido com `Ctrl-C` (128 + SIGINT)"]]}},
  { code: `adopt Arcane.OS as OS

action principal(args):
    given args["entrada"] is void:
        // Uso errado sai com 2, e a mensagem vai para o STDERR:
        // quem canaliza a saída quer o dado, não o erro.
        yield 2
    yield 0

assert principal({"entrada": void}) is 2
assert principal({"entrada": "a.csv"}) is 0`, lang: 'df' },
  {"p": "O erro vai para o `stderr` porque `prog > saida.txt` guarda só o resultado: misturar os dois faz a mensagem de erro entrar no arquivo de dados, e ninguém nota até o dia em que o arquivo é lido por outro programa."},
  { code: `adopt Arcane.OS as OS

// O dado vai para a saída normal…
out "linha de dado"

// …e a queixa, para o stderr. Aqui, à mão, para o bloco não encerrar:
// 'Cli.erro(texto)' faz as duas coisas — escreve no stderr E SAI com 1.
// É o 'die' de um script, e por isso não há linha depois dele.
assert OS.is_tty() is yes or OS.is_tty() is no`, lang: 'df' },
  { code: `adopt Arcane.Cli as Cli

// Última linha do programa, de propósito: ela encerra com código 1.
Cli.erro("não achei o arquivo 'vendas.csv'")`, lang: 'df', title: `encerra com 1` },
  {"h2": "Terminar sem deixar sujeira"},
  {"p": "`defer` roda na saída da ação **onde quer que esteja escrito** — inclusive no topo do programa, no fim dele. É o que garante que o arquivo temporário some, a conexão fecha e o relé desliga:"},
  { code: `adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-cli-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

IO.write($"{pasta}/trabalho.txt", "processando")
assert IO.exists($"{pasta}/trabalho.txt")
out "o defer apaga a pasta ao sair — inclusive se o programa falhar"`, lang: 'df' },
  {"h2": "O `Ctrl-C`"},
  { code: `adopt Arcane.Inicio as Inicio

// 'ao_encerrar' roda no caminho normal E no Ctrl-C: é onde mora
// "salve o que deu tempo" e "solte o que estiver segurando".
salvos := []
Inicio.ao_encerrar(lambda => salvos.append("estado gravado"))
out "encerramento registrado"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um laço sem saída controlando um recurso", "texto": "`persist yes:` sem condição de parada, com um arquivo aberto ou um relé ligado, é o pior desenho desta área: o `Ctrl-C` interrompe no meio, e o recurso fica como estava. A saída é um `defer` (que roda) ou uma condição lida de fora."}},
  {"h2": "Erro que a pessoa consegue resolver"},
  { code: `adopt Arcane.IO as IO

action abrir(caminho):
    given not IO.exists(caminho):
        // O que, onde, e o que fazer. As três partes.
        trigger $"não achei '{caminho}'. Confira o caminho, ou passe '-' para ler da entrada padrão."
    yield IO.read(caminho)

monitor:
    abrir("nao-existe.csv")
handle Error as e:
    out e.message`, lang: 'df' },
];

const headings = [{ id: 'o-codigo-de-saida-e-a-resposta-que-o-script-le', text: "O código de saída é a resposta que o script lê", level: 2 as const }, { id: 'terminar-sem-deixar-sujeira', text: "Terminar sem deixar sujeira", level: 2 as const }, { id: 'o-ctrl-c', text: "O `Ctrl-C`", level: 2 as const }, { id: 'erro-que-a-pessoa-consegue-resolver', text: "Erro que a pessoa consegue resolver", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Código de saída, erro e Ctrl-C"}
      description={"O que o shell lê, o que vai para o stderr, e como terminar sem deixar sujeira."}
      href={"/docs/receitas/cli/saida-e-sinais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
