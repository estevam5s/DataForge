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
from .errors import DataForgeError


LOGO = r"""
     ____        _        _____                    
    |  _ \  __ _| |_ __ _|  ___|__  _ __ __ _  ___ 
    | | | |/ _` | __/ _` | |_ / _ \| '__/ _` |/ _ \
    | |_| | (_| | || (_| |  _| (_) | | | (_| |  __/
    |____/ \__,_|\__\__,_|_|  \___/|_|  \__, |\___|
                                         |___/      
"""

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
        Cmd("new", "dataforge new [template] [nome]",
            "Cria um projeto a partir de um template",
            "Templates: cli, api, lib, data, game, script.\n"
            "Sem argumento, lista os disponiveis.",
            exemplos=[("dataforge new", "lista os templates"),
                      ("dataforge new cli minha-ferramenta", "projeto de CLI")],
            veja=("init",)),
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

    ("Ambiente", [
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
            veja=("version",)),
    ]),
    ("Diagnostico", [
        Cmd("explain", "dataforge explain <codigo>",
            "Explica um codigo de erro",
            "Todo erro do DataForge tem um codigo estavel, como DF0601.\n"
            "Este comando diz o que ele significa e como resolver.",
            exemplos=[("dataforge explain DF0601", ""),
                      ("dataforge explain 0401", "o prefixo e opcional")],
            veja=("check",)),
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
    linhas = [LOGO.rstrip("\n")]
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
    print(f"  arquivo  {os.path.relpath(caminho)}")
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


def new_project():
    """Interactive project creation with colored output."""
    print()
    print(color("  ╔══════════════════════════════════════════╗", "1;36"))
    print(color("  ║      🔥 DataForge — Novo Projeto         ║", "1;36"))
    print(color("  ╚══════════════════════════════════════════╝", "1;36"))
    print()

    # Show project types
    print(color("  Escolha o tipo de projeto:\n", "1;37"))
    templates_list = list(PROJECT_TEMPLATES.keys())
    for i, key in enumerate(templates_list, 1):
        t = PROJECT_TEMPLATES[key]
        num = color(f"  [{i}]", "1;33")
        icon = t["icon"]
        name = color(t["name"], "1;37")
        desc = color(t["description"], "0;90")
        print(f"{num} {icon} {name}")
        print(f"       {desc}")
        print()

    # Get choice
    try:
        choice = input(color("  ➜ Número do template (1-" + str(len(templates_list)) + "): ", "1;32"))
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(templates_list):
            print(color("  ✗ Opção inválida.", "1;31"))
            sys.exit(1)
    except (ValueError, EOFError, KeyboardInterrupt):
        print(color("\n  ✗ Operação cancelada.", "1;31"))
        sys.exit(1)

    template_key = templates_list[choice_idx]
    template = PROJECT_TEMPLATES[template_key]

    # Get project name
    try:
        default_name = template["name"].replace(" ", "-").lower()
        proj_name = input(color(f"  ➜ Nome do projeto ({default_name}): ", "1;32")).strip()
        if not proj_name:
            proj_name = default_name
    except (EOFError, KeyboardInterrupt):
        print(color("\n  ✗ Operação cancelada.", "1;31"))
        sys.exit(1)

    # Sanitize name for directory
    dir_name = proj_name.replace(" ", "-").lower()
    dir_name = "".join(c for c in dir_name if c.isalnum() or c in "-_")

    if os.path.exists(dir_name):
        print(color(f"  ✗ Diretório '{dir_name}' já existe!", "1;31"))
        sys.exit(1)

    # Create project
    print()
    print(color(f"  ⚡ Criando projeto '{proj_name}'...", "1;33"))
    print()

    created_files = []
    for filepath, content in template["files"].items():
        full_path = os.path.join(dir_name, filepath)
        os.makedirs(os.path.dirname(full_path) if os.path.dirname(full_path) else dir_name, exist_ok=True)
        formatted = content.format(name=proj_name, version=__version__)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        created_files.append(filepath)
        print(color(f"    ✓ ", "1;32") + color(filepath, "0;37"))

    # Summary
    print()
    print(color("  ╔══════════════════════════════════════════╗", "1;32"))
    print(color("  ║      ✅ Projeto criado com sucesso!       ║", "1;32"))
    print(color("  ╚══════════════════════════════════════════╝", "1;32"))
    print()
    print(color(f"  📁 Diretório: ", "0;37") + color(dir_name + "/", "1;36"))
    print(color(f"  📦 Template:  ", "0;37") + color(f"{template['icon']} {template['name']}", "1;33"))
    print(color(f"  📄 Arquivos:  ", "0;37") + color(str(len(created_files)), "1;37"))
    print()
    print(color("  Para executar:", "1;37"))
    print()

    # Determine the main file
    main_file = "main.df" if "main.df" in template["files"] else list(template["files"].keys())[0]
    print(color(f"    cd {dir_name}", "1;36"))
    print(color(f"    dataforge run {main_file}", "1;36"))
    print()


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
    print(f"  manifesto  {os.path.relpath(manifesto.caminho)}")
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
                if visivel(os.path.relpath(a, alvo)) or (base & ignorar))
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


def explain_command(codigo):
    """dataforge explain DF0601 — o que significa um codigo de erro."""
    from .diagnosticos import CATALOGO, buscar

    if not codigo:
        print(color("Erro: informe o codigo.", "1;31"))
        print("  dataforge explain DF0601")
        print()
        print("  Codigos conhecidos:")
        for c in sorted(CATALOGO):
            print(f"    {c}  {CATALOGO[c]['titulo']}")
        sys.exit(1)

    entrada = buscar(codigo)
    if entrada is None:
        print(color(f"Nao conheco o codigo '{codigo}'.", "1;31"))
        print(f"\n  Codigos disponiveis: {', '.join(sorted(CATALOGO))}")
        sys.exit(1)

    cod, dados = entrada
    print()
    print(f"  {color(cod, '1;31')}  {color(dados['titulo'], '1;37')}")
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
        curto = os.path.relpath(caminho)
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

NOME_EXTENSAO = "dataforge.dataforge-language-4.2.0"


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

    args = [a for a in bruto if not a.startswith('--')]
    flags = [a for a in bruto if a.startswith('--')]

    debug = '--debug' in flags
    show_time = '--time' in flags

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

    elif command == 'editor':
        sys.exit(editor_command(args[1:], flags))

    elif command == 'editor':
        sys.exit(editor_command(args[1:], flags))

    elif command == 'new':
        new_project()

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
