# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de functional.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Functional as F

nums := [5, 1, 4, 2, 8, 3]

out F.sort_by(lambda n: n, nums)
out F.chunk(2, nums)
out F.take_while(lambda n: n bigger 0, nums)
out F.unique_by(lambda n: n % 3, nums)
out F.group_by(lambda n: n % 2 is 0 and "par" or "impar", nums)`, title: `exemplo` }''',
]
