"""
DataForge CLI (Command Line Interface)
Main entry point for the DataForge language.
"""

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
    
    COMMANDS:
        run <file.df>      Run a DataForge source file
        repl               Start interactive REPL
        new                Create a new project from template
        tokens <file.df>   Show token stream
        ast <file.df>      Show Abstract Syntax Tree
        check <file.df>    Syntax check without running
        version            Show version information
        help               Show this help message
    
    OPTIONS:
        --debug            Enable debug output
        --time             Show execution time
        --no-color         Disable colored output
    
    EXAMPLES:
        dataforge run hello.df
        dataforge repl
        dataforge check myprogram.df
        df run examples/demo.df
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

        result = interpreter.run(tree)

        end_time = time.perf_counter()

        if show_time:
            elapsed = (end_time - start_time) * 1000
            print(color(f"\n⚡ Execution time: {elapsed:.2f}ms", "1;36"))

    except DataForgeError as e:
        print(color(f"\n{e.format()}", "1;31"))
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


def check_file(filepath: str):
    """Syntax-check a file without executing."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tokens = tokenize(source, filepath)
        tree = parse(tokens, filepath)
        print(color(f"✓ {filepath}: No syntax errors ({len(tree.body)} statements)", "1;32"))

    except DataForgeError as e:
        print(color(f"✗ {filepath}: {e.format()}", "1;31"))
        sys.exit(1)


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
            print(color("Error: No file specified. Usage: dataforge run <file.df>", "1;31"))
            sys.exit(1)
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
        if len(args) < 2:
            print(color("Error: No file specified.", "1;31"))
            sys.exit(1)
        check_file(args[1])

    elif command == 'version':
        print(f"DataForge v{__version__}")
        print(f"Python {sys.version}")

    elif command == 'help':
        print(USAGE)

    elif command.endswith('.df'):
        # Direct file execution: dataforge myfile.df
        run_file(command, debug=debug, show_time=show_time)

    else:
        print(color(f"Unknown command: {command}", "1;31"))
        print("Run 'dataforge help' for usage.")
        sys.exit(1)


if __name__ == '__main__':
    main()
