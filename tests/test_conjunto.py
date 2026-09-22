"""O conjunto como tipo da linguagem: '{1, 2}', 'set(xs)', 'x: Set<T>'.

'typeof' já respondia "Set" para um conjunto que viesse de
Arcane.Collections — e a linguagem não tinha como criar um, nem como
anotá-lo: 'x: Set' dizia "Unknown type". O que se cobra aqui é que as
três metades concordem, e que o vault não perca nenhuma forma que tinha.
"""
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402


def _arquivo(tmp_path, fonte):
    f = tmp_path / "c.df"
    f.write_text(fonte + "\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ, env=dict(os.environ, NO_COLOR="1"))
    return r


def _diagnosticos(fonte):
    return list(check_program(parse(tokenize(fonte + "\n", "<t>"), "<t>"), "<t>"))


@pytest.mark.parametrize("fonte", [
    'assert typeof({1, 2}) is "Set"',
    'assert {1, 2, 2} is {2, 1}',
    'assert typeof({}) is "Vault"',
    'assert typeof(set()) is "Set" and len(set()) is 0',
    'assert set([3, 3, 1]) is {1, 3}',
    'assert set({"a": 1, "b": 2}) is {"a", "b"}',
    'assert set("abc") is {"abc"}',
    'assert {n % 3 cycle n in range(0, 9)} is {0, 1, 2}',
    'xs := [1, 2]\nassert {...xs, 3} is {1, 2, 3}',
    'b := {"a": 1}\nv := {...b, "c": 2}\nassert typeof(v) is "Vault" and v["c"] is 2',
    'b := {"a": 1}\nassert typeof({...b}) is "Vault"',
    'assert freeze({1, 2}) is freeze({2, 1})',
    's: Set := {1}\nt: Set<Integer> := {1, 2}\nassert 2 in t',
    's := {\n    1,\n    2\n}\nassert len(s) is 2',
])
def test_o_conjunto_se_comporta(tmp_path, fonte):
    r = _arquivo(tmp_path, fonte)
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_saida_e_estavel_e_com_a_grafia_da_linguagem(tmp_path):
    saidas = {_arquivo(tmp_path, 'out {"verde", "azul", "rosa"}, set()').stdout for _ in range(4)}
    assert saidas == {"{azul, rosa, verde} set()\n"}


def test_item_que_muda_e_recusado_no_check_e_em_execucao(tmp_path):
    d = _diagnosticos("x := {[1, 2], 3}")
    assert [x.code for x in d if x.severity == "error"] == ["set-item-mutavel"]
    r = _arquivo(tmp_path, "xs := [1]\ny := {xs}")
    assert r.returncode == 1 and "freeze" in r.stdout and "Cluster" in r.stdout


def test_a_anotacao_set_e_conhecida_e_o_tipo_e_cobrado(tmp_path):
    assert not [x for x in _diagnosticos("s: Set := {1}") if x.severity == "error"]
    r = _arquivo(tmp_path, 't: Set<Integer> := {1, "dois"}')
    assert r.returncode == 1


def test_o_formatador_preserva_as_tres_formas(tmp_path):
    f = tmp_path / "f.df"
    f.write_text("x := {1,2 ,3}\ny := {n cycle n in [1,2]}\nz := {...[1], 2}\n", encoding="utf-8")
    subprocess.run([sys.executable, "-m", "dataforge", "fmt", str(f)], cwd=RAIZ,
                   capture_output=True)
    assert f.read_text(encoding="utf-8") == \
        "x := {1, 2, 3}\ny := {n cycle n in [1, 2]}\nz := {...[1], 2}\n"


def test_a_propriedade_set_continua_valendo(tmp_path):
    r = _arquivo(tmp_path, "blueprint T:\n    _c := 0\n    get c():\n        yield self._c\n"
                           "    set c(v):\n        self._c := v\n"
                           "t := spawn T()\nt.c := 3\nassert t.c is 3\nassert set([1]) is {1}")
    assert r.returncode == 0, r.stdout
