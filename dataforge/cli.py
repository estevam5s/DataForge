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
