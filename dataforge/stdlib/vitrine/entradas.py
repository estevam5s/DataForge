"""Entradas — os campos que o painel de verdade precisa.

Os nove campos de `componentes.py` cobrem um formulário. Um painel
pede mais: um intervalo de datas, uma faixa de valores, um grupo de
pílulas para trocar o período sem abrir uma lista, uma nota de uma a
cinco estrelas.

Duas regras valem para todos:

1. **Devolver o valor, sempre.** Nenhum campo aqui devolve `void` para
   dizer "ninguém mexeu": ele devolve o padrão. O programa roda de
   cima para baixo, e a linha seguinte precisa de um valor.

2. **O padrão é conferido contra as opções.** Um valor guardado que
   saiu da lista — porque a lista mudou entre duas execuções — volta
   ao padrão em vez de virar um estado impossível.
"""

from . import componentes as C

_str = C._str
_por = C._por
_ctx = C._ctx
_numero_de = C._numero_de


# ═══════════════════════════════════════════════════════════
#  Tempo
# ═══════════════════════════════════════════════════════════

def hora(rotulo, valor="09:00", passo=60, chave=None):
    """Um horário. Devolve `"14:30"`."""
    ctx = _ctx()
    k = ctx.chave_para("hora", rotulo, chave)
    atual = _str(ctx.valor_de(k, valor))
    ctx.guardar_valor(k, atual)
    _por("hora", {"rotulo": _str(rotulo), "valor": atual,
                  "passo": max(1, int(passo)), "chave": k}, chave=k)
    return atual


def periodo(rotulo, inicio="", fim="", chave=None):
    """Duas datas. Devolve um cluster `[inicio, fim]`.

    Quando o fim vem antes do início, os dois são **trocados** em vez
    de recusados: é o que a pessoa quis dizer, e um erro aqui só
    obrigaria a arrastar de novo.
    """
    ctx = _ctx()
    k = ctx.chave_para("periodo", rotulo, chave)
    padrao = [_str(inicio), _str(fim)]
    atual = ctx.valor_de(k, padrao)
    if not isinstance(atual, (list, tuple)) or len(atual) != 2:
        atual = padrao
    a, b = _str(atual[0]), _str(atual[1])
    if a and b and a > b:
        a, b = b, a
    ctx.guardar_valor(k, [a, b])
    _por("periodo", {"rotulo": _str(rotulo), "inicio": a, "fim": b,
                     "chave": k}, chave=k)
    return [a, b]


# ═══════════════════════════════════════════════════════════
#  Faixas
# ═══════════════════════════════════════════════════════════

def faixa(rotulo, minimo=0, maximo=100, valor=None, passo=1, chave=None):
    """Dois cursores na mesma trilha. Devolve `[menor, maior]`."""
    ctx = _ctx()
    k = ctx.chave_para("faixa", rotulo, chave)
    piso = _numero_de(minimo, 0)
    teto = _numero_de(maximo, 100)
    padrao = list(valor) if isinstance(valor, (list, tuple)) and len(valor) == 2 \
        else [piso, teto]
    atual = ctx.valor_de(k, padrao)
    if not isinstance(atual, (list, tuple)) or len(atual) != 2:
        atual = padrao
    a = max(piso, min(teto, _numero_de(atual[0], piso)))
    b = max(piso, min(teto, _numero_de(atual[1], teto)))
    if a > b:
        a, b = b, a
    ctx.guardar_valor(k, [a, b])
    _por("faixa", {"rotulo": _str(rotulo), "minimo": piso, "maximo": teto,
                   "de": a, "ate": b, "passo": passo, "chave": k}, chave=k)
    return [a, b]


def deslizante_opcoes(rotulo, opcoes, indice=0, chave=None):
    """Um cursor sobre uma lista de rótulos. Devolve o rótulo escolhido.

    É o jeito de escolher entre `P`, `M` e `G`, ou entre sete faixas de
    preço, sem a pessoa precisar saber que por baixo há um número.
    """
    ctx = _ctx()
    lista = [_str(o) for o in (opcoes or [])] or [""]
    k = ctx.chave_para("deslizante_opcoes", rotulo, chave)
    padrao = lista[indice] if 0 <= indice < len(lista) else lista[0]
    atual = ctx.valor_de(k, padrao)
    if atual not in lista:
        # O valor pode ter vindo como posição: é o que o navegador
        # manda, porque o cursor é numérico.
        posicao = _numero_de(atual, -1)
        atual = lista[int(posicao)] if 0 <= int(posicao) < len(lista) else padrao
    ctx.guardar_valor(k, atual)
    _por("deslizante_opcoes", {"rotulo": _str(rotulo), "opcoes": lista,
                               "valor": atual,
                               "posicao": lista.index(atual),
                               "chave": k}, chave=k)
    return atual


# ═══════════════════════════════════════════════════════════
#  Escolha compacta
# ═══════════════════════════════════════════════════════════

def pilulas(rotulo, opcoes, padrao=None, varios=False, chave=None):
    """Botões arredondados, lado a lado. Um ou vários.

    Com `varios := no` devolve o rótulo; com `varios := yes` devolve um
    cluster. É o filtro que fica **visível** — uma lista suspensa
    esconde as opções, e num painel a pessoa precisa ver o que existe.
    """
    ctx = _ctx()
    lista = [_str(o) for o in (opcoes or [])]
    k = ctx.chave_para("pilulas", rotulo, chave)
    if varios:
        inicial = [_str(p) for p in (padrao or [])]
        atual = ctx.valor_de(k, inicial)
        if not isinstance(atual, (list, tuple)):
            atual = [atual] if atual else []
        atual = [v for v in atual if v in lista]
        ctx.guardar_valor(k, list(atual))
        _por("pilulas", {"rotulo": _str(rotulo), "opcoes": lista,
                         "valor": list(atual), "varios": True, "chave": k},
             chave=k)
        return list(atual)

    inicial = _str(padrao) if padrao is not None else (lista[0] if lista else "")
    atual = _str(ctx.valor_de(k, inicial))
    if atual not in lista and lista:
        atual = inicial if inicial in lista else lista[0]
    ctx.guardar_valor(k, atual)
    _por("pilulas", {"rotulo": _str(rotulo), "opcoes": lista, "valor": atual,
                     "varios": False, "chave": k}, chave=k)
    return atual


def segmentado(rotulo, opcoes, indice=0, chave=None):
    """Um grupo colado, com um segmento aceso. Devolve o rótulo."""
    ctx = _ctx()
    lista = [_str(o) for o in (opcoes or [])]
    k = ctx.chave_para("segmentado", rotulo, chave)
    padrao = lista[indice] if 0 <= indice < len(lista) else (
        lista[0] if lista else "")
    atual = _str(ctx.valor_de(k, padrao))
    if atual not in lista and lista:
        atual = padrao
    ctx.guardar_valor(k, atual)
    _por("segmentado", {"rotulo": _str(rotulo), "opcoes": lista,
                        "valor": atual, "chave": k}, chave=k)
    return atual


def avaliacao(rotulo, tipo="estrelas", maximo=5, valor=0, chave=None):
    """Uma nota. `tipo`: estrelas, coracoes ou polegares.

    Devolve `0` quando ninguém avaliou, e não `void`: a média de uma
    coluna de notas não deveria ter de tratar ausência antes de existir
    uma nota.
    """
    ctx = _ctx()
    k = ctx.chave_para("avaliacao", rotulo, chave)
    forma = _str(tipo)
    if forma not in ("estrelas", "coracoes", "polegares"):
        forma = "estrelas"
    teto = 2 if forma == "polegares" else max(2, int(maximo))
    atual = int(_numero_de(ctx.valor_de(k, valor), valor) or 0)
    atual = max(0, min(teto, atual))
    ctx.guardar_valor(k, atual)
    _por("avaliacao", {"rotulo": _str(rotulo), "tipo": forma, "maximo": teto,
                       "valor": atual, "chave": k}, chave=k)
    return atual


def tags(rotulo, valor=None, sugestoes=None, chave=None):
    """Etiquetas que se acrescenta digitando. Devolve um cluster."""
    ctx = _ctx()
    k = ctx.chave_para("tags", rotulo, chave)
    inicial = [_str(v) for v in (valor or [])]
    atual = ctx.valor_de(k, inicial)
    if isinstance(atual, str):
        # O navegador manda tudo junto, separado por vírgula.
        atual = [p.strip() for p in atual.split(",") if p.strip()]
    if not isinstance(atual, (list, tuple)):
        atual = inicial
    limpo = []
    for item in atual:
        texto = _str(item).strip()
        if texto and texto not in limpo:
            limpo.append(texto)
    ctx.guardar_valor(k, limpo)
    _por("tags", {"rotulo": _str(rotulo), "valor": limpo,
                  "sugestoes": [_str(s) for s in (sugestoes or [])],
                  "chave": k}, chave=k)
    return limpo


def autocompletar(rotulo, opcoes, valor="", dica="", chave=None):
    """Um campo de texto com sugestões. Devolve o que está escrito.

    Aceita o que não está na lista **de propósito**: a lista é atalho,
    não restrição. Para restringir, `V.escolha`.
    """
    ctx = _ctx()
    k = ctx.chave_para("autocompletar", rotulo, chave)
    atual = _str(ctx.valor_de(k, valor))
    ctx.guardar_valor(k, atual)
    _por("autocompletar", {"rotulo": _str(rotulo), "valor": atual,
                           "dica": _str(dica),
                           "opcoes": [_str(o) for o in (opcoes or [])],
                           "chave": k}, chave=k)
    return atual


# ═══════════════════════════════════════════════════════════
#  Atalhos sobre `V.entrada`
# ═══════════════════════════════════════════════════════════

def senha(rotulo="Senha", dica="", chave=None):
    return C.entrada(rotulo, "", dica, "senha", chave)


def busca(rotulo="Buscar", dica="", chave=None):
    return C.entrada(rotulo, "", dica or "digite para filtrar…", "busca", chave)


def email(rotulo="E-mail", valor="", dica="", chave=None):
    return C.entrada(rotulo, valor, dica, "email", chave)


def camera(rotulo="Foto", chave=None):
    """Tira uma foto pela câmera. Devolve o vault do arquivo, ou `void`.

    Depende de permissão do navegador **e de HTTPS** — um navegador não
    entrega a câmera numa página servida por HTTP fora de `localhost`.
    A mensagem que aparece quando a permissão é negada diz isso, porque
    o sintoma (um retângulo preto) não diz.
    """
    ctx = _ctx()
    k = ctx.chave_para("camera", rotulo, chave)
    _por("camera", {"rotulo": _str(rotulo), "chave": k}, chave=k)
    return ctx.sessao.obter(f"__arquivo__{k}")


# ═══════════════════════════════════════════════════════════
#  Reagir a uma mudança
# ═══════════════════════════════════════════════════════════

def mudou(chave):
    """`yes` quando o campo dessa chave chegou diferente **nesta** execução.

    É o `on_change` deste framework, e ele é uma pergunta em vez de um
    retorno de chamada por um motivo: o programa roda inteiro a cada
    interação, então a linha que reage à mudança pode estar onde ela é
    lida, e não num lugar separado.

        regiao := V.escolha("Região", regioes, chave := "regiao")
        given V.mudou("regiao"):
            V.estado.definir("pagina", 1)
    """
    return str(chave) in _ctx().mudados


def mudancas():
    """As chaves que mudaram nesta execução."""
    return sorted(_ctx().mudados)
