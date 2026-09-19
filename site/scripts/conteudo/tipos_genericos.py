"""Generics, tipos indexados e o sistema de traits.

Todo bloco `df` destas páginas RODA e passa pelo `check`:
`tests/test_genericos.py` executa cada um. Documentação de sistema de
tipos que não roda é pior que nenhuma — o leitor copia a anotação.
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/tipos/genericos",
"title": "Generics",
"description": "<T> e <T extends X> em ação, blueprint, record, enum e trait: o que o parâmetro documenta, o que o limite cobra, e onde o argumento chega ao conteúdo.",
"blocos": [
 {"p": "Um parâmetro de tipo diz **qual é a relação** entre a entrada e a saída. `action primeiro<T>(xs: Cluster<T>) -> T` promete que o que sai é do mesmo tipo do que estava dentro — e é isso que uma assinatura sem `T` não consegue dizer."},

 {"table": {"head": ["Declaração", "Forma", "O que é cobrado"], "rows": [
   ["ação", "`action eco<T>(x: T) -> T`", "nada: `<T>` documenta"],
   ["ação com limite", "`action maior<T extends Number>(a: T, b: T)`", "`check` na chamada, e execução no valor"],
   ["blueprint", "`blueprint Pilha<T>`", "o conteúdo dos campos anotados com `T`"],
   ["record", "`record Caixa<T>`", "o campo, quando a anotação diz `Caixa<Integer>`"],
   ["enum", "`enum Talvez<T>`", "documenta a relação do valor que ele carrega"],
   ["trait", "`trait Comparavel<T>`", "documenta o que quem implementa recebe"],
   ["alias", "`type Par<T> := Cluster<T>`", "a substituição: `Par<Integer>` é `Cluster<Integer>`"]]}},

 {"h2": "Ação genérica"},
 {"p": "O `<T>` solto **não** é verificado, e isso é de propósito: ele existe para descrever a relação, e a linguagem é de tipagem dinâmica. O `<T extends X>` é verificável, e por isso é verificado nas duas metades — o `check` confere o argumento na chamada, e a execução confere o valor."},
 {"code": """action primeiro<T>(xs: Cluster<T>) -> T:
    yield xs[0]

action maior<T extends Number>(a: T, b: T) -> T:
    yield a given a bigger b otherwise b

assert primeiro([1, 2, 3]) is 1
assert primeiro(["a", "b"]) is "a"      // o mesmo T, outro tipo
assert maior(2, 7) is 7
assert maior(1.5, 0.5) is 1.5

monitor:
    maior("dois", "sete")               // String não é Number
    assert no
handle TypeError as e:
    assert "Number" in e.message""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Dentro do corpo, um T com limite É o limite", "texto": "`T extends Number` permite escrever `a bigger b` no corpo sem o analisador reclamar: para ele, ali dentro, `T` é um `Number`. É o que torna o limite útil, e não só decorativo."}},

 {"h2": "Record genérico"},
 {"p": "O parâmetro chega ao **campo**. Sem isso, `Caixa<Integer>` prometeria uma coisa e aceitaria outra — o parâmetro viraria comentário."},
 {"code": """record Caixa<T>:
    valor: T

record Par<A, B>:
    esquerda: A
    direita: B

action girar(p: Par<Integer, String>) -> Par<String, Integer>:
    yield Par(p.direita, p.esquerda)

c := Caixa(7)
assert c.valor is 7
assert typeof(c) is "Caixa"

g := girar(Par(1, "um"))
assert g.esquerda is "um" and g.direita is 1

monitor:
    errada: Caixa<Integer> := Caixa("texto")
    assert no
handle TypeError as e:
    assert "Caixa<Integer>" in e.message
    assert "valor" in e.message""", "lang": "df"},
 {"p": "Com limite, o record cobra na construção — e o `check` acusa antes, com o código `generic-bound`:"},
 {"code": """record Medida<T extends Number>:
    quanto: T
    action dobro():
        yield self.quanto * 2

assert Medida(2.5).dobro() is 5.0

monitor:
    Medida("dois")
    assert no
handle TypeError as e:
    assert "Number" in e.message""", "lang": "df"},

 {"h2": "Enum genérico"},
 {"p": "Um enum genérico descreve o tipo que os membros carregam. É como se escreve um resultado sem inventar dois records:"},
 {"code": """enum Talvez<T>:
    Nada
    Algo

action achar<T>(xs: Cluster<T>, alvo: T) -> Talvez<T>:
    cycle x in xs:
        given x is alvo:
            yield Talvez.Algo
    yield Talvez.Nada

assert achar([1, 2, 3], 2).name is "Algo"
assert achar([1], 9).name is "Nada" """, "lang": "df"},

 {"h2": "Blueprint genérico"},
 {"code": """blueprint Pilha<T>:
    itens: Cluster<T> := []

    action por(x):
        self.itens.append(x)
        yield self

    action tirar():
        yield self.itens.pop(len(self.itens) - 1)

p := spawn Pilha()
p.por(1)
p.por(2)
assert p.tirar() is 2
assert len(p.itens) is 1""", "lang": "df"},

 {"h3": "A anotação `Caixa<Integer>`, e o que ela cobra"},
 {"p": "Anotar a variável **vincula** o parâmetro de tipo, e daí em diante a conferência tem contra o que comparar."},
 {"code": """blueprint Caixa<T>(valor: T):
    action guardar(v: T):
        self.valor := v
    action ler() -> T:
        yield self.valor

// A anotacao vincula T, e a fronteira confere o conteudo
inteira: Caixa<Integer> := spawn Caixa(7)
assert inteira.ler() is 7

monitor:
    errada: Caixa<Integer> := spawn Caixa("texto")
    assert no
handle TypeError as e:
    assert "field 'valor' of Caixa<Integer>" in e.message
    assert "declared as Integer but got String" in e.message

out "o vinculo e cobrado na fronteira" """, "lang": "df"},
 {"p": "A conferência olha os campos do cabeçalho **e** do corpo, **e os herdados** — um campo que vem da mãe é tão declarado quanto um próprio, e a mãe é quem costuma declarar o genérico."},
 {"table": {"head": ["Onde", "O que é cobrado"], "rows": [
   ["a fronteira (a atribuição anotada)", "todo campo cujo tipo declarado é um parâmetro, inclusive o herdado"],
   ["o `check`, na chamada de método", "`c.guardar(\"texto\")` com `c: Caixa<Integer>` — acusado **na linha que causa**, com o código `generic-argument`"],
   ["a execução, com limite", "`<T extends Number>` é cobrado no valor, com ou sem anotação"],
   ["a aridade dos argumentos", "`Caixa<Integer, String>` num `<T>` é recusado na leitura"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Por que o `check` importa aqui: o erro aparecia no lugar errado", "texto": "Um parâmetro de `T` **sem limite** não é conferido em execução. O campo recebia o texto calado, e a queixa saía na leitura seguinte — *\"a variável 'n' declared as Integer but got String\"*, uma linha depois e sobre **outro nome**. Quem lê a mensagem vai depurar o `n`, que está certo."}},
 {"callout": {"tipo": "perigo", "titulo": "Três defeitos moravam atrás desta anotação", "texto": "Ela era **erro de sintaxe**: `parse_blueprint` lia os parâmetros de tipo e não os registrava — `record`, `enum`, `trait` e `type` registravam, só o blueprint não, e a mensagem sugeria escrever `type Caixa<T> := …`, que é o caminho errado. O ramo de blueprint da conferência era **código morto**, lendo um atributo que nunca existiu. E escrever o argumento de tipo **desligava** a conferência de membro: `p: Par<Integer, String>` e depois `p.naoExiste` passava limpo — escrever **mais** informação de tipo comprava **menos** verificação."}},

 {"h3": "O limite: o objeto não carrega o vínculo"},
 {"p": "O vínculo vive na **anotação**, não na instância. Uma escrita posterior em campo com um valor que o analisador não consegue ver não é conferida:"},
 {"code": """blueprint Caixa<T>:
    guardado: T

action de_fora():
    yield "texto"

c: Caixa<Integer> := spawn Caixa()
c.guardado := de_fora()        // passa: o vinculo nao viaja com o objeto
assert c.guardado is "texto"
out "e um silencio, e ele esta escrito" """, "lang": "df"},
 {"p": "Fazer o objeto carregar o vínculo custaria estado **por instância**, e a linguagem trata isso como uma decisão de [custo zero](/docs/ecossistema/principios): contrato, invariante e estado por objeto vivem atrás de três sentinelas `None` justamente para não cobrar de quem não usa. O silêncio está nomeado em [o que falta](/docs/ecossistema/mapa) em vez de escondido."},

 {"h2": "Tipos indexados: quando o parâmetro é um número"},
 {"p": "`Vetor<3>` é um tipo cujo **argumento é um valor**. O parâmetro entra na regra do tipo, e o tamanho passa a fazer parte dele: é a forma prática dos tipos dependentes, e resolve o problema real de \"esta ação só aceita coordenada de duas casas\"."},
 {"code": """type Vetor<N> := Cluster<Float> where len(valor) is N

action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0], a[1] + b[1]]

assert somar([1.0, 2.0], [3.0, 4.0]) is [4.0, 6.0]

v: Vetor<3> := [1.0, 2.0, 3.0]
assert len(v) is 3

monitor:
    curto: Vetor<3> := [1.0, 2.0]
    assert no
handle TypeError as e:
    assert "len(valor) is N" in e.message""", "lang": "df"},
 {"p": "O `check` prova o tamanho de um **literal** antes de rodar: `v: Vetor<3> := [1.0, 2.0]` é acusado com `tipo-refinado`. O valor que vem de uma chamada não é — e essa é a linha entre verificar e adivinhar."},

 {"h2": "O que não existe"},
 {"table": {"head": ["Não existe", "Por quê"], "rows": [
   ["monomorfização", "não há compilação para código de máquina: o DataForge interpreta a árvore, e o genérico é uma conferência na fronteira"],
   ["especialização por tipo (`impl<Integer>`)", "exigiria despacho por tipo em tempo de compilação; o caminho aqui é sobrecarga (`overload`), que decide na chamada"],
   ["variância declarada (`covariant`/`contravariant`)", "**não se aplica** — e isso foi medido. A conferência é estrutural sobre os valores reais em cada fronteira, então ela já dá a resposta certa: `Caixa<Integer>` passa numa anotação `Caixa<Number>` e é recusada numa `Caixa<String>`. Uma palavra de variância não teria o que decidir, e seria a oitava reservada removida por ser cara sem entregar nada"],
   ["`<T>` cobrado sem limite", "de propósito — o parâmetro solto documenta, e cobrar o que não foi declarado seria inventar uma regra que o código não escreveu"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/tipos/traits",
"title": "Sistema de traits",
"description": "Traits com implementação padrão, herança entre traits, tipos e constantes associados, interseção, despacho dinâmico e o que a linguagem cobra de quem implementa.",
"blocos": [
 {"p": "Um `trait` descreve **o que um objeto sabe fazer**. Um método sem corpo é exigência; um método com corpo é implementação padrão, que quem adota recebe de graça."},
 {"code": """trait Legivel:
    action ler()                       // exigência
    action descrever():                // padrão: vem junto
        yield $"leio: {self.ler()}"

blueprint Documento extends Legivel:
    conteudo := "vazio"
    action ler():
        yield self.conteudo

d := spawn Documento()
assert d.ler() is "vazio"
assert d.descrever() is "leio: vazio" """, "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Trait ou contract?", "texto": "`trait` pode trazer implementação; `contract` só declara, confere a aridade de quem implementa e pode estender outros contratos. Quando você quer só a forma, use `contract`; quando quer forma **e** comportamento padrão, use `trait`."}},

 {"h3": "A prova de que a variância não tem o que decidir"},
 {"code": """blueprint Caixa<T>(valor: T):
    action ler() -> T:
        yield self.valor

inteira: Caixa<Integer> := spawn Caixa(7)

// Covariancia, de graca: um Integer E um Number
larga: Caixa<Number> := inteira
assert larga.ler() is 7

// E o incompativel e recusado — sem nenhuma declaracao de variancia
monitor:
    errada: Caixa<String> := inteira
    assert no
handle TypeError as e:
    assert "declared as String but got Integer" in e.message

out "a conferencia estrutural ja responde assignability" """, "lang": "df"},
 {"p": "O preço da escolha estrutural, nomeado: ela custa uma passada pelos campos **em cada atribuição anotada**, e não decide nada antes de rodar para um valor que o analisador não vê. Um sistema nominal decide estaticamente e de graça — e precisa da declaração de variância para isso."},

 {"h2": "Um trait herda de outro"},
 {"p": "`trait Editavel extends Legivel` soma as exigências e as implementações padrão. A mensagem de quem não implementa aponta **onde a exigência nasceu**, e não quem a repassou — numa cadeia de traits, o nome errado manda procurar no arquivo errado."},
 {"code": """trait Legivel:
    action ler()
    action descrever():
        yield $"leio: {self.ler()}"

trait Editavel extends Legivel:
    action escrever(x)

blueprint Nota extends Editavel:
    texto := ""
    action ler():
        yield self.texto
    action escrever(x):
        self.texto := x

n := spawn Nota()
n.escrever("oi")
assert n.ler() is "oi"
assert n.descrever() is "leio: oi" """, "lang": "df"},
 {"p": "Quem implementa só metade é recusado **na declaração**, e a mensagem diz de onde vem a exigência:"},
 {"code": """trait Legivel:
    action ler()

trait Editavel extends Legivel:
    action escrever(x)

monitor:
    blueprint Meio extends Editavel:
        action escrever(x):
            yield x
    assert no
handle TraitContractError as e:
    assert "ler" in e.message
    assert "Legivel" in e.message        // quem exigiu, não quem repassou""", "lang": "df"},

 {"h2": "Tipo associado e constante associada"},
 {"p": "Um trait pode declarar um **tipo** que quem implementa preenche, e uma **constante** que todos compartilham. O tipo associado é usado nas anotações dos métodos, e é conferido em execução como qualquer anotação."},
 {"code": """trait Coletor:
    type Item := Any                   // tipo associado
    steady LIMITE := 3                 // constante associada
    action pegar() -> Item

blueprint Fila extends Coletor:
    type Item := Integer               // preenchido aqui
    itens := [1, 2]
    action pegar() -> Item:
        yield self.itens[0]

f := spawn Fila()
assert f.pegar() is 1
assert Fila.LIMITE is 3
assert Fila.Item is "Integer" """, "lang": "df"},
 {"code": """trait Coletor:
    type Item := Any
    action pegar() -> Item

blueprint Errada extends Coletor:
    type Item := Integer
    action pegar() -> Item:
        yield "nao e numero"

monitor:
    (spawn Errada()).pegar()
    assert no
handle TypeError as e:
    assert "Integer" in e.message and "String" in e.message""", "lang": "df"},

 {"h2": "Trait genérico"},
 {"code": """trait Comparavel<T>:
    action comparar(outro: T) -> Integer

blueprint Dinheiro extends Comparavel:
    valor := 0
    action comparar(outro: Dinheiro) -> Integer:
        yield self.valor - outro.valor

a := spawn Dinheiro()
b := spawn Dinheiro()
b.valor := 5
assert a.comparar(b) is -5""", "lang": "df"},

 {"h2": "Exigir dois traits ao mesmo tempo"},
 {"p": "A interseção de tipos (`&`) é o que diz \"precisa saber as duas coisas\" sem inventar um trait novo só para juntá-las. Ver [tipos nomeados](/docs/tipos-nomeados)."},
 {"code": """trait Serial:
    action serializar()

trait Ordenavel:
    action comparar(outro)

type Auditavel := Serial & Ordenavel

blueprint Lancamento extends Serial, Ordenavel:
    valor := 7
    action serializar():
        yield $"L{self.valor}"
    action comparar(outro):
        yield self.valor - outro.valor

action registrar(x: Auditavel) -> String:
    yield x.serializar()

assert registrar(spawn Lancamento()) is "L7" """, "lang": "df"},

 {"h2": "Despacho: dinâmico por padrão"},
 {"p": "A chamada de método resolve pelo objeto, em execução, subindo a linhagem (C3, como o `super()` do Python). Não há vtable a declarar nem `virtual` a escrever: **todo** método é despachado assim."},
 {"table": {"head": ["Pergunta", "Resposta no DataForge"], "rows": [
   ["despacho dinâmico", "sim, sempre: o método vem do objeto"],
   ["despacho estático", "não existe como escolha — o analisador resolve o **nome** antes de rodar, mas a chamada é dinâmica"],
   ["vtable", "não há tabela declarável: a busca usa a linhagem e um cache de método por blueprint"],
   ["trait object", "um parâmetro anotado com o trait já é isso: qualquer objeto que o implemente serve"],
   ["`root`", "chama a implementação de quem **declarou** o método em execução, resolvendo o diamante por C3"]]}},
 {"code": """trait Forma:
    action area()

blueprint Quadrado extends Forma:
    lado := 2
    action area():
        yield self.lado ** 2

blueprint Circulo extends Forma:
    raio := 1
    action area():
        yield 3.14 * self.raio ** 2

action somar_areas(formas: Cluster<Forma>) -> Float:
    total := 0.0
    cycle f in formas:
        total += f.area()          // despacho dinâmico
    yield total

assert round(somar_areas([spawn Quadrado(), spawn Circulo()]), 2) is 7.14""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O que o trait NÃO faz", "texto": "Ele não declara campo obrigatório nem construtor. O que ele cobra é método e propriedade — e quem implementa decide como guardar o estado. Um trait que exigisse campo obrigaria um layout, e aí seria herança com outro nome."}},
]},
]
