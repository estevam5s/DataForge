# -*- coding: utf-8 -*-
"""Crucible — a segunda metade: o que um teste precisa alem de comparar.

O `crucible.py` responde "o valor e o esperado?" com 59 matchers, e
responde bem. Este arquivo responde as perguntas que sobram, e que
custam caro justamente porque nao ha matcher para elas:

    o que MUDOU?          `to_change` — a diferenca entre antes e depois
    quem foi CHAMADO?     os matchers de dublê
    e sob concorrencia?   `corrida` — duas threads na mesma variavel
    e sem a rede?         `servidor_falso` — um HTTP que voce controla
    e amanha?             `relogio` — o tempo que anda quando voce manda
    e o teste TESTA?      `mutar` — quebra o codigo e ve se alguem acusa

Por que num arquivo separado
-----------------------------
`crucible.py` tem 2.200 linhas e uma responsabilidade clara: registrar
suites, rodar trials e comparar valores. O que esta aqui sao
**ferramentas de cenario** — elas montam o mundo em que o trial roda, e
nao comparam nada. Misturar as duas coisas faria a classe `Expectativa`
crescer sem parar e esconderia a fronteira.

Os matchers novos sao acrescentados a `Expectativa` no fim do arquivo,
pelo mesmo motivo que `render_extra.py` escreve em `_DESENHO`: quem
procura um matcher procura na classe, e ela continua sendo o lugar.
"""

import io
import json
import os
import re
import sys
import threading
import time

from . import crucible as C

Expectativa = C.Expectativa
FalhaDeExpectativa = C.FalhaDeExpectativa
NADA = C.NADA
_texto = C._texto


def _erro(mensagem, nota="", dica="", doc="crucible"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


# ═══════════════════════════════════════════════════════════
#  O que mudou
# ═══════════════════════════════════════════════════════════

class Mudanca:
    """O resultado de `expect(acao).to_change(leitor)`.

    Ele existe para que `por`, `de_para` e `em` se encadeiem depois da
    cobranca — e nao antes. A ordem importa: `to_change(saldo).por(10)`
    le como se fala, e `to_change_by(saldo, 10)` nao.
    """

    __slots__ = ("antes", "depois", "expectativa")

    def __init__(self, antes, depois, expectativa):
        self.antes = antes
        self.depois = depois
        self.expectativa = expectativa

    def por(self, quanto):
        """A diferenca exata. Aceita numero — para texto, use `de_para`."""
        real = self.depois - self.antes
        if real != quanto:
            raise FalhaDeExpectativa(
                f"devia mudar em {_texto(quanto)}, mas mudou em "
                f"{_texto(real)} (de {_texto(self.antes)} para "
                f"{_texto(self.depois)})",
                esperado=quanto, obtido=real)
        return self

    def de_para(self, de, para):
        if self.antes != de:
            raise FalhaDeExpectativa(
                f"devia comecar em {_texto(de)}, mas comecou em "
                f"{_texto(self.antes)}", esperado=de, obtido=self.antes)
        if self.depois != para:
            raise FalhaDeExpectativa(
                f"devia terminar em {_texto(para)}, mas terminou em "
                f"{_texto(self.depois)}", esperado=para, obtido=self.depois)
        return self

    def para(self, valor):
        return self.de_para(self.antes, valor)

    def em(self, quanto):
        """Apelido de `por`, para quem le 'mudou em 10'."""
        return self.por(quanto)

    def __repr__(self):
        return f"<mudanca {_texto(self.antes)} → {_texto(self.depois)}>"


def _ler(leitor):
    """O valor de agora. Aceita uma acao, ou um valor ja pronto."""
    return leitor() if callable(leitor) else leitor


def to_change(self, leitor):
    """Roda a acao sob teste e cobra que o leitor tenha mudado.

        expect(lambda => conta.depositar(10)).to_change(
            lambda => conta.saldo()).por(10)

    E o matcher que mais falta num framework de teste, porque ele cobre
    o caso que um `assert` simples cobre mal: o efeito colateral. Sem
    ele, escreve-se `antes := saldo()`, a acao, `depois := saldo()` e
    um assert — quatro linhas em que a do meio pode falhar em silencio.
    """
    if not callable(self.valor):
        raise _erro(
            "'to_change' espera uma ACAO, e nao um valor.",
            nota="ele precisa rodar alguma coisa para ver o que mudou",
            dica="expect(lambda => conta.depositar(10)).to_change(...)")
    # O 'negado' e lido ANTES de ser zerado: zerar primeiro e depois
    # consulta-lo deixa o ramo da negacao morto, e a mensagem de "nao
    # devia mudar" nunca sairia.
    negado = self._negado
    self._negado = False
    antes = _ler(leitor)
    self.valor()
    depois = _ler(leitor)
    mudou = antes != depois
    if mudou == negado:
        if negado:
            raise FalhaDeExpectativa(
                f"nao devia mudar, mas foi de {_texto(antes)} para "
                f"{_texto(depois)}", esperado=antes, obtido=depois)
        raise FalhaDeExpectativa(
            f"devia mudar, mas continuou em {_texto(antes)}",
            esperado="uma mudanca", obtido=antes)
    return Mudanca(antes, depois, self)


def to_not_change(self, leitor):
    """O contrario, com mensagem propria.

    `nao().to_change(...)` funcionaria e devolveria uma `Mudanca` sem
    sentido — encadear `.por(...)` depois de "nao mudou" nao quer dizer
    nada. Por isso este e um matcher separado.
    """
    if not callable(self.valor):
        raise _erro("'to_not_change' espera uma ACAO, e nao um valor.",
                    dica="expect(lambda => ler(x)).to_not_change(...)")
    antes = _ler(leitor)
    self.valor()
    depois = _ler(leitor)
    if antes != depois:
        raise FalhaDeExpectativa(
            f"nao devia mudar, mas foi de {_texto(antes)} para "
            f"{_texto(depois)}", esperado=antes, obtido=depois)
    self._negado = False
    return self


# ═══════════════════════════════════════════════════════════
#  Dublês
# ═══════════════════════════════════════════════════════════

def _chamadas_de(alvo):
    chamadas = getattr(alvo, "chamadas", None)
    if chamadas is None:
        raise _erro(
            "este matcher so vale para um dublê.",
            nota="dublês vem de Crucible.spy, .stub ou .mock",
            dica="expect(Crucible.spy(x)).to_have_been_called()")
    return list(chamadas)


def _nomes(chamadas):
    return [c[0] for c in chamadas]


def to_have_been_called(self, metodo=""):
    chamadas = _chamadas_de(self.valor)
    alvo = [c for c in chamadas if not metodo or c[0] == metodo]
    como = f"'{metodo}' " if metodo else ""
    return self._cobrar(
        bool(alvo),
        f"ter sido chamado {como}ao menos uma vez — chamaram "
        f"{_texto(_nomes(chamadas)) if chamadas else 'nada'}")


def to_have_been_called_times(self, quantas, metodo=""):
    chamadas = _chamadas_de(self.valor)
    alvo = [c for c in chamadas if not metodo or c[0] == metodo]
    como = f"'{metodo}' " if metodo else ""
    return self._cobrar(
        len(alvo) == int(quantas),
        f"ter sido chamado {como}{quantas} vez(es), e foi {len(alvo)}",
        esperado=quantas)


def to_have_been_called_once(self, metodo=""):
    """O caso mais comum, e o que mais engana.

    "Foi chamado" passa com tres chamadas, e tres chamadas de
    `cobrar()` e um bug de cobranca duplicada — o tipo que ninguem
    perdoa.
    """
    return to_have_been_called_times(self, 1, metodo)


def to_have_been_called_with(self, *args, **kwargs):
    """Alguma chamada teve exatamente estes argumentos."""
    chamadas = _chamadas_de(self.valor)
    procurado = (list(args), dict(kwargs))
    achou = any([c[1], c[2]] == [procurado[0], procurado[1]]
                for c in chamadas)
    return self._cobrar(
        achou,
        f"ter sido chamado com {_texto(list(args))} — as chamadas foram "
        f"{_texto([[c[0], c[1]] for c in chamadas])}",
        esperado=list(args))


def to_have_been_called_in_order(self, *metodos):
    """Os metodos aconteceram nesta ordem — com outros no meio, tudo bem.

    Cobrar a sequencia EXATA quebraria a cada chamada nova que o codigo
    passasse a fazer, e um teste que quebra sem o comportamento mudar
    e um teste que sera apagado.
    """
    vistos = _nomes(_chamadas_de(self.valor))
    procurados = [str(m) for m in metodos]
    posicao = 0
    for nome in vistos:
        if posicao < len(procurados) and nome == procurados[posicao]:
            posicao += 1
    return self._cobrar(
        posicao == len(procurados),
        f"ter chamado {_texto(procurados)} nesta ordem — a ordem foi "
        f"{_texto(vistos)}",
        esperado=procurados)


def to_have_never_been_called(self, metodo=""):
    chamadas = _chamadas_de(self.valor)
    alvo = [c for c in chamadas if not metodo or c[0] == metodo]
    como = f"'{metodo}' " if metodo else ""
    return self._cobrar(
        not alvo, f"nunca ter sido chamado {como}— mas foi {len(alvo)} vez(es)")


# ═══════════════════════════════════════════════════════════
#  Forma e conteudo
# ═══════════════════════════════════════════════════════════

def to_match_vault(self, parcial):
    """As chaves dadas batem; as outras sao ignoradas.

        expect(resposta).to_match_vault({"status": 200})

    Cobrar o vault inteiro obriga a escrever no teste campos que ele
    nao testa — e no dia em que um campo novo aparece, dez testes
    quebram sem nenhum comportamento ter mudado.
    """
    if not isinstance(self.valor, dict):
        return self._cobrar(False, f"ser um vault, e e {_texto(self.valor)}")
    faltando = {}
    for chave, esperado in (parcial or {}).items():
        atual = self.valor.get(chave, NADA)
        if atual is NADA or atual != esperado:
            faltando[chave] = {"esperava": esperado,
                               "veio": None if atual is NADA else atual}
    return self._cobrar(
        not faltando,
        f"casar com {_texto(parcial)} — difere em {_texto(faltando)}",
        esperado=parcial)


def to_have_shape(self, forma):
    """Cada chave tem o TIPO dito, sem olhar o valor.

        expect(linha).to_have_shape({"id": "Integer", "nome": "String"})

    E o que se cobra de um dado que vem de fora: o valor muda a cada
    execucao, e a forma nao.
    """
    if not isinstance(self.valor, dict):
        return self._cobrar(False, f"ser um vault, e e {_texto(self.valor)}")
    erradas = {}
    for chave, tipo in (forma or {}).items():
        if chave not in self.valor:
            erradas[chave] = f"falta (esperava {tipo})"
            continue
        real = C._tipo(self.valor[chave])
        if real != str(tipo):
            erradas[chave] = f"{real}, esperava {tipo}"
    return self._cobrar(
        not erradas,
        f"ter a forma {_texto(forma)} — difere em {_texto(erradas)}",
        esperado=forma)


def to_satisfy(self, condicao, descricao=""):
    """A saida de emergencia: qualquer regra que voce escreva.

    Ela existe para que ninguem precise abandonar `expect` por causa de
    uma cobranca que nenhum matcher cobre — e volte ao `assert` nu, que
    nao diz o que veio.
    """
    try:
        passou = bool(condicao(self.valor))
    except Exception as erro:                                # noqa: BLE001
        raise FalhaDeExpectativa(
            f"a condicao de 'to_satisfy' estourou: {erro}",
            obtido=self.valor)
    return self._cobrar(
        passou, descricao or "satisfazer a condicao dada")


def to_be_one_of(self, opcoes):
    lista = list(opcoes or [])
    return self._cobrar(
        self.valor in lista,
        f"ser um de {_texto(lista)}, e veio {_texto(self.valor)}",
        esperado=lista)


def to_contain_exactly(self, itens):
    """Os mesmos itens, em qualquer ordem, sem sobrar nem faltar."""
    try:
        atual = sorted(self.valor, key=_texto)
        esperado = sorted(list(itens or []), key=_texto)
    except TypeError:
        atual, esperado = list(self.valor), list(itens or [])
    faltando = [i for i in esperado if i not in atual]
    sobrando = [i for i in atual if i not in esperado]
    return self._cobrar(
        not faltando and not sobrando,
        f"conter exatamente {_texto(esperado)} — falta {_texto(faltando)}, "
        f"sobra {_texto(sobrando)}",
        esperado=esperado)


def to_be_subset_of(self, maior):
    fora = [i for i in self.valor if i not in (maior or [])]
    return self._cobrar(
        not fora, f"estar contido — mas {_texto(fora)} nao esta la")


def to_be_ordered_by(self, campo, decrescente=False):
    """Ordenado por um campo — de vault, record ou instancia."""
    from .arcane_collections import _campo_de

    valores = [_campo_de(i, campo) for i in self.valor]
    esperado = sorted(valores, reverse=bool(decrescente))
    return self._cobrar(
        valores == esperado,
        f"estar ordenado por '{campo}' — a ordem veio {_texto(valores)}",
        esperado=esperado)


def to_round_trip(self, ida, volta):
    """Serializar e desserializar devolve o mesmo valor.

        expect(pedido).to_round_trip(Json.stringify, Json.parse)

    E a propriedade que todo formato promete e quase nenhum cumpre na
    borda: `void`, texto vazio, numero com virgula, data.
    """
    try:
        recuperado = volta(ida(self.valor))
    except Exception as erro:                                # noqa: BLE001
        raise FalhaDeExpectativa(
            f"a ida e volta estourou: {erro}", obtido=self.valor)
    return self._cobrar(
        recuperado == self.valor,
        f"voltar igual da serializacao — voltou {_texto(recuperado)}",
        esperado=self.valor)


def to_be_within_percent(self, esperado, percentual):
    """Perto o bastante, em proporcao — e nao em valor absoluto.

    Uma tolerancia absoluta serve mal a grandezas de escalas
    diferentes: 0,01 e muito para um percentual e nada para um saldo.
    """
    try:
        alvo = float(esperado)
        veio = float(self.valor)
    except (TypeError, ValueError):
        return self._cobrar(False, f"ser um numero, e e {_texto(self.valor)}")
    if alvo == 0:
        return self._cobrar(veio == 0,
                            f"ser zero, e veio {_texto(veio)}", esperado=0)
    desvio = abs(veio - alvo) / abs(alvo) * 100
    return self._cobrar(
        desvio <= float(percentual),
        f"estar a {percentual}% de {_texto(alvo)} — veio {_texto(veio)}, "
        f"{desvio:.2f}% de diferenca",
        esperado=alvo)


def to_raise_matching(self, padrao):
    """Levanta um erro cuja MENSAGEM casa com a expressao regular.

    Cobrar a mensagem inteira quebra na primeira melhoria do texto; um
    trecho estavel — o nome do campo, o codigo — nao quebra.
    """
    if not callable(self.valor):
        return self._cobrar(False, "ser uma acao, para poder ser chamada")
    try:
        self.valor()
    except Exception as erro:                                # noqa: BLE001
        mensagem = getattr(erro, "message", None) or str(erro)
        return self._cobrar(
            bool(re.search(str(padrao), mensagem)),
            f"levantar um erro casando /{padrao}/ — a mensagem foi "
            f"'{mensagem}'",
            esperado=str(padrao))
    return self._cobrar(False, f"levantar um erro casando /{padrao}/, "
                               f"mas nada foi levantado")


def _colher(fonte, quantos, limite):
    """Os primeiros valores de um percorrivel, sem travar.

    O teto existe porque um `stream action` infinito e comum na
    linguagem — e comparar com ele travaria o teste em vez de falhar,
    que e o pior desfecho de um framework de teste.
    """
    saida = []
    for valor in fonte:
        saida.append(valor)
        if len(saida) >= min(quantos, limite):
            break
    return saida


def to_emit(self, esperados, limite=1000):
    """Um gerador produz EXATAMENTE esta sequencia, e para.

    Para um gerador infinito — que e comum na linguagem —, a pergunta
    util e outra, e ela tem outro matcher: `to_emit_first`. Fundir as
    duas faria `to_emit([0, 1, 2])` passar sobre uma serie que nunca
    acaba, e a afirmacao "produz [0,1,2]" seria falsa.
    """
    alvo = list(esperados or [])
    fonte = self.valor() if callable(self.valor) else self.valor
    try:
        # Um a mais do que o esperado: e o que distingue "emitiu isto"
        # de "comecou com isto".
        saida = _colher(fonte, len(alvo) + 1, limite)
    except TypeError:
        return self._cobrar(False, f"ser percorrivel, e e {_texto(self.valor)}")
    return self._cobrar(
        saida == alvo,
        f"emitir {_texto(alvo)}, e emitiu {_texto(saida)}"
        + (" (e continuou)" if len(saida) > len(alvo) else ""),
        esperado=alvo)


def to_emit_first(self, esperados, limite=1000):
    """Os PRIMEIROS valores sao estes — o que sobra nao importa.

    E a forma de cobrar um `stream action` infinito, que na linguagem
    e o caso comum: `fib()` nao acaba, e o que se quer saber e se os
    oito primeiros estao certos.
    """
    alvo = list(esperados or [])
    fonte = self.valor() if callable(self.valor) else self.valor
    try:
        saida = _colher(fonte, len(alvo), limite)
    except TypeError:
        return self._cobrar(False, f"ser percorrivel, e e {_texto(self.valor)}")
    return self._cobrar(
        saida == alvo,
        f"comecar emitindo {_texto(alvo)}, e comecou com {_texto(saida)}",
        esperado=alvo)


# ═══════════════════════════════════════════════════════════
#  Concorrencia
# ═══════════════════════════════════════════════════════════

class Corrida:
    """O resultado de `Crucible.corrida(...)`."""

    __slots__ = ("esperado", "obtido", "threads", "voltas", "erros", "ms")

    def __init__(self, esperado, obtido, threads, voltas, erros, ms):
        self.esperado = esperado
        self.obtido = obtido
        self.threads = threads
        self.voltas = voltas
        self.erros = erros
        self.ms = ms

    def perdeu(self):
        return self.esperado != self.obtido

    def perdidas(self):
        return self.esperado - self.obtido

    def para_vault(self):
        return {"esperado": self.esperado, "obtido": self.obtido,
                "perdidas": self.perdidas(), "threads": self.threads,
                "voltas": self.voltas, "erros": list(self.erros),
                "ms": round(self.ms, 2)}

    def __repr__(self):
        return (f"<corrida {self.obtido}/{self.esperado} em "
                f"{self.threads} thread(s)>")


def corrida(acao, threads=4, voltas=5000, leitor=None, esperado=None):
    """Roda a acao em N threads e diz quantas atualizacoes se perderam.

        r := Crucible.corrida(lambda => contador.somar(),
                              threads := 4, voltas := 5000,
                              leitor := lambda => contador.valor())
        expect(r.perdeu()).to_be_false()

    Por que isto existe
    -------------------
    A linguagem **nao sincroniza sozinha**, e isso esta documentado:
    duas threads escrevendo no mesmo nome perdem atualizacoes, em
    silencio. O `check` avisa sobre o padrao, mas avisar nao e provar —
    e um teste que roda a acao uma vez por thread nao detecta nada,
    porque a janela de corrida e estreita.

    Este ajudante abre a janela de proposito: as threads comecam juntas
    (uma barreira), e cada uma repete milhares de vezes. O que sai e um
    numero, e nao uma impressao.
    """
    if not callable(acao):
        raise _erro("'corrida' espera uma acao para repetir.")
    quantas = max(1, int(threads))
    repeticoes = max(1, int(voltas))
    erros = []
    largada = threading.Barrier(quantas)

    def trabalhar():
        try:
            # A barreira e o ponto: sem ela, a primeira thread costuma
            # terminar antes de a ultima comecar, e o teste passa
            # justamente no codigo que tem a corrida.
            largada.wait(timeout=10)
        except threading.BrokenBarrierError:
            pass
        for _ in range(repeticoes):
            try:
                acao()
            except Exception as erro:                        # noqa: BLE001
                erros.append(str(erro))
                return

    comeco = time.perf_counter()
    linhas = [threading.Thread(target=trabalhar, daemon=True)
              for _ in range(quantas)]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join(timeout=120)
    decorrido = (time.perf_counter() - comeco) * 1000

    total = quantas * repeticoes if esperado is None else esperado
    obtido = _ler(leitor) if leitor is not None else total
    return Corrida(total, obtido, quantas, repeticoes, erros[:10], decorrido)


def determinismo(acao, vezes=5):
    """Roda a acao N vezes e cobra que a saida seja sempre a mesma.

    E a propriedade que um relatorio precisa ter e que quase nada tem:
    um `id()` na chave de um cache, uma ordem de dicionario, um
    `random` sem semente — os tres passam no teste que roda uma vez.
    """
    if not callable(acao):
        raise _erro("'determinismo' espera uma acao para repetir.")
    saidas = []
    for _ in range(max(2, int(vezes))):
        saidas.append(_congelar(acao()))
    primeiro = saidas[0]
    iguais = all(s == primeiro for s in saidas)
    return {"estavel": iguais, "vezes": len(saidas),
            "distintas": len({_texto(s) for s in saidas}),
            "primeira": primeiro,
            "diferente": next((s for s in saidas if s != primeiro), None)}


def _congelar(valor):
    """Uma foto comparavel do valor, para o caso de ele ser mutavel."""
    try:
        return json.dumps(_serializavel(valor), sort_keys=True,
                          ensure_ascii=False)
    except (TypeError, ValueError):
        return _texto(valor)


def _serializavel(valor):
    if isinstance(valor, dict):
        return {str(k): _serializavel(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple, set)):
        return [_serializavel(v) for v in valor]
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    if hasattr(valor, "fields"):
        return _serializavel(dict(valor.fields))
    return _texto(valor)


# ═══════════════════════════════════════════════════════════
#  O relogio
# ═══════════════════════════════════════════════════════════

class Relogio:
    """Um tempo que so anda quando voce manda.

    `freeze_time` congela; este ANDA. A diferenca importa para testar
    o que depende de intervalo — um cache com validade, um recuo, um
    prazo — porque congelado eles nunca vencem, e com o relogio de
    verdade o teste precisa dormir.

        r := Crucible.relogio("2026-09-20T10:00:00")
        cache.guardar("x", 1)
        r.avancar(minutos := 31)
        expect(cache.obter("x")).to_be_void()
    """

    def __init__(self, inicio=None):
        self.agora = _instante(inicio)
        self._original = None
        self._trava = threading.RLock()

    def avancar(self, segundos=0, minutos=0, horas=0, dias=0):
        with self._trava:
            self.agora += (float(segundos) + float(minutos) * 60
                           + float(horas) * 3600 + float(dias) * 86400)
        return self.agora

    def voltar(self, segundos=0, minutos=0, horas=0, dias=0):
        return self.avancar(-float(segundos), -float(minutos),
                            -float(horas), -float(dias))

    def ir_para(self, quando):
        with self._trava:
            self.agora = _instante(quando)
        return self.agora

    def ligar(self):
        """Passa a valer para `time.time` e `time.monotonic`.

        E preciso desligar depois — `Crucible.com_relogio` faz os dois
        e e o caminho recomendado, porque um relogio ligado que vaza
        para o proximo trial envenena a suite inteira.
        """
        if self._original is not None:
            return self
        self._original = (time.time, time.monotonic)
        time.time = lambda: self.agora
        time.monotonic = lambda: self.agora
        return self

    def desligar(self):
        if self._original is None:
            return self
        time.time, time.monotonic = self._original
        self._original = None
        return self

    def __repr__(self):
        return f"<relogio {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.agora))}>"


def _instante(quando):
    if quando is None:
        return time.time()
    if isinstance(quando, (int, float)):
        return float(quando)
    texto = str(quando).strip().replace("T", " ")
    for forma in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return time.mktime(time.strptime(texto[:len(
                time.strftime(forma, time.gmtime(0)))], forma))
        except ValueError:
            continue
    raise _erro(f"nao entendi o instante '{quando}'.",
                nota="use '2026-09-20', '2026-09-20 10:30' ou um numero")


def relogio(inicio=None):
    return Relogio(inicio)


def com_relogio(acao, inicio=None):
    """Roda a acao com o relogio ligado, e desliga mesmo com falha.

    O `finally` nao e zelo: um relogio ligado que escapa de um trial
    que estourou faz TODOS os seguintes verem o tempo parado, e a
    suite passa a falhar em lugares que nao tem nada a ver.
    """
    r = Relogio(inicio).ligar()
    try:
        return acao(r)
    finally:
        r.desligar()


# ═══════════════════════════════════════════════════════════
#  Um servidor que voce controla
# ═══════════════════════════════════════════════════════════

class ServidorFalso:
    """Um HTTP de mentira, para testar quem CHAMA HTTP.

        s := Crucible.servidor_falso()
        s.responder("/precos", {"dolar": 5.4})
        s.falhar("/lento", 503, vezes := 2)
        cliente.buscar(s.url("/precos"))
        expect(s.pedidos("/precos")).to_have_length(1)

    Por que nao um dublê comum
    ---------------------------
    Um dublê substitui o cliente HTTP e prova que o codigo chamou um
    metodo. Isto sobe um socket de verdade e prova que o codigo fala
    HTTP direito — cabecalho, corpo, status, e o que ele faz com um
    503 ou um tempo esgotado. Sao perguntas diferentes, e a segunda e
    a que quebra em producao.
    """

    def __init__(self, porta=0):
        self.rotas = {}
        self.pedidos_recebidos = []
        self.atraso = 0.0
        self._servidor = None
        self._linha = None
        self.porta = int(porta)
        self._trava = threading.RLock()

    # ── programar ────────────────────────────────────────────

    def responder(self, caminho, corpo=None, status=200, cabecalhos=None,
                  tipo="application/json"):
        with self._trava:
            self.rotas.setdefault(str(caminho), []).append({
                "corpo": corpo, "status": int(status),
                "cabecalhos": dict(cabecalhos or {}), "tipo": tipo,
                "vezes": None})
        return self

    def falhar(self, caminho, status=500, vezes=None, corpo=None):
        """Responde com erro — `vezes` limita, para testar a retentativa.

        Sem o limite nao da para testar "falha duas vezes e na terceira
        funciona", que e o comportamento que um cliente com recuo
        promete e quase nunca tem teste.
        """
        with self._trava:
            self.rotas.setdefault(str(caminho), []).append({
                "corpo": corpo if corpo is not None else {"erro": status},
                "status": int(status), "cabecalhos": {},
                "tipo": "application/json",
                "vezes": None if vezes is None else int(vezes)})
        return self

    def demorar(self, segundos):
        self.atraso = float(segundos)
        return self

    # ── subir ────────────────────────────────────────────────

    def subir(self):
        import http.server

        dono = self

        class Tratador(http.server.BaseHTTPRequestHandler):
            def _atender(self):
                caminho = self.path.split("?")[0]
                tamanho = int(self.headers.get("Content-Length") or 0)
                corpo = self.rfile.read(tamanho) if tamanho else b""
                with dono._trava:
                    dono.pedidos_recebidos.append({
                        "metodo": self.command, "caminho": caminho,
                        "query": self.path[len(caminho) + 1:],
                        "corpo": corpo.decode("utf-8", "replace"),
                        "cabecalhos": {k.lower(): v
                                       for k, v in self.headers.items()}})
                    programadas = dono.rotas.get(caminho)
                    resposta = dono._proxima(programadas)
                if dono.atraso:
                    time.sleep(dono.atraso)
                if resposta is None:
                    resposta = {"corpo": {"erro": "sem rota"}, "status": 404,
                                "cabecalhos": {}, "tipo": "application/json"}
                dados = resposta["corpo"]
                if not isinstance(dados, (bytes, bytearray)):
                    dados = (json.dumps(dados, ensure_ascii=False).encode()
                             if resposta["tipo"].startswith("application/json")
                             else str(dados).encode())
                self.send_response(resposta["status"])
                self.send_header("Content-Type", resposta["tipo"])
                self.send_header("Content-Length", str(len(dados)))
                for chave, valor in resposta["cabecalhos"].items():
                    self.send_header(chave, str(valor))
                self.end_headers()
                self.wfile.write(dados)

            do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = _atender

            def log_message(self, *args):
                # Silencio: o log do http.server vai para stderr e
                # polui a saida de toda suite que usa este ajudante.
                pass

        # `_ServidorKiln`, e nao o `ThreadingHTTPServer` cru: o
        # `server_bind` do `http.server` chama `socket.getfqdn` entre o
        # `bind` e o `listen`, e numa maquina sem resolvedor reverso
        # alcancavel a porta fica LIGADA e NAO ESCUTANDO pelo tempo do
        # sistema. Quem conecta recebe recusa, e nao ha erro nenhum
        # para ver. Ha uma trava no repositorio cobrando esta classe.
        from .kiln import _ServidorKiln

        self._servidor = _ServidorKiln(("127.0.0.1", self.porta), Tratador)
        self.porta = self._servidor.server_address[1]
        self._linha = threading.Thread(target=self._servidor.serve_forever,
                                       daemon=True)
        self._linha.start()
        return self

    def _proxima(self, programadas):
        """A proxima resposta da fila; a ultima fica valendo para sempre.

        Sem isso, `responder` uma vez e chamar duas daria 404 na
        segunda — e o teste falharia por um motivo que nao e o que ele
        testa.
        """
        if not programadas:
            return None
        for item in programadas:
            if item["vezes"] is None:
                if len(programadas) > 1 and item is programadas[0] and \
                        any(p["vezes"] is not None for p in programadas[1:]):
                    continue
                return item
            if item["vezes"] > 0:
                item["vezes"] -= 1
                return item
        return programadas[-1]

    def url(self, caminho="/"):
        if self._servidor is None:
            self.subir()
        return f"http://127.0.0.1:{self.porta}{caminho}"

    # ── perguntar ────────────────────────────────────────────

    def pedidos(self, caminho=""):
        with self._trava:
            if not caminho:
                return list(self.pedidos_recebidos)
            return [p for p in self.pedidos_recebidos
                    if p["caminho"] == str(caminho)]

    def ultimo(self, caminho=""):
        recebidos = self.pedidos(caminho)
        return recebidos[-1] if recebidos else None

    def quantos(self, caminho=""):
        return len(self.pedidos(caminho))

    def limpar(self):
        with self._trava:
            self.pedidos_recebidos.clear()
        return self

    def parar(self):
        if self._servidor is not None:
            self._servidor.shutdown()
            self._servidor.server_close()
            self._servidor = None
        return self

    def __repr__(self):
        return f"<servidor falso :{self.porta}, {len(self.rotas)} rota(s)>"


def servidor_falso(porta=0):
    """Sobe um HTTP de mentira e devolve o controle dele."""
    return ServidorFalso(porta).subir()


# ═══════════════════════════════════════════════════════════
#  Contrato: um trait, muitas implementacoes
# ═══════════════════════════════════════════════════════════

def contrato(nome, casos):
    """Um conjunto de trials que vale para TODA implementacao de um trait.

        provas := Crucible.contrato("Armazem", [
            {"nome": "guarda e le", "prova": lambda a => …},
            {"nome": "apaga", "prova": lambda a => …}])

        provas.para("em memoria", lambda => spawn EmMemoria())
        provas.para("em disco", lambda => spawn EmDisco("/tmp/x"))

    Por que isso importa
    --------------------
    Duas implementacoes do mesmo trait costumam ter DOIS conjuntos de
    testes, escritos em epocas diferentes, cobrindo coisas diferentes.
    A segunda implementacao passa nos testes dela e quebra no uso —
    porque o que ela nao cumpre e justamente o que so o teste da
    primeira cobria.
    """
    provas = []
    for caso in (casos or []):
        if not isinstance(caso, dict) or not callable(caso.get("prova")):
            raise _erro(
                "cada caso de um contrato e um vault com 'nome' e 'prova'.",
                nota='ex.: {"nome": "guarda", "prova": lambda a => …}')
        provas.append({"nome": str(caso.get("nome", "caso")),
                       "prova": caso["prova"]})
    return _Contrato(str(nome), provas)


class _Contrato:
    __slots__ = ("nome", "provas", "resultados")

    def __init__(self, nome, provas):
        self.nome = nome
        self.provas = provas
        self.resultados = []

    def para(self, rotulo, construtor):
        """Roda todas as provas contra uma implementacao."""
        for prova in self.provas:
            registro = {"contrato": self.nome, "implementacao": str(rotulo),
                        "caso": prova["nome"], "estado": "passou",
                        "motivo": ""}
            try:
                prova["prova"](construtor())
            except Exception as erro:                        # noqa: BLE001
                registro["estado"] = "falhou"
                registro["motivo"] = (getattr(erro, "message", None)
                                      or str(erro))
            self.resultados.append(registro)
        return self

    def falhas(self):
        return [r for r in self.resultados if r["estado"] != "passou"]

    def resumo(self):
        return {"contrato": self.nome, "casos": len(self.resultados),
                "falhas": len(self.falhas()),
                "implementacoes": sorted({r["implementacao"]
                                          for r in self.resultados}),
                "detalhes": list(self.resultados)}

    def cobrar(self):
        """Levanta quando alguma implementacao nao cumpre o contrato."""
        falhas = self.falhas()
        if falhas:
            linhas = [f"{f['implementacao']}: {f['caso']} — {f['motivo']}"
                      for f in falhas[:6]]
            raise FalhaDeExpectativa(
                f"{len(falhas)} caso(s) do contrato '{self.nome}' nao "
                f"passaram:\n    " + "\n    ".join(linhas))
        return True

    def __repr__(self):
        return f"<contrato {self.nome}, {len(self.provas)} prova(s)>"


# ═══════════════════════════════════════════════════════════
#  Teste de mutação: o teste testa mesmo?
# ═══════════════════════════════════════════════════════════
#
# Cobertura responde "esta linha rodou?". Ela nao responde "se esta
# linha estivesse errada, alguem reclamaria?" — e as duas perguntas
# divergem justamente onde importa: um teste que chama a funcao e nao
# confere o resultado dá 100% de cobertura e zero de proteção.
#
# A mutação responde a segunda: troca um operador no código, roda a
# suíte, e vê se ela falha. Se **passar**, aquele teste não testava
# aquilo. O jargão chama o mutante de "sobrevivente", e cada
# sobrevivente é um buraco com endereço.

#: As trocas. Cada uma é uma mudança que um humano faria por engano, e
#: que um teste de verdade pegaria. Trocas que quase sempre produzem
#: erro de sintaxe ou laço infinito ficam de fora: elas gastam uma
#: rodada da suíte para não dizer nada.
MUTACOES = (
    ("bigger_eq", "bigger", "afrouxa um limite: '>=' vira '>'"),
    ("smaller_eq", "smaller", "afrouxa um limite: '<=' vira '<'"),
    ("bigger", "smaller", "inverte a comparação"),
    ("smaller", "bigger", "inverte a comparação"),
    (" is not ", " is ", "inverte a igualdade"),
    (" and ", " or ", "troca o conectivo"),
    (" or ", " and ", "troca o conectivo"),
    (" + ", " - ", "troca a operação"),
    (" - ", " + ", "troca a operação"),
    (" * ", " / ", "troca a operação"),
    ("yes", "no", "inverte um literal lógico"),
)

#: Onde NÃO mutar. Mudar um literal dentro de um comentário ou de um
#: texto não muda comportamento nenhum, e o mutante sobreviveria
#: sempre — enchendo o relatório de falsos buracos.
_IGNORAR_LINHA = ("//", "#")


def _fronteira(trecho):
    """A expressao que casa `trecho` como palavra, quando ele e uma.

    Operadores como ' + ' ja vem cercados de espaco e nao precisam de
    fronteira; palavras como 'bigger' precisam, senao casam dentro de
    'bigger_eq'.
    """
    if trecho.strip() != trecho:
        return re.escape(trecho)
    return r"\b" + re.escape(trecho) + r"\b"


def _mutantes(fonte, limite=40):
    """As variações do código-fonte, uma troca por vez.

    Uma troca por mutante é o ponto: com duas, um teste que pega a
    primeira esconde a segunda, e o relatório diz que ambas estão
    cobertas.
    """
    linhas = fonte.split("\n")
    gerados = []
    for numero, linha in enumerate(linhas):
        limpa = linha.strip()
        if not limpa or limpa.startswith(_IGNORAR_LINHA):
            continue
        sem_texto = re.sub(r'"[^"]*"', '""', linha)
        for de, para, descricao in MUTACOES:
            # A busca e por PALAVRA inteira: 'bigger' e um pedaco de
            # 'bigger_eq', e sem a fronteira a mesma linha gerava duas
            # mutacoes — uma delas trocando '>=' por '<=', que nao e a
            # troca anunciada. Um relatorio que descreve uma mudanca e
            # faz outra e pior que nenhum relatorio.
            achado = re.search(_fronteira(de), sem_texto)
            if achado is None:
                continue
            posicao = achado.start()
            mutada = linha[:posicao] + para + linha[posicao + len(de):]
            copia = list(linhas)
            copia[numero] = mutada
            gerados.append({
                "linha": numero + 1, "de": de.strip(), "para": para.strip(),
                "descricao": descricao, "antes": limpa,
                "depois": mutada.strip(), "fonte": "\n".join(copia)})
            if len(gerados) >= limite:
                return gerados
    return gerados


def mutar(arquivo, rodar_testes, limite=40):
    """Quebra o código de propósito e vê se a suíte acusa.

        r := Crucible.mutar("src/calculo.df",
                            lambda => Crucible.run()["falhas"] bigger 0)
        expect(r["sobreviventes"]).to_be_empty()

    `rodar_testes` é uma ação que devolve `yes` quando a suíte
    **reprovou** — ou seja, quando ela pegou o mutante. Ela recebe o
    caminho do arquivo já mutado no lugar do original, e a restauração
    acontece de qualquer jeito.

    O que o resultado diz
    ---------------------
    `sobreviventes` são as mutações que a suíte **não** pegou. Cada uma
    é uma linha cujo comportamento ninguém confere: trocar `>=` por `>`
    ali não faz teste nenhum falhar.

    O custo, dito de frente
    ------------------------
    Cada mutante roda a suíte inteira. Com quarenta mutantes e uma
    suíte de dois segundos, são oitenta segundos — por isso o `limite`
    existe e por isso isto não roda no CI de cada commit. É uma
    ferramenta de auditoria, e não um portão.
    """
    caminho = str(arquivo)
    if not os.path.isfile(caminho):
        raise _erro(f"nao achei '{caminho}' para mutar.")
    original = open(caminho, encoding="utf-8").read()
    gerados = _mutantes(original, limite)
    if not gerados:
        return {"arquivo": caminho, "mutantes": 0, "pegos": 0,
                "sobreviventes": [], "placar": 1.0,
                "nota": "nenhuma mutação se aplica a este arquivo"}

    pegos, sobreviventes = 0, []
    try:
        for mutante in gerados:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(mutante["fonte"])
            try:
                pegou = bool(rodar_testes())
            except Exception:                                # noqa: BLE001
                # Um mutante que faz a suíte ESTOURAR também foi pego:
                # o código quebrado não passou despercebido, que é a
                # única coisa que esta ferramenta pergunta.
                pegou = True
            if pegou:
                pegos += 1
            else:
                sobreviventes.append({
                    "linha": mutante["linha"], "de": mutante["de"],
                    "para": mutante["para"],
                    "descricao": mutante["descricao"],
                    "antes": mutante["antes"], "depois": mutante["depois"]})
    finally:
        # A restauração é num `finally` porque o arquivo do usuário
        # ficaria mutado se a suíte estourasse de um jeito que este
        # laço não prevê — e um código-fonte silenciosamente alterado
        # é o pior desfecho possível para uma ferramenta de teste.
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(original)

    return {"arquivo": caminho, "mutantes": len(gerados), "pegos": pegos,
            "sobreviventes": sobreviventes,
            "placar": round(pegos / len(gerados), 4),
            "nota": ("a suíte pega tudo o que este arquivo pode errar"
                     if not sobreviventes else
                     f"{len(sobreviventes)} mutação(ões) passaram sem "
                     f"ninguém reclamar")}


def relatorio_de_mutacao(resultado):
    """O resultado de `mutar`, como texto para o terminal."""
    linhas = [f"  {resultado['arquivo']}",
              f"  {resultado['pegos']}/{resultado['mutantes']} mutantes "
              f"pegos ({resultado['placar'] * 100:.0f}%)"]
    if resultado["sobreviventes"]:
        linhas.append("")
        linhas.append("  sobreviveram — ninguém reclamou destas trocas:")
        for s in resultado["sobreviventes"][:12]:
            linhas.append(f"    linha {s['linha']}: {s['de']} → {s['para']}"
                          f"  ({s['descricao']})")
            linhas.append(f"      {s['antes']}")
    return "\n".join(linhas)


# ═══════════════════════════════════════════════════════════
#  Ligar os matchers na Expectativa
# ═══════════════════════════════════════════════════════════
#
# Eles entram na classe, e não num objeto à parte: quem procura um
# matcher procura em `expect(...)`, e um segundo lugar para procurar é
# um matcher que ninguém acha.

_NOVOS = {
    "to_change": to_change,
    "to_not_change": to_not_change,
    "to_have_been_called": to_have_been_called,
    "to_have_been_called_times": to_have_been_called_times,
    "to_have_been_called_once": to_have_been_called_once,
    "to_have_been_called_with": to_have_been_called_with,
    "to_have_been_called_in_order": to_have_been_called_in_order,
    "to_have_never_been_called": to_have_never_been_called,
    "to_match_vault": to_match_vault,
    "to_have_shape": to_have_shape,
    "to_satisfy": to_satisfy,
    "to_be_one_of": to_be_one_of,
    "to_contain_exactly": to_contain_exactly,
    "to_be_subset_of": to_be_subset_of,
    "to_be_ordered_by": to_be_ordered_by,
    "to_round_trip": to_round_trip,
    "to_be_within_percent": to_be_within_percent,
    "to_raise_matching": to_raise_matching,
    "to_emit": to_emit,
    "to_emit_first": to_emit_first,
}

for _nome, _funcao in _NOVOS.items():
    if hasattr(Expectativa, _nome):
        raise RuntimeError(
            f"'{_nome}' ja existe em Expectativa — dois matchers com o "
            f"mesmo nome fariam o segundo sumir em silencio")
    setattr(Expectativa, _nome, _funcao)
del _nome, _funcao


# ═══════════════════════════════════════════════════════════
#  Cenário — dado, quando, então
# ═══════════════════════════════════════════════════════════

_ORDEM_DOS_PASSOS = {"dado": 0, "quando": 1, "entao": 2}


class Cenario:
    """Um teste escrito como comportamento: dado, quando, então.

    O valor não é a sintaxe — é o que a falha diz. Um `assert` que cai
    na linha 40 de um teste de 60 linhas diz *onde*; um cenário diz
    **em qual frase**: *"quebrou no passo 3 (então o saldo fica em
    70)"*, que é a frase que o analista de negócio escreveu.

    Três regras, e cada uma é cobrada:

    1. **A ordem é dado → quando → então.** Um `dado` depois de um
       `quando` mistura preparo com ação, e o teste passa a testar duas
       coisas — quando ele falha, não se sabe qual.
    2. **Sem `entao` não há cenário.** Um cenário que só prepara e age
       não confere nada, e passaria sempre.
    3. **Os passos dividem um `mundo`** (um vault), que é o único estado
       entre eles. Variável solta entre passos esconderia de onde veio
       o valor que o `entao` confere.
    """

    def __init__(self, nome):
        self.nome = str(nome)
        self.passos = []
        self.mundo = {}

    def _acrescentar(self, tipo, texto, acao):
        if not callable(acao):
            raise _erro(
                f"cenario '{self.nome}': o passo '{tipo} {texto}' precisa "
                "de uma acao que receba o mundo.",
                dica="cenario.dado(\"um carrinho vazio\", lambda m: m.set(...))")
        if self.passos:
            anterior = self.passos[-1][0]
            if _ORDEM_DOS_PASSOS[tipo] < _ORDEM_DOS_PASSOS[anterior]:
                raise _erro(
                    f"cenario '{self.nome}': '{tipo} {texto}' vem depois de "
                    f"um '{anterior}'. A ordem e dado → quando → entao.",
                    nota="um preparo depois da acao faz o cenario testar "
                         "duas coisas, e a falha nao diz qual.",
                    dica="parta em dois cenarios.")
        self.passos.append((tipo, str(texto), acao))
        return self

    def dado(self, texto, acao):
        return self._acrescentar("dado", texto, acao)

    def quando(self, texto, acao):
        return self._acrescentar("quando", texto, acao)

    def entao(self, texto, acao):
        return self._acrescentar("entao", texto, acao)

    def e(self, texto, acao):
        """Continua o tipo do passo anterior — o `And` do Gherkin."""
        if not self.passos:
            raise _erro(f"cenario '{self.nome}': 'e' precisa de um passo antes.")
        return self._acrescentar(self.passos[-1][0], texto, acao)

    def texto(self):
        """O cenário como ele se lê — é o que vai para o relatório."""
        linhas = [f"Cenario: {self.nome}"]
        anterior = None
        for tipo, frase, _ in self.passos:
            palavra = "E" if tipo == anterior else {
                "dado": "Dado", "quando": "Quando", "entao": "Entao"}[tipo]
            linhas.append(f"  {palavra} {frase}")
            anterior = tipo
        return "\n".join(linhas)

    def rodar(self):
        """Roda os passos em ordem. Devolve o relatório, ou levanta
        dizendo em qual passo quebrou."""
        if not any(t == "entao" for t, _, _ in self.passos):
            raise _erro(
                f"cenario '{self.nome}' nao tem nenhum 'entao'.",
                nota="sem 'entao' o cenario so prepara e age — nao confere "
                     "nada, e passaria sempre.")
        self.mundo = {}
        feitos = []
        for i, (tipo, frase, acao) in enumerate(self.passos, start=1):
            try:
                resultado = acao(self.mundo)
            except BaseException as erro:   # noqa: BLE001
                if not isinstance(erro, Exception):
                    raise
                motivo = getattr(erro, "message", None) or str(erro)
                raise C.FalhaDeExpectativa(
                    f"cenario '{self.nome}' quebrou no passo {i} "
                    f"({tipo} {frase}): {motivo}")
            if tipo == "entao" and resultado is False:
                raise C.FalhaDeExpectativa(
                    f"cenario '{self.nome}' quebrou no passo {i} "
                    f"({tipo} {frase}): a conferencia deu 'no'")
            feitos.append({"passo": i, "tipo": tipo, "frase": frase})
        return {"cenario": self.nome, "passos": feitos, "ok": True,
                "mundo": dict(self.mundo)}


def cenario(nome):
    """Um cenário dado/quando/então. Ver `Cenario`."""
    return Cenario(nome)


#: O que este arquivo acrescenta ao dicionário do módulo.
EXTRAS = {
    "corrida": corrida,
    "cenario": cenario,
    "determinismo": determinismo,
    "relogio": relogio,
    "com_relogio": com_relogio,
    "servidor_falso": servidor_falso,
    "contrato": contrato,
    "mutar": mutar,
    "relatorio_de_mutacao": relatorio_de_mutacao,
    "mutacoes": [{"de": d, "para": p, "descricao": x} for d, p, x in MUTACOES],
    "matchers_novos": sorted(_NOVOS),
}
