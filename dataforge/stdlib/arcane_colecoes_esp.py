"""
Arcane.Collections — estruturas de dados especializadas.

Cluster e vault cobrem quase tudo. Estas cobrem o resto: fila que
remove das duas pontas em O(1), contador que ordena por frequencia,
vault com valor padrao, vault que lembra a ordem de insercao, e o
conjunto — que responde 'esta aqui?' em O(1) e faz uniao e interseccao.

    adopt Arcane.Collections as C

    fila := C.deque([1, 2, 3])
    C.push_left(fila, 0)
    out C.pop_left(fila)          // 0

    contagem := C.counter(["a", "b", "a"])
    out C.most_common(contagem, 1)    // [["a", 2]]

─── Por que nao usar cluster para tudo ─────────────────────

'xs.pop(0)' desloca todos os outros: e O(n), e num laco vira O(n^2).
Uma fila de mil itens processada assim faz um milhao de deslocamentos
para nada. A 'deque' remove das duas pontas em O(1) — e a diferenca
entre um processamento que termina e um que nao termina.
"""

import collections
import heapq
import itertools


class ArcaneCollections(dict):
    """Estruturas especializadas: fila, contador, conjunto, heap.

    Este modulo COMPLEMENTA 'arcane_collections.py', que ja trazia
    'group_by', 'sort_by_field' e a metade do conjunto. Os dois sao
    servidos sob o mesmo nome — 'Arcane.Collections' — porque sao o
    mesmo assunto, e obrigar quem escreve a lembrar em qual dos dois
    esta cada funcao seria arbitrario.

    Quando os dois definem o mesmo nome, o DESTE vence: ele e o mais
    completo (a 'deque' daqui remove das duas pontas; a de la era um
    cluster com outro nome).
    """

    def __new__(cls):
        return {
            # ── fila de duas pontas ──
            "deque": cls._deque,
            "push": cls._push,
            "push_left": cls._push_left,
            "pop": cls._pop,
            "pop_left": cls._pop_left,
            "peek": cls._peek,
            "peek_left": cls._peek_left,
            "rotate": cls._rotate,
            "extend_left": cls._extend_left,

            # ── contador ──
            "counter": cls._counter,
            "most_common": cls._most_common,
            "total": cls._total,
            "subtract": cls._subtract,
            "elements": cls._elements,

            # ── vault com padrao ──
            "default_vault": cls._default_vault,
            "group": cls._group,
            "index_by": cls._index_by,

            # ── conjunto ──
            "set": cls._set,
            "add": cls._add,
            "discard": cls._discard,
            "union": cls._union,
            "intersection": cls._intersection,
            "difference": cls._difference,
            "symmetric_difference": cls._symmetric_difference,
            "is_subset": cls._is_subset,
            "is_superset": cls._is_superset,
            "is_disjoint": cls._is_disjoint,

            # ── heap (fila de prioridade) ──
            "heap": cls._heap,
            "heap_push": cls._heap_push,
            "heap_pop": cls._heap_pop,
            "heap_peek": cls._heap_peek,
            "n_smallest": cls._n_smallest,
            "n_largest": cls._n_largest,

            # ── vault ordenado ──
            "ordered": cls._ordered,
            "move_to_end": cls._move_to_end,
            "first_key": cls._first_key,
            "last_key": cls._last_key,

            # ── tupla nomeada ──
            "named": cls._named,

            # ── encadeamento ──
            "chain_vaults": cls._chain_vaults,

            # ── frozen ──
            "frozen": cls._frozen,
        }

    # ── deque ───────────────────────────────────────────────

    @staticmethod
    def _deque(itens=None, maximo=0):
        """Uma fila de duas pontas. Com 'maximo', ela descarta a mais velha.

        O 'maximo' e o que faz um historico de N itens sem nenhuma
        conta: empurrar o item 101 numa fila de 100 tira o primeiro
        sozinho.
        """
        return collections.deque(list(itens or []),
                                 maxlen=maximo if maximo > 0 else None)

    @staticmethod
    def _push(fila, item):
        fila.append(item)
        return fila

    @staticmethod
    def _push_left(fila, item):
        fila.appendleft(item)
        return fila

    @staticmethod
    def _pop(fila):
        return fila.pop() if fila else None

    @staticmethod
    def _pop_left(fila):
        return fila.popleft() if fila else None

    @staticmethod
    def _peek(fila):
        return fila[-1] if fila else None

    @staticmethod
    def _peek_left(fila):
        return fila[0] if fila else None

    @staticmethod
    def _rotate(fila, n=1):
        """Gira a fila. Positivo leva o fim para o comeco."""
        fila.rotate(n)
        return fila

    @staticmethod
    def _extend_left(fila, itens):
        fila.extendleft(itens)
        return fila

    # ── contador ────────────────────────────────────────────

    @staticmethod
    def _counter(itens=None):
        """Conta ocorrencias numa passada.

        Aceita um cluster (conta os itens) ou um vault (usa os valores
        como contagem inicial).
        """
        if isinstance(itens, dict):
            return dict(collections.Counter(itens))
        return dict(collections.Counter(list(itens or [])))

    @staticmethod
    def _most_common(contagem, n=0):
        """Os mais frequentes, do maior para o menor.

        Devolve pares [chave, contagem] e nao um vault: um vault nao
        garante ordem em toda implementacao, e a ordem e o ponto.
        """
        c = collections.Counter(contagem)
        pares = c.most_common(n if n > 0 else None)
        return [[k, v] for k, v in pares]

    @staticmethod
    def _total(contagem):
        return sum(contagem.values())

    @staticmethod
    def _subtract(a, b):
        """Subtrai as contagens de 'b' de 'a'."""
        c = collections.Counter(a)
        c.subtract(collections.Counter(b))
        return dict(c)

    @staticmethod
    def _elements(contagem):
        """Cada chave repetida quantas vezes ela conta."""
        return list(collections.Counter(contagem).elements())

    # ── vault com padrao ────────────────────────────────────

    @staticmethod
    def _default_vault(padrao=None):
        """Um vault que devolve o padrao em vez de estourar.

        Evita o 'given not v.has(k): v[k] := []' antes de todo acesso —
        o padrao mais repetitivo que existe ao agrupar.
        """
        if isinstance(padrao, list):
            return collections.defaultdict(list)
        if isinstance(padrao, dict):
            return collections.defaultdict(dict)
        if isinstance(padrao, (int, float)):
            return collections.defaultdict(lambda: padrao)
        return collections.defaultdict(lambda: padrao)

    @staticmethod
    def _group(itens, chave):
        """Agrupa numa passada: {valor_da_chave: [itens]}."""
        saida = {}
        for item in itens:
            saida.setdefault(chave(item), []).append(item)
        return saida

    @staticmethod
    def _index_by(itens, chave):
        """Indexa por chave unica: {valor: item}. O ultimo vence."""
        return {chave(item): item for item in itens}

    # ── conjunto ────────────────────────────────────────────

    @staticmethod
    def _set(itens=None):
        """Um conjunto: itens unicos, e 'esta aqui?' em O(1)."""
        return set(itens or [])

    @staticmethod
    def _add(conjunto, item):
        conjunto.add(item)
        return conjunto

    @staticmethod
    def _discard(conjunto, item):
        """Remove sem estourar se nao estiver la."""
        conjunto.discard(item)
        return conjunto

    @staticmethod
    def _union(a, b):
        return set(a) | set(b)

    @staticmethod
    def _intersection(a, b):
        return set(a) & set(b)

    @staticmethod
    def _difference(a, b):
        return set(a) - set(b)

    @staticmethod
    def _symmetric_difference(a, b):
        """O que esta em um ou no outro, mas nao nos dois."""
        return set(a) ^ set(b)

    @staticmethod
    def _is_subset(a, b):
        return set(a) <= set(b)

    @staticmethod
    def _is_superset(a, b):
        return set(a) >= set(b)

    @staticmethod
    def _is_disjoint(a, b):
        return set(a).isdisjoint(set(b))

    # ── heap ────────────────────────────────────────────────

    @staticmethod
    def _heap(itens=None):
        """Uma fila de prioridade: o menor sai primeiro, em O(log n)."""
        h = list(itens or [])
        heapq.heapify(h)
        return h

    @staticmethod
    def _heap_push(h, item):
        heapq.heappush(h, item)
        return h

    @staticmethod
    def _heap_pop(h):
        return heapq.heappop(h) if h else None

    @staticmethod
    def _heap_peek(h):
        return h[0] if h else None

    @staticmethod
    def _n_smallest(itens, n, chave=None):
        return heapq.nsmallest(n, itens, key=chave)

    @staticmethod
    def _n_largest(itens, n, chave=None):
        return heapq.nlargest(n, itens, key=chave)

    # ── vault ordenado ──────────────────────────────────────

    @staticmethod
    def _ordered(pares=None):
        """Um vault que lembra a ordem em que as chaves entraram."""
        return collections.OrderedDict(pares or {})

    @staticmethod
    def _move_to_end(v, chave, para_o_fim=True):
        if isinstance(v, collections.OrderedDict) and chave in v:
            v.move_to_end(chave, last=para_o_fim)
        return v

    @staticmethod
    def _first_key(v):
        for k in v:
            return k
        return None

    @staticmethod
    def _last_key(v):
        ultimo = None
        for k in v:
            ultimo = k
        return ultimo

    # ── tupla nomeada ───────────────────────────────────────

    @staticmethod
    def _named(nome, campos, valores):
        """Um registro leve: campos com nome, sem declarar um record.

        Devolve um vault — em DataForge o record ja cobre o caso
        tipado, e isto e para o descartavel.
        """
        nomes = campos.split() if isinstance(campos, str) else list(campos)
        return dict(zip(nomes, list(valores)))

    # ── encadeamento ────────────────────────────────────────

    @staticmethod
    def _chain_vaults(*vaults):
        """Vaults consultados em ordem: o primeiro que tiver a chave vence.

        E como configuracao em camadas funciona: padrao, arquivo,
        ambiente, argumento — sem copiar tudo a cada camada.
        """
        saida = {}
        for v in reversed(vaults):
            saida.update(v)
        return saida

    # ── frozen ──────────────────────────────────────────────

    @staticmethod
    def _frozen(itens):
        """Um conjunto imutavel — serve de chave de vault."""
        return frozenset(itens)
