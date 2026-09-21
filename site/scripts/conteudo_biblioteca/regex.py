# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de regex.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Regex as Regex

texto := "contato: ana@exemplo.com, tel (48) 99999-1234"

out Regex.extract_emails(texto)
out Regex.extract_numbers(texto)
out Regex.is_email("ana@exemplo.com")
out Regex.is_cpf("529.982.247-25")
out Regex.replace_all("\\\\d", "#", "abc123")`, title: `exemplo` }''',
]
