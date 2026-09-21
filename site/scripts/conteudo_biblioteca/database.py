# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de database.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Database as DB

conn := DB.memory()
DB.execute(conn, "CREATE TABLE alunos (nome TEXT, nota REAL)")
DB.execute(conn, "INSERT INTO alunos VALUES (?, ?)", ["Ana", 9.5])

cycle linha in DB.query(conn, "SELECT nome, nota FROM alunos"):
    out $"{linha["nome"]}: {linha["nota"]}"

DB.close(conn)`, title: `exemplo` }''',
    r'''{"callout": {"tipo": "perigo", "titulo": "Sempre use parâmetros", "texto": "Nunca monte SQL com interpolação. Com `?`, o valor é enviado separado do comando e nunca é interpretado como SQL. Veja [Banco de dados](/docs/tecnicas/banco-de-dados)."}}''',
    r'''{"p": "Guia com contexto e boas práticas: [Database](/docs/tecnicas/banco-de-dados)."}''',
]
