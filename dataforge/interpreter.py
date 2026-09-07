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
    DataForgeError, RuntimeError_, TypeError_, NameError_, TriggerError,
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
                 param_types=None, return_type=""):
        self.name = name
        self.params = params
        self.defaults = defaults
        self.body = body
        self.closure = closure
        self.is_async = is_async
        self.param_types = param_types or {}
        self.return_type = return_type

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

    def __init__(self, name, parents, methods, statics, env, constructor_params=None, constructor_body=None):
        self.name = name
        self.parents = parents       # list of DFBlueprint
        self.methods = methods       # dict: name → DFAction
        self.statics = statics       # dict: name → value
        self.env = env
        self.constructor_params = constructor_params or []
        self.constructor_body = constructor_body or []

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

    def run(self, program: ast.Program):
        """Execute a full program."""
        return self.exec_block(program.body, self.global_env)

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
        return [self.evaluate(elem, env) for elem in node.elements]

    def eval_DictLiteral(self, node: ast.DictLiteral, env):
        result = {}
        for key_node, val_node in node.pairs:
            key = self.evaluate(key_node, env)
            val = self.evaluate(val_node, env)
            result[key] = val
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

        # ── Operator overloading for blueprint instances ───
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

    def eval_ComparisonOp(self, node: ast.ComparisonOp, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.op

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

        if isinstance(obj, DFInstance):
            # Instance built-in methods
            if node.member == 'blueprint_name':
                return obj.blueprint.name
            if node.member == 'fields':
                return dict(obj.fields)
            if node.member == 'methods':
                return list(obj.blueprint.methods.keys())
            return obj.get(node.member)
        elif isinstance(obj, DFBlueprint):
            if node.member in obj.statics:
                return obj.statics[node.member]
            if node.member in obj.methods:
                return obj.methods[node.member]
            raise NameError_(f"Blueprint '{obj.name}' has no member '{node.member}'")
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
        args = [self.evaluate(arg, env) for arg in node.args]
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}
        return self._call(callee, args, kwargs, node, env)

    def eval_MethodCall(self, node: ast.MethodCall, env):
        obj = self.evaluate(node.object, env)
        args = [self.evaluate(arg, env) for arg in node.args]
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}

        # Handle root (super) proxy calls
        if isinstance(obj, _RootProxy):
            method = obj.get(node.method)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj.instance)
            if callable(method):
                return method(*args, **kwargs)

        if isinstance(obj, DFInstance):
            method = obj.get(node.method)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj)
            if callable(method):
                return method(*args, **kwargs)
        elif isinstance(obj, DFBlueprint):
            if node.method in obj.methods:
                method = obj.methods[node.method]
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
            raise TypeError_(f"Cannot spawn non-blueprint: {blueprint}", node.line, node.column)

        instance = DFInstance(blueprint)
        args = [self.evaluate(arg, env) for arg in node.args]
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
        value = self.evaluate(node.operand, env)
        type_map = {
            int: "Integer",
            float: "Float",
            str: "String",
            bool: "Boolean",
            list: "Cluster",
            dict: "Vault",
            type(None): "Void",
        }
        if isinstance(value, DFInstance):
            return value.blueprint.name
        if isinstance(value, DFBlueprint):
            return "Blueprint"
        if isinstance(value, DFAction):
            return "Action"
        return type_map.get(type(value), type(value).__name__)

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
            if isinstance(obj, DFInstance):
                obj.set(node.target.member, value)
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
        value = self.evaluate(node.expression, env)
        for point_val, point_body in node.points:
            pv = self.evaluate(point_val, env)
            if value == pv:
                return self.exec_block(point_body, env.child("<point>"))

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

        # Execute blueprint body to collect methods and statics
        bp_env = env.child(f"<blueprint {node.name}>")
        methods = {}
        statics = {}
        constructor_body = []

        # Inherit parent methods
        for parent in parents:
            methods.update(parent.methods)
            statics.update(parent.statics)

        # Merge trait methods (with Trait1, Trait2)
        for tname in getattr(node, 'traits', []):
            try:
                trait = env.get(tname)
                if isinstance(trait, DFBlueprint):
                    for mname, mval in trait.methods.items():
                        if mname not in methods:
                            methods[mname] = mval
            except NameError_:
                pass

        for stmt in node.body:
            if isinstance(stmt, ast.ActionDeclaration):
                action = DFAction(
                    name=stmt.name, params=stmt.params,
                    defaults=stmt.defaults, body=stmt.body,
                    closure=bp_env, is_async=stmt.is_async,
                    param_types=getattr(stmt, 'param_types', None),
                    return_type=getattr(stmt, 'return_type', ""),
                )
                methods[stmt.name] = action
            elif isinstance(stmt, ast.StaticDeclaration):
                statics[stmt.name] = self.evaluate(stmt.value, bp_env)
            elif isinstance(stmt, ast.Assignment):
                if node.constructor_params:
                    # If we have constructor params, non-action statements go to constructor body
                    constructor_body.append(stmt)
                elif isinstance(stmt.target, ast.Identifier):
                    statics[stmt.target.name] = self.evaluate(stmt.value, bp_env)
            elif node.constructor_params:
                # Any non-action, non-static statement in a parameterized blueprint
                # is part of the constructor body (e.g., given/otherwise, out, etc.)
                constructor_body.append(stmt)

        blueprint = DFBlueprint(
            name=node.name, parents=parents,
            methods=methods, statics=statics, env=bp_env,
            constructor_params=node.constructor_params,
            constructor_body=constructor_body
        )
        bp_env.set_local(node.name, blueprint)
        env.set_local(node.name, blueprint)
        return blueprint

    def exec_TraitDeclaration(self, node: ast.TraitDeclaration, env):
        """Traits are stored as blueprints with abstract methods."""
        methods = {}
        for stmt in node.methods:
            if isinstance(stmt, ast.ActionDeclaration):
                action = DFAction(
                    name=stmt.name, params=stmt.params,
                    defaults=stmt.defaults, body=stmt.body,
                    closure=env
                )
                methods[stmt.name] = action

        blueprint = DFBlueprint(
            name=node.name, parents=[], methods=methods,
            statics={}, env=env
        )
        env.set_local(node.name, blueprint)
        return blueprint

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
        module_name = node.module
        alias = node.alias or module_name.split('.')[-1]

        # Check if module already loaded
        if module_name in self.modules:
            env.set_local(alias, self.modules[module_name])
            return

        # Try to load from stdlib
        from .stdlib import get_module, list_modules
        module = get_module(module_name)
        if module is not None:
            self.modules[module_name] = module
            env.set_local(alias, module)
            return

        # Try to load .df file
        import os
        parts = module_name.replace('.', os.sep)
        for ext in ['.df', '/main.df']:
            path = parts + ext
            if os.path.exists(path):
                self._load_module_file(path, module_name, env, alias)
                return

        raise ImportError_(
            f"Module '{module_name}' not found. "
            f"Available: {', '.join(sorted(set(list_modules())))}",
            node.line, node.column)

    def exec_RelayStatement(self, node: ast.RelayStatement, env):
        # In the current context, relay marks names for export
        # This is handled at module level
        pass

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
        """Observe: iterate over a source (reactive stream simulation)."""
        source = self.evaluate(node.source, env)
        if not isinstance(source, (list, tuple, dict)):
            raise TypeError_(
                f"Cannot observe a value of type {self._type_of(source)}: "
                f"expected a Cluster or a stream",
                node.line, node.column)
        if isinstance(source, (list, tuple)):
            for item in source:
                obs_env = env.child("<observe>")
                obs_env.set_local(node.var, item)
                try:
                    self.exec_block(node.body, obs_env)
                except HaltSignal:
                    break
                except SkipSignal:
                    continue
        elif isinstance(source, dict) and source.get("__type__") == "Stream":
            data = source.get("data", [])
            for item in data:
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

    def _call(self, callee, args, kwargs, node, env):
        """Call a callable value."""
        if isinstance(callee, BuiltinFunction):
            try:
                return callee(*args, **kwargs)
            except Exception as e:
                raise RuntimeError_(str(e), node.line, node.column)

        if isinstance(callee, DFAction):
            return self._call_action(callee, args, kwargs, node, env)

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
        try:
            self.exec_block(action.body, call_env)
            result = None
        except YieldSignal as ys:
            result = ys.value
        except RecursionError:
            raise StackOverflowError_(
                f"Python recursion limit reached while running '{action.name}'",
                node.line, node.column)
        finally:
            self._depth -= 1
            # Deferred blocks run on every exit path, including an error —
            # that is the whole point of 'defer'.
            self._run_deferred(call_env)
        if action.return_type:
            self._check_type(
                result, action.return_type,
                f"return value of action '{action.name}'", node)
        return result

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
        if isinstance(value, list):
            items = ', '.join(self._to_str(i) for i in value)
            return f"[{items}]"
        if isinstance(value, dict):
            if "__type__" in value:
                return f"<{value['__type__']}>"
            pairs = ', '.join(f"{self._to_str(k)}: {self._to_str(v)}" for k, v in value.items())
            return '{' + pairs + '}'
        return str(value)

    def _load_module_file(self, path, module_name, env, alias):
        """Load and execute a .df file as a module."""
        from .lexer import tokenize
        from .parser import parse

        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()

        tokens = tokenize(source, path)
        tree = parse(tokens, path)

        mod_env = self.global_env.child(f"<module {module_name}>")
        self.exec_block(tree.body, mod_env)

        module_obj = dict(mod_env.variables)
        module_obj["__name__"] = module_name
        self.modules[module_name] = module_obj
        env.set_local(alias, module_obj)
