import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "21 · OOP avançado",
  description: "Campos, propriedades, operadores, visibilidade, abstratos e modelagem.",
};

const blocos: Bloco[] = [
  {"p": "Dez exercícios sobre o OOP do 4.1: campos declarados, estáticos, propriedades, visibilidade, sobrecarga de operadores, abstratos e contratos de trait."},
  { code: `python3 exercicios/run_all.py 21`, lang: 'bash' },
  {"p": "Cada um tem um `.md` ao lado explicando o conceito, comparando com outras linguagens e listando as armadilhas."},
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "O que ensina"], "rows": [["181", "**Campos declarados**", "Declare campos com tipo e padrao no corpo do blueprint"], ["182", "**Metodos estaticos**", "Crie metodos que pertencem ao blueprint, nao a instancia"], ["183", "**Propriedades com get e set**", "Exponha um valor calculado, e valide na atribuicao"], ["184", "**Visibilidade: private e protected**", "Proteja o estado interno de um objeto"], ["185", "**Sobrecarga de operadores**", "Faca '+' e '==' funcionarem no seu proprio tipo"], ["186", "**Blueprints abstratos e contratos de trait**", "Declare o que um tipo precisa ter, e deixe o compilador cobrar"], ["187", "**Heranca e 'root'**", "Estenda um comportamento sem reescrever o do pai"], ["188", "**Composicao no lugar de heranca**", "Monte comportamento juntando objetos, nao estendendo"], ["189", "**Quando usar record e quando usar blueprint**", "Compare os dois, e escolha pelo que o dado precisa"], ["190", "**Polimorfismo**", "Trate tipos diferentes pela interface comum"]]}},
  {"callout": {"tipo": "nota", "titulo": "A ordem importa", "texto": "181 a 185 são as ferramentas novas; 186 a 190 são as decisões de modelagem que elas permitem. Fazer 188 antes de 186 funciona, mas a discussão sobre herança e composição fica mais clara depois de ver o contrato de trait em ação."}},
  {"h2": "181 · Campos declarados"},
  {"p": "Declare campos com tipo e padrao no corpo do blueprint."},
  { code: `// Exercicio 181 — Campos declarados
// Enunciado: declare campos com tipo e padrao no corpo do blueprint.

// Antes do 4.1, todo campo nascia no setup. Declara-los no corpo diz o
// que o objeto tem antes de dizer como ele nasce — e o padrao evita o
// setup repetitivo.

blueprint Contador:
    valor: Integer := 0
    passo: Integer := 1

    action somar():
        self.valor += self.passo
        yield self.valor

c := spawn Contador()
out "comeca em:", c.valor
out "depois de somar:", c.somar()
assert c.valor is 1, "o campo declarado ja existe no spawn"

// Sem padrao, o campo nasce void
blueprint Pessoa:
    nome: String
    idade: Integer := 0

p := spawn Pessoa()
out "nome sem padrao:", p.nome
assert p.nome is void, "campo sem padrao comeca void"
assert p.idade is 0, "campo com padrao comeca com ele"

// Campos sao herdados
blueprint Funcionario extends Pessoa:
    salario: Float := 0.0

f := spawn Funcionario()
assert f.idade is 0, "o campo do pai foi herdado"
assert f.salario is 0.0, "e o proprio tambem existe"
out "ok"`, lang: 'df' },
  {"h2": "182 · Metodos estaticos"},
  {"p": "Crie metodos que pertencem ao blueprint, nao a instancia."},
  { code: `// Exercicio 182 — Metodos estaticos
// Enunciado: crie metodos que pertencem ao blueprint, nao a instancia.

// Um metodo estatico nao usa 'self'. Serve para o que e da familia toda:
// construtores alternativos, conversoes, constantes calculadas.

blueprint Temperatura:
    celsius: Float := 0.0

    static action de_fahrenheit(f):
        t := spawn Temperatura()
        t.celsius := (f - 32) * 5 / 9
        yield t

    static action congelamento():
        yield 0.0

    action em_fahrenheit():
        yield self.celsius * 9 / 5 + 32

// chamado no blueprint, sem instancia
gelo := Temperatura.de_fahrenheit(32)
assert round(gelo.celsius, 6) is 0.0, "32F sao 0C"
assert Temperatura.congelamento() is 0.0, "constante da familia"

// o metodo de instancia precisa de uma
t := spawn Temperatura()
t.celsius := 100
assert t.em_fahrenheit() is 212.0, "100C sao 212F"

// chamar metodo de instancia no blueprint da erro util
monitor:
    Temperatura.em_fahrenheit()
    assert no, "deveria ter recusado"
handle e:
    out "recusado, como esperado"
    assert e.message.contains("spawn"), "a mensagem diz o que fazer"

out "ok"`, lang: 'df' },
  {"h2": "183 · Propriedades com get e set"},
  {"p": "Exponha um valor calculado, e valide na atribuicao."},
  { code: `// Exercicio 183 — Propriedades com get e set
// Enunciado: exponha um valor calculado, e valide na atribuicao.

// Uma propriedade e lida como campo mas roda codigo. O ganho: dá para
// validar na escrita, e mudar a implementacao sem mexer em quem usa.

blueprint Retangulo:
    private _largura: Float := 1.0
    private _altura: Float := 1.0

    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    get largura():
        yield self._largura

    set largura(v):
        given v smaller_eq 0:
            trigger "largura precisa ser positiva"
        self._largura := v

    get altura():
        yield self._altura

    set altura(v):
        given v smaller_eq 0:
            trigger "altura precisa ser positiva"
        self._altura := v

    // so leitura: nao ha 'set area'
    get area():
        yield self._largura * self._altura

    get e_quadrado():
        yield self._largura is self._altura

r := spawn Retangulo(3, 4)
out "area:", r.area
assert r.area is 12.0, "area calculada na leitura"
assert not r.e_quadrado, "3x4 nao e quadrado"

// a atribuicao passa pelo setter
r.largura := 4
assert r.area is 16.0, "a area acompanhou"
assert r.e_quadrado, "agora e quadrado"

// e o setter valida
monitor:
    r.largura := -5
    assert no, "deveria ter recusado"
handle e:
    assert e.message.contains("positiva"), "a validacao rodou"

// propriedade so leitura recusa escrita
monitor:
    r.area := 100
    assert no, "deveria ter recusado"
handle e:
    assert e.message.contains("read-only"), "diz que falta o set"

out "ok"`, lang: 'df' },
  {"h2": "184 · Visibilidade: private e protected"},
  {"p": "Proteja o estado interno de um objeto."},
  { code: `// Exercicio 184 — Visibilidade: private e protected
// Enunciado: proteja o estado interno de um objeto.

// 'private' e visivel so dentro do blueprint. 'protected' alcanca
// tambem os herdeiros. O que fica publico e a promessa que voce
// mantem; o resto voce pode mudar sem avisar ninguem.

blueprint Conta:
    private saldo: Float := 0.0
    protected titular: String := ""

    action setup(titular):
        self.titular := titular

    action depositar(valor):
        given valor smaller_eq 0:
            trigger "deposito precisa ser positivo"
        self.saldo += valor
        yield self.saldo

    action sacar(valor):
        given valor bigger self.saldo:
            trigger "saldo insuficiente"
        self.saldo -= valor
        yield self.saldo

    get extrato():
        yield $"{self.titular}: {self.saldo}"

c := spawn Conta("Ana")
c.depositar(100)
c.sacar(30)
out c.extrato
assert c.extrato is "Ana: 70.0", "as operacoes publicas funcionam"

// de fora, o saldo nao se alcanca
monitor:
    out c.saldo
    assert no, "deveria ter recusado"
handle e:
    assert e.message.contains("private"), "diz que e private"
    out "saldo protegido"

// e nem se altera
monitor:
    c.saldo := 999999
    assert no, "deveria ter recusado"
handle e:
    out "nao da para forjar saldo"

// 'protected' alcanca o herdeiro
blueprint ContaPremium extends Conta:
    action saudacao():
        yield $"Bem-vinda, {self.titular}"

p := spawn ContaPremium("Bruna")
assert p.saudacao() is "Bem-vinda, Bruna", "protected alcanca o filho"

out "ok"`, lang: 'df' },
  {"h2": "185 · Sobrecarga de operadores"},
  {"p": "Faca '+' e '==' funcionarem no seu proprio tipo."},
  { code: `// Exercicio 185 — Sobrecarga de operadores
// Enunciado: faca '+' e '==' funcionarem no seu proprio tipo.

// Sobrecarregar operador so vale quando a operacao e obvia: somar dois
// vetores, comparar dois dinheiros. Se alguem precisa ler a
// documentacao para saber o que '+' faz, use um metodo com nome.

blueprint Vetor:
    x: Float := 0.0
    y: Float := 0.0

    action setup(x, y):
        self.x := x
        self.y := y

    operator + (o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)

    operator - (o):
        yield spawn Vetor(self.x - o.x, self.y - o.y)

    operator * (k):
        yield spawn Vetor(self.x * k, self.y * k)

    operator == (o):
        yield self.x is o.x and self.y is o.y

    get comprimento():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action toString():
        yield $"({self.x}, {self.y})"

a := spawn Vetor(1, 2)
b := spawn Vetor(3, 4)

out "a + b =", str(a + b)
assert (a + b).x is 4.0, "soma componente a componente"
assert (b - a).y is 2.0, "subtracao"
assert (a * 3).x is 3.0, "multiplicacao por escalar"

// igualdade estrutural, nao de identidade
assert a == spawn Vetor(1, 2), "dois vetores iguais sao =="
assert not (a == b), "vetores diferentes nao sao"

// '!=' sai de '==' negado, sem precisar declarar
assert a isnt b, "isnt deriva do =="

out "comprimento de (3,4):", b.comprimento
assert b.comprimento is 5.0, "3-4-5"

out "ok"`, lang: 'df' },
  {"h2": "186 · Blueprints abstratos e contratos de trait"},
  {"p": "Declare o que um tipo precisa ter, e deixe o compilador cobrar."},
  { code: `// Exercicio 186 — Blueprints abstratos e contratos de trait
// Enunciado: declare o que um tipo precisa ter, e deixe o compilador cobrar.

// Um blueprint abstrato nao pode ser spawnado: ele existe para ser
// herdado. Um metodo abstrato e uma exigencia — quem herdar precisa
// implementar, e o erro sai na declaracao, nao na chamada.

abstract blueprint Forma:
    abstract action area()

    // metodo concreto: os herdeiros ganham de graca
    action descrever():
        yield $"{self.nome()} com area {round(self.area(), 2)}"

    abstract action nome()

blueprint Quadrado extends Forma:
    lado: Float := 0.0

    action setup(lado):
        self.lado := lado

    action area():
        yield self.lado ** 2

    action nome():
        yield "quadrado"

blueprint Circulo extends Forma:
    raio: Float := 0.0

    action setup(raio):
        self.raio := raio

    action area():
        yield PI * self.raio ** 2

    action nome():
        yield "circulo"

formas := [spawn Quadrado(4), spawn Circulo(2)]
cycle f in formas:
    out f.descrever()

assert (spawn Quadrado(4)).area() is 16.0, "area do quadrado"

// o abstrato nao pode ser instanciado
monitor:
    spawn Forma()
    assert no, "deveria ter recusado"
handle e:
    assert e.message.contains("abstract"), "diz que e abstrato"
    out "abstrato nao se instancia"

// trait declara contrato
trait Comparavel:
    action comparar(outro)

blueprint Peso with Comparavel:
    kg: Float := 0.0
    action setup(kg):
        self.kg := kg
    action comparar(o):
        given self.kg smaller o.kg:
            yield -1
        given self.kg bigger o.kg:
            yield 1
        yield 0

assert (spawn Peso(1)).comparar(spawn Peso(2)) is -1, "o contrato foi cumprido"

out "ok"`, lang: 'df' },
  {"h2": "187 · Heranca e 'root'"},
  {"p": "Estenda um comportamento sem reescrever o do pai."},
  { code: `// Exercicio 187 — Heranca e 'root'
// Enunciado: estenda um comportamento sem reescrever o do pai.

// 'root' chama a versao do pai. Serve para acrescentar sem duplicar —
// e o que distingue estender de reimplementar.

blueprint Documento:
    titulo: String := ""
    action setup(titulo):
        self.titulo := titulo

    action cabecalho():
        yield $"# {self.titulo}"

    action render():
        yield self.cabecalho()

blueprint Artigo extends Documento:
    autor: String := ""

    action setup(titulo, autor):
        self.titulo := titulo
        self.autor := autor

    // acrescenta ao do pai, em vez de refazer
    action cabecalho():
        yield root.cabecalho() + $"\\npor {self.autor}"

a := spawn Artigo("Sobre pipelines", "Ana")
out a.render()
assert a.render().contains("# Sobre pipelines"), "o cabecalho do pai veio"
assert a.render().contains("por Ana"), "e o acrescimo tambem"

// 'render' foi herdado sem mudanca, e chama o 'cabecalho' do filho —
// e o polimorfismo funcionando
d := spawn Documento("Simples")
assert d.render() is "# Simples", "o pai continua o mesmo"

// 'final' impede sobrescrita: o erro sai na declaracao do herdeiro,
// nao quando alguem chama o metodo.
blueprint Base:
    final action identidade():
        yield "base"

assert (spawn Base()).identidade() is "base", "o final funciona normalmente"

out "ok"`, lang: 'df' },
  {"h2": "188 · Composicao no lugar de heranca"},
  {"p": "Monte comportamento juntando objetos, nao estendendo."},
  { code: `// Exercicio 188 — Composicao no lugar de heranca
// Enunciado: monte comportamento juntando objetos, nao estendendo.

// Heranca amarra o filho ao pai para sempre. Composicao troca a peca
// quando precisar. A regra pratica: heranca quando A *e* um B;
// composicao quando A *tem* um B.

trait Motor:
    action ligar()
    action potencia()

blueprint MotorEletrico with Motor:
    kw: Float := 0.0
    action setup(kw):
        self.kw := kw
    action ligar():
        yield "zumbido"
    action potencia():
        yield self.kw

blueprint MotorCombustao with Motor:
    cavalos: Float := 0.0
    action setup(cavalos):
        self.cavalos := cavalos
    action ligar():
        yield "ronco"
    action potencia():
        yield self.cavalos * 0.7355

blueprint Carro:
    modelo: String := ""

    action setup(modelo, motor):
        self.modelo := modelo
        self.motor := motor        // o carro TEM um motor

    action dar_partida():
        yield $"{self.modelo}: {self.motor.ligar()}"

    action ficha():
        yield $"{self.modelo} — {round(self.motor.potencia(), 1)} kW"

eletrico := spawn Carro("Modelo E", spawn MotorEletrico(150))
combustao := spawn Carro("Modelo C", spawn MotorCombustao(200))

out eletrico.dar_partida()
out combustao.dar_partida()
out eletrico.ficha()

assert eletrico.dar_partida().contains("zumbido"), "usou o motor eletrico"
assert combustao.dar_partida().contains("ronco"), "e o outro carro, o outro motor"
assert eletrico.ficha().contains("150"), "a potencia veio do motor"

// trocar o motor e trocar um campo — com heranca seria outro tipo
eletrico.motor := spawn MotorCombustao(100)
assert eletrico.dar_partida().contains("ronco"), "o mesmo carro, outro motor"

out "ok"`, lang: 'df' },
  {"h2": "189 · Quando usar record e quando usar blueprint"},
  {"p": "Compare os dois, e escolha pelo que o dado precisa."},
  { code: `// Exercicio 189 — Quando usar record e quando usar blueprint
// Enunciado: compare os dois, e escolha pelo que o dado precisa.

// record: imutavel, igualdade estrutural, sem estado que muda.
// blueprint: identidade propria, estado que evolui, comportamento.
//
// A pergunta que decide: dois desses com os mesmos valores sao a mesma
// coisa? Se sim, record.

record Ponto:
    x: Integer
    y: Integer

    action distancia_ate(outro):
        yield sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)

// dois pontos com as mesmas coordenadas SAO o mesmo ponto
a := Ponto(1, 2)
b := Ponto(1, 2)
assert a is b, "records com os mesmos valores sao iguais"
assert a.distancia_ate(Ponto(4, 6)) is 5.0, "e tem comportamento"

// e nao mudam: 'with' cria outro
movido := a with {"x": 10}
assert a.x is 1, "o original nao mudou"
assert movido.x is 10, "a copia tem o valor novo"

monitor:
    a.x := 99
    assert no, "deveria ter recusado"
handle e:
    out "record e imutavel"

// ja duas contas com o mesmo saldo NAO sao a mesma conta
blueprint Conta:
    private saldo: Float := 0.0
    numero: String := ""

    action setup(numero):
        self.numero := numero

    action depositar(v):
        self.saldo += v
        yield self.saldo

c1 := spawn Conta("001")
c2 := spawn Conta("002")
c1.depositar(100)
c2.depositar(100)

// mesmo saldo, contas diferentes — cada uma tem identidade
assert c1.numero isnt c2.numero, "sao contas distintas"
c1.depositar(50)
assert c1.numero is "001", "e cada uma evolui por conta propria"

out "record para valor, blueprint para identidade"
out "ok"`, lang: 'df' },
  {"h2": "190 · Polimorfismo"},
  {"p": "Trate tipos diferentes pela interface comum."},
  { code: `// Exercicio 190 — Polimorfismo
// Enunciado: trate tipos diferentes pela interface comum.

// O ganho do polimorfismo nao e evitar 'given': e poder acrescentar um
// tipo novo sem tocar em quem usa. O codigo que percorre a lista abaixo
// nao muda quando chega um formato novo.

trait Exportavel:
    action exportar()
    action extensao()

blueprint ComoJson with Exportavel:
    dados: Vault := {}
    action setup(dados):
        self.dados := dados
    action exportar():
        adopt Arcane.Serialization as S
        yield S.to_json(self.dados)
    action extensao():
        yield "json"

blueprint ComoCsv with Exportavel:
    dados: Vault := {}
    action setup(dados):
        self.dados := dados
    action exportar():
        chaves := sorted(self.dados.keys())
        valores := []
        cycle k in chaves:
            valores.append(str(self.dados[k]))
        yield chaves.join(",") + "\\n" + valores.join(",")
    action extensao():
        yield "csv"

blueprint ComoTexto with Exportavel:
    dados: Vault := {}
    action setup(dados):
        self.dados := dados
    action exportar():
        linhas := []
        cycle k in sorted(self.dados.keys()):
            linhas.append($"{k}: {self.dados[k]}")
        yield linhas.join("\\n")
    action extensao():
        yield "txt"

dados := {"nome": "Ana", "idade": 30}
formatos := [spawn ComoJson(dados), spawn ComoCsv(dados), spawn ComoTexto(dados)]

// este laco nao sabe quantos formatos existem, nem quais
cycle f in formatos:
    out $"--- .{f.extensao()} ---"
    out f.exportar()

assert len(formatos) is 3, "tres formatos"
assert formatos[0].extensao() is "json", "cada um se identifica"
assert formatos[1].exportar().contains("idade,nome"), "o csv tem cabecalho"

// acrescentar um quarto formato nao muda nada acima
blueprint ComoMarkdown with Exportavel:
    dados: Vault := {}
    action setup(dados):
        self.dados := dados
    action exportar():
        linhas := ["| chave | valor |", "|---|---|"]
        cycle k in sorted(self.dados.keys()):
            linhas.append($"| {k} | {self.dados[k]} |")
        yield linhas.join("\\n")
    action extensao():
        yield "md"

formatos.append(spawn ComoMarkdown(dados))
assert len(formatos) is 4, "o laco acima funcionaria igual"

out "ok"`, lang: 'df' },
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '181--campos-declarados', text: "181 · Campos declarados", level: 2 as const }, { id: '182--metodos-estaticos', text: "182 · Metodos estaticos", level: 2 as const }, { id: '183--propriedades-com-get-e-set', text: "183 · Propriedades com get e set", level: 2 as const }, { id: '184--visibilidade-private-e-protected', text: "184 · Visibilidade: private e protected", level: 2 as const }, { id: '185--sobrecarga-de-operadores', text: "185 · Sobrecarga de operadores", level: 2 as const }, { id: '186--blueprints-abstratos-e-contratos-de-trait', text: "186 · Blueprints abstratos e contratos de trait", level: 2 as const }, { id: '187--heranca-e-root', text: "187 · Heranca e 'root'", level: 2 as const }, { id: '188--composicao-no-lugar-de-heranca', text: "188 · Composicao no lugar de heranca", level: 2 as const }, { id: '189--quando-usar-record-e-quando-usar-blueprint', text: "189 · Quando usar record e quando usar blueprint", level: 2 as const }, { id: '190--polimorfismo', text: "190 · Polimorfismo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"21 · OOP avançado"}
      description={"Campos, propriedades, operadores, visibilidade, abstratos e modelagem."}
      href={"/docs/exercicios/21-oop-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
