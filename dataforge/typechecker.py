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
    #: O decimal EXATO — o tipo de '19.99d' e de 'Dec.de("19.99")'.
    #: Sem ele aqui, o literal tinha tipo e nao tinha como ser
    #: ANOTADO: 'x: Decimal := 19.99d' dizia "Unknown type".
    "decimal": "Decimal", "Decimal": "Decimal",
    "number": "Number", "Number": "Number",
    "string": "String", "str": "String", "text": "String", "String": "String",
    "boolean": "Boolean", "bool": "Boolean", "Boolean": "Boolean",
    "cluster": "Cluster", "list": "Cluster", "array": "Cluster", "Cluster": "Cluster",
    "vault": "Vault", "dict": "Vault", "map": "Vault", "Vault": "Vault",
    "void": "Void", "none": "Void", "Void": "Void",
    "action": "Action", "function": "Action", "Action": "Action",
    "stream": "Stream", "Stream": "Stream",
    "tuple": "Tuple", "Tuple": "Tuple",
    #: O conjunto: '{1, 2}', 'set(xs)'. O 'typeof' já respondia "Set", e
    #: a anotação 'x: Set' dizia "Unknown type" — o tipo existia em
    #: execução e não tinha nome para quem escreve.
    "set": "Set", "Set": "Set",
    "any": ANY, "Any": ANY,
}


def canonical(nome: str) -> str:
    if "<" in nome:
        base, argumentos = partir_tipo(nome)
        return juntar_tipo(ALIASES.get(base, base),
                           [canonical(a) for a in argumentos])
    return ALIASES.get(nome, nome)


class _SemValor:
    """O que este módulo devolve quando NÃO conseguiu decidir.

    'None' não serve: 'void' é um valor legítimo da linguagem, e
    confundir "não sei" com "vale void" faria o analisador acusar código
    certo — que é o pior defeito que ele pode ter.
    """

    def __repr__(self):                                    # pragma: no cover
        return "<sem valor>"


_SEM_VALOR = _SemValor()

#: As funções que a prova de um refinamento pode chamar. É uma lista
#: FECHADA: a regra é código de quem escreveu, e o analisador não pode
#: executar código arbitrário para decidir se acusa ou cala.
_PURAS = {
    "len": len, "abs": abs, "min": min, "max": max, "round": round,
    "sum": sum, "int": int, "float": float, "str": str,
    "upper": lambda t: t.upper(), "lower": lambda t: t.lower(),
}

_ARITMETICA = {
    "+": lambda a, b: a + b, "-": lambda a, b: a - b,
    "*": lambda a, b: a * b, "/": lambda a, b: a / b,
    "%": lambda a, b: a % b, "**": lambda a, b: a ** b,
    "~/": lambda a, b: a // b,
}

_ORDEM = {
    "is": lambda a, b: a == b, "isnt": lambda a, b: a != b,
    "bigger": lambda a, b: a > b, "smaller": lambda a, b: a < b,
    "bigger_eq": lambda a, b: a >= b, "smaller_eq": lambda a, b: a <= b,
}


def valor_constante(no):
    """O valor de um literal, ou `_SEM_VALOR`. Nada é executado aqui."""
    if isinstance(no, ast.IntegerLiteral) or isinstance(no, ast.FloatLiteral) \
            or isinstance(no, ast.StringLiteral):
        return no.value
    if isinstance(no, ast.BooleanLiteral):
        return bool(no.value)
    if isinstance(no, ast.VoidLiteral):
        return None
    if isinstance(no, ast.UnaryOp) and no.op == "-":
        interno = valor_constante(no.operand)
        return _SEM_VALOR if interno is _SEM_VALOR else -interno
    if isinstance(no, ast.ListLiteral):
        itens = [valor_constante(i) for i in no.elements]
        return _SEM_VALOR if any(i is _SEM_VALOR for i in itens) else itens
    if isinstance(no, ast.DictLiteral):
        pares = {}
        for chave, valor in no.pairs:
            k, v = valor_constante(chave), valor_constante(valor)
            if k is _SEM_VALOR or v is _SEM_VALOR or isinstance(k, (list, dict)):
                return _SEM_VALOR
            pares[k] = v
        return pares
    return _SEM_VALOR


def avaliar_puro(no, ambiente):
    """A regra de um refinamento sobre um valor conhecido.

    Só entende o que é PURO — literal, nome do ambiente, conta,
    comparação, 'and'/'or'/'not', índice e as funções de `_PURAS`.
    Qualquer outra coisa devolve `_SEM_VALOR`, e o analisador cala.
    """
    constante = valor_constante(no)
    if constante is not _SEM_VALOR:
        return constante
    if isinstance(no, ast.Identifier):
        return ambiente.get(no.name, _SEM_VALOR)
    if isinstance(no, ast.NotOp):
        interno = avaliar_puro(no.operand, ambiente)
        return _SEM_VALOR if interno is _SEM_VALOR else not interno
    if isinstance(no, ast.LogicalOp):
        esquerda = avaliar_puro(no.left, ambiente)
        if esquerda is _SEM_VALOR:
            return _SEM_VALOR
        if no.op == "and" and not esquerda:
            return esquerda
        if no.op == "or" and esquerda:
            return esquerda
        return avaliar_puro(no.right, ambiente)
    if isinstance(no, (ast.BinaryOp, ast.ComparisonOp)):
        esquerda = avaliar_puro(no.left, ambiente)
        direita = avaliar_puro(no.right, ambiente)
        if esquerda is _SEM_VALOR or direita is _SEM_VALOR:
            return _SEM_VALOR
        operacao = (_ORDEM if isinstance(no, ast.ComparisonOp)
                    else _ARITMETICA).get(no.op)
        if operacao is None:
            return _SEM_VALOR
        try:
            return operacao(esquerda, direita)
        except Exception:                                  # noqa: BLE001
            # Comparar texto com número, dividir por zero: quem decide
            # isso é a execução, com a mensagem dela.
            return _SEM_VALOR
    if isinstance(no, ast.IndexAccess):
        alvo = avaliar_puro(no.object, ambiente)
        indice = avaliar_puro(no.index, ambiente)
        if alvo is _SEM_VALOR or indice is _SEM_VALOR:
            return _SEM_VALOR
        try:
            return alvo[indice]
        except Exception:                                  # noqa: BLE001
            return _SEM_VALOR
    if isinstance(no, ast.FunctionCall) and isinstance(no.callee, ast.Identifier):
        funcao = _PURAS.get(no.callee.name)
        if funcao is None or no.kwargs:
            return _SEM_VALOR
        argumentos = [avaliar_puro(a, ambiente) for a in no.args]
        if any(a is _SEM_VALOR for a in argumentos):
            return _SEM_VALOR
        try:
            return funcao(*argumentos)
        except Exception:                                  # noqa: BLE001
            return _SEM_VALOR
    return _SEM_VALOR


def _e_numero(texto):
    """'3' e '2.5' são valores; 'Integer' é um tipo."""
    try:
        float(str(texto).strip())
        return True
    except ValueError:
        return False


def _como_texto(valor):
    """O valor na mensagem, no vocabulário da linguagem."""
    if valor is None:
        return "void"
    if valor is True:
        return "yes"
    if valor is False:
        return "no"
    return repr(valor) if isinstance(valor, str) else str(valor)


def base_do_tipo(nome: str) -> str:
    """'Cluster<Integer>' -> 'Cluster'. O resto das conferencias fala da base."""
    return partir_tipo(nome)[0] if "<" in nome else nome


def compatible(esperado: str, obtido: str) -> bool:
    """O valor de tipo 'obtido' serve onde se espera 'esperado'?"""
    if UNKNOWN in (esperado, obtido) or ANY in (esperado, obtido):
        return True
    if "<" in esperado or "<" in obtido:
        # A base decide. O conteudo so decide quando OS DOIS lados o
        # conhecem: 'Cluster' sozinho e um cluster de conteudo que nao se
        # sabe, e acusa-lo seria o falso alarme de sempre.
        be, ae = partir_tipo(esperado)
        bo, ao = partir_tipo(obtido)
        if not compatible(be, bo):
            return False
        if ae and ao and len(ae) == len(ao):
            return all(compatible(x, y) for x, y in zip(ae, ao))
        return True
    if esperado == obtido:
        return True
    if esperado == "Number":
        return obtido in ("Integer", "Float", "Number")
    if esperado == "Float" and obtido == "Integer":
        return True          # um inteiro serve onde se espera decimal
    return False


from .colecoes_tipadas import partir as partir_tipo, juntar as juntar_tipo  # noqa: E402
from .tipos_nomeados import separar_uniao  # noqa: E402


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
        # O desenho fala o idioma em vigor; 'self.message' fica como
        # nasceu, que e o que a suite e as ferramentas comparam.
        from .idioma import traduzir
        cabecalho = (f"{filename}:{self.line}:{self.column}: {rotulo}: "
                     f"{traduzir(self.message)}")
        if self.hint:
            cabecalho += f"\n    sugestão: {traduzir(self.hint)}"
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
                 'is_generator', 'line', 'type_params', 'type_bounds')

    def __init__(self, decl):
        self.name = decl.name
        self.params = list(decl.params)
        self.defaults = set(decl.defaults or {})
        self.param_types = dict(getattr(decl, 'param_types', {}) or {})
        self.return_type = canonical(getattr(decl, 'return_type', '') or UNKNOWN)
        # Um DECORADOR substitui a acao, e com ela o tipo que volta. O
        # '-> String' de 'eco' continua escrito, e 'mark @repetir(3)' faz
        # a chamada devolver um Cluster: o tipo declarado deixa de ser
        # promessa e passa a ser historia.
        #
        # 'trilha/17' tem exatamente esse caso, e 'eco("oi") is
        # ["oi","oi","oi"]' PASSA em execucao — era o analisador que
        # estava errado ao dizer que a comparacao nunca da certo.
        #
        # Nao ha como saber qual decorador substitui: um que devolve
        # 'void' nao substitui nada (e o que permite '@Rota("/x")' so
        # anotar), e um que devolve acao substitui. Diante de duas
        # respostas possiveis, o analisador cala.
        if getattr(decl, 'decorators', None):
            self.return_type = UNKNOWN
        #: '<T>' e '<T extends X>'. Um 'T' NAO e um tipo: e um lugar para
        #: um. Tratado como nome de tipo, 'eco<T>(x: T)' chamado com um
        #: texto era acusado de "espera T, e recebeu String" — em TODA
        #: chamada de todo generico com parametro do tipo T.
        self.type_params = set(getattr(decl, 'type_params', None) or ())
        self.type_bounds = dict(getattr(decl, 'type_bounds', None) or {})
        if self.return_type in self.type_params:
            # 'primeiro<T>(l) -> T' devolve o que entrou, e o analisador
            # nao acompanha qual T foi: o limite, se houver, e o que se
            # sabe com certeza; sem limite, nada.
            self.return_type = canonical(
                self.type_bounds.get(self.return_type) or UNKNOWN)
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
        #: Os METODOS de cada record, separados dos campos.
        #:
        #: Separados porque 'self.records' governa outras tres coisas: a
        #: aridade do construtor, os nomes aceitos por 'P(x := 1)' e as
        #: chaves aceitas por 'p with {…}'. Um metodo no mesmo dicionario
        #: faria 'P(norma := 1)' e 'p with {"norma": 1}' passarem, que e
        #: trocar um falso alarme por um silencio — pior troca.
        self.record_methods = {}  # nome -> set(metodos)
        #: nome -> ('Cluster', tamanho) | ('Vault', {chaves})
        self._literais_fixos = {}
        #: trait -> os metodos que ele EXIGE (declarados sem corpo).
        #: Um metodo com corpo e implementacao padrao, e nao exigencia.
        self.trait_exigidos = {}
        #: Dentro do lado esquerdo de um '??', onde a chave
        #: ausente e legitima — ver 'ex_CoalesceOp'.
        self._sob_coalesce = 0
        self.record_defaults = {}
        self.enums = {}          # nome -> [membros]
        self.blueprints = {}     # nome -> set(membros proprios)
        self.tipos_de_campo = {}  # blueprint -> {campo: tipo declarado}
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
        #: apelido -> nome do módulo, para saber de onde veio 'P.dono(…)'
        self.modulos_adotados = {}
        #: Um ciclo e uma propriedade do ARQUIVO, nao de cada 'adopt'.
        #: Sem esta marca, um arquivo com cinco imports repetiria a
        #: mesma mensagem cinco vezes.
        self._ciclo_relatado = False
        self.known_types = set(ALIASES.values())
        #: Os 'type' declarados: nome -> o nó da declaração. Serve para
        #: resolver a anotação, provar o literal e recusar o ciclo.
        self.tipos_nomeados = {}
        #: nome -> (parametros, limites) de record, enum, trait e blueprint
        #: genéricos. É o que distingue 'T documenta' de '<T extends X>
        #: cobra'.
        self.genericos_de_tipo = {}
        #: Posse: nome -> a linha em que foi movido. Enquanto estiver
        #: aqui, usar o nome é usar o que já não se tem. Reatribuir o
        #: nome limpa a marca — a partir dali ele é outro valor.
        self.posse_movida = {}
        #: nome -> o nó que criou o recurso, enquanto ninguém o soltou,
        #: moveu, devolveu nem passou adiante.
        self.recursos_abertos = {}
        #: Os nomes que NASCERAM de 'Arcane.Posse' nesta ação. Só eles
        #: entram na conta: um blueprint com um método chamado 'mover'
        #: não tem nada a ver com posse, e acusá-lo seria o falso alarme
        #: que ensina a desligar o analisador.
        self.posse_criada = set()
        # Os '<T>' do blueprint que esta sendo analisado. Um metodo dele
        # pode usa-los como tipo; fora dali, eles nao existem.
        self._genericos_do_blueprint = set()
        self._genericos_da_acao = set()
        self._limites_do_blueprint = {}
        #: Blueprints 'abstract' deste arquivo — a raiz de uma hierarquia
        #: que o 'match' pode conferir por completo.
        self.abstratos = set()
        # ── OOP 1.2 ──
        #: 'final blueprint', 'sealed blueprint', 'meta blueprint', 'contract'
        self.finais = set()
        self.selados = set()
        self.metas = set()
        self.contratos = set()
        #: blueprint -> {metodo: ActionSignature} — o que um override confere
        self.assinaturas_de_metodo = {}
        #: blueprint -> campos 'readonly'
        self.somente_leitura = {}
        #: acoes de topo com 'overload' — a aridade de uma nao vale para a outra
        self.sobrecarregadas = set()
        #: blueprints cujo membro pode nascer em execucao: '__getattr__',
        #: '__getattribute__', ou governados por metaclasse
        self.dinamicos = set()
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
        #: O que a LINGUAGEM pos no escopo global, e nao quem escreve.
        #: Serve para nao confundir uma variavel local que sombreia uma
        #: embutida com estado compartilhado — ver '_so_e_embutida'.
        self._nomes_da_linguagem = set(builtins)
        for nome in builtins:
            self.global_scope.declare(nome, ANY)
        for extra in ("self", "this", "root", "__file__", "__name__", "error"):
            self.global_scope.declare(extra, ANY)
            self._nomes_da_linguagem.add(extra)

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
        self._recolher_literais_fixos(program)
        self._avisar_declaracao_repetida(program.body)
        self.visit_block(program.body, escopo)
        return self._sem_os_silenciados(program)

    #: Os nós que declaram um nome no topo do arquivo.
    _DECLARAM_NOME = ("ActionDeclaration", "RecordDeclaration",
                      "BlueprintDeclaration", "EnumDeclaration",
                      "TraitDeclaration", "ContractDeclaration")

    def _avisar_declaracao_repetida(self, corpo):
        """Duas declarações com o mesmo nome no topo do mesmo arquivo.

        A segunda vence, e a primeira não tem como ser alcançada — é
        engano de copiar e colar, e num arquivo de mil linhas as duas
        ficam longe uma da outra. O campo repetido de um `record` e o
        membro repetido de um `enum` já eram acusados; a declaração
        inteira, não.

        É **aviso**, e não erro, por duas razões: o Python aceita calado,
        então quem chega de lá não está fazendo nada exótico; e um arquivo
        gerado pode legitimamente redeclarar. Mas o aviso é o suficiente
        para achar o engano.

        Só o **topo** do arquivo. Dentro de um ramo de `given`, declarar o
        mesmo nome nos dois caminhos é como se escolhe a implementação, e
        acusar isso proibiria o uso certo.
        """
        onde = {}
        for no in corpo or []:
            if type(no).__name__ not in self._DECLARAM_NOME:
                continue
            nome = getattr(no, "name", "")
            if not nome:
                continue
            if getattr(no, "is_overload", False) and nome in self.sobrecarregadas:
                # 'overload action f' declarado duas vezes e o recurso, e nao
                # engano: cada declaracao e uma variante
                continue
            if nome in onde:
                self.warn(
                    f"'{nome}' já foi declarado na linha {onde[nome]}",
                    no, "a segunda declaração vence, e a primeira não tem "
                        "como ser alcançada", "declaracao-repetida")
            else:
                onde[nome] = no.line

    # ── o que um literal garante ────────────────────────────

    #: Os metodos que mudam o TAMANHO ou as CHAVES de uma colecao.
    #:
    #: Lista propria, e nao a `_MUTAM` do aviso de concorrencia: aquela
    #: exclui `append` de proposito, porque o GIL protege a operacao
    #: inteira e avisar sobre ela seria falso alarme. Aqui `append`
    #: importa — ele muda o tamanho, e um `xs[3]` que era erro deixa de
    #: ser. As duas listas respondem perguntas diferentes, e fundi-las
    #: estragaria uma das duas.
    _MUDAM_O_TAMANHO = frozenset({
        "append", "push", "extend", "insert", "remove", "pop", "clear",
        "delete", "discard", "update", "merge_in", "setdefault",
        "sort", "reverse", "shuffle", "add",
    })

    def _recolher_literais_fixos(self, program):
        """Quais nomes guardam um literal que ninguem mexe.

        Com isso, `xs := [1, 2, 3]` seguido de `xs[10]` e um erro
        DEMONSTRAVEL, e nao um palpite. Sem isso, o indice fora do
        alcance so aparece quando aquela linha executa — e num ramo raro
        isso significa producao.

        A coleta e por NOME e vale para o arquivo inteiro, o que e
        conservador na direcao certa: se o nome e reusado em outro escopo,
        o fato cai, e a conferencia cala. Provar por escopo exigiria
        acompanhar o fluxo, e um analisador que erra aqui acusa codigo
        que funciona.

        O nome perde a garantia se QUALQUER destas coisas acontece em
        qualquer lugar do arquivo:

        | o que | por que |
        |---|---|
        | recebe valor duas vezes | o segundo pode ter outro tamanho |
        | e passado como argumento | quem recebe pode mexer nele |
        | chamam nele um metodo que muda o tamanho | deixa de ser o literal |
        | escrevem num indice ou chave dele | idem para vault |
        | e nome de parametro, ou variavel de laco | o valor vem de fora |
        """
        vezes = {}
        literal = {}
        perdidos = set()

        def marcar(no):
            if isinstance(no, ast.Identifier):
                perdidos.add(no.name)

        def andar(no):
            if isinstance(no, ast.Assignment):
                alvo = no.target
                if isinstance(alvo, ast.Identifier):
                    vezes[alvo.name] = vezes.get(alvo.name, 0) + 1
                    if getattr(no, "compound_op", None):
                        perdidos.add(alvo.name)
                    elif isinstance(no.value, (ast.ListLiteral, ast.DictLiteral)):
                        literal[alvo.name] = no.value
                else:
                    # 'xs[0] := …' e 'v["k"] := …' mudam o conteudo.
                    base = alvo
                    while isinstance(base, (ast.IndexAccess, ast.MemberAccess)):
                        base = getattr(base, "object", None)
                    marcar(base)

            # Passar adiante e abrir mao da garantia.
            for campo in ("args", "elements", "values"):
                for item in (getattr(no, campo, None) or []):
                    alvo = getattr(item, "value", item)
                    marcar(alvo)
            for valor in (getattr(no, "kwargs", None) or {}).values():
                marcar(valor)

            if isinstance(no, ast.MethodCall) and \
                    no.method in self._MUDAM_O_TAMANHO:
                base = no.object
                while isinstance(base, (ast.IndexAccess, ast.MemberAccess)):
                    base = getattr(base, "object", None)
                marcar(base)

            # Nome que vem de fora nunca e o literal daqui.
            for campo in ("params", "vars"):
                for nome in (getattr(no, campo, None) or []):
                    if isinstance(nome, str):
                        perdidos.add(nome)
            for campo in ("var", "name"):
                valor = getattr(no, campo, None)
                if isinstance(valor, str) and isinstance(
                        no, (ast.CycleIn, ast.CycleFromTo)):
                    perdidos.add(valor)

            for filho in self._filhos(no):
                andar(filho)

        andar(program)

        for nome, no in literal.items():
            if vezes.get(nome) != 1 or nome in perdidos:
                continue
            if isinstance(no, ast.ListLiteral):
                # Um spread torna o tamanho desconhecido.
                if any(isinstance(e, ast.SpreadElement) for e in no.elements):
                    continue
                self._literais_fixos[nome] = ("Cluster", len(no.elements))
            else:
                chaves = set()
                for chave, _ in no.pairs:
                    if not isinstance(chave, ast.StringLiteral):
                        chaves = None
                        break
                    chaves.add(chave.value)
                if chaves is None:
                    continue      # chave calculada: nao sei quais existem
                self._literais_fixos[nome] = ("Vault", chaves)

    @staticmethod
    def _filhos(no):
        """Os nós filhos, sem saber o nome de cada campo.

        Uma lista de campos por tipo de nó apodreceria: um recurso novo na
        linguagem deixaria de ser varrido, e a falta não dá erro — só faz
        a garantia valer onde não devia.
        """
        import dataclasses

        if not dataclasses.is_dataclass(no):
            return
        for campo in dataclasses.fields(no):
            valor = getattr(no, campo.name, None)
            if isinstance(valor, ast.ASTNode):
                yield valor
            elif isinstance(valor, (list, tuple)):
                for item in valor:
                    if isinstance(item, ast.ASTNode):
                        yield item
                    elif isinstance(item, (list, tuple)):
                        for dentro in item:
                            if isinstance(dentro, ast.ASTNode):
                                yield dentro
            elif isinstance(valor, dict):
                for item in valor.values():
                    if isinstance(item, ast.ASTNode):
                        yield item

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
                    if getattr(stmt, "is_overload", False) or \
                            stmt.name in self.sobrecarregadas:
                        # a aridade de uma variante nao vale para a outra;
                        # a chamada e conferida em execucao, pela resolucao
                        self.sobrecarregadas.add(stmt.name)
                        self.actions.pop(stmt.name, None)
                    else:
                        self.actions[stmt.name] = ActionSignature(stmt)
                escopo.declare(stmt.name, "Action", stmt.line, stmt.column)
            elif isinstance(stmt, ast.ContractDeclaration):
                exigidos = {m.name for m in stmt.members}
                self.blueprints[stmt.name] = set(exigidos)
                self.trait_exigidos[stmt.name] = set(exigidos)
                self.contratos.add(stmt.name)
                self.maes[stmt.name] = list(stmt.parents or [])
                self.assinaturas_de_metodo[stmt.name] = {
                    m.name: ActionSignature(m) for m in stmt.members
                    if isinstance(m, ast.ActionDeclaration)}
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Blueprint", stmt.line, stmt.column)
            elif isinstance(stmt, ast.AugmentDeclaration):
                if stmt.name in self.blueprints:
                    self.blueprints[stmt.name] |= self._membros_de(stmt)
            elif isinstance(stmt, ast.RecordDeclaration):
                self.records[stmt.name] = {c: canonical(t) for c, t, _ in stmt.fields}
                self.genericos_de_tipo[stmt.name] = (
                    tuple(getattr(stmt, "type_params", ()) or ()),
                    dict(getattr(stmt, "type_bounds", None) or {}))
                self.record_methods[stmt.name] = set(stmt.methods or ())
                self.record_defaults[stmt.name] = {c for c, _, d in stmt.fields if d is not None}
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Record", stmt.line, stmt.column)
            elif isinstance(stmt, ast.TypeDeclaration):
                # O nome existe a partir daqui, e a ordem no arquivo não
                # importa: um 'type' declarado embaixo é usado em cima.
                self.tipos_nomeados.setdefault(stmt.name, stmt)
                self.known_types.add(stmt.name)
            elif isinstance(stmt, ast.EnumDeclaration):
                self.enums[stmt.name] = [m for m, _ in stmt.members]
                self.genericos_de_tipo[stmt.name] = (
                    tuple(getattr(stmt, "type_params", ()) or ()),
                    dict(getattr(stmt, "type_bounds", None) or {}))
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Enum", stmt.line, stmt.column)
            elif isinstance(stmt, (ast.BlueprintDeclaration, ast.TraitDeclaration)):
                self.blueprints[stmt.name] = self._membros_de(stmt)
                self.genericos_de_tipo[stmt.name] = (
                    tuple(getattr(stmt, "type_params", ()) or ()),
                    dict(getattr(stmt, "type_bounds", None) or {}))
                if isinstance(stmt, ast.TraitDeclaration):
                    # Sem corpo = exigencia; com corpo = implementacao
                    # padrao, que o blueprint herda e nao precisa escrever.
                    self.trait_exigidos[stmt.name] = {
                        m.name for m in stmt.methods
                        if isinstance(m, ast.ActionDeclaration) and not m.body}
                if isinstance(stmt, ast.BlueprintDeclaration) and \
                        getattr(stmt, "is_abstract", False):
                    self.abstratos.add(stmt.name)
                if isinstance(stmt, ast.BlueprintDeclaration):
                    self.maes[stmt.name] = [
                        p if isinstance(p, str) else getattr(p, "name", "")
                        for p in (list(stmt.parents or [])
                                  + list(stmt.traits or []))]
                    if getattr(stmt, "is_final", False):
                        self.finais.add(stmt.name)
                    if getattr(stmt, "is_sealed", False):
                        self.selados.add(stmt.name)
                    if getattr(stmt, "is_meta", False):
                        self.metas.add(stmt.name)
                    # Um blueprint DECORADO pode ganhar qualquer membro:
                    # 'mark @M.derivar(…)' gera '__str__' e 'para_vault' na
                    # carga, e o analisador não tem como vê-los. Calar aqui
                    # é a mesma regra do blueprint que herda de algo não
                    # visto — acusar seria falso alarme em código que roda.
                    if getattr(stmt, "metaclass", "") \
                            or getattr(stmt, "decorators", None) \
                            or any(isinstance(m, ast.ActionDeclaration)
                                   and m.name in ("__getattr__", "__getattribute__")
                                   for m in stmt.body):
                        self.dinamicos.add(stmt.name)
                    self.assinaturas_de_metodo[stmt.name] = {
                        m.name: ActionSignature(m) for m in stmt.body
                        if isinstance(m, ast.ActionDeclaration)
                        and not getattr(m, "is_overload", False)}
                    self.somente_leitura[stmt.name] = {
                        n for n, mods in (getattr(stmt, "field_modifiers", None) or {}).items()
                        if "readonly" in mods}
                    # campo -> tipo DECLARADO. 'self.blueprints' guarda só
                    # os NOMES, e com eles não dá para saber que o
                    # 'guardado' de um 'Caixa<T>' é o T — que é o que
                    # permite acusar 'c.guardado := "texto"' antes de
                    # rodar. O interpretador já lia os mesmos dois
                    # lugares (ver '_tipos_de_campo_do_molde').
                    campos_tipados = dict(
                        getattr(stmt, "tipos_do_cabecalho", None) or {})
                    for declarado in (stmt.fields_decl or ()):
                        if isinstance(declarado, (list, tuple)) \
                                and len(declarado) >= 2 and declarado[1]:
                            campos_tipados[declarado[0]] = declarado[1]
                    self.tipos_de_campo[stmt.name] = campos_tipados
                self.known_types.add(stmt.name)
                escopo.declare(stmt.name, "Blueprint", stmt.line, stmt.column)
        # Um trait que herda de outro leva os membros e as exigencias dele.
        # Numa segunda passada: a mae pode estar declarada depois.
        for stmt in statements:
            if isinstance(stmt, ast.TraitDeclaration):
                for mae in getattr(stmt, "parents", None) or []:
                    self.blueprints[stmt.name] = (
                        self.blueprints.get(stmt.name, set())
                        | self.blueprints.get(mae, set()))
                    self.trait_exigidos[stmt.name] = (
                        self.trait_exigidos.get(stmt.name, set())
                        | self.trait_exigidos.get(mae, set()))
                    self.maes.setdefault(stmt.name, []).append(mae)
        for stmt in statements:
            if isinstance(stmt, ast.AugmentDeclaration) and stmt.name in self.blueprints:
                self.blueprints[stmt.name] |= self._membros_de(stmt)

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
        corpo = (stmt.body if isinstance(stmt, (ast.BlueprintDeclaration,
                                                ast.AugmentDeclaration))
                 else stmt.methods)

        for sub in corpo:
            if isinstance(sub, (ast.ActionDeclaration, ast.StaticDeclaration,
                                ast.PropertyDeclaration, ast.BlueprintDeclaration,
                                ast.RecordDeclaration, ast.EnumDeclaration,
                                ast.ContractDeclaration, ast.TraitDeclaration,
                                ast.TypeDeclaration)):
                # 'type Item := Integer' e um membro: 'Fila.Item' responde.
                membros.add(sub.name)
            elif isinstance(sub, ast.Assignment) and \
                    isinstance(sub.target, ast.Identifier):
                # 'porta := 80' solto no corpo e um CAMPO com padrao — o
                # interpretador o trata assim desde que deixou de virar
                # estatico, e o analisador nao tinha acompanhado
                membros.add(sub.target.name)

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

    def _membros_implementados(self, nome, vistos=None):
        """Os membros que existem DE FATO na linhagem.

        Diferente de `_membros_com_heranca` num ponto só, e o ponto é
        tudo: o método abstrato de um trait **não** conta. Para
        `p.desserializar` ele conta — o trait promete que o membro existe,
        e quem escreve pode chamá-lo. Para o contrato, contar a promessa
        como cumprimento faz a conferência aprovar exatamente o que ela
        deveria recusar, e foi o primeiro jeito que escrevi.
        """
        vistos = vistos or set()
        if nome in vistos or nome not in self.blueprints:
            return set()
        vistos.add(nome)

        proprios = set(self.blueprints[nome])
        # Num trait, o que não tem corpo é exigência, e não implementação.
        proprios -= self.trait_exigidos.get(nome, set())
        for mae in self.maes.get(nome, ()):
            proprios |= self._membros_implementados(mae, vistos)
        return proprios

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

    def _nome_do_alvo(self, node):
        alvo = getattr(node, "target", None)
        return getattr(alvo, "name", "") or "the value"

    def _acusar_tipo(self, declarado, obtido, node, o_que):
        """A mensagem certa para o tipo certo — e o código que se silencia."""
        partes = self._partes_do_tipo(declarado)
        if partes is None:
            self.error(
                f"Declared as {declarado} but the value is {obtido}", node,
                f"Change the annotation to {obtido} or fix the value",
                "type-mismatch")
            return
        especie, nomes, opaco = partes
        if opaco:
            self.error(
                f"{o_que} declared as {declarado} but the value is {obtido}",
                node, f"{declarado} is opaque — build it with {declarado}(…)",
                "tipo-opaco")
        elif especie == "uniao":
            self.error(
                f"{o_que} declared as {declarado} ({' | '.join(nomes)}) but "
                f"the value is {obtido}", node,
                f"Pass one of: {' | '.join(nomes)}", "tipo-uniao")
        elif especie == "intersecao":
            self.error(
                f"{o_que} declared as {declarado} ({' & '.join(nomes)}) but "
                f"the value is {obtido}", node,
                f"{obtido} has to be all of: {' & '.join(nomes)}",
                "tipo-intersecao")
        else:
            self.error(
                f"{o_que} declared as {declarado} (a {nomes[0]}) but the "
                f"value is {obtido}", node,
                f"Change the annotation to {obtido} or fix the value",
                "type-mismatch")

    def _provar_nomeado(self, declarado, valor, escopo, o_que):
        """A regra de um refinamento, sobre um literal — antes de rodar."""
        declaracao = self._declaracao_de_tipo(declarado)
        if declaracao is None or declaracao.regra is None:
            return
        self._provar_regra(declaracao, valor, escopo, o_que,
                           self._ligacoes_do_tipo(declaracao, declarado))

    def _ligacoes_do_tipo(self, declaracao, usado):
        """'Vetor<3>' — o que cada parâmetro vale aqui.

        Um argumento que é NÚMERO entra na prova como número: é o que faz
        o `check` acusar 'Vetor<3> := [1.0, 2.0]' antes de rodar.
        """
        parametros = tuple(getattr(declaracao, "type_params", ()) or ())
        if not parametros or "<" not in str(usado):
            return {}
        ligacoes = {}
        for parametro, argumento in zip(parametros, partir_tipo(usado)[1]):
            texto = argumento.strip()
            try:
                ligacoes[parametro] = int(texto)
            except ValueError:
                try:
                    ligacoes[parametro] = float(texto)
                except ValueError:
                    continue
        return ligacoes

    def _provar_regra(self, declaracao, valor, escopo, o_que, ligacoes=None):
        constante = valor_constante(valor)
        if constante is _SEM_VALOR:
            return
        ambiente = {"valor": constante}
        ambiente.update(ligacoes or {})
        resposta = avaliar_puro(declaracao.regra, ambiente)
        if resposta is _SEM_VALOR or resposta:
            return
        self.error(
            f"{o_que} declared as {declaracao.name}, and "
            f"{_como_texto(constante)} breaks its rule: "
            f"{declaracao.regra_texto}", valor,
            f"{declaracao.name} is a {declaracao.partes[0]} where "
            f"{declaracao.regra_texto}", "tipo-refinado")

    def st_ComptimeBlock(self, node, escopo):
        """'comptime' roda na CARGA — então o `check` já pode rodá-lo.

        É o que transforma uma validação de `comptime` em erro **antes**
        de o programa começar: `assert len(TABELA) is 3` com dois itens
        falha aqui, e não na primeira execução em produção.
        """
        self.visit_block(node.body, escopo)
        self._rodar_comptime_no_check(node)
        return False

    def _rodar_comptime_no_check(self, node):
        from .interpreter import Interpreter
        from .errors import DataForgeError
        interpretador = getattr(self, "_comptime", None)
        if interpretador is None:
            interpretador = self._comptime = Interpreter()
            interpretador.compilar_corpos = False
        try:
            interpretador.exec_ComptimeBlock(node, interpretador.global_env)
        except DataForgeError as erro:
            self.error(
                getattr(erro, "message", str(erro)), node,
                "o 'comptime' roda na carga: conserte a conta, ou tire o "
                "'comptime' se ela precisa de dado de execução",
                "comptime-falhou")
        except Exception:                                   # noqa: BLE001
            # Um comptime que quebra de forma inesperada não pode
            # derrubar o analisador: ele acusa e segue.
            self.error(
                "o 'comptime' não pôde ser calculado aqui", node,
                "rode o arquivo para ver o erro completo", "comptime-falhou")

    def st_TypeDeclaration(self, node, escopo):
        """'type Nome := …' — o nome existe, as partes existem, e não há ciclo."""
        anterior = self.tipos_nomeados.get(node.name)
        # Dentro de um trait ou blueprint, 'type Item := …' é um membro
        # ASSOCIADO: ele existe justamente para ser preenchido por quem
        # implementa, e acusar isso proibiria o recurso.
        if self._em_membro:
            self.tipos_nomeados.setdefault(node.name, node)
            self.known_types.add(node.name)
            return False
        if anterior is not None and anterior is not node:
            self.error(
                f"Type '{node.name}' is declared twice in this file", node,
                "The second declaration is the one that runs — rename one",
                "declaracao-repetida")
        self.tipos_nomeados[node.name] = node
        self.known_types.add(node.name)

        genericos = tuple(node.type_params or ())
        for parte in node.partes:
            falta = self._tipo_desconhecido(parte, genericos)
            if falta and falta != node.name:
                self.error(
                    f"Unknown type '{falta}' in 'type {node.name}'", node,
                    self._hint_tipo(falta), "unknown-type")
        cadeia = self._ciclo_de_tipo(node.name)
        if cadeia:
            self.error(
                f"Type '{node.name}' is defined in terms of itself: "
                f"{' → '.join(cadeia)}", node,
                "A type needs a concrete base — break the chain with a "
                "record, a blueprint or a builtin type",
                "tipo-circular")
        if node.regra is not None:
            escopo_da_regra = Scope(escopo)
            escopo_da_regra.declare("valor", canonical(node.partes[0]),
                                    node.line, node.column)
            # 'type Vetor<N> := … where len(valor) is N' — o parâmetro é
            # um nome comum dentro da regra, e vale o que a anotação
            # passar ('Vetor<3>').
            for parametro in node.type_params or ():
                escopo_da_regra.declare(parametro, UNKNOWN,
                                        node.line, node.column)
            self.infer(node.regra, escopo_da_regra)
        return False

    def _ciclo_de_tipo(self, nome, vistos=None):
        """A cadeia 'A → B → A', ou vazio. Em largura: a mais curta."""
        vistos = vistos or []
        if nome in vistos:
            return vistos + [nome]
        declaracao = self.tipos_nomeados.get(nome)
        if declaracao is None:
            return []
        for parte in declaracao.partes:
            base = partir_tipo(canonical(parte))[0] if "<" in parte else parte
            achado = self._ciclo_de_tipo(base, vistos + [nome])
            if achado:
                return achado
        return []

    def st_Assignment(self, node, escopo):
        tipo = self.infer(node.value, escopo)
        self._anotar_recurso(node, escopo)
        declarado = canonical(getattr(node, 'declared_type', '') or '')

        if declarado:
            falta = self._tipo_desconhecido(declarado)
            if falta:
                self.error(
                    f"Unknown type '{falta}'"
                    + (f" in '{node.declared_type}'" if falta != node.declared_type else ""),
                    node, self._hint_tipo(falta), "unknown-type")
            elif base_do_tipo(declarado) == "Tuple" and \
                    isinstance(node.value, ast.TupleLiteral):
                # A tupla literal é conferida PELA POSIÇÃO: "o lugar 0 é
                # String" diz onde corrigir, e "o valor é
                # Tuple<String, Integer>" manda comparar de cabeça.
                self._conferir_conteudo(declarado, node.value, escopo)
            elif not self._compativel(declarado, tipo):
                self._acusar_tipo(declarado, tipo, node.value or node,
                                  f"variable '{self._nome_do_alvo(node)}'")
            else:
                self._conferir_conteudo(declarado, node.value, escopo)
                self._provar_nomeado(declarado, node.value, escopo,
                                     f"variable '{self._nome_do_alvo(node)}'")

        # 'xs[0] := "x"' num Cluster<Integer> conhecido
        if isinstance(node.target, ast.IndexAccess) and \
                isinstance(node.target.object, ast.Identifier):
            do_alvo = escopo.lookup(node.target.object.name)
            if isinstance(do_alvo, str) and "<" in do_alvo:
                base, argumentos = partir_tipo(do_alvo)
                if base == "Cluster":
                    self._conferir_item(argumentos[0], node.value, escopo,
                                        do_alvo, "the assigned item")
                elif base == "Vault":
                    self._conferir_item(argumentos[0], node.target.index, escopo,
                                        do_alvo, "the key")
                    self._conferir_item(argumentos[1], node.value, escopo,
                                        do_alvo, "the assigned value")

        # 'c.guardado := "texto"' num 'Caixa<Integer>' conhecido
        if isinstance(node.target, ast.MemberAccess):
            self._conferir_campo_generico(node, escopo)

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
        # Devolver o recurso é entregar a posse: quem recebe solta.
        self._recurso_escapou(node.value)
        tipo = self.infer(node.value, escopo) if node.value else "Void"
        if self._action_depth == 0:
            self.error("'yield' outside of an action", node,
                       "'yield' returns from an action; use 'out' to print",
                       "yield-outside-action")
        elif (self._current_return
              and self._current_return not in (UNKNOWN, ANY)
              and self._current_return not in self._genericos_em_escopo()):
            if not self._compativel(self._current_return, tipo):
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

    def _estreitar_por(self, condicao):
        """O que a condicao prova sobre um nome, dentro do ramo dela.

        Hoje ela prova uma coisa so, e e a que mais aparece:
        `given x is not void:` garante que `x` nao e `Void` ali dentro.
        Sem isso, o idioma mais comum de guarda contra nulo era acusado
        na linha seguinte — `Cannot index a value of type Void` sobre um
        codigo que roda —, e a saida de quem escreve seria desligar o
        analisador ou parar de usar a guarda.

        O tipo que entra e `UNKNOWN`, e nao o tipo real: o analisador
        sabe que **nao e void**, e nao sabe o que e. Inventar um tipo
        aqui seria acusar outra coisa mais adiante, com confianca.
        """
        import dataforge.ast_nodes as ast

        if not isinstance(condicao, ast.ComparisonOp):
            return {}
        if condicao.op != "isnt":
            return {}
        # Aceita as duas ordens: `x is not void` e `void is not x`.
        for um, outro in ((condicao.left, condicao.right),
                          (condicao.right, condicao.left)):
            if isinstance(um, ast.Identifier) and \
                    isinstance(outro, ast.VoidLiteral):
                return {um.name: UNKNOWN}
        return {}

    def st_GivenBlock(self, node, escopo):
        """Os nomes de um ramo sobrevivem ao bloco; os TIPOS, nao.

        As duas metades resolvem problemas opostos, e as duas importam:

            given n % 2 is 0:
                rotulo := "par"
            otherwise:
                rotulo := "impar"
            out rotulo

        Sem os nomes saindo do ramo, isto virava "Undefined name
        'rotulo'" — e o interpretador roda. Por isso cada ramo publica o
        que declarou.

        Mas os ramos sao MUTUAMENTE EXCLUSIVOS, e herdar o tipo de um
        deles no seguinte acusa codigo certo:

            given typeof(atual) is "Vault":
                atual := atual[parte] ?? void      // aqui pode virar Void
            otherwise:
                atual := atual[parte]              // "Cannot index Void"

        O segundo ramo nunca roda depois do primeiro. Por isso o tipo que
        volta e UNKNOWN: e o que o analisador sabe de verdade quando dois
        caminhos escrevem no mesmo nome, e um analisador que inventa o
        que nao sabe ensina a ignora-lo.
        """
        self.infer(node.condition, escopo)
        ramos = []
        # Cada corpo leva junto o que a condicao dele PROVA sobre um
        # nome — ver `_estreitar_por`.
        corpos = [(node.body, self._estreitar_por(node.condition))]
        for cond, corpo in node.orif_blocks:
            self.infer(cond, escopo)
            corpos.append((corpo, self._estreitar_por(cond)))
        if node.otherwise_body:
            corpos.append((node.otherwise_body, {}))

        novos = {}
        for corpo, estreitados in corpos:
            filho = Scope(escopo)
            for nome, tipo in estreitados.items():
                if escopo.has(nome):
                    filho.declare(nome, tipo, node.line, node.column)
            ramos.append(self.visit_block(corpo, filho))
            for nome, tipo in filho.names.items():
                if nome in novos and novos[nome] != tipo:
                    novos[nome] = UNKNOWN
                else:
                    novos[nome] = tipo
            for nome in filho.used:
                escopo.used.add(nome)

        for nome, tipo in novos.items():
            if not escopo.has(nome):
                # Declarado so dentro do bloco: o nome passa a existir,
                # e o tipo fica em aberto — so um dos ramos roda.
                escopo.declare(nome, UNKNOWN, node.line, node.column)

        if node.otherwise_body:
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
            self._conferir_capturas_repetidas(caso.pattern)
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
        """Um 'match' que deixou um caso de fora.

        Sem isto, o caso esquecido devolve 'void' em silencio — e 'void'
        costuma atravessar meia dezena de chamadas antes de virar erro em
        outro lugar, longe da causa.

        Quatro formas, e todas so falam quando conseguem PROVAR:

          enum         'point Cor.Verde' sem 'Cor.Azul'
          booleano     'point yes' sem 'point no'
          sequencia    'point [x, ...resto]' sem 'point []' — a recursao
                       que quebra na lista vazia, o caso classico
          hierarquia   'point Circulo', 'point Quadrado' sob um blueprint
                       'abstract' que tem um 'Triangulo' concreto

        Um 'default' ou uma captura solta cobrem o resto. Um 'point' COM
        GUARDA nao cobre nada: 'point Cor.Azul when x' deixa passar o Azul
        em que 'x' nao vale — contar esse ramo fazia a checagem de enum
        calar sobre um caso que ficou, de fato, de fora.
        """
        if getattr(node, "default_body", None):
            return
        padroes = []
        for caso in node.points:
            if isinstance(caso, tuple):
                return                  # forma antiga: nada a inspecionar
            if caso.guard is not None:
                continue
            padrao = caso.pattern
            if isinstance(padrao, (ast.CapturePattern, ast.WildcardPattern)):
                return
            if isinstance(padrao, ast.OrPattern):
                padroes.extend(padrao.options)
            else:
                padroes.append(padrao)

        # A forma do match e decidida pelos ramos COM guarda tambem: um
        # match de enum em que todo ramo tem guarda continua sendo de enum.
        todos = []
        for caso in node.points:
            p_ = caso.pattern
            todos.extend(p_.options if isinstance(p_, ast.OrPattern) else [p_])

        for conferir in (self._exaustividade_de_enum,
                         self._exaustividade_booleana,
                         self._exaustividade_aninhada,
                         self._exaustividade_de_sequencia,
                         self._exaustividade_de_hierarquia):
            if conferir(node, padroes, todos):
                return

    def _avisar_incompleto(self, node, texto, dica):
        self.warn(texto, node, dica, "match-incompleto")

    def _exaustividade_de_enum(self, node, padroes, todos):
        enums = set()
        for padrao in todos:
            dono, _ = self._membro_de_enum(padrao)
            if dono is None:
                return False
            enums.add(dono)
        # Um match sobre DOIS enums diferentes nao e um match sobre um
        # enum: e outra coisa, e nao cabe cobrar exaustividade.
        if len(enums) != 1:
            return True
        nome_enum = enums.pop()
        membros = self.enums.get(nome_enum)
        if not membros:
            return True
        vistos = {self._membro_de_enum(p)[1] for p in padroes}
        faltando = [m for m in membros if m not in vistos]
        if faltando:
            lista = ", ".join(f"{nome_enum}.{m}" for m in faltando)
            # Um aviso por membro viraria ruido num enum de dez.
            self._avisar_incompleto(
                node,
                f"'match' não cobre {len(faltando)} membro(s) de "
                f"'{nome_enum}': {lista}",
                "Trate cada um, ou acrescente 'default:' para o resto")
        return True

    def _exaustividade_booleana(self, node, padroes, todos):
        if not todos or not all(isinstance(p, ast.LiteralPattern)
                                and isinstance(p.value, bool) for p in todos):
            return False
        vistos = {p.value for p in padroes}
        faltando = [nome for valor, nome in ((True, "yes"), (False, "no"))
                    if valor not in vistos]
        if faltando:
            self._avisar_incompleto(
                node, f"'match' não cobre {' nem '.join(faltando)}",
                "Um booleano tem dois valores: trate os dois, ou use "
                "'default:'")
        return True

    @staticmethod
    def _irrefutavel(padrao):
        """Casa com qualquer valor naquela posição?"""
        return isinstance(padrao, (ast.CapturePattern, ast.WildcardPattern))

    #: Ate quantas combinacoes vale enumerar. Um aviso que lista
    #: duzentas combinacoes e ruido, e ninguem o le duas vezes.
    _TETO_DE_COMBINACOES = 64

    def _exaustividade_aninhada(self, node, padroes, todos):
        """'point [Cor.A, x]' sem o 'Cor.B' — o enum DENTRO da sequencia.

        A conferencia de enum olha o padrao inteiro, e um
        `SequencePattern` nao e membro de enum: ela devolve `False`. A de
        sequencia REIVINDICA o match e se cala, porque `Cor.A` nao e
        irrefutavel e o ramo nao conta como cobertura de tamanho. O
        resultado era silencio total sobre um caso que ficou de fora.

        Aqui a cobertura e por POSICAO, e o que ela cobra e o produto
        cartesiano dos eixos de enum. Ela desiste — e deixa a conferencia
        de sequencia seguir — quando nao consegue concluir:

          * ramos de tamanhos diferentes, ou com `...resto`: ali a
            pergunta e de tamanho, e e a outra conferencia que responde;
          * uma posicao com literal, record ou vault: `[Cor.A, 0]` nao
            cobre `[Cor.A, *]`, e tratar como se cobrisse inverteria o
            sentido do aviso;
          * duas posicoes do mesmo eixo com enums diferentes;
          * mais de `_TETO_DE_COMBINACOES` combinacoes.

        Uma posicao IRREFUTAVEL cobre todos os membros daquele eixo — e e
        isso que faz `point [Cor.A, x]` mais `point [c, x]` ser completo.
        """
        if not todos or not all(isinstance(p, ast.SequencePattern)
                                for p in todos):
            return False
        tamanhos = {len(p.elements) for p in todos}
        if len(tamanhos) != 1 or any(p.rest_index >= 0 or p.rest_name
                                     for p in todos):
            return False
        largura = tamanhos.pop()
        if largura == 0:
            return False

        # Que eixo e cada posicao? Um enum, ou livre.
        eixos = {}
        for posicao in range(largura):
            donos = set()
            for padrao in todos:
                elemento = padrao.elements[posicao]
                if self._irrefutavel(elemento):
                    continue
                dono, _membro = self._membro_de_enum(elemento)
                if dono is None:
                    return False          # literal, record, vault: calar
                donos.add(dono)
            if len(donos) > 1:
                return False
            if donos:
                nome = donos.pop()
                membros = self.enums.get(nome)
                if not membros:
                    return False
                eixos[posicao] = (nome, list(membros))
        if not eixos:
            return False

        total = 1
        for _nome, membros in eixos.values():
            total *= len(membros)
        if total > self._TETO_DE_COMBINACOES:
            return True                   # reivindica, e nao enumera

        # O que cada ramo SEM GUARDA cobre: o produto de {membro} nas
        # posicoes de enum, e de TODOS os membros onde ele e irrefutavel.
        import itertools

        posicoes = sorted(eixos)
        cobertas = set()
        for padrao in padroes:
            if len(padrao.elements) != largura:
                continue
            opcoes = []
            for posicao in posicoes:
                elemento = padrao.elements[posicao]
                _nome, membros = eixos[posicao]
                if self._irrefutavel(elemento):
                    opcoes.append(list(membros))
                else:
                    opcoes.append([self._membro_de_enum(elemento)[1]])
            cobertas.update(itertools.product(*opcoes))

        todas = set(itertools.product(*[eixos[p][1] for p in posicoes]))
        faltando = sorted(todas - cobertas)
        if faltando:
            def desenhar(combinacao):
                partes = []
                for posicao in range(largura):
                    if posicao in eixos:
                        nome = eixos[posicao][0]
                        membro = combinacao[posicoes.index(posicao)]
                        partes.append(f"{nome}.{membro}")
                    else:
                        partes.append("_")
                return "[" + ", ".join(partes) + "]"

            mostradas = [desenhar(c) for c in faltando[:4]]
            resto = (f" e {len(faltando) - 4} outra(s)"
                     if len(faltando) > 4 else "")
            self._avisar_incompleto(
                node,
                f"'match' não cobre {len(faltando)} combinação(ões): "
                f"{', '.join(mostradas)}{resto}",
                "Trate cada uma, use uma captura na posição que sobra, ou "
                "acrescente 'default:'")
        return True

    def _exaustividade_de_sequencia(self, node, padroes, todos):
        if not todos or not all(isinstance(p, ast.SequencePattern) for p in todos):
            return False
        exatos = set()        # tamanhos cobertos exatamente
        a_partir = None       # 'resto' cobre todo tamanho >= este
        for padrao in padroes:
            if not all(self._irrefutavel(e) for e in padrao.elements):
                continue      # '[0, x]' nao cobre todo cluster de dois
            fixos = len(padrao.elements)
            if padrao.rest_index >= 0 or padrao.rest_name:
                a_partir = fixos if a_partir is None else min(a_partir, fixos)
            else:
                exatos.add(fixos)
        if a_partir is None:
            # Sem 'resto', nenhum conjunto finito de tamanhos cobre todo
            # cluster — mas avisar aqui acusaria o match que so trata
            # pares, que e legitimo quando o dado e sempre par. Calar.
            return True
        faltando = [n for n in range(a_partir) if n not in exatos]
        if faltando:
            tamanhos = ", ".join(str(n) for n in faltando)
            vazio = " — inclusive o vazio" if 0 in faltando else ""
            self._avisar_incompleto(
                node,
                f"'match' não cobre cluster(s) de {tamanhos} item(ns){vazio}",
                "Acrescente 'point []:' (e os tamanhos menores que faltam), "
                "ou use 'default:'. Numa recursão, é o caso que para")
        return True

    def _exaustividade_de_hierarquia(self, node, padroes, todos):
        """'point Circulo' e 'point Quadrado' sob um 'abstract blueprint Forma'.

        Um blueprint 'abstract' e a raiz de uma familia: ninguem o
        instancia, e o que chega ao 'match' e sempre uma das filhas
        concretas. Se todas as filhas concretas DESTE ARQUIVO nao estao
        cobertas, falta um caso. Uma filha declarada em outro arquivo o
        analisador nao ve — por isso e aviso, e nao erro.
        """
        if not todos or not all(isinstance(p, ast.TypePattern)
                                and p.type_name in self.blueprints for p in todos):
            return False
        cobertos = set()
        for padrao in padroes:
            subs = list(padrao.sub_patterns) + list(padrao.field_patterns.values())
            if all(self._irrefutavel(s) for s in subs):
                cobertos.add(padrao.type_name)

        # A raiz: um abstrato que esta na linhagem de TODOS os padroes.
        candidatas = None
        for padrao in todos:
            linhagem = self._linhagem(padrao.type_name) | {padrao.type_name}
            abstratas = linhagem & self.abstratos
            candidatas = abstratas if candidatas is None else candidatas & abstratas
        if not candidatas:
            return True
        # A mais proxima: a que tem menos ancestrais abstratos acima dela
        # contados de baixo — na pratica, a de linhagem mais longa.
        raiz = max(candidatas, key=lambda r: len(self._linhagem(r)))

        concretas = sorted(
            nome for nome in self.blueprints
            if nome not in self.abstratos
            and nome not in self.trait_exigidos
            and "." not in nome
            and raiz in self._linhagem(nome))
        faltando = [c for c in concretas
                    if not ({c} | self._linhagem(c)) & cobertos]
        if faltando:
            self._avisar_incompleto(
                node,
                f"'match' não cobre {len(faltando)} tipo(s) de '{raiz}': "
                f"{', '.join(faltando)}",
                f"'{raiz}' é abstract, e cada filha concreta chega a este "
                f"match: trate as que faltam, ou use 'default:'")
        return True

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

    def _conferir_capturas_repetidas(self, padrao):
        """O mesmo nome ligado duas vezes no MESMO padrão.

        `point [a, a]` diz "dois itens iguais", e era lido como "dois
        itens quaisquer, e fique com o segundo" — `[1, 2]` casava, com
        `a` valendo 2. Em Rust e no `match` do Python repetir um nome no
        mesmo padrão é erro justamente por isso.

        É a mesma família do argumento nomeado repetido e do parâmetro
        declarado duas vezes: um nome ligado duas vezes, calado.

        **O `or` é a exceção**, e ele é o motivo de a conta ser por
        ramo: `point [a] or {"v": a}` liga `a` uma vez em cada lado, e
        exatamente um lado casa. Recusar isso proibiria a forma que
        existe para unificar dois formatos.
        """
        vistos = {}
        for nome, no in self._capturas_de(padrao):
            if nome in vistos:
                self.error(
                    f"'{nome}' é capturado duas vezes no mesmo padrão",
                    no, "um nome por padrão: o segundo apagava o primeiro, "
                        "e o padrão casava com valores diferentes",
                    "captura-repetida")
                return
            vistos[nome] = no

    def _capturas_de(self, padrao):
        """Os nomes que este padrão liga, com o nó de cada um.

        Num `or`, o MAIOR dos ramos — e não a soma: os ramos são
        alternativas, e somar acusaria o uso correto.
        """
        if padrao is None:
            return []
        saida = []
        if getattr(padrao, "binding", ""):
            saida.append((padrao.binding, padrao))
        if isinstance(padrao, ast.CapturePattern):
            saida.append((padrao.name, padrao))
        elif isinstance(padrao, ast.SequencePattern):
            for sub in padrao.elements:
                saida += self._capturas_de(sub)
            if padrao.rest_name:
                saida.append((padrao.rest_name, padrao))
        elif isinstance(padrao, ast.MappingPattern):
            for _, sub in padrao.pairs:
                saida += self._capturas_de(sub)
            if padrao.rest_name:
                saida.append((padrao.rest_name, padrao))
        elif isinstance(padrao, ast.TypePattern):
            for sub in padrao.sub_patterns:
                saida += self._capturas_de(sub)
            for sub in padrao.field_patterns.values():
                saida += self._capturas_de(sub)
        elif isinstance(padrao, ast.OrPattern):
            maior = []
            for opcao in padrao.options:
                desta = self._capturas_de(opcao)
                if len(desta) > len(maior):
                    maior = desta
            saida += maior
        return saida

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
        self._conferir_faixa(node)
        interno = Scope(escopo, "loop")
        interno.declare(node.var, "Integer", node.line, node.column)
        self._loop_depth += 1
        try:
            self.visit_block(node.body, interno)
        finally:
            self._loop_depth -= 1
        return False

    def _conferir_faixa(self, node):
        """Um `cycle from/to` que não pode rodar, ou não pode parar.

        Só com os três valores escritos à mão: com uma variável no meio,
        não há o que provar, e acusar ali seria o falso alarme que ensina
        a desligar a verificação.

        A faixa é INCLUSIVA nos dois extremos, então `from 1 to 1` roda
        uma vez — é `from 5 to 1` sem passo negativo que nunca roda, e é
        um erro de digitação tão comum quanto silencioso: o corpo
        simplesmente não executa, e nada aparece.
        """
        inicio = self._inteiro_literal(node.start)
        fim = self._inteiro_literal(node.end)
        passo = 1 if node.step is None else self._inteiro_literal(node.step)
        if inicio is None or fim is None or passo is None:
            return

        if passo == 0:
            self.error(
                "'cycle … step 0' never ends", node,
                "A step of zero never reaches the end; use 1, or -1 to "
                "count down", "cycle-vazio")
            return
        if passo > 0 and inicio > fim:
            self.warn(
                f"This loop never runs: it counts up from {inicio} to {fim}",
                node,
                f"To count down, say  step -1  — or swap the bounds to "
                f"from {fim} to {inicio}", "cycle-vazio")
        elif passo < 0 and inicio < fim:
            self.warn(
                f"This loop never runs: it counts down from {inicio} "
                f"to {fim}", node,
                f"To count up, drop the negative step — or swap the "
                f"bounds to from {fim} to {inicio}", "cycle-vazio")

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
            corpo_sempre = self.visit_block(node.body, escopo)
        handles_sempre = True
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
            if not self.visit_block(clausula.body, escopo):
                handles_sempre = False
        ensure_sempre = False
        if node.ensure_body:
            ensure_sempre = self.visit_block(node.ensure_body, Scope(escopo))
        # Um 'monitor' cujo corpo e cujos 'handle' TODOS terminam em
        # 'yield' nao deixa por onde cair depois dele. Devolver False
        # aqui acusava
        #
        #     action f() -> Resultado:
        #         monitor:
        #             yield Resultado(yes, …)
        #         handle Error as e:
        #             yield Resultado(no, …)
        #
        # de "pode terminar sem 'yield'" — e essa e a forma canonica de
        # uma acao que devolve sucesso ou falha. Um erro que nenhum
        # 'handle' captura sobe: ele nao cai no fim da acao, e por isso
        # nao precisa de um 'yield' ali.
        return ensure_sempre or (corpo_sempre and handles_sempre)

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
        # 'assert xs >> morph v: v is 3' le o 'is' DENTRO do corpo do
        # morph: o assert confere uma lista de booleanos, que e verdadeira
        # sempre que nao estiver vazia. O teste passa sem conferir nada —
        # achado assim numa pagina desta documentacao.
        cond = node.condition
        if isinstance(cond, (ast.PipelineExpression, ast.ListLiteral,
                             ast.ListComprehension, ast.DictLiteral,
                             ast.SetLiteral, ast.SetComprehension)):
            forma = ("a pipeline" if isinstance(cond, ast.PipelineExpression)
                     else "a collection")
            self.warn(
                f"this assert checks {forma}, which is true whenever it is "
                "not empty — it proves nothing",
                node,
                hint="wrap the pipeline in parentheses before comparing: "
                     "assert (xs >> morph v: v * 2) is [2, 4]",
                code="assert-sempre-verdadeiro")
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
            # Uma EMBUTIDA nao e estado compartilhado. 'id := int(...)'
            # dentro de uma rota declara uma variavel local — e o nome
            # so "existe fora" porque 'id' e uma das 228 funcoes da
            # linguagem. Avisar ali e falso alarme no caminho mais
            # comum: 'id', 'total', 'count' e 'max' sao nomes de
            # variavel antes de serem nomes de funcao.
            if self._so_e_embutida(nome, escopo):
                continue
            self.warn(
                f"'{nome}' e escrito dentro de '{palavra}' e vem de fora: "
                f"duas threads podem perder atualizacoes",
                no,
                "a linguagem nao sincroniza sozinha — use "
                "'Arcane.Concurrent': 'contador()' para somar, 'mutex()' "
                "para um bloco, ou 'canal()' para passar o valor adiante",
                self._CODIGO_CORRIDA)

    def _so_e_embutida(self, nome, escopo):
        """O nome existe APENAS como função da linguagem?

        Se sim, escrever nele dentro de um bloco concorrente declara uma
        variável local — e não toca estado compartilhado nenhum. Foi o
        interpretador que mudou: uma atribuição não sobe mais até as
        embutidas para sobrescrevê-las.
        """
        if nome not in getattr(self, "_nomes_da_linguagem", ()):
            return False
        atual = escopo
        while atual is not None:
            if nome in atual.names and atual is not self.global_scope:
                return False
            atual = atual.parent
        return True

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

        # Mutar por METODO, mas so o que PERDE DADO.
        #
        # Medido antes de escrever esta lista: 'append' de quatro
        # threads, 5 mil vezes cada, entregou 20.000 de 20.000 — ele e
        # atomico, porque o GIL protege a operacao inteira. Avisar sobre
        # ele seria falso alarme em codigo que funciona.
        #
        # O que perde e LER-MODIFICAR-ESCREVER: 'v["n"] := v["n"] + 1'
        # deu 33.740 de 40.000, e 'lista[0] := lista[0] + 1' deu 31.705.
        # Esses ja sao pegos como atribuicao, acima.
        #
        # Ficam aqui os metodos que leem para decidir o que escrever —
        # 'remove' procura antes de tirar, 'pop' devolve o que tirou,
        # 'insert' desloca. Dois deles ao mesmo tempo podem tirar o
        # mesmo item ou pular um.
        if isinstance(no, ast.MethodCall) and no.method in self._MUTAM:
            base = getattr(no, "object", None)
            while isinstance(base, (ast.IndexAccess, ast.MemberAccess)):
                base = getattr(base, "object", None)
            if isinstance(base, ast.Identifier) \
                    and base.name not in ("self", "this", "root") \
                    and not self._e_modulo(base.name):
                # Um MODULO nao e colecao compartilhada. 'Xls.set(aba,
                # "F1", …)' e chamada de funcao, e casava com 'set' da
                # lista — um falso alarme no 'projetos/loja-web', que
                # exporta uma planilha numa rota.
                #
                # Foi o unico falso alarme dos seis arquivos acusados, e
                # so apareceu porque a checagem rodou no repositorio
                # inteiro antes de eu commitar.
                saida.setdefault(base.name, no)

        for campo in getattr(no, "__dataclass_fields__", {}):
            if campo in ("line", "column"):
                continue
            self._colher_escritas(getattr(no, campo, None), saida)

    def _e_modulo(self, nome):
        """`nome` e um modulo adotado?

        Pelo TIPO que o `adopt` declarou (`"Module"`), e nao por uma
        lista nova: o `st_AdoptStatement` ja sabe disso, e uma segunda
        fonte divergiria. A superficie cobre o `adopt ./vizinho`.
        """
        if nome in self.superficies:
            return True
        return self.global_scope.lookup(nome) == "Module"

    #: Os metodos que LEEM para decidir o que escrever.
    #:
    #: 'append' e 'add' ficam de FORA: sao atomicos sob o GIL, e
    #: avisar sobre eles daria falso alarme em codigo que funciona —
    #: medido, 20.000 de 20.000 com quatro threads.
    #:
    #: 'sorted', 'count' e 'index' tambem: devolvem sem mudar nada.
    _MUTAM = frozenset({
        # Procuram o item antes de mexer: duas threads podem tirar o
        # mesmo, ou uma pular o que a outra ja tirou.
        "remove", "pop", "insert", "delete", "discard",
        # Reordenam a colecao inteira a partir do estado atual.
        "sort", "reverse", "clear",
        # Leem o que existe para decidir o que fica.
        "update", "merge_in", "setdefault", "extend",
    })

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
        # Uma rota roda numa THREAD por pedido: o Kiln usa
        # 'ThreadingHTTPServer'. Escrever num nome de fora do bloco e a
        # mesma corrida de 'thread'/'parallel', e e o caso mais comum
        # em producao — um contador de visitas, um cache em memoria.
        #
        # Medido: seis pedidos simultaneos numa rota que le, espera e
        # escreve entregaram 1 de 6. Cinco incrementos perdidos, sem
        # nada denunciando.
        #
        # A checagem so olhava 'thread' e 'parallel', que aparecem no
        # codigo. Aqui a concorrencia e INVISIVEL: quem escreve a rota
        # nao ve thread nenhuma.
        self._avisar_escrita_compartilhada(node.body, escopo, "route")
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
        if not self._em_membro and node.name not in self.sobrecarregadas:
            self.actions.setdefault(node.name, assinatura)
        escopo.declare(node.name, "Action", node.line, node.column)

        interno = Scope(escopo, "action")
        limites = {**self._limites_do_blueprint,
                   **(getattr(node, "type_bounds", None) or {})}
        genericos_aqui = (set(getattr(node, "type_params", None) or [])
                          | self._genericos_do_blueprint)
        for param in node.params:
            tipo = canonical(assinatura.param_types.get(param, UNKNOWN))
            if tipo in genericos_aqui:
                # Dentro do corpo, um 'T extends Number' E um Number — e o
                # que permite 'a bigger b', que era acusado de "Cannot
                # order T against T". Sem limite, nao se sabe nada.
                tipo = canonical(limites.get(tipo) or UNKNOWN)
            interno.declare(param, tipo, node.line, node.column)

        for nome_t, limite in (getattr(node, "type_bounds", None) or {}).items():
            if not self._e_concreto(canonical(limite)):
                self.error(f"Unknown type '{limite}' in '<{nome_t} extends {limite}>'",
                           node, self._hint_tipo(limite), "unknown-type")

        # Os parametros de tipo ('<T>') valem como nome de tipo dentro
        # desta acao — e so dentro dela. Sem isto, 'action primeiro<T>(l)
        # -> T' acusaria "tipo T desconhecido", que e o oposto do que a
        # declaracao acabou de dizer.
        genericos = set(getattr(node, "type_params", None) or [])
        genericos |= self._genericos_do_blueprint

        for tipo in assinatura.param_types.values():
            falta = self._tipo_desconhecido(tipo, genericos)
            if falta:
                self.error(f"Unknown parameter type '{falta}'", node,
                           self._hint_tipo(falta), "unknown-type")

        retorno_anterior = self._current_return
        genericos_anteriores = self._genericos_da_acao
        self._current_return = assinatura.return_type
        if canonical(getattr(node, "return_type", "") or "") in self._genericos_do_blueprint:
            self._current_return = canonical(
                limites.get(canonical(node.return_type)) or UNKNOWN)
        self._genericos_da_acao = set(getattr(node, "type_params", None) or [])
        self._action_depth += 1
        self._hoist(node.body, interno)
        # A posse é por AÇÃO: um recurso aberto numa não fala da outra, e
        # um nome movido lá dentro não contamina o de fora.
        posse_anterior = (self.posse_movida, self.recursos_abertos,
                          self.posse_criada)
        self.posse_movida, self.recursos_abertos = {}, {}
        self.posse_criada = set()
        try:
            self._conferir_fluxo(node, interno)
            sempre_retorna = self.visit_block(node.body, interno)
            self._cobrar_recursos_soltos(interno, node)
            promessas = getattr(node, "postconditions", None) or []
            if promessas:
                # 'outcome' e o valor devolvido, com o tipo que a acao
                # declara; 'before(…)' le o escopo da entrada, que e o mesmo
                saida = Scope(interno, "promises")
                saida.declare("outcome", canonical(assinatura.return_type),
                              node.line, node.column)
                for promessa in promessas:
                    self.infer(promessa.condition, saida)
                    if promessa.message is not None:
                        self.infer(promessa.message, saida)
        finally:
            self._action_depth -= 1
            self._current_return = retorno_anterior
            self._genericos_da_acao = genericos_anteriores
            (self.posse_movida, self.recursos_abertos,
             self.posse_criada) = posse_anterior

        declarado = assinatura.return_type
        # Um metodo de 'trait' e so a assinatura: corpo vazio, de
        # proposito. Cobrar um 'yield' de quem nao tem corpo pede o
        # impossivel, e era o unico aviso que a declaracao de um
        # contrato produzia.
        if (declarado not in (UNKNOWN, ANY, "Void")
                and declarado not in genericos
                and node.body
                and not sempre_retorna and not assinatura.is_generator):
            self.warn(
                f"Action '{node.name}' declares '-> {declarado}' but can end "
                f"without a 'yield'", node,
                "Add a 'yield' at the end, or drop the return type",
                "missing-return")
        return False

    def _conferir_fluxo(self, node, escopo):
        """`talvez-nao-definida`: o nome que só um caminho atribui.

        ```
        given n bigger 10:
            rotulo := "alto"
        yield rotulo          # e quando a condicao e falsa?
        ```

        O analisador registra o nome do ramo, e isso **está certo** — um
        `given` compartilha o escopo, e é assim que se decide um valor em
        dois caminhos. O que faltava era contar por quantos caminhos ele
        passa, e essa pergunta só o grafo de fluxo responde.

        A conta é do `mir.py`, e o que ela precisa daqui é a lista de
        nomes visíveis **de fora**: `:=` dentro de uma ação escreve o
        nome externo quando ele existe (medido), então um nome de fora
        nunca pode ser acusado aqui. É aviso, e não erro: o caminho que
        não define pode ser o que nunca acontece, e só quem escreveu
        sabe.
        """
        if not node.body:
            return
        try:
            from . import mir
            corpo = mir.corpo_de_acao(node)
        except Exception:
            return                      # um grafo que nao sai nao acusa nada

        externos = set()
        alvo = escopo
        while alvo is not None:
            externos |= set(alvo.names)
            alvo = alvo.parent

        self._conferir_ramo_morto(corpo, externos)

        for nome, instrucao in mir.talvez_nao_definidas(corpo, externos):
            self.warn(
                f"'{nome}' may not be defined here: some path to this line "
                f"does not assign it",
                instrucao,
                f"Give '{nome}' a value before the branch, or add the "
                f"'otherwise' that covers the other path",
                "talvez-nao-definida")

    def _conferir_ramo_morto(self, corpo, externos):
        """`ramo-morto`: o ramo cuja condicao se PROVA falsa.

        ```
        limite := 5
        given limite bigger 10:      # nunca roda
            yield "alto"
        ```

        A prova vem da propagacao condicional sobre SSA, e nao de olhar
        o literal: e a forma que aparece em codigo de verdade — numero
        magico virando constante nomeada, e a comparacao ficando sempre
        falsa depois de alguem mexer no numero.

        O que a faz **calar**:

        | Cala quando | Porque |
        |---|---|
        | a condicao le nome de fora do corpo | o valor nao e deste corpo, e `:=` numa acao escreve o de fora |
        | o corpo tem fechamento, `monitor`, `defer` ou bloco opaco | o mesmo motivo de `talvez-nao-definida`: a ordem nao e a do grafo |
        | a condicao nao se prova | e o caso de quase todo codigo, e e o silencio certo |
        | o rotulo do bloco morto nao e `sim`/`nao` | `halt`, `skip`, `volta` e `point` nao se provam por valor |

        E aviso, e nao erro: um ramo que nunca roda pode ser uma guarda
        deixada de proposito, e so quem escreveu sabe.
        """
        if corpo.tem_monitor or corpo.tem_defer or corpo.tem_closure \
                or corpo.tem_opaco:
            return
        try:
            from . import mir, ssa
            forma = ssa.construir(corpo)
            _fixas, mortos = ssa.constantes_condicionais(forma)
        except Exception:
            return
        if not mortos:
            return

        for bloco in forma.blocos:
            if bloco.terminador != "ramo" or not bloco.instrucoes:
                continue
            # 'persist yes:' com 'halt' dentro e o laco infinito legitimo, e
            # 'stream action' vive disso: a saida do laco fica "morta" no
            # grafo e nao ha nada de errado. A cabeca de um laco e o unico
            # bloco com rotulo 'condicao', e por isso ela fica de fora.
            # Medido: sem esta linha, 29 acusacoes no repositorio, todas
            # em generator infinito.
            if bloco.rotulo == "condicao":
                continue
            condicao = bloco.instrucoes[-1]
            # Um nome que vem de fora nao tem valor provavel AQUI.
            if set(mir.lidos(condicao.no)) & set(externos):
                continue
            morre = sorted({r for d, r in bloco.saidas
                            if d in mortos and r in ("sim", "nao")})
            vivos = [d for d, r in bloco.saidas if d not in mortos]
            if len(morre) != 1 or not vivos:
                continue
            lado = "the 'given' body" if morre[0] == "sim" \
                else "the 'otherwise' body"
            self.warn(
                f"this condition is always "
                f"{'no' if morre[0] == 'sim' else 'yes'}: {lado} never runs",
                condicao.no,
                "Drop the branch that cannot run, or fix the value the "
                "condition compares against",
                "ramo-morto")

    def st_BlueprintDeclaration(self, node, escopo):
        if node.name not in self.maes:
            # Declarado dentro de um bloco ('monitor', 'given'), que nao passa
            # pelo hoisting do topo: sem registrar aqui, a linhagem dele seria
            # desconhecida e o 'override' e o contrato acusariam o que existe.
            self._hoist([node], escopo, registrar_acoes=False)
        interno = Scope(escopo, "blueprint")
        interno.declare("self", node.name, node.line, node.column)
        interno.declare("this", node.name, node.line, node.column)
        interno.declare("root", ANY, node.line, node.column)
        for param in node.constructor_params or []:
            interno.declare(param, UNKNOWN, node.line, node.column)
        for pai in node.parents:
            if "." in pai:
                continue                    # vem de modulo: a execucao confere
            if pai in self.finais:
                self.error(
                    f"'{node.name}' cannot extend '{pai}', which is declared final",
                    node, f"keep a {pai} in a field instead — composition works "
                          f"where inheritance was forbidden", "heranca-final")
            elif pai in self.contratos:
                self.error(
                    f"'{node.name}' extends the contract '{pai}'", node,
                    f"a contract is adopted: blueprint {node.name} with {pai}:",
                    "contrato-como-mae")
            if pai not in self.blueprints and pai not in self.known_types:
                self.error(f"Unknown parent blueprint '{pai}'", node,
                           self._hint_nome(pai, self.blueprints), "unknown-parent")
            elif pai == node.name:
                # 'blueprint Ciclo extends Ciclo' passava limpo, e em
                # execucao a mae era ignorada: o blueprint nascia sem mae
                # nenhuma e a declaracao dizia o contrario.
                self.error(
                    f"Blueprint '{node.name}' cannot extend itself", node,
                    "a blueprint inherits from ANOTHER one; remove the "
                    "'extends', or name the real parent", "heranca-circular")
        for trait in getattr(node, 'traits', []) or []:
            if "." in trait:
                continue
            if trait not in self.blueprints:
                self.error(f"Unknown trait '{trait}'", node,
                           self._hint_nome(trait, self.blueprints), "unknown-trait")
        meta = getattr(node, "metaclass", "") or ""
        if meta and "." not in meta:
            if meta not in self.blueprints:
                self.error(f"Unknown metaclass '{meta}'", node,
                           self._hint_nome(meta, self.metas) or
                           f"declare 'meta blueprint {meta}:'", "unknown-metaclass")
            elif meta not in self.metas:
                self.error(f"'{meta}' is not a metaclass", node,
                           f"declare it as 'meta blueprint {meta}:'",
                           "metaclasse-invalida")
        for campo, tipo in (getattr(node, "constructor_types", None) or {}).items():
            falta = self._tipo_desconhecido(tipo, getattr(node, "type_params", None) or ())
            if falta:
                self.error(f"Unknown type '{falta}' for '{campo}'", node,
                           self._hint_tipo(falta), "unknown-type")
        self._hoist(node.body, interno, registrar_acoes=False)
        anterior = self._em_membro
        genericos_antes = self._genericos_do_blueprint
        limites_antes = self._limites_do_blueprint
        self._em_membro = True
        # Os '<T>' deste blueprint valem nos metodos dele — e so ali.
        self._genericos_do_blueprint = set(
            getattr(node, "type_params", None) or [])
        self._limites_do_blueprint = dict(getattr(node, "type_bounds", None) or {})
        for nome_t, limite in self._limites_do_blueprint.items():
            if not self._e_concreto(canonical(limite)):
                self.error(f"Unknown type '{limite}' in '<{nome_t} extends {limite}>'",
                           node, self._hint_tipo(limite), "unknown-type")
        try:
            self.visit_block(node.body, interno)
        finally:
            self._em_membro = anterior
            self._genericos_do_blueprint = genericos_antes
            self._limites_do_blueprint = limites_antes
        self._conferir_contrato_de_trait(node)
        self._conferir_membros_repetidos(node)
        self._conferir_oop(node)
        return False

    # ── OOP 1.2: override, sobrecarga, readonly, metaclasse, contrato ──

    _CONSTRUTORES = ("setup", "initiate", "__init__")

    def _exigidos_de(self, trait, vistos=None):
        """O que um trait ou contrato exige, inclusive o que ele herda."""
        vistos = vistos or set()
        if trait in vistos:
            return set()
        vistos.add(trait)
        exigidos = self.trait_exigidos.get(trait)
        if exigidos is None:
            return None
        todos = set(exigidos)
        for mae in self.maes.get(trait, ()):
            if mae in self.contratos:
                herdados = self._exigidos_de(mae, vistos)
                if herdados is None:
                    return None
                todos |= herdados
        return todos

    def _assinatura_herdada(self, blueprint, metodo, vistos=None):
        """A assinatura do metodo na mae mais proxima que o declara."""
        vistos = vistos or set()
        for mae in self.maes.get(blueprint, ()):
            if mae in vistos:
                continue
            vistos.add(mae)
            tabela = self.assinaturas_de_metodo.get(mae, {})
            if metodo in tabela:
                return mae, tabela[metodo]
            achado = self._assinatura_herdada(mae, metodo, vistos)
            if achado is not None:
                return achado
        return None

    @staticmethod
    def _aridade(sig):
        return len(sig.params) - len(sig.defaults), len(sig.params)

    def _conferir_oop(self, node):
        fechado = self._blueprint_e_fechado(node.name)
        herdados = set()
        for mae in self.maes.get(node.name, ()):
            herdados |= self._membros_com_heranca(mae)
            exigidos = self._exigidos_de(mae)
            if exigidos:
                herdados |= exigidos

        # meta blueprint: os ganchos existem
        if getattr(node, "is_meta", False):
            from .objetos import GANCHOS_DE_META
            for membro in node.body:
                nome = getattr(membro, "name", "")
                if isinstance(membro, ast.ActionDeclaration) and \
                        nome.startswith("on_") and nome not in GANCHOS_DE_META:
                    self.error(f"'{nome}' is not a metaclass hook", membro,
                               self._hint_nome(nome, GANCHOS_DE_META) or
                               "the hooks are: " + ", ".join(GANCHOS_DE_META),
                               "gancho-desconhecido")

        readonly = self.somente_leitura.get(node.name, set())
        variantes = {}
        for membro in node.body:
            nome = getattr(membro, "name", "")
            e_acao = isinstance(membro, ast.ActionDeclaration)
            if isinstance(membro, (ast.ActionDeclaration, ast.PropertyDeclaration)) \
                    and getattr(membro, "is_override", False) and fechado \
                    and nome not in herdados:
                self.error(
                    f"'{node.name}.{nome}' is marked override, but nothing it "
                    f"inherits has '{nome}'", membro,
                    self._hint_nome(nome, herdados) or
                    "remove 'override', or fix the name to match the parent",
                    "override-sem-alvo")

            if not e_acao:
                continue

            if getattr(membro, "is_overload", False):
                sig = ActionSignature(membro)
                for outra in variantes.get(nome, []):
                    if self._aridade(outra) == self._aridade(sig) and all(
                            canonical(outra.param_types.get(a, UNKNOWN)) ==
                            canonical(sig.param_types.get(b, UNKNOWN))
                            for a, b in zip(outra.params, sig.params)):
                        self.error(
                            f"Two overloads of '{node.name}.{nome}' have the same "
                            f"signature", membro,
                            f"the one on line {outra.line} can never be chosen — "
                            f"change a parameter type or remove one",
                            "sobrecarga-duplicada")
                variantes.setdefault(nome, []).append(sig)
                continue

            # readonly escrito fora da construcao
            if readonly and nome not in self._CONSTRUTORES and \
                    not getattr(membro, "is_static", False):
                for campo in sorted(self._campos_atribuidos(membro.body) & readonly):
                    self.error(
                        f"'{node.name}.{campo}' is readonly and '{nome}' writes it "
                        f"after construction", membro,
                        "assign it in the default, the header or 'setup' — or "
                        "remove 'readonly'", "readonly-fora-da-construcao")

            # Liskov: a filha aceita tudo o que a mae aceitava?
            if nome.startswith("__") or nome in self._CONSTRUTORES or \
                    getattr(membro, "is_static", False) or not fechado:
                continue
            achado = self._assinatura_herdada(node.name, nome)
            if achado is None:
                continue
            mae, da_mae = achado
            filha = ActionSignature(membro)
            fmin, fmax = self._aridade(filha)
            mmin, mmax = self._aridade(da_mae)
            if fmin <= mmin and fmax >= mmax:
                continue
            if mae in self.contratos:
                self.error(
                    f"'{node.name}.{nome}' does not match the signature of contract "
                    f"'{mae}'", membro,
                    f"the contract passes {mmin} to {mmax} argument(s); accept all "
                    f"of them — extra parameters need a default",
                    "assinatura-incompativel")
            else:
                self.warn(
                    f"'{node.name}.{nome}' accepts {fmin}–{fmax} argument(s), but "
                    f"'{mae}.{nome}' accepted {mmin}–{mmax}", membro,
                    f"code written for {mae} breaks when it receives a "
                    f"{node.name} (Liskov substitution) — keep the parent's "
                    f"parameters, and give the new ones a default",
                    "substituicao-quebrada")

    def st_ContractDeclaration(self, node, escopo):
        if node.name not in self.contratos:
            self._hoist([node], escopo, registrar_acoes=False)
        interno = Scope(escopo, "contract")
        interno.declare("self", node.name, node.line, node.column)
        for mae in node.parents or []:
            if "." in mae:
                continue
            if mae not in self.blueprints:
                self.error(f"Unknown contract '{mae}'", node,
                           self._hint_nome(mae, self.contratos), "unknown-trait")
            elif mae not in self.contratos:
                self.error(f"Contract '{node.name}' extends '{mae}', which is not "
                           f"a contract", node,
                           "a contract extends only other contracts",
                           "contrato-como-mae")
        anterior = self._em_membro
        genericos_antes = self._genericos_do_blueprint
        self._em_membro = True
        self._genericos_do_blueprint = set(node.type_params or [])
        try:
            for membro in node.members:
                if isinstance(membro, ast.ActionDeclaration):
                    self.visit(membro, interno)
        finally:
            self._em_membro = anterior
            self._genericos_do_blueprint = genericos_antes
        return False

    def st_AugmentDeclaration(self, node, escopo):
        if node.name in self.finais:
            self.error(f"Cannot augment '{node.name}': it is declared final", node,
                       "write an action that receives the object instead",
                       "augment-final")
        if node.name in self.contratos:
            self.error(f"Cannot augment the contract '{node.name}'", node,
                       "declare a new contract that extends it", "augment-final")
        elif node.name not in self.blueprints and "." not in node.name \
                and not escopo.has(node.name):
            self.error(f"Cannot augment '{node.name}': it does not exist", node,
                       self._hint_nome(node.name, self.blueprints), "unknown-blueprint")
        interno = Scope(escopo, "blueprint")
        interno.declare("self", node.name, node.line, node.column)
        interno.declare("this", node.name, node.line, node.column)
        interno.declare("root", ANY, node.line, node.column)
        anterior = self._em_membro
        self._em_membro = True
        try:
            self.visit_block(node.body, interno)
        finally:
            self._em_membro = anterior
        return False

    def st_InvariantStatement(self, node, escopo):
        if not self._em_membro:
            self.error("'invariant' only has meaning in the body of a blueprint",
                       node, "inside an action, use 'expects' or 'assert'",
                       "invariant-fora")
        self.infer(node.condition, escopo)
        if node.message is not None:
            self.infer(node.message, escopo)
        return False

    def st_ExpectsStatement(self, node, escopo):
        self.infer(node.condition, escopo)
        if node.message is not None:
            self.infer(node.message, escopo)
        return False

    def st_PromisesStatement(self, node, escopo):
        self.error("'promises' has to be at the top level of an action body", node,
                   "it runs when the action returns; move it next to the "
                   "first statements of the action", "promises-fora-do-topo")
        return False

    def ex_BeforeExpression(self, node, escopo):
        return self.infer(node.expression, escopo)

    def _conferir_membros_repetidos(self, node):
        """Dois métodos com o mesmo nome, ou um método com o nome de um campo.

        O segundo vencia, calado, e o de cima não tinha como ser chamado.
        O campo repetido de um `record` e o membro repetido de um `enum` já
        eram acusados — o método de um `blueprint`, não.

        O caso do campo é o pior dos dois: em `blueprint B(x)` com
        `action x()`, o campo vence sempre, e `b.x` devolve o valor. O
        método existe no arquivo e **nunca roda**.

        Cala para propriedade (`get x` e `set x` são o mesmo nome de
        propósito) e para método sobrescrito na filha, que é o ponto da
        herança: isto olha um blueprint por vez.
        """
        campos = set(node.constructor_params or [])
        vistos = {}
        for membro in node.body or []:
            if type(membro).__name__ != "ActionDeclaration":
                continue
            nome = getattr(membro, "name", "")
            if not nome or nome.startswith("__"):
                continue
            if getattr(membro, "is_overload", False):
                continue
            if nome in campos:
                self.error(
                    f"'{nome}' is both a field and a method of '{node.name}'",
                    membro, "the field wins, so the method can never be "
                            "called — rename one of them", "membro-repetido")
            elif nome in vistos:
                self.error(
                    f"Duplicate method '{nome}' in blueprint '{node.name}'",
                    membro, f"the one on line {vistos[nome]} can never be "
                            f"called — remove one of them", "membro-repetido")
            else:
                vistos[nome] = membro.line

    def _conferir_contrato_de_trait(self, node):
        """Um blueprint concreto implementa tudo o que prometeu.

        O interpretador já cobrava isto, e cobrava no lugar certo — na
        **declaração**, não na chamada. Mas cobrava em **execução**: um
        blueprint que esquece um método do trait passava no `check` e
        derrubava o programa ao ser declarado. Num projeto grande, o
        arquivo que declara o blueprint pode ser importado só num ramo, e
        aí o erro chega em produção.

        Cala pelas mesmas razões de sempre: um blueprint `abstract`
        promete e não entrega de propósito, um trait que não vimos pode
        exigir qualquer coisa, e uma linhagem aberta pode trazer o método
        de onde não estamos olhando.
        """
        if getattr(node, "is_abstract", False):
            return
        traits = [t for t in (getattr(node, "traits", None) or [])]
        if not traits:
            return
        if not self._blueprint_e_fechado(node.name):
            return

        membros = self._membros_implementados(node.name)
        faltando = {}
        for trait in traits:
            exigidos = self._exigidos_de(trait)
            if exigidos is None:
                return        # trait de outro arquivo: nao sei o que exige
            for metodo in sorted(exigidos):
                if metodo not in membros:
                    faltando.setdefault(metodo, trait)

        if not faltando:
            return
        lista = ", ".join(f"{m}() (de '{t}')" for m, t in sorted(faltando.items()))
        plural = "methods" if len(faltando) > 1 else "method"
        self.error(
            f"Blueprint '{node.name}' does not implement "
            f"{len(faltando)} trait {plural}: {lista}", node,
            f"Write {'them' if len(faltando) > 1 else 'it'} in "
            f"'{node.name}', or declare the blueprint 'abstract'",
            "contrato-de-trait")

    def st_TraitDeclaration(self, node, escopo):
        interno = Scope(escopo, "trait")
        interno.declare("self", node.name, node.line, node.column)
        # 'trait Comparavel<T>' — o 'T' e um tipo valido DENTRO do trait.
        for parametro in getattr(node, "type_params", ()) or ():
            self.known_types.add(parametro)
        anterior = self._em_membro
        self._em_membro = True
        try:
            self.visit_block(node.methods, interno)
        finally:
            self._em_membro = anterior
        return False

    def st_RecordDeclaration(self, node, escopo):
        vistos = set()
        genericos = tuple(getattr(node, "type_params", ()) or ())
        for campo, tipo, padrao in node.fields:
            if campo in vistos:
                self.error(f"Duplicate field '{campo}' in record '{node.name}'",
                           node, "Remove the repeated field", "duplicate-field")
            vistos.add(campo)
            alvo = canonical(tipo)
            falta = self._tipo_desconhecido(tipo, genericos)
            if falta:
                self.error(f"Unknown type '{falta}' for field '{campo}'", node,
                           self._hint_tipo(falta), "unknown-type")
            if padrao is not None:
                obtido = self.infer(padrao, escopo)
                if alvo in genericos:
                    continue
                if not self._compativel(alvo, obtido):
                    self.error(
                        f"Default value of '{campo}' is {obtido}, expected {alvo}",
                        node, f"Use a {alvo} as the default", "type-mismatch")
        interno = Scope(escopo, "record")
        interno.declare("self", node.name, node.line, node.column)
        limites = dict(getattr(node, "type_bounds", None) or {})
        for campo, tipo, _ in node.fields:
            # 'T extends Number' É um Number dentro da declaração: é o que
            # deixa escrever 'self.quanto * 2'. Um 'T' solto é UNKNOWN,
            # que é o que o analisador sabe de verdade.
            anotado = canonical(tipo)
            if tipo in genericos:
                anotado = canonical(limites.get(tipo, UNKNOWN))
            interno.declare(campo, anotado, node.line, node.column)
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
            self.modulos_adotados[alias] = node.module
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
            if membro.especie in ("record", "blueprint", "enum"):
                # Ele passa a ser um NOME DE TIPO escrivivel:
                # 'action criar() -> M.Pedido:' e o jeito de tipar num
                # projeto modular, e sem esta linha o analisador
                # respondia "Unknown type 'M.Pedido'" com a lista dos
                # sete embutidos — sugerindo 'Integer' para quem pediu
                # um record que ele mesmo acabou de registrar duas
                # linhas abaixo.
                self.known_types.add(qualificado)
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
    def ex_DecimalLiteral(self, node, escopo): return "Decimal"
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

    def ex_SetLiteral(self, node, escopo):
        tipos = set()
        for e in node.elements:
            tipos.add(self.infer(e.value if isinstance(e, ast.SpreadElement) else e, escopo))
            if isinstance(e, (ast.ListLiteral, ast.DictLiteral, ast.SetLiteral)):
                self.error(
                    "a Set holds only values that do not change; a literal "
                    f"{'Cluster' if isinstance(e, ast.ListLiteral) else 'Vault' if isinstance(e, ast.DictLiteral) else 'Set'} "
                    "can change after it goes in",
                    e, hint="freeze(x), or a tuple (1, 2)", code="set-item-mutavel")
        return "Set"

    def ex_SetComprehension(self, node, escopo):
        interno = self._scope_for_clauses(node.clauses, escopo)
        self.infer(node.expression, interno)
        return "Set"

    def ex_DictLiteral(self, node, escopo):
        self._avisar_chave_repetida(node)
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

    #: Os operadores em que 'Decimal' participa como numero.
    _CONTAS_DE_DECIMAL = ("+", "-", "*", "/", "%", "**", "~/")

    def _conta_com_decimal(self, esq, dir_, node, op):
        """A conta com `Decimal` — e a mistura com `Float` recusada.

        Ela é recusada na linguagem de propósito: um `Decimal` existe para
        ser exato, e somá-lo a um `Float` devolveria um número com o erro
        binário de volta dentro — o exato contaminado pelo aproximado, sem
        nada denunciar.

        Devolve `None` quando não é a sua conta, para o fluxo normal
        seguir (`Decimal * String`, por exemplo, continua sendo o erro
        que já era).
        """
        outro = dir_ if esq == "Decimal" else esq
        if outro == "Decimal" or outro in ("Integer", "Number"):
            # 'Number' passa porque ele pode ser um Integer; recusá-lo
            # aqui acusaria uma ação que recebe 'n: Number' e a usa com
            # um preço, e o analisador não sabe qual dos dois chegou.
            return "Decimal"
        if outro == "Float":
            self.error(
                f"'{op}' between a Decimal and a Float is refused", node,
                'Use a Decimal on both sides (19.99d), or convert on '
                'purpose with Dec.float(x) — and lose the exactness',
                "decimal-com-float")
            return "Decimal"
        return None

    def ex_BinaryOp(self, node, escopo):
        # Um 'type' transparente CONTA como o tipo de baixo: 'Positivo' é
        # um Integer, e sem esta tradução 'x + y' virava "Cannot add
        # Positivo and Positivo" — um falso alarme sobre código certo.
        esq = self._para_a_base(self.infer(node.left, escopo))
        dir_ = self._para_a_base(self.infer(node.right, escopo))
        op = node.op

        if UNKNOWN in (esq, dir_) or ANY in (esq, dir_):
            return UNKNOWN

        # Blueprints e records podem sobrecarregar add/sub/mul/div/mod/pow.
        if self._overloads(esq) or self._overloads(dir_):
            return esq if self._overloads(esq) else dir_

        # 'Decimal' tem regra propria, e ela vem ANTES de NUMERIC.
        #
        # Pôr 'Decimal' dentro de NUMERIC faria 'Decimal + Float' passar
        # no 'check' — e a execução o RECUSA. Seria trocar um erro pego
        # por um silêncio, que é a pior das trocas: o programa quebraria
        # na primeira conta, longe de quem escreveu o literal.
        if "Decimal" in (esq, dir_) and op in self._CONTAS_DE_DECIMAL:
            resultado = self._conta_com_decimal(esq, dir_, node, op)
            if resultado is not None:
                return resultado

        if op == '+':
            # 'void' em texto e erro, e aqui ele e PROVAVEL antes de rodar.
            # '"Ola, " + nome' devolvia '"Ola, void"' — a palavra 'void'
            # impressa onde devia ir o nome, e o analisador calava porque
            # o resultado era um 'String' legitimo. O tipo estava certo e
            # o programa errado.
            if "String" in (esq, dir_) and "Void" in (esq, dir_):
                self.error(
                    "Cannot add Void to text", node,
                    'Give it a default:  x ?? ""  — or render it on '
                    'purpose with  $"{x}", which keeps the word "void"',
                    "void-em-texto")
                return "String"
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

    def _compativel(self, esperado, obtido):
        """'compatible', mais a herança: a filha serve onde se espera a mãe.

        A função solta compara NOMES, e por isso 'usar(b: Base)' recebendo
        uma 'Filha' era acusado de erro — "espera Base, e recebeu Filha".
        É polimorfismo básico, o motivo de a herança existir, e o 'check'
        o recusava; a execução, que olha a MRO, aceitava.

        Um trait adotado conta como mãe, pelo mesmo motivo: é o que um
        parâmetro 'm: Medivel' quer dizer.

        Cala quando a linhagem de 'obtido' passa por algo que este arquivo
        não viu: a mãe de outro módulo pode herdar de 'esperado', e acusar
        ali seria o falso alarme de sempre.
        """
        if self.tipos_nomeados:
            decidido = self._compativel_nomeado(esperado, obtido)
            if decidido is not None:
                return decidido
            # 'type Coordenada := Tuple<Float, Float>' dentro de outro
            # genérico: 'Tuple<Coordenada, Coordenada>' e
            # 'Tuple<Tuple<Float, Float>, …>' são o MESMO tipo, e sem
            # expandir os dois lados o analisador acusa código certo.
            aberto_esperado = self._expandir_aliases(esperado)
            aberto_obtido = self._expandir_aliases(obtido)
            if (aberto_esperado, aberto_obtido) != (esperado, obtido) and \
                    compatible(aberto_esperado, aberto_obtido):
                return True
        if compatible(esperado, obtido):
            return True
        if obtido not in self.blueprints:
            return False
        if esperado in self._linhagem(obtido):
            return True
        return not self._blueprint_e_fechado(obtido)

    def _compativel_nomeado(self, esperado, obtido):
        """O lado esperado é um 'type'? Então quem decide é ele. None = não é.

        Um tipo OPACO é nominal: só serve o que veio do construtor, e o
        que o analisador sabe disso é o tipo inferido ('Cpf' sai de
        'Cpf(…)'). Um transparente vale pela base — é o que faz um alias
        não atrapalhar nada.
        """
        if esperado == obtido:
            return True
        partes = self._partes_do_tipo(esperado)
        if partes is None:
            return None
        especie, nomes, opaco = partes
        if opaco:
            return obtido in (UNKNOWN, ANY, esperado, base_do_tipo(esperado))
        if especie == "uniao":
            return any(self._compativel(n, obtido) for n in nomes)
        if especie == "intersecao":
            # Provar interseção exige a linhagem inteira dos dois lados;
            # quando não dá para provar, o analisador cala.
            return all(self._compativel(n, obtido) for n in nomes) or \
                obtido in (UNKNOWN, ANY)
        return self._compativel(nomes[0], obtido)

    def _ordenavel(self, tipo):
        """O tipo que decide a ordem: o de baixo, opaco ou não."""
        declaracao = self._declaracao_de_tipo(tipo)
        if declaracao is not None and declaracao.opaco:
            return canonical(declaracao.partes[0])
        return self._para_a_base(tipo)

    def _expandir_aliases(self, tipo, vistos=()):
        """Troca todo alias transparente pelo tipo de baixo, inclusive
        dentro de um genérico. Um tipo opaco NÃO se abre: ele é nominal."""
        if not isinstance(tipo, str) or not self.tipos_nomeados:
            return tipo
        if "<" in tipo:
            base, argumentos = partir_tipo(tipo)
            return juntar_tipo(self._expandir_aliases(base, vistos),
                               [self._expandir_aliases(a, vistos)
                                for a in argumentos])
        declaracao = self._declaracao_de_tipo(tipo)
        if declaracao is None or declaracao.opaco or tipo in vistos \
                or declaracao.especie != "alias":
            return tipo
        return self._expandir_aliases(
            canonical(declaracao.partes[0]), vistos + (tipo,))

    def _para_a_base(self, tipo, vistos=()):
        """'Positivo' -> 'Integer'. Um tipo opaco NÃO se desfaz: ele é
        nominal, e tratá-lo como o de baixo desligaria a proteção."""
        declaracao = self._declaracao_de_tipo(tipo)
        if declaracao is None or declaracao.opaco or tipo in vistos:
            return tipo
        if declaracao.especie != "alias":
            return UNKNOWN          # união e interseção: o que se sabe é pouco
        return self._para_a_base(
            canonical(self._trocar_parametros(declaracao,
                                              declaracao.partes[0], tipo)),
            vistos + (tipo,))

    def _partes_do_tipo(self, nome):
        """(especie, partes, opaco) de um 'type' — inclusive 'Par<Integer>'.

        Vale também para a união escrita direto na anotação
        ('Integer | String'), que é a mesma coisa sem nome.
        """
        if isinstance(nome, str) and ("|" in nome or "&" in nome):
            especie, partes = separar_uniao(nome)
            if especie != "alias":
                return especie, partes, False
        declaracao = self._declaracao_de_tipo(nome)
        if declaracao is None:
            return None
        partes = [self._trocar_parametros(declaracao, p, nome)
                  for p in declaracao.partes]
        return declaracao.especie, partes, declaracao.opaco

    def _declaracao_de_tipo(self, nome):
        if not isinstance(nome, str) or not self.tipos_nomeados:
            return None
        achado = self.tipos_nomeados.get(nome)
        if achado is not None:
            return achado
        if "<" in nome:
            return self.tipos_nomeados.get(partir_tipo(nome)[0])
        return None

    def _trocar_parametros(self, declaracao, parte, usado):
        """'type Par<T> := Cluster<T>' visto como 'Par<Integer>'."""
        if not declaracao.type_params or "<" not in usado:
            return parte
        argumentos = partir_tipo(usado)[1]
        troca = dict(zip(declaracao.type_params, argumentos))
        for parametro, valor in troca.items():
            parte = re.sub(rf"\b{re.escape(parametro)}\b", valor, parte)
        return parte

    def _linhagem(self, nome, vistos=None):
        """Todas as mães e traits de um blueprint, transitivamente."""
        vistos = vistos if vistos is not None else set()
        for mae in self.maes.get(nome, ()):
            if mae not in vistos:
                vistos.add(mae)
                self._linhagem(mae, vistos)
        return vistos

    def _overloads(self, tipo):
        """O tipo pode definir operadores próprios (add, mul, ...)?"""
        return tipo in self.blueprints or tipo in self.records

    @staticmethod
    def _inteiro_literal(no):
        """O valor, se o nó for um inteiro escrito à mão. Senão, `None`.

        Trata o sinal: `step -1` chega como `UnaryOp('-')` em volta de um
        literal, e ignorar isso faria a checagem calar justamente no laço
        decrescente, que é o caso em que ela mais serve.
        """
        if isinstance(no, ast.IntegerLiteral):
            return no.value
        if isinstance(no, ast.UnaryOp) and no.op in ('-', '+'):
            dentro = TypeChecker._inteiro_literal(no.operand)
            if dentro is None:
                return None
            return -dentro if no.op == '-' else dentro
        return None

    #: O magico que responde por cada operador unario.
    _MAGICO_UNARIO = {"-": "__neg__", "+": "__pos__", "~": "__invert__"}

    def ex_UnaryOp(self, node, escopo):
        tipo = self.infer(node.operand, escopo)
        if tipo in (UNKNOWN, ANY) or tipo in NUMERIC:
            return tipo
        # Um blueprint que declara '__neg__' aceita '-obj', e a
        # execucao o honra. Acusar aqui e acusar codigo que roda — e um
        # falso alarme sobre um recurso que a propria referencia
        # documenta ensina a ignorar o analisador.
        magico = self._MAGICO_UNARIO.get(node.op)
        if magico and tipo in self.blueprints:
            if magico in self._membros_com_heranca(tipo):
                return tipo
            # Um blueprint que herda de algo nao visto pode ganhar o
            # magico por heranca: ali o analisador cala.
            if self._linhagem_incompleta(tipo):
                return tipo
        self.error(f"Unary '{node.op}' does not apply to {tipo}", node,
                   "Use it on a number", "operator-types")
        return tipo

    def _linhagem_incompleta(self, nome, vistos=None):
        """Ha um ancestral que este arquivo nao declara?"""
        vistos = vistos or set()
        if nome in vistos:
            return False
        vistos.add(nome)
        for mae in self.maes.get(nome, ()):
            if mae not in self.blueprints or self._linhagem_incompleta(
                    mae, vistos):
                return True
        return False

    def ex_NotOp(self, node, escopo):
        self.infer(node.operand, escopo)
        return "Boolean"

    def ex_ComparisonOp(self, node, escopo):
        # Um 'type' transparente vale pela base; um opaco compara com
        # outro do MESMO tipo, delegando ao que ele embrulha.
        esq = self._ordenavel(self.infer(node.left, escopo))
        dir_ = self._ordenavel(self.infer(node.right, escopo))
        if node.op in ('bigger', 'smaller', 'bigger_eq', 'smaller_eq'):
            if UNKNOWN not in (esq, dir_) and ANY not in (esq, dir_):
                if esq in NUMERIC and dir_ in NUMERIC:
                    pass
                elif esq == dir_ and esq in ORDERABLE:
                    pass
                elif self._overloads(esq) or self._overloads(dir_):
                    # Um blueprint ou record ordena a si mesmo com
                    # '__lt__'. O ramo aritmetico ja consultava isto; a
                    # comparacao nao, e acusava "Cannot order Dinheiro
                    # against Dinheiro" num arquivo que roda — um falso
                    # alarme no unico lugar em que a mensagem soa
                    # absurda, porque os dois lados sao o MESMO tipo.
                    pass
                else:
                    self.error(
                        f"Cannot order {esq} against {dir_}", node,
                        "Compare values of the same comparable type", "compare-types")
        elif node.op in ('is', 'isnt', '==', '!='):
            self._conferir_igualdade(node, esq, dir_)
        return "Boolean"

    #: O que uma comparacao de igualdade entre tipos diferentes pode ser
    #: de propósito. Cada entrada aqui é uma razão para CALAR.
    #:
    #:  Void      'x is void' é o idioma de "veio algo?", e o mais comum
    #:            que existe. Acusá-lo tornaria a regra inútil no ato.
    #:  numérico  '1 is 1.0' é verdadeiro: Integer e Float se comparam.
    #:  Boolean   'yes is 1' é verdadeiro — um booleano É um inteiro por
    #:            dentro, e quem escreve isso pode estar contando com
    #:            aquilo.
    _IGUALDADE_LIVRE = frozenset({"Void", "Boolean"})

    def _e_concreto(self, tipo):
        """O nome designa um tipo de verdade, e não um lugar para um tipo.

        `Integer` é concreto; o `T` de um genérico não é. A diferença
        importa porque toda conferência que compara dois tipos precisa
        calar diante do segundo — e o parâmetro de tipo chega aqui com
        cara de tipo, que é o que torna o engano fácil.
        """
        return (tipo in self.known_types or tipo in self.records
                or tipo in self.enums or tipo in self.blueprints)

    def _conferir_igualdade(self, node, esq, dir_):
        """`1 is "1"` é sempre `no`, e quem escreveu não queria isso.

        A comparação de igualdade entre dois tipos diferentes não é erro —
        ela responde, e a resposta é sempre a mesma. É por isso que é
        aviso: o programa roda, e roda errado em silêncio, que é a pior
        combinação e a que nenhuma ferramenta mencionava.
        """
        if UNKNOWN in (esq, dir_) or ANY in (esq, dir_):
            return
        if esq == dir_:
            return
        # So tipos CONCRETOS. Um parametro de tipo — o 'T' de
        # 'action primeiro<T>(…) -> T' — nao e um tipo: e um nome que
        # representa qualquer um, e 'primeiro([1,2,3]) is 1' e verdadeiro.
        # Sem esta linha, a trilha do repositorio ganhava dois alarmes
        # falsos no capitulo que ENSINA generics.
        if not self._e_concreto(esq) or not self._e_concreto(dir_):
            return
        if esq in NUMERIC and dir_ in NUMERIC:
            return
        if self._IGUALDADE_LIVRE & {esq, dir_}:
            return
        # Um record ou blueprint decide a própria igualdade com '__eq__',
        # e comparar dois tipos dele pode ter resposta.
        if self._overloads(esq) or self._overloads(dir_):
            return

        sempre = "no" if node.op in ('is', '==') else "yes"
        self.warn(
            f"Comparing {esq} with {dir_} is always '{sempre}'", node,
            f"They are different types, so '{node.op}' never changes its "
            f"answer. Convert one side — 'str(x)', 'int(x)' — or compare "
            f"'typeof(x)'", "igualdade-impossivel")

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
        # ── A armadilha da precedência ──────────────────────
        #
        #     lambda x => "sim" given x bigger 3 otherwise "nao"
        #
        # O corpo do lambda é `"sim"`, e o ternário recebe o LAMBDA
        # como valor-se-verdadeiro. O `x` da condição está FORA do
        # lambda, e a mensagem que saía era "Undefined name 'x'" —
        # apontando o parâmetro que a própria linha acabou de declarar,
        # como se ele não existisse.
        #
        # É a mesma família do pipeline dentro de lambda, que já ganhou
        # mensagem própria. Aqui o sinal é seguro: um lambda como
        # valor-se-verdadeiro de um ternário é raríssimo, e um cujo
        # parâmetro aparece na CONDIÇÃO é sempre este engano.
        alvo = node.then_value
        if isinstance(alvo, ast.LambdaExpression):
            params = set(getattr(alvo, "params", None) or [])
            usados = (_nomes_usados(node.condition)
                      | _nomes_usados(node.else_value))
            vazando = sorted(params & usados)
            if vazando:
                self.error(
                    f"'{vazando[0]}' is a parameter of the lambda and is "
                    f"used outside it", node,
                    "the lambda body binds tighter than 'given': wrap it — "
                    "lambda x => (a given c otherwise b)",
                    "lambda-precedencia")
                return UNKNOWN
        self.infer(node.condition, escopo)
        a = self.infer(node.then_value, escopo)
        b = self.infer(node.else_value, escopo)
        return a if a == b else UNKNOWN

    def ex_CoalesceOp(self, node, escopo):
        """`v["k"] ?? padrao` — e o `??` resgata a chave ausente.

        O interpretador trata o lado esquerdo de um `??` com indulgencia:
        `v["b"] ?? "padrao"` devolve `"padrao"` em vez de levantar. Logo a
        conferencia de chave constante tem de CALAR aqui — e este e o caso
        que mais importa, porque `?? padrao` e exatamente o que a dica
        daquele erro recomenda. Um analisador que acusa o conserto que ele
        proprio sugere e um analisador que se desliga.
        """
        self._sob_coalesce += 1
        try:
            self.infer(node.left, escopo)
        finally:
            self._sob_coalesce -= 1
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
            if isinstance(op, ast.QuadroOperation):
                resultado = self._verbo_de_quadro(op, escopo)
                continue
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

    #: O que cada verbo de quadro DEVOLVE. 'agrupar' e o unico que nao
    #: devolve quadro: ele devolve um agrupamento, que so vira tabela
    #: depois de um 'resumir'.
    _DEVOLVE_DO_VERBO = {
        "onde": "Quadro", "pegar": "Quadro", "sem": "Quadro",
        "ordenar": "Quadro", "resumir": "Quadro", "agrupar": "Grupo",
    }

    def _verbo_de_quadro(self, op, escopo):
        """Confere um `>> onde …` e devolve o tipo que ele produz.

        A expressão de um `onde` NÃO é inferida no escopo de fora: os
        nomes dela são COLUNAS, e o analisador não sabe quais colunas um
        quadro tem em tempo de análise. Inferir ali acusaria
        `onde valor bigger 50` com "'valor' is not defined" — um falso
        alarme no caminho mais comum do verbo, que é exatamente o que
        ensina a desligar a verificação inteira.

        O que ele confere é o que consegue provar: que 'agrupar' é
        seguido de 'resumir', e que o verbo existe.
        """
        if op.verbo == "resumir" and op.expressao is not None:
            # O vault de agregações é expressão comum: ele se infere.
            self.infer(op.expressao, escopo)
        return self._DEVOLVE_DO_VERBO.get(op.verbo, UNKNOWN)

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
        self._conferir_indice_constante(node)
        return UNKNOWN

    def _conferir_indice_constante(self, node):
        """`xs[10]` num cluster de três, e `v["b"]` num vault sem `b`.

        Os dois erros já aparecem — na primeira vez que aquela linha
        executa. Num arquivo de quarenta linhas isso é imediato; num ramo
        raro de um sistema, é produção. A informação para provar existe
        desde a atribuição, e era só não jogá-la fora.

        Confere a fonte de duas formas: o literal escrito ali mesmo
        (`[1, 2, 3][9]`) e o nome que guarda um literal que ninguém mexe —
        ver `_recolher_literais_fixos`, que é onde mora a prudência.
        """
        if self._sob_coalesce:
            return
        origem = node.object
        fato = None
        if isinstance(origem, ast.Identifier):
            fato = self._literais_fixos.get(origem.name)
            onde = f"'{origem.name}'"
        elif isinstance(origem, ast.ListLiteral):
            if not any(isinstance(e, ast.SpreadElement) for e in origem.elements):
                fato = ("Cluster", len(origem.elements))
            onde = "this cluster"
        elif isinstance(origem, ast.DictLiteral):
            chaves = {c.value for c, _ in origem.pairs
                      if isinstance(c, ast.StringLiteral)}
            if len(chaves) == len(origem.pairs):
                fato = ("Vault", chaves)
            onde = "this vault"
        if fato is None:
            return

        especie, conteudo = fato
        if especie == "Cluster":
            indice = self._inteiro_literal(node.index)
            if indice is None:
                return
            # O índice negativo conta do fim, e -n é válido num cluster
            # de n. Tratar o negativo como sempre fora acusaria 'xs[-1]',
            # que é a forma normal de pegar o último.
            if -conteudo <= indice < conteudo:
                return
            self.error(
                f"Index {indice} is out of range: {onde} has "
                f"{conteudo} item(s)", node,
                (f"valid indexes go from 0 to {conteudo - 1}, or -1 to "
                 f"-{conteudo} from the end") if conteudo else
                "it is empty, so no index is valid", "indice-fora-do-alcance")
        else:
            if not isinstance(node.index, ast.StringLiteral):
                return
            chave = node.index.value
            if chave in conteudo:
                return
            listadas = ", ".join(f'"{c}"' for c in sorted(conteudo))
            self.error(
                f'Key "{chave}" is not in {onde}', node,
                (self._hint_nome(chave, conteudo)
                 or (f"it has: {listadas}" if conteudo else "it is empty"))
                + '. Use  v["k"] ?? padrao  when the key may be absent',
                "chave-ausente")

    def ex_SliceAccess(self, node, escopo):
        alvo = self.infer(node.object, escopo)
        for parte in (node.start, node.stop, node.step):
            if parte is not None:
                tipo = self.infer(parte, escopo)
                if tipo not in (UNKNOWN, ANY) and tipo != "Integer":
                    self.error(f"Slice bounds must be Integer, got {tipo}", node,
                               "Use whole numbers in the slice", "slice-type")
        return alvo if alvo in ("Cluster", "String") else UNKNOWN

    def _molde_do_tipo(self, tipo):
        """'Caixa<Integer>' -> 'Caixa', quando 'Caixa' e declarado aqui.

        Sem isto, ESCREVER o argumento de tipo DESLIGAVA a conferencia de
        membro. `p: Par<Integer, String>` e depois `p.naoExiste` passava
        limpo, porque a busca era `alvo in self.records` e a chave e
        'Par' — com os argumentos, nenhum ramo casava e a funcao caia no
        `return UNKNOWN`.

        O defeito ja existia para `record`, que podia ser anotado assim
        desde sempre; ligar o `blueprint` a mesma anotacao o estenderia.
        E ele e da pior especie: escrever MAIS informacao de tipo compra
        MENOS verificacao, em silencio.

        So tira os argumentos quando a base e um molde conhecido: uma
        `Cluster<Integer>` precisa deles — e o ramo que confere
        `xs.append("x")` le exatamente esses.
        """
        if not isinstance(tipo, str) or "<" not in tipo:
            return tipo
        base = base_do_tipo(tipo)
        if base in self.records or base in self.blueprints:
            return base
        return tipo

    def ex_MemberAccess(self, node, escopo):
        alvo = self._molde_do_tipo(
            self.infer(node.object, escopo))

        if alvo in self.records:
            campos = self.records[alvo]
            # Um metodo de record e um nome valido aqui, e ele nao mora em
            # 'campos'. Sem esta linha, 'f := p.norma' — passar o metodo
            # adiante como valor, que a linguagem permite e o interpretador
            # faz — era acusado de "has no field 'norma'": um falso alarme
            # no codigo certo, que e o defeito que ensina a desligar a
            # verificacao inteira.
            metodos = self.record_methods.get(alvo, set())
            if node.member in metodos:
                return UNKNOWN
            if node.member not in campos and node.member not in ('fields', 'record_name'):
                self.error(
                    f"Record '{alvo}' has no field '{node.member}'", node,
                    self._hint_nome(node.member, set(campos) | metodos) or
                    f"Fields: {', '.join(campos)}", "unknown-field")
                return UNKNOWN
            return self._tipo_de_campo(alvo, campos.get(node.member, UNKNOWN))

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
        if self._linhagem_dinamica(tipo):
            return               # '__getattr__' ou metaclasse: nada a provar

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

    def _linhagem_dinamica(self, tipo, vistos=None):
        vistos = vistos or set()
        if tipo in vistos:
            return False
        vistos.add(tipo)
        if tipo in self.dinamicos:
            return True
        return any(self._linhagem_dinamica(m, vistos) for m in self.maes.get(tipo, ()))

    def ex_SafeMemberAccess(self, node, escopo):
        self.infer(node.object, escopo)
        return UNKNOWN

    #: Os metodos que INSEREM, e onde esta o que eles inserem.
    _INSEREM = {"append": 0, "push": 0, "insert": 1, "add": 0}

    #: Perguntas sobre o estado: valem em qualquer momento.
    _PERGUNTAM_O_ESTADO = ("vivo", "movido", "solto", "contar", "fracas",
                           "emprestimos", "estado")
    #: Os métodos que TIRAM a posse de quem chamou.
    _TIRAM_A_POSSE = ("mover", "soltar")
    #: O que cria um recurso com liberação determinística.
    _CRIAM_RECURSO = ("dono", "compartilhado", "atomico")

    def ex_MethodCall(self, node, escopo):
        self._conferir_posse(node, escopo)
        self._conferir_emprestimo(node)
        self._recurso_escapou(*node.args, *node.kwargs.values())
        alvo = self.infer(node.object, escopo)
        for a in node.args:
            self.infer(a.value if isinstance(a, ast.SpreadElement) else a, escopo)
        for v in node.kwargs.values():
            self.infer(v, escopo)

        # 'xs.append("x")' num Cluster<Integer>: o literal prova o erro
        if isinstance(alvo, str) and "<" in alvo:
            base, argumentos = partir_tipo(alvo)
            posicao = self._INSEREM.get(node.method)
            if base in ("Cluster", "Set") and posicao is not None \
                    and len(node.args) > posicao:
                self._conferir_item(argumentos[0], node.args[posicao], escopo,
                                    alvo, f"the item of {node.method}")
            elif base == "Cluster" and node.method == "extend" and node.args:
                self._conferir_conteudo(alvo, node.args[0], escopo)
            elif base == "Vault" and node.method == "set" and len(node.args) >= 2:
                self._conferir_item(argumentos[0], node.args[0], escopo, alvo, "the key")
                self._conferir_item(argumentos[1], node.args[1], escopo, alvo, "the value")

        # 'c.guardar("texto")' num Caixa<Integer>: o literal prova o erro.
        self._conferir_argumento_generico(alvo, node, escopo)

        # Os argumentos de tipo ja foram usados acima (é o ramo das
        # coleções que os lê). Daqui para baixo fala-se do MOLDE, e sem
        # esta linha 'c: Caixa<Integer>' desligava a conferência de
        # método — ver `_molde_do_tipo`.
        alvo = self._molde_do_tipo(alvo)

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
        # 'p.naoExiste()' num record. O acesso a campo era conferido e a
        # CHAMADA nao — um quarto da conferencia faltando, e justamente na
        # forma que mais se escreve. O erro existia em execucao; aqui ele
        # passa a aparecer antes de rodar, como no blueprint ao lado.
        #
        # Um campo pode guardar uma acao, e 'p.f()' com 'f' entre os campos
        # e legitimo: so acusa quem nao esta em nenhum dos dois.
        elif alvo in self.records:
            campos = self.records[alvo]
            metodos = self.record_methods.get(alvo, set())
            if node.method not in campos and node.method not in metodos:
                nomes = set(campos) | metodos
                self.error(
                    f"Record '{alvo}' has no field or method '{node.method}'",
                    node,
                    self._hint_nome(node.method, nomes) or
                    f"It has: {', '.join(sorted(nomes))}", "unknown-field")
        return UNKNOWN

    def _conferir_argumento_generico(self, tipo, node, escopo):
        """'c.guardar("texto")' num `Caixa<Integer>` — acusado na causa.

        O erro JA existia em execução, e aparecia no lugar errado: o
        parâmetro de um `T` sem limite não é conferido, o campo recebia o
        texto calado, e a queixa saía na leitura seguinte —
        *"a variável 'n' declared as Integer but got String"*, uma linha
        depois e sobre outro nome. Quem lê vai depurar o `n`.

        Aqui o `check` resolve `T` pelo argumento da anotação e cobra o
        literal, na linha que causa. Ele **cala** quando não consegue
        concluir: sem anotação de tipo não há vínculo, e um `T` que não
        aparece na lista de parâmetros do molde não é substituível.
        """
        if not isinstance(tipo, str) or "<" not in tipo:
            return
        base, argumentos = partir_tipo(tipo)
        parametros, _limites = self.genericos_de_tipo.get(base, ((), {}))
        # Aridade diferente é outro erro, e o parser já o acusa. Concluir
        # daqui com listas de tamanhos diferentes casaria o argumento
        # errado com o parâmetro errado.
        if not parametros or len(parametros) != len(argumentos):
            return
        assinatura = self.assinaturas_de_metodo.get(base, {}).get(node.method)
        if assinatura is None:
            return

        troca = dict(zip(parametros, argumentos))
        for indice, arg in enumerate(node.args):
            if indice >= len(assinatura.params) \
                    or isinstance(arg, ast.SpreadElement):
                continue
            nome_do_parametro = assinatura.params[indice]
            declarado = assinatura.param_types.get(nome_do_parametro, UNKNOWN)
            esperado = troca.get(declarado)
            if not esperado:
                continue
            obtido = self.infer(arg, escopo)
            if not self._compativel(canonical(esperado), obtido):
                self.error(
                    f"Parameter '{nome_do_parametro}' of '{node.method}' is a "
                    f"{declarado}, and this is a {tipo} — so {declarado} is "
                    f"{esperado}, but got {obtido}", arg,
                    f"Pass a {esperado}, or annotate as "
                    f"{base}<{obtido}>", "generic-argument")

    def _tipo_declarado_do_campo(self, molde, campo, vistos=None):
        """O tipo declarado de um campo, subindo a linhagem.

        Um campo herdado é tão declarado quanto um próprio, e a mãe é
        quem costuma declarar o genérico. A filha vence: é o que ela
        escreve que vale, e a primeira versão do irmão deste método no
        interpretador empilhava ao contrário — `campo: T` da filha
        virava o `campo: String` da mãe, e a conferência falava do tipo
        errado.
        """
        vistos = vistos or set()
        if molde in vistos:
            return None                  # herança circular: outro erro
        vistos.add(molde)

        proprio = self.tipos_de_campo.get(molde, {})
        if campo in proprio:
            return proprio[campo]
        if molde in self.records:
            do_record = self.records[molde].get(campo)
            if do_record:
                return do_record
        for mae in self.maes.get(molde, []):
            herdado = self._tipo_declarado_do_campo(mae, campo, vistos)
            if herdado:
                return herdado
        return None

    def _conferir_campo_generico(self, node, escopo):
        """`c.guardado := "texto"` num `Caixa<Integer>`, antes de rodar.

        A execução já recusa isto desde que a instância passou a
        carregar o vínculo (`DFInstance._tipos`): a mensagem é
        *"field 'guardado' of Caixa<Integer> declared as Integer but got
        String"*. O que faltava era o `check` dizer o mesmo **antes**,
        que é a diferença entre descobrir num teste e descobrir no dia
        em que aquele ramo roda.

        Ele **cala** em tudo que não consegue provar, e cada silêncio
        tem motivo:

        | Cala quando | Porque |
        |---|---|
        | o objeto não tem tipo anotado | sem anotação não há vínculo — `spawn Caixa()` solto aceita qualquer coisa, e é assim que a maioria do código cria instância |
        | a aridade não fecha | casar listas de tamanhos diferentes parearia o argumento errado com o parâmetro errado, e o parser já acusa a aridade |
        | o campo não é um parâmetro de tipo puro | `itens: Cluster<T>` precisaria descer na coleção, e um alarme impreciso aqui é pior que silêncio |
        | o valor é de tipo desconhecido | o analisador é otimista de propósito |
        """
        alvo = node.target
        if not isinstance(alvo.object, ast.Identifier):
            return
        do_objeto = escopo.lookup(alvo.object.name)
        if not isinstance(do_objeto, str) or "<" not in do_objeto:
            return

        base, argumentos = partir_tipo(do_objeto)
        parametros, _limites = self.genericos_de_tipo.get(base, ((), {}))
        if not parametros or len(parametros) != len(argumentos):
            return

        declarado = self._tipo_declarado_do_campo(base, alvo.member)
        esperado = dict(zip(parametros, argumentos)).get(declarado)
        if not esperado:
            return

        obtido = self.infer(node.value, escopo)
        if obtido in (UNKNOWN, ANY):
            return
        if not self._compativel(canonical(esperado), obtido):
            self.error(
                f"Field '{alvo.member}' is a {declarado}, and this is a "
                f"{do_objeto} — so {declarado} is {esperado}, but got "
                f"{obtido}", node.value or node,
                f"Assign a {esperado}, or annotate "
                f"'{alvo.object.name}' as {base}<{obtido}>",
                "generic-field")

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
            if obtido and not self._compativel(esperado, obtido):
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
            if obtido and not self._compativel(esperado, obtido):
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

        self._recurso_escapou(*node.args, *node.kwargs.values())
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

        opaco = self._declaracao_de_tipo(nome)
        if opaco is not None and opaco.opaco:
            return self._check_chamada_de_opaco(opaco, node, escopo)

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
            if declarado in assinatura.type_params:
                limite = assinatura.type_bounds.get(declarado)
                obtido = self.infer(arg, escopo)
                if limite and not self._compativel(canonical(limite), obtido):
                    self.error(
                        f"Parameter '{assinatura.params[indice]}' of '{nome}' is a "
                        f"{declarado}, and {declarado} extends {limite} — but got "
                        f"{obtido}", arg,
                        f"Pass a {limite}", "generic-bound")
                continue
            if declarado in (UNKNOWN, ANY):
                continue
            obtido = self.infer(arg, escopo)
            rotulo = f"parameter '{assinatura.params[indice]}' of '{nome}'"
            if not self._compativel(declarado, obtido):
                if self._declaracao_de_tipo(declarado) is not None:
                    self._acusar_tipo(declarado, obtido, arg, rotulo.capitalize())
                else:
                    self.error(
                        f"Parameter '{assinatura.params[indice]}' of '{nome}' expects "
                        f"{declarado} but got {obtido}", arg,
                        f"Pass a {declarado}", "argument-type")
            else:
                self._conferir_conteudo(declarado, arg, escopo)
                self._provar_nomeado(declarado, arg, escopo, rotulo.capitalize())

        if assinatura.is_generator:
            return "Stream"
        return assinatura.return_type

    def _conferir_posse(self, node, escopo):
        """Usar um valor depois de mover é usar o que já não se tem.

        A marca é por NOME e vale a partir da linha do 'mover'. Reatribuir
        o nome limpa: dali em diante ele é outro valor. Um nome que não
        veio de 'P.dono(…)' nunca entra aqui — o analisador cala sobre o
        que não viu nascer.
        """
        if not isinstance(node.object, ast.Identifier):
            return
        nome = node.object.name
        if nome not in self.posse_criada:
            return
        movido_em = self.posse_movida.get(nome)
        # Perguntar o ESTADO de um dono movido é legítimo — é a pergunta
        # que se faz justamente depois de mover.
        if node.method in self._PERGUNTAM_O_ESTADO:
            return
        if movido_em is not None:
            self.error(
                f"'{nome}' já foi movido com 'mover': quem move, perde a posse",
                node,
                f"o valor saiu daqui na linha {movido_em} — use o nome que o "
                f"recebeu", "posse-movida")
            return
        if node.method in self._TIRAM_A_POSSE and nome in self.recursos_abertos:
            del self.recursos_abertos[nome]
            if node.method == "mover":
                self.posse_movida[nome] = node.line
        elif node.method == "mover":
            self.posse_movida[nome] = node.line

    #: Os métodos que entregam o valor por um TEMPO — o corpo que os
    #: recebe é o escopo do empréstimo.
    _EMPRESTAM = ("usar", "mudar", "ler", "escrever")

    def _conferir_emprestimo(self, node):
        """'d.usar(lambda x => x)' devolve o que foi emprestado.

        O valor sai do corpo que o recebeu e passa a viver por fora, onde
        o dono já não controla nada — é o empréstimo que escapa do
        escopo, e é a única forma dele que dá para provar lendo o código.
        """
        if node.method not in self._EMPRESTAM or len(node.args) != 1:
            return
        corpo = node.args[0]
        if not isinstance(corpo, ast.LambdaExpression) or not corpo.params:
            return
        if isinstance(corpo.body, ast.Identifier) and \
                corpo.body.name == corpo.params[0]:
            self.warn(
                f"este '{node.method}' devolve o próprio valor emprestado",
                node,
                "o empréstimo vale enquanto o corpo roda — faça o trabalho "
                "dentro dele, ou copie o que precisa levar",
                "emprestimo-escapa")

    def _recurso_escapou(self, *valores):
        """O recurso saiu do alcance desta ação — e deixa de ser cobrado.

        Vale para o 'yield', para o argumento de qualquer chamada e para
        o campo de um objeto: a partir dali quem solta é outro, e este
        arquivo não tem como saber quem.
        """
        for valor in valores:
            if isinstance(valor, ast.Identifier):
                self.recursos_abertos.pop(valor.name, None)

    def _anotar_recurso(self, node, escopo):
        """'d := P.dono(…)' — a partir daqui alguém tem de soltar."""
        if not isinstance(node.target, ast.Identifier):
            return
        nome = node.target.name
        self.posse_movida.pop(nome, None)
        valor = node.value
        if isinstance(valor, ast.MethodCall) and \
                valor.method in self._CRIAM_RECURSO and \
                isinstance(valor.object, ast.Identifier) and \
                self._e_modulo_de_posse(valor.object.name):
            self.recursos_abertos[nome] = node
            self.posse_criada.add(nome)
        else:
            self.recursos_abertos.pop(nome, None)
            # 'd := outra_coisa' — o nome deixou de ser aquele recurso.
            if isinstance(valor, ast.MethodCall) and valor.method == "mover" \
                    and isinstance(valor.object, ast.Identifier) \
                    and valor.object.name in self.posse_criada:
                self.posse_criada.add(nome)
                self.recursos_abertos[nome] = node
            else:
                self.posse_criada.discard(nome)

    def _e_modulo_de_posse(self, apelido):
        """O apelido aponta para 'Arcane.Posse'? Só ele conta."""
        return self.modulos_adotados.get(apelido, "") in ("Arcane.Posse", "Posse")

    def _cobrar_recursos_soltos(self, escopo, node):
        """No fim da ação, o que ninguém soltou vira aviso — não erro.

        Aviso porque a análise é de um arquivo só: o recurso pode ser
        guardado num campo, entregue a outra ação por um caminho que
        este arquivo não vê, ou solto num 'defer'. Acusar como erro
        ensinaria a desligar a verificação.
        """
        for nome, criacao in list(self.recursos_abertos.items()):
            self.warn(
                f"'{nome}' abre um recurso que ninguém solta nesta ação", criacao,
                "solte com 'soltar()', entregue com 'mover()', ou use "
                "'P.com(dono, acao)', que solta até quando o corpo falha",
                "recurso-vazado")
        self.recursos_abertos.clear()

    def _check_chamada_de_opaco(self, declaracao, node, escopo):
        """'Cpf("…")' — um argumento, do tipo de baixo, e sai um Cpf."""
        nome = declaracao.name
        if len(node.args) != 1 or node.kwargs:
            self.error(
                f"'{nome}' takes exactly one value: the {declaracao.partes[0]} "
                f"it wraps", node, f"Write {nome}(valor)", "arity")
            return nome
        base = canonical(declaracao.partes[0])
        obtido = self.infer(node.args[0], escopo)
        if not self._compativel(base, obtido):
            self.error(
                f"'{nome}' wraps a {base} but got {obtido}", node.args[0],
                f"Pass a {base}", "tipo-opaco")
        else:
            self._provar_regra(declaracao, node.args[0], escopo,
                               f"'{nome}(…)'")
        return nome

    def _check_record_call(self, nome, node, escopo):
        campos = self.records[nome]
        genericos = self.genericos_de_tipo.get(nome, ((), {}))
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
        parametros, limites = genericos
        for indice, arg in enumerate(node.args):
            if indice >= len(campos):
                break
            campo = list(campos)[indice]
            esperado = campos[campo]
            obtido = self.infer(arg, escopo)
            if esperado in parametros:
                # '<T>' solto documenta e aceita tudo; '<T extends X>' e
                # verificavel, e por isso e verificado — as duas metades,
                # aqui e na execucao.
                limite = limites.get(esperado)
                if limite and not self._compativel(canonical(limite), obtido):
                    self.error(
                        f"Field '{campo}' of record '{nome}' is a {esperado}, "
                        f"and {esperado} extends {limite} — but got {obtido}",
                        arg, f"Pass a {limite}", "generic-bound")
                continue
            if not self._compativel(esperado, obtido):
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
            if nome in self.contratos:
                self.error(f"'{nome}' is a contract and cannot be spawned", node,
                           f"spawn a blueprint declared 'with {nome}'",
                           "spawn-de-contrato")
            return nome
        return UNKNOWN

    def _avisar_chave_repetida(self, node):
        """`{"a": 1, "a": 2}` fica com o 2, e o 1 desaparece calado.

        A regra da linguagem é essa e não muda — mas escrever a mesma chave
        duas vezes no MESMO literal é sempre engano, e é o tipo de engano
        que se lê por cima.
        """
        vistas, repetidas = set(), []
        for chave, _ in node.pairs:
            if not isinstance(chave, ast.StringLiteral):
                continue
            if chave.value in vistas and chave.value not in repetidas:
                repetidas.append(chave.value)
            vistas.add(chave.value)
        if repetidas:
            lista = ", ".join(f'"{c}"' for c in repetidas)
            self.warn(
                f"a chave {lista} aparece duas vezes neste vault", node,
                "a última vence, e a primeira desaparece sem erro — "
                "apague uma das duas", "chave-repetida")

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

    def ex_TupleLiteral(self, node, escopo):
        """'(1, "a")' — o tipo traz a forma: 'Tuple<Integer, String>'.

        Saber a forma é o que deixa o analisador provar tamanho e posição
        antes de rodar. Um item de tipo desconhecido apaga a forma
        inteira: metade de uma prova não prova nada.
        """
        partes = [self.infer(item, escopo) for item in node.elements]
        if not partes or any(p in (UNKNOWN, ANY) for p in partes):
            return "Tuple"
        return juntar_tipo("Tuple", partes)

    def ex_FrameExpression(self, node, escopo):
        self.infer(node.data, escopo)
        return "Vault"

    # ── Sugestões ──────────────────────────────────────────

    def _hint_nome(self, nome, candidatos):
        parecido = self._similar(nome, candidatos)
        if parecido:
            return f"Did you mean '{parecido}'?"
        return ""

    def _tipo_de_campo(self, dono, tipo):
        """O tipo de um campo, traduzido quando ele é um parâmetro.

        'record Medida<T extends Number>' com 'quanto: T': dentro da
        declaração, 'self.quanto' É um Number — é o que deixa escrever
        'self.quanto * 2'. Um 'T' solto vira UNKNOWN, que é o que o
        analisador sabe de verdade; tratá-lo como tipo faria
        "Cannot multiply T by Integer" num código que roda.
        """
        parametros, limites = self.genericos_de_tipo.get(dono, ((), {}))
        if tipo in parametros:
            return canonical(limites.get(tipo, UNKNOWN))
        return tipo

    def _e_parametro_de_tipo(self, tipo):
        """'T' de um '<T>' declarado em qualquer lugar deste arquivo."""
        return any(tipo in parametros
                   for parametros, _ in self.genericos_de_tipo.values()) or \
            any(tipo in (a.type_params or ())
                for a in self.actions.values()
                if getattr(a, "type_params", None))

    def _tipo_conhecido(self, tipo, genericos=()):
        """Todo nome dentro de 'Vault<String, Cluster<Pedido>>' existe?"""
        if "|" in tipo or "&" in tipo:
            _, partes = separar_uniao(tipo)
            return all(self._tipo_conhecido(p, genericos) for p in partes)
        if "<" not in tipo:
            alvo = canonical(tipo)
            return (alvo in self.known_types or alvo == UNKNOWN
                    or tipo in genericos or "." in tipo)
        base, argumentos = partir_tipo(tipo)
        return (self._tipo_conhecido(base, genericos)
                and all(self._tipo_conhecido(a, genericos)
                        or _e_numero(a) for a in argumentos))

    def _tipo_desconhecido(self, tipo, genericos=()):
        """O primeiro nome que nao existe — o que a dica deve corrigir."""
        if "|" in tipo or "&" in tipo:
            for parte in separar_uniao(tipo)[1]:
                falta = self._tipo_desconhecido(parte, genericos)
                if falta:
                    return falta
            return None
        if "<" not in tipo:
            return None if self._tipo_conhecido(tipo, genericos) else tipo
        base, argumentos = partir_tipo(tipo)
        for parte in (base,) + tuple(argumentos):
            # 'Vetor<3>': o 3 e um VALOR — o tamanho faz parte do tipo.
            if _e_numero(parte):
                continue
            falta = self._tipo_desconhecido(parte, genericos)
            if falta:
                return falta
        return None

    def _conferir_conteudo(self, esperado, valor, escopo, onde="value"):
        """O literal cabe no 'Cluster<T>' / 'Vault<K, V>' declarado?

        So acusa o que PROVA: um item cujo tipo foi inferido e nao serve.
        Um item de tipo desconhecido — uma chamada, um nome de fora —
        cala, pelo mesmo motivo de todo o resto do analisador.
        """
        if not isinstance(esperado, str) or "<" not in esperado:
            return
        base, argumentos = partir_tipo(canonical(esperado))
        if base == "Tuple" and isinstance(valor, ast.TupleLiteral):
            if len(valor.elements) != len(argumentos):
                self.error(
                    f"{esperado} has {len(argumentos)} place(s), and this "
                    f"tuple has {len(valor.elements)}", valor,
                    "The size of a Tuple is part of its type",
                    "tipo-do-conteudo")
                return
            for indice, (item, tipo) in enumerate(zip(valor.elements, argumentos)):
                self._conferir_item(tipo, item, escopo, esperado,
                                    f"place {indice}")
            return
        if base in ("Cluster", "Set") and isinstance(valor, ast.ListLiteral):
            for indice, item in enumerate(valor.elements):
                if isinstance(item, ast.SpreadElement):
                    continue
                self._conferir_item(argumentos[0], item, escopo, esperado,
                                    f"item {indice}")
        elif base == "Vault" and isinstance(valor, ast.DictLiteral):
            for chave, item in valor.pairs:
                if isinstance(chave, ast.SpreadElement):
                    continue
                rotulo = (f'the key "{chave.value}"' if isinstance(chave, ast.StringLiteral)
                          else "a key")
                self._conferir_item(argumentos[0], chave, escopo, esperado, rotulo)
                self._conferir_item(argumentos[1], item, escopo, esperado,
                                    f"the value of {rotulo}")

    def _conferir_item(self, tipo, no, escopo, colecao, rotulo):
        # 'Cluster<T>' com 'T' de '<T>': o parametro documenta a relacao,
        # e aceita qualquer valor. Cobrar aqui acusaria 'primeiro([1])',
        # que e o uso certo do generico.
        if self._e_parametro_de_tipo(tipo):
            return
        if "<" in tipo:
            self._conferir_conteudo(tipo, no, escopo)
        obtido = self.infer(no, escopo)
        if obtido in (UNKNOWN, ANY) or self._compativel(tipo, obtido):
            return
        self.error(f"{colecao} cannot hold {obtido}: {rotulo} is {obtido}", no,
                   f"every item has to be a {tipo} — fix the value, or widen the "
                   f"annotation (Any accepts everything)", "tipo-do-conteudo")

    def _hint_tipo(self, nome):
        parecido = self._similar(nome, self.known_types)
        if parecido:
            return f"Did you mean '{parecido}'?"
        return f"Known types: Integer, Float, String, Boolean, Cluster, Vault, Void"


def _nomes_usados(no, achados=None):
    """Todo Identifier que aparece nesta subárvore."""
    achados = set() if achados is None else achados
    if isinstance(no, ast.Identifier):
        achados.add(no.name)
    for campo in getattr(no, "__dataclass_fields__", ()):
        valor = getattr(no, campo, None)
        if isinstance(valor, ast.ASTNode):
            _nomes_usados(valor, achados)
        elif isinstance(valor, (list, tuple)):
            for item in valor:
                if isinstance(item, ast.ASTNode):
                    _nomes_usados(item, achados)
    return achados


def check_program(program, filename="<stdin>", strict=False, source=None):
    """Analisa um programa e devolve a lista de diagnósticos.

    `source` e opcional: com ela, os '// df: permitir <regra>' sao
    lidos sem tocar o disco — o que importa para o LSP, que reanalisa
    a cada tecla e tem o texto do editor, ainda nao salvo.
    """
    verificador = TypeChecker(filename=filename, strict=strict, source=source)
    return verificador.check(program)
