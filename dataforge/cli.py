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
    "api": {
        "name": "API REST",
        "description": "Servidor HTTP com rotas REST, CRUD e JSON",
        "icon": "🌐",
        "files": {
            "main.df": '''// {name} - API REST
// Criado com DataForge v{version}

adopt Http from "Arcane.Http"
adopt Data from "Arcane.Data"

// Criar aplicação
app := Http.create("{name}")

// Middleware
Http.cors(app)
Http.logger(app)

// Banco de dados em memória
items := []

// GET /api/items — Listar todos
Http.get(app, "/api/items", action(req, res):
    res.json(items)
end)

// GET /api/items/:id — Buscar por ID
Http.get(app, "/api/items/:id", action(req, res):
    id := to_number(req.params.id)
    item := items >> sift(i => i.id is id) >> first()
    given item isnot void:
        res.json(item)
    otherwise:
        res.json({{"error": "Item não encontrado"}}, 404)
    end
end)

// POST /api/items — Criar item
Http.post(app, "/api/items", action(req, res):
    body := req.json
    item := {{
        "id": length(items) + 1,
        "name": body.name,
        "status": "active"
    }}
    push(items, item)
    res.json(item, 201)
end)

// DELETE /api/items/:id — Remover item
Http.delete(app, "/api/items/:id", action(req, res):
    id := to_number(req.params.id)
    items := items >> sift(i => i.id isnot id)
    res.json({{"message": "Item removido"}})
end)

// Iniciar servidor
Http.listen(app, 3000)
''',
            "README.md": '''# {name}

API REST criada com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/items | Listar todos |
| GET | /api/items/:id | Buscar por ID |
| POST | /api/items | Criar item |
| DELETE | /api/items/:id | Remover item |

## Porta

Servidor roda em `http://localhost:3000`
''',
            "config.df": '''// Configurações do projeto
steady API_PORT := 3000
steady API_HOST := "0.0.0.0"
steady API_NAME := "{name}"
steady VERSION := "1.0.0"
''',
        }
    },
    "data": {
        "name": "Data Analytics",
        "description": "Projeto de análise de dados com estatísticas e visualização",
        "icon": "📊",
        "files": {
            "main.df": '''// {name} - Análise de Dados
// Criado com DataForge v{version}

adopt Math from "Arcane.Math"
adopt Data from "Arcane.Data"
adopt Analytics from "Arcane.Analytics"
adopt IO from "Arcane.IO"

// ─── Dataset de exemplo ───
dados := [
    {{"nome": "Alice", "idade": 28, "salario": 5500}},
    {{"nome": "Bruno", "idade": 34, "salario": 7200}},
    {{"nome": "Carla", "idade": 25, "salario": 4800}},
    {{"nome": "Diego", "idade": 41, "salario": 9100}},
    {{"nome": "Elena", "idade": 30, "salario": 6300}}
]

// ─── Análise estatística ───
salarios := dados >> morph(d => d.salario)

show("═══ Relatório de Análise ═══")
show("Total de registros: " + to_string(length(dados)))
show("Média salarial: R$ " + to_string(Math.mean(salarios)))
show("Mediana: R$ " + to_string(Math.median(salarios)))
show("Mínimo: R$ " + to_string(Math.min(salarios)))
show("Máximo: R$ " + to_string(Math.max(salarios)))
show("Desvio padrão: R$ " + to_string(Math.round(Math.std(salarios), 2)))

// ─── Filtros ───
show("\\n═══ Salários acima de R$ 6000 ═══")
altos := dados >> sift(d => d.salario bigger 6000)
cycle item in altos:
    show("  " + item.nome + ": R$ " + to_string(item.salario))
end

// ─── Transformação ───
show("\\n═══ Com bônus de 15% ═══")
com_bonus := dados >> morph(d => {{
    "nome": d.nome,
    "salario": d.salario,
    "bonus": Math.round(d.salario * 0.15, 2),
    "total": Math.round(d.salario * 1.15, 2)
}})

cycle item in com_bonus:
    show("  " + item.nome + ": R$ " + to_string(item.total))
end
''',
            "README.md": '''# {name}

Projeto de **Análise de Dados** criado com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Funcionalidades

- Estatísticas descritivas (média, mediana, desvio padrão)
- Filtragem e transformação de dados com pipelines
- Relatórios formatados no terminal
''',
        }
    },
    "web": {
        "name": "Web App",
        "description": "Aplicação web com servidor HTTP, templates e arquivos estáticos",
        "icon": "🖥️",
        "files": {
            "main.df": '''// {name} - Web Application
// Criado com DataForge v{version}

adopt Http from "Arcane.Http"

app := Http.create("{name}")
Http.cors(app)
Http.logger(app)
Http.static(app, "./public")

// Página inicial
Http.get(app, "/", action(req, res):
    html := "<html><head><title>{name}</title>"
    html := html + "<style>body{{font-family:sans-serif;max-width:800px;margin:50px auto;padding:20px}}</style>"
    html := html + "</head><body>"
    html := html + "<h1>🔥 {name}</h1>"
    html := html + "<p>Servidor DataForge rodando!</p>"
    html := html + "<a href='/api/status'>Ver status da API</a>"
    html := html + "</body></html>"
    res.html(html)
end)

// API Status
Http.get(app, "/api/status", action(req, res):
    res.json({{
        "status": "online",
        "app": "{name}",
        "version": "1.0.0"
    }})
end)

Http.listen(app, 3000)
''',
            "README.md": '''# {name}

Aplicação Web criada com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Estrutura

- `main.df` — Servidor principal
- `public/` — Arquivos estáticos (CSS, JS, imagens)
''',
            "public/index.html": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{name}</title>
</head>
<body>
    <h1>{name}</h1>
    <p>Bem-vindo ao {name}!</p>
</body>
</html>
''',
        }
    },
    "cli": {
        "name": "CLI Tool",
        "description": "Ferramenta de linha de comando com argumentos e cores",
        "icon": "⚡",
        "files": {
            "main.df": '''// {name} - CLI Tool
// Criado com DataForge v{version}

adopt IO from "Arcane.IO"
adopt Text from "Arcane.Text"

// ─── Configurações ───
steady APP_NAME := "{name}"
steady VERSION := "1.0.0"

// ─── Funções ───
action show_help():
    show("╔═══════════════════════════════╗")
    show("║  " + APP_NAME + " v" + VERSION + "  ║")
    show("╚═══════════════════════════════╝")
    show("")
    show("Uso: dataforge run main.df [comando]")
    show("")
    show("Comandos:")
    show("  help     Mostra essa ajuda")
    show("  version  Mostra a versão")
    show("  greet    Saudação personalizada")
end

action greet(name):
    show("👋 Olá, " + name + "! Bem-vindo ao " + APP_NAME + "!")
end

// ─── Main ───
show_help()
greet("Desenvolvedor")
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
    "crud": {
        "name": "CRUD Completo",
        "description": "API REST com CRUD completo, validação e testes",
        "icon": "🗃️",
        "files": {
            "main.df": '''// {name} - CRUD API
// Criado com DataForge v{version}

adopt Http from "Arcane.Http"
adopt Data from "Arcane.Data"

app := Http.create("{name}")
Http.cors(app)
Http.logger(app)

// ─── Database em memória ───
db := {{
    "users": [],
    "next_id": 1
}}

// ─── Validação ───
action validate_user(data):
    given data is void:
        yield {{"valid": no, "error": "Dados não fornecidos"}}
    end
    given data.name is void or length(data.name) smaller 2:
        yield {{"valid": no, "error": "Nome deve ter pelo menos 2 caracteres"}}
    end
    given data.email is void:
        yield {{"valid": no, "error": "Email é obrigatório"}}
    end
    yield {{"valid": yes}}
end

// CREATE
Http.post(app, "/api/users", action(req, res):
    validation := validate_user(req.json)
    given validation.valid is no:
        res.json({{"error": validation.error}}, 400)
        yield void
    end
    user := {{
        "id": db.next_id,
        "name": req.json.name,
        "email": req.json.email,
        "created_at": "2025-01-01"
    }}
    db.next_id := db.next_id + 1
    push(db.users, user)
    res.json(user, 201)
end)

// READ ALL
Http.get(app, "/api/users", action(req, res):
    res.json(db.users)
end)

// READ ONE
Http.get(app, "/api/users/:id", action(req, res):
    id := to_number(req.params.id)
    user := db.users >> sift(u => u.id is id) >> first()
    given user isnot void:
        res.json(user)
    otherwise:
        res.json({{"error": "Usuário não encontrado"}}, 404)
    end
end)

// UPDATE
Http.put(app, "/api/users/:id", action(req, res):
    id := to_number(req.params.id)
    cycle i in range(0, length(db.users)):
        given db.users[i].id is id:
            db.users[i].name := req.json.name or db.users[i].name
            db.users[i].email := req.json.email or db.users[i].email
            res.json(db.users[i])
            yield void
        end
    end
    res.json({{"error": "Usuário não encontrado"}}, 404)
end)

// DELETE
Http.delete(app, "/api/users/:id", action(req, res):
    id := to_number(req.params.id)
    db.users := db.users >> sift(u => u.id isnot id)
    res.json({{"message": "Usuário removido"}})
end)

show("🗃️ {name} — CRUD API")
Http.listen(app, 3000)
''',
            "tests.df": '''// Testes do CRUD
adopt Test from "Arcane.Test"

Test.describe("Validação de Usuário", [
    ["deve rejeitar dados vazios", action():
        Test.assert_equal(validate_user(void).valid, no)
    end],
    ["deve aceitar dados válidos", action():
        result := validate_user({{"name": "Teste", "email": "t@t.com"}})
        Test.assert_equal(result.valid, yes)
    end]
])
''',
            "README.md": '''# {name}

CRUD API completa criada com **DataForge** v{version}.

## Executar

```bash
dataforge run main.df
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/users | Criar usuário |
| GET | /api/users | Listar todos |
| GET | /api/users/:id | Buscar por ID |
| PUT | /api/users/:id | Atualizar |
| DELETE | /api/users/:id | Remover |
''',
        }
    },
    "fullstack": {
        "name": "Fullstack App",
        "description": "Aplicação completa com frontend HTML, API backend, e database",
        "icon": "🚀",
        "files": {
            "server.df": '''// {name} - Fullstack Server
// Criado com DataForge v{version}

adopt Http from "Arcane.Http"

app := Http.create("{name}")
Http.cors(app)
Http.logger(app)
Http.static(app, "./public")

// API
tasks := []
next_id := 1

Http.get(app, "/", action(req, res):
    res.html("<!DOCTYPE html><html><head><title>{name}</title></head>"
        + "<body><h1>🚀 {name}</h1>"
        + "<p>Acesse <a href='/api/tasks'>/api/tasks</a></p>"
        + "</body></html>")
end)

Http.get(app, "/api/tasks", action(req, res):
    res.json(tasks)
end)

Http.post(app, "/api/tasks", action(req, res):
    task := {{"id": next_id, "title": req.json.title, "done": no}}
    next_id := next_id + 1
    push(tasks, task)
    res.json(task, 201)
end)

show("🚀 {name} iniciado!")
Http.listen(app, 3000)
''',
            "public/index.html": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui; background: #0f0f23; color: #eee; padding: 2rem; }}
        h1 {{ color: #00d4ff; margin-bottom: 1rem; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {name}</h1>
        <p>Aplicação fullstack DataForge</p>
    </div>
</body>
</html>
''',
            "README.md": '''# {name}

Aplicação Fullstack criada com **DataForge** v{version}.

## Executar

```bash
dataforge run server.df
```

Abre `http://localhost:3000` no navegador.
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
