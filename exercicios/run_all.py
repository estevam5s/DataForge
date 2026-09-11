#!/usr/bin/env python3
"""Executa todos os exercicios DataForge e resume o resultado.

Uso:
    python3 exercicios/run_all.py            # roda tudo
    python3 exercicios/run_all.py 03 05      # roda apenas os modulos 03 e 05
"""

import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dataforge import marca  # noqa: E402

# A saida deste script tambem precisa sobreviver a um terminal que nao
# fala UTF-8. A CLI ja faz isto no comeco de 'main'; aqui nao fazia, e
# no Windows o relatorio de falha — que repete a ultima linha do
# exercicio, com acento e com os tracos das tabelas — estourava com
# UnicodeEncodeError ANTES de dizer qual exercicio falhou.
marca.preparar_saida()
EXERCICIOS = os.path.join(ROOT, "exercicios")
VERDE, VERMELHO, CINZA, RESET = "\033[1;32m", "\033[1;31m", "\033[0;90m", "\033[0m"


def modulos(filtros):
    for caminho in sorted(glob.glob(os.path.join(EXERCICIOS, "*"))):
        if not os.path.isdir(caminho):
            continue
        nome = os.path.basename(caminho)
        if filtros and not any(f in nome for f in filtros):
            continue
        yield caminho, nome


def main():
    filtros = sys.argv[1:]
    env = dict(os.environ, PYTHONPATH=ROOT)
    total_ok = total_falha = 0
    falhas = []

    for caminho, nome in modulos(filtros):
        ok = falha = 0
        for arquivo in sorted(glob.glob(os.path.join(caminho, "*.df"))):
            base = os.path.basename(arquivo)
            # Arquivos que comecam com letra sao modulos auxiliares (importados,
            # nao executados diretamente).
            if base[0].isalpha():
                continue
            proc = subprocess.run(
                [sys.executable, "-m", "dataforge", base, "--no-color"],
                capture_output=True, text=True, encoding="utf-8",
                timeout=120, cwd=caminho, env=env,
            )
            if proc.returncode == 0:
                ok += 1
            else:
                falha += 1
                saida = (proc.stdout + proc.stderr).strip().splitlines()
                falhas.append((nome, base, saida[-1] if saida else "sem saida"))

        total_ok += ok
        total_falha += falha
        cor = VERDE if falha == 0 else VERMELHO
        print(f"  {nome:<24} {cor}{ok:3d} ok{RESET}  {falha} falha(s)")

    print()
    for nome, base, msg in falhas:
        print(f"  {VERMELHO}FALHA{RESET} {nome}/{base}: {msg}")

    total = total_ok + total_falha
    cor = VERDE if total_falha == 0 else VERMELHO
    print(f"\n  {cor}{total_ok}/{total} exercicios passaram{RESET}")
    return 0 if total_falha == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
