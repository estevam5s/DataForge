# -*- coding: utf-8 -*-
"""Arcane.Pipeline e Arcane.Qualidade — orquestração e qualidade.

O que se testa aqui não é "roda": é o que um pipeline precisa GARANTIR
quando algo dá errado, que é quando ele importa.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import ValueError_                          # noqa: E402
from dataforge.stdlib import get_module                           # noqa: E402

P = get_module("Arcane.Pipeline")
Q = get_module("Arcane.Qualidade")


# ═══════════════════════════════════════════════════════════
#  O DAG
# ═══════════════════════════════════════════════════════════

class TestOrdem:
    def test_respeita_as_dependencias(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "c", lambda ctx: 3, ["b"])
        P["etapa"](f, "a", lambda ctx: 1)
        P["etapa"](f, "b", lambda ctx: 2, ["a"])
        assert P["ordem"](f) == ["a", "b", "c"]

    def test_a_ordem_de_declaracao_desempata(self):
        """Sem isso, a mesma lista rodaria em ordens diferentes.

        Um bug que só aparece numa das ordens seria irreproduzível.
        """
        f = P["fluxo"]("t")
        for nome in ("z", "m", "a"):
            P["etapa"](f, nome, lambda ctx: 1)
        assert P["ordem"](f) == ["z", "m", "a"]

    def test_ciclo_e_erro_e_nao_aviso(self):
        """Um ciclo não tem ordem possível; escolher uma seria mentira."""
        f = P["fluxo"]("t")
        P["etapa"](f, "x", lambda ctx: 1, ["y"])
        P["etapa"](f, "y", lambda ctx: 2, ["x"])
        with pytest.raises(ValueError_) as e:
            P["ordem"](f)
        assert "dependem umas das outras" in str(e.value)

    def test_dependencia_que_nao_existe_e_apanhada_antes_de_rodar(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "a", lambda ctx: 1, ["fantasma"])
        with pytest.raises(ValueError_) as e:
            P["rodar"](f)
        assert "fantasma" in str(e.value)

    def test_nome_repetido_e_recusado(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "a", lambda ctx: 1)
        with pytest.raises(ValueError_):
            P["etapa"](f, "a", lambda ctx: 2)


# ═══════════════════════════════════════════════════════════
#  O que acontece quando falha
# ═══════════════════════════════════════════════════════════

class TestFalha:
    def _fluxo_que_quebra(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "a", lambda ctx: 1)
        P["etapa"](f, "b", lambda ctx: (_ for _ in ()).throw(RuntimeError("caiu")),
                   ["a"])
        P["etapa"](f, "c", lambda ctx: 3, ["b"])
        P["etapa"](f, "solta", lambda ctx: 9)
        return f

    def test_quem_depende_e_pulado_e_nao_executado(self):
        """Rodar com entrada faltando produz dado corrompido.

        Dado corrompido é pior que dado ausente: o ausente alguém nota.
        """
        r = P["rodar"](self._fluxo_que_quebra())
        estados = {e["etapa"]: e["estado"] for e in r["etapas"]}
        assert estados["b"] == "falhou"
        assert estados["c"] == "pulada"

    def test_o_que_nao_depende_continua_rodando(self):
        r = P["rodar"](self._fluxo_que_quebra())
        estados = {e["etapa"]: e["estado"] for e in r["etapas"]}
        assert estados["solta"] == "ok"

    def test_o_relatorio_diz_por_que_pulou(self):
        r = P["rodar"](self._fluxo_que_quebra())
        pulada = next(e for e in r["etapas"] if e["etapa"] == "c")
        assert "b" in pulada["motivo"]

    def test_a_mensagem_do_erro_chega_ao_relatorio(self):
        r = P["rodar"](self._fluxo_que_quebra())
        falha = next(e for e in r["etapas"] if e["etapa"] == "b")
        assert "caiu" in falha["motivo"]
        assert falha["tipo_do_erro"] == "RuntimeError"

    def test_etapa_opcional_nao_derruba_o_fluxo(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "a", lambda ctx: (_ for _ in ()).throw(RuntimeError("x")),
                   [], 1, 0, None, True)
        assert P["rodar"](f)["ok"]


class TestRetry:
    def test_insiste_e_registra_quantas_vezes(self):
        estado = {"n": 0}

        def instavel(ctx):
            estado["n"] += 1
            if estado["n"] < 3:
                raise RuntimeError("rede")
            return "ok"

        f = P["fluxo"]("t")
        P["etapa"](f, "i", instavel, [], 3, 0.001)
        r = P["rodar"](f)
        assert r["ok"]
        assert r["etapas"][0]["tentativas"] == 3

    def test_desiste_depois_do_teto(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "i", lambda ctx: (_ for _ in ()).throw(RuntimeError("x")),
                   [], 2, 0.001)
        r = P["rodar"](f)
        assert not r["ok"]
        assert r["etapas"][0]["tentativas"] == 2


class TestCondicao:
    def test_quando_falso_salta_a_etapa(self):
        f = P["fluxo"]("t")
        P["etapa"](f, "a", lambda ctx: 1, [], 1, 0, lambda ctx: False)
        r = P["rodar"](f)
        assert r["etapas"][0]["estado"] == "saltada"
        assert r["ok"], "saltar não é falhar"


# ═══════════════════════════════════════════════════════════
#  Incremental — a garantia que mais importa
# ═══════════════════════════════════════════════════════════

class TestIncremental:
    def test_a_marca_sobrevive_entre_execucoes(self, tmp_path):
        arquivo = str(tmp_path / "e.json")
        f = P["fluxo"]("i", arquivo)
        P["etapa"](f, "a", lambda ctx: P["marcar"](f, "ate", 100))
        assert P["marca"](f, "ate") is None
        P["rodar"](f)

        outro = P["fluxo"]("i", arquivo)
        assert P["marca"](outro, "ate") == 100

    def test_a_marca_nao_avanca_quando_a_execucao_falha(self, tmp_path):
        """É a garantia que evita perda silenciosa de dado.

        Avançar depois de uma falha deixaria a marca à frente do que foi
        carregado — e o que ficou no meio some, sem ninguém notar.
        """
        arquivo = str(tmp_path / "e.json")
        f = P["fluxo"]("i", arquivo)
        P["etapa"](f, "avanca", lambda ctx: P["marcar"](f, "ate", 999))
        P["etapa"](f, "quebra",
                   lambda ctx: (_ for _ in ()).throw(RuntimeError("x")),
                   ["avanca"])
        P["rodar"](f)

        outro = P["fluxo"]("i", arquivo)
        assert P["marca"](outro, "ate") is None

    def test_estado_corrompido_nao_impede_de_rodar(self, tmp_path):
        """Reprocessar demais é ruim; não rodar é pior."""
        arquivo = tmp_path / "e.json"
        arquivo.write_text("{isto não é json", encoding="utf-8")
        f = P["fluxo"]("i", str(arquivo))
        P["etapa"](f, "a", lambda ctx: 1)
        assert P["rodar"](f)["ok"]

    def test_esquecer_a_marca_faz_reprocessar(self, tmp_path):
        arquivo = str(tmp_path / "e.json")
        f = P["fluxo"]("i", arquivo)
        P["marcar"](f, "ate", 5)
        f.gravar()
        P["esquecer_marca"](f, "ate")
        assert P["marca"](P["fluxo"]("i", arquivo), "ate") is None


class TestRodarAte:
    def test_roda_so_o_que_o_alvo_precisa(self):
        f = P["fluxo"]("t")
        for nome, deps in (("a", []), ("b", ["a"]), ("c", ["b"]), ("z", [])):
            P["etapa"](f, nome, lambda ctx: 1, deps)
        r = P["rodar_ate"](f, "b")
        assert {e["etapa"] for e in r["etapas"]} == {"a", "b"}


# ═══════════════════════════════════════════════════════════
#  Qualidade
# ═══════════════════════════════════════════════════════════

LINHAS = [
    {"id": 1, "nome": "Ana", "valor": 10.0, "email": "a@b.co"},
    {"id": 2, "nome": "Bo", "valor": 20.0, "email": "c@d.co"},
    {"id": 2, "nome": "", "valor": -5.0, "email": "nao-e-email"},
]

REGRAS = {
    "id": {"obrigatorio": True, "tipo": "inteiro", "unico": True},
    "nome": {"obrigatorio": True, "tipo": "texto", "minimo": 2},
    "valor": {"tipo": "numero", "minimo": 0},
    "email": {"formato": "email"},
}


class TestConferir:
    def test_acha_as_quatro_violacoes(self):
        r = Q["conferir"](LINHAS, REGRAS)
        assert not r["ok"]
        assert r["violacoes"] == 4
        assert set(r["por_campo"]) == {"id", "nome", "valor", "email"}

    def test_cada_violacao_diz_linha_campo_valor_e_motivo(self):
        """'falhou' leva a abrir o arquivo; isto leva a uma decisão."""
        r = Q["conferir"](LINHAS, REGRAS)
        v = r["por_campo"]["email"]["exemplos"][0]
        assert v["linha"] == 2
        assert v["valor"] == "nao-e-email"
        assert "email" in v["problema"]

    def test_a_taxa_boa_e_por_linha_e_nao_por_violacao(self):
        """Quatro violações numa linha só é 1 linha ruim, não 4.

        A distinção decide se o pipeline para: 4 violações espalhadas
        por 4 linhas de mil é outra coisa que 4 numa linha só.
        """
        r = Q["conferir"](LINHAS, REGRAS)
        assert r["violacoes"] == 4
        assert r["linhas_com_problema"] == 1
        assert r["taxa_boa"] == pytest.approx(2 / 3, abs=0.01)

    def test_o_repetido_e_marcado_na_segunda_ocorrencia(self):
        """A primeira é a original — é a mesma regra de 'sem_duplicadas'."""
        r = Q["conferir"](LINHAS, {"id": {"unico": True}})
        assert [e["linha"] for e in r["por_campo"]["id"]["exemplos"]] == [2]

    def test_dado_limpo_passa(self):
        assert Q["conferir"](LINHAS[:2], REGRAS)["ok"]

    def test_texto_so_com_espaco_conta_como_vazio(self):
        """Passou por 'não é void' e mesmo assim não tem dado."""
        r = Q["conferir"]([{"nome": "   "}], {"nome": {"obrigatorio": True}})
        assert not r["ok"]

    def test_unico_aponta_onde_ja_tinha_aparecido(self):
        r = Q["conferir"](LINHAS, {"id": {"unico": True}})
        assert "linha 1" in r["por_campo"]["id"]["exemplos"][0]["problema"]

    def test_booleano_nao_passa_por_inteiro(self):
        r = Q["conferir"]([{"n": True}], {"n": {"tipo": "inteiro"}})
        assert not r["ok"]


class TestEsperar:
    def test_levanta_abaixo_do_minimo(self):
        with pytest.raises(ValueError_) as e:
            Q["esperar"](LINHAS, REGRAS, 1.0)
        assert "qualidade abaixo do mínimo" in str(e.value)

    def test_tolera_o_que_o_minimo_permite(self):
        """Parar por 0,1% de e-mails inválidos costuma ser pior."""
        assert Q["esperar"](LINHAS, REGRAS, 0.3)["linhas"] == 3


class TestPerfil:
    def test_mede_sem_regra_nenhuma(self):
        p = Q["perfil"](LINHAS)
        assert p["linhas"] == 3
        assert p["campos"]["nome"]["vazios"] == 1
        assert p["campos"]["valor"]["minimo"] == -5.0

    def test_acha_o_campo_que_parece_chave(self):
        p = Q["perfil"]([{"id": i} for i in range(10)])
        assert p["campos"]["id"].get("parece_chave")

    def test_aponta_tipo_misto(self):
        """Quase sempre é defeito de origem — CSV lido sem esquema."""
        p = Q["perfil"]([{"v": 1}, {"v": "dois"}])
        assert p["campos"]["v"]["tipo_misto"]

    def test_lista_vazia_nao_estoura(self):
        assert Q["perfil"]([])["linhas"] == 0


class TestLimpeza:
    def test_sem_duplicadas_mantem_a_primeira(self):
        """Em dado de origem, a primeira é a original."""
        r = Q["sem_duplicadas"](LINHAS, ["id"])
        assert len(r) == 2
        assert r[1]["nome"] == "Bo"

    def test_so_validas_filtra(self):
        assert len(Q["so_validas"](LINHAS, REGRAS)) == 2

    def test_preencher_nao_toca_no_que_veio(self):
        r = Q["preencher"]([{"a": 1, "b": None}], {"b": 0, "a": 99})
        assert r[0] == {"a": 1, "b": 0}

    def test_duplicadas_agrupa_as_linhas(self):
        d = Q["duplicadas"](LINHAS, ["id"])
        assert len(d) == 1 and d[0]["linhas"] == [1, 2]

    def test_unicidade_de_uma_chave_e_um(self):
        assert Q["unicidade"](LINHAS[:2], "id") == 1.0
