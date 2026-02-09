"""
DataForge Interactive REPL (Read-Eval-Print Loop)
"""

import sys
import traceback

from .lexer import tokenize
from .parser import parse
from .interpreter import Interpreter
from .errors import DataForgeError


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ____        _        _____                               ║
║    |  _ \  __ _| |_ __ _|  ___|__  _ __ __ _  ___           ║
║    | | | |/ _` | __/ _` | |_ / _ \| '__/ _` |/ _ \          ║
║    | |_| | (_| | || (_| |  _| (_) | | | (_| |  __/          ║
║    |____/ \__,_|\__\__,_|_|  \___/|_|  \__, |\___|          ║
║                                         |___/                ║
║                                                              ║
║    DataForge Programming Language v2.0                       ║
║    Type 'exit' to quit | 'help' for commands                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
╔══════════════════════════════════════════════════════════════╗
║  DATAFORGE REPL COMMANDS                                     ║
╠══════════════════════════════════════════════════════════════╣
║  exit / quit      - Exit the REPL                            ║
║  help             - Show this help                           ║
║  clear            - Clear screen                             ║
║  env              - Show current environment variables        ║
║  reset            - Reset the interpreter state               ║
║  tokens <code>    - Show tokens for code                     ║
║  ast <code>       - Show AST for code                        ║
║  version          - Show version info                        ║
╚══════════════════════════════════════════════════════════════╝
"""


class REPL:
    """Interactive DataForge REPL."""

    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []

    def start(self):
        """Start the REPL loop."""
        print(BANNER)

        while True:
            try:
                # Read input
                line = input("\033[1;36mforge>\033[0m ")

                if not line.strip():
                    continue

                # Handle multi-line input (blocks)
                if line.strip().endswith(':'):
                    line = self._read_block(line)

                self.history.append(line)

                # Handle commands
                cmd = line.strip().lower()
                if cmd in ('exit', 'quit'):
                    print("\n\033[1;33m⚡ Farewell, Forger!\033[0m\n")
                    break
                elif cmd == 'help':
                    print(HELP_TEXT)
                    continue
                elif cmd == 'clear':
                    print('\033[2J\033[H', end='')
                    continue
                elif cmd == 'env':
                    self._show_env()
                    continue
                elif cmd == 'reset':
                    self.interpreter = Interpreter()
                    print("\033[1;32m✓ Interpreter reset.\033[0m")
                    continue
                elif cmd == 'version':
                    from . import __version__
                    print(f"DataForge v{__version__}")
                    continue
                elif cmd.startswith('tokens '):
                    self._show_tokens(line[7:])
                    continue
                elif cmd.startswith('ast '):
                    self._show_ast(line[4:])
                    continue

                # Execute DataForge code
                self._execute(line)

            except KeyboardInterrupt:
                print("\n\033[1;33m(Use 'exit' to quit)\033[0m")
            except EOFError:
                print("\n\033[1;33m⚡ Farewell, Forger!\033[0m\n")
                break

    def _read_block(self, first_line: str) -> str:
        """Read a multi-line block until empty line."""
        lines = [first_line]
        while True:
            try:
                continuation = input("\033[1;90m..... \033[0m")
                if continuation.strip() == '':
                    break
                lines.append(continuation)
            except (KeyboardInterrupt, EOFError):
                break
        return '\n'.join(lines)

    def _execute(self, source: str):
        """Execute a line of DataForge code."""
        try:
            tokens = tokenize(source, "<repl>")
            tree = parse(tokens, "<repl>")
            result = self.interpreter.run(tree)
            if result is not None:
                formatted = self.interpreter._to_str(result)
                print(f"\033[1;32m=> {formatted}\033[0m")
        except DataForgeError as e:
            print(f"\033[1;31m{e.format()}\033[0m")
        except Exception as e:
            print(f"\033[1;31mInternal Error: {e}\033[0m")
            if '--debug' in sys.argv:
                traceback.print_exc()

    def _show_env(self):
        """Display current environment."""
        env = self.interpreter.global_env
        print("\n\033[1;35m── Environment ──\033[0m")
        for name, value in sorted(env.variables.items()):
            if name.startswith('_') or callable(value):
                continue
            vstr = self.interpreter._to_str(value)
            if len(vstr) > 60:
                vstr = vstr[:57] + "..."
            print(f"  \033[1;36m{name}\033[0m = {vstr}")
        print()

    def _show_tokens(self, source: str):
        """Show token list for source code."""
        try:
            tokens = tokenize(source, "<repl>")
            for tok in tokens:
                print(f"  {tok}")
        except DataForgeError as e:
            print(f"\033[1;31m{e.format()}\033[0m")

    def _show_ast(self, source: str):
        """Show AST for source code."""
        try:
            tokens = tokenize(source, "<repl>")
            tree = parse(tokens, "<repl>")
            self._print_ast(tree, 0)
        except DataForgeError as e:
            print(f"\033[1;31m{e.format()}\033[0m")

    def _print_ast(self, node, depth: int):
        """Pretty-print an AST node."""
        indent = "  " * depth
        name = type(node).__name__
        print(f"{indent}\033[1;33m{name}\033[0m", end="")

        from . import ast_nodes as ast
        if isinstance(node, (ast.IntegerLiteral, ast.FloatLiteral)):
            print(f" ({node.value})")
        elif isinstance(node, ast.StringLiteral):
            print(f" ({node.value!r})")
        elif isinstance(node, ast.BooleanLiteral):
            print(f" ({'yes' if node.value else 'no'})")
        elif isinstance(node, ast.Identifier):
            print(f" ({node.name})")
        elif isinstance(node, ast.BinaryOp):
            print(f" (op={node.op})")
            self._print_ast(node.left, depth + 1)
            self._print_ast(node.right, depth + 1)
        elif isinstance(node, ast.Assignment):
            print()
            self._print_ast(node.target, depth + 1)
            self._print_ast(node.value, depth + 1)
        elif isinstance(node, ast.Program):
            print(f" ({len(node.body)} statements)")
            for stmt in node.body:
                self._print_ast(stmt, depth + 1)
        else:
            print()


def start_repl():
    """Start the DataForge REPL."""
    repl = REPL()
    repl.start()
