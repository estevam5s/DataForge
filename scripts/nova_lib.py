#!/usr/bin/env python3
"""Cria o esqueleto de um pacote em packages/<nome>/.

    python3 scripts/nova_lib.py <nome> "<descricao>" "tag1,tag2"

Escreve o forge.toml, src/main.df e tests/. O conteudo real vem depois.
"""
import os
import sys

MANIFESTO = '''[package]
name = "{nome}"
version = "1.0.0"
description = "{descricao}"
authors = ["DataForge"]
license = "MIT"
entry = "src/main.df"
dataforge = ">=1.0"
keywords = [{tags}]

[dependencies]

[scripts]
test = "test tests/"
'''


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    nome, descricao = sys.argv[1], sys.argv[2]
    tags = sys.argv[3] if len(sys.argv) > 3 else ""
    tags_toml = ", ".join(f'"{t.strip()}"' for t in tags.split(",") if t.strip())

    base = os.path.join("packages", nome)
    os.makedirs(os.path.join(base, "src"), exist_ok=True)
    os.makedirs(os.path.join(base, "tests"), exist_ok=True)

    with open(os.path.join(base, "forge.toml"), "w", encoding="utf-8") as f:
        f.write(MANIFESTO.format(nome=nome, descricao=descricao,
                                 tags=tags_toml))
    print(f"packages/{nome}/  criado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
