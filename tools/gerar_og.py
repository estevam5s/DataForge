#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a imagem de previa que aparece quando alguem compartilha o site.

Por que este arquivo existe
---------------------------
O 'openGraph.images' apontava para um **SVG**. Nenhuma das redes que
mostram previa aceita SVG — nem o Facebook, nem o LinkedIn, nem o
WhatsApp, o Discord ou o Telegram. O link era compartilhado e aparecia
sem imagem nenhuma, que e o pior resultado possivel: o card fica pior
do que se nao houvesse metadado.

Tres numeros que as redes cobram, e que o banner sozinho nao atende:

    proporcao   1.91:1   o banner e 2.98:1 e seria cortado em cima e
                         embaixo, comendo metade do conteudo
    tamanho     1200x630 o que o Facebook e o LinkedIn pedem
    peso        < 300 KB acima disso o WhatsApp costuma desistir da
                         previa; o banner tem 1,3 MB

Entao a imagem e MONTADA: o banner em cima, o titulo embaixo e a
descricao embaixo dele — que e como um card se le, de cima para baixo.

    python3 tools/gerar_og.py            # regera
    python3 tools/gerar_og.py --check    # so confere
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import marca                            # noqa: E402

marca.preparar_saida()

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLICO = os.path.join(RAIZ, "site", "public")
BANNER = os.path.join(PUBLICO, "banner.png")

#: 1200x630 e a medida que o Facebook e o LinkedIn pedem, e a que o
#: Twitter/X usa no 'summary_large_image'. Qualquer outra e recortada.
LARGURA, ALTURA = 1200, 630

FUNDO = (8, 6, 6)
AMARELO = (250, 204, 21)
BRANCO = (245, 245, 247)
CINZA = (154, 154, 164)
LINHA = (38, 34, 34)

NEGRITO = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
NORMAL = "/System/Library/Fonts/Supplemental/Arial.ttf"

#: Cada pagina que vale ser compartilhada sozinha tem a sua.
CARDS = [
    {
        "arquivo": "og.png",
        "titulo": "DataForge",
        "descricao": "Uma linguagem de programação completa, em português, "
                     "com 40 módulos de biblioteca, dois frameworks web e "
                     "uma consulta tipada própria.",
    },
    {
        "arquivo": "og-docs.png",
        "titulo": "Documentação do DataForge",
        "descricao": "Mais de 190 páginas, 234 exercícios que verificam o "
                     "próprio resultado, e cada trecho de código compilado "
                     "a cada mudança.",
    },
    {
        "arquivo": "og-lavra.png",
        "titulo": "Lavra — a consulta tipada",
        "descricao": "O cliente diz exatamente quais campos quer, e recebe "
                     "exatamente aqueles. O esquema nasce dos seus records.",
    },
]


def _fonte(caminho, tamanho):
    try:
        return ImageFont.truetype(caminho, tamanho)
    except OSError:
        return ImageFont.load_default()


def _quebrar(texto, fonte, desenho, largura_maxima):
    """Quebra o texto em linhas que cabem. Palavra inteira, nunca no meio."""
    linhas, atual = [], []
    for palavra in texto.split():
        tentativa = " ".join(atual + [palavra])
        if desenho.textlength(tentativa, font=fonte) <= largura_maxima:
            atual.append(palavra)
        else:
            if atual:
                linhas.append(" ".join(atual))
            atual = [palavra]
    if atual:
        linhas.append(" ".join(atual))
    return linhas


def montar(titulo, descricao):
    tela = Image.new("RGB", (LARGURA, ALTURA), FUNDO)
    desenho = ImageDraw.Draw(tela)

    # ── O banner, no topo, na largura inteira ──
    banner = Image.open(BANNER).convert("RGB")
    altura_banner = round(LARGURA * banner.height / banner.width)
    banner = banner.resize((LARGURA, altura_banner), Image.LANCZOS)
    tela.paste(banner, (0, 0))

    # Uma linha fina separa o banner do texto. Sem ela, o preto do
    # banner e o preto do fundo viram a mesma mancha e o titulo parece
    # flutuar dentro da arte.
    desenho.line([(0, altura_banner), (LARGURA, altura_banner)],
                 fill=LINHA, width=2)

    margem = 64
    y = altura_banner + 38

    fonte_titulo = _fonte(NEGRITO, 46)
    desenho.text((margem, y), titulo, font=fonte_titulo, fill=BRANCO)
    y += 60

    fonte_desc = _fonte(NORMAL, 25)
    for linha in _quebrar(descricao, fonte_desc, desenho,
                          LARGURA - margem * 2)[:3]:
        desenho.text((margem, y), linha, font=fonte_desc, fill=CINZA)
        y += 34

    # A barra amarela na borda de baixo: a marca aparece mesmo quando a
    # rede recorta o card em proporcao diferente.
    desenho.rectangle([(0, ALTURA - 6), (LARGURA, ALTURA)], fill=AMARELO)
    return tela


def gravar(tela, caminho):
    """Grava com peso controlado.

    O WhatsApp costuma desistir da previa acima de ~300 KB, e um PNG de
    1200x630 com uma foto passa disso facil. A paleta adaptativa de 256
    cores resolve sem custo visivel — a arte e de duas cores e preto.
    """
    reduzida = tela.convert("P", palette=Image.ADAPTIVE, colors=256)
    reduzida.save(caminho, "PNG", optimize=True)
    if os.path.getsize(caminho) > 300 * 1024:
        tela.save(caminho, "PNG", optimize=True)
    return os.path.getsize(caminho)


def main():
    conferir = "--check" in sys.argv
    problemas = []
    for card in CARDS:
        destino = os.path.join(PUBLICO, card["arquivo"])
        tela = montar(card["titulo"], card["descricao"])
        if conferir:
            if not os.path.isfile(destino):
                problemas.append(f"{card['arquivo']} nao existe")
                continue
            atual = Image.open(destino).convert("RGB")
            if atual.size != (LARGURA, ALTURA):
                problemas.append(
                    f"{card['arquivo']} e {atual.size}, e as redes pedem "
                    f"{LARGURA}x{ALTURA}")
            continue
        tamanho = gravar(tela, destino)
        print(f"  {card['arquivo']}  {LARGURA}x{ALTURA}  "
              f"{tamanho / 1024:.0f} KB")

    if problemas:
        print("\n".join("  ✗ " + p for p in problemas))
        return 1
    if conferir:
        print("  as imagens de previa estao em dia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
