# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de test.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Test as Test

action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

Test.assert_eq(fatorial(5), 120, "fatorial de 5")
Test.assert_true(fatorial(3) bigger fatorial(2), "cresce")
Test.assert_between(fatorial(4), 20, 30, "24 no intervalo")`, title: `exemplo` }''',
    r'''{"p": "Guia com contexto e boas práticas: [Test](/docs/tecnicas/testes)."}''',
]
