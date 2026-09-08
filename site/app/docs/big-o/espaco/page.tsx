import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Complexidade de espaço",
  description: "Trocar tempo por memória, e quando isso não vale.",
};

const blocos: Bloco[] = [
  {"p": "Tempo não é o único recurso. `dataforge big-o` reporta os dois:"},
  { code: `  ● dobrar                   O(n)        tempo   O(n) espaco
  ● somar                    O(n)        tempo   O(1) espaco`, lang: 'text' },
  {"h2": "O que conta como espaço"},
  {"p": "Só a memória **adicional** que o algoritmo pede — a entrada não conta, porque ela já existia."},
  { code: `// O(1) de espaço: uma variável, não importa o tamanho de xs
action somar(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

// O(n) de espaço: a saída cresce com a entrada
action dobrar(xs):
    saida := []
    cycle x in xs:
        saida.append(x * 2)
    yield saida

assert somar([1, 2, 3]) is 6
assert dobrar([1, 2]) is [2, 4]`, lang: 'df' },
  {"h2": "A pilha também é memória"},
  {"p": "Cada chamada recursiva ocupa um quadro. Uma recursão de profundidade n custa O(n) de espaço mesmo sem alocar nada:"},
  { code: `// O(n) de espaço — n quadros de pilha
action soma_recursiva(n):
    given n smaller_eq 0:
        yield 0
    yield n + soma_recursiva(n - 1)

// O(1) de espaço — um laço não empilha
action soma_iterativa(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

assert soma_recursiva(100) is soma_iterativa(100)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Recursão profunda estoura", "texto": "`StackOverflowError` (DF0801) aparece por volta de mil níveis. Para profundidade grande, reescreva como laço."}},
  {"h2": "A troca"},
  {"p": "O padrão que mais aparece: gastar O(n) de memória para derrubar O(n²) para O(n)."},
  {"table": {"head": ["", "Tempo", "Espaço"], "rows": [["busca linear em laço", "O(n²)", "O(1)"], ["índice em vault", "**O(n)**", "**O(n)**"], ["fibonacci ingênuo", "O(2ⁿ)", "O(n)"], ["fibonacci com memoização", "**O(n)**", "**O(n)**"]]}},
  {"p": "Quase sempre vale. As exceções:"},
  {"list": ["**A entrada não cabe na memória.** Aí o algoritmo O(1) de espaço é o único possível, e processa-se em fluxo.", "**A memória é o gargalo.** Num contêiner com limite apertado, estourar a memória derruba o processo — enquanto ser lento só irrita.", "**O índice é usado uma vez só.** Construir um vault para uma consulta única custa mais que a busca linear."]},
  {"h2": "Trabalhar em fluxo"},
  {"p": "Generators processam sem materializar. Um arquivo de dez milhões de linhas cabe em O(1) de memória:"},
  { code: `stream action pares(xs):
    cycle x in xs:
        given x % 2 is 0:
            emit x

// O(1) de espaço: um item por vez, e só os 3 primeiros são calculados
out pares(range(1000000)).take(3)`, lang: 'df' },
  {"p": "Comparado à compreensão, que aloca a lista inteira:"},
  { code: `// O(n) de espaço — materializa um milhão de itens
todos := [x cycle x in range(1000000) given x % 2 is 0]
out len(todos)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Preguiça é uma estratégia de memória", "texto": "`stream action` + `take(n)` é como processar mais dados do que cabem na RAM. Ver [generators](/docs/fundamentos/generators)."}},
];

const headings = [{ id: 'o-que-conta-como-espaco', text: "O que conta como espaço", level: 2 as const }, { id: 'a-pilha-tambem-e-memoria', text: "A pilha também é memória", level: 2 as const }, { id: 'a-troca', text: "A troca", level: 2 as const }, { id: 'trabalhar-em-fluxo', text: "Trabalhar em fluxo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Complexidade de espaço"}
      description={"Trocar tempo por memória, e quando isso não vale."}
      href={"/docs/big-o/espaco"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
