"""Os desenhos dos gráficos que vieram com o painel profissional.

Tudo aqui é SVG escrito à mão, com as mesmas peças que `render.py` já
usava: a moldura, a escala redonda, a grade e o formatador de número.
Reaproveitá-las não é economia de linhas — é o que faz um eixo em reais
ser escrito do mesmo jeito num gráfico de barras e num de velas.

A regra de ouro ao acrescentar um desenho aqui: **o tipo tem de estar
em `graficos.TIPOS` e a função tem de entrar em `render._SVG`**. Faltar
de um lado é um gráfico que some calado — `_svg_linha` assume, e quem
pediu um funil vê uma linha. Há teste conferindo os dois lados.
"""

import math

from . import render as R

_e = R._e
_a = R._a
_L = R._L
_MARGEM = R._MARGEM
_moldura = R._moldura
_escala = R._escala
_grade = R._grade
_rotulos_x = R._rotulos_x
_y_de = R._y_de
_area_util = R._area_util
_fmt = R.formatar_valor
_curto = R._numero_curto
_encurtar = R._encurtar
_passo_bonito = R._passo_bonito


def _cores(props):
    return props.get("cores") or ["#FED403"]


def _vazio(altura, mensagem="sem dados para desenhar", props=None):
    return _moldura(altura, f'<text class="v-eixo" x="400" y="{altura / 2:.0f}" '
                            f'text-anchor="middle">{_e(mensagem)}</text>', props)


# ═══════════════════════════════════════════════════════════
#  Combinado — barra e linha, com duas escalas
# ═══════════════════════════════════════════════════════════

def svg_combo(props, series, categorias):
    altura = int(props.get("altura", 280))
    largura_util, _alt = _area_util(altura)
    cores = _cores(props)
    n = len(categorias)
    tipos = props.get("tipos_de_serie") or {}
    direita = set(props.get("direita") or [])

    esquerdas = [s for s in series if s["nome"] not in direita]
    direitas = [s for s in series if s["nome"] in direita]
    # Se a escala da esquerda só tem linha, ela não precisa do zero —
    # a mesma razão do gráfico de linha puro. Havendo barra, o zero
    # volta a ser obrigatório: ali o comprimento é o que significa.
    tem_barra = any(tipos.get(s["nome"], "barra") == "barra"
                    for s in (esquerdas or series))
    piso, topo, passo = _escala(esquerdas or series, props,
                                bool(props.get("empilhado")),
                                ancorar_no_zero=tem_barra)
    partes = [_grade(piso, topo, passo, altura, props.get("grade", True), props)]

    piso2 = topo2 = 0.0
    if direitas:
        piso2, topo2, passo2 = _escala(direitas, {}, ancorar_no_zero=False)
        partes.append(_eixo_direito(piso2, topo2, passo2, altura, props))
    partes.append(R.decoracoes(props, altura, piso, topo, categorias))

    barras = [s for s in series if tipos.get(s["nome"], "barra") == "barra"]
    linhas = [s for s in series if tipos.get(s["nome"], "barra") == "linha"]
    grupo = largura_util / max(1, n)
    base = _y_de(max(piso, 0), piso, topo, altura)
    empilhado = bool(props.get("empilhado"))

    for i in range(n):
        acumulado = 0.0
        for indice, serie in enumerate(barras):
            valor = serie["valores"][i] if i < len(serie["valores"]) else 0
            cor = cores[series.index(serie) % len(cores)]
            if empilhado:
                y0 = _y_de(acumulado, piso, topo, altura)
                y1 = _y_de(acumulado + valor, piso, topo, altura)
                x = _MARGEM["esq"] + grupo * i + grupo * 0.16
                larg = grupo * 0.68
                acumulado += valor
            else:
                larg = grupo * 0.68 / max(1, len(barras))
                x = _MARGEM["esq"] + grupo * i + grupo * 0.16 + larg * indice
                y0, y1 = base, _y_de(valor, piso, topo, altura)
            partes.append(
                f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{larg:.1f}" '
                f'height="{max(abs(y1 - y0), 0.5):.1f}" rx="2" '
                f'fill="{_a(cor)}"><title>{_e(categorias[i])} — '
                f'{_e(serie["nome"])}: {_e(_fmt(props, valor))}</title></rect>')

    for serie in linhas:
        cor = cores[series.index(serie) % len(cores)]
        usa_direita = serie["nome"] in direita
        p_, t_ = (piso2, topo2) if usa_direita else (piso, topo)
        pontos = []
        for i, valor in enumerate(serie["valores"][:n]):
            x = _MARGEM["esq"] + grupo * i + grupo / 2
            pontos.append((x, _y_de(valor, p_, t_, altura)))
        if not pontos:
            continue
        caminho = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                           for i, (x, y) in enumerate(pontos))
        risco = ' stroke-dasharray="7 5"' if serie["nome"] in (
            props.get("tracejadas") or []) else ""
        partes.append(f'<path d="{caminho}" fill="none" stroke="{_a(cor)}" '
                      f'stroke-width="2.6" stroke-linecap="round"{risco}/>')
        for i, (x, y) in enumerate(pontos):
            valor = serie["valores"][i]
            partes.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{_a(cor)}" '
                f'stroke="var(--v-superficie)" stroke-width="1.5">'
                f'<title>{_e(categorias[i])} — {_e(serie["nome"])}: '
                f'{_e(_fmt(props, valor))}</title></circle>')
    partes.append(_rotulos_x(categorias, altura, props))
    return _moldura(altura, "".join(partes), props)


def _eixo_direito(piso, topo, passo, altura, props):
    """A segunda escala, encostada na borda direita.

    Ela é desenhada com a mesma marcação da esquerda, e **sem grade**:
    duas grades sobrepostas produzem linhas que não pertencem a escala
    nenhuma, e quem lê acaba medindo a série errada pela linha errada.
    """
    _larg, altura_util = _area_util(altura)
    partes = []
    valor = piso
    while valor <= topo + passo / 2:
        y = _MARGEM["cima"] + altura_util * (1 - (valor - piso) / (topo - piso))
        partes.append(
            f'<text class="v-eixo v-eixo-dir" x="{_L - _MARGEM["dir"] + 4}" '
            f'y="{y + 4:.1f}">{_e(_curto(valor))}</text>')
        valor += passo
    return "".join(partes)


def svg_barras_100(props, series, categorias):
    return R._svg_barras({**props, "cem_por_cento": True, "empilhado": True},
                         series, categorias)


# ═══════════════════════════════════════════════════════════
#  Radar
# ═══════════════════════════════════════════════════════════

def svg_radar(props, series, categorias):
    altura = int(props.get("altura", 320))
    cores = _cores(props)
    n = len(categorias)
    if n < 3:
        return _vazio(altura, "o radar precisa de pelo menos três eixos")
    cx, cy = 400.0, altura / 2
    raio = min(altura / 2 - 34, 132)
    todos = [v for s in series for v in s["valores"] if R.presente(v)]
    maior = max(todos) if todos else 1.0
    if maior <= 0:
        maior = 1.0
    partes = []

    for anel in (0.25, 0.5, 0.75, 1.0):
        pontos = " ".join(
            f"{cx + math.cos(_ang(i, n)) * raio * anel:.1f},"
            f"{cy + math.sin(_ang(i, n)) * raio * anel:.1f}" for i in range(n))
        partes.append(f'<polygon points="{pontos}" fill="none" '
                      f'class="v-grade"/>')
    for i in range(n):
        x = cx + math.cos(_ang(i, n)) * raio
        y = cy + math.sin(_ang(i, n)) * raio
        partes.append(f'<line x1="{cx}" y1="{cy:.1f}" x2="{x:.1f}" '
                      f'y2="{y:.1f}" class="v-grade"/>')
        rx = cx + math.cos(_ang(i, n)) * (raio + 20)
        ry = cy + math.sin(_ang(i, n)) * (raio + 20)
        ancora = ("middle" if abs(rx - cx) < 8 else
                  ("start" if rx > cx else "end"))
        partes.append(
            f'<text class="v-eixo" x="{rx:.1f}" y="{ry + 4:.1f}" '
            f'text-anchor="{ancora}">{_e(_encurtar(categorias[i], 14))}</text>')

    for indice, serie in enumerate(series):
        cor = cores[indice % len(cores)]
        pontos = []
        for i in range(n):
            valor = serie["valores"][i] if i < len(serie["valores"]) else 0
            valor = valor if R.presente(valor) else 0.0
            distancia = raio * max(0.0, valor) / maior
            pontos.append((cx + math.cos(_ang(i, n)) * distancia,
                           cy + math.sin(_ang(i, n)) * distancia))
        traco = " ".join(f"{x:.1f},{y:.1f}" for x, y in pontos)
        partes.append(f'<polygon points="{traco}" fill="{_a(cor)}" '
                      f'fill-opacity="0.18" stroke="{_a(cor)}" '
                      f'stroke-width="2"/>')
        for i, (x, y) in enumerate(pontos):
            partes.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{_a(cor)}">'
                f'<title>{_e(categorias[i])} — {_e(serie["nome"])}: '
                f'{_e(_fmt(props, serie["valores"][i]))}</title></circle>')
    return _moldura(altura, "".join(partes), props)


def _ang(i, n):
    """O ângulo do eixo i. Começa no topo, e gira no sentido do relógio."""
    return -math.pi / 2 + 2 * math.pi * i / n


# ═══════════════════════════════════════════════════════════
#  Medidor e bala
# ═══════════════════════════════════════════════════════════

def svg_medidor(props, series, categorias):
    altura = int(props.get("altura", 280))
    valor = float(props.get("valor", 0))
    piso = float(props.get("minimo", 0))
    teto = float(props.get("maximo", 100))
    faixa = (teto - piso) or 1.0
    cx, cy = 400.0, altura * 0.78
    raio = min(altura * 0.62, 190)
    espessura = max(14.0, raio * 0.2)
    partes = [_arco(cx, cy, raio, espessura, 0.0, 1.0, "var(--v-borda)")]

    anterior = piso
    for f in (props.get("faixas") or []):
        ate = max(piso, min(teto, float(f.get("ate", teto))))
        partes.append(_arco(cx, cy, raio, espessura,
                            (anterior - piso) / faixa, (ate - piso) / faixa,
                            f.get("cor") or _cores(props)[0]))
        anterior = ate
    if not props.get("faixas"):
        partes.append(_arco(cx, cy, raio, espessura, 0.0,
                            (valor - piso) / faixa, _cores(props)[0]))

    fracao = max(0.0, min(1.0, (valor - piso) / faixa))
    angulo = math.pi * (1 + fracao)
    ponta_x = cx + math.cos(angulo) * (raio - espessura - 6)
    ponta_y = cy + math.sin(angulo) * (raio - espessura - 6)
    partes.append(
        f'<line x1="{cx}" y1="{cy:.1f}" x2="{ponta_x:.1f}" y2="{ponta_y:.1f}" '
        f'stroke="var(--v-texto)" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{cy:.1f}" r="6" fill="var(--v-texto)"/>')
    partes.append(
        f'<text class="v-centro-valor" x="{cx}" y="{cy - raio * 0.30:.1f}" '
        f'text-anchor="middle">{_e(_fmt(props, valor))}</text>')
    if props.get("rotulo"):
        partes.append(
            f'<text class="v-centro-rotulo" x="{cx}" y="{cy - raio * 0.30 + 20:.1f}" '
            f'text-anchor="middle">{_e(props["rotulo"])}</text>')
    partes.append(
        f'<text class="v-eixo" x="{cx - raio + espessura / 2:.1f}" '
        f'y="{cy + 18:.1f}" text-anchor="middle">{_e(_fmt(props, piso))}</text>'
        f'<text class="v-eixo" x="{cx + raio - espessura / 2:.1f}" '
        f'y="{cy + 18:.1f}" text-anchor="middle">{_e(_fmt(props, teto))}</text>')
    return _moldura(altura, "".join(partes), props)


def _arco(cx, cy, raio, espessura, de, ate, cor):
    """Um pedaço do semicírculo, de `de` a `ate` (de 0 a 1)."""
    de, ate = max(0.0, min(1.0, de)), max(0.0, min(1.0, ate))
    if ate <= de:
        return ""
    a1, a2 = math.pi * (1 + de), math.pi * (1 + ate)
    r2 = raio - espessura
    x1, y1 = cx + math.cos(a1) * raio, cy + math.sin(a1) * raio
    x2, y2 = cx + math.cos(a2) * raio, cy + math.sin(a2) * raio
    x3, y3 = cx + math.cos(a2) * r2, cy + math.sin(a2) * r2
    x4, y4 = cx + math.cos(a1) * r2, cy + math.sin(a1) * r2
    grande = 1 if (a2 - a1) > math.pi else 0
    return (f'<path d="M{x1:.1f},{y1:.1f} A{raio:.1f},{raio:.1f} 0 {grande} 1 '
            f'{x2:.1f},{y2:.1f} L{x3:.1f},{y3:.1f} A{r2:.1f},{r2:.1f} 0 '
            f'{grande} 0 {x4:.1f},{y4:.1f} Z" fill="{_a(cor)}"/>')


def svg_bala(props, series, categorias):
    altura = int(props.get("altura", 92))
    valor = float(props.get("valor", 0))
    alvo = float(props.get("alvo", 0))
    piso = float(props.get("minimo", 0))
    teto = float(props.get("maximo", 100)) or 1.0
    faixa = (teto - piso) or 1.0
    esq, dir_ = 12, 96
    largura = _L - esq - dir_
    meio = altura / 2
    espessura = min(30.0, altura * 0.42)
    partes = []

    anterior = piso
    faixas = props.get("faixas") or [{"ate": teto, "cor": "var(--v-borda)"}]
    for i, f in enumerate(faixas):
        ate = max(piso, min(teto, float(f.get("ate", teto))))
        x = esq + largura * (anterior - piso) / faixa
        larg = largura * (ate - anterior) / faixa
        cor = f.get("cor") or "var(--v-borda)"
        opacidade = 1.0 if f.get("cor") else 1.0
        partes.append(
            f'<rect x="{x:.1f}" y="{meio - espessura / 2:.1f}" '
            f'width="{max(0.0, larg):.1f}" height="{espessura:.1f}" '
            f'fill="{_a(cor)}" fill-opacity="{0.22 + i * 0.08:.2f}"/>')
        anterior = ate

    larg_valor = largura * max(0.0, (valor - piso)) / faixa
    partes.append(
        f'<rect x="{esq}" y="{meio - espessura / 5:.1f}" '
        f'width="{larg_valor:.1f}" height="{espessura * 0.4:.1f}" rx="2" '
        f'fill="{_a(_cores(props)[0])}"><title>{_e(props.get("rotulo", ""))}: '
        f'{_e(_fmt(props, valor))}</title></rect>')
    if alvo:
        x = esq + largura * (alvo - piso) / faixa
        partes.append(
            f'<line x1="{x:.1f}" y1="{meio - espessura / 2 - 3:.1f}" '
            f'x2="{x:.1f}" y2="{meio + espessura / 2 + 3:.1f}" '
            f'stroke="var(--v-texto)" stroke-width="3">'
            f'<title>meta: {_e(_fmt(props, alvo))}</title></line>')
    partes.append(
        f'<text class="v-eixo v-bala-num" x="{_L - 12}" y="{meio + 5:.1f}" '
        f'text-anchor="end">{_e(_fmt(props, valor))}</text>')
    if props.get("rotulo"):
        partes.append(f'<text class="v-eixo" x="{esq}" y="14">'
                      f'{_e(props["rotulo"])}</text>')
    return _moldura(altura, "".join(partes), props)


# ═══════════════════════════════════════════════════════════
#  Funil, treemap, cascata, pareto
# ═══════════════════════════════════════════════════════════

def svg_funil(props, series, categorias):
    etapas = props.get("etapas") or []
    if not etapas:
        return _vazio(int(props.get("altura", 280)))
    altura = max(int(props.get("altura", 280)), 52 * len(etapas) + 24)
    cores = _cores(props)
    topo_valor = max((e["valor"] for e in etapas), default=1) or 1
    cx = 300.0
    largura_max = 440.0
    passo = (altura - 20) / len(etapas)
    partes = []

    for i, etapa in enumerate(etapas):
        seguinte = etapas[i + 1]["valor"] if i + 1 < len(etapas) else etapa["valor"]
        w1 = largura_max * etapa["valor"] / topo_valor
        w2 = largura_max * seguinte / topo_valor
        y1 = 10 + passo * i
        y2 = y1 + passo * 0.82
        cor = cores[i % len(cores)]
        partes.append(
            f'<path d="M{cx - w1 / 2:.1f},{y1:.1f} L{cx + w1 / 2:.1f},{y1:.1f} '
            f'L{cx + w2 / 2:.1f},{y2:.1f} L{cx - w2 / 2:.1f},{y2:.1f} Z" '
            f'fill="{_a(cor)}" fill-opacity="0.88">'
            f'<title>{_e(etapa["rotulo"])}: {_e(_fmt(props, etapa["valor"]))}'
            f"</title></path>")
        partes.append(
            f'<text class="v-fatia" x="{cx:.1f}" y="{y1 + passo * 0.5:.1f}" '
            f'text-anchor="middle">{_e(_fmt(props, etapa["valor"]))}</text>')
        partes.append(
            f'<text class="v-eixo" x="{cx + largura_max / 2 + 18:.1f}" '
            f'y="{y1 + passo * 0.38:.1f}">{_e(_encurtar(etapa["rotulo"], 20))}'
            f"</text>")
        conversao = (f'{etapa["da_anterior"]:.1f}% da etapa anterior' if i
                     else "topo do funil")
        partes.append(
            f'<text class="v-eixo v-funil-sub" x="{cx + largura_max / 2 + 18:.1f}" '
            f'y="{y1 + passo * 0.62:.1f}">{_e(conversao)}</text>')
    return _moldura(altura, "".join(partes), props)


def svg_treemap(props, series, categorias):
    itens = props.get("itens") or []
    altura = int(props.get("altura", 280))
    if not itens:
        return _vazio(altura)
    cores = _cores(props)
    total = sum(i["valor"] for i in itens) or 1.0
    partes = []
    caixas = _fatiar(itens, 0.0, 0.0, float(_L), float(altura), total)
    for i, (item, x, y, w, h) in enumerate(caixas):
        cor = cores[i % len(cores)]
        partes.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(0.0, w - 2):.1f}" '
            f'height="{max(0.0, h - 2):.1f}" rx="3" fill="{_a(cor)}" '
            f'fill-opacity="0.9"><title>{_e(item["rotulo"])}: '
            f'{_e(_fmt(props, item["valor"]))} · '
            f'{item["valor"] / total * 100:.1f}%</title></rect>')
        if w > 62 and h > 30:
            partes.append(
                f'<text class="v-fatia" x="{x + 8:.1f}" y="{y + 20:.1f}">'
                f'{_e(_encurtar(item["rotulo"], int(w / 8)))}</text>')
        if w > 62 and h > 48:
            partes.append(
                f'<text class="v-fatia v-tm-num" x="{x + 8:.1f}" '
                f'y="{y + 38:.1f}">{_e(_fmt(props, item["valor"]))}</text>')
    return _moldura(altura, "".join(partes), props)


def _fatiar(itens, x, y, largura, altura, total):
    """Corte alternado: a faixa vai no lado mais curto da área que sobra.

    Não é o *squarify* clássico, que otimiza a proporção de cada
    retângulo. É determinístico, cabe em vinte linhas, e dá retângulos
    razoáveis — o algoritmo completo renderia forma melhor e uma página
    a mais de código que ninguém releria.
    """
    if not itens or largura <= 0 or altura <= 0:
        return []
    if len(itens) == 1:
        return [(itens[0], x, y, largura, altura)]
    metade, acumulado = 0, 0.0
    alvo = total / 2
    for i, item in enumerate(itens):
        acumulado += item["valor"]
        metade = i + 1
        if acumulado >= alvo:
            break
    primeira, segunda = itens[:metade], itens[metade:]
    if not segunda:
        primeira, segunda = itens[:1], itens[1:]
        acumulado = primeira[0]["valor"]
    resto = total - acumulado
    if largura >= altura:
        corte = largura * acumulado / total
        return (_fatiar(primeira, x, y, corte, altura, acumulado)
                + _fatiar(segunda, x + corte, y, largura - corte, altura, resto))
    corte = altura * acumulado / total
    return (_fatiar(primeira, x, y, largura, corte, acumulado)
            + _fatiar(segunda, x, y + corte, largura, altura - corte, resto))


def svg_cascata(props, series, categorias):
    passos = props.get("passos") or []
    altura = int(props.get("altura", 280))
    if not passos:
        return _vazio(altura)
    largura_util, _alt = _area_util(altura)
    valores = [p["de"] for p in passos] + [p["ate"] for p in passos] + [0.0]
    piso, topo, passo_grade = _escala(
        [{"nome": "", "valores": valores}], props)
    partes = [_grade(piso, topo, passo_grade, altura,
                     props.get("grade", True), props)]
    cores = _cores(props)
    sobe = props.get("cor_sobe") or "#24A148"
    desce = props.get("cor_desce") or "#FA4D56"
    n = len(passos)
    grupo = largura_util / max(1, n)
    anterior_x = anterior_y = None

    for i, p in enumerate(passos):
        y1 = _y_de(p["de"], piso, topo, altura)
        y2 = _y_de(p["ate"], piso, topo, altura)
        x = _MARGEM["esq"] + grupo * i + grupo * 0.2
        larg = grupo * 0.6
        cor = {"sobe": sobe, "desce": desce}.get(p["tipo"], cores[0])
        partes.append(
            f'<rect x="{x:.1f}" y="{min(y1, y2):.1f}" width="{larg:.1f}" '
            f'height="{max(abs(y2 - y1), 1.5):.1f}" rx="2" fill="{_a(cor)}">'
            f'<title>{_e(p["rotulo"])}: {_e(_fmt(props, p["valor"]))}</title>'
            f"</rect>")
        partes.append(
            f'<text class="v-eixo" x="{x + larg / 2:.1f}" '
            f'y="{min(y1, y2) - 5:.1f}" text-anchor="middle">'
            f'{_e(_fmt(props, p["valor"]))}</text>')
        if anterior_x is not None:
            partes.append(
                f'<line x1="{anterior_x:.1f}" y1="{anterior_y:.1f}" '
                f'x2="{x:.1f}" y2="{anterior_y:.1f}" class="v-grade" '
                f'stroke-dasharray="3 3"/>')
        anterior_x, anterior_y = x + larg, y2
    partes.append(_rotulos_x([p["rotulo"] for p in passos], altura, props))
    return _moldura(altura, "".join(partes), props)


def svg_pareto(props, series, categorias):
    altura = int(props.get("altura", 280))
    acumulado = props.get("acumulado") or []
    base = R._svg_barras({**props, "legenda": False}, series, categorias)
    if not acumulado:
        return base
    largura_util, _alt = _area_util(altura)
    n = len(categorias)
    grupo = largura_util / max(1, n)
    pontos = []
    for i, pct in enumerate(acumulado):
        x = _MARGEM["esq"] + grupo * i + grupo / 2
        pontos.append((x, _y_de(pct, 0, 100, altura)))
    caminho = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                       for i, (x, y) in enumerate(pontos))
    corte = float(props.get("corte", 80))
    y_corte = _y_de(corte, 0, 100, altura)
    extra = [
        f'<line x1="{_MARGEM["esq"]}" y1="{y_corte:.1f}" '
        f'x2="{_L - _MARGEM["dir"]}" y2="{y_corte:.1f}" stroke="#FA4D56" '
        f'stroke-width="1.2" stroke-dasharray="6 4"/>',
        f'<text class="v-eixo" x="{_L - _MARGEM["dir"] - 4}" '
        f'y="{y_corte - 5:.1f}" text-anchor="end" fill="#FA4D56">'
        f'{corte:.0f}%</text>',
        f'<path d="{caminho}" fill="none" stroke="var(--v-texto)" '
        f'stroke-width="2"/>',
    ]
    for i, (x, y) in enumerate(pontos):
        extra.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" '
                     f'fill="var(--v-texto)"><title>acumulado: '
                     f'{acumulado[i]:.1f}%</title></circle>')
    # O SVG já está fechado: a curva entra antes do `</svg>`, que é o
    # único ponto em que ela fica por cima das barras.
    return base.replace("</svg>", "".join(extra) + "</svg>")


# ═══════════════════════════════════════════════════════════
#  Matrizes de cor
# ═══════════════════════════════════════════════════════════

def svg_mapa_de_calor(props, series, categorias):
    matriz = props.get("matriz") or []
    colunas = props.get("colunas_x") or []
    linhas = props.get("linhas_y") or []
    if not matriz or not colunas:
        return _vazio(int(props.get("altura", 280)))
    celula = max(16.0, min(42.0, (_L - 150.0) / max(1, len(colunas))))
    altura = int(max(props.get("altura", 280) or 0,
                     celula * len(linhas) + 58))
    esq = 118.0
    partes = []
    menor = float(props.get("minimo", 0))
    maior = float(props.get("maximo", 1))
    escala = props.get("escala") or []

    for li, linha in enumerate(linhas):
        y = 14 + celula * li
        partes.append(
            f'<text class="v-eixo" x="{esq - 8}" y="{y + celula / 2 + 4:.1f}" '
            f'text-anchor="end">{_e(_encurtar(linha, 16))}</text>')
        for ci, coluna in enumerate(colunas):
            valor = matriz[li][ci] if ci < len(matriz[li]) else None
            x = esq + celula * ci
            if valor is None:
                partes.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{celula - 2:.1f}" '
                    f'height="{celula - 2:.1f}" rx="2" fill="var(--v-fundo-alt)"/>')
                continue
            intensidade = ((valor - menor) / (maior - menor)
                           if maior > menor else 1.0)
            partes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{celula - 2:.1f}" '
                f'height="{celula - 2:.1f}" rx="2" '
                f'fill="{_a(_tom(intensidade, escala, _cores(props)[0]))}">'
                f'<title>{_e(linha)} × {_e(coluna)}: '
                f'{_e(_fmt(props, valor))}</title></rect>')
    salto = max(1, math.ceil(len(colunas) / 16))
    for ci, coluna in enumerate(colunas):
        if ci % salto and ci != len(colunas) - 1:
            continue
        partes.append(
            f'<text class="v-eixo" x="{esq + celula * ci + celula / 2:.1f}" '
            f'y="{14 + celula * len(linhas) + 16:.1f}" text-anchor="middle">'
            f"{_e(_encurtar(coluna, 8))}</text>")
    partes.append(_regua_de_cor(menor, maior, escala, _cores(props)[0],
                                altura, props))
    return _moldura(altura, "".join(partes), props)


def _tom(intensidade, escala, cor_base):
    """A cor de uma célula: a mesma matiz, do apagado ao cheio.

    Uma escala sequencial de **uma** matiz é lida como ordem; uma de
    arco-íris é lida como categoria, e quem olha vê fronteiras onde o
    dado é contínuo.
    """
    intensidade = max(0.0, min(1.0, intensidade))
    if escala:
        posicao = min(len(escala) - 1, int(intensidade * len(escala)))
        return escala[posicao]
    return (f'color-mix(in srgb, {cor_base} {8 + intensidade * 88:.0f}%, '
            f'var(--v-fundo-alt))')


def _regua_de_cor(menor, maior, escala, cor, altura, props):
    partes = [f'<text class="v-eixo" x="{_L - 210}" y="{altura - 8}">'
              f'{_e(_fmt(props, menor))}</text>']
    for i in range(10):
        partes.append(
            f'<rect x="{_L - 168 + i * 14}" y="{altura - 20}" width="14" '
            f'height="10" fill="{_a(_tom(i / 9, escala, cor))}"/>')
    partes.append(f'<text class="v-eixo" x="{_L - 22}" y="{altura - 8}">'
                  f'{_e(_fmt(props, maior))}</text>')
    return "".join(partes)


def svg_calendario(props, series, categorias):
    dias = props.get("dias") or {}
    altura = int(props.get("altura", 190))
    if not dias:
        return _vazio(altura, "sem dias para desenhar")
    ano = int(props.get("ano") or 0)
    menor = float(props.get("minimo", 0))
    maior = float(props.get("maximo", 1))
    escala = props.get("escala") or []
    cor = _cores(props)[0]
    lado, folga = 12.0, 2.0
    esq, topo = 42.0, 26.0
    partes = []

    primeiro = _dia_da_semana(ano, 1, 1)
    for nome, indice in (("seg", 1), ("qua", 3), ("sex", 5)):
        partes.append(
            f'<text class="v-eixo" x="{esq - 6}" '
            f'y="{topo + indice * (lado + folga) + 9:.1f}" text-anchor="end">'
            f"{nome}</text>")

    dia_do_ano = 0
    meses_vistos = {}
    for mes in range(1, 13):
        for dia in range(1, _dias_do_mes(ano, mes) + 1):
            semana = (dia_do_ano + primeiro) // 7
            linha = (dia_do_ano + primeiro) % 7
            chave = f"{ano:04d}-{mes:02d}-{dia:02d}"
            valor = dias.get(chave)
            x = esq + semana * (lado + folga)
            y = topo + linha * (lado + folga)
            if mes not in meses_vistos:
                meses_vistos[mes] = x
            if valor is None:
                preenchimento = "var(--v-fundo-alt)"
                dica = f"{chave}: sem registro"
            else:
                intensidade = ((valor - menor) / (maior - menor)
                               if maior > menor else 1.0)
                preenchimento = _tom(intensidade, escala, cor)
                dica = f"{chave}: {_fmt(props, valor)}"
            partes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{lado}" height="{lado}" '
                f'rx="2" fill="{_a(preenchimento)}"><title>{_e(dica)}</title>'
                f"</rect>")
            dia_do_ano += 1
    nomes = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set",
             "out", "nov", "dez")
    for mes, x in meses_vistos.items():
        partes.append(f'<text class="v-eixo" x="{x:.1f}" y="18">'
                      f"{nomes[mes - 1]}</text>")
    return _moldura(altura, "".join(partes), props)


def _dias_do_mes(ano, mes):
    if mes == 2:
        bissexto = ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)
        return 29 if bissexto else 28
    return 30 if mes in (4, 6, 9, 11) else 31


def _dia_da_semana(ano, mes, dia):
    """Segunda é 0. Fórmula de Zeller, para não importar `datetime`.

    Não é economia de import: `datetime` levantaria num ano fora da
    faixa que ele aceita, e um calendário que dispara por causa de um
    ano estranho no dado é pior que um calendário torto.
    """
    if mes < 3:
        mes += 12
        ano -= 1
    k, j = ano % 100, ano // 100
    h = (dia + (13 * (mes + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
    return (h + 5) % 7


# ═══════════════════════════════════════════════════════════
#  Distribuição e relação
# ═══════════════════════════════════════════════════════════

def svg_caixa(props, series, categorias):
    resumos = props.get("resumos") or []
    altura = int(props.get("altura", 280))
    if not resumos:
        return _vazio(altura)
    largura_util, _alt = _area_util(altura)
    todos = [v for r in resumos
             for v in (r["minimo"], r["maximo"], *r["fora"])]
    piso, topo, passo = _escala(
        [{"nome": "", "valores": todos}],
        {**props, "min_y": props.get("min_y"), "max_y": props.get("max_y")})
    partes = [_grade(piso, topo, passo, altura, props.get("grade", True), props)]
    cores = _cores(props)
    n = len(resumos)
    grupo = largura_util / max(1, n)

    for i, r in enumerate(resumos):
        cor = cores[i % len(cores)]
        cx = _MARGEM["esq"] + grupo * i + grupo / 2
        larg = min(56.0, grupo * 0.46)
        y_q1 = _y_de(r["q1"], piso, topo, altura)
        y_q3 = _y_de(r["q3"], piso, topo, altura)
        y_med = _y_de(r["mediana"], piso, topo, altura)
        y_min = _y_de(r["minimo"], piso, topo, altura)
        y_max = _y_de(r["maximo"], piso, topo, altura)
        partes.append(
            f'<line x1="{cx:.1f}" y1="{y_max:.1f}" x2="{cx:.1f}" '
            f'y2="{y_min:.1f}" stroke="{_a(cor)}" stroke-width="1.4"/>'
            f'<line x1="{cx - larg / 3:.1f}" y1="{y_max:.1f}" '
            f'x2="{cx + larg / 3:.1f}" y2="{y_max:.1f}" stroke="{_a(cor)}" '
            f'stroke-width="1.4"/>'
            f'<line x1="{cx - larg / 3:.1f}" y1="{y_min:.1f}" '
            f'x2="{cx + larg / 3:.1f}" y2="{y_min:.1f}" stroke="{_a(cor)}" '
            f'stroke-width="1.4"/>')
        partes.append(
            f'<rect x="{cx - larg / 2:.1f}" y="{min(y_q1, y_q3):.1f}" '
            f'width="{larg:.1f}" height="{max(abs(y_q1 - y_q3), 1.5):.1f}" '
            f'rx="2" fill="{_a(cor)}" fill-opacity="0.32" stroke="{_a(cor)}">'
            f'<title>{_e(r["nome"])} — mediana {_e(_fmt(props, r["mediana"]))}, '
            f'q1 {_e(_fmt(props, r["q1"]))}, q3 {_e(_fmt(props, r["q3"]))}, '
            f'n={r["n"]}</title></rect>')
        partes.append(
            f'<line x1="{cx - larg / 2:.1f}" y1="{y_med:.1f}" '
            f'x2="{cx + larg / 2:.1f}" y2="{y_med:.1f}" stroke="{_a(cor)}" '
            f'stroke-width="2.6"/>')
        for fora in r["fora"]:
            partes.append(
                f'<circle cx="{cx:.1f}" cy="{_y_de(fora, piso, topo, altura):.1f}" '
                f'r="2.6" fill="none" stroke="{_a(cor)}" stroke-width="1.2">'
                f'<title>fora da curva: {_e(_fmt(props, fora))}</title></circle>')
    partes.append(_rotulos_x([r["nome"] for r in resumos], altura, props))
    return _moldura(altura, "".join(partes), props)


def svg_bolhas(props, series, categorias):
    pontos = props.get("pontos") or []
    altura = int(props.get("altura", 280))
    if not pontos:
        return _vazio(altura)
    cores = _cores(props)
    partes, piso_x, faixa_x, piso_y, topo_y, passo_y = _plano_xy(props, pontos,
                                                                 altura)
    maior_tamanho = max((p["tamanho"] for p in pontos), default=1.0) or 1.0
    largura_util, _alt = _area_util(altura)
    for i, p in enumerate(pontos):
        x = _MARGEM["esq"] + largura_util * (p["x"] - piso_x) / faixa_x
        y = _y_de(p["y"], piso_y, topo_y, altura)
        # A ÁREA é proporcional ao valor: o raio sai da raiz. Usar o
        # raio direto quadruplicaria a mancha de um valor dobrado.
        raio = 4 + 22 * math.sqrt(max(0.0, p["tamanho"]) / maior_tamanho)
        partes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{raio:.1f}" '
            f'fill="{_a(cores[i % len(cores)])}" fill-opacity="0.55" '
            f'stroke="{_a(cores[i % len(cores)])}"><title>{_e(p["rotulo"])} — '
            f'{_e(props.get("rotulo_x", "x"))}: {_e(_fmt(props, p["x"]))}, '
            f'{_e(props.get("rotulo_y", "y"))}: {_e(_fmt(props, p["y"]))}'
            f"</title></circle>")
    return _moldura(altura, "".join(partes), props)


def svg_dispersao_xy(props, series, categorias):
    pontos = props.get("pontos") or []
    altura = int(props.get("altura", 280))
    if not pontos:
        return _vazio(altura)
    cor = _cores(props)[0]
    partes, piso_x, faixa_x, piso_y, topo_y, passo_y = _plano_xy(props, pontos,
                                                                 altura)
    largura_util, _alt = _area_util(altura)
    for p in pontos:
        x = _MARGEM["esq"] + largura_util * (p["x"] - piso_x) / faixa_x
        y = _y_de(p["y"], piso_y, topo_y, altura)
        partes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{_a(cor)}" '
            f'fill-opacity="0.7"><title>{_e(props.get("rotulo_x", "x"))}: '
            f'{_e(_fmt(props, p["x"]))} · {_e(props.get("rotulo_y", "y"))}: '
            f'{_e(_fmt(props, p["y"]))}</title></circle>')
    reta = props.get("tendencia")
    if reta:
        x1 = piso_x
        x2 = piso_x + faixa_x
        px1 = _MARGEM["esq"]
        px2 = _MARGEM["esq"] + largura_util
        py1 = _y_de(reta["a"] * x1 + reta["b"], piso_y, topo_y, altura)
        py2 = _y_de(reta["a"] * x2 + reta["b"], piso_y, topo_y, altura)
        partes.append(
            f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" '
            f'y2="{py2:.1f}" stroke="var(--v-texto)" stroke-width="1.6" '
            f'stroke-dasharray="7 4"/>'
            f'<text class="v-eixo" x="{px2 - 4:.1f}" y="{_MARGEM["cima"] + 12}" '
            f'text-anchor="end">r² = {reta["r2"]:.3f}</text>')
    return _moldura(altura, "".join(partes), props)


def _plano_xy(props, pontos, altura):
    """Grade com os dois eixos numéricos, e os limites que ela usou."""
    xs = [p["x"] for p in pontos]
    ys = [p["y"] for p in pontos]
    piso_y, topo_y, passo_y = _escala([{"nome": "", "valores": ys}], props)
    menor_x, maior_x = min(xs), max(xs)
    if maior_x == menor_x:
        maior_x = menor_x + 1
    folga = (maior_x - menor_x) * 0.05
    piso_x, faixa_x = menor_x - folga, (maior_x - menor_x) + folga * 2
    partes = [_grade(piso_y, topo_y, passo_y, altura,
                     props.get("grade", True), props)]
    largura_util, _alt = _area_util(altura)
    for i in range(6):
        valor = piso_x + faixa_x * i / 5
        x = _MARGEM["esq"] + largura_util * i / 5
        partes.append(
            f'<text class="v-eixo" x="{x:.1f}" y="{altura - 12}" '
            f'text-anchor="middle">{_e(_curto(valor))}</text>')
    return partes, piso_x, faixa_x, piso_y, topo_y, passo_y


# ═══════════════════════════════════════════════════════════
#  Financeiro
# ═══════════════════════════════════════════════════════════

def svg_velas(props, series, categorias):
    velas = props.get("velas") or []
    altura = int(props.get("altura", 280))
    if not velas:
        return _vazio(altura)
    largura_util, _alt = _area_util(altura)
    valores = [v for vela in velas for v in (vela["maxima"], vela["minima"])]
    piso, topo, passo = _escala([{"nome": "", "valores": valores}], props)
    partes = [_grade(piso, topo, passo, altura, props.get("grade", True), props)]
    sobe = props.get("cor_sobe") or "#24A148"
    desce = props.get("cor_desce") or "#FA4D56"
    n = len(velas)
    grupo = largura_util / max(1, n)
    corpo = max(2.0, min(14.0, grupo * 0.58))

    for i, vela in enumerate(velas):
        cx = _MARGEM["esq"] + grupo * i + grupo / 2
        cor = sobe if vela["subiu"] else desce
        y_alto = _y_de(vela["maxima"], piso, topo, altura)
        y_baixo = _y_de(vela["minima"], piso, topo, altura)
        y_ab = _y_de(vela["abertura"], piso, topo, altura)
        y_fe = _y_de(vela["fechamento"], piso, topo, altura)
        partes.append(
            f'<line x1="{cx:.1f}" y1="{y_alto:.1f}" x2="{cx:.1f}" '
            f'y2="{y_baixo:.1f}" stroke="{_a(cor)}" stroke-width="1.2"/>'
            f'<rect x="{cx - corpo / 2:.1f}" y="{min(y_ab, y_fe):.1f}" '
            f'width="{corpo:.1f}" height="{max(abs(y_fe - y_ab), 1.5):.1f}" '
            f'fill="{_a(cor)}" rx="1"><title>{_e(vela["rotulo"])} — '
            f'abertura {_e(_fmt(props, vela["abertura"]))}, '
            f'máxima {_e(_fmt(props, vela["maxima"]))}, '
            f'mínima {_e(_fmt(props, vela["minima"]))}, '
            f'fechamento {_e(_fmt(props, vela["fechamento"]))}</title></rect>')
    partes.append(_rotulos_x([v["rotulo"] for v in velas], altura, props))
    return _moldura(altura, "".join(partes), props)


# ═══════════════════════════════════════════════════════════
#  Fluxo, cronograma, lugar, rede
# ═══════════════════════════════════════════════════════════

def svg_sankey(props, series, categorias):
    ligacoes = props.get("ligacoes") or []
    camadas = props.get("camadas") or {}
    altura = int(props.get("altura", 340))
    if not ligacoes:
        return _vazio(altura)
    cores = _cores(props)
    por_camada = {}
    for no, camada in camadas.items():
        por_camada.setdefault(camada, []).append(no)
    total_camadas = max(por_camada) + 1
    larg_no = 16.0
    vao = (_L - 60.0 - larg_no) / max(1, total_camadas - 1) if total_camadas > 1 \
        else 0.0

    fluxo = {}
    for l in ligacoes:
        fluxo[l["de"]] = fluxo.get(l["de"], 0.0) + l["valor"]
        fluxo[l["para"]] = max(fluxo.get(l["para"], 0.0), 0.0) + 0.0
    entrada = {}
    for l in ligacoes:
        entrada[l["para"]] = entrada.get(l["para"], 0.0) + l["valor"]
    tamanho = {no: max(fluxo.get(no, 0.0), entrada.get(no, 0.0))
               for no in camadas}

    posicoes, partes = {}, []
    for camada, nos in sorted(por_camada.items()):
        total = sum(tamanho[n] for n in nos) or 1.0
        disponivel = altura - 44 - 8 * (len(nos) - 1)
        y = 24.0
        for i, no in enumerate(nos):
            h = max(6.0, disponivel * tamanho[no] / total)
            x = 30.0 + vao * camada
            posicoes[no] = {"x": x, "y": y, "h": h, "usado_saida": 0.0,
                            "usado_entrada": 0.0}
            cor = cores[(hash(no) % len(cores))]
            partes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{larg_no}" '
                f'height="{h:.1f}" rx="2" fill="{_a(cor)}">'
                f'<title>{_e(no)}: {_e(_fmt(props, tamanho[no]))}</title></rect>')
            ancora = "start" if camada < total_camadas - 1 else "end"
            tx = x + larg_no + 6 if ancora == "start" else x - 6
            partes.append(
                f'<text class="v-eixo" x="{tx:.1f}" y="{y + h / 2 + 4:.1f}" '
                f'text-anchor="{ancora}">{_e(_encurtar(no, 18))}</text>')
            y += h + 8

    for l in ligacoes:
        origem, destino = posicoes[l["de"]], posicoes[l["para"]]
        total_saida = sum(x["valor"] for x in ligacoes if x["de"] == l["de"]) or 1.0
        total_entrada = entrada.get(l["para"], 1.0) or 1.0
        h1 = origem["h"] * l["valor"] / total_saida
        h2 = destino["h"] * l["valor"] / total_entrada
        y1 = origem["y"] + origem["usado_saida"]
        y2 = destino["y"] + destino["usado_entrada"]
        origem["usado_saida"] += h1
        destino["usado_entrada"] += h2
        x1 = origem["x"] + larg_no
        x2 = destino["x"]
        meio = (x1 + x2) / 2
        cor = cores[(hash(l["de"]) % len(cores))]
        partes.append(
            f'<path d="M{x1:.1f},{y1:.1f} C{meio:.1f},{y1:.1f} {meio:.1f},'
            f'{y2:.1f} {x2:.1f},{y2:.1f} L{x2:.1f},{y2 + h2:.1f} '
            f'C{meio:.1f},{y2 + h2:.1f} {meio:.1f},{y1 + h1:.1f} '
            f'{x1:.1f},{y1 + h1:.1f} Z" fill="{_a(cor)}" fill-opacity="0.3">'
            f'<title>{_e(l["de"])} → {_e(l["para"])}: '
            f'{_e(_fmt(props, l["valor"]))}</title></path>')
    return _moldura(altura, "".join(partes), props)


def svg_gantt(props, series, categorias):
    tarefas = props.get("tarefas") or []
    altura = int(props.get("altura", 280))
    if not tarefas:
        return _vazio(altura, "sem tarefas com início e fim")
    inicio = min(_dia_juliano(t["inicio"]) for t in tarefas)
    fim = max(_dia_juliano(t["fim"]) for t in tarefas)
    faixa = max(1, fim - inicio)
    esq = R._largura_do_rotulo([t["tarefa"] for t in tarefas],
                              R.escala_do_texto(props))
    largura = _L - esq - 24
    passo = (altura - 44) / max(1, len(tarefas))
    cores = _cores(props)
    grupos = []
    partes = []

    for i in range(5):
        x = esq + largura * i / 4
        partes.append(
            f'<line class="v-grade" x1="{x:.1f}" y1="18" x2="{x:.1f}" '
            f'y2="{altura - 22}"/>'
            f'<text class="v-eixo" x="{x:.1f}" y="{altura - 6}" '
            f'text-anchor="middle">'
            f'{_e(_data_juliana(inicio + faixa * i // 4))}</text>')

    for i, t in enumerate(tarefas):
        if t["grupo"] and t["grupo"] not in grupos:
            grupos.append(t["grupo"])
        cor = cores[(grupos.index(t["grupo"]) if t["grupo"] in grupos else i)
                    % len(cores)]
        a = _dia_juliano(t["inicio"])
        b = _dia_juliano(t["fim"])
        x = esq + largura * (a - inicio) / faixa
        larg = max(3.0, largura * max(1, b - a) / faixa)
        y = 20 + passo * i + passo * 0.18
        alt = max(8.0, passo * 0.56)
        partes.append(
            f'<text class="v-eixo" x="{esq - 8}" y="{y + alt / 2 + 4:.1f}" '
            f'text-anchor="end">{_e(_encurtar(t["tarefa"], 24))}</text>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{larg:.1f}" '
            f'height="{alt:.1f}" rx="3" fill="{_a(cor)}" fill-opacity="0.35"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" '
            f'width="{larg * t["progresso"] / 100:.1f}" height="{alt:.1f}" '
            f'rx="3" fill="{_a(cor)}"><title>{_e(t["tarefa"])}: '
            f'{_e(t["inicio"])} → {_e(t["fim"])} · '
            f'{t["progresso"]:.0f}%</title></rect>')
    return _moldura(altura, "".join(partes), props)


def _dia_juliano(iso):
    """`2026-09-20` vira um número de dias. Sem `datetime`, e sem fuso.

    O fuso é o ponto: um cronograma é feito de datas, não de instantes,
    e converter para instante faria uma tarefa mudar de dia conforme o
    servidor.
    """
    try:
        ano, mes, dia = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    except (ValueError, IndexError):
        return 0
    a = (14 - mes) // 12
    y = ano + 4800 - a
    m = mes + 12 * a - 3
    return (dia + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400
            - 32045)


def _data_juliana(numero):
    """O caminho de volta — para escrever a marca do eixo."""
    a = numero + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    dia = e - (153 * m + 2) // 5 + 1
    mes = m + 3 - 12 * (m // 10)
    ano = 100 * b + d - 4800 + m // 10
    return f"{dia:02d}/{mes:02d}"


def svg_mapa(props, series, categorias):
    pontos = props.get("pontos") or []
    altura = int(props.get("altura", 340))
    if not pontos:
        return _vazio(altura, "sem pontos para situar")
    partes = []
    esq, dir_, topo, baixo = 24.0, 24.0, 16.0, 26.0
    largura = _L - esq - dir_
    util = altura - topo - baixo

    for i in range(7):
        x = esq + largura * i / 6
        partes.append(f'<line class="v-grade" x1="{x:.1f}" y1="{topo}" '
                      f'x2="{x:.1f}" y2="{topo + util:.1f}"/>')
        partes.append(
            f'<text class="v-eixo" x="{x:.1f}" y="{altura - 8}" '
            f'text-anchor="middle">{-180 + 60 * i}°</text>')
    for i in range(5):
        y = topo + util * i / 4
        partes.append(f'<line class="v-grade" x1="{esq}" y1="{y:.1f}" '
                      f'x2="{esq + largura:.1f}" y2="{y:.1f}"/>')
        partes.append(f'<text class="v-eixo" x="{esq - 4}" y="{y + 4:.1f}" '
                      f'text-anchor="end">{90 - 45 * i}°</text>')

    maior = max((abs(p["valor"]) for p in pontos), default=0.0)
    cor = _cores(props)[0]
    for p in pontos:
        x = esq + largura * (p["lon"] + 180) / 360
        y = topo + util * (90 - p["lat"]) / 180
        raio = 4.0 + (10.0 * math.sqrt(abs(p["valor"]) / maior) if maior else 0.0)
        partes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{raio:.1f}" '
            f'fill="{_a(cor)}" fill-opacity="0.6" stroke="{_a(cor)}">'
            f'<title>{_e(p["rotulo"])} ({p["lat"]:.3f}, {p["lon"]:.3f})'
            f'{": " + _fmt(props, p["valor"]) if p["valor"] else ""}</title>'
            f"</circle>")
    return _moldura(altura, "".join(partes), props)


def svg_rede(props, series, categorias):
    nos = props.get("nos") or []
    ligacoes = props.get("ligacoes") or []
    altura = int(props.get("altura", 340))
    if not nos:
        return _vazio(altura)
    cx, cy = 400.0, altura / 2
    raio = min(altura / 2 - 34, 130)
    n = len(nos)
    graus = props.get("graus") or {}
    cores = _cores(props)
    posicao = {}
    for i, no in enumerate(nos):
        angulo = 2 * math.pi * i / n - math.pi / 2
        posicao[no] = (cx + math.cos(angulo) * raio,
                       cy + math.sin(angulo) * raio)
    partes = []
    maior_peso = max((l["peso"] for l in ligacoes), default=1.0) or 1.0
    for l in ligacoes:
        x1, y1 = posicao[l["de"]]
        x2, y2 = posicao[l["para"]]
        # A aresta curva pelo centro: reta, duas ligações opostas viram
        # uma só linha e o grafo perde metade da informação.
        partes.append(
            f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="var(--v-texto-fraco)" stroke-opacity="0.38" '
            f'stroke-width="{0.8 + 2.6 * l["peso"] / maior_peso:.2f}">'
            f'<title>{_e(l["de"])} → {_e(l["para"])}: {l["peso"]:g}</title>'
            f"</path>")
    maior_grau = max(graus.values()) if graus else 1
    for i, no in enumerate(nos):
        x, y = posicao[no]
        r = 5 + 9 * (graus.get(no, 1) / (maior_grau or 1))
        partes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
            f'fill="{_a(cores[i % len(cores)])}">'
            f'<title>{_e(no)} — {graus.get(no, 0)} ligação(ões)</title></circle>')
        angulo = 2 * math.pi * i / n - math.pi / 2
        tx = cx + math.cos(angulo) * (raio + 18)
        ty = cy + math.sin(angulo) * (raio + 18)
        ancora = ("middle" if abs(tx - cx) < 10 else
                  ("start" if tx > cx else "end"))
        partes.append(
            f'<text class="v-eixo" x="{tx:.1f}" y="{ty + 4:.1f}" '
            f'text-anchor="{ancora}">{_e(_encurtar(no, 14))}</text>')
    return _moldura(altura, "".join(partes), props)


#: O que este arquivo acrescenta ao despacho do renderizador.
DESENHOS = {
    "combo": svg_combo,
    "barras_100": svg_barras_100,
    "radar": svg_radar,
    "medidor": svg_medidor,
    "bala": svg_bala,
    "funil": svg_funil,
    "treemap": svg_treemap,
    "cascata": svg_cascata,
    "pareto": svg_pareto,
    "mapa_de_calor": svg_mapa_de_calor,
    "calendario": svg_calendario,
    "caixa": svg_caixa,
    "bolhas": svg_bolhas,
    "dispersao_xy": svg_dispersao_xy,
    "velas": svg_velas,
    "sankey": svg_sankey,
    "gantt": svg_gantt,
    "mapa": svg_mapa,
    "rede": svg_rede,
}
