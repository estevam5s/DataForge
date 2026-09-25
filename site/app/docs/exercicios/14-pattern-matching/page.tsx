// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "14 · Pattern matching",
  description: "6 exercícios: point, when, tipos, sequências e vaults.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **A linguagem a fundo** · point, when, tipos, sequências e vaults · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 14`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[139](#139-padroes-basicos)", "**Padroes basicos**", "case por literal, capture com um nome e use o curinga."], ["[140](#140-padroes-de-tipo)", "**Padroes de tipo**", "case pelo tipo do valor e ligue o resultado ja tipado."], ["[141](#141-padroes-de-sequencia)", "**Padroes de sequencia**", "desmonte listas por posicao, com cabeca, cauda e tamanho fixo."], ["[142](#142-padroes-de-record-e-vault)", "**Padroes de record e vault**", "extraia campos direto no padrao, por posicao ou por nome."], ["[143](#143-guardas-e-ligacao-com-as)", "**Guardas e ligacao com as**", "combine condicoes e apelidos para casos precisos."], ["[144](#144-projeto-validador-de-dados)", "**Projeto: validador de dados**", "junte padroes de tipo, sequencia e vault num validador de esquema."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "139 · Padroes basicos"},
  {"p": "**Enunciado.** case por literal, capture com um nome e use o curinga."},
  { code: `action classificar(v):
    match v:
        point 0:
            yield "zero"
        point 1 or 2 or 3:
            yield "pequeno"
        point "sim" or "yes":
            yield "afirmativo"
        point void:
            yield "vazio"
        point n:
            yield $"outro: {n}"

cycle v in [0, 2, "sim", void, 99]:
    out classificar(v)

assert classificar(0) is "zero", "literal"
assert classificar(3) is "pequeno", "alternativa com or"
assert classificar("yes") is "afirmativo", "texto"
assert classificar(void) is "vazio", "void"
assert classificar(99) is "outro: 99", "captura"

// O curinga _ casa com tudo e nao liga nome
action tem_valor(v):
    match v:
        point void:
            yield no
        point _:
            yield yes

assert tem_valor(void) is no, "void"
assert tem_valor(0) is yes, "zero e um valor"
assert tem_valor("") is yes, "texto vazio e um valor"

// A ordem importa: o primeiro que casa vence
//
// O analisador ACUSA isto — e esta certo: o 'point 5' e codigo morto.
// Aqui o erro e o assunto do exercicio, e 'df: permitir' diz isso a
// ele. A regra e nomeada de proposito: um 'permitir' solto esconderia
// o erro seguinte, que ninguem pediu para esconder.
action ordem(n):
    match n:
        point x:
            yield "pegou tudo"
        // df: permitir point-inalcancavel
        point 5:
            yield "nunca chega aqui"

assert ordem(5) is "pegou tudo", "captura antes de literal engole tudo"
out "cuidado: uma captura no topo torna os demais inalcancaveis"`, lang: 'df', title: `exercicios/14-pattern-matching/139_padroes_basicos.df` },
  {"h3": "Conceitos"},
  {"p": "`match` avalia uma expressão e testa cada `point` **de cima para baixo**. O primeiro que casa executa, e os demais são ignorados."},
  {"p": "**Padrão literal**"},
  { code: `point 0:
point "sim":
point void:`, lang: 'df' },
  {"p": "Casa por igualdade exata."},
  {"p": "**Alternativas com `or`**"},
  { code: `point 1 or 2 or 3:
    yield "pequeno"`, lang: 'df' },
  {"p": "Um só ramo para vários valores."},
  {"p": "**Captura**"},
  {"p": "Um nome **em minúscula** casa com qualquer coisa e liga o valor:"},
  { code: `point n:
    yield $"outro: {n}"`, lang: 'df' },
  {"p": "**Curinga**"},
  {"p": "`_` casa com qualquer coisa e **não** liga nome — use quando o valor não interessa:"},
  { code: `point _:
    yield yes`, lang: 'df' },
  {"h3": "A convenção maiúscula/minúscula"},
  {"p": "Esta é a regra que organiza tudo:"},
  {"table": {"head": ["Escrita", "Significa"], "rows": [["`point n`", "**captura** — casa com tudo, liga a `n`"], ["`point Integer`", "**tipo** — casa se for um Integer"], ["`point Status.Ativo`", "**valor** — casa por igualdade"], ["`point _`", "**curinga**"]]}},
  {"p": "Minúscula captura, maiúscula testa o tipo. Sem essa convenção, `point Integer` seria ambíguo: comparar com uma variável chamada `Integer` ou testar o tipo?"},
  {"h3": "A ordem é tudo"},
  { code: `match n:
    point x:              // captura tudo
        yield "pegou tudo"
    point 5:              // inalcançável
        yield "nunca chega aqui"`, lang: 'df' },
  {"p": "Uma captura no topo engole todos os casos abaixo. Coloque sempre **do mais específico para o mais geral** — literais primeiro, tipos depois, captura ou `default` por último."},
  {"h3": "Saída esperada"},
  { code: `zero
pequeno
afirmativo
vazio
outro: 99
cuidado: uma captura no topo torna os demais inalcancaveis`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Inverta os dois `point` de `ordem` e veja o resultado mudar.", "Troque `point n` final por `default:` — qual a diferença prática?"]},
  {"h2": "140 · Padroes de tipo"},
  {"p": "**Enunciado.** case pelo tipo do valor e ligue o resultado ja tipado."},
  { code: `record Ponto:
    x: Integer
    y: Integer

action descrever(v):
    match v:
        point Integer as n when n smaller 0:
            yield $"inteiro negativo ({n})"
        point Integer as n:
            yield $"inteiro {n}"
        point Float as d:
            yield $"decimal {d}"
        point String as s:
            yield $"texto de {len(s)} letras"
        point Boolean:
            yield "booleano"
        point Cluster as c:
            yield $"lista com {len(c)} itens"
        point Vault:
            yield "dicionario"
        point Ponto as p:
            yield $"ponto ({p.x}, {p.y})"
        point Void:
            yield "nada"
        default:
            yield "tipo desconhecido"

valores := [7, -3, 2.5, "abc", yes, [1, 2], {"a":1}, Ponto(3, 4), void]
cycle v in valores:
    out descrever(v)

assert descrever(7) is "inteiro 7", "Integer"
assert descrever(-3) is "inteiro negativo (-3)", "guarda antes do geral"
assert descrever(2.5) is "decimal 2.5", "Float"
assert descrever(Ponto(3, 4)) is "ponto (3, 4)", "record por tipo"
assert descrever(void) is "nada", "Void"

// Number aceita Integer e Float
action e_numero(v):
    match v:
        point Number:
            yield yes
        default:
            yield no

assert e_numero(1) is yes, "Integer e Number"
assert e_numero(1.5) is yes, "Float e Number"
assert e_numero("1") is no, "texto nao e Number"

// Any casa com tudo, inclusive void
action sempre(v):
    match v:
        point Any:
            yield "casou"
assert sempre(void) is "casou", "Any casa ate com void"`, lang: 'df', title: `exercicios/14-pattern-matching/140_padroes_de_tipo.df` },
  {"h3": "Conceitos"},
  {"p": "Um nome **em maiúscula** num `point` testa o tipo:"},
  { code: `point Integer as n:
    yield $"inteiro {n}"`, lang: 'df' },
  {"p": "Isso faz duas coisas de uma vez: **testa** que `v` é um Integer e **liga** `n` ao valor. É o *type narrowing* que TypeScript faz com `typeof x === \"number\"`, aqui como sintaxe de primeira classe."},
  {"h3": "Tipos aceitos"},
  {"p": "Todos os que valem numa anotação:"},
  {"p": "`Integer` · `Float` · `Number` · `String` · `Boolean` · `Cluster` · `Vault` · `Void` · `Action` · `Stream` · `Any` · e o nome de qualquer record, blueprint ou enum que você definiu."},
  {"h3": "`Number` e `Any`"},
  {"p": "Dois casos especiais que valem entender:"},
  { code: `point Number:     // casa com Integer OU Float
point Any:        // casa com tudo, inclusive void`, lang: 'df' },
  {"p": "`point Any` é equivalente a `point _` — use `_` quando não precisar do valor, `Any` quando quiser deixar explícito que aceita qualquer tipo."},
  {"h3": "Guardas com `when`"},
  {"p": "Um `when` acrescenta uma condição que roda **depois** de o padrão casar:"},
  { code: `point Integer as n when n smaller 0:
    yield $"inteiro negativo ({n})"
point Integer as n:
    yield $"inteiro {n}"`, lang: 'df' },
  {"p": "Se a guarda falha, o `match` **continua** para o próximo `point`. Por isso o par acima funciona: negativos param no primeiro, o resto cai no segundo."},
  {"p": "Isso torna a ordem ainda mais importante: o específico (com guarda) vem antes do geral."},
  {"h3": "Por que `when` e não `given`"},
  {"p": "`given` já é o ternário (`a given c otherwise b`). Usar a mesma palavra numa guarda criaria ambiguidade real no parser: em `point n given x` o parser não saberia se `given` abre uma guarda ou um ternário. `when` resolve isso sem ambiguidade."},
  {"h3": "Saída esperada"},
  { code: `inteiro 7
inteiro negativo (-3)
decimal 2.5
texto de 3 letras
booleano
lista com 2 itens
dicionario
ponto (3, 4)
nada`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Remova `point Void` e veja `void` cair no `default`.", "Adicione `point Integer as n when n % 2 is 0` e escolha onde colocá-lo."]},
  {"h2": "141 · Padroes de sequencia"},
  {"p": "**Enunciado.** desmonte listas por posicao, com cabeca, cauda e tamanho fixo."},
  { code: `action descrever(lista):
    match lista:
        point []:
            yield "vazia"
        point [unico]:
            yield $"um item: {unico}"
        point [a, b]:
            yield $"par: {a} e {b}"
        point [primeiro, ...resto]:
            yield $"comeca com {primeiro}, mais {len(resto)}"
        default:
            yield "nao e lista"

cycle l in [[], [7], [1, 2], [1, 2, 3, 4], "texto"]:
    out descrever(l)

assert descrever([]) is "vazia", "lista vazia"
assert descrever([7]) is "um item: 7", "um elemento"
assert descrever([1, 2]) is "par: 1 e 2", "dois elementos"
assert descrever([1, 2, 3, 4]) is "comeca com 1, mais 3", "cabeca e cauda"
assert descrever("texto") is "nao e lista", "texto nao casa com sequencia"

// Padroes aninhados
action ler_par(p):
    match p:
        point [nome, [x, y]]:
            yield $"{nome} em ({x}, {y})"
        default:
            yield "formato inesperado"

out ler_par(["origem", [0, 0]])
assert ler_par(["origem", [0, 0]]) is "origem em (0, 0)", "aninhado"

// Literais dentro do padrao
action comando(partes):
    match partes:
        point ["mover", direcao, passos]:
            yield $"mover {passos} para {direcao}"
        point ["parar"]:
            yield "parando"
        point ["dizer", ...palavras]:
            yield $"dizendo: {palavras.join(" ")}"
        default:
            yield "comando desconhecido"

out comando(["mover", "norte", 3])
out comando(["parar"])
out comando(["dizer", "ola", "mundo"])
out comando(["voar"])

assert comando(["mover", "norte", 3]) is "mover 3 para norte", "com literal"
assert comando(["dizer", "ola", "mundo"]) is "dizendo: ola mundo", "resto"

// Recursao sobre cabeca e cauda
action somar(lista):
    match lista:
        point []:
            yield 0
        point [cabeca, ...cauda]:
            yield cabeca + somar(cauda)

assert somar([1, 2, 3, 4, 5]) is 15, "soma recursiva"
out $"soma recursiva: {somar([1, 2, 3, 4, 5])}"`, lang: 'df', title: `exercicios/14-pattern-matching/141_padroes_de_sequencia.df` },
  {"h3": "Conceitos"},
  {"p": "Colchetes num `point` formam um **padrão de sequência**:"},
  { code: `point []:                    // exatamente vazia
point [unico]:               // exatamente um item
point [a, b]:                // exatamente dois
point [primeiro, ...resto]:  // um ou mais`, lang: 'df' },
  {"p": "O padrão casa pelo **comprimento** e liga cada posição a um nome."},
  {"h3": "Só sequências de verdade"},
  {"p": "Um vault é iterável, mas **não** casa com `[…]`:"},
  { code: `descrever({"a": 1})     // "nao e lista"`, lang: 'df' },
  {"p": "Isso é deliberado: um vault casa com `{…}`, uma lista com `[…]`. Sem essa separação, `point [a, b]` capturaria dicionários de duas chaves por acidente — um bug difícil de enxergar."},
  {"h3": "Literais dentro do padrão"},
  {"p": "Você pode misturar literais e capturas:"},
  { code: `point ["mover", direcao, passos]:
    yield $"mover {passos} para {direcao}"`, lang: 'df' },
  {"p": "Casa só se o primeiro elemento for exatamente `\"mover\"` **e** houver três elementos. É a forma natural de interpretar comandos."},
  {"h3": "Padrões aninhados"},
  { code: `point [nome, [x, y]]:
    yield $"{nome} em ({x}, {y})"`, lang: 'df' },
  {"p": "Um padrão dentro do outro, na profundidade que precisar."},
  {"h3": "Cabeça e cauda: o padrão recursivo"},
  { code: `action somar(lista):
    match lista:
        point []:
            yield 0
        point [cabeca, ...cauda]:
            yield cabeca + somar(cauda)`, lang: 'df' },
  {"p": "Dois casos e a função está completa: a lista vazia (caso base) e \"um elemento mais o resto\" (caso recursivo). É como se escreve sobre listas em Haskell, Elixir e Erlang."},
  {"p": "Para listas grandes, prefira `>> distill` — a recursão consome pilha e o limite é 1000 quadros."},
  {"h3": "Saída esperada"},
  { code: `vazia
um item: 7
par: 1 e 2
comeca com 1, mais 3
nao e lista
origem em (0, 0)
mover 3 para norte
parando
dizendo: ola mundo
comando desconhecido
soma recursiva: 15`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Adicione `point [a, b, c]` e veja onde colocá-lo para ser alcançado.", "Escreva `inverter(lista)` usando cabeça e cauda.", "Reescreva `somar` com `>> distill` e compare em `[1..2000]`."]},
  {"h2": "142 · Padroes de record e vault"},
  {"p": "**Enunciado.** extraia campos direto no padrao, por posicao ou por nome."},
  { code: `record Usuario:
    nome: String
    idade: Integer
    papel: String := "leitor"

action permissao(u):
    match u:
        point Usuario(papel := "admin"):
            yield "acesso total"
        point Usuario(nome := n, idade := i) when i smaller 18:
            yield $"{n} e menor: acesso limitado"
        point Usuario(nome := n):
            yield $"{n}: acesso padrao"
        default:
            yield "nao e usuario"

cycle u in [
    Usuario("Root", 40, "admin"),
    Usuario("Kid", 12),
    Usuario("Ana", 30),
]:
    out permissao(u)

assert permissao(Usuario("Root", 40, "admin")) is "acesso total", "por campo"
assert permissao(Usuario("Kid", 12)) is "Kid e menor: acesso limitado", "guarda"
assert permissao(Usuario("Ana", 30)) is "Ana: acesso padrao", "geral"

// Por posicao, na ordem dos campos
action resumo(u):
    match u:
        point Usuario(n, i, p):
            yield $"{n}/{i}/{p}"
        default:
            yield "?"

assert resumo(Usuario("Ana", 30)) is "Ana/30/leitor", "posicional"

// Vaults casam com chaves
action rotear(req):
    match req:
        point {"metodo": "GET", "rota": r}:
            yield $"lendo {r}"
        point {"metodo": "POST", "rota": r, "corpo": c}:
            yield $"criando em {r} com {len(c.keys())} campos"
        point {"metodo": m}:
            yield $"metodo {m} nao suportado"
        default:
            yield "requisicao invalida"

out rotear({"metodo": "GET", "rota": "/usuarios"})
out rotear({"metodo": "POST", "rota": "/usuarios", "corpo": {"nome": "Ana"}})
out rotear({"metodo": "DELETE", "rota": "/x"})
out rotear("nao e vault")

assert rotear({"metodo": "GET", "rota": "/x"}) is "lendo /x", "GET"
assert rotear({"metodo": "DELETE", "rota": "/x"}) is "metodo DELETE nao suportado", "outro"

// Chaves extras nao atrapalham
assert rotear({"metodo": "GET", "rota": "/x", "extra": 1}) is "lendo /x", "casamento parcial"`, lang: 'df', title: `exercicios/14-pattern-matching/142_padroes_de_registro.df` },
  {"h3": "Conceitos"},
  {"p": "**Record por posição**"},
  { code: `point Usuario(n, i, p):`, lang: 'df' },
  {"p": "Casa pelo tipo e liga os campos **na ordem em que foram declarados**."},
  {"p": "**Record por nome**"},
  { code: `point Usuario(nome := n, idade := i):`, lang: 'df' },
  {"p": "Casa pelo tipo e liga só os campos citados, **pelo nome**. Preferível quando o record tem muitos campos ou quando você só precisa de dois deles."},
  {"p": "**Testar um valor específico**"},
  { code: `point Usuario(papel := "admin"):`, lang: 'df' },
  {"p": "Aqui `\"admin\"` é um literal, não uma captura: casa apenas quando o campo `papel` vale exatamente isso. Um teste de tipo e um teste de valor na mesma linha."},
  {"h3": "Padrões de vault"},
  { code: `point {"metodo": "GET", "rota": r}:
    yield $"lendo {r}"`, lang: 'df' },
  {"p": "O casamento é **parcial**: o vault precisa ter as chaves citadas, mas pode ter outras. Por isso `{\"metodo\": \"GET\", \"rota\": \"/x\", \"extra\": 1}` casa normalmente."},
  {"p": "Essa é a escolha certa para dados que vêm de fora — um JSON de API sempre traz campos que você não usa, e exigir correspondência exata quebraria a cada mudança do fornecedor."},
  {"h3": "O roteador em oito linhas"},
  { code: `match req:
    point {"metodo": "GET", "rota": r}:
    point {"metodo": "POST", "rota": r, "corpo": c}:
    point {"metodo": m}:
    default:`, lang: 'df' },
  {"p": "Cada linha diz simultaneamente **o formato esperado** e **como extrair os dados**. Sem pattern matching, isso seria uma escada de `given req[\"metodo\"] is …` com verificações de chave espalhadas."},
  {"h3": "Saída esperada"},
  { code: `acesso total
Kid e menor: acesso limitado
Ana: acesso padrao
lendo /usuarios
criando em /usuarios com 1 campos
metodo DELETE nao suportado
requisicao invalida`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `point {\"metodo\": \"PUT\", \"rota\": r, \"id\": i}`.", "Use `...resto` no padrão de vault para capturar as chaves não citadas."]},
  {"h2": "143 · Guardas e ligacao com as"},
  {"p": "**Enunciado.** combine condicoes e apelidos para casos precisos."},
  { code: `action faixa(n):
    match n:
        point Integer as v when v smaller 0:
            yield "negativo"
        point 0:
            yield "zero"
        point Integer as v when v smaller_eq 9:
            yield "unidade"
        point Integer as v when v smaller_eq 99:
            yield "dezena"
        point Integer:
            yield "grande"
        default:
            yield "nao e inteiro"

cycle n in [-5, 0, 7, 42, 1000, "x"]:
    out $"{n} -> {faixa(n)}"

assert faixa(-5) is "negativo", "negativo"
assert faixa(0) is "zero", "zero vem antes da faixa das unidades"
assert faixa(7) is "unidade", "unidade"
assert faixa(42) is "dezena", "dezena"
assert faixa(1000) is "grande", "sem guarda, pega o resto"

// 'as' liga o valor inteiro, mesmo em padroes compostos
action analisar(lista):
    match lista:
        point [a, b] as tudo when a is b:
            yield $"par repetido {tudo}"
        point [a, b] as tudo:
            yield $"par distinto {tudo}"
        point [] as vazia:
            yield $"vazia {vazia}"
        default:
            yield "outro"

out analisar([3, 3])
out analisar([1, 2])
assert analisar([3, 3]) is "par repetido [3, 3]", "as guarda a lista toda"

// Guarda que usa nomes ligados no proprio padrao
record Pedido:
    itens: Cluster
    total: Number

action revisar(p):
    match p:
        point Pedido(itens := i, total := t) when len(i) is 0 and t bigger 0:
            yield "inconsistente: total sem itens"
        point Pedido(itens := i) when len(i) is 0:
            yield "pedido vazio"
        point Pedido(total := t) when t bigger 1000:
            yield "pedido grande"
        point Pedido:
            yield "pedido normal"
        default:
            yield "?"

out revisar(Pedido([], 500))
out revisar(Pedido([], 0))
out revisar(Pedido(["a"], 2000))
out revisar(Pedido(["a"], 50))

assert revisar(Pedido([], 500)) is "inconsistente: total sem itens", "duas condicoes"
assert revisar(Pedido(["a"], 2000)) is "pedido grande", "guarda no total"`, lang: 'df', title: `exercicios/14-pattern-matching/143_guardas_e_binding.df` },
  {"h3": "Conceitos"},
  {"p": "**`when` — a guarda**"},
  {"p": "Roda **depois** que o padrão casou. Se for falsa, o `match` continua para o próximo `point`:"},
  { code: `point Integer as v when v smaller 0:
    yield "negativo"
point Integer as v when v smaller_eq 9:
    yield "unidade"`, lang: 'df' },
  {"p": "O primeiro casa o tipo, liga `v`, testa a condição. Falhou? Tenta o próximo."},
  {"p": "Isso permite escrever faixas de forma direta, sem repetir o teste de tipo em cada ramo."},
  {"p": "**`as` — o apelido**"},
  {"p": "Liga o valor **que casou**, não uma parte dele:"},
  { code: `point [a, b] as tudo when a is b:
    yield $"par repetido {tudo}"`, lang: 'df' },
  {"p": "Aqui `a` e `b` são os elementos e `tudo` é a lista inteira. Sem `as`, você teria que remontar `[a, b]` para exibi-la."},
  {"h3": "A guarda enxerga o que o padrão ligou"},
  {"p": "Este é o ponto que dá poder à combinação:"},
  { code: `point Pedido(itens := i, total := t) when len(i) is 0 and t bigger 0:
    yield "inconsistente: total sem itens"`, lang: 'df' },
  {"p": "O padrão extrai `itens` e `total`; a guarda os relaciona. Você acabou de expressar uma **regra de negócio** — \"não pode haver total sem itens\" — como um único caso do `match`."},
  {"h3": "Ordenar por especificidade"},
  {"p": "Com guardas, a ordem passa a codificar a lógica:"},
  { code: `point Pedido(itens := i, total := t) when len(i) is 0 and t bigger 0:   // 2 condições
point Pedido(itens := i) when len(i) is 0:                             // 1 condição
point Pedido(total := t) when t bigger 1000:                           // 1 condição
point Pedido:                                                          // nenhuma`, lang: 'df' },
  {"p": "Do mais restrito ao mais amplo. Invertida, a ordem faria os casos específicos nunca serem alcançados — e nenhum erro apareceria, só o comportamento errado."},
  {"h3": "Saída esperada"},
  { code: `-5 -> negativo
0 -> zero
7 -> unidade
42 -> dezena
1000 -> grande
x -> nao e inteiro
par repetido [3, 3]
par distinto [1, 2]
inconsistente: total sem itens
pedido vazio
pedido grande
pedido normal`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Mova `point Integer:` (sem guarda) para o topo e veja tudo virar \"grande\".", "Acrescente uma faixa de milhares entre \"dezena\" e \"grande\"."]},
  {"h2": "144 · Projeto: validador de dados"},
  {"p": "**Enunciado.** junte padroes de tipo, sequencia e vault num validador de esquema."},
  { code: `// Um validador que percorre dados e um esquema em paralelo.
// Esquema: {"tipo": "String"} ou {"tipo": "Cluster", "de": <esquema>}
//          ou {"tipo": "Vault", "campos": {<nome>: <esquema>}}

action validar(dado, esquema, caminho := "raiz"):
    problemas := []
    esperado := esquema["tipo"]

    match esquema:
        point {"tipo": "Cluster", "de": interno}:
            given typeof(dado) isnt "Cluster":
                problemas.append($"{caminho}: esperava Cluster, veio {typeof(dado)}")
                yield problemas
            cycle i from 0 to len(dado) - 1:
                cycle p in validar(dado[i], interno, $"{caminho}[{i}]"):
                    problemas.append(p)

        point {"tipo": "Vault", "campos": campos}:
            given typeof(dado) isnt "Vault":
                problemas.append($"{caminho}: esperava Vault, veio {typeof(dado)}")
                yield problemas
            cycle nome in campos.keys():
                given nome not in dado:
                    problemas.append($"{caminho}.{nome}: campo obrigatorio ausente")
                otherwise:
                    cycle p in validar(dado[nome], campos[nome], $"{caminho}.{nome}"):
                        problemas.append(p)

        default:
            given typeof(dado) isnt esperado:
                problemas.append($"{caminho}: esperava {esperado}, veio {typeof(dado)}")

    yield problemas

esquema_usuario := {
    "tipo": "Vault",
    "campos": {
        "nome": {"tipo": "String"},
        "idade": {"tipo": "Integer"},
        "tags": {"tipo": "Cluster", "de": {"tipo": "String"}}
    }
}

bom := {"nome": "Ana", "idade": 30, "tags": ["admin", "dev"]}
ruim := {"nome": 42, "tags": ["ok", 7]}

out "── dados validos ──"
out validar(bom, esquema_usuario)

out ""
out "── dados invalidos ──"
cycle p in validar(ruim, esquema_usuario):
    out $"  {p}"

assert len(validar(bom, esquema_usuario)) is 0, "dados bons passam"
achados := validar(ruim, esquema_usuario)
assert len(achados) is 3, "nome errado, idade ausente, tag errada"
out ""
out $"{len(achados)} problema(s) encontrados"`, lang: 'df', title: `exercicios/14-pattern-matching/144_interpretador_json.df` },
  {"h3": "O problema"},
  {"p": "Dados que vêm de fora — JSON de uma API, CSV, formulário — não têm garantia de formato. Validar campo a campo com `given` espalhado pelo código não escala: a regra fica misturada com a lógica de negócio, e cada campo novo exige mexer em vários lugares."},
  {"p": "A saída é **declarar o formato como dado** e escrever um interpretador para ele."},
  {"h3": "O esquema"},
  { code: `esquema_usuario := {
    "tipo": "Vault",
    "campos": {
        "nome": {"tipo": "String"},
        "idade": {"tipo": "Integer"},
        "tags": {"tipo": "Cluster", "de": {"tipo": "String"}}
    }
}`, lang: 'df' },
  {"p": "Três formas, recursivamente compostas:"},
  {"table": {"head": ["Forma", "Significa"], "rows": [["`{\"tipo\": \"String\"}`", "um valor daquele tipo"], ["`{\"tipo\": \"Cluster\", \"de\": E}`", "uma lista cujos itens seguem `E`"], ["`{\"tipo\": \"Vault\", \"campos\": {…}}`", "um objeto com aqueles campos"]]}},
  {"h3": "O validador"},
  {"p": "O `match` sobre o **esquema** escolhe a estratégia:"},
  { code: `match esquema:
    point {"tipo": "Cluster", "de": interno}:
        // valida cada item contra 'interno'
    point {"tipo": "Vault", "campos": campos}:
        // valida cada campo declarado
    default:
        // tipo simples: compara com typeof`, lang: 'df' },
  {"p": "Repare que os dois primeiros padrões extraem exatamente o que precisam (`interno`, `campos`) ao mesmo tempo em que identificam a forma."},
  {"h3": "Caminhos nas mensagens"},
  {"p": "O parâmetro `caminho` acumula a posição:"},
  { code: `raiz.nome: esperava String, veio Integer
raiz.tags[1]: esperava String, veio Integer`, lang: 'text' },
  {"p": "Isso transforma um relatório inútil (\"dados inválidos\") em algo acionável. Custa um parâmetro a mais e paga por si na primeira vez que alguém precisa depurar um JSON aninhado."},
  {"h3": "Coletar em vez de parar no primeiro"},
  {"p": "O validador devolve **todos** os problemas, não só o primeiro. Quem preencheu um formulário quer ver os três erros de uma vez."},
  {"h3": "Saída esperada"},
  { code: `── dados validos ──
[]

── dados invalidos ──
  raiz.nome: esperava String, veio Integer
  raiz.idade: campo obrigatorio ausente
  raiz.tags[1]: esperava String, veio Integer

3 problema(s) encontrados`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `{\"tipo\": \"String\", \"opcional\": yes}` e trate campos opcionais.", "Adicione validação de faixa: `{\"tipo\": \"Integer\", \"min\": 0, \"max\": 150}`.", "Faça o validador aceitar `{\"tipo\": \"Enum\", \"valores\": [...]}`."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/14-pattern-matching/139_padroes_basicos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '139-padroes-basicos', text: "139 · Padroes basicos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'a-convencao-maiusculaminuscula', text: "A convenção maiúscula/minúscula", level: 3 as const }, { id: 'a-ordem-e-tudo', text: "A ordem é tudo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '140-padroes-de-tipo', text: "140 · Padroes de tipo", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'tipos-aceitos', text: "Tipos aceitos", level: 3 as const }, { id: 'number-e-any', text: "`Number` e `Any`", level: 3 as const }, { id: 'guardas-com-when', text: "Guardas com `when`", level: 3 as const }, { id: 'por-que-when-e-nao-given', text: "Por que `when` e não `given`", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '141-padroes-de-sequencia', text: "141 · Padroes de sequencia", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'so-sequencias-de-verdade', text: "Só sequências de verdade", level: 3 as const }, { id: 'literais-dentro-do-padrao', text: "Literais dentro do padrão", level: 3 as const }, { id: 'padroes-aninhados', text: "Padrões aninhados", level: 3 as const }, { id: 'cabeca-e-cauda-o-padrao-recursivo', text: "Cabeça e cauda: o padrão recursivo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '142-padroes-de-record-e-vault', text: "142 · Padroes de record e vault", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'padroes-de-vault', text: "Padrões de vault", level: 3 as const }, { id: 'o-roteador-em-oito-linhas', text: "O roteador em oito linhas", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '143-guardas-e-ligacao-com-as', text: "143 · Guardas e ligacao com as", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'a-guarda-enxerga-o-que-o-padrao-ligou', text: "A guarda enxerga o que o padrão ligou", level: 3 as const }, { id: 'ordenar-por-especificidade', text: "Ordenar por especificidade", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '144-projeto-validador-de-dados', text: "144 · Projeto: validador de dados", level: 2 as const }, { id: 'o-problema', text: "O problema", level: 3 as const }, { id: 'o-esquema', text: "O esquema", level: 3 as const }, { id: 'o-validador', text: "O validador", level: 3 as const }, { id: 'caminhos-nas-mensagens', text: "Caminhos nas mensagens", level: 3 as const }, { id: 'coletar-em-vez-de-parar-no-primeiro', text: "Coletar em vez de parar no primeiro", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"14 · Pattern matching"}
      description={"6 exercícios: point, when, tipos, sequências e vaults."}
      href={"/docs/exercicios/14-pattern-matching"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
