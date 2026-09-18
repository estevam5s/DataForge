"""Tuplas, e a visão geral do sistema de tipos.

Todo bloco `df` destas páginas RODA e passa pelo `check`
(`tests/test_tuplas.py` e `tests/test_sistema_de_tipos.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/tipos/tuplas",
"title": "Tuplas",
"description": "(1, \"a\") — a sequência de tamanho fixo e imutável, com um tipo por posição: o que ela garante, e a diferença entre Tuple, Cluster e Frozen.",
"blocos": [
 {"p": "Uma tupla é **uma forma**: duas casas, cada uma do seu tipo, nesta ordem. O contorno antigo era um cluster de dois itens — que aceita três, aceita zero, e deixa a leitura por índice sem garantia nenhuma."},
 {"code": """t := (1, "a")

assert typeof(t) is "Tuple"
assert len(t) is 2
assert t[0] is 1 and t[1] is "a"
assert t[-1] is "a"

vazia := ()
um := (7,)                     // a vírgula faz a tupla de um item
assert len(vazia) is 0 and len(um) is 1""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "'(1)' é agrupamento, não tupla", "texto": "Essa é a única ambiguidade da forma, e ela é resolvida como em Python: `(1)` é o número 1 entre parênteses, e `(1,)` é a tupla de um item. `(2 + 3) * 2` continua sendo 10."}},

 {"h2": "Três coisas parecidas, e a diferença entre elas"},
 {"table": {"head": ["Tipo", "Muda?", "Conteúdo", "Serve para"], "rows": [
   ["`Cluster`", "sim", "itens do mesmo tipo, quantidade livre", "uma lista de coisas"],
   ["`Frozen`", "não", "itens do mesmo tipo (`freeze([1, 2])`)", "um cluster que não muda mais"],
   ["`Tuple`", "não", "**um tipo por casa**, quantidade fixa", "uma forma: par, coordenada, retorno duplo"]]}},
 {"code": """cluster := [1, 2, 3]
congelado := freeze([1, 2, 3])
tupla := (1, "a", 3.0)

assert typeof(cluster) is "Cluster"
assert typeof(congelado) is "Frozen"
assert typeof(tupla) is "Tuple" """, "lang": "df"},

 {"h2": "Imutável de verdade"},
 {"code": """t := (1, 2)

monitor:
    t[0] := 9
    assert no
handle TypeError as e:
    assert "immutable" in e.message""", "lang": "df"},
 {"p": "Para mudar, construa outra — e é isso que torna a tupla segura de passar adiante, guardar num vault e usar como chave:"},
 {"code": """adopt Arcane.Collections as C

a := (1, "x")
b := (1, "x")

grade := {}
grade[a] := "achei"

assert a is b                        // igualdade estrutural
assert grade[b] is "achei"           // hash pelo conteúdo
assert len(C.set([a, b])) is 1""", "lang": "df"},

 {"h2": "O tipo: `Tuple<A, B, …>`"},
 {"p": "Na anotação, a **quantidade de argumentos é o tamanho**: `Tuple<Integer, String>` tem duas casas, e a casa 0 é um `Integer`. O erro nomeia a casa."},
 {"code": """t: Tuple<Integer, String> := (1, "a")
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
    assert "place" in e.message or "2 place(s)" in e.message""", "lang": "df"},
 {"p": "É o tipo natural do **retorno duplo**, que antes obrigava a devolver um cluster ou um vault:"},
 {"code": """action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield (a ~/ b, a % b)

inteiro, resto := dividir(17, 5)      // desestruturação
assert inteiro is 3 and resto is 2""", "lang": "df"},

 {"h2": "Com alias, aninhada e dentro de coleção"},
 {"code": """type Coordenada := Tuple<Float, Float>
type Segmento := Tuple<Coordenada, Coordenada>

s: Segmento := ((0.0, 0.0), (1.0, 1.0))
assert s[1][0] is 1.0

pares := [(1, "um"), (2, "dois")]
assert pares[1][1] is "dois"

record Trecho:
    de: Coordenada
    para: Coordenada

t := Trecho((0.0, 0.0), (2.0, 2.0))
assert t.para[1] is 2.0""", "lang": "df"},

 {"h2": "O que o `check` prova"},
 {"p": "Sobre um literal, ele decide antes de rodar: tamanho errado e posição errada saem com o código `tipo-do-conteudo`. Sobre um valor que vem de uma chamada, ele **cala**."},
 {"code": """action ler() -> Tuple<Integer, String>:
    yield (1, "a")

t: Tuple<Integer, String> := ler()    // o check cala: não dá para provar
u: Tuple<Integer, String> := (2, "b") // prova que passa

assert t[0] + u[0] is 3""", "lang": "df"},

 {"h2": "Conviver com o resto"},
 {"p": "Ela percorre, serializa e atravessa processo — e volta como tupla:"},
 {"code": """adopt Arcane.Serialization as S
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
assert saida[0][0] is 2 and saida[1][1] is "b" """, "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "No JSON ela é um array", "texto": "JSON não tem tupla. `to_json((1, \"a\"))` produz `[1, \"a\"]`, e o caminho de volta traz um `Cluster` — a forma não sobrevive ao formato. Quando a forma importa na fronteira, declare `Tuple<…>` e converta na entrada."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/tipos/visao-geral",
"title": "O sistema de tipos",
"description": "O mapa: tipos internos, anotações, coleções tipadas, tipos nomeados, generics, indexados, opacos e traits — e o que cada camada garante.",
"blocos": [
 {"p": "O DataForge é de tipagem **dinâmica com anotação verificada**: você escreve o tipo onde ele importa, e a linguagem cobra em duas horas diferentes — o `dataforge check` antes de rodar, quando consegue **provar**, e o interpretador na fronteira, sempre."},

 {"h2": "As camadas"},
 {"table": {"head": ["Camada", "Escreve-se", "Quem confere", "Página"], "rows": [
   ["tipos internos", "`Integer`, `String`, `Cluster`, `Vault`, `Set`, `Tuple`, `Frozen`, `Bytes`, `Any`", "execução, na anotação", "[Tipos](/docs/tipos)"],
   ["anotação", "`x: Integer := 3`, `-> Float`", "as duas", "[Anotações](/docs/fundamentos/anotacoes-de-tipo)"],
   ["conteúdo de coleção", "`Cluster<Integer>`, `Vault<String, Pedido>`, `Set<T>`", "fronteira, inserção e `check`", "[Anotações](/docs/fundamentos/anotacoes-de-tipo)"],
   ["tupla", "`Tuple<Integer, String>`", "posição e tamanho", "[Tuplas](/docs/tipos/tuplas)"],
   ["alias, união, interseção", "`type Json := String \\| Integer`", "as duas", "[Tipos nomeados](/docs/tipos-nomeados)"],
   ["refinamento", "`type Positivo := Integer where valor bigger 0`", "toda fronteira, e `check` sobre literal", "[Tipos nomeados](/docs/tipos-nomeados)"],
   ["opaco", "`opaque type Cpf := String where …`", "nominal: só o construtor cria", "[Tipos nomeados](/docs/tipos-nomeados)"],
   ["generics", "`<T>`, `<T extends Number>`", "limite nas duas metades", "[Generics](/docs/tipos/genericos)"],
   ["indexado", "`Vetor<3>`", "a regra vê o número", "[Generics](/docs/tipos/genericos)"],
   ["traits", "`trait`, `extends`, `type Item`, `&`", "declaração e execução", "[Traits](/docs/tipos/traits)"]]}},

 {"h2": "Um exemplo com todas elas"},
 {"code": """type Id := Integer
type Email := String where "@" in valor
type Vetor<N> := Cluster<Float> where len(valor) is N
opaque type Cpf := String where len(valor) is 11

trait Auditavel:
    action resumo() -> String

record Cliente<T extends Number>:
    id: Id
    email: Email
    documento: Cpf
    saldo: T
    coordenada: Tuple<Float, Float>

blueprint Carteira extends Auditavel:
    clientes: Cluster<Cliente> := []

    action guardar(c: Cliente):
        self.clientes.append(c)
        yield self

    action resumo() -> String:
        yield $"{len(self.clientes)} cliente(s)"

action distancia(a: Vetor<2>, b: Vetor<2>) -> Float:
    yield ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

c := Cliente(1, "ana@exemplo.com", Cpf("12345678901"), 250.0, (1.0, 2.0))
carteira := spawn Carteira()
carteira.guardar(c)

assert carteira.resumo() is "1 cliente(s)"
assert c.documento.valor is "12345678901"
assert distancia([0.0, 0.0], [3.0, 4.0]) is 5.0""", "lang": "df"},

 {"h2": "Quando cada uma acusa"},
 {"p": "A regra é uma só: **o analisador cala quando não consegue provar**. Um falso alarme ensina a desligar a verificação, e aí ela deixa de valer para tudo."},
 {"table": {"head": ["Situação", "`check`", "Execução"], "rows": [
   ["`x: Integer := \"a\"`", "acusa (`type-mismatch`)", "acusa"],
   ["`x: Positivo := -1`", "acusa (`tipo-refinado`)", "acusa"],
   ["`x: Positivo := ler()`", "cala", "acusa se o valor não servir"],
   ["`xs: Cluster<Integer> := [1, \"a\"]`", "acusa (`tipo-do-conteudo`)", "acusa"],
   ["`xs.append(\"a\")` num `Cluster<Integer>`", "acusa quando conhece a coleção", "acusa sempre"],
   ["`f(\"texto\")` num `<T extends Number>`", "acusa (`generic-bound`)", "acusa"],
   ["`cadastrar(\"123…\")` num `Cpf`", "acusa (`tipo-opaco`)", "acusa"]]}},

 {"h2": "O que o sistema de tipos NÃO faz"},
 {"p": "Vale dizer, para ninguém contar com o que não está aqui."},
 {"table": {"head": ["Não existe", "Por quê"], "rows": [
   ["inferência de tipo para variável sem anotação", "a linguagem é dinâmica: o analisador infere o que consegue para acusar, e não para exigir"],
   ["monomorfização e especialização", "não há compilação para código de máquina"],
   ["variância declarada (`in`/`out`)", "ainda não — `Cluster<T>` é conferido item a item"],
   ["prova formal do refinamento", "o `where` é verificado, não provado: literal no `check`, valor na fronteira"],
   ["apagamento de tipo, ABI, layout", "assunto de linguagem compilada; aqui a anotação é conferência em execução"]]}},
 {"callout": {"tipo": "nota", "titulo": "Custo", "texto": "Quem não anota nada não paga nada. A conferência acontece onde a anotação existe, e a coleção tipada só guarda quando **nasce** numa declaração tipada — uma lista que já existia é conferida e continua sendo o mesmo objeto."}},
]},
]
