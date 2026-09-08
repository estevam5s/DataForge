#!/usr/bin/env python3
"""
Confere todo bloco de código DataForge publicado no site.

    python3 tools/verificar_docs.py           # só o relatório
    python3 tools/verificar_docs.py --lista   # mostra cada bloco ok

Um trecho na documentação que não compila ensina errado. Este script
extrai os blocos das páginas, separa o que é DataForge do que é shell ou
saída de terminal, e confere se o resto faz parse.

Fragmentos são tratados como fragmentos: `route GET "/x":` sozinho não é
um programa válido — as palavras do Kiln são contextuais e só valem
dentro de um bloco `server`. O script envolve esses trechos antes de
conferir, que é como eles serão usados.
"""

import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.lexer import tokenize                             # noqa: E402
from dataforge.parser import parse                               # noqa: E402

PAGINAS = os.path.join(RAIZ, "site", "app")

VERDE, VERMELHO, AMARELO, CINZA, LIMPO = (
    "\033[1;32m", "\033[1;31m", "\033[1;33m", "\033[0;90m", "\033[0m")

#: Começos que denunciam shell, não DataForge.
COMANDOS = (
    "dataforge", "df ", "npm", "npx", "pip", "python3", "curl", "wget",
    "docker", "git", "cd ", "ls ", "mkdir", "cp ", "rm ", "export",
    "alias", "irm ", "sudo", "chmod", "brew", "apt", "$", "#!", "sh ",
    "tar ", "shasum", "echo ", "cat ", "code ", "psql", "supabase",
    "DATAFORGE_", "FROM ", "RUN ", "COPY ", "CMD ", "ENV ", "EXPOSE",
    "LABEL", "WORKDIR", "select ", "SELECT ", "insert ", "create ",
)

#: Palavras do Kiln que só valem dentro de um bloco 'server'.
FRAGMENTOS_KILN = ("route ", "respond ", "render ", "redirect ",
                   "middleware ", "mount ", "assets ", "views ")

#: Palavras contextuais de blueprint — idem, mas dentro de blueprint.
FRAGMENTOS_BLUEPRINT = ("get ", "set ", "private ", "protected ",
                        "operator ", "final ", "abstract ")

#: Marcas de um bloco que **mostra o erro de propósito**. Conferir a
#: sintaxe deles seria exigir que o exemplo errado estivesse certo.
MARCAS_DE_ERRO = ("# ERRO", "// ERRO", "# erro:", "// erro:",
                  "# ruim", "// ruim", "# nunca entra", "# não compila")

#: Marcas de elipse: o bloco omite parte do código de propósito.
#: '{...}' não é um vault vazio, é "o que vier aqui".
ELIPSES = ("{...}", "{…}", "[...]", "…", "/* … */")


def blocos_das_paginas():
    """Todo `{ code: \\`…\\` }` das páginas, com a rota e a linha."""
    achados = []
    for pasta, _, arquivos in os.walk(PAGINAS):
        if "page.tsx" not in arquivos:
            continue
        caminho = os.path.join(pasta, "page.tsx")
        fonte = open(caminho, encoding="utf-8").read()
        relativo = os.path.relpath(pasta, PAGINAS).replace(os.sep, "/")
        rota = "/" if relativo == "." else "/" + relativo

        for m in re.finditer(
                r"\{\s*code:\s*`((?:[^`\\]|\\.)*)`([^}]*)\}", fonte, re.S):
            codigo, resto = m.group(1), m.group(2)
            # Um bloco marcado com outra linguagem não é DataForge.
            marca = re.search(r"lang:\s*'([^']+)'", resto)
            lingua = marca.group(1) if marca else ""
            codigo = (codigo.replace("\\`", "`")
                            .replace("\\${", "${")
                            .replace("\\\\", "\\"))
            linha = fonte[:m.start()].count("\n") + 1
            achados.append({
                "rota": rota, "arquivo": caminho, "linha": linha,
                "codigo": codigo, "lingua": lingua,
            })
    return achados


def classificar(bloco):
    """O que é este bloco, e como conferi-lo."""
    if bloco["lingua"] and bloco["lingua"] != "dataforge":
        return "outro"

    codigo = bloco["codigo"]
    linhas = [l for l in codigo.split("\n") if l.strip()]
    if not linhas:
        return "outro"

    primeira = linhas[0].strip()

    # Blocos que mostram o erro de propósito.
    if any(marca in codigo for marca in MARCAS_DE_ERRO):
        return "outro"

    # Elipse: o bloco omite parte do código de propósito.
    if any(l.strip() in ("...", "…", "# …", "// …") for l in linhas):
        return "outro"
    if any(marca in codigo for marca in ELIPSES):
        return "outro"

    # Duas ou mais linhas soltas que abrem bloco, e nada indentado, é uma
    # comparação lado a lado ("assim é claro / assim funciona mas…"),
    # não um programa. O comentário depois do ':' não muda isso, então
    # ele é removido antes da conta.
    sem_comentario = [re.sub(r"\s*(#|//).*$", "", l).rstrip() for l in linhas]
    abre_bloco = [l for l in sem_comentario if l.endswith(":")]
    indentadas = [l for l in linhas if l.startswith((" ", "\t"))]
    if len(abre_bloco) >= 2 and not indentadas:
        return "outro"

    # Um fragmento de match começa com 'point'.
    if primeira.startswith("point "):
        return "fragmento-match"

    # Saída de terminal: setas, ✓/✗, ou uma tabela desenhada.
    if any(marca in bloco["codigo"] for marca in ("→", "├", "└", "│", "✓ ", "✗ ")):
        return "outro"

    if any(primeira.startswith(c) for c in COMANDOS):
        return "outro"

    # Um bloco onde a maioria das linhas começa com comando é shell.
    comandos = sum(1 for l in linhas
                   if any(l.strip().startswith(c) for c in COMANDOS))
    if comandos > len(linhas) / 2:
        return "outro"

    # Um bloco pode misturar código solto com uma rota: envolvê-lo
    # inteiro num 'server' quebraria o que vem antes, então o
    # tratamento é por trecho (veja preparar()).
    if any(primeira.startswith(p) for p in FRAGMENTOS_KILN):
        return "fragmento-kiln"
    if any(re.match(rf"^\s*{p.strip()}\s", l) for l in linhas
           for p in ("route", "respond", "render", "redirect")):
        return "misto-kiln"
    if any(primeira.startswith(p) for p in FRAGMENTOS_BLUEPRINT):
        return "fragmento-blueprint"
    return "dataforge"


def preparar(codigo, tipo):
    """Envolve o fragmento no contexto em que ele será usado."""
    if tipo == "misto-kiln":
        # Cada trecho que começa com uma palavra do Kiln ganha o seu
        # 'server'; o resto fica como está. É como o leitor usará.
        saida, dentro = [], False
        for linha in codigo.split("\n"):
            abre = any(linha.startswith(p) for p in FRAGMENTOS_KILN)
            if abre and not dentro:
                saida.append("server s on 0:")
                dentro = True
            if dentro and linha.strip() and not linha.startswith((" ", "\t")):
                if not abre:
                    dentro = False
                    saida.append(linha)
                    continue
            saida.append("    " + linha if dentro and linha.strip() else linha)
        return "\n".join(saida)
    if tipo == "fragmento-match":
        recuado = "\n".join("    " + l for l in codigo.split("\n"))
        return "match valor:\n" + recuado
    if tipo == "fragmento-kiln":
        recuado = "\n".join("    " + l for l in codigo.split("\n"))
        return 'server s on 0:\n' + recuado
    if tipo == "fragmento-blueprint":
        recuado = "\n".join("    " + l for l in codigo.split("\n"))
        return "blueprint B:\n" + recuado
    return codigo


def main():
    blocos = blocos_das_paginas()
    contagem = {"dataforge": 0, "fragmento-kiln": 0,
                "fragmento-blueprint": 0, "fragmento-match": 0,
                "misto-kiln": 0, "outro": 0}
    falhas = []

    for bloco in blocos:
        tipo = classificar(bloco)
        contagem[tipo] += 1
        if tipo == "outro":
            continue
        try:
            parse(tokenize(preparar(bloco["codigo"], tipo)))
        except Exception as erro:
            falhas.append((bloco, tipo, str(erro)))
        else:
            if "--lista" in sys.argv:
                print(f"  {VERDE}✓{LIMPO} {bloco['rota']}:{bloco['linha']}")

    print(f"\n  {len(blocos)} blocos nas páginas")
    print(f"    {contagem['dataforge']} programas DataForge")
    print(f"    {contagem['fragmento-kiln']} fragmentos de rota")
    print(f"    {contagem['fragmento-blueprint']} fragmentos de blueprint")
    print(f"    {contagem['fragmento-match']} fragmentos de match")
    print(f"    {contagem['misto-kiln']} blocos com rota solta")
    print(f"    {contagem['outro']} shell, saída ou outra linguagem")

    if not falhas:
        conferidos = (contagem["dataforge"] + contagem["fragmento-kiln"]
                      + contagem["fragmento-blueprint"]
                      + contagem["fragmento-match"]
                      + contagem["misto-kiln"])
        print(f"\n  {VERDE}os {conferidos} blocos de DataForge compilam{LIMPO}\n")
        return 0

    print(f"\n  {VERMELHO}{len(falhas)} bloco(s) com erro de sintaxe{LIMPO}\n")
    for bloco, tipo, erro in falhas:
        print(f"  {VERMELHO}✗{LIMPO} {bloco['rota']}  "
              f"{CINZA}({os.path.relpath(bloco['arquivo'], RAIZ)}"
              f":{bloco['linha']}){LIMPO}")
        print(f"      {AMARELO}{erro.splitlines()[0][:110]}{LIMPO}")
        for linha in bloco["codigo"].strip().split("\n")[:4]:
            print(f"      {CINZA}{linha[:96]}{LIMPO}")
        print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
