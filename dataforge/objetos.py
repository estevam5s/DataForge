"""
O runtime de OOP que nao cabe no caminho quente do interpretador.

`interpreter.py` guarda o que roda em TODA chamada e em TODO acesso a
membro. O que so roda quando um blueprint pede — contrato, sobrecarga,
invariante, metaclasse, trava por objeto, propriedade preguicosa — mora
aqui, e o interpretador so paga por isso com uma leitura de atributo:

    acao.extras is None          a acao nao tem nada de especial
    blueprint.vigias is None     o blueprint nao tem invariante nem meta
    instancia._estado is None    o objeto nunca foi congelado, travado,
                                 nem esta sendo construido

Tres `None`, e o programa que nao usa nada disto roda como antes. Foi a
condicao para trazer os recursos: o interpretador ja tem sete gargalos
medidos e resolvidos, e nenhum deles podia voltar por causa de um
recurso que a maioria dos programas nao usa.

─── Por que um objeto de estado, e nao campos na instancia ─────────

`DFInstance` usa `__slots__`, e cada slot custa oito bytes em TODA
instancia. Congelar, travar e construir sao raros; um slot so, que
aponta para um `EstadoDoObjeto` quando algum deles acontece, mantem a
instancia comum do tamanho de sempre.
"""

import difflib
import threading

from .errors import (
    AmbiguousOverloadError, FrozenObjectError, InvariantError,
    MetaclassError, OverloadResolutionError, PostconditionError,
    PreconditionError, ReadOnlyFieldError,
)


# ═════════════════════════════════════════════════════════════
#  Os ganchos de metaclasse
# ═════════════════════════════════════════════════════════════

#: nome -> (parametros, quando roda). A ordem e a da doc.
GANCHOS_DE_META = {
    "on_forge":       ("molde",
                       "o blueprint acabou de ser montado; devolver outro o substitui"),
    "on_extend":      ("mae, filha",
                       "um blueprint governado ganhou uma filha"),
    "on_spawn":       ("molde, args",
                       "antes de construir; devolver um objeto o entrega no lugar"),
    "on_ready":       ("obj",
                       "o objeto terminou de nascer, invariantes conferidas"),
    "on_read":        ("obj, nome, valor",
                       "toda leitura de membro; devolver algo troca o valor lido"),
    "on_missing":     ("obj, nome",
                       "leitura de um membro que nao existe"),
    "on_write":       ("obj, nome, valor",
                       "toda escrita de campo; devolver algo troca o valor gravado"),
    "on_call":        ("obj, nome, args",
                       "antes de cada chamada de metodo vinda de fora do objeto"),
    "on_serialize":   ("obj, vault",
                       "Objetos.para_vault; devolver um vault o substitui"),
    "on_deserialize": ("molde, vault",
                       "Objetos.de_vault, antes de montar; devolver um vault o substitui"),
}


def conferir_ganchos(meta_bp):
    """Um 'meta blueprint' so declara ganchos que existem.

    'on_forje' em vez de 'on_forge' nunca rodaria, e nada avisaria: a
    metaclasse pareceria ignorada. Por isso todo metodo 'on_…' precisa
    ser um gancho conhecido.
    """
    for nome in meta_bp.methods:
        if nome.startswith("on_") and nome not in GANCHOS_DE_META:
            perto = difflib.get_close_matches(nome, GANCHOS_DE_META, n=1)
            raise MetaclassError(
                f"'{meta_bp.name}.{nome}' is not a metaclass hook.",
                nota="a meta blueprint method starting with 'on_' is a hook, "
                     "and this one would never run",
                dica=(f"did you mean '{perto[0]}'?" if perto else
                      "the hooks are: " + ", ".join(GANCHOS_DE_META)),
                doc="oop/metaclasses")


# ═════════════════════════════════════════════════════════════
#  Estado por objeto, vigias por blueprint, extras por acao
# ═════════════════════════════════════════════════════════════

class EstadoDoObjeto:
    """O que so alguns objetos precisam guardar."""

    __slots__ = ("construindo", "congelado", "trava", "profundidade", "cache")

    def __init__(self):
        self.construindo = False
        self.congelado = False
        self.trava = None
        #: Quantas chamadas de metodo estao abertas NESTE objeto. A
        #: invariante e conferida quando volta a zero: dentro de um metodo
        #: o objeto pode estar, de passagem, num estado intermediario.
        self.profundidade = 0
        #: 'lazy get' — nome -> valor ja calculado
        self.cache = None


_TRAVA_DO_ESTADO = threading.Lock()


def estado_de(obj):
    """O estado do objeto, criado na primeira vez que alguem precisa."""
    estado = obj._estado
    if estado is None:
        with _TRAVA_DO_ESTADO:
            estado = obj._estado
            if estado is None:
                estado = obj._estado = EstadoDoObjeto()
    return estado


def trava_de(obj):
    """A trava reentrante do objeto, para 'exclusive action'.

    Reentrante porque um metodo exclusivo que chama outro do mesmo objeto
    e o caso normal — com uma trava simples, ele esperaria por si mesmo
    para sempre.
    """
    estado = estado_de(obj)
    if estado.trava is None:
        with _TRAVA_DO_ESTADO:
            if estado.trava is None:
                estado.trava = threading.RLock()
    return estado.trava


class Vigias:
    """O que um blueprint confere a cada operacao. None quando nada.

    Juntado da linhagem inteira na declaracao: uma invariante da mae vale
    na filha, e a metaclasse e herdada.
    """

    __slots__ = ("invariantes", "ganchos", "meta")

    def __init__(self, invariantes=(), ganchos=None, meta=None):
        #: [(no, escopo, nome_do_blueprint)]
        self.invariantes = list(invariantes)
        #: nome do gancho -> DFAction do meta blueprint
        self.ganchos = dict(ganchos or {})
        #: a instancia do meta blueprint — 'self' dentro dos ganchos
        self.meta = meta

    def vazio(self):
        return not self.invariantes and not self.ganchos


class Extras:
    """O que uma acao tem de especial. None na quase totalidade delas."""

    __slots__ = ("variantes", "promessas", "antes", "exclusivo", "grupo")

    def __init__(self):
        #: overload: as variantes, na ordem em que foram escritas
        self.variantes = None
        #: [PromisesStatement]
        self.promessas = ()
        #: [BeforeExpression] dentro das promessas — avaliados na ENTRADA
        self.antes = ()
        self.exclusivo = False
        #: o nome do grupo de sobrecarga, para a mensagem
        self.grupo = ""


def nos_before(no):
    """Todo 'before(expr)' dentro de uma expressao, em ordem."""
    from . import ast_nodes as ast
    achados = []

    def andar(x):
        if isinstance(x, ast.BeforeExpression):
            achados.append(x)
            return
        if isinstance(x, ast.ASTNode):
            for valor in vars(x).values():
                andar(valor)
        elif isinstance(x, (list, tuple)):
            for item in x:
                andar(item)
        elif isinstance(x, dict):
            for item in x.values():
                andar(item)

    andar(no)
    return achados


# ═════════════════════════════════════════════════════════════
#  Sobrecarga
# ═════════════════════════════════════════════════════════════

def aridade(acao):
    """(minimo, maximo) de argumentos posicionais."""
    total = len(acao.params)
    obrigatorios = sum(1 for p in acao.params if p not in acao.defaults)
    return obrigatorios, total


def assinatura(acao):
    """'area(l: Float, a: Float)' — para mensagens."""
    partes = []
    for p in acao.params:
        tipo = acao.param_types.get(p)
        texto = f"{p}: {tipo}" if tipo else p
        if p in acao.defaults:
            texto += " := …"
        partes.append(texto)
    return f"{acao.name}({', '.join(partes)})"


def mesma_assinatura(a, b):
    """Duas variantes que nenhuma chamada consegue distinguir."""
    if aridade(a) != aridade(b):
        return False
    return all(a.param_types.get(pa) == b.param_types.get(pb)
               for pa, pb in zip(a.params, b.params))


def resolver_sobrecarga(interp, acao, args, kwargs, node):
    """A variante que a chamada pede.

    Duas passadas. A primeira filtra pela quantidade e pelos nomes; a
    segunda confere os TIPOS declarados, com a mesma regra que a
    anotacao usa em qualquer chamada. Entre as que servem, vence a mais
    especifica — a que declara mais tipos. Um empate e erro: escolher
    pela ordem em que foram escritas faria mover uma variante de lugar
    mudar o resultado de um programa que nao a chama.
    """
    candidatas = []
    for variante in acao.extras.variantes:
        minimo, maximo = aridade(variante)
        if len(args) > maximo:
            continue
        if any(k not in variante.params for k in kwargs):
            continue
        preenchidos = set(variante.params[:len(args)]) | set(kwargs)
        if any(p not in preenchidos and p not in variante.defaults
               for p in variante.params):
            continue
        valores = dict(zip(variante.params, args))
        valores.update(kwargs)
        serve = True
        tipados = 0
        for nome, valor in valores.items():
            tipo = variante.param_types.get(nome)
            if not tipo:
                continue
            if not interp._serve_ao_tipo(valor, tipo, variante):
                serve = False
                break
            # o tipo EXATO vale mais que o que so aceita: um Integer serve
            # onde se pede Float, e 'f(3)' com as duas variantes nao pode
            # empatar — a de Integer e a que quem escreveu quis
            exato = interp.TYPE_ALIASES.get(tipo, tipo) == interp._type_of(valor)
            tipados += 2 if exato else 1
        if serve:
            candidatas.append((tipados, variante))

    if not candidatas:
        opcoes = "\n".join("    " + assinatura(v) for v in acao.extras.variantes)
        tipos = ", ".join(interp._type_of(a) for a in args)
        raise OverloadResolutionError(
            f"No overload of '{acao.extras.grupo}' accepts ({tipos}).",
            node.line, node.column,
            nota="the variants are:\n" + opcoes,
            dica="pass arguments that one variant accepts, or declare the "
                 "variant that is missing",
            doc="oop/sobrecarga")

    melhor = max(t for t, _ in candidatas)
    empatadas = [v for t, v in candidatas if t == melhor]
    if len(empatadas) > 1:
        opcoes = "\n".join("    " + assinatura(v) for v in empatadas)
        raise AmbiguousOverloadError(
            f"The call to '{acao.extras.grupo}' matches {len(empatadas)} "
            f"overloads equally well.",
            node.line, node.column,
            nota="these accept the arguments with the same precision:\n" + opcoes,
            dica="declare the parameter types that tell them apart",
            doc="oop/sobrecarga")
    return empatadas[0]


# ═════════════════════════════════════════════════════════════
#  Construcao, escrita e contrato
# ═════════════════════════════════════════════════════════════

def conferir_escrita(obj, nome, node):
    """Levanta se o campo nao pode ser escrito agora. Nao escreve."""
    estado = obj._estado
    if estado is not None and estado.congelado:
        raise FrozenObjectError(
            f"'{obj.blueprint.name}' is frozen: cannot assign to '{nome}'.",
            node.line, node.column,
            nota="Objetos.congelar made every field read-only for good",
            dica="work on a copy:  outro := Objetos.clonar(obj)",
            doc="oop/objetos")
    somente = obj.blueprint.somente_leitura
    if somente and nome in somente and (estado is None or not estado.construindo):
        raise ReadOnlyFieldError(
            f"'{obj.blueprint.name}.{nome}' is readonly and the object is "
            f"already built.",
            node.line, node.column,
            nota="a readonly field is assigned while the object is born: in "
                 "its default, the header or 'setup'",
            dica="build another object, or remove 'readonly' if the field "
                 "really changes",
            doc="oop/modificadores")


def falha_de_contrato(classe, texto, node, nota="", dica=""):
    return classe(texto, node.line, node.column, nota=nota, dica=dica,
                  doc="oop/contratos")


__all__ = [
    "GANCHOS_DE_META", "EstadoDoObjeto", "Vigias", "Extras", "estado_de",
    "trava_de", "nos_before", "aridade", "assinatura", "mesma_assinatura",
    "resolver_sobrecarga", "conferir_escrita", "conferir_ganchos",
    "falha_de_contrato", "PreconditionError", "PostconditionError",
    "InvariantError",
]
