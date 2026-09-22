// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Classificador de clientes",
  description: "Treinar, medir no que o modelo não viu, e explicar o que ele aprendeu.",
};

const blocos: Bloco[] = [
  {"p": "O erro mais caro em aprendizado de máquina não é o modelo ruim: é o modelo medido nos mesmos dados em que treinou, que parece ótimo até a primeira semana em produção. Este projeto separa antes de olhar, mede no conjunto de teste e compara com a linha de base — *“sempre responder a classe mais comum”* — que é o número que o modelo precisa bater."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`ML.dividir`", "separar treino e teste **antes** de tudo"], ["`ML.floresta`", "o modelo"], ["`ML.avaliar`", "acurácia e F1 no que ele não viu"], ["a linha de base", "o número que ele precisa bater"]]}},
  {"h2": "Estrutura"},
  { code: `churn/
  src/
    dados.df       ler e limpar
    treinar.df     dividir, treinar, avaliar
    prever.df      carregar o modelo salvo e responder
  modelos/         o .json treinado (versionado com a data)
  tests/`, lang: 'text' },
  { code: `[project]
name = "churn"
version = "0.1.0"
description = "Classificador de cancelamento"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Cortex as ML

// Dados sinteticos: quem visita pouco e tem plano barato cancela mais.
clientes := []
cycle i from 1 to 240:
    visitas := i % 12
    plano := [29, 59, 99][i % 3]
    cancela := "sim" given visitas smaller 4 and plano is 29 otherwise "nao"
    clientes.append({"visitas": visitas, "plano": plano, "meses": i % 24, "cancela": cancela})

treino, teste := ML.dividir(clientes, 0.25, 42, "cancela")
modelo := ML.floresta(treino, "cancela", ["visitas", "plano", "meses"], 20)
r := ML.avaliar(modelo, teste)

// A linha de base: responder sempre a classe mais comum.
nao := len(teste >> sift c: c["cancela"] is "nao")
base := nao / len(teste)
out $"acuracia {round(r['acuracia'], 3)} contra linha de base {round(base, 3)}"

assert r["acuracia"] bigger base
assert len(treino) + len(teste) is len(clientes)`, lang: 'df', title: `src/treinar.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/treinar as T

crucible "modelo":
    trial "ganha da linha de base":
        expect T.r["acuracia"] bigger T.base

    trial "nenhum cliente fica de fora da divisao":
        expect len(T.treino) + len(T.teste) is len(T.clientes)`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["dividir **antes** de olhar", "a acurácia de 99% é memória, não aprendizado"], ["semente fixa (`42`)", "cada execução dá um número, e ninguém sabe se melhorou"], ["comparar com a linha de base", "90% de acerto num conjunto com 90% de *“não”* não aprendeu nada"], ["estratificar pela classe", "o teste sai sem nenhum *“sim”*, e o F1 não tem o que medir"]]}},
  {"h2": "Para ir além"},
  {"list": ["Importância de cada variável e matriz de confusão: [ML](/docs/tecnicas/ml).", "Salvar e versionar o modelo: `ML.salvar` com a data no nome.", "Os açúcares `train` e `predict` da linguagem: [Arcane.Cortex](/docs/biblioteca/cortex)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Classificador de clientes"}
      description={"Treinar, medir no que o modelo não viu, e explicar o que ele aprendeu."}
      href={"/docs/projetos/classificador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
