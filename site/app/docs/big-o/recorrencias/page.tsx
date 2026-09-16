// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Recorrências e o Teorema Mestre",
  description: "Como se resolve o custo de um algoritmo que chama a si mesmo — e por que o merge sort e o fibonacci ingênuo têm a mesma forma e custos opostos.",
};

const blocos: Bloco[] = [
  {"p": "Um laço se conta olhando. Uma **recursão**, não: o custo dela é definido em termos de si mesmo, e resolver isso é a única parte da análise de complexidade que tem método próprio."},
  {"p": "O método cabe numa linha. Escreva quanto custa uma chamada em função do que ela delega:"},
  { code: `T(n) = a · T(n/b) + f(n)`, lang: 'text' },
  {"list": ["**a** — quantas chamadas a função faz a si mesma", "**b** — por quanto a entrada é dividida em cada uma", "**f(n)** — o trabalho que ela faz **fora** das chamadas"]},
  {"p": "Os três números estão à vista no código, e é essa leitura que o `dataforge big-o` faz por você."},
  {"h2": "Os três casos do Teorema Mestre"},
  {"p": "Compare o que a recursão multiplica (`n^log_b(a)`) com o que ela faz por nível (`f(n)`). Vence o maior dos dois; empate acrescenta um `log n`."},
  {"table": {"head": ["Caso", "Quando", "Resultado"], "rows": [["**1 — a folha domina**", "`f(n)` cresce menos que `n^log_b(a)`", "`T(n) = Θ(n^log_b(a))`"], ["**2 — empate**", "`f(n) = Θ(n^log_b(a))`", "`T(n) = Θ(n^log_b(a) · log n)`"], ["**3 — a raiz domina**", "`f(n)` cresce mais que `n^log_b(a)`", "`T(n) = Θ(f(n))`"]]}},
  {"callout": {"tipo": "nota", "titulo": "Por que `log n` aparece do nada", "texto": "Dividir por `b` até chegar a 1 leva `log_b(n)` passos. Todo `log` numa análise de complexidade vem daí — de uma quantidade que se divide, nunca de uma que se subtrai."}},
  {"h2": "As quatro formas que aparecem no código real"},
  {"p": "Quase tudo o que se escreve cai numa destas quatro. A coluna da direita é o que o `dataforge big-o` responde:"},
  {"table": {"head": ["Forma", "a, b", "Recorrência", "Classe"], "rows": [["busca binária", "1, 2", "`T(n) = T(n/2) + O(1)`", "`O(log n)`"], ["merge sort", "2, 2", "`T(n) = 2T(n/2) + O(n)`", "`O(n log n)`"], ["percorrer uma árvore", "2, 2", "`T(n) = 2T(n/2) + O(1)`", "`O(n)`"], ["fibonacci ingênuo", "2, —", "`T(n) = T(n-1) + T(n-2) + O(1)`", "`O(2^n)`"]]}},
  {"p": "A última linha é a que não tem `b`: a entrada **diminui de um em um** em vez de se dividir. É a diferença inteira entre um algoritmo que serve e um que não termina."},
  {"h2": "Uma chamada, entrada pela metade — `O(log n)`"},
  { code: `action busca(xs, alvo, baixo, alto):
    given baixo bigger alto:
        yield -1
    meio := (baixo + alto) ~/ 2
    given xs[meio] is alvo:
        yield meio
    given xs[meio] smaller alvo:
        yield busca(xs, alvo, meio + 1, alto)
    yield busca(xs, alvo, baixo, meio - 1)

out busca([1, 3, 5, 7, 9], 9, 0, 4)     // 4`, lang: 'df' },
  {"p": "Há **duas** chamadas escritas, e só **uma** roda: elas estão em ramos mutuamente exclusivos. Contá-las como duas é o erro que transforma uma busca binária em `O(2^n)` — a análise tem de olhar o caminho, e não a árvore."},
  { code: `$ dataforge big-o busca.df -v

  ● busca                      O(log n)    tempo   O(n) espaco`, lang: 'bash' },
  {"h2": "Duas chamadas sobre metades — `O(n log n)`"},
  {"p": "O merge sort é o caso 2 do teorema: `n^log₂(2) = n`, e a intercalação também é `O(n)`. Empate, e o resultado ganha o `log n`."},
  { code: `action intercalar(a, b):
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

action ordenar(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    yield intercalar(ordenar(xs[0:meio]), ordenar(xs[meio:]))

out ordenar([5, 2, 9, 1, 7])     // [1, 2, 5, 7, 9]`, lang: 'df' },
  {"p": "A conta por níveis deixa isso visível: no topo, um trabalho de `n`; no nível seguinte, dois de `n/2` — que somam `n` de novo; e assim por `log n` níveis. **Cada nível custa `n`**, e são `log n` deles."},
  { code: `nivel 0:                    n            = n
nivel 1:        n/2   +   n/2            = n
nivel 2:   n/4 + n/4 + n/4 + n/4         = n
   …                                       …
             log n niveis  ×  n  =  n log n`, lang: 'text' },
  {"h2": "Duas chamadas, entrada quase inteira — `O(2^n)`"},
  { code: `action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

out fib(12)     // 144`, lang: 'df' },
  {"p": "A forma é **idêntica** à do merge sort: duas chamadas por nível. O que muda é o `b`: aqui a entrada perde **um**, e não metade. A árvore de chamadas tem profundidade `n` em vez de `log n`, e cada nível dobra."},
  {"callout": {"tipo": "atencao", "titulo": "A diferença cabe num caractere", "texto": "`fib(n - 1)` e `ordenar(xs[0:meio])` são a mesma linha com um argumento diferente, e separam `O(2^n)` de `O(n log n)`. Com n = 50: um termina antes de você soltar a tecla, o outro leva mais de dez dias."}},
  {"h2": "Memoizar muda a recorrência, não o código"},
  {"p": "O fibonacci ingênuo recalcula `fib(30)` milhões de vezes. Guardando o que já foi calculado, cada argumento distinto roda **uma vez** — e a recorrência deixa de ser exponencial:"},
  { code: `cache := {}

action fib_memo(n):
    given n smaller 2:
        yield n
    given cache.has(str(n)):
        yield cache[str(n)]
    valor := fib_memo(n - 1) + fib_memo(n - 2)
    cache[str(n)] := valor
    yield valor

out fib_memo(30)     // 832040`, lang: 'df' },
  {"p": "São `n` argumentos possíveis e trabalho constante em cada um: `O(n)` de tempo, `O(n)` de espaço. O `dataforge big-o` reconhece o par que caracteriza o cache — a consulta que devolve cedo, e a escrita na mesma coleção — e para de acusar exponencial."},
  {"p": "`Arcane.Functional.memoize` faz o mesmo sem o cache à mão, e `Arcane.Iter.cache_info` diz quantas vezes ele acertou."},
  {"h2": "Quando o Teorema Mestre não se aplica"},
  {"list": ["**As partes são desiguais** — `T(n) = T(n/3) + T(2n/3) + O(n)` não tem um `b` único. (O resultado ainda é `O(n log n)`, por outro caminho.)", "**`a` ou `b` mudam com `n`** — o teorema pressupõe os dois constantes.", "**A diferença entre `f(n)` e `n^log_b(a)` não é polinomial** — é a lacuna entre os casos 2 e 3, e ela existe de verdade.", "**A recursão é indireta** — `f` chama `g`, que chama `f`. Aqui a análise do DataForge cala, porque olha uma ação por vez."]},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/classes", "title": "As classes", "desc": "de O(1) a O(n!), com um exemplo que roda de cada uma"}, {"href": "/docs/big-o/amortizada", "title": "Análise amortizada", "desc": "por que 'append' é O(1) mesmo custando O(n) de vez em quando"}, {"href": "/docs/big-o/limites", "title": "Limites inferiores", "desc": "Ω, Θ, e por que nenhuma ordenação por comparação vence n log n"}]},
];

const headings = [{ id: 'os-tres-casos-do-teorema-mestre', text: "Os três casos do Teorema Mestre", level: 2 as const }, { id: 'as-quatro-formas-que-aparecem-no-codigo-real', text: "As quatro formas que aparecem no código real", level: 2 as const }, { id: 'uma-chamada-entrada-pela-metade-olog-n', text: "Uma chamada, entrada pela metade — `O(log n)`", level: 2 as const }, { id: 'duas-chamadas-sobre-metades-on-log-n', text: "Duas chamadas sobre metades — `O(n log n)`", level: 2 as const }, { id: 'duas-chamadas-entrada-quase-inteira-o2n', text: "Duas chamadas, entrada quase inteira — `O(2^n)`", level: 2 as const }, { id: 'memoizar-muda-a-recorrencia-nao-o-codigo', text: "Memoizar muda a recorrência, não o código", level: 2 as const }, { id: 'quando-o-teorema-mestre-nao-se-aplica', text: "Quando o Teorema Mestre não se aplica", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Recorrências e o Teorema Mestre"}
      description={"Como se resolve o custo de um algoritmo que chama a si mesmo — e por que o merge sort e o fibonacci ingênuo têm a mesma forma e custos opostos."}
      href={"/docs/big-o/recorrencias"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
