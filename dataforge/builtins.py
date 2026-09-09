"""
DataForge Built-in Functions v3.0
Native functions available in every DataForge program.
Comprehensive string, math, collection, functional, regex, and utility functions.
"""

import time
import math
import random
import re
import hashlib
import json
import itertools
import functools
import os


class BuiltinFunction:
    """Wraps a Python callable as a DataForge built-in."""

    def __init__(self, name: str, func, arity: int = -1):
        self.name = name
        self.func = func
        self.arity = arity  # -1 = variadic

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return f"<builtin action '{self.name}'>"


# ═══════════════════════════════════════════════════════════
#  TYPE & CONVERSION
# ═══════════════════════════════════════════════════════════

#: O interpretador se registra aqui para os embutidos poderem chamar
#: metodos magicos. Uma lista de um item, e nao uma variavel global,
#: porque o modulo e importado antes de o interpretador existir.
_MAGICO = [None]


def set_magic_dispatcher(fn):
    """O interpretador instala aqui o chamador de metodo magico."""
    _MAGICO[0] = fn


def _magico(obj, nome, *args):
    """Chama o metodo magico, ou devolve None se nao houver."""
    if _MAGICO[0] is None:
        return None
    return _MAGICO[0](obj, nome, args)


def _df_len(obj):
    """len(x) — honra '__len__' quando o objeto o declara."""
    resultado = _magico(obj, "__len__")
    if resultado is not None:
        return int(resultado)
    return len(obj)

#: Tipo do Python -> nome que a linguagem usa. 'bool' vem antes de
#: 'int' na busca porque em Python todo booleano E um inteiro.
_NOMES_DE_TIPO = {
    bool: "Boolean",
    int: "Integer",
    float: "Float",
    str: "String",
    list: "Cluster",
    dict: "Vault",
    type(None): "Void",
    tuple: "Frozen",
}


def _df_type(obj):
    """O tipo, no vocabulario do DataForge.

    Uma instancia devolve o nome do blueprint dela, e um record o nome
    do record. Antes vinha 'DFInstance' e 'DFRecordInstance' — nomes de
    classes internas do interpretador, que quem escreve DataForge nunca
    viu e nao pode usar para nada.
    """
    nome = _NOMES_DE_TIPO.get(type(obj))
    if nome is not None:
        return nome

    blueprint = getattr(obj, "blueprint", None)
    if blueprint is not None and getattr(blueprint, "name", None):
        return blueprint.name
    for campo in ("record", "enum"):
        dono = getattr(obj, campo, None)
        if dono is not None and getattr(dono, "name", None):
            return dono.name

    # Um membro de enum e do tipo do ENUM, nao do proprio nome:
    # 'Status.Ativo' e um Status, como '3' e um Integer.
    do_enum = getattr(obj, "enum_name", None)
    if do_enum:
        return do_enum

    interno = type(obj).__name__
    conhecidos = {
        "DFAction": "Action",
        "BuiltinFunction": "Action",
        "DFStream": "Stream",
        "DFError": "Error",
    }
    if interno in conhecidos:
        return conhecidos[interno]

    # Um blueprint, record ou trait usado como VALOR e o proprio tipo.
    proprio = getattr(obj, "name", None)
    if proprio and interno.startswith("DF"):
        return proprio
    return interno


def _df_linhagem(obj):
    """Os blueprints de que este objeto descende, do proprio ate a raiz.

    E o que permite perguntar 'isto e um Cachorro?' sem comparar o nome
    exato — um herdeiro de Cachorro tambem responde que sim:

        given "Animal" in linhagem(bicho):
            out bicho.nome
    """
    blueprint = getattr(obj, "blueprint", None)
    if blueprint is None:
        blueprint = obj if getattr(obj, "linhagem", None) else None
    if blueprint is None or not hasattr(blueprint, "linhagem"):
        return [_df_type(obj)]
    return [bp.name for bp in blueprint.linhagem()]


def _df_e_um(obj, nome):
    """O objeto e daquele tipo, ou descende dele?"""
    alvo = nome if isinstance(nome, str) else getattr(nome, "name", str(nome))
    return alvo == _df_type(obj) or alvo in _df_linhagem(obj)

def _df_str(obj):
    if obj is None:
        return "void"
    if isinstance(obj, bool):
        return "yes" if obj else "no"
    # Delegate to the interpreter so blueprint instances honour toString() and
    # clusters/vaults print with DataForge spelling — same as 'out'.
    formatter = _STRINGIFY[0]
    if formatter is not None:
        return formatter(obj)
    return str(obj)


# Set by Interpreter.__init__ so str() and out agree on formatting.
_STRINGIFY = [None]


def set_stringifier(fn):
    _STRINGIFY[0] = fn

def _df_int(obj):
    return int(obj)

def _df_float(obj):
    return float(obj)

def _df_bool(obj):
    return bool(obj)

def _df_cluster(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__') and not isinstance(args[0], str):
        return list(args[0])
    return list(args)

def _df_vault(*args):
    if len(args) == 1 and isinstance(args[0], dict):
        return dict(args[0])
    return {}

def _df_range(*args):
    return list(range(*args))

# ═══════════════════════════════════════════════════════════
#  STRING FUNCTIONS (50+ methods)
# ═══════════════════════════════════════════════════════════

def _df_join(separator, iterable):
    return separator.join(str(x) for x in iterable)

def _df_split(string, separator=" "):
    return string.split(separator)

def _df_strip(string, chars=None):
    return string.strip(chars)

def _df_lstrip(string, chars=None):
    return string.lstrip(chars)

def _df_rstrip(string, chars=None):
    return string.rstrip(chars)

def _df_upper(string):
    return string.upper()

def _df_lower(string):
    return string.lower()

def _df_title(string):
    return string.title()

def _df_capitalize(string):
    return string.capitalize()

def _df_swapcase(string):
    return string.swapcase()

def _df_center(string, width, fill=" "):
    return string.center(width, fill)

def _df_ljust(string, width, fill=" "):
    return string.ljust(width, fill)

def _df_rjust(string, width, fill=" "):
    return string.rjust(width, fill)

def _df_zfill(string, width):
    return string.zfill(width)

def _df_replace(string, old, new, count=-1):
    if count == -1:
        return string.replace(old, new)
    return string.replace(old, new, count)

def _df_startswith(string, prefix):
    return string.startswith(prefix)

def _df_endswith(string, suffix):
    return string.endswith(suffix)

def _df_find(string, sub, start=0, end=None):
    if end is None:
        return string.find(sub, start)
    return string.find(sub, start, end)

def _df_rfind(string, sub, start=0, end=None):
    if end is None:
        return string.rfind(sub, start)
    return string.rfind(sub, start, end)

def _df_index_of(string, sub, start=0):
    return string.find(sub, start)

def _df_last_index_of(string, sub):
    return string.rfind(sub)

def _df_char_at(string, index):
    if 0 <= index < len(string):
        return string[index]
    return ""

def _df_substring(string, start, end=None):
    if end is None:
        return string[start:]
    return string[start:end]

def _df_isalpha(string):
    return string.isalpha()

def _df_isdigit(string):
    return string.isdigit()

def _df_isalnum(string):
    return string.isalnum()

def _df_isspace(string):
    return string.isspace()

def _df_isupper(string):
    return string.isupper()

def _df_islower(string):
    return string.islower()

def _df_istitle(string):
    return string.istitle()

def _df_isnumeric(string):
    return string.isnumeric()

def _df_isascii(string):
    return all(ord(c) < 128 for c in string)

def _df_repeat(string, n):
    return string * n

def _df_reverse_str(string):
    return string[::-1]

def _df_trim(string):
    return string.strip()

def _df_pad_start(string, length, fill=" "):
    return string.rjust(length, fill)

def _df_pad_end(string, length, fill=" "):
    return string.ljust(length, fill)

def _df_includes(string, sub):
    return sub in string

def _df_concat(*args):
    return "".join(str(a) for a in args)

def _df_char(code):
    return chr(code)

def _df_ord_fn(char):
    return ord(char)

def _df_encode(string, encoding="utf-8"):
    return list(string.encode(encoding))

def _df_decode(bytes_list, encoding="utf-8"):
    return bytes(bytes_list).decode(encoding)

def _df_format(template, *args, **kwargs):
    return template.format(*args, **kwargs)

def _df_count_str(string, sub):
    return string.count(sub)

def _df_expandtabs(string, tabsize=8):
    return string.expandtabs(tabsize)

def _df_partition(string, sep):
    return list(string.partition(sep))

def _df_rpartition(string, sep):
    return list(string.rpartition(sep))

def _df_splitlines(string, keepends=False):
    return string.splitlines(keepends)

def _df_removeprefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

def _df_removesuffix(string, suffix):
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    return string

def _df_words(string):
    return string.split()

def _df_lines(string):
    return string.splitlines()

def _df_template(string, data):
    result = string
    if isinstance(data, dict):
        for key, val in data.items():
            result = result.replace("{" + str(key) + "}", str(val))
    return result

# ═══════════════════════════════════════════════════════════
#  REGEX FUNCTIONS
# ═══════════════════════════════════════════════════════════

def _df_regex_match(pattern, string, flags=0):
    m = re.match(pattern, string, flags)
    if m:
        return {"matched": True, "groups": list(m.groups()), "span": list(m.span()), "value": m.group()}
    return {"matched": False, "groups": [], "span": [], "value": ""}

def _df_regex_search(pattern, string, flags=0):
    m = re.search(pattern, string, flags)
    if m:
        return {"matched": True, "groups": list(m.groups()), "span": list(m.span()), "value": m.group()}
    return {"matched": False, "groups": [], "span": [], "value": ""}

def _df_regex_findall(pattern, string, flags=0):
    return re.findall(pattern, string, flags)

def _df_regex_sub(pattern, repl, string, count=0, flags=0):
    return re.sub(pattern, repl, string, count, flags)

def _df_regex_split(pattern, string, maxsplit=0, flags=0):
    return re.split(pattern, string, maxsplit, flags)

def _df_regex_test(pattern, string):
    return bool(re.search(pattern, string))

def _df_regex_count(pattern, string):
    return len(re.findall(pattern, string))

def _df_regex_extract(pattern, string):
    m = re.search(pattern, string)
    if m:
        return list(m.groups()) if m.groups() else [m.group()]
    return []

# ═══════════════════════════════════════════════════════════
#  MATH FUNCTIONS (expanded 40+)
# ═══════════════════════════════════════════════════════════

def _df_abs(x):
    return abs(x)

def _df_min(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return min(args[0])
    return min(args)

def _df_max(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return max(args[0])
    return max(args)

def _df_sum(iterable):
    return sum(iterable)

def _df_sorted(iterable, chave=None, reverse=False):
    """Ordena. O segundo argumento pode ser uma acao que da o criterio.

        sorted([3, 1, 2])                       -> [1, 2, 3]
        sorted(pessoas, lambda p => p["idade"]) -> por idade
        sorted(nums, void, yes)                 -> decrescente

    Sem a chave, ordenar uma lista de vaults falha com uma mensagem do
    Python ("'<' not supported between instances of 'dict'"), que nao
    diz o que fazer. Com ela, o caso comum simplesmente funciona.
    """
    if chave is None:
        return sorted(iterable, reverse=reverse)
    if not callable(chave):
        raise TypeError(
            f"o segundo argumento de 'sorted' deve ser uma acao que "
            f"devolve o criterio, nao {type(chave).__name__}. "
            f'Exemplo: sorted(pessoas, lambda p => p["idade"])')
    return sorted(iterable, key=chave, reverse=reverse)

def _df_reversed(iterable):
    return list(reversed(iterable))

def _df_round(number, digits=0):
    return round(number, digits)

def _df_floor(number):
    return math.floor(number)

def _df_ceil(number):
    return math.ceil(number)

def _df_sqrt(number):
    return math.sqrt(number)

def _df_cbrt(number):
    return number ** (1/3)

def _df_pow(base, exp):
    return math.pow(base, exp)

def _df_log(number, base=math.e):
    return math.log(number, base)

def _df_log2(number):
    return math.log2(number)

def _df_log10(number):
    return math.log10(number)

def _df_exp(number):
    return math.exp(number)

def _df_sin(x):
    return math.sin(x)

def _df_cos(x):
    return math.cos(x)

def _df_tan(x):
    return math.tan(x)

def _df_asin(x):
    return math.asin(x)

def _df_acos(x):
    return math.acos(x)

def _df_atan(x):
    return math.atan(x)

def _df_atan2(y, x):
    return math.atan2(y, x)

def _df_degrees(radians):
    return math.degrees(radians)

def _df_radians(degrees):
    return math.radians(degrees)

def _df_hypot(*args):
    return math.hypot(*args)

def _df_factorial(n):
    return math.factorial(n)

def _df_gcd(a, b):
    return math.gcd(a, b)

def _df_lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def _df_comb(n, k):
    return math.comb(n, k)

def _df_perm(n, k=None):
    return math.perm(n, k)

def _df_clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def _df_lerp(a, b, t):
    return a + (b - a) * t

def _df_sign(x):
    if x > 0: return 1
    if x < 0: return -1
    return 0

def _df_is_nan(x):
    return math.isnan(x)

def _df_is_inf(x):
    return math.isinf(x)

def _df_is_finite(x):
    return math.isfinite(x)

def _df_mean(data):
    return sum(data) / len(data)

def _df_median(data):
    s = sorted(data)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]

def _df_stdev(data):
    m = sum(data) / len(data)
    return math.sqrt(sum((x - m) ** 2 for x in data) / max(len(data) - 1, 1))

def _df_variance(data):
    m = sum(data) / len(data)
    return sum((x - m) ** 2 for x in data) / max(len(data) - 1, 1)

def _df_mode(data):
    from collections import Counter
    c = Counter(data)
    return c.most_common(1)[0][0]

def _df_percentile(data, p):
    s = sorted(data)
    k = (len(s) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)

# ═══════════════════════════════════════════════════════════
#  COLLECTION FUNCTIONS
# ═══════════════════════════════════════════════════════════

def _df_enumerate(iterable):
    return list(enumerate(iterable))

def _df_zip(*iterables):
    return [list(x) for x in zip(*iterables)]

def _df_append(lst, item):
    lst.append(item)
    return lst

def _df_pop(lst, index=-1):
    return lst.pop(index)

def _df_insert(lst, index, item):
    lst.insert(index, item)
    return lst

def _df_remove(lst, item):
    lst.remove(item)
    return lst

def _df_keys(d):
    return list(d.keys())

def _df_values(d):
    return list(d.values())

def _df_items(d):
    return [list(pair) for pair in d.items()]

def _df_contains(collection, item):
    return item in collection

def _df_slice(collection, start=None, end=None, step=None):
    return collection[start:end:step]

def _df_flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            result.extend(_df_flatten(item))
        else:
            result.append(item)
    return result

def _df_unique(lst):
    seen = set()
    result = []
    for item in lst:
        key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def _df_count(collection, item=None):
    if item is not None:
        return collection.count(item)
    return len(collection)

def _df_index(collection, item):
    return collection.index(item)

def _df_first(collection):
    if collection:
        return collection[0]
    return None

def _df_last(collection):
    if collection:
        return collection[-1]
    return None

def _df_take(collection, n):
    return collection[:n]

def _df_drop(collection, n):
    return collection[n:]

def _df_chunk(collection, size):
    return [collection[i:i+size] for i in range(0, len(collection), size)]

def _df_interleave(*collections):
    result = []
    for items in itertools.zip_longest(*collections):
        for item in items:
            if item is not None:
                result.append(item)
    return result

def _df_rotate(lst, n):
    if not lst:
        return lst
    n = n % len(lst)
    return lst[n:] + lst[:n]

def _df_unzip(pairs):
    if not pairs:
        return [[], []]
    return [list(x) for x in zip(*pairs)]

def _df_merge_dicts(*dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result

def _df_invert_dict(d):
    return {v: k for k, v in d.items()}

def _df_pick(d, *keys_list):
    # If first arg is a list, use it as the keys
    if len(keys_list) == 1 and isinstance(keys_list[0], list):
        keys_list = keys_list[0]
    return {k: d[k] for k in keys_list if k in d}

def _df_omit(d, *keys_list):
    # If first arg is a list, use it as the keys
    if len(keys_list) == 1 and isinstance(keys_list[0], list):
        keys_list = keys_list[0]
    return {k: v for k, v in d.items() if k not in keys_list}

def _df_deep_copy(obj):
    import copy
    return copy.deepcopy(obj)

def _df_frequencies(lst):
    freq = {}
    for item in lst:
        key = str(item)
        freq[key] = freq.get(key, 0) + 1
    return freq

# ═══════════════════════════════════════════════════════════
#  FUNCTIONAL PROGRAMMING
# ═══════════════════════════════════════════════════════════

def _df_map(func, iterable):
    return list(map(func, iterable))

def _df_filter(func, iterable):
    return list(filter(func, iterable))

def _df_reduce(func, iterable, initial=None):
    if initial is not None:
        return functools.reduce(func, iterable, initial)
    return functools.reduce(func, iterable)

def _df_compose(*funcs):
    def composed(x):
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return BuiltinFunction("composed", composed)

def _df_pipe_fn(*funcs):
    def piped(x):
        result = x
        for f in funcs:
            result = f(result)
        return result
    return BuiltinFunction("piped", piped)

def _df_partial(func, *partial_args):
    def applied(*args):
        return func(*partial_args, *args)
    return BuiltinFunction("partial", applied)

def _df_curry(func, arity=None):
    if arity is None:
        import inspect
        try:
            arity = len(inspect.signature(func).parameters)
        except (ValueError, TypeError):
            arity = 2
    def curried(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        def more(*more_args):
            return curried(*args, *more_args)
        return BuiltinFunction("curried", more)
    return BuiltinFunction("curried", curried)

def _df_memoize(func):
    cache = {}
    def memoized(*args):
        key = str(args)
        if key not in cache:
            cache[key] = func(*args)
        return cache[key]
    return BuiltinFunction("memoized", memoized)

def _df_once(func):
    result = [None]
    called = [False]
    def once_fn(*args):
        if not called[0]:
            result[0] = func(*args)
            called[0] = True
        return result[0]
    return BuiltinFunction("once", once_fn)

def _df_tap(func, value):
    func(value)
    return value

def _df_identity(x):
    return x

def _df_constantly(value):
    def const_fn(*args):
        return value
    return BuiltinFunction("constant", const_fn)

def _df_complement(func):
    def negated(*args):
        return not func(*args)
    return BuiltinFunction("complement", negated)

def _df_every(func, iterable):
    return all(func(item) for item in iterable)

def _df_some(func, iterable):
    return any(func(item) for item in iterable)

def _df_none_of(func, iterable):
    return not any(func(item) for item in iterable)

def _df_find_first(func, iterable):
    for item in iterable:
        if func(item):
            return item
    return None

def _df_find_last(func, iterable):
    result = None
    for item in iterable:
        if func(item):
            result = item
    return result

def _df_flat_map(func, iterable):
    result = []
    for item in iterable:
        mapped = func(item)
        if isinstance(mapped, list):
            result.extend(mapped)
        else:
            result.append(mapped)
    return result

def _df_scan(func, iterable, initial=None):
    result = []
    acc = initial
    it = iter(iterable)
    if acc is None:
        acc = next(it)
        result.append(acc)
    else:
        result.append(acc)
    for item in it:
        acc = func(acc, item)
        result.append(acc)
    return result

def _df_zip_with(func, *iterables):
    return [func(*group) for group in zip(*iterables)]

# ═══════════════════════════════════════════════════════════
#  TIME & UTILITY
# ═══════════════════════════════════════════════════════════

def _df_random_fn():
    return random.random()

def _df_randint(a, b):
    return random.randint(a, b)

def _df_choice(lst):
    return random.choice(lst)

def _df_shuffle(lst):
    random.shuffle(lst)
    return lst

def _df_sample(lst, k):
    return random.sample(lst, k)

def _df_time():
    return time.time()

def _df_sleep(seconds):
    time.sleep(seconds / 1000.0)

def _df_exists(obj):
    return obj is not None

def _df_freeze(obj):
    if isinstance(obj, list):
        return tuple(obj)
    if isinstance(obj, dict):
        return tuple(sorted(obj.items()))
    return obj

def _df_thaw(obj):
    if isinstance(obj, tuple):
        return list(obj)
    return obj

def _df_hash_fn(obj):
    return hash(str(obj))

def _df_id_fn(obj):
    return id(obj)

def _df_inspect(obj):
    return f"<inspect type={type(obj).__name__} value={obj!r}>"

def _df_to_json(obj, indent=None):
    def default_serializer(o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        return str(o)
    return json.dumps(obj, indent=indent, default=default_serializer, ensure_ascii=False)

def _df_from_json(string):
    return json.loads(string)

def _df_uuid():
    import uuid
    return str(uuid.uuid4())

def _df_timestamp():
    import datetime
    return datetime.datetime.now().isoformat()

def _df_env_var(name, default=None):
    return os.environ.get(name, default)

def _df_hash_md5(string):
    return hashlib.md5(string.encode()).hexdigest()

def _df_hash_sha256(string):
    return hashlib.sha256(string.encode()).hexdigest()

def _df_base64_encode(string):
    import base64
    return base64.b64encode(string.encode()).decode()

def _df_base64_decode(string):
    import base64
    return base64.b64decode(string.encode()).decode()

def _df_chain(*iterables):
    result = []
    for it in iterables:
        result.extend(it)
    return result

def _df_product(*iterables):
    return [list(p) for p in itertools.product(*iterables)]

def _df_permutations(iterable, r=None):
    return [list(p) for p in itertools.permutations(iterable, r)]

def _df_combinations(iterable, r):
    return [list(c) for c in itertools.combinations(iterable, r)]

def _df_repeat_val(value, n):
    return [value] * n

def _df_accumulate(iterable, func=None):
    if func:
        return list(itertools.accumulate(iterable, func))
    return list(itertools.accumulate(iterable))

# ═══════════════════════════════════════════════════════════
#  TYPE CHECKING & VALIDATION
# ═══════════════════════════════════════════════════════════

def _df_is_empty(obj):
    if obj is None:
        return True
    if isinstance(obj, (str, list, dict, tuple)):
        return len(obj) == 0
    return False

def _df_is_string(obj):
    return isinstance(obj, str)

def _df_is_number(obj):
    return isinstance(obj, (int, float)) and not isinstance(obj, bool)

def _df_is_integer(obj):
    return isinstance(obj, int) and not isinstance(obj, bool)

def _df_is_float(obj):
    return isinstance(obj, float)

def _df_is_boolean(obj):
    return isinstance(obj, bool)

def _df_is_list(obj):
    return isinstance(obj, list)

def _df_is_dict(obj):
    return isinstance(obj, dict)

def _df_is_void(obj):
    return obj is None

def _df_is_callable(obj):
    return callable(obj)

def _df_coalesce(*args):
    for arg in args:
        if arg is not None:
            return arg
    return None

def _df_default(value, fallback):
    return value if value is not None else fallback

def _df_assert_type(value, expected_type_name):
    actual = _df_type(value)
    if actual != expected_type_name:
        raise TypeError(f"Expected {expected_type_name}, got {actual}")
    return value

def _df_validate(value, predicate, message="Validation failed"):
    if callable(predicate):
        if not predicate(value):
            raise ValueError(message)
    return value


# ═══════════════════════════════════════════════════════════
#  OOP AVANÇADO (Advanced Object-Oriented)
# ═══════════════════════════════════════════════════════════

def _df_instanceof(instance, blueprint):
    """Check if instance is of given blueprint or inherits from it."""
    if hasattr(instance, 'isinstance_of'):
        return instance.isinstance_of(blueprint)
    return False

def _df_has_method(instance, name):
    """Check if instance has a given method."""
    if hasattr(instance, 'has_method'):
        return instance.has_method(name)
    return False

def _df_has_field(instance, name):
    """Check if instance has a given field."""
    if hasattr(instance, 'fields'):
        return name in instance.fields
    return False

def _df_get_fields(instance):
    """Get all field names of an instance."""
    if hasattr(instance, 'fields'):
        return list(instance.fields.keys())
    return []

def _df_get_methods(instance):
    """Get all method names of an instance's blueprint."""
    if hasattr(instance, 'blueprint'):
        methods = list(instance.blueprint.methods.keys())
        for parent in instance.blueprint.parents:
            methods.extend(k for k in parent.methods.keys() if k not in methods)
        return methods
    return []

def _df_get_mro(instance):
    """Get Method Resolution Order of an instance."""
    if hasattr(instance, 'get_mro'):
        return [bp.name for bp in instance.get_mro()]
    return []

def _df_get_parent(instance):
    """Get first parent blueprint name."""
    if hasattr(instance, 'blueprint') and instance.blueprint.parents:
        return instance.blueprint.parents[0].name
    return None

def _df_class_name(instance):
    """Get the class/blueprint name of an instance."""
    if hasattr(instance, 'blueprint'):
        return instance.blueprint.name
    return type(instance).__name__


# ═══════════════════════════════════════════════════════════
#  REGISTRY
# ═══════════════════════════════════════════════════════════

def _df_expect(valor, rotulo=""):
    """O valor sob teste, com os matchers do Crucible."""
    from .stdlib.crucible import Expectativa
    return Expectativa(valor, rotulo)


def get_builtins() -> dict:
    """Return all built-in functions as a dictionary."""
    return {
        # ── Crucible ──
        # '__expect__' e o alvo interno de 'expect(x).to_be(y)'. Tem
        # dois sublinhados porque nao e para ser chamado a mao: quem
        # escreve o teste ve 'expect', e o parser traduz.
        "__expect__": BuiltinFunction("__expect__", _df_expect, 1),

        # ── Type & Conversion ──
        "len": BuiltinFunction("len", _df_len, 1),
        "type": BuiltinFunction("type", _df_type, 1),
        "linhagem": BuiltinFunction("linhagem", _df_linhagem, 1),
        "e_um": BuiltinFunction("e_um", _df_e_um, 2),
        "str": BuiltinFunction("str", _df_str, 1),
        "int": BuiltinFunction("int", _df_int, 1),
        "float": BuiltinFunction("float", _df_float, 1),
        "bool": BuiltinFunction("bool", _df_bool, 1),
        "cluster": BuiltinFunction("cluster", _df_cluster),
        "vault": BuiltinFunction("vault", _df_vault),
        "range": BuiltinFunction("range", _df_range),
        "cast": BuiltinFunction("cast", _df_str, 1),

        # ── String Functions (50+) ──
        "join": BuiltinFunction("join", _df_join, 2),
        "split": BuiltinFunction("split", _df_split),
        "strip": BuiltinFunction("strip", _df_strip),
        "lstrip": BuiltinFunction("lstrip", _df_lstrip),
        "rstrip": BuiltinFunction("rstrip", _df_rstrip),
        "upper": BuiltinFunction("upper", _df_upper, 1),
        "lower": BuiltinFunction("lower", _df_lower, 1),
        "title": BuiltinFunction("title", _df_title, 1),
        "capitalize": BuiltinFunction("capitalize", _df_capitalize, 1),
        "swapcase": BuiltinFunction("swapcase", _df_swapcase, 1),
        "center": BuiltinFunction("center", _df_center),
        "ljust": BuiltinFunction("ljust", _df_ljust),
        "rjust": BuiltinFunction("rjust", _df_rjust),
        "zfill": BuiltinFunction("zfill", _df_zfill, 2),
        "replace": BuiltinFunction("replace", _df_replace),
        "startswith": BuiltinFunction("startswith", _df_startswith, 2),
        "endswith": BuiltinFunction("endswith", _df_endswith, 2),
        "find": BuiltinFunction("find", _df_find),
        "rfind": BuiltinFunction("rfind", _df_rfind),
        "index_of": BuiltinFunction("index_of", _df_index_of),
        "last_index_of": BuiltinFunction("last_index_of", _df_last_index_of, 2),
        "char_at": BuiltinFunction("char_at", _df_char_at, 2),
        "substring": BuiltinFunction("substring", _df_substring),
        "isalpha": BuiltinFunction("isalpha", _df_isalpha, 1),
        "isdigit": BuiltinFunction("isdigit", _df_isdigit, 1),
        "isalnum": BuiltinFunction("isalnum", _df_isalnum, 1),
        "isspace": BuiltinFunction("isspace", _df_isspace, 1),
        "isupper": BuiltinFunction("isupper", _df_isupper, 1),
        "islower": BuiltinFunction("islower", _df_islower, 1),
        "istitle": BuiltinFunction("istitle", _df_istitle, 1),
        "isnumeric": BuiltinFunction("isnumeric", _df_isnumeric, 1),
        "isascii": BuiltinFunction("isascii", _df_isascii, 1),
        "repeat": BuiltinFunction("repeat", _df_repeat, 2),
        "reverse_str": BuiltinFunction("reverse_str", _df_reverse_str, 1),
        "trim": BuiltinFunction("trim", _df_trim, 1),
        "pad_start": BuiltinFunction("pad_start", _df_pad_start),
        "pad_end": BuiltinFunction("pad_end", _df_pad_end),
        "includes": BuiltinFunction("includes", _df_includes, 2),
        "concat": BuiltinFunction("concat", _df_concat),
        "char": BuiltinFunction("char", _df_char, 1),
        "ord": BuiltinFunction("ord", _df_ord_fn, 1),
        "encode": BuiltinFunction("encode", _df_encode),
        "decode": BuiltinFunction("decode", _df_decode),
        "format": BuiltinFunction("format", _df_format),
        "count_str": BuiltinFunction("count_str", _df_count_str, 2),
        "expandtabs": BuiltinFunction("expandtabs", _df_expandtabs),
        "partition": BuiltinFunction("partition", _df_partition, 2),
        "rpartition": BuiltinFunction("rpartition", _df_rpartition, 2),
        "splitlines": BuiltinFunction("splitlines", _df_splitlines),
        "removeprefix": BuiltinFunction("removeprefix", _df_removeprefix, 2),
        "removesuffix": BuiltinFunction("removesuffix", _df_removesuffix, 2),
        "words": BuiltinFunction("words", _df_words, 1),
        "lines": BuiltinFunction("lines", _df_lines, 1),
        "template": BuiltinFunction("template", _df_template, 2),

        # ── Regex Functions ──
        "regex_match": BuiltinFunction("regex_match", _df_regex_match),
        "regex_search": BuiltinFunction("regex_search", _df_regex_search),
        "regex_findall": BuiltinFunction("regex_findall", _df_regex_findall),
        "regex_sub": BuiltinFunction("regex_sub", _df_regex_sub),
        "regex_split": BuiltinFunction("regex_split", _df_regex_split),
        "regex_test": BuiltinFunction("regex_test", _df_regex_test, 2),
        "regex_count": BuiltinFunction("regex_count", _df_regex_count, 2),
        "regex_extract": BuiltinFunction("regex_extract", _df_regex_extract, 2),

        # ── Math (expanded 40+) ──
        "abs": BuiltinFunction("abs", _df_abs, 1),
        "min": BuiltinFunction("min", _df_min),
        "max": BuiltinFunction("max", _df_max),
        "sum": BuiltinFunction("sum", _df_sum, 1),
        "round": BuiltinFunction("round", _df_round),
        "floor": BuiltinFunction("floor", _df_floor, 1),
        "ceil": BuiltinFunction("ceil", _df_ceil, 1),
        "sqrt": BuiltinFunction("sqrt", _df_sqrt, 1),
        "cbrt": BuiltinFunction("cbrt", _df_cbrt, 1),
        "pow": BuiltinFunction("pow", _df_pow, 2),
        "log": BuiltinFunction("log", _df_log),
        "log2": BuiltinFunction("log2", _df_log2, 1),
        "log10": BuiltinFunction("log10", _df_log10, 1),
        "exp": BuiltinFunction("exp", _df_exp, 1),
        "sin": BuiltinFunction("sin", _df_sin, 1),
        "cos": BuiltinFunction("cos", _df_cos, 1),
        "tan": BuiltinFunction("tan", _df_tan, 1),
        "asin": BuiltinFunction("asin", _df_asin, 1),
        "acos": BuiltinFunction("acos", _df_acos, 1),
        "atan": BuiltinFunction("atan", _df_atan, 1),
        "atan2": BuiltinFunction("atan2", _df_atan2, 2),
        "degrees": BuiltinFunction("degrees", _df_degrees, 1),
        "radians": BuiltinFunction("radians", _df_radians, 1),
        "hypot": BuiltinFunction("hypot", _df_hypot),
        "factorial": BuiltinFunction("factorial", _df_factorial, 1),
        "gcd": BuiltinFunction("gcd", _df_gcd, 2),
        "lcm": BuiltinFunction("lcm", _df_lcm, 2),
        "comb": BuiltinFunction("comb", _df_comb, 2),
        "perm": BuiltinFunction("perm", _df_perm),
        "clamp": BuiltinFunction("clamp", _df_clamp, 3),
        "lerp": BuiltinFunction("lerp", _df_lerp, 3),
        "sign": BuiltinFunction("sign", _df_sign, 1),
        "is_nan": BuiltinFunction("is_nan", _df_is_nan, 1),
        "is_inf": BuiltinFunction("is_inf", _df_is_inf, 1),
        "is_finite": BuiltinFunction("is_finite", _df_is_finite, 1),
        "mean": BuiltinFunction("mean", _df_mean, 1),
        "median": BuiltinFunction("median", _df_median, 1),
        "stdev": BuiltinFunction("stdev", _df_stdev, 1),
        "variance": BuiltinFunction("variance", _df_variance, 1),
        "mode": BuiltinFunction("mode", _df_mode, 1),
        "percentile": BuiltinFunction("percentile", _df_percentile, 2),

        # ── Random ──
        "random": BuiltinFunction("random", _df_random_fn, 0),
        "randint": BuiltinFunction("randint", _df_randint, 2),
        "choice": BuiltinFunction("choice", _df_choice, 1),
        "shuffle": BuiltinFunction("shuffle", _df_shuffle, 1),
        "sample": BuiltinFunction("sample", _df_sample, 2),

        # ── Collections (expanded) ──
        "sorted": BuiltinFunction("sorted", _df_sorted),
        "reversed": BuiltinFunction("reversed", _df_reversed, 1),
        "enumerate": BuiltinFunction("enumerate", _df_enumerate, 1),
        "zip": BuiltinFunction("zip", _df_zip),
        "append": BuiltinFunction("append", _df_append, 2),
        "pop": BuiltinFunction("pop", _df_pop),
        "insert": BuiltinFunction("insert", _df_insert, 3),
        "remove": BuiltinFunction("remove", _df_remove, 2),
        "keys": BuiltinFunction("keys", _df_keys, 1),
        "values": BuiltinFunction("values", _df_values, 1),
        "items": BuiltinFunction("items", _df_items, 1),
        "contains": BuiltinFunction("contains", _df_contains, 2),
        "flatten": BuiltinFunction("flatten", _df_flatten, 1),
        "unique": BuiltinFunction("unique", _df_unique, 1),
        "count": BuiltinFunction("count", _df_count),
        "index": BuiltinFunction("index", _df_index, 2),
        "slice": BuiltinFunction("slice", _df_slice),
        "first": BuiltinFunction("first", _df_first, 1),
        "last": BuiltinFunction("last", _df_last, 1),
        "take": BuiltinFunction("take", _df_take, 2),
        "drop": BuiltinFunction("drop", _df_drop, 2),
        "chunk": BuiltinFunction("chunk", _df_chunk, 2),
        "interleave": BuiltinFunction("interleave", _df_interleave),
        "rotate": BuiltinFunction("rotate", _df_rotate, 2),
        "unzip": BuiltinFunction("unzip", _df_unzip, 1),
        "merge_dicts": BuiltinFunction("merge_dicts", _df_merge_dicts),
        "invert_dict": BuiltinFunction("invert_dict", _df_invert_dict, 1),
        "pick": BuiltinFunction("pick", _df_pick),
        "omit": BuiltinFunction("omit", _df_omit),
        "deep_copy": BuiltinFunction("deep_copy", _df_deep_copy, 1),
        "frequencies": BuiltinFunction("frequencies", _df_frequencies, 1),

        # ── Functional Programming ──
        "map": BuiltinFunction("map", _df_map, 2),
        "filter": BuiltinFunction("filter", _df_filter, 2),
        "reduce": BuiltinFunction("reduce", _df_reduce),
        "compose": BuiltinFunction("compose", _df_compose),
        "pipe_fn": BuiltinFunction("pipe_fn", _df_pipe_fn),
        "partial": BuiltinFunction("partial", _df_partial),
        "curry": BuiltinFunction("curry", _df_curry),
        "memoize": BuiltinFunction("memoize", _df_memoize, 1),
        "once": BuiltinFunction("once", _df_once, 1),
        "tap": BuiltinFunction("tap", _df_tap, 2),
        "identity": BuiltinFunction("identity", _df_identity, 1),
        "constantly": BuiltinFunction("constantly", _df_constantly, 1),
        "complement": BuiltinFunction("complement", _df_complement, 1),
        "every": BuiltinFunction("every", _df_every, 2),
        "some": BuiltinFunction("some", _df_some, 2),
        "none_of": BuiltinFunction("none_of", _df_none_of, 2),
        "find_first": BuiltinFunction("find_first", _df_find_first, 2),
        "find_last": BuiltinFunction("find_last", _df_find_last, 2),
        "flat_map": BuiltinFunction("flat_map", _df_flat_map, 2),
        "scan": BuiltinFunction("scan", _df_scan),
        "zip_with": BuiltinFunction("zip_with", _df_zip_with),

        # ── Itertools ──
        "chain": BuiltinFunction("chain", _df_chain),
        "product": BuiltinFunction("product", _df_product),
        "permutations": BuiltinFunction("permutations", _df_permutations),
        "combinations": BuiltinFunction("combinations", _df_combinations, 2),
        "repeat_val": BuiltinFunction("repeat_val", _df_repeat_val, 2),
        "accumulate": BuiltinFunction("accumulate", _df_accumulate),

        # ── Time ──
        "time": BuiltinFunction("time", _df_time, 0),
        "sleep": BuiltinFunction("sleep", _df_sleep, 1),
        "timestamp": BuiltinFunction("timestamp", _df_timestamp, 0),

        # ── Utility ──
        "exists": BuiltinFunction("exists", _df_exists, 1),
        "freeze": BuiltinFunction("freeze", _df_freeze, 1),
        "thaw": BuiltinFunction("thaw", _df_thaw, 1),
        "hash": BuiltinFunction("hash", _df_hash_fn, 1),
        "id": BuiltinFunction("id", _df_id_fn, 1),
        "uuid": BuiltinFunction("uuid", _df_uuid, 0),
        "to_json": BuiltinFunction("to_json", _df_to_json),
        "from_json": BuiltinFunction("from_json", _df_from_json, 1),
        "hash_md5": BuiltinFunction("hash_md5", _df_hash_md5, 1),
        "hash_sha256": BuiltinFunction("hash_sha256", _df_hash_sha256, 1),
        "base64_encode": BuiltinFunction("base64_encode", _df_base64_encode, 1),
        "base64_decode": BuiltinFunction("base64_decode", _df_base64_decode, 1),
        "env_var": BuiltinFunction("env_var", _df_env_var),

        # ── Type Checking ──
        "is_empty": BuiltinFunction("is_empty", _df_is_empty, 1),
        "is_string": BuiltinFunction("is_string", _df_is_string, 1),
        "is_number": BuiltinFunction("is_number", _df_is_number, 1),
        "is_integer": BuiltinFunction("is_integer", _df_is_integer, 1),
        "is_float": BuiltinFunction("is_float", _df_is_float, 1),
        "is_boolean": BuiltinFunction("is_boolean", _df_is_boolean, 1),
        "is_list": BuiltinFunction("is_list", _df_is_list, 1),
        "is_dict": BuiltinFunction("is_dict", _df_is_dict, 1),
        "is_void": BuiltinFunction("is_void", _df_is_void, 1),
        "is_callable": BuiltinFunction("is_callable", _df_is_callable, 1),
        "coalesce": BuiltinFunction("coalesce", _df_coalesce),
        "default": BuiltinFunction("default", _df_default, 2),
        "default_val": BuiltinFunction("default_val", _df_default, 2),
        "assert_type": BuiltinFunction("assert_type", _df_assert_type, 2),
        "validate": BuiltinFunction("validate", _df_validate),

        # ── OOP Avançado ──
        "instanceof": BuiltinFunction("instanceof", _df_instanceof, 2),
        "has_method": BuiltinFunction("has_method", _df_has_method, 2),
        "has_field": BuiltinFunction("has_field", _df_has_field, 2),
        "get_fields": BuiltinFunction("get_fields", _df_get_fields, 1),
        "get_methods": BuiltinFunction("get_methods", _df_get_methods, 1),
        "get_mro": BuiltinFunction("get_mro", _df_get_mro, 1),
        "get_parent": BuiltinFunction("get_parent", _df_get_parent, 1),
        "class_name": BuiltinFunction("class_name", _df_class_name, 1),

        # ── Constants ──
        "PI": math.pi,
        "E": math.e,
        "TAU": math.tau,
        "INF": math.inf,
        "NAN": math.nan,
        "NEWLINE": "\n",
        "TAB": "\t",
        "EMPTY": "",
        "MAX_INT": 2**63 - 1,
        "MIN_INT": -(2**63),
    }
