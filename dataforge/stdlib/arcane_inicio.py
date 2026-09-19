# -*- coding: utf-8 -*-
"""Arcane.Inicio — o que roda antes da primeira linha, e a pilha.

O que faltava
-------------
Um programa não começa na primeira linha. Antes dela o `comptime` rodou
numa caixa sem E/S, os `adopt` carregaram módulos, e as declarações de
topo foram içadas. Nada disso era **visível** — e "por que a partida
demora 400 ms?" não tinha como ser respondido sem cronometrar à mão.

    adopt Arcane.Inicio as I

    out I.relatorio()["mais_caro"]     // qual 'adopt' custou mais

Mais duas peças que faltavam de verdade:

**Armazenamento por thread** (§59). `threading.local` dá o armazém e não
dá o resto: não há inicialização declarada por thread nem **finalizador**
quando a thread acaba. Sem finalizador, uma conexão aberta por thread
fica aberta depois que ela morre — e o sintoma aparece no servidor, não
no código.

**A pilha** (§60). Ela tinha limite (mil quadros) e não tinha como ser
perguntada: nem a profundidade atual, nem quanto falta, nem os nomes dos
quadros. Uma travessia de árvore de cinco mil nós não tem nada de
infinita, e quem a escreve precisa saber de quanto é o teto antes de
bater nele.

Três decisões
-------------
1. **A cronometragem do `adopt` é sempre ligada.** São dois floats por
   import, num lugar que roda uma vez. Ligá-la por opção faria a medida
   existir só para quem já desconfiava — e a pergunta aparece quando
   alguém *não* desconfiava.

2. **O finalizador roda quando a thread é COLETADA**, não no instante em
   que ela termina. É o que `weakref.finalize` garante, e fingir
   precisão maior seria prometer um gancho que o Python não tem. Para
   liberar na hora exata, use [`Arcane.Posse`](/docs/memoria/posse).

3. **Baixar o limite da pilha vale de verdade**, e subi-lo é recusado
   além do que o Python aguenta: cada chamada da linguagem gasta vários
   quadros do CPython, e um teto alto demais troca uma mensagem clara
   por um `RecursionError` cru.
"""

import sys
import threading
import weakref

from ..errors import RuntimeError_

#: O caminho da partida, em ordem. É o que `fases()` devolve, e a
#: descrição é a documentação — há teste cobrando o tamanho dela.
FASES = (
    ("lexer", "o texto vira tokens, com linha e coluna em cada um"),
    ("parser", "os tokens viram a árvore; um erro de sintaxe para aqui"),
    ("comptime", "os blocos 'comptime' rodam numa caixa sem E/S, e o que "
                 "eles decidem vira constante antes de o programa existir"),
    ("hoisting", "as declarações de topo são içadas: uma ação pode ser "
                 "chamada antes da linha em que foi escrita"),
    ("adopt", "cada módulo é resolvido e carregado, na ordem do arquivo — "
              "é aqui que a partida costuma ser gasta"),
    ("programa", "a primeira instrução de topo finalmente roda"),
    ("defer", "os 'defer' de topo rodam no fim, na ordem inversa"),
)


def _interp():
    """O interpretador em execução — o mesmo caminho do `Arcane.Reflexo`."""
    from ..interpreter import DFAction

    interp = DFAction._interpreter
    if interp is None:                          # pragma: no cover
        raise RuntimeError_(
            "Inicio needs a running interpreter.", doc="partida/inicio")
    return interp


# ── a partida ─────────────────────────────────────────────────

def fases():
    """As fases da partida, em ordem, com o que cada uma faz."""
    return [{"ordem": i, "fase": nome, "o_que": texto}
            for i, (nome, texto) in enumerate(FASES)]


def adocoes():
    """Quanto cada `adopt` custou, na ordem em que aconteceram."""
    return [{"modulo": nome, "ms": round(ms, 4)}
            for nome, ms in _interp().boot_adocoes]


def relatorio():
    """O resumo da partida: quantos módulos, quanto tempo, e o pior."""
    registro = _interp().boot_adocoes
    total = sum(ms for _n, ms in registro)
    mais_caro = max(registro, key=lambda par: par[1]) if registro else None
    return {
        "adocoes": len(registro),
        "total_ms": round(total, 4),
        "mais_caro": ({"modulo": mais_caro[0], "ms": round(mais_caro[1], 4)}
                      if mais_caro else None),
        "fases": len(FASES),
    }


def texto_do_relatorio():
    """A partida escrita, do módulo mais caro para o mais barato."""
    registro = sorted(_interp().boot_adocoes, key=lambda p: -p[1])
    if not registro:
        return "  nenhum 'adopt' neste programa"
    total = sum(ms for _n, ms in registro)
    linhas = [f"  {len(registro)} modulo(s) carregado(s) em {total:.2f} ms",
              ""]
    for nome, ms in registro[:12]:
        fatia = 100.0 * ms / total if total else 0.0
        linhas.append(f"   {nome:<28} {ms:>8.3f} ms  {fatia:>5.1f}%")
    return "\n".join(linhas)


# ── armazenamento por thread (§59) ────────────────────────────

class Local:
    """Uma variável por thread, com nascimento e fim declarados.

    `threading.local` dá o armazém; o que falta nele é justamente o que
    torna a coisa utilizável num servidor: a inicialização declarada num
    lugar só, e o **finalizador** quando a thread acaba.
    """

    __slots__ = ("_inicial", "_ao_terminar", "_valores", "_trava",
                 "_finalizadores", "_nome")

    def __init__(self, inicial, ao_terminar=None, nome=""):
        if not callable(inicial):
            raise RuntimeError_(
                "Inicio.local needs an action that BUILDS the initial value, "
                "not the value itself: it runs once per thread, and a shared "
                "value would defeat the whole point.",
                doc="partida/por-thread")
        self._inicial = inicial
        self._ao_terminar = ao_terminar
        self._valores = {}
        self._finalizadores = {}
        self._trava = threading.Lock()
        self._nome = nome or "<local>"

    def meu(self):
        ident = threading.get_ident()
        with self._trava:
            if ident in self._valores:
                return self._valores[ident]
        # A inicialização roda FORA da trava: ela é código de quem
        # chamou, pode demorar, e segurar a trava ali faria uma thread
        # lenta parar todas as outras.
        valor = self._inicial()
        with self._trava:
            if ident not in self._valores:
                self._valores[ident] = valor
                self._marcar_fim(ident)
            return self._valores[ident]

    def _marcar_fim(self, ident):
        if self._ao_terminar is None:
            return
        atual = threading.current_thread()
        self._finalizadores[ident] = weakref.finalize(
            atual, self._acabou, ident)

    def _acabou(self, ident):
        with self._trava:
            valor = self._valores.pop(ident, None)
            self._finalizadores.pop(ident, None)
        if self._ao_terminar is not None and valor is not None:
            try:
                self._ao_terminar(valor)
            except Exception:
                # Um finalizador que levanta no desmonte de uma thread
                # não tem para onde subir — e derrubaria o coletor.
                pass

    def definir(self, valor):
        ident = threading.get_ident()
        with self._trava:
            novo = ident not in self._valores
            self._valores[ident] = valor
        if novo:
            self._marcar_fim(ident)
        return valor

    def limpar(self):
        ident = threading.get_ident()
        with self._trava:
            self._valores.pop(ident, None)
            fim = self._finalizadores.pop(ident, None)
        if fim is not None:
            fim.detach()
        return True

    def quantas(self):
        with self._trava:
            return len(self._valores)


def local(inicial, ao_terminar=None, nome=""):
    return Local(inicial, ao_terminar, nome)


def _de_local(alvo, onde):
    if not isinstance(alvo, Local):
        raise RuntimeError_(
            f"Inicio.{onde} expects a per-thread variable, made with "
            f"Inicio.local().", doc="partida/por-thread")
    return alvo


# ── a pilha (§60) ─────────────────────────────────────────────

def pilha():
    """Onde estamos, de quanto é o teto, e quanto falta."""
    interp = _interp()
    profundidade = interp._depth
    limite = interp.MAX_CALL_DEPTH
    return {
        "profundidade": profundidade,
        "limite": limite,
        "restante": limite - profundidade,
        "quadros": len(interp._call_stack),
    }


def quadros():
    """Os quadros abertos, do mais antigo ao mais novo."""
    saida = []
    for quadro in _interp()._call_stack:
        saida.append({
            "acao": getattr(quadro, "name", getattr(quadro, "acao", "?")),
            "linha": getattr(quadro, "line", getattr(quadro, "linha", 0)),
            "arquivo": getattr(quadro, "filename",
                               getattr(quadro, "arquivo", "")),
        })
    return saida


def limite_da_pilha(novo=None):
    """Lê o teto de quadros, ou o ajusta.

    Subir demais é **recusado**: cada chamada da linguagem gasta vários
    quadros do CPython, e um teto alto demais troca uma mensagem clara
    ("a recursão passou de mil quadros, e aqui estão as duas saídas")
    por um `RecursionError` cru do Python, que não fala desta linguagem.
    """
    interp = _interp()
    if novo is None:
        return interp.MAX_CALL_DEPTH

    novo = int(novo)
    if novo < 1:
        raise RuntimeError_(
            f"the frame ceiling has to be at least 1, got {novo}.",
            doc="partida/pilha")

    # Medido no interpretador: uma chamada da linguagem custa vários
    # quadros do Python. O quatro é folgado de propósito — errar para o
    # lado da mensagem clara.
    teto = sys.getrecursionlimit() // 4
    if novo > teto:
        raise RuntimeError_(
            f"{novo} frames is more than the Python recursion limit can "
            f"carry: each call of this language costs several CPython "
            f"frames, and the ceiling here is {teto}. Raise Python's limit "
            f"first, or use 'yield f(…)' as a whole return — a tail call "
            f"has no ceiling.",
            doc="partida/pilha")
    interp.MAX_CALL_DEPTH = novo
    return novo


class ArcaneInicio:
    """O dicionário que `adopt Arcane.Inicio` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Inicio",

            # ── a partida ──
            "fases": fases,
            "adocoes": adocoes,
            "relatorio": relatorio,
            "texto_do_relatorio": texto_do_relatorio,

            # ── por thread ──
            "local": local,
            "meu": lambda a: _de_local(a, "meu").meu(),
            "definir": lambda a, v: _de_local(a, "definir").definir(v),
            "limpar": lambda a: _de_local(a, "limpar").limpar(),
            "threads_com_valor": lambda a: _de_local(
                a, "threads_com_valor").quantas(),

            # ── a pilha ──
            "pilha": pilha,
            "quadros": quadros,
            "limite_da_pilha": limite_da_pilha,
        }
