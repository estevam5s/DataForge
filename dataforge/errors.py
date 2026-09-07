"""
DataForge Custom Error Types
"""


class DataForgeError(Exception):
    """Base error for all DataForge errors."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format())

    def format(self):
        loc = ""
        if self.line:
            loc = f" [line {self.line}"
            if self.column:
                loc += f", col {self.column}"
            loc += "]"
        return f"{self.__class__.__name__}{loc}: {self.message}"


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
