# -*- coding: utf-8 -*-
"""Fundamentos — as nove páginas que faltavam.

As dezesseis páginas de fundamentos cobrem as construções (record, enum,
match, generics…). Estas cobrem o que fica ENTRE elas e que todo
programa usa: o conjunto (tipo novo), os números, a ausência, a
conversão, a igualdade, a imutabilidade, o texto, a ação como valor e a
recursão. Todo bloco roda.
"""

PAGINAS = [
{'href': '/docs/fundamentos', 'title': 'Fundamentos', 'description': 'O que vem depois dos primeiros passos: tipos, coleções, padrões, ações de ordem superior, recursão e o sistema de tipos — o mapa da seção.', 'blocos': [{'p': 'Os [primeiros passos](/docs/primeiros-passos) ensinam a escrever um programa. Os fundamentos ensinam a escrever **o programa certo**: qual coleção escolher, quando um valor pode mudar, o que `is` compara, onde mora a ausência, como uma ação recebe outra.'}, {'p': 'Não há ordem obrigatória. Cada página se sustenta sozinha, e todo bloco de código roda — foi conferido executando.'}, {'h2': 'A linguagem por dentro'}, {'cards': [{'href': '/docs/fundamentos/anotacoes-de-tipo', 'title': 'Anotações de tipo', 'desc': 'Tipos opcionais em variáveis, parâmetros e retorno — verificados em execução e por análise estática.'}, {'href': '/docs/fundamentos/records', 'title': 'Records', 'desc': 'Dados imutáveis com igualdade estrutural, valores padrão, métodos e o operador with.'}, {'href': '/docs/fundamentos/enums', 'title': 'Enums', 'desc': 'Conjuntos fechados de valores nomeados, com valores associados e integração com match.'}, {'href': '/docs/fundamentos/pattern-matching', 'title': 'Pattern matching', 'desc': 'match estrutural: literais, tipos, sequências, records, vaults, enums, alternativas e guardas.'}, {'href': '/docs/fundamentos/desestruturacao', 'title': 'Desestruturação', 'desc': 'Extrair vários valores de uma vez, por posição ou por nome.'}, {'href': '/docs/fundamentos/spread', 'title': 'Spread e rest', 'desc': 'O operador ... expandindo coleções e coletando o que sobra.'}, {'href': '/docs/fundamentos/compreensoes', 'title': 'Compreensões', 'desc': 'Construir listas e vaults numa expressão, transformando e filtrando.'}, {'href': '/docs/fundamentos/interpolacao', 'title': 'Interpolação', 'desc': 'Strings com $ que embutem expressões, e como formatar saída legível.'}, {'href': '/docs/fundamentos/generators', 'title': 'Generators', 'desc': 'stream action e emit: sequências produzidas sob demanda, inclusive infinitas.'}, {'href': '/docs/fundamentos/closures', 'title': 'Closures e lambdas', 'desc': 'Ações como valores: alta ordem, closures, lambdas e composição.'}, {'href': '/docs/fundamentos/decoradores', 'title': 'Decoradores', 'desc': 'mark @nome — envolver uma ação sem alterar seu corpo.'}, {'href': '/docs/fundamentos/decoradores-avancados', 'title': 'Decoradores avançados', 'desc': 'Embrulhar e anotar — e o que os metadados permitem construir.'}, {'href': '/docs/fundamentos/traits', 'title': 'Traits', 'desc': 'Contratos de interface compostos com with.'}, {'href': '/docs/fundamentos/generics', 'title': 'Generics', 'desc': 'Uma estrutura que serve para qualquer tipo.'}, {'href': '/docs/fundamentos/escopo', 'title': 'Escopo', 'desc': 'Como os nomes são resolvidos, e o que shadow faz.'}, {'href': '/docs/fundamentos/modulos', 'title': 'Módulos', 'desc': 'adopt, relay, imports seletivos e detecção de ciclos.'}]}, {'h2': 'Valores, coleções e ações'}, {'p': 'Conjuntos, números exatos, ausência, conversões, igualdade, imutabilidade, texto, ordem superior e recursão — com as armadilhas que cada um esconde.'}, {'cards': [{'href': '/docs/fundamentos/conjuntos', 'title': 'Conjuntos', 'desc': 'O tipo Set: o literal {1, 2}, set(xs), a compreensão, as operações — e por que um Cluster não entra nele.'}, {'href': '/docs/fundamentos/numeros', 'title': 'Números', 'desc': 'Integer, Float e Decimal — a divisão, o arredondamento, e o 0,1 + 0,2.'}, {'href': '/docs/fundamentos/ausencia', 'title': 'Verdade e ausência', 'desc': "void, o que é verdadeiro, ?? e ?. — e por que 'não sei' não é zero."}, {'href': '/docs/fundamentos/conversoes', 'title': 'Conversões', 'desc': 'int, float, str, cast e typeof — e o que acontece quando o valor não converte.'}, {'href': '/docs/fundamentos/igualdade', 'title': 'Igualdade e comparação', 'desc': 'is compara pelo valor, por estrutura — e as três formas de comparar coleções e objetos.'}, {'href': '/docs/fundamentos/imutabilidade', 'title': 'Imutabilidade', 'desc': 'steady, record, freeze e tupla — o que muda, o que não muda, e por que isso importa.'}, {'href': '/docs/fundamentos/textos-avancados', 'title': 'Texto a fundo', 'desc': 'Fatiar, procurar, trocar, dividir, juntar e formatar — e o texto de várias linhas.'}, {'href': '/docs/fundamentos/ordem-superior', 'title': 'Ações como valores', 'desc': 'Passar uma ação para outra, devolver uma ação, lambda — e o pipeline como a forma idiomática.'}, {'href': '/docs/fundamentos/recursao', 'title': 'Recursão', 'desc': 'Uma ação que chama a si mesma, o caso base, o teto de mil quadros — e as duas saídas.'}]}, {'h2': 'O sistema de tipos'}, {'cards': [{'href': '/docs/tipos/visao-geral', 'title': 'Sistema de tipos: visão geral', 'desc': 'O mapa: tipos internos, anotações, coleções tipadas, tipos nomeados, generics, indexados, opacos e traits — e o que cada camada garante.'}, {'href': '/docs/tipos-nomeados', 'title': 'Tipos nomeados', 'desc': 'type e opaque type: alias, união, interseção, refinamento e tipo opaco — o que cada um promete, quem confere e quando o analisador cala.'}, {'href': '/docs/tipos/tuplas', 'title': 'Tuplas', 'desc': '(1, \\'}, {'href': '/docs/tipos/resultado', 'title': 'Resultado e Talvez', 'desc': 'A falha como valor: ok/falha com mapear, entao e recuperar; e Talvez para onde void é ambíguo — as três formas de lidar com o que dá errado.'}, {'href': '/docs/tipos/reflexao', 'title': 'Reflexão de tipos', 'desc': 'Arcane.Tipos: os metadados de um type declarado, conferir sem levantar, a forma estrutural de um valor e os campos de um record com o tipo de cada um.'}, {'href': '/docs/tipos/mapa', 'title': 'Fundamentos e tipos: o mapa', 'desc': 'Item por item das partes 1 e 2 da referência Deep Tech, cruzado com o DataForge: o que existe e onde está, o que tem outro nome, e o que não existe por decisão.'}, {'href': '/docs/tipos/genericos', 'title': 'Generics: o sistema de tipos', 'desc': '<T> e <T extends X> em ação, blueprint, record, enum e trait: o que o parâmetro documenta, o que o limite cobra, e onde o argumento chega ao conteúdo.'}, {'href': '/docs/tipos/traits', 'title': 'Sistema de traits', 'desc': 'Traits com implementação padrão, herança entre traits, tipos e constantes associados, interseção, despacho dinâmico e o que a linguagem cobra de quem implementa.'}]}]},
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/conjuntos",
"title": "Conjuntos",
"description": "O tipo Set: o literal {1, 2}, set(xs), a compreensão, as operações — e por que um Cluster não entra nele.",
"blocos": [
 {"p": "Um **conjunto** guarda valores sem repetição e sem ordem, e responde uma pergunta em tempo constante: *este valor está aqui?*. É o tipo certo para uma lista de permissões, para tirar duplicatas, e para comparar dois grupos."},
 {"code": """cores := {"azul", "verde", "azul"}      // a repeticao some
assert len(cores) is 2
assert "verde" in cores
assert typeof(cores) is "Set"

vazio := set()                           // '{}' e o vault vazio
assert typeof(vazio) is "Set" and typeof({}) is "Vault"

assert set([3, 1, 3, 2]) is {1, 2, 3}   // de uma lista
assert {n % 3 cycle n in range(0, 10)} is {0, 1, 2}   // compreensao

xs := [1, 2]
assert {...xs, 9} is {1, 2, 9}           // espalhando
out cores                                // sai em ordem: {azul, verde}""", "lang": "df"},
 {"h2": "As operações"},
 {"code": """dev := {"ana", "bia", "caio"}
ops := {"bia", "davi"}

assert dev.union(ops) is {"ana", "bia", "caio", "davi"}        // em qualquer um
assert dev.intersection(ops) is {"bia"}                        // nos dois
assert dev.difference(ops) is {"ana", "caio"}                  // so no primeiro
assert dev.symmetric_difference(ops) is {"ana", "caio", "davi"}
assert {"bia"}.issubset(dev)

dev.add("eva")
dev.discard("ninguem")      // 'discard' nao reclama do que nao existe
assert len(dev) is 4""", "lang": "df"},
 {"h2": "Anotar o tipo"},
 {"code": """permitidos: Set<String> := {"admin", "editor"}
assert "admin" in permitidos
// permitidos: Set<String> := {1} — recusado em execucao
// e o 'check' conhece 'Set' e 'Set<T>'""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um Cluster não entra num Set", "texto": "Um conjunto só guarda o que não muda: um Cluster dentro dele poderia mudar depois de entrar e ficar no lugar errado. `{[1, 2]}` é acusado pelo `check` (`set-item-mutavel`) e recusado em execução com a dica — congele com `freeze(x)`, ou use uma tupla `(1, 2)`."}},
 {"h2": "Quando usar"},
 {"table": {"head": ["Pergunta", "Tipo", "Custo de `x in …`"], "rows": [
   ["*este valor está aqui?*, muitas vezes", "Set", "O(1)"],
   ["*qual é o terceiro?*, *em que ordem?*", "Cluster", "O(n)"],
   ["*quanto vale esta chave?*", "Vault", "O(1)"]]}},
 {"p": "A diferença do `in` aparece com volume: ver [Estruturas](/docs/big-o/estruturas)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/numeros",
"title": "Números",
"description": "Integer, Float e Decimal — a divisão, o arredondamento, e o 0,1 + 0,2.",
"blocos": [
 {"p": "Três tipos de número, e cada um existe por um motivo. **Integer** é exato e sem limite de tamanho. **Float** é rápido e aproximado. **Decimal** é exato com casas — o que dinheiro precisa."},
 {"code": """assert typeof(7) is "Integer"
assert typeof(7.0) is "Float"
assert typeof(7.0d) is "Decimal"

assert 2 ** 100 is 1267650600228229401496703205376    // inteiro nao estoura
assert 7 / 2 is 3.5          // '/' sempre da Float
assert 7 ~/ 2 is 3           // divisao inteira
assert -7 ~/ 2 is -4         // arredonda para BAIXO, e nao para o zero
assert 7 % 3 is 1
assert 1_000_000 is 1000000  // o '_' e so para ler""", "lang": "df"},
 {"h2": "O 0,1 + 0,2"},
 {"code": """adopt Arcane.Decimal as Dec

assert 0.1 + 0.2 isnt 0.3                    // Float: aproximado
assert 0.1d + 0.2d is 0.3d                   // Decimal: exato
assert Dec.texto(Dec.soma([19.99d, 0.01d])) is "20.00"
out 0.1 + 0.2""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Dinheiro é Decimal", "texto": "Float guarda 0,1 como uma fração binária que não fecha — é por isso que `0.1 + 0.2` dá `0.30000000000000004`. Num total de pedido, esse erro aparece como um centavo a mais. Use o literal `19.99d`, e misturar Decimal com Float numa conta é **recusado** de propósito."}},
 {"h2": "Arredondar"},
 {"code": """adopt Arcane.Decimal as Dec

assert round(2.675, 2) is 2.67          // Float: 2.675 e na verdade 2.67499…
assert Dec.texto(Dec.arredondar(2.675d, 2)) is "2.68"   // Decimal: o que se espera
assert floor(-2.5) is -3 and ceil(-2.5) is -2""", "lang": "df"},
 {"table": {"head": ["Quero", "Use"], "rows": [
   ["contar, indexar, somar inteiros", "Integer"],
   ["medir, calcular estatística, ciência", "Float"],
   ["dinheiro, imposto, qualquer coisa que se concilie", "Decimal (`19.99d`)"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/ausencia",
"title": "Verdade e ausência",
"description": "void, o que é verdadeiro, ?? e ?. — e por que 'não sei' não é zero.",
"blocos": [
 {"p": "`void` é a ausência: *não há valor aqui*. Ele não é zero, não é texto vazio e não é `no` — confundir os três é a origem de metade dos bugs de dados: a média que conta o *“não respondeu”* como zero."},
 {"code": """nada := void
assert nada is void
assert typeof(nada) is "Void"
assert void isnt 0 and void isnt "" and void isnt no""", "lang": "df"},
 {"h2": "O que conta como verdadeiro"},
 {"table": {"head": ["Falso (`no`)", "Verdadeiro (`yes`)"], "rows": [
   ["`no`, `void`", "`yes`"],
   ["`0`, `0.0`", "qualquer outro número"],
   ["`\"\"`", "qualquer texto com algo"],
   ["`[]`, `{}`, `set()`", "qualquer coleção com algo"]]}},
 {"code": """action tem_algo(x):
    given x:
        yield yes
    yield no

assert not tem_algo(0) and not tem_algo("") and not tem_algo([]) and not tem_algo(void)
assert tem_algo(-1) and tem_algo(" ") and tem_algo([0])""", "lang": "df"},
 {"h2": "Tratar a ausência: `??` e `?.`"},
 {"code": """cliente := {"nome": "Ana"}

// ?? — o valor, ou um padrao quando e void (ou a chave nao existe).
assert cliente["telefone"] ?? "sem telefone" is "sem telefone"

// ?. — le o membro so se houver objeto; senao, void, sem erro.
endereco := void
assert endereco?.cidade is void

// 'and' e 'or' devolvem o VALOR que decidiu.
assert (void or "padrao") is "padrao"
assert (0 or "padrao") is "padrao"      // cuidado: 0 tambem e falso!
assert (0 ?? "padrao") is 0             // '??' so troca o void""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`or` troca o zero; `??` não", "texto": "`quantidade or 1` transforma uma quantidade **zero** em 1 — porque zero é falso. `quantidade ?? 1` só troca a ausência. Para padrão de valor, use `??`."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/conversoes",
"title": "Conversões",
"description": "int, float, str, cast e typeof — e o que acontece quando o valor não converte.",
"blocos": [
 {"p": "O que vem de fora — do teclado, de um CSV, de um JSON — chega quase sempre como texto. Converter é explícito nesta linguagem: `\"42\" + 1` é erro, e não `\"421\"` nem `43`."},
 {"code": """assert int("42") + 1 is 43
assert float("3.5") * 2 is 7.0
assert str(42) + "!" is "42!"
assert int(3.9) is 3                 // corta, nao arredonda
assert cast "7" as Integer is 7
assert bool(0) is no and bool("x") is yes
assert typeof(int("5")) is "Integer\"""", "lang": "df"},
 {"h2": "Quando não converte"},
 {"code": """action como_inteiro(texto, padrao := void):
    monitor:
        yield int(texto)
    handle Error:
        yield padrao

assert como_inteiro("12") is 12
assert como_inteiro("12,5") is void          // virgula nao e ponto
assert como_inteiro("", 0) is 0
out "o que nao converte vira void — e voce decide o que fazer\"""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Num CSV grande, converta a coluna", "texto": "Converter linha a linha com `monitor` num arquivo de um milhão de linhas é lento e esconde quantas falharam. `Quadro.converter({\"idade\": \"Integer\"})` converte a coluna inteira, põe `void` no que não converte, e conta as falhas em `perfil()`."}},
 {"h2": "Texto de um valor"},
 {"code": """assert str([1, 2]) is "[1, 2]"
assert str({"a": 1}) is "{a: 1}"
assert str(void) is "void" and str(yes) is "yes"
assert $"total: {10 * 3}" is "total: 30\"""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/igualdade",
"title": "Igualdade e comparação",
"description": "is compara pelo valor, por estrutura — e as três formas de comparar coleções e objetos.",
"blocos": [
 {"p": "`is` pergunta *“são iguais?”* **pelo valor**, e não *“são o mesmo objeto?”*. Duas listas com os mesmos itens são iguais; dois records com os mesmos campos também."},
 {"code": """assert [1, 2] is [1, 2]
assert {"a": 1, "b": 2} is {"b": 2, "a": 1}     // a ordem das chaves nao importa
assert {1, 2} is {2, 1}
assert [1, 2] isnt [2, 1]                        // a ordem da lista importa

record Ponto:
    x: Integer
    y: Integer
assert Ponto(1, 2) is Ponto(1, 2)               // record: por estrutura
assert Ponto(1, 2) isnt Ponto(2, 1)""", "lang": "df"},
 {"h2": "Tipos diferentes nunca são iguais"},
 {"code": """assert 1 isnt "1"
assert 1 is 1.0                    // numeros comparam pelo valor
// 1 is "1" e acusado pelo check: 'igualdade-impossivel'""", "lang": "df"},
 {"h2": "Ordenar"},
 {"code": """assert "banana" bigger "abacate"          // texto: ordem de dicionario
assert "Z" smaller "a"                       // maiuscula vem antes!
assert sorted(["b", "A", "c"]) is ["A", "b", "c"]
assert sorted(["b", "A", "c"], lambda s: s.lower()) is ["A", "b", "c"]
assert 1 smaller 2 smaller 3                  // a comparacao encadeia""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Blueprint compara por identidade — a menos que você diga", "texto": "Duas instâncias de um `blueprint` são iguais só se forem o **mesmo** objeto, porque um objeto mutável com os mesmos campos hoje pode ter campos diferentes amanhã. Para comparar por valor, declare `__eq__` — ver [métodos mágicos](/docs/oop/magicos)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/imutabilidade",
"title": "Imutabilidade",
"description": "steady, record, freeze e tupla — o que muda, o que não muda, e por que isso importa.",
"blocos": [
 {"p": "Um valor que não muda pode ser passado para qualquer lugar sem medo: ninguém o altera pelas suas costas. A linguagem tem quatro formas de dizer *“isto não muda”*, e cada uma vale para uma coisa."},
 {"table": {"head": ["Forma", "O que não muda"], "rows": [
   ["`steady NOME := …`", "o **nome**: não recebe outro valor"],
   ["`record`", "os **campos**: `p.x := 1` é erro; `p with {…}` devolve outro"],
   ["`freeze(xs)`", "a **lista**: vira uma sequência que não aceita `append`"],
   ["`(1, \"a\")`", "a **tupla**: uma forma fixa, com um tipo por posição"]]}},
 {"code": """record Pedido:
    id: Integer
    total: Float

p := Pedido(1, 100.0)
p2 := p with {"total": 90.0}
assert p.total is 100.0 and p2.total is 90.0      // o original ficou

monitor:
    p.total := 0.0
    assert no
handle Error as e:
    out "record e imutavel:", e.type

congelada := freeze([1, 2, 3])
monitor:
    congelada.append(4)
    assert no
handle Error:
    out "a lista congelada nao aceita append"
assert thaw(congelada) is [1, 2, 3]""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`steady` protege o nome, não o conteúdo", "texto": "`steady XS := [1, 2]` impede `XS := outra`, mas **não** impede `XS.append(3)`: a lista continua mutável. Para uma constante que não muda de verdade, `steady XS := freeze([1, 2])`."}},
 {"p": "Continue em [Records](/docs/fundamentos/records) e [Tuplas](/docs/tipos/tuplas)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/textos-avancados",
"title": "Texto a fundo",
"description": "Fatiar, procurar, trocar, dividir, juntar e formatar — e o texto de várias linhas.",
"blocos": [
 {"p": "Texto é a coleção mais usada de todas: nomes, arquivos, mensagens, CSV. Ele é **imutável** — todo método devolve um texto novo, e o original não muda."},
 {"code": """nome := "  Maria da Silva  "
limpo := nome.trim()
assert limpo is "Maria da Silva"
assert limpo.upper() is "MARIA DA SILVA"
assert limpo.startswith("Maria") and limpo.endswith("Silva")
assert limpo[0:5] is "Maria"                   // fatia: do 0 ate antes do 5
assert limpo[-5:] is "Silva"
assert "da" in limpo
assert limpo.replace("da ", "") is "Maria Silva"
assert limpo.split(" ") is ["Maria", "da", "Silva"]
assert ", ".join(["a", "b"]) is "a, b"
assert len("cafe") is 4""", "lang": "df"},
 {"h2": "Formatar"},
 {"code": """preco := 1234.5
assert $"R$ {round(preco, 2)}" is "R$ 1234.5"
assert str(7).pad_start(3, "0") is "007"
assert "ab".pad_end(5, ".") is "ab..."
item := {"id": 7}
assert $"item {item["id"]}" is "item 7"        // aspas normais dentro de {}""", "lang": "df"},
 {"h2": "Várias linhas"},
 {"code": """sql := \"\"\"SELECT nome
FROM clientes
WHERE ativo = 1\"\"\"
assert len(sql.lines()) is 3""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Dentro de `$\"{…}\"`, aspas normais", "texto": "`$\"item {v[\"id\"]}\"` funciona; `$\"item {v[\\\"id\\\"]}\"` não — o escape quebra a leitura, e a mensagem (*“Unterminated interpolation”*) não aponta para a causa."}},
 {"p": "Continue em [Interpolação](/docs/fundamentos/interpolacao) e [Arcane.Regex](/docs/biblioteca/regex)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/ordem-superior",
"title": "Ações como valores",
"description": "Passar uma ação para outra, devolver uma ação, lambda — e o pipeline como a forma idiomática.",
"blocos": [
 {"p": "Uma ação é um valor como outro qualquer: pode ser guardada numa variável, passada como argumento e devolvida por outra ação. É o que permite escrever `ordenar(pessoas, pela_idade)` em vez de uma ordenação nova para cada campo."},
 {"code": """action aplicar_duas_vezes(f, x):
    yield f(f(x))

dobro := lambda n: n * 2
assert aplicar_duas_vezes(dobro, 3) is 12

// Uma acao que DEVOLVE uma acao.
action multiplicador(k):
    yield lambda n: n * k

triplo := multiplicador(3)
assert triplo(5) is 15

pessoas := [{"nome": "Bia", "idade": 30}, {"nome": "Ana", "idade": 25}]
assert sorted(pessoas, lambda p: p["idade"])[0]["nome"] is "Ana\"""", "lang": "df"},
 {"h2": "O pipeline"},
 {"code": """vendas := [120, 45, 300, 80, 15]

// filtrar, transformar, reduzir — lido de cima para baixo
total := vendas
    >> sift v: v bigger_eq 50
    >> morph v: v * 0.9
    >> distill acc, v: acc + v 0

assert total is 450.0""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um pipeline dentro de um lambda precisa de parênteses", "texto": "`lambda => xs >> morph x: x * 2` canaliza o **lambda**, e não `xs`. A forma certa é `lambda => (xs >> morph x: x * 2)`. E um ternário no corpo de `morph` também: `morph n: (n given n bigger 0 otherwise 0)`."}},
 {"p": "Continue em [Closures](/docs/fundamentos/closures) e [Pipelines](/docs/pipelines)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/fundamentos/recursao",
"title": "Recursão",
"description": "Uma ação que chama a si mesma, o caso base, o teto de mil quadros — e as duas saídas.",
"blocos": [
 {"p": "Recursão é resolver um problema resolvendo uma versão menor dele. Toda recursão tem duas partes: o **caso base**, que responde sem chamar ninguém, e o **passo**, que chama a si mesma com algo menor."},
 {"code": """action fatorial(n):
    given n smaller_eq 1:
        yield 1                      // caso base
    yield n * fatorial(n - 1)        // passo

assert fatorial(5) is 120

// Percorrer uma arvore e o uso natural.
arvore := {"valor": 1, "filhos": [
    {"valor": 2, "filhos": []},
    {"valor": 3, "filhos": [{"valor": 4, "filhos": []}]}]}

action somar(nodo):          // 'no' e palavra reservada (e o falso)
    total := nodo["valor"]
    cycle f in nodo["filhos"]:
        total += somar(f)
    yield total

assert somar(arvore) is 10""", "lang": "df"},
 {"h2": "O teto, e as duas saídas"},
 {"p": "Cada chamada ocupa um quadro, e o teto é mil. Uma recursão legítima de cinco mil níveis não tem nada de infinita — e mesmo assim bate no teto. Há duas saídas:"},
 {"code": """// 1. Chamada de cauda: 'yield f(...)' como retorno INTEIRO vira salto,
//    e nao empilha. Testado com 200 mil.
action somar_ate(n, acc := 0):
    given n is 0:
        yield acc
    yield somar_ate(n - 1, acc + n)

assert somar_ate(10000) is 50005000

// 2. Um laco com pilha explicita.
action contar_nos(raiz):
    pilha := [raiz]
    n := 0
    persist len(pilha) bigger 0:
        nodo := pilha.pop()
        n += 1
        cycle f in nodo["filhos"]:
            pilha.append(f)
    yield n

assert contar_nos(arvore) is 4""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`n * fatorial(n - 1)` não é cauda", "texto": "Depois da chamada ainda há uma multiplicação, então o quadro precisa ficar. Só `yield f(...)` **sozinho** é cauda — por isso `somar_ate` leva o acumulador como parâmetro."}},
 {"p": "O custo de uma recursão: [Recorrências](/docs/big-o/recorrencias)."},
]},
]

# Um bloco de recursao usa a 'arvore' do anterior: o segundo bloco e o
# primeiro juntos, para rodar sozinho.
for _b in PAGINAS[-1]["blocos"]:
    if _b.get("code", "").startswith("// 1. Chamada de cauda"):
        _b["code"] = ('arvore := {"valor": 1, "filhos": [{"valor": 2, "filhos": []}, '
                      '{"valor": 3, "filhos": [{"valor": 4, "filhos": []}]}]}\n\n' + _b["code"])
