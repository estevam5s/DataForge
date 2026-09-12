"""
DataForge CLI (Command Line Interface)
Main entry point for the DataForge language.
"""

import re
import sys
import os
import time

from . import __version__
from .lexer import tokenize
from .parser import parse
from .interpreter import Interpreter
from .repl import start_repl
from .caminhos import curto as _curto
from .errors import DataForgeError


# A marca no terminal vem de dataforge/marca.py, que a gera de logo.png.
# Escrever o nome em ASCII era o que se fazia antes de a linguagem ter
# uma marca — agora ela tem, e a CLI mostra a mesma do site.
from . import marca
from .marca import marca_colorida as _marca


# ═══════════════════════════════════════════════════════════
#  Catalogo de comandos
#
#  Uma entrada por comando, agrupada por proposito. E daqui que saem
#  o help geral, a ajuda de cada comando e a sugestao quando alguem
#  erra o nome — assim as tres nunca divergem.
# ═══════════════════════════════════════════════════════════

class Cmd:
    """Um comando da CLI."""

    __slots__ = ("nome", "uso", "resumo", "detalhe", "opcoes",
                 "exemplos", "apelidos", "veja")

    def __init__(self, nome, uso, resumo, detalhe="", opcoes=(),
                 exemplos=(), apelidos=(), veja=()):
        self.nome = nome
        self.uso = uso
        self.resumo = resumo
        self.detalhe = detalhe
        self.opcoes = opcoes          # [(flag, descricao)]
        self.exemplos = exemplos      # [(comando, o que faz)]
        self.apelidos = apelidos
        self.veja = veja              # comandos relacionados


GRUPOS = [
    ("Projeto", [
        Cmd("init", "dataforge init [pasta]",
            "Cria forge.toml e o esqueleto do projeto",
            "Escreve o manifesto, a pasta src/ com um main.df e a tests/.\n"
            "Sem argumento, usa a pasta atual.",
            exemplos=[("dataforge init", "aqui mesmo"),
                      ("dataforge init meu-app", "numa pasta nova")],
            veja=("new", "info")),
        Cmd("api", "dataforge api <arquivo.df> [--formato]",
            "exporta a API de um servidor Kiln",
            detalhe=(
                "As rotas sao a fonte da verdade: o arquivo e executado\n"
                "para que elas se registrem, e o resultado sai do que\n"
                "esta la — nao de uma descricao escrita a mao, que\n"
                "divergiria na primeira semana.\n\n"
                "Aponte para o modulo que MONTA o servidor ('app.df'), e\n"
                "nao para o que sobe ('main.df')."),
            opcoes=(
                ("--openapi", "OpenAPI 3.1 — Swagger, geradores de cliente"),
                ("--insomnia", "colecao do Insomnia, uma requisicao por rota"),
                ("--postman", "colecao do Postman v2.1"),
                ("--curl", "um comando curl por rota"),
                ("--markdown", "a tabela de rotas (padrao)"),
                ("--saida=<arq>", "grava em vez de imprimir"),
            ),
            exemplos=(
                ("dataforge api src/app.df", "a tabela de rotas"),
                ("dataforge api src/app.df --openapi -o=openapi.json", ""),
                ("dataforge api src/app.df --insomnia -o=insomnia.json", ""),
            ),
            veja=("run", "test")),
        Cmd("converter", "dataforge converter <arquivo.py|pasta>",
            "traduz Python para DataForge",
            detalhe=(
                "Le com o 'ast' do Python, e nao com expressao regular.\n"
                "O que nao tem equivalente honesto vira um comentario\n"
                "'TODO(converter)' com o codigo original ao lado — um\n"
                "conversor que erra em silencio e pior que um que aponta\n"
                "onde errou.\n\n"
                "O relatorio no fim conta as duas coisas: o que saiu pronto\n"
                "e o que precisa de voce."),
            opcoes=(
                ("--saida=<arq>", "onde gravar (um arquivo so)"),
                ("--seco", "mostra sem gravar"),
                ("--forcar", "sobrescreve um .df que ja exista"),
            ),
            exemplos=(
                ("dataforge converter app.py", "grava app.df ao lado"),
                ("dataforge converter src/", "a pasta inteira, recursiva"),
                ("dataforge converter app.py --seco", "so mostra"),
            ),
            apelidos=("convert", "migrar"),
            veja=("check", "fmt")),
        Cmd("new", "dataforge new [modelo] [nome]",
            "Cria um projeto a partir de um modelo",
            "Oito modelos, e todos produzem um projeto que RODA e passa\n"
            "nos proprios testes — nao um esqueleto com TODOs:\n"
            "\n"
            "  cli      ferramenta de linha de comando, com --help\n"
            "  api      API REST com o Kiln, testes sem abrir socket\n"
            "  web      site com paginas HTML e arquivos estaticos\n"
            "  data     banco, estatistica e exportacao para Excel\n"
            "  lib      biblioteca com relay, pronta para publicar\n"
            "  oop      blueprints, traits, propriedades, operadores\n"
            "  script   automacao: arquivos, JSON, datas\n"
            "  test     como se testa em DataForge\n"
            "\n"
            "Sem argumento, pergunta na tela.",
            opcoes=[("--list", "so lista os modelos, sem perguntar nada")],
            exemplos=[("dataforge new", "escolhe na tela"),
                      ("dataforge new api", "usa o modelo, pergunta o nome"),
                      ("dataforge new api minha-api", "direto ao ponto"),
                      ("dataforge new --list", "so os modelos")],
            veja=("init", "run", "test")),
        Cmd("info", "dataforge info",
            "Mostra o manifesto do projeto atual",
            "Nome, versao, entrada, scripts e dependencias declaradas.",
            veja=("init", "list")),
    ]),

    ("Executar", [
        Cmd("run", "dataforge run [arquivo.df] [-- args]",
            "Executa um programa",
            "Sem arquivo, usa a entrada declarada no forge.toml.\n"
            "O que vier depois de '--' chega ao programa em OS.argv().",
            opcoes=[("--time", "mostra o tempo de execucao"),
                    ("--debug", "mostra tokens, AST e traceback completo")],
            exemplos=[("dataforge run ola.df", ""),
                      ("dataforge run", "usa a entrada do forge.toml"),
                      ("dataforge run app.df -- --porta 8080",
                       "passa argumentos ao programa")],
            veja=("eval", "watch", "repl")),
        Cmd("eval", "dataforge eval \'<codigo>\'",
            "Executa uma linha de codigo direto",
            "Para experimentar sem criar arquivo. Multiplas instrucoes\n"
            "podem ser separadas por ponto e virgula ou quebra de linha.",
            exemplos=[('dataforge eval \'out 2 ** 10\'', ""),
                      ('dataforge eval \'out [1,2,3] >> morph n: n * 2\'', "")],
            veja=("run", "repl")),
        Cmd("watch", "dataforge watch [arquivo.df]",
            "Reexecuta a cada mudanca no arquivo",
            "Fica observando e roda de novo quando voce salva.\n"
            "Ctrl+C para sair.",
            opcoes=[("--test", "roda a suite em vez do arquivo"),
                    ("--check", "roda a analise estatica")],
            exemplos=[("dataforge watch src/main.df", ""),
                      ("dataforge watch --test", "TDD: a suite a cada save")],
            veja=("run", "test")),
        Cmd("repl", "dataforge repl",
            "Console interativo",
            "Comandos internos: :type <expr>, :ast <expr>, :check <expr>,\n"
            ":load <arquivo>, :vars, :help, :quit.",
            veja=("run", "eval")),
    ]),

    ("Qualidade", [
        Cmd("check", "dataforge check [alvo]",
            "Analise estatica: nomes, aridade, tipos e alcance",
            "Aceita arquivo, pasta ou padrao. Sem alvo, analisa a pasta atual.\n"
            "Sai com codigo 1 se houver erro — serve na esteira de CI.",
            opcoes=[("--strict", "trata avisos como erros"),
                    ("--syntax-only", "so a sintaxe, sem analise semantica")],
            exemplos=[("dataforge check .", "o projeto inteiro"),
                      ("dataforge check src/ --strict", "avisos viram erros")],
            veja=("lint", "explain")),
        Cmd("test", "dataforge test [alvo]",
            "Executa a suite de testes",
            "Descobre *_test.df e a pasta tests/. Cada acao que comeca\n"
            "com 'test_' vira um caso.",
            opcoes=[("--verbose, -v", "mostra cada caso"),
                    ("--filter=<texto>", "so os casos cujo nome contem o texto"),
                    ("--fail-fast", "para na primeira falha")],
            exemplos=[("dataforge test", ""),
                      ("dataforge test tests/ -v", ""),
                      ("dataforge test --filter=soma", "so o que casa")],
            veja=("bench", "watch")),
        Cmd("fmt", "dataforge fmt [alvo]",
            "Formata o codigo",
            "Idempotente: formatar duas vezes da o mesmo resultado.",
            opcoes=[("--check", "so verifica, nao reescreve (sai 1 se houver "
                                "pendencia)")],
            exemplos=[("dataforge fmt .", "reescreve"),
                      ("dataforge fmt . --check", "para a esteira de CI")],
            veja=("lint",)),
        Cmd("lint", "dataforge lint [alvo]",
            "Aponta problemas de estilo e higiene",
            "Treze regras: nome fora do padrao, variavel escrita e nunca\n"
            "lida, ramo redundante, e outras.",
            opcoes=[("--strict", "trata avisos como erros")],
            veja=("fmt", "check")),
        Cmd("bench", "dataforge bench <arquivo.df>",
            "Mede o tempo de execucao, repetindo",
            "Roda varias vezes e mostra minimo, mediana e desvio.\n"
            "Descarta as primeiras execucoes, que aquecem o cache.",
            opcoes=[("--runs=<n>", "quantas repeticoes (padrao 10)")],
            exemplos=[("dataforge bench algoritmo.df", ""),
                      ("dataforge bench alg.df --runs=50", "")],
            veja=("test", "run")),
    ]),

    ("Pacotes", [
        Cmd("add", "dataforge add <pacote>[@versao] …",
            "Instala uma dependencia e grava no forge.toml",
            "Sem faixa, grava '^' da versao mais recente. Aceita tambem\n"
            "caminho local, git+URL e URL de tarball.",
            opcoes=[("--offline", "so com o cache local")],
            exemplos=[("dataforge add validador", ""),
                      ("dataforge add tabela@^2.0", "faixa de versoes"),
                      ("dataforge add ../lib-interna", "pasta local")],
            veja=("install", "remove", "search")),
        Cmd("remove", "dataforge remove <pacote> …",
            "Desinstala e tira do forge.toml",
            apelidos=("rm", "uninstall"), veja=("add", "list")),
        Cmd("install", "dataforge install",
            "Instala tudo o que o forge.toml declara",
            "O comando que se roda depois de clonar um projeto.",
            opcoes=[("--dry-run", "mostra o plano sem baixar"),
                    ("--offline", "so com o cache local")],
            apelidos=("i", "sync"), veja=("add", "list", "tree")),
        Cmd("list", "dataforge list",
            "Mostra o que esta instalado",
            "Marca as transitivas e o que sumiu do disco.",
            apelidos=("ls",), veja=("tree", "outdated")),
        Cmd("tree", "dataforge tree",
            "Desenha a arvore de dependencias",
            "Mostra quem trouxe cada pacote, e onde ha versao compartilhada.",
            veja=("list", "why")),
        Cmd("why", "dataforge why <pacote>",
            "Explica por que um pacote esta instalado",
            "Mostra a cadeia desde o forge.toml ate ele.",
            exemplos=[("dataforge why tabela", "")],
            veja=("tree", "list")),
        Cmd("outdated", "dataforge outdated",
            "Lista dependencias com versao mais nova disponivel",
            "Separa o que cabe na faixa declarada do que exigiria\n"
            "mudar o forge.toml.",
            veja=("add", "list")),
        Cmd("search", "dataforge search <termo>",
            "Procura pacotes no registro",
            "Busca no nome, na descricao e nas tags.",
            exemplos=[("dataforge search cpf", ""),
                      ('dataforge search ""', "lista tudo")],
            veja=("add",)),
        Cmd("pack", "dataforge pack",
            "Empacota este projeto para publicar",
            "Gera dist/<nome>-<versao>.tar.gz com o sha256.\n"
            "Reprodutivel: mesma fonte, mesmo hash.",
            veja=("publish",)),
        Cmd("publish", "dataforge publish --registry=<pasta>",
            "Publica o pacote num registro",
            "O registro e uma pasta com index.json e pacotes/.",
            veja=("pack",)),
    ]),

    ("Analise", [
        Cmd("stats", "dataforge stats [alvo]",
            "O tamanho e a forma do codigo",
            "Nao e 'linhas de codigo' como metrica de produtividade — e o\n"
            "inventario: quantas acoes, quantos blueprints, o arquivo mais\n"
            "longo, a acao mais longa.\n"
            "\nServe para achar o que cresceu demais sem ninguem notar. Uma\n"
            "acao acima de 50 linhas costuma fazer mais de uma coisa.",
            exemplos=[("dataforge stats", "o projeto inteiro"),
                      ("dataforge stats src/", "so uma pasta")],
            veja=("lint", "check")),
        Cmd("profile", "dataforge profile <arquivo>",
            "Onde o tempo foi gasto, acao por acao",
            "Um 'bench' diz que esta lento; um 'profile' diz ONDE.\n"
            "Mede cada acao: quantas chamadas, tempo acumulado e por\n"
            "chamada, ordenado pelo que mais custa.\n"
            "\nMeca antes de otimizar. A acao que voce acha que e o gargalo\n"
            "quase nunca e.",
            exemplos=[("dataforge profile src/main.df", "")],
            veja=("bench", "run")),
        Cmd("fix", "dataforge fix [alvo]",
            "Formata e aponta o que precisa de voce",
            "Roda o formatador e, em seguida, o linter — arrumando o que da\n"
            "para arrumar sozinho e listando o resto.\n"
            "\nO que exige julgamento nao e 'consertado' automaticamente:\n"
            "uma ferramenta que muda o codigo precisa ser previsivel.",
            opcoes=[("--dry-run", "mostra o que faria, sem escrever")],
            exemplos=[("dataforge fix", "o projeto inteiro"),
                      ("dataforge fix --dry-run", "so o relatorio")],
            veja=("fmt", "lint")),
    ]),
    ("Ambiente", [
        Cmd("vitrine", "dataforge vitrine <run|dev|doctor|new>",
            "Sobe um painel feito com Arcane.Vitrine",
            "Um programa de cima para baixo vira uma pagina web. 'dev'\n"
            "recarrega ao salvar; 'doctor' diz por que ela nao sobe.\n"
            "\nNao ha 'build': nao existe bundler nem transpilacao — o\n"
            "que roda e o proprio .df.",
            opcoes=[("--porta=<n>", "a porta (padrao 8501)"),
                    ("--host=<ip>", "o endereco (padrao 127.0.0.1)")],
            exemplos=[("dataforge vitrine dev", "sobe recarregando ao salvar"),
                      ("dataforge vitrine doctor", "o que falta para subir"),
                      ("dataforge vitrine new meupainel", "cria o projeto")],
            veja=("new", "run")),
        Cmd("editor", "dataforge editor [status|remove]",
            "Instala a coloracao de sintaxe no VS Code",
            "Copia a extensao para o VS Code, Insiders, Cursor, VSCodium e\n"
            "Windsurf — todos os que encontrar. Depois disso, todo arquivo\n"
            ".df abre com as palavras reservadas coloridas, 23 snippets e a\n"
            "indentacao de 4 espacos que a linguagem exige.\n"
            "\nO instalador ja faz isso; use este comando para reinstalar\n"
            "depois de atualizar o DataForge ou de instalar um editor novo.",
            opcoes=[("status", "mostra onde esta instalada"),
                    ("remove", "desinstala de todos os editores")],
            exemplos=[("dataforge editor", "instala em todos"),
                      ("dataforge editor status", "so confere")],
            veja=("version", "lsp")),
        Cmd("debug", "dataforge debug <arquivo.df>",
            "Roda parando onde voce mandar",
            "Para, mostra o que esta valendo e deixa andar de uma\n"
            "instrucao por vez. Dentro dele: 'p' passo, 'n' proximo,\n"
            "'f' sai da acao, 'c' continua, 'vars' lista o escopo,\n"
            "'pilha' mostra quem chamou quem, e qualquer expressao e\n"
            "avaliada no quadro onde voce parou.\n"
            "\nSem '--parar', ele para na primeira instrucao.",
            opcoes=[("--parar=N,M", "paradas ja nas linhas N e M")],
            exemplos=[("dataforge debug conta.df", "para no comeco"),
                      ("dataforge debug conta.df --parar=42", "so na linha 42")],
            veja=("run", "check")),
        Cmd("lsp", "dataforge lsp",
            "Servidor de linguagem para o editor",
            "Fala o Language Server Protocol por stdin/stdout. E o que da\n"
            "ao editor autocompletar sensivel a contexto, erro sublinhado\n"
            "enquanto se digita, ir-para-definicao, renomear com seguranca,\n"
            "o esquema do arquivo e ajuda de assinatura.\n"
            "\nVoce nao o roda a mao: a extensao do VS Code o inicia\n"
            "sozinha. Este comando existe para outros editores — Neovim,\n"
            "Helix, Emacs — que perguntam qual comando iniciar.",
            opcoes=[("--log=ARQUIVO", "grava o que acontece, para depurar")],
            exemplos=[("dataforge lsp", "o que o editor executa"),
                      ("dataforge lsp --log=/tmp/lsp.log", "com registro")],
            veja=("editor", "check")),
    ]),
    ("Diagnostico", [
        Cmd("explain", "dataforge explain <codigo>",
            "Explica um codigo de erro",
            "Todo erro do DataForge tem um codigo estavel, como DF0601.\n"
            "Este comando diz o que ele significa e como resolver.",
            exemplos=[("dataforge explain DF0601", ""),
                      ("dataforge explain 0401", "o prefixo e opcional"),
                      ("dataforge explain KeyError", "o nome da classe tambem")],
            veja=("check", "erros")),
        Cmd("crucible", "dataforge crucible [alvo]",
            "Roda as suites do Crucible, o framework de testes",
            "Descobre os arquivos, carrega as suites e roda tudo junto.\n"
            "Sem alvo, procura em tests/, testes/ e *_crucible.df.",
            opcoes=[("--verbose, -v", "mostra tambem o que passou"),
                    ("--filtro=<t>", "so os trials cujo nome contem <t>"),
                    ("--tag=<a,b>", "so os marcados com estas tags"),
                    ("--sem-tag=<a>", "pula os marcados com esta tag"),
                    ("--aleatorio", "embaralha a ordem; ordem oculta aparece"),
                    ("--semente=<n>", "repete um embaralhamento especifico"),
                    ("--repetir=<n>", "roda cada trial n vezes"),
                    ("--prazo=<ms>", "falha o que passar deste tempo"),
                    ("--fail-fast", "para na primeira falha"),
                    ("--formato=<f>", "texto | junit | json | tap"),
                    ("--out=<arq>", "escreve o relatorio num arquivo"),
                    ("--matchers", "lista tudo o que se pode cobrar")],
            exemplos=[("dataforge crucible", "roda tudo"),
                      ("dataforge crucible --tag=rapido", "so os rapidos"),
                      ("dataforge crucible --formato=junit --out=r.xml",
                       "para o CI")],
            veja=("test", "bench")),
        Cmd("big-o", "dataforge big-o [alvo]",
            "Calcula a complexidade de cada acao, sem rodar o codigo",
            "Le a arvore e conta estrutura: lacos aninhados, recursao,\n"
            "e o custo das funcoes embutidas que aparecem. Diz a classe\n"
            "E o porque — 'O(n^2)' sozinho nao ajuda a melhorar nada.",
            opcoes=[("--verbose, -v", "mostra o porque e o que fazer"),
                    ("--escala", "a tabela do que cada classe custa"),
                    ("--json", "saida estruturada, para o editor"),
                    ("--strict", "sai com erro se algo passar de O(n log n)")],
            exemplos=[("dataforge big-o src/ -v", ""),
                      ("dataforge big-o --escala", "a tabela de referencia")],
            veja=("profile", "bench")),
        Cmd("custo", "dataforge custo [alvo]",
            "Mostra o que cada 'adopt' traz junto",
            "Uma linha de import nao parece cara. Um modulo de 200\n"
            "simbolos entra inteiro no processo.",
            exemplos=[("dataforge custo src/", "")],
            veja=("big-o",)),
        Cmd("erros", "dataforge erros [termo]",
            "Lista o catalogo de erros da linguagem",
            "Sao 177 codigos em 15 familias. Sem termo, lista tudo\n"
            "agrupado; com termo, procura no titulo e na explicacao.",
            exemplos=[("dataforge erros", "o catalogo inteiro"),
                      ("dataforge erros banco", "so o que fala de banco")],
            veja=("explain",)),
        Cmd("doc", "dataforge doc [alvo]",
            "Gera documentacao Markdown a partir dos comentarios",
            opcoes=[("--out=<arquivo>", "escreve num arquivo")],
            exemplos=[("dataforge doc src/ --out=doc/API.md", "")]),
        Cmd("deps", "dataforge deps [alvo]",
            "Mostra o grafo de imports do codigo",
            "Quem adota quem, e avisa sobre ciclos.",
            veja=("tree",)),
        Cmd("tokens", "dataforge tokens <arquivo>",
            "Mostra o fluxo de tokens (lexer)",
            veja=("ast",)),
        Cmd("ast", "dataforge ast <arquivo>",
            "Mostra a arvore sintatica (parser)",
            veja=("tokens",)),
        Cmd("clean", "dataforge clean",
            "Limpa caches e artefatos de build",
            "Remove dist/, __pycache__ e o cache de pacotes baixados.",
            opcoes=[("--all", "inclui forge_modules/ e o cache global")]),
        Cmd("version", "dataforge version",
            "Mostra a versao", apelidos=("--version", "-V")),
        Cmd("help", "dataforge help [comando]",
            "Mostra esta ajuda, ou a de um comando",
            exemplos=[("dataforge help", "visao geral"),
                      ("dataforge help add", "so o 'add'")],
            apelidos=("--help", "-h")),
    ]),
]

#: nome ou apelido -> Cmd
COMANDOS = {}
for _grupo, _lista in GRUPOS:
    for _c in _lista:
        COMANDOS[_c.nome] = _c
        for _a in _c.apelidos:
            COMANDOS[_a] = _c


def ajuda_geral():
    """O help principal: comandos agrupados por proposito."""
    linhas = ["", _marca(), ""]
    linhas.append(f"  {color('DataForge', '1;37')} "
                  f"{color('v' + __version__, '0;90')}"
                  f"  —  linguagem de programacao\n")
    linhas.append(f"  {color('USO', '1;36')}")
    linhas.append(f"      dataforge <comando> [alvo] [opcoes]\n")

    for grupo, comandos in GRUPOS:
        linhas.append(f"  {color(grupo.upper(), '1;36')}")
        for c in comandos:
            nome = c.nome.ljust(10)
            linhas.append(f"      {color(nome, '1;37')} {c.resumo}")
        linhas.append("")

    linhas.append(f"  {color('OPCOES GERAIS', '1;36')}")
    for flag, desc in [("--no-color", "desliga as cores"),
                       ("--debug", "traceback completo do interpretador"),
                       ("-h, --help", "ajuda de um comando")]:
        linhas.append(f"      {flag.ljust(14)} {desc}")
    linhas.append("")
    linhas.append(f"  {color('PARA COMECAR', '1;36')}")
    linhas.append(f"      dataforge init meu-app     cria um projeto")
    linhas.append(f"      dataforge repl             experimenta a linguagem")
    linhas.append(f"      dataforge help run         ajuda de um comando\n")
    linhas.append(color("  documentacao: https://dataforge-lang.vercel.app/docs",
                        "0;90"))
    return "\n".join(linhas)


def ajuda_comando(nome):
    """A ajuda detalhada de um comando."""
    cmd = COMANDOS.get(nome)
    if cmd is None:
        return None

    linhas = [""]
    linhas.append(f"  {color(cmd.nome, '1;37')} — {cmd.resumo}")
    linhas.append("")
    linhas.append(f"  {color('USO', '1;36')}")
    linhas.append(f"      {cmd.uso}")

    if cmd.apelidos:
        linhas.append("")
        linhas.append(f"  {color('TAMBEM', '1;36')}")
        linhas.append(f"      {', '.join(cmd.apelidos)}")

    if cmd.detalhe:
        linhas.append("")
        for linha in cmd.detalhe.split("\n"):
            linhas.append(f"      {linha}")

    if cmd.opcoes:
        linhas.append("")
        linhas.append(f"  {color('OPCOES', '1;36')}")
        larg = max(len(o[0]) for o in cmd.opcoes) + 2
        for flag, desc in cmd.opcoes:
            linhas.append(f"      {color(flag.ljust(larg), '1;37')} {desc}")

    if cmd.exemplos:
        linhas.append("")
        linhas.append(f"  {color('EXEMPLOS', '1;36')}")
        larg = max(len(e[0]) for e in cmd.exemplos) + 2
        for comando, o_que in cmd.exemplos:
            sufixo = color(f"  {o_que}", "0;90") if o_que else ""
            linhas.append(f"      {comando.ljust(larg) if o_que else comando}"
                          f"{sufixo}")

    if cmd.veja:
        linhas.append("")
        linhas.append(f"  {color('VEJA TAMBEM', '1;36')}")
        linhas.append(f"      {', '.join(cmd.veja)}")

    linhas.append("")
    return "\n".join(linhas)


def comando_parecido(nome):
    """Sugestao para quem errou o nome do comando."""
    import difflib
    perto = difflib.get_close_matches(nome, sorted(COMANDOS), n=3, cutoff=0.6)
    return perto


USAGE = None      # montado sob demanda, para as cores respeitarem --no-color


def color(text: str, code: str) -> str:
    """Apply ANSI color if supported."""
    if '--no-color' in sys.argv:
        return text
    return f"\033[{code}m{text}\033[0m"


def run_file(filepath: str, debug: bool = False, show_time: bool = False):
    """Execute a DataForge source file."""
    if not os.path.exists(filepath):
        print(color(f"Error: File not found: {filepath}", "1;31"))
        sys.exit(1)

    if not filepath.endswith('.df'):
        print(color(f"Warning: File does not have .df extension: {filepath}", "1;33"))

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        start_time = time.perf_counter()

        # Tokenize
        tokens = tokenize(source, filepath)
        if debug:
            print(color("── TOKENS ──", "1;35"))
            for tok in tokens:
                print(f"  {tok}")
            print()

        # Parse
        tree = parse(tokens, filepath)
        if debug:
            print(color("── AST ──", "1;35"))
            print(f"  Program with {len(tree.body)} statements")
            print()

        # Interpret
        interpreter = Interpreter()

        # Set __file__ and __name__
        interpreter.global_env.set_local("__file__", filepath)
        interpreter.global_env.set_local("__name__", "__main__")

        result = interpreter.run(tree, filename=filepath)

        end_time = time.perf_counter()

        if show_time:
            elapsed = (end_time - start_time) * 1000
            print(color(f"\n⚡ Execution time: {elapsed:.2f}ms", "1;36"))

    except DataForgeError as e:
        print()
        print(e.render(color='--no-color' not in sys.argv,
                       source_lines=source.splitlines(), debug=debug))
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(color(f"\nInternal Error: {e}", "1;31"))
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def show_tokens(filepath: str):
    """Show token stream for a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tokens = tokenize(source, filepath)
    print(color(f"── Tokens for {filepath} ──", "1;35"))
    for tok in tokens:
        print(f"  {tok}")


def show_ast(filepath: str):
    """Show AST for a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tokens = tokenize(source, filepath)
    tree = parse(tokens, filepath)
    print(color(f"── AST for {filepath} ──", "1;35"))
    print(f"  Program: {len(tree.body)} top-level statements")
    for i, stmt in enumerate(tree.body):
        print(f"  [{i}] {type(stmt).__name__}")


def check_file(filepath: str, strict: bool = False, only_syntax: bool = False):
    """Analisa sintaxe e semântica sem executar o programa."""
    from .typechecker import check_program

    if not os.path.exists(filepath):
        print(color(f"Erro: arquivo não encontrado: {filepath}", "1;31"))
        sys.exit(1)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tokens = tokenize(source, filepath)
        tree = parse(tokens, filepath)
    except DataForgeError as e:
        print(color(f"✗ {filepath}: {e.format()}", "1;31"))
        sys.exit(1)

    if only_syntax:
        print(color(f"✓ {filepath}: sintaxe ok ({len(tree.body)} instruções)", "1;32"))
        return

    diagnosticos = check_program(tree, filepath, strict=strict)
    erros = [d for d in diagnosticos if d.severity == 'error']
    avisos = [d for d in diagnosticos if d.severity == 'warning']
    usar_cor = '--no-color' not in sys.argv

    for d in sorted(diagnosticos, key=lambda x: (x.line, x.column)):
        print(d.format(filepath, color=usar_cor))

    if erros:
        print(color(f"\n✗ {len(erros)} erro(s), {len(avisos)} aviso(s)", "1;31"))
        sys.exit(1)
    if avisos:
        print(color(f"\n✓ sem erros, {len(avisos)} aviso(s)", "1;33"))
        return
    print(color(f"✓ {filepath}: sem erros "
                f"({len(tree.body)} instruções analisadas)", "1;32"))



def check_command(alvos, strict=False, only_syntax=False):
    """dataforge check — analisa um arquivo, uma pasta ou um padrao.

    Um unico arquivo mantem a saida detalhada de sempre. Com varios,
    imprime os diagnosticos de cada um e um resumo no fim.
    """
    from .typechecker import check_program

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        alvo = alvos[0] if alvos else "."
        print(color(f"Nenhum arquivo .df encontrado em: {alvo}", "1;33"))
        sys.exit(1)

    if len(arquivos) == 1:
        check_file(arquivos[0], strict=strict, only_syntax=only_syntax)
        return

    usar_cor = '--no-color' not in sys.argv
    total_erros = total_avisos = ilegiveis = 0

    for caminho in arquivos:
        fonte, motivo = _ler(caminho)
        if motivo:
            print(color(f"\u2717 {caminho}: {motivo}", "1;31"))
            ilegiveis += 1
            continue
        try:
            arvore = parse(tokenize(fonte, caminho), caminho)
        except DataForgeError as e:
            print(color(f"\u2717 {caminho}: {e.format()}", "1;31"))
            total_erros += 1
            continue

        if only_syntax:
            continue

        for d in sorted(check_program(arvore, caminho, strict=strict),
                        key=lambda x: (x.line, x.column)):
            print(d.format(caminho, color=usar_cor))
            if d.severity == 'error':
                total_erros += 1
            else:
                total_avisos += 1

    n = len(arquivos)
    if total_erros or ilegiveis:
        resumo = f"{total_erros} erro(s), {total_avisos} aviso(s)"
        if ilegiveis:
            resumo += f", {ilegiveis} arquivo(s) ilegivel(is)"
        print(color(f"\n\u2717 {resumo} em {n} arquivo(s)", "1;31"))
        sys.exit(1)
    if total_avisos:
        print(color(f"\n\u2713 sem erros, {total_avisos} aviso(s) "
                    f"em {n} arquivo(s)", "1;33"))
        return
    print(color(f"\u2713 {n} arquivo(s) sem erros", "1;32"))


# ─── Gerenciador de pacotes ─────────────────────────────────────

def _manifesto_ou_sair():
    from . import project as proj
    m = proj.carregar(".")
    if m is None:
        print(color("Nenhum forge.toml encontrado.", "1;31"))
        print("  Crie um projeto com:  dataforge init")
        sys.exit(1)
    return m


def _escrever_dependencias(manifesto, mapa):
    """Reescreve so a secao [dependencies] do forge.toml, preservando o resto.

    Reserializar o arquivo inteiro perderia comentarios e ordem; por isso a
    substituicao e textual, com fallback para acrescentar a secao no fim.
    """
    texto = open(manifesto.caminho, encoding="utf-8").read()

    linhas = ["[dependencies]"]
    for nome in sorted(mapa):
        valor = mapa[nome]
        if isinstance(valor, dict):
            campos = ", ".join(f'{k} = "{v}"' for k, v in valor.items())
            linhas.append(f"{nome} = {{ {campos} }}")
        else:
            linhas.append(f'{nome} = "{valor}"')
    bloco = "\n".join(linhas)

    padrao = re.compile(r"^\[dependencies\]\s*$.*?(?=^\[|\Z)",
                        re.MULTILINE | re.DOTALL)
    if padrao.search(texto):
        texto = padrao.sub(bloco + "\n\n", texto, count=1)
    else:
        texto = texto.rstrip() + "\n\n" + bloco + "\n"

    open(manifesto.caminho, "w", encoding="utf-8").write(texto)


def _sincronizar(manifesto, alvos=None, offline=False, so_conferir=False):
    """Resolve e instala. Devolve a lista de (nome, versao, fonte)."""
    from . import packages as pk

    registro = pk.Registro(offline=offline)
    declaradas = pk.ler_dependencias(manifesto.dependencies)
    if alvos:
        declaradas = [d for d in declaradas if d.nome in alvos]
    if not declaradas:
        print(color("Nenhuma dependencia declarada.", "1;33"))
        print("  Adicione uma com:  dataforge add <pacote>")
        return []

    try:
        plano = pk.resolver(declaradas, registro, raiz=manifesto.raiz)
    except pk.ErroPacote as e:
        print(color(f"✗ {e}", "1;31"))
        sys.exit(1)
    lock = pk.Lock(manifesto.raiz)
    instalados = []

    for nome in sorted(plano):
        item = plano[nome]
        rotulo = f"{nome}@{item['versao']}" if item["versao"] else nome
        if so_conferir:
            print(f"  {rotulo}  ({item['dep'].fonte})")
            instalados.append((nome, item["versao"], item["dep"].fonte))
            continue
        try:
            versao, sha, fonte = pk.instalar_pacote(
                nome, item, manifesto.raiz, registro)
        except pk.ErroPacote as e:
            print(color(f"  ✗ {nome}: {e}", "1;31"))
            sys.exit(1)
        transitivas = {}
        if item["dep"].fonte == "registro":
            transitivas = registro.lancamento(nome, versao).get("dependencias", {})
        lock.registrar(nome, versao, fonte, sha, transitivas)
        print(color(f"  + {nome}@{versao}", "1;32") +
              color(f"  ({fonte})", "0;90"))
        instalados.append((nome, versao, fonte))

    if not so_conferir:
        lock.gravar(registro.url)
    return instalados


def add_command(alvos, offline=False, salvar=True):
    """dataforge add <pacote>[@versao] — instala e grava no forge.toml."""
    from . import packages as pk

    if not alvos:
        print(color("Erro: informe ao menos um pacote.", "1;31"))
        print("  dataforge add validador")
        print("  dataforge add validador@1.2.0")
        print("  dataforge add tabela@^2.0")
        print("  dataforge add ./lib-local")
        print("  dataforge add git+https://github.com/alguem/lib.git")
        sys.exit(1)

    manifesto = _manifesto_ou_sair()
    registro = pk.Registro(offline=offline)
    deps = dict(manifesto.dependencies)
    novos = []

    for alvo in alvos:
        # 'nome@faixa' so e versao se o alvo nao for caminho nem URL
        if "@" in alvo and not alvo.startswith((".", "/", "http", "git+")):
            nome, _, faixa = alvo.partition("@")
        else:
            nome, faixa = alvo, ""

        if alvo.startswith((".", "/", "http", "git+")):
            dep = pk.Dependencia(os.path.basename(alvo.rstrip("/")).replace(".git", ""), alvo)
            deps[dep.nome] = dep.para_toml()
            novos.append(dep.nome)
            continue

        try:
            disponiveis = registro.versoes(nome)
        except pk.ErroPacote as e:
            print(color(f"✗ {e}", "1;31"))
            sys.exit(1)

        requisito = pk.Requisito(faixa or "*")
        escolhida = requisito.melhor(disponiveis)
        if escolhida is None:
            print(color(f"✗ '{nome}' nao tem versao que satisfaca '{faixa}'. "
                        f"Ha: {', '.join(sorted(disponiveis))}", "1;31"))
            sys.exit(1)

        # sem faixa explicita, trava o 'maior' — a convencao do npm e do cargo
        deps[nome] = faixa or f"^{escolhida}"
        novos.append(nome)

    manifesto.dados["dependencies"] = deps
    if salvar:
        _escrever_dependencias(manifesto, deps)

    print(color(f"Instalando em {pk.PASTA_MODULOS}/", "1;36"))
    _sincronizar(manifesto, offline=offline)
    print(color(f"\n✓ {', '.join(novos)} adicionado(s) ao forge.toml", "1;32"))


def remove_command(alvos):
    """dataforge remove <pacote> — desinstala e tira do forge.toml."""
    from . import packages as pk
    import shutil

    if not alvos:
        print(color("Erro: informe o pacote a remover.", "1;31"))
        sys.exit(1)

    manifesto = _manifesto_ou_sair()
    deps = dict(manifesto.dependencies)
    lock = pk.Lock(manifesto.raiz)
    removidos = []

    for nome in alvos:
        if nome not in deps:
            print(color(f"  '{nome}' nao esta no forge.toml", "1;33"))
            continue
        deps.pop(nome)
        lock.esquecer(nome)
        pasta = os.path.join(manifesto.raiz, pk.PASTA_MODULOS, nome)
        if os.path.isdir(pasta):
            shutil.rmtree(pasta)
        removidos.append(nome)
        print(color(f"  - {nome}", "1;31"))

    if not removidos:
        return
    _escrever_dependencias(manifesto, deps)
    lock.gravar()
    print(color(f"\n✓ {', '.join(removidos)} removido(s)", "1;32"))


def install_command(offline=False, conferir=False):
    """dataforge install — instala tudo o que o forge.toml declara."""
    manifesto = _manifesto_ou_sair()
    if conferir:
        print(color("Plano de instalacao:", "1;36"))
        _sincronizar(manifesto, offline=offline, so_conferir=True)
        return
    print(color(f"Instalando as dependencias de {manifesto.name or 'seu projeto'}",
                "1;36"))
    instalados = _sincronizar(manifesto, offline=offline)
    if instalados:
        print(color(f"\n✓ {len(instalados)} pacote(s) prontos", "1;32"))


def list_command():
    """dataforge list — o que esta instalado agora."""
    from . import packages as pk

    manifesto = _manifesto_ou_sair()
    lock = pk.Lock(manifesto.raiz)
    pasta = os.path.join(manifesto.raiz, pk.PASTA_MODULOS)

    if not lock.pacotes:
        print(color("Nenhum pacote instalado.", "1;33"))
        print("  dataforge add <pacote>")
        return

    diretas = set(manifesto.dependencies)
    print(color(f"{manifesto.name or 'projeto'} {manifesto.version}", "1;36"))
    for nome, info in sorted(lock.pacotes.items()):
        presente = os.path.isdir(os.path.join(pasta, nome))
        marca = color("✓", "1;32") if presente else color("✗", "1;31")
        tipo = "" if nome in diretas else color("  (transitiva)", "0;90")
        fonte = color(f"  {info['fonte']}", "0;90") if info["fonte"] != "registro" else ""
        print(f"  {marca} {nome}@{info['versao']}{tipo}{fonte}")

    faltando = [n for n in lock.pacotes
                if not os.path.isdir(os.path.join(pasta, n))]
    if faltando:
        print(color(f"\n{len(faltando)} no lock mas nao em disco — "
                    f"rode 'dataforge install'", "1;33"))


def search_command(termo, offline=False):
    """dataforge search <termo> — procura no registro."""
    from . import packages as pk

    if not termo:
        print(color("Erro: informe o que procurar.", "1;31"))
        sys.exit(1)

    registro = pk.Registro(offline=offline)
    try:
        achados = registro.buscar(termo)
    except pk.ErroPacote as e:
        print(color(f"✗ {e}", "1;31"))
        sys.exit(1)

    if not achados:
        print(color(f"Nada encontrado para '{termo}'.", "1;33"))
        total = len(registro.pacotes())
        print(f"  O registro tem {total} pacote(s). "
              f"Veja todos com: dataforge search ''")
        return

    print(color(f"{len(achados)} resultado(s) para '{termo}':\n", "1;36"))
    for nome, info in achados:
        versoes = sorted(info.get("versoes", {}), key=pk.Versao)
        ultima = versoes[-1] if versoes else "?"
        print(color(f"  {nome}", "1;37") + color(f"  {ultima}", "0;90"))
        if info.get("descricao"):
            print(f"    {info['descricao']}")
        if info.get("tags"):
            print(color(f"    {' '.join('#' + t for t in info['tags'])}", "0;90"))
        print()
    print(color("  dataforge add <nome>", "0;90"))


def pack_command():
    """dataforge pack — gera o tarball publicavel deste projeto."""
    from . import packages as pk

    try:
        caminho, sha, nome, versao = pk.empacotar(".")
    except pk.ErroPacote as e:
        print(color(f"✗ {e}", "1;31"))
        sys.exit(1)

    tamanho = os.path.getsize(caminho)
    print(color(f"✓ {nome} {versao}", "1;32"))
    print(f"  arquivo  {_curto(caminho)}")
    print(f"  tamanho  {tamanho / 1024:.1f} KB")
    print(f"  sha256   {sha}")
    print()
    print(color("Para publicar no registro, veja: dataforge publish --help", "0;90"))


def publish_command(destino=None):
    """dataforge publish — empacota e registra num indice local.

    O registro oficial e um indice estatico. 'publish' prepara o tarball e
    atualiza um index.json — apontando --registry para o clone do registro,
    o fluxo e: publish, conferir o diff, abrir um PR.
    """
    from . import packages as pk
    import json as _json
    import shutil as _shutil

    if destino is None:
        destino = os.environ.get("DATAFORGE_REGISTRY_DIR")
    if not destino:
        print(color("Erro: informe a pasta do registro.", "1;31"))
        print("  dataforge publish --registry=/caminho/do/registro")
        print("  ou defina DATAFORGE_REGISTRY_DIR")
        print()
        print("  O registro e uma pasta com index.json e pacotes/.")
        print("  Publicar = acrescentar seu tarball e abrir um PR.")
        sys.exit(1)

    try:
        caminho, sha, nome, versao = pk.empacotar(".")
    except pk.ErroPacote as e:
        print(color(f"✗ {e}", "1;31"))
        sys.exit(1)

    from . import project as proj
    manifesto = proj.carregar(".")
    secao = manifesto.dados.get("package") or manifesto.dados.get("project") or {}

    pasta_pacotes = os.path.join(destino, "pacotes")
    os.makedirs(pasta_pacotes, exist_ok=True)
    _shutil.copy2(caminho, os.path.join(pasta_pacotes, os.path.basename(caminho)))

    indice_path = os.path.join(destino, "index.json")
    if os.path.exists(indice_path):
        with open(indice_path, encoding="utf-8") as f:
            indice = _json.load(f)
    else:
        indice = {"registro": "dataforge", "pacotes": {}}

    pacote = indice.setdefault("pacotes", {}).setdefault(nome, {})
    pacote["descricao"] = secao.get("description", "")
    pacote["licenca"] = secao.get("license", "")
    pacote["autores"] = secao.get("authors", [])
    pacote.setdefault("tags", secao.get("keywords", []))
    if str(versao) in pacote.setdefault("versoes", {}):
        print(color(f"✗ {nome} {versao} ja existe no registro. "
                    f"Suba a versao no forge.toml.", "1;31"))
        sys.exit(1)
    pacote["versoes"][str(versao)] = {
        "arquivo": os.path.basename(caminho),
        "sha256": sha,
        "dependencias": manifesto.dependencies,
        "dataforge": secao.get("dataforge", ""),
    }

    with open(indice_path, "w", encoding="utf-8") as f:
        _json.dump(indice, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(color(f"✓ {nome} {versao} publicado em {destino}", "1;32"))
    print(f"  pacotes/{os.path.basename(caminho)}")
    print(f"  index.json atualizado")


# ─── Project Templates ──────────────────────────────────────────

PROJECT_TEMPLATES = {
    "cli": {
        "name": "CLI Tool",
        "description": "Ferramenta de linha de comando com acoes, constantes e cores",
        "icon": "⚡",
        "files": {
            "main.df": '''// {name} — ferramenta de linha de comando
// Criado com DataForge v{version}

adopt Arcane.Text as Text

steady APP_NAME := "{name}"
steady VERSION := "1.0.0"

action cabecalho():
    out Text.box(APP_NAME + " v" + VERSION)

action ajuda():
    out "Uso: dataforge run main.df"
    out ""
    out "Comandos disponiveis:"
    cmds := [
        ["ajuda", "mostra esta tela"],
        ["versao", "mostra a versao"],
        ["saudar", "saudacao personalizada"]
    ]
    cycle c in cmds:
        out "  " + c[0].pad_end(12) + c[1]

action saudar(nome: String) -> String:
    yield "Ola, " + nome + "! Bem-vindo ao " + APP_NAME + "."

cabecalho()
ajuda()
out ""
out saudar("Desenvolvedor")
''',
            "README.md": '''# {name}

Ferramenta CLI criada com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```
''',
        }
    },
    "data": {
        "name": "Data Analytics",
        "description": "Analise de dados com estatistica, pipelines e relatorio",
        "icon": "📊",
        "files": {
            "main.df": '''// {name} — analise de dados
// Criado com DataForge v{version}

adopt Arcane.Math as Math
adopt Arcane.Analytics as Analytics

steady TITULO := "{name}"

dados := [
    {{"nome": "Alice", "idade": 28, "salario": 5500}},
    {{"nome": "Bruno", "idade": 34, "salario": 7200}},
    {{"nome": "Carla", "idade": 25, "salario": 4800}},
    {{"nome": "Diego", "idade": 41, "salario": 9100}},
    {{"nome": "Elena", "idade": 30, "salario": 6300}}
]

salarios := dados >> morph d: d["salario"]

action moeda(valor) -> String:
    yield "R$ " + str(round(valor, 2))

out "=== " + TITULO + " ==="
out "Registros:      " + str(len(dados))
out "Media salarial: " + moeda(Math.mean(salarios))
out "Mediana:        " + moeda(Math.median(salarios))
out "Minimo:         " + moeda(min(salarios))
out "Maximo:         " + moeda(max(salarios))
out "Desvio padrao:  " + moeda(Math.stdev(salarios))

out ""
out "=== Acima de R$ 6.000 ==="
altos := dados >> sift d: d["salario"] bigger 6000
cycle p in altos:
    out "  " + p["nome"] + ": " + moeda(p["salario"])

out ""
out "=== Com bonus de 15% ==="
com_bonus := dados >> morph d: {{
    "nome": d["nome"],
    "total": round(d["salario"] * 1.15, 2)
}}
cycle p in com_bonus:
    out "  " + p["nome"] + ": " + moeda(p["total"])

out ""
out "=== Folha total ==="
folha := salarios >> distill acc, v: acc + v 0
out "  " + moeda(folha)
''',
            "README.md": '''# {name}

Projeto de **analise de dados** criado com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## O que faz

- Estatistica descritiva (media, mediana, desvio padrao)
- Filtragem e transformacao com pipelines `>> sift` / `>> morph` / `>> distill`
- Relatorio formatado no terminal
''',
        }
    },
    "oop": {
        "name": "Orientado a Objetos",
        "description": "Blueprints, heranca, traits e polimorfismo",
        "icon": "🧩",
        "files": {
            "main.df": '''// {name} — modelagem com blueprints
// Criado com DataForge v{version}

trait Descritivel:
    action descrever()

blueprint Conta(titular, saldo) with Descritivel:
    action depositar(valor: Number):
        given valor smaller_eq 0:
            trigger "Valor de deposito invalido"
        self.saldo := self.saldo + valor
        yield self.saldo

    action sacar(valor: Number):
        guard valor smaller_eq self.saldo, "Saldo insuficiente"
        self.saldo := self.saldo - valor
        yield self.saldo

    action descrever() -> String:
        yield self.titular + ": R$ " + str(round(self.saldo, 2))

blueprint ContaPoupanca(titular, saldo, taxa) extends Conta:
    action render():
        juros := self.saldo * self.taxa
        self.saldo := self.saldo + juros
        yield juros

    action descrever() -> String:
        yield "[poupanca] " + root.descrever()

contas := [
    spawn Conta("Alice", 1000),
    spawn ContaPoupanca("Bruno", 2000, 0.05)
]

cycle c in contas:
    c.depositar(500)
    out c.descrever()

poupanca := contas[1]
out "Juros creditados: R$ " + str(round(poupanca.render(), 2))
out poupanca.descrever()

monitor:
    conta := contas[0]
    conta.sacar(999999)
handle e:
    out "Erro tratado: " + e
''',
            "README.md": '''# {name}

Projeto **orientado a objetos** criado com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Conceitos usados

- `trait` (interface) e `with` para compor
- `blueprint` com parametros de construtor
- `extends` para heranca e `root` para chamar o pai
- `guard` / `trigger` / `monitor` / `handle` para erros
''',
        }
    },
    "test": {
        "name": "Suite de Testes",
        "description": "Codigo + testes automatizados com Arcane.Test",
        "icon": "🧪",
        "files": {
            "lib.df": '''// {name} — funcoes sob teste

action somar(a: Number, b: Number) -> Number:
    yield a + b

action fatorial(n: Integer) -> Integer:
    given n smaller 0:
        trigger "fatorial exige n >= 0"
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

action eh_primo(n: Integer) -> Boolean:
    given n smaller 2:
        yield no
    i := 2
    persist i * i smaller_eq n:
        given n % i is 0:
            yield no
        i += 1
    yield yes

relay somar, fatorial, eh_primo
''',
            "tests.df": '''// {name} — testes
// Executar: dataforge run tests.df

adopt lib
adopt Arcane.Test as Test

total := 0
falhas := 0

action checar(nome: String, obtido, esperado):
    total += 1
    given obtido is esperado:
        out "  ok   " + nome
    otherwise:
        falhas += 1
        out "  FALHA " + nome + " -> esperado " + str(esperado) + ", obtido " + str(obtido)

out "=== {name} ==="
checar("somar(2, 3)", lib.somar(2, 3), 5)
checar("somar(-1, 1)", lib.somar(-1, 1), 0)
checar("fatorial(0)", lib.fatorial(0), 1)
checar("fatorial(5)", lib.fatorial(5), 120)
checar("eh_primo(7)", lib.eh_primo(7), yes)
checar("eh_primo(9)", lib.eh_primo(9), no)

monitor:
    lib.fatorial(-1)
    checar("fatorial(-1) dispara erro", no, yes)
handle e:
    checar("fatorial(-1) dispara erro", yes, yes)

out ""
out "Total: " + str(total) + " | falhas: " + str(falhas)
assert falhas is 0, "a suite tem falhas"
out "Suite verde."
''',
            "README.md": '''# {name}

Projeto com **suite de testes** criado com **DataForge** v{version}.

## Executar

```bash
dataforge run tests.df
```

`lib.df` guarda as funcoes e exporta com `relay`; `tests.df` importa com
`adopt lib` e verifica cada caso.
''',
        }
    },
    "api": {
        "name": "API REST",
        "description": "Servidor HTTP com rotas REST e JSON (Arcane.Http)",
        "icon": "🌐",
        "files": {
            "main.df": '''// {name} — API REST
// Criado com DataForge v{version}
// Executar: dataforge run main.df  (Ctrl+C para parar)

adopt Arcane.Http as Http

steady PORTA := 3000

app := Http.create("{name}")
Http.cors(app)
Http.logger(app)

itens := [
    {{"id": 1, "nome": "Primeiro item", "status": "ativo"}}
]
proximo_id := 2

action listar(req, res):
    res.json(itens)

action buscar(req, res):
    id := int(req["params"]["id"])
    achados := itens >> sift i: i["id"] is id
    given len(achados) is 0:
        res.json({{"erro": "Item nao encontrado"}}, 404)
    otherwise:
        res.json(achados[0])

action criar(req, res):
    corpo := req["json"]
    item := {{
        "id": proximo_id,
        "nome": corpo["nome"],
        "status": "ativo"
    }}
    proximo_id += 1
    itens.append(item)
    res.json(item, 201)

action remover(req, res):
    id := int(req["params"]["id"])
    itens := itens >> sift i: i["id"] isnt id
    res.json({{"mensagem": "Item removido"}})

Http.get(app, "/api/itens", listar)
Http.get(app, "/api/itens/:id", buscar)
Http.post(app, "/api/itens", criar)
Http.delete(app, "/api/itens/:id", remover)

out "{name} escutando em http://localhost:" + str(PORTA)
Http.listen(app, PORTA)
''',
            "README.md": '''# {name}

API REST criada com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | /api/itens | Lista todos |
| GET | /api/itens/:id | Busca por id |
| POST | /api/itens | Cria item |
| DELETE | /api/itens/:id | Remove item |

Servidor em `http://localhost:3000`.
''',
            "config.df": '''// Configuracoes do projeto
steady API_PORT := 3000
steady API_HOST := "0.0.0.0"
steady API_NAME := "{name}"
steady VERSION := "1.0.0"

relay API_PORT, API_HOST, API_NAME, VERSION
''',
        }
    },
    "web": {
        "name": "Web App",
        "description": "Servidor HTTP com pagina HTML e arquivos estaticos",
        "icon": "🖥️",
        "files": {
            "main.df": '''// {name} — aplicacao web
// Criado com DataForge v{version}

adopt Arcane.Http as Http

steady PORTA := 3000

app := Http.create("{name}")
Http.cors(app)
Http.logger(app)
Http.static(app, "./public")

action home(req, res):
    html := "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
    html += "<title>{name}</title>"
    html += "<style>body{{font-family:system-ui;max-width:720px;margin:60px auto;padding:0 20px}}</style>"
    html += "</head><body>"
    html += "<h1>{name}</h1>"
    html += "<p>Servidor DataForge no ar.</p>"
    html += "<p><a href='/api/status'>Ver status da API</a></p>"
    html += "</body></html>"
    res.html(html)

action status(req, res):
    res.json({{
        "status": "online",
        "app": "{name}",
        "versao": "1.0.0"
    }})

Http.get(app, "/", home)
Http.get(app, "/api/status", status)

out "{name} escutando em http://localhost:" + str(PORTA)
Http.listen(app, PORTA)
''',
            "README.md": '''# {name}

Aplicacao web criada com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Estrutura

- `main.df` — servidor
- `public/` — arquivos estaticos
''',
            "public/index.html": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
</head>
<body>
    <h1>{name}</h1>
    <p>Arquivo estatico servido por DataForge.</p>
</body>
</html>
''',
        }
    },
}


def api_command(args, flags=()):
    """dataforge api — exporta a API de um servidor Kiln.

        dataforge api src/app.df                  a tabela de rotas
        dataforge api src/app.df --openapi        OpenAPI 3.1
        dataforge api src/app.df --insomnia -o=x.json

    O arquivo e EXECUTADO para que as rotas se registrem — e assim que
    um servidor Kiln se declara. Por isso ele precisa ser o modulo que
    monta ('app.df'), e nao o que sobe ('main.df'): o segundo chamaria
    'ignite' e nunca voltaria.
    """
    from .marca import cor as _cor
    from .stdlib import get_module

    if not args:
        print(_cor("Erro: informe o arquivo que monta o servidor.", "1;31"))
        print(_cor("      dataforge api src/app.df --openapi", "0;90"))
        return 1

    caminho = args[0]
    if not os.path.isfile(caminho):
        print(_cor(f"Erro: '{caminho}' nao existe.", "1;31"))
        return 1

    formatos = {
        "--openapi": "openapi", "--swagger": "openapi",
        "--insomnia": "insomnia",
        "--postman": "postman",
        "--curl": "curl",
        "--markdown": "markdown", "--md": "markdown",
    }
    formato = "markdown"
    for flag in flags:
        if flag in formatos:
            formato = formatos[flag]

    saida = None
    for flag in flags:
        for prefixo in ("--saida=", "--out=", "-o="):
            if flag.startswith(prefixo):
                saida = flag[len(prefixo):]

    # ── executar para que as rotas se registrem ──
    fonte, motivo = _ler(caminho)
    if motivo:
        print(_cor(f"Erro: {motivo}", "1;31"))
        return 1

    interp = Interpreter()
    try:
        import io as _io
        from contextlib import redirect_stdout
        with redirect_stdout(_io.StringIO()):
            interp.run(parse(tokenize(fonte, caminho), caminho), caminho)
    except DataForgeError as erro:
        print(_cor(f"Erro ao carregar '{_curto(caminho)}':", "1;31"))
        print(erro.format(caminho, color=True) if hasattr(erro, "format")
              else str(erro))
        return 1

    # ── achar o servidor ──
    servidores = [(nome, valor)
                  for nome, valor in interp.global_env.variables.items()
                  if hasattr(valor, "rotas")]
    if not servidores:
        print(_cor(f"Nenhum servidor Kiln em '{_curto(caminho)}'.", "1;33"))
        print()
        print(_cor("  Um servidor se declara assim:", "0;90"))
        print(_cor("      adopt Kiln", "1;36"))
        print(_cor("      server API on 8080:", "1;36"))
        print(_cor('          route GET "/":', "1;36"))
        print(_cor('              respond json {}', "1;36"))
        print()
        print(_cor("  Se o arquivo chama 'ignite', aponte para o que MONTA",
                   "0;90"))
        print(_cor("  (app.df), e nao para o que sobe (main.df).", "0;90"))
        return 1

    nome_servidor, app = servidores[0]
    if len(servidores) > 1:
        print(_cor(f"  ({len(servidores)} servidores; usando "
                   f"'{nome_servidor}')", "0;90"))

    api = get_module("Arcane.API")
    config = {"titulo": f"API de {os.path.basename(caminho)}"}
    texto = api[formato](app, config)

    if saida:
        with open(saida, "w", encoding="utf-8") as f:
            f.write(texto if texto.endswith("\n") else texto + "\n")
        rotas = len(api["rotas"](app))
        print(_cor(f"  ✓ {rotas} rota(s) em {formato} → "
                   f"{_curto(saida)}", "1;32"))
        if formato == "insomnia":
            print(_cor("    Insomnia → Import → From File", "0;90"))
        elif formato == "openapi":
            print(_cor("    abra em editor.swagger.io, ou gere um cliente",
                       "0;90"))
        return 0

    print(texto)
    return 0


def converter_command(args, flags=()):
    """dataforge converter — Python vira DataForge.

        dataforge converter app.py            grava app.df ao lado
        dataforge converter src/              a pasta inteira
        dataforge converter app.py --saida=x.df
        dataforge converter src/ --seco       mostra sem gravar

    Traduz com o 'ast' do Python, e nao com expressao regular. O que nao
    tem equivalente honesto vira um 'TODO(converter)' com o codigo
    original ao lado — um conversor que erra em silencio e pior que um
    que aponta onde errou.
    """
    from .marca import cor as _cor
    from .migrar import converter_fonte

    if not args:
        print(_cor("Erro: informe o arquivo ou a pasta.", "1;31"))
        print(_cor("      dataforge converter app.py", "0;90"))
        print(_cor("      dataforge converter src/", "0;90"))
        return 1

    seco = "--seco" in flags or "--dry-run" in flags
    forcar = "--forcar" in flags or "--force" in flags
    saida_pedida = None
    for flag in flags:
        for prefixo in ("--saida=", "--out=", "-o="):
            if flag.startswith(prefixo):
                saida_pedida = flag[len(prefixo):]

    # ── o que converter ──
    alvos = []
    for alvo in args:
        if os.path.isdir(alvo):
            for raiz, pastas, arquivos in os.walk(alvo):
                pastas[:] = [p for p in pastas
                             if p not in ("__pycache__", ".git", ".venv",
                                          "node_modules", "venv", "build",
                                          "dist", ".tox", ".mypy_cache")]
                alvos += [os.path.join(raiz, a) for a in sorted(arquivos)
                          if a.endswith(".py")]
        elif os.path.isfile(alvo):
            alvos.append(alvo)
        else:
            print(_cor(f"Erro: '{alvo}' nao existe.", "1;31"))
            return 1

    if not alvos:
        print(_cor("Nenhum arquivo .py encontrado.", "1;33"))
        return 1

    if saida_pedida and len(alvos) > 1:
        print(_cor("Erro: '--saida' vale para UM arquivo.", "1;31"))
        print(_cor("      Numa pasta, cada .py vira o .df ao lado.", "0;90"))
        return 1

    print()
    print(_cor(f"  convertendo {len(alvos)} arquivo(s)", "1;37"))
    print()

    convertidos = 0
    total_pendencias = 0
    problemas = []

    for caminho in alvos:
        curto_nome = _curto(caminho)
        try:
            with open(caminho, encoding="utf-8") as f:
                fonte = f.read()
        except (OSError, UnicodeDecodeError) as erro:
            problemas.append((curto_nome, f"nao deu para ler: {erro}"))
            print(f"  {_cor('✗', '1;31')} {curto_nome}")
            continue

        try:
            texto, pendencias = converter_fonte(fonte, caminho)
        except SyntaxError as erro:
            # Traduzir Python quebrado produziria lixo com aparencia de
            # traducao. Melhor recusar e dizer onde.
            problemas.append(
                (curto_nome, f"Python invalido na linha {erro.lineno}: "
                             f"{erro.msg}"))
            print(f"  {_cor('✗', '1;31')} {curto_nome}  "
                  f"{_cor(f'linha {erro.lineno}: {erro.msg}', '0;90')}")
            continue

        destino = saida_pedida or (os.path.splitext(caminho)[0] + ".df")

        if seco:
            print(_cor(f"  ── {curto_nome} → {_curto(destino)} ──", "1;36"))
            print(texto)
            convertidos += 1
            total_pendencias += len(pendencias)
            continue

        if os.path.exists(destino) and not forcar:
            problemas.append((curto_nome,
                              f"'{_curto(destino)}' ja existe (use --forcar)"))
            print(f"  {_cor('•', '1;33')} {curto_nome}  "
                  f"{_cor('ja existe, pulado', '0;90')}")
            continue

        with open(destino, "w", encoding="utf-8") as f:
            f.write(texto)

        convertidos += 1
        total_pendencias += len(pendencias)
        marca_linha = (_cor(f"{len(pendencias)} a revisar", "1;33")
                       if pendencias else _cor("pronto", "1;32"))
        print(f"  {_cor('✓', '1;32')} {curto_nome} → "
              f"{_cor(_curto(destino), '1;37')}  {marca_linha}")

    # ── o relatorio, que e onde a honestidade aparece ──
    print()
    if problemas:
        print(_cor(f"  {len(problemas)} arquivo(s) nao converteram:", "1;31"))
        for nome, motivo in problemas[:10]:
            print(f"    {nome}: {_cor(motivo, '0;90')}")
        print()

    if convertidos:
        print(_cor(f"  {convertidos} arquivo(s) convertido(s).", "1;32"))
    if total_pendencias:
        print(_cor(f"  {total_pendencias} ponto(s) precisam de voce — "
                   f"procure por 'TODO(converter)'.", "1;33"))
        print()
        print(_cor("  A traducao nunca e completa: Python tem construcoes",
                   "0;90"))
        print(_cor("  que esta linguagem nao tem, e adivinhar seria pior.",
                   "0;90"))
    elif convertidos:
        print(_cor("  Nada ficou pendente.", "0;90"))

    if convertidos and not seco:
        print()
        print(_cor("  Confira antes de confiar:", "1;37"))
        print(_cor("    dataforge check .", "1;36"))
        print(_cor("    dataforge fmt .", "1;36"))
    print()
    return 1 if problemas else 0


def _tem_alguem_para_responder():
    """Da para abrir um prompt e esperar resposta?

    'isatty' e a pergunta certa e nao e confiavel sozinha: no Windows o
    pytest entrega um stdin que se apresenta como terminal e devolve EOF
    na primeira leitura. Por isso quem chama esta funcao tambem trata o
    EOF do 'input' como "nao havia ninguem".
    """
    try:
        return bool(sys.stdin) and sys.stdin.isatty()
    except (ValueError, AttributeError, OSError):
        return False


def _falta_o_modelo(chaves):
    """A recusa de 'new' sem modelo, dita uma vez so.

    Ela precisa NOMEAR os modelos: "falta dizer o modelo" manda a pessoa
    adivinhar qual e a lista.
    """
    from .marca import cor as _cor

    print(_cor("  ✗ falta dizer o modelo.", "1;31"))
    print(_cor(f"    dataforge new <nome> --modelo=<{'|'.join(chaves)}>",
               "0;90"))
    return 1


def new_project(args=None, flags=()):
    """dataforge new — cria um projeto, com apresentacao.

        dataforge new                 escolhe o modelo na tela
        dataforge new api             usa o modelo, pergunta o nome
        dataforge new api minha-api   direto ao ponto

    A animacao nao e enfeite: 'new' e a primeira coisa que alguem faz
    com a linguagem, e a impressao dessa etapa fica.
    """
    from .marca import cor as _cor
    from .modelos import MODELOS
    from .scaffold import Girador, abertura, apresentar, criar_projeto

    args = list(args or [])
    chaves = list(MODELOS)

    # ── so a lista, para quem le por programa ──
    # O editor precisa dos modelos sem entrar no modo interativo: sem
    # isto, a extensao teria a propria lista, e ela envelheceria no dia
    # em que um modelo novo fosse acrescentado aqui.
    if "--listar" in flags or "--list" in flags:
        if "--json" in flags:
            import json as _json
            print(_json.dumps(
                [{"nome": c, "titulo": MODELOS[c]["name"],
                  "descricao": MODELOS[c]["description"]} for c in chaves],
                ensure_ascii=False, indent=2))
        else:
            for chave in chaves:
                print(f"  {chave:<10}  {MODELOS[chave]['description']}")
        return

    # ── qual modelo ──
    #
    # Duas formas, e as duas precisam funcionar:
    #
    #     dataforge new api minha-api        posicional, para quem digita
    #     dataforge new minha-api --modelo=api   nomeada, para quem chama
    #
    # A segunda e a que a extensao do VS Code usa, e ela era IGNORADA: a
    # CLI caia no menu interativo, o editor nao tem um terminal para
    # responder, e o projeto nunca era criado. A mensagem que o usuario
    # via — "Rode no terminal para ver o erro" — mandava rodar
    # exatamente o comando que nao funcionava.
    escolhido = args[0] if args and args[0] in MODELOS else None

    pedido = None
    for flag in flags:
        for prefixo in ("--modelo=", "--template=", "-m="):
            if flag.startswith(prefixo):
                pedido = flag[len(prefixo):].strip()
    if pedido:
        if pedido not in MODELOS:
            import difflib
            perto = difflib.get_close_matches(pedido, chaves, n=1, cutoff=0.6)
            print(_cor(f"  ✗ '{pedido}' não é um modelo.", "1;31"))
            if perto:
                print(_cor(f"    Você quis dizer '{perto[0]}'?", "0;90"))
            print(_cor(f"    Os modelos: {', '.join(chaves)}", "0;90"))
            return 1
        escolhido = pedido
        # Com '--modelo=', o primeiro posicional e o NOME do projeto.
        if args and args[0] == pedido:
            args = args[1:]

    # ── nao perguntar nada quando ja se sabe tudo ──
    #
    # Quem chama por programa — o editor, um script, o CI — nao tem
    # ninguem para responder um prompt. '--silencioso' garante isso
    # mesmo quando falta informacao: ai o certo e falhar dizendo o que
    # falta, e nao esperar para sempre por uma resposta.
    silencioso = ("--silencioso" in flags or "--quiet" in flags
                  or "-q" in flags or not _tem_alguem_para_responder())

    abertura("criando um projeto")

    if not escolhido and silencioso:
        return _falta_o_modelo(chaves)

    if not escolhido:
        print(_cor("  Que tipo de projeto?", "1;37"))
        print()
        for i, chave in enumerate(chaves, 1):
            modelo = MODELOS[chave]
            print(f"  {_cor(f'{i}.', '1;33')} {modelo['icon']}  "
                  f"{_cor(modelo['name'], '1;37')}  "
                  f"{_cor(chave, '0;90')}")
            print(f"      {_cor(modelo['description'], '0;90')}")
        print()
        try:
            resposta = input(_cor(f"  › número ou nome (1-{len(chaves)}): ",
                                  "1;32")).strip()
        except KeyboardInterrupt:
            print(_cor("\n  cancelado.", "0;90"))
            return 1
        except (EOFError, OSError):
            # Nao havia ninguem do outro lado. 'isatty' ja deveria ter
            # dito isso, e no Windows nem sempre diz — o pytest de la
            # entrega um stdin que se apresenta como terminal e devolve
            # EOF na primeira leitura.
            #
            # Chegar ate aqui e a prova definitiva, e a resposta e a
            # mesma: dizer o que falta, em vez de "cancelado", que nao
            # ajuda quem chamou por programa.
            print()
            return _falta_o_modelo(chaves)

        if resposta in MODELOS:
            escolhido = resposta
        else:
            try:
                indice = int(resposta) - 1
                if not 0 <= indice < len(chaves):
                    raise ValueError
                escolhido = chaves[indice]
            except ValueError:
                print(_cor(f"  ✗ '{resposta}' não é um modelo. "
                           f"Use um número de 1 a {len(chaves)}, "
                           f"ou o nome ({', '.join(chaves)}).", "1;31"))
                return 1

    modelo = MODELOS[escolhido]

    # ── qual nome ──
    nome = args[1] if len(args) > 1 else (
        args[0] if args and args[0] not in MODELOS else None)
    if not nome:
        padrao = "meu-" + escolhido
        if silencioso:
            nome = padrao
        else:
            try:
                nome = input(_cor(f"  › nome do projeto ({padrao}): ",
                                  "1;32")).strip() or padrao
            except KeyboardInterrupt:
                print(_cor("\n  cancelado.", "0;90"))
                return 1
            except (EOFError, OSError):
                nome = padrao        # sem ninguem para responder

    pasta = "".join(c for c in nome.replace(" ", "-").lower()
                    if c.isalnum() or c in "-_")
    if not pasta:
        print(_cor("  ✗ nome vazio depois de limpo. Use letras e números.",
                   "1;31"))
        return 1

    if os.path.exists(pasta):
        print()
        print(_cor(f"  ✗ a pasta '{pasta}' já existe.", "1;31"))
        print(_cor("      Escolha outro nome, ou apague a pasta antes.",
                   "0;90"))
        return 1

    # ── criar ──
    print()
    with Girador(f"criando {pasta}") as g:
        criados = criar_projeto(pasta, modelo, pasta, __version__)
        g.ok(f"{len(criados)} arquivo(s) criados")

    with Girador("conferindo a sintaxe") as g:
        # Um modelo que nao compila e pior que nenhum: quem acabou de
        # criar o projeto acha que errou alguma coisa.
        from .lexer import tokenize
        from .parser import parse
        problemas = []
        for relativo in criados:
            if not relativo.endswith(".df"):
                continue
            caminho = os.path.join(pasta, relativo)
            try:
                parse(tokenize(open(caminho, encoding="utf-8").read()),
                      caminho)
            except DataForgeError as erro:
                problemas.append((relativo, erro.message))
        if problemas:
            g.__exit__()
            print(f"  {_cor('✗', '1;31')} o modelo tem erro de sintaxe:")
            for arquivo, motivo in problemas:
                print(f"      {arquivo}: {motivo}")
            print(_cor("      Isto é um bug do DataForge — por favor "
                       "reporte.", "0;90"))
            return 1
        g.ok("sintaxe conferida")

    apresentar(pasta, modelo, criados, pasta)
    return 0


def list_templates():
    """dataforge new --list — so os modelos, sem perguntar nada."""
    from .marca import cor as _cor
    from .modelos import MODELOS

    print()
    print(_cor("  Modelos de projeto", "1;37"))
    print()
    for chave, modelo in MODELOS.items():
        print(f"  {modelo['icon']}  {_cor(chave.ljust(8), '1;33')} "
              f"{_cor(modelo['name'], '1;37')}")
        print(f"      {_cor(modelo['description'], '0;90')}")
        print(f"      {_cor(f'dataforge new {chave} <nome>', '0;36')}")
        print()
    return 0


def fmt_command(alvos, checar=False):
    """dataforge fmt — formata arquivos .df."""
    from .formatter import format_source

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        return

    alterados, com_erro = [], []
    for caminho in arquivos:
        original, motivo = _ler(caminho)
        if motivo:
            com_erro.append((caminho, motivo))
            continue
        try:
            formatado = format_source(original)
        except DataForgeError as e:
            com_erro.append((caminho, e.message))
            continue
        if formatado != original:
            alterados.append(caminho)
            if not checar:
                open(caminho, 'w', encoding='utf-8').write(formatado)

    for caminho, mensagem in com_erro:
        print(color(f"✗ {caminho}: {mensagem}", "1;31"))

    if checar:
        for caminho in alterados:
            print(color(f"  precisa formatar  {caminho}", "1;33"))
        if alterados or com_erro:
            print(color(f"\n{len(alterados)} arquivo(s) fora do formato, "
                        f"{len(com_erro)} com erro", "1;33"))
            sys.exit(1)
        print(color(f"✓ {len(arquivos)} arquivo(s) já formatados", "1;32"))
        return

    for caminho in alterados:
        print(color(f"  formatado  {caminho}", "1;36"))
    print(color(f"\n{len(alterados)} de {len(arquivos)} arquivo(s) reescritos",
                "1;32" if not com_erro else "1;33"))
    if com_erro:
        sys.exit(1)


def lint_command(alvos, strict=False):
    """dataforge lint — encontra problemas de estilo e higiene."""
    from .linter import REGRAS, lint_program
    from . import project as proj

    # [lint] ignore do forge.toml desliga regras que nao servem ao projeto
    manifesto = proj.carregar(alvos[0] if alvos else ".")
    ignorar = list(manifesto.lint_ignore) if manifesto else []
    desconhecidas = [r for r in ignorar if r not in REGRAS]
    if desconhecidas:
        print(color(f"Aviso: [lint] ignore cita regra(s) que nao existem: "
                    f"{', '.join(desconhecidas)}", "1;33"))
        print(color(f"  Regras validas: {', '.join(sorted(REGRAS))}", "0;90"))
    if manifesto and manifesto.lint_strict:
        strict = True

    arquivos = _expandir(alvos or ["."])
    usar_cor = '--no-color' not in sys.argv
    total = 0
    for caminho in arquivos:
        fonte, motivo = _ler(caminho)
        if motivo:
            print(color(f"\u2717 {caminho}: {motivo}", "1;31"))
            total += 1
            continue
        try:
            arvore = parse(tokenize(fonte, caminho), caminho)
        except DataForgeError as e:
            print(color(f"✗ {caminho}: {e.format()}", "1;31"))
            total += 1
            continue
        for d in lint_program(arvore, caminho, fonte, ignorar):
            print(d.format(caminho, color=usar_cor))
            total += 1

    if total:
        print(color(f"\n{total} aviso(s) em {len(arquivos)} arquivo(s)", "1;33"))
        if strict:
            sys.exit(1)
        return
    print(color(f"✓ {len(arquivos)} arquivo(s) sem avisos", "1;32"))


def test_command(alvos, verboso=False, filtro="", parar=False):
    """dataforge test — executa a suíte de testes."""
    from .testrunner import executar

    alvo = alvos[0] if alvos else "."
    _, ok = executar(alvo, verboso=verboso, filtro=filtro,
                     cor='--no-color' not in sys.argv, parar_no_primeiro=parar)
    if not ok:
        sys.exit(1)


def crucible_command(alvos, opcoes):
    """dataforge crucible — roda as suites do Crucible.

    Descobre os arquivos, executa cada um (o que registra as suites) e
    so entao roda tudo junto. A ordem importa: rodar durante a
    descoberta impediria '--aleatorio' de embaralhar entre arquivos, e
    'setup all' de uma suite espalhada em dois arquivos rodaria duas
    vezes.
    """
    from .stdlib.crucible import (REGISTRO, Executor, relatorio,
                                  relatorio_junit, relatorio_json,
                                  relatorio_tap)
    from .interpreter import Interpreter
    from .lexer import tokenize
    from .parser import parse

    if opcoes.get("matchers"):
        return _listar_matchers()

    arquivos = _expandir(alvos or ["."])
    arquivos = [a for a in arquivos
                if "_crucible" in os.path.basename(a)
                or "_test" in os.path.basename(a)
                or os.sep + "tests" + os.sep in a
                or os.sep + "testes" + os.sep in a] or arquivos

    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        sys.exit(1)

    REGISTRO.reiniciar()
    cor = "--no-color" not in sys.argv

    problemas = []
    for caminho in arquivos:
        fonte, motivo = _ler(caminho)
        if fonte is None:
            problemas.append((caminho, motivo))
            continue
        try:
            interpretador = Interpreter()
            interpretador.run(parse(tokenize(fonte, caminho), caminho), caminho)
        except SystemExit:
            raise
        except BaseException as e:          # noqa: BLE001
            problemas.append((caminho, f"{type(e).__name__}: {e}"))

    if problemas:
        print(color("\n  Arquivos que nao puderam ser carregados:", "1;31"))
        for caminho, motivo in problemas:
            print(f"    {_curto(caminho)}: {motivo}")
        print()

    if REGISTRO.raiz.total() == 0:
        print(color("Nenhuma suite encontrada.", "1;33"))
        print(color("  Uma suite comeca com:  crucible \"o que voce testa\":",
                    "0;90"))
        sys.exit(1)

    executor = Executor(
        semente=opcoes.get("semente"),
        aleatorio=bool(opcoes.get("aleatorio")),
        prazo_padrao=opcoes.get("prazo", 0),
        filtro=opcoes.get("filtro", ""),
        tags=opcoes.get("tags", ()),
        sem_tags=opcoes.get("sem_tags", ()),
        parar_na_primeira=bool(opcoes.get("parar")),
        repetir=opcoes.get("repetir", 1),
    )
    executor.rodar(REGISTRO.raiz)

    formato = opcoes.get("formato", "texto")
    if formato == "junit":
        saida = relatorio_junit(executor)
    elif formato == "json":
        saida = relatorio_json(executor)
    elif formato == "tap":
        saida = relatorio_tap(executor)
    else:
        saida = relatorio(executor, colorir=cor,
                          verboso=bool(opcoes.get("verboso")))

    destino = opcoes.get("saida", "")
    if destino:
        os.makedirs(os.path.dirname(destino) or ".", exist_ok=True)
        open(destino, "w", encoding="utf-8").write(saida)
        print(color(f"✓ relatorio escrito em {destino}", "1;32"))
    else:
        print(saida)

    if not executor.resumo()["verde"] or problemas:
        sys.exit(1)


def _listar_matchers():
    """dataforge crucible --matchers — o que se pode cobrar."""
    from .stdlib.crucible import Expectativa

    grupos = {
        "igualdade": ("to_be", "to_equal", "to_be_exactly", "to_be_close_to",
                      "to_be_between"),
        "verdade": ("to_be_true", "to_be_false", "to_be_truthy",
                    "to_be_falsy", "to_be_void", "to_exist", "to_be_empty"),
        "tipos": ("to_be_a", "to_be_number", "to_be_text", "to_be_cluster",
                  "to_be_vault", "to_be_action", "to_be_integer",
                  "to_be_float", "to_be_boolean", "to_be_instance_of"),
        "numeros": ("to_be_greater_than", "to_be_less_than", "to_be_at_least",
                    "to_be_at_most", "to_be_positive", "to_be_negative",
                    "to_be_zero", "to_be_even", "to_be_odd",
                    "to_be_divisible_by", "to_be_finite", "to_be_nan"),
        "texto": ("to_start_with", "to_end_with", "to_match", "to_be_blank",
                  "to_be_uppercase", "to_be_lowercase", "to_contain_text",
                  "to_have_lines"),
        "colecoes": ("to_contain", "to_contain_all", "to_contain_any",
                     "to_be_in", "to_have_length", "to_have_key",
                     "to_have_keys", "to_have_field", "to_be_sorted",
                     "to_be_unique", "to_all_satisfy", "to_any_satisfy",
                     "to_have_same_items"),
        "erros": ("to_raise", "to_not_raise"),
        "desempenho": ("to_finish_within",),
        "saida": ("to_print",),
    }
    print()
    total = sum(len(v) for v in grupos.values())
    print(f"  {color('MATCHERS DO CRUCIBLE', '1;37')}  "
          f"{color(f'{total} em {len(grupos)} grupos', '0;90')}")
    for nome, matchers in grupos.items():
        print()
        print(f"  {color(nome.upper(), '1;36')}")
        for m in matchers:
            doc = (getattr(Expectativa, m).__doc__ or "").strip().split("\n")[0]
            print(f"    {color(m, '1;33'):<34} {color(doc, '0;90')}")
    print()
    print(color("  Todo matcher aceita '.nao()' antes dele para inverter.",
                "0;90"))
    print()


def doc_command(alvos, saida=""):
    """dataforge doc — gera documentação Markdown."""
    from .docgen import gerar_doc, gerar_doc_pasta

    alvo = alvos[0] if alvos else "."
    if os.path.isdir(alvo):
        texto = gerar_doc_pasta(alvo, f"Documentação de {os.path.basename(os.path.abspath(alvo))}")
    else:
        texto = gerar_doc(alvo)

    if saida:
        os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
        open(saida, 'w', encoding='utf-8').write(texto)
        print(color(f"✓ documentação escrita em {saida}", "1;32"))
    else:
        print(texto)


def init_command(args):
    """dataforge init — cria o forge.toml e o esqueleto do projeto."""
    from . import project

    pasta = args[0] if args else "."
    existente = os.path.join(pasta, project.ARQUIVO)
    if os.path.exists(existente):
        print(color(f"✗ já existe um {project.ARQUIVO} em {pasta}", "1;31"))
        sys.exit(1)

    nome = os.path.basename(os.path.abspath(pasta)) or "meu-projeto"
    try:
        digitado = input(color(f"  nome do projeto ({nome}): ", "1;32")).strip()
        nome = digitado or nome
        descricao = input(color("  descrição: ", "1;32")).strip()
        autor = input(color("  autor: ", "1;32")).strip()
    except (EOFError, KeyboardInterrupt):
        descricao, autor = "", ""

    os.makedirs(os.path.join(pasta, "src"), exist_ok=True)
    os.makedirs(os.path.join(pasta, "tests"), exist_ok=True)

    principal = os.path.join(pasta, "src", "main.df")
    if not os.path.exists(principal):
        open(principal, 'w', encoding='utf-8').write(
            f'// {nome}\n\naction principal():\n'
            f'    out "Ola, {nome}!"\n\nprincipal()\n')

    teste = os.path.join(pasta, "tests", "principal_test.df")
    if not os.path.exists(teste):
        open(teste, 'w', encoding='utf-8').write(
            'action test_soma():\n    assert 1 + 1 is 2, "aritmetica basica"\n')

    caminho = project.criar(pasta, nome, descricao, autor,
                            entrada="src/main.df", versao=__version__)
    print()
    print(color(f"✓ projeto '{nome}' iniciado", "1;32"))
    for arquivo in (project.ARQUIVO, "src/main.df", "tests/principal_test.df"):
        print(color(f"    {arquivo}", "0;37"))
    print()
    print(color("  dataforge run src/main.df", "1;36"))
    print(color("  dataforge test tests/", "1;36"))


def info_command(args):
    """dataforge info — mostra o manifesto do projeto atual."""
    from . import project

    manifesto = project.carregar(args[0] if args else ".")
    if manifesto is None:
        print(color("Nenhum forge.toml encontrado aqui nem acima.", "1;33"))
        print("Crie um com: dataforge init")
        sys.exit(1)

    ok, exigido = manifesto.requires(__version__)
    print()
    print(color(f"  {manifesto.name} {manifesto.version}", "1;36"))
    descricao = manifesto.dados["project"].get("description", "")
    if descricao:
        print(f"  {descricao}")
    print()
    print(f"  manifesto  {_curto(manifesto.caminho)}")
    print(f"  entrada    {manifesto.entry}")
    autores = manifesto.dados["project"].get("authors") or []
    if autores:
        print(f"  autores    {', '.join(autores)}")
    licenca = manifesto.dados["project"].get("license", "")
    if licenca:
        print(f"  licença    {licenca}")
    if exigido:
        estado = color("ok", "1;32") if ok else color(
            f"incompatível (você tem {__version__})", "1;31")
        print(f"  requer     DataForge {exigido}  {estado}")
    if manifesto.dependencies:
        print()
        print(color("  dependências", "1;37"))
        for nome, versao in manifesto.dependencies.items():
            print(f"    {nome} {versao}")
    if manifesto.scripts:
        print()
        print(color("  scripts", "1;37"))
        for nome, comando in manifesto.scripts.items():
            print(f"    {nome:<10} dataforge {comando}")
    print()
    if not ok:
        sys.exit(1)


def _rodar_script(nome, flags):
    """Executa um script declarado no forge.toml."""
    from . import project

    manifesto = project.carregar(".")
    if manifesto is None or nome not in manifesto.scripts:
        return False
    comando = manifesto.scripts[nome]
    anterior = os.getcwd()
    os.chdir(manifesto.raiz)
    try:
        sys.argv = ["dataforge"] + comando.split() + flags
        main()
    finally:
        os.chdir(anterior)
    return True


def _ler(caminho):
    """Le um .df. Devolve (fonte, None) ou (None, motivo) — nunca estoura.

    Um arquivo mal codificado no meio de uma pasta nao pode derrubar
    'fmt .' ou 'lint .' inteiro; ele e reportado e os demais seguem.
    """
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read(), None
    except UnicodeDecodeError:
        return None, "nao esta em UTF-8"
    except OSError as e:
        return None, e.strerror or str(e)


#: Pastas que uma varredura por '.' nunca deve entrar.
#  forge_modules e codigo de terceiros: analisar, formatar ou lintar o que
#  se baixou nao ajuda ninguem, e enche a saida de ruido que o usuario nao
#  pode corrigir. E o mesmo motivo pelo qual ninguem linta node_modules.
PASTAS_IGNORADAS = {
    "forge_modules", ".git", "__pycache__", ".venv", "venv",
    "node_modules", "dist", ".pytest_cache", ".mypy_cache",
}


def _expandir(alvos, incluir_dependencias=False):
    """Resolve caminhos e pastas numa lista de arquivos .df.

    Uma pasta explicita e sempre respeitada: 'dataforge check
    forge_modules/x' analisa o que foi pedido. O filtro so vale para a
    varredura recursiva.
    """
    import glob as _glob

    ignorar = set() if incluir_dependencias else PASTAS_IGNORADAS
    arquivos = []

    def visivel(caminho):
        partes = set(os.path.normpath(caminho).split(os.sep))
        return not (partes & ignorar)

    for alvo in alvos:
        if os.path.isdir(alvo):
            achados = _glob.glob(os.path.join(alvo, "**", "*.df"),
                                 recursive=True)
            # o que foi pedido explicitamente nao e filtrado
            base = set(os.path.normpath(alvo).split(os.sep))
            arquivos.extend(
                a for a in achados
                if visivel(_curto(a, alvo)) or (base & ignorar))
        elif os.path.isfile(alvo):
            arquivos.append(alvo)
        else:
            achados = _glob.glob(alvo, recursive=True)
            arquivos.extend(a for a in achados
                            if a.endswith('.df') and visivel(a))
    return sorted(set(os.path.normpath(a) for a in arquivos))


# ═══════════════════════════════════════════════════════════
#  Comandos novos do 4.1
# ═══════════════════════════════════════════════════════════

def eval_command(codigo, debug=False):
    """dataforge eval '<codigo>' — roda uma linha sem criar arquivo."""
    if not codigo:
        print(color("Erro: informe o codigo entre aspas.", "1;31"))
        print("  dataforge eval 'out 2 ** 10'")
        sys.exit(1)

    # ';' separa instrucoes, para caber numa linha do shell
    fonte = codigo.replace("; ", "\n").replace(";", "\n")
    try:
        arvore = parse(tokenize(fonte, "<eval>"), "<eval>")
        Interpreter().run(arvore, "<eval>")
    except DataForgeError as e:
        e.filename = "<eval>"
        print(e.render(color='--no-color' not in sys.argv,
                       source_lines=fonte.split("\n")))
        sys.exit(1)


def watch_command(alvo, modo="run"):
    """dataforge watch — reexecuta a cada save.

    Sem biblioteca de watch: compara o mtime a cada meio segundo. Para
    um punhado de arquivos isso e mais simples e mais portatil que
    inotify, e a diferenca nao se percebe.
    """
    import subprocess

    arquivos = _expandir([alvo]) if alvo else _expandir(["."])
    if not arquivos:
        print(color("Nenhum arquivo .df para observar.", "1;33"))
        sys.exit(1)

    rotulo = {"run": f"run {alvo}", "test": "test", "check": "check ."}[modo]
    print(color(f"observando {len(arquivos)} arquivo(s) — Ctrl+C para sair",
                "1;36"))

    def rodar():
        os.system("clear" if os.name != "nt" else "cls")
        print(color(f"$ dataforge {rotulo}", "0;90"))
        print()
        comando = {"run": ["run", alvo] if alvo else ["run"],
                   "test": ["test"], "check": ["check", "."]}[modo]
        subprocess.run([sys.executable, "-m", "dataforge"] + comando)
        print()
        print(color("aguardando mudancas…", "0;90"))

    marcas = {a: os.path.getmtime(a) for a in arquivos}
    rodar()
    try:
        while True:
            time.sleep(0.5)
            mudou = False
            for a in list(marcas):
                try:
                    agora = os.path.getmtime(a)
                except OSError:
                    continue
                if agora != marcas[a]:
                    marcas[a] = agora
                    mudou = True
            if mudou:
                rodar()
    except KeyboardInterrupt:
        print("\n" + color("ate a proxima.", "1;33"))


def bench_command(alvo, repeticoes=10):
    """dataforge bench — mede o tempo, repetindo."""
    import statistics

    if not alvo or not os.path.exists(alvo):
        print(color(f"Erro: arquivo nao encontrado: {alvo}", "1;31"))
        sys.exit(1)

    fonte, motivo = _ler(alvo)
    if motivo:
        print(color(f"Erro: {alvo}: {motivo}", "1;31"))
        sys.exit(1)

    try:
        arvore = parse(tokenize(fonte, alvo), alvo)
    except DataForgeError as e:
        print(color(f"✗ {alvo}: {e.format()}", "1;31"))
        sys.exit(1)

    import io
    from contextlib import redirect_stdout

    print(color(f"medindo {os.path.basename(alvo)} — "
                f"{repeticoes} repeticoes", "1;36"))

    # As primeiras execucoes aquecem cache e alocador; medi-las
    # distorce a mediana para cima.
    aquecimento = min(3, max(1, repeticoes // 5))
    tempos = []
    for i in range(repeticoes + aquecimento):
        inicio = time.perf_counter()
        try:
            with redirect_stdout(io.StringIO()):
                Interpreter().run(arvore, alvo)
        except DataForgeError as e:
            print(color(f"✗ o programa falhou: {e.message}", "1;31"))
            sys.exit(1)
        decorrido = time.perf_counter() - inicio
        if i >= aquecimento:
            tempos.append(decorrido)

    def ms(v):
        return f"{v * 1000:.2f} ms"

    print()
    print(f"  mediana   {color(ms(statistics.median(tempos)), '1;32')}")
    print(f"  minimo    {ms(min(tempos))}")
    print(f"  maximo    {ms(max(tempos))}")
    if len(tempos) > 1:
        desvio = statistics.stdev(tempos)
        print(f"  desvio    {ms(desvio)}  "
              f"{color(f'({desvio / statistics.median(tempos) * 100:.1f}%)', '0;90')}")
    print(color(f"\n  {aquecimento} execucao(oes) de aquecimento descartada(s)",
                "0;90"))


def bigo_command(alvos, opcoes):
    """dataforge big-o — a complexidade de cada acao, sem rodar o codigo."""
    import json as _json
    from .complexidade import ESCALA, analisar_arquivo, para_json

    if opcoes.get("escala"):
        return _tabela_de_escala()

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        sys.exit(1)

    tudo = {}
    piores = []
    for caminho in arquivos:
        try:
            resultados = analisar_arquivo(caminho)
        except Exception as e:                       # noqa: BLE001
            if not opcoes.get("json"):
                print(color(f"  {_curto(caminho)}: "
                            f"{type(e).__name__}", "1;33"))
            continue
        tudo[caminho] = resultados
        piores.extend(resultados)

    if opcoes.get("json"):
        print(_json.dumps(
            {_curto(c): para_json(r) for c, r in tudo.items()},
            ensure_ascii=False, indent=2))
        return

    cores = {0: "1;32", 1: "1;36", 2: "1;33", 3: "1;31"}
    simbolos = {0: "●", 1: "●", 2: "▲", 3: "■"}

    for caminho, resultados in tudo.items():
        if not resultados:
            continue
        print()
        print(f"  {color(_curto(caminho), '1;37')}")
        for r in resultados:
            g = r.tempo.gravidade()
            print(f"    {color(simbolos[g], cores[g])} "
                  f"{r.nome:<26} "
                  f"{color(r.tempo.texto(), cores[g]):<22} tempo   "
                  f"{color(r.espaco.texto(), '0;90')} espaco")
            if opcoes.get("verboso"):
                for motivo in r.tempo.motivos[:3]:
                    print(f"        {color('· ' + motivo, '0;90')}")
                for aviso in r.avisos:
                    cor = {"grave": "1;31", "atencao": "1;33"}.get(
                        aviso["nivel"], "0;90")
                    print(f"        {color('⚠ ' + aviso['texto'], cor)}")
                    print(f"          {color(aviso['sugestao'], '0;90')}")

    ruins = [r for r in piores if r.tempo.gravidade() >= 2]
    print()
    if ruins:
        print(color(f"  {len(ruins)} acao(oes) acima de O(n log n):", "1;33"))
        for r in sorted(ruins, key=lambda x: -x.tempo._peso())[:8]:
            print(f"    {r.tempo.texto():<12} {r.nome}")
        print()
        print(color("  dataforge big-o <arquivo> -v   mostra o porque e o que fazer",
                    "0;90"))
    else:
        print(color(f"  ✓ {len(piores)} acao(oes), nenhuma acima de O(n log n)",
                    "1;32"))
    print()

    if opcoes.get("estrito") and ruins:
        sys.exit(1)


def _tabela_de_escala():
    """dataforge big-o --escala — o que cada classe custa na pratica."""
    from .complexidade import ESCALA

    print()
    print(f"  {color('A ESCALA', '1;37')}   "
          f"{color('operacoes por tamanho de entrada', '0;90')}")
    print()
    cabecalho = (f"  {'classe':<12} {'nome':<16} {'n=10':>10} "
                 f"{'n=1.000':>12} {'n=1.000.000':>14}")
    print(color(cabecalho, "0;90"))
    print(color("  " + "─" * 68, "0;90"))
    for linha in ESCALA:
        cor = {"O(1)": "1;32", "O(log n)": "1;32", "O(n)": "1;36",
               "O(n log n)": "1;36", "O(n^2)": "1;33", "O(n^3)": "1;33"}.get(
                   linha["notacao"], "1;31")
        print(f"  {color(linha['notacao'], cor):<21} {linha['nome']:<16} "
              f"{linha['n10']:>10} {linha['n1k']:>12} {linha['n1m']:>14}")
    print()
    for linha in ESCALA:
        print(f"  {color(linha['notacao'], '1;37'):<20} {linha['descricao']}")
        print(f"  {' ' * 12} {color(linha['exemplo'], '0;90')}")
    print()


def custo_command(alvos):
    """dataforge custo — o que cada 'adopt' traz junto.

    Uma linha de import nao parece cara. Um modulo com 200 simbolos e
    30 KB de codigo entra inteiro no processo, e num programa que so
    queria 'sqrt' isso e desperdicio que ninguem ve.
    """
    from .lexer import tokenize
    from .parser import parse
    from . import ast_nodes as ast
    from .stdlib import get_module

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        sys.exit(1)

    total_simbolos = 0
    print()
    for caminho in arquivos:
        fonte, motivo = _ler(caminho)
        if fonte is None:
            continue
        try:
            arvore = parse(tokenize(fonte, caminho), caminho)
        except Exception:                            # noqa: BLE001
            continue

        adocoes = [n for n in arvore.body if isinstance(n, ast.AdoptStatement)]
        if not adocoes:
            continue

        print(f"  {color(_curto(caminho), '1;37')}")
        for no in adocoes:
            nome = getattr(no, "module", "") or getattr(no, "path", "")
            modulo = get_module(nome) or get_module(nome.split(".")[-1])
            if modulo is None:
                print(f"    {color('?', '0;90')} {nome:<28} "
                      f"{color('modulo local', '0;90')}")
                continue

            simbolos = len(modulo)
            selecionados = getattr(no, "names", None) or []
            total_simbolos += simbolos

            tamanho = _peso_do_modulo(nome)
            cor = ("1;32" if simbolos < 20 else
                   "1;36" if simbolos < 60 else "1;33")
            detalhe = f"{simbolos} simbolos"
            if tamanho:
                detalhe += f", {tamanho // 1024} KB"
            print(f"    {color('●', cor)} {nome:<28} {color(detalhe, cor)}")

            if selecionados and len(selecionados) < simbolos / 3:
                print(f"      {color(f'usa {len(selecionados)} de {simbolos}', '0;90')}")
            elif not selecionados and simbolos > 40:
                print(f"      {color('adopt seletivo traria so o que voce usa:', '0;90')}")
                print(f"      {color(f'adopt {nome}.' + '{' + 'sqrt, floor' + '}', '0;90')}")
        print()

    print(color(f"  {total_simbolos} simbolo(s) importados no total", "0;90"))
    print()


def _peso_do_modulo(nome):
    """Bytes do arquivo que implementa o modulo, quando da para achar."""
    from . import stdlib
    base = os.path.dirname(os.path.abspath(stdlib.__file__))
    curto = nome.split(".")[-1].lower()
    for candidato in (f"arcane_{curto}.py", f"{curto}.py"):
        caminho = os.path.join(base, candidato)
        if os.path.isfile(caminho):
            return os.path.getsize(caminho)
    pasta = os.path.join(base, curto)
    if os.path.isdir(pasta):
        return sum(os.path.getsize(os.path.join(pasta, f))
                   for f in os.listdir(pasta) if f.endswith(".py"))
    return 0


def erros_command(filtro=""):
    """dataforge erros [termo] — o catalogo inteiro, por familia.

    Com 177 codigos, uma lista plana nao se le. O agrupamento por
    familia e o mesmo do codigo: os dois primeiros digitos depois do
    'DF' dizem a familia, entao quem ve 'DF06xx' na mensagem ja sabe
    que o problema e de colecao.
    """
    from .diagnosticos import por_familia, procurar

    if filtro:
        achados = procurar(filtro)
        if not achados:
            print(color(f"Nada no catalogo menciona '{filtro}'.", "1;33"))
            print("  Sem termo, 'dataforge erros' lista tudo.")
            sys.exit(1)
        print()
        print(f"  {len(achados)} resultado(s) para {color(filtro, '1;37')}")
        print()
        for e in achados:
            print(f"    {color(e['codigo'], '1;31')}  "
                  f"{e['titulo']:<42} {color(e['classe'], '0;90')}")
        print()
        print(color("  dataforge explain <codigo>  para o detalhe", "0;90"))
        print()
        return

    grupos = por_familia()
    total = sum(len(v) for v in grupos.values())
    print()
    print(f"  {color('CATALOGO DE ERROS', '1;37')}  "
          f"{color(f'{total} codigos em {len(grupos)} familias', '0;90')}")
    for nome, entradas in grupos.items():
        faixa = entradas[0]["codigo"][:4] + "xx"
        print()
        print(f"  {color(faixa, '1;33')}  {color(nome.upper(), '1;36')}")
        for e in entradas:
            print(f"    {color(e['codigo'], '1;31')}  "
                  f"{e['titulo']:<42} {color(e['classe'], '0;90')}")
    print()
    print(color("  dataforge explain <codigo|Classe>   o detalhe de um", "0;90"))
    print(color("  dataforge erros <termo>             procura no catalogo", "0;90"))
    print()


def explain_command(codigo):
    """dataforge explain DF0601 — o que significa um codigo de erro."""
    from .diagnosticos import CATALOGO, buscar

    if not codigo:
        print(color("Erro: informe o codigo.", "1;31"))
        print("  dataforge explain DF0601")
        print("  dataforge explain KeyError      (o nome tambem serve)")
        print()
        print(color("  dataforge erros   lista o catalogo inteiro", "0;90"))
        sys.exit(1)

    entrada = buscar(codigo)
    if entrada is None:
        print(color(f"Nao conheco o codigo '{codigo}'.", "1;31"))
        print(color("\n  dataforge erros            lista os 177 codigos", "0;90"))
        print(color("  dataforge erros <termo>    procura por assunto", "0;90"))
        sys.exit(1)

    cod, dados = entrada
    print()
    print(f"  {color(cod, '1;31')}  {color(dados['titulo'], '1;37')}")
    if dados.get('classe'):
        linhagem = f"{dados['classe']} < {dados['pai']}"
        print(f"  {color(dados['familia'], '1;36')}   "
              f"{color(linhagem, '0;90')}")
    print()
    for linha in dados['explicacao'].strip().split("\n"):
        print(f"  {linha}")
    if dados.get('exemplo'):
        print()
        print(f"  {color('EXEMPLO', '1;36')}")
        for linha in dados['exemplo'].strip().split("\n"):
            print(f"      {linha}")
    if dados.get('solucao'):
        print()
        print(f"  {color('COMO RESOLVER', '1;36')}")
        for linha in dados['solucao'].strip().split("\n"):
            print(f"      {linha}")
    if dados.get('doc'):
        print()
        print(color(f"  doc: https://dataforge-lang.vercel.app/docs/"
                    f"{dados['doc']}", "0;90"))
    print()


def tree_command():
    """dataforge tree — a arvore de dependencias."""
    from . import packages as pk

    manifesto = _manifesto_ou_sair()
    lock = pk.Lock(manifesto.raiz)
    if not lock.pacotes:
        print(color("Nenhum pacote instalado.", "1;33"))
        return

    diretas = list(manifesto.dependencies)
    print(color(f"{manifesto.name or 'projeto'} "
                f"{manifesto.version}", "1;36"))

    vistos = set()

    def ramo(nome, prefixo, ultimo):
        marca = "└─ " if ultimo else "├─ "
        info = lock.pacotes.get(nome)
        if info is None:
            print(f"{prefixo}{marca}{color(nome, '1;31')} "
                  f"{color('(nao instalado)', '0;90')}")
            return
        repetido = nome in vistos
        rotulo = f"{nome}@{info['versao']}"
        sufixo = color("  (ja mostrado)", "0;90") if repetido else ""
        print(f"{prefixo}{marca}{color(rotulo, '1;37')}{sufixo}")
        if repetido:
            return
        vistos.add(nome)

        filhos = sorted(info.get("dependencias", {}))
        novo_prefixo = prefixo + ("   " if ultimo else "│  ")
        for i, filho in enumerate(filhos):
            ramo(filho, novo_prefixo, i == len(filhos) - 1)

    for i, nome in enumerate(sorted(diretas)):
        ramo(nome, "", i == len(diretas) - 1)

    orfaos = sorted(set(lock.pacotes) - vistos)
    if orfaos:
        print()
        print(color(f"  {len(orfaos)} no lock mas fora da arvore: "
                    f"{', '.join(orfaos)}", "1;33"))
        print(color("  rode 'dataforge install' para reconciliar", "0;90"))


def why_command(nome):
    """dataforge why <pacote> — quem trouxe este pacote."""
    from . import packages as pk

    if not nome:
        print(color("Erro: informe o pacote.", "1;31"))
        sys.exit(1)

    manifesto = _manifesto_ou_sair()
    lock = pk.Lock(manifesto.raiz)
    if nome not in lock.pacotes:
        print(color(f"'{nome}' nao esta instalado.", "1;33"))
        perto = [n for n in lock.pacotes if nome in n]
        if perto:
            print(f"  Instalados parecidos: {', '.join(perto)}")
        sys.exit(1)

    diretas = set(manifesto.dependencies)
    caminhos = []

    def buscar_ate(alvo, atual, caminho):
        if atual == alvo and caminho:
            caminhos.append(list(caminho))
            return
        for filho in lock.pacotes.get(atual, {}).get("dependencias", {}):
            if filho in caminho:
                continue
            buscar_ate(alvo, filho, caminho + [filho])

    if nome in diretas:
        faixa = manifesto.dependencies[nome]
        faixa = faixa if isinstance(faixa, str) else "(fonte propria)"
        print(f"  {color(nome, '1;37')} e uma dependencia "
              f"{color('direta', '1;32')}")
        print(f"  declarada no forge.toml como {color(faixa, '1;37')}")
    else:
        for direta in sorted(diretas):
            buscar_ate(nome, direta, [direta])
        if not caminhos:
            print(color(f"  '{nome}' esta no lock, mas ninguem o exige.",
                        "1;33"))
            print(color("  rode 'dataforge install' para reconciliar", "0;90"))
            return
        print(f"  {color(nome, '1;37')} e "
              f"{color('transitiva', '1;33')} — veio por:")
        for caminho in caminhos:
            print("      " + color(" → ", "0;90").join(caminho))

    versao = lock.pacotes[nome]["versao"]
    print()
    print(f"  versao instalada: {color(versao, '1;37')}")


def outdated_command(offline=False):
    """dataforge outdated — o que tem versao mais nova."""
    from . import packages as pk

    manifesto = _manifesto_ou_sair()
    lock = pk.Lock(manifesto.raiz)
    if not lock.pacotes:
        print(color("Nenhum pacote instalado.", "1;33"))
        return

    registro = pk.Registro(offline=offline)
    declaradas = {d.nome: d for d in pk.ler_dependencias(manifesto.dependencies)}

    dentro_da_faixa, exige_mudanca, erros = [], [], []
    for nome, info in sorted(lock.pacotes.items()):
        dep = declaradas.get(nome)
        if dep is not None and dep.fonte != "registro":
            continue
        try:
            disponiveis = registro.versoes(nome)
        except pk.ErroPacote:
            erros.append(nome)
            continue

        atual = pk.Versao(info["versao"])
        mais_nova = max((pk.Versao(v) for v in disponiveis),
                        key=lambda v: v.chave, default=atual)
        if mais_nova <= atual:
            continue

        requisito = dep.requisito if dep else pk.Requisito("*")
        cabe = requisito.melhor(disponiveis)
        if cabe is not None and cabe > atual:
            dentro_da_faixa.append((nome, atual, cabe, mais_nova, requisito))
        else:
            exige_mudanca.append((nome, atual, mais_nova, requisito))

    if not dentro_da_faixa and not exige_mudanca:
        print(color("✓ tudo atualizado", "1;32"))
        return

    if dentro_da_faixa:
        print(color("Dentro da faixa declarada — basta reinstalar:", "1;36"))
        for nome, atual, cabe, ultima, req in dentro_da_faixa:
            print(f"  {nome:<18} {color(str(atual), '0;90')} → "
                  f"{color(str(cabe), '1;32')}   "
                  f"{color(f'({req})', '0;90')}")
        print(color("\n  dataforge install", "0;90"))

    if exige_mudanca:
        print()
        print(color("Exige mudar o forge.toml:", "1;33"))
        for nome, atual, ultima, req in exige_mudanca:
            print(f"  {nome:<18} {color(str(atual), '0;90')} → "
                  f"{color(str(ultima), '1;33')}   "
                  f"{color(f'a faixa {req} nao alcanca', '0;90')}")
        print(color("\n  confira o que mudou antes de subir a faixa", "0;90"))

    if erros:
        print()
        print(color(f"  nao consegui consultar: {', '.join(erros)}", "0;90"))


def deps_command(alvos):
    """dataforge deps — o grafo de imports do codigo."""
    import re as _re

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        return

    grafo, stdlib = {}, {}
    for caminho in arquivos:
        fonte, motivo = _ler(caminho)
        if motivo:
            continue
        curto = _curto(caminho)
        # 'adopt geometria.{a, b}' importa de 'geometria': o ponto antes
        # da chave separa o modulo dos nomes, e nao faz parte do nome.
        adotados = _re.findall(r'^\s*adopt\s+([A-Za-z_][\w.]*?)\.?(?=\s|\{|$)',
                               fonte, _re.MULTILINE)
        adotados += _re.findall(r'\bfrom\s+([A-Za-z_][\w.]*)', fonte)
        proprios = [a for a in adotados if not a.startswith("Arcane")
                    and a not in ("IO", "Math", "Text", "Data")]
        grafo[curto] = sorted(set(proprios))
        for a in adotados:
            if a.startswith("Arcane") or a in ("IO", "Math", "Text", "Data"):
                stdlib[a] = stdlib.get(a, 0) + 1

    com_deps = {k: v for k, v in grafo.items() if v}
    print(color(f"{len(grafo)} arquivo(s), "
                f"{len(com_deps)} com imports proprios", "1;36"))
    if com_deps:
        print()
        for arquivo in sorted(com_deps):
            print(f"  {color(arquivo, '1;37')}")
            for alvo in com_deps[arquivo]:
                print(f"      → {alvo}")

    if stdlib:
        print()
        print(color("Modulos da biblioteca padrao mais usados:", "1;36"))
        for nome, n in sorted(stdlib.items(), key=lambda x: -x[1])[:10]:
            print(f"  {nome:<24} {color(str(n) + '×', '0;90')}")

    # Ciclos: A adota B e B adota A, direta ou indiretamente
    ciclos = []
    def caminhar(no, visto):
        for vizinho in grafo.get(no, []):
            candidato = next((k for k in grafo if k.endswith(vizinho + ".df")),
                             None)
            if candidato is None:
                continue
            if candidato in visto:
                ciclos.append(visto[visto.index(candidato):] + [candidato])
                continue
            caminhar(candidato, visto + [candidato])
    for no in grafo:
        caminhar(no, [no])
    if ciclos:
        print()
        print(color(f"⚠ {len(ciclos)} ciclo(s) de import:", "1;33"))
        for c in ciclos[:5]:
            print("    " + " → ".join(c))


def clean_command(tudo=False):
    """dataforge clean — remove artefatos gerados."""
    import shutil

    from . import project as proj
    manifesto = proj.carregar(".")
    raiz = manifesto.raiz if manifesto else os.getcwd()

    alvos = [
        (os.path.join(raiz, "dist"), "dist/"),
    ]
    if tudo:
        from . import packages as pk
        alvos.append((os.path.join(raiz, pk.PASTA_MODULOS),
                      f"{pk.PASTA_MODULOS}/"))
        alvos.append((pk.CACHE, "cache global de pacotes"))

    liberado, removidos = 0, []
    for caminho, rotulo in alvos:
        if os.path.isdir(caminho):
            liberado += sum(
                os.path.getsize(os.path.join(pasta, f))
                for pasta, _, arquivos in os.walk(caminho) for f in arquivos)
            shutil.rmtree(caminho)
            removidos.append(rotulo)

    # __pycache__ espalhado
    n_cache = 0
    for pasta, subpastas, _ in os.walk(raiz):
        for sub in list(subpastas):
            if sub == "__pycache__":
                alvo = os.path.join(pasta, sub)
                liberado += sum(
                    os.path.getsize(os.path.join(p, f))
                    for p, _, fs in os.walk(alvo) for f in fs)
                shutil.rmtree(alvo, ignore_errors=True)
                subpastas.remove(sub)
                n_cache += 1
    if n_cache:
        removidos.append(f"{n_cache} __pycache__")

    if not removidos:
        print(color("Nada a limpar.", "1;33"))
        return
    print(color(f"✓ removido: {', '.join(removidos)}", "1;32"))
    print(f"  {liberado / 1024:.0f} KB liberados")
    if not tudo:
        print(color("  (--all inclui forge_modules/ e o cache global)", "0;90"))


# ─────────────────────────────────────────────────────────────
#  dataforge editor — instala a coloracao no VS Code
# ─────────────────────────────────────────────────────────────

#: Onde cada editor guarda as extensoes. Copiar a pasta e o que o
#: 'code --install-extension' faz por baixo, e funciona mesmo quando o
#: comando 'code' nao esta no PATH — o caso da maioria das instalacoes
#: no macOS.
PASTAS_DE_EDITOR = [
    ("VS Code",          "~/.vscode/extensions"),
    ("VS Code Insiders", "~/.vscode-insiders/extensions"),
    ("VSCodium",         "~/.vscode-oss/extensions"),
    ("Cursor",           "~/.cursor/extensions"),
    ("Windsurf",         "~/.windsurf/extensions"),
    ("VS Code (WSL)",    "~/.vscode-server/extensions"),
]

def _nome_extensao():
    """A pasta da extensao inclui a versao, como o VS Code espera.

    Derivar de __version__ em vez de escrever a mao evita o que ja
    aconteceu: a linguagem virou 1.0.0 e a pasta continuou dizendo
    4.2.0, porque ninguem lembrou de trocar em dois lugares.
    """
    return f"dataforge.dataforge-language-{__version__}"


NOME_EXTENSAO = _nome_extensao()


def _origem_da_extensao():
    """A pasta editor/vscode que veio junto com a instalacao."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(aqui, "editor", "vscode"),                   # no pacote
        os.path.join(os.path.dirname(aqui), "editor", "vscode"),  # no repo
    ]
    for caminho in candidatos:
        if os.path.isfile(os.path.join(caminho, "package.json")):
            return caminho
    return None


def _editores_presentes():
    achados = []
    for nome, bruto in PASTAS_DE_EDITOR:
        pasta = os.path.expanduser(bruto)
        if os.path.isdir(pasta):
            achados.append((nome, pasta))
    return achados


def _todas_as_versoes(pasta):
    """Qualquer versao da extensao ja instalada nesta pasta."""
    achadas = []
    try:
        for nome in os.listdir(pasta):
            if nome.startswith("dataforge") and "language" in nome:
                caminho = os.path.join(pasta, nome)
                if os.path.isdir(caminho):
                    achadas.append(caminho)
    except OSError:
        pass
    return achadas


def editor_command(args, flags=()):
    """Instala, remove ou confere a coloracao de sintaxe nos editores."""
    import shutil

    pedido = args[0] if args else ""
    remover = "--remove" in flags or pedido == "remove"
    so_status = "--status" in flags or pedido == "status"

    editores = _editores_presentes()
    if not editores:
        print(color("Nenhum editor compativel encontrado.", "1;33"))
        print()
        print("Procurei em:")
        for nome, bruto in PASTAS_DE_EDITOR:
            print("  " + color("·", "0;90") + f" {bruto}  " +
                  color(nome, "0;90"))
        print()
        print(color("dica:", "1;36") + " instale o VS Code e rode "
              "'dataforge editor' de novo.")
        return 1

    if so_status:
        print()
        print(color("  Coloracao de sintaxe do DataForge", "1;37"))
        print()
        for nome, pasta in editores:
            instalado = os.path.isdir(os.path.join(pasta, NOME_EXTENSAO))
            marca = (color("instalada", "1;32") if instalado
                     else color("nao instalada", "0;90"))
            print(f"  {nome:<20} {marca}")
        antigas = [c for _, p in editores for c in _todas_as_versoes(p)
                   if os.path.basename(c) != NOME_EXTENSAO]
        if antigas:
            print()
            print("  " + color("versoes antigas:", "1;33") +
                  f" {len(antigas)} — 'dataforge editor' substitui")
        print()
        return 0

    if remover:
        removidas = 0
        for nome, pasta in editores:
            for alvo in _todas_as_versoes(pasta):
                shutil.rmtree(alvo, ignore_errors=True)
                removidas += 1
                print("  " + color("removida", "1;31") + f" de {nome}")
        print()
        print(f"  {removidas} instalacao(oes) removida(s). Reinicie o editor.")
        print()
        return 0

    origem = _origem_da_extensao()
    if origem is None:
        print(color("Erro: os arquivos da extensao nao foram encontrados.",
                    "1;31"))
        print()
        print(color("nota:", "1;36") + " eles ficam em editor/vscode/.")
        print(color("dica:", "1;36") + " se instalou por curl/wget, baixe de "
              "novo — a extensao passou a vir junto na 4.2.0.")
        return 1

    print()
    print(color("  Instalando a coloracao do DataForge", "1;37"))
    print()
    instalados = 0
    for nome, pasta in editores:
        destino = os.path.join(pasta, NOME_EXTENSAO)
        try:
            # Uma versao antiga ficaria ativa junto com a nova, e o
            # editor escolheria uma das duas sem avisar qual.
            for antiga in _todas_as_versoes(pasta):
                shutil.rmtree(antiga, ignore_errors=True)
            shutil.copytree(origem, destino, dirs_exist_ok=True)
            instalados += 1
            print("  " + color("✓", "1;32") + f" {nome:<20} " +
                  color(destino, "0;90"))
        except OSError as erro:
            print("  " + color("✗", "1;31") + f" {nome:<20} {erro}")

    if not instalados:
        return 1

    print()
    print("  " + color("Pronto.", "1;32") +
          " Reinicie o editor e abra um arquivo .df.")
    print(color("  Voce ganha: cores para as palavras reservadas, snippets,",
                "0;90"))
    print(color("              indentacao de 4 espacos e dobra de blocos.",
                "0;90"))
    print()
    return 0


def main():
    """Main CLI entry point."""
    # Antes de qualquer coisa: garantir que o terminal aceita o que a
    # CLI desenha. No Windows, a saida redirecionada para um cano vem em
    # 'cp1252', que nao tem nenhum dos tracos das tabelas — e a metade
    # dos comandos morria com UnicodeEncodeError antes de imprimir a
    # primeira linha util.
    marca.preparar_saida()

    # Tudo depois de '--' pertence ao programa, nao ao dataforge.
    # Sem esta separacao, 'dataforge run app.df -- --porta 8080' faria o
    # proprio dataforge tentar entender '--porta'.
    bruto = sys.argv[1:]
    if '--' in bruto:
        corte = bruto.index('--')
        do_programa = bruto[corte + 1:]
        bruto = bruto[:corte]
    else:
        do_programa = []

    # O que o programa recebe em OS.argv(). JSON porque uma variavel de
    # ambiente nao aceita byte nulo, e um separador comum (':' ou ',')
    # quebraria num argumento que o contenha.
    import json as _json
    os.environ['DATAFORGE_ARGV'] = _json.dumps(do_programa)

    # Flag e o que comeca com '-' e tem mais que isso. Antes so o '--'
    # contava, e '-v' caia entre os ALVOS: 'dataforge test -v' procurava
    # um arquivo chamado '-v', e o modo verboso nunca ligava — em
    # nenhum comando que o oferecia.
    #
    # Um '-' sozinho continua sendo alvo: e como se pede a entrada
    # padrao.
    def _e_flag(a):
        return len(a) > 1 and a.startswith('-')

    args = [a for a in bruto if not _e_flag(a)]
    flags = [a for a in bruto if _e_flag(a)]

    debug = '--debug' in flags
    show_time = '--time' in flags

    # '--version' e o que todo script chama para conferir a instalacao —
    # o instalador, o CI, a extensao do editor. Ele caia no ramo "sem
    # argumentos" e imprimia a AJUDA INTEIRA, que nenhum deles sabe ler.
    if any(f in flags for f in ('--version', '-V')):
        print(f"DataForge v{__version__}")
        print(f"Python {sys.version}")
        sys.exit(0)

    if not args:
        # '-h' / '--help' sozinhos tambem caem aqui
        print(ajuda_geral())
        sys.exit(0)

    command = args[0]

    # 'dataforge <comando> --help' mostra a ajuda daquele comando
    if '--help' in flags or '-h' in sys.argv[1:]:
        detalhe = ajuda_comando(command)
        if detalhe:
            print(detalhe)
            sys.exit(0)

    if command == 'run':
        if len(args) < 2:
            # Sem arquivo: usa a entrada declarada no forge.toml.
            from . import project
            manifesto = project.carregar(".")
            if manifesto is None:
                print(color("Erro: informe o arquivo a executar, ou crie um "
                            "forge.toml com 'dataforge init'.", "1;31"))
                sys.exit(1)
            alvo = manifesto.entry_path()
            if not os.path.exists(alvo):
                print(color(f"Erro: a entrada '{manifesto.entry}' do forge.toml "
                            f"não existe.", "1;31"))
                sys.exit(1)
            run_file(alvo, debug=debug, show_time=show_time)
        else:
            run_file(args[1], debug=debug, show_time=show_time)

    elif command == 'repl':
        start_repl()

    elif command == 'stats':
        sys.exit(stats_command(args[1:], flags))

    elif command == 'profile':
        sys.exit(profile_command(args[1:], flags))

    elif command == 'fix':
        sys.exit(fix_command(args[1:], flags))

    elif command == 'editor':
        sys.exit(editor_command(args[1:], flags))

    elif command == 'vitrine':
        from .vitrine_cli import executar
        sys.exit(executar(args[1:], flags))

    elif command == 'debug':
        from .depurador import depurar
        paradas = []
        for f in flags:
            if f.startswith('--parar='):
                paradas += [int(x) for x in f.split('=', 1)[1].split(',')
                            if x.strip().isdigit()]
        resto = [a for a in args[1:] if not a.startswith('--')]
        if not resto:
            print("uso: dataforge debug <arquivo.df> [--parar=12,40]")
            sys.exit(1)
        sys.exit(depurar(resto[0], paradas, resto[1:]))

    elif command == 'lsp':
        # Nada de print aqui: stdout E o canal do protocolo, e um
        # caractere solto corrompe a proxima mensagem — o editor
        # desiste sem dizer por que.
        from .lsp import main as lsp_main
        sys.exit(lsp_main(args[1:] + list(flags)))

    elif command == 'new':
        if '--list' in flags or (len(args) > 1 and args[1] == 'list'):
            sys.exit(list_templates())
        sys.exit(new_project(args[1:], flags))

    elif command == 'api':
        sys.exit(api_command(args[1:], flags))

    elif command in ('converter', 'convert', 'migrar'):
        sys.exit(converter_command(args[1:], flags))

    elif command == 'tokens':
        if len(args) < 2:
            print(color("Error: No file specified.", "1;31"))
            sys.exit(1)
        show_tokens(args[1])

    elif command == 'ast':
        if len(args) < 2:
            print(color("Error: No file specified.", "1;31"))
            sys.exit(1)
        show_ast(args[1])

    elif command == 'check':
        check_command(args[1:], strict='--strict' in flags,
                      only_syntax='--syntax-only' in flags)

    elif command == 'fmt':
        fmt_command(args[1:], checar='--check' in flags)

    elif command == 'lint':
        lint_command(args[1:], strict='--strict' in flags)

    elif command == 'test':
        filtro = ""
        for f in flags:
            if f.startswith('--filter='):
                filtro = f.split('=', 1)[1]
        test_command(args[1:], verboso='--verbose' in flags or '-v' in flags,
                     filtro=filtro, parar='--fail-fast' in flags)

    elif command in ('crucible', 'cr'):
        opcoes = {
            "verboso": '--verbose' in flags or '-v' in flags,
            "aleatorio": '--aleatorio' in flags or '--random' in flags,
            "parar": '--fail-fast' in flags or '--parar' in flags,
            "matchers": '--matchers' in flags,
            "formato": "texto", "saida": "", "filtro": "",
            "tags": (), "sem_tags": (), "prazo": 0, "repetir": 1,
            "semente": None,
        }
        for f in flags:
            if f.startswith('--filter=') or f.startswith('--filtro='):
                opcoes["filtro"] = f.split('=', 1)[1]
            elif f.startswith('--tag='):
                opcoes["tags"] = tuple(f.split('=', 1)[1].split(','))
            elif f.startswith('--sem-tag='):
                opcoes["sem_tags"] = tuple(f.split('=', 1)[1].split(','))
            elif f.startswith('--formato='):
                opcoes["formato"] = f.split('=', 1)[1]
            elif f.startswith('--out='):
                opcoes["saida"] = f.split('=', 1)[1]
            elif f.startswith('--prazo='):
                opcoes["prazo"] = float(f.split('=', 1)[1])
            elif f.startswith('--repetir='):
                opcoes["repetir"] = int(f.split('=', 1)[1])
            elif f.startswith('--semente='):
                opcoes["semente"] = int(f.split('=', 1)[1])
        crucible_command(args[1:], opcoes)

    elif command == 'doc':
        saida = ""
        for f in flags:
            if f.startswith('--out='):
                saida = f.split('=', 1)[1]
        doc_command(args[1:], saida=saida)

    elif command == 'init':
        init_command(args[1:])

    elif command == 'add':
        add_command(args[1:], offline='--offline' in flags)

    elif command in ('remove', 'rm', 'uninstall'):
        remove_command(args[1:])

    elif command in ('install', 'i', 'sync'):
        install_command(offline='--offline' in flags,
                        conferir='--dry-run' in flags or '--check' in flags)

    elif command in ('list', 'ls'):
        list_command()

    elif command == 'search':
        search_command(args[1] if len(args) > 1 else '',
                       offline='--offline' in flags)

    elif command == 'pack':
        pack_command()

    elif command == 'publish':
        destino = None
        for f in flags:
            if f.startswith('--registry='):
                destino = f.split('=', 1)[1]
        publish_command(destino)

    elif command == 'info':
        info_command(args[1:])

    elif command == 'eval':
        eval_command(" ".join(args[1:]), debug=debug)

    elif command == 'watch':
        modo = ('test' if '--test' in flags
                else 'check' if '--check' in flags else 'run')
        watch_command(args[1] if len(args) > 1 else None, modo)

    elif command == 'bench':
        repeticoes = 10
        for f in flags:
            if f.startswith('--runs='):
                try:
                    repeticoes = max(1, int(f.split('=', 1)[1]))
                except ValueError:
                    print(color(f"--runs precisa de um numero: {f}", "1;31"))
                    sys.exit(1)
        bench_command(args[1] if len(args) > 1 else None, repeticoes)

    elif command == 'explain':
        explain_command(args[1] if len(args) > 1 else "")
    elif command in ('big-o', 'bigo', 'complexidade'):
        opcoes = {
            "verboso": '--verbose' in flags or '-v' in flags,
            "json": '--json' in flags,
            "escala": '--escala' in flags or '--scale' in flags,
            "estrito": '--strict' in flags or '--estrito' in flags,
        }
        bigo_command(args[1:], opcoes)
    elif command in ('custo', 'cost'):
        custo_command(args[1:])
    elif command in ('erros', 'errors'):
        erros_command(args[1] if len(args) > 1 else "")

    elif command == 'tree':
        tree_command()

    elif command == 'why':
        why_command(args[1] if len(args) > 1 else "")

    elif command == 'outdated':
        outdated_command(offline='--offline' in flags)

    elif command == 'deps':
        deps_command(args[1:])

    elif command == 'clean':
        clean_command(tudo='--all' in flags)

    elif command == 'version':
        print(f"DataForge v{__version__}")
        print(f"Python {sys.version}")

    elif command in ('help', '--help', '-h'):
        if len(args) > 1:
            detalhe = ajuda_comando(args[1])
            if detalhe:
                print(detalhe)
            else:
                print(color(f"Nao ha comando '{args[1]}'.", "1;31"))
                perto = comando_parecido(args[1])
                if perto:
                    print(f"  Voce quis dizer: {', '.join(perto)}?")
                sys.exit(1)
        else:
            print(ajuda_geral())

    elif command.endswith('.df'):
        # Direct file execution: dataforge myfile.df
        run_file(command, debug=debug, show_time=show_time)

    elif _rodar_script(command, sys.argv[2:]):
        pass

    else:
        print(color(f"'{command}' nao e um comando do DataForge.", "1;31"))
        perto = comando_parecido(command)
        if perto:
            if len(perto) == 1:
                print(f"\n  Voce quis dizer {color(perto[0], '1;37')}?")
            else:
                opcoes = ", ".join(color(p, '1;37') for p in perto)
                print(f"\n  Voce quis dizer: {opcoes}?")
        print(f"\n  {color('dataforge help', '1;36')} lista os "
              f"{len(set(c.nome for _, l in GRUPOS for c in l))} comandos.")
        sys.exit(1)


if __name__ == '__main__':
    main()


# ═══════════════════════════════════════════════════════════
#  Comandos 1.0 — analise, medicao e manutencao
# ═══════════════════════════════════════════════════════════

def stats_command(alvos, flags=()):
    """dataforge stats — o tamanho e a forma do codigo.

    Nao e 'linhas de codigo' como metrica de produtividade, que nao
    mede nada. E o inventario: quantas acoes, quantos blueprints, o
    arquivo mais longo, a acao mais longa. Serve para achar o que
    cresceu demais sem ninguem notar.
    """
    from .lexer import tokenize
    from .parser import parse
    from . import ast_nodes as ast

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        return 1

    total = {
        "arquivos": 0, "linhas": 0, "codigo": 0, "comentario": 0, "vazias": 0,
        "acoes": 0, "blueprints": 0, "records": 0, "enums": 0, "traits": 0,
        "testes": 0, "decoradores": 0,
    }
    maiores_arquivos = []
    maiores_acoes = []
    problemas = []

    for caminho in arquivos:
        fonte, motivo = _ler(caminho)
        if motivo:
            problemas.append((caminho, motivo))
            continue

        linhas = fonte.split("\n")
        total["arquivos"] += 1
        total["linhas"] += len(linhas)
        for linha in linhas:
            limpa = linha.strip()
            if not limpa:
                total["vazias"] += 1
            elif limpa.startswith("//") or limpa.startswith("#"):
                total["comentario"] += 1
            else:
                total["codigo"] += 1
        maiores_arquivos.append((len(linhas), caminho))

        try:
            arvore = parse(tokenize(fonte, caminho), caminho)
        except DataForgeError as erro:
            problemas.append((caminho, erro.message))
            continue

        pilha = list(arvore.body)
        while pilha:
            no = pilha.pop()
            if isinstance(no, ast.ActionDeclaration):
                total["acoes"] += 1
                if no.name.startswith("test_"):
                    total["testes"] += 1
                # A acao vai do 'action' ate o fim do corpo.
                fim = no.line
                for interno in no.body:
                    fim = max(fim, getattr(interno, "line", fim))
                maiores_acoes.append((fim - no.line + 1, no.name, caminho))
                pilha.extend(no.body)
            elif isinstance(no, ast.BlueprintDeclaration):
                total["blueprints"] += 1
                pilha.extend(no.body)
            elif isinstance(no, ast.RecordDeclaration):
                total["records"] += 1
            elif isinstance(no, ast.EnumDeclaration):
                total["enums"] += 1
            elif isinstance(no, ast.TraitDeclaration):
                total["traits"] += 1
            else:
                for campo in getattr(no, "__dataclass_fields__", ()):
                    valor = getattr(no, campo, None)
                    if isinstance(valor, list):
                        pilha.extend(v for v in valor
                                     if isinstance(v, ast.ASTNode))
            total["decoradores"] += len(getattr(no, "decorators", None) or [])

    print()
    print(color(f"  {total['arquivos']} arquivo(s) .df", "1;37"))
    print()

    linhas_uteis = max(total["codigo"], 1)
    print(f"  {color('linhas', '1;36')}")
    print(f"      {total['linhas']:>7}  total")
    print(f"      {total['codigo']:>7}  código")
    # Reusar a MESMA aspa dentro da f-string so vale a partir do 3.12;
    # ate o 3.11 o interpretador ve a string terminando ali.
    proporcao = total["comentario"] * 100 // linhas_uteis
    print(f"      {total['comentario']:>7}  comentário  "
          f"{color(f'({proporcao}% do código)', '0;90')}")
    print(f"      {total['vazias']:>7}  em branco")
    print()

    print(f"  {color('declarações', '1;36')}")
    for rotulo, chave in (("ações", "acoes"), ("blueprints", "blueprints"),
                          ("records", "records"), ("enums", "enums"),
                          ("traits", "traits"),
                          ("decoradores", "decoradores")):
        if total[chave]:
            print(f"      {total[chave]:>7}  {rotulo}")
    if total["testes"]:
        print(f"      {total['testes']:>7}  {color('testes', '1;32')}")
    print()

    if maiores_arquivos:
        maiores_arquivos.sort(reverse=True)
        print(f"  {color('maiores arquivos', '1;36')}")
        for tamanho, caminho in maiores_arquivos[:5]:
            print(f"      {tamanho:>7}  {color(caminho, '0;90')}")
        print()

    if maiores_acoes:
        maiores_acoes.sort(reverse=True)
        print(f"  {color('maiores ações', '1;36')}")
        for tamanho, nome, caminho in maiores_acoes[:5]:
            marca = "1;33" if tamanho > 50 else "0;90"
            print(f"      {color(f'{tamanho:>7}', marca)}  {nome}  "
                  f"{color(os.path.basename(caminho), '0;90')}")
        if maiores_acoes[0][0] > 50:
            # A expressao sai da f-string: quebra-la dentro das chaves
            # so vale a partir do 3.12, e a linguagem promete 3.10+.
            aviso = color("uma ação acima de 50 linhas costuma fazer "
                          "mais de uma coisa", "0;90")
            print(f"      {aviso}")
        print()

    if problemas:
        recado = color(f"{len(problemas)} arquivo(s) não puderam ser lidos",
                       "1;33")
        print(f"  {recado}")
        for caminho, motivo in problemas[:3]:
            print(f"      {caminho}: {motivo[:60]}")
        print()
    return 0


def fix_command(alvos, flags=()):
    """dataforge fix — formata e conserta o que da para consertar sozinho.

    Hoje: 'dataforge fmt' mais um relatorio do que o lint achou e nao
    da para arrumar automaticamente. A separacao importa — uma
    ferramenta que muda o codigo tem que ser previsivel, e 'consertar'
    o que exige julgamento seria pior do que apontar.
    """
    from .formatter import format_source
    from .lexer import tokenize
    from .linter import lint_program
    from .parser import parse

    arquivos = _expandir(alvos or ["."])
    if not arquivos:
        print(color("Nenhum arquivo .df encontrado.", "1;33"))
        return 1

    formatados, restantes, com_erro = [], [], []
    for caminho in arquivos:
        original, motivo = _ler(caminho)
        if motivo:
            com_erro.append((caminho, motivo))
            continue
        try:
            novo = format_source(original)
        except DataForgeError as erro:
            com_erro.append((caminho, erro.message))
            continue
        if novo != original:
            if "--dry-run" not in flags:
                open(caminho, "w", encoding="utf-8").write(novo)
            formatados.append(caminho)
        try:
            arvore = parse(tokenize(novo, caminho), caminho)
            for aviso in lint_program(arvore, caminho, novo):
                restantes.append((caminho, aviso))
        except DataForgeError:
            pass          # erro de sintaxe: o 'check' e quem reporta

    print()
    verbo = "seriam formatados" if "--dry-run" in flags else "formatados"
    if formatados:
        print(f"  {color('✓', '1;32')} {len(formatados)} arquivo(s) {verbo}")
        for caminho in formatados[:8]:
            print(f"      {color(caminho, '0;90')}")
    else:
        print(f"  {color('✓', '1;32')} tudo já estava formatado")

    if restantes:
        print()
        recado = color(f"{len(restantes)} aviso(s) que precisam de você",
                       "1;33")
        print(f"  {recado}")
        for caminho, aviso in restantes[:10]:
            texto = getattr(aviso, "message", str(aviso))
            linha = getattr(aviso, "line", "?")
            print(f"      {color(f'{caminho}:{linha}', '0;90')}  {texto[:70]}")
        if len(restantes) > 10:
            print(f"      {color(f'… e mais {len(restantes) - 10}', '0;90')}")
        print()
        print(f"      {color('rode', '0;90')} dataforge lint "
              f"{color('para ver todos', '0;90')}")

    if com_erro:
        print()
        for caminho, motivo in com_erro:
            print(f"  {color('✗', '1;31')} {caminho}: {motivo[:70]}")
    print()
    return 1 if com_erro else 0


def profile_command(args, flags=()):
    """dataforge profile <arquivo> — onde o tempo foi gasto.

    Um 'bench' diz que esta lento; um 'profile' diz onde. Mede por acao,
    contando chamadas e tempo acumulado, e mostra as mais caras.
    """
    if not args:
        print(color("Erro: informe o arquivo a analisar.", "1;31"))
        print(color("      dataforge profile src/main.df", "0;90"))
        return 1

    caminho = args[0]
    if not os.path.exists(caminho):
        print(color(f"Erro: '{caminho}' não existe.", "1;31"))
        return 1

    import time as _time
    from .interpreter import Interpreter
    from .lexer import tokenize
    from .parser import parse

    fonte, motivo = _ler(caminho)
    if motivo:
        print(color(f"Erro: {motivo}", "1;31"))
        return 1

    medidas = {}
    interpretador = Interpreter()
    original = interpretador._call_action
    # Uma acao recursiva (ou que chama outra) tem o tempo das chamadas
    # internas dentro do proprio. Somar tudo daria mais de 100% — foi
    # o que aconteceu na primeira versao: fib apareceu com 207%.
    #
    # O que se mede aqui e o tempo PROPRIO: o total menos o que foi
    # gasto nas chamadas que ela mesma fez. E o que responde "onde
    # mexer", que e a pergunta.
    pilha_tempo = []

    def medido(action, *resto, **kwargs):
        nome = getattr(action, "name", "?")
        pilha_tempo.append(0.0)
        inicio = _time.perf_counter()
        try:
            return original(action, *resto, **kwargs)
        finally:
            gasto = _time.perf_counter() - inicio
            nos_filhos = pilha_tempo.pop()
            proprio = max(gasto - nos_filhos, 0.0)
            if pilha_tempo:
                pilha_tempo[-1] += gasto
            atual = medidas.setdefault(nome, [0, 0.0, 0.0])
            atual[0] += 1
            atual[1] += proprio
            atual[2] += gasto

    interpretador._call_action = medido

    print()
    print(color(f"  medindo {caminho}…", "0;90"))
    comeco = _time.perf_counter()
    try:
        interpretador.run(parse(tokenize(fonte, caminho), caminho), caminho)
    except DataForgeError as erro:
        print()
        print(erro.render(fonte, color='--no-color' not in sys.argv))
        return 1
    total = _time.perf_counter() - comeco

    print()
    print(f"  {color('total', '1;37')}  {total * 1000:.1f} ms")
    print()

    if not medidas:
        print(color("  nenhuma ação foi chamada — o programa é só código "
                    "de topo", "0;90"))
        print()
        return 0

    # Ordena pelo tempo proprio: e onde vale mexer primeiro.
    ordenadas = sorted(medidas.items(), key=lambda kv: -kv[1][1])
    print(f"  {'ação':<26} {'chamadas':>9} {'próprio':>11} "
          f"{'acumulado':>12} {'por chamada':>13}")
    print(f"  {color('─' * 74, '0;90')}")
    for nome, (chamadas, proprio, acumulado) in ordenadas[:15]:
        fatia = proprio / total * 100 if total else 0
        marca = "1;33" if fatia > 20 else "0;37"
        print(f"  {color(nome[:24].ljust(24), marca)}  "
              f"{chamadas:>9}  "
              f"{proprio * 1000:>8.1f} ms  "
              f"{acumulado * 1000:>9.1f} ms  "
              f"{proprio / max(chamadas, 1) * 1000:>9.3f} ms  "
              f"{color(f'{fatia:4.1f}%', '0;90')}")
    print()
    print(f"  {color('próprio', '0;90')} = tempo na ação em si; "
          f"{color('acumulado', '0;90')} = inclui o que ela chamou")
    print()
    if ordenadas and ordenadas[0][1][1] / max(total, 1e-9) > 0.5:
        recado = color("metade do tempo está numa ação só — é por ela "
                       "que se começa", "0;90")
        print(f"  {recado}")
        print()
    return 0
