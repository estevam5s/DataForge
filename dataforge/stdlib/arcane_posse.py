# -*- coding: utf-8 -*-
"""Arcane.Posse — quem é o dono, quem tomou emprestado, e quando solta.

O que faltava
-------------
Numa linguagem com coleta automática, "vazar memória" quase nunca é o
problema: o coletor resolve. O que ele NÃO resolve é o **recurso** — o
arquivo que não fecha, a conexão que fica aberta, o cadeado que ninguém
solta — porque o coletor não promete *quando* passa. E há o defeito
irmão: duas partes do programa escrevendo no mesmo objeto porque nenhuma
delas sabe quem manda nele.

Este módulo traz a disciplina de posse para um mundo com coletor:

    d := P.dono(conexao, lambda c => c.fechar())
    P.com(d, lambda c => c.consultar("select 1"))     # fecha no fim, sempre

    outro := d.mover()        # quem move, perde
    d.usar(…)                 # erro, dizendo ONDE foi movido

O que ele não é
---------------
Não é o `borrow checker` do Rust, e fingir que é seria pior que não ter.
Três diferenças que valem estar escritas:

1. **Nada aqui vira endereço inválido.** O coletor continua no caminho:
   o que a posse protege é o *protocolo* (soltar uma vez, não usar
   depois), e não a integridade da memória — essa nunca esteve em risco.

2. **A regra do empréstimo é cobrada QUANDO RODA**, como o `RefCell`, e
   não numa análise de regiões em tempo de compilação. O `check` prova o
   que dá para provar com o fluxo de um arquivo (uso depois de mover,
   recurso que ninguém solta) e cala no resto.

3. **O empréstimo vive num escopo explícito** — o corpo de `usar`,
   `mudar`, `ler` e `escrever` —, e não até o fim do bloco. É o mesmo
   efeito prático dos *non-lexical lifetimes*, por um caminho mais
   simples: quem entrega o valor sabe exatamente quando ele volta.

Decisões
--------
- **`soltar` é idempotente, e o finalizador roda uma vez.** Um `close()`
  chamado duas vezes é normal em código de verdade — no `defer` e no
  caminho de erro, por exemplo — e transformar isso em erro faria a
  disciplina atrapalhar em vez de ajudar.
- **A contagem do compartilhado é determinística.** O finalizador roda
  quando o último dono solta, e não quando o coletor decide passar. É o
  que diferencia isto de uma referência comum.
- **O ciclo de referências fortes vaza, e isso é mostrado** em vez de
  escondido: é o mesmo problema do `Rc` em qualquer linguagem, e a saída
  é a mesma — uma das voltas tem de ser fraca.
"""

import threading

from ..errors import RuntimeError_

#: O que `Dono` responde quando já não pode entregar o valor.
_MORTO = "soltou"
_MOVIDO = "moveu"


def _recusa(estado, onde, node_linha=0, nome="valor"):
    if estado == _MOVIDO:
        return RuntimeError_(
            f"este dono já moveu o {nome}: quem move, perde.", 0, 0,
            nota=f"movido em {onde}" if onde else "",
            dica="use o dono que recebeu o valor, ou tire o 'mover'",
            doc="memoria/posse")
    return RuntimeError_(
        f"este dono já soltou o {nome}.", 0, 0,
        nota=f"solto em {onde}" if onde else "",
        dica="solte no fim do uso — 'P.com(dono, acao)' faz isso por você",
        doc="memoria/posse")


class Emprestimo:
    """O valor entregue por um tempo — e só por esse tempo.

    Ele existe para que o empréstimo tenha um objeto próprio: um handle
    que sai do escopo e continua sendo usado é o erro que o borrow
    checker existe para pegar, e aqui ele é pego quando roda.
    """

    __slots__ = ("_valor", "_vivo", "_exclusivo")

    def __init__(self, valor, exclusivo=False):
        self._valor = valor
        self._vivo = True
        self._exclusivo = exclusivo

    def ler(self):
        if not self._vivo:
            raise RuntimeError_(
                "este empréstimo já saiu do escopo em que valia.", 0, 0,
                nota="um empréstimo vale enquanto o corpo que o recebeu roda",
                dica="faça o trabalho dentro de 'usar'/'mudar', ou peça o "
                     "valor ao dono de novo",
                doc="memoria/posse")
        return self._valor

    def exclusivo(self):
        return self._exclusivo

    def vivo(self):
        return self._vivo

    def _encerrar(self):
        self._vivo = False

    def __repr__(self):                                    # pragma: no cover
        return f"<emprestimo {'vivo' if self._vivo else 'encerrado'}>"


class Dono:
    """Posse exclusiva, com liberação determinística.

    É o `Box`/`unique_ptr` desta linguagem: um valor, um dono, um
    finalizador que roda uma vez — no `soltar()`, no fim de um
    `P.com(…)`, ou nunca, se quem escreveu esquecer (e aí o `check`
    avisa).
    """

    __slots__ = ("_valor", "_ao_soltar", "_estado", "_onde", "_lendo",
                 "_escrevendo", "_trava", "_nome")

    def __init__(self, valor, ao_soltar=None, nome="valor"):
        self._valor = valor
        self._ao_soltar = ao_soltar
        self._estado = "vivo"
        self._onde = ""
        self._lendo = 0
        self._escrevendo = False
        self._trava = threading.RLock()
        self._nome = nome

    # ── estado ──
    def vivo(self):
        return self._estado == "vivo"

    def movido(self):
        return self._estado == _MOVIDO

    def solto(self):
        return self._estado == _MORTO

    def _exigir_vivo(self):
        if self._estado != "vivo":
            raise _recusa(self._estado, self._onde, nome=self._nome)

    # ── empréstimo com escopo ──
    def usar(self, acao):
        """Empresta para LER. Vários podem ler ao mesmo tempo."""
        self._exigir_vivo()
        if self._escrevendo:
            raise _conflito("ler", "escrevendo")
        with self._trava:
            self._lendo += 1
        emprestimo = Emprestimo(self._valor)
        try:
            return acao(self._valor)
        finally:
            emprestimo._encerrar()
            with self._trava:
                self._lendo -= 1

    def mudar(self, acao):
        """Empresta para ESCREVER. Um de cada vez, e ninguém lendo.

        Como em `Celula.escrever`, o que a ação devolver passa a ser o
        valor — senão `mudar` não muda nada num número ou num texto,
        onde não há como mexer no lugar.
        """
        self._exigir_vivo()
        if self._escrevendo:
            raise _conflito("escrever", "escrevendo")
        if self._lendo:
            raise _conflito("escrever", "lendo")
        self._escrevendo = True
        try:
            novo = acao(self._valor)
            if novo is not None:
                self._valor = novo
            return self._valor
        finally:
            self._escrevendo = False

    def emprestar(self):
        """Um empréstimo SEM escopo — e por isso já nasce encerrado.

        Ele existe para que o erro seja claro: quem quer o valor fora de
        um corpo está pedindo para guardar uma referência que o dono não
        controla, e é isso que a mensagem diz.
        """
        self._exigir_vivo()
        emprestimo = Emprestimo(self._valor)
        emprestimo._encerrar()
        return emprestimo

    # ── posse ──
    def mover(self, onde=""):
        """Transfere a posse. Devolve o novo dono; este fica movido."""
        self._exigir_vivo()
        novo = Dono(self._valor, self._ao_soltar, self._nome)
        self._estado = _MOVIDO
        self._onde = str(onde or "")
        self._valor = None
        self._ao_soltar = None
        return novo

    def copiar(self):
        """Outro dono do MESMO valor — a cópia rasa.

        Os dois veem a mesma coisa: é o que se quer quando o valor é o
        recurso (uma conexão), e é o que NÃO se quer quando ele é o dado.
        Para o dado, `clonar`.
        """
        self._exigir_vivo()
        return Dono(self._valor, None, self._nome)

    def clonar(self, copiador=None):
        """Outro dono de uma CÓPIA — o clone.

        Sem `copiador`, copia com o que a linguagem sabe copiar. Com ele,
        quem chama decide a profundidade.
        """
        self._exigir_vivo()
        if copiador is not None:
            return Dono(copiador(self._valor), None, self._nome)
        import copy
        return Dono(copy.deepcopy(self._valor), None, self._nome)

    def soltar(self):
        """Roda o finalizador AGORA. Chamar de novo não faz nada."""
        with self._trava:
            if self._estado != "vivo":
                return False
            self._estado = _MORTO
            finalizador, valor = self._ao_soltar, self._valor
            self._ao_soltar = None
            self._valor = None
        if finalizador is not None:
            finalizador(valor)
        soltar_aninhados(valor)
        return True

    def __repr__(self):                                    # pragma: no cover
        return f"<dono {self._estado}>"


def _conflito(querido, atual):
    return RuntimeError_(
        f"não dá para {querido}: alguém está {atual} este valor agora.",
        0, 0,
        nota="empréstimo: muitos leem, ou um escreve — nunca os dois",
        dica="feche a leitura antes de escrever, ou faça as duas coisas "
             "dentro do mesmo 'mudar'",
        doc="memoria/posse")


class Celula:
    """Mutabilidade interior, com a regra do empréstimo cobrada na hora.

    É o `RefCell`: o valor é compartilhado, e a disciplina — muitos leem
    OU um escreve — é conferida quando roda. Sem ela, "posse" viraria
    documentação: o objeto continuaria alcançável por dois caminhos, e
    nada impediria a escrita no meio da leitura.
    """

    __slots__ = ("_valor", "_lendo", "_escrevendo", "_trava")

    def __init__(self, valor):
        self._valor = valor
        self._lendo = 0
        self._escrevendo = False
        self._trava = threading.RLock()

    def ler(self, acao):
        if self._escrevendo:
            raise _conflito("ler", "escrevendo")
        with self._trava:
            self._lendo += 1
        try:
            return acao(self._valor)
        finally:
            with self._trava:
                self._lendo -= 1

    def escrever(self, acao):
        """Escreve com exclusividade — e GUARDA o que a acao devolver.

        Ela so entregava o valor para a acao mexer no lugar, e
        descartava o retorno. Num cluster ou num vault isso funciona
        por acidente (mexer no lugar muda o mesmo objeto); num
        **numero ou num texto** nao ha como mexer no lugar, e
        `escrever(lambda v => v + 1)` nao escrevia nada — o programa
        seguia com o valor velho, calado. Uma escrita que nao escreve
        e o pior desfecho possivel numa peca chamada `escrever`.

        Devolver `void` continua sendo mexer no lugar: quem escreve
        `cel.escrever(lambda v => out v)` nao esta pedindo para
        guardar `void`.
        """
        if self._escrevendo:
            raise _conflito("escrever", "escrevendo")
        if self._lendo:
            raise _conflito("escrever", "lendo")
        self._escrevendo = True
        try:
            novo = acao(self._valor)
            if novo is not None:
                self._valor = novo
            return self._valor
        finally:
            self._escrevendo = False

    def trocar(self, novo):
        """Troca o valor inteiro. Recusado durante qualquer empréstimo."""
        if self._escrevendo or self._lendo:
            raise _conflito("trocar", "escrevendo" if self._escrevendo else "lendo")
        anterior, self._valor = self._valor, novo
        return anterior

    def emprestimos(self):
        """Quantos empréstimos estão abertos agora."""
        return self._lendo + (1 if self._escrevendo else 0)

    def __repr__(self):                                    # pragma: no cover
        return f"<celula {self.emprestimos()} emprestimo(s)>"


class Compartilhado:
    """Posse compartilhada, com contagem determinística — o `Rc`.

    Cada `clonar()` soma um; cada `soltar()` tira um. Quando o último
    sai, o finalizador roda — naquele instante, e não quando o coletor
    resolver passar. É essa previsibilidade que justifica a peça existir
    ao lado de uma referência comum.
    """

    __slots__ = ("_nucleo", "_solto")

    def __init__(self, valor=None, ao_soltar=None, _nucleo=None, atomico=False):
        self._nucleo = _nucleo or _Nucleo(valor, ao_soltar, atomico)
        self._nucleo.somar()
        self._solto = False

    def clonar(self):
        """Mais um dono. A contagem sobe."""
        self._exigir_vivo()
        return Compartilhado(_nucleo=self._nucleo)

    def usar(self, acao):
        self._exigir_vivo()
        return acao(self._nucleo.valor)

    def valor(self):
        self._exigir_vivo()
        return self._nucleo.valor

    def contar(self):
        return self._nucleo.fortes

    def fracas(self):
        return self._nucleo.fracas

    def vivo(self):
        return not self._solto and self._nucleo.fortes > 0

    def soltar(self):
        """Este dono sai. O finalizador roda quando o último sair."""
        if self._solto:
            return False
        self._solto = True
        self._nucleo.tirar()
        return True

    def _exigir_vivo(self):
        if self._solto:
            raise RuntimeError_(
                "este dono compartilhado já soltou a parte dele.", 0, 0,
                dica="peça outra cópia a quem ainda a tem",
                doc="memoria/posse")
        if self._nucleo.fortes <= 0:
            raise RuntimeError_(
                "o valor compartilhado já foi liberado: o último dono saiu.",
                0, 0, doc="memoria/posse")

    def __repr__(self):                                    # pragma: no cover
        return f"<compartilhado {self._nucleo.fortes} dono(s)>"


class _Nucleo:
    """O que os donos compartilham: o valor, a contagem e o finalizador."""

    __slots__ = ("valor", "ao_soltar", "fortes", "fracas", "_trava", "atomico")

    def __init__(self, valor, ao_soltar, atomico=False):
        self.valor = valor
        self.ao_soltar = ao_soltar
        self.fortes = 0
        self.fracas = 0
        self.atomico = atomico
        #: A trava existe sempre; o que 'atomico' muda é a PROMESSA de
        #: que a contagem vale entre threads. Uma contagem sem trava
        #: perde incrementos em silêncio — medido, no repositório, em
        #: 40.425 de 80.000.
        self._trava = threading.RLock()

    def somar(self):
        with self._trava:
            self.fortes += 1

    def tirar(self):
        with self._trava:
            self.fortes -= 1
            if self.fortes > 0:
                return
            finalizador, valor = self.ao_soltar, self.valor
            self.ao_soltar = None
            self.valor = None
        if finalizador is not None:
            finalizador(valor)
        soltar_aninhados(valor)


def soltar_aninhados(valor, _vistos=None, _fundo=0):
    """Quem solta, solta o que possuía — o 'drop glue'.

    Um dono que guarda outro dono é dono dos dois: soltar o de fora e
    deixar o de dentro aberto é exatamente o vazamento que esta peça
    existe para evitar. É também o que faz um ciclo de referências
    FORTES aparecer como ele é — ninguém chega a zero — em vez de sumir
    num silêncio.
    """
    if _fundo > 6 or valor is None:
        return
    _vistos = set() if _vistos is None else _vistos
    if id(valor) in _vistos:
        return
    _vistos.add(id(valor))
    if isinstance(valor, (Dono, Compartilhado)):
        valor.soltar()
        return
    itens = ()
    if isinstance(valor, dict):
        itens = list(valor.values())
    elif isinstance(valor, (list, tuple, set, frozenset)):
        itens = list(valor)
    else:
        campos = getattr(valor, "fields", None) or getattr(valor, "values", None)
        if isinstance(campos, dict):
            itens = list(campos.values())
    for item in itens:
        soltar_aninhados(item, _vistos, _fundo + 1)


class Fraco:
    """Uma referência que NÃO segura — e é honesta sobre isso.

    Ela existe para o mesmo problema de sempre: o ciclo. Dois
    compartilhados que se apontam nunca chegam a zero, e o finalizador
    de nenhum dos dois roda. Uma das voltas tem de ser fraca.
    """

    __slots__ = ("_nucleo",)

    def __init__(self, compartilhado):
        self._nucleo = compartilhado._nucleo
        self._nucleo.fracas += 1

    def vivo(self):
        return self._nucleo.fortes > 0

    def obter(self):
        """`Talvez` do valor: `algo(…)` enquanto vive, `nada()` depois."""
        from .arcane_resultado import Talvez
        if self._nucleo.fortes <= 0:
            return Talvez(False)
        return Talvez(True, self._nucleo.valor)

    def promover(self):
        """Um dono forte de novo, se ainda houver valor. `void` se não."""
        if self._nucleo.fortes <= 0:
            return None
        return Compartilhado(_nucleo=self._nucleo)

    def __repr__(self):                                    # pragma: no cover
        return f"<fraco {'vivo' if self.vivo() else 'morto'}>"


class Escopo:
    """Vários recursos, uma saída — e a ordem INVERSA da entrada.

    É a forma prática do que uma linguagem com destrutores chama de
    *lifetime*: o recurso vive enquanto o escopo vive. A ordem importa e
    é a inversa de propósito — o que foi aberto por último costuma
    depender do que veio antes, e fechar na ordem da entrada quebraria a
    transação antes de a conexão dela sair.
    """

    __slots__ = ("_itens", "_solto", "_trava")

    def __init__(self):
        self._itens = []
        self._solto = False
        self._trava = threading.RLock()

    def guardar(self, alvo):
        """Entrega o recurso ao escopo, e o devolve para ser usado."""
        if self._solto:
            raise RuntimeError_(
                "este escopo já foi solto: o que entrar agora não sai mais.",
                0, 0, dica="abra outro escopo", doc="memoria/posse")
        with self._trava:
            self._itens.append(alvo)
        return alvo

    def dono(self, valor=None, ao_soltar=None, nome="valor"):
        """Cria o dono JÁ guardado — o caminho que não dá para esquecer."""
        return self.guardar(Dono(valor, ao_soltar, str(nome)))

    def quantos(self):
        return len(self._itens)

    def vivo(self):
        return not self._solto

    def soltar(self):
        """Solta tudo, do último para o primeiro. Erro num não para os outros."""
        with self._trava:
            if self._solto:
                return 0
            self._solto = True
            itens = list(reversed(self._itens))
            self._itens = []
        soltos, falhas = 0, []
        for item in itens:
            soltador = getattr(item, "soltar", None)
            if not callable(soltador):
                continue
            try:
                soltador()
                soltos += 1
            except Exception as erro:                      # noqa: BLE001
                # Um recurso que falha ao fechar não pode deixar os
                # outros abertos: é o mesmo raciocínio do 'defer'.
                falhas.append(erro)
        if falhas:
            raise RuntimeError_(
                f"{len(falhas)} recurso(s) falharam ao soltar; os demais "
                f"foram soltos assim mesmo.", 0, 0,
                nota=str(falhas[0]), doc="memoria/posse")
        return soltos

    def __repr__(self):                                    # pragma: no cover
        return f"<escopo {len(self._itens)} recurso(s)>"


# ═════════════════════════════════════════════════════════════
#  As portas de entrada
# ═════════════════════════════════════════════════════════════

def dono(valor=None, ao_soltar=None, nome="valor"):
    return Dono(valor, ao_soltar, str(nome))


def com(alvo, acao):
    """RAII: usa e SOLTA no fim — inclusive quando o corpo levanta.

    É o `defer` da linguagem aplicado a um dono, num lugar só. Sem ele,
    metade dos recursos vaza pelo caminho de erro, que é justamente o
    caminho que ninguém testa.
    """
    try:
        if isinstance(alvo, Dono):
            return alvo.usar(acao)
        return acao(alvo.valor() if isinstance(alvo, Compartilhado) else alvo)
    finally:
        soltador = getattr(alvo, "soltar", None)
        if callable(soltador):
            soltador()


def celula(valor=None):
    return Celula(valor)


def escopo():
    """Um escopo que solta tudo o que recebeu, na ordem inversa."""
    return Escopo()


def com_escopo(acao):
    """Abre um escopo, roda o corpo e solta tudo — inclusive no erro."""
    alvo = Escopo()
    try:
        return acao(alvo)
    finally:
        alvo.soltar()


def compartilhado(valor=None, ao_soltar=None):
    return Compartilhado(valor, ao_soltar)


def atomico(valor=None, ao_soltar=None):
    """O mesmo do compartilhado, com a contagem válida entre threads."""
    return Compartilhado(valor, ao_soltar, atomico=True)


def fraco(alvo):
    if not isinstance(alvo, Compartilhado):
        raise RuntimeError_(
            "'fraco' precisa de um valor compartilhado: é a contagem dele "
            "que a referência fraca observa.", 0, 0,
            dica="P.fraco(P.compartilhado(valor))",
            doc="memoria/posse")
    return Fraco(alvo)


def e_dono(valor):
    return isinstance(valor, Dono)


def estado(alvo):
    """Um vault com o que a peça sabe sobre si — para log e depuração."""
    if isinstance(alvo, Dono):
        return {"especie": "dono", "estado": alvo._estado,
                "emprestimos": alvo._lendo + (1 if alvo._escrevendo else 0)}
    if isinstance(alvo, Compartilhado):
        return {"especie": "compartilhado", "fortes": alvo.contar(),
                "fracas": alvo.fracas(), "vivo": alvo.vivo()}
    if isinstance(alvo, Celula):
        return {"especie": "celula", "emprestimos": alvo.emprestimos()}
    if isinstance(alvo, Fraco):
        return {"especie": "fraco", "vivo": alvo.vivo()}
    return {"especie": "outro", "vivo": True}


class ArcanePosse:
    """O dicionário que `adopt Arcane.Posse` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Posse",

            # ── posse exclusiva ──
            "dono": dono,
            "com": com,
            "Dono": Dono,

            # ── escopo ──
            "escopo": escopo,
            "com_escopo": com_escopo,
            "Escopo": Escopo,

            # ── empréstimo ──
            "celula": celula,
            "Celula": Celula,
            "Emprestimo": Emprestimo,

            # ── posse compartilhada ──
            "compartilhado": compartilhado,
            "atomico": atomico,
            "fraco": fraco,
            "Compartilhado": Compartilhado,
            "Fraco": Fraco,

            # ── inspeção ──
            "e_dono": e_dono,
            "estado": estado,
        }
