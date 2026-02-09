"""
DataForge Parser
Converts a token stream into an Abstract Syntax Tree (AST).
Implements recursive descent parsing with indentation-based scoping.
"""

from .tokens import Token, TokenType
from .errors import ParseError
from . import ast_nodes as ast


class Parser:
    """Recursive descent parser for DataForge."""

    def __init__(self, tokens: list[Token], filename: str = "<stdin>"):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0

    # ── Helpers ────────────────────────────────────────────

    def error(self, message: str):
        tok = self.current()
        raise ParseError(message, tok.line, tok.column)

    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None)

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token(TokenType.EOF, None)

    def advance(self) -> Token:
        tok = self.current()
        self.pos += 1
        return tok

    def expect(self, token_type: TokenType, message: str = "") -> Token:
        tok = self.current()
        if tok.type != token_type:
            msg = message or f"Expected {token_type.name}, got {tok.type.name} ({tok.value!r})"
            self.error(msg)
        return self.advance()

    def match(self, *types: TokenType) -> Token | None:
        if self.current().type in types:
            return self.advance()
        return None

    def skip_newlines(self):
        while self.current().type == TokenType.NEWLINE:
            self.advance()

    def at_end(self) -> bool:
        return self.current().type == TokenType.EOF

    # ── Entry Point ────────────────────────────────────────

    def parse(self) -> ast.Program:
        """Parse the full program."""
        self.skip_newlines()
        program = ast.Program(body=[], line=1, column=1)
        while not self.at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                program.body.append(stmt)
            self.skip_newlines()
        return program

    # ── Block parsing ──────────────────────────────────────

    def parse_block(self) -> list:
        """Parse an indented block of statements."""
        self.skip_newlines()
        self.expect(TokenType.INDENT, "Expected indented block")
        stmts = []
        while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self.skip_newlines()
        if self.current().type == TokenType.DEDENT:
            self.advance()
        return stmts

    # ── Statement ──────────────────────────────────────────

    def parse_statement(self):
        """Parse a single statement."""
        self.skip_newlines()
        tok = self.current()
        tt = tok.type

        if tt == TokenType.EOF:
            return None

        # ── mark @Decorator ──
        if tt == TokenType.MARK:
            return self.parse_decorator()

        # ── adopt ──
        if tt == TokenType.ADOPT:
            return self.parse_adopt()

        # ── relay ──
        if tt == TokenType.RELAY:
            return self.parse_relay()

        # ── steady ──
        if tt == TokenType.STEADY:
            return self.parse_steady()

        # ── shadow ──
        if tt == TokenType.SHADOW:
            return self.parse_shadow()

        # ── action ──
        if tt == TokenType.ACTION:
            return self.parse_action()

        # ── async action ──
        if tt == TokenType.ASYNC:
            return self.parse_async_action()

        # ── blueprint ──
        if tt == TokenType.BLUEPRINT:
            return self.parse_blueprint()

        # ── trait ──
        if tt == TokenType.TRAIT:
            return self.parse_trait()

        # ── given ──
        if tt == TokenType.GIVEN:
            return self.parse_given()

        # ── match ──
        if tt == TokenType.MATCH:
            return self.parse_match()

        # ── cycle ──
        if tt == TokenType.CYCLE:
            return self.parse_cycle()

        # ── persist ──
        if tt == TokenType.PERSIST:
            return self.parse_persist()

        # ── perform ──
        if tt == TokenType.PERFORM:
            return self.parse_perform()

        # ── monitor ──
        if tt == TokenType.MONITOR:
            return self.parse_monitor()

        # ── out / emit ──
        if tt == TokenType.OUT or tt == TokenType.EMIT:
            return self.parse_out()

        # ── yield ──
        if tt == TokenType.YIELD:
            return self.parse_yield()

        # ── halt ──
        if tt == TokenType.HALT:
            self.advance()
            self.match(TokenType.NEWLINE)
            return ast.HaltStatement(line=tok.line, column=tok.column)

        # ── skip ──
        if tt == TokenType.SKIP:
            self.advance()
            self.match(TokenType.NEWLINE)
            return ast.SkipStatement(line=tok.line, column=tok.column)

        # ── trigger ──
        if tt == TokenType.TRIGGER:
            return self.parse_trigger()

        # ── delete ──
        if tt == TokenType.DELETE:
            self.advance()
            expr = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.DeleteStatement(target=expr, line=tok.line, column=tok.column)

        # ── assert ──
        if tt == TokenType.ASSERT:
            return self.parse_assert()

        # ── wait ──
        if tt == TokenType.WAIT:
            self.advance()
            expr = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.WaitStatement(duration=expr, line=tok.line, column=tok.column)

        # ── inspect ──
        if tt == TokenType.INSPECT:
            self.advance()
            expr = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.InspectStatement(expression=expr, line=tok.line, column=tok.column)

        # ── thread ──
        if tt == TokenType.THREAD:
            return self.parse_thread()

        # ── channel ──
        if tt == TokenType.CHANNEL:
            return self.parse_channel()

        # ── pulse ──
        if tt == TokenType.PULSE:
            return self.parse_pulse()

        # ── guard ──
        if tt == TokenType.GUARD:
            return self.parse_guard()

        # ── retry ──
        if tt == TokenType.RETRY:
            return self.parse_retry()

        # ── validate ──
        if tt == TokenType.VALIDATE:
            return self.parse_validate()

        # ── propagate ──
        if tt == TokenType.PROPAGATE:
            return self.parse_propagate()

        # ── defer ──
        if tt == TokenType.DEFER:
            return self.parse_defer()

        # ── observe ──
        if tt == TokenType.OBSERVE:
            return self.parse_observe()

        # ── parallel ──
        if tt == TokenType.PARALLEL:
            return self.parse_parallel()

        # ── static ──
        if tt == TokenType.STATIC:
            return self.parse_static()

        # ── Expression statement or assignment ──
        return self.parse_expression_statement()

    # ── Specific Statement Parsers ─────────────────────────

    def parse_decorator(self):
        """mark @Name [→ followed by action/blueprint]"""
        tok = self.advance()  # consume 'mark'
        self.expect(TokenType.AT, "Expected '@' after 'mark'")
        name_tok = self.expect(TokenType.IDENTIFIER, "Expected decorator name")
        decorator = ast.MarkDecorator(name=name_tok.value, line=tok.line, column=tok.column)

        # Optional args
        if self.current().type == TokenType.LPAREN:
            self.advance()
            args = []
            while self.current().type != TokenType.RPAREN:
                args.append(self.parse_expression())
                self.match(TokenType.COMMA)
            self.expect(TokenType.RPAREN)
            decorator.args = args

        self.skip_newlines()

        # The decorated item follows
        next_stmt = self.parse_statement()
        if isinstance(next_stmt, ast.ActionDeclaration):
            next_stmt.decorators.append(decorator)
        elif isinstance(next_stmt, ast.BlueprintDeclaration):
            pass  # could attach decorators to blueprints too
        return next_stmt

    def parse_adopt(self):
        """adopt Module[.Sub] [as Alias]"""
        tok = self.advance()  # consume 'adopt'
        parts = [self.expect(TokenType.IDENTIFIER).value]
        while self.match(TokenType.DOT):
            parts.append(self.expect(TokenType.IDENTIFIER).value)
        module_name = '.'.join(parts)

        alias = ""
        if self.match(TokenType.AS):
            alias = self.expect(TokenType.IDENTIFIER).value

        self.match(TokenType.NEWLINE)
        return ast.AdoptStatement(module=module_name, alias=alias, line=tok.line, column=tok.column)

    def parse_relay(self):
        """relay name1, name2, ..."""
        tok = self.advance()  # consume 'relay'
        names = [self.expect(TokenType.IDENTIFIER).value]
        while self.match(TokenType.COMMA):
            names.append(self.expect(TokenType.IDENTIFIER).value)
        self.match(TokenType.NEWLINE)
        return ast.RelayStatement(names=names, line=tok.line, column=tok.column)

    def parse_steady(self):
        """steady NAME := value"""
        tok = self.advance()  # consume 'steady'
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN, "Expected ':=' after steady name")
        value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.SteadyDeclaration(name=name, value=value, line=tok.line, column=tok.column)

    def parse_shadow(self):
        """shadow NAME := value"""
        tok = self.advance()  # consume 'shadow'
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN, "Expected ':=' after shadow name")
        value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.ShadowDeclaration(name=name, value=value, line=tok.line, column=tok.column)

    def parse_action(self, is_async: bool = False, decorators: list = None):
        """action name(params): block"""
        tok = self.advance()  # consume 'action'

        # Handle decorator-style: action @server.on_request(...)
        if self.current().type == TokenType.AT:
            # This is a decorated route-style action, parse as normal action with special name
            pass

        name = self.expect(TokenType.IDENTIFIER, "Expected action name").value

        self.expect(TokenType.LPAREN, "Expected '(' after action name")
        params, defaults = self._parse_params()
        self.expect(TokenType.RPAREN, "Expected ')'")

        # Allow action signatures without body (trait/abstract methods)
        if self.current().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            self.match(TokenType.NEWLINE)
            return ast.ActionDeclaration(
                name=name, params=params, defaults=defaults, body=[],
                is_async=is_async, decorators=decorators or [],
                line=tok.line, column=tok.column
            )

        self.expect(TokenType.COLON, "Expected ':' after action signature")
        self.match(TokenType.NEWLINE)

        body = self.parse_block()
        return ast.ActionDeclaration(
            name=name, params=params, defaults=defaults, body=body,
            is_async=is_async, decorators=decorators or [],
            line=tok.line, column=tok.column
        )

    def parse_async_action(self):
        """async action name(...):"""
        self.advance()  # consume 'async'
        if self.current().type == TokenType.ACTION:
            return self.parse_action(is_async=True)

        # async: block (standalone async block)
        if self.current().type == TokenType.COLON:
            tok = self.current()
            self.advance()
            self.match(TokenType.NEWLINE)
            body = self.parse_block()
            # Wrap in a nameless async action
            return ast.ActionDeclaration(
                name="<async>", params=[], defaults={}, body=body,
                is_async=True, line=tok.line, column=tok.column
            )
        self.error("Expected 'action' or ':' after 'async'")

    def parse_blueprint(self):
        """blueprint Name [(params)] [extends Parent] [with Trait]: block
        OR blueprint Name [(Parent)]: block  (backward compat)"""
        tok = self.advance()  # consume 'blueprint'
        name = self.expect(TokenType.IDENTIFIER).value
        parents = []
        traits = []
        constructor_params = []

        # Parse optional parenthesized list
        paren_names = []
        if self.match(TokenType.LPAREN):
            while self.current().type != TokenType.RPAREN:
                paren_names.append(self.expect(TokenType.IDENTIFIER).value)
                self.match(TokenType.COMMA)
            self.expect(TokenType.RPAREN)

        # Check what follows to determine meaning of parenthesized names
        if self.current().type == TokenType.EXTENDS:
            # New style: params in parens, extends for parent
            constructor_params = paren_names
            self.advance()  # consume 'extends'
            parents.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                parents.append(self.expect(TokenType.IDENTIFIER).value)
        elif self.current().type == TokenType.WITH:
            # New style: params in parens, with for traits
            constructor_params = paren_names
        elif self.current().type == TokenType.COLON and paren_names:
            # Check if paren_names look like constructor params (used with 'fields' or 'this.')
            # Simple heuristic: if name starts with lowercase, treat as constructor params
            # For backward compat: if name starts with uppercase, treat as parents
            has_lower = any(n[0].islower() for n in paren_names)
            has_upper = any(n[0].isupper() for n in paren_names)
            if has_lower and not has_upper:
                constructor_params = paren_names
            else:
                parents = paren_names

        # Parse 'with' for traits (can appear after extends too)
        if self.current().type == TokenType.WITH:
            self.advance()  # consume 'with'
            traits.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                traits.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.COLON, "Expected ':' after blueprint header")
        self.match(TokenType.NEWLINE)
        body = self.parse_block()

        return ast.BlueprintDeclaration(
            name=name, parents=parents, body=body, traits=traits,
            constructor_params=constructor_params,
            line=tok.line, column=tok.column
        )

    def parse_trait(self):
        """trait Name: method_signatures"""
        tok = self.advance()  # consume 'trait'
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        methods = self.parse_block()
        return ast.TraitDeclaration(name=name, methods=methods, line=tok.line, column=tok.column)

    def parse_given(self):
        """given condition: block [orif condition: block]* [otherwise: block]"""
        tok = self.advance()  # consume 'given'
        condition = self.parse_expression()
        self.expect(TokenType.COLON, "Expected ':' after condition")
        self.match(TokenType.NEWLINE)
        body = self.parse_block()

        orif_blocks = []
        otherwise_body = []

        self.skip_newlines()
        while self.current().type == TokenType.ORIF:
            self.advance()
            orif_cond = self.parse_expression()
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            orif_body = self.parse_block()
            orif_blocks.append((orif_cond, orif_body))
            self.skip_newlines()

        if self.current().type == TokenType.OTHERWISE:
            self.advance()
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            otherwise_body = self.parse_block()

        return ast.GivenBlock(
            condition=condition, body=body,
            orif_blocks=orif_blocks, otherwise_body=otherwise_body,
            line=tok.line, column=tok.column
        )

    def parse_match(self):
        """match expr: point value: ... default: ..."""
        tok = self.advance()  # consume 'match'
        expression = self.parse_expression()
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        self.skip_newlines()
        self.expect(TokenType.INDENT)

        points = []
        default_body = []

        while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.current().type == TokenType.POINT:
                self.advance()
                value = self.parse_expression()
                self.expect(TokenType.COLON)
                self.match(TokenType.NEWLINE)
                point_body = self.parse_block()
                points.append((value, point_body))
            elif self.current().type == TokenType.DEFAULT:
                self.advance()
                self.expect(TokenType.COLON)
                self.match(TokenType.NEWLINE)
                default_body = self.parse_block()
            else:
                break
            self.skip_newlines()

        if self.current().type == TokenType.DEDENT:
            self.advance()

        return ast.MatchBlock(
            expression=expression, points=points, default_body=default_body,
            line=tok.line, column=tok.column
        )

    def parse_cycle(self):
        """cycle var from start to end [step s]: block
           cycle var in collection: block"""
        tok = self.advance()  # consume 'cycle'
        var_name = self.expect(TokenType.IDENTIFIER).value

        if self.match(TokenType.FROM):
            # cycle var from X to Y [step Z]:
            start = self.parse_expression()
            self.expect(TokenType.TO, "Expected 'to' in cycle range")
            end = self.parse_expression()
            step = None
            if self.match(TokenType.STEP):
                step = self.parse_expression()
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            body = self.parse_block()
            return ast.CycleFromTo(
                var=var_name, start=start, end=end, step=step, body=body,
                line=tok.line, column=tok.column
            )
        elif self.match(TokenType.IN):
            # cycle var in collection:
            collection = self.parse_expression()
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            body = self.parse_block()
            return ast.CycleIn(
                var=var_name, collection=collection, body=body,
                line=tok.line, column=tok.column
            )
        else:
            self.error("Expected 'from' or 'in' after cycle variable")

    def parse_persist(self):
        """persist condition: block"""
        tok = self.advance()  # consume 'persist'
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()
        return ast.PersistBlock(condition=condition, body=body, line=tok.line, column=tok.column)

    def parse_perform(self):
        """perform: block persist condition"""
        tok = self.advance()  # consume 'perform'
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()
        self.skip_newlines()
        self.expect(TokenType.PERSIST, "Expected 'persist' after perform block")
        condition = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.PerformBlock(body=body, condition=condition, line=tok.line, column=tok.column)

    def parse_monitor(self):
        """monitor: block [handle [error]: block] [ensure: block]"""
        tok = self.advance()  # consume 'monitor'
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()

        handle_name = "error"
        handle_body = []
        ensure_body = []

        self.skip_newlines()
        if self.current().type == TokenType.HANDLE:
            self.advance()
            if self.current().type == TokenType.IDENTIFIER:
                handle_name = self.advance().value
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            handle_body = self.parse_block()

        self.skip_newlines()
        if self.current().type == TokenType.ENSURE:
            self.advance()
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            ensure_body = self.parse_block()

        return ast.MonitorBlock(
            body=body, handle_name=handle_name, handle_body=handle_body,
            ensure_body=ensure_body, line=tok.line, column=tok.column
        )

    def parse_out(self):
        """out expr1, expr2, ..."""
        tok = self.advance()  # consume 'out'
        expressions = []
        if self.current().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            expressions.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                expressions.append(self.parse_expression())
        self.match(TokenType.NEWLINE)
        return ast.OutStatement(expressions=expressions, line=tok.line, column=tok.column)

    def parse_yield(self):
        """yield [expression]"""
        tok = self.advance()  # consume 'yield'
        value = None
        if self.current().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.YieldStatement(value=value, line=tok.line, column=tok.column)

    def parse_trigger(self):
        """trigger expression"""
        tok = self.advance()  # consume 'trigger'
        value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.TriggerStatement(value=value, line=tok.line, column=tok.column)

    def parse_assert(self):
        """assert condition [, message]"""
        tok = self.advance()  # consume 'assert'
        condition = self.parse_expression()
        message = None
        if self.match(TokenType.COMMA):
            message = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.AssertStatement(condition=condition, message=message, line=tok.line, column=tok.column)

    def parse_thread(self):
        """thread: block"""
        tok = self.advance()  # consume 'thread'
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()
        return ast.ThreadBlock(body=body, line=tok.line, column=tok.column)

    def parse_channel(self):
        """channel name"""
        tok = self.advance()  # consume 'channel'
        name = self.expect(TokenType.IDENTIFIER).value
        self.match(TokenType.NEWLINE)
        return ast.ChannelDeclaration(name=name, line=tok.line, column=tok.column)

    def parse_pulse(self):
        """pulse event, data"""
        tok = self.advance()  # consume 'pulse'
        event = self.parse_expression()
        data = None
        if self.match(TokenType.COMMA):
            data = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.PulseStatement(event=event, data=data, line=tok.line, column=tok.column)

    def parse_guard(self):
        """guard condition, message  OR  guard condition else: block"""
        tok = self.advance()  # consume 'guard'
        condition = self.parse_expression()
        # Check for 'else' keyword (IDENTIFIER "else")
        if self.current().type == TokenType.OTHERWISE:
            self.advance()  # consume 'otherwise' (else alias)
            self.match(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            else_body = self.parse_block()
            return ast.GuardStatement(condition=condition, message=None, else_body=else_body, line=tok.line, column=tok.column)
        elif self.current().type == TokenType.IDENTIFIER and self.current().value == "else":
            self.advance()  # consume 'else'
            self.match(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            else_body = self.parse_block()
            return ast.GuardStatement(condition=condition, message=None, else_body=else_body, line=tok.line, column=tok.column)
        message = None
        if self.match(TokenType.COMMA):
            message = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.GuardStatement(condition=condition, message=message, else_body=[], line=tok.line, column=tok.column)

    def parse_retry(self):
        """retry count: block [handle error: block]"""
        tok = self.advance()  # consume 'retry'
        count = self.parse_expression()
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()

        handle_name = "error"
        handle_body = []
        self.skip_newlines()
        if self.current().type in (TokenType.HANDLE, TokenType.RECOVER):
            self.advance()
            if self.current().type == TokenType.IDENTIFIER:
                handle_name = self.advance().value
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            handle_body = self.parse_block()

        return ast.RetryBlock(
            count=count, body=body,
            handle_name=handle_name, handle_body=handle_body,
            line=tok.line, column=tok.column
        )

    def parse_validate(self):
        """validate expression, message  OR  validate expression otherwise: block"""
        tok = self.advance()  # consume 'validate'
        value = self.parse_expression()
        if self.current().type == TokenType.OTHERWISE:
            self.advance()  # consume 'otherwise'
            self.match(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            else_body = self.parse_block()
            return ast.ValidateStatement(value=value, message=None, else_body=else_body, line=tok.line, column=tok.column)
        message = None
        if self.match(TokenType.COMMA):
            message = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.ValidateStatement(value=value, message=message, else_body=[], line=tok.line, column=tok.column)

    def parse_propagate(self):
        """propagate [expression]"""
        tok = self.advance()  # consume 'propagate'
        value = None
        if self.current().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.PropagateStatement(value=value, line=tok.line, column=tok.column)

    def parse_defer(self):
        """defer: block"""
        tok = self.advance()  # consume 'defer'
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()
        return ast.DeferStatement(body=body, line=tok.line, column=tok.column)

    def parse_observe(self):
        """observe var in source: block"""
        tok = self.advance()  # consume 'observe'
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        source = self.parse_expression()
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()
        return ast.ObserveBlock(source=source, var=var, body=body, line=tok.line, column=tok.column)

    def parse_parallel(self):
        """parallel: block1 block2 ..."""
        tok = self.advance()  # consume 'parallel'
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()
        return ast.ParallelBlock(blocks=body, line=tok.line, column=tok.column)

    def parse_static(self):
        """static name := value"""
        tok = self.advance()  # consume 'static'
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.StaticDeclaration(name=name, value=value, line=tok.line, column=tok.column)

    # ── Expression statement / assignment ──────────────────

    def parse_expression_statement(self):
        """Parse an expression or assignment statement."""
        expr = self.parse_expression()

        # Assignment: target := value
        if self.current().type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.Assignment(target=expr, value=value, line=expr.line, column=expr.column)

        self.match(TokenType.NEWLINE)
        return expr  # Expression statement

    # ── Expression Parsing (Precedence Climbing) ───────────

    def parse_expression(self):
        """Parse a full expression."""
        return self.parse_pipeline()

    def parse_pipeline(self):
        """expr >> sift/morph/distill ..."""
        expr = self.parse_or()

        if self.current().type == TokenType.PIPE:
            ops = []
            while self.match(TokenType.PIPE):
                op = self.parse_pipeline_op()
                ops.append(op)
            return ast.PipelineExpression(source=expr, operations=ops, line=expr.line, column=expr.column)

        return expr

    def parse_pipeline_op(self):
        """Parse sift/morph/distill pipeline operation.
        Supports both inline lambda and named function reference:
          sift param: condition    OR    sift func_name
          morph param: expression  OR    morph func_name
          distill acc, val: expr   OR    distill func_name initial_value
        """
        tok = self.current()

        if self.match(TokenType.SIFT):
            name = self.expect(TokenType.IDENTIFIER).value
            # If next token is COLON, it's inline lambda: sift param: condition
            if self.current().type == TokenType.COLON:
                self.advance()  # skip colon
                condition = self.parse_or()
                return ast.SiftOperation(param=name, condition=condition, line=tok.line, column=tok.column)
            # Otherwise, it's a function reference: sift func_name
            return ast.SiftOperation(func_ref=name, line=tok.line, column=tok.column)

        if self.match(TokenType.MORPH):
            name = self.expect(TokenType.IDENTIFIER).value
            # If next token is COLON, it's inline lambda: morph param: expression
            if self.current().type == TokenType.COLON:
                self.advance()  # skip colon
                expression = self.parse_or()
                return ast.MorphOperation(param=name, expression=expression, line=tok.line, column=tok.column)
            # Otherwise, it's a function reference: morph func_name
            return ast.MorphOperation(func_ref=name, line=tok.line, column=tok.column)

        if self.match(TokenType.DISTILL):
            name = self.expect(TokenType.IDENTIFIER).value
            # Check if next is COMMA or IDENTIFIER followed by COLON → inline lambda
            # Supports: distill acc, val: expr [initial]  AND  distill acc val: expr [initial]
            if self.current().type == TokenType.COMMA:
                self.advance()  # skip comma
                val = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                expression = self.parse_or()
                # Check for optional initial value
                initial = None
                if self.pos < len(self.tokens) and self.current().type not in (
                    TokenType.PIPE, TokenType.NEWLINE, TokenType.EOF,
                    TokenType.RPAREN, TokenType.RBRACKET, TokenType.RBRACE,
                ):
                    initial = self.parse_or()
                return ast.DistillOperation(acc_param=name, val_param=val, expression=expression, initial=initial, line=tok.line, column=tok.column)
            if self.current().type == TokenType.IDENTIFIER and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == TokenType.COLON:
                # Space-separated: distill acc val: expr [initial]
                val = self.advance().value
                self.advance()  # skip colon
                expression = self.parse_or()
                # Check for optional initial value
                initial = None
                if self.pos < len(self.tokens) and self.current().type not in (
                    TokenType.PIPE, TokenType.NEWLINE, TokenType.EOF,
                    TokenType.RPAREN, TokenType.RBRACKET, TokenType.RBRACE,
                ):
                    initial = self.parse_or()
                return ast.DistillOperation(acc_param=name, val_param=val, expression=expression, initial=initial, line=tok.line, column=tok.column)
            # Otherwise, function reference: distill func_name initial_value
            initial = self.parse_or()
            return ast.DistillOperation(func_ref=name, initial=initial, line=tok.line, column=tok.column)

        self.error(f"Expected pipeline operation (sift/morph/distill), got {tok.type.name}")

    def parse_or(self):
        left = self.parse_and()
        while self.current().type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = ast.LogicalOp(left=left, op="or", right=right, line=left.line, column=left.column)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.current().type == TokenType.AND:
            self.advance()
            right = self.parse_not()
            left = ast.LogicalOp(left=left, op="and", right=right, line=left.line, column=left.column)
        return left

    def parse_not(self):
        if self.current().type == TokenType.NOT:
            tok = self.advance()
            operand = self.parse_not()
            return ast.NotOp(operand=operand, line=tok.line, column=tok.column)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()

        comp_types = {
            TokenType.IS: "is",
            TokenType.ISNT: "isnt",
            TokenType.BIGGER: "bigger",
            TokenType.SMALLER: "smaller",
            TokenType.BIGGER_EQ: "bigger_eq",
            TokenType.SMALLER_EQ: "smaller_eq",
            TokenType.EQUAL: "==",
            TokenType.NOT_EQUAL: "!=",
        }

        if self.current().type in comp_types:
            op = comp_types[self.current().type]
            self.advance()
            right = self.parse_addition()
            return ast.ComparisonOp(left=left, op=op, right=right, line=left.line, column=left.column)

        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = ast.BinaryOp(left=left, op=op, right=right, line=left.line, column=left.column)
        return left

    def parse_multiplication(self):
        left = self.parse_power()
        while self.current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.FLOOR_DIV):
            op = self.advance().value
            right = self.parse_power()
            left = ast.BinaryOp(left=left, op=op, right=right, line=left.line, column=left.column)
        return left

    def parse_power(self):
        base = self.parse_unary()
        if self.current().type == TokenType.POWER:
            self.advance()
            exp = self.parse_unary()
            return ast.BinaryOp(left=base, op="**", right=exp, line=base.line, column=base.column)
        return base

    def parse_unary(self):
        if self.current().type == TokenType.MINUS:
            tok = self.advance()
            operand = self.parse_unary()
            return ast.UnaryOp(op="-", operand=operand, line=tok.line, column=tok.column)
        if self.current().type == TokenType.NOT:
            tok = self.advance()
            operand = self.parse_unary()
            return ast.NotOp(operand=operand, line=tok.line, column=tok.column)
        return self.parse_postfix()

    def parse_postfix(self):
        """Handle member access, indexing, and function calls."""
        expr = self.parse_primary()

        while True:
            if self.current().type == TokenType.DOT:
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value

                # Check for method call: obj.method(args)
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args, kwargs = self._parse_call_args()
                    self.expect(TokenType.RPAREN)
                    expr = ast.MethodCall(
                        object=expr, method=member, args=args, kwargs=kwargs,
                        line=expr.line, column=expr.column
                    )
                else:
                    expr = ast.MemberAccess(
                        object=expr, member=member,
                        line=expr.line, column=expr.column
                    )
            elif self.current().type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = ast.IndexAccess(
                    object=expr, index=index,
                    line=expr.line, column=expr.column
                )
            elif self.current().type == TokenType.LPAREN and isinstance(expr, ast.Identifier):
                self.advance()
                args, kwargs = self._parse_call_args()
                self.expect(TokenType.RPAREN)
                expr = ast.FunctionCall(
                    callee=expr, args=args, kwargs=kwargs,
                    line=expr.line, column=expr.column
                )
            else:
                break

        return expr

    def parse_primary(self):
        """Parse primary expressions (literals, identifiers, grouped)."""
        tok = self.current()

        # Integer
        if tok.type == TokenType.INTEGER:
            self.advance()
            return ast.IntegerLiteral(value=tok.value, line=tok.line, column=tok.column)

        # Float
        if tok.type == TokenType.FLOAT:
            self.advance()
            return ast.FloatLiteral(value=tok.value, line=tok.line, column=tok.column)

        # String
        if tok.type == TokenType.STRING:
            self.advance()
            return ast.StringLiteral(value=tok.value, line=tok.line, column=tok.column)

        # Boolean
        if tok.type == TokenType.BOOLEAN:
            self.advance()
            return ast.BooleanLiteral(value=tok.value, line=tok.line, column=tok.column)

        # Void
        if tok.type == TokenType.VOID:
            self.advance()
            return ast.VoidLiteral(line=tok.line, column=tok.column)

        # Self
        if tok.type == TokenType.SELF:
            self.advance()
            expr = ast.Identifier(name="self", line=tok.line, column=tok.column)
            # Allow self.member
            while self.current().type == TokenType.DOT:
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args, kwargs = self._parse_call_args()
                    self.expect(TokenType.RPAREN)
                    expr = ast.MethodCall(object=expr, method=member, args=args, kwargs=kwargs,
                                          line=tok.line, column=tok.column)
                else:
                    expr = ast.MemberAccess(object=expr, member=member, line=tok.line, column=tok.column)
            return expr

        # Root
        if tok.type == TokenType.ROOT:
            self.advance()
            expr = ast.Identifier(name="root", line=tok.line, column=tok.column)
            while self.current().type == TokenType.DOT:
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args, kwargs = self._parse_call_args()
                    self.expect(TokenType.RPAREN)
                    expr = ast.MethodCall(object=expr, method=member, args=args, kwargs=kwargs,
                                          line=tok.line, column=tok.column)
                else:
                    expr = ast.MemberAccess(object=expr, member=member, line=tok.line, column=tok.column)
            return expr

        # Spawn/Forge: spawn/forge ClassName(args)
        if tok.type in (TokenType.SPAWN, TokenType.FORGE):
            self.advance()
            class_expr = self.parse_postfix()
            if isinstance(class_expr, ast.FunctionCall):
                return ast.SpawnExpression(
                    class_name=class_expr.callee, args=class_expr.args,
                    kwargs=class_expr.kwargs, line=tok.line, column=tok.column
                )
            return ast.SpawnExpression(class_name=class_expr, line=tok.line, column=tok.column)

        # Typeof
        if tok.type == TokenType.TYPEOF:
            self.advance()
            operand = self.parse_unary()
            return ast.TypeofExpression(operand=operand, line=tok.line, column=tok.column)

        # Cast: cast expr as Type
        if tok.type == TokenType.CAST:
            self.advance()
            operand = self.parse_unary()
            self.expect(TokenType.AS)
            target = self.expect(TokenType.IDENTIFIER).value
            return ast.CastExpression(operand=operand, target_type=target, line=tok.line, column=tok.column)

        # Await
        if tok.type == TokenType.AWAIT:
            self.advance()
            expr = self.parse_expression()
            return ast.AwaitExpression(expression=expr, line=tok.line, column=tok.column)

        # In (input): in "prompt"
        if tok.type == TokenType.IN:
            self.advance()
            prompt = None
            if self.current().type == TokenType.STRING:
                prompt = self.parse_expression()
            return ast.InExpression(prompt=prompt, line=tok.line, column=tok.column)

        # Frame: frame [[1,2],[3,4]]
        if tok.type == TokenType.FRAME:
            self.advance()
            data = self.parse_primary()
            return ast.FrameExpression(data=data, line=tok.line, column=tok.column)

        # Train: train model using data
        if tok.type == TokenType.TRAIN:
            self.advance()
            model = self.parse_postfix()
            self.expect(TokenType.USING)
            data = self.parse_expression()
            return ast.TrainExpression(model=model, data=data, line=tok.line, column=tok.column)

        # Predict
        if tok.type == TokenType.PREDICT:
            self.advance()
            model = self.parse_postfix()
            self.expect(TokenType.USING)
            data = self.parse_expression()
            return ast.PredictExpression(model=model, data=data, line=tok.line, column=tok.column)

        # List literal: [a, b, c]
        if tok.type == TokenType.LBRACKET:
            return self.parse_list()

        # Dict literal: {key: value, ...}
        if tok.type == TokenType.LBRACE:
            return self.parse_dict()

        # Grouped expression: (expr)
        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')'")
            return expr

        # Identifier
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return ast.Identifier(name=tok.value, line=tok.line, column=tok.column)

        self.error(f"Unexpected token: {tok.type.name} ({tok.value!r})")

    def parse_list(self):
        """Parse [a, b, c]"""
        tok = self.advance()  # [
        elements = []
        while self.current().type != TokenType.RBRACKET:
            self.skip_newlines()
            elements.append(self.parse_expression())
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACKET)
        return ast.ListLiteral(elements=elements, line=tok.line, column=tok.column)

    def parse_dict(self):
        """Parse {key: value, ...}"""
        tok = self.advance()  # {
        pairs = []
        while self.current().type != TokenType.RBRACE:
            self.skip_newlines()
            key = self.parse_expression()
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return ast.DictLiteral(pairs=pairs, line=tok.line, column=tok.column)

    # ── Helper: parse parameters ───────────────────────────

    def _parse_params(self):
        """Parse function parameter list: (a, b, c := default)"""
        params = []
        defaults = {}
        while self.current().type != TokenType.RPAREN:
            name = self.expect(TokenType.IDENTIFIER).value
            params.append(name)
            if self.match(TokenType.ASSIGN):
                defaults[name] = self.parse_expression()
            self.match(TokenType.COMMA)
        return params, defaults

    def _parse_call_args(self):
        """Parse function call arguments: (a, b, key := val)"""
        args = []
        kwargs = {}
        while self.current().type != TokenType.RPAREN:
            # Check for keyword arg: name := value
            if (self.current().type == TokenType.IDENTIFIER and
                    self.peek().type == TokenType.ASSIGN):
                name = self.advance().value
                self.advance()  # skip :=
                value = self.parse_expression()
                kwargs[name] = value
            else:
                args.append(self.parse_expression())
            self.match(TokenType.COMMA)
        return args, kwargs


def parse(tokens: list[Token], filename: str = "<stdin>") -> ast.Program:
    """Convenience function to parse tokens into AST."""
    parser = Parser(tokens, filename)
    return parser.parse()
