# -*- coding: utf-8 -*-
"""Primeiros passos — dez páginas para quem nunca programou.

A página `/docs/primeiros-passos` instala e roda o primeiro arquivo.
Estas continuam dali, na ordem em que um curso ensinaria: mostrar,
guardar, perguntar, decidir, repetir, agrupar, nomear, juntar tudo num
programa, ler um erro, e saber para onde ir.

Uma regra que atravessa todas: cada bloco roda do jeito que está, e
termina com `assert` — é assim que quem está começando confere que
entendeu, e é assim que esta página é conferida a cada build.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/ola-mundo",
"title": "1. Olá, mundo — de verdade",
"description": "O que acontece quando você roda um arquivo: a linha, a ordem, e o que 'out' faz.",
"blocos": [
 {"p": "Um programa é uma lista de instruções que o computador executa **de cima para baixo**, uma de cada vez. O primeiro programa de toda linguagem mostra um texto na tela — e aqui isso se escreve com `out`."},
 {"code": """out "Ola, mundo!"
out "Esta e a segunda linha."
out 2 + 3
out "o dobro de", 21, "e", 21 * 2""", "lang": "df", "title": "ola.df"},
 {"code": """dataforge run ola.df""", "lang": "bash"},
 {"table": {"head": ["Você escreveu", "Sai na tela", "Porque"], "rows": [
   ["`out \"Ola, mundo!\"`", "`Ola, mundo!`", "o texto entre aspas sai como está"],
   ["`out 2 + 3`", "`5`", "sem aspas, é uma **conta**, e o resultado sai"],
   ["`out \"a\", 1`", "`a 1`", "a vírgula separa várias coisas, com um espaço entre elas"]]}},
 {"callout": {"tipo": "dica", "titulo": "Aspas mudam tudo", "texto": "`out \"2 + 3\"` mostra `2 + 3`; `out 2 + 3` mostra `5`. Entre aspas é **texto**, e o texto não é calculado. É a primeira distinção de toda linguagem, e a que mais confunde no começo."}},
 {"h2": "Comentários"},
 {"code": """// Tudo depois de // e comentario: o computador ignora.
// Serve para quem LE o codigo — inclusive voce, daqui a um mes.
out "so esta linha roda"   // e aqui tambem pode""", "lang": "df"},
 {"p": "Próximo: [2. Variáveis e contas](/docs/primeiros-passos/variaveis-e-contas)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/variaveis-e-contas",
"title": "2. Variáveis e contas",
"description": "Dar nome a um valor com :=, e as contas que a linguagem sabe fazer.",
"blocos": [
 {"p": "Uma **variável** é um nome para um valor. Você guarda o valor uma vez e usa o nome quantas vezes quiser. Em DataForge, guardar se escreve `:=` — lê-se *“recebe”*."},
 {"code": """preco := 12.50
quantidade := 3
total := preco * quantidade
out "total:", total

// O nome pode receber outro valor depois.
quantidade := 4
total := preco * quantidade
out "agora:", total
assert total is 50.0""", "lang": "df"},
 {"h2": "As contas"},
 {"table": {"head": ["Escreva", "Faz", "Exemplo", "Dá"], "rows": [
   ["`+` `-` `*`", "soma, subtração, multiplicação", "`7 * 3`", "`21`"],
   ["`/`", "divisão — sempre com vírgula", "`7 / 2`", "`3.5`"],
   ["`~/`", "divisão **inteira**", "`7 ~/ 2`", "`3`"],
   ["`%`", "o resto da divisão", "`7 % 2`", "`1`"],
   ["`**`", "potência", "`2 ** 10`", "`1024`"]]}},
 {"code": """assert 7 / 2 is 3.5
assert 7 ~/ 2 is 3
assert 7 % 2 is 1
assert 2 ** 10 is 1024
assert (2 + 3) * 4 is 20     // os parenteses mandam
assert 2 + 3 * 4 is 14       // sem eles, a multiplicacao vem antes
out "todas as contas conferem\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`//` não é divisão", "texto": "Em muitas linguagens `//` divide; aqui, `//` começa um **comentário**. A divisão inteira é `~/`. Se você escrever `x // 2` e o resultado parecer estranho, é isso."}},
 {"h2": "Constantes"},
 {"code": """steady PI := 3.14159
raio := 2
out "area:", PI * raio ** 2
// PI := 3 daria erro: 'steady' e um valor que nao muda.""", "lang": "df"},
 {"p": "Próximo: [3. Perguntar ao usuário](/docs/primeiros-passos/entrada)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/entrada",
"title": "3. Perguntar ao usuário",
"description": "input(): ler o que a pessoa digita, converter em número, e o fim da entrada.",
"blocos": [
 {"p": "Um programa fica interessante quando responde a quem o usa. `input(pergunta)` mostra a pergunta, espera a pessoa digitar e apertar Enter, e devolve **o texto** digitado."},
 {"code": """nome := input("Qual e o seu nome? ")
out $"Ola, {nome}!\"""", "lang": "df", "title": "saudacao.df"},
 {"code": """$ dataforge run saudacao.df
Qual e o seu nome? Ana
Ola, Ana!""", "lang": "text"},
 {"callout": {"tipo": "atencao", "titulo": "O que se digita é sempre TEXTO", "texto": "Mesmo que a pessoa digite `42`, `input` devolve o texto `\"42\"`. Para fazer conta, converta com `int(...)` ou `float(...)` — `\"42\" + 1` é um erro, e `int(\"42\") + 1` é `43`."}},
 {"code": """// '?? "0"': se a entrada acabar, input devolve void, e int(void) seria erro.
idade := int(input("Sua idade: ") ?? "0")
out $"daqui a 10 anos voce tera {idade + 10}\"""", "lang": "df", "title": "idade.df"},
 {"h2": "Quando a pessoa digita algo que não é número"},
 {"code": """action ler_inteiro(texto):
    monitor:
        yield int(texto)
    handle Error:
        yield void

assert ler_inteiro("42") is 42
assert ler_inteiro("quarenta") is void
out "o texto que nao e numero vira void, e o programa nao cai\"""", "lang": "df"},
 {"h2": "Ler até acabar"},
 {"p": "Quando a entrada termina — Ctrl+D no terminal, ou o fim de um arquivo redirecionado —, `input` devolve `void`. É isso que deixa um laço de leitura terminar sozinho:"},
 {"code": """total := 0
linha := input()
persist linha isnt void:
    total += int(linha)
    linha := input()
out $"soma: {total}\"""", "lang": "df", "title": "soma.df"},
 {"code": """$ printf '10\\n20\\n12\\n' | dataforge run soma.df
soma: 42""", "lang": "text"},
 {"p": "Próximo: [4. Decidir](/docs/primeiros-passos/decisoes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/decisoes",
"title": "4. Decidir",
"description": "given, orif e otherwise — e as comparações que decidem.",
"blocos": [
 {"p": "Decidir é fazer uma coisa **ou** outra dependendo de uma condição. Em DataForge: `given` (*se*), `orif` (*senão, se*) e `otherwise` (*senão*). O que está recuado embaixo de cada um só roda quando ele é escolhido."},
 {"code": """nota := 7.5

given nota bigger_eq 9:
    conceito := "A"
orif nota bigger_eq 7:
    conceito := "B"
orif nota bigger_eq 5:
    conceito := "C"
otherwise:
    conceito := "D"

out $"nota {nota}: conceito {conceito}"
assert conceito is "B\"""", "lang": "df"},
 {"h2": "As comparações"},
 {"table": {"head": ["Escreva", "Pergunta"], "rows": [
   ["`a is b`", "são iguais?"],
   ["`a isnt b`", "são diferentes?"],
   ["`a bigger b` / `a smaller b`", "maior? menor?"],
   ["`a bigger_eq b` / `a smaller_eq b`", "maior ou igual? menor ou igual?"],
   ["`x in lista`", "está dentro?"],
   ["`c1 and c2` / `c1 or c2` / `not c`", "as duas? alguma? o contrário?"]]}},
 {"callout": {"tipo": "dica", "titulo": "A ordem dos `orif` importa", "texto": "O primeiro que for verdadeiro ganha, e os outros nem são olhados. Por isso a nota 9,5 cai em `A` e não em `B` — mesmo sendo, também, maior ou igual a 7."}},
 {"h2": "Numa linha só"},
 {"code": """idade := 20
situacao := "maior" given idade bigger_eq 18 otherwise "menor"
assert situacao is "maior\"""", "lang": "df"},
 {"p": "Próximo: [5. Repetir](/docs/primeiros-passos/repeticao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/repeticao",
"title": "5. Repetir",
"description": "cycle para contar e percorrer, persist para repetir enquanto for verdade.",
"blocos": [
 {"p": "Repetir é a razão de existir do computador: ele faz a mesma coisa mil vezes sem cansar e sem errar. Há duas formas, e a escolha é a pergunta que você está fazendo."},
 {"table": {"head": ["Pergunta", "Use"], "rows": [
   ["*“faça isto para cada número de 1 a 10”*", "`cycle i from 1 to 10`"],
   ["*“faça isto para cada item da lista”*", "`cycle item in lista`"],
   ["*“faça isto enquanto for verdade”*", "`persist condicao`"]]}},
 {"code": """// A tabuada do 7 — 'from ... to' inclui as DUAS pontas.
cycle i from 1 to 10:
    out $"7 x {i} = {7 * i}"

// Somar uma lista, item por item.
total := 0
cycle preco in [10, 25, 7]:
    total += preco
assert total is 42

// Dobrar ate passar de 1000.
n := 1
passos := 0
persist n smaller 1000:
    n := n * 2
    passos += 1
out $"{passos} dobras: {n}"
assert n is 1024""", "lang": "df"},
 {"h2": "Parar antes, ou pular"},
 {"code": """// 'halt' sai do laco; 'skip' pula para a proxima volta.
primeiro_par := void
cycle n in [7, 3, 8, 5, 10]:
    given n % 2 isnt 0:
        skip
    primeiro_par := n
    halt
assert primeiro_par is 8""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O laço que nunca termina", "texto": "Um `persist` cuja condição nunca fica falsa roda para sempre — o programa parece travado. Confira que alguma coisa **dentro** do laço muda a condição. Ctrl+C interrompe."}},
 {"p": "Próximo: [6. Listas e vaults](/docs/primeiros-passos/colecoes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/colecoes",
"title": "6. Listas, vaults e conjuntos",
"description": "Guardar muitos valores: a lista em ordem, o vault por nome, o conjunto sem repetição.",
"blocos": [
 {"p": "Uma variável guarda um valor. Para guardar muitos, há três coleções, e cada uma responde uma pergunta diferente."},
 {"table": {"head": ["Coleção", "Escreve", "Responde"], "rows": [
   ["**Cluster** (lista)", "`[10, 20, 30]`", "*qual é o terceiro?* — pela posição, a partir de 0"],
   ["**Vault** (dicionário)", "`{\"nome\": \"Ana\"}`", "*qual é o nome?* — pela chave"],
   ["**Set** (conjunto)", "`{\"azul\", \"verde\"}`", "*isto está aqui?* — sem repetição e sem ordem"]]}},
 {"code": """notas := [7.5, 9, 6]
notas.append(10)
out notas[0], notas[-1], len(notas)     // o primeiro, o ultimo, quantos
assert notas[1] is 9

aluna := {"nome": "Ana", "idade": 20}
aluna["curso"] := "Matematica"
out aluna["nome"], "cursa", aluna["curso"]
assert "idade" in aluna

cores := {"azul", "verde", "azul"}       // a repeticao some
assert len(cores) is 2 and "verde" in cores
assert set([1, 1, 2]) is {1, 2}""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A lista começa no zero", "texto": "`notas[0]` é o **primeiro** item, e `notas[1]` o segundo. É a convenção de quase toda linguagem, e o erro mais comum de quem começa. `notas[-1]` é o último, sem precisar saber o tamanho."}},
 {"h2": "Percorrer"},
 {"code": """produtos := {"cafe": 18.5, "pao": 7.0, "leite": 5.2}
total := 0
cycle nome in produtos:
    out $"{nome}: R$ {produtos[nome]}"
    total += produtos[nome]
assert total is 30.7""", "lang": "df"},
 {"p": "Próximo: [7. Ações](/docs/primeiros-passos/acoes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/acoes",
"title": "7. Ações — dar nome a um pedaço de código",
"description": "action, parâmetros e yield: escrever uma vez, usar em qualquer lugar.",
"blocos": [
 {"p": "Quando o mesmo pedaço de código aparece duas vezes, ele merece um nome. Uma **ação** (a *função* de outras linguagens) recebe valores, faz algo com eles, e devolve um resultado com `yield`."},
 {"code": """action imc(peso, altura):
    yield peso / (altura ** 2)

action classificar(valor):
    given valor smaller 18.5:
        yield "abaixo do peso"
    given valor smaller 25:
        yield "normal"
    yield "acima do peso"

meu := imc(70, 1.75)
out $"IMC {round(meu, 1)}: {classificar(meu)}"
assert classificar(imc(70, 1.75)) is "normal\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`yield` devolve **e sai**", "texto": "Assim que um `yield` roda, a ação termina — o que vem depois não é executado. É o que permite escrever `classificar` sem `otherwise`: se a primeira condição valer, a ação já saiu."}},
 {"h2": "Valor padrão e tipos"},
 {"code": """action saudar(nome: String, cumprimento := "Ola") -> String:
    yield $"{cumprimento}, {nome}!"

assert saudar("Ana") is "Ola, Ana!"
assert saudar("Bia", "Bom dia") is "Bom dia, Bia!"
// saudar(42) e acusado pelo 'dataforge check' antes de rodar""", "lang": "df"},
 {"p": "Próximo: [8. O primeiro programa completo](/docs/primeiros-passos/primeiro-programa)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/primeiro-programa",
"title": "8. O primeiro programa completo",
"description": "Um jogo de adivinhar o número — com a lógica separada da conversa, e testada.",
"blocos": [
 {"p": "Tudo junto: o computador sorteia um número de 1 a 100, a pessoa chuta, e ele diz *“maior”* ou *“menor”* até ela acertar. O segredo de um programa que dá para testar é separar a **regra** (comparar o chute) da **conversa** (perguntar e mostrar)."},
 {"code": """// ── a regra: nao pergunta nada, so decide ──
action avaliar(segredo, chute):
    given chute is segredo:
        yield "acertou"
    given chute smaller segredo:
        yield "maior"
    yield "menor"

action ler_chute(texto):
    monitor:
        n := int(texto)
    handle Error:
        yield void
    given n smaller 1 or n bigger 100:
        yield void
    yield n

// ── o teste da regra, sem ninguem digitando ──
assert avaliar(42, 42) is "acertou"
assert avaliar(42, 10) is "maior"
assert avaliar(42, 90) is "menor"
assert ler_chute("abc") is void
assert ler_chute("500") is void
assert ler_chute("37") is 37
out "a regra do jogo confere\"""", "lang": "df", "title": "regras.df"},
 {"code": """// ── a conversa: usa a regra ──
segredo := randint(1, 100)
tentativas := 0
resposta := ""
persist resposta isnt "acertou":
    texto := input("Seu chute (1 a 100): ")
    given texto is void:
        out ""
        out "ate a proxima!"
        halt
    chute := ler_chute(texto)
    given chute is void:
        out "digite um numero de 1 a 100"
        skip
    tentativas += 1
    resposta := avaliar(segredo, chute)
    given resposta is "acertou":
        out $"Acertou em {tentativas} tentativa(s)!"
    otherwise:
        out $"O numero e {resposta}.\"""", "lang": "text", "title": "jogo.df (junto de regras.df)"},
 {"callout": {"tipo": "dica", "titulo": "Por que separar", "texto": "A regra se testa em milissegundos, sem ninguém digitar nada, e os três `assert` provam que ela está certa. A conversa é fina o bastante para errar pouco. É a mesma separação que um sistema grande faz entre regra de negócio e tela — ver [os tipos de projeto](/docs/projetos)."}},
 {"p": "Próximo: [9. Ler um erro](/docs/primeiros-passos/erros-comuns)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/erros-comuns",
"title": "9. Ler uma mensagem de erro",
"description": "Onde olhar numa mensagem de erro, e os seis erros que quem começa mais encontra.",
"blocos": [
 {"p": "Errar é o normal; o que muda com a prática é quanto tempo se leva para achar o erro. Uma mensagem de erro do DataForge tem sempre quatro partes, e lê-las em ordem resolve a maioria dos casos."},
 {"code": """erro[DF0401]: 'totl' nao esta definido.
  ┌─ conta.df:3:5
  │
3 │ out totl * 2
  │     ^^^^ usado aqui
  = nota: este nome nunca recebeu valor em nenhum escopo ao redor
  = dica: voce quis dizer 'total'?""", "lang": "text"},
 {"table": {"head": ["Parte", "O que diz"], "rows": [
   ["`erro[DF0401]`", "o **código** — `dataforge explain DF0401` explica em detalhe"],
   ["`conta.df:3:5`", "o **arquivo**, a **linha** e a **coluna**"],
   ["a linha com `^^^^`", "o **ponto exato**"],
   ["`nota` / `dica`", "o **porquê** e o **que fazer**"]]}},
 {"h2": "Os seis mais comuns"},
 {"table": {"head": ["A mensagem fala de", "O que costuma ser"], "rows": [
   ["nome não definido", "um erro de digitação — a dica sugere o nome parecido"],
   ["indentação / `SyncError`", "um **tab** no lugar de espaços: use 4 espaços"],
   ["`Expected ':'`", "faltou o `:` no fim do `given`, do `cycle` ou da `action`"],
   ["não se soma texto com número", "o que veio do `input` ainda é texto — `int(...)`"],
   ["índice fora do alcance", "a lista começa no zero; o último é `[-1]`"],
   ["`'no'` é palavra reservada", "`no`, `in`, `is`, `to`, `from` não podem ser nomes"]]}},
 {"code": """// Conferir ANTES de rodar acha a maioria deles:
//   dataforge check conta.df
monitor:
    x := "10" + 1
handle Error as e:
    out "o erro:", e.message
assert int("10") + 1 is 11""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "`dataforge check` antes de `run`", "texto": "Ele lê o arquivo sem executar e acusa nome errado, número errado de argumentos e tipo errado — em menos de um segundo, e com a mesma cara de mensagem. É o hábito que mais poupa tempo no começo."}},
 {"p": "Próximo: [10. Para onde ir](/docs/primeiros-passos/proximos-passos)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/primeiros-passos/proximos-passos",
"title": "10. Para onde ir agora",
"description": "Os caminhos depois do básico — conforme o que você quer construir.",
"blocos": [
 {"p": "Com o que está nestas dez páginas já dá para escrever programas úteis: ler dados, decidir, repetir, organizar em ações. O próximo passo depende do que você quer construir."},
 {"table": {"head": ["Quero…", "Comece em"], "rows": [
   ["entender a linguagem a fundo", "[Fundamentos](/docs/fundamentos) e [a referência](/docs/referencia/gramatica)"],
   ["analisar uma planilha ou um CSV", "[Dados](/docs/dados)"],
   ["fazer um site ou uma API", "[Kiln](/docs/kiln)"],
   ["um painel de gráficos", "[Vitrine](/docs/vitrine)"],
   ["um bot", "[Telegram](/docs/telegram)"],
   ["programar melhor, com testes", "[TDD](/docs/testes/tdd)"],
   ["entender por que um programa é lento", "[Big-O](/docs/big-o)"],
   ["ver um projeto de cada tipo", "[Os 22 tipos de projeto](/docs/projetos)"]]}},
 {"h2": "Praticar"},
 {"code": """dataforge new cli minha-ferramenta   # um projeto que ja passa nos testes
dataforge palavras                   # cada palavra da linguagem, com exemplo que roda
python3 exercicios/run_all.py 01     # os exercicios do modulo 1""", "lang": "bash"},
 {"code": """// Um ultimo exercicio: some so os pares de 1 a 100.
soma := 0
cycle n from 1 to 100:
    given n % 2 is 0:
        soma += n
assert soma is 2550
out "voce terminou os primeiros passos\"""", "lang": "df"},
]},
]
