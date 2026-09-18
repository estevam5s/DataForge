// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "38 · Sistema de tipos",
  description: "3 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 38`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[252](#252-tipos-nomeados-alias-uniao-intersecao-refinamento-e-opaco)", "**Tipos nomeados: alias, uniao, intersecao, refinamento e opaco**", ""], ["[253](#253-generics-tipos-indexados-e-o-sistema-de-traits)", "**Generics, tipos indexados e o sistema de traits**", ""], ["[254](#254-tuplas-a-forma-de-tamanho-fixo)", "**Tuplas: a forma de tamanho fixo**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "252 · Tipos nomeados: alias, uniao, intersecao, refinamento e opaco"},
  { code: `// Um 'type' da nome a um tipo. As cinco formas sao a MESMA declaracao:
// o que muda e o que vem depois do ':='.
//
// A regra de ouro: tipo transparente CONFERE, tipo opaco EMBRULHA.

// ── alias: um nome para o que ja existe ──
type Id := Integer
type Ids := Cluster<Id>

x: Id := 7
lista: Ids := [1, 2, 3]

assert typeof(x) is "Integer"        // o alias nao cria tipo novo
assert len(lista) is 3

// o nome que a pessoa escreveu aparece na mensagem
monitor:
    errado: Id := "sete"
    assert no
handle TypeError as e:
    assert "Id" in e.message and "Integer" in e.message

// ── alias generico: uma funcao de tipo ──
type Par<T> := Cluster<T>

p: Par<Integer> := [1, 2]
assert len(p) is 2

monitor:
    misturado: Par<Integer> := [1, "dois"]
    assert no
handle TypeError as e:
    assert "Integer" in e.message

// ── uniao: um destes, e nada mais ──
type Json := String | Integer | Boolean | Void

a: Json := "oi"
b: Json := 3
c: Json := void
assert $"{a} {b} {c}" is "oi 3 void"

monitor:
    d: Json := [1]
    assert no
handle TypeError as e:
    assert "String" in e.message and "Integer" in e.message

// a uniao tambem vale sem nome, direto na anotacao
action tamanho(v: Integer | String) -> Integer:
    yield len($"{v}")

assert tamanho(42) is 2
assert tamanho("abc") is 3

// ── intersecao: os dois ao mesmo tempo ──
trait Serial:
    action serializar()

trait Ordenavel:
    action comparar(outro)

type Auditavel := Serial & Ordenavel

blueprint Lancamento extends Serial, Ordenavel:
    valor := 10
    action serializar():
        yield $"L{self.valor}"
    action comparar(outro):
        yield self.valor - outro.valor

blueprint Rascunho extends Serial:
    action serializar():
        yield "rascunho"

action registrar(item: Auditavel) -> String:
    yield item.serializar()

assert registrar(spawn Lancamento()) is "L10"

monitor:
    registrar(spawn Rascunho())          // so serializa: falta comparar
    assert no
handle TypeError as e:
    assert "Ordenavel" in e.message

// ── refinamento: o tipo com uma regra ──
type Positivo := Integer where valor bigger 0
type Email := String where "@" in valor

record Produto:
    nome: String
    preco: Positivo

action desconto(preco: Positivo, por_cento: Positivo) -> Positivo:
    yield preco - (preco * por_cento ~/ 100)

assert desconto(200, 10) is 180
assert Produto("caneta", 3).preco is 3

contato: Email := "ana@exemplo.com"
assert "@" in contato

// a regra vale na fronteira: campo, parametro e retorno
monitor:
    Produto("brinde", 0)
    assert no
handle TypeError as e:
    assert "Positivo" in e.message
    assert "valor bigger 0" in e.message   // a regra aparece na mensagem

monitor:
    desconto(100, 200)                     // devolveria -100
    assert no
handle TypeError as e:
    assert "return value" in e.message

// ── opaco: so nasce validado, e e nominal ──
opaque type Cpf := String where len(valor) is 11
opaque type Metros := Float where valor bigger_eq 0.0

documento := Cpf("12345678901")
distancia := Metros(2.5)

assert typeof(documento) is "Cpf"
assert documento.valor is "12345678901"    // o dado de dentro
assert $"{documento}" is "12345678901"     // texto, pelo valor
assert distancia.valor * 2 is 5.0
assert distancia bigger Metros(1.0)        // ordem, pelo valor

action cadastrar(quem: Cpf) -> String:
    yield quem.valor

assert cadastrar(documento) is "12345678901"

// um texto com onze digitos NAO e um Cpf: e isso que o opaco protege
monitor:
    cadastrar("12345678901")
    assert no
handle TypeError as e:
    assert "Cpf" in e.message

// e o construtor valida
monitor:
    Cpf("123")
    assert no
handle TypeError as e:
    assert "Cpf" in e.message

// igualdade e serializacao olham o valor de dentro
adopt Arcane.Serialization as S
adopt Arcane.Collections as C

outro := Cpf("12345678901")
assert documento is outro
assert S.to_json({"cpf": documento}) is "{\\"cpf\\": \\"12345678901\\"}"
assert len(C.set([documento, outro])) is 1

out "252 ok"`, lang: 'df', title: `exercicios/38-tipos/252_tipos_nomeados.df` },
  {"p": "`type` dá nome a um tipo. Cinco formas, uma declaração só: o que muda é o que vem depois do `:=`."},
  {"table": {"head": ["Forma", "Escreve-se", "O que promete"], "rows": [["alias", "`type Id := Integer`", "um nome para o mesmo tipo"], ["alias genérico", "`type Par<T> := Cluster<T>`", "uma função de tipo"], ["união", "`type Json := String \\", "Integer`", "um destes, e nada mais"], ["interseção", "`type Auditavel := Serial & Ordenavel`", "todos ao mesmo tempo"], ["refinamento", "`type Positivo := Integer where valor bigger 0`", "o tipo, com uma regra"], ["opaco", "`opaque type Cpf := String where len(valor) is 11`", "só nasce validado"]]}},
  {"h3": "Transparente confere, opaco embrulha"},
  {"p": "Um tipo transparente é uma **conferência**: `x: Positivo := 5` guarda o número 5, e `typeof(x)` responde `Integer`. Nada muda de forma, e por isso nada quebra — o valor continua sendo aceito onde um `Integer` é aceito."},
  {"p": "Um tipo opaco é um **valor**: `Cpf(\"12345678901\")` devolve um objeto que sabe o próprio nome. É o que torna o tipo **nominal**, e é o ponto todo — um texto com onze dígitos não é um `Cpf`:"},
  { code: `action cadastrar(quem: Cpf) -> String:
    yield quem.valor

cadastrar("12345678901")     // recusado: texto não é Cpf
cadastrar(Cpf("12345678901")) // aceito`, lang: 'df' },
  {"p": "Se o opaco fosse só uma conferência de formato, `cadastrar(senha)` passaria sem reclamar — e aí o tipo não protegeria de nada."},
  {"h3": "A regra roda na fronteira"},
  {"p": "`where valor bigger 0` é uma expressão comum, com `valor` ligado ao que está entrando. Ela é conferida na declaração, no parâmetro, no **retorno** e no campo. É por isso que `desconto(100, 200)` falha: a conta daria `-100`, e o retorno promete `Positivo`."},
  {"p": "A **base vem antes da regra**, sempre. `type Nome := String where len(valor) bigger 2` recebendo um número recusa por tipo — rodar `len` sobre um número daria uma mensagem sobre `len`, e não sobre o tipo que você escreveu."},
  {"h3": "O que o `check` prova antes de rodar"},
  {"p": "Sobre um **literal**, o analisador decide: `x: Positivo := -1` é acusado com `tipo-refinado` antes de a primeira linha rodar. Sobre um valor que vem de uma chamada, de um arquivo ou da rede, ele **cala** — um falso alarme ensina a desligar o analisador."},
  {"p": "Dentro de um `monitor` os erros viram avisos, que é o que você vê ao rodar o `check` neste exercício: as falhas aqui são de propósito."},
  {"h2": "253 · Generics, tipos indexados e o sistema de traits"},
  { code: `// O que um parametro de tipo faz, e o que ele NAO faz:
//
//   <T>              documenta a relacao entre entrada e saida
//   <T extends X>    documenta E cobra, no check e na execucao
//   Vetor<3>         o argumento e um VALOR, e o tamanho entra no tipo

adopt Arcane.Collections as C

// ── acao generica: um T, dois tipos ──
action primeiro<T>(xs: Cluster<T>) -> T:
    yield xs[0]

action maior<T extends Number>(a: T, b: T) -> T:
    yield a given a bigger b otherwise b

assert primeiro([1, 2, 3]) is 1
assert primeiro(["a", "b"]) is "a"
assert maior(2, 7) is 7
assert maior(1.5, 0.5) is 1.5

// o limite e cobrado; o parametro solto nao
monitor:
    maior("dois", "sete")
    assert no
handle TypeError as e:
    assert "Number" in e.message

// ── record generico: o argumento chega ao campo ──
record Caixa<T>:
    valor: T

record Par<A, B>:
    esquerda: A
    direita: B

action girar(p: Par<Integer, String>) -> Par<String, Integer>:
    yield Par(p.direita, p.esquerda)

assert Caixa(7).valor is 7
assert Caixa("oi").valor is "oi"

g := girar(Par(1, "um"))
assert g.esquerda is "um" and g.direita is 1

monitor:
    errada: Caixa<Integer> := Caixa("texto")
    assert no
handle TypeError as e:
    assert "Caixa<Integer>" in e.message
    assert "valor" in e.message           // o campo culpado aparece

// com limite, o record cobra na construcao
record Medida<T extends Number>:
    quanto: T
    action dobro():
        yield self.quanto * 2

assert Medida(2.5).dobro() is 5.0

monitor:
    Medida("dois")
    assert no
handle TypeError as e:
    assert "Number" in e.message

// ── enum generico ──
enum Talvez<T>:
    Nada
    Algo

action achar<T>(xs: Cluster<T>, alvo: T) -> Talvez<T>:
    cycle x in xs:
        given x is alvo:
            yield Talvez.Algo
    yield Talvez.Nada

assert achar([1, 2, 3], 2).name is "Algo"
assert achar([1], 9).name is "Nada"

// ── blueprint generico: a colecao de T aceita qualquer T ──
blueprint Pilha<T>:
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
assert len(p.itens) is 1

// cada instancia tem a sua colecao
outra := spawn Pilha()
assert len(outra.itens) is 0

// ── tipo indexado: o tamanho faz parte do tipo ──
type Vetor<N> := Cluster<Float> where len(valor) is N

action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0], a[1] + b[1]]

assert somar([1.0, 2.0], [3.0, 4.0]) is [4.0, 6.0]

v: Vetor<3> := [1.0, 2.0, 3.0]
assert len(v) is 3

monitor:
    curto: Vetor<3> := [1.0, 2.0]
    assert no
handle TypeError as e:
    assert "len(valor) is N" in e.message

// ── trait: exigencia, padrao e heranca ──
trait Legivel:
    action ler()                          // exigencia: sem corpo
    action descrever():                   // padrao: vem de graca
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
assert n.descrever() is "leio: oi"        // o padrao herdado do trait da mae

// quem implementa metade e recusado, e a mensagem diz de onde vem a exigencia
monitor:
    blueprint Meio extends Editavel:
        action escrever(x):
            yield x
    assert no
handle TraitContractError as e:
    assert "ler" in e.message
    assert "Legivel" in e.message         // quem exigiu, nao quem repassou

// ── trait generico, tipo e constante associados ──
trait Coletor:
    type Item := Any
    steady LIMITE := 3
    action pegar() -> Item

blueprint Fila extends Coletor:
    type Item := Integer                  // preenchido por quem implementa
    itens := [10, 20]
    action pegar() -> Item:
        yield self.itens[0]

f := spawn Fila()
assert f.pegar() is 10
assert Fila.LIMITE is 3
assert Fila.Item is "Integer"

// o tipo associado vale como qualquer anotacao
blueprint Errada extends Coletor:
    type Item := Integer
    action pegar() -> Item:
        yield "nao e numero"

monitor:
    (spawn Errada()).pegar()
    assert no
handle TypeError as e:
    assert "Integer" in e.message and "String" in e.message

// ── despacho dinamico: o metodo vem do objeto ──
trait Forma:
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
    cycle forma in formas:
        total += forma.area()
    yield total

assert round(somar_areas([spawn Quadrado(), spawn Circulo()]), 2) is 7.14

// e a intersecao cobra os dois lados de uma vez
trait Serial:
    action serializar()

type Auditavel := Serial & Forma

blueprint Lancamento extends Serial, Forma:
    action serializar():
        yield "L"
    action area():
        yield 1

action registrar(x: Auditavel) -> String:
    yield x.serializar()

assert registrar(spawn Lancamento()) is "L"

monitor:
    registrar(spawn Quadrado())           // tem area, nao tem serializar
    assert no
handle TypeError as e:
    assert "Serial" in e.message

out "253 ok"`, lang: 'df', title: `exercicios/38-tipos/253_genericos_e_traits.df` },
  {"p": "Três perguntas, e as respostas que este exercício demonstra."},
  {"h3": "1. O que um `<T>` promete?"},
  {"p": "Nada sobre o valor — e isso é de propósito. Ele descreve a **relação**: `action primeiro<T>(xs: Cluster<T>) -> T` diz que o que sai é do mesmo tipo do que estava dentro. É por isso que `primeiro([1,2,3])` e `primeiro([\"a\",\"b\"])` são os dois válidos."},
  {"p": "Com `extends`, o parâmetro passa a ser **verificável**, e então é verificado nas duas metades: o `check` acusa a chamada antes de rodar, e a execução confere o valor."},
  {"table": {"head": ["Forma", "Documenta", "Cobra"], "rows": [["`<T>`", "sim", "não"], ["`<T extends Number>`", "sim", "sim, nos dois lados"]]}},
  {"p": "Dentro da declaração, um `T extends Number` **é** um `Number`: é o que permite escrever `self.quanto * 2` sem o analisador reclamar."},
  {"h3": "2. Onde o argumento chega?"},
  {"p": "No **campo**. `Caixa<Integer>` recusa `Caixa(\"texto\")`, e a mensagem nomeia o campo culpado:"},
  { code: `field 'valor' of Caixa<Integer> in variable 'errada' declared as Integer but got String`, lang: 'text' },
  {"p": "Sem isso, o parâmetro viraria comentário — o tipo prometeria uma coisa e aceitaria outra."},
  {"p": "Uma coleção anotada com o parâmetro (`itens: Cluster<T> := []`) **não** guarda o conteúdo: `T` aceita qualquer coisa, e um `Pilha<T>` que recusasse `append(1)` não serviria para nada. Uma coleção com tipo concreto (`Cluster<Integer>`) continua guardando."},
  {"h3": "3. O tamanho pode fazer parte do tipo?"},
  {"p": "Pode, e é o que `Vetor<3>` faz. O argumento de um genérico pode ser um **número**, e ele entra na regra do tipo:"},
  { code: `type Vetor<N> := Cluster<Float> where len(valor) is N

action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0], a[1] + b[1]]`, lang: 'df' },
  {"p": "É a forma prática dos tipos dependentes: a ação passa a recusar uma coordenada de três casas na fronteira, e o `check` prova o erro de um literal antes de rodar."},
  {"h3": "Traits: exigência, padrão e herança"},
  {"p": "Um método **sem corpo** é exigência; **com corpo** é implementação padrão, que quem adota recebe. `trait Editavel extends Legivel` soma as duas coisas da mãe."},
  {"p": "A mensagem de quem implementa metade nomeia **quem declarou** a exigência (`Legivel`), e não quem a repassou (`Editavel`). Numa cadeia de traits, o nome errado manda procurar no arquivo errado."},
  {"p": "Um trait também declara:"},
  {"list": ["**tipo associado** — `type Item := Any`, preenchido por quem"]},
  {"p": "implementa (`type Item := Integer`) e conferido como qualquer anotação;"},
  {"list": ["**constante associada** — `steady LIMITE := 3`, que vira membro"]},
  {"p": "(`Fila.LIMITE`)."},
  {"p": "E para exigir dois traits ao mesmo tempo, a interseção: `type Auditavel := Serial & Forma`. Um objeto que tem só metade é recusado na fronteira, dizendo qual metade falta."},
  {"h2": "254 · Tuplas: a forma de tamanho fixo"},
  { code: `// Cluster e uma LISTA: itens do mesmo tipo, quantidade livre.
// Tuple e uma FORMA: uma casa por tipo, quantidade fixa, imutavel.
//
// O contorno antigo era um cluster de dois itens — que aceita tres,
// aceita zero, e nao promete nada sobre a casa 0.

adopt Arcane.Collections as C
adopt Arcane.Serialization as S

// ── a forma, e a ambiguidade unica ──
t := (1, "a")
assert typeof(t) is "Tuple"
assert len(t) is 2
assert t[0] is 1 and t[1] is "a" and t[-1] is "a"

x := (2 + 3) * 2                  // agrupamento, nao tupla
assert x is 10 and typeof(x) is "Integer"

um := (7,)                        // a virgula faz a tupla de um
vazia := ()
assert len(um) is 1 and len(vazia) is 0

// fatia de tupla continua tupla
assert typeof(t[0:1]) is "Tuple"

// ── tres tipos parecidos, tres promessas diferentes ──
assert typeof([1, 2]) is "Cluster"          // muda
assert typeof(freeze([1, 2])) is "Frozen"   // cluster congelado
assert typeof((1, 2)) is "Tuple"            // forma fixa

// ── imutavel: escrever e recusado, com o motivo ──
monitor:
    t[0] := 9
    assert no
handle TypeError as e:
    assert "immutable" in e.message

// ── igualdade estrutural, hash e uso como chave ──
a := (1, "x")
b := (1, "x")
grade := {}
grade[a] := "achei"

assert a is b
assert a isnt (1, "y")
assert grade[b] is "achei"
assert len(C.set([a, b])) is 1

// ── o tipo: a quantidade de argumentos E o tamanho ──
par: Tuple<Integer, String> := (1, "a")
assert par[1] is "a"

monitor:
    trocada: Tuple<Integer, String> := ("a", 1)
    assert no
handle TypeError as e:
    assert "place 0" in e.message              // a casa culpada

monitor:
    grande: Tuple<Integer, String> := (1, "a", 2)
    assert no
handle TypeError as e:
    assert "place(s)" in e.message             // o tamanho faz parte do tipo

// ── o retorno duplo, que antes exigia cluster ou vault ──
action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield (a ~/ b, a % b)

inteiro, resto := dividir(17, 5)
assert inteiro is 3 and resto is 2

monitor:
    action errada() -> Tuple<Integer, Integer>:
        yield (1, "dois")
    errada()
    assert no
handle TypeError as e:
    assert "return value" in e.message

// ── com alias, aninhada, em record e em colecao ──
type Coordenada := Tuple<Float, Float>
type Segmento := Tuple<Coordenada, Coordenada>

record Trecho:
    de: Coordenada
    para: Coordenada

s: Segmento := ((0.0, 0.0), (3.0, 4.0))
trecho := Trecho(s[0], s[1])
pares := [(1, "um"), (2, "dois")]

assert s[1][0] is 3.0
assert trecho.para[1] is 4.0
assert pares[1][1] is "dois"

action distancia(de: Coordenada, para: Coordenada) -> Float:
    yield ((para[0] - de[0]) ** 2 + (para[1] - de[1]) ** 2) ** 0.5

assert distancia(s[0], s[1]) is 5.0

monitor:
    ruim: Coordenada := (1.0, "dois")
    assert no
handle TypeError as e:
    assert "Coordenada" in e.message

// ── percorrer, pertencer, serializar ──
soma := 0
cycle item in (1, 2, 3):
    soma += item
assert soma is 6
assert 2 in (1, 2, 3)
assert S.to_json((1, "a")) is "[1, \\"a\\"]"    // JSON nao tem tupla: vira array

out "254 ok"`, lang: 'df', title: `exercicios/38-tipos/254_tuplas.df` },
  {"p": "`Cluster` é uma **lista**: itens do mesmo tipo, quantidade livre, e ela muda. `Tuple` é uma **forma**: uma casa por tipo, quantidade fixa, e ela não muda."},
  {"table": {"head": ["", "Muda?", "Conteúdo", "Serve para"], "rows": [["`Cluster`", "sim", "mesmo tipo, quantidade livre", "uma lista de coisas"], ["`Frozen`", "não", "mesmo tipo (`freeze([1, 2])`)", "um cluster que não muda mais"], ["`Tuple`", "não", "**um tipo por casa**", "par, coordenada, retorno duplo"]]}},
  {"h3": "A única ambiguidade: `(1)` não é tupla"},
  {"p": "`(1)` é o número 1 entre parênteses — sem isso, `(2 + 3) * 2` deixaria de ser 10. A tupla de um item se escreve `(7,)`, e a vazia, `()`."},
  {"h3": "O tamanho faz parte do tipo"},
  {"p": "Em `Tuple<Integer, String>`, a **quantidade de argumentos é o tamanho**. Uma tupla de três casas não é \"uma tupla com um item errado\": é outra forma, e a mensagem diz isso. Quando a posição é que está errada, o erro nomeia a casa (`place 0`)."},
  {"p": "É o tipo natural do retorno duplo:"},
  { code: `action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield (a ~/ b, a % b)

inteiro, resto := dividir(17, 5)`, lang: 'df' },
  {"p": "Antes, isso obrigava a devolver um cluster (que não promete duas casas) ou um vault (que obriga a nomear o que já tem ordem)."},
  {"h3": "Por que ela é hasheável"},
  {"p": "Porque é imutável. É isso que permite usá-la como **chave de vault** e dentro de um `Set` — e é a razão prática de a tupla existir ao lado do cluster. Um cluster não pode ser chave: ele mudaria, e a chave mudaria com ele."},
  {"h3": "Na fronteira do JSON"},
  {"p": "JSON não tem tupla: `to_json((1, \"a\"))` produz `[1, \"a\"]`, e o caminho de volta traz um `Cluster`. A forma não sobrevive ao formato — quando ela importa, declare `Tuple<…>` na entrada e converta ali."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/38-tipos/252_tipos_nomeados.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '252-tipos-nomeados-alias-uniao-intersecao-refinamento-e-opaco', text: "252 · Tipos nomeados: alias, uniao, intersecao, refinamento e opaco", level: 2 as const }, { id: 'transparente-confere-opaco-embrulha', text: "Transparente confere, opaco embrulha", level: 3 as const }, { id: 'a-regra-roda-na-fronteira', text: "A regra roda na fronteira", level: 3 as const }, { id: 'o-que-o-check-prova-antes-de-rodar', text: "O que o `check` prova antes de rodar", level: 3 as const }, { id: '253-generics-tipos-indexados-e-o-sistema-de-traits', text: "253 · Generics, tipos indexados e o sistema de traits", level: 2 as const }, { id: '1-o-que-um-t-promete', text: "1. O que um `<T>` promete?", level: 3 as const }, { id: '2-onde-o-argumento-chega', text: "2. Onde o argumento chega?", level: 3 as const }, { id: '3-o-tamanho-pode-fazer-parte-do-tipo', text: "3. O tamanho pode fazer parte do tipo?", level: 3 as const }, { id: 'traits-exigencia-padrao-e-heranca', text: "Traits: exigência, padrão e herança", level: 3 as const }, { id: '254-tuplas-a-forma-de-tamanho-fixo', text: "254 · Tuplas: a forma de tamanho fixo", level: 2 as const }, { id: 'a-unica-ambiguidade-1-nao-e-tupla', text: "A única ambiguidade: `(1)` não é tupla", level: 3 as const }, { id: 'o-tamanho-faz-parte-do-tipo', text: "O tamanho faz parte do tipo", level: 3 as const }, { id: 'por-que-ela-e-hasheavel', text: "Por que ela é hasheável", level: 3 as const }, { id: 'na-fronteira-do-json', text: "Na fronteira do JSON", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"38 · Sistema de tipos"}
      description={"3 exercícios: ."}
      href={"/docs/exercicios/38-tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
