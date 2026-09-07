"""CLI: catalogo de comandos, help, explain e as varreduras."""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import cli                                    # noqa: E402
from dataforge.diagnosticos import CATALOGO, buscar          # noqa: E402


def sem_cor(texto):
    import re
    return re.sub(r'\x1b\[[0-9;]*m', '', texto)


def saida_de(funcao, *args, **kwargs):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        funcao(*args, **kwargs)
    return sem_cor(buffer.getvalue())


# ─── Catalogo ──────────────────────────────────────────────

def test_todo_comando_do_catalogo_tem_resumo_e_uso():
    for _grupo, comandos in cli.GRUPOS:
        for c in comandos:
            assert c.resumo, f"{c.nome} sem resumo"
            assert c.uso.startswith("dataforge"), f"{c.nome}: uso estranho"


def test_apelidos_apontam_para_o_comando():
    assert cli.COMANDOS["rm"] is cli.COMANDOS["remove"]
    assert cli.COMANDOS["ls"] is cli.COMANDOS["list"]
    assert cli.COMANDOS["i"] is cli.COMANDOS["install"]


def test_veja_tambem_so_cita_comando_que_existe():
    """Um 'veja tambem' quebrado manda o usuario para o nada."""
    for _grupo, comandos in cli.GRUPOS:
        for c in comandos:
            for referido in c.veja:
                assert referido in cli.COMANDOS, \
                    f"{c.nome} aponta para '{referido}', que nao existe"


def test_help_geral_lista_todos_os_comandos():
    texto = sem_cor(cli.ajuda_geral())
    for _grupo, comandos in cli.GRUPOS:
        for c in comandos:
            assert c.nome in texto, f"'{c.nome}' fora do help"


def test_help_de_comando_traz_uso_e_exemplos():
    texto = sem_cor(cli.ajuda_comando("add"))
    assert "dataforge add" in texto
    assert "--offline" in texto
    assert "validador" in texto          # veio dos exemplos


def test_help_de_comando_inexistente_devolve_none():
    assert cli.ajuda_comando("naoexiste") is None


@pytest.mark.parametrize("errado,esperado", [
    ("instal", "install"),
    ("tets", "test"),
    ("chek", "check"),
    ("serach", "search"),
])
def test_sugere_o_comando_certo(errado, esperado):
    assert esperado in cli.comando_parecido(errado)


# ─── Diagnosticos ──────────────────────────────────────────

def test_busca_aceita_as_tres_formas():
    for forma in ("DF0601", "df0601", "0601"):
        achado = buscar(forma)
        assert achado is not None and achado[0] == "DF0601"


def test_codigo_desconhecido_devolve_none():
    assert buscar("DF9999") is None
    assert buscar("") is None


def test_todo_diagnostico_tem_titulo_e_explicacao():
    for codigo, dados in CATALOGO.items():
        assert dados["titulo"], f"{codigo} sem titulo"
        assert dados["explicacao"].strip(), f"{codigo} sem explicacao"
        assert codigo.startswith("DF") and len(codigo) == 6


def test_codigos_dos_erros_estao_no_catalogo():
    """Todo codigo que o runtime emite precisa ter explicacao."""
    from dataforge import errors

    classes = [errors.SyncError, errors.LexError, errors.ParseError,
               errors.RuntimeError_, errors.TypeError_, errors.NameError_,
               errors.ImportError_, errors.IndexError_, errors.TriggerError,
               errors.StackOverflowError_]
    for classe in classes:
        assert classe.CODIGO in CATALOGO, \
            f"{classe.__name__} emite {classe.CODIGO}, que nao esta catalogado"


def test_explain_imprime_a_explicacao():
    texto = saida_de(cli.explain_command, "DF0401")
    assert "DF0401" in texto
    assert "Nome nao definido" in texto
    assert "COMO RESOLVER" in texto


# ─── Varredura de arquivos ─────────────────────────────────

def test_expandir_ignora_dependencias_baixadas(tmp_path):
    """forge_modules e codigo de terceiros: nao entra na varredura."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "meu.df").write_text("out 1\n", encoding="utf-8")
    fm = tmp_path / "forge_modules" / "lib" / "src"
    fm.mkdir(parents=True)
    (fm / "main.df").write_text("out 2\n", encoding="utf-8")

    achados = cli._expandir([str(tmp_path)])
    assert any("meu.df" in a for a in achados)
    assert not any("forge_modules" in a for a in achados)


def test_expandir_respeita_alvo_explicito(tmp_path):
    """Pedir a pasta ignorada por nome analisa o que foi pedido."""
    fm = tmp_path / "forge_modules" / "lib"
    fm.mkdir(parents=True)
    (fm / "main.df").write_text("out 2\n", encoding="utf-8")

    achados = cli._expandir([str(fm)])
    assert len(achados) == 1


def test_expandir_ignora_pycache_e_venv(tmp_path):
    for pasta in ("__pycache__", ".venv", "node_modules"):
        d = tmp_path / pasta
        d.mkdir()
        (d / "x.df").write_text("out 1\n", encoding="utf-8")
    (tmp_path / "bom.df").write_text("out 1\n", encoding="utf-8")

    achados = cli._expandir([str(tmp_path)])
    assert len(achados) == 1 and achados[0].endswith("bom.df")
