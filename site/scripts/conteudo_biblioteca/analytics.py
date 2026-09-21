# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de analytics.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Analytics as An

x := [1, 2, 3, 4, 5]
y := [2, 4, 6, 8, 10]

out round(An.correlation(x, y), 4)
out An.quartiles(x)
out An.outliers([10, 11, 12, 200])

modelo := An.linear_regression(x, y)
out round(modelo["slope"], 2), round(An.predict_linear(modelo, 6), 2)`, title: `exemplo` }''',
]
