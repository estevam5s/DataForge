// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Planilha reativa",
  description: "Células que dependem de células — recalculadas sozinhas, só quando alguém lê, e sem o valor que nunca existiu.",
};

const blocos: Bloco[] = [
  {"p": "Uma planilha é o programa reativo que todo mundo já usou: mudar uma célula atualiza as que dependem dela. O que torna isso difícil é o **losango** — quando `C` depende de `A` e de `B`, e `B` também depende de `A`, uma propagação ingênua mostra por um instante um valor que nunca foi verdade."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`R.sinal`", "a célula de entrada"], ["`R.derivado`", "a célula com fórmula — preguiçosa e memorizada"], ["`R.efeito`", "quem desenha a tela"], ["a onda de duas fases", "o losango sem valor intermediário"]]}},
  {"h2": "Estrutura"},
  { code: `orcamento/
  src/
    celulas.df     as entradas e as formulas
    tela.df        o efeito que imprime
  tests/`, lang: 'text' },
  { code: `[project]
name = "orcamento"
version = "0.1.0"
description = "Orçamento reativo"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Reativo as R

steady receita := R.sinal(10000)
steady custo_fixo := R.sinal(4000)
steady margem := R.sinal(0.2)

contas := {"n": 0}
action calcular_variavel():
    contas["n"] += 1
    yield receita.ler() * 0.3

steady custo_variavel := R.derivado(calcular_variavel)
steady lucro := R.derivado(lambda => receita.ler() - custo_fixo.ler() - custo_variavel.ler())
steady meta := R.derivado(lambda => receita.ler() * margem.ler())

vistos := []
steady tela := R.efeito(lambda => vistos.append(lucro.ler()))

assert lucro.ler() is 3000.0
assert contas["n"] is 1

// 'lucro' le 'receita' direto E via 'custo_variavel': o losango.
receita.escrever(20000)
assert lucro.ler() is 10000.0

// O efeito viu 3000 e depois 10000 — nunca o intermediario de 13000
// (20000 - 4000 - o custo velho de 3000).
assert vistos is [3000.0, 10000.0]
assert meta.ler() is 4000.0
out vistos`, lang: 'df', title: `src/celulas.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/celulas as C

crucible "planilha":
    trial "ler duas vezes nao recalcula":
        antes := C.contas["n"]
        C.lucro.ler()
        C.lucro.ler()
        expect C.contas["n"] is antes`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o derivado é **preguiçoso**", "cada leitura recalcula a planilha inteira"], ["propagação em duas fases", "a tela pisca um lucro de 13 mil que nunca existiu"], ["o efeito roda uma vez por onda", "a tela redesenha duas vezes por mudança"], ["dependências descobertas na execução", "a lista de dependências escrita à mão envelhece na primeira fórmula nova"]]}},
  {"h2": "Para ir além"},
  {"list": ["A explicação do losango, medida: [Arcane.Reativo](/docs/biblioteca/reativo).", "Agrupar três escritas numa notificação: `R.lote`.", "Fluxos (não valores): `R.observavel`."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Planilha reativa"}
      description={"Células que dependem de células — recalculadas sozinhas, só quando alguém lê, e sem o valor que nunca existiu."}
      href={"/docs/projetos/planilha-reativa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
