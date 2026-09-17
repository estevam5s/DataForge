"""
Arcane.Reflexo — o programa olhando para os proprios tipos.

    adopt Arcane.Reflexo as R

    R.metodos(Pedido)             [{nome, parametros, visibilidade, …}]
    R.campos(pedido)              [{nome, tipo, readonly, anotacoes, …}]
    R.mro(Gerente)                [Gerente, Funcionario, Pessoa]
    R.herdeiros(Forma)            [Circulo, Quadrado]
    R.invocar(pedido, "total")    chama pelo nome
    R.diagrama([Pedido, Item])    o diagrama de classes, em Mermaid

─── Reflexao nao e porta dos fundos ─────────────────────────────

Toda leitura, escrita e chamada feita por aqui passa pela MESMA
conferencia de visibilidade que 'obj.campo' passa. Um 'private' continua
private quando o nome chega por texto: se a reflexao abrisse o que o
autor fechou, 'private' seria so uma sugestao para quem nao conhece este
modulo — e e exatamente quem conhece que precisa ser contido.

As listas (campos, metodos) mostram os membros nao publicos com a
visibilidade ao lado, porque saber que existem e documentacao. O VALOR
de um membro fechado, nao.

─── Tipos criados em execucao ──────────────────────────────────

'R.criar_blueprint' monta um blueprint a partir de um vault. Ele passa
pelas mesmas regras de uma declaracao escrita: mae 'final' recusa, mae
'sealed' de outro arquivo recusa, contrato nao cumprido recusa. Um tipo
dinamico que escapasse das regras seria o caminho para contorna-las.
"""

import difflib


def _ler_opcoes(opcoes, padroes, onde):
    """Recusa a chave desconhecida E aplica os padroes."""
    from .opcoes import ler
    return {**padroes, **ler(dict(opcoes or {}), padroes, onde)}


def _interp():
    from ..interpreter import DFAction
    interp = DFAction._interpreter
    if interp is None:
        raise RuntimeError("Reflexo needs a running interpreter")
    return interp


def _classes():
    from .. import interpreter as i
    return i


def _molde(alvo):
    """O blueprint de uma instancia, ou o proprio blueprint."""
    i = _classes()
    if isinstance(alvo, i.DFBlueprint):
        return alvo
    if isinstance(alvo, i.DFInstance):
        return alvo.blueprint
    if isinstance(alvo, i.DFRecordInstance):
        return alvo.record
    if isinstance(alvo, (i.DFRecord, i.DFEnum)):
        return alvo
    return None


def _exigir_molde(alvo, funcao):
    molde = _molde(alvo)
    if molde is None:
        from ..errors import TypeError_
        interp = _interp()
        raise TypeError_(
            f"Reflexo.{funcao} expects a blueprint, a record or an instance, "
            f"and got {interp._nome_do_tipo(alvo)}.",
            dica="pass the blueprint itself (Pedido) or an object (spawn Pedido())",
            doc="oop/reflexao")
    return molde


def _no():
    return _interp()._no_interno()


def _escopo_de_fora():
    """O escopo de quem nao esta dentro de blueprint nenhum."""
    return _interp().global_env


# ── tipos ────────────────────────────────────────────────────

def _tipo(valor):
    """O nome do tipo, no vocabulario da linguagem — o mesmo de typeof."""
    return _interp()._type_of(valor)


def _nome(alvo):
    molde = _molde(alvo)
    if molde is not None:
        return molde.name
    return getattr(alvo, "name", None) or _tipo(alvo)


def _especie(alvo):
    """'blueprint', 'contract', 'meta blueprint', 'trait', 'record', 'enum',
    'instance', 'record instance' ou o tipo do valor."""
    i = _classes()
    if isinstance(alvo, i.DFBlueprint):
        if alvo.e_contrato:
            return "contract"
        if alvo.e_meta:
            return "meta blueprint"
        if getattr(alvo, "e_trait", False):
            return "trait"
        return "blueprint"
    if isinstance(alvo, i.DFInstance):
        return "instance"
    if isinstance(alvo, i.DFRecord):
        return "record"
    if isinstance(alvo, i.DFRecordInstance):
        return "record instance"
    if isinstance(alvo, i.DFEnum):
        return "enum"
    return _tipo(alvo)


def _modificadores_de_blueprint(molde):
    saida = []
    if getattr(molde, "is_abstract", False) and not molde.e_contrato:
        saida.append("abstract")
    if molde.e_final:
        saida.append("final")
    if molde.e_selado:
        saida.append("sealed")
    if molde.e_meta:
        saida.append("meta")
    return saida


# ── membros ──────────────────────────────────────────────────

def _assinatura_de(acao):
    return {
        "nome": acao.name,
        "parametros": list(acao.params),
        "tipos": dict(acao.param_types),
        "padroes": [p for p in acao.params if p in acao.defaults],
        "retorno": acao.return_type or None,
        "genericos": list(acao.type_params),
        "async": bool(acao.is_async),
        "stream": bool(acao.is_generator),
    }


def _modificadores(alvo, membro):
    """Os modificadores de um membro: ['private', 'static', 'final', …]."""
    molde = _exigir_molde(alvo, "modificadores")
    saida = []
    visib = molde.visibilidade_de(membro) if hasattr(molde, "visibilidade_de") else "public"
    saida.append(visib)
    metodos = getattr(molde, "methods", {}) or {}
    acao = metodos.get(membro)
    if membro in getattr(molde, "static_methods", ()) or (
            membro in getattr(molde, "statics", {}) and acao is None):
        saida.append("static")
    if membro in getattr(molde, "constantes", ()):
        saida.append("steady")
    if acao is not None and getattr(acao, "is_abstract", False) or \
            membro in getattr(molde, "abstract_methods", ()):
        saida.append("abstract")
    if membro in getattr(molde, "final_methods", ()):
        saida.append("final")
    if acao is not None and acao.extras is not None:
        if acao.extras.variantes:
            saida.append("overload")
        if acao.extras.exclusivo:
            saida.append("exclusive")
    if membro in getattr(molde, "somente_leitura", ()):
        saida.append("readonly")
    prop = molde.buscar_propriedade(membro) if hasattr(molde, "buscar_propriedade") else None
    if prop and prop.get("lazy"):
        saida.append("lazy")
    return saida


def _metodos(alvo):
    """Os metodos, com assinatura, visibilidade, dono e modificadores."""
    i = _classes()
    molde = _exigir_molde(alvo, "metodos")
    saida = []
    metodos = getattr(molde, "methods", {}) or {}
    for nome in sorted(metodos):
        acao = metodos[nome]
        if not isinstance(acao, i.DFAction):
            continue
        item = _assinatura_de(acao)
        if acao.extras is not None and acao.extras.variantes:
            item["variantes"] = [_assinatura_de(v) for v in acao.extras.variantes]
        dono = getattr(acao, "dono", None)
        item["dono"] = getattr(dono, "name", None) or getattr(acao, "owner", None)
        item["modificadores"] = _modificadores(molde, nome)
        item["visibilidade"] = item["modificadores"][0]
        item["anotacoes"] = list(getattr(acao, "__metadados__", None) or [])
        saida.append(item)
    for nome, assinatura in sorted((getattr(molde, "assinaturas", {}) or {}).items()):
        if nome not in metodos:
            item = _assinatura_de(assinatura)
            item["dono"] = getattr(assinatura, "owner", molde.name)
            item["modificadores"] = ["public", "abstract"]
            item["visibilidade"] = "public"
            item["anotacoes"] = []
            saida.append(item)
    return saida


def _campos(alvo):
    """Os campos declarados, com tipo, visibilidade, readonly e anotacoes."""
    i = _classes()
    molde = _exigir_molde(alvo, "campos")
    if isinstance(molde, i.DFRecord):
        return [{"nome": n, "tipo": t, "visibilidade": "public",
                 "readonly": True, "anotacoes": []}
                for n, t in molde.field_types.items()]
    vistos = []
    saida = []

    def acrescentar(nome, tipo):
        if nome in vistos:
            return
        vistos.append(nome)
        saida.append({
            "nome": nome,
            "tipo": tipo,
            "visibilidade": molde.visibilidade_de(nome),
            "readonly": nome in molde.somente_leitura,
            "anotacoes": list(molde.metadados_de_campo.get(nome, [])),
            "descritor": nome in molde.descritores,
        })

    for nome in molde.constructor_params:
        acrescentar(nome, molde.tipos_do_cabecalho.get(nome))
    for nome, tipo, _padrao, _visib in molde.fields_decl:
        acrescentar(nome, tipo)
    if isinstance(alvo, i.DFInstance):
        for nome in alvo.fields:
            acrescentar(nome, None)
    return saida


def _propriedades(alvo):
    molde = _exigir_molde(alvo, "propriedades")
    saida = []
    for nome, prop in sorted((getattr(molde, "properties", {}) or {}).items()):
        saida.append({"nome": nome, "get": "get" in prop, "set": "set" in prop,
                      "lazy": bool(prop.get("lazy")),
                      "visibilidade": molde.visibilidade_de(nome)})
    for nome in sorted(getattr(molde, "propriedades_exigidas", ()) or ()):
        if nome not in (getattr(molde, "properties", {}) or {}):
            saida.append({"nome": nome, "get": True, "set": False, "lazy": False,
                          "visibilidade": "public", "exigida": True})
    return saida


def _operadores(alvo):
    molde = _exigir_molde(alvo, "operadores")
    simbolos = sorted((getattr(molde, "operators", {}) or {}))
    magicos = sorted(n for n in (getattr(molde, "methods", {}) or {})
                     if n.startswith("__") and n.endswith("__"))
    return {"operadores": simbolos, "magicos": magicos}


def _estaticos(alvo):
    """Os estaticos PUBLICOS, com o valor."""
    i = _classes()
    molde = _exigir_molde(alvo, "estaticos")
    saida = {}
    for nome, valor in (getattr(molde, "statics", {}) or {}).items():
        if isinstance(valor, i.DFAction):
            continue
        if molde.visibilidade_de(nome) == "public":
            saida[nome] = valor
    return saida


def _membros(alvo):
    """Todos os nomes que 'alvo.' oferece; honra '__dir__'."""
    i = _classes()
    if isinstance(alvo, i.DFInstance):
        r = _interp()._chamar_magico(alvo, "__dir__", [], _no())
        if r is not i._SEM_MAGICO:
            return sorted(r)
    molde = _exigir_molde(alvo, "membros")
    nomes = set(getattr(molde, "methods", {}) or {})
    nomes |= set(getattr(molde, "properties", {}) or {})
    nomes |= set(getattr(molde, "statics", {}) or {})
    nomes |= {c[0] for c in getattr(molde, "fields_decl", [])}
    nomes |= set(getattr(molde, "constructor_params", []))
    if isinstance(alvo, i.DFInstance):
        nomes |= set(alvo.fields)
    return sorted(n for n in nomes if molde.visibilidade_de(n) == "public"
                  or not hasattr(molde, "visibilidade_de"))


# ── heranca ──────────────────────────────────────────────────

def _maes(alvo):
    return list(_exigir_molde(alvo, "maes").parents)


def _mro(alvo):
    molde = _exigir_molde(alvo, "mro")
    return list(molde.linhagem()) if hasattr(molde, "linhagem") else [molde]


def _herdeiros(alvo):
    molde = _exigir_molde(alvo, "herdeiros")
    return [f for f in (ref() for ref in getattr(molde, "herdeiros", [])) if f is not None]


def _descendentes(alvo):
    saida = []
    pendentes = _herdeiros(alvo)
    while pendentes:
        atual = pendentes.pop(0)
        if atual not in saida:
            saida.append(atual)
            pendentes.extend(_herdeiros(atual))
    return saida


def _traits(alvo):
    return list(getattr(_exigir_molde(alvo, "traits"), "traits", []) or [])


def _contratos(alvo):
    """Todos os traits e contratos, inclusive os que um contrato estende."""
    return sorted(getattr(_exigir_molde(alvo, "contratos"), "contratos_todos", ()) or ())


def _descende(a, b):
    """'a' e 'b', descende de 'b', ou adota 'b'? Honra '__subclasscheck__'."""
    i = _classes()
    ma, mb = _molde(a), _molde(b)
    if ma is None or mb is None:
        return False
    if isinstance(mb, i.DFBlueprint):
        gancho = i.Interpreter._achar_magico_no_molde(mb, "__subclasscheck__")
        if gancho is not None:
            return bool(_interp()._call_action(gancho, [ma], {}, _no(), None))
    if not isinstance(ma, i.DFBlueprint):
        return ma is mb
    return (any(x is mb for x in ma.linhagem())
            or mb.name in getattr(ma, "contratos_todos", ()))


def _e_instancia(valor, molde):
    """Honra '__instancecheck__' do molde, como 'instanceof'."""
    i = _classes()
    if isinstance(molde, i.DFBlueprint):
        gancho = i.Interpreter._achar_magico_no_molde(molde, "__instancecheck__")
        if gancho is not None:
            return bool(_interp()._call_action(gancho, [valor], {}, _no(), None))
    alvo = _molde(valor)
    return alvo is not None and _descende(alvo, molde)


def _meta(alvo):
    """A metaclasse que governa o blueprint, ou void."""
    return getattr(_exigir_molde(alvo, "meta"), "meta_blueprint", None)


def _meta_instancia(alvo):
    """O objeto da metaclasse — o 'self' dos ganchos, onde ela guarda estado."""
    meta = _meta(alvo)
    if meta is None:
        return None
    return _interp()._instancia_de_meta(meta)


def _anotacoes(alvo, membro=None):
    """Os decoradores de um alvo — ou de um membro dele, campo inclusive."""
    if membro is None:
        return list(getattr(alvo, "__metadados__", None) or [])
    molde = _exigir_molde(alvo, "anotacoes")
    if membro in molde.metadados_de_campo:
        return list(molde.metadados_de_campo[membro])
    acao = (getattr(molde, "methods", {}) or {}).get(membro)
    if acao is not None:
        return list(getattr(acao, "__metadados__", None) or [])
    prop = molde.buscar_propriedade(membro) or {}
    for chave in ("get", "set"):
        if chave in prop:
            return list(getattr(prop[chave], "__metadados__", None) or [])
    return []


def _documentacao(alvo):
    """O texto de '__doc__', quando o blueprint declara."""
    i = _classes()
    if isinstance(alvo, i.DFInstance):
        r = _interp()._chamar_magico(alvo, "__doc__", [], _no())
        if r is not i._SEM_MAGICO:
            return r
    molde = _molde(alvo)
    acao = (getattr(molde, "methods", {}) or {}).get("__doc__") if molde else None
    if acao is not None and "__doc__" in getattr(molde, "static_methods", ()):
        return _interp()._call_action(acao, [], {}, _no(), None)
    return None


# ── registro ─────────────────────────────────────────────────

def _blueprints():
    """Todo blueprint e contrato declarado ate agora, na ordem."""
    registro = getattr(_interp(), "blueprints_declarados", None) or []
    return [bp for bp in (ref() for ref in registro) if bp is not None]


def _procurar(nome):
    for bp in reversed(_blueprints()):
        if bp.name == nome:
            return bp
    return None


# ── dinamico ─────────────────────────────────────────────────

def _instanciar(molde, args=None, nomeados=None):
    interp = _interp()
    return interp._instanciar(_exigir_molde(molde, "instanciar"),
                              list(args or []), dict(nomeados or {}), _no(),
                              _escopo_de_fora())


def _tem(obj, nome):
    i = _classes()
    molde = _molde(obj)
    if molde is None:
        return isinstance(obj, dict) and nome in obj
    if isinstance(obj, i.DFInstance) and nome in obj.fields:
        return True
    return nome in _membros(obj) or (
        nome in (getattr(molde, "methods", {}) or {}))


def _ler(obj, nome):
    interp = _interp()
    no = _no_com_membro(nome)
    return interp._ler_membro(obj, no, _escopo_de_fora(), membro=nome)


def _escrever(obj, nome, valor):
    interp = _interp()
    interp._escrever_membro(obj, nome, valor, _no_com_membro(nome), _escopo_de_fora())
    return valor


def _invocar(obj, nome, args=None, nomeados=None):
    interp = _interp()
    from .. import ast_nodes as ast
    no = ast.MethodCall(object=None, method=nome, args=[], kwargs={})
    return interp._chamar_metodo(obj, list(args or []), dict(nomeados or {}), no,
                                 _escopo_de_fora())


def _no_com_membro(nome):
    from .. import ast_nodes as ast
    return ast.MemberAccess(object=None, member=nome)


def _cumpre(obj, contrato):
    """Tem todos os metodos e propriedades do contrato? Por FORMA, nao por nome.

    'with Contrato' e a promessa nominal. Isto e a pergunta estrutural —
    duck typing com verificacao: um objeto de outra biblioteca que nunca
    ouviu falar do contrato pode cumpri-lo.
    """
    return not _faltando(obj, contrato)


def _faltando(obj, contrato):
    """O que falta para cumprir o contrato: ['salvar(item)', 'get total']."""
    i = _classes()
    molde = _exigir_molde(contrato, "faltando")
    alvo = _molde(obj)
    faltam = []
    for nome, assinatura in sorted((getattr(molde, "assinaturas", {}) or {}).items()):
        acao = (getattr(alvo, "methods", {}) or {}).get(nome) if alvo else None
        if not isinstance(acao, i.DFAction) or getattr(acao, "is_abstract", False):
            faltam.append(f"{nome}({', '.join(assinatura.params)})")
            continue
        if acao.extras is None or not acao.extras.variantes:
            if not i.Interpreter._aridade_compativel(acao, assinatura):
                faltam.append(f"{nome}({', '.join(assinatura.params)})")
    for nome in sorted(molde.abstract_methods - set(getattr(molde, "assinaturas", {}))):
        if not alvo or nome not in (getattr(alvo, "methods", {}) or {}):
            faltam.append(f"{nome}()")
    for prop in sorted(getattr(molde, "propriedades_exigidas", ()) or ()):
        tem = alvo is not None and (
            (alvo.buscar_propriedade(prop) or {}).get("get") is not None
            or prop in {c[0] for c in alvo.fields_decl}
            or prop in alvo.constructor_params
            or (isinstance(obj, i.DFInstance) and prop in obj.fields))
        if not tem:
            faltam.append(f"get {prop}")
    return faltam


def _definir_metodo(molde, nome, acao):
    """Acrescenta um metodo em execucao. Recusa final, sealed de fora e substituicao."""
    i = _classes()
    from ..errors import AugmentError
    interp = _interp()
    molde = _exigir_molde(molde, "definir_metodo")
    if not isinstance(molde, i.DFBlueprint) or molde.e_contrato:
        raise AugmentError(f"Only a blueprint accepts new methods; '{molde.name}' "
                           f"is not one.", doc="oop/reflexao")
    if molde.e_final:
        raise AugmentError(f"Cannot add '{nome}' to '{molde.name}': it is final.",
                           doc="oop/reflexao")
    if molde.e_selado and (molde.arquivo or "") != (interp.filename or ""):
        raise AugmentError(f"Cannot add '{nome}' to '{molde.name}' from this file: "
                           f"it is sealed.", doc="oop/reflexao")
    if nome in molde.methods and not getattr(molde.methods[nome], "is_abstract", False):
        raise AugmentError(
            f"'{molde.name}' already has '{nome}'.",
            dica="reflection adds; replacing is what a child blueprint is for",
            doc="oop/reflexao")
    if not isinstance(acao, i.DFAction):
        raise AugmentError(f"Reflexo.definir_metodo needs an action, and got "
                           f"{interp._nome_do_tipo(acao)}.", doc="oop/reflexao")
    metodo = i.DFAction(name=nome, params=acao.params, defaults=acao.defaults,
                        body=acao.body, closure=acao.closure, is_async=acao.is_async,
                        param_types=acao.param_types, return_type=acao.return_type,
                        is_generator=acao.is_generator, type_params=acao.type_params,
                        type_bounds=acao.type_bounds)
    metodo.arquivo = acao.arquivo
    metodo.dono = molde
    metodo.owner = molde.name
    molde.methods[nome] = metodo
    molde.abstract_methods.discard(nome)
    molde.visibility[nome] = "public"
    molde.esquecer_caches()
    return metodo


def _criar_blueprint(nome, definicao=None):
    """Um blueprint montado de um vault, pelas regras de uma declaracao.

        R.criar_blueprint("Ponto", {
            "campos": {"x": 0, "y": 0},
            "metodos": {"norma": lambda self => sqrt(self.x ** 2 + self.y ** 2)},
            "maes": [Forma],
            "contratos": [Medivel],
        })

    Um metodo recebe o objeto como PRIMEIRO parametro — um lambda nao tem
    'self' — e o resto dos argumentos em seguida.
    """
    i = _classes()
    from .. import ast_nodes as ast
    interp = _interp()
    definicao = _ler_opcoes(definicao or {}, {"campos": {}, "metodos": {},
                                              "maes": [], "contratos": [],
                                              "estaticos": {}},
                            "Reflexo.criar_blueprint")
    if not isinstance(nome, str) or not nome[:1].isupper() or not nome.isidentifier():
        from ..errors import TypeError_
        raise TypeError_(f"A blueprint name is a capitalized identifier; "
                         f"'{nome}' is not.", doc="oop/reflexao")
    escopo = interp.global_env.child(f"<criar {nome}>")
    maes, contratos = [], []
    for k, mae in enumerate(definicao["maes"]):
        apelido = f"__mae_{k}"
        escopo.set_local(apelido, mae)
        maes.append(apelido)
    for k, contrato in enumerate(definicao["contratos"]):
        apelido = f"__contrato_{k}"
        escopo.set_local(apelido, contrato)
        contratos.append(apelido)
    campos = [(campo, None, ast.ValorPronto(value=valor), "public")
              for campo, valor in definicao["campos"].items()]
    corpo = [ast.StaticDeclaration(name=k, value=ast.ValorPronto(value=v))
             for k, v in definicao["estaticos"].items()]
    decl = ast.BlueprintDeclaration(name=nome, parents=maes, traits=contratos,
                                    body=corpo, fields_decl=campos)
    molde = interp.exec_BlueprintDeclaration(decl, escopo)
    for nome_metodo, acao in definicao["metodos"].items():
        _definir_metodo_funcional(molde, nome_metodo, acao)
    if not molde.is_abstract:
        pendentes = molde.pendencias_abstratas()
        if pendentes:
            from ..errors import TraitContractError
            raise TraitContractError(
                f"Blueprint '{nome}' does not implement: "
                f"{', '.join(sorted(pendentes))}.", doc="oop/reflexao")
    return molde


def _definir_metodo_funcional(molde, nome, acao):
    """Um lambda '(self, …) => …' vira metodo: o objeto entra como 1o argumento."""
    i = _classes()
    from .. import ast_nodes as ast
    if not isinstance(acao, i.DFAction):
        raise TypeError(f"the method '{nome}' needs an action or a lambda")
    params = list(acao.params[1:])
    chamada = ast.FunctionCall(
        callee=ast.ValorPronto(value=acao),
        args=[ast.Identifier(name="self")] + [ast.Identifier(name=p) for p in params],
        kwargs={})
    corpo = [ast.YieldStatement(value=chamada)]
    metodo = i.DFAction(name=nome, params=params, defaults={}, body=corpo,
                        closure=molde.env)
    metodo.dono = molde
    metodo.owner = molde.name
    molde.methods[nome] = metodo
    molde.abstract_methods.discard(nome)
    molde.visibility.setdefault(nome, "public")
    molde.esquecer_caches()
    return metodo


# ── inspecao e diagrama ──────────────────────────────────────

def _inspecionar(obj):
    """Tudo o que um depurador mostraria, respeitando a visibilidade."""
    i = _classes()
    molde = _exigir_molde(obj, "inspecionar")
    saida = {
        "tipo": molde.name,
        "especie": _especie(obj),
        "modificadores": _modificadores_de_blueprint(molde)
        if isinstance(molde, i.DFBlueprint) else [],
        "mro": [bp.name for bp in _mro(molde)] if isinstance(molde, i.DFBlueprint) else [molde.name],
        "contratos": _contratos(molde) if isinstance(molde, i.DFBlueprint) else [],
        "metaclasse": getattr(_meta(molde), "name", None) if isinstance(molde, i.DFBlueprint) else None,
    }
    if isinstance(obj, i.DFInstance):
        valores = {}
        for campo in _campos(obj):
            nome = campo["nome"]
            if campo["visibilidade"] == "public" and nome in obj.fields:
                valores[nome] = obj.fields[nome]
            elif nome in obj.fields:
                valores[nome] = f"<{campo['visibilidade']}>"
        saida["campos"] = valores
        estado = obj._estado
        saida["congelado"] = bool(estado and estado.congelado)
        saida["identidade"] = id(obj)
    else:
        saida["campos"] = [c["nome"] for c in _campos(molde)] \
            if isinstance(molde, (i.DFBlueprint, i.DFRecord)) else []
    saida["metodos"] = [m["nome"] for m in _metodos(molde)] \
        if isinstance(molde, i.DFBlueprint) else []
    return saida


_SIMBOLO_UML = {"public": "+", "private": "-", "protected": "#", "internal": "~"}


def _diagrama(moldes, opcoes=None):
    """O diagrama de classes em Mermaid: heranca, contratos e composicao.

    A composicao sai do TIPO declarado dos campos: 'itens: Item' liga
    Pedido a Item. Um campo sem tipo nao desenha seta — adivinhar pelo
    valor desenharia a relacao de um objeto, e nao a do tipo.
    """
    i = _classes()
    opcoes = _ler_opcoes(opcoes or {}, {"membros": True, "titulo": ""},
                         "Reflexo.diagrama")
    if isinstance(moldes, i.DFBlueprint):
        moldes = [moldes] + _descendentes(moldes)
    moldes = [m for m in (_molde(x) for x in moldes) if m is not None]
    nomes = {m.name for m in moldes}
    linhas = ["classDiagram"]
    if opcoes["titulo"]:
        linhas.insert(0, f"---\ntitle: {opcoes['titulo']}\n---")
    for m in moldes:
        if not isinstance(m, i.DFBlueprint):
            linhas.append(f"    class {m.name}")
            continue
        estereotipo = ("interface" if m.e_contrato else "abstract" if m.is_abstract
                       else "metaclass" if m.e_meta else None)
        if not opcoes["membros"]:
            linhas.append(f"    class {m.name}")
        else:
            linhas.append(f"    class {m.name} {{")
            if estereotipo:
                linhas.append(f"        <<{estereotipo}>>")
            for campo in _campos(m):
                simbolo = _SIMBOLO_UML.get(campo["visibilidade"], "+")
                tipo = f"{campo['tipo']} " if campo["tipo"] else ""
                linhas.append(f"        {simbolo}{tipo}{campo['nome']}")
            for metodo in _metodos(m):
                if metodo["dono"] not in (m.name, None) and not m.e_contrato:
                    continue
                simbolo = _SIMBOLO_UML.get(metodo["visibilidade"], "+")
                sufixo = "*" if "abstract" in metodo["modificadores"] else \
                    "$" if "static" in metodo["modificadores"] else ""
                retorno = f" {metodo['retorno']}" if metodo["retorno"] else ""
                linhas.append(f"        {simbolo}{metodo['nome']}"
                              f"({', '.join(metodo['parametros'])}){sufixo}{retorno}")
            linhas.append("    }")
        for mae in m.parents:
            if mae.name in nomes:
                linhas.append(f"    {mae.name} <|-- {m.name}")
        for contrato in m.traits:
            if contrato in nomes:
                linhas.append(f"    {contrato} <|.. {m.name}")
        for campo in _campos(m):
            tipo = campo["tipo"] or ""
            if tipo in nomes and tipo != m.name:
                linhas.append(f"    {m.name} *-- {tipo} : {campo['nome']}")
    return "\n".join(linhas) + "\n"


def _hierarquia(alvo):
    """A arvore de descendentes, como texto indentado."""
    molde = _exigir_molde(alvo, "hierarquia")
    linhas = []

    def andar(m, nivel):
        marcas = _modificadores_de_blueprint(m)
        sufixo = f"  [{', '.join(marcas)}]" if marcas else ""
        linhas.append("  " * nivel + m.name + sufixo)
        for filha in _herdeiros(m):
            andar(filha, nivel + 1)

    andar(molde, 0)
    return "\n".join(linhas)


def _sugerir(alvo, nome):
    """O membro de nome parecido — o 'did you mean' como dado."""
    perto = difflib.get_close_matches(nome, _membros(alvo), n=3, cutoff=0.6)
    return perto


class ArcaneReflexo:
    """Reflexao sobre blueprints, contratos, records e instancias."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Reflexo",
            # tipos
            "tipo": _tipo,
            "nome": _nome,
            "especie": _especie,
            "molde": _molde,
            # membros
            "metodos": _metodos,
            "campos": _campos,
            "propriedades": _propriedades,
            "operadores": _operadores,
            "estaticos": _estaticos,
            "membros": _membros,
            "modificadores": _modificadores,
            "anotacoes": _anotacoes,
            "documentacao": _documentacao,
            "sugerir": _sugerir,
            # heranca
            "maes": _maes,
            "mro": _mro,
            "herdeiros": _herdeiros,
            "descendentes": _descendentes,
            "traits": _traits,
            "contratos": _contratos,
            "descende": _descende,
            "e_instancia": _e_instancia,
            "meta": _meta,
            "meta_instancia": _meta_instancia,
            # registro
            "blueprints": _blueprints,
            "procurar": _procurar,
            # dinamico
            "instanciar": _instanciar,
            "tem": _tem,
            "ler": _ler,
            "escrever": _escrever,
            "invocar": _invocar,
            "cumpre": _cumpre,
            "faltando": _faltando,
            "definir_metodo": _definir_metodo,
            "criar_blueprint": _criar_blueprint,
            # inspecao
            "inspecionar": _inspecionar,
            "diagrama": _diagrama,
            "hierarquia": _hierarquia,
        }
