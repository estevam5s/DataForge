"""Histórico (desfazer/refazer) e recurso (o dado que chega depois)."""
import os
import sys
import threading
import time

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

R = get_module("Arcane.Reativo")


def test_desfazer_e_refazer_andam_pelos_passos():
    s = R["sinal"]("")
    h = R["historico"](s)
    for v in ("a", "ab", "abc"):
        s.escrever(v)
    assert h.desfazer() and s.ler() == "ab"
    assert h.desfazer() and s.ler() == "a"
    assert h.refazer() and s.ler() == "ab"
    assert h.passos() == {"desfazer": 2, "refazer": 1}


def test_escrever_depois_de_desfazer_apaga_o_refazer():
    s = R["sinal"](0)
    h = R["historico"](s)
    s.escrever(1)
    s.escrever(2)
    h.desfazer()
    s.escrever(9)
    assert not h.pode_refazer() and h.passos()["desfazer"] == 2


def test_um_lote_e_um_passo_so():
    s = R["sinal"](0)
    h = R["historico"](s)

    def colar():
        s.escrever(1)
        s.escrever(2)
        s.escrever(3)

    R["lote"](colar)
    assert s.ler() == 3 and h.passos()["desfazer"] == 1
    h.desfazer()
    assert s.ler() == 0


def test_nada_a_desfazer_devolve_no_e_o_limite_descarta_o_mais_velho():
    s = R["sinal"](0)
    h = R["historico"](s, 2)
    assert h.desfazer() is False
    for v in (1, 2, 3):
        s.escrever(v)
    assert h.passos()["desfazer"] == 2
    h.desfazer()
    h.desfazer()
    assert s.ler() == 1 and h.desfazer() is False


def test_historico_de_derivado_e_recusado():
    s = R["sinal"](1)
    with pytest.raises(Exception, match="de um sinal"):
        R["historico"](R["derivado"](lambda: s.ler() * 2))


def test_recurso_chega_pronto():
    r = R["recurso"](lambda: 42)
    assert r.aguardar(2) == {"estado": "pronto", "valor": 42, "erro": None}


def test_recurso_que_falha_fica_em_erro():
    def falhar():
        raise ValueError("fora do ar")
    final = R["recurso"](falhar).aguardar(2)
    assert final["estado"] == "erro" and "fora do ar" in final["erro"]


def test_a_resposta_velha_e_descartada():
    """A busca lenta de 'a' chega depois da de 'ab' — e não pode vencer."""
    termo = R["sinal"]("a")
    liberar_a = threading.Event()

    def buscar(t):
        if t == "a":
            liberar_a.wait(2)
        return f"resultado de {t}"

    r = R["recurso"](buscar, termo)
    termo.escrever("ab")
    assert r.aguardar(2)["valor"] == "resultado de ab"
    liberar_a.set()
    time.sleep(0.2)
    assert r.ler()["valor"] == "resultado de ab"
    assert r.descartadas() == 1


def test_estado_e_um_sinal_que_um_derivado_pode_ler():
    r = R["recurso"](lambda: 7)
    rotulo = R["derivado"](lambda: r.estado().ler()["estado"])
    r.aguardar(2)
    assert rotulo.ler() == "pronto"
