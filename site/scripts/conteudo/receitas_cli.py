# -*- coding: utf-8 -*-
"""Receitas de linha de comando — nove páginas.

A `/docs/receitas/cli` era uma página só, com um exemplo. Uma ferramenta
de terminal de verdade tem oito problemas além de ler `--flag`: o que
fazer quando a entrada vem canalizada, como não colorir quando a saída
não é um terminal, o código de saída, o `Ctrl-C`, a configuração em
camadas, a ajuda que não mente, o empacotamento e o teste.

Todo bloco roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/argumentos",
"title": "Argumentos, opções e a ajuda",
"description": "Declarar o que o comando aceita — e ganhar a ajuda, a validação e o erro de graça.",
"blocos": [
 {"p": "Ler `OS.argv()` à mão funciona para um script de dez linhas e apodrece no primeiro dia em que alguém escreve `--formato json` em vez de `--formato=json`. `Arcane.Cli` inverte isso: você **declara** o que o comando aceita, e a ajuda, a validação e a mensagem de erro saem da declaração."},
 {"code": '''adopt Arcane.Cli as Cli

cmd := Cli.comando("relatorio", "Gera um relatório de vendas", "1.0.0")
cmd.posicional("entrada", "o CSV de vendas")
cmd.opcao("formato", "texto", "f", "tabela", "tabela, json ou csv", no,
          ["tabela", "json", "csv"])
cmd.opcao("limite", "inteiro", "n", 10, "quantas linhas")
cmd.opcao("cores", "sim_nao", "", no, "colorir a saída")

args := cmd.ler(["vendas.csv", "--formato=json", "-n", "5", "--cores"])
assert args["entrada"] is "vendas.csv"
assert args["formato"] is "json"
assert args["limite"] is 5          // já vem Integer, não texto
assert args["cores"] is yes''', "lang": "df"},
 {"h2": "A ajuda é gerada, e por isso não mente"},
 {"p": "Uma ajuda escrita à mão envelhece na primeira opção nova — e ninguém relê a ajuda do próprio programa. Aqui ela sai da mesma declaração que faz a leitura:"},
 {"code": '''adopt Arcane.Cli as Cli

cmd := Cli.comando("relatorio", "Gera um relatório de vendas", "1.0.0")
cmd.posicional("entrada", "o CSV de vendas")
cmd.opcao("formato", "texto", "f", "tabela", "tabela, json ou csv", no,
          ["tabela", "json", "csv"])
cmd.exemplo("relatorio vendas.csv --formato=json", "em JSON")

texto := cmd.ajuda()
assert "uso: relatorio" in texto
assert "--formato" in texto
assert "tabela|json|csv" in texto       // as escolhas aparecem
assert "exemplos:" in texto
out texto''', "lang": "df"},
 {"h2": "O que a declaração compra"},
 {"table": {
   "head": ["Você declara", "Ganha"],
   "rows": [
     ["`tipo := \"inteiro\"`", "conversão, e erro claro em `--limite=abc`"],
     ["`escolhas := [...]`", "recusa o que não está na lista, e mostra a lista"],
     ["`exigida := yes`", "recusa a falta, dizendo qual falta"],
     ["`curta := \"n\"`", "`-n 5`, `-n=5` e `--limite 5` passam a ser a mesma coisa"],
     ["`tipo := \"sim_nao\"`", "`--cores` sem valor vira `yes`"],
     ["`cmd.exemplo(…)`", "a seção de exemplos da ajuda"]]}},
 {"h2": "O erro sai antes do trabalho"},
 {"code": '''adopt Arcane.Cli as Cli

cmd := Cli.comando("relatorio", "")
cmd.opcao("formato", "texto", "f", "tabela", "", no, ["tabela", "json"])

monitor:
    cmd.ler(["--formato=xml"])
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"p": "Validar **antes** de abrir o arquivo é o que separa um erro de uma linha de um traceback no meio do processamento — e o que permite ao programa falhar sem ter escrito nada."},
 {"h2": "Vários valores para o mesmo posicional"},
 {"code": '''adopt Arcane.Cli as Cli

cmd := Cli.comando("somar", "soma números")
cmd.posicional("numeros", "os números", yes)      // varios := yes

args := cmd.ler(["1", "2", "3"])
assert len(args["numeros"]) is 3
assert [int(n) cycle n in args["numeros"]] >> distill a, v: a + v 0 is 6''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "`rodar` sai; `ler` levanta", "texto": "`cmd.rodar()` imprime a ajuda ou o erro e **encerra o processo** — é o que se quer no `main`. `cmd.ler(…)` levanta, e é o que se quer num teste: um teste que chama `rodar` mata o próprio corredor."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/subcomandos",
"title": "Subcomandos",
"description": "git-style: um programa, vários verbos — e a ajuda de cada um.",
"blocos": [
 {"p": "`git commit`, `docker run`, `dataforge check`. Quando a ferramenta cresce, o verbo vira o primeiro argumento, e cada verbo tem as suas opções."},
 {"code": '''adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "Gerenciador de tarefas", "2.0.0")

criar := app.subcomando("criar", "cria uma tarefa")
criar.posicional("titulo", "o título")
criar.opcao("prazo", "texto", "p", "", "quando vence")

listar := app.subcomando("listar", "lista as tarefas")
listar.opcao("todas", "sim_nao", "a", no, "inclusive as concluídas")

args := app.ler(["criar", "comprar café", "--prazo=amanhã"])
assert args["__comando__"] is "criar"
assert args["titulo"] is "comprar café"
assert args["prazo"] is "amanhã"

args := app.ler(["listar", "-a"])
assert args["__comando__"] is "listar"
assert args["todas"] is yes''', "lang": "df"},
 {"h2": "Despachar"},
 {"p": "Um vault de ações é melhor que uma escada de `given`: acrescentar um verbo passa a ser acrescentar uma entrada, e a lista de verbos vira dado — dá para listá-la, testá-la e conferi-la."},
 {"code": '''adopt Arcane.Cli as Cli

action criar(args):
    yield $"criada: {args['titulo']}"

action listar(args):
    yield "3 tarefas"

VERBOS := {"criar": criar, "listar": listar}

app := Cli.comando("tarefa", "")
c := app.subcomando("criar", "")
c.posicional("titulo", "")
app.subcomando("listar", "")

args := app.ler(["criar", "café"])
acao := VERBOS[args["__comando__"]]
assert acao(args) is "criada: café"

// e a lista de verbos é DADO: dá para conferir que nenhum ficou sem ação
assert sorted(keys(VERBOS)) is ["criar", "listar"]''', "lang": "df"},
 {"h2": "A ajuda do programa lista os verbos"},
 {"code": '''adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "Gerenciador de tarefas")
app.subcomando("criar", "cria uma tarefa")
app.subcomando("listar", "lista as tarefas")

texto := app.ajuda()
assert "criar" in texto and "cria uma tarefa" in texto
out texto''', "lang": "df"},
 {"h2": "Um verbo que não existe"},
 {"code": '''adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "")
app.subcomando("criar", "")
app.subcomando("listar", "")

monitor:
    app.ler(["crear", "x"])       // erro de digitação
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"p": "Uma sugestão (\"você quis dizer `criar`?\") é o que transforma um erro de digitação em um segundo de perda, em vez de uma ida à documentação."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/saida",
"title": "Cor, tabela e o terminal que não é terminal",
"description": "Colorir sem estragar o `| grep`, e desenhar tabela, árvore e barra sem dependência.",
"blocos": [
 {"p": "A regra que quase todo programa de terminal erra: **cor só quando a saída é um terminal**. Canalizado para um arquivo ou para o `grep`, o código de escape vira lixo no meio do dado — e um `grep \"erro\"` deixa de casar porque há um `\\x1b[31m` grudado na palavra."},
 {"code": '''adopt Arcane.Color as Cor
adopt Arcane.OS as OS

// 'auto' decide pelo terminal; 'supports' responde o que ele aceita
assert Cor.supports() is yes or Cor.supports() is no

// E 'strip' tira a cor de um texto já colorido — é o que um teste faz.
pintado := Cor.red("falhou")
assert Cor.strip(pintado) is "falhou"
out Cor.strip(Cor.bold(Cor.green("ok")))''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`NO_COLOR` é um padrão, não uma preferência", "texto": "A variável `NO_COLOR` desliga a cor de qualquer ferramenta que a respeite, e existe justamente para quem canaliza, registra em log ou usa leitor de tela. O `dataforge` a respeita em toda a CLI — e isso foi um defeito real aqui: só o depurador a lia."}},
 {"h2": "Tabela"},
 {"code": '''adopt Arcane.Color as Cor

linhas := [
    ["produto", "qtd", "preço"],
    ["café", "12", "R$ 32,90"],
    ["filtro", "3", "R$ 8,50"],
]
desenho := Cor.table(linhas)
assert "produto" in desenho
out desenho''', "lang": "df"},
 {"h2": "Árvore, régua e barra"},
 {"code": '''adopt Arcane.Color as Cor

out Cor.rule("Relatório")
out Cor.tree({"projeto": {"src": ["main.df", "util.df"], "tests": ["main_test.df"]}})
out Cor.bar(0.72, 30)
out Cor.box("Concluído em 1,2 s")''', "lang": "df"},
 {"h2": "Progresso que não polui um log"},
 {"p": "Uma barra que se reescreve com `\\r` é ótima num terminal e é uma linha por quadro num arquivo de log. A saída é perguntar antes:"},
 {"code": '''adopt Arcane.Color as Cor
adopt Arcane.OS as OS

action progresso(feito, total):
    given not OS.is_tty():
        // canalizado: uma linha por marco, e só
        given feito % 50 is 0:
            out $"  {feito}/{total}"
        yield void
    out $"\\r  {Cor.bar(feito / total, 24)} {feito}/{total}"
    yield void

cycle i from 1 to 100:
    given i % 50 is 0:
        progresso(i, 100)
out ""''', "lang": "df"},
 {"h2": "A largura do terminal"},
 {"code": '''adopt Arcane.Cli as Cli
adopt Arcane.Color as Cor

largura := Cli.largura()
assert largura > 0
// Sem terminal, ela devolve um padrão — e é por isso que ela nunca é
// zero: uma divisão por largura no meio do desenho estouraria.
out $"largura: {largura} colunas"''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/entrada",
"title": "Entrada: teclado, cano e arquivo",
"description": "Perguntar quando há alguém do outro lado — e ler do `stdin` quando não há.",
"blocos": [
 {"p": "Uma ferramenta de terminal recebe dado de três lugares, e confundi-los é o que faz um programa travar dentro de um script: **o teclado**, **o cano** (`cat x | prog`) e **o arquivo** passado como argumento."},
 {"code": '''adopt Arcane.OS as OS
adopt Arcane.Cli as Cli

// A pergunta só faz sentido com alguém do outro lado.
given Cli.tem_terminal():
    out "aqui eu poderia perguntar"
otherwise:
    out "sem terminal: leio do cano, e não pergunto"''', "lang": "df"},
 {"h2": "Ler o que vier pelo cano"},
 {"p": "`input()` devolve `void` no fim da entrada, e **não levanta**: um programa canalizado termina a entrada, e isso não é erro. É o que torna o laço abaixo o idioma da linguagem:"},
 {"code": '''linhas := []
persist yes:
    linha := input()
    given linha is void:
        halt
    linhas.append(linha)

out $"{len(linhas)} linha(s) pelo cano"''', "lang": "df"},
 {"h2": "O padrão que cobre os três casos"},
 {"code": '''adopt Arcane.IO as IO
adopt Arcane.Cli as Cli

action ler_tudo(caminho):
    // Um '-' como caminho quer dizer "a entrada padrão", e é
    // convenção de quase toda ferramenta Unix.
    given caminho is void or caminho is "-":
        pedacos := []
        persist yes:
            linha := input()
            given linha is void:
                halt
            pedacos.append(linha)
        yield join("\\n", pedacos)
    yield IO.read(caminho)

// com o arquivo:
adopt Arcane.OS as OS
pasta := $"{OS.temp_dir()}/df-cli-{randint(100000, 999999)}"
IO.mkdir(pasta)
IO.write($"{pasta}/a.txt", "uma linha")
assert ler_tudo($"{pasta}/a.txt") is "uma linha"
IO.remove_tree(pasta)''', "lang": "df"},
 {"h2": "Perguntar, escolher, confirmar"},
 {"code": '''adopt Arcane.Cli as Cli

// Num terminal, estes três param e esperam. Num script, eles
// precisam de um padrão — senão a automação trava sem dizer por quê.
action nome_do_projeto(args):
    given args["nome"] is not void:
        yield args["nome"]
    given not Cli.tem_terminal():
        trigger "sem terminal: passe --nome"
    yield Cli.perguntar("nome do projeto", "meu-app")

assert nome_do_projeto({"nome": "loja"}) is "loja"

monitor:
    nome_do_projeto({"nome": void})
handle Error as e:
    out e.message''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Nunca peça segredo quando não há terminal", "texto": "`Cli.segredo(\"senha\")` esconde o que se digita. Sem terminal, ele não tem como esconder — e uma senha lida de um cano acaba no log de quem chamou. Prefira uma variável de ambiente, e diga isso na mensagem."}},
 {"h2": "Validar na entrada"},
 {"code": '''adopt Arcane.Cli as Cli

// 'valida' é uma ação que devolve yes/no; a pergunta se repete.
action e_email(texto):
    yield "@" in texto and "." in texto

assert e_email("a@b.co") is yes
assert e_email("nada") is no''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/configuracao",
"title": "Configuração em camadas",
"description": "Padrão, arquivo, ambiente e flag — nessa ordem, e com quem venceu dito na tela.",
"blocos": [
 {"p": "Toda ferramenta séria lê configuração de quatro lugares, e a **ordem** é o contrato: o padrão do programa, o arquivo do projeto, a variável de ambiente e a flag da linha de comando. A da direita vence."},
 {"table": {
   "head": ["Camada", "Para quê", "Exemplo"],
   "rows": [
     ["padrão", "funcionar sem configurar nada", "`{\"formato\": \"tabela\"}`"],
     ["arquivo", "a decisão do projeto, versionada", "`forge.toml`, `.minharc`"],
     ["ambiente", "a decisão da máquina ou do CI", "`MINHA_FORMATO=json`"],
     ["flag", "a decisão desta execução", "`--formato=json`"]]}},
 {"code": '''adopt Arcane.OS as OS

PADRAO := {"formato": "tabela", "limite": 10, "cor": yes}

action em_camadas(arquivo, prefixo, flags):
    valor := {...PADRAO}
    cycle chave in keys(arquivo):
        valor[chave] := arquivo[chave]
    cycle chave in keys(valor):
        do_ambiente := OS.get_env($"{prefixo}_{upper(chave)}")
        given do_ambiente is not void:
            valor[chave] := do_ambiente
    cycle chave in keys(flags):
        given flags[chave] is not void:
            valor[chave] := flags[chave]
    yield valor

final := em_camadas({"limite": 50}, "MINHA", {"formato": "json"})
assert final["formato"] is "json"      // a flag venceu
assert final["limite"] is 50           // o arquivo venceu o padrão
assert final["cor"] is yes             // ninguém mexeu: o padrão''', "lang": "df"},
 {"h2": "Dizer de onde veio cada valor"},
 {"p": "A pergunta que aparece em todo suporte é \"por que ele está usando isso?\". Guardar a camada ao lado do valor transforma meia hora de investigação numa linha:"},
 {"code": '''PADRAO := {"formato": "tabela", "limite": 10}

action com_origem(arquivo, ambiente, flags):
    saida := {}
    cycle chave in keys(PADRAO):
        saida[chave] := {"valor": PADRAO[chave], "de": "padrão"}
    cycle chave in keys(arquivo):
        saida[chave] := {"valor": arquivo[chave], "de": "arquivo"}
    cycle chave in keys(ambiente):
        saida[chave] := {"valor": ambiente[chave], "de": "ambiente"}
    cycle chave in keys(flags):
        saida[chave] := {"valor": flags[chave], "de": "flag"}
    yield saida

visto := com_origem({"limite": 50}, {}, {"formato": "json"})
cycle chave in sorted(keys(visto)):
    out $"  {chave} = {visto[chave]['valor']}   ({visto[chave]['de']})"
assert visto["limite"]["de"] is "arquivo"''', "lang": "df"},
 {"h2": "O cofre, quando há muitas camadas"},
 {"p": "`packages/cofre` é um pacote deste repositório que faz exatamente isto, e serve de referência — ele está publicado no registro e tem testes."},
 {"code": '''$ dataforge add cofre
$ dataforge search config''', "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "Segredo não é configuração", "texto": "Senha, token e chave não entram no arquivo versionado — eles vêm do ambiente ou de um cofre. `Arcane.Seguranca.varrer_segredo` acha o que escapou, e `dataforge seguranca` roda isso sobre o projeto inteiro, não só sobre os `.df`: um segredo vaza do arquivo de configuração muito mais do que do código."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/saida-e-sinais",
"title": "Código de saída, erro e Ctrl-C",
"description": "O que o shell lê, o que vai para o stderr, e como terminar sem deixar sujeira.",
"blocos": [
 {"p": "Um programa de terminal conversa com o shell por três canais, e dois deles são invisíveis para quem só olha a tela: o **código de saída**, o **stderr** e os **sinais**."},
 {"h2": "O código de saída é a resposta que o script lê"},
 {"table": {
   "head": ["Código", "Convenção"],
   "rows": [
     ["`0`", "deu certo — e **só** isso"],
     ["`1`", "falhou por um motivo do programa"],
     ["`2`", "uso errado: argumento faltando, flag desconhecida"],
     ["`130`", "interrompido com `Ctrl-C` (128 + SIGINT)"]]}},
 {"code": '''adopt Arcane.OS as OS

action principal(args):
    given args["entrada"] is void:
        // Uso errado sai com 2, e a mensagem vai para o STDERR:
        // quem canaliza a saída quer o dado, não o erro.
        yield 2
    yield 0

assert principal({"entrada": void}) is 2
assert principal({"entrada": "a.csv"}) is 0''', "lang": "df"},
 {"p": "O erro vai para o `stderr` porque `prog > saida.txt` guarda só o resultado: misturar os dois faz a mensagem de erro entrar no arquivo de dados, e ninguém nota até o dia em que o arquivo é lido por outro programa."},
 {"code": '''adopt Arcane.OS as OS

// O dado vai para a saída normal…
out "linha de dado"

// …e a queixa, para o stderr. Aqui, à mão, para o bloco não encerrar:
// 'Cli.erro(texto)' faz as duas coisas — escreve no stderr E SAI com 1.
// É o 'die' de um script, e por isso não há linha depois dele.
assert OS.is_tty() is yes or OS.is_tty() is no''', "lang": "df"},
 {"code": '''adopt Arcane.Cli as Cli

// Última linha do programa, de propósito: ela encerra com código 1.
Cli.erro("não achei o arquivo 'vendas.csv'")''', "lang": "df", "title": "encerra com 1"},
 {"h2": "Terminar sem deixar sujeira"},
 {"p": "`defer` roda na saída da ação **onde quer que esteja escrito** — inclusive no topo do programa, no fim dele. É o que garante que o arquivo temporário some, a conexão fecha e o relé desliga:"},
 {"code": '''adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-cli-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

IO.write($"{pasta}/trabalho.txt", "processando")
assert IO.exists($"{pasta}/trabalho.txt")
out "o defer apaga a pasta ao sair — inclusive se o programa falhar"''', "lang": "df"},
 {"h2": "O `Ctrl-C`"},
 {"code": '''adopt Arcane.Inicio as Inicio

// 'ao_encerrar' roda no caminho normal E no Ctrl-C: é onde mora
// "salve o que deu tempo" e "solte o que estiver segurando".
salvos := []
Inicio.ao_encerrar(lambda => salvos.append("estado gravado"))
out "encerramento registrado"''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um laço sem saída controlando um recurso", "texto": "`persist yes:` sem condição de parada, com um arquivo aberto ou um relé ligado, é o pior desenho desta área: o `Ctrl-C` interrompe no meio, e o recurso fica como estava. A saída é um `defer` (que roda) ou uma condição lida de fora."}},
 {"h2": "Erro que a pessoa consegue resolver"},
 {"code": '''adopt Arcane.IO as IO

action abrir(caminho):
    given not IO.exists(caminho):
        // O que, onde, e o que fazer. As três partes.
        trigger $"não achei '{caminho}'. Confira o caminho, ou passe '-' para ler da entrada padrão."
    yield IO.read(caminho)

monitor:
    abrir("nao-existe.csv")
handle Error as e:
    out e.message''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/testar",
"title": "Testar uma ferramenta de terminal",
"description": "Sem subprocesso onde não precisa, e com subprocesso onde só ele prova.",
"blocos": [
 {"p": "Uma CLI tem duas metades, e elas se testam de formas diferentes: a **leitura dos argumentos** é função pura, e a **execução** é um processo com código de saída, `stdout` e `stderr`."},
 {"h2": "A metade pura: `ler`, nunca `rodar`"},
 {"code": '''adopt Arcane.Cli as Cli
adopt Arcane.Crucible as Crucible

action montar():
    cmd := Cli.comando("relatorio", "")
    cmd.posicional("entrada", "")
    cmd.opcao("limite", "inteiro", "n", 10, "")
    yield cmd

crucible "os argumentos":

    trial "o padrao vale quando a flag nao vem":
        args := montar().ler(["a.csv"])
        expect args["limite"] is 10

    trial "a forma curta e a longa sao a mesma coisa":
        expect montar().ler(["a.csv", "-n", "5"])["limite"] is 5
        expect montar().ler(["a.csv", "--limite=5"])["limite"] is 5

    trial "o inteiro chega como INTEIRO":
        expect montar().ler(["a.csv", "-n", "7"])["limite"] is 7

Crucible.run()''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`rodar` mata o corredor de testes", "texto": "Ele imprime e chama `OS.exit`. Um teste que o chama derruba o próprio processo do teste — e o relatório some junto. `ler` levanta, que é o que um teste quer."}},
 {"h2": "A metade impura: o processo de verdade"},
 {"p": "O que só o subprocesso prova é o que acontece **na fronteira**: o código de saída, o que foi para cada canal, e o que o shell vê."},
 {"code": '''adopt Arcane.Process as P

// O próprio interpretador serve de cobaia: ele é uma CLI.
r := P.run(["python3", "-m", "dataforge", "--versao"])
assert r["exit_code"] is 0 and r["ok"] is yes
assert len(r["stdout"]) > 0
out r["stdout"]

// 'capture' e o atalho para quando so o stdout importa
assert len(P.capture(["python3", "-m", "dataforge", "--versao"])) > 0''', "lang": "df"},
 {"code": '''adopt Arcane.Process as P

// Um comando que não existe: o código de saída é o que prova.
r := P.run(["python3", "-m", "dataforge", "nao-existe-esse-comando"])
assert r["failed"] is yes
out $"saiu com {r['exit_code']}"''', "lang": "df"},
 {"h2": "A entrada canalizada"},
 {"code": '''adopt Arcane.Process as P
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-cli-t-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

IO.write($"{pasta}/soma.df", """persist yes:
    linha := input()
    given linha is void:
        halt
    out int(linha) * 2
""")

r := P.run(["python3", "-m", "dataforge", "run", $"{pasta}/soma.df"],
           no, void, void, void, "5\\n7\\n")
assert r["exit_code"] is 0
assert "10" in r["stdout"] and "14" in r["stdout"]
out r["stdout"]''', "lang": "df"},
 {"h2": "O que testar, em ordem de retorno"},
 {"list": [
   "**O código de saída** em cada caminho — é o que um `&&` no shell lê, e o que um CI usa para reprovar.",
   "**A ajuda cita cada opção** — um teste de três linhas que impede a ajuda de envelhecer.",
   "**A mensagem de erro de uso** — ela é lida por quem está travado, e é a única documentação que essa pessoa vai ler.",
   "**A saída canalizada não tem cor** — o `| grep` de alguém depende disso.",
   "**O temporário some** — rode duas vezes e confira que nada ficou para trás."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/distribuir",
"title": "Distribuir a ferramenta",
"description": "Do `.df` no seu computador ao comando que outra pessoa instala.",
"blocos": [
 {"p": "Uma ferramenta que só roda na sua máquina é um script. Três formas de entregá-la, em ordem de esforço:"},
 {"table": {
   "head": ["Forma", "Quem instala precisa de", "Quando"],
   "rows": [
     ["um `.df` e o `forge.toml`", "DataForge instalado", "equipe que já usa a linguagem"],
     ["um pacote no registro", "`dataforge add sua-lib`", "biblioteca, ou ferramenta reusável"],
     ["contêiner", "Docker", "CI, e máquina que não vai instalar nada"]]}},
 {"h2": "O projeto"},
 {"code": '''$ dataforge new cli minha-ferramenta
$ cd minha-ferramenta
$ dataforge test
$ dataforge run src/main.df -- --ajuda''', "lang": "bash"},
 {"p": "O `--` separa o que é do `dataforge` do que é **seu**: sem ele, `--ajuda` seria lido pela CLI da linguagem, e a sua nunca veria a flag."},
 {"h2": "Empacotar e publicar"},
 {"code": '''$ dataforge pack
$ dataforge publish --registry=../registro''', "lang": "bash"},
 {"p": "O tarball é **reprodutível** (`mtime=0`, uid e gid zerados): sem isso o sha256 mudaria a cada empacotamento, e a verificação de integridade do `forge.lock` não significaria nada."},
 {"h2": "Um contêiner que não precisa do DataForge instalado"},
 {"code": '''$ dataforge devops dockerfile
$ docker build -t minha-ferramenta .
$ docker run --rm minha-ferramenta --ajuda''', "lang": "bash"},
 {"p": "O `Dockerfile` gerado copia o manifesto **antes** do código (um commit numa linha deixa de reinstalar tudo), roda como `USER forge` — um escape de container vira um usuário sem privilégio, e não root no host — e põe o `.env` no `.dockerignore`, porque o segredo ficaria na camada e `docker history` o mostraria."},
 {"h2": "O que conferir antes de publicar"},
 {"code": '''adopt Arcane.Abi as Abi

// 'Abi' responde qual bump de semver a mudança exige, comparando a
// SUPERFÍCIE de duas versões — e não o texto do código.
assert "maior" in Abi.regras() or len(Abi.regras()) > 0
out "as regras de compatibilidade estão em Arcane.Abi"''', "lang": "df"},
 {"list": [
   "`dataforge test` e `dataforge check` verdes.",
   "`dataforge abi` entre a versão publicada e esta — **renomear um parâmetro é quebra**, porque a chamada com nome existe nesta linguagem.",
   "A ajuda cita cada opção, e os exemplos rodam.",
   "O `forge.lock` versionado: quem clonar em outro dia recebe a mesma árvore."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/completar",
"title": "Completar com Tab",
"description": "bash, zsh e fish — gerados do catálogo, e não escritos à mão.",
"blocos": [
 {"p": "Completar com Tab é a diferença entre uma ferramenta que se usa de cabeça e uma que exige `--ajuda` a cada vez. O script de completação é gerado **do catálogo de comandos** — escrito à mão, ele envelheceria na primeira flag nova."},
 {"code": '''$ dataforge completar bash > ~/.dataforge-completar.bash
$ echo 'source ~/.dataforge-completar.bash' >> ~/.bashrc

$ dataforge completar zsh  > ~/.zsh/completions/_dataforge
$ dataforge completar fish > ~/.config/fish/completions/dataforge.fish''', "lang": "bash"},
 {"h2": "Para a sua ferramenta"},
 {"p": "O mesmo princípio: a declaração do comando já sabe quais são as opções e os subcomandos, então o script sai dela."},
 {"code": '''adopt Arcane.Cli as Cli

app := Cli.comando("tarefa", "")
app.subcomando("criar", "cria")
app.subcomando("listar", "lista")

action script_bash(nome, verbos):
    palavras := join(" ", verbos)
    corpo := $"  COMPREPLY=($(compgen -W \\"{palavras}\\" -- \\"$" + "{COMP_WORDS[1]}\\"))"
    linhas := [$"_{nome}() {{", corpo, "}", $"complete -F _{nome} {nome}"]
    yield join("\\n", linhas)

texto := script_bash("tarefa", ["criar", "listar"])
assert "complete -F _tarefa tarefa" in texto
out texto''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Testado com Tab de verdade", "texto": "O completar do `dataforge` é conferido com um Tab **simulado no bash**, e não lendo o script: um script de completação com erro de sintaxe é aceito pelo shell em silêncio, e o Tab simplesmente não faz nada — que é indistinguível de não ter instalado."}},
 {"h2": "O que completar, em ordem de utilidade"},
 {"list": [
   "**Os subcomandos** — é o primeiro Tab de toda sessão.",
   "**As flags do subcomando atual**, e não as do programa inteiro.",
   "**As escolhas de uma opção** (`--formato=` → `tabela json csv`).",
   "**Caminhos**, quando o posicional é um arquivo — o shell já faz isso, desde que o script não o atrapalhe."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/receitas/cli/completa",
"title": "Uma ferramenta inteira",
"description": "Do argumento ao código de saída: um contador de linhas de código, em 60 linhas.",
"blocos": [
 {"p": "Juntando tudo: uma ferramenta que varre uma pasta, conta linhas por extensão e responde em tabela ou JSON — com ajuda, validação, cor condicional e código de saída."},
 {"code": '''adopt Arcane.Cli as Cli
adopt Arcane.Color as Cor
adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Serialization as Ser

// ── o que o comando aceita ─────────────────────────────────
action montar():
    cmd := Cli.comando("contar", "Conta linhas por extensão", "1.0.0")
    cmd.posicional("pasta", "a pasta a varrer")
    cmd.opcao("formato", "texto", "f", "tabela", "tabela ou json", no,
              ["tabela", "json"])
    cmd.opcao("minimo", "inteiro", "m", 0, "esconde extensões abaixo disto")
    cmd.exemplo("contar src --formato=json", "para outro programa ler")
    yield cmd

// ── o trabalho, sem saber que existe terminal ──────────────
action contar(pasta):
    por_extensao := {}
    cycle nome in IO.list_dir(pasta):
        caminho := $"{pasta}/{nome}"
        given not IO.file_exists(caminho):
            skip
        ponto := caminho.split(".")
        ext := ponto[len(ponto) - 1] given len(ponto) > 1 otherwise "(sem)"
        linhas := len(IO.read(caminho).split("\\n"))
        por_extensao[ext] := (por_extensao[ext] ?? 0) + linhas
    yield por_extensao

// ── o desenho, que é a única parte que sabe ────────────────
action desenhar(dados, formato, minimo):
    filtrado := {}
    cycle ext in keys(dados):
        given dados[ext] >= minimo:
            filtrado[ext] := dados[ext]
    given formato is "json":
        yield Ser.to_json(filtrado)
    linhas := [["extensão", "linhas"]]
    cycle ext in sorted(keys(filtrado)):
        linhas.append([ext, str(filtrado[ext])])
    yield Cor.table(linhas)

// ── juntar ─────────────────────────────────────────────────
pasta := $"{OS.temp_dir()}/df-contar-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)
IO.write($"{pasta}/a.df", "out 1\\nout 2\\n")
IO.write($"{pasta}/b.df", "out 3\\n")
IO.write($"{pasta}/leiame.md", "# título\\n")

args := montar().ler([pasta, "--formato=json"])
dados := contar(args["pasta"])
assert dados["df"] is 5 and dados["md"] is 2
out desenhar(dados, args["formato"], args["minimo"])

// e em tabela
out desenhar(dados, "tabela", 0)''', "lang": "df"},
 {"h2": "As decisões que ela carrega"},
 {"table": {
   "head": ["Decisão", "O que ela evita"],
   "rows": [
     ["o trabalho não sabe que existe terminal", "não dá para testar contagem sem simular um terminal"],
     ["o desenho é a única parte que colore", "a cor vazar para o JSON, que outro programa vai ler"],
     ["`defer` logo depois de criar a pasta", "o temporário sobreviver a uma falha no meio"],
     ["`?? 0` ao somar no vault", "`KeyError` na primeira extensão nova"],
     ["a ajuda e os exemplos na declaração", "a ajuda envelhecer na primeira opção nova"]]}},
 {"h2": "O que falta para virar produção"},
 {"list": [
   "**Ignorar `.git`, `node_modules` e binários** — varrer tudo é o defeito nº 1 de um contador de linhas.",
   "**Um `--excluir` com padrão glob**, porque a lista do que ignorar é do projeto, não da ferramenta.",
   "**Paralelismo** quando a pasta é grande: `P.map` sobre os arquivos, que é E/S e por isso escapa do GIL.",
   "**Um teste que roda a ferramenta como processo** e confere o código de saída."]},
]},
]
