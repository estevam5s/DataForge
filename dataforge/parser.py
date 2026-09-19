"""
DataForge Parser
Converts a token stream into an Abstract Syntax Tree (AST).
Implements recursive descent parsing with indentation-based scoping.
"""

from .tokens import KEYWORDS, Token, TokenType
from .errors import DataForgeError, ParseError
from . import ast_nodes as ast


class Parser:
    """Recursive descent parser for DataForge."""

    def __init__(self, tokens: list[Token], filename: str = "<stdin>"):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0
        # Contextos onde certas producoes ficariam ambiguas:
        #  _no_ternary     — 'given' seria guarda/condicao, nao ternario
        #  _no_membership  — 'in' pertence ao cabecalho de cycle/observe
        self._no_ternary = 0
        self._no_membership = 0
        #: Os 'type Nome<T> := …' ja lidos NESTE arquivo. É o que deixa
        #: 'Par<Integer>' ser anotação sem abrir a porta para
        #: 'Integer<String>', que continua sendo erro.
        self._tipos_genericos = {}
        #  _em_server / _em_rota — onde as palavras do Kiln valem
        self._em_server = 0
        self._em_rota = 0
        #  _em_crucible / _em_trial — onde as palavras do Crucible valem
        self._em_crucible = 0
        self._em_trial = 0
        #  _no_with — 'with' abre os dados do render, nao 'record with {…}'
        self._no_with = 0
        self._ultimos_limites = {}
        #: Os erros de sintaxe ja encontrados nesta leitura.
        #:
        #: Um parser que para no primeiro obriga a
        #: corrigir-compilar-corrigir uma vez por erro. Quatro erros num
        #: arquivo davam UMA mensagem, e ela apontava a linha 2 para um
        #: descuido da linha 1 — porque o '+' pendurado no fim da linha 1
        #: so revela o problema quando o ':=' da linha 2 aparece.
        self._erros = []
        #: Quantos reportar antes de desistir. Depois de um certo ponto o
        #: que se le nao sao erros: e o eco de um deles, e uma tela de
        #: cascata esconde o primeiro, que e o unico confiavel.
        self._limite_de_erros = 12

    # ── Helpers ────────────────────────────────────────────

    def error(self, message: str, tok=None):
        tok = tok or self.current()
        raise ParseError(message, tok.line, tok.column)

    def _registrar(self, erro):
        """Guarda o erro, uma vez por linha.

        Uma linha errada costuma produzir varios erros em cascata: o
        primeiro e o diagnostico, os seguintes sao o eco. Guardar so o
        primeiro de cada linha e o que faz a leva ser legivel — sem
        isso, um 'given' sem ':' rendia cinco mensagens sobre a mesma
        linha e empurrava os outros arquivos para fora da tela.
        """
        if any(o.line == erro.line for o in self._erros):
            return
        if len(self._erros) < self._limite_de_erros:
            self._erros.append(erro)

    def _ressincronizar(self):
        """Anda ate o proximo ponto seguro depois de um erro.

        O ponto seguro e o fim da instrucao: a NEWLINE no MESMO nivel de
        recuo em que se estava. Contar INDENT e DEDENT e o que impede a
        recuperacao de sair do bloco por engano — um erro dentro do corpo
        de uma acao nao pode fazer o parser achar que a acao terminou, ou
        o resto do arquivo vira um segundo mar de erros falsos.

        Ao encontrar o DEDENT que fecha o bloco de FORA, para sem
        consumi-lo: quem o consome e o laco de 'parse_block'.
        """
        profundidade = 0
        while not self.at_end():
            tipo = self.current().type
            if tipo is TokenType.INDENT:
                profundidade += 1
            elif tipo is TokenType.DEDENT:
                if profundidade == 0:
                    return
                profundidade -= 1
            elif tipo is TokenType.NEWLINE and profundidade == 0:
                self.advance()
                return
            self.advance()

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

    def continuar_linha(self):
        """Pula a quebra de linha logo apos um operador binario.

        Uma linha que termina em operador esta obviamente incompleta —
        nao ha o que ela possa significar sozinha. Permitir a quebra ali
        deixa escrever uma expressao longa em varias linhas:

            mensagem := "primeira parte " +
                        "segunda parte"

        A indentacao seguinte e ignorada de proposito: o lexer ja emitiu
        INDENT/DEDENT, mas dentro de uma expressao continuada eles nao
        delimitam bloco nenhum.
        """
        while self.current().type in (TokenType.NEWLINE, TokenType.INDENT,
                                      TokenType.DEDENT):
            self.advance()

    def expect_member_name(self) -> str:
        """Expect an identifier or a keyword used as a member name after '.'."""
        tok = self.current()
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return tok.value
        # Allow keywords as member names (e.g., Database.delete, IO.delete)
        if tok.value and isinstance(tok.value, str) and tok.value.isidentifier():
            self.advance()
            return tok.value
        self.error(f"Expected member name after '.', got {tok.type.name} ({tok.value!r})")

    def at_end(self) -> bool:
        return self.current().type == TokenType.EOF

    # ── Entry Point ────────────────────────────────────────

    def parse(self) -> ast.Program:
        """Parse the full program."""
        self.skip_newlines()
        program = ast.Program(body=[], line=1, column=1)
        while not self.at_end():
            marca = self.pos
            try:
                stmt = self.parse_statement()
            except ParseError as erro:
                self._registrar(erro)
                self._ressincronizar()
                # A rede de seguranca: se a recuperacao nao andou, o
                # proximo laco daria o MESMO erro para sempre. Acontece
                # quando o token que ofende e justamente a borda em que
                # '_ressincronizar' para de proposito.
                if self.pos == marca:
                    self.advance()
                self.skip_newlines()
                continue
            if stmt is not None:
                program.body.append(stmt)
            self.skip_newlines()
        if self._erros:
            primeiro = self._erros[0]
            primeiro.outros = self._erros[1:]
            raise primeiro
        return program

    # ── Block parsing ──────────────────────────────────────

    def parse_block(self) -> list:
        """Parse an indented block of statements."""
        self.skip_newlines()
        self.expect(TokenType.INDENT, "Expected indented block")
        stmts = []
        while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
            marca = self.pos
            try:
                stmt = self.parse_statement()
            except ParseError as erro:
                self._registrar(erro)
                self._ressincronizar()
                if self.pos == marca:
                    self.advance()
                self.skip_newlines()
                continue
            if stmt is not None:
                stmts.append(stmt)
            self.skip_newlines()
        if self.current().type == TokenType.DEDENT:
            self.advance()
        return stmts


    # ── Kiln ───────────────────────────────────────────────
    #  As palavras do Kiln nao estao em KEYWORDS: sao reconhecidas
    #  aqui, pelo texto, e so onde fazem sentido. Fora de um bloco
    #  'server', 'route' e 'render' continuam sendo nomes livres.

    def _abre_server(self) -> bool:
        """'server' so abre bloco em 'server <nome> on/at/:'.

        Sem esta confirmacao, 'server := ...' ou 'server(x)' seriam
        lidos como declaracao e o programa quebraria.
        """
        if self.peek(1).type != TokenType.IDENTIFIER:
            return False
        seguinte = self.peek(2)
        if seguinte.type == TokenType.COLON:
            return True
        return (seguinte.type == TokenType.IDENTIFIER
                and seguinte.value in ("on", "at"))

    def _kiln_no_server(self, palavra):
        return {
            "route":      self.parse_route,
            "middleware": self.parse_middleware,
            "after":      self.parse_after,
            "mount":      self.parse_mount,
            "assets":     self.parse_assets,
            "views":      self.parse_views,
        }.get(palavra)

    def _kiln_na_rota(self, palavra):
        return {
            "respond":  self.parse_respond,
            "render":   self.parse_render,
            "redirect": self.parse_redirect,
        }.get(palavra)

    # ── Crucible ───────────────────────────────────────────
    #  Mesma regra do Kiln: as dez palavras do Crucible so tem
    #  sentido dentro de um bloco 'crucible'. Fora dele, 'expect',
    #  'trial' e 'setup' seguem sendo nomes livres — e 'setup' e o
    #  nome do construtor de blueprint, entao tirar seria caro.

    def _abre_crucible(self) -> bool:
        """'crucible' so abre bloco quando o que vem depois confirma.

        Aceita 'crucible "nome":' e 'crucible nome:'. Sem esta
        confirmacao, 'crucible := ...' viraria declaracao de suite.
        """
        seguinte = self.peek(1)
        if seguinte.type not in (TokenType.STRING, TokenType.IDENTIFIER):
            return False
        depois = self.peek(2)
        return depois.type == TokenType.COLON or (
            depois.type == TokenType.IDENTIFIER
            and depois.value in ("tagged", "pending"))

    def _crucible_na_suite(self, palavra):
        return {
            "trial":    self.parse_trial,
            "crucible": self.parse_crucible,
            "fixture":  self.parse_fixture,
            "setup":    lambda: self.parse_hook("setup"),
            "teardown": lambda: self.parse_hook("teardown"),
            "bench":    self.parse_bench,
        }.get(palavra)

    def parse_crucible(self):
        """crucible "<nome>" [tagged ...] [pending "..."]: corpo"""
        tok = self.advance()                       # 'crucible'
        nome = self.parse_expression()
        tags, pendente = self._modificadores_de_suite()
        self.expect(TokenType.COLON, "Expected ':' after the crucible name")

        self._em_crucible += 1
        try:
            corpo = self.parse_block()
        finally:
            self._em_crucible -= 1
        return ast.CrucibleBlock(line=tok.line, column=tok.column,
                                 name=nome, tags=tags, pending=pendente,
                                 body=corpo)

    def _modificadores_de_suite(self):
        tags, pendente = [], None
        while True:
            if self._consumir_palavra("tagged"):
                tags.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    tags.append(self.parse_expression())
            elif self._consumir_palavra("pending"):
                pendente = (self.parse_expression()
                            if self.current().type == TokenType.STRING
                            else ast.StringLiteral(value="pendente"))
            else:
                break
        return tags, pendente

    def parse_trial(self):
        """trial "<nome>" [modificadores]: corpo"""
        tok = self.advance()                       # 'trial'
        nome = self.parse_expression()
        tags, pendente = [], None
        focado = False
        repetir = dentro = sobre = None

        while True:
            if self._consumir_palavra("tagged"):
                tags.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    tags.append(self.parse_expression())
            elif self._consumir_palavra("pending"):
                pendente = (self.parse_expression()
                            if self.current().type == TokenType.STRING
                            else ast.StringLiteral(value="pendente"))
            elif self._consumir_palavra("only"):
                focado = True
            elif self._consumir_palavra("repeat"):
                repetir = self.parse_expression()
            elif self._consumir_palavra("within"):
                dentro = self.parse_expression()
            elif self._consumir_palavra("over"):
                sobre = self.parse_expression()
            else:
                break

        self.expect(TokenType.COLON, "Expected ':' after the trial name")
        self._em_trial += 1
        try:
            corpo = self.parse_block()
        finally:
            self._em_trial -= 1
        return ast.TrialBlock(line=tok.line, column=tok.column, name=nome,
                              tags=tags, pending=pendente, focused=focado,
                              repeat=repetir, within=dentro, over=sobre,
                              body=corpo)

    def parse_fixture(self):
        """fixture <nome>() [scope suite|arquivo]: corpo"""
        tok = self.advance()                       # 'fixture'
        nome = self.expect(TokenType.IDENTIFIER,
                           "Expected a name after 'fixture'").value
        params = []
        if self.match(TokenType.LPAREN):
            while self.current().type != TokenType.RPAREN:
                params.append(self.expect(TokenType.IDENTIFIER,
                                          "Expected a parameter name").value)
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN, "Expected ')'")

        escopo = "trial"
        if self._consumir_palavra("scope"):
            escopo = str(self.advance().value or "trial")

        self.expect(TokenType.COLON, "Expected ':' after the fixture header")
        corpo = self.parse_block()
        return ast.FixtureBlock(line=tok.line, column=tok.column, name=nome,
                                params=params, scope=escopo, body=corpo)

    def parse_provide(self):
        """provide <valor>"""
        tok = self.advance()                       # 'provide'
        valor = None
        if self.current().type not in (TokenType.NEWLINE, TokenType.EOF,
                                       TokenType.DEDENT):
            valor = self.parse_expression()
        return ast.ProvideStatement(line=tok.line, column=tok.column,
                                    value=valor)

    def parse_hook(self, qual):
        """setup: | teardown: | setup all: | teardown all:"""
        tok = self.advance()                       # 'setup' ou 'teardown'
        cada = not self._consumir_palavra("all")
        self.expect(TokenType.COLON, f"Expected ':' after '{qual}'")
        corpo = self.parse_block()
        return ast.HookBlock(line=tok.line, column=tok.column, kind=qual,
                             every=cada, body=corpo)

    def parse_bench(self):
        """bench "<nome>" [times <n>]: corpo"""
        tok = self.advance()                       # 'bench'
        nome = self.parse_expression()
        vezes = None
        if self._consumir_palavra("times"):
            vezes = self.parse_expression()
        self.expect(TokenType.COLON, "Expected ':' after the bench name")
        corpo = self.parse_block()
        return ast.BenchBlock(line=tok.line, column=tok.column, name=nome,
                              times=vezes, body=corpo)

    #: Operador de comparacao -> matcher, para a forma curta
    #: 'expect total is 10' e 'expect n bigger 5'.
    _MATCHER_DE_OPERADOR = {
        "is": "to_be",
        "isnt": "to_not_be",
        "bigger": "to_be_greater_than",
        "smaller": "to_be_less_than",
        "bigger_eq": "to_be_at_least",
        "smaller_eq": "to_be_at_most",
    }

    #: Matchers escritos por palavra: 'expect nome matches "^A"'.
    _MATCHER_CURTO = {
        "matches": "to_match", "raises": "to_raise",
        "has": "to_contain", "near": "to_be_close_to",
        "type": "to_be_a", "length": "to_have_length",
        "starts": "to_start_with", "ends": "to_end_with",
    }

    def parse_expect(self):
        """expect <expr> [<matcher> <arg>]

        A forma longa ('expect(x).to_be(1)') e so uma expressao: o
        'expect' inicial e consumido aqui e o resto vira chamada de
        metodo pelo caminho comum. A curta ('expect x is 1') existe
        porque quatro de cada cinco cobrancas sao igualdade, e
        '.to_be(...)' em volta delas so acrescenta ruido.
        """
        tok = self.advance()                       # 'expect'

        # Forma longa: 'expect(' — devolve a cadeia inteira como
        # expressao, para os matchers encadearem naturalmente.
        if self.current().type == TokenType.LPAREN:
            # Uma expressao solta ja e uma instrucao valida aqui: o
            # interpretador avalia e descarta o valor, e os matchers
            # levantam por conta propria quando nao se cumprem.
            return self._expect_encadeado(tok)

        negado = self._consumir_palavra("not")
        valor = self.parse_expression()
        matcher, args = "", []

        # 'is', 'bigger' e 'in' sao operadores de comparacao: quando o
        # parser chega aqui, 'expect 2 + 2 is 4' ja virou UM no de
        # comparacao, e nao 'expect <2+2>' seguido de 'is 4'.
        #
        # Baixar a precedencia para deixar o 'is' de fora quebraria
        # 'expect a and b' e 'expect x ?? y'. Decompor o no depois
        # custa nada e preserva a expressao inteira nos dois casos.
        if isinstance(valor, ast.ComparisonOp) and \
                valor.op in self._MATCHER_DE_OPERADOR:
            matcher = self._MATCHER_DE_OPERADOR[valor.op]
            args = [valor.right]
            valor = valor.left
        elif isinstance(valor, ast.BinaryOp) and valor.op == "in":
            matcher, args, valor = "to_be_in", [valor.right], valor.left
        else:
            # Forma com palavra: 'expect texto matches "^a"'.
            atual = self.current()
            texto = atual.value if atual.type == TokenType.IDENTIFIER else None
            if texto in self._MATCHER_CURTO:
                self.advance()
                matcher = self._MATCHER_CURTO[texto]
                if self.current().type not in (TokenType.NEWLINE, TokenType.EOF,
                                               TokenType.DEDENT):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())

        return ast.ExpectStatement(line=tok.line, column=tok.column,
                                   value=valor, matcher=matcher, args=args,
                                   negated=negado)

    def _expect_encadeado(self, tok):
        """'(valor).matcher(...)…' — devolve a expressao inteira."""
        self.advance()                             # '('
        valor = self.parse_expression()
        self.expect(TokenType.RPAREN, "Expected ')' after the expected value")
        expr = ast.FunctionCall(
            callee=ast.Identifier(name="__expect__", line=tok.line,
                                  column=tok.column),
            args=[valor], kwargs={}, line=tok.line, column=tok.column)
        while self.current().type == TokenType.DOT:
            self.advance()
            membro = self.advance().value
            args, kwargs = [], {}
            if self.current().type == TokenType.LPAREN:
                self.advance()
                args, kwargs = self._parse_call_args()
                # '_parse_call_args' para NO ')' e deixa o fechamento
                # para quem chamou — como fazem os outros usos dele.
                self.expect(TokenType.RPAREN, "Expected ')' after the matcher")
            expr = ast.MethodCall(object=expr, method=membro, args=args,
                                  kwargs=kwargs, line=tok.line,
                                  column=tok.column)
        return expr

    def _palavra(self, texto) -> bool:
        """A instrucao atual e o identificador <texto>?"""
        tok = self.current()
        return tok.type == TokenType.IDENTIFIER and tok.value == texto

    def _consumir_palavra(self, texto) -> bool:
        if self._palavra(texto):
            self.advance()
            return True
        return False

    def parse_server(self):
        """server <nome> [on <porta>] [at <host>]: corpo"""
        tok = self.advance()                       # 'server'
        nome = self.expect(TokenType.IDENTIFIER,
                           "Expected a name after 'server'").value
        porta = host = None
        while True:
            if self._consumir_palavra("on"):
                porta = self.parse_expression()
            elif self._consumir_palavra("at"):
                host = self.parse_expression()
            else:
                break
        self.expect(TokenType.COLON, "Expected ':' after the server header")

        self._em_server += 1
        try:
            corpo = self.parse_block()
        finally:
            self._em_server -= 1
        return ast.ServerBlock(line=tok.line, column=tok.column, name=nome,
                               port=porta, host=host, body=corpo)

    def parse_route(self):
        """route <VERBO> <caminho>: corpo"""
        from .tokens import VERBOS_KILN
        tok = self.advance()                       # 'route'
        verbo_tok = self.current()
        verbo = str(verbo_tok.value or "").upper()

        # Os verbos chegam como identificadores; 'delete' e palavra
        # reservada e chega como DELETE, dai a segunda checagem.
        if verbo_tok.type == TokenType.DELETE:
            verbo = "DELETE"
            self.advance()
        elif verbo_tok.type == TokenType.IDENTIFIER and verbo in VERBOS_KILN:
            self.advance()
        else:
            aceitos = ", ".join(VERBOS_KILN)
            self.error(f"'{verbo_tok.value}' is not an HTTP verb. "
                       f"Use one of: {aceitos}.")

        caminho = self.parse_expression()
        self.expect(TokenType.COLON, "Expected ':' after the route path")

        self._em_rota += 1
        try:
            corpo = self.parse_block()
        finally:
            self._em_rota -= 1
        return ast.RouteBlock(line=tok.line, column=tok.column,
                              method="ANY" if verbo == "ANY" else verbo,
                              path=caminho, body=corpo)

    def parse_respond(self):
        """respond [status] [json|html|text|file] <expr>"""
        tok = self.advance()                       # 'respond'
        status = None
        # Um inteiro logo apos 'respond' e o status, nunca o corpo:
        # 'respond 404' devolve 404, e 'respond json 404' devolve o
        # numero 404 como JSON.
        if self.current().type == TokenType.INTEGER:
            status = ast.IntegerLiteral(value=self.advance().value)
            # 'respond 404, "nao achei"' — a virgula depois do status e
            # o que se escreve por reflexo, vindo de qualquer framework
            # web. Recusa-la nao ensinava nada: so obrigava a apagar um
            # caractere depois de um erro de sintaxe.
            self.match(TokenType.COMMA)

        tipo = ""
        if self.current().type == TokenType.IDENTIFIER and \
                self.current().value in ("json", "html", "text", "file"):
            tipo = self.advance().value

        valor = None
        if self.current().type not in (TokenType.NEWLINE, TokenType.DEDENT,
                                       TokenType.EOF):
            valor = self.parse_expression()
        elif status is None:
            self.error("'respond' needs a status, a body, or both.")

        return ast.RespondStatement(line=tok.line, column=tok.column,
                                    value=valor, kind=tipo, status=status)

    def parse_render(self):
        """render <template> [with <vault>] [status <n>]"""
        tok = self.advance()                       # 'render'
        # Sem esta guarda, 'render "x" with {…}' seria lido como a
        # expressao 'record with {…}' e o template comeria os dados.
        self._no_with += 1
        try:
            template = self.parse_expression()
        finally:
            self._no_with -= 1
        dados = status = None
        if self.match(TokenType.WITH):
            dados = self.parse_expression()
        if self._consumir_palavra("status"):
            status = self.parse_expression()
        return ast.RenderStatement(line=tok.line, column=tok.column,
                                   template=template, data=dados, status=status)

    def parse_redirect(self):
        """redirect <destino> [status <n>]"""
        tok = self.advance()                       # 'redirect'
        destino = self.parse_expression()
        status = None
        if self._consumir_palavra("status"):
            status = self.parse_expression()
        return ast.RedirectStatement(line=tok.line, column=tok.column,
                                     target=destino, status=status)

    def parse_middleware(self):
        """middleware <expr>"""
        tok = self.advance()
        return ast.MiddlewareStatement(line=tok.line, column=tok.column,
                                       value=self.parse_expression())

    def parse_after(self):
        """after <expr> — middleware que roda DEPOIS, com a resposta."""
        tok = self.advance()
        return ast.MiddlewareStatement(line=tok.line, column=tok.column,
                                       value=self.parse_expression(),
                                       depois=True)

    def parse_mount(self):
        """mount <server> at <prefixo>"""
        tok = self.advance()
        alvo = self.parse_expression()
        prefixo = None
        if self._consumir_palavra("at"):
            prefixo = self.parse_expression()
        else:
            self.error("'mount' needs a prefix: mount admin at \"/admin\"")
        return ast.MountStatement(line=tok.line, column=tok.column,
                                  value=alvo, prefix=prefixo)

    def parse_assets(self):
        """assets <prefixo> from <pasta>"""
        tok = self.advance()
        prefixo = self.parse_expression()
        if not self.match(TokenType.FROM):
            self.error("'assets' needs a folder: assets \"/static\" from \"./www\"")
        pasta = self.parse_expression()
        return ast.AssetsStatement(line=tok.line, column=tok.column,
                                   prefix=prefixo, folder=pasta)

    def parse_views(self):
        """views <pasta>"""
        tok = self.advance()
        return ast.ViewsStatement(line=tok.line, column=tok.column,
                                  folder=self.parse_expression())

    def parse_ignite(self):
        """ignite <server> [on <porta>] [at <host>]"""
        tok = self.advance()                       # 'ignite'
        # Uma expressao, nao so um nome: o server pode vir de um modulo
        # ('ignite App.loja'), que e como um projeto de verdade separa
        # quem monta de quem acende.
        alvo = self.parse_expression()
        porta = host = None
        while True:
            if self._consumir_palavra("on"):
                porta = self.parse_expression()
            elif self._consumir_palavra("at"):
                host = self.parse_expression()
            else:
                break
        return ast.IgniteStatement(line=tok.line, column=tok.column,
                                   target=alvo, port=porta, host=host)

    # ── Statement ──────────────────────────────────────────

    def parse_statement(self):
        """Parse a single statement."""
        self.skip_newlines()
        tok = self.current()
        tt = tok.type

        if tt == TokenType.EOF:
            return None

        # ── Kiln: 'server nome …:' e 'ignite nome' ──
        if tt == TokenType.IDENTIFIER and tok.value == "server" \
                and self._abre_server():
            return self.parse_server()
        if tt == TokenType.IDENTIFIER and tok.value == "ignite" \
                and self.peek(1).type == TokenType.IDENTIFIER:
            return self.parse_ignite()

        # ── Kiln: palavras validas dentro de 'server' ──
        if self._em_server and tt == TokenType.IDENTIFIER:
            producao = self._kiln_no_server(tok.value)
            if producao is not None:
                return producao()

        # ── Kiln: palavras validas dentro de 'route' ──
        if self._em_rota and tt == TokenType.IDENTIFIER:
            producao = self._kiln_na_rota(tok.value)
            if producao is not None:
                return producao()

        # ── 'comptime …' — o que roda na carga ──
        if tt == TokenType.IDENTIFIER and tok.value == "comptime" \
                and self._abre_comptime():
            return self.parse_comptime()

        # ── 'type Nome := …' e 'opaque type Nome := …' ──
        if tt == TokenType.IDENTIFIER and tok.value in ("type", "opaque") \
                and self._abre_tipo():
            return self.parse_declaracao_de_tipo()

        # ── Crucible: 'crucible "nome":' abre a suite ──
        if tt == TokenType.IDENTIFIER and tok.value == "crucible" \
                and self._abre_crucible():
            return self.parse_crucible()

        # ── Crucible: palavras validas dentro da suite ──
        if self._em_crucible and tt == TokenType.IDENTIFIER:
            producao = self._crucible_na_suite(tok.value)
            if producao is not None:
                return producao()
            if tok.value == "provide":
                return self.parse_provide()
            if tok.value == "expect":
                return self.parse_expect()

        # ── @Decorador (com ou sem 'mark' antes) ──
        if tt == TokenType.AT or (tt == TokenType.MARK
                                  and self.peek(1).type == TokenType.AT):
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

        # ── abstract / final / sealed / meta blueprint ──
        if tt == TokenType.IDENTIFIER and self._modificadores_antes_de_blueprint():
            return self.parse_blueprint_com_modificadores()

        # ── contract Nome: ── (contextual: so quando um nome vem depois)
        if (tt == TokenType.IDENTIFIER and tok.value == "contract"
                and self.peek(1).type == TokenType.IDENTIFIER
                and self.peek(2).type in (TokenType.COLON, TokenType.LT,
                                          TokenType.EXTENDS)):
            return self.parse_contract()

        # ── augment Nome: ──
        if (tt == TokenType.IDENTIFIER and tok.value == "augment"
                and self.peek(1).type == TokenType.IDENTIFIER
                and self.peek(2).type == TokenType.COLON):
            return self.parse_augment()

        # ── overload action f(...) ── (no topo do arquivo)
        if (tt == TokenType.IDENTIFIER and tok.value == "overload"
                and self.peek(1).type == TokenType.ACTION):
            self.advance()
            decl = self.parse_action()
            decl.is_overload = True
            return decl

        # ── invariant fora de um blueprint: lido, para a mensagem certa ──
        if tt == TokenType.IDENTIFIER and self._abre_condicao("invariant"):
            return self._parse_condicao_com_mensagem(ast.InvariantStatement,
                                                     "invariant")

        # ── expects cond / promises cond ──
        if tt == TokenType.IDENTIFIER and self._abre_condicao("expects"):
            return self.parse_expects()
        if tt == TokenType.IDENTIFIER and self._abre_condicao("promises"):
            return self.parse_promises()

        # ── record ──
        if tt == TokenType.RECORD:
            return self.parse_record()

        # ── enum ──
        if tt == TokenType.ENUM:
            return self.parse_enum()

        # ── stream action (generator) ──
        if tt == TokenType.STREAM and self.peek().type == TokenType.ACTION:
            self.advance()
            return self.parse_action(is_generator=True)

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

        # ── out ──
        if tt == TokenType.OUT:
            return self.parse_out()

        # ── emit ──
        if tt == TokenType.EMIT:
            return self.parse_emit()

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

        # ── with recurso as nome: ──
        # So quando 'with' ABRE a instrucao. No meio de uma expressao
        # ele continua sendo o operador de record ('p with {…}'), que e
        # o uso muito mais frequente.
        if tt == TokenType.WITH:
            return self.parse_with()

        # ── static ──
        if tt == TokenType.STATIC:
            return self.parse_static()

        # ── Expression statement or assignment ──
        return self.parse_expression_statement()

    # ── Specific Statement Parsers ─────────────────────────

    def parse_um_decorador(self):
        """Um '@Nome' ou '@Nome(argumentos)'.

        Aceita nome pontuado ('@Http.Get') e argumentos nomeados
        ('@Rota(metodo: "GET")') — os dois aparecem em qualquer
        framework que use decoradores para configurar.
        """
        tok = self.expect(TokenType.AT, "Expected '@'")

        partes = [self.expect_member_name()]
        while self.current().type is TokenType.DOT:
            self.advance()
            partes.append(self.expect_member_name())

        decorador = ast.MarkDecorator(name=".".join(partes),
                                      line=tok.line, column=tok.column)

        if self.current().type is TokenType.LPAREN:
            self.advance()
            self.skip_newlines()
            args, kwargs = [], {}
            while self.current().type is not TokenType.RPAREN:
                # Argumento nomeado, nas DUAS formas.
                #
                # 'nome := valor' e o que o resto da linguagem usa —
                # '_parse_call_args' aceita so essa — e o decorador
                # aceitava so 'nome: valor'. A divergencia nao produzia
                # erro em nenhum dos dois lados: produzia um
                # 'mark @V.cache(validade := 300)' que nao compila,
                # escrito na documentacao por quem conhecia a forma
                # comum.
                if (self.current().type is TokenType.IDENTIFIER
                        and self.peek(1).type in (TokenType.COLON,
                                                  TokenType.ASSIGN)):
                    chave = self.advance().value
                    self.advance()                 # ':' ou ':='
                    self._recusar_nomeado_repetido(kwargs, chave)
                    kwargs[chave] = self.parse_expression()
                elif self.current().type is TokenType.SPREAD:
                    marca = self.advance()
                    args.append(ast.SpreadElement(
                        value=self.parse_expression(),
                        line=marca.line, column=marca.column))
                else:
                    args.append(self.parse_expression())
                self.skip_newlines()
                if not self.match(TokenType.COMMA):
                    break
                self.skip_newlines()
            self.expect(TokenType.RPAREN,
                        "Expected ')' closing the decorator arguments")
            decorador.args = args
            decorador.kwargs = kwargs

        return decorador

    def parse_decorator(self):
        """Uma pilha de decoradores, e o que eles decoram.

            @Injetavel
            @Rota("/itens")
            action listar():
                ...

        O 'mark' antes do '@' e opcional — ele existia porque o parser
        antigo precisava de uma palavra para se orientar. Hoje '@' basta,
        e 'mark @Nome' continua funcionando para nao quebrar o que ja
        foi escrito.
        """
        if self.current().type is TokenType.MARK:
            self.advance()

        decoradores = [self.parse_um_decorador()]
        self.skip_newlines()

        # Uma pilha: cada '@' seguinte se acumula sobre o mesmo alvo.
        while (self.current().type is TokenType.AT
               or (self.current().type is TokenType.MARK
                   and self.peek(1).type is TokenType.AT)):
            if self.current().type is TokenType.MARK:
                self.advance()
            decoradores.append(self.parse_um_decorador())
            self.skip_newlines()

        alvo = self.parse_statement()

        if isinstance(alvo, (ast.ActionDeclaration, ast.BlueprintDeclaration,
                             ast.RecordDeclaration)):
            alvo.decorators = list(decoradores) + list(
                getattr(alvo, "decorators", []) or [])
            return alvo

        # Um decorador sobre outra coisa nao tem o que fazer, e calar
        # seria pior: quem escreveu espera que ele valha alguma coisa.
        nomes = ", ".join("@" + d.name for d in decoradores)
        tipo = type(alvo).__name__ if alvo else "nada"
        self.error(
            f"{nomes} não pode decorar isto ({tipo}). "
            f"Decoradores valem para 'action', 'blueprint' e 'record'.")

    def parse_adopt(self):
        """adopt Modulo[.Sub] [as Alias]
           adopt {nome1, nome2 as apelido} from Modulo    (import seletivo)
           adopt Modulo.{nome1, nome2}                    (forma compacta)
        """
        tok = self.advance()  # consume 'adopt'

        # adopt {a, b as c} from Modulo
        if self.current().type == TokenType.LBRACE:
            selecao = self._parse_selecao()
            self.expect(TokenType.FROM, "Expected 'from' after the selected names")
            # Caminho relativo PRIMEIRO, como 'parse_relay' ja fazia.
            #
            # Sem isto, 'adopt {somar} from ./calculadora' nao compilava
            # enquanto 'adopt {sqrt} from Arcane.Math' compilava: a
            # forma que a pessoa aprende na documentacao da biblioteca
            # nao servia para o proprio projeto dela, e a mensagem
            # ("Expected the module name") nao dizia por que.
            modulo = self._parse_caminho_relativo()
            if modulo is None:
                modulo = self._parse_caminho_de_modulo()
            self.match(TokenType.NEWLINE)
            return ast.AdoptStatement(module=modulo, alias="", selection=selecao,
                                      line=tok.line, column=tok.column)

        # adopt ./util  |  adopt ../compartilhado/config  |  adopt "caminho"
        caminho_relativo = self._parse_caminho_relativo()
        if caminho_relativo is not None:
            selecao = None
            if self.current().type == TokenType.DOT and \
                    self.peek(1).type == TokenType.LBRACE:
                self.advance()
                selecao = self._parse_selecao()
            alias = ""
            if self.match(TokenType.AS):
                alias = self.expect(TokenType.IDENTIFIER,
                                    "Expected the alias name after 'as'").value
            self.match(TokenType.NEWLINE)
            return ast.AdoptStatement(
                module=caminho_relativo, alias=alias, selection=selecao,
                line=tok.line, column=tok.column)

        # O nome NU tambem cola o hifen: 'dataforge init minha-lib' cria um
        # pacote chamado 'minha-lib', e 'adopt minha-lib' nao compilava —
        # a linguagem criava um pacote que ela mesma nao conseguia
        # importar pelo nome, que e justamente como o teste de uma
        # biblioteca precisa importa-la. O caminho relativo ja colava.
        if self.current().type is TokenType.IDENTIFIER:
            partes = [self._segmento_de_caminho()]
        else:
            partes = [self.expect(TokenType.IDENTIFIER,
                                  "Expected the module name after 'adopt'.\n"
                                  "    Use a name (adopt Arcane.Math), a relative "
                                  "path (adopt ./util) or a selection "
                                  "(adopt {a, b} from M).").value]
        selecao = None
        while self.match(TokenType.DOT):
            # adopt Arcane.Math.{sqrt, floor}
            if self.current().type == TokenType.LBRACE:
                selecao = self._parse_selecao()
                break
            partes.append(self.expect_member_name())
        modulo = '.'.join(partes)

        alias = ""
        if self.match(TokenType.AS):
            alias = self.expect(TokenType.IDENTIFIER,
                                "Expected the alias name after 'as'").value

        self.match(TokenType.NEWLINE)
        return ast.AdoptStatement(module=modulo, alias=alias, selection=selecao,
                                  line=tok.line, column=tok.column)

    def _parse_caminho_relativo(self):
        """Le './x', '../y/z' ou "caminho" — ou devolve None se nao e isso.

        Um caminho relativo comeca sempre por '.' ou '..', que o lexer
        entrega como DOT ou SPREAD ('...' seria tres, mas '..' vem como
        dois DOT). Assim './util' se distingue de 'util' sem ambiguidade.
        """
        # forma literal: adopt "src/util.df"
        if self.current().type == TokenType.STRING:
            return self.advance().value

        if self.current().type != TokenType.DOT:
            return None

        pedacos = []
        while self.current().type == TokenType.DOT:
            self.advance()
            if self.current().type == TokenType.DOT:      # '..'
                self.advance()
                pedacos.append("..")
            else:
                pedacos.append(".")
            if self.current().type == TokenType.SLASH:
                self.advance()
            else:
                break

        if not pedacos:
            return None

        # o resto: nomes separados por '/'
        nomes = []
        while self.current().type == TokenType.IDENTIFIER:
            nomes.append(self._segmento_de_caminho())
            if self.current().type == TokenType.SLASH:
                self.advance()
                continue
            break

        if not nomes:
            self.error("Expected a path after "
                       f"'{'/'.join(pedacos)}', as in 'adopt ./util'")
        return "/".join(pedacos + nomes)

    def _segmento_de_caminho(self):
        """Um pedaco de caminho: 'util', 'minha-lib', 'v2', 'util.df'.

        O hifen e o ponto fazem parte do NOME DO ARQUIVO, e o lexer nao
        tem como saber disso — ele entrega MINUS e DOT, que em qualquer
        outro lugar sao operadores.

        Sem isto, 'adopt ./minha-lib as L' nao compilava: o loop paravan
        no MINUS e o parser reclamava de 'as' inesperado. E hifen em
        nome de pasta e comum — os projetos deste repositorio se chamam
        'analise-vendas' e 'api-links'.

        A colagem exige ADJACENCIA de coluna. 'adopt ./a - b' continua
        sendo erro, e nao um caminho chamado 'a-b': sem essa guarda, uma
        subtracao escrita com espaco viraria nome de arquivo.
        """
        primeiro = self.advance()
        partes = [str(primeiro.value)]
        fim = primeiro.column + len(str(primeiro.value))

        while True:
            atual = self.current()
            if atual.column != fim:
                break            # ha espaco: acabou o segmento
            if atual.type == TokenType.MINUS:
                seguinte = self.peek(1)
                # Um '-' solto no fim nao e nome de arquivo.
                if seguinte is None or \
                        seguinte.type not in (TokenType.IDENTIFIER,
                                              TokenType.INTEGER) or \
                        seguinte.column != atual.column + 1:
                    break
                self.advance()
                valor = self.advance()
                partes.append("-" + str(valor.value))
                fim = valor.column + len(str(valor.value))
                continue
            if atual.type == TokenType.INTEGER:
                self.advance()
                partes.append(str(atual.value))
                fim = atual.column + len(str(atual.value))
                continue
            if atual.type == TokenType.DOT:
                # './util.df' — a extensao. So quando o que vem depois
                # e um nome colado; senao o DOT pertence a outra coisa.
                seguinte = self.peek(1)
                if seguinte is None or \
                        seguinte.type != TokenType.IDENTIFIER or \
                        seguinte.column != atual.column + 1:
                    break
                self.advance()
                valor = self.advance()
                partes.append("." + str(valor.value))
                fim = valor.column + len(str(valor.value))
                continue
            break

        return "".join(partes)

    def _parse_selecao(self):
        """{nome, outro as apelido} — a lista de nomes importados."""
        self.expect(TokenType.LBRACE)
        selecao = []
        while self.current().type != TokenType.RBRACE:
            self.skip_newlines()
            nome = self.expect_member_name()
            apelido = nome
            if self.match(TokenType.AS):
                apelido = self.expect(TokenType.IDENTIFIER,
                                      "Expected the alias name after 'as'").value
            selecao.append((nome, apelido))
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        if not selecao:
            self.error("Empty selection: name at least one symbol to import")
        return selecao

    def _parse_caminho_de_modulo(self):
        partes = [self.expect(TokenType.IDENTIFIER, "Expected the module name").value]
        while self.match(TokenType.DOT):
            partes.append(self.expect_member_name())
        return '.'.join(partes)

    def parse_relay(self):
        """relay nome1, nome2, …   |   relay from ./modulo"""
        tok = self.advance()  # consume 'relay'

        # relay from ./util — re-exporta tudo o que aquele modulo exporta
        if self.current().type == TokenType.FROM:
            self.advance()
            origem = self._parse_caminho_relativo()
            if origem is None:
                origem = self._parse_caminho_de_modulo()
            self.match(TokenType.NEWLINE)
            return ast.RelayStatement(names=[], origem=origem,
                                      line=tok.line, column=tok.column)

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

    def parse_action(self, is_async: bool = False, decorators: list = None,
                     is_generator: bool = False, sem_corpo: bool = False):
        """action name(params): block

        Com sem_corpo=True (metodo abstrato), aceita a assinatura sozinha:
        'abstract action falar()' declara o contrato sem implementar.
        """
        tok = self.advance()  # consume 'action'

        # Handle decorator-style: action @server.on_request(...)
        if self.current().type == TokenType.AT:
            # This is a decorated route-style action, parse as normal action with special name
            pass

        name = self.expect(TokenType.IDENTIFIER, "Expected action name").value
        # 'action primeiro<T>(lista) -> T:' — acao generica.
        tipos = self._parse_parametros_de_tipo()
        limites = dict(self._ultimos_limites) if tipos else {}

        self.expect(TokenType.LPAREN, "Expected '(' after action name")
        params, defaults, param_types = self._parse_params()
        self.expect(TokenType.RPAREN, "Expected ')'")

        # Optional return type: -> Type
        return_type = ""
        if self.match(TokenType.ARROW):
            return_type = self._parse_nome_de_tipo(
                "Expected a return type after '->'")

        # Allow action signatures without body (trait/abstract methods)
        if self.current().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            self.match(TokenType.NEWLINE)
            return ast.ActionDeclaration(
                name=name, params=params, defaults=defaults, body=[],
                is_async=is_async, decorators=decorators or [],
                type_params=tipos, type_bounds=limites,
                param_types=param_types, return_type=return_type,
                is_generator=is_generator,
                line=tok.line, column=tok.column
            )

        self.expect(TokenType.COLON, "Expected ':' after action signature")
        # Um metodo abstrato pode terminar aqui mesmo, sem ':' nem bloco.
        if sem_corpo and self.current().type in (TokenType.NEWLINE,
                                                 TokenType.DEDENT,
                                                 TokenType.EOF):
            self.match(TokenType.NEWLINE)
            return ast.ActionDeclaration(
                name=name, params=params, defaults=defaults, body=[],
                is_async=is_async, decorators=decorators or [],
                type_params=tipos, type_bounds=limites,
                param_types=param_types, return_type=return_type,
                is_generator=is_generator, is_abstract=True,
                line=tok.line, column=tok.column
            )

        self.match(TokenType.NEWLINE)

        body = self.parse_block()
        # 'promises' no topo do corpo sai do corpo: ele nao roda onde esta
        # escrito, roda na SAIDA. Deixa-lo no corpo o faria rodar antes do
        # trabalho, e a pos-condicao testaria o estado de ANTES.
        promessas = [s for s in body if isinstance(s, ast.PromisesStatement)]
        if promessas:
            body = [s for s in body if not isinstance(s, ast.PromisesStatement)]
            if is_generator:
                self.error(f"'promises' has no single result to check in a "
                           f"stream action: '{name}' emits many. Check each "
                           f"item where it is produced.", promessas[0])
        return ast.ActionDeclaration(
            name=name, params=params, defaults=defaults, body=body,
            is_async=is_async, decorators=decorators or [],
            type_params=tipos, type_bounds=limites,
            param_types=param_types, return_type=return_type,
            is_generator=is_generator, postconditions=promessas,
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

    def _abre_comptime(self):
        """'comptime' so vira palavra quando abre bloco ou prefixa algo.

        'comptime := 3' e 'action comptime(x)' continuam sendo codigo
        comum: a declaracao exige ':' (bloco) ou uma instrucao logo
        depois — e nunca ':=' nem '(' colado.
        """
        depois = self.peek(1)
        if depois.type is TokenType.COLON:
            return True
        if depois.type in (TokenType.ASSIGN, TokenType.LPAREN,
                           TokenType.NEWLINE, TokenType.EOF, TokenType.DOT,
                           TokenType.COMMA, TokenType.RPAREN):
            return False
        if depois.type in self.COMPOUND_ASSIGN:
            return False
        # 'comptime NOME := …', 'comptime steady …', 'comptime assert …'
        if depois.type is TokenType.IDENTIFIER:
            return self.peek(2).type in (TokenType.ASSIGN, TokenType.COLON)
        return depois.type in (TokenType.STEADY, TokenType.ASSERT,
                               TokenType.ACTION, TokenType.STATIC)

    def parse_comptime(self):
        """comptime <instrucao>, ou 'comptime:' com bloco indentado."""
        tok = self.advance()                      # 'comptime'
        if self.match(TokenType.COLON):
            self.match(TokenType.NEWLINE)
            corpo = self.parse_block()
            return ast.ComptimeBlock(body=corpo, line=tok.line,
                                     column=tok.column)
        instrucao = self.parse_statement()
        return ast.ComptimeBlock(body=[instrucao] if instrucao else [],
                                 line=tok.line, column=tok.column)

    def _abre_tipo(self):
        """'type' e 'opaque' so viram palavra quando a linha confirma.

        'type := 3', 'action type(x)', 'opaque.valor' e 'v["type"]'
        continuam sendo codigo comum: a declaracao exige um NOME logo
        depois, e um ':=' (ou um '<' de generico) depois dele.
        """
        i = 0
        if self.peek(i).value == "opaque":
            if self.peek(i + 1).type is not TokenType.IDENTIFIER \
                    or self.peek(i + 1).value != "type":
                return False
            i += 1
        if self.peek(i + 1).type is not TokenType.IDENTIFIER:
            return False
        depois = self.peek(i + 2).type
        # NEWLINE e EOF entram de proposito: 'type Id' sozinho nao e
        # expressao nenhuma, e cair aqui rende "faltou ':='" em vez de
        # "Unexpected token".
        return depois in (TokenType.ASSIGN, TokenType.LT,
                          TokenType.NEWLINE, TokenType.EOF)

    def parse_declaracao_de_tipo(self):
        """type Nome := Base | Outro where regra   ·   opaque type Nome := …"""
        from .tipos_nomeados import separar_uniao
        tok = self.current()
        opaco = False
        if tok.value == "opaque":
            self.advance()
            opaco = True
        self.advance()                                   # 'type'
        nome = self.expect(TokenType.IDENTIFIER,
                           "Expected the type name after 'type'").value
        parametros = self._parse_parametros_de_tipo()
        if parametros:
            self._tipos_genericos[nome] = len(parametros)
        self.expect(TokenType.ASSIGN,
                    f"Expected ':=' after 'type {nome}' — a type is declared "
                    f"like a value: 'type {nome} := Integer'")
        tipo = self._parse_tipo_composto(f"Expected a type after 'type {nome} :='")
        especie, partes = separar_uniao(tipo)

        regra = regra_texto = None
        if self.current().type is TokenType.IDENTIFIER \
                and self.current().value == "where":
            self.advance()
            if self.current().type in (TokenType.NEWLINE, TokenType.EOF):
                self.error("Expected a rule after 'where', written about "
                           "'valor' — as in 'where valor bigger 0'")
            inicio = self.pos
            regra = self.parse_expression()
            regra_texto = self._texto_dos_tokens(inicio, self.pos)
            if not regra_texto:
                self.error("Expected a rule after 'where', written about "
                           "'valor' — as in 'where valor bigger 0'")
        self.match(TokenType.NEWLINE)
        return ast.TypeDeclaration(
            name=nome, especie=especie, partes=partes, type_params=parametros,
            regra=regra, regra_texto=regra_texto or "", opaco=opaco,
            line=tok.line, column=tok.column)

    #: Onde NAO cabe espaco ao remontar o texto de uma regra.
    _SEM_ESPACO_ANTES = {")", "]", ",", ":", "."}
    _SEM_ESPACO_DEPOIS = {"(", "[", "."}
    #: Depois destes, '(' e '[' sao chamada e indice — e colam.
    _COLAM_ABERTURA = (TokenType.IDENTIFIER, TokenType.RPAREN,
                       TokenType.RBRACKET, TokenType.STRING)

    def _texto_dos_tokens(self, inicio, fim):
        """A regra do 'where', como ela foi escrita — para a mensagem.

        A mensagem de um refinamento mostra a regra ('valor bigger 0'), e
        sem ela o erro diria apenas que o valor nao serve, sem dizer por
        que. Remontar dos tokens custa nada e nao exige guardar a fonte.
        """
        pedacos = []
        anterior = None
        for indice in range(inicio, min(fim, len(self.tokens))):
            token = self.tokens[indice]
            if token.type in (TokenType.NEWLINE, TokenType.EOF,
                              TokenType.INDENT, TokenType.DEDENT):
                continue
            texto = token.value
            if token.type is TokenType.STRING:
                texto = f'"{texto}"'
            texto = str(texto)
            colado = (texto in ("(", "[") and anterior is not None
                      and anterior in self._COLAM_ABERTURA)
            if pedacos and not colado and texto not in self._SEM_ESPACO_ANTES \
                    and pedacos[-1] not in self._SEM_ESPACO_DEPOIS:
                pedacos.append(" ")
            pedacos.append(texto)
            anterior = token.type
        return "".join(pedacos).strip()

    def _parse_tipo_composto(self, mensagem):
        """O tipo de uma declaracao. A uniao vale em toda anotacao, e
        quem a le e o proprio '_parse_nome_de_tipo'."""
        return self._parse_nome_de_tipo(mensagem)

    def _juntar_tipos(self, primeiro):
        """'A | B' e 'A & B'.

        Os dois nao se misturam: 'A | B & C' seria lido de duas formas, e
        o parser recusa em vez de escolher uma calado. A linguagem nao
        tem parenteses de tipo — quem precisa do outro agrupamento
        declara um 'type' para a metade e usa o nome dele aqui.
        """
        partes = [primeiro]
        simbolo = None
        while self.current().type in (TokenType.VBAR, TokenType.AMP):
            atual = self.current()
            if simbolo is not None and atual.type is not simbolo:
                self.error(
                    "'|' and '&' cannot be mixed in the same type: write a "
                    "'type' for one of the halves and use its name here.",
                    atual)
            simbolo = atual.type
            self.advance()
            partes.append(self._parse_nome_de_tipo(
                f"Expected a type after '{atual.value}'"))
        juncao = " | " if simbolo is TokenType.VBAR else " & "
        return juncao.join(partes) if len(partes) > 1 else partes[0]

    def _parse_parametros_de_tipo(self):
        """<T>, <K, V> — os parametros de tipo de um generico.

        O analisador estatico os trata como nomes de tipo validos dentro
        da declaracao; o interpretador os ignora, porque a linguagem e
        de tipagem dinamica. Isso e o mesmo que TypeScript faz ao
        compilar: os tipos somem, e o que fica e a documentacao mais o
        que o analisador conseguiu provar.

        Sem isto, 'blueprint Caixa<T>:' era erro de sintaxe, e quem vem
        de Java ou TypeScript batia nele na primeira tentativa.
        """
        if self.current().type is not TokenType.LT:
            return []

        # 'Caixa<T>' e generico; 'a < b' e comparacao. O que separa e o
        # que vem depois: um nome de tipo (maiusculo) seguido de '>' ou
        # ','. Sem esta checagem, 'x < y' viraria erro de sintaxe.
        salvo = self.pos
        self.advance()
        tipos = []
        limites = {}
        self._ultimos_limites = {}
        while True:
            atual = self.current()
            if atual.type is not TokenType.IDENTIFIER or \
                    not str(atual.value or "")[:1].isupper():
                self.pos = salvo
                return []
            nome = self.advance().value
            tipos.append(nome)
            # '<T extends Number>' — o limite. Diferente do '<T>' solto,
            # que so documenta, um limite e VERIFICAVEL: o 'check' confere
            # o argumento na chamada, e a execucao confere o valor.
            if self.current().type is TokenType.EXTENDS:
                self.advance()
                limite = self.current()
                if limite.type is not TokenType.IDENTIFIER:
                    self.error(f"Expected a type after '{nome} extends'")
                limites[nome] = self._parse_nome_de_tipo(
                    f"Expected a type after '{nome} extends'")
            if self.match(TokenType.COMMA):
                continue
            break

        if self.current().type is not TokenType.GT:
            self.pos = salvo
            return []
        self.advance()
        # Guardado aqui, e lido LOGO depois por quem chamou: o corpo da
        # declaracao pode ter outro generico, e ele sobrescreveria isto.
        self._ultimos_limites = limites
        return tipos

    #: As palavras que podem vir ANTES de 'blueprint', em qualquer ordem.
    MODIFICADORES_DE_BLUEPRINT = ("abstract", "final", "sealed", "meta")

    def _modificadores_antes_de_blueprint(self):
        """'abstract sealed blueprint X' — as palavras, ou None.

        So devolve alguma coisa quando a sequencia TERMINA em
        'blueprint'. Assim 'final := 3' e 'meta.x' continuam sendo nomes
        comuns: a palavra so vira modificador quando o que vem depois
        confirma a intencao.
        """
        i = 0
        palavras = []
        while True:
            tok = self.peek(i)
            if tok.type == TokenType.BLUEPRINT:
                return palavras if palavras else None
            if (tok.type == TokenType.IDENTIFIER
                    and tok.value in self.MODIFICADORES_DE_BLUEPRINT
                    and tok.value not in palavras):
                palavras.append(tok.value)
                i += 1
                continue
            return None

    def parse_blueprint_com_modificadores(self):
        """Consome 'abstract'/'final'/'sealed'/'meta' e le o blueprint."""
        palavras = self._modificadores_antes_de_blueprint() or []
        primeiro = self.current()
        for _ in palavras:
            self.advance()
        if "abstract" in palavras and "final" in palavras:
            self.error("A blueprint cannot be both 'abstract' and 'final': "
                       "abstract needs a child to be used, and final "
                       "forbids children. Pick one.", primeiro)
        if "final" in palavras and "sealed" in palavras:
            self.error("'final' already forbids every child, so 'sealed' "
                       "adds nothing. Keep one of them.", primeiro)
        return self.parse_blueprint(abstrato="abstract" in palavras,
                                    modificadores=palavras)

    def parse_blueprint(self, abstrato: bool = False, modificadores=()):
        """blueprint Name [<T>] [(params)] [extends Pai] [with Trait] [using Meta]: bloco
        OR blueprint Name [(Parent)]: block  (backward compat)

        Com abstrato=True veio de 'abstract blueprint Nome:' — nao pode
        ser instanciado com spawn, so herdado.

        Os parametros do cabecalho aceitam tipo e padrao, como os de uma
        acao: 'blueprint Caixa<T>(valor: T, rotulo := "")'. Sem isso, o
        generico mais comum que existe — uma caixa que guarda um T —
        era erro de sintaxe no primeiro ':'.
        """
        tok = self.advance()  # consume 'blueprint'
        name = self.expect(TokenType.IDENTIFIER).value
        tipos = self._parse_parametros_de_tipo()
        limites = dict(self._ultimos_limites) if tipos else {}
        # Sem esta linha, 'Caixa<Integer>' era ERRO DE SINTAXE.
        #
        # 'type', 'record', 'enum' e 'trait' registram os parametros de
        # tipo aqui; o blueprint LIA os dele e nao registrava. O efeito
        # era uma assimetria sem explicacao: 'Par<Integer, String>' num
        # record anotava, e 'Caixa<Integer>' num blueprint respondia
        # "nao e um tipo de colecao" — e a mensagem sugeria escrever
        # 'type Caixa<T> := …', que e o caminho errado.
        #
        # O runtime ja estava pronto: '_conferir_generico_do_usuario'
        # tem o ramo de DFInstance desde sempre. Faltava so poder
        # ESCREVER a anotacao.
        if tipos:
            self._tipos_genericos[name] = len(tipos)
        parents = []
        traits = []
        constructor_params = []
        tipos_do_cabecalho = {}
        padroes_do_cabecalho = {}
        metaclasse = ""

        # Parse optional parenthesized list
        paren_names = []
        if self.match(TokenType.LPAREN):
            while self.current().type != TokenType.RPAREN:
                nome_param = self.expect(TokenType.IDENTIFIER).value
                self._recusar_parametro_repetido(paren_names, nome_param)
                paren_names.append(nome_param)
                if self.match(TokenType.COLON):
                    tipos_do_cabecalho[nome_param] = self._parse_nome_de_tipo(
                        f"Expected the type of '{nome_param}' after ':'")
                if self.match(TokenType.ASSIGN):
                    padroes_do_cabecalho[nome_param] = self.parse_expression()
                elif padroes_do_cabecalho:
                    self._recusar_obrigatorio_depois_de_padrao(
                        nome_param, padroes_do_cabecalho)
                self.match(TokenType.COMMA)
            self.expect(TokenType.RPAREN)

        # Check what follows to determine meaning of parenthesized names
        if tipos_do_cabecalho or padroes_do_cabecalho:
            # Com tipo ou padrao nao ha ambiguidade: sao parametros.
            constructor_params = paren_names
            if self.current().type == TokenType.EXTENDS:
                self.advance()
                parents.append(self._nome_pontuado())
                while self.match(TokenType.COMMA):
                    parents.append(self._nome_pontuado())
        elif self.current().type == TokenType.EXTENDS:
            # New style: params in parens, extends for parent
            constructor_params = paren_names
            self.advance()  # consume 'extends'
            parents.append(self._nome_pontuado())
            while self.match(TokenType.COMMA):
                parents.append(self._nome_pontuado())
        elif self.current().type in (TokenType.WITH, TokenType.USING):
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

        # 'with' (traits e contratos) e 'using' (metaclasse), em qualquer ordem
        while self.current().type in (TokenType.WITH, TokenType.USING):
            if self.match(TokenType.WITH):
                traits.append(self._nome_pontuado())
                while self.match(TokenType.COMMA):
                    traits.append(self._nome_pontuado())
            else:
                usando = self.advance()
                if metaclasse:
                    self.error(f"Blueprint '{name}' names two metaclasses. "
                               f"A blueprint is governed by one 'using'.",
                               usando)
                metaclasse = self._nome_pontuado(
                    "Expected the metaclass after 'using', as in "
                    "'blueprint Usuario using Registro:'")

        self.expect(TokenType.COLON, "Expected ':' after blueprint header")
        self.match(TokenType.NEWLINE)
        body, campos = self.parse_blueprint_body()
        modificadores_de_campo = self._ultimos_mods_de_campo
        decoradores_de_campo = self._ultimos_decos_de_campo

        return ast.BlueprintDeclaration(
            name=name, parents=parents, body=body, traits=traits,
            constructor_params=constructor_params,
            fields_decl=campos, is_abstract=abstrato, type_params=tipos,
            type_bounds=limites,
            is_final="final" in modificadores,
            is_sealed="sealed" in modificadores,
            is_meta="meta" in modificadores,
            metaclass=metaclasse,
            constructor_types=tipos_do_cabecalho,
            constructor_defaults=padroes_do_cabecalho,
            field_modifiers=modificadores_de_campo,
            field_decorators=decoradores_de_campo,
            line=tok.line, column=tok.column
        )

    def _nome_pontuado(self, mensagem="Expected a name"):
        """'Forma' ou 'Geo.Forma' — um nome que pode vir de um modulo."""
        partes = [self.expect(TokenType.IDENTIFIER, mensagem).value]
        while (self.current().type == TokenType.DOT
               and self.peek(1).type == TokenType.IDENTIFIER):
            self.advance()
            partes.append(self.advance().value)
        return ".".join(partes)

    # ── Corpo do blueprint ───────────────────────────────────

    #: Operadores que podem ser sobrecarregados, e o metodo que cada um vira.
    OPERADORES_SOBRECARREGAVEIS = {
        TokenType.PLUS: "+", TokenType.MINUS: "-", TokenType.STAR: "*",
        TokenType.SLASH: "/", TokenType.PERCENT: "%", TokenType.POWER: "**",
        TokenType.EQUAL: "==", TokenType.NOT_EQUAL: "!=",
        TokenType.LT: "<", TokenType.GT: ">",
        TokenType.LT_EQ: "<=", TokenType.GT_EQ: ">=",
        TokenType.SMALLER: "<", TokenType.BIGGER: ">",
        TokenType.SMALLER_EQ: "<=", TokenType.BIGGER_EQ: ">=",
        TokenType.IS: "==", TokenType.ISNT: "!=",
    }

    #: Os modificadores de membro, na ordem em que a doc os apresenta.
    MODIFICADORES_DE_MEMBRO = (
        "private", "protected", "internal", "abstract", "final", "override",
        "overload", "exclusive", "readonly", "lazy")

    #: O que cada modificador aceita modificar. Um 'lazy' num campo, ou um
    #: 'readonly' numa acao, e recusado na leitura — calar faria a palavra
    #: parecer valer sem valer nada.
    _MODIFICADOR_SERVE = {
        "private": {"action", "field", "property"},
        "protected": {"action", "field", "property"},
        "internal": {"action", "field", "property"},
        "abstract": {"action", "blueprint"},
        "final": {"action", "blueprint"},
        "override": {"action", "property"},
        "overload": {"action"},
        "exclusive": {"action"},
        "readonly": {"field"},
        "lazy": {"property"},
    }

    def parse_blueprint_body(self):
        """Le o corpo de um blueprint.

        Devolve (instrucoes, campos_declarados). Reconhece, alem de acoes:

            nome: Tipo [:= padrao]     campo declarado
            private action f(): ...    visibilidade (private/protected/internal)
            static action f(): ...     metodo de classe
            static steady MAX := 3     constante de classe
            abstract action f()        sem corpo, obriga o herdeiro
            final action f(): ...      nao pode ser sobrescrito
            override action f(): ...   tem de sobrescrever algo
            overload action f(x: T)    uma variante, escolhida na chamada
            exclusive action f(): ...  uma thread por vez neste objeto
            readonly nome := valor     so a construcao escreve
            get area(): ...            propriedade de leitura
            lazy get total(): ...      calculada uma vez por objeto
            set area(v): ...           propriedade de escrita
            operator + (o): ...        sobrecarga
            invariant cond, "msg"      vale depois de toda operacao publica
            @Anotacao                  sobre qualquer membro, inclusive campo

        Os modificadores e os decoradores de CAMPO ficam em
        '_ultimos_mods_de_campo' e '_ultimos_decos_de_campo', lidos por
        quem chamou logo depois: a tupla de campo tem quatro posicoes e e
        desempacotada em muitos lugares, e crescer a tupla quebraria
        todos eles.
        """
        self.skip_newlines()
        self.expect(TokenType.INDENT, "A blueprint needs an indented body")

        mods_antes = getattr(self, "_mods_de_campo", None)
        decos_antes = getattr(self, "_decos_de_campo", None)
        self._mods_de_campo, self._decos_de_campo = {}, {}
        try:
            corpo, campos = [], []
            while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
                self.skip_newlines()
                if self.current().type in (TokenType.DEDENT, TokenType.EOF):
                    break

                item, campo = self.parse_membro_blueprint()
                if campo is not None:
                    campos.append(campo)
                if item is not None:
                    corpo.append(item)
                self.skip_newlines()

            if self.current().type == TokenType.DEDENT:
                self.advance()
            self._ultimos_mods_de_campo = self._mods_de_campo
            self._ultimos_decos_de_campo = self._decos_de_campo
            return corpo, campos
        finally:
            self._mods_de_campo, self._decos_de_campo = mods_antes, decos_antes

    @staticmethod
    def _texto_e(token, *palavras):
        """O token e um identificador com um destes textos?"""
        return (token.type == TokenType.IDENTIFIER
                and token.value in palavras)

    def _e_modificador(self, palavra):
        """'private' so e modificador se vier antes de outro membro.

        'private action f()' e modificador. Ja 'private := 1' e uma
        variavel chamada 'private', e a palavra nao tem poder nenhum.
        """
        if not self._texto_e(self.current(), palavra):
            return False
        prox = self.peek(1)
        if prox.type in (TokenType.ACTION, TokenType.STATIC,
                         TokenType.BLUEPRINT, TokenType.ASYNC):
            return True
        if prox.type == TokenType.STREAM and self.peek(2).type == TokenType.ACTION:
            return True
        if self._texto_e(prox, "get", "set", "operator",
                         *self.MODIFICADORES_DE_MEMBRO,
                         *self.MODIFICADORES_DE_BLUEPRINT):
            return True
        # 'private nome: Tipo' e 'readonly nome := valor' — campo
        return (prox.type == TokenType.IDENTIFIER
                and self.peek(2).type in (TokenType.COLON, TokenType.ASSIGN))

    def _e_propriedade(self):
        """'get nome(' ou 'set nome(' — e ai sim uma propriedade."""
        return (self._texto_e(self.current(), "get", "set")
                and self.peek(1).type == TokenType.IDENTIFIER
                and self.peek(2).type == TokenType.LPAREN)

    #: O que pode comecar a expressao de um 'invariant'/'expects'/'promises'.
    #: A lista e POSITIVA de proposito: 'expects := 1', 'expects(x)' e
    #: 'expects.campo' continuam sendo um nome comum.
    _COMECA_CONDICAO = frozenset({
        TokenType.IDENTIFIER, TokenType.SELF, TokenType.NOT,
        TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
        TokenType.INTERP_STRING, TokenType.BOOLEAN, TokenType.VOID,
        TokenType.TYPEOF,
    })

    def _abre_condicao(self, palavra):
        return (self._palavra(palavra)
                and self.peek(1).type in self._COMECA_CONDICAO)

    def _parse_condicao_com_mensagem(self, no, rotulo):
        """'<palavra> cond [, "mensagem"]' — o formato das tres clausulas."""
        tok = self.advance()                    # a palavra
        condicao = self.parse_expression()
        mensagem = None
        if self.match(TokenType.COMMA):
            mensagem = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return no(condition=condicao, message=mensagem,
                  line=tok.line, column=tok.column)

    def parse_expects(self):
        """expects cond [, "mensagem"] — pre-condicao."""
        return self._parse_condicao_com_mensagem(ast.ExpectsStatement, "expects")

    def parse_promises(self):
        """promises cond [, "mensagem"] — pos-condicao; aceita before(expr)."""
        self._em_promessa = getattr(self, "_em_promessa", 0) + 1
        try:
            return self._parse_condicao_com_mensagem(ast.PromisesStatement,
                                                     "promises")
        finally:
            self._em_promessa -= 1

    def parse_membro_blueprint(self):
        """Um membro do corpo. Devolve (instrucao, campo) — um dos dois e None."""
        visibilidade = "public"
        estatico = False
        flags = []
        inicio = self.current()

        # Decoradores sobre o membro — inclusive sobre um CAMPO, que e onde
        # '@Coluna("email")' e '@Injetar' mais servem.
        decoradores = []
        while (self.current().type is TokenType.AT
               or (self.current().type is TokenType.MARK
                   and self.peek(1).type is TokenType.AT)):
            if self.current().type is TokenType.MARK:
                self.advance()
            decoradores.append(self.parse_um_decorador())
            self.skip_newlines()

        # Modificadores, em qualquer ordem: 'private static action f()'.
        # Sao palavras contextuais: reconhecidas pelo texto, e so quando o
        # que vem em seguida confirma que sao modificador. Assim
        # 'final := 10' continua sendo uma variavel chamada 'final'.
        while True:
            achou = False
            for palavra in self.MODIFICADORES_DE_MEMBRO:
                if self._e_modificador(palavra):
                    tok_mod = self.advance()
                    if palavra in ("private", "protected", "internal"):
                        if visibilidade != "public":
                            self.error(
                                f"A member has one visibility; "
                                f"'{visibilidade}' and '{palavra}' were both "
                                f"written.", tok_mod)
                        visibilidade = palavra
                    elif palavra in flags:
                        self.error(f"'{palavra}' was written twice.", tok_mod)
                    else:
                        flags.append(palavra)
                    achou = True
                    break
            if achou:
                continue
            if (self.current().type == TokenType.STATIC
                    and (self.peek(1).type in (TokenType.ACTION, TokenType.STEADY,
                                               TokenType.ASYNC)
                         or self._texto_e(self.peek(1), "get", "set"))):
                estatico = True
                self.advance()
                continue
            break

        t = self.current().type

        def recusar_se_nao_serve(especie):
            for palavra in flags + ([visibilidade] if visibilidade != "public" else []):
                if especie not in self._MODIFICADOR_SERVE[palavra]:
                    nomes = {"action": "an action", "field": "a field",
                             "property": "a property", "blueprint": "a blueprint",
                             "invariant": "an invariant"}
                    serve = ", ".join(sorted(self._MODIFICADOR_SERVE[palavra]))
                    self.error(f"'{palavra}' cannot modify {nomes[especie]}; "
                               f"it applies to: {serve}.", inicio)

        # invariant cond, "mensagem"
        if self._abre_condicao("invariant"):
            if flags or visibilidade != "public" or estatico or decoradores:
                self.error("'invariant' takes no modifier or decorator: it "
                           "always holds, for every public operation.", inicio)
            return self._parse_condicao_com_mensagem(
                ast.InvariantStatement, "invariant"), None

        # blueprint aninhado, com os proprios modificadores
        if t == TokenType.BLUEPRINT or self._modificadores_antes_de_blueprint():
            recusar_se_nao_serve("blueprint")
            if t == TokenType.BLUEPRINT:
                decl = self.parse_blueprint(abstrato="abstract" in flags,
                                            modificadores=flags)
            else:
                decl = self.parse_blueprint_com_modificadores()
            decl.decorators = decoradores + list(decl.decorators or [])
            return decl, None

        # get nome(): ...   |   set nome(valor): ...
        if self._e_propriedade():
            recusar_se_nao_serve("property")
            prop = self.parse_property(visibilidade)
            prop.is_lazy = "lazy" in flags
            prop.is_override = "override" in flags
            if prop.is_lazy and prop.kind != "get":
                self.error(f"'lazy' applies to a 'get': 'lazy get "
                           f"{prop.name}()'. A setter has nothing to cache.",
                           inicio)
            prop.decorators = decoradores
            return prop, None

        # operator + (outro): ...
        # 'operator' seguido de ':=', '(' ou '.' e uma variavel chamada
        # 'operator'; qualquer outra coisa e uma tentativa de sobrecarga —
        # inclusive um simbolo invalido, que merece a mensagem certa.
        if self._texto_e(self.current(), "operator") and self.peek(1).type not in (
                TokenType.ASSIGN, TokenType.LPAREN, TokenType.DOT,
                TokenType.NEWLINE, TokenType.COLON, TokenType.COMMA,
                TokenType.RPAREN, TokenType.LBRACKET):
            if flags or visibilidade != "public":
                self.error("An 'operator' takes no modifier: it is public by "
                           "nature, because the language calls it.", inicio)
            return self.parse_operator(), None

        # action / abstract action / async action / stream action
        if t in (TokenType.ACTION, TokenType.ASYNC) or (
                t == TokenType.STREAM and self.peek(1).type == TokenType.ACTION):
            recusar_se_nao_serve("action")
            abstrato = "abstract" in flags
            if t == TokenType.ACTION:
                decl = self.parse_action(sem_corpo=abstrato)
            elif t == TokenType.ASYNC:
                decl = self.parse_async_action()
            else:
                self.advance()
                decl = self.parse_action(is_generator=True, sem_corpo=abstrato)
            decl.visibility = visibilidade
            decl.is_static = estatico
            decl.is_abstract = abstrato or bool(getattr(decl, "is_abstract", False))
            decl.is_final = "final" in flags
            decl.is_override = "override" in flags
            decl.is_overload = "overload" in flags
            decl.is_exclusive = "exclusive" in flags
            if decl.is_abstract and decl.is_final:
                self.error(f"'{decl.name}' cannot be abstract and final: "
                           f"abstract asks a child to write it, final "
                           f"forbids that.", inicio)
            if decl.is_exclusive and estatico:
                self.error(f"'exclusive' locks the OBJECT, and a static "
                           f"action has none. Use Arcane.Concurrent.mutex "
                           f"for class-wide exclusion.", inicio)
            decl.decorators = decoradores + list(decl.decorators or [])
            return decl, None

        # slots ["a", "b"]  —  restringe os campos da instancia
        #
        # Contextual, como 'get' e 'final': reconhecido pelo TEXTO, e so
        # quando o que vem depois confirma. 'slots := 3' continua sendo
        # uma variavel chamada 'slots'.
        if (self._palavra("slots")
                and self.peek(1).type in (TokenType.LBRACKET,
                                          TokenType.IDENTIFIER,
                                          TokenType.STRING)):
            tok = self.advance()
            nomes = []
            if self.match(TokenType.LBRACKET):
                while self.current().type != TokenType.RBRACKET:
                    tok_nome = self.current()
                    if tok_nome.type == TokenType.STRING:
                        nomes.append(self.advance().value)
                    elif tok_nome.type == TokenType.IDENTIFIER:
                        nomes.append(self.advance().value)
                    else:
                        self.error("'slots' takes field names: "
                                   "slots [\"a\", \"b\"]")
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RBRACKET, "Expected ']' after slots")
            else:
                # 'slots a, b' tambem, sem colchetes
                while self.current().type == TokenType.IDENTIFIER:
                    nomes.append(self.advance().value)
                    if not self.match(TokenType.COMMA):
                        break
            self.match(TokenType.NEWLINE)
            return ast.SlotsDeclaration(names=nomes, line=tok.line,
                                        column=tok.column), None

        # static x := valor   |   static steady MAX := valor
        if t == TokenType.STATIC or (estatico and t == TokenType.STEADY):
            if flags or visibilidade != "public":
                self.error("A static field takes no other modifier.", inicio)
            if estatico:
                # 'static' ja foi consumido no laco dos modificadores
                return self._parse_static_depois_da_palavra(inicio), None
            return self.parse_statement(), None

        # nome: Tipo [:= padrao] — campo declarado
        if t == TokenType.IDENTIFIER and self.peek(1).type == TokenType.COLON:
            recusar_se_nao_serve("field")
            nome_tok = self.advance()
            self.advance()                      # ':'
            tipo = self._parse_nome_de_tipo(
                f"Field '{nome_tok.value}' needs a type, as in "
                f"'{nome_tok.value}: String'")
            padrao = None
            if self.match(TokenType.ASSIGN):
                padrao = self.parse_expression()
            self.match(TokenType.NEWLINE)
            self._registrar_campo(nome_tok.value, flags, decoradores)
            return None, (nome_tok.value, tipo, padrao, visibilidade)

        # nome := padrao — campo sem tipo, com modificador ou decorador
        if (t == TokenType.IDENTIFIER and self.peek(1).type == TokenType.ASSIGN
                and (flags or visibilidade != "public" or decoradores)):
            recusar_se_nao_serve("field")
            stmt = self.parse_statement()
            stmt.visibility = visibilidade
            self._registrar_campo(stmt.target.name, flags, decoradores)
            return stmt, None

        if flags or visibilidade != "public" or estatico:
            palavras = " ".join(([visibilidade] if visibilidade != "public" else [])
                                + flags + (["static"] if estatico else []))
            self.error(f"'{palavras}' must be followed by a member: an action, "
                       f"a field, a property or a blueprint.", inicio)
        if decoradores:
            self.error("A decorator inside a blueprint needs a member below "
                       "it: an action, a field or a property.", inicio)

        # qualquer outra instrucao (out, given, corpo de construtor…)
        return self.parse_statement(), None

    def _registrar_campo(self, nome, flags, decoradores):
        """Guarda os modificadores e os decoradores de um campo."""
        if flags:
            self._mods_de_campo[nome] = set(flags)
        if decoradores:
            self._decos_de_campo[nome] = list(decoradores)

    def parse_property(self, visibilidade="public", sem_corpo=False):
        """get nome() [-> Tipo]: bloco   |   set nome(valor): bloco"""
        tok = self.advance()                    # 'get' ou 'set'
        tipo = tok.value
        nome = self.expect(
            TokenType.IDENTIFIER,
            f"Expected the property name after '{tipo}'").value

        parametro = ""
        self.expect(TokenType.LPAREN, f"Expected '(' after the property '{nome}'")
        if tipo == "set":
            parametro = self.expect(
                TokenType.IDENTIFIER,
                f"The setter '{nome}' needs one parameter: the value being "
                f"assigned, as in 'set {nome}(valor):'").value
        elif self.current().type != TokenType.RPAREN:
            self.error(f"The getter '{nome}' takes no parameters. "
                       f"Write 'get {nome}():'.")
        self.expect(TokenType.RPAREN, "Expected ')'")

        tipo_retorno = ""
        if self.match(TokenType.ARROW):
            tipo_retorno = self._parse_nome_de_tipo(
                "Expected the return type after '->'")

        # Num contrato, a propriedade e so a assinatura: 'get nome() -> T'.
        if sem_corpo and self.current().type in (TokenType.NEWLINE,
                                                 TokenType.DEDENT, TokenType.EOF):
            self.match(TokenType.NEWLINE)
            return ast.PropertyDeclaration(
                name=nome, kind=tipo, param=parametro, body=[],
                visibility=visibilidade, return_type=tipo_retorno,
                is_abstract=True, line=tok.line, column=tok.column)

        self.expect(TokenType.COLON, f"Expected ':' after the property '{nome}'")
        self.match(TokenType.NEWLINE)
        corpo = self.parse_block()

        return ast.PropertyDeclaration(
            name=nome, kind=tipo, param=parametro, body=corpo,
            visibility=visibilidade, return_type=tipo_retorno,
            line=tok.line, column=tok.column)

    def parse_operator(self):
        """operator <simbolo> (outro): bloco"""
        tok = self.advance()                    # 'operator'
        simbolo_tok = self.current()
        simbolo = self.OPERADORES_SOBRECARREGAVEIS.get(simbolo_tok.type)
        if simbolo is None:
            aceitos = ", ".join(sorted(set(self.OPERADORES_SOBRECARREGAVEIS.values())))
            self.error(f"'{simbolo_tok.text or simbolo_tok.value}' cannot be "
                       f"overloaded. You can overload: {aceitos}")
        self.advance()

        self.expect(TokenType.LPAREN, f"Expected '(' after 'operator {simbolo}'")
        parametro = self.expect(
            TokenType.IDENTIFIER,
            f"'operator {simbolo}' needs one parameter: the value on the "
            f"other side, as in 'operator {simbolo} (outro):'").value
        self.expect(TokenType.RPAREN, "Expected ')'")
        self.expect(TokenType.COLON, f"Expected ':' after 'operator {simbolo}'")
        self.match(TokenType.NEWLINE)
        corpo = self.parse_block()

        return ast.OperatorDeclaration(
            symbol=simbolo, param=parametro, body=corpo,
            line=tok.line, column=tok.column)

    def parse_contract(self):
        """contract Nome<T> [extends A, B]: assinaturas

        Cada membro e uma assinatura sem corpo:

            contract Repositorio<T>:
                action salvar(item: T)
                action buscar(id: Integer) -> T
                get total() -> Integer

        Um corpo e recusado na LEITURA. Implementacao padrao e o que o
        trait faz; deixar o contrato ter corpo apagaria a unica
        diferenca entre os dois, e com ela o motivo de ter os dois.
        """
        tok = self.advance()                    # 'contract'
        nome = self.expect(TokenType.IDENTIFIER, "Expected the contract name").value
        tipos = self._parse_parametros_de_tipo()
        limites = dict(self._ultimos_limites) if tipos else {}
        pais = []
        if self.match(TokenType.EXTENDS):
            pais.append(self._nome_pontuado())
            while self.match(TokenType.COMMA):
                pais.append(self._nome_pontuado())
        self.expect(TokenType.COLON, f"Expected ':' after 'contract {nome}'")
        self.match(TokenType.NEWLINE)
        self.skip_newlines()
        self.expect(TokenType.INDENT, f"Contract '{nome}' needs an indented body "
                                      f"with at least one signature")
        membros = []
        while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.current().type in (TokenType.DEDENT, TokenType.EOF):
                break
            atual = self.current()
            if atual.type == TokenType.ACTION or (
                    atual.type in (TokenType.ASYNC, TokenType.STREAM)
                    and self.peek(1).type == TokenType.ACTION):
                geradora = atual.type == TokenType.STREAM
                assincrona = atual.type == TokenType.ASYNC
                if geradora or assincrona:
                    self.advance()
                assinatura = self.parse_action(sem_corpo=True,
                                               is_generator=geradora,
                                               is_async=assincrona)
                if assinatura.body:
                    self.error(
                        f"'{nome}.{assinatura.name}' has a body, and a contract "
                        f"only declares. Move the code to a trait, or to the "
                        f"blueprint that fulfills '{nome}'.", atual)
                assinatura.is_abstract = True
                membros.append(assinatura)
            elif self._e_propriedade():
                membros.append(self.parse_property(sem_corpo=True))
                if membros[-1].body:
                    self.error(f"The property '{membros[-1].name}' of contract "
                               f"'{nome}' has a body; a contract only declares.",
                               atual)
            elif atual.type == TokenType.STRING:
                # uma linha de documentacao, como no topo de uma acao
                self.advance()
                self.match(TokenType.NEWLINE)
            else:
                self.error(f"A contract holds signatures: 'action nome(…)' or "
                           f"'get nome()'. Found '{atual.value}'.", atual)
            self.skip_newlines()
        if self.current().type == TokenType.DEDENT:
            self.advance()
        if not membros and not pais:
            self.error(f"Contract '{nome}' declares nothing. Add a signature, "
                       f"or extend other contracts.", tok)
        return ast.ContractDeclaration(name=nome, parents=pais, members=membros,
                                       type_params=tipos, type_bounds=limites,
                                       line=tok.line, column=tok.column)

    def parse_augment(self):
        """augment Nome: membros — acrescenta a um blueprint que ja existe.

        O corpo e o de um blueprint. O que ele NAO pode fazer e decidido
        em execucao, onde o blueprint existe: substituir um membro,
        mexer num 'final', ou atravessar o arquivo de um 'sealed'.
        """
        tok = self.advance()                    # 'augment'
        nome = self._nome_pontuado("Expected the blueprint to augment")
        self.expect(TokenType.COLON, f"Expected ':' after 'augment {nome}'")
        self.match(TokenType.NEWLINE)
        corpo, campos = self.parse_blueprint_body()
        return ast.AugmentDeclaration(name=nome, body=corpo, fields_decl=campos,
                                      field_modifiers=self._ultimos_mods_de_campo,
                                      line=tok.line, column=tok.column)

    def parse_record(self):
        """record Nome: campo: Tipo [:= padrao] ... [action metodo(): ...]"""
        tok = self.advance()  # record
        nome = self.expect(TokenType.IDENTIFIER, "Expected the record name").value
        tipos = self._parse_parametros_de_tipo()
        limites = dict(self._ultimos_limites)
        if tipos:
            self._tipos_genericos[nome] = len(tipos)
        self.expect(TokenType.COLON, "Expected ':' after the record name")
        self.match(TokenType.NEWLINE)
        self.skip_newlines()
        self.expect(TokenType.INDENT, "A record needs an indented body")

        campos = []
        metodos = {}
        while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.current().type in (TokenType.DEDENT, TokenType.EOF):
                break
            if self.current().type == TokenType.ACTION:
                metodo = self.parse_action()
                metodos[metodo.name] = metodo
                self.skip_newlines()
                continue
            campo = self.expect(TokenType.IDENTIFIER,
                                "Expected a field name in the record").value
            self.expect(TokenType.COLON,
                        f"Field '{campo}' needs a type: '{campo}: Tipo'")
            tipo = self._parse_nome_de_tipo(
                f"Expected the type of field '{campo}'")
            padrao = None
            if self.match(TokenType.ASSIGN):
                padrao = self.parse_expression()
            campos.append((campo, tipo, padrao))
            self.match(TokenType.NEWLINE)
            self.skip_newlines()
        if self.current().type == TokenType.DEDENT:
            self.advance()

        if not campos:
            self.error(f"Record '{nome}' has no fields. "
                       f"Declare at least one as 'campo: Tipo'.")
        return ast.RecordDeclaration(name=nome, fields=campos, methods=metodos,
                                     type_params=tipos, type_bounds=limites,
                                     line=tok.line, column=tok.column)

    def parse_enum(self):
        """enum Nome: MEMBRO [:= valor] ... [action metodo(): ...]"""
        tok = self.advance()  # enum
        nome = self.expect(TokenType.IDENTIFIER, "Expected the enum name").value
        tipos_do_enum = self._parse_parametros_de_tipo()
        limites_do_enum = dict(self._ultimos_limites)
        if tipos_do_enum:
            self._tipos_genericos[nome] = len(tipos_do_enum)
        self.expect(TokenType.COLON, "Expected ':' after the enum name")
        self.match(TokenType.NEWLINE)
        self.skip_newlines()
        self.expect(TokenType.INDENT, "An enum needs an indented body")

        membros = []
        metodos = {}
        while self.current().type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.current().type in (TokenType.DEDENT, TokenType.EOF):
                break
            if self.current().type == TokenType.ACTION:
                metodo = self.parse_action()
                metodos[metodo.name] = metodo
                self.skip_newlines()
                continue
            membro = self.expect(TokenType.IDENTIFIER,
                                 "Expected an enum member name").value
            valor = None
            if self.match(TokenType.ASSIGN):
                valor = self.parse_expression()
            membros.append((membro, valor))
            self.match(TokenType.NEWLINE)
            self.skip_newlines()
        if self.current().type == TokenType.DEDENT:
            self.advance()

        if not membros:
            self.error(f"Enum '{nome}' has no members.")
        return ast.EnumDeclaration(name=nome, members=membros, methods=metodos,
                                   type_params=tipos_do_enum,
                                   type_bounds=limites_do_enum,
                                   line=tok.line, column=tok.column)

    def parse_emit(self):
        """emit expr — produz num generator, imprime fora dele."""
        tok = self.advance()
        expressoes = []
        if self.current().type not in (TokenType.NEWLINE, TokenType.EOF,
                                       TokenType.DEDENT):
            expressoes.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                expressoes.append(self.parse_expression())
        self.match(TokenType.NEWLINE)
        return ast.EmitStatement(expressions=expressoes,
                                 line=tok.line, column=tok.column)

    def parse_trait(self):
        """trait Nome [<T>] [extends Outro, …]: assinaturas e padrões."""
        tok = self.advance()  # consume 'trait'
        name = self.expect(TokenType.IDENTIFIER).value
        tipos = self._parse_parametros_de_tipo()
        limites = dict(self._ultimos_limites)
        if tipos:
            self._tipos_genericos[name] = len(tipos)
        # 'trait Editavel extends Legivel' — um trait herda exigências e
        # implementações padrão de outro, como um contrato herda de outro.
        pais = []
        if self.match(TokenType.EXTENDS):
            while True:
                pais.append(self._parse_nome_de_tipo(
                    "Expected the name of the trait after 'extends'"))
                if not self.match(TokenType.COMMA):
                    break
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        methods = self.parse_block()
        return ast.TraitDeclaration(name=name, methods=methods, parents=pais,
                                    type_params=tipos, type_bounds=limites,
                                    line=tok.line, column=tok.column)

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
                ptok = self.advance()
                padrao = self.parse_pattern()
                guarda = None
                if self.match(TokenType.WHEN):
                    self._no_ternary += 1
                    try:
                        guarda = self.parse_expression()
                    finally:
                        self._no_ternary -= 1
                self.expect(TokenType.COLON, "Expected ':' after the pattern")
                self.match(TokenType.NEWLINE)
                point_body = self.parse_block()
                points.append(ast.MatchCase(
                    pattern=padrao, guard=guarda, body=point_body,
                    line=ptok.line, column=ptok.column))
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

    # ── Padrões de 'match / point' ─────────────────────────

    def parse_pattern(self):
        """Um padrão de 'point', com 'or' e 'as' no topo."""
        opcoes = [self._parse_pattern_primary()]
        while self.match(TokenType.OR):
            opcoes.append(self._parse_pattern_primary())
        padrao = opcoes[0] if len(opcoes) == 1 else ast.OrPattern(
            options=opcoes, line=opcoes[0].line, column=opcoes[0].column)

        if self.match(TokenType.AS):
            padrao.binding = self.expect(
                TokenType.IDENTIFIER, "Expected a name after 'as'").value
        return padrao

    def _parse_pattern_primary(self):
        tok = self.current()

        # Literais
        if tok.type in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
                        TokenType.BOOLEAN, TokenType.VOID):
            self.advance()
            return ast.LiteralPattern(value=tok.value,
                                      line=tok.line, column=tok.column)

        # Número negativo
        if tok.type == TokenType.MINUS and self.peek().type in (
                TokenType.INTEGER, TokenType.FLOAT):
            self.advance()
            num = self.advance()
            return ast.LiteralPattern(value=-num.value,
                                      line=tok.line, column=tok.column)

        # Sequência: [a, b, ...resto]
        if tok.type == TokenType.LBRACKET:
            self.advance()
            elementos = []
            rest_index, rest_name = -1, ""
            while self.current().type != TokenType.RBRACKET:
                self.skip_newlines()
                if self.match(TokenType.SPREAD):
                    if rest_index != -1:
                        self.error("Only one '...rest' is allowed in a pattern")
                    rest_index = len(elementos)
                    if self.current().type == TokenType.IDENTIFIER:
                        rest_name = self.advance().value
                else:
                    elementos.append(self.parse_pattern())
                self.skip_newlines()
                self.match(TokenType.COMMA)
                self.skip_newlines()
            self.expect(TokenType.RBRACKET)
            return ast.SequencePattern(
                elements=elementos, rest_index=rest_index, rest_name=rest_name,
                line=tok.line, column=tok.column)

        # Mapa: {"chave": padrao, ...resto}
        if tok.type == TokenType.LBRACE:
            self.advance()
            pares = []
            rest_name = ""
            while self.current().type != TokenType.RBRACE:
                self.skip_newlines()
                if self.match(TokenType.SPREAD):
                    if self.current().type == TokenType.IDENTIFIER:
                        rest_name = self.advance().value
                else:
                    chave = self.parse_primary()
                    self.expect(TokenType.COLON,
                                "Expected ':' after the key in the pattern")
                    pares.append((chave, self.parse_pattern()))
                self.skip_newlines()
                self.match(TokenType.COMMA)
                self.skip_newlines()
            self.expect(TokenType.RBRACE)
            return ast.MappingPattern(pairs=pares, rest_name=rest_name,
                                      line=tok.line, column=tok.column)

        if tok.type == TokenType.IDENTIFIER:
            nome = self.advance().value

            # Curinga
            if nome == "_":
                return ast.WildcardPattern(line=tok.line, column=tok.column)

            # Valor nomeado: Status.Ativo
            if self.current().type == TokenType.DOT:
                expr = ast.Identifier(name=nome, line=tok.line, column=tok.column)
                while self.match(TokenType.DOT):
                    membro = self.expect_member_name()
                    expr = ast.MemberAccess(object=expr, member=membro,
                                            line=tok.line, column=tok.column)
                return ast.ValuePattern(expression=expr,
                                        line=tok.line, column=tok.column)

            # Tipo com sub-padrões: Usuario(nome, idade) / Usuario(nome := p)
            if self.current().type == TokenType.LPAREN:
                self.advance()
                sub, campos = [], {}
                while self.current().type != TokenType.RPAREN:
                    self.skip_newlines()
                    if (self.current().type == TokenType.IDENTIFIER
                            and self.peek().type == TokenType.ASSIGN):
                        campo = self.advance().value
                        self.advance()
                        campos[campo] = self.parse_pattern()
                    else:
                        sub.append(self.parse_pattern())
                    self.skip_newlines()
                    self.match(TokenType.COMMA)
                    self.skip_newlines()
                self.expect(TokenType.RPAREN)
                return ast.TypePattern(type_name=nome, sub_patterns=sub,
                                       field_patterns=campos,
                                       line=tok.line, column=tok.column)

            # Convenção: Maiúscula casa por tipo, minúscula captura
            if nome[0].isupper():
                return ast.TypePattern(type_name=nome,
                                       line=tok.line, column=tok.column)
            return ast.CapturePattern(name=nome, line=tok.line, column=tok.column)

        self.error(
            f"Invalid pattern after 'point': {tok.type.name}. "
            f"Use a literal, a name, [..], {{..}} or a Type.")

    def parse_cycle(self):
        """cycle var from start to end [step s]: block
           cycle var in collection: block"""
        tok = self.advance()  # consume 'cycle'
        var_name = self.expect(TokenType.IDENTIFIER).value

        # 'cycle i, item in …' — desestrutura cada item do percurso.
        # A linguagem ja desestrutura em atribuicao ('a, b := xs'); nao
        # aceitar aqui obrigava a escrever tres linhas para o padrao
        # mais comum que existe: percorrer com indice.
        nomes = []
        while self.current().type == TokenType.COMMA:
            self.advance()
            nomes.append(self.expect(
                TokenType.IDENTIFIER,
                "Expected another name after ',' in cycle").value)
        if nomes:
            nomes.insert(0, var_name)
            if self.current().type == TokenType.FROM:
                self.error("'cycle a, b from …' does not exist: a counted "
                           "loop has one variable. Use 'cycle a, b in …'.")

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
            self._no_membership += 1
            try:
                collection = self.parse_expression()
            finally:
                self._no_membership -= 1
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            body = self.parse_block()
            return ast.CycleIn(
                var=var_name, vars=nomes, collection=collection, body=body,
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
        """monitor: block {handle [Tipo [as nome] | nome]: block} [ensure: block]"""
        tok = self.advance()  # consume 'monitor'
        self.expect(TokenType.COLON)
        self.match(TokenType.NEWLINE)
        body = self.parse_block()

        handles = []
        ensure_body = []

        # Uma clausula por tipo de erro, na ordem escrita: vence a
        # primeira que casar. E a mesma regra dos 'point' do match, e
        # pelo mesmo motivo — do especifico para o geral.
        self.skip_newlines()
        while self.current().type == TokenType.HANDLE:
            # A posicao e a do 'handle', nao a do 'monitor': um aviso
            # sobre a clausula precisa sublinhar a clausula.
            tok_handle = self.advance()
            # handle:  |  handle nome:  |  handle Tipo:  |  handle Tipo as nome:
            #
            # Sem 'as', a inicial decide: 'handle KeyError:' filtra pelo
            # tipo, 'handle erro:' da nome ao erro. E a mesma convencao
            # do resto da linguagem — Integer, Cluster e Ponto sao tipos,
            # 'total' e 'erro' sao valores.
            #
            # Antes, tudo sem 'as' virava nome, e 'handle KeyError:'
            # capturava QUALQUER erro sob o nome 'KeyError'. Com um
            # punhado de tipos isso passava; com 177, e uma armadilha:
            # o bloco engole erros sem relacao nenhuma e o programa
            # segue como se nada tivesse acontecido.
            nome, tipo = "error", ""
            if self.current().type == TokenType.IDENTIFIER:
                first = self.advance().value
                if self.match(TokenType.AS):
                    tipo = first
                    nome = self.expect(TokenType.IDENTIFIER,
                                       "Expected error name after 'as'").value
                elif first[:1].isupper():
                    tipo = first
                else:
                    nome = first
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            corpo = self.parse_block()
            handles.append(ast.HandleClause(
                error_type=tipo, error_name=nome, body=corpo,
                line=tok_handle.line, column=tok_handle.column))
            self.skip_newlines()

        if self.current().type == TokenType.ENSURE:
            self.advance()
            self.expect(TokenType.COLON)
            self.match(TokenType.NEWLINE)
            ensure_body = self.parse_block()

        return ast.MonitorBlock(
            body=body, handles=handles, ensure_body=ensure_body,
            line=tok.line, column=tok.column
        )

    def parse_out(self, uma_so=False):
        """out expr1, expr2, ...

        Com 'uma_so', para na primeira expressao. E o que ele precisa
        ser como corpo de lambda dentro de um cluster:

            [lambda => out "a", lambda => out "b"]

        Sem a limitacao, o primeiro 'out' engole a virgula e o segundo
        lambda vira argumento dele — e o cluster passa a ter um item.
        """
        tok = self.advance()  # consume 'out'
        expressions = []
        if self.current().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            expressions.append(self.parse_expression())
            while not uma_so and self.match(TokenType.COMMA):
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
        self._no_membership += 1
        try:
            source = self.parse_expression()
        finally:
            self._no_membership -= 1
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

    #: As instrucoes que valem como corpo de lambda.
    #:
    #: O corpo de um lambda e uma expressao — e assim que ele devolve
    #: valor. Mas duas instrucoes aparecem o tempo todo em callback e
    #: nao tem forma de expressao:
    #:
    #:     bus.assinar("pedido", lambda p => out $"novo: {p}")
    #:     expect(lambda => trigger "falhou").to_raise()
    #:
    #: Recusa-las obrigava a declarar uma acao de uma linha para cada
    #: callback, o que e ruido puro. Elas devolvem void, que e o valor
    #: certo para um callback que so age.
    _STATEMENTS_EM_LAMBDA = {
        TokenType.OUT: "parse_out",
        TokenType.TRIGGER: "parse_trigger",
        TokenType.ASSERT: "parse_assert",
    }

    def _corpo_de_lambda(self):
        """O corpo: uma expressao, ou uma das instrucoes que cabem aqui."""
        producao = self._STATEMENTS_EM_LAMBDA.get(self.current().type)
        if producao is None:
            return self.parse_or()
        if producao == "parse_out":
            return self.parse_out(uma_so=True)
        return getattr(self, producao)()

    def parse_with(self):
        """with <recurso> [as <nome>]: corpo"""
        tok = self.advance()                        # 'with'
        recurso = self.parse_expression()
        nome = ""
        if self.match(TokenType.AS):
            nome = self.expect(
                TokenType.IDENTIFIER,
                "Expected a name after 'as'").value
        self.expect(TokenType.COLON, "Expected ':' after the 'with' header")
        self.match(TokenType.NEWLINE)
        corpo = self.parse_block()
        return ast.WithBlock(resource=recurso, name=nome, body=corpo,
                             line=tok.line, column=tok.column)

    def parse_static(self):
        """static nome [: Tipo] := valor

        A anotacao de tipo e opcional aqui pelo mesmo motivo que em
        qualquer outra declaracao: ela documenta e o analisador a
        confere. Recusa-la num campo estatico era so uma
        inconsistencia — o campo de instancia ao lado a aceitava, e
        quem escrevia os dois juntos tropecava no primeiro.
        """
        tok = self.advance()                    # 'static'
        return self._parse_static_depois_da_palavra(tok)

    def _parse_static_depois_da_palavra(self, tok):
        """O resto de 'static [steady] nome [: Tipo] := valor'.

        'static steady MAX := 3' e uma CONSTANTE de classe: le-se por
        'Blueprint.MAX' como qualquer estatico, e escrever nela e
        recusado — a mesma promessa do 'steady' de uma variavel.
        """
        constante = bool(self.match(TokenType.STEADY))
        name = self.expect(TokenType.IDENTIFIER).value

        tipo = ""
        if self.match(TokenType.COLON):
            tipo = self._parse_nome_de_tipo(
                f"Static field '{name}' needs a type after ':', as in "
                f"'static {name}: Integer := 0'")

        self.expect(TokenType.ASSIGN,
                    f"Static field '{name}' needs a value: "
                    f"'static {name} := 0'")
        value = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return ast.StaticDeclaration(name=name, value=value,
                                     declared_type=tipo, is_steady=constante,
                                     line=tok.line, column=tok.column)

    # ── Expression statement / assignment ──────────────────

    COMPOUND_ASSIGN = {
        TokenType.PLUS_ASSIGN: "+",
        TokenType.MINUS_ASSIGN: "-",
        TokenType.STAR_ASSIGN: "*",
        TokenType.SLASH_ASSIGN: "/",
        TokenType.PERCENT_ASSIGN: "%",
    }

    def _looks_like_destructuring(self) -> bool:
        """Ha 'a, b := ...' ou '{a, b} := ...' a partir daqui?"""
        i = self.pos
        toks = self.tokens
        n = len(toks)

        if toks[i].type == TokenType.LBRACE:
            # {nome, idade} := registro
            i += 1
            vistos = 0
            while i < n and toks[i].type != TokenType.RBRACE:
                if toks[i].type == TokenType.IDENTIFIER:
                    vistos += 1
                elif toks[i].type not in (TokenType.COMMA, TokenType.SPREAD):
                    return False
                i += 1
            if i >= n or vistos == 0:
                return False
            return i + 1 < n and toks[i + 1].type == TokenType.ASSIGN

        if toks[i].type not in (TokenType.IDENTIFIER, TokenType.SPREAD):
            return False
        tem_virgula = False
        while i < n:
            if toks[i].type == TokenType.SPREAD:
                i += 1
                continue
            if toks[i].type != TokenType.IDENTIFIER:
                return False
            i += 1
            if i < n and toks[i].type == TokenType.COMMA:
                tem_virgula = True
                i += 1
                continue
            break
        return tem_virgula and i < n and toks[i].type == TokenType.ASSIGN

    def parse_destructuring(self):
        """a, b := lista   |   a, ...resto := lista   |   {nome, idade} := registro"""
        tok = self.current()
        alvos = []
        is_mapping = False

        if self.match(TokenType.LBRACE):
            is_mapping = True
            while self.current().type != TokenType.RBRACE:
                resto = bool(self.match(TokenType.SPREAD))
                nome = self.expect(TokenType.IDENTIFIER,
                                   "Expected a field name to destructure").value
                alvos.append((nome, resto))
                self.match(TokenType.COMMA)
            self.expect(TokenType.RBRACE)
        else:
            while True:
                resto = bool(self.match(TokenType.SPREAD))
                nome = self.expect(TokenType.IDENTIFIER,
                                   "Expected a name to destructure into").value
                alvos.append((nome, resto))
                if not self.match(TokenType.COMMA):
                    break

        restos = [n for n, r in alvos if r]
        if len(restos) > 1:
            self.error("Only one '...rest' target is allowed when destructuring")

        self.expect(TokenType.ASSIGN, "Expected ':=' in the destructuring")
        valor = self.parse_expression()

        # Lado direito com vírgulas vira uma lista: a, b := b, a (troca)
        if self.current().type == TokenType.COMMA:
            elementos = [valor]
            while self.match(TokenType.COMMA):
                elementos.append(self._parse_element())
            valor = ast.ListLiteral(elements=elementos,
                                    line=valor.line, column=valor.column)
        self.match(TokenType.NEWLINE)
        return ast.DestructuringAssignment(
            targets=alvos, value=valor, is_mapping=is_mapping,
            line=tok.line, column=tok.column)

    #: O que cada alvo invalido e, e o que fazer.
    #:
    #: Uma mensagem que so diz "alvo invalido" deixa a pessoa procurando o
    #: erro de sintaxe que nao existe: a sintaxe esta certa, o alvo e que
    #: nao e um lugar onde se guarda valor.
    _ALVOS_INVALIDOS = {
        "FunctionCall": ("the result of a call",
                         "store the result first:  x := f(…)"),
        "MethodCall": ("the result of a call",
                       "store the result first:  x := obj.m(…)"),
        "IntegerLiteral": ("a number", "assign to a name:  x := 1"),
        "FloatLiteral": ("a number", "assign to a name:  x := 1.5"),
        "StringLiteral": ("a text", 'assign to a name:  x := "a"'),
        "BooleanLiteral": ("a boolean", "assign to a name:  x := yes"),
        "VoidLiteral": ("void", "assign to a name:  x := void"),
        "ListLiteral": ("a cluster written here",
                        "to unpack, drop the brackets:  a, b := [1, 2]"),
        "DictLiteral": ("a vault written here",
                        'to unpack, use  {nome, idade} := pessoa'),
        "BinaryOp": ("the result of a calculation",
                     "assign to a name:  x := a + b"),
        "ComparisonOp": ("the result of a comparison",
                         "':=' assigns; 'is' compares"),
        "SliceAccess": ("a slice",
                        "assign one position:  xs[0] := v"),
    }

    def _porque_nao_da_para_atribuir(self, expr):
        que_e, dica = self._ALVOS_INVALIDOS.get(
            type(expr).__name__, ("this", "assign to a name, a field, or an index"))
        return (f"Cannot assign to {que_e}. {dica[0].upper()}{dica[1:]}.")

    def _recusar_nomeado_repetido(self, kwargs, nome):
        """`f(a := 1, a := 2)` — o segundo apagava o primeiro, em silencio.

        Num vault isso e legitimo (a ultima chave vence, e a linguagem diz
        isso), mas numa CHAMADA nao ha leitura possivel: um dos dois valores
        foi escrito por engano, e adivinhar qual e o que nao se pode fazer.
        'P(x := 1, x := 2)' construia o record com 2 e ninguem sabia.
        """
        if nome in kwargs:
            self.error(
                f"'{nome}' was given twice in the same call. "
                f"Remove one of them.")

    def _recusar_parametro_repetido(self, params, nome):
        """`action f(a, a)` — o primeiro nao tinha como ser lido.

        `f(1, 2)` devolvia 2, e o parametro de cima ficava inalcancavel:
        um dos dois nomes foi escrito por engano. E o irmao do argumento
        nomeado repetido, do lado da declaracao.
        """
        if nome in params:
            self.error(
                f"'{nome}' is declared twice in the same parameter list. "
                f"Rename one of them.")

    def _recusar_obrigatorio_depois_de_padrao(self, nome, defaults):
        """`action f(a := 1, b)` — a declaracao se contradiz.

        O padrao de `a` nunca pode ser usado: `f(2)` deixa `b` sem valor, e
        `f(2, 3)` passa por cima do padrao. Os dois jeitos de chamar estao
        errados, e a declaracao passava limpa.
        """
        if defaults:
            anterior = list(defaults)[-1]
            self.error(
                f"'{nome}' has no default but comes after '{anterior}', "
                f"which has one. Move it before '{anterior}'.")

    def parse_expression_statement(self):
        """Parse an expression, an assignment, or a typed declaration."""
        if self._looks_like_destructuring():
            return self.parse_destructuring()

        start = self.current()

        # Uma palavra RESERVADA seguida de ':=' e erro de nome, e a mensagem
        # a nomeia em vez de apontar para o que o parser daquela palavra
        # engasgou.
        #
        # A condicao exige que ela esteja em KEYWORDS: antes bastava nao ser
        # identificador, e por isso '"a" := 1' respondia "'a' e palavra
        # reservada" — 'a' e o conteudo de um TEXTO, e nao uma palavra da
        # linguagem. Quem lesse aquilo trocaria o nome de uma variavel que
        # nao existe.
        if (start.type not in (TokenType.IDENTIFIER, TokenType.SELF)
                and start.text in KEYWORDS
                and self.peek().type == TokenType.ASSIGN):
            self.error(
                f"'{start.text}' is a reserved keyword and cannot be assigned to. "
                f"Pick another name.")

        expr = self.parse_expression()

        # Um alvo que nao pode receber valor. Aqui ha DUAS causas, e elas
        # pediam mensagens diferentes: a palavra reservada, e o alvo que
        # nao e um lugar onde se guarda algo.
        #
        # Este ramo dizia "palavra reservada" para as duas. 'f() := 2'
        # respondia "'f' e palavra reservada e nao pode receber valor.
        # Escolha outro nome." — e 'f' nao e reservada, e renomear nao
        # conserta nada: o problema e atribuir ao RESULTADO de uma chamada.
        if self.current().type == TokenType.ASSIGN and not isinstance(
                expr, (ast.Identifier, ast.MemberAccess, ast.IndexAccess)):
            palavra = start.text
            if (start.type not in (TokenType.IDENTIFIER, TokenType.SELF)
                    and palavra in KEYWORDS):
                self.error(
                    f"'{palavra}' is a reserved keyword and cannot be assigned to. "
                    f"Pick another name.")
            self.error(self._porque_nao_da_para_atribuir(expr))

        # Typed declaration: name: Type := value
        if (self.current().type == TokenType.COLON
                and isinstance(expr, ast.Identifier)
                and self.peek().type == TokenType.IDENTIFIER
                and self._anotacao_termina_em_assign()):
            self.advance()  # ':'
            declared = self._parse_nome_de_tipo("Expected a type after ':'")
            self.advance()  # ':='
            value = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.Assignment(target=expr, value=value, declared_type=declared,
                                  line=expr.line, column=expr.column)

        # Assignment: target := value
        if self.current().type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.Assignment(target=expr, value=value, line=expr.line, column=expr.column)

        # Compound assignment: target += value (and friends)
        if self.current().type in self.COMPOUND_ASSIGN:
            op = self.COMPOUND_ASSIGN[self.current().type]
            self.advance()
            rhs = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return ast.Assignment(target=expr, value=rhs, compound_op=op,
                                  line=expr.line, column=expr.column)

        self.match(TokenType.NEWLINE)
        return expr  # Expression statement

    # ── Expression Parsing (Precedence Climbing) ───────────

    def parse_expression(self):
        """Parse a full expression."""
        return self.parse_pipeline()

    def parse_pipeline(self):
        """expr >> sift/morph/distill ..."""
        expr = self.parse_ternary()

        if self.current().type == TokenType.PIPE:
            ops = []
            while self.match(TokenType.PIPE):
                op = self.parse_pipeline_op()
                ops.append(op)
            return ast.PipelineExpression(source=expr, operations=ops, line=expr.line, column=expr.column)

        return expr

    #: Os verbos de quadro, reconhecidos SO depois de um '>>'.
    #:
    #: Eles nao entram em KEYWORDS de proposito. 'agrupar', 'ordenar',
    #: 'onde' e 'pegar' sao nomes bons demais para tirar de quem escreve
    #: — e o repositorio ja removeu sete palavras reservadas por serem
    #: caras sem entregar nada. E o mesmo tratamento das onze palavras do
    #: Kiln: contextuais, e livres em todo o resto.
    VERBOS_DE_QUADRO = {
        "onde":    "expressao",   # filtra, com as colunas como nomes nus
        "pegar":   "colunas",     # escolhe colunas
        "sem":     "colunas",     # descarta colunas
        "agrupar": "colunas",     # agrupa
        "resumir": "expressao",   # agrega, recebendo um vault
        "ordenar": "ordem",       # ordena, com 'desc' opcional
    }

    def _e_verbo_de_quadro(self):
        tok = self.current()
        return (tok.type is TokenType.IDENTIFIER
                and tok.value in self.VERBOS_DE_QUADRO)

    def _parse_verbo_de_quadro(self):
        """`>> onde valor bigger 50`, `>> agrupar "cidade"`, `>> ordenar v desc`."""
        tok = self.advance()
        verbo = tok.value
        forma = self.VERBOS_DE_QUADRO[verbo]

        if forma == "expressao":
            return ast.QuadroOperation(
                verbo=verbo, expressao=self.parse_or(),
                line=tok.line, column=tok.column)

        if forma == "ordem":
            coluna = self._nome_de_coluna()
            # 'desc' tambem e contextual: so aqui, e so depois do nome.
            decrescente = (self.current().type is TokenType.IDENTIFIER
                           and self.current().value in ("desc", "decrescente"))
            if decrescente:
                self.advance()
            return ast.QuadroOperation(
                verbo=verbo, colunas=[coluna], decrescente=decrescente,
                line=tok.line, column=tok.column)

        colunas = [self._nome_de_coluna()]
        while self.match(TokenType.COMMA):
            colunas.append(self._nome_de_coluna())
        return ast.QuadroOperation(verbo=verbo, colunas=colunas,
                                   line=tok.line, column=tok.column)

    def _nome_de_coluna(self):
        """Uma coluna se escreve nua (`valor`) ou entre aspas (`"valor"`).

        As duas formas existem porque nem todo cabecalho de CSV e um
        identificador valido: 'Valor Total' e 'preco/kg' sao nomes de
        coluna comuns, e so a forma com aspas os alcanca.
        """
        tok = self.current()
        if tok.type is TokenType.STRING:
            return self.advance().value
        if tok.type in (TokenType.IDENTIFIER, TokenType.INTEGER):
            return str(self.advance().value)
        self.error(
            "era esperado o nome de uma coluna aqui.\n"
            '    Escreva-o nu (agrupar cidade) ou entre aspas '
            '(agrupar "Valor Total").')

    def parse_pipeline_op(self):
        """Parse sift/morph/distill pipeline operation.
        Supports both inline lambda and named function reference:
          sift param: condition    OR    sift func_name
          morph param: expression  OR    morph func_name
          distill acc, val: expr   OR    distill func_name initial_value
        """
        tok = self.current()

        if self._e_verbo_de_quadro():
            return self._parse_verbo_de_quadro()

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

    def parse_ternary(self):
        """valor given condicao otherwise alternativa.

        Le-se "este valor, dado que a condicao vale, senao o outro".
        Nao se aplica em contexto de padrao (guardas usam 'when').
        """
        expr = self.parse_coalesce()
        if self._no_ternary or self.current().type != TokenType.GIVEN:
            return expr
        self.advance()  # given
        condition = self.parse_coalesce()
        self.expect(TokenType.OTHERWISE,
                    "Expected 'otherwise' to close the conditional expression")
        alternativa = self.parse_ternary()
        return ast.TernaryExpression(
            then_value=expr, condition=condition, else_value=alternativa,
            line=expr.line, column=expr.column)

    def parse_coalesce(self):
        """a ?? b — b entra em cena so quando a e void."""
        left = self.parse_or()
        while self.current().type == TokenType.COALESCE:
            self.advance()
            right = self.parse_or()
            left = ast.CoalesceOp(left=left, right=right,
                                  line=left.line, column=left.column)
        return left

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

    COMPARISON_OPS = {
        TokenType.IS: "is",
        TokenType.ISNT: "isnt",
        TokenType.BIGGER: "bigger",
        TokenType.SMALLER: "smaller",
        TokenType.BIGGER_EQ: "bigger_eq",
        TokenType.SMALLER_EQ: "smaller_eq",
        TokenType.EQUAL: "==",
        TokenType.NOT_EQUAL: "!=",
        TokenType.GT: "bigger",
        TokenType.LT: "smaller",
        TokenType.GT_EQ: "bigger_eq",
        TokenType.LT_EQ: "smaller_eq",
    }

    def _operador_de_comparacao(self):
        """O operador de comparacao a seguir, ja consumido, ou None.

        'is not' sao dois tokens e UM operador — o mesmo que 'isnt'.
        Sem tratar o par aqui, ele era lido como 'is' aplicado a
        '(not x)': '5 is not 3' virava '5 is no' e respondia 'no'.
        Compilava, rodava, passava no analisador e no lint, e dava a
        resposta errada em silencio.

        E o mesmo par que 'not in' ja formava logo acima; quem vem do
        Python escreve os dois sem pensar.
        """
        tipo = self.current().type
        if tipo not in self.COMPARISON_OPS:
            return None
        if tipo == TokenType.IS and self.peek().type == TokenType.NOT:
            self.advance()
            self.advance()
            return "isnt"
        self.advance()
        return self.COMPARISON_OPS[tipo]

    def parse_comparison(self):
        """Comparisons, including chains such as '1 smaller x smaller 10'."""
        left = self.parse_addition()

        # Pertinencia: x in colecao / x not in colecao
        if self.current().type == TokenType.IN and not self._no_membership:
            self.advance()
            container = self.parse_addition()
            return ast.MembershipOp(element=left, container=container, negated=False,
                                    line=left.line, column=left.column)
        if (self.current().type == TokenType.NOT
                and self.peek().type == TokenType.IN and not self._no_membership):
            self.advance(); self.advance()
            container = self.parse_addition()
            return ast.MembershipOp(element=left, container=container, negated=True,
                                    line=left.line, column=left.column)

        op = self._operador_de_comparacao()
        if op is None:
            return left

        right = self.parse_addition()
        result = ast.ComparisonOp(left=left, op=op, right=right,
                                  line=left.line, column=left.column)

        # Chained comparison: a < b < c  ==>  (a < b) and (b < c)
        while True:
            op = self._operador_de_comparacao()
            if op is None:
                break
            next_right = self.parse_addition()
            link = ast.ComparisonOp(left=right, op=op, right=next_right,
                                    line=right.line, column=right.column)
            result = ast.LogicalOp(left=result, op="and", right=link,
                                   line=result.line, column=result.column)
            right = next_right

        return result

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = ast.BinaryOp(left=left, op=op, right=right, line=left.line, column=left.column)
        return left

    def parse_multiplication(self):
        left = self.parse_unary()
        while self.current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.FLOOR_DIV):
            op = self.advance().value
            right = self.parse_unary()
            left = ast.BinaryOp(left=left, op=op, right=right, line=left.line, column=left.column)
        return left

    def parse_unary(self):
        """Sign and 'not', binding looser than '**' so -2 ** 2 == -(2 ** 2)."""
        if self.current().type == TokenType.PLUS:
            tok = self.advance()
            operand = self.parse_unary()
            return ast.UnaryOp(op="+", operand=operand, line=tok.line, column=tok.column)
        if self.current().type == TokenType.MINUS:
            tok = self.advance()
            operand = self.parse_unary()
            return ast.UnaryOp(op="-", operand=operand, line=tok.line, column=tok.column)
        if self.current().type == TokenType.NOT:
            tok = self.advance()
            operand = self.parse_unary()
            return ast.NotOp(operand=operand, line=tok.line, column=tok.column)
        return self.parse_power()

    def parse_power(self):
        """Exponentiation, right-associative: 2 ** 3 ** 2 == 2 ** (3 ** 2)."""
        base = self.parse_postfix()
        if self.current().type == TokenType.POWER:
            self.advance()
            exp = self.parse_unary()
            return ast.BinaryOp(left=base, op="**", right=exp, line=base.line, column=base.column)
        return base

    def _parse_subscript(self, expr):
        """Parse the inside of '[...]': an index or a slice (start:stop:step)."""
        start = None
        if self.current().type != TokenType.COLON:
            start = self.parse_expression()

        if self.current().type != TokenType.COLON:
            self.expect(TokenType.RBRACKET)
            return ast.IndexAccess(object=expr, index=start,
                                   line=expr.line, column=expr.column)

        self.advance()  # first ':'
        stop = None
        step = None
        if self.current().type not in (TokenType.RBRACKET, TokenType.COLON):
            stop = self.parse_expression()
        if self.match(TokenType.COLON):
            if self.current().type != TokenType.RBRACKET:
                step = self.parse_expression()
        self.expect(TokenType.RBRACKET)
        return ast.SliceAccess(object=expr, start=start, stop=stop, step=step,
                               line=expr.line, column=expr.column)

    def parse_postfix(self):
        """Handle member access, indexing, and function calls."""
        expr = self.parse_primary()

        while True:
            if self.current().type == TokenType.DOT:
                self.advance()
                member = self.expect_member_name()

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
            elif self.current().type == TokenType.SAFE_DOT:
                self.advance()
                member = self.expect_member_name()
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args, kwargs = self._parse_call_args()
                    self.expect(TokenType.RPAREN)
                    expr = ast.SafeMethodCall(
                        object=expr, method=member, args=args, kwargs=kwargs,
                        line=expr.line, column=expr.column)
                else:
                    expr = ast.SafeMemberAccess(
                        object=expr, member=member,
                        line=expr.line, column=expr.column)
            elif (self.current().type == TokenType.WITH
                  and self.peek().type == TokenType.LBRACE
                  and not self._no_with):
                # registro with {"campo": novo_valor}
                self.advance()
                changes = self.parse_dict()
                expr = ast.WithExpression(source=expr, changes=changes,
                                          line=expr.line, column=expr.column)
            elif self.current().type == TokenType.LBRACKET:
                self.advance()
                expr = self._parse_subscript(expr)
            elif self.current().type == TokenType.LPAREN and isinstance(
                    expr, (ast.Identifier, ast.FunctionCall, ast.MethodCall,
                           ast.IndexAccess, ast.MemberAccess)):
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

    def _alvo_de_spawn(self, tok):
        """O nome e os argumentos de um `spawn`, sem comer o resto.

        Devolve `None` quando o que vem depois do `spawn` não é um nome —
        aí o caminho antigo assume, e nada que funcionava deixa de
        funcionar.
        """
        if self.current().type != TokenType.IDENTIFIER:
            return None
        alvo = ast.Identifier(name=self.advance().value,
                              line=tok.line, column=tok.column)
        # 'spawn Modulo.Blueprint(...)': o caminho pontilhado é o nome do
        # que se constrói.
        while self.current().type == TokenType.DOT:
            self.advance()
            alvo = ast.MemberAccess(object=alvo, member=self.expect_member_name(),
                                    line=tok.line, column=tok.column)
        args, kwargs = [], {}
        if self.current().type == TokenType.LPAREN:
            self.advance()
            args, kwargs = self._parse_call_args()
            self.expect(TokenType.RPAREN)
        return ast.SpawnExpression(class_name=alvo, args=args, kwargs=kwargs,
                                   line=tok.line, column=tok.column)

    def parse_primary(self):
        """Parse primary expressions (literals, identifiers, grouped)."""
        tok = self.current()

        # before(expr) — so dentro de 'promises', onde tem sentido: o
        # valor da expressao na ENTRADA da acao. Fora dali, 'before' e um
        # nome como outro qualquer.
        if (getattr(self, "_em_promessa", 0) and tok.type == TokenType.IDENTIFIER
                and tok.value == "before" and self.peek(1).type == TokenType.LPAREN):
            self.advance()
            self.advance()
            interna = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' to close 'before('")
            return ast.BeforeExpression(expression=interna,
                                        line=tok.line, column=tok.column)

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

        # String interpolada: $"texto {expr}"
        if tok.type == TokenType.INTERP_STRING:
            self.advance()
            partes = []
            for tipo, conteudo in tok.value:
                if tipo == 'text':
                    partes.append(('text', conteudo))
                elif tipo == 'fmt':
                    expressao, formato = conteudo
                    partes.append(('fmt', (
                        self._parse_sub_expression(expressao, tok), formato)))
                else:
                    partes.append(('expr', self._parse_sub_expression(conteudo, tok)))
            return ast.InterpolatedString(parts=partes, line=tok.line, column=tok.column)

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
                member = self.expect_member_name()
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
                member = self.expect_member_name()
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
            # O 'spawn' leva o NOME e os argumentos do construtor, e para
            # ali. Com 'parse_postfix' ele comia a cadeia inteira, e
            # 'spawn B().f()' virava 'spawn (B().f())': o que chegava para
            # construir era o resultado de um método, e a mensagem culpava
            # a ação. Devolvendo daqui, o pós-fixo de quem nos chamou
            # aplica '.f()' sobre a instância — que é o que está escrito.
            restrito = self._alvo_de_spawn(tok)
            if restrito is not None:
                return restrito
            class_expr = self.parse_postfix()
            if isinstance(class_expr, ast.FunctionCall):
                return ast.SpawnExpression(
                    class_name=class_expr.callee, args=class_expr.args,
                    kwargs=class_expr.kwargs, line=tok.line, column=tok.column
                )
            # 'spawn Modulo.Blueprint(args)' chega como MethodCall. O que
            # se quer construir e 'Modulo.Blueprint'; os argumentos vao
            # para o construtor, nao para uma chamada de metodo.
            if isinstance(class_expr, ast.MethodCall):
                alvo = ast.MemberAccess(
                    object=class_expr.object, member=class_expr.method,
                    line=class_expr.line, column=class_expr.column)
                return ast.SpawnExpression(
                    class_name=alvo, args=class_expr.args,
                    kwargs=class_expr.kwargs, line=tok.line, column=tok.column
                )
            return ast.SpawnExpression(class_name=class_expr, line=tok.line, column=tok.column)

        # Lambda: lambda a, b: expr   |   lambda a, b => expr   |   lambda: expr
        if tok.type == TokenType.LAMBDA:
            self.advance()
            params = []
            param_types = {}
            defaults = {}
            has_parens = bool(self.match(TokenType.LPAREN))
            while self.current().type == TokenType.IDENTIFIER:
                name = self.advance().value
                self._recusar_parametro_repetido(params, name)
                params.append(name)
                # A ':' type annotation is only unambiguous inside parentheses;
                # without them 'lambda n: n' means the body starts at ':'.
                if has_parens and self.match(TokenType.COLON):
                    param_types[name] = self._parse_nome_de_tipo(
                        "Expected a type name after ':'")
                if self.match(TokenType.ASSIGN):
                    defaults[name] = self.parse_or()
                else:
                    self._recusar_obrigatorio_depois_de_padrao(name, defaults)
                if not self.match(TokenType.COMMA):
                    break
            if has_parens:
                self.expect(TokenType.RPAREN, "Expected ')' after lambda parameters")
            if not self.match(TokenType.COLON, TokenType.FAT_ARROW):
                self.error("Expected ':' or '=>' after lambda parameters")
            body = self._corpo_de_lambda()
            return ast.LambdaExpression(params=params, defaults=defaults,
                                        param_types=param_types, body=body,
                                        line=tok.line, column=tok.column)

        # Stream: stream <expr>
        if tok.type == TokenType.STREAM:
            self.advance()
            source = self.parse_or()
            return ast.StreamExpression(source=source, line=tok.line, column=tok.column)

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
            # 'parse_unary', e nao 'parse_expression': 'await' aperta como
            # operador unario, igual a 'typeof' e a 'cast'. Com a
            # expressao inteira, 'await buscar() is "ok"' virava
            # 'await (buscar() is "ok")' — aguardava a COMPARACAO e
            # devolvia o booleano dela. O erro ficou escondido enquanto
            # 'await' era identidade, porque comparar antes ou depois de
            # nao fazer nada da no mesmo.
            expr = self.parse_unary()
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

        # Tupla, ou agrupamento: '(1, "a")' e tupla; '(1)' e agrupamento.
        if tok.type == TokenType.LPAREN:
            self.advance()
            # '()' — a tupla vazia.
            if self.current().type is TokenType.RPAREN:
                self.advance()
                return ast.TupleLiteral(elements=[], line=tok.line,
                                        column=tok.column)
            primeiro = self.parse_expression()
            if self.current().type is not TokenType.COMMA:
                self.expect(TokenType.RPAREN, "Expected ')'")
                return primeiro
            itens = [primeiro]
            while self.match(TokenType.COMMA):
                # '(7,)' — a virgula sozinha faz a tupla de um item, e e a
                # unica forma de escreve-la: '(7)' e o numero 7.
                if self.current().type is TokenType.RPAREN:
                    break
                itens.append(self.parse_expression())
            self.expect(TokenType.RPAREN, "Expected ')' to close the tuple")
            return ast.TupleLiteral(elements=itens, line=tok.line,
                                    column=tok.column)

        # Identifier
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return ast.Identifier(name=tok.value, line=tok.line, column=tok.column)

        word = tok.text
        if word and self.peek().type in (TokenType.ASSIGN, TokenType.COLON):
            self.error(
                f"'{word}' is a reserved keyword and cannot be used as a name. "
                f"Pick another identifier.")
        if word:
            self.error(f"Unexpected token: {tok.type.name} ('{word}')")
        self.error(f"Unexpected token: {tok.type.name} ({tok.value!r})")

    def _parse_sub_expression(self, fonte: str, tok):
        """Compila o trecho de dentro de {...} numa expressao."""
        from .lexer import tokenize
        try:
            sub_tokens = tokenize(fonte, self.filename)
            sub = Parser(sub_tokens, self.filename)
            expr = sub.parse_expression()
        except ParseError as e:
            raise ParseError(
                f"Invalid expression inside the interpolated string "
                f"({{{fonte}}}): {e.message}", tok.line, tok.column)
        # O trecho e compilado isolado, entao os nos nascem na linha 1.
        # Reposicionar so a raiz nao basta: qualquer ferramenta que desca
        # na arvore — o linter, um futuro LSP — encontraria linha 1 nos
        # filhos, e mediria distancias absurdas. Reposiciona tudo.
        self._reposicionar(expr, tok.line, tok.column)
        return expr

    @classmethod
    def _reposicionar(cls, node, linha, coluna):
        """Poe a subarvore inteira na posicao da string que a contem."""
        if not isinstance(node, ast.ASTNode):
            return
        node.line, node.column = linha, coluna
        for campo, valor in vars(node).items():
            if campo in ('line', 'column'):
                continue
            if isinstance(valor, ast.ASTNode):
                cls._reposicionar(valor, linha, coluna)
            elif isinstance(valor, list):
                for item in valor:
                    cls._reposicionar(item, linha, coluna)
            elif isinstance(valor, dict):
                for item in valor.values():
                    cls._reposicionar(item, linha, coluna)
        return node

    def parse_list(self):
        """[a, b, c]  |  [...a, b]  |  [expr cycle x in fonte given cond]"""
        tok = self.advance()  # [
        self.skip_newlines()

        if self.current().type == TokenType.RBRACKET:
            self.advance()
            return ast.ListLiteral(elements=[], line=tok.line, column=tok.column)

        primeiro = self._parse_element()
        self.skip_newlines()

        # Compreensao de lista
        if self.current().type == TokenType.CYCLE:
            clauses = self._parse_comprehension_clauses(TokenType.RBRACKET)
            self.expect(TokenType.RBRACKET)
            return ast.ListComprehension(expression=primeiro, clauses=clauses,
                                         line=tok.line, column=tok.column)

        elements = [primeiro]
        self.match(TokenType.COMMA)
        self.skip_newlines()
        while self.current().type != TokenType.RBRACKET:
            self.skip_newlines()
            elements.append(self._parse_element())
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACKET)
        return ast.ListLiteral(elements=elements, line=tok.line, column=tok.column)

    def _parse_element(self):
        """Um elemento de literal: expressao ou '...expr'."""
        if self.current().type == TokenType.SPREAD:
            tok = self.advance()
            valor = self.parse_expression()
            return ast.SpreadElement(value=valor, line=tok.line, column=tok.column)
        return self.parse_expression()

    def _parse_comprehension_clauses(self, fim):
        """Uma ou mais clausulas 'cycle x in fonte [given cond]'."""
        clauses = []
        while self.current().type == TokenType.CYCLE:
            tok = self.advance()
            alvos = [self.expect(TokenType.IDENTIFIER,
                                 "Expected a name after 'cycle'").value]
            while self.match(TokenType.COMMA):
                alvos.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.IN, "Expected 'in' after the comprehension name")
            self._no_membership += 1
            self._no_ternary += 1
            try:
                fonte = self.parse_expression()
            finally:
                self._no_membership -= 1
                self._no_ternary -= 1
            condicao = None
            if self.current().type == TokenType.GIVEN:
                self.advance()
                self._no_ternary += 1
                try:
                    condicao = self.parse_expression()
                finally:
                    self._no_ternary -= 1
            clauses.append(ast.ComprehensionClause(
                var=alvos[0], targets=alvos, source=fonte, condition=condicao,
                line=tok.line, column=tok.column))
            self.skip_newlines()
        if not clauses:
            self.error("Expected 'cycle' to start the comprehension")
        return clauses

    def parse_dict(self):
        """{k: v}  |  {...base, k: v}  |  {k: v cycle x in fonte given cond}"""
        tok = self.advance()  # {
        pairs = []
        self.skip_newlines()

        if self.current().type == TokenType.RBRACE:
            self.advance()
            return ast.DictLiteral(pairs=[], line=tok.line, column=tok.column)

        while self.current().type != TokenType.RBRACE:
            self.skip_newlines()
            if self.current().type == TokenType.SPREAD:
                stok = self.advance()
                pairs.append((ast.SpreadElement(value=self.parse_expression(),
                                                line=stok.line, column=stok.column),
                              None))
            else:
                chave = self.parse_expression()
                self.expect(TokenType.COLON, "Expected ':' between key and value")
                valor = self.parse_expression()

                # Compreensao de vault, detectada apos o primeiro par
                if not pairs and self.current().type == TokenType.CYCLE:
                    clauses = self._parse_comprehension_clauses(TokenType.RBRACE)
                    self.expect(TokenType.RBRACE)
                    return ast.VaultComprehension(
                        key=chave, value=valor, clauses=clauses,
                        line=tok.line, column=tok.column)

                pairs.append((chave, valor))
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return ast.DictLiteral(pairs=pairs, line=tok.line, column=tok.column)

    # ── Helper: parse parameters ───────────────────────────

    def _anotacao_termina_em_assign(self):
        """'x: M.Pedido := …' e anotacao; 'x: y' sozinho nao e.

        A conferencia era 'peek(2) e ASSIGN', o que so enxerga um nome
        de tipo de UMA palavra. Com 'M.Pedido' os tokens sao
        COLON IDENT DOT IDENT ASSIGN, o ':=' esta duas casas mais
        adiante, e a linha caia em "Unexpected token: COLON".
        """
        i = 2
        while (self.peek(i).type == TokenType.DOT
               and self.peek(i + 1).type == TokenType.IDENTIFIER):
            i += 2
        # 'x: Cluster<Vault<String, Integer>> := …' — pula o generico
        # inteiro, contando '>>' como dois fechamentos: o lexer o entrega
        # como o operador de pipeline.
        if self.peek(i).type == TokenType.LT:
            profundidade = 0
            while True:
                tipo = self.peek(i).type
                if tipo == TokenType.LT:
                    profundidade += 1
                elif tipo == TokenType.GT:
                    profundidade -= 1
                elif tipo == TokenType.PIPE:
                    profundidade -= 2
                elif tipo in (TokenType.NEWLINE, TokenType.EOF, TokenType.ASSIGN):
                    return False
                i += 1
                if profundidade <= 0:
                    break
        # 'x: Integer | String := 1' — a uniao faz parte da anotacao, e
        # sem isto a linha inteira caia em "Unexpected token: COLON".
        while self.peek(i).type in (TokenType.VBAR, TokenType.AMP):
            i += 1
            if self.peek(i).type is not TokenType.IDENTIFIER:
                return False
            i += 1
            while (self.peek(i).type == TokenType.DOT
                   and self.peek(i + 1).type == TokenType.IDENTIFIER):
                i += 2
            if self.peek(i).type == TokenType.LT:
                profundidade = 0
                while True:
                    tipo = self.peek(i).type
                    if tipo == TokenType.LT:
                        profundidade += 1
                    elif tipo == TokenType.GT:
                        profundidade -= 1
                    elif tipo == TokenType.PIPE:
                        profundidade -= 2
                    elif tipo in (TokenType.NEWLINE, TokenType.EOF,
                                  TokenType.ASSIGN):
                        return False
                    i += 1
                    if profundidade <= 0:
                        break
        return self.peek(i).type == TokenType.ASSIGN

    def _parse_nome_de_tipo(self, mensagem):
        """Um nome de tipo, que pode ser QUALIFICADO: 'M.Pedido'.

        Num projeto de um arquivo todo tipo e local, e um IDENTIFIER
        bastava. Num projeto modular a maioria dos tipos mora em outro
        arquivo, e a forma de nomea-los e a mesma de nomear qualquer
        coisa importada — 'M.Pedido'. O parser recusava as tres
        posicoes:

            action criar() -> M.Pedido:        Expected ':' after signature
            action ver(p: M.Pedido):           Expected IDENTIFIER, got DOT
            p: M.Pedido := M.Pedido(3)         Unexpected token: COLON

        Ou seja: dava para CRIAR o valor e nao dava para DECLARAR o
        tipo dele. Quem quisesse tipar um sistema de muitos modulos
        tinha de desistir do tipo — e o analisador, que ja traduz
        '-> Pedido' do outro arquivo para 'M.Pedido' deste, falava um
        vocabulario que ninguem podia escrever.

        O ponto so e consumido quando o que vem depois e um nome
        colado a ele: 'M . Pedido' com espaco nao e um tipo, e sim o
        comeco de outra coisa.
        """
        nome = self.expect(TokenType.IDENTIFIER, mensagem).value
        while (self.current().type == TokenType.DOT
               and self.peek().type == TokenType.IDENTIFIER):
            self.advance()
            nome += "." + self.advance().value
        # 'Cluster<Integer>', 'Vault<String, Cluster<Integer>>', 'Set<T>':
        # o tipo do CONTEUDO. Ate aqui era recusado com a frase "o tipo do
        # que esta dentro nao e verificado" — agora e verificado na
        # fronteira, na insercao e pelo 'check'. Ver colecoes_tipadas.py.
        if self.current().type == TokenType.LT:
            nome = self._parse_argumentos_de_colecao(nome)
        if self.current().type in (TokenType.VBAR, TokenType.AMP):
            return self._juntar_tipos(nome)
        return nome

    def _parse_argumentos_de_colecao(self, base):
        from .colecoes_tipadas import COLECOES, FORMA
        inicio = self.current()
        proprio = self._tipos_genericos.get(base.rsplit(".", 1)[-1])
        if base not in COLECOES and proprio is None:
            self.error(
                f"'{base}<…>' is not a collection type: only Cluster<T>, "
                f"Vault<K, V> and Set<T> declare the type of what is inside — "
                f"or a 'type {base}<T> := …' declared in this file. "
                f"Annotate as '{base}'.", inicio)
        self.advance()                                   # '<'
        argumentos = []
        while True:
            atual = self.current()
            # 'Vetor<3>' — o argumento e um VALOR, e nao um tipo. Vale so
            # para um generico declarado neste arquivo: 'Cluster<3>' nao
            # quer dizer nada, e continua sendo erro.
            if proprio is not None and atual.type in (TokenType.INTEGER,
                                                      TokenType.FLOAT):
                self.advance()
                argumentos.append(str(atual.value))
            else:
                argumentos.append(self._parse_nome_de_tipo(
                    f"Expected a type inside '{base}<…>'"))
            if not self.match(TokenType.COMMA):
                break
        # '>>' fecha dois de uma vez: 'Cluster<Cluster<Integer>>'. O lexer
        # nao tem como saber que ali nao e o pipeline, entao quem fecha o
        # de dentro deixa um '>' pendente para o de fora.
        if getattr(self, "_fechamento_pendente", 0):
            self._fechamento_pendente -= 1
        elif self.current().type == TokenType.GT:
            self.advance()
        elif self.current().type == TokenType.PIPE:
            self.advance()
            self._fechamento_pendente = getattr(self, "_fechamento_pendente", 0) + 1
        else:
            self.error(f"Expected '>' to close '{base}<…>'")
        esperados = COLECOES.get(base, proprio)
        # 'Tuple<A, B, C>' — a aridade e livre, porque ela E o tamanho.
        if base in COLECOES and COLECOES[base] is None:
            esperados = len(argumentos)
        if len(argumentos) != esperados:
            quantos = ("one type" if esperados == 1 else
                       "two types: the key and the value" if base in COLECOES
                       else f"{esperados} types")
            forma = FORMA.get(base, f"{base}<…>")
            self.error(
                f"{forma} takes {quantos} — got {len(argumentos)} in "
                f"'{base}<{', '.join(argumentos)}>'.", inicio)
        return f"{base}<{', '.join(argumentos)}>"

    def _parse_params(self):
        """Parse a parameter list: (a, b: Integer, c := default)."""
        params = []
        defaults = {}
        types = {}
        while self.current().type != TokenType.RPAREN:
            name = self.expect(TokenType.IDENTIFIER).value
            self._recusar_parametro_repetido(params, name)
            params.append(name)
            if self.match(TokenType.COLON):
                types[name] = self._parse_nome_de_tipo(
                    "Expected a type name after ':'")
            if self.match(TokenType.ASSIGN):
                defaults[name] = self.parse_expression()
            else:
                self._recusar_obrigatorio_depois_de_padrao(name, defaults)
            self.match(TokenType.COMMA)
        return params, defaults, types

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
                self._recusar_nomeado_repetido(kwargs, name)
                kwargs[name] = value
            elif self.current().type == TokenType.SPREAD:
                stok = self.advance()
                args.append(ast.SpreadElement(value=self.parse_expression(),
                                              line=stok.line, column=stok.column))
            else:
                args.append(self.parse_expression())
            self.match(TokenType.COMMA)
        return args, kwargs


def parse(tokens: list[Token], filename: str = "<stdin>") -> ast.Program:
    """Convenience function to parse tokens into AST."""
    parser = Parser(tokens, filename)
    try:
        return parser.parse()
    except DataForgeError as erro:
        for um in [erro] + list(getattr(erro, "outros", ())):
            if not um.filename:
                um.filename = filename
        raise
