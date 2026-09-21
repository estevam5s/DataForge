# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de crypto.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Crypto as Crypto

out Crypto.sha256("DataForge")[0:16]

guardada := Crypto.hash_password("minha-senha")
out Crypto.verify_password("minha-senha", guardada)
out Crypto.verify_password("outra", guardada)

out Crypto.mask("4111111111111111")
out Crypto.random_token(12)`, title: `exemplo` }''',
    r'''{"callout": {"tipo": "atencao", "texto": "`md5` e `sha1` existem para compatibilidade (checksums), **não para senhas**. Para senha, use `hash_password` / `verify_password`, que aplicam PBKDF2 com sal."}}''',
    r'''{"p": "Guia com contexto e boas práticas: [Crypto](/docs/tecnicas/criptografia)."}''',
]
