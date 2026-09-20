# -*- coding: utf-8 -*-
"""Arcane.Stm — memória transacional: escritas que acontecem JUNTAS.

O que faltava
-------------
O repositório já mediu o problema: duas threads somando na mesma
variável entregaram **40.425 de 80.000**, em silêncio. As respostas que
existiam eram `mutex` — e a disciplina de lembrar dele em todo lugar — e
`contador`, que só serve para contar.

O que nenhuma das duas resolve é **compor**. Transferir de uma conta
para outra são duas escritas que precisam acontecer juntas ou não
acontecer:

    T.atomicamente(transferir)       # as duas, ou nenhuma

Com mutex, isso vira ordem de aquisição; ordem errada é impasse, e
"pegue sempre na mesma ordem" é uma regra que não dá para verificar.
Numa transação não há ordem a lembrar: o que existe é o conjunto do que
foi lido e do que foi escrito.

Como funciona
-------------
Otimismo com validação, no modelo clássico:

1. a transação lê e escreve num **rascunho** (nada sai dali);
2. no fim, sob uma trava curta, ela confere se alguma variável que leu
   mudou de versão desde que a leitura aconteceu;
3. se mudou, **descarta tudo e tenta de novo** — o conflito custa
   trabalho repetido, e não um dado errado;
4. se não mudou, publica as escritas de uma vez e acorda quem espera.

Quatro decisões
---------------
1. **A transação enxerga a própria escrita.** `ler` depois de `escrever`
   devolve o que ela mesma escreveu, e não o valor publicado — sem isso
   o código de dentro leria um valor que já não vale, e a transação
   mentiria para si mesma.

2. **`retentar()` não é um laço ocupado.** Ele abandona a transação e
   **espera** até que alguma variável lida por ela mude. Um `persist`
   girando gastaria um núcleo para não fazer nada.

3. **O erro de dentro desfaz tudo e sobe.** Uma transação que falha no
   meio não deixa metade escrita — é a atomicidade, e é a razão de a
   peça existir. O erro não é engolido: quem chamou decide.

4. **Ler ou escrever fora de uma transação é recusado.** Uma variável
   transacional lida solta seria um valor sem garantia nenhuma, com
   cara de garantia. Para ler sem transação existe `valor(var)`, que diz
   no nome que é uma foto.

5. **Otimismo puro não garante PROGRESSO, e por isso há um plano B.**
   Validar-e-repetir garante que ninguém escreve errado; não garante que
   alguém termina. Uma transação lenta que disputa a mesma variável com
   transações rápidas perde a corrida toda vez: as outras avançam, ela
   repete para sempre. É inanição (*livelock*), e ela não aparece na
   máquina de quem desenvolve — aparece onde há mais threads que
   núcleos.

   Foi o que o CI mostrou: 40 threads somando 200 vezes na mesma
   variável, em runner de poucos núcleos, estouraram as **mil**
   tentativas nos quatro Pythons do Linux. Aqui, com dez núcleos, a
   transação mais azarada precisou de 15.

   Depois de `_PESSIMISTA` tentativas perdidas, a transação passa a
   rodar **segurando a trava do commit**: ninguém mais publica enquanto
   ela roda, a validação não tem como falhar, e ela termina. É a
   *transação irrevogável* dos STM que levam progresso a sério.

   O preço é real e está documentado: enquanto uma transação
   pessimista roda, as outras esperam para confirmar. Por isso ela é o
   fim da fila, e não o começo — quem não disputa nada nunca chega lá,
   e a passagem é contada em `estatisticas()`.
"""

import threading

from ..errors import RuntimeError_

#: O estado da transação da thread atual. Cada thread tem o seu: uma
#: transação é sempre de quem a abriu.
_LOCAL = threading.local()

#: A trava do commit. Curta de propósito: ela protege a VALIDAÇÃO e a
#: publicação, e não o corpo da transação — se protegesse o corpo, isto
#: seria um mutex global com outro nome.
_TRAVA = threading.RLock()
_MUDOU = threading.Condition(_TRAVA)

_ESTATISTICAS = {"confirmadas": 0, "conflitos": 0, "retentativas": 0,
                 "esperas": 0, "pessimistas": 0}

#: Quantas corridas perdidas antes de a transação parar de apostar.
#: Dezesseis é alto o bastante para que o caminho rápido seja a regra
#: (uma disputa normal fecha em uma ou duas) e baixo o bastante para
#: que a inanição termine em milissegundos, e não em mil repetições do
#: corpo inteiro.
_PESSIMISTA = 16


class _PedirRetentativa(BaseException):
    """'retentar()': a transação não pode seguir com o que existe agora.

    Deriva de BaseException pelo mesmo motivo de `halt` e `skip`: o
    interpretador embrulha toda `Exception` num erro de execução, e isto
    não é um erro — é um pedido de espera.
    """


class Variavel:
    """Uma variável transacional: valor, versão e quem a espera."""

    __slots__ = ("_valor", "_versao", "_nome")

    def __init__(self, valor=None, nome=""):
        self._valor = valor
        self._versao = 0
        self._nome = str(nome or "")

    def nome(self):
        return self._nome

    def versao(self):
        return self._versao

    def valor(self):
        """Uma FOTO, sem garantia nenhuma — e o nome diz isso."""
        return self._valor

    def __repr__(self):                                    # pragma: no cover
        return f"<variavel v{self._versao}>"


class _Transacao:
    """O rascunho: o que foi lido (com a versão) e o que foi escrito."""

    __slots__ = ("lidas", "escritas", "profundidade")

    def __init__(self):
        self.lidas = {}
        self.escritas = {}
        self.profundidade = 1


def _atual():
    return getattr(_LOCAL, "transacao", None)


def _exigir_transacao(o_que):
    transacao = _atual()
    if transacao is None:
        raise RuntimeError_(
            f"'{o_que}' só vale dentro de uma transação.", 0, 0,
            nota="fora dela, o valor não teria garantia nenhuma — com cara "
                 "de garantia",
            dica="T.atomicamente(acao), ou T.valor(var) para uma foto sem "
                 "promessa",
            doc="concorrencia/stm")
    return transacao


def variavel(valor=None, nome=""):
    return Variavel(valor, nome)


def ler(var):
    """O valor dentro da transação — inclusive o que ela mesma escreveu."""
    transacao = _exigir_transacao("ler")
    _exigir_variavel(var, "ler")
    if var in transacao.escritas:
        return transacao.escritas[var]
    if var not in transacao.lidas:
        # A versão é guardada JUNTO: é ela que a validação compara.
        transacao.lidas[var] = var._versao
    return var._valor


def escrever(var, valor):
    """Escreve no rascunho. Nada sai dali antes do commit."""
    transacao = _exigir_transacao("escrever")
    _exigir_variavel(var, "escrever")
    transacao.escritas[var] = valor
    return None


def modificar(var, acao):
    """`escrever(var, acao(ler(var)))` — a forma que não esquece o ler."""
    return escrever(var, acao(ler(var)))


def _exigir_variavel(var, o_que):
    if not isinstance(var, Variavel):
        from ..interpreter import DFAction
        interp = DFAction._interpreter
        tipo = interp._type_of(var) if interp is not None else type(var).__name__
        raise RuntimeError_(
            f"'{o_que}' precisa de uma variável transacional, e recebeu {tipo}.",
            0, 0, dica="crie com T.variavel(valor)", doc="concorrencia/stm")


def retentar():
    """Desiste desta tentativa e ESPERA alguma variável lida mudar."""
    _exigir_transacao("retentar")
    raise _PedirRetentativa()


def ou_entao(primeira, segunda):
    """Tenta a primeira; se ela pedir para esperar, tenta a segunda.

    É a composição que um mutex não tem: duas operações bloqueantes
    viram uma que escolhe a que estiver pronta.
    """
    transacao = _exigir_transacao("ou_entao")
    lidas_antes = dict(transacao.lidas)
    escritas_antes = dict(transacao.escritas)
    try:
        return primeira()
    except _PedirRetentativa:
        # O rascunho da primeira é descartado; o que ela LEU continua
        # valendo para a espera, senão 'ou_entao' esqueceria o que
        # observou e nunca acordaria por causa dela.
        transacao.escritas = escritas_antes
        transacao.lidas.update(lidas_antes)
        return segunda()


def atomicamente(acao, tentativas=1000):
    """Roda a ação como uma transação: tudo, ou nada.

    Aninhar é achatar: uma transação dentro de outra é a MESMA
    transação. Sem isso, duas ações que já são transacionais não
    poderiam ser compostas numa terceira — que é o ponto da peça.
    """
    de_fora = _atual()
    if de_fora is not None:
        de_fora.profundidade += 1
        try:
            return acao()
        finally:
            de_fora.profundidade -= 1

    tentativa = 0
    while True:
        tentativa += 1
        if tentativa > tentativas:
            raise RuntimeError_(
                f"a transação não fechou em {tentativas} tentativas: há "
                f"conflito demais nesta variável.", 0, 0,
                dica="divida o estado em variáveis menores, ou faça menos "
                     "trabalho dentro da transação",
                doc="concorrencia/stm")

        # Depois de perder muitas corridas, esta transação para de
        # apostar: ela roda segurando a trava do commit, e ninguém
        # publica no meio dela. É o que transforma "talvez termine" em
        # "termina" — ver a decisão 5, no topo.
        pessimista = tentativa > _PESSIMISTA
        if pessimista:
            _ESTATISTICAS["pessimistas"] += 1
            _TRAVA.acquire()
        try:
            transacao = _Transacao()
            _LOCAL.transacao = transacao
            esperar_por = None
            confirmou = False
            try:
                # Atomicidade: se o corpo levantar, o rascunho morre com
                # ele e o erro sobe — o 'finally' abaixo só desfaz a
                # transação da thread.
                resultado = acao()
            except _PedirRetentativa:
                esperar_por = dict(transacao.lidas)
            finally:
                if _atual() is transacao:
                    _LOCAL.transacao = None
            if esperar_por is None:
                confirmou = _confirmar(transacao)
        finally:
            # 'retentar()' dentro de uma transação pessimista sairia
            # daqui segurando a trava, e a espera por uma mudança que
            # depende dela seria um impasse.
            if pessimista:
                _TRAVA.release()

        if esperar_por is not None:
            _ESTATISTICAS["esperas"] += 1
            _esperar_mudanca(esperar_por)
            continue

        if confirmou:
            return resultado
        _ESTATISTICAS["conflitos"] += 1
        _ESTATISTICAS["retentativas"] += 1


def _confirmar(transacao):
    """Valida o que foi lido e publica o que foi escrito — sob a trava."""
    with _TRAVA:
        for var, versao in transacao.lidas.items():
            if var._versao != versao:
                return False
        for var, valor in transacao.escritas.items():
            var._valor = valor
            var._versao += 1
        _ESTATISTICAS["confirmadas"] += 1
        if transacao.escritas:
            _MUDOU.notify_all()
    return True


def _esperar_mudanca(lidas, prazo=5.0):
    """Dorme até alguma das variáveis lidas mudar de versão."""
    with _TRAVA:
        if any(var._versao != versao for var, versao in lidas.items()):
            return
        _MUDOU.wait(prazo)


def valor(var):
    """Uma FOTO do valor, fora de transação. Sem promessa nenhuma."""
    _exigir_variavel(var, "valor")
    return var._valor


def definir(var, novo):
    """Escreve numa transação de uma escrita só — o atalho honesto."""
    return atomicamente(lambda: escrever(var, novo))


def estatisticas():
    """Quantas confirmaram, quantas conflitaram, quantas esperaram."""
    with _TRAVA:
        return dict(_ESTATISTICAS)


def zerar_estatisticas():
    with _TRAVA:
        for chave in _ESTATISTICAS:
            _ESTATISTICAS[chave] = 0
    return True


def em_transacao():
    """Estamos dentro de uma transação agora?"""
    return _atual() is not None


class ArcaneStm:
    """O dicionário que `adopt Arcane.Stm` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Stm",

            "variavel": variavel,
            "Variavel": Variavel,

            "atomicamente": atomicamente,
            "ler": ler,
            "escrever": escrever,
            "modificar": modificar,
            "valor": valor,
            "definir": definir,

            "retentar": retentar,
            "ou_entao": ou_entao,
            "em_transacao": em_transacao,

            "estatisticas": estatisticas,
            "zerar_estatisticas": zerar_estatisticas,
        }
