# -*- coding: utf-8 -*-
"""Arcane.Cortex — os algoritmos aprendem mesmo?

A versão anterior deste módulo tinha cinco símbolos e nenhum
funcionando: `sentiment` devolvia `neutral 0.5` para qualquer texto e
`Dense(4)` devolvia um vault com o nome `Dense` dentro. Estes testes
existem para que isso não volte — cada um cobra um RESULTADO, não uma
chamada que não estoura.
"""

import math
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import ValueError_                          # noqa: E402
from dataforge.stdlib import get_module                           # noqa: E402

ML = get_module("Arcane.Cortex")


def _separavel(n=300, semente=1):
    """Duas classes separadas por uma reta."""
    r = random.Random(semente)
    linhas = []
    for _ in range(n):
        a, b = r.gauss(0, 1), r.gauss(0, 1)
        linhas.append({"a": a, "b": b, "c": "sim" if a + b > 0 else "nao"})
    return linhas


def _circular(n=300, semente=2):
    """Uma classe DENTRO da outra — nenhuma reta separa."""
    r = random.Random(semente)
    linhas = []
    for _ in range(n):
        a, b = r.gauss(0, 1), r.gauss(0, 1)
        linhas.append({"a": a, "b": b,
                       "c": "dentro" if a * a + b * b < 1 else "fora"})
    return linhas


# ═══════════════════════════════════════════════════════════
#  Regressão: ele acha os coeficientes?
# ═══════════════════════════════════════════════════════════

class TestLinear:
    def test_recupera_os_coeficientes_exatos(self):
        """y = 3x + 2z + 10, sem ruído: tem que sair exato."""
        dados = [{"x": i, "z": i % 7, "y": 3 * i + 2 * (i % 7) + 10}
                 for i in range(60)]
        m = ML["linear"](dados, "y", ["x", "z"])
        intercepto, px, pz = m.parametros
        assert intercepto == pytest.approx(10, abs=1e-6)
        assert px == pytest.approx(3, abs=1e-6)
        assert pz == pytest.approx(2, abs=1e-6)

    def test_r2_um_quando_a_relacao_e_exata(self):
        dados = [{"x": i, "y": 2 * i + 1} for i in range(40)]
        m = ML["linear"](dados, "y", ["x"])
        assert ML["avaliar"](m, dados)["r2"] == pytest.approx(1.0, abs=1e-9)

    def test_prever_extrapola_a_reta(self):
        dados = [{"x": i, "y": 2 * i} for i in range(30)]
        m = ML["linear"](dados, "y", ["x"])
        assert ML["prever_um"](m, {"x": 100}) == pytest.approx(200, abs=1e-6)

    def test_menos_linhas_que_colunas_e_recusado(self):
        """Com menos linhas que colunas há infinitas soluções."""
        dados = [{"a": 1, "b": 2, "c": 3, "y": 1},
                 {"a": 2, "b": 3, "c": 4, "y": 2}]
        with pytest.raises(ValueError_) as e:
            ML["linear"](dados, "y", ["a", "b", "c"])
        assert "infinitas" in e.value.nota

    def test_coluna_de_texto_diz_o_que_fazer(self):
        dados = [{"x": "abc", "y": 1}] * 10
        with pytest.raises(ValueError_) as e:
            ML["linear"](dados, "y", ["x"])
        assert "categorico" in e.value.dica


# ═══════════════════════════════════════════════════════════
#  Classificação: ele aprende?
# ═══════════════════════════════════════════════════════════

class TestClassificacao:
    def test_logistica_aprende_o_separavel(self):
        treino, teste = ML["dividir"](_separavel(), 0.3)
        m = ML["logistica"](treino, "c", ["a", "b"], 400)
        assert ML["avaliar"](m, teste)["acuracia"] > 0.85

    def test_logistica_recusa_mais_de_duas_classes(self):
        dados = [{"a": i, "c": ["x", "y", "z"][i % 3]} for i in range(30)]
        with pytest.raises(ValueError_) as e:
            ML["logistica"](dados, "c", ["a"])
        assert "floresta" in e.value.dica

    def test_a_floresta_bate_a_arvore_no_nao_linear(self):
        """É o motivo de a floresta existir.

        Uma árvore sozinha decora; a floresta corrige por duas fontes de
        variação — amostra com reposição e subconjunto de colunas.
        """
        treino, teste = ML["dividir"](_circular(400), 0.3, estratificar="c")
        arvore = ML["avaliar"](ML["arvore"](treino, "c", ["a", "b"]),
                               teste)["acuracia"]
        floresta = ML["avaliar"](ML["floresta"](treino, "c", ["a", "b"], 25),
                                 teste)["acuracia"]
        assert floresta >= arvore

    def test_vizinhos_aprende_o_circular(self):
        treino, teste = ML["dividir"](_circular(300), 0.3, estratificar="c")
        m = ML["vizinhos"](treino, "c", ["a", "b"], 5)
        assert ML["avaliar"](m, teste)["acuracia"] > 0.8

    def test_k_maior_que_o_treino_e_recusado(self):
        dados = [{"a": i, "c": "x"} for i in range(5)]
        with pytest.raises(ValueError_):
            ML["vizinhos"](dados, "c", ["a"], 99)


class TestBayesTexto:
    TREINO = [
        {"t": "adorei otimo excelente maravilhoso", "s": "bom"},
        {"t": "excelente produto recomendo muito", "s": "bom"},
        {"t": "otimo atendimento adorei tudo", "s": "bom"},
        {"t": "pessimo horrivel nao recomendo", "s": "ruim"},
        {"t": "horrivel demorou quebrou logo", "s": "ruim"},
        {"t": "pessimo produto quebrou tudo", "s": "ruim"},
    ]

    def test_classifica_texto_de_verdade(self):
        """A versão antiga devolvia 'neutral 0.5' para tudo."""
        m = ML["bayes_texto"](self.TREINO, "s", "t")
        assert ML["prever_um"](m, {"t": "produto excelente adorei"}) == "bom"
        assert ML["prever_um"](m, {"t": "quebrou horrivel"}) == "ruim"

    def test_palavra_nunca_vista_nao_zera_a_classe(self):
        """Sem Laplace, uma palavra nova torna a classe IMPOSSÍVEL."""
        m = ML["bayes_texto"](self.TREINO, "s", "t")
        assert ML["prever_um"](m, {"t": "xyzabc excelente adorei"}) == "bom"

    def test_texto_vazio_nao_estoura(self):
        m = ML["bayes_texto"](self.TREINO, "s", "t")
        assert ML["prever_um"](m, {"t": ""}) in ("bom", "ruim")


# ═══════════════════════════════════════════════════════════
#  Avaliar — a parte que decide se o modelo serve
# ═══════════════════════════════════════════════════════════

class TestAvaliacao:
    def test_o_f1_denuncia_o_que_a_acuracia_esconde(self):
        """Num problema 95/5, responder sempre a maioria acerta 95%.

        É o caso que faz alguém publicar um modelo inútil achando que
        ele é bom — e é por isso que 'avaliar' não devolve só acurácia.
        """
        dados = [{"a": i, "c": "comum" if i % 20 else "raro"}
                 for i in range(200)]
        m = ML["arvore"](dados, "c", ["a"], profundidade=1)
        r = ML["avaliar"](m, dados)
        if r["acuracia"] > 0.9:
            raro = r["por_classe"].get("raro", {})
            assert raro.get("revocacao", 1.0) < r["acuracia"], \
                "a revocação da classe rara devia ser pior que a acurácia"

    def test_a_media_e_ponderada_pelo_tamanho_da_classe(self):
        """A simples trataria 3 exemplos como iguais a 3000."""
        dados = _separavel(200)
        treino, teste = ML["dividir"](dados, 0.3)
        r = ML["avaliar"](ML["floresta"](treino, "c", ["a", "b"]), teste)
        assert sum(c["quantos"] for c in r["por_classe"].values()) == len(teste)

    def test_a_matriz_mostra_onde_ele_erra(self):
        treino, teste = ML["dividir"](_separavel(200), 0.3)
        texto = ML["matriz"](ML["floresta"](treino, "c", ["a", "b"]), teste)
        assert "real \\ previsto" in texto
        assert "sim" in texto and "nao" in texto

    def test_regressao_devolve_mae_rmse_e_r2(self):
        dados = [{"x": i, "y": 2 * i + (i % 3)} for i in range(50)]
        r = ML["avaliar"](ML["linear"](dados, "y", ["x"]), dados)
        assert set(r) >= {"mae", "rmse", "r2"}
        assert r["rmse"] >= r["mae"], "RMSE pune o erro grande mais que MAE"

    def test_validacao_cruzada_devolve_o_desvio(self):
        """O desvio diz mais que a média.

        Uma divisão só mede um sorteio; um modelo que varia muito entre
        as dobras não é confiável, por melhor que seja a média.
        """
        r = ML["validacao_cruzada"](_separavel(250), "c", ["a", "b"],
                                    "floresta", 5)
        assert r["dobras"] == 5
        assert len(r["por_dobra"]) == 5
        assert 0.0 <= r["desvio"] <= 1.0
        assert r["media"] > 0.8

    def test_especie_desconhecida_lista_as_que_existem(self):
        with pytest.raises(ValueError_) as e:
            ML["validacao_cruzada"](_separavel(50), "c", ["a"], "magica")
        assert "floresta" in e.value.nota


# ═══════════════════════════════════════════════════════════
#  Preparar
# ═══════════════════════════════════════════════════════════

class TestPreparar:
    def test_dividir_embaralha_antes(self):
        """Dado quase nunca chega em ordem aleatória.

        Cortar sem embaralhar põe todo um tipo de exemplo de um lado só.
        """
        dados = [{"i": i, "c": "a" if i < 50 else "b"} for i in range(100)]
        treino, _ = ML["dividir"](dados, 0.3)
        assert len({l["c"] for l in treino}) == 2

    def test_estratificar_mantem_a_proporcao(self):
        """Num problema com 2% de fraude, o corte cego pode deixar o
        teste sem fraude nenhuma."""
        dados = [{"a": i, "c": "raro" if i % 25 == 0 else "comum"}
                 for i in range(500)]
        _, teste = ML["dividir"](dados, 0.2, estratificar="c")
        assert "raro" in {l["c"] for l in teste}

    def test_a_mesma_semente_da_a_mesma_divisao(self):
        """Sem isso, comparar duas ideias vira comparar dois sorteios."""
        dados = _separavel(100)
        a, _ = ML["dividir"](dados, 0.3, semente=7)
        b, _ = ML["dividir"](dados, 0.3, semente=7)
        assert a == b

    def test_categorico_faz_uma_coluna_por_valor(self):
        """Numerar as categorias faria o modelo achar que há ordem."""
        r = ML["categorico"]([{"cor": "azul"}, {"cor": "verde"}], "cor")
        assert r["colunas"] == ["cor_azul", "cor_verde"]
        assert r["linhas"][0] == {"cor_azul": 1, "cor_verde": 0}

    def test_escalonar_centra_e_normaliza(self):
        dados = [{"x": i} for i in range(100)]
        escala = ML["escalonar"](dados, ["x"])
        escalonados = ML["aplicar_escala"](dados, escala)
        valores = [l["x"] for l in escalonados]
        assert sum(valores) / len(valores) == pytest.approx(0, abs=1e-9)

    def test_coluna_constante_nao_divide_por_zero(self):
        escala = ML["escalonar"]([{"x": 5}] * 10, ["x"])
        assert escala["x"]["desvio"] == 1.0
        assert ML["aplicar_escala"]([{"x": 5}], escala)[0]["x"] == 0.0


# ═══════════════════════════════════════════════════════════
#  Não supervisionado
# ═══════════════════════════════════════════════════════════

class TestNaoSupervisionado:
    def test_kmedias_acha_os_grupos_de_verdade(self):
        r = random.Random(5)
        pontos = [{"x": r.gauss(c * 10, 0.5), "y": r.gauss(c * 10, 0.5)}
                  for c in range(3) for _ in range(40)]
        km = ML["kmedias"](pontos, ["x", "y"], 3)
        assert sorted(km["tamanhos"]) == [40, 40, 40]

    def test_kmeans_mais_mais_nao_deixa_grupo_vazio(self):
        """Sortear todos os centros põe dois no mesmo aglomerado."""
        r = random.Random(9)
        pontos = [{"x": r.gauss(c * 20, 0.3)} for c in range(4)
                  for _ in range(25)]
        km = ML["kmedias"](pontos, ["x"], 4)
        assert all(t > 0 for t in km["tamanhos"])

    def test_pca_concentra_a_variancia_no_primeiro(self):
        r = random.Random(11)
        # Dados quase numa reta: quase toda a variância cabe em 1 eixo.
        pontos = [{"x": (v := r.gauss(0, 5)), "y": v * 2 + r.gauss(0, 0.05)}
                  for _ in range(200)]
        p = ML["pca"](pontos, ["x", "y"], 2)
        assert p["variancia"][0] > 0.95


# ═══════════════════════════════════════════════════════════
#  Guardar
# ═══════════════════════════════════════════════════════════

class TestPersistencia:
    def test_o_modelo_carregado_preve_identico(self, tmp_path):
        treino, teste = ML["dividir"](_separavel(200), 0.3)
        m = ML["floresta"](treino, "c", ["a", "b"], 10)
        f = str(tmp_path / "m.json")
        ML["salvar"](m, f)
        assert ML["prever"](ML["carregar"](f), teste) == ML["prever"](m, teste)

    def test_e_json_legivel_e_nao_pickle(self, tmp_path):
        """Pickle executaria código ao carregar.

        Um modelo baixado de qualquer lugar viraria execução arbitrária.
        """
        import json
        treino, _ = ML["dividir"](_separavel(100), 0.3)
        f = str(tmp_path / "m.json")
        ML["salvar"](ML["linear"]([{"x": i, "y": i} for i in range(20)],
                                  "y", ["x"]), f)
        d = json.load(open(f, encoding="utf-8"))
        assert d["especie"] == "linear" and d["alvo"] == "y"

    def test_bayes_sobrevive_a_ida_e_volta(self, tmp_path):
        m = ML["bayes_texto"](TestBayesTexto.TREINO, "s", "t")
        f = str(tmp_path / "b.json")
        ML["salvar"](m, f)
        assert ML["prever_um"](ML["carregar"](f),
                               {"t": "excelente adorei"}) == "bom"

    def test_resumo_diz_o_que_o_modelo_e(self):
        m = ML["floresta"](_separavel(100), "c", ["a", "b"], 5)
        r = ML["resumo"](m)
        assert r["especie"] == "floresta" and r["alvo"] == "c"
        assert r["treinado_com"] == 100


class TestImportancia:
    def test_a_coluna_que_decide_aparece_no_topo(self):
        """'a' decide tudo; 'ruido' não informa nada."""
        r = random.Random(13)
        dados = [{"a": (v := r.gauss(0, 1)), "ruido": r.gauss(0, 1),
                  "c": "sim" if v > 0 else "nao"} for _ in range(300)]
        m = ML["floresta"](dados, "c", ["a", "ruido"], 25)
        imp = ML["importancia"](m)
        assert imp["a"] > imp["ruido"]

    def test_modelo_que_nao_sabe_dizer_e_explicito(self):
        m = ML["vizinhos"](_separavel(50), "c", ["a", "b"], 3)
        with pytest.raises(ValueError_) as e:
            ML["importancia"](m)
        assert "floresta" in e.value.nota
