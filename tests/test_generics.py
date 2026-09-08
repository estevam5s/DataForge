"""
Testes de generics.

Era o item que o roadmap listava como pendente. A linguagem é de
tipagem dinâmica, então `<T>` não é verificado em tempo de execução —
ele documenta a relação entre entrada e saída e é aceito pelo analisador
estático. É o mesmo que o TypeScript faz ao compilar: os tipos somem.

O que **não** pode acontecer é `<T>` ser erro de sintaxe, que era o
estado anterior — quem vem de Java ou TypeScript batia nisso na
primeira tentativa.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.interpreter import Interpreter                    # noqa: E402
from dataforge.lexer import tokenize                             # noqa: E402
from dataforge.parser import parse                               # noqa: E402
from dataforge.typechecker import check_program                  # noqa: E402


def run(fonte):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte)))
    return buffer.getvalue().strip()


def erros(fonte):
    return [d for d in check_program(parse(tokenize(fonte)), "t.df")
            if d.severity == "error"]


# ── Sintaxe ──────────────────────────────────────────────────

def test_acao_generica():
    assert run('''
action primeiro<T>(lista) -> T:
    yield lista[0]

out primeiro([1, 2, 3]), primeiro(["a", "b"])''') == "1 a"


def test_dois_parametros_de_tipo():
    assert run('''
action par<K, V>(k: K, v: V) -> V:
    yield v

out par("idade", 42)''') == "42"


def test_blueprint_generico():
    assert run('''
blueprint Pilha<T>:
    itens: Cluster := []

    action por(x: T):
        self.itens.append(x)

    action tirar() -> T:
        yield self.itens.pop()

p := spawn Pilha()
p.por(1)
p.por(2)
out p.tirar()''') == "2"


def test_o_generico_serve_para_qualquer_tipo():
    """É o ponto do genérico: a mesma estrutura, tipos diferentes."""
    assert run('''
blueprint Caixa<T>(valor):
    action pegar() -> T:
        yield self.valor

out (spawn Caixa(42)).pegar(), (spawn Caixa("texto")).pegar()''') == "42 texto"


def test_o_tipo_do_blueprint_vale_nos_metodos():
    """'blueprint Pilha<T>' com 'action por(x: T)' é o caso normal."""
    assert erros('''
blueprint Pilha<T>:
    action por(x: T):
        out x
    action tirar() -> T:
        yield 1''') == []


# ── Não pode quebrar a comparação ────────────────────────────

@pytest.mark.parametrize("fonte,esperado", [
    ("out 3 < 5", "yes"),
    ("out 5 < 3", "no"),
    ("a := 1\nb := 2\nout a < b", "yes"),
    ("out 3 < 5, 5 > 3", "yes yes"),
    ("x := 10\nout x < 20 and x > 5", "yes"),
])
def test_comparacao_com_menor_continua_funcionando(fonte, esperado):
    """'<' abre um genérico só quando o que segue confirma: um nome de
    tipo (maiúsculo) e um '>' fechando. 'a < b' segue comparação."""
    assert run(fonte) == esperado


def test_comparacao_com_nome_maiusculo_nao_vira_generico():
    assert run('''
Total := 5
Limite := 10
out Total < Limite''') == "yes"


# ── O analisador estático ────────────────────────────────────

def test_o_checker_aceita_o_parametro_de_tipo():
    assert erros('''
action primeiro<T>(lista: Cluster) -> T:
    yield lista[0]''') == []


def test_o_checker_ainda_recusa_tipo_inexistente():
    """O genérico não pode virar uma porta para qualquer nome passar."""
    problemas = erros('''
action f(x: NaoExiste):
    yield x''')
    assert any("NaoExiste" in d.message for d in problemas)


def test_o_parametro_de_tipo_nao_vaza_para_fora():
    """'T' vale dentro da ação que o declarou, e só ali."""
    problemas = erros('''
action com_generico<T>(x: T):
    yield x

action sem_generico(y: T):
    yield y''')
    assert any("'T'" in d.message for d in problemas), (
        "o T da primeira ação não pode valer na segunda")


# ── Em tempo de execução, o tipo normal ainda é verificado ───

def test_tipo_declarado_normal_continua_verificado():
    from dataforge.errors import DataForgeError
    with pytest.raises(DataForgeError, match="Integer"):
        run('action f(x: Integer):\n    yield x\n\nf("texto")')


def test_o_parametro_de_tipo_aceita_qualquer_valor():
    """A linguagem é dinâmica: <T> documenta, não verifica."""
    assert run('''
action eco<T>(x: T) -> T:
    yield x

out eco(1), eco("a"), eco([1, 2]), eco(yes)''') == "1 a [1, 2] yes"
