// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "13 · Desestruturação",
  description: "6 exercícios: cluster, vault, rest e troca de variáveis.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 13`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[133](#133-desestruturacao-de-listas)", "**Desestruturacao de listas**", "extraia varios valores de uma lista numa unica linha."], ["[134](#134-resto-e-spread)", "**Resto e spread**", "colete o que sobra com ...resto e expanda colecoes com ..."], ["[135](#135-desestruturar-records-e-vaults)", "**Desestruturar records e vaults**", "extraia campos nomeados de um record ou de um dicionario."], ["[136](#136-compreensao-de-listas)", "**Compreensao de listas**", "construa listas transformando e filtrando numa unica expressao."], ["[137](#137-compreensao-de-vaults)", "**Compreensao de vaults**", "construa dicionarios com a mesma sintaxe, produzindo chave e valor."], ["[138](#138-interpolacao-de-strings)", "**Interpolacao de strings**", "monte textos com valores embutidos, sem concatenacao manual."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "133 · Desestruturacao de listas"},
  {"p": "**Enunciado.** extraia varios valores de uma lista numa unica linha."},
  { code: `// Forma basica: um nome para cada posicao
a, b := [1, 2]
out a, b
assert a is 1 and b is 2, "dois valores"

x, y, z := [10, 20, 30]
assert x + y + z is 60, "tres valores"

// Troca sem variavel temporaria
p := "primeiro"
q := "segundo"
p, q := q, p
out p, q
assert p is "segundo", "troca"

// Quantidade errada e erro, nao silencio
erro := no
monitor:
    m, n := [1, 2, 3]
handle e:
    erro := yes
    out e.message
assert erro is yes, "3 valores nao cabem em 2 nomes"

// Desestruturar dentro de um laco
pares := [[1, "um"], [2, "dois"], [3, "tres"]]
cycle par in pares:
    numero, palavra := par
    out $"{numero} = {palavra}"

// Retornar varios valores de uma acao
action divide_com_resto(a, b):
    yield [a ~/ b, a % b]

quociente, resto := divide_com_resto(17, 5)
out $"17 / 5 = {quociente} resto {resto}"
assert quociente is 3 and resto is 2, "divisao com resto"`, lang: 'df', title: `exercicios/13-desestruturacao/133_desestruturar_listas.df` },
  {"h3": "Conceitos"},
  { code: `a, b := [1, 2]`, lang: 'df' },
  {"p": "Uma atribuição, dois nomes. O lado direito é percorrido e cada elemento vai para o nome correspondente."},
  {"h3": "A troca sem temporária"},
  { code: `p, q := q, p`, lang: 'df' },
  {"p": "O lado direito é avaliado **inteiro antes** de qualquer atribuição acontecer. Por isso não há variável temporária nem risco de sobrescrever `p` antes de ler."},
  {"p": "Comparando: em C você escreveria três linhas com um `tmp`. Aqui é uma."},
  {"h3": "Quantidade errada falha"},
  { code: `m, n := [1, 2, 3]
// erro: Cannot unpack 3 value(s) into 2 name(s)`, lang: 'df' },
  {"p": "Isso é deliberado. Um `[1, 2, 3]` chegando onde se esperavam dois valores quase sempre significa que a suposição sobre os dados estava errada — e falhar alto é melhor que descartar o `3` em silêncio."},
  {"p": "Quando a sobra é esperada, existe `...resto` (próximo exercício)."},
  {"h3": "Retornando vários valores"},
  {"p": "DataForge não tem tuplas separadas de listas. Devolver vários valores é devolver uma lista, e quem chama desestrutura:"},
  { code: `action divide_com_resto(a, b):
    yield [a ~/ b, a % b]

quociente, resto := divide_com_resto(17, 5)`, lang: 'df' },
  {"p": "Isso lê melhor que `resultado[0]` e `resultado[1]` espalhados pelo código."},
  {"h3": "Saída esperada"},
  { code: `1 2
segundo primeiro
Cannot unpack 3 value(s) into 2 name(s)
1 = um
2 = dois
3 = tres
17 / 5 = 3 resto 2`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Desestruture direto no cabeçalho: `cycle` ainda não aceita, mas `numero,"]},
  {"p": "palavra := par` na primeira linha resolve."},
  {"list": ["Escreva `action min_max(lista)` devolvendo os dois extremos."]},
  {"h2": "134 · Resto e spread"},
  {"p": "**Enunciado.** colete o que sobra com ...resto e expanda colecoes com ..."},
  { code: `// ...resto captura o que sobrou
primeiro, ...outros := [1, 2, 3, 4, 5]
out primeiro, outros
assert primeiro is 1, "cabeca"
assert outros is [2, 3, 4, 5], "cauda"

// O resto pode estar no meio
inicio, ...meio, fim := [1, 2, 3, 4, 5]
out inicio, meio, fim
assert meio is [2, 3, 4], "o meio"
assert fim is 5, "o ultimo"

// Resto vazio e valido
so_um, ...nada := [9]
assert nada is [], "resto pode ser vazio"

// Spread expande na construcao
a := [1, 2]
b := [3, 4]
juntos := [...a, ...b, 5]
out juntos
assert juntos is [1, 2, 3, 4, 5], "concatenacao com spread"

// Spread em vaults: o ultimo vence
padrao := {"tema": "claro", "fonte": 14}
usuario := {"tema": "escuro"}
final := {...padrao, ...usuario}
out final
assert final is {"tema": "escuro", "fonte": 14}, "usuario sobrescreve padrao"

// Spread em chamadas
action somar_tres(a, b, c):
    yield a + b + c

args := [10, 20, 30]
out somar_tres(...args)
assert somar_tres(...args) is 60, "argumentos expandidos"

// Copia rasa: o novo nao e o mesmo objeto
original := [1, 2, 3]
copia := [...original]
copia.append(4)
out original, copia
assert original is [1, 2, 3], "o original nao mudou"
assert copia is [1, 2, 3, 4], "a copia mudou"`, lang: 'df', title: `exercicios/13-desestruturacao/134_resto_e_spread.df` },
  {"h3": "Conceitos"},
  {"p": "`...` faz dois trabalhos opostos, distinguidos pelo lado em que aparece."},
  {"p": "**À esquerda do `:=` — **coleta****"},
  { code: `primeiro, ...outros := [1, 2, 3, 4, 5]
// primeiro = 1
// outros   = [2, 3, 4, 5]`, lang: 'df' },
  {"p": "O resto pode estar em qualquer posição, inclusive no meio:"},
  { code: `inicio, ...meio, fim := [1, 2, 3, 4, 5]
// inicio = 1, meio = [2, 3, 4], fim = 5`, lang: 'df' },
  {"p": "Só é permitido **um** `...resto` por desestruturação — com dois, não haveria como saber onde um termina e o outro começa."},
  {"p": "**À direita — **expande****"},
  { code: `juntos := [...a, ...b, 5]
final  := {...padrao, ...usuario}
soma   := somar_tres(...args)`, lang: 'df' },
  {"h3": "O padrão de configuração"},
  {"p": "Esta é a aplicação mais comum do spread em vaults:"},
  { code: `padrao := {"tema": "claro", "fonte": 14}
usuario := {"tema": "escuro"}
final := {...padrao, ...usuario}       // {tema: escuro, fonte: 14}`, lang: 'df' },
  {"p": "**O último vence.** As preferências do usuário sobrescrevem o padrão; o que ele não definiu vem do padrão. Uma linha resolve o que normalmente seriam cinco."},
  {"h3": "Cópia rasa"},
  { code: `copia := [...original]`, lang: 'df' },
  {"p": "Isso cria uma lista **nova**. Alterar `copia` não toca em `original`. É \"rasa\" porque objetos *dentro* da lista continuam compartilhados — para uma cópia profunda existe `deep_copy`."},
  {"h3": "Comparando"},
  {"table": {"head": ["DataForge", "JavaScript", "Python"], "rows": [["`a, ...r := lista`", "`const [a, ...r] = lista`", "`a, *r = lista`"], ["`[...a, ...b]`", "`[...a, ...b]`", "`[*a, *b]`"], ["`{...a, ...b}`", "`{...a, ...b}`", "`{**a, **b}`"], ["`f(...args)`", "`f(...args)`", "`f(*args)`"]]}},
  {"h3": "Saída esperada"},
  { code: `1 [2, 3, 4, 5]
1 [2, 3, 4] 5
[1, 2, 3, 4, 5]
{tema: escuro, fonte: 14}
60
[1, 2, 3] [1, 2, 3, 4]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Escreva `a, ...m, ...n := [1,2,3]` e leia o erro.", "Use spread para inserir no meio: `[...antes, novo, ...depois]`."]},
  {"h2": "135 · Desestruturar records e vaults"},
  {"p": "**Enunciado.** extraia campos nomeados de um record ou de um dicionario."},
  { code: `record Usuario:
    nome: String
    idade: Integer
    cidade: String

u := Usuario("Ana", 30, "Floripa")

// Por nome, na ordem que quiser
{nome, cidade} := u
out $"{nome} mora em {cidade}"
assert nome is "Ana" and cidade is "Floripa", "campos por nome"

// Funciona igual em vaults
config := {"host": "localhost", "porta": 8080, "debug": yes}
{host, porta} := config
out $"{host}:{porta}"
assert host is "localhost" and porta is 8080, "chaves do vault"

// Chave inexistente e erro
erro := no
monitor:
    {inexistente} := config
handle e:
    erro := yes
    out e.message
assert erro is yes, "chave que nao existe dispara"

// Resto captura os campos restantes
{nome, ...resto} := u
out resto
assert resto is {"idade": 30, "cidade": "Floripa"}, "resto do record"

// Padrao util: desempacotar no inicio da acao
action apresentar(pessoa):
    {nome, idade} := pessoa
    yield $"{nome}, {idade} anos"

out apresentar(u)
out apresentar(Usuario("Bruno", 25, "Recife"))
assert apresentar(u) is "Ana, 30 anos", "desempacota no inicio"

// Tambem funciona em pattern matching
action saudacao(p):
    match p:
        point Usuario(nome := n, idade := i) when i smaller 18:
            yield $"oi, {n}"
        point Usuario(nome := n):
            yield $"bom dia, {n}"
        default:
            yield "?"

out saudacao(u), saudacao(Usuario("Kid", 12, "SP"))
assert saudacao(Usuario("Kid", 12, "SP")) is "oi, Kid", "menor de idade"`, lang: 'df', title: `exercicios/13-desestruturacao/135_desestruturar_registros.df` },
  {"h3": "Conceitos"},
  {"p": "Com chaves, a desestruturação passa a ser **por nome**:"},
  { code: `{nome, cidade} := u`, lang: 'df' },
  {"p": "A ordem não importa — `{cidade, nome}` daria o mesmo resultado. Isso é o oposto da forma com colchetes, onde a posição é tudo."},
  {"table": {"head": ["Forma", "Casa por", "Fonte"], "rows": [["`a, b := …`", "posição", "lista, record"], ["`{a, b} := …`", "nome", "vault, record, instância"]]}},
  {"h3": "Chave ausente falha"},
  { code: `{inexistente} := config
// erro: Vault has no key 'inexistente' to destructure. Keys: host, porta, debug`, lang: 'df' },
  {"p": "A mensagem lista as chaves que existem — quase sempre o erro é um nome digitado errado, e ver a lista resolve na hora."},
  {"h3": "Resto nomeado"},
  { code: `{nome, ...resto} := u
// nome  = "Ana"
// resto = {idade: 30, cidade: "Floripa"}`, lang: 'df' },
  {"p": "Útil para \"pegue esses dois campos e passe o resto adiante\" — um padrão comum ao tratar requisições HTTP."},
  {"h3": "O padrão de desempacotar no início"},
  { code: `action apresentar(pessoa):
    {nome, idade} := pessoa
    yield $"{nome}, {idade} anos"`, lang: 'df' },
  {"p": "Duas vantagens sobre usar `pessoa.nome` no corpo inteiro:"},
  {"p": "1. A primeira linha **documenta** o que a ação consome. 2. O resto do corpo fica mais curto e legível."},
  {"h3": "E no pattern matching"},
  {"p": "Dentro de um `point`, a mesma ideia aparece com `campo := padrao`:"},
  { code: `point Usuario(nome := n, idade := i) when i smaller 18:
    yield $"oi, {n}"`, lang: 'df' },
  {"p": "Isso casa pelo tipo, extrai dois campos **por nome** e ainda aplica uma guarda."},
  {"h3": "Saída esperada"},
  { code: `Ana mora em Floripa
localhost:8080
Vault has no key 'inexistente' to destructure. Keys: host, porta, debug
{idade: 30, cidade: Floripa}
Ana, 30 anos
Bruno, 25 anos
bom dia, Ana oi, Kid`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Desestruture um vault aninhado em dois passos.", "Escreva uma ação que recebe `{...opcoes}` e mescla com um padrão."]},
  {"h2": "136 · Compreensao de listas"},
  {"p": "**Enunciado.** construa listas transformando e filtrando numa unica expressao."},
  { code: `nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Transformar
quadrados := [n * n cycle n in nums]
out quadrados
assert quadrados[0] is 1 and quadrados[9] is 100, "quadrados"

// Filtrar
pares := [n cycle n in nums given n % 2 is 0]
out pares
assert pares is [2, 4, 6, 8, 10], "so os pares"

// Transformar e filtrar juntos
dobro_dos_impares := [n * 2 cycle n in nums given n % 2 is 1]
out dobro_dos_impares
assert dobro_dos_impares is [2, 6, 10, 14, 18], "dobro dos impares"

// Sobre texto
letras := [c.upper() cycle c in "dataforge" given c isnt "a"]
out letras.join("")
assert letras.join("") is "DTFORGE", "sem os a"

// Aninhada: duas fontes
tabuada := [$"{a}x{b}={a * b}" cycle a in [2, 3] cycle b in [1, 2, 3]]
out tabuada
assert len(tabuada) is 6, "2 x 3 combinacoes"

// Sobre registros
pessoas := [
    {"nome": "Ana", "idade": 30},
    {"nome": "Bruno", "idade": 17},
    {"nome": "Carla", "idade": 25}
]
adultos := [p["nome"] cycle p in pessoas given p["idade"] bigger_eq 18]
out adultos
assert adultos is ["Ana", "Carla"], "nomes dos adultos"

// A variavel do cycle nao vaza
_ := [i cycle i in [1, 2]]
vazou := yes
monitor:
    out i
handle e:
    vazou := no
assert vazou is no, "i so existe dentro da compreensao"`, lang: 'df', title: `exercicios/13-desestruturacao/136_comprehension_lista.df` },
  {"h3": "Conceitos"},
  {"p": "A forma geral:"},
  { code: `[ <expressão>  cycle <nome> in <fonte>  [given <condição>] ]`, lang: 'text' },
  {"p": "Lê-se: *\"a expressão, para cada nome na fonte, dado que a condição vale\"*."},
  { code: `quadrados := [n * n cycle n in nums]
pares     := [n cycle n in nums given n % 2 is 0]`, lang: 'df' },
  {"p": "Repare que a compreensão **reutiliza palavras que você já conhece** — `cycle` e `given` são as mesmas dos laços e condicionais. Não há sintaxe nova para memorizar."},
  {"h3": "Comparando com o laço equivalente"},
  { code: `// laço
quadrados := []
cycle n in nums:
    quadrados.append(n * n)

// compreensão
quadrados := [n * n cycle n in nums]`, lang: 'df' },
  {"p": "A compreensão diz **o que** você quer; o laço diz **como** obter. Para transformações simples, a primeira é mais direta. Para lógica com vários passos, o laço continua sendo a escolha certa — não force tudo numa linha."},
  {"h3": "Compreensão ou pipeline?"},
  {"p": "DataForge tem as duas:"},
  { code: `[n * 2 cycle n in nums given n % 2 is 1]
nums >> sift n: n % 2 is 1 >> morph n: n * 2`, lang: 'df' },
  {"p": "Quando escolher cada uma:"},
  {"table": {"head": ["Situação", "Prefira"], "rows": [["um filtro e uma transformação", "compreensão"], ["vários estágios encadeados", "pipeline"], ["duas fontes combinadas", "compreensão"], ["terminar com uma redução", "pipeline (`distill`)"]]}},
  {"h3": "Múltiplas fontes"},
  { code: `[$"{a}x{b}" cycle a in [2, 3] cycle b in [1, 2, 3]]`, lang: 'df' },
  {"p": "O `cycle` da direita gira mais rápido — é o laço interno. O resultado tem `2 × 3 = 6` itens."},
  {"h3": "Escopo"},
  {"p": "A variável do `cycle` **não vaza**:"},
  { code: `_ := [i cycle i in [1, 2]]
out i        // erro: Undefined name 'i'`, lang: 'df' },
  {"p": "Isso evita o bug clássico de reaproveitar sem querer o `i` de uma compreensão anterior."},
  {"h3": "Saída esperada"},
  { code: `[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
[2, 4, 6, 8, 10]
[2, 6, 10, 14, 18]
DTFORGE
[2x1=2, 2x2=4, 2x3=6, 3x1=3, 3x2=6, 3x3=9]
[Ana, Carla]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Reescreva `dobro_dos_impares` como pipeline e compare.", "Gere os pares `[a, b]` com `a smaller b` a partir de `[1,2,3]`."]},
  {"h2": "137 · Compreensao de vaults"},
  {"p": "**Enunciado.** construa dicionarios com a mesma sintaxe, produzindo chave e valor."},
  { code: `nums := [1, 2, 3, 4, 5]

// Chave e valor a partir de uma fonte
quadrados := {n: n * n cycle n in nums}
out quadrados
assert quadrados[4] is 16, "chave 4 mapeia para 16"

// Filtrando
pares := {n: n * n cycle n in nums given n % 2 is 0}
out pares
assert len(pares.keys()) is 2, "so 2 e 4"

// Inverter um dicionario
originais := {"a": 1, "b": 2, "c": 3}
invertido := {originais[k]: k cycle k in originais.keys()}
out invertido
assert invertido[2] is "b", "valor virou chave"

// Indexar registros por um campo
pessoas := [
    {"id": 10, "nome": "Ana"},
    {"id": 20, "nome": "Bruno"}
]
por_id := {p["id"]: p["nome"] cycle p in pessoas}
out por_id
assert por_id[20] is "Bruno", "acesso direto por id"

// Contar ocorrencias
palavras := ["sol", "lua", "sol", "mar", "sol", "lua"]
distintas := unique(palavras)
contagem := {p: palavras.count(p) cycle p in distintas}
out contagem
assert contagem["sol"] is 3, "sol aparece 3 vezes"

// Normalizar chaves de entrada
bruto := {"  Nome ": "Ana", "IDADE": 30}
limpo := {k.trim().lower(): bruto[k] cycle k in bruto.keys()}
out limpo
assert "nome" in limpo, "chave normalizada"
assert limpo["idade"] is 30, "valor preservado"`, lang: 'df', title: `exercicios/13-desestruturacao/137_comprehension_vault.df` },
  {"h3": "Conceitos"},
  {"p": "A única diferença para a compreensão de lista é que a expressão vira um par:"},
  { code: `{ <chave>: <valor>  cycle <nome> in <fonte>  [given <condição>] }`, lang: 'text' },
  { code: `quadrados := {n: n * n cycle n in nums}
// {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}`, lang: 'df' },
  {"h3": "Percorrendo um vault"},
  {"p": "`cycle k in umVault` percorre as **chaves**, não os pares. Para chegar ao valor, indexe:"},
  { code: `invertido := {originais[k]: k cycle k in originais.keys()}`, lang: 'df' },
  {"p": "Isso é consistente com `\"chave\" in vault`, que também testa chaves."},
  {"h3": "Três aplicações que valem memorizar"},
  {"p": "**Indexar por um campo**"},
  {"p": "Transformar uma lista num índice de acesso direto:"},
  { code: `por_id := {p["id"]: p["nome"] cycle p in pessoas}
out por_id[20]        // "Bruno" — sem varrer a lista`, lang: 'df' },
  {"p": "De busca linear para acesso direto, numa linha."},
  {"p": "**Contar ocorrências**"},
  { code: `distintas := unique(palavras)
contagem := {p: palavras.count(p) cycle p in distintas}`, lang: 'df' },
  {"p": "Para listas grandes prefira `Arcane.Collections.counter`, que percorre uma vez só em vez de uma vez por item distinto."},
  {"p": "**Normalizar chaves**"},
  { code: `limpo := {k.trim().lower(): bruto[k] cycle k in bruto.keys()}`, lang: 'df' },
  {"p": "Dados de fora chegam com espaços e caixa inconsistentes. Normalizar na fronteira evita ter que lembrar disso no resto do programa."},
  {"h3": "Chaves repetidas"},
  {"p": "Se duas iterações produzem a mesma chave, **a última vence** — mesma regra do spread. Isso é silencioso, então cuidado ao usar como chave algo que pode se repetir."},
  {"h3": "Saída esperada"},
  { code: `{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
{2: 4, 4: 16}
{1: a, 2: b, 3: c}
{10: Ana, 20: Bruno}
{sol: 3, lua: 2, mar: 1}
{nome: Ana, idade: 30}`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Agrupe as pessoas por faixa etária em vez de indexar por id.", "Compare a contagem manual com `Arcane.Collections.counter`."]},
  {"h2": "138 · Interpolacao de strings"},
  {"p": "**Enunciado.** monte textos com valores embutidos, sem concatenacao manual."},
  { code: `nome := "Ana"
idade := 30
saldo := 1234.5

// Basico
out $"Ola, {nome}!"
assert $"Ola, {nome}!" is "Ola, Ana!", "interpolacao simples"

// Qualquer expressao dentro das chaves
out $"{nome} tem {idade} anos e fara {idade + 1} no proximo aniversario"
out $"metade do saldo: {saldo / 2}"
assert $"{idade + 1}" is "31", "expressao aritmetica"

// Chamadas de acao
action moeda(v):
    yield $"R$ {round(v, 2)}"

out $"saldo formatado: {moeda(saldo)}"
assert moeda(1234.5) is "R$ 1234.5", "acao dentro da interpolacao"

// Acesso a campos e indices
usuario := {"nome": "Bruno", "tags":["admin", "dev"]}
out $"{usuario["nome"]} e {usuario["tags"][0]}"
assert $"{usuario["tags"][0]}" is "admin", "indice dentro da chave"

// Booleanos e void seguem a grafia da linguagem
out $"ativo={yes} vazio={void}"
assert $"{yes} {no} {void}" is "yes no void", "grafia DataForge"

// Chaves literais: dobre
out $"{{isso e literal}} e {nome} e interpolado"
assert $"{{x}}" is "{x}", "chaves duplicadas escapam"

// Comparando com concatenacao
antigo := "Ola, " + nome + "! Voce tem " + str(idade) + " anos."
novo := $"Ola, {nome}! Voce tem {idade} anos."
out antigo
out novo
assert antigo is novo, "as duas formas produzem o mesmo texto"

// Montando um relatorio
itens := [{"produto":"Mouse", "qtd":2, "preco":80.0}]
cycle i in itens:
    out $"{i["produto"].pad_end(10)} {i["qtd"]}x  {moeda(i["preco"] * i["qtd"])}"`, lang: 'df', title: `exercicios/13-desestruturacao/138_interpolacao.df` },
  {"h3": "Conceitos"},
  {"p": "Uma string prefixada por `$` interpreta `{…}` como expressão:"},
  { code: `out $"Ola, {nome}!"`, lang: 'df' },
  {"p": "Compare com a alternativa:"},
  { code: `"Ola, " + nome + "! Voce tem " + str(idade) + " anos."
$"Ola, {nome}! Voce tem {idade} anos."`, lang: 'df' },
  {"p": "A segunda tem menos ruído, menos `+` e nenhum `str()` — a conversão é automática."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`f\"Ola, {nome}\"`"], ["JavaScript", "`` `Ola, ${nome}` ``"], ["C#", "`$\"Ola, {nome}\"`"], ["Kotlin", "`\"Ola, $nome\"`"]]}},
  {"h3": "Por que o `$` é obrigatório"},
  {"p": "Strings comuns **não** interpolam:"},
  { code: `out "{nome}"      // sai literalmente: {nome}
out $"{nome}"     // sai: Ana`, lang: 'df' },
  {"p": "Isso preserva o código existente e permite escrever JSON, regex e templates de outros sistemas sem escapar nada."},
  {"h3": "O que cabe dentro das chaves"},
  {"p": "Qualquer expressão:"},
  { code: `$"{idade + 1}"                    // aritmética
$"{moeda(saldo)}"                 // chamada de ação
$"{usuario["tags"][0]}"           // índices e chaves
$"{"par" given n % 2 is 0 otherwise "impar"}"    // ternário`, lang: 'df' },
  {"p": "Inclusive strings com aspas duplas dentro — o lexer acompanha o aninhamento."},
  {"h3": "Formatação segue a linguagem"},
  {"p": "Os valores são convertidos com as mesmas regras de `out`:"},
  { code: `$"{yes} {no} {void}"     // "yes no void", não "True False None"`, lang: 'df' },
  {"p": "Um record com `toString` usa o seu `toString`. Uma lista sai como `[1, 2, 3]`."},
  {"h3": "Chaves literais"},
  {"p": "Para uma chave de verdade no texto, dobre:"},
  { code: `$"{{isso e literal}}"     // {isso e literal}`, lang: 'df' },
  {"h3": "Saída esperada"},
  { code: `Ola, Ana!
Ana tem 30 anos e fara 31 no proximo aniversario
metade do saldo: 617.25
saldo formatado: R$ 1234.5
Bruno e admin
ativo=yes vazio=void
{isso e literal} e Ana e interpolado
Ola, Ana! Voce tem 30 anos.
Ola, Ana! Voce tem 30 anos.
Mouse       2x  R$ 160.0`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Use `pad_end` e `pad_start` dentro da interpolação para alinhar colunas.", "Escreva `$\"{}\"` e leia o erro do lexer."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/13-desestruturacao/133_desestruturar_listas.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '133-desestruturacao-de-listas', text: "133 · Desestruturacao de listas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'a-troca-sem-temporaria', text: "A troca sem temporária", level: 3 as const }, { id: 'quantidade-errada-falha', text: "Quantidade errada falha", level: 3 as const }, { id: 'retornando-varios-valores', text: "Retornando vários valores", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '134-resto-e-spread', text: "134 · Resto e spread", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-padrao-de-configuracao', text: "O padrão de configuração", level: 3 as const }, { id: 'copia-rasa', text: "Cópia rasa", level: 3 as const }, { id: 'comparando', text: "Comparando", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '135-desestruturar-records-e-vaults', text: "135 · Desestruturar records e vaults", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'chave-ausente-falha', text: "Chave ausente falha", level: 3 as const }, { id: 'resto-nomeado', text: "Resto nomeado", level: 3 as const }, { id: 'o-padrao-de-desempacotar-no-inicio', text: "O padrão de desempacotar no início", level: 3 as const }, { id: 'e-no-pattern-matching', text: "E no pattern matching", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '136-compreensao-de-listas', text: "136 · Compreensao de listas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'comparando-com-o-laco-equivalente', text: "Comparando com o laço equivalente", level: 3 as const }, { id: 'compreensao-ou-pipeline', text: "Compreensão ou pipeline?", level: 3 as const }, { id: 'multiplas-fontes', text: "Múltiplas fontes", level: 3 as const }, { id: 'escopo', text: "Escopo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '137-compreensao-de-vaults', text: "137 · Compreensao de vaults", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'percorrendo-um-vault', text: "Percorrendo um vault", level: 3 as const }, { id: 'tres-aplicacoes-que-valem-memorizar', text: "Três aplicações que valem memorizar", level: 3 as const }, { id: 'chaves-repetidas', text: "Chaves repetidas", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '138-interpolacao-de-strings', text: "138 · Interpolacao de strings", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-o-e-obrigatorio', text: "Por que o `$` é obrigatório", level: 3 as const }, { id: 'o-que-cabe-dentro-das-chaves', text: "O que cabe dentro das chaves", level: 3 as const }, { id: 'formatacao-segue-a-linguagem', text: "Formatação segue a linguagem", level: 3 as const }, { id: 'chaves-literais', text: "Chaves literais", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"13 · Desestruturação"}
      description={"6 exercícios: cluster, vault, rest e troca de variáveis."}
      href={"/docs/exercicios/13-desestruturacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
