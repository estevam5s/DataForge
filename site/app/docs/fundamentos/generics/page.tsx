import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Generics",
  description: "Uma estrutura que serve para qualquer tipo.",
};

const blocos: Bloco[] = [
  {"p": "Um genérico é uma estrutura que serve para qualquer tipo. `Pilha<T>` é uma pilha de qualquer coisa — e o `<T>` documenta que **o que entra é o que sai**."},
  {"h2": "A forma"},
  { code: `blueprint Pilha<T>:
    itens: Cluster := []

    action por(x: T):
        self.itens.append(x)

    action tirar() -> T:
        yield self.itens.pop()

// a mesma estrutura, tipos diferentes
numeros := spawn Pilha()
numeros.por(1)
numeros.por(2)
out numeros.tirar()          // 2

textos := spawn Pilha()
textos.por("a")
out textos.tirar()           // a` },
  {"h2": "Em ações"},
  { code: `action primeiro<T>(lista: Cluster) -> T:
    yield lista[0]

out primeiro([1, 2, 3])      // 1
out primeiro(["a", "b"])     // a` },
  {"p": "O `<T>` diz que o retorno é do mesmo tipo dos itens da lista. É uma afirmação sobre a **relação** entre entrada e saída, que o nome do tipo sozinho não conseguiria fazer."},
  {"h2": "Mais de um parâmetro"},
  { code: `blueprint Par<K, V>(chave, valor):
    action get_chave() -> K:
        yield self.chave

    action get_valor() -> V:
        yield self.valor

par := spawn Par("idade", 42)
out par.get_chave(), "=", par.get_valor()   // idade = 42` },
  {"p": "A convenção é `T` para um tipo qualquer, `K`/`V` para chave e valor, `E` para elemento. Não é regra — qualquer nome que comece com maiúscula serve."},
  {"h2": "O que o `<T>` faz, e o que não faz"},
  {"table": {"head": ["", "Acontece?"], "rows": [["o analisador estático aceita `T` como tipo dentro da declaração", "**sim**"], ["o `<T>` do blueprint vale nos métodos dele", "**sim**"], ["`T` fora da declaração que o criou", "**erro** — ele não vaza"], ["verificar em tempo de execução que os dois `T` batem", "**não**"], ["`<T extends Comparable>`", "**ainda não** — veja o [roadmap](/docs/roadmap)"]]}},
  {"p": "A linguagem é de tipagem dinâmica: o parâmetro de tipo documenta e é aceito pelo analisador, mas não é verificado quando o programa roda. É o mesmo que o TypeScript faz ao compilar — os tipos somem, e o que fica é a documentação mais o que o analisador conseguiu provar."},
  {"h2": "O que continua sendo verificado"},
  { code: `action f(x: Integer):
    yield x

f("texto")
// erro: parameter 'x' of action 'f' declared as Integer but got String` },
  {"p": "Um tipo concreto continua sendo cobrado, em tempo de execução e na análise estática. O genérico não é uma porta para qualquer nome passar: `action f(x: NaoExiste)` segue sendo erro."},
  {"h2": "`<` de genérico e `<` de comparação"},
  { code: `blueprint Caixa<T>:      // genérico
    action f():
        yield 1

a := 3
b := 5
out a < b                // comparação — segue funcionando` },
  {"p": "O parser distingue pelo que vem depois: `<` seguido de um **nome de tipo** (maiúscula) e um `>` fechando abre um genérico; qualquer outra coisa é comparação. `Total < Limite`, com os dois em maiúscula, ainda é comparação — porque falta o `>` fechando."},
  {"h2": "Um caso completo"},
  { code: `blueprint Resultado<T, E>(valor, erro):
    action ok() -> Boolean:
        yield self.erro is void

    action pegar() -> T:
        given not self.ok():
            trigger "resultado com erro: " + str(self.erro)
        yield self.valor

    action erro_ou<F>(padrao: F) -> F:
        yield self.erro ?? padrao

action dividir(a, b) -> Resultado:
    given b is 0:
        yield spawn Resultado(void, "divisão por zero")
    yield spawn Resultado(a / b, void)

r := dividir(10, 2)
out r.ok(), r.pegar()                    // yes 5.0

ruim := dividir(1, 0)
out ruim.ok(), ruim.erro_ou("sem erro")  // no divisão por zero` },
  {"p": "Um `Resultado<T, E>` é o padrão que Rust chama de `Result` e Haskell de `Either`: o valor **ou** o erro, sem exceção no meio. O genérico é o que permite escrevê-lo uma vez e usá-lo em qualquer lugar."},
  {"h2": "Comparado ao que você conhece"},
  {"table": {"head": ["", "DataForge", "TypeScript", "Java"], "rows": [["classe", "`blueprint Pilha<T>`", "`class Pilha<T>`", "`class Pilha<T>`"], ["função", "`action primeiro<T>()`", "`function primeiro<T>()`", "`<T> T primeiro()`"], ["dois parâmetros", "`<K, V>`", "`<K, V>`", "`<K, V>`"], ["verificado em execução", "não", "não", "não (apagamento)"], ["restrição", "**ainda não**", "`<T extends X>`", "`<T extends X>`"]]}},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'em-acoes', text: "Em ações", level: 2 as const }, { id: 'mais-de-um-parametro', text: "Mais de um parâmetro", level: 2 as const }, { id: 'o-que-o-t-faz-e-o-que-nao-faz', text: "O que o `<T>` faz, e o que não faz", level: 2 as const }, { id: 'o-que-continua-sendo-verificado', text: "O que continua sendo verificado", level: 2 as const }, { id: 'de-generico-e--de-comparacao', text: "`<` de genérico e `<` de comparação", level: 2 as const }, { id: 'um-caso-completo', text: "Um caso completo", level: 2 as const }, { id: 'comparado-ao-que-voce-conhece', text: "Comparado ao que você conhece", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Generics"}
      description={"Uma estrutura que serve para qualquer tipo."}
      href={"/docs/fundamentos/generics"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
