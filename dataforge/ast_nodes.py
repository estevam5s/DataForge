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
class Assignment(ASTNode):
    target: Any = None
    value: Any = None
    declared_type: str = ""

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
    param_types: dict = field(default_factory=dict)
    return_type: str = ""

@dataclass
class BlueprintDeclaration(ASTNode):
    """blueprint Name [(params)] [extends Parent] [with Trait]:"""
    name: str = ""
    parents: list = field(default_factory=list)
    body: list = field(default_factory=list)
    traits: list = field(default_factory=list)
    constructor_params: list = field(default_factory=list)

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
    """adopt Module [as Alias]"""
    module: str = ""
    alias: str = ""

@dataclass
class RelayStatement(ASTNode):
    """relay name"""
    names: list = field(default_factory=list)


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
    """mark @Name"""
    name: str = ""
    args: list = field(default_factory=list)


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
