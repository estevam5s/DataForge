# -*- coding: utf-8 -*-
"""Onde as duas metades de `Arcane.Collections` se encontram.

O problema
----------
`Arcane.Collections` é montado de dois arquivos: `arcane_collections`
(cluster, vault, agrupamento) e `arcane_colecoes_esp` (fila, heap,
conjunto). A regra de junção era "o complemento vence nos nomes
repetidos: ele é o mais completo" — e ela está errada em doze nomes,
porque nesses doze **os dois não fazem a mesma coisa**.

O sintoma era silencioso ou enganoso, conforme o caso:

    C.index_by(itens, "categoria")   'String' object is not callable
    C.rotate([1, 2, 3], 1)           'Cluster' object has no attribute 'rotate'
    C.union([3, 1], [1, 2])          {1, 2, 3} — um Set, sem ordem

O `index_by` por NOME de campo está na documentação e parou de
funcionar; o `rotate` de um cluster é o uso comum e virou erro sobre um
atributo do Python; e o `union` de dois clusters passou a devolver
outro tipo, sem ordem, estourando num cluster de clusters.

A resposta
----------
Nenhuma das duas versões é "a certa": elas atendem entradas
diferentes. Estas funções **decidem pelo que receberam** — conjunto com
conjunto dá conjunto; cluster com cluster dá cluster, com a ordem
preservada.

É o que quem escreve espera, e é o que faz as duas metades caberem sob
um nome só sem uma delas sumir.
"""

from collections import Counter, deque

from .arcane_collections import _campo_de, _Deque, _Set


def _e_conjunto(valor):
    return isinstance(valor, (set, frozenset, _Set))


def _cru(valor):
    """Os itens de um conjunto, seja ele Python ou o _Set da linguagem."""
    if isinstance(valor, _Set):
        return set(valor._itens)
    if isinstance(valor, (set, frozenset)):
        return set(valor)
    return set(valor)


def _sem_repetir(itens):
    """Únicos, NA ORDEM em que apareceram.

    Não é `set`: a ordem é o que distingue a união de dois clusters da
    união de dois conjuntos, e perdê-la faz uma listagem mudar de ordem
    entre execuções.
    """
    from ..builtins import chave_de_identidade
    vistos, saida = set(), []
    for item in itens:
        chave = chave_de_identidade(item)
        if chave not in vistos:
            vistos.add(chave)
            saida.append(item)
    return saida


def _binaria(nome, sobre_conjunto, sobre_cluster):
    """A operação de dois argumentos, escolhida pelo que chegou."""
    def operar(a, b):
        if _e_conjunto(a) and _e_conjunto(b):
            resultado = sobre_conjunto(_cru(a), _cru(b))
            if isinstance(a, _Set) or isinstance(b, _Set):
                return _Set(resultado) if isinstance(resultado, set) else resultado
            return resultado
        return sobre_cluster(list(a), list(b))
    operar.__name__ = nome
    return operar


union = _binaria(
    "union",
    lambda a, b: a | b,
    lambda a, b: _sem_repetir(a + b))

intersection = _binaria(
    "intersection",
    lambda a, b: a & b,
    lambda a, b: [x for x in _sem_repetir(a) if x in b])

difference = _binaria(
    "difference",
    lambda a, b: a - b,
    lambda a, b: [x for x in _sem_repetir(a) if x not in b])

symmetric_difference = _binaria(
    "symmetric_difference",
    lambda a, b: a ^ b,
    lambda a, b: ([x for x in _sem_repetir(a) if x not in b]
                  + [x for x in _sem_repetir(b) if x not in a]))

is_subset = _binaria(
    "is_subset",
    lambda a, b: a <= b,
    lambda a, b: all(x in b for x in a))

is_superset = _binaria(
    "is_superset",
    lambda a, b: a >= b,
    lambda a, b: all(x in a for x in b))

is_disjoint = _binaria(
    "is_disjoint",
    lambda a, b: a.isdisjoint(b),
    lambda a, b: not any(x in b for x in a))


def rotate(colecao, n=1):
    """Gira. Numa fila, no lugar; num cluster, devolvendo uma cópia nova.

    A fila de duas pontas existe para ser mudada no lugar — é o que a
    torna barata. Um cluster não: mudá-lo por baixo de quem o passou é
    a classe de bug que este projeto persegue.
    """
    if isinstance(colecao, _Deque):
        return colecao.rotate(n)
    if isinstance(colecao, deque):
        colecao.rotate(n)
        return colecao
    itens = list(colecao)
    if not itens:
        return []
    corte = n % len(itens)
    return itens[corte:] + itens[:corte]


def index_by(itens, chave):
    """Indexa por chave única. `chave` é um NOME de campo ou uma ação.

    O nome de campo é a forma documentada e a mais usada — e era
    justamente a que o sombreamento tinha quebrado.
    """
    funcao = chave if callable(chave) else (lambda item: _campo_de(item, chave))
    return {funcao(item): item for item in itens}


def group_by(itens, chave):
    """Agrupa. Mesma regra do `index_by` para a chave."""
    funcao = chave if callable(chave) else (lambda item: _campo_de(item, chave))
    agrupado = {}
    for item in itens:
        agrupado.setdefault(funcao(item), []).append(item)
    return agrupado


def counter(itens=None):
    """Conta ocorrências. Um vault já contado passa direto."""
    if itens is None:
        return {}
    if isinstance(itens, dict):
        return dict(itens)
    return dict(Counter(itens))


def most_common(fonte, n=0):
    """Os mais frequentes, do maior para o menor.

    Aceita os ITENS ou um vault já contado — as duas metades chamavam
    isto com coisas diferentes, e exigir uma delas quebraria a outra.
    """
    contagem = fonte if isinstance(fonte, dict) else Counter(fonte)
    pares = Counter(contagem).most_common(n or None)
    return [list(p) for p in pares]


#: Os nomes que as duas metades declaram, e a versão que decide por si.
#: Toda colisão entre as metades precisa estar aqui — há um teste que
#: compara as duas listas, porque uma colisão nova voltaria a ser
#: resolvida por ordem de merge, em silêncio.
RESOLVIDOS = {
    "union": union,
    "intersection": intersection,
    "difference": difference,
    "symmetric_difference": symmetric_difference,
    "is_subset": is_subset,
    "is_superset": is_superset,
    "is_disjoint": is_disjoint,
    "rotate": rotate,
    "index_by": index_by,
    "group_by": group_by,
    "counter": counter,
    "most_common": most_common,
}

#: Colisões em que as duas versões são a MESMA ideia e a do complemento
#: é de fato a mais completa. Ficam com ela, e estão listadas para que a
#: escolha seja deliberada.
#:
#: 'set' e 'deque' devolvem o objeto CRU do Python no complemento e o
#: embrulho da linguagem na base. O cru vence porque é o que o resto da
#: biblioteca produz e consome — 'unique', 'frequencies' e o próprio
#: 'union' acima falam com ele.
DO_COMPLEMENTO = ("set", "deque", "default_vault")
