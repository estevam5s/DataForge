"""NO_COLOR vale para a CLI inteira, e não só para o depurador.

`NO_COLOR` é o padrão de fato (no-color.org). O depurador e a marca já o
respeitavam; a CLI e os diagnósticos do `check`, não — um log de CI com
NO_COLOR=1 saía cheio de `\\x1b[1;31m`, e um script que procurava
"erro:" na saída não achava.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _check(tmp_path, env_extra, *flags):
    (tmp_path / "a.df").write_text("x := naoExiste\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "NO_COLOR"}
    env.update(env_extra, PYTHONPATH=RAIZ)
    return subprocess.run([sys.executable, "-m", "dataforge", "check", "a.df", *flags],
                          cwd=tmp_path, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env).stdout


def test_no_color_tira_a_cor_do_diagnostico_e_do_resumo(tmp_path):
    saida = _check(tmp_path, {"NO_COLOR": "1"})
    assert "\x1b[" not in saida
    assert "a.df:1:6: erro:" in saida


def test_a_flag_continua_valendo(tmp_path):
    assert "\x1b[" not in _check(tmp_path, {}, "--no-color")


def test_sem_nada_a_cor_continua(tmp_path):
    assert "\x1b[" in _check(tmp_path, {})
