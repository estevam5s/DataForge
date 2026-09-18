# -*- coding: utf-8 -*-
"""Arcane.Tipos — perguntar sobre um tipo, e conferir sem levantar.

O que faltava
-------------
`typeof` responde o nome do tipo de um valor, e nada mais. Quem escreve
validação genérica, serialização ou um formulário a partir de um record
precisa de duas coisas que não existiam:

1. **os metadados de um `type` declarado** — ele é união? refinamento?
   opaco? qual é a base, qual é a regra?
2. **conferir sem levantar** — `Tipos.satisfaz(valor, "Positivo")`
   responde `yes`/`no`; o caminho que levanta já existia na anotação.

    type Positivo := Integer where valor bigger 0

    assert Tipos.satisfaz(5, "Positivo")
    assert no Tipos.satisfaz(-5, "Positivo")
    assert Tipos.de("Positivo")["especie"] is "refinamento"

Duas decisões
-------------
1. **A forma de um valor é estrutural, e não o nome do tipo.**
   `Tipos.forma((1, "a"))` responde `Tuple<Integer, String>`, e
   `Tipos.forma([1, 2])` responde `Cluster<Integer>` — é o que um
   gerador de esquema precisa, e é diferente do `typeof`, que responde
   `Tuple` e `Cluster`.

2. **`satisfaz` não executa a regra num valor da base errada.** A base
   vem antes, como em toda conferência de refinamento: perguntar
   `len(valor)` a um número daria um erro do interpretador em vez de um
   `no` honesto.
"""

from ..errors import DataForgeError
from ..tipos_nomeados import ALIAS, INTERSECAO, UNIAO

#: Como cada espécie se chama para quem lê a resposta.
_ESPECIE = {UNIAO: "uniao", INTERSECAO: "intersecao", ALIAS: "alias"}


def _interp():
    from ..interpreter import DFAction
    return DFAction._interpreter


def _no():
    interp = _interp()
    return interp._no_interno() if interp is not None else None


def declarados():
    """Os nomes de todo `type` declarado neste programa."""
    interp = _interp()
    if interp is None:
        return []
    return sorted(interp.tipos_nomeados.por_nome)


def de(nome):
    """Os metadados de um `type`, ou `void` se ele não existe."""
    interp = _interp()
    if interp is None:
        return None
    tipo = interp.tipos_nomeados.obter(str(nome))
    if tipo is None:
        return None
    especie = _ESPECIE.get(tipo.especie, tipo.especie)
    if tipo.regra is not None and especie == "alias":
        especie = "refinamento"
    return {
        "nome": tipo.nome,
        "especie": "opaco" if tipo.opaco else especie,
        "base": tipo.base,
        "partes": list(tipo.partes),
        "parametros": list(tipo.parametros),
        "regra": tipo.regra_texto or None,
        "opaco": tipo.opaco,
    }


def existe(nome):
    return de(nome) is not None


def satisfaz(valor, nome):
    """O valor serve para esse tipo? Responde `yes`/`no`, sem levantar."""
    interp = _interp()
    if interp is None:
        return False
    try:
        interp._check_type(valor, str(nome), "a value", _no())
        return True
    except DataForgeError:
        return False


def conferir(valor, nome):
    """O valor, ou o erro de sempre — o mesmo que a anotação levanta."""
    interp = _interp()
    if interp is None:
        return valor
    return interp._check_type(valor, str(nome), "a value", _no())


def nome_de(valor):
    """O mesmo que `typeof`, disponível como função de módulo."""
    interp = _interp()
    return interp._type_of(valor) if interp is not None else type(valor).__name__


def forma(valor, profundidade=3):
    """A forma ESTRUTURAL do valor: `Cluster<Integer>`, `Tuple<A, B>`…

    É o que um gerador de esquema precisa, e é diferente de `typeof`:
    `typeof([1, 2])` responde `Cluster`, e a forma responde
    `Cluster<Integer>`. Uma coleção de tipos misturados responde
    `Cluster<Any>` — dizer o primeiro tipo seria mentira.
    """
    from ..colecoes_tipadas import Tupla
    interp = _interp()
    if interp is None:
        return type(valor).__name__
    nome = interp._type_of(valor)
    if profundidade <= 0:
        return nome
    if isinstance(valor, Tupla):
        if not valor:
            return "Tuple"
        return f"Tuple<{', '.join(forma(i, profundidade - 1) for i in valor)}>"
    if isinstance(valor, (list, set, frozenset)):
        return f"{nome}<{_um_tipo(valor, profundidade)}>"
    if isinstance(valor, dict):
        return (f"Vault<{_um_tipo(valor.keys(), profundidade)}, "
                f"{_um_tipo(valor.values(), profundidade)}>")
    return nome


def _um_tipo(itens, profundidade):
    """O tipo comum dos itens, ou `Any` quando eles divergem."""
    formas = {forma(i, profundidade - 1) for i in itens}
    if not formas:
        return "Any"
    return formas.pop() if len(formas) == 1 else "Any"


def campos(valor):
    """Os campos de um record, de uma instância ou de um vault, com o tipo.

    É o que transforma um tipo em formulário, em tabela ou em esquema
    sem escrever a lista de campos à mão duas vezes.
    """
    from ..interpreter import DFInstance, DFRecord, DFRecordInstance
    if isinstance(valor, DFRecordInstance):
        declarados_do_record = valor.record.field_types
        return {nome: {"tipo": declarados_do_record.get(nome) or forma(v),
                       "valor": v}
                for nome, v in valor.values.items()}
    if isinstance(valor, DFRecord):
        return {nome: {"tipo": tipo or "Any", "valor": None}
                for nome, tipo in valor.field_types.items()}
    if isinstance(valor, DFInstance):
        return {nome: {"tipo": forma(v), "valor": v}
                for nome, v in valor.fields.items()
                if not nome.startswith("_")}
    if isinstance(valor, dict):
        return {str(nome): {"tipo": forma(v), "valor": v}
                for nome, v in valor.items()}
    return {}


def e_colecao(valor):
    from ..colecoes_tipadas import Tupla
    return isinstance(valor, (list, dict, set, frozenset, tuple, Tupla))


def e_imutavel(valor):
    """O valor muda? Texto, número, tupla, `Frozen` e record não mudam."""
    from ..colecoes_tipadas import Tupla
    from ..interpreter import DFRecordInstance
    from ..tipos_nomeados import Opaco
    return isinstance(valor, (bool, int, float, str, bytes, tuple, Tupla,
                              frozenset, DFRecordInstance, Opaco)) \
        or valor is None


class ArcaneTipos:
    """O dicionário que `adopt Arcane.Tipos` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Tipos",

            "declarados": declarados,
            "de": de,
            "existe": existe,
            "satisfaz": satisfaz,
            "conferir": conferir,
            "nome_de": nome_de,
            "forma": forma,
            "campos": campos,
            "e_colecao": e_colecao,
            "e_imutavel": e_imutavel,
        }
