// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Cli",
  description: "A linha de comando de um programa escrito em DataForge: opções tipadas, subcomandos, ajuda gerada e perguntas no terminal.",
};

const blocos: Bloco[] = [
  {"p": "O `dataforge` tem uma CLI completa. Um programa **escrito em** DataForge não tinha nada: `OS.args()` devolve a lista crua, e ler `--porta=8080` dela é escrever o mesmo laço de novo em cada programa."},
  {"h2": "Declarar"},
  { code: `adopt Arcane.Cli as Cli

app := Cli.comando("relatorio", sobre := "Gera o relatório do mês.",
    versao := "1.0.0")

app.opcao("mes", "inteiro", curta := "m", exigida := yes, sobre := "de 1 a 12")
app.opcao("formato", escolhas := ["csv", "json"], padrao := "csv")
app.opcao("enviar", "sim_nao", sobre := "manda por e-mail")
app.posicional("saida", exigido := no)
app.exemplo("relatorio -m 9 --formato json out.json")

opcoes := app.rodar()
out opcoes["mes"], opcoes["formato"]`, lang: 'df' },
  {"table": {"head": ["Tipo", "Na linha"], "rows": [["`texto`", "`--nome valor`"], ["`inteiro` · `numero`", "convertidos, e recusados se não forem"], ["`sim_nao`", "`--nome` (sem valor)"], ["`lista`", "`--nome a,b,c`"]]}},
  {"p": "As formas aceitas são as de sempre: `--porta 9000`, `--porta=9000`, `-p 9000` e `-p9000`."},
  {"h2": "A ajuda sai da declaração"},
  { code: `Sobe a forja.

uso: forja [opções] [config]

opções:
  -p, --porta INTEIRO  a porta  (padrão: 8080)
      --modo TEXTO     o ambiente  (dev|prod; padrão: dev)
  -v, --verboso        fala mais
  -h, --ajuda          mostra esta ajuda
      --versao         mostra a versão`, lang: 'text' },
  {"callout": {"tipo": "dica", "titulo": "Por que gerada", "texto": "Escrita à mão, ela envelhece no primeiro flag novo — e a **ajuda errada é pior que nenhuma**, porque quem lê confia nela."}},
  {"h2": "O erro sugere"},
  { code: `$ relatorio --mess 9
relatorio: não conheço '--mess'.
  Você quis dizer '--mes'?

$ relatorio --mes abc
relatorio: '--mes' espera inteiro e recebeu 'abc'.

$ relatorio --formato xml
relatorio: '--formato' aceita csv, json — veio 'xml'.`, lang: 'bash' },
  {"callout": {"tipo": "nota", "titulo": "Sai com código 2", "texto": "Código 1 é *\"o programa rodou e deu errado\"*; 2 é *\"você chamou errado\"*. Um script que testa `$?` precisa distinguir os dois."}},
  {"h2": "Subcomandos"},
  { code: `app := Cli.comando("forja")
subir := app.subcomando("subir", "põe no ar")
subir.opcao("porta", "inteiro", padrao := 8080)
app.subcomando("parar", "tira do ar")

opcoes := app.rodar()
match opcoes["__comando__"]:
    point "subir":
        subir_servidor(opcoes["porta"])
    point "parar":
        parar_servidor()`, lang: 'df' },
  {"h2": "Perguntar"},
  { code: `nome := Cli.perguntar("Nome do projeto", padrao := "meu-app")
banco := Cli.escolher("Banco?", ["SQLite", "Postgres", "MySQL"])
senha := Cli.segredo("Senha do banco")

given Cli.confirmar("Apagar tudo?", padrao := no):
    apagar()`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Elas recusam rodar sem terminal", "texto": "Numa pipeline de CI, uma pergunta interativa trava o build **para sempre**, sem dizer por quê. É melhor falhar na hora, dizendo qual opção passar. `Cli.tem_terminal()` responde antes."}},
  {"h2": "Console interativo"},
  { code: `c := Cli.console("forja> ", sobre := "Console da forja.")
c.registrar("listar", lambda _ => listar_pedidos(), "mostra os pedidos")
c.registrar("ver", lambda id => ver(id), "detalha um pedido")
c.rodar()`, lang: 'df' },
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'a-ajuda-sai-da-declaracao', text: "A ajuda sai da declaração", level: 2 as const }, { id: 'o-erro-sugere', text: "O erro sugere", level: 2 as const }, { id: 'subcomandos', text: "Subcomandos", level: 2 as const }, { id: 'perguntar', text: "Perguntar", level: 2 as const }, { id: 'console-interativo', text: "Console interativo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Cli"}
      description={"A linha de comando de um programa escrito em DataForge: opções tipadas, subcomandos, ajuda gerada e perguntas no terminal."}
      href={"/docs/biblioteca/cli"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
