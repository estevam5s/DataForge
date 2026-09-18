// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_tuplas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Tuplas",
  description: "(1, \"a\") — a sequência de tamanho fixo e imutável, com um tipo por posição: o que ela garante, e a diferença entre Tuple, Cluster e Frozen.",
};

const blocos: Bloco[] = [
  {"p": "Uma tupla é **uma forma**: duas casas, cada uma do seu tipo, nesta ordem. O contorno antigo era um cluster de dois itens — que aceita três, aceita zero, e deixa a leitura por índice sem garantia nenhuma."},
  { code: `t := (1, "a")

assert typeof(t) is "Tuple"
assert len(t) is 2
assert t[0] is 1 and t[1] is "a"
assert t[-1] is "a"

vazia := ()
um := (7,)                     // a vírgula faz a tupla de um item
assert len(vazia) is 0 and len(um) is 1`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "'(1)' é agrupamento, não tupla", "texto": "Essa é a única ambiguidade da forma, e ela é resolvida como em Python: `(1)` é o número 1 entre parênteses, e `(1,)` é a tupla de um item. `(2 + 3) * 2` continua sendo 10."}},
  {"h2": "Três coisas parecidas, e a diferença entre elas"},
  {"table": {"head": ["Tipo", "Muda?", "Conteúdo", "Serve para"], "rows": [["`Cluster`", "sim", "itens do mesmo tipo, quantidade livre", "uma lista de coisas"], ["`Frozen`", "não", "itens do mesmo tipo (`freeze([1, 2])`)", "um cluster que não muda mais"], ["`Tuple`", "não", "**um tipo por casa**, quantidade fixa", "uma forma: par, coordenada, retorno duplo"]]}},
  { code: `cluster := [1, 2, 3]
congelado := freeze([1, 2, 3])
tupla := (1, "a", 3.0)

assert typeof(cluster) is "Cluster"
assert typeof(congelado) is "Frozen"
assert typeof(tupla) is "Tuple" `, lang: 'df' },
  {"h2": "Imutável de verdade"},
  { code: `t := (1, 2)

monitor:
    t[0] := 9
    assert no
handle TypeError as e:
    assert "immutable" in e.message`, lang: 'df' },
  {"p": "Para mudar, construa outra — e é isso que torna a tupla segura de passar adiante, guardar num vault e usar como chave:"},
  { code: `adopt Arcane.Collections as C

a := (1, "x")
b := (1, "x")

grade := {}
grade[a] := "achei"

assert a is b                        // igualdade estrutural
assert grade[b] is "achei"           // hash pelo conteúdo
assert len(C.set([a, b])) is 1`, lang: 'df' },
  {"h2": "O tipo: `Tuple<A, B, …>`"},
  {"p": "Na anotação, a **quantidade de argumentos é o tamanho**: `Tuple<Integer, String>` tem duas casas, e a casa 0 é um `Integer`. O erro nomeia a casa."},
  { code: `t: Tuple<Integer, String> := (1, "a")
assert t[1] is "a"

monitor:
    trocada: Tuple<Integer, String> := ("a", 1)
    assert no
handle TypeError as e:
    assert "place 0" in e.message

monitor:
    grande: Tuple<Integer, String> := (1, "a", 2)
    assert no
handle TypeError as e:
    assert "place" in e.message or "2 place(s)" in e.message`, lang: 'df' },
  {"p": "É o tipo natural do **retorno duplo**, que antes obrigava a devolver um cluster ou um vault:"},
  { code: `action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield (a ~/ b, a % b)

inteiro, resto := dividir(17, 5)      // desestruturação
assert inteiro is 3 and resto is 2`, lang: 'df' },
  {"h2": "Com alias, aninhada e dentro de coleção"},
  { code: `type Coordenada := Tuple<Float, Float>
type Segmento := Tuple<Coordenada, Coordenada>

s: Segmento := ((0.0, 0.0), (1.0, 1.0))
assert s[1][0] is 1.0

pares := [(1, "um"), (2, "dois")]
assert pares[1][1] is "dois"

record Trecho:
    de: Coordenada
    para: Coordenada

t := Trecho((0.0, 0.0), (2.0, 2.0))
assert t.para[1] is 2.0`, lang: 'df' },
  {"h2": "O que o `check` prova"},
  {"p": "Sobre um literal, ele decide antes de rodar: tamanho errado e posição errada saem com o código `tipo-do-conteudo`. Sobre um valor que vem de uma chamada, ele **cala**."},
  { code: `action ler() -> Tuple<Integer, String>:
    yield (1, "a")

t: Tuple<Integer, String> := ler()    // o check cala: não dá para provar
u: Tuple<Integer, String> := (2, "b") // prova que passa

assert t[0] + u[0] is 3`, lang: 'df' },
  {"h2": "Conviver com o resto"},
  {"p": "Ela percorre, serializa e atravessa processo — e volta como tupla:"},
  { code: `adopt Arcane.Serialization as S
adopt Arcane.Concurrent as P

t := (1, "a")
assert S.to_json(t) is "[1, \\"a\\"]"

soma := 0
cycle item in (1, 2, 3):
    soma += item
assert soma is 6
assert 2 in (1, 2, 3)

action dobrar(par):
    yield (par[0] * 2, par[1])

saida := P.map_processos(dobrar, [(1, "a"), (2, "b")])
assert saida[0][0] is 2 and saida[1][1] is "b" `, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "No JSON ela é um array", "texto": "JSON não tem tupla. `to_json((1, \"a\"))` produz `[1, \"a\"]`, e o caminho de volta traz um `Cluster` — a forma não sobrevive ao formato. Quando a forma importa na fronteira, declare `Tuple<…>` e converta na entrada."}},
];

const headings = [{ id: 'tres-coisas-parecidas-e-a-diferenca-entre-elas', text: "Três coisas parecidas, e a diferença entre elas", level: 2 as const }, { id: 'imutavel-de-verdade', text: "Imutável de verdade", level: 2 as const }, { id: 'o-tipo-tuplea-b', text: "O tipo: `Tuple<A, B, …>`", level: 2 as const }, { id: 'com-alias-aninhada-e-dentro-de-colecao', text: "Com alias, aninhada e dentro de coleção", level: 2 as const }, { id: 'o-que-o-check-prova', text: "O que o `check` prova", level: 2 as const }, { id: 'conviver-com-o-resto', text: "Conviver com o resto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Tuplas"}
      description={"(1, \"a\") — a sequência de tamanho fixo e imutável, com um tipo por posição: o que ela garante, e a diferença entre Tuple, Cluster e Frozen."}
      href={"/docs/tipos/tuplas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
