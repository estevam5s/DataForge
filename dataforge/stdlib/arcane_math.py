"""
Arcane.Math - Scientific Computing & Mathematics
"""

import cmath
import math
from fractions import Fraction
import random



def _fracao(a, b=None):
    """Uma fracao exata. Aceita (1, 3), '1/3', 0.25 ou outra fracao."""
    if b is not None:
        return Fraction(int(a), int(b))
    if isinstance(a, Fraction):
        return a
    if isinstance(a, str):
        return Fraction(a)
    if isinstance(a, float):
        # De float vem a fracao EXATA daquele float — que para 0.1 e
        # 3602879701896397/36028797018963968, e nao 1/10. Limitar o
        # denominador devolve o que a pessoa quis dizer.
        return Fraction(a).limit_denominator(1000000)
    return Fraction(int(a))


def _dobrar(partes, operacao):
    if len(partes) == 1 and isinstance(partes[0], (list, tuple)):
        partes = partes[0]
    valores = [_fracao(p) for p in partes]
    if not valores:
        return Fraction(0)
    total = valores[0]
    for v in valores[1:]:
        total = operacao(total, v)
    return total


def _complexo_texto(z):
    """'3 + 4i', que e como se escreve — e nao o 'j' do Python."""
    z = complex(z)
    real = f"{z.real:g}"
    imag = f"{abs(z.imag):g}"
    sinal = "-" if z.imag < 0 else "+"
    if z.imag == 0:
        return real
    if z.real == 0:
        return f"{'-' if z.imag < 0 else ''}{imag}i"
    return f"{real} {sinal} {imag}i"


class ArcaneMath:
    """Mathematics and scientific computing module."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Math",

            # ── Fracao exata ───────────────────────────────────
            #
            # 1/3 em float e 0.333…, e tres deles nao dao 1. A fracao
            # guarda o numerador e o denominador, e a conta fecha:
            #
            #     f := Math.fracao(1, 3)
            #     Math.fracao_texto(Math.fracao_soma(f, f, f))   "1"
            #
            # E diferente do Decimal: o Decimal e exato em BASE DEZ (e
            # por isso serve para dinheiro), a fracao e exata em
            # qualquer razao — 1/3 nao tem forma decimal finita.
            "fracao": _fracao,
            "fracao_de_texto": lambda t: Fraction(str(t)),
            "fracao_soma": lambda *p: _dobrar(p, lambda a, b: a + b),
            "fracao_menos": lambda a, b: _fracao(a) - _fracao(b),
            "fracao_vezes": lambda *p: _dobrar(p, lambda a, b: a * b),
            "fracao_dividido": lambda a, b: _fracao(a) / _fracao(b),
            "fracao_texto": lambda f: str(_fracao(f)),
            "fracao_partes": lambda f: [_fracao(f).numerator,
                                        _fracao(f).denominator],
            "fracao_float": lambda f: float(_fracao(f)),
            "fracao_limitar": lambda f, teto: _fracao(f).limit_denominator(
                int(teto)),

            # ── Numero complexo ────────────────────────────────
            #
            # A linguagem nao tem literal complexo, entao ele e um par:
            # 'Math.complexo(3, 4)' e 3 + 4i. Sinal e fase servem a
            # quem trabalha com onda; a raiz de numero negativo, a quem
            # cai nela sem querer.
            "complexo": lambda real, imaginario=0.0: complex(
                float(real), float(imaginario)),
            "complexo_partes": lambda z: [z.real, z.imag],
            # Envolvidas de proposito: uma funcao C do Python nao tem
            # assinatura estavel entre versoes, e a doc GERADA passaria
            # a mudar conforme o Python de quem a gera. Ha teste sobre
            # isso ('a doc gerada nao depende da versao do Python').
            "complexo_modulo": lambda z: abs(z),
            "complexo_fase": lambda z: cmath.phase(z),
            "complexo_polar": lambda z: list(cmath.polar(z)),
            "complexo_de_polar": lambda r, a: cmath.rect(float(r), float(a)),
            "complexo_conjugado": lambda z: complex(z).conjugate(),
            "complexo_raiz": lambda z: cmath.sqrt(z),
            "complexo_exp": lambda z: cmath.exp(z),
            "complexo_log": lambda z, base=None: (
                cmath.log(z) if base is None else cmath.log(z, base)),
            "complexo_texto": _complexo_texto,

            # Constants
            "PI": math.pi,
            "E": math.e,
            "TAU": math.tau,
            "INF": math.inf,
            "NAN": math.nan,

            # Basic
            "sum": cls._sum,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,

            # Powers & Roots
            "sqrt": math.sqrt,
            "cbrt": lambda x: x ** (1/3),
            "pow": math.pow,
            "exp": math.exp,
            "log": math.log,
            "log2": math.log2,
            "log10": math.log10,

            # Trigonometry
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "atan2": math.atan2,
            "degrees": math.degrees,
            "radians": math.radians,
            "hypot": math.hypot,

            # Statistics
            "mean": cls._mean,
            "median": cls._median,
            "stdev": cls._stdev,
            "variance": cls._variance,

            # Random
            "random": cls._random_dict(),

            # Matrix operations
            "matrix": cls._matrix,
            "dot": cls._dot,
            "transpose": cls._transpose,
            "zeros": cls._zeros,
            "ones": cls._ones,
            "identity": cls._identity,
            "determinant": cls._determinant,

            # Combinatorics
            "factorial": math.factorial,
            "gcd": math.gcd,
            "lcm": cls._lcm,
            "comb": math.comb,
            "perm": math.perm,

            # Special
            "clamp": cls._clamp,
            "lerp": cls._lerp,
            "map_range": cls._map_range,
            "fibonacci": cls._fibonacci,
            "is_prime": cls._is_prime,
        }

    @staticmethod
    def _sum(data):
        if isinstance(data, list):
            if data and isinstance(data[0], list):
                # Matrix/vector sum
                return [sum(row) for row in data]
            return sum(data)
        return sum(data)

    @staticmethod
    def _mean(data):
        return sum(data) / len(data)

    @staticmethod
    def _median(data):
        s = sorted(data)
        n = len(s)
        mid = n // 2
        if n % 2 == 0:
            return (s[mid - 1] + s[mid]) / 2
        return s[mid]

    @staticmethod
    def _stdev(data):
        mean = sum(data) / len(data)
        return math.sqrt(sum((x - mean) ** 2 for x in data) / (len(data) - 1))

    @staticmethod
    def _variance(data):
        mean = sum(data) / len(data)
        return sum((x - mean) ** 2 for x in data) / (len(data) - 1)

    @staticmethod
    def _random_dict():
        return {
            "random": random.random,
            "randint": random.randint,
            "choice": random.choice,
            "shuffle": lambda lst: (random.shuffle(lst), lst)[-1],
            "uniform": random.uniform,
            "gauss": random.gauss,
            "seed": random.seed,
            "sample": random.sample,
        }

    @staticmethod
    def _matrix(data):
        """Create a matrix (list of lists)."""
        return [list(row) for row in data]

    @staticmethod
    def _dot(a, b):
        """Matrix dot product."""
        if isinstance(a[0], list):  # Matrix * Matrix
            rows_a, cols_a = len(a), len(a[0])
            cols_b = len(b[0]) if isinstance(b[0], list) else 1
            result = [[0] * cols_b for _ in range(rows_a)]
            for i in range(rows_a):
                for j in range(cols_b):
                    for k in range(cols_a):
                        bval = b[k][j] if isinstance(b[0], list) else b[k]
                        result[i][j] += a[i][k] * bval
            return result
        else:
            # Vector dot product
            return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _transpose(matrix):
        return [list(row) for row in zip(*matrix)]

    @staticmethod
    def _zeros(rows, cols=None):
        if cols is None:
            return [0] * rows
        return [[0] * cols for _ in range(rows)]

    @staticmethod
    def _ones(rows, cols=None):
        if cols is None:
            return [1] * rows
        return [[1] * cols for _ in range(rows)]

    @staticmethod
    def _identity(n):
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    @staticmethod
    def _determinant(matrix):
        n = len(matrix)
        if n == 1:
            return matrix[0][0]
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        det = 0
        for j in range(n):
            minor = [row[:j] + row[j+1:] for row in matrix[1:]]
            det += ((-1) ** j) * matrix[0][j] * ArcaneMath._determinant(minor)
        return det

    @staticmethod
    def _lcm(a, b):
        return abs(a * b) // math.gcd(a, b)

    @staticmethod
    def _clamp(value, min_val, max_val):
        return max(min_val, min(max_val, value))

    @staticmethod
    def _lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def _map_range(value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def _fibonacci(n):
        a, b = 0, 1
        result = []
        for _ in range(n):
            result.append(a)
            a, b = b, a + b
        return result

    @staticmethod
    def _is_prime(n):
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True
