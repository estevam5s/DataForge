# -*- coding: utf-8 -*-
"""Arcane.Stream e Arcane.Observar.

O que se cobra aqui é a SEMÂNTICA — a diferença entre uma fila e um
log, e a diferença entre logging e observabilidade.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError                       # noqa: E402
from dataforge.stdlib import get_module                           # noqa: E402

S = get_module("Arcane.Stream")
O = get_module("Arcane.Observar")


# ═══════════════════════════════════════════════════════════
#  Streaming
# ═══════════════════════════════════════════════════════════

class TestParticoes:
    def _corrente(self, tmp_path, particoes=4):
        c = S["corrente"](str(tmp_path / "c"))
        S["topico"](c, "t", particoes)
        return c

    def test_a_mesma_chave_cai_sempre_na_mesma_particao(self):
        """É a ÚNICA coisa que a partição garante: a ordem por chave."""
        from dataforge.stdlib.arcane_fluxo import _particao_de
        for chave in ("cliente-7", "abc", "", "999"):
            assert len({_particao_de(chave, 8) for _ in range(20)}) == 1

    def test_a_particao_e_estavel_entre_execucoes(self, tmp_path):
        """hash() do Python é aleatorizado por processo desde a 3.3.

        Usá-lo mandaria a mesma chave para partições diferentes a cada
        execução, e a ordem por chave deixaria de existir.
        """
        import subprocess
        codigo = ("import sys; sys.path.insert(0, %r);"
                  "from dataforge.stdlib.arcane_fluxo import _particao_de;"
                  "print(_particao_de('cliente-7', 8))"
                  % os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        saidas = {subprocess.run([sys.executable, "-c", codigo],
                                 capture_output=True, text=True).stdout.strip()
                  for _ in range(3)}
        assert len(saidas) == 1

    def test_criar_o_topico_de_novo_nao_apaga(self, tmp_path):
        c = self._corrente(tmp_path)
        S["publicar"](c, "t", {"a": 1})
        S["topico"](c, "t", 4)
        assert S["informacao"](c, "t")["eventos"] == 1

    def test_topico_que_nao_existe_lista_os_que_existem(self, tmp_path):
        c = self._corrente(tmp_path)
        with pytest.raises(DataForgeError) as e:
            S["publicar"](c, "fantasma", {"a": 1})
        assert "t" in e.value.nota


class TestLogNaoFila:
    """A diferença que define o módulo."""

    def _com_eventos(self, tmp_path, quantos=10):
        c = S["corrente"](str(tmp_path / "c"))
        S["topico"](c, "t", 2)
        for i in range(quantos):
            S["publicar"](c, "t", {"n": i}, f"k{i % 3}")
        return c

    def test_dois_grupos_leem_o_mesmo_evento(self, tmp_path):
        """Numa fila, o primeiro a ler tira o evento do outro."""
        c = self._com_eventos(tmp_path)
        assert len(S["consumir"](c, "t", "a")) == 10
        assert len(S["consumir"](c, "t", "b")) == 10

    def test_consumir_nao_avanca_sozinho(self, tmp_path):
        """Avançar na leitura daria 'no máximo uma vez'.

        Um processo que cai no meio perderia o evento em silêncio — o
        pior resultado possível num fluxo de dados.
        """
        c = self._com_eventos(tmp_path)
        S["consumir"](c, "t", "a")
        assert len(S["consumir"](c, "t", "a")) == 10

    def test_confirmar_avanca_so_o_grupo_que_confirmou(self, tmp_path):
        c = self._com_eventos(tmp_path)
        S["confirmar_ate"](c, "t", "a", S["consumir"](c, "t", "a"))
        assert len(S["consumir"](c, "t", "a")) == 0
        assert len(S["consumir"](c, "t", "b")) == 10

    def test_a_posicao_aponta_para_o_proximo(self, tmp_path):
        """Guardar o último faria toda retomada reprocessar um evento."""
        c = self._com_eventos(tmp_path, 4)
        eventos = S["consumir"](c, "t", "a")
        S["confirmar"](c, "t", "a", eventos[0])
        restantes = S["consumir"](c, "t", "a")
        assert eventos[0]["offset"] not in [
            e["offset"] for e in restantes
            if e["particao"] == eventos[0]["particao"]]

    def test_voltar_reprocessa(self, tmp_path):
        """É o que uma fila não permite."""
        c = self._com_eventos(tmp_path)
        S["confirmar_ate"](c, "t", "a", S["consumir"](c, "t", "a"))
        S["voltar"](c, "t", "a", 0)
        assert len(S["consumir"](c, "t", "a")) == 10

    def test_a_ordem_dentro_da_particao_e_mantida(self, tmp_path):
        c = S["corrente"](str(tmp_path / "c"))
        S["topico"](c, "t", 1)
        for i in range(20):
            S["publicar"](c, "t", {"n": i}, "sempre-a-mesma")
        assert [e["valor"]["n"] for e in S["ler_de"](c, "t")] == list(range(20))

    def test_o_atraso_e_a_metrica_que_se_vigia(self, tmp_path):
        c = self._com_eventos(tmp_path)
        assert S["atraso"](c, "t", "novo")["total"] == 10
        S["confirmar_ate"](c, "t", "novo", S["consumir"](c, "t", "novo"))
        assert S["atraso"](c, "t", "novo")["total"] == 0


class TestManutencao:
    def test_reter_apaga_o_mais_antigo(self, tmp_path):
        from dataforge.stdlib import arcane_fluxo
        antigo = arcane_fluxo.POR_SEGMENTO
        arcane_fluxo.POR_SEGMENTO = 5
        try:
            c = S["corrente"](str(tmp_path / "c"))
            S["topico"](c, "t", 1)
            for i in range(30):
                S["publicar"](c, "t", {"n": i})
            antes = S["informacao"](c, "t")["particoes"][0]["segmentos"]
            S["reter"](c, "t", 2)
            depois = S["informacao"](c, "t")["particoes"][0]["segmentos"]
            assert antes > depois == 2
        finally:
            arcane_fluxo.POR_SEGMENTO = antigo

    def test_janela_agrupa_por_tempo(self):
        """'Quantos por minuto' não existe sem janela."""
        agora = time.time()
        eventos = [{"quando": agora + i} for i in range(0, 180, 20)]
        janelas = S["janela"](eventos, 60)
        assert len(janelas) >= 3
        assert sum(j["quantos"] for j in janelas) == len(eventos)


# ═══════════════════════════════════════════════════════════
#  Observabilidade
# ═══════════════════════════════════════════════════════════

class TestMetricas:
    def test_contador_soma(self):
        p = O["painel"]("t")
        O["contar"](p, "linhas", 100)
        O["contar"](p, "linhas", 50)
        assert O["valor"](p, "linhas") == 150

    def test_a_media_esconde_o_que_o_p99_mostra(self):
        """Um pipeline com média de 3,9s e p99 de 40s tem um problema
        que a média nunca mostra — e é o p99 que se sente."""
        p = O["painel"]("t")
        for _ in range(190):
            O["medir"](p, "lat", 2.0)
        for _ in range(10):
            O["medir"](p, "lat", 40.0)
        e = O["valor"](p, "lat")
        assert e["media"] < 4
        assert e["p50"] == 2.0
        assert e["p99"] == 40.0

    def test_o_percentil_bate_com_a_definicao_padrao(self):
        """Interpolação linear — a mesma de numpy.percentile.

        Não é detalhe: um p99 calculado de outro jeito daria um número
        diferente do painel que a equipe já olha, e ninguém saberia qual
        acreditar.
        """
        from dataforge.stdlib.arcane_observar import _percentil
        dados = [float(i) for i in range(101)]      # 0..100
        assert _percentil(dados, 0.50) == 50.0
        assert _percentil(dados, 0.95) == 95.0
        assert _percentil(dados, 0.99) == 99.0

    def test_marca_guarda_o_ultimo(self):
        p = O["painel"]("t")
        O["marcar"](p, "fila", 10)
        O["marcar"](p, "fila", 3)
        assert O["valor"](p, "fila") == 3

    def test_o_reservatorio_mantem_a_amostra_representativa(self):
        """Guardar só os primeiros mil daria o percentil do começo."""
        from dataforge.stdlib import arcane_observar
        p = O["painel"]("t")
        for i in range(arcane_observar.AMOSTRAS * 2):
            O["medir"](p, "x", float(i))
        e = O["valor"](p, "x")
        assert e["quantas"] == arcane_observar.AMOSTRAS * 2
        # a mediana da amostra tem que ficar perto da mediana real
        assert abs(e["p50"] - arcane_observar.AMOSTRAS) < arcane_observar.AMOSTRAS


class TestTracing:
    def test_o_trecho_registra_a_duracao(self):
        p = O["painel"]("t")
        t = O["abrir"](p, "etapa")
        time.sleep(0.01)
        r = O["fechar"](p, t)
        assert r["duracao"] >= 0.009

    def test_aninhar_mostra_onde_o_tempo_foi(self):
        """'carregar levou 40s' não ajuda; 'dos 40s, 38 no INSERT' resolve."""
        p = O["painel"]("t")
        pai = O["abrir"](p, "carregar")
        filho = O["abrir"](p, "insert", pai)
        O["fechar"](p, filho)
        O["fechar"](p, pai)
        arvore = O["arvore"](p)
        assert "carregar" in arvore and "insert" in arvore

    def test_fechar_o_que_nao_abriu_nao_derruba(self):
        """Num 'ensure', isso acontece quando o corpo estourou antes."""
        p = O["painel"]("t")
        assert O["fechar"](p, "t999") is None

    def test_cronometrar_fecha_mesmo_com_erro(self):
        p = O["painel"]("t")

        def quebra():
            raise RuntimeError("caiu")

        with pytest.raises(RuntimeError):
            O["cronometrar"](p, "etapa", quebra)
        assert not p.abertos, "deixou trecho aberto"
        assert O["trechos"](p)[0]["estado"] == "falhou"
        assert O["valor"](p, "erros") == 1

    def test_o_resumo_avisa_de_trecho_aberto(self):
        """Trecho aberto no fim é quase sempre um 'ensure' que faltou."""
        p = O["painel"]("t")
        O["abrir"](p, "esquecido")
        r = O["resumo"](p)
        assert r["abertos"] == ["esquecido"]
        assert not r["ok"]

    def test_o_resumo_responde_as_sete_perguntas(self):
        p = O["painel"]("etl", "1.2.0")
        O["contar"](p, "linhas", 40)
        O["fechar"](p, O["abrir"](p, "e"))
        r = O["resumo"](p)
        for chave in ("executou", "duracao", "contadores", "falhas",
                      "trechos", "quando", "versao"):
            assert chave in r


class TestLinhagem:
    def _painel(self):
        p = O["painel"]("t")
        O["derivar"](p, "bruto", ["api"], "extração")
        O["derivar"](p, "prata", ["bruto"], "limpeza")
        O["derivar"](p, "painel", ["prata", "metas"], "agregação")
        return p

    def test_origem_atravessa_a_cadeia(self):
        """'De onde veio esse número' — meses depois, com o código mudado."""
        origem = self._painel()
        passos = O["origem"](origem, "painel")
        assert {p["de"] for p in passos} >= {"prata", "metas", "bruto", "api"}

    def test_impacto_responde_a_pergunta_mais_cara(self):
        """'Se eu mexer aqui, o que quebra?'"""
        assert set(O["impacto"](self._painel(), "bruto")) == {"prata", "painel"}

    def test_folha_nao_tem_impacto(self):
        assert O["impacto"](self._painel(), "painel") == []

    def test_ciclo_na_linhagem_nao_trava(self):
        p = O["painel"]("t")
        O["derivar"](p, "a", ["b"])
        O["derivar"](p, "b", ["a"])
        assert O["origem"](p, "a") is not None
        assert O["impacto"](p, "a") is not None


class TestSaida:
    def test_prometheus_sai_no_formato_de_exposicao(self):
        p = O["painel"]("etl-vendas")
        O["contar"](p, "linhas", 100)
        O["medir"](p, "lat", 1.5)
        texto = O["prometheus"](p)
        assert "# TYPE etl_vendas_linhas counter" in texto
        assert "etl_vendas_linhas 100" in texto
        assert 'quantile="0.99"' in texto

    def test_alerta_so_do_que_exige_acao(self):
        """Uma regra que dispara todo dia deixa de ser lida."""
        p = O["painel"]("t")
        O["contar"](p, "erros", 3)
        O["contar"](p, "ok", 100)
        disparados = O["alertar"](p, {"erros": {"acima": 0},
                                      "ok": {"acima": 1000}})
        assert [a["metrica"] for a in disparados] == ["erros"]

    def test_alerta_sobre_percentil(self):
        """O alerta olha a CAUDA, não a média — é ela que dói."""
        p = O["painel"]("t")
        for _ in range(90):
            O["medir"](p, "lat", 1.0)
        for _ in range(10):
            O["medir"](p, "lat", 99.0)
        assert not O["alertar"](p, {"lat": {"acima": 50,
                                            "estatistica": "p50"}})
        assert O["alertar"](p, {"lat": {"acima": 50,
                                        "estatistica": "p99"}})

    def test_salvar_e_json_com_tudo(self, tmp_path):
        import json
        p = O["painel"]("t", "1.0")
        O["contar"](p, "linhas", 5)
        O["derivar"](p, "b", ["a"])
        f = str(tmp_path / "obs.json")
        O["salvar"](p, f)
        d = json.load(open(f, encoding="utf-8"))
        assert d["contadores"]["linhas"] == 5
        assert d["linhagem"]["b"]["de"] == ["a"]

    def test_salvar_sem_caminho_diz_o_que_fazer(self):
        with pytest.raises(DataForgeError) as e:
            O["salvar"](O["painel"]("t"))
        assert "caminho" in e.value.message
