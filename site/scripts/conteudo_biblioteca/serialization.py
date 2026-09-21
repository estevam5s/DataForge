# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de serialization.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Serialization as Serde

dados := {"app": "DataForge", "versao": 4, "web": {"porta": 8080}}

out Serde.to_json(dados)
out Serde.json_path(dados, "web.porta")
out Serde.flatten(dados)
out Serde.to_toml(dados)`, title: `exemplo` }''',
    r'''{"p": "Guia com contexto e boas práticas: [Serialization](/docs/tecnicas/serializacao)."}''',
]
