#!/usr/bin/env python3
"""Refaz o "nesta página" de cada página da documentação.

O problema
----------
Cada `page.tsx` declara duas coisas: `blocos`, que é o conteúdo, e
`headings`, que é o índice lateral. As duas eram mantidas à mão, e
divergiram em **50 páginas** — seções que existem e não aparecem no
índice, e âncoras no índice que não levam a lugar nenhum porque o `id`
foi escrito diferente do que o componente calcula.

Ninguém percebe: a página abre, o texto está lá, e só o sumário mente.

A solução
---------
O índice passa a ser derivado do conteúdo, e não escrito ao lado dele.
O `id` sai da mesma `slugify` que o `<h2>` usa em `components/Doc.tsx` —
se as duas discordarem, o link quebra, então elas não podem ser duas
implementações.

Uso
---
    python site/scripts/gerar_indices.py            # reescreve
    python site/scripts/gerar_indices.py --check    # só confere
"""

import glob
import io
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = os.path.join(RAIZ, "app", "docs", "**", "page.tsx")

#: Os títulos dentro de `blocos`, na ordem em que aparecem.
_TITULO = re.compile(r'\{\s*"(h2|h3)"\s*:\s*"((?:[^"\\]|\\.)*)"')

#: A linha inteira do índice, para trocar de uma vez.
_INDICE = re.compile(r"^const headings = \[.*?\];$", re.MULTILINE | re.DOTALL)


def slugify(texto: str) -> str:
    """A mesma regra de `site/components/Doc.tsx`.

    Duas implementações da mesma coisa é como o `id` do índice deixou de
    bater com o `id` do título. Esta existe só porque o gerador é
    Python e o componente é TypeScript; há teste comparando as duas.
    """
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s-]", "", texto).strip()
    return re.sub(r"\s+", "-", texto)


def titulos_de(fonte: str):
    """Os `h2`/`h3` de `blocos`, como (nível, texto-cru).

    O texto sai **exatamente** como está escrito no arquivo, com os
    escapes intactos: reemiti-lo tem de dar o mesmo byte.
    """
    inicio = fonte.index("const blocos")
    fim = fonte.index("const headings")
    return [(m.group(1), m.group(2))
            for m in _TITULO.finditer(fonte[inicio:fim])]


def indice_de(titulos) -> str:
    if not titulos:
        return "const headings: never[] = [];"
    partes = []
    for nivel, cru in titulos:
        # O 'id' vem do texto RENDERIZADO, então os escapes precisam
        # virar os caracteres de verdade antes de passar pela slugify.
        legivel = cru.replace('\\"', '"').replace("\\\\", "\\")
        partes.append(
            f"{{ id: '{slugify(legivel)}', text: \"{cru}\", "
            f"level: {nivel[1]} as const }}")
    return "const headings = [" + ", ".join(partes) + "];"


def main() -> int:
    conferir = "--check" in sys.argv
    mudadas = []

    for caminho in sorted(glob.glob(PAGINAS, recursive=True)):
        fonte = io.open(caminho, encoding="utf-8").read()
        if "const headings" not in fonte or "const blocos" not in fonte:
            continue

        # 're.sub' com uma FUNCAO nao processa escapes no retorno — com
        # uma string, processaria, e um '\\"' do titulo viraria '\\\\"',
        # quebrando o TypeScript. Foi o que aconteceu na primeira versao.
        novo = _INDICE.sub(lambda _: indice_de(titulos_de(fonte)),
                           fonte, count=1)
        if novo == fonte:
            continue

        mudadas.append(os.path.relpath(caminho, RAIZ))
        if not conferir:
            io.open(caminho, "w", encoding="utf-8").write(novo)

    if conferir and mudadas:
        print(f"  {len(mudadas)} pagina(s) com o indice fora de sincronia:")
        for c in mudadas[:20]:
            print(f"    {c}")
        return 1

    print(f"  {len(mudadas)} indice(s) refeito(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
