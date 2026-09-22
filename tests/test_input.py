"""input(pergunta) — a entrada do usuário, que a linguagem não tinha.

Não havia jeito nenhum de ler do teclado: nem embutida, nem Arcane.OS,
nem Arcane.IO. O primeiro programa interativo de quem está começando não
tinha como ser escrito.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rodar(tmp_path, fonte, entrada):
    f = tmp_path / "e.df"
    f.write_text(fonte + "\n", encoding="utf-8")
    return subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)],
                          input=entrada, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=RAIZ,
                          env=dict(os.environ, NO_COLOR="1"))


def test_le_uma_linha_sem_a_quebra(tmp_path):
    r = _rodar(tmp_path, 'n := input("nome: ")\nassert n is "Ana"\nout $"[{n}]"', "Ana\n")
    assert r.returncode == 0, r.stdout
    assert r.stdout == "nome: [Ana]\n"


def test_no_fim_da_entrada_devolve_void_e_o_laco_termina(tmp_path):
    fonte = ('t := 0\nl := input()\npersist l isnt void:\n'
             '    t += int(l)\n    l := input()\nout t')
    r = _rodar(tmp_path, fonte, "1\n2\n39\n")
    assert r.returncode == 0 and r.stdout.strip() == "42"


def test_a_linha_vazia_e_texto_vazio_e_nao_void(tmp_path):
    r = _rodar(tmp_path, 'l := input()\nassert l is ""\nassert input() is void', "\n")
    assert r.returncode == 0, r.stdout


def test_sem_pergunta_nao_imprime_nada(tmp_path):
    r = _rodar(tmp_path, 'x := input()', "a\n")
    assert r.stdout == ""


def test_a_quebra_do_windows_tambem_sai(tmp_path):
    r = _rodar(tmp_path, 'assert input() is "ok"', "ok\r\n")
    assert r.returncode == 0, r.stdout


def test_o_check_conhece_a_embutida(tmp_path):
    f = tmp_path / "c.df"
    f.write_text('x := input("? ")\nout x\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "check", str(f)],
                       capture_output=True, text=True, encoding="utf-8",
                       cwd=RAIZ, env=dict(os.environ, NO_COLOR="1"))
    assert "sem erros" in r.stdout, r.stdout
