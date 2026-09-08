"""O sistema de erros: catalogo, classes, hierarquia e traducao.

O catalogo e as classes nascem da mesma tabela. Estes testes existem
para que continuem nascendo: uma divergencia entre os dois so aparece
quando um usuario procura a explicacao de um erro e nao acha.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import errors as E                     # noqa: E402
from dataforge.catalogo_erros import ERROS, familia   # noqa: E402
from dataforge.diagnosticos import CATALOGO, buscar, procurar  # noqa: E402
from dataforge.interpreter import Interpreter         # noqa: E402
from dataforge.lexer import tokenize                  # noqa: E402
from dataforge.parser import parse                    # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<teste>"), "<teste>"), "<teste>")
    return saida.getvalue().strip()


# ─── O catalogo se sustenta ────────────────────────────────

def test_o_pedido_de_cem_tipos_foi_cumprido():
    assert len(ERROS) > 100


def test_codigos_sao_unicos():
    codigos = [e["codigo"] for e in ERROS]
    repetidos = {c for c in codigos if codigos.count(c) > 1}
    assert not repetidos, f"codigos repetidos: {sorted(repetidos)}"


def test_classes_sao_unicas():
    nomes = [e["classe"] for e in ERROS if e["classe"]]
    repetidos = {n for n in nomes if nomes.count(n) > 1}
    assert not repetidos, f"classes repetidas: {sorted(repetidos)}"


def test_codigo_tem_o_formato_estavel():
    for e in ERROS:
        assert e["codigo"].startswith("DF"), e["codigo"]
        assert len(e["codigo"]) == 6, e["codigo"]
        assert e["codigo"][2:].isdigit(), e["codigo"]


def test_toda_entrada_tem_texto_util():
    """Um codigo sem explicacao e pior que nenhum: promete ajuda e nao da."""
    for e in ERROS:
        assert e["titulo"], e["codigo"]
        assert len(e["explicacao"]) > 40, f"{e['codigo']} mal explicado"
        assert e["solucao"], f"{e['codigo']} sem 'como resolver'"
        assert e["doc"], f"{e['codigo']} sem ancora de doc"


def test_toda_familia_tem_nome():
    for e in ERROS:
        assert familia(e["codigo"]) != "desconhecida", e["codigo"]


# ─── Classes e catalogo nao divergem ───────────────────────

def test_toda_entrada_virou_classe():
    for e in ERROS:
        if not e["classe"]:
            continue
        assert e["classe"] in E.ERROS_POR_NOME, e["classe"]


def test_a_classe_carrega_o_proprio_codigo():
    for e in ERROS:
        if not e["classe"]:
            continue
        assert E.ERROS_POR_NOME[e["classe"]].CODIGO == e["codigo"]


def test_toda_classe_desce_de_DataForgeError():
    for classe in E.ERROS_POR_NOME.values():
        assert issubclass(classe, E.DataForgeError)


def test_a_heranca_declarada_e_a_heranca_real():
    for e in ERROS:
        if not e["classe"]:
            continue
        mae = E.ERROS_POR_NOME[e["pai"]]
        assert issubclass(E.ERROS_POR_NOME[e["classe"]], mae)


def test_todo_codigo_tem_explicacao_no_catalogo():
    for e in ERROS:
        assert e["codigo"] in CATALOGO


def test_explain_acha_por_codigo_e_por_nome():
    assert buscar("DF0602")[0] == "DF0602"
    assert buscar("df0602")[0] == "DF0602"
    assert buscar("602")[0] == "DF0602"
    assert buscar("KeyError")[0] == "DF0602"
    assert buscar("KeyError_")[0] == "DF0602"
    assert buscar("nao existe") is None


def test_procura_encontra_por_assunto():
    assert any(e["codigo"] == "DF1201" for e in procurar("banco"))
    assert procurar("zzzznada") == []


# ─── 'handle' captura pela familia ─────────────────────────

def test_handle_generico_pega_o_especifico():
    assert rodar('''
monitor:
    out 1 / 0
handle RuntimeError as e:
    out e.type
''') == "DivisionByZeroError"


def test_handle_especifico_pega_o_especifico():
    assert rodar('''
monitor:
    out 1 / 0
handle DivisionByZeroError:
    out "sim"
''') == "sim"


def test_handle_de_outra_familia_nao_pega():
    with pytest.raises(E.DivisionByZeroError):
        rodar('''
monitor:
    out 1 / 0
handle IndexError:
    out "nao deveria"
''')


def test_handle_sem_tipo_pega_tudo():
    assert rodar('''
monitor:
    out {"a": 1}["b"]
handle e:
    out e.type
''') == "KeyError"


@pytest.mark.parametrize("nome", [
    "Error", "Exception", "Any", "DataForgeError",
])
def test_nomes_que_pegam_qualquer_erro(nome):
    assert rodar(f'''
monitor:
    out 1 / 0
handle {nome}:
    out "pego"
''') == "pego"


def test_halt_e_skip_atravessam_o_handle():
    """Desvio de fluxo nao e erro: 'monitor' nao pode engoli-lo."""
    assert rodar('''
cycle i from 1 to 5:
    monitor:
        given i is 3:
            halt
    handle e:
        out "nao devia capturar"
    out i
''') == "1\n2"


# ─── Excecao do Python vira erro da linguagem ──────────────

@pytest.mark.parametrize("fonte, esperado", [
    ("out [].min()",            "EmptyCollectionError"),
    ("out [1, 2].index_of(9)",  "ValueNotFoundError"),
    ('out int("abc")',          "ConversionError"),
    ("out [1, 2][::0]",         "SliceError"),
    ("out 10 % 0",              "DivisionByZeroError"),
    ("out 1 / 0",               "DivisionByZeroError"),
    ('out {"a": 1}["b"]',       "KeyError"),
    ("out [1, 2][9]",           "IndexError"),
])
def test_traducao_da_excecao(fonte, esperado):
    assert rodar(f'''
monitor:
    {fonte}
handle e:
    out e.type
''') == esperado


def test_nenhuma_excecao_do_python_escapa_capturavel():
    """A rede final: o que nao foi traduzido perto da causa vira erro aqui.

    Sem ela, uma chamada nova da stdlib do Python que levante algo
    inesperado volta a subir como 'Internal Error' incapturavel.
    """
    assert rodar('''
monitor:
    out [].pop()
handle e:
    out "capturado"
''') == "capturado"


# ─── O relatorio ───────────────────────────────────────────

def test_erro_de_lexer_diz_o_arquivo(tmp_path):
    """Regressao: erros de lexer e parser mostravam '<stdin>'."""
    from dataforge.errors import DataForgeError
    arquivo = tmp_path / "x.df"
    arquivo.write_text("x := 1\ny = 2\n", encoding="utf-8")
    with pytest.raises(DataForgeError) as exc:
        parse(tokenize(arquivo.read_text(encoding="utf-8"), str(arquivo)),
              str(arquivo))
    assert exc.value.filename == str(arquivo)


def test_erro_de_parser_diz_o_arquivo(tmp_path):
    from dataforge.errors import DataForgeError
    arquivo = tmp_path / "y.df"
    arquivo.write_text("x := \n", encoding="utf-8")
    with pytest.raises(DataForgeError) as exc:
        parse(tokenize(arquivo.read_text(encoding="utf-8"), str(arquivo)),
              str(arquivo))
    assert exc.value.filename == str(arquivo)


def test_erro_por_nome_aceita_as_duas_formas():
    assert E.erro_por_nome("TypeError") is E.TypeError_
    assert E.erro_por_nome("TypeError_") is E.TypeError_
    assert E.erro_por_nome("NaoExiste") is None
