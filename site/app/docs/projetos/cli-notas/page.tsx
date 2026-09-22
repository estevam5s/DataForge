// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "CLI de anotações",
  description: "Uma ferramenta de terminal com subcomandos, persistência em JSON e saída legível.",
};

const blocos: Bloco[] = [
  {"p": "O projeto mais comum que existe, e o que mais cedo mostra se a arquitetura aguenta crescer: cada subcomando é uma ação, o estado mora num arquivo, e a leitura dos argumentos fica **separada** do que eles fazem — senão testar `adicionar` exige simular a linha de comando inteira."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`OS.argv()`", "ler os argumentos sem biblioteca"], ["`to_json` / `from_json`", "persistir sem banco"], ["`match`", "despachar o subcomando"], ["record", "a nota é imutável; editar devolve outra"]]}},
  {"h2": "Estrutura"},
  { code: `cli-notas/
  forge.toml
  src/
    main.df        le argv e despacha — e nada mais
    notas.df       a regra: adicionar, listar, concluir, buscar
    arquivo.df     onde o estado mora
  tests/
    notas_test.df`, lang: 'text' },
  { code: `[project]
name = "cli-notas"
version = "0.1.0"
description = "Anotações no terminal"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `record Nota:
    id: Integer
    texto: String
    feita: Boolean

action adicionar(notas, texto):
    given texto.trim() is "":
        trigger "uma nota vazia nao e uma nota"
    proximo := 1 given len(notas) is 0 otherwise notas[-1].id + 1
    yield [...notas, Nota(proximo, texto.trim(), no)]

action concluir(notas, id):
    achou := no
    novas := []
    cycle n in notas:
        given n.id is id:
            achou := yes
            novas.append(n with {"feita": yes})
        otherwise:
            novas.append(n)
    given not achou:
        trigger $"nao ha nota {id}"
    yield novas

action buscar(notas, termo):
    yield notas >> sift n: termo.lower() in n.texto.lower()

action linha(n):
    marca := "[x]" given n.feita otherwise "[ ]"
    yield $"{marca} {str(n.id).pad_start(3)}  {n.texto}"

// O despacho: a unica parte que conhece a linha de comando.
action executar(notas, argv):
    given len(argv) is 0:
        yield {"notas": notas, "saida": ["uso: notas <adicionar|listar|feita|buscar>"]}
    comando := argv[0]
    resto := " ".join(argv[1:])
    match comando:
        point "adicionar":
            yield {"notas": adicionar(notas, resto), "saida": ["anotado"]}
        point "listar":
            yield {"notas": notas, "saida": notas >> morph n: linha(n)}
        point "feita":
            yield {"notas": concluir(notas, int(resto)), "saida": ["concluida"]}
        point "buscar":
            yield {"notas": notas, "saida": buscar(notas, resto) >> morph n: linha(n)}
        default:
            yield {"notas": notas, "saida": [$"comando desconhecido: {comando}"]}

// A persistencia e so texto: o record vira vault na ida e volta na volta.
action para_json(notas):
    yield to_json(notas >> morph n: {"id": n.id, "texto": n.texto, "feita": n.feita})

action de_json(texto):
    yield from_json(texto) >> morph v: Nota(v["id"], v["texto"], v["feita"])

estado := []
estado := executar(estado, ["adicionar", "comprar", "cafe"])["notas"]
estado := executar(estado, ["adicionar", "revisar", "o", "PR"])["notas"]
estado := executar(estado, ["feita", "1"])["notas"]
cycle l in executar(estado, ["listar"])["saida"]:
    out l

volta := de_json(para_json(estado))
assert volta is estado
assert len(buscar(estado, "revisar")) is 1
assert estado[0].feita and not estado[1].feita`, lang: 'df', title: `src/notas.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/notas as N

crucible "notas":
    trial "o id continua depois do ultimo":
        a := N.adicionar([], "um")
        b := N.adicionar(a, "dois")
        expect b[1].id is 2

    trial "nota vazia e recusada":
        expect(lambda => N.adicionar([], "   ")).to_raise()

    trial "concluir o que nao existe levanta":
        expect(lambda => N.concluir([], 7)).to_raise()`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["`executar` recebe `argv` como lista", "testar exige mexer no `sys.argv` do processo"], ["o record é imutável (`with`)", "`concluir` muda a lista que outra parte ainda está lendo"], ["`trigger` com o motivo", "a CLI imprime *“erro”* e sai com 0"], ["o id vem do **último**, não do tamanho", "apagar a nota 2 de 3 faz a próxima nascer com o id 3 — repetido"]]}},
  {"h2": "Para ir além"},
  {"list": ["Troque o JSON por `Arcane.Database` sem mexer em `notas.df` — é para isso que a regra não sabe onde mora.", "Acrescente `--json` para a saída ser lida por outro programa.", "Veja [Receitas → CLI](/docs/receitas/cli) para cor, tabela e ajuda gerada."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"CLI de anotações"}
      description={"Uma ferramenta de terminal com subcomandos, persistência em JSON e saída legível."}
      href={"/docs/projetos/cli-notas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
