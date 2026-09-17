"""
Arcane.Memoria — o ciclo de vida dos objetos, visto de dentro.

    adopt Arcane.Memoria as Mem

    ref := Mem.fraca(cache)          nao segura o objeto vivo
    ref.viva()                       yes enquanto alguem mais o segura
    ref.obter()                      o objeto, ou void depois de coletado
    Mem.ao_descartar(conexao, acao)  roda 'acao' quando o objeto for embora
    Mem.coletar()                    forca a coleta; devolve quantos ciclos soltou
    Mem.vivos(Pedido)                quantas instancias existem agora
    Mem.tamanho(pedido)              bytes aproximados, com o que ele guarda

─── Como a memoria funciona aqui ───────────────────────────────

O DataForge roda sobre o CPython, e herda o modelo dele: cada objeto tem
um CONTADOR de referencias, e morre no instante em que ele chega a zero —
e por isso que 'teardown' roda assim que a ultima variavel solta o
objeto, sem esperar. O que o contador nao resolve e o CICLO (a aponta
para b, b aponta para a): para isso ha um coletor GERACIONAL, que roda de
tempos em tempos e que 'coletar()' forca.

Uma referencia FRACA aponta sem contar. E o que um cache ou um registro
de observadores precisa: guardar o objeto enquanto ele existir, sem ser
a razao de ele existir. Um cache com referencia forte e o vazamento de
memoria mais comum que existe.
"""

import gc
import sys
import weakref


def _i():
    from .. import interpreter as i
    return i


def _interp():
    from ..interpreter import DFAction
    return DFAction._interpreter


class RefFraca:
    """Uma referencia que nao mantem o objeto vivo."""

    def __init__(self, obj):
        try:
            self._ref = weakref.ref(obj)
        except TypeError:
            from ..errors import TypeError_
            raise TypeError_(
                f"{_interp()._nome_do_tipo(obj)} cannot have a weak reference.",
                nota="only objects (blueprint instances, actions, blueprints) can; "
                     "numbers and text are values, and are copied",
                doc="oop/memoria") from None

    def viva(self):
        return self._ref() is not None

    def obter(self):
        return self._ref()

    def __repr__(self):
        return "<ref fraca viva>" if self.viva() else "<ref fraca morta>"


class MapaFraco:
    """Um vault cujas CHAVES sao objetos, e some a entrada quando o objeto morre."""

    def __init__(self):
        self._mapa = weakref.WeakKeyDictionary()

    def definir(self, obj, valor):
        self._mapa[obj] = valor
        return valor

    def obter(self, obj, padrao=None):
        return self._mapa.get(obj, padrao)

    def tem(self, obj):
        return obj in self._mapa

    @property
    def tamanho(self):
        return len(self._mapa)


def _fraca(obj):
    return RefFraca(obj)


def _ao_descartar(obj, acao):
    """'acao()' roda quando o objeto for coletado. Devolve um cancelador."""
    interp = _interp()
    no = interp._no_interno()

    def rodar():
        try:
            interp._call(acao, [], {}, no, interp.global_env)
        except BaseException as erro:          # nunca propaga do coletor
            sys.stderr.write(f"aviso: ao_descartar falhou: "
                             f"{getattr(erro, 'message', erro)}\n")
    try:
        finalizador = weakref.finalize(obj, rodar)
    except TypeError:
        from ..errors import TypeError_
        raise TypeError_(f"{interp._nome_do_tipo(obj)} is a value and is never "
                         f"'discarded'.", doc="oop/memoria") from None
    return lambda: bool(finalizador.detach())


def _coletar(geracao=2):
    return gc.collect(int(geracao))


def _vivos(molde):
    """Quantas instancias do blueprint (e das filhas) existem agora."""
    i = _i()
    gc.collect()
    total = 0
    for obj in gc.get_objects():
        if isinstance(obj, i.DFInstance):
            bp = obj.blueprint
            if bp is molde or any(x is molde for x in bp.linhagem()):
                total += 1
    return total


def _estatisticas():
    """O que o coletor sabe: contagem por geracao e o limiar de cada uma."""
    contagem = gc.get_count()
    limiares = gc.get_threshold()
    return {
        "geracoes": [{"geracao": g, "objetos": contagem[g], "limiar": limiares[g]}
                     for g in range(len(contagem))],
        "coletas": [s.get("collections", 0) for s in gc.get_stats()],
        "ativo": gc.isenabled(),
        "rastreados": len(gc.get_objects()),
    }


def _tamanho(obj):
    """Bytes aproximados do objeto e de tudo que so ele alcanca."""
    i = _i()
    vistos = set()

    def medir(x):
        if id(x) in vistos:
            return 0
        vistos.add(id(x))
        total = sys.getsizeof(x)
        if isinstance(x, i.DFInstance):
            total += medir(x._valores)
        elif isinstance(x, dict):
            total += sum(medir(k) + medir(v) for k, v in x.items())
        elif isinstance(x, (list, tuple, set)):
            total += sum(medir(v) for v in x)
        return total

    return medir(obj)


def _referencias(obj):
    """Quantas referencias fortes apontam para o objeto (o contador do CPython)."""
    # menos as duas desta propria chamada: o parametro e o argumento
    return max(0, sys.getrefcount(obj) - 3)


class ArcaneMemoria:
    """Referencias fracas, finalizacao e o coletor."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Memoria",
            "fraca": _fraca,
            "mapa_fraco": lambda: MapaFraco(),
            "ao_descartar": _ao_descartar,
            "coletar": _coletar,
            "vivos": _vivos,
            "estatisticas": _estatisticas,
            "tamanho": _tamanho,
            "referencias": _referencias,
        }
