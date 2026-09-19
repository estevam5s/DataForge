# -*- coding: utf-8 -*-
"""Arcane.Perfil — medir com rigor: percentis, significância e regressão.

O que faltava
-------------
`Arcane.Bench` responde "quanto tempo leva" com uma **média**. É o que
quase toda ferramenta de benchmark faz, e é onde quase toda decisão de
performance erra:

* **a média esconde a cauda**, e é a cauda que o usuário sente. Cem
  requisições de 10 ms e uma de 1000 ms dão média 20 ms — e a pessoa que
  pegou a última espera um segundo.
* **duas médias diferentes podem ser a mesma coisa com ruído.** Sem
  teste estatístico não há como saber, e é assim que se escolhe a
  implementação errada com convicção.
* **um número sozinho não responde "piorou desde a semana passada?"**.

    adopt Arcane.Perfil as P

    m := P.medir(consultar, {"amostras": 200})
    out m["p50"], m["p95"], m["p99"]        // a cauda, nao a media

    v := P.comparar(antiga, nova, {"amostras": 60})
    given v["significativo"]:
        out $"{v['mais_rapido']} ganha por {v['fator']}x"

O teste que importa
-------------------
Comparar uma ação **com ela mesma** não pode dar "3% mais rápida". É o
que separa medição de superstição, e é o primeiro teste do arquivo.

A conta é o **Mann-Whitney U**, e não o teste t: tempo de execução não é
normal — tem cauda longa à direita, piso duro à esquerda e picos de
escalonamento. Um teste que supõe normalidade responde com confiança
sobre uma suposição falsa. O U não supõe nada sobre a forma: ele compara
**ordens**.

O que cada número responde
--------------------------
| Número | Responde |
|---|---|
| `p50` | o caso comum |
| `p95`, `p99` | o que o usuário reclama |
| `p_valor` | a diferença é real, ou é ruído? |
| `sobreposicao` | **quanto** é a diferença (tamanho do efeito) |
| `fator` | quantas vezes, na mediana |

Três decisões
-------------
1. **O aquecimento é separado e declarado.** As primeiras execuções
   medem cache frio, import preguiçoso e alocação inicial. Misturá-las
   com o resto não é medir o programa: é medir a partida.

2. **Os percentis saem da amostra, por posto** (*nearest-rank*), e não
   de uma interpolação. Interpolar inventa um valor que não aconteceu —
   e num P99 de latência o que se quer é uma medida que existiu.

3. **O flame graph é das AÇÕES**, pelo mesmo gancho que o
   `dataforge profile` usa (`_call_action` sombreado). Um perfil dos
   quadros do Python mostraria `evaluate` e `execute` no topo em todo
   programa — verdade, e inútil.
"""

import gc
import json
import math
import os
import threading
import time

from ..errors import RuntimeError_
from .opcoes import ler as _ler_opcoes

#: O padrão de `medir`. A lista é a documentação — e uma chave
#: desconhecida é recusada em vez de ignorada em silêncio.
MEDIR = {"amostras": 30, "aquecimento": 3, "argumento": None}

CONFERIR = {"arquivo": "perfil-base.json", "tolerancia": 0.15,
            "criterio": "p95"}

COMPARAR = {"amostras": 30, "aquecimento": 3, "argumento": None,
            "alfa": 0.05}


# ── resumo de uma amostra ─────────────────────────────────────

def _percentil(ordenados, q):
    """O valor na posição, por posto — sem interpolar.

    Interpolar inventa um valor que não aconteceu. Num P99 de latência o
    que se quer é uma medida que existiu de verdade.
    """
    if not ordenados:
        raise RuntimeError_("no samples", doc="observabilidade/perfil")
    posicao = math.ceil(q * len(ordenados))
    return ordenados[min(max(posicao, 1), len(ordenados)) - 1]


def resumir(valores, casas=4):
    """A distribuição de uma amostra: percentis, média e desvio."""
    dados = [float(v) for v in valores]
    if not dados:
        raise RuntimeError_(
            "Perfil.resumir needs at least one sample: the distribution of "
            "nothing is not zero, it is undefined.",
            doc="observabilidade/perfil")
    ordenados = sorted(dados)
    n = len(ordenados)
    media = sum(ordenados) / n
    if n > 1:
        variancia = sum((v - media) ** 2 for v in ordenados) / (n - 1)
    else:
        variancia = 0.0
    return {
        "amostras": n,
        "min": round(ordenados[0], casas),
        "p50": round(_percentil(ordenados, 0.50), casas),
        "p90": round(_percentil(ordenados, 0.90), casas),
        "p95": round(_percentil(ordenados, 0.95), casas),
        "p99": round(_percentil(ordenados, 0.99), casas),
        "p999": round(_percentil(ordenados, 0.999), casas),
        "max": round(ordenados[-1], casas),
        "media": round(media, casas),
        "desvio": round(math.sqrt(variancia), casas),
    }


# ── medir ─────────────────────────────────────────────────────

def _chamar(acao, argumento):
    return acao() if argumento is None else acao(argumento)


def _amostrar(acao, argumento, amostras, aquecimento):
    for _ in range(max(0, int(aquecimento))):
        _chamar(acao, argumento)
    tempos = []
    for _ in range(max(1, int(amostras))):
        inicio = time.perf_counter()
        _chamar(acao, argumento)
        tempos.append((time.perf_counter() - inicio) * 1000.0)
    return tempos


def medir(acao, opcoes=None):
    """A distribuição do tempo de uma ação, em milissegundos."""
    # `ler` RECUSA chave desconhecida e nao aplica padrao: quem chama
    # tem o seu `get`, e aplicar duas vezes criaria dois lugares para o
    # padrao divergir.
    config = _ler_opcoes(opcoes, MEDIR, "Perfil.medir")
    aquecimento = int(config.get("aquecimento", MEDIR["aquecimento"]))
    tempos = _amostrar(acao, config.get("argumento"),
                       config.get("amostras", MEDIR["amostras"]),
                       aquecimento)
    saida = resumir(tempos)
    saida["aquecimento"] = aquecimento
    saida["vazao"] = round(1000.0 / saida["p50"], 2) if saida["p50"] else 0.0
    saida["unidade"] = "ms"
    return saida


# ── significância ─────────────────────────────────────────────

def _phi(z):
    """A acumulada da normal — `math.erf` basta, e não traz dependência."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def mann_whitney(a, b):
    """`(U, p bilateral, sobreposição)` — sem supor forma nenhuma.

    Tempo de execução não é normal: tem cauda longa à direita, piso duro
    à esquerda e picos de escalonamento. Um teste t responderia com
    confiança sobre uma suposição falsa. O U compara **ordens**, e a
    correção de empates importa quando o relógio tem resolução grossa.
    """
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        raise RuntimeError_("both samples need values",
                            doc="observabilidade/comparar")

    juntos = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    postos = [0.0] * len(juntos)
    empates = []
    i = 0
    while i < len(juntos):
        j = i
        while j + 1 < len(juntos) and juntos[j + 1][0] == juntos[i][0]:
            j += 1
        posto_medio = (i + j) / 2.0 + 1.0     # postos começam em 1
        for k in range(i, j + 1):
            postos[k] = posto_medio
        if j > i:
            empates.append(j - i + 1)
        i = j + 1

    soma_a = sum(p for p, (_v, lado) in zip(postos, juntos) if lado == 0)
    u_a = soma_a - n1 * (n1 + 1) / 2.0
    u_b = n1 * n2 - u_a
    u = min(u_a, u_b)

    n = n1 + n2
    media = n1 * n2 / 2.0
    correcao = sum(t ** 3 - t for t in empates)
    variancia = (n1 * n2 / 12.0) * ((n + 1) - correcao / (n * (n - 1.0))) \
        if n > 1 else 0.0
    if variancia <= 0:
        return u, 1.0, 0.5
    z = (u - media) / math.sqrt(variancia)
    p = 2.0 * _phi(-abs(z))
    # A "linguagem comum": a chance de um sorteio de A ser menor que um
    # de B. É o tamanho do efeito, e é o que `p` NÃO diz.
    sobreposicao = u_b / (n1 * n2)
    return u, min(1.0, max(0.0, p)), sobreposicao


def comparar(a, b, opcoes=None):
    """As duas ações são diferentes — ou é ruído?"""
    config = _ler_opcoes(opcoes, COMPARAR, "Perfil.comparar")
    argumento = config.get("argumento")
    amostras = int(config.get("amostras", COMPARAR["amostras"]))
    aquecimento = int(config.get("aquecimento", COMPARAR["aquecimento"]))

    # Intercalar as duas medições é o que tira a deriva da máquina da
    # conta: medir A inteiro e depois B inteiro faz uma queda de clock no
    # meio virar "B é mais lenta".
    tempos_a, tempos_b = [], []
    for _ in range(aquecimento):
        _chamar(a, argumento)
        _chamar(b, argumento)
    for _ in range(max(1, amostras)):
        inicio = time.perf_counter()
        _chamar(a, argumento)
        tempos_a.append((time.perf_counter() - inicio) * 1000.0)
        inicio = time.perf_counter()
        _chamar(b, argumento)
        tempos_b.append((time.perf_counter() - inicio) * 1000.0)

    resumo_a, resumo_b = resumir(tempos_a), resumir(tempos_b)
    _u, p, sobreposicao = mann_whitney(tempos_a, tempos_b)
    alfa = float(config.get("alfa", COMPARAR["alfa"]))
    significativo = p < alfa

    if not significativo:
        mais_rapido, fator = "empate", 1.0
    elif resumo_a["p50"] <= resumo_b["p50"]:
        mais_rapido = "a"
        fator = (resumo_b["p50"] / resumo_a["p50"]) if resumo_a["p50"] else 0.0
    else:
        mais_rapido = "b"
        fator = (resumo_a["p50"] / resumo_b["p50"]) if resumo_b["p50"] else 0.0

    return {
        "mais_rapido": mais_rapido,
        "fator": round(fator, 3),
        "significativo": significativo,
        "p_valor": round(p, 6),
        "alfa": alfa,
        "sobreposicao": round(sobreposicao, 4),
        "a": resumo_a,
        "b": resumo_b,
    }


# ── linha de base e regressão ─────────────────────────────────

def _carregar(arquivo):
    if not os.path.isfile(arquivo):
        return {}
    try:
        with open(arquivo, encoding="utf-8") as f:
            dados = json.load(f)
        return dados if isinstance(dados, dict) else {}
    except (OSError, ValueError):
        return {}


def guardar(nome, medida, arquivo="perfil-base.json"):
    """Grava esta medida como a referência de `nome`."""
    base = _carregar(arquivo)
    base[str(nome)] = {chave: medida[chave] for chave in
                       ("p50", "p95", "p99", "media", "amostras")
                       if chave in medida}
    base[str(nome)]["quando"] = time.strftime("%Y-%m-%d %H:%M:%S")
    pasta = os.path.dirname(os.path.abspath(arquivo))
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2, sort_keys=True)
    return True


def conferir(nome, medida, opcoes=None):
    """Comparou com a referência: piorou, melhorou, ou está igual?

    **A primeira medida nunca reprova.** Sem base guardada não há
    regressão — só um começo; reprovar ali faria todo CI novo nascer
    vermelho, e a primeira coisa que se faz com um CI vermelho por
    desenho é desligá-lo.
    """
    config = _ler_opcoes(opcoes, CONFERIR, "Perfil.conferir")
    criterio = str(config.get("criterio", CONFERIR["criterio"]))
    tolerancia = float(config.get("tolerancia", CONFERIR["tolerancia"]))
    arquivo = config.get("arquivo", CONFERIR["arquivo"])
    base = _carregar(arquivo).get(str(nome))

    if not base or criterio not in base:
        return {"conhecida": False, "regrediu": False, "melhorou": False,
                "fator": 1.0, "criterio": criterio,
                "dica": "primeira medida: guarde-a com Perfil.guardar"}

    antes, agora = float(base[criterio]), float(medida[criterio])
    fator = (agora / antes) if antes else 1.0
    return {
        "conhecida": True,
        "regrediu": fator > 1.0 + tolerancia,
        "melhorou": fator < 1.0 - tolerancia,
        "fator": round(fator, 3),
        "antes": antes,
        "agora": agora,
        "criterio": criterio,
        "tolerancia": tolerancia,
        "quando": base.get("quando", ""),
    }


# ── flame graph das AÇÕES ─────────────────────────────────────

class _Coleta:
    """O estado de um perfil em andamento."""

    __slots__ = ("interp", "original", "pilha", "proprio", "pilhas",
                 "chamadas", "inicio")

    def __init__(self, interp):
        self.interp = interp
        self.original = interp._call_action
        self.pilha = []
        self.proprio = []
        self.pilhas = {}
        self.chamadas = 0
        self.inicio = time.perf_counter()


def comecar_perfil(interp):
    """Sombreia `_call_action` — o mesmo gancho do `dataforge profile`.

    Um perfil dos quadros do **Python** mostraria `evaluate` e `execute`
    no topo de todo programa: verdadeiro, e inútil. O que responde "onde
    mexer" é a ação da linguagem.
    """
    coleta = _Coleta(interp)

    def medido(action, *resto, **kwargs):
        nome = getattr(action, "name", "?") or "<lambda>"
        coleta.pilha.append(nome)
        coleta.proprio.append(0.0)
        coleta.chamadas += 1
        comeco = time.perf_counter()
        try:
            return coleta.original(action, *resto, **kwargs)
        finally:
            gasto = time.perf_counter() - comeco
            nos_filhos = coleta.proprio.pop()
            # Tempo PRÓPRIO: o total menos o que as chamadas internas
            # gastaram. Somar o acumulado daria mais de 100%, e um
            # flame graph com 207% não é um flame graph.
            sozinho = max(0.0, gasto - nos_filhos)
            caminho = ";".join(coleta.pilha)
            coleta.pilhas[caminho] = coleta.pilhas.get(caminho, 0.0) + sozinho
            coleta.pilha.pop()
            if coleta.proprio:
                coleta.proprio[-1] += gasto

    interp._call_action = medido
    return coleta


def terminar_perfil(coleta):
    """Devolve o gancho e entrega as pilhas dobradas."""
    try:
        del coleta.interp._call_action
    except AttributeError:                      # pragma: no cover
        coleta.interp._call_action = coleta.original
    total = time.perf_counter() - coleta.inicio
    pilhas = {caminho: int(round(seg * 1_000_000))
              for caminho, seg in coleta.pilhas.items()}
    pilhas = {c: us for c, us in pilhas.items() if us > 0}
    return {
        "pilhas": pilhas,
        "total_us": int(round(total * 1_000_000)),
        "acoes": len({c.split(";")[-1] for c in coleta.pilhas}),
        "chamadas": coleta.chamadas,
    }


def perfilar(acao, interp=None):
    """Roda a ação com o perfil ligado e devolve `(resultado, perfil)`."""
    from ..interpreter import Interpreter

    alvo = interp
    if alvo is None:
        alvo = getattr(acao, "closure", None)
        alvo = getattr(alvo, "interpreter", None)
    if alvo is None:                            # pragma: no cover
        raise RuntimeError_(
            "Perfil.perfilar needs the interpreter: call it from inside a "
            "program, or use comecar_perfil/terminar_perfil.",
            doc="observabilidade/chamadas")
    coleta = comecar_perfil(alvo)
    try:
        resultado = acao()
    finally:
        perfil = terminar_perfil(coleta)
    return {"resultado": resultado, "perfil": perfil}


def chama_texto(perfil):
    """O formato dobrado: `a;b;c <microssegundos>`, uma pilha por linha.

    É o que o `flamegraph.pl` consome, e o que qualquer visualizador de
    perfil aceita — inclusive os de navegador. Escolhido por isso: um
    formato próprio obrigaria a escrever o visualizador também.
    """
    linhas = [f"{caminho} {us}"
              for caminho, us in sorted(perfil.get("pilhas", {}).items())]
    return "\n".join(linhas)


def _cor(nome):
    """Uma cor quente estável por nome — é o que faz o gráfico ser lido."""
    semente = 0
    for letra in nome:
        semente = (semente * 31 + ord(letra)) & 0xFFFFFFFF
    vermelho = 205 + semente % 50
    verde = 80 + (semente >> 8) % 130
    azul = 30 + (semente >> 16) % 50
    return f"#{vermelho:02x}{verde:02x}{azul:02x}"


def _escapar(texto):
    return (str(texto).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def chama_svg(perfil, largura=1200, altura_linha=18):
    """O flame graph, em SVG e sem nada de fora.

    Sem CDN, sem script externo e sem fonte remota — a mesma regra da
    Vitrine, e pelo mesmo motivo: um gráfico de perfil costuma ser aberto
    em rede fechada.
    """
    pilhas = perfil.get("pilhas", {})
    if not pilhas:
        return ('<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"'
                ' width="400" height="40"><text x="8" y="24" '
                'font-family="monospace" font-size="12">sem amostras</text>'
                '</svg>')

    # A árvore: cada pilha dobrada vira um caminho, e o peso sobe.
    raiz = {"nome": "todo o programa", "valor": 0, "filhos": {}}
    for caminho, valor in pilhas.items():
        no = raiz
        no["valor"] += valor
        for parte in caminho.split(";"):
            no = no["filhos"].setdefault(
                parte, {"nome": parte, "valor": 0, "filhos": {}})
            no["valor"] += valor

    profundidade = [0]

    def medir_fundo(no, nivel):
        profundidade[0] = max(profundidade[0], nivel)
        for filho in no["filhos"].values():
            medir_fundo(filho, nivel + 1)

    medir_fundo(raiz, 0)
    altura = (profundidade[0] + 1) * altura_linha + 34
    total = max(1, raiz["valor"])
    partes = []

    def desenhar(no, nivel, x, largura_no):
        if largura_no < 0.35:
            return
        y = altura - (nivel + 1) * altura_linha - 4
        fracao = 100.0 * no["valor"] / total
        rotulo = _escapar(no["nome"])
        partes.append(
            f'<g><title>{rotulo} — {no["valor"]}us ({fracao:.1f}%)</title>'
            f'<rect x="{x:.2f}" y="{y}" width="{largura_no:.2f}" '
            f'height="{altura_linha - 1}" fill="{_cor(no["nome"])}" '
            f'rx="2"/>')
        if largura_no > 34:
            cabem = int((largura_no - 8) / 6.2)
            texto = no["nome"] if len(no["nome"]) <= cabem \
                else no["nome"][:max(1, cabem - 1)] + "…"
            partes.append(
                f'<text x="{x + 4:.2f}" y="{y + altura_linha - 6}" '
                f'font-family="monospace" font-size="11" fill="#1a1a1a">'
                f'{_escapar(texto)}</text>')
        partes.append("</g>")
        filho_x = x
        for filho in sorted(no["filhos"].values(),
                            key=lambda f: -f["valor"]):
            filho_largura = largura_no * filho["valor"] / max(1, no["valor"])
            desenhar(filho, nivel + 1, filho_x, filho_largura)
            filho_x += filho_largura

    desenhar(raiz, 0, 0.0, float(largura))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" '
        f'height="{altura}" viewBox="0 0 {largura} {altura}">'
        f'<rect width="{largura}" height="{altura}" fill="#faf8f5"/>'
        f'<text x="8" y="18" font-family="monospace" font-size="12" '
        f'fill="#555">tempo proprio por acao — {perfil.get("chamadas", 0)} '
        f'chamada(s), {perfil.get("acoes", 0)} acao(oes)</text>'
        + "".join(partes) + "</svg>")


# ── pausas do coletor ─────────────────────────────────────────

def gc_pausas(acao):
    """Quanto o coletor parou o programa enquanto a ação rodava.

    A pausa do coletor é o que transforma um P50 bom num P99 ruim, e ela
    não aparece em medida nenhuma que olhe só o tempo total. `gc.callbacks`
    entrega o começo e o fim de cada coleta — é a medida na fonte.
    """
    pausas = []
    comeco = {"t": None, "geracao": 0}

    def ouvir(fase, info):
        if fase == "start":
            comeco["t"] = time.perf_counter()
            comeco["geracao"] = info.get("generation", 0)
        elif fase == "stop" and comeco["t"] is not None:
            pausas.append(((time.perf_counter() - comeco["t"]) * 1000.0,
                           comeco["geracao"]))
            comeco["t"] = None

    gc.callbacks.append(ouvir)
    try:
        resultado = acao()
    finally:
        try:
            gc.callbacks.remove(ouvir)
        except ValueError:                      # pragma: no cover
            pass

    tempos = [t for t, _g in pausas]
    saida = {
        "resultado": resultado,
        "pausas": len(pausas),
        "total_ms": round(sum(tempos), 4),
        "por_geracao": {str(g): sum(1 for _t, gg in pausas if gg == g)
                        for g in (0, 1, 2)},
    }
    if tempos:
        saida.update({chave: valor for chave, valor in resumir(tempos).items()
                      if chave in ("p50", "p95", "p99", "max", "media")})
        saida["maior_ms"] = saida.pop("max")
    else:
        saida.update({"p50": 0.0, "p95": 0.0, "p99": 0.0, "media": 0.0,
                      "maior_ms": 0.0})
    return saida


# ── contenção de trava ────────────────────────────────────────

class TravaObservada:
    """Um mutex que conta quem esperou, e por quanto.

    Contenção não aparece num perfil de CPU: a thread bloqueada não gasta
    CPU nenhuma. Ela aparece como latência que ninguém explica — e a
    única forma de vê-la é medir na própria trava.
    """

    __slots__ = ("_trava", "_aquisicoes", "_esperas", "_esperando",
                 "_segurando", "_conta")

    def __init__(self):
        self._trava = threading.Lock()
        self._conta = threading.Lock()
        self._aquisicoes = 0
        self._esperas = 0
        self._esperando = 0.0
        self._segurando = 0.0

    def com(self, acao):
        inicio = time.perf_counter()
        # A tentativa sem bloqueio é o que distingue "peguei na hora" de
        # "esperei": sem ela, toda aquisição contaria como espera.
        pegou = self._trava.acquire(blocking=False)
        esperou = 0.0
        if not pegou:
            self._trava.acquire()
            esperou = time.perf_counter() - inicio
        dentro = time.perf_counter()
        try:
            return acao()
        finally:
            gasto = time.perf_counter() - dentro
            self._trava.release()
            with self._conta:
                self._aquisicoes += 1
                self._segurando += gasto
                if esperou > 0:
                    self._esperas += 1
                    self._esperando += esperou

    def estatisticas(self):
        with self._conta:
            return {
                "aquisicoes": self._aquisicoes,
                "esperas": self._esperas,
                "tempo_esperando_ms": round(self._esperando * 1000.0, 4),
                "tempo_segurando_ms": round(self._segurando * 1000.0, 4),
                "disputa": round(self._esperas / self._aquisicoes, 4)
                if self._aquisicoes else 0.0,
            }


def trava():
    return TravaObservada()


def com_trava(alvo, acao):
    if not isinstance(alvo, TravaObservada):
        raise RuntimeError_(
            "Perfil.com_trava expects a lock made with Perfil.trava().",
            doc="observabilidade/chamadas")
    return alvo.com(acao)


def estatisticas_da_trava(alvo):
    if not isinstance(alvo, TravaObservada):
        raise RuntimeError_(
            "Perfil.estatisticas_da_trava expects a lock made with "
            "Perfil.trava().", doc="observabilidade/chamadas")
    return alvo.estatisticas()


# ── relatório ─────────────────────────────────────────────────

def relatorio(medida):
    """A distribuição escrita, com a cauda em destaque."""
    linhas = [
        f"  amostras   {medida.get('amostras', 0)}"
        f"   (aquecimento: {medida.get('aquecimento', 0)})",
        "",
        f"  p50        {medida.get('p50', 0):>10.4f} ms   o caso comum",
        f"  p90        {medida.get('p90', 0):>10.4f} ms",
        f"  p95        {medida.get('p95', 0):>10.4f} ms   a cauda",
        f"  p99        {medida.get('p99', 0):>10.4f} ms   o que reclamam",
        f"  max        {medida.get('max', 0):>10.4f} ms",
        "",
        f"  media      {medida.get('media', 0):>10.4f} ms"
        f"   (desvio {medida.get('desvio', 0):.4f})",
    ]
    p50, media = medida.get("p50", 0), medida.get("media", 0)
    if p50 and media / p50 > 1.3:
        linhas.append("")
        linhas.append("  a media esta bem acima da mediana: ha cauda, e e")
        linhas.append("  ela que o usuario sente. Olhe o p99.")
    return "\n".join(linhas)


class ArcanePerfil:
    """O dicionário que `adopt Arcane.Perfil` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Perfil",

            # ── medir ──
            "medir": medir,
            "resumir": resumir,
            "relatorio": relatorio,

            # ── comparar ──
            "comparar": comparar,
            "mann_whitney": mann_whitney,

            # ── regressão ──
            "guardar": guardar,
            "conferir": conferir,

            # ── flame graph ──
            "perfilar": perfilar,
            "comecar_perfil": comecar_perfil,
            "terminar_perfil": terminar_perfil,
            "chama_texto": chama_texto,
            "chama_svg": chama_svg,

            # ── coletor ──
            "gc_pausas": gc_pausas,

            # ── contenção ──
            "trava": trava,
            "com_trava": com_trava,
            "estatisticas_da_trava": estatisticas_da_trava,
        }
