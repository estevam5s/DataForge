import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Polimorfismo",
  description: "O mesmo nome, comportamentos diferentes — e por que isso elimina o if gigante.",
};

const blocos: Bloco[] = [
  {"p": "Polimorfismo é **um nome, várias implementações**, escolhidas pelo tipo do objeto. O que ele resolve, na prática: o `if` gigante que cresce a cada tipo novo."},
  {"h2": "O problema"},
  { code: `// Sem polimorfismo: cada forma nova mexe nesta função
action area(forma):
    match forma["tipo"]:
        point "circulo":
            yield 3.14159 * forma["raio"] ** 2
        point "quadrado":
            yield forma["lado"] ** 2
        default:
            trigger "forma desconhecida"

assert area({"tipo": "quadrado", "lado": 3}) is 9`, lang: 'df' },
  {"p": "Acrescentar um triângulo obriga a mexer aqui — e em toda outra função que faça esse `match`. Perímetro, desenhar, serializar: cada uma tem o seu."},
  {"h2": "A solução"},
  { code: `trait Forma:
    action area()
    action perimetro()

blueprint Circulo(raio) with Forma:
    action area():
        yield 3.14159 * self.raio ** 2
    action perimetro():
        yield 2 * 3.14159 * self.raio

blueprint Quadrado(lado) with Forma:
    action area():
        yield self.lado ** 2
    action perimetro():
        yield 4 * self.lado

// esta função nunca mais muda
action area_total(formas):
    total := 0.0
    cycle f in formas:
        total += f.area()
    yield total

assert area_total([spawn Quadrado(3), spawn Quadrado(4)]) is 25.0`, lang: 'df' },
  {"p": "Um triângulo novo é um arquivo novo. Nada do que já existe muda — é o [princípio aberto/fechado](/docs/oop/solid) em ação."},
  {"h2": "Sobrescrita (override)"},
  {"p": "O herdeiro redefine um método da mãe. `root` chama a versão dela:"},
  { code: `blueprint Animal:
    action setup(nome):
        self.nome := nome

    action falar():
        yield $"{self.nome} faz algum som"

blueprint Cachorro extends Animal:
    action falar():
        yield $"{self.nome} late"

blueprint Filhote extends Cachorro:
    action falar():
        yield root.falar() + " baixinho"

assert (spawn Animal("bicho")).falar() is "bicho faz algum som"
assert (spawn Cachorro("Rex")).falar() is "Rex late"
assert (spawn Filhote("Pip")).falar() is "Pip late baixinho"`, lang: 'df' },
  {"h2": "Sobrecarga (overload)"},
  {"p": "DataForge **não tem** sobrecarga por assinatura — dois métodos com o mesmo nome e parâmetros diferentes. O motivo: numa linguagem dinâmica não há tipo em tempo de compilação para escolher qual chamar."},
  {"p": "O que existe no lugar, e resolve os mesmos casos:"},
  { code: `blueprint Registro:
    // valores padrão cobrem o caso de "menos argumentos"
    action registrar(mensagem, nivel := "info", quando := void):
        marca := quando ?? "agora"
        yield $"[{nivel}] {marca}: {mensagem}"

r := spawn Registro()
assert r.registrar("oi") is "[info] agora: oi"
assert r.registrar("erro", "grave") is "[grave] agora: erro"`, lang: 'df' },
  { code: `// e 'match' cobre o caso de "tipos diferentes"
action descrever(x):
    match x:
        point Integer as n:
            yield $"inteiro {n}"
        point String as s:
            yield $"texto de {len(s)} letras"
        point [a, b]:
            yield "par"
        default:
            yield "outro"

assert descrever(42) is "inteiro 42"
assert descrever("oi") is "texto de 2 letras"
assert descrever([1, 2]) is "par"`, lang: 'df' },
  {"h2": "Upcasting e downcasting"},
  {"p": "Tratar um `Cachorro` como `Animal` é upcasting — sempre seguro, e é o que o polimorfismo faz o tempo todo. O caminho de volta precisa de verificação:"},
  { code: `blueprint Animal:
    action setup(nome):
        self.nome := nome

blueprint Cachorro extends Animal:
    action buscar():
        yield $"{self.nome} busca a bolinha"

action interagir(a):
    // 'linhagem' diz de que blueprints o objeto descende
    given "Cachorro" in linhagem(a):
        yield a.buscar()
    yield $"{a.nome} não busca nada"

assert interagir(spawn Cachorro("Rex")) is "Rex busca a bolinha"
assert interagir(spawn Animal("bicho")) is "bicho não busca nada"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Downcasting é sinal de alerta", "texto": "Perguntar o tipo para decidir o que fazer costuma significar que falta um método no trait. Antes de escrever o `given`, pergunte se `buscar()` não deveria existir em `Animal` sem fazer nada."}},
  {"h2": "Tempo de compilação e tempo de execução"},
  {"p": "Em linguagens estáticas, sobrecarga é resolvida na compilação e sobrescrita na execução. Em DataForge **tudo é na execução** — o método vem do objeto real, sempre:"},
  { code: `blueprint A:
    action quem():
        yield "A"

blueprint B extends A:
    action quem():
        yield "B"

action perguntar(x):
    yield x.quem()

// a função não sabe o tipo; o objeto decide
assert perguntar(spawn A()) is "A"
assert perguntar(spawn B()) is "B"`, lang: 'df' },
  {"p": "É mais flexível e mais lento — a busca do método acontece a cada chamada. Ver [análise estática](/docs/tecnicas/analise-estatica)."},
];

const headings = [{ id: 'o-problema', text: "O problema", level: 2 as const }, { id: 'a-solucao', text: "A solução", level: 2 as const }, { id: 'sobrescrita-override', text: "Sobrescrita (override)", level: 2 as const }, { id: 'sobrecarga-overload', text: "Sobrecarga (overload)", level: 2 as const }, { id: 'upcasting-e-downcasting', text: "Upcasting e downcasting", level: 2 as const }, { id: 'tempo-de-compilacao-e-tempo-de-execucao', text: "Tempo de compilação e tempo de execução", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Polimorfismo"}
      description={"O mesmo nome, comportamentos diferentes — e por que isso elimina o if gigante."}
      href={"/docs/oop/polimorfismo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
