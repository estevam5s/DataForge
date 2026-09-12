"""
DataForge Static Analyzer (Type Checker)
=========================================

Runs between the parser and the interpreter. It walks the AST once and reports
problems that would otherwise only surface when that exact line executes:

  * names used before being defined
  * calls with the wrong number of arguments
  * type annotations contradicted by the value assigned
  * operations between incompatible types
  * fields and members that a record or enum does not have
  * unreachable code after 'yield', 'halt' or 'skip'
  * actions with a declared return type that can fall through without yielding
  * assignment to a 'steady' constant
  * imports of modules that do not exist

Design notes
------------
The checker is deliberately *optimistic*: when it cannot prove something is
wrong it stays quiet. DataForge is dynamically typed, so a false alarm is worse
than a missed one. Every diagnostic carries a line, a column and a suggested
fix.
"""

import os
import re

from . import ast_nodes as ast
from .caminhos import curto as _curto
from .tokens import KEYWORDS


# ── Tipos internos ─────────────────────────────────────────

ANY = "Any"
UNKNOWN = "?"

NUMERIC = {"Integer", "Float", "Number"}
ORDERABLE = NUMERIC | {"String"}

ALIASES = {
    "integer": "Integer", "int": "Integer", "Integer": "Integer",
    "float": "Float", "Float": "Float",
    "number": "Number", "Number": "Number",
    "string": "String", "str": "String", "text": "String", "String": "String",
    "boolean": "Boolean", "bool": "Boolean", "Boolean": "Boolean",
    "cluster": "Cluster", "list": "Cluster", "array": "Cluster", "Cluster": "Cluster",
    "vault": "Vault", "dict": "Vault", "map": "Vault", "Vault": "Vault",
    "void": "Void", "none": "Void", "Void": "Void",
    "action": "Action", "function": "Action", "Action": "Action",
    "stream": "Stream", "Stream": "Stream",
    "any": ANY, "Any": ANY,
}


def canonical(nome: str) -> str:
    return ALIASES.get(nome, nome)


def compatible(esperado: str, obtido: str) -> bool:
    """O valor de tipo 'obtido' serve onde se espera 'esperado'?"""
    if UNKNOWN in (esperado, obtido) or ANY in (esperado, obtido):
        return True
    if esperado == obtido:
        return True
    if esperado == "Number":
        return obtido in ("Integer", "Float", "Number")
    if esperado == "Float" and obtido == "Integer":
        return True          # um inteiro serve onde se espera decimal
    return False


class Diagnostic:
    """Um problema encontrado, com onde e como corrigir."""

    __slots__ = ('severity', 'message', 'line', 'column', 'hint', 'code')

    def __init__(self, severity, message, line, column, hint="", code=""):
        self.severity = severity          # 'error' | 'warning'
        self.message = message
        self.line = line
        self.column = column
        self.hint = hint
        self.code = code

    def format(self, filename="<stdin>", color=True):
        cores = {'error': '1;31', 'warning': '1;33'} if color else {}
        rotulo = 'erro' if self.severity == 'error' else 'aviso'
        if color:
            rotulo = f"\033[{cores[self.severity]}m{rotulo}\033[0m"
        cabecalho = f"{filename}:{self.line}:{self.column}: {rotulo}: {self.message}"
        if self.hint:
            cabecalho += f"\n    sugestão: {self.hint}"
        return cabecalho

    def __repr__(self):
        return f"<{self.severity} L{self.line}: {self.message}>"


class Scope:
    """Escopo léxico usado só na análise."""

    def __init__(self, parent=None, kind="block"):
        self.parent = parent
        self.kind = kind
        self.names = {}        # nome -> tipo
        self.constants = set()
        self.used = set()
        self.declared_at = {}  # nome -> (linha, coluna)

    def declare(self, nome, tipo=UNKNOWN, linha=0, coluna=0, constante=False):
        self.names[nome] = tipo
        self.declared_at[nome] = (linha, coluna)
        if constante:
            self.constants.add(nome)

    def lookup(self, nome):
        escopo = self
        while escopo is not None:
            if nome in escopo.names:
                escopo.used.add(nome)
                return escopo.names[nome]
            escopo = escopo.parent
        return None

    def is_constant(self, nome):
        escopo = self
        while escopo is not None:
            if nome in escopo.names:
                return nome in escopo.constants
            escopo = escopo.parent
        return False

    def has(self, nome):
        escopo = self
        while escopo is not None:
            if nome in escopo.names:
                return True
            escopo = escopo.parent
        return False


class ActionSignature:
    __slots__ = ('name', 'params', 'defaults', 'param_types', 'return_type',
                 'is_generator', 'line')

    def __init__(self, decl):
        self.name = decl.name
        self.params = list(decl.params)
        self.defaults = set(decl.defaults or {})
        self.param_types = dict(getattr(decl, 'param_types', {}) or {})
        self.return_type = canonical(getattr(decl, 'return_type', '') or UNKNOWN)
        self.is_generator = getattr(decl, 'is_generator', False)
        self.line = decl.line

    @property
    def required(self):
        return [p for p in self.params if p not in self.defaults]


class TypeChecker:
    """Percorre a AST reportando problemas antes da execução."""

    def __init__(self, filename="<stdin>", builtins=None, strict=False,
                 source=None):
        self.filename = filename
        self.strict = strict
        #: A fonte, quando quem chamou a tem — para ler os
        #: '// df: permitir <regra>'. Sem ela, o arquivo e lido do
        #: disco na primeira vez que se precisa; e sem arquivo (o REPL,
        #: uma string), nao ha comentario a ler e nada e silenciado.
        self._fonte = source
        self._silencio = None
        self.diagnostics = []
        self.global_scope = Scope(kind="global")
        self.actions = {}        # nome -> ActionSignature
        self.records = {}        # nome -> {campo: tipo}
        self.record_defaults = {}
        self.enums = {}          # nome -> [membros]
        self.blueprints = {}     # nome -> set(membros proprios)
        self.maes = {}           # nome -> [blueprints e traits de quem herda]
        #: Campos que alguem acrescentou DE FORA, com 'obj.x := …'.
        #: Quem faz isso perde a conferencia naquele nome, e e a escolha
        #: de quem escreveu — nao um erro a acusar. Guardar so o NOME, e
        #: nao o par (tipo, nome), perde um pouco de rigor e nao ganha
        #: nenhum falso alarme.
        self.campos_postos_de_fora = set()
        #: apelido do 'adopt' -> Superficie do modulo local.
        #:
        #: E o que torna possivel conferir chamada ENTRE arquivos. Num
        #: sistema de 200 modulos a maioria das chamadas e entre
        #: modulos, e todas elas eram invisiveis: 'P.naoExiste()' e
        #: 'P.criar(1, 2, 3)' so falhavam em execucao.
        self.superficies = {}
        #: Um ciclo e uma propriedade do ARQUIVO, nao de cada 'adopt'.
        #: Sem esta marca, um arquivo com cinco imports repetiria a
        #: mesma mensagem cinco vezes.
        self._ciclo_relatado = False
        self.known_types = set(ALIASES.values())
        # Os '<T>' do blueprint que esta sendo analisado. Um metodo dele
        # pode usa-los como tipo; fora dali, eles nao existem.
        self._genericos_do_blueprint = set()
        self._genericos_da_acao = set()
        self._action_depth = 0
        self._loop_depth = 0
        self._current_return = None
        self._demote = 0
        self._em_membro = False   # dentro de blueprint/record/enum/trait
        self._seed_builtins(builtins)

    # ── Infra ──────────────────────────────────────────────

    def _seed_builtins(self, builtins):
        if builtins is None:
            from .builtins import get_builtins
            builtins = get_builtins()
        for nome in builtins:
            self.global_scope.declare(nome, ANY)
        for extra in ("self", "this", "root", "__file__", "__name__", "error"):
            self.global_scope.declare(extra, ANY)

        # Os 177 nomes de erro sao valores: 'to_raise(KeyError)',
        # 'e.type is KeyError'. Sem isto o analisador acusa "nome nao
        # definido" em todo teste que nomeia o erro que espera.
        from .errors import ALIAS_DE_ERRO
        for nome in ALIAS_DE_ERRO:
            self.global_scope.declare(nome, "Error")

    def _demoted(self):
        """Contexto em que 'erro' vira 'aviso' (corpo de monitor/retry)."""
        verificador = self

        class _Contexto:
            def __enter__(self):
                verificador._demote += 1

            def __exit__(self, *_):
                verificador._demote -= 1
                return False

        return _Contexto()

    #: Nomes que capturam qualquer erro. A mesma lista do interpretador
    #: (Interpreter._CAPTURA_TUDO); se uma mudar, a outra precisa mudar.
    CAPTURA_TUDO = frozenset({"Error", "Exception", "Any", "DataForgeError"})

    def error(self, mensagem, node, hint="", code=""):
        severidade = 'warning' if self._demote else 'error'
        if severidade == 'warning':
            hint = (hint + " (inside a 'monitor' or 'expect', "
                    "so this is only a warning)").strip()
        self.diagnostics.append(Diagnostic(
            severidade, mensagem, getattr(node, 'line', 0),
            getattr(node, 'column', 0), hint, code))

    def warn(self, mensagem, node, hint="", code=""):
        self.diagnostics.append(Diagnostic(
            'warning', mensagem, getattr(node, 'line', 0),
            getattr(node, 'column', 0), hint, code))

    @property
    def errors(self):
        return [d for d in self.diagnostics if d.severity == 'error']

    @property
    def warnings(self):
        return [d for d in self.diagnostics if d.severity == 'warning']

    def _similar(self, nome, candidatos):
        """Sugere o nome existente mais parecido (distância de edição curta)."""
        import difflib
        proximos = difflib.get_close_matches(nome, [c for c in candidatos], n=1, cutoff=0.75)
        return proximos[0] if proximos else ""

    def _visible_names(self, escopo):
        nomes = set()
        atual = escopo
        while atual is not None:
            nomes.update(atual.names)
            atual = atual.parent
        return nomes

    # ── Entrada ────────────────────────────────────────────

    def check(self, program):
        escopo = self.global_scope
        self._hoist(program.body, escopo)
        # Antes de conferir qualquer acesso: a escrita pode estar DEPOIS
        # da leitura no arquivo.
        self._recolher_campos_externos(program, escopo)
        self.visit_block(program.body, escopo)
        return self._sem_os_silenciados(program)

    # ── silenciar uma linha, de propósito ────────────────────

    #: `// df: permitir <regra>` silencia aquela regra naquela linha.
    #:
    #: Um analisador sem escape obriga quem escreve a escolher entre
    #: conviver com um alarme falso e desligar a verificação inteira —
    #: e a segunda é o que acontece.
    #:
    #: O caso que provou a necessidade está no repositório: o exercício
    #: 139 **demonstra** a armadilha de um `point` inalcançável, com um
    #: `assert` provando o comportamento. O analisador estava certo, e o
    #: exercício também.
    #:
    #: A regra tem de ser NOMEADA. Um `permitir` solto que silenciasse
    #: tudo naquela linha esconderia o erro seguinte, que ninguém pediu
    #: para esconder.
    _SILENCIO = re.compile(r"//\s*df:\s*permitir\s+([a-z0-9\-, ]+)")

    def _ler_fonte(self):
        if self._fonte is not None:
            return self._fonte
        self._fonte = ""
        nome = self.filename or ""
        if nome and not nome.startswith("<") and os.path.isfile(nome):
            try:
                with open(nome, encoding="utf-8") as f:
                    self._fonte = f.read()
            except OSError:
                pass
        return self._fonte

    def _silenciados_por_linha(self):
        """`{linha: {regra, …}}`, lido da FONTE.

        Do texto, e não dos tokens: o lexer descarta comentário, e
        guardá-lo na árvore só para isto encareceria toda compilação.
        """
        if self._silencio is not None:
            return self._silencio
        self._silencio = {}
        fonte = self._ler_fonte()
        for numero, linha in enumerate(fonte.split("\n"), 1):
            achado = self._SILENCIO.search(linha)
            if achado:
                regras = {r.strip() for r in achado.group(1).replace(",", " ").split()}
                self._silencio[numero] = {r for r in regras if r}
        return self._silencio

    def _sem_os_silenciados(self, program):
        mapa = self._silenciados_por_linha()
        if not mapa:
            return self.diagnostics
        sobrou = []
        for d in self.diagnostics:
            # A própria linha, ou a de cima: um `match` longo põe o
            # comentário acima do `point`, onde ele cabe.
            regras = mapa.get(d.line, set()) | mapa.get(d.line - 1, set())
            if d.code and d.code in regras:
                continue
            sobrou.append(d)
        return sobrou

    def _hoist(self, statements, escopo, registrar_acoes=True):
        """Declara ações, records, enums e blueprints antes de visitar o corpo,
        para que a ordem de definição no arquivo não importe.

        'registrar_acoes' fica falso dentro de um blueprint/record/enum: um
        método chamado 'descrever' não deve ser confundido com uma ação global
        de mesmo nome na hora de verificar aridade.
        """
        for stmt in statements:
            if isinstance(stmt, ast.ActionDeclaration):
                if registrar_acoes:
                    self.actions[stmt.name] = ActionSignature(stmt)
                escopo.declare(stmt.name, "Action", stmt.line, stmt.column)
            elif isinstance(stmt, ast.RecordDeclaration):
                self.records[stmt.name] = {c: canonical(t) for c, t, _ in stmt.fields}
                self.record_defaults[stmt.name] = {c for c, _, d in stmt.fields if d is not None}
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Record", stmt.line, stmt.column)
            elif isinstance(stmt, ast.EnumDeclaration):
                self.enums[stmt.name] = [m for m, _ in stmt.members]
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Enum", stmt.line, stmt.column)
            elif isinstance(stmt, (ast.BlueprintDeclaration, ast.TraitDeclaration)):
                self.blueprints[stmt.name] = self._membros_de(stmt)
                if isinstance(stmt, ast.BlueprintDeclaration):
                    self.maes[stmt.name] = [
                        p if isinstance(p, str) else getattr(p, "name", "")
                        for p in (list(stmt.parents or [])
                                  + list(stmt.traits or []))]
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Blueprint", stmt.line, stmt.column)

    # ── O que um blueprint tem ─────────────────────────────
    #
    #  Isto existia pela metade: só ações, estáticos e parâmetros do
    #  construtor. Faltavam os campos declarados, as propriedades, e —
    #  o mais comum de todos — o campo que nasce de um 'self.x := …'
    #  dentro de um método.
    #
    #  Faltava sobretudo alguém CONSULTAR. Com a lista incompleta,
    #  conferir teria dado falso alarme em código correto, e um falso
    #  alarme ensina a ignorar a ferramenta.

    @staticmethod
    def _membros_de(stmt):
        """Tudo o que se pode escrever depois do ponto, neste blueprint.

        Não inclui o que vem da mãe: isso é resolvido em
        '_membros_com_heranca', que precisa da tabela inteira montada.
        """
        membros = set()
        corpo = (stmt.body if isinstance(stmt, ast.BlueprintDeclaration)
                 else stmt.methods)

        for sub in corpo:
            if isinstance(sub, (ast.ActionDeclaration, ast.StaticDeclaration,
                                ast.PropertyDeclaration)):
                membros.add(sub.name)

        if isinstance(stmt, ast.BlueprintDeclaration):
            membros.update(stmt.constructor_params or [])
            for campo in (stmt.fields_decl or []):
                nome = campo[0] if isinstance(campo, (tuple, list)) \
                    else getattr(campo, "name", None)
                if nome:
                    membros.add(nome)

            # 'self.x := …' declara um campo, e ele aparece em dois
            # lugares: dentro de um método, e SOLTO no corpo do
            # blueprint — que é o construtor inline. Varrer o corpo
            # inteiro cobre os dois de uma vez.
            #
            # Olhar só dentro dos métodos deu 32 falsos alarmes num
            # exemplo que funciona há meses.
            membros |= TypeChecker._campos_atribuidos(corpo)

        return membros

    @staticmethod
    def _campos_atribuidos(no):
        """Os nomes de todo 'self.x := …' abaixo deste nó."""
        achados = set()
        pilha = [no]
        while pilha:
            atual = pilha.pop()
            if isinstance(atual, ast.Assignment):
                alvo = atual.target
                if (isinstance(alvo, ast.MemberAccess)
                        and isinstance(alvo.object, ast.Identifier)
                        and alvo.object.name in ("self", "this")):
                    achados.add(alvo.member)
            if isinstance(atual, ast.ASTNode):
                for campo, valor in vars(atual).items():
                    if not campo.startswith("_"):
                        pilha.append(valor)
            elif isinstance(atual, (list, tuple)):
                pilha.extend(atual)
            elif isinstance(atual, dict):
                pilha.extend(atual.values())
        return achados

    def _recolher_campos_externos(self, programa, escopo):
        """'obj.x := …' fora do blueprint acrescenta o campo em execução.

        Quem escreve assim abre mão da conferência **naquele campo** —
        é a escolha dele, e não um erro a acusar. O que não dá é acusar
        a LEITURA e deixar a escrita passar: seria reclamar de ler o que
        o próprio arquivo escreveu duas linhas acima.

        Roda antes de conferir qualquer acesso, porque a escrita pode
        estar depois da leitura no arquivo.
        """
        pilha = [programa]
        while pilha:
            atual = pilha.pop()
            if isinstance(atual, ast.Assignment):
                alvo = atual.target
                if (isinstance(alvo, ast.MemberAccess)
                        and isinstance(alvo.object, ast.Identifier)
                        and alvo.object.name not in ("self", "this")):
                    # O NOME do campo basta, e o tipo da variavel nao
                    # esta resolvido nesta passagem. A consequencia e
                    # que um campo posto de fora num tipo desliga a
                    # conferencia daquele nome em todos — e essa e a
                    # troca certa: perde-se um pouco de rigor e nao se
                    # ganha um unico falso alarme.
                    self.campos_postos_de_fora.add(alvo.member)
            if isinstance(atual, ast.ASTNode):
                for campo, valor in vars(atual).items():
                    if not campo.startswith("_"):
                        pilha.append(valor)
            elif isinstance(atual, (list, tuple)):
                pilha.extend(atual)
            elif isinstance(atual, dict):
                pilha.extend(atual.values())

    def _membros_com_heranca(self, nome, vistos=None):
        """Os membros do blueprint MAIS os de toda a linhagem.

        Um método herdado é tão legítimo quanto um declarado aqui, e
        acusar 'Filha' de não ter o que 'Base' tem seria o falso alarme
        mais óbvio possível.

        'vistos' corta ciclo de herança: ele é erro em outro lugar, e
        aqui não pode virar recursão infinita.
        """
        vistos = vistos or set()
        if nome in vistos or nome not in self.blueprints:
            return set()
        vistos.add(nome)

        membros = set(self.blueprints[nome])
        for mae in self.maes.get(nome, ()):
            membros |= self._membros_com_heranca(mae, vistos)
        return membros

    def _blueprint_e_fechado(self, nome, vistos=None):
        """Dá para afirmar que este blueprint não ganha membro em tempo de execução?

        Não dá quando ele — ou alguém na linhagem — herda de algo que o
        analisador não viu: um blueprint de outro arquivo, ou um valor
        vindo de um módulo. Nesses casos o silêncio é a resposta certa.
        """
        vistos = vistos or set()
        if nome in vistos:
            return True                     # ciclo: outro erro cuida
        vistos.add(nome)

        for mae in self.maes.get(nome, ()):
            if mae not in self.blueprints:
                return False
            if not self._blueprint_e_fechado(mae, vistos):
                return False
        return True

    # ── Instruções ─────────────────────────────────────────

    def visit_block(self, statements, escopo):
        terminou = False
        for stmt in statements:
            if terminou and not isinstance(stmt, (ast.ActionDeclaration,
                                                  ast.BlueprintDeclaration,
                                                  ast.RecordDeclaration,
                                                  ast.EnumDeclaration)):
                self.warn(
                    "Unreachable code: the block already ended above",
                    stmt,
                    "Remove this line or move it before the 'yield'/'halt'/'skip'",
                    "unreachable")
                terminou = True
                continue
            if self.visit(stmt, escopo):
                terminou = True
        return terminou

    def visit(self, node, escopo):
        """Visita uma instrução. Devolve True se ela encerra o fluxo do bloco."""
        if node is None:
            return False
        metodo = getattr(self, f"st_{type(node).__name__}", None)
        if metodo:
            return metodo(node, escopo)
        # Expressão em posição de instrução
        self.infer(node, escopo)
        return False

    def st_Assignment(self, node, escopo):
        tipo = self.infer(node.value, escopo)
        declarado = canonical(getattr(node, 'declared_type', '') or '')

        if declarado:
            if declarado not in self.known_types and declarado != UNKNOWN:
                self.error(
                    f"Unknown type '{node.declared_type}'", node,
                    self._hint_tipo(node.declared_type), "unknown-type")
            elif not compatible(declarado, tipo):
                self.error(
                    f"Declared as {declarado} but the value is {tipo}", node,
                    f"Change the annotation to {tipo} or fix the value",
                    "type-mismatch")

        if isinstance(node.target, ast.Identifier):
            nome = node.target.name
            if escopo.is_constant(nome):
                self.error(
                    f"Cannot reassign the steady constant '{nome}'", node,
                    "Use another name, or drop 'steady' from the declaration",
                    "steady-reassign")
                return False
            escopo.declare(nome, declarado or tipo, node.line, node.column)
        else:
            self.infer(node.target, escopo)
        return False

    def st_DestructuringAssignment(self, node, escopo):
        self.infer(node.value, escopo)
        for nome, _ in node.targets:
            escopo.declare(nome, UNKNOWN, node.line, node.column)
        return False

    def st_SteadyDeclaration(self, node, escopo):
        tipo = self.infer(node.value, escopo)
        if escopo.has(node.name) and escopo.is_constant(node.name):
            self.error(f"Constant '{node.name}' is already defined", node,
                       "Pick another name", "steady-redeclare")
        escopo.declare(node.name, tipo, node.line, node.column, constante=True)
        return False

    def st_ShadowDeclaration(self, node, escopo):
        escopo.declare(node.name, self.infer(node.value, escopo), node.line, node.column)
        return False

    def st_StaticDeclaration(self, node, escopo):
        escopo.declare(node.name, self.infer(node.value, escopo), node.line, node.column)
        return False

    def st_OutStatement(self, node, escopo):
        for e in node.expressions:
            self.infer(e, escopo)
        return False

    st_EmitStatement = st_OutStatement

    def _genericos_em_escopo(self):
        """Os '<T>' que valem aqui: os da acao mais os do blueprint."""
        return self._genericos_da_acao | self._genericos_do_blueprint

    def st_YieldStatement(self, node, escopo):
        tipo = self.infer(node.value, escopo) if node.value else "Void"
        if self._action_depth == 0:
            self.error("'yield' outside of an action", node,
                       "'yield' returns from an action; use 'out' to print",
                       "yield-outside-action")
        elif (self._current_return
              and self._current_return not in (UNKNOWN, ANY)
              and self._current_return not in self._genericos_em_escopo()):
            if not compatible(self._current_return, tipo):
                self.error(
                    f"Action declares '-> {self._current_return}' but yields {tipo}",
                    node,
                    f"Return a {self._current_return} or change the declared type",
                    "return-mismatch")
        return True

    def st_HaltStatement(self, node, escopo):
        if self._loop_depth == 0:
            self.error("'halt' outside of a loop", node,
                       "'halt' breaks out of cycle/persist/perform", "halt-outside-loop")
        return True

    def st_SkipStatement(self, node, escopo):
        if self._loop_depth == 0:
            self.error("'skip' outside of a loop", node,
                       "'skip' jumps to the next iteration", "skip-outside-loop")
        return True

    def st_TriggerStatement(self, node, escopo):
        self.infer(node.value, escopo)
        return True

    def st_PropagateStatement(self, node, escopo):
        if node.value:
            self.infer(node.value, escopo)
        return True

    def st_GivenBlock(self, node, escopo):
        self.infer(node.condition, escopo)
        ramos = [self.visit_block(node.body, escopo.__class__(escopo))]
        for cond, corpo in node.orif_blocks:
            self.infer(cond, escopo)
            ramos.append(self.visit_block(corpo, Scope(escopo)))
        if node.otherwise_body:
            ramos.append(self.visit_block(node.otherwise_body, Scope(escopo)))
            return all(ramos)
        return False

    def st_MatchBlock(self, node, escopo):
        self.infer(node.expression, escopo)
        ramos = []
        for caso in node.points:
            if isinstance(caso, tuple):
                alvo, corpo = caso
                self.infer(alvo, escopo)
                ramos.append(self.visit_block(corpo, Scope(escopo)))
                continue
            interno = Scope(escopo)
            self._declare_pattern(caso.pattern, interno)
            if caso.guard is not None:
                self.infer(caso.guard, interno)
            ramos.append(self.visit_block(caso.body, interno))
        if node.default_body:
            ramos.append(self.visit_block(node.default_body, Scope(escopo)))
            self._conferir_exaustividade(node, escopo)
            self._conferir_ordem_dos_pontos(node)
            return bool(ramos) and all(ramos)
        self._conferir_exaustividade(node, escopo)
        self._conferir_ordem_dos_pontos(node)
        return False

    def _conferir_ordem_dos_pontos(self, node):
        """Um 'point' que vem DEPOIS de uma captura nunca casa.

        `match` decide do primeiro ao ultimo, e uma captura solta
        (`point n:`) casa com tudo. O que vem abaixo dela e codigo morto
        — e morto em silencio: o programa compila, roda e devolve o
        ramo errado.

            match x:
                point n:                  <- casa com tudo
                    yield "qualquer"
                point Integer:            <- nunca
                    yield "inteiro"

        Isto e a armadilha 10 da linguagem, e era a unica documentada
        como armadilha que o analisador nao pegava. Um 'default' no fim
        e diferente: ele e a captura ESCRITA como tal, e o parser nao
        deixa pôr nada depois.

        A guarda salva o caso legitimo: `point n when n bigger 100:`
        casa com tudo *se a condicao valer*, e o que vem abaixo continua
        alcancavel.
        """
        capturou = None
        for caso in node.points:
            if isinstance(caso, tuple):
                # Forma antiga (alvo, corpo): sem padrao estruturado
                # para inspecionar. Calar.
                return
            if capturou is not None:
                self.error(
                    "este 'point' nunca casa: a captura acima dele casa "
                    "com tudo",
                    caso,
                    f"a captura esta na linha {capturou}; mova-a para o "
                    f"fim, ou troque-a por 'default:'",
                    "point-inalcancavel")
                return          # um aviso basta: os outros sao o mesmo
            if self._casa_com_tudo(caso):
                capturou = getattr(caso, "line", 0)

    @staticmethod
    def _casa_com_tudo(caso):
        """`point n:` sem guarda — o unico padrao que casa sempre.

        Com guarda, nao: `point n when n bigger 100:` deixa passar o que
        nao satisfaz a condicao.
        """
        if getattr(caso, "guard", None) is not None:
            return False
        padrao = getattr(caso, "pattern", None)
        return isinstance(padrao, ast.CapturePattern)

    def _conferir_exaustividade(self, node, escopo):
        """Um 'match' sobre enum que deixou membro de fora.

        Sem isto, esquecer um membro devolve 'void' em silencio — e
        'void' costuma atravessar meia dezena de chamadas antes de
        virar erro em outro lugar, longe da causa.

        So fala quando consegue PROVAR: e preciso saber de que enum se
        trata, e todo 'point' precisa ser um membro dele. Um 'default'
        ou uma captura solta cobrem o resto, e ai nao ha o que dizer.
        """
        if getattr(node, "default_body", None):
            return

        membros_vistos = []
        enums = set()
        for caso in node.points:
            padrao = caso[0] if isinstance(caso, tuple) else caso.pattern
            dono, membro = self._membro_de_enum(padrao)
            if dono is None:
                # Um padrao que nao e membro de enum — captura, tipo,
                # sequencia. Nao da para concluir nada.
                return
            enums.add(dono)
            membros_vistos.append(membro)

        # Um match sobre DOIS enums diferentes nao e um match sobre um
        # enum: e outra coisa, e nao cabe cobrar exaustividade.
        if len(enums) != 1:
            return
        nome_enum = enums.pop()
        todos = self.enums.get(nome_enum)
        if not todos:
            return

        faltando = [m for m in todos if m not in membros_vistos]
        if not faltando:
            return

        lista = ", ".join(f"{nome_enum}.{m}" for m in faltando)
        # Um aviso por membro viraria ruido num enum de dez.
        self.warn(
            f"'match' não cobre {len(faltando)} membro(s) de "
            f"'{nome_enum}': {lista}",
            node,
            "Trate cada um, ou acrescente 'default:' para o resto",
            "match-incompleto")

    def _membro_de_enum(self, padrao):
        """('Cor', 'Azul') se o padrao for 'point Cor.Azul'; senao (None, None).

        Uma captura com nome ('point Cor.Azul as c') continua sendo o
        membro: o 'as' liga um nome, nao muda o que casa.
        """
        expressao = getattr(padrao, "expression", None)
        if expressao is None:
            return None, None
        if not isinstance(expressao, ast.MemberAccess):
            return None, None
        objeto = getattr(expressao, "object", None)
        if not isinstance(objeto, ast.Identifier):
            return None, None
        if objeto.name not in self.enums:
            return None, None
        return objeto.name, expressao.member

    def _declare_pattern(self, padrao, escopo):
        if padrao is None:
            return
        if getattr(padrao, 'binding', ''):
            escopo.declare(padrao.binding, UNKNOWN, padrao.line, padrao.column)
        if isinstance(padrao, ast.CapturePattern):
            escopo.declare(padrao.name, UNKNOWN, padrao.line, padrao.column)
        elif isinstance(padrao, ast.SequencePattern):
            for sub in padrao.elements:
                self._declare_pattern(sub, escopo)
            if padrao.rest_name:
                escopo.declare(padrao.rest_name, "Cluster", padrao.line, padrao.column)
        elif isinstance(padrao, ast.MappingPattern):
            for _, sub in padrao.pairs:
                self._declare_pattern(sub, escopo)
            if padrao.rest_name:
                escopo.declare(padrao.rest_name, "Vault", padrao.line, padrao.column)
        elif isinstance(padrao, ast.TypePattern):
            if (padrao.type_name not in self.known_types
                    and padrao.type_name not in ALIASES):
                self.warn(
                    f"Unknown type '{padrao.type_name}' in the pattern", padrao,
                    self._hint_tipo(padrao.type_name), "unknown-type")
            for sub in padrao.sub_patterns:
                self._declare_pattern(sub, escopo)
            for sub in padrao.field_patterns.values():
                self._declare_pattern(sub, escopo)
        elif isinstance(padrao, ast.OrPattern):
            for opcao in padrao.options:
                self._declare_pattern(opcao, escopo)

    def st_CycleFromTo(self, node, escopo):
        for parte in (node.start, node.end, node.step):
            if parte is not None:
                tipo = self.infer(parte, escopo)
                if tipo not in (UNKNOWN, ANY) and tipo not in NUMERIC:
                    self.error(
                        f"'cycle from/to' needs numbers, got {tipo}", parte,
                        "Use integers in the range bounds", "cycle-range-type")
        interno = Scope(escopo, "loop")
        interno.declare(node.var, "Integer", node.line, node.column)
        self._loop_depth += 1
        try:
            self.visit_block(node.body, interno)
        finally:
            self._loop_depth -= 1
        return False

    def st_CycleIn(self, node, escopo):
        tipo = self.infer(node.collection, escopo)
        if tipo in ("Integer", "Float", "Boolean", "Void"):
            self.error(
                f"Cannot cycle over {tipo}", node.collection,
                "Use a Cluster, a Vault, a String or a Stream", "cycle-not-iterable")
        interno = Scope(escopo, "loop")
        for nome in (getattr(node, "vars", None) or [node.var]):
            interno.declare(nome, UNKNOWN, node.line, node.column)
        self._loop_depth += 1
        try:
            self.visit_block(node.body, interno)
        finally:
            self._loop_depth -= 1
        return False

    def st_PersistBlock(self, node, escopo):
        self.infer(node.condition, escopo)
        self._loop_depth += 1
        try:
            self.visit_block(node.body, Scope(escopo, "loop"))
        finally:
            self._loop_depth -= 1
        return False

    def st_PerformBlock(self, node, escopo):
        self._loop_depth += 1
        try:
            self.visit_block(node.body, Scope(escopo, "loop"))
        finally:
            self._loop_depth -= 1
        self.infer(node.condition, escopo)
        return False

    def st_ObserveBlock(self, node, escopo):
        self.infer(node.source, escopo)
        interno = Scope(escopo, "loop")
        interno.declare(node.var, UNKNOWN, node.line, node.column)
        self._loop_depth += 1
        try:
            self.visit_block(node.body, interno)
        finally:
            self._loop_depth -= 1
        return False

    def st_WithBlock(self, node, escopo):
        self.infer(node.resource, escopo)
        # O corpo usa o escopo de FORA, como o do monitor: uma variavel
        # atribuida dentro continua existindo depois. So o nome do
        # recurso e local.
        if node.name:
            escopo.declare(node.name, UNKNOWN, node.line, node.column)
        self.visit_block(node.body, escopo)
        return False

    def st_MonitorBlock(self, node, escopo):
        # O corpo de um 'monitor' existe para conter falhas; codigo que provoca
        # um erro de proposito e legitimo ali. Por isso os diagnosticos do corpo
        # sao rebaixados a aviso.
        #
        # O corpo usa o escopo de FORA, como o interpretador: uma variavel
        # atribuida dentro do monitor continua existindo depois dele.
        with self._demoted():
            self.visit_block(node.body, escopo)
        pega_tudo = False
        for clausula in node.handles:
            # Um 'handle' sem tipo — ou com 'Error' — captura qualquer
            # coisa, e torna inalcancavel todo 'handle' abaixo dele. E a
            # mesma armadilha da ordem dos 'point' num match, e vira
            # aviso pelo mesmo motivo que codigo inalcancavel: o
            # programa roda, so tem um bloco que nunca executa.
            if pega_tudo:
                self.warn(
                    "Unreachable 'handle': the one above catches every error",
                    clausula,
                    "Put the specific error types first and the catch-all last",
                    "unreachable")
            if not clausula.error_type or clausula.error_type in self.CAPTURA_TUDO:
                pega_tudo = True
            # o nome do erro existe so aqui; o resto compartilha o escopo
            escopo.declare(clausula.error_name, "Error",
                           clausula.line, clausula.column)
            self.visit_block(clausula.body, escopo)
        if node.ensure_body:
            self.visit_block(node.ensure_body, Scope(escopo))
        return False

    def st_RetryBlock(self, node, escopo):
        self.infer(node.count, escopo)
        # mesma regra do monitor: o corpo nao cria escopo proprio
        with self._demoted():
            self.visit_block(node.body, escopo)
        if node.handle_body:
            escopo.declare(node.handle_name, "Error", node.line, node.column)
            self.visit_block(node.handle_body, escopo)
        return False

    def st_GuardStatement(self, node, escopo):
        self.infer(node.condition, escopo)
        if node.message is not None:
            self.infer(node.message, escopo)
        if node.else_body:
            self.visit_block(node.else_body, Scope(escopo))
        return False

    def st_ValidateStatement(self, node, escopo):
        self.infer(node.value, escopo)
        if node.message is not None:
            self.infer(node.message, escopo)
        if node.else_body:
            self.visit_block(node.else_body, Scope(escopo))
        return False

    def st_AssertStatement(self, node, escopo):
        self.infer(node.condition, escopo)
        if node.message is not None:
            self.infer(node.message, escopo)
        return False

    def st_DeferStatement(self, node, escopo):
        self.visit_block(node.body, Scope(escopo))
        return False

    def st_ThreadBlock(self, node, escopo):
        self._avisar_escrita_compartilhada(node.body, escopo, "thread")
        self.visit_block(node.body, Scope(escopo))
        return False

    def st_ParallelBlock(self, node, escopo):
        self._avisar_escrita_compartilhada(node.blocks, escopo, "parallel")
        self.visit_block(node.blocks, Scope(escopo))
        return False

    #: O que uma escrita concorrente perde, em silencio.
    #:
    #: Quatro threads somando 20 mil vezes na mesma variavel entregaram
    #: 40.425 de 80.000 — metade, e sem nada denunciando. 'x := x + 1'
    #: sao tres passos (ler, somar, escrever), e o interpretador pode
    #: trocar de thread entre eles.
    #:
    #: A linguagem tem a resposta ('Arcane.Concurrent': mutex, contador
    #: atomico, canal) e nao a aplicava sozinha — nem AVISAVA. O bug mais
    #: caro que ela permite era o unico que nem o 'check' nem o 'lint'
    #: mencionavam.
    #:
    #: E um AVISO, e nao erro: escrever de duas threads e legitimo
    #: quando quem escreve sabe — um acumulador protegido por mutex
    #: passa por aqui igual, e recusa-lo seria proibir o uso correto.
    _CODIGO_CORRIDA = "escrita-concorrente"

    def _avisar_escrita_compartilhada(self, corpo, escopo, palavra):
        """Nomes de FORA que o corpo concorrente escreve."""
        escritos = {}
        self._colher_escritas(corpo, escritos)
        if not escritos:
            return

        for nome, no in sorted(escritos.items(), key=lambda p: p[1].line):
            # Declarado dentro do bloco: cada thread tem o seu, e nao ha
            # corrida. So o que vem de fora e compartilhado.
            if not escopo.has(nome):
                continue
            self.warn(
                f"'{nome}' e escrito dentro de '{palavra}' e vem de fora: "
                f"duas threads podem perder atualizacoes",
                no,
                "a linguagem nao sincroniza sozinha — use "
                "'Arcane.Concurrent': 'contador()' para somar, 'mutex()' "
                "para um bloco, ou 'canal()' para passar o valor adiante",
                self._CODIGO_CORRIDA)

    def _colher_escritas(self, no, saida):
        """Os nomes que este no atribui, em qualquer profundidade.

        Desce em tudo: um 'given' dentro de um 'cycle' dentro de uma
        acao chamada pelo bloco nao e alcancado — a analise para na
        fronteira da acao, porque seguir chamada exigiria um grafo, e um
        aviso que depende disso seria impreciso nos dois sentidos.
        """
        if no is None:
            return
        if isinstance(no, (list, tuple)):
            for item in no:
                self._colher_escritas(item, saida)
            return
        if not isinstance(no, ast.ASTNode):
            return

        # Uma acao declarada dentro do bloco: o corpo dela roda quando
        # alguem a chama, e nao aqui.
        if isinstance(no, (ast.ActionDeclaration, ast.BlueprintDeclaration,
                           ast.RecordDeclaration)):
            return

        if isinstance(no, ast.Assignment):
            nome = None
            alvo = getattr(no, "target", None)
            if isinstance(alvo, str):
                nome = alvo
            elif isinstance(alvo, ast.Identifier):
                nome = alvo.name
            elif isinstance(alvo, ast.IndexAccess):
                # 'v["n"] := …' — a escrita e no VAULT, e o vault vem de
                # fora. E a forma mais comum do bug, porque parece que
                # so o campo muda.
                base = alvo
                while isinstance(base, (ast.IndexAccess, ast.MemberAccess)):
                    base = getattr(base, "object", None)
                if isinstance(base, ast.Identifier):
                    nome = base.name
            elif isinstance(alvo, ast.MemberAccess):
                base = getattr(alvo, "object", None)
                if isinstance(base, ast.Identifier):
                    nome = base.name
            if nome and nome not in ("self", "this", "root"):
                saida.setdefault(nome, no)

        for campo in getattr(no, "__dataclass_fields__", {}):
            if campo in ("line", "column"):
                continue
            self._colher_escritas(getattr(no, campo, None), saida)

    def st_ChannelDeclaration(self, node, escopo):
        escopo.declare(node.name, "Channel", node.line, node.column)
        return False

    # ── Kiln ───────────────────────────────────────────────

    # ── Crucible ───────────────────────────────────────────

    def st_CrucibleBlock(self, node, escopo):
        """A suite ve o escopo de fora; o que ela declara nao vaza."""
        self.infer(node.name, escopo)
        for t in node.tags:
            self.infer(t, escopo)
        if node.pending is not None:
            self.infer(node.pending, escopo)
        self.visit_block(node.body, Scope(escopo, "crucible"))
        return False

    def st_TrialBlock(self, node, escopo):
        self.infer(node.name, escopo)
        for t in node.tags:
            self.infer(t, escopo)
        for campo in (node.pending, node.repeat, node.within, node.over):
            if campo is not None:
                self.infer(campo, escopo)
        interno = Scope(escopo, "action")
        # 'caso' existe quando o trial percorre uma tabela ('over'), e
        # so entao. Declarar sempre produziria "nao usado" em todo
        # trial comum; nao declarar nunca acusaria "nao definido" nos
        # parametrizados. Por isso a condicao.
        if node.over is not None:
            interno.declare("caso", UNKNOWN, node.line, node.column)
        self.visit_block(node.body, interno)
        return False

    def st_HookBlock(self, node, escopo):
        # O gancho declara no escopo da SUITE, nao num filho: e assim
        # que 'setup' entrega valores aos trials.
        self.visit_block(node.body, escopo)
        return False

    def st_FixtureBlock(self, node, escopo):
        escopo.declare(node.name, "Action", node.line, node.column)
        interno = Scope(escopo, "action")
        for p in node.params:
            interno.declare(p, UNKNOWN, node.line, node.column)
        self.visit_block(node.body, interno)
        return False

    def st_ProvideStatement(self, node, escopo):
        if node.value is not None:
            self.infer(node.value, escopo)
        # 'provide' divide a fixture, nao a encerra: o que vem depois e
        # a limpeza, e precisa ser analisado.
        return False

    def st_ExpectStatement(self, node, escopo):
        # Um 'expect' existe para provocar: 'expect(lambda => 1 / 0)
        # .to_raise(...)' e o jeito certo de testar a divisao por zero,
        # e acusar erro ali ensina a ignorar o analisador. Mesma regra
        # do corpo de 'monitor'.
        with self._demoted():
            self.infer(node.value, escopo)
            for a in node.args:
                self.infer(a, escopo)
        return False

    def st_BenchBlock(self, node, escopo):
        self.infer(node.name, escopo)
        if node.times is not None:
            self.infer(node.times, escopo)
        self.visit_block(node.body, Scope(escopo, "action"))
        return False

    def st_ServerBlock(self, node, escopo):
        """O nome do server passa a existir no escopo de fora."""
        escopo.declare(node.name, "Server", node.line, node.column)
        if node.port is not None:
            self.infer(node.port, escopo)
        if node.host is not None:
            self.infer(node.host, escopo)
        self.visit_block(node.body, Scope(escopo, "server"))
        return False

    def st_RouteBlock(self, node, escopo):
        self.infer(node.path, escopo)
        interno = Scope(escopo, "action")
        # O corpo da rota recebe estes seis prontos.
        for nome, tipo in (("req", "Vault"), ("params", "Vault"),
                           ("query", "Vault"), ("body", UNKNOWN),
                           ("headers", "Vault"), ("session", "Vault")):
            interno.declare(nome, tipo, node.line, node.column)
        self.visit_block(node.body, interno)
        return False

    def st_RespondStatement(self, node, escopo):
        if node.value is not None:
            self.infer(node.value, escopo)
        if node.status is not None:
            self.infer(node.status, escopo)
        # 'respond' encerra a rota, como 'yield' encerra uma acao:
        # marcar isso evita "codigo inalcancavel" falso logo abaixo.
        return True

    def st_RenderStatement(self, node, escopo):
        self.infer(node.template, escopo)
        if node.data is not None:
            self.infer(node.data, escopo)
        if node.status is not None:
            self.infer(node.status, escopo)
        return True

    def st_RedirectStatement(self, node, escopo):
        self.infer(node.target, escopo)
        if node.status is not None:
            self.infer(node.status, escopo)
        return True

    def st_MiddlewareStatement(self, node, escopo):
        self.infer(node.value, escopo)
        return False

    def st_MountStatement(self, node, escopo):
        self.infer(node.value, escopo)
        self.infer(node.prefix, escopo)
        return False

    def st_AssetsStatement(self, node, escopo):
        self.infer(node.prefix, escopo)
        self.infer(node.folder, escopo)
        return False

    def st_ViewsStatement(self, node, escopo):
        self.infer(node.folder, escopo)
        return False

    def st_IgniteStatement(self, node, escopo):
        self.infer(node.target, escopo)
        if node.port is not None:
            self.infer(node.port, escopo)
        if node.host is not None:
            self.infer(node.host, escopo)
        return False

    def st_ActionDeclaration(self, node, escopo):
        assinatura = ActionSignature(node)
        if not self._em_membro:
            self.actions.setdefault(node.name, assinatura)
        escopo.declare(node.name, "Action", node.line, node.column)

        interno = Scope(escopo, "action")
        for param in node.params:
            interno.declare(param, canonical(assinatura.param_types.get(param, UNKNOWN)),
                            node.line, node.column)

        # Os parametros de tipo ('<T>') valem como nome de tipo dentro
        # desta acao — e so dentro dela. Sem isto, 'action primeiro<T>(l)
        # -> T' acusaria "tipo T desconhecido", que e o oposto do que a
        # declaracao acabou de dizer.
        genericos = set(getattr(node, "type_params", None) or [])
        genericos |= self._genericos_do_blueprint

        for tipo in assinatura.param_types.values():
            alvo = canonical(tipo)
            if (alvo not in self.known_types and alvo != UNKNOWN
                    and tipo not in genericos):
                self.error(f"Unknown parameter type '{tipo}'", node,
                           self._hint_tipo(tipo), "unknown-type")

        retorno_anterior = self._current_return
        genericos_anteriores = self._genericos_da_acao
        self._current_return = assinatura.return_type
        self._genericos_da_acao = set(getattr(node, "type_params", None) or [])
        self._action_depth += 1
        self._hoist(node.body, interno)
        try:
            sempre_retorna = self.visit_block(node.body, interno)
        finally:
            self._action_depth -= 1
            self._current_return = retorno_anterior
            self._genericos_da_acao = genericos_anteriores

        declarado = assinatura.return_type
        if (declarado not in (UNKNOWN, ANY, "Void")
                and declarado not in genericos
                and not sempre_retorna and not assinatura.is_generator):
            self.warn(
                f"Action '{node.name}' declares '-> {declarado}' but can end "
                f"without a 'yield'", node,
                "Add a 'yield' at the end, or drop the return type",
                "missing-return")
        return False

    def st_BlueprintDeclaration(self, node, escopo):
        interno = Scope(escopo, "blueprint")
        interno.declare("self", node.name, node.line, node.column)
        interno.declare("this", node.name, node.line, node.column)
        interno.declare("root", ANY, node.line, node.column)
        for param in node.constructor_params or []:
            interno.declare(param, UNKNOWN, node.line, node.column)
        for pai in node.parents:
            if pai not in self.blueprints and pai not in self.known_types:
                self.error(f"Unknown parent blueprint '{pai}'", node,
                           self._hint_nome(pai, self.blueprints), "unknown-parent")
        for trait in getattr(node, 'traits', []) or []:
            if trait not in self.blueprints:
                self.error(f"Unknown trait '{trait}'", node,
                           self._hint_nome(trait, self.blueprints), "unknown-trait")
        self._hoist(node.body, interno, registrar_acoes=False)
        anterior = self._em_membro
        genericos_antes = self._genericos_do_blueprint
        self._em_membro = True
        # Os '<T>' deste blueprint valem nos metodos dele — e so ali.
        self._genericos_do_blueprint = set(
            getattr(node, "type_params", None) or [])
        try:
            self.visit_block(node.body, interno)
        finally:
            self._em_membro = anterior
            self._genericos_do_blueprint = genericos_antes
        return False

    def st_TraitDeclaration(self, node, escopo):
        interno = Scope(escopo, "trait")
        interno.declare("self", node.name, node.line, node.column)
        anterior = self._em_membro
        self._em_membro = True
        try:
            self.visit_block(node.methods, interno)
        finally:
            self._em_membro = anterior
        return False

    def st_RecordDeclaration(self, node, escopo):
        vistos = set()
        for campo, tipo, padrao in node.fields:
            if campo in vistos:
                self.error(f"Duplicate field '{campo}' in record '{node.name}'",
                           node, "Remove the repeated field", "duplicate-field")
            vistos.add(campo)
            alvo = canonical(tipo)
            if alvo not in self.known_types:
                self.error(f"Unknown type '{tipo}' for field '{campo}'", node,
                           self._hint_tipo(tipo), "unknown-type")
            if padrao is not None:
                obtido = self.infer(padrao, escopo)
                if not compatible(alvo, obtido):
                    self.error(
                        f"Default value of '{campo}' is {obtido}, expected {alvo}",
                        node, f"Use a {alvo} as the default", "type-mismatch")
        interno = Scope(escopo, "record")
        interno.declare("self", node.name, node.line, node.column)
        for campo, tipo, _ in node.fields:
            interno.declare(campo, canonical(tipo), node.line, node.column)
        anterior = self._em_membro
        self._em_membro = True
        try:
            for metodo in node.methods.values():
                self.visit(metodo, interno)
        finally:
            self._em_membro = anterior
        return False

    def st_EnumDeclaration(self, node, escopo):
        vistos = set()
        for membro, valor in node.members:
            if membro in vistos:
                self.error(f"Duplicate member '{membro}' in enum '{node.name}'",
                           node, "Remove the repeated member", "duplicate-member")
            vistos.add(membro)
            if valor is not None:
                self.infer(valor, escopo)
        interno = Scope(escopo, "enum")
        interno.declare("self", node.name, node.line, node.column)
        anterior = self._em_membro
        self._em_membro = True
        try:
            for metodo in node.methods.values():
                self.visit(metodo, interno)
        finally:
            self._em_membro = anterior
        return False

    def st_AdoptStatement(self, node, escopo):
        from .stdlib import get_module, list_modules

        selecao = getattr(node, 'selection', None)
        if selecao:
            # adopt M.{a, b as c} — os nomes entram direto no escopo
            for _, apelido in selecao:
                escopo.declare(apelido, ANY, node.line, node.column)
                self.actions.setdefault(apelido, None)
        else:
            alias = node.alias or node.module.split('.')[-1]
            escopo.declare(alias, "Module", node.line, node.column)
        # 'Python.x' nao e um modulo da stdlib nem um arquivo vizinho:
        # e a ponte. Mas o analisador pode PROVAR uma coisa util sobre
        # ela — se o pacote esta instalado neste Python — e avisar disso
        # antes de rodar e justamente o trabalho dele.
        from .ponte import e_caminho_de_ponte, tem, PREFIXO
        if e_caminho_de_ponte(node.module):
            pacote = node.module[len(PREFIXO) + 1:].split('.')[0]
            if pacote and not tem(pacote):
                self.warn(
                    f"o pacote Python '{pacote}' nao esta instalado aqui",
                    node,
                    "se ele existir na maquina que vai RODAR o programa, "
                    "este aviso nao se aplica",
                    "pacote-python-ausente")
            return False

        modulo_padrao = get_module(node.module)
        if modulo_padrao is not None:
            # A superficie de um modulo da BIBLIOTECA e a mais confiavel
            # que existe: ele esta carregado, e a lista de simbolos e o
            # proprio dicionario. 'Math.sqrtt(4)' passava pelo 'check'
            # sem uma palavra e so falhava ao rodar — e num ramo que so
            # roda em producao, falhava em producao.
            from . import superficie as sup
            if selecao:
                for original, apelido in selecao:
                    if original not in modulo_padrao:
                        self.error(
                            f"module '{node.module}' does not export "
                            f"'{original}'", node,
                            self._hint_nome(original, sorted(
                                k for k in modulo_padrao
                                if not k.startswith('__'))),
                            "unknown-export")
                return False
            alias = node.alias or node.module.split('.')[-1]
            self.superficies[alias] = sup.de_modulo_padrao(
                node.module, modulo_padrao)
            return False

        # ── Um modulo LOCAL ──
        #
        # A resolucao mora em 'resolucao.py', a mesma que o
        # interpretador usa. Antes estava copiada aqui e fazia
        # `node.module.replace('.', os.sep)`, o que transforma './mod'
        # em '//mod': TODO 'adopt' relativo de TODO projeto virava um
        # aviso "não encontrei" falso. Eram 62 no repositorio e 795 num
        # projeto de 21 mil linhas — 795 de 795.
        from . import superficie as sup

        achada = sup.de_modulo(node.module, self.filename)
        if achada is None:
            from . import resolucao
            declaradas = resolucao.dependencias_declaradas(self.filename)
            raiz_pedida = node.module.split('.')[0]
            if raiz_pedida in declaradas:
                # Declarado no forge.toml e nao instalado. Dizer o
                # comando que resolve e a diferenca entre um aviso util
                # e um aviso que so incomoda.
                self.warn(
                    f"package '{raiz_pedida}' is declared in forge.toml "
                    f"but not installed", node,
                    "run 'dataforge install'", "pacote-nao-instalado")
            else:
                self.warn(
                    f"Module '{node.module}' was not found", node,
                    f"Available: {', '.join(sorted(set(list_modules()))[:8])}…",
                    "unknown-module")
            return False

        if selecao:
            # 'adopt ./x.{a, b}' — confere que 'a' e 'b' existem la.
            for original, apelido in selecao:
                if not achada.tem(original):
                    self.error(
                        f"Module '{node.module}' does not export "
                        f"'{original}'", node,
                        self._hint_nome(original, achada.nomes()) or
                        f"Exports: {', '.join(achada.nomes()[:10])}",
                        "unknown-export")
            return False

        # Um ciclo estoura em EXECUCAO, no primeiro 'adopt'. Achar
        # isso antes de rodar e o trabalho do analisador, e ele nao
        # fazia: o 'check' passava limpo num projeto que nao sobe.
        ciclo = sup.ciclo_a_partir_de(self.filename) \
            if self.filename and not self.filename.startswith('<') else None
        if ciclo and not self._ciclo_relatado:
            self._ciclo_relatado = True
            cadeia = " → ".join(_curto(c) for c in ciclo)
            self.error(
                f"circular import: {cadeia}", node,
                "move the shared part into a third module", "import-circular")

        alias = node.alias or node.module.split('.')[-1]
        self.superficies[alias] = achada
        self._registrar_tipos_de(alias, achada)
        return False

    def _registrar_tipos_de(self, alias, superficie):
        """Os records e blueprints do outro arquivo entram nas tabelas.

        Sob o nome qualificado (`M0.Ponto0`), que é o que
        `ex_MemberAccess` devolve. Assim a conferência de campo que já
        existe para o tipo local passa a valer para o importado, sem
        uma segunda implementação da mesma regra.
        """
        for nome in superficie.nomes():
            membro = superficie.obter(nome)
            qualificado = f"{alias}.{nome}"
            if membro.especie == "record":
                # Sem os tipos dos campos: a superfície guarda o nome, e
                # inventar um tipo daria erro onde não há.
                self.records.setdefault(
                    qualificado, {c: ANY for c in membro.campos})
            elif membro.especie == "blueprint":
                if membro.campos:
                    self.blueprints.setdefault(qualificado,
                                               set(membro.campos))
                else:
                    # Conjunto vazio na superfície significa "herda de
                    # algo que não vi". Registrar como mãe desconhecida
                    # é o que faz a regra existente calar.
                    self.blueprints.setdefault(qualificado, set())
                    self.maes.setdefault(qualificado, ["<outro arquivo>"])
            elif membro.especie == "enum":
                self.enums.setdefault(qualificado, list(membro.campos))

    def st_RelayStatement(self, node, escopo):
        for nome in node.names:
            if not escopo.has(nome):
                self.error(f"'relay' exports '{nome}', which is not defined", node,
                           self._hint_nome(nome, self._visible_names(escopo)),
                           "relay-undefined")
        return False

    def st_DeleteStatement(self, node, escopo):
        self.infer(node.target, escopo)
        return False

    def st_WaitStatement(self, node, escopo):
        self.infer(node.duration, escopo)
        return False

    def st_InspectStatement(self, node, escopo):
        self.infer(node.expression, escopo)
        return False

    def st_PulseStatement(self, node, escopo):
        self.infer(node.event, escopo)
        if node.data is not None:
            self.infer(node.data, escopo)
        return False

    # ── Expressões: inferência ─────────────────────────────

    def infer(self, node, escopo):
        if node is None:
            return "Void"
        metodo = getattr(self, f"ex_{type(node).__name__}", None)
        if metodo:
            return metodo(node, escopo)
        return UNKNOWN

    def ex_IntegerLiteral(self, node, escopo): return "Integer"
    def ex_FloatLiteral(self, node, escopo): return "Float"
    def ex_StringLiteral(self, node, escopo): return "String"
    def ex_BooleanLiteral(self, node, escopo): return "Boolean"
    def ex_VoidLiteral(self, node, escopo): return "Void"

    def ex_InterpolatedString(self, node, escopo):
        for tipo, conteudo in node.parts:
            if tipo == 'expr':
                self.infer(conteudo, escopo)
            elif tipo == 'fmt':
                # A parte com formato tambem carrega uma expressao. Sem
                # olha-la, '{naoexiste:.2f}' passaria pelo 'check' e so
                # estouraria em execucao — que e o que o analisador
                # existe para evitar.
                self.infer(conteudo[0], escopo)
        return "String"

    def ex_ListLiteral(self, node, escopo):
        for e in node.elements:
            self.infer(e.value if isinstance(e, ast.SpreadElement) else e, escopo)
        return "Cluster"

    def ex_DictLiteral(self, node, escopo):
        for chave, valor in node.pairs:
            if isinstance(chave, ast.SpreadElement):
                self.infer(chave.value, escopo)
                continue
            self.infer(chave, escopo)
            self.infer(valor, escopo)
        return "Vault"

    def ex_SpreadElement(self, node, escopo):
        return self.infer(node.value, escopo)

    def ex_Identifier(self, node, escopo):
        tipo = escopo.lookup(node.name)
        if tipo is None:
            if node.name in KEYWORDS:
                self.error(f"'{node.name}' is a reserved keyword", node,
                           "Pick another name", "reserved-word")
            else:
                self.error(f"Undefined name '{node.name}'", node,
                           self._hint_nome(node.name, self._visible_names(escopo)),
                           "undefined-name")
            return UNKNOWN
        return tipo

    def ex_BinaryOp(self, node, escopo):
        esq = self.infer(node.left, escopo)
        dir_ = self.infer(node.right, escopo)
        op = node.op

        if UNKNOWN in (esq, dir_) or ANY in (esq, dir_):
            return UNKNOWN

        # Blueprints e records podem sobrecarregar add/sub/mul/div/mod/pow.
        if self._overloads(esq) or self._overloads(dir_):
            return esq if self._overloads(esq) else dir_

        if op == '+':
            if "String" in (esq, dir_):
                return "String"
            if esq == "Cluster" and dir_ == "Cluster":
                return "Cluster"
            if esq in NUMERIC and dir_ in NUMERIC:
                return "Float" if "Float" in (esq, dir_) else "Integer"
            self.error(f"Cannot add {esq} and {dir_}", node,
                       "Convert one side with str() or int()", "operator-types")
            return UNKNOWN

        if op == '*':
            if {esq, dir_} == {"String", "Integer"} or {esq, dir_} == {"Cluster", "Integer"}:
                return esq if esq != "Integer" else dir_
            if esq in NUMERIC and dir_ in NUMERIC:
                return "Float" if "Float" in (esq, dir_) else "Integer"
            self.error(f"Cannot multiply {esq} by {dir_}", node,
                       "Multiplication needs numbers", "operator-types")
            return UNKNOWN

        if op in ('-', '%', '**', '//'):
            if esq in NUMERIC and dir_ in NUMERIC:
                if op == '//':
                    return "Integer" if {esq, dir_} <= {"Integer"} else "Float"
                return "Float" if "Float" in (esq, dir_) else "Integer"
            self.error(f"Operator '{op}' does not apply to {esq} and {dir_}", node,
                       f"'{op}' needs numbers on both sides", "operator-types")
            return UNKNOWN

        if op == '/':
            if esq in NUMERIC and dir_ in NUMERIC:
                if isinstance(node.right, ast.IntegerLiteral) and node.right.value == 0:
                    self.error("Division by zero", node,
                               "Check the divisor before dividing", "division-by-zero")
                return "Float"
            self.error(f"Cannot divide {esq} by {dir_}", node,
                       "Division needs numbers", "operator-types")
            return UNKNOWN

        return UNKNOWN

    def _overloads(self, tipo):
        """O tipo pode definir operadores próprios (add, mul, ...)?"""
        return tipo in self.blueprints or tipo in self.records

    def ex_UnaryOp(self, node, escopo):
        tipo = self.infer(node.operand, escopo)
        if tipo not in (UNKNOWN, ANY) and tipo not in NUMERIC:
            self.error(f"Unary '{node.op}' does not apply to {tipo}", node,
                       "Use it on a number", "operator-types")
        return tipo

    def ex_NotOp(self, node, escopo):
        self.infer(node.operand, escopo)
        return "Boolean"

    def ex_ComparisonOp(self, node, escopo):
        esq = self.infer(node.left, escopo)
        dir_ = self.infer(node.right, escopo)
        if node.op in ('bigger', 'smaller', 'bigger_eq', 'smaller_eq'):
            if UNKNOWN not in (esq, dir_) and ANY not in (esq, dir_):
                if esq in NUMERIC and dir_ in NUMERIC:
                    pass
                elif esq == dir_ and esq in ORDERABLE:
                    pass
                else:
                    self.error(
                        f"Cannot order {esq} against {dir_}", node,
                        "Compare values of the same comparable type", "compare-types")
        return "Boolean"

    def ex_LogicalOp(self, node, escopo):
        self.infer(node.left, escopo)
        self.infer(node.right, escopo)
        return "Boolean"

    def ex_MembershipOp(self, node, escopo):
        self.infer(node.element, escopo)
        recipiente = self.infer(node.container, escopo)
        if recipiente in ("Integer", "Float", "Boolean", "Void"):
            self.error(f"Cannot test membership in {recipiente}", node,
                       "'in' needs a Cluster, Vault or String", "membership-type")
        return "Boolean"

    def ex_TernaryExpression(self, node, escopo):
        self.infer(node.condition, escopo)
        a = self.infer(node.then_value, escopo)
        b = self.infer(node.else_value, escopo)
        return a if a == b else UNKNOWN

    def ex_CoalesceOp(self, node, escopo):
        self.infer(node.left, escopo)
        return self.infer(node.right, escopo)

    def ex_TypeofExpression(self, node, escopo):
        self.infer(node.operand, escopo)
        return "String"

    def ex_CastExpression(self, node, escopo):
        self.infer(node.operand, escopo)
        alvo = canonical(node.target_type)
        if alvo not in self.known_types:
            self.error(f"Unknown cast target '{node.target_type}'", node,
                       self._hint_tipo(node.target_type), "unknown-type")
            return UNKNOWN
        return alvo

    def ex_AwaitExpression(self, node, escopo):
        return self.infer(node.expression, escopo)

    def ex_InExpression(self, node, escopo):
        if node.prompt is not None:
            self.infer(node.prompt, escopo)
        return "String"

    def ex_PipelineExpression(self, node, escopo):
        fonte = self.infer(node.source, escopo)
        if fonte in ("Integer", "Float", "Boolean", "Void"):
            self.error(f"Cannot pipeline from {fonte}", node,
                       "Pipelines start from a Cluster", "pipeline-source")
        resultado = "Cluster"
        for op in node.operations:
            interno = Scope(escopo)
            if isinstance(op, ast.SiftOperation):
                if op.func_ref:
                    self._check_ref(op.func_ref, op, escopo, 1)
                else:
                    interno.declare(op.param, UNKNOWN, op.line, op.column)
                    self.infer(op.condition, interno)
            elif isinstance(op, ast.MorphOperation):
                if op.func_ref:
                    self._check_ref(op.func_ref, op, escopo, 1)
                else:
                    interno.declare(op.param, UNKNOWN, op.line, op.column)
                    self.infer(op.expression, interno)
            elif isinstance(op, ast.DistillOperation):
                if op.func_ref:
                    self._check_ref(op.func_ref, op, escopo, 2)
                else:
                    interno.declare(op.acc_param, UNKNOWN, op.line, op.column)
                    interno.declare(op.val_param, UNKNOWN, op.line, op.column)
                    self.infer(op.expression, interno)
                if op.initial is not None:
                    self.infer(op.initial, escopo)
                resultado = UNKNOWN
        return resultado

    def _check_ref(self, nome, node, escopo, aridade):
        if not escopo.has(nome):
            self.error(f"Undefined action '{nome}' in the pipeline", node,
                       self._hint_nome(nome, self.actions), "undefined-name")
            return
        assinatura = self.actions.get(nome)
        if assinatura and len(assinatura.required) > aridade:
            self.error(
                f"Action '{nome}' needs {len(assinatura.required)} argument(s) "
                f"but the pipeline passes {aridade}", node,
                f"Give the extra parameters a default value", "arity")

    def ex_ListComprehension(self, node, escopo):
        interno = self._scope_for_clauses(node.clauses, escopo)
        self.infer(node.expression, interno)
        return "Cluster"

    def ex_VaultComprehension(self, node, escopo):
        interno = self._scope_for_clauses(node.clauses, escopo)
        self.infer(node.key, interno)
        self.infer(node.value, interno)
        return "Vault"

    def _scope_for_clauses(self, clauses, escopo):
        atual = escopo
        for clause in clauses:
            fonte = self.infer(clause.source, atual)
            if fonte in ("Integer", "Float", "Boolean", "Void"):
                self.error(
                    f"Cannot iterate over {fonte} in the comprehension",
                    clause, "Use a Cluster, a Vault or a String", "cycle-not-iterable")
            atual = Scope(atual)
            for alvo in (clause.targets or [clause.var]):
                atual.declare(alvo, UNKNOWN, clause.line, clause.column)
            if clause.condition is not None:
                self.infer(clause.condition, atual)
        return atual

    def ex_LambdaExpression(self, node, escopo):
        interno = Scope(escopo, "action")
        for param in node.params:
            interno.declare(param, canonical(node.param_types.get(param, UNKNOWN)),
                            node.line, node.column)
        for padrao in node.defaults.values():
            self.infer(padrao, escopo)
        self.infer(node.body, interno)
        return "Action"

    def ex_IndexAccess(self, node, escopo):
        alvo = self.infer(node.object, escopo)
        self.infer(node.index, escopo)
        if alvo in ("Integer", "Float", "Boolean", "Void"):
            self.error(f"Cannot index a value of type {alvo}", node,
                       "Indexing needs a Cluster, Vault or String", "index-type")
        return UNKNOWN

    def ex_SliceAccess(self, node, escopo):
        alvo = self.infer(node.object, escopo)
        for parte in (node.start, node.stop, node.step):
            if parte is not None:
                tipo = self.infer(parte, escopo)
                if tipo not in (UNKNOWN, ANY) and tipo != "Integer":
                    self.error(f"Slice bounds must be Integer, got {tipo}", node,
                               "Use whole numbers in the slice", "slice-type")
        return alvo if alvo in ("Cluster", "String") else UNKNOWN

    def ex_MemberAccess(self, node, escopo):
        alvo = self.infer(node.object, escopo)

        if alvo in self.records:
            campos = self.records[alvo]
            if node.member not in campos and node.member not in ('fields', 'record_name'):
                self.error(
                    f"Record '{alvo}' has no field '{node.member}'", node,
                    self._hint_nome(node.member, campos) or
                    f"Fields: {', '.join(campos)}", "unknown-field")
                return UNKNOWN
            return campos.get(node.member, UNKNOWN)

        if isinstance(node.object, ast.Identifier):
            nome = node.object.name

            # 'P.naoExiste' num modulo local. O apelido so entra em
            # 'superficies' quando o arquivo foi lido E a lista de
            # exportados e confiavel.
            superficie = self.superficies.get(nome)
            if superficie is not None and not superficie.aberta:
                if not superficie.tem(node.member):
                    self.error(
                        f"module '{nome}' has no '{node.member}'", node,
                        self._hint_nome(node.member, superficie.nomes()) or
                        f"it offers: {', '.join(superficie.nomes()[:10])}",
                        "unknown-module-member")
                    return UNKNOWN
                membro = superficie.obter(node.member)
                # Um record ou blueprint de outro arquivo: o TIPO passa
                # a ser conhecido aqui, e é o que permite conferir o
                # campo de uma instância dele logo abaixo.
                if membro is not None and membro.especie in ("record",
                                                             "blueprint",
                                                             "enum"):
                    return f"{nome}.{node.member}"
                return UNKNOWN

            if nome in self.enums:
                membros = self.enums[nome]
                metodos = {'names', 'values', 'members', 'count', 'has',
                           'from_value', 'from_name'}
                if node.member not in membros and node.member not in metodos:
                    self.error(
                        f"Enum '{nome}' has no member '{node.member}'", node,
                        self._hint_nome(node.member, membros) or
                        f"Members: {', '.join(membros)}", "unknown-member")
                    return UNKNOWN
                return nome if node.member in membros else UNKNOWN

        # ── Membro de instância ──
        #
        # O caso que faltava, e o que mais custa em projeto grande:
        # 'self.clientte' passava pelo 'check' sem uma palavra, e só
        # explodia no dia em que aquele ramo rodasse.
        self._conferir_membro_de_instancia(alvo, node)
        return UNKNOWN

    #: O que toda instância tem, venha de onde vier.
    #:
    #: `self` e `this` são o próprio objeto; os métodos mágicos são
    #: chamados pelo runtime e podem não estar declarados no arquivo que
    #: se está olhando.
    _SEMPRE_NA_INSTANCIA = {
        "self", "this", "root", "blueprint_name", "fields",
        "toString", "to_string", "copy", "clone", "equals", "hash",
    }

    def _conferir_membro_de_instancia(self, tipo, node):
        """'p.clientte' quando 'p' é um blueprint conhecido.

        Só acusa quando consegue PROVAR: o tipo é um blueprint deste
        arquivo, a linhagem inteira é conhecida, e o nome não está em
        lugar nenhum dela. Fora disso, silêncio — o analisador é
        otimista de propósito, e um falso alarme ensina a ignorar a
        ferramenta.
        """
        if tipo not in self.blueprints:
            return
        if not self._blueprint_e_fechado(tipo):
            return               # herda de algo que não vimos

        membro = node.member
        if membro.startswith("__") or membro in self._SEMPRE_NA_INSTANCIA:
            return

        membros = self._membros_com_heranca(tipo)
        if membro in membros:
            return

        # 'obj.x := …' fora do blueprint acrescenta o campo em execução.
        # Quem faz isso perde a conferência, e é a escolha de quem
        # escreveu — não um erro a acusar.
        if membro in self.campos_postos_de_fora:
            return

        self.error(
            f"'{tipo}' has no member '{membro}'", node,
            self._hint_nome(membro, membros)
            or (f"It has: {', '.join(sorted(membros)[:8])}"
                + ("…" if len(membros) > 8 else "")),
            "unknown-member")

    def ex_SafeMemberAccess(self, node, escopo):
        self.infer(node.object, escopo)
        return UNKNOWN

    def ex_MethodCall(self, node, escopo):
        alvo = self.infer(node.object, escopo)
        for a in node.args:
            self.infer(a.value if isinstance(a, ast.SpreadElement) else a, escopo)
        for v in node.kwargs.values():
            self.infer(v, escopo)

        # 'P.criar(1, 2, 3)' num modulo local: existe, e com quantos?
        if isinstance(node.object, ast.Identifier):
            resultado = self._conferir_chamada_de_modulo(node, escopo)
            if resultado is not None:
                return resultado

        # 'c.sacarr(10)' — o mesmo trabalho do acesso a campo, porque é
        # o mesmo erro: um nome que não existe naquele blueprint.
        #
        # Um nó de MethodCall não tem '.member'; a mensagem de erro o
        # lê, então passa-se um nó equivalente com a posição certa.
        if alvo in self.blueprints:
            self._conferir_membro_de_instancia(
                alvo, ast.MemberAccess(object=node.object, member=node.method,
                                       line=node.line, column=node.column))
        return UNKNOWN

    def _conferir_chamada_de_modulo(self, node, escopo=None):
        """`P.criar(1, 2, 3)` quando `P` é um módulo local lido.

        Devolve o tipo quando tratou o caso, ou `None` para deixar o
        fluxo normal seguir. Só acusa o que consegue **provar**: a
        superfície aberta — arquivo que não compila, ciclo de import,
        `relay` de nome calculado — não acusa nada.
        """
        superficie = self.superficies.get(node.object.name)
        if superficie is None or superficie.aberta:
            return None

        membro = superficie.obter(node.method)
        if membro is None:
            self.error(
                f"module '{node.object.name}' has no '{node.method}'", node,
                self._hint_nome(node.method, superficie.nomes()) or
                f"it offers: {', '.join(superficie.nomes()[:10])}",
                "unknown-module-member")
            return UNKNOWN

        # Spread esconde a contagem: '...args' pode ser qualquer
        # tamanho, e cobrar aridade ali seria inventar um erro.
        if any(isinstance(a, ast.SpreadElement) for a in node.args):
            return UNKNOWN

        quantos = len(node.args) + len(node.kwargs)
        if not membro.aceita(quantos):
            plural = "" if quantos == 1 else "s"
            self.error(
                f"'{node.object.name}.{node.method}' takes "
                f"{membro.esperado()} argument(s), got {quantos}", node,
                f"declared in {_curto(superficie.caminho)}"
                f"{f' line {membro.linha}' if membro.linha else ''}",
                "module-arity")
            return UNKNOWN

        if membro.especie in ("record", "blueprint", "enum"):
            return f"{node.object.name}.{node.method}"

        self._conferir_tipos_do_modulo(node, membro, superficie, escopo)

        # O tipo declarado em '-> Tipo' ATRAVESSA a fronteira do modulo.
        #
        # Devolver UNKNOWN aqui fazia o tipo se perder: uma acao que
        # declara '-> Pedido' e chamada de outro arquivo virava um valor
        # sem tipo, e 'P.criar(1, "Ana").clientte' passava no 'check'.
        # No mesmo arquivo esse campo errado e acusado com sugestao.
        #
        # Num sistema de 200 arquivos a maioria das chamadas atravessa
        # modulo, e era ali que a conferencia calava.
        if membro.retorno:
            traduzido = self._tipo_do_modulo(node.object.name, membro.retorno)
            if traduzido:
                return traduzido
        return UNKNOWN

    def _conferir_tipos_do_modulo(self, node, membro, superficie,
                                  escopo=None):
        """Os tipos dos PARAMETROS, atraves do `adopt`.

        A aridade era conferida e o tipo nao: a superficie sabia quantos
        argumentos a acao aceita, e nao o que cada um devia ser. Entao
        `D.valor_de("texto")` — onde a declaracao e `n: Integer` —
        passava no `check`, e estourava em execucao na primeira conta.
        """
        if not membro.tipos or not membro.parametros:
            return
        # O escopo de QUEM CHAMA, e nao o global.
        #
        # 'self.global_scope' nao ve parametro de acao nem variavel de
        # bloco: 'D.valor_de(n)' dentro de 'action f(n)' virava
        # "Undefined name 'n'". Foram 649 falsos alarmes num projeto de
        # 252 arquivos — cada uso de um parametro numa chamada entre
        # modulos.
        #
        # Os argumentos JA foram inferidos com o escopo certo em
        # 'ex_MethodCall', antes de chegar aqui; o que se faz agora e
        # repetir a inferencia para comparar, e ela precisa do mesmo
        # escopo.
        if escopo is None:
            return
        for indice, argumento in enumerate(node.args):
            if isinstance(argumento, ast.SpreadElement):
                return          # o spread esconde quem vai onde
            if indice >= len(membro.parametros):
                break
            esperado = self._esperado_do_modulo(
                node.object.name, membro.tipos.get(membro.parametros[indice]))
            if not esperado:
                continue
            obtido = self.infer(argumento, escopo)
            if obtido and not compatible(esperado, obtido):
                nome = membro.parametros[indice]
                self.error(
                    f"Parameter '{nome}' of '{node.object.name}."
                    f"{node.method}' expects {esperado} but got {obtido}",
                    argumento,
                    f"declared in {_curto(superficie.caminho)}"
                    f"{f' line {membro.linha}' if membro.linha else ''}",
                    "module-arg-type")

        for nome, valor in (node.kwargs or {}).items():
            esperado = self._esperado_do_modulo(node.object.name,
                                                membro.tipos.get(nome))
            if not esperado:
                continue
            obtido = self.infer(valor, escopo)
            if obtido and not compatible(esperado, obtido):
                self.error(
                    f"Parameter '{nome}' of '{node.object.name}."
                    f"{node.method}' expects {esperado} but got {obtido}",
                    valor, "", "module-arg-type")

    def _esperado_do_modulo(self, apelido, nome_do_tipo):
        """O tipo de um PARAMETRO, no vocabulario deste arquivo.

        `p: Pedido` no outro arquivo precisa virar `P.Pedido` aqui —
        que e como o retorno de `P.criar` chega. Sem a traducao, o
        analisador comparava `Pedido` com `P.Pedido` e acusava um erro
        no codigo CERTO:

            Parameter 'p' of 'P.com_total' expects Pedido but got
            P.Pedido

        Um falso alarme como esse, no caminho mais comum de um projeto
        modular, ensinaria a desligar a verificacao inteira.

        Devolve `None` quando nao da para concluir — e ai a conferencia
        cala, que e a politica.
        """
        if not nome_do_tipo:
            return None
        traduzido = self._tipo_do_modulo(apelido, nome_do_tipo)
        if traduzido and traduzido != UNKNOWN:
            return traduzido
        # Um tipo que o outro modulo nao exporta: nao ha como saber o
        # que ele e daqui.
        return None

    def _tipo_do_modulo(self, apelido, nome_do_tipo):
        """O tipo de retorno de outro modulo, no vocabulario DESTE arquivo.

        Um `-> Pedido` no outro arquivo e `P.Pedido` aqui: o nome nu nao
        existe neste escopo, e devolve-lo faria o analisador procurar um
        record chamado 'Pedido' que este arquivo nao declara — e acusar
        o que nao devia.

        Um tipo embutido (`Integer`, `String`, `Cluster`) atravessa como
        esta. Um tipo que o outro modulo declara vira `apelido.Tipo`,
        e so quando ele REALMENTE o exporta.
        """
        limpo = canonical(nome_do_tipo)
        if limpo in set(ALIASES.values()):
            return limpo
        superficie = self.superficies.get(apelido)
        if superficie is None or superficie.aberta:
            return None
        membro = superficie.obter(nome_do_tipo)
        if membro is not None and membro.especie in ("record", "blueprint",
                                                     "enum"):
            return f"{apelido}.{nome_do_tipo}"
        return None

    def ex_SafeMethodCall(self, node, escopo):
        return self.ex_MethodCall(node, escopo)

    def ex_FunctionCall(self, node, escopo):
        # 'expect(...)' na forma encadeada chega aqui como chamada a
        # '__expect__'. O argumento existe para provocar falha —
        # 'expect(lambda => 1 / 0).to_raise(...)' e a forma correta de
        # testar divisao por zero — entao vale a mesma tolerancia do
        # 'monitor'. Sem ela, o analisador acusa o teste que faz certo.
        if isinstance(node.callee, ast.Identifier) \
                and node.callee.name == "__expect__":
            with self._demoted():
                for a in node.args:
                    self.infer(a, escopo)
            return "Expectativa"

        for a in node.args:
            self.infer(a.value if isinstance(a, ast.SpreadElement) else a, escopo)
        for v in node.kwargs.values():
            self.infer(v, escopo)

        if not isinstance(node.callee, ast.Identifier):
            self.infer(node.callee, escopo)
            return UNKNOWN

        nome = node.callee.name

        if nome in self.records:
            return self._check_record_call(nome, node, escopo)

        if not escopo.has(nome):
            self.error(f"Undefined action '{nome}'", node,
                       self._hint_nome(nome, self._visible_names(escopo)),
                       "undefined-name")
            return UNKNOWN
        escopo.lookup(nome)

        assinatura = self.actions.get(nome)
        if assinatura is None:
            # Nome importado seletivamente ou definido fora deste arquivo:
            # não há assinatura para conferir.
            return UNKNOWN
        if any(isinstance(a, ast.SpreadElement) for a in node.args):
            return assinatura.return_type

        posicionais = len(node.args)
        fornecidos = set(assinatura.params[:posicionais]) | set(node.kwargs)
        faltando = [p for p in assinatura.required if p not in fornecidos]
        if faltando:
            self.error(
                f"Action '{nome}' is missing argument(s): {', '.join(faltando)}",
                node, f"Call it as {nome}({', '.join(assinatura.params)})", "arity")
        if posicionais > len(assinatura.params):
            self.error(
                f"Action '{nome}' takes {len(assinatura.params)} argument(s) "
                f"but {posicionais} were given", node,
                f"Call it as {nome}({', '.join(assinatura.params)})", "arity")
        desconhecidos = [k for k in node.kwargs if k not in assinatura.params]
        if desconhecidos:
            self.error(
                f"Action '{nome}' has no parameter(s): {', '.join(desconhecidos)}",
                node, f"Parameters: {', '.join(assinatura.params)}", "unknown-argument")

        for indice, arg in enumerate(node.args):
            if indice >= len(assinatura.params):
                break
            declarado = canonical(assinatura.param_types.get(assinatura.params[indice], UNKNOWN))
            if declarado in (UNKNOWN, ANY):
                continue
            obtido = self.infer(arg, escopo)
            if not compatible(declarado, obtido):
                self.error(
                    f"Parameter '{assinatura.params[indice]}' of '{nome}' expects "
                    f"{declarado} but got {obtido}", arg,
                    f"Pass a {declarado}", "argument-type")

        if assinatura.is_generator:
            return "Stream"
        return assinatura.return_type

    def _check_record_call(self, nome, node, escopo):
        campos = self.records[nome]
        opcionais = self.record_defaults.get(nome, set())
        obrigatorios = [c for c in campos if c not in opcionais]
        posicionais = len(node.args)
        fornecidos = set(list(campos)[:posicionais]) | set(node.kwargs)
        faltando = [c for c in obrigatorios if c not in fornecidos]
        if faltando:
            self.error(
                f"Record '{nome}' is missing field(s): {', '.join(faltando)}",
                node, f"Build it as {nome}({', '.join(campos)})", "record-arity")
        if posicionais > len(campos):
            self.error(
                f"Record '{nome}' has {len(campos)} field(s) but "
                f"{posicionais} value(s) were given", node,
                f"Build it as {nome}({', '.join(campos)})", "record-arity")
        desconhecidos = [k for k in node.kwargs if k not in campos]
        if desconhecidos:
            self.error(
                f"Record '{nome}' has no field(s): {', '.join(desconhecidos)}",
                node, f"Fields: {', '.join(campos)}", "unknown-field")
        for indice, arg in enumerate(node.args):
            if indice >= len(campos):
                break
            campo = list(campos)[indice]
            esperado = campos[campo]
            obtido = self.infer(arg, escopo)
            if not compatible(esperado, obtido):
                self.error(
                    f"Field '{campo}' of record '{nome}' expects {esperado} "
                    f"but got {obtido}", arg, f"Pass a {esperado}", "field-type")
        return nome

    def ex_SpawnExpression(self, node, escopo):
        for a in node.args:
            self.infer(a.value if isinstance(a, ast.SpreadElement) else a, escopo)
        if isinstance(node.class_name, ast.Identifier):
            nome = node.class_name.name
            if nome in self.records:
                self.error(
                    f"'{nome}' is a record, not a blueprint", node,
                    f"Build it with {nome}(...) instead of 'spawn'", "spawn-record")
                return nome
            if nome not in self.blueprints and not escopo.has(nome):
                self.error(f"Unknown blueprint '{nome}'", node,
                           self._hint_nome(nome, self.blueprints), "unknown-blueprint")
                return UNKNOWN
            return nome
        return UNKNOWN

    def ex_WithExpression(self, node, escopo):
        base = self.infer(node.source, escopo)
        self.infer(node.changes, escopo)
        if base in self.records and isinstance(node.changes, ast.DictLiteral):
            campos = self.records[base]
            for chave, _ in node.changes.pairs:
                if isinstance(chave, ast.StringLiteral) and chave.value not in campos:
                    self.error(
                        f"Record '{base}' has no field '{chave.value}'", node,
                        self._hint_nome(chave.value, campos) or
                        f"Fields: {', '.join(campos)}", "unknown-field")
        return base

    def ex_FrameExpression(self, node, escopo):
        self.infer(node.data, escopo)
        return "Vault"

    # ── Sugestões ──────────────────────────────────────────

    def _hint_nome(self, nome, candidatos):
        parecido = self._similar(nome, candidatos)
        if parecido:
            return f"Did you mean '{parecido}'?"
        return ""

    def _hint_tipo(self, nome):
        parecido = self._similar(nome, self.known_types)
        if parecido:
            return f"Did you mean '{parecido}'?"
        return f"Known types: Integer, Float, String, Boolean, Cluster, Vault, Void"


def check_program(program, filename="<stdin>", strict=False, source=None):
    """Analisa um programa e devolve a lista de diagnósticos.

    `source` e opcional: com ela, os '// df: permitir <regra>' sao
    lidos sem tocar o disco — o que importa para o LSP, que reanalisa
    a cada tecla e tem o texto do editor, ainda nao salvo.
    """
    verificador = TypeChecker(filename=filename, strict=strict, source=source)
    return verificador.check(program)
