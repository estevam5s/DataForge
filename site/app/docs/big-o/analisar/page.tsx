// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Analisar o seu código",
  description: "O comando, o que ele prova, e o que ele honestamente não prova.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge big-o` lê a árvore do programa e conta estrutura: quantos laços aninhados, se o contador dobra ou soma, quantas vezes uma ação chama a si mesma, e quanto custa cada função embutida que aparece."},
  { code: `dataforge big-o programa.df           # a classe de cada ação
dataforge big-o src/ -v              # com o porquê e a sugestão
dataforge big-o src/ --strict        # sai com erro acima de O(n log n)
dataforge big-o --escala             # a tabela de referência
dataforge big-o programa.df --json   # para o editor e o CI`, lang: 'bash' },
  {"h2": "No editor"},
  {"p": "A [extensão do VS Code](/docs/tecnicas/editor) mostra a classe acima de cada ação, enquanto se escreve. O motivo aparece no hover, e o comando *Analisar complexidade* abre o relatório completo."},
  {"p": "É a mesma análise: a extensão chama a CLI. O que o editor mostra é exatamente o que o CI vai reprovar."},
  {"h2": "O que ele detecta"},
  {"table": {"head": ["Padrão", "Classe", "Como reconhece"], "rows": [["`cycle x in xs`", "O(n)", "uma volta por item"], ["dois `cycle` aninhados", "O(n²)", "multiplica as ordens"], ["`persist` com `n ~/ 2`", "O(log n)", "a variável se divide a cada volta"], ["`persist` com `n -= 1`", "O(n)", "avança de um em um"], ["`cycle i from 1 to 10`", "O(1)", "limites constantes"], ["`sorted(xs)`", "O(n log n)", "custo conhecido da embutida"], ["`x in xs`", "O(n)", "percorre o cluster"], ["`v.has(k)`", "O(1)", "vault indexa"], ["uma chamada recursiva, `n - 1`", "O(n)", "profundidade linear"], ["uma chamada recursiva, `n ~/ 2`", "O(log n)", "profundidade logarítmica"], ["duas chamadas, `n - 1`", "O(2ⁿ)", "ramifica sem dividir"], ["duas chamadas, metade cada", "O(n log n)", "divisão e conquista"], ["compreensão aninhada", "O(n²)", "cabe numa linha e é um laço duplo"]]}},
  {"h2": "A distinção que mais importa"},
  {"p": "Merge sort e fibonacci ingênuo têm a **mesma forma**: uma ação que chama a si mesma duas vezes. O que os separa é a entrada — metade contra n−1:"},
  { code: `// duas chamadas sobre METADE  →  O(n log n)
action merge_sort(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    yield intercalar(merge_sort(xs[:meio]), merge_sort(xs[meio:]))

// duas chamadas sobre n-1  →  O(2^n)
action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)`, lang: 'df' },
  {"p": "Confundir os dois condenaria todo algoritmo de divisão e conquista. A análise olha o argumento da chamada recursiva para separá-los."},
  {"h2": "Generators têm custo por item"},
  {"p": "Um `stream action` com `persist yes` não é um laço infinito por engano — é uma sequência preguiçosa, e quem consome decide quantos itens quer. A análise reporta o custo **por item emitido**:"},
  { code: `stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1

out naturais().take(5)`, lang: 'df' },
  {"p": "`naturais` é O(1) por item. Analisar o corpo inteiro daria O(?) para todo generator correto da linguagem."},
  {"h2": "O que ele não faz"},
  {"p": "Três limites, declarados de propósito:"},
  {"list": ["**Não decide o indecidível.** Saber se um laço termina é o problema da parada. Quando a análise não consegue provar, ela diz `O(?)` em vez de inventar um número.", "**Não segue valor.** `cycle i from 1 to k` é O(k). Se `k` vier de fora, ela usa `k` como símbolo em vez de fingir que é constante.", "**Não mede constante.** O(n) com constante grande pode ser mais lento que O(n²) para entrada pequena."]},
  {"callout": {"tipo": "nota", "titulo": "O(?) não é erro", "texto": "Significa que a análise não conseguiu provar a ordem, não que o código esteja errado. Nos 216 exercícios da linguagem, zero ficam indeterminados."}},
  {"h2": "No CI"},
  {"p": "`--strict` faz o comando sair com código 1 se alguma ação passar de O(n log n). É o suficiente para uma regra de projeto:"},
  { code: `# .github/workflows/ci.yml
- name: complexidade
  run: dataforge big-o src/ --strict`, lang: 'text' },
  {"p": "Use com julgamento: há problemas cuja melhor solução conhecida é quadrática. A regra serve para o quadrático **acidental**, que é a maioria."},
];

const headings = [{ id: 'no-editor', text: "No editor", level: 2 as const }, { id: 'o-que-ele-detecta', text: "O que ele detecta", level: 2 as const }, { id: 'a-distincao-que-mais-importa', text: "A distinção que mais importa", level: 2 as const }, { id: 'generators-tem-custo-por-item', text: "Generators têm custo por item", level: 2 as const }, { id: 'o-que-ele-nao-faz', text: "O que ele não faz", level: 2 as const }, { id: 'no-ci', text: "No CI", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Analisar o seu código"}
      description={"O comando, o que ele prova, e o que ele honestamente não prova."}
      href={"/docs/big-o/analisar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
