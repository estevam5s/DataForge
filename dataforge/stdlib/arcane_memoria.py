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

from ..errors import RuntimeError_


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


def _layout(alvo, amostras=20):
    """Como um objeto daquele blueprint ocupa memoria — MEDIDO.

    Nao ha alinhamento nem padding para inspecionar: isso e assunto de
    linguagem com layout fixo. O que existe aqui, e que custa caro na
    pratica, e a diferenca entre guardar os campos num DICIONARIO por
    objeto e guarda-los numa LISTA indexada, que e o que 'slots' faz.
    Medido no repositorio: 64% menos memoria por objeto.

    O numero sai de objetos de verdade — 'amostras' deles —, e nao de
    uma conta sobre o codigo: um palpite sobre memoria e sempre otimista.
    """
    i = _i()
    if not isinstance(alvo, i.DFBlueprint):
        return {"nome": _nome_de(alvo), "slots": False, "campos": [],
                "bytes": _tamanho(alvo), "amostras": 1,
                "nota": "layout pede um blueprint; isto e um valor"}
    interp = i.DFAction._interpreter
    no = interp._no_interno() if interp is not None else None
    objetos = []
    for _ in range(max(1, int(amostras))):
        try:
            objetos.append(interp._instanciar(alvo, [], {}, no, interp.global_env))
        except Exception:                                  # noqa: BLE001
            break
    if not objetos:
        return {"nome": alvo.name, "slots": bool(getattr(alvo, "slots", None)),
                "campos": list(getattr(alvo, "slots", None) or []),
                "bytes": 0, "amostras": 0,
                "nota": "este blueprint precisa de argumentos para nascer"}
    total = sum(_tamanho(o) for o in objetos)
    campos = list(getattr(alvo, "slots", None) or [])
    if not campos and objetos:
        campos = [c for c in getattr(objetos[0], "fields", {}) or {}]
    return {
        "nome": alvo.name,
        "slots": bool(getattr(alvo, "slots", None)),
        "campos": campos,
        "bytes": round(total / len(objetos)),
        "amostras": len(objetos),
    }


def _comparar_layout(um, outro, amostras=20):
    """Dois blueprints, lado a lado — e quanto um economiza."""
    a, b = _layout(um, amostras), _layout(outro, amostras)
    maior = max(a["bytes"], b["bytes"]) or 1
    menor = min(a["bytes"], b["bytes"])
    return {
        "a": a, "b": b,
        "diferenca_bytes": abs(a["bytes"] - b["bytes"]),
        "economia_percentual": round((maior - menor) * 100 / maior, 1),
        "menor": a["nome"] if a["bytes"] <= b["bytes"] else b["nome"],
    }


def _nome_de(valor):
    interp = _i().DFAction._interpreter
    if interp is None:
        return type(valor).__name__
    return interp._type_of(valor)


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


# ── O coletor sob controle (parte 10) ─────────────────────────
#
# A distincao que quase todo mundo erra: no CPython, quem libera e a
# CONTAGEM DE REFERENCIA, e ela roda na hora. O coletor existe so para o
# CICLO — 'a' apontando para 'b' que aponta para 'a'. Desligar o coletor
# NAO vaza memoria em geral: so deixa o ciclo para tras.
#
# E por isso que desliga-lo num trecho curto e sensivel a latencia e uma
# tecnica segura, e nao uma gambiarra. O que ela compra esta medido em
# 'tests/test_memoria_e_gc.py'.


def _gc_ligado():
    return gc.isenabled()


def _gc_ligar():
    gc.enable()
    return True


def _gc_desligar():
    gc.disable()
    return True


def _sem_gc(acao):
    """Roda a acao com o coletor desligado, e RELIGA mesmo se ela falhar.

    O 'finally' nao e detalhe: deixar o coletor desligado por causa de um
    erro e muito pior que a pausa que se queria evitar — e o programa
    seguiria assim ate terminar, sem nada denunciando.
    """
    estava = gc.isenabled()
    gc.disable()
    try:
        return acao()
    finally:
        if estava:
            gc.enable()


def _gc_limiares(*valores):
    """Le os limiares, ou ajusta os tres de uma vez."""
    if not valores:
        return list(gc.get_threshold())
    if len(valores) != 3:
        raise RuntimeError_(
            f"the collector has three generations: pass three thresholds, "
            f"got {len(valores)}. Read them with gc_limiares().",
            doc="memoria/coletor")
    gc.set_threshold(*[int(v) for v in valores])
    return list(gc.get_threshold())


def _gc_congelar():
    """Tira o que ja vive das varreduras — para sempre.

    E o que um servidor faz depois da carga e antes do primeiro pedido:
    tudo o que foi importado e montado nunca mais e varrido. O ganho e
    proporcional ao tamanho do que ja esta vivo.
    """
    gc.freeze()
    return gc.get_freeze_count()


def _gc_descongelar():
    gc.unfreeze()
    return gc.get_freeze_count()


def _gc_congelados():
    return gc.get_freeze_count()


def _gc_geracoes():
    """Quantas coletas houve em cada geracao, e quanto cada uma rendeu."""
    return [{"geracao": i,
             "coletas": e.get("collections", 0),
             "colecionados": e.get("collected", 0),
             "incolecionaveis": e.get("uncollectable", 0)}
            for i, e in enumerate(gc.get_stats())]


# ── Arena (parte 10) ──────────────────────────────────────────

class Arena:
    """Um lote preparado de uma vez, reaproveitado em vez de realocado.

    Nao e um allocator: quem aloca continua sendo o Python. O que a
    arena troca e o PADRAO de uso — em vez de criar e descartar por
    volta, um lote e preparado, emprestado e devolvido. O ganho aparece
    quando o objeto e caro de montar, nao quando ele e um vault de tres
    chaves.

    'limpar' e a operacao que ela existe para ter: soltar o lote inteiro
    numa chamada, que e o tempo de vida de arena da literatura.
    """

    __slots__ = ("_fabrica", "_livres", "_emprestados", "_criados",
                 "_entregues", "_reaproveitados", "_cresceu")

    def __init__(self, quantos, fabrica):
        self._fabrica = fabrica
        self._livres = [fabrica() for _ in range(max(0, int(quantos)))]
        self._emprestados = {}
        self._criados = len(self._livres)
        self._entregues = 0
        self._reaproveitados = 0
        self._cresceu = 0

    def pegar(self):
        if self._livres:
            item = self._livres.pop()
        else:
            # Travar seria pior; crescer CALADO esconderia que a arena
            # foi dimensionada errada. Por isso ela cresce e CONTA.
            item = self._fabrica()
            self._criados += 1
            self._cresceu += 1
        self._emprestados[id(item)] = item
        self._entregues += 1
        return item

    def devolver(self, item):
        if id(item) not in self._emprestados:
            raise RuntimeError_(
                "this object did not come from this arena. Giving back what "
                "was not taken would grow the pool with strangers, and the "
                "next 'pegar' would hand one of them out.",
                doc="memoria/coletor")
        del self._emprestados[id(item)]
        self._livres.append(item)
        self._reaproveitados += 1
        return True

    def limpar(self):
        """Devolve o lote inteiro de uma vez."""
        quantos = len(self._emprestados)
        self._livres.extend(self._emprestados.values())
        self._emprestados.clear()
        return quantos

    def estatisticas(self):
        return {
            "criados": self._criados,
            "entregues": self._entregues,
            "reaproveitados": self._reaproveitados,
            "em_uso": len(self._emprestados),
            "disponiveis": len(self._livres),
            "cresceu": self._cresceu,
        }


def _arena(quantos, fabrica):
    return Arena(quantos, fabrica)


def _de_arena(alvo, onde):
    if not isinstance(alvo, Arena):
        raise RuntimeError_(
            f"Memoria.{onde} expects an arena, made with Memoria.arena().",
            doc="memoria/coletor")
    return alvo


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
            "layout": _layout,
            "comparar_layout": _comparar_layout,
            "referencias": _referencias,

            # ── o coletor sob controle ──
            "gc_ligado": _gc_ligado,
            "gc_ligar": _gc_ligar,
            "gc_desligar": _gc_desligar,
            "sem_gc": _sem_gc,
            "gc_limiares": _gc_limiares,
            "gc_congelar": _gc_congelar,
            "gc_descongelar": _gc_descongelar,
            "gc_congelados": _gc_congelados,
            "gc_geracoes": _gc_geracoes,

            # ── arena ──
            "arena": _arena,
            "pegar": lambda a: _de_arena(a, "pegar").pegar(),
            "devolver": lambda a, i: _de_arena(a, "devolver").devolver(i),
            "limpar": lambda a: _de_arena(a, "limpar").limpar(),
            "arena_estatisticas":
                lambda a: _de_arena(a, "arena_estatisticas").estatisticas(),
        }
