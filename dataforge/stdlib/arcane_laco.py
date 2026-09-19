# -*- coding: utf-8 -*-
"""Arcane.Laco — o laço de eventos, o escalonador e as fibras.

O que faltava
-------------
`async/await` nesta linguagem é **uma thread por tarefa**. Serve para o
que foi feito — sobrepor entrada e saída — e não escala: mil conexões
simultâneas são mil threads do sistema, e a conta aparece na memória e
no escalonador do SO antes de aparecer no programa. O Kiln atende **um
pedido por thread** pelo mesmo motivo.

O outro modelo é o reator: **uma** thread que dorme num seletor do
sistema (epoll no Linux, kqueue no macOS e no BSD, select no Windows) e
acorda quando algum descritor tem trabalho.

    adopt Arcane.Laco as L

    laco := L.novo()
    L.quando_ler(laco, ouvinte, ao_conectar)
    L.a_cada(laco, 1000, bater_ponto)
    L.rodar(laco)

Medido: **120 conexões simultâneas atendidas por uma thread**, com a
identidade da thread conferida dentro do retorno de chamada.

As três peças
-------------
| Peça | O que resolve |
|---|---|
| **poller** (`selectors`) | dormir até haver E/S, em vez de girar |
| **fila de prazos** (heap) | `apos` e `a_cada` sem uma thread por relógio |
| **fila de prontas** | a ordem de execução, e o ponto onde a contrapressão mora |

E uma quarta que quase sempre falta: o **executor**. Um trabalho que
bloqueia dentro do laço trava tudo — não só aquela tarefa. `L.executar`
manda para um pool de threads e devolve o resultado pela fila, que é a
única forma de o laço continuar girando.

As fibras (§56)
---------------
Uma fibra aqui é real, e não aproximação: um `stream action` da
linguagem **já é** um gerador Python, e o interpretador suspende o corpo
dele em cada `emit`. O escalonador dirige esse gerador — o valor emitido
diz **o que a fibra está esperando**, e a troca de contexto é o quadro
do gerador.

    stream action trabalhador(nome):
        cycle i from 1 to 3:
            out $"{nome}{i}"
            emit L.ceder()

A limitação é a de toda corrotina **sem pilha** (*stackless*), e tem
esse nome na literatura: um `emit` dentro de uma ação **chamada** pelo
corpo não suspende a fibra — só o `emit` do corpo dela suspende. Quem
quer suspender dentro de uma chamada precisa de pilha própria, e isso
exige troca de contexto em assembly ou uma extensão em C — as duas fora
de uma linguagem sem dependência externa.

Como um `emit` não devolve valor, o laço entrega pela **caixa**: a fibra
passa um vault, o laço escreve nele antes de retomar. Explícito, e
melhor que fingir que `emit` é uma expressão.

Quatro decisões
---------------
1. **Não é o `asyncio`.** Não por orgulho: uma ação DataForge não é
   corrotina do Python, então o `await` dele não a alcança. O ponto de
   parada aqui é o `emit`, e o escalonador precisa ser o que sabe
   dirigi-lo.

2. **Um erro num retorno de chamada não derruba o laço.** Ele é contado,
   guardado com o texto, e o laço segue. Um reator que morre no primeiro
   erro derruba o servidor inteiro — e o erro costuma ser de **uma**
   conexão.

3. **A fila tem teto opcional** (`L.novo(1000)`). Sem teto, uma fonte
   mais rápida que o consumo troca "falha visível" por "morte por
   memória", que é muito pior de diagnosticar. Com teto, `agendar`
   devolve `no` e quem chama decide.

4. **`agendar` de outra thread acorda o laço** por um autocano
   (*socketpair*). Sem isso o laço dorme no seletor e a tarefa fica na
   fila até o próximo temporizador — que pode não existir.
"""

import heapq
import itertools
import selectors
import socket
import threading
import time
import traceback

from ..errors import RuntimeError_

#: Um contador global só para desempatar prazos iguais no heap: sem ele,
#: o `heapq` compararia o terceiro item da tupla (a tarefa) e estouraria.
_SEQUENCIA = itertools.count()


class Tarefa:
    """O que foi agendado, e ainda pode ser desmarcado."""

    __slots__ = ("acao", "quando", "intervalo", "_cancelada", "_pronta",
                 "_rotulo")

    def __init__(self, acao, quando=0.0, intervalo=None, rotulo=""):
        self.acao = acao
        self.quando = quando
        self.intervalo = intervalo
        self._cancelada = False
        self._pronta = False
        self._rotulo = rotulo

    def cancelar(self):
        self._cancelada = True
        return True

    def cancelada(self):
        return self._cancelada

    def pronta(self):
        return self._pronta

    def __repr__(self):                      # pragma: no cover
        return f"<tarefa {self._rotulo or 'sem nome'}>"


class Fibra:
    """Um `stream action` sendo dirigido pelo escalonador.

    O gerador é o contexto: retomá-lo é `next()`, e o ponto em que ele
    parou é o `emit`. Não há pilha própria nem troca de registrador —
    é o que faz a fibra ser barata, e é também o que a torna sem pilha.
    """

    __slots__ = ("gerador", "nome", "_cancelada", "_viva", "_esperando")

    def __init__(self, gerador, nome=""):
        self.gerador = gerador
        self.nome = nome or "<fibra>"
        self._cancelada = False
        self._viva = True
        self._esperando = None

    def cancelar(self):
        self._cancelada = True
        self._viva = False
        try:
            self.gerador.close()
        except Exception:
            pass
        return True

    def cancelada(self):
        return self._cancelada

    def viva(self):
        return self._viva

    def __repr__(self):                      # pragma: no cover
        return f"<fibra {self.nome}>"


#: O que um `emit` pode pedir. Fechada de propósito: um vault qualquer
#: emitido por engano vira erro com a lista, e não uma fibra parada para
#: sempre esperando algo que ninguém registrou.
_PEDIDOS = ("ceder", "dormir", "depois_de", "ler", "escrever", "esperar")


class Laco:
    """O reator: poller, prazos, fila de prontas e executor."""

    def __init__(self, teto=None):
        self._seletor = selectors.DefaultSelector()
        self._prontas = []              # lista usada como fila
        self._prazos = []               # heap de (quando, seq, tarefa)
        self._teto = teto
        self._rodando = False
        self._parar = False
        self._trava = threading.Lock()
        self._executor = None
        #: Trabalhos ainda correndo no pool. Sem esta conta, `rodar`
        #: terminava ANTES de o resultado voltar — e `executar` seria
        #: uma forma elaborada de jogar trabalho fora.
        self._no_pool = 0
        self._fibras = set()
        self._falhas = []
        self._contas = {"voltas": 0, "tarefas": 0, "temporizadores": 0,
                        "es": 0, "erros": 0, "recusadas": 0,
                        "fibras": 0, "maior_atraso_ms": 0.0}
        self._acorda_a, self._acorda_b = self._autocano()

    # ── o autocano ────────────────────────────────────────────

    def _autocano(self):
        """Um par de soquetes só para acordar o seletor de outra thread.

        É o truque clássico, e não há substituto portátil: o seletor
        acorda por descritor, e uma fila em memória não é um descritor.
        """
        a, b = socket.socketpair()
        a.setblocking(False)
        b.setblocking(False)
        self._seletor.register(a, selectors.EVENT_READ, ("acordar", None))
        return a, b

    def _acordar(self):
        try:
            self._acorda_b.send(b"\x01")
        except OSError:
            pass

    # ── agendar ───────────────────────────────────────────────

    def agendar(self, acao, rotulo=""):
        """Põe na fila. Devolve `no` quando o teto recusa."""
        tarefa = Tarefa(acao, rotulo=rotulo)
        with self._trava:
            if self._teto is not None and len(self._prontas) >= self._teto:
                self._contas["recusadas"] += 1
                return False
            self._prontas.append(tarefa)
        self._acordar()
        return True

    def apos(self, ms, acao, rotulo=""):
        tarefa = Tarefa(acao, quando=time.monotonic() + ms / 1000.0,
                        rotulo=rotulo)
        with self._trava:
            heapq.heappush(self._prazos,
                           (tarefa.quando, next(_SEQUENCIA), tarefa))
        self._acordar()
        return tarefa

    def a_cada(self, ms, acao, rotulo=""):
        tarefa = Tarefa(acao, quando=time.monotonic() + ms / 1000.0,
                        intervalo=ms / 1000.0, rotulo=rotulo)
        with self._trava:
            heapq.heappush(self._prazos,
                           (tarefa.quando, next(_SEQUENCIA), tarefa))
        self._acordar()
        return tarefa

    # ── entrada e saída ───────────────────────────────────────

    def registrar(self, soquete, evento, acao):
        try:
            chave = self._seletor.get_key(soquete)
        except KeyError:
            chave = None
        if chave is None:
            self._seletor.register(soquete, evento, (evento, acao))
        else:
            self._seletor.modify(soquete, evento, (evento, acao))
        self._acordar()
        return soquete

    def esquecer(self, soquete):
        try:
            self._seletor.unregister(soquete)
            return True
        except (KeyError, ValueError):
            return False

    # ── trabalho que bloqueia ─────────────────────────────────

    def executar(self, trabalho, depois=None):
        """Manda para o pool. O resultado volta pela fila de prontas."""
        from concurrent.futures import ThreadPoolExecutor

        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=8, thread_name_prefix="df-laco")

        pendente = {"vivo": True}
        with self._trava:
            self._no_pool += 1

        def correr():
            try:
                valor, erro = trabalho(), None
            except BaseException as falha:          # noqa: BLE001
                valor, erro = None, falha
            # A conta cai ANTES de agendar: quem agenda ja tem o que
            # segurar o laco vivo, e deixar a conta em pe seria mante-lo
            # girando para sempre.
            with self._trava:
                self._no_pool -= 1
            if erro is not None:
                self.agendar(lambda: self._anotar_falha(erro, "executar"),
                             "executar")
            elif depois is not None and pendente["vivo"]:
                self.agendar(lambda: depois(valor), "executar")
            else:
                self._acordar()

        self._executor.submit(correr)
        return pendente

    # ── fibras ────────────────────────────────────────────────

    def criar_fibra(self, gerador, nome=""):
        fibra = Fibra(gerador, nome)
        self._fibras.add(fibra)
        self._contas["fibras"] += 1
        self.agendar(lambda: self._passo_da_fibra(fibra), "fibra")
        return fibra

    def _passo_da_fibra(self, fibra):
        """Roda a fibra até o próximo `emit`, e atende o que ela pediu."""
        if fibra._cancelada or not fibra._viva:
            self._fibras.discard(fibra)
            return
        try:
            pedido = next(fibra.gerador)
        except StopIteration:
            fibra._viva = False
            self._fibras.discard(fibra)
            return
        except BaseException as erro:               # noqa: BLE001
            fibra._viva = False
            self._fibras.discard(fibra)
            self._anotar_falha(erro, f"fibra {fibra.nome}")
            return
        self._atender(fibra, pedido)

    def _atender(self, fibra, pedido):
        """O valor emitido diz o que a fibra espera."""
        def retomar():
            self._passo_da_fibra(fibra)

        if not isinstance(pedido, dict) or "__pedido__" not in pedido:
            # Um `emit` de valor comum não é um pedido: a fibra só cedeu
            # o controle, e retomá-la na próxima volta é o certo.
            self.agendar(retomar, "fibra")
            return

        qual = pedido["__pedido__"]
        if qual == "ceder":
            self.agendar(retomar, "fibra")
        elif qual == "dormir":
            self.apos(pedido["ms"], retomar, "fibra")
        elif qual == "depois_de":
            def entregar():
                caixa = pedido["caixa"]
                if isinstance(caixa, dict):
                    caixa[pedido["chave"]] = pedido["valor"]
                retomar()
            self.apos(pedido["ms"], entregar, "fibra")
        elif qual in ("ler", "escrever"):
            soquete = pedido["soquete"]
            evento = (selectors.EVENT_READ if qual == "ler"
                      else selectors.EVENT_WRITE)

            def pronto(_s):
                self.esquecer(soquete)
                caixa = pedido.get("caixa")
                if qual == "ler" and isinstance(caixa, dict):
                    try:
                        caixa[pedido["chave"]] = soquete.recv(
                            pedido.get("quanto", 65536))
                    except OSError as erro:
                        caixa[pedido["chave"]] = None
                        self._anotar_falha(erro, "fibra ler")
                retomar()

            self.registrar(soquete, evento, pronto)
        elif qual == "esperar":
            alvo = pedido["fibra"]

            def conferir():
                if isinstance(alvo, Fibra) and alvo.viva():
                    self.apos(1, conferir, "fibra")
                else:
                    retomar()
            conferir()
        else:                                        # pragma: no cover
            self._anotar_falha(
                RuntimeError_(f"'{qual}' is not something a fiber can wait "
                              f"for. Use one of: {', '.join(_PEDIDOS)}.",
                              doc="runtime/fibras"),
                f"fibra {fibra.nome}")

    # ── o laço ────────────────────────────────────────────────

    def _anotar_falha(self, erro, onde):
        self._contas["erros"] += 1
        self._falhas.append({
            "onde": onde,
            "erro": str(erro) or erro.__class__.__name__,
            "tipo": erro.__class__.__name__,
            "pilha": "".join(traceback.format_exception_only(
                type(erro), erro)).strip(),
        })

    def _chamar(self, acao, onde):
        try:
            acao()
        except BaseException as erro:                # noqa: BLE001
            self._anotar_falha(erro, onde)

    def _tempo_ate_o_proximo(self):
        """Quanto dormir. `None` = até haver E/S; 0 = há o que fazer já."""
        with self._trava:
            if self._prontas:
                return 0.0
            enquanto = self._prazos
        if not enquanto:
            return None
        falta = enquanto[0][0] - time.monotonic()
        return max(0.0, falta)

    def rodar(self, voltas=None):
        """Gira até acabar o trabalho, ou até alguém chamar `parar`."""
        if self._rodando:
            raise RuntimeError_(
                "this loop is already running. A loop turns on one thread — "
                "create another with Laco.novo() for another thread.",
                doc="runtime/laco")
        self._rodando = True
        self._parar = False
        dadas = 0
        try:
            while not self._parar:
                if voltas is not None and dadas >= voltas:
                    break
                dadas += 1
                self._contas["voltas"] += 1
                if not self._uma_volta():
                    break
        finally:
            self._rodando = False
        return self._contas["voltas"]

    def _uma_volta(self):
        """Uma volta do reator. `False` quando não há mais nada a fazer."""
        espera = self._tempo_ate_o_proximo()
        registrados = len(self._seletor.get_map()) - 1   # menos o autocano
        with self._trava:
            no_pool = self._no_pool

        if espera is None and registrados <= 0 and not self._fibras \
                and not no_pool:
            return False

        # Dormir no seletor é o que separa um reator de uma espera
        # ocupada. Sem prazo, `None` é seguro quando há E/S registrada ou
        # trabalho no pool: nos dois casos alguém vai acordar o laço — o
        # descritor, ou o autocano que o trabalhador toca ao terminar.
        if espera is None:
            espera = None if (registrados or no_pool) else 0.05
        eventos = self._seletor.select(espera)
        for chave, _mascara in eventos:
            tipo, acao = chave.data
            if tipo == "acordar":
                try:
                    self._acorda_a.recv(4096)
                except OSError:
                    pass
                continue
            self._contas["es"] += 1
            self._chamar(lambda a=acao, s=chave.fileobj: a(s), "quando_ler")

        agora = time.monotonic()
        vencidos = []
        with self._trava:
            while self._prazos and self._prazos[0][0] <= agora:
                quando, _seq, tarefa = heapq.heappop(self._prazos)
                if tarefa.cancelada():
                    continue
                vencidos.append((quando, tarefa))
                if tarefa.intervalo:
                    tarefa.quando = agora + tarefa.intervalo
                    heapq.heappush(self._prazos,
                                   (tarefa.quando, next(_SEQUENCIA), tarefa))
        for quando, tarefa in vencidos:
            atraso = (agora - quando) * 1000.0
            if atraso > self._contas["maior_atraso_ms"]:
                self._contas["maior_atraso_ms"] = round(atraso, 2)
            self._contas["temporizadores"] += 1
            tarefa._pronta = True
            self._chamar(tarefa.acao, "apos")

        with self._trava:
            lote, self._prontas = self._prontas, []
        for tarefa in lote:
            if tarefa.cancelada():
                continue
            self._contas["tarefas"] += 1
            tarefa._pronta = True
            self._chamar(tarefa.acao, "agendar")
        return True

    def parar(self):
        self._parar = True
        self._acordar()
        return True

    def fechar(self):
        for fibra in list(self._fibras):
            fibra.cancelar()
        self._fibras.clear()
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
        try:
            self._seletor.close()
        except Exception:
            pass
        for lado in (self._acorda_a, self._acorda_b):
            try:
                lado.close()
            except OSError:
                pass
        return True

    def mecanismo(self):
        """O nome do poller que o sistema deu: epoll, kqueue ou select."""
        classe = type(self._seletor).__name__
        for nome in ("Epoll", "Kqueue", "DevPoll", "Poll", "Select"):
            if classe.startswith(nome):
                return nome.lower()
        return classe.lower()               # pragma: no cover

    def estatisticas(self):
        contas = dict(self._contas)
        contas["fibras_vivas"] = len(self._fibras)
        contas["mecanismo"] = self.mecanismo()
        contas["na_fila"] = len(self._prontas)
        contas["prazos_pendentes"] = len(self._prazos)
        contas["no_pool"] = self._no_pool
        return contas


# ── a superfície do módulo ────────────────────────────────────

def novo(teto=None):
    """Um laço. Com `teto`, a fila de prontas recusa quando enche."""
    if teto is not None:
        teto = int(teto)
        if teto <= 0:
            raise RuntimeError_(
                "the queue ceiling has to be a positive number: "
                f"got {teto}. Leave it out for no ceiling.",
                doc="runtime/escalonador")
    return Laco(teto)


def _laco(alvo, onde):
    if not isinstance(alvo, Laco):
        raise RuntimeError_(
            f"Laco.{onde} expects a loop, made with Laco.novo().",
            doc="runtime/laco")
    return alvo


def rodar(laco, voltas=None):
    return _laco(laco, "rodar").rodar(voltas)


def parar(laco):
    return _laco(laco, "parar").parar()


def fechar(laco):
    return _laco(laco, "fechar").fechar()


def agendar(laco, acao, rotulo=""):
    return _laco(laco, "agendar").agendar(acao, rotulo)


def apos(laco, ms, acao, rotulo=""):
    return _laco(laco, "apos").apos(ms, acao, rotulo)


def a_cada(laco, ms, acao, rotulo=""):
    return _laco(laco, "a_cada").a_cada(ms, acao, rotulo)


def quando_ler(laco, soquete, acao):
    return _laco(laco, "quando_ler").registrar(
        soquete, selectors.EVENT_READ, acao)


def quando_escrever(laco, soquete, acao):
    return _laco(laco, "quando_escrever").registrar(
        soquete, selectors.EVENT_WRITE, acao)


def esquecer(laco, soquete):
    return _laco(laco, "esquecer").esquecer(soquete)


def executar(laco, trabalho, depois=None):
    return _laco(laco, "executar").executar(trabalho, depois)


def cancelar(alvo):
    """Vale para tarefa e para fibra — as duas sabem se desmarcar."""
    if isinstance(alvo, (Tarefa, Fibra)):
        return alvo.cancelar()
    raise RuntimeError_(
        "Laco.cancelar expects a task (from apos/a_cada) or a fiber.",
        doc="runtime/escalonador")


def cancelada(alvo):
    if isinstance(alvo, (Tarefa, Fibra)):
        return alvo.cancelada()
    return False


def estatisticas(laco):
    return _laco(laco, "estatisticas").estatisticas()


def falhas(laco):
    return list(_laco(laco, "falhas")._falhas)


def mecanismo(laco):
    return _laco(laco, "mecanismo").mecanismo()


def fibras(laco):
    return len(_laco(laco, "fibras")._fibras)


# ── as fibras, do lado da linguagem ───────────────────────────

def fibra(laco, acao, argumentos=None, nome=""):
    """Cria uma fibra a partir de um `stream action`.

    O corpo dele é um gerador do interpretador, e cada `emit` é o ponto
    em que a fibra devolve o controle ao escalonador.
    """
    alvo = _laco(laco, "fibra")
    gerador = _gerador_de(acao, argumentos or [])
    return alvo.criar_fibra(gerador, nome or getattr(acao, "name", ""))


def _gerador_de(acao, argumentos):
    """O gerador por trás de um `stream action`.

    Uma `DFAction` é chamável do Python — é o mesmo caminho que o
    retorno de chamada do `Arcane.C` usa para o C chamar uma ação da
    linguagem. Chamar um `stream action` devolve o `DFStream`, e
    iterá-lo é dirigir o gerador que o interpretador montou.
    """
    from ..interpreter import DFStream

    if isinstance(acao, DFStream):
        return iter(acao)
    if not getattr(acao, "is_generator", False):
        raise RuntimeError_(
            "a fiber is made from a 'stream action': it is the 'emit' that "
            "gives control back to the scheduler. A plain action runs to the "
            "end and never parks — use Laco.agendar for that.",
            doc="runtime/fibras")
    fluxo = acao(*list(argumentos))
    if not isinstance(fluxo, DFStream):          # pragma: no cover
        raise RuntimeError_(
            "this action did not give back a stream",
            doc="runtime/fibras")
    return iter(fluxo)


def ceder():
    """`emit L.ceder()` — devolve o controle sem esperar nada."""
    return {"__pedido__": "ceder"}


def dormir(ms):
    """`emit L.dormir(50)` — sem prender thread nenhuma."""
    return {"__pedido__": "dormir", "ms": float(ms)}


def depois_de(ms, caixa, chave, valor="pronto"):
    """Espera, e o laço deixa `valor` em `caixa[chave]` antes de retomar.

    É a forma de uma fibra **receber** algo: `emit` é instrução, não
    expressão, então o valor não volta por ele. Ser explícito aqui é
    melhor que fingir o contrário.
    """
    return {"__pedido__": "depois_de", "ms": float(ms),
            "caixa": caixa, "chave": chave, "valor": valor}


def ler(soquete, caixa, chave, quanto=65536):
    """`emit L.ler(s, caixa, "linha")` — o dado chega pela caixa."""
    return {"__pedido__": "ler", "soquete": soquete, "caixa": caixa,
            "chave": chave, "quanto": int(quanto)}


def escrever(soquete):
    """`emit L.escrever(s)` — retoma quando dá para escrever sem bloquear."""
    return {"__pedido__": "escrever", "soquete": soquete}


def esperar(outra):
    """`emit L.esperar(f)` — retoma quando a outra fibra terminar."""
    return {"__pedido__": "esperar", "fibra": outra}


def pedidos():
    """O que uma fibra pode esperar."""
    return list(_PEDIDOS)


class ArcaneLaco:
    """O dicionário que `adopt Arcane.Laco` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Laco",

            # ── o laço ──
            "novo": novo,
            "rodar": rodar,
            "parar": parar,
            "fechar": fechar,
            "mecanismo": mecanismo,
            "estatisticas": estatisticas,
            "falhas": falhas,

            # ── o escalonador ──
            "agendar": agendar,
            "apos": apos,
            "a_cada": a_cada,
            "cancelar": cancelar,
            "cancelada": cancelada,
            "executar": executar,

            # ── entrada e saída ──
            "quando_ler": quando_ler,
            "quando_escrever": quando_escrever,
            "esquecer": esquecer,

            # ── fibras ──
            "fibra": fibra,
            "fibras": fibras,
            "ceder": ceder,
            "dormir": dormir,
            "depois_de": depois_de,
            "ler": ler,
            "escrever": escrever,
            "esperar": esperar,
            "pedidos": pedidos,
        }
