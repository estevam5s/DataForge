"""O glossário aponta para páginas que existem.

Um glossário que manda para 404 ensina a não clicar — e o roadmap já
teve oito passos assim, com nomes de rota que "soavam certos".
"""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

E = get_module("Arcane.Ecossistema")


def test_todo_termo_aponta_para_uma_pagina_que_existe():
    faltam = []
    for item in E["glossario"]():
        pagina = os.path.join(RAIZ, "site", "app", item["pagina"].lstrip("/"),
                              "page.tsx")
        if not os.path.exists(pagina):
            faltam.append(f"{item['termo']} → {item['pagina']}")
    assert not faltam, "\n".join(faltam)


def test_os_termos_nao_se_repetem():
    termos = [i["termo"].lower() for i in E["glossario"]()]
    assert len(termos) == len(set(termos))


def test_definir_acha_sem_diferenciar_maiusculas_e_sugere():
    assert E["definir"]("ssa")["termo"] == "SSA"
    with pytest.raises(Exception) as info:
        E["definir"]("dominacia")
    assert "dominancia" in info.value.dica
