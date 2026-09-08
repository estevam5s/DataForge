import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fundamentos",
  description: "Objeto, classe, instância, estado, identidade — e o que cada palavra significa em DataForge.",
};

const blocos: Bloco[] = [
  {"p": "Antes da sintaxe, o vocabulário. Cada termo abaixo tem um nome próprio em DataForge, e saber qual é qual poupa a maior parte da confusão."},
  {"h2": "O que é orientação a objetos"},
  {"p": "Um jeito de organizar programa juntando **dados** e o **comportamento** que age sobre eles. A alternativa — dados de um lado, funções de outro — funciona bem até o programa crescer; aí ninguém mais sabe quais funções podem mexer em quais dados."},
  {"p": "OOP responde isso pondo os dois no mesmo lugar e controlando quem entra."},
  {"h2": "Classe e instância"},
  {"p": "A **classe** é a forma; a **instância** é a peça. Em DataForge a classe é o `blueprint` — a planta — e a peça nasce com `spawn`:"},
  { code: `blueprint Conta:
    private saldo: Float := 0.0

    action setup(titular):
        self.titular := titular

    action depositar(valor):
        self.saldo += valor
        yield self.saldo

    get extrato():
        yield $"{self.titular}: {self.saldo}"

// a planta é uma; as peças são duas, e independentes
a := spawn Conta("Ana")
b := spawn Conta("Bia")
a.depositar(100)

assert a.extrato is "Ana: 100.0"
assert b.extrato is "Bia: 0.0"`, lang: 'df' },
  {"h2": "Estado, comportamento, identidade"},
  {"p": "Todo objeto tem três coisas, e elas se confundem com frequência:"},
  {"table": {"head": ["", "O que é", "Em DataForge"], "rows": [["**estado**", "os valores que ele guarda agora", "os campos: `self.saldo`"], ["**comportamento**", "o que ele sabe fazer", "os métodos: `action depositar`"], ["**identidade**", "o que faz ele ser ele, e não outro igual", "a referência — dois `spawn` dão dois objetos"]]}},
  {"p": "A identidade é o que separa `blueprint` de `record`. Duas contas com o mesmo saldo **não são a mesma conta**; dois pontos (1,2) **são o mesmo ponto**:"},
  { code: `record Ponto:
    x: Integer
    y: Integer

blueprint Caixa:
    action setup(n):
        self.n := n

// record: igualdade estrutural — o conteúdo decide
assert Ponto(1, 2) is Ponto(1, 2)

// blueprint: identidade — cada spawn é um objeto
assert (spawn Caixa(1)) isnt (spawn Caixa(1))`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "A pergunta que decide", "texto": "**Dois destes, com os mesmos valores, são a mesma coisa?** Se sim, é `record`. Se não, é `blueprint`. Essa pergunta resolve a maioria das dúvidas de modelagem."}},
  {"h2": "Atributos e métodos"},
  {"p": "Campos guardam; métodos agem. Ambos podem ser **de instância** (cada objeto tem o seu) ou **estáticos** (um só, da classe):"},
  { code: `blueprint Contador:
    static total: Integer := 0
    valor: Integer := 0

    action somar():
        self.valor += 1
        yield self.valor

    static action zerar():
        yield 0

a := spawn Contador()
b := spawn Contador()
a.somar()
a.somar()
b.somar()

assert a.valor is 2
assert b.valor is 1
assert Contador.zerar() is 0`, lang: 'df' },
  {"p": "Ver [métodos estáticos](/docs/oop/estaticos) para quando usar cada um."},
  {"h2": "Construtor"},
  {"p": "`setup` é o construtor: roda uma vez, no `spawn`, e é onde o objeto nasce válido. Há duas formas:"},
  { code: `// forma explícita
blueprint Retangulo:
    action setup(largura, altura):
        given largura smaller_eq 0 or altura smaller_eq 0:
            trigger "as medidas precisam ser positivas"
        self.largura := largura
        self.altura := altura

// forma inline — os parâmetros viram campos
blueprint Circulo(raio):
    action area():
        yield 3.14159 * self.raio ** 2

assert (spawn Retangulo(3, 4)) isnt void
assert round((spawn Circulo(1)).area(), 3) is 3.142`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Não há destrutor", "texto": "DataForge coleta memória sozinho. Para liberar um recurso — arquivo, conexão — use `defer` ou `with`, que rodam mesmo se algo falhar no meio."}},
  {"h2": "`self`"},
  {"p": "`self` é o objeto em que o método está rodando. **Escrever `x` em vez de `self.x` lê a variável do escopo externo** — é a armadilha mais comum de quem começa:"},
  { code: `valor := "de fora"

blueprint Errado:
    action setup():
        self.valor := "de dentro"

    action mostrar():
        yield valor          // lê o de FORA

blueprint Certo:
    action setup():
        self.valor := "de dentro"

    action mostrar():
        yield self.valor     // lê o campo

assert (spawn Errado()).mostrar() is "de fora"
assert (spawn Certo()).mostrar() is "de dentro"`, lang: 'df' },
  {"h2": "Modificadores de acesso"},
  {"p": "Três níveis, e eles valem de verdade — não por convenção de nome:"},
  {"table": {"head": ["", "Quem alcança"], "rows": [["(padrão)", "qualquer um"], ["`protected`", "o blueprint que declarou e seus herdeiros"], ["`private`", "só o blueprint que declarou — nem o herdeiro"]]}},
  {"p": "Ver [campos e visibilidade](/docs/oop/campos) e [encapsulamento](/docs/oop/encapsulamento)."},
];

const headings = [{ id: 'o-que-e-orientacao-a-objetos', text: "O que é orientação a objetos", level: 2 as const }, { id: 'classe-e-instancia', text: "Classe e instância", level: 2 as const }, { id: 'estado-comportamento-identidade', text: "Estado, comportamento, identidade", level: 2 as const }, { id: 'atributos-e-metodos', text: "Atributos e métodos", level: 2 as const }, { id: 'construtor', text: "Construtor", level: 2 as const }, { id: 'self', text: "`self`", level: 2 as const }, { id: 'modificadores-de-acesso', text: "Modificadores de acesso", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fundamentos"}
      description={"Objeto, classe, instância, estado, identidade — e o que cada palavra significa em DataForge."}
      href={"/docs/oop/fundamentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
