// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A constante que decide",
  description: "Big-O ignora a constante de propósito — e é ela que decide qual código é mais rápido no tamanho que você realmente tem.",
};

const blocos: Bloco[] = [
  {"p": "`O(n)` e `O(n²)` dizem como o custo **cresce**. Nenhum dos dois diz quanto o custo **é**. Entre um `O(n)` com constante mil e um `O(n²)` com constante um, o segundo ganha até n = 1000 — e muito sistema nunca passa de mil."},
  {"p": "Essa página é o contrapeso das outras: ela existe para que a análise não vire superstição."},
  {"h2": "Uma medição que prova o ponto"},
  {"p": "A ordenação por contagem é `O(n + k)`; a ordenação por comparação é `O(n log n)`. A primeira é assintoticamente melhor. Com 200 mil inteiros de 0 a 999:"},
  { code: `comparacao (n log n): 13.5 ms
contagem   (n + k):   381.3 ms
`, lang: 'text', title: `medido` },
  {"p": "A melhor no papel perdeu por **28x**. O motivo não é o algoritmo: `sorted` é um Timsort escrito em C, e a contagem está escrita em DataForge, interpretada. A constante de \"uma volta de laço no interpretador\" é centenas de vezes maior que a de \"uma comparação em C\"."},
  {"callout": {"tipo": "atencao", "titulo": "A regra prática", "texto": "Quando um lado roda em C e o outro no interpretador, a diferença de constante costuma engolir uma classe inteira de complexidade. Antes de reimplementar um embutido \"com um algoritmo melhor\", meça."}},
  {"h2": "E uma em que a classe ganha, com folga"},
  {"p": "O mesmo par de forças, invertido: aqui os dois lados pagam a mesma constante, e só a classe separa."},
  { code: `adopt Arcane.Time as T

N := 50000
BUSCAS := 2000

xs := [i cycle i in range(0, N)]
v := {}
cycle i in xs:
    v[i] := yes

// procura itens AUSENTES: o pior caso da busca linear, e o caso
// honesto — um item no começo da lista sai rápido por sorte.
inicio := T.monotonic()
cycle k from 1 to BUSCAS:
    given (N + k) in xs:
        out "achou"
cluster_ms := (T.monotonic() - inicio) * 1000

inicio := T.monotonic()
cycle k from 1 to BUSCAS:
    given (N + k) in v:
        out "achou"
vault_ms := (T.monotonic() - inicio) * 1000

out $"cluster: {round(cluster_ms, 1)} ms"
out $"vault:   {round(vault_ms, 1)} ms"
out $"razao:   {round(cluster_ms / vault_ms, 1)}x"
`, lang: 'df' },
  { code: `cluster: 255.8 ms
vault:   2.2 ms
razao:   118.5x
`, lang: 'text', title: `saída (50 mil itens)` },
  {"p": "**118x**, e essa distância cresce com `n` — é a diferença entre `O(n)` e `O(1)`. Nenhuma constante salva a busca linear aqui, porque não há constante: há uma classe."},
  {"h2": "Como um benchmark mente"},
  {"p": "A primeira versão da medição acima dizia o **contrário** — que o cluster era 3x mais rápido que o vault. Dois erros, os dois comuns:"},
  {"table": {"head": ["O erro", "O que ele fez", "A correção"], "rows": [["procurar itens que estão no **começo**", "`in` de cluster achava na posição 1, 2, 3… e nunca percorria nada", "procurar itens **ausentes**, ou sorteados"], ["medir a **montagem** junto da busca", "construir o vault de 50 mil dominou o tempo", "montar antes, cronometrar só a busca"]]}},
  {"p": "Um benchmark que confirma o que você esperava é o mais perigoso de todos — é o que ninguém revisa. Quando o número contrariar a teoria, desconfie do número **e** da teoria, nessa ordem."},
  {"h2": "Os quatro custos que o Big-O não conta"},
  {"table": {"head": ["Custo", "Por que ele some na notação", "Quando ele decide"], "rows": [["**a constante**", "some na definição de O", "sempre que `n` é pequeno"], ["**localidade de memória**", "não é uma operação", "percorrer um cluster contíguo é muito mais rápido que seguir ponteiros, com a mesma classe"], ["**alocação**", "conta como O(1)", "um algoritmo que aloca por item perde de um que trabalha no lugar"], ["**partida**", "não depende de `n`", "criar 5 threads custa mais que 60 ms de trabalho — [ver paralelismo](/docs/big-o/paralelo)"]]}},
  {"h2": "Medir: as três ferramentas"},
  {"table": {"head": ["Ferramenta", "Responde", "Quando usar"], "rows": [["[`dataforge big-o`](/docs/big-o/analisar)", "como o custo **cresce**", "antes de escrever, e no CI"], ["[`dataforge profile`](/docs/cli/bench)", "onde o tempo **está indo** hoje", "quando já está lento e você não sabe onde"], ["[`Arcane.Bench`](/docs/tecnicas/bench)", "quanto custa **este trecho**", "para comparar duas implementações"]]}},
  {"p": "As três respondem perguntas diferentes, e nenhuma substitui as outras. O `big-o` não sabe que você só tem 200 itens; o `profile` não sabe que amanhã serão 200 mil."},
  {"h2": "A ordem em que vale a pena mexer"},
  {"list": ["**Meça.** O gargalo quase nunca está onde a intuição aponta — este interpretador já teve sete otimizações feitas assim, e nenhuma delas no lugar esperado.", "**Troque a classe primeiro.** `O(n²)` para `O(n)` ganha de qualquer ajuste de constante, se `n` crescer.", "**Depois ataque a constante**, e só no trecho que o profile apontou.", "**Meça de novo.** Uma otimização que não foi medida depois é uma hipótese, não um ganho."], "ordered": true},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/paralelo", "title": "Complexidade em paralelo", "desc": "trabalho, profundidade e o teto de Amdahl"}, {"href": "/docs/big-o/analisar", "title": "Analisar o seu código", "desc": "o comando, e o que ele consegue provar"}, {"href": "/docs/cli/bench", "title": "Medir de verdade", "desc": "profile e bench: o tempo próprio de cada ação"}]},
];

const headings = [{ id: 'uma-medicao-que-prova-o-ponto', text: "Uma medição que prova o ponto", level: 2 as const }, { id: 'e-uma-em-que-a-classe-ganha-com-folga', text: "E uma em que a classe ganha, com folga", level: 2 as const }, { id: 'como-um-benchmark-mente', text: "Como um benchmark mente", level: 2 as const }, { id: 'os-quatro-custos-que-o-big-o-nao-conta', text: "Os quatro custos que o Big-O não conta", level: 2 as const }, { id: 'medir-as-tres-ferramentas', text: "Medir: as três ferramentas", level: 2 as const }, { id: 'a-ordem-em-que-vale-a-pena-mexer', text: "A ordem em que vale a pena mexer", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A constante que decide"}
      description={"Big-O ignora a constante de propósito — e é ela que decide qual código é mais rápido no tamanho que você realmente tem."}
      href={"/docs/big-o/constantes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
