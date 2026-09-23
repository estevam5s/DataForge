# -*- coding: utf-8 -*-
"""O runtime por dentro, o sistema de arquivos, o REPL e o SQLite."""

PAGINAS = [
{
"href": "/docs/vm",
"title": "A máquina: como um .df executa",
"description": "Do texto ao resultado — lexer, parser, análise, compilação para fechamentos e o interpretador de árvore.",
"blocos": [
 {"p": "Esta página responde o que acontece entre você apertar Enter e o programa dar resposta. Ela é honesta sobre a parte que mais gera pergunta: **não há VM de bytecode**, e a razão está medida mais abaixo."},
 {"code": """arquivo.df → tokenize() → parse() → [check_program()] → run(ast)
             lexer.py    parser.py  typechecker.py      interpreter.py
""", "lang": "text"},

 {"h2": "As cinco etapas"},
 {"table": {"head": ["Etapa", "Arquivo", "O que entra e o que sai"], "rows": [
   ["**léxico**", "`lexer.py`", "texto → tokens, com INDENT/DEDENT e interpolação"],
   ["**sintaxe**", "`parser.py`", "tokens → árvore, por descida recursiva"],
   ["**análise**", "`typechecker.py`", "árvore → diagnósticos, sem executar nada"],
   ["**compilação**", "`compilador.py`", "árvore → fechamentos Python, uma vez"],
   ["**execução**", "`interpreter.py`", "fechamentos → o programa rodando"]]}},
 {"p": "A análise é **opcional** para rodar e obrigatória no `check`: é a mesma função nos dois casos, e é por isso que o editor, o CI e a linha de comando nunca discordam."},

 {"h2": "A indentação vira token"},
 {"p": "Blocos por indentação exigem que o lexer conte colunas e emita marcas — não há chave para o parser casar:"},
 {"code": """given x > 5:
    out "grande"
out "fim"
""", "lang": "df"},
 {"code": """GIVEN  IDENT(x)  GT  INT(5)  COLON  NEWLINE
INDENT  OUT  STRING  NEWLINE
DEDENT  OUT  STRING  NEWLINE  EOF
""", "lang": "text"},
 {"p": "Tab é erro, e não equivalente a espaços: a mistura dos dois produz um arquivo que se lê de um jeito e executa de outro, conforme a largura do tab no editor de cada um."},

 {"h2": "Despacho: de string para tabela, e daí para fechamento"},
 {"p": "O interpretador começou despachando por **nome de classe** — um nó `GivenBlock` procurava `exec_GivenBlock`. Funciona e é lento: é uma busca de atributo por instrução executada, e um programa médio executa mais de um milhão."},
 {"p": "Hoje há duas camadas:"},
 {"list": [
   "**Tabela por classe** — o nome vira uma entrada de dicionário resolvida uma vez.",
   "**Compilação para fechamentos** — a árvore é percorrida **uma vez** e cada nó vira uma função Python que faz o que aquele nó faz. Executar passa a ser chamar funções: sem busca, sem `isinstance`, sem ler campo de nó."], "ordered": True},
 {"code": """// o que a compilação faz, em espírito
// antes:  a cada volta, olhar o nó e decidir o que ele é
// depois: uma função por nó, decidida uma vez

soma := 0
cycle i from 1 to 1000000:
    soma += i
""", "lang": "df"},
 {"p": "Medido: **1,5× a 1,8×**, conforme a carga. Três regras governam esse arquivo, e a terceira é a que mais surpreende:"},
 {"table": {"head": ["Regra", "Porque"], "rows": [
   ["cada construtor espelha um `exec_`/`eval_` e **delega aos mesmos auxiliares**", "a semântica não é reimplementada; divergir faria a linguagem responder duas coisas"],
   ["o que não está na tabela **recua** para o interpretador", "um recurso novo continua funcionando sem tocar aqui — só não fica mais rápido"],
   ["o **depurador desliga tudo**", "ele para em cada linha sombreando `execute`, e o corpo compilado passaria por fora: um depurador que enxerga metade das instruções é pior que um interpretador lento"]]}},

 {"h2": "Por que não há bytecode"},
 {"p": "A pergunta é justa: quase toda linguagem interpretada compila para bytecode e roda uma VM. A resposta é um número."},
 {"table": {"head": ["Técnica", "Ganho medido", "Custo"], "rows": [
   ["interpretador de árvore (o ponto de partida)", "1×", "—"],
   ["tabela de despacho", "incluída abaixo", "pequeno"],
   ["**compilação para fechamentos** (hoje)", "**1,5× a 1,8×**", "um arquivo de 330 linhas"],
   ["VM de bytecode **em Python**", "~6,5× (o teto)", "reescrever o interpretador inteiro"],
   ["sair do Python", "muito mais", "a promessa de zero dependência acaba"]]}},
 {"p": "O teto de **6,5×** é o ponto: uma VM escrita em Python continua sendo Python executando o laço de despacho. O ganho existe e não é transformador, e o custo é reescrever a parte do sistema que mais tem teste e mais tem semântica sutil."},
 {"callout": {"tipo": "nota", "titulo": "Onde o esforço foi, em vez disso", "texto": "Sete gargalos medidos com `cProfile` — não com intuição. O maior: as tabelas de método de texto, vault e cluster eram literais reconstruídos a **cada** acesso, e 146 lambdas nasciam num `xs.append(i)`. 200 mil `append`: **0,77 s → 0,27 s**. Nenhum deles estava onde se esperava."}},

 {"h2": "O escopo, e a otimização mais perigosa"},
 {"p": "Um laço reaproveita o escopo entre voltas — alocar um por volta é caro. Mas se o corpo **captura** o escopo (uma ação, um `lambda`, um `blueprint`, um `thread`, um `defer`), cada volta precisa do seu:"},
 {"code": """acoes := []
cycle i from 1 to 3:
    acoes.append(lambda: i)

out [f() cycle f in acoes]      // [1, 2, 3] — e não [3, 3, 3]
""", "lang": "df"},
 {"p": "Sem essa distinção, as três closures veriam o último valor — o clássico que existe em várias linguagens e que aqui não acontece. A varredura olha a árvore **inteira**, e não só as instruções: um `lambda` vive dentro de uma expressão."},

 {"h2": "A pilha, e o salto de cauda"},
 {"p": "O teto de quadros é mil, e recursão legítima o atinge: uma travessia de árvore de cinco mil nós não tem nada de infinita. Há duas saídas, e a primeira é automática:"},
 {"code": """action somar_ate(n, total := 0):
    given n is 0:
        yield total
    yield somar_ate(n - 1, total + n)     // retorno INTEIRO: vira salto

out somar_ate(50000)
""", "lang": "df"},
 {"p": "`yield f(…)` como retorno inteiro não empilha: o quadro é reusado. Testado com 200 mil. Quatro casos são **recusados** pela análise, antes de rodar — há `defer` na ação, o `yield` está dentro de `monitor`, a recursão é indireta, ou **todo** `yield` da ação é cauda (aí ela nunca devolve, e virar laço mudo seria pior que o erro)."},

 {"h2": "Threads, processos e o GIL"},
 {"table": {"head": ["Ferramenta", "Paralelismo real", "Para quê"], "rows": [
   ["`thread:` / `parallel:`", "**não** em CPU", "rede, disco, banco, espera"],
   ["`async` / `await`", "**não** em CPU", "entrada e saída sobreposta"],
   ["`P.map_processos`", "**sim**", "trabalho de CPU — medido 4,71× em 10 núcleos"]]}},
 {"p": "O GIL do Python deixa uma thread por vez executar bytecode. A travessia de processo copia a **declaração** da ação, e não o fechamento — ver [complexidade em paralelo](/docs/big-o/paralelo)."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/referencia/arquitetura", "title": "Arquitetura do runtime", "desc": "o mapa dos arquivos, um por um"},
   {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que otimizar sem medir é chute"},
   {"href": "/docs/tecnicas/ponte", "title": "A ponte para o Python", "desc": "como um objeto estranho atravessa sem cópia"}]},
]},

{
"href": "/docs/arquivos",
"title": "Sistema de arquivos",
"description": "Ler, escrever, percorrer e não deixar lixo — Arcane.IO e Arcane.OS na prática.",
"blocos": [
 {"p": "Dois módulos dividem o trabalho: **`Arcane.IO`** mexe em arquivos e pastas; **`Arcane.OS`** responde sobre o ambiente — onde é a casa, qual é o temporário, o que há no `PATH`."},

 {"h2": "Ler e escrever"},
 {"code": """adopt Arcane.IO as IO

IO.write("notas.txt", "primeira linha\\n")
IO.append("notas.txt", "segunda linha\\n")

out IO.read("notas.txt").strip().split("\\n")
out IO.exists("notas.txt"), IO.size("notas.txt")
""", "lang": "df"},
 {"code": """[primeira linha, segunda linha]
yes 29
""", "lang": "text", "title": "saída"},
 {"p": "`IO.write` **sobrescreve**; `IO.append` acrescenta. Não há modo intermediário de propósito: um terceiro verbo com semântica sutil é o tipo de coisa que se erra às três da manhã."},

 {"h2": "Caminhos: monte, não concatene"},
 {"code": """IO.join(pasta, "dados", "brutos.csv")    // usa o separador do sistema
IO.basename("/tmp/a/b.txt")              // b.txt
IO.dirname("/tmp/a/b.txt")               // /tmp/a
IO.ext("/tmp/a/b.txt")                   // .txt
IO.abs("./relativo")                     // o caminho absoluto
""", "lang": "df"},
 {"p": "Concatenar com `+` produz um caminho que funciona no seu computador e falha no Windows — e o teste local nunca pega."},

 {"h2": "JSON e CSV, sem cerimônia"},
 {"code": """adopt Arcane.IO as IO

IO.write_json("config.json", {"porta": 8000, "debug": yes})
out IO.read_json("config.json")["porta"]          // 8000

// um cluster de VAULTS: a primeira linha vira o cabeçalho
IO.write_csv("dados.csv", [{"nome": "Ana", "idade": 30},
                           {"nome": "Bruno", "idade": 25}])
out IO.read("dados.csv").strip()
""", "lang": "df"},
 {"code": """nome,idade
Ana,30
Bruno,25
""", "lang": "text", "title": "saída"},
 {"p": "Na leitura, escolha a forma:"},
 {"code": """linhas := IO.read_csv("dados.csv")          // cluster de clusters
linhas := IO.read_csv("dados.csv", yes)     // cluster de VAULTS, pelo cabeçalho
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O vault era destruído em silêncio", "texto": "Até esta versão, `write_csv` passava a lista direto para o escritor — e iterar um vault dá as **chaves**. Gravar dois registros escrevia `nome,idade` duas vezes, e os valores sumiam sem erro nenhum. Perder dado calado é a pior falha possível numa função de gravar arquivo."}},

 {"h2": "Pastas"},
 {"code": """adopt Arcane.IO as IO

IO.mkdir("saida")                    // cria, inclusive os pais
out IO.list_dir("saida")             // o que há dentro
IO.copy("a.txt", "saida/a.txt")
IO.copy_tree("modelos", "saida/modelos")
IO.rename("saida/a.txt", "saida/b.txt")
IO.delete("saida/b.txt")             // um arquivo
IO.remove_tree("saida")              // a pasta inteira
""", "lang": "df"},
 {"callout": {"tipo": "perigo", "titulo": "`remove_tree` não pergunta", "texto": "`IO.remove_tree(OS.temp_dir())` destrói o temporário de **todo processo da máquina**. Um exercício deste repositório fez exatamente isso na primeira versão. Sempre uma subpasta própria."}},

 {"h2": "Arquivo ou pasta?"},
 {"p": "`IO.exists` responde *\u201cha algo aqui?\u201d*, e ha um caso em que isso nao basta: `list_dir` devolve **nomes**, e um deles pode ser uma subpasta. Todo `cycle` sobre uma pasta tinha de adivinhar."},
 {"code": """adopt Arcane.IO as IO

arquivos := []
pastas := []
cycle nome in IO.list_dir("."):
    caminho := IO.join(".", nome)
    given IO.is_file(caminho):
        arquivos.append({"nome": nome, "bytes": IO.size(caminho)})
    orif IO.is_dir(caminho):
        pastas.append(nome)

out $"{len(arquivos)} arquivo(s), {len(pastas)} pasta(s)"
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`size` de uma pasta nao e o que voce quer", "texto": "`IO.size` devolve o tamanho da **entrada** de diretorio, nao a soma do conteudo. Contar subpasta como arquivo nao levanta erro nenhum: o relatorio so sai com um numero a mais. O modelo `script` do `dataforge new` fazia isso, e foi so por ele que a falta de `is_file` apareceu."}},

 {"h2": "Temporário: sempre uma subpasta sua"},
 {"code": """adopt Arcane.IO as IO
adopt Arcane.OS as OS

base := $"{OS.temp_dir()}/meu-programa-{randint(100000, 999999)}"
IO.mkdir(base)

defer:
    IO.remove_tree(base)         // roda na saída da ação, inclusive por erro

IO.write(IO.join(base, "trabalho.txt"), "…")
""", "lang": "df"},
 {"p": "O `defer` é o que garante a limpeza quando a ação sai por erro — que é justamente quando ninguém lembra de limpar."},

 {"h2": "O ambiente, com `Arcane.OS`"},
 {"table": {"head": ["Pergunta", "Resposta"], "rows": [
   ["onde estou?", "`OS.cwd()`"],
   ["onde está o script?", "`OS.script_dir()`"],
   ["qual é a casa do usuário?", "`OS.home()`"],
   ["qual é o temporário?", "`OS.temp_dir()`"],
   ["qual sistema?", "`OS.is_windows()`, `OS.is_mac()`, `OS.is_linux()`"],
   ["quantos núcleos?", "`OS.cpu_count()`"],
   ["a variável de ambiente", "`OS.get_env(nome, padrao)`, `OS.set_env`, `OS.unset_env`"],
   ["este comando existe?", "`OS.which(\"git\")`"]]}},
 {"p": "`OS.unset_env` existe porque a falta dela aparecia como poluição entre execuções: um exercício imprimia 77 variáveis na primeira rodada e 78 na segunda. Ela devolve `yes`/`no` em vez de levantar — remover é pedir um estado final, e nesse ponto já não importa se estava lá."},

 {"h2": "Arquivo grande: não carregue inteiro"},
 {"p": "`IO.read` traz tudo para a memória. Para um arquivo maior que a RAM, processe por partes — ver [complexidade de espaço](/docs/big-o/espaco)."},
 {"code": """// O(n) de espaço: o arquivo inteiro na memória
todas := IO.read("grande.csv").split("\\n")

// O(1) de espaço: uma linha por vez
stream action linhas_de(caminho):
    cycle linha in IO.read(caminho).split("\\n"):
        emit linha

out linhas_de("grande.csv").take(3)
""", "lang": "df"},

 {"h2": "Erros: o que pode falhar, e como"},
 {"table": {"head": ["Situação", "O que acontece"], "rows": [
   ["ler arquivo que não existe", "erro, com o caminho na mensagem"],
   ["escrever em pasta que não existe", "erro — crie com `IO.mkdir` antes"],
   ["escrever sem permissão", "erro do sistema, traduzido"],
   ["`delete` de algo ausente", "erro — confira com `IO.exists`"],
   ["arquivo fora de UTF-8", "erro de leitura, dizendo qual arquivo"]]}},
 {"code": """monitor:
    config := IO.read_json("config.json")
handle Error as e:
    out $"usando o padrao: {e.message}"
    config := {"porta": 8000}
""", "lang": "df"},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/biblioteca/io", "title": "Arcane.IO", "desc": "a referência completa"},
   {"href": "/docs/biblioteca/os", "title": "Arcane.OS", "desc": "o ambiente, o processo e a máquina"},
   {"href": "/docs/tecnicas/arquivos", "title": "Receitas com arquivos", "desc": "padrões prontos"},
   {"href": "/docs/big-o/dados", "title": "Custo de I/O", "desc": "por que o bloco é a unidade"}]},
]},

{
"href": "/docs/repl",
"title": "O REPL",
"description": "O console interativo: avaliar, inspecionar a árvore, medir tempo e carregar um arquivo na sessão.",
"blocos": [
 {"p": "O REPL é onde se responde \"o que essa linha faz?\" sem criar arquivo. Ele carrega o mesmo interpretador, a mesma biblioteca e o mesmo analisador — o que você vê ali é o que o programa vai fazer."},
 {"code": """dataforge repl
""", "lang": "bash"},
 {"code": """forge> x := 21
forge> x * 2
=> 42
forge> :type x
Integer  = 21
forge> exit
""", "lang": "text"},

 {"h2": "Os comandos"},
 {"table": {"head": ["Comando", "O que faz"], "rows": [
   ["`:help`", "a lista (ou `help`)"],
   ["`:exit`", "sai (ou `exit`, `quit`, Ctrl+D)"],
   ["`:env`", "as variáveis definidas na sessão"],
   ["`:type <expr>`", "o tipo **e** o valor de uma expressão"],
   ["`:doc <nome>`", "o que é um nome definido na sessão"],
   ["`:check <código>`", "roda o analisador estático sobre o trecho"],
   ["`:tokens <código>`", "o fluxo de tokens — para entender o lexer"],
   ["`:ast <código>`", "a árvore sintática"],
   ["`:time <código>`", "executa e mede"],
   ["`:load <arquivo>`", "carrega e executa um `.df` **na sessão atual**"],
   ["`:save <arquivo>`", "grava o histórico da sessão num `.df`"],
   ["`:history [n]`", "os últimos comandos"],
   ["`:modules`", "os módulos `Arcane` disponíveis"],
   ["`:reset`", "zera o interpretador"],
   ["`:clear`", "limpa a tela"],
   ["`:version`", "a versão"]]}},

 {"h2": "Blocos de várias linhas"},
 {"p": "Uma linha terminada em `:` abre um bloco, que continua até uma **linha em branco**:"},
 {"code": """forge> action dobro(n):
   ...     yield n * 2
   ...
forge> dobro(21)
=> 42
""", "lang": "text"},

 {"h2": "Carregar um arquivo e continuar de dentro dele"},
 {"p": "`:load` é o que transforma o REPL em ferramenta de depuração: o programa roda, e você fica com **as variáveis dele** ao alcance."},
 {"code": """forge> :load src/main.df
forge> :env
forge> clientes[0]
forge> calcular_total(clientes)
""", "lang": "text"},

 {"h2": "Entender a linguagem por dentro"},
 {"p": "Três comandos existem para responder perguntas sobre a própria linguagem, e são os mesmos que se usa ao mexer no interpretador:"},
 {"code": """forge> :tokens x := 7 ~/ 2
forge> :ast given a: out 1
forge> :check xs := [1, 2]
       out xs[10]
""", "lang": "text"},
 {"p": "O `:tokens` é a forma rápida de resolver a dúvida do `//`: seguido de dígito é divisão, seguido de nome é comentário."},

 {"h2": "Medir no lugar certo"},
 {"code": """forge> :time [x * x cycle x in range(100000)]
""", "lang": "text"},
 {"p": "`:time` mede **aquela** expressão. Para comparar duas implementações com rigor, use [`Arcane.Bench`](/docs/tecnicas/bench); para achar onde o tempo vai num programa real, `dataforge profile`."},

 {"h2": "O que o REPL não é"},
 {"list": [
   "**Não é um editor.** Para algo com mais de dez linhas, `:save` e siga num arquivo.",
   "**Não guarda estado entre sessões.** `:save` grava o histórico; fechar o console perde as variáveis.",
   "**Não substitui teste.** O que funcionou no console precisa virar `trial` para continuar funcionando amanhã."]},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/cli/repl", "title": "Referência do comando", "desc": "as opções de linha de comando"},
   {"href": "/docs/cli/explain", "title": "dataforge explain", "desc": "o que um código de erro significa"},
   {"href": "/docs/primeiros-passos", "title": "Primeiros passos", "desc": "a linguagem em cinco minutos"}]},
]},
]
