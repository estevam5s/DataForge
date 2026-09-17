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

import json
import os
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


# ══════════════════════════════════════════════════════════════
#  Fila persistente
# ══════════════════════════════════════════════════════════════
#
# A 'Fila' acima vive na memoria: o processo que morre leva junto o que
# nao foi feito, e um deploy no meio do expediente perde os e-mails da
# manha. Esta guarda cada tarefa num SQLite — o 'sqlite3' da biblioteca
# padrao, que ja e o motor do Arcane.Database —, e o arquivo e o estado.
#
# Quatro decisoes:
#
# 1. **Reservar tem prazo.** Pegar uma tarefa grava 'reservada_ate'. Se o
#    processo morre sem terminar, nada limpa a reserva — ela vence, e a
#    tarefa volta a ficar disponivel. Um 'finally' nao serve: um processo
#    morto por 'kill -9' ou por falta de memoria nao roda 'finally'.
#    A contrapartida e honesta: a tarefa pode rodar DUAS vezes (a que
#    morreu pode ter terminado o efeito antes de morrer). Isso e o
#    "pelo menos uma vez" de toda fila de verdade, e por isso 'chave'
#    existe, e por isso o trabalhador deve ser idempotente.
#
# 2. **A reserva e atomica.** 'BEGIN IMMEDIATE' antes de escolher, e um
#    UPDATE que so vale se a tarefa ainda estiver livre. Dois operarios —
#    ou dois processos — no mesmo arquivo nunca pegam a mesma tarefa.
#
# 3. **A falha espera, e cada vez mais.** 'recuo * fator^(tentativa-1)',
#    com teto e com tremor. Sem o tremor, cem tarefas que falharam juntas
#    contra um servico fora do ar voltam juntas, e derrubam o servico de
#    novo no instante em que ele volta.
#
# 4. **A carta morta guarda o motivo.** Depois de 'tentativas' falhas a
#    tarefa nao some: fica com o ultimo erro e o historico de todos, para
#    ser analisada, reprocessada ou descartada. Uma fila que apaga o que
#    falhou transforma um bug em dado perdido.

_OPCOES_DA_FILA = {
    "operarios": 1,          # threads que processam; 0 = so 'processar()'
    "tentativas": 5,         # quantas falhas ate a carta morta
    "recuo": 1.0,            # segundos antes da 2a tentativa
    "fator": 2.0,            # multiplicador a cada falha
    "recuo_maximo": 300.0,   # o teto do recuo
    "tremor": 0.1,           # fracao aleatoria (+/-) sobre o recuo
    "reserva": 60.0,         # segundos ate uma tarefa reservada voltar
    "nome": "padrao",        # varias filas no mesmo arquivo
    "espera_vazia": 0.05,    # quanto um operario dorme sem trabalho
}


class FilaPersistente:
    """Tarefas num arquivo SQLite: sobrevivem ao processo."""

    def __init__(self, caminho, trabalhador=None, opcoes=None):
        import random
        from .opcoes import ler
        dadas = dict(opcoes or {})
        relogio = dadas.pop("_relogio", None)
        config = {**_OPCOES_DA_FILA, **ler(dadas, _OPCOES_DA_FILA,
                                           "Eventos.fila_persistente")}
        if int(config["tentativas"]) < 1:
            raise ErroDeEventos("a fila persistente precisa de 'tentativas' "
                                "de pelo menos 1")
        self.caminho = str(caminho)
        self.trabalhador = trabalhador
        self.config = config
        self.nome = str(config["nome"])
        self._relogio = relogio or time.time
        self._sorteio = random.Random()
        self._local = threading.local()
        self._conexoes = []
        self._trava_conexoes = threading.Lock()
        self.rodando = False
        self._threads = []
        self._criar_tabelas()
        if trabalhador is not None and int(config["operarios"]) > 0:
            self.iniciar()

    # ── o arquivo ──

    def _conexao(self):
        import sqlite3
        conexao = getattr(self._local, "conexao", None)
        if conexao is None:
            pasta = os.path.dirname(os.path.abspath(self.caminho))
            os.makedirs(pasta, exist_ok=True)
            # 'isolation_level=None': as transacoes sao explicitas, e o
            # 'BEGIN IMMEDIATE' da reserva precisa ser o primeiro comando.
            conexao = sqlite3.connect(self.caminho, timeout=30,
                                      isolation_level=None,
                                      check_same_thread=False)
            conexao.execute("PRAGMA journal_mode=WAL")
            conexao.execute("PRAGMA busy_timeout=30000")
            self._local.conexao = conexao
            with self._trava_conexoes:
                self._conexoes.append(conexao)
        return conexao

    def _criar_tabelas(self):
        c = self._conexao()
        c.execute("""CREATE TABLE IF NOT EXISTS df_tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fila TEXT NOT NULL,
            item TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendente',
            prioridade INTEGER NOT NULL DEFAULT 0,
            tentativas INTEGER NOT NULL DEFAULT 0,
            disponivel_em REAL NOT NULL,
            reservada_ate REAL,
            chave TEXT,
            erro TEXT,
            historico TEXT NOT NULL DEFAULT '[]',
            criada_em REAL NOT NULL,
            falhou_em REAL,
            UNIQUE (fila, chave))""")
        c.execute("""CREATE INDEX IF NOT EXISTS df_tarefas_proxima
                     ON df_tarefas (fila, estado, disponivel_em)""")
        c.execute("""CREATE TABLE IF NOT EXISTS df_filas (
            fila TEXT PRIMARY KEY,
            feitos INTEGER NOT NULL DEFAULT 0,
            falhas INTEGER NOT NULL DEFAULT 0)""")
        c.execute("INSERT OR IGNORE INTO df_filas (fila) VALUES (?)", (self.nome,))

    # ── publicar ──

    def publicar(self, item, opcoes=None):
        """Guarda a tarefa. Devolve o id — o mesmo, se a 'chave' ja existe."""
        from .opcoes import ler
        padroes = {"atraso": 0.0, "quando": None, "prioridade": 0, "chave": None}
        opcoes = {**padroes, **ler(dict(opcoes or {}), padroes,
                                   "fila_persistente.publicar")}
        texto = self._serializar(item)
        agora = self._relogio()
        quando = opcoes["quando"]
        disponivel = float(quando) if quando is not None \
            else agora + float(opcoes["atraso"] or 0)
        chave = opcoes["chave"]
        c = self._conexao()
        c.execute("BEGIN IMMEDIATE")
        try:
            if chave is not None:
                existente = c.execute(
                    "SELECT id FROM df_tarefas WHERE fila = ? AND chave = ?",
                    (self.nome, str(chave))).fetchone()
                if existente:
                    c.execute("COMMIT")
                    return existente[0]
            cursor = c.execute(
                """INSERT INTO df_tarefas (fila, item, prioridade,
                   disponivel_em, chave, criada_em) VALUES (?, ?, ?, ?, ?, ?)""",
                (self.nome, texto, int(opcoes["prioridade"] or 0), disponivel,
                 None if chave is None else str(chave), agora))
            c.execute("COMMIT")
            return cursor.lastrowid
        except BaseException:
            c.execute("ROLLBACK")
            raise

    def agendar(self, item, quando, opcoes=None):
        """Publica para uma hora marcada (segundos desde a epoca)."""
        return self.publicar(item, {**dict(opcoes or {}), "quando": quando})

    def _serializar(self, item):
        try:
            return json.dumps(item, ensure_ascii=False)
        except (TypeError, ValueError):
            from ..errors import SerializationError
            from ..builtins import _df_type
            raise SerializationError(
                f"A fila persistente guarda a tarefa em disco, e "
                f"{_df_type(item)} nao pode ser gravado.",
                dica="publique um vault, um cluster, texto ou numero — para "
                     "um objeto, Objetos.para_vault(obj)",
                doc="biblioteca/eventos") from None

    # ── processar ──

    def recuo_de(self, tentativa):
        """Os segundos de espera depois da falha numero 'tentativa'."""
        c = self.config
        base = min(float(c["recuo_maximo"]),
                   float(c["recuo"]) * float(c["fator"]) ** (int(tentativa) - 1))
        tremor = float(c["tremor"])
        if tremor:
            base *= 1 + self._sorteio.uniform(-tremor, tremor)
        return max(0.0, base)

    def _reservar(self):
        """Pega a proxima tarefa disponivel, atomicamente. None se nao ha."""
        agora = self._relogio()
        c = self._conexao()
        c.execute("BEGIN IMMEDIATE")
        try:
            linha = c.execute(
                """SELECT id, item, tentativas, historico FROM df_tarefas
                   WHERE fila = ? AND (
                       (estado = 'pendente' AND disponivel_em <= ?)
                    OR (estado = 'andamento' AND reservada_ate <= ?))
                   ORDER BY prioridade DESC, disponivel_em, id LIMIT 1""",
                (self.nome, agora, agora)).fetchone()
            if linha is None:
                c.execute("COMMIT")
                return None
            ident, texto, tentativas, historico = linha
            c.execute(
                """UPDATE df_tarefas SET estado = 'andamento',
                   reservada_ate = ?, tentativas = tentativas + 1
                   WHERE id = ?""",
                (agora + float(self.config["reserva"]), ident))
            c.execute("COMMIT")
        except BaseException:
            c.execute("ROLLBACK")
            raise
        return {"id": ident, "item": json.loads(texto),
                "tentativa": tentativas + 1, "historico": json.loads(historico)}

    def _concluir(self, tarefa):
        c = self._conexao()
        c.execute("BEGIN IMMEDIATE")
        c.execute("DELETE FROM df_tarefas WHERE id = ?", (tarefa["id"],))
        c.execute("UPDATE df_filas SET feitos = feitos + 1 WHERE fila = ?",
                  (self.nome,))
        c.execute("COMMIT")

    def _falhar(self, tarefa, erro):
        agora = self._relogio()
        mensagem = getattr(erro, "message", None) or str(erro) or type(erro).__name__
        historico = tarefa["historico"] + [
            {"tentativa": tarefa["tentativa"], "erro": mensagem, "quando": agora}]
        morreu = tarefa["tentativa"] >= int(self.config["tentativas"])
        c = self._conexao()
        c.execute("BEGIN IMMEDIATE")
        if morreu:
            c.execute(
                """UPDATE df_tarefas SET estado = 'morta', reservada_ate = NULL,
                   erro = ?, historico = ?, falhou_em = ? WHERE id = ?""",
                (mensagem, json.dumps(historico, ensure_ascii=False), agora,
                 tarefa["id"]))
        else:
            c.execute(
                """UPDATE df_tarefas SET estado = 'pendente', reservada_ate = NULL,
                   erro = ?, historico = ?, disponivel_em = ? WHERE id = ?""",
                (mensagem, json.dumps(historico, ensure_ascii=False),
                 agora + self.recuo_de(tarefa["tentativa"]), tarefa["id"]))
        c.execute("UPDATE df_filas SET falhas = falhas + 1 WHERE fila = ?",
                  (self.nome,))
        c.execute("COMMIT")

    def processar_um(self):
        """Processa UMA tarefa disponivel. None se nao havia; yes/no se deu certo."""
        if self.trabalhador is None:
            raise ErroDeEventos("esta fila persistente nao tem trabalhador: "
                                "passe a acao ao criar a fila")
        tarefa = self._reservar()
        if tarefa is None:
            return None
        info = {"id": tarefa["id"], "tentativa": tarefa["tentativa"]}
        try:
            _chamar_com_o_que_aceita(self.trabalhador, (tarefa["item"], info))
        except Exception as erro:                    # noqa: BLE001
            self._falhar(tarefa, erro)
            return False
        self._concluir(tarefa)
        return True

    def processar(self, limite=None):
        """Processa o que esta disponivel AGORA. Devolve quantas deram certo."""
        feitas = 0
        vezes = 0
        while limite is None or vezes < int(limite):
            resultado = self.processar_um()
            if resultado is None:
                break
            vezes += 1
            if resultado:
                feitas += 1
        return feitas

    # ── operarios ──

    def iniciar(self):
        if self.rodando:
            return self
        self.rodando = True
        self._threads = [threading.Thread(target=self._laco, daemon=True)
                         for _ in range(max(1, int(self.config["operarios"])))]
        for t in self._threads:
            t.start()
        return self

    def _laco(self):
        while self.rodando:
            try:
                if self.processar_um() is None:
                    time.sleep(float(self.config["espera_vazia"]))
            except Exception:                        # noqa: BLE001
                # o banco ocupado alem do timeout: tenta de novo, sem morrer
                time.sleep(float(self.config["espera_vazia"]))

    def parar(self):
        self.rodando = False
        for t in self._threads:
            t.join(timeout=5)
        self._threads = []
        return self

    def esperar(self, prazo=None):
        """Espera nao haver tarefa disponivel nem em andamento. As agendadas nao contam."""
        fim = None if prazo is None else time.perf_counter() + float(prazo)
        while self.pendentes() or self.em_andamento():
            if fim is not None and time.perf_counter() >= fim:
                break
            time.sleep(0.02)
        return self

    def fechar(self):
        self.parar()
        with self._trava_conexoes:
            for conexao in self._conexoes:
                try:
                    conexao.close()
                except Exception:                    # noqa: BLE001
                    pass
            self._conexoes = []
        self._local = threading.local()
        return self

    # ── olhar ──

    def _contar(self, onde, parametros=()):
        return self._conexao().execute(
            f"SELECT COUNT(*) FROM df_tarefas WHERE fila = ? AND {onde}",
            (self.nome,) + tuple(parametros)).fetchone()[0]

    def pendentes(self):
        agora = self._relogio()
        return self._contar(
            "((estado = 'pendente' AND disponivel_em <= ?) "
            "OR (estado = 'andamento' AND reservada_ate <= ?))", (agora, agora))

    def agendadas(self):
        return self._contar("estado = 'pendente' AND disponivel_em > ?",
                            (self._relogio(),))

    def em_andamento(self):
        return self._contar("estado = 'andamento' AND reservada_ate > ?",
                            (self._relogio(),))

    def mortas(self):
        linhas = self._conexao().execute(
            """SELECT id, item, tentativas, erro, historico, falhou_em, criada_em
               FROM df_tarefas WHERE fila = ? AND estado = 'morta' ORDER BY id""",
            (self.nome,)).fetchall()
        return [{"id": i, "item": json.loads(item), "tentativas": t, "erro": e,
                 "historico": json.loads(h), "falhou_em": f, "criada_em": cr}
                for i, item, t, e, h, f, cr in linhas]

    def reprocessar(self, ident=None):
        """Devolve da carta morta para a fila — uma, ou todas. Zera as tentativas."""
        c = self._conexao()
        onde = "fila = ? AND estado = 'morta'"
        parametros = [self._relogio(), self.nome]
        if ident is not None:
            onde += " AND id = ?"
            parametros.append(int(ident))
        c.execute("BEGIN IMMEDIATE")
        cursor = c.execute(
            f"""UPDATE df_tarefas SET estado = 'pendente', tentativas = 0,
                disponivel_em = ?, falhou_em = NULL WHERE {onde}""", parametros)
        c.execute("COMMIT")
        return cursor.rowcount

    def descartar_mortas(self, ident=None):
        c = self._conexao()
        onde = "fila = ? AND estado = 'morta'"
        parametros = [self.nome]
        if ident is not None:
            onde += " AND id = ?"
            parametros.append(int(ident))
        c.execute("BEGIN IMMEDIATE")
        cursor = c.execute(f"DELETE FROM df_tarefas WHERE {onde}", parametros)
        c.execute("COMMIT")
        return cursor.rowcount

    def resumo(self):
        feitos, falhas = self._conexao().execute(
            "SELECT feitos, falhas FROM df_filas WHERE fila = ?",
            (self.nome,)).fetchone()
        return {"feitos": feitos, "falhas": falhas, "pendentes": self.pendentes(),
                "agendadas": self.agendadas(), "em_andamento": self.em_andamento(),
                "mortas": self._contar("estado = 'morta'"),
                "operarios": len(self._threads)}

    def __repr__(self):
        return f"<fila persistente '{self.nome}' {self.pendentes()} pendentes>"


def fila_persistente(caminho, trabalhador=None, opcoes=None):
    return FilaPersistente(caminho, trabalhador, opcoes)


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
            "fila_persistente": fila_persistente,
            "FilaPersistente": FilaPersistente,
        }
