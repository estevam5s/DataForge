"""
Arcane.Objetos — copiar, congelar, comparar e serializar objetos.

    adopt Arcane.Objetos as O

    copia := O.clonar(pedido)            rasa: os campos apontam para os mesmos valores
    funda := O.clonar_fundo(pedido)      funda: nada e compartilhado
    O.congelar(config)                   nenhum campo aceita escrita, para sempre
    O.igual(a, b)                        mesmo tipo e mesmos campos, recursivo
    v := O.para_vault(pedido)            {"$tipo": "Pedido", "id": 1, …}
    p := O.de_vault(v, [Pedido, Item])   so reconstroi os tipos da lista

─── Por que a desserializacao exige a lista de tipos ─────────────

Um JSON que chega de fora com "$tipo": "Admin" nao pode decidir qual
blueprint o programa constroi. E assim que desserializacao vira execucao
de codigo alheio em toda linguagem que deixou o dado escolher o tipo —
o pickle do Python e o ObjectInputStream do Java sao os exemplos
classicos. Aqui a lista e obrigatoria, e um tipo fora dela e recusado
com 'UnsafeDeserializationError'.

A reconstrucao tambem nao roda o 'setup': o construtor pede argumentos
que o dado nao tem, e roda-lo com 'void' produziria um objeto errado.
Os campos sao gravados, e em seguida as INVARIANTES sao conferidas — um
dado que chega violando a regra do tipo e recusado ali, e nao tres
telas depois.

─── Ciclos ─────────────────────────────────────────────────────

'pedido.cliente.pedidos[0] is pedido' e comum num grafo de objetos, e
serializar seguindo referencias daria recursao infinita. A segunda vez
que o mesmo objeto aparece ele vira {"$ref": n}, apontando para o
{"$id": n} da primeira.
"""

import json as _json


def _ler_opcoes(opcoes, padroes, onde):
    """Recusa a chave desconhecida E aplica os padroes."""
    from .opcoes import ler
    return {**padroes, **ler(dict(opcoes or {}), padroes, onde)}


def _interp():
    from ..interpreter import DFAction
    return DFAction._interpreter


def _i():
    from .. import interpreter as i
    return i


def _no():
    return _interp()._no_interno()


# ── copia ────────────────────────────────────────────────────

def _clonar(obj):
    """Copia rasa. Honra '__copy__' e '__clone__'."""
    import copy
    i = _i()
    if isinstance(obj, i.DFRecordInstance):
        return obj
    if isinstance(obj, (list, dict, set)):
        return copy.copy(obj)
    return copy.copy(obj)


def _clonar_fundo(obj):
    """Copia funda. Honra '__deepcopy__' e '__clone__'."""
    import copy
    return copy.deepcopy(obj)


# ── imutabilidade ────────────────────────────────────────────

def _congelar(obj, fundo=False):
    """Nenhum campo aceita escrita depois disto. Com fundo=yes, desce nos campos."""
    i = _i()
    from ..objetos import estado_de
    if isinstance(obj, i.DFInstance):
        estado_de(obj).congelado = True
        if fundo:
            for valor in list(obj.fields.values()):
                _congelar(valor, True)
        return obj
    if isinstance(obj, (i.DFRecordInstance, str, int, float, bool, type(None), tuple)):
        return obj
    if fundo and isinstance(obj, list):
        for item in obj:
            _congelar(item, True)
    if fundo and isinstance(obj, dict):
        for item in obj.values():
            _congelar(item, True)
    return obj


def _congelado(obj):
    i = _i()
    if isinstance(obj, i.DFInstance):
        return bool(obj._estado is not None and obj._estado.congelado)
    return isinstance(obj, (i.DFRecordInstance, str, int, float, bool, tuple, type(None)))


# ── igualdade, hash e ordem ──────────────────────────────────

def _igual(a, b):
    """Igualdade ESTRUTURAL: mesmo blueprint e campos iguais, recursivamente.

    O 'is' de duas instancias e identidade — e e o certo para entidade.
    Esta funcao responde a outra pergunta, a de objeto de valor, sem
    obrigar o blueprint a escrever '__eq__'.
    """
    return _igual_memo(a, b, set())


def _igual_memo(a, b, vistos):
    i = _i()
    if a is b:
        return True
    if isinstance(a, i.DFInstance) and isinstance(b, i.DFInstance):
        if a.blueprint is not b.blueprint:
            return False
        par = (id(a), id(b))
        if par in vistos:
            return True
        vistos.add(par)
        ca, cb = a.fields, b.fields
        if set(ca) != set(cb):
            return False
        return all(_igual_memo(ca[k], cb[k], vistos) for k in ca)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_igual_memo(x, y, vistos) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_igual_memo(a[k], b[k], vistos) for k in a)
    return a == b


def _identico(a, b):
    return a is b


def _hash(obj):
    """Um numero coerente com 'igual': objetos iguais dao o mesmo hash."""
    i = _i()
    if isinstance(obj, i.DFInstance):
        r = _interp()._chamar_magico(obj, "__hash__", [], _no())
        if r is not i._SEM_MAGICO:
            return hash(r)
        return hash((obj.blueprint.name,) + tuple(
            (k, _hash(v)) for k, v in sorted(obj.fields.items())))
    if isinstance(obj, list):
        return hash(tuple(_hash(x) for x in obj))
    if isinstance(obj, dict):
        return hash(tuple(sorted((str(k), _hash(v)) for k, v in obj.items())))
    try:
        return hash(obj)
    except TypeError:
        return hash(str(obj))


def _comparar_por(campos):
    """Uma acao de comparacao (-1, 0, 1) por uma lista de campos, em ordem.

        ordenados := O.ordenar(pessoas, ["sobrenome", "nome"])

    Ordem total: dois objetos so empatam se TODOS os campos empatam.
    """
    from .arcane_collections import _campo_de
    nomes = [campos] if isinstance(campos, str) else list(campos)

    def comparar(a, b):
        for nome in nomes:
            decrescente = nome.startswith("-")
            chave = nome[1:] if decrescente else nome
            va, vb = _campo_de(a, chave), _campo_de(b, chave)
            if va == vb:
                continue
            if va is None:
                r = -1
            elif vb is None:
                r = 1
            else:
                r = -1 if va < vb else 1
            return -r if decrescente else r
        return 0
    return comparar


def _ordenar(itens, campos):
    import functools
    return sorted(itens, key=functools.cmp_to_key(_comparar_por(campos)))


# ── serializacao ─────────────────────────────────────────────

_CONFIG_SERIAL = {"tipos": True, "privados": False, "versao": None}


def _para_vault(obj, opcoes=None):
    """O objeto como vault, com '$tipo' e referencias para ciclos.

    Por padrao so os campos PUBLICOS saem: serializar e publicar, e o
    que o autor marcou como private nao foi feito para sair do objeto.
    '{"privados": yes}' inclui os demais, para persistencia propria.
    """
    opcoes = _ler_opcoes(opcoes or {}, _CONFIG_SERIAL, "Objetos.para_vault")
    ids = {}
    return _serializar(obj, opcoes, ids)


def _serializar(valor, opcoes, ids):
    i = _i()
    if isinstance(valor, (str, int, float, bool, type(None))):
        return valor
    if isinstance(valor, (list, tuple)):
        return [_serializar(x, opcoes, ids) for x in valor]
    if isinstance(valor, dict):
        return {str(k): _serializar(v, opcoes, ids) for k, v in valor.items()}
    if isinstance(valor, i.DFEnumMember):
        return {"$enum": valor.enum_name, "nome": valor.name} if opcoes["tipos"] \
            else valor.value
    if isinstance(valor, i.DFRecordInstance):
        saida = {"$tipo": valor.record.name} if opcoes["tipos"] else {}
        for k, v in valor.values.items():
            saida[k] = _serializar(v, opcoes, ids)
        return saida
    if isinstance(valor, i.DFInstance):
        if id(valor) in ids:
            return {"$ref": ids[id(valor)]}
        ids[id(valor)] = len(ids) + 1
        bp = valor.blueprint
        saida = {}
        if opcoes["tipos"]:
            saida["$tipo"] = bp.name
            saida["$id"] = ids[id(valor)]
            versao = opcoes["versao"] if opcoes["versao"] is not None else \
                bp.statics.get("versao_do_esquema")
            if versao is not None:
                saida["$versao"] = versao
        for k, v in valor.fields.items():
            if not opcoes["privados"] and bp.visibilidade_de(k) != "public":
                continue
            saida[k] = _serializar(v, opcoes, ids)
        vigias = bp.vigias
        if vigias is not None and "on_serialize" in vigias.ganchos:
            trocado = _interp()._gancho_de_vigia(vigias, "on_serialize",
                                                 [valor, saida], _no())
            if isinstance(trocado, dict):
                saida = trocado
        return saida
    from ..errors import SerializationError
    raise SerializationError(
        f"{_interp()._nome_do_tipo(valor)} cannot be serialized.",
        dica="serialize the data it holds, not the value itself",
        doc="oop/objetos")


def _de_vault(dado, tipos, opcoes=None):
    """Reconstroi objetos a partir de um vault — so dos tipos listados."""
    i = _i()
    from ..errors import UnsafeDeserializationError, TypeError_
    if isinstance(tipos, i.DFBlueprint) or isinstance(tipos, i.DFRecord):
        tipos = [tipos]
    if not isinstance(tipos, (list, tuple)) or not tipos:
        raise TypeError_(
            "Objetos.de_vault needs the list of allowed types.",
            nota="the data does not get to choose which blueprint is built",
            dica="Objetos.de_vault(dado, [Pedido, Item])",
            doc="oop/objetos")
    permitidos = {}
    enums = {}
    for t in tipos:
        if isinstance(t, i.DFEnum):
            enums[t.name] = t
        elif isinstance(t, (i.DFBlueprint, i.DFRecord)):
            permitidos[t.name] = t
    return _desserializar(dado, permitidos, enums, {}, [])


def _desserializar(dado, permitidos, enums, feitos, pendentes):
    i = _i()
    from ..errors import UnsafeDeserializationError
    if isinstance(dado, list):
        return [_desserializar(x, permitidos, enums, feitos, pendentes) for x in dado]
    if not isinstance(dado, dict):
        return dado
    if "$ref" in dado and len(dado) == 1:
        alvo = feitos.get(dado["$ref"])
        if alvo is None:
            from ..errors import SerializationError
            raise SerializationError(
                f"The data refers to object {dado['$ref']} before declaring it.",
                doc="oop/objetos")
        return alvo
    if "$enum" in dado:
        enum = enums.get(dado["$enum"])
        if enum is None:
            raise UnsafeDeserializationError(
                f"The data asks for the enum '{dado['$enum']}', which is not in "
                f"the allowed list.", doc="oop/objetos")
        return enum.members[dado["nome"]]
    if "$tipo" not in dado:
        return {k: _desserializar(v, permitidos, enums, feitos, pendentes)
                for k, v in dado.items()}
    nome = dado["$tipo"]
    molde = permitidos.get(nome)
    if molde is None:
        raise UnsafeDeserializationError(
            f"The data asks for the type '{nome}', which is not in the allowed "
            f"list.",
            nota="allowed: " + (", ".join(sorted(permitidos)) or "nothing"),
            dica="add the type to the list if it is expected; if it is not, "
                 "the data cannot be trusted",
            doc="oop/objetos")
    campos = {k: v for k, v in dado.items() if not k.startswith("$")}
    interp = _interp()
    if isinstance(molde, i.DFRecord):
        valores = {k: _desserializar(v, permitidos, enums, feitos, pendentes)
                   for k, v in campos.items()}
        return interp._call(molde, [], valores, _no(), interp.global_env)
    vigias = molde.vigias
    if vigias is not None and "on_deserialize" in vigias.ganchos:
        trocado = interp._gancho_de_vigia(vigias, "on_deserialize",
                                          [molde, dict(campos)], _no())
        if isinstance(trocado, dict):
            campos = {k: v for k, v in trocado.items() if not k.startswith("$")}
    if molde.is_abstract or molde.e_contrato:
        raise UnsafeDeserializationError(
            f"The data asks to build '{nome}', which is abstract.", doc="oop/objetos")
    classe = i.DFInstanceFinal if molde.finalizador is not None else i.DFInstance
    obj = classe(molde)
    if "$id" in dado:
        feitos[dado["$id"]] = obj
    for nome_campo, _t, padrao, _v in molde.fields_decl:
        interp._gravar_campo_cru(obj, nome_campo, interp._copiar_padrao(padrao))
    for k, v in campos.items():
        interp._gravar_campo_cru(obj, k, _desserializar(v, permitidos, enums,
                                                        feitos, pendentes))
    if vigias is not None and vigias.invariantes:
        interp._conferir_invariantes(obj, _no())
    return obj


def _para_json(obj, opcoes=None, indent=None):
    return _json.dumps(_para_vault(obj, opcoes), ensure_ascii=False, indent=indent)


def _de_json(texto, tipos):
    return _de_vault(_json.loads(texto), tipos)


class ArcaneObjetos:
    """Copia, imutabilidade, igualdade e serializacao de objetos."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Objetos",
            "clonar": _clonar,
            "clonar_fundo": _clonar_fundo,
            "congelar": _congelar,
            "congelado": _congelado,
            "igual": _igual,
            "identico": _identico,
            "hash": _hash,
            "comparar_por": _comparar_por,
            "ordenar": _ordenar,
            "para_vault": _para_vault,
            "de_vault": _de_vault,
            "para_json": _para_json,
            "de_json": _de_json,
        }
