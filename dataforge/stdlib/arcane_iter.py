"""
Arcane.Iter — iteradores, combinatoria e composicao de acoes.

Duas famílias que andam juntas: percorrer sem materializar
(itertools) e combinar acoes (functools).

    adopt Arcane.Iter as I

    out I.take(I.count(1), 5)              // [1, 2, 3, 4, 5]
    out I.chunk([1,2,3,4,5], 2)            // [[1,2], [3,4], [5]]
    out I.combinations(["a","b","c"], 2)   // 3 pares

─── Preguica ───────────────────────────────────────────────

Quase tudo aqui devolve um GENERATOR, e nao um cluster: 'I.count(1)'
conta ate o infinito e nao ocupa memoria nenhuma ate alguem pedir os
itens. Quem quer a lista chama 'I.to_cluster' ou 'I.take(n)'.

As funcoes que precisam ver tudo — 'sorted_by', 'group_all' — devolvem
cluster, porque nao ha como ordenar sem ter tudo em maos.
"""

import functools
import itertools
import operator


class ArcaneIter(dict):
    """Iteradores preguicosos, combinatoria e composicao."""

    def __new__(cls):
        return {
            # ── infinitos ──
            "count": cls._count,
            "cycle_forever": cls._cycle_forever,
            "repeat": cls._repeat,

            # ── fatiar e agrupar ──
            "take": cls._take,
            "drop": cls._drop,
            "slice": cls._slice,
            "chunk": cls._chunk,
            "window": cls._window,
            "pairwise": cls._pairwise,
            "batched": cls._chunk,

            # ── combinar ──
            "chain": cls._chain,
            "zip_longest": cls._zip_longest,
            "product": cls._product,
            "permutations": cls._permutations,
            "combinations": cls._combinations,
            "combinations_with_repetition": cls._combinations_rep,
            "powerset": cls._powerset,

            # ── filtrar ──
            "take_while": cls._take_while,
            "drop_while": cls._drop_while,
            "filter_false": cls._filter_false,
            "compress": cls._compress,
            "unique": cls._unique,
            "unique_by": cls._unique_by,

            # ── acumular ──
            "accumulate": cls._accumulate,
            "running_sum": cls._running_sum,
            "running_max": cls._running_max,
            "group_runs": cls._group_runs,

            # ── materializar ──
            "to_cluster": cls._to_cluster,
            "flatten": cls._flatten,
            "flat_map": cls._flat_map,

            # ── composicao de acoes ──
            "reduce": cls._reduce,
            "partial": cls._partial,
            "compose": cls._compose,
            "pipe": cls._pipe,
            "curry": cls._curry,
            "flip": cls._flip,
            "identity": cls._identity,
            "constant": cls._constant,
            "once": cls._once,
            "memoize": cls._memoize,
            "cache_info": cls._cache_info,

            # ── operadores como acao ──
            "op": cls._op,
            "attr": cls._attr,
            "item": cls._item,
        }

    # ── infinitos ───────────────────────────────────────────

    @staticmethod
    def _count(inicio=0, passo=1):
        """Conta para sempre. So produz o que alguem pedir."""
        return itertools.count(inicio, passo)

    @staticmethod
    def _cycle_forever(itens):
        """Repete a colecao sem fim."""
        return itertools.cycle(itens)

    @staticmethod
    def _repeat(valor, vezes=0):
        return (itertools.repeat(valor, vezes) if vezes > 0
                else itertools.repeat(valor))

    # ── fatiar e agrupar ────────────────────────────────────

    @staticmethod
    def _take(fonte, n):
        """Os n primeiros, como cluster. Funciona sobre infinito."""
        return list(itertools.islice(fonte, n))

    @staticmethod
    def _drop(fonte, n):
        return itertools.islice(fonte, n, None)

    @staticmethod
    def _slice(fonte, inicio, fim=None, passo=1):
        return itertools.islice(fonte, inicio, fim, passo)

    @staticmethod
    def _chunk(fonte, tamanho):
        """Pedacos de tamanho fixo. O ultimo pode ser menor.

        E como se processa um arquivo grande em lotes: mil linhas por
        vez, sem carregar o arquivo inteiro.
        """
        if tamanho <= 0:
            from ...errors import NegativeSizeError
            raise NegativeSizeError("chunk size must be positive.", doc="colecoes")
        it = iter(fonte)
        saida = []
        while True:
            pedaco = list(itertools.islice(it, tamanho))
            if not pedaco:
                return saida
            saida.append(pedaco)

    @staticmethod
    def _window(fonte, tamanho):
        """Janelas deslizantes: [1,2,3,4] com 2 da [[1,2],[2,3],[3,4]].

        E como se calcula media movel sem indice manual.
        """
        itens = list(fonte)
        if tamanho > len(itens):
            return []
        return [itens[i:i + tamanho] for i in range(len(itens) - tamanho + 1)]

    @staticmethod
    def _pairwise(fonte):
        """Cada item com o seguinte: [1,2,3] da [[1,2],[2,3]]."""
        itens = list(fonte)
        return [[itens[i], itens[i + 1]] for i in range(len(itens) - 1)]

    # ── combinar ────────────────────────────────────────────

    @staticmethod
    def _chain(*fontes):
        """Percorre varias colecoes como se fossem uma."""
        return itertools.chain(*fontes)

    @staticmethod
    def _zip_longest(a, b, preencher=None):
        """Junta aos pares, indo ate a mais longa."""
        return [list(t) for t in itertools.zip_longest(a, b, fillvalue=preencher)]

    @staticmethod
    def _product(*fontes, repetir=1):
        """Produto cartesiano: todas as combinacoes possiveis.

        Cuidado com o tamanho: tres colecoes de dez dao mil resultados,
        e quatro dao dez mil. E O(n^k).
        """
        return [list(t) for t in itertools.product(*fontes, repeat=repetir)]

    @staticmethod
    def _permutations(fonte, tamanho=0):
        """Todas as ordens possiveis. O(n!) — inviavel acima de dez."""
        itens = list(fonte)
        n = tamanho if tamanho > 0 else len(itens)
        return [list(t) for t in itertools.permutations(itens, n)]

    @staticmethod
    def _combinations(fonte, tamanho):
        """Subconjuntos de tamanho fixo, sem repetir e sem ordem."""
        return [list(t) for t in itertools.combinations(list(fonte), tamanho)]

    @staticmethod
    def _combinations_rep(fonte, tamanho):
        return [list(t) for t in
                itertools.combinations_with_replacement(list(fonte), tamanho)]

    @staticmethod
    def _powerset(fonte):
        """Todos os subconjuntos. Sao 2^n — cuidado acima de vinte."""
        itens = list(fonte)
        return [list(c) for n in range(len(itens) + 1)
                for c in itertools.combinations(itens, n)]

    # ── filtrar ─────────────────────────────────────────────

    @staticmethod
    def _take_while(fonte, condicao):
        """Enquanto a condicao valer; para no primeiro que nao vale."""
        return list(itertools.takewhile(condicao, fonte))

    @staticmethod
    def _drop_while(fonte, condicao):
        return list(itertools.dropwhile(condicao, fonte))

    @staticmethod
    def _filter_false(fonte, condicao):
        return list(itertools.filterfalse(condicao, fonte))

    @staticmethod
    def _compress(fonte, marcas):
        """Fica com os itens cuja marca correspondente e verdadeira."""
        return list(itertools.compress(fonte, marcas))

    @staticmethod
    def _unique(fonte):
        """Sem repetidos, PRESERVANDO a ordem.

        Um conjunto tambem tira repetidos, e perde a ordem — que
        costuma importar.
        """
        vistos, saida = set(), []
        for item in fonte:
            chave = item if isinstance(item, (str, int, float, bool, tuple)) \
                else repr(item)
            if chave not in vistos:
                vistos.add(chave)
                saida.append(item)
        return saida

    @staticmethod
    def _unique_by(fonte, chave):
        vistos, saida = set(), []
        for item in fonte:
            k = chave(item)
            marca = k if isinstance(k, (str, int, float, bool, tuple)) else repr(k)
            if marca not in vistos:
                vistos.add(marca)
                saida.append(item)
        return saida

    # ── acumular ────────────────────────────────────────────

    @staticmethod
    def _accumulate(fonte, funcao=None, inicial=None):
        """Os resultados PARCIAIS, e nao so o final.

        'reduce' devolve o total; 'accumulate' devolve o caminho ate
        ele — que e o que um grafico de saldo precisa.
        """
        f = funcao or operator.add
        if inicial is not None:
            return list(itertools.accumulate(fonte, f, initial=inicial))
        return list(itertools.accumulate(fonte, f))

    @staticmethod
    def _running_sum(fonte):
        return list(itertools.accumulate(fonte, operator.add))

    @staticmethod
    def _running_max(fonte):
        return list(itertools.accumulate(fonte, max))

    @staticmethod
    def _group_runs(fonte, chave=None):
        """Agrupa itens CONSECUTIVOS iguais.

        Diferente de 'group_by': aqui a ordem importa. [1,1,2,1] da
        tres grupos, nao dois.
        """
        saida = []
        for k, grupo in itertools.groupby(fonte, key=chave):
            saida.append([k, list(grupo)])
        return saida

    # ── materializar ────────────────────────────────────────

    @staticmethod
    def _to_cluster(fonte):
        return list(fonte)

    @staticmethod
    def _flatten(fonte, profundidade=1):
        """Achata um nivel por vez, e nao tudo de uma vez.

        Achatar tudo por padrao destroi estrutura que costuma importar:
        [[1,2],[3,[4,5]]] com profundidade 1 vira [1,2,3,[4,5]].
        """
        atual = list(fonte)
        for _ in range(max(0, profundidade)):
            proximo = []
            for item in atual:
                if isinstance(item, (list, tuple)):
                    proximo.extend(item)
                else:
                    proximo.append(item)
            atual = proximo
        return atual

    @staticmethod
    def _flat_map(fonte, funcao):
        """Aplica e achata num passo so."""
        saida = []
        for item in fonte:
            r = funcao(item)
            if isinstance(r, (list, tuple)):
                saida.extend(r)
            else:
                saida.append(r)
        return saida

    # ── composicao ──────────────────────────────────────────

    @staticmethod
    def _reduce(fonte, funcao, inicial=None):
        if inicial is None:
            return functools.reduce(funcao, fonte)
        return functools.reduce(funcao, fonte, inicial)

    @staticmethod
    def _partial(funcao, *fixos, **nomeados):
        """Fixa alguns argumentos e devolve uma acao que espera o resto.

            dobrar := I.partial(multiplicar, 2)
            out dobrar(21)        // 42
        """
        return functools.partial(funcao, *fixos, **nomeados)

    @staticmethod
    def _compose(*acoes):
        """Encadeia da DIREITA para a esquerda, como a matematica.

            f := I.compose(dobrar, somar_um)
            f(3)    // dobrar(somar_um(3)) = 8
        """
        def composta(x):
            for acao in reversed(acoes):
                x = acao(x)
            return x
        return composta

    @staticmethod
    def _pipe(*acoes):
        """Encadeia da ESQUERDA para a direita, como se le.

        E 'compose' invertida — e a que quase todo mundo quer.
        """
        def encanada(x):
            for acao in acoes:
                x = acao(x)
            return x
        return encanada

    @staticmethod
    def _curry(funcao, aridade=2):
        """Uma acao de N argumentos vira N acoes de um argumento."""
        def acumular(recebidos):
            def receber(x):
                juntos = recebidos + [x]
                if len(juntos) >= aridade:
                    return funcao(*juntos)
                return acumular(juntos)
            return receber
        return acumular([])

    @staticmethod
    def _flip(funcao):
        """Inverte os dois primeiros argumentos."""
        return lambda a, b, *resto: funcao(b, a, *resto)

    @staticmethod
    def _identity(x):
        """Devolve o que recebe. Util como padrao de 'chave'."""
        return x

    @staticmethod
    def _constant(valor):
        """Uma acao que devolve sempre o mesmo, ignorando o argumento."""
        return lambda *_a, **_kw: valor

    @staticmethod
    def _once(funcao):
        """Roda uma vez; das proximas, devolve o mesmo resultado."""
        estado = {}

        def uma_vez(*a, **kw):
            if "v" not in estado:
                estado["v"] = funcao(*a, **kw)
            return estado["v"]
        return uma_vez

    @staticmethod
    def _memoize(funcao, tamanho=128):
        """Guarda o resultado por argumento.

        Derruba fibonacci de O(2^n) para O(n). O teto existe para o
        cache nao virar vazamento de memoria num programa longo.
        """
        return functools.lru_cache(maxsize=tamanho if tamanho > 0 else None)(funcao)

    @staticmethod
    def _cache_info(memoizada):
        """Acertos e erros do cache — para saber se ele esta ajudando."""
        info = getattr(memoizada, "cache_info", None)
        if info is None:
            return {}
        i = info()
        return {"acertos": i.hits, "erros": i.misses,
                "tamanho": i.currsize, "teto": i.maxsize}

    # ── operadores como acao ────────────────────────────────

    @staticmethod
    def _op(simbolo):
        """O operador como acao, para passar a 'reduce' e 'map'.

            I.reduce(xs, I.op("+"))
        """
        tabela = {
            "+": operator.add, "-": operator.sub, "*": operator.mul,
            "/": operator.truediv, "//": operator.floordiv,
            "~/": operator.floordiv, "%": operator.mod, "**": operator.pow,
            "==": operator.eq, "is": operator.eq,
            "!=": operator.ne, "isnt": operator.ne,
            "<": operator.lt, "smaller": operator.lt,
            ">": operator.gt, "bigger": operator.gt,
            "<=": operator.le, ">=": operator.ge,
            "and": lambda a, b: a and b, "or": lambda a, b: a or b,
            "min": min, "max": max,
        }
        acao = tabela.get(simbolo)
        if acao is None:
            from ...errors import ValueError_
            raise ValueError_(
                f"'{simbolo}' is not an operator this accepts.",
                nota=f"it takes: {', '.join(sorted(tabela))}",
                doc="colecoes")
        return acao

    @staticmethod
    def _attr(nome):
        """Uma acao que le um campo — para 'sorted_by' e 'map'."""
        def ler(obj):
            if isinstance(obj, dict):
                return obj.get(nome)
            campos = getattr(obj, "values", None) or getattr(obj, "fields", None)
            if isinstance(campos, dict):
                return campos.get(nome)
            return getattr(obj, nome, None)
        return ler

    @staticmethod
    def _item(indice):
        """Uma acao que le um indice ou chave."""
        return lambda obj: obj[indice]
