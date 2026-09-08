"""
DataForge AST Node Definitions
Abstract Syntax Tree nodes produced by the parser.
"""

from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════
#  BASE
# ═══════════════════════════════════════════════════════════

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


# ═══════════════════════════════════════════════════════════
#  PROGRAM
# ═══════════════════════════════════════════════════════════

@dataclass
class Program(ASTNode):
    """Root node: list of statements."""
    body: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
#  LITERALS
# ═══════════════════════════════════════════════════════════

@dataclass
class IntegerLiteral(ASTNode):
    value: int = 0

@dataclass
class FloatLiteral(ASTNode):
    value: float = 0.0

@dataclass
class StringLiteral(ASTNode):
    value: str = ""

@dataclass
class BooleanLiteral(ASTNode):
    value: bool = False

@dataclass
class VoidLiteral(ASTNode):
    pass

@dataclass
class ListLiteral(ASTNode):
    elements: list = field(default_factory=list)

@dataclass
class DictLiteral(ASTNode):
    pairs: list = field(default_factory=list)  # list of (key, value) tuples


# ═══════════════════════════════════════════════════════════
#  EXPRESSIONS
# ═══════════════════════════════════════════════════════════

@dataclass
class Identifier(ASTNode):
    name: str = ""

@dataclass
class BinaryOp(ASTNode):
    left: Any = None
    op: str = ""
    right: Any = None

@dataclass
class UnaryOp(ASTNode):
    op: str = ""
    operand: Any = None

@dataclass
class ComparisonOp(ASTNode):
    left: Any = None
    op: str = ""  # is, isnt, bigger, smaller, bigger_eq, smaller_eq
    right: Any = None

@dataclass
class LogicalOp(ASTNode):
    left: Any = None
    op: str = ""  # and, or
    right: Any = None

@dataclass
class NotOp(ASTNode):
    operand: Any = None

@dataclass
class ValorPronto(ASTNode):
    """Embrulha um valor ja calculado para reaproveita-lo numa arvore.

    Serve a quem precisa montar um no de expressao a partir de algo que
    ja foi avaliado — a atribuicao composta, que nao pode avaliar o alvo
    duas vezes.
    """
    value: Any = None


@dataclass
class Assignment(ASTNode):
    """alvo := valor   |   alvo += valor (com compound_op preenchido)

    Numa atribuicao composta, 'value' e so o lado direito — nao o
    BinaryOp inteiro. O interpretador avalia o alvo uma vez, le, aplica e
    escreve. Guardar o BinaryOp aqui faria o alvo ser avaliado duas
    vezes, e 'v[sortear()] += 1' consumiria dois sorteios.
    """
    target: Any = None
    value: Any = None
    declared_type: str = ""
    compound_op: str = ""

@dataclass
class SteadyDeclaration(ASTNode):
    """Immutable constant: steady NAME := value"""
    name: str = ""
    value: Any = None

@dataclass
class MemberAccess(ASTNode):
    """object.member"""
    object: Any = None
    member: str = ""

@dataclass
class IndexAccess(ASTNode):
    """object[index]"""
    object: Any = None
    index: Any = None

@dataclass
class SliceAccess(ASTNode):
    """obj[start:stop:step]"""
    object: Any = None
    start: Any = None
    stop: Any = None
    step: Any = None


@dataclass
class LambdaExpression(ASTNode):
    """lambda a, b: expression"""
    params: list = field(default_factory=list)
    defaults: dict = field(default_factory=dict)
    body: Any = None
    param_types: dict = field(default_factory=dict)


@dataclass
class FunctionCall(ASTNode):
    callee: Any = None
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

@dataclass
class MethodCall(ASTNode):
    object: Any = None
    method: str = ""
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

@dataclass
class SpawnExpression(ASTNode):
    """spawn ClassName(args)"""
    class_name: Any = None
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

@dataclass
class TypeofExpression(ASTNode):
    """typeof expr"""
    operand: Any = None

@dataclass
class CastExpression(ASTNode):
    """cast expr as Type"""
    operand: Any = None
    target_type: str = ""

@dataclass
class PipelineExpression(ASTNode):
    """data >> sift/morph/distill ..."""
    source: Any = None
    operations: list = field(default_factory=list)

@dataclass
class SiftOperation(ASTNode):
    """sift var: condition  OR  sift func_name"""
    param: str = ""
    condition: Any = None
    func_ref: str = ""  # Named function reference

@dataclass
class MorphOperation(ASTNode):
    """morph var: expression  OR  morph func_name"""
    param: str = ""
    expression: Any = None
    func_ref: str = ""  # Named function reference

@dataclass
class DistillOperation(ASTNode):
    """distill acc, var: expression  OR  distill func_name initial"""
    acc_param: str = ""
    val_param: str = ""
    expression: Any = None
    initial: Any = None
    func_ref: str = ""  # Named function reference

@dataclass
class AwaitExpression(ASTNode):
    expression: Any = None

# ═══════════════════════════════════════════════════════════
#  STATEMENTS
# ═══════════════════════════════════════════════════════════

@dataclass
class OutStatement(ASTNode):
    """out expression"""
    expressions: list = field(default_factory=list)

@dataclass
class InExpression(ASTNode):
    """in "prompt" """
    prompt: Any = None

@dataclass
class YieldStatement(ASTNode):
    """yield expression"""
    value: Any = None

@dataclass
class HaltStatement(ASTNode):
    """halt (break)"""
    pass

@dataclass
class SkipStatement(ASTNode):
    """skip (continue)"""
    pass

@dataclass
class TriggerStatement(ASTNode):
    """trigger expression"""
    value: Any = None

@dataclass
class DeleteStatement(ASTNode):
    """delete target"""
    target: Any = None

@dataclass
class AssertStatement(ASTNode):
    """assert expression"""
    condition: Any = None
    message: Any = None

@dataclass
class WaitStatement(ASTNode):
    """wait(ms)"""
    duration: Any = None

@dataclass
class InspectStatement(ASTNode):
    """inspect expression"""
    expression: Any = None


# ═══════════════════════════════════════════════════════════
#  CONTROL FLOW
# ═══════════════════════════════════════════════════════════

@dataclass
class GivenBlock(ASTNode):
    """given ... : / orif ... : / otherwise:"""
    condition: Any = None
    body: list = field(default_factory=list)
    orif_blocks: list = field(default_factory=list)  # list of (condition, body)
    otherwise_body: list = field(default_factory=list)

@dataclass
class MatchBlock(ASTNode):
    """match expression: / point value: / default:"""
    expression: Any = None
    points: list = field(default_factory=list)    # list of (value, body)
    default_body: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
#  LOOPS
# ═══════════════════════════════════════════════════════════

@dataclass
class CycleFromTo(ASTNode):
    """cycle var from start to end [step s]:"""
    var: str = ""
    start: Any = None
    end: Any = None
    step: Any = None
    body: list = field(default_factory=list)

@dataclass
class CycleIn(ASTNode):
    """cycle var in collection:"""
    var: str = ""
    collection: Any = None
    body: list = field(default_factory=list)

@dataclass
class PersistBlock(ASTNode):
    """persist condition:"""
    condition: Any = None
    body: list = field(default_factory=list)

@dataclass
class PerformBlock(ASTNode):
    """perform: ... persist condition"""
    body: list = field(default_factory=list)
    condition: Any = None


# ═══════════════════════════════════════════════════════════
#  FUNCTIONS & CLASSES
# ═══════════════════════════════════════════════════════════

@dataclass
class ActionDeclaration(ASTNode):
    """action name(params):"""
    name: str = ""
    params: list = field(default_factory=list)
    defaults: dict = field(default_factory=dict)
    body: list = field(default_factory=list)
    is_async: bool = False
    decorators: list = field(default_factory=list)
    type_params: list = field(default_factory=list)
    param_types: dict = field(default_factory=dict)
    return_type: str = ""
    is_generator: bool = False
    visibility: str = "public"   # public | private | protected
    is_static: bool = False
    is_abstract: bool = False
    is_final: bool = False

@dataclass
class BlueprintDeclaration(ASTNode):
    """blueprint Name [(params)] [extends Parent] [with Trait]:"""
    name: str = ""
    parents: list = field(default_factory=list)
    body: list = field(default_factory=list)
    traits: list = field(default_factory=list)
    constructor_params: list = field(default_factory=list)
    # (nome, tipo, padrao, visibilidade) — campos declarados no corpo
    fields_decl: list = field(default_factory=list)
    is_abstract: bool = False
    decorators: list = field(default_factory=list)
    # (nome_do_campo, [decoradores]) — decoradores em campos declarados
    field_decorators: dict = field(default_factory=dict)
    # <T>, <K, V> — nomes de tipo validos dentro desta declaracao
    type_params: list = field(default_factory=list)


@dataclass
class PropertyDeclaration(ASTNode):
    """get nome(): ...  |  set nome(valor): ...

    Uma propriedade e lida e escrita como campo, mas roda codigo.
    """
    name: str = ""
    kind: str = "get"            # 'get' ou 'set'
    param: str = ""              # so no set: o nome do valor recebido
    body: list = field(default_factory=list)
    visibility: str = "public"
    return_type: str = ""


@dataclass
class OperatorDeclaration(ASTNode):
    """operator + (outro): ... — sobrecarga de operador."""
    symbol: str = ""             # '+', '-', '*', '/', '%', '**', '==', '<', …
    param: str = ""
    body: list = field(default_factory=list)
    line: int = 0
    column: int = 0

@dataclass
class TraitDeclaration(ASTNode):
    """trait Name:"""
    name: str = ""
    methods: list = field(default_factory=list)

@dataclass
class StaticDeclaration(ASTNode):
    """static name := value"""
    name: str = ""
    value: Any = None


# ═══════════════════════════════════════════════════════════
#  ERROR HANDLING
# ═══════════════════════════════════════════════════════════

@dataclass
class MonitorBlock(ASTNode):
    """monitor: / handle: / ensure:"""
    body: list = field(default_factory=list)
    handle_name: str = ""
    handle_type: str = ""
    handle_body: list = field(default_factory=list)
    ensure_body: list = field(default_factory=list)


@dataclass
class GuardStatement(ASTNode):
    """guard condition else: body"""
    condition: Any = None
    message: Any = None
    else_body: list = field(default_factory=list)


@dataclass
class RetryBlock(ASTNode):
    """retry count: body"""
    count: Any = None
    body: list = field(default_factory=list)
    handle_name: str = "error"
    handle_body: list = field(default_factory=list)


@dataclass
class ValidateStatement(ASTNode):
    """validate value otherwise: else_body"""
    value: Any = None
    predicate: Any = None
    message: Any = None
    else_body: list = field(default_factory=list)


@dataclass
class PropagateStatement(ASTNode):
    """propagate (re-raise current error)"""
    value: Any = None


@dataclass
class DeferStatement(ASTNode):
    """defer: body (runs at end of scope)"""
    body: list = field(default_factory=list)


@dataclass
class ObserveBlock(ASTNode):
    """observe source: body"""
    source: Any = None
    var: str = ""
    body: list = field(default_factory=list)


@dataclass
class StreamExpression(ASTNode):
    """stream data"""
    source: Any = None


@dataclass
class ParallelBlock(ASTNode):
    """parallel: blocks"""
    blocks: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
#  MODULES
# ═══════════════════════════════════════════════════════════

@dataclass
class AdoptStatement(ASTNode):
    """adopt Modulo [as Alias] | adopt {a, b as c} from Modulo"""
    module: str = ""
    alias: str = ""
    selection: list = None      # [(nome, apelido)] quando o import é seletivo

@dataclass
class RelayStatement(ASTNode):
    """relay nome, outro   |   relay from ./modulo

    Com 'origem' preenchida, e re-exportacao: tudo o que aquele modulo
    exporta passa a sair tambem por este. E o que permite montar uma
    fachada — um index.df que reune varios modulos internos numa API so.
    """
    names: list = field(default_factory=list)
    origem: str = ""


# ═══════════════════════════════════════════════════════════
#  ASYNC & CONCURRENCY
# ═══════════════════════════════════════════════════════════

@dataclass
class ThreadBlock(ASTNode):
    """thread: body"""
    body: list = field(default_factory=list)

@dataclass
class ChannelDeclaration(ASTNode):
    """channel name"""
    name: str = ""

@dataclass
class PulseStatement(ASTNode):
    """pulse event_name, data"""
    event: Any = None
    data: Any = None


# ═══════════════════════════════════════════════════════════
#  DECORATORS
# ═══════════════════════════════════════════════════════════

@dataclass
class MarkDecorator(ASTNode):
    """@Nome  ou  @Nome(argumentos)

    Aplica-se a acao, blueprint, record, metodo e campo. O 'mark' antes
    do '@' continua aceito, mas e opcional — '@Nome' sozinho e a forma
    normal, e a que a documentacao ensina.
    """
    name: str = ""
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
#  DATA SCIENCE
# ═══════════════════════════════════════════════════════════

@dataclass
class FrameExpression(ASTNode):
    """frame [[...], [...]]"""
    data: Any = None
    columns: list = field(default_factory=list)

@dataclass
class TrainExpression(ASTNode):
    """train model using data"""
    model: Any = None
    data: Any = None

@dataclass
class PredictExpression(ASTNode):
    """predict model using data"""
    model: Any = None
    data: Any = None


# ═══════════════════════════════════════════════════════════
#  SHADOW
# ═══════════════════════════════════════════════════════════

@dataclass
class ShadowDeclaration(ASTNode):
    """shadow name := value"""
    name: str = ""
    value: Any = None


# ═══════════════════════════════════════════════════════════
#  DataForge 4.0 — EXPRESSÕES
# ═══════════════════════════════════════════════════════════

@dataclass
class InterpolatedString(ASTNode):
    """$"texto {expr} texto" — partes já resolvidas em nós."""
    parts: list = field(default_factory=list)   # [('text', str) | ('expr', ASTNode)]


@dataclass
class TernaryExpression(ASTNode):
    """valor_se_verdadeiro given condicao otherwise valor_se_falso"""
    then_value: Any = None
    condition: Any = None
    else_value: Any = None


@dataclass
class MembershipOp(ASTNode):
    """x in colecao  /  x not in colecao"""
    element: Any = None
    container: Any = None
    negated: bool = False


@dataclass
class CoalesceOp(ASTNode):
    """a ?? b — devolve b quando a for void"""
    left: Any = None
    right: Any = None


@dataclass
class SafeMemberAccess(ASTNode):
    """obj?.membro — void quando obj for void"""
    object: Any = None
    member: str = ""


@dataclass
class SafeMethodCall(ASTNode):
    """obj?.metodo(args)"""
    object: Any = None
    method: str = ""
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


@dataclass
class SpreadElement(ASTNode):
    """...expr dentro de lista, vault ou chamada"""
    value: Any = None


@dataclass
class ComprehensionClause(ASTNode):
    """cycle <var> in <fonte> [given <cond>]"""
    var: str = ""
    targets: list = field(default_factory=list)   # desestruturação no cycle
    source: Any = None
    condition: Any = None


@dataclass
class ListComprehension(ASTNode):
    """[expr cycle x in fonte given cond]"""
    expression: Any = None
    clauses: list = field(default_factory=list)


@dataclass
class VaultComprehension(ASTNode):
    """{k: v cycle x in fonte given cond}"""
    key: Any = None
    value: Any = None
    clauses: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
#  DataForge 4.0 — DECLARAÇÕES
# ═══════════════════════════════════════════════════════════

@dataclass
class RecordDeclaration(ASTNode):
    """record Nome: campo: Tipo [:= padrao]"""
    name: str = ""
    fields: list = field(default_factory=list)     # [(nome, tipo, default|None)]
    methods: dict = field(default_factory=dict)    # nome -> ActionDeclaration
    decorators: list = field(default_factory=list)
    field_decorators: dict = field(default_factory=dict)
    type_params: list = field(default_factory=list)


@dataclass
class EnumDeclaration(ASTNode):
    """enum Nome: MEMBRO [:= valor]"""
    name: str = ""
    members: list = field(default_factory=list)    # [(nome, valor_expr|None)]
    methods: dict = field(default_factory=dict)


@dataclass
class DestructuringAssignment(ASTNode):
    """a, b := expr   |   a, ...resto := expr   |   {nome, idade} := registro"""
    targets: list = field(default_factory=list)    # [(nome, is_rest)]
    value: Any = None
    is_mapping: bool = False                       # forma {a, b} := vault/record
    declared_types: dict = field(default_factory=dict)


@dataclass
class WithExpression(ASTNode):
    """registro with {"campo": valor} — cópia alterada"""
    source: Any = None
    changes: Any = None


# ═══════════════════════════════════════════════════════════
#  DataForge 4.0 — PATTERN MATCHING
# ═══════════════════════════════════════════════════════════

@dataclass
class Pattern(ASTNode):
    """Base dos padrões de 'point'."""
    binding: str = ""        # 'padrao as nome'


@dataclass
class WildcardPattern(Pattern):
    """_ — casa com qualquer coisa"""


@dataclass
class LiteralPattern(Pattern):
    """1, "a", yes, void — casa por igualdade"""
    value: Any = None


@dataclass
class CapturePattern(Pattern):
    """nome — casa com qualquer coisa e liga ao nome"""
    name: str = ""


@dataclass
class TypePattern(Pattern):
    """Integer, Usuario — casa pelo tipo"""
    type_name: str = ""
    sub_patterns: list = field(default_factory=list)   # Usuario(a, b)
    field_patterns: dict = field(default_factory=dict) # Usuario(nome := p)


@dataclass
class SequencePattern(Pattern):
    """[a, b, ...resto]"""
    elements: list = field(default_factory=list)
    rest_index: int = -1
    rest_name: str = ""


@dataclass
class MappingPattern(Pattern):
    """{"chave": padrao, ...}"""
    pairs: list = field(default_factory=list)   # [(chave_expr, padrao)]
    rest_name: str = ""


@dataclass
class ValuePattern(Pattern):
    """Status.Ativo — casa por igualdade com um valor nomeado"""
    expression: Any = None


@dataclass
class OrPattern(Pattern):
    """p1 or p2"""
    options: list = field(default_factory=list)


@dataclass
class MatchCase(ASTNode):
    """point <padrao> [when <guarda>]: corpo"""
    pattern: Any = None
    guard: Any = None
    body: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
#  DataForge 4.0 — GENERATORS
# ═══════════════════════════════════════════════════════════

@dataclass
class EmitStatement(ASTNode):
    """emit valor — produz num 'stream action'; imprime fora dele (legado)."""
    expressions: list = field(default_factory=list)


@dataclass
class _Wrapped(ASTNode):
    """Nó interno: transporta um valor já avaliado para reaproveitar um eval_*."""
    value: Any = None


# ═══════════════════════════════════════════════════════════
#  DataForge 4.2 — KILN (framework web)
# ═══════════════════════════════════════════════════════════

@dataclass
class ServerBlock(ASTNode):
    """server <nome> [on <porta>] [at <host>]: corpo

    Liga <nome> a uma aplicacao Kiln. Nao sobe nada — quem acende o
    forno e o 'ignite'.
    """
    name: str = ""
    port: Any = None
    host: Any = None
    body: list = field(default_factory=list)


@dataclass
class RouteBlock(ASTNode):
    """route <VERBO> "<caminho>": corpo

    Dentro do corpo existem 'req' e os atalhos 'params', 'query',
    'body' e 'headers'.
    """
    method: str = "GET"
    path: Any = None
    body: list = field(default_factory=list)


@dataclass
class RespondStatement(ASTNode):
    """respond [status] [json|html|text|file] <expr>"""
    value: Any = None
    kind: str = ""            # "", "json", "html", "text", "file"
    status: Any = None


@dataclass
class RenderStatement(ASTNode):
    """render "<template>" [with <vault>] [status <n>]"""
    template: Any = None
    data: Any = None
    status: Any = None


@dataclass
class RedirectStatement(ASTNode):
    """redirect "<destino>" [status <n>]"""
    target: Any = None
    status: Any = None


@dataclass
class MiddlewareStatement(ASTNode):
    """middleware <expr> — roda antes de toda rota do server."""
    value: Any = None


@dataclass
class MountStatement(ASTNode):
    """mount <expr> at "<prefixo>" — junta outro server sob um prefixo."""
    value: Any = None
    prefix: Any = None


@dataclass
class AssetsStatement(ASTNode):
    """assets "<prefixo>" from "<pasta>" — serve arquivos do disco."""
    prefix: Any = None
    folder: Any = None


@dataclass
class ViewsStatement(ASTNode):
    """views "<pasta>" — onde ficam os templates."""
    folder: Any = None


@dataclass
class IgniteStatement(ASTNode):
    """ignite <server> [on <porta>] — acende o forno (bloqueia)."""
    target: Any = None
    port: Any = None
    host: Any = None
