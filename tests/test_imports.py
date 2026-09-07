"""Importacao de modulos: caminhos relativos, selecao, re-exportacao."""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError, ImportError_   # noqa: E402
from dataforge.interpreter import Interpreter               # noqa: E402
from dataforge.lexer import tokenize                        # noqa: E402
from dataforge.parser import parse                          # noqa: E402


def rodar_arquivo(caminho):
    fonte = open(caminho, encoding="utf-8").read()
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, caminho), caminho), caminho)
    return saida.getvalue().strip()


@pytest.fixture
def projeto(tmp_path):
    """Um projetinho com lib/, sub/ e uma fachada."""
    (tmp_path / "lib").mkdir()
    (tmp_path / "sub").mkdir()
    (tmp_path / "lib" / "util.df").write_text(
        'action dobro(x):\n    yield x * 2\n\n'
        'steady VERSAO := "1.0"\n\nrelay dobro, VERSAO\n', encoding="utf-8")
    (tmp_path / "lib" / "mat.df").write_text(
        'action somar(a, b):\n    yield a + b\n\nrelay somar\n', encoding="utf-8")
    (tmp_path / "lib" / "index.df").write_text(
        'relay from ./util\nrelay from ./mat\n', encoding="utf-8")
    return tmp_path


def test_import_relativo_mesma_pasta(projeto):
    (projeto / "lib" / "usa.df").write_text(
        'adopt ./util as U\nout U.dobro(21)\n', encoding="utf-8")
    assert rodar_arquivo(str(projeto / "lib" / "usa.df")) == "42"


def test_import_relativo_pasta_abaixo(projeto):
    (projeto / "app.df").write_text(
        'adopt ./lib/util as U\nout U.dobro(10)\n', encoding="utf-8")
    assert rodar_arquivo(str(projeto / "app.df")) == "20"


def test_import_relativo_sobe_diretorio(projeto):
    (projeto / "sub" / "a.df").write_text(
        'adopt ../lib/util as U\nout U.dobro(5)\n', encoding="utf-8")
    assert rodar_arquivo(str(projeto / "sub" / "a.df")) == "10"


def test_relativo_resolve_pelo_arquivo_nao_pelo_cwd(projeto, monkeypatch):
    """Rodar de outra pasta nao pode mudar o que um import significa."""
    (projeto / "sub" / "a.df").write_text(
        'adopt ../lib/util as U\nout U.dobro(3)\n', encoding="utf-8")
    monkeypatch.chdir(os.path.dirname(str(projeto)))
    assert rodar_arquivo(str(projeto / "sub" / "a.df")) == "6"


def test_selecao_com_caminho_relativo(projeto):
    (projeto / "app.df").write_text(
        'adopt ./lib/util.{dobro}\nout dobro(4)\n', encoding="utf-8")
    assert rodar_arquivo(str(projeto / "app.df")) == "8"


def test_relay_from_monta_fachada(projeto):
    """Um index.df reune varios modulos internos numa API so."""
    (projeto / "app.df").write_text(
        'adopt ./lib/index as Lib\nout Lib.dobro(21)\nout Lib.somar(1, 2)\n',
        encoding="utf-8")
    assert rodar_arquivo(str(projeto / "app.df")) == "42\n3"


def test_fachada_nao_sobrescreve_nome_local(projeto):
    """O que o modulo define por conta propria vence o re-exportado."""
    (projeto / "lib" / "index2.df").write_text(
        'action dobro(x):\n    yield 999\n\n'
        'relay dobro\nrelay from ./util\n', encoding="utf-8")
    (projeto / "app.df").write_text(
        'adopt ./lib/index2 as L\nout L.dobro(1)\n', encoding="utf-8")
    assert rodar_arquivo(str(projeto / "app.df")) == "999"


def test_caminho_relativo_inexistente_diz_onde_procurou(projeto):
    (projeto / "app.df").write_text(
        'adopt ./lib/naoexiste as X\n', encoding="utf-8")
    with pytest.raises(ImportError_) as exc:
        rodar_arquivo(str(projeto / "app.df"))
    msg = str(exc.value)
    assert "naoexiste" in msg


def test_ciclo_e_detectado(projeto):
    (projeto / "a.df").write_text('adopt ./b as B\naction f():\n    yield 1\n'
                                  'relay f\n', encoding="utf-8")
    (projeto / "b.df").write_text('adopt ./a as A\naction g():\n    yield 2\n'
                                  'relay g\n', encoding="utf-8")
    with pytest.raises(DataForgeError) as exc:
        rodar_arquivo(str(projeto / "a.df"))
    assert "Circular" in str(exc.value)


def test_relay_de_nome_inexistente_sugere(projeto):
    (projeto / "x.df").write_text(
        'action dobro(n):\n    yield n\n\nrelay dobr\n', encoding="utf-8")
    (projeto / "app.df").write_text('adopt ./x as X\n', encoding="utf-8")
    with pytest.raises(DataForgeError) as exc:
        rodar_arquivo(str(projeto / "app.df"))
    # a mensagem cita o nome errado; a sugestao vem no campo 'dica'
    assert "dobr" in str(exc.value)
    assert "dobro" in exc.value.dica


def test_forma_pontilhada_continua_valendo(projeto):
    """A sintaxe antiga nao pode quebrar."""
    (projeto / "app.df").write_text(
        'adopt lib.util as U\nout U.dobro(7)\n', encoding="utf-8")
    assert rodar_arquivo(str(projeto / "app.df")) == "14"


def test_stdlib_continua_valendo():
    fonte = 'adopt Arcane.Math as M\nout M.floor(3.7)\n'
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    assert saida.getvalue().strip() == "3"
