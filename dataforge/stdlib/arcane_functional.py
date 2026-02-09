"""
Arcane.Functional - Functional Programming Module
Advanced FP tools: monads, functors, lenses, transducers, pattern matching.
"""

import functools
import itertools
import copy


class ArcaneFunctional:
    """Advanced functional programming tools for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Functional",

            # Core FP
            "compose": cls._compose,
            "pipe": cls._pipe,
            "partial": cls._partial,
            "curry": cls._curry,
            "memoize": cls._memoize,
            "once": cls._once,
            "identity": cls._identity,
            "constantly": cls._constantly,
            "complement": cls._complement,
            "juxt": cls._juxt,
            "flip": cls._flip,
            "spread": cls._spread,

            # Collections
            "map": cls._map,
            "filter": cls._filter,
            "reduce": cls._reduce,
            "flat_map": cls._flat_map,
            "scan": cls._scan,
            "zip_with": cls._zip_with,
            "group_by": cls._group_by,
            "sort_by": cls._sort_by,
            "unique_by": cls._unique_by,
            "partition_by": cls._partition_by,
            "take_while": cls._take_while,
            "drop_while": cls._drop_while,
            "chunk": cls._chunk,
            "interleave": cls._interleave,
            "frequencies": cls._frequencies,
            "index_by": cls._index_by,

            # Maybe monad
            "maybe": cls._maybe,
            "just": cls._just,
            "nothing": cls._nothing,
            "is_just": cls._is_just,
            "is_nothing": cls._is_nothing,
            "from_maybe": cls._from_maybe,

            # Either monad
            "left": cls._left,
            "right": cls._right,
            "is_left": cls._is_left,
            "is_right": cls._is_right,
            "from_either": cls._from_either,
            "try_catch": cls._try_catch,

            # Lenses
            "lens": cls._lens,
            "view": cls._view,
            "set_lens": cls._set_lens,
            "over": cls._over,

            # Pattern matching
            "match": cls._match,
            "when": cls._when,

            # Transducers / pipelines
            "transduce": cls._transduce,
            "into": cls._into,

            # Predicates
            "all_pass": cls._all_pass,
            "any_pass": cls._any_pass,
            "both": cls._both,
            "either": cls._either,

            # Utilities
            "tap": cls._tap,
            "thread_first": cls._thread_first,
            "thread_last": cls._thread_last,
            "trampoline": cls._trampoline,
        }

    # ── Core FP ──────────────────────────────────────────

    @staticmethod
    def _compose(*fns):
        """Compose functions right-to-left."""
        def composed(x):
            result = x
            for fn in reversed(fns):
                result = fn(result)
            return result
        return composed

    @staticmethod
    def _pipe(*fns):
        """Compose functions left-to-right."""
        def piped(x):
            result = x
            for fn in fns:
                result = fn(result)
            return result
        return piped

    @staticmethod
    def _partial(fn, *args):
        """Partially apply a function."""
        def partial_fn(*rest):
            return fn(*args, *rest)
        return partial_fn

    @staticmethod
    def _curry(fn, arity=None):
        """Curry a function."""
        if arity is None:
            import inspect
            try:
                arity = len(inspect.signature(fn).parameters)
            except (ValueError, TypeError):
                arity = 2

        def curried(*args):
            if len(args) >= arity:
                return fn(*args[:arity])
            def inner(*more):
                return curried(*args, *more)
            return inner
        return curried

    @staticmethod
    def _memoize(fn):
        """Memoize a function."""
        cache = {}
        def memoized(*args):
            key = str(args)
            if key not in cache:
                cache[key] = fn(*args)
            return cache[key]
        memoized.cache = cache
        memoized.clear = lambda: cache.clear()
        return memoized

    @staticmethod
    def _once(fn):
        """Create function that runs only once."""
        result = [None]
        called = [False]
        def once_fn(*args):
            if not called[0]:
                result[0] = fn(*args)
                called[0] = True
            return result[0]
        return once_fn

    @staticmethod
    def _identity(x):
        return x

    @staticmethod
    def _constantly(x):
        def const_fn(*args):
            return x
        return const_fn

    @staticmethod
    def _complement(fn):
        def comp(*args):
            return not fn(*args)
        return comp

    @staticmethod
    def _juxt(*fns):
        """Apply multiple functions to the same arguments."""
        def juxted(*args):
            return [fn(*args) for fn in fns]
        return juxted

    @staticmethod
    def _flip(fn):
        """Flip first two arguments of a function."""
        def flipped(a, b, *rest):
            return fn(b, a, *rest)
        return flipped

    @staticmethod
    def _spread(fn):
        """Turn fn(list) into fn(a, b, c)."""
        def spread_fn(lst):
            return fn(*lst)
        return spread_fn

    # ── Collections ──────────────────────────────────────

    @staticmethod
    def _map(fn, collection):
        return [fn(item) for item in collection]

    @staticmethod
    def _filter(fn, collection):
        return [item for item in collection if fn(item)]

    @staticmethod
    def _reduce(fn, collection, initial=None):
        if initial is not None:
            return functools.reduce(fn, collection, initial)
        return functools.reduce(fn, collection)

    @staticmethod
    def _flat_map(fn, collection):
        result = []
        for item in collection:
            r = fn(item)
            if isinstance(r, list):
                result.extend(r)
            else:
                result.append(r)
        return result

    @staticmethod
    def _scan(fn, collection, initial):
        result = [initial]
        acc = initial
        for item in collection:
            acc = fn(acc, item)
            result.append(acc)
        return result

    @staticmethod
    def _zip_with(fn, *collections):
        return [fn(*items) for items in zip(*collections)]

    @staticmethod
    def _group_by(fn, collection):
        result = {}
        for item in collection:
            key = fn(item)
            key = str(key)
            if key not in result:
                result[key] = []
            result[key].append(item)
        return result

    @staticmethod
    def _sort_by(fn, collection):
        return sorted(collection, key=fn)

    @staticmethod
    def _unique_by(fn, collection):
        seen = set()
        result = []
        for item in collection:
            key = str(fn(item))
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    @staticmethod
    def _partition_by(fn, collection):
        yes, no = [], []
        for item in collection:
            if fn(item):
                yes.append(item)
            else:
                no.append(item)
        return [yes, no]

    @staticmethod
    def _take_while(fn, collection):
        result = []
        for item in collection:
            if fn(item):
                result.append(item)
            else:
                break
        return result

    @staticmethod
    def _drop_while(fn, collection):
        result = []
        dropping = True
        for item in collection:
            if dropping and fn(item):
                continue
            dropping = False
            result.append(item)
        return result

    @staticmethod
    def _chunk(n, collection):
        return [collection[i:i+n] for i in range(0, len(collection), n)]

    @staticmethod
    def _interleave(*collections):
        result = []
        for items in itertools.zip_longest(*collections):
            for item in items:
                if item is not None:
                    result.append(item)
        return result

    @staticmethod
    def _frequencies(collection):
        freq = {}
        for item in collection:
            key = str(item)
            freq[key] = freq.get(key, 0) + 1
        return freq

    @staticmethod
    def _index_by(fn, collection):
        result = {}
        for item in collection:
            key = str(fn(item))
            result[key] = item
        return result

    # ── Maybe Monad ──────────────────────────────────────

    @staticmethod
    def _maybe(value):
        if value is None:
            return {"__type__": "Maybe", "tag": "Nothing", "value": None}
        return {"__type__": "Maybe", "tag": "Just", "value": value}

    @staticmethod
    def _just(value):
        return {"__type__": "Maybe", "tag": "Just", "value": value}

    @staticmethod
    def _nothing():
        return {"__type__": "Maybe", "tag": "Nothing", "value": None}

    @staticmethod
    def _is_just(m):
        return isinstance(m, dict) and m.get("tag") == "Just"

    @staticmethod
    def _is_nothing(m):
        return isinstance(m, dict) and m.get("tag") == "Nothing"

    @staticmethod
    def _from_maybe(default, m):
        if isinstance(m, dict) and m.get("tag") == "Just":
            return m["value"]
        return default

    # ── Either Monad ─────────────────────────────────────

    @staticmethod
    def _left(value):
        return {"__type__": "Either", "tag": "Left", "value": value}

    @staticmethod
    def _right(value):
        return {"__type__": "Either", "tag": "Right", "value": value}

    @staticmethod
    def _is_left(e):
        return isinstance(e, dict) and e.get("tag") == "Left"

    @staticmethod
    def _is_right(e):
        return isinstance(e, dict) and e.get("tag") == "Right"

    @staticmethod
    def _from_either(left_fn, right_fn, e):
        if isinstance(e, dict) and e.get("tag") == "Right":
            return right_fn(e["value"])
        return left_fn(e.get("value"))

    @staticmethod
    def _try_catch(fn):
        """Wrap a function to return Either."""
        try:
            result = fn()
            return {"__type__": "Either", "tag": "Right", "value": result}
        except Exception as e:
            return {"__type__": "Either", "tag": "Left", "value": str(e)}

    # ── Lenses ───────────────────────────────────────────

    @staticmethod
    def _lens(*keys):
        """Create a lens for nested object access."""
        return {"__type__": "Lens", "path": list(keys)}

    @staticmethod
    def _view(lens, obj):
        """View value through a lens."""
        result = obj
        for key in lens.get("path", []):
            if isinstance(result, dict):
                result = result.get(key)
            elif isinstance(result, list) and isinstance(key, int):
                result = result[key] if 0 <= key < len(result) else None
            else:
                return None
        return result

    @staticmethod
    def _set_lens(lens, value, obj):
        """Set value through a lens (returns new object)."""
        result = copy.deepcopy(obj)
        target = result
        path = lens.get("path", [])
        for key in path[:-1]:
            if isinstance(target, dict):
                target = target.get(key, {})
            elif isinstance(target, list):
                target = target[key]
        if path:
            last = path[-1]
            if isinstance(target, dict):
                target[last] = value
            elif isinstance(target, list) and isinstance(last, int):
                target[last] = value
        return result

    @staticmethod
    def _over(lens, fn, obj):
        """Apply function to value at lens."""
        current = ArcaneFunctional._view(lens, obj)
        new_val = fn(current)
        return ArcaneFunctional._set_lens(lens, new_val, obj)

    # ── Pattern Matching ─────────────────────────────────

    @staticmethod
    def _match(value, *cases):
        """Pattern match on value. Cases are [pattern, result] pairs."""
        for case in cases:
            if isinstance(case, (list, tuple)) and len(case) >= 2:
                pattern, result = case[0], case[1]
                if pattern == "_" or pattern == value:
                    return result(value) if callable(result) else result
                if callable(pattern) and pattern(value):
                    return result(value) if callable(result) else result
        return None

    @staticmethod
    def _when(*conditions):
        """Multi-condition branching. Pairs of [predicate, result]."""
        for cond in conditions:
            if isinstance(cond, (list, tuple)) and len(cond) >= 2:
                pred, result = cond[0], cond[1]
                if pred is True or (callable(pred) and pred()):
                    return result() if callable(result) else result
        return None

    # ── Transducers ──────────────────────────────────────

    @staticmethod
    def _transduce(xform, reducer, initial, collection):
        """Apply transducer to collection."""
        transformed = xform(collection)
        return functools.reduce(reducer, transformed, initial)

    @staticmethod
    def _into(target_type, xform, collection):
        """Transform and collect into target type."""
        result = xform(collection)
        if target_type == "list":
            return list(result)
        elif target_type == "string":
            return "".join(str(x) for x in result)
        elif target_type == "set":
            return list(set(result))
        return list(result)

    # ── Predicates ───────────────────────────────────────

    @staticmethod
    def _all_pass(*preds):
        """Create predicate that passes when all predicates pass."""
        def check(x):
            return all(p(x) for p in preds)
        return check

    @staticmethod
    def _any_pass(*preds):
        """Create predicate that passes when any predicate passes."""
        def check(x):
            return any(p(x) for p in preds)
        return check

    @staticmethod
    def _both(f, g):
        def check(x):
            return f(x) and g(x)
        return check

    @staticmethod
    def _either(f, g):
        def check(x):
            return f(x) or g(x)
        return check

    # ── Utilities ────────────────────────────────────────

    @staticmethod
    def _tap(fn, value):
        """Execute side-effect function and return value."""
        fn(value)
        return value

    @staticmethod
    def _thread_first(value, *fns):
        """Thread value as first argument through functions."""
        result = value
        for fn in fns:
            if isinstance(fn, (list, tuple)):
                f, *args = fn
                result = f(result, *args)
            else:
                result = fn(result)
        return result

    @staticmethod
    def _thread_last(value, *fns):
        """Thread value as last argument through functions."""
        result = value
        for fn in fns:
            if isinstance(fn, (list, tuple)):
                f, *args = fn
                result = f(*args, result)
            else:
                result = fn(result)
        return result

    @staticmethod
    def _trampoline(fn, *args):
        """Trampoline for tail-call optimization."""
        result = fn(*args)
        while callable(result):
            result = result()
        return result
