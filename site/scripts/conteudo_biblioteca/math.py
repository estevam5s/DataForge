# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de math.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Math as Math

out Math.sqrt(16), Math.factorial(5)
out Math.is_prime(97), Math.fibonacci(12)
out Math.gcd(48, 18), Math.lcm(4, 6)
out Math.clamp(15, 0, 10)

amostra := [12, 15, 11, 18, 20, 15]
out Math.mean(amostra), Math.median(amostra)
out round(Math.stdev(amostra), 4)`, title: `exemplo` }''',
]
