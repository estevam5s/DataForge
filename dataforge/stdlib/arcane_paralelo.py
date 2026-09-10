"""
Arcane.Concurrent — threads, processos e sincronizacao de verdade.

    adopt Arcane.Concurrent as P

    // um trabalhador por item, com teto
    resultados := P.map(baixar, urls, trabalhadores := 8)

    // travas de verdade
    trava := P.mutex()
    P.com_trava(trava, lambda => contador.somar())

    // processos, para trabalho de CPU
    somas := P.map_processos(calcular_pesado, blocos)

─── Thread ou processo? ────────────────────────────────────

A pergunta e sempre a mesma: o trabalho ESPERA ou CALCULA?

    espera (rede, disco, banco)  ->  thread
    calcula (numeros, imagem)    ->  processo

O motivo e o GIL: duas threads Python nunca executam bytecode ao mesmo
tempo. Para trabalho que espera, isso nao importa — a thread solta o
GIL enquanto espera, e dez downloads acontecem juntos. Para trabalho
que calcula, oito threads levam o mesmo tempo que uma; so processos
usam os oito nucleos.

'P.map' usa threads. 'P.map_processos' usa processos, e paga o custo
de serializar os dados — vale a partir de alguns milissegundos de
trabalho por item.

─── O que o 'thread' da linguagem nao resolvia ─────────────

A palavra 'thread' ja existia e dispara uma linha de execucao. O que
faltava era o resto: esperar por ela, coletar o que ela devolveu,
limitar quantas rodam juntas, e coordenar o acesso ao que elas
compartilham. Sem isso, duas threads escrevendo no mesmo vault perdem
atualizacoes — e o bug so aparece sob carga.
"""

import concurrent.futures as futuros
import pickle
import multiprocessing
import os
import queue
import threading
import time

from ..errors import (ConcurrencyError, DeadlockError, TimeoutError_,
                      ThreadError, TypeError_)


#: Quantos trabalhadores por padrao.
#:
#: Para espera, mais que nucleos compensa: a maior parte do tempo cada
#: um esta parado. Para calculo, mais que nucleos so acrescenta troca
#: de contexto.
PADRAO_THREADS = min(32, (os.cpu_count() or 4) * 4)
PADRAO_PROCESSOS = os.cpu_count() or 4


class Tarefa:
    """Uma linha de execucao com resultado.

    O 'thread' da linguagem dispara e esquece. Isto lembra: guarda o
    que a acao devolveu, guarda o erro se houve, e 'esperar()' entrega
    um ou levanta o outro.
    """

    __slots__ = ("_futuro", "nome", "_inicio")

    def __init__(self, futuro, nome=""):
        self._futuro = futuro
        self.nome = nome
        self._inicio = time.perf_counter()

    def esperar(self, prazo=None):
        """O resultado. Levanta aqui o erro que aconteceu la dentro.

        Sem isto, uma excecao numa thread some — ela morre no
        interpretador de threads e o programa segue como se tudo
        tivesse dado certo. E o modo mais silencioso de perder dado.
        """
        try:
            return self._futuro.result(timeout=prazo)
        except futuros.TimeoutError:
            raise TimeoutError_(
                f"the task {self.nome or ''} did not finish in {prazo}s.",
                dica="raise the deadline, or cancel it with 'cancelar'",
                doc="tecnicas/concorrencia") from None

    def pronta(self):
        return self._futuro.done()

    def cancelar(self):
        """Cancela — se ela ainda nao comecou.

        Uma thread que ja esta rodando nao pode ser interrompida de
        fora sem risco de deixar o estado pela metade. Python nao
        oferece isso, e fingir que oferece seria pior.
        """
        return self._futuro.cancel()

    def erro(self):
        """O erro, sem levanta-lo. None se deu certo ou ainda roda."""
        if not self._futuro.done():
            return None
        return self._futuro.exception()

    def duracao(self):
        return round(time.perf_counter() - self._inicio, 6)

    def __repr__(self):
        estado = "pronta" if self.pronta() else "rodando"
        return f"<tarefa {self.nome or '?'} {estado}>"


class Grupo:
    """Um conjunto de tarefas que se espera junto.

    A alternativa — guardar as tarefas num cluster e esperar uma a uma
    — funciona ate uma falhar: as outras continuam rodando, e o
    programa termina com threads soltas escrevendo em arquivos que
    ninguem mais le.
    """

    def __init__(self, trabalhadores=None, nome=""):
        self.nome = nome
        self._pool = futuros.ThreadPoolExecutor(
            max_workers=trabalhadores or PADRAO_THREADS,
            thread_name_prefix=nome or "df")
        self._tarefas = []

    def rodar(self, acao, *args):
        t = Tarefa(self._pool.submit(acao, *args), getattr(acao, "name", ""))
        self._tarefas.append(t)
        return t

    def esperar_todas(self, prazo=None):
        """Todos os resultados, na ordem em que foram disparadas.

        Se alguma falhou, o erro sobe — depois de esperar as outras.
        Subir na hora deixaria as demais rodando sem dono.
        """
        resultados, primeiro_erro = [], None
        for t in self._tarefas:
            try:
                resultados.append(t.esperar(prazo))
            except BaseException as e:              # noqa: BLE001
                resultados.append(None)
                if primeiro_erro is None:
                    primeiro_erro = e
        if primeiro_erro is not None:
            raise primeiro_erro
        return resultados

    def resultados(self):
        """O que deu certo e o que deu errado, sem levantar nada."""
        saida = []
        for t in self._tarefas:
            if not t.pronta():
                saida.append({"estado": "rodando", "valor": None, "erro": ""})
            elif t.erro() is not None:
                saida.append({"estado": "erro", "valor": None,
                              "erro": str(t.erro())})
            else:
                saida.append({"estado": "ok", "valor": t.esperar(),
                              "erro": ""})
        return saida

    def fechar(self, esperar=True):
        self._pool.shutdown(wait=esperar)
        return len(self._tarefas)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()
        return False


class Canal:
    """Uma fila entre threads, com espera de verdade.

    O 'channel' da linguagem devolve void na hora quando a fila esta
    vazia — o consumidor precisa girar num laco perguntando, o que
    queima CPU e ainda perde mensagem por corrida.

    Aqui 'receber' BLOQUEIA ate haver algo, com prazo opcional. E o
    que faz um produtor/consumidor funcionar sem laco de espera.
    """

    def __init__(self, capacidade=0):
        self._fila = queue.Queue(maxsize=capacidade if capacidade > 0 else 0)
        self._fechado = threading.Event()

    def enviar(self, valor, prazo=None):
        if self._fechado.is_set():
            raise ConcurrencyError(
                "this channel is closed.",
                dica="check with 'aberto()' before sending",
                doc="tecnicas/concorrencia")
        try:
            self._fila.put(valor, timeout=prazo)
            return True
        except queue.Full:
            raise TimeoutError_(
                f"the channel is full and did not free up in {prazo}s.",
                dica="raise the capacity, or consume faster",
                doc="tecnicas/concorrencia") from None

    def receber(self, prazo=None):
        """Espera ate chegar algo. Devolve void quando o canal fecha."""
        while True:
            try:
                return self._fila.get(timeout=prazo if prazo else 0.05)
            except queue.Empty:
                if self._fechado.is_set() and self._fila.empty():
                    return None
                if prazo is not None:
                    raise TimeoutError_(
                        f"nothing arrived in {prazo}s.",
                        dica="raise the deadline, or check whether the "
                             "producer is still running",
                        doc="tecnicas/concorrencia") from None

    def tentar_receber(self):
        """Sem esperar: devolve void se estiver vazio."""
        try:
            return self._fila.get_nowait()
        except queue.Empty:
            return None

    def fechar(self):
        """Fecha. Quem espera recebe void e sai do laco."""
        self._fechado.set()
        return True

    def aberto(self):
        return not self._fechado.is_set()

    def tamanho(self):
        return self._fila.qsize()

    def vazio(self):
        return self._fila.empty()

    def __iter__(self):
        """'cycle item in canal' consome ate o canal fechar."""
        while True:
            item = self.receber()
            if item is None and self._fechado.is_set():
                return
            if item is not None:
                yield item


class Contador:
    """Um numero que varias threads somam sem perder atualizacao.

    'x := x + 1' em duas threads perde uma das somas: as duas leem o
    mesmo valor antes de qualquer uma gravar. Com a trava, nao.
    """

    __slots__ = ("_valor", "_trava")

    def __init__(self, inicial=0):
        self._valor = inicial
        self._trava = threading.Lock()

    def somar(self, quanto=1):
        with self._trava:
            self._valor += quanto
            return self._valor

    def subtrair(self, quanto=1):
        return self.somar(-quanto)

    def valor(self):
        with self._trava:
            return self._valor

    def zerar(self):
        with self._trava:
            anterior, self._valor = self._valor, 0
            return anterior


class ArcaneConcurrent(dict):
    """Threads, processos, travas e canais."""

    def __new__(cls):
        return {
            # ── disparar ──
            "rodar": cls._rodar,
            "grupo": cls._grupo,
            "esperar": cls._esperar,
            "esperar_todas": cls._esperar_todas,
            "esperar_primeira": cls._esperar_primeira,

            # ── mapear ──
            "map": cls._map,
            "map_processos": cls._map_processos,
            "para_cada": cls._para_cada,
            "lotes": cls._lotes,

            # ── sincronizacao ──
            "mutex": cls._mutex,
            "com_trava": cls._com_trava,
            "semaforo": cls._semaforo,
            "evento": cls._evento,
            "barreira": cls._barreira,
            "condicao": cls._condicao,
            "contador": cls._contador,
            "trava_leitura_escrita": cls._rwlock,

            # ── canal ──
            "canal": cls._canal,

            # ── informacao ──
            "nucleos": lambda: os.cpu_count() or 1,
            "thread_atual": cls._thread_atual,
            "threads_vivas": lambda: threading.active_count(),
            "sou_principal": cls._sou_principal,

            # ── tempo ──
            "dormir": cls._dormir,
            "com_prazo": cls._com_prazo,
            "repetir_a_cada": cls._repetir_a_cada,
        }

    # ── disparar ────────────────────────────────────────────

    @staticmethod
    def _rodar(acao, *args):
        """Dispara numa thread e devolve a tarefa."""
        pool = futuros.ThreadPoolExecutor(max_workers=1)
        tarefa = Tarefa(pool.submit(acao, *args), getattr(acao, "name", ""))
        # O pool se desmonta quando a tarefa termina; sem isto, cada
        # 'rodar' deixaria uma thread ociosa viva ate o fim do programa.
        pool.shutdown(wait=False)
        return tarefa

    @staticmethod
    def _grupo(trabalhadores=None, nome=""):
        return Grupo(trabalhadores, nome)

    @staticmethod
    def _exigir_tarefa(valor, funcao, indice=None):
        """Recusa quem nao veio de 'rodar', com a mensagem certa.

        Passar a ACAO em vez da TAREFA e o engano natural: 'map' e
        'para_cada' recebem acoes, e estes recebem tarefas. Sem esta
        checagem o erro era "'DFAction' object has no attribute
        'esperar'" — o nome de uma classe interna do interpretador,
        que nao diz nada a quem escreve DataForge.
        """
        if isinstance(valor, Tarefa):
            return valor
        onde = "" if indice is None else f" (o item {indice} da lista)"
        if callable(valor):
            raise TypeError_(
                f"{funcao} espera uma tarefa, e recebeu uma acao{onde}.",
                nota="uma acao so vira tarefa depois de ser disparada",
                dica=("dispare antes:  t := Concurrent.rodar(acao)  e entao "
                      f"{funcao}(t)\n"
                      "para rodar a acao sobre varios itens de uma vez, use "
                      "'map' ou 'para_cada'"),
                doc="tecnicas/concorrencia")
        raise TypeError_(
            f"{funcao} espera uma tarefa, e recebeu {type(valor).__name__}{onde}.",
            dica="uma tarefa vem de 'rodar', de 'grupo.enviar' ou de 'lotes'",
            doc="tecnicas/concorrencia")

    @staticmethod
    def _esperar(tarefa, prazo=None):
        return ArcaneConcurrent._exigir_tarefa(tarefa, "esperar").esperar(prazo)

    @staticmethod
    def _esperar_todas(tarefas, prazo=None):
        return [ArcaneConcurrent._exigir_tarefa(t, "esperar_todas", i).esperar(prazo)
                for i, t in enumerate(tarefas)]

    @staticmethod
    def _esperar_primeira(tarefas, prazo=None):
        """O primeiro resultado que chegar; as outras seguem rodando."""
        pendentes = [
            ArcaneConcurrent._exigir_tarefa(t, "esperar_primeira", i)._futuro
            for i, t in enumerate(tarefas)]
        prontas, _ = futuros.wait(
            pendentes, timeout=prazo, return_when=futuros.FIRST_COMPLETED)
        if not prontas:
            raise TimeoutError_(
                f"none of the {len(tarefas)} tasks finished in {prazo}s.",
                doc="tecnicas/concorrencia")
        return next(iter(prontas)).result()

    # ── mapear ──────────────────────────────────────────────

    @staticmethod
    def _map(acao, itens, trabalhadores=None, prazo=None):
        """A acao sobre cada item, em paralelo, NA ORDEM da entrada.

        A ordem importa: um resultado fora de ordem obriga quem chama
        a reassociar item e resultado, e e ai que se erra.

        Use para trabalho que ESPERA — rede, disco, banco. Para
        trabalho que calcula, veja 'map_processos'.
        """
        lista = list(itens)
        if not lista:
            return []
        n = trabalhadores or min(PADRAO_THREADS, len(lista))
        with futuros.ThreadPoolExecutor(max_workers=n) as pool:
            return list(pool.map(acao, lista, timeout=prazo))

    @staticmethod
    def _map_processos(acao, itens, trabalhadores=None):
        """Igual, mas em PROCESSOS — para trabalho que calcula.

        Duas threads Python nunca executam bytecode ao mesmo tempo (o
        GIL). Para calculo, oito threads levam o mesmo tempo que uma;
        so processos usam os oito nucleos.

        O custo e serializar os dados de ida e volta: vale a partir de
        alguns milissegundos de trabalho por item.
        """
        lista = list(itens)
        if not lista:
            return []
        try:
            n = trabalhadores or min(PADRAO_PROCESSOS, len(lista))
            with futuros.ProcessPoolExecutor(max_workers=n) as pool:
                return list(pool.map(acao, lista))
        except (TypeError, AttributeError, OSError, pickle.PicklingError) as e:
            # 'PicklingError' nao deriva de TypeError. Ate o Python 3.13
            # a falha chegava aqui como TypeError, e a partir do 3.14 ela
            # vem tipada — sem esta linha, a mensagem crua do pickle
            # escapava para o usuario, falando de '_CallItem' e de
            # 'serializing tuple item', que nao existem em DataForge.
            raise ConcurrencyError(
                f"this action cannot cross into another process: {e}",
                nota="a process receives the data by copy, and a closure "
                     "over the local scope does not travel",
                dica=("declare the action at the top level of the file, "
                      "and pass everything it needs as arguments — or use "
                      "'map', which uses threads and shares memory"),
                doc="tecnicas/concorrencia") from None

    @staticmethod
    def _para_cada(acao, itens, trabalhadores=None):
        """Como 'map', mas descarta o resultado — e nao levanta no meio.

        Devolve quantas deram certo e quantas falharam. Para efeito
        colateral em lote — enviar e-mails, gravar arquivos — parar na
        primeira falha costuma ser pior que seguir e relatar.
        """
        lista = list(itens)
        if not lista:
            return {"ok": 0, "erros": []}
        n = trabalhadores or min(PADRAO_THREADS, len(lista))
        ok, erros = 0, []
        with futuros.ThreadPoolExecutor(max_workers=n) as pool:
            enviados = {pool.submit(acao, item): item for item in lista}
            for f in futuros.as_completed(enviados):
                if f.exception() is None:
                    ok += 1
                else:
                    erros.append({"item": enviados[f],
                                  "erro": str(f.exception())})
        return {"ok": ok, "erros": erros}

    @staticmethod
    def _lotes(acao, itens, tamanho=10, trabalhadores=None):
        """Processa em lotes: a acao recebe uma LISTA por vez.

        Para trabalho com custo fixo por chamada — uma consulta ao
        banco, uma chamada de API — mil itens em lotes de cem custam
        dez chamadas em vez de mil.
        """
        lista = list(itens)
        pedacos = [lista[i:i + tamanho]
                   for i in range(0, len(lista), max(1, tamanho))]
        return ArcaneConcurrent._map(acao, pedacos, trabalhadores)

    # ── sincronizacao ───────────────────────────────────────

    @staticmethod
    def _mutex():
        """Uma trava: so uma thread por vez passa.

        Reentrante de proposito. A nao reentrante trava o programa
        quando uma acao com trava chama outra com a MESMA trava — e
        isso acontece por engano com facilidade.
        """
        return threading.RLock()

    @staticmethod
    def _com_trava(trava, acao):
        """Roda a acao com a trava tomada, e a solta mesmo com erro.

        Tomar e soltar a mao funciona ate o corpo estourar: ai a trava
        fica tomada para sempre, e a proxima thread espera eternamente.
        """
        with trava:
            return acao()

    @staticmethod
    def _semaforo(quantos=1):
        """Deixa passar N ao mesmo tempo, e nao uma.

        E o que limita concorrencia contra um recurso externo: cinco
        conexoes simultaneas ao banco, tres chamadas por vez a uma API
        com limite.
        """
        return threading.Semaphore(max(1, quantos))

    @staticmethod
    def _evento():
        """Um sinal de 'pode ir', que varias threads esperam."""
        return threading.Event()

    @staticmethod
    def _barreira(quantas):
        """Segura todas ate a ultima chegar, e ai libera juntas."""
        return threading.Barrier(max(1, quantas))

    @staticmethod
    def _condicao():
        """Espera ate uma condicao mudar, sem girar perguntando."""
        return threading.Condition()

    @staticmethod
    def _contador(inicial=0):
        return Contador(inicial)

    @staticmethod
    def _rwlock():
        """Muitos leem juntos; quem escreve espera todos sairem.

        Para dado lido com frequencia e escrito raramente — um cache,
        uma configuracao — um mutex comum serializa leituras que
        poderiam acontecer juntas.
        """
        return _TravaLeituraEscrita()

    # ── canal ───────────────────────────────────────────────

    @staticmethod
    def _canal(capacidade=0):
        """Uma fila entre threads. 'receber' ESPERA ate chegar algo.

        Com capacidade, o produtor tambem espera quando ela enche — e
        e assim que se evita um produtor rapido estourar a memoria
        contra um consumidor lento.
        """
        return Canal(capacidade)

    # ── informacao ──────────────────────────────────────────

    @staticmethod
    def _thread_atual():
        t = threading.current_thread()
        return {"nome": t.name, "id": t.ident, "principal": t is threading.main_thread()}

    @staticmethod
    def _sou_principal():
        return threading.current_thread() is threading.main_thread()

    # ── tempo ───────────────────────────────────────────────

    @staticmethod
    def _dormir(segundos):
        time.sleep(max(0.0, float(segundos)))
        return True

    @staticmethod
    def _com_prazo(acao, segundos):
        """Roda com prazo. Estoura TimeoutError se passar.

        A acao NAO e interrompida — Python nao permite matar uma
        thread de fora sem risco de deixar estado pela metade. Ela
        segue rodando em segundo plano; o que o prazo garante e que
        QUEM CHAMOU nao fica preso.
        """
        pool = futuros.ThreadPoolExecutor(max_workers=1)
        try:
            f = pool.submit(acao)
            return f.result(timeout=segundos)
        except futuros.TimeoutError:
            raise TimeoutError_(
                f"it did not finish in {segundos}s.",
                nota="the action keeps running in the background: Python "
                     "cannot kill a thread from outside safely",
                dica="raise the deadline, or make the action check a flag",
                doc="tecnicas/concorrencia") from None
        finally:
            pool.shutdown(wait=False)

    @staticmethod
    def _repetir_a_cada(acao, segundos, vezes=0):
        """Roda a cada N segundos, numa thread. Devolve como parar.

        O intervalo conta a partir do FIM da execucao anterior: se a
        acao demora mais que o intervalo, as execucoes nao se
        empilham.
        """
        parar = threading.Event()
        contagem = {"n": 0}

        def laco():
            while not parar.is_set():
                if vezes and contagem["n"] >= vezes:
                    return
                try:
                    acao()
                except BaseException:               # noqa: BLE001
                    pass
                contagem["n"] += 1
                parar.wait(segundos)

        t = threading.Thread(target=laco, daemon=True, name="repeticao")
        t.start()
        return {"parar": lambda: (parar.set(), True)[1],
                "vezes": lambda: contagem["n"],
                "viva": lambda: t.is_alive()}


class _TravaLeituraEscrita:
    """Muitos leitores, um escritor.

    O escritor espera os leitores sairem. Leitores que chegam depois
    de um escritor pedir a trava entram na fila atras dele — sem isso,
    um fluxo constante de leitura deixaria o escritor esperando para
    sempre.
    """

    def __init__(self):
        self._trava = threading.Condition()
        self._leitores = 0
        self._escritor = False
        self._escritores_esperando = 0

    def ler(self, acao):
        with self._trava:
            while self._escritor or self._escritores_esperando > 0:
                self._trava.wait()
            self._leitores += 1
        try:
            return acao()
        finally:
            with self._trava:
                self._leitores -= 1
                if self._leitores == 0:
                    self._trava.notify_all()

    def escrever(self, acao):
        with self._trava:
            self._escritores_esperando += 1
            while self._escritor or self._leitores > 0:
                self._trava.wait()
            self._escritores_esperando -= 1
            self._escritor = True
        try:
            return acao()
        finally:
            with self._trava:
                self._escritor = False
                self._trava.notify_all()
