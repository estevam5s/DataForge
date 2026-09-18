# -*- coding: utf-8 -*-
"""Arcane.Dsl — combinadores para escrever uma linguagem pequena.

O que faltava
-------------
A linguagem tem duas formas de DSL **interna**: palavra contextual no
parser (as onze do Kiln, os seis verbos do Quadro) e objeto com
operadores. As duas exigem mexer no DataForge ou desenhar uma API.

O que não havia era a DSL **externa**: ler um texto que segue uma
gramática sua — uma regra de preço, um filtro de busca, um formato de
configuração — sem trazer dependência nem escrever um analisador à mão
com índice e `persist`.

    numero := D.mapear(D.numero(), lambda t => cast t as Integer)
    soma := D.mapear(D.seq([numero, D.texto("+"), numero]),
                     lambda p => p[0] + p[2])

    D.analisar(soma, "2+3").valor()      # 5

Três decisões
-------------
1. **O resultado é um `Resultado`**, e não uma exceção. Texto de fora
   falha o tempo todo: obrigar `monitor` em volta de cada análise faria
   o caminho normal ser o do erro.

2. **A falha diz a POSIÇÃO e o que era esperado.** "não deu certo" não
   ajuda ninguém a consertar a linha 3 de um arquivo de configuração.

3. **O espaço é explícito.** Um combinador que pulasse espaço sozinho
   estaria decidindo por quem escreve a gramática — e em formato de
   largura fixa isso é exatamente o que não se quer. `D.espaco()` e
   `D.simbolo(x)` existem para quem quer o comportamento comum.
"""

from ..errors import RuntimeError_


class _Estado:
    """Onde a análise está: o texto e a posição."""

    __slots__ = ("texto", "pos")

    def __init__(self, texto, pos=0):
        self.texto = texto
        self.pos = pos


def _ok(valor, pos):
    return {"ok": True, "valor": valor, "pos": pos}


def _falha(pos, esperado):
    return {"ok": False, "pos": pos, "esperado": esperado}


def _chamar(analisador, estado):
    return analisador(estado)


# ═════════════════════════════════════════════════════════════
#  Os básicos
# ═════════════════════════════════════════════════════════════

def texto(esperado):
    """Casa exatamente este texto."""
    alvo = str(esperado)

    def analisar_texto(estado):
        if estado.texto.startswith(alvo, estado.pos):
            return _ok(alvo, estado.pos + len(alvo))
        return _falha(estado.pos, f"'{alvo}'")
    return analisar_texto


def numero():
    """Um número: `12`, `-3`, `2.5`. Devolve o TEXTO dele."""
    def analisar_numero(estado):
        inicio = estado.pos
        pos = inicio
        if pos < len(estado.texto) and estado.texto[pos] in "+-":
            pos += 1
        digitos = pos
        while pos < len(estado.texto) and estado.texto[pos].isdigit():
            pos += 1
        if pos == digitos:
            return _falha(inicio, "um numero")
        if pos < len(estado.texto) and estado.texto[pos] == ".":
            pos += 1
            while pos < len(estado.texto) and estado.texto[pos].isdigit():
                pos += 1
        return _ok(estado.texto[inicio:pos], pos)
    return analisar_numero


def nome():
    """Um identificador: letra ou '_', depois letras, dígitos e '_'."""
    def analisar_nome(estado):
        inicio = estado.pos
        pos = inicio
        if pos >= len(estado.texto) or not (estado.texto[pos].isalpha()
                                            or estado.texto[pos] == "_"):
            return _falha(inicio, "um nome")
        pos += 1
        while pos < len(estado.texto) and (estado.texto[pos].isalnum()
                                           or estado.texto[pos] == "_"):
            pos += 1
        return _ok(estado.texto[inicio:pos], pos)
    return analisar_nome


def entre_aspas(aspa='"'):
    """Um texto entre aspas, com `\\` escapando a próxima."""
    def analisar_aspas(estado):
        inicio = estado.pos
        if inicio >= len(estado.texto) or estado.texto[inicio] != aspa:
            return _falha(inicio, f"texto entre {aspa}")
        pos = inicio + 1
        pedacos = []
        while pos < len(estado.texto):
            ch = estado.texto[pos]
            if ch == "\\" and pos + 1 < len(estado.texto):
                pedacos.append(estado.texto[pos + 1])
                pos += 2
                continue
            if ch == aspa:
                return _ok("".join(pedacos), pos + 1)
            pedacos.append(ch)
            pos += 1
        return _falha(inicio, f"o {aspa} que fecha")
    return analisar_aspas


def espaco(obrigatorio=False):
    """Espaços e tabulações. Por padrão, zero ou mais."""
    def analisar_espaco(estado):
        pos = estado.pos
        while pos < len(estado.texto) and estado.texto[pos] in " \t":
            pos += 1
        if obrigatorio and pos == estado.pos:
            return _falha(estado.pos, "um espaco")
        return _ok(estado.texto[estado.pos:pos], pos)
    return analisar_espaco


def simbolo(qual):
    """Um texto com espaço opcional dos dois lados — a forma comum."""
    return mapear(seq([espaco(), texto(qual), espaco()]),
                  lambda partes: partes[1])


def qualquer_de(caracteres):
    """Um caractere que esteja nesta lista."""
    conjunto = set(str(caracteres))

    def analisar_um(estado):
        if estado.pos < len(estado.texto) and estado.texto[estado.pos] in conjunto:
            return _ok(estado.texto[estado.pos], estado.pos + 1)
        return _falha(estado.pos, f"um de '{''.join(sorted(conjunto))}'")
    return analisar_um


def ate(parada):
    """Tudo até encontrar este texto (que não é consumido)."""
    alvo = str(parada)

    def analisar_ate(estado):
        achado = estado.texto.find(alvo, estado.pos)
        if achado < 0:
            return _falha(estado.pos, f"'{alvo}' em algum lugar adiante")
        return _ok(estado.texto[estado.pos:achado], achado)
    return analisar_ate


# ═════════════════════════════════════════════════════════════
#  Os combinadores
# ═════════════════════════════════════════════════════════════

def seq(analisadores):
    """Todos, em ordem. Devolve um cluster com o que cada um casou."""
    lista = list(analisadores)

    def analisar_seq(estado):
        pos = estado.pos
        valores = []
        for analisador in lista:
            saida = _chamar(analisador, _Estado(estado.texto, pos))
            if not saida["ok"]:
                return saida
            valores.append(saida["valor"])
            pos = saida["pos"]
        return _ok(valores, pos)
    return analisar_seq


def ou(analisadores):
    """O primeiro que casar. A falha relatada é a que foi MAIS LONGE.

    Relatar a última tentativa apontaria sempre para a alternativa
    final, que raramente é a que a pessoa queria escrever.
    """
    lista = list(analisadores)

    def analisar_ou(estado):
        melhor = None
        for analisador in lista:
            saida = _chamar(analisador, _Estado(estado.texto, estado.pos))
            if saida["ok"]:
                return saida
            if melhor is None or saida["pos"] > melhor["pos"]:
                melhor = saida
        return melhor or _falha(estado.pos, "alguma alternativa")
    return analisar_ou


def muitos(analisador, minimo=0):
    """Zero ou mais — ou `minimo` ou mais."""
    def analisar_muitos(estado):
        pos = estado.pos
        valores = []
        while True:
            saida = _chamar(analisador, _Estado(estado.texto, pos))
            if not saida["ok"] or saida["pos"] == pos:
                break
            valores.append(saida["valor"])
            pos = saida["pos"]
        if len(valores) < minimo:
            return _falha(pos, f"pelo menos {minimo}")
        return _ok(valores, pos)
    return analisar_muitos


def opcional(analisador, padrao=None):
    """Casa se der; se não der, devolve o padrão sem consumir nada."""
    def analisar_opcional(estado):
        saida = _chamar(analisador, estado)
        return saida if saida["ok"] else _ok(padrao, estado.pos)
    return analisar_opcional


def separado_por(item, separador, minimo=0):
    """`a, b, c` — itens separados, sem sobra no fim."""
    resto = muitos(mapear(seq([separador, item]), lambda p: p[1]))

    def analisar_lista(estado):
        primeiro = _chamar(item, estado)
        if not primeiro["ok"]:
            if minimo == 0:
                return _ok([], estado.pos)
            return primeiro
        seguinte = _chamar(resto, _Estado(estado.texto, primeiro["pos"]))
        valores = [primeiro["valor"]] + list(seguinte["valor"])
        if len(valores) < minimo:
            return _falha(seguinte["pos"], f"pelo menos {minimo} item(ns)")
        return _ok(valores, seguinte["pos"])
    return analisar_lista


def mapear(analisador, acao):
    """Transforma o que casou."""
    def analisar_mapeado(estado):
        saida = _chamar(analisador, estado)
        if not saida["ok"]:
            return saida
        return _ok(acao(saida["valor"]), saida["pos"])
    return analisar_mapeado


def exigir(analisador, mensagem):
    """Troca a mensagem de falha por uma que fale a língua da gramática."""
    def analisar_exigido(estado):
        saida = _chamar(analisador, estado)
        if saida["ok"]:
            return saida
        return _falha(saida["pos"], str(mensagem))
    return analisar_exigido


def adiado(pegar):
    """Para a gramática que se refere a si mesma (expressão dentro de parêntese)."""
    def analisar_adiado(estado):
        return _chamar(pegar(), estado)
    return analisar_adiado


# ═════════════════════════════════════════════════════════════
#  Rodar
# ═════════════════════════════════════════════════════════════

def analisar(analisador, entrada, tudo=True):
    """Roda a gramática. Devolve `Resultado`: `ok(valor)` ou `falha(…)`.

    Com `tudo := yes` (o padrão), sobra de texto é falha — senão uma
    gramática que casa o começo aceitaria qualquer coisa depois.
    """
    from .arcane_resultado import Resultado
    fonte = str(entrada)
    saida = _chamar(analisador, _Estado(fonte, 0))
    if not saida["ok"]:
        return Resultado(False, erro={
            "posicao": saida["pos"],
            "esperado": saida.get("esperado", ""),
            "trecho": _trecho(fonte, saida["pos"]),
            "mensagem": (f"esperava {saida.get('esperado', 'outra coisa')} "
                         f"na posicao {saida['pos']}"),
        })
    if tudo and saida["pos"] < len(fonte):
        return Resultado(False, erro={
            "posicao": saida["pos"],
            "esperado": "o fim do texto",
            "trecho": _trecho(fonte, saida["pos"]),
            "mensagem": f"sobrou texto a partir da posicao {saida['pos']}",
        })
    return Resultado(True, saida["valor"])


def _trecho(fonte, pos, volta=12):
    inicio = max(0, pos - volta)
    fim = min(len(fonte), pos + volta)
    return fonte[inicio:fim]


def gramatica(regras, inicial):
    """Um vault de regras com um ponto de entrada — para gramáticas grandes.

    As regras podem se referir umas às outras pelo NOME, e é isso que
    permite recursão sem ordem de declaração.
    """
    if inicial not in regras:
        raise RuntimeError_(
            f"a regra inicial '{inicial}' não está na gramática.", 0, 0,
            nota=f"regras: {', '.join(sorted(regras))}",
            doc="metaprogramacao/dsl")

    def por_nome(qual):
        return adiado(lambda: regras[qual])

    return {"inicial": regras[inicial], "regra": por_nome,
            "analisar": lambda entrada, tudo=True: analisar(
                regras[inicial], entrada, tudo)}


class ArcaneDsl:
    """O dicionário que `adopt Arcane.Dsl` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Dsl",

            # ── básicos ──
            "texto": texto,
            "numero": numero,
            "nome": nome,
            "entre_aspas": entre_aspas,
            "espaco": espaco,
            "simbolo": simbolo,
            "qualquer_de": qualquer_de,
            "ate": ate,

            # ── combinadores ──
            "seq": seq,
            "ou": ou,
            "muitos": muitos,
            "opcional": opcional,
            "separado_por": separado_por,
            "mapear": mapear,
            "exigir": exigir,
            "adiado": adiado,

            # ── rodar ──
            "analisar": analisar,
            "gramatica": gramatica,
        }
