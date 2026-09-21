# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de http.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Http as Http

app := Http.create("Minha API")
Http.cors(app)

action listar(req, res):
    res.json([{"id": 1, "nome": "Primeiro"}])

Http.get(app, "/api/itens", listar)
Http.listen(app, 3000)`, title: `exemplo` }''',
    r'''{"callout": {"tipo": "nota", "texto": "`Http.listen` bloqueia: ele fica servindo até você interromper. Guia completo em [Servidor HTTP](/docs/tecnicas/http)."}}''',
    r'''{"p": "Guia com contexto e boas práticas: [Http](/docs/tecnicas/http)."}''',
]
