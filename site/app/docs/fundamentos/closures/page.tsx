import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Closures e lambdas",
  description: "Ações como valores: alta ordem, closures, lambdas e composição.",
};

const blocos: Bloco[] = [
  {"h2": "Ações são valores"},
  {"p": "Uma ação pode ser guardada numa variável, passada como argumento e devolvida por outra ação:"},
  { code: `action dobro(x):
    yield x * 2

f := dobro                       # guardada
out f(21)                        # 42
out [1, 2, 3].map(dobro)         # passada` },
  {"h2": "Alta ordem"},
  { code: `action aplicar_duas_vezes(fn, valor):
    yield fn(fn(valor))

out aplicar_duas_vezes(dobro, 5)     # 20` },
  {"h2": "Closures"},
  {"p": "Uma ação aninhada **lembra** o escopo onde foi criada:"},
  { code: `action fabrica_somador(n):
    action somador(x):
        yield x + n          # 'n' vem do escopo de fora
    yield somador

soma10 := fabrica_somador(10)
out soma10(5)                  # 15
out fabrica_somador(3)(4)      # 7 — chamada encadeada` },
  {"h3": "Estado que persiste"},
  { code: `action criar_contador(inicio := 0):
    estado := {"valor": inicio}
    action proximo():
        estado["valor"] := estado["valor"] + 1
        yield estado["valor"]
    yield proximo

c1 := criar_contador()
c2 := criar_contador(100)

out c1(), c1(), c1()     # 1 2 3
out c2(), c2()           # 101 102` },
  {"p": "Cada chamada de `criar_contador` produz um contador com **estado próprio**. É o padrão de encapsulamento sem classe."},
  {"h2": "Lambdas"},
  {"p": "Três grafias, todas equivalentes:"},
  { code: `quadrado := lambda x: x * x
soma := lambda a, b => a + b
constante := lambda: 42

out quadrado(7), soma(3, 4), constante()` },
  {"p": "Com anotação de tipo, os parênteses são obrigatórios — sem eles, `:` iniciaria o corpo:"},
  { code: `lambda (n: Integer): n + 1` },
  {"h3": "Onde usam-se"},
  { code: `out [1, 2, 3].map(lambda n: n * n)
out [1, 2, 3, 4].filter(lambda n: n % 2 is 0)
out [1, 2, 3].reduce(lambda a, b: a + b, 0)
out Col.sort_by(itens, lambda i: -i["preco"])` },
  {"p": "Para lógica de mais de uma linha, prefira uma ação nomeada: ela pode ser testada isoladamente e o nome documenta a intenção."},
  {"h2": "Composição"},
  { code: `action mais_um(x):
    yield x + 1

action dobrar(x):
    yield x * 2

composta := compose(dobrar, mais_um)     # direita para esquerda
encadeada := pipe_fn(mais_um, dobrar)    # esquerda para direita

out composta(5), encadeada(5)            # 12 12` },
  {"h2": "Aplicação parcial"},
  { code: `action multiplicar(a, b):
    yield a * b

triplicar := partial(multiplicar, 3)
out triplicar(7)                     # 21
out [1, 2, 3].map(triplicar)         # [3, 6, 9]` },
  {"h2": "Memoização"},
  { code: `cache := {}

action fib(n):
    given n smaller 2:
        yield n
    given cache.has(str(n)):
        yield cache[str(n)]
    valor := fib(n - 1) + fib(n - 2)
    cache[str(n)] := valor
    yield valor

out fib(30)     # instantâneo — sem cache seriam milhões de chamadas` },
  {"p": "A biblioteca também traz `memoize` pronto em [Arcane.Functional](/docs/biblioteca/functional)."},
];

const headings = [{ id: 'acoes-sao-valores', text: "Ações são valores", level: 2 as const }, { id: 'alta-ordem', text: "Alta ordem", level: 2 as const }, { id: 'closures', text: "Closures", level: 2 as const }, { id: 'estado-que-persiste', text: "Estado que persiste", level: 3 as const }, { id: 'lambdas', text: "Lambdas", level: 2 as const }, { id: 'onde-usam-se', text: "Onde usam-se", level: 3 as const }, { id: 'composicao', text: "Composição", level: 2 as const }, { id: 'aplicacao-parcial', text: "Aplicação parcial", level: 2 as const }, { id: 'memoizacao', text: "Memoização", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Closures e lambdas"}
      description={"Ações como valores: alta ordem, closures, lambdas e composição."}
      href={"/docs/fundamentos/closures"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
