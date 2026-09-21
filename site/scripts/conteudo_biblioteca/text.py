# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de text.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Text as Text

out Text.box("Relatorio")
out Text.slug("Ola Mundo DataForge!")
out Text.snake_case("MinhaVariavelLegal")
out Text.truncate("frase bem longa demais", 10)
out Text.number_format(1234567.891, 2)

cabecalho := ["Produto", "Qtd"]
linhas := [["Mouse", "12"], ["Teclado", "5"]]
out Text.table(cabecalho, linhas)`, title: `exemplo` }''',
]
