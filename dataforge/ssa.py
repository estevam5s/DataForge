"""SSA — uma definição por nome, e o nó φ onde os caminhos se juntam.

O que o MIR não responde
------------------------
`mir.py` diz por onde o programa passa. O que ele **não** diz é *qual*
atribuição uma leitura vê. Num corpo com três `x := …`, a pergunta "de
onde vem este `x`?" precisa ser reconstruída a cada análise — e cada
análise que a reconstrói é uma chance de reconstruí-la diferente.

SSA responde isso por construção: cada nome é **numerado**, cada versão
tem **exatamente uma** definição, e onde dois caminhos trazem versões
diferentes aparece um nó **φ** que diz de onde cada uma vem.

```
given c:                 bloco 1:  x₁ := 1
    x := 1               bloco 2:  x₂ := 2
otherwise:               bloco 3:  x₃ := φ(1: x₁, 2: x₂)
    x := 2                         out x₃
out x
```

O que ela paga: a propagação condicional
----------------------------------------
`mir.constantes` junta os ramos por **interseção**, e por isso perde o
que só um ramo decide. `constantes_condicionais` não avalia o ramo cuja
condição ela prova falsa — e aí a junção tem um predecessor vivo só, o φ
tem uma fonte só, e o valor **se conclui**:

```
x := 1
given x bigger 5:        // provado falso: este ramo nao roda
    y := "nunca"
otherwise:
    y := "sempre"
out y                    // 'sempre', e a propagacao sobre o MIR nao sabia
```

`tests/test_ssa_e_otimizacao.py` prova que isso é **estritamente** mais
forte, comparando as duas análises no mesmo programa.

Três decisões
-------------
1. **As instruções não são reescritas.** Um SSA de livro transforma o
   código em três endereços (`t1 := a + b`) e renomeia os operandos.
   Aqui as instruções continuam sendo os nós da árvore, e a versão é
   **anexada**: cada instrução leva `le` (nome → versão lida) e
   `escreve` (nome, versão criada). Reescrever a árvore em três endereços
   criaria uma segunda semântica para manter em sincronia — o risco que
   `compilador.py` evita ao delegar aos mesmos auxiliares.

2. **A dominância é calculada por ponto fixo, e não por Lengauer-Tarjan.**
   Os corpos desta linguagem têm dezenas de blocos, não milhares; o
   algoritmo rápido é três vezes mais código para ganhar microssegundos
   num lugar que roda uma vez por corpo.

3. **O que não é alcançável não entra.** Um bloco morto teria φ com
   fonte de lugar nenhum, e a análise passaria a concluir a partir de
   código que não roda — o oposto do que ela existe para fazer.
"""

from dataclasses import dataclass, field

from . import ast_nodes as ast
from . import mir as _mir

__all__ = ["Fi", "InstrucaoSSA", "BlocoSSA", "CorpoSSA", "construir",
           "dominadores", "dominador_imediato", "fronteira_de_dominancia",
           "definicao_de", "constantes_condicionais", "texto"]


@dataclass
class Fi:
    """`x₃ := φ(1: x₁, 2: x₂)` — de onde vem o nome nesta junção."""
    nome: str
    versao: int
    #: {id do bloco de onde vem: versão que vem dali}
    fontes: dict = field(default_factory=dict)


@dataclass
class InstrucaoSSA:
    """Uma instrução do MIR, com as versões anexadas."""
    no: object
    #: {nome: versão lida}
    le: dict = field(default_factory=dict)
    #: (nome, versão criada), ou None
    escreve: object = None

    @property
    def linha(self):
        return getattr(self.no, "line", 0)


@dataclass
class BlocoSSA:
    id: int
    rotulo: str = ""
    fis: list = field(default_factory=list)
    instrucoes: list = field(default_factory=list)
    saidas: list = field(default_factory=list)
    terminador: str = ""


@dataclass
class CorpoSSA:
    nome: str
    blocos: list = field(default_factory=list)
    entrada: int = 0
    parametros: tuple = ()
    #: {(nome, versão): ('fi', id do bloco) | ('instrucao', id, índice)}
    definicoes: dict = field(default_factory=dict)
    #: versões que nascem sem valor provável (variável de laço, nome de erro)
    sem_valor: set = field(default_factory=set)

    def bloco(self, id_):
        for b in self.blocos:
            if b.id == id_:
                return b
        raise KeyError(id_)


# ── dominância ────────────────────────────────────────────────

def _dominancia(corpo):
    """`(vivos, dom, idom, predecessores)` — calculado UMA vez.

    As três perguntas saem do mesmo ponto fixo. Recalculá-lo por
    pergunta é o que fazia a fronteira chamar `dominador_imediato` dentro
    de um laço, e a construção do SSA ficar cúbica no número de blocos.
    """
    vivos = _mir.alcancaveis(corpo)
    antes = _mir._predecessores(corpo, vivos)

    dom = {i: set(vivos) for i in vivos}
    dom[corpo.entrada] = {corpo.entrada}
    mudou = True
    while mudou:
        mudou = False
        for id_ in sorted(vivos):
            if id_ == corpo.entrada:
                continue
            fontes = [dom[p] for p in antes[id_] if p in dom]
            novo_conjunto = (set.intersection(*fontes) if fontes else set())
            novo_conjunto = novo_conjunto | {id_}
            if novo_conjunto != dom[id_]:
                dom[id_] = novo_conjunto
                mudou = True

    idom = {}
    for id_ in vivos:
        candidatos = dom[id_] - {id_}
        idom[id_] = None
        for c in candidatos:
            # o imediato é o candidato que todos os outros dominam
            if all(c == outro or outro in dom[c] for outro in candidatos):
                idom[id_] = c
                break
    return vivos, dom, idom, antes


def dominadores(corpo):
    """`{id: os blocos por que TODO caminho até ele passa}`.

    Alcançar é poder chegar; dominar é não haver como chegar por outro
    lado. É a diferença que decide onde um φ é necessário: num ramo, não;
    na junção, sim.
    """
    return _dominancia(corpo)[1]


def dominador_imediato(corpo):
    """`{id: o dominador mais próximo}` — a árvore de dominância."""
    return _dominancia(corpo)[2]


def fronteira_de_dominancia(corpo):
    """`{id: onde a dominância dele acaba}` — e onde os φ vão.

    O algoritmo é o de Cytron, e a condição dele é fácil de escrever ao
    contrário: sobe-se da PREDECESSORA até o dominador imediato da
    junção, e cada bloco do caminho ganha a junção na fronteira. A
    primeira versão perguntava "b domina atual?" em vez de "atual é o
    dominador imediato de b?" — e o resultado era um φ em todo bloco de
    todo laço, para nomes que nem se juntavam ali.

    Um bloco com **um** predecessor não é junção de nada, e por isso não
    entra na fronteira de ninguém.
    """
    vivos, _dom, idom, antes = _dominancia(corpo)
    fronteira = {i: set() for i in vivos}
    for b in sorted(vivos):
        if len(antes[b]) < 2:
            continue
        for p in antes[b]:
            atual = p
            visto = set()
            while atual is not None and atual != idom[b] and atual not in visto:
                visto.add(atual)
                fronteira[atual].add(b)
                atual = idom.get(atual)
    return fronteira


# ── a construção ──────────────────────────────────────────────

def construir(corpo):
    """O `Corpo` do MIR, com os nomes numerados e os φ postos."""
    vivos, dom, idom, _antes = _dominancia(corpo)
    fronteira = fronteira_de_dominancia(corpo)
    por_id = {b.id: b for b in corpo.blocos}

    # 1. onde cada nome é escrito
    escreve_em = {}
    for b in corpo.blocos:
        if b.id not in vivos:
            continue
        for nome in b.escreve:
            escreve_em.setdefault(nome, set()).add(b.id)
        for instrucao in b.instrucoes:
            for nome in _mir.escritos(instrucao):
                escreve_em.setdefault(nome, set()).add(b.id)

    # 2. os φ, nas fronteiras — o algoritmo clássico de propagação
    fis_em = {i: {} for i in vivos}
    for nome, blocos in escreve_em.items():
        pendentes = list(blocos)
        vistos = set(blocos)
        while pendentes:
            bloco = pendentes.pop()
            for alvo in fronteira.get(bloco, ()):
                if nome in fis_em[alvo]:
                    continue
                fis_em[alvo][nome] = Fi(nome=nome, versao=0)
                if alvo not in vistos:
                    vistos.add(alvo)
                    pendentes.append(alvo)

    # 3. renomear, descendo a árvore de dominância
    forma = CorpoSSA(nome=corpo.nome, entrada=corpo.entrada,
                     parametros=corpo.parametros)
    contador = {}
    filhos = {i: [] for i in vivos}
    for id_ in sorted(vivos):
        pai = idom.get(id_)
        if pai is not None:
            filhos[pai].append(id_)

    blocos_ssa = {}
    for id_ in sorted(vivos):
        original = por_id[id_]
        blocos_ssa[id_] = BlocoSSA(
            id=id_, rotulo=original.rotulo, saidas=list(original.saidas),
            terminador=original.terminador,
            fis=[fis_em[id_][n] for n in sorted(fis_em[id_])])

    def nova(nome):
        contador[nome] = contador.get(nome, 0) + 1
        return contador[nome]

    def descer(id_, versoes):
        bloco = blocos_ssa[id_]
        atuais = dict(versoes)

        for fi in bloco.fis:
            fi.versao = nova(fi.nome)
            atuais[fi.nome] = fi.versao
            forma.definicoes[(fi.nome, fi.versao)] = ("fi", id_)

        for nome in por_id[id_].escreve:
            # A variável de laço e o nome de um 'handle' nascem aqui, e
            # o valor delas não vem de instrução nenhuma: ganham versão
            # para o φ funcionar, e nunca ganham valor provado.
            versao = nova(nome)
            atuais[nome] = versao
            forma.definicoes[(nome, versao)] = ("liga", id_)
            forma.sem_valor.add((nome, versao))

        for indice, no in enumerate(por_id[id_].instrucoes):
            le = {n: atuais[n] for n in sorted(_mir.lidos(no)) if n in atuais}
            escritos = sorted(_mir.escritos(no))
            escreve = None
            if len(escritos) == 1:
                nome = escritos[0]
                versao = nova(nome)
                atuais[nome] = versao
                escreve = (nome, versao)
                forma.definicoes[(nome, versao)] = ("instrucao", id_, indice)
            else:
                # Desestruturação liga vários nomes numa instrução. SSA
                # de livro cria uma definição por nome; aqui basta
                # numerar os dois, e `escreve` fica vazio — quem pergunta
                # "qual definição?" recebe a do bloco.
                for nome in escritos:
                    versao = nova(nome)
                    atuais[nome] = versao
                    forma.definicoes[(nome, versao)] = ("instrucao", id_, indice)
            bloco.instrucoes.append(InstrucaoSSA(no=no, le=le, escreve=escreve))

        # as fontes dos φ dos sucessores
        for destino, _rotulo in por_id[id_].saidas:
            if destino not in blocos_ssa:
                continue
            for fi in blocos_ssa[destino].fis:
                if fi.nome in atuais:
                    fi.fontes[id_] = atuais[fi.nome]

        for filho in filhos[id_]:
            descer(filho, atuais)

    inicio = {p: 0 for p in corpo.parametros}
    for nome in inicio:
        contador[nome] = 0
    descer(corpo.entrada, inicio)

    forma.blocos = [blocos_ssa[i] for i in sorted(vivos)]
    # Um φ com uma fonte só não é junção de nada: ele aparece quando um
    # predecessor é inalcançável, e manter isso escondia a informação
    # de que o caminho não existe.
    for bloco in forma.blocos:
        bloco.fis = [f for f in bloco.fis if f.fontes]
    return forma


def definicao_de(forma, nome, versao):
    """Onde `nome` naquela versão foi criado, ou `None`."""
    onde = forma.definicoes.get((nome, versao))
    if onde is None:
        return None
    if onde[0] == "instrucao":
        _, id_, indice = onde
        return forma.bloco(id_).instrucoes[indice]
    if onde[0] == "fi":
        for fi in forma.bloco(onde[1]).fis:
            if fi.nome == nome and fi.versao == versao:
                return fi
    return onde


# ── propagação condicional ────────────────────────────────────

class _Sem:
    """"Ainda não se sabe" — diferente de "não se prova"."""

    def __repr__(self):                      # pragma: no cover
        return "⊥"


class _Varia:
    """"Não se prova": dois caminhos concordam em discordar."""

    def __repr__(self):                      # pragma: no cover
        return "⊤"


_SEM = _Sem()
_VARIA = _Varia()

_CONTAS = {
    "+": lambda a, b: a + b, "-": lambda a, b: a - b,
    "*": lambda a, b: a * b, "%": lambda a, b: a % b,
    "**": lambda a, b: a ** b, "~/": lambda a, b: a // b,
}
_COMPARA = {
    "is": lambda a, b: a == b, "==": lambda a, b: a == b,
    "isnt": lambda a, b: a != b, "!=": lambda a, b: a != b,
    "bigger": lambda a, b: a > b, ">": lambda a, b: a > b,
    "smaller": lambda a, b: a < b, "<": lambda a, b: a < b,
    "bigger_eq": lambda a, b: a >= b, ">=": lambda a, b: a >= b,
    "smaller_eq": lambda a, b: a <= b, "<=": lambda a, b: a <= b,
}


def constantes_condicionais(forma):
    """`({(nome, versão): valor}, {ids de bloco que nunca rodam})`.

    A propagação condicional esparsa, na forma que esta linguagem
    permite: o valor sobe pela rede de versões, e a **alcançabilidade**
    desce junto. Um ramo cuja condição se prova falsa não entra na conta,
    e por isso o que ele escreve não contamina o φ da junção.

    O que ela **não** tenta provar, de propósito:

    | Cala sobre | Porque |
    |---|---|
    | chamada de ação | o valor depende do corpo, e provar isso exige análise interprocedural |
    | leitura de índice, membro ou coleção | o conteúdo pode mudar por outro caminho |
    | conta que pode falhar (`1 / 0`) | dobrar isso moveria o erro para a carga |
    | nome que vem de fora do corpo | `:=` numa ação escreve o de fora, e o valor não é deste corpo |
    """
    valores = {chave: _VARIA for chave in forma.sem_valor}
    for nome in forma.parametros:
        valores[(nome, 0)] = _VARIA
    vivos = {forma.entrada}
    arestas = set()
    pendentes = [forma.entrada]

    def valor_de(nome, versao):
        return valores.get((nome, versao), _SEM)

    def avaliar(no, le):
        """O valor de uma expressão, ou `_SEM`/`_VARIA`."""
        if isinstance(no, (ast.IntegerLiteral, ast.FloatLiteral,
                           ast.StringLiteral, ast.BooleanLiteral)):
            return no.value
        if isinstance(no, ast.VoidLiteral):
            return None
        if isinstance(no, ast.Identifier):
            versao = le.get(no.name)
            if versao is None:
                return _VARIA
            return valor_de(no.name, versao)
        if isinstance(no, ast.NotOp):
            dentro = avaliar(no.operand, le)
            if dentro is _SEM or dentro is _VARIA:
                return dentro
            return not dentro
        if isinstance(no, ast.UnaryOp) and no.op in ("-", "+"):
            dentro = avaliar(no.operand, le)
            if dentro is _SEM or dentro is _VARIA:
                return dentro
            if not isinstance(dentro, (int, float)) or isinstance(dentro, bool):
                return _VARIA
            return -dentro if no.op == "-" else +dentro
        if isinstance(no, (ast.BinaryOp, ast.ComparisonOp)):
            tabela = _CONTAS if isinstance(no, ast.BinaryOp) else _COMPARA
            if no.op not in tabela:
                return _VARIA
            esquerda = avaliar(no.left, le)
            direita = avaliar(no.right, le)
            for lado in (esquerda, direita):
                if lado is _SEM:
                    return _SEM
                if lado is _VARIA:
                    return _VARIA
            if isinstance(esquerda, str) != isinstance(direita, str):
                return _VARIA
            try:
                return tabela[no.op](esquerda, direita)
            except Exception:
                return _VARIA          # '1 / 0' não vira erro de carga
        if isinstance(no, ast.LogicalOp):
            esquerda = avaliar(no.left, le)
            if esquerda is _SEM:
                return _SEM
            if esquerda is not _VARIA:
                if no.op == "and" and not esquerda:
                    return esquerda
                if no.op == "or" and esquerda:
                    return esquerda
            direita = avaliar(no.right, le)
            if esquerda is _VARIA or direita is _SEM or direita is _VARIA:
                return _VARIA
            return direita
        return _VARIA

    def anotar(chave, novo):
        antigo = valores.get(chave, _SEM)
        if antigo is _VARIA or novo is _SEM:
            return False
        if antigo is _SEM:
            valores[chave] = novo
            return True
        if antigo != novo or type(antigo) is not type(novo):
            valores[chave] = _VARIA
            return True
        return False

    for _ in range(len(forma.blocos) * 4 + 8):
        mudou = False
        for bloco in forma.blocos:
            if bloco.id not in vivos:
                continue

            # Um φ só junta o que vem por aresta PROVADA viva. É esta
            # linha que faz a análise ser condicional: o ramo morto não
            # contribui, e por isso a junção conclui.
            for fi in bloco.fis:
                juntos = _SEM
                for origem, versao in fi.fontes.items():
                    if (origem, bloco.id) not in arestas:
                        continue
                    vindo = valor_de(fi.nome, versao)
                    if vindo is _SEM:
                        continue
                    if juntos is _SEM:
                        juntos = vindo
                    elif juntos is _VARIA or juntos != vindo \
                            or type(juntos) is not type(vindo):
                        juntos = _VARIA
                if anotar((fi.nome, fi.versao), juntos):
                    mudou = True

            for instrucao in bloco.instrucoes:
                if instrucao.escreve is None:
                    continue
                nome, versao = instrucao.escreve
                novo = _valor_da_escrita(instrucao.no, instrucao.le, avaliar)
                if anotar((nome, versao), novo):
                    mudou = True

            # a alcançabilidade desce
            for destino, rotulo in bloco.saidas:
                if not _aresta_viva(bloco, rotulo, avaliar):
                    continue
                arestas.add((bloco.id, destino))
                if destino not in vivos:
                    vivos.add(destino)
                    mudou = True
        if not mudou:
            break

    # o que continua sem valor não se prova
    fixas = {chave: valor for chave, valor in valores.items()
             if valor is not _SEM and valor is not _VARIA}
    mortos = {b.id for b in forma.blocos} - vivos
    return fixas, mortos


def _valor_da_escrita(no, le, avaliar):
    if isinstance(no, ast.Assignment):
        if getattr(no, "compound_op", ""):
            return _VARIA
        return avaliar(no.value, le)
    if isinstance(no, ast.SteadyDeclaration):
        return avaliar(no.value, le)
    return _VARIA


def _condicao_do_bloco(bloco):
    """A última instrução de um bloco que termina em ramo é a condição."""
    if bloco.terminador != "ramo" or not bloco.instrucoes:
        return None
    return bloco.instrucoes[-1]


def _aresta_viva(bloco, rotulo, avaliar):
    """A aresta pode ser percorrida?

    Só `sim`/`nao` de um ramo com condição provada é que morrem. `halt`,
    `skip`, `erro`, `volta`, `point` e `default` **sempre** contam: o
    grafo não sabe quantas voltas um laço dá nem qual padrão casa, e
    supor isso mataria caminho que existe.

    E o `match` fica **inteiro** de fora, mesmo na aresta `nao`. A última
    instrução de um `match` é a expressão casada, não uma condição:
    `match 1:` tem valor provável e verdadeiro, e nada disso diz se
    algum `point` casa. Matar a saída dali seria afirmar que um dos
    padrões casa — o que exigiria avaliar padrão, e não valor.
    """
    if rotulo not in ("sim", "nao"):
        return True
    if any(r in ("point", "default") for _d, r in bloco.saidas):
        return True
    condicao = _condicao_do_bloco(bloco)
    if condicao is None:
        return True
    valor = avaliar(condicao.no, condicao.le)
    if valor is _SEM or valor is _VARIA:
        return True
    verdade = bool(valor)
    return verdade if rotulo == "sim" else not verdade


# ── o desenho ─────────────────────────────────────────────────

_SUBSCRITO = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _v(nome, versao):
    return f"{nome}{str(versao).translate(_SUBSCRITO)}"


def texto(formas, com_constantes=False):
    """O SSA escrito, com os φ e as versões."""
    if isinstance(formas, CorpoSSA):
        formas = [formas]
    linhas = []
    for forma in formas:
        cabeca = f"  {forma.nome}"
        if forma.parametros:
            cabeca += f"({', '.join(forma.parametros)})"
        linhas.append(f"{cabeca}   {len(forma.blocos)} bloco(s) alcancavel(is)")
        fixas, mortos = (constantes_condicionais(forma)
                         if com_constantes else ({}, set()))
        for bloco in forma.blocos:
            arestas = ", ".join(f"{d}" + (f" ({r})" if r else "")
                                for d, r in bloco.saidas)
            marca = "×" if bloco.id in mortos else " "
            fim = f" → {arestas}" if arestas else \
                (f" ⏹ {bloco.terminador}" if bloco.terminador else "")
            rotulo = f" [{bloco.rotulo}]" if bloco.rotulo else ""
            linhas.append(f"   {marca} bloco {bloco.id}{rotulo}{fim}")
            for fi in bloco.fis:
                fontes = ", ".join(f"{b}: {_v(fi.nome, v)}"
                                   for b, v in sorted(fi.fontes.items()))
                linhas.append(f"        {_v(fi.nome, fi.versao)} := φ({fontes})")
            for instrucao in bloco.instrucoes:
                partes = []
                if instrucao.escreve:
                    partes.append(f"{_v(*instrucao.escreve)} :=")
                partes.append(instrucao.no.__class__.__name__)
                if instrucao.le:
                    partes.append("le " + ", ".join(
                        _v(n, v) for n, v in sorted(instrucao.le.items())))
                linhas.append(f"        linha {instrucao.linha}: "
                              + "  ".join(partes))
        if com_constantes and fixas:
            linhas.append("        provadas: " + ", ".join(
                f"{_v(n, v)}={valor!r}"
                for (n, v), valor in sorted(fixas.items())))
        if com_constantes and mortos:
            linhas.append(f"        nunca rodam: {sorted(mortos)}")
        linhas.append("")
    return "\n".join(linhas)


def de_acao(no, nome=None):
    """O SSA de uma ação só — o que o `check` usa."""
    return construir(_mir.corpo_de_acao(no, nome))
