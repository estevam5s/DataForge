"""Canal entre fibras, errno do FFI, e o grafo de fluxo em DOT."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402
from tests._df import rodar  # noqa: E402

PRODUTOR = '''adopt Arcane.Laco as L
laco := L.novo()
c := L.canal(CAP)
log := []
stream action produtor(n):
    cycle i from 1 to n:
        log.append($"e{i}")
        emit L.enviar(c, i)
    c.fechar()
stream action consumidor():
    caixa := {}
    persist yes:
        emit L.receber(c, caixa, "v")
        given caixa["v"] is void:
            halt
        log.append($"r{caixa["v"]}")
        emit L.dormir(1)
L.fibra(laco, produtor, [5])
L.fibra(laco, consumidor)
L.rodar(laco)
out log
'''


def _log(tmp_path, capacidade):
    r = rodar(tmp_path, PRODUTOR.replace("CAP", str(capacidade)))
    assert r.returncode == 0, r.stderr
    return r.stdout.strip().strip("[]").split(", ")


def test_canal_com_capacidade_limita_quanto_o_produtor_adianta(tmp_path):
    log = _log(tmp_path, 2)
    recebidos = [x for x in log if x.startswith("r")]
    assert recebidos == ["r1", "r2", "r3", "r4", "r5"]
    # Em nenhum ponto há mais de capacidade + 1 enviados sem receber.
    pendentes = 0
    for x in log:
        pendentes += 1 if x.startswith("e") else -1
        assert pendentes <= 3


def test_canal_sem_capacidade_e_um_encontro(tmp_path):
    log = _log(tmp_path, 0)
    pendentes = 0
    for x in log:
        pendentes += 1 if x.startswith("e") else -1
        assert pendentes <= 1


def test_enviar_em_canal_fechado_e_uma_falha_anotada(tmp_path):
    r = rodar(tmp_path, '''adopt Arcane.Laco as L
laco := L.novo()
c := L.canal(1)
c.fechar()
stream action f():
    emit L.enviar(c, 1)
L.fibra(laco, f)
L.rodar(laco)
out L.falhas(laco)[0]["erro"]
''')
    assert r.returncode == 0, r.stderr
    assert "closed channel" in r.stdout


def test_errno_depois_de_uma_chamada_que_falhou():
    if sys.platform.startswith("win"):
        pytest.skip("o 'open' da msvcrt nao e o do POSIX")
    C = get_module("Arcane.C")
    abrir = C["padrao"]().funcao("open", ["texto", "i32"], "i32")
    C["zerar_errno"]()
    assert abrir("/nao/existe/de/jeito/nenhum", 0) == -1
    erro = C["errno"]()
    assert erro["nome"] == "ENOENT" and erro["codigo"] > 0


def test_dot_desenha_os_blocos_e_as_arestas_rotuladas():
    Comp = get_module("Arcane.Compilador")
    fonte = "action f(x):\n    given x bigger 0:\n        yield 1\n    yield 2\n"
    texto = Comp["dot"](fonte, "f")
    assert texto.startswith("digraph fluxo {") and texto.rstrip().endswith("}")
    assert '[label="sim"]' in texto and '[label="nao"]' in texto
    assert "\\l" in texto and "\\\\l" not in texto


def test_dot_marca_o_codigo_que_nunca_roda():
    Comp = get_module("Arcane.Compilador")
    fonte = "action f():\n    yield 1\n    out \"nunca\"\n"
    assert "style=dashed" in Comp["dot"](fonte, "f")


def test_dominancia_da_juncao_e_do_laco():
    Comp = get_module("Arcane.Compilador")
    fonte = ("action f(x):\n    given x bigger 0:\n        y := 1\n"
             "    otherwise:\n        y := 2\n    cycle i from 1 to 3:\n"
             "        y += i\n    yield y\n")
    d = Comp["dominancia"](fonte, "f")
    # os dois ramos não dominam a junção; a entrada domina tudo
    assert all(0 in v for v in d["dominadores"].values())
    assert d["fronteira"]["1"] == d["fronteira"]["2"] != []
    juncao = d["fronteira"]["1"][0]
    assert d["imediato"][str(juncao)] == 0
