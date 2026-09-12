"""`frame`, `train` e `predict` — três palavras que não faziam nada.

Elas devolviam um vault com `__type__` e paravam ali. Eram o pior tipo
de lacuna numa linguagem: **pareciam** implementadas. Quem lia a
gramática, a coloração do editor ou a lista de palavras reservadas não
tinha como saber que ali não havia nada.

E a tabela e os algoritmos já existiam, um módulo ao lado:
`Arcane.Analytics` tem um Frame com 25 métodos e `Arcane.Cortex` tem 25
algoritmos de verdade. As palavras não precisavam ser implementadas —
precisavam ser **ligadas**.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError        # noqa: E402
from dataforge.interpreter import Interpreter      # noqa: E402
from dataforge.lexer import tokenize               # noqa: E402
from dataforge.parser import parse                 # noqa: E402


def rodar(fonte):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte, "<ml>"), "<ml>"))
    return buffer.getvalue().strip()


def valor(fonte, nome):
    interp = Interpreter()
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize(fonte, "<ml>"), "<ml>"))
    return interp.global_env.get(nome)


REGISTROS = '''
registros := [
    {"area": 50.0, "quartos": 1.0, "preco": 200.0},
    {"area": 70.0, "quartos": 2.0, "preco": 280.0},
    {"area": 90.0, "quartos": 3.0, "preco": 360.0},
    {"area": 110.0, "quartos": 3.0, "preco": 440.0}
]
'''


# ── frame ────────────────────────────────────────────────────

def test_frame_de_registros_vira_tabela_de_verdade():
    """Antes devolvia `{"__type__": "Frame"}` e nada acontecia."""
    t = valor(REGISTROS + "t := frame registros", "t")
    assert type(t).__name__ == "AnalyticsFrame"
    assert t.columns == ["area", "quartos", "preco"]
    assert t.shape() == [4, 3]


def test_frame_de_colunas():
    t = valor('t := frame {"a": [1, 2], "b": [3, 4]}', "t")
    assert t.columns == ["a", "b"]
    assert t.shape() == [2, 2]


def test_frame_de_matriz():
    t = valor("t := frame [[1, 2], [3, 4], [5, 6]]", "t")
    assert t.shape() == [3, 2]


def test_a_tabela_tem_os_metodos_que_uma_tabela_tem():
    """Ligar a palavra ao Frame que já existia trouxe 25 métodos."""
    t = valor(REGISTROS + "t := frame registros", "t")
    for metodo in ("select", "filter", "where", "group_by", "sort_by",
                   "merge", "head", "describe", "to_csv", "to_json"):
        assert callable(getattr(t, metodo, None)), f"faltou '{metodo}'"


def test_frame_com_o_que_nao_e_tabela_explica():
    with pytest.raises(DataForgeError) as capturado:
        rodar("out frame 42")
    assert "registros" in str(getattr(capturado.value, "dica", ""))


# ── train ────────────────────────────────────────────────────

def test_train_treina_de_verdade():
    """Os dados são exatamente lineares: `preco = 4 × area`.

    Se `train` ainda fosse um marcador, não haveria o que prever — e um
    teste que só checasse "devolveu alguma coisa" continuaria passando.
    """
    saida = rodar(REGISTROS + '''
modelo := train "linear" using {
    "linhas": registros,
    "alvo": "preco",
    "colunas": ["area", "quartos"]
}
out predict modelo using [{"area": 80.0, "quartos": 2.0}]''')
    assert saida == "[320.0]"


def test_train_aceita_um_frame_como_entrada():
    """`frame` e `train` são do mesmo assunto: têm de conversar."""
    saida = rodar(REGISTROS + '''
modelo := train "linear" using {
    "linhas": frame registros,
    "alvo": "preco",
    "colunas": ["area"]
}
out predict modelo using [{"area": 100.0}]''')
    assert saida == "[400.0]"


def test_train_repassa_as_opcoes_do_algoritmo():
    """O vault é de argumentos nomeados — por isso a palavra não esconde nada.

    Quem precisa de `arvores=50` escreve `arvores`, sem sair da sintaxe.
    """
    modelo = valor('''
flores := [
    {"l": 1.4, "a": 0.2, "e": "setosa"},
    {"l": 1.3, "a": 0.2, "e": "setosa"},
    {"l": 4.7, "a": 1.4, "e": "versicolor"},
    {"l": 4.5, "a": 1.5, "e": "versicolor"}
]
m := train "floresta" using {
    "linhas": flores, "alvo": "e", "colunas": ["l", "a"], "arvores": 7
}''', "m")
    assert modelo.especie, "devia ter vindo um modelo do Cortex"


def test_classificacao_acerta():
    saida = rodar('''
flores := [
    {"l": 1.4, "a": 0.2, "e": "setosa"},
    {"l": 1.3, "a": 0.2, "e": "setosa"},
    {"l": 4.7, "a": 1.4, "e": "versicolor"},
    {"l": 4.5, "a": 1.5, "e": "versicolor"},
    {"l": 6.0, "a": 2.5, "e": "virginica"},
    {"l": 5.8, "a": 2.2, "e": "virginica"}
]
c := train "floresta" using {
    "linhas": flores, "alvo": "e", "colunas": ["l", "a"], "arvores": 10
}
out predict c using [{"l": 1.35, "a": 0.2}, {"l": 5.9, "a": 2.3}]''')
    assert saida == "[setosa, virginica]"


def test_uma_acao_sua_tambem_serve_de_modelo():
    """A palavra não pode ser exclusiva do Cortex."""
    assert rodar('''
action meu_modelo(linhas):
    yield [linha["x"] * 2 cycle linha in linhas]

out predict meu_modelo using [{"x": 21}]''') == "[42]"


def test_train_com_algoritmo_que_nao_existe_sugere_o_certo():
    with pytest.raises(DataForgeError) as capturado:
        rodar('out train "florestaaa" using {"linhas": [], "alvo": "a", '
              '"colunas": []}')
    assert "floresta" in str(getattr(capturado.value, "dica", ""))


def test_train_nao_aceita_o_que_nao_treina():
    """`validacao_cruzada` recebe `(linhas, alvo, colunas)` e devolve NOTA.

    Qualquer filtro por nome de parâmetro a chamaria de treinador. Por
    isso a lista vive no Cortex, e não numa dedução sobre assinaturas.
    """
    with pytest.raises(DataForgeError) as capturado:
        rodar('out train "validacao_cruzada" using {"linhas": [], '
              '"alvo": "a", "colunas": []}')
    assert "nao e um algoritmo de treino" in str(capturado.value)


def test_train_sem_vault_explica():
    with pytest.raises(DataForgeError) as capturado:
        rodar('out train "linear" using [1, 2]')
    assert "vault" in str(capturado.value).lower()


def test_predict_com_o_que_nao_e_modelo_explica():
    with pytest.raises(DataForgeError) as capturado:
        rodar("out predict 42 using [{}]")
    assert "modelo treinado" in str(capturado.value)


# ── A lista de treinadores é a fonte da verdade ──────────────

def test_todo_treinador_declarado_existe_e_treina():
    """A lista vive no Cortex; este teste garante que ela não envelhece."""
    from dataforge.stdlib import get_module
    from dataforge.stdlib.arcane_cortex import TREINADORES

    cortex = get_module("Arcane.Cortex")
    for nome in TREINADORES:
        assert nome in cortex, f"'{nome}' nao existe no Arcane.Cortex"
        assert callable(cortex[nome]), f"'{nome}' nao e chamavel"


def test_nenhuma_das_tres_palavras_devolve_marcador():
    """A regressão que importa: elas voltarem a ser cascas.

    Um vault com `__type__` e nada dentro passaria em qualquer teste que
    só checasse "não levantou erro".
    """
    t = valor(REGISTROS + "t := frame registros", "t")
    assert not (isinstance(t, dict) and t.get("__type__") == "Frame")

    m = valor(REGISTROS + '''
m := train "linear" using {
    "linhas": registros, "alvo": "preco", "colunas": ["area"]
}''', "m")
    assert not (isinstance(m, dict) and m.get("__type__") == "TrainedModel")

    p = valor(REGISTROS + '''
m := train "linear" using {
    "linhas": registros, "alvo": "preco", "colunas": ["area"]
}
p := predict m using [{"area": 100.0}]''', "p")
    assert not (isinstance(p, dict) and p.get("__type__") == "Prediction")
    assert isinstance(p, list), "predict devia devolver as previsoes"
