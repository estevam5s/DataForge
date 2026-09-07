#!/usr/bin/env python3
"""Gera o tarball do DataForge que o site serve para os instaladores.

    python3 scripts/gerar_tarball.py

Escreve site/public/dist/dataforge-<versao>.tar.gz e o .sha256 ao lado.
A versao vem de dataforge/__init__.py — nao ha numero repetido a mao.

Roda isto sempre que a versao mudar: o instalador baixa deste arquivo.
"""

import hashlib
import os
import pathlib
import sys
import tarfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dataforge import __version__ as VERSAO  # noqa: E402

# O que o pacote instalavel precisa. Exercicios, exemplos, testes e o
# site ficam de fora: sao dezenas de MB que ninguem baixa para rodar
# 'dataforge run'. Quem quer isso clona o repositorio.
INCLUIR = ["dataforge", "pyproject.toml", "README.md", "LICENSE", "CLAUDE.md", "doc"]
IGNORAR = {"__pycache__", ".pyc", ".DS_Store", ".pytest_cache", "dist", ".egg-info"}


def filtrar(info):
    if any(marca in info.name for marca in IGNORAR):
        return None
    # tarball reproduzivel: mesmo fonte, mesmo sha256
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    return info


def main():
    saida = RAIZ / "site" / "public" / "dist"
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / f"dataforge-{VERSAO}.tar.gz"

    with tarfile.open(destino, "w:gz") as tar:
        for item in INCLUIR:
            caminho = RAIZ / item
            if caminho.exists():
                tar.add(caminho, arcname=f"dataforge-{VERSAO}/{item}",
                        filter=filtrar)
            else:
                print(f"  aviso: {item} nao existe, pulando")

    sha = hashlib.sha256(destino.read_bytes()).hexdigest()
    (saida / f"dataforge-{VERSAO}.tar.gz.sha256").write_text(
        f"{sha}  dataforge-{VERSAO}.tar.gz\n", encoding="utf-8")

    print(f"{destino.relative_to(RAIZ)}")
    print(f"  {destino.stat().st_size / 1024:.0f} KB")
    print(f"  sha256 {sha}")

    # Os instaladores tem a versao embutida como padrao. Se ela divergir,
    # quem roda o curl baixa um arquivo que nao existe — foi o que
    # aconteceu no 4.1.0, porque havia duas copias do script e so uma foi
    # atualizada. Agora a copia publicada e gerada aqui, sempre.
    problemas = []
    for origem, destino in [("scripts/instalar.sh", "site/public/instalar.sh"),
                            ("scripts/instalar.ps1", "site/public/instalar.ps1")]:
        fonte = RAIZ / origem
        if not fonte.exists():
            continue
        texto = fonte.read_text(encoding="utf-8")
        if VERSAO not in texto:
            problemas.append(f"{origem} nao menciona {VERSAO}")
        alvo = RAIZ / destino
        alvo.write_text(texto, encoding="utf-8")
        alvo.chmod(fonte.stat().st_mode)
        print(f"  {destino} <- {origem}")

    if problemas:
        print("\n  ATENCAO:")
        for p_ in problemas:
            print(f"    {p_}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
