"""
DataForge Lexer (Tokenizer)
Converts source code text into a stream of tokens.
Handles indentation-based scoping with INDENT/DEDENT tokens.
"""

from .tokens import Token, TokenType, KEYWORDS
from .errors import DataForgeError, LexError, SyncError


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

    def read_interpolated(self, quote: str) -> Token:
        """Read $"texto {expr} texto" into a list of parts.

        The token value is a list of ('text', str) and ('expr', source) pairs;
        the parser turns each 'expr' source into a real sub-expression.
        Use '{{' and '}}' for literal braces.
        """
        line, col = self.line, self.column
        self.advance()  # skip '$'
        triple = self.peek(1) == quote and self.peek(2) == quote
        if triple:
            self.advance(); self.advance(); self.advance()
        else:
            self.advance()  # opening quote

        parts = []
        buffer = []

        def flush():
            if buffer:
                parts.append(('text', ''.join(buffer)))
                buffer.clear()

        while self.pos < len(self.source):
            ch = self.peek()

            if triple and ch == quote and self.peek(1) == quote and self.peek(2) == quote:
                self.advance(); self.advance(); self.advance()
                flush()
                return Token(TokenType.INTERP_STRING, parts, line, col)
            if not triple and ch == quote:
                self.advance()
                flush()
                return Token(TokenType.INTERP_STRING, parts, line, col)

            if ch == '\\':
                self.advance()
                esc = self.advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                              "'": "'", '"': '"', '0': '\0', '{': '{', '}': '}'}
                buffer.append(escape_map.get(esc, '\\' + esc))
                continue

            if ch == '{':
                if self.peek(1) == '{':      # '{{' escapes a literal brace
                    self.advance(); self.advance()
                    buffer.append('{')
                    continue
                self.advance()               # opening brace
                flush()
                depth = 1
                expr_chars = []
                while self.pos < len(self.source) and depth > 0:
                    c = self.peek()
                    if c in ('"', "'"):
                        # copy a nested string literal verbatim
                        q = self.advance()
                        expr_chars.append(q)
                        while self.pos < len(self.source) and self.peek() != q:
                            if self.peek() == '\\':
                                expr_chars.append(self.advance())
                            expr_chars.append(self.advance())
                        if self.pos < len(self.source):
                            expr_chars.append(self.advance())
                        continue
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            self.advance()
                            break
                    if c == '\n':
                        self.error("Unterminated interpolation: '}' expected")
                    expr_chars.append(self.advance())
                else:
                    if depth > 0:
                        self.error("Unterminated interpolation: '}' expected")
                fonte = ''.join(expr_chars).strip()
                if not fonte:
                    self.error("Empty interpolation: '{}' needs an expression")
                expressao, formato = _separar_formato(fonte)
                parts.append(('expr', expressao)
                             if not formato else ('fmt', (expressao, formato)))
                continue

            if ch == '}' and self.peek(1) == '}':
                self.advance(); self.advance()
                buffer.append('}')
                continue

            if ch == '\n' and not triple:
                self.error("Unterminated interpolated string")

            buffer.append(self.advance())

        self.error("Unterminated interpolated string")

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

        # Notacao cientifica: '6.022e23', '1e-7', '2E+3'.
        #
        # O 'e' so faz parte do numero quando ha DIGITO depois dele —
        # com sinal opcional no meio. Sem essa confirmacao, 'x := 2' e
        # 'e := 3' em linhas seguidas viraria um numero so, e um nome
        # chamado 'e' deixaria de existir.
        expoente = False
        if self.pos < len(self.source) and self.peek() in ('e', 'E'):
            adiante = 1
            if self.peek(adiante) in ('+', '-'):
                adiante += 1
            if self.peek(adiante).isdigit():
                expoente = True
                result.append(self.advance())              # e/E
                if self.peek() in ('+', '-'):
                    result.append(self.advance())          # sinal
                while self.pos < len(self.source) and (
                        self.peek().isdigit() or self.peek() == '_'):
                    c = self.advance()
                    if c != '_':
                        result.append(c)

        text = ''.join(result)
        if has_dot or expoente:
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
            return Token(tok_type, value, line, col, text=word)

        return Token(TokenType.IDENTIFIER, word, line, col)

    #: Operadores que, no fim da linha, indicam que ela continua abaixo.
    #  'not' e o unario '-' ficam de fora: uma linha pode legitimamente
    #  terminar neles em outro contexto.
    FIM_INCOMPLETO = frozenset({
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
        TokenType.PERCENT, TokenType.POWER, TokenType.FLOOR_DIV,
        TokenType.AND, TokenType.OR,
        TokenType.EQUAL, TokenType.NOT_EQUAL,
        TokenType.LT, TokenType.GT, TokenType.LT_EQ, TokenType.GT_EQ,
        TokenType.IS, TokenType.ISNT,
        TokenType.BIGGER, TokenType.SMALLER,
        TokenType.BIGGER_EQ, TokenType.SMALLER_EQ,
        TokenType.COALESCE, TokenType.COMMA, TokenType.ASSIGN,
        TokenType.PIPE, TokenType.ARROW, TokenType.FAT_ARROW,
        TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
        TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN,
        TokenType.PERCENT_ASSIGN,
    })

    def _continua_expressao(self):
        """A linha anterior terminou em operador, esperando o resto?"""
        i = len(self.tokens) - 1
        while i >= 0 and self.tokens[i].type == TokenType.NEWLINE:
            i -= 1
        return i >= 0 and self.tokens[i].type in self.FIM_INCOMPLETO

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

        # Continuation lines: a line that starts with '.' continues a method
        # chain, and one that starts with '>>' continues a pipeline. In both
        # cases drop the pending NEWLINE and skip the indent bookkeeping.
        here = self.source[self.pos]
        if here == '.' or (here == '>' and self.source[self.pos + 1:self.pos + 2] == '>'):
            if self.tokens and self.tokens[-1].type == TokenType.NEWLINE:
                self.tokens.pop()
            return

        # A linha ANTERIOR terminou num operador binario? Entao ela esta
        # obviamente incompleta — nao ha o que possa significar sozinha —
        # e esta e a continuacao dela:
        #
        #     mensagem := "primeira parte " +
        #                 "segunda parte"
        #
        # Sem isto, o recuo da segunda linha viraria INDENT e o parser
        # veria um bloco onde ha uma expressao.
        if self._continua_expressao():
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

    # ── '//' disambiguation ────────────────────────────────
    _EXPR_END_TYPES = None

    @staticmethod
    def _numero_e_operando(depois: str) -> bool:
        """O numero logo apos '//' e um operando, ou o inicio de prosa?

        '7 // 2' e divisao. '// 200, application/json' e comentario.
        A diferenca esta no que segue o numero: depois de um operando
        vem fim de linha, operador, fecha-delimitador ou virgula de
        argumento — nunca uma palavra.

        Sem isto, todo comentario que comeca com numero vira codigo, e
        o programa quebra num lugar que nao tem nada a ver com o erro.
        """
        i = 0
        while i < len(depois) and (depois[i].isdigit() or depois[i] == '.'):
            i += 1
        resto = depois[i:].lstrip()

        if not resto:
            return True                     # '7 // 2'

        # Uma letra logo depois do numero e prosa: '// 200 OK'.
        # (Um espaco ja foi consumido pelo lstrip.)
        if resto[0].isalpha() or resto[0] == '_':
            return False

        # Pontuacao que NAO existe em expressao so aparece em prosa. O
        # travessao e o caso que mais dói: '// 10 — o dobro' e um
        # comentario que qualquer um escreve, e sem esta linha ele vira
        # 'x // 10' seguido de um caractere que o lexer nao conhece —
        # com o erro apontando para o travessao, longe da causa.
        if resto[0] in '—–…"\'‘’“”¡¿·•':
            return False

        # Dois pontos e virgula seguidos de palavra tambem: '// 404, nao achei'
        if resto[0] in ',:' :
            seguinte = resto[1:].lstrip()
            # 'seguinte and ...' antes do 'in': em Python, uma string
            # VAZIA e subcadeia de qualquer outra, e sem a guarda
            # 'cycle i from 1 to n // 20:' — onde nada segue os dois
            # pontos — virava comentario e o laco perdia o limite.
            prosa = (seguinte[:1].isalpha() or seguinte[:1] == '_'
                     or (seguinte and seguinte[0] in '—–'))
            return not prosa
        return True

    def _looks_like_floor_div(self) -> bool:
        """Decide se o '//' na posicao atual e divisao inteira ou comentario.

        Regra (deliberadamente conservadora): '//' e um COMENTARIO, como em
        praticamente toda linguagem da familia C. So vira divisao inteira nos
        casos em que o que vem depois nao pode ser prosa:

          * um numero        ->  7 // 2
          * um parenteses    ->  x // (a + b)
          * uma chamada,
            indexacao ou
            acesso a membro  ->  (a * b) // mdc(a, b)

        Um identificador solto depois de '//' e tratado como comentario
        ('// backtrack', '// TODO'). Para divisao inteira sem ambiguidade use
        o operador dedicado '~/'.
        """
        if not self.tokens:
            return False
        expr_end = {
            TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.FLOAT,
            TokenType.STRING, TokenType.RPAREN, TokenType.RBRACKET,
            TokenType.RBRACE, TokenType.BOOLEAN, TokenType.VOID,
            TokenType.SELF,
        }
        if self.tokens[-1].type not in expr_end:
            return False

        resto = self.source[self.pos + 2:]
        quebra = resto.find('\n')
        if quebra != -1:
            resto = resto[:quebra]
        depois = resto.lstrip()
        if not depois:
            return False

        primeiro = depois[0]
        if primeiro.isdigit() or primeiro == '(':
            # Um numero depois de '//' quase sempre e divisao — mas
            # '// 200, application/json' e '// 302, temporario' sao
            # comentarios que comecam com numero, e sao comuns em
            # documentacao de HTTP. O que os denuncia e o que vem
            # DEPOIS do numero: uma divisao termina a expressao ali,
            # enquanto a prosa continua com virgula, letra ou dois
            # pontos.
            if not self._numero_e_operando(depois):
                return False
            return True
        if primeiro == '-' and len(depois) > 1 and (depois[1].isdigit() or depois[1] == '('):
            return True

        # Identificador: so e codigo se for chamada, indexacao ou membro.
        if primeiro.isalpha() or primeiro == '_':
            i = 0
            while i < len(depois) and (depois[i].isalnum() or depois[i] == '_'):
                i += 1
            if depois[i:i + 1] not in ('(', '[', '.'):
                return False
            # '// O(n), uma vez' tambem casa com "chamada" — e prosa.
            # O que denuncia e o mesmo de sempre: depois da chamada
            # fechada, uma divisao TERMINA a expressao, e a prosa
            # continua com virgula ou letra.
            return self._chamada_e_operando(depois, i)

        return False

    @staticmethod
    def _chamada_e_operando(depois: str, inicio: int) -> bool:
        """Depois da chamada vem fim de expressao, ou continua a frase?

        'x // mdc(a, b)' e divisao. '// O(n), uma vez' e comentario.
        A diferenca esta no que segue o fecha-parenteses.
        """
        i = inicio
        # Anda ate fechar o que abriu, contando o aninhamento.
        if depois[i] in '([':
            abre, fecha = depois[i], ')' if depois[i] == '(' else ']'
            nivel = 0
            while i < len(depois):
                if depois[i] == abre:
                    nivel += 1
                elif depois[i] == fecha:
                    nivel -= 1
                    if nivel == 0:
                        i += 1
                        break
                i += 1
        else:
            # Acesso a membro: anda pelo nome.
            i += 1
            while i < len(depois) and (depois[i].isalnum() or depois[i] in '_.'):
                i += 1

        resto = depois[i:].lstrip()
        if not resto:
            return True                     # 'x // f(a)'

        # Virgula ou letra depois da chamada e prosa: a expressao teria
        # terminado ali.
        if resto[0].isalpha() or resto[0] == '_':
            return False
        if resto[0] == ',':
            seguinte = resto[1:].lstrip()
            return not (seguinte[:1].isalpha() or seguinte[:1] == '_')
        if resto[0] in '—–…':
            return False
        return True

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
            # '//' is ambiguous in DataForge: it opens a line comment AND is the
            # legacy floor-division operator. Prefer the unambiguous '~/' for
            # floor division; the heuristic below keeps old code working.
            if ch == '/' and self.peek(1) == '/':
                if self._looks_like_floor_div():
                    line, col = self.line, self.column
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.FLOOR_DIV, '//', line, col))
                    continue
                self.skip_comment()
                continue
            if ch == '#':
                self.skip_comment()
                continue
            if ch == '/' and self.peek(1) == '*':
                self.advance()  # skip /
                self.skip_block_comment()
                continue

            # Interpolated string: $"..{expr}.."
            if ch == '$' and self.peek(1) in ('"', "'"):
                self.tokens.append(self.read_interpolated(self.peek(1)))
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

            three = ch + self.peek(1) + self.peek(2)
            if three == '...':
                self.advance(); self.advance(); self.advance()
                self.tokens.append(Token(TokenType.SPREAD, '...', line, col))
                continue

            two = ch + self.peek(1)
            two_char_map = {
                '~/': TokenType.FLOOR_DIV,
                '->': TokenType.ARROW,
                '=>': TokenType.FAT_ARROW,
                '+=': TokenType.PLUS_ASSIGN,
                '-=': TokenType.MINUS_ASSIGN,
                '*=': TokenType.STAR_ASSIGN,
                '/=': TokenType.SLASH_ASSIGN,
                '%=': TokenType.PERCENT_ASSIGN,
                '<=': TokenType.LT_EQ,
                '>=': TokenType.GT_EQ,
                '?.': TokenType.SAFE_DOT,
                '??': TokenType.COALESCE,
            }
            if two in two_char_map:
                self.advance(); self.advance()
                # '~/' is a spelling of the floor-division operator: normalise
                # its value so the parser and interpreter see a single form.
                value = '//' if two == '~/' else two
                self.tokens.append(Token(two_char_map[two], value, line, col))
                continue

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
                '<': TokenType.LT,
                '>': TokenType.GT,
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
    try:
        return lexer.tokenize()
    except DataForgeError as erro:
        # Carimba o arquivo na saida, e nao em cada 'raise': ha varios
        # pontos que levantam SyncError direto, e um deles esquecido
        # devolveria '<stdin>' para um arquivo que tem nome.
        if not erro.filename:
            erro.filename = filename
        raise


#: O que um formato pode ser — a mini-linguagem do 'format'.
#:
#:    [[preenchimento]alinhamento][sinal][#][0][largura][,][.precisao][tipo]
_FORMATO = __import__("re").compile(
    r"^(?:.?[<>^=])?[+\- ]?#?0?\d*[,_]?(?:\.\d+)?[bcdeEfFgGnosxX%]?$")


def _separar_formato(fonte):
    """'x:.2f' -> ('x', '.2f'). Sem formato, devolve ('x', '').

    O ':' e ambiguo em DataForge: ele separa o formato, mas tambem abre
    o corpo de um lambda e de um 'morph'/'sift'. Cortar no primeiro que
    aparece quebraria isto —

        $"nomes: {xs >> morph p: p["n"]}"

    — e foi assim que o exercicio 165 quebrou: o corpo virava 'formato'
    e o 'p' dele, nome indefinido.

    Sao tres condicoes, e todas precisam valer:

    1. O ':' esta FORA de parentese, colchete, chave e aspas.
    2. Nao ha espaco depois dele. Ninguem escreve '{x: .2f}'; todo
       mundo escreve 'morph p: p[...]' com espaco. E a diferenca que a
       propria escrita ja faz.
    3. O que vem depois PARECE um formato — so os caracteres da
       mini-linguagem. Codigo tem letra, colchete e aspas; formato nao.

    A busca e da direita para a esquerda: em '{v["a"]:.2f}' o ':' do
    formato e o ultimo.
    """
    profundidade = 0
    aspas = ""
    candidatos = []
    i = 0
    while i < len(fonte):
        c = fonte[i]
        if aspas:
            if c == "\\":
                i += 2
                continue
            if c == aspas:
                aspas = ""
        elif c in "\"'":
            aspas = c
        elif c in "([{":
            profundidade += 1
        elif c in ")]}":
            profundidade -= 1
        elif c == ":" and profundidade == 0:
            candidatos.append(i)
        i += 1

    for corte in reversed(candidatos):
        esquerda = fonte[:corte].strip()
        direita = fonte[corte + 1:]
        if not esquerda or not direita:
            continue
        if direita[0].isspace():
            continue                     # o ':' de um lambda ou pipeline
        if not _FORMATO.match(direita):
            continue                     # aquilo e codigo, nao formato
        return esquerda, direita
    return fonte, ""
