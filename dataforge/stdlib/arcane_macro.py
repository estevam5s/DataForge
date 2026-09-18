# -*- coding: utf-8 -*-
"""Arcane.Macro — a árvore como dado: ler, reescrever e gerar código.

O que faltava
-------------
Um decorador troca o **valor**: ele recebe a ação pronta e devolve outra
coisa. O que ele não alcança é o **corpo** — e metade da metaprogramação
que vale a pena é justamente sobre o corpo: instrumentar cada instrução,
derivar um método a partir dos campos, gerar uma ação a partir de um
esquema.

    arvore := M.arvore(somar)            # o corpo, como dado
    nova := M.reescrever(somar, trocar)  # o corpo, reescrito
    gerada := M.acao("dobro", ["x"], M.citar("x * 2"))

Cinco decisões
--------------
1. **A árvore é um vault, e não um objeto opaco.** Um nó vira
   `{"tipo": …, "linha": …, …}` — assim ele percorre com `cycle`, casa
   com `match`, serializa em JSON e atravessa processo, sem que nada
   disso precise conhecer a classe do nó. É o mesmo raciocínio do
   `Quadro` e da ponte para o Python.

2. **A volta é conferida.** `M.acao(…)` reconstrói nós de verdade a
   partir do vault, e um campo inventado é recusado ali, com o nome do
   nó — e não num erro estranho de execução, três passos depois.

3. **A macro roda na CARGA**, quando o decorador é aplicado, e não a
   cada chamada. Reescrever o corpo a cada chamada seria pagar a
   metaprogramação em tempo de execução para sempre.

4. **Higiene é explícita.** `nome_fresco` e `renomear` existem para quem
   gera código não capturar um nome de quem chamou. Fazer isso
   automaticamente exigiria saber o que é "de dentro", e essa decisão é
   de quem escreve a macro.

5. **`texto` é aproximado, e o nome não esconde isso.** A fonte original
   não é guardada; o texto é reconstruído da árvore para ler, comparar e
   depurar — não para ser byte a byte igual ao que foi escrito.
"""

from .. import ast_nodes as ast
from ..errors import RuntimeError_

#: Um contador por processo, para 'nome_fresco'.
_FRESCOS = {"n": 0}

#: Os campos que todo nó carrega, e que não descrevem a estrutura.
_POSICAO = ("line", "column")


def _interp():
    from ..interpreter import DFAction
    return DFAction._interpreter


# ═════════════════════════════════════════════════════════════
#  A árvore, como dado
# ═════════════════════════════════════════════════════════════

def _para_dado(no):
    """Um nó da árvore vira um vault; uma lista, um cluster."""
    if isinstance(no, list):
        return [_para_dado(i) for i in no]
    if isinstance(no, tuple):
        return [_para_dado(i) for i in no]
    if isinstance(no, dict):
        return {str(k): _para_dado(v) for k, v in no.items()}
    if not isinstance(no, ast.ASTNode):
        return no
    saida = {"tipo": type(no).__name__,
             "linha": getattr(no, "line", 0),
             "coluna": getattr(no, "column", 0)}
    for campo, valor in vars(no).items():
        if campo in _POSICAO:
            continue
        saida[_TRADUZ.get(campo, campo)] = _para_dado(valor)
    return saida


#: Os campos com nome em português — o resto passa como está. Traduzir
#: TUDO criaria um segundo vocabulário para a mesma árvore; traduzir o
#: que aparece em toda macro é o que faz o dado se ler.
_TRADUZ = {
    "name": "nome", "value": "valor", "body": "corpo", "params": "parametros",
    "op": "op", "left": "esquerda", "right": "direita", "elements": "itens",
    "condition": "condicao", "args": "argumentos", "target": "alvo",
    "operand": "operando", "method": "metodo", "object": "objeto",
    "callee": "chamado", "expressions": "expressoes", "pairs": "pares",
    "defaults": "padroes", "index": "indice", "message": "mensagem",
}
_DESTRADUZ = {v: k for k, v in _TRADUZ.items()}


def _para_no(dado, onde="a árvore"):
    """O caminho de volta: vault -> nó. Um campo inventado é recusado."""
    if isinstance(dado, list):
        return [_para_no(i, onde) for i in dado]
    if not isinstance(dado, dict) or "tipo" not in dado:
        return dado
    nome = str(dado["tipo"])
    classe = getattr(ast, nome, None)
    if classe is None or not (isinstance(classe, type)
                              and issubclass(classe, ast.ASTNode)):
        raise RuntimeError_(
            f"'{nome}' não é um nó da árvore.", 0, 0,
            nota=f"em {onde}",
            dica="use M.citar(texto) para construir, ou copie o 'tipo' de um "
                 "nó que M.arvore devolveu",
            doc="metaprogramacao/macros")
    campos = {c: v for c, v in vars(classe()).items()}
    argumentos = {}
    for chave, valor in dado.items():
        if chave in ("tipo", "linha", "coluna"):
            continue
        campo = _DESTRADUZ.get(chave, chave)
        if campo not in campos:
            conhecidos = ", ".join(sorted(_TRADUZ.get(c, c) for c in campos))
            raise RuntimeError_(
                f"'{nome}' não tem o campo '{chave}'.", 0, 0,
                nota=f"campos de {nome}: {conhecidos}",
                dica="confira o nome do campo contra o que M.arvore devolve",
                doc="metaprogramacao/macros")
        argumentos[campo] = _para_no(valor, onde)
    no = classe(**argumentos)
    no.line = int(dado.get("linha", 0) or 0)
    no.column = int(dado.get("coluna", 0) or 0)
    return no


def _acao_de(alvo, o_que):
    from ..interpreter import DFAction
    if not isinstance(alvo, DFAction):
        interp = _interp()
        tipo = interp._type_of(alvo) if interp else type(alvo).__name__
        raise RuntimeError_(
            f"'{o_que}' precisa de uma ação, e recebeu {tipo}.", 0, 0,
            doc="metaprogramacao/macros")
    return alvo


def arvore(alvo):
    """A árvore de uma ação — ou de um blueprint — como dado."""
    from ..interpreter import DFAction, DFBlueprint
    if isinstance(alvo, DFAction):
        return {
            "tipo": "ActionDeclaration",
            "nome": alvo.name,
            "parametros": list(alvo.params or []),
            "corpo": _para_dado(list(alvo.body or [])),
            "linha": getattr(alvo, "line", 0),
            "coluna": 0,
        }
    if isinstance(alvo, DFBlueprint):
        return {
            "tipo": "BlueprintDeclaration",
            "nome": alvo.name,
            "metodos": sorted(alvo.methods),
            "campos": [c[0] for c in (alvo.fields_decl or [])],
            "linha": 0, "coluna": 0,
        }
    if isinstance(alvo, ast.ASTNode):
        return _para_dado(alvo)
    return _para_dado(alvo)


def citar(texto):
    """Texto vira árvore. É o 'quote' desta linguagem.

    Uma expressão devolve o nó dela; várias instruções devolvem um
    `Program` com o corpo dentro.
    """
    from ..lexer import tokenize
    from ..parser import parse
    fonte = str(texto)
    if not fonte.endswith("\n"):
        fonte += "\n"
    programa = parse(tokenize(fonte, "<citar>"), "<citar>")
    corpo = list(programa.body)
    if len(corpo) == 1:
        unico = corpo[0]
        # 'x * 2' chega como instrução de expressão: o que interessa é a
        # expressão, senão toda citação viria embrulhada.
        return _para_dado(unico)
    return {"tipo": "Program", "corpo": _para_dado(corpo), "linha": 0, "coluna": 0}


def texto(dado):
    """A árvore de volta para texto — aproximado, e para ler."""
    return _texto_de(_para_no(dado) if isinstance(dado, dict) else dado)


def _texto_de(no, nivel=0):
    if isinstance(no, list):
        return "\n".join(_texto_de(i, nivel) for i in no)
    if not isinstance(no, ast.ASTNode):
        return "void" if no is None else (
            f'"{no}"' if isinstance(no, str) else str(no))
    nome = type(no).__name__
    recuo = "    " * nivel
    if nome == "Identifier":
        return no.name
    if nome in ("IntegerLiteral", "FloatLiteral"):
        return str(no.value)
    if nome == "StringLiteral":
        return f'"{no.value}"'
    if nome == "BooleanLiteral":
        return "yes" if no.value else "no"
    if nome == "VoidLiteral":
        return "void"
    if nome in ("BinaryOp", "ComparisonOp", "LogicalOp"):
        return f"{_texto_de(no.left)} {no.op} {_texto_de(no.right)}"
    if nome == "UnaryOp":
        return f"{no.op}{_texto_de(no.operand)}"
    if nome == "NotOp":
        return f"not {_texto_de(no.operand)}"
    if nome == "ListLiteral":
        return "[" + ", ".join(_texto_de(i) for i in no.elements) + "]"
    if nome == "TupleLiteral":
        dentro = ", ".join(_texto_de(i) for i in no.elements)
        return f"({dentro},)" if len(no.elements) == 1 else f"({dentro})"
    if nome == "DictLiteral":
        return "{" + ", ".join(f"{_texto_de(k)}: {_texto_de(v)}"
                               for k, v in no.pairs) + "}"
    if nome == "Assignment":
        tipo = f": {no.declared_type}" if getattr(no, "declared_type", "") else ""
        op = f" {no.compound_op}= " if getattr(no, "compound_op", "") else " := "
        return f"{recuo}{_texto_de(no.target)}{tipo}{op}{_texto_de(no.value)}"
    if nome == "YieldStatement":
        return f"{recuo}yield {_texto_de(no.value)}"
    if nome == "OutStatement":
        return f"{recuo}out " + ", ".join(_texto_de(e) for e in no.expressions)
    if nome == "FunctionCall":
        return (f"{_texto_de(no.callee)}("
                + ", ".join(_texto_de(a) for a in no.args) + ")")
    if nome == "MethodCall":
        return (f"{_texto_de(no.object)}.{no.method}("
                + ", ".join(_texto_de(a) for a in no.args) + ")")
    if nome == "MemberAccess":
        return f"{_texto_de(no.object)}.{no.member}"
    if nome == "IndexAccess":
        return f"{_texto_de(no.object)}[{_texto_de(no.index)}]"
    if nome == "ActionDeclaration":
        cabeca = f"{recuo}action {no.name}({', '.join(no.params or [])}):"
        return cabeca + "\n" + _texto_de(list(no.body or []), nivel + 1)
    if nome == "GivenBlock":
        cabeca = f"{recuo}given {_texto_de(no.condition)}:"
        return cabeca + "\n" + _texto_de(list(no.body or []), nivel + 1)
    if nome == "Program":
        return _texto_de(list(no.body or []), nivel)
    return f"{recuo}<{nome}>"


# ═════════════════════════════════════════════════════════════
#  Percorrer e reescrever
# ═════════════════════════════════════════════════════════════

def percorrer(dado, visitante):
    """Chama `visitante(no)` em cada nó, de fora para dentro."""
    if isinstance(dado, list):
        for item in dado:
            percorrer(item, visitante)
        return dado
    if not isinstance(dado, dict):
        return dado
    if "tipo" in dado:
        visitante(dado)
    for chave, valor in dado.items():
        if chave in ("tipo", "linha", "coluna"):
            continue
        percorrer(valor, visitante)
    return dado


def transformar(dado, acao):
    """Devolve uma árvore NOVA, com `acao(no)` aplicada a cada nó.

    A ação recebe o nó e devolve o que ele vira: ele mesmo, outro nó, ou
    `void` para deixá-lo como está. A árvore original não é tocada — uma
    macro que mutasse o que recebeu mudaria a ação de quem chamou.
    """
    if isinstance(dado, list):
        return [transformar(i, acao) for i in dado]
    if not isinstance(dado, dict):
        return dado
    novo = {}
    for chave, valor in dado.items():
        novo[chave] = (valor if chave in ("tipo", "linha", "coluna")
                       else transformar(valor, acao))
    if "tipo" not in novo:
        return novo
    trocado = acao(novo)
    return novo if trocado is None else trocado


def substituir(dado, de, para):
    """Troca todo nó cujo `tipo` é `de` pelo nó `para`."""
    return transformar(dado, lambda no: para if no.get("tipo") == de else None)


def renomear(dado, de, para):
    """Troca o nome de todo identificador chamado `de`."""
    def trocar(no):
        if no.get("tipo") == "Identifier" and no.get("nome") == de:
            copia = dict(no)
            copia["nome"] = para
            return copia
        return None
    return transformar(dado, trocar)


def nome_fresco(base="temp"):
    """Um nome que não existe no código de quem chamou — a higiene."""
    _FRESCOS["n"] += 1
    return f"__{base}_{_FRESCOS['n']}"


# ═════════════════════════════════════════════════════════════
#  Gerar
# ═════════════════════════════════════════════════════════════

def acao(nome, parametros, corpo, fechamento=None):
    """Monta uma ação a partir de uma árvore.

    `corpo` pode ser uma expressão (vira `yield expressao`) ou uma lista
    de instruções.
    """
    from ..interpreter import DFAction
    interp = _interp()
    if interp is None:
        raise RuntimeError_("Macro.acao precisa do interpretador.", 0, 0)
    no = _para_no(corpo, f"o corpo de '{nome}'")
    if isinstance(no, list):
        instrucoes = no
    elif isinstance(no, ast.Program):
        instrucoes = list(no.body)
    elif isinstance(no, ast.ASTNode) and _e_instrucao(no):
        instrucoes = [no]
    else:
        instrucoes = [ast.YieldStatement(value=no, line=getattr(no, "line", 0))]
    return DFAction(
        name=str(nome), params=[str(p) for p in (parametros or [])],
        defaults={}, body=instrucoes,
        closure=fechamento or interp.global_env)


def _e_instrucao(no):
    """Tem 'exec_<Nó>' no interpretador? Então é instrução.

    A mesma definição que a cobertura usa: uma lista à parte
    envelheceria, e o sintoma seria uma macro que devolve `void`.
    """
    interp = _interp()
    return interp is not None and hasattr(interp, f"exec_{type(no).__name__}")


def reescrever(alvo, transformador):
    """Uma ação nova, com o corpo passado pelo transformador."""
    acao_alvo = _acao_de(alvo, "reescrever")
    corpo = transformar(_para_dado(list(acao_alvo.body or [])), transformador)
    return acao(acao_alvo.name, list(acao_alvo.params or []), corpo,
                acao_alvo.closure)


def compilar(texto_fonte, nome="gerada", parametros=None):
    """Texto vira ação, num passo: `citar` + `acao`."""
    return acao(nome, parametros or [], citar(texto_fonte))


# ═════════════════════════════════════════════════════════════
#  Macro de atributo: derivar
# ═════════════════════════════════════════════════════════════

def derivar(*quais):
    """`mark @M.derivar("texto", "igualdade")` sobre um blueprint.

    É a macro derivada: em vez de escrever `__str__` e `__eq__` à mão em
    cada blueprint, os campos que já existem geram os dois.
    """
    pedidos = [str(q) for q in quais] or ["texto", "igualdade"]

    def aplicar(alvo):
        from ..interpreter import DFAction, DFBlueprint
        if not isinstance(alvo, DFBlueprint):
            raise RuntimeError_(
                "'derivar' vale sobre um blueprint.", 0, 0,
                dica="mark @M.derivar(…) logo acima de 'blueprint Nome:'",
                doc="metaprogramacao/macros")
        campos = [c[0] for c in (alvo.fields_decl or [])]
        for pedido in pedidos:
            gerador = _DERIVAVEIS.get(pedido)
            if gerador is None:
                raise RuntimeError_(
                    f"não sei derivar '{pedido}'.", 0, 0,
                    nota=f"sei derivar: {', '.join(sorted(_DERIVAVEIS))}",
                    doc="metaprogramacao/macros")
            nome, funcao = gerador(alvo, campos)
            metodo = DFAction(name=nome, params=funcao["parametros"],
                              defaults={}, body=funcao["corpo"],
                              closure=alvo.env)
            metodo.owner = alvo.name
            alvo.methods[nome] = metodo
        esquecer = getattr(alvo, "esquecer_caches", None)
        if callable(esquecer):
            esquecer()
        return alvo

    return aplicar


def _derivar_texto(blueprint, campos):
    dentro = ", ".join(f"{c}={{self.{c}}}" for c in campos)
    corpo = citar(f'yield $"{blueprint.name}({dentro})"')
    return "__str__", {"parametros": [], "corpo": [_para_no(corpo)]}


def _derivar_igualdade(blueprint, campos):
    if campos:
        condicao = " and ".join(f"self.{c} is outro.{c}" for c in campos)
    else:
        condicao = "yes"
    corpo = citar(f"yield {condicao}")
    return "__eq__", {"parametros": ["outro"], "corpo": [_para_no(corpo)]}


def _derivar_ordem(blueprint, campos):
    primeiro = campos[0] if campos else None
    if primeiro is None:
        corpo = citar("yield no")
    else:
        corpo = citar(f"yield self.{primeiro} smaller outro.{primeiro}")
    return "__lt__", {"parametros": ["outro"], "corpo": [_para_no(corpo)]}


def _derivar_vault(blueprint, campos):
    pares = ", ".join(f'"{c}": self.{c}' for c in campos)
    corpo = citar(f"yield {{{pares}}}")
    return "para_vault", {"parametros": [], "corpo": [_para_no(corpo)]}


_DERIVAVEIS = {
    "texto": _derivar_texto,
    "igualdade": _derivar_igualdade,
    "ordem": _derivar_ordem,
    "vault": _derivar_vault,
}


class ArcaneMacro:
    """O dicionário que `adopt Arcane.Macro` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Macro",

            # ── ler ──
            "arvore": arvore,
            "citar": citar,
            "texto": texto,

            # ── percorrer e reescrever ──
            "percorrer": percorrer,
            "transformar": transformar,
            "substituir": substituir,
            "renomear": renomear,
            "nome_fresco": nome_fresco,

            # ── gerar ──
            "acao": acao,
            "compilar": compilar,
            "reescrever": reescrever,

            # ── macro de atributo ──
            "derivar": derivar,
            "derivaveis": lambda: sorted(_DERIVAVEIS),
        }
