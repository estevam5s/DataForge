"""O sistema de tipos nomeados: alias, união, interseção, refinamento e opaco.

Todo bloco `df` desta página RODA: `tests/test_documentacao_de_tipos.py`
executa cada um e passa cada um pelo `check`. Documentação que não roda
ensina errado — e este é o assunto em que errar custa mais caro, porque
o leitor copia a anotação para o próprio código.
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/tipos-nomeados",
"title": "Tipos nomeados",
"description": "type e opaque type: alias, união, interseção, refinamento e tipo opaco — o que cada um promete, quem confere e quando o analisador cala.",
"blocos": [
 {"p": "A linguagem sabia declarar `record`, `enum`, `blueprint` e `trait` — e não sabia dar nome a um **tipo**. `type` resolve isso com uma declaração só; o que muda é o que vem depois do `:=`."},

 {"table": {"head": ["Forma", "Escreve-se", "Serve para"], "rows": [
   ["alias", "`type Id := Integer`", "um nome para o mesmo tipo, em 200 arquivos"],
   ["alias genérico", "`type Par<T> := Cluster<T>`", "uma função de tipo: o nome recebe o parâmetro"],
   ["união", "`type Json := String | Integer | Void`", "o valor é um destes, e nada mais"],
   ["interseção", "`type Auditavel := Serial & Ordenavel`", "tem de ser os dois ao mesmo tempo"],
   ["refinamento", "`type Positivo := Integer where valor bigger 0`", "o tipo com uma regra, cobrada em toda fronteira"],
   ["opaco", "`opaque type Cpf := String where len(valor) is 11`", "só nasce validado, e um texto não serve no lugar"]]}},

 {"callout": {"tipo": "nota", "titulo": "'type', 'opaque' e 'where' continuam sendo nomes", "texto": "As três são palavras **contextuais**, como as onze do Kiln: `type := 3`, `action type(x)` e uma coluna chamada `where` continuam valendo. A declaração só começa quando a linha confirma — um nome, e um `:=` depois dele."}},

 {"h2": "Alias: um nome, o mesmo tipo"},
 {"p": "O alias não cria tipo novo: ele dá nome ao que já existe. `typeof` responde o tipo de baixo, e um `Id` é aceito em todo lugar que aceita um `Integer` — é o que faz um alias não atrapalhar nada."},
 {"code": """type Id := Integer
type Ids := Cluster<Id>

action buscar(id: Id) -> Id:
    yield id * 2

x: Id := 7
lista: Ids := [1, 2, 3]

assert buscar(x) is 14
assert typeof(x) is "Integer"
assert len(lista) is 3""", "lang": "df"},
 {"p": "O nome aparece na mensagem quando algo não serve — e é o nome que a pessoa escreveu no arquivo, não o tipo de baixo:"},
 {"code": """type Id := Integer

monitor:
    x: Id := "sete"
    assert no
handle TypeError as e:
    assert "Id" in e.message
    assert "Integer" in e.message""", "lang": "df"},

 {"h3": "Alias genérico: a função de tipo"},
 {"p": "`type Par<T> := Cluster<T>` recebe um parâmetro e devolve um tipo. É a menor forma de programação em nível de tipo que existe, e é o que torna o alias útil para coleções: sem a troca de `T`, `Par<Integer>` conferiria `Cluster<T>`, e `T` aceita tudo."},
 {"code": """type Par<T> := Cluster<T>
type Indice<V> := Vault<String, V>

p: Par<Integer> := [1, 2]
i: Indice<Float> := {"altura": 1.75}

assert len(p) is 2
assert i["altura"] is 1.75

monitor:
    errado: Par<Integer> := [1, "dois"]
    assert no
handle TypeError as e:
    assert "Integer" in e.message""", "lang": "df"},

 {"h2": "União: um destes, e nada mais"},
 {"p": "A união aceita um valor de **qualquer um** dos membros, e recusa o resto listando as alternativas. Ela vale com nome (`type Json := …`) e direto na anotação — que é a forma curta para um parâmetro que aceita dois formatos."},
 {"code": """type Json := String | Integer | Boolean | Void

a: Json := "oi"
b: Json := 3
c: Json := yes
d: Json := void

action medir(x: Integer | String) -> Integer:
    yield len($"{x}")

assert medir(2) is 1
assert medir("abc") is 3

monitor:
    errado: Json := [1, 2]
    assert no
handle TypeError as e:
    assert "String" in e.message and "Integer" in e.message""", "lang": "df"},
 {"p": "Os membros podem ser qualquer tipo que a linguagem conhece — embutido, `record`, `enum`, `blueprint` ou outro `type`:"},
 {"code": """record Ponto:
    x: Integer
    y: Integer

enum Falha:
    ForaDoAlcance
    Invalido

type Resposta := Ponto | Falha

action ler(bom) -> Resposta:
    yield Ponto(1, 2) given bom otherwise Falha.Invalido

match ler(no):
    point Ponto(x, y):
        assert no
    default:
        assert yes""", "lang": "df"},

 {"h2": "Interseção: os dois ao mesmo tempo"},
 {"p": "A interseção cobra **todos** os lados. É o que diz \"este parâmetro precisa saber serializar *e* comparar\" sem inventar um trait novo só para juntar os dois."},
 {"code": """trait Serial:
    action serializar()

trait Ordenavel:
    action comparar(outro)

type Auditavel := Serial & Ordenavel

blueprint Lancamento extends Serial, Ordenavel:
    valor := 0
    action serializar():
        yield $"{self.valor}"
    action comparar(outro):
        yield self.valor - outro.valor

blueprint Rascunho extends Serial:
    action serializar():
        yield "rascunho"

action registrar(x: Auditavel) -> String:
    yield x.serializar()

assert registrar(spawn Lancamento()) is "0"

monitor:
    registrar(spawn Rascunho())
    assert no
handle TypeError as e:
    assert "Ordenavel" in e.message""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "'|' e '&' não se misturam na mesma anotação", "texto": "`A | B & C` teria duas leituras, e a linguagem não tem parênteses de tipo. O parser recusa em vez de escolher uma calado: declare um `type` para a metade e use o nome dele."}},

 {"h2": "Refinamento: o tipo com uma regra"},
 {"p": "`where` liga uma regra ao tipo, escrita sobre `valor`. Ela é conferida em **toda fronteira** onde o nome aparece — declaração, parâmetro, retorno e campo. Um refinamento que só valesse na criação seria uma sugestão, não um tipo."},
 {"code": """type Positivo := Integer where valor bigger 0
type Email := String where "@" in valor
type Coordenada := Cluster<Float> where len(valor) is 2

record Item:
    preco: Positivo

action metade(n: Positivo) -> Positivo:
    yield n ~/ 2

assert metade(10) is 5
assert Item(3).preco is 3

c: Coordenada := [1.0, 2.0]
assert len(c) is 2

monitor:
    Item(0)
    assert no
handle TypeError as e:
    assert "Positivo" in e.message
    assert "valor bigger 0" in e.message""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "A base vem antes da regra, sempre", "texto": "`type Nome := String where len(valor) bigger 2` sobre um número recusa por **tipo**, e não tenta rodar a regra: `len` de um número levantaria um erro do interpretador, e a mensagem falaria de `len` em vez do tipo que a pessoa escreveu."}},

 {"h2": "Opaco: o tipo que só nasce validado"},
 {"p": "Um tipo transparente é uma **conferência**; um tipo opaco é um **valor**. `Cpf(\"…\")` é a única porta de entrada, e ela valida. É isso que torna o tipo nominal: um texto com onze dígitos **não** é um `Cpf`, e essa é a única forma de o tipo proteger de alguma coisa."},
 {"code": """opaque type Cpf := String where len(valor) is 11
opaque type Metros := Float where valor bigger_eq 0.0

c := Cpf("12345678901")
d := Metros(2.5)

assert typeof(c) is "Cpf"
assert c.valor is "12345678901"       // o dado de dentro
assert $"{c}" is "12345678901"        // texto, pelo valor
assert d.valor * 2 is 5.0
assert d bigger Metros(1.0)

action cadastrar(documento: Cpf) -> String:
    yield documento.valor

monitor:
    cadastrar("12345678901")           // texto não serve: é nominal
    assert no
handle TypeError as e:
    assert "Cpf" in e.message""", "lang": "df"},
 {"p": "O valor opaco delega por **protocolo** — texto, igualdade, ordem, hash, conta, tamanho, índice e iteração. É a mesma escolha da ponte para o Python: quem pergunta `len(x)` não precisa saber o que `x` é."},
 {"code": """adopt Arcane.Serialization as S
adopt Arcane.Collections as C

opaque type Cpf := String where len(valor) is 11

a := Cpf("12345678901")
b := Cpf("12345678901")

assert a is b                                  // igualdade pelo valor
assert S.to_json({"cpf": a}) is "{\\"cpf\\": \\"12345678901\\"}"
assert len(C.set([a, b])) is 1                 // hash pelo valor""", "lang": "df"},

 {"h2": "O que o analisador prova antes de rodar"},
 {"p": "O `dataforge check` prova o que **dá para provar** com um literal, e cala no resto. Cada acusação tem código próprio, e um código se silencia com `// df: permitir <codigo>` quando a exceção é de propósito."},
 {"table": {"head": ["Código", "Acusa"], "rows": [
   ["`tipo-refinado`", "o literal quebra a regra do `where`"],
   ["`tipo-uniao`", "o literal não é nenhum dos membros da união"],
   ["`tipo-intersecao`", "o valor não é todas as partes"],
   ["`tipo-opaco`", "um valor cru onde o tipo é opaco, ou `Cpf(…)` com a base errada"],
   ["`tipo-circular`", "`type A := B` e `type B := A`"],
   ["`declaracao-repetida`", "dois `type` com o mesmo nome no arquivo"],
   ["`unknown-type`", "um nome que não existe, com sugestão"]]}},
 {"code": """// dataforge check acusa as quatro linhas abaixo, antes de rodar:
//
//   type Positivo := Integer where valor bigger 0
//   x: Positivo := -1              tipo-refinado
//
//   type Json := String | Integer
//   y: Json := [1]                 tipo-uniao
//
//   type Id := Inteiro             unknown-type  (você quis dizer Integer?)
//   type A := B                    tipo-circular
//   type B := A
out "veja o bloco acima" """, "lang": "df"},
 {"p": "E **cala** quando não consegue provar. O valor que vem de uma chamada, de um arquivo ou da rede não é acusado: um falso alarme ensina a desligar o analisador, e aí ele deixa de servir para qualquer coisa."},
 {"code": """type Positivo := Integer where valor bigger 0

action ler() -> Integer:
    yield 3

x: Positivo := ler()      // o check cala: não dá para provar
y: Positivo := 4          // prova que passa

assert x + y is 7         // 'Positivo' conta como o Integer que é""", "lang": "df"},

 {"h2": "Entre arquivos"},
 {"p": "Um tipo atravessa o `adopt` como qualquer outra declaração: `relay` o exporta, e o outro arquivo o nomeia com o apelido do módulo."},
 {"code": """type Positivo := Integer where valor bigger 0
opaque type Cpf := String where len(valor) is 11

relay Positivo, Cpf""", "lang": "df", "title": "tipos.df"},
 {"code": """adopt ./tipos as T

x: T.Positivo := 4
c := T.Cpf("12345678901")

assert x is 4
assert c.valor is "12345678901" """, "lang": "df", "title": "main.df"},

 {"h2": "O que isto não é"},
 {"p": "Vale dizer o que **não** existe, para ninguém contar com o que não está aqui."},
 {"table": {"head": ["Não existe", "Por quê"], "rows": [
   ["apagamento de tipo em tempo de compilação", "o DataForge interpreta a árvore: a anotação vira conferência em execução, e não some"],
   ["garantia de ABI ou compatibilidade binária", "não há binário — isso é assunto de linguagem compilada com layout fixo"],
   ["prova formal de que a regra nunca falha", "o `where` é **verificado**, não provado: o analisador decide sobre literais, e o resto é conferido quando roda"],
   ["variância declarada (`in`/`out` em `<T>`)", "ainda não; `Cluster<T>` é conferido item a item na fronteira"]]}},
 {"callout": {"tipo": "nota", "titulo": "Custo", "texto": "Quem não declara nenhum `type` não paga nada: o registro nasce vazio, e a conferência só olha para ele quando o nome não é um tipo embutido — uma busca de dicionário que já acontecia. A regra de um refinamento é lida uma vez, na declaração."}},
]},
]
