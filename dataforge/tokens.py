"""
DataForge Token Definitions
All token types used by the lexer and parser.
"""

from enum import Enum, auto


class TokenType(Enum):
    # ── Literals ──────────────────────────────────────────
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    INTERP_STRING = auto()   # $"texto {expr}" — valor e a lista de partes
    BOOLEAN = auto()         # yes / no
    VOID = auto()            # void
    IDENTIFIER = auto()

    # ── Assignment & Operators ────────────────────────────
    ASSIGN = auto()          # :=
    COLON = auto()           # :
    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    PERCENT = auto()         # %
    POWER = auto()           # **
    FLOOR_DIV = auto()       # //
    PIPE = auto()            # >>  (pipeline)
    ARROW = auto()           # ->  (return type annotation)
    FAT_ARROW = auto()       # =>  (lambda body)
    PLUS_ASSIGN = auto()     # +=
    MINUS_ASSIGN = auto()    # -=
    STAR_ASSIGN = auto()     # *=
    SLASH_ASSIGN = auto()    # /=
    PERCENT_ASSIGN = auto()  # %=
    SPREAD = auto()          # ...  (spread / rest)
    SAFE_DOT = auto()        # ?.   (acesso seguro)
    COALESCE = auto()        # ??   (valor padrao para void)
    DOT = auto()             # .
    COMMA = auto()           # ,
    AT = auto()              # @

    # ── Delimiters ────────────────────────────────────────
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    LBRACE = auto()          # {
    RBRACE = auto()          # }

    # ── Comparison ────────────────────────────────────────
    IS = auto()              # is
    ISNT = auto()            # isnt
    BIGGER = auto()          # bigger
    SMALLER = auto()         # smaller
    BIGGER_EQ = auto()       # bigger_eq
    SMALLER_EQ = auto()      # smaller_eq
    EQUAL = auto()           # ==
    NOT_EQUAL = auto()       # !=
    LT = auto()              # <   (alias of smaller)
    GT = auto()              # >   (alias of bigger)
    LT_EQ = auto()           # <=  (alias of smaller_eq)
    GT_EQ = auto()           # >=  (alias of bigger_eq)

    # ── Logic ─────────────────────────────────────────────
    AND = auto()             # and
    OR = auto()              # or
    NOT = auto()             # not

    # ── Foundation ────────────────────────────────────────
    STEADY = auto()          # steady (const)
    OUT = auto()             # out (print)
    IN = auto()              # in (input/in-keyword)
    TYPEOF = auto()          # typeof
    SHADOW = auto()          # shadow

    # ── Conditionals ──────────────────────────────────────
    GIVEN = auto()           # given (if)
    ORIF = auto()            # orif (else if)
    OTHERWISE = auto()       # otherwise (else)
    MATCH = auto()           # match (switch)
    POINT = auto()           # point (case)
    DEFAULT = auto()         # default

    # ── Loops ─────────────────────────────────────────────
    CYCLE = auto()           # cycle (for)
    PERSIST = auto()         # persist (while)
    PERFORM = auto()         # perform (do-while)
    HALT = auto()            # halt (break)
    SKIP = auto()            # skip (continue)
    FROM = auto()            # from (range start)
    TO = auto()              # to (range end)
    STEP = auto()            # step (range step)

    # ── Structure & Modularity ────────────────────────────
    ACTION = auto()          # action (function)
    YIELD = auto()           # yield (return)
    BLUEPRINT = auto()       # blueprint (class)
    SPAWN = auto()           # spawn (new)
    SELF = auto()            # self
    ROOT = auto()            # root (super)
    ADOPT = auto()           # adopt (import)
    RELAY = auto()           # relay (export)
    TRAIT = auto()           # trait (interface)
    STATIC = auto()          # static
    ABSTRACT = auto()
    SLOTS = auto()           # slots  (restringe os campos da instancia)        # abstract
    GET = auto()             # get      (propriedade de leitura)
    SET = auto()             # set      (propriedade de escrita)
    PRIVATE = auto()         # private  (so dentro do blueprint)
    PROTECTED = auto()       # protected (blueprint e herdeiros)
    OPERATOR = auto()        # operator (sobrecarga)
    FINAL = auto()           # final    (nao pode ser sobrescrito)

    # ── Error Handling ────────────────────────────────────
    MONITOR = auto()         # monitor (try)
    HANDLE = auto()          # handle (catch)
    ENSURE = auto()          # ensure (finally)
    TRIGGER = auto()         # trigger (raise)
    RETRY = auto()           # retry (retry block)
    RECOVER = auto()         # recover (recover handler)
    GUARD = auto()           # guard (precondition check)
    PROPAGATE = auto()       # propagate (re-raise)
    VALIDATE = auto()        # validate (assertion-like)

    # ── Async & Concurrency ───────────────────────────────
    ASYNC = auto()           # async
    AWAIT = auto()           # await
    THREAD = auto()          # thread
    CHANNEL = auto()         # channel
    PULSE = auto()           # pulse (event emit)
    OBSERVE = auto()         # observe (reactive subscribe)
    STREAM = auto()          # stream (reactive stream)
    DEFER = auto()           # defer (deferred execution)
    PARALLEL = auto()        # parallel (parallel execution)

    # ── Metadata & Memory ─────────────────────────────────
    MARK = auto()            # mark (decorator)
    CLAIM = auto()           # claim (pointer take)
    RELEASE = auto()         # release (pointer free)

    # ── Data Science ──────────────────────────────────────
    FRAME = auto()           # frame (DataFrame)
    CLUSTER = auto()         # cluster (list/array)
    VAULT = auto()           # vault (dict/map)
    SIFT = auto()            # sift (filter)
    MORPH = auto()           # morph (map)
    DISTILL = auto()         # distill (reduce)
    TRAIN = auto()           # train (ML fit)
    PREDICT = auto()         # predict (ML infer)

    # ── Extra Keywords ────────────────────────────────────
    USING = auto()           # using
    WITH = auto()            # with
    AS = auto()              # as
    EXTENDS = auto()         # extends (inheritance)
    RANGE = auto()           # range
    WAIT = auto()            # wait (sleep)
    EMIT = auto()            # emit
    LISTEN = auto()          # listen
    EACH = auto()            # each
    FORGE = auto()           # forge (create/build)
    LINK = auto()            # link (connect)
    UNLINK = auto()          # unlink (disconnect)
    FREEZE = auto()          # freeze (lock)
    THAW = auto()            # thaw (unlock)
    CAST = auto()            # cast (type conversion)
    LAMBDA = auto()          # lambda (anonymous action)
    RECORD = auto()          # record (dado imutavel)
    ENUM = auto()            # enum
    WHEN = auto()            # when (guarda de pattern)
    INSPECT = auto()         # inspect (debug)
    ASSERT = auto()          # assert
    DELETE = auto()          # delete
    EXISTS = auto()          # exists

    # ── Kiln — framework web (contextuais) ────────────────
    SERVER = auto()          # server   (declara a aplicacao)
    ROUTE = auto()           # route    (declara uma rota)
    RESPOND = auto()         # respond  (envia a resposta)
    RENDER = auto()          # render   (renderiza um template)
    REDIRECT = auto()        # redirect (302 para outro caminho)
    MIDDLEWARE = auto()      # middleware (roda antes das rotas)
    MOUNT = auto()           # mount    (junta outro server sob um prefixo)
    ASSETS = auto()          # assets   (arquivos estaticos)
    VIEWS = auto()           # views    (pasta de templates)
    IGNITE = auto()          # ignite   (acende o forno: sobe o servidor)

    # ── Crucible — framework de testes (contextuais) ──────
    CRUCIBLE = auto()        # crucible (abre uma suite)
    TRIAL = auto()           # trial    (um caso de teste)
    EXPECT = auto()          # expect   (cobra um valor)
    FIXTURE = auto()         # fixture  (preparo compartilhado)
    PROVIDE = auto()         # provide  (entrega o valor da fixture)
    SETUP_ = auto()          # setup    (roda antes de cada trial)
    TEARDOWN = auto()        # teardown (roda depois de cada trial)
    TAGGED = auto()          # tagged   (marca o trial)
    PENDING = auto()         # pending  (nao roda, e diz por que)
    BENCH = auto()           # bench    (mede em vez de cobrar)

    # ── Structural ────────────────────────────────────────
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    COMMENT = auto()


class Token:
    """Represents a single token from the source code."""

    __slots__ = ('type', 'value', 'line', 'column', 'text')

    def __init__(self, type: TokenType, value, line: int = 0, column: int = 0,
                 text: str | None = None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        # Source spelling; differs from 'value' for yes/no/void.
        self.text = text if text is not None else (
            value if isinstance(value, str) else None)

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return NotImplemented


# ── Keyword map ─────────────────────────────────────────────
KEYWORDS = {
    # Foundation
    "steady": TokenType.STEADY,
    "void": TokenType.VOID,
    "yes": TokenType.BOOLEAN,
    "no": TokenType.BOOLEAN,
    "out": TokenType.OUT,
    "in": TokenType.IN,
    "typeof": TokenType.TYPEOF,
    "shadow": TokenType.SHADOW,

    # Logic
    "given": TokenType.GIVEN,
    "orif": TokenType.ORIF,
    "otherwise": TokenType.OTHERWISE,
    "match": TokenType.MATCH,
    "point": TokenType.POINT,
    "default": TokenType.DEFAULT,

    # Comparison & Logic
    "is": TokenType.IS,
    "isnt": TokenType.ISNT,
    "bigger": TokenType.BIGGER,
    "smaller": TokenType.SMALLER,
    "bigger_eq": TokenType.BIGGER_EQ,
    "smaller_eq": TokenType.SMALLER_EQ,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,

    # Loops
    "cycle": TokenType.CYCLE,
    "persist": TokenType.PERSIST,
    "perform": TokenType.PERFORM,
    "halt": TokenType.HALT,
    "skip": TokenType.SKIP,
    "from": TokenType.FROM,
    "to": TokenType.TO,
    "step": TokenType.STEP,

    # Structure
    "action": TokenType.ACTION,
    "yield": TokenType.YIELD,
    "blueprint": TokenType.BLUEPRINT,
    "spawn": TokenType.SPAWN,
    "self": TokenType.SELF,
    "root": TokenType.ROOT,
    "adopt": TokenType.ADOPT,
    "relay": TokenType.RELAY,
    "trait": TokenType.TRAIT,
    "static": TokenType.STATIC,

    # Error handling
    "monitor": TokenType.MONITOR,
    "handle": TokenType.HANDLE,
    "ensure": TokenType.ENSURE,
    "trigger": TokenType.TRIGGER,
    "retry": TokenType.RETRY,
    "recover": TokenType.RECOVER,
    "guard": TokenType.GUARD,
    "propagate": TokenType.PROPAGATE,
    "validate": TokenType.VALIDATE,

    # Async
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
    "thread": TokenType.THREAD,
    "channel": TokenType.CHANNEL,
    "pulse": TokenType.PULSE,
    "observe": TokenType.OBSERVE,
    "stream": TokenType.STREAM,
    "defer": TokenType.DEFER,
    "parallel": TokenType.PARALLEL,

    # Metadata
    "mark": TokenType.MARK,

    # Data Science
    "frame": TokenType.FRAME,
    "sift": TokenType.SIFT,
    "morph": TokenType.MORPH,
    "distill": TokenType.DISTILL,
    "train": TokenType.TRAIN,
    "predict": TokenType.PREDICT,

    # Extra
    "using": TokenType.USING,
    "with": TokenType.WITH,
    "extends": TokenType.EXTENDS,
    "as": TokenType.AS,
    "wait": TokenType.WAIT,
    "emit": TokenType.EMIT,
    "forge": TokenType.FORGE,
    "cast": TokenType.CAST,
    "lambda": TokenType.LAMBDA,
    "record": TokenType.RECORD,
    "enum": TokenType.ENUM,
    "when": TokenType.WHEN,
    "inspect": TokenType.INSPECT,
    "assert": TokenType.ASSERT,
    "delete": TokenType.DELETE,
}


# ── Palavras contextuais ─────────────────────────────────────
# Estas NAO sao reservadas: 'get', 'set' e 'final' sao nomes bons demais
# para tirar de quem escreve ('action get()', 'final := ...'). Elas so
# ganham sentido especial dentro do corpo de um blueprint, onde o parser
# as reconhece pelo texto. Fora dali, seguem sendo identificadores.
CONTEXTUAIS_BLUEPRINT = {
    "get":       TokenType.GET,
    "set":       TokenType.SET,
    "private":   TokenType.PRIVATE,
    "protected": TokenType.PROTECTED,
    "operator":  TokenType.OPERATOR,
    "final":     TokenType.FINAL,
    "abstract":  TokenType.ABSTRACT,
    "slots":     TokenType.SLOTS,
}


# ── Palavras do Kiln ─────────────────────────────────────────
# Mesmo raciocinio de CONTEXTUAIS_BLUEPRINT: 'route', 'render' e
# 'server' sao nomes bons demais para tirar de quem escreve. Elas so
# valem como palavra do Kiln dentro de um bloco 'server' — e o proprio
# 'server' so quando abre um bloco ('server nome on ...:'). Em qualquer
# outro lugar seguem sendo identificadores comuns.
CONTEXTUAIS_KILN = {
    "server":     TokenType.SERVER,
    "route":      TokenType.ROUTE,
    "respond":    TokenType.RESPOND,
    "render":     TokenType.RENDER,
    "redirect":   TokenType.REDIRECT,
    "middleware": TokenType.MIDDLEWARE,
    "mount":      TokenType.MOUNT,
    "assets":     TokenType.ASSETS,
    "views":      TokenType.VIEWS,
    "ignite":     TokenType.IGNITE,
}

# ── Palavras do Crucible ─────────────────────────────────────
# Mesmo raciocinio das anteriores. 'expect', 'trial' e 'setup' sao
# nomes que ninguem deveria perder — 'setup' e o proprio nome do
# construtor de blueprint. Elas so valem dentro de um bloco
# 'crucible', e 'crucible' so quando abre um ('crucible "nome":').
CONTEXTUAIS_CRUCIBLE = {
    "crucible": TokenType.CRUCIBLE,
    "trial":    TokenType.TRIAL,
    "expect":   TokenType.EXPECT,
    "fixture":  TokenType.FIXTURE,
    "provide":  TokenType.PROVIDE,
    "setup":    TokenType.SETUP_,
    "teardown": TokenType.TEARDOWN,
    "tagged":   TokenType.TAGGED,
    "pending":  TokenType.PENDING,
    "bench":    TokenType.BENCH,
}

#: Os modificadores que podem seguir o nome de um trial.
MODIFICADORES_TRIAL = ("tagged", "pending", "only", "repeat", "within")


#: Os verbos aceitos depois de 'route'.
VERBOS_KILN = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "ANY")
