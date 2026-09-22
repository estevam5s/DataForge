"""`Tg.dividir` e o teclado paginado.

O limite do Telegram é em unidades UTF-16 — um emoji vale dois. Um
teste que só usa ASCII passaria com a conta errada.
"""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402
from dataforge.stdlib.arcane_telegram import _unidades  # noqa: E402

Tg = get_module("Arcane.Telegram")


def test_texto_curto_e_um_pedaco_so():
    assert Tg["dividir"]("oi") == ["oi"]
    assert Tg["dividir"]("") == [""]


def test_nenhum_pedaco_passa_do_limite_em_utf16():
    texto = "😀" * 3000                    # 6000 unidades UTF-16
    pedacos = Tg["dividir"](texto)
    assert all(_unidades(p) <= 4096 for p in pedacos)
    assert "".join(pedacos) == texto       # nada perdido


def test_prefere_cortar_no_paragrafo():
    texto = ("a" * 30 + "\n\n") + ("b" * 30)
    assert Tg["dividir"](texto, 40) == ["a" * 30, "b" * 30]


def test_depois_na_linha_e_depois_no_espaco():
    assert Tg["dividir"]("aaaa bbbb\ncccc", 11) == ["aaaa bbbb", "cccc"]
    assert Tg["dividir"]("aaaa bbbb cccc", 11) == ["aaaa bbbb", "cccc"]


def test_palavra_maior_que_o_limite_e_cortada_no_meio():
    assert Tg["dividir"]("x" * 25, 10) == ["x" * 10, "x" * 10, "x" * 5]


def test_nao_separa_o_escape_do_markdown_da_barra():
    pedacos = Tg["dividir"]("a" * 9 + "\\." + "b" * 5, 10)
    assert not any(p.endswith("\\") and not p.endswith("\\\\") for p in pedacos)
    assert "".join(pedacos) == "a" * 9 + "\\." + "b" * 5


def test_limite_absurdo_e_recusado():
    with pytest.raises(Exception, match="ao menos 2"):
        Tg["dividir"]("abc", 1)


def test_paginado_monta_o_teclado_e_limita_a_pagina():
    p = Tg["paginado"](list(range(12)), 3, 5)
    assert p["itens"] == [10, 11] and p["paginas"] == 3
    linha = p["teclado"]["inline_keyboard"][0]
    assert [b["callback_data"] for b in linha] == ["pg:2", "pg:3"]
    # Um callback velho, de quando havia mais páginas, cai na última.
    assert Tg["paginado"](list(range(12)), 9, 5)["pagina"] == 3


def test_uma_pagina_so_nao_tem_teclado():
    assert Tg["paginado"]([1, 2], 1, 5)["teclado"] is None


def test_ler_pagina_so_aceita_o_proprio_prefixo():
    assert Tg["ler_pagina"]("pg:4") == 4
    assert Tg["ler_pagina"]("menu:4") is None
    assert Tg["ler_pagina"]("pg:x") is None
    assert Tg["ler_pagina"]("lista:2", "lista") == 2


def test_a_sonda_trata_id_negativo_como_grupo():
    """Antes, todo chat era privado — e ali `e_admin()` é sempre yes."""
    from dataforge.stdlib.arcane_telegram_app import _tipo_do_chat
    assert _tipo_do_chat(1001) == "private"
    assert _tipo_do_chat(-4567) == "group"
    assert _tipo_do_chat(-1001234567) == "supergroup"
    app = Tg["app"]("123456:TESTE-exemplo")
    vistos = []
    app.comando("quem", lambda ctx: vistos.append((ctx.e_grupo(), ctx.e_admin())))
    Tg["testar"](app, -100123).comando("quem")
    Tg["testar"](app, 1001).comando("quem")
    assert vistos == [(True, False), (False, True)]
