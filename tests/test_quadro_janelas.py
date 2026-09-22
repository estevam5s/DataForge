"""As janelas do Quadro — média móvel, acumulado, defasagem, variação, posição.

O que se confere aqui é a DECISÃO sobre a ausência e sobre as pontas,
porque é nela que uma série erra calada: a média de um valor só fingindo
ser a média de sete, o zero que virou "crescimento de 100%", o vendedor
sem venda aparecendo em último.
"""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

Q = get_module("Arcane.Quadro")


def _q(valores):
    return Q["de_vaults"]([{"i": i, "v": v} for i, v in enumerate(valores)])


def _col(q, nome):
    return q.coluna(nome)


def test_janela_so_responde_com_valores_suficientes():
    q = _q([10, 20, 30, 40]).janela("v", 3)
    assert _col(q, "v_media_3") == [None, None, 20, 30]


def test_janela_com_minimo_aceita_menos_de_proposito():
    q = _q([10, 20, 30]).janela("v", 3, "soma", minimo=1)
    assert _col(q, "v_soma_3") == [10, 30, 60]


def test_janela_pula_a_ausencia_e_exige_o_tamanho_em_valores_validos():
    q = _q([10, None, 30, 50]).janela("v", 2)
    assert _col(q, "v_media_2") == [None, None, None, 40]


def test_agregacao_desconhecida_e_recusada_com_a_lista():
    with pytest.raises(Exception) as e:
        _q([1]).janela("v", 2, "mediano")
    assert "mediana" in str(e.value)


def test_acumulado_pula_a_ausencia_sem_zerar():
    q = _q([5, None, 10]).acumulado("v")
    assert _col(q, "v_soma_acumulado") == [5, 5, 15]
    q = _q([3, 9, 4]).acumulado("v", "maximo")
    assert _col(q, "v_maximo_acumulado") == [3, 9, 9]


def test_defasar_para_tras_e_para_frente_sem_repetir_a_ponta():
    q = _q([1, 2, 3]).defasar("v").defasar("v", -1)
    assert _col(q, "v_antes_1") == [None, 1, 2]
    assert _col(q, "v_depois_1") == [2, 3, None]


def test_variacao_percentual_e_absoluta_e_o_zero_nao_vira_infinito():
    q = _q([100, 110, 0, 50, None, 10]).variacao("v")
    assert _col(q, "v_variacao") == [None, 0.1, -1.0, None, None, None]
    q = _q([100, 110]).variacao("v", "d", percentual=False)
    assert _col(q, "d") == [None, 10]


def test_ranquear_minimo_denso_e_ausencia():
    q = _q([50, 80, 80, 10, None]).ranquear("v").ranquear("v", "denso", empates="denso")
    assert _col(q, "v_posicao") == [3, 1, 1, 4, None]
    assert _col(q, "denso") == [2, 1, 1, 3, None]
    q = _q([50, 80, 10]).ranquear("v", "asc", decrescente=False)
    assert _col(q, "asc") == [2, 3, 1]
    with pytest.raises(Exception):
        _q([1]).ranquear("v", empates="medio")


def test_coluna_que_nao_existe_e_erro_com_sugestao():
    with pytest.raises(Exception) as e:
        _q([1]).janela("vv", 2)
    assert "v" in str(e.value)


def test_o_quadro_original_nao_muda():
    q = _q([1, 2])
    q.janela("v", 1).acumulado("v")
    assert q.colunas() == ["i", "v"]
