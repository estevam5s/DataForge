"""Arcane.Evolucao — obsoleta, experimental, renomeada.

O que se cobra: a ação continua funcionando, o aviso sai UMA vez por
ação e na saída de ERRO (nunca no meio da saída do programa), e
DF_OBSOLETOS escolhe entre avisar, calar e reprovar.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROGRAMA = '''adopt Arcane.Evolucao as Ev

action novo(a):
    yield a * 2

mark @Ev.obsoleta("motivo", desde := "1.4", use := "novo")
action velho(a):
    yield a * 2

cycle i in range(0, 5):
    assert velho(i) is i * 2
out "saida limpa"
'''


def _rodar(tmp_path, fonte, **env):
    f = tmp_path / "e.df"
    f.write_text(fonte, encoding="utf-8")
    return subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=RAIZ,
                          env=dict(os.environ, NO_COLOR="1", **env))


def test_funciona_avisa_uma_vez_e_na_saida_de_erro(tmp_path):
    r = _rodar(tmp_path, PROGRAMA)
    assert r.returncode == 0
    assert r.stdout == "saida limpa\n"
    avisos = [l for l in r.stderr.splitlines() if l.startswith("aviso:")]
    assert avisos == ["aviso: 'velho' esta obsoleta desde a 1.4: motivo. Use 'novo'."]


def test_df_obsoletos_erro_reprova(tmp_path):
    r = _rodar(tmp_path, PROGRAMA, DF_OBSOLETOS="erro")
    assert r.returncode == 1 and "obsoleta" in r.stdout + r.stderr


def test_df_obsoletos_silencio_cala(tmp_path):
    r = _rodar(tmp_path, PROGRAMA, DF_OBSOLETOS="silencio")
    assert r.returncode == 0 and "aviso" not in r.stderr


def test_experimental_nao_reprova_nem_com_erro(tmp_path):
    fonte = ('adopt Arcane.Evolucao as Ev\nmark @Ev.experimental("muda")\n'
             'action f():\n    yield 1\nassert f() is 1\n')
    r = _rodar(tmp_path, fonte, DF_OBSOLETOS="erro")
    assert r.returncode == 0 and "experimental" in r.stderr


def test_renomeada_e_avisos(tmp_path):
    fonte = ('adopt Arcane.Evolucao as Ev\naction novo(x):\n    yield x\n'
             'antigo := Ev.renomeada(novo, "antigo", "2.0")\nassert antigo(7) is 7\n'
             'a := Ev.avisos()\nassert len(a) is 1 and a[0]["acao"] is "antigo"\n'
             'Ev.esquecer()\nassert len(Ev.avisos()) is 0\n')
    r = _rodar(tmp_path, fonte)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "renomeada para 'novo' na 2.0" in r.stderr
