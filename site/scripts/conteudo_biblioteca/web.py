# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de web.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Web as Web

out Web.encode_url("busca com espacos")
out Web.json_stringify({"acao": "criar"})
out Web.json_parse('{"a": 1}')`, title: `exemplo` }''',
]
