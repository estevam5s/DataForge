// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "38 · Sistema de tipos",
  description: "5 exercícios: alias, união, refinamento, opaco, generics, tuplas e posse.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Sistemas e arquitetura** · alias, união, refinamento, opaco, generics, tuplas e posse · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 38`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[252](#252-tipos-nomeados-alias-uniao-intersecao-refinamento-e-opaco)", "**Tipos nomeados: alias, uniao, intersecao, refinamento e opaco**", ""], ["[253](#253-generics-tipos-indexados-e-o-sistema-de-traits)", "**Generics, tipos indexados e o sistema de traits**", ""], ["[254](#254-tuplas-a-forma-de-tamanho-fixo)", "**Tuplas: a forma de tamanho fixo**", ""], ["[255](#255-a-falha-como-valor-e-a-reflexao-de-tipos)", "**A falha como valor, e a reflexao de tipos**", ""], ["[256](#256-posse-emprestimo-e-liberacao-deterministica)", "**Posse, emprestimo e liberacao deterministica**", ""]]}},
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

assert typeof(x) is "Integer"  // o alias nao cria tipo novo
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
    registrar(spawn Rascunho())  // so serializa: falta comparar
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
    assert "valor bigger 0" in e.message  // a regra aparece na mensagem

monitor:
    desconto(100, 200)  // devolveria -100
    assert no
handle TypeError as e:
    assert "return value" in e.message

// ── opaco: so nasce validado, e e nominal ──
opaque type Cpf := String where len(valor) is 11
opaque type Metros := Float where valor bigger_eq 0.0

documento := Cpf("12345678901")
distancia := Metros(2.5)

assert typeof(documento) is "Cpf"
assert documento.valor is "12345678901"  // o dado de dentro
assert $"{documento}" is "12345678901"  // texto, pelo valor
assert distancia.valor * 2 is 5.0
assert distancia bigger Metros(1.0)  // ordem, pelo valor

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
assert S.to_json({"cpf": documento}) is '{"cpf": "12345678901"}'
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
    assert "valor" in e.message  // o campo culpado aparece

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
    action ler()  // exigencia: sem corpo
    action descrever():  // padrao: vem de graca
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
assert n.descrever() is "leio: oi"  // o padrao herdado do trait da mae

// quem implementa metade e recusado, e a mensagem diz de onde vem a exigencia
monitor:
    blueprint Meio extends Editavel:
        action escrever(x):
            yield x
    assert no
handle TraitContractError as e:
    assert "ler" in e.message
    assert "Legivel" in e.message  // quem exigiu, nao quem repassou

// ── trait generico, tipo e constante associados ──
trait Coletor:
    type Item := Any
    steady LIMITE := 3
    action pegar() -> Item

blueprint Fila extends Coletor:
    type Item := Integer  // preenchido por quem implementa
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
    registrar(spawn Quadrado())  // tem area, nao tem serializar
    assert no
handle TypeError as e:
    assert "Serial" in e.message

// ── A anotacao generica de um blueprint proprio ──────────────
//
// 'Guarda<Integer>' era ERRO DE SINTAXE, e tres defeitos moravam atras
// disso: o parser nao registrava os parametros de tipo do blueprint (os
// quatro irmaos registram), o ramo de blueprint da conferencia lia um
// atributo que nunca existiu — codigo morto —, e escrever o argumento
// de tipo DESLIGAVA a conferencia de membro.

blueprint Guarda<T>(guardado: T):
    action guardar(v: T):
        self.guardado := v
    action ler() -> T:
        yield self.guardado

// A anotacao vincula T, e a fronteira confere o conteudo
inteira: Guarda<Integer> := spawn Guarda(7)
assert inteira.ler() is 7

monitor:
    errada: Guarda<Integer> := spawn Guarda("texto")
    assert no
handle TypeError as e:
    assert "field 'guardado' of Guarda<Integer>" in e.message
    assert "declared as Integer but got String" in e.message

// O campo HERDADO conta: quem declara o generico costuma ser a mae
blueprint Raiz<T>:
    do_pai: T

blueprint Dupla<T> extends Raiz:
    proprio: T

d := spawn Dupla()
d.do_pai := "texto"
monitor:
    conferida: Dupla<Integer> := d
    assert no
handle TypeError as e:
    assert "field 'do_pai'" in e.message

// E um campo AINDA SEM VALOR nao da falso alarme: recusar 'void' aqui
// proibiria 'spawn Dupla()', que e a forma mais comum de criar um.
vazia: Dupla<Integer> := spawn Dupla()
vazia.proprio := 1
assert vazia.proprio is 1

// ── Variancia: ela nao tem o que decidir aqui ───────────────
//
// A conferencia e ESTRUTURAL sobre os valores reais em cada fronteira.
// Por isso ela ja da covariancia correta de graca...
larga: Guarda<Number> := inteira
assert larga.ler() is 7

// ...e recusa o incompativel, sem nenhuma palavra 'covariant'.
monitor:
    trocada: Guarda<String> := inteira
    assert no
handle TypeError as e:
    assert "declared as String but got Integer" in e.message

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

x := (2 + 3) * 2  // agrupamento, nao tupla
assert x is 10 and typeof(x) is "Integer"

um := (7,)  // a virgula faz a tupla de um
vazia := ()
assert len(um) is 1 and len(vazia) is 0

// fatia de tupla continua tupla
assert typeof(t[0:1]) is "Tuple"

// ── tres tipos parecidos, tres promessas diferentes ──
assert typeof([1, 2]) is "Cluster"  // muda
assert typeof(freeze([1, 2])) is "Frozen"  // cluster congelado
assert typeof((1, 2)) is "Tuple"  // forma fixa

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
assert a isnt(1, "y")
assert grade[b] is "achei"
assert len(C.set([a, b])) is 1

// ── o tipo: a quantidade de argumentos E o tamanho ──
par: Tuple<Integer, String> := (1, "a")
assert par[1] is "a"

monitor:
    trocada: Tuple<Integer, String> := ("a", 1)
    assert no
handle TypeError as e:
    assert "place 0" in e.message  // a casa culpada

monitor:
    grande: Tuple<Integer, String> := (1, "a", 2)
    assert no
handle TypeError as e:
    assert "place(s)" in e.message  // o tamanho faz parte do tipo

// ── o retorno duplo, que antes exigia cluster ou vault ──
action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield(a ~/ b, a % b)

inteiro, resto := dividir(17, 5)
assert inteiro is 3 and resto is 2

monitor:
    action errada() -> Tuple<Integer, Integer>:
        yield(1, "dois")
    errada()
    assert no
handle TypeError as e:
    assert "return value" in e.message

// ── com alias, aninhada, em record e em colecao ──
type Coordenada := Tuple < Float, Float >
type Segmento := Tuple < Coordenada, Coordenada >

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
    yield((para[0] - de[0]) ** 2 + (para[1] - de[1]) ** 2) ** 0.5

assert distancia(s[0], s[1]) is 5.0

monitor:
    ruim: Coordenada := (1.0, "dois")
    assert no
handle TypeError as e:
    assert "Coordenada" in e.message

// ── percorrer, pertencer, serializar ──
soma := 0
cycle item in(1, 2, 3):
    soma += item
assert soma is 6
assert 2 in(1, 2, 3)
assert S.to_json((1, "a")) is '[1, "a"]'  // JSON nao tem tupla: vira array

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
  {"h2": "255 · A falha como valor, e a reflexao de tipos"},
  { code: `// Tres formas de lidar com o que da errado, e a pergunta de cada uma:
//
//   monitor/handle/trigger   o que NAO era esperado: interrompe
//   void com ?? e ?.         a ausencia simples: segue com um padrao
//   Arcane.Resultado         a falha ESPERADA: vira valor, e quem
//                            chama decide

adopt Arcane.Resultado as R
adopt Arcane.Tipos as Tipos

// ── ok e falha ──
action buscar(id) -> Resultado:
    given id smaller 0:
        yield R.falha("id negativo", 400)
    yield R.ok({"id": id, "nome": "Ana"})

achado := buscar(7)
perdido := buscar(-1)

assert achado.deu_certo()
assert achado.valor()["nome"] is "Ana"
assert perdido.falhou()
assert perdido.erro() is "id negativo"
assert perdido.detalhe() is 400
assert perdido.ou("ninguem") is "ninguem"  // 'ou' nunca levanta

// ler o valor de uma falha e uma AFIRMACAO, e ela levanta
monitor:
    perdido.valor()
    assert no
handle RuntimeError as e:
    assert "id negativo" in e.message

// com a sua propria mensagem
monitor:
    perdido.exigir("o cliente nao existe")
    assert no
handle RuntimeError as e:
    assert e.message is "o cliente nao existe"

// ── a falha atravessa a corrente, intacta ──
action dobro(x):
    yield R.ok(x * 2)

assert R.ok(2).mapear(lambda x => x + 1).valor() is 3
assert R.ok(2).entao(dobro).valor() is 4
assert R.falha("parou").mapear(lambda x => x + 1).erro() is "parou"
assert R.falha("parou").entao(dobro).erro() is "parou"
assert R.falha("parou").recuperar(lambda motivo => R.ok(0)).valor() is 0

// ── tentar: o erro da linguagem vira valor ──
action dividir(a, b):
    yield a / b

assert R.tentar(dividir, 10, 2).valor() is 5.0
quebrou := R.tentar(dividir, 1, 0)
assert quebrou.falhou() and "zero" in quebrou.erro()

// ── todos: a lista pronta, ou o primeiro motivo ──
assert R.todos([R.ok(1), R.ok(2), R.ok(3)]).valor() is [1, 2, 3]
assert R.todos([R.ok(1), R.falha("cpf"), R.falha("email")]).erro() is "cpf"
assert R.erros([R.ok(1), R.falha("cpf"), R.falha("email")]) is ["cpf", "email"]

// ── Talvez: onde void e ambiguo ──
config := {"tema": void}
tem := R.chave(config, "tema")
nao := R.chave(config, "idioma")

assert tem.tem() and tem.valor() is void  // esta la, e vale void
assert not nao.tem()  // nao esta la
assert nao.ou("pt-BR") is "pt-BR"
assert R.primeiro([1, 2, 3], lambda x => x bigger 2).valor() is 3
assert not R.primeiro([1, 2], lambda x => x bigger 9).tem()

// ── reflexao: os metadados de um 'type' ──
type Positivo := Integer where valor bigger 0
type Json := String | Integer
opaque type Cpf := String where len(valor) is 11

assert Tipos.de("Json")["especie"] is "uniao"
assert Tipos.de("Positivo")["especie"] is "refinamento"
assert Tipos.de("Positivo")["regra"] is "valor bigger 0"
assert Tipos.de("Cpf")["opaco"]
assert Tipos.de("NaoExiste") is void

// conferir sem levantar
assert Tipos.satisfaz(5, "Positivo")
assert not Tipos.satisfaz(-5, "Positivo")
assert not Tipos.satisfaz("texto", "Positivo")  // a base decide primeiro
assert not Tipos.satisfaz("12345678901", "Cpf")  // opaco e nominal

// a forma ESTRUTURAL, que 'typeof' nao da
assert typeof([1, 2]) is "Cluster"
assert Tipos.forma([1, 2]) is "Cluster<Integer>"
assert Tipos.forma([1, "a"]) is "Cluster<Any>"  // misturado: Any, nao o primeiro
assert Tipos.forma((1, "a")) is "Tuple<Integer, String>"
assert Tipos.forma({"a": 1}) is "Vault<String, Integer>"

// ── juntando as duas: um validador generico ──
record Pedido:
    quantidade: Positivo
    contato: String

action validar(vault, esperado) -> Resultado:
    problemas := []
    cycle campo in esperado:
        given not Tipos.satisfaz(vault[campo] ?? void, esperado[campo]):
            problemas.append($"{campo} nao e {esperado[campo]}")
    yield R.falha(problemas) given len(problemas) bigger 0 otherwise R.ok(vault)

esperado := {"quantidade": "Positivo", "contato": "String"}

assert validar({"quantidade": 2, "contato": "ana@x.com"}, esperado).deu_certo()

ruim := validar({"quantidade": 0, "contato": 7}, esperado)
assert ruim.falhou()
assert len(ruim.erro()) is 2

// os campos de um record, com o tipo de cada um
p := Pedido(3, "ana@x.com")
campos := Tipos.campos(p)
assert campos["quantidade"]["tipo"] is "Positivo"
assert campos["contato"]["valor"] is "ana@x.com"

out "255 ok"`, lang: 'df', title: `exercicios/38-tipos/255_resultado_e_reflexao.df` },
  {"h3": "Três formas, três perguntas"},
  {"table": {"head": ["Forma", "Quando", "O que acontece"], "rows": [["`monitor`/`handle`/`trigger`", "o que **não era esperado**: disco cheio, rede caída, bug", "interrompe, e sobe até quem sabe tratar"], ["`void` com `??` e `?.`", "a **ausência** simples: campo opcional, cache vazio", "segue com um padrão"], ["`Arcane.Resultado`", "a falha **esperada** de uma fronteira: validação, busca, parsing", "vira valor, e quem chama decide"]]}},
  {"p": "A regra prática: se quem chama **precisa** decidir o que fazer, devolva `Resultado`. Se ninguém ali pode fazer nada a respeito, `trigger`."},
  {"p": "Um `Resultado` que todo mundo ignora é pior que um erro — ele passa adiante calado. Um `trigger` para o que era esperado obriga `monitor` em todo lugar, e aí ninguém lê mais nenhum."},
  {"h3": "Ler o valor é uma afirmação"},
  {"p": "`r.valor()` numa falha **levanta**, com o motivo dentro da mensagem: ali quem escreveu afirmou que deu certo. Quem não quer afirmar tem duas saídas que nunca levantam:"},
  {"list": ["`r.ou(padrao)` — o valor, ou o padrão;", "`r.exigir(\"minha mensagem\")` — levanta, mas com a frase de quem chama."]},
  {"p": "E `mapear`, `entao` e `recuperar` atravessam a falha **intacta**, o que dispensa um `given` entre cada passo da corrente."},
  {"h3": "`tentar` não engole sinal de controle"},
  {"p": "`R.tentar` captura `DataForgeError` — o erro da linguagem. Um `halt`, um `skip` ou um `yield` atravessa: eles derivam de `BaseException` de propósito, e transformá-los em falha faria um `halt` dentro de um `tentar` parar de sair do laço, calado."},
  {"h3": "`Talvez`, apesar de `void`"},
  {"p": "`void` resolve a ausência em quase todo lugar. O que ele não resolve é distinguir **\"a chave não está lá\"** de **\"a chave está lá e vale void\"** — a dúvida de todo vault de configuração:"},
  { code: `config := {"tema": void}
R.chave(config, "tema").tem()      // yes: está lá
R.chave(config, "idioma").tem()    // no:  não está`, lang: 'df' },
  {"h3": "Reflexão: o que `typeof` não responde"},
  {"p": "`typeof` dá o **nome** do tipo. `Arcane.Tipos` dá o resto:"},
  {"list": ["`Tipos.de(\"Positivo\")` — espécie (`alias`, `uniao`, `intersecao`,"]},
  {"p": "`refinamento`, `opaco`), base, partes, regra;"},
  {"list": ["`Tipos.satisfaz(valor, \"Positivo\")` — confere e **responde**, em vez"]},
  {"p": "de levantar;"},
  {"list": ["`Tipos.forma(valor)` — a forma **estrutural**: `Cluster<Integer>`,"]},
  {"p": "`Tuple<Integer, String>`, `Vault<String, Integer>`. Uma coleção misturada responde `Cluster<Any>`, porque dizer o tipo do primeiro item seria mentira;"},
  {"list": ["`Tipos.campos(valor)` — os campos de um record, instância ou vault,"]},
  {"p": "com o tipo de cada um."},
  {"p": "Juntando as duas peças sai um validador genérico em oito linhas: os campos vêm da reflexão, a regra vem do tipo declarado, e o relato vem do `Resultado`."},
  {"p": "Reflexão responde **em execução**; o `dataforge check` prova antes de rodar o que um literal permite provar. As duas se completam, e nenhuma substitui a outra."},
  {"h2": "256 · Posse, emprestimo e liberacao deterministica"},
  { code: `// Num mundo com coletor, "vazar memoria" quase nunca e o problema: o
// coletor resolve. O que ele NAO resolve e o RECURSO — o arquivo que
// nao fecha, a conexao que fica aberta — porque ele nao promete QUANDO
// passa. E o defeito irmao: duas partes escrevendo no mesmo objeto
// porque nenhuma sabe quem e o dono.

adopt Arcane.Posse as P
adopt Arcane.Memoria as Mem
adopt Arcane.Concurrent as C

// ── dono: um valor, um dono, um finalizador ──
fechados := []
d := P.dono("conexao", lambda x => fechados.append(x))

assert d.usar(lambda x => len(x)) is 7
assert d.vivo()

d.soltar()  // roda AGORA, e nao quando der
assert not d.vivo()
assert fechados is ["conexao"]

d.soltar()  // idempotente
d.soltar()
assert len(fechados) is 1

// usar depois de soltar diz o que aconteceu
monitor:
    d.usar(lambda x => x)
    assert no
handle RuntimeError as e:
    assert "soltou" in e.message

// ── com: o RAII, inclusive quando o corpo falha ──
soltos := []
valor := P.com(P.dono("a", lambda x => soltos.append(x)), lambda x => len(x))
assert valor is 1 and soltos is ["a"]

monitor:
    P.com(P.dono("b", lambda x => soltos.append(x)),
        lambda x => trigger "falhou no meio")
handle Error as e:
    assert e.message is "falhou no meio"

assert soltos is ["a", "b"]  // o caminho de erro tambem solta

// ── mover: quem move, perde ──
a := P.dono([1, 2])
b := a.mover()

assert a.movido()  // perguntar o estado e legitimo
assert b.usar(lambda x => len(x)) is 2

monitor:
    a.usar(lambda x => len(x))
    assert no
handle RuntimeError as e:
    assert "moveu" in e.message

// ── copia e clone sao coisas diferentes ──
original := P.dono([1, 2])

rasa := original.copiar()  // o MESMO valor
rasa.mudar(lambda x => x.append(3))

funda := original.clonar(lambda x => [...x])
funda.mudar(lambda x => x.append(9))

assert original.usar(lambda x => len(x)) is 3
assert funda.usar(lambda x => len(x)) is 4

// ── emprestimo: muitos leem OU um escreve ──
c := P.celula({"n": 0})

assert c.ler(lambda v => v["n"]) is 0
c.escrever(lambda v => v.set("n", 5))
assert c.ler(lambda v => v["n"]) is 5
assert c.emprestimos() is 0

// duas leituras: pode
assert c.ler(lambda v => c.ler(lambda w => 1)) is 1

// escrever no meio de uma leitura: nao
monitor:
    c.ler(lambda v => c.escrever(lambda w => w.set("n", 9)))
    assert no
handle RuntimeError as e:
    assert "lendo" in e.message

// o emprestimo nao sobrevive ao escopo
fugitivo := P.dono([1]).emprestar()
monitor:
    fugitivo.ler()
    assert no
handle RuntimeError as e:
    assert "escopo" in e.message

// ── compartilhado: a contagem decide quando solta ──
cacheados := []
um := P.compartilhado("cache", lambda x => cacheados.append(x))
dois := um.clonar()
tres := um.clonar()

assert um.contar() is 3
dois.soltar()
assert um.contar() is 2 and cacheados is []
tres.soltar()
um.soltar()
assert um.contar() is 0 and cacheados is ["cache"]

// atomico: a mesma coisa, valida entre threads
raiz := P.atomico("recurso")
copias := []

action clonar_uma(i):
    copias.append(raiz.clonar())

C.para_cada(clonar_uma, [i cycle i in range(1, 51)])
assert raiz.contar() is 51

// ── o ciclo vaza, e a fraca o quebra ──
vazados := []
pai := P.compartilhado({"nome": "pai"}, lambda x => vazados.append("pai"))
filho := P.compartilhado({"nome": "filho"}, lambda x => vazados.append("filho"))

pai.usar(lambda v => v.set("filho", filho.clonar()))
filho.usar(lambda v => v.set("pai", pai.clonar()))  // forte: o ciclo

pai.soltar()
filho.soltar()
assert vazados is []  // ninguem chegou a zero

// agora com a volta fraca
quebrados := []
p2 := P.compartilhado({"nome": "pai"}, lambda x => quebrados.append("pai"))
f2 := P.compartilhado({"nome": "filho"}, lambda x => quebrados.append("filho"))

p2.usar(lambda v => v.set("filho", f2.clonar()))
f2.usar(lambda v => v.set("pai", P.fraco(p2)))  // FRACA: nao conta

f2.soltar()
p2.soltar()
assert quebrados is ["pai", "filho"]  // o de fora, e o que ele possuia

// a fraca responde Talvez: ela nao promete que o valor existe
forte := P.compartilhado({"id": 1})
fraca := P.fraco(forte)
assert fraca.vivo() and fraca.obter().tem()
forte.soltar()
assert not fraca.vivo() and not fraca.obter().tem()

// ── layout: o que da para medir ──
blueprint Compacta:
    slots x, y
    x := 1
    y := 2

blueprint Solta:
    x := 1
    y := 2

com_slots := Mem.layout(Compacta)
sem_slots := Mem.layout(Solta)

assert com_slots["slots"] and not sem_slots["slots"]
assert com_slots["campos"] is ["x", "y"]
assert com_slots["bytes"] smaller sem_slots["bytes"]
assert Mem.comparar_layout(Compacta, Solta)["menor"] is "Compacta"

out "256 ok"`, lang: 'df', title: `exercicios/38-tipos/256_posse_e_recursos.df` },
  {"p": "Num mundo com coletor, **vazar memória quase nunca é o problema**. O que o coletor não resolve é o **recurso**: o arquivo que não fecha, a conexão que fica aberta, o cadeado que ninguém solta — porque ele não promete *quando* passa."},
  {"h3": "O que cada peça garante"},
  {"table": {"head": ["Peça", "Garante", "Equivale a"], "rows": [["`P.dono(v, ao_soltar)`", "um dono, um finalizador, uma vez", "`Box` / `unique_ptr`"], ["`P.com(dono, acao)`", "solta no fim, **inclusive no erro**", "RAII / `with`"], ["`P.celula(v)`", "muitos leem **ou** um escreve", "`RefCell`"], ["`P.compartilhado(v)`", "solta quando o **último** sai", "`Rc`"], ["`P.atomico(v)`", "o mesmo, válido entre threads", "`Arc`"], ["`P.fraco(c)`", "observa sem segurar", "`Weak`"]]}},
  {"h3": "Quem move, perde"},
  {"p": "`a.mover()` transfere a posse: `a` fica movido, e usá-lo é erro — com a linha em que o valor saiu. Perguntar o **estado** (`a.movido()`, `a.vivo()`) continua valendo: é exatamente o que se pergunta depois de mover."},
  {"p": "O `dataforge check` acusa isso **antes de rodar** (`posse-movida`) quando o fluxo do arquivo permite provar. Ele só olha nomes que nasceram de `Arcane.Posse`: um blueprint com um método chamado `mover` não tem nada a ver com posse, e acusá-lo seria o falso alarme que ensina a desligar o analisador."},
  {"h3": "Cópia não é clone"},
  {"list": ["`copiar()` — outro dono do **mesmo** valor. É o que se quer quando o"]},
  {"p": "valor *é* o recurso (uma conexão)."},
  {"list": ["`clonar()` — outro dono de uma **cópia**. É o que se quer quando o"]},
  {"p": "valor é o dado."},
  {"p": "Confundir os dois é como confundir `=` com `copy.deepcopy`: funciona até o dia em que alguém escreve na sua lista."},
  {"h3": "O empréstimo tem escopo"},
  {"p": "O valor é entregue ao corpo de `usar`, `mudar`, `ler` ou `escrever` — e vale enquanto esse corpo roda. Pedir o valor **fora** de um corpo (`emprestar()`) devolve um empréstimo já encerrado, e a mensagem diz por quê: quem guarda a referência está pedindo o que o dono não controla mais."},
  {"p": "É o mesmo efeito prático dos *non-lexical lifetimes*, por um caminho mais simples: quem entrega sabe exatamente quando o valor volta."},
  {"h3": "O ciclo vaza — e isso é mostrado"},
  {"p": "Dois compartilhados que se apontam com referências **fortes** nunca chegam a zero, e nenhum finalizador roda. É o problema do `Rc` em qualquer linguagem. Aqui ele aparece como é, em vez de sumir num silêncio, e a saída é a de sempre: uma das voltas é fraca."},
  {"p": "Quando o de fora solta, o que ele possuía é solto junto (*drop glue*) — por isso a ordem é `[\"pai\", \"filho\"]`, e não o contrário."},
  {"h3": "O que isto não é"},
  {"p": "Não é o borrow checker do Rust. Nada aqui vira endereço inválido: o coletor continua no caminho, e a integridade da memória nunca esteve em risco. O que a posse protege é o **protocolo** — soltar uma vez, não usar depois, não escrever no meio da leitura de outro. Não há ponteiro cru, `unsafe`, lifetime explícito nem escolha entre pilha e heap: essas peças pertencem a uma linguagem compilada com layout fixo."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/38-tipos/252_tipos_nomeados.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '252-tipos-nomeados-alias-uniao-intersecao-refinamento-e-opaco', text: "252 · Tipos nomeados: alias, uniao, intersecao, refinamento e opaco", level: 2 as const }, { id: 'transparente-confere-opaco-embrulha', text: "Transparente confere, opaco embrulha", level: 3 as const }, { id: 'a-regra-roda-na-fronteira', text: "A regra roda na fronteira", level: 3 as const }, { id: 'o-que-o-check-prova-antes-de-rodar', text: "O que o `check` prova antes de rodar", level: 3 as const }, { id: '253-generics-tipos-indexados-e-o-sistema-de-traits', text: "253 · Generics, tipos indexados e o sistema de traits", level: 2 as const }, { id: '1-o-que-um-t-promete', text: "1. O que um `<T>` promete?", level: 3 as const }, { id: '2-onde-o-argumento-chega', text: "2. Onde o argumento chega?", level: 3 as const }, { id: '3-o-tamanho-pode-fazer-parte-do-tipo', text: "3. O tamanho pode fazer parte do tipo?", level: 3 as const }, { id: 'traits-exigencia-padrao-e-heranca', text: "Traits: exigência, padrão e herança", level: 3 as const }, { id: '254-tuplas-a-forma-de-tamanho-fixo', text: "254 · Tuplas: a forma de tamanho fixo", level: 2 as const }, { id: 'a-unica-ambiguidade-1-nao-e-tupla', text: "A única ambiguidade: `(1)` não é tupla", level: 3 as const }, { id: 'o-tamanho-faz-parte-do-tipo', text: "O tamanho faz parte do tipo", level: 3 as const }, { id: 'por-que-ela-e-hasheavel', text: "Por que ela é hasheável", level: 3 as const }, { id: 'na-fronteira-do-json', text: "Na fronteira do JSON", level: 3 as const }, { id: '255-a-falha-como-valor-e-a-reflexao-de-tipos', text: "255 · A falha como valor, e a reflexao de tipos", level: 2 as const }, { id: 'tres-formas-tres-perguntas', text: "Três formas, três perguntas", level: 3 as const }, { id: 'ler-o-valor-e-uma-afirmacao', text: "Ler o valor é uma afirmação", level: 3 as const }, { id: 'tentar-nao-engole-sinal-de-controle', text: "`tentar` não engole sinal de controle", level: 3 as const }, { id: 'talvez-apesar-de-void', text: "`Talvez`, apesar de `void`", level: 3 as const }, { id: 'reflexao-o-que-typeof-nao-responde', text: "Reflexão: o que `typeof` não responde", level: 3 as const }, { id: '256-posse-emprestimo-e-liberacao-deterministica', text: "256 · Posse, emprestimo e liberacao deterministica", level: 2 as const }, { id: 'o-que-cada-peca-garante', text: "O que cada peça garante", level: 3 as const }, { id: 'quem-move-perde', text: "Quem move, perde", level: 3 as const }, { id: 'copia-nao-e-clone', text: "Cópia não é clone", level: 3 as const }, { id: 'o-emprestimo-tem-escopo', text: "O empréstimo tem escopo", level: 3 as const }, { id: 'o-ciclo-vaza-e-isso-e-mostrado', text: "O ciclo vaza — e isso é mostrado", level: 3 as const }, { id: 'o-que-isto-nao-e', text: "O que isto não é", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"38 · Sistema de tipos"}
      description={"5 exercícios: alias, união, refinamento, opaco, generics, tuplas e posse."}
      href={"/docs/exercicios/38-tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
