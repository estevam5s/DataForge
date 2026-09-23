// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Carga incremental",
  description: "Marca d'água, reprocessamento e a idempotência que separa um pipeline de um script.",
};

const blocos: Bloco[] = [
  {"p": "Ler tudo toda vez funciona até o dado crescer. A partir daí, o pipeline precisa saber **até onde já leu** — e precisa aguentar rodar duas vezes sem contar o mesmo dia duas vezes."},
  { code: `adopt Arcane.Pipeline as Pipe
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-inc-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

// Um fluxo com ESTADO lembra entre execuções.
fluxo := Pipe.fluxo("vendas", $"{pasta}/estado.json")

// Na primeira execução, a marca é void — e isso é o "carregue tudo".
assert Pipe.marca(fluxo, "ultima_venda") is void

TODAS := [
    {"id": 1, "dia": "2026-01-05"},
    {"id": 2, "dia": "2026-01-06"},
    {"id": 3, "dia": "2026-01-07"},
]

action carregar(ctx):
    desde := Pipe.marca(fluxo, "ultima_venda") ?? ""
    novas := [v cycle v in TODAS given v["dia"] > desde]
    given len(novas) > 0:
        // A marca só vai ao disco no FIM da execução: se a etapa
        // seguinte falhar, o próximo run relê o mesmo lote.
        Pipe.marcar(fluxo, "ultima_venda", novas[len(novas) - 1]["dia"])
    yield len(novas)

Pipe.etapa(fluxo, "carregar", carregar)
r := Pipe.rodar(fluxo)
assert r["ok"] is yes
out $"primeira execução: {r['resultados']['carregar']} linha(s)"

// A segunda execução não relê nada.
r2 := Pipe.rodar(fluxo)
out $"segunda execução: {r2['resultados']['carregar']} linha(s)"
assert r2["resultados"]["carregar"] is 0`, lang: 'df' },
  {"h2": "A marca só vale se ela for gravada DEPOIS"},
  {"p": "Gravar a marca antes de a etapa seguinte terminar é o defeito clássico: a carga vai até o dia 7, a transformação falha, e o próximo run começa do dia 8 — o dia 7 **nunca** é processado, e ninguém descobre. Por isso ela só vai ao disco no fim da execução."},
  {"h2": "Reprocessar é um comando, e não um acidente"},
  { code: `adopt Arcane.Pipeline as Pipe
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-inc2-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

fluxo := Pipe.fluxo("vendas", $"{pasta}/estado.json")
Pipe.etapa(fluxo, "ler", lambda ctx => 1)
Pipe.marcar(fluxo, "ate", "2026-01-07")
Pipe.rodar(fluxo)
assert Pipe.marca(fluxo, "ate") is "2026-01-07"

// 'esquecer_marca' é o botão de reprocessar — explícito, e não um
// efeito colateral de apagar um arquivo.
Pipe.esquecer_marca(fluxo, "ate")
assert Pipe.marca(fluxo, "ate") is void
out "a próxima execução relê tudo"`, lang: 'df' },
  {"h2": "Idempotência: a partição inteira, e não o acréscimo"},
  {"p": "A forma que funciona para reprocessar um dia é **apagar a partição daquele dia e gravar de novo**, e não acrescentar. Acrescentar duplica; sobrescrever a partição é idempotente por construção:"},
  { code: `adopt Arcane.Lago as Lago
adopt Arcane.OS as OS
adopt Arcane.IO as IO

raiz := $"{OS.temp_dir()}/df-lago-{randint(100000, 999999)}"
IO.mkdir(raiz)
defer:
    IO.remove_tree(raiz)

lago := Lago.lago(raiz)

action gravar_dia(dia, linhas):
    // Apagar a partição ANTES é o que torna o reprocessamento
    // idempotente: rodar duas vezes dá o mesmo resultado.
    Lago.remover_particao(lago, "vendas", {"dia": dia})
    Lago.acrescentar(lago, "vendas", linhas, ["dia"])
    yield len(linhas)

gravar_dia("2026-01-05", [{"dia": "2026-01-05", "v": 10}])
gravar_dia("2026-01-05", [{"dia": "2026-01-05", "v": 10}])   // de novo

lidas := Lago.ler(lago, "vendas", {"dia": "2026-01-05"})
assert len(lidas) is 1
out "rodou duas vezes, e há uma linha"`, lang: 'df' },
  {"table": {"head": ["Estratégia", "Reprocessar é", "Quando"], "rows": [["acrescentar", "**duplicar**", "só para evento imutável com id próprio"], ["sobrescrever a partição", "idempotente", "o padrão para dado por período"], ["`upsert` por chave", "idempotente", "quando a linha muda de valor depois"], ["truncar e recarregar", "idempotente, e caro", "tabela pequena de apoio"]]}},
  {"callout": {"tipo": "nota", "titulo": "A marca d'água não é a data de hoje", "texto": "Ela é o maior valor **do que foi lido**. Usar a data do relógio faz o pipeline perder tudo o que chegou atrasado — e dado atrasado é a regra, não a exceção: um evento de ontem que só chegou hoje de manhã some para sempre."}},
];

const headings = [{ id: 'a-marca-so-vale-se-ela-for-gravada-depois', text: "A marca só vale se ela for gravada DEPOIS", level: 2 as const }, { id: 'reprocessar-e-um-comando-e-nao-um-acidente', text: "Reprocessar é um comando, e não um acidente", level: 2 as const }, { id: 'idempotencia-a-particao-inteira-e-nao-o-acrescimo', text: "Idempotência: a partição inteira, e não o acréscimo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Carga incremental"}
      description={"Marca d'água, reprocessamento e a idempotência que separa um pipeline de um script."}
      href={"/docs/dados/incremental"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
