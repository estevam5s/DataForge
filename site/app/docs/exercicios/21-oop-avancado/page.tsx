// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "21 · OOP avançado",
  description: "10 exercícios: propriedades, estáticos, operadores, SOLID.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **A linguagem a fundo** · propriedades, estáticos, operadores, SOLID · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 21`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[182](#182-campos-declarados)", "**Campos declarados**", "declare campos com tipo e padrao no corpo do blueprint."], ["[183](#183-metodos-estaticos)", "**Metodos estaticos**", "crie metodos que pertencem ao blueprint, nao a instancia."], ["[184](#184-propriedades-com-get-e-set)", "**Propriedades com get e set**", "exponha um valor calculado, e valide na atribuicao."], ["[185](#185-visibilidade-private-e-protected)", "**Visibilidade: private e protected**", "proteja o estado interno de um objeto."], ["[186](#186-sobrecarga-de-operadores)", "**Sobrecarga de operadores**", "faca '+' e '==' funcionarem no seu proprio tipo."], ["[187](#187-blueprints-abstratos-e-contratos-de-trait)", "**Blueprints abstratos e contratos de trait**", "declare o que um tipo precisa ter, e deixe o compilador cobrar."], ["[188](#188-heranca-e-root)", "**Heranca e 'root'**", "estenda um comportamento sem reescrever o do pai."], ["[189](#189-composicao-no-lugar-de-heranca)", "**Composicao no lugar de heranca**", "monte comportamento juntando objetos, nao estendendo."], ["[190](#190-quando-usar-record-e-quando-usar-blueprint)", "**Quando usar record e quando usar blueprint**", "compare os dois, e escolha pelo que o dado precisa."], ["[191](#191-polimorfismo)", "**Polimorfismo**", "trate tipos diferentes pela interface comum."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "182 · Campos declarados"},
  {"p": "**Enunciado.** declare campos com tipo e padrao no corpo do blueprint."},
  { code: `// Antes do 4.1, todo campo nascia no setup. Declara-los no corpo diz o
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
out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/182_campos_declarados.df` },
  {"h3": "Conceitos"},
  {"p": "Até o 4.0, todo campo nascia por atribuição no `setup`. Isso funciona, mas esconde a forma do objeto: para saber o que ele tem, era preciso ler o corpo do construtor inteiro."},
  { code: `blueprint Contador:
    valor: Integer := 0
    passo: Integer := 1`, lang: 'df' },
  {"p": "Declarar o campo separa **o que o objeto tem** de **como ele nasce** — e o valor padrão elimina o `setup` repetitivo."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "atributo de classe, ou `@dataclass`"], ["TypeScript", "`campo: Tipo = valor` na classe"], ["Java", "`private int valor = 0;`"], ["Kotlin", "`var valor: Int = 0`"]]}},
  {"h3": "O que observar"},
  {"p": "**Campo sem padrão começa `void`.** Não é erro: é o valor que diz \"ainda não tem\". Um campo obrigatório deve ser preenchido no `setup`."},
  {"p": "**Campos são herdados.** O filho enxerga os do pai sem redeclarar, e pode acrescentar os seus."},
  {"p": "**O tipo é documentação verificada.** O analisador estático usa a anotação para apontar atribuição incompatível antes de rodar."},
  {"h3": "Armadilhas"},
  {"list": ["Um campo declarado **não** é criado pelo `setup` automaticamente — se o"]},
  {"p": "construtor recebe `nome`, ainda é preciso `self.nome := nome`."},
  {"list": ["O padrão é avaliado uma vez, na declaração do blueprint. Para um valor que"]},
  {"p": "precisa ser novo a cada objeto (uma lista, por exemplo), atribua no `setup`."},
  {"h3": "Relacionados"},
  {"list": ["[182 — Métodos estáticos](182_metodos_estaticos.md)", "[184 — Visibilidade](184_visibilidade.md)", "[189 — Records vs blueprints](189_records_vs_blueprints.md)"]},
  {"h2": "183 · Metodos estaticos"},
  {"p": "**Enunciado.** crie metodos que pertencem ao blueprint, nao a instancia."},
  { code: `// Um metodo estatico nao usa 'self'. Serve para o que e da familia toda:
// construtores alternativos, conversoes, constantes calculadas.

blueprint Temperatura:
    celsius: Float := 0.0

    static action de_fahrenheit(f):
        nova := spawn Temperatura()
        nova.celsius := (f - 32) * 5 / 9
        yield nova

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

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/183_metodos_estaticos.df` },
  {"h3": "Conceitos"},
  {"p": "Um método estático não recebe `self`. Ele é chamado no blueprint:"},
  { code: `blueprint Temperatura:
    static action de_fahrenheit(f):
        t := spawn Temperatura()
        t.celsius := (f - 32) * 5 / 9
        yield t

gelo := Temperatura.de_fahrenheit(32)`, lang: 'df' },
  {"p": "O uso mais comum é o **construtor alternativo** — uma segunda forma de criar o objeto, com nome que diz o que ela faz. `Temperatura.de_fahrenheit(32)` é mais claro que um `setup` com um parâmetro `escala`."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`@staticmethod` / `@classmethod`"], ["TypeScript", "`static metodo()`"], ["Java", "`public static`"], ["Rust", "função associada, `impl` sem `self`"]]}},
  {"h3": "O que observar"},
  {"p": "**Chamar um método de instância no blueprint dá erro útil.** A mensagem mostra o `spawn` que falta, em vez de estourar `Undefined name: 'self'` lá dentro:"},
  { code: `erro[DF0301]: 'Temperatura.em_fahrenheit()' is an instance method and needs an object.
    Spawn one first:
        obj := spawn Temperatura(…)
        obj.em_fahrenheit(…)
    Or declare it as 'static action em_fahrenheit(…)' if it does not use 'self'.`, lang: 'text' },
  {"h3": "Armadilhas"},
  {"list": ["Um método estático **não enxerga `self`**. Se precisar do estado do objeto,"]},
  {"p": "ele não deveria ser estático."},
  {"list": ["`static x := valor` (sem `action`) declara um valor compartilhado por todas as"]},
  {"p": "instâncias — e mudá-lo muda para todas."},
  {"h3": "Relacionados"},
  {"list": ["[181 — Campos declarados](181_campos_declarados.md)", "[183 — Propriedades](183_propriedades.md)"]},
  {"h2": "184 · Propriedades com get e set"},
  {"p": "**Enunciado.** exponha um valor calculado, e valide na atribuicao."},
  { code: `// Uma propriedade e lida como campo mas roda codigo. O ganho: dá para
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

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/184_propriedades.df` },
  {"h3": "Conceitos"},
  {"p": "Uma propriedade é **lida e escrita como campo, mas roda código**:"},
  { code: `blueprint Retangulo:
    get area():
        yield self._largura * self._altura

    set largura(v):
        given v smaller_eq 0:
            trigger "largura precisa ser positiva"
        self._largura := v`, lang: 'df' },
  {"p": "Quem usa escreve `r.area` e `r.largura := 4` — não `r.obter_area()`. A diferença importa: você pode transformar um campo em propriedade depois, sem quebrar quem já usava."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`@property` / `@x.setter`"], ["TypeScript", "`get x()` / `set x(v)`"], ["C#", "`public int X { get; set; }`"], ["Kotlin", "`val x get() = …`"]]}},
  {"h3": "O que observar"},
  {"p": "**Propriedade só de leitura recusa escrita**, dizendo o que falta:"},
  { code: `erro[DF0301]: 'Retangulo.area' is read-only: it has a 'get' but no 'set'.
    Add one:  set area(valor): …`, lang: 'text' },
  {"p": "**O setter é o lugar da validação.** Um campo público aceita qualquer coisa; uma propriedade decide o que é válido no momento da escrita, e não depois."},
  {"p": "**Propriedades são herdadas**, e o `get` do pai enxerga os campos do filho."},
  {"h3": "Armadilhas"},
  {"list": ["O campo de apoio precisa ter outro nome (`_largura`), senão o setter chama a si"]},
  {"p": "mesmo — recursão infinita."},
  {"list": ["Uma propriedade que faz trabalho pesado engana: quem lê `obj.x` espera um custo"]},
  {"p": "de leitura. Se a conta é cara, um método com nome é mais honesto."},
  {"h3": "Relacionados"},
  {"list": ["[184 — Visibilidade](184_visibilidade.md)", "[182 — Métodos estáticos](182_metodos_estaticos.md)"]},
  {"h2": "185 · Visibilidade: private e protected"},
  {"p": "**Enunciado.** proteja o estado interno de um objeto."},
  { code: `// 'private' e visivel so dentro do blueprint. 'protected' alcanca
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

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/185_visibilidade.df` },
  {"h3": "Conceitos"},
  { code: `blueprint Conta:
    private saldo: Float := 0.0      // só dentro de Conta
    protected titular: String := ""  // Conta e seus herdeiros
    numero: String := ""             // público`, lang: 'df' },
  {"p": "O que fica público é **a promessa que você mantém**. O resto você pode mudar sem avisar ninguém — e é essa liberdade que a visibilidade compra."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`_nome` por convenção (não impede nada)"], ["TypeScript", "`private` / `protected`"], ["Java", "`private` / `protected`"], ["Rust", "privado por padrão, `pub` para expor"]]}},
  {"h3": "O que observar"},
  {"p": "**Em DataForge, `private` impede de verdade.** Não é convenção: o acesso de fora é recusado em tempo de execução, com mensagem que diz de onde partiu:"},
  { code: `erro[DF0301]: 'Conta.saldo' is private and was accessed outside any blueprint.
              Only 'Conta' can read it.`, lang: 'text' },
  {"p": "**`protected` alcança o herdeiro**, `private` não. Um campo que o filho precisa ler é `protected`; um que só o pai usa é `private`."},
  {"p": "**A verificação vale para leitura e escrita.** Não dá para forjar o saldo de fora."},
  {"h3": "Armadilhas"},
  {"list": ["`private` de um pai **não** vaza para o filho. Se o filho precisa, é"]},
  {"p": "`protected`."},
  {"list": ["Tornar tudo privado e criar um `get`/`set` para cada campo devolve o problema"]},
  {"p": "ao ponto de partida. Exponha comportamento (`depositar`), não estado (`saldo`)."},
  {"h3": "Relacionados"},
  {"list": ["[183 — Propriedades](183_propriedades.md)", "[187 — Herança e root](187_heranca_e_root.md)"]},
  {"h2": "186 · Sobrecarga de operadores"},
  {"p": "**Enunciado.** faca '+' e '==' funcionarem no seu proprio tipo."},
  { code: `// Sobrecarregar operador so vale quando a operacao e obvia: somar dois
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
assert(a + b).x is 4.0, "soma componente a componente"
assert(b - a).y is 2.0, "subtracao"
assert(a * 3).x is 3.0, "multiplicacao por escalar"

// igualdade estrutural, nao de identidade
assert a == spawn Vetor(1, 2), "dois vetores iguais sao =="
assert not(a == b), "vetores diferentes nao sao"

// '!=' sai de '==' negado, sem precisar declarar
assert a isnt b, "isnt deriva do =="

out "comprimento de (3,4):", b.comprimento
assert b.comprimento is 5.0, "3-4-5"

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/186_sobrecarga_operadores.df` },
  {"h3": "Conceitos"},
  { code: `blueprint Vetor:
    operator + (o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)

    operator == (o):
        yield self.x is o.x and self.y is o.y`, lang: 'df' },
  {"p": "Sobrecarregar operador só vale quando a operação é **óbvia**: somar dois vetores, comparar dois valores monetários. Se alguém precisa ler a documentação para saber o que `+` faz no seu tipo, um método com nome é melhor."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`__add__`, `__eq__`"], ["C++", "`operator+`"], ["Rust", "`impl Add for T`"], ["Kotlin", "`operator fun plus`"]]}},
  {"h3": "O que observar"},
  {"p": "**`isnt` sai de `==` negado.** Declarar `operator ==` já faz `isnt` funcionar — não é preciso declarar os dois."},
  {"p": "**Operadores são herdados.** Um filho ganha os do pai sem redeclarar."},
  {"p": "**Nem todo símbolo pode ser sobrecarregado.** A mensagem lista quais:"},
  { code: `erro[DF0103]: '@' cannot be overloaded. You can overload: !=, %, *, **, +, -, /, <, <=, ==, >, >=`, lang: 'text' },
  {"h3": "Armadilhas"},
  {"list": ["`+` deve **devolver um valor novo**, não alterar `self`. `a + b` que muda `a`"]},
  {"p": "surpreende quem lê."},
  {"list": ["Operadores não comutativos (`-`, `/`, `<`) só são tentados no lado esquerdo."]},
  {"p": "`2 * vetor` não funciona se só `Vetor` define `*`; escreva `vetor * 2`."},
  {"h3": "Relacionados"},
  {"list": ["[189 — Records vs blueprints](189_records_vs_blueprints.md)", "[186 — Abstratos e traits](186_abstratos_e_traits.md)"]},
  {"h2": "187 · Blueprints abstratos e contratos de trait"},
  {"p": "**Enunciado.** declare o que um tipo precisa ter, e deixe o compilador cobrar."},
  { code: `// Um blueprint abstrato nao pode ser spawnado: ele existe para ser
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

assert(spawn Quadrado(4)).area() is 16.0, "area do quadrado"

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

assert(spawn Peso(1)).comparar(spawn Peso(2)) is -1, "o contrato foi cumprido"

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/187_abstratos_e_traits.df` },
  {"h3": "Conceitos"},
  { code: `abstract blueprint Forma:
    abstract action area()       // exigência: o herdeiro implementa

    action descrever():          // concreto: o herdeiro ganha de graça
        yield $"area {self.area()}"`, lang: 'df' },
  {"p": "Um blueprint abstrato **não pode ser spawnado** — ele existe para ser herdado. Um método abstrato é uma exigência, e o erro sai **na declaração do herdeiro**, não na primeira chamada."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`ABC` + `@abstractmethod`"], ["TypeScript", "`abstract class` / `interface`"], ["Java", "`abstract class` / `interface`"], ["Rust", "`trait` com método sem corpo"]]}},
  {"h3": "O que observar"},
  {"p": "**O contrato é conferido na declaração.** Um blueprint que adota um trait e não implementa o que ele exige falha ao ser declarado:"},
  { code: `erro[DF0301]: Blueprint 'Ruim' does not implement 1 abstract method:
    comparar()  — declarado em 'Comparavel'
    Implement it, or mark 'Ruim' as 'abstract blueprint' if it is not meant
    to be spawned directly.`, lang: 'text' },
  {"p": "Isso é diferente de descobrir o problema quando alguém chama o método ausente, em produção."},
  {"p": "**Trait pode ter implementação padrão.** Método com corpo no trait é herdado; método sem corpo é exigência."},
  {"p": "**Um abstrato pode ter métodos concretos** que chamam os abstratos — é o padrão \"método molde\": o pai define o roteiro, o filho preenche os passos."},
  {"h3": "Armadilhas"},
  {"list": ["Um blueprint que herda de abstrato e **não implementa tudo** também precisa ser"]},
  {"p": "`abstract`. Deixar pela metade não compila."},
  {"list": ["Trait não guarda estado. Para compartilhar campos, use herança ou composição."]},
  {"h3": "Relacionados"},
  {"list": ["[188 — Composição](188_composicao.md)", "[190 — Polimorfismo](190_polimorfismo.md)"]},
  {"h2": "188 · Heranca e 'root'"},
  {"p": "**Enunciado.** estenda um comportamento sem reescrever o do pai."},
  { code: `// 'root' chama a versao do pai. Serve para acrescentar sem duplicar —
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

assert(spawn Base()).identidade() is "base", "o final funciona normalmente"

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/188_heranca_e_root.df` },
  {"h3": "Conceitos"},
  { code: `blueprint Artigo extends Documento:
    action cabecalho():
        yield root.cabecalho() + $"\\npor {self.autor}"`, lang: 'df' },
  {"p": "`root` chama a versão do pai. É o que distingue **estender** de **reimplementar**: o filho acrescenta, e continua acompanhando as mudanças do pai."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`super()`"], ["TypeScript / Java", "`super`"], ["Rust", "não tem herança; usa composição"]]}},
  {"h3": "O que observar"},
  {"p": "**Polimorfismo sem esforço.** O método `render` foi herdado sem mudança e chama `self.cabecalho()` — que resolve para a versão do filho. Um método do pai enxerga as sobrescritas do filho."},
  {"p": "**`final` impede sobrescrita.** Um método marcado `final` não pode ser trocado pelo herdeiro, e a tentativa falha na declaração:"},
  { code: `erro[DF0301]: 'Filho.identidade' cannot override 'Base.identidade',
              which is declared final`, lang: 'text' },
  {"p": "Use `final` no que o resto da hierarquia depende para funcionar."},
  {"h3": "Armadilhas"},
  {"list": ["Herança amarra o filho ao pai **para sempre**. Antes de estender, pergunte se"]},
  {"p": "não é composição — veja o [188](188_composicao.md)."},
  {"list": ["Uma cadeia de herança com mais de dois ou três níveis costuma ser sinal de que"]},
  {"p": "a modelagem foi longe demais."},
  {"h3": "Relacionados"},
  {"list": ["[188 — Composição](188_composicao.md)", "[184 — Visibilidade](184_visibilidade.md)"]},
  {"h2": "189 · Composicao no lugar de heranca"},
  {"p": "**Enunciado.** monte comportamento juntando objetos, nao estendendo."},
  { code: `// Heranca amarra o filho ao pai para sempre. Composicao troca a peca
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
        self.motor := motor  // o carro TEM um motor

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

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/189_composicao.df` },
  {"h3": "Conceitos"},
  {"p": "A regra prática que decide:"},
  {"list": ["**Herança** quando A *é* um B — um Artigo é um Documento.", "**Composição** quando A *tem* um B — um Carro tem um Motor."]},
  { code: `blueprint Carro:
    action setup(modelo, motor):
        self.motor := motor          // TEM um motor

    action dar_partida():
        yield self.motor.ligar()`, lang: 'df' },
  {"p": "Herança amarra o filho ao pai para sempre. Composição permite **trocar a peça**:"},
  { code: `carro.motor := spawn MotorCombustao(100)   // mesmo carro, outro motor`, lang: 'df' },
  {"p": "Com herança, isso exigiria outro tipo."},
  {"h3": "O que observar"},
  {"p": "**O trait define o encaixe.** `Motor` diz o que qualquer motor precisa saber fazer; o carro depende do contrato, não da implementação."},
  {"p": "**Testar fica mais simples.** Para testar o carro, passe um motor de mentira — não é preciso montar a hierarquia inteira."},
  {"h3": "Armadilhas"},
  {"list": ["Composição custa uma indireção: `self.motor.ligar()` em vez de `self.ligar()`."]},
  {"p": "Para uma relação que realmente é \"é um\", herança é mais direta."},
  {"list": ["Um objeto que compõe cinco outros e só repassa chamadas provavelmente devia ser"]},
  {"p": "cinco objetos separados."},
  {"h3": "Relacionados"},
  {"list": ["[186 — Abstratos e traits](186_abstratos_e_traits.md)", "[190 — Polimorfismo](190_polimorfismo.md)"]},
  {"h2": "190 · Quando usar record e quando usar blueprint"},
  {"p": "**Enunciado.** compare os dois, e escolha pelo que o dado precisa."},
  { code: `// record: imutavel, igualdade estrutural, sem estado que muda.
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
out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/190_records_vs_blueprints.df` },
  {"h3": "Conceitos"},
  {"p": "A pergunta que decide: **dois desses, com os mesmos valores, são a mesma coisa?**"},
  {"table": {"head": ["", "`record`", "`blueprint`"], "rows": [["Igualdade", "estrutural — mesmos valores, mesmo record", "por identidade"], ["Mutação", "imutável; `with` cria cópia", "estado evolui"], ["Uso típico", "valor: ponto, dinheiro, data", "entidade: conta, usuário, sessão"]]}},
  {"p": "Dois pontos `(1, 2)` **são** o mesmo ponto — record. Duas contas com o mesmo saldo **não** são a mesma conta — blueprint."},
  {"table": {"head": ["Linguagem", "record", "blueprint"], "rows": [["Python", "`@dataclass(frozen=True)`", "`class`"], ["Java", "`record`", "`class`"], ["Kotlin", "`data class`", "`class`"], ["Rust", "`struct` + `derive(PartialEq)`", "`struct` + `impl`"]]}},
  {"h3": "O que observar"},
  {"p": "**Record também tem comportamento.** `distancia_ate` é um método normal — a diferença não é ter ou não métodos, é a identidade e a mutabilidade."},
  {"p": "**`with` devolve uma cópia**, e o original não muda. É o que torna record seguro de compartilhar: ninguém altera o seu pelas costas."},
  {"p": "**Tentar atribuir a um campo de record é recusado**, com a alternativa na mensagem."},
  {"h3": "Armadilhas"},
  {"list": ["Usar blueprint para valor força você a implementar `operator ==` à mão, e a"]},
  {"p": "lembrar de copiar antes de passar adiante."},
  {"list": ["Usar record para entidade obriga a recriar o objeto inteiro a cada mudança, e"]},
  {"p": "perde a identidade — duas contas iguais viram uma."},
  {"h3": "Relacionados"},
  {"list": ["[181 — Campos declarados](181_campos_declarados.md)", "[185 — Sobrecarga de operadores](185_sobrecarga_operadores.md)"]},
  {"h2": "191 · Polimorfismo"},
  {"p": "**Enunciado.** trate tipos diferentes pela interface comum."},
  { code: `// O ganho do polimorfismo nao e evitar 'given': e poder acrescentar um
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

out "ok"`, lang: 'df', title: `exercicios/21-oop-avancado/191_polimorfismo.df` },
  {"h3": "Conceitos"},
  { code: `formatos := [spawn ComoJson(dados), spawn ComoCsv(dados), spawn ComoTexto(dados)]

cycle f in formatos:
    out f.exportar()      // não sabe qual formato é`, lang: 'df' },
  {"p": "O ganho do polimorfismo **não é evitar `given`**. É que o laço acima não muda quando chega um quarto formato. Compare com o alternativo:"},
  { code: `given tipo is "json":
    ...
orif tipo is "csv":
    ...              // toda vez que chega um formato, este bloco cresce`, lang: 'df' },
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "duck typing / `Protocol`"], ["TypeScript", "`interface`"], ["Java", "`interface` + `implements`"], ["Rust", "`dyn Trait`"]]}},
  {"h3": "O que observar"},
  {"p": "**O trait é o que garante.** Sem ele, um formato que esqueceu `exportar` só falharia quando o laço chegasse nele. Com trait, falha na declaração."},
  {"p": "**Acrescentar um tipo é uma adição, não uma edição.** `ComoMarkdown` entrou no fim do exercício, e nenhuma linha anterior mudou. É essa propriedade que faz o código envelhecer bem."},
  {"h3": "Armadilhas"},
  {"list": ["Polimorfismo com dois casos que nunca vão crescer é cerimônia: um `given`"]},
  {"p": "resolve, e se lê melhor."},
  {"list": ["Se cada implementação precisa de um parâmetro diferente, a interface comum não"]},
  {"p": "existe de verdade — e forçá-la produz assinaturas com argumentos que metade ignora."},
  {"h3": "Relacionados"},
  {"list": ["[186 — Abstratos e traits](186_abstratos_e_traits.md)", "[188 — Composição](188_composicao.md)"]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/21-oop-avancado/182_campos_declarados.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '182-campos-declarados', text: "182 · Campos declarados", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '183-metodos-estaticos', text: "183 · Metodos estaticos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '184-propriedades-com-get-e-set', text: "184 · Propriedades com get e set", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '185-visibilidade-private-e-protected', text: "185 · Visibilidade: private e protected", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '186-sobrecarga-de-operadores', text: "186 · Sobrecarga de operadores", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '187-blueprints-abstratos-e-contratos-de-trait', text: "187 · Blueprints abstratos e contratos de trait", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '188-heranca-e-root', text: "188 · Heranca e 'root'", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '189-composicao-no-lugar-de-heranca', text: "189 · Composicao no lugar de heranca", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '190-quando-usar-record-e-quando-usar-blueprint', text: "190 · Quando usar record e quando usar blueprint", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '191-polimorfismo', text: "191 · Polimorfismo", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"21 · OOP avançado"}
      description={"10 exercícios: propriedades, estáticos, operadores, SOLID."}
      href={"/docs/exercicios/21-oop-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
