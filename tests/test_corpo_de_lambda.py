"""O corpo de um lambda absorve o ternário e o `??`; o pipeline, não.

Com o corpo lido abaixo do `??`, `lambda x: v[x] ?? 0` era
`(lambda x: v[x]) ?? 0` — e o padrão nunca servia, porque um lambda
nunca é void. `lambda s: "" given ok(s) otherwise "erro"` virava um
ternário SOBRE o lambda, avaliando `s` fora dele. Uma página da Vitrine
mostrava exatamente essa forma.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from tests._df import rodar  # noqa: E402


def test_ternario_e_coalesce_ficam_dentro_do_lambda(tmp_path):
    r = rodar(tmp_path, '''v := {"a": 1}
padrao := lambda x: v[x] ?? 0
curta := lambda s: "ok" given len(s) bigger 3 otherwise "curta"
out padrao("a"), padrao("b"), curta("ab"), curta("abcd")
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["1", "0", "curta", "ok"]


def test_o_pipeline_continua_fora(tmp_path):
    """A armadilha 22 continua valendo: é ela que a mensagem explica."""
    r = rodar(tmp_path, '''xs := [1, 2]
f := lambda => (xs >> morph x: x * 2)
out f()
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "[2, 4]"
