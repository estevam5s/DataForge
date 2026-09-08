"""Crucible — o framework de testes do DataForge.

Testar um framework de testes tem uma armadilha: e facil escrever um
teste que passa porque o framework nunca rodou nada. Por isso quase
todo teste aqui confere o RESULTADO da execucao, e nao so que ela nao
estourou.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.interpreter import Interpreter          # noqa: E402
from dataforge.lexer import tokenize                   # noqa: E402
from dataforge.parser import parse                     # noqa: E402
from dataforge.stdlib.crucible import (                # noqa: E402
    ArcaneCrucible, Executor, Expectativa, FalhaDeExpectativa, Gerador,
    REGISTRO, Suite, Trial, diferenca, relatorio, relatorio_junit,
    relatorio_tap, verificar_propriedade, PASSOU, FALHOU, ERRO, PENDENTE,
)


@pytest.fixture(autouse=True)
def registro_limpo():
    """Cada teste comeca com o registro vazio.

    Sem isto, uma suite declarada num teste apareceria nos resultados
    do proximo — exatamente o vazamento que o Crucible promete nao ter.
    """
    REGISTRO.reiniciar()
    yield
    REGISTRO.reiniciar()


def rodar(fonte, **opcoes):
    """Executa o .df (que registra as suites) e roda o que ele registrou.

    Reinicia o registro a cada chamada: um teste que roda a mesma fonte
    tres vezes com filtros diferentes veria as tres declaracoes
    somadas, e contaria nove trials onde ha tres.
    """
    REGISTRO.reiniciar()
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<teste>"), "<teste>"),
                          "<teste>")
    executor = Executor(**opcoes)
    executor.rodar(REGISTRO.raiz)
    return executor


def estados(executor):
    return {r.nome: r.estado for r in executor.resultados}


# ═══ Os matchers ═══════════════════════════════════════════

def test_to_be_passa_e_falha():
    Expectativa(4).to_be(4)
    with pytest.raises(FalhaDeExpectativa):
        Expectativa(4).to_be(5)


def test_a_cadeia_encadeia():
    Expectativa(4).to_be_even().to_be_positive().to_be_between(1, 10)


def test_nao_inverte_so_o_proximo():
    """Se 'nao' ficasse pendurado, a segunda cobranca sairia invertida."""
    e = Expectativa([1, 2, 3])
    e.nao().to_contain(9).to_contain(2)


def test_float_se_compara_por_aproximacao():
    """0.1 + 0.2 nao da 0.3 em nenhuma linguagem com IEEE 754."""
    Expectativa(0.1 + 0.2).to_be_close_to(0.3)
    with pytest.raises(FalhaDeExpectativa):
        Expectativa(0.1 + 0.2).to_be(0.3)


def test_to_raise_pega_a_familia():
    """'to_raise(RuntimeError)' aceita DivisionByZeroError, como o 'handle'."""
    from dataforge.errors import DivisionByZeroError, RuntimeError_

    def estoura():
        raise DivisionByZeroError("x")

    Expectativa(estoura).to_raise(RuntimeError_)
    Expectativa(estoura).to_raise(DivisionByZeroError)
    with pytest.raises(FalhaDeExpectativa):
        Expectativa(estoura).to_raise("KeyError")


def test_to_raise_recusa_um_valor_ja_avaliado():
    """'expect(1/0)' ja estourou antes de chegar ao matcher."""
    with pytest.raises(FalhaDeExpectativa) as exc:
        Expectativa(42).to_raise()
    assert "acao" in str(exc.value)


def test_to_raise_cobra_a_mensagem():
    def estoura():
        raise ValueError("saldo insuficiente")

    Expectativa(estoura).to_raise(mensagem="saldo")
    with pytest.raises(FalhaDeExpectativa):
        Expectativa(estoura).to_raise(mensagem="outra coisa")


def test_to_not_raise():
    Expectativa(lambda: 1 + 1).to_not_raise()
    with pytest.raises(FalhaDeExpectativa):
        Expectativa(lambda: 1 / 0).to_not_raise()


def test_matchers_de_colecao():
    Expectativa([3, 1, 2]).to_have_length(3).to_contain(2)
    Expectativa([1, 2, 3]).to_be_sorted().to_be_unique()
    Expectativa([1, 1]).nao().to_be_unique()
    Expectativa({"a": 1}).to_have_key("a").nao().to_have_key("z")
    Expectativa([1, 2, 3]).to_have_same_items([3, 2, 1])


def test_to_have_field_serve_para_vault_record_e_instancia():
    """O teste nao deveria precisar saber qual dos tres o valor e."""
    Expectativa({"nome": "Ana"}).to_have_field("nome", "Ana")

    class Falso:
        fields = {"nome": "Bia"}

    Expectativa(Falso()).to_have_field("nome", "Bia")


def test_to_print_captura_a_saida():
    Expectativa(lambda: print("ola")).to_print("ola")
    with pytest.raises(FalhaDeExpectativa):
        Expectativa(lambda: print("ola")).to_print("tchau")


def test_mensagem_usa_o_vocabulario_da_linguagem():
    """'True' na mensagem obriga a traduzir de cabeca antes de entender."""
    with pytest.raises(FalhaDeExpectativa) as exc:
        Expectativa(True).to_be(False)
    assert "yes" in str(exc.value) and "no" in str(exc.value)
    assert "True" not in str(exc.value)


# ═══ A diferenca ═══════════════════════════════════════════

def test_diferenca_de_vault_aponta_so_a_chave_que_difere():
    d = diferenca({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 9, "c": 3})
    assert '"b"' in d
    assert '"a"' not in d


def test_diferenca_de_cluster_aponta_o_indice():
    d = diferenca([1, 2, 3], [1, 9, 3])
    assert "[1]" in d


def test_diferenca_de_texto_aponta_a_coluna():
    d = diferenca("abacate", "abacaxi")
    assert "coluna 6" in d


def test_diferenca_diz_o_que_faltou_e_o_que_sobrou():
    d = diferenca({"a": 1}, {"b": 2})
    assert "faltou" in d and "sobrou" in d


# ═══ A sintaxe da linguagem ════════════════════════════════

def test_suite_e_trial_pela_sintaxe():
    ex = rodar('''
crucible "Soma":
    trial "dois e dois":
        expect 2 + 2 is 4
''')
    assert estados(ex) == {"dois e dois": PASSOU}


def test_forma_curta_e_encadeada_dao_no_mesmo():
    ex = rodar('''
crucible "Formas":
    trial "curta":
        expect 2 + 2 is 4
    trial "encadeada":
        expect(2 + 2).to_be(4)
''')
    assert set(estados(ex).values()) == {PASSOU}


def test_forma_curta_com_operador_de_comparacao():
    """'expect x is 4' vira UM no de comparacao; o parser o decompoe."""
    ex = rodar('''
crucible "Operadores":
    trial "is":
        expect 4 is 4
    trial "bigger":
        expect 5 bigger 3
    trial "smaller":
        expect 3 smaller 5
''')
    assert set(estados(ex).values()) == {PASSOU}


def test_forma_curta_falha_quando_deve():
    ex = rodar('''
crucible "Falhas":
    trial "erra":
        expect 2 + 2 is 5
''')
    assert estados(ex) == {"erra": FALHOU}
    assert "devia ser 5" in ex.resultados[0].motivo


def test_expect_sozinho_cobra_verdade():
    ex = rodar('''
crucible "Verdade":
    trial "passa":
        expect yes
    trial "falha":
        expect no
''')
    assert estados(ex) == {"passa": PASSOU, "falha": FALHOU}


def test_setup_entrega_valores_ao_trial():
    ex = rodar('''
crucible "Com setup":
    setup:
        base := 10
    trial "ve a base":
        expect base is 10
''')
    assert estados(ex) == {"ve a base": PASSOU}


def test_um_trial_nao_vaza_para_o_proximo():
    """A garantia central: cada trial roda no proprio escopo."""
    ex = rodar('''
crucible "Isolamento":
    setup:
        contador := 0
    trial "primeiro soma":
        contador := contador + 1
        expect contador is 1
    trial "segundo ve o valor original":
        expect contador is 0
''')
    assert set(estados(ex).values()) == {PASSOU}


def test_suites_aninham_e_herdam_o_setup():
    ex = rodar('''
crucible "Fora":
    setup:
        valor := 7
    crucible "Dentro":
        trial "herda":
            expect valor is 7
''')
    assert list(estados(ex).values()) == [PASSOU]
    assert ex.resultados[0].suite == "Fora > Dentro"


def test_pending_nao_roda_e_diz_por_que():
    ex = rodar('''
crucible "Adiado":
    trial "depois" pending "esperando a API":
        expect 1 is 2
''')
    assert ex.resultados[0].estado == PENDENTE
    assert ex.resultados[0].motivo == "esperando a API"


def test_tags_filtram():
    fonte = '''
crucible "Marcados":
    trial "rapido" tagged "rapido":
        expect 1 is 1
    trial "lento" tagged "lento":
        expect 1 is 1
'''
    assert len(rodar(fonte, tags=("rapido",)).resultados) == 1
    assert len(rodar(fonte, sem_tags=("lento",)).resultados) == 1
    assert len(rodar(fonte).resultados) == 2


def test_filtro_por_nome():
    fonte = '''
crucible "Nomes":
    trial "soma":
        expect 1 is 1
    trial "subtracao":
        expect 1 is 1
'''
    assert len(rodar(fonte, filtro="soma").resultados) == 1


def test_only_foca():
    """Com um 'only' na suite, so os focados rodam."""
    ex = rodar('''
crucible "Foco":
    trial "este" only:
        expect 1 is 1
    trial "aquele":
        expect 1 is 2
''')
    assert estados(ex) == {"este": PASSOU}


def test_within_cobra_o_prazo():
    ex = rodar('''
crucible "Prazo":
    trial "estoura" within 0.0001:
        cycle i from 1 to 2000:
            x := i * 2
''')
    assert ex.resultados[0].estado == FALHOU
    assert "prazo" in ex.resultados[0].motivo


def test_over_gera_um_trial_por_linha():
    ex = rodar('''
crucible "Tabela":
    trial "e par" over [2, 4, 6]:
        expect caso % 2 is 0
''')
    assert len(ex.resultados) == 3
    assert set(estados(ex).values()) == {PASSOU}
    assert "[2]" in ex.resultados[0].nome


def test_over_mostra_qual_caso_falhou():
    ex = rodar('''
crucible "Tabela":
    trial "e par" over [2, 3]:
        expect caso % 2 is 0
''')
    ruins = [r for r in ex.resultados if r.estado == FALHOU]
    assert len(ruins) == 1
    assert "[3]" in ruins[0].nome


def test_erro_no_trial_vira_estado_de_erro_e_nao_derruba_a_suite():
    ex = rodar('''
crucible "Com erro":
    trial "estoura":
        out inexistente
    trial "segue rodando":
        expect 1 is 1
''')
    assert estados(ex) == {"estoura": ERRO, "segue rodando": PASSOU}


def test_teardown_roda_mesmo_com_falha():
    """A limpeza esquecida e o modo mais comum de a suite virar fragil."""
    ex = rodar('''
crucible "Limpeza":
    setup:
        marca := []
    teardown:
        expect 1 is 1
    trial "falha":
        expect 1 is 2
''')
    assert ex.resultados[0].estado == FALHOU


def test_fixture_com_provide():
    ex = rodar('''
crucible "Fixtures":
    fixture caixa():
        itens := [1, 2, 3]
        provide itens

    trial "usa a fixture":
        expect caixa() exists
''')
    assert list(estados(ex).values()) == [PASSOU]


def test_provide_fora_de_fixture_explica():
    """O executor captura o erro do trial; a mensagem tem de ensinar."""
    ex = rodar('''
crucible "Solto":
    trial "erra":
        provide 1
''')
    assert ex.resultados[0].estado == ERRO
    assert "fixture" in ex.resultados[0].motivo


def test_palavras_do_crucible_continuam_livres_fora_dele():
    """'expect', 'trial' e 'setup' sao nomes bons demais para tirar.

    'setup' e o nome do construtor de blueprint: reserva-lo quebraria
    todo blueprint com construtor da linguagem inteira.
    """
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize('''
trial := 10
expect := 20
crucible := 30
fixture := 40
pending := 50
bench := 60

blueprint Caixa(x):
    action setup(x):
        self.x := x

out trial + expect + crucible + fixture + pending + bench
out (spawn Caixa(7)).x
''', "<t>"), "<t>"), "<t>")
    assert saida.getvalue().split() == ["210", "7"]


def test_bench_mede_e_nao_cobra():
    ex = rodar('''
crucible "Medindo":
    bench "soma" times 5:
        x := 1 + 1
''')
    assert ex.resultados[0].estado == PASSOU
    assert "bench" in ex.resultados[0].tags


# ═══ O executor ════════════════════════════════════════════

def test_aleatorio_com_a_mesma_semente_repete_a_ordem():
    fonte = '''
crucible "Ordem":
    trial "a":
        expect 1 is 1
    trial "b":
        expect 1 is 1
    trial "c":
        expect 1 is 1
    trial "d":
        expect 1 is 1
'''
    uma = [r.nome for r in rodar(fonte, aleatorio=True, semente=42).resultados]
    outra = [r.nome for r in rodar(fonte, aleatorio=True, semente=42).resultados]
    assert uma == outra


def test_parar_na_primeira_falha():
    ex = rodar('''
crucible "Para":
    trial "falha":
        expect 1 is 2
    trial "nao roda":
        expect 1 is 1
''', parar_na_primeira=True)
    assert len(ex.resultados) == 1


def test_resumo_conta_certo():
    ex = rodar('''
crucible "Contagem":
    trial "passa":
        expect 1 is 1
    trial "falha":
        expect 1 is 2
    trial "adiado" pending "x":
        expect 1 is 1
''')
    n = ex.resumo()
    assert (n["passou"], n["falhou"], n["pendente"]) == (1, 1, 1)
    assert n["verde"] is False


def test_suite_toda_verde_e_verde():
    ex = rodar('''
crucible "Verde":
    trial "a":
        expect 1 is 1
''')
    assert ex.resumo()["verde"] is True


# ═══ Os relatorios ═════════════════════════════════════════

def test_relatorio_de_texto_mostra_a_falha():
    ex = rodar('''
crucible "Relatorio":
    trial "erra":
        expect 2 is 3
''')
    texto = relatorio(ex, colorir=False)
    assert "Relatorio > erra" in texto
    assert "devia ser 3" in texto
    assert "1 falhou" in texto


def test_relatorio_junit_e_xml_valido():
    import xml.etree.ElementTree as ET
    ex = rodar('''
crucible "CI":
    trial "passa":
        expect 1 is 1
    trial "falha":
        expect 1 is 2
''')
    arvore = ET.fromstring(relatorio_junit(ex))
    assert arvore.tag == "testsuites"
    assert arvore.get("failures") == "1"
    assert len(arvore.findall(".//testcase")) == 2


def test_relatorio_tap():
    ex = rodar('''
crucible "TAP":
    trial "passa":
        expect 1 is 1
    trial "falha":
        expect 1 is 2
''')
    texto = relatorio_tap(ex)
    assert texto.startswith("TAP version 13")
    assert "1..2" in texto
    assert "not ok 2" in texto


# ═══ Dublês ════════════════════════════════════════════════

def test_mock_anota_as_chamadas():
    m = ArcaneCrucible._mock("servico")
    m.buscar(1)
    m.buscar(2)
    m.salvar("x")
    assert m.vezes("buscar") == 2
    assert m.chamado_com("salvar", "x")
    assert not m.foi_chamado("apagar")


def test_mock_devolve_o_que_foi_programado():
    m = ArcaneCrucible._mock()
    m.quando("buscar").devolve([1, 2])
    assert m.buscar() == [1, 2]


def test_mock_devolve_em_sequencia():
    m = ArcaneCrucible._mock()
    m.quando("proximo").devolve_em_sequencia([1, 2, 3])
    assert [m.proximo(), m.proximo(), m.proximo()] == [1, 2, 3]


def test_mock_levanta_o_que_foi_programado():
    m = ArcaneCrucible._mock()
    m.quando("falhar").levanta(ValueError("planejado"))
    with pytest.raises(ValueError):
        m.falhar()


def test_spy_deixa_passar_e_anota():
    class Real:
        def dobro(self, x):
            return x * 2

    espiao = ArcaneCrucible._spy(Real())
    assert espiao.dobro(4) == 8
    assert espiao.chamado_com("dobro", 4)


# ═══ Teste por propriedade ═════════════════════════════════

def test_propriedade_verdadeira_passa():
    g = ArcaneCrucible._g_integers(0, 100)
    ok, contra, _ = verificar_propriedade(g, lambda n: n >= 0, casos=50)
    assert ok and contra is None


def test_propriedade_falsa_acha_contraexemplo():
    g = ArcaneCrucible._g_integers(-100, 100)
    ok, contra, _ = verificar_propriedade(g, lambda n: n >= 0, casos=200,
                                          semente=1)
    assert not ok
    assert contra < 0


def test_contraexemplo_e_encolhido():
    """Um contraexemplo de 900 digitos prova o bug e nao ajuda a achar."""
    g = ArcaneCrucible._g_clusters(tamanho_max=30)
    ok, contra, _ = verificar_propriedade(g, lambda xs: len(xs) < 3,
                                          casos=300, semente=7)
    assert not ok
    assert len(contra) == 3, f"devia encolher ate o minimo que falha: {contra}"


def test_gerador_mapeia_e_filtra():
    g = ArcaneCrucible._g_integers(0, 100).mapear(lambda n: n * 2)
    assert all(v % 2 == 0 for v in g.amostra(20, semente=3))
    pares = ArcaneCrucible._g_integers(0, 100).filtrar(lambda n: n % 2 == 0)
    assert all(v % 2 == 0 for v in pares.amostra(10, semente=3))


# ═══ Utilidades ════════════════════════════════════════════

def test_capture_pega_saida_e_valor():
    r = ArcaneCrucible._capture(lambda: (print("oi"), 42)[1])
    assert r["saida"].strip() == "oi"
    assert r["valor"] == 42


def test_benchmark_devolve_as_estatisticas_que_importam():
    """Media sozinha engana: uma pausa do coletor move a media e some."""
    m = ArcaneCrucible._benchmark("nada", lambda: None, vezes=50,
                                  aquecimento=2)
    assert m["vezes"] == 50
    for chave in ("media_ms", "mediana_ms", "p95_ms", "p99_ms", "ops_por_s"):
        assert chave in m
    assert m["min_ms"] <= m["mediana_ms"] <= m["max_ms"]


def test_approx_compara_com_margem():
    a = ArcaneCrucible._approx(0.3)
    assert a == 0.1 + 0.2
    assert a != 0.5


def test_a_api_expoe_o_que_a_doc_promete():
    modulo = ArcaneCrucible()
    for nome in ("suite", "trial", "expect", "mock", "run", "report",
                 "junit", "benchmark", "forall", "fixture"):
        assert nome in modulo, nome
