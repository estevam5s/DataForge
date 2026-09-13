// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "06 · Blueprints",
  description: "14 exercícios: campos, métodos, herança, traits e records.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 06`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[063](#063-blueprint-com-construtor)", "**Blueprint com construtor**", "modele um ponto no plano com campos e um metodo."], ["[064](#064-construtor-com-setup)", "**Construtor com setup**", "use o metodo setup como construtor tradicional."], ["[065](#065-estado-mutavel)", "**Estado mutavel**", "uma conta bancaria que muda de saldo."], ["[066](#066-heranca-com-extends)", "**Heranca com extends**", "especialize um blueprint reutilizando o pai."], ["[067](#067-root-super)", "**root (super)**", "chame a implementacao do pai a partir do filho."], ["[068](#068-traits-interfaces)", "**Traits (interfaces)**", "declare um contrato e implemente em dois blueprints."], ["[069](#069-polimorfismo)", "**Polimorfismo**", "calcule a area de formas diferentes pela mesma interface."], ["[070](#070-membros-estaticos)", "**Membros estaticos**", "conte quantas instancias foram criadas."], ["[071](#071-sobrecarga-de-operadores)", "**Sobrecarga de operadores**", "some e multiplique vetores com + e *."], ["[072](#072-composicao)", "**Composicao**", "um pedido composto por varios itens."], ["[073](#073-cadeia-de-heranca)", "**Cadeia de heranca**", "tres niveis de heranca e resolucao de metodos."], ["[074](#074-introspeccao)", "**Introspeccao**", "descubra campos, metodos e tipo de uma instancia."], ["[075](#075-padrao-singleton)", "**Padrao Singleton**", "garanta uma unica instancia de configuracao usando membro estatico."], ["[076](#076-padrao-observador)", "**Padrao Observador**", "notifique varios assinantes quando o estado mudar."]]}},
  {"h2": "063 · Blueprint com construtor"},
  {"p": "**Enunciado.** modele um ponto no plano com campos e um metodo."},
  { code: `blueprint Ponto(x, y):
    action distancia_origem():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action toString():
        yield "(" + str(self.x) + ", " + str(self.y) + ")"

p := spawn Ponto(3, 4)
out p, p.distancia_origem()

assert p.x is 3, "campo x"
assert p.y is 4, "campo y"
assert p.distancia_origem() is 5.0, "distancia"
assert str(p) is "(3, 4)", "toString"`, lang: 'df', title: `exercicios/06-blueprints/063_blueprint_basico.df` },
  {"h2": "064 · Construtor com setup"},
  {"p": "**Enunciado.** use o metodo setup como construtor tradicional."},
  { code: `blueprint Retangulo:
    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    action area():
        yield self.largura * self.altura

    action perimetro():
        yield 2 * (self.largura + self.altura)

r := spawn Retangulo(4, 6)
out "area:", r.area(), "perimetro:", r.perimetro()

assert r.area() is 24, "area"
assert r.perimetro() is 20, "perimetro"`, lang: 'df', title: `exercicios/06-blueprints/064_setup.df` },
  {"h2": "065 · Estado mutavel"},
  {"p": "**Enunciado.** uma conta bancaria que muda de saldo."},
  { code: `blueprint Conta(titular, saldo):
    action depositar(valor):
        self.saldo := self.saldo + valor
        yield self.saldo

    action sacar(valor):
        given valor bigger self.saldo:
            trigger "Saldo insuficiente"
        self.saldo := self.saldo - valor
        yield self.saldo

c := spawn Conta("Ana", 100)
c.depositar(50)
c.sacar(30)
out c.titular, "tem", c.saldo

assert c.saldo is 120, "saldo apos operacoes"

erro := no
monitor:
    c.sacar(9999)
handle e:
    erro := yes
assert erro is yes, "saque acima do saldo dispara"`, lang: 'df', title: `exercicios/06-blueprints/065_metodos_e_estado.df` },
  {"h2": "066 · Heranca com extends"},
  {"p": "**Enunciado.** especialize um blueprint reutilizando o pai."},
  { code: `blueprint Animal(nome):
    action falar():
        yield "..."

    action apresentar():
        yield self.nome + " diz " + self.falar()

blueprint Cachorro(nome) extends Animal:
    action falar():
        yield "Au au"

blueprint Gato(nome) extends Animal:
    action falar():
        yield "Miau"

bichos := [spawn Cachorro("Rex"), spawn Gato("Mia"), spawn Animal("X")]
cycle b in bichos:
    out b.apresentar()

assert bichos[0].apresentar() is "Rex diz Au au", "cachorro"
assert bichos[1].apresentar() is "Mia diz Miau", "gato"
assert bichos[2].falar() is "...", "animal generico"`, lang: 'df', title: `exercicios/06-blueprints/066_heranca.df` },
  {"h2": "067 · root (super)"},
  {"p": "**Enunciado.** chame a implementacao do pai a partir do filho."},
  { code: `blueprint Base(nome):
    action descrever():
        yield "Base:" + self.nome

blueprint Derivada(nome) extends Base:
    action descrever():
        yield "Derivada[" + root.descrever() + "]"

d := spawn Derivada("teste")
out d.descrever()

assert d.descrever() is "Derivada[Base:teste]", "root chama o pai"`, lang: 'df', title: `exercicios/06-blueprints/067_root.df` },
  {"h2": "068 · Traits (interfaces)"},
  {"p": "**Enunciado.** declare um contrato e implemente em dois blueprints."},
  { code: `trait Serializavel:
    action serializar()

trait Comparavel:
    action comparar(outro)

blueprint Produto(nome, preco) with Serializavel, Comparavel:
    action serializar():
        yield {"nome": self.nome, "preco": self.preco}

    action comparar(outro):
        yield self.preco - outro.preco

a := spawn Produto("Mouse", 80)
b := spawn Produto("Teclado", 200)

out a.serializar()
out "diferenca:", a.comparar(b)

assert a.serializar() is {"nome": "Mouse", "preco": 80}, "serializar"
assert a.comparar(b) is -120, "comparar"
assert has_method(a, "serializar") is yes, "implementa o trait"`, lang: 'df', title: `exercicios/06-blueprints/068_traits.df` },
  {"h2": "069 · Polimorfismo"},
  {"p": "**Enunciado.** calcule a area de formas diferentes pela mesma interface."},
  { code: `blueprint Forma:
    action area():
        yield 0

blueprint Quadrado(lado) extends Forma:
    action area():
        yield self.lado ** 2

blueprint Circulo(raio) extends Forma:
    action area():
        yield round(3.14159 * self.raio ** 2, 2)

blueprint Triangulo(base, altura) extends Forma:
    action area():
        yield self.base * self.altura / 2

formas := [spawn Quadrado(4), spawn Circulo(2), spawn Triangulo(6, 4)]
areas := []
cycle f in formas:
    areas.append(f.area())
    out typeof(f), "->", f.area()

assert areas is [16, 12.57, 12.0], "areas polimorficas"
assert typeof(formas[0]) is "Quadrado", "typeof devolve o blueprint"`, lang: 'df', title: `exercicios/06-blueprints/069_polimorfismo.df` },
  {"h2": "070 · Membros estaticos"},
  {"p": "**Enunciado.** conte quantas instancias foram criadas."},
  { code: `blueprint Registro(dado):
    static criados := 0

    action registrar():
        Registro.criados := Registro.criados + 1
        yield Registro.criados

assert Registro.criados is 0, "comeca em zero"
a := spawn Registro("x")
b := spawn Registro("y")
a.registrar()
b.registrar()
out "instancias registradas:", Registro.criados
assert Registro.criados is 2, "contador estatico compartilhado"`, lang: 'df', title: `exercicios/06-blueprints/070_estaticos.df` },
  {"h2": "071 · Sobrecarga de operadores"},
  {"p": "**Enunciado.** some e multiplique vetores com + e *."},
  { code: `blueprint Vetor(x, y):
    action add(outro):
        yield spawn Vetor(self.x + outro.x, self.y + outro.y)

    action mul(escalar):
        yield spawn Vetor(self.x * escalar, self.y * escalar)

    action toString():
        yield "<" + str(self.x) + ", " + str(self.y) + ">"

a := spawn Vetor(1, 2)
b := spawn Vetor(3, 4)

soma := a + b
escalado := a * 3

out soma, escalado
assert str(soma) is "<4, 6>", "soma de vetores"
assert str(escalado) is "<3, 6>", "produto por escalar"`, lang: 'df', title: `exercicios/06-blueprints/071_sobrecarga_operadores.df` },
  {"h2": "072 · Composicao"},
  {"p": "**Enunciado.** um pedido composto por varios itens."},
  { code: `blueprint Item(nome, preco, qtd):
    action subtotal():
        yield self.preco * self.qtd

blueprint Pedido(cliente):
    action setup(cliente):
        self.cliente := cliente
        self.itens := []

    action adicionar(item):
        self.itens.append(item)
        yield len(self.itens)

    action total():
        soma := 0
        cycle i in self.itens:
            soma += i.subtotal()
        yield soma

p := spawn Pedido("Ana")
p.adicionar(spawn Item("Mouse", 80, 2))
p.adicionar(spawn Item("Teclado", 200, 1))

out p.cliente, "->", len(p.itens), "itens, total R$", p.total()
assert len(p.itens) is 2, "dois itens"
assert p.total() is 360, "total do pedido"`, lang: 'df', title: `exercicios/06-blueprints/072_composicao.df` },
  {"h2": "073 · Cadeia de heranca"},
  {"p": "**Enunciado.** tres niveis de heranca e resolucao de metodos."},
  { code: `blueprint A:
    action quem():
        yield "A"
    action so_de_a():
        yield "metodo de A"

blueprint B extends A:
    action quem():
        yield "B"

blueprint C extends B:
    action quem():
        yield "C"

c := spawn C()
out c.quem(), c.so_de_a()

assert c.quem() is "C", "o mais especifico vence"
assert c.so_de_a() is "metodo de A", "herda do avo"
assert class_name(c) is "C", "class_name"`, lang: 'df', title: `exercicios/06-blueprints/073_heranca_profunda.df` },
  {"h2": "074 · Introspeccao"},
  {"p": "**Enunciado.** descubra campos, metodos e tipo de uma instancia."},
  { code: `blueprint Usuario(nome, email):
    action ativar():
        self.ativo := yes
        yield self.ativo

u := spawn Usuario("Ana", "ana@x.com")
u.ativar()

out "campos:  ", get_fields(u)
out "metodos: ", get_methods(u)
out "tipo:    ", typeof(u)

assert has_field(u, "nome") is yes, "tem campo nome"
assert has_field(u, "senha") is no, "nao tem campo senha"
assert has_method(u, "ativar") is yes, "tem metodo ativar"
assert u.ativo is yes, "campo criado em tempo de execucao"`, lang: 'df', title: `exercicios/06-blueprints/074_introspeccao.df` },
  {"h2": "075 · Padrao Singleton"},
  {"p": "**Enunciado.** garanta uma unica instancia de configuracao usando membro estatico."},
  { code: `blueprint Config:
    static instancia := void

    action setup():
        self.valores := {"tema": "escuro"}

action config_unica():
    given Config.instancia is void:
        Config.instancia := spawn Config()
    yield Config.instancia

a := config_unica()
b := config_unica()
a.valores["tema"] := "claro"

out b.valores
assert b.valores["tema"] is "claro", "a e b sao a mesma instancia"
assert Config.instancia isnt void, "a instancia ficou guardada no estatico"`, lang: 'df', title: `exercicios/06-blueprints/075_padrao_singleton.df` },
  {"h2": "076 · Padrao Observador"},
  {"p": "**Enunciado.** notifique varios assinantes quando o estado mudar."},
  { code: `blueprint Assunto:
    action setup():
        self.assinantes := []
        self.estado := 0

    action assinar(fn):
        self.assinantes.append(fn)
        yield len(self.assinantes)

    action definir(valor):
        self.estado := valor
        cycle fn in self.assinantes:
            fn(valor)
        yield valor

recebidos := []
s := spawn Assunto()
s.assinar(lambda v: recebidos.append("A:" + str(v)))
s.assinar(lambda v: recebidos.append("B:" + str(v)))
s.definir(7)
s.definir(9)

out recebidos
assert recebidos is ["A:7", "B:7", "A:9", "B:9"], "todos os assinantes receberam"`, lang: 'df', title: `exercicios/06-blueprints/076_padrao_observador.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/06-blueprints/063_blueprint_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '063-blueprint-com-construtor', text: "063 · Blueprint com construtor", level: 2 as const }, { id: '064-construtor-com-setup', text: "064 · Construtor com setup", level: 2 as const }, { id: '065-estado-mutavel', text: "065 · Estado mutavel", level: 2 as const }, { id: '066-heranca-com-extends', text: "066 · Heranca com extends", level: 2 as const }, { id: '067-root-super', text: "067 · root (super)", level: 2 as const }, { id: '068-traits-interfaces', text: "068 · Traits (interfaces)", level: 2 as const }, { id: '069-polimorfismo', text: "069 · Polimorfismo", level: 2 as const }, { id: '070-membros-estaticos', text: "070 · Membros estaticos", level: 2 as const }, { id: '071-sobrecarga-de-operadores', text: "071 · Sobrecarga de operadores", level: 2 as const }, { id: '072-composicao', text: "072 · Composicao", level: 2 as const }, { id: '073-cadeia-de-heranca', text: "073 · Cadeia de heranca", level: 2 as const }, { id: '074-introspeccao', text: "074 · Introspeccao", level: 2 as const }, { id: '075-padrao-singleton', text: "075 · Padrao Singleton", level: 2 as const }, { id: '076-padrao-observador', text: "076 · Padrao Observador", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"06 · Blueprints"}
      description={"14 exercícios: campos, métodos, herança, traits e records."}
      href={"/docs/exercicios/06-blueprints"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
