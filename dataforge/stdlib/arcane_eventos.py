# -*- coding: utf-8 -*-
"""Arcane.Eventos — publicar, assinar, e o contexto que atravessa.

O que faltava
-------------
Duas partes de um programa que precisam conversar sem se conhecer. O
Kiln tem `Sala` para WebSocket e o Lavra tem `Fonte` para assinatura —
os dois resolvem o mesmo problema para um transporte especifico, e nao
havia a peca geral.

Tres decisoes
-------------
1. **Um ouvinte que falha nao derruba os outros.** Ele e REMOVIDO e o
   erro vai para a lista — porque um ouvinte quebrado que continua
   inscrito quebra a cada evento, para sempre, e some no meio do log.

2. **`emitir` devolve quantos ouviram.** Zero e informacao: o evento
   com o nome errado nao falha, ele simplesmente nao chega — e essa e
   a falha mais dificil de achar num sistema de eventos.

3. **O contexto e por THREAD.** `Eventos.contexto` guarda o que
   atravessa uma operacao — o id do pedido, quem pediu — sem passar
   por parametro em cada camada. Um vault global serviria ate o
   segundo pedido simultaneo.
"""

import threading
import time


class ErroDeEventos(Exception):
    pass


class Emissor:
    """Quem publica, e quem ouve, sem se conhecerem."""

    def __init__(self, nome="emissor", teto=1000):
        self.nome = nome
        self.teto = teto
        self._ouvintes = {}
        self._uma_vez = {}
        self._trava = threading.RLock()
        self.emitidos = 0
        self.entregues = 0
        self.erros = []

    # ── assinar ──

    def ao(self, evento, acao):
        """Ouve sempre. Devolve a acao que cancela."""
        with self._trava:
            fila = self._ouvintes.setdefault(evento, [])
            if len(fila) >= self.teto:
                raise ErroDeEventos(
                    f"'{evento}' ja tem {self.teto} ouvintes.\n"
                    f"  Esse numero quase sempre significa um 'ao(...)' "
                    f"dentro de um laco ou de um handler — cada volta "
                    f"inscreve mais um, e nenhum sai.\n"
                    f"  Se sao muitos mesmo, suba o teto ao criar o "
                    f"emissor.")
            fila.append(acao)
        return lambda: self.remover(evento, acao)

    def uma_vez(self, evento, acao):
        """Ouve o proximo, e sai."""
        with self._trava:
            self._uma_vez.setdefault(evento, []).append(acao)
        return lambda: self.remover(evento, acao)

    def remover(self, evento, acao=None):
        with self._trava:
            if acao is None:
                self._ouvintes.pop(evento, None)
                self._uma_vez.pop(evento, None)
                return self
            for mapa in (self._ouvintes, self._uma_vez):
                if evento in mapa and acao in mapa[evento]:
                    mapa[evento].remove(acao)
        return self

    def limpar(self):
        with self._trava:
            self._ouvintes.clear()
            self._uma_vez.clear()
        return self

    # ── publicar ──

    def emitir(self, evento, *dados):
        """Avisa todo mundo. Devolve QUANTOS ouviram.

        Zero e informacao: um evento com o nome errado nao falha, ele
        simplesmente nao chega — e essa e a falha mais dificil de achar
        num sistema de eventos.
        """
        with self._trava:
            ouvintes = list(self._ouvintes.get(evento, ()))
            de_uma_vez = list(self._uma_vez.get(evento, ()))
            self._uma_vez.pop(evento, None)
            curingas = list(self._ouvintes.get("*", ()))

        self.emitidos += 1
        quantos = 0
        for acao in ouvintes + de_uma_vez:
            if self._chamar(acao, evento, dados, remover_se_falhar=True):
                quantos += 1
        for acao in curingas:
            self._chamar(acao, evento, (evento,) + dados)
        self.entregues += quantos
        return quantos

    def _chamar(self, acao, evento, dados, remover_se_falhar=False):
        try:
            _chamar_com_o_que_aceita(acao, dados)
            return True
        except Exception as erro:                    # noqa: BLE001
            # Um ouvinte quebrado que continua inscrito quebra a cada
            # evento, para sempre, e some no meio do log. Ele sai.
            self.erros.append({"evento": evento, "erro": str(erro),
                               "quando": time.time()})
            if remover_se_falhar:
                self.remover(evento, acao)
            return False

    # ── olhar ──

    def ouvintes(self, evento=None):
        with self._trava:
            if evento is None:
                return {e: len(l) for e, l in self._ouvintes.items() if l}
            return len(self._ouvintes.get(evento, ()))

    def eventos(self):
        with self._trava:
            return sorted(e for e, l in self._ouvintes.items() if l)

    def resumo(self):
        return {"emitidos": self.emitidos, "entregues": self.entregues,
                "ouvintes": self.ouvintes(), "erros": len(self.erros)}

    def __repr__(self):
        return f"<emissor '{self.nome}' {sum(self.ouvintes().values())} ouvintes>"


def _chamar_com_o_que_aceita(acao, dados):
    """Chama com quantos argumentos a acao aceitar.

    Um ouvinte que so quer saber que aconteceu nao devia precisar
    declarar os tres campos que o evento carrega.
    """
    params = getattr(acao, "params", None)
    if isinstance(params, (list, tuple)):
        return acao(*dados[:len(params)])
    import inspect
    try:
        assinatura = inspect.signature(acao)
    except (TypeError, ValueError):
        return acao(*dados)
    quantos = 0
    for p in assinatura.parameters.values():
        if p.kind is p.VAR_POSITIONAL:
            return acao(*dados)
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
            quantos += 1
    return acao(*dados[:quantos])


def emissor(nome="emissor", teto=1000):
    return Emissor(nome, teto)


# ══════════════════════════════════════════════════════════════
#  Contexto por thread
# ══════════════════════════════════════════════════════════════

_LOCAL = threading.local()


def _pilha():
    if not hasattr(_LOCAL, "pilha"):
        _LOCAL.pilha = []
    return _LOCAL.pilha


def com_contexto(dados, acao):
    """Roda a ação com esses valores no contexto, e os tira no fim.

    É por THREAD: um vault global serviria até o segundo pedido
    simultâneo, e aí o id de um apareceria no log do outro.
    """
    pilha = _pilha()
    base = dict(pilha[-1]) if pilha else {}
    base.update(dados or {})
    pilha.append(base)
    try:
        return acao()
    finally:
        pilha.pop()


def contexto():
    """O que está no contexto desta thread, agora."""
    pilha = _pilha()
    return dict(pilha[-1]) if pilha else {}


def por(chave, padrao=None):
    return contexto().get(chave, padrao)


def guardar(chave, valor):
    """Acrescenta ao contexto atual. Sem contexto aberto, não faz nada."""
    pilha = _pilha()
    if not pilha:
        return False
    pilha[-1][chave] = valor
    return True


# ══════════════════════════════════════════════════════════════
#  Fila de trabalho
# ══════════════════════════════════════════════════════════════

class Fila:
    """Trabalho que roda depois, em outra thread.

    A diferença para o emissor: o emissor entrega AGORA, na thread de
    quem emitiu. A fila aceita e devolve o controle — quem publicou não
    espera o trabalho terminar.
    """

    def __init__(self, trabalhador, operarios=2, nome="fila"):
        import queue
        self.nome = nome
        self._fila = queue.Queue()
        self.trabalhador = trabalhador
        self.feitos = 0
        self.falhos = 0
        self.erros = []
        self.rodando = True
        self._threads = [
            threading.Thread(target=self._laco, daemon=True)
            for _ in range(max(1, operarios))
        ]
        for t in self._threads:
            t.start()

    def _laco(self):
        import queue
        while self.rodando:
            try:
                item = self._fila.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                self.trabalhador(item)
                self.feitos += 1
            except Exception as erro:                # noqa: BLE001
                self.falhos += 1
                self.erros.append(str(erro))
            finally:
                self._fila.task_done()

    def publicar(self, item):
        self._fila.put(item)
        return self

    def esperar(self, prazo=None):
        """Espera a fila esvaziar. É o que um teste precisa."""
        if prazo is None:
            self._fila.join()
            return self
        fim = time.perf_counter() + prazo
        while not self._fila.empty() and time.perf_counter() < fim:
            time.sleep(0.01)
        return self

    def pendentes(self):
        return self._fila.qsize()

    def parar(self):
        self.rodando = False
        return self

    def resumo(self):
        return {"feitos": self.feitos, "falhos": self.falhos,
                "pendentes": self.pendentes(), "operarios": len(self._threads)}

    def __repr__(self):
        return f"<fila '{self.nome}' {self.pendentes()} pendentes>"


def fila(trabalhador, operarios=2, nome="fila"):
    return Fila(trabalhador, operarios, nome)


class ArcaneEventos:
    """O dicionário que `adopt Arcane.Eventos` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Eventos",

            "emissor": emissor,
            "Emissor": Emissor,

            "com_contexto": com_contexto,
            "contexto": contexto,
            "por": por,
            "guardar": guardar,

            "fila": fila,
            "Fila": Fila,
        }
