# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de data.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Data as Data

registros := [
    {"nome": "Ana", "setor": "TI"},
    {"nome": "Bruno", "setor": "RH"}
]

out Data.group_by(registros, "setor").keys()`, title: `exemplo` }''',
]
