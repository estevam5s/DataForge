// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Argumentos da linha de comando",
  description: "OS.argv para o simples, Cli.comando para o que tem opção, tipo e ajuda — gerada da declaração.",
};

const blocos: Bloco[] = [
  {"p": "Os argumentos chegam depois de `--`: `dataforge run relatorio.df -- --mes 9 saida.csv`. `OS.argv()` os entrega crus; `Cli.comando` os **declara** — nome, tipo, padrão, se é exigido — e confere, converte e gera a ajuda a partir disso."},
  { code: `adopt Arcane.Cli as Cli

programa := Cli.comando("relatorio", sobre := "Gera o relatório do mês.", versao := "1.0.0")
_ := programa.opcao("mes", "inteiro", curta := "m", exigida := yes, sobre := "de 1 a 12")
_ := programa.opcao("formato", escolhas := ["csv", "json"], padrao := "csv")
_ := programa.posicional("saida", exigido := no)

lido := programa.ler(["-m", "9", "--formato", "json", "saida.json"])
assert lido["mes"] is 9                     // já convertido para inteiro
assert lido["formato"] is "json"
assert lido["saida"] is "saida.json"

out programa.ajuda()`, lang: 'df' },
  {"h2": "O erro sugere o que existe"},
  { code: `adopt Arcane.Cli as Cli

programa := Cli.comando("relatorio")
_ := programa.opcao("mes", "inteiro")

sugeriu := no
monitor:
    programa.ler(["--mess", "9"])
handle Error as e:
    sugeriu := e.message.contains("--mes")
assert sugeriu`, lang: 'df' },
  {"list": ["**A ajuda é gerada.** Escrita à mão, ela envelhece na primeira opção nova — e ajuda errada é pior que nenhuma.", "**Chamado errado sai com 2**, e não 1: o script que chama distingue \"eu errei a chamada\" de \"o programa falhou\".", "**`Cli.perguntar`, `confirmar` e `segredo`** leem do terminal — e `Cli.tem_terminal()` diz se há alguém do outro lado, antes de travar esperando uma resposta num CI."]},
];

const headings = [{ id: 'o-erro-sugere-o-que-existe', text: "O erro sugere o que existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Argumentos da linha de comando"}
      description={"OS.argv para o simples, Cli.comando para o que tem opção, tipo e ajuda — gerada da declaração."}
      href={"/docs/partida/argumentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
