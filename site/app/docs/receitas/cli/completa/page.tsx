// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Uma ferramenta inteira",
  description: "Do argumento ao código de saída: um contador de linhas de código, em 60 linhas.",
};

const blocos: Bloco[] = [
  {"p": "Juntando tudo: uma ferramenta que varre uma pasta, conta linhas por extensão e responde em tabela ou JSON — com ajuda, validação, cor condicional e código de saída."},
  { code: `adopt Arcane.Cli as Cli
adopt Arcane.Color as Cor
adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Serialization as Ser

// ── o que o comando aceita ─────────────────────────────────
action montar():
    cmd := Cli.comando("contar", "Conta linhas por extensão", "1.0.0")
    cmd.posicional("pasta", "a pasta a varrer")
    cmd.opcao("formato", "texto", "f", "tabela", "tabela ou json", no,
              ["tabela", "json"])
    cmd.opcao("minimo", "inteiro", "m", 0, "esconde extensões abaixo disto")
    cmd.exemplo("contar src --formato=json", "para outro programa ler")
    yield cmd

// ── o trabalho, sem saber que existe terminal ──────────────
action contar(pasta):
    por_extensao := {}
    cycle nome in IO.list_dir(pasta):
        caminho := $"{pasta}/{nome}"
        given not IO.file_exists(caminho):
            skip
        ponto := caminho.split(".")
        ext := ponto[len(ponto) - 1] given len(ponto) > 1 otherwise "(sem)"
        linhas := len(IO.read(caminho).split("\\n"))
        por_extensao[ext] := (por_extensao[ext] ?? 0) + linhas
    yield por_extensao

// ── o desenho, que é a única parte que sabe ────────────────
action desenhar(dados, formato, minimo):
    filtrado := {}
    cycle ext in keys(dados):
        given dados[ext] >= minimo:
            filtrado[ext] := dados[ext]
    given formato is "json":
        yield Ser.to_json(filtrado)
    linhas := [["extensão", "linhas"]]
    cycle ext in sorted(keys(filtrado)):
        linhas.append([ext, str(filtrado[ext])])
    yield Cor.table(linhas)

// ── juntar ─────────────────────────────────────────────────
pasta := $"{OS.temp_dir()}/df-contar-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)
IO.write($"{pasta}/a.df", "out 1\\nout 2\\n")
IO.write($"{pasta}/b.df", "out 3\\n")
IO.write($"{pasta}/leiame.md", "# título\\n")

args := montar().ler([pasta, "--formato=json"])
dados := contar(args["pasta"])
assert dados["df"] is 5 and dados["md"] is 2
out desenhar(dados, args["formato"], args["minimo"])

// e em tabela
out desenhar(dados, "tabela", 0)`, lang: 'df' },
  {"h2": "As decisões que ela carrega"},
  {"table": {"head": ["Decisão", "O que ela evita"], "rows": [["o trabalho não sabe que existe terminal", "não dá para testar contagem sem simular um terminal"], ["o desenho é a única parte que colore", "a cor vazar para o JSON, que outro programa vai ler"], ["`defer` logo depois de criar a pasta", "o temporário sobreviver a uma falha no meio"], ["`?? 0` ao somar no vault", "`KeyError` na primeira extensão nova"], ["a ajuda e os exemplos na declaração", "a ajuda envelhecer na primeira opção nova"]]}},
  {"h2": "O que falta para virar produção"},
  {"list": ["**Ignorar `.git`, `node_modules` e binários** — varrer tudo é o defeito nº 1 de um contador de linhas.", "**Um `--excluir` com padrão glob**, porque a lista do que ignorar é do projeto, não da ferramenta.", "**Paralelismo** quando a pasta é grande: `P.map` sobre os arquivos, que é E/S e por isso escapa do GIL.", "**Um teste que roda a ferramenta como processo** e confere o código de saída."]},
];

const headings = [{ id: 'as-decisoes-que-ela-carrega', text: "As decisões que ela carrega", level: 2 as const }, { id: 'o-que-falta-para-virar-producao', text: "O que falta para virar produção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Uma ferramenta inteira"}
      description={"Do argumento ao código de saída: um contador de linhas de código, em 60 linhas."}
      href={"/docs/receitas/cli/completa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
