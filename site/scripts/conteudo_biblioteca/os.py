# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de os.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.OS as OS

out $"{OS.name()} {OS.arch()} com {OS.cpu_count()} CPUs"
out $"disco livre: {OS.disk_usage().free_gb} GB"
out $"usuario: {OS.user()}"
out OS.get_env("PATH_INEXISTENTE", "(padrao)")`, title: `exemplo` }''',
]
