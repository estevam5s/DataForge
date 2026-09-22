# -*- coding: utf-8 -*-
"""Arcane.Algoritmos — os clássicos, com a complexidade dita junto.

A documentação de Big-O ensina por que uma busca binária é O(log n) e
um Dijkstra é O((V + E) log V). Este módulo é o outro lado: as mesmas
implementações, prontas, e cada uma com a sua complexidade como **dado**
(`complexidade("dijkstra")`) — o que permite a um programa escolher, e
a um teste conferir que a classe declarada é a medida.

Três decisões:

1. **O grafo é um vault de listas**, o formato que um JSON já traz:
   `{"a": ["b", "c"]}` sem peso, ou `{"a": [["b", 4], ["c", 1]]}` com.
   Um vizinho que não aparece como chave é aceito — é um nó sem saída.
2. **O inalcançável é `void`**, e não infinito: uma distância infinita
   somada a um preço dá infinito, calado.
3. **O erro de entrada diz qual entrada**: a ordem topológica de um grafo
   com ciclo levanta mostrando o ciclo, e o Dijkstra com peso negativo
   recusa antes de responder um caminho errado com confiança.
"""

import heapq
import math
from bisect import bisect_left


def _erro(mensagem, nota="", dica="", doc="biblioteca/algoritmos"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


CATALOGO = {
    "busca_binaria": ("O(log n)", "O(1)", "o cluster precisa estar ordenado"),
    "limite_inferior": ("O(log n)", "O(1)", "a posição onde o alvo entraria"),
    "ordenar_mesclando": ("O(n log n)", "O(n)", "estável: iguais mantêm a ordem"),
    "ordenar_contando": ("O(n + k)", "O(k)", "só inteiros; k é a faixa de valores"),
    "bfs": ("O(V + E)", "O(V)", "a menor distância em número de arestas"),
    "dfs": ("O(V + E)", "O(V)", "a ordem de visita, em profundidade"),
    "ordem_topologica": ("O(V + E)", "O(V)", "recusa grafo com ciclo, e mostra o ciclo"),
    "dijkstra": ("O((V + E) log V)", "O(V)", "pesos não negativos"),
    "caminho": ("O(V)", "O(V)", "reconstrói a partir de 'anterior'"),
    "lcs": ("O(n·m)", "O(n·m)", "a maior subsequência comum"),
    "levenshtein": ("O(n·m)", "O(m)", "a distância de edição"),
    "mochila": ("O(n·W)", "O(n·W)", "W é a capacidade inteira"),
    "kmp": ("O(n + m)", "O(m)", "todas as posições do padrão"),
    "crivo": ("O(n log log n)", "O(n)", "os primos até n"),
}


def complexidade(nome):
    """`{tempo, espaco, nota}` de um algoritmo deste módulo."""
    if nome not in CATALOGO:
        import difflib
        perto = difflib.get_close_matches(str(nome), list(CATALOGO), 1)
        raise _erro(f"nao ha algoritmo '{nome}'"
                    + (f". Voce quis dizer '{perto[0]}'?" if perto else "."))
    t, e, n = CATALOGO[nome]
    return {"nome": nome, "tempo": t, "espaco": e, "nota": n}


def catalogo():
    return [complexidade(n) for n in CATALOGO]


# ── busca e ordenação ───────────────────────────────────────────

def busca_binaria(xs, alvo):
    """O índice de `alvo` num cluster ORDENADO, ou -1."""
    i = bisect_left(xs, alvo)
    return i if i < len(xs) and xs[i] == alvo else -1


def limite_inferior(xs, alvo):
    """A primeira posição onde `alvo` poderia entrar mantendo a ordem."""
    return bisect_left(xs, alvo)


def ordenar_mesclando(xs, chave=None):
    """Merge sort estável. `chave` é uma ação que diz pelo que ordenar."""
    itens = list(xs)
    if len(itens) <= 1:
        return itens
    k = chave or (lambda v: v)

    def mesclar(a, b):
        saida, i, j = [], 0, 0
        while i < len(a) and j < len(b):
            if k(b[j]) < k(a[i]):          # estrito: iguais ficam na ordem
                saida.append(b[j]); j += 1
            else:
                saida.append(a[i]); i += 1
        return saida + a[i:] + b[j:]

    largura = 1
    while largura < len(itens):
        itens = [x for inicio in range(0, len(itens), 2 * largura)
                 for x in mesclar(itens[inicio:inicio + largura],
                                  itens[inicio + largura:inicio + 2 * largura])]
        largura *= 2
    return itens


def ordenar_contando(xs):
    """Counting sort para inteiros: O(n + k), sem comparar."""
    itens = list(xs)
    if not itens:
        return []
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in itens):
        raise _erro("ordenar_contando so ordena inteiros — use ordenar_mesclando")
    menor, maior = min(itens), max(itens)
    if maior - menor > 10_000_000:
        raise _erro(f"a faixa de valores e {maior - menor + 1}: contar gastaria mais "
                    "memoria que ordenar. Use ordenar_mesclando.")
    contagem = [0] * (maior - menor + 1)
    for v in itens:
        contagem[v - menor] += 1
    return [i + menor for i, n in enumerate(contagem) for _ in range(n)]


# ── grafos ──────────────────────────────────────────────────────

def _vizinhos(grafo, no):
    for v in grafo.get(no, []) or []:
        if isinstance(v, (list, tuple)):
            yield v[0], (v[1] if len(v) > 1 else 1)
        else:
            yield v, 1


def _nos(grafo):
    nos = list(grafo)
    for no in list(grafo):
        for v, _p in _vizinhos(grafo, no):
            if v not in grafo and v not in nos:
                nos.append(v)
    return nos


def bfs(grafo, origem):
    """A distância em arestas de `origem` a cada nó alcançável."""
    dist = {origem: 0}
    fila, i = [origem], 0
    while i < len(fila):
        no = fila[i]; i += 1
        for v, _p in _vizinhos(grafo, no):
            if v not in dist:
                dist[v] = dist[no] + 1
                fila.append(v)
    return dist


def dfs(grafo, origem):
    """A ordem de visita em profundidade — iterativa, sem teto de recursão."""
    vistos, ordem, pilha = set(), [], [origem]
    while pilha:
        no = pilha.pop()
        if no in vistos:
            continue
        vistos.add(no)
        ordem.append(no)
        vizinhos = [v for v, _p in _vizinhos(grafo, no)]
        pilha.extend(reversed(vizinhos))
    return ordem


def ordem_topologica(grafo):
    """Os nós numa ordem em que toda aresta vai para a frente.

    Um ciclo não tem ordem possível — e a mensagem mostra o ciclo, porque
    "o grafo tem ciclo" sem dizer onde é impossível de consertar.
    """
    nos = _nos(grafo)
    estado = {n: 0 for n in nos}          # 0 novo, 1 na pilha, 2 pronto
    ordem = []
    for inicio in nos:
        if estado[inicio]:
            continue
        pilha = [(inicio, iter([v for v, _p in _vizinhos(grafo, inicio)]))]
        caminho = [inicio]
        estado[inicio] = 1
        while pilha:
            no, it = pilha[-1]
            proximo = next(it, None)
            if proximo is None:
                pilha.pop(); caminho.pop()
                estado[no] = 2
                ordem.append(no)
            elif estado[proximo] == 1:
                ciclo = caminho[caminho.index(proximo):] + [proximo]
                raise _erro("o grafo tem ciclo: " + " → ".join(map(str, ciclo)),
                            dica="uma ordem topologica so existe sem ciclo")
            elif estado[proximo] == 0:
                estado[proximo] = 1
                caminho.append(proximo)
                pilha.append((proximo, iter([v for v, _p in _vizinhos(grafo, proximo)])))
    return list(reversed(ordem))


def dijkstra(grafo, origem):
    """`{distancia, anterior}` — a menor distância ponderada a cada nó."""
    for no in grafo:
        for v, p in _vizinhos(grafo, no):
            if p < 0:
                raise _erro(f"a aresta {no} → {v} tem peso {p}: Dijkstra nao aceita "
                            "peso negativo, e responderia um caminho errado",
                            dica="com peso negativo, o algoritmo e Bellman-Ford")
    dist = {origem: 0}
    anterior = {}
    fila = [(0, 0, origem)]
    contador = 1                          # desempata sem comparar os nós
    feitos = set()
    while fila:
        d, _c, no = heapq.heappop(fila)
        if no in feitos:
            continue
        feitos.add(no)
        for v, p in _vizinhos(grafo, no):
            nd = d + p
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                anterior[v] = no
                heapq.heappush(fila, (nd, contador, v))
                contador += 1
    return {"distancia": dist, "anterior": anterior}


def caminho(resultado, destino):
    """O caminho até `destino` a partir do que `dijkstra` devolveu — ou `void`."""
    dist = resultado.get("distancia", {})
    if destino not in dist:
        return None
    anterior = resultado.get("anterior", {})
    saida = [destino]
    while saida[0] in anterior:
        saida.insert(0, anterior[saida[0]])
    return saida


# ── programação dinâmica e texto ────────────────────────────────

def lcs(a, b):
    """A maior subsequência comum de dois textos (ou clusters)."""
    n, m = len(a), len(b)
    t = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            t[i][j] = t[i + 1][j + 1] + 1 if a[i] == b[j] else max(t[i + 1][j], t[i][j + 1])
    i = j = 0
    saida = []
    while i < n and j < m:
        if a[i] == b[j]:
            saida.append(a[i]); i += 1; j += 1
        elif t[i + 1][j] >= t[i][j + 1]:
            i += 1
        else:
            j += 1
    return "".join(saida) if isinstance(a, str) and isinstance(b, str) else saida


def levenshtein(a, b):
    """Quantas inserções, remoções e trocas levam `a` a `b`."""
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        for j, cb in enumerate(b, 1):
            atual.append(min(anterior[j] + 1, atual[j - 1] + 1,
                             anterior[j - 1] + (ca != cb)))
        anterior = atual
    return anterior[-1]


def mochila(itens, capacidade):
    """A mochila 0/1: `itens` é um cluster de `{peso, valor}` (e o resto viaja junto).

    Devolve `{valor, escolhidos}`. O peso precisa ser inteiro: é ele que
    indexa a tabela, e é por isso que o custo é O(n·W) — pseudo-polinomial.
    """
    capacidade = int(capacidade)
    lista = list(itens)
    for it in lista:
        if not isinstance(it.get("peso"), int) or it["peso"] < 0:
            raise _erro("cada item precisa de 'peso' inteiro e nao negativo")
    n = len(lista)
    t = [[0] * (capacidade + 1) for _ in range(n + 1)]
    for i, it in enumerate(lista, 1):
        p, v = it["peso"], it.get("valor", 0)
        for w in range(capacidade + 1):
            t[i][w] = t[i - 1][w]
            if p <= w and t[i - 1][w - p] + v > t[i][w]:
                t[i][w] = t[i - 1][w - p] + v
    escolhidos, w = [], capacidade
    for i in range(n, 0, -1):
        if t[i][w] != t[i - 1][w]:
            escolhidos.insert(0, lista[i - 1])
            w -= lista[i - 1]["peso"]
    return {"valor": t[n][capacidade], "escolhidos": escolhidos}


def kmp(texto, padrao):
    """Todas as posições de `padrao` em `texto`, em O(n + m)."""
    if padrao == "":
        raise _erro("o padrao esta vazio: ele casaria em toda posicao")
    falha = [0] * len(padrao)
    k = 0
    for i in range(1, len(padrao)):
        while k and padrao[i] != padrao[k]:
            k = falha[k - 1]
        if padrao[i] == padrao[k]:
            k += 1
        falha[i] = k
    saida, k = [], 0
    for i, c in enumerate(texto):
        while k and c != padrao[k]:
            k = falha[k - 1]
        if c == padrao[k]:
            k += 1
        if k == len(padrao):
            saida.append(i - k + 1)
            k = falha[k - 1]
    return saida


def crivo(n):
    """Os primos até `n`, pelo crivo de Eratóstenes."""
    n = int(n)
    if n < 2:
        return []
    marca = bytearray([1]) * (n + 1)
    marca[0] = marca[1] = 0
    for i in range(2, int(math.isqrt(n)) + 1):
        if marca[i]:
            marca[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    return [i for i in range(n + 1) if marca[i]]


class ArcaneAlgoritmos:
    """Arcane.Algoritmos — os clássicos, com a complexidade como dado."""

    def __new__(cls):
        return {
            "complexidade": complexidade, "catalogo": catalogo,
            "busca_binaria": busca_binaria, "limite_inferior": limite_inferior,
            "ordenar_mesclando": ordenar_mesclando, "ordenar_contando": ordenar_contando,
            "bfs": bfs, "dfs": dfs, "ordem_topologica": ordem_topologica,
            "dijkstra": dijkstra, "caminho": caminho,
            "lcs": lcs, "levenshtein": levenshtein, "mochila": mochila,
            "kmp": kmp, "crivo": crivo,
        }
