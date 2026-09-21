# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de logging.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Logging as Log

registro := Log.logger("pedidos", "DEBUG")
registro.info("pedido recebido", {"id": 1042})
registro.warn("estoque baixo", {"restam": 3})
registro.error("pagamento recusado", {"codigo": 402})

out registro.stats()`, title: `exemplo` }''',
    r'''{"p": "Guia com contexto e boas práticas: [Logging](/docs/tecnicas/logging)."}''',
]
