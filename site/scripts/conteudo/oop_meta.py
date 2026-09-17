"""OOP de verdade: modificadores, contratos, metaclasses, reflexão, injeção e padrões.

Toda página aqui tem blocos `df` que RODAM: `tests/test_oop_avancada.py`
executa cada um e passa cada um pelo `check`. Um exemplo de documentação
que não roda ensina errado.
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/modificadores",
"title": "Modificadores",
"description": "private, protected, internal, readonly, override, final, sealed, exclusive, lazy e static steady — o que cada um promete, e quem confere.",
"blocos": [
 {"p": "Um modificador é uma promessa escrita na declaração. A diferença entre uma promessa e um comentário é que **alguém confere**: o `dataforge check` antes de rodar, e o interpretador quando roda. Cada linha da tabela abaixo tem um erro com nome próprio, que um `handle` pega."},
 {"table": {"head": ["Modificador", "Vale em", "Promete", "Quebrar dá"], "rows": [
   ["`private`", "ação, campo, propriedade", "só o blueprint que declarou lê, escreve e chama", "`TypeError`"],
   ["`protected`", "ação, campo, propriedade", "o blueprint e os herdeiros", "`TypeError`"],
   ["`internal`", "ação, campo, propriedade", "só o **arquivo** que declarou", "`InternalAccessError`"],
   ["`readonly`", "campo", "só a construção escreve", "`ReadOnlyFieldError`"],
   ["`static steady`", "campo estático", "constante de classe", "`ConstantReassignmentError`"],
   ["`override`", "ação, propriedade", "substitui um membro herdado", "`OverrideTargetError`"],
   ["`final`", "ação", "a filha não substitui", "`FinalOverrideError`"],
   ["`final blueprint`", "blueprint", "ninguém herda", "`FinalBlueprintError`"],
   ["`sealed blueprint`", "blueprint", "só herda quem está no mesmo arquivo", "`SealedBlueprintError`"],
   ["`exclusive`", "ação", "uma thread por vez no objeto", "—"],
   ["`lazy`", "`get`", "calcula uma vez por objeto", "—"]]}},

 {"h2": "Visibilidade: private, protected, internal"},
 {"p": "`private` e `protected` falam de **linhagem**; `internal` fala de **arquivo**. É a visibilidade de um módulo: as peças de dentro conversam, e quem adota o arquivo vê só o público."},
 {"code": """blueprint Conta:
    private saldo := 0.0
    protected taxa := 0.01
    internal action auditar():
        yield $"saldo {self.saldo}"

    action depositar(v):
        self.saldo += v
        yield self.saldo

blueprint ContaPremium extends Conta:
    action custo(v):
        yield v * self.taxa          // protected: a filha lê

c := spawn ContaPremium()
c.depositar(100)
assert c.custo(100) is 1.0
assert c.auditar() is "saldo 100.0"   // internal: mesmo arquivo

monitor:
    out c.saldo
    assert no
handle TypeError as e:
    assert "private" in e.message""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Vale para a chamada também", "texto": "`obj.privado()` de fora é recusado exatamente como `obj.privado`. A leitura já era conferida; a chamada de método não era, e um `private action` podia ser chamado de qualquer lugar."}},

 {"h2": "readonly: identidade que não muda"},
 {"p": "Um campo `readonly` recebe valor enquanto o objeto nasce — no padrão, no cabeçalho, no `setup`, no corpo solto do blueprint — e depois disso é recusado. O `check` também acusa um método comum que o escreve."},
 {"code": """blueprint Pedido:
    readonly id := 0
    readonly criado_em := "2026-09-17"
    itens := []

    action setup(id):
        self.id := id                 // construindo: permitido

p := spawn Pedido(42)
assert p.id is 42

monitor:
    p.id := 43
    assert no
handle ReadOnlyFieldError:
    out "o id de um pedido não muda"

// 'with' constrói OUTRO objeto, e por isso pode mudar um readonly
copia := p with {"id": 7}
assert copia.id is 7 and p.id is 42""", "lang": "df"},

 {"h2": "Constante de classe: static steady"},
 {"code": """blueprint Http:
    static steady PORTA_PADRAO := 80
    static conexoes := 0

Http.conexoes := Http.conexoes + 1     // estático comum: muda
assert Http.PORTA_PADRAO is 80

monitor:
    Http.PORTA_PADRAO := 8080
    assert no
handle ConstantReassignmentError:
    out "constante é constante" """, "lang": "df"},

 {"h2": "override: a promessa que pega o erro de digitação"},
 {"p": "Sem `override`, um método com o nome quase certo vira um método novo, e o da mãe continua rodando — em silêncio. Com `override`, o nome errado é erro, com sugestão."},
 {"code": """blueprint Animal:
    action falar():
        yield "..."

blueprint Gato extends Animal:
    override action falar():
        yield "miau"

assert (spawn Gato()).falar() is "miau"
""", "lang": "df"},
 {"code": """blueprint Cachorro extends Animal:
    override action fala():     // erro[override-sem-alvo]: did you mean 'falar'?
        yield "au"
""", "lang": "text"},

 {"h2": "final e sealed: fechar a hierarquia"},
 {"p": "`final blueprint` fecha para todo mundo. `sealed blueprint` fecha para **fora do arquivo**: a família é conhecida e completa, que é o que deixa um `match` confiar que cobriu os casos."},
 {"code": """final blueprint Dinheiro(centavos):
    action somar(outro):
        yield spawn Dinheiro(self.centavos + outro.centavos)

abstract sealed blueprint Forma:
    abstract action area()

blueprint Quadrado(lado) extends Forma:
    action area():
        yield self.lado ** 2

assert (spawn Dinheiro(150)).somar(spawn Dinheiro(50)).centavos is 200
assert (spawn Quadrado(3)).area() is 9

monitor:
    blueprint Moeda extends Dinheiro:
        simbolo := "R$"
    assert no
handle FinalBlueprintError:
    out "use composição: guarde um Dinheiro num campo" """, "lang": "df"},

 {"h2": "exclusive: o monitor do objeto"},
 {"p": "O `check` avisa quando duas threads escrevem no mesmo lugar (`escrita-concorrente`). `exclusive` é a correção no nível do objeto: só uma thread por vez roda um método exclusivo **daquele** objeto. A trava é reentrante — um método exclusivo que chama outro não espera por si mesmo."},
 {"code": """blueprint Estoque:
    quantidade := 0
    exclusive action entrar(n):
        atual := self.quantidade
        self.quantidade := atual + n

e := spawn Estoque()
parallel:
    thread:
        cycle i from 1 to 500:
            e.entrar(1)
    thread:
        cycle i from 1 to 500:
            e.entrar(1)

assert e.quantidade is 1000""", "lang": "df"},

 {"h2": "lazy: calcular uma vez"},
 {"code": """blueprint Relatorio(linhas):
    contas := 0
    lazy get total():
        self.contas += 1
        yield sum(self.linhas)

r := spawn Relatorio([10, 20, 30])
assert r.total is 60
assert r.total is 60
assert r.contas is 1        // o corpo rodou uma vez só""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/contratos",
"title": "Contratos",
"description": "contract, invariant, expects e promises: interfaces que não carregam código, e design por contrato que diz de quem é o erro.",
"blocos": [
 {"p": "Há dois sentidos de contrato em orientação a objetos, e o DataForge tem os dois: o **contrato de interface** (o que um tipo promete oferecer) e o **design por contrato** (o que uma operação exige e garante)."},

 {"h2": "contract: só a assinatura"},
 {"p": "Um `contract` declara métodos e propriedades sem corpo. Um corpo é recusado na leitura: implementação padrão é o papel do `trait`, e deixar o contrato carregar código apagaria a única diferença entre os dois."},
 {"code": """contract Leitura<T>:
    action buscar(id: Integer) -> T

contract Escrita<T>:
    action salvar(item: T)

contract Repositorio<T> extends Leitura, Escrita:
    get total() -> Integer

blueprint RepoMemoria with Repositorio:
    itens := {}
    action buscar(id: Integer):
        yield self.itens[id] ?? void
    action salvar(item):
        self.itens[len(self.itens) + 1] := item
    get total():
        yield len(self.itens)

// quem só lê depende só de Leitura — o Princípio da Segregação de Interface
action primeiro(fonte: Leitura):
    yield fonte.buscar(1)

r := spawn RepoMemoria()
r.salvar("caneta")
assert primeiro(r) is "caneta"
assert r.total is 1""", "lang": "df"},
 {"table": {"head": ["", "trait", "contract"], "rows": [
   ["corpo de método", "pode ter (implementação padrão)", "recusado"],
   ["estende outro", "não", "`contract A extends B, C`"],
   ["confere aridade de quem implementa", "não", "sim — `SignatureMismatchError`"],
   ["propriedade exigida", "não", "`get total() -> Integer`"],
   ["vale como tipo de parâmetro", "sim", "sim, inclusive o que ele herda"]]}},
 {"p": "Na declaração, o blueprint concreto que adota um contrato precisa ter cada método, **aceitar todos os argumentos** que o contrato passa (parâmetros a mais precisam de padrão) e ter cada propriedade exigida — como `get` ou como campo."},

 {"h2": "expects, promises, invariant"},
 {"p": "As três cláusulas respondem a mesma pergunta — *de quem é o erro?* — e é isso que as separa de um `assert`:"},
 {"table": {"head": ["Cláusula", "Onde", "Quando roda", "Erro", "Quem errou"], "rows": [
   ["`expects cond, msg`", "corpo de ação", "onde estiver", "`PreconditionError`", "quem chamou"],
   ["`promises cond, msg`", "topo do corpo", "na saída, com `outcome`", "`PostconditionError`", "a ação"],
   ["`invariant cond, msg`", "corpo de blueprint", "depois de construir e de cada método público", "`InvariantError`", "a operação"]]}},
 {"code": """blueprint Conta:
    saldo := 0
    invariant self.saldo bigger_eq 0, "saldo nunca fica negativo"

    action depositar(valor):
        expects valor bigger 0, "depósito precisa ser positivo"
        promises self.saldo is before(self.saldo) + valor
        self.saldo += valor
        yield self.saldo

    action sacar(valor):
        expects valor bigger 0, "saque precisa ser positivo"
        promises outcome is self.saldo
        self.saldo -= valor
        yield self.saldo

c := spawn Conta()
c.depositar(100)
assert c.sacar(30) is 70

monitor:
    c.depositar(-5)
    assert no
handle PreconditionError as e:
    assert "positivo" in e.message

monitor:
    c.sacar(500)
    assert no
handle InvariantError as e:
    assert "negativo" in e.message""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "before(…) é o valor da entrada", "texto": "`promises self.saldo is before(self.saldo) + valor` compara o estado da SAÍDA com o da ENTRADA. `before` avalia a expressão antes do corpo rodar e guarda o resultado — é o `old` do Eiffel."}},
 {"p": "A invariante é conferida quando a chamada **mais de fora** termina. Dentro de um método o objeto pode passar por estados intermediários — transferir entre dois campos exige duas escritas — e cobrar ali recusaria todo método correto. Um método `private` não dispara a conferência: ele é passo de outro."},

 {"h2": "Liskov, conferido"},
 {"p": "O Princípio da Substituição diz que a filha serve onde a mãe servia. A parte que dá para **provar** sem rodar, o `check` prova: uma sobrescrita que aceita menos argumentos que a mãe quebra todo código escrito para a mãe, e vira aviso `substituicao-quebrada`. Contra um contrato, é erro."},
 {"code": """blueprint Exportador:
    action exportar(dados, formato := "csv"):
        yield formato

blueprint ExportadorJson extends Exportador:
    action exportar(dados, formato := "json"):     // aceita o mesmo: ok
        yield formato

assert (spawn ExportadorJson()).exportar([]) is "json"
""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/sobrecarga",
"title": "Sobrecarga",
"description": "overload: variantes da mesma ação escolhidas pela aridade e pelos tipos, com empate recusado.",
"blocos": [
 {"p": "Uma linguagem dinâmica não precisa de sobrecarga para aceitar tipos diferentes — um `given typeof(x)` resolve. O que ela ganha com sobrecarga é **declarar** as formas aceitas, e deixar a linguagem recusar a que não serve com a lista das que servem."},
 {"code": """overload action formatar(valor: Integer):
    yield $"{valor}"
overload action formatar(valor: Float):
    yield $"{round(valor, 2)}"
overload action formatar(valor: String, largura: Integer):
    yield valor.ljust(largura)

assert formatar(3) is "3"
assert formatar(2.5) is "2.5"
assert formatar("ab", 4) is "ab  "

monitor:
    formatar(yes)
    assert no
handle OverloadResolutionError as e:
    out e.message""", "lang": "df"},

 {"h2": "Como a variante é escolhida"},
 {"list": [
   "descarta as que não aceitam a **quantidade** e os **nomes** dos argumentos;",
   "confere os **tipos declarados**, com a mesma regra de qualquer anotação (um `Integer` serve onde se pede `Float`);",
   "entre as que sobram, vence a que declara **mais tipos** — a mais específica;",
   "um empate é `AmbiguousOverloadError`. Escolher pela ordem de escrita faria mover uma variante de lugar mudar um programa que não a chama."], "ordered": True},

 {"h2": "Construtores sobrecarregados"},
 {"code": """blueprint Cor:
    r := 0
    g := 0
    b := 0
    overload action setup(cinza: Integer):
        self.r := cinza
        self.g := cinza
        self.b := cinza
    overload action setup(r: Integer, g: Integer, b: Integer):
        self.r := r
        self.g := g
        self.b := b

assert (spawn Cor(128)).g is 128
assert (spawn Cor(1, 2, 3)).b is 3""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Todas marcadas", "texto": "Toda variante leva `overload`, inclusive a primeira. Misturar uma ação comum com variantes do mesmo nome é recusado: não há leitura em que as duas convivam."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/metaclasses",
"title": "Metaclasses",
"description": "meta blueprint e using: interceptar a criação de classes, a construção de objetos e o acesso a membros, com ganchos de nome fixo.",
"blocos": [
 {"p": "Uma metaclasse é o blueprint que governa como **outros blueprints** nascem e se comportam. Em DataForge ela é um `meta blueprint`, aplicado com `using`, e fala com a linguagem por **ganchos de nome fixo** — um `on_…` desconhecido é recusado com sugestão, porque um gancho com nome errado nunca rodaria e nada avisaria."},
 {"table": {"head": ["Gancho", "Quando", "Devolver algo"], "rows": [
   ["`on_forge(molde)`", "o blueprint acabou de ser montado", "substitui o blueprint"],
   ["`on_extend(mae, filha)`", "um blueprint governado ganhou filha", "—"],
   ["`on_spawn(molde, args)`", "antes de construir", "entrega esse objeto no lugar"],
   ["`on_ready(obj)`", "o objeto nasceu, invariantes conferidas", "—"],
   ["`on_read(obj, nome, valor)`", "toda leitura de membro", "troca o valor lido"],
   ["`on_missing(obj, nome)`", "leitura de membro que não existe", "é o valor lido"],
   ["`on_write(obj, nome, valor)`", "toda escrita de campo", "troca o valor gravado"],
   ["`on_call(obj, nome, args)`", "chamada de método vinda de fora", "—"],
   ["`on_serialize(obj, vault)`", "`Objetos.para_vault`", "substitui o vault"],
   ["`on_deserialize(molde, vault)`", "`Objetos.de_vault`", "substitui o vault"]]}},

 {"h2": "Registro automático de classes"},
 {"code": """adopt Arcane.Reflexo as R

meta blueprint Registro:
    tabelas := {}
    action on_forge(molde):
        self.tabelas[R.nome(molde)] := R.nome(molde).lower() + "s"

blueprint Entidade using Registro:
    id := 0

blueprint Usuario extends Entidade:
    nome := ""

blueprint Pedido extends Entidade:
    total := 0

reg := R.meta_instancia(Pedido)
assert reg.tabelas["Usuario"] is "usuarios"
assert len(reg.tabelas) is 3""", "lang": "df"},
 {"p": "A metaclasse é **herdada**: `Usuario` não escreve `using`, e é governado. Ela tem uma instância só, compartilhada por tudo que governa — é o `self` dos ganchos e onde ela guarda estado."},

 {"h2": "Validar a classe na declaração"},
 {"code": """adopt Arcane.Reflexo as R

meta blueprint ComId:
    action on_forge(molde):
        nomes := [c["nome"] cycle c in R.campos(molde)]
        given not ("id" in nomes):
            trigger $"{R.nome(molde)} precisa de um campo 'id'"

blueprint Cliente using ComId:
    id := 0

monitor:
    blueprint Rascunho using ComId:
        texto := ""
    assert no
handle Error as e:
    assert "precisa de um campo" in e.message""", "lang": "df"},

 {"h2": "Instanciação controlada e auditoria"},
 {"code": """meta blueprint Auditado:
    escritas := []
    unicos := {}
    action on_write(obj, nome, valor):
        self.escritas.append(nome)
    action on_spawn(molde, args):
        yield void            // void: constrói normalmente

blueprint Config using Auditado:
    porta := 80
    action trocar(p):
        self.porta := p

c := spawn Config()
c.trocar(8080)
c.porta := 9090
assert c.porta is 9090""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um gancho não dispara outro", "texto": "Dentro de `on_read`, ler um campo do objeto não chama `on_read` de novo — seria recursão sem fim. E duas metaclasses só convivem na mesma linhagem se uma descender da outra: a filha não pode escolher qual regra da mãe ignorar (`MetaclassError`)."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/augment",
"title": "augment",
"description": "Acrescentar membros a um blueprint que já existe — sem substituir nada, sem atravessar final nem sealed.",
"blocos": [
 {"p": "`augment` é a extensão de um tipo sem herança: métodos, propriedades, operadores e estáticos novos num blueprint que já existe — e nos objetos que já foram criados. É o que outras linguagens chamam de método de extensão ou classe parcial."},
 {"code": """blueprint Dinheiro(centavos):
    action reais():
        yield self.centavos / 100

carteira := spawn Dinheiro(1250)

augment Dinheiro:
    get texto():
        yield $"R$ {self.reais():.2f}"
    operator + (outro):
        yield spawn Dinheiro(self.centavos + outro.centavos)

assert carteira.texto is "R$ 12.50"               // o objeto de antes ganhou
assert (carteira + spawn Dinheiro(50)).centavos is 1300""", "lang": "df"},
 {"h2": "O que augment recusa"},
 {"table": {"head": ["Tentativa", "Por quê"], "rows": [
   ["substituir um membro que existe", "substituir é o papel da herança; um augment que troca comportamento de longe é impossível de depurar"],
   ["augment de `final blueprint`", "final promete que o tipo está completo"],
   ["augment de `sealed` de outro arquivo", "sealed promete que a família é conhecida"],
   ["acrescentar campo de instância", "os objetos que já existem não o teriam"],
   ["ver `private` de outro arquivo", "augment não pode ser a porta dos fundos para o que o autor fechou"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/reflexao",
"title": "Reflexão",
"description": "Arcane.Reflexo: descobrir campos, métodos, modificadores, herança e anotações; invocar por nome; criar tipos em execução; desenhar o diagrama de classes.",
"blocos": [
 {"p": "Reflexão é o programa olhando para os próprios tipos. `Arcane.Reflexo` responde o que a declaração diz — e passa pelas **mesmas regras** que o código comum: um `private` continua private quando o nome chega por texto."},
 {"code": """adopt Arcane.Reflexo as R

contract Identificavel:
    get id() -> Integer

abstract blueprint Pessoa with Identificavel:
    readonly id := 0
    nome: String := ""
    abstract action papel()

blueprint Aluno extends Pessoa:
    mark @Coluna("matricula")
    matricula := ""
    override action papel():
        yield "aluno"

assert R.especie(Identificavel) is "contract"
assert R.mro(Aluno)[1] is Pessoa
assert Aluno in R.herdeiros(Pessoa)
assert R.contratos(Aluno) is ["Identificavel"]
assert "readonly" in R.modificadores(Aluno, "id")
assert R.anotacoes(Aluno, "matricula")[0]["args"] is ["matricula"]

nomes := [m["nome"] cycle m in R.metodos(Aluno)]
assert "papel" in nomes

a := spawn Aluno()
assert R.invocar(a, "papel") is "aluno"
R.escrever(a, "nome", "Ana")
assert R.ler(a, "nome") is "Ana"
assert R.cumpre(a, Identificavel)""", "lang": "df"},

 {"h2": "A API"},
 {"table": {"head": ["Grupo", "Funções"], "rows": [
   ["tipos", "`tipo`, `nome`, `especie`, `molde`"],
   ["membros", "`campos`, `metodos`, `propriedades`, `operadores`, `estaticos`, `membros`, `modificadores`, `anotacoes`, `documentacao`, `sugerir`"],
   ["herança", "`maes`, `mro`, `herdeiros`, `descendentes`, `traits`, `contratos`, `descende`, `e_instancia`, `meta`, `meta_instancia`"],
   ["registro", "`blueprints`, `procurar`"],
   ["dinâmico", "`instanciar`, `tem`, `ler`, `escrever`, `invocar`, `cumpre`, `faltando`, `definir_metodo`, `criar_blueprint`"],
   ["inspeção", "`inspecionar`, `diagrama`, `hierarquia`"]]}},

 {"h2": "Tipos criados em execução"},
 {"p": "`criar_blueprint` monta um tipo a partir de um vault, pelas regras de uma declaração escrita: mãe `final` recusa, contrato não cumprido recusa. Um método é um lambda que recebe o objeto como primeiro argumento."},
 {"code": """adopt Arcane.Reflexo as R

Ponto := R.criar_blueprint("Ponto", {
    "campos": {"x": 0, "y": 0},
    "metodos": {"norma": lambda p => sqrt(p.x ** 2 + p.y ** 2)},
})

p := R.instanciar(Ponto)
p.x := 3
p.y := 4
assert p.norma() is 5.0
assert R.procurar("Ponto") is Ponto""", "lang": "df"},

 {"h2": "Diagrama de classes"},
 {"code": """adopt Arcane.Reflexo as R

abstract blueprint Forma:
    abstract action area()
blueprint Circulo(raio: Float) extends Forma:
    action area():
        yield 3.14 * self.raio ** 2

texto := R.diagrama(Forma)
assert "Forma <|-- Circulo" in texto
out texto""", "lang": "df"},
 {"p": "A saída é Mermaid, que o GitHub e a maioria dos editores de Markdown desenham. O mesmo diagrama sai sem rodar nada com `dataforge oop src/ --diagrama`."},
 {"callout": {"tipo": "perigo", "titulo": "Reflexão tem custo", "texto": "Cada chamada por texto passa pela busca completa de membro, de visibilidade e de ganchos — o caminho rápido do interpretador não se aplica. Use para framework, serialização e ferramenta; no laço quente, chame o método."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/objetos",
"title": "Objetos: cópia, imutabilidade e serialização",
"description": "Arcane.Objetos: clonar raso e fundo, congelar, igualdade e hash coerentes, e serialização polimórfica que não deixa o dado escolher o tipo.",
"blocos": [
 {"h2": "Identidade e igualdade"},
 {"p": "`is` entre instâncias é **identidade** — dois `spawn` são dois objetos. É o certo para entidade. Para objeto de valor há `__eq__`, ou `Objetos.igual`, que compara estrutura sem obrigar o blueprint a escrever nada."},
 {"code": """adopt Arcane.Objetos as O

blueprint Endereco(rua, numero):
    x := 0

a := spawn Endereco("Flores", 10)
b := spawn Endereco("Flores", 10)
assert a isnt b                 // identidade
assert O.igual(a, b)            // estrutura
assert O.hash(a) is O.hash(b)   // coerente com igual""", "lang": "df"},

 {"h2": "Contrato entre __eq__ e __hash__"},
 {"p": "Uma instância é chave de vault. Quem declara `__eq__` precisa declarar `__hash__` coerente — objetos iguais com hash diferente somem do vault."},
 {"code": """blueprint Cpf(numero):
    action __eq__(outro):
        yield self.numero is outro.numero
    action __hash__():
        yield self.numero

donos := {}
donos[spawn Cpf("123")] := "Ana"
assert donos[spawn Cpf("123")] is "Ana"
assert sorted([3, 1, 2]) is [1, 2, 3]""", "lang": "df"},

 {"h2": "Cópia"},
 {"code": """adopt Arcane.Objetos as O

blueprint Carrinho:
    itens := []

c1 := spawn Carrinho()
c1.itens.append("caneta")

raso := O.clonar(c1)
fundo := O.clonar_fundo(c1)
fundo.itens.append("lápis")

assert raso.itens is c1.itens          // a mesma lista
assert len(c1.itens) is 1              // o fundo não mexeu no original""", "lang": "df"},
 {"p": "A cópia não roda `setup` — ela não **nasce**, é duplicada. `__copy__`, `__deepcopy__` e `__clone__` no blueprint assumem a cópia quando existem."},

 {"h2": "Congelar"},
 {"code": """adopt Arcane.Objetos as O

blueprint Config:
    porta := 80

c := O.congelar(spawn Config())
assert O.congelado(c)
monitor:
    c.porta := 81
    assert no
handle FrozenObjectError:
    out "passe um objeto congelado a outra thread sem medo" """, "lang": "df"},

 {"h2": "Serialização polimórfica, e segura"},
 {"p": "`para_vault` grava `$tipo` e resolve ciclos com `$id`/`$ref`. `de_vault` **exige a lista de tipos** que pode reconstruir: um dado de fora com `\"$tipo\": \"Admin\"` não decide qual blueprint o programa constrói. É assim que desserialização vira execução de código alheio em linguagens que deixaram o dado escolher."},
 {"code": """adopt Arcane.Objetos as O

blueprint Item(nome, preco):
    x := 0
blueprint Pedido:
    itens := []
    invariant len(self.itens) smaller_eq 100

p := spawn Pedido()
p.itens.append(spawn Item("caneta", 3))
dado := O.para_vault(p)
assert dado["$tipo"] is "Pedido"

volta := O.de_vault(dado, [Pedido, Item])
assert volta.itens[0].nome is "caneta"

monitor:
    O.de_vault({"$tipo": "Admin", "poderes": "todos"}, [Pedido, Item])
    assert no
handle UnsafeDeserializationError:
    out "tipo fora da lista: recusado" """, "lang": "df"},
 {"list": [
   "só os campos **públicos** saem por padrão; `{\"privados\": yes}` inclui os outros, para persistência própria;",
   "a reconstrução confere as **invariantes** — um dado que chega violando a regra do tipo é recusado ali;",
   "`static versao_do_esquema := 2` grava `$versao`, e `on_deserialize` numa metaclasse migra o vault antes de montar."]},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/injecao",
"title": "Injeção de dependência",
"description": "Arcane.Injecao: contêiner com único, transitório e por escopo, fábrica, valor, preguiçoso, dependência opcional e detecção de ciclo.",
"blocos": [
 {"p": "O Princípio da Inversão de Dependência pede que o código de alto nível dependa de **contratos**, e que alguém de fora escolha a implementação. Esse alguém é o contêiner. Ele lê o que já está escrito — o **tipo** dos parâmetros do construtor — e não pede anotação nova."},
 {"code": """adopt Arcane.Injecao as DI

contract Repositorio:
    action salvar(item)

contract Relogio:
    action agora()

blueprint RepoMemoria with Repositorio:
    itens := []
    action salvar(item):
        self.itens.append(item)
        yield len(self.itens)

blueprint RelogioFixo with Relogio:
    action agora():
        yield "2026-09-17"

blueprint Cadastro(repo: Repositorio, relogio: Relogio):
    action registrar(nome):
        yield self.repo.salvar($"{nome}@{self.relogio.agora()}")

c := DI.conteiner()
c.unico(Repositorio, RepoMemoria)
c.unico(Relogio, RelogioFixo)

cadastro := c.resolver(Cadastro)
assert cadastro.registrar("ana") is 1
assert cadastro.repo is c.resolver(Repositorio)     // único: a mesma instância""", "lang": "df"},

 {"h2": "Tempo de vida"},
 {"table": {"head": ["Registro", "Quantas instâncias"], "rows": [
   ["`c.unico(Tipo, Impl)`", "uma para o contêiner inteiro"],
   ["`c.transitorio(Tipo, Impl)`", "uma nova a cada `resolver`"],
   ["`c.por_escopo(Tipo, Impl)`", "uma por escopo: `e := c.escopo()` … `e.fechar()`"],
   ["`c.valor(Tipo, obj)`", "o objeto pronto — configuração, conexão, dublê de teste"],
   ["`c.fabrica(Tipo, acao, escopo)`", "`acao(c)` constrói, quando o construtor não basta"]]}},
 {"code": """adopt Arcane.Injecao as DI

blueprint Conexao:
    fechada := no
    action fechar():
        self.fechada := yes

c := DI.conteiner()
c.por_escopo(Conexao)

pedido1 := c.escopo()
a := pedido1.resolver(Conexao)
assert a is pedido1.resolver(Conexao)       // mesma no escopo
pedido1.fechar()
assert a.fechada                             // o escopo fecha o que abriu

pedido2 := c.escopo()
assert pedido2.resolver(Conexao) isnt a      // outro escopo, outra conexão""", "lang": "df"},

 {"h2": "O que o contêiner recusa"},
 {"code": """adopt Arcane.Injecao as DI

blueprint Ovo(galinha: Galinha):
    x := 0
blueprint Galinha(ovo: Ovo):
    x := 0

monitor:
    DI.conteiner().resolver(Ovo)
    assert no
handle CircularDependencyError as e:
    assert "Ovo → Galinha → Ovo" in e.message""", "lang": "df"},
 {"list": [
   "**ciclo**, com a cadeia inteira — `c.preguicoso(Tipo)` quebra, entregando um objeto que só resolve no primeiro uso;",
   "**parâmetro sem registro** — a menos que tenha padrão, e aí é dependência opcional;",
   "**único que depende de por-escopo** — o objeto de escopo ficaria preso para sempre dentro do único;",
   "**por-escopo pedido ao contêiner raiz** — resolvê-lo ali o transformaria num único calado."]},
 {"p": "Injeção por **campo** usa `@Injetar` sobre um campo tipado; por **método**, `c.chamar(acao)` resolve os parâmetros tipados. `c.conferir()` resolve tudo o que foi registrado e devolve a lista de problemas — num teste, isso pega o registro que falta antes da produção."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/padroes",
"title": "Padrões de projeto",
"description": "Os 23 padrões clássicos em DataForge: os que são a própria linguagem, e os que pedem mecanismo — Arcane.Padroes.",
"blocos": [
 {"p": "A maior parte do catálogo clássico **já é a linguagem**, e escrever biblioteca para esses seria cerimônia. O módulo `Arcane.Padroes` existe para os que pedem estado ou controle que ninguém deveria reescrever a cada projeto."},
 {"table": {"head": ["Padrão", "Em DataForge"], "rows": [
   ["Template Method", "`abstract blueprint` com `abstract action`"],
   ["Strategy", "`contract` + implementações; `Padroes.estrategias()` quando a escolha vem de configuração"],
   ["Decorator", "`mark @decorador`"],
   ["Iterator", "`stream action` + `emit`, ou `__iter__`"],
   ["Factory Method / Static Factory", "`static action criar(…)`; `overload action setup` para construtores nomeados"],
   ["Abstract Factory", "um `contract` de fábrica, injetado"],
   ["Singleton", "`Padroes.unico(fabrica)`, ou `c.unico(Tipo)` no contêiner"],
   ["Object Pool", "`Padroes.pool(fabrica, tamanho)`"],
   ["Builder", "`Padroes.construtor(Tipo, obrigatorios)`"],
   ["Prototype", "`Padroes.prototipos()`, com `clonar_fundo`"],
   ["Flyweight", "`Padroes.compartilhado(fabrica)`"],
   ["Adapter", "blueprint que embrulha, ou `Padroes.adaptar(obj, mapa)`"],
   ["Proxy", "`Padroes.proxy(alvo, interceptar)`, ou `on_call` numa metaclasse"],
   ["Composite", "`Padroes.composto()`"],
   ["Facade / Bridge", "blueprint comum, com o implementador num campo tipado por contrato"],
   ["Command", "`Padroes.comandos()` — executar, desfazer, refazer"],
   ["Chain of Responsibility", "`Padroes.cadeia([manipuladores])`"],
   ["Observer", "`Padroes.observavel()` — prioridade, filtro e 'parar'; `Arcane.Eventos` entre módulos"],
   ["Mediator", "`Padroes.mediador()`"],
   ["Memento", "`Padroes.memento(obj)` / `Padroes.restaurar(obj, m)`"],
   ["State", "`Padroes.maquina(inicial, transicoes)`"],
   ["Visitor", "`Padroes.visitar(obj, visitante)` — `visitar_<Tipo>` subindo a MRO"],
   ["Specification", "`Padroes.especificacao(predicado)` com `e`, `ou`, `nao`"]]}},

 {"h2": "Comandos com desfazer"},
 {"code": """adopt Arcane.Padroes as P

blueprint Texto:
    conteudo := ""

blueprint Escrever(doc, trecho):
    action executar():
        self.doc.conteudo := self.doc.conteudo + self.trecho
    action desfazer():
        tamanho := len(self.doc.conteudo) - len(self.trecho)
        self.doc.conteudo := self.doc.conteudo.substring(0, tamanho)

doc := spawn Texto()
historico := P.comandos()
historico.executar(spawn Escrever(doc, "olá"))
historico.executar(spawn Escrever(doc, " mundo"))
historico.desfazer()
assert doc.conteudo is "olá"
historico.refazer()
assert doc.conteudo is "olá mundo"
""", "lang": "df"},

 {"h2": "Máquina de estados"},
 {"code": """adopt Arcane.Padroes as P

pedido := P.maquina("rascunho", {
    "enviar":   {"de": ["rascunho"], "para": "enviado"},
    "aprovar":  {"de": ["enviado"], "para": "aprovado"},
    "cancelar": {"de": ["rascunho", "enviado"], "para": "cancelado"},
})
pedido.ir("enviar")
assert pedido.eventos() is ["aprovar", "cancelar"]
monitor:
    pedido.ir("enviar")
    assert no
handle StateError as e:
    out e.message""", "lang": "df"},

 {"h2": "Especificação e repositório"},
 {"code": """adopt Arcane.Padroes as P

record Produto:
    id: Integer
    preco: Float
    ativo: Boolean

repo := P.repositorio()
repo.salvar(Produto(1, 10.0, yes))
repo.salvar(Produto(2, 99.0, yes))
repo.salvar(Produto(3, 150.0, no))

caro := P.especificacao(lambda p => p.preco bigger 50, "caro")
ativo := P.especificacao(lambda p => p.ativo, "ativo")
assert len(repo.filtrar(caro.e(ativo))) is 1""", "lang": "df"},

 {"h2": "Arquitetura: portas e adaptadores"},
 {"p": "Hexagonal, Clean e Onion dizem a mesma coisa com desenhos diferentes: o **domínio** não conhece banco, HTTP nem fila. Em DataForge, a porta é um `contract`, o adaptador é um blueprint `with` ele, e o contêiner liga os dois na borda do programa."},
 {"code": """adopt Arcane.Injecao as DI
adopt Arcane.Padroes as P

// ── domínio: não adota nada de fora ──
contract Pagamentos:
    action cobrar(valor: Float) -> Boolean

blueprint Checkout(pagamentos: Pagamentos):
    action finalizar(total: Float):
        expects total bigger 0
        yield "pago" given self.pagamentos.cobrar(total) otherwise "recusado"

// ── adaptadores: a borda ──
blueprint PagamentoFalso with Pagamentos:
    action cobrar(valor: Float) -> Boolean:
        yield valor smaller 1000

// ── composição: um lugar só ──
c := DI.conteiner()
c.unico(Pagamentos, PagamentoFalso)
checkout := c.resolver(Checkout)
assert checkout.finalizar(50.0) is "pago"
assert checkout.finalizar(5000.0) is "recusado"
""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/memoria",
"title": "Ciclo de vida e memória",
"description": "Construção, teardown, referências fracas e o coletor: o que acontece com um objeto do spawn ao descarte.",
"blocos": [
 {"h2": "Do spawn ao descarte"},
 {"list": [
   "`on_spawn` da metaclasse — pode entregar um objeto pronto;",
   "`__new__` — idem;",
   "os padrões dos campos, copiados quando mutáveis;",
   "os parâmetros do cabeçalho, com tipo e padrão;",
   "`setup` (ou `initiate`, ou `__init__`), e o corpo solto do blueprint;",
   "as invariantes e `on_ready`;",
   "…a vida do objeto…",
   "`teardown` (ou `__del__`) quando o último nome o solta."], "ordered": True},

 {"h2": "teardown"},
 {"p": "O DataForge roda sobre o CPython e herda o modelo de memória dele: cada objeto tem um **contador de referências** e morre no instante em que ele chega a zero. É por isso que `teardown` roda na hora, e não \"em algum momento\". Só os blueprints que declaram finalizador pagam por ele."},
 {"code": """log := []

blueprint Arquivo(nome):
    action teardown():
        log.append($"fechou {self.nome}")

a := spawn Arquivo("dados.csv")
a := void
assert log is ["fechou dados.csv"]""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Para recurso, prefira with ou defer", "texto": "`teardown` depende de o último nome soltar o objeto — um objeto preso num ciclo espera o coletor. Arquivo, conexão e trava fecham melhor com `with` ou `defer`, que rodam num ponto conhecido do código."}},

 {"h2": "Referências fracas"},
 {"p": "Uma referência **fraca** aponta sem segurar. É o que um cache e um registro de observadores precisam — guardar o objeto enquanto ele existir, sem ser a razão de ele existir. Um cache com referência forte é o vazamento de memória mais comum que existe."},
 {"code": """adopt Arcane.Memoria as Mem

blueprint Sessao:
    usuario := "ana"

s := spawn Sessao()
ref := Mem.fraca(s)
assert ref.viva()
assert ref.obter().usuario is "ana"

s := void
assert not ref.viva()
assert ref.obter() is void

cache := Mem.mapa_fraco()
chave := spawn Sessao()
cache.definir(chave, "dados caros")
assert cache.tamanho is 1
chave := void
assert cache.tamanho is 0""", "lang": "df"},

 {"h2": "O coletor"},
 {"table": {"head": ["Função", "O que responde"], "rows": [
   ["`Mem.coletar()`", "força a coleta de ciclos; devolve quantos objetos soltou"],
   ["`Mem.vivos(Tipo)`", "quantas instâncias do blueprint (e das filhas) existem agora"],
   ["`Mem.tamanho(obj)`", "bytes aproximados do objeto e do que só ele alcança"],
   ["`Mem.referencias(obj)`", "o contador do CPython"],
   ["`Mem.ao_descartar(obj, acao)`", "roda a ação quando o objeto for coletado"],
   ["`Mem.estatisticas()`", "gerações, limiares e coletas"]]}},
 {"p": "Para economizar memória por objeto, `slots` guarda os campos numa lista em vez de num vault — ver [slots](/docs/oop/slots)."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/oop/metricas",
"title": "Métricas e cheiros",
"description": "dataforge oop: WMC, DIT, NOC, CBO, RFC, LCOM, fan-in, instabilidade e manutenibilidade — e os anti-padrões ligados ao princípio SOLID que ferem.",
"blocos": [
 {"p": "`dataforge oop` lê a árvore, sem executar, e mede cada blueprint pelas métricas de Chidamber e Kemerer — as que a engenharia de software usa desde 1994 para prever onde os defeitos aparecem."},
 {"code": """dataforge oop src/
dataforge oop src/ --diagrama > classes.mmd
dataforge oop src/ --hierarquia
dataforge oop src/ --json
dataforge oop src/ --strict      # sai com erro se houver cheiro""", "lang": "bash"},
 {"table": {"head": ["Métrica", "O que mede", "Alto significa"], "rows": [
   ["WMC", "soma da complexidade ciclomática dos métodos", "difícil de testar"],
   ["DIT", "profundidade na árvore de herança", "comportamento espalhado pelas mães"],
   ["NOC", "filhas diretas", "mudar a mãe afeta muita gente"],
   ["CBO", "com quantos tipos ele conversa", "acoplamento"],
   ["RFC", "métodos próprios + métodos que ele chama", "resposta difícil de prever"],
   ["LCOM", "0 coeso, 1 cada método mexe no seu campo", "vários blueprints dentro de um"],
   ["fan-in / fan-out", "quem depende dele / de quem ele depende", ""],
   ["instabilidade", "fan-out / (fan-in + fan-out)", "0 estável, 1 fácil de mudar"],
   ["MI", "índice de manutenibilidade, 0 a 100", "baixo é caro de manter"]]}},

 {"h2": "Cada cheiro diz o princípio"},
 {"table": {"head": ["Cheiro", "Princípio", "O que fazer"], "rows": [
   ["`god-blueprint`", "SRP", "separar o que muda por motivos diferentes"],
   ["`baixa-coesao`", "SRP", "grupos de métodos com grupos de campos são blueprints diferentes"],
   ["`metodo-longo`", "SRP", "extrair passos com nome"],
   ["`switch-de-tipo`", "OCP", "um método no contrato, sobrescrito por cada tipo"],
   ["`sobrescrita-que-recusa`", "LSP", "se a filha não cumpre, ela não é subtipo"],
   ["`contrato-gordo`", "ISP", "contratos pequenos, um por cliente"],
   ["`dependencia-concreta`", "DIP", "receber pelo construtor, tipado pelo contrato"],
   ["`heranca-funda`", "composição sobre herança", "trocar níveis por campos"],
   ["`acoplamento-excessivo`", "baixo acoplamento", "depender de contratos"],
   ["`modelo-anemico`", "tell, don't ask", "trazer a regra para perto dos dados"],
   ["`inveja-de-recurso`", "tell, don't ask", "o método talvez pertença ao outro objeto"],
   ["`parametros-demais`", "KISS", "agrupar num record"],
   ["`dependencia-circular`", "acoplamento", "extrair um contrato"]]}},
 {"p": "Os limites estão numa tabela só (`LIMITES` em `dataforge/oop_analise.py`), porque são opinião — e opinião escrita em um lugar é discutível; espalhada, não. Os cheiros são sugestões: um blueprint que agrega e roteia pode ter CBO alto de propósito, e o comando só reprova com `--strict`."},

 {"h2": "O que o check prova, e o que o oop sugere"},
 {"p": "A fronteira é a certeza. O `dataforge check` acusa o que dá para **provar** e é erro em qualquer leitura: `override` sem alvo, herança de `final`, contrato incompleto ou com aridade incompatível, `readonly` escrito fora da construção, gancho de metaclasse desconhecido, variantes de `overload` com a mesma assinatura, `spawn` de contrato. O `dataforge oop` aponta o que é **provável**, e deixa a decisão com quem escreveu."},
]},
]
