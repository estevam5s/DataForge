#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roda a trilha inteira e resume o resultado.

    python3 trilha/run_all.py            # tudo
    python3 trilha/run_all.py 08 12      # so estes capitulos

Por que ela existe
------------------
A trilha e a adaptacao integral de um material de Python para o
vocabulario desta linguagem — 45 capitulos, do primeiro 'out' as
arquiteturas. Um material assim envelhece rapido: uma mudanca no
interpretador invalida um exemplo, e quem le confia no texto.

Por isso cada capitulo e um '.df' que RODA e prova o que afirma com
'assert'. Um capitulo que deixou de ser verdade fica vermelho aqui, e
nao na cara de quem esta aprendendo.

Escrevendo a trilha, isto encontrou cinco defeitos reais na
linguagem — entre eles 'trigger' descartando o record levantado e
'typeof' respondendo com o nome do tipo do Python.
"""

import glob
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca                      # noqa: E402

marca.preparar_saida()

TRILHA = os.path.join(RAIZ, "trilha")
VERDE, VERMELHO, CINZA, BRANCO, RESET = (
    "\033[1;32m", "\033[1;31m", "\033[0;90m", "\033[1;37m", "\033[0m")


def _cor(texto, codigo):
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return texto
    return f"{codigo}{texto}{RESET}"


def capitulos(filtros):
    for caminho in sorted(glob.glob(os.path.join(TRILHA, "[0-9]*.df"))):
        nome = os.path.basename(caminho)
        if filtros and not any(f in nome for f in filtros):
            continue
        yield caminho, nome


def _motivo(saida):
    """A linha que EXPLICA, e nao a que fecha a moldura do erro."""
    limpas = [re.sub(r"\x1b\[[0-9;]*m", "", l).strip()
              for l in saida.strip().splitlines()]
    for linha in limpas:
        if re.match(r"erro\[[A-Z]+\d+\]", linha) or linha.startswith("erro:"):
            return linha
    for linha in reversed(limpas):
        if linha and not set(linha) <= set("─═│┌┐└┘├┤┬┴┼^ "):
            return linha
    return "(sem saida)"


def main():
    filtros = [a for a in sys.argv[1:] if not a.startswith("-")]
    itens = list(capitulos(filtros))
    if not itens:
        print("nenhum capitulo casou com o filtro")
        return 1

    print()
    falhas = []
    for caminho, nome in itens:
        r = subprocess.run(
            [sys.executable, "-m", "dataforge", "run", caminho, "--no-color"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=RAIZ)
        if r.returncode == 0:
            print(f"  {_cor('✓', VERDE)} {nome}")
        else:
            print(f"  {_cor('✗', VERMELHO)} {nome}")
            falhas.append((nome, _motivo(r.stdout + r.stderr)))

    print()
    if falhas:
        print(_cor(f"  {len(falhas)} de {len(itens)} capitulo(s) falharam:",
                   VERMELHO))
        for nome, motivo in falhas:
            print(f"    {nome}: {_cor(motivo, CINZA)}")
        print()
        return 1
    print(_cor(f"  {len(itens)}/{len(itens)} capitulos da trilha passaram",
               VERDE))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
