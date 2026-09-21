# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de async.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Async as Async

// Promessas e agendamento
tarefa := Async.promise(lambda: 42)
out Async.resolve(tarefa)`, title: `exemplo` }''',
]
