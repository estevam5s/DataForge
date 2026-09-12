#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cada link de download baixa um arquivo de verdade?

    python3 scripts/verificar_downloads.py
    python3 scripts/verificar_downloads.py --site=http://localhost:3000

Por que existe
--------------
A página `/download` anunciava sete arquivos, e **nenhum existia**: não
havia release no repositório, e cada botão levava à página 404 do
GitHub.

Havia um teste sobre isso — e ele passava. Ele conferia que os nomes na
página batiam com o que o `release.yml` constrói: a coerência entre dois
arquivos do repositório. Nada checava se o arquivo estava publicado.

Uma trava que valida o mapa e não o território. Este script vai ao
território: pede cada arquivo e confere o código, o tamanho e o tipo.

O que ele NÃO faz
-----------------
Não baixa o conteúdo inteiro. `HEAD`, e um `GET` com `Range` quando o
servidor não responde a `HEAD` — sete arquivos de 12 MB a cada
verificação seria desperdício, e o que interessa é se o arquivo existe
e tem o tamanho certo.

Não roda no `pytest` por padrão: ele depende da rede e de um release
publicado, e um teste que falha por falta de internet ensina a ignorar
a suíte. Entra no `verificar_tudo.sh`, onde o silêncio não reprova.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.marca import preparar_saida          # noqa: E402

SITE = "https://dataforge-lang.vercel.app"

#: Abaixo disto, o "arquivo" é uma página de erro disfarçada.
#:
#: O 404 do GitHub responde **200** em alguns caminhos e devolve HTML de
#: ~10 KB. Conferir só o código de status deixaria isso passar, e o
#: usuário baixaria uma página HTML com o nome `.exe`.
MINIMO = 100 * 1024


def _cor(texto, codigo):
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return texto
    return f"\033[{codigo}m{texto}\033[0m"


def arquivos_da_pagina():
    """Os nomes que `/download` oferece, lidos da fonte."""
    caminho = os.path.join(RAIZ, "site", "app", "download", "page.tsx")
    with open(caminho, encoding="utf-8") as f:
        fonte = f.read()

    from dataforge import __version__
    achados = re.findall(r"\$\{RELEASES\}/([A-Za-z0-9_.${}-]+)", fonte)
    return sorted({n.replace("${VERSAO}", __version__) for n in achados})


def conferir(url):
    """`(ok, detalhe)` para um endereço.

    Segue redirecionamento — o rewrite do Vercel e o do GitHub para o
    armazenamento de assets são dois saltos, e recusá-los daria falso
    negativo em tudo.
    """
    pedido = urllib.request.Request(url, method="HEAD",
                                    headers={"User-Agent": "dataforge-check"})
    try:
        with urllib.request.urlopen(pedido, timeout=30) as r:
            tamanho = int(r.headers.get("Content-Length") or 0)
            tipo = r.headers.get("Content-Type", "")
            codigo = r.status
    except urllib.error.HTTPError as erro:
        if erro.code != 405:
            return False, f"HTTP {erro.code}"
        # Servidor que recusa HEAD: pedir o primeiro byte basta.
        return _conferir_por_range(url)
    except (urllib.error.URLError, TimeoutError) as erro:
        return None, f"sem resposta: {erro}"

    if codigo != 200:
        return False, f"HTTP {codigo}"
    if tamanho and tamanho < MINIMO:
        return False, (f"so {tamanho // 1024} KB — pequeno demais para um "
                       f"binario; provavelmente e uma pagina de erro")
    if "text/html" in tipo:
        return False, "devolveu HTML, e nao um arquivo"
    return True, f"{tamanho / (1024 * 1024):.1f} MB"


def _conferir_por_range(url):
    pedido = urllib.request.Request(
        url, headers={"User-Agent": "dataforge-check", "Range": "bytes=0-1023"})
    try:
        with urllib.request.urlopen(pedido, timeout=30) as r:
            faixa = r.headers.get("Content-Range", "")
            corpo = r.read(1024)
    except urllib.error.HTTPError as erro:
        return False, f"HTTP {erro.code}"
    except (urllib.error.URLError, TimeoutError) as erro:
        return None, f"sem resposta: {erro}"

    if corpo.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
        return False, "devolveu HTML, e nao um arquivo"
    total = faixa.split("/")[-1] if "/" in faixa else ""
    if total.isdigit() and int(total) < MINIMO:
        return False, f"so {int(total) // 1024} KB"
    return True, f"{int(total) / (1024 * 1024):.1f} MB" if total.isdigit() \
        else "existe"


def main():
    preparar_saida()
    argumentos = argparse.ArgumentParser(add_help=True)
    argumentos.add_argument("--site", default=SITE)
    opcoes = argumentos.parse_args()
    site = opcoes.site.rstrip("/")

    nomes = arquivos_da_pagina()
    print()
    print(f"  {_cor(site + '/download', '1;37')} — {len(nomes)} arquivo(s)")
    print()

    ruins = []
    sem_rede = 0
    for nome in nomes:
        ok, detalhe = conferir(f"{site}/baixar/{nome}")
        if ok is None:
            sem_rede += 1
            marca = _cor("?", "1;33")
        elif ok:
            marca = _cor("✓", "1;32")
        else:
            marca = _cor("✗", "1;31")
            ruins.append((nome, detalhe))
        print(f"    {marca} {nome:<44} {_cor(detalhe, '0;90')}")

    print()
    if sem_rede == len(nomes):
        print(_cor("  sem rede — nao deu para conferir nenhum", "1;33"))
        print()
        return 0            # offline não é reprovação
    if ruins:
        print(_cor(f"  {len(ruins)} link(s) quebrado(s):", "1;31"))
        for nome, motivo in ruins:
            print(f"    {nome}: {motivo}")
        print()
        print(_cor("  se o release nao existe, crie a tag:", "0;90"))
        print(_cor("    git tag -a v<versao> -m '…' && git push origin "
                   "v<versao>", "0;90"))
        print()
        return 1
    print(_cor(f"  os {len(nomes)} baixam", "1;32"))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
