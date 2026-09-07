"""
Arcane.Collections — estruturas de dados e algoritmos.

Pilha, fila, deque, heap, conjunto, contador, fila de prioridade, união-busca,
grafo e as travessias mais usadas. Tudo em vaults com __type__, para que as
estruturas circulem pelo runtime como qualquer valor DataForge.
"""

import heapq
from collections import Counter, OrderedDict, defaultdict, deque


def _estrutura(tipo, **campos):
    return {"__type__": tipo, **campos}


def _campo_de(item, campo):
    """Lê um campo de um vault, de um record ou de uma instância de blueprint."""
    if isinstance(item, dict):
        return item.get(campo)
    # DFRecordInstance guarda os campos em .values; DFInstance, em .fields.
    valores = getattr(item, 'values', None)
    if isinstance(valores, dict) and campo in valores:
        return valores[campo]
    campos = getattr(item, 'fields', None)
    if isinstance(campos, dict) and campo in campos:
        return campos[campo]
    return getattr(item, campo, None)


def _chave_ordenavel(valor):
    """Chave de ordenação que não estoura ao misturar tipos ou encontrar void."""
    if valor is None:
        return (0, 0, "")
    if isinstance(valor, bool):
        return (1, int(valor), "")
    if isinstance(valor, (int, float)):
        return (1, valor, "")
    return (2, 0, str(valor))


class _Stack:
    def __init__(self, itens=None):
        self._itens = list(itens or [])

    def push(self, v): self._itens.append(v); return self
    def pop(self): return self._itens.pop() if self._itens else None
    def peek(self): return self._itens[-1] if self._itens else None
    def is_empty(self): return not self._itens
    def size(self): return len(self._itens)
    def clear(self): self._itens.clear(); return self
    def to_cluster(self): return list(self._itens)
    def __repr__(self): return f"<stack {self._itens}>"


class _Queue:
    def __init__(self, itens=None):
        self._itens = deque(itens or [])

    def enqueue(self, v): self._itens.append(v); return self
    def dequeue(self): return self._itens.popleft() if self._itens else None
    def peek(self): return self._itens[0] if self._itens else None
    def is_empty(self): return not self._itens
    def size(self): return len(self._itens)
    def clear(self): self._itens.clear(); return self
    def to_cluster(self): return list(self._itens)
    def __repr__(self): return f"<queue {list(self._itens)}>"


class _Deque:
    def __init__(self, itens=None, limite=None):
        self._itens = deque(itens or [], maxlen=limite)

    def push_front(self, v): self._itens.appendleft(v); return self
    def push_back(self, v): self._itens.append(v); return self
    def pop_front(self): return self._itens.popleft() if self._itens else None
    def pop_back(self): return self._itens.pop() if self._itens else None
    def front(self): return self._itens[0] if self._itens else None
    def back(self): return self._itens[-1] if self._itens else None
    def rotate(self, n=1): self._itens.rotate(n); return self
    def size(self): return len(self._itens)
    def is_empty(self): return not self._itens
    def to_cluster(self): return list(self._itens)
    def __repr__(self): return f"<deque {list(self._itens)}>"


class _PriorityQueue:
    """Fila de prioridade: menor prioridade sai primeiro."""

    def __init__(self):
        self._heap = []
        self._ordem = 0

    def push(self, item, prioridade=0):
        heapq.heappush(self._heap, (prioridade, self._ordem, item))
        self._ordem += 1
        return self

    def pop(self):
        return heapq.heappop(self._heap)[2] if self._heap else None

    def peek(self):
        return self._heap[0][2] if self._heap else None

    def size(self): return len(self._heap)
    def is_empty(self): return not self._heap
    def to_cluster(self): return [item for _, _, item in sorted(self._heap)]
    def __repr__(self): return f"<priority_queue n={len(self._heap)}>"


class _Set:
    def __init__(self, itens=None):
        self._itens = set(itens or [])

    def add(self, v): self._itens.add(v); return self
    def remove(self, v): self._itens.discard(v); return self
    def has(self, v): return v in self._itens
    def size(self): return len(self._itens)
    def union(self, outro): return _Set(self._itens | _Set._raw(outro))
    def intersection(self, outro): return _Set(self._itens & _Set._raw(outro))
    def difference(self, outro): return _Set(self._itens - _Set._raw(outro))
    def symmetric_difference(self, outro): return _Set(self._itens ^ _Set._raw(outro))
    def is_subset(self, outro): return self._itens <= _Set._raw(outro)
    def is_superset(self, outro): return self._itens >= _Set._raw(outro)
    def to_cluster(self): return sorted(self._itens, key=lambda x: (str(type(x)), str(x)))
    def clear(self): self._itens.clear(); return self

    @staticmethod
    def _raw(outro):
        return outro._itens if isinstance(outro, _Set) else set(outro)

    def __repr__(self): return f"<set {sorted(map(str, self._itens))}>"


class _UnionFind:
    """União-busca com compressão de caminho — componentes conexos."""

    def __init__(self, itens=None):
        self._pai = {}
        for item in (itens or []):
            self._pai[item] = item

    def find(self, x):
        self._pai.setdefault(x, x)
        raiz = x
        while self._pai[raiz] != raiz:
            raiz = self._pai[raiz]
        while self._pai[x] != raiz:
            self._pai[x], x = raiz, self._pai[x]
        return raiz

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._pai[rb] = ra
            return True
        return False

    def connected(self, a, b):
        return self.find(a) == self.find(b)

    def groups(self):
        agrupado = defaultdict(list)
        for item in self._pai:
            agrupado[self.find(item)].append(item)
        return [sorted(map(str, g)) for g in agrupado.values()]

    def count(self):
        return len({self.find(i) for i in self._pai})


class _Graph:
    """Grafo por lista de adjacência, com ou sem direção."""

    def __init__(self, dirigido=False):
        self.dirigido = bool(dirigido)
        self._adj = defaultdict(dict)

    def add_node(self, n): self._adj.setdefault(n, {}); return self

    def add_edge(self, a, b, peso=1):
        self._adj[a][b] = peso
        self._adj.setdefault(b, {})
        if not self.dirigido:
            self._adj[b][a] = peso
        return self

    def neighbors(self, n): return list(self._adj.get(n, {}).keys())
    def nodes(self): return list(self._adj.keys())
    def edges(self):
        saida = []
        vistos = set()
        for a, vizinhos in self._adj.items():
            for b, peso in vizinhos.items():
                chave = (a, b) if self.dirigido else tuple(sorted(map(str, (a, b))))
                if chave in vistos:
                    continue
                vistos.add(chave)
                saida.append([a, b, peso])
        return saida

    def has_edge(self, a, b): return b in self._adj.get(a, {})
    def degree(self, n): return len(self._adj.get(n, {}))

    def bfs(self, inicio):
        visitados, ordem, fila = {inicio}, [], deque([inicio])
        while fila:
            atual = fila.popleft()
            ordem.append(atual)
            for vizinho in self._adj.get(atual, {}):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        return ordem

    def dfs(self, inicio):
        visitados, ordem, pilha = set(), [], [inicio]
        while pilha:
            atual = pilha.pop()
            if atual in visitados:
                continue
            visitados.add(atual)
            ordem.append(atual)
            for vizinho in reversed(list(self._adj.get(atual, {}))):
                if vizinho not in visitados:
                    pilha.append(vizinho)
        return ordem

    def shortest_path(self, inicio, fim):
        """Dijkstra. Devolve o caminho e o custo."""
        distancias = {inicio: 0}
        anterior = {}
        fila = [(0, inicio)]
        visitados = set()
        while fila:
            custo, atual = heapq.heappop(fila)
            if atual in visitados:
                continue
            visitados.add(atual)
            if atual == fim:
                break
            for vizinho, peso in self._adj.get(atual, {}).items():
                novo = custo + peso
                if novo < distancias.get(vizinho, float("inf")):
                    distancias[vizinho] = novo
                    anterior[vizinho] = atual
                    heapq.heappush(fila, (novo, vizinho))
        if fim not in distancias:
            return {"path": [], "cost": -1, "found": False}
        caminho, atual = [], fim
        while atual != inicio:
            caminho.append(atual)
            atual = anterior[atual]
        caminho.append(inicio)
        return {"path": list(reversed(caminho)),
                "cost": distancias[fim], "found": True}

    def has_cycle(self):
        cor = {}

        def visitar(n):
            cor[n] = 1
            for vizinho in self._adj.get(n, {}):
                estado = cor.get(vizinho, 0)
                if estado == 1 and (self.dirigido or vizinho != pai.get(n)):
                    return True
                if estado == 0:
                    pai[vizinho] = n
                    if visitar(vizinho):
                        return True
            cor[n] = 2
            return False

        pai = {}
        return any(cor.get(n, 0) == 0 and visitar(n) for n in list(self._adj))

    def topological_sort(self):
        if not self.dirigido:
            raise ValueError("ordenação topológica exige um grafo dirigido")
        grau = {n: 0 for n in self._adj}
        for vizinhos in self._adj.values():
            for v in vizinhos:
                grau[v] = grau.get(v, 0) + 1
        fila = deque([n for n, g in grau.items() if g == 0])
        ordem = []
        while fila:
            atual = fila.popleft()
            ordem.append(atual)
            for vizinho in self._adj.get(atual, {}):
                grau[vizinho] -= 1
                if grau[vizinho] == 0:
                    fila.append(vizinho)
        return ordem if len(ordem) == len(grau) else []

    def __repr__(self):
        return f"<graph nós={len(self._adj)} dirigido={self.dirigido}>"


class ArcaneCollections:
    """Estruturas de dados e algoritmos sobre coleções."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Collections",

            # ── Estruturas ──
            "stack": lambda itens=None: _Stack(itens),
            "queue": lambda itens=None: _Queue(itens),
            "deque": lambda itens=None, limite=None: _Deque(itens, limite),
            "priority_queue": lambda: _PriorityQueue(),
            "set": lambda itens=None: _Set(itens),
            "union_find": lambda itens=None: _UnionFind(itens),
            "graph": lambda dirigido=False: _Graph(dirigido),

            # ── Contagem e agrupamento ──
            "counter": lambda itens: dict(Counter(itens)),
            "most_common": lambda itens, n=1: [
                list(p) for p in Counter(itens).most_common(n)],
            "group_by": cls._group_by,
            "partition": cls._partition,
            "index_by": cls._index_by,

            # ── Combinação ──
            "zip_longest": cls._zip_longest,
            "cartesian": cls._cartesian,
            "pairwise": lambda itens: [
                [itens[i], itens[i + 1]] for i in range(len(list(itens)) - 1)],
            "sliding_window": cls._sliding_window,
            "batched": lambda itens, n: [
                list(itens)[i:i + n] for i in range(0, len(list(itens)), n)],

            # ── Ordenação ──
            "sort_by": lambda itens, chave: sorted(
                itens, key=lambda i: _chave_ordenavel(chave(i))),
            "sort_by_field": cls._sort_by_field,
            "binary_search": cls._binary_search,
            "merge_sorted": cls._merge_sorted,
            "top_n": lambda itens, n, chave=None: heapq.nlargest(n, itens, key=chave),
            "bottom_n": lambda itens, n, chave=None: heapq.nsmallest(n, itens, key=chave),

            # ── Conjuntos sobre listas ──
            "union": lambda a, b: cls._dedup(list(a) + list(b)),
            "intersection": lambda a, b: [x for x in cls._dedup(a) if x in list(b)],
            "difference": lambda a, b: [x for x in cls._dedup(a) if x not in list(b)],
            "symmetric_difference": lambda a, b: (
                [x for x in cls._dedup(a) if x not in list(b)]
                + [x for x in cls._dedup(b) if x not in list(a)]),
            "is_subset": lambda a, b: all(x in list(b) for x in a),

            # ── Utilidades ──
            "ordered_vault": lambda pares=None: OrderedDict(pares or []),
            "default_vault": cls._default_vault,
            "flatten_deep": cls._flatten_deep,
            "deep_merge": cls._deep_merge,
            "unique_by": cls._unique_by,
            "rotate": lambda itens, n: (list(itens)[n % len(itens):]
                                        + list(itens)[:n % len(itens)]) if itens else [],
            "chunk_evenly": cls._chunk_evenly,
        }

    @staticmethod
    def _dedup(itens):
        visto, saida = set(), []
        for item in itens:
            chave = str(item)
            if chave not in visto:
                visto.add(chave)
                saida.append(item)
        return saida

    @staticmethod
    def _group_by(itens, chave):
        agrupado = defaultdict(list)
        funcao = chave if callable(chave) else (lambda item: _campo_de(item, chave))
        for item in itens:
            agrupado[funcao(item)].append(item)
        return dict(agrupado)

    @staticmethod
    def _partition(itens, predicado):
        sim, nao = [], []
        for item in itens:
            (sim if predicado(item) else nao).append(item)
        return [sim, nao]

    @staticmethod
    def _index_by(itens, chave):
        funcao = chave if callable(chave) else (lambda item: _campo_de(item, chave))
        return {funcao(item): item for item in itens}

    @staticmethod
    def _zip_longest(a, b, preencher=None):
        a, b = list(a), list(b)
        n = max(len(a), len(b))
        return [[a[i] if i < len(a) else preencher,
                 b[i] if i < len(b) else preencher] for i in range(n)]

    @staticmethod
    def _cartesian(a, b):
        return [[x, y] for x in a for y in b]

    @staticmethod
    def _sliding_window(itens, tamanho):
        itens = list(itens)
        if tamanho > len(itens):
            return []
        return [itens[i:i + tamanho] for i in range(len(itens) - tamanho + 1)]

    @staticmethod
    def _sort_by_field(itens, campo, reverso=False):
        """Ordena por um campo, aceitando vaults, records e instâncias."""
        return sorted(itens,
                      key=lambda item: _chave_ordenavel(_campo_de(item, campo)),
                      reverse=bool(reverso))

    @staticmethod
    def _binary_search(ordenado, alvo):
        esq, dir_ = 0, len(ordenado) - 1
        while esq <= dir_:
            meio = (esq + dir_) // 2
            if ordenado[meio] == alvo:
                return meio
            if ordenado[meio] < alvo:
                esq = meio + 1
            else:
                dir_ = meio - 1
        return -1

    @staticmethod
    def _merge_sorted(a, b):
        return list(heapq.merge(a, b))

    @staticmethod
    def _default_vault(padrao=0):
        return defaultdict(lambda: padrao)

    @staticmethod
    def _flatten_deep(itens, profundidade=-1):
        saida = []
        for item in itens:
            if isinstance(item, (list, tuple)) and profundidade != 0:
                saida.extend(ArcaneCollections._flatten_deep(item, profundidade - 1))
            else:
                saida.append(item)
        return saida

    @staticmethod
    def _deep_merge(a, b):
        resultado = dict(a)
        for chave, valor in b.items():
            if (chave in resultado and isinstance(resultado[chave], dict)
                    and isinstance(valor, dict)):
                resultado[chave] = ArcaneCollections._deep_merge(resultado[chave], valor)
            else:
                resultado[chave] = valor
        return resultado

    @staticmethod
    def _unique_by(itens, chave):
        visto, saida = set(), []
        for item in itens:
            k = str(chave(item))
            if k not in visto:
                visto.add(k)
                saida.append(item)
        return saida

    @staticmethod
    def _chunk_evenly(itens, partes):
        itens = list(itens)
        if partes <= 0:
            return []
        tamanho, resto = divmod(len(itens), partes)
        saida, inicio = [], 0
        for i in range(partes):
            fim = inicio + tamanho + (1 if i < resto else 0)
            saida.append(itens[inicio:fim])
            inicio = fim
        return saida
