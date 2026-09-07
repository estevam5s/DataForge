"""
DataForge Interactive REPL (Read-Eval-Print Loop)
"""

import os
import sys
import time
import traceback

from .lexer import tokenize
from .parser import parse
from .interpreter import Interpreter
from .errors import DataForgeError
from . import __version__


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
║    DataForge Programming Language                            ║
║    Digite 'exit' para sair | 'help' para os comandos         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
  COMANDOS DO REPL

    :help              esta ajuda                    (ou 'help')
    :exit              sai                           (ou 'exit', 'quit', Ctrl+D)
    :clear             limpa a tela
    :reset             zera o interpretador
    :env               variáveis definidas
    :type <expr>       o tipo de uma expressão
    :tokens <código>   o fluxo de tokens
    :ast <código>      a árvore sintática
    :check <código>    roda o analisador estático
    :load <arquivo>    carrega e executa um .df na sessão
    :save <arquivo>    grava o histórico da sessão num .df
    :history [n]       últimos comandos
    :time <código>     executa e mede o tempo
    :doc <nome>        o que é um nome definido na sessão
    :modules           módulos Arcane disponíveis
    :version           versão

  Um bloco começa com ':' no fim da linha e continua até uma linha em branco.
"""

HISTORICO_PADRAO = os.path.join(
    os.path.expanduser("~"), ".dataforge_history")

class REPL:
    """Interactive DataForge REPL."""

    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []
        self.sessao = []          # linhas de código válidas, para :save
        self._preparar_historico()

    def _preparar_historico(self):
        """Liga o histórico do readline, quando disponível."""
        try:
            import readline
        except ImportError:
            self._readline = None
            return
        self._readline = readline
        try:
            readline.read_history_file(HISTORICO_PADRAO)
        except (FileNotFoundError, OSError):
            pass
        readline.set_history_length(1000)
        try:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self._completar)
            readline.set_completer_delims(" \t\n(),:")
        except Exception:
            pass

    def _salvar_historico(self):
        if getattr(self, '_readline', None):
            try:
                self._readline.write_history_file(HISTORICO_PADRAO)
            except OSError:
                pass

    def _completar(self, texto, estado):
        """Autocompleta nomes definidos, palavras-chave e comandos."""
        from .tokens import KEYWORDS
        candidatos = sorted(
            set(self.interpreter.global_env.variables)
            | set(KEYWORDS)
            | {":help", ":exit", ":clear", ":reset", ":env", ":type", ":tokens",
               ":ast", ":check", ":load", ":save", ":history", ":time", ":doc",
               ":modules", ":version"})
        achados = [c for c in candidatos if c.startswith(texto)]
        return achados[estado] if estado < len(achados) else None

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

                if self._comando(line):
                    continue

                self._execute(line)

            except SystemExit:
                break
            except KeyboardInterrupt:
                print("\n\033[1;33m(use :exit para sair)\033[0m")
            except EOFError:
                self._salvar_historico()
                print("\n\033[1;33m⚡ Até a próxima!\033[0m\n")
                break

    def _comando(self, linha: str) -> bool:
        """Trata um comando do REPL. Devolve True se consumiu a linha."""
        nua = linha.strip()
        simples = nua.lstrip(':').lower()
        argumento = ""
        if " " in nua:
            cabeca, argumento = nua.split(" ", 1)
            simples_cabeca = cabeca.lstrip(':').lower()
        else:
            simples_cabeca = simples

        if simples in ('exit', 'quit', 'sair'):
            self._salvar_historico()
            print("\n\033[1;33m⚡ Até a próxima!\033[0m\n")
            raise SystemExit(0)
        if simples in ('help', 'ajuda', '?'):
            print(HELP_TEXT)
            return True
        if simples in ('clear', 'limpar'):
            print('\033[2J\033[H', end='')
            return True
        if simples == 'env':
            self._show_env()
            return True
        if simples == 'reset':
            self.interpreter = Interpreter()
            self.sessao.clear()
            print("\033[1;32m✓ interpretador zerado\033[0m")
            return True
        if simples == 'version':
            from . import __version__
            print(f"DataForge v{__version__}")
            return True
        if simples == 'modules':
            self._listar_modulos()
            return True

        if simples_cabeca == 'type' and argumento:
            self._mostrar_tipo(argumento)
            return True
        if simples_cabeca == 'tokens' and argumento:
            self._show_tokens(argumento)
            return True
        if simples_cabeca == 'ast' and argumento:
            self._show_ast(argumento)
            return True
        if simples_cabeca == 'check' and argumento:
            self._checar(argumento)
            return True
        if simples_cabeca == 'load' and argumento:
            self._carregar(argumento.strip())
            return True
        if simples_cabeca == 'save' and argumento:
            self._gravar(argumento.strip())
            return True
        if simples_cabeca in ('history', 'historico'):
            self._mostrar_historico(argumento)
            return True
        if simples_cabeca == 'time' and argumento:
            self._medir(argumento)
            return True
        if simples_cabeca == 'doc' and argumento:
            self._documentar(argumento.strip())
            return True

        # ':' sozinho ou comando desconhecido começando com ':'
        if nua.startswith(':'):
            print(f"\033[1;31mComando desconhecido: {nua.split()[0]}\033[0m")
            print("Use :help para ver a lista.")
            return True
        return False

    def _mostrar_tipo(self, fonte):
        try:
            tokens = tokenize(fonte, "<repl>")
            tree = parse(tokens, "<repl>")
            valor = self.interpreter.run(tree)
            tipo = self.interpreter._type_of(valor)
            print(f"\033[1;36m{tipo}\033[0m  = {self.interpreter._to_str(valor)}")
        except DataForgeError as e:
            print(f"\033[1;31m{e.format()}\033[0m")

    def _checar(self, fonte):
        from .typechecker import check_program
        try:
            tree = parse(tokenize(fonte, "<repl>"), "<repl>")
        except DataForgeError as e:
            print(f"\033[1;31m{e.format()}\033[0m")
            return
        diagnosticos = check_program(tree, "<repl>")
        if not diagnosticos:
            print("\033[1;32m✓ sem problemas\033[0m")
            return
        for d in diagnosticos:
            print(d.format("<repl>", color=True))

    def _carregar(self, caminho):
        if not os.path.exists(caminho):
            print(f"\033[1;31marquivo não encontrado: {caminho}\033[0m")
            return
        fonte = open(caminho, encoding='utf-8').read()
        try:
            self.interpreter.run(parse(tokenize(fonte, caminho), caminho),
                                 filename=caminho)
            definidos = len(self.interpreter.global_env.variables)
            print(f"\033[1;32m✓ {caminho} carregado "
                  f"({definidos} nomes na sessão)\033[0m")
            self.sessao.append(f"// carregado de {caminho}")
            self.sessao.append(fonte)
        except DataForgeError as e:
            print(e.render(color=True, source_lines=fonte.splitlines()))

    def _gravar(self, caminho):
        if not self.sessao:
            print("\033[1;33mnada para gravar ainda\033[0m")
            return
        if not caminho.endswith('.df'):
            caminho += '.df'
        conteudo = "// Sessão do REPL DataForge\n\n" + "\n".join(self.sessao) + "\n"
        open(caminho, 'w', encoding='utf-8').write(conteudo)
        print(f"\033[1;32m✓ {len(self.sessao)} trecho(s) gravados em {caminho}\033[0m")

    def _mostrar_historico(self, argumento):
        try:
            quantos = int(argumento.strip()) if argumento.strip() else 20
        except ValueError:
            quantos = 20
        recentes = self.history[-quantos:]
        largura = len(str(len(self.history)))
        inicio = len(self.history) - len(recentes) + 1
        for indice, linha in enumerate(recentes, start=inicio):
            print(f"  \033[0;90m{indice:>{largura}}\033[0m  {linha}")

    def _medir(self, fonte):
        inicio = time.perf_counter()
        self._execute(fonte)
        decorrido = (time.perf_counter() - inicio) * 1000
        print(f"\033[0;90m   {decorrido:.2f} ms\033[0m")

    def _documentar(self, nome):
        variaveis = self.interpreter.global_env.variables
        if nome not in variaveis:
            print(f"\033[1;33m'{nome}' não está definido nesta sessão\033[0m")
            return
        valor = variaveis[nome]
        tipo = self.interpreter._type_of(valor)
        print(f"  \033[1;36m{nome}\033[0m : {tipo}")
        from .interpreter import DFAction, DFBlueprint, DFEnum, DFRecord
        if isinstance(valor, DFAction):
            params = ", ".join(valor.params)
            print(f"  action {nome}({params})")
        elif isinstance(valor, DFRecord):
            print(f"  record {nome}: " + ", ".join(
                f"{c}: {t}" for c, t, _ in valor.fields))
        elif isinstance(valor, DFEnum):
            print(f"  enum {nome}: " + ", ".join(valor.members))
        elif isinstance(valor, DFBlueprint):
            print(f"  blueprint {nome}: " + ", ".join(valor.methods))
        elif isinstance(valor, dict) and "__name__" in valor:
            nomes = [k for k in valor if not k.startswith("__")]
            print(f"  módulo com {len(nomes)} símbolos")
            print("  " + ", ".join(sorted(nomes)[:12]) + ("…" if len(nomes) > 12 else ""))
        else:
            print(f"  = {self.interpreter._to_str(valor)}")

    def _listar_modulos(self):
        from .stdlib import get_module, list_modules
        canonicos = sorted(n for n in set(list_modules()) if n.startswith("Arcane."))
        print("\n\033[1;35m── Módulos Arcane ──\033[0m")
        for nome in canonicos:
            modulo = get_module(nome)
            quantos = len([k for k in modulo if not k.startswith("__")])
            print(f"  \033[1;36m{nome:<24}\033[0m {quantos:>3} símbolos")
        print()

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
            self.sessao.append(source)
            if result is not None:
                formatted = self.interpreter._to_str(result)
                print(f"\033[1;32m=> {formatted}\033[0m")
        except DataForgeError as e:
            print(e.render(color=True, source_lines=source.splitlines()))
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
