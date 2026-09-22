"""Um 'assert' que confere uma coleção não confere nada.

'assert xs >> morph v: v is 9' lê o 'is' DENTRO do corpo do morph, e o
assert recebe uma lista de booleanos — verdadeira sempre que não está
vazia. O teste passa sem provar nada. Foi achado numa página desta
documentação, que "provava" a estabilidade de uma ordenação assim.
"""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402


def _codigos(fonte):
    return [d.code for d in check_program(parse(tokenize(fonte + "\n", "t"), "t"), "t")]


@pytest.mark.parametrize("fonte", [
    "xs := [1]\nassert xs >> morph v: v is 9",
    "xs := [1]\nassert xs >> sift v: v bigger 5",
    "assert [1 is 2]",
    "assert [v cycle v in [1] given v is 2]",
])
def test_acusa(fonte):
    assert "assert-sempre-verdadeiro" in _codigos(fonte)


@pytest.mark.parametrize("fonte", [
    "xs := [1]\nassert (xs >> morph v: v * 2) is [2]",
    "assert len([1]) is 1",
    "assert 1 in [1]",
    "assert yes",
])
def test_cala(fonte):
    assert "assert-sempre-verdadeiro" not in _codigos(fonte)
