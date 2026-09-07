"""
DataForge Interpreter
Tree-walking interpreter that executes AST nodes.
"""

import sys
import threading
import time
import asyncio

from . import ast_nodes as ast
from .environment import Environment
from .builtins import BuiltinFunction, get_builtins, set_stringifier
from .errors import (
    DataForgeError, Frame, RuntimeError_, TypeError_, NameError_, TriggerError,
    HaltSignal, SkipSignal, YieldSignal, IndexError_, ImportError_,
    StackOverflowError_,
)


# ── DataForge Runtime Objects ──────────────────────────────

def _flatten_deep(lst):
    """Recursively flatten nested lists."""
    result = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            result.extend(_flatten_deep(item))
        else:
            result.append(item)
    return result

def _unique_list(lst):
    """Remove duplicates preserving order."""
    seen = set()
    result = []
    for item in lst:
        key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def _reduce_list(lst, func, initial=None):
    """Reduce a list with a function."""
    from functools import reduce as _reduce
    if initial is not None:
        return _reduce(func, lst, initial)
    return _reduce(func, lst)

def _freq_list(lst):
    """Count frequencies in a list."""
    freq = {}
    for item in lst:
        key = str(item)
        freq[key] = freq.get(key, 0) + 1
    return freq

def _dict_set(d, key, val):
    """Set a key in dict and return dict."""
    d[key] = val
    return d

def _dict_delete(d, key):
    """Delete key from dict and return value."""
    return d.pop(key, None)

class DFAction:
    """A user-defined function (action)."""
    _interpreter = None  # Set during Interpreter.__init__

    def __init__(self, name, params, defaults, body, closure, is_async=False,
                 param_types=None, return_type="", is_generator=False):
        self.name = name
        self.params = params
        self.defaults = defaults
        self.body = body
        self.closure = closure
        self.is_async = is_async
        self.param_types = param_types or {}
        self.return_type = return_type
        self.is_generator = is_generator

    def __call__(self, *args, **kwargs):
        """Allow DFAction to be called like a Python function."""
        if DFAction._interpreter is None:
            raise RuntimeError("No interpreter available")
        # Create a fake node for error reporting
        class _FakeNode:
            line = 0
            column = 0
        return DFAction._interpreter._call_action(self, list(args), kwargs, _FakeNode(), None)

    def __repr__(self):
        return f"<action '{self.name}'>"


class DFBlueprint:
    """A user-defined class (blueprint)."""

    def __init__(self, name, parents, methods, statics, env,
                 constructor_params=None, constructor_body=None,
                 properties=None, operators=None, fields_decl=None,
                 visibility=None, is_abstract=False, abstract_methods=None,
                 static_methods=None, final_methods=None, traits=None):
        self.name = name
        self.parents = parents       # list of DFBlueprint
        self.methods = methods       # dict: name → DFAction
        self.statics = statics       # dict: name → value
        self.env = env
        self.constructor_params = constructor_params or []
        self.constructor_body = constructor_body or []
        # ── DataForge 4.1 ──
        self.properties = properties or {}       # nome → {'get': acao, 'set': acao}
        self.operators = operators or {}         # '+' → DFAction
        self.fields_decl = fields_decl or []     # [(nome, tipo, padrao, visib)]
        self.visibility = visibility or {}       # membro → public|private|protected
        self.is_abstract = is_abstract
        self.abstract_methods = abstract_methods or set()
        self.static_methods = static_methods or set()
        self.final_methods = final_methods or set()
        self.traits = traits or []               # nomes dos traits adotados

    def buscar_operador(self, simbolo):
        """O operador sobrecarregado, olhando a cadeia de heranca."""
        if simbolo in self.operators:
            return self.operators[simbolo]
        for pai in self.parents:
            achado = pai.buscar_operador(simbolo)
            if achado is not None:
                return achado
        return None

    def buscar_propriedade(self, nome):
        """A propriedade, olhando a cadeia de heranca."""
        if nome in self.properties:
            return self.properties[nome]
        for pai in self.parents:
            achado = pai.buscar_propriedade(nome)
            if achado is not None:
                return achado
        return None

    def visibilidade_de(self, nome):
        if nome in self.visibility:
            return self.visibility[nome]
        for pai in self.parents:
            v = pai.visibilidade_de(nome)
            if v != "public":
                # private do pai nao vaza para o filho; protected sim
                return "protected" if v == "protected" else "private"
        return "public"

    def linhagem(self):
        """Este blueprint e todos os ancestrais, do mais proximo ao mais longe."""
        vistos, ordem, fila = {self.name}, [self], list(self.parents)
        while fila:
            bp = fila.pop(0)
            if bp.name in vistos:
                continue
            vistos.add(bp.name)
            ordem.append(bp)
            fila.extend(bp.parents)
        return ordem

    def pendencias_abstratas(self):
        """Metodos abstratos herdados que ninguem implementou ainda."""
        faltando = {}
        for bp in reversed(self.linhagem()):
            for nome in bp.abstract_methods:
                faltando[nome] = bp.name
            for nome, acao in bp.methods.items():
                if nome in faltando and not getattr(acao, "is_abstract", False):
                    faltando.pop(nome)
        return faltando

    def __repr__(self):
        return f"<blueprint '{self.name}'>"


class DFInstance:
    """An instance of a blueprint (spawn)."""

    def __init__(self, blueprint: DFBlueprint):
        self.blueprint = blueprint
        self.fields: dict = {}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        # Look in blueprint methods
        if name in self.blueprint.methods:
            return self.blueprint.methods[name]
        # Look in statics
        if name in self.blueprint.statics:
            return self.blueprint.statics[name]
        # Look in parent blueprints (MRO: depth-first)
        for parent in self.blueprint.parents:
            try:
                return self._resolve_from_blueprint(parent, name)
            except NameError_:
                continue
        raise NameError_(f"'{self.blueprint.name}' has no member '{name}'")

    def _resolve_from_blueprint(self, bp, name):
        """Resolve a name from blueprint chain (supports deep inheritance)."""
        if name in bp.methods:
            return bp.methods[name]
        if name in bp.statics:
            return bp.statics[name]
        for parent in bp.parents:
            try:
                return self._resolve_from_blueprint(parent, name)
            except NameError_:
                continue
        raise NameError_(f"Not found: '{name}'")

    def set(self, name, value):
        self.fields[name] = value

    def isinstance_of(self, blueprint):
        """Check if this instance is of given blueprint or inherits from it."""
        if self.blueprint is blueprint or self.blueprint.name == blueprint.name:
            return True
        return self._check_parents(self.blueprint, blueprint)

    def _check_parents(self, bp, target):
        for parent in bp.parents:
            if parent is target or parent.name == target.name:
                return True
            if self._check_parents(parent, target):
                return True
        return False

    def get_mro(self):
        """Get Method Resolution Order (C3 linearization simplified)."""
        mro = [self.blueprint]
        visited = {self.blueprint.name}
        queue = list(self.blueprint.parents)
        while queue:
            bp = queue.pop(0)
            if bp.name not in visited:
                visited.add(bp.name)
                mro.append(bp)
                queue.extend(bp.parents)
        return mro

    def has_method(self, name):
        """Check if instance has a given method."""
        try:
            val = self.get(name)
            return isinstance(val, (DFAction, BuiltinFunction)) or callable(val)
        except NameError_:
            return False

    def __repr__(self):
        return f"<{self.blueprint.name} instance>"


class DFError:
    """A runtime error captured by 'monitor / handle'.

    Behaves like the error message string (so older code that concatenates or
    compares it keeps working) while also exposing '.type', '.message' and
    '.line'.
    """

    def __init__(self, kind: str, message: str, original=None):
        self.type = kind
        self.message = message
        self.original = original
        self.line = getattr(original, 'line', 0)
        self.column = getattr(original, 'column', 0)

    def __str__(self):
        return self.message

    def __eq__(self, other):
        if isinstance(other, str):
            return self.message == other
        if isinstance(other, DFError):
            return self.type == other.type and self.message == other.message
        return NotImplemented

    def __hash__(self):
        return hash((self.type, self.message))

    def __bool__(self):
        return True

    def __repr__(self):
        return f"<{self.type}: {self.message}>"


class DFRecord:
    """Um tipo record: dados imutáveis, com igualdade estrutural."""

    def __init__(self, name, fields, methods, env):
        self.name = name
        self.fields = fields        # [(nome, tipo, default_node|None)]
        self.field_names = [f[0] for f in fields]
        self.field_types = {f[0]: f[1] for f in fields}
        self.methods = methods      # nome -> DFAction
        self.env = env

    def __repr__(self):
        return f"<record '{self.name}'>"


class DFRecordInstance:
    """Uma instância de record. Imutável: use 'with' para gerar uma cópia."""

    __slots__ = ('record', 'values')

    def __init__(self, record: DFRecord, values: dict):
        self.record = record
        self.values = values

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if name in self.record.methods:
            return self.record.methods[name]
        raise NameError_(
            f"Record '{self.record.name}' has no field or method '{name}'. "
            f"It has: {', '.join(self.record.field_names)}")

    def replace(self, changes: dict):
        """Cópia com campos trocados — a base do operador 'with'."""
        desconhecidos = [k for k in changes if k not in self.record.field_names]
        if desconhecidos:
            raise NameError_(
                f"Record '{self.record.name}' has no field(s): "
                f"{', '.join(desconhecidos)}")
        novos = dict(self.values)
        novos.update(changes)
        return DFRecordInstance(self.record, novos)

    def __eq__(self, other):
        if isinstance(other, DFRecordInstance):
            return (self.record.name == other.record.name
                    and self.values == other.values)
        return NotImplemented

    def __hash__(self):
        return hash((self.record.name, tuple(sorted(
            (k, v) for k, v in self.values.items() if isinstance(v, (int, float, str, bool, type(None)))))))

    def __repr__(self):
        campos = ', '.join(f"{k}: {v!r}" for k, v in self.values.items())
        return f"{self.record.name}({campos})"


class DFEnumMember:
    """Um membro de enum. Compara por identidade dentro do enum."""

    __slots__ = ('enum_name', 'name', 'value', 'index')

    def __init__(self, enum_name, name, value, index):
        self.enum_name = enum_name
        self.name = name
        self.value = value
        self.index = index

    def __eq__(self, other):
        if isinstance(other, DFEnumMember):
            return self.enum_name == other.enum_name and self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash((self.enum_name, self.name))

    def __repr__(self):
        return f"{self.enum_name}.{self.name}"


class DFEnum:
    """Um tipo enum e seus membros."""

    def __init__(self, name, members, methods, env):
        self.name = name
        self.members = members      # nome -> DFEnumMember (ordenado)
        self.methods = methods
        self.env = env

    def get(self, name):
        if name in self.members:
            return self.members[name]
        if name in self.methods:
            return self.methods[name]
        raise NameError_(
            f"Enum '{self.name}' has no member '{name}'. "
            f"Members: {', '.join(self.members)}")

    def __repr__(self):
        return f"<enum '{self.name}'>"


class DFStream:
    """Uma sequência preguiçosa produzida por um 'stream action'."""

    def __init__(self, name, produce):
        self.name = name
        self._produce = produce     # callable -> generator Python
        self._iter = None

    def __iter__(self):
        return self._produce()

    def take(self, n):
        saida = []
        for i, item in enumerate(self):
            if i >= n:
                break
            saida.append(item)
        return saida

    def to_cluster(self):
        return list(self)

    def next(self):
        if self._iter is None:
            self._iter = iter(self)
        try:
            return next(self._iter)
        except StopIteration:
            return None

    def reset(self):
        self._iter = None
        return self

    def __repr__(self):
        return f"<stream '{self.name}'>"


class BoundRecordMethod:
    """Um método de record já ligado à sua instância."""

    __slots__ = ('interpreter', 'instance', 'action')

    def __init__(self, interpreter, instance, action):
        self.interpreter = interpreter
        self.instance = instance
        self.action = action

    def __call__(self, *args, **kwargs):
        no = type('_N', (), {'line': 0, 'column': 0})()
        return self.interpreter._call_action(
            self.action, list(args), kwargs, no, None, instance=self.instance)

    def __repr__(self):
        return f"<method '{self.action.name}' of {self.instance.record.name}>"


class DFChannel:
    """Thread-safe communication channel."""

    def __init__(self, name):
        self.name = name
        self._queue = []
        self._lock = threading.Lock()

    def send(self, value):
        with self._lock:
            self._queue.append(value)

    def receive(self):
        with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None

    def __repr__(self):
        return f"<channel '{self.name}'>"


class _RootProxy:
    """Proxy for 'root' (super) calls - resolves methods from parent blueprints."""
    def __init__(self, instance, parent_blueprint, interpreter):
        self.instance = instance
        self.parent = parent_blueprint
        self.interpreter = interpreter

    def get(self, name):
        if name in self.parent.methods:
            return self.parent.methods[name]
        if name in self.parent.statics:
            return self.parent.statics[name]
        for p in self.parent.parents:
            if name in p.methods:
                return p.methods[name]
            if name in p.statics:
                return p.statics[name]
        raise NameError_(f"Parent has no member '{name}'")


# ── Interpreter ────────────────────────────────────────────

class Interpreter:
    """Tree-walking interpreter for DataForge AST."""

    def __init__(self):
        self.global_env = Environment(name="<global>")
        self.modules = {}
        self.events = {}  # event name → list of callbacks
        self._depth = 0   # current action-call depth
        self._call_stack = []  # quadros para o stack trace
        self._loading = []     # módulos em carga, para detectar ciclos
        self.filename = "<stdin>"
        # A DataForge frame costs several Python frames; give the interpreter
        # room so its own depth guard reports the error instead of CPython.
        if sys.getrecursionlimit() < 20000:
            sys.setrecursionlimit(20000)

        # Set interpreter reference for DFAction __call__
        DFAction._interpreter = self

        # str() and 'out' must format values identically.
        set_stringifier(self._to_str)

        # Load builtins
        for name, value in get_builtins().items():
            self.global_env.set_local(name, value)

    def run(self, program: ast.Program, filename: str = ""):
        """Execute a full program."""
        if filename:
            self.filename = filename
        try:
            return self.exec_block(program.body, self.global_env)
        except DataForgeError as erro:
            self._attach_stack(erro)
            raise

    def exec_block(self, statements: list, env: Environment):
        """Execute a block of statements."""
        result = None
        for stmt in statements:
            result = self.execute(stmt, env)
        return result

    def execute(self, node, env: Environment):
        """Execute a single AST node."""
        if node is None:
            return None

        method_name = f"exec_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method:
            return method(node, env)

        # If it's an expression node, evaluate it
        return self.evaluate(node, env)

    def evaluate(self, node, env: Environment):
        """Evaluate an expression node and return its value."""
        if node is None:
            return None

        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method:
            return method(node, env)

        # Fallback: try execute
        method_name2 = f"exec_{type(node).__name__}"
        method2 = getattr(self, method_name2, None)
        if method2:
            return method2(node, env)

        raise RuntimeError_(f"Cannot evaluate node type: {type(node).__name__}", node.line, node.column)

    # ═══════════════════════════════════════════════════════
    #  LITERAL EVALUATION
    # ═══════════════════════════════════════════════════════

    def eval_IntegerLiteral(self, node: ast.IntegerLiteral, env):
        return node.value

    def eval_FloatLiteral(self, node: ast.FloatLiteral, env):
        return node.value

    def eval_StringLiteral(self, node: ast.StringLiteral, env):
        return node.value

    def eval_BooleanLiteral(self, node: ast.BooleanLiteral, env):
        return node.value

    def eval_VoidLiteral(self, node: ast.VoidLiteral, env):
        return None

    def eval_ListLiteral(self, node: ast.ListLiteral, env):
        if any(isinstance(e, ast.SpreadElement) for e in node.elements):
            return self._expand_elements(node.elements, env)
        return [self.evaluate(elem, env) for elem in node.elements]

    def eval_DictLiteral(self, node: ast.DictLiteral, env):
        result = {}
        for key_node, val_node in node.pairs:
            if isinstance(key_node, ast.SpreadElement):
                base = self.evaluate(key_node.value, env)
                if isinstance(base, DFRecordInstance):
                    base = dict(base.values)
                elif isinstance(base, DFInstance):
                    base = dict(base.fields)
                if not isinstance(base, dict):
                    raise TypeError_(
                        f"Cannot spread {self._type_of(base)} into a vault: "
                        f"'...' needs a Vault, a record or an instance",
                        key_node.line, key_node.column)
                result.update(base)
                continue
            result[self.evaluate(key_node, env)] = self.evaluate(val_node, env)
        return result

    # ═══════════════════════════════════════════════════════
    #  EXPRESSION EVALUATION
    # ═══════════════════════════════════════════════════════

    def eval_Identifier(self, node: ast.Identifier, env):
        # Special: 'root' inside a method = proxy to parent blueprint methods
        if node.name == 'root':
            # Find 'self' in scope to get the instance's parent
            if env.has('self'):
                instance = env.get('self')
                if isinstance(instance, DFInstance) and instance.blueprint.parents:
                    # Return a proxy dict that resolves parent methods
                    parent = instance.blueprint.parents[0]
                    return _RootProxy(instance, parent, self)
        return env.get(node.name)

    def eval_BinaryOp(self, node: ast.BinaryOp, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.op

        # ── Sobrecarga de operador ─────────────────────────
        # 'operator + (outro):' declarado no blueprint tem prioridade.
        for lado, outro, invertido in ((left, right, False), (right, left, True)):
            if not isinstance(lado, DFInstance):
                continue
            sobrecarga = lado.blueprint.buscar_operador(op)
            if sobrecarga is None:
                continue
            # a + b tenta 'a'; se so 'b' define, ainda funciona para
            # operadores comutativos, mas nunca para os que nao sao
            if invertido and op in ('-', '/', '%', '**', '<', '>', '<=', '>='):
                continue
            return self._call_action(sobrecarga, [outro], {}, node, env,
                                     instance=lado)

        # Forma antiga, mantida: metodos 'add', 'sub'…
        op_methods = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div',
                      '%': 'mod', '**': 'pow', '//': 'floordiv'}
        if isinstance(left, DFInstance) and op in op_methods:
            method_name = op_methods[op]
            if left.has_method(method_name):
                method = left.get(method_name)
                return self._call_action(method, [right], {}, node, env, instance=left)

        try:
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return self._to_str(left) + self._to_str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise RuntimeError_("Division by zero", node.line, node.column)
                return left / right
            elif op == '%':
                return left % right
            elif op == '**':
                return left ** right
            elif op == '//':
                if right == 0:
                    raise RuntimeError_("Division by zero", node.line, node.column)
                return left // right
        except TypeError as e:
            raise TypeError_(str(e), node.line, node.column)

        raise RuntimeError_(f"Unknown binary operator: {op!r}", node.line, node.column)

    def eval_UnaryOp(self, node: ast.UnaryOp, env):
        operand = self.evaluate(node.operand, env)
        if node.op == '-':
            return -operand
        if node.op == '+':
            return +operand
        raise RuntimeError_(f"Unknown unary operator: {node.op}", node.line, node.column)

    #: 'is' e '==' sao o mesmo operador para efeito de sobrecarga.
    _SIMBOLO_COMPARACAO = {
        'is': '==', '==': '==', 'isnt': '!=', '!=': '!=',
        'bigger': '>', '>': '>', 'smaller': '<', '<': '<',
        'bigger_eq': '>=', '>=': '>=', 'smaller_eq': '<=', '<=': '<=',
    }

    def eval_ComparisonOp(self, node: ast.ComparisonOp, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.op

        # ── Sobrecarga de comparacao ───────────────────────
        simbolo = self._SIMBOLO_COMPARACAO.get(op)
        if simbolo is not None:
            for lado, outro, invertido in ((left, right, False),
                                           (right, left, True)):
                if not isinstance(lado, DFInstance):
                    continue
                sobrecarga = lado.blueprint.buscar_operador(simbolo)
                if sobrecarga is None:
                    # '!=' pode sair de '==' negado; '>' de '<' invertido
                    if simbolo == '!=':
                        eq = lado.blueprint.buscar_operador('==')
                        if eq is not None:
                            return not bool(self._call_action(
                                eq, [outro], {}, node, env, instance=lado))
                    continue
                if invertido and simbolo in ('<', '>', '<=', '>='):
                    continue
                return self._call_action(sobrecarga, [outro], {}, node, env,
                                         instance=lado)

        if op == 'is':
            return left == right
        elif op == 'isnt':
            return left != right
        elif op == 'bigger':
            return left > right
        elif op == 'smaller':
            return left < right
        elif op == 'bigger_eq':
            return left >= right
        elif op == 'smaller_eq':
            return left <= right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        raise RuntimeError_(f"Unknown comparison: {op}", node.line, node.column)

    def eval_LogicalOp(self, node: ast.LogicalOp, env):
        left = self.evaluate(node.left, env)
        if node.op == 'and':
            if not left:
                return left
            return self.evaluate(node.right, env)
        elif node.op == 'or':
            if left:
                return left
            return self.evaluate(node.right, env)

    def eval_NotOp(self, node: ast.NotOp, env):
        return not self.evaluate(node.operand, env)

    def eval_MemberAccess(self, node: ast.MemberAccess, env):
        obj = self.evaluate(node.object, env)

        # Handle root (super) proxy
        if isinstance(obj, _RootProxy):
            return obj.get(node.member)

        if isinstance(obj, DFRecordInstance):
            if node.member == 'fields':
                return dict(obj.values)
            if node.member == 'record_name':
                return obj.record.name
            valor = obj.get(node.member)
            if isinstance(valor, DFAction):
                return BoundRecordMethod(self, obj, valor)
            return valor

        if isinstance(obj, DFRecord):
            if node.member == 'fields':
                return list(obj.field_names)
            if node.member in obj.methods:
                return obj.methods[node.member]
            raise NameError_(
                f"Record '{obj.name}' has no static member '{node.member}'",
                node.line, node.column)

        if isinstance(obj, DFEnumMember):
            if node.member == 'name':
                return obj.name
            if node.member == 'value':
                return obj.value
            if node.member == 'index':
                return obj.index
            if node.member == 'enum_name':
                return obj.enum_name
            raise NameError_(
                f"Enum member '{obj}' has no member '{node.member}'. "
                f"Use .name, .value or .index",
                node.line, node.column)

        if isinstance(obj, DFEnum):
            enum_methods = {
                'names': lambda: list(obj.members.keys()),
                'values': lambda: [m.value for m in obj.members.values()],
                'members': lambda: list(obj.members.values()),
                'count': lambda: len(obj.members),
                'has': lambda n: n in obj.members,
                'from_value': lambda v: next(
                    (m for m in obj.members.values() if m.value == v), None),
                'from_name': lambda n: obj.members.get(n),
            }
            if node.member in obj.members:
                return obj.members[node.member]
            if node.member in enum_methods:
                return BuiltinFunction(node.member, enum_methods[node.member])
            if node.member in obj.methods:
                return obj.methods[node.member]
            raise NameError_(
                f"Enum '{obj.name}' has no member '{node.member}'. "
                f"Members: {', '.join(obj.members)}",
                node.line, node.column)

        if isinstance(obj, DFStream):
            stream_methods = {
                'take': lambda n: obj.take(n),
                'to_cluster': lambda: obj.to_cluster(),
                'next': lambda: obj.next(),
                'reset': lambda: obj.reset(),
                'count': lambda: sum(1 for _ in obj),
                'map': lambda f: [f(x) for x in obj],
                'filter': lambda f: [x for x in obj if f(x)],
                'first': lambda: next(iter(obj), None),
            }
            if node.member in stream_methods:
                return BuiltinFunction(node.member, stream_methods[node.member])
            raise NameError_(
                f"Stream has no member '{node.member}'. Use take, to_cluster, "
                f"next, reset, count, map, filter or first",
                node.line, node.column)

        if isinstance(obj, DFInstance):
            # Instance built-in methods
            if node.member == 'blueprint_name':
                return obj.blueprint.name
            if node.member == 'fields':
                return dict(obj.fields)
            if node.member == 'methods':
                return list(obj.blueprint.methods.keys())

            # Propriedade: 'p.area' roda o corpo do 'get area()'
            prop = obj.blueprint.buscar_propriedade(node.member)
            if prop is not None and 'get' in prop:
                self._conferir_acesso(obj.blueprint, node.member, env, node)
                return self._call(prop['get'], [], {}, node, env, instancia=obj)
            if prop is not None:
                raise TypeError_(
                    f"'{obj.blueprint.name}.{node.member}' is write-only: it "
                    f"has a 'set' but no 'get'.",
                    node.line, node.column)

            self._conferir_acesso(obj.blueprint, node.member, env, node)
            return obj.get(node.member)

        elif isinstance(obj, DFBlueprint):
            if node.member in obj.statics:
                return obj.statics[node.member]
            if node.member in obj.methods:
                if node.member in obj.static_methods:
                    return obj.methods[node.member]
                raise TypeError_(
                    f"'{obj.name}.{node.member}' is an instance method: it "
                    f"needs an object.\n"
                    f"    Spawn one first:  obj := spawn {obj.name}(…)  "
                    f"then obj.{node.member}(…)\n"
                    f"    Or declare it as 'static action {node.member}(…)'.",
                    node.line, node.column)
            self._erro_membro_blueprint(obj, node)
        elif isinstance(obj, dict):
            # Module namespace dicts: check key access first
            if "__name__" in obj and node.member in obj:
                return obj[node.member]
            # Check dict methods
            dict_methods = {
                'keys': lambda: list(obj.keys()),
                'values': lambda: list(obj.values()),
                'items': lambda: [list(p) for p in obj.items()],
                'has': lambda key: key in obj,
                'contains': lambda key: key in obj,
                'get': lambda key, default=None: obj.get(key, default),
                'set': lambda key, val: _dict_set(obj, key, val),
                'delete': lambda key: _dict_delete(obj, key),
                'length': lambda: len(obj),
                'merge': lambda other: {**obj, **other},
                'update': lambda other: (obj.update(other), obj)[-1],
                'clear': lambda: (obj.clear(), obj)[-1],
                'copy': lambda: dict(obj),
                'pick': lambda *ks: {k: obj[k] for k in ks if k in obj},
                'omit': lambda *ks: {k: v for k, v in obj.items() if k not in ks},
                'invert': lambda: {v: k for k, v in obj.items()},
                'map_values': lambda f: {k: f(v) for k, v in obj.items()},
                'filter_keys': lambda f: {k: v for k, v in obj.items() if f(k)},
                'to_pairs': lambda: [list(p) for p in obj.items()],
            }
            if node.member in dict_methods:
                return BuiltinFunction(node.member, dict_methods[node.member])
            if node.member == 'length':
                return len(obj)
            # Fall back to key access
            if node.member in obj:
                return obj[node.member]
            raise NameError_(f"Vault has no key '{node.member}'")
        elif isinstance(obj, str):
            # String methods - comprehensive
            string_methods = {
                'length': lambda: len(obj),
                'upper': lambda: obj.upper(),
                'lower': lambda: obj.lower(),
                'strip': lambda chars=None: obj.strip(chars),
                'lstrip': lambda chars=None: obj.lstrip(chars),
                'rstrip': lambda chars=None: obj.rstrip(chars),
                'title': lambda: obj.title(),
                'capitalize': lambda: obj.capitalize(),
                'swapcase': lambda: obj.swapcase(),
                'center': lambda w, f=" ": obj.center(w, f),
                'ljust': lambda w, f=" ": obj.ljust(w, f),
                'rjust': lambda w, f=" ": obj.rjust(w, f),
                'zfill': lambda w: obj.zfill(w),
                'split': lambda sep=" ": obj.split(sep),
                'replace': lambda old, new, count=-1: obj.replace(old, new) if count == -1 else obj.replace(old, new, count),
                'startswith': lambda prefix: obj.startswith(prefix),
                'endswith': lambda suffix: obj.endswith(suffix),
                'find': lambda sub, start=0: obj.find(sub, start),
                'rfind': lambda sub, start=0: obj.rfind(sub, start),
                'index_of': lambda sub, start=0: obj.find(sub, start),
                'last_index_of': lambda sub: obj.rfind(sub),
                'char_at': lambda i: obj[i] if 0 <= i < len(obj) else "",
                'substring': lambda start, end=None: obj[start:end],
                'slice': lambda start, end=None: obj[start:end],
                'contains': lambda sub: sub in obj,
                'includes': lambda sub: sub in obj,
                'isalpha': lambda: obj.isalpha(),
                'isdigit': lambda: obj.isdigit(),
                'isalnum': lambda: obj.isalnum(),
                'isspace': lambda: obj.isspace(),
                'isupper': lambda: obj.isupper(),
                'islower': lambda: obj.islower(),
                'istitle': lambda: obj.istitle(),
                'isnumeric': lambda: obj.isnumeric(),
                'repeat': lambda n: obj * n,
                'reverse': lambda: obj[::-1],
                'trim': lambda: obj.strip(),
                'pad_start': lambda l, f=" ": obj.rjust(l, f),
                'pad_end': lambda l, f=" ": obj.ljust(l, f),
                'concat': lambda *args: obj + "".join(str(a) for a in args),
                'count': lambda sub: obj.count(sub),
                'expandtabs': lambda ts=8: obj.expandtabs(ts),
                'partition': lambda sep: list(obj.partition(sep)),
                'rpartition': lambda sep: list(obj.rpartition(sep)),
                'splitlines': lambda keepends=False: obj.splitlines(keepends),
                'removeprefix': lambda pfx: obj[len(pfx):] if obj.startswith(pfx) else obj,
                'removesuffix': lambda sfx: obj[:-len(sfx)] if sfx and obj.endswith(sfx) else obj,
                'words': lambda: obj.split(),
                'lines': lambda: obj.splitlines(),
                'encode': lambda enc="utf-8": list(obj.encode(enc)),
                'format': lambda *a, **kw: obj.format(*a, **kw),
                'join': lambda it: obj.join(str(x) for x in it),
            }
            if node.member in string_methods:
                return BuiltinFunction(node.member, string_methods[node.member])
            if node.member == 'length':
                return len(obj)
        elif isinstance(obj, list):
            list_methods = {
                'length': lambda: len(obj),
                'append': lambda item: obj.append(item),
                'push': lambda item: obj.append(item),
                'pop': lambda idx=-1: obj.pop(idx),
                'insert': lambda idx, item: obj.insert(idx, item),
                'remove': lambda item: obj.remove(item),
                'sort': lambda: (obj.sort(), obj)[-1],
                'reverse': lambda: (obj.reverse(), obj)[-1],
                'contains': lambda item: item in obj,
                'includes': lambda item: item in obj,
                'index': lambda item: obj.index(item),
                'index_of': lambda item: obj.index(item),
                'count': lambda item: obj.count(item),
                'first': lambda: obj[0] if obj else None,
                'last': lambda: obj[-1] if obj else None,
                'take': lambda n: obj[:n],
                'drop': lambda n: obj[n:],
                'slice': lambda s=None, e=None: obj[s:e],
                'flatten': lambda: _flatten_deep(obj),
                'unique': lambda: _unique_list(obj),
                'chunk': lambda s: [obj[i:i+s] for i in range(0, len(obj), s)],
                'rotate': lambda n: obj[n%len(obj):] + obj[:n%len(obj)] if obj else [],
                'reversed': lambda: list(reversed(obj)),
                'join': lambda sep=", ": sep.join(str(x) for x in obj),
                'map': lambda f: [f(x) for x in obj],
                'filter': lambda f: [x for x in obj if f(x)],
                'reduce': lambda f, init=None: _reduce_list(obj, f, init),
                'every': lambda f: all(f(x) for x in obj),
                'some': lambda f: any(f(x) for x in obj),
                'find': lambda f: next((x for x in obj if f(x)), None),
                'sum': lambda: sum(obj),
                'min': lambda: min(obj),
                'max': lambda: max(obj),
                'mean': lambda: sum(obj) / len(obj) if obj else 0,
                'clear': lambda: (obj.clear(), obj)[-1],
                'copy': lambda: list(obj),
                'extend': lambda other: (obj.extend(other), obj)[-1],
                'frequencies': lambda: _freq_list(obj),
            }
            if node.member in list_methods:
                return BuiltinFunction(node.member, list_methods[node.member])
            if node.member == 'length':
                return len(obj)
        elif hasattr(obj, node.member):
            return getattr(obj, node.member)

        raise NameError_(f"Cannot access member '{node.member}' on {type(obj).__name__}", node.line, node.column)

    def eval_IndexAccess(self, node: ast.IndexAccess, env):
        obj = self.evaluate(node.object, env)
        index = self.evaluate(node.index, env)
        try:
            return obj[index]
        except (IndexError, KeyError) as e:
            raise IndexError_(str(e), node.line, node.column)
        except TypeError:
            raise TypeError_(
                f"Cannot index a value of type {self._type_of(obj)}",
                node.line, node.column)

    def eval_SliceAccess(self, node: ast.SliceAccess, env):
        obj = self.evaluate(node.object, env)
        start = self.evaluate(node.start, env) if node.start is not None else None
        stop = self.evaluate(node.stop, env) if node.stop is not None else None
        step = self.evaluate(node.step, env) if node.step is not None else None
        try:
            return obj[start:stop:step]
        except TypeError as e:
            raise TypeError_(f"Cannot slice {type(obj).__name__}: {e}", node.line, node.column)

    def eval_LambdaExpression(self, node: ast.LambdaExpression, env):
        """A lambda is an anonymous action closing over the current scope."""
        return DFAction(
            name="<lambda>",
            params=list(node.params),
            defaults=dict(node.defaults),
            body=[ast.YieldStatement(value=node.body, line=node.line, column=node.column)],
            closure=env,
            param_types=dict(node.param_types),
        )

    def eval_FunctionCall(self, node: ast.FunctionCall, env):
        callee = self.evaluate(node.callee, env)
        args = self._eval_args(node.args, env)
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}
        return self._call(callee, args, kwargs, node, env)

    def eval_MethodCall(self, node: ast.MethodCall, env):
        obj = self.evaluate(node.object, env)
        args = self._eval_args(node.args, env)
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}

        # Handle root (super) proxy calls
        if isinstance(obj, _RootProxy):
            method = obj.get(node.method)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj.instance)
            if callable(method):
                return method(*args, **kwargs)

        if isinstance(obj, DFRecordInstance):
            metodo = obj.get(node.method)
            if isinstance(metodo, DFAction):
                return self._call_action(metodo, args, kwargs, node, env, instance=obj)
            if callable(metodo):
                return metodo(*args, **kwargs)

        if isinstance(obj, DFInstance):
            method = obj.get(node.method)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj)
            if callable(method):
                return method(*args, **kwargs)
        elif isinstance(obj, DFBlueprint):
            if node.method in obj.methods:
                method = obj.methods[node.method]
                if node.method not in obj.static_methods:
                    # Sem instancia, 'self' fica solto e o erro sai la dentro,
                    # longe da causa. Melhor recusar aqui, dizendo o que fazer.
                    raise TypeError_(
                        f"'{obj.name}.{node.method}()' is an instance method "
                        f"and needs an object.\n"
                        f"    Spawn one first:\n"
                        f"        obj := spawn {obj.name}(…)\n"
                        f"        obj.{node.method}(…)\n"
                        f"    Or declare it as "
                        f"'static action {node.method}(…)' if it does not "
                        f"use 'self'.",
                        node.line, node.column)
                return self._call_action(method, args, kwargs, node, env)
            if node.method in obj.statics:
                val = obj.statics[node.method]
                if callable(val):
                    return val(*args, **kwargs)
                return val
        elif isinstance(obj, (BuiltinFunction,)):
            return obj(*args, **kwargs)
        elif hasattr(obj, '__call__'):
            return obj(*args, **kwargs)

        # Try getting a builtin method
        member = self.eval_MemberAccess(
            ast.MemberAccess(object=node.object, member=node.method, line=node.line, column=node.column),
            env
        )
        if callable(member):
            return member(*args, **kwargs)

        raise RuntimeError_(f"Cannot call method '{node.method}' on {type(obj).__name__}", node.line, node.column)

    def eval_SpawnExpression(self, node: ast.SpawnExpression, env):
        blueprint = self.evaluate(node.class_name, env)
        if not isinstance(blueprint, DFBlueprint):
            nome = getattr(node.class_name, 'name', None) or self._to_str(blueprint)
            raise TypeError_(
                f"'{nome}' is not a blueprint, so it cannot be spawned.\n"
                f"    'spawn' builds an object from a blueprint; "
                f"'{nome}' is {self._nome_do_tipo(blueprint)}.",
                node.line, node.column)

        if blueprint.is_abstract:
            faltando = blueprint.pendencias_abstratas()
            detalhe = ""
            if faltando:
                itens = ", ".join(f"{n}()" for n in sorted(faltando))
                detalhe = f"\n    It still misses: {itens}"
            raise TypeError_(
                f"'{blueprint.name}' is an abstract blueprint and cannot be "
                f"spawned directly.{detalhe}\n"
                f"    Spawn a blueprint that extends it instead.",
                node.line, node.column)

        instance = DFInstance(blueprint)

        # Campos declarados no corpo comecam com o padrao (ou void)
        for nome_campo, _tipo, padrao, _visib in blueprint.fields_decl:
            instance.fields[nome_campo] = padrao
        args = self._eval_args(node.args, env)
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}

        # If blueprint has constructor_params, assign them to instance fields
        if blueprint.constructor_params:
            for i, param in enumerate(blueprint.constructor_params):
                if i < len(args):
                    instance.fields[param] = args[i]
                else:
                    instance.fields[param] = None

            # A 'setup' method still runs, so a blueprint may declare params and
            # still initialise derived fields explicitly.
            if 'setup' in blueprint.methods:
                self._call_action(blueprint.methods['setup'], args, kwargs, node, env,
                                  instance=instance)

            # Execute the constructor body with 'this'/'self' bound to instance
            if blueprint.constructor_body:
                ctor_env = blueprint.env.child(f"<{blueprint.name}.__init__>")
                ctor_env.set_local("this", instance)
                ctor_env.set_local("self", instance)
                # Also make params available as local variables
                for i, param in enumerate(blueprint.constructor_params):
                    if i < len(args):
                        ctor_env.set_local(param, args[i])
                    else:
                        ctor_env.set_local(param, None)
                try:
                    self.exec_block(blueprint.constructor_body, ctor_env)
                except YieldSignal:
                    pass  # constructors shouldn't yield, but ignore if they do

        # Call setup (constructor) if exists (traditional style)
        elif 'setup' in blueprint.methods:
            self._call_action(blueprint.methods['setup'], args, kwargs, node, env, instance=instance)
        elif 'initiate' in blueprint.methods:
            self._call_action(blueprint.methods['initiate'], args, kwargs, node, env, instance=instance)

        return instance

    def eval_TypeofExpression(self, node: ast.TypeofExpression, env):
        """typeof x — o nome DataForge do tipo, igual ao usado nas anotações."""
        return self._type_of(self.evaluate(node.operand, env))

    def eval_CastExpression(self, node: ast.CastExpression, env):
        value = self.evaluate(node.operand, env)
        target = node.target_type
        cast_map = {
            "Integer": int, "int": int,
            "Float": float, "float": float,
            "String": str, "str": str,
            "Boolean": bool, "bool": bool,
            "Cluster": list, "list": list,
        }
        if target in cast_map:
            try:
                return cast_map[target](value)
            except (ValueError, TypeError) as e:
                raise TypeError_(f"Cannot cast to {target}: {e}", node.line, node.column)
        raise TypeError_(f"Unknown cast target: {target}", node.line, node.column)

    def eval_PipelineExpression(self, node: ast.PipelineExpression, env):
        data = self.evaluate(node.source, env)
        for op in node.operations:
            if isinstance(op, ast.SiftOperation):
                if op.func_ref:
                    # Named function reference: sift func_name
                    func = env.get(op.func_ref)
                    data = [item for item in data if self._call_func(func, [item], op)]
                else:
                    data = [item for item in data if self._eval_lambda(op.param, op.condition, item, env)]
            elif isinstance(op, ast.MorphOperation):
                if op.func_ref:
                    # Named function reference: morph func_name
                    func = env.get(op.func_ref)
                    data = [self._call_func(func, [item], op) for item in data]
                else:
                    data = [self._eval_lambda(op.param, op.expression, item, env) for item in data]
            elif isinstance(op, ast.DistillOperation):
                if op.func_ref:
                    # Named function reference: distill func_name initial_value
                    func = env.get(op.func_ref)
                    acc = self.evaluate(op.initial, env) if op.initial else data[0]
                    start = 0 if op.initial is not None else 1
                    for item in data[start:]:
                        acc = self._call_func(func, [acc, item], op)
                    data = acc
                else:
                    acc = self.evaluate(op.initial, env) if op.initial else data[0]
                    start = 0 if op.initial else 1
                    for item in data[start:]:
                        local = env.child("<distill>")
                        local.set_local(op.acc_param, acc)
                        local.set_local(op.val_param, item)
                        acc = self.evaluate(op.expression, local)
                    data = acc
        return data

    def _call_func(self, func, args, node):
        """Call a DFAction or Python callable with given args."""
        if isinstance(func, DFAction):
            local = func.closure.child(func.name)
            for i, param in enumerate(func.params):
                if i < len(args):
                    local.set_local(param, args[i])
                elif param in func.defaults:
                    local.set_local(param, self.evaluate(func.defaults[param], func.closure))
            try:
                self.exec_block(func.body, local)
                return None
            except YieldSignal as ys:
                return ys.value
            finally:
                self._run_deferred(local)
        elif callable(func):
            return func(*args)
        raise TypeError_("Value is not callable in a pipeline stage", node.line, node.column)

    def eval_AwaitExpression(self, node: ast.AwaitExpression, env):
        result = self.evaluate(node.expression, env)
        if asyncio.iscoroutine(result):
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(result)
            finally:
                loop.close()
        return result

    def eval_InExpression(self, node: ast.InExpression, env):
        prompt = ""
        if node.prompt:
            prompt = self.evaluate(node.prompt, env)
        return input(self._to_str(prompt))

    def eval_FrameExpression(self, node: ast.FrameExpression, env):
        data = self.evaluate(node.data, env)
        # Return as a simple list-of-lists (DataFrame simulation)
        return {"__type__": "Frame", "data": data, "columns": node.columns}

    def eval_TrainExpression(self, node: ast.TrainExpression, env):
        model = self.evaluate(node.model, env)
        data = self.evaluate(node.data, env)
        return {"__type__": "TrainedModel", "model": model, "data": data}

    def eval_PredictExpression(self, node: ast.PredictExpression, env):
        model = self.evaluate(node.model, env)
        data = self.evaluate(node.data, env)
        return {"__type__": "Prediction", "model": model, "data": data}

    # ═══════════════════════════════════════════════════════
    #  STATEMENT EXECUTION
    # ═══════════════════════════════════════════════════════

    def exec_OutStatement(self, node: ast.OutStatement, env):
        values = [self._to_str(self.evaluate(expr, env)) for expr in node.expressions]
        print(' '.join(values))

    def exec_EmitStatement(self, node, env):
        """Fora de um 'stream action', 'emit' é um alias histórico de 'out'.

        Dentro do corpo de um stream ele é interceptado por _lazy_stmt e produz
        um valor em vez de imprimir.
        """
        valores = [self.evaluate(e, env) for e in node.expressions]
        print(' '.join(self._to_str(v) for v in valores))
        return None

    def exec_YieldStatement(self, node: ast.YieldStatement, env):
        value = self.evaluate(node.value, env) if node.value else None
        raise YieldSignal(value)

    def exec_HaltStatement(self, node: ast.HaltStatement, env):
        raise HaltSignal()

    def exec_SkipStatement(self, node: ast.SkipStatement, env):
        raise SkipSignal()

    def exec_TriggerStatement(self, node: ast.TriggerStatement, env):
        value = self.evaluate(node.value, env)
        raise TriggerError(self._to_str(value), node.line, node.column)

    def exec_DeleteStatement(self, node: ast.DeleteStatement, env):
        if isinstance(node.target, ast.Identifier):
            env.delete(node.target.name)
        elif isinstance(node.target, ast.IndexAccess):
            obj = self.evaluate(node.target.object, env)
            idx = self.evaluate(node.target.index, env)
            del obj[idx]
        else:
            raise RuntimeError_("Cannot delete this expression", node.line, node.column)

    def exec_AssertStatement(self, node: ast.AssertStatement, env):
        condition = self.evaluate(node.condition, env)
        if not condition:
            msg = "Assertion failed"
            if node.message:
                msg = self._to_str(self.evaluate(node.message, env))
            raise RuntimeError_(msg, node.line, node.column)

    def exec_WaitStatement(self, node: ast.WaitStatement, env):
        duration = self.evaluate(node.duration, env)
        time.sleep(duration / 1000.0)  # milliseconds

    def exec_InspectStatement(self, node: ast.InspectStatement, env):
        value = self.evaluate(node.expression, env)
        type_name = self.eval_TypeofExpression(
            ast.TypeofExpression(operand=node.expression, line=node.line, column=node.column), env
        ) if isinstance(node.expression, ast.Identifier) else type(value).__name__
        print(f"[INSPECT] type={type_name} value={value!r}")

    def exec_Assignment(self, node: ast.Assignment, env):
        value = self.evaluate(node.value, env)

        declared = getattr(node, 'declared_type', "")
        if declared:
            self._check_type(value, declared, f"variable '{self._target_name(node.target)}'", node)

        if isinstance(node.target, ast.Identifier):
            env.set(node.target.name, value)
        elif isinstance(node.target, ast.MemberAccess):
            obj = self.evaluate(node.target.object, env)
            if isinstance(obj, DFRecordInstance):
                raise RuntimeError_(
                    f"Record '{obj.record.name}' is immutable: cannot assign to "
                    f"'{node.target.member}'. Build a changed copy with "
                    f"\"registro with {{'{node.target.member}': valor}}\".",
                    node.line, node.column)
            if isinstance(obj, DFInstance):
                membro = node.target.member
                # Propriedade com 'set': a atribuicao roda o corpo do setter
                prop = obj.blueprint.buscar_propriedade(membro)
                if prop is not None:
                    if 'set' not in prop:
                        raise TypeError_(
                            f"'{obj.blueprint.name}.{membro}' is read-only: it "
                            f"has a 'get' but no 'set'.\n"
                            f"    Add one:  set {membro}(valor): …",
                            node.line, node.column)
                    self._conferir_acesso(obj.blueprint, membro, env, node.target)
                    self._call(prop['set'], [value], {}, node, env, instancia=obj)
                    return value
                self._conferir_acesso(obj.blueprint, membro, env, node.target)
                obj.set(membro, value)
            elif isinstance(obj, DFBlueprint):
                obj.statics[node.target.member] = value
            elif isinstance(obj, dict):
                obj[node.target.member] = value
            else:
                raise RuntimeError_(
                    f"Cannot set member on {type(obj).__name__}",
                    node.line, node.column
                )
        elif isinstance(node.target, ast.IndexAccess):
            obj = self.evaluate(node.target.object, env)
            idx = self.evaluate(node.target.index, env)
            obj[idx] = value
        else:
            raise RuntimeError_("Invalid assignment target", node.line, node.column)

        return value

    def exec_SteadyDeclaration(self, node: ast.SteadyDeclaration, env):
        value = self.evaluate(node.value, env)
        env.define_steady(node.name, value)
        return value

    def exec_ShadowDeclaration(self, node: ast.ShadowDeclaration, env):
        value = self.evaluate(node.value, env)
        env.define_shadow(node.name, value)
        return value

    def exec_StaticDeclaration(self, node: ast.StaticDeclaration, env):
        value = self.evaluate(node.value, env)
        env.set_local(node.name, value)
        return value

    # ── Control Flow ───────────────────────────────────────

    def exec_GivenBlock(self, node: ast.GivenBlock, env):
        condition = self.evaluate(node.condition, env)
        if condition:
            return self.exec_block(node.body, env.child("<given>"))

        for orif_cond, orif_body in node.orif_blocks:
            if self.evaluate(orif_cond, env):
                return self.exec_block(orif_body, env.child("<orif>"))

        if node.otherwise_body:
            return self.exec_block(node.otherwise_body, env.child("<otherwise>"))

        return None

    def exec_MatchBlock(self, node: ast.MatchBlock, env):
        valor = self.evaluate(node.expression, env)

        for caso in node.points:
            # Compatibilidade: 'point' antigo guardado como tupla (valor, corpo)
            if isinstance(caso, tuple):
                alvo, corpo = caso
                if valor == self.evaluate(alvo, env):
                    return self.exec_block(corpo, env.child("<point>"))
                continue

            ligacoes = {}
            if not self._match_pattern(caso.pattern, valor, env, ligacoes):
                continue
            escopo = env.child("<point>")
            for nome, ligado in ligacoes.items():
                escopo.set_local(nome, ligado)
            if caso.guard is not None and not self.evaluate(caso.guard, escopo):
                continue
            return self.exec_block(caso.body, escopo)

        if node.default_body:
            return self.exec_block(node.default_body, env.child("<default>"))
        return None

    # ── Loops ──────────────────────────────────────────────

    def exec_CycleFromTo(self, node: ast.CycleFromTo, env):
        start = self.evaluate(node.start, env)
        end = self.evaluate(node.end, env)
        step = self.evaluate(node.step, env) if node.step else 1

        i = start
        while (step > 0 and i <= end) or (step < 0 and i >= end):
            loop_env = env.child("<cycle>")
            loop_env.set_local(node.var, i)
            try:
                self.exec_block(node.body, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                pass
            i += step

    def exec_CycleIn(self, node: ast.CycleIn, env):
        collection = self.evaluate(node.collection, env)
        if not hasattr(collection, '__iter__'):
            raise TypeError_(
                f"Cannot cycle over {self._type_of(collection)}: "
                f"expected a Cluster, Vault or String",
                node.line, node.column)
        for item in collection:
            loop_env = env.child("<cycle>")
            loop_env.set_local(node.var, item)
            try:
                self.exec_block(node.body, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue

    def exec_PersistBlock(self, node: ast.PersistBlock, env):
        while self.evaluate(node.condition, env):
            loop_env = env.child("<persist>")
            try:
                self.exec_block(node.body, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue

    def exec_PerformBlock(self, node: ast.PerformBlock, env):
        while True:
            loop_env = env.child("<perform>")
            try:
                self.exec_block(node.body, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                pass
            if not self.evaluate(node.condition, env):
                break

    # ── Functions & Classes ────────────────────────────────

    def exec_ActionDeclaration(self, node: ast.ActionDeclaration, env):
        action = DFAction(
            name=node.name,
            params=node.params,
            defaults=node.defaults,
            body=node.body,
            closure=env,
            is_async=node.is_async,
            param_types=getattr(node, 'param_types', None),
            return_type=getattr(node, 'return_type', ""),
            is_generator=getattr(node, 'is_generator', False),
        )
        env.set_local(node.name, action)

        # Apply 'mark @decorator' wrappers, innermost (closest) first.
        value = action
        for deco in reversed(getattr(node, 'decorators', []) or []):
            wrapper = env.get(deco.name)
            deco_args = [self.evaluate(a, env) for a in getattr(deco, 'args', []) or []]
            if deco_args:
                factory = self._call(wrapper, deco_args, {}, node, env)
                value = self._call(factory, [value], {}, node, env)
            else:
                value = self._call(wrapper, [value], {}, node, env)
            env.set_local(node.name, value)
        return value

    def exec_BlueprintDeclaration(self, node: ast.BlueprintDeclaration, env):
        parents = []
        for pname in node.parents:
            try:
                parent = env.get(pname)
                if isinstance(parent, DFBlueprint):
                    parents.append(parent)
            except NameError_:
                pass  # Trait or not found

        bp_env = env.child(f"<blueprint {node.name}>")
        methods, statics = {}, {}
        properties, operators, visibility = {}, {}, {}
        abstract_methods, static_methods, final_methods = set(), set(), set()
        origem_abstrata = {}          # metodo -> quem exigiu (trait ou pai)
        constructor_body = []

        # Herda do pai: metodos, estaticos, propriedades e operadores
        for parent in parents:
            methods.update(parent.methods)
            statics.update(parent.statics)
            properties.update(parent.properties)
            operators.update(parent.operators)
            static_methods |= parent.static_methods
            final_methods |= parent.final_methods

        # Traits: so preenchem o que ainda nao existe
        traits_adotados = list(getattr(node, 'traits', []))
        for tname in traits_adotados:
            try:
                trait = env.get(tname)
            except NameError_:
                continue
            if not isinstance(trait, DFBlueprint):
                continue
            for mname, mval in trait.methods.items():
                if mname not in methods:
                    methods[mname] = mval
            for pname, pval in trait.properties.items():
                properties.setdefault(pname, pval)
            for n in trait.abstract_methods:
                if n not in methods:
                    abstract_methods.add(n)
                    origem_abstrata[n] = tname

        for stmt in node.body:
            if isinstance(stmt, ast.ActionDeclaration):
                nome = stmt.name
                # 'final' do pai nao pode ser sobrescrito
                if nome in final_methods:
                    dono = next((bp.name for bp in
                                 (p for pa in parents for p in pa.linhagem())
                                 if nome in bp.methods), "the parent")
                    raise TypeError_(
                        f"'{node.name}.{nome}' cannot override "
                        f"'{dono}.{nome}', which is declared final",
                        stmt.line, stmt.column)

                if getattr(stmt, 'is_abstract', False):
                    abstract_methods.add(nome)
                else:
                    abstract_methods.discard(nome)

                action = DFAction(
                    name=nome, params=stmt.params,
                    defaults=stmt.defaults, body=stmt.body,
                    closure=bp_env, is_async=stmt.is_async,
                    param_types=getattr(stmt, 'param_types', None),
                    return_type=getattr(stmt, 'return_type', ""),
                )
                action.is_abstract = getattr(stmt, 'is_abstract', False)
                action.owner = node.name
                methods[nome] = action

                visibility[nome] = getattr(stmt, 'visibility', 'public')
                if getattr(stmt, 'is_static', False):
                    static_methods.add(nome)
                    statics[nome] = action
                if getattr(stmt, 'is_final', False):
                    final_methods.add(nome)

            elif isinstance(stmt, ast.PropertyDeclaration):
                acao = DFAction(
                    name=stmt.name,
                    params=[stmt.param] if stmt.kind == 'set' else [],
                    defaults={}, body=stmt.body, closure=bp_env,
                    return_type=getattr(stmt, 'return_type', ""))
                acao.owner = node.name
                properties.setdefault(stmt.name, {})
                properties[stmt.name] = {**properties[stmt.name],
                                         stmt.kind: acao}
                visibility[stmt.name] = getattr(stmt, 'visibility', 'public')

            elif isinstance(stmt, ast.OperatorDeclaration):
                acao = DFAction(name=f"operator{stmt.symbol}",
                                params=[stmt.param], defaults={},
                                body=stmt.body, closure=bp_env)
                acao.owner = node.name
                operators[stmt.symbol] = acao

            elif isinstance(stmt, ast.StaticDeclaration):
                statics[stmt.name] = self.evaluate(stmt.value, bp_env)

            elif isinstance(stmt, ast.Assignment):
                if node.constructor_params:
                    constructor_body.append(stmt)
                elif isinstance(stmt.target, ast.Identifier):
                    statics[stmt.target.name] = self.evaluate(stmt.value, bp_env)

            elif node.constructor_params:
                constructor_body.append(stmt)

        # Campos declarados: 'nome: Tipo := padrao'
        campos = []
        for nome, tipo, padrao, visib in getattr(node, 'fields_decl', []):
            valor = self.evaluate(padrao, bp_env) if padrao is not None else None
            campos.append((nome, tipo, valor, visib))
            visibility[nome] = visib
        for parent in parents:
            declarados = {c[0] for c in campos}
            campos = [c for c in parent.fields_decl
                      if c[0] not in declarados] + campos

        blueprint = DFBlueprint(
            name=node.name, parents=parents,
            methods=methods, statics=statics, env=bp_env,
            constructor_params=node.constructor_params,
            constructor_body=constructor_body,
            properties=properties, operators=operators,
            fields_decl=campos, visibility=visibility,
            is_abstract=getattr(node, 'is_abstract', False),
            abstract_methods=abstract_methods,
            static_methods=static_methods,
            final_methods=final_methods,
            traits=traits_adotados,
        )
        blueprint.origem_abstrata = origem_abstrata

        # Contrato de trait: conferido aqui, na declaracao, e nao na chamada.
        # Descobrir que falta um metodo so quando alguem o chama, em producao,
        # e tarde demais.
        if not blueprint.is_abstract:
            self._conferir_contrato(blueprint, node, env)

        bp_env.set_local(node.name, blueprint)
        env.set_local(node.name, blueprint)
        return blueprint

    def _conferir_contrato(self, blueprint, node, env):
        """Um blueprint concreto precisa implementar tudo o que prometeu."""
        faltando = blueprint.pendencias_abstratas()
        faltando.update({n: o for n, o in
                         getattr(blueprint, 'origem_abstrata', {}).items()
                         if n in faltando})
        if not faltando:
            return

        itens = sorted(faltando.items())
        linhas = [f"    {nome}()  — declarado em '{origem}'"
                  for nome, origem in itens]
        plural = "methods" if len(itens) > 1 else "method"
        raise TypeError_(
            f"Blueprint '{node.name}' does not implement {len(itens)} "
            f"abstract {plural}:\n" + "\n".join(linhas) +
            f"\n    Implement {'them' if len(itens) > 1 else 'it'}, or mark "
            f"'{node.name}' as 'abstract blueprint' if it is not meant to be "
            f"spawned directly.",
            node.line, node.column)

    def exec_TraitDeclaration(self, node: ast.TraitDeclaration, env):
        """Um trait e um blueprint so com contrato.

        Metodo com corpo vira implementacao padrao; metodo sem corpo vira
        exigencia — quem adotar o trait precisa implementar.
        """
        methods, properties, abstratos = {}, {}, set()

        for stmt in node.methods:
            if isinstance(stmt, ast.PropertyDeclaration):
                acao = DFAction(
                    name=stmt.name,
                    params=[stmt.param] if stmt.kind == 'set' else [],
                    defaults={}, body=stmt.body, closure=env)
                acao.owner = node.name
                properties.setdefault(stmt.name, {})[stmt.kind] = acao
                continue

            if not isinstance(stmt, ast.ActionDeclaration):
                continue

            # Sem corpo (ou so com o marcador abstract) = exigencia
            vazio = not stmt.body or getattr(stmt, 'is_abstract', False)
            if vazio:
                abstratos.add(stmt.name)

            action = DFAction(
                name=stmt.name, params=stmt.params,
                defaults=stmt.defaults, body=stmt.body,
                closure=env,
                param_types=getattr(stmt, 'param_types', None),
                return_type=getattr(stmt, 'return_type', ""),
            )
            action.is_abstract = vazio
            action.owner = node.name
            if not vazio:
                methods[stmt.name] = action

        blueprint = DFBlueprint(
            name=node.name, parents=[], methods=methods,
            statics={}, env=env, properties=properties,
            is_abstract=True, abstract_methods=abstratos,
        )
        env.set_local(node.name, blueprint)
        return blueprint

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — RECORDS E ENUMS
    # ═══════════════════════════════════════════════════════

    def exec_RecordDeclaration(self, node, env):
        rec_env = env.child(f"<record {node.name}>")
        metodos = {}
        for nome, decl in node.methods.items():
            metodos[nome] = DFAction(
                name=nome, params=decl.params, defaults=decl.defaults,
                body=decl.body, closure=rec_env,
                param_types=getattr(decl, 'param_types', None),
                return_type=getattr(decl, 'return_type', ""))
        record = DFRecord(node.name, node.fields, metodos, rec_env)
        rec_env.set_local(node.name, record)
        env.set_local(node.name, record)
        return record

    def exec_EnumDeclaration(self, node, env):
        enum_env = env.child(f"<enum {node.name}>")
        membros = {}
        for indice, (nome, valor_node) in enumerate(node.members):
            valor = self.evaluate(valor_node, enum_env) if valor_node is not None else nome
            membros[nome] = DFEnumMember(node.name, nome, valor, indice)
        metodos = {}
        for nome, decl in node.methods.items():
            metodos[nome] = DFAction(
                name=nome, params=decl.params, defaults=decl.defaults,
                body=decl.body, closure=enum_env,
                param_types=getattr(decl, 'param_types', None),
                return_type=getattr(decl, 'return_type', ""))
        enum = DFEnum(node.name, membros, metodos, enum_env)
        enum_env.set_local(node.name, enum)
        env.set_local(node.name, enum)
        return enum

    def _build_record(self, record: DFRecord, args, kwargs, node, env):
        """Constrói uma instância de record a partir dos argumentos."""
        nomes = record.field_names
        if len(args) > len(nomes):
            raise TypeError_(
                f"Record '{record.name}' has {len(nomes)} field(s) "
                f"but {len(args)} value(s) were given",
                node.line, node.column)
        desconhecidos = [k for k in kwargs if k not in nomes]
        if desconhecidos:
            raise NameError_(
                f"Record '{record.name}' has no field(s): "
                f"{', '.join(desconhecidos)}. It has: {', '.join(nomes)}",
                node.line, node.column)

        valores = {}
        for indice, nome in enumerate(nomes):
            tipo, padrao = record.field_types[nome], record.fields[indice][2]
            if indice < len(args):
                valor = args[indice]
            elif nome in kwargs:
                valor = kwargs[nome]
            elif padrao is not None:
                valor = self.evaluate(padrao, record.env)
            else:
                raise TypeError_(
                    f"Record '{record.name}' is missing field '{nome}'",
                    node.line, node.column)
            if tipo:
                self._check_type(valor, tipo,
                                 f"field '{nome}' of record '{record.name}'", node)
            valores[nome] = valor
        return DFRecordInstance(record, valores)

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — DESESTRUTURAÇÃO
    # ═══════════════════════════════════════════════════════

    def exec_DestructuringAssignment(self, node, env):
        valor = self.evaluate(node.value, env)

        if node.is_mapping:
            for nome, is_rest in node.targets:
                if is_rest:
                    usados = {n for n, r in node.targets if not r}
                    if isinstance(valor, DFRecordInstance):
                        resto = {k: v for k, v in valor.values.items() if k not in usados}
                    elif isinstance(valor, dict):
                        resto = {k: v for k, v in valor.items() if k not in usados}
                    else:
                        raise TypeError_(
                            f"Cannot destructure {self._type_of(valor)} with {{...}}",
                            node.line, node.column)
                    env.set(nome, resto)
                    continue
                if isinstance(valor, DFRecordInstance):
                    env.set(nome, valor.get(nome))
                elif isinstance(valor, dict):
                    if nome not in valor:
                        raise NameError_(
                            f"Vault has no key '{nome}' to destructure. "
                            f"Keys: {', '.join(str(k) for k in valor)}",
                            node.line, node.column)
                    env.set(nome, valor[nome])
                elif isinstance(valor, DFInstance):
                    env.set(nome, valor.get(nome))
                else:
                    raise TypeError_(
                        f"Cannot destructure {self._type_of(valor)} with {{...}}: "
                        f"expected a record, a vault or an instance",
                        node.line, node.column)
            return valor

        if isinstance(valor, DFStream):
            valor = list(valor)
        if isinstance(valor, DFRecordInstance):
            valor = [valor.values[n] for n in valor.record.field_names]
        if isinstance(valor, dict):
            valor = list(valor.items())
        if not hasattr(valor, '__iter__') or isinstance(valor, str) and len(node.targets) > len(valor):
            if not hasattr(valor, '__iter__'):
                raise TypeError_(
                    f"Cannot destructure {self._type_of(valor)}: "
                    f"expected a Cluster or a record",
                    node.line, node.column)
        itens = list(valor)

        rest_pos = next((i for i, (_, r) in enumerate(node.targets) if r), -1)
        fixos = len(node.targets) - (1 if rest_pos >= 0 else 0)
        if rest_pos < 0 and len(itens) != fixos:
            raise RuntimeError_(
                f"Cannot unpack {len(itens)} value(s) into {fixos} name(s)",
                node.line, node.column)
        if rest_pos >= 0 and len(itens) < fixos:
            raise RuntimeError_(
                f"Cannot unpack {len(itens)} value(s): at least {fixos} needed",
                node.line, node.column)

        if rest_pos < 0:
            for (nome, _), item in zip(node.targets, itens):
                env.set(nome, item)
        else:
            antes = node.targets[:rest_pos]
            depois = node.targets[rest_pos + 1:]
            for (nome, _), item in zip(antes, itens[:len(antes)]):
                env.set(nome, item)
            fim = len(itens) - len(depois)
            env.set(node.targets[rest_pos][0], itens[len(antes):fim])
            for (nome, _), item in zip(depois, itens[fim:]):
                env.set(nome, item)
        return valor

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — PATTERN MATCHING
    # ═══════════════════════════════════════════════════════

    def _match_pattern(self, padrao, valor, env, ligacoes):
        """Tenta casar 'valor' com 'padrao'. Preenche 'ligacoes'. Devolve bool."""
        casou = self._match_pattern_inner(padrao, valor, env, ligacoes)
        if casou and getattr(padrao, 'binding', ''):
            ligacoes[padrao.binding] = valor
        return casou

    def _match_pattern_inner(self, padrao, valor, env, ligacoes):
        if isinstance(padrao, ast.WildcardPattern):
            return True

        if isinstance(padrao, ast.LiteralPattern):
            return valor == padrao.value and (
                type(valor) is type(padrao.value)
                or not isinstance(padrao.value, bool) and not isinstance(valor, bool))

        if isinstance(padrao, ast.CapturePattern):
            ligacoes[padrao.name] = valor
            return True

        if isinstance(padrao, ast.ValuePattern):
            return valor == self.evaluate(padrao.expression, env)

        if isinstance(padrao, ast.OrPattern):
            for opcao in padrao.options:
                tentativa = {}
                if self._match_pattern(opcao, valor, env, tentativa):
                    ligacoes.update(tentativa)
                    return True
            return False

        if isinstance(padrao, ast.SequencePattern):
            # Só sequências de verdade: um vault casa com {..}, não com [..].
            if isinstance(valor, DFStream):
                valor = list(valor)
            if not isinstance(valor, (list, tuple)):
                return False
            itens = list(valor)
            fixos = padrao.elements
            if padrao.rest_index < 0:
                if len(itens) != len(fixos):
                    return False
                return all(self._match_pattern(p, i, env, ligacoes)
                           for p, i in zip(fixos, itens))
            antes = fixos[:padrao.rest_index]
            depois = fixos[padrao.rest_index:]
            if len(itens) < len(antes) + len(depois):
                return False
            for p, i in zip(antes, itens[:len(antes)]):
                if not self._match_pattern(p, i, env, ligacoes):
                    return False
            fim = len(itens) - len(depois)
            if padrao.rest_name:
                ligacoes[padrao.rest_name] = itens[len(antes):fim]
            for p, i in zip(depois, itens[fim:]):
                if not self._match_pattern(p, i, env, ligacoes):
                    return False
            return True

        if isinstance(padrao, ast.MappingPattern):
            if isinstance(valor, DFRecordInstance):
                mapa = valor.values
            elif isinstance(valor, DFInstance):
                mapa = valor.fields
            elif isinstance(valor, dict):
                mapa = valor
            else:
                return False
            usadas = set()
            for chave_node, sub in padrao.pairs:
                chave = self.evaluate(chave_node, env)
                if chave not in mapa:
                    return False
                usadas.add(chave)
                if not self._match_pattern(sub, mapa[chave], env, ligacoes):
                    return False
            if padrao.rest_name:
                ligacoes[padrao.rest_name] = {
                    k: v for k, v in mapa.items() if k not in usadas}
            return True

        if isinstance(padrao, ast.TypePattern):
            if not self._value_has_type(valor, padrao.type_name, env):
                return False
            if padrao.sub_patterns:
                campos = self._positional_fields(valor)
                if campos is None or len(campos) < len(padrao.sub_patterns):
                    return False
                for sub, item in zip(padrao.sub_patterns, campos):
                    if not self._match_pattern(sub, item, env, ligacoes):
                        return False
            for campo, sub in padrao.field_patterns.items():
                try:
                    atual = self._field_of(valor, campo)
                except (NameError_, KeyError):
                    return False
                if not self._match_pattern(sub, atual, env, ligacoes):
                    return False
            return True

        return False

    def _value_has_type(self, valor, nome_tipo, env) -> bool:
        canonico = self.TYPE_ALIASES.get(nome_tipo, nome_tipo)
        if canonico == "Any":
            return True
        if canonico == "Number":
            return isinstance(valor, (int, float)) and not isinstance(valor, bool)
        atual = self._type_of(valor)
        if atual == canonico:
            return True
        if isinstance(valor, DFInstance):
            return any(bp.name == nome_tipo for bp in valor.get_mro())
        if isinstance(valor, DFRecordInstance):
            return valor.record.name == nome_tipo
        if isinstance(valor, DFEnumMember):
            return valor.enum_name == nome_tipo
        return False

    def _positional_fields(self, valor):
        if isinstance(valor, DFRecordInstance):
            return [valor.values[n] for n in valor.record.field_names]
        if isinstance(valor, DFInstance):
            return list(valor.fields.values())
        if isinstance(valor, (list, tuple)):
            return list(valor)
        return None

    def _field_of(self, valor, campo):
        if isinstance(valor, DFRecordInstance):
            return valor.get(campo)
        if isinstance(valor, DFInstance):
            return valor.get(campo)
        if isinstance(valor, dict):
            return valor[campo]
        raise NameError_(f"No field '{campo}'")

    # ── Error Handling ─────────────────────────────────────

    def exec_MonitorBlock(self, node: ast.MonitorBlock, env):
        try:
            return self.exec_block(node.body, env.child("<monitor>"))
        except Exception as e:
            # A 'monitor' with no 'handle' is a try/finally: never swallow the error.
            if not node.handle_body:
                raise
            if not self._error_matches(e, node.handle_type, env):
                raise
            handle_env = env.child("<handle>")
            handle_env.set_local(node.handle_name, self._error_value(e))
            return self.exec_block(node.handle_body, handle_env)
        finally:
            if node.ensure_body:
                self.exec_block(node.ensure_body, env.child("<ensure>"))

    def _error_value(self, exc):
        """Wrap a caught exception into the value bound by 'handle'."""
        message = exc.message if isinstance(exc, DataForgeError) else str(exc)
        return DFError(type(exc).__name__.rstrip('_'), message, exc)

    def _error_matches(self, exc, handle_type, env) -> bool:
        """Check whether a caught exception matches an optional 'handle <Type>' filter."""
        if not handle_type:
            return True
        name = type(exc).__name__.rstrip('_')
        if handle_type in (name, type(exc).__name__):
            return True
        # Allow the generic aliases used in the docs.
        aliases = {
            "Error": True,
            "Exception": True,
            "Any": True,
        }
        return bool(aliases.get(handle_type))

    # ── Modules ────────────────────────────────────────────

    def exec_AdoptStatement(self, node: ast.AdoptStatement, env):
        """Importa um módulo da stdlib ou um arquivo .df vizinho.

        Três formas:
            adopt Arcane.Math as M          — o módulo inteiro, sob um nome
            adopt Arcane.Math.{sqrt, floor} — só os símbolos nomeados
            adopt {sqrt} from Arcane.Math   — idem, com a ordem invertida
        """
        nome_modulo = node.module
        modulo = self._resolver_modulo(nome_modulo, node, env)

        if node.selection:
            faltando = [n for n, _ in node.selection if n not in modulo]
            if faltando:
                disponiveis = sorted(k for k in modulo if not k.startswith('__'))
                raise ImportError_(
                    f"Module '{nome_modulo}' does not export: "
                    f"{', '.join(faltando)}. "
                    f"It exports: {', '.join(disponiveis[:10])}"
                    f"{'…' if len(disponiveis) > 10 else ''}",
                    node.line, node.column)
            for nome, apelido in node.selection:
                env.set_local(apelido, modulo[nome])
            return

        alias = node.alias or nome_modulo.split('.')[-1]
        env.set_local(alias, modulo)

    def _resolver_modulo(self, nome_modulo, node, env):
        """Encontra o módulo: cache, stdlib ou arquivo .df."""
        if nome_modulo in self.modules:
            return self.modules[nome_modulo]

        from .stdlib import get_module, list_modules
        modulo = get_module(nome_modulo)
        if modulo is not None:
            self.modules[nome_modulo] = modulo
            return modulo

        import os
        # Caminhos relativos ao arquivo que faz o import, não ao diretório atual
        bases = []
        if self.filename and not self.filename.startswith('<'):
            bases.append(os.path.dirname(os.path.abspath(self.filename)))
        bases.append(os.getcwd())

        partes = nome_modulo.replace('.', os.sep)
        for base in bases:
            for sufixo in ('.df', os.path.join('', 'main.df')):
                caminho = os.path.join(base, partes + sufixo) if sufixo == '.df' \
                    else os.path.join(base, partes, 'main.df')
                if os.path.exists(caminho):
                    return self._load_module_file(caminho, nome_modulo)

        # Pacotes instalados: forge_modules/<pacote>/, procurando a partir
        # do arquivo atual para cima — assim um .df em qualquer subpasta do
        # projeto enxerga o que 'dataforge add' instalou na raiz.
        caminho = self._procurar_em_pacotes(nome_modulo, bases)
        if caminho:
            return self._load_module_file(caminho, nome_modulo)

        disponiveis = sorted(set(list_modules()))
        instalados = self._pacotes_instalados(bases)
        dica = ""
        if instalados:
            import difflib
            raiz_pedida = nome_modulo.split('.')[0]
            perto = difflib.get_close_matches(raiz_pedida, instalados, n=2, cutoff=0.6)
            if perto:
                dica = f" Installed packages: {', '.join(perto)}."
            else:
                dica = f" Installed: {', '.join(sorted(instalados)[:6])}."
        else:
            dica = " No packages installed — try 'dataforge add <package>'."

        raise ImportError_(
            f"Module '{nome_modulo}' not found. "
            f"Looked in the standard library, next to "
            f"{os.path.basename(self.filename) if self.filename else 'the current file'}, "
            f"and in forge_modules/.{dica} "
            f"Standard library: {', '.join(disponiveis[:6])}…",
            node.line, node.column)

    @staticmethod
    def _raizes_de_projeto(bases):
        """Sobe de cada base ate achar forge_modules/ ou forge.toml."""
        import os
        raizes = []
        for base in bases:
            atual = os.path.abspath(base)
            while True:
                if os.path.isdir(os.path.join(atual, 'forge_modules')) or \
                        os.path.exists(os.path.join(atual, 'forge.toml')):
                    if atual not in raizes:
                        raizes.append(atual)
                    break
                pai = os.path.dirname(atual)
                if pai == atual:
                    break
                atual = pai
        return raizes

    def _procurar_em_pacotes(self, nome_modulo, bases):
        """Encontra o .df de um modulo dentro de forge_modules/.

        'adopt validador' carrega o ponto de entrada do pacote;
        'adopt validador.email' carrega src/email.df (ou email.df) dentro dele.
        """
        import os
        raiz_pacote, _, resto = nome_modulo.partition('.')
        for raiz in self._raizes_de_projeto(bases):
            pasta = os.path.join(raiz, 'forge_modules', raiz_pacote)
            if not os.path.isdir(pasta):
                continue

            if resto:
                sub = resto.replace('.', os.sep)
                for candidato in (os.path.join(pasta, 'src', sub + '.df'),
                                  os.path.join(pasta, sub + '.df'),
                                  os.path.join(pasta, 'src', sub, 'main.df'),
                                  os.path.join(pasta, sub, 'main.df')):
                    if os.path.exists(candidato):
                        return candidato
                continue

            entrada = self._entrada_do_pacote(pasta)
            if entrada and os.path.exists(entrada):
                return entrada
            for candidato in (os.path.join(pasta, 'src', 'main.df'),
                              os.path.join(pasta, 'main.df'),
                              os.path.join(pasta, f'{raiz_pacote}.df')):
                if os.path.exists(candidato):
                    return candidato
        return None

    @staticmethod
    def _entrada_do_pacote(pasta):
        """Le 'entry' do forge.toml do pacote, se houver."""
        import os
        manifesto = os.path.join(pasta, 'forge.toml')
        if not os.path.exists(manifesto):
            return None
        try:
            from .stdlib.arcane_serialization import ArcaneSerialization
            dados = ArcaneSerialization()['from_toml'](
                open(manifesto, encoding='utf-8').read())
            secao = dados.get('package') or dados.get('project') or {}
            entrada = secao.get('entry')
            return os.path.join(pasta, entrada) if entrada else None
        except Exception:
            return None

    def _pacotes_instalados(self, bases):
        import os
        nomes = []
        for raiz in self._raizes_de_projeto(bases):
            pasta = os.path.join(raiz, 'forge_modules')
            if os.path.isdir(pasta):
                nomes += [d for d in os.listdir(pasta)
                          if os.path.isdir(os.path.join(pasta, d))
                          and not d.startswith('.')]
        return sorted(set(nomes))

    def exec_RelayStatement(self, node: ast.RelayStatement, env):
        """Marca quais nomes o módulo exporta.

        Sem nenhum 'relay', o módulo exporta tudo o que definiu no topo — é o
        comportamento conveniente para scripts. Com pelo menos um 'relay', só
        os nomes listados atravessam o 'adopt'.
        """
        exportados = getattr(env, '_exports', None)
        if exportados is None:
            exportados = env._exports = []
        for nome in node.names:
            if not env.has(nome):
                raise NameError_(
                    f"'relay' exports '{nome}', which is not defined in this module",
                    node.line, node.column)
            exportados.append(nome)

    # ── Concurrency ────────────────────────────────────────

    def exec_ThreadBlock(self, node: ast.ThreadBlock, env):
        thread_env = env.child("<thread>")

        def thread_func():
            try:
                self.exec_block(node.body, thread_env)
            except Exception as e:
                print(f"[Thread Error] {e}")

        t = threading.Thread(target=thread_func, daemon=True)
        t.start()
        return t

    def exec_ChannelDeclaration(self, node: ast.ChannelDeclaration, env):
        ch = DFChannel(node.name)
        env.set_local(node.name, ch)
        return ch

    def exec_PulseStatement(self, node: ast.PulseStatement, env):
        event = self.evaluate(node.event, env)
        data = self.evaluate(node.data, env) if node.data else None
        event_name = self._to_str(event)
        if event_name in self.events:
            for callback in self.events[event_name]:
                self._call(callback, [data] if data else [], {}, node, env)

    # ── New Error Handling ─────────────────────────────────

    def exec_GuardStatement(self, node: ast.GuardStatement, env):
        """Guard: check condition, run else_body or trigger error if false.
        When the guard fails and else_body runs, raises YieldSignal to exit the function."""
        condition = self.evaluate(node.condition, env)
        if not condition:
            if node.else_body:
                for stmt in node.else_body:
                    self.execute(stmt, env)
                raise YieldSignal(None)
            msg = "Guard condition failed"
            if node.message:
                msg = self._to_str(self.evaluate(node.message, env))
            raise TriggerError(msg, node.line, node.column)

    def exec_RetryBlock(self, node: ast.RetryBlock, env):
        """Retry: attempt block up to N times."""
        count = self.evaluate(node.count, env)
        last_error = None
        for attempt in range(int(count)):
            try:
                return self.exec_block(node.body, env.child(f"<retry-{attempt}>"))
            except Exception as e:
                last_error = self._error_value(e)

        # All attempts failed
        if node.handle_body and last_error is not None:
            handle_env = env.child("<retry-handle>")
            handle_env.set_local(node.handle_name, last_error)
            return self.exec_block(node.handle_body, handle_env)
        return None

    def exec_ValidateStatement(self, node: ast.ValidateStatement, env):
        """Validate: check value is truthy, run else_body or trigger if not.
        When validation fails and else_body runs, raises YieldSignal to exit the function."""
        value = self.evaluate(node.value, env)
        if not value:
            if node.else_body:
                for stmt in node.else_body:
                    self.execute(stmt, env)
                raise YieldSignal(None)
            msg = "Validation failed"
            if node.message:
                msg = self._to_str(self.evaluate(node.message, env))
            raise TriggerError(msg, node.line, node.column)
        return value

    def exec_PropagateStatement(self, node: ast.PropagateStatement, env):
        """Re-raise an error."""
        if node.value:
            value = self.evaluate(node.value, env)
            raise TriggerError(self._to_str(value), node.line, node.column)
        raise TriggerError("Propagated error", node.line, node.column)

    def exec_DeferStatement(self, node: ast.DeferStatement, env):
        """Defer: schedule block to run at scope exit.
        Stores the deferred block in the environment's _deferred list."""
        if not hasattr(env, '_deferred'):
            env._deferred = []
        env._deferred.append((node.body, env))

    def exec_ObserveBlock(self, node: ast.ObserveBlock, env):
        """observe var in fonte: reage a cada item que chega.

        A fonte pode ser um Cluster, um DFStream (de um 'stream action'), ou o
        vault {"__type__": "Stream"} produzido por stream(colecao).
        """
        source = self.evaluate(node.source, env)

        if isinstance(source, DFStream):
            itens = source
        elif isinstance(source, (list, tuple)):
            itens = source
        elif isinstance(source, dict) and source.get("__type__") == "Stream":
            itens = source.get("data", [])
        elif isinstance(source, dict):
            itens = list(source.keys())
        elif isinstance(source, str):
            itens = source
        else:
            raise TypeError_(
                f"Cannot observe a value of type {self._type_of(source)}: "
                f"expected a Cluster, a Vault, a String or a stream",
                node.line, node.column)

        for item in itens:
            obs_env = env.child("<observe>")
            obs_env.set_local(node.var, item)
            try:
                self.exec_block(node.body, obs_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue

    def eval_StreamExpression(self, node: ast.StreamExpression, env):
        """Create a reactive stream from data."""
        data = self.evaluate(node.source, env)
        return {"__type__": "Stream", "data": data if isinstance(data, list) else [data]}

    def exec_ParallelBlock(self, node: ast.ParallelBlock, env):
        """Parallel: run sub-blocks in threads."""
        threads = []
        results = []

        # Group sequential statements into "blocks" separated by action declarations
        for stmt in node.blocks:
            thread_env = env.child("<parallel>")

            def run_stmt(s=stmt, e=thread_env):
                try:
                    return self.execute(s, e)
                except Exception as ex:
                    print(f"[Parallel Error] {ex}")

            t = threading.Thread(target=run_stmt, daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=30)

    # ═══════════════════════════════════════════════════════
    #  INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════

    #: Como cada tipo do runtime se chama em DataForge.
    _NOMES_DE_TIPO = {
        int: "an Integer", float: "a Float", str: "a String",
        bool: "a Boolean", list: "a Cluster", dict: "a Vault",
        type(None): "void",
    }

    def _nome_do_tipo(self, valor):
        """Descreve o tipo de um valor com o vocabulario da linguagem."""
        if isinstance(valor, DFInstance):
            return f"an instance of '{valor.blueprint.name}'"
        if isinstance(valor, DFBlueprint):
            return f"the blueprint '{valor.name}'"
        if isinstance(valor, DFRecord):
            return f"the record type '{valor.name}'"
        if isinstance(valor, DFRecordInstance):
            return f"a '{valor.record.name}' record"
        if isinstance(valor, DFEnum):
            return f"the enum '{valor.name}'"
        if isinstance(valor, DFAction):
            return f"the action '{valor.name}'"
        if isinstance(valor, BuiltinFunction):
            return f"the builtin '{valor.name}'"
        for tipo, nome in self._NOMES_DE_TIPO.items():
            if type(valor) is tipo:
                return nome
        return f"a {type(valor).__name__}"

    # ── Visibilidade e diagnostico de membros ────────────────

    def _conferir_acesso(self, blueprint, membro, env, node):
        """'private' so dentro do proprio blueprint; 'protected' tambem nos herdeiros.

        O escopo diz de onde a leitura partiu: um ambiente '<blueprint X>'
        na cadeia significa que estamos dentro de X.
        """
        visib = blueprint.visibilidade_de(membro)
        if visib == "public":
            return

        de_dentro = self._blueprint_do_escopo(env)
        if de_dentro is None:
            onde = "outside any blueprint"
        else:
            if visib == "private" and de_dentro == blueprint.name:
                return
            if visib == "protected" and any(
                    bp.name == de_dentro for bp in blueprint.linhagem()):
                return
            onde = f"from '{de_dentro}'"

        dica = (f"Only '{blueprint.name}' can read it."
                if visib == "private"
                else f"Only '{blueprint.name}' and its subtypes can read it.")
        raise TypeError_(
            f"'{blueprint.name}.{membro}' is {visib} and was accessed {onde}. "
            f"{dica}",
            node.line, node.column)

    @staticmethod
    def _blueprint_do_escopo(env):
        """Nome do blueprint em cujo corpo estamos, ou None."""
        atual = env
        while atual is not None:
            nome = getattr(atual, "name", "") or ""
            if nome.startswith("<blueprint "):
                return nome[len("<blueprint "):-1]
            atual = getattr(atual, "parent", None)
        return None

    def _erro_membro_blueprint(self, blueprint, node):
        """Membro inexistente: diz o que existe, e sugere o parecido."""
        import difflib
        disponiveis = sorted(
            set(blueprint.statics) | set(blueprint.methods) |
            set(blueprint.properties) | {c[0] for c in blueprint.fields_decl})
        perto = difflib.get_close_matches(node.member, disponiveis, n=1, cutoff=0.6)

        msg = f"Blueprint '{blueprint.name}' has no member '{node.member}'."
        if perto:
            msg += f"\n    Did you mean '{perto[0]}'?"
        elif disponiveis:
            mostra = ", ".join(disponiveis[:8])
            resto = "…" if len(disponiveis) > 8 else ""
            msg += f"\n    It has: {mostra}{resto}"
        raise NameError_(msg, node.line, node.column)

    def _call(self, callee, args, kwargs, node, env, instancia=None):
        """Call a callable value.

        Com 'instancia', a acao roda como metodo: 'self' aponta para ela.
        """
        if instancia is not None and isinstance(callee, DFAction):
            return self._call_action(callee, args, kwargs, node, env,
                                     instance=instancia)
        if isinstance(callee, BuiltinFunction):
            try:
                return callee(*args, **kwargs)
            except Exception as e:
                raise RuntimeError_(str(e), node.line, node.column)

        if isinstance(callee, DFAction):
            return self._call_action(callee, args, kwargs, node, env)

        if isinstance(callee, DFRecord):
            return self._build_record(callee, args, kwargs, node, env)

        if isinstance(callee, DFEnum):
            # Enum(valor) procura o membro por valor
            if len(args) == 1:
                for membro in callee.members.values():
                    if membro.value == args[0] or membro.name == args[0]:
                        return membro
                raise RuntimeError_(
                    f"Enum '{callee.name}' has no member with value {args[0]!r}",
                    node.line, node.column)
            raise TypeError_(
                f"Calling enum '{callee.name}' takes exactly 1 value",
                node.line, node.column)

        if isinstance(callee, DFBlueprint):
            # Calling a blueprint = spawn
            instance = DFInstance(callee)
            if callee.constructor_params:
                # Inline constructor — assign params to fields + run body
                for i, pname in enumerate(callee.constructor_params):
                    val = args[i] if i < len(args) else None
                    instance.set(pname, val)
                if 'setup' in callee.methods:
                    self._call_action(callee.methods['setup'], args, kwargs, node, env,
                                      instance=instance)
                if callee.constructor_body:
                    ctor_env = env.child(f"<constructor {callee.name}>")
                    ctor_env.set_local("self", instance)
                    ctor_env.set_local("this", instance)
                    for i, pname in enumerate(callee.constructor_params):
                        ctor_env.set_local(pname, instance.fields.get(pname))
                    for stmt in callee.constructor_body:
                        self.execute(stmt, ctor_env)
            elif 'setup' in callee.methods:
                self._call_action(callee.methods['setup'], args, kwargs, node, env, instance=instance)
            elif 'initiate' in callee.methods:
                self._call_action(callee.methods['initiate'], args, kwargs, node, env, instance=instance)
            return instance

        if callable(callee):
            try:
                return callee(*args, **kwargs)
            except Exception as e:
                raise RuntimeError_(str(e), node.line, node.column)

        raise TypeError_(f"'{callee}' is not callable", node.line, node.column)

    MAX_CALL_DEPTH = 1000

    def _call_action(self, action: DFAction, args, kwargs, node, env, instance=None):
        """Call a user-defined action (function)."""
        self._check_arity(action, args, kwargs, node)

        if getattr(action, 'is_generator', False):
            return self._make_stream(action, args, kwargs, node, instance)

        call_env = action.closure.child(f"<action {action.name}>")

        # Bind parameters
        params = action.params
        for i, param in enumerate(params):
            if i < len(args):
                value = args[i]
            elif param in kwargs:
                value = kwargs[param]
            elif param in action.defaults:
                value = self.evaluate(action.defaults[param], call_env)
            else:
                value = None
            declared = action.param_types.get(param)
            if declared:
                self._check_type(
                    value, declared,
                    f"parameter '{param}' of action '{action.name}'", node)
            call_env.set_local(param, value)

        # Bind 'self' and 'this' for instance methods
        if instance is not None:
            call_env.set_local("self", instance)
            call_env.set_local("this", instance)

        # Execute body, guarding against runaway recursion
        self._depth += 1
        if self._depth > self.MAX_CALL_DEPTH:
            self._depth -= 1
            raise StackOverflowError_(
                f"Call stack exceeded {self.MAX_CALL_DEPTH} frames "
                f"(infinite recursion in '{action.name}'?)", node.line, node.column)
        self._call_stack.append(Frame(
            action.name, getattr(node, 'line', 0), getattr(node, 'column', 0),
            self.filename))
        try:
            self.exec_block(action.body, call_env)
            result = None
        except YieldSignal as ys:
            result = ys.value
        except RecursionError:
            raise StackOverflowError_(
                f"Python recursion limit reached while running '{action.name}'",
                node.line, node.column)
        except DataForgeError as erro:
            self._attach_stack(erro)
            raise
        finally:
            self._depth -= 1
            self._call_stack.pop()
            # Deferred blocks run on every exit path, including an error —
            # that is the whole point of 'defer'.
            self._run_deferred(call_env)
        if action.return_type:
            self._check_type(
                result, action.return_type,
                f"return value of action '{action.name}'", node)
        return result

    def _make_stream(self, action, args, kwargs, node, instance):
        """Um 'stream action' devolve um DFStream verdadeiramente preguiçoso."""
        interpretador = self

        def produzir():
            call_env = action.closure.child(f"<stream {action.name}>")
            for indice, param in enumerate(action.params):
                if indice < len(args):
                    valor = args[indice]
                elif param in kwargs:
                    valor = kwargs[param]
                elif param in action.defaults:
                    valor = interpretador.evaluate(action.defaults[param], call_env)
                else:
                    valor = None
                call_env.set_local(param, valor)
            if instance is not None:
                call_env.set_local("self", instance)
                call_env.set_local("this", instance)

            try:
                yield from interpretador._lazy_block(action.body, call_env)
            except YieldSignal:
                pass
            finally:
                interpretador._run_deferred(call_env)

        return DFStream(action.name, produzir)

    # ── Executor preguiçoso de generators ──────────────────
    #
    # 'emit' precisa entregar cada valor no instante em que é produzido, mesmo
    # dentro de um laço infinito. Por isso o corpo de um 'stream action' é
    # percorrido por este executor paralelo, que é um gerador Python: ele desce
    # nas estruturas onde 'emit' pode aparecer e delega o resto ao execute()
    # normal. 'emit' fora dessas estruturas (dentro de outra ação, por exemplo)
    # não é preguiçoso — precisa aparecer no corpo do próprio stream.

    def _lazy_block(self, statements, env):
        for stmt in statements:
            yield from self._lazy_stmt(stmt, env)

    def _lazy_stmt(self, node, env):
        if isinstance(node, ast.EmitStatement):
            valores = [self.evaluate(e, env) for e in node.expressions]
            yield valores[0] if len(valores) == 1 else valores
            return

        if isinstance(node, ast.GivenBlock):
            if self.evaluate(node.condition, env):
                yield from self._lazy_block(node.body, env.child("<given>"))
                return
            for cond, corpo in node.orif_blocks:
                if self.evaluate(cond, env):
                    yield from self._lazy_block(corpo, env.child("<orif>"))
                    return
            if node.otherwise_body:
                yield from self._lazy_block(node.otherwise_body, env.child("<otherwise>"))
            return

        if isinstance(node, ast.CycleFromTo):
            inicio = self.evaluate(node.start, env)
            fim = self.evaluate(node.end, env)
            passo = self.evaluate(node.step, env) if node.step else 1
            i = inicio
            while (passo > 0 and i <= fim) or (passo < 0 and i >= fim):
                escopo = env.child("<cycle>")
                escopo.set_local(node.var, i)
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    pass
                i += passo
            return

        if isinstance(node, ast.ObserveBlock):
            fonte = self.evaluate(node.source, env)
            if isinstance(fonte, dict) and fonte.get("__type__") == "Stream":
                fonte = fonte.get("data", [])
            elif isinstance(fonte, dict):
                fonte = list(fonte.keys())
            for item in fonte:
                escopo = env.child("<observe>")
                escopo.set_local(node.var, item)
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    continue
            return

        if isinstance(node, ast.CycleIn):
            colecao = self.evaluate(node.collection, env)
            if isinstance(colecao, DFStream):
                colecao = iter(colecao)
            elif not hasattr(colecao, '__iter__'):
                raise TypeError_(
                    f"Cannot cycle over {self._type_of(colecao)}",
                    node.line, node.column)
            for item in colecao:
                escopo = env.child("<cycle>")
                escopo.set_local(node.var, item)
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    continue
            return

        if isinstance(node, ast.PersistBlock):
            while self.evaluate(node.condition, env):
                escopo = env.child("<persist>")
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    continue
            return

        if isinstance(node, ast.PerformBlock):
            while True:
                escopo = env.child("<perform>")
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    pass
                if not self.evaluate(node.condition, env):
                    return

        if isinstance(node, ast.MatchBlock):
            valor = self.evaluate(node.expression, env)
            for caso in node.points:
                if isinstance(caso, tuple):
                    alvo, corpo = caso
                    if valor == self.evaluate(alvo, env):
                        yield from self._lazy_block(corpo, env.child("<point>"))
                        return
                    continue
                ligacoes = {}
                if not self._match_pattern(caso.pattern, valor, env, ligacoes):
                    continue
                escopo = env.child("<point>")
                for nome, ligado in ligacoes.items():
                    escopo.set_local(nome, ligado)
                if caso.guard is not None and not self.evaluate(caso.guard, escopo):
                    continue
                yield from self._lazy_block(caso.body, escopo)
                return
            if node.default_body:
                yield from self._lazy_block(node.default_body, env.child("<default>"))
            return

        if isinstance(node, ast.MonitorBlock):
            try:
                yield from self._lazy_block(node.body, env.child("<monitor>"))
            except Exception as e:
                if not node.handle_body or not self._error_matches(e, node.handle_type, env):
                    raise
                escopo = env.child("<handle>")
                escopo.set_local(node.handle_name, self._error_value(e))
                yield from self._lazy_block(node.handle_body, escopo)
            finally:
                if node.ensure_body:
                    self.exec_block(node.ensure_body, env.child("<ensure>"))
            return

        # Qualquer outra instrução roda normalmente (não produz valores).
        self.execute(node, env)

    def _attach_stack(self, erro):
        """Guarda a pilha no erro, uma única vez (a mais interna vence)."""
        if not getattr(erro, 'stack', None):
            erro.stack = list(self._call_stack)
        if not getattr(erro, 'filename', ''):
            erro.filename = self.filename
        return erro

    def _run_deferred(self, env):
        """Run all deferred blocks registered in the environment, in LIFO order."""
        if hasattr(env, '_deferred') and env._deferred:
            for body, defer_env in reversed(env._deferred):
                try:
                    self.exec_block(body, defer_env.child("<defer>"))
                except Exception:
                    pass  # Deferred blocks should not propagate errors
            env._deferred.clear()

    def _eval_lambda(self, param_name, body_expr, value, env):
        """Evaluate a lambda-like expression for pipelines."""
        local = env.child("<lambda>")
        local.set_local(param_name, value)
        return self.evaluate(body_expr, local)

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — EXPRESSÕES NOVAS
    # ═══════════════════════════════════════════════════════

    def eval_InterpolatedString(self, node, env):
        partes = []
        for tipo, conteudo in node.parts:
            if tipo == 'text':
                partes.append(conteudo)
            else:
                partes.append(self._to_str(self.evaluate(conteudo, env)))
        return ''.join(partes)

    def eval_TernaryExpression(self, node, env):
        if self.evaluate(node.condition, env):
            return self.evaluate(node.then_value, env)
        return self.evaluate(node.else_value, env)

    def eval_CoalesceOp(self, node, env):
        esquerda = self.evaluate(node.left, env)
        if esquerda is None:
            return self.evaluate(node.right, env)
        return esquerda

    def eval_MembershipOp(self, node, env):
        elemento = self.evaluate(node.element, env)
        recipiente = self.evaluate(node.container, env)
        if recipiente is None:
            raise TypeError_(
                "Cannot test membership in void", node.line, node.column)
        try:
            if isinstance(recipiente, DFRecordInstance):
                presente = elemento in recipiente.values
            elif isinstance(recipiente, DFEnum):
                presente = any(m == elemento or m.value == elemento
                               for m in recipiente.members.values())
            elif isinstance(recipiente, DFStream):
                presente = any(item == elemento for item in recipiente)
            else:
                presente = elemento in recipiente
        except TypeError:
            raise TypeError_(
                f"Cannot test membership in {self._type_of(recipiente)}",
                node.line, node.column)
        return (not presente) if node.negated else presente

    def eval_SafeMemberAccess(self, node, env):
        obj = self.evaluate(node.object, env)
        if obj is None:
            return None
        return self.eval_MemberAccess(
            ast.MemberAccess(object=ast._Wrapped(value=obj), member=node.member,
                             line=node.line, column=node.column), env)

    def eval_SafeMethodCall(self, node, env):
        obj = self.evaluate(node.object, env)
        if obj is None:
            return None
        return self.eval_MethodCall(
            ast.MethodCall(object=ast._Wrapped(value=obj), method=node.method,
                           args=node.args, kwargs=node.kwargs,
                           line=node.line, column=node.column), env)

    def eval__Wrapped(self, node, env):
        """Nó interno que carrega um valor já avaliado."""
        return node.value

    def eval_SpreadElement(self, node, env):
        # Um spread solto (fora de literal/chamada) não faz sentido.
        raise RuntimeError_(
            "'...' can only be used inside a list, a vault or a call",
            node.line, node.column)

    def _eval_args(self, nodes, env):
        """Avalia argumentos de chamada, expandindo '...expr'."""
        if any(isinstance(a, ast.SpreadElement) for a in nodes):
            return self._expand_elements(nodes, env)
        return [self.evaluate(a, env) for a in nodes]

    def _expand_elements(self, elementos, env):
        """Avalia elementos de literal expandindo os '...expr'."""
        saida = []
        for elemento in elementos:
            if isinstance(elemento, ast.SpreadElement):
                valor = self.evaluate(elemento.value, env)
                if isinstance(valor, DFStream):
                    valor = list(valor)
                if isinstance(valor, dict):
                    saida.extend(valor.keys())
                elif hasattr(valor, '__iter__') and not isinstance(valor, str):
                    saida.extend(valor)
                elif isinstance(valor, str):
                    saida.extend(valor)
                else:
                    raise TypeError_(
                        f"Cannot spread {self._type_of(valor)}: "
                        f"'...' needs a Cluster, Vault or String",
                        elemento.line, elemento.column)
            else:
                saida.append(self.evaluate(elemento, env))
        return saida

    def _run_clauses(self, clauses, indice, env, emitir):
        """Executa as cláusulas de uma comprehension, recursivamente."""
        clause = clauses[indice]
        fonte = self.evaluate(clause.source, env)
        if isinstance(fonte, DFStream):
            fonte = list(fonte)
        if isinstance(fonte, dict):
            fonte = list(fonte.keys())
        if not hasattr(fonte, '__iter__'):
            raise TypeError_(
                f"Cannot iterate over {self._type_of(fonte)} in the comprehension",
                clause.line, clause.column)

        for item in fonte:
            local = env.child("<comprehension>")
            alvos = clause.targets or [clause.var]
            if len(alvos) == 1:
                local.set_local(alvos[0], item)
            else:
                valores = list(item) if hasattr(item, '__iter__') and not isinstance(item, str) else [item]
                if len(valores) != len(alvos):
                    raise RuntimeError_(
                        f"Cannot unpack {len(valores)} value(s) into "
                        f"{len(alvos)} name(s) in the comprehension",
                        clause.line, clause.column)
                for nome, valor in zip(alvos, valores):
                    local.set_local(nome, valor)

            if clause.condition is not None and not self.evaluate(clause.condition, local):
                continue
            if indice + 1 < len(clauses):
                self._run_clauses(clauses, indice + 1, local, emitir)
            else:
                emitir(local)

    def eval_ListComprehension(self, node, env):
        saida = []
        self._run_clauses(node.clauses, 0, env,
                          lambda escopo: saida.append(
                              self.evaluate(node.expression, escopo)))
        return saida

    def eval_VaultComprehension(self, node, env):
        saida = {}
        def registrar(escopo):
            saida[self.evaluate(node.key, escopo)] = self.evaluate(node.value, escopo)
        self._run_clauses(node.clauses, 0, env, registrar)
        return saida

    def eval_WithExpression(self, node, env):
        base = self.evaluate(node.source, env)
        mudancas = self.evaluate(node.changes, env)
        if not isinstance(mudancas, dict):
            raise TypeError_("'with' needs a vault of changes: obj with {\"campo\": valor}",
                             node.line, node.column)
        if isinstance(base, DFRecordInstance):
            return base.replace(mudancas)
        if isinstance(base, dict):
            return {**base, **mudancas}
        if isinstance(base, DFInstance):
            copia = DFInstance(base.blueprint)
            copia.fields = dict(base.fields)
            copia.fields.update(mudancas)
            return copia
        raise TypeError_(
            f"'with' does not apply to {self._type_of(base)}: "
            f"use it on a record, a vault or a blueprint instance",
            node.line, node.column)

    # ── Type annotations (checked at runtime) ──────────────

    TYPE_ALIASES = {
        "integer": "Integer", "int": "Integer", "Integer": "Integer",
        "float": "Float", "Float": "Float", "number": "Number", "Number": "Number",
        "string": "String", "str": "String", "String": "String", "text": "String",
        "boolean": "Boolean", "bool": "Boolean", "Boolean": "Boolean",
        "cluster": "Cluster", "list": "Cluster", "Cluster": "Cluster", "array": "Cluster",
        "vault": "Vault", "dict": "Vault", "Vault": "Vault", "map": "Vault",
        "void": "Void", "Void": "Void", "none": "Void",
        "action": "Action", "Action": "Action", "function": "Action",
        "any": "Any", "Any": "Any",
    }

    def _target_name(self, target) -> str:
        if isinstance(target, ast.Identifier):
            return target.name
        return "<expression>"

    def _type_of(self, value) -> str:
        if isinstance(value, bool):
            return "Boolean"
        if isinstance(value, int):
            return "Integer"
        if isinstance(value, float):
            return "Float"
        if isinstance(value, str):
            return "String"
        if isinstance(value, list):
            return "Cluster"
        if isinstance(value, dict):
            return "Vault"
        if value is None:
            return "Void"
        if isinstance(value, DFInstance):
            return value.blueprint.name
        if isinstance(value, DFRecordInstance):
            return value.record.name
        if isinstance(value, DFRecord):
            return "Record"
        if isinstance(value, DFEnumMember):
            return value.enum_name
        if isinstance(value, DFEnum):
            return "Enum"
        if isinstance(value, DFStream):
            return "Stream"
        if isinstance(value, DFBlueprint):
            return "Blueprint"
        if isinstance(value, (DFAction, BuiltinFunction)) or callable(value):
            return "Action"
        return type(value).__name__

    def _check_type(self, value, declared: str, what: str, node):
        """Enforce a declared type annotation. Unknown names name a blueprint."""
        expected = self.TYPE_ALIASES.get(declared, declared)
        if expected == "Any":
            return value
        actual = self._type_of(value)

        if expected == "Number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError_(
                    f"{what} declared as Number but got {actual}", node.line, node.column)
            return value
        if expected == "Float" and isinstance(value, int) and not isinstance(value, bool):
            return value  # an Integer widens to Float
        if expected == actual:
            return value
        if isinstance(value, DFInstance):
            for bp in value.get_mro():
                if bp.name == expected:
                    return value
        raise TypeError_(
            f"{what} declared as {expected} but got {actual}", node.line, node.column)

    def _check_arity(self, action, args, kwargs, node):
        """Reject calls with too few or too many arguments."""
        params = action.params
        required = [p for p in params if p not in action.defaults]
        supplied = set(params[:len(args)]) | set(kwargs)
        missing = [p for p in required if p not in supplied]
        if missing:
            raise TypeError_(
                f"action '{action.name}' is missing argument(s): {', '.join(missing)}",
                node.line, node.column)
        if len(args) > len(params):
            raise TypeError_(
                f"action '{action.name}' takes {len(params)} argument(s) "
                f"but {len(args)} were given",
                node.line, node.column)
        unknown = [k for k in kwargs if k not in params]
        if unknown:
            raise TypeError_(
                f"action '{action.name}' got unexpected argument(s): {', '.join(unknown)}",
                node.line, node.column)

    def _to_str(self, value) -> str:
        """Convert a DataForge value to its string representation."""
        if value is None:
            return "void"
        if isinstance(value, bool):
            return "yes" if value else "no"
        if isinstance(value, DFInstance):
            # Check if instance has a custom toString method
            if value.has_method('toString'):
                method = value.get('toString')
                if isinstance(method, DFAction):
                    return str(self._call_action(method, [], {}, type('_N', (), {'line': 0, 'column': 0})(), None, instance=value))
            return f"<{value.blueprint.name} instance>"
        if isinstance(value, DFBlueprint):
            return f"<blueprint {value.name}>"
        if isinstance(value, DFAction):
            return f"<action {value.name}>"
        if isinstance(value, DFChannel):
            return f"<channel {value.name}>"
        if isinstance(value, DFError):
            return value.message
        if isinstance(value, DFRecordInstance):
            if 'toString' in value.record.methods:
                no = type('_N', (), {'line': 0, 'column': 0})()
                return str(self._call_action(
                    value.record.methods['toString'], [], {}, no, None,
                    instance=value))
            campos = ', '.join(f"{k}: {self._to_str(v)}"
                               for k, v in value.values.items())
            return f"{value.record.name}({campos})"
        if isinstance(value, DFRecord):
            return f"<record {value.name}>"
        if isinstance(value, DFEnumMember):
            return f"{value.enum_name}.{value.name}"
        if isinstance(value, DFEnum):
            return f"<enum {value.name}>"
        if isinstance(value, DFStream):
            return f"<stream {value.name}>"
        if isinstance(value, list):
            items = ', '.join(self._to_str(i) for i in value)
            return f"[{items}]"
        if isinstance(value, dict):
            if "__type__" in value:
                return f"<{value['__type__']}>"
            pairs = ', '.join(f"{self._to_str(k)}: {self._to_str(v)}" for k, v in value.items())
            return '{' + pairs + '}'
        return str(value)

    def _load_module_file(self, path, module_name):
        """Executa um arquivo .df como módulo e devolve o que ele exporta."""
        import os
        from .lexer import tokenize
        from .parser import parse

        real = os.path.abspath(path)
        if real in self._loading:
            cadeia = " → ".join(os.path.basename(p) for p in self._loading)
            raise ImportError_(
                f"Circular import: {cadeia} → {os.path.basename(real)}. "
                f"Break the cycle by moving the shared part into a third module.")

        with open(path, 'r', encoding='utf-8') as f:
            fonte = f.read()

        tokens = tokenize(fonte, path)
        arvore = parse(tokens, path)

        mod_env = self.global_env.child(f"<module {module_name}>")
        arquivo_anterior = self.filename
        self._loading.append(real)
        self.filename = path
        try:
            self.exec_block(arvore.body, mod_env)
        finally:
            self._loading.pop()
            self.filename = arquivo_anterior

        exportados = getattr(mod_env, '_exports', None)
        if exportados:
            objeto = {nome: mod_env.get(nome) for nome in exportados}
        else:
            objeto = dict(mod_env.variables)
        objeto["__name__"] = module_name
        objeto["__file__"] = path
        self.modules[module_name] = objeto
        return objeto
