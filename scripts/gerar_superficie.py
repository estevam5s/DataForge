#!/usr/bin/env python3
"""Fotografa a superfície pública da linguagem.

Por que isto existe
-------------------
Uma promessa de estabilidade escrita em prosa não impede ninguém de
renomear um símbolo. Ela vira verdade quando alguma coisa **compara**.

Este arquivo produz `doc/superficie.json`: a lista de tudo o que um
programa de terceiro pode depender — palavras reservadas, funções
embutidas, módulos e seus símbolos, comandos da CLI e códigos de erro.
`tests/test_estabilidade.py` compara o que existe hoje com essa foto.

A regra que o teste aplica
--------------------------
**Acrescentar é livre. Tirar e renomear exigem decisão consciente.**

Um símbolo novo não quebra ninguém; um símbolo que some quebra todo
programa que o usava. Quando a remoção for mesmo o certo, atualiza-se a
foto no mesmo commit — e aí a mudança aparece no diff, com nome e
motivo, em vez de escapar no meio de um refactor.

Uso
---
    python scripts/gerar_superficie.py           # refotografa
    python scripts/gerar_superficie.py --check   # só compara
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca  # noqa: E402

marca.preparar_saida()

DESTINO = os.path.join(RAIZ, "doc", "superficie.json")


def fotografar():
    """O que um programa de fora pode tocar, hoje."""
    from dataforge import __version__
    from dataforge.builtins import get_builtins
    from dataforge.stdlib import get_module, _CANONICO
    from dataforge.tokens import KEYWORDS

    modulos = {}
    for oficial in sorted(set(_CANONICO.values())):
        conteudo = get_module(oficial)
        if isinstance(conteudo, dict):
            modulos[oficial] = sorted(
                k for k in conteudo if not k.startswith("__"))

    # Os apelidos contam: 'adopt Zip' é tão público quanto
    # 'adopt Arcane.Archive', e tirar um quebra código de verdade.
    apelidos = sorted(_CANONICO)

    # 'ERROS' e uma lista de fichas; o que e publico e o CODIGO, que
    # aparece na mensagem e em 'dataforge explicar DF0101'.
    try:
        from dataforge.catalogo_erros import ERROS
        codigos = sorted(ficha["codigo"] for ficha in ERROS)
    except Exception:                            # noqa: BLE001
        codigos = []

    try:
        from dataforge.cli import COMANDOS
        comandos = sorted(COMANDOS)
    except Exception:                            # noqa: BLE001
        comandos = []

    return {
        "versao": __version__,
        "palavras": sorted(KEYWORDS),
        "embutidas": sorted(get_builtins()),
        "modulos": modulos,
        "apelidos": apelidos,
        "comandos": comandos,
        "codigos_de_erro": codigos,
    }


def gravar(dados):
    with open(DESTINO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def carregar():
    if not os.path.exists(DESTINO):
        return None
    with open(DESTINO, encoding="utf-8") as f:
        return json.load(f)


def comparar(antes, agora):
    """O que SUMIU — e só isso, porque acrescentar é livre."""
    perdas = []

    for campo in ("palavras", "embutidas", "apelidos", "comandos",
                  "codigos_de_erro"):
        sumiram = sorted(set(antes.get(campo, [])) - set(agora.get(campo, [])))
        for nome in sumiram:
            perdas.append(f"{campo}: '{nome}'")

    modulos_antes = antes.get("modulos", {})
    modulos_agora = agora.get("modulos", {})
    for modulo in sorted(set(modulos_antes) - set(modulos_agora)):
        perdas.append(f"modulo inteiro: '{modulo}'")

    for modulo, simbolos in sorted(modulos_antes.items()):
        if modulo not in modulos_agora:
            continue
        sumiram = sorted(set(simbolos) - set(modulos_agora[modulo]))
        for nome in sumiram:
            perdas.append(f"{modulo}.{nome}")

    return perdas


def main():
    agora = fotografar()
    antes = carregar()

    if "--check" in sys.argv:
        if antes is None:
            print("  ainda nao ha foto — rode sem --check")
            return 1
        perdas = comparar(antes, agora)
        if perdas:
            print(f"  {len(perdas)} coisa(s) sumiram da superficie publica:")
            for p in perdas[:30]:
                print(f"    {p}")
            return 1
        novos = sum(
            len(set(agora["modulos"].get(m, [])) - set(s))
            for m, s in antes.get("modulos", {}).items())
        print(f"  nada sumiu. {novos} simbolo(s) novo(s) em modulos "
              f"existentes.")
        return 0

    gravar(agora)
    total = sum(len(v) for v in agora["modulos"].values())
    print(f"  {DESTINO}")
    print(f"  {len(agora['palavras'])} palavras, "
          f"{len(agora['embutidas'])} embutidas, "
          f"{len(agora['modulos'])} modulos ({total} simbolos), "
          f"{len(agora['comandos'])} comandos, "
          f"{len(agora['codigos_de_erro'])} codigos de erro")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
