# -*- coding: utf-8 -*-
"""Arcane.Reativo — valores que avisam quando mudam.

A linguagem ja tem tres formas de lidar com mudanca, e nenhuma resolve
o mesmo problema:

    Arcane.Eventos    um emissor: quem escuta recebe o que foi emitido
    Arcane.Stream     topicos com offset — Kafka, e nao RxJS
    stream action     um gerador preguicoso, que produz sob demanda

O que falta e a quarta: um **valor** que outros valores acompanham. E a
diferenca entre "me avise quando algo acontecer" e "este total e sempre
a soma daqueles tres".

    adopt Arcane.Reativo as R

    preco := R.sinal(10.0)
    quantidade := R.sinal(3)
    total := R.derivado(lambda => preco.ler() * quantidade.ler())

    out total.ler()        // 30.0
    quantidade.escrever(5)
    out total.ler()        // 50.0 — ninguem recalculou a mao

Duas metades, e a diferenca entre elas
---------------------------------------
**Sinal** e valor: ele tem um estado agora, e quem pergunta recebe o
valor de agora. **Observavel** e fluxo: ele nao tem estado, e quem se
inscreve recebe o que vier daqui para a frente. Um clique e um fluxo;
um saldo e um valor.

Frameworks reativos costumam ter os dois e chamar os dois de "stream",
e ai a pergunta "qual e o valor atual?" passa a nao ter resposta.

Seis decisoes que valem lembrar
-------------------------------
1. **O derivado e preguicoso e memorizado.** Ele so recalcula quando
   alguem le E alguma dependencia mudou. Recalcular na escrita faria
   uma cadeia de dez derivados rodar dez vezes por mudanca, e a maioria
   deles nunca e lida.

2. **As dependencias sao descobertas na execucao.** Nao ha lista para
   declarar: o derivado roda, e todo sinal lido durante a execucao
   entra. Uma lista escrita a mao envelhece na primeira condicao nova
   dentro da formula — e o sintoma e um valor que para de atualizar.

3. **Um ciclo e recusado, com o caminho.** `a` depende de `b` que
   depende de `a` estouraria a pilha; aqui ele levanta dizendo a
   cadeia, que e o unico jeito de quebra-la.

4. **O efeito roda uma vez ao ser criado.** Sem isso, quem escreve
   `R.efeito(lambda => desenhar(total))` ve a tela vazia ate a primeira
   mudanca — e conclui que o efeito nao funciona.

5. **Escrever o mesmo valor nao notifica.** Um sinal que avisa sobre
   `x := x` faz uma cadeia de derivados recalcular por nada, e um
   efeito de rede disparar duas vezes.

6. **A propagacao tem duas fases: marcar TUDO, e so entao avisar.**
   Num losango — `c` le `a` e `b`, e `b` le `a` — a marcacao e o aviso
   numa fase so entregam um valor que nunca existiu. Medido, com
   `b = a * 2` e `c = a + b`: escrever `a := 5` fazia o efeito ver
   **7** (o `a` novo somado ao `b` velho) antes de ver 15. Nao e uma
   notificacao a mais; e um numero errado na tela, que aparece e some
   sozinho. E `_derivados` e um SET, entao qual caminho vem primeiro
   nao e escolhido por ninguem: o defeito ia e vinha conforme a ordem
   de hash.

   Daqui saem tres regras. O aviso pertence a **propagacao**, e nao ao
   recalculo — avisar de dentro do `_calcular` fazia uma simples
   LEITURA disparar efeito de terceiros. O efeito alcancado por dois
   caminhos roda **uma** vez, deduplicado pelo proprio objeto (e nao
   por `id()`, que so e unico entre objetos vivos). E uma escrita
   dentro de um efeito abre a **proxima** onda, em vez de reentrar na
   que esta sendo percorrida.
"""

import threading
import time

_erro_doc = "tecnicas/reativo"


def _erro(mensagem, nota="", dica="", classe="ReactiveError"):
    """O erro do grafo reativo, com a CLASSE certa.

    `handle ReactiveError` pega a familia inteira; quem precisa
    distinguir um ciclo de uma escrita indevida nomeia o especifico.
    Levantar `RuntimeError` em tudo faria as duas coisas chegarem
    iguais a quem escreve o `handle`.
    """
    from .. import errors
    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_erro_doc)


# ═══════════════════════════════════════════════════════════
#  O rastreador de dependencias
# ═══════════════════════════════════════════════════════════

class _Rastro:
    """Quem esta sendo calculado agora, por thread.

    E `threading.local` porque dois derivados calculando em threads
    diferentes nao podem registrar dependencia um no outro — esse bug
    seria intermitente e quase impossivel de reproduzir.
    """

    _local = threading.local()

    @classmethod
    def pilha(cls):
        if not hasattr(cls._local, "pilha"):
            cls._local.pilha = []
        return cls._local.pilha

    @classmethod
    def atual(cls):
        pilha = cls.pilha()
        return pilha[-1] if pilha else None

    @classmethod
    def entrar(cls, alvo):
        cls.pilha().append(alvo)

    @classmethod
    def sair(cls):
        pilha = cls.pilha()
        if pilha:
            pilha.pop()


# ═══════════════════════════════════════════════════════════
#  A onda: marcar TUDO, e so entao avisar
# ═══════════════════════════════════════════════════════════

def _avisar(ouvinte, valor):
    """O aviso de um sinal, com o valor ja decidido na escrita."""
    def rodar():
        ouvinte(valor)
    return rodar


def _avisar_do(derivado, ouvinte, anterior):
    """O aviso de um derivado: o valor e lido na HORA de avisar.

    Ler na marcacao puxaria um vizinho ainda nao marcado — e a leitura
    devolveria o valor velho dele, que e o losango outra vez.

    `anterior` e o valor de quando a marcacao comecou: um derivado
    invalidado por uma fonte que mudou pode recalcular para o MESMO
    valor (`modulo` de 3 e de -3), e avisar ali faria a tela redesenhar
    e um efeito de rede disparar por nada. E a mesma regra do sinal,
    um nivel acima.
    """
    def rodar():
        novo = derivado.ler()
        try:
            igual = bool(novo == anterior)
        except Exception:                                    # noqa: BLE001
            igual = novo is anterior
        if not igual:
            ouvinte(novo)
    return rodar


class _Onda:
    """A propagacao acontece em duas fases, e essa e a correcao inteira.

    Numa fase so, um losango entrega um valor que nunca existiu. Com
    `c` lendo `a` e `b`, e `b` lendo `a`::

        a.escrever(5)
        a notifica os seus dependentes — e `_derivados` e um SET,
        entao a ordem nao e escolhida por ninguem

    Se `c` vem primeiro, o efeito que acompanha `c` roda enquanto `b`
    ainda esta limpo com o valor velho. Medido, com `b = a * 2` e
    `c = a + b`: o efeito viu **7** (5 + o `b` antigo) antes de ver
    15. Nao e uma notificacao a mais — e um valor **errado** na tela,
    e ele aparece e some sozinho, que e a pior classe de defeito.

    Aqui a marcacao de sujo percorre o grafo inteiro **primeiro**, e
    so depois os efeitos e os ouvintes rodam. Quando eles rodam, todo
    derivado alcancado ja sabe que esta sujo, e a leitura puxa o valor
    novo por todos os caminhos.

    Duas decisoes:

    - **Dedup por objeto, e nao por `id()`.** Um efeito alcancado por
      dois caminhos roda uma vez. A chave e o proprio objeto: `id()`
      so e unico entre objetos VIVOS, e o CPython reaproveita o
      endereco de um que morreu — e o mesmo defeito que o cache da
      Vitrine teve.
    - **Quem abre a onda e quem a fecha.** Uma escrita dentro de um
      efeito nao reentra na onda que esta correndo: ela abre a
      proxima, depois que esta terminou. Reentrar faria a fila crescer
      enquanto e percorrida, e um efeito que escreve o que le nunca
      terminaria de forma visivel.
    """

    _local = threading.local()

    @classmethod
    def abrir(cls):
        """Devolve yes para quem virou dono desta onda."""
        if getattr(cls._local, "fila", None) is not None:
            return False
        cls._local.fila = {"acoes": [], "vistos": set()}
        return True

    @classmethod
    def fechar(cls):
        fila = getattr(cls._local, "fila", None)
        cls._local.fila = None
        if not fila:
            return
        for acao in fila["acoes"]:
            acao()

    @classmethod
    def adiar(cls, chave, acao):
        """Guarda para a segunda fase. Devolve no quando nao ha onda."""
        fila = getattr(cls._local, "fila", None)
        if fila is None:
            return False
        if chave is not None:
            if chave in fila["vistos"]:
                return True
            fila["vistos"].add(chave)
        fila["acoes"].append(acao)
        return True


class _onda:
    """`with _onda():` — a marcacao corre dentro, os avisos saem no fim."""

    __slots__ = ("_dono",)

    def __init__(self):
        self._dono = False

    def __enter__(self):
        self._dono = _Onda.abrir()
        return self

    def __exit__(self, *_erro):
        if self._dono:
            _Onda.fechar()
        return False


# ═══════════════════════════════════════════════════════════
#  Sinal: um valor que avisa
# ═══════════════════════════════════════════════════════════

class Sinal:
    """Um valor que sabe quem depende dele.

        preco := R.sinal(10.0)
        preco.ler()
        preco.escrever(12.0)
        preco.atualizar(lambda v => v * 1.1)
    """

    __slots__ = ("_valor", "_ouvintes", "_derivados", "_trava", "nome",
                 "_iguais")

    def __init__(self, inicial=None, nome="sinal", iguais=None):
        self._valor = inicial
        self._ouvintes = []
        self._derivados = set()
        self._trava = threading.RLock()
        self.nome = str(nome)
        #: Como decidir se o valor mudou. O padrao e `==`; um vault
        #: grande pode querer identidade, e uma comparacao cara pode
        #: querer uma chave.
        self._iguais = iguais

    # ── ler e escrever ───────────────────────────────────────

    def ler(self):
        """O valor de agora — e registra a dependencia de quem esta lendo."""
        alvo = _Rastro.atual()
        if alvo is not None:
            alvo._depender_de(self)
        return self._valor

    def valor(self):
        """O valor, SEM registrar dependencia.

        E a saida para ler um sinal dentro de um derivado sem que ele
        passe a depender dali — o `untracked` dos outros frameworks.
        Sem isso, um derivado que le um contador de depuracao passaria a
        recalcular a cada incremento dele.
        """
        return self._valor

    def escrever(self, novo):
        # A formula de um derivado e lida para descobrir de QUE ela
        # depende. Escrever de dentro dela faz a propagacao correr no
        # meio da propria descoberta: o grafo muda enquanto esta sendo
        # percorrido, e o resultado passa a depender da ordem em que
        # as dependencias foram visitadas — que e um conjunto, e
        # portanto nao e escolhida por ninguem.
        #
        # Um EFEITO escrevendo e outra coisa, e e legitimo: ele nao
        # tem valor a produzir, e a escrita dele abre a proxima onda.
        dentro = _Rastro.atual()
        if isinstance(dentro, Derivado):
            raise _erro(
                f"o derivado '{dentro.nome}' tentou escrever em "
                f"'{self.nome}'.",
                nota="um derivado so LE: e da leitura que saem as "
                     "dependencias dele",
                dica="para reagir a uma mudanca, use um efeito",
                classe="ReactiveWriteError")
        with self._trava:
            if self._mesmo(self._valor, novo):
                # Escrever o mesmo valor nao notifica: uma cadeia de
                # derivados recalcularia por nada, e um efeito de rede
                # dispararia duas vezes.
                return novo
            self._valor = novo
            alvos = list(self._derivados)
            ouvintes = list(self._ouvintes)
        with _onda():
            for derivado in alvos:
                derivado._sujar()
            for ouvinte in ouvintes:
                _Onda.adiar((self, ouvinte), _avisar(ouvinte, novo)) \
                    or ouvinte(novo)
        return novo

    def atualizar(self, acao):
        """Escreve a partir do valor de agora, sem a corrida do le-e-escreve."""
        with self._trava:
            atual = self._valor
        return self.escrever(acao(atual))

    def _mesmo(self, a, b):
        if self._iguais is not None:
            try:
                return bool(self._iguais(a, b))
            except Exception:                                # noqa: BLE001
                return False
        try:
            return bool(a == b)
        except Exception:                                    # noqa: BLE001
            return a is b

    # ── quem acompanha ───────────────────────────────────────

    def observar(self, acao, agora=False):
        """Chama a acao a cada mudanca. Devolve o cancelador."""
        with self._trava:
            self._ouvintes.append(acao)
        if agora:
            acao(self._valor)

        def cancelar():
            with self._trava:
                if acao in self._ouvintes:
                    self._ouvintes.remove(acao)
            return True

        return cancelar

    def _registrar(self, derivado):
        with self._trava:
            self._derivados.add(derivado)

    def _esquecer(self, derivado):
        with self._trava:
            self._derivados.discard(derivado)

    def ouvintes(self):
        return len(self._ouvintes) + len(self._derivados)

    def __repr__(self):
        return f"<sinal {self.nome}={self._valor!r}>"


def sinal(inicial=None, nome="sinal", iguais=None):
    return Sinal(inicial, nome, iguais)


# ═══════════════════════════════════════════════════════════
#  Derivado: um valor calculado de outros
# ═══════════════════════════════════════════════════════════

class Derivado:
    """Um valor que vem de outros, recalculado sob demanda.

        total := R.derivado(lambda => preco.ler() * quantidade.ler())

    Ele e **preguicoso** e **memorizado**: so recalcula quando alguem
    le e alguma dependencia mudou. Recalcular na escrita faria uma
    cadeia de dez derivados rodar dez vezes por mudanca, e a maioria
    deles nunca e lida.
    """

    __slots__ = ("_formula", "_valor", "_sujo", "_fontes", "_derivados",
                 "_ouvintes", "_trava", "nome", "_calculando")

    def __init__(self, formula, nome="derivado"):
        if not callable(formula):
            raise _erro("um derivado precisa de uma acao que calcula.",
                        dica="R.derivado(lambda => a.ler() + b.ler())")
        self._formula = formula
        self._valor = None
        self._sujo = True
        self._fontes = set()
        self._derivados = set()
        self._ouvintes = []
        self._trava = threading.RLock()
        self.nome = str(nome)
        self._calculando = False

    def ler(self):
        alvo = _Rastro.atual()
        if alvo is not None and alvo is not self:
            alvo._depender_de(self)
        if self._sujo:
            self._calcular()
        return self._valor

    def valor(self):
        if self._sujo:
            self._calcular()
        return self._valor

    def _calcular(self):
        if self._calculando:
            # A cadeia esta em `_Rastro`, e e ela que torna o ciclo
            # quebravel: dizer so "ha um ciclo" manda procurar em toda
            # a formula.
            cadeia = " → ".join(a.nome for a in _Rastro.pilha())
            raise _erro(
                f"o derivado '{self.nome}' depende de si mesmo.",
                nota=f"a cadeia: {cadeia} → {self.nome}",
                dica="quebre o ciclo: um dos dois precisa ser um sinal",
                classe="ReactiveCycleError")

        antigas = set(self._fontes)
        self._fontes = set()
        self._calculando = True
        _Rastro.entrar(self)
        try:
            novo = self._formula()
        finally:
            _Rastro.sair()
            self._calculando = False

        # As fontes que sumiram param de notificar. Sem isto, uma
        # formula com `given` acumularia dependencias dos dois ramos e
        # recalcularia por mudancas que ela nem le mais.
        for fonte in antigas - self._fontes:
            fonte._esquecer(self)
        for fonte in self._fontes - antigas:
            fonte._registrar(self)

        # Quem avisa os ouvintes e a PROPAGACAO, e nao o recalculo.
        # Avisar daqui significava que uma simples LEITURA disparava
        # efeito de terceiro — num instante escolhido por quem leu
        # primeiro, que e exatamente a janela do losango. E, com as
        # duas metades ligadas, o ouvinte era chamado duas vezes por
        # escrita: uma na onda e outra aqui.
        with self._trava:
            self._valor = novo
            self._sujo = False
        return novo

    def _depender_de(self, fonte):
        self._fontes.add(fonte)

    def _sujar(self):
        with self._trava:
            if self._sujo:
                return
            self._sujo = True
            anterior = self._valor
            alvos = list(self._derivados)
            ouvintes = list(self._ouvintes)
        with _onda():
            for derivado in alvos:
                derivado._sujar()
            for ouvinte in ouvintes:
                # Um derivado com ouvinte deixa de ser preguicoso:
                # alguem esta esperando o valor novo, e nao vai
                # perguntar. Mas a LEITURA fica para a segunda fase —
                # ler aqui puxaria um vizinho que ainda nao foi
                # marcado, que e o losango de novo.
                aviso = _avisar_do(self, ouvinte, anterior)
                if not _Onda.adiar((self, ouvinte), aviso):
                    aviso()

    def _registrar(self, derivado):
        with self._trava:
            self._derivados.add(derivado)

    def _esquecer(self, derivado):
        with self._trava:
            self._derivados.discard(derivado)

    def observar(self, acao, agora=False):
        """Chama a acao a cada mudanca. Devolve o cancelador.

        A leitura no fim NAO e um detalhe de eficiencia: as
        dependencias de um derivado sao descobertas **executando** a
        formula, entao um derivado que ninguem leu ainda nao esta
        ligado a fonte nenhuma. Sem ela, `observar` num derivado
        recem-criado registrava o ouvinte num objeto que jamais seria
        avisado — a acao ficava guardada para sempre, e nada
        denunciava.
        """
        with self._trava:
            self._ouvintes.append(acao)
        valor = self.ler()
        if agora:
            acao(valor)

        def cancelar():
            with self._trava:
                if acao in self._ouvintes:
                    self._ouvintes.remove(acao)
            return True

        return cancelar

    def fontes(self):
        """De quem este valor depende — descoberto, e nao declarado."""
        if self._sujo:
            self._calcular()
        return sorted(f.nome for f in self._fontes)

    def __repr__(self):
        estado = "sujo" if self._sujo else repr(self._valor)
        return f"<derivado {self.nome}={estado}>"


def derivado(formula, nome="derivado"):
    return Derivado(formula, nome)


# ═══════════════════════════════════════════════════════════
#  Efeito: o que acontece quando muda
# ═══════════════════════════════════════════════════════════

class Efeito:
    """Roda uma acao sempre que algo que ela le mudar.

        R.efeito(lambda => out $"total: {total.ler()}")

    Ele roda **uma vez ao ser criado**: sem isso, quem escreve um
    efeito que desenha a tela ve a tela vazia ate a primeira mudanca, e
    conclui que o efeito nao funciona.
    """

    __slots__ = ("_acao", "_fontes", "_ativo", "_trava", "nome", "execucoes",
                 "_limpeza")

    def __init__(self, acao, nome="efeito", agora=True):
        if not callable(acao):
            raise _erro("um efeito precisa de uma acao para rodar.")
        self._acao = acao
        self._fontes = set()
        self._ativo = True
        self._trava = threading.RLock()
        self.nome = str(nome)
        self.execucoes = 0
        self._limpeza = None
        if agora:
            self._rodar()

    def _rodar(self):
        if not self._ativo:
            return
        if callable(self._limpeza):
            # A limpeza do ciclo anterior roda ANTES do proximo: e como
            # se cancela a inscricao antiga antes de abrir a nova, e sem
            # isso um efeito que abre conexao abre uma por mudanca.
            try:
                self._limpeza()
            except Exception:                                # noqa: BLE001
                pass
            self._limpeza = None

        antigas = set(self._fontes)
        self._fontes = set()
        _Rastro.entrar(self)
        try:
            devolvido = self._acao()
        finally:
            _Rastro.sair()
        if callable(devolvido):
            self._limpeza = devolvido
        self.execucoes += 1

        for fonte in antigas - self._fontes:
            fonte._esquecer(self)
        for fonte in self._fontes - antigas:
            fonte._registrar(self)

    def _depender_de(self, fonte):
        self._fontes.add(fonte)

    def _sujar(self):
        # A chave e o proprio efeito: alcancado por dois caminhos do
        # mesmo losango, ele roda UMA vez — e depois que os dois
        # caminhos foram marcados.
        if not _Onda.adiar(self, self._rodar):
            self._rodar()

    def parar(self):
        """Cancela o efeito e roda a limpeza dele."""
        with self._trava:
            if not self._ativo:
                return False
            self._ativo = False
            fontes = list(self._fontes)
        for fonte in fontes:
            fonte._esquecer(self)
        if callable(self._limpeza):
            try:
                self._limpeza()
            except Exception:                                # noqa: BLE001
                pass
        return True

    def fontes(self):
        return sorted(f.nome for f in self._fontes)

    def __repr__(self):
        return (f"<efeito {self.nome}, {self.execucoes} execucao(oes)"
                f"{'' if self._ativo else ', parado'}>")


def efeito(acao, nome="efeito", agora=True):
    return Efeito(acao, nome, agora)


# ═══════════════════════════════════════════════════════════
#  Lote: uma notificacao para muitas escritas
# ═══════════════════════════════════════════════════════════

def lote(acao):
    """Agrupa varias escritas numa notificacao so.

        R.lote(lambda => atualizar_tudo())

    Sem ele, mudar tres sinais que alimentam o mesmo derivado faz o
    efeito rodar tres vezes — e as duas primeiras veem um estado
    intermediario que nunca deveria aparecer na tela.

    A primeira versao montava uma lista de adiados que **ninguem
    lia**: o gancho era escrito num `threading.local` e nenhum caminho
    de escrita o consultava. `lote` existia, tinha doc, tinha teste de
    que nao estourava — e nao agrupava nada. Medido: tres escritas
    davam tres notificacoes, exatamente como sem ele.

    Hoje ele e a mesma onda que uma escrita abre, mantida aberta pela
    acao inteira: as marcacoes se acumulam, os efeitos sao
    deduplicados pelo proprio objeto, e todos rodam uma vez no fim.
    """
    with _onda():
        return acao()


# ═══════════════════════════════════════════════════════════
#  Observavel: um fluxo, e nao um valor
# ═══════════════════════════════════════════════════════════

class Inscricao:
    """O que uma inscricao devolve: o jeito de cancela-la."""

    __slots__ = ("_cancelar", "ativa")

    def __init__(self, cancelar):
        self._cancelar = cancelar
        self.ativa = True

    def cancelar(self):
        if not self.ativa:
            return False
        self.ativa = False
        if callable(self._cancelar):
            self._cancelar()
        return True

    def __repr__(self):
        return f"<inscricao {'ativa' if self.ativa else 'cancelada'}>"


class Observavel:
    """Um fluxo de valores no tempo.

    Diferente do sinal, ele **nao tem valor atual**: quem se inscreve
    recebe o que vier daqui para a frente. Um clique e um fluxo; um
    saldo e um valor, e confundir os dois faz a pergunta "qual e o
    valor agora?" deixar de ter resposta.
    """

    __slots__ = ("_inscritos", "_trava", "nome", "_encerrado")

    def __init__(self, nome="observavel"):
        self._inscritos = []
        self._trava = threading.RLock()
        self.nome = str(nome)
        self._encerrado = False

    # ── emitir ───────────────────────────────────────────────

    def emitir(self, valor):
        """Entrega o valor a quem esta inscrito.

        Num fluxo ja encerrado isto **levanta**. Devolver `no` calado
        era o que acontecia antes, e ninguem le o retorno de um
        `emitir`: o valor sumia, e o defeito aparecia como um painel
        que para de atualizar sem nada no log.
        """
        if self._encerrado:
            raise _erro(
                f"o fluxo '{self.nome}' ja foi encerrado.",
                nota="quem estava inscrito ja foi avisado do fim e "
                     "cancelou a inscricao — este valor nao chegaria a "
                     "ninguem",
                dica="abra outro observavel; um fluxo encerrado nao reabre",
                classe="StreamClosedError")
        return self._empurrar(valor)

    def _empurrar(self, valor):
        """O caminho de dentro: entrega, e desiste calado se ja fechou.

        Os operadores e as fontes frias escrevem por aqui. Um
        temporizador que bate depois de o assinante cancelar nao pode
        levantar: o erro sairia numa thread que ninguem observa, e o
        cancelamento e o caminho NORMAL de um `esperar` ou de um
        `intervalo`.
        """
        if self._encerrado:
            return False
        with self._trava:
            alvos = list(self._inscritos)
        for alvo in alvos:
            alvo["ao_valor"](valor)
        return True

    def falhar(self, erro):
        with self._trava:
            alvos = list(self._inscritos)
        for alvo in alvos:
            if callable(alvo.get("ao_erro")):
                alvo["ao_erro"](erro)
        return self.encerrar()

    def encerrar(self):
        if self._encerrado:
            return False
        self._encerrado = True
        with self._trava:
            alvos = list(self._inscritos)
            self._inscritos.clear()
        for alvo in alvos:
            if callable(alvo.get("ao_fim")):
                alvo["ao_fim"]()
        return True

    # ── ouvir ────────────────────────────────────────────────

    def inscrever(self, ao_valor, ao_erro=None, ao_fim=None):
        registro = {"ao_valor": ao_valor, "ao_erro": ao_erro,
                    "ao_fim": ao_fim}
        with self._trava:
            self._inscritos.append(registro)

        def cancelar():
            with self._trava:
                if registro in self._inscritos:
                    self._inscritos.remove(registro)

        return Inscricao(cancelar)

    def inscritos(self):
        return len(self._inscritos)

    # ── operadores ───────────────────────────────────────────

    def morph(self, transformar):
        """Cada valor vira outro. O nome e o mesmo do pipeline da
        linguagem, de proposito: `>> morph` faz isto com um cluster."""
        return _ligar(self, lambda valor, saida: saida._empurrar(
            transformar(valor)), f"{self.nome}.morph")

    def sift(self, condicao):
        """So passa o que satisfaz — o `>> sift` do pipeline."""
        def passar(valor, saida):
            if condicao(valor):
                saida._empurrar(valor)

        return _ligar(self, passar, f"{self.nome}.sift")

    def distill(self, juntar, inicial=None):
        """Acumula e emite o acumulado a cada valor.

        Note a diferenca para o `>> distill` do pipeline: la o
        resultado sai UMA vez, no fim; aqui sai a cada valor, porque um
        fluxo nao tem fim para esperar.
        """
        estado = {"atual": inicial}

        def acumular(valor, saida):
            estado["atual"] = juntar(estado["atual"], valor)
            saida._empurrar(estado["atual"])

        return _ligar(self, acumular, f"{self.nome}.distill")

    def distintos(self, chave=None):
        """Pula o valor repetido em seguida ao anterior."""
        estado = {"ultimo": _SEM_VALOR}

        def filtrar(valor, saida):
            atual = chave(valor) if callable(chave) else valor
            if estado["ultimo"] is _SEM_VALOR or atual != estado["ultimo"]:
                estado["ultimo"] = atual
                saida._empurrar(valor)

        return _ligar(self, filtrar, f"{self.nome}.distintos")

    def primeiros(self, quantos):
        """Os N primeiros, e encerra. E o `take` de sempre."""
        estado = {"vistos": 0}

        def contar(valor, saida):
            if estado["vistos"] >= quantos:
                return
            estado["vistos"] += 1
            saida._empurrar(valor)
            if estado["vistos"] >= quantos:
                saida.encerrar()

        return _ligar(self, contar, f"{self.nome}.primeiros")

    def pular(self, quantos):
        estado = {"vistos": 0}

        def contar(valor, saida):
            estado["vistos"] += 1
            if estado["vistos"] > quantos:
                saida._empurrar(valor)

        return _ligar(self, contar, f"{self.nome}.pular")

    def blocos(self, tamanho):
        """Junta em grupos de N e emite o grupo."""
        estado = {"atual": []}

        def juntar(valor, saida):
            estado["atual"].append(valor)
            if len(estado["atual"]) >= tamanho:
                saida._empurrar(list(estado["atual"]))
                estado["atual"] = []

        return _ligar(self, juntar, f"{self.nome}.blocos")

    def esperar(self, segundos):
        """So emite quando para de chegar por N segundos — o *debounce*.

        E o operador que existe para a caixa de busca: sem ele, cada
        tecla dispara uma consulta, e a resposta da terceira pode chegar
        depois da quinta.
        """
        estado = {"timer": None}

        def receber(valor, saida):
            if estado["timer"] is not None:
                estado["timer"].cancel()
            # O timer e *daemon*: um debounce pendente nao pode segurar
            # o processo aberto depois que o programa terminou.
            timer = threading.Timer(float(segundos),
                                    lambda: saida._empurrar(valor))
            timer.daemon = True
            estado["timer"] = timer
            timer.start()

        return _ligar(self, receber, f"{self.nome}.esperar")

    def limitar(self, segundos):
        """Emite no maximo um por janela — o *throttle*.

        Diferente de `esperar`: este emite o PRIMEIRO e ignora o resto
        da janela. Para um botao que nao pode ser clicado duas vezes,
        e este; para uma busca, e o outro.
        """
        estado = {"ultimo": 0.0}

        def passar(valor, saida):
            agora = time.monotonic()
            if agora - estado["ultimo"] >= float(segundos):
                estado["ultimo"] = agora
                saida._empurrar(valor)

        return _ligar(self, passar, f"{self.nome}.limitar")

    def ao_falhar(self, tratador):
        """Troca o erro por um valor, e o fluxo continua."""
        alvo = _AoFalhar(self, tratador, f"{self.nome}.ao_falhar")
        return alvo

    def para_sinal(self, inicial=None):
        """O fluxo vira valor: o sinal guarda o ultimo emitido.

        E a ponte entre as duas metades, e ela so vai num sentido —
        um valor sempre pode virar fluxo (`observar`), e um fluxo so
        vira valor quando alguem diz qual e o valor ANTES do primeiro
        item.
        """
        alvo = Sinal(inicial, f"{self.nome}.sinal")
        self.inscrever(alvo.escrever)
        return alvo

    def __repr__(self):
        return (f"<observavel {self.nome}, {len(self._inscritos)} inscrito(s)"
                f"{', encerrado' if self._encerrado else ''}>")


class _AoFalhar(Observavel):
    """Troca o erro por um valor. Liga preguicoso, como `_Operador`."""

    __slots__ = ("_fonte", "_tratador", "_ligado")

    def __init__(self, fonte, tratador, nome):
        super().__init__(nome)
        self._fonte = fonte
        self._tratador = tratador
        self._ligado = False

    def inscrever(self, ao_valor, ao_erro=None, ao_fim=None):
        inscricao = super().inscrever(ao_valor, ao_erro, ao_fim)
        if not self._ligado:
            self._ligado = True
            self._fonte.inscrever(
                self.emitir,
                lambda erro: self._empurrar(self._tratador(erro)),
                self.encerrar)
        return inscricao


class _SemValor:
    def __repr__(self):
        return "<sem valor>"


_SEM_VALOR = _SemValor()


class _Operador(Observavel):
    """Um observavel que so escuta a fonte quando ALGUEM escuta ele.

    A ligacao preguicosa nao e economia: com a ligacao na construcao,
    uma fonte FRIA — que emite ao ser escutada, como `de_cluster` —
    despejava os valores no operador antes de o assinante final
    existir, e o resultado era uma lista vazia sem erro nenhum.

    E o problema classico de fonte fria, e a correcao classica: a
    cadeia inteira so liga quando a ponta e escutada.
    """

    __slots__ = ("_fonte", "_passo", "_ligado")

    def __init__(self, fonte, passo, nome):
        super().__init__(nome)
        self._fonte = fonte
        self._passo = passo
        self._ligado = False

    def inscrever(self, ao_valor, ao_erro=None, ao_fim=None):
        inscricao = super().inscrever(ao_valor, ao_erro, ao_fim)
        if not self._ligado:
            self._ligado = True
            self._fonte.inscrever(lambda valor: self._passo(valor, self),
                                  self.falhar, self.encerrar)
        return inscricao


def _ligar(fonte, passo, nome):
    """Liga um operador: a fonte alimenta um observavel novo."""
    return _Operador(fonte, passo, nome)


def observavel(nome="observavel"):
    return Observavel(nome)


class _DeCluster(Observavel):
    """Um observavel que repete os mesmos itens a cada inscricao.

    E uma SUBCLASSE, e nao um metodo trocado na instancia: `Observavel`
    tem `__slots__`, e trocar o metodo num objeto com slots levanta
    "attribute is read-only" — o que so apareceria na primeira vez que
    alguem usasse a funcao.
    """

    __slots__ = ("_itens",)

    def __init__(self, itens, nome="de_cluster"):
        super().__init__(nome)
        self._itens = list(itens or [])

    def inscrever(self, ao_valor, ao_erro=None, ao_fim=None):
        inscricao = super().inscrever(ao_valor, ao_erro, ao_fim)
        for item in self._itens:
            ao_valor(item)
        if callable(ao_fim):
            ao_fim()
        return inscricao


def de_cluster(itens, nome="de_cluster"):
    """Um observavel que emite os itens dados e encerra.

    Os itens sao emitidos na INSCRICAO, e nao agora: emitir antes de
    alguem escutar seria emitir para ninguem, que e o erro mais comum
    ao aprender fluxos.
    """
    return _DeCluster(itens, nome)


def juntar(*fontes):
    """Um observavel com tudo o que chega de qualquer um deles."""
    alvo = Observavel("juntar")
    pendentes = {"quantos": len(fontes)}

    def um_acabou():
        pendentes["quantos"] -= 1
        if pendentes["quantos"] <= 0:
            alvo.encerrar()

    for fonte in fontes:
        fonte.inscrever(alvo.emitir, alvo.falhar, um_acabou)
    return alvo


def combinar(*fontes):
    """Emite um cluster com o ULTIMO de cada um, a cada mudanca.

    Ele so comeca a emitir quando **todos** ja emitiram uma vez: antes
    disso o cluster teria buracos, e quem recebe teria de tratar um
    `void` que so acontece no comeco — a fonte mais comum de bug em
    codigo reativo.
    """
    ultimos = [_SEM_VALOR] * len(fontes)
    alvo = Observavel("combinar")

    def fazer(indice):
        def receber(valor):
            ultimos[indice] = valor
            if all(u is not _SEM_VALOR for u in ultimos):
                alvo._empurrar(list(ultimos))
        return receber

    for i, fonte in enumerate(fontes):
        fonte.inscrever(fazer(i), alvo.falhar)
    return alvo


class _Intervalo(Observavel):
    """O relogio que emite. Subclasse pelo mesmo motivo de `_DeCluster`."""

    __slots__ = ("_segundos", "_quantos", "_n", "_timer", "_vivo")

    def __init__(self, segundos, quantos, nome):
        super().__init__(nome)
        self._segundos = float(segundos)
        self._quantos = int(quantos)
        self._n = 0
        self._timer = None
        self._vivo = True

    def _agendar(self):
        # O timer e *daemon*: um observavel esquecido nao pode impedir
        # o processo de terminar.
        timer = threading.Timer(self._segundos, self._bater)
        timer.daemon = True
        self._timer = timer
        timer.start()

    def _bater(self):
        if not self._vivo:
            return
        self._empurrar(self._n)
        self._n += 1
        if self._quantos and self._n >= self._quantos:
            self.encerrar()
            return
        self._agendar()

    def encerrar(self):
        self._vivo = False
        if self._timer is not None:
            self._timer.cancel()
        return super().encerrar()


def intervalo(segundos, quantos=0, nome="intervalo"):
    """Emite 0, 1, 2… a cada N segundos. `quantos := 0` nao para.

    O timer e *daemon*: um observavel esquecido nao pode impedir o
    processo de terminar.
    """
    alvo = _Intervalo(segundos, quantos, nome)
    alvo._agendar()
    return alvo


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneReativo:
    """Arcane.Reativo — valores que avisam quando mudam."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Reativo",

            # ── valor ──
            "sinal": sinal,
            "Sinal": Sinal,
            "derivado": derivado,
            "Derivado": Derivado,
            "efeito": efeito,
            "Efeito": Efeito,
            "lote": lote,

            # ── fluxo ──
            "observavel": observavel,
            "Observavel": Observavel,
            "de_cluster": de_cluster,
            "juntar": juntar,
            "combinar": combinar,
            "intervalo": intervalo,
            "Inscricao": Inscricao,
        }
