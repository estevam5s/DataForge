"""Crucible.cenario — dado, quando, então, e as três regras que ele cobra."""
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402
from dataforge.stdlib.crucible import FalhaDeExpectativa  # noqa: E402

C = get_module("Arcane.Crucible")


def _saque(valor_final):
    c = C["cenario"]("sacar")
    c.dado("uma conta com 100", lambda m: m.__setitem__("saldo", 100))
    c.quando("saco 30", lambda m: m.__setitem__("saldo", m["saldo"] - 30))
    c.entao(f"o saldo fica em {valor_final}", lambda m: m["saldo"] == valor_final)
    return c


def test_o_cenario_certo_passa_e_devolve_os_passos():
    r = _saque(70).rodar()
    assert r["ok"] and [p["tipo"] for p in r["passos"]] == ["dado", "quando", "entao"]
    assert r["mundo"] == {"saldo": 70}


def test_a_falha_diz_o_passo_e_a_frase():
    with pytest.raises(FalhaDeExpectativa) as e:
        _saque(60).rodar()
    assert "passo 3" in str(e.value) and "o saldo fica em 60" in str(e.value)


def test_um_erro_dentro_do_passo_tambem_nomeia_o_passo():
    c = C["cenario"]("quebra")
    c.dado("nada", lambda m: None)
    c.quando("divido por zero", lambda m: 1 / 0)
    c.entao("nunca chega", lambda m: True)
    with pytest.raises(FalhaDeExpectativa) as e:
        c.rodar()
    assert "passo 2" in str(e.value) and "quando divido por zero" in str(e.value)


def test_dado_depois_de_quando_e_recusado_na_montagem():
    c = C["cenario"]("fora de ordem")
    c.quando("ajo", lambda m: None)
    with pytest.raises(Exception) as e:
        c.dado("preparo", lambda m: None)
    assert "dado → quando → entao" in str(e.value)


def test_sem_entao_nao_ha_cenario():
    c = C["cenario"]("sem conferencia")
    c.dado("x", lambda m: None)
    c.quando("y", lambda m: None)
    with pytest.raises(Exception) as e:
        c.rodar()
    assert "entao" in str(e.value)


def test_e_continua_o_tipo_anterior_e_o_texto_se_le():
    c = C["cenario"]("com e")
    c.dado("a", lambda m: m.__setitem__("n", 1))
    c.e("b", lambda m: m.__setitem__("n", m["n"] + 1))
    c.quando("c", lambda m: None)
    c.entao("n e 2", lambda m: m["n"] == 2)
    c.e("n e positivo", lambda m: m["n"] > 0)
    assert c.texto().splitlines() == [
        "Cenario: com e", "  Dado a", "  E b", "  Quando c",
        "  Entao n e 2", "  E n e positivo"]
    assert c.rodar()["ok"]


def test_o_mundo_recomeca_a_cada_rodada():
    c = _saque(70)
    c.rodar()
    assert c.rodar()["mundo"] == {"saldo": 70}


def test_funciona_de_dentro_de_um_df(tmp_path):
    f = tmp_path / "c.df"
    f.write_text(
        'adopt Arcane.Crucible as C\n'
        'c := C.cenario("x")\n'
        'c.dado("100", lambda m: m.set("s", 100))\n'
        'c.entao("fica 100", lambda m: m["s"] is 100)\n'
        'assert c.rodar()["ok"]\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ)
    assert r.returncode == 0, r.stdout + r.stderr
