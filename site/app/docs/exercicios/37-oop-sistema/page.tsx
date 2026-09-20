// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "37 · OOP como sistema",
  description: "10 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 37`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[242](#242-contratos-pequenos-e-quem-depende-de-qual)", "**Contratos pequenos, e quem depende de qual**", "modele um armazenamento de documentos em que quem so LE"], ["[243](#243-o-que-cada-modificador-promete)", "**O que cada modificador promete**", "modele uma conta com identidade imutavel, limite de classe,"], ["[244](#244-de-quem-e-o-erro)", "**De quem e o erro?**", "um estoque com pre-condicao, pos-condicao e invariante, e"], ["[245](#245-sobrecarga-que-diz-o-que-aceita)", "**Sobrecarga que diz o que aceita**", "uma formatacao de valores com variantes por tipo e aridade,"], ["[246](#246-uma-metaclasse-que-registra-valida-e-audita)", "**Uma metaclasse que registra, valida e audita**", "todo modelo de dominio precisa de 'id', ganha nome de tabela"], ["[247](#247-um-validador-generico-escrito-com-reflexao)", "**Um validador generico escrito com reflexao**", "valide qualquer objeto pelas anotacoes dos campos, sem que o"], ["[248](#248-copia-imutabilidade-e-serializacao-que-nao-confia-no-dado)", "**Copia, imutabilidade e serializacao que nao confia no dado**", "persista um pedido com cliente e itens (e um ciclo), recarregue"], ["[249](#249-portas-adaptadores-e-o-conteiner)", "**Portas, adaptadores e o conteiner**", "um caso de uso de cadastro que nao conhece banco nem e-mail,"], ["[250](#250-padroes-com-mecanismo-comando-estado-e-especificacao)", "**Padroes com mecanismo: comando, estado e especificacao**", "um editor de pedido com desfazer, um fluxo de aprovacao que"], ["[251](#251-nascer-viver-sob-threads-e-morrer-limpo)", "**Nascer, viver sob threads, e morrer limpo**", "um contador de acessos seguro sob concorrencia, um cache que"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "242 · Contratos pequenos, e quem depende de qual"},
  {"p": "**Enunciado.** modele um armazenamento de documentos em que quem so LE"},
  { code: `// nao dependa de quem ESCREVE, e confira que um blueprint que promete
// um contrato cumpre a assinatura inteira.

contract Leitura:
    action buscar(id: Integer)
    get total() -> Integer

contract Escrita:
    action salvar(id: Integer, texto: String)

contract Armazem extends Leitura, Escrita:
    action apagar(id: Integer)

blueprint ArmazemMemoria with Armazem:
    private docs := {}

    action buscar(id: Integer):
        yield self.docs[id] ?? void

    action salvar(id: Integer, texto: String):
        self.docs[id] := texto

    action apagar(id: Integer):
        self.docs.remove(id)

    get total():
        yield len(self.docs)

// Quem so exibe depende de Leitura — e nada mais.
action exibir(fonte: Leitura, id: Integer) -> String:
    yield fonte.buscar(id) ?? "(vazio)"

a := spawn ArmazemMemoria()
a.salvar(1, "ata da reunião")
assert exibir(a, 1) is "ata da reunião"
assert exibir(a, 2) is "(vazio)"
assert a.total is 1

// O contrato vale como tipo — inclusive o que ele herda.
action arquivar(destino: Escrita):
    destino.salvar(99, "arquivado")
arquivar(a)
assert a.total is 2

// Uma implementacao que pede argumento a menos e recusada na declaracao.
monitor:
    blueprint Quebrado with Escrita:
        action salvar(id: Integer):
            yield id
    assert no, "devia ter recusado"
handle SignatureMismatchError as e:
    assert "Escrita" in e.message

// E uma que esquece um metodo tambem.
monitor:
    blueprint Esquecido with Leitura:
        total := 0
    assert no, "devia ter recusado"
handle TraitContractError as e:
    assert "buscar" in e.message

// Um contrato nao nasce.
monitor:
    spawn Leitura()
    assert no
handle AbstractInstantiationError:
    out "contrato nao se instancia"

out "242 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/242_contratos_e_segregacao.df` },
  {"h3": "O que se pratica"},
  {"p": "Declarar `contract`, estender contratos, adotar com `with`, usar o contrato como tipo de parâmetro, e ver as duas recusas da declaração."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. O contrato não tem corpo, e isso é o que o separa do trait.** Um `trait` pode trazer implementação padrão; um `contract` só declara. A diferença parece pequena até o dia em que um contrato \"com um método padrão só\" arrasta uma dependência para todo mundo que o implementa."},
  {"p": "**2. Segregar é depender do menor contrato que serve.** `exibir` recebe uma `Leitura`, e não um `Armazem`. Um cache, um arquivo remoto ou um dublê de teste servem ali sem implementar `salvar` e `apagar` — é o Princípio da Segregação de Interface escrito no tipo do parâmetro."},
  {"p": "**3. A assinatura é conferida, e não só o nome.** `salvar(id)` com o nome certo e um argumento a menos quebra todo código escrito contra o contrato. O nome certo é o que faria a quebra passar despercebida até a primeira chamada — por isso a recusa é na **declaração** (`SignatureMismatchError`), e o `check` acusa antes de rodar."},
  {"p": "**4. Uma propriedade exigida aceita campo.** `get total() -> Integer` é cumprido por um `get total()` ou por um campo `total`. Quem lê não sabe a diferença, e não deveria saber."},
  {"h3": "Para ir além"},
  {"list": ["Acrescente um `contract Buscavel extends Leitura` com `procurar(termo)`"]},
  {"p": "e veja o `check` cobrar a implementação."},
  {"list": ["Troque `fonte: Leitura` por `fonte: Armazem` em `exibir` e responda:"]},
  {"p": "que blueprint de teste ficou mais caro de escrever?"},
  {"h2": "243 · O que cada modificador promete"},
  {"p": "**Enunciado.** modele uma conta com identidade imutavel, limite de classe,"},
  { code: `// estado privado e uma familia fechada de tipos de conta.

abstract sealed blueprint Conta:
    readonly numero := 0
    static steady LIMITE_DIARIO := 5000
    private saldo := 0.0
    protected historico := []

    action setup(numero):
        self.numero := numero

    abstract action tarifa(valor)

    action depositar(valor):
        self.saldo += valor
        self.historico.append(valor)
        yield self.saldo

    final action extrato():
        yield $"{self.numero}: {self.saldo}"

    internal action auditoria():
        yield len(self.historico)

blueprint Corrente extends Conta:
    override action tarifa(valor):
        yield valor * 0.01

final blueprint Poupanca extends Conta:
    override action tarifa(valor):
        yield 0

c := spawn Corrente(101)
c.depositar(200)
assert c.extrato() is "101: 200.0"
assert c.tarifa(100) is 1.0
assert c.auditoria() is 1  // internal: mesmo arquivo
assert Conta.LIMITE_DIARIO is 5000

// readonly: so a construcao escreve
monitor:
    c.numero := 999
    assert no
handle ReadOnlyFieldError:
    out "o numero de uma conta nao muda"

// private: nem leitura, nem chamada de fora
monitor:
    out c.saldo
    assert no
handle TypeError as e:
    assert "private" in e.message

// static steady: constante de classe
monitor:
    Conta.LIMITE_DIARIO := 1
    assert no
handle ConstantReassignmentError:
    out "limite e constante"

// final: ninguem herda de Poupanca
monitor:
    blueprint PoupancaPlus extends Poupanca:
        bonus := 1
    assert no
handle FinalBlueprintError:
    out "poupanca e final"

// final action: a filha nao troca o extrato
monitor:
    blueprint Fraude extends Conta:
        override action tarifa(v):
            yield 0
        action extrato():
            yield "tudo certo"
    assert no
handle FinalOverrideError:
    out "extrato e final"

// override: o nome errado e pego na declaracao
monitor:
    blueprint Digitada extends Conta:
        override action tarifaa(v):
            yield 0
    assert no
handle OverrideTargetError as e:
    assert "tarifa" in e.dica

out "243 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/243_modificadores.df` },
  {"h3": "O que se pratica"},
  {"p": "`readonly`, `static steady`, `private`, `protected`, `internal`, `abstract`, `final` (em ação e em blueprint), `sealed` e `override` — cada um com a recusa que o torna real."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. Um modificador que ninguém confere é um comentário.** Cada linha do exercício termina num erro com nome próprio (`ReadOnlyFieldError`, `FinalBlueprintError`, `OverrideTargetError`…), e é esse nome que um `handle` pega. É a diferença entre uma convenção e uma regra."},
  {"p": "**2. `readonly` é sobre o nascimento, não sobre o arquivo.** O `setup` escreve `numero`; depois, ninguém escreve — nem um método da própria conta. O `check` acusa um método comum que tente, antes de rodar."},
  {"p": "**3. `internal` fala de ARQUIVO; `private` e `protected` falam de LINHAGEM.** A auditoria é visível para todo o código deste arquivo, e invisível para quem adota o arquivo. É a visibilidade de um módulo."},
  {"p": "**4. `abstract sealed` fecha a família.** `Corrente` e `Poupanca` são as únicas contas possíveis — outra só num `.df` diferente, que o `sealed` recusa. `final` em `Poupanca` fecha ainda mais: nem aqui ela tem filhas."},
  {"p": "**5. `override` pega o erro de digitação.** Sem ele, `tarifaa` seria um método novo, a `tarifa` abstrata continuaria pendente, e a mensagem falaria de método faltando — longe da causa. Com ele, a mensagem diz \"did you mean 'tarifa'?\"."},
  {"h3": "Para ir além"},
  {"list": ["Rode `dataforge check` neste arquivo sem os `monitor`: cada recusa vira"]},
  {"p": "erro antes de rodar."},
  {"list": ["Mova `Corrente` para outro arquivo e veja o `SealedBlueprintError`."]},
  {"h2": "244 · De quem e o erro?"},
  {"p": "**Enunciado.** um estoque com pre-condicao, pos-condicao e invariante, e"},
  { code: `// uma operacao defeituosa que o contrato denuncia.

blueprint Estoque:
    itens := {}
    invariant len([q cycle q in self.itens.values() given q smaller 0]) is 0, "quantidade negativa"

    action entrar(produto, n):
        expects n bigger 0, "entrada precisa ser positiva"
        promises self.quantidade(produto) is before(self.quantidade(produto)) + n
        self.itens[produto] := self.quantidade(produto) + n
        yield self.itens[produto]

    action sair(produto, n):
        expects n bigger 0, "saida precisa ser positiva"
        self.itens[produto] := self.quantidade(produto) - n
        yield self.itens[produto]

    action entrar_com_bug(produto, n):
        promises self.quantidade(produto) is before(self.quantidade(produto)) + n, "somou errado"
        self.itens[produto] := self.quantidade(produto) + n - 1

    action quantidade(produto):
        yield self.itens[produto] ?? 0

e := spawn Estoque()
assert e.entrar("caneta", 10) is 10
assert e.sair("caneta", 4) is 6

// pre-condicao: quem CHAMOU errou
monitor:
    e.entrar("caneta", 0)
    assert no
handle PreconditionError as erro:
    assert "positiva" in erro.message

// pos-condicao: a ACAO errou
monitor:
    e.entrar_com_bug("lapis", 5)
    assert no
handle PostconditionError as erro:
    assert "somou errado" in erro.message

// invariante: a operacao deixou o objeto inconsistente
monitor:
    e.sair("caneta", 100)
    assert no
handle InvariantError as erro:
    assert "negativa" in erro.message

// Os tres sao ContractError: um handle so pega a familia inteira.
monitor:
    e.sair("caneta", -1)
handle ContractError as erro:
    out "contrato:", erro.type

out "244 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/244_design_por_contrato.df` },
  {"h3": "O que se pratica"},
  {"p": "`expects`, `promises` com `before(…)` e `outcome`, e `invariant` — e a família `ContractError`, que pega os três."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. A cláusula diz de quem é a culpa.** Um `assert` diz *que* algo deu errado. `expects` diz que **quem chamou** errou; `promises` diz que **a ação** errou; `invariant` diz que **a operação** deixou o objeto inconsistente. Num sistema de duzentos arquivos, é a diferença entre abrir o arquivo certo e abrir três."},
  {"p": "**2. `promises` roda na saída, mesmo escrito no topo.** Ele é tirado do corpo pelo parser e conferido quando a ação devolve. `before(expr)` guarda o valor da entrada — sem ele, uma pós-condição não conseguiria falar de *mudança*, só de estado final."},
  {"p": "**3. A invariante é conferida quando a chamada mais de fora termina.** Dentro de um método o objeto passa por estados intermediários — tirar de um lugar e pôr em outro são duas escritas. Cobrar a invariante entre elas recusaria todo método correto."},
  {"p": "**4. `quantidade` é chamada dentro de `promises` e da invariante.** Uma chamada de dentro do próprio objeto não dispara a conferência de novo: ela é passo da operação, não operação."},
  {"h3": "Para ir além"},
  {"list": ["Remova o `expects` de `sair` e veja o `sair(…, -1)` aparecer como"]},
  {"p": "**invariante** quebrada — o erro certo, mas agora culpando a operação em vez de quem chamou."},
  {"h2": "245 · Sobrecarga que diz o que aceita"},
  {"p": "**Enunciado.** uma formatacao de valores com variantes por tipo e aridade,"},
  { code: `// um construtor com duas formas, e as duas recusas da resolucao.

overload action formatar(valor: Integer):
    yield $"{valor}"
overload action formatar(valor: Float):
    yield $"{valor:.2f}"
overload action formatar(valor: Float, casas: Integer):
    yield str(round(valor, casas))
overload action formatar(valor: Boolean):
    yield "sim" given valor otherwise "não"

assert formatar(3) is "3"  // Integer vence Float: e exato
assert formatar(2.5) is "2.50"
assert formatar(2.567, 1) is "2.6"
assert formatar(yes) is "sim"

blueprint Intervalo:
    inicio := 0
    fim := 0

    overload action setup(fim: Integer):
        self.fim := fim
    overload action setup(inicio: Integer, fim: Integer):
        self.inicio := inicio
        self.fim := fim

    action tamanho():
        yield self.fim - self.inicio

assert(spawn Intervalo(10)).tamanho() is 10
assert(spawn Intervalo(3, 10)).tamanho() is 7

// nenhuma variante aceita texto: a mensagem lista as que existem
monitor:
    formatar("dez")
    assert no
handle OverloadResolutionError as e:
    assert "formatar(valor: Integer)" in e.nota

// duas variantes igualmente boas: escolher pela ordem seria arbitrario
overload action juntar(a: Integer, b):
    yield "primeira"
overload action juntar(a, b: Integer):
    yield "segunda"
monitor:
    juntar(1, 2)
    assert no
handle AmbiguousOverloadError:
    out "empate recusado"
assert juntar(1, "x") is "primeira"

out "245 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/245_sobrecarga.df` },
  {"h3": "O que se pratica"},
  {"p": "`overload action` no topo e em construtor, a escolha por aridade e por tipo, e as recusas `OverloadResolutionError` e `AmbiguousOverloadError`."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. Numa linguagem dinâmica, sobrecarga é documentação que se cumpre.** Um `given typeof(valor)` faria o mesmo — e aceitaria qualquer coisa, falhando lá dentro. As variantes declaram as formas, e a chamada fora delas é recusada **com a lista das que existem** na nota."},
  {"p": "**2. O tipo exato vence o compatível.** Um `Integer` serve onde se pede `Float`. Sem essa regra `formatar(3)` empataria entre as duas primeiras variantes; com ela, vence a de `Integer`, que é a que quem escreveu quis."},
  {"p": "**3. Empate é erro, e não sorteio.** `juntar(1, 2)` cabe nas duas variantes com a mesma precisão. Escolher a primeira escrita faria mover uma variante de lugar mudar o resultado de um programa que não a chama. `juntar(1, \"x\")` não empata: só a primeira aceita texto em `b`."},
  {"p": "**4. Toda variante é marcada.** Misturar `action f` com `overload action f` é recusado — não há leitura em que as duas convivam."},
  {"h3": "Para ir além"},
  {"list": ["Acrescente `overload action formatar(valor: Integer, casas: Integer)`"]},
  {"p": "e descubra qual chamada existente passa a empatar."},
  {"h2": "246 · Uma metaclasse que registra, valida e audita"},
  {"p": "**Enunciado.** todo modelo de dominio precisa de 'id', ganha nome de tabela"},
  { code: `// automaticamente, e cada escrita de campo fica registrada.

adopt Arcane.Reflexo as R

meta blueprint Modelo:
    tabelas := {}
    escritas := []

    action on_forge(molde):
        campos := [c["nome"] cycle c in R.campos(molde)]
        given not("id" in campos):
            trigger $"{R.nome(molde)} precisa declarar 'id'"
        self.tabelas[R.nome(molde)] := R.nome(molde).lower() + "s"

    action on_write(obj, nome, valor):
        self.escritas.append($"{R.nome(obj)}.{nome}")

    action on_missing(obj, nome):
        yield void

blueprint Entidade using Modelo:
    id := 0

blueprint Cliente extends Entidade:
    nome := ""

blueprint Pedido extends Entidade:
    total := 0.0

meta_obj := R.meta_instancia(Pedido)
assert meta_obj.tabelas is {"Entidade": "entidades", "Cliente": "clientes", "Pedido": "pedidos"}

c := spawn Cliente()
c.nome := "Ana"
c.id := 7
assert meta_obj.escritas is ["Cliente.nome", "Cliente.id"]
assert c.telefone is void  // on_missing: campo opcional

// a validacao roda na DECLARACAO
monitor:
    blueprint SemId using Modelo:
        texto := ""
    assert no
handle Error as e:
    assert "precisa declarar 'id'" in e.message

// um gancho com nome errado nunca rodaria — por isso e recusado
monitor:
    meta blueprint Errada:
        action on_forje(m):
            yield void
    assert no
handle MetaclassError as e:
    assert "on_forge" in e.dica

out "246 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/246_metaclasses.df` },
  {"h3": "O que se pratica"},
  {"p": "`meta blueprint`, `using`, os ganchos `on_forge`, `on_write` e `on_missing`, a herança da metaclasse e `Reflexo.meta_instancia`."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. A metaclasse age sobre a CLASSE, uma vez, e sobre os OBJETOS, sempre.** `on_forge` roda quando `Cliente` é declarado; `on_write` roda em cada escrita de cada cliente. É por isso que a validação de `id` falha na declaração, antes de existir objeto nenhum."},
  {"p": "**2. Ela é herdada.** `Cliente` e `Pedido` não escrevem `using`, e são governados. Uma regra de domínio escrita uma vez vale para a família inteira — e uma filha não consegue escapar dela."},
  {"p": "**3. A metaclasse tem uma instância só.** `tabelas` e `escritas` são campos dessa instância, compartilhada por todos os modelos. É o `self` dos ganchos, e é onde um registro de classes naturalmente mora."},
  {"p": "**4. Nomes de gancho são fixos, e o errado é recusado.** Um `on_forje` nunca rodaria, e nada avisaria: a metaclasse pareceria ignorada. A recusa vem com a sugestão do nome certo."},
  {"p": "**5. Um gancho não dispara outro.** `R.campos(molde)` e `R.nome(obj)` dentro dos ganchos não caem em `on_read` — sem essa regra, auditar leituras seria recursão infinita."},
  {"h3": "Para ir além"},
  {"list": ["Acrescente `on_spawn` devolvendo um objeto já criado para o mesmo `id`"]},
  {"p": "e transforme o modelo num mapa de identidade."},
  {"h2": "247 · Um validador generico escrito com reflexao"},
  {"p": "**Enunciado.** valide qualquer objeto pelas anotacoes dos campos, sem que o"},
  { code: `// validador conheca o tipo — e confirme que a reflexao nao fura 'private'.

adopt Arcane.Reflexo as R

action Obrigatorio(alvo):
    yield void
action Tamanho(minimo, maximo):
    yield lambda alvo => void

blueprint Usuario:
    @Obrigatorio
    @Tamanho(3, 20)
    nome := ""

    @Obrigatorio
    email := ""

    private senha := "segredo"

    action saudar():
        yield "olá, " + self.nome

// O validador so conhece anotacoes, nunca 'Usuario'.
action validar(obj):
    problemas := []
    cycle campo in R.campos(obj):
        given campo["visibilidade"] isnt "public":
            skip
        valor := R.ler(obj, campo["nome"])
        cycle marca in campo["anotacoes"]:
            given marca["nome"] is "Obrigatorio" and valor is "":
                problemas.append($"{campo['nome']} é obrigatório")
            orif marca["nome"] is "Tamanho" and valor isnt "":
                minimo, maximo := marca["args"]
                given len(valor) smaller minimo or len(valor) bigger maximo:
                    problemas.append($"{campo['nome']} fora de {minimo}..{maximo}")
    yield problemas

u := spawn Usuario()
assert validar(u) is ["nome é obrigatório", "email é obrigatório"]
R.escrever(u, "nome", "Al")
R.escrever(u, "email", "al@x.com")
assert validar(u) is ["nome fora de 3..20"]
u.nome := "Alice"
assert validar(u) is []

// invocacao por nome
assert R.invocar(u, "saudar") is "olá, Alice"
assert R.tem(u, "saudar")
assert "senha" in [c["nome"] cycle c in R.campos(Usuario)]  // saber que existe…
monitor:
    R.ler(u, "senha")  // …nao e poder ler
    assert no
handle TypeError as e:
    assert "private" in e.message

// sugestao de nome parecido, como dado
assert R.sugerir(u, "sadar") is ["saudar"]

// o diagrama sai da mesma informacao
diagrama := R.diagrama([Usuario])
assert "-senha" in diagrama and "+saudar()" in diagrama

out "247 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/247_reflexao.df` },
  {"h3": "O que se pratica"},
  {"p": "Anotações em campo (`@Obrigatorio`, `@Tamanho(3, 20)`), `Reflexo.campos`, `ler`/`escrever`/`invocar` por nome, `sugerir` e `diagrama`."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. Em campo, o decorador é anotação.** `@Tamanho(3, 20)` não embrulha nada — não há valor para embrulhar na declaração. Ele grava nome e argumentos, e quem precisa lê: aqui, o validador."},
  {"p": "**2. O validador não conhece `Usuario`.** Ele pergunta ao tipo o que o tipo declara. É assim que ORM, serializador e formulário são escritos uma vez para todos os modelos — e é por isso que reflexão existe."},
  {"p": "**3. Saber que existe não é poder ler.** `R.campos` lista `senha` com a visibilidade ao lado, porque isso é documentação. `R.ler(u, \"senha\")` é recusado exatamente como `u.senha` seria: se a reflexão abrisse o que o autor fechou, `private` seria só uma sugestão para quem não conhece o módulo — e é justamente quem conhece que precisa ser contido."},
  {"p": "**4. Reflexão custa.** Cada leitura por texto passa pela busca completa de membro, visibilidade e ganchos. Use em framework e ferramenta; no laço quente, escreva `u.nome`."},
  {"h3": "Para ir além"},
  {"list": ["Acrescente `@Formato(\"email\")` e valide com `Arcane.Regex`.", "Gere o formulário HTML de `Usuario` a partir das mesmas anotações."]},
  {"h2": "248 · Copia, imutabilidade e serializacao que nao confia no dado"},
  {"p": "**Enunciado.** persista um pedido com cliente e itens (e um ciclo), recarregue"},
  { code: `// so os tipos esperados, e passe uma configuracao congelada adiante.

adopt Arcane.Objetos as O

blueprint Cliente(nome):
    pedidos := []
    private cpf := "000"

blueprint Item(produto, preco):
    quantidade := 1

blueprint Pedido(cliente):
    itens := []
    invariant len(self.itens) smaller_eq 50

    action total():
        yield sum([i.preco * i.quantidade cycle i in self.itens])

ana := spawn Cliente("Ana")
p := spawn Pedido(ana)
p.itens.append(spawn Item("caneta", 3.0))
p.itens.append(spawn Item("caderno", 12.5))
ana.pedidos.append(p)  // ciclo: cliente -> pedido -> cliente

// ── serializar ──
dado := O.para_vault(ana)
assert dado["$tipo"] is "Cliente"
assert not("cpf" in dado)  // private nao sai
assert dado["pedidos"][0]["cliente"]["$ref"] is dado["$id"]

texto := O.para_json(ana)
volta := O.de_json(texto, [Cliente, Pedido, Item])
assert volta.pedidos[0].total() is 15.5
assert volta.pedidos[0].cliente is volta  // o ciclo voltou como ciclo

// ── o dado nao escolhe o tipo ──
monitor:
    O.de_vault({"$tipo": "Administrador", "poderes": "todos"}, [Cliente, Pedido, Item])
    assert no
handle UnsafeDeserializationError:
    out "tipo nao autorizado: recusado"

// ── invariante conferida na chegada ──
itens_demais := [{"$tipo":"Item", "produto":"x", "preco":1} cycle i in range(60)]
monitor:
    O.de_vault({"$tipo": "Pedido", "itens": itens_demais}, [Pedido, Item])
    assert no
handle InvariantError:
    out "dado que viola a regra: recusado na chegada"

// ── copia e igualdade ──
copia := O.clonar_fundo(p)
copia.itens[0].quantidade := 10
assert p.itens[0].quantidade is 1
assert not O.igual(copia, p)
assert O.igual(O.clonar_fundo(p), p)

// ── congelar ──
blueprint Config:
    porta := 8080
    hosts := ["a"]
cfg := O.congelar(spawn Config())
monitor:
    cfg.porta := 80
    assert no
handle FrozenObjectError:
    out "config congelada"
editavel := O.clonar(cfg)
editavel.porta := 80
assert editavel.porta is 80 and cfg.porta is 8080

out "248 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/248_objetos_e_serializacao.df` },
  {"h3": "O que se pratica"},
  {"p": "`Objetos.para_vault`/`para_json` com ciclo, `de_vault`/`de_json` com lista de tipos, `clonar` e `clonar_fundo`, `igual` e `congelar`."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. O dado não escolhe o tipo.** `de_vault` exige a lista do que pode construir. Um JSON com `\"$tipo\": \"Administrador\"` é recusado com `UnsafeDeserializationError`. Em linguagens que deixaram o dado escolher, foi assim que desserialização virou execução de código alheio."},
  {"p": "**2. Ciclo não é recursão infinita.** O pedido aponta para o cliente, que aponta para o pedido. A segunda vez que um objeto aparece ele vira `{\"$ref\": n}`, e na volta a referência é religada: `volta.pedidos[0].cliente is volta`."},
  {"p": "**3. A reconstrução confere a invariante.** O `setup` não roda — ele pede argumentos que o dado não tem —, mas a regra do tipo vale: um pedido com 60 itens é recusado **na chegada**, e não três telas depois."},
  {"p": "**4. `private` não sai.** Serializar é publicar. `{\"privados\": yes}` inclui os campos fechados para persistência própria, e a escolha fica explícita."},
  {"p": "**5. Congelar é para sempre; a cópia não.** `clonar` de um objeto congelado devolve um objeto editável — é o jeito de mexer numa configuração que outra thread pode estar lendo."},
  {"h3": "Para ir além"},
  {"list": ["Declare `static versao_do_esquema := 2` em `Pedido` e escreva uma"]},
  {"p": "metaclasse com `on_deserialize` que migra o dado da versão 1."},
  {"h2": "249 · Portas, adaptadores e o conteiner"},
  {"p": "**Enunciado.** um caso de uso de cadastro que nao conhece banco nem e-mail,"},
  { code: `// montado por um conteiner — e trocado por dubles no teste.

adopt Arcane.Injecao as DI

// ── portas (o dominio) ──
contract Usuarios:
    action existe(email: String) -> Boolean
    action gravar(email: String)

contract Avisos:
    action enviar(para: String, texto: String)

blueprint Cadastro(usuarios: Usuarios, avisos: Avisos):
    action registrar(email: String):
        expects "@" in email, "e-mail invalido"
        given self.usuarios.existe(email):
            yield "ja existe"
        self.usuarios.gravar(email)
        self.avisos.enviar(email, "bem-vindo")
        yield "criado"

// ── adaptadores (a borda) ──
blueprint UsuariosMemoria with Usuarios:
    emails := []
    action existe(email: String) -> Boolean:
        yield email in self.emails
    action gravar(email: String):
        self.emails.append(email)

blueprint AvisosFalsos with Avisos:
    enviados := []
    action enviar(para: String, _texto: String):
        self.enviados.append(para)

// ── composicao: um lugar so ──
c := DI.conteiner()
c.unico(Usuarios, UsuariosMemoria)
c.unico(Avisos, AvisosFalsos)
c.transitorio(Cadastro)

cadastro := c.resolver(Cadastro)
assert cadastro.registrar("ana@x.com") is "criado"
assert cadastro.registrar("ana@x.com") is "ja existe"
assert c.resolver(Avisos).enviados is ["ana@x.com"]
assert c.conferir() is []

// ── o grafo que o conteiner monta ──
assert c.grafo()["Cadastro"] is ["Usuarios", "Avisos"]

// ── escopo: um por pedido ──
blueprint Transacao:
    aberta := yes
    action fechar():
        self.aberta := no

c.por_escopo(Transacao)
pedido := c.escopo("pedido 1")
t := pedido.resolver(Transacao)
assert t is pedido.resolver(Transacao)
pedido.fechar()
assert not t.aberta

// ── o que ele recusa ──
monitor:
    DI.conteiner().resolver(Cadastro)
    assert no
handle DependencyResolutionError as e:
    assert "Usuarios" in e.message

out "249 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/249_injecao_hexagonal.df` },
  {"h3": "O que se pratica"},
  {"p": "`contract` como porta, blueprint `with` como adaptador, `Arcane.Injecao` com `unico`, `transitorio`, `por_escopo`, `conferir` e `grafo`."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. O caso de uso não adota nada de fora.** `Cadastro` conhece dois contratos e zero implementações. Trocar SQLite por PostgreSQL, ou SMTP por uma fila, não muda uma linha dele — é a arquitetura hexagonal, e é o Princípio da Inversão de Dependência escrito em tipos."},
  {"p": "**2. O contêiner lê o que já estava escrito.** `usuarios: Usuarios` no cabeçalho é a dependência declarada; não há anotação `@Inject` nova. O contêiner resolve pelo tipo."},
  {"p": "**3. A composição mora num lugar só.** As quatro linhas de registro são o único ponto do programa que sabe quais adaptadores existem. No teste, são essas quatro linhas que mudam — e só elas."},
  {"p": "**4. `conferir()` no teste pega o registro que falta.** Um contêiner que só descobre a dependência sem registro quando a rota é chamada descobre em produção."},
  {"p": "**5. Por escopo é por pedido.** Uma transação por pedido HTTP, fechada no fim. Pedir uma dependência `por_escopo` ao contêiner raiz é recusado: ali ela viraria um único calado, e duas requisições dividiriam a transação."},
  {"h3": "Para ir além"},
  {"list": ["Registre `Usuarios` como `por_escopo` e `Cadastro` como `unico`, e leia"]},
  {"p": "a mensagem sobre dependência cativa."},
  {"h2": "250 · Padroes com mecanismo: comando, estado e especificacao"},
  {"p": "**Enunciado.** um editor de pedido com desfazer, um fluxo de aprovacao que"},
  { code: `// recusa transicao invalida, e regras de negocio combinaveis.

adopt Arcane.Padroes as P

// ── Command: desfazer e refazer ──
blueprint Carrinho:
    itens := []

blueprint Adicionar(carrinho, item):
    action executar():
        self.carrinho.itens.append(self.item)
    action desfazer():
        self.carrinho.itens.pop()

carrinho := spawn Carrinho()
historico := P.comandos()
historico.executar(spawn Adicionar(carrinho, "caneta"))
historico.executar(spawn Adicionar(carrinho, "caderno"))
historico.desfazer()
assert carrinho.itens is ["caneta"]
historico.refazer()
assert carrinho.itens is ["caneta", "caderno"]

// ── State: transicoes com guarda ──
fluxo := P.maquina("rascunho", {
        "enviar": {"de": ["rascunho"], "para": "em_analise",
            "guarda": lambda ctx => len(ctx.itens) bigger 0},
        "aprovar": {"de": ["em_analise"], "para": "aprovado"},
        "recusar": {"de": ["em_analise"], "para": "rascunho"},
    })
assert not fluxo.pode("aprovar")
fluxo.ir("enviar", carrinho)
fluxo.ir("recusar")
fluxo.ir("enviar", carrinho)
fluxo.ir("aprovar")
assert fluxo.historico is ["rascunho", "em_analise", "rascunho", "em_analise", "aprovado"]
monitor:
    fluxo.ir("enviar", carrinho)
    assert no
handle StateError:
    out "aprovado nao volta para analise"

// ── Specification + Repository ──
record Produto:
    id: Integer
    preco: Float
    estoque: Integer

repo := P.repositorio()
repo.salvar(Produto(1, 5.0, 10))
repo.salvar(Produto(2, 80.0, 0))
repo.salvar(Produto(3, 120.0, 3))

caro := P.especificacao(lambda p => p.preco bigger 50, "caro")
disponivel := P.especificacao(lambda p => p.estoque bigger 0, "disponivel")
vitrine := repo.filtrar(caro.e(disponivel))
assert [p.id cycle p in vitrine] is [3]
assert [p.id cycle p in repo.filtrar(caro.nao().ou(disponivel.nao()))] is [1, 2]

// ── Observer com prioridade ──
auditoria := []
eventos := P.observavel()
eventos.assinar(lambda d => auditoria.append("log"), 0)
eventos.assinar(lambda d => auditoria.append("seguranca"), 10)
eventos.notificar("pedido aprovado")
assert auditoria is ["seguranca", "log"]

out "250 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/250_padroes.df` },
  {"h3": "O que se pratica"},
  {"p": "`Padroes.comandos`, `Padroes.maquina` com guarda, `Padroes.especificacao` combinada, `Padroes.repositorio` e `Padroes.observavel` com prioridade."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. Metade do catálogo já é a linguagem.** Template Method é `abstract blueprint`; Strategy é um contrato com duas implementações; Decorator é `mark @…`. O módulo só traz os padrões que pedem **estado** — histórico de comandos, estado atual de uma máquina — que ninguém deveria reescrever."},
  {"p": "**2. A máquina recusa em vez de ignorar.** `fluxo.ir(\"enviar\")` num pedido aprovado é `StateError`, com a lista de onde o evento é permitido. Uma máquina que ignora evento inválido esconde exatamente o bug que ela existia para impedir."},
  {"p": "**3. A especificação é uma regra de negócio com nome.** `caro.e(disponivel)` lê como a frase do negócio, e cada peça se testa sozinha. O repositório recebe a regra, e não um `given` espalhado por quem lista produtos."},
  {"p": "**4. Prioridade decide a ordem; o registro não.** O ouvinte de segurança foi assinado depois e roda antes. Um observador que depende da ordem de assinatura quebra no dia em que alguém move um `adopt`."},
  {"h3": "Para ir além"},
  {"list": ["Faça o ouvinte de segurança devolver `\"parar\"` para um pedido suspeito,"]},
  {"p": "e veja o de log não receber o evento."},
  {"h2": "251 · Nascer, viver sob threads, e morrer limpo"},
  {"p": "**Enunciado.** um contador de acessos seguro sob concorrencia, um cache que"},
  { code: `// nao segura os objetos, e um recurso que se libera sozinho.

adopt Arcane.Memoria as Mem

// ── exclusive: o monitor do objeto ──
blueprint Contador:
    acessos := 0
    exclusive action registrar():
        atual := self.acessos
        self.acessos := atual + 1
    exclusive action registrar_dois():
        self.registrar()  // reentrante: nao espera por si
        self.registrar()

contador := spawn Contador()
parallel:
    thread:
        cycle i from 1 to 300:
            contador.registrar()
    thread:
        cycle i from 1 to 150:
            contador.registrar_dois()
    thread:
        cycle i from 1 to 300:
            contador.registrar()
assert contador.acessos is 900

// ── lazy: calcular uma vez por objeto ──
blueprint Relatorio(linhas):
    calculos := 0
    lazy get total():
        self.calculos += 1
        yield sum(self.linhas)

r := spawn Relatorio([1, 2, 3, 4])
assert r.total is 10 and r.total is 10
assert r.calculos is 1

// ── teardown: o recurso se libera quando o ultimo nome solta ──
liberados := []
blueprint Conexao(nome):
    action teardown():
        liberados.append(self.nome)

a := spawn Conexao("principal")
_outra := a
a := void
assert liberados is []  // '_outra' ainda segura
_outra := void
assert liberados is ["principal"]

// ── referencia fraca: o cache que nao vaza ──
cache := Mem.mapa_fraco()
sessao := spawn Conexao("sessao")
cache.definir(sessao, "dados caros de calcular")
assert cache.tamanho is 1
sessao := void
assert cache.tamanho is 0
assert "sessao" in liberados

// ── quantos existem ──
_lote := [spawn Conexao($"c{i}") cycle i in range(5)]
assert Mem.vivos(Conexao) is 5
_lote := void
assert Mem.vivos(Conexao) is 0

out "251 ok"`, lang: 'df', title: `exercicios/37-oop-sistema/251_ciclo_de_vida_e_concorrencia.df` },
  {"h3": "O que se pratica"},
  {"p": "`exclusive action` reentrante sob `parallel`, `lazy get`, `teardown`, `Memoria.mapa_fraco` e `Memoria.vivos`."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. Sem `exclusive`, o contador perde acessos, calado.** Ler, somar e escrever são três passos, e duas threads intercaladas somam o mesmo valor — a armadilha 14 do `CLAUDE.md` mediu 40.425 de 80.000. `exclusive` põe uma trava **por objeto**: dois contadores diferentes não esperam um pelo outro."},
  {"p": "**2. A trava é reentrante.** `registrar_dois` chama `registrar`, que também é exclusivo. Com uma trava simples a thread esperaria por si mesma para sempre."},
  {"p": "**3. `teardown` roda na hora, e não \"algum dia\".** O DataForge herda do CPython a contagem de referências: o objeto morre quando o último nome o solta. Enquanto `_outra` segurar a conexão, ela vive — é o que o assert do meio confere."},
  {"p": "**4. O cache com referência forte é o vazamento mais comum que existe.** `mapa_fraco` guarda o dado *enquanto* a sessão existir, sem ser a razão de ela existir. Soltar a sessão apaga a entrada."},
  {"p": "**5. Recurso importante fecha com `with` ou `defer`.** `teardown` depende de o último nome soltar o objeto; um objeto preso num ciclo espera o coletor. Para arquivo e conexão, o ponto de fechamento conhecido é melhor."},
  {"h3": "Para ir além"},
  {"list": ["Tire o `exclusive` de `registrar` e rode algumas vezes: o total muda.", "Rode `dataforge check` sem o `exclusive` e leia o aviso"]},
  {"p": "`escrita-concorrente`."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/37-oop-sistema/242_contratos_e_segregacao.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '242-contratos-pequenos-e-quem-depende-de-qual', text: "242 · Contratos pequenos, e quem depende de qual", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '243-o-que-cada-modificador-promete', text: "243 · O que cada modificador promete", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '244-de-quem-e-o-erro', text: "244 · De quem e o erro?", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '245-sobrecarga-que-diz-o-que-aceita', text: "245 · Sobrecarga que diz o que aceita", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '246-uma-metaclasse-que-registra-valida-e-audita', text: "246 · Uma metaclasse que registra, valida e audita", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '247-um-validador-generico-escrito-com-reflexao', text: "247 · Um validador generico escrito com reflexao", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '248-copia-imutabilidade-e-serializacao-que-nao-confia-no-dado', text: "248 · Copia, imutabilidade e serializacao que nao confia no dado", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '249-portas-adaptadores-e-o-conteiner', text: "249 · Portas, adaptadores e o conteiner", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '250-padroes-com-mecanismo-comando-estado-e-especificacao', text: "250 · Padroes com mecanismo: comando, estado e especificacao", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }, { id: '251-nascer-viver-sob-threads-e-morrer-limpo', text: "251 · Nascer, viver sob threads, e morrer limpo", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"37 · OOP como sistema"}
      description={"10 exercícios: ."}
      href={"/docs/exercicios/37-oop-sistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
