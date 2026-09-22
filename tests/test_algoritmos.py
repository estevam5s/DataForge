"""Arcane.Algoritmos — conferido contra a versão ingênua, com entrada aleatória.

Testar um algoritmo contra os exemplos que o autor escolheu prova pouco:
os exemplos são os casos em que ele pensou. Aqui cada um é comparado
com a forma óbvia (e lenta) sobre centenas de entradas sorteadas com
semente fixa.
"""
import itertools
import os
import random
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

A = get_module("Arcane.Algoritmos")
R = random.Random(20260922)


def test_busca_binaria_contra_index():
    for _ in range(300):
        xs = sorted(set(R.randint(0, 50) for _ in range(R.randint(0, 20))))
        alvo = R.randint(-2, 52)
        assert A["busca_binaria"](xs, alvo) == (xs.index(alvo) if alvo in xs else -1)
        assert A["limite_inferior"](xs, alvo) == sum(1 for x in xs if x < alvo)


def test_ordenar_mesclando_e_estavel_e_ordena():
    for _ in range(200):
        xs = [(R.randint(0, 5), i) for i in range(R.randint(0, 30))]
        assert A["ordenar_mesclando"](xs, lambda p: p[0]) == sorted(xs, key=lambda p: p[0])


def test_ordenar_contando_e_recusas():
    for _ in range(100):
        xs = [R.randint(-20, 20) for _ in range(R.randint(0, 40))]
        assert A["ordenar_contando"](xs) == sorted(xs)
    with pytest.raises(Exception):
        A["ordenar_contando"]([1.5, 2])
    with pytest.raises(Exception):
        A["ordenar_contando"]([0, 10 ** 9])


def _grafo_aleatorio(n=8, p=0.3, pesos=True):
    nos = [f"n{i}" for i in range(n)]
    g = {a: [] for a in nos}
    for a in nos:
        for b in nos:
            if a != b and R.random() < p:
                g[a].append([b, R.randint(1, 9)] if pesos else b)
    return g


def _floyd(g):
    nos = list(g)
    d = {(a, b): (0 if a == b else float("inf")) for a in nos for b in nos}
    for a in nos:
        for b, p in g[a]:
            d[(a, b)] = min(d[(a, b)], p)
    for k, i, j in itertools.product(nos, nos, nos):
        if d[(i, k)] + d[(k, j)] < d[(i, j)]:
            d[(i, j)] = d[(i, k)] + d[(k, j)]
    return d


def test_dijkstra_contra_floyd_warshall_e_o_caminho_soma_a_distancia():
    for _ in range(60):
        g = _grafo_aleatorio()
        ref = _floyd(g)
        r = A["dijkstra"](g, "n0")
        for b in g:
            esperado = ref[("n0", b)]
            if esperado == float("inf"):
                assert b not in r["distancia"] and A["caminho"](r, b) is None
            else:
                assert r["distancia"][b] == esperado
                c = A["caminho"](r, b)
                custo = sum(dict((v, p) for v, p in g[x])[y] for x, y in zip(c, c[1:]))
                assert c[0] == "n0" and c[-1] == b and custo == esperado


def test_dijkstra_recusa_peso_negativo():
    with pytest.raises(Exception) as e:
        A["dijkstra"]({"a": [["b", -1]]}, "a")
    assert "negativo" in str(e.value)


def test_bfs_e_a_menor_quantidade_de_arestas():
    for _ in range(60):
        g = _grafo_aleatorio(pesos=False)
        ref = _floyd({a: [[b, 1] for b in vs] for a, vs in g.items()})
        d = A["bfs"](g, "n0")
        for b in g:
            assert d.get(b, float("inf")) == ref[("n0", b)]


def test_dfs_visita_o_alcancavel_uma_vez():
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": ["a"], "x": []}
    ordem = A["dfs"](g, "a")
    assert ordem[0] == "a" and sorted(ordem) == ["a", "b", "c", "d"]


def test_ordem_topologica_respeita_as_arestas_e_mostra_o_ciclo():
    for _ in range(80):
        n = 8
        g = {f"n{i}": [f"n{j}" for j in range(i + 1, n) if R.random() < 0.3] for i in range(n)}
        ordem = A["ordem_topologica"](g)
        pos = {v: i for i, v in enumerate(ordem)}
        assert all(pos[a] < pos[b] for a in g for b in g[a])
    with pytest.raises(Exception) as e:
        A["ordem_topologica"]({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert "a → b → c → a" in str(e.value) or "ciclo" in str(e.value)


def _lcs_ingenua(a, b):
    melhor = 0
    for k in range(len(a) + 1):
        for comb in itertools.combinations(a, k):
            it = iter(b)
            if all(c in it for c in comb):
                melhor = max(melhor, k)
    return melhor


def test_lcs_tem_o_tamanho_otimo_e_e_subsequencia_das_duas():
    for _ in range(150):
        a = "".join(R.choice("abc") for _ in range(R.randint(0, 7)))
        b = "".join(R.choice("abc") for _ in range(R.randint(0, 7)))
        s = A["lcs"](a, b)
        assert len(s) == _lcs_ingenua(a, b)
        for texto in (a, b):
            it = iter(texto)
            assert all(c in it for c in s)


def _lev_ingenua(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    return min(_lev_ingenua(a[1:], b) + 1, _lev_ingenua(a, b[1:]) + 1,
               _lev_ingenua(a[1:], b[1:]) + (a[0] != b[0]))


def test_levenshtein_contra_a_recursao():
    assert A["levenshtein"]("gato", "rato") == 1
    for _ in range(150):
        a = "".join(R.choice("ab") for _ in range(R.randint(0, 5)))
        b = "".join(R.choice("ab") for _ in range(R.randint(0, 5)))
        assert A["levenshtein"](a, b) == _lev_ingenua(a, b)


def test_mochila_contra_forca_bruta():
    for _ in range(100):
        itens = [{"peso": R.randint(1, 6), "valor": R.randint(0, 20), "id": i}
                 for i in range(R.randint(0, 7))]
        cap = R.randint(0, 15)
        melhor = max((sum(i["valor"] for i in c) for k in range(len(itens) + 1)
                      for c in itertools.combinations(itens, k)
                      if sum(i["peso"] for i in c) <= cap), default=0)
        r = A["mochila"](itens, cap)
        assert r["valor"] == melhor
        assert sum(i["peso"] for i in r["escolhidos"]) <= cap
        assert sum(i["valor"] for i in r["escolhidos"]) == melhor


def test_kmp_contra_find():
    for _ in range(300):
        t = "".join(R.choice("ab") for _ in range(R.randint(0, 20)))
        p = "".join(R.choice("ab") for _ in range(R.randint(1, 4)))
        assert A["kmp"](t, p) == [i for i in range(len(t)) if t.startswith(p, i)]
    with pytest.raises(Exception):
        A["kmp"]("abc", "")


def test_crivo_contra_divisao():
    primo = lambda n: n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))
    assert A["crivo"](200) == [n for n in range(201) if primo(n)]
    assert A["crivo"](1) == []


def test_o_catalogo_cobre_todo_algoritmo_exportado():
    exportados = {k for k in A if not k.startswith("__")} - {"complexidade", "catalogo"}
    assert {c["nome"] for c in A["catalogo"]()} == exportados
    assert A["complexidade"]("dijkstra")["tempo"] == "O((V + E) log V)"
    with pytest.raises(Exception) as e:
        A["complexidade"]("dikstra")
    assert "dijkstra" in str(e.value)


def test_do_dataforge(tmp_path):
    f = tmp_path / "a.df"
    f.write_text(
        'adopt Arcane.Algoritmos as Alg\n'
        'g := {"a": [["b", 4], ["c", 1]], "c": [["b", 1]]}\n'
        'r := Alg.dijkstra(g, "a")\n'
        'assert Alg.caminho(r, "b") is ["a", "c", "b"]\n'
        'assert Alg.ordenar_mesclando([3, 1, 2]) is [1, 2, 3]\n'
        'assert Alg.ordenar_mesclando([{"n": 2}, {"n": 1}], lambda v: v["n"])[0]["n"] is 1\n'
        'assert Alg.levenshtein("gato", "rato") is 1\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
