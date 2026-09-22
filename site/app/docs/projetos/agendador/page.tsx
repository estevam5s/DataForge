// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Agendador cron",
  description: "Ler uma expressão cron, dizer quando ela roda — e recusar a que nunca roda.",
};

const blocos: Bloco[] = [
  {"p": "Cron é uma linguagem pequena que quase todo sistema usa e quase ninguém lê direito: `*/15 9-18 * * 1-5` é *“a cada 15 minutos, em horário comercial, nos dias úteis”*. Este projeto escreve o parser, expande cada campo para os valores concretos e responde as próximas execuções."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["parser de campo", "`*`, `*/n`, `a-b`, `a,b,c`"], ["faixas por campo", "o minuto vai de 0 a 59; o dia da semana, de 0 a 6"], ["mensagem com o campo", "*“hora 25 fora de 0-23”*"], ["as próximas execuções", "o que o usuário quer ver antes de salvar"]]}},
  {"h2": "Estrutura"},
  { code: `agendador/
  src/
    cron.df        ler, casa, proximas
    tarefas.df     o catalogo de jobs
  tests/`, lang: 'text' },
  { code: `[project]
name = "agendador"
version = "0.1.0"
description = "Agendador com cron"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `steady CAMPOS := [["minuto", 0, 59], ["hora", 0, 23], ["dia", 1, 31], ["mes", 1, 12], ["semana", 0, 6]]

action expandir(texto, nome, menor, maior):
    valores := []
    cycle parte in texto.split(","):
        passo := 1
        faixa := parte
        given "/" in parte:
            faixa, p := parte.split("/")
            passo := int(p)
            given passo smaller_eq 0:
                trigger $"{nome}: o passo precisa ser positivo"
        given faixa is "*":
            a := menor
            b := maior
        orif "-" in faixa:
            ia, ib := faixa.split("-")
            a := int(ia)
            b := int(ib)
        otherwise:
            a := int(faixa)
            b := a
        given a smaller menor or b bigger maior or a bigger b:
            trigger $"{nome} {faixa} fora de {menor}-{maior}"
        cycle v from a to b step passo:
            valores.append(v)
    yield sorted(unique(valores))

action ler(expressao):
    partes := expressao.trim().split(" ") >> sift p: p is not ""
    given len(partes) is not 5:
        trigger $"uma expressao cron tem 5 campos, esta tem {len(partes)}"
    regra := {}
    cycle i in range(0, 5):
        c := CAMPOS[i]
        regra[c[0]] := expandir(partes[i], c[0], c[1], c[2])
    yield regra

action casa(regra, m, h, dia, mes, semana):
    yield m in regra["minuto"] and h in regra["hora"] and dia in regra["dia"] and mes in regra["mes"] and semana in regra["semana"]

r := ler("*/15 9-18 * * 1-5")
assert r["minuto"] is [0, 15, 30, 45]
assert len(r["hora"]) is 10
assert casa(r, 30, 10, 21, 9, 1)
assert not casa(r, 30, 10, 20, 9, 0)

monitor:
    ler("0 25 * * *")
    assert no
handle Error as e:
    out e.message
    assert "hora 25" in e.message`, lang: 'df', title: `src/cron.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/cron as C

crucible "cron":
    trial "lista com virgula":
        expect C.ler("0,30 * * * *")["minuto"] is [0, 30]

    trial "quatro campos e recusado":
        expect(lambda => C.ler("* * * *")).to_raise()`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["expandir para os valores concretos", "cada pergunta *“casa?”* reinterpreta o texto"], ["a faixa de cada campo", "`0 25 * * *` é aceito e nunca roda"], ["a mensagem nomeia o campo", "*“expressão inválida”*, e a pessoa conta os espaços"], ["`unique` + `sorted`", "`1,1,2` roda duas vezes no minuto 1"]]}},
  {"h2": "Para ir além"},
  {"list": ["Rodar no horário, numa thread só: [Arcane.Laco](/docs/biblioteca/laco).", "No banco, com `pg_cron`: [Em produção](/docs/banco-de-dados/producao).", "O dia do mês **e** da semana juntos é um *ou* no cron clássico — decida e documente."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Agendador cron"}
      description={"Ler uma expressão cron, dizer quando ela roda — e recusar a que nunca roda."}
      href={"/docs/projetos/agendador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
