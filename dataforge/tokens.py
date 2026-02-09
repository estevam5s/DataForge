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
    ABSTRACT = auto()        # abstract

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
    INSPECT = auto()         # inspect (debug)
    ASSERT = auto()          # assert
    DELETE = auto()          # delete
    EXISTS = auto()          # exists

    # ── Structural ────────────────────────────────────────
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    COMMENT = auto()


class Token:
    """Represents a single token from the source code."""

    __slots__ = ('type', 'value', 'line', 'column')

    def __init__(self, type: TokenType, value, line: int = 0, column: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

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
    "abstract": TokenType.ABSTRACT,

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
    "claim": TokenType.CLAIM,
    "release": TokenType.RELEASE,

    # Data Science
    "frame": TokenType.FRAME,
    "cluster": TokenType.CLUSTER,
    "vault": TokenType.VAULT,
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
    "range": TokenType.RANGE,
    "wait": TokenType.WAIT,
    "emit": TokenType.EMIT,
    "listen": TokenType.LISTEN,
    "each": TokenType.EACH,
    "forge": TokenType.FORGE,
    "link": TokenType.LINK,
    "unlink": TokenType.UNLINK,
    "cast": TokenType.CAST,
    "inspect": TokenType.INSPECT,
    "assert": TokenType.ASSERT,
    "delete": TokenType.DELETE,
}
