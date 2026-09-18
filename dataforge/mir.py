"""MIR — o grafo de fluxo, e o que ele prova.

A árvore diz o que o programa **é**; o grafo diz por onde ele **passa**.
São perguntas diferentes, e as que mais interessam a um analisador só a
segunda responde: este código é alcançável? este nome está definido em
todo caminho que chega aqui? este valor ainda vai ser lido? este local
escapa do quadro?

`construir(programa)` devolve um `Corpo` por ação — mais um para o nível
de topo — e cada corpo é uma lista de **blocos básicos**: uma sequência
de instruções sem desvio no meio, com arestas rotuladas para os blocos
seguintes.

Três decisões que valem lembrar:

1. **O MIR é construído a partir do HIR**, não da árvore crua. É o que
   paga a normalização: sem ela, `orif` e `perform` seriam dois casos a
   mais aqui, e um caso esquecido num construtor de grafo não dá erro —
   produz análise errada com cara de verdade.

2. **A aresta de erro sai da ENTRADA do `monitor`**, e não de cada
   instrução do corpo. Precisa ser assim para a análise ficar
   conservadora: o `handle` vê o estado de **antes** do corpo, que é o
   pior caso honesto. Uma aresta por instrução daria o mesmo resultado
   com um grafo três vezes maior.

3. **O que roda fora da ordem é opaco.** `thread`, `parallel`, `route`,
   `server` e as suas famílias entram como **uma** instrução. Abrir o
   corpo deles num grafo sequencial afirmaria uma ordem que não existe —
   e é exatamente sobre concorrência que uma afirmação errada custa.

As análises: `alcancaveis`, `vivas`, `talvez_nao_definidas`,
`constantes` e `escapam`. Só a terceira virou diagnóstico do `check`
(`talvez-nao-definida`), porque era a única pergunta que ele ainda não
sabia responder.
"""

import dataclasses
from dataclasses import dataclass, field

from . import ast_nodes as ast
from . import hir as _hir

__all__ = ["Bloco", "Corpo", "construir", "texto", "destinos",
           "alcancaveis", "vivas", "talvez_nao_definidas", "constantes",
           "escapam"]


@dataclass
class Bloco:
    """Uma sequência sem desvio no meio."""
    id: int
    rotulo: str = ""
    instrucoes: list = field(default_factory=list)
    #: [(id do destino, rótulo da aresta)]
    saidas: list = field(default_factory=list)
    #: '' | 'ramo' | 'yield' | 'halt' | 'skip' | 'trigger' | 'fim'
    terminador: str = ""
    #: nomes que passam a existir ao ENTRAR no bloco (variável de laço,
    #: nome do erro de um 'handle'). Não são instruções, e sem este
    #: campo virariam nós sintéticos que não existem no programa.
    escreve: tuple = ()
    linha: int = 0


@dataclass
class Corpo:
    """O grafo de uma ação, de uma rota, ou do nível de topo."""
    nome: str
    blocos: list = field(default_factory=list)
    entrada: int = 0
    linha: int = 0
    parametros: tuple = ()
    #: o que faz uma análise calar — ver `talvez_nao_definidas`
    tem_monitor: bool = False
    tem_closure: bool = False
    tem_defer: bool = False
    tem_opaco: bool = False


def destinos(bloco):
    """Só os ids, sem os rótulos — o que um teste de forma precisa."""
    return [d for d, _ in bloco.saidas]


# ── o que um nó lê e o que ele escreve ────────────────────────

#: Um corpo que roda fora da ordem, ou depois. Entra como UMA instrução.
_OPACOS = (ast.ThreadBlock, ast.ParallelBlock, ast.ServerBlock,
           ast.IgniteStatement, ast.CrucibleBlock, ast.TrialBlock,
           ast.BenchBlock, ast.FixtureBlock, ast.HookBlock,
           ast.ChannelDeclaration, ast.StreamExpression)

#: Declaração: opaca no corpo que a contém, e dona de um `Corpo` próprio.
_DECLARACOES = (ast.ActionDeclaration, ast.BlueprintDeclaration,
                ast.RecordDeclaration, ast.TraitDeclaration,
                ast.EnumDeclaration, ast.TypeDeclaration,
                ast.PropertyDeclaration, ast.OperatorDeclaration,
                ast.StaticDeclaration, ast.AugmentDeclaration,
                ast.ContractDeclaration, ast.ShadowDeclaration,
                ast.SlotsDeclaration, ast.ComptimeBlock)

_FECHAMENTOS = (ast.LambdaExpression, ast.ActionDeclaration,
                ast.BlueprintDeclaration, ast.ThreadBlock,
                ast.ParallelBlock, ast.StreamExpression)


def _sub(no):
    """Os filhos diretos de um nó, achatados."""
    if not isinstance(no, ast.ASTNode) or isinstance(no, ast.ValorPronto):
        return
    for campo in dataclasses.fields(no):
        valor = getattr(no, campo.name)
        yield from _achatar(valor)


def _achatar(valor):
    if isinstance(valor, ast.ASTNode):
        yield valor
    elif isinstance(valor, (list, tuple)):
        for item in valor:
            yield from _achatar(item)
    elif isinstance(valor, dict):
        for item in valor.values():
            yield from _achatar(item)


def _todos(no):
    """O nó e toda a subárvore."""
    if isinstance(no, ast.ASTNode):
        yield no
        for filho in _sub(no):
            yield from _todos(filho)
    else:
        for filho in _achatar(no):
            yield from _todos(filho)


def lidos(no):
    """Os nomes que a avaliação deste nó **lê de fora**.

    Duas exclusões, e as duas foram bug antes de serem regra:

    1. **o alvo de uma atribuição simples não é leitura** — é o que
       distingue `x := 1` de `x := x + 1`, e a distinção é a base de
       toda análise de fluxo de dados;
    2. **o que a própria expressão liga não é leitura de fora** — o `p`
       de `[p * 2 cycle p in xs]`, o parâmetro de um `lambda`, o `v` de
       um `>> morph v: …`. Sem isto, toda compreensão acusaria o próprio
       índice de não estar definido, e a análise ficaria inútil no
       caminho mais comum da linguagem.

    E um caso que devolve **nada**: os nomes de um verbo de quadro
    (`>> onde valor bigger 50`) são **colunas**, não variáveis. Lê-los
    como nome do escopo é o falso alarme que a doc do `check` descreve.
    """
    saida = set()

    def andar(alvo, ligados):
        if not isinstance(alvo, ast.ASTNode):
            for filho in _achatar(alvo):
                andar(filho, ligados)
            return

        if isinstance(alvo, ast.Identifier):
            if alvo.name not in ligados:
                saida.add(alvo.name)
            return

        if isinstance(alvo, ast.Assignment) and isinstance(alvo.target,
                                                           ast.Identifier):
            if alvo.compound_op:
                saida.add(alvo.target.name)
            andar(alvo.value, ligados)
            return

        if isinstance(alvo, ast.SteadyDeclaration):
            andar(alvo.value, ligados)
            return

        if isinstance(alvo, ast.QuadroOperation):
            return

        if isinstance(alvo, (ast.ListComprehension, ast.VaultComprehension)):
            dentro = set(ligados)
            for clausula in getattr(alvo, "clauses", None) or ():
                andar(getattr(clausula, "source", None), dentro)
                if getattr(clausula, "var", ""):
                    dentro.add(clausula.var)
                for nome in getattr(clausula, "targets", None) or ():
                    if isinstance(nome, str):
                        dentro.add(nome)
                andar(getattr(clausula, "condition", None), dentro)
            for campo in ("expression", "key", "value"):
                andar(getattr(alvo, campo, None), dentro)
            return

        if isinstance(alvo, (ast.LambdaExpression, ast.ActionDeclaration,
                             ast.BlueprintDeclaration)):
            # O parâmetro é ligado pela declaração: contá-lo como leitura
            # faria a ação parecer capturar o nome que ela própria cria —
            # e a escapatória apontaria o 'n' de 'action f(n)'.
            crus = (getattr(alvo, "params", None)
                    or getattr(alvo, "constructor_params", None) or [])
            dentro = set(ligados) | {
                p if isinstance(p, str) else getattr(p, "name", "")
                for p in crus} | {"self", "this", "root"}
            andar(getattr(alvo, "defaults", None), ligados)
            andar(getattr(alvo, "body", None), dentro)
            for campo in ("methods", "fields_decl", "postconditions",
                          "members", "invariants", "properties"):
                andar(getattr(alvo, campo, None), dentro)
            return

        if isinstance(alvo, (ast.SiftOperation, ast.MorphOperation)):
            dentro = set(ligados) | ({alvo.param} if alvo.param else set())
            andar(getattr(alvo, "condition", None), dentro)
            andar(getattr(alvo, "expression", None), dentro)
            if alvo.func_ref:
                saida.add(alvo.func_ref)
            return

        if isinstance(alvo, ast.DistillOperation):
            dentro = set(ligados) | {n for n in (alvo.acc_param,
                                                 alvo.val_param) if n}
            andar(alvo.expression, dentro)
            andar(alvo.initial, ligados)
            if alvo.func_ref:
                saida.add(alvo.func_ref)
            return

        if isinstance(alvo, (ast.CycleIn, ast.CycleFromTo, ast.ObserveBlock)):
            dentro = set(ligados)
            if getattr(alvo, "var", ""):
                dentro.add(alvo.var)
            for nome in getattr(alvo, "vars", None) or ():
                if isinstance(nome, str):
                    dentro.add(nome)
            for campo in ("collection", "source", "start", "end", "step"):
                andar(getattr(alvo, campo, None), ligados)
            andar(alvo.body, dentro)
            return

        if isinstance(alvo, ast.MatchBlock):
            andar(alvo.expression, ligados)
            for caso in alvo.points or ():
                corpo, guarda, ligou = _partes_do_point(caso)
                dentro = set(ligados) | set(ligou)
                andar(guarda, dentro)
                andar(corpo, dentro)
            andar(alvo.default_body, ligados)
            return

        if isinstance(alvo, ast.MonitorBlock):
            andar(alvo.body, ligados)
            for clausula in alvo.handles or ():
                dentro = set(ligados)
                dentro.add(getattr(clausula, "error_name", "") or "error")
                andar(clausula.body, dentro)
            andar(alvo.ensure_body, ligados)
            return

        for filho in _sub(alvo):
            andar(filho, ligados)

    andar(no, frozenset())
    return saida


def escritos(no):
    """Os nomes que a execução deste nó **liga**."""
    saida = set()
    for alvo in _todos(no):
        if isinstance(alvo, ast.Assignment) and isinstance(alvo.target,
                                                           ast.Identifier):
            saida.add(alvo.target.name)
        elif isinstance(alvo, ast.SteadyDeclaration):
            saida.add(alvo.name)
        elif isinstance(alvo, ast.DestructuringAssignment):
            for nome in getattr(alvo, "targets", []) or []:
                if isinstance(nome, str):
                    saida.add(nome)
        elif isinstance(alvo, (ast.CycleIn, ast.CycleFromTo,
                               ast.ComprehensionClause, ast.ObserveBlock)):
            if getattr(alvo, "var", ""):
                saida.add(alvo.var)
            for nome in (list(getattr(alvo, "vars", None) or [])
                         + list(getattr(alvo, "targets", None) or [])):
                if isinstance(nome, str):
                    saida.add(nome)
        elif isinstance(alvo, _DECLARACOES) and getattr(alvo, "name", ""):
            saida.add(alvo.name)
    return saida


# ── a construção ──────────────────────────────────────────────

class _Construtor:
    def __init__(self, nome, parametros, linha):
        self.corpo = Corpo(nome=nome, parametros=tuple(parametros),
                           linha=linha)
        self.atual = self._novo("entrada")
        self.corpo.entrada = self.atual.id
        self.lacos = []          # [(id da cabeça, id da saída)]
        self.tratadores = []     # [id do bloco de tratador]

    # -- mecânica --

    def _novo(self, rotulo="", escreve=()):
        bloco = Bloco(id=len(self.corpo.blocos), rotulo=rotulo,
                      escreve=tuple(escreve))
        self.corpo.blocos.append(bloco)
        return bloco

    def _ligar(self, de, para, rotulo=""):
        destino = para.id if isinstance(para, Bloco) else para
        if (destino, rotulo) not in de.saidas:
            de.saidas.append((destino, rotulo))

    def _garantir(self):
        """O bloco corrente, criando um inalcançável se não houver."""
        if self.atual is None:
            self.atual = self._novo("morto")
        return self.atual

    def _erro_para_o_tratador(self, bloco):
        if self.tratadores:
            self._ligar(bloco, self.tratadores[-1], "erro")

    # -- corpo --

    def bloco(self, instrucoes):
        for instrucao in instrucoes or ():
            self.instrucao(instrucao)

    def instrucao(self, no):
        metodo = _TABELA.get(no.__class__)
        if metodo is not None:
            metodo(self, no)
        else:
            self._simples(no)

    def _simples(self, no):
        atual = self._garantir()
        atual.instrucoes.append(no)
        if not atual.linha:
            atual.linha = getattr(no, "line", 0)
        if isinstance(no, _OPACOS) or any(isinstance(d, _OPACOS)
                                          for d in _todos(no)):
            self.corpo.tem_opaco = True
        if any(isinstance(d, _FECHAMENTOS) for d in _todos(no)):
            self.corpo.tem_closure = True

    # -- desvios --

    def _given(self, no):
        cabeca = self._garantir()
        if no.condition is not None:
            cabeca.instrucoes.append(no.condition)
        cabeca.terminador = "ramo"
        pendentes, cai_fora = [], None

        entao = self._novo("sim")
        self._ligar(cabeca, entao, "sim")
        self.atual = entao
        self.bloco(no.body)
        if self.atual is not None:
            pendentes.append(self.atual)

        if no.otherwise_body:
            senao = self._novo("nao")
            self._ligar(cabeca, senao, "nao")
            self.atual = senao
            self.bloco(no.otherwise_body)
            if self.atual is not None:
                pendentes.append(self.atual)
        else:
            cai_fora = cabeca

        fim = self._novo("juncao")
        for bloco in pendentes:
            self._ligar(bloco, fim)
        if cai_fora is not None:
            self._ligar(cai_fora, fim, "nao")
        self.atual = fim

    def _guard(self, no):
        """`guard c else: …` — o ramo do `else` normalmente encerra."""
        cabeca = self._garantir()
        if no.condition is not None:
            cabeca.instrucoes.append(no.condition)
        cabeca.terminador = "ramo"

        senao = self._novo("nao")
        self._ligar(cabeca, senao, "nao")
        self.atual = senao
        self.bloco(no.else_body)
        pendentes = [self.atual] if self.atual is not None else []

        fim = self._novo("sim")
        self._ligar(cabeca, fim, "sim")
        for bloco in pendentes:
            self._ligar(bloco, fim)
        self.atual = fim

    def _match(self, no):
        cabeca = self._garantir()
        if no.expression is not None:
            cabeca.instrucoes.append(no.expression)
        cabeca.terminador = "ramo"
        pendentes = []

        for i, caso in enumerate(no.points or ()):
            corpo_do_caso, guarda, ligado = _partes_do_point(caso)
            bloco = self._novo(f"point {i}", escreve=ligado)
            if guarda is not None:
                bloco.instrucoes.append(guarda)
            self._ligar(cabeca, bloco, "point")
            self.atual = bloco
            self.bloco(corpo_do_caso)
            if self.atual is not None:
                pendentes.append(self.atual)

        tem_default = bool(no.default_body)
        if tem_default:
            bloco = self._novo("default")
            self._ligar(cabeca, bloco, "default")
            self.atual = bloco
            self.bloco(no.default_body)
            if self.atual is not None:
                pendentes.append(self.atual)

        fim = self._novo("juncao")
        for bloco in pendentes:
            self._ligar(bloco, fim)
        if not tem_default:
            self._ligar(cabeca, fim, "nao")
        self.atual = fim

    # -- laços --

    def _laco(self, no, fontes, liga=()):
        antes = self._garantir()
        cabeca = self._novo("condicao")
        self._ligar(antes, cabeca)
        for fonte in fontes:
            if fonte is not None:
                cabeca.instrucoes.append(fonte)
        cabeca.terminador = "ramo"

        corpo = self._novo("corpo", escreve=liga)
        self._ligar(cabeca, corpo, "sim")
        saida = self._novo("saida")
        self._ligar(cabeca, saida, "nao")

        self.lacos.append((cabeca.id, saida.id))
        self.atual = corpo
        self.bloco(no.body)
        if self.atual is not None:
            self._ligar(self.atual, cabeca, "volta")
        self.lacos.pop()
        self.atual = saida

    def _persist(self, no):
        self._laco(no, [no.condition])

    def _cycle_em(self, no):
        nomes = [n for n in ([no.var] + list(no.vars or [])) if n]
        self._laco(no, [no.collection], liga=nomes)

    def _cycle_de_ate(self, no):
        self._laco(no, [no.start, no.end, no.step],
                   liga=[no.var] if no.var else ())

    def _perform(self, no):
        """Sobrevive ao HIR só quando alguém constrói o MIR da árvore crua."""
        antes = self._garantir()
        corpo = self._novo("corpo")
        self._ligar(antes, corpo)
        cabeca = self._novo("condicao")
        saida = self._novo("saida")

        self.lacos.append((cabeca.id, saida.id))
        self.atual = corpo
        self.bloco(no.body)
        if self.atual is not None:
            self._ligar(self.atual, cabeca)
        self.lacos.pop()

        if no.condition is not None:
            cabeca.instrucoes.append(no.condition)
        cabeca.terminador = "ramo"
        self._ligar(cabeca, corpo, "volta")
        self._ligar(cabeca, saida, "nao")
        self.atual = saida

    def _retry(self, no):
        """`retry n:` é um laço com um tratador no caminho de volta."""
        antes = self._garantir()
        cabeca = self._novo("condicao")
        self._ligar(antes, cabeca)
        if no.count is not None:
            cabeca.instrucoes.append(no.count)
        cabeca.terminador = "ramo"

        corpo = self._novo("corpo")
        self._ligar(cabeca, corpo, "sim")
        saida = self._novo("saida")
        self._ligar(cabeca, saida, "nao")

        tratador = None
        if no.handle_body:
            tratador = self._novo("tratador", escreve=(no.handle_name,))
            self._ligar(corpo, tratador, "erro")

        self.lacos.append((cabeca.id, saida.id))
        self.tratadores.append(tratador.id if tratador else None)
        if self.tratadores[-1] is None:
            self.tratadores.pop()
        self.atual = corpo
        self.bloco(no.body)
        if self.atual is not None:
            self._ligar(self.atual, cabeca, "volta")
        if tratador is not None:
            self.tratadores.pop()
            self.atual = tratador
            self.bloco(no.handle_body)
            if self.atual is not None:
                self._ligar(self.atual, cabeca, "volta")
        self.lacos.pop()
        self.atual = saida
        self.corpo.tem_monitor = True

    # -- erro --

    def _monitor(self, no):
        self.corpo.tem_monitor = True
        antes = self._garantir()

        corpo = self._novo("corpo")
        self._ligar(antes, corpo)

        tratadores = []
        for clausula in no.handles or ():
            nome = getattr(clausula, "error_name", "error") or "error"
            bloco = self._novo("tratador", escreve=(nome,))
            self._ligar(corpo, bloco, "erro")
            tratadores.append((bloco, clausula))

        # A aresta de erro sai da ENTRADA do corpo: o tratador vê o
        # estado de antes, que é o pior caso honesto.
        self.tratadores.append(tratadores[0][0].id if tratadores else None)
        if self.tratadores[-1] is None:
            self.tratadores.pop()

        self.atual = corpo
        self.bloco(no.body)
        pendentes = [self.atual] if self.atual is not None else []
        if tratadores:
            self.tratadores.pop()

        for bloco, clausula in tratadores:
            self.atual = bloco
            self.bloco(clausula.body)
            if self.atual is not None:
                pendentes.append(self.atual)

        if no.ensure_body:
            garantia = self._novo("ensure")
            for bloco in pendentes:
                self._ligar(bloco, garantia)
            if not pendentes:
                self._ligar(corpo, garantia, "erro")
            self.atual = garantia
            self.bloco(no.ensure_body)
            pendentes = [self.atual] if self.atual is not None else []

        fim = self._novo("juncao")
        for bloco in pendentes:
            self._ligar(bloco, fim)
        self.atual = fim

    def _trigger(self, no):
        atual = self._garantir()
        atual.instrucoes.append(no)
        atual.terminador = "trigger"
        self._erro_para_o_tratador(atual)
        self.atual = None

    def _defer(self, no):
        """Roda na SAÍDA da ação, onde quer que esteja escrito."""
        self.corpo.tem_defer = True
        atual = self._garantir()
        adiado = self._novo("defer")
        self._ligar(atual, adiado, "defer")
        anterior, self.atual = self.atual, adiado
        self.bloco(no.body if isinstance(getattr(no, "body", None), list)
                   else [no.body] if getattr(no, "body", None) else [])
        self.atual = anterior

    # -- saltos --

    def _devolver(self, no):
        atual = self._garantir()
        atual.instrucoes.append(no)
        atual.terminador = "yield"
        self.atual = None

    def _halt(self, no):
        atual = self._garantir()
        atual.instrucoes.append(no)
        atual.terminador = "halt"
        if self.lacos:
            self._ligar(atual, self.lacos[-1][1], "halt")
        self.atual = None

    def _skip(self, no):
        atual = self._garantir()
        atual.instrucoes.append(no)
        atual.terminador = "skip"
        if self.lacos:
            self._ligar(atual, self.lacos[-1][0], "skip")
        self.atual = None

    # -- regiões que rodam em linha --

    def _em_linha(self, no):
        atual = self._garantir()
        atual.instrucoes.append(_Marca(no))
        self.bloco(_corpo_de(no))


@dataclass
class _Marca(ast.ASTNode):
    """O cabeçalho de uma região aberta em linha, para o desenho."""
    alvo: object = None

    def __post_init__(self):
        if self.alvo is not None:
            self.line = getattr(self.alvo, "line", 0)
            self.column = getattr(self.alvo, "column", 0)


def _corpo_de(no):
    for campo in ("body", "blocks"):
        valor = getattr(no, campo, None)
        if isinstance(valor, list):
            return valor
    return []


def _partes_do_point(caso):
    """`(corpo, guarda, nomes que o padrão liga)` de um `point`."""
    if isinstance(caso, ast.MatchCase):
        return caso.body, caso.guard, _nomes_do_padrao(caso.pattern)
    if isinstance(caso, (tuple, list)) and len(caso) >= 2:
        return caso[1], None, ()
    return [], None, ()


def _nomes_do_padrao(padrao):
    nomes = []
    for no in _todos(padrao) if padrao is not None else ():
        for campo in ("binding", "name"):
            valor = getattr(no, campo, None)
            if isinstance(valor, str) and valor and valor != "_":
                nomes.append(valor)
    return tuple(nomes)


_TABELA = {
    ast.GivenBlock: _Construtor._given,
    ast.GuardStatement: _Construtor._guard,
    ast.MatchBlock: _Construtor._match,
    ast.PersistBlock: _Construtor._persist,
    ast.CycleIn: _Construtor._cycle_em,
    ast.CycleFromTo: _Construtor._cycle_de_ate,
    ast.PerformBlock: _Construtor._perform,
    ast.RetryBlock: _Construtor._retry,
    ast.MonitorBlock: _Construtor._monitor,
    ast.TriggerStatement: _Construtor._trigger,
    ast.DeferStatement: _Construtor._defer,
    ast.YieldStatement: _Construtor._devolver,
    ast.HaltStatement: _Construtor._halt,
    ast.SkipStatement: _Construtor._skip,
    ast.ObserveBlock: _Construtor._em_linha,
    ast.WithBlock: _Construtor._em_linha,
}


def _fechar(corpo):
    """Todo bloco sem saída termina — um buraco no grafo é bug calado."""
    for bloco in corpo.blocos:
        if not bloco.saidas and not bloco.terminador:
            bloco.terminador = "fim"
    return corpo


def _corpo_para(nome, instrucoes, parametros=(), linha=0):
    construtor = _Construtor(nome, parametros, linha)
    construtor.bloco(instrucoes)
    return _fechar(construtor.corpo)


def construir(programa, normalizar=True):
    """Um `Corpo` por ação (e por rota), mais `(programa)` no topo."""
    raiz = _hir.normalizar(programa) if normalizar else programa
    corpos = [_corpo_para("(programa)", getattr(raiz, "body", []) or [],
                          linha=getattr(raiz, "line", 0))]
    corpos.extend(_corpos_aninhados(raiz))
    return corpos


def _corpos_aninhados(raiz):
    saida = []

    def visitar(no, prefixo):
        if isinstance(no, ast.ActionDeclaration):
            saida.append(_corpo_para(
                f"{prefixo}{no.name}", no.body,
                parametros=[p if isinstance(p, str) else
                            getattr(p, "name", str(p)) for p in (no.params or [])],
                linha=no.line))
        elif isinstance(no, ast.RouteBlock):
            caminho = getattr(no, "path", "") or getattr(no, "pattern", "")
            saida.append(_corpo_para(f"route {caminho}".strip(), no.body,
                                     linha=no.line))
        elif isinstance(no, ast.PropertyDeclaration):
            for metade, sufixo in (("getter_body", ".get"),
                                   ("setter_body", ".set")):
                corpo = getattr(no, metade, None)
                if corpo:
                    saida.append(_corpo_para(
                        f"{prefixo}{no.name}{sufixo}", corpo, linha=no.line))

        dentro = prefixo
        if isinstance(no, (ast.BlueprintDeclaration, ast.RecordDeclaration,
                           ast.TraitDeclaration)):
            dentro = f"{getattr(no, 'name', '?')}."
        for filho in _sub(no):
            visitar(filho, dentro)

    for filho in _sub(raiz):
        visitar(filho, "")
    return saida


# ── as análises ───────────────────────────────────────────────

def alcancaveis(corpo):
    """Os ids que se alcançam a partir da entrada."""
    vistos, pilha = set(), [corpo.entrada]
    por_id = {b.id: b for b in corpo.blocos}
    while pilha:
        atual = pilha.pop()
        if atual in vistos or atual not in por_id:
            continue
        vistos.add(atual)
        pilha.extend(destinos(por_id[atual]))
    return vistos


def _predecessores(corpo, so_alcancaveis=None):
    antes = {b.id: [] for b in corpo.blocos}
    for bloco in corpo.blocos:
        if so_alcancaveis is not None and bloco.id not in so_alcancaveis:
            continue
        for destino in destinos(bloco):
            if destino in antes:
                antes[destino].append(bloco.id)
    return antes


def vivas(corpo):
    """`{id: nomes que ainda serão lidos}` — para trás, união nas junções.

    Um nome vivo na entrada de um bloco é um nome cujo valor atual ainda
    importa. É a metade que responde "esta escrita serve para alguma
    coisa?", e a base de qualquer alocação de registrador — que aqui não
    existe, mas a pergunta é a mesma na hora de olhar um corpo grande.
    """
    por_id = {b.id: b for b in corpo.blocos}
    entrada = {b.id: set() for b in corpo.blocos}
    mudou = True
    while mudou:
        mudou = False
        for bloco in reversed(corpo.blocos):
            depois = set()
            for destino in destinos(bloco):
                depois |= entrada.get(destino, set())
            estado = set(depois)
            for instrucao in reversed(bloco.instrucoes):
                estado -= escritos(instrucao)
                estado |= lidos(instrucao)
            estado -= set(bloco.escreve)
            if estado != entrada[bloco.id]:
                entrada[bloco.id] = estado
                mudou = True
    return entrada


def talvez_nao_definidas(corpo, externos=()):
    """Os nomes lidos num ponto que algum caminho não definiu.

    ```
    given cond:
        rotulo := "alto"
    yield rotulo          # e quando 'cond' e falso?
    ```

    É a pergunta que o `check` não sabia responder: ele registra o nome
    do ramo — e isso está certo, porque `given` compartilha o escopo —
    mas não olha por quantos caminhos ele passa.

    O que a faz **calar**, e cada silêncio é um falso alarme que não
    acontece:

    | Cala quando | Porque |
    |---|---|
    | o corpo tem `monitor` | o `handle` lê o que o corpo talvez não tenha atribuído, e isso é o uso normal |
    | o corpo tem `defer` | ele roda na saída, fora da ordem do grafo |
    | há fechamento no corpo | um `lambda` pode ligar o nome depois, e o grafo não vê quando ele roda |
    | há bloco opaco (`thread`, `parallel`) | a ordem é outra |
    | o nome existe **fora** | `:=` dentro de uma ação escreve o de fora quando ele existe — medido |
    | o nome não é escrito neste corpo | então é global, embutido ou erro, e isso o `check` já responde |
    """
    if corpo.tem_monitor or corpo.tem_defer or corpo.tem_closure \
            or corpo.tem_opaco:
        return []

    vivos = alcancaveis(corpo)
    por_id = {b.id: b for b in corpo.blocos}

    # Os conjuntos são calculados UMA vez. Sem isto, o ponto fixo
    # reandaria a subárvore de cada instrução a cada volta, e um corpo
    # de duzentas linhas ficaria quadrático — num analisador que roda
    # sobre trezentos e sessenta arquivos.
    le, liga, tudo_que_liga = {}, {}, set()
    for bloco in corpo.blocos:
        if bloco.id not in vivos:
            continue
        for indice, instrucao in enumerate(bloco.instrucoes):
            chave = (bloco.id, indice)
            le[chave] = lidos(instrucao)
            liga[chave] = escritos(instrucao)
            tudo_que_liga |= liga[chave]
        tudo_que_liga |= set(bloco.escreve)

    candidatos = tudo_que_liga - set(externos) - set(corpo.parametros)
    if not candidatos:
        return []

    antes = _predecessores(corpo, vivos)
    # 'definido em todo caminho': para frente, interseção nas junções.
    # O topo é "tudo definido", senão um laço nunca converge.
    entrada = {i: set(candidatos) for i in vivos}
    entrada[corpo.entrada] = set()
    saida = {i: set(candidatos) for i in vivos}
    ordem = sorted(vivos)

    def depois_de(id_):
        estado = entrada[id_] | set(por_id[id_].escreve)
        for indice in range(len(por_id[id_].instrucoes)):
            estado = estado | liga[(id_, indice)]
        return estado

    for _ in range(len(vivos) + 2):
        mudou = False
        for id_ in ordem:
            if id_ != corpo.entrada:
                fontes = [saida[p] for p in antes[id_] if p in saida]
                novo = set.intersection(*fontes) if fontes else set()
                if novo != entrada[id_]:
                    entrada[id_] = novo
                    mudou = True
            estado = depois_de(id_)
            if estado != saida[id_]:
                saida[id_] = estado
                mudou = True
        if not mudou:
            break

    achados, ja = [], set()
    for id_ in ordem:
        bloco = por_id[id_]
        estado = entrada[id_] | set(bloco.escreve)
        for indice, instrucao in enumerate(bloco.instrucoes):
            for nome in sorted(le[(id_, indice)] & candidatos):
                if nome not in estado and nome not in ja:
                    ja.add(nome)
                    achados.append((nome, instrucao))
            estado = estado | liga[(id_, indice)]
    return achados


def corpo_de_acao(no, nome=None):
    """O `Corpo` de uma ação só, já normalizado — o que o `check` usa."""
    corpo_normalizado = _hir.normalizar(ast.Program(body=list(no.body or [])))
    parametros = [p if isinstance(p, str) else getattr(p, "name", str(p))
                  for p in (getattr(no, "params", None) or [])]
    return _corpo_para(nome or getattr(no, "name", "(acao)"),
                       corpo_normalizado.body, parametros=parametros,
                       linha=getattr(no, "line", 0))


_PUROS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
          "*": lambda a, b: a * b, "%": lambda a, b: a % b,
          "**": lambda a, b: a ** b}


def constantes(corpo):
    """`{nome: valor}` no fim do corpo, só onde todo caminho concorda.

    Propagação de constante de verdade: uma atribuição que o grafo prova
    única. Um nome que dois ramos escrevem com valores diferentes sai da
    tabela — é a interseção que faz isso, e é ela que separa esta
    análise de uma varredura de texto.
    """
    vivos = alcancaveis(corpo)
    por_id = {b.id: b for b in corpo.blocos}
    antes = _predecessores(corpo, vivos)
    entrada = {i: None for i in vivos}      # None = ainda não visitado
    entrada[corpo.entrada] = {}
    saida = {}

    def juntar(a, b):
        return {k: v for k, v in a.items() if k in b and b[k] == v}

    for _ in range(len(vivos) + 2):
        mudou = False
        for id_ in sorted(vivos):
            bloco = por_id[id_]
            if id_ != corpo.entrada:
                fontes = [saida[p] for p in antes[id_] if p in saida]
                novo = {}
                if fontes:
                    novo = fontes[0]
                    for outro in fontes[1:]:
                        novo = juntar(novo, outro)
                if novo != entrada[id_]:
                    entrada[id_] = novo
                    mudou = True
            estado = dict(entrada[id_] or {})
            for nome in bloco.escreve:
                estado.pop(nome, None)
            for instrucao in bloco.instrucoes:
                _aplicar(instrucao, estado)
            if saida.get(id_) != estado:
                saida[id_] = estado
                mudou = True
        if not mudou:
            break

    finais = [saida[b.id] for b in corpo.blocos
              if b.id in vivos and not destinos(b)]
    if not finais:
        return {}
    resultado = finais[0]
    for outro in finais[1:]:
        resultado = juntar(resultado, outro)
    return resultado


def _valor(no, tabela):
    """O valor de uma expressão, ou `_SEM` quando não se prova."""
    if isinstance(no, (ast.IntegerLiteral, ast.FloatLiteral,
                       ast.StringLiteral)):
        return no.value
    if isinstance(no, ast.BooleanLiteral):
        return no.value
    if isinstance(no, ast.Identifier):
        return tabela.get(no.name, _SEM)
    if isinstance(no, ast.BinaryOp) and no.op in _PUROS:
        esquerda = _valor(no.left, tabela)
        direita = _valor(no.right, tabela)
        if esquerda is _SEM or direita is _SEM:
            return _SEM
        if isinstance(esquerda, str) != isinstance(direita, str):
            return _SEM
        try:
            return _PUROS[no.op](esquerda, direita)
        except Exception:
            return _SEM
    return _SEM


class _Sem:
    def __repr__(self):                      # pragma: no cover
        return "<sem valor>"


_SEM = _Sem()


def _aplicar(instrucao, estado):
    if isinstance(instrucao, (ast.Assignment, ast.SteadyDeclaration)):
        alvo = getattr(instrucao, "target", None)
        nome = alvo.name if isinstance(alvo, ast.Identifier) \
            else getattr(instrucao, "name", None)
        if not nome:
            return
        if getattr(instrucao, "compound_op", ""):
            estado.pop(nome, None)
            return
        valor = _valor(instrucao.value, estado)
        if valor is _SEM:
            estado.pop(nome, None)
        else:
            estado[nome] = valor
        return
    for nome in escritos(instrucao):
        estado.pop(nome, None)


#: Por que um local escapa do quadro. A ordem é a da mensagem.
_MOTIVOS = (
    ("devolvido", "sai da ação por 'yield'"),
    ("fechamento", "um 'lambda' ou uma ação aninhada o lê"),
    ("concorrente", "um 'thread' ou 'parallel' o lê"),
    ("guardado", "vai para dentro de um objeto ou coleção"),
)


def escapam(corpo):
    """`{nome: motivo}` — os locais que saem do quadro.

    É a pergunta que decide se um valor pode viver na pilha, e por isso
    é o primeiro passo de qualquer alocação de escape. Aqui ela não
    move nada de lugar — o coletor do Python continua respondendo por
    isso — mas responde uma pergunta prática: **o que mais alguém pode
    estar lendo?** Um nome que escapa para um `thread` é a metade de
    todo bug de concorrência.
    """
    locais = set()
    for bloco in corpo.blocos:
        locais |= set(bloco.escreve)
        for instrucao in bloco.instrucoes:
            locais |= escritos(instrucao)
    if not locais:
        return {}

    saida = {}

    def marcar(nomes, motivo):
        for nome in nomes & locais:
            saida.setdefault(nome, motivo)

    for bloco in corpo.blocos:
        for instrucao in bloco.instrucoes:
            for no in _todos(instrucao):
                if isinstance(no, ast.YieldStatement):
                    marcar(lidos(no), "devolvido")
                elif isinstance(no, (ast.ThreadBlock, ast.ParallelBlock)):
                    marcar(lidos(no), "concorrente")
                elif isinstance(no, (ast.LambdaExpression,
                                     ast.ActionDeclaration)):
                    marcar(lidos(no), "fechamento")
                elif isinstance(no, ast.Assignment) and isinstance(
                        no.target, (ast.MemberAccess, ast.IndexAccess)):
                    marcar(lidos(no.value), "guardado")
                elif isinstance(no, ast.MethodCall) and no.method in _GUARDAM:
                    for argumento in no.args or ():
                        marcar(lidos(argumento), "guardado")
    return saida


#: Métodos que põem o argumento **dentro** de algo que sobrevive à
#: chamada. Fechada de propósito: um nome que "parece guardar" e não
#: guarda produziria escapatória onde não há.
_GUARDAM = frozenset({"append", "add", "insert", "extend", "push",
                      "put", "send", "set", "update"})


# ── o desenho ─────────────────────────────────────────────────

def texto(corpos, com_analises=False):
    """O grafo escrito, um corpo por vez."""
    if isinstance(corpos, Corpo):
        corpos = [corpos]
    linhas = []
    for corpo in corpos:
        vivos = alcancaveis(corpo)
        cabeca = f"  {corpo.nome}"
        if corpo.parametros:
            cabeca += f"({', '.join(corpo.parametros)})"
        linhas.append(f"{cabeca}   {len(corpo.blocos)} bloco(s)"
                      + (f", {len(corpo.blocos) - len(vivos)} inalcancavel(is)"
                         if len(vivos) != len(corpo.blocos) else ""))
        for bloco in corpo.blocos:
            marca = " " if bloco.id in vivos else "×"
            rotulo = f" [{bloco.rotulo}]" if bloco.rotulo else ""
            arestas = ", ".join(
                f"{d}" + (f" ({r})" if r else "") for d, r in bloco.saidas)
            fim = f" → {arestas}" if arestas else \
                (f" ⏹ {bloco.terminador}" if bloco.terminador else "")
            linhas.append(f"   {marca} bloco {bloco.id}{rotulo}{fim}")
            if bloco.escreve:
                linhas.append(f"        liga: {', '.join(bloco.escreve)}")
            for instrucao in bloco.instrucoes:
                linhas.append(f"        {_uma_linha(instrucao)}")
        if com_analises:
            linhas.extend(_linhas_de_analise(corpo))
        linhas.append("")
    return "\n".join(linhas)


def _linhas_de_analise(corpo):
    linhas = []
    fora = sorted(set(b.id for b in corpo.blocos) - alcancaveis(corpo))
    linhas.append(f"        alcance: {len(alcancaveis(corpo))} de "
                  f"{len(corpo.blocos)}"
                  + (f" (fora: {fora})" if fora else ""))
    fixas = constantes(corpo)
    if fixas:
        linhas.append("        constantes: " +
                      ", ".join(f"{k}={v!r}" for k, v in sorted(fixas.items())))
    fugas = escapam(corpo)
    if fugas:
        linhas.append("        escapam: " +
                      ", ".join(f"{k} ({v})" for k, v in sorted(fugas.items())))
    duvidas = talvez_nao_definidas(corpo)
    if duvidas:
        linhas.append("        talvez nao definidas: " +
                      ", ".join(f"{n} (linha {getattr(i, 'line', 0)})"
                                for n, i in duvidas))
    return linhas


def _uma_linha(no):
    """Uma instrução em uma linha, sem a subárvore inteira."""
    if isinstance(no, _Marca):
        return f"{no.alvo.__class__.__name__} (aberto em linha)"
    nome = no.__class__.__name__
    detalhe = ""
    if isinstance(no, ast.Assignment) and isinstance(no.target, ast.Identifier):
        detalhe = f" {no.target.name} :="
    elif isinstance(no, ast.Identifier):
        detalhe = f" {no.name}"
    elif isinstance(no, (ast.IntegerLiteral, ast.FloatLiteral,
                         ast.StringLiteral)):
        detalhe = f" {no.value!r}"
    elif isinstance(no, (ast.ComparisonOp, ast.BinaryOp, ast.LogicalOp)):
        detalhe = f" {no.op}"
    elif isinstance(no, ast.FunctionCall) and isinstance(no.callee,
                                                         ast.Identifier):
        detalhe = f" {no.callee.name}()"
    elif isinstance(no, ast.MethodCall):
        detalhe = f" .{no.method}()"
    return f"linha {getattr(no, 'line', 0)}: {nome}{detalhe}"
