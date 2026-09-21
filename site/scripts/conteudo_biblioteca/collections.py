# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de collections.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Collections as Col

g := Col.graph()
g.add_edge("casa", "mercado", 3)
g.add_edge("mercado", "trabalho", 4)
g.add_edge("casa", "trabalho", 10)
out g.shortest_path("casa", "trabalho")

fila := Col.priority_queue()
fila.push("rotina", 5)
fila.push("urgente", 1)
out fila.pop()`, title: `exemplo` }''',
    r'''{"p": "As estruturas são objetos com métodos próprios (`push`, `pop`, `add_edge`…), não vaults. Chame-os diretamente: `fila.push(x)`."}''',
]
