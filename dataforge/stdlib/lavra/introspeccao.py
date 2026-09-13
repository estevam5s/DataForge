# -*- coding: utf-8 -*-
"""O esquema se descreve — e é ele mesmo quem responde.

Por que ela existe
------------------
Sem introspecção, um cliente precisa de documentação ao lado para saber
o que pedir, e essa documentação envelhece em silêncio. Com ela, o
editor completa o campo, o cliente confere a consulta antes de mandar,
e a página de documentação é GERADA do que está no ar.

O ponto é que a resposta vem do MESMO objeto que executa. Não há um
segundo lugar descrevendo o esquema para divergir do primeiro — é a
mesma regra que este projeto aplica à tabela de módulos e à gramática
do editor.

Ela pode ser desligada
----------------------
`Lavra.introspeccao(esq, no)` tira as buscas `__esquema` e `__tipo`.
Em produção, um esquema exposto é um mapa do que existe para quem for
procurar — e quem precisa dele é o time, que pode lê-lo do repositório.
"""

from .esquema import Campo, Tipo, ler_tipo


def _tipo_como_vault(esquema, nome_ou_ref, profundo=True):
    ref = ler_tipo(nome_ou_ref) if isinstance(nome_ou_ref, str) else nome_ou_ref
    if ref.lista:
        return {"especie": "lista", "obrigatorio": ref.obrigatorio,
                "de": _tipo_como_vault(esquema, ref.de, profundo)}
    tipo = esquema.obter(ref.nome)
    saida = {"nome": ref.nome, "obrigatorio": ref.obrigatorio,
             "especie": tipo.especie if tipo else "desconhecido"}
    if tipo is not None and profundo:
        saida["descricao"] = tipo.descricao
    return saida


def descrever_campo(esquema, campo):
    return {
        "nome": campo.nome,
        "tipo": str(ler_tipo(campo.tipo)),
        "forma": _tipo_como_vault(esquema, campo.tipo),
        "descricao": campo.descricao,
        "obsoleto": campo.obsoleto,
        "complexidade": campo.complexidade,
        "argumentos": [
            {"nome": nome, "tipo": str(ler_tipo(_texto(decl))),
             "padrao": _padrao(decl)}
            for nome, decl in campo.argumentos.items()
        ],
    }


def _texto(decl):
    return decl.get("tipo", "String") if isinstance(decl, dict) else decl


def _padrao(decl):
    from .esquema import padrao_do_argumento, SEM_PADRAO
    valor = padrao_do_argumento(decl)
    return None if valor is SEM_PADRAO else valor


def descrever_tipo(esquema, tipo):
    if tipo is None:
        return None
    saida = {
        "nome": tipo.nome,
        "especie": tipo.especie,
        "descricao": tipo.descricao,
        "campos": [descrever_campo(esquema, c) for c in tipo.campos.values()],
    }
    if tipo.contratos:
        saida["contratos"] = list(tipo.contratos)
    if tipo.membros:
        saida["membros"] = list(tipo.membros)
    if tipo.valores:
        saida["valores"] = list(tipo.valores)
    if tipo.especie == "contrato":
        saida["cumprem"] = sorted(t.nome for t in esquema.tipos.values()
                                  if tipo.nome in t.contratos)
    return saida


def descrever(esquema):
    """O esquema inteiro, como dado."""
    return {
        "nome": esquema.nome,
        "busca": descrever_tipo(esquema, esquema.busca),
        "mudanca": descrever_tipo(esquema, esquema.mudanca),
        "assinatura": descrever_tipo(esquema, esquema.assinatura),
        "tipos": [descrever_tipo(esquema, t)
                  for t in esquema.tipos.values()],
        "diretivas": sorted(["incluir", "pular", *esquema.diretivas]),
        "limites": dict(esquema.limites),
    }


def texto(esquema):
    """O esquema como TEXTO, na notação do Lavra.

    Serve para versionar: um esquema em arquivo entra no diff, e uma
    mudança que quebra o cliente aparece na revisão em vez de na
    produção.
    """
    linhas = [f"# esquema {esquema.nome}", ""]

    def campo_txt(c):
        args = ""
        if c.argumentos:
            partes = []
            for nome, decl in c.argumentos.items():
                padrao = _padrao(decl)
                texto_arg = f"{nome}: {ler_tipo(_texto(decl))}"
                if padrao is not None:
                    texto_arg += f" := {padrao!r}"
                partes.append(texto_arg)
            args = "(" + ", ".join(partes) + ")"
        obs = "   # obsoleto: " + c.obsoleto if c.obsoleto else ""
        return f"    {c.nome}{args}: {ler_tipo(c.tipo)}{obs}"

    for rotulo, tipo in (("busca", esquema.busca), ("mudanca", esquema.mudanca),
                         ("assinatura", esquema.assinatura)):
        if not tipo.campos:
            continue
        linhas.append(f"{rotulo}:")
        linhas.extend(campo_txt(c) for c in tipo.campos.values())
        linhas.append("")

    for tipo in esquema.tipos.values():
        if tipo.especie == "escalar" and tipo.serializar is None:
            continue                      # embutido: não precisa declarar
        if tipo.especie == "escalar":
            linhas.append(f"escalar {tipo.nome}")
            linhas.append("")
            continue
        if tipo.especie == "enum":
            linhas.append(f"enum {tipo.nome}:")
            linhas.extend(f"    {n}" for n in tipo.valores)
            linhas.append("")
            continue
        if tipo.especie == "uniao":
            linhas.append(f"uniao {tipo.nome}: " + " | ".join(tipo.membros))
            linhas.append("")
            continue
        palavra = {"objeto": "tipo", "entrada": "entrada",
                   "contrato": "contrato"}[tipo.especie]
        cumpre = (" cumpre " + ", ".join(tipo.contratos)) if tipo.contratos else ""
        linhas.append(f"{palavra} {tipo.nome}{cumpre}:")
        linhas.extend(campo_txt(c) for c in tipo.campos.values())
        linhas.append("")

    return "\n".join(linhas).rstrip() + "\n"


def instalar(esquema):
    """Acrescenta `__esquema` e `__tipo` às buscas."""
    esquema.busca.campos["__esquema"] = Campo(
        "__esquema", "Esquema!", {},
        resolver=lambda _r, _a, _c: descrever(esquema),
        descricao="O esquema inteiro, como dado.")
    esquema.busca.campos["__tipo"] = Campo(
        "__tipo", "TipoDescrito", {"nome": "String!"},
        resolver=lambda _r, a, _c: descrever_tipo(esquema,
                                                  esquema.obter(a["nome"])),
        descricao="Um tipo pelo nome.")
    _registrar_tipos_da_introspeccao(esquema)


def remover(esquema):
    for nome in ("__esquema", "__tipo"):
        esquema.busca.campos.pop(nome, None)


def _registrar_tipos_da_introspeccao(esquema):
    """Os tipos que descrevem tipos.

    Eles são `Vault` de propósito: descrever a descrição exigiria um
    tipo por campo da introspecção, e o ganho seria nenhum — quem
    consome isto é ferramenta, e ferramenta lê dado.
    """
    if "Esquema" not in esquema.tipos:
        t = Tipo("Esquema", "escalar", "A descrição completa do esquema.")
        t.serializar = lambda v: v
        esquema.tipos["Esquema"] = t
    if "TipoDescrito" not in esquema.tipos:
        t = Tipo("TipoDescrito", "escalar", "A descrição de um tipo.")
        t.serializar = lambda v: v
        esquema.tipos["TipoDescrito"] = t
