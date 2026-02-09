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


class TestResults:
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


results = TestResults()


def test(name, source, expected_output=None, expected_var=None, expected_value=None):
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

test("Integer assignment", "x := 42", expected_var="x", expected_value=42)
test("Float assignment", "x := 3.14", expected_var="x", expected_value=3.14)
test("String assignment", 'x := "hello"', expected_var="x", expected_value="hello")
test("Boolean yes", "x := yes", expected_var="x", expected_value=True)
test("Boolean no", "x := no", expected_var="x", expected_value=False)
test("Void", "x := void", expected_var="x", expected_value=None)
test("List/Cluster", "x := [1, 2, 3]", expected_var="x", expected_value=[1, 2, 3])

# ── Output Tests ──
print("\n\033[1;36m[Output]\033[0m")

test("out string", 'out "Hello"', expected_output="Hello")
test("out number", "out 42", expected_output="42")
test("out boolean", "out yes", expected_output="yes")
test("out void", "out void", expected_output="void")
test("out concat", 'out "a" + "b"', expected_output="ab")
test("out math", "out 2 + 3", expected_output="5")

# ── Arithmetic ──
print("\n\033[1;36m[Arithmetic]\033[0m")

test("Addition", "x := 10 + 20", expected_var="x", expected_value=30)
test("Subtraction", "x := 50 - 15", expected_var="x", expected_value=35)
test("Multiplication", "x := 6 * 7", expected_var="x", expected_value=42)
test("Division", "x := 10 / 4", expected_var="x", expected_value=2.5)
test("Modulo", "x := 17 % 5", expected_var="x", expected_value=2)
test("Power", "x := 2 ** 10", expected_var="x", expected_value=1024)
test("Precedence", "x := 2 + 3 * 4", expected_var="x", expected_value=14)
test("Parentheses", "x := (2 + 3) * 4", expected_var="x", expected_value=20)
test("Negative", "x := -5 + 10", expected_var="x", expected_value=5)

# ── Comparison ──
print("\n\033[1;36m[Comparison]\033[0m")

test("is equal", "x := 5 is 5", expected_var="x", expected_value=True)
test("isnt", "x := 5 isnt 3", expected_var="x", expected_value=True)
test("bigger", "x := 10 bigger 5", expected_var="x", expected_value=True)
test("smaller", "x := 3 smaller 7", expected_var="x", expected_value=True)
test("bigger false", "x := 3 bigger 7", expected_var="x", expected_value=False)

# ── Logic ──
print("\n\033[1;36m[Logic]\033[0m")

test("and true", "x := yes and yes", expected_var="x", expected_value=True)
test("and false", "x := yes and no", expected_var="x", expected_value=False)
test("or true", "x := no or yes", expected_var="x", expected_value=True)
test("or false", "x := no or no", expected_var="x", expected_value=False)
test("not", "x := not no", expected_var="x", expected_value=True)

# ── Conditionals ──
print("\n\033[1;36m[Conditionals]\033[0m")

test("given true",
     'x := 5\ngiven x is 5:\n    out "yes"',
     expected_output="yes")

test("given false → otherwise",
     'x := 3\ngiven x is 5:\n    out "five"\notherwise:\n    out "other"',
     expected_output="other")

test("given → orif",
     'x := 2\ngiven x is 1:\n    out "one"\norif x is 2:\n    out "two"\notherwise:\n    out "other"',
     expected_output="two")

# ── Match ──
print("\n\033[1;36m[Match]\033[0m")

test("match point",
     'x := "B"\nmatch x:\n    point "A":\n        out "alpha"\n    point "B":\n        out "beta"\n    default:\n        out "other"',
     expected_output="beta")

test("match default",
     'x := "Z"\nmatch x:\n    point "A":\n        out "alpha"\n    default:\n        out "unknown"',
     expected_output="unknown")

# ── Loops ──
print("\n\033[1;36m[Loops]\033[0m")

test("cycle from to",
     'result := 0\ncycle i from 1 to 5:\n    result := result + i',
     expected_var="result", expected_value=15)

test("cycle in",
     'result := ""\ncycle x in ["a", "b", "c"]:\n    result := result + x',
     expected_var="result", expected_value="abc")

test("cycle halt",
     'result := 0\ncycle i from 1 to 100:\n    given i bigger 3:\n        halt\n    result := result + i',
     expected_var="result", expected_value=6)

test("cycle skip",
     'result := 0\ncycle i from 1 to 5:\n    given i % 2 is 0:\n        skip\n    result := result + i',
     expected_var="result", expected_value=9)

test("persist loop",
     'x := 0\npersist x smaller 5:\n    x := x + 1',
     expected_var="x", expected_value=5)

# ── Actions ──
print("\n\033[1;36m[Actions]\033[0m")

test("simple action",
     'action add(a, b):\n    yield a + b\nx := add(3, 4)',
     expected_var="x", expected_value=7)

test("action default param",
     'action greet(name := "World"):\n    yield "Hello " + name\nx := greet()',
     expected_var="x", expected_value="Hello World")

test("recursive action",
     'action fact(n):\n    given n smaller_eq 1:\n        yield 1\n    yield n * fact(n - 1)\nx := fact(5)',
     expected_var="x", expected_value=120)

# ── Blueprints ──
print("\n\033[1;36m[Blueprints]\033[0m")

test("blueprint spawn",
     'blueprint Dog:\n    action setup(name):\n        self.name := name\n    action bark():\n        yield "Woof from " + self.name\nd := spawn Dog("Rex")\nx := d.bark()',
     expected_var="x", expected_value="Woof from Rex")

test("blueprint statics",
     'blueprint Counter:\n    static count := 0\n    action setup():\n        Counter.count := Counter.count + 1\nc1 := spawn Counter()\nc2 := spawn Counter()\nx := Counter.count',
     expected_var="x", expected_value=2)

# ── Error Handling ──
print("\n\033[1;36m[Error Handling]\033[0m")

test("monitor/handle",
     'x := "ok"\nmonitor:\n    trigger "boom"\n    x := "fail"\nhandle e:\n    x := e',
     expected_var="x", expected_value="boom")

test("monitor/ensure",
     'x := 0\nmonitor:\n    x := 1\n    trigger "error"\nhandle e:\n    x := 2\nensure:\n    x := x + 10',
     expected_var="x", expected_value=12)

# ── Steady (Constants) ──
print("\n\033[1;36m[Steady]\033[0m")

test("steady declaration",
     'steady MAX := 100\nx := MAX',
     expected_var="x", expected_value=100)

# ── Pipeline ──
print("\n\033[1;36m[Pipelines]\033[0m")

test("sift (filter)",
     'data := [1, 2, 3, 4, 5]\nx := data >> sift n: n bigger 3',
     expected_var="x", expected_value=[4, 5])

test("morph (map)",
     'data := [1, 2, 3]\nx := data >> morph n: n * 10',
     expected_var="x", expected_value=[10, 20, 30])

test("chained pipeline",
     'data := [1, 2, 3, 4, 5, 6]\nx := data >> sift n: n % 2 is 0 >> morph n: n * n',
     expected_var="x", expected_value=[4, 16, 36])

# ── Builtins ──
print("\n\033[1;36m[Built-in Functions]\033[0m")

test("len", 'x := len([1, 2, 3])', expected_var="x", expected_value=3)
test("abs", "x := abs(-10)", expected_var="x", expected_value=10)
test("min", "x := min(3, 1, 2)", expected_var="x", expected_value=1)
test("max", "x := max(3, 1, 2)", expected_var="x", expected_value=3)
test("sum", "x := sum([1, 2, 3, 4, 5])", expected_var="x", expected_value=15)
test("upper", 'x := upper("hello")', expected_var="x", expected_value="HELLO")
test("lower", 'x := lower("HELLO")', expected_var="x", expected_value="hello")
test("join", 'x := join("-", [1, 2, 3])', expected_var="x", expected_value="1-2-3")
test("split", 'x := split("a b c")', expected_var="x", expected_value=["a", "b", "c"])
test("contains", 'x := contains([1, 2, 3], 2)', expected_var="x", expected_value=True)
test("sorted", "x := sorted([3, 1, 2])", expected_var="x", expected_value=[1, 2, 3])
test("unique", "x := unique([1, 2, 2, 3, 3])", expected_var="x", expected_value=[1, 2, 3])
test("flatten", "x := flatten([[1, 2], [3, [4]]])", expected_var="x", expected_value=[1, 2, 3, 4])

# ═══════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════
success = results.summary()
sys.exit(0 if success else 1)
