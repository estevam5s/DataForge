"""`dataforge completar` — o autocompletar sai do catálogo, e o shell o aceita.

O script é conferido pelo **shell**, e não pelo texto: `bash -n` e
`zsh -n` recusam o que um teste de `in` aprovaria. E o Tab é simulado
de verdade no bash, porque um script que carrega e não completa nada
passaria em todo o resto.
"""
import os
import shutil
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import completar  # noqa: E402
from dataforge.cli import GRUPOS  # noqa: E402

NOMES = [c.nome for _g, cmds in GRUPOS for c in cmds]


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_todo_comando_do_catalogo_esta_no_script(shell):
    texto = completar.SHELLS[shell]()
    faltando = [n for n in NOMES if n not in texto]
    assert not faltando, f"fora do autocompletar de {shell}: {faltando}"


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_o_shell_aceita_a_sintaxe(shell, tmp_path):
    if not shutil.which(shell):
        pytest.skip(f"{shell} ausente")
    f = tmp_path / f"c.{shell}"
    f.write_text(completar.SHELLS[shell](), encoding="utf-8")
    r = subprocess.run([shell, "-n", str(f)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr


def _tab_no_bash(tmp_path, palavras):
    if not shutil.which("bash"):
        pytest.skip("bash ausente")
    f = tmp_path / "c.bash"
    f.write_text(completar.bash(), encoding="utf-8")
    lista = " ".join(f"'{p}'" for p in palavras)
    script = (f"source {f}; COMP_WORDS=({lista}); COMP_CWORD={len(palavras) - 1}; "
              "_dataforge; echo \"${COMPREPLY[@]}\"")
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=tmp_path)
    return r.stdout.split()


def test_o_tab_completa_o_comando(tmp_path):
    assert _tab_no_bash(tmp_path, ["dataforge", "complet"]) == ["completar", "completion"]


def test_as_opcoes_sao_do_comando_e_nao_de_todos(tmp_path):
    opcoes = _tab_no_bash(tmp_path, ["dataforge", "check", "--"])
    assert "--strict" in opcoes and "--formato" in opcoes
    assert "--forcar" not in opcoes          # e do devops


def test_depois_de_run_o_tab_completa_arquivo(tmp_path):
    (tmp_path / "main.df").write_text("out 1\n")
    assert _tab_no_bash(tmp_path, ["dataforge", "run", "ma"]) == ["main.df"]


def test_shell_desconhecido_sai_com_erro():
    r = subprocess.run([sys.executable, "-m", "dataforge", "completar", "tcsh"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ)
    assert r.returncode == 1 and "bash|zsh|fish" in r.stdout
