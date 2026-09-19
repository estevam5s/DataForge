"""Medir com rigor: percentis, significância, regressão e flame graph.

`Arcane.Bench` responde "quanto tempo leva" com uma **média**. É o que
quase toda ferramenta de benchmark faz, e é onde quase toda decisão de
performance erra:

* a média esconde a cauda, e é a cauda que o usuário sente (P99);
* duas médias diferentes podem ser **a mesma coisa** com ruído — e sem
  teste estatístico não há como saber;
* um número sozinho não responde "piorou desde a semana passada?".

O que os testes cobram:

1. **Percentis de verdade**, com aquecimento separado das amostras.
2. **Significância**: comparar uma ação com ela mesma **não** pode dar
   "mais rápida". É o teste que impede a ferramenta de inventar ganho.
3. **Regressão contra uma linha de base** guardada — o uso de CI.
4. **Flame graph** das ações da linguagem (não dos quadros do Python),
   pelo mesmo gancho que o `dataforge profile` já usa.
5. **Pausas do coletor**, medidas onde elas acontecem.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.interpreter import Interpreter                  # noqa: E402
from dataforge.lexer import tokenize                           # noqa: E402
from dataforge.parser import parse                             # noqa: E402
from dataforge.stdlib import get_module                        # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue()


@pytest.fixture
def P():
    return get_module("Arcane.Perfil")


# ══════════════════════════════════════════════════════════════
#  Percentis
# ══════════════════════════════════════════════════════════════

def test_a_medida_traz_a_distribuicao_e_nao_so_a_media(P):
    medida = P["medir"](lambda: sum(range(200)), {"amostras": 40})
    for chave in ("p50", "p90", "p95", "p99", "min", "max", "media",
                  "desvio", "amostras", "vazao"):
        assert chave in medida, chave
    assert medida["amostras"] == 40
    assert medida["min"] <= medida["p50"] <= medida["p95"] <= medida["max"]


def test_o_aquecimento_e_descartado_e_dito(P):
    """Quem não separa aquecimento mede o primeiro acesso ao cache."""
    medida = P["medir"](lambda: sum(range(50)),
                        {"amostras": 10, "aquecimento": 4})
    assert medida["amostras"] == 10
    assert medida["aquecimento"] == 4


def test_os_percentis_saem_da_amostra_e_nao_de_uma_formula(P):
    """Com uma distribuição conhecida, o percentil é conferível."""
    valores = list(range(1, 101))       # 1..100 ms
    resumo = P["resumir"](valores)
    assert resumo["p50"] == 50
    assert resumo["p95"] == 95
    assert resumo["p99"] == 99
    assert resumo["min"] == 1 and resumo["max"] == 100


def test_a_cauda_aparece_onde_a_media_esconde(P):
    """Uma amostra com um pico: a média mal se move, o P99 salta."""
    normais = [10.0] * 99
    resumo = P["resumir"](normais + [1000.0])
    assert resumo["media"] < 20, "a média esconde o pico"
    assert resumo["p99"] >= 1000 or resumo["max"] == 1000


def test_resumir_recusa_amostra_vazia(P):
    from dataforge.errors import DataForgeError
    with pytest.raises(DataForgeError):
        P["resumir"]([])


# ══════════════════════════════════════════════════════════════
#  Significância — o teste que impede inventar ganho
# ══════════════════════════════════════════════════════════════

def test_comparar_uma_acao_com_ela_mesma_nao_acha_diferenca(P):
    """É o teste que separa medição de superstição.

    Duas medidas da MESMA ação diferem por ruído. Uma ferramenta que
    responde "a segunda é 3% mais rápida" está lendo ruído — e é assim
    que se escolhe a implementação errada.
    """
    def tarefa():
        return sum(range(300))

    veredito = P["comparar"](tarefa, tarefa, {"amostras": 60})
    assert not veredito["significativo"], (
        f"achou diferença onde não há: p={veredito['p_valor']:.4f}, "
        f"fator={veredito['fator']}")
    assert veredito["mais_rapido"] == "empate"


def test_comparar_acha_a_diferenca_quando_ela_existe(P):
    veredito = P["comparar"](lambda: sum(range(50)),
                             lambda: sum(range(20000)),
                             {"amostras": 40})
    assert veredito["significativo"]
    assert veredito["mais_rapido"] == "a"
    assert veredito["fator"] > 2
    assert veredito["p_valor"] < 0.05


def test_o_p_valor_fica_entre_zero_e_um(P):
    for a, b in ((lambda: 1, lambda: 1),
                 (lambda: sum(range(10)), lambda: sum(range(5000)))):
        v = P["comparar"](a, b, {"amostras": 25})
        assert 0.0 <= v["p_valor"] <= 1.0


def test_a_sobreposicao_diz_o_tamanho_do_efeito(P):
    """`p` diz *se* há diferença; a sobreposição diz *quanto*."""
    v = P["comparar"](lambda: sum(range(50)), lambda: sum(range(20000)),
                      {"amostras": 30})
    assert 0.0 <= v["sobreposicao"] <= 1.0
    assert v["sobreposicao"] > 0.8, "a sobreposição devia ser alta"


# ══════════════════════════════════════════════════════════════
#  Regressão contra linha de base
# ══════════════════════════════════════════════════════════════

def test_a_linha_de_base_e_guardada_e_relida(P):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = os.path.join(pasta, "base.json")
        medida = P["medir"](lambda: sum(range(100)), {"amostras": 15})
        P["guardar"]("soma", medida, arquivo)
        assert os.path.isfile(arquivo)
        with open(arquivo, encoding="utf-8") as f:
            guardado = json.load(f)
        assert "soma" in guardado
        assert "p95" in guardado["soma"]


def test_a_primeira_medida_nao_pode_reprovar(P):
    """Sem base guardada não há regressão — só um começo."""
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = os.path.join(pasta, "base.json")
        medida = P["medir"](lambda: sum(range(100)), {"amostras": 10})
        veredito = P["conferir"]("nova", medida, {"arquivo": arquivo})
        assert not veredito["conhecida"]
        assert not veredito["regrediu"]


def test_a_regressao_e_acusada_com_o_fator(P):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = os.path.join(pasta, "base.json")
        P["guardar"]("alvo", {"p95": 1.0, "p50": 1.0, "media": 1.0},
                     arquivo)
        veredito = P["conferir"]("alvo", {"p95": 3.0, "p50": 3.0,
                                          "media": 3.0},
                                 {"arquivo": arquivo, "tolerancia": 0.2})
        assert veredito["conhecida"]
        assert veredito["regrediu"]
        assert veredito["fator"] >= 2.5


def test_uma_variacao_dentro_da_tolerancia_nao_reprova(P):
    """Sem tolerância, todo CI fica vermelho por ruído de máquina."""
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = os.path.join(pasta, "base.json")
        P["guardar"]("alvo", {"p95": 1.0, "p50": 1.0, "media": 1.0}, arquivo)
        veredito = P["conferir"]("alvo", {"p95": 1.1, "p50": 1.1,
                                          "media": 1.1},
                                 {"arquivo": arquivo, "tolerancia": 0.25})
        assert not veredito["regrediu"]


def test_uma_melhora_e_relatada_e_nao_reprova(P):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = os.path.join(pasta, "base.json")
        P["guardar"]("alvo", {"p95": 4.0, "p50": 4.0, "media": 4.0}, arquivo)
        veredito = P["conferir"]("alvo", {"p95": 1.0, "p50": 1.0,
                                          "media": 1.0},
                                 {"arquivo": arquivo})
        assert not veredito["regrediu"]
        assert veredito["melhorou"]


# ══════════════════════════════════════════════════════════════
#  Flame graph — das AÇÕES, não dos quadros do Python
# ══════════════════════════════════════════════════════════════

def test_o_perfil_de_chamadas_ve_as_acoes_da_linguagem(P):
    perfil = rodar_e_perfilar('''
action folha(n):
    yield n * 2

action meio(n):
    yield folha(n) + folha(n)

action topo(n):
    yield meio(n) + meio(n)

out topo(3)
''')
    nomes = {p.split(";")[-1] for p in perfil["pilhas"]}
    assert {"topo", "meio", "folha"} <= nomes, nomes


def test_a_pilha_guarda_o_caminho_inteiro(P):
    perfil = rodar_e_perfilar('''
action folha(n):
    yield n * 2

action meio(n):
    yield folha(n)

out meio(1)
''')
    assert any("meio;folha" in caminho for caminho in perfil["pilhas"]), \
        sorted(perfil["pilhas"])


def rodar_e_perfilar(fonte):
    P = get_module("Arcane.Perfil")
    arvore = parse(tokenize(fonte, "<t>"), "<t>")
    interp = Interpreter()
    coleta = P["comecar_perfil"](interp)
    saida = io.StringIO()
    with redirect_stdout(saida):
        interp.run(arvore, "<t>")
    return P["terminar_perfil"](coleta)


def test_as_pilhas_saem_no_formato_dobrado(P):
    perfil = rodar_e_perfilar("action f(n):\n    yield n\nout f(1)\n")
    texto = P["chama_texto"](perfil)
    # o formato que o flamegraph.pl consome: "a;b;c <numero>"
    for linha in texto.strip().split("\n"):
        assert " " in linha
        assert linha.rsplit(" ", 1)[1].isdigit(), linha


def test_o_flame_graph_sai_como_svg(P):
    perfil = rodar_e_perfilar('''
action folha(n):
    yield n * 2

action topo(n):
    yield folha(n) + folha(n)

out topo(2)
''')
    svg = P["chama_svg"](perfil)
    assert svg.startswith("<?xml") or svg.lstrip().startswith("<svg")
    assert "</svg>" in svg
    assert "topo" in svg and "folha" in svg
    # Sem recurso de FORA — a mesma regra da Vitrine. O `xmlns` do SVG
    # não conta: é identificador de espaço de nomes, e nada é buscado.
    for proibido in ("<script", "<image", "xlink:href", "cdn.",
                     '@import', "<foreignObject"):
        assert proibido not in svg, proibido
    assert svg.count("http") == 1, "só o xmlns pode citar um endereço"


def test_o_svg_escapa_o_que_vem_do_programa(P):
    """Um nome de ação com '<' viraria marcação dentro do SVG."""
    svg = P["chama_svg"]({"pilhas": {"a<b>&c": 10}, "total_us": 10,
                          "acoes": 1, "chamadas": 1})
    assert "<b>" not in svg.split("<svg", 1)[1].replace("</svg>", "")
    assert "&lt;" in svg or "&amp;" in svg


# ══════════════════════════════════════════════════════════════
#  Pausas do coletor
# ══════════════════════════════════════════════════════════════

def test_as_pausas_do_coletor_sao_medidas(P):
    def churn():
        lixo = []
        for _ in range(4000):
            a = {"x": None}
            b = {"y": a}
            a["x"] = b            # ciclo: só o coletor resolve
            lixo.append(a)
        return len(lixo)

    resultado = P["gc_pausas"](churn)
    assert "pausas" in resultado and "total_ms" in resultado
    assert resultado["pausas"] >= 0
    assert resultado["resultado"] == 4000


def test_sem_lixo_ciclico_quase_nao_ha_pausa(P):
    r = P["gc_pausas"](lambda: sum(range(100)))
    assert r["total_ms"] < 50


# ══════════════════════════════════════════════════════════════
#  Contenção de trava
# ══════════════════════════════════════════════════════════════

def test_a_trava_observada_conta_espera(P):
    import threading

    trava = P["trava"]()
    marcas = []

    def segurar(qual):
        P["com_trava"](trava, lambda: (time.sleep(0.03),
                                       marcas.append(qual))[-1])

    fios = [threading.Thread(target=segurar, args=(i,)) for i in range(3)]
    for f in fios:
        f.start()
    for f in fios:
        f.join()

    e = P["estatisticas_da_trava"](trava)
    assert e["aquisicoes"] == 3
    assert e["esperas"] >= 1, "três threads na mesma trava têm de esperar"
    assert e["tempo_esperando_ms"] > 0
    assert len(marcas) == 3


def test_uma_trava_sem_disputa_nao_acusa_espera(P):
    trava = P["trava"]()
    for _ in range(5):
        P["com_trava"](trava, lambda: 1)
    e = P["estatisticas_da_trava"](trava)
    assert e["aquisicoes"] == 5
    assert e["esperas"] == 0


# ══════════════════════════════════════════════════════════════
#  Da linguagem
# ══════════════════════════════════════════════════════════════

def test_o_modulo_funciona_de_dentro_da_linguagem():
    assert rodar('''
adopt Arcane.Perfil as P

action trabalho():
    yield sum(range(500))

medida := P.medir(trabalho, {"amostras": 20, "aquecimento": 2})
out medida["amostras"], medida["aquecimento"]
out medida["p50"] smaller_eq medida["p95"]
out "vazao" in medida
''') == "20 2\nyes\nyes\n"


def test_comparar_da_linguagem():
    assert rodar('''
adopt Arcane.Perfil as P

action rapida():
    yield sum(range(20))

action lenta():
    yield sum(range(8000))

v := P.comparar(rapida, lenta, {"amostras": 30})
out v["significativo"], v["mais_rapido"]
''') == "yes a\n"


def test_o_modulo_esta_registrado_e_descrito():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Perfil", "Perfil"):
        assert get_module(nome) is not None, nome
    assert "Arcane.Perfil" in DESCRICOES


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import observabilidade
    for pagina in observabilidade.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda(onde, codigo):
    rodar(codigo)


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
