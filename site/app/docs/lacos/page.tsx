import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Laços",
  description: "cycle, persist, perform, halt e skip — os quatro laços da linguagem.",
};

const blocos: Bloco[] = [
  {"h2": "cycle — intervalo numérico"},
  { code: `cycle i from 1 to 5:
    out i                 # 1 2 3 4 5 — o limite é INCLUSIVO

cycle i from 0 to 10 step 2:
    out i                 # 0 2 4 6 8 10

cycle i from 5 to 1 step -1:
    out i                 # 5 4 3 2 1` },
  {"callout": {"tipo": "nota", "texto": "`to` é inclusivo nos dois extremos. `cycle i from 1 to 5` roda cinco vezes, não quatro — diferente do `range(1, 5)` do Python."}},
  {"h2": "cycle — sobre uma coleção"},
  { code: `cycle fruta in ["maca", "uva", "pera"]:
    out fruta

cycle letra in "abc":
    out letra

precos := {"maca": 3.5, "uva": 8.0}
cycle chave in precos.keys():
    out $"{chave}: {precos[chave]}"` },
  {"p": "Percorrer um `Vault` diretamente com `cycle k in precos` também funciona e itera as **chaves** — a mesma convenção de `in`."},
  {"h2": "persist — enquanto (while)"},
  { code: `n := 1024
divisoes := 0
persist n bigger 1:
    n := n ~/ 2
    divisoes += 1

out $"1024 vira 1 apos {divisoes} divisoes"` },
  { code: `1024 vira 1 apos 10 divisoes`, lang: 'text', title: `saída` },
  {"h2": "perform — faça-enquanto (do-while)"},
  {"p": "A condição é testada **depois** do corpo, então ele roda pelo menos uma vez:"},
  { code: `execucoes := 0
perform:
    execucoes += 1
persist no

out $"executou {execucoes} vez mesmo com a condicao falsa"` },
  {"h2": "halt e skip"},
  {"table": {"head": ["Palavra", "Efeito"], "rows": [["`halt`", "sai do laço"], ["`skip`", "vai para a próxima iteração"]]}},
  { code: `selecionados := []
cycle i from 1 to 100:
    given i % 3 is 0:
        skip                  # pula os múltiplos de 3
    given i bigger 10:
        halt                  # para ao passar de 10
    selecionados.append(i)

out selecionados` },
  { code: `[1, 2, 4, 5, 7, 8, 10]`, lang: 'text', title: `saída` },
  {"callout": {"tipo": "nota", "texto": "`halt` e `skip` **atravessam** blocos `monitor` sem serem capturados. São controle de fluxo, não erros — e o interpretador trata os dois como coisas diferentes."}},
  {"h2": "Laços aninhados"},
  { code: `matriz := []
cycle i from 1 to 3:
    linha := []
    cycle j from 1 to 3:
        linha.append(i * j)
    matriz.append(linha)

cycle l in matriz:
    out l` },
  {"p": "`halt` e `skip` afetam apenas o laço **mais interno** em que aparecem."},
  {"h2": "Quando não usar laço"},
  {"p": "Para transformar ou filtrar uma coleção, [compreensões](/docs/fundamentos/compreensoes) e [pipelines](/docs/pipelines) dizem melhor o que você quer:"},
  { code: `# com laço — descreve COMO
quadrados := []
cycle n in nums:
    quadrados.append(n * n)

# com compreensão — descreve O QUE
quadrados := [n * n cycle n in nums]

# com pipeline — quando há vários estágios
total := nums >> sift n: n bigger 0 >> morph n: n * n >> distill a, v: a + v 0` },
  {"p": "O laço continua sendo a escolha certa quando há lógica com vários passos, efeitos colaterais ou saída antecipada."},
];

const headings = [{ id: 'cycle--intervalo-numerico', text: "cycle — intervalo numérico", level: 2 as const }, { id: 'cycle--sobre-uma-colecao', text: "cycle — sobre uma coleção", level: 2 as const }, { id: 'persist--enquanto-while', text: "persist — enquanto (while)", level: 2 as const }, { id: 'perform--faca-enquanto-do-while', text: "perform — faça-enquanto (do-while)", level: 2 as const }, { id: 'halt-e-skip', text: "halt e skip", level: 2 as const }, { id: 'lacos-aninhados', text: "Laços aninhados", level: 2 as const }, { id: 'quando-nao-usar-laco', text: "Quando não usar laço", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Laços"}
      description={"cycle, persist, perform, halt e skip — os quatro laços da linguagem."}
      href={"/docs/lacos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
