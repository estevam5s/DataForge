"""
Cluster<T>, Vault<K, V> e Set<T> — o tipo do que esta DENTRO.

Tres pecas, usadas pelo parser, pelo analisador e pelo interpretador:

    partir("Vault<String, Cluster<Integer>>")
        -> ("Vault", ("String", "Cluster<Integer>"))

    ClusterTipado / VaultTipado / SetTipado
        a colecao que recusa uma insercao fora do tipo

─── Por que subclasse de list, dict e set ──────────────────────

Porque todo o resto da linguagem — 'len', 'cycle', o '>>', o JSON, a
igualdade, os metodos de cluster e de vault, a ponte para o Python —
pergunta 'isinstance(x, list)' e segue funcionando sem saber que a
colecao e tipada. Um embrulho proprio obrigaria cada um desses lugares a
aprender uma classe nova, e o que ficasse de fora quebraria calado.

─── Por que so a colecao que NASCE tipada e guardada ───────────

A guarda de insercao vale para a colecao criada na declaracao — literal,
compreensao, padrao de campo. Uma colecao que ja existia e conferida
item a item na entrada e continua sendo o MESMO objeto. A alternativa,
copiar para poder guardar, mudaria a semantica de toda acao que recebe
uma lista para modificar: 'acrescentar(xs: Cluster<Integer>, n)' passaria
a acrescentar numa copia que ninguem ve, e nada avisaria.

─── Custo ──────────────────────────────────────────────────────

A anotacao sem '<' nao passa por aqui: o interpretador pergunta
'"<" in tipo', que e uma busca de caractere. Uma colecao tipada paga
UMA conferencia por item inserido; a conferencia na fronteira e O(n), e
por isso so acontece onde a anotacao pede.
"""

from functools import lru_cache

#: As colecoes que declaram o tipo do conteudo, e quantos tipos cada uma leva.
COLECOES = {"Cluster": 1, "Vault": 2, "Set": 1}

#: Como a doc escreve cada uma — e o que a mensagem de erro mostra.
FORMA = {"Cluster": "Cluster<T>", "Vault": "Vault<K, V>", "Set": "Set<T>"}


@lru_cache(maxsize=512)
def partir(tipo):
    """'Base<A, B<C>>' -> ('Base', ('A', 'B<C>')). Sem '<', (tipo, ())."""
    if "<" not in tipo:
        return tipo, ()
    inicio = tipo.index("<")
    base = tipo[:inicio].strip()
    miolo = tipo[inicio + 1:tipo.rindex(">")]
    partes, profundidade, atual = [], 0, []
    for ch in miolo:
        if ch == "<":
            profundidade += 1
        elif ch == ">":
            profundidade -= 1
        if ch == "," and profundidade == 0:
            partes.append("".join(atual).strip())
            atual = []
        else:
            atual.append(ch)
    partes.append("".join(atual).strip())
    return base, tuple(partes)


def juntar(base, argumentos):
    return f"{base}<{', '.join(argumentos)}>" if argumentos else base


def e_generico(tipo):
    return isinstance(tipo, str) and "<" in tipo


# ═════════════════════════════════════════════════════════════
#  As colecoes que guardam
# ═════════════════════════════════════════════════════════════

def _conferir(valor, tipo, o_que):
    """Confere um valor contra um tipo, pelo mesmo '_check_type' das anotacoes."""
    from .interpreter import DFAction
    interp = DFAction._interpreter
    if interp is None:
        return
    interp._check_type(valor, tipo, o_que, interp._no_interno())


def _recusa(colecao, valor, operacao, tipo_item, erro):
    """O erro de insercao, com a colecao inteira no texto."""
    from .errors import TypeError_
    from .interpreter import DFAction
    interp = DFAction._interpreter
    obtido = interp._type_of(valor) if interp else type(valor).__name__
    return TypeError_(
        f"{colecao._tipo} only holds {tipo_item}, and {operacao} got {obtido}.",
        # o motivo interno so acrescenta quando o item e ele mesmo uma
        # colecao tipada: la esta a posicao do que falhou dentro dela
        nota=getattr(erro, "message", str(erro)) if "<" in tipo_item else "",
        dica=f"insert a {tipo_item}, or widen the annotation "
             f"(Any accepts everything)",
        doc="tipos")


class ClusterTipado(list):
    """Um Cluster que recusa item fora de T."""

    __slots__ = ("_tipo", "_item")

    def __init__(self, itens=(), tipo="Cluster<Any>"):
        super().__init__(itens)
        self._tipo = tipo
        self._item = partir(tipo)[1][0]

    def _guardar(self, valor, operacao):
        from .errors import TypeError_
        try:
            _conferir(valor, self._item, operacao)
        except TypeError_ as erro:
            raise _recusa(self, valor, operacao, self._item, erro) from None
        return valor

    def append(self, valor):
        super().append(self._guardar(valor, "append"))

    def insert(self, posicao, valor):
        super().insert(posicao, self._guardar(valor, "insert"))

    def extend(self, valores):
        super().extend([self._guardar(v, "extend") for v in valores])

    def __setitem__(self, posicao, valor):
        if isinstance(posicao, slice):
            valor = [self._guardar(v, "a slice assignment") for v in valor]
        else:
            valor = self._guardar(valor, f"[{posicao}] :=")
        super().__setitem__(posicao, valor)

    def __iadd__(self, valores):
        self.extend(valores)
        return self

    def __add__(self, outros):
        return ClusterTipado([*self, *[self._guardar(v, "+") for v in outros]],
                             self._tipo)

    def copy(self):
        return ClusterTipado(self, self._tipo)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        import copy
        return ClusterTipado([copy.deepcopy(v, memo) for v in self], self._tipo)

    def __reduce__(self):
        # atravessa processo e pickle como a colecao comum que e por fora
        return (list, (list(self),))


class VaultTipado(dict):
    """Um Vault que recusa chave fora de K e valor fora de V."""

    __slots__ = ("_tipo", "_chave", "_valor")

    def __init__(self, pares=(), tipo="Vault<Any, Any>"):
        super().__init__(pares)
        self._tipo = tipo
        self._chave, self._valor = partir(tipo)[1]

    def _guardar(self, chave, valor, operacao):
        from .errors import TypeError_
        try:
            _conferir(chave, self._chave, operacao)
        except TypeError_ as erro:
            raise _recusa(self, chave, f"the key of {operacao}", self._chave,
                          erro) from None
        try:
            _conferir(valor, self._valor, operacao)
        except TypeError_ as erro:
            raise _recusa(self, valor, f"{operacao} at key {chave!r}",
                          self._valor, erro) from None
        return valor

    def __setitem__(self, chave, valor):
        super().__setitem__(chave, self._guardar(chave, valor, f"[{chave!r}] :="))

    def setdefault(self, chave, valor=None):
        if chave not in self:
            self[chave] = valor
        return self[chave]

    def update(self, *outros, **nomeados):
        for outro in outros:
            pares = outro.items() if hasattr(outro, "items") else outro
            for chave, valor in pares:
                self[chave] = valor
        for chave, valor in nomeados.items():
            self[chave] = valor

    def __ior__(self, outro):
        self.update(outro)
        return self

    def copy(self):
        return VaultTipado(self, self._tipo)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        import copy
        return VaultTipado({k: copy.deepcopy(v, memo) for k, v in self.items()},
                           self._tipo)

    def __reduce__(self):
        return (dict, (dict(self),))


class SetTipado(set):
    """Um Set que recusa item fora de T."""

    __slots__ = ("_tipo", "_item")

    def __init__(self, itens=(), tipo="Set<Any>"):
        super().__init__(itens)
        self._tipo = tipo
        self._item = partir(tipo)[1][0]

    def _guardar(self, valor, operacao):
        from .errors import TypeError_
        try:
            _conferir(valor, self._item, operacao)
        except TypeError_ as erro:
            raise _recusa(self, valor, operacao, self._item, erro) from None
        return valor

    def add(self, valor):
        super().add(self._guardar(valor, "add"))

    def update(self, *outros):
        for outro in outros:
            for valor in outro:
                self.add(valor)

    def __ior__(self, outro):
        self.update(outro)
        return self

    def copy(self):
        return SetTipado(self, self._tipo)

    def __reduce__(self):
        return (set, (set(self),))


TIPADAS = (ClusterTipado, VaultTipado, SetTipado)


def tipar(valor, tipo, parametros=()):
    """A colecao tipada com o conteudo de 'valor'. Quem chama ja conferiu.

    'parametros' sao os '<T>' da declaracao em volta. Uma colecao cujo
    item e um parametro de tipo NAO e guardada: 'blueprint Pilha<T>' com
    'itens: Cluster<T> := []' recusaria 'append(1)', e o generico
    deixaria de servir para o unico uso que ele tem.
    """
    base, argumentos = partir(tipo)
    if parametros and any(a in parametros for a in argumentos):
        return valor
    if base == "Cluster" and isinstance(valor, list):
        if isinstance(valor, ClusterTipado) and valor._tipo == tipo:
            return valor
        return ClusterTipado([_tipar_se_literal(v, argumentos[0]) for v in valor], tipo)
    if base == "Vault" and isinstance(valor, dict):
        if isinstance(valor, VaultTipado) and valor._tipo == tipo:
            return valor
        return VaultTipado({k: _tipar_se_literal(v, argumentos[1])
                            for k, v in valor.items()}, tipo)
    if base == "Set" and isinstance(valor, (set, frozenset)):
        if isinstance(valor, SetTipado) and valor._tipo == tipo:
            return valor
        return SetTipado(valor, tipo)
    return valor


def _tipar_se_literal(valor, tipo):
    """Um item que e colecao, num tipo aninhado, nasce tipado tambem.

    'm: Vault<String, Cluster<Integer>> := {"a": [1]}' — o [1] de dentro
    nasceu no mesmo literal, e 'm["a"].append("x")' tem de ser recusado
    como seria no de fora.
    """
    if e_generico(tipo) and type(valor) in (list, dict, set):
        return tipar(valor, tipo)
    return valor
