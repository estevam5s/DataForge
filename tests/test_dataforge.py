"""
DataForge Test Suite
Comprehensive tests for the DataForge language.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.lexer import tokenize
from dataforge.parser import parse
from dataforge.interpreter import Interpreter
from dataforge.errors import DataForgeError, HaltSignal, SkipSignal, YieldSignal
from dataforge.tokens import TokenType
import io
from contextlib import redirect_stdout


def capture_output(source: str) -> str:
    """Run DataForge code and capture stdout."""
    tokens = tokenize(source)
    tree = parse(tokens)
    interp = Interpreter()
    f = io.StringIO()
    with redirect_stdout(f):
        interp.run(tree)
    return f.getvalue().strip()


def run_and_get_env(source: str) -> dict:
    """Run code and return the global environment."""
    tokens = tokenize(source)
    tree = parse(tokens)
    interp = Interpreter()
    f = io.StringIO()
    with redirect_stdout(f):
        interp.run(tree)
    return interp.global_env.variables


class Resultados:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, name):
        self.passed += 1
        print(f"  \033[1;32m✓\033[0m {name}")

    def fail(self, name, expected, got):
        self.failed += 1
        self.errors.append((name, expected, got))
        print(f"  \033[1;31m✗\033[0m {name}")
        print(f"    Expected: {expected!r}")
        print(f"    Got:      {got!r}")

    def error(self, name, err):
        self.failed += 1
        self.errors.append((name, "no error", str(err)))
        print(f"  \033[1;31m✗\033[0m {name}")
        print(f"    Error: {err}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} passed", end="")
        if self.failed:
            print(f", \033[1;31m{self.failed} failed\033[0m")
        else:
            print(f" \033[1;32m— All tests passed!\033[0m")
        print(f"{'='*50}\n")
        return self.failed == 0


results = Resultados()


def verificar(name, source, expected_output=None, expected_var=None, expected_value=None):
    """Run a test case."""
    try:
        if expected_output is not None:
            output = capture_output(source)
            if output == expected_output:
                results.ok(name)
            else:
                results.fail(name, expected_output, output)
        elif expected_var is not None:
            env = run_and_get_env(source)
            val = env.get(expected_var)
            if val == expected_value:
                results.ok(name)
            else:
                results.fail(name, expected_value, val)
    except Exception as e:
        results.error(name, e)


# ═══════════════════════════════════════════════════════════
#  TEST SUITE
# ═══════════════════════════════════════════════════════════

print("\n\033[1;35m── DataForge Test Suite ──\033[0m\n")

# ── Lexer Tests ──
print("\033[1;36m[Lexer]\033[0m")

def test_lexer():
    tokens = tokenize('x := 42')
    types = [t.type for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
    if types == [TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INTEGER]:
        results.ok("Lexer: basic assignment tokens")
    else:
        results.fail("Lexer: basic assignment tokens", "IDENTIFIER ASSIGN INTEGER", str(types))

    tokens = tokenize('"hello world"')
    string_tokens = [t for t in tokens if t.type == TokenType.STRING]
    if string_tokens and string_tokens[0].value == "hello world":
        results.ok("Lexer: string literal")
    else:
        results.fail("Lexer: string literal", "hello world", str(string_tokens))

    tokens = tokenize('given x bigger 10:')
    kw_types = [t.type for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
    expected = [TokenType.GIVEN, TokenType.IDENTIFIER, TokenType.BIGGER, TokenType.INTEGER, TokenType.COLON]
    if kw_types == expected:
        results.ok("Lexer: keywords")
    else:
        results.fail("Lexer: keywords", str(expected), str(kw_types))

test_lexer()

# ── Literal Tests ──
print("\n\033[1;36m[Literals & Variables]\033[0m")

verificar("Integer assignment", "x := 42", expected_var="x", expected_value=42)
verificar("Float assignment", "x := 3.14", expected_var="x", expected_value=3.14)
verificar("String assignment", 'x := "hello"', expected_var="x", expected_value="hello")
verificar("Boolean yes", "x := yes", expected_var="x", expected_value=True)
verificar("Boolean no", "x := no", expected_var="x", expected_value=False)
verificar("Void", "x := void", expected_var="x", expected_value=None)
verificar("List/Cluster", "x := [1, 2, 3]", expected_var="x", expected_value=[1, 2, 3])

# ── Output Tests ──
print("\n\033[1;36m[Output]\033[0m")

verificar("out string", 'out "Hello"', expected_output="Hello")
verificar("out number", "out 42", expected_output="42")
verificar("out boolean", "out yes", expected_output="yes")
verificar("out void", "out void", expected_output="void")
verificar("out concat", 'out "a" + "b"', expected_output="ab")
verificar("out math", "out 2 + 3", expected_output="5")

# ── Arithmetic ──
print("\n\033[1;36m[Arithmetic]\033[0m")

verificar("Addition", "x := 10 + 20", expected_var="x", expected_value=30)
verificar("Subtraction", "x := 50 - 15", expected_var="x", expected_value=35)
verificar("Multiplication", "x := 6 * 7", expected_var="x", expected_value=42)
verificar("Division", "x := 10 / 4", expected_var="x", expected_value=2.5)
verificar("Modulo", "x := 17 % 5", expected_var="x", expected_value=2)
verificar("Power", "x := 2 ** 10", expected_var="x", expected_value=1024)
verificar("Precedence", "x := 2 + 3 * 4", expected_var="x", expected_value=14)
verificar("Parentheses", "x := (2 + 3) * 4", expected_var="x", expected_value=20)
verificar("Negative", "x := -5 + 10", expected_var="x", expected_value=5)

# ── Comparison ──
print("\n\033[1;36m[Comparison]\033[0m")

verificar("is equal", "x := 5 is 5", expected_var="x", expected_value=True)
verificar("isnt", "x := 5 isnt 3", expected_var="x", expected_value=True)
verificar("bigger", "x := 10 bigger 5", expected_var="x", expected_value=True)
verificar("smaller", "x := 3 smaller 7", expected_var="x", expected_value=True)
verificar("bigger false", "x := 3 bigger 7", expected_var="x", expected_value=False)

# ── Logic ──
print("\n\033[1;36m[Logic]\033[0m")

verificar("and true", "x := yes and yes", expected_var="x", expected_value=True)
verificar("and false", "x := yes and no", expected_var="x", expected_value=False)
verificar("or true", "x := no or yes", expected_var="x", expected_value=True)
verificar("or false", "x := no or no", expected_var="x", expected_value=False)
verificar("not", "x := not no", expected_var="x", expected_value=True)

# ── Conditionals ──
print("\n\033[1;36m[Conditionals]\033[0m")

verificar("given true",
     'x := 5\ngiven x is 5:\n    out "yes"',
     expected_output="yes")

verificar("given false → otherwise",
     'x := 3\ngiven x is 5:\n    out "five"\notherwise:\n    out "other"',
     expected_output="other")

verificar("given → orif",
     'x := 2\ngiven x is 1:\n    out "one"\norif x is 2:\n    out "two"\notherwise:\n    out "other"',
     expected_output="two")

# ── Match ──
print("\n\033[1;36m[Match]\033[0m")

verificar("match point",
     'x := "B"\nmatch x:\n    point "A":\n        out "alpha"\n    point "B":\n        out "beta"\n    default:\n        out "other"',
     expected_output="beta")

verificar("match default",
     'x := "Z"\nmatch x:\n    point "A":\n        out "alpha"\n    default:\n        out "unknown"',
     expected_output="unknown")

# ── Loops ──
print("\n\033[1;36m[Loops]\033[0m")

verificar("cycle from to",
     'result := 0\ncycle i from 1 to 5:\n    result := result + i',
     expected_var="result", expected_value=15)

verificar("cycle in",
     'result := ""\ncycle x in ["a", "b", "c"]:\n    result := result + x',
     expected_var="result", expected_value="abc")

verificar("cycle halt",
     'result := 0\ncycle i from 1 to 100:\n    given i bigger 3:\n        halt\n    result := result + i',
     expected_var="result", expected_value=6)

verificar("cycle skip",
     'result := 0\ncycle i from 1 to 5:\n    given i % 2 is 0:\n        skip\n    result := result + i',
     expected_var="result", expected_value=9)

verificar("persist loop",
     'x := 0\npersist x smaller 5:\n    x := x + 1',
     expected_var="x", expected_value=5)

# ── Actions ──
print("\n\033[1;36m[Actions]\033[0m")

verificar("simple action",
     'action add(a, b):\n    yield a + b\nx := add(3, 4)',
     expected_var="x", expected_value=7)

verificar("action default param",
     'action greet(name := "World"):\n    yield "Hello " + name\nx := greet()',
     expected_var="x", expected_value="Hello World")

verificar("recursive action",
     'action fact(n):\n    given n smaller_eq 1:\n        yield 1\n    yield n * fact(n - 1)\nx := fact(5)',
     expected_var="x", expected_value=120)

# ── Blueprints ──
print("\n\033[1;36m[Blueprints]\033[0m")

verificar("blueprint spawn",
     'blueprint Dog:\n    action setup(name):\n        self.name := name\n    action bark():\n        yield "Woof from " + self.name\nd := spawn Dog("Rex")\nx := d.bark()',
     expected_var="x", expected_value="Woof from Rex")

verificar("blueprint statics",
     'blueprint Counter:\n    static count := 0\n    action setup():\n        Counter.count := Counter.count + 1\nc1 := spawn Counter()\nc2 := spawn Counter()\nx := Counter.count',
     expected_var="x", expected_value=2)

# ── Error Handling ──
print("\n\033[1;36m[Error Handling]\033[0m")

verificar("monitor/handle",
     'x := "ok"\nmonitor:\n    trigger "boom"\n    x := "fail"\nhandle e:\n    x := e',
     expected_var="x", expected_value="boom")

verificar("monitor/ensure",
     'x := 0\nmonitor:\n    x := 1\n    trigger "error"\nhandle e:\n    x := 2\nensure:\n    x := x + 10',
     expected_var="x", expected_value=12)

# ── Steady (Constants) ──
print("\n\033[1;36m[Steady]\033[0m")

verificar("steady declaration",
     'steady MAX := 100\nx := MAX',
     expected_var="x", expected_value=100)

# ── Pipeline ──
print("\n\033[1;36m[Pipelines]\033[0m")

verificar("sift (filter)",
     'data := [1, 2, 3, 4, 5]\nx := data >> sift n: n bigger 3',
     expected_var="x", expected_value=[4, 5])

verificar("morph (map)",
     'data := [1, 2, 3]\nx := data >> morph n: n * 10',
     expected_var="x", expected_value=[10, 20, 30])

verificar("chained pipeline",
     'data := [1, 2, 3, 4, 5, 6]\nx := data >> sift n: n % 2 is 0 >> morph n: n * n',
     expected_var="x", expected_value=[4, 16, 36])

# ── Builtins ──
print("\n\033[1;36m[Built-in Functions]\033[0m")

verificar("len", 'x := len([1, 2, 3])', expected_var="x", expected_value=3)
verificar("abs", "x := abs(-10)", expected_var="x", expected_value=10)
verificar("min", "x := min(3, 1, 2)", expected_var="x", expected_value=1)
verificar("max", "x := max(3, 1, 2)", expected_var="x", expected_value=3)
verificar("sum", "x := sum([1, 2, 3, 4, 5])", expected_var="x", expected_value=15)
verificar("upper", 'x := upper("hello")', expected_var="x", expected_value="HELLO")
verificar("lower", 'x := lower("HELLO")', expected_var="x", expected_value="hello")
verificar("join", 'x := join("-", [1, 2, 3])', expected_var="x", expected_value="1-2-3")
verificar("split", 'x := split("a b c")', expected_var="x", expected_value=["a", "b", "c"])
verificar("contains", 'x := contains([1, 2, 3], 2)', expected_var="x", expected_value=True)
verificar("sorted", "x := sorted([3, 1, 2])", expected_var="x", expected_value=[1, 2, 3])
verificar("unique", "x := unique([1, 2, 2, 3, 3])", expected_var="x", expected_value=[1, 2, 3])
verificar("flatten", "x := flatten([[1, 2], [3, [4]]])", expected_var="x", expected_value=[1, 2, 3, 4])

# ═══════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════
success = results.summary()

# Executado como script: devolve o codigo de saida. Sob pytest, este arquivo e
# apenas importado — sair aqui abortaria a coleta, entao so saimos quando o
# modulo e o __main__.
if __name__ == "__main__":
    sys.exit(0 if success else 1)


def test_suite_legada():
    """Expoe a suite legada ao pytest como um unico teste."""
    assert success, "a suite legada tem falhas"
