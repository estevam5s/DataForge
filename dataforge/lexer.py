"""
DataForge Lexer (Tokenizer)
Converts source code text into a stream of tokens.
Handles indentation-based scoping with INDENT/DEDENT tokens.
"""

from .tokens import Token, TokenType, KEYWORDS
from .errors import LexError, SyncError


class Lexer:
    """Tokenizes DataForge source code."""

    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.indent_stack = [0]  # Stack of indentation levels
        self.bracket_depth = 0   # Track (), [], {} nesting depth

    def error(self, message: str):
        raise LexError(message, self.line, self.column)

    def peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return '\0'

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def skip_comment(self):
        """Skip // single-line comments and # comments."""
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.advance()

    def skip_block_comment(self):
        """Skip /* ... */ block comments."""
        self.advance()  # skip *
        while self.pos < len(self.source):
            if self.peek() == '*' and self.peek(1) == '/':
                self.advance()
                self.advance()
                return
            self.advance()
        self.error("Unterminated block comment")

    def read_string(self, quote: str) -> Token:
        """Read a string literal (single or double quoted)."""
        line, col = self.line, self.column
        self.advance()  # skip opening quote
        result = []

        while self.pos < len(self.source):
            ch = self.peek()
            if ch == '\\':
                self.advance()
                esc = self.advance()
                escape_map = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    '\\': '\\', "'": "'", '"': '"',
                    '0': '\0',
                }
                result.append(escape_map.get(esc, '\\' + esc))
            elif ch == quote:
                self.advance()  # skip closing quote
                return Token(TokenType.STRING, ''.join(result), line, col)
            elif ch == '\n':
                self.error("Unterminated string literal")
            else:
                result.append(self.advance())

        self.error("Unterminated string literal")

    def read_multiline_string(self, quote: str) -> Token:
        """Read triple-quoted strings."""
        line, col = self.line, self.column
        # Skip the 3 opening quotes
        self.advance()
        self.advance()
        self.advance()
        result = []

        while self.pos < len(self.source):
            if self.peek() == quote and self.peek(1) == quote and self.peek(2) == quote:
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.STRING, ''.join(result), line, col)
            result.append(self.advance())

        self.error("Unterminated multiline string")

    def read_number(self) -> Token:
        """Read integer or float literal."""
        line, col = self.line, self.column
        result = []
        has_dot = False

        # Handle hex/octal/binary
        if self.peek() == '0' and self.peek(1) in ('x', 'X', 'o', 'O', 'b', 'B'):
            result.append(self.advance())  # 0
            result.append(self.advance())  # x/o/b
            while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
                if self.peek() != '_':
                    result.append(self.advance())
                else:
                    self.advance()  # skip _
            return Token(TokenType.INTEGER, int(''.join(result), 0), line, col)

        while self.pos < len(self.source):
            ch = self.peek()
            if ch == '_':
                self.advance()  # numeric separator
                continue
            if ch == '.' and not has_dot and self.peek(1).isdigit():
                has_dot = True
                result.append(self.advance())
            elif ch.isdigit():
                result.append(self.advance())
            else:
                break

        text = ''.join(result)
        if has_dot:
            return Token(TokenType.FLOAT, float(text), line, col)
        return Token(TokenType.INTEGER, int(text), line, col)

    def read_identifier(self) -> Token:
        """Read identifier or keyword."""
        line, col = self.line, self.column
        result = []
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
            result.append(self.advance())

        word = ''.join(result)

        # Check keywords
        if word in KEYWORDS:
            tok_type = KEYWORDS[word]
            value = word
            # Boolean literals
            if word == "yes":
                value = True
            elif word == "no":
                value = False
            elif word == "void":
                value = None
            return Token(tok_type, value, line, col)

        return Token(TokenType.IDENTIFIER, word, line, col)

    def handle_indentation(self):
        """Process indentation at the start of a logical line.
        Emits INDENT/DEDENT tokens."""
        spaces = 0
        start_pos = self.pos

        while self.pos < len(self.source) and self.source[self.pos] in (' ', '\t'):
            ch = self.source[self.pos]
            if ch == '\t':
                raise SyncError(
                    "Tab character detected. DataForge requires spaces only.",
                    self.line, self.column
                )
            spaces += 1
            self.pos += 1
            self.column += 1

        # Blank line or comment-only line: skip
        if self.pos >= len(self.source) or self.source[self.pos] == '\n':
            return
        if self.source[self.pos] == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
            return
        if self.source[self.pos] == '#':
            return

        # Dot-continuation: if the line starts with '.', it's a method chain
        # continuation. Remove the preceding NEWLINE and skip indent logic.
        if self.source[self.pos] == '.':
            if self.tokens and self.tokens[-1].type == TokenType.NEWLINE:
                self.tokens.pop()
            return

        current_indent = self.indent_stack[-1]

        if spaces > current_indent:
            self.indent_stack.append(spaces)
            self.tokens.append(Token(TokenType.INDENT, spaces, self.line, 1))
        elif spaces < current_indent:
            while self.indent_stack and self.indent_stack[-1] > spaces:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, spaces, self.line, 1))
            if self.indent_stack[-1] != spaces:
                raise SyncError(
                    f"Indentation mismatch: expected {self.indent_stack[-1]} spaces, got {spaces}",
                    self.line, 1
                )

    def tokenize(self) -> list[Token]:
        """Main tokenization loop. Returns list of tokens."""
        self.tokens = []
        at_line_start = True

        while self.pos < len(self.source):
            ch = self.peek()

            # Handle line starts (indentation) - only outside brackets
            if at_line_start:
                if self.bracket_depth == 0:
                    self.handle_indentation()
                else:
                    # Inside brackets: skip whitespace at line start
                    while self.pos < len(self.source) and self.source[self.pos] in (' ', '\t'):
                        self.pos += 1
                        self.column += 1
                at_line_start = False
                if self.pos >= len(self.source):
                    break
                ch = self.peek()

            # Newlines
            if ch == '\n':
                # Only emit NEWLINE tokens outside brackets
                if self.bracket_depth == 0:
                    self.tokens.append(Token(TokenType.NEWLINE, '\\n', self.line, self.column))
                self.advance()
                at_line_start = True
                continue

            # Whitespace (non-newline)
            if ch in (' ', '\r'):
                self.advance()
                continue

            # Tab in middle of line
            if ch == '\t':
                raise SyncError(
                    "Tab character in middle of line. Use spaces.",
                    self.line, self.column
                )

            # Comments vs Floor Division (//)
            if ch == '/' and self.peek(1) == '/':
                # Check if this is floor division or a comment
                # Floor division requires: last token ends an expression + next chars look like expression start
                # Also, if there are 3+ spaces before //, it's almost certainly a trailing comment
                is_floor_div = False
                if self.tokens:
                    last_type = self.tokens[-1].type
                    expr_end_types = {
                        TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.FLOAT,
                        TokenType.STRING, TokenType.RPAREN, TokenType.RBRACKET,
                        TokenType.RBRACE, TokenType.BOOLEAN, TokenType.VOID,
                    }
                    if last_type in expr_end_types:
                        # Check spacing before // — if 3+ spaces precede it, treat as comment
                        spaces_before = 0
                        check_pos = self.pos - 1
                        while check_pos >= 0 and self.source[check_pos] == ' ':
                            spaces_before += 1
                            check_pos -= 1
                        if spaces_before < 3:
                            # Check what follows // (skip whitespace)
                            look = self.pos + 2
                            while look < len(self.source) and self.source[look] == ' ':
                                look += 1
                            if look < len(self.source):
                                next_ch = self.source[look]
                                # Floor div if followed by a digit, (, identifier, or - (negative number)
                                if next_ch.isdigit() or next_ch == '(' or next_ch == '-' or next_ch.isalpha() or next_ch == '_':
                                    is_floor_div = True
                if is_floor_div:
                    line, col = self.line, self.column
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.FLOOR_DIV, '//', line, col))
                    continue
                else:
                    self.skip_comment()
                    continue
            if ch == '#':
                self.skip_comment()
                continue
            if ch == '/' and self.peek(1) == '*':
                self.advance()  # skip /
                self.skip_block_comment()
                continue

            # Strings
            if ch in ('"', "'"):
                if self.peek(1) == ch and self.peek(2) == ch:
                    self.tokens.append(self.read_multiline_string(ch))
                else:
                    self.tokens.append(self.read_string(ch))
                continue

            # Numbers
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue

            # Identifiers / Keywords
            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier())
                continue

            # Multi-char operators
            line, col = self.line, self.column

            if ch == ':' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, ':=', line, col))
                continue

            if ch == '*' and self.peek(1) == '*':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.POWER, '**', line, col))
                continue

            if ch == '>' and self.peek(1) == '>':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.PIPE, '>>', line, col))
                continue

            if ch == '!' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', line, col))
                continue

            if ch == '=' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.EQUAL, '==', line, col))
                continue

            # Single-char tokens
            single_map = {
                ':': TokenType.COLON,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.STAR,
                '/': TokenType.SLASH,
                '%': TokenType.PERCENT,
                '.': TokenType.DOT,
                ',': TokenType.COMMA,
                '@': TokenType.AT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
            }

            if ch in single_map:
                self.advance()
                # Track bracket depth for multi-line expressions
                if ch in ('(', '[', '{'):
                    self.bracket_depth += 1
                elif ch in (')', ']', '}'):
                    self.bracket_depth = max(0, self.bracket_depth - 1)
                self.tokens.append(Token(single_map[ch], ch, line, col))
                continue

            self.error(f"Unexpected character: {ch!r}")

        # Emit remaining DEDENTs
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, 0, self.line, 1))

        # Final NEWLINE if needed
        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self.tokens.append(Token(TokenType.NEWLINE, '\\n', self.line, self.column))

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(source: str, filename: str = "<stdin>") -> list[Token]:
    """Convenience function to tokenize source code."""
    lexer = Lexer(source, filename)
    return lexer.tokenize()
