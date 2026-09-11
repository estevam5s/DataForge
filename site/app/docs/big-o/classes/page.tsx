import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "As classes de complexidade",
  description: "De O(1) a O(n!) — cada uma com um exemplo que roda.",
};

const blocos: Bloco[] = [
  {"p": "Cada classe abaixo tem um exemplo em DataForge que você pode rodar, e o comando que confirma a análise."},
  {"h2": "O(1) — constante"},
  {"p": "O tamanho da entrada não muda o tempo. Ler um índice, ler uma chave de vault, somar dois números."},
  { code: `action primeiro(xs):
    yield xs[0]

action tem_chave(v, chave):
    yield v.has(chave)

assert primeiro([9, 8, 7]) is 9
assert tem_chave({"a": 1}, "a") is yes`, lang: 'df' },
  {"p": "Um vault com um milhão de chaves responde tão rápido quanto um com três. É por isso que trocar `in cluster` por `in vault` derruba um O(n²) para O(n)."},
  {"h2": "O(log n) — logarítmica"},
  {"p": "Cada passo descarta metade do que sobrou. Vinte passos bastam para um milhão de itens."},
  { code: `action busca_binaria(ordenada, alvo):
    baixo := 0
    alto := len(ordenada) - 1
    persist baixo smaller_eq alto:
        meio := (baixo + alto) ~/ 2
        given ordenada[meio] is alvo:
            yield meio
        orif ordenada[meio] smaller alvo:
            baixo := meio + 1
        otherwise:
            alto := meio - 1
    yield -1

assert busca_binaria([1, 3, 5, 7, 9, 11], 9) is 4
assert busca_binaria([1, 3, 5], 4) is -1`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A entrada precisa estar ordenada", "texto": "Ordenar custa O(n log n). Buscar uma vez numa lista desordenada é O(n) — mais barato que ordenar para depois buscar. A busca binária compensa a partir da segunda busca."}},
  {"h2": "O(n) — linear"},
  {"p": "Dobrar a entrada dobra o tempo. Percorrer, somar, procurar sem índice."},
  { code: `action maior(xs):
    given len(xs) is 0:
        trigger "cluster vazio"
    m := xs[0]
    cycle x in xs:
        given x bigger m:
            m := x
    yield m

assert maior([3, 9, 2]) is 9`, lang: 'df' },
  {"p": "Dois laços em **sequência** também são O(n): O(n) + O(n) = O(2n) = O(n). É o aninhamento que multiplica, não a repetição."},
  {"h2": "O(n log n) — linearítmica"},
  {"p": "O melhor possível para ordenar comparando elementos — há prova matemática disso. `sorted()` é O(n log n)."},
  { code: `action ordenar_por_idade(pessoas):
    yield sorted(pessoas, chave := lambda p: p["idade"])

gente := [{"nome": "Ana", "idade": 30}, {"nome": "Bia", "idade": 25}]
assert ordenar_por_idade(gente)[0]["nome"] is "Bia"`, lang: 'df' },
  {"p": "Merge sort e quicksort são O(n log n) por dividirem ao meio e fazerem trabalho linear em cada nível: log n níveis × n de trabalho."},
  { code: `action merge_sort(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    esquerda := merge_sort(xs[:meio])
    direita := merge_sort(xs[meio:])
    yield intercalar(esquerda, direita)

action intercalar(a, b):
    saida := []
    i := 0
    j := 0
    persist i smaller len(a) and j smaller len(b):
        given a[i] smaller_eq b[j]:
            saida.append(a[i])
            i += 1
        otherwise:
            saida.append(b[j])
            j += 1
    yield [...saida, ...a[i:], ...b[j:]]

assert merge_sort([5, 2, 9, 1]) is [1, 2, 5, 9]`, lang: 'df' },
  {"h2": "O(n²) — quadrática"},
  {"p": "Dobrar a entrada quadruplica o tempo. Dois laços aninhados, comparar todos com todos."},
  { code: `action pares_iguais(xs):
    achados := []
    cycle i from 0 to len(xs) - 1:
        cycle j from i + 1 to len(xs) - 1:
            given xs[i] is xs[j]:
                achados.append(xs[i])
    yield achados

assert pares_iguais([1, 2, 1, 3]) is [1]`, lang: 'df' },
  {"p": "Quase sempre há uma versão O(n) usando um vault. Ver [padrões e como melhorar](/docs/big-o/padroes)."},
  {"h2": "O(n³) — cúbica"},
  {"p": "Três laços aninhados. Multiplicação de matriz pelo método direto."},
  { code: `action multiplicar(a, b, n):
    saida := [[0 cycle _ in range(n)] cycle _ in range(n)]
    cycle i from 0 to n - 1:
        cycle j from 0 to n - 1:
            cycle k from 0 to n - 1:
                saida[i][j] := saida[i][j] + a[i][k] * b[k][j]
    yield saida

m := [[1, 2], [3, 4]]
assert multiplicar(m, m, 2) is [[7, 10], [15, 22]]`, lang: 'df' },
  {"p": "Com n=1.000, são 10⁹ operações — minutos. Com n=10.000, 10¹² — dias."},
  {"h2": "O(2ⁿ) — exponencial"},
  {"p": "Cada item a mais **dobra** o custo. Recursão que se ramifica sem guardar resultado."},
  { code: `action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

assert fib(10) is 55`, lang: 'df' },
  {"p": "`fib(40)` faz mais de um bilhão de chamadas, quase todas repetindo cálculo já feito. Guardar o que já foi calculado derruba para O(n):"},
  { code: `cache := {}

action fib_rapido(n):
    given n smaller 2:
        yield n
    chave := str(n)
    given cache.has(chave):
        yield cache[chave]
    resultado := fib_rapido(n - 1) + fib_rapido(n - 2)
    cache[chave] := resultado
    yield resultado

assert fib_rapido(40) is 102334155`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Memoização", "texto": "Trocar tempo exponencial por memória linear é quase sempre um bom negócio. O snippet `memo` no VS Code escreve esse padrão."}},
  {"h2": "O(n!) — fatorial"},
  {"p": "Todas as permutações. Inviável acima de uma dúzia de itens: 12! já são 479 milhões."},
  { code: `action permutacoes(xs):
    given len(xs) smaller_eq 1:
        yield [xs]
    saida := []
    cycle i from 0 to len(xs) - 1:
        resto := [...xs[:i], ...xs[i + 1:]]
        cycle p in permutacoes(resto):
            saida.append([xs[i], ...p])
    yield saida

assert len(permutacoes([1, 2, 3])) is 6`, lang: 'df' },
  {"p": "O caixeiro-viajante por força bruta é O(n!). Para valores reais, usa-se programação dinâmica (O(2ⁿ·n²)) ou heurísticas."},
  {"h2": "Comparando"},
  {"componente": "escala-big-o"},
];

const headings = [{ id: 'o1-constante', text: "O(1) — constante", level: 2 as const }, { id: 'olog-n-logaritmica', text: "O(log n) — logarítmica", level: 2 as const }, { id: 'on-linear', text: "O(n) — linear", level: 2 as const }, { id: 'on-log-n-linearitmica', text: "O(n log n) — linearítmica", level: 2 as const }, { id: 'on-quadratica', text: "O(n²) — quadrática", level: 2 as const }, { id: 'on-cubica', text: "O(n³) — cúbica", level: 2 as const }, { id: 'o2-exponencial', text: "O(2ⁿ) — exponencial", level: 2 as const }, { id: 'on-fatorial', text: "O(n!) — fatorial", level: 2 as const }, { id: 'comparando', text: "Comparando", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"As classes de complexidade"}
      description={"De O(1) a O(n!) — cada uma com um exemplo que roda."}
      href={"/docs/big-o/classes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
