"""
DataForge Custom Error Types
"""


class Frame:
    """Um quadro da pilha de chamadas do DataForge."""

    __slots__ = ('name', 'line', 'column', 'filename', 'kind')

    def __init__(self, name, line=0, column=0, filename="", kind="action"):
        self.name = name
        self.line = line
        self.column = column
        self.filename = filename
        self.kind = kind

    def __repr__(self):
        return f"<frame {self.name} L{self.line}>"


class DataForgeError(Exception):
    """Base error for all DataForge errors."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        self.stack = []        # list[Frame], preenchida pelo interpretador
        self.source_line = ""  # texto da linha que falhou
        self.filename = ""
        super().__init__(self.format())

    def format(self):
        loc = ""
        if self.line:
            loc = f" [line {self.line}"
            if self.column:
                loc += f", col {self.column}"
            loc += "]"
        return f"{self.__class__.__name__}{loc}: {self.message}"

    def friendly_name(self):
        """Nome do erro sem o sublinhado interno."""
        return self.__class__.__name__.rstrip('_')

    @staticmethod
    def _curto(caminho):
        """Caminho relativo ao diretório atual, quando isso encurta."""
        import os
        if not caminho or caminho.startswith('<'):
            return caminho or "<stdin>"
        try:
            relativo = os.path.relpath(caminho)
        except ValueError:
            return caminho
        return relativo if len(relativo) < len(caminho) else caminho

    def render(self, color=True, source_lines=None, debug=False):
        """Relatório completo: mensagem, trecho do código e pilha de chamadas."""
        def tinta(texto, codigo):
            return f"\033[{codigo}m{texto}\033[0m" if color else texto

        partes = []
        local = self._curto(self.filename)
        partes.append(
            f"{tinta(self.friendly_name(), '1;31')}: {self.message}")
        partes.append(f"  em {local}:{self.line}:{self.column}")

        # Trecho da linha que falhou, com um marcador na coluna
        if source_lines and 0 < self.line <= len(source_lines):
            texto = source_lines[self.line - 1].rstrip()
            recuo = len(texto) - len(texto.lstrip())
            partes.append("")
            partes.append(f"  {self.line:>4} | {texto}")
            if self.column:
                seta = ' ' * (self.column - 1) + '^'
                partes.append(f"       | {tinta(seta, '1;31')}")
            elif recuo >= 0:
                partes.append("       |")

        if self.stack:
            partes.append("")
            partes.append(tinta("  Pilha de chamadas (mais recente primeiro):", '1;36'))
            for quadro in reversed(self.stack):
                nome = quadro.name
                arquivo = self._curto(quadro.filename) if quadro.filename else local
                partes.append(f"    em {nome:<22} {arquivo}:{quadro.line}")
        return "\n".join(partes)


class SyncError(DataForgeError):
    """Raised when indentation is inconsistent (mixed tabs/spaces)."""
    pass


class LexError(DataForgeError):
    """Raised during tokenization."""
    pass


class ParseError(DataForgeError):
    """Raised during parsing."""
    pass


class RuntimeError_(DataForgeError):
    """Raised during interpretation/runtime."""
    pass


class TypeError_(DataForgeError):
    """Raised on type mismatch."""
    pass


class NameError_(DataForgeError):
    """Raised when a name is not found."""
    pass


class ImportError_(DataForgeError):
    """Raised when an adopt (import) fails."""
    pass


class IndexError_(DataForgeError):
    """Raised on invalid index access."""
    pass


class TriggerError(DataForgeError):
    """User-raised error via 'trigger'."""
    pass


class StackOverflowError_(DataForgeError):
    """Raised when recursion goes too deep."""
    pass


class ControlSignal(BaseException):
    """Base for internal control-flow signals.

    Derives from BaseException (not Exception) on purpose: 'halt', 'skip' and
    'yield' are control flow, not errors, so a 'monitor/handle' block must never
    swallow them.
    """
    pass


class HaltSignal(ControlSignal):
    """Internal signal for 'halt' (break)."""
    pass


class SkipSignal(ControlSignal):
    """Internal signal for 'skip' (continue)."""
    pass


class YieldSignal(ControlSignal):
    """Internal signal for 'yield' (return)."""

    def __init__(self, value=None):
        self.value = value
        super().__init__()
