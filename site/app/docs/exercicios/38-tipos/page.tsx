// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "38 · Sistema de tipos",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 38`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[252](#252-tipos-nomeados-alias-uniao-intersecao-refinamento-e-opaco)", "**Tipos nomeados: alias, uniao, intersecao, refinamento e opaco**", ""]]}},
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
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/38-tipos/252_tipos_nomeados.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '252-tipos-nomeados-alias-uniao-intersecao-refinamento-e-opaco', text: "252 · Tipos nomeados: alias, uniao, intersecao, refinamento e opaco", level: 2 as const }, { id: 'transparente-confere-opaco-embrulha', text: "Transparente confere, opaco embrulha", level: 3 as const }, { id: 'a-regra-roda-na-fronteira', text: "A regra roda na fronteira", level: 3 as const }, { id: 'o-que-o-check-prova-antes-de-rodar', text: "O que o `check` prova antes de rodar", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"38 · Sistema de tipos"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/38-tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
