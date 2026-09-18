"""HIR — a árvore depois do açúcar.

A árvore que o parser entrega tem cento e quarenta formas de nó. Boa
parte delas é **conveniência de escrita**: `orif` é um `given` deitado,
`soma += 1` é `soma := soma + 1`, `x not in xs` é `not (x in xs)`. Cada
uma dessas formas é um caso a mais em todo analisador que percorre a
árvore — e é assim que uma análise fica certa num caminho e errada no
outro sem ninguém ver.

O HIR é a mesma árvore com menos formas. `normalizar(no)` devolve uma
**cópia** em que cada açúcar desta lista foi aberto:

| Nome | O que abre |
|---|---|
| `orif-aninhado` | a corrente de `orif` vira `given`/`otherwise` aninhado |
| `composta-simples` | `x += 1` vira `x := x + 1` **só quando o alvo é um nome** |
| `pertence-negado` | `x not in xs` vira `not (x in xs)` |
| `perform-para-persist` | `perform … persist c` vira uma volta garantida mais o laço |
| `sinal-de-literal` | `-5`, hoje um `UnaryOp` sobre `5`, vira o literal `-5` |

**A prova de que a normalização está certa não é a forma da árvore: é a
saída.** `tests/test_compilador_interno.py` roda exercícios do
repositório nas duas formas e compara caractere por caractere. Um
desaçucaramento errado não levanta erro — ele muda o resultado, e só a
comparação pega isso.

`NAO_E_ACUCAR` é a outra metade, e ela é mais informativa que a primeira:
oito formas que **parecem** açúcar, não são, e o motivo de cada uma está
escrito ao lado. Uma lista dessas sem o porquê apodrece, e há teste
cobrando o motivo.
"""

import dataclasses

from . import ast_nodes as ast

__all__ = ["normalizar", "texto", "acucares_usados", "resolucao",
           "ACUCARES", "NAO_E_ACUCAR", "Ligacao"]


#: nome do açúcar -> o que ele abre. É esta tabela que o
#: `dataforge ir --fase=hir` mostra, e a que o teste compara.
ACUCARES = {
    "orif-aninhado":
        "a corrente de 'orif' vira 'given'/'otherwise' aninhado",
    "composta-simples":
        "'x += 1' vira 'x := x + 1' quando o alvo e um nome",
    "pertence-negado":
        "'x not in xs' vira 'not (x in xs)'",
    "perform-para-persist":
        "'perform … persist c' vira a primeira volta mais o laco",
    "sinal-de-literal":
        "'-5' vira o literal -5, e nao uma operacao sobre 5",
}

#: O que parece açúcar e não é — com o motivo. Vale mais que a lista de
#: cima: é o que impede alguém de "simplificar" a árvore e mudar a
#: linguagem sem notar.
NAO_E_ACUCAR = {
    "CycleFromTo":
        "'range' materializa a lista: um laco de um milhao de voltas "
        "viraria uma lista de um milhao de itens, e o laco de contador "
        "existe justamente para nao pagar isso",
    "TernaryExpression":
        "o ternario e EXPRESSAO e o 'given' e INSTRUCAO; trocar um pelo "
        "outro exigiria uma variavel temporaria, que muda o escopo",
    "CoalesceOp":
        "'a ?? b' avaliaria 'a' duas vezes na forma com ternario, e o "
        "lado esquerdo de um '??' costuma ser uma chamada",
    "SafeMemberAccess":
        "'x?.y' tem o mesmo problema: o ternario equivalente avalia 'x' "
        "duas vezes, e 'f()?.campo' chamaria 'f' duas vezes",
    "InterpolatedString":
        "'$\"{x:.2f}\"' nao tem forma de expressao — o formato depois "
        "dos dois-pontos nao existe como operador na linguagem",
    "ListComprehension":
        "a compreensao e expressao com escopo proprio; virar laco exigiria "
        "instrucao, e o valor teria de sair por uma variavel",
    "MarkDecorator":
        "'g := f(g)' seria errado: um decorador que devolve 'void' NAO "
        "substitui o alvo, e e isso que deixa '@Rota(\"/x\")' so anotar",
    "PipelineExpression":
        "os estagios sao preguiçosos e os verbos de quadro pedem o "
        "quadro, nao a lista; virar chamada aninhada tiraria os dois",
}


class _Varias(list):
    """Uma instrução que virou várias. Achatada no corpo que a contém."""


# ── a travessia genérica ──────────────────────────────────────

def _copiar(no, trocas):
    """Um nó novo da mesma classe, com os campos já normalizados."""
    campos = {c.name: trocas.get(c.name, getattr(no, c.name))
              for c in dataclasses.fields(no)}
    return no.__class__(**campos)


def _normalizar_valor(valor):
    """Normaliza qualquer coisa que apareça num campo de nó."""
    if isinstance(valor, ast.ASTNode):
        return _normalizar_no(valor)
    if isinstance(valor, list):
        return _corpo(valor)
    if isinstance(valor, tuple):
        return tuple(_normalizar_valor(v) for v in valor)
    if isinstance(valor, dict):
        return {k: _normalizar_valor(v) for k, v in valor.items()}
    return valor


def _corpo(instrucoes):
    """Uma lista de instruções, com o que virou várias já achatado."""
    saida = []
    for item in instrucoes:
        pronto = _normalizar_valor(item)
        if isinstance(pronto, _Varias):
            saida.extend(pronto)
        else:
            saida.append(pronto)
    return saida


def _normalizar_no(no):
    """De baixo para cima: primeiro os filhos, depois a reescrita.

    A ordem importa. Reescrever de cima para baixo faria a reescrita
    receber filhos com açúcar dentro, e cada reescritor teria de
    normalizar os seus — cinco cópias da travessia.
    """
    if isinstance(no, ast.ValorPronto):
        return no                       # um valor já resolvido, sem filhos

    trocas = {}
    for campo in dataclasses.fields(no):
        antes = getattr(no, campo.name)
        depois = _normalizar_valor(antes)
        if depois is not antes:
            trocas[campo.name] = depois
    novo = _copiar(no, trocas)

    for reescrever in _REESCRITORES:
        pronto = reescrever(novo)
        if pronto is not None:
            return pronto
    return novo


def normalizar(no):
    """A árvore sem açúcar. A original não é tocada."""
    return _normalizar_no(no)


# ── os reescritores ───────────────────────────────────────────

def _r_orif(no):
    """`given a: A orif b: B otherwise: C` → `given a: A otherwise: given b: …`"""
    if not isinstance(no, ast.GivenBlock) or not no.orif_blocks:
        return None
    corpo = no.otherwise_body
    for condicao, corpo_orif in reversed(no.orif_blocks):
        linha = getattr(condicao, "line", no.line)
        coluna = getattr(condicao, "column", no.column)
        corpo = [ast.GivenBlock(line=linha, column=coluna,
                                condition=condicao, body=corpo_orif,
                                orif_blocks=[], otherwise_body=corpo)]
    return ast.GivenBlock(line=no.line, column=no.column,
                          condition=no.condition, body=no.body,
                          orif_blocks=[], otherwise_body=corpo)


def _r_composta(no):
    """`x += 1` → `x := x + 1`, **só** quando o alvo é um nome.

    Com índice ou membro o alvo seria avaliado duas vezes, e
    `v[sortear()] += 1` consumiria dois sorteios. É o mesmo motivo por
    que `Assignment.value` guarda só o lado direito.
    """
    if not isinstance(no, ast.Assignment) or not no.compound_op:
        return None
    if not isinstance(no.target, ast.Identifier):
        return None
    leitura = ast.Identifier(line=no.target.line, column=no.target.column,
                             name=no.target.name)
    conta = ast.BinaryOp(line=no.line, column=no.column,
                         left=leitura, op=no.compound_op, right=no.value)
    return ast.Assignment(line=no.line, column=no.column, target=no.target,
                          value=conta, declared_type=no.declared_type,
                          compound_op="")


def _r_pertence(no):
    """`x not in xs` → `not (x in xs)`."""
    if not isinstance(no, ast.MembershipOp) or not no.negated:
        return None
    dentro = ast.MembershipOp(line=no.line, column=no.column,
                              element=no.element, container=no.container,
                              negated=False)
    return ast.NotOp(line=no.line, column=no.column, operand=dentro)


_CONTADOR = [0]


def _nome_fresco(prefixo):
    """Um nome que o lexer não consegue produzir, e por isso não colide."""
    _CONTADOR[0] += 1
    return f"{prefixo}#{_CONTADOR[0]}"


def _r_perform(no):
    """`perform: C persist cond` → `m := yes` + `persist m or cond: m := no; C`.

    A marca garante a primeira volta, e o `or` curto-circuita: na
    primeira passada `cond` não é avaliada — que é exatamente o
    contrato do `perform`. `halt` e `skip` continuam valendo porque o
    corpo continua **dentro** de um laço; duplicar o corpo fora dele
    faria um `halt` da primeira volta escapar do laço inteiro.
    """
    if not isinstance(no, ast.PerformBlock):
        return None
    marca = _nome_fresco("perform")
    pos = {"line": no.line, "column": no.column}

    def nome():
        return ast.Identifier(name=marca, **pos)

    ligar = ast.Assignment(target=nome(),
                           value=ast.BooleanLiteral(value=True, **pos), **pos)
    desligar = ast.Assignment(target=nome(),
                              value=ast.BooleanLiteral(value=False, **pos), **pos)
    laco = ast.PersistBlock(
        condition=ast.LogicalOp(left=nome(), op="or",
                                right=no.condition, **pos),
        body=[desligar] + list(no.body), **pos)
    return _Varias([ligar, laco])


_LITERAL_NUMERICO = (ast.IntegerLiteral, ast.FloatLiteral)


def _r_sinal(no):
    """`-5` → o literal `-5`.

    O parser entrega `UnaryOp('-', 5)`, e é a forma certa de ler: o
    menos é um operador. Mas toda análise que pergunta "isto é um
    literal?" responde **não** para um número negativo, e aí um
    `cycle i from -3 to 3` deixa de ser provável como o positivo é.
    """
    if not isinstance(no, ast.UnaryOp) or no.op not in ("-", "+"):
        return None
    if not isinstance(no.operand, _LITERAL_NUMERICO):
        return None
    valor = no.operand.value
    return no.operand.__class__(line=no.line, column=no.column,
                                value=valor if no.op == "+" else -valor)


_REESCRITORES = (_r_orif, _r_composta, _r_pertence, _r_perform, _r_sinal)


# ── quanto açúcar um arquivo usa ──────────────────────────────

def _percorrer(no):
    """Todo nó da árvore, uma vez."""
    if isinstance(no, ast.ASTNode):
        yield no
        if isinstance(no, ast.ValorPronto):
            return
        for campo in dataclasses.fields(no):
            yield from _percorrer(getattr(no, campo.name))
    elif isinstance(no, (list, tuple)):
        for item in no:
            yield from _percorrer(item)
    elif isinstance(no, dict):
        for item in no.values():
            yield from _percorrer(item)


def acucares_usados(no):
    """`{nome do açúcar: quantas vezes}` — vazio num HIR."""
    contagem = {}

    def somar(nome):
        contagem[nome] = contagem.get(nome, 0) + 1

    for alvo in _percorrer(no):
        if isinstance(alvo, ast.GivenBlock) and alvo.orif_blocks:
            somar("orif-aninhado")
        elif isinstance(alvo, ast.Assignment) and alvo.compound_op \
                and isinstance(alvo.target, ast.Identifier):
            somar("composta-simples")
        elif isinstance(alvo, ast.MembershipOp) and alvo.negated:
            somar("pertence-negado")
        elif isinstance(alvo, ast.PerformBlock):
            somar("perform-para-persist")
        elif isinstance(alvo, ast.UnaryOp) and alvo.op in ("-", "+") \
                and isinstance(alvo.operand, _LITERAL_NUMERICO):
            somar("sinal-de-literal")
    return contagem


# ── resolução de nomes ────────────────────────────────────────

@dataclasses.dataclass
class Ligacao:
    """De onde vem cada nome que um corpo menciona."""
    nome: str
    linha: int = 0
    parametros: tuple = ()
    locais: tuple = ()
    livres: tuple = ()
    embutidos: tuple = ()


def _embutidos():
    from .builtins import get_builtins
    try:
        return set(get_builtins())
    except Exception:                       # pragma: no cover
        return set()


def _nomes_lidos(corpo):
    """Todo nome lido no corpo, sem descer em declaração aninhada."""
    lidos = set()
    for no in _percorrer(corpo):
        if isinstance(no, ast.Identifier):
            lidos.add(no.name)
        elif isinstance(no, ast.FunctionCall) and isinstance(no.callee, ast.Identifier):
            lidos.add(no.callee.name)
    return lidos


def _nomes_escritos(corpo):
    escritos = set()
    for no in _percorrer(corpo):
        if isinstance(no, ast.Assignment) and isinstance(no.target, ast.Identifier):
            escritos.add(no.target.name)
        elif isinstance(no, ast.SteadyDeclaration):
            escritos.add(no.name)
        elif isinstance(no, (ast.CycleIn, ast.CycleFromTo)):
            escritos.add(no.var)
            escritos.update(getattr(no, "vars", []) or [])
        elif isinstance(no, ast.DestructuringAssignment):
            escritos.update(n for n in no.targets if isinstance(n, str))
    return escritos


def resolucao(programa):
    """Uma `Ligacao` por ação declarada, mais uma para o topo.

    É a resposta a "de onde vem este nome": parâmetro, local, livre (vem
    de fora) ou embutido. A classificação é por **nome**, e não por
    ocorrência: um nome que é local em algum ponto do corpo é local no
    corpo — conservador na direção de não chamar de livre o que não é.
    """
    embutidos = _embutidos()
    saida = []

    def visitar(no, prefixo=""):
        if isinstance(no, ast.ActionDeclaration):
            nome = f"{prefixo}{no.name}"
            params = tuple(_nome_de_parametro(p) for p in (no.params or []))
            escritos = _nomes_escritos(no.body) - set(params)
            lidos = _nomes_lidos(no.body)
            livres = lidos - set(params) - escritos - embutidos - {"self", "root"}
            saida.append(Ligacao(
                nome=nome, linha=no.line, parametros=params,
                locais=tuple(sorted(escritos)),
                livres=tuple(sorted(livres)),
                embutidos=tuple(sorted(lidos & embutidos))))
        novo = prefixo
        if isinstance(no, (ast.BlueprintDeclaration, ast.RecordDeclaration,
                           ast.TraitDeclaration)):
            novo = f"{getattr(no, 'name', '?')}."
        if isinstance(no, ast.ASTNode) and not isinstance(no, ast.ValorPronto):
            for campo in dataclasses.fields(no):
                descer(getattr(no, campo.name), novo)

    def descer(valor, prefixo):
        if isinstance(valor, ast.ASTNode):
            visitar(valor, prefixo)
        elif isinstance(valor, (list, tuple)):
            for item in valor:
                descer(item, prefixo)
        elif isinstance(valor, dict):
            for item in valor.values():
                descer(item, prefixo)

    visitar(programa)
    return saida


def _nome_de_parametro(p):
    if isinstance(p, str):
        return p
    for atributo in ("name", "nome"):
        if hasattr(p, atributo):
            return getattr(p, atributo)
    if isinstance(p, (list, tuple)) and p:
        return p[0]
    return str(p)


# ── o desenho ─────────────────────────────────────────────────

def texto(no, largura=2):
    """O HIR escrito, com a contagem de açúcar no cabeçalho."""
    linhas = []
    usados = acucares_usados(no)
    if usados:
        linhas.append("  acucar que sobrou: " +
                      ", ".join(f"{k}×{v}" for k, v in sorted(usados.items())))
    else:
        linhas.append("  acucar que sobrou: nenhum")
    linhas.append("")
    linhas.extend(_desenhar(no, 1, largura))
    return "\n".join(linhas)


_RESUMIR = {
    ast.Identifier: lambda n: n.name,
    ast.IntegerLiteral: lambda n: repr(n.value),
    ast.FloatLiteral: lambda n: repr(n.value),
    ast.StringLiteral: lambda n: repr(n.value),
    ast.BooleanLiteral: lambda n: "yes" if n.value else "no",
    ast.VoidLiteral: lambda n: "void",
    ast.BinaryOp: lambda n: n.op,
    ast.ComparisonOp: lambda n: n.op,
    ast.LogicalOp: lambda n: n.op,
    ast.UnaryOp: lambda n: n.op,
}


def _desenhar(valor, nivel, largura):
    espaco = " " * (nivel * largura)
    if isinstance(valor, ast.ASTNode):
        rotulo = valor.__class__.__name__
        resumo = _RESUMIR.get(valor.__class__)
        cabeca = f"{espaco}{rotulo}"
        if resumo is not None:
            return [f"{cabeca} {resumo(valor)}"]
        linhas = [cabeca]
        if isinstance(valor, ast.ValorPronto):
            return linhas
        for campo in dataclasses.fields(valor):
            if campo.name in ("line", "column"):
                continue
            dentro = getattr(valor, campo.name)
            if dentro in (None, "", [], {}, ()):
                continue
            if isinstance(dentro, (ast.ASTNode, list, tuple, dict)):
                linhas.append(f"{espaco}{' ' * largura}{campo.name}:")
                linhas.extend(_desenhar(dentro, nivel + 2, largura))
            else:
                linhas.append(f"{espaco}{' ' * largura}{campo.name}: {dentro!r}")
        return linhas
    if isinstance(valor, (list, tuple)):
        linhas = []
        for item in valor:
            linhas.extend(_desenhar(item, nivel, largura))
        return linhas
    if isinstance(valor, dict):
        linhas = []
        for chave, item in valor.items():
            linhas.append(f"{espaco}{chave}:")
            linhas.extend(_desenhar(item, nivel + 1, largura))
        return linhas
    return [f"{espaco}{valor!r}"]
