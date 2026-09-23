# -*- coding: utf-8 -*-
"""O tipo literal, e os metodos embutidos que o analisador nao conferia.

Duas adicoes ao sistema de tipos, e as duas sairam da mesma medida: uma
bateria de quinze erros que FALHAM EM EXECUCAO, conferida contra o que o
`dataforge check` pegava antes de rodar. Ele pegava oito. Dos sete
silencios, quatro eram o mesmo caso — um metodo que nao existe num tipo
embutido — e o resto pedia inferencia de fluxo, que e outra conversa.
"""

PAGINAS = [

{"href": "/docs/tipos/literais",
 "title": "Tipos literais",
 "description": "Um valor vira um tipo: type Estado := \"ativo\" | \"inativo\". A conferência acontece onde o dado entra, e não espalhada por cinquenta comparações.",
 "blocos": [
 {"p": "Um tipo literal é um tipo cujo conjunto de valores tem **um** elemento. Sozinho ele é curioso; em união ele é o recurso: `type Estado := \"ativo\" | \"inativo\"` diz, num lugar só, o que antes vivia espalhado em `given e is \"ativo\" or e is \"inativo\"` — e esquecido numa das fronteiras."},

 {"h2": "A forma"},
 {"code": """type Estado := "ativo" | "inativo" | "suspenso"
type Nivel  := 1 | 2 | 3
type Ligado := yes

action mudar(e: Estado) -> String:
    yield e

assert mudar("ativo") is "ativo"
assert mudar("suspenso") is "suspenso"
out "a fronteira confere, e o resto do programa nao precisa"
""", "lang": "df"},
 {"p": "Texto, inteiro, decimal e booleano podem ser literais. `void` fica de fora de propósito: `Void` já é o tipo dele, e `type T := void` seria uma segunda forma de dizer a mesma coisa."},

 {"h2": "Onde ele é cobrado"},
 {"table": {"head": ["Momento", "O que acontece"], "rows": [
   ["`dataforge check`, com o **literal** na mão", "acusa, e lista os valores que valem (`tipo-literal`)"],
   ["`dataforge check`, com uma variável", "**cala** — não há o que provar"],
   ["execução, em toda fronteira", "recusa, nomeando o tipo e o que chegou"]]}},
 {"code": """type Estado := "ativo" | "inativo"

// Provado antes de rodar: o literal esta na mao.
// e: Estado := "zzz"
//   erro: a variável 'e' declared as Estado ("ativo" | "inativo")
//         but the value is 'zzz'

// E cobrado na fronteira, quando o valor vem de fora.
action mudar(e: Estado) -> String:
    yield e

recusou := no
monitor:
    mudar("zzz")
handle Error as erro:
    recusou := yes

assert recusou
out "o que o analisador nao prova, a fronteira cobra"
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O silêncio é o recurso", "texto": "Um `String` que veio de `input()` ou de uma coluna não prova nada, e acusá-lo recusaria justamente o código para o qual o tipo existe: **ler a entrada e passá-la adiante**, deixando a fronteira decidir. O analisador só fala com o literal na mão."}},

 {"h2": "`yes` e `1` não se confundem"},
 {"p": "A comparação é por igualdade **e** por tipo. Em Python `True == 1` é verdadeiro, e sem a conferência de tipo um `type Ligado := yes` aceitaria o número 1 calado — um valor que nunca foi escrito passando por um tipo que existe para não deixar."},

 {"h2": "A base de uma união de literais é conhecida"},
 {"code": """type Estado := "ativo" | "inativo"

action rotulo(e: Estado) -> String:
    // 'e' e um String para o analisador, e por isso isto e aceito:
    // sem essa leitura, devolver 'e' num '-> String' seria acusado.
    yield e + "!"

assert rotulo("ativo") is "ativo!"
out "uniao so de literais do mesmo tipo abre para a base"
""", "lang": "df"},
 {"p": "Uma união **mista** — `\"auto\" | Integer` — não tem base única, e ali o analisador volta a calar em vez de escolher uma: escolher faria ele aprovar o que a execução recusa."},

 {"h2": "Quando usar, e quando não"},
 {"table": {"head": ["Use um tipo literal quando", "Use um `enum` quando"], "rows": [
   ["o valor **é** o dado — vem de um JSON, de uma coluna, de um `?estado=`", "o valor é um conceito do domínio, com nome próprio"],
   ["você quer conferir na fronteira sem converter nada", "você quer método, `.name`, `.value` e exaustividade no `match`"],
   ["a lista é pequena e fechada", "a lista cresce, ou carrega comportamento"]]}},
 {"cards": [
   {"href": "/docs/tipos", "title": "O sistema de tipos", "desc": "o guia"},
   {"href": "/docs/faq/tipos", "title": "FAQ: tipos", "desc": "o que é conferido, e quando"},
   {"href": "/docs/tipos/genericos", "title": "Genéricos", "desc": "`<T extends X>`"}]},
]},

{"href": "/docs/tipos/metodos-embutidos",
 "title": "O método que não existe",
 "description": "O check acusava p.clientte num record e calava em \"ana\".naoExiste(). A conferência agora vale para os dois, e a lista de métodos é lida do interpretador.",
 "blocos": [
 {"p": "A forma mais comum de erro de digitação numa linguagem é chamar um método que não existe. O `dataforge check` acusava isso num `record` e num `blueprint` — com sugestão — e **calava** num texto, num cluster e num vault."},

 {"h2": "A medida"},
 {"p": "Quinze erros que **falham em execução**, conferidos contra o que o `check` pegava antes de rodar. Ele pegava oito. Dos sete silêncios, quatro eram este mesmo caso em tipos diferentes:"},
 {"code": """nome := "ana"
xs := [1, 2, 3]

// Os dois abaixo sao acusados agora, com sugestao:
//   nome.uppper()   ->  'String' has no method 'uppper'
//                       sugestão: Você quis dizer 'upper'?
//   xs.apend(3)     ->  'Cluster' has no method 'apend'
//                       sugestão: Você quis dizer 'append'?

assert nome.upper() is "ANA"
xs.append(4)
assert len(xs) is 4
out "o mesmo erro, o mesmo tratamento"
""", "lang": "df"},

 {"h2": "A lista vem do interpretador"},
 {"p": "As tabelas de método de texto e de cluster moram em `dataforge/interpreter.py`, e o analisador as **lê de lá**. Uma segunda lista divergiria no primeiro método novo — e a divergência não daria erro: ela faria o analisador acusar um método que funciona, que é o falso alarme que ensina a desligar a verificação."},

 {"h2": "Onde ele cala, e por quê"},
 {"table": {"head": ["Cala sobre", "Porque"], "rows": [
   ["um **Vault**", "`v.cidade` cai na chave quando ela existe — acusar exigiria saber as chaves"],
   ["um objeto vindo de `adopt Python.x`", "ali o membro é resolvido pelo Python, e a análise não sabe quais são"],
   ["um nome começando com `_`", "é combinado entre quem escreveu, não um engano"],
   ["um tipo que ele não conseguiu inferir", "a regra de sempre: sem prova, silêncio"]]}},
 {"callout": {"tipo": "nota", "titulo": "Zero falso alarme em 532 arquivos", "texto": "A calibragem foi feita rodando o `check` sobre `examples`, `exercicios`, `projetos`, `packages` e `trilha` — as cinco pastas do repositório. Nenhum arquivo que funciona passou a ser acusado."}},
 {"cards": [
   {"href": "/docs/faq/tipos", "title": "FAQ: tipos", "desc": "o que é conferido, e quando"},
   {"href": "/docs/biblioteca", "title": "A biblioteca", "desc": "os métodos de cada tipo"},
   {"href": "/docs/erros", "title": "Códigos de erro", "desc": "o catálogo"}]},
]},
]
