"""`dataforge converter` — Python vira DataForge.

O que estes testes cobram, em ordem de importância:

1. que o resultado **rode** — compilar não basta, e foi assim que três
   bugs apareceram (blueprint sem `spawn`, `setup` com aridade errada,
   `json.dumps` que não existe aqui);
2. que o que não traduz seja **marcado**, e não adivinhado;
3. que Python inválido seja recusado, em vez de virar lixo com
   aparência de tradução.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.interpreter import Interpreter    # noqa: E402
from dataforge.lexer import tokenize             # noqa: E402
from dataforge.migrar import converter_fonte     # noqa: E402
from dataforge.parser import parse               # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402


def converter(py):
    return converter_fonte(py, "prova.py")


def roda(py):
    """Converte, executa, e devolve o que o programa imprimiu.

    É o teste que importa: um `.df` que compila e explode ao rodar é
    exatamente o que este conversor existe para não produzir.
    """
    texto, _ = converter(py)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(texto, "c.df"), "c.df"), "c.df")
    return buffer.getvalue().strip()


def sem_erros(py):
    texto, _ = converter(py)
    arvore = parse(tokenize(texto, "c.df"), "c.df")
    return [d for d in check_program(arvore, "c.df") if d.severity == "error"]


# ── O básico, e ele tem de RODAR ─────────────────────────────

def test_funcao_e_retorno():
    assert roda("def dobro(n):\n    return n * 2\nprint(dobro(21))") == "42"


def test_condicional_com_elif():
    assert roda('''
def f(n):
    if n > 9:
        return "alto"
    elif n > 5:
        return "medio"
    else:
        return "baixo"
print(f(10), f(7), f(1))''') == "alto medio baixo"


def test_laco_sobre_range_e_inclusivo_nos_dois_extremos():
    """`range(3)` dá 0,1,2 — e `cycle from 0 to 3` daria 0,1,2,3.

    Por isso a tradução põe `- 1` no fim. Um conversor que esquecesse
    disso geraria um laço com uma volta a mais, e o erro passaria
    despercebido em metade dos programas.
    """
    assert roda("for i in range(3):\n    print(i)") == "0\n1\n2"


def test_laco_sobre_colecao():
    assert roda("for x in [10, 20]:\n    print(x)") == "10\n20"


def test_while_break_continue():
    assert roda('''
n = 0
while True:
    n += 1
    if n == 2:
        continue
    if n > 3:
        break
    print(n)''') == "1\n3"


def test_try_except_finally():
    assert roda('''
try:
    raise ValueError("falhou")
except ValueError as e:
    print("peguei")
finally:
    print("fim")''') == "peguei\nfim"


def test_fstring_com_formato():
    assert roda('x = 3.14159\nprint(f"{x:.2f}")') == "3.14"


def test_compreensao_com_condicao():
    assert roda("print([x * x for x in range(6) if x % 2 == 0])") \
        == "[0, 4, 16]"


def test_lambda():
    assert roda("f = lambda x: x * 2\nprint(f(21))") == "42"


def test_divisao_inteira_vira_til_barra():
    """`//` é **comentário** em DataForge. Traduzir literal apagaria a conta."""
    texto, _ = converter("print(7 // 2)")
    assert "~/" in texto, "'//' precisa virar '~/'"
    assert roda("print(7 // 2)") == "3"


def test_true_false_none():
    assert roda("print(True, False, None)") == "yes no void"


# ── Classes: três bugs moraram aqui ──────────────────────────

def test_classe_constroi_com_spawn():
    """Sem `spawn`, a linha compila e explode: "'Conta' is not callable"."""
    assert roda('''
class Ponto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def soma(self):
        return self.x + self.y

p = Ponto(3, 4)
print(p.soma())''') == "7"


def test_campo_mutavel_do_init_vira_campo_com_padrao():
    """`self.itens = []` não pode virar um `setup()`.

    `setup` receberia zero argumentos e explodiria na construção. Campo
    com padrão é copiado por instância — a mesma garantia que o
    `__init__` dava.
    """
    assert roda('''
class Caixa:
    def __init__(self, nome):
        self.nome = nome
        self.itens = []

    def por(self, x):
        self.itens.append(x)
        return len(self.itens)

c = Caixa("a")
d = Caixa("b")
c.por(1)
print(c.itens, d.itens)''') == "[1] []"


def test_heranca():
    assert roda('''
class Base:
    def nome(self):
        return "base"

class Filha(Base):
    def nome(self):
        return "filha"

print(Filha().nome())''') == "filha"


# ── Módulos: mapear o módulo não basta ───────────────────────

def test_import_da_stdlib_vira_modulo_nativo():
    texto, _ = converter("import math\nprint(math.sqrt(16))")
    assert "adopt Arcane.Math as math" in texto
    assert roda("import math\nprint(math.sqrt(16))") == "4.0"


def test_o_nome_da_funcao_muda_junto_com_o_modulo():
    """`json.dumps` vira `Arcane.Serialization`, e lá se chama `to_json`.

    Sem mapear o nome, o arquivo compila e explode ao rodar: "module
    has no 'dumps'". É exatamente a falha que o conversor existe para
    não produzir.
    """
    assert roda('import json\nprint(json.dumps({"a": 1}))') == '{"a": 1}'


def test_pacote_sem_equivalente_abre_a_ponte():
    texto, _ = converter("import numpy\nprint(1)")
    assert "adopt Python.numpy" in texto


def test_from_import():
    texto, _ = converter("from math import sqrt, floor")
    assert "Arcane.Math" in texto and "sqrt" in texto


# ── O que NÃO traduz precisa aparecer ────────────────────────

@pytest.mark.parametrize("py,esperado", [
    ("def f(*args):\n    return 1", "*args"),
    ("def f(p):\n    with open(p) as x:\n        return 1", "with"),
    ("def f():\n    global g\n    g = 1", "global"),
    ("def f(xs):\n    return {x: x for x in xs}", "dicionario"),
    ("def f(xs):\n    if (n := len(xs)) > 3:\n        return n\n    return 0",
     "walrus"),
])
def test_o_intraduzivel_vira_pendencia_marcada(py, esperado):
    """Um conversor que erra em silêncio é pior que um que aponta.

    No primeiro caso alguém descobre em produção.
    """
    texto, pendencias = converter(py)
    assert pendencias, f"'{esperado}' passou sem marcacao"
    assert "TODO(converter)" in texto or "/*" in texto
    assert any(esperado in m for _, m, _ in pendencias), \
        f"nenhuma pendencia menciona '{esperado}': {pendencias}"


def test_a_pendencia_traz_o_python_original():
    """Um `// TODO` sozinho não diz o que estava ali."""
    texto, _ = converter("def f():\n    global contador\n    contador = 1")
    assert "Python: global contador" in texto


def test_o_cabecalho_conta_quantas_pendencias():
    texto, _ = converter("def f(*a):\n    return 1")
    assert "precisam de revisao" in texto

    limpo, _ = converter("def f(n):\n    return n")
    assert "Nada ficou pendente" in limpo


# ── Recusas ──────────────────────────────────────────────────

def test_python_invalido_e_recusado():
    """Traduzir código quebrado produziria lixo com cara de tradução."""
    with pytest.raises(SyntaxError):
        converter("def f(\n    isto nao e python")


def test_o_resultado_passa_no_analisador_estatico():
    """Compilar não é o mesmo que estar certo — mas é o piso."""
    assert not sem_erros('''
class Pilha:
    def __init__(self):
        self.itens = []

    def empilhar(self, x):
        self.itens.append(x)
        return len(self.itens)

def principal():
    p = Pilha()
    for i in range(3):
        p.empilhar(i)
    return p.itens

print(principal())''')


# ── generator ────────────────────────────────────────────────

def test_yield_do_python_vira_stream_action_com_emit():
    """`yield` retorna em DataForge; quem produz sequência é `emit`.

    Traduzir literal daria uma ação que devolve o primeiro item e
    encerra — errado de um jeito que parece certo.
    """
    texto, _ = converter("def pares(n):\n    for i in range(n):\n"
                         "        if i % 2 == 0:\n            yield i")
    assert "stream action" in texto
    assert "emit i" in texto

    assert roda('''
def pares(n):
    for i in range(n):
        if i % 2 == 0:
            yield i

print(list(pares(6)))''') == "[0, 2, 4]"
