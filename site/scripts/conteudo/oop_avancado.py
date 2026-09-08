"""As páginas de OOP que faltavam — de fundamentos a arquitetura."""

PAGINAS = [
{
"href": "/docs/oop/fundamentos",
"title": "Fundamentos",
"description": "Objeto, classe, instância, estado, identidade — e o que cada palavra significa em DataForge.",
"blocos": [
 {"p": "Antes da sintaxe, o vocabulário. Cada termo abaixo tem um nome próprio em DataForge, e saber qual é qual poupa a maior parte da confusão."},

 {"h2": "O que é orientação a objetos"},
 {"p": "Um jeito de organizar programa juntando **dados** e o **comportamento** que age sobre eles. A alternativa — dados de um lado, funções de outro — funciona bem até o programa crescer; aí ninguém mais sabe quais funções podem mexer em quais dados."},
 {"p": "OOP responde isso pondo os dois no mesmo lugar e controlando quem entra."},

 {"h2": "Classe e instância"},
 {"p": "A **classe** é a forma; a **instância** é a peça. Em DataForge a classe é o `blueprint` — a planta — e a peça nasce com `spawn`:"},
 {"code": """blueprint Conta:
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
assert b.extrato is "Bia: 0.0\"""", "lang": "df"},

 {"h2": "Estado, comportamento, identidade"},
 {"p": "Todo objeto tem três coisas, e elas se confundem com frequência:"},
 {"table": {"head": ["", "O que é", "Em DataForge"], "rows": [
   ["**estado**", "os valores que ele guarda agora", "os campos: `self.saldo`"],
   ["**comportamento**", "o que ele sabe fazer", "os métodos: `action depositar`"],
   ["**identidade**", "o que faz ele ser ele, e não outro igual", "a referência — dois `spawn` dão dois objetos"]]}},
 {"p": "A identidade é o que separa `blueprint` de `record`. Duas contas com o mesmo saldo **não são a mesma conta**; dois pontos (1,2) **são o mesmo ponto**:"},
 {"code": """record Ponto:
    x: Integer
    y: Integer

blueprint Caixa:
    action setup(n):
        self.n := n

// record: igualdade estrutural — o conteúdo decide
assert Ponto(1, 2) is Ponto(1, 2)

// blueprint: identidade — cada spawn é um objeto
assert (spawn Caixa(1)) isnt (spawn Caixa(1))""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "A pergunta que decide", "texto": "**Dois destes, com os mesmos valores, são a mesma coisa?** Se sim, é `record`. Se não, é `blueprint`. Essa pergunta resolve a maioria das dúvidas de modelagem."}},

 {"h2": "Atributos e métodos"},
 {"p": "Campos guardam; métodos agem. Ambos podem ser **de instância** (cada objeto tem o seu) ou **estáticos** (um só, da classe):"},
 {"code": """blueprint Contador:
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
assert Contador.zerar() is 0""", "lang": "df"},
 {"p": "Ver [métodos estáticos](/docs/oop/estaticos) para quando usar cada um."},

 {"h2": "Construtor"},
 {"p": "`setup` é o construtor: roda uma vez, no `spawn`, e é onde o objeto nasce válido. Há duas formas:"},
 {"code": """// forma explícita
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
assert round((spawn Circulo(1)).area(), 3) is 3.142""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Não há destrutor", "texto": "DataForge coleta memória sozinho. Para liberar um recurso — arquivo, conexão — use `defer` ou `with`, que rodam mesmo se algo falhar no meio."}},

 {"h2": "`self`"},
 {"p": "`self` é o objeto em que o método está rodando. **Escrever `x` em vez de `self.x` lê a variável do escopo externo** — é a armadilha mais comum de quem começa:"},
 {"code": """valor := "de fora"

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
assert (spawn Certo()).mostrar() is "de dentro\"""", "lang": "df"},

 {"h2": "Modificadores de acesso"},
 {"p": "Três níveis, e eles valem de verdade — não por convenção de nome:"},
 {"table": {"head": ["", "Quem alcança"], "rows": [
   ["(padrão)", "qualquer um"],
   ["`protected`", "o blueprint que declarou e seus herdeiros"],
   ["`private`", "só o blueprint que declarou — nem o herdeiro"]]}},
 {"p": "Ver [campos e visibilidade](/docs/oop/campos) e [encapsulamento](/docs/oop/encapsulamento)."},
]},

{
"href": "/docs/oop/encapsulamento",
"title": "Encapsulamento",
"description": "Esconder o detalhe para poder mudá-lo — e as validações que só existem porque ele existe.",
"blocos": [
 {"p": "Encapsular não é esconder por esconder. É **separar o que os outros dependem do que você pode mudar amanhã**."},
 {"p": "Um campo público faz parte do contrato: mudá-lo quebra quem o usa. Um campo privado é seu — você troca a implementação e ninguém percebe."},

 {"h2": "O problema, concretamente"},
 {"code": """// Sem encapsulamento: qualquer um mexe no saldo
blueprint ContaAberta:
    saldo: Float := 0.0

c := spawn ContaAberta()
c.saldo := -1000        // ninguém impediu
assert c.saldo is -1000.0""", "lang": "df"},
 {"code": """// Com encapsulamento: a regra mora com o dado
blueprint Conta:
    private saldo: Float := 0.0

    action depositar(valor):
        given valor smaller_eq 0:
            trigger "depósito precisa ser positivo"
        self.saldo += valor
        yield self.saldo

    action sacar(valor):
        given valor bigger self.saldo:
            trigger "saldo insuficiente"
        self.saldo -= valor
        yield self.saldo

    get extrato():
        yield self.saldo

c := spawn Conta()
c.depositar(100)
c.sacar(30)
assert c.extrato is 70.0

monitor:
    c.sacar(1000)
handle e:
    assert e.message is "saldo insuficiente\"""", "lang": "df"},
 {"p": "O saldo nunca fica negativo, e não porque quem usa lembrou de conferir — porque não há caminho até ele que não passe pela regra."},

 {"h2": "`private` alcança quem?"},
 {"p": "Só o blueprint que **declarou** o membro. Nem o herdeiro entra:"},
 {"code": """blueprint Base:
    private segredo: Integer := 42
    protected compartilhado: Integer := 7

    action ler_proprio():
        yield self.segredo

blueprint Filho extends Base:
    action ler_protegido():
        yield self.compartilhado

// um método de Base lê o private de Base, mesmo numa instância de Filho
assert (spawn Filho()).ler_proprio() is 42
assert (spawn Filho()).ler_protegido() is 7

monitor:
    out (spawn Base()).segredo
handle e:
    assert "private" in e.message""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Quem declarou, não quem instanciou", "texto": "Um método herdado de `Base` que lê um `private` de `Base` funciona numa instância de `Filho` — o dono da visibilidade é quem escreveu o membro."}},

 {"h2": "Getters e setters, com propósito"},
 {"p": "Um `get`/`set` que só devolve e atribui o campo não encapsula nada — é um campo público com três linhas a mais. O valor aparece quando há **regra** ou **derivação**:"},
 {"code": """blueprint Temperatura:
    private _celsius: Float := 0.0

    // derivada: não há campo 'fahrenheit', ele é calculado
    get fahrenheit():
        yield self._celsius * 9 / 5 + 32

    set fahrenheit(valor):
        self._celsius := (valor - 32) * 5 / 9

    get celsius():
        yield self._celsius

    set celsius(valor):
        given valor smaller -273.15:
            trigger "abaixo do zero absoluto"
        self._celsius := valor

t := spawn Temperatura()
t.celsius := 100
assert t.fahrenheit is 212.0
t.fahrenheit := 32
assert t.celsius is 0.0""", "lang": "df"},
 {"p": "Ver [propriedades](/docs/oop/propriedades) para a sintaxe completa."},

 {"h2": "Imutabilidade"},
 {"p": "A forma mais forte de encapsulamento: um valor que **não muda** não precisa de proteção. `record` é imutável, e alterar produz um valor novo:"},
 {"code": """record Dinheiro:
    centavos: Integer
    moeda: String

    action somar(outro):
        given outro.moeda isnt self.moeda:
            trigger "moedas diferentes"
        yield Dinheiro(self.centavos + outro.centavos, self.moeda)

a := Dinheiro(1050, "BRL")
b := a.somar(Dinheiro(250, "BRL"))

assert a.centavos is 1050       // o original não mudou
assert b.centavos is 1300""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Imutável passa sem medo", "texto": "Um record pode ser passado a qualquer função sem risco de ela alterá-lo. É o que torna código concorrente tratável — e o que permite usá-lo como chave de vault."}},

 {"h2": "Ocultação de informação"},
 {"p": "O princípio geral, de David Parnas: **um módulo deve esconder uma decisão de projeto**. Se a decisão mudar, só ele muda."},
 {"code": """blueprint Cache:
    private itens: Vault := {}
    private ordem: Cluster := []
    private limite: Integer := 100

    action guardar(chave, valor):
        given not self.itens.has(chave):
            self.ordem.append(chave)
        self.itens[chave] := valor
        given len(self.ordem) bigger self.limite:
            velha := self.ordem.pop(0)
            delete self.itens[velha]
        yield valor

    action pegar(chave):
        yield self.itens.get(chave, void)

c := spawn Cache()
c.guardar("a", 1)
assert c.pegar("a") is 1
assert c.pegar("z") is void""", "lang": "df"},
 {"p": "A decisão escondida aqui é *como* o cache decide o que descartar. Trocar por LRU de verdade, ou por tempo de vida, não muda uma linha de quem usa."},
]},

{
"href": "/docs/oop/polimorfismo",
"title": "Polimorfismo",
"description": "O mesmo nome, comportamentos diferentes — e por que isso elimina o if gigante.",
"blocos": [
 {"p": "Polimorfismo é **um nome, várias implementações**, escolhidas pelo tipo do objeto. O que ele resolve, na prática: o `if` gigante que cresce a cada tipo novo."},

 {"h2": "O problema"},
 {"code": """// Sem polimorfismo: cada forma nova mexe nesta função
action area(forma):
    match forma["tipo"]:
        point "circulo":
            yield 3.14159 * forma["raio"] ** 2
        point "quadrado":
            yield forma["lado"] ** 2
        default:
            trigger "forma desconhecida"

assert area({"tipo": "quadrado", "lado": 3}) is 9""", "lang": "df"},
 {"p": "Acrescentar um triângulo obriga a mexer aqui — e em toda outra função que faça esse `match`. Perímetro, desenhar, serializar: cada uma tem o seu."},

 {"h2": "A solução"},
 {"code": """trait Forma:
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

assert area_total([spawn Quadrado(3), spawn Quadrado(4)]) is 25.0""", "lang": "df"},
 {"p": "Um triângulo novo é um arquivo novo. Nada do que já existe muda — é o [princípio aberto/fechado](/docs/oop/solid) em ação."},

 {"h2": "Sobrescrita (override)"},
 {"p": "O herdeiro redefine um método da mãe. `root` chama a versão dela:"},
 {"code": """blueprint Animal:
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
assert (spawn Filhote("Pip")).falar() is "Pip late baixinho\"""", "lang": "df"},

 {"h2": "Sobrecarga (overload)"},
 {"p": "DataForge **não tem** sobrecarga por assinatura — dois métodos com o mesmo nome e parâmetros diferentes. O motivo: numa linguagem dinâmica não há tipo em tempo de compilação para escolher qual chamar."},
 {"p": "O que existe no lugar, e resolve os mesmos casos:"},
 {"code": """blueprint Registro:
    // valores padrão cobrem o caso de "menos argumentos"
    action registrar(mensagem, nivel := "info", quando := void):
        marca := quando ?? "agora"
        yield $"[{nivel}] {marca}: {mensagem}"

r := spawn Registro()
assert r.registrar("oi") is "[info] agora: oi"
assert r.registrar("erro", "grave") is "[grave] agora: erro\"""", "lang": "df"},
 {"code": """// e 'match' cobre o caso de "tipos diferentes"
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
assert descrever([1, 2]) is "par\"""", "lang": "df"},

 {"h2": "Upcasting e downcasting"},
 {"p": "Tratar um `Cachorro` como `Animal` é upcasting — sempre seguro, e é o que o polimorfismo faz o tempo todo. O caminho de volta precisa de verificação:"},
 {"code": """blueprint Animal:
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
assert interagir(spawn Animal("bicho")) is "bicho não busca nada\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Downcasting é sinal de alerta", "texto": "Perguntar o tipo para decidir o que fazer costuma significar que falta um método no trait. Antes de escrever o `given`, pergunte se `buscar()` não deveria existir em `Animal` sem fazer nada."}},

 {"h2": "Tempo de compilação e tempo de execução"},
 {"p": "Em linguagens estáticas, sobrecarga é resolvida na compilação e sobrescrita na execução. Em DataForge **tudo é na execução** — o método vem do objeto real, sempre:"},
 {"code": """blueprint A:
    action quem():
        yield "A"

blueprint B extends A:
    action quem():
        yield "B"

action perguntar(x):
    yield x.quem()

// a função não sabe o tipo; o objeto decide
assert perguntar(spawn A()) is "A"
assert perguntar(spawn B()) is "B\"""", "lang": "df"},
 {"p": "É mais flexível e mais lento — a busca do método acontece a cada chamada. Ver [desempenho](/docs/desempenho)."},
]},

{
"href": "/docs/oop/relacionamentos",
"title": "Relacionamentos entre objetos",
"description": "Associação, agregação, composição, dependência — e por que a diferença importa.",
"blocos": [
 {"p": "Objetos se conhecem de jeitos diferentes, e o jeito decide quem cria quem, quem morre com quem, e o que quebra ao mudar."},

 {"h2": "As quatro formas"},
 {"table": {"head": ["", "Força", "Ciclo de vida", "Exemplo"], "rows": [
   ["**dependência**", "a mais fraca", "independentes", "um método recebe um `Relatorio` como parâmetro"],
   ["**associação**", "fraca", "independentes", "`Pedido` conhece o `Cliente`"],
   ["**agregação**", "média", "independentes", "`Time` tem `Jogador`; o jogador sobrevive ao time"],
   ["**composição**", "forte", "morrem juntos", "`Pedido` tem `ItemDePedido`; sem pedido, o item não existe"]]}},

 {"h2": "Dependência"},
 {"p": "A mais fraca: o objeto usa outro, mas não o guarda."},
 {"code": """blueprint Impressora:
    // 'documento' entra, é usado, e vai embora
    action imprimir(documento):
        yield $"imprimindo: {documento.titulo}"

record Documento:
    titulo: String

p := spawn Impressora()
assert p.imprimir(Documento("Contrato")) is "imprimindo: Contrato\"""", "lang": "df"},

 {"h2": "Associação"},
 {"p": "O objeto **guarda** uma referência ao outro, mas os dois existem por conta própria:"},
 {"code": """blueprint Cliente:
    action setup(nome):
        self.nome := nome

blueprint Pedido:
    action setup(cliente, total):
        self.cliente := cliente
        self.total := total

    get resumo():
        yield $"{self.cliente.nome}: {self.total}"

ana := spawn Cliente("Ana")
p1 := spawn Pedido(ana, 100)
p2 := spawn Pedido(ana, 250)

// um cliente, dois pedidos — e o cliente existia antes deles
assert p1.resumo is "Ana: 100"
assert p2.cliente is p1.cliente""", "lang": "df"},

 {"h2": "Agregação"},
 {"p": "\"Tem um\", mas a parte sobrevive ao todo:"},
 {"code": """blueprint Jogador:
    action setup(nome):
        self.nome := nome

blueprint Time:
    action setup(nome):
        self.nome := nome
        self.jogadores := []

    action contratar(jogador):
        self.jogadores.append(jogador)
        yield len(self.jogadores)

    action liberar(jogador):
        self.jogadores.remove(jogador)
        yield len(self.jogadores)

j := spawn Jogador("Pelé")
t := spawn Time("Santos")
t.contratar(j)
t.liberar(j)

// o time acabou com ele; o jogador continua existindo
assert j.nome is "Pelé\"""", "lang": "df"},

 {"h2": "Composição"},
 {"p": "\"É feito de\": a parte **nasce e morre** com o todo, e não é compartilhada:"},
 {"code": """record ItemDePedido:
    produto: String
    quantidade: Integer
    preco: Float

    action subtotal():
        yield self.quantidade * self.preco

blueprint Pedido:
    action setup():
        self.itens := []

    // o pedido CRIA seus itens — eles não vêm de fora
    action adicionar(produto, quantidade, preco):
        self.itens.append(ItemDePedido(produto, quantidade, preco))
        yield len(self.itens)

    get total():
        soma := 0.0
        cycle i in self.itens:
            soma += i.subtotal()
        yield soma

p := spawn Pedido()
p.adicionar("Teclado", 2, 250.0)
p.adicionar("Mouse", 1, 90.0)
assert p.total is 590.0""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Como distinguir", "texto": "Pergunte: **se o todo for destruído, a parte ainda faz sentido?** Um jogador sem time faz. Um item de pedido sem pedido não faz. O primeiro é agregação, o segundo é composição."}},

 {"h2": "Cardinalidade"},
 {"p": "Quantos de cada lado. É o que vira chave estrangeira no banco:"},
 {"table": {"head": ["Notação", "Significa", "No [ORM](/docs/orm/relacoes)"], "rows": [
   ["1 → 1", "um para um", "`tem_um`"],
   ["1 → N", "um para muitos", "`tem_muitos`"],
   ["N → 1", "muitos para um", "`pertence_a`"],
   ["N → N", "muitos para muitos", "`muitos_para_muitos`, com tabela ponte"]]}},
 {"code": """// Cliente 1 ─── N Pedido ─── N Produto
adopt Forge

db := Forge.conectar(":memory:")

Cliente := Forge.modelo("Cliente", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})

Pedido := Forge.modelo("Pedido", {
    "id": {"tipo": "Serial"},
    "cliente_id": {"tipo": "Inteiro", "indice": yes},
    "total": {"tipo": "Real", "padrao": 0}
}, {"conexao": db})

Cliente.tem_muitos("pedidos", "Pedido")
Pedido.pertence_a("cliente", "Cliente")
Forge.migrar_tudo(db)

ana := Cliente.criar({"nome": "Ana"})
Pedido.criar({"cliente_id": ana["id"], "total": 100.0})

com_pedidos := Cliente.com(Cliente.todos(), "pedidos")
assert len(com_pedidos[0]["pedidos"]) is 1""", "lang": "df"},

 {"h2": "Navegabilidade"},
 {"p": "Uma associação pode ser **unidirecional** (o pedido conhece o cliente, mas o cliente não lista pedidos) ou **bidirecional** (os dois se conhecem)."},
 {"p": "Bidirecional é mais conveniente e mais caro: os dois lados precisam ficar consistentes, e há sempre o risco de um ciclo na serialização."},
 {"callout": {"tipo": "atencao", "titulo": "Comece unidirecional", "texto": "Só acrescente o outro lado quando alguém precisar dele. Uma referência que ninguém usa é código para manter sem retorno — e um ciclo esperando para estourar no `para_json`."}},
]},

{
"href": "/docs/oop/solid",
"title": "SOLID",
"description": "Os cinco princípios, cada um com o problema que resolve — em DataForge.",
"blocos": [
 {"p": "SOLID não é lei; são cinco observações sobre o que costuma dar errado. Cada uma abaixo vem com o código ruim e o bom, para a diferença ficar concreta."},

 {"h2": "S — Responsabilidade única"},
 {"p": "*Uma classe deve ter um só motivo para mudar.*"},
 {"code": """// Ruim: muda se a regra de imposto mudar, se o formato do
// relatório mudar, OU se o banco mudar. Três motivos.
blueprint FolhaRuim:
    action setup(salario):
        self.salario := salario

    action calcular_imposto():
        yield self.salario * 0.275

    action formatar_relatorio():
        yield $"Salário: {self.salario}"

    action salvar():
        yield "gravado"

assert (spawn FolhaRuim(1000)).calcular_imposto() is 275.0""", "lang": "df"},
 {"code": """// Bom: cada peça muda por um motivo só
record Folha:
    salario: Float

blueprint CalculadoraDeImposto:
    action calcular(folha):
        yield folha.salario * 0.275

blueprint RelatorioDeFolha:
    action formatar(folha):
        yield $"Salário: {folha.salario}"

f := Folha(1000.0)
assert (spawn CalculadoraDeImposto()).calcular(f) is 275.0
assert (spawn RelatorioDeFolha()).formatar(f) is "Salário: 1000.0\"""", "lang": "df"},

 {"h2": "O — Aberto/fechado"},
 {"p": "*Aberto para extensão, fechado para modificação.* Acrescentar comportamento não deveria exigir editar o que já funciona."},
 {"code": """// Ruim: cada meio de pagamento novo mexe aqui
action cobrar_ruim(tipo, valor):
    match tipo:
        point "pix":
            yield valor
        point "cartao":
            yield valor * 1.05
        default:
            trigger "meio desconhecido"

assert cobrar_ruim("pix", 100) is 100""", "lang": "df"},
 {"code": """// Bom: um meio novo é um blueprint novo
trait MeioDePagamento:
    action cobrar(valor)

blueprint Pix with MeioDePagamento:
    action cobrar(valor):
        yield valor

blueprint Cartao with MeioDePagamento:
    action cobrar(valor):
        yield valor * 1.05

blueprint Boleto with MeioDePagamento:
    action cobrar(valor):
        yield valor + 3.50

action cobrar(meio, valor):
    yield meio.cobrar(valor)

assert cobrar(spawn Pix(), 100) is 100
assert cobrar(spawn Boleto(), 100) is 103.5""", "lang": "df"},

 {"h2": "L — Substituição de Liskov"},
 {"p": "*Onde cabe a mãe, tem de caber a filha.* Uma subclasse não pode quebrar o que a mãe prometeu."},
 {"code": """// Ruim: Quadrado herda de Retangulo e quebra a promessa
blueprint Retangulo:
    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    action area():
        yield self.largura * self.altura

blueprint QuadradoRuim extends Retangulo:
    action setup(lado):
        root.setup(lado, lado)

    // quem tem um Retangulo espera mudar um lado só
    action mudar_largura(v):
        self.largura := v
        self.altura := v        // surpresa

r := spawn QuadradoRuim(5)
r.mudar_largura(3)
assert r.area() is 9          // quem esperava 15 se enganou""", "lang": "df"},
 {"code": """// Bom: os dois implementam o contrato, sem herdar um do outro
trait Forma:
    action area()

blueprint Retangulo(largura, altura) with Forma:
    action area():
        yield self.largura * self.altura

blueprint Quadrado(lado) with Forma:
    action area():
        yield self.lado ** 2

assert (spawn Retangulo(3, 5)).area() is 15
assert (spawn Quadrado(4)).area() is 16""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "O clássico quadrado/retângulo", "texto": "Matematicamente todo quadrado é um retângulo. Em código, a herança quebra porque `Retangulo` promete que largura e altura mudam separadamente — e o quadrado não pode cumprir. **Ser um** na matemática não é **ser um** no código."}},

 {"h2": "I — Segregação de interface"},
 {"p": "*Ninguém deve depender de método que não usa.* Traits pequenos e específicos, não um grande."},
 {"code": """// Ruim: uma impressora simples é obrigada a saber escanear
trait MaquinaRuim:
    action imprimir(doc)
    action escanear(doc)
    action enviar_fax(doc)

blueprint SimplesRuim with MaquinaRuim:
    action imprimir(doc):
        yield "imprimiu"
    action escanear(doc):
        trigger "não sei escanear"        // implementa para nada
    action enviar_fax(doc):
        trigger "não sei mandar fax"

assert (spawn SimplesRuim()).imprimir("x") is "imprimiu\"""", "lang": "df"},
 {"code": """// Bom: traits separados, cada objeto implementa o que faz
trait Impressora:
    action imprimir(doc)

trait Scanner:
    action escanear(doc)

blueprint Simples with Impressora:
    action imprimir(doc):
        yield "imprimiu"

blueprint Multifuncional with Impressora, Scanner:
    action imprimir(doc):
        yield "imprimiu"
    action escanear(doc):
        yield "escaneou"

assert (spawn Simples()).imprimir("x") is "imprimiu"
assert (spawn Multifuncional()).escanear("x") is "escaneou\"""", "lang": "df"},

 {"h2": "D — Inversão de dependência"},
 {"p": "*Dependa de abstração, não de implementação.* O código de negócio não deveria saber que o banco é PostgreSQL."},
 {"code": """// Ruim: a regra de negócio conhece o detalhe do armazenamento
blueprint ServicoRuim:
    action setup():
        self.linhas := []

    action cadastrar(nome):
        self.linhas.append($"INSERT INTO usuarios VALUES ('{nome}')")
        yield len(self.linhas)

assert (spawn ServicoRuim()).cadastrar("Ana") is 1""", "lang": "df"},
 {"code": """// Bom: a regra depende de um contrato; o detalhe entra por fora
trait RepositorioDeUsuarios:
    action salvar(nome)
    action contar()

blueprint RepositorioEmMemoria with RepositorioDeUsuarios:
    action setup():
        self.itens := []
    action salvar(nome):
        self.itens.append(nome)
        yield nome
    action contar():
        yield len(self.itens)

blueprint ServicoDeCadastro:
    action setup(repositorio):
        self.repositorio := repositorio

    action cadastrar(nome):
        given len(nome) smaller 2:
            trigger "nome curto demais"
        yield self.repositorio.salvar(nome)

// o teste usa memória; a produção usaria o Forge — mesma classe
s := spawn ServicoDeCadastro(spawn RepositorioEmMemoria())
s.cadastrar("Ana")
assert s.repositorio.contar() is 1""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "É o que torna teste barato", "texto": "Um serviço que recebe o repositório por parâmetro se testa sem banco nenhum. Um que constrói o próprio exige subir PostgreSQL para testar uma regra de validação de nome."}},

 {"h2": "Acoplamento e coesão"},
 {"p": "Os cinco princípios servem a duas ideias mais gerais:"},
 {"table": {"head": ["", "Você quer", "Sinal de problema"], "rows": [
   ["**acoplamento**", "baixo — poucas peças se conhecem", "mudar A obriga a mudar B, C e D"],
   ["**coesão**", "alta — o que está junto pertence junto", "uma classe chamada `Utils` ou `Manager`"]]}},
 {"p": "Ver [composição e arquitetura](/docs/oop/composicao)."},
]},
]
