"""Os gráficos que um painel de verdade pede.

Os seis primeiros — linha, barras, área, dispersão, pizza, histograma —
cobrem um relatório. Um **painel** pede o resto: a rosca com o total no
meio, o combinado de barra e linha, a cascata que explica de onde veio
a diferença, o mapa de calor que mostra a hora de pico, o medidor que
compara com a meta.

Todos continuam sendo **SVG escrito no servidor**, pela mesma razão do
primeiro dia: nenhuma biblioteca de gráfico, nenhuma CDN, nada que
quebre numa rede fechada.

O preço da escolha, dito de frente
----------------------------------
Um gráfico desenhado no servidor não tem zoom, nem seleção de faixa com
o mouse, nem o legendário clique-para-esconder-a-série de uma biblioteca
de JavaScript. O que ele tem é a dica ao passar o cursor, que é escrita
em SVG puro, e a legenda com os valores ao lado — que é o que a maioria
dos painéis realmente usa. Quem precisa de exploração interativa tem
`V.grade`, que filtra e ordena o dado por baixo do gráfico.

Cada função aqui faz uma coisa: transforma o dado na forma que o
desenho espera, e põe **um** nó na árvore. O desenho mora em
`render_extra.py`, e a separação é a mesma do resto do framework — a
árvore é dado, e é ela que os testes conferem.
"""

import math

from . import graficos as G
from .nucleo import No

_registros = G._registros
_num = G._numero
_texto = G._texto
PALETA = G.PALETA


def _ctx():
    from .componentes import _ctx as obter
    return obter()


def _por_grafico(tipo, props):
    """Um nó de gráfico com os padrões que todos compartilham."""
    base = {"grafico": tipo, "cores": list(PALETA), "altura": 280,
            "grade": True, "legenda": True, "legenda_em": "baixo",
            "rotulos": False, "empilhado": False, "suave": False,
            "dica": True, "formato": "", "series": [], "categorias": []}
    base.update({k: v for k, v in props.items() if v is not None})
    ctx = _ctx()
    base["largura_css"] = ctx.largura
    ctx.por(No("grafico", base))
    return base


def _extras(titulo, altura, cores, formato, kw):
    saida = {"titulo": str(titulo) if titulo else None,
             "altura": max(80, int(altura)) if altura else None,
             "cores": [str(c) for c in cores] if cores else None,
             "formato": str(formato) if formato else None}
    saida.update(kw or {})
    return saida


# ═══════════════════════════════════════════════════════════
#  Combinado — barra e linha na mesma moldura
# ═══════════════════════════════════════════════════════════

def grafico_combo(dados, x="", barras=None, linhas=None, titulo="",
                  altura=None, cores=None, formato="", direita=None,
                  empilhado=False, **kw):
    """Barras e linhas no mesmo gráfico.

        V.grafico_combo(mes_a_mes, x := "mes",
                        barras := ["receita", "despesa"],
                        linhas := ["margem"], direita := ["margem"])

    `direita` põe aquelas séries numa **segunda escala**. Sem ela, uma
    margem de 0 a 100 ao lado de uma receita de milhões vira uma linha
    colada no zero: o gráfico existe e não mostra nada.
    """
    registros = _registros(dados)
    campos_barra = [str(c) for c in (barras or [])]
    campos_linha = [str(c) for c in (linhas or [])]
    if not campos_barra and not campos_linha:
        campos_barra = _numericas(registros, x)[:1]
        campos_linha = _numericas(registros, x)[1:2]

    categorias = _categorias(registros, x)
    series, tipos = [], {}
    for campo in campos_barra + campos_linha:
        series.append({"nome": campo,
                       "valores": [_num(r.get(campo)) for r in registros]})
        tipos[campo] = "barra" if campo in campos_barra else "linha"
    return _por_grafico("combo", _extras(titulo, altura, cores, formato, {
        "series": series, "categorias": categorias, "tipos_de_serie": tipos,
        "direita": [str(d) for d in (direita or [])],
        "empilhado": bool(empilhado), **kw}))


# ═══════════════════════════════════════════════════════════
#  Composição
# ═══════════════════════════════════════════════════════════

def grafico_barras_100(dados, x="", y=None, titulo="", altura=None,
                       cores=None, **kw):
    """Barras empilhadas em que cada categoria soma 100%.

    É a pergunta "de que isto é feito?", contra a "quanto é?" das
    barras normais — e a diferença importa quando o total varia muito
    entre as categorias.
    """
    series, categorias = _series_de(dados, x, y)
    return _por_grafico("barras_100", _extras(titulo, altura, cores, "", {
        "series": series, "categorias": categorias, "empilhado": True,
        "cem_por_cento": True, "formato": "percentual", **kw}))


def grafico_area_empilhada(dados, x="", y=None, titulo="", altura=None,
                           cores=None, **kw):
    """Áreas somadas — a evolução do todo e das partes ao mesmo tempo."""
    series, categorias = _series_de(dados, x, y)
    return _por_grafico("area", _extras(titulo, altura, cores, "", {
        "series": series, "categorias": categorias, "empilhado": True, **kw}))


def grafico_funil(dados, x="", y="", titulo="", altura=None, cores=None,
                  formato="", **kw):
    """O funil: quanto sobra em cada etapa.

    Cada faixa traz a conversão **em relação à etapa anterior** e ao
    topo. Só o total seria pior que inútil: o gargalo é uma passagem, e
    não um estágio.
    """
    series, categorias = _series_de(dados, x, [y] if y else None)
    valores = series[0]["valores"] if series else []
    return _por_grafico("funil", _extras(titulo, altura, cores, formato, {
        "series": series, "categorias": categorias, "legenda": False,
        "etapas": _etapas_do_funil(categorias, valores), **kw}))


def _etapas_do_funil(categorias, valores):
    topo = valores[0] if valores else 0
    etapas = []
    for i, valor in enumerate(valores):
        anterior = valores[i - 1] if i else valor
        etapas.append({
            "rotulo": categorias[i] if i < len(categorias) else str(i + 1),
            "valor": valor,
            "do_topo": (valor / topo * 100) if topo else 0.0,
            "da_anterior": (valor / anterior * 100) if anterior else 0.0,
        })
    return etapas


def grafico_treemap(dados, rotulo="", valor="", titulo="", altura=None,
                    cores=None, formato="", **kw):
    """Retângulos proporcionais — a composição quando há itens demais.

    Uma pizza com vinte fatias é ilegível; um treemap com vinte
    retângulos ainda diz quem é grande e quem é pequeno.
    """
    registros = _registros(dados)
    campo_r = str(rotulo) or _primeiro_texto(registros)
    campo_v = str(valor) or (_numericas(registros, campo_r) or [""])[0]
    itens = [{"rotulo": _texto(r.get(campo_r, "")),
              "valor": max(0.0, _num(r.get(campo_v)))} for r in registros]
    itens = [i for i in itens if i["valor"] > 0]
    itens.sort(key=lambda i: -i["valor"])
    return _por_grafico("treemap", _extras(titulo, altura, cores, formato, {
        "itens": itens, "legenda": False,
        "series": [{"nome": campo_v, "valores": [i["valor"] for i in itens]}],
        "categorias": [i["rotulo"] for i in itens], **kw}))


# ═══════════════════════════════════════════════════════════
#  Explicar uma diferença
# ═══════════════════════════════════════════════════════════

def grafico_cascata(dados, x="", y="", titulo="", altura=None, cores=None,
                    formato="", total=True, **kw):
    """A cascata: de onde veio a diferença entre o começo e o fim.

    Cada barra parte de onde a anterior terminou. É o gráfico que
    responde "por que o resultado caiu?" — e a resposta é a soma das
    contribuições, que uma barra por categoria nunca mostra.

    Um item com valor **negativo** desce, e a cor muda. `total := yes`
    fecha com a barra do saldo, ancorada no zero.
    """
    registros = _registros(dados)
    campo_x = str(x) or _primeiro_texto(registros)
    campo_y = str(y) or (_numericas(registros, campo_x) or [""])[0]
    passos, acumulado = [], 0.0
    for r in registros:
        valor = _num(r.get(campo_y))
        passos.append({"rotulo": _texto(r.get(campo_x, "")), "valor": valor,
                       "de": acumulado, "ate": acumulado + valor,
                       "tipo": "sobe" if valor >= 0 else "desce"})
        acumulado += valor
    if total:
        passos.append({"rotulo": "Total", "valor": acumulado, "de": 0.0,
                       "ate": acumulado, "tipo": "total"})
    return _por_grafico("cascata", _extras(titulo, altura, cores, formato, {
        "passos": passos, "legenda": False,
        "series": [{"nome": campo_y, "valores": [p["ate"] for p in passos]}],
        "categorias": [p["rotulo"] for p in passos], **kw}))


def grafico_pareto(dados, x="", y="", titulo="", altura=None, cores=None,
                   formato="", corte=80, **kw):
    """Barras em ordem, com a curva do acumulado.

    A linha de 80% não é enfeite: ela mostra quantos itens respondem
    pela maior parte do total, que é a única pergunta que um Pareto
    existe para responder.
    """
    registros = _registros(dados)
    campo_x = str(x) or _primeiro_texto(registros)
    campo_y = str(y) or (_numericas(registros, campo_x) or [""])[0]
    pares = [(_texto(r.get(campo_x, "")), _num(r.get(campo_y)))
             for r in registros]
    pares.sort(key=lambda p: -p[1])
    total = sum(v for _, v in pares) or 1.0
    acumulado, curva = 0.0, []
    for _, valor in pares:
        acumulado += valor
        curva.append(acumulado / total * 100)
    return _por_grafico("pareto", _extras(titulo, altura, cores, formato, {
        "series": [{"nome": campo_y, "valores": [v for _, v in pares]}],
        "categorias": [c for c, _ in pares], "acumulado": curva,
        "corte": float(corte), **kw}))


# ═══════════════════════════════════════════════════════════
#  Comparar com a meta
# ═══════════════════════════════════════════════════════════

def medidor(valor, minimo=0, maximo=100, titulo="", faixas=None, altura=None,
            formato="", rotulo="", cores=None, **kw):
    """Um ponteiro numa escala, com faixas coloridas.

        V.medidor(72, 0, 100, faixas := [
            {"ate": 50, "cor": "#FA4D56"},
            {"ate": 80, "cor": "#F1C21B"},
            {"ate": 100, "cor": "#24A148"}])

    A faixa é o que dá sentido ao número: 72 é bom ou ruim depende de
    onde estão as fronteiras, e um medidor sem elas é um número grande
    com um arco em volta.
    """
    piso, teto = float(minimo), float(maximo)
    if teto <= piso:
        teto = piso + 1
    atual = max(piso, min(teto, _num(valor)))
    listadas = []
    for faixa in (faixas or []):
        if isinstance(faixa, dict):
            listadas.append({"ate": float(faixa.get("ate", teto)),
                             "cor": str(faixa.get("cor", ""))})
    return _por_grafico("medidor", _extras(titulo, altura, cores, formato, {
        "valor": atual, "minimo": piso, "maximo": teto, "faixas": listadas,
        "rotulo": str(rotulo), "legenda": False, "grade": False,
        "series": [{"nome": str(rotulo or titulo or "valor"),
                    "valores": [atual]}],
        "categorias": [str(rotulo or "")], **kw}))


def grafico_bala(valor, alvo, minimo=0, maximo=None, rotulo="", faixas=None,
                 titulo="", altura=None, cores=None, formato="", **kw):
    """A barra-bala: o valor, a meta e as faixas de referência numa linha.

    Ocupa a altura de uma linha de texto e diz o que um medidor diz
    ocupando um quarto da tela — é o que permite pôr oito indicadores
    com meta um embaixo do outro.
    """
    atingido = _num(valor)
    meta = _num(alvo)
    teto = float(maximo) if maximo is not None else max(atingido, meta) * 1.25
    return _por_grafico("bala", _extras(titulo, altura or 92, cores, formato, {
        "valor": atingido, "alvo": meta, "minimo": float(minimo),
        "maximo": teto or 1.0, "rotulo": str(rotulo), "legenda": False,
        "grade": False,
        "faixas": [{"ate": float(f.get("ate", teto)), "cor": str(f.get("cor", ""))}
                   for f in (faixas or []) if isinstance(f, dict)],
        "series": [{"nome": str(rotulo or "valor"), "valores": [atingido]}],
        "categorias": [str(rotulo or "")], **kw}))


# ═══════════════════════════════════════════════════════════
#  Matrizes
# ═══════════════════════════════════════════════════════════

def mapa_de_calor(dados, x="", y="", valor="", titulo="", altura=None,
                  cores=None, formato="", escala=None, **kw):
    """Uma matriz colorida — hora × dia, produto × região, mês × canal.

    A escala é **sequencial** e vai do claro ao forte da cor escolhida:
    uma escala de arco-íris inventa fronteiras onde o dado é contínuo, e
    é por isso que ela não é o padrão aqui.
    """
    registros = _registros(dados)
    campo_x = str(x) or _primeiro_texto(registros)
    restantes = [c for c in _colunas(registros) if c != campo_x]
    campo_y = str(y) or (restantes[0] if restantes else "")
    campo_v = str(valor) or (_numericas(registros, campo_x) or [""])[0]

    colunas, linhas, celulas = [], [], {}
    for r in registros:
        cx, cy = _texto(r.get(campo_x, "")), _texto(r.get(campo_y, ""))
        if cx not in colunas:
            colunas.append(cx)
        if cy not in linhas:
            linhas.append(cy)
        celulas[(cy, cx)] = _num(r.get(campo_v))
    matriz = [[celulas.get((lin, col)) for col in colunas] for lin in linhas]
    presentes = [v for linha in matriz for v in linha if v is not None]
    return _por_grafico("mapa_de_calor", _extras(titulo, altura, cores, formato, {
        "matriz": matriz, "colunas_x": colunas, "linhas_y": linhas,
        "minimo": min(presentes) if presentes else 0.0,
        "maximo": max(presentes) if presentes else 1.0,
        "escala": [str(c) for c in (escala or [])], "legenda": False,
        "grade": False,
        "series": [{"nome": campo_v, "valores": presentes}],
        "categorias": colunas, **kw}))


def grafico_calendario(dados, data="", valor="", ano=None, titulo="",
                       altura=None, cores=None, escala=None, **kw):
    """Um ano inteiro em quadradinhos, uma semana por coluna.

    É o mapa de calor de uma série diária, e serve para a pergunta que
    uma linha de 365 pontos não responde: *em que dias da semana isto
    acontece?*
    """
    registros = _registros(dados)
    campo_d = str(data) or _primeiro_texto(registros)
    campo_v = str(valor) or (_numericas(registros, campo_d) or [""])[0]
    dias = {}
    for r in registros:
        chave = _texto(r.get(campo_d, ""))[:10]
        if len(chave) == 10:
            dias[chave] = dias.get(chave, 0.0) + _num(r.get(campo_v))
    if not dias:
        return _por_grafico("calendario", _extras(titulo, altura, cores, "", {
            "dias": {}, "ano": int(ano) if ano else 0, "legenda": False,
            "series": [], "categorias": [], **kw}))
    qual = int(ano) if ano else int(sorted(dias)[len(dias) // 2][:4])
    valores = list(dias.values())
    return _por_grafico("calendario", _extras(titulo, altura or 190, cores, "", {
        "dias": dias, "ano": qual, "legenda": False, "grade": False,
        "minimo": min(valores), "maximo": max(valores),
        "escala": [str(c) for c in (escala or [])],
        "series": [{"nome": campo_v, "valores": valores}],
        "categorias": sorted(dias), **kw}))


def grafico_radar(dados, x="", y=None, titulo="", altura=None, cores=None,
                  **kw):
    """Eixos saindo do centro — comparar poucos itens em vários critérios.

    Funciona até umas oito pontas; acima disso vira uma teia ilegível, e
    a resposta certa é um gráfico de barras agrupadas.
    """
    series, categorias = _series_de(dados, x, y)
    return _por_grafico("radar", _extras(titulo, altura or 320, cores, "", {
        "series": series, "categorias": categorias, "grade": True, **kw}))


# ═══════════════════════════════════════════════════════════
#  Distribuição e relação
# ═══════════════════════════════════════════════════════════

def grafico_caixa(dados, y=None, titulo="", altura=None, cores=None,
                  formato="", **kw):
    """Caixa e bigodes: mediana, quartis e os pontos fora da curva.

    Uma média esconde a distribuição inteira — duas colunas com a mesma
    média podem ter formas completamente diferentes, e é só isto que um
    box-plot mostra.
    """
    registros = _registros(dados)
    campos = [str(c) for c in (y or _numericas(registros, ""))]
    resumos = []
    for campo in campos:
        valores = sorted(_num(r.get(campo)) for r in registros
                         if r.get(campo) is not None)
        if not valores:
            continue
        resumos.append(_resumo_de_caixa(campo, valores))
    todos = [v for r in resumos for v in (r["minimo"], r["maximo"])]
    return _por_grafico("caixa", _extras(titulo, altura, cores, formato, {
        "resumos": resumos, "legenda": False,
        "series": [{"nome": r["nome"], "valores": [r["mediana"]]}
                   for r in resumos],
        "categorias": [r["nome"] for r in resumos],
        "min_y": min(todos) if todos else 0,
        "max_y": max(todos) if todos else 1, **kw}))


def _resumo_de_caixa(nome, valores):
    """Os cinco números, com o quartil **por posição**.

    Interpolar inventa um valor que não aconteceu. É a mesma escolha do
    `Arcane.Perfil`, e pela mesma razão: num resumo de distribuição, o
    que se quer é uma medida que existiu.
    """
    def quartil(fracao):
        posicao = max(0, min(len(valores) - 1,
                             int(round(fracao * (len(valores) - 1)))))
        return valores[posicao]

    q1, mediana, q3 = quartil(0.25), quartil(0.5), quartil(0.75)
    amplitude = (q3 - q1) * 1.5
    dentro = [v for v in valores if q1 - amplitude <= v <= q3 + amplitude]
    fora = [v for v in valores if v not in dentro]
    return {"nome": str(nome), "q1": q1, "mediana": mediana, "q3": q3,
            "minimo": min(dentro) if dentro else valores[0],
            "maximo": max(dentro) if dentro else valores[-1],
            "fora": fora[:40], "n": len(valores)}


def grafico_bolhas(dados, x="", y="", tamanho="", rotulo="", titulo="",
                   altura=None, cores=None, formato="", **kw):
    """Três grandezas de uma vez: posição, posição e área.

    A área é proporcional ao valor, **não o raio**: dobrar o raio
    quadruplica a mancha, e o olho lê a área. É o erro mais comum num
    gráfico de bolhas, e ele exagera a diferença por um fator de dois.
    """
    registros = _registros(dados)
    numericas = _numericas(registros, "")
    campo_x = str(x) or (numericas[0] if numericas else "")
    campo_y = str(y) or (numericas[1] if len(numericas) > 1 else campo_x)
    campo_t = str(tamanho) or (numericas[2] if len(numericas) > 2 else "")
    campo_r = str(rotulo) or _primeiro_texto(registros)

    pontos = []
    for r in registros:
        pontos.append({"x": _num(r.get(campo_x)), "y": _num(r.get(campo_y)),
                       "tamanho": _num(r.get(campo_t)) if campo_t else 1.0,
                       "rotulo": _texto(r.get(campo_r, ""))})
    return _por_grafico("bolhas", _extras(titulo, altura, cores, formato, {
        "pontos": pontos, "rotulo_x": campo_x, "rotulo_y": campo_y,
        "legenda": False,
        "series": [{"nome": campo_y, "valores": [p["y"] for p in pontos]}],
        "categorias": [p["rotulo"] for p in pontos], **kw}))


def grafico_dispersao_xy(dados, x="", y="", titulo="", altura=None,
                         cores=None, formato="", tendencia=False, **kw):
    """Dispersão com o eixo x **numérico de verdade**.

    A `V.grafico_dispersao` usa a posição da linha como x, que é o certo
    para uma série ordenada e errado para uma relação entre duas
    grandezas: dois pontos com o mesmo x cairiam em lugares diferentes.

    `tendencia := yes` acrescenta a reta de mínimos quadrados e o r².
    """
    registros = _registros(dados)
    numericas = _numericas(registros, "")
    campo_x = str(x) or (numericas[0] if numericas else "")
    campo_y = str(y) or (numericas[1] if len(numericas) > 1 else campo_x)
    pontos = [{"x": _num(r.get(campo_x)), "y": _num(r.get(campo_y))}
              for r in registros]
    props = {"pontos": pontos, "rotulo_x": campo_x, "rotulo_y": campo_y,
             "legenda": False,
             "series": [{"nome": campo_y, "valores": [p["y"] for p in pontos]}],
             "categorias": [str(round(p["x"], 4)) for p in pontos]}
    if tendencia:
        props["tendencia"] = _minimos_quadrados(pontos)
    props.update(kw)
    return _por_grafico("dispersao_xy",
                        _extras(titulo, altura, cores, formato, props))


def _minimos_quadrados(pontos):
    """A reta, e o r² junto dela.

    Sem o r², uma reta é desenhada com a mesma confiança sobre uma nuvem
    sem relação nenhuma — e quem olha conclui que há uma.
    """
    n = len(pontos)
    if n < 2:
        return None
    sx = sum(p["x"] for p in pontos)
    sy = sum(p["y"] for p in pontos)
    sxy = sum(p["x"] * p["y"] for p in pontos)
    sxx = sum(p["x"] * p["x"] for p in pontos)
    denominador = n * sxx - sx * sx
    if abs(denominador) < 1e-12:
        return None
    a = (n * sxy - sx * sy) / denominador
    b = (sy - a * sx) / n
    media = sy / n
    total = sum((p["y"] - media) ** 2 for p in pontos)
    residuo = sum((p["y"] - (a * p["x"] + b)) ** 2 for p in pontos)
    r2 = 1 - residuo / total if total else 0.0
    return {"a": a, "b": b, "r2": round(r2, 4)}


# ═══════════════════════════════════════════════════════════
#  Financeiro
# ═══════════════════════════════════════════════════════════

def grafico_velas(dados, data="", abertura="abertura", maxima="maxima",
                  minima="minima", fechamento="fechamento", titulo="",
                  altura=None, cores=None, formato="", **kw):
    """Candlestick: abertura, máxima, mínima e fechamento.

    A cor sai da comparação entre abertura e fechamento — verde quando
    fechou acima, vermelho quando abaixo. É a convenção, e trocá-la
    tornaria o gráfico ilegível para quem já lê candles.
    """
    registros = _registros(dados)
    campo_d = str(data) or _primeiro_texto(registros)
    velas = []
    for r in registros:
        a, f = _num(r.get(abertura)), _num(r.get(fechamento))
        velas.append({
            "rotulo": _texto(r.get(campo_d, "")), "abertura": a,
            "maxima": _num(r.get(maxima)), "minima": _num(r.get(minima)),
            "fechamento": f, "subiu": f >= a})
    valores = [v for vela in velas for v in (vela["maxima"], vela["minima"])]
    return _por_grafico("velas", _extras(titulo, altura, cores, formato, {
        "velas": velas, "legenda": False,
        "series": [{"nome": "fechamento",
                    "valores": [v["fechamento"] for v in velas]}],
        "categorias": [v["rotulo"] for v in velas],
        "min_y": min(valores) if valores else 0,
        "max_y": max(valores) if valores else 1, **kw}))


# ═══════════════════════════════════════════════════════════
#  Fluxo, projeto e lugar
# ═══════════════════════════════════════════════════════════

def grafico_sankey(ligacoes, titulo="", altura=None, cores=None, formato="",
                   **kw):
    """Para onde o dinheiro (ou o usuário) foi.

        V.grafico_sankey([
            {"de": "Receita", "para": "Custos", "valor": 62},
            {"de": "Receita", "para": "Lucro",  "valor": 38}])

    O desenho é em **camadas**, e não com posição livre: uma otimização
    de cruzamentos exigiria iteração e daria um resultado diferente a
    cada execução — num relatório, isso é pior que um cruzamento.
    """
    lista = []
    for item in (ligacoes or []):
        if not isinstance(item, dict):
            continue
        lista.append({"de": _texto(item.get("de", "")),
                      "para": _texto(item.get("para", "")),
                      "valor": max(0.0, _num(item.get("valor", 0)))})
    lista = [l for l in lista if l["valor"] > 0 and l["de"] and l["para"]]
    return _por_grafico("sankey", _extras(titulo, altura or 340, cores, formato, {
        "ligacoes": lista, "camadas": _camadas_do_sankey(lista),
        "legenda": False, "grade": False,
        "series": [{"nome": "fluxo", "valores": [l["valor"] for l in lista]}],
        "categorias": [f'{l["de"]}→{l["para"]}' for l in lista], **kw}))


def _camadas_do_sankey(ligacoes):
    """Em que coluna cada nó fica: a mais à direita que suas origens.

    Um ciclo pararia o laço: o teto de voltas é o número de nós, e
    depois dele o que sobrou fica onde está. Um gráfico torto é melhor
    que um servidor preso.
    """
    nos = {}
    for l in ligacoes:
        nos.setdefault(l["de"], 0)
        nos.setdefault(l["para"], 0)
    for _ in range(len(nos)):
        mudou = False
        for l in ligacoes:
            if nos[l["para"]] < nos[l["de"]] + 1:
                nos[l["para"]] = nos[l["de"]] + 1
                mudou = True
        if not mudou:
            break
    return nos


def grafico_gantt(tarefas, titulo="", altura=None, cores=None, **kw):
    """Barras no tempo — o cronograma.

        V.grafico_gantt([
            {"tarefa": "Levantamento", "inicio": "2026-01-05",
             "fim": "2026-02-10", "grupo": "Descoberta", "progresso": 100}])
    """
    lista = []
    for item in (tarefas or []):
        if not isinstance(item, dict):
            continue
        lista.append({
            "tarefa": _texto(item.get("tarefa", item.get("nome", ""))),
            "inicio": _texto(item.get("inicio", ""))[:10],
            "fim": _texto(item.get("fim", ""))[:10],
            "grupo": _texto(item.get("grupo", "")),
            "progresso": max(0.0, min(100.0, _num(item.get("progresso", 0)))),
        })
    lista = [t for t in lista if len(t["inicio"]) == 10 and len(t["fim"]) == 10]
    return _por_grafico("gantt", _extras(
        titulo, altura or max(160, 30 * len(lista) + 56), cores, "", {
            "tarefas": lista, "legenda": False, "grade": True,
            "series": [{"nome": "progresso",
                        "valores": [t["progresso"] for t in lista]}],
            "categorias": [t["tarefa"] for t in lista], **kw}))


def grafico_mapa(pontos, titulo="", altura=None, cores=None, formato="",
                 **kw):
    """Pontos por latitude e longitude, numa projeção equirretangular.

        V.grafico_mapa([{"lat": -27.59, "lon": -48.55,
                         "rotulo": "Florianópolis", "valor": 120}])

    **Não há mapa por baixo.** Desenhar contorno de país exigiria
    carregar a geometria de algum lugar, e a regra deste framework é
    não buscar nada. O que existe aqui é a grade de meridianos e
    paralelos, que situa o ponto sem fingir um mapa que não veio junto.
    """
    lista = []
    for item in (pontos or []):
        if not isinstance(item, dict):
            continue
        lista.append({"lat": _num(item.get("lat", item.get("latitude", 0))),
                      "lon": _num(item.get("lon", item.get("longitude", 0))),
                      "rotulo": _texto(item.get("rotulo", "")),
                      "valor": _num(item.get("valor", 0))})
    return _por_grafico("mapa", _extras(titulo, altura or 340, cores, formato, {
        "pontos": lista, "legenda": False, "grade": True,
        "series": [{"nome": "valor", "valores": [p["valor"] for p in lista]}],
        "categorias": [p["rotulo"] for p in lista], **kw}))


def grafico_rede(ligacoes, titulo="", altura=None, cores=None, **kw):
    """Nós e arestas, dispostos em círculo.

    O círculo é escolha, e não limitação: um layout por força é
    iterativo, e num relatório o mesmo dado precisa dar o mesmo desenho
    todas as vezes.
    """
    lista, nos = [], []
    for item in (ligacoes or []):
        if not isinstance(item, dict):
            continue
        de = _texto(item.get("de", ""))
        para = _texto(item.get("para", ""))
        if not de or not para:
            continue
        lista.append({"de": de, "para": para,
                      "peso": max(0.1, _num(item.get("peso", 1)) or 1.0)})
        for nome in (de, para):
            if nome not in nos:
                nos.append(nome)
    graus = {n: 0 for n in nos}
    for l in lista:
        graus[l["de"]] += 1
        graus[l["para"]] += 1
    return _por_grafico("rede", _extras(titulo, altura or 340, cores, "", {
        "ligacoes": lista, "nos": nos, "graus": graus, "legenda": False,
        "grade": False,
        "series": [{"nome": "grau", "valores": [graus[n] for n in nos]}],
        "categorias": nos, **kw}))


# ═══════════════════════════════════════════════════════════
#  Miudezas
# ═══════════════════════════════════════════════════════════

def mini_grafico(valores, tipo="linha", cor="", altura=34, largura=120,
                 mostrar_valor=False):
    """Uma série miúda, do tamanho de uma linha de texto.

    Sem eixo, sem grade e sem legenda: ela não responde "quanto", e sim
    "para onde isto vem indo" ao lado do número que responde "quanto".
    """
    serie = [_num(v) for v in (valores or [])]
    forma = str(tipo)
    if forma not in ("linha", "barras", "area"):
        forma = "linha"
    _ctx().por(No("mini", {
        "valores": serie, "tipo": forma, "cor": str(cor),
        "altura": max(12, int(altura)), "largura": max(24, int(largura)),
        "mostrar_valor": bool(mostrar_valor)}))
    return valores


# ═══════════════════════════════════════════════════════════
#  Internas
# ═══════════════════════════════════════════════════════════

def _colunas(registros):
    vistas = []
    for r in registros:
        for c in r:
            if c not in vistas:
                vistas.append(c)
    return vistas


def _primeiro_texto(registros):
    """A primeira coluna não numérica — quase sempre o rótulo."""
    for coluna in _colunas(registros):
        amostra = next((r.get(coluna) for r in registros
                        if r.get(coluna) is not None), None)
        if not isinstance(amostra, (int, float)) or isinstance(amostra, bool):
            return coluna
    return _colunas(registros)[0] if registros else ""


def _numericas(registros, exceto):
    saida = []
    for coluna in _colunas(registros):
        if coluna == exceto:
            continue
        amostra = next((r.get(coluna) for r in registros
                        if r.get(coluna) is not None), None)
        if isinstance(amostra, (int, float)) and not isinstance(amostra, bool):
            saida.append(coluna)
    return saida


def _categorias(registros, x):
    campo = str(x) or _primeiro_texto(registros)
    if not campo:
        return [str(i + 1) for i in range(len(registros))]
    return [_texto(r.get(campo, "")) for r in registros]


def _series_de(dados, x, y):
    """O caminho comum: usa a mesma extração dos gráficos de sempre.

    Uma segunda leitura do dado divergiria da primeira — e aí o mesmo
    vault daria eixos diferentes conforme o tipo de gráfico escolhido.
    """
    props = {}
    if x:
        props["x"] = str(x)
    if y:
        props["y"] = [str(c) for c in (y if isinstance(y, (list, tuple)) else [y])]
    series, categorias = G._extrair(dados, props)
    return series, categorias
