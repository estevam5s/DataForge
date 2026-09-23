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


# ═══════════════════════════════════════════════════════════
#  Partição — a pergunta certa
# ═══════════════════════════════════════════════════════════
#
# Sem partição, TODA função de janela responde a pergunta errada no
# caso mais comum que existe. "Média móvel de sete dias **por loja**"
# atravessava a fronteira das lojas: a primeira venda da loja B entrava
# com as três últimas da loja A. O resultado é um número plausível, sem
# erro nenhum — que é a forma mais cara de estar errado.

def _vendas():
    return Q["de_vaults"]([
        {"loja": "sul", "dia": 1, "v": 10},
        {"loja": "norte", "dia": 1, "v": 100},
        {"loja": "sul", "dia": 2, "v": 20},
        {"loja": "norte", "dia": 2, "v": 200},
        {"loja": "sul", "dia": 3, "v": 30},
    ])


def test_o_acumulado_sem_particao_atravessa_os_grupos():
    """O número que a versão anterior entregava — para ficar registrado
    o que mudou, e para a diferença ser visível."""
    assert _vendas().acumulado("v").coluna("v_soma_acumulado") == [10, 110, 130, 330, 360]


def test_o_acumulado_COM_particao_conta_dentro_do_grupo():
    q = _vendas().acumulado("v", "soma", None, "loja")
    assert q.coluna("v_soma_acumulado") == [10, 100, 30, 300, 60]


def test_a_ordem_das_linhas_e_preservada():
    """A coluna nova volta na posição ORIGINAL, e não agrupada: um
    quadro reordenado pela janela quebraria o `com`, que casa por
    posição."""
    q = _vendas().acumulado("v", "soma", None, "loja")
    assert q.coluna("loja") == ["sul", "norte", "sul", "norte", "sul"]
    assert q.coluna("dia") == [1, 1, 2, 2, 3]


def test_janela_por_grupo():
    q = _vendas().janela("v", 2, "media", None, None, "loja")
    # sul: void, 15, 25   |   norte: void, 150
    assert q.coluna("v_media_2") == [None, None, 15.0, 150.0, 25.0]


def test_defasar_por_grupo_nao_pega_a_linha_do_outro():
    q = _vendas().defasar("v", 1, None, "loja")
    assert q.coluna("v_antes_1") == [None, None, 10, 100, 20]


def test_variacao_por_grupo():
    q = _vendas().variacao("v", None, False, "loja")
    assert q.coluna("v_variacao") == [None, None, 10, 100, 10]


def test_ranquear_por_grupo_da_o_ranking_DENTRO_do_grupo():
    """Um ranking global responde "quem vendeu mais no total"; o que
    quase sempre se quer é "quem é o primeiro **da sua categoria**"."""
    q = _vendas().ranquear("v", None, True, "minimo", "loja")
    # sul: 30>20>10 → 3, 2, 1   |   norte: 200>100 → 2, 1
    assert q.coluna("v_posicao") == [3, 2, 2, 1, 1]


def test_a_particao_aceita_VARIAS_colunas():
    q = Q["de_vaults"]([
        {"a": "x", "b": 1, "v": 1},
        {"a": "x", "b": 1, "v": 2},
        {"a": "x", "b": 2, "v": 10},
        {"a": "y", "b": 1, "v": 100},
    ]).acumulado("v", "soma", None, ["a", "b"])
    assert q.coluna("v_soma_acumulado") == [1, 3, 10, 100]


def test_particionar_por_coluna_que_nao_existe_e_erro_com_sugestao():
    """Devolver a coluna inteira sem particionar seria o silêncio que
    esta correção existe para acabar."""
    with pytest.raises(Exception) as info:
        _vendas().acumulado("v", "soma", None, "lojja")
    assert "lojja" in str(info.value)


def test_a_ausencia_continua_sendo_pulada_dentro_do_grupo():
    q = Q["de_vaults"]([
        {"g": "a", "v": 10},
        {"g": "a", "v": None},
        {"g": "a", "v": 30},
        {"g": "b", "v": 5},
    ]).acumulado("v", "soma", None, "g")
    assert q.coluna("v_soma_acumulado") == [10, 10, 40, 5]


# ═══════════════════════════════════════════════════════════
#  A cardinalidade da junção
# ═══════════════════════════════════════════════════════════
#
# O desastre mais caro da engenharia de dados: uma tabela de apoio com
# a chave DUPLICADA multiplica as linhas do fato, e o total sobe sem
# nada acusar. Medido no caso pequeno abaixo: duas vendas somando 30
# viram três linhas somando **40**.

def _vendas_e_clientes(duplicado):
    vendas = Q["de_vaults"]([{"cli": "a", "v": 10}, {"cli": "b", "v": 20}])
    linhas = [{"cli": "a", "nome": "Ana"}, {"cli": "b", "nome": "Bia"}]
    if duplicado:
        linhas.insert(1, {"cli": "a", "nome": "Ana (duplicada)"})
    return vendas, Q["de_vaults"](linhas)


def test_a_duplicata_do_apoio_INFLA_o_total_quando_ninguem_declara():
    """O comportamento de sempre, registrado: sem declarar nada, a
    junção continua permissiva — e é por isso que declarar importa."""
    vendas, clientes = _vendas_e_clientes(duplicado=True)
    junto = vendas.juntar(clientes, "cli")
    assert junto.altura() == 3
    assert sum(junto.coluna("v")) == 40        # eram 30


def test_declarar_muitos_para_um_RECUSA_a_duplicata():
    vendas, clientes = _vendas_e_clientes(duplicado=True)
    with pytest.raises(Exception) as info:
        vendas.juntar(clientes, "cli", "dentro", "muitos_para_um")
    assert "muitos_para_um" in str(info.value)
    assert "2 vezes do outro lado" in str(info.value)
    assert "sem_duplicadas" in info.value.dica


def test_a_junção_limpa_passa_com_a_mesma_declaracao():
    vendas, clientes = _vendas_e_clientes(duplicado=False)
    junto = vendas.juntar(clientes, "cli", "dentro", "muitos_para_um")
    assert junto.altura() == 2
    assert sum(junto.coluna("v")) == 30


def test_um_para_muitos_olha_o_lado_de_CA():
    esquerda = Q["de_vaults"]([{"k": 1, "a": "x"}, {"k": 1, "a": "y"}])
    direita = Q["de_vaults"]([{"k": 1, "b": "z"}])
    with pytest.raises(Exception) as info:
        esquerda.juntar(direita, "k", "dentro", "um_para_muitos")
    assert "deste lado" in str(info.value)


def test_um_para_um_cobra_os_dois_lados():
    esquerda = Q["de_vaults"]([{"k": 1}, {"k": 1}])
    direita = Q["de_vaults"]([{"k": 1, "b": 1}])
    with pytest.raises(Exception):
        esquerda.juntar(direita, "k", "dentro", "um_para_um")


def test_muitos_para_muitos_e_a_permissiva_declarada():
    """Declarar que a explosão é esperada é diferente de não dizer
    nada: quem lê o código sabe que alguém pensou nisso."""
    vendas, clientes = _vendas_e_clientes(duplicado=True)
    assert vendas.juntar(clientes, "cli", "dentro",
                         "muitos_para_muitos").altura() == 3


def test_uma_cardinalidade_que_nao_existe_e_recusada_com_a_lista():
    vendas, clientes = _vendas_e_clientes(duplicado=False)
    with pytest.raises(Exception) as info:
        vendas.juntar(clientes, "cli", "dentro", "um_pra_um")
    assert "nao e uma cardinalidade" in str(info.value)
    # A lista das que existem vai na NOTA: quem errou o nome precisa
    # dela, e procurá-la na documentação é o caminho longo.
    assert "um_para_um" in info.value.nota
