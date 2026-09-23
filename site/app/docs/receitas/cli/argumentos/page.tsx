// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Argumentos, opções e a ajuda",
  description: "Declarar o que o comando aceita — e ganhar a ajuda, a validação e o erro de graça.",
};

const blocos: Bloco[] = [
  {"p": "Ler `OS.argv()` à mão funciona para um script de dez linhas e apodrece no primeiro dia em que alguém escreve `--formato json` em vez de `--formato=json`. `Arcane.Cli` inverte isso: você **declara** o que o comando aceita, e a ajuda, a validação e a mensagem de erro saem da declaração."},
  { code: `adopt Arcane.Cli as Cli

cmd := Cli.comando("relatorio", "Gera um relatório de vendas", "1.0.0")
cmd.posicional("entrada", "o CSV de vendas")
cmd.opcao("formato", "texto", "f", "tabela", "tabela, json ou csv", no,
          ["tabela", "json", "csv"])
cmd.opcao("limite", "inteiro", "n", 10, "quantas linhas")
cmd.opcao("cores", "sim_nao", "", no, "colorir a saída")

args := cmd.ler(["vendas.csv", "--formato=json", "-n", "5", "--cores"])
assert args["entrada"] is "vendas.csv"
assert args["formato"] is "json"
assert args["limite"] is 5          // já vem Integer, não texto
assert args["cores"] is yes`, lang: 'df' },
  {"h2": "A ajuda é gerada, e por isso não mente"},
  {"p": "Uma ajuda escrita à mão envelhece na primeira opção nova — e ninguém relê a ajuda do próprio programa. Aqui ela sai da mesma declaração que faz a leitura:"},
  { code: `adopt Arcane.Cli as Cli

cmd := Cli.comando("relatorio", "Gera um relatório de vendas", "1.0.0")
cmd.posicional("entrada", "o CSV de vendas")
cmd.opcao("formato", "texto", "f", "tabela", "tabela, json ou csv", no,
          ["tabela", "json", "csv"])
cmd.exemplo("relatorio vendas.csv --formato=json", "em JSON")

texto := cmd.ajuda()
assert "uso: relatorio" in texto
assert "--formato" in texto
assert "tabela|json|csv" in texto       // as escolhas aparecem
assert "exemplos:" in texto
out texto`, lang: 'df' },
  {"h2": "O que a declaração compra"},
  {"table": {"head": ["Você declara", "Ganha"], "rows": [["`tipo := \"inteiro\"`", "conversão, e erro claro em `--limite=abc`"], ["`escolhas := [...]`", "recusa o que não está na lista, e mostra a lista"], ["`exigida := yes`", "recusa a falta, dizendo qual falta"], ["`curta := \"n\"`", "`-n 5`, `-n=5` e `--limite 5` passam a ser a mesma coisa"], ["`tipo := \"sim_nao\"`", "`--cores` sem valor vira `yes`"], ["`cmd.exemplo(…)`", "a seção de exemplos da ajuda"]]}},
  {"h2": "O erro sai antes do trabalho"},
  { code: `adopt Arcane.Cli as Cli

cmd := Cli.comando("relatorio", "")
cmd.opcao("formato", "texto", "f", "tabela", "", no, ["tabela", "json"])

monitor:
    cmd.ler(["--formato=xml"])
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"p": "Validar **antes** de abrir o arquivo é o que separa um erro de uma linha de um traceback no meio do processamento — e o que permite ao programa falhar sem ter escrito nada."},
  {"h2": "Vários valores para o mesmo posicional"},
  { code: `adopt Arcane.Cli as Cli

cmd := Cli.comando("somar", "soma números")
cmd.posicional("numeros", "os números", yes)      // varios := yes

args := cmd.ler(["1", "2", "3"])
assert len(args["numeros"]) is 3
assert [int(n) cycle n in args["numeros"]] >> distill a, v: a + v 0 is 6`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "`rodar` sai; `ler` levanta", "texto": "`cmd.rodar()` imprime a ajuda ou o erro e **encerra o processo** — é o que se quer no `main`. `cmd.ler(…)` levanta, e é o que se quer num teste: um teste que chama `rodar` mata o próprio corredor."}},
];

const headings = [{ id: 'a-ajuda-e-gerada-e-por-isso-nao-mente', text: "A ajuda é gerada, e por isso não mente", level: 2 as const }, { id: 'o-que-a-declaracao-compra', text: "O que a declaração compra", level: 2 as const }, { id: 'o-erro-sai-antes-do-trabalho', text: "O erro sai antes do trabalho", level: 2 as const }, { id: 'varios-valores-para-o-mesmo-posicional', text: "Vários valores para o mesmo posicional", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Argumentos, opções e a ajuda"}
      description={"Declarar o que o comando aceita — e ganhar a ajuda, a validação e o erro de graça."}
      href={"/docs/receitas/cli/argumentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
