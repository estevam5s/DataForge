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

USAGE = f"""{LOGO}
    DataForge Programming Language v{__version__}
    
    USAGE:
        dataforge <command> [options]
    
    COMANDOS:
        init [pasta]       Cria forge.toml e o esqueleto do projeto
        info               Mostra o manifesto do projeto atual
        run <arquivo.df>   Executa um programa (sem argumento usa forge.toml)
        check <alvo>       Análise estática: sintaxe, nomes e tipos
        test [alvo]        Executa a suíte de testes (*_test.df, tests/)
        fmt [alvo]         Formata o código (--check só verifica)
        lint [alvo]        Aponta problemas de estilo e higiene
        doc [alvo]         Gera documentação Markdown (--out=arquivo)
        repl               Console interativo
        new                Cria um projeto a partir de um template
        tokens <arquivo>   Mostra o fluxo de tokens (lexer)
        ast <arquivo>      Mostra a árvore sintática (parser)
        version            Mostra a versão
        help               Mostra esta ajuda
    
    OPTIONS:
        --debug            Mostra tokens, AST e traceback completo
        --time             Mostra o tempo de execução
        --no-color         Desliga as cores
        --strict           check: trata avisos como erros
        --syntax-only      check: só a sintaxe, sem análise semântica
        --check            fmt: só verifica, não reescreve
        --strict           check/lint: trata avisos como erros
        --verbose, -v      test: mostra cada caso
        --filter=<texto>   test: só os casos cujo nome contém o texto
        --fail-fast        test: para na primeira falha
        --out=<arquivo>    doc: escreve num arquivo em vez do terminal
    
    EXEMPLOS:
        dataforge run ola.df
        dataforge check src/
        dataforge test tests/ -v
        dataforge fmt . --check
        dataforge lint src/ --strict
        dataforge doc src/ --out=doc/API.md
"""


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

    plano = pk.resolver(declaradas, registro)
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
    from .linter import lint_program

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
        for d in lint_program(arvore, caminho, fonte):
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


def _expandir(alvos):
    """Resolve caminhos e pastas numa lista de arquivos .df."""
    import glob as _glob
    arquivos = []
    for alvo in alvos:
        if os.path.isdir(alvo):
            arquivos.extend(_glob.glob(os.path.join(alvo, "**", "*.df"),
                                       recursive=True))
        elif os.path.isfile(alvo):
            arquivos.append(alvo)
        else:
            achados = _glob.glob(alvo, recursive=True)
            arquivos.extend(a for a in achados if a.endswith('.df'))
    return sorted(set(os.path.normpath(a) for a in arquivos))


def main():
    """Main CLI entry point."""
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    debug = '--debug' in flags
    show_time = '--time' in flags

    if not args:
        print(USAGE)
        sys.exit(0)

    command = args[0]

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

    elif command == 'version':
        print(f"DataForge v{__version__}")
        print(f"Python {sys.version}")

    elif command == 'help':
        print(USAGE)

    elif command.endswith('.df'):
        # Direct file execution: dataforge myfile.df
        run_file(command, debug=debug, show_time=show_time)

    elif _rodar_script(command, sys.argv[2:]):
        pass

    else:
        print(color(f"Comando desconhecido: {command}", "1;31"))
        print("Rode 'dataforge help' para ver a lista.")
        sys.exit(1)


if __name__ == '__main__':
    main()
