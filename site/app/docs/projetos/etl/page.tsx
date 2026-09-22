// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pipeline ETL",
  description: "Extrair, converter, validar e carregar — e separar a linha ruim em vez de parar tudo.",
};

const blocos: Bloco[] = [
  {"p": "Um ETL de verdade recebe dado sujo. As duas respostas erradas são parar na primeira linha ruim (o lote de ontem nunca carrega) e engolir a linha ruim (o relatório de amanhã soma zero onde havia um valor). A certa é **separar**: a linha ruim vai para uma lista com o motivo, e o resto segue."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`lines` / `split`", "ler CSV sem biblioteca"], ["pipeline `>>`", "converter e filtrar em cadeia"], ["`Arcane.Decimal`", "somar dinheiro sem erro de float"], ["vault de rejeitados", "o motivo por linha, para quem corrige a fonte"]]}},
  {"h2": "Estrutura"},
  { code: `etl-vendas/
  src/
    extrair.df     texto -> linhas cruas
    transformar.df linha crua -> venda, ou motivo da recusa
    carregar.df    vendas -> banco / relatorio
    main.df        liga os tres
  dados/
    entrada.csv
  tests/`, lang: 'text' },
  { code: `[project]
name = "etl-vendas"
version = "0.1.0"
description = "ETL de vendas"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Decimal as Dec

steady CSV := """data,loja,valor
2026-09-01,centro,120.50
2026-09-01,norte,80.00
2026-09-02,centro,abc
2026-09-02,,45.10
2026-09-03,norte,19.99
"""

action extrair(texto):
    linhas := texto.trim().lines()
    cabecalho := linhas[0].split(",")
    cruas := []
    cycle i from 1 to len(linhas) - 1:
        campos := linhas[i].split(",")
        cruas.append({"linha": i + 1, "campos": zip(cabecalho, campos)})
    yield cruas

action transformar(crua):
    c := {}
    cycle par in crua["campos"]:
        c[par[0]] := par[1].trim()
    given c["loja"] is "":
        yield {"ok": no, "linha": crua["linha"], "motivo": "loja vazia"}
    given not regex_test("^[0-9]+([.][0-9]{1,2})?$", c["valor"]):
        yield {"ok": no, "linha": crua["linha"], "motivo": $"valor '{c["valor"]}' nao e numero"}
    yield {"ok": yes, "venda": {"data": c["data"], "loja": c["loja"], "valor": Dec.de(c["valor"])}}

action rodar(texto):
    resultados := extrair(texto) >> morph r: transformar(r)
    boas := resultados >> sift r: r["ok"] >> morph r: r["venda"]
    ruins := resultados >> sift r: not r["ok"]
    por_loja := {}
    cycle v in boas:
        por_loja[v["loja"]] := Dec.soma([por_loja[v["loja"]] ?? Dec.zero(), v["valor"]])
    yield {"carregadas": len(boas), "rejeitadas": ruins, "por_loja": por_loja}

r := rodar(CSV)
out $"{r['carregadas']} carregadas, {len(r['rejeitadas'])} rejeitadas"
cycle ruim in r["rejeitadas"]:
    out $"  linha {ruim['linha']}: {ruim['motivo']}"

assert r["carregadas"] is 3
assert Dec.texto(r["por_loja"]["norte"]) is "99.99"
assert Dec.texto(r["por_loja"]["centro"]) is "120.50"`, lang: 'df', title: `src/main.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/main as T

crucible "transformar":
    trial "valor com letra vira recusa, e nao zero":
        r := T.transformar({"linha": 4, "campos": [["data", "x"], ["loja", "a"], ["valor", "1,5"]]})
        expect r["ok"] is no
        expect r["linha"] is 4`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["a linha ruim é **separada**, não descartada", "o total fecha, e ninguém sabe que faltam três vendas"], ["o número da linha vai junto do motivo", "quem corrige a fonte procura a linha num arquivo de 40 mil"], ["`Decimal` a partir do **texto**", "`0.1 + 0.2` vira `0.30000000000000004` no relatório financeiro"], ["extrair, transformar e carregar em arquivos diferentes", "trocar CSV por API reescreve a validação junto"]]}},
  {"h2": "Para ir além"},
  {"list": ["Grave os rejeitados num CSV ao lado — é o que o time da fonte vai pedir.", "Troque o `for` por `Arcane.Quadro` quando o volume passar de 100 mil linhas: [Quadro](/docs/dados/quadro).", "Agende com cron e alerte quando `rejeitadas` passar de 5%."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pipeline ETL"}
      description={"Extrair, converter, validar e carregar — e separar a linha ruim em vez de parar tudo."}
      href={"/docs/projetos/etl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
