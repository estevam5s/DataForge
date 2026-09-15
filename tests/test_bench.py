"""Arcane.Bench — a complexidade que se MEDE, não a que se lê.

A linguagem já sabia dizer a complexidade que ela **lê** no código
(`complexidade.py`). Ela não sabia dizer a que **acontece** quando o
programa roda — e as duas erram de formas opostas:

    a análise estática   vê 'cycle dentro de cycle' e diz O(n²), mesmo
                         que o laço interno rode três vezes
    a medição            vê o tempo real, com cache e interpretador
                         dentro, e não sabe o que acontece com n maior

Os testes aqui cobram o classificador contra curvas de complexidade
**conhecida**. Se ele erra num O(n²) escrito à mão, não serve para o
código de ninguém.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib.arcane_bench import (  # noqa: E402
    ArcaneBench, _classificar, _fatores,
)

B = ArcaneBench()


# ═══ O classificador, sem medir nada ═══════════════════════
#
# Alimentado com fatores sintéticos: aqui não há relógio, e por isso
# não há instabilidade. É o único jeito de cobrar a regra em si.

def test_o_fator_de_cada_classe_e_reconhecido():
    assert _classificar([1.0, 1.0, 1.0])[0] == "O(1)"
    assert "O(n)" in _classificar([2.0, 2.0, 2.0])
    assert _classificar([4.0, 4.0, 4.0]) == ["O(n^2)"]
    assert _classificar([8.0, 8.0, 8.0]) == ["O(n^3)"]


def test_o_exponencial_e_o_fator_CRESCENDO_e_nao_um_numero():
    """Dobrar n num O(2^n) multiplica o tempo por 2^n — que depende de n.

    A assinatura dele não é um fator: é o fator crescendo entre uma
    medida e a seguinte. Um O(n³) tem 8,0 estável; um O(2^n) vai de 4
    para 16 para 256.

    Dar-lhe um centro na tabela criava sobreposição: com folga larga o
    bastante para pegá-lo, o fator 8,0 de um cúbico casava com os dois,
    e `_classificar([8, 8, 8])` respondia `['O(n^3)', 'O(2^n)']`.
    """
    assert _classificar([4.0, 16.0, 256.0]) == ["O(2^n) ou pior"]
    # e o cúbico continua sendo cúbico
    assert _classificar([8.0, 8.0, 8.0]) == ["O(n^3)"]


def test_duas_classes_vizinhas_saem_JUNTAS():
    """O(n) e O(n log n) ficam a 0,15 de distância.

    Nenhuma medição as separa com honestidade abaixo de uns cem mil
    itens. Escolher uma seria inventar precisão — e a pessoa levaria
    embora um número que o teste não sustenta.
    """
    classes = _classificar([2.05, 2.08, 2.06])
    assert classes == ["O(n)", "O(n log n)"]


def test_o_que_cai_ENTRE_duas_classes_nomeia_as_duas():
    """`s += "x"` num laço mede 2,7: nem linear nem quadrático.

    O CPython otimiza parte das concatenações e não todas. Responder
    "indeterminado" escondia a informação mais útil que havia — que o
    custo está entre as duas, e que piora conforme n cresce.
    """
    assert _classificar([2.7, 2.8, 2.75]) == ["entre O(n log n) e O(n^2)"]
    assert _classificar([5.0, 5.2, 4.9]) == ["entre O(n^2) e O(n^3)"]


def test_a_mediana_e_nao_a_media():
    """Uma pausa do coletor no meio da amostra vira um fator absurdo.

    A média o carrega para sempre; a mediana o descarta. Sem isso, uma
    coleta bem colocada faz um O(n) ser reportado como exponencial.
    """
    # Três fatores lineares e um disparate.
    assert "O(n)" in _classificar([2.0, 2.0, 40.0, 2.0])


def test_fator_normaliza_tamanhos_que_NAO_dobram():
    """100 → 250 → 500 tem de entrar na mesma tabela que 100 → 200.

    Sem a normalização, medir em tamanhos que não dobram produzia
    fatores sem sentido, e a classe saía sempre pior do que é.
    """
    # O(n) exato, com razões 2,5 e 2,0
    fatores = _fatores([(100.0, 1.0), (250.0, 2.5), (500.0, 5.0)])
    for f in fatores:
        assert abs(f - 2.0) < 0.01, f"esperava 2,0 por dobra, veio {f}"


# ═══ Medindo de verdade ════════════════════════════════════

def test_medir_devolve_tempo_e_taxa():
    r = B["medir"](lambda _: sum(range(1000)), None, 3, 1)
    assert r["ms"] > 0
    assert r["por_segundo"] > 0
    assert r["repeticoes"] == 3


def test_comparar_elege_o_mais_rapido():
    devagar = lambda _: sum(range(200000))      # noqa: E731
    rapido = lambda _: sum(range(200))          # noqa: E731

    r = B["comparar"]({"devagar": devagar, "rapido": rapido},
                      None, 3, 1)
    assert r["vencedor"] == "rapido"
    assert r["resultados"][0]["vezes"] == 1.0
    assert r["resultados"][1]["vezes"] > 1.0


def test_comparar_recusa_o_que_nao_e_acao():
    from dataforge.errors import TypeError_
    with pytest.raises(TypeError_):
        B["comparar"]({"nao e acao": 42}, None, 1, 0)


def test_classe_exige_tres_tamanhos():
    """Com dois pontos toda curva é uma reta."""
    from dataforge.errors import RuntimeError_
    with pytest.raises(RuntimeError_) as exc:
        B["classe"](lambda n: n, [10, 20])
    assert "three sizes" in str(exc.value)


@pytest.mark.parametrize("nome,acao,tamanhos,esperada", [
    ("quadratica",
     lambda n: sum(1 for _ in range(n) for _ in range(n)),
     [400, 800, 1600], "O(n^2)"),
])
def test_a_classe_medida_bate_com_a_conhecida(nome, acao, tamanhos, esperada):
    """O único que se cobra exato é o O(n²).

    Ele tem fator 4,0, e o vizinho mais próximo (O(n log n), 2,15) está
    a quase dois de distância. Já O(n) e O(n log n) são cobrados como PAR
    nos testes sintéticos acima: cobrar um deles exato aqui seria um teste
    que reprova sozinho num runner ocupado.

    Esta docstring dizia que "nenhuma máquina carregada transforma um no
    outro", e 'scripts/verificar_tudo.sh' mediu **2,923** — "entre
    O(n log n) e O(n²)". Os tamanhos eram [150, 300, 600] com 2
    repetições: a medida INTEIRA levava ~20 ms, e alguns milissegundos de
    escalonamento achatam a razão. É a lição que o CLAUDE.md já tinha
    escrito para o paralelismo — a razão não basta se o trabalho for
    pequeno. Com [400, 800, 1600] e o mínimo de 3 a medida leva ~200 ms, e
    um soluço de escalonamento vira ruído em vez de mudar a classe.
    """
    r = B["classe"](acao, tamanhos, None, 3)
    assert esperada in r["classes"], (
        f"{nome}: fator medido {r['fator']}, classes {r['classes']}")


def test_a_curva_nao_mede_o_preparo():
    """'preparar' roda FORA da medida.

    Construir a entrada de cem mil itens custa mais que percorrê-la, e
    somá-la à conta apagaria a curva do que se queria medir.
    """
    vistos = []

    def preparar(n):
        vistos.append(n)
        return list(range(n))

    r = B["curva"](lambda xs: len(xs), [100, 200, 400], preparar, 1, 0)
    assert vistos == [100, 200, 400]
    assert len(r["pontos"]) == 3


def test_relatorio_e_tabela_saem_como_texto():
    r = B["classe"](lambda n: sum(range(n)), [2000, 4000, 8000], None, 2)
    texto = B["relatorio"](r)
    assert "fator medio" in texto
    assert "n" in texto.splitlines()[0]

    c = B["comparar"]({"a": lambda _: 1, "b": lambda _: 2}, None, 2, 0)
    assert "x" in B["tabela"](c)


# ═══ O Construtor de texto ═════════════════════════════════

def test_o_construtor_monta_o_mesmo_que_a_concatenacao():
    from dataforge.stdlib import get_module
    T = get_module("Arcane.Text")

    c = T["construtor"]()
    c.add("a").add("b", "c").linha("d").juntar(["x", "y"], "-")
    assert c.texto() == "abcd\nx-y"
    assert c.tamanho() == 8
    assert len(c) == 8


def test_texto_pode_ser_chamado_mais_de_uma_vez():
    """'texto()' COMPACTA as partes — e não pode perder o que vem depois.

    A compactação existe para que chamá-lo dentro de um laço não refaça
    o `join` a cada volta, o que devolveria o Construtor ao custo
    quadrático pela porta dos fundos. Ela não pode custar a correção.
    """
    from dataforge.stdlib import get_module
    T = get_module("Arcane.Text")

    c = T["construtor"]("inicio")
    c.add("-meio")
    assert c.texto() == "inicio-meio"
    c.add("-fim")
    assert c.texto() == "inicio-meio-fim"
    assert c.texto() == "inicio-meio-fim"


def test_o_construtor_e_linear_e_a_concatenacao_nao():
    """A razão de o Construtor existir, medida — e no lugar certo.

    A primeira versão deste teste mediu `s += "x"` sobre uma variável
    **local de Python** e obteve fator 2,1: linear. Ela estava certa, e
    media a coisa errada.

    O CPython tem uma otimização in-place para `s += t` quando a string
    tem **uma referência só**. Numa variável local ela tem; dentro do
    escopo do interpretador, que é um dicionário, ela não tem — e aí
    cada `+=` copia a string inteira.

        variável local de Python .............. fator 2,11   O(n)
        string dentro de um dicionário ........ fator 4,06   O(n²)
        dentro do interpretador DataForge ..... fator 2,48   entre os dois

    O interpretador fica no meio porque o custo por volta dele é grande
    e **linear**, e a essas alturas ainda mascara parte da cópia; com
    n maior a curva sobe (medido: 3,07 em 160 mil). O mecanismo é o do
    dicionário, e é ele que o teste mede — é rápido, é estável, e é a
    causa.
    """
    from dataforge.stdlib import get_module
    T = get_module("Arcane.Text")

    def concat_em_escopo(n):
        # Como o interpretador guarda: a string vive num dicionário, e
        # a otimização in-place do CPython não se aplica.
        env = {"s": ""}
        for _ in range(n):
            env["s"] = env["s"] + "x"
        return len(env["s"])

    def com_construtor(n):
        b = T["construtor"]()
        for _ in range(n):
            b.add("x")
        return b.tamanho()

    tamanhos = [20000, 40000, 80000]
    linear = B["classe"](com_construtor, tamanhos, None, 2)
    concat = B["classe"](concat_em_escopo, tamanhos, None, 2)

    # A RAZÃO entre os dois, e não um limite sobre cada um: limite
    # absoluto mede a máquina, e reprova quando a suíte inteira disputa
    # a CPU. É a mesma lição que CLAUDE.md registra para paralelismo.
    razao = concat["fator"] / max(linear["fator"], 0.01)
    assert razao > 1.4, (
        "a concatenação repetida deixou de crescer mais rápido que o "
        f"construtor — construtor {linear['fator']}, concat "
        f"{concat['fator']}, razão {razao:.2f}")

    assert "O(n)" in linear["classes"], (
        f"o construtor saiu do linear: {linear['classes']} "
        f"(fator {linear['fator']})")
