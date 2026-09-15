# -*- coding: utf-8 -*-
"""Arcane.Url — ler, montar e escapar endereços.

Todo programa que fala HTTP mexe com URL, e a linguagem não tinha onde: o
Kiln partia a query por dentro e o `Arcane.Http` montava endereço com
concatenação de texto. Escrever isso à mão tem dois bugs conhecidos — o
`?` que aparece dentro de um valor, e o acento que precisa virar `%C3%A9`.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError          # noqa: E402
from dataforge.interpreter import Interpreter        # noqa: E402
from dataforge.lexer import tokenize                 # noqa: E402
from dataforge.parser import parse                   # noqa: E402
from dataforge.stdlib import get_module              # noqa: E402

U = get_module("Arcane.Url")

ENDERECO = ("https://ana:s3nha@loja.com:8443/itens/42"
            "?pagina=2&q=caf%C3%A9&tag=a&tag=b#topo")


def rodar(fonte):
    interp = Interpreter()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        interp.run(parse(tokenize(fonte, "t.df"), "t.df"))
    return buffer.getvalue().strip()


# ── Ler ────────────────────────────────────────────────────

@pytest.mark.parametrize("campo,valor", [
    ("esquema", "https"),
    ("usuario", "ana"),
    ("senha", "s3nha"),
    ("host", "loja.com"),
    ("porta", 8443),
    ("caminho", "/itens/42"),
    ("fragmento", "topo"),
    ("query_texto", "pagina=2&q=caf%C3%A9&tag=a&tag=b"),
])
def test_ler_parte_o_endereco(campo, valor):
    assert U["ler"](ENDERECO)[campo] == valor


def test_a_porta_e_um_inteiro_e_sem_porta_e_void():
    """Texto faria 'porta + 1' concatenar. E sem porta é 'void', não 80 —
    inventar o padrão seria dizer o que a URL não disse."""
    assert U["ler"](ENDERECO)["porta"] == 8443
    assert U["ler"]("https://a.com/x")["porta"] is None


def test_a_origem_nao_leva_credencial():
    """'origem' vai para log e para cabeçalho de CORS: a senha vazaria."""
    origem = U["ler"](ENDERECO)["origem"]
    assert origem == "https://loja.com:8443"
    assert "s3nha" not in origem


def test_o_acento_volta_decodificado():
    assert U["ler"](ENDERECO)["query"]["q"] == "café"


def test_a_chave_repetida_fica_com_a_ultima_e_query_lista_traz_as_duas():
    lido = U["ler"](ENDERECO)
    assert lido["query"]["tag"] == "b"
    assert lido["query_lista"]["tag"] == ["a", "b"]


def test_uma_porta_impossivel_nao_derruba_a_leitura():
    """O resto da URL ainda é legível, e é o que se quer ver."""
    lido = U["ler"]("http://a.com:99999/x")
    assert lido["host"] == "a.com" and lido["porta"] is None


def test_e_absoluto():
    assert U["e_absoluto"]("https://a.com") is True
    assert U["e_absoluto"]("/itens") is False


# ── Montar ─────────────────────────────────────────────────

def test_montar_e_o_contrario_de_ler():
    partes = U["ler"]("https://a.com:8080/b/c?x=1#t")
    remontado = U["montar"]({k: partes[k] for k in U["campos"]()})
    assert remontado == "https://a.com:8080/b/c?x=1#t"


def test_montar_aceita_vault_na_query_e_escapa():
    assert U["montar"]({"esquema": "https", "host": "a.com", "caminho": "/b",
                        "query": {"q": "com espaço"}}) == \
        "https://a.com/b?q=com+espa%C3%A7o"


def test_montar_recusa_campo_que_nao_conhece():
    """'caminh' montaria um endereço sem caminho, sem nada denunciando."""
    with pytest.raises(DataForgeError) as erro:
        U["montar"]({"caminh": "/x"})
    assert "caminh" in str(erro.value)


def test_juntar_resolve_o_relativo_como_um_navegador():
    assert U["juntar"]("https://a.com/doc/x", "../y") == "https://a.com/y"
    assert U["juntar"]("https://a.com/doc/x", "/z") == "https://a.com/z"


def test_com_query_troca_um_parametro_e_preserva_os_outros():
    assert U["com_query"]("https://a.com/l?pagina=1&q=z", {"pagina": 3}) == \
        "https://a.com/l?pagina=1&q=z".replace("pagina=1", "pagina=3")


def test_void_em_com_query_apaga_o_parametro():
    """É como se tira um filtro de uma busca."""
    assert U["com_query"]("https://a.com/l?pagina=1&q=z", {"q": None}) == \
        "https://a.com/l?pagina=1"


def test_sem_query_tira_query_e_fragmento():
    assert U["sem_query"]("https://a.com/l?a=1#t") == "https://a.com/l"


# ── Query string ───────────────────────────────────────────

def test_query_texto_repete_a_chave_para_um_cluster():
    assert U["query_texto"]({"tag": ["a", "b"]}) == "tag=a&tag=b"


def test_um_booleano_sai_como_a_linguagem_escreve():
    """'True' é do Python; quem lê do outro lado é um .df."""
    assert U["query_texto"]({"ok": True, "nao": False}) == "ok=yes&nao=no"


def test_void_na_query_nao_vira_a_palavra_void():
    assert U["query_texto"]({"a": 1, "b": None}) == "a=1"


def test_query_e_query_lista_sao_o_contrario_de_query_texto():
    texto = U["query_texto"]({"tag": ["a", "b"], "p": 2})
    assert U["query_lista"](texto) == {"tag": ["a", "b"], "p": ["2"]}
    assert U["query"](texto) == {"tag": "b", "p": "2"}


def test_o_valor_vazio_e_preservado():
    """'?q=' é diferente de não ter 'q': é uma busca vazia."""
    assert U["query"]("q=") == {"q": ""}


# ── Escapar ────────────────────────────────────────────────

def test_escapar_preserva_a_barra_e_escapar_tudo_nao():
    assert U["escapar"]("/itens/ação") == "/itens/a%C3%A7%C3%A3o"
    assert U["escapar_tudo"]("/itens/ação") == "%2Fitens%2Fa%C3%A7%C3%A3o"


def test_desescapar_volta_o_acento_e_o_mais():
    assert U["desescapar"]("caf%C3%A9+quente") == "café quente"


# ── Pela linguagem ─────────────────────────────────────────

def test_o_modulo_funciona_pela_linguagem():
    assert rodar('adopt Arcane.Url as U\n'
                 'p := U.ler("https://a.com/x?n=1")\n'
                 'out p["host"], p["query"]["n"]\n') == "a.com 1"


def test_o_apelido_curto_responde_pelo_nome_oficial():
    assert rodar('adopt Url as U\nout U.host_de("https://a.com/x")') == "a.com"
    assert get_module("Endereco")["__name__"] == "Arcane.Url"


def test_um_texto_que_nao_e_texto_e_recusado_com_o_nome_do_tipo():
    with pytest.raises(DataForgeError) as erro:
        U["ler"](42)
    assert "Integer" in str(erro.value)
