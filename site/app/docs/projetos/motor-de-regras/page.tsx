// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Motor de regras",
  description: "Regras de desconto e elegibilidade como dados, com o motivo de cada decisão.",
};

const blocos: Bloco[] = [
  {"p": "Regra de negócio escrita como `given` aninhado vira um arquivo que ninguém quer tocar: a décima regra é a exceção da terceira, e a ordem importa sem que ninguém saiba por quê. Um motor de regras transforma cada regra num **dado** com nome, condição e efeito — e a decisão passa a vir com a lista do que se aplicou."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["lambda como dado", "a condição e o efeito de cada regra"], ["prioridade explícita", "a ordem deixa de ser a do arquivo"], ["o relatório da decisão", "quem liga no suporte pergunta *por quê*"], ["`exclusiva`", "a regra que, quando vale, impede as outras"]]}},
  {"h2": "Estrutura"},
  { code: `motor-descontos/
  src/
    regras.df      o catalogo — so dados
    motor.df       avaliar, na ordem de prioridade
  tests/
    regras_test.df  um trial por regra`, lang: 'text' },
  { code: `[project]
name = "motor-descontos"
version = "0.1.0"
description = "Descontos como regras"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `action regra(nome, prioridade, quando, desconto, exclusiva := no):
    yield {"nome": nome, "prioridade": prioridade, "quando": quando,
           "desconto": desconto, "exclusiva": exclusiva}

REGRAS := [
    regra("black-friday", 1, lambda p: p["data"] is "2026-11-27", 0.30, yes),
    regra("primeira-compra", 2, lambda p: p["compras_antes"] is 0, 0.10),
    regra("carrinho-grande", 3, lambda p: p["total"] bigger_eq 500, 0.05),
    regra("fidelidade", 4, lambda p: p["compras_antes"] bigger_eq 10, 0.08)
]

action avaliar(pedido, regras):
    aplicadas := []
    cycle r in sorted(regras, lambda a: a["prioridade"]):
        given r["quando"](pedido):
            aplicadas.append(r)
            given r["exclusiva"]:
                halt
    // desconto composto, com teto: dois descontos de 50% nao sao 100%
    fator := 1.0
    cycle r in aplicadas:
        fator := fator * (1 - r["desconto"])
    desconto := min(1 - fator, 0.35)
    yield {"total": round(pedido["total"] * (1 - desconto), 2),
           "desconto": round(desconto, 4),
           "porque": aplicadas >> morph r: r["nome"]}

novo := avaliar({"data": "2026-09-21", "compras_antes": 0, "total": 600}, REGRAS)
out novo
assert novo["porque"] is ["primeira-compra", "carrinho-grande"]
assert novo["total"] is 513.0

bf := avaliar({"data": "2026-11-27", "compras_antes": 12, "total": 600}, REGRAS)
assert bf["porque"] is ["black-friday"]
assert bf["total"] is 420.0`, lang: 'df', title: `src/motor.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/motor as M

crucible "descontos":
    trial "o teto segura a soma":
        p := {"data": "2026-09-21", "compras_antes": 12, "total": 1000}
        expect M.avaliar(p, M.REGRAS)["desconto"] smaller_eq 0.35

    trial "a exclusiva impede as outras":
        p := {"data": "2026-11-27", "compras_antes": 0, "total": 1000}
        expect M.avaliar(p, M.REGRAS)["porque"] is ["black-friday"]`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["prioridade é um campo", "reordenar o arquivo muda o preço cobrado"], ["o resultado traz `porque`", "o suporte não consegue explicar um preço"], ["teto no desconto composto", "três regras somadas dão 120% e o pedido sai com preço negativo"], ["regra exclusiva **para** a avaliação", "a Black Friday soma com o cupom que ela devia substituir"]]}},
  {"h2": "Para ir além"},
  {"list": ["Carregue as regras de um arquivo — a condição vira uma expressão avaliada com [Arcane.Dsl](/docs/biblioteca/dsl).", "Registre cada decisão com `porque` para auditoria.", "Teste por propriedade: nenhum pedido sai com total negativo — [Propriedades](/docs/crucible/propriedades)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Motor de regras"}
      description={"Regras de desconto e elegibilidade como dados, com o motivo de cada decisão."}
      href={"/docs/projetos/motor-de-regras"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
