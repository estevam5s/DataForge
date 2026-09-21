# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de process.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Process as Proc

r := Proc.run("echo ola do processo")
out r.stdout.trim(), r.exit_code, r.ok

out Proc.capture("echo direto")
out Proc.exists("echo")`, title: `exemplo` }''',
    r'''{"callout": {"tipo": "perigo", "texto": "Por padrão os comandos **não passam pelo shell** — isso previne injeção. Só use `shell := yes` quando precisar de pipes, e nunca com texto vindo do usuário."}}''',
    r'''{"p": "Guia com contexto e boas práticas: [Process](/docs/tecnicas/processos)."}''',
]
