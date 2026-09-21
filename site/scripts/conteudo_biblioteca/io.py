# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de io.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.IO as IO

IO.write("_temp.txt", "linha 1\\nlinha 2")
out IO.read("_temp.txt").lines().length()
out IO.size("_temp.txt"), IO.ext("_temp.txt")
IO.delete("_temp.txt")`, title: `exemplo` }''',
    r'''{"p": "Guia com contexto e boas práticas: [IO](/docs/tecnicas/arquivos)."}''',
]
