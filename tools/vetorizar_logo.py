#!/usr/bin/env python3
"""
Vetoriza o logo do DataForge: logo.png -> SVG de um caminho so.

    python3 tools/vetorizar_logo.py

O logo e uma silhueta de duas cores. Isso torna a vetorizacao viavel sem
potrace: separa-se a figura do fundo por limiar, segue-se a fronteira de
cada regiao, simplifica-se com Douglas-Peucker e suaviza-se com Beziers.

O resultado e um unico <path> com fill-rule="evenodd" — os buracos
(olho, boca, vaos entre as garras) sao subcaminhos no sentido inverso.
Um caminho so importa: e ele que vira favicon, icone do editor, marca no
cabecalho e glifo monocromatico, sempre herdando a cor de quem o usa.
"""

import os
import sys

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(RAIZ, "logo.png")

#: Abaixo disto, o pixel e fundo. O logo tem amarelo saturado sobre
#: preto, entao qualquer limiar no meio serve; 128 e o meio.
LIMIAR = 128

#: Quanto o Douglas-Peucker pode desviar, em pixels da imagem original.
#: 0.8 mantem as garras e o desenho do olho; acima de 1.5 elas somam.
TOLERANCIA = 0.8

#: Regioes menores que isto sao ruido de anti-aliasing, nao desenho.
AREA_MINIMA = 60

#: A cor da marca onde ela nao pode herdar a do contexto: favicon,
#: apple-touch-icon e o icone do editor.
#:
#: E o amarelo do proprio logo.png (#FED403), nao o vermelho do site: a
#: marca tem uma cor, e ela nao muda porque o tema da pagina e outro.
COR_MARCA = "#FED403"

#: O preto do fundo do logo. Um icone de favicon precisa de fundo
#: proprio — o amarelo sobre a barra clara do navegador some.
FUNDO_MARCA = (10, 10, 12, 255)


def carregar_mascara(caminho):
    """A figura como matriz booleana, com uma borda de fundo em volta.

    A borda garante que nenhuma regiao encoste no limite da imagem — o
    seguidor de fronteira precisa de um vizinho fora, sempre.
    """
    imagem = Image.open(caminho).convert("L")
    dados = np.array(imagem) > LIMIAR
    return np.pad(dados, 1, constant_values=False)


def rotular(mascara):
    """Componentes conexas por inundacao iterativa (4-vizinhos).

    Iterativa de proposito: recursao estoura a pilha do Python num
    logo de 1254x1254.
    """
    altura, largura = mascara.shape
    rotulos = np.zeros((altura, largura), dtype=np.int32)
    atual = 0
    for y in range(altura):
        for x in range(largura):
            if not mascara[y, x] or rotulos[y, x]:
                continue
            atual += 1
            pilha = [(y, x)]
            rotulos[y, x] = atual
            while pilha:
                cy, cx = pilha.pop()
                for ny, nx in ((cy - 1, cx), (cy + 1, cx),
                               (cy, cx - 1), (cy, cx + 1)):
                    if (0 <= ny < altura and 0 <= nx < largura
                            and mascara[ny, nx] and not rotulos[ny, nx]):
                        rotulos[ny, nx] = atual
                        pilha.append((ny, nx))
    return rotulos, atual


def seguir_fronteira(mascara, inicio):
    """Contorno de uma regiao pelo algoritmo de Moore.

    Anda pela borda mantendo a figura a esquerda. Devolve os vertices em
    coordenadas de canto de pixel, nao de centro: assim as arestas caem
    exatamente entre os pixels e nao ha meio pixel de erro.
    """
    altura, largura = mascara.shape
    vizinhos = [(0, 1), (1, 1), (1, 0), (1, -1),
                (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    contorno = [inicio]
    atual = inicio
    direcao = 7
    primeiro_passo = True

    while True:
        achou = False
        for volta in range(8):
            d = (direcao + volta) % 8
            dy, dx = vizinhos[d]
            ny, nx = atual[0] + dy, atual[1] + dx
            if 0 <= ny < altura and 0 <= nx < largura and mascara[ny, nx]:
                atual = (ny, nx)
                # Volta duas casas: e onde a proxima busca deve comecar
                # para nao pular um vizinho da diagonal.
                direcao = (d + 5) % 8
                achou = True
                break
        if not achou:
            break                       # pixel isolado
        if atual == inicio and not primeiro_passo:
            break
        primeiro_passo = False
        contorno.append(atual)
        if len(contorno) > 4 * altura * largura:
            break                       # cinto de seguranca
    return contorno


def douglas_peucker(pontos, tolerancia):
    """Simplifica mantendo os vertices que importam."""
    if len(pontos) < 3:
        return pontos

    inicio, fim = np.array(pontos[0]), np.array(pontos[-1])
    reta = fim - inicio
    tamanho = np.hypot(*reta)

    if tamanho == 0:
        distancias = [np.hypot(*(np.array(p) - inicio)) for p in pontos[1:-1]]
    else:
        normal = np.array([-reta[1], reta[0]]) / tamanho
        distancias = [abs(np.dot(np.array(p) - inicio, normal))
                      for p in pontos[1:-1]]

    if not distancias:
        return [pontos[0], pontos[-1]]

    maior = max(distancias)
    if maior <= tolerancia:
        return [pontos[0], pontos[-1]]

    corte = distancias.index(maior) + 1
    esquerda = douglas_peucker(pontos[:corte + 1], tolerancia)
    direita = douglas_peucker(pontos[corte:], tolerancia)
    return esquerda[:-1] + direita


def suavizar(pontos, k=0.32):
    """Poligono fechado -> Beziers cubicas, estilo Catmull-Rom.

    Sem isto o logo fica facetado: um contorno organico simplificado a
    0.8 px tem centenas de segmentos retos, visiveis acima de 64 px.

    O detalhe que importa: a alca de cada ponto de controle e escalada
    pelo **comprimento do proprio segmento**, nao pela distancia entre
    os vizinhos. O Douglas-Peucker deixa segmentos de tamanhos muito
    diferentes; com a formula ingenua (p1 + (p2-p0)*t), um segmento
    curto entre dois longos ganha uma alca maior que ele mesmo, a curva
    da um laco, e com fill-rule evenodd o laco inverte o preenchimento
    — o logo inteiro vira um bloco cheio.
    """
    n = len(pontos)
    if n < 3:
        return []

    def direcao(a, b):
        """Vetor unitario de a para b, ou zero se coincidem."""
        v = b - a
        norma = np.hypot(*v)
        return v / norma if norma > 1e-9 else v * 0

    segmentos = []
    for i in range(n):
        p0 = np.array(pontos[(i - 1) % n], dtype=float)
        p1 = np.array(pontos[i], dtype=float)
        p2 = np.array(pontos[(i + 1) % n], dtype=float)
        p3 = np.array(pontos[(i + 2) % n], dtype=float)

        comprimento = np.hypot(*(p2 - p1))
        # A tangente aponta na direcao p0->p2 (a media local), mas o
        # tamanho da alca vem do segmento que estamos desenhando.
        t1 = direcao(p0, p2)
        t2 = direcao(p1, p3)
        c1 = p1 + t1 * comprimento * k
        c2 = p2 - t2 * comprimento * k
        segmentos.append((c1, c2, p2))
    return segmentos


def numero(valor):
    """Duas casas, sem zeros a toa — o SVG fica bem menor."""
    texto = f"{valor:.2f}".rstrip("0").rstrip(".")
    return texto if texto not in ("", "-0") else "0"


def caminho_svg(contornos, escala, deslocamento):
    """Os contornos como um unico atributo 'd'."""
    partes = []
    for pontos in contornos:
        transformados = [((x - deslocamento[0]) * escala,
                          (y - deslocamento[1]) * escala) for y, x in pontos]
        curvas = suavizar(transformados)
        if not curvas:
            continue
        inicio = transformados[0]
        partes.append(f"M{numero(inicio[0])} {numero(inicio[1])}")
        for c1, c2, fim in curvas:
            partes.append(
                f"C{numero(c1[0])} {numero(c1[1])} "
                f"{numero(c2[0])} {numero(c2[1])} "
                f"{numero(fim[0])} {numero(fim[1])}")
        partes.append("Z")
    return "".join(partes)


def extrair(caminho_origem, lado=512):
    """logo.png -> (atributo d, lado da viewBox)."""
    figura = carregar_mascara(caminho_origem)
    fundo = ~figura

    rotulos_figura, quantas = rotular(figura)
    rotulos_fundo, quantos_fundo = rotular(fundo)

    # O fundo que encosta na borda e o de fora; qualquer outra regiao de
    # fundo e um buraco dentro da figura, e precisa virar subcaminho.
    externo = rotulos_fundo[0, 0]

    regioes = []
    for r in range(1, quantas + 1):
        pixels = np.argwhere(rotulos_figura == r)
        if len(pixels) >= AREA_MINIMA:
            regioes.append((rotulos_figura, r, len(pixels)))
    for r in range(1, quantos_fundo + 1):
        if r == externo:
            continue
        pixels = np.argwhere(rotulos_fundo == r)
        if len(pixels) >= AREA_MINIMA:
            regioes.append((rotulos_fundo, r, len(pixels)))

    contornos = []
    for matriz, rotulo, _ in regioes:
        mascara = matriz == rotulo
        primeiro = tuple(np.argwhere(mascara)[0])
        bruto = seguir_fronteira(mascara, primeiro)
        if len(bruto) < 8:
            continue
        contornos.append(douglas_peucker(bruto, TOLERANCIA))

    # Enquadra pelo que foi desenhado, com uma folga de 4% para o traco
    # nao encostar na borda da viewBox.
    todos = [p for c in contornos for p in c]
    ys = [p[0] for p in todos]
    xs = [p[1] for p in todos]
    largura, altura = max(xs) - min(xs), max(ys) - min(ys)
    maior = max(largura, altura)
    escala = (lado * 0.92) / maior
    folga_x = (lado - largura * escala) / 2 / escala
    folga_y = (lado - altura * escala) / 2 / escala

    return caminho_svg(contornos, escala,
                       (min(xs) - folga_x, min(ys) - folga_y)), lado


def main():
    origem = sys.argv[1] if len(sys.argv) > 1 else ORIGEM
    if not os.path.isfile(origem):
        raise SystemExit(f"não achei {origem}")

    print(f"lendo {os.path.relpath(origem, RAIZ)}…")
    d, lado = extrair(origem)
    print(f"  {d.count('M')} subcaminhos, {len(d)} caracteres")

    destino = os.path.join(RAIZ, "site", "lib", "marca.ts")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(f'''/**
 * A marca do DataForge, vetorizada de logo.png.
 *
 * Gerado por tools/vetorizar_logo.py — não edite à mão.
 *
 * É um caminho só, com fill-rule evenodd: os vãos (olho, boca, garras)
 * são subcaminhos no sentido inverso. Isso deixa a marca herdar a cor
 * de quem a usa — no cabeçalho, no favicon, no ícone do editor.
 */

export const VIEWBOX_MARCA = "0 0 {lado} {lado}";

export const CAMINHO_MARCA =
  "{d}";
''')
    print(f"  escrito: {os.path.relpath(destino, RAIZ)}")

    def svg_com(cor):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {lado} {lado}" fill="{cor}">'
                f'<path fill-rule="evenodd" d="{d}"/></svg>\n')

    # Duas variantes, porque 'currentColor' so resolve quando o SVG e
    # inline. Dentro de <img>, de um favicon ou do icone do editor, ele
    # vira preto — invisivel sobre fundo escuro.
    saidas = [
        (os.path.join(RAIZ, "site", "public", "marca.svg"), "currentColor"),
        (os.path.join(RAIZ, "site", "app", "icon.svg"), COR_MARCA),
        (os.path.join(RAIZ, "editor", "vscode", "marca.svg"), COR_MARCA),
    ]
    for saida, cor in saidas:
        os.makedirs(os.path.dirname(saida), exist_ok=True)
        with open(saida, "w", encoding="utf-8") as f:
            f.write(svg_com(cor))
        print(f"  escrito: {os.path.relpath(saida, RAIZ)}  ({cor})")

    # PNG para quem nao aceita SVG: apple-touch-icon e o icone da
    # extensao, que a loja do VS Code exige em bitmap.
    _gravar_pngs(d, lado)


def _gravar_pngs(d, lado):
    """Rasteriza a marca nos tamanhos que precisam ser bitmap."""
    from PIL import Image, ImageDraw

    # Reconstroi os poligonos a partir dos mesmos contornos, sem passar
    # por um renderizador de SVG (nao ha um aqui, e nao vale uma
    # dependencia so para isto).
    figura = carregar_mascara(ORIGEM)
    rotulos_figura, quantas = rotular(figura)
    rotulos_fundo, quantos_fundo = rotular(~figura)
    externo = rotulos_fundo[0, 0]

    partes = []
    for r in range(1, quantas + 1):
        if (rotulos_figura == r).sum() >= AREA_MINIMA:
            partes.append((rotulos_figura == r, True))
    for r in range(1, quantos_fundo + 1):
        if r != externo and (rotulos_fundo == r).sum() >= AREA_MINIMA:
            partes.append((rotulos_fundo == r, False))

    contornos = []
    for mascara, cheio in partes:
        bruto = seguir_fronteira(mascara, tuple(np.argwhere(mascara)[0]))
        contornos.append((douglas_peucker(bruto, TOLERANCIA), cheio))

    todos = [p for c, _ in contornos for p in c]
    ys = [p[0] for p in todos]
    xs = [p[1] for p in todos]

    def desenhar(tamanho, cor, fundo):
        largura, altura = max(xs) - min(xs), max(ys) - min(ys)
        escala = (tamanho * 0.86) / max(largura, altura)
        dx = min(xs) - (tamanho - largura * escala) / 2 / escala
        dy = min(ys) - (tamanho - altura * escala) / 2 / escala
        imagem = Image.new("RGBA", (tamanho * 4, tamanho * 4), fundo)
        pincel = ImageDraw.Draw(imagem)
        for pontos, cheio in contornos:
            pincel.polygon([(int((x - dx) * escala * 4),
                             int((y - dy) * escala * 4)) for y, x in pontos],
                           fill=cor if cheio else fundo)
        # Desenha 4x e reduz: e o antialiasing que o ImageDraw nao tem.
        return imagem.resize((tamanho, tamanho), Image.LANCZOS)

    rgb = tuple(int(COR_MARCA[i:i + 2], 16) for i in (1, 3, 5))

    saidas = [
        (os.path.join(RAIZ, "site", "app", "apple-icon.png"), 180,
         rgb + (255,), FUNDO_MARCA),
        (os.path.join(RAIZ, "editor", "vscode", "icone.png"), 256,
         rgb + (255,), FUNDO_MARCA),
        (os.path.join(RAIZ, "site", "public", "marca-256.png"), 256,
         rgb + (255,), (0, 0, 0, 0)),
    ]
    for caminho, tamanho, cor, fundo in saidas:
        desenhar(tamanho, cor, fundo).save(caminho)
        print(f"  escrito: {os.path.relpath(caminho, RAIZ)}  ({tamanho}px)")

    # O .ico ainda importa: o Next.js o declara ANTES do SVG, e navegador
    # que aceita os dois costuma usar o primeiro. Sem gerar este aqui, o
    # favicon fica sendo o do logo antigo para sempre.
    ico = os.path.join(RAIZ, "site", "app", "favicon.ico")
    tamanhos = [16, 32, 48, 64, 128, 256]
    imagens = [desenhar(t, rgb + (255,), FUNDO_MARCA) for t in tamanhos]
    imagens[-1].save(ico, format="ICO",
                     sizes=[(t, t) for t in tamanhos])
    print(f"  escrito: {os.path.relpath(ico, RAIZ)}  "
          f"({', '.join(str(t) for t in tamanhos)}px)")

    # E o ícone dos arquivos .df no editor, que o VS Code exige em PNG.
    tema = os.path.join(RAIZ, "editor", "vscode", "icone-arquivo.png")
    desenhar(128, rgb + (255,), (0, 0, 0, 0)).save(tema)
    print(f"  escrito: {os.path.relpath(tema, RAIZ)}  (128px)")


if __name__ == "__main__":
    main()
