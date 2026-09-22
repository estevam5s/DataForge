"""Um parâmetro com nome de palavra reservada diz que a palavra é reservada.

'action f(no)' respondia "Expected IDENTIFIER, got BOOLEAN (False)" — que
fala do token e não da causa. 'no', 'in', 'is', 'to', 'from' são nomes
naturais em português, e a atribuição já dizia a coisa certa.
"""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402


@pytest.mark.parametrize("palavra", ["no", "in", "is", "to", "from", "step", "default"])
def test_a_mensagem_diz_que_a_palavra_e_reservada(palavra):
    with pytest.raises(Exception) as e:
        parse(tokenize(f"action f({palavra}):\n    yield 1\n", "t"), "t")
    msg = str(e.value)
    assert f"'{palavra}' is a reserved keyword" in msg and "parameter" in msg


def test_o_nome_valido_continua_valendo():
    parse(tokenize("action f(no_, nodo):\n    yield nodo\n", "t"), "t")
