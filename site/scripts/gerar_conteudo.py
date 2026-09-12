"""Gera as páginas .tsx a partir das definições em scripts/conteudo/.

As páginas do site são dados: uma lista de blocos por página. Este
script transforma esses dados nos componentes React que o Next compila.

Escrever .tsx à mão para 200 páginas produziria 200 variações do mesmo
markup. Aqui a moldura é uma só, e o que muda é o conteúdo.
"""
import importlib
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerar_paginas import escrever  # noqa: E402

#: Os módulos de conteúdo, na ordem em que aparecem na navegação.
MODULOS = [
    "big_o",
    "oop_avancado",
    "oop_magicos",
    "exercicios",
    "lsp",
    "editor",
    "dados",
    "lago",
    "ml",
    "fluxo",
    "banco",
    "banco_sqlite",
    "kiln_extra",
    "microservicos",
    "devops",
    "crucible_doc",
    "vitrine",
    "versoes",
]


def main():
    total = 0
    for nome in MODULOS:
        try:
            modulo = importlib.import_module(f"conteudo.{nome}")
        except ModuleNotFoundError:
            print(f"  (pulando {nome}: ainda não existe)")
            continue
        for pagina in modulo.PAGINAS:
            # De onde veio, para o aviso no topo da pagina gerada poder
            # apontar o arquivo que a pessoa precisa abrir.
            pagina.setdefault("fonte", f"site/scripts/conteudo/{nome}.py")
            escrever(pagina)
            total += 1
            print(f"  {pagina['href']}")
    print(f"\n  {total} página(s) geradas")


if __name__ == "__main__":
    main()
