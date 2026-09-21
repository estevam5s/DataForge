"""
DataForge Interpreter
Tree-walking interpreter that executes AST nodes.
"""

import collections as _collections
from functools import partial as _functools_partial
import numbers as _numeros
import re as _re
import sys
import threading
import time
import asyncio

from . import ast_nodes as ast
from .environment import Environment
from . import magicos
from . import objetos
from .colecoes_tipadas import (Tupla as _Tupla, partir as _partir_tipo,
                               tipar as _tipar_colecao)
from .builtins import (BuiltinFunction, get_builtins,
                       set_magic_dispatcher, set_stringifier,
                       set_repr)
from .caminhos import curto as _curto
from .cauda import MARCA as _MARCA_CAUDA
from . import tipos_nomeados as _TiposNomeados
from .tipos_nomeados import ALIAS, INTERSECAO, UNIAO, Opaco
from .errors import (
    ChamadaDeCauda,
    ControlSignal,
    DataForgeError, Frame, RuntimeError_, TypeError_, NameError_, TriggerError,
    HaltSignal, SkipSignal, YieldSignal, IndexError_, ImportError_,
    StackOverflowError_,
    erro_por_nome, ERROS_POR_NOME,
    DivisionByZeroError, ConversionError, NullReferenceError, ValueError_,
    ImmutableError, ConstantReassignmentError, UnpackError, OperatorError,
    ComparisonError, RangeError, ArithmeticOverflowError, StateError,
    ArityError, NotCallableError, NotIterableError, NotIndexableError,
    NotHashableError, UndefinedMemberError, KeyError_, EmptyCollectionError,
    SliceError, ValueNotFoundError, SortKeyError, NegativeSizeError,
    PrivateAccessError, ProtectedAccessError, AbstractInstantiationError,
    TraitContractError, FinalOverrideError, ReadOnlyPropertyError,
    FinalBlueprintError, SealedBlueprintError, OverrideTargetError,
    AmbiguousOverloadError, MetaclassError, AugmentError, InternalAccessError,
    SignatureMismatchError, UnknownTraitError, PreconditionError,
    PostconditionError, InvariantError,
    RecordMutationError, UnknownFieldError, EnumMemberError, EnumValueError,
    ModuleNotFoundError_, CircularImportError, IOError_, FileNotFoundError_,
    PermissionError_, SerializationError, RegexError, DateTimeError,
    ObjectError, EncodingError, FormatError, MemoryLimitError,
    NotImplementedError_, InfiniteLoopError,
)


#: Marcador de "este metodo magico nao existe, ou nao soube responder".
#:
#: Precisa ser um objeto proprio, e nao None: um '__add__' que devolve
#: 'void' devolveu um valor — e confundir os dois faria a soma cair no
#: caminho numerico e estourar com uma mensagem sobre tipos.
class _SemMagico:
    __slots__ = ()

    def __repr__(self):
        return "<sem metodo magico>"


_SEM_MAGICO = _SemMagico()

#: O fim de um percurso do Python, para quem nao pode confundi-lo com
#: 'void': um stream pode legitimamente produzir 'void' como item.
_FIM = object()


# ── DataForge Runtime Objects ──────────────────────────────

def _agrupar_por(itens, chave):
    """Agrupa numa vault: {valor_da_chave: [itens]}."""
    grupos = {}
    for item in itens:
        grupos.setdefault(chave(item), []).append(item)
    return grupos


def _intercalar(itens, separador):
    """Poe o separador entre os itens, nao nas pontas."""
    saida = []
    for i, item in enumerate(itens):
        if i:
            saida.append(separador)
        saida.append(item)
    return saida


def _flatten_deep(lst):
    """Recursively flatten nested lists."""
    result = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            result.extend(_flatten_deep(item))
        else:
            result.append(item)
    return result

def _unique_list(lst):
    """Remove duplicates preserving order."""
    seen = set()
    result = []
    for item in lst:
        key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def _reduce_list(lst, func, initial=None):
    """Reduce a list with a function."""
    from functools import reduce as _reduce
    if initial is not None:
        return _reduce(func, lst, initial)
    return _reduce(func, lst)

def _freq_list(lst):
    """Count frequencies in a list."""
    freq = {}
    for item in lst:
        key = str(item)
        freq[key] = freq.get(key, 0) + 1
    return freq

def _dict_set(d, key, val):
    """Set a key in dict and return dict."""
    d[key] = val
    return d

def _dict_delete(d, key):
    """Delete key from dict and return value."""
    return d.pop(key, None)

#: Os metodos embutidos de vault, texto e cluster — montados UMA vez.
#:
#: Eles moravam DENTRO de '_ler_membro_cru', como literais de dicionario
#: cheios de lambdas que capturavam 'obj'. A cada 'xs.append(i)', a cada
#: '"a".upper()', o interpretador construia a tabela inteira — 76 lambdas
#: para texto, 51 para cluster — escolhia uma e jogava o resto fora. Medido
#: num laco de 200 mil 'append': 0,5 s so nisso, o maior custo por operacao
#: do interpretador, e nada a ver com arvore ou bytecode.
#:
#: Agora cada lambda recebe o objeto como primeiro argumento, e o acesso
#: liga so o escolhido ('_ligar_ao_objeto'). O comportamento e o mesmo,
#: inclusive a mensagem de aridade: o nome continua '<lambda>'.
_METODOS_DE_VAULT = {
    'keys': lambda obj: list(obj.keys()),
    'values': lambda obj: list(obj.values()),
    'items': lambda obj: [list(p) for p in obj.items()],
    'has': lambda obj, key: key in obj,
    'contains': lambda obj, key: key in obj,
    'get': lambda obj, key, default=None: obj.get(key, default),
    'set': lambda obj, key, val: _dict_set(obj, key, val),
    'delete': lambda obj, key: _dict_delete(obj, key),
    'length': lambda obj: len(obj),
    'merge': lambda obj, other: {**obj, **other},
    'update': lambda obj, other: (obj.update(other), obj)[-1],
    'clear': lambda obj: (obj.clear(), obj)[-1],
    'copy': lambda obj: dict(obj),
    'pick': lambda obj, *ks: {k: obj[k] for k in ks if k in obj},
    'omit': lambda obj, *ks: {k: v for k, v in obj.items() if k not in ks},
    'invert': lambda obj: {v: k for k, v in obj.items()},
    'map_values': lambda obj, f: {k: f(v) for k, v in obj.items()},
    'filter_keys': lambda obj, f: {k: v for k, v in obj.items() if f(k)},
    'to_pairs': lambda obj: [list(p) for p in obj.items()],
}

_METODOS_DE_TEXTO = {
    'length': lambda obj: len(obj),
    'upper': lambda obj: obj.upper(),
    'lower': lambda obj: obj.lower(),
    'strip': lambda obj, chars=None: obj.strip(chars),
    'lstrip': lambda obj, chars=None: obj.lstrip(chars),
    'rstrip': lambda obj, chars=None: obj.rstrip(chars),
    'title': lambda obj: obj.title(),
    'capitalize': lambda obj: obj.capitalize(),
    'swapcase': lambda obj: obj.swapcase(),
    'center': lambda obj, w, f=" ": obj.center(w, f),
    'ljust': lambda obj, w, f=" ": obj.ljust(w, f),
    'rjust': lambda obj, w, f=" ": obj.rjust(w, f),
    'zfill': lambda obj, w: obj.zfill(w),
    'split': lambda obj, sep=" ": obj.split(sep),
    'replace': lambda obj, old, new, count=-1: obj.replace(old, new) if count == -1 else obj.replace(old, new, count),
    'startswith': lambda obj, prefix: obj.startswith(prefix),
    'endswith': lambda obj, suffix: obj.endswith(suffix),
    'find': lambda obj, sub, start=0: obj.find(sub, start),
    'rfind': lambda obj, sub, start=0: obj.rfind(sub, start),
    'index_of': lambda obj, sub, start=0: obj.find(sub, start),
    'last_index_of': lambda obj, sub: obj.rfind(sub),
    'char_at': lambda obj, i: obj[i] if 0 <= i < len(obj) else "",
    'substring': lambda obj, start, end=None: obj[start:end],
    'slice': lambda obj, start, end=None: obj[start:end],
    'contains': lambda obj, sub: sub in obj,
    'includes': lambda obj, sub: sub in obj,
    'isalpha': lambda obj: obj.isalpha(),
    'isdigit': lambda obj: obj.isdigit(),
    'isalnum': lambda obj: obj.isalnum(),
    'isspace': lambda obj: obj.isspace(),
    'isupper': lambda obj: obj.isupper(),
    'islower': lambda obj: obj.islower(),
    'istitle': lambda obj: obj.istitle(),
    'isnumeric': lambda obj: obj.isnumeric(),
    'repeat': lambda obj, n: obj * n,
    'reverse': lambda obj: obj[::-1],
    'trim': lambda obj: obj.strip(),
    'pad_start': lambda obj, l, f=" ": obj.rjust(l, f),
    'pad_end': lambda obj, l, f=" ": obj.ljust(l, f),
    'concat': lambda obj, *args: obj + "".join(str(a) for a in args),
    'count': lambda obj, sub: obj.count(sub),
    'expandtabs': lambda obj, ts=8: obj.expandtabs(ts),
    'partition': lambda obj, sep: list(obj.partition(sep)),
    'rpartition': lambda obj, sep: list(obj.rpartition(sep)),
    'splitlines': lambda obj, keepends=False: obj.splitlines(keepends),
    'removeprefix': lambda obj, pfx: obj[len(pfx):] if obj.startswith(pfx) else obj,
    'removesuffix': lambda obj, sfx: obj[:-len(sfx)] if sfx and obj.endswith(sfx) else obj,
    'words': lambda obj: obj.split(),
    'lines': lambda obj: obj.splitlines(),
    'encode': lambda obj, enc="utf-8": list(obj.encode(enc)),
    'format': lambda obj, *a, **kw: obj.format(*a, **kw),
    'join': lambda obj, it: obj.join(str(x) for x in it),
    # O resto da linguagem e snake_case ('index_of', 'pad_start',
    # 'char_at'). Estes nomes vieram do Python e destoavam: quem
    # escrevia o obvio 'starts_with' recebia "membro nao existe".
    'starts_with': lambda obj, prefix: obj.startswith(prefix),
    'ends_with': lambda obj, suffix: obj.endswith(suffix),
    'is_alpha': lambda obj: obj.isalpha(),
    'is_digit': lambda obj: obj.isdigit(),
    'is_alnum': lambda obj: obj.isalnum(),
    'is_space': lambda obj: obj.isspace(),
    'is_upper': lambda obj: obj.isupper(),
    'is_lower': lambda obj: obj.islower(),
    'is_title': lambda obj: obj.istitle(),
    'is_numeric': lambda obj: obj.isnumeric(),
    'is_empty': lambda obj: len(obj) == 0,
    'split_lines': lambda obj, keepends=False: obj.splitlines(keepends),
    'remove_prefix': lambda obj, pfx: obj[len(pfx):] if obj.startswith(pfx) else obj,
    'remove_suffix': lambda obj, sfx: obj[:-len(sfx)] if sfx and obj.endswith(sfx) else obj,
    'expand_tabs': lambda obj, ts=8: obj.expandtabs(ts),
    'trim_start': lambda obj: obj.lstrip(),
    'trim_end': lambda obj: obj.rstrip(),
    'to_upper': lambda obj: obj.upper(),
    'to_lower': lambda obj: obj.lower(),
    'title_case': lambda obj: obj.title(),
    'swap_case': lambda obj: obj.swapcase(),
    'count_of': lambda obj, sub: obj.count(sub),
    'chars': lambda obj: list(obj),
    'bytes': lambda obj, enc="utf-8": list(obj.encode(enc)),
}

_METODOS_DE_CLUSTER = {
    'length': lambda obj: len(obj),
    'append': lambda obj, item: obj.append(item),
    'push': lambda obj, item: obj.append(item),
    'pop': lambda obj, idx=-1: obj.pop(idx),
    'insert': lambda obj, idx, item: obj.insert(idx, item),
    'remove': lambda obj, item: obj.remove(item),
    # Sem 'chave', ordenar vaults ou records era impossivel
    # pela lista — so pela funcao global 'sorted'.
    'sort': lambda obj, chave=None, reverso=False: (
        obj.sort(key=chave, reverse=reverso), obj)[-1],
    'sorted': lambda obj, chave=None, reverso=False:
        sorted(obj, key=chave, reverse=reverso),
    'is_empty': lambda obj: len(obj) == 0,
    'sum_of': lambda obj, f: sum(f(x) for x in obj),
    'group_by': lambda obj, f: _agrupar_por(obj, f),
    'partition': lambda obj, f: [
        [x for x in obj if f(x)], [x for x in obj if not f(x)]],
    'zip_with': lambda obj, outra: [list(t) for t in zip(obj, outra)],
    'index_where': lambda obj, f: next(
        (i for i, x in enumerate(obj) if f(x)), -1),
    'find_last': lambda obj, f: next(
        (x for x in reversed(obj) if f(x)), None),
    'none': lambda obj, f: not any(f(x) for x in obj),
    'sliding': lambda obj, n: [obj[i:i+n] for i in range(len(obj)-n+1)]
        if n <= len(obj) else [],
    'intersperse': lambda obj, sep: _intercalar(obj, sep),
    'compact': lambda obj: [x for x in obj if x is not None],
    'tally': lambda obj: _freq_list(obj),
    'reverse': lambda obj: (obj.reverse(), obj)[-1],
    'contains': lambda obj, item: item in obj,
    'includes': lambda obj, item: item in obj,
    'index': lambda obj, item: obj.index(item),
    'index_of': lambda obj, item: obj.index(item),
    'count': lambda obj, item: obj.count(item),
    'first': lambda obj: obj[0] if obj else None,
    'last': lambda obj: obj[-1] if obj else None,
    'take': lambda obj, n: obj[:n],
    'drop': lambda obj, n: obj[n:],
    'slice': lambda obj, s=None, e=None: obj[s:e],
    'flatten': lambda obj: _flatten_deep(obj),
    'unique': lambda obj: _unique_list(obj),
    'chunk': lambda obj, s: [obj[i:i+s] for i in range(0, len(obj), s)],
    'rotate': lambda obj, n: obj[n%len(obj):] + obj[:n%len(obj)] if obj else [],
    'reversed': lambda obj: list(reversed(obj)),
    'join': lambda obj, sep=", ": sep.join(str(x) for x in obj),
    'map': lambda obj, f: [f(x) for x in obj],
    'filter': lambda obj, f: [x for x in obj if f(x)],
    'reduce': lambda obj, f, init=None: _reduce_list(obj, f, init),
    'every': lambda obj, f: all(f(x) for x in obj),
    'some': lambda obj, f: any(f(x) for x in obj),
    'find': lambda obj, f: next((x for x in obj if f(x)), None),
    'sum': lambda obj: sum(obj),
    'min': lambda obj: min(obj),
    'max': lambda obj: max(obj),
    'mean': lambda obj: sum(obj) / len(obj) if obj else 0,
    'clear': lambda obj: (obj.clear(), obj)[-1],
    'copy': lambda obj: list(obj),
    'extend': lambda obj, other: (obj.extend(other), obj)[-1],
    'frequencies': lambda obj: _freq_list(obj),
}


def _ligar_ao_objeto(metodo, obj):
    """O metodo da tabela, com o objeto ja no primeiro argumento."""
    return _functools_partial(metodo, obj)


class DFAction:
    """A user-defined function (action)."""
    _interpreter = None  # Set during Interpreter.__init__

    def __init__(self, name, params, defaults, body, closure, is_async=False,
                 param_types=None, return_type="", is_generator=False,
                 type_params=None, type_bounds=None):
        self.name = name
        self.params = params
        self.defaults = defaults
        self.body = body
        self.closure = closure
        self.is_async = is_async
        self.param_types = param_types or {}
        self.return_type = return_type
        self.is_generator = is_generator
        # <T> de 'action primeiro<T>(l) -> T' — nomes que valem como
        # tipo dentro desta acao, e aceitam qualquer valor.
        self.type_params = tuple(type_params or ())
        #: <T extends Number> — o limite de cada parametro de tipo. Um 'T'
        #: com limite deixa de aceitar qualquer valor: o valor tem de
        #: servir onde se espera o limite.
        self.type_bounds = dict(type_bounds or {})
        #: "<action nome>", montado na primeira chamada e nao em todas.
        self.nome_do_escopo = None

        # O corpo compilado para fechamentos, montado na primeira
        # chamada. Fica aqui e nao no no da arvore porque o
        # interpretador que compila esta amarrado nos fechamentos: dois
        # interpretadores sobre a mesma arvore — o REPL, os testes —
        # nao podem compartilhar o compilado de outro.
        self.corpo_compilado = None

        # 'yield f(...)' onde 'f' e esta acao vira salto, e nao chamada.
        # None = ainda nao analisado; a analise custa uma varredura da
        # arvore e acontece na primeira chamada.
        self.tem_cauda = None

        # O arquivo onde esta acao foi DECLARADA.
        #
        # Sem isto, um erro dentro de uma acao de modulo importado era
        # reportado com o arquivo e a LINHA DE QUEM CHAMOU: um '1 / 0'
        # na linha 2 de 'lib.df' aparecia como 'main.df:2', com o trecho
        # errado desenhado embaixo da seta. Num projeto de duzentos
        # arquivos, isso manda a pessoa depurar o arquivo errado.
        #
        # O carimbo e AQUI, e nao em quem constroi, porque ha NOVE
        # lugares que criam uma DFAction — metodo de blueprint, de
        # record, propriedade, operador, lambda, metodo magico. Carimbar
        # em cada um deixaria de fora os que vierem depois, e a falta
        # nao da erro: so faz o arquivo errado aparecer na mensagem.
        interp = DFAction._interpreter
        self.arquivo = getattr(interp, "filename", "") if interp else ""

        #: O membro de enum ao qual este metodo ja esta ligado.
        #:
        #: Um metodo de enum e lido a partir do MEMBRO ('Cor.Verde.hex'),
        #: e e o membro que precisa virar 'self' — e ele que tem
        #: '.value'. A ligacao viaja na acao porque entre ler o membro e
        #: chama-lo nao ha nada que carregue o dono.
        self.self_do_enum = None

        #: O blueprint que DECLAROU este metodo, ou None.
        #:
        #: E o que 'root' precisa saber: com tres niveis de heranca, o
        #: blueprint da instancia nao diz de onde continuar a busca, e
        #: 'root' voltava para o mesmo metodo, para sempre.
        self.dono = None

        #: O que esta acao tem de especial — sobrecarga, pos-condicao,
        #: trava — ou None. E a UNICA leitura que uma chamada comum paga
        #: por esses recursos: ver 'objetos.py'.
        self.extras = None

    def __call__(self, *args, **kwargs):
        """Allow DFAction to be called like a Python function."""
        if DFAction._interpreter is None:
            raise RuntimeError("No interpreter available")
        # Create a fake node for error reporting
        class _FakeNode:
            line = 0
            column = 0
        return DFAction._interpreter._call_action(self, list(args), kwargs, _FakeNode(), None)

    def __repr__(self):
        return f"<action '{self.name}'>"


class DFBlueprint:
    """A user-defined class (blueprint)."""

    def __init__(self, name, parents, methods, statics, env,
                 constructor_params=None, constructor_body=None,
                 properties=None, operators=None, fields_decl=None,
                 visibility=None, is_abstract=False, abstract_methods=None,
                 static_methods=None, final_methods=None, traits=None,
                 slots=None, metaclasse=None):
        self.name = name
        self.parents = parents       # list of DFBlueprint
        self.methods = methods       # dict: name → DFAction
        self.statics = statics       # dict: name → value
        self.env = env
        self.constructor_params = constructor_params or []
        self.constructor_body = constructor_body or []
        # ── DataForge 4.1 ──
        self.properties = properties or {}       # nome → {'get': acao, 'set': acao}
        self.operators = operators or {}         # '+' → DFAction
        self.fields_decl = fields_decl or []     # [(nome, tipo, padrao, visib)]
        self.visibility = visibility or {}       # membro → public|private|protected
        self.is_abstract = is_abstract
        self.abstract_methods = abstract_methods or set()
        self.static_methods = static_methods or set()
        self.final_methods = final_methods or set()
        self.traits = traits or []               # nomes dos traits adotados
        # ── DataForge 1.1 ──
        #: Campos permitidos na instancia, ou None para "qualquer um".
        #: Declarar 'slots' faz a instancia guardar os valores numa
        #: LISTA em vez de num dicionario: 64% menos memoria por objeto,
        #: medido. Num programa com um milhao de instancias, isso e a
        #: diferenca entre caber e nao caber.
        self.slots = slots
        #: O indice de cada campo na lista. Fica em None ate a primeira
        #: instancia: ele precisa dos slots EFETIVOS — os proprios mais
        #: os herdados — e os pais podem nem estar prontos aqui.
        self.indice_slots = None
        #: O blueprint que controla a criacao deste — a metaclasse.
        self.metaclasse = metaclasse
        #: A MRO, calculada uma vez. O C3 nao e caro, mas a linhagem e
        #: consultada em toda busca de metodo magico — e ai a conta
        #: apareceria.
        self._mro = None

        # ── OOP 1.2 ──
        self.e_final = False            # 'final blueprint'
        self.e_selado = False           # 'sealed blueprint'
        self.e_meta = False             # 'meta blueprint'
        self.e_contrato = False         # 'contract'
        self.e_trait = False            # 'trait'
        #: O arquivo que declarou — e o que 'sealed' e 'internal' comparam.
        self.arquivo = ""
        #: 'static steady' — nomes de estaticos que nao aceitam escrita
        self.constantes = set()
        #: campos 'readonly' da linhagem inteira
        self.somente_leitura = frozenset()
        #: membros nao publicos da linhagem: so eles pagam a conferencia
        #: de acesso. A busca de visibilidade sobe pelos pais, e fazer
        #: isso em toda leitura de campo publico era custo sem motivo.
        self.nao_publicos = frozenset()
        #: invariantes e ganchos de metaclasse, ou None — ver objetos.Vigias
        self.vigias = None
        #: a metaclasse: o 'meta blueprint' nomeado em 'using' (ou herdado)
        self.meta_blueprint = None
        #: as filhas diretas, por referencia fraca: um blueprint criado e
        #: descartado em tempo de execucao nao pode ficar vivo so por ter
        #: sido filha de alguem.
        self.herdeiros = []
        #: '@Coluna("x")' sobre um campo — nome -> [{nome, args, kwargs}]
        self.metadados_de_campo = {}
        #: contrato: nome -> a acao-assinatura, para conferir aridade
        self.assinaturas = {}
        #: contrato: propriedades exigidas ('get total() -> Integer')
        self.propriedades_exigidas = set()
        #: todos os traits e contratos adotados, inclusive os que um
        #: contrato herda de outro — e o que 'x: Contrato' confere
        self.contratos_todos = frozenset()
        self.tipos_do_cabecalho = {}
        self.padroes_do_cabecalho = {}
        #: 'teardown' ou '__del__': quando existe, a instancia nasce da
        #: subclasse que sabe morrer — as outras nao pagam por isso
        self.finalizador = None
        #: campos cujo padrao e um DESCRITOR (__get__/__set__)
        self.descritores = {}
        #: o metodo magico ja procurado na linhagem, ou None
        self.cache_magico = {}
        #: '__getattribute__' / '__setattr__' declarados na linhagem
        self.leitura_magica = False
        self.escrita_magica = False
        #: a instancia unica de um 'meta blueprint' — o 'self' dos ganchos
        self.instancia_meta = None
        #: O acesso a membro nao tem nada de especial: nem propriedade, nem
        #: descritor, nem gancho, nem '__getattribute__'. E a pergunta que
        #: o caminho quente faz UMA vez, em vez de cinco. Nasce 'no' — o
        #: caminho completo e sempre correto, so mais lento.
        self.leitura_simples = False
        self.escrita_simples = False
        #: 'setup', 'initiate' ou '__init__', achado uma vez
        self.construtor = None

    def recalcular_acesso(self):
        """Recalcula os atalhos depois que o blueprint muda."""
        props = any(bp.properties for bp in self.linhagem())
        especial = (self.leitura_magica or self.vigias is not None or props
                    or bool(self.descritores))
        self.leitura_simples = not especial
        self.escrita_simples = not (especial or self.escrita_magica
                                    or bool(self.somente_leitura))
        self.construtor = next(
            (self.methods[n] for n in ("setup", "initiate", "__init__")
             if isinstance(self.methods.get(n), DFAction)), None)

    def slots_efetivos(self):
        """Os slots deste blueprint e dos ancestrais, juntos.

        Herdar de um blueprint com slots e acrescentar os proprios e o
        caso normal. Se QUALQUER ancestral nao declara slots, a
        restricao cai por terra — ele aceita campo livre, e a instancia
        precisa de um dicionario de qualquer jeito.
        """
        if self.slots is None:
            return None
        juntos = []
        for bp in reversed(self.linhagem()):
            if bp.slots is None:
                return None
            for nome in bp.slots:
                if nome not in juntos:
                    juntos.append(nome)
        return juntos

    def buscar_operador(self, simbolo):
        """O operador sobrecarregado, olhando a cadeia de heranca."""
        if simbolo in self.operators:
            return self.operators[simbolo]
        for pai in self.parents:
            achado = pai.buscar_operador(simbolo)
            if achado is not None:
                return achado
        return None

    def buscar_propriedade(self, nome):
        """A propriedade, olhando a cadeia de heranca."""
        if nome in self.properties:
            return self.properties[nome]
        for pai in self.parents:
            achado = pai.buscar_propriedade(nome)
            if achado is not None:
                return achado
        return None

    def visibilidade_de(self, nome):
        if nome in self.visibility:
            return self.visibility[nome]
        for pai in self.parents:
            v = pai.visibilidade_de(nome)
            if v != "public":
                # private do pai nao vaza para o filho; protected sim.
                # 'internal' e do ARQUIVO, nao da linhagem: continua
                # internal, e quem decide e onde o codigo esta escrito.
                return v if v in ("protected", "internal") else "private"
        return "public"

    def esquecer_caches(self):
        """Um membro mudou em execucao: o que foi calculado perde a validade."""
        self.cache_magico = {}
        self.leitura_magica = self.leitura_magica or any(
            "__getattribute__" in bp.methods for bp in self.linhagem())
        self.escrita_magica = self.escrita_magica or any(
            "__setattr__" in bp.methods for bp in self.linhagem())
        self.recalcular_acesso()
        for ref in list(self.herdeiros):
            filha = ref()
            if filha is not None:
                filha.esquecer_caches()

    def declarante_de(self, nome):
        """O blueprint da linhagem que DECLAROU este membro.

        E o que decide a visibilidade: um metodo de Base acessando um
        'private' de Base funciona mesmo quando 'self' e uma Derivada.
        Comparar com o blueprint da instancia — como se fazia — recusava
        exatamente esse caso, que e o normal em qualquer linguagem com
        heranca.
        """
        # A subclasse COPIA os campos declarados do pai, entao
        # 'fields_decl' nao distingue quem declarou. O que distingue e
        # 'visibility': ele so recebe entrada no blueprint onde o membro
        # aparece escrito. Por isso ele vem primeiro, e o resto e
        # desempate para membros publicos.
        for bp in self.linhagem():
            if nome in bp.visibility:
                return bp
        for bp in self.linhagem():
            if (nome in bp.methods or nome in bp.properties
                    or any(c[0] == nome for c in bp.fields_decl)):
                return bp
        return self

    def linhagem(self):
        r"""A ordem de resolucao de metodos (MRO), por linearizacao C3.

        Com heranca simples, e so a corrente de pais — e o resultado e o
        mesmo de antes. Com heranca multipla, o C3 e o que resolve o
        problema do diamante de um jeito previsivel:

                A
               / \
              B   C
               \ /
                D

        Um metodo que existe em A, B e C precisa de uma regra para
        decidir qual vale em D. A busca em largura, que era o que havia
        aqui, daria [D, B, C, A] — parece certo, mas ela quebra em
        hierarquias mais fundas: ela pode pos um ancestral ANTES de um
        descendente dele, e um metodo da mae sobrescrever o da filha.

        O C3 garante tres coisas: a classe vem antes das maes, a ordem
        em que as maes foram escritas e respeitada, e um ancestral
        nunca aparece antes de quem descende dele. Quando nao ha ordem
        que satisfaca as tres, a hierarquia e ambigua — e ai o C3
        avisa, em vez de escolher em silencio.
        """
        if self._mro is not None:
            return self._mro

        if not self.parents:
            self._mro = [self]
            return self._mro

        def fundir(sequencias):
            resultado = []
            sequencias = [list(s) for s in sequencias if s]
            while sequencias:
                # A cabeca boa e a que nao aparece na CAUDA de nenhuma
                # outra: por-la agora nao adianta ninguem na frente.
                cabeca = None
                for seq in sequencias:
                    candidata = seq[0]
                    if not any(candidata in outra[1:] for outra in sequencias):
                        cabeca = candidata
                        break
                if cabeca is None:
                    nomes = " e ".join(
                        sorted({s[0].name for s in sequencias}))
                    raise InheritanceCycleError(
                        f"'{self.name}' has an ambiguous inheritance order.",
                        nota=f"no consistent order puts {nomes} in place",
                        dica=("reorder the parents, or extract what they "
                              "share into a common ancestor"),
                        doc="oop/heranca")
                resultado.append(cabeca)
                for seq in sequencias:
                    if seq and seq[0] is cabeca:
                        del seq[0]
                sequencias = [s for s in sequencias if s]
            return resultado

        self._mro = [self] + fundir(
            [p.linhagem() for p in self.parents] + [list(self.parents)])
        return self._mro

    def pendencias_abstratas(self):
        """Metodos abstratos herdados que ninguem implementou ainda."""
        faltando = {}
        for bp in reversed(self.linhagem()):
            # 'trait Editavel extends Legivel': quem EXIGE 'ler' e o
            # Legivel. Culpar quem repassou manda procurar no arquivo
            # errado — e num sistema de traits a cadeia e comprida.
            de_onde = getattr(bp, "origem_das_exigencias", None) or {}
            for nome in bp.abstract_methods:
                faltando[nome] = de_onde.get(nome, bp.name)
            for nome, acao in bp.methods.items():
                if nome in faltando and not getattr(acao, "is_abstract", False):
                    faltando.pop(nome)
        return faltando

    def __repr__(self):
        return f"<blueprint '{self.name}'>"


class DFInstance:
    """An instance of a blueprint (spawn).

    Com 'slots' declarados, os valores vao para uma LISTA indexada em
    vez de um dicionario — 64% menos memoria por objeto, medido. O
    campo 'fields' continua existindo como vista, para o resto do
    interpretador nao precisar saber qual dos dois esta em uso.
    """

    __slots__ = ("blueprint", "_valores", "_indice", "_estado", "_tipos",
                 "__weakref__")

    #: Marcador de slot ainda nao preenchido. Nao pode ser None:
    #: 'self.x := void' e uma atribuicao legitima, e confundir os dois
    #: faria um campo atribuido parecer nunca atribuido.
    _VAZIO = object()

    def __init__(self, blueprint: DFBlueprint):
        self.blueprint = blueprint
        indice = blueprint.indice_slots
        if indice is None and blueprint.slots is not None:
            efetivos = blueprint.slots_efetivos()
            if efetivos is not None:
                indice = {n: i for i, n in enumerate(efetivos)}
                blueprint.indice_slots = indice
        self._indice = indice
        self._valores = ([DFInstance._VAZIO] * len(indice)
                         if indice is not None else {})
        #: None ate alguem congelar, travar ou construir com 'readonly' —
        #: ver objetos.EstadoDoObjeto
        self._estado = None
        #: None ate este objeto passar por uma anotacao generica
        #: ('c: Caixa<Integer> := …'), e ai guarda {'T': 'Integer'}.
        #:
        #: Ele NASCE com None, e nao ausente: 'getattr' num slot nunca
        #: atribuido custa 7x mais, porque levanta e captura um
        #: AttributeError por dentro — foi o que comeu o ganho de uma
        #: otimizacao anterior neste mesmo arquivo.
        self._tipos = None

    @property
    def fields(self):
        """Os campos como dicionario — a vista que o resto do codigo usa."""
        if self._indice is None:
            return self._valores
        return {nome: self._valores[i] for nome, i in self._indice.items()
                if self._valores[i] is not DFInstance._VAZIO}

    def _tem_campo(self, name):
        if self._indice is None:
            return name in self._valores
        i = self._indice.get(name)
        return i is not None and self._valores[i] is not DFInstance._VAZIO

    def _ler_campo(self, name):
        if self._indice is None:
            return self._valores[name]
        return self._valores[self._indice[name]]

    def get(self, name):
        """O membro, procurado na ORDEM DA MRO.

        Antes a busca era em profundidade: 'D extends B, C' com as duas
        herdando de 'A' encontrava o metodo de 'C' quando devia
        encontrar o de 'B' — porque descia por 'B' ate 'A' antes de
        olhar 'C'. Seguir a MRO e o que faz a heranca multipla se
        comportar como quem escreveu espera.
        """
        if self._tem_campo(name):
            return self._ler_campo(name)
        for bp in self.blueprint.linhagem():
            if name in bp.methods:
                return bp.methods[name]
            if name in bp.statics:
                return bp.statics[name]
        raise NameError_(f"'{self.blueprint.name}' has no member '{name}'")

    def _resolve_from_blueprint(self, bp, name):
        """Resolve a name from blueprint chain (supports deep inheritance)."""
        if name in bp.methods:
            return bp.methods[name]
        if name in bp.statics:
            return bp.statics[name]
        for parent in bp.parents:
            try:
                return self._resolve_from_blueprint(parent, name)
            except NameError_:
                continue
        raise NameError_(f"Not found: '{name}'")

    def set(self, name, value):
        if self._indice is None:
            self._valores[name] = value
            return
        i = self._indice.get(name)
        if i is None:
            permitidos = ", ".join(sorted(self._indice))
            raise UndefinedMemberError(
                f"'{self.blueprint.name}' has no field '{name}'.",
                nota=f"it declares slots: {permitidos}",
                dica=("slots list every field the object may have; "
                      "add it there, or remove the 'slots' declaration"),
                doc="oop/slots")
        self._valores[i] = value

    def isinstance_of(self, blueprint):
        """Check if this instance is of given blueprint or inherits from it."""
        if self.blueprint is blueprint or self.blueprint.name == blueprint.name:
            return True
        return self._check_parents(self.blueprint, blueprint)

    def _check_parents(self, bp, target):
        for parent in bp.parents:
            if parent is target or parent.name == target.name:
                return True
            if self._check_parents(parent, target):
                return True
        return False

    def get_mro(self):
        """Get Method Resolution Order (C3 linearization simplified)."""
        mro = [self.blueprint]
        visited = {self.blueprint.name}
        queue = list(self.blueprint.parents)
        while queue:
            bp = queue.pop(0)
            if bp.name not in visited:
                visited.add(bp.name)
                mro.append(bp)
                queue.extend(bp.parents)
        return mro

    def has_method(self, name):
        """Check if instance has a given method."""
        try:
            val = self.get(name)
            return isinstance(val, (DFAction, BuiltinFunction)) or callable(val)
        except NameError_:
            return False

    def __repr__(self):
        return f"<{self.blueprint.name} instance>"

    # ── Os protocolos do Python, respondidos pelos metodos magicos ──
    #
    # 'int(obj)', 'round(obj)', 'sorted(objs)' e 'hash(obj)' sao
    # chamadas do PYTHON: os embutidos da linguagem sao funcoes do host,
    # e a stdlib inteira tambem. Responder aqui, uma vez, faz o
    # '__int__' do blueprint valer em todas elas — e nao so nos lugares
    # que alguem lembrou de adaptar. Era por isso que metade dos 95
    # metodos magicos da documentacao nao rodava: cada embutido precisava
    # saber deles, e nenhum sabia.
    #
    # O que NAO esta aqui, de proposito: '__len__', '__bool__' e
    # '__iter__'. O interpretador pergunta 'if obj:' sobre instancias em
    # dezenas de lugares, e um '__len__' no Python mudaria a verdade de
    # todo objeto que declara tamanho. Esses tres ja sao atendidos pela
    # propria linguagem ('len', 'given', 'cycle').

    def _magico_py(self, nome, *args):
        interp = DFAction._interpreter
        if interp is None:
            return _SEM_MAGICO
        acao = Interpreter._achar_magico(self, nome)
        if acao is None:
            return _SEM_MAGICO
        return interp._call_action(acao, list(args), {}, interp._no_interno(),
                                   None, instance=self)

    def _recusar_conversao(self, tipo, magico):
        raise TypeError(
            f"an instance of '{self.blueprint.name}' cannot become {tipo}: "
            f"declare 'action {magico}()' in the blueprint")

    def __int__(self):
        for nome in ("__int__", "__index__"):
            r = self._magico_py(nome)
            if r is not _SEM_MAGICO:
                return int(r)
        self._recusar_conversao("Integer", "__int__")

    def __index__(self):
        r = self._magico_py("__index__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("an index", "__index__")
        return int(r)

    def __float__(self):
        r = self._magico_py("__float__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("Float", "__float__")
        return float(r)

    def __complex__(self):
        r = self._magico_py("__complex__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("Complex", "__complex__")
        return complex(r)

    def __round__(self, casas=None):
        r = (self._magico_py("__round__") if casas is None
             else self._magico_py("__round__", casas))
        if r is _SEM_MAGICO:
            self._recusar_conversao("a rounded number", "__round__")
        return r

    def __floor__(self):
        r = self._magico_py("__floor__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("a floor", "__floor__")
        return r

    def __ceil__(self):
        r = self._magico_py("__ceil__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("a ceiling", "__ceil__")
        return r

    def __trunc__(self):
        r = self._magico_py("__trunc__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("a truncated number", "__trunc__")
        return r

    def __abs__(self):
        r = self._magico_py("__abs__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("an absolute value", "__abs__")
        return r

    def __reversed__(self):
        r = self._magico_py("__reversed__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("a reversed sequence", "__reversed__")
        return iter(r)

    def __format__(self, especificador):
        r = self._magico_py("__format__", especificador)
        if r is _SEM_MAGICO:
            if not especificador:
                return DFAction._interpreter._to_str(self) \
                    if DFAction._interpreter else repr(self)
            self._recusar_conversao(f"text formatted with '{especificador}'",
                                    "__format__")
        return str(r)

    def __bytes__(self):
        r = self._magico_py("__bytes__")
        if r is _SEM_MAGICO:
            self._recusar_conversao("Bytes", "__bytes__")
        return r if isinstance(r, bytes) else str(r).encode("utf-8")

    def __hash__(self):
        r = self._magico_py("__hash__")
        if r is _SEM_MAGICO:
            return object.__hash__(self)
        return hash(r)

    def __eq__(self, outro):
        if self is outro:
            return True
        r = self._magico_py("__eq__", outro)
        if r is not _SEM_MAGICO:
            return bool(r)
        c = self._magico_py("__cmp__", outro)
        if c is not _SEM_MAGICO and isinstance(c, (int, float)):
            return c == 0
        return False

    def __ne__(self, outro):
        r = self._magico_py("__ne__", outro)
        if r is not _SEM_MAGICO:
            return bool(r)
        return not self.__eq__(outro)

    def _comparar_py(self, nome, outro, de_cmp):
        r = self._magico_py(nome, outro)
        if r is not _SEM_MAGICO and r is not NotImplemented:
            return bool(r)
        c = self._magico_py("__cmp__", outro)
        if c is not _SEM_MAGICO and isinstance(c, (int, float)):
            return de_cmp(c)
        return NotImplemented

    def __lt__(self, outro):
        return self._comparar_py("__lt__", outro, lambda c: c < 0)

    def __le__(self, outro):
        return self._comparar_py("__le__", outro, lambda c: c <= 0)

    def __gt__(self, outro):
        return self._comparar_py("__gt__", outro, lambda c: c > 0)

    def __ge__(self, outro):
        return self._comparar_py("__ge__", outro, lambda c: c >= 0)

    def __copy__(self):
        for nome in ("__copy__", "__clone__"):
            r = self._magico_py(nome)
            if r is not _SEM_MAGICO:
                return r
        return copiar_instancia(self, fundo=False)

    def __deepcopy__(self, memo):
        for nome in ("__deepcopy__", "__clone__"):
            r = self._magico_py(nome)
            if r is not _SEM_MAGICO:
                return r
        return copiar_instancia(self, fundo=True, memo=memo)


def copiar_instancia(original, fundo=False, memo=None):
    """Uma instancia nova do mesmo blueprint, com os mesmos campos.

    Nao roda 'setup': a copia nao NASCE, ela e duplicada — e o que o
    Python faz, e o unico jeito de copiar um objeto cujo construtor pede
    argumentos que a copia nao tem. Congelamento e trava NAO sao
    copiados: a copia existe justamente para ser mexida.
    """
    import copy as _copy
    classe = type(original)
    copia = classe.__new__(classe)
    DFInstance.__init__(copia, original.blueprint)
    if memo is not None:
        memo[id(original)] = copia
    for nome, valor in original.fields.items():
        if fundo:
            valor = _copy.deepcopy(valor, memo if memo is not None else {})
        copia.set(nome, valor)
    return copia


class DFInstanceFinal(DFInstance):
    """A instancia de um blueprint que declara 'teardown' ou '__del__'.

    Uma subclasse, e nao um '__del__' em toda instancia: o coletor do
    Python trata objeto com finalizador de outro jeito, e um programa
    com um milhao de objetos sem finalizador nao pode pagar por isso.
    """

    __slots__ = ()

    def __del__(self):
        import sys as _sys
        if _sys.is_finalizing():
            # No fim do processo o interpretador ja pode estar desmontado;
            # rodar codigo do usuario ali daria erro sobre nada.
            return
        interp = DFAction._interpreter
        acao = getattr(self.blueprint, "finalizador", None)
        if interp is None or acao is None:
            return
        try:
            interp._call_action(acao, [], {}, interp._no_interno(), None,
                                instance=self)
        except BaseException as erro:          # um finalizador nunca propaga
            try:
                mensagem = getattr(erro, "message", None) or str(erro)
                _sys.stderr.write(
                    f"aviso: o finalizador de '{self.blueprint.name}' falhou: "
                    f"{mensagem}\n")
            except Exception:
                pass


#: As classes de instancia que podem ter vigias — o teste do caminho quente.
_COM_VIGIAS = frozenset((DFInstance, DFInstanceFinal))

def _posicionar(erro, node):
    """Da ao erro a posicao do no, e redesenha a mensagem com ela."""
    erro.line = getattr(node, "line", 0) or 0
    erro.column = getattr(node, "column", 0) or 0
    erro.args = (erro.format(),)


#: As expressoes que CRIAM a colecao: so ela nasce tipada numa declaracao.
#: Uma colecao que ja existia e conferida, e continua sendo o mesmo objeto.
_NASCE_AQUI = (ast.ListLiteral, ast.DictLiteral, ast.ListComprehension,
               ast.VaultComprehension)

#: Os embutidos que sempre devolvem uma colecao NOVA: 'cluster(xs)' copia.
_CRIAM_COLECAO = frozenset({"cluster", "vault"})

#: E as funcoes de modulo que tambem sempre criam: (modulo, funcao).
_MODULOS_QUE_CRIAM = frozenset({("Arcane.Collections", "set")})


def _nasce_aqui(no, env):
    """A expressao cria a colecao, em vez de apontar para uma que ja existia?

    A pergunta e SINTATICA de proposito: um literal, uma compreensao, ou
    uma funcao conhecida por sempre devolver uma colecao nova. Uma chamada
    qualquer pode devolver uma lista guardada em outro lugar, e tipa-la
    seria copiar — e a copia mudaria em silencio quem ja a segurava.
    """
    if isinstance(no, _NASCE_AQUI):
        return True
    try:
        if (isinstance(no, ast.FunctionCall) and isinstance(no.callee, ast.Identifier)
                and no.callee.name in _CRIAM_COLECAO):
            return isinstance(env.get(no.callee.name), BuiltinFunction)
        if (isinstance(no, ast.MethodCall) and isinstance(no.object, ast.Identifier)):
            modulo = env.get(no.object.name)
            return (isinstance(modulo, dict)
                    and (modulo.get("__name__"), no.method) in _MODULOS_QUE_CRIAM)
    except NameError_:
        return False
    return False


#: Os nomes que 'obj.' responde sem olhar os campos.
_EMBUTIDOS_DA_INSTANCIA = frozenset(("blueprint_name", "fields", "methods"))


#: O nome que o Python usa -> o nome que a linguagem usa.
#:
#: Fica aqui, e nao espalhado pelas mensagens, porque a traducao tem de
#: valer para o que o Python levanta de QUALQUER lugar — uma comparacao,
#: um 'len', uma conversao. Cada uma dessas mensagens e escrita pelo
#: CPython, e nenhuma conhece as palavras desta linguagem.
_TIPOS_DO_PYTHON = (
    ("'NoneType'", "Void"),
    ("'bool'", "Boolean"),
    ("'int'", "Integer"),
    ("'float'", "Float"),
    ("'complex'", "Complex"),
    ("'str'", "String"),
    ("'bytes'", "Bytes"),
    ("'list'", "Cluster"),
    ("'tuple'", "Cluster"),
    ("'dict'", "Vault"),
    ("'set'", "Set"),
    ("'frozenset'", "Set"),
    # A forma sem aspas aparece em "object of type 'int' has no len()"
    # e em "descriptor 'x' for 'str' objects".
    ("NoneType", "Void"),
    # Aspas DUPLAS: 'can only concatenate str (not "int") to str'.
    ('"bool"', "Boolean"), ('"int"', "Integer"), ('"float"', "Float"),
    ('"str"', "String"), ('"bytes"', "Bytes"), ('"list"', "Cluster"),
    ('"tuple"', "Cluster"), ('"dict"', "Vault"), ('"set"', "Set"),
    ('"NoneType"', "Void"),
)

#: O mesmo mapa, para o nome escrito SEM aspas.
_NOMES_NUS = {
    "NoneType": "Void", "bool": "Boolean", "int": "Integer",
    "float": "Float", "complex": "Complex", "str": "String",
    "bytes": "Bytes", "bytearray": "Bytes", "list": "Cluster",
    "tuple": "Cluster", "dict": "Vault", "set": "Set",
    "frozenset": "Set", "os.PathLike": "path",
}

#: As MOLDURAS exatas em que o CPython escreve o nome de tipo sem aspas.
#:
#: Reconhecer a moldura inteira — e nao a palavra solta — e o que permite
#: estender a traducao sem estragar texto legitimo. Era o medo escrito na
#: docstring antiga, e ele e justificado: uma mensagem sobre um arquivo
#: chamado 'list.txt' contem a palavra, e trocar a palavra solta a
#: transformaria em 'Cluster.txt'. Nenhuma das molduras abaixo casa com
#: "file not found: list.txt", e ", not dict" casa com todas as que
#: importam.
#:
#: Sem elas, a metade das mensagens do CPython que NAO usa aspas passava
#: inteira: 'expected str, bytes or os.PathLike object, not dict' era o
#: que a linguagem respondia a quem abria um banco com o argumento
#: errado, e nenhuma daquelas cinco palavras existe aqui.
_MOLDURAS_NUAS = (
    # ", not dict"  —  a virgula e o que separa isto de "not found: list"
    r",\s*not\s+(?P<tipos>[\w.]+)",
    # "must be str, bytes or bytearray"
    r"\bmust be\s+(?P<tipos>[\w.]+(?:,\s*[\w.]+)*(?:\s+or\s+[\w.]+)?)",
    # "expected str, bytes or os.PathLike"
    r"\bexpected\s+(?P<tipos>[\w.]+(?:,\s*[\w.]+)*(?:\s+or\s+[\w.]+)?)",
    # "by non-int of type 'String'" — o CPython cola o nome do tipo num
    # prefixo, e o hifen e fronteira de palavra, entao a moldura de
    # ", not X" nao chega ali. Exigir o prefixo 'non-' e o que separa
    # isto de "non-empty" e "non-standard", que nao sao tipo nenhum.
    r"\bnon-(?P<tipos>int|str|float|bool|bytes|list|dict|tuple|set|complex)\b",
    # 'can only concatenate str (not "int") to str' — a moldura leva o
    # rabo ate o fim, senao o ultimo 'str' ficava para tras. 'to' sozinho
    # nao serve de pista: "add it to list" viraria "add it to Cluster".
    r"\bcan only concatenate\s+(?P<tipos>[\w.]+"
    r"(?:\s*\(not\s*\"?[\w.]+\"?\))?\s*to\s+[\w.]+)",
)

_MOLDURAS_NUAS = tuple(_re.compile(p) for p in _MOLDURAS_NUAS)

#: A palavra de tipo dentro de uma moldura. Os nomes mais longos
#: primeiro, senao 'os.PathLike' seria comido pelo alternativo curto.
_PALAVRA_NUA = _re.compile(
    r"\b(" + "|".join(sorted((_re.escape(n) for n in _NOMES_NUS),
                             key=len, reverse=True)) + r")\b")


def _traduzir_um_nome(encontrado):
    return _NOMES_NUS.get(encontrado.group(1), encontrado.group(1))


def _traduzir_moldura(encontrado):
    """Troca os nomes DENTRO de uma moldura, e so ali."""
    inteiro = encontrado.group(0)
    tipos = encontrado.group("tipos")

    # Uma LISTA so de nomes de tipo e reescrita por inteiro, porque a
    # traducao pode juntar dois nomes num: 'bytes or bytearray' vira
    # 'Bytes or Bytes', e repetir o mesmo nome na mesma frase parece
    # defeito — a informacao que a repeticao carregava (sao dois tipos
    # do Python) nao existe nesta linguagem.
    nomes = _re.split(r",\s*|\s+or\s+", tipos)
    if len(nomes) > 1 and all(n in _NOMES_NUS for n in nomes):
        unicos = list(dict.fromkeys(_NOMES_NUS[n] for n in nomes))
        traduzido = (unicos[0] if len(unicos) == 1 else
                     ", ".join(unicos[:-1]) + " or " + unicos[-1])
    else:
        traduzido = _PALAVRA_NUA.sub(_traduzir_um_nome, tipos)
    return inteiro.replace(tipos, traduzido, 1)


#: Os recados do CPython que chegam ao usuario inteiros.
#:
#: '_traduzir_tipos' troca os NOMES de tipo, e isso resolve a maioria.
#: Sobram as mensagens cuja FRASE e do Python: elas falam de funcoes que
#: nao existem aqui ('int()', 'math domain'), e nenhuma diz o que fazer.
#:
#: 'int(texto)' e o caso que mais importa: e o erro mais comum de todo
#: programa que le entrada — formulario, CSV, argumento de linha de
#: comando. Responder "invalid literal for int() with base 10" a quem
#: digitou 'abc' num campo de idade nao ajuda ninguem.
#:
#: Cada entrada e (padrao, mensagem, dica). Os grupos nomeados do padrao
#: entram nas duas por '{nome}'.
_RECADOS_CRUS = (
    (r"invalid literal for int\(\) with base \d+: (?P<valor>.+)",
     "não dá para ler {valor} como número inteiro",
     "confira a entrada antes de converter:\n"
     "    given texto.is_digit():\n"
     "        n := int(texto)"),
    (r"could not convert string to float: (?P<valor>.+)",
     "não dá para ler {valor} como número decimal",
     "troque a vírgula por ponto, ou confira a entrada antes:\n"
     '    n := float(texto.replace(",", "."))'),
    # O CPython <= 3.13 dizia so 'math domain error'; o 3.14 trocou por
    # tres frases especificas. As quatro entradas convivem porque o
    # mesmo interpretador roda nas duas versoes, e a traducao que casa
    # so uma delas deixa a outra chegar crua ao usuario — foi o que
    # aconteceu: 'expected a nonnegative input, got -1.0' passou meses
    # saindo sem dica nenhuma.
    (r"^math domain error$",
     "esta conta não tem resposta real",
     "raiz de número negativo e logaritmo de zero ou negativo não têm\n"
     "resposta nos números desta linguagem — confira o valor antes"),
    (r"expected a nonnegative input(, got (?P<valor>\S+))?",
     "raiz de número negativo não tem resposta real",
     "confira o valor antes de tirar a raiz:\n"
     "    given x bigger_eq 0:\n"
     "        r := sqrt(x)"),
    (r"expected a positive input(, got (?P<valor>\S+))?",
     "esta conta pede um número maior que zero",
     "o logaritmo de zero e de negativo não tem resposta nos números\n"
     "desta linguagem — confira o valor antes"),
    (r"expected a number in range from -1 up to 1(, got (?P<valor>\S+))?",
     "esta conta só aceita valor entre -1 e 1",
     "'acos' e 'asin' recebem um cosseno ou um seno, e os dois vivem\n"
     "entre -1 e 1 — confira o valor antes"),
    (r"object cannot be interpreted as an integer",
     "aqui é preciso um número inteiro",
     "converta antes com  int(x)"),
    (r"object is not iterable",
     "este valor não pode ser percorrido item a item",
     "só cluster, vault, texto e stream podem — confira com  typeof(x)"),
    (r"^string index out of range$",
     "esta posição não existe neste texto",
     "confira o tamanho com  len(texto)  antes de indexar"),
    (r"^list index out of range$",
     "esta posição não existe neste cluster",
     "confira o tamanho com  len(xs)  antes de indexar"),
)

_RECADOS_CRUS = tuple(
    (_re.compile(padrao), mensagem, dica)
    for padrao, mensagem, dica in _RECADOS_CRUS)


def _refazer_recado(texto):
    """A mensagem do Python vira a desta linguagem, com dica.

    Devolve `(mensagem, dica)` ou `None` quando o texto nao e um dos
    recados conhecidos — e ai o caminho de sempre continua valendo. A
    tabela e curta de proposito: cobrir todo o CPython seria mentira, e
    o que nao esta aqui sai como estava, legivel em ingles.
    """
    if not texto:
        return None
    for padrao, mensagem, dica in _RECADOS_CRUS:
        achado = padrao.search(texto)
        if achado:
            campos = achado.groupdict()
            return mensagem.format(**campos), dica.format(**campos)
    return None


def _traduzir_tipos(texto):
    """Troca os nomes de tipo do Python pelos da linguagem.

    Duas passadas, e as duas conservadoras. A primeira troca o nome ENTRE
    ASPAS, que e como o CPython o escreve em boa parte das mensagens. A
    segunda cuida das que o escrevem NU, e para nao estragar texto
    legitimo ela exige a MOLDURA inteira: ", not dict" e "must be str"
    sao trocados, "file not found: list.txt" nao.
    """
    if not texto:
        return texto
    for py, df in _TIPOS_DO_PYTHON:
        if py in texto:
            aspas = py[0] if py[0] in "'\"" else ""
            texto = texto.replace(py, f"{aspas}{df}{aspas}" if aspas else df)
    for moldura in _MOLDURAS_NUAS:
        texto = moldura.sub(_traduzir_moldura, texto)
    return texto


class DFError:
    """A runtime error captured by 'monitor / handle'.

    Behaves like the error message string (so older code that concatenates or
    compares it keeps working) while also exposing '.type', '.message' and
    '.line'.
    """

    #: Campos do erro original que o programa pode ler pelo nome.
    #:
    #: Um erro carrega mais que a mensagem. 'ValidationError' traz a
    #: lista de campos que falharam; 'HttpError' traz o codigo e o
    #: corpo. Sem expor isso, o programa recebe um texto e tem de
    #: reconstruir por extracao o que o erro ja sabia — e a doc que
    #: promete 'e.campos' vira mentira.
    EXTRAS = ("nota", "dica", "codigo", "doc", "campos", "caminho",
              "motivo", "corpo", "cabecalhos", "esperado", "obtido",
              "diferenca", "restricao", "tabela", "coluna")

    #: A pilha de chamadas, como DADO.
    #:
    #: Ela ja era guardada no erro ('_attach_stack') e desenhada no
    #: stack trace, mas era inalcancavel de dentro do programa: um
    #: 'handle' via a mensagem e nada sobre o caminho. Numa acao chamada
    #: de cinco lugares, "deu erro em media()" nao ajuda — o que importa
    #: e QUAL das cinco chamadas, e essa informacao existia e ficava
    #: guardada.
    #:
    #: Fica separada de EXTRAS porque precisa de CONVERSAO: os quadros
    #: sao objetos 'Frame', e entregar objeto de Python ao programa
    #: funcionaria por protocolo mas nao seria dado que se possa
    #: serializar, comparar ou mandar para um log.
    PILHA = ("pilha", "stack")

    def __init__(self, kind: str, message: str, original=None):
        self.type = kind
        self.message = message
        self.original = original
        self.line = getattr(original, 'line', 0)
        self.column = getattr(original, 'column', 0)

    #: O que o 'trigger' levantou, como DADO.
    #:
    #: Nos dois idiomas, como a pilha: '.type' e '.message' sao em
    #: ingles e os extras em portugues, e obrigar a escolher aqui so
    #: faria a metade errada dar AttributeError.
    VALOR = ("valor", "value")

    #: Os OUTROS erros que viajam com este.
    #:
    #: Um 'parallel' em que duas instrucoes falham, um 'defer' que quebra
    #: numa acao que ja estava falhando: ha mais de um erro, e so o
    #: primeiro chega ao 'handle'. Sem isto, os demais eram desenhados no
    #: terminal e INALCANCAVEIS de dentro do programa — que e justamente
    #: quem precisa decidir o que fazer com eles.
    OUTROS = ("outros", "others")

    #: O erro que estava sendo tratado quando este nasceu.
    #:
    #: 'void' quando nao ha — e nao um erro vazio: quem pergunta
    #: 'e.causa' quer saber SE houve, e um objeto falso ali faria todo
    #: teste de presenca dar verdadeiro.
    CAUSA = ("causa", "cause")

    def __getattr__(self, nome):
        """Os campos extras do erro original, lidos pelo nome.

        Fica em '__getattr__' e nao no construtor porque so e chamado
        quando o atributo NAO existe — nao custa nada nos acessos
        comuns, que sao '.type' e '.message'.
        """
        if nome in DFError.PILHA:
            return self._pilha_como_dado()
        if nome in DFError.OUTROS:
            # Cada um como o mesmo valor que o 'handle' recebe, com '.type'
            # e '.message': um Cluster de erros que o programa le igual ao
            # primeiro.
            return [DFError(type(o).__name__.rstrip('_'),
                            getattr(o, "message", str(o)), o)
                    for o in (getattr(self.original, "outros", None) or [])]
        if nome in DFError.CAUSA:
            causa = getattr(self.original, "causa", None)
            if causa is None:
                return None
            return DFError(type(causa).__name__.rstrip("_"),
                           getattr(causa, "message", str(causa)), causa)
        if nome in DFError.VALOR:
            # 'void' quando o erro nao veio de um 'trigger': um '1 / 0'
            # nao foi levantado por ninguem com um valor, e devolver a
            # mensagem ali faria '.valor' significar duas coisas
            # conforme a origem.
            return getattr(self.original, "valor", None)
        if nome.startswith("_") or nome not in DFError.EXTRAS:
            raise AttributeError(nome)
        valor = getattr(self.original, nome, None)
        if valor is None and nome == "codigo":
            valor = getattr(type(self.original), "CODIGO", "")
        return valor

    def _pilha_como_dado(self):
        """Do mais externo para o mais interno.

        E a ordem em que se le "quem chamou quem", e a mesma em que o
        stack trace desenha — inverter aqui faria o programa e a tela
        discordarem sobre a mesma pilha.
        """
        quadros = getattr(self.original, "stack", None) or []
        return [{"name": getattr(q, "name", "?"),
                 "line": getattr(q, "line", 0),
                 "column": getattr(q, "column", 0),
                 "file": getattr(q, "filename", "")}
                for q in quadros]

    def __str__(self):
        return self.message

    def __eq__(self, other):
        if isinstance(other, str):
            return self.message == other
        if isinstance(other, DFError):
            return self.type == other.type and self.message == other.message
        return NotImplemented

    def __hash__(self):
        return hash((self.type, self.message))

    def __bool__(self):
        return True

    def __repr__(self):
        return f"<{self.type}: {self.message}>"


class DFRecord:
    """Um tipo record: dados imutáveis, com igualdade estrutural."""

    def __init__(self, name, fields, methods, env, type_params=(), type_bounds=None):
        self.name = name
        self.fields = fields        # [(nome, tipo, default_node|None)]
        self.field_names = [f[0] for f in fields]
        self.field_types = {f[0]: f[1] for f in fields}
        self.methods = methods      # nome -> DFAction
        self.env = env
        #: 'record Caixa<T>' — o parametro documenta a relacao entre os
        #: campos, e o LIMITE ('<T extends Number>') e cobrado de verdade.
        self.type_params = tuple(type_params or ())
        self.type_bounds = dict(type_bounds or {})

    def __repr__(self):
        return f"<record '{self.name}'>"


class DFRecordInstance:
    """Uma instância de record. Imutável: use 'with' para gerar uma cópia."""

    __slots__ = ('record', 'values')

    def __init__(self, record: DFRecord, values: dict):
        self.record = record
        self.values = values

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if name in self.record.methods:
            return self.record.methods[name]
        # A dica lista campos E metodos. Listar so os campos manda quem
        # errou 'normaa' procurar entre 'x, y' — omitindo justamente o
        # 'norma' que ele queria, que e um nome valido aqui.
        tem = list(self.record.field_names) + [
            m for m in self.record.methods if m not in self.record.field_names]
        raise NameError_(
            f"Record '{self.record.name}' has no field or method '{name}'. "
            f"It has: {', '.join(tem)}")

    def replace(self, changes: dict):
        """Cópia com campos trocados — a base do operador 'with'."""
        desconhecidos = [k for k in changes if k not in self.record.field_names]
        if desconhecidos:
            raise NameError_(
                f"Record '{self.record.name}' has no field(s): "
                f"{', '.join(desconhecidos)}")
        novos = dict(self.values)
        novos.update(changes)
        return DFRecordInstance(self.record, novos)

    def __eq__(self, other):
        if isinstance(other, DFRecordInstance):
            return (self.record.name == other.record.name
                    and self.values == other.values)
        return NotImplemented

    def __hash__(self):
        return hash((self.record.name, tuple(sorted(
            (k, v) for k, v in self.values.items() if isinstance(v, (int, float, str, bool, type(None)))))))

    def __repr__(self):
        campos = ', '.join(f"{k}: {v!r}" for k, v in self.values.items())
        return f"{self.record.name}({campos})"


class DFEnumMember:
    """Um membro de enum. Compara por identidade dentro do enum."""

    #: 'enum' e preenchido pela declaracao, logo depois de o DFEnum
    #: existir — ele nao pode ser argumento porque os membros nascem
    #: ANTES do enum que os contem.
    #:
    #: Sem ele, um metodo declarado no enum ficava inalcancavel: o
    #: parser aceitava 'action hex()', o interpretador o guardava em
    #: 'DFEnum.methods', e 'Cor.Verde.hex()' respondia "has no member
    #: 'hex'. Use .name, .value or .index". Codigo que se escreve, que
    #: compila, e que nunca roda.
    __slots__ = ('enum_name', 'name', 'value', 'index', 'enum')

    def __init__(self, enum_name, name, value, index, enum=None):
        self.enum_name = enum_name
        self.name = name
        self.value = value
        self.index = index
        self.enum = enum

    def __eq__(self, other):
        if isinstance(other, DFEnumMember):
            return self.enum_name == other.enum_name and self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash((self.enum_name, self.name))

    def __repr__(self):
        return f"{self.enum_name}.{self.name}"


class DFEnum:
    """Um tipo enum e seus membros."""

    def __init__(self, name, members, methods, env):
        self.name = name
        self.members = members      # nome -> DFEnumMember (ordenado)
        self.methods = methods
        self.env = env

    def get(self, name):
        if name in self.members:
            return self.members[name]
        if name in self.methods:
            return self.methods[name]
        raise NameError_(
            f"Enum '{self.name}' has no member '{name}'. "
            f"Members: {', '.join(self.members)}")

    def __repr__(self):
        return f"<enum '{self.name}'>"


class DFStream:
    """Uma sequência preguiçosa produzida por um 'stream action'."""

    def __init__(self, name, produce):
        self.name = name
        self._produce = produce     # callable -> generator Python
        self._iter = None

    def __iter__(self):
        return self._produce()

    def take(self, n):
        """Os 'n' primeiros itens, e nem um a mais PRODUZIDO.

        A versao anterior parava depois de PUXAR o item n+1: com a
        fonte materializada isso nao aparecia, mas com 'map' e 'filter'
        preguicosos a fonte roda uma volta a mais — e uma volta de
        'stream action' pode ser uma consulta ou uma escrita.
        """
        if n <= 0:
            return []
        saida = []
        for item in self:
            saida.append(item)
            if len(saida) >= n:
                break
        return saida

    def map(self, f):
        """Transforma cada item, SEM percorrer a sequencia.

        Devolve um stream, e nao um cluster: 'fib().map(...)' sobre um
        stream infinito tem de voltar, e o resultado precisa poder ser
        encadeado com outro 'map', com 'filter' e com 'take'.
        """
        return DFStream(self.name, lambda: (f(x) for x in self))

    def filter(self, f, verdade=bool):
        """Escolhe itens, SEM percorrer a sequencia.

        A verdade e a da linguagem — uma instancia com '__bool__'
        responde por si —, por isso ela chega de fora em vez de ser o
        'bool' do Python.
        """
        return DFStream(self.name, lambda: (x for x in self if verdade(f(x))))

    def skip(self, n):
        """Descarta os 'n' primeiros, e segue preguicoso."""
        def produzir():
            it = iter(self)
            for _ in range(max(0, n)):
                if next(it, _FIM) is _FIM:
                    return
            yield from it
        return DFStream(self.name, produzir)

    def enumerate(self, inicio=0):
        """Cada item com a sua posicao, como '[i, item]'.

        Um cluster de dois, e nao uma tupla: a linguagem nao tem
        tupla, e a desestruturacao 'i, v := par' ja funciona assim.
        """
        return DFStream(
            self.name,
            lambda: ([i, x] for i, x in enumerate(self, inicio)))

    def reduce(self, f, inicial=None):
        """Dobra a sequencia num valor so. Consome — nao e preguicoso."""
        it = iter(self)
        if inicial is None:
            acc = next(it, None)
        else:
            acc = inicial
        for item in it:
            acc = f(acc, item)
        return acc

    def to_cluster(self):
        return list(self)

    def next(self):
        if self._iter is None:
            self._iter = iter(self)
        try:
            return next(self._iter)
        except StopIteration:
            return None

    def reset(self):
        self._iter = None
        return self

    def __repr__(self):
        return f"<stream '{self.name}'>"


class BoundRecordMethod:
    """Um método de record já ligado à sua instância."""

    __slots__ = ('interpreter', 'instance', 'action')

    def __init__(self, interpreter, instance, action):
        self.interpreter = interpreter
        self.instance = instance
        self.action = action

    def __call__(self, *args, **kwargs):
        no = type('_N', (), {'line': 0, 'column': 0})()
        return self.interpreter._call_action(
            self.action, list(args), kwargs, no, None, instance=self.instance)

    def __repr__(self):
        return f"<method '{self.action.name}' of {self.instance.record.name}>"


class DFChannel:
    """Canal entre linhas de execucao. FIFO, e seguro entre threads.

    'receive()' NAO bloqueia, e isso e contrato: dois exercicios do
    repositorio afirmam 'fila.receive() is void' para o canal vazio, e ha
    laco escrito contando com isso. Trocar o padrao por espera nao daria
    erro — daria TRAVAMENTO, que e a pior falha possivel, porque nao ha
    mensagem nem pilha para investigar.

    A espera entra por argumento, entao quem a quer pede:

        fila.receive()            devolve void na hora, se estiver vazio
        fila.receive(2000)        espera ate 2 segundos; depois, void
        fila.receive(void)        espera o que for preciso

    A fila e uma 'deque' e a espera e uma 'Condition': um 'sleep' em laco
    gastaria CPU e acordaria tarde, e a diferenca aparece justamente com
    muitos consumidores, que e quando um canal serve para algo.
    """

    def __init__(self, name):
        self.name = name
        self._queue = _collections.deque()
        self._cheio = threading.Condition()

    def send(self, value):
        with self._cheio:
            self._queue.append(value)
            # 'notify' e nao 'notify_all': um item atende um consumidor,
            # e acordar dez para nove voltarem a dormir e desperdicio que
            # cresce com o numero deles.
            self._cheio.notify()

    def receive(self, espera=0):
        """Tira o proximo item. Ver a docstring da classe para a espera."""
        with self._cheio:
            if self._queue:
                return self._queue.popleft()
            if espera == 0:
                return None
            # 'void' (None) quer dizer "o que for preciso". Um numero e o
            # teto em MILISSEGUNDOS, a mesma unidade de 'sleep'.
            limite = None if espera is None else max(0.0, espera / 1000.0)
            if self._cheio.wait_for(lambda: bool(self._queue), timeout=limite):
                return self._queue.popleft()
            return None

    def pending(self):
        """Quantos itens estao na fila agora.

        E uma FOTO: com outra thread enviando, o numero pode mudar entre
        esta chamada e a proxima linha. Serve para medir e para registrar,
        nao para decidir se o proximo 'receive' vai achar algo.
        """
        with self._cheio:
            return len(self._queue)

    def __len__(self):
        return self.pending()

    def __repr__(self):
        return f"<channel '{self.name}'>"


#: Quanto de pilha uma linha de execucao do DataForge precisa, em ordem
#: de preferencia.
#:
#: Uma chamada da linguagem custa ~10 quadros do Python — medido, nao
#: estimado: 200 chamadas aninhadas produzem 2024 quadros. Como
#: 'MAX_CALL_DEPTH' permite mil, uma recursao legitima no limite pede
#: ~10 mil quadros, e a pilha precisa caber neles ANTES que o guarda da
#: linguagem dispare. Se nao couber, o processo morre sem mensagem.
#:
#: O custo por quadro nao e o mesmo em todo lugar, e a diferenca e
#: grande:
#:
#:   macOS 3.10   ~1,2 KB/quadro   (8 MB morre, 12 MB basta)
#:   Windows 3.10  >6,5 KB/quadro  (32 MB morria em 500 chamadas)
#:
#: Por isso uma escada, e nao um numero: pede-se o maior, e cai-se para
#: o seguinte se a plataforma recusar. E reserva de espaco de
#: enderecamento, nao de memoria — as paginas so passam a existir
#: conforme a pilha cresce, entao pedir 256 MB nao custa 256 MB.
_PILHAS = (256 * 1024 * 1024, 128 * 1024 * 1024,
           64 * 1024 * 1024, 32 * 1024 * 1024)

#: O que de fato se conseguiu. Zero = a plataforma decide.
_PILHA = 0

#: Esta thread ja foi criada com a pilha grande?
_PROVISIONADA = threading.local()


def _reservar_pilha():
    """Faz toda thread criada daqui em diante nascer com pilha grande.

    Vale para as tarefas 'async', para os blocos 'thread' e para o
    executor de 'run' — e e especialmente importante no macOS, onde uma
    thread comum nasce com 512 KB contra os 8 MB da principal: uma
    recursao que funciona no corpo do programa derrubaria o processo
    inteiro so por estar dentro de uma acao 'async'.

    Desce a escada ate a plataforma aceitar. Nao conseguindo nenhuma,
    baixa o limite de recursao do Python para que ELE dispare primeiro:
    um 'RecursionError' vira erro da linguagem em '_corpo_da_acao', e um
    erro e sempre melhor que um processo morto sem mensagem.
    """
    global _PILHA
    if _PILHA:
        return

    for tamanho in _PILHAS:
        try:
            threading.stack_size(tamanho)
        except (ValueError, RuntimeError, OverflowError):
            continue
        _PILHA = tamanho
        return

    _PILHA = -1      # tentado e recusado; nao insistir a cada thread
    sys.setrecursionlimit(min(sys.getrecursionlimit(), 3000))


def _com_pilha_propria(funcao):
    """Roda 'funcao' numa thread com pilha suficiente, e devolve o que ela deu.

    No Python 3.12 a CPython passou a vigiar a pilha de C por conta
    propria e levanta 'RecursionError' antes de estoura-la. Nas versoes
    anteriores nao ha essa rede: o limite de recursao e a unica protecao,
    e o interpretador o eleva a 20000 justamente porque uma chamada da
    linguagem custa varios quadros do Python. O resultado era um
    'Segmentation fault' — o processo morria sem mensagem nenhuma, onde
    deveria sair um erro da linguagem dizendo 'recursao infinita?'.
    """
    if getattr(_PROVISIONADA, "sim", False):
        return funcao()

    _reservar_pilha()
    caixa = {}

    def dentro():
        _PROVISIONADA.sim = True
        try:
            caixa["valor"] = funcao()
        except BaseException as erro:          # noqa: BLE001
            caixa["erro"] = erro

    t = threading.Thread(target=dentro, name="df-programa", daemon=True)
    t.start()
    t.join()
    if "erro" in caixa:
        raise caixa["erro"]
    return caixa.get("valor")


class _PorThread(threading.local):
    """O que cada thread do interpretador tem só para si.

    A profundidade de chamada e a pilha de quadros descrevem *uma* linha
    de execução. Compartilhadas entre threads, duas ações 'async'
    rodando juntas somavam a profundidade uma da outra — vinte chamadas
    paralelas de dez quadros pareciam duzentas para o guarda de
    recursão — e o stack trace de um erro saía com quadros da outra.
    """

    def __init__(self):
        self.depth = 0
        self.pilha = []
        # A acao cujo quadro esta em execucao NESTA thread. So o
        # trampolim da chamada de cauda precisa dela, e so ele a escreve.
        self.acao = None
        # Um gancho de metaclasse rodando: os ganchos nao disparam uns aos
        # outros, senao um 'on_read' que le um campo leria para sempre.
        self.em_gancho = False
        # '__getattribute__'/'__setattr__' rodando, por objeto: dentro
        # deles, 'self.x' e o acesso cru, como 'object.__getattribute__'.
        self.magicos_ativos = set()


class _Ganchos:
    """Os ganchos do ciclo de vida de uma tarefa `async`.

    O que o Node chama de *async hooks*, e o problema que eles resolvem:
    uma tarefa nasce numa thread, termina em outra, e no meio disso não
    há onde pendurar um cronômetro, um id de requisição ou um contador.
    Sem isso, medir "quanto tempo as tarefas deste pedido levaram" exige
    instrumentar cada ação à mão.

    Três decisões:

    1. **Um gancho que levanta não derruba a tarefa.** Ele é observação,
       e observação que quebra o observado é pior que não observar. O
       erro dele é engolido de propósito — é o único lugar do
       interpretador onde isso é certo.
    2. **Eles rodam na thread da tarefa**, e não numa fila. Um gancho
       que precisa saber em que thread está — e é justamente esse o caso
       de quem propaga contexto — não teria como descobrir depois.
    3. **A lista é global ao processo**, como a de `defer`: ganchos
       existem para diagnóstico e rastro, e um registro por escopo faria
       o gancho sumir quando a ação que o registrou terminasse.
    """

    __slots__ = ("criada", "terminou", "falhou")

    def __init__(self):
        self.criada = []
        self.terminou = []
        self.falhou = []

    def registrar(self, quando, funcao):
        getattr(self, quando).append(funcao)

    def limpar(self):
        self.criada.clear()
        self.terminou.clear()
        self.falhou.clear()

    def disparar(self, quando, tarefa):
        for funcao in tuple(getattr(self, quando)):
            try:
                funcao(tarefa)
            except BaseException:                         # noqa: BLE001
                pass


#: Os ganchos deste processo. 'Arcane.Async' os expoe a quem escreve.
_GANCHOS = _Ganchos()


class DFTarefa:
    """Uma ação 'async' em andamento.

    Existe porque 'async' passou tempo demais sendo enfeite: a palavra
    era aceita, guardada em 'is_async' e nunca lida, e 'await' devolvia
    o valor que já estava pronto. Escrever 'async' não deixava nada mais
    rápido — e a linguagem dizia que sim.

    Agora a chamada começa a rodar na hora, numa thread própria, e
    'await' espera terminar. É concorrência de verdade para trabalho de
    entrada e saída — rede, disco, banco, 'sleep' — onde o Python larga
    o GIL. Para trabalho de CPU o GIL continua no caminho, e a resposta
    é 'Arcane.Concurrent', que usa processos.

    Uma thread por chamada, sem piscina: dentro de uma ação 'async' é
    comum aguardar outra, e uma piscina de tamanho fixo travaria com as
    trabalhadoras todas bloqueadas esperando uma vaga que só elas
    poderiam liberar.
    """

    # '__weakref__' esta aqui porque a lista de tarefas vivas e FRACA:
    # sem ele, um objeto com '__slots__' nao aceita referencia fraca, e
    # a alternativa — guardar forte — faria toda tarefa ja colhida viver
    # ate o fim do programa.
    __slots__ = ("nome", "_thread", "_valor", "_erro", "_pronto", "_colhida",
                 "_dono", "_no", "__weakref__")

    #: Toda tarefa viva deste processo, para o relatorio do fim e para
    #: 'Async.vivas()'. Lista fraca: uma tarefa colhida e esquecida nao
    #: pode segurar memoria ate o programa acabar.
    _VIVAS = __import__("weakref").WeakSet()

    def __init__(self, nome, trabalho, dono=None, no=None):
        self.nome = nome
        self._dono = dono
        self._no = no
        self._valor = None
        self._erro = None
        self._colhida = False
        self._pronto = threading.Event()

        def correr():
            _PROVISIONADA.sim = True
            try:
                self._valor = trabalho()
            except BaseException as erro:      # noqa: BLE001
                # BaseException porque 'halt', 'skip' e 'yield' derivam
                # dela nesta linguagem. Um sinal solto dentro da tarefa
                # precisa chegar a quem deu 'await', e não sumir.
                self._erro = erro
            finally:
                self._pronto.set()
                _GANCHOS.disparar(
                    "falhou" if self._erro is not None else "terminou", self)

        _reservar_pilha()
        DFTarefa._VIVAS.add(self)
        _GANCHOS.disparar("criada", self)
        self._thread = threading.Thread(
            target=correr, name=f"df-async-{nome}", daemon=True)
        self._thread.start()

    def pronta(self) -> bool:
        """Já terminou? Não bloqueia."""
        return self._pronto.is_set()

    def aguardar(self, limite=None):
        """Espera terminar e devolve o valor, ou levanta o erro."""
        self._pronto.wait(limite)
        if not self._pronto.is_set():
            raise TimeoutError(
                f"a tarefa '{self.nome}' nao terminou em {limite}s")
        self._colhida = True
        if self._erro is not None:
            raise self._erro
        return self._valor

    def falhou(self) -> bool:
        return self._pronto.is_set() and self._erro is not None

    def orfa(self) -> bool:
        """Falhou, e ninguem deu 'await' nela.

        É a versão desta linguagem da promessa rejeitada sem tratamento:
        o trabalho quebrou, o erro não chegou a lugar nenhum, e sem esta
        conta o programa sairia com código 0.
        """
        return self.falhou() and not self._colhida

    @property
    def erro(self):
        return self._erro

    def __repr__(self):
        if not self._pronto.is_set():
            estado = "rodando"
        elif self._erro is not None:
            estado = f"falhou: {self._erro}"
        else:
            estado = "pronta"
        return f"<tarefa '{self.nome}' {estado}>"


class _RootProxy:
    """'root' — o membro procurado no RESTO da linhagem.

    Ele guarda uma FATIA da MRO, e nao um blueprint: 'root' significa
    "o proximo depois de quem esta rodando", e quem esta rodando muda a
    cada salto.

    Antes ele guardava o pai da classe da INSTANCIA, e com tres niveis
    isso virava laco infinito:

        blueprint A:            action v(): yield "A"
        blueprint B extends A:  action v(): yield "B>" + root.v()
        blueprint C extends B:  action v(): yield "C>" + root.v()

        spawn C().v()    ->  o teto de mil quadros, estourado

    'C.v' achava 'B.v' certo. Mas dentro de 'B.v' o 'self' continua
    sendo a instancia de C, entao 'root' voltava a ser o pai de C — o
    proprio B — e 'B.v' chamava a si mesmo para sempre. Com dois niveis
    funcionava, e por isso passou: toda heranca de dois niveis do
    repositorio esta certa.

    A fatia vem da MRO da instancia, cortada DEPOIS do blueprint que
    declarou o metodo em execucao ('__dono__'). E o mesmo que o
    'super()' do Python faz, e e o unico jeito que funciona com heranca
    multipla: o proximo da MRO nao e necessariamente uma mae direta.
    """

    __slots__ = ("instance", "restante", "interpreter")

    def __init__(self, instance, restante, interpreter):
        self.instance = instance
        self.restante = list(restante)
        self.interpreter = interpreter

    @property
    def parent(self):
        """O primeiro da fatia — o que 'root' significa hoje."""
        return self.restante[0] if self.restante else None

    def get(self, name):
        for bp in self.restante:
            if name in bp.methods:
                return bp.methods[name]
            if name in bp.statics:
                return bp.statics[name]
        raise NameError_(
            f"Parent has no member '{name}'.",
            nota=("'root' searches the rest of the lineage: "
                  + " → ".join(bp.name for bp in self.restante)
                  if self.restante else "there is no parent after this one"),
            dica="check the name, or declare the member in the parent",
            doc="oop")



def _carimbar_dono(blueprint):
    """Cada metodo passa a saber QUAL blueprint o declarou.

    O carimbo e aqui, sobre o blueprint pronto, e nao em cada um dos
    lugares que criam uma DFAction: metodo, operador, getter e setter
    sao quatro, e um quinto que aparecesse depois ficaria de fora sem
    dar erro — so faria 'root' voltar a procurar no lugar errado.
    """
    for acao in blueprint.methods.values():
        if isinstance(acao, DFAction) and acao.dono is None:
            acao.dono = blueprint
    for acao in blueprint.operators.values():
        if isinstance(acao, DFAction) and acao.dono is None:
            acao.dono = blueprint
    for prop in blueprint.properties.values():
        for acao in (prop or {}).values():
            if isinstance(acao, DFAction) and acao.dono is None:
                acao.dono = blueprint
    return blueprint


# ── Interpreter ────────────────────────────────────────────

class Interpreter:
    """Tree-walking interpreter for DataForge AST."""

    @property
    def _depth(self):
        return self._por_thread.depth

    @_depth.setter
    def _depth(self, valor):
        self._por_thread.depth = valor

    @property
    def _call_stack(self):
        return self._por_thread.pilha

    def __init__(self):
        # Tabelas de despacho, preenchidas sob demanda por classe de no.
        # Uma por interpretador (e nao de classe) porque os metodos
        # ligados guardam a referencia a esta instancia.
        self._tabela_exec = {}
        self._tabela_eval = {}

        self.global_env = Environment(name="<global>")
        self.modules = {}
        #: [(modulo, ms)] — quanto cada 'adopt' custou. E o que 'Arcane.Inicio'
        #: le para dizer onde a partida foi gasta.
        self.boot_adocoes = []
        #: Os 'type' declarados. Nasce vazio, e quem nao declara nenhum
        #: nao paga nada: '_check_type' so olha para ca quando o nome
        #: nao e um tipo embutido.
        self.tipos_nomeados = _TiposNomeados.Registro()
        self.events = {}  # event name → list of callbacks
        # A profundidade e a pilha de quadros sao POR THREAD.
        # Compartilhadas, duas acoes 'async' rodando juntas somavam a
        # profundidade uma da outra e trocavam de quadro no meio do
        # stack trace: o erro de uma aparecia com o caminho da outra.
        self._por_thread = _PorThread()
        self._loading = []     # módulos em carga, para detectar ciclos

        # Compilar o corpo das acoes para fechamentos. Desligado pelo
        # depurador: ele sombreia 'execute' para parar em cada linha, e
        # o corpo compilado passa POR FORA de 'execute' — um depurador
        # que enxerga metade das instrucoes e pior que um interpretador
        # mais lento.
        self.compilar_corpos = True

        # Estado de biblioteca que pertence a UMA execucao — hoje so o
        # registro de testes do Crucible — e zerado na primeira, e nao
        # aqui: construir um interpretador nao deve mexer no de outro
        # que ja esteja rodando.
        self._primeira_execucao = True
        #: Erros de corpos de 'thread:' — ver 'exec_ThreadBlock'.
        self._falhas_de_thread = []
        self._trava_das_falhas = threading.Lock()
        self.filename = "<stdin>"
        # A DataForge frame costs several Python frames; give the interpreter
        # room so its own depth guard reports the error instead of CPython.
        if sys.getrecursionlimit() < 20000:
            sys.setrecursionlimit(20000)

        # Set interpreter reference for DFAction __call__
        DFAction._interpreter = self

        # str() and 'out' must format values identically.
        set_stringifier(self._to_str)
        set_repr(self._repr_do_objeto)
        # Os embutidos precisam chamar metodo magico: 'len(obj)' honra
        # '__len__', 'int(obj)' honra '__int__'. Eles nao podem importar
        # o interpretador — seria ciclo — entao ele se registra aqui.
        set_magic_dispatcher(self._despachar_magico)

        # Load builtins
        #
        # Elas ficam MARCADAS: uma atribuicao dentro de uma acao nao
        # pode subir ate aqui e apagar 'len' para o programa inteiro.
        # Ver 'Environment.embutidas'.
        self.global_env.embutidas = set()
        for name, value in get_builtins().items():
            self.global_env.set_local(name, value)
            self.global_env.embutidas.add(name)

    #: Como explicar um sinal de controle que escapou ate o topo.
    _SINAIS_SOLTOS = {
        'HaltSignal': ("halt", "loop",
                       "'halt' leaves the loop it is in. Outside a "
                       "'cycle', 'persist' or 'perform', there is nothing "
                       "to leave.\n"
                       "    To end the program, use 'yield' inside an "
                       "action, or just let it reach the end."),
        'SkipSignal': ("skip", "loop",
                       "'skip' jumps to the next iteration. Outside a "
                       "'cycle', 'persist' or 'perform', there is no next "
                       "iteration to jump to.\n"
                       "    Inside a 'handle', to ignore the error and go "
                       "on, leave the block empty or write what should "
                       "happen instead."),
        'YieldSignal': ("yield", "action",
                        "'yield' returns from the action it is in. At the "
                        "top level of a file there is no action to return "
                        "from.\n"
                        "    Use 'out' to print a value, or wrap the code "
                        "in an action."),
    }

    def run(self, program: ast.Program, filename: str = ""):
        """Execute a full program."""
        if filename:
            self.filename = filename
        try:
            resultado = _com_pilha_propria(lambda: self._rodar(program))
        finally:
            # Os 'defer' escritos no topo rodam no fim do programa, inclusive
            # quando ele sai por erro — que e o ponto de um 'defer'.
            self._run_deferred(self.global_env)
        self._cobrar_tarefas_orfas()
        self._cobrar_falhas_de_thread()
        return resultado

    #: Quanto esperar, no fim do programa, por uma tarefa que ainda roda.
    #: Curto de proposito: o objetivo e colher quem ja falhou, nao virar
    #: um 'join' que segura a saida.
    PRAZO_DAS_ORFAS = 0.05

    def _cobrar_tarefas_orfas(self):
        """Uma tarefa 'async' que falhou e ninguem colheu nao pode sumir.

        Era a ultima das tres a engolir erro em silencio: 'thread' e
        'parallel' ja desenham o erro e reprovam a saida, e a tarefa
        'async' saia com codigo 0 levando o erro junto. E o mesmo defeito
        que fez o Node passar a derrubar o processo numa promessa
        rejeitada sem tratamento — o trabalho quebra, o erro nao chega a
        lugar nenhum, e o CI fica verde.

        Quem deu 'await' NAO e cobrado aqui: ele ja recebeu o erro, e um
        'handle' pode te-lo tratado. Cobrar de novo faria um programa
        correto falhar.
        """
        # So as tarefas DESTE interpretador, e cada uma cobrada uma vez.
        # A lista de vivas e do processo — util para 'Async.vivas()' —, e
        # sem o dono um teste cobraria a tarefa orfa do teste anterior.
        orfas = []
        for tarefa in list(DFTarefa._VIVAS):
            if tarefa._dono is not self:
                continue
            if not tarefa.pronta():
                tarefa._pronto.wait(self.PRAZO_DAS_ORFAS)
            if tarefa.orfa():
                orfas.append(tarefa)
                tarefa._colhida = True
        if not orfas:
            return

        primeira = orfas[0]
        erro = primeira.erro
        mensagem = getattr(erro, "message", None) or str(erro)
        n = len(orfas)
        nomes = ", ".join(sorted({t.nome for t in orfas})[:4])
        resumo = RuntimeError_(
            f"{n} async task(s) failed and nobody awaited them: {nomes}",
            getattr(primeira._no, "line", 0),
            getattr(primeira._no, "column", 0),
            nota=f"first: {mensagem}",
            dica="use  await  to receive the value AND the error, or wrap "
                 "the call in 'monitor' inside the action itself",
            doc="biblioteca/async")
        resumo.filename = self.filename
        for outra in orfas[1:]:
            resumo.outros.append(outra.erro)
        raise resumo

    def _cobrar_falhas_de_thread(self):
        """Uma thread que falhou nao pode terminar o programa com codigo 0.

        O erro dela ja foi desenhado quando aconteceu. Este e o recibo:
        curto, na linha do 'thread:', e o bastante para o CI reprovar.
        """
        with self._trava_das_falhas:
            falhas = list(self._falhas_de_thread)
            self._falhas_de_thread.clear()
        if not falhas:
            return
        erro, node = falhas[0]
        n = len(falhas)
        resumo = RuntimeError_(
            f"{n} thread(s) failed. The error{'s' if n > 1 else ''} "
            f"{'are' if n > 1 else 'is'} shown above.",
            getattr(node, "line", 0), getattr(node, "column", 0),
            nota=f"first: {erro.message}",
            dica="to catch the error with 'handle', use 'parallel', which "
                 "waits for its statements",
            doc="tecnicas/concorrencia")
        resumo.filename = self.filename
        raise resumo

    def _rodar(self, program: ast.Program):
        if self._primeira_execucao:
            self._primeira_execucao = False
            from .stdlib import reiniciar_por_execucao
            reiniciar_por_execucao()
        # 'comptime' roda ANTES do programa: é o que faz dele tempo de
        # compilação, e não "mais cedo". O que ele define já está no
        # escopo global quando a primeira linha do corpo executa.
        self._rodar_comptime(program.body)
        try:
            # O corpo do programa tambem e compilado: sem isto, um laco
            # escrito no topo — que e como quase todo exemplo comeca —
            # nao veria ganho nenhum, so o que estivesse dentro de uma
            # acao.
            if self.compilar_corpos:
                from .compilador import compilar_bloco
                return compilar_bloco(self, program.body)(self.global_env)
            return self.exec_block(program.body, self.global_env)
        except DataForgeError as erro:
            self._attach_stack(erro)
            raise
        except ControlSignal as sinal:
            # 'halt', 'skip' e 'yield' sao BaseException de proposito, para
            # que 'monitor' nao os engula. O preco e que, soltos no topo,
            # escapariam como traceback do Python — e quem escreveu .df nao
            # tem o que fazer com isso. Aqui viram erro da linguagem.
            raise self._erro_de_sinal(sinal) from None

    def _erro_de_sinal(self, sinal):
        palavra, contexto, explicacao = self._SINAIS_SOLTOS.get(
            type(sinal).__name__, ("this", "block", ""))
        artigo = "an" if contexto[0] in "aeiou" else "a"
        erro = RuntimeError_(
            f"'{palavra}' was used outside {artigo} {contexto}.",
            getattr(sinal, 'line', 0), getattr(sinal, 'column', 0),
            nota=explicacao.split("\n")[0],
            dica="\n".join(explicacao.split("\n")[1:]).strip(),
            doc="lacos" if contexto == "loop" else "acoes")
        erro.filename = self.filename
        return erro

    def exec_block(self, statements: list, env: Environment):
        """Execute a block of statements."""
        result = None
        for stmt in statements:
            result = self.execute(stmt, env)
        return result

    # ── Despacho ───────────────────────────────────────────
    #
    #  Um programa de porte medio percorre mais de um milhao de nos, e
    #  cada um passava por f"exec_{type(node).__name__}" mais um getattr.
    #  Montar string e buscar por nome nesse volume domina o tempo de
    #  execucao — era 15% do total no perfil.
    #
    #  A tabela abaixo indexa pela CLASSE do no, resolvida uma vez por
    #  tipo. Um dict de classe para metodo ligado e a estrutura mais
    #  rapida que o Python oferece para isto.

    def _resolver_exec(self, classe):
        """O metodo que executa esta classe de no. Memoriza."""
        metodo = getattr(self, f"exec_{classe.__name__}", None)
        if metodo is None:
            metodo = getattr(self, f"eval_{classe.__name__}", None)
        self._tabela_exec[classe] = metodo
        return metodo

    def _resolver_eval(self, classe):
        """O metodo que avalia esta classe de no. Memoriza."""
        metodo = getattr(self, f"eval_{classe.__name__}", None)
        if metodo is None:
            metodo = getattr(self, f"exec_{classe.__name__}", None)
        self._tabela_eval[classe] = metodo
        return metodo

    def execute(self, node, env: Environment):
        """Executa um no."""
        if node is None:
            return None
        classe = node.__class__
        metodo = self._tabela_exec.get(classe)
        if metodo is None:
            metodo = self._resolver_exec(classe)
            if metodo is None:
                raise RuntimeError_(
                    f"Cannot execute node type: {classe.__name__}",
                    node.line, node.column)
        try:
            return metodo(node, env)
        except DataForgeError as erro:
            # Ja e da linguagem: passa reto. So ganha a posicao da
            # instrucao quando nao tem nenhuma — o erro levantado longe do
            # codigo (a colecao tipada recusando um 'xs[0] :=') nao conhece
            # a linha, e sem ela sairia em 0:0, sem o trecho desenhado.
            if not erro.line:
                _posicionar(erro, node)
            raise
        except ControlSignal:
            # Desvio de fluxo: passa reto, sem mexer no traceback.
            raise
        except Exception as e:
            # Rede final. Qualquer coisa que o Python levante e que nao
            # tenha sido traduzida mais perto da causa vira erro da
            # linguagem AQUI, e nao no topo do programa — e essa a
            # diferenca entre 'monitor' capturar e nao capturar.
            #
            # Fica em 'execute' e nao em 'evaluate' de proposito: a
            # instrucao e a menor unidade que 'monitor' delimita, e
            # sao muito menos por segundo que expressoes.
            raise self._traduzir_excecao(e, node) from None

    def evaluate(self, node, env: Environment):
        """Avalia um no e devolve o valor."""
        if node is None:
            return None
        classe = node.__class__
        metodo = self._tabela_eval.get(classe)
        if metodo is None:
            metodo = self._resolver_eval(classe)
            if metodo is None:
                raise RuntimeError_(
                    f"Cannot evaluate node type: {classe.__name__}",
                    node.line, node.column)
        return metodo(node, env)

    # ═══════════════════════════════════════════════════════
    #  LITERAL EVALUATION
    # ═══════════════════════════════════════════════════════

    def eval_IntegerLiteral(self, node: ast.IntegerLiteral, env):
        return node.value

    def eval_FloatLiteral(self, node: ast.FloatLiteral, env):
        return node.value

    def eval_DecimalLiteral(self, node: ast.DecimalLiteral, env):
        return node.value

    def eval_StringLiteral(self, node: ast.StringLiteral, env):
        return node.value

    def eval_BooleanLiteral(self, node: ast.BooleanLiteral, env):
        return node.value

    def eval_VoidLiteral(self, node: ast.VoidLiteral, env):
        return None

    def eval_ListLiteral(self, node: ast.ListLiteral, env):
        if any(isinstance(e, ast.SpreadElement) for e in node.elements):
            return self._expand_elements(node.elements, env)
        return [self.evaluate(elem, env) for elem in node.elements]

    def eval_TupleLiteral(self, node: ast.TupleLiteral, env):
        """'(1, "a")' — uma tupla do Python, que e imutavel de verdade.

        Reaproveitar o tipo do Python e o que faz 'len', 'cycle', 'in',
        indice, fatia, igualdade e hash funcionarem sem que nenhum deles
        saiba o que e uma tupla. O mesmo raciocinio das colecoes tipadas.
        """
        if any(isinstance(e, ast.SpreadElement) for e in node.elements):
            return _Tupla(self._expand_elements(node.elements, env))
        return _Tupla(self.evaluate(elem, env) for elem in node.elements)

    def eval_DictLiteral(self, node: ast.DictLiteral, env):
        result = {}
        for key_node, val_node in node.pairs:
            if isinstance(key_node, ast.SpreadElement):
                base = self.evaluate(key_node.value, env)
                if isinstance(base, DFRecordInstance):
                    base = dict(base.values)
                elif isinstance(base, DFInstance):
                    base = dict(base.fields)
                if not isinstance(base, dict):
                    raise TypeError_(
                        f"Cannot spread {self._type_of(base)} into a vault: "
                        f"'...' needs a Vault, a record or an instance",
                        key_node.line, key_node.column)
                result.update(base)
                continue
            result[self.evaluate(key_node, env)] = self.evaluate(val_node, env)
        return result

    # ═══════════════════════════════════════════════════════
    #  EXPRESSION EVALUATION
    # ═══════════════════════════════════════════════════════

    def eval_Identifier(self, node: ast.Identifier, env):
        # Special: 'root' inside a method = proxy to parent blueprint methods
        if node.name == 'root':
            # Find 'self' in scope to get the instance's parent
            if env.has('self'):
                instance = env.get('self')
                if isinstance(instance, DFInstance):
                    restante = self._linhagem_acima(instance, env)
                    if restante:
                        return _RootProxy(instance, restante, self)
        try:
            return env.get(node.name)
        except NameError_ as e:
            # Nome de erro como valor: 'to_raise(KeyError)',
            # 'e.type is KeyError'. Fica aqui, e nao nos builtins,
            # porque sao TIPOS e nao funcoes — a doc de embutidas
            # listaria 177 nomes que ninguem chama.
            #
            # E o ultimo recurso, depois do escopo: quem declarar uma
            # variavel chamada 'KeyError' continua vendo a sua.
            tipo = erro_por_nome(node.name)
            if tipo is not None:
                return tipo

            # O Environment nao conhece posicao; o no conhece.
            if not e.line:
                e.line, e.column = node.line, node.column
                e.span = len(node.name)
                e.args = (e.format(),)
            raise

    def eval_BinaryOp(self, node: ast.BinaryOp, env):
        return self._operar(self.evaluate(node.left, env), node.op,
                            self.evaluate(node.right, env), node, env)

    # ═══════════════════════════════════════════════════════
    #  Metodos magicos
    # ═══════════════════════════════════════════════════════
    #
    # Um metodo magico e um gancho: a linguagem o procura no blueprint
    # quando uma operacao acontece. Declarar '__add__' faz o '+'
    # funcionar sobre a instancia.
    #
    # A busca custa uma leitura de dicionario por operacao sobre
    # instancia — e ZERO sobre numero, texto ou colecao, porque o
    # 'isinstance' que a guarda vem antes. Isso importa: o caminho
    # rapido do interpretador nao pode pagar por um recurso que a
    # maioria dos programas nao usa.

    _NO_SEM_POSICAO = None

    def _no_interno(self):
        """Um no falso, para chamar metodo fora de uma expressao."""
        if Interpreter._NO_SEM_POSICAO is None:
            Interpreter._NO_SEM_POSICAO = type(
                "_NoInterno", (), {"line": 0, "column": 0})()
        return Interpreter._NO_SEM_POSICAO

    @staticmethod
    def _achar_magico(valor, nome):
        """O metodo magico na linhagem do objeto, ou None.

        Percorre a MRO, e nao so o blueprint direto: um '__str__'
        declarado na mae vale para a filha, como qualquer metodo.
        """
        bp = getattr(valor, "blueprint", None)
        if bp is None:
            return None
        cache = getattr(bp, "cache_magico", None)
        if cache is not None:
            try:
                return cache[nome]
            except KeyError:
                pass
        achado = None
        for ancestral in bp.linhagem():
            acao = ancestral.methods.get(nome)
            if acao is not None:
                achado = acao
                break
        if cache is not None:
            cache[nome] = achado
        return achado

    def _tem_magico(self, valor, nome):
        return self._achar_magico(valor, nome) is not None

    def _chamar_magico(self, valor, nome, args, node=None):
        """Chama o metodo magico. Quem chama ja conferiu que ele existe."""
        acao = self._achar_magico(valor, nome)
        if acao is None:
            return _SEM_MAGICO
        return self._call_action(acao, list(args), {},
                                 node or self._no_interno(), None,
                                 instance=valor)

    def _despachar_magico(self, obj, nome, args=()):
        """O ponto por onde os embutidos chamam um metodo magico.

        Devolve None quando o metodo nao existe — e o que 'builtins.py'
        espera para cair no comportamento normal.
        """
        if not isinstance(obj, DFInstance):
            return None
        resultado = self._chamar_magico(obj, nome, list(args))
        return None if resultado is _SEM_MAGICO else resultado

    def _magico_binario(self, left, op, right, node, env):
        """O metodo magico de um operador binario, se houver.

        Tenta o da esquerda; se ele nao existir ou devolver o marcador
        de 'nao sei fazer', tenta o REFLETIDO da direita. E o que faz
        '2 * vetor' funcionar quando so o vetor sabe multiplicar.
        """
        nome = magicos.POR_OPERADOR.get(op)
        if nome is None:
            return _SEM_MAGICO

        if isinstance(left, DFInstance):
            resultado = self._chamar_magico(left, nome, [right], node)
            if resultado is not _SEM_MAGICO and resultado is not NotImplemented:
                return resultado

        refletido = magicos.REFLETIDO.get(nome)
        if refletido and isinstance(right, DFInstance):
            resultado = self._chamar_magico(right, refletido, [left], node)
            if resultado is not _SEM_MAGICO and resultado is not NotImplemented:
                return resultado

        return _SEM_MAGICO

    def _magico_comparacao(self, left, op, right, node):
        """O metodo magico de uma comparacao.

        Quando so '__cmp__' existe, ele responde os seis: devolve
        negativo, zero ou positivo, e a tabela traduz. E o atalho de
        quem tem uma ordem natural e nao quer escrever seis metodos.
        """
        nome = magicos.POR_COMPARACAO.get(op)
        if nome is None:
            return _SEM_MAGICO

        for lado, outro, inverter in ((left, right, False), (right, left, True)):
            if not isinstance(lado, DFInstance):
                continue

            alvo = nome
            if inverter:
                # a < b vira b > a quando so 'b' sabe comparar.
                alvo = {"__lt__": "__gt__", "__gt__": "__lt__",
                        "__le__": "__ge__", "__ge__": "__le__"}.get(nome, nome)

            if self._tem_magico(lado, alvo):
                return self._chamar_magico(lado, alvo, [outro], node)

            if self._tem_magico(lado, "__cmp__"):
                c = self._chamar_magico(lado, "__cmp__", [outro], node)
                if c is not _SEM_MAGICO and isinstance(c, (int, float)):
                    return magicos.DE_CMP[alvo](c)

        return _SEM_MAGICO

    def _verdade(self, valor, node=None):
        """O que 'given valor:' decide.

        Uma instancia com '__bool__' responde por si. Sem ele, mas com
        '__len__', vale a regra do Python: tamanho zero e falso. Sem os
        dois, todo objeto e verdadeiro — que e o que faz sentido para
        algo que existe.
        """
        if isinstance(valor, DFInstance):
            if self._tem_magico(valor, "__bool__"):
                return bool(self._chamar_magico(valor, "__bool__", [], node))
            if self._tem_magico(valor, "__len__"):
                return bool(self._chamar_magico(valor, "__len__", [], node))
            return True
        return bool(valor)

    def _operar(self, left, op, right, node, env):
        """Aplica um operador binario a dois valores JA avaliados.

        Separado de eval_BinaryOp para que 'x += 1' possa chamar isto
        direto. Antes, a atribuicao composta montava dois nos de AST por
        volta so para reusar a avaliacao — 220 mil alocacoes num laco de
        200 mil voltas, jogadas fora em seguida.
        """
        # ── Sobrecarga de operador ─────────────────────────
        # 'operator + (outro):' declarado no blueprint tem prioridade.
        for lado, outro, invertido in ((left, right, False), (right, left, True)):
            if not isinstance(lado, DFInstance):
                continue
            sobrecarga = lado.blueprint.buscar_operador(op)
            if sobrecarga is None:
                continue
            # a + b tenta 'a'; se so 'b' define, ainda funciona para
            # operadores comutativos, mas nunca para os que nao sao
            if invertido and op in ('-', '/', '%', '**', '<', '>', '<=', '>='):
                continue
            return self._call_action(sobrecarga, [outro], {}, node, env,
                                     instance=lado)

        # ── Metodo magico ──────────────────────────────────
        # Depois de 'operator', que e a forma nativa e mais direta de
        # ler; antes do caminho numerico, senao '1 + vetor' estouraria
        # antes de perguntar ao vetor.
        if isinstance(left, DFInstance) or isinstance(right, DFInstance):
            resultado = self._magico_binario(left, op, right, node, env)
            if resultado is not _SEM_MAGICO:
                return resultado

        # Forma antiga, mantida: metodos 'add', 'sub'…
        op_methods = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div',
                      '%': 'mod', '**': 'pow', '//': 'floordiv'}
        if isinstance(left, DFInstance) and op in op_methods:
            method_name = op_methods[op]
            if left.has_method(method_name):
                method = left.get(method_name)
                return self._call_action(method, [right], {}, node, env, instance=left)

        try:
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    # 'void' em texto e recusado. Todo o resto coage.
                    #
                    # '"Ola, " + nome' com 'nome' void devolvia
                    # '"Ola, void"' — a palavra 'void' impressa na nota
                    # fiscal, e nem o 'check' nem o 'lint' diziam nada.
                    # E o '"undefined"' do JavaScript, e era a unica
                    # armadilha de corrupcao silenciosa que a linguagem
                    # ainda tinha: um campo que nao veio nao vira texto,
                    # vira erro.
                    #
                    # Numero e booleano continuam coagindo ('42 + "x"' e
                    # '"42x"'): ali os dois lados existem, e o resultado
                    # e o que quem escreveu quis dizer. O que nao existe
                    # e que nao pode virar texto em silencio.
                    #
                    # A interpolacao NAO passa por aqui, e de proposito:
                    # '$"Ola, {nome}"' e um pedido explicito de desenhar
                    # o valor, e continua escrevendo 'void'. E tambem a
                    # saida de quem quer o comportamento antigo.
                    lado = 'left' if left is None else (
                        'right' if right is None else None)
                    if lado:
                        raise TypeError_(
                            "Cannot add Void to text.",
                            node.line, node.column,
                            nota=f"the {lado} side evaluated to 'void'",
                            dica=("a missing value does not become text. "
                                  "Give it a default:\n"
                                  '    "Ola, " + (nome ?? "")\n'
                                  "or render it on purpose, which keeps "
                                  "the word 'void':\n"
                                  '    $"Ola, {nome}"'),
                            doc="operadores")
                    return self._to_str(left) + self._to_str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise DivisionByZeroError(
                        "Division by zero.", node.line, node.column,
                        nota="the right side evaluated to 0",
                        dica=("guard the divisor first:\n"
                              "    given divisor isnt 0:\n"
                              "        out a / divisor"),
                        doc="operadores")
                return left / right
            elif op == '%':
                if right == 0:
                    raise DivisionByZeroError(
                        "Remainder by zero.", node.line, node.column,
                        nota="'%' divides too, so a zero on the right has no answer",
                        dica=("guard the divisor first:\n"
                              "    given divisor isnt 0:\n"
                              "        out a % divisor"),
                        doc="operadores")
                return left % right
            elif op == '**':
                return left ** right
            elif op == '//':
                if right == 0:
                    raise DivisionByZeroError(
                        "Division by zero.", node.line, node.column,
                        nota="the right side evaluated to 0",
                        dica=("guard the divisor first:\n"
                              "    given divisor isnt 0:\n"
                              "        out a / divisor"),
                        doc="operadores")
                return left // right
        except TypeError as e:
            for lado in (left, right):
                if isinstance(lado, DFTarefa):
                    raise self._erro_de_tarefa(lado, node) from None
            misto = self._erro_de_exato_com_float(left, right, op, node)
            if misto is not None:
                raise misto from None
            # "unsupported operand type(s) for +: 'int' and 'list'" esta
            # certa e fala de tipos que nao existem aqui. A que importa
            # diz o que se tentou somar, no vocabulario da linguagem.
            esquerda = self._nome_do_tipo(left)
            direita = self._nome_do_tipo(right)
            raise TypeError_(
                f"'{op}' between {esquerda} and {direita} is not defined.",
                node.line, node.column,
                nota=_traduzir_tipos(str(e)),
                dica=self._dica_de_operacao(left, right, op),
                doc="operadores") from None

    def _dica_de_operacao(self, left, right, op):
        """O que fazer, quando da para saber.

        Uma dica errada e pior que nenhuma, entao so fala nos casos em
        que a intencao e obvia — e sao justamente os que mais aparecem.
        """
        if op == "+" and isinstance(left, (list, tuple)) != isinstance(
                right, (list, tuple)):
            return ("to put an item into a cluster, use  [...xs, item]  "
                    "or  xs.append(item)")
        if op == "+" and isinstance(left, dict) or isinstance(right, dict):
            return "to join two vaults, use  {...a, ...b}"
        if op in ("*", "/", "-") and (isinstance(left, str)
                                      or isinstance(right, str)):
            return ("a String only accepts  +  (which joins) and  *  by an "
                    "Integer (which repeats)")
        if isinstance(left, type(None)) or isinstance(right, type(None)):
            return ("one side is Void — check with  ??  before the "
                    "operation:  (x ?? 0) + 1")
        return ""

    @staticmethod
    def _erro_de_exato_com_float(left, right, op, node):
        """Um lado exato e o outro aproximado — a recusa e deliberada.

        Somar um Decimal com um Float devolveria um Float, e a garantia
        que a pessoa veio buscar desapareceria em silencio. A mensagem
        crua do Python — "unsupported operand type(s) for +:
        'decimal.Decimal' and 'float'" — esta certa e nao diz nada disso.
        """
        import decimal as _dec

        exato = isinstance(left, _dec.Decimal), isinstance(right, _dec.Decimal)
        flutuante = isinstance(left, float), isinstance(right, float)
        if not (any(exato) and any(flutuante)):
            return None

        qual = "a esquerda" if exato[0] else "a direita"
        outro = "direita" if exato[0] else "esquerda"
        return TypeError_(
            f"'{op}' entre um Decimal e um Float e recusado.",
            node.line, node.column,
            nota=f"{qual} e exata e a {outro} e aproximada; o resultado "
                 f"seria aproximado, e a garantia se perderia sem aviso",
            dica="converta o lado que falta:\n"
                 "    Decimal.de(x) + exato       para seguir exato\n"
                 "    Decimal.float(exato) + x    para aceitar o float",
            doc="tecnicas/decimal")

        raise RuntimeError_(f"Unknown binary operator: {op!r}", node.line, node.column)

    def _conferir_fonte_do_pipeline(self, fonte, node):
        """Um `>>` sobre algo que nao e colecao.

        O caso que traz quase todo mundo aqui e a precedencia do
        lambda:

            f := lambda => xs >> morph x: x * 2

        O corpo do lambda e `xs`, e o pipeline recebe o LAMBDA como
        fonte. A mensagem que saia — "'DFAction' object is not
        iterable" — fala de uma classe do Python e nao diz o que
        fazer; a resposta e um par de parenteses.
        """
        if isinstance(fonte, (list, tuple, set, dict, str, range)):
            return
        if isinstance(fonte, DFAction):
            raise TypeError_(
                "A pipeline cannot start from an action.",
                getattr(node, "line", 0), getattr(node, "column", 0),
                nota="a lambda body binds tighter than '>>', so "
                     "'lambda => xs >> morph …' pipes the LAMBDA",
                dica="wrap the body:  lambda => (xs >> morph x: x * 2)",
                doc="pipelines")
        if fonte is None:
            raise TypeError_(
                "A pipeline cannot start from Void.",
                getattr(node, "line", 0), getattr(node, "column", 0),
                nota="whatever produced the source returned 'void'",
                dica="use  ?? []  to pipe an empty cluster instead:  "
                     "(x ?? []) >> morph …",
                doc="pipelines")
        # Objeto estranho — da ponte, um generator, um iteravel proprio:
        # calar. Ele pode ser iteravel por protocolo, e recusar aqui
        # quebraria 'adopt Python.numpy' num pipeline.

    def eval_UnaryOp(self, node: ast.UnaryOp, env):
        return self._aplicar_unario(self.evaluate(node.operand, env),
                                    node.op, node)

    def _aplicar_unario(self, operand, op, node):
        """`-x`, `+x`, `~x` — com o valor ja avaliado.

        A decisao mora aqui, e nao em `eval_UnaryOp`, para o compilador
        de fechamentos poder chamar a MESMA regra em vez de escrever a
        segunda copia dela. E a regra que a trava pede: quando um
        `eval_` avalia as partes e depois decide, a decisao sai para um
        auxiliar que recebe os valores prontos.
        """
        if isinstance(operand, DFInstance):
            nome = magicos.POR_UNARIO.get(op)
            if nome:
                resultado = self._chamar_magico(operand, nome, [], node)
                if resultado is not _SEM_MAGICO:
                    return resultado

        if op == '-':
            return -operand
        if op == '+':
            return +operand
        if op == '~':
            return ~operand
        raise RuntimeError_(f"Unknown unary operator: {op}", node.line, node.column)

    #: 'is' e '==' sao o mesmo operador para efeito de sobrecarga.
    _SIMBOLO_COMPARACAO = {
        'is': '==', '==': '==', 'isnt': '!=', '!=': '!=',
        'bigger': '>', '>': '>', 'smaller': '<', '<': '<',
        'bigger_eq': '>=', '>=': '>=', 'smaller_eq': '<=', '<=': '<=',
    }

    def eval_ComparisonOp(self, node: ast.ComparisonOp, env):
        return self._comparar(self.evaluate(node.left, env), node.op,
                              self.evaluate(node.right, env), node, env)

    def _comparar(self, left, op, right, node, env):
        """A comparacao com os dois lados JA avaliados.

        Separado de 'eval_ComparisonOp' porque o compilador de closures
        precisa exatamente disto: ele avalia os lados pelos fechamentos
        que ja montou, e so entao pergunta o resultado. Chamar
        'eval_ComparisonOp' o faria reavaliar a arvore.
        """
        # ── Sobrecarga de comparacao ───────────────────────
        simbolo = self._SIMBOLO_COMPARACAO.get(op)
        if simbolo is not None:
            for lado, outro, invertido in ((left, right, False),
                                           (right, left, True)):
                if not isinstance(lado, DFInstance):
                    continue
                sobrecarga = lado.blueprint.buscar_operador(simbolo)
                if sobrecarga is None:
                    # '!=' pode sair de '==' negado; '>' de '<' invertido
                    if simbolo == '!=':
                        eq = lado.blueprint.buscar_operador('==')
                        if eq is not None:
                            return not bool(self._call_action(
                                eq, [outro], {}, node, env, instance=lado))
                    continue
                if invertido and simbolo in ('<', '>', '<=', '>='):
                    continue
                return self._call_action(sobrecarga, [outro], {}, node, env,
                                         instance=lado)

        # ── Metodo magico de comparacao ────────────────────
        if isinstance(left, DFInstance) or isinstance(right, DFInstance):
            resultado = self._magico_comparacao(left, op, right, node)
            if resultado is not _SEM_MAGICO:
                return resultado

        if op == 'is':
            return left == right
        elif op == 'isnt':
            return left != right
        elif op in ('bigger', 'smaller', 'bigger_eq', 'smaller_eq'):
            # A ORDEM e o unico grupo que pode falhar: 'is' e 'isnt'
            # comparam qualquer coisa, mas "qual e o maior" nao tem
            # resposta entre um texto e um numero. A mensagem do Python
            # — "'<' not supported between instances of 'int' and 'str'"
            # — fala de tipos que nao existem nesta linguagem.
            try:
                if op == 'bigger':
                    return left > right
                if op == 'smaller':
                    return left < right
                if op == 'bigger_eq':
                    return left >= right
                return left <= right
            except TypeError as e:
                palavra = {'bigger': 'bigger', 'smaller': 'smaller',
                           'bigger_eq': 'bigger_eq',
                           'smaller_eq': 'smaller_eq'}[op]
                erro = TypeError_(
                    f"'{palavra}' between {self._nome_do_tipo(left)} and "
                    f"{self._nome_do_tipo(right)} has no answer.",
                    node.line, node.column,
                    nota=_traduzir_tipos(str(e)),
                    dica=("'is' and 'isnt' compare anything; ordering needs "
                          "two values of the same kind — convert one side "
                          "first"),
                    doc="operadores")
                # A marca deixa este erro RECONHECIVEL sem comparar texto
                # de mensagem: o 'onde' de um quadro precisa distinguir
                # "comparei com o desconhecido" de qualquer outra falha,
                # e casar a frase quebraria na primeira traducao.
                erro.ordem_sem_resposta = True
                raise erro from None
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        raise RuntimeError_(f"Unknown comparison: {op}", node.line, node.column)

    def eval_LogicalOp(self, node: ast.LogicalOp, env):
        left = self.evaluate(node.left, env)
        if node.op == 'and':
            if not left:
                return left
            return self.evaluate(node.right, env)
        elif node.op == 'or':
            if left:
                return left
            return self.evaluate(node.right, env)

    def eval_NotOp(self, node: ast.NotOp, env):
        return not self._verdade(self.evaluate(node.operand, env), node)

    def eval_MemberAccess(self, node: ast.MemberAccess, env):
        return self._ler_membro(self.evaluate(node.object, env), node, env)

    def _ler_membro(self, obj, node, env, membro=None):
        """'obj.membro' com o objeto JA avaliado.

        O mesmo motivo de '_comparar' e '_chamar_metodo': o compilador
        de closures ja tem o objeto, e nao pode percorrer a arvore de
        novo para obte-lo.

        Esta casca existe para a POSICAO. Um objeto que decide sozinho o
        que fazer com um nome desconhecido — a ponte para o Python e o
        caso — levanta o proprio erro, com a mensagem boa, e sem linha:
        quem levanta nao conhece o arquivo. A linha esta aqui, e so
        aqui, porque o 'hasattr' la dentro dispara o erro antes de
        qualquer outro ponto poder captura-lo.
        """
        try:
            return self._ler_membro_cru(obj, node, env, membro)
        except DataForgeError as erro:
            if not erro.line:
                nome = membro if membro is not None else \
                    getattr(node, "member", "")
                erro.line, erro.column = node.line, node.column
                erro.span = len(str(nome))
                erro.args = (erro.format(),)
            raise

    def _metodo_do_enum(self, membro, nome):
        """O metodo do enum, com 'self' ja ligado neste membro.

        'Cor.Verde.hex()' precisa que 'self' seja o MEMBRO, e nao o
        enum: e o membro que tem '.value'. Um metodo sem 'self' ligado
        leria o nome do escopo de fora, e devolveria o valor errado
        sem dar erro.
        """
        enum = getattr(membro, "enum", None)
        acao = (getattr(enum, "methods", {}) or {}).get(nome)
        if not isinstance(acao, DFAction):
            return None
        ligado = DFAction(
            name=acao.name, params=acao.params, defaults=acao.defaults,
            body=acao.body, closure=acao.closure, is_async=acao.is_async,
            param_types=acao.param_types, return_type=acao.return_type,
            is_generator=acao.is_generator, type_params=acao.type_params,
            type_bounds=getattr(acao, 'type_bounds', None))
        ligado.arquivo = acao.arquivo
        ligado.self_do_enum = membro
        return ligado

    @staticmethod
    def _metodos_do_enum(membro):
        enum = getattr(membro, "enum", None)
        nomes = sorted((getattr(enum, "methods", {}) or {}))
        if not nomes:
            return ""
        return f"this enum declares: {', '.join(nomes)}"

    def _linhagem_acima(self, instance, env):
        """O que vem DEPOIS de quem declarou o metodo que esta rodando.

        '__dono__' e ligado junto de 'self' quando o metodo e chamado, e
        guarda o blueprint que o DECLAROU — que nao e o da instancia
        assim que ha tres niveis de heranca.

        Sem dono conhecido — um metodo criado a mao, um 'self.f := …' —
        recua para o comportamento antigo: as maes diretas da instancia.
        E o que 'root' sempre significou ali, e mudar isso sem saber de
        quem e o metodo seria adivinhar.
        """
        mro = instance.blueprint.linhagem()
        dono = env.get('__dono__') if env.has('__dono__') else None
        if dono is not None:
            for i, bp in enumerate(mro):
                if bp is dono:
                    return mro[i + 1:]
        return list(instance.blueprint.parents)

    def _ler_da_instancia(self, obj, membro, node, env):
        """'obj.membro' numa instancia de blueprint.

        A ordem e a de uma linguagem com descritor: '__getattribute__'
        intercepta tudo; depois a propriedade e o descritor, que vivem na
        CLASSE; depois o campo; e so quando nada existe, '__getattr__' e
        o 'on_missing' da metaclasse.
        """
        bp = obj.blueprint
        if bp.leitura_magica:
            ativos = self._por_thread.magicos_ativos
            chave = (id(obj), "__getattribute__")
            if chave not in ativos:
                acao = self._achar_magico(obj, "__getattribute__")
                ativos.add(chave)
                try:
                    return self._call_action(acao, [membro], {}, node, env,
                                             instance=obj)
                finally:
                    ativos.discard(chave)

        if membro in bp.nao_publicos:
            self._conferir_acesso(bp, membro, env, node)

        # Propriedade: 'p.area' roda o corpo do 'get area()'
        prop = bp.buscar_propriedade(membro)
        if prop is not None:
            if 'get' not in prop:
                raise TypeError_(
                    f"'{bp.name}.{membro}' is write-only: it "
                    f"has a 'set' but no 'get'.",
                    node.line, node.column)
            if prop.get('lazy'):
                estado = objetos.estado_de(obj)
                if estado.cache is None:
                    estado.cache = {}
                if membro in estado.cache:
                    valor = estado.cache[membro]
                else:
                    valor = estado.cache[membro] = self._call(
                        prop['get'], [], {}, node, env, instancia=obj)
            else:
                valor = self._call(prop['get'], [], {}, node, env, instancia=obj)
        elif bp.descritores and membro in bp.descritores:
            descritor = bp.descritores[membro]
            valor = self._chamar_magico(descritor, "__get__", [obj, bp], node)
            if valor is _SEM_MAGICO:
                valor = descritor
        else:
            try:
                valor = obj.get(membro)
            except NameError_:
                valor = self._membro_ausente(obj, membro, node, env)

        vigias = bp.vigias
        if vigias is not None and "on_read" in vigias.ganchos:
            trocado = self._gancho_de_vigia(vigias, "on_read", [obj, membro, valor], node)
            if trocado is not None and trocado is not _SEM_MAGICO:
                valor = trocado
        return valor

    def _membro_ausente(self, obj, membro, node, env):
        """O membro nao existe: '__getattr__', 'on_missing', ou o erro."""
        acao = self._achar_magico(obj, "__getattr__")
        if acao is not None:
            chave = (id(obj), "__getattr__", membro)
            ativos = self._por_thread.magicos_ativos
            if chave not in ativos:
                ativos.add(chave)
                try:
                    return self._call_action(acao, [membro], {}, node, env,
                                             instance=obj)
                finally:
                    ativos.discard(chave)
        vigias = obj.blueprint.vigias
        if vigias is not None and "on_missing" in vigias.ganchos:
            achado = self._gancho_de_vigia(vigias, "on_missing", [obj, membro], node)
            if achado is not _SEM_MAGICO:
                return achado
        return obj.get(membro)          # levanta o erro de sempre

    def _ler_membro_cru(self, obj, node, env, membro=None):
        membro = membro if membro is not None else node.member
        # O caso de quase todo acesso: 'obj.campo' num blueprint sem nada de
        # especial. Primeiro, e sem passar pelas seis perguntas de tipo que
        # vem abaixo — nenhuma delas casa com uma instancia.
        if type(obj) is DFInstance:
            bp = obj.blueprint
            if bp.leitura_simples and membro not in bp.nao_publicos \
                    and membro not in _EMBUTIDOS_DA_INSTANCIA:
                valores = obj._valores
                if obj._indice is None and membro in valores:
                    return valores[membro]
                try:
                    return obj.get(membro)
                except NameError_:
                    return self._membro_ausente(obj, membro, node, env)
        # Handle root (super) proxy
        if isinstance(obj, _RootProxy):
            return obj.get(membro)

        if isinstance(obj, DFRecordInstance):
            if membro == 'fields':
                return dict(obj.values)
            if membro == 'record_name':
                return obj.record.name
            valor = obj.get(membro)
            if isinstance(valor, DFAction):
                return BoundRecordMethod(self, obj, valor)
            return valor

        if isinstance(obj, DFRecord):
            if membro == 'fields':
                return list(obj.field_names)
            if membro in obj.methods:
                return obj.methods[membro]
            raise NameError_(
                f"Record '{obj.name}' has no static member '{membro}'",
                node.line, node.column)

        if isinstance(obj, DFEnumMember):
            if membro == 'name':
                return obj.name
            if membro == 'value':
                return obj.value
            if membro == 'index':
                return obj.index
            if membro == 'enum_name':
                return obj.enum_name
            metodo = self._metodo_do_enum(obj, membro)
            if metodo is not None:
                return metodo
            raise NameError_(
                f"Enum member '{obj}' has no member '{membro}'. "
                f"Use .name, .value or .index",
                node.line, node.column,
                nota=self._metodos_do_enum(obj),
                doc="tipos")

        if isinstance(obj, DFEnum):
            enum_methods = {
                'names': lambda: list(obj.members.keys()),
                'values': lambda: [m.value for m in obj.members.values()],
                'members': lambda: list(obj.members.values()),
                'count': lambda: len(obj.members),
                'has': lambda n: n in obj.members,
                'from_value': lambda v: next(
                    (m for m in obj.members.values() if m.value == v), None),
                'from_name': lambda n: obj.members.get(n),
            }
            if membro in obj.members:
                return obj.members[membro]
            if membro in enum_methods:
                return BuiltinFunction(membro, enum_methods[membro])
            if membro in obj.methods:
                return obj.methods[membro]
            raise NameError_(
                f"Enum '{obj.name}' has no member '{membro}'. "
                f"Members: {', '.join(obj.members)}",
                node.line, node.column)

        if isinstance(obj, DFStream):
            stream_methods = {
                'take': lambda n: obj.take(n),
                'to_cluster': lambda: obj.to_cluster(),
                'next': lambda: obj.next(),
                'reset': lambda: obj.reset(),
                'count': lambda: sum(1 for _ in obj),
                'map': lambda f: obj.map(f),
                'filter': lambda f: obj.filter(f, self._verdade),
                'skip': lambda n: obj.skip(n),
                'enumerate': lambda inicio=0: obj.enumerate(inicio),
                'reduce': lambda f, inicial=None: obj.reduce(f, inicial),
                'first': lambda: next(iter(obj), None),
            }
            if membro in stream_methods:
                return BuiltinFunction(membro, stream_methods[membro])
            raise NameError_(
                f"Stream has no member '{membro}'. Use take, skip, "
                f"to_cluster, next, reset, count, map, filter, enumerate, "
                f"reduce or first",
                node.line, node.column)

        if isinstance(obj, DFInstance):
            # Instance built-in methods
            if membro == 'blueprint_name':
                return obj.blueprint.name
            if membro == 'fields':
                return dict(obj.fields)
            if membro == 'methods':
                return list(obj.blueprint.methods.keys())

            return self._ler_da_instancia(obj, membro, node, env)

        elif isinstance(obj, DFBlueprint):
            if membro in obj.statics:
                return obj.statics[membro]
            if membro in obj.methods:
                if membro in obj.static_methods:
                    return obj.methods[membro]
                raise TypeError_(
                    f"'{obj.name}.{membro}' is an instance method: it "
                    f"needs an object.\n"
                    f"    Spawn one first:  obj := spawn {obj.name}(…)  "
                    f"then obj.{membro}(…)\n"
                    f"    Or declare it as 'static action {membro}(…)'.",
                    node.line, node.column)
            self._erro_membro_blueprint(obj, node)
        elif isinstance(obj, dict):
            # Module namespace dicts: check key access first
            if "__name__" in obj and membro in obj:
                return obj[membro]
            # Check dict methods
            dict_methods = _METODOS_DE_VAULT
            if membro in dict_methods:
                return BuiltinFunction(membro, _ligar_ao_objeto(dict_methods[membro], obj))
            if membro == 'length':
                return len(obj)
            # Fall back to key access
            if membro in obj:
                return obj[membro]
            raise self._erro_membro(obj, membro, node)
        elif isinstance(obj, str):
            # String methods - comprehensive
            string_methods = _METODOS_DE_TEXTO
            if membro in string_methods:
                return BuiltinFunction(membro, _ligar_ao_objeto(string_methods[membro], obj))
            if membro == 'length':
                return len(obj)
        elif isinstance(obj, list):
            list_methods = _METODOS_DE_CLUSTER
            if membro in list_methods:
                return BuiltinFunction(membro, _ligar_ao_objeto(list_methods[membro], obj))
            if membro == 'length':
                return len(obj)
        elif isinstance(obj, DFAction):
            # Uma acao expoe o que DECIDIMOS que ela expoe.
            #
            # Ela caia no 'hasattr' logo abaixo — a porta do Python,
            # que existe para um 'ndarray' e para o que vem por
            # 'adopt Python.…'. Uma DFAction nao vem de fora: os
            # atributos dela sao os campos da classe do interpretador,
            # e 'f.body' devolvia
            #
            #     [YieldStatement(line=2, column=5, value=Identifier(…))]
            #
            # — a arvore, com os nomes das classes do Python, num
            # valor e nao numa mensagem. Quem lesse aquilo concluiria
            # que a linguagem tem reflexao sobre a arvore, e ela nao
            # tem: sao os bastidores escapando.
            if membro == 'name':
                return obj.name
            if membro == 'aridade':
                return len(obj.params)
            raise NameError_(
                f"Action '{obj.name}' has no member '{membro}'.",
                node.line, node.column,
                nota="an action offers 'name' and 'aridade'",
                dica=f"to call it, write  {obj.name}(…)")
        elif hasattr(obj, membro):
            return getattr(obj, membro)

        if obj is None:
            # O caso mais comum, e o unico com resposta pronta: uma
            # busca que nao achou, um campo que nao veio, uma chamada
            # que devolveu 'void'.
            raise NameError_(
                f"Cannot read '{membro}': the value is Void.",
                node.line, node.column,
                nota="something before this returned 'void'",
                dica=(f"use  ?.  to stop safely:  x?.{membro}\n"
                      f"    or a default:  (x ?? padrao).{membro}"),
                doc="operadores")
        raise NameError_(
            f"Cannot access member '{membro}' on "
            f"{self._nome_do_tipo(obj)}.",
            node.line, node.column)

    def eval_IndexAccess(self, node: ast.IndexAccess, env):
        return self._ler_indice(self.evaluate(node.object, env),
                                self.evaluate(node.index, env), node, env)

    def _ler_indice(self, obj, index, node, env):
        """'obj[index]' com os dois JA avaliados.

        O mesmo motivo de '_comparar', '_chamar_metodo' e '_ler_membro':
        o compilador de fechamentos ja tem os valores, e nao pode
        percorrer a arvore de novo para obte-los.
        """
        if isinstance(obj, DFInstance):
            resultado = self._chamar_magico(obj, "__getitem__", [index], node)
            if resultado is not _SEM_MAGICO:
                return resultado
            # '__missing__' e a ultima chance antes do erro: e como um
            # vault com valor padrao se escreve.
            resultado = self._chamar_magico(obj, "__missing__", [index], node)
            if resultado is not _SEM_MAGICO:
                return resultado

        try:
            return obj[index]
        except KeyError:
            raise self._erro_chave(obj, index, node)
        except IndexError:
            raise self._erro_indice(obj, index, node)
        except TypeError:
            if isinstance(index, (dict, list)):
                raise TypeError_(
                    f"An index cannot be {self._nome_do_tipo(index)}.",
                    node.line, node.column,
                    dica="Use an Integer for a Cluster, or a String for a Vault.",
                    doc="colecoes")
            if isinstance(obj, DFTarefa):
                raise self._erro_de_tarefa(obj, node)
            raise TypeError_(
                f"{self._nome_do_tipo(obj).capitalize()} cannot be indexed.",
                node.line, node.column,
                nota="Only Cluster, Vault, String and record accept [ ].",
                doc="colecoes")

    def _erro_membro(self, alvo, membro, node):
        """'x.membro' que nao existe: diz onde procurou e o que existe.

        Um modulo se identifica por '__name__' — e a mensagem precisa
        chama-lo de modulo, nao de vault. Antes era um seco
        "Vault has no key 'chunks'": nenhuma sugestao, e o nome errado
        para a coisa. Uma variavel errada ja ganhava "did you mean";
        um simbolo da stdlib, nao — e sao 1016 deles.
        """
        import difflib

        nomes = [k for k in alvo if not str(k).startswith("__")]
        modulo = alvo.get("__name__") if isinstance(alvo, dict) else None
        onde = f"module '{modulo}'" if modulo else "this vault"

        perto = difflib.get_close_matches(str(membro), [str(k) for k in nomes],
                                          n=3, cutoff=0.6)
        if perto:
            alvos = " or ".join(f"'{p}'" for p in perto)
            dica = f"did you mean {alvos}?"
        elif modulo:
            dica = ("in the repl, ':modules' lists the modules and ':doc <nome>' "
                    "lists the symbols of one; doc/BIBLIOTECA_PADRAO.md has "
                    "every signature")
        else:
            amostra = ", ".join(f"'{k}'" for k in nomes[:6])
            resto = f" (+{len(nomes) - 6} more)" if len(nomes) > 6 else ""
            dica = (f"it has: {amostra}{resto}" if nomes
                    else "it is empty — fill it before reading")

        return NameError_(
            f"{onde} has no '{membro}'.",
            getattr(node, "line", 0), getattr(node, "column", 0),
            nota=(f"the module has {len(nomes)} symbols" if modulo and not perto
                  else ""),
            dica=dica,
            doc="biblioteca" if modulo else "colecoes")

    def _erro_chave(self, vault, chave, node):
        """Chave ausente num vault: mostra o que existe e o que fazer."""
        import difflib
        chaves = [k for k in vault] if isinstance(vault, dict) else []
        texto_chave = self._to_str(chave)

        perto = difflib.get_close_matches(
            str(chave), [str(k) for k in chaves], n=1, cutoff=0.6)
        if perto:
            nota = f"there is a similar key: \"{perto[0]}\""
            dica = f"did you mean vault[\"{perto[0]}\"]?"
        elif not chaves:
            nota = "this vault is empty"
            dica = "fill it before reading, or use ?? for a fallback value"
        else:
            amostra = ", ".join(f'"{k}"' for k in list(chaves)[:6])
            resto = f" (+{len(chaves) - 6} more)" if len(chaves) > 6 else ""
            nota = (f"the vault has {len(chaves)} "
                    f"{'key' if len(chaves) == 1 else 'keys'}: {amostra}{resto}")
            dica = ("use  valor ?? padrao  for a fallback, or check first "
                    "with  vault.has(chave)")

        return KeyError_(
            f'Key "{texto_chave}" is not in this vault.',
            node.line, node.column, nota=nota, dica=dica, doc="colecoes",
            rotulo="key read here")

    def _erro_indice(self, sequencia, indice, node):
        """Indice fora da faixa: diz o tamanho e a faixa valida."""
        n = len(sequencia)
        tipo = "Cluster" if isinstance(sequencia, list) else "String"

        if n == 0:
            return EmptyCollectionError(
                f"Index {indice} is out of range: this {tipo.lower()} is empty.",
                node.line, node.column,
                dica=("check it is not empty before reading:  "
                      "given len(itens) bigger 0:"),
                doc="colecoes", rotulo="nothing to read")

        return IndexError_(
            f"Index {indice} is out of range for a {tipo.lower()} "
            f"of {n} {'item' if n == 1 else 'items'}.",
            node.line, node.column,
            nota=f"valid indexes go from 0 to {n - 1}, or -1 to -{n} from the end",
            dica=("remember the last index is len(x) - 1, not len(x)"
                  if indice == n else
                  f"use  x[-1]  for the last item"),
            doc="colecoes", rotulo="out of range")

    def eval_SliceAccess(self, node: ast.SliceAccess, env):
        obj = self.evaluate(node.object, env)
        start = self.evaluate(node.start, env) if node.start is not None else None
        stop = self.evaluate(node.stop, env) if node.stop is not None else None
        step = self.evaluate(node.step, env) if node.step is not None else None
        try:
            return obj[start:stop:step]
        except TypeError as e:
            raise TypeError_(
                f"Cannot slice {self._nome_do_tipo(obj)}.",
                node.line, node.column,
                nota=_traduzir_tipos(str(e)),
                dica="only Cluster, String and Bytes accept  [a:b]",
                doc="colecoes") from None

    def eval_LambdaExpression(self, node: ast.LambdaExpression, env):
        """A lambda is an anonymous action closing over the current scope."""
        return DFAction(
            name="<lambda>",
            params=list(node.params),
            defaults=dict(node.defaults),
            body=[ast.YieldStatement(value=node.body, line=node.line, column=node.column)],
            closure=env,
            param_types=dict(node.param_types),
        )

    def eval_FunctionCall(self, node: ast.FunctionCall, env):
        callee = self.evaluate(node.callee, env)
        args = self._eval_args(node.args, env)
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}
        return self._call(callee, args, kwargs, node, env)

    def eval_MethodCall(self, node: ast.MethodCall, env):
        return self._chamar_metodo(
            self.evaluate(node.object, env),
            self._eval_args(node.args, env),
            {k: self.evaluate(v, env) for k, v in node.kwargs.items()},
            node, env)

    def _chamar_metodo(self, obj, args, kwargs, node, env):
        """'obj.metodo(...)' com o objeto e os argumentos JA avaliados.

        Esta casca existe para a POSICAO, pelo mesmo motivo que a de
        '_ler_membro' — e a simetria e o ponto. Quem decide que o nome
        nao existe e o objeto ('DFRecordInstance.get', 'DFInstance.get'),
        e ele levanta com a mensagem boa e sem linha: quem levanta nao
        conhece o arquivo.

        A leitura tinha a casca e a chamada nao, entao as duas metades do
        mesmo erro sairam diferentes: 'o.semCampo' era reportado na linha
        certa e 'o.semMetodo()' em '0:0' — sem linha, sem coluna e sem o
        trecho desenhado, para record E para blueprint. Num arquivo de
        200 linhas a segunda forma nao diz onde.
        """
        try:
            return self._chamar_metodo_cru(obj, args, kwargs, node, env)
        except DataForgeError as erro:
            if not erro.line:
                erro.line, erro.column = node.line, node.column
                erro.span = len(str(node.method))
                erro.args = (erro.format(),)
            raise

    def _chamar_metodo_cru(self, obj, args, kwargs, node, env):
        """A chamada em si. Separada de 'eval_MethodCall' pelo mesmo
        motivo que '_comparar': o compilador de closures avalia as partes
        pelos fechamentos que ja montou, e so entao pergunta o resultado.
        Chamar 'eval_MethodCall' o faria percorrer a arvore de novo.
        """
        # A chamada de metodo numa instancia vem PRIMEIRO: e o caso comum
        # de todo codigo orientado a objeto, e chegava aqui depois de tres
        # testes que nunca casam com ela (proxy, record, modulo). Os tipos
        # sao disjuntos, entao a ordem nao muda o resultado.
        if type(obj) is DFInstance:
            nome = node.method
            if nome in obj.blueprint.nao_publicos:
                self._conferir_acesso(obj.blueprint, nome, env, node)
            # 'on_read' e leitura de CAMPO: a busca do metodo para chama-lo
            # nao passa por ele, senao todo 'obj.f()' seria tambem uma
            # leitura de 'f' no registro de quem audita.
            if obj.blueprint.leitura_magica:
                method = self._ler_da_instancia(obj, nome, node, env)
            else:
                try:
                    method = obj.get(nome)
                except NameError_:
                    method = self._membro_ausente(obj, nome, node, env)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj)
            if isinstance(method, DFInstance):
                return self._call(method, args, kwargs, node, env)
            if callable(method):
                return self._invocar(method, args, kwargs, node, node.method)

        # Handle root (super) proxy calls
        if isinstance(obj, _RootProxy):
            method = obj.get(node.method)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj.instance)
            if callable(method):
                return self._invocar(method, args, kwargs, node, node.method)

        if isinstance(obj, DFRecordInstance):
            metodo = obj.get(node.method)
            if isinstance(metodo, DFAction):
                return self._call_action(metodo, args, kwargs, node, env, instance=obj)
            if callable(metodo):
                return self._invocar(metodo, args, kwargs, node, node.method)

        # Um modulo e um dict de nomes. 'M.Ponto(1, 2)' precisa construir
        # o record que esta sob 'Ponto' — sem isto, a chamada procurava
        # um metodo de dict com esse nome e falhava.
        #
        # So records entram aqui: blueprint se constroi com 'spawn', que
        # avalia 'M.Caixa' como valor e faz o resto sozinho; acao ja e
        # tratada mais abaixo, pelo caminho comum.
        if isinstance(obj, dict) and isinstance(obj.get(node.method), DFRecord):
            return self._call(obj[node.method], args, kwargs, node, env)

        if isinstance(obj, DFInstance):
            nome = node.method
            if nome in obj.blueprint.nao_publicos:
                self._conferir_acesso(obj.blueprint, nome, env, node)
            # 'on_read' e leitura de CAMPO: a busca do metodo para chama-lo
            # nao passa por ele, senao todo 'obj.f()' seria tambem uma
            # leitura de 'f' no registro de quem audita.
            if obj.blueprint.leitura_magica:
                method = self._ler_da_instancia(obj, nome, node, env)
            else:
                try:
                    method = obj.get(nome)
                except NameError_:
                    method = self._membro_ausente(obj, nome, node, env)
            if isinstance(method, DFAction):
                return self._call_action(method, args, kwargs, node, env, instance=obj)
            if isinstance(method, DFInstance):
                return self._call(method, args, kwargs, node, env)
            if callable(method):
                return self._invocar(method, args, kwargs, node, node.method)
        elif isinstance(obj, DFBlueprint):
            if node.method in obj.methods:
                method = obj.methods[node.method]
                if node.method not in obj.static_methods:
                    # Sem instancia, 'self' fica solto e o erro sai la dentro,
                    # longe da causa. Melhor recusar aqui, dizendo o que fazer.
                    raise TypeError_(
                        f"'{obj.name}.{node.method}()' is an instance method "
                        f"and needs an object.\n"
                        f"    Spawn one first:\n"
                        f"        obj := spawn {obj.name}(…)\n"
                        f"        obj.{node.method}(…)\n"
                        f"    Or declare it as "
                        f"'static action {node.method}(…)' if it does not "
                        f"use 'self'.",
                        node.line, node.column)
                return self._call_action(method, args, kwargs, node, env)
            if node.method in obj.statics:
                val = obj.statics[node.method]
                if callable(val):
                    return self._invocar(val, args, kwargs, node, node.method)
                return val
        elif isinstance(obj, (BuiltinFunction,)):
            return self._invocar(obj, args, kwargs, node, node.method)
        elif hasattr(obj, '__call__'):
            # Um receptor que por acaso e chamavel NAO transforma
            # 'obj.metodo()' em 'obj()'. Era o que acontecia: o ramo
            # ignorava 'node.method' e invocava o proprio objeto.
            #
            # Aparece em qualquer objeto da biblioteca que defina
            # '__call__' por conveniencia. Medido em 'Arcane.Estrutura':
            # 'molde.mapa' devolvia a acao certa, e 'molde.mapa()'
            # devolvia um Bloco — porque chamava o molde. Nao havia erro
            # nenhum: o valor errado seguia adiante, e a queixa saia na
            # linha de baixo, sobre outra coisa.
            #
            # O recuo continua: sem o membro, o objeto e chamado como
            # antes, e nada que funcionava deixou de funcionar.
            metodo = getattr(obj, node.method, None)
            if callable(metodo):
                return self._invocar(metodo, args, kwargs, node, node.method)
            return self._invocar(obj, args, kwargs, node, node.method)

        # Try getting a builtin method.
        #
        # Com o objeto que JA foi avaliado — antes isto montava um no de
        # AST apontando para 'node.object' e mandava avalia-lo de novo.
        # Nao era so custo: 'dar_lista().count(1)' chamava 'dar_lista()'
        # DUAS vezes, e todo efeito colateral do objeto se repetia sem
        # que nada denunciasse.
        member = self._ler_membro(obj, node, env, membro=node.method)
        if callable(member):
            return self._invocar(member, args, kwargs, node, node.method)

        if obj is None:
            raise NotCallableError(
                f"Cannot call '{node.method}': the value is Void.",
                node.line, node.column,
                nota="something before this returned 'void'",
                dica=f"use  ?.  to stop safely:  x?.{node.method}(…)",
                doc="operadores")
        raise NotCallableError(
            f"Cannot call method '{node.method}' on "
            f"{self._nome_do_tipo(obj)}.",
            node.line, node.column)

    @staticmethod
    def _copiar_padrao(valor):
        """Uma copia rasa do padrao, quando ele for mutavel.

        Rasa e o suficiente: o caso real e '[]' e '{}' na declaracao do
        campo. Copia profunda seria cara e surpreendente — quem poe uma
        estrutura aninhada como padrao provavelmente quer compartilha-la.
        """
        if isinstance(valor, (list, dict, set)):
            # 'copy' e o da classe: a colecao tipada devolve outra tipada,
            # e cada instancia ganha a sua com a mesma guarda
            return valor.copy() if type(valor) not in (list, dict, set) \
                else type(valor)(valor)
        return valor

    def eval_SpawnExpression(self, node: ast.SpawnExpression, env):
        blueprint = self.evaluate(node.class_name, env)
        if not isinstance(blueprint, DFBlueprint):
            nome = getattr(node.class_name, 'name', None) or self._to_str(blueprint)
            raise TypeError_(
                f"'{nome}' is not a blueprint, so it cannot be spawned.\n"
                f"    'spawn' builds an object from a blueprint; "
                f"'{nome}' is {self._nome_do_tipo(blueprint)}.",
                node.line, node.column)
        args = self._eval_args(node.args, env)
        kwargs = {k: self.evaluate(v, env) for k, v in node.kwargs.items()}
        return self._instanciar(blueprint, args, kwargs, node, env)

    #: Os nomes do construtor, na ordem em que sao procurados.
    CONSTRUTORES = ("setup", "initiate", "__init__")

    def _instanciar(self, blueprint, args, kwargs, node, env):
        """Constroi uma instancia. O UNICO caminho — 'spawn', 'Nome(…)', DI.

        Eram dois, e divergiam: chamar o blueprint como funcao nao copiava
        o padrao dos campos declarados, e um 'Nome()' nascia com campos que
        o 'spawn Nome()' tinha. Um caminho so e o que impede a proxima
        divergencia.
        """
        if blueprint.e_contrato:
            raise AbstractInstantiationError(
                f"'{blueprint.name}' is a contract and cannot be spawned.",
                node.line, node.column,
                nota="a contract only declares what a blueprint promises",
                dica=f"spawn a blueprint declared  with {blueprint.name}",
                doc="oop/contratos")
        if blueprint.is_abstract:
            faltando = blueprint.pendencias_abstratas()
            detalhe = ""
            if faltando:
                itens = ", ".join(f"{n}()" for n in sorted(faltando))
                detalhe = f"\n    It still misses: {itens}"
            raise TypeError_(
                f"'{blueprint.name}' is an abstract blueprint and cannot be "
                f"spawned directly.{detalhe}\n"
                f"    Spawn a blueprint that extends it instead.",
                node.line, node.column)

        vigias = blueprint.vigias
        if vigias is not None and "on_spawn" in vigias.ganchos:
            entregue = self._gancho_de_vigia(vigias, "on_spawn",
                                             [blueprint, list(args)], node)
            if entregue is not None and entregue is not _SEM_MAGICO:
                return entregue

        # '__new__' decide antes de existir objeto: devolver um pronto (o
        # unico, o do cache, o do pool) dispensa a construcao.
        criador = blueprint.methods.get("__new__")
        if isinstance(criador, DFAction):
            pronto = self._call_action(criador, list(args), dict(kwargs), node, env)
            if pronto is not None:
                return pronto

        classe = DFInstanceFinal if blueprint.finalizador is not None else DFInstance
        instance = classe(blueprint)
        estado = None
        if blueprint.somente_leitura or vigias is not None:
            estado = objetos.estado_de(instance)
            estado.construindo = True
        try:
            self._construir(instance, blueprint, args, kwargs, node, env)
        finally:
            if estado is not None:
                estado.construindo = False

        if vigias is not None:
            if vigias.invariantes:
                self._conferir_invariantes(instance, node)
            if "on_ready" in vigias.ganchos:
                self._gancho_de_vigia(vigias, "on_ready", [instance], node)
        return instance

    def _construir(self, instance, blueprint, args, kwargs, node, env):
        # Campos declarados no corpo comecam com o padrao (ou void).
        #
        # O padrao e COPIADO quando for mutavel: 'itens: Cluster := []'
        # avalia o literal uma vez, na declaracao do blueprint, e sem a
        # copia todas as instancias compartilhariam a mesma lista — o
        # 'a.itens.append(1)' de uma apareceria em todas as outras. E a
        # armadilha do argumento mutavel padrao do Python, e aqui ela
        # nao tem justificativa nenhuma.
        descritores = blueprint.descritores
        for nome_campo, _tipo, padrao, _visib in blueprint.fields_decl:
            if descritores and nome_campo in descritores:
                continue
            self._gravar_campo_cru(instance, nome_campo, self._copiar_padrao(padrao))

        parametros = blueprint.constructor_params
        construtor = blueprint.construtor
        valores = {}
        if parametros:
            valores = self._ligar_cabecalho(blueprint, args, kwargs, node,
                                            construtor is not None)
            for param in parametros:
                self._gravar_campo_cru(instance, param, valores[param])
            if construtor is not None:
                # o construtor ainda roda: um blueprint pode declarar
                # parametros e ainda inicializar campos derivados
                self._call_action(construtor, args,
                                  {k: v for k, v in kwargs.items()
                                   if k in construtor.params},
                                  node, env, instance=instance)

        # O corpo do construtor roda SEMPRE que existir — inclusive num
        # blueprint sem parametros.
        #
        # Isto estava dentro do 'if blueprint.constructor_params', e a
        # consequencia era silenciosa: num 'blueprint Forma:' o
        # 'self.tipo := "forma"' nao ia para lugar nenhum. A linha
        # existia, estava certa, e nao fazia nada.
        if blueprint.constructor_body:
            ctor_env = blueprint.env.child(f"<{blueprint.name}.__init__>")
            ctor_env.set_local("this", instance)
            ctor_env.set_local("self", instance)
            for param in parametros:
                ctor_env.set_local(param, valores.get(param))
            try:
                self.exec_block(blueprint.constructor_body, ctor_env)
            except YieldSignal:
                pass  # construtor nao devolve; se devolver, ignoramos

        if not parametros and construtor is not None:
            self._call_action(construtor, args, kwargs, node, env, instance=instance)

    def _ligar_cabecalho(self, blueprint, args, kwargs, node, tem_construtor):
        """Os parametros do cabecalho: posicao, nome, padrao e tipo."""
        parametros = blueprint.constructor_params
        if len(args) > len(parametros) and not tem_construtor:
            raise ArityError(
                f"'{blueprint.name}' takes {len(parametros)} argument(s) but "
                f"{len(args)} were given.",
                node.line, node.column,
                nota=f"the header declares ({', '.join(parametros)})",
                doc="oop/blueprints")
        valores = {}
        tipos = blueprint.tipos_do_cabecalho
        padroes = blueprint.padroes_do_cabecalho
        for i, param in enumerate(parametros):
            if i < len(args):
                valor = args[i]
            elif param in kwargs:
                valor = kwargs[param]
            elif param in padroes:
                valor = self._copiar_padrao(self.evaluate(padroes[param], blueprint.env))
            else:
                valor = None
            if tipos and param in tipos:
                self._check_type(valor, tipos[param],
                                 f"parameter '{param}' of '{blueprint.name}'", node,
                                 getattr(blueprint, "type_params", ()),
                                 getattr(blueprint, "type_bounds", None))
            valores[param] = valor
        return valores

    @staticmethod
    def _gravar_campo_cru(instance, nome, valor):
        """Escreve sem passar por visibilidade, readonly nem gancho.

        E a escrita da CONSTRUCAO: o padrao de um campo 'private
        readonly' precisa chegar la, e nenhuma das regras de fora vale
        para o proprio blueprint montando o objeto.
        """
        try:
            instance.set(nome, valor)
        except UndefinedMemberError:
            # um campo declarado fora dos 'slots': a declaracao do campo e
            # a dos slots discordam, e o erro certo aparece na primeira
            # leitura, com a lista de slots na mensagem
            pass

    def eval_TypeofExpression(self, node: ast.TypeofExpression, env):
        """typeof x — o nome DataForge do tipo, igual ao usado nas anotações."""
        return self._type_of(self.evaluate(node.operand, env))

    def eval_CastExpression(self, node: ast.CastExpression, env):
        value = self.evaluate(node.operand, env)
        target = node.target_type
        cast_map = {
            "Integer": int, "int": int,
            "Float": float, "float": float,
            "String": str, "str": str,
            "Boolean": bool, "bool": bool,
            "Cluster": list, "list": list,
        }
        if target in cast_map:
            try:
                return cast_map[target](value)
            except (ValueError, TypeError) as e:
                raise TypeError_(f"Cannot cast to {target}: {e}", node.line, node.column)
        raise TypeError_(f"Unknown cast target: {target}", node.line, node.column)

    def eval_PipelineExpression(self, node: ast.PipelineExpression, env):
        data = self.evaluate(node.source, env)

        # Um verbo de quadro trabalha sobre o QUADRO, e nao sobre a lista
        # de linhas: 'agrupar' precisa das colunas, e converter para
        # cluster aqui perderia exatamente isso. Os verbos e o
        # 'sift/morph/distill' convivem no mesmo pipeline porque a
        # conversao virou preguicosa — cada estagio pede a forma de que
        # precisa, na hora em que precisa.
        tem_verbo = any(isinstance(o, ast.QuadroOperation)
                        for o in node.operations)
        if not tem_verbo:
            # Um objeto que declara '__iter__' e fonte legitima, como no
            # 'cycle' e na compreensao. Sem isto o pipeline era o unico
            # dos tres que recusava, com uma mensagem que nomeia a classe
            # interna do interpretador ("'DFInstance' object is not
            # iterable") — uma palavra que quem escreve nunca viu.
            data = self._percorrer(data, node)
            self._conferir_fonte_do_pipeline(data, node)

        for op in node.operations:
            if isinstance(op, ast.QuadroOperation):
                data = self._verbo_de_quadro(op, data, env)
            elif isinstance(op, ast.SiftOperation):
                if op.func_ref:
                    # Named function reference: sift func_name
                    func = env.get(op.func_ref)
                    data = [item for item in data if self._call_func(func, [item], op, env)]
                else:
                    data = [item for item in data if self._eval_lambda(op.param, op.condition, item, env)]
            elif isinstance(op, ast.MorphOperation):
                if op.func_ref:
                    # Named function reference: morph func_name
                    func = env.get(op.func_ref)
                    data = [self._call_func(func, [item], op, env) for item in data]
                else:
                    data = [self._eval_lambda(op.param, op.expression, item, env) for item in data]
            elif isinstance(op, ast.DistillOperation):
                if op.func_ref:
                    # Named function reference: distill func_name initial_value
                    func = env.get(op.func_ref)
                    acc = self.evaluate(op.initial, env) if op.initial else data[0]
                    start = 0 if op.initial is not None else 1
                    for item in data[start:]:
                        acc = self._call_func(func, [acc, item], op, env)
                    data = acc
                else:
                    acc = self.evaluate(op.initial, env) if op.initial else data[0]
                    start = 0 if op.initial else 1
                    for item in data[start:]:
                        local = env.child("<distill>")
                        local.set_local(op.acc_param, acc)
                        local.set_local(op.val_param, item)
                        acc = self.evaluate(op.expression, local)
                    data = acc
        return data

    # ── os verbos de quadro ─────────────────────────────────

    def _verbo_de_quadro(self, op, valor, env):
        """`>> onde …`, `>> pegar …`, `>> agrupar …` e os outros tres.

        A fonte pode ser um quadro OU um cluster de vaults: o segundo e o
        que sai de 'IO.read_csv(c, yes)' e de 'Database.query', e obrigar
        a converter na mao faria o verbo valer menos justamente onde o
        dado entra.
        """
        from .stdlib.arcane_quadro import Grupo, Quadro

        # 'resumir' e o UNICO que aceita um agrupamento — ele e o passo
        # que fecha o 'agrupar'. Converter antes de olhar o verbo
        # recusava justamente o par que o documento pede.
        if op.verbo == "resumir":
            pedido = self.evaluate(op.expressao, env)
            alvo = valor if isinstance(valor, Grupo) \
                else self._como_quadro(valor, op)
            return alvo.resumir(pedido)

        quadro = self._como_quadro(valor, op)

        if op.verbo == "onde":
            return quadro.onde(
                lambda linha: self._testar_na_linha(op.expressao, linha, env))
        if op.verbo == "pegar":
            return quadro.pegar(*op.colunas)
        if op.verbo == "sem":
            return quadro.sem(*op.colunas)
        if op.verbo == "ordenar":
            return quadro.ordenar(op.colunas, op.decrescente)
        if op.verbo == "agrupar":
            return quadro.agrupar(op.colunas)
        raise RuntimeError_(
            f"verbo de quadro desconhecido: '{op.verbo}'",
            getattr(op, "line", 0), getattr(op, "column", 0),
            doc="dados/quadro")

    def _como_quadro(self, valor, op):
        """O valor como quadro — aceitando o cluster de vaults."""
        from .stdlib.arcane_quadro import Grupo, Quadro

        if isinstance(valor, Quadro):
            return valor
        if isinstance(valor, Grupo):
            # 'agrupar' seguido de algo que nao e 'resumir' nao tem
            # leitura: o grupo nao tem forma retangular ate agregar.
            raise RuntimeError_(
                f"'{op.verbo}' não se aplica a um agrupamento",
                getattr(op, "line", 0), getattr(op, "column", 0),
                nota="depois de 'agrupar' vem 'resumir'",
                dica='… >> agrupar cidade >> resumir {"valor": "soma"}',
                doc="dados/quadro")
        if isinstance(valor, list) and all(isinstance(x, dict) for x in valor):
            return Quadro.de_vaults(valor)
        raise RuntimeError_(
            f"'{op.verbo}' precisa de um quadro",
            getattr(op, "line", 0), getattr(op, "column", 0),
            nota=f"recebi {self._nome_do_tipo(valor)}",
            dica="use Quadro.de_vaults(linhas), ou um cluster de vaults",
            doc="dados/quadro")

    def _testar_na_linha(self, expressao, linha, env):
        """Avalia a expressão de um `onde` com as COLUNAS em escopo.

        É o que faz `>> onde valor bigger 50` ler como se lê. A coluna
        vence um nome de fora com o mesmo nome — dentro de um `onde`, um
        nome nu é uma coluna, e essa é a regra do verbo. O escopo de fora
        continua alcançável para tudo o que não for coluna: um limite
        guardado numa variável funciona em `onde valor bigger limite`.
        """
        local = env.child("<onde>")
        for coluna, valor in linha.items():
            local.set_local(str(coluna), valor)
        try:
            return self._verdade(self.evaluate(expressao, local))
        except TypeError_ as erro:
            # Comparar com o DESCONHECIDO nao da nem sim nem nao, e a
            # linha nao passa — e a logica de tres valores do SQL, e a
            # de toda ferramenta de dados que existe.
            #
            # Levantar aqui seria a outra escolha defensavel, e ela torna
            # o verbo inutil: todo conjunto real tem ausencia, e o
            # primeiro 'onde' de todo programa morreria na primeira
            # linha vazia. Quem QUER contar a ausencia escreve
            # 'onde valor is void'.
            #
            # So esta falha e engolida. Uma coluna que nao existe, uma
            # acao que quebra, uma divisao por zero — tudo o mais sobe.
            if getattr(erro, "ordem_sem_resposta", False):
                return False
            raise

    def _call_func(self, func, args, node, env=None):
        """Chama a acao nomeada de um estagio do pipeline: 'morph dobrar'.

        Era um caminho PARALELO a chamada normal: montava o escopo, rodava
        o corpo pela arvore e devolvia. Sem conferir aridade, sem conferir
        o tipo dos parametros nem o do retorno, sem empilhar quadro — e
        sem o corpo compilado. Medido:

            action dobrar(n: Integer) -> Integer: ...
            dobrar("x")                     recusado: declared as Integer
            ["x", "y"] >> morph dobrar      [xx, yy], calado

        e uma acao de dois parametros num 'morph' dizia "'b' is not
        defined" em vez de nomear a aridade. A mesma acao respondia duas
        coisas conforme fosse chamada com parenteses ou por um '>>'.
        """
        if isinstance(func, DFAction):
            return self._call_action(func, list(args), {}, node,
                                     env if env is not None else func.closure)
        if callable(func):
            return func(*args)
        raise TypeError_("Value is not callable in a pipeline stage", node.line, node.column)

    def eval_AwaitExpression(self, node: ast.AwaitExpression, env):
        """Espera o trabalho terminar e entrega o resultado.

        Aceita quatro coisas, e a terceira e a que faz 'async' valer a
        pena:

          - uma tarefa, o resultado de chamar uma acao 'async';
          - uma corrotina do Python, vinda da biblioteca padrao;
          - um cluster de tarefas, aguardadas TODAS ao mesmo tempo —
            elas ja estao correndo desde a chamada, entao o custo e o da
            mais lenta, e nao a soma;
          - qualquer outro valor, devolvido como esta. Aguardar o que ja
            esta pronto e legitimo: e o que permite trocar uma acao
            'async' por uma comum sem mexer em quem chama.

        O erro de dentro da tarefa e relevantado aqui, na linha do
        'await', que e onde quem escreveu pode fazer algo a respeito —
        e por isso 'monitor'/'handle' em volta de um 'await' pega o
        'trigger' que aconteceu na outra thread.
        """
        result = self.evaluate(node.expression, env)
        return self._aguardar(result)

    def _aguardar(self, valor):
        if isinstance(valor, DFTarefa):
            return valor.aguardar()

        if isinstance(valor, list) and any(
                isinstance(item, DFTarefa) for item in valor):
            return [self._aguardar(item) for item in valor]

        if asyncio.iscoroutine(valor):
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(valor)
            finally:
                loop.close()

        return valor

    def eval_InExpression(self, node: ast.InExpression, env):
        prompt = ""
        if node.prompt:
            prompt = self.evaluate(node.prompt, env)
        return input(self._to_str(prompt))

    # ═══════════════════════════════════════════════════════
    #  frame / train / predict
    # ═══════════════════════════════════════════════════════
    #
    #  As tres devolviam um vault com '__type__' e nada acontecia — tres
    #  palavras reservadas que PARECIAM implementadas. Eram o pior tipo
    #  de lacuna, porque quem lia a gramatica nao tinha como saber.
    #
    #  E a tabela e os algoritmos ja existiam, um modulo ao lado:
    #  'Arcane.Analytics' tem um Frame com 25 metodos, e 'Arcane.Cortex'
    #  tem 25 algoritmos de verdade. As palavras nao precisavam ser
    #  implementadas — precisavam ser LIGADAS.
    #
    #  Elas continuam sendo acucar fino, e isso e deliberado: quem
    #  precisa de controle chama 'Cortex.floresta(...)' direto, e ve
    #  todos os parametros.

    def eval_FrameExpression(self, node: ast.FrameExpression, env):
        """'frame <dados>' — uma tabela de verdade, do Arcane.Analytics.

        Aceita as tres formas em que dado tabular aparece na linguagem:

            frame [{"a": 1}, {"a": 2}]      registros (o que o CSV e o
                                            banco devolvem)
            frame {"a": [1, 2], "b": [3, 4]}  colunas
            frame [[1, 2], [3, 4]]          matriz, com colunas
                                            geradas
        """
        from .stdlib import get_module
        analytics = get_module("Arcane.Analytics")
        dados = self.evaluate(node.data, env)

        if isinstance(dados, list) and dados and isinstance(dados[0], dict):
            return analytics["from_records"](dados)

        if isinstance(dados, dict):
            return analytics["from_dict"](dados)

        if isinstance(dados, list):
            colunas = list(node.columns) if node.columns else None
            return analytics["create_frame"](dados, colunas)

        raise TypeError_(
            f"'frame' precisa de registros, colunas ou uma matriz — "
            f"veio {self._nome_do_tipo(dados)}.",
            node.line, node.column,
            dica='frame [{"a": 1}, {"a": 2}]      registros\n'
                 'frame {"a": [1, 2]}             colunas\n'
                 'frame [[1, 2], [3, 4]]          matriz',
            doc="tecnicas/ml")

    @staticmethod
    def _registros_de(valor):
        """Um Frame ou um cluster de vaults, sempre como registros."""
        if hasattr(valor, "to_dict") and hasattr(valor, "columns"):
            return valor.to_dict()
        return valor

    def eval_TrainExpression(self, node: ast.TrainExpression, env):
        """'train <algoritmo> using <config>' — treina de verdade.

        O algoritmo e o nome de um treinador do 'Arcane.Cortex', ou uma
        acao sua. A configuracao e um vault com os argumentos dele — o
        que mantem a palavra fina o bastante para nao esconder nada:

            modelo := train "floresta" using {
                "linhas": treino,
                "alvo": "especie",
                "colunas": ["largura", "altura"],
                "arvores": 50
            }
        """
        from .stdlib import get_module
        algoritmo = self.evaluate(node.model, env)
        config = self.evaluate(node.data, env)

        if not isinstance(config, dict):
            raise TypeError_(
                f"'train … using' precisa de um vault com os argumentos, "
                f"e veio {self._nome_do_tipo(config)}.",
                node.line, node.column,
                dica='train "linear" using {"linhas": dados, '
                     '"alvo": "preco", "colunas": ["area"]}',
                doc="tecnicas/ml")

        config = dict(config)
        if "linhas" in config:
            config["linhas"] = self._registros_de(config["linhas"])

        treinador = algoritmo
        if isinstance(algoritmo, str):
            cortex = get_module("Arcane.Cortex")
            from .stdlib.arcane_cortex import TREINADORES
            treinador = cortex.get(algoritmo) if algoritmo in TREINADORES \
                else None
            if not callable(treinador):
                import difflib
                perto = difflib.get_close_matches(
                    algoritmo, TREINADORES, n=2, cutoff=0.6)
                dica = (f"voce quis dizer "
                        f"{' ou '.join(repr(p) for p in perto)}?"
                        if perto else
                        f"os que treinam: {', '.join(TREINADORES)}")
                raise NameError_(
                    f"'{algoritmo}' nao e um algoritmo de treino do "
                    f"Arcane.Cortex.",
                    node.line, node.column,
                    nota=f"os que treinam: {', '.join(TREINADORES)}"
                         if perto else "",
                    dica=dica,
                    doc="tecnicas/ml")

        if not callable(treinador):
            raise TypeError_(
                f"'train' precisa do nome de um algoritmo ou de uma acao, "
                f"e veio {self._nome_do_tipo(algoritmo)}.",
                node.line, node.column,
                dica='train "linear" using {…}   ou   train minha_acao using {…}',
                doc="tecnicas/ml")

        return self._invocar(treinador, [], config, node, "train")

    def eval_PredictExpression(self, node: ast.PredictExpression, env):
        """'predict <modelo> using <linhas>' — prediz de verdade.

        Um modelo do Cortex vai por 'Cortex.prever'. Uma acao sua e
        chamada com os dados — assim a palavra serve tambem a quem
        escreveu o proprio modelo.
        """
        from .stdlib import get_module
        modelo = self.evaluate(node.model, env)
        dados = self._registros_de(self.evaluate(node.data, env))

        if callable(modelo):
            return self._invocar(modelo, [dados], {}, node, "predict")

        # Um modelo do Cortex se reconhece por 'especie' — e o campo que
        # o proprio 'prever' consulta para escolher como prever.
        if hasattr(modelo, "especie"):
            return get_module("Arcane.Cortex")["prever"](modelo, dados)

        raise TypeError_(
            f"'predict' precisa de um modelo treinado ou de uma acao, "
            f"e veio {self._nome_do_tipo(modelo)}.",
            node.line, node.column,
            nota="um modelo treinado sai de 'train … using …' ou de "
                 "'Arcane.Cortex'",
            doc="tecnicas/ml")

    # ═══════════════════════════════════════════════════════
    #  STATEMENT EXECUTION
    # ═══════════════════════════════════════════════════════

    def exec_OutStatement(self, node: ast.OutStatement, env):
        values = [self._to_str(self.evaluate(expr, env)) for expr in node.expressions]
        print(' '.join(values))

    def exec_EmitStatement(self, node, env):
        """Fora de um 'stream action', 'emit' é um alias histórico de 'out'.

        Dentro do corpo de um stream ele é interceptado por _lazy_stmt e produz
        um valor em vez de imprimir.
        """
        valores = [self.evaluate(e, env) for e in node.expressions]
        print(' '.join(self._to_str(v) for v in valores))
        return None


    # ═══════════════════════════════════════════════════════
    #  Kiln — framework web
    # ═══════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════
    #  Crucible — o framework de testes
    # ═══════════════════════════════════════════════════════

    def exec_CrucibleBlock(self, node: ast.CrucibleBlock, env):
        """crucible "<nome>": corpo — abre uma suite e a preenche.

        O corpo roda UMA vez, na declaracao, e o que ele faz e
        registrar: 'trial' guarda um corpo para depois, 'setup' guarda
        um gancho. Nada e executado agora — quem executa e o
        'Crucible.run()', ou o 'dataforge crucible'.

        Essa separacao e a mesma de 'server' e 'ignite', e pelo mesmo
        motivo: um arquivo importado nao pode sair rodando a suite
        inteira so por ter sido lido.
        """
        from .stdlib.crucible import REGISTRO

        nome = self.evaluate(node.name, env)
        suite = REGISTRO.abrir_suite(self._to_str(nome))
        suite.tags = [self._to_str(self.evaluate(t, env)) for t in node.tags]
        if node.pending is not None:
            suite.pendente = self._to_str(self.evaluate(node.pending, env))

        interno = Environment(parent=env, name=f"<crucible {nome}>")
        interno.set_local("__crucible_suite__", suite)

        # O quadro do trial: um escopo filho, refeito antes de cada
        # trial. O 'setup' escreve nele e o corpo do trial le dali —
        # e como um le o que o outro preparou sem que o valor sobreviva
        # ao trial seguinte.
        def abrir_quadro():
            suite.quadro = Environment(parent=interno, name=f"<quadro {nome}>")
            return suite.quadro

        suite.abrir_quadro = abrir_quadro
        abrir_quadro()

        try:
            for stmt in node.body:
                self.execute(stmt, interno)
        finally:
            REGISTRO.fechar_suite()
        return suite

    def _suite_do_escopo(self, env, node, palavra):
        from .stdlib.crucible import REGISTRO
        try:
            return env.get("__crucible_suite__")
        except Exception:
            if REGISTRO.atual is not REGISTRO.raiz:
                return REGISTRO.atual
            raise RuntimeError_(
                f"'{palavra}' only works inside a 'crucible' block.",
                node.line, node.column,
                dica=('open one first:\n'
                      '    crucible "o que voce testa":\n'
                      f'        {palavra} …'),
                doc="crucible")

    def exec_TrialBlock(self, node: ast.TrialBlock, env):
        """trial "<nome>" [modificadores]: corpo"""
        from .stdlib.crucible import Trial

        suite = self._suite_do_escopo(env, node, "trial")
        nome = self._to_str(self.evaluate(node.name, env))
        tags = [self._to_str(self.evaluate(t, env)) for t in node.tags]
        pendente = ("" if node.pending is None
                    else self._to_str(self.evaluate(node.pending, env)))
        repetir = 1 if node.repeat is None else int(self.evaluate(node.repeat, env))
        prazo = 0 if node.within is None else float(self.evaluate(node.within, env))
        dados = None if node.over is None else list(self.evaluate(node.over, env))

        corpo_node = node.body
        arquivo = self.filename

        def corpo(caso=None):
            """Roda no quadro da suite, que o executor acabou de refazer.

            Escrever direto no quadro, e nao num filho dele, e o que
            permite 'contador := contador + 1' funcionar como se
            espera — e nao vazar, porque o quadro nasce de novo a cada
            trial.
            """
            escopo = suite.quadro or Environment(parent=env,
                                                 name=f"<trial {nome}>")
            if caso is not None:
                escopo.set_local("caso", caso)
            for stmt in corpo_node:
                self.execute(stmt, escopo)

        suite.trials.append(Trial(
            nome, corpo, tags, pendente=pendente, focado=node.focused,
            repetir=repetir, prazo=prazo, arquivo=arquivo, linha=node.line,
            dados=dados))
        return nome

    def exec_HookBlock(self, node: ast.HookBlock, env):
        """setup: / teardown: / setup all: / teardown all:"""
        suite = self._suite_do_escopo(env, node, node.kind)
        corpo_node = node.body

        def gancho(alvo=None):
            # Escreve NO quadro do trial, nao num escopo proprio: o que
            # o 'setup' declara precisa chegar ao corpo do trial, e e
            # exatamente para isso que ele existe.
            escopo = (alvo.quadro if alvo is not None and alvo.quadro
                      else suite.quadro)
            if escopo is None:
                escopo = Environment(parent=env, name=f"<{node.kind}>")
            for stmt in corpo_node:
                self.execute(stmt, escopo)
            return dict(escopo.variables)

        if node.kind == "setup":
            (suite.antes_de_cada if node.every else suite.antes_de_tudo).append(gancho)
        else:
            (suite.depois_de_cada if node.every else suite.depois_de_tudo).append(gancho)
        return None

    def exec_FixtureBlock(self, node: ast.FixtureBlock, env):
        """fixture <nome>(): corpo — preparo e limpeza em um lugar so.

        O 'provide' divide o corpo em duas metades: o que vem antes
        prepara, o que vem depois limpa. Escrever as duas juntas e o
        que impede a limpeza de ser esquecida — que e o modo mais comum
        de uma suite passar a depender da ordem.
        """
        suite = self._suite_do_escopo(env, node, "fixture")
        corpo_node = node.body
        interpretador = self

        def montar():
            """Prepara, registra a limpeza, e devolve o valor.

            Devolver o VALOR — e nao um par (valor, limpeza) — e o que
            faz 'db := banco()' funcionar como quem escreve espera. A
            limpeza vai para a suite, que a executa no fim do trial;
            devolve-la junto obrigaria todo teste a desempacotar um
            par e a lembrar de chamar a segunda metade, que e
            exatamente o esquecimento que a fixture existe para
            impedir.
            """
            escopo = Environment(parent=env, name=f"<fixture {node.name}>")
            entregue = []
            resto = []
            for i, stmt in enumerate(corpo_node):
                if isinstance(stmt, ast.ProvideStatement):
                    entregue.append(interpretador.evaluate(stmt.value, escopo)
                                    if stmt.value is not None else None)
                    resto = corpo_node[i + 1:]
                    break
                interpretador.execute(stmt, escopo)

            if resto:
                def limpar():
                    for stmt in resto:
                        interpretador.execute(stmt, escopo)

                suite.limpezas.append(limpar)

            return entregue[0] if entregue else None

        suite.fixtures[node.name] = montar
        env.set(node.name, montar)
        return node.name

    def exec_ProvideStatement(self, node: ast.ProvideStatement, env):
        """provide <valor> — so tem sentido dentro de uma fixture."""
        raise RuntimeError_(
            "'provide' only works inside a 'fixture' block.",
            node.line, node.column,
            dica=("it splits the fixture in two: what comes before "
                  "prepares, what comes after cleans up"),
            doc="crucible")

    def exec_ExpectStatement(self, node: ast.ExpectStatement, env):
        """expect <expr> <matcher> <arg> — a forma curta."""
        from .stdlib.crucible import Expectativa, FalhaDeExpectativa

        valor = self.evaluate(node.value, env)
        expectativa = Expectativa(valor)
        if node.negated:
            expectativa.nao()

        if not node.matcher:
            # 'expect <expr>' sozinho cobra que o valor seja verdadeiro.
            if bool(valor) == node.negated:
                raise FalhaDeExpectativa(
                    f"devia valer como verdadeiro, e veio "
                    f"{self._to_str(valor)}")
            return None

        args = [self.evaluate(a, env) for a in node.args]

        # 'to_not_be' nao existe como matcher: e 'to_be' negado.
        nome = node.matcher
        if nome.startswith("to_not_"):
            expectativa.nao()
            nome = "to_" + nome[len("to_not_"):]

        metodo = getattr(expectativa, nome, None)
        if metodo is None:
            disponiveis = sorted(
                m for m in dir(Expectativa) if m.startswith("to_"))
            import difflib
            perto = difflib.get_close_matches(nome, disponiveis, n=3, cutoff=0.5)
            raise RuntimeError_(
                f"'{nome}' is not a matcher.", node.line, node.column,
                nota=(f"did you mean: {', '.join(perto)}?" if perto else
                      f"there are {len(disponiveis)} matchers"),
                dica="dataforge crucible --matchers  lists them all",
                doc="crucible")
        metodo(*args)
        return None

    def exec_BenchBlock(self, node: ast.BenchBlock, env):
        """bench "<nome>" [times <n>]: corpo — mede em vez de cobrar."""
        from .stdlib.crucible import Trial

        suite = self._suite_do_escopo(env, node, "bench")
        nome = self._to_str(self.evaluate(node.name, env))
        vezes = 1000 if node.times is None else int(self.evaluate(node.times, env))
        corpo_node = node.body
        interpretador = self
        arquivo = self.filename

        def corpo(caso=None):
            from .stdlib.crucible import ArcaneCrucible
            escopo = suite.quadro or Environment(parent=env,
                                                 name=f"<bench {nome}>")

            def uma_volta():
                for stmt in corpo_node:
                    interpretador.execute(stmt, escopo)

            medida = ArcaneCrucible._benchmark(nome, uma_volta, vezes)
            print(f"    ⏱  {nome}: {medida['media_ms']:.4f}ms media, "
                  f"{medida['mediana_ms']:.4f}ms mediana, "
                  f"p95 {medida['p95_ms']:.4f}ms, "
                  f"{medida['ops_por_s']:.0f} ops/s")

        suite.trials.append(Trial(nome, corpo, ["bench"], arquivo=arquivo,
                                  linha=node.line))
        return nome

    def exec_ServerBlock(self, node: ast.ServerBlock, env):
        """server <nome> [on <porta>]: corpo

        Monta a aplicacao e liga ao nome. Nao sobe nada: quem acende o
        forno e 'ignite'. Separar as duas coisas e o que permite testar
        uma rota sem abrir socket.
        """
        from .stdlib.kiln import App

        app = App(node.name)
        if node.port is not None:
            app.config["porta"] = self.evaluate(node.port, env)
        if node.host is not None:
            app.config["host"] = self.evaluate(node.host, env)

        # O corpo enxerga o escopo de fora — as rotas costumam usar
        # dados e acoes declarados antes do 'server'.
        interno = Environment(parent=env, name=f"<server {node.name}>")
        interno.set_local("__kiln_app__", app)

        for stmt in node.body:
            self.execute(stmt, interno)

        env.set(node.name, app)
        return app

    def _app_do_escopo(self, env, node, palavra):
        try:
            return env.get("__kiln_app__")
        except Exception:
            raise RuntimeError_(
                f"'{palavra}' only works inside a 'server' block.",
                node.line, node.column,
                nota=f"'{palavra}' configures a server, so it needs one",
                dica=f"wrap it in 'server nome on 8080:' — or call the "
                     f"matching Kiln.* function directly",
                doc="kiln")

    def exec_RouteBlock(self, node: ast.RouteBlock, env):
        """route <VERBO> <caminho>: corpo"""
        app = self._app_do_escopo(env, node, "route")
        caminho = self.evaluate(node.path, env)
        fechamento = env

        def handler(req, _no=node, _env=fechamento):
            escopo = Environment(parent=_env, name=f"<{_no.method} {caminho}>")
            escopo.set_local("req", req)
            # Atalhos: quem escreve a rota quase sempre quer estes quatro,
            # e 'req["params"]["id"]' repetido cansa.
            escopo.set_local("params", req.get("params", {}))
            escopo.set_local("query", req.get("query", {}))
            escopo.set_local("body", req.get("body"))
            escopo.set_local("headers", req.get("headers", {}))
            escopo.set_local("session", req.get("session", {}))
            try:
                self.exec_block(_no.body, escopo)
            except YieldSignal as sinal:
                return sinal.value
            return None

        app.rota(node.method if node.method != "ANY" else "*", caminho, handler)
        return None

    def _sair_com(self, resposta):
        """Toda resposta encerra a rota — igual a 'yield' numa acao."""
        raise YieldSignal(resposta)

    def exec_RespondStatement(self, node: ast.RespondStatement, env):
        from .stdlib.kiln import ArcaneKiln, resposta as _resp

        status = self.evaluate(node.status, env) if node.status else 200
        valor = self.evaluate(node.value, env) if node.value is not None else None

        if node.kind == "json":
            self._sair_com(ArcaneKiln._json(valor, status))
        if node.kind == "html":
            self._sair_com(ArcaneKiln._html(self._to_str(valor), status))
        if node.kind == "text":
            self._sair_com(ArcaneKiln._text(self._to_str(valor), status))
        if node.kind == "file":
            self._sair_com(ArcaneKiln._file(self._to_str(valor)))

        # Sem tipo: 'respond 204' e so status; o resto se descobre pelo
        # valor (vault/cluster viram JSON, texto vira html ou plain).
        if valor is None:
            self._sair_com(ArcaneKiln._status(status))
        if isinstance(valor, dict) and valor.get("__kiln__"):
            valor["status"] = int(status) if node.status else valor["status"]
            self._sair_com(valor)
        if isinstance(valor, (dict, list)):
            self._sair_com(ArcaneKiln._json(valor, status))
        self._sair_com(_resp(self._to_str(valor), status))

    def exec_RenderStatement(self, node: ast.RenderStatement, env):
        from .stdlib.kiln import ArcaneKiln

        app = self._app_do_escopo(env, node, "render")
        nome = self._to_str(self.evaluate(node.template, env))
        dados = self.evaluate(node.data, env) if node.data else {}
        status = self.evaluate(node.status, env) if node.status else 200
        self._sair_com(ArcaneKiln._render(app, nome, dados, status))

    def exec_RedirectStatement(self, node: ast.RedirectStatement, env):
        from .stdlib.kiln import ArcaneKiln

        destino = self._to_str(self.evaluate(node.target, env))
        status = self.evaluate(node.status, env) if node.status else 302
        self._sair_com(ArcaneKiln._redirect(destino, status))

    def exec_MiddlewareStatement(self, node: ast.MiddlewareStatement, env):
        palavra = "after" if node.depois else "middleware"
        app = self._app_do_escopo(env, node, palavra)
        funcao = self.evaluate(node.value, env)

        if node.depois:
            app.apos(funcao)
            return None

        app.usar(funcao)
        # Um middleware de ENTRADA pode trazer a metade de SAIDA junto —
        # 'request_id' poe o id no estado e precisa devolve-lo no
        # cabecalho; 'idempotente' guarda a resposta que acabou de sair.
        # Sem isto, quem usa teria de escrever as duas linhas e lembrar
        # da ordem; esquecer a segunda deixa a primeira pela metade, em
        # silencio.
        saida = getattr(funcao, "depois", None)
        if callable(saida):
            app.apos(saida)
        return None

    def exec_MountStatement(self, node: ast.MountStatement, env):
        app = self._app_do_escopo(env, node, "mount")
        outro = self.evaluate(node.value, env)
        prefixo = self._to_str(self.evaluate(node.prefix, env))
        app.montar(prefixo, outro)
        return None

    def exec_AssetsStatement(self, node: ast.AssetsStatement, env):
        app = self._app_do_escopo(env, node, "assets")
        prefixo = self._to_str(self.evaluate(node.prefix, env))
        pasta = self._to_str(self.evaluate(node.folder, env))
        app.estaticos.append(("/" + prefixo.strip("/"), pasta))
        return None

    def exec_ViewsStatement(self, node: ast.ViewsStatement, env):
        app = self._app_do_escopo(env, node, "views")
        app.pasta_templates = self._to_str(self.evaluate(node.folder, env))
        return None

    def exec_IgniteStatement(self, node: ast.IgniteStatement, env):
        """ignite <server> [on <porta>] — bloqueia ate Ctrl-C."""
        from .stdlib.kiln import ArcaneKiln, App

        app = self.evaluate(node.target, env)
        if not isinstance(app, App):
            raise RuntimeError_(
                f"'ignite' expects a server, got {self._nome_do_tipo(app)}.",
                node.line, node.column,
                nota="only a name declared with 'server' can be ignited",
                dica="declare it first: server api on 8080: …",
                doc="kiln")

        porta = (self.evaluate(node.port, env) if node.port is not None
                 else app.config.get("porta", 8080))
        host = (self.evaluate(node.host, env) if node.host is not None
                else app.config.get("host", "127.0.0.1"))
        return ArcaneKiln._listen(app, porta, host)

    def exec_YieldStatement(self, node: ast.YieldStatement, env):
        nome = getattr(node, _MARCA_CAUDA, None)
        if nome is not None:
            salto = self._tentar_saltar(node, nome, env)
            if salto is not None:
                raise salto
        value = self.evaluate(node.value, env) if node.value else None
        raise YieldSignal(value)

    def _tentar_saltar(self, node, nome, env):
        """'yield f(...)' vira salto — se 'f' for mesmo esta acao.

        A analise marcou o no pelo NOME, e nome pode ser reapontado:
        'f := outra_coisa' dentro do corpo faria o salto reusar um
        quadro que nao e o dono da chamada. Por isso a marca nao basta,
        e confere-se a IDENTIDADE aqui, onde ela e conhecida.
        """
        atual = self._por_thread.acao
        if atual is None or atual.name != nome:
            return None

        chamada = node.value
        if isinstance(chamada, ast.MethodCall):
            # 'self.f(...)': o metodo tem de ser ESTE, e nao um de mesmo
            # nome herdado ou substituido no meio do caminho.
            if not env.has("self"):
                return None
            instancia = env.get("self")
            bp = getattr(instancia, "blueprint", None)
            if bp is None:
                return None
            achado = None
            for ancestral in bp.linhagem():
                if nome in ancestral.methods:
                    achado = ancestral.methods[nome]
                    break
            if achado is not atual:
                return None
        else:
            if not env.has(nome) or env.get(nome) is not atual:
                return None

        return ChamadaDeCauda(self._eval_args(chamada.args, env), {})

    def exec_HaltStatement(self, node: ast.HaltStatement, env):
        raise HaltSignal()

    def exec_SkipStatement(self, node: ast.SkipStatement, env):
        raise SkipSignal()

    def exec_TriggerStatement(self, node: ast.TriggerStatement, env):
        value = self.evaluate(node.value, env)
        erro = TriggerError(self._to_str(value), node.line, node.column)
        # O valor ORIGINAL viaja junto. Antes so a renderizacao dele
        # sobrevivia: 'trigger SaldoInsuficiente(100, 250)' chegava ao
        # 'handle' como o texto "SaldoInsuficiente(saldo: 100, ...)", e
        # quem tratava precisava extrair por regex o que o programa ja
        # tinha como dado.
        #
        # E a mensagem nao muda — quem so le 'e.message' nao percebe
        # diferenca, e quase todo 'trigger' do repositorio levanta um
        # texto, onde os dois sao o mesmo.
        erro.valor = value
        # E o NOME do tipo levantado vira o rotulo que 'handle' casa.
        #
        # '_error_matches' ja consultava 'tipo_usuario' — com a
        # docstring explicando que serve a 'trigger MinhaFalha(...)' —
        # e NADA no interpretador o escrevia. O ramo existia, estava
        # documentado, e era inalcancavel: quem levantava um record de
        # dominio (a forma que a trilha ensina) so podia captura-lo com
        # 'handle Error' e um 'match' sobre 'e.value', embora o
        # cabecalho do erro imprimisse o nome do record.
        erro.tipo_usuario = self._nome_levantado(value)
        # O erro que estava sendo TRATADO vira a causa deste. Sem isso,
        # 'handle Error as e: trigger "nao deu para carregar"' apagava o
        # original — e embrulhar erro e a norma, nao a excecao.
        em_tratamento = getattr(self, "_erro_em_tratamento", None)
        if em_tratamento is not None and em_tratamento is not erro:
            # O arquivo da causa precisa estar certo ANTES de desenhar:
            # sem ele o trecho sai de '<stdin>', e o desenho aponta uma
            # linha que nao e daquele arquivo.
            if not getattr(em_tratamento, "filename", "") or \
                    em_tratamento.filename == "<stdin>":
                em_tratamento.filename = self.filename
            erro.causa = em_tratamento
        raise erro

    def _repr_do_objeto(self, valor):
        """O '__repr__' declarado pelo objeto, ou None.

        Devolver None e o que deixa o embutido decidir: sem isso, um
        cluster de numeros passaria por aqui e voltaria como texto de
        instancia.
        """
        if not isinstance(valor, DFInstance):
            return None
        acao = self._achar_magico(valor, "__repr__")
        if not isinstance(acao, DFAction):
            return None
        return str(self._call_action(acao, [], {}, self._no_interno(), None,
                                     instance=valor))

    @staticmethod
    def _nome_levantado(valor):
        """O nome que 'handle' casa, quando o valor levantado tem um.

        So record, instancia e membro de enum tem: um texto nao nomeia
        nada, e devolver 'String' ali faria 'handle String' capturar
        todo 'trigger "..."' do programa.
        """
        if isinstance(valor, DFRecordInstance):
            return getattr(valor.record, "name", None)
        if isinstance(valor, DFInstance):
            return getattr(valor.blueprint, "name", None)
        enum = getattr(valor, "enum", None)
        if enum is not None:
            return getattr(enum, "name", None)
        return None

    def exec_DeleteStatement(self, node: ast.DeleteStatement, env):
        if isinstance(node.target, ast.Identifier):
            env.delete(node.target.name)
        elif isinstance(node.target, ast.IndexAccess):
            obj = self.evaluate(node.target.object, env)
            idx = self.evaluate(node.target.index, env)
            if isinstance(obj, DFInstance):
                if self._chamar_magico(obj, "__delitem__", [idx], node) is not _SEM_MAGICO:
                    return None
                raise NotIndexableError(
                    f"'{obj.blueprint.name}' does not support 'delete obj[…]'.",
                    node.line, node.column,
                    dica="declare  action __delitem__(chave):  in the blueprint",
                    doc="oop/magicos")
            del obj[idx]
        elif isinstance(node.target, ast.MemberAccess):
            obj = self.evaluate(node.target.object, env)
            membro = node.target.member
            if isinstance(obj, DFInstance):
                if self._chamar_magico(obj, "__delattr__", [membro], node) is not _SEM_MAGICO:
                    return None
                bp = obj.blueprint
                if bp.descritores and membro in bp.descritores and \
                        self._chamar_magico(bp.descritores[membro], "__delete__",
                                            [obj], node) is not _SEM_MAGICO:
                    return None
                if membro in bp.nao_publicos:
                    self._conferir_acesso(bp, membro, env, node.target)
                objetos.conferir_escrita(obj, membro, node.target) \
                    if (obj._estado is not None or bp.somente_leitura) else None
                if obj._indice is None and membro in obj._valores:
                    del obj._valores[membro]
                    return None
                if obj._indice is not None and membro in obj._indice:
                    obj._valores[obj._indice[membro]] = DFInstance._VAZIO
                    return None
                raise UndefinedMemberError(
                    f"'{bp.name}' has no field '{membro}' to delete.",
                    node.line, node.column, doc="oop")
            if isinstance(obj, dict):
                obj.pop(membro, None)
                return None
            raise RuntimeError_(f"Cannot delete a member of {self._nome_do_tipo(obj)}.",
                                node.line, node.column)
        else:
            raise RuntimeError_("Cannot delete this expression", node.line, node.column)

    def exec_AssertStatement(self, node: ast.AssertStatement, env):
        condition = self.evaluate(node.condition, env)
        if not condition:
            msg = "Assertion failed"
            if node.message:
                msg = self._to_str(self.evaluate(node.message, env))
            raise RuntimeError_(msg, node.line, node.column)

    def exec_WaitStatement(self, node: ast.WaitStatement, env):
        duration = self.evaluate(node.duration, env)
        time.sleep(duration / 1000.0)  # milliseconds

    def exec_InspectStatement(self, node: ast.InspectStatement, env):
        value = self.evaluate(node.expression, env)
        type_name = self.eval_TypeofExpression(
            ast.TypeofExpression(operand=node.expression, line=node.line, column=node.column), env
        ) if isinstance(node.expression, ast.Identifier) else type(value).__name__
        print(f"[INSPECT] type={type_name} value={value!r}")

    def eval_ValorPronto(self, node, env):
        return node.value

    def _atribuicao_composta(self, node, op, env):
        """x += v — le, aplica e escreve, avaliando o alvo uma vez so."""
        alvo = node.target
        direita = self.evaluate(node.value, env)

        def aplicar(atual):
            # Direto sobre os valores: montar dois nos de AST por volta
            # so para joga-los fora custava mais que a operacao em si.
            return self._operar(atual, op, direita, node, env)

        if isinstance(alvo, ast.Identifier):
            novo = aplicar(env.get(alvo.name))
            env.set(alvo.name, novo)
            return novo

        if isinstance(alvo, ast.IndexAccess):
            # objeto e indice avaliados uma vez, e reaproveitados
            obj = self.evaluate(alvo.object, env)
            idx = self.evaluate(alvo.index, env)
            if isinstance(obj, DFInstance):
                atual = self._chamar_magico(obj, "__getitem__", [idx], alvo)
                if atual is _SEM_MAGICO:
                    raise NotIndexableError(
                        f"'{obj.blueprint.name}' does not accept '[ ]'.",
                        alvo.line, alvo.column,
                        dica="declare  action __getitem__(chave):",
                        doc="oop/magicos")
                novo = aplicar(atual)
                self._chamar_magico(obj, "__setitem__", [idx, novo], alvo)
                return novo
            try:
                atual = obj[idx]
            except KeyError:
                raise self._erro_chave(obj, idx, alvo)
            except IndexError:
                raise self._erro_indice(obj, idx, alvo)
            novo = aplicar(atual)
            obj[idx] = novo
            return novo

        if isinstance(alvo, ast.MemberAccess):
            # O objeto e avaliado UMA vez, e a leitura e a escrita usam
            # o mesmo valor. Antes isto montava cinco nos de AST por
            # execucao so para joga-los fora.
            obj = self.evaluate(alvo.object, env)
            novo = aplicar(self._ler_membro(obj, alvo, env))
            self._escrever_membro(obj, alvo.member, novo, node, env, alvo)
            return novo

        raise RuntimeError_(
            f"'{op}=' needs a variable, a field or an index on the left.",
            node.line, node.column, doc="operadores")

    def _escrever_membro(self, obj, membro, value, node, env, alvo=None):
        """'obj.membro := valor' com o objeto JA avaliado.

        Devolve '_SEM_MAGICO' quando a escrita foi feita e nao ha valor
        a propagar, e o valor quando ela passou por um 'set' de
        propriedade — que e o unico caso em que 'exec_Assignment'
        retornava cedo.

        Extraido para que a atribuicao COMPOSTA num membro pare de
        montar tres nos de AST por execucao: 'self.n += 1' criava um
        'MemberAccess' para ler, e um 'Assignment' com outro
        'MemberAccess' e dois 'ValorPronto' para escrever — cinco
        objetos por volta de laco, jogados fora em seguida.
        """
        alvo = alvo if alvo is not None else node

        if isinstance(obj, DFRecordInstance):
            raise RuntimeError_(
                f"Record '{obj.record.name}' is immutable: cannot assign to "
                f"'{membro}'. Build a changed copy with "
                f"\"registro with {{'{membro}': valor}}\".",
                node.line, node.column)

        # '_tipos is None' e o que mantem o custo ZERO: um objeto que
        # nunca passou por uma anotacao generica continua pelo caminho
        # rapido, sem uma unica conferencia a mais. E a mesma disciplina
        # dos tres sentinelas de OOP.
        if type(obj) is DFInstance and obj.blueprint.escrita_simples \
                and obj._estado is None and obj._tipos is None \
                and membro not in obj.blueprint.nao_publicos:
            obj.set(membro, value)
            return _SEM_MAGICO
        if isinstance(obj, DFInstance):
            bp = obj.blueprint
            if bp.escrita_magica:
                chave = (id(obj), "__setattr__")
                ativos = self._por_thread.magicos_ativos
                if chave not in ativos:
                    acao = self._achar_magico(obj, "__setattr__")
                    ativos.add(chave)
                    try:
                        self._call_action(acao, [membro, value], {}, node, env,
                                          instance=obj)
                    finally:
                        ativos.discard(chave)
                    return _SEM_MAGICO
            if membro in bp.nao_publicos:
                self._conferir_acesso(bp, membro, env, alvo)
            # Propriedade com 'set': a atribuicao roda o corpo do setter
            prop = bp.buscar_propriedade(membro)
            if prop is not None:
                if 'set' not in prop:
                    raise ReadOnlyPropertyError(
                        f"'{bp.name}.{membro}' is read-only: it "
                        f"has a 'get' but no 'set'.\n"
                        f"    Add one:  set {membro}(valor): …",
                        node.line, node.column)
                self._call(prop['set'], [value], {}, node, env, instancia=obj)
                if prop.get('lazy') and obj._estado is not None and obj._estado.cache:
                    obj._estado.cache.pop(membro, None)
                return value
            if bp.descritores and membro in bp.descritores:
                resposta = self._chamar_magico(bp.descritores[membro], "__set__",
                                               [obj, value], node)
                if resposta is not _SEM_MAGICO:
                    return _SEM_MAGICO
            if obj._estado is not None or bp.somente_leitura:
                objetos.conferir_escrita(obj, membro, alvo)
            if obj._tipos is not None:
                self._conferir_campo_generico(obj, membro, value, alvo)
            vigias = bp.vigias
            if vigias is not None and "on_write" in vigias.ganchos:
                trocado = self._gancho_de_vigia(vigias, "on_write",
                                                [obj, membro, value], node)
                if trocado is not None and trocado is not _SEM_MAGICO:
                    value = trocado
            obj.set(membro, value)
        elif isinstance(obj, DFBlueprint):
            if membro in obj.constantes:
                raise ConstantReassignmentError(
                    f"'{obj.name}.{membro}' is a class constant and cannot be "
                    f"reassigned.",
                    node.line, node.column,
                    nota=f"it was declared  static steady {membro} := …",
                    dica="declare it  static  without 'steady' if it has to change",
                    doc="oop/estaticos")
            obj.statics[membro] = value
        elif isinstance(obj, dict):
            obj[membro] = value
        elif type(obj).__setattr__ is not object.__setattr__:
            # O objeto de fora DECLAROU o que fazer numa escrita, e e
            # ele quem sabe dizer o porque. 'Cannot set a member on a
            # Valor' e verdade e nao ajuda; o proprio objeto responde
            # "e um objeto de valor: ele nao muda" e sugere o '.com()'.
            #
            # A porta e estreita de proposito: so passa quem define
            # '__setattr__'. Um objeto que nao define continua no
            # caminho de antes — a leitura ja era por protocolo, e esta
            # e a metade que faltava.
            try:
                setattr(obj, membro, value)
            except DataForgeError:
                raise
            except Exception as erro:                    # noqa: BLE001
                raise RuntimeError_(
                    self._traduzir_tipos(str(erro)),
                    node.line, node.column, doc="oop")
        else:
            raise RuntimeError_(
                f"Cannot set a member on {self._nome_do_tipo(obj)}.",
                node.line, node.column,
                nota="only a blueprint instance and a vault accept "
                     "'x.campo := …'",
                dica=("a record is immutable — use  p with {\"campo\": valor}"
                      if isinstance(obj, DFRecordInstance) else ""),
                doc="oop")
        return _SEM_MAGICO

    def exec_Assignment(self, node: ast.Assignment, env):
        # Atribuicao composta ('x += 1') avalia o alvo UMA vez: 'v[f()] += 1'
        # nao pode chamar f() duas vezes, uma para ler e outra para escrever.
        op = getattr(node, 'compound_op', "")
        if op:
            return self._atribuicao_composta(node, op, env)

        value = self.evaluate(node.value, env)

        declared = getattr(node, 'declared_type', "")
        if declared:
            self._check_type(value, declared, f"variable '{self._target_name(node.target)}'", node)
            if "<" in declared and _nasce_aqui(node.value, env):
                value = _tipar_colecao(value, declared)

        if isinstance(node.target, ast.Identifier):
            env.set(node.target.name, value)
        elif isinstance(node.target, ast.MemberAccess):
            obj = self.evaluate(node.target.object, env)
            devolvido = self._escrever_membro(
                obj, node.target.member, value, node, env, node.target)
            if devolvido is not _SEM_MAGICO:
                return devolvido
        elif isinstance(node.target, ast.IndexAccess):
            self._escrever_indice(self.evaluate(node.target.object, env),
                                  self.evaluate(node.target.index, env),
                                  value, node)
        else:
            raise RuntimeError_("Invalid assignment target", node.line, node.column)

        return value

    def _escrever_indice(self, obj, idx, value, node):
        """`v["k"] := x` e `xs[i] := x` — com objeto e indice prontos."""
        if isinstance(obj, DFInstance):
            feito = self._chamar_magico(obj, "__setitem__", [idx, value], node)
            if feito is _SEM_MAGICO:
                raise NotIndexableError(
                    f"'{obj.blueprint.name}' does not accept "
                    f"'obj[chave] := valor'.",
                    node.line, node.column,
                    dica="declare  action __setitem__(chave, valor):",
                    doc="oop/magicos")
        elif isinstance(obj, tuple):
            self._recusar_escrita_em_tupla(node)
        else:
            obj[idx] = value

    def exec_SteadyDeclaration(self, node: ast.SteadyDeclaration, env):
        value = self.evaluate(node.value, env)
        env.define_steady(node.name, value)
        return value

    def exec_ShadowDeclaration(self, node: ast.ShadowDeclaration, env):
        value = self.evaluate(node.value, env)
        env.define_shadow(node.name, value)
        return value

    def exec_StaticDeclaration(self, node: ast.StaticDeclaration, env):
        value = self.evaluate(node.value, env)
        env.set_local(node.name, value)
        return value

    # ── Control Flow ───────────────────────────────────────

    def exec_GivenBlock(self, node: ast.GivenBlock, env):
        """given / orif / otherwise.

        O corpo roda no MESMO escopo, como o do 'monitor', e pelo mesmo
        motivo: decidir um valor em dois ramos e o padrao mais comum que
        existe, e com escopo proprio ele nao funcionava.

            given n % 2 is 0:
                rotulo := "par"
            otherwise:
                rotulo := "impar"
            out rotulo          // 'rotulo' is not defined

        O 'monitor' ja tinha essa decisao tomada e escrita; o 'given'
        ficou de fora, e a linguagem respondia coisas diferentes para a
        mesma pergunta. Quem batia nisso declarava 'rotulo := ""' antes
        do bloco — um valor que nunca e usado, so para o nome existir.

        A mudanca so ACRESCENTA: um nome que ja existia fora continuava
        sendo atualizado de qualquer jeito, porque 'Environment.set' sobe
        a cadeia. O que muda e o nome que nascia aqui dentro, e que antes
        morria com o bloco.

        O 'cycle' continua com escopo proprio, e isso e de proposito: e o
        que faz cada volta ter o seu 'i', e um 'lambda' criado no corpo
        lembrar o valor da volta em que nasceu. Sem isso as tres closures
        de um laco de tres voltas veriam todas o ultimo valor — o
        classico que o Python tem e que aqui nao acontece.
        """
        # '_verdade' e nao 'bool': uma instancia com '__bool__' decide
        # por si, e uma com '__len__' segue a regra do tamanho zero.
        condition = self._verdade(self.evaluate(node.condition, env), node)
        if condition:
            return self.exec_block(node.body, env)

        for orif_cond, orif_body in node.orif_blocks:
            if self._verdade(self.evaluate(orif_cond, env), node):
                return self.exec_block(orif_body, env)

        if node.otherwise_body:
            return self.exec_block(node.otherwise_body, env)

        return None

    def exec_MatchBlock(self, node: ast.MatchBlock, env):
        valor = self.evaluate(node.expression, env)

        for caso in node.points:
            # Compatibilidade: 'point' antigo guardado como tupla (valor, corpo)
            if isinstance(caso, tuple):
                alvo, corpo = caso
                if valor == self.evaluate(alvo, env):
                    return self.exec_block(corpo, env.child("<point>"))
                continue

            ligacoes = {}
            if not self._match_pattern(caso.pattern, valor, env, ligacoes):
                continue
            escopo = env.child("<point>")
            for nome, ligado in ligacoes.items():
                escopo.set_local(nome, ligado)
            if caso.guard is not None and not self.evaluate(caso.guard, escopo):
                continue
            return self.exec_block(caso.body, escopo)

        if node.default_body:
            return self.exec_block(node.default_body, env.child("<default>"))
        return None

    # ── Loops ──────────────────────────────────────────────

    @staticmethod
    def _corpo_captura_escopo(corpo):
        """O corpo do laco guarda uma referencia ao escopo da volta?

        Uma acao declarada dentro do laco captura o escopo no
        fechamento; um 'thread' ou 'defer' idem. Nesses casos cada volta
        precisa do proprio escopo, senao todas compartilhariam o ultimo
        — o classico 'todas as funcoes veem o mesmo i'.

        Fora esses casos, o escopo pode ser reaproveitado, e um laco de
        200 mil voltas deixa de alocar 200 mil objetos.
        """
        CAPTURAM = (ast.ActionDeclaration, ast.BlueprintDeclaration,
                    ast.RecordDeclaration, ast.ThreadBlock,
                    ast.DeferStatement, ast.ParallelBlock,
                    ast.LambdaExpression)

        # Varre a arvore inteira do corpo, nao so o primeiro nivel: um
        # 'lambda' vive DENTRO de uma expressao ('lista.append(lambda …)'),
        # e olhar so as instrucoes o deixaria passar — todas as closures
        # da volta acabariam vendo o ultimo valor.
        pilha = list(corpo)
        vistos = 0
        while pilha:
            no = pilha.pop()
            vistos += 1
            if vistos > 5000:
                # Corpo enorme: assumir que captura e o lado seguro.
                return True
            if isinstance(no, CAPTURAM):
                return True
            if isinstance(no, (list, tuple)):
                pilha.extend(no)
                continue
            if isinstance(no, dict):
                pilha.extend(no.values())
                continue
            if not isinstance(no, ast.ASTNode):
                continue
            for campo in getattr(no, "__dataclass_fields__", ()):
                valor = getattr(no, campo, None)
                if isinstance(valor, (ast.ASTNode, list, tuple, dict)):
                    pilha.append(valor)
        return False

    def _escopo_de_laco(self, node, env, nome):
        """O escopo da volta — novo a cada vez, ou um so reaproveitado.

        A decisao e por no de laco e memorizada: analisar o corpo a cada
        volta custaria mais do que a alocacao que se quer evitar.
        """
        captura = getattr(node, "_captura_escopo", None)
        if captura is None:
            captura = self._corpo_captura_escopo(node.body)
            try:
                node._captura_escopo = captura
            except AttributeError:
                pass
        if captura:
            return None                       # um novo por volta
        return env.child(nome)

    def exec_CycleFromTo(self, node: ast.CycleFromTo, env):
        start = self.evaluate(node.start, env)
        end = self.evaluate(node.end, env)
        step = self.evaluate(node.step, env) if node.step else 1

        reusavel = self._escopo_de_laco(node, env, "<cycle>")
        corpo = node.body
        i = start
        while (step > 0 and i <= end) or (step < 0 and i >= end):
            if reusavel is None:
                loop_env = env.child("<cycle>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            loop_env.set_local(node.var, i)
            try:
                self.exec_block(corpo, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                pass
            i += step

    def _percorrer(self, valor, node=None):
        """Os itens de um valor, honrando '__iter__' e '__next__'.

        Um objeto com '__iter__' devolve o proprio percorrivel — que
        pode ser um cluster, um generator, ou ele mesmo com '__next__'.
        E o protocolo do Python, e o mesmo que quem escreve espera.

        O fim do percurso e sinalizado devolvendo 'void' de
        '__next__', e nao levantando erro: em DataForge, usar erro
        para fluxo normal e caro e obscuro.
        """
        if not isinstance(valor, DFInstance):
            return valor

        fonte = valor
        interno = self._chamar_magico(valor, "__iter__", [], node)
        if interno is not _SEM_MAGICO and interno is not None:
            fonte = interno
            if not isinstance(fonte, DFInstance):
                return fonte

        if not self._tem_magico(fonte, "__next__"):
            raise TypeError_(
                f"'{valor.blueprint.name}' cannot be cycled over.",
                getattr(node, "line", 0), getattr(node, "column", 0),
                nota="it has no '__iter__' that yields a collection, "
                     "and no '__next__'",
                dica=("declare  action __iter__():  yielding a cluster, or "
                      "declare  action __next__():  yielding void at the end"),
                doc="oop/magicos")

        def gerar():
            # Um teto: um '__next__' que nunca devolve void trava o
            # programa sem dizer por que. Com o teto, ele para e
            # explica — e o numero e alto o suficiente para nao
            # atrapalhar percurso legitimo.
            for _ in range(10_000_000):
                item = self._chamar_magico(fonte, "__next__", [], node)
                if item is _SEM_MAGICO or item is None:
                    return
                yield item
            raise InfiniteLoopError(
                f"'{fonte.blueprint.name}.__next__' never returned void.",
                getattr(node, "line", 0), getattr(node, "column", 0),
                nota="10 million items were produced",
                dica="yield void when the sequence ends",
                doc="oop/magicos")

        return gerar()

    def exec_CycleIn(self, node: ast.CycleIn, env):
        collection = self.evaluate(node.collection, env)
        if isinstance(collection, DFInstance):
            collection = self._percorrer(collection, node)
        if not hasattr(collection, '__iter__'):
            raise TypeError_(
                f"Cannot cycle over {self._type_of(collection)}: "
                f"expected a Cluster, Vault or String",
                node.line, node.column)
        reusavel = self._escopo_de_laco(node, env, "<cycle>")
        corpo = node.body
        nomes = getattr(node, "vars", None) or []
        for item in collection:
            if reusavel is None:
                loop_env = env.child("<cycle>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            if nomes:
                self._espalhar_no_laco(nomes, item, loop_env, node)
            else:
                loop_env.set_local(node.var, item)
            try:
                self.exec_block(corpo, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue

    def _espalhar_no_laco(self, nomes, item, escopo, node):
        """'cycle i, item in …' — reparte cada item pelos nomes.

        Um item que nao se reparte da erro AQUI, dizendo quantos nomes
        havia e quantos valores vieram. Sem isso o erro apareceria mais
        tarde, ao usar um dos nomes, e ele diria 'nao definido'.
        """
        if isinstance(item, dict):
            valores = list(item.items())[0] if len(nomes) == 2 else None
            if valores is None:
                valores = list(item.values())
        elif isinstance(item, (list, tuple)):
            valores = list(item)
        else:
            raise TypeError_(
                f"cannot split {self._nome_do_tipo(item)} across "
                f"{len(nomes)} names.",
                node.line, node.column,
                nota=f"the loop asked for {', '.join(nomes)}",
                dica=("each item needs to be a Cluster or a pair; "
                      "'enumerate(xs)' produces pairs"),
                doc="lacos")

        if len(valores) != len(nomes):
            raise UnpackError(
                f"each item has {len(valores)} value(s), but the loop "
                f"asks for {len(nomes)} name(s).",
                node.line, node.column,
                nota=f"names: {', '.join(nomes)}",
                dica="use one name to receive the item whole",
                doc="fundamentos/desestruturacao")

        for nome, valor in zip(nomes, valores):
            escopo.set_local(nome, valor)

    def exec_PersistBlock(self, node: ast.PersistBlock, env):
        reusavel = self._escopo_de_laco(node, env, "<persist>")
        corpo = node.body
        while self._verdade(self.evaluate(node.condition, env), node):
            if reusavel is None:
                loop_env = env.child("<persist>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            try:
                self.exec_block(corpo, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue

    def exec_PerformBlock(self, node: ast.PerformBlock, env):
        reusavel = self._escopo_de_laco(node, env, "<perform>")
        while True:
            if reusavel is None:
                loop_env = env.child("<perform>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            try:
                self.exec_block(node.body, loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                pass
            if not self.evaluate(node.condition, env):
                break

    # ── Functions & Classes ────────────────────────────────

    def exec_ActionDeclaration(self, node: ast.ActionDeclaration, env):
        action = DFAction(
            name=node.name,
            params=node.params,
            defaults=node.defaults,
            body=node.body,
            closure=env,
            is_async=node.is_async,
            param_types=getattr(node, 'param_types', None),
            return_type=getattr(node, 'return_type', ""),
            is_generator=getattr(node, 'is_generator', False),
            type_params=getattr(node, 'type_params', None),
            type_bounds=getattr(node, 'type_bounds', None),
        )
        self._extras_da_declaracao(action, node)
        if getattr(node, 'is_overload', False):
            anterior = env.variables.get(node.name)
            if anterior is not None and not (
                    isinstance(anterior, DFAction) and anterior.extras is not None
                    and anterior.extras.variantes):
                raise AmbiguousOverloadError(
                    f"'{node.name}' already exists and is not an overload group.",
                    node.line, node.column,
                    nota="every declaration of an overloaded action is marked "
                         "'overload', including the first",
                    dica=f"write  overload action {node.name}(…)  in all of them",
                    doc="oop/sobrecarga")
            action = self._aplicar_decoradores(action, node, env)
            grupo = self._grupo_de_sobrecarga(node.name, action, anterior, node)
            env.set_local(node.name, grupo)
            return grupo
        env.set_local(node.name, action)

        valor = self._aplicar_decoradores(action, node, env)
        env.set_local(node.name, valor)
        return valor

    # ── Decoradores ────────────────────────────────────────

    def _resolver_decorador(self, nome, node, env):
        """O decorador pelo nome, aceitando 'Modulo.Nome'."""
        partes = nome.split(".")
        try:
            valor = env.get(partes[0])
        except NameError_:
            raise RuntimeError_(
                f"'@{nome}' não existe.",
                node.line, node.column,
                nota="um decorador é uma ação que recebe o que decora "
                     "e devolve o que fica no lugar",
                dica=f"declare 'action {partes[0]}(alvo):' antes de usá-lo, "
                     f"ou importe o módulo que o traz",
                doc="fundamentos/decoradores") from None

        for parte in partes[1:]:
            if isinstance(valor, dict):
                if parte not in valor:
                    raise RuntimeError_(
                        f"'{parte}' não existe em '{partes[0]}'.",
                        node.line, node.column, doc="fundamentos/decoradores")
                valor = valor[parte]
            else:
                valor = getattr(valor, parte, None)
        return valor

    def _aplicar_decoradores(self, alvo, node, env):
        """Aplica a pilha de decoradores, o mais proximo primeiro.

            @A
            @B
            action f(): …        vira  A(B(f))

        E a ordem de toda linguagem que tem decoradores: o de baixo
        embrulha primeiro, e o de cima embrulha o resultado.

        Antes de aplicar, os metadados do decorador sao gravados no
        alvo. E o que permite um decorador so anotar — '@Rota("/x")' nao
        precisa embrulhar nada, so registrar o caminho para outra parte
        do programa ler depois.
        """
        decoradores = getattr(node, "decorators", None) or []
        if not decoradores:
            return alvo

        for deco in decoradores:
            args = [self.evaluate(a, env) for a in (deco.args or [])]
            kwargs = {k: self.evaluate(v, env)
                      for k, v in (deco.kwargs or {}).items()}
            self._gravar_metadado(alvo, deco.name, args, kwargs)

        valor = alvo
        for deco in reversed(decoradores):
            funcao = self._resolver_decorador(deco.name, node, env)
            args = [self.evaluate(a, env) for a in (deco.args or [])]
            kwargs = {k: self.evaluate(v, env)
                      for k, v in (deco.kwargs or {}).items()}

            if args or kwargs:
                # Com argumentos, o decorador e uma FABRICA: primeiro
                # recebe a configuracao, depois o alvo.
                fabrica = self._call(funcao, args, kwargs, node, env)
                novo = self._call(fabrica, [valor], {}, node, env)
            else:
                novo = self._call(funcao, [valor], {}, node, env)

            # Um decorador que so anota devolve void; nesse caso o alvo
            # segue sendo ele mesmo. Sem isto, '@Rota("/x")' apagaria a
            # acao que decorou.
            if novo is not None:
                self._herdar_metadados(valor, novo)
                valor = novo

        return valor

    @staticmethod
    def _gravar_metadado(alvo, nome, args, kwargs):
        """Guarda '@Nome(args)' no alvo, para leitura posterior."""
        try:
            registro = getattr(alvo, "__metadados__", None)
            if registro is None:
                registro = []
                alvo.__metadados__ = registro
            registro.append({"nome": nome, "args": list(args),
                             "kwargs": dict(kwargs)})
        except (AttributeError, TypeError):
            pass          # o alvo nao aceita atributo; segue sem metadado

    @staticmethod
    def _herdar_metadados(antigo, novo):
        """O embrulho herda os metadados do que embrulhou.

        Sem isto, '@Injetavel @Rota("/x")' perderia a anotacao assim que
        o primeiro decorador devolvesse um embrulho.
        """
        try:
            herdados = getattr(antigo, "__metadados__", None)
            if herdados and not getattr(novo, "__metadados__", None):
                novo.__metadados__ = list(herdados)
        except (AttributeError, TypeError):
            pass

    def _valor_pontuado(self, nome, env):
        """'Forma' ou 'Geo.Forma' — o valor de um nome que pode vir de modulo."""
        partes = nome.split(".")
        valor = env.get(partes[0])
        for parte in partes[1:]:
            if isinstance(valor, dict) and parte in valor:
                valor = valor[parte]
            elif isinstance(valor, DFBlueprint) and parte in valor.statics:
                valor = valor.statics[parte]
            else:
                raise NameError_(f"'{nome}' does not exist: '{parte}' is not "
                                 f"in '{'.'.join(partes[:partes.index(parte)])}'.")
        return valor

    def exec_BlueprintDeclaration(self, node: ast.BlueprintDeclaration, env):
        parents = []
        for pname in node.parents:
            # Uma mae que nao existe era IGNORADA em silencio: o blueprint
            # nascia sem ela, e a falta aparecia paginas depois como "has no
            # member 'x'" — longe da causa, e apontando a chamada em vez da
            # declaracao. O 'check' ja acusava; a execucao, nao.
            #
            # O trait e a excecao: ele e lido como texto em 'traits', e o
            # nome dele pode nao existir como valor.
            if pname == node.name:
                # Dizer "nao existe" aqui e verdade (o nome ainda nao esta
                # ligado) e confunde: o problema e o 'extends' apontar para
                # o proprio blueprint.
                raise TypeError_(
                    f"Blueprint '{node.name}' cannot extend itself.",
                    node.line, node.column,
                    dica="a blueprint inherits from ANOTHER one; remove the "
                         "'extends', or name the real parent",
                    doc="oop")
            try:
                parent = self._valor_pontuado(pname, env)
            except NameError_:
                if pname in (getattr(node, "traits", None) or ()):
                    continue
                raise NameError_(
                    f"Blueprint '{node.name}' extends '{pname}', which does "
                    f"not exist.",
                    node.line, node.column,
                    nota="the parent has to be declared before the child",
                    dica=f"declare 'blueprint {pname}' first, or remove the "
                         f"'extends'",
                    doc="oop") from None
            if isinstance(parent, DFBlueprint):
                self._conferir_mae(node, parent)
                parents.append(parent)
            elif pname not in (getattr(node, "traits", None) or ()):
                raise TypeError_(
                    f"Blueprint '{node.name}' extends '{pname}', which is "
                    f"{self._nome_do_tipo(parent)} and not a blueprint.",
                    node.line, node.column, doc="oop")

        meta_bp = self._metaclasse_de(node, parents, env)

        bp_env = env.child(f"<blueprint {node.name}>")
        methods, statics = {}, {}
        properties, operators, visibility = {}, {}, {}
        slots_declarados = None
        abstract_methods, static_methods, final_methods = set(), set(), set()
        origem_abstrata = {}          # metodo -> quem exigiu (trait ou pai)
        constructor_body = []
        #: 'x := valor' no corpo — campo com padrao, sem tipo declarado.
        campos_sem_tipo = []
        constantes = set()
        #: 'type Item := Integer' no corpo — o tipo associado do trait,
        #: preenchido por quem implementa.
        associados_do_corpo = {}
        invariantes = []
        descritores = {}
        contratos = set()
        adotados = []

        # Herda dos pais, na ordem INVERSA da declaracao.
        #
        # 'update' faz o ultimo vencer. Percorrendo na ordem escrita,
        # 'blueprint D extends B, C' daria o metodo de C — e a regra em
        # toda linguagem com heranca multipla e que o PRIMEIRO pai
        # escrito tem prioridade. Invertendo, B sobrescreve C e a
        # prioridade fica certa.
        #
        # Isto e a MRO aplicada na construcao. Ela existe tambem em
        # 'linhagem()', para a busca dinamica; as duas precisam
        # concordar, e concordam porque as duas respeitam a ordem em
        # que os pais foram escritos.
        for parent in reversed(parents):
            methods.update(parent.methods)
            statics.update(parent.statics)
            properties.update(parent.properties)
            operators.update(parent.operators)
            static_methods |= parent.static_methods
            final_methods |= parent.final_methods
            constantes |= parent.constantes
            descritores.update(parent.descritores)
            contratos |= parent.contratos_todos

        # Traits e contratos: so preenchem o que ainda nao existe
        traits_adotados = list(getattr(node, 'traits', []))
        for tname in traits_adotados:
            try:
                trait = self._valor_pontuado(tname, env)
            except NameError_:
                continue
            if not isinstance(trait, DFBlueprint):
                continue
            adotados.append(trait)
            contratos |= trait.contratos_todos | {trait.name}
            for mname, mval in trait.methods.items():
                if mname not in methods:
                    methods[mname] = mval
            for pname, pval in trait.properties.items():
                properties.setdefault(pname, pval)
            for nome_associado, tipo_associado in (
                    getattr(trait, "tipos_associados", None) or {}).items():
                associados_do_corpo.setdefault(nome_associado, tipo_associado)
                statics.setdefault(nome_associado, tipo_associado)
            herdadas_do_trait = getattr(trait, "origem_das_exigencias", None) or {}
            for n in trait.abstract_methods:
                if n not in methods:
                    abstract_methods.add(n)
                    # 'Editavel extends Legivel': quem exige 'ler' é o
                    # Legivel, e é o nome dele que ajuda quem lê o erro.
                    origem_abstrata[n] = herdadas_do_trait.get(n, tname)

        #: o que ja existia ANTES do corpo — e o que um 'override' pode mirar
        herdados = set(methods) | set(abstract_methods)
        for parent in parents:
            for ancestral in parent.linhagem():
                herdados |= ancestral.abstract_methods
        propriedades_herdadas = set(properties) | {
            p for t in adotados for p in t.propriedades_exigidas}
        declarados_aqui = set()

        for stmt in node.body:
            if isinstance(stmt, ast.SlotsDeclaration):
                slots_declarados = list(stmt.names)
                continue
            # 'type Item := Integer' — o tipo associado. Ele existe como
            # nome de tipo (para as anotacoes dos metodos) e como membro
            # estatico ('Fila.Item'), que e como se pergunta por ele.
            if isinstance(stmt, ast.TypeDeclaration):
                self.exec_TypeDeclaration(stmt, bp_env)
                associados_do_corpo[stmt.name] = (
                    stmt.partes[0] if stmt.partes else "Any")
                statics[stmt.name] = associados_do_corpo[stmt.name]
                continue
            if isinstance(stmt, ast.ActionDeclaration):
                nome = stmt.name
                # 'final' do pai nao pode ser sobrescrito
                if nome in final_methods and nome not in declarados_aqui:
                    dono = next((bp.name for bp in
                                 (p for pa in parents for p in pa.linhagem())
                                 if nome in bp.methods), "the parent")
                    raise FinalOverrideError(
                        f"'{node.name}.{nome}' cannot override "
                        f"'{dono}.{nome}', which is declared final",
                        stmt.line, stmt.column, doc="oop/modificadores")

                if getattr(stmt, 'is_override', False) and nome not in herdados:
                    self._erro_override(node, stmt, nome, herdados)

                if getattr(stmt, 'is_abstract', False):
                    abstract_methods.add(nome)
                else:
                    abstract_methods.discard(nome)

                action = self._acao_de_metodo(stmt, node, bp_env)

                # Decoradores do metodo. Sem isto, '@Rota("/x")' dentro
                # de um blueprint seria ignorado — e e justamente ai que
                # ele mais serve, para um controlador declarar as rotas
                # ao lado dos metodos que as atendem.
                action = self._aplicar_decoradores(action, stmt, bp_env)

                if getattr(stmt, 'is_overload', False):
                    anterior = methods.get(nome) if nome in declarados_aqui else \
                        (methods.get(nome) if isinstance(methods.get(nome), DFAction)
                         and methods[nome].extras is not None
                         and methods[nome].extras.variantes else None)
                    action = self._grupo_de_sobrecarga(nome, action, anterior, stmt)
                elif nome in declarados_aqui and isinstance(methods.get(nome), DFAction) \
                        and methods[nome].extras is not None and methods[nome].extras.variantes:
                    raise AmbiguousOverloadError(
                        f"'{node.name}.{nome}' mixes 'overload' variants with a "
                        f"plain action of the same name.",
                        stmt.line, stmt.column,
                        dica="mark every variant with 'overload', or rename one",
                        doc="oop/sobrecarga")
                methods[nome] = action
                declarados_aqui.add(nome)

                visibility[nome] = getattr(stmt, 'visibility', 'public')
                if getattr(stmt, 'is_static', False):
                    static_methods.add(nome)
                    statics[nome] = action
                if getattr(stmt, 'is_final', False):
                    final_methods.add(nome)

            elif isinstance(stmt, ast.PropertyDeclaration):
                if getattr(stmt, 'is_override', False) and \
                        stmt.name not in propriedades_herdadas:
                    self._erro_override(node, stmt, stmt.name,
                                        propriedades_herdadas, "property")
                acao = DFAction(
                    name=stmt.name,
                    params=[stmt.param] if stmt.kind == 'set' else [],
                    defaults={}, body=stmt.body, closure=bp_env,
                    return_type=getattr(stmt, 'return_type', ""))
                acao.owner = node.name
                acao.visibilidade = getattr(stmt, 'visibility', 'public')
                atual = dict(properties.get(stmt.name) or {})
                atual[stmt.kind] = acao
                if getattr(stmt, 'is_lazy', False):
                    atual['lazy'] = True
                properties[stmt.name] = atual
                declarados_aqui.add(stmt.name)
                visibility[stmt.name] = getattr(stmt, 'visibility', 'public')
                decos = getattr(stmt, 'decorators', None) or []
                if decos:
                    self._gravar_metadados_de_membro(
                        stmt.name, decos, bp_env, acao)

            elif isinstance(stmt, ast.OperatorDeclaration):
                acao = DFAction(name=f"operator{stmt.symbol}",
                                params=[stmt.param], defaults={},
                                body=stmt.body, closure=bp_env)
                acao.owner = node.name
                operators[stmt.symbol] = acao

            elif isinstance(stmt, ast.StaticDeclaration):
                if stmt.name in constantes and stmt.name not in declarados_aqui:
                    raise ConstantReassignmentError(
                        f"'{node.name}.{stmt.name}' is a class constant of the "
                        f"parent and cannot be redeclared.",
                        stmt.line, stmt.column, doc="oop/estaticos")
                valor_estatico = self.evaluate(stmt.value, bp_env)
                if getattr(stmt, 'declared_type', ""):
                    self._check_type(valor_estatico, stmt.declared_type,
                                     f"static field '{stmt.name}'", stmt)
                statics[stmt.name] = valor_estatico
                if getattr(stmt, 'is_steady', False):
                    constantes.add(stmt.name)
                declarados_aqui.add(stmt.name)

            elif isinstance(stmt, ast.InvariantStatement):
                invariantes.append((stmt, bp_env, node.name))

            elif isinstance(stmt, (ast.BlueprintDeclaration, ast.RecordDeclaration,
                                   ast.EnumDeclaration, ast.ContractDeclaration,
                                   ast.TraitDeclaration)):
                # Declaracao aninhada: vira membro estatico do blueprint de
                # fora. 'spawn Pedido.Item()' e o jeito de dizer que Item so
                # existe em funcao de Pedido — e de nao poluir o arquivo.
                self.execute(stmt, bp_env)
                statics[stmt.name] = bp_env.get(stmt.name)

            elif isinstance(stmt, ast.Assignment):
                # 'x := valor' e um CAMPO com padrao, sempre — venha o
                # blueprint com parametros ou sem.
                #
                # Antes dependia do cabecalho, e das tres maneiras
                # possiveis so uma fazia o que parece:
                #
                #   blueprint C(p):  x := 1        nao criava nada
                #   blueprint C:     x := 1        virava ESTATICO,
                #                                  compartilhado por
                #                                  todas as instancias
                #   blueprint C:     x: Integer := 1   campo, por
                #                                      instancia
                #
                # O estatico com valor mutavel e o pior deles:
                # 'itens := []' dava UMA lista para todas as
                # instancias, e o 'append' de uma aparecia em todas —
                # sem erro. A forma COM TIPO ja copiava o padrao por
                # instancia justamente por isso, e as duas escritas do
                # mesmo campo faziam coisas opostas.
                #
                # Para um valor de CLASSE existe 'static x := valor',
                # que e explicito e continua funcionando.
                if isinstance(stmt.target, ast.Identifier):
                    campos_sem_tipo.append(
                        (stmt.target.name, None, stmt.value,
                         getattr(stmt, 'visibility', 'public')))
                else:
                    # 'self.x := …' — vai para o construtor.
                    constructor_body.append(stmt)

            else:
                constructor_body.append(stmt)

        # Campos declarados: 'nome: Tipo := padrao'
        campos = []
        for nome, tipo, padrao, visib in (list(getattr(node, 'fields_decl', []))
                                          + campos_sem_tipo):
            valor = self.evaluate(padrao, bp_env) if padrao is not None else None
            if tipo and "<" in tipo and valor is not None:
                parametros_do_molde = tuple(getattr(node, "type_params", ()) or ())
                self._check_type(valor, tipo, f"field '{nome}' of '{node.name}'",
                                 node, parametros_do_molde,
                                 getattr(node, "type_bounds", None))
                if _nasce_aqui(padrao, bp_env):
                    valor = _tipar_colecao(valor, tipo, parametros_do_molde)
            campos.append((nome, tipo, valor, visib))
            visibility[nome] = visib
            if isinstance(valor, DFInstance) and (
                    self._achar_magico(valor, "__get__") is not None
                    or self._achar_magico(valor, "__set__") is not None):
                descritores[nome] = valor
        for parent in parents:
            declarados = {c[0] for c in campos}
            campos = [c for c in parent.fields_decl
                      if c[0] not in declarados] + campos

        for nome_param, tipo_param in (getattr(node, 'constructor_types', None) or {}).items():
            if nome_param not in visibility:
                visibility.setdefault(nome_param, "public")

        blueprint = DFBlueprint(
            name=node.name, parents=parents,
            methods=methods, statics=statics, env=bp_env,
            constructor_params=node.constructor_params,
            constructor_body=constructor_body,
            slots=slots_declarados,
            properties=properties, operators=operators,
            fields_decl=campos, visibility=visibility,
            is_abstract=getattr(node, 'is_abstract', False),
            abstract_methods=abstract_methods,
            static_methods=static_methods,
            final_methods=final_methods,
            traits=traits_adotados,
        )
        blueprint.origem_abstrata = origem_abstrata
        blueprint.e_final = getattr(node, 'is_final', False)
        blueprint.e_selado = getattr(node, 'is_sealed', False)
        blueprint.e_meta = getattr(node, 'is_meta', False)
        blueprint.arquivo = self.filename or ""
        blueprint.constantes = constantes
        blueprint.descritores = descritores
        blueprint.contratos_todos = frozenset(contratos)
        blueprint.tipos_do_cabecalho = dict(getattr(node, 'constructor_types', None) or {})
        blueprint.padroes_do_cabecalho = dict(getattr(node, 'constructor_defaults', None) or {})
        blueprint.type_params = list(getattr(node, 'type_params', None) or [])
        blueprint.type_bounds = dict(getattr(node, 'type_bounds', None) or {})
        blueprint.meta_blueprint = meta_bp
        modificadores = getattr(node, 'field_modifiers', None) or {}
        proprios_readonly = {n for n, m in modificadores.items() if 'readonly' in m}
        blueprint.somente_leitura = frozenset(
            proprios_readonly.union(*(p.somente_leitura for p in parents)))
        blueprint.nao_publicos = frozenset(
            {n for n, v in visibility.items() if v != "public"}.union(
                *(p.nao_publicos for p in parents)))
        blueprint.finalizador = next(
            (methods[n] for n in ("teardown", "__del__")
             if isinstance(methods.get(n), DFAction)), None)
        blueprint.leitura_magica = "__getattribute__" in methods
        blueprint.escrita_magica = "__setattr__" in methods
        for nome_campo, decos in (getattr(node, 'field_decorators', None) or {}).items():
            self._gravar_metadados_de_membro(nome_campo, decos, bp_env, None,
                                             blueprint)
        for parent in parents:
            for nome_campo, marcas in parent.metadados_de_campo.items():
                blueprint.metadados_de_campo.setdefault(nome_campo, list(marcas))
        blueprint.vigias = self._montar_vigias(blueprint, parents, invariantes,
                                               meta_bp)
        blueprint.recalcular_acesso()
        _carimbar_dono(blueprint)

        if blueprint.e_meta:
            objetos.conferir_ganchos(blueprint)

        # Contrato de trait: conferido aqui, na declaracao, e nao na chamada.
        # Descobrir que falta um metodo so quando alguem o chama, em producao,
        # e tarde demais.
        if not blueprint.is_abstract:
            self._conferir_contrato(blueprint, node, env)
            self._conferir_assinaturas(blueprint, adotados, node)

        import weakref as _weakref
        for parent in parents:
            parent.herdeiros.append(_weakref.ref(blueprint))
        self._registrar_blueprint(blueprint)

        bp_env.set_local(node.name, blueprint)

        # Os ganchos do nascimento da classe, na ordem do Python: o nome de
        # cada descritor, depois a mae ('__init_subclass__'), depois a
        # metaclasse — e so entao os decoradores, que recebem a classe
        # pronta.
        for nome_campo, descritor in descritores.items():
            if nome_campo in {c[0] for c in getattr(node, 'fields_decl', [])} | \
                    {c[0] for c in campos_sem_tipo}:
                self._chamar_magico(descritor, "__set_name__",
                                    [blueprint, nome_campo], node)
        for parent in parents:
            gancho = Interpreter._achar_magico_no_molde(parent, "__init_subclass__")
            if gancho is not None:
                self._call_action(gancho, [blueprint], {}, node, env)
        valor = blueprint
        if meta_bp is not None:
            for parent in parents:
                if parent.meta_blueprint is not None:
                    self._chamar_gancho(parent.meta_blueprint, "on_extend",
                                        [parent, blueprint], node)
            devolvido = self._chamar_gancho(meta_bp, "on_forge", [blueprint], node)
            if devolvido is not None and devolvido is not _SEM_MAGICO:
                valor = devolvido

        # Decoradores do blueprint. Um deles pode devolver outro valor
        # (uma fabrica, um proxy) e e esse que fica com o nome.
        bp_env.set_local(node.name, valor)
        valor = self._aplicar_decoradores(valor, node, env)
        bp_env.set_local(node.name, valor)
        env.set_local(node.name, valor)
        return valor

    # ── Declaracao: as pecas ─────────────────────────────────

    def _conferir_mae(self, node, mae):
        """'final' e 'sealed' decidem quem pode herdar; 'contract' nao se herda."""
        if mae.e_contrato:
            raise TypeError_(
                f"Blueprint '{node.name}' extends '{mae.name}', which is a "
                f"contract.",
                node.line, node.column,
                nota="a contract is adopted, not inherited: it has no code to "
                     "inherit",
                dica=f"write  blueprint {node.name} with {mae.name}:",
                doc="oop/contratos")
        if mae.e_final:
            raise FinalBlueprintError(
                f"Blueprint '{node.name}' cannot extend '{mae.name}', which is "
                f"declared final.",
                node.line, node.column,
                nota=f"'final blueprint {mae.name}' closes the hierarchy",
                dica=f"keep a {mae.name} in a field instead of inheriting from "
                     f"it — composition works where inheritance was forbidden",
                doc="oop/modificadores")
        if mae.e_selado and (mae.arquivo or "") != (self.filename or ""):
            raise SealedBlueprintError(
                f"Blueprint '{node.name}' cannot extend '{mae.name}' from this "
                f"file.",
                node.line, node.column,
                nota=f"'sealed blueprint {mae.name}' only accepts children "
                     f"declared in {mae.arquivo or 'its own file'}",
                dica="declare the child next to the parent, or remove 'sealed'",
                doc="oop/modificadores")

    def _metaclasse_de(self, node, maes, env):
        """A metaclasse do blueprint: a de 'using', ou a herdada.

        Duas metaclasses so convivem se uma descende da outra. Sem essa
        regra, uma filha governada por 'Auditoria' de uma mae governada
        por 'Registro' teria de escolher qual regra ignorar — e ignorar
        a da mae quebra o que a mae prometeu a quem a usa.
        """
        propria = None
        nome = getattr(node, "metaclass", "") or ""
        if nome:
            try:
                propria = self._valor_pontuado(nome, env)
            except NameError_:
                raise MetaclassError(
                    f"Blueprint '{node.name}' uses '{nome}', which does not "
                    f"exist.", node.line, node.column,
                    dica=f"declare 'meta blueprint {nome}:' before it",
                    doc="oop/metaclasses") from None
            if not isinstance(propria, DFBlueprint) or not propria.e_meta:
                raise MetaclassError(
                    f"'{nome}' is not a metaclass.", node.line, node.column,
                    nota="'using' names a 'meta blueprint' — the blueprint that "
                         "governs how others are built",
                    dica=f"declare it as  meta blueprint {nome}:",
                    doc="oop/metaclasses")
        for mae in maes:
            herdada = mae.meta_blueprint
            if herdada is None:
                continue
            if propria is None:
                propria = herdada
            elif herdada is not propria and herdada not in propria.linhagem():
                raise MetaclassError(
                    f"Blueprint '{node.name}' uses '{propria.name}', but its "
                    f"parent '{mae.name}' is governed by '{herdada.name}'.",
                    node.line, node.column,
                    nota="a child keeps the rules of its parent's metaclass",
                    dica=f"make '{propria.name}' extend '{herdada.name}'",
                    doc="oop/metaclasses")
        return propria

    def _acao_de_metodo(self, stmt, node, bp_env):
        """A DFAction de um metodo, com os extras de contrato e trava."""
        action = DFAction(
            name=stmt.name, params=stmt.params,
            defaults=stmt.defaults, body=stmt.body,
            closure=bp_env, is_async=stmt.is_async,
            param_types=getattr(stmt, 'param_types', None),
            return_type=getattr(stmt, 'return_type', ""),
            is_generator=getattr(stmt, 'is_generator', False),
            # O <T> do blueprint vale dentro dos metodos dele:
            # 'blueprint Pilha<T>' com 'action por(x: T)' e o
            # caso normal de um generico, e sem isto o T do
            # metodo seria um blueprint inexistente.
            type_params=(list(getattr(stmt, 'type_params', None) or [])
                         + list(getattr(node, 'type_params', None) or [])),
            # o limite do metodo vence o do blueprint, se os dois
            # usarem o mesmo nome — o mais proximo manda.
            type_bounds={**(getattr(node, 'type_bounds', None) or {}),
                         **(getattr(stmt, 'type_bounds', None) or {})},
        )
        action.is_abstract = getattr(stmt, 'is_abstract', False)
        action.owner = node.name
        action.visibilidade = getattr(stmt, 'visibility', 'public')
        self._extras_da_declaracao(action, stmt)
        return action

    def _extras_da_declaracao(self, action, stmt):
        """Pos-condicoes e 'exclusive' viram extras da acao."""
        promessas = list(getattr(stmt, 'postconditions', None) or [])
        exclusiva = bool(getattr(stmt, 'is_exclusive', False))
        if not promessas and not exclusiva:
            return
        if stmt.is_async and (promessas or exclusiva):
            palavra = "promises" if promessas else "exclusive"
            raise TypeError_(
                f"'{stmt.name}' is async, and '{palavra}' needs the result "
                f"in hand.", stmt.line, stmt.column,
                nota="an async action returns a task at once; the work "
                     "finishes later, on another thread",
                dica="check the result where it is awaited, or use "
                     "Arcane.Concurrent.mutex inside the action",
                doc="oop/contratos")
        extras = objetos.Extras()
        extras.promessas = promessas
        extras.antes = [n for p in promessas for n in objetos.nos_before(p)]
        extras.exclusivo = exclusiva
        action.extras = extras

    def _grupo_de_sobrecarga(self, nome, variante, anterior, stmt):
        """Junta a variante ao grupo de 'overload' com esse nome."""
        if anterior is None or anterior.extras is None or not anterior.extras.variantes:
            grupo = DFAction(name=nome, params=[], defaults={}, body=[],
                             closure=variante.closure)
            grupo.extras = objetos.Extras()
            grupo.extras.variantes = []
            grupo.extras.grupo = nome
            grupo.owner = getattr(variante, "owner", None)
            grupo.visibilidade = getattr(variante, "visibilidade", "public")
        else:
            grupo = DFAction(name=nome, params=[], defaults={}, body=[],
                             closure=anterior.closure)
            grupo.extras = objetos.Extras()
            grupo.extras.variantes = list(anterior.extras.variantes)
            grupo.extras.grupo = nome
            grupo.owner = getattr(variante, "owner", None)
            grupo.visibilidade = getattr(anterior, "visibilidade", "public")
        substituida = False
        for i, outra in enumerate(grupo.extras.variantes):
            if objetos.mesma_assinatura(outra, variante):
                if getattr(outra, "owner", None) != getattr(variante, "owner", None):
                    # a filha sobrescreve a variante herdada com a mesma forma
                    grupo.extras.variantes[i] = variante
                    substituida = True
                    break
                raise AmbiguousOverloadError(
                    f"Two overloads of '{nome}' have the same signature: "
                    f"{objetos.assinatura(variante)}.",
                    stmt.line, stmt.column,
                    nota="no call could ever choose between them",
                    dica="change a parameter type, or remove one of them",
                    doc="oop/sobrecarga")
        if not substituida:
            grupo.extras.variantes.append(variante)
        return grupo

    def _erro_override(self, node, stmt, nome, candidatos, especie="action"):
        import difflib
        perto = difflib.get_close_matches(nome, sorted(candidatos), n=1, cutoff=0.6)
        raise OverrideTargetError(
            f"'{node.name}.{nome}' is marked override, but no parent, trait or "
            f"contract has a {'property' if especie == 'property' else 'method'} "
            f"'{nome}'.",
            stmt.line, stmt.column,
            nota="'override' promises that this member replaces an inherited one",
            dica=(f"did you mean '{perto[0]}'?" if perto
                  else "remove 'override', or fix the name to match the parent"),
            doc="oop/modificadores")

    def _gravar_metadados_de_membro(self, nome, decoradores, env, alvo=None,
                                    blueprint=None):
        """'@Coluna("email")' sobre um membro: anotacao, lida por Reflexo/Meta.

        Num CAMPO o decorador nao embrulha nada — nao ha valor para
        embrulhar na declaracao. Ele grava, e quem precisa le: o ORM, o
        conteiner de injecao, o validador.
        """
        for deco in decoradores:
            args = [self.evaluate(a, env) for a in (deco.args or [])]
            kwargs = {k: self.evaluate(v, env)
                      for k, v in (deco.kwargs or {}).items()}
            if alvo is not None:
                self._gravar_metadado(alvo, deco.name, args, kwargs)
            if blueprint is not None:
                blueprint.metadados_de_campo.setdefault(nome, []).append(
                    {"nome": deco.name, "args": list(args), "kwargs": dict(kwargs)})

    def _montar_vigias(self, blueprint, maes, invariantes, meta_bp):
        """Invariantes da linhagem e ganchos da metaclasse, ou None."""
        todas = []
        for mae in maes:
            if mae.vigias is not None:
                for item in mae.vigias.invariantes:
                    if item not in todas:
                        todas.append(item)
        todas.extend(invariantes)
        ganchos = {}
        instancia = None
        if meta_bp is not None:
            for nome in objetos.GANCHOS_DE_META:
                acao = Interpreter._achar_magico_no_molde(meta_bp, nome)
                if acao is not None:
                    ganchos[nome] = acao
            if ganchos:
                instancia = self._instancia_de_meta(meta_bp)
        if not todas and not ganchos:
            return None
        return objetos.Vigias(todas, ganchos, instancia)

    def _instancia_de_meta(self, meta_bp):
        """A instancia unica do meta blueprint — o 'self' dos ganchos.

        Uma so, e compartilhada por todos os blueprints que ele governa:
        e o que deixa um registro de classes morar em 'self.classes'.
        """
        if meta_bp.instancia_meta is None:
            meta_bp.instancia_meta = self._instanciar(
                meta_bp, [], {}, self._no_interno(), meta_bp.env)
        return meta_bp.instancia_meta

    def _chamar_gancho(self, meta_bp, nome, args, node):
        """Roda um gancho da metaclasse; _SEM_MAGICO quando ela nao o tem."""
        acao = Interpreter._achar_magico_no_molde(meta_bp, nome)
        if acao is None:
            return _SEM_MAGICO
        por_thread = self._por_thread
        if getattr(por_thread, "em_gancho", False):
            # um gancho que le um campo do objeto nao dispara o gancho de
            # novo: seria recursao sem fim, e nenhum 'on_read' quer isso
            return _SEM_MAGICO
        por_thread.em_gancho = True
        try:
            return self._call_action(acao, list(args), {}, node, None,
                                     instance=self._instancia_de_meta(meta_bp))
        finally:
            por_thread.em_gancho = False

    def _gancho_de_vigia(self, vigias, nome, args, node):
        acao = vigias.ganchos.get(nome)
        if acao is None:
            return _SEM_MAGICO
        por_thread = self._por_thread
        if getattr(por_thread, "em_gancho", False):
            return _SEM_MAGICO
        por_thread.em_gancho = True
        try:
            return self._call_action(acao, list(args), {}, node, None,
                                     instance=vigias.meta)
        finally:
            por_thread.em_gancho = False

    def _registrar_blueprint(self, blueprint):
        import weakref as _weakref
        registro = getattr(self, "blueprints_declarados", None)
        if registro is None:
            registro = self.blueprints_declarados = []
        registro.append(_weakref.ref(blueprint))

    @staticmethod
    def _achar_magico_no_molde(molde, nome):
        """O metodo na linhagem de um BLUEPRINT (e nao de uma instancia)."""
        for ancestral in molde.linhagem():
            acao = ancestral.methods.get(nome)
            if acao is not None:
                return acao
        return None

    def _conferir_contrato(self, blueprint, node, env):
        """Um blueprint concreto precisa implementar tudo o que prometeu."""
        faltando = blueprint.pendencias_abstratas()
        faltando.update({n: o for n, o in
                         getattr(blueprint, 'origem_abstrata', {}).items()
                         if n in faltando})
        if not faltando:
            return

        itens = sorted(faltando.items())
        linhas = [f"    {nome}()  — declarado em '{origem}'"
                  for nome, origem in itens]
        plural = "methods" if len(itens) > 1 else "method"
        raise TraitContractError(
            f"Blueprint '{node.name}' does not implement {len(itens)} "
            f"abstract {plural}:\n" + "\n".join(linhas) +
            f"\n    Implement {'them' if len(itens) > 1 else 'it'}, or mark "
            f"'{node.name}' as 'abstract blueprint' if it is not meant to be "
            f"spawned directly.",
            node.line, node.column)

    def _conferir_assinaturas(self, blueprint, adotados, node):
        """O que um CONTRATO exige alem do nome: aridade e propriedades.

        Um metodo com o nome certo que pede um argumento a mais quebra
        todo codigo escrito contra o contrato — e o nome certo e o que
        faz a quebra passar despercebida ate a primeira chamada.
        """
        campos = {c[0] for c in blueprint.fields_decl} | set(blueprint.constructor_params)
        for contrato in adotados:
            if not contrato.e_contrato:
                continue
            for nome, assinatura in contrato.assinaturas.items():
                impl = blueprint.methods.get(nome)
                if not isinstance(impl, DFAction) or getattr(impl, "is_abstract", False):
                    continue
                if impl.extras is not None and impl.extras.variantes:
                    if not any(self._aridade_compativel(v, assinatura)
                               for v in impl.extras.variantes):
                        self._erro_de_assinatura(blueprint, contrato, nome,
                                                 impl.extras.variantes[0],
                                                 assinatura, node)
                    continue
                if not self._aridade_compativel(impl, assinatura):
                    self._erro_de_assinatura(blueprint, contrato, nome, impl,
                                             assinatura, node)
            for prop in contrato.propriedades_exigidas:
                tem = blueprint.buscar_propriedade(prop)
                if (tem is not None and 'get' in tem) or prop in campos:
                    continue
                raise TraitContractError(
                    f"Blueprint '{node.name}' does not provide the property "
                    f"'{prop}' required by contract '{contrato.name}'.",
                    node.line, node.column,
                    dica=f"declare  get {prop}():  or a field named '{prop}'",
                    doc="oop/contratos")

    @staticmethod
    def _aridade_compativel(impl, assinatura):
        imin, imax = objetos.aridade(impl)
        smin, smax = objetos.aridade(assinatura)
        return imin <= smin and imax >= smax

    def _erro_de_assinatura(self, blueprint, contrato, nome, impl, assinatura, node):
        raise SignatureMismatchError(
            f"'{blueprint.name}.{nome}' does not match the signature required "
            f"by contract '{contrato.name}'.",
            node.line, node.column,
            nota=f"the contract declares  {objetos.assinatura(assinatura)}\n"
                 f"      the blueprint has   {objetos.assinatura(impl)}",
            dica="accept every argument the contract passes — extra parameters "
                 "need a default",
            doc="oop/contratos")

    def exec_ContractDeclaration(self, node, env):
        """Um contrato e um blueprint que so promete, e nunca nasce."""
        maes = []
        for nome in node.parents:
            try:
                mae = self._valor_pontuado(nome, env)
            except NameError_:
                raise UnknownTraitError(
                    f"Contract '{node.name}' extends '{nome}', which does not "
                    f"exist.", node.line, node.column,
                    dica=f"declare 'contract {nome}:' first",
                    doc="oop/contratos") from None
            if not isinstance(mae, DFBlueprint) or not mae.e_contrato:
                raise TypeError_(
                    f"Contract '{node.name}' extends '{nome}', which is not a "
                    f"contract.", node.line, node.column,
                    nota="a contract extends only other contracts",
                    dica="a blueprint adopts a contract with 'with'",
                    doc="oop/contratos")
            maes.append(mae)

        assinaturas, exigidas, abstratos, origem = {}, set(), set(), {}
        contratos = set()
        for mae in maes:
            assinaturas.update(mae.assinaturas)
            exigidas |= mae.propriedades_exigidas
            abstratos |= mae.abstract_methods
            origem.update(getattr(mae, "origem_abstrata", {}))
            contratos |= mae.contratos_todos | {mae.name}
        for membro in node.members:
            if isinstance(membro, ast.PropertyDeclaration):
                exigidas.add(membro.name)
                continue
            acao = DFAction(
                name=membro.name, params=membro.params, defaults=membro.defaults,
                body=[], closure=env, is_async=membro.is_async,
                param_types=getattr(membro, "param_types", None),
                return_type=getattr(membro, "return_type", ""),
                is_generator=getattr(membro, "is_generator", False),
                type_params=(list(getattr(membro, "type_params", None) or [])
                             + list(node.type_params or [])))
            acao.is_abstract = True
            acao.owner = node.name
            assinaturas[membro.name] = acao
            abstratos.add(membro.name)
            origem[membro.name] = node.name

        contrato = DFBlueprint(name=node.name, parents=[], methods={},
                               statics={}, env=env, is_abstract=True,
                               abstract_methods=abstratos)
        contrato.e_contrato = True
        contrato.assinaturas = assinaturas
        contrato.propriedades_exigidas = exigidas
        contrato.origem_abstrata = origem
        contrato.contratos_todos = frozenset(contratos)
        contrato.arquivo = self.filename or ""
        contrato.type_params = list(node.type_params or [])
        self._registrar_blueprint(contrato)
        env.set_local(node.name, contrato)
        valor = self._aplicar_decoradores(contrato, node, env)
        env.set_local(node.name, valor)
        return valor

    def exec_AugmentDeclaration(self, node, env):
        """augment Nome: acrescenta membros, sem substituir nenhum."""
        try:
            alvo = self._valor_pontuado(node.name, env)
        except NameError_:
            raise AugmentError(
                f"Cannot augment '{node.name}': it does not exist.",
                node.line, node.column,
                dica=f"declare 'blueprint {node.name}' before augmenting it",
                doc="oop/augment") from None
        if not isinstance(alvo, DFBlueprint) or alvo.e_contrato or alvo.e_meta:
            raise AugmentError(
                f"Cannot augment '{node.name}': only a blueprint accepts "
                f"'augment'.", node.line, node.column,
                nota=f"'{node.name}' is {self._nome_do_tipo(alvo)}",
                dica="to grow a contract, declare a new one that extends it",
                doc="oop/augment")
        if alvo.e_final:
            raise AugmentError(
                f"Cannot augment '{alvo.name}': it is declared final.",
                node.line, node.column,
                nota="final promises the blueprint is complete",
                dica="write an action that receives the object instead",
                doc="oop/augment")
        mesmo_arquivo = (alvo.arquivo or "") == (self.filename or "")
        if alvo.e_selado and not mesmo_arquivo:
            raise AugmentError(
                f"Cannot augment '{alvo.name}' from this file: it is sealed.",
                node.line, node.column,
                dica=f"augment it in {alvo.arquivo or 'its own file'}",
                doc="oop/augment")

        # Do mesmo arquivo, o escopo e o do blueprint — os membros privados
        # dele ficam visiveis, como se estivessem escritos la. De outro
        # arquivo, NAO: um 'augment' nao pode virar a porta dos fundos para
        # o que o autor marcou como private.
        nome_escopo = (f"<blueprint {alvo.name}>" if mesmo_arquivo
                       else f"<augment {alvo.name}>")
        escopo = env.child(nome_escopo)
        escopo.set_local(alvo.name, alvo)

        def ja_existe(nome):
            return (nome in alvo.statics or nome in alvo.properties
                    or nome in {c[0] for c in alvo.fields_decl}
                    or (nome in alvo.methods
                        and not getattr(alvo.methods[nome], "is_abstract", False))
                    or any(nome in bp.methods for bp in alvo.linhagem()[1:]
                           if not getattr(bp.methods.get(nome), "is_abstract", False)))

        def recusar(nome, stmt):
            raise AugmentError(
                f"'augment {alvo.name}' cannot replace '{nome}', which already "
                f"exists.", stmt.line, stmt.column,
                nota="augment only adds; replacing is what inheritance is for",
                dica=f"declare a child blueprint that overrides '{nome}'",
                doc="oop/augment")

        novos_nao_publicos = set()
        for stmt in node.body:
            if isinstance(stmt, ast.ActionDeclaration):
                if ja_existe(stmt.name):
                    recusar(stmt.name, stmt)
                acao = self._acao_de_metodo(stmt, ast.BlueprintDeclaration(
                    name=alvo.name, type_params=getattr(alvo, "type_params", [])),
                    escopo)
                acao = self._aplicar_decoradores(acao, stmt, escopo)
                acao.dono = alvo
                alvo.methods[stmt.name] = acao
                alvo.abstract_methods.discard(stmt.name)
                alvo.visibility[stmt.name] = stmt.visibility
                if stmt.visibility != "public":
                    novos_nao_publicos.add(stmt.name)
                if stmt.is_static:
                    alvo.static_methods.add(stmt.name)
                    alvo.statics[stmt.name] = acao
            elif isinstance(stmt, ast.PropertyDeclaration):
                if stmt.name in alvo.methods or \
                        (alvo.buscar_propriedade(stmt.name) or {}).get(stmt.kind):
                    recusar(stmt.name, stmt)
                acao = DFAction(name=stmt.name,
                                params=[stmt.param] if stmt.kind == 'set' else [],
                                defaults={}, body=stmt.body, closure=escopo,
                                return_type=stmt.return_type)
                acao.dono = alvo
                acao.owner = alvo.name
                alvo.properties.setdefault(stmt.name, {})[stmt.kind] = acao
                if stmt.is_lazy:
                    alvo.properties[stmt.name]['lazy'] = True
                alvo.visibility[stmt.name] = stmt.visibility
                if stmt.visibility != "public":
                    novos_nao_publicos.add(stmt.name)
            elif isinstance(stmt, ast.OperatorDeclaration):
                if stmt.symbol in alvo.operators:
                    recusar(f"operator {stmt.symbol}", stmt)
                acao = DFAction(name=f"operator{stmt.symbol}", params=[stmt.param],
                                defaults={}, body=stmt.body, closure=escopo)
                acao.dono = alvo
                alvo.operators[stmt.symbol] = acao
            elif isinstance(stmt, ast.StaticDeclaration):
                if ja_existe(stmt.name):
                    recusar(stmt.name, stmt)
                alvo.statics[stmt.name] = self.evaluate(stmt.value, escopo)
                if stmt.is_steady:
                    alvo.constantes.add(stmt.name)
            else:
                raise AugmentError(
                    f"'augment {alvo.name}' accepts actions, properties, operators "
                    f"and static fields.", stmt.line, stmt.column,
                    nota="a new instance field would leave the objects that "
                         "already exist without it",
                    dica="declare the field in the blueprint itself",
                    doc="oop/augment")
        if novos_nao_publicos:
            alvo.nao_publicos = frozenset(alvo.nao_publicos | novos_nao_publicos)
        if node.fields_decl:
            raise AugmentError(
                f"'augment {alvo.name}' cannot add the field "
                f"'{node.fields_decl[0][0]}'.", node.line, node.column,
                nota="the objects that already exist would not have it",
                dica="declare the field in the blueprint itself",
                doc="oop/augment")
        alvo.finalizador = alvo.finalizador or next(
            (alvo.methods[n] for n in ("teardown", "__del__")
             if isinstance(alvo.methods.get(n), DFAction)), None)
        alvo.leitura_magica = alvo.leitura_magica or "__getattribute__" in alvo.methods
        alvo.escrita_magica = alvo.escrita_magica or "__setattr__" in alvo.methods
        alvo.esquecer_caches()
        return alvo

    # ── Contratos em execucao: invariant, expects, promises ──

    def exec_InvariantStatement(self, node, env):
        raise RuntimeError_(
            "'invariant' only has meaning in the body of a blueprint.",
            node.line, node.column,
            nota="an invariant describes an object, and is checked after every "
                 "public operation on it",
            dica="inside an action, use  expects  for the input or  assert",
            doc="oop/contratos")

    def exec_ExpectsStatement(self, node, env):
        if self._verdade(self.evaluate(node.condition, env)):
            return None
        quadro = self._call_stack[-1].name if self._call_stack else "the program"
        mensagem = (self._to_str(self.evaluate(node.message, env))
                    if node.message is not None else "")
        raise PreconditionError(
            f"Precondition of '{quadro}' failed"
            + (f": {mensagem}" if mensagem else "."),
            node.line, node.column,
            nota="'expects' checks what the CALLER must provide — the "
                 "mistake is in the call, not in the action",
            dica="check the arguments at the call site",
            doc="oop/contratos")

    def exec_PromisesStatement(self, node, env):
        raise RuntimeError_(
            "'promises' has to be at the top level of an action body.",
            node.line, node.column,
            nota="it runs when the action returns, with 'outcome' bound to the "
                 "returned value — inside a block it would have no single exit",
            dica="move it next to the other statements at the start of the action",
            doc="oop/contratos")

    def eval_BeforeExpression(self, node, env):
        try:
            antes = env.get("__antes__")
        except NameError_:
            antes = None
        if not isinstance(antes, dict) or id(node) not in antes:
            raise RuntimeError_(
                "'before(…)' only has meaning inside 'promises'.",
                node.line, node.column, doc="oop/contratos")
        return antes[id(node)]

    def _conferir_promessas(self, action, extras, args, kwargs, node,
                            instance, resultado, antes):
        estado = (objetos.estado_de(instance)
                  if instance is not None and instance.__class__ in _COM_VIGIAS
                  else None)
        if estado is not None:
            estado.profundidade += 1
        try:
            self._avaliar_promessas(action, extras, args, kwargs, node,
                                    instance, resultado, antes)
        finally:
            if estado is not None:
                estado.profundidade -= 1

    def _avaliar_promessas(self, action, extras, args, kwargs, node,
                           instance, resultado, antes):
        escopo = self._ligar_parametros(action, args, kwargs, node, instance)
        escopo.set_local("outcome", resultado)
        escopo.set_local("__antes__", antes or {})
        for promessa in extras.promessas:
            if self._verdade(self.evaluate(promessa.condition, escopo)):
                continue
            mensagem = (self._to_str(self.evaluate(promessa.message, escopo))
                        if promessa.message is not None else "")
            erro = PostconditionError(
                f"Postcondition of '{action.name}' failed"
                + (f": {mensagem}" if mensagem else "."),
                promessa.line, promessa.column,
                nota=f"the action returned {self._to_str(resultado)} — 'promises' "
                     f"checks what the ACTION guarantees, so the mistake is inside it",
                dica="fix the action body; the caller did its part",
                doc="oop/contratos")
            erro.filename = getattr(action, "arquivo", "") or self.filename
            raise erro

    def _conferir_invariantes(self, obj, node, depois_de=""):
        vigias = obj.blueprint.vigias
        if vigias is None or not vigias.invariantes:
            return
        # Conferir conta como estar DENTRO do objeto: uma invariante que
        # chama 'self.area()' dispararia a conferencia de novo, e de novo —
        # recursao sem fim sobre o caso mais natural de se escrever.
        estado = objetos.estado_de(obj)
        estado.profundidade += 1
        try:
            self._avaliar_invariantes(obj, node, depois_de, vigias)
        finally:
            estado.profundidade -= 1

    def _avaliar_invariantes(self, obj, node, depois_de, vigias):
        for stmt, escopo_bp, dono in vigias.invariantes:
            escopo = escopo_bp.child(f"<invariant {dono}>")
            escopo.set_local("self", obj)
            escopo.set_local("this", obj)
            if self._verdade(self.evaluate(stmt.condition, escopo)):
                continue
            mensagem = (self._to_str(self.evaluate(stmt.message, escopo))
                        if stmt.message is not None else "")
            quando = (f"after '{depois_de}'" if depois_de else "after construction")
            erro = InvariantError(
                f"'{obj.blueprint.name}' broke an invariant {quando}"
                + (f": {mensagem}" if mensagem else "."),
                getattr(node, "line", 0) or stmt.line,
                getattr(node, "column", 0) or stmt.column,
                nota=f"the invariant declared in '{dono}' at line {stmt.line} "
                     f"no longer holds",
                dica="an invariant must hold after every public operation; "
                     "the operation above left the object inconsistent",
                doc="oop/contratos")
            raise erro

    #: O que NÃO existe dentro de um 'comptime'. Sem esta lista, "tempo
    #: de compilação" seria só "mais cedo": um 'out' imprimiria na carga,
    #: um 'adopt' traria E/S, e uma thread deixaria trabalho correndo por
    #: baixo do programa que ainda não começou.
    _FORA_DO_COMPTIME = {
        "OutStatement": "escrever na saída",
        "AdoptStatement": "adotar um módulo",
        "ThreadBlock": "abrir uma thread",
        "ParallelBlock": "rodar em paralelo",
        "InExpression": "ler da entrada",
        "ServerDeclaration": "subir um servidor",
        "IgniteStatement": "subir um servidor",
        "WaitStatement": "esperar",
    }

    def _rodar_comptime(self, corpo):
        """Roda os blocos 'comptime' do topo, na ordem, antes do programa."""
        for no in corpo:
            if isinstance(no, ast.ComptimeBlock):
                self.exec_ComptimeBlock(no, self.global_env)

    def exec_ComptimeBlock(self, node: ast.ComptimeBlock, env):
        """O corpo roda uma vez, numa caixa, e o que ele define fica.

        Rodar de novo quando o programa chega na linha seria calcular
        duas vezes — e o ponto de 'comptime' é calcular uma.
        """
        if getattr(node, "_ja_rodou", False):
            return None
        node._ja_rodou = True
        self._recusar_impuro(node.body)
        caixa = Environment(parent=self.global_env, name="<comptime>")
        anterior = self.compilar_corpos
        try:
            # Sem compilação de corpos: o ganho não existe numa passada
            # única, e o depurador precisa enxergar o que roda aqui.
            self.compilar_corpos = False
            self.exec_block(node.body, caixa)
        except DataForgeError as erro:
            raise RuntimeError_(
                f"o 'comptime' falhou: {getattr(erro, 'message', erro)}",
                node.line, node.column,
                nota="ele roda na carga, antes da primeira linha do programa",
                dica="conserte a conta, ou tire o 'comptime' se ela precisa "
                     "de dado que só existe em execução",
                doc="metaprogramacao/comptime") from None
        finally:
            self.compilar_corpos = anterior
        # O que a caixa definiu vira CONSTANTE do programa.
        for nome, valor in caixa.variables.items():
            if nome.startswith("__"):
                continue
            if nome in caixa.constants:
                self.global_env.define_steady(nome, valor)
            else:
                self.global_env.set_local(nome, valor)
        return None

    def _recusar_impuro(self, corpo, profundidade=0):
        """Varre o corpo do 'comptime' e recusa o que não é conta."""
        if profundidade > 12:
            return
        for no in corpo or []:
            nome = type(no).__name__
            motivo = self._FORA_DO_COMPTIME.get(nome)
            if motivo:
                raise RuntimeError_(
                    f"'comptime' não pode {motivo}.",
                    getattr(no, "line", 0), getattr(no, "column", 0),
                    nota="ele é uma conta feita na carga; E/S e módulos "
                         "pertencem ao programa",
                    dica="mova esta linha para fora do 'comptime'",
                    doc="metaprogramacao/comptime")
            for campo, valor in vars(no).items():
                if campo in ("line", "column"):
                    continue
                if isinstance(valor, list):
                    self._recusar_impuro(
                        [i for i in valor if isinstance(i, ast.ASTNode)],
                        profundidade + 1)
                elif isinstance(valor, ast.ASTNode):
                    self._recusar_impuro([valor], profundidade + 1)

    def exec_TypeDeclaration(self, node: ast.TypeDeclaration, env):
        """'type Nome := …' — registra o tipo; 'opaque' tambem cria o nome.

        Um tipo transparente e so uma CONFERENCIA: nenhum valor muda de
        forma, e por isso nada que ja funcionava deixa de funcionar. Um
        tipo opaco e um VALOR, e o nome dele passa a ser a unica porta de
        entrada — e ela valida.
        """
        tipo = _TiposNomeados.TipoNomeado(
            nome=node.name, especie=node.especie, partes=node.partes,
            parametros=node.type_params, regra=node.regra,
            regra_texto=node.regra_texto, opaco=node.opaco,
            escopo=env, arquivo=self.filename)
        self.tipos_nomeados.declarar(tipo)
        if node.opaco:
            env.set_local(node.name, self._construtor_de_opaco(tipo))
        return None

    def _construtor_de_opaco(self, tipo):
        """'Cpf(texto)' — a unica forma de existir um valor daquele tipo."""
        def construir(valor=None):
            valor = _TiposNomeados.desembrulhar(valor)
            self._conferir_base_e_regra(tipo, valor, f"{tipo.nome}(…)",
                                        self._no_interno())
            return Opaco(valor, tipo.nome)
        construir.__name__ = tipo.nome
        construir.__df_tipo_opaco__ = tipo.nome
        return construir

    def _conferir_base_e_regra(self, tipo, valor, o_que, node,
                               parametros_de_tipo=(), limites=None):
        """A base ANTES da regra, sempre.

        'len(valor)' sobre um numero levantaria um erro do interpretador,
        e a mensagem falaria de 'len' em vez do tipo que a pessoa
        escreveu.
        """
        base = tipo.base
        try:
            valor = self._check_type(valor, base, o_que, node,
                                     parametros_de_tipo, limites)
        except TypeError_ as erro:
            # O nome que a pessoa escreveu tem de aparecer: sem isto, um
            # 'x: Id := "a"' respondia "declared as Integer", e quem leu
            # o codigo procura 'Id' no arquivo e nao acha nada.
            if tipo.nome == base:
                raise
            raise TypeError_(
                f"{o_que} declared as {tipo.nome} (a {base}) but got "
                f"{self._type_of(valor)}",
                erro.line, erro.column,
                nota=getattr(erro, "nota", "") or f"{tipo.nome} is a {base}",
                dica=getattr(erro, "dica", ""), doc="tipos-nomeados") from None
        if tipo.regra is not None and not self._regra_aceita(tipo, valor):
            raise _TiposNomeados.erro_de_regra(
                tipo, self._to_repr(valor), o_que, node)
        return valor

    def _regra_aceita(self, tipo, valor):
        """A regra do 'where', com 'valor' ligado ao que esta entrando."""
        escopo = Environment(parent=tipo.escopo or self.global_env,
                             name=f"<type {tipo.nome}>")
        escopo.set_local("valor", _TiposNomeados.desembrulhar(valor))
        for parametro, ligado in tipo.ligacoes.items():
            escopo.set_local(parametro, ligado)
        return self._verdade(self.evaluate(tipo.regra, escopo))

    def _checar_tipo_nomeado(self, tipo, value, declared, what, node,
                             parametros_de_tipo=(), limites=None):
        """Uniao, intersecao, refinamento e opaco — as quatro conferencias."""
        if tipo.opaco:
            if isinstance(value, Opaco) and value.tipo == tipo.nome:
                return value
            raise _TiposNomeados.erro_de_opaco(
                tipo, self._type_of(value), what, node)
        if tipo.especie == UNIAO:
            for parte in tipo.partes:
                try:
                    return self._check_type(value, parte, what, node,
                                            parametros_de_tipo, limites)
                except TypeError_:
                    continue
            raise _TiposNomeados.erro_de_uniao(
                tipo.nome, tipo.partes, self._type_of(value), what, node)
        if tipo.especie == INTERSECAO:
            for parte in tipo.partes:
                try:
                    self._check_type(value, parte, what, node,
                                     parametros_de_tipo, limites)
                except TypeError_:
                    raise _TiposNomeados.erro_de_intersecao(
                        tipo.nome, parte, self._type_of(value), what,
                        node) from None
            return value
        return self._conferir_base_e_regra(tipo, value, what, node,
                                           parametros_de_tipo, limites)

    def _generico_do_usuario(self, base):
        """O record, enum ou blueprint com esse nome — se ele for genérico."""
        nome = base.rsplit(".", 1)[-1]
        alvo = self.global_env.variables.get(nome)
        if alvo is None:
            return None
        if getattr(alvo, "type_params", ()):
            return alvo
        return None

    def _conferir_generico_do_usuario(self, alvo, value, declared, what, node):
        """'Caixa<Integer>': o valor é um Caixa, e o conteúdo dele confere.

        O argumento chega ao CAMPO: um record genérico sem esta conferência
        prometeria 'Caixa<Integer>' e aceitaria um texto lá dentro — o
        parâmetro viraria comentário.
        """
        base, argumentos = _partir_tipo(declared)
        self._check_type(value, base.rsplit(".", 1)[-1], what, node)
        troca = dict(zip(alvo.type_params, argumentos))
        # O carimbo: o objeto passa a CARREGAR o vinculo, e dai em diante
        # toda escrita de campo e conferida.
        #
        # O PRIMEIRO carimbo vence. 'larga: Caixa<Number> := inteira' e
        # legitimo — a conferencia estrutural o aceita —, mas deixa-lo
        # reescrever o vinculo AFROUXARIA o objeto: escrever um Float ali
        # quebraria a vista 'inteira', que continua apontando para ele. E
        # a inseguranca classica da covariancia com objeto mutavel, e a
        # regra de primeiro-vence a fecha sem proibir o alargamento.
        if isinstance(value, DFInstance) and value._tipos is None and troca:
            value._tipos = troca
        if isinstance(alvo, DFRecord) and isinstance(value, DFRecordInstance):
            for campo, tipo_do_campo in alvo.field_types.items():
                esperado = troca.get(tipo_do_campo)
                if not esperado or campo not in value.values:
                    continue
                self._check_type(
                    value.values[campo], esperado,
                    f"field '{campo}' of {declared} in {what}", node)
        elif isinstance(value, DFInstance):
            declarados = Interpreter._tipos_de_campo_do_molde(alvo)
            for campo, valor_do_campo in list(value.fields.items()):
                # 'void' e campo AINDA SEM VALOR, e recusa-lo proibiria
                # 'spawn Caixa()' — a forma mais comum de criar um. A
                # primeira versao acusava 'declared as Integer but got
                # Void' em todo blueprint generico anotado, e o recurso
                # inteiro ficava inutilizavel.
                #
                # O preco: um campo que guarda 'void' DE PROPOSITO passa
                # sem conferencia. Nao ha como separar os dois casos sem
                # o objeto carregar "este campo foi escrito", e um falso
                # alarme no caminho comum e pior que esse silencio.
                if valor_do_campo is None:
                    continue
                esperado = troca.get(declarados.get(campo))
                if esperado:
                    self._check_type(
                        valor_do_campo, esperado,
                        f"field '{campo}' of {declared} in {what}", node)
        return value

    def _conferir_campo_generico(self, obj, membro, value, node):
        """'c.guardado := "texto"' num objeto vinculado a Caixa<Integer>.

        O vinculo vive no OBJETO, e nao na anotacao: sem isso, a
        conferencia acontecia so na fronteira (a atribuicao anotada) e
        toda escrita posterior passava calada — o parametro de tipo valia
        uma vez e depois era decoracao.
        """
        declarados = Interpreter._tipos_de_campo_do_molde(obj.blueprint)
        esperado = obj._tipos.get(declarados.get(membro))
        if esperado:
            self._check_type(
                value, esperado,
                f"field '{membro}' of "
                f"{obj.blueprint.name}<{', '.join(obj._tipos.values())}>",
                node)

    @staticmethod
    def _tipos_de_campo_do_molde(molde):
        """campo -> tipo declarado, do blueprint e da linhagem dele.

        Este ramo era CODIGO MORTO. Ele lia `alvo.tipos_dos_campos`, um
        atributo que nunca existiu: os nomes reais sao
        `tipos_do_cabecalho` (os parametros do cabecalho) e `fields_decl`
        (os campos do corpo). `getattr` com padrao devolvia `{}`, o laco
        nao conferia nada, e `Caixa<Integer>` recebendo um texto passava
        calada — o parametro de tipo virava comentario.

        E a falta nao dava erro em lugar nenhum, que e o que a fez
        sobreviver: a unica forma de nota-la era anotar um blueprint
        generico, e isso era erro de sintaxe (ver `parse_blueprint`).

        A linhagem entra porque um campo herdado e tao declarado quanto
        um proprio, e a mae e quem costuma declarar o generico.
        """
        # A ordem importa: o ANCESTRAL entra primeiro e o molde por
        # ultimo, para que o que a filha declara VENCA o que ela herda.
        # A primeira versao empilhava e a mae sobrescrevia a filha —
        # 'campo: T' na filha virava o 'campo: String' da mae, e a
        # conferencia passava a falar do tipo errado.
        ordem = []
        vistos = set()

        def visitar(atual):
            if atual is None or id(atual) in vistos:
                return
            vistos.add(id(atual))
            for mae in getattr(atual, "parents", None) or []:
                visitar(mae)
            ordem.append(atual)

        visitar(molde)

        tipos = {}
        for atual in ordem:
            for campo, tipo in (getattr(atual, "tipos_do_cabecalho",
                                        None) or {}).items():
                tipos[campo] = tipo
            for declarado in getattr(atual, "fields_decl", None) or ():
                if isinstance(declarado, (list, tuple)) and len(declarado) >= 2:
                    nome, tipo = declarado[0], declarado[1]
                    if tipo:
                        tipos[nome] = tipo
        return tipos

    def _checar_composto_anonimo(self, value, declared, what, node,
                                 parametros_de_tipo=(), limites=None):
        """'x: Integer | String' — a união sem nome, conferida igual."""
        especie, partes = _TiposNomeados.separar_uniao(declared)
        anonimo = _TiposNomeados.TipoNomeado(
            nome=declared, especie=especie, partes=partes)
        return self._checar_tipo_nomeado(anonimo, value, declared, what, node,
                                         parametros_de_tipo, limites)

    def _tipo_declarado(self, declared):
        """O 'type' com esse nome, ja resolvido o generico ('Par<Integer>')."""
        if not self.tipos_nomeados:
            return None, declared
        achado = self.tipos_nomeados.obter(declared)
        if achado is not None:
            return achado, declared
        if "<" in declared:
            base, argumentos = _partir_tipo(declared)
            molde = self.tipos_nomeados.obter(base)
            if molde is not None and molde.parametros:
                return _TiposNomeados.especializar(molde, argumentos), declared
        return None, declared

    def exec_TraitDeclaration(self, node: ast.TraitDeclaration, env):
        """Um trait e um blueprint so com contrato.

        Metodo com corpo vira implementacao padrao; metodo sem corpo vira
        exigencia — quem adotar o trait precisa implementar.
        """
        methods, properties, abstratos = {}, {}, set()
        estaticos = {}
        associados = {}
        origem_das_exigencias = {}

        # 'trait Editavel extends Legivel' — o que a mãe exige continua
        # exigido, e o que ela implementa vem junto. Sem isto, herdar um
        # trait era uma promessa que ninguém cobrava.
        maes = []
        for nome_da_mae in getattr(node, "parents", None) or []:
            mae = env.get(nome_da_mae) if env.has(nome_da_mae) else None
            if mae is None or not isinstance(mae, DFBlueprint):
                raise NameError_(
                    f"'trait {node.name} extends {nome_da_mae}': "
                    f"'{nome_da_mae}' is not a trait declared before this one.",
                    node.line, node.column,
                    dica="declare the parent trait above, or fix the name",
                    doc="oop/contratos")
            maes.append(mae)
            methods.update(mae.methods)
            properties.update(mae.properties or {})
            estaticos.update(mae.statics or {})
            associados.update(getattr(mae, "tipos_associados", None) or {})
            da_mae = getattr(mae, "origem_das_exigencias", None) or {}
            for exigido in mae.abstract_methods or ():
                origem_das_exigencias[exigido] = da_mae.get(exigido, mae.name)
            abstratos |= set(mae.abstract_methods or ())

        for stmt in node.methods:
            # 'type Item := Any' — o tipo associado; 'steady MAXIMO := 3'
            # — a constante associada. Quem implementa o trait recebe os
            # dois, e pode redeclarar o tipo com o que ele é de verdade.
            if isinstance(stmt, ast.TypeDeclaration):
                self.exec_TypeDeclaration(stmt, env)
                associados[stmt.name] = stmt.partes[0] if stmt.partes else "Any"
                continue
            if isinstance(stmt, ast.SteadyDeclaration):
                estaticos[stmt.name] = self.evaluate(stmt.value, env)
                continue
            if isinstance(stmt, ast.PropertyDeclaration):
                acao = DFAction(
                    name=stmt.name,
                    params=[stmt.param] if stmt.kind == 'set' else [],
                    defaults={}, body=stmt.body, closure=env)
                acao.owner = node.name
                properties.setdefault(stmt.name, {})[stmt.kind] = acao
                continue

            if not isinstance(stmt, ast.ActionDeclaration):
                continue

            # Sem corpo (ou so com o marcador abstract) = exigencia
            vazio = not stmt.body or getattr(stmt, 'is_abstract', False)
            if vazio:
                abstratos.add(stmt.name)
                origem_das_exigencias[stmt.name] = node.name

            action = DFAction(
                name=stmt.name, params=stmt.params,
                defaults=stmt.defaults, body=stmt.body,
                closure=env,
                param_types=getattr(stmt, 'param_types', None),
                return_type=getattr(stmt, 'return_type', ""),
            )
            action.is_abstract = vazio
            action.owner = node.name
            if not vazio:
                methods[stmt.name] = action

        blueprint = DFBlueprint(
            name=node.name, parents=[], methods=methods,
            statics=estaticos, env=env, properties=properties,
            is_abstract=True, abstract_methods=abstratos,
        )
        blueprint.e_trait = True
        blueprint.tipos_associados = associados
        blueprint.origem_das_exigencias = origem_das_exigencias
        blueprint.type_params = tuple(getattr(node, "type_params", ()) or ())
        blueprint.type_bounds = dict(getattr(node, "type_bounds", None) or {})
        #: Os traits de onde ele herdou — o 'check' e a mensagem de
        #: exigência não encontrada precisam saber de onde veio cada uma.
        blueprint.traits_herdados = [m.name for m in maes]
        blueprint.arquivo = self.filename or ""
        _carimbar_dono(blueprint)
        self._registrar_blueprint(blueprint)
        env.set_local(node.name, blueprint)
        return blueprint

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — RECORDS E ENUMS
    # ═══════════════════════════════════════════════════════

    def exec_RecordDeclaration(self, node, env):
        rec_env = env.child(f"<record {node.name}>")
        metodos = {}
        for nome, decl in node.methods.items():
            metodos[nome] = DFAction(
                name=nome, params=decl.params, defaults=decl.defaults,
                body=decl.body, closure=rec_env,
                param_types=getattr(decl, 'param_types', None),
                return_type=getattr(decl, 'return_type', ""))
        record = DFRecord(node.name, node.fields, metodos, rec_env,
                          type_params=getattr(node, "type_params", ()),
                          type_bounds=getattr(node, "type_bounds", None))
        rec_env.set_local(node.name, record)

        valor = self._aplicar_decoradores(record, node, env)
        env.set_local(node.name, valor)
        return valor

    def exec_EnumDeclaration(self, node, env):
        enum_env = env.child(f"<enum {node.name}>")
        membros = {}
        for indice, (nome, valor_node) in enumerate(node.members):
            valor = self.evaluate(valor_node, enum_env) if valor_node is not None else nome
            membros[nome] = DFEnumMember(node.name, nome, valor, indice)
        metodos = {}
        for nome, decl in node.methods.items():
            metodos[nome] = DFAction(
                name=nome, params=decl.params, defaults=decl.defaults,
                body=decl.body, closure=enum_env,
                param_types=getattr(decl, 'param_types', None),
                return_type=getattr(decl, 'return_type', ""))
        enum = DFEnum(node.name, membros, metodos, enum_env)
        for membro in membros.values():
            membro.enum = enum
        enum_env.set_local(node.name, enum)
        env.set_local(node.name, enum)
        return enum

    def _build_record(self, record: DFRecord, args, kwargs, node, env):
        """Constrói uma instância de record a partir dos argumentos."""
        nomes = record.field_names
        if len(args) > len(nomes):
            raise TypeError_(
                f"Record '{record.name}' has {len(nomes)} field(s) "
                f"but {len(args)} value(s) were given",
                node.line, node.column)
        desconhecidos = [k for k in kwargs if k not in nomes]
        if desconhecidos:
            raise NameError_(
                f"Record '{record.name}' has no field(s): "
                f"{', '.join(desconhecidos)}. It has: {', '.join(nomes)}",
                node.line, node.column)

        valores = {}
        for indice, nome in enumerate(nomes):
            tipo, padrao = record.field_types[nome], record.fields[indice][2]
            if indice < len(args):
                valor = args[indice]
            elif nome in kwargs:
                valor = kwargs[nome]
            elif padrao is not None:
                valor = self.evaluate(padrao, record.env)
            else:
                raise TypeError_(
                    f"Record '{record.name}' is missing field '{nome}'",
                    node.line, node.column)
            if tipo:
                self._check_type(valor, tipo,
                                 f"field '{nome}' of record '{record.name}'", node,
                                 record.type_params, record.type_bounds)
            valores[nome] = valor
        return DFRecordInstance(record, valores)

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — DESESTRUTURAÇÃO
    # ═══════════════════════════════════════════════════════

    def exec_DestructuringAssignment(self, node, env):
        valor = self.evaluate(node.value, env)

        if node.is_mapping:
            for nome, is_rest in node.targets:
                if is_rest:
                    usados = {n for n, r in node.targets if not r}
                    if isinstance(valor, DFRecordInstance):
                        resto = {k: v for k, v in valor.values.items() if k not in usados}
                    elif isinstance(valor, dict):
                        resto = {k: v for k, v in valor.items() if k not in usados}
                    else:
                        raise TypeError_(
                            f"Cannot destructure {self._type_of(valor)} with {{...}}",
                            node.line, node.column)
                    env.set(nome, resto)
                    continue
                if isinstance(valor, DFRecordInstance):
                    env.set(nome, valor.get(nome))
                elif isinstance(valor, dict):
                    if nome not in valor:
                        raise NameError_(
                            f"Vault has no key '{nome}' to destructure. "
                            f"Keys: {', '.join(str(k) for k in valor)}",
                            node.line, node.column)
                    env.set(nome, valor[nome])
                elif isinstance(valor, DFInstance):
                    env.set(nome, valor.get(nome))
                else:
                    raise TypeError_(
                        f"Cannot destructure {self._type_of(valor)} with {{...}}: "
                        f"expected a record, a vault or an instance",
                        node.line, node.column)
            return valor

        if isinstance(valor, DFStream):
            valor = list(valor)
        if isinstance(valor, DFRecordInstance):
            valor = [valor.values[n] for n in valor.record.field_names]
        if isinstance(valor, dict):
            valor = list(valor.items())
        if not hasattr(valor, '__iter__') or isinstance(valor, str) and len(node.targets) > len(valor):
            if not hasattr(valor, '__iter__'):
                raise TypeError_(
                    f"Cannot destructure {self._type_of(valor)}: "
                    f"expected a Cluster or a record",
                    node.line, node.column)
        itens = list(valor)

        rest_pos = next((i for i, (_, r) in enumerate(node.targets) if r), -1)
        fixos = len(node.targets) - (1 if rest_pos >= 0 else 0)
        if rest_pos < 0 and len(itens) != fixos:
            raise RuntimeError_(
                f"Cannot unpack {len(itens)} value(s) into {fixos} name(s)",
                node.line, node.column)
        if rest_pos >= 0 and len(itens) < fixos:
            raise RuntimeError_(
                f"Cannot unpack {len(itens)} value(s): at least {fixos} needed",
                node.line, node.column)

        if rest_pos < 0:
            for (nome, _), item in zip(node.targets, itens):
                env.set(nome, item)
        else:
            antes = node.targets[:rest_pos]
            depois = node.targets[rest_pos + 1:]
            for (nome, _), item in zip(antes, itens[:len(antes)]):
                env.set(nome, item)
            fim = len(itens) - len(depois)
            env.set(node.targets[rest_pos][0], itens[len(antes):fim])
            for (nome, _), item in zip(depois, itens[fim:]):
                env.set(nome, item)
        return valor

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — PATTERN MATCHING
    # ═══════════════════════════════════════════════════════

    def _match_pattern(self, padrao, valor, env, ligacoes):
        """Tenta casar 'valor' com 'padrao'. Preenche 'ligacoes'. Devolve bool."""
        casou = self._match_pattern_inner(padrao, valor, env, ligacoes)
        if casou and getattr(padrao, 'binding', ''):
            ligacoes[padrao.binding] = valor
        return casou

    def _match_pattern_inner(self, padrao, valor, env, ligacoes):
        if isinstance(padrao, ast.WildcardPattern):
            return True

        if isinstance(padrao, ast.LiteralPattern):
            return valor == padrao.value and (
                type(valor) is type(padrao.value)
                or not isinstance(padrao.value, bool) and not isinstance(valor, bool))

        if isinstance(padrao, ast.CapturePattern):
            ligacoes[padrao.name] = valor
            return True

        if isinstance(padrao, ast.ValuePattern):
            return valor == self.evaluate(padrao.expression, env)

        if isinstance(padrao, ast.OrPattern):
            for opcao in padrao.options:
                tentativa = {}
                if self._match_pattern(opcao, valor, env, tentativa):
                    ligacoes.update(tentativa)
                    return True
            return False

        if isinstance(padrao, ast.SequencePattern):
            # Só sequências de verdade: um vault casa com {..}, não com [..].
            if isinstance(valor, DFStream):
                valor = list(valor)
            if not isinstance(valor, (list, tuple)):
                return False
            itens = list(valor)
            fixos = padrao.elements
            if padrao.rest_index < 0:
                if len(itens) != len(fixos):
                    return False
                return all(self._match_pattern(p, i, env, ligacoes)
                           for p, i in zip(fixos, itens))
            antes = fixos[:padrao.rest_index]
            depois = fixos[padrao.rest_index:]
            if len(itens) < len(antes) + len(depois):
                return False
            for p, i in zip(antes, itens[:len(antes)]):
                if not self._match_pattern(p, i, env, ligacoes):
                    return False
            fim = len(itens) - len(depois)
            if padrao.rest_name:
                ligacoes[padrao.rest_name] = itens[len(antes):fim]
            for p, i in zip(depois, itens[fim:]):
                if not self._match_pattern(p, i, env, ligacoes):
                    return False
            return True

        if isinstance(padrao, ast.MappingPattern):
            if isinstance(valor, DFRecordInstance):
                mapa = valor.values
            elif isinstance(valor, DFInstance):
                mapa = valor.fields
            elif isinstance(valor, dict):
                mapa = valor
            else:
                return False
            usadas = set()
            for chave_node, sub in padrao.pairs:
                chave = self.evaluate(chave_node, env)
                if chave not in mapa:
                    return False
                usadas.add(chave)
                if not self._match_pattern(sub, mapa[chave], env, ligacoes):
                    return False
            if padrao.rest_name:
                ligacoes[padrao.rest_name] = {
                    k: v for k, v in mapa.items() if k not in usadas}
            return True

        if isinstance(padrao, ast.TypePattern):
            if not self._value_has_type(valor, padrao.type_name, env):
                return False
            if padrao.sub_patterns:
                campos = self._positional_fields(valor)
                if campos is None or len(campos) < len(padrao.sub_patterns):
                    return False
                for sub, item in zip(padrao.sub_patterns, campos):
                    if not self._match_pattern(sub, item, env, ligacoes):
                        return False
            for campo, sub in padrao.field_patterns.items():
                try:
                    atual = self._field_of(valor, campo)
                except (NameError_, KeyError):
                    return False
                if not self._match_pattern(sub, atual, env, ligacoes):
                    return False
            return True

        return False

    def _value_has_type(self, valor, nome_tipo, env) -> bool:
        canonico = self.TYPE_ALIASES.get(nome_tipo, nome_tipo)
        if canonico == "Any":
            return True
        if canonico == "Number":
            return isinstance(valor, (int, float)) and not isinstance(valor, bool)
        atual = self._type_of(valor)
        if atual == canonico:
            return True
        if isinstance(valor, DFInstance):
            return any(bp.name == nome_tipo for bp in valor.get_mro())
        if isinstance(valor, DFRecordInstance):
            return valor.record.name == nome_tipo
        if isinstance(valor, DFEnumMember):
            return valor.enum_name == nome_tipo
        return False

    def _positional_fields(self, valor):
        if isinstance(valor, DFRecordInstance):
            return [valor.values[n] for n in valor.record.field_names]
        if isinstance(valor, DFInstance):
            return list(valor.fields.values())
        if isinstance(valor, (list, tuple)):
            return list(valor)
        return None

    def _field_of(self, valor, campo):
        if isinstance(valor, DFRecordInstance):
            return valor.get(campo)
        if isinstance(valor, DFInstance):
            return valor.get(campo)
        if isinstance(valor, dict):
            return valor[campo]
        raise NameError_(f"No field '{campo}'")

    # ── Error Handling ─────────────────────────────────────

    def exec_MonitorBlock(self, node: ast.MonitorBlock, env):
        """monitor / handle / ensure.

        O corpo roda no MESMO escopo, nao num filho. Em Python, Java e
        JavaScript, 'try' nao cria escopo — e a expectativa de quem chega
        de qualquer uma delas:

            monitor:
                resposta := buscar()
            handle e:
                out e.message
            out resposta          // precisa existir aqui

        Com escopo proprio, esse padrao — o mais comum de todos — nao
        funcionava, e a variavel sumia sem explicacao.

        'handle' e 'ensure' ganham filho: 'handle' porque precisa ligar o
        nome do erro sem vazar depois, e 'ensure' porque roda em qualquer
        saida e nao deveria deixar rastro.
        """
        try:
            return self.exec_block(node.body, env)
        except Exception as e:
            # A 'monitor' with no 'handle' is a try/finally: never swallow the error.
            clausula = next((h for h in node.handles
                             if self._error_matches(e, h.error_type, env)), None)
            if clausula is None:
                raise
            # O 'handle' roda no escopo de fora, para que o que ele
            # atribui continue valendo — mas o nome do erro nao vaza:
            # ele e removido no fim, ou devolvido ao valor anterior se
            # ja existia um nome igual.
            tinha = clausula.error_name in env.variables
            anterior = env.variables.get(clausula.error_name)
            env.set_local(clausula.error_name, self._error_value(e))
            # Enquanto o corpo do 'handle' roda, ESTE e o erro em
            # tratamento: um 'trigger' ali dentro o guarda como causa. O
            # valor anterior e restaurado no fim, e nao zerado, porque
            # 'handle' dentro de 'handle' e legitimo — e o de fora
            # continua sendo a causa do que vier depois dele.
            anterior_em_tratamento = getattr(self, "_erro_em_tratamento", None)
            self._erro_em_tratamento = e if isinstance(e, DataForgeError) else None
            try:
                return self.exec_block(clausula.body, env)
            finally:
                self._erro_em_tratamento = anterior_em_tratamento
                if tinha:
                    env.variables[clausula.error_name] = anterior
                else:
                    env.variables.pop(clausula.error_name, None)
        finally:
            if node.ensure_body:
                self.exec_block(node.ensure_body, env.child("<ensure>"))

    def _error_value(self, exc):
        """Wrap a caught exception into the value bound by 'handle'."""
        message = exc.message if isinstance(exc, DataForgeError) else str(exc)
        return DFError(type(exc).__name__.rstrip('_'), message, exc)

    #: Nomes que capturam qualquer erro.
    _CAPTURA_TUDO = frozenset({"Error", "Exception", "Any", "DataForgeError"})

    def _error_matches(self, exc, handle_type, env) -> bool:
        """O erro capturado casa com o filtro de 'handle <Tipo>'?

        A comparacao e por HERANCA, nao por nome. Com 177 codigos
        organizados em familias, comparar nomes exatos obrigaria a
        listar cada erro possivel:

            handle DivisionByZeroError:
            handle ConversionError:
            handle NullReferenceError:      // ... e mais dezessete

        Com heranca, 'handle RuntimeError' pega os tres, e quem
        precisa distinguir ainda pode nomear o especifico. E a
        expectativa de quem chega de qualquer linguagem com excecoes.

        Um erro do proprio programa ('trigger MinhaFalha(...)') nao tem
        classe: casa pelo nome que o 'trigger' deu.
        """
        if not handle_type:
            return True
        if handle_type in self._CAPTURA_TUDO:
            return True

        # Erro nomeado pelo programa: 'trigger SaldoInsuficiente(...)'.
        rotulo = getattr(exc, "tipo_usuario", None)
        if rotulo and rotulo == handle_type:
            return True

        alvo = erro_por_nome(handle_type)
        if alvo is not None:
            return isinstance(exc, alvo)

        # Nome desconhecido: cai no confronto textual de antes, para
        # nao quebrar codigo que capture um erro do Python cru.
        nome = type(exc).__name__
        return handle_type in (nome, nome.rstrip('_'))

    # ── Modules ────────────────────────────────────────────

    def exec_AdoptStatement(self, node: ast.AdoptStatement, env):
        """Importa um módulo da stdlib ou um arquivo .df vizinho.

        Três formas:
            adopt Arcane.Math as M          — o módulo inteiro, sob um nome
            adopt Arcane.Math.{sqrt, floor} — só os símbolos nomeados
            adopt {sqrt} from Arcane.Math   — idem, com a ordem invertida
        """
        nome_modulo = node.module
        # Quanto cada 'adopt' custou na partida. Sao dois floats por
        # import — e e a unica forma de responder "por que o programa
        # demora 400 ms para comecar?" sem cronometrar a mao.
        _comeco = time.perf_counter()
        modulo = self._resolver_modulo(nome_modulo, node, env)
        self.boot_adocoes.append(
            (nome_modulo, (time.perf_counter() - _comeco) * 1000.0))

        if node.selection:
            faltando = [n for n, _ in node.selection if n not in modulo]
            if faltando:
                disponiveis = sorted(k for k in modulo if not k.startswith('__'))
                raise ImportError_(
                    f"Module '{nome_modulo}' does not export: "
                    f"{', '.join(faltando)}. "
                    f"It exports: {', '.join(disponiveis[:10])}"
                    f"{'…' if len(disponiveis) > 10 else ''}",
                    node.line, node.column)
            for nome, apelido in node.selection:
                env.set_local(apelido, modulo[nome])
            return

        alias = node.alias or nome_modulo.split('.')[-1]
        env.set_local(alias, modulo)

    def _resolver_modulo(self, nome_modulo, node, env):
        """Encontra o módulo: a ponte, o cache, a stdlib ou um .df."""
        if nome_modulo in self.modules:
            return self.modules[nome_modulo]

        # 'Python.x' abre a ponte para o Python. Vem antes de tudo o
        # mais porque e um espaco de nomes RESERVADO: nao ha modulo da
        # stdlib nem arquivo local que deva responder por ele, e deixar
        # que respondessem faria um 'Python.df' no disco sequestrar o
        # import sem nada denunciando.
        from .ponte import e_caminho_de_ponte, importar as importar_python
        if e_caminho_de_ponte(nome_modulo):
            modulo = importar_python(nome_modulo, node)
            self.modules[nome_modulo] = modulo
            return modulo

        from .stdlib import get_module, list_modules
        modulo = get_module(nome_modulo)
        if modulo is not None:
            self.modules[nome_modulo] = modulo
            return modulo

        import os

        # ── Caminho relativo explicito: './util', '../lib/x' ──
        # Resolve sempre a partir do arquivo que escreve o import, nunca do
        # diretorio de onde se rodou o programa. Assim mover a pasta inteira
        # nao quebra nada, e ler o codigo basta para saber o que ele importa.
        if nome_modulo.startswith(('./', '../', '.\\', '..\\')) or \
                nome_modulo.endswith('.df'):
            origem = (os.path.dirname(os.path.abspath(self.filename))
                      if self.filename and not self.filename.startswith('<')
                      else os.getcwd())
            alvo = os.path.normpath(os.path.join(origem, nome_modulo))
            for candidato in (alvo, alvo + '.df',
                              os.path.join(alvo, 'main.df'),
                              os.path.join(alvo, 'src', 'main.df')):
                if os.path.isfile(candidato):
                    return self._load_module_file(candidato, nome_modulo)
            raise ImportError_(
                f"Module '{nome_modulo}' not found.",
                node.line, node.column,
                nota=f"resolved to {_curto(alvo)} "
                     f"relative to {os.path.basename(self.filename)}",
                dica="check the path, or that the file ends in .df",
                doc="pacotes")

        # Caminhos relativos ao arquivo que faz o import, não ao diretório atual
        bases = []
        if self.filename and not self.filename.startswith('<'):
            bases.append(os.path.dirname(os.path.abspath(self.filename)))
        bases.append(os.getcwd())

        partes = nome_modulo.replace('.', os.sep)
        for base in bases:
            for sufixo in ('.df', os.path.join('', 'main.df')):
                caminho = os.path.join(base, partes + sufixo) if sufixo == '.df' \
                    else os.path.join(base, partes, 'main.df')
                if os.path.exists(caminho):
                    return self._load_module_file(caminho, nome_modulo)

        # Pacotes instalados: forge_modules/<pacote>/, procurando a partir
        # do arquivo atual para cima — assim um .df em qualquer subpasta do
        # projeto enxerga o que 'dataforge add' instalou na raiz.
        caminho = self._procurar_em_pacotes(nome_modulo, bases)
        if caminho:
            return self._load_module_file(caminho, nome_modulo)

        # O PROPRIO pacote, pelo nome que ele declara no forge.toml.
        #
        # O teste de uma biblioteca escreve 'adopt validador', e nao
        # 'adopt ../src/main', porque ele precisa exercita-la pelo mesmo
        # caminho que um usuario usaria. Sem isto a suite de um pacote
        # so roda depois de publicado e instalado — e as dos VINTE
        # pacotes deste repositorio falhavam exatamente assim.
        from . import resolucao
        caminho = resolucao.achar_no_proprio_pacote(nome_modulo, self.filename)
        if caminho:
            return self._load_module_file(caminho, nome_modulo)

        disponiveis = sorted(set(list_modules()))
        instalados = self._pacotes_instalados(bases)
        dica = ""
        if instalados:
            import difflib
            raiz_pedida = nome_modulo.split('.')[0]
            perto = difflib.get_close_matches(raiz_pedida, instalados, n=2, cutoff=0.6)
            if perto:
                dica = f" Installed packages: {', '.join(perto)}."
            else:
                dica = f" Installed: {', '.join(sorted(instalados)[:6])}."
        else:
            dica = " No packages installed — try 'dataforge add <package>'."

        raise ImportError_(
            f"Module '{nome_modulo}' not found. "
            f"Looked in the standard library, next to "
            f"{os.path.basename(self.filename) if self.filename else 'the current file'}, "
            f"and in forge_modules/.{dica} "
            f"Standard library: {', '.join(disponiveis[:6])}…",
            node.line, node.column)

    @staticmethod
    def _raizes_de_projeto(bases):
        """Sobe de cada base ate achar forge_modules/ ou forge.toml."""
        import os
        raizes = []
        for base in bases:
            atual = os.path.abspath(base)
            while True:
                if os.path.isdir(os.path.join(atual, 'forge_modules')) or \
                        os.path.exists(os.path.join(atual, 'forge.toml')):
                    if atual not in raizes:
                        raizes.append(atual)
                    break
                pai = os.path.dirname(atual)
                if pai == atual:
                    break
                atual = pai
        return raizes

    def _procurar_em_pacotes(self, nome_modulo, bases):
        """Encontra o .df de um modulo dentro de forge_modules/.

        'adopt validador' carrega o ponto de entrada do pacote;
        'adopt validador.email' carrega src/email.df (ou email.df) dentro dele.
        """
        import os
        raiz_pacote, _, resto = nome_modulo.partition('.')
        for raiz in self._raizes_de_projeto(bases):
            pasta = os.path.join(raiz, 'forge_modules', raiz_pacote)
            if not os.path.isdir(pasta):
                continue

            if resto:
                sub = resto.replace('.', os.sep)
                for candidato in (os.path.join(pasta, 'src', sub + '.df'),
                                  os.path.join(pasta, sub + '.df'),
                                  os.path.join(pasta, 'src', sub, 'main.df'),
                                  os.path.join(pasta, sub, 'main.df')):
                    if os.path.exists(candidato):
                        return candidato
                continue

            entrada = self._entrada_do_pacote(pasta)
            if entrada and os.path.exists(entrada):
                return entrada
            for candidato in (os.path.join(pasta, 'src', 'main.df'),
                              os.path.join(pasta, 'main.df'),
                              os.path.join(pasta, f'{raiz_pacote}.df')):
                if os.path.exists(candidato):
                    return candidato
        return None

    @staticmethod
    def _entrada_do_pacote(pasta):
        """Le 'entry' do forge.toml do pacote, se houver."""
        import os
        manifesto = os.path.join(pasta, 'forge.toml')
        if not os.path.exists(manifesto):
            return None
        try:
            from .stdlib.arcane_serialization import ArcaneSerialization
            dados = ArcaneSerialization()['from_toml'](
                open(manifesto, encoding='utf-8').read())
            secao = dados.get('package') or dados.get('project') or {}
            entrada = secao.get('entry')
            return os.path.join(pasta, entrada) if entrada else None
        except Exception:
            return None

    def _pacotes_instalados(self, bases):
        import os
        nomes = []
        for raiz in self._raizes_de_projeto(bases):
            pasta = os.path.join(raiz, 'forge_modules')
            if os.path.isdir(pasta):
                nomes += [d for d in os.listdir(pasta)
                          if os.path.isdir(os.path.join(pasta, d))
                          and not d.startswith('.')]
        return sorted(set(nomes))

    def exec_RelayStatement(self, node: ast.RelayStatement, env):
        """Marca quais nomes o módulo exporta.

        Sem nenhum 'relay', o módulo exporta tudo o que definiu no topo — é o
        comportamento conveniente para scripts. Com pelo menos um 'relay', só
        os nomes listados atravessam o 'adopt'.
        """
        exportados = getattr(env, '_exports', None)
        if exportados is None:
            exportados = env._exports = []

        # 'relay from ./util' — re-exporta tudo daquele modulo
        if getattr(node, 'origem', ''):
            modulo = self._resolver_modulo(node.origem, node, env)
            if not isinstance(modulo, dict):
                raise ImportError_(
                    f"'relay from {node.origem}' needs a module, but that "
                    f"resolved to {self._nome_do_tipo(modulo)}.",
                    node.line, node.column, doc="pacotes")
            for nome, valor in modulo.items():
                if nome.startswith('__'):
                    continue
                # o nome local vence: um 'relay from' nao sobrescreve o
                # que este modulo definiu por conta propria
                if not env.has(nome):
                    env.set_local(nome, valor)
                if nome not in exportados:
                    exportados.append(nome)
            return

        for nome in node.names:
            if not env.has(nome) and nome in self.tipos_nomeados:
                # Um 'type' transparente nao e um VALOR: ele vive no
                # registro de tipos, que e do interpretador inteiro. Sem
                # este ramo, 'relay Positivo' acusava um nome que existe.
                exportados.append(nome)
                continue
            if not env.has(nome):
                import difflib
                visiveis = [n for n in env.variables if not n.startswith('__')]
                perto = difflib.get_close_matches(nome, visiveis, n=1, cutoff=0.6)
                raise NameError_(
                    f"'relay' exports '{nome}', which this module never defines.",
                    node.line, node.column,
                    dica=(f"did you mean '{perto[0]}'?" if perto else
                          "define it before the 'relay', or remove it from the list"),
                    doc="pacotes")
            exportados.append(nome)

    # ── Concurrency ────────────────────────────────────────

    def exec_ThreadBlock(self, node: ast.ThreadBlock, env):
        """Dispara o corpo numa thread e segue sem esperar.

        Um erro no corpo era impresso como '[Thread Error] …' — uma linha
        sem trecho de codigo, sem pilha — e o programa terminava com codigo
        0. O CI passava verde com a thread morta.

        'thread' NAO e estruturado: quando o corpo falha, quem o disparou
        ja esta em outra linha, e nao ha onde levantar o erro. Por isso
        duas coisas, e as duas importam:

        1. o erro e DESENHADO na hora, completo, na saida de erro. Guardar
           para o fim nao serve: se a principal estiver esperando o item
           que esta thread ia enviar, o fim nunca chega, e o programa
           trava sem mensagem nenhuma — a pior falha possivel.
        2. ao terminar o programa, 'run' levanta um erro dizendo quantas
           threads falharam, e o codigo de saida deixa de ser 0.

        Quem precisa pegar o erro com 'handle' quer 'parallel', que espera.
        """
        thread_env = env.child("<thread>")

        def thread_func():
            try:
                try:
                    self.exec_block(node.body, thread_env)
                finally:
                    self._run_deferred(thread_env)
            except ControlSignal as sinal:
                self._registrar_falha_de_thread(RuntimeError_(
                    f"'{self._palavra_do_sinal(sinal)}' cannot leave a "
                    f"'thread' block.",
                    node.line, node.column,
                    nota="the body runs in another thread, so there is no "
                         "loop or action around it to end",
                    doc="tecnicas/concorrencia"), node)
            except DataForgeError as erro:
                self._registrar_falha_de_thread(erro, node)
            except Exception as ex:                       # noqa: BLE001
                self._registrar_falha_de_thread(
                    self._traduzir_excecao(ex, node), node)

        t = threading.Thread(target=thread_func, daemon=True)
        t.start()
        return t

    def _palavra_do_sinal(self, sinal):
        return self._SINAIS_SOLTOS.get(
            type(sinal).__name__, ("this",))[0]

    def _registrar_falha_de_thread(self, erro, node):
        """Desenha o erro agora e guarda para o codigo de saida."""
        self._attach_stack(erro)
        if not getattr(erro, "filename", ""):
            erro.filename = self.filename
        with self._trava_das_falhas:
            self._falhas_de_thread.append((erro, node))
        try:
            import sys as _sys
            cor = _sys.stderr.isatty()
            print(erro.render(color=cor), file=_sys.stderr, flush=True)
        except Exception:                                 # noqa: BLE001
            # Desenhar nao pode derrubar a thread de novo; o erro ja esta
            # guardado, e 'run' vai reporta-lo.
            pass

    def exec_ChannelDeclaration(self, node: ast.ChannelDeclaration, env):
        ch = DFChannel(node.name)
        env.set_local(node.name, ch)
        return ch

    def exec_PulseStatement(self, node: ast.PulseStatement, env):
        event = self.evaluate(node.event, env)
        data = self.evaluate(node.data, env) if node.data else None
        event_name = self._to_str(event)
        if event_name in self.events:
            for callback in self.events[event_name]:
                self._call(callback, [data] if data else [], {}, node, env)

    # ── New Error Handling ─────────────────────────────────

    def exec_GuardStatement(self, node: ast.GuardStatement, env):
        """Guard: check condition, run else_body or trigger error if false.
        When the guard fails and else_body runs, raises YieldSignal to exit the function."""
        condition = self.evaluate(node.condition, env)
        if not condition:
            if node.else_body:
                for stmt in node.else_body:
                    self.execute(stmt, env)
                raise YieldSignal(None)
            msg = "Guard condition failed"
            if node.message:
                msg = self._to_str(self.evaluate(node.message, env))
            raise TriggerError(msg, node.line, node.column)

    def exec_RetryBlock(self, node: ast.RetryBlock, env):
        """Retry: attempt block up to N times."""
        count = self.evaluate(node.count, env)
        last_error = None
        for attempt in range(int(count)):
            try:
                # mesmo escopo do monitor: o que a tentativa atribui
                # continua valendo depois do bloco
                return self.exec_block(node.body, env)
            except Exception as e:
                last_error = self._error_value(e)

        # All attempts failed
        if node.handle_body and last_error is not None:
            tinha = node.handle_name in env.variables
            anterior = env.variables.get(node.handle_name)
            env.set_local(node.handle_name, last_error)
            try:
                return self.exec_block(node.handle_body, env)
            finally:
                if tinha:
                    env.variables[node.handle_name] = anterior
                else:
                    env.variables.pop(node.handle_name, None)
        return None

    def exec_ValidateStatement(self, node: ast.ValidateStatement, env):
        """Validate: check value is truthy, run else_body or trigger if not.
        When validation fails and else_body runs, raises YieldSignal to exit the function."""
        value = self.evaluate(node.value, env)
        if not value:
            if node.else_body:
                for stmt in node.else_body:
                    self.execute(stmt, env)
                raise YieldSignal(None)
            msg = "Validation failed"
            if node.message:
                msg = self._to_str(self.evaluate(node.message, env))
            raise TriggerError(msg, node.line, node.column)
        return value

    def exec_PropagateStatement(self, node: ast.PropagateStatement, env):
        """Re-raise an error."""
        if node.value:
            value = self.evaluate(node.value, env)
            raise TriggerError(self._to_str(value), node.line, node.column)
        raise TriggerError("Propagated error", node.line, node.column)

    def _sair_do_contexto(self, recurso, erro, node):
        """'__exit__' com o que ele aceitar: nada, ou (tipo, erro, pilha).

        A forma de tres argumentos e a do Python, e a de nenhum e a mais
        comum aqui. Aceitar so uma obrigava a escrever parametros que
        ninguem usa — ou dava "missing argument(s)" no fim do bloco.
        """
        for nome in ("__exit__", "__aexit__"):
            acao = self._achar_magico(recurso, nome)
            if acao is None:
                continue
            capturado = None
            if erro is not None:
                capturado = DFError(type(erro).__name__.rstrip("_"),
                                    getattr(erro, "message", str(erro)), erro)
            if len(acao.params) >= 3:
                args = ([capturado.type, capturado, None] if capturado is not None
                        else [None, None, None])
            elif len(acao.params) == 1:
                args = [capturado]
            else:
                args = []
            return self._call_action(acao, args, {}, node, None, instance=recurso)
        return _SEM_MAGICO

    def exec_WithBlock(self, node: ast.WithBlock, env):
        """with <recurso> [as <nome>]: corpo — abre, usa e fecha.

        O fechamento roda em QUALQUER saida: retorno, erro, 'halt'. E o
        que separa isto de abrir e fechar a mao — a mao esquece
        exatamente no caminho de erro, que e onde mais importa.

        Reconhece tres formas de recurso, na ordem:
            'abrir()' e 'fechar()' — o protocolo do Forge e do Kiln
            '__enter__' / '__exit__' — objetos do host
            'fechar()' sozinho — o caso mais comum
        """
        recurso = self.evaluate(node.resource, env)

        valor = recurso

        # Uma instancia com '__enter__' decide o que 'as' recebe. E o
        # protocolo de contexto do Python, e o que faz um blueprint
        # proprio servir de recurso gerenciado.
        if isinstance(recurso, DFInstance):
            entrar = "__enter__" if self._tem_magico(recurso, "__enter__") else "__aenter__"
            entregue = self._chamar_magico(recurso, entrar, [], node)
            if isinstance(entregue, DFTarefa):
                entregue = entregue.aguardar()
            if entregue is not _SEM_MAGICO:
                valor = entregue
            interno = Environment(parent=env, name="<with>")
            tinha_i = node.name and node.name in env.variables
            anterior_i = env.variables.get(node.name) if tinha_i else None
            if node.name:
                env.set_local(node.name, valor)
            erro_do_corpo = None
            try:
                return self.exec_block(node.body, env)
            except DataForgeError as erro:
                erro_do_corpo = erro
                raise
            finally:
                if node.name:
                    if tinha_i:
                        env.variables[node.name] = anterior_i
                    else:
                        env.variables.pop(node.name, None)
                saida = self._sair_do_contexto(recurso, erro_do_corpo, node)
                if saida is _SEM_MAGICO:
                    self._fechar_recurso(recurso, node)

        entrar = getattr(recurso, "__enter__", None)
        if callable(entrar):
            valor = entrar()
        elif callable(getattr(recurso, "abrir", None)):
            aberto = recurso.abrir()
            if aberto is not None:
                valor = aberto

        # O corpo roda no escopo de FORA, como o do 'monitor', e pelo
        # mesmo motivo: o que ele calcula costuma ser necessario depois.
        #
        #     with abrir(caminho) as f:
        #         conteudo := f.ler()
        #     out conteudo          <- precisa existir aqui
        #
        # So o nome do recurso e local: ele deixa de valer quando o
        # recurso fecha, e mante-lo visivel seria um convite a usa-lo
        # fechado. E devolvido ao valor anterior se ja existia um nome
        # igual.
        tinha = node.name and node.name in env.variables
        anterior = env.variables.get(node.name) if tinha else None
        if node.name:
            env.set_local(node.name, valor)

        try:
            return self.exec_block(node.body, env)
        finally:
            if node.name:
                if tinha:
                    env.variables[node.name] = anterior
                else:
                    env.variables.pop(node.name, None)
            self._fechar_recurso(recurso, node)

    def _fechar_recurso(self, recurso, node):
        """Fecha o que o 'with' abriu, pelo primeiro jeito que servir.

        Um erro AO FECHAR nao pode esconder o erro que veio do corpo:
        se o corpo ja estourou, este 'finally' roda durante aquela
        excecao, e levantar outra aqui a substituiria — trocando a
        causa real por um sintoma.
        """
        sair = getattr(recurso, "__exit__", None)
        try:
            if callable(sair):
                sair(None, None, None)
                return
            fechar = getattr(recurso, "fechar", None)
            if callable(fechar):
                fechar()
                return
            close = getattr(recurso, "close", None)
            if callable(close):
                close()
        except (DataForgeError, Exception):           # noqa: BLE001
            pass

    #: Os escopos que RODAM os 'defer' registrados dentro deles.
    #:
    #: Um 'defer' se registrava no escopo onde aparece, e so o escopo da
    #: ACAO era consultado na saida. O resultado, calado:
    #:
    #:     action f():
    #:         cycle i from 1 to 2:
    #:             defer:
    #:                 fechar(arquivo)     nunca rodava
    #:
    #: 'given' e 'monitor' funcionavam por acidente — eles compartilham o
    #: escopo da acao. 'cycle' e 'persist' tem escopo proprio, e ali o
    #: 'defer' ia para um lugar que ninguem olhava. No topo do programa,
    #: idem: nao ha acao nenhuma, e ele nunca rodava.
    #:
    #: A fronteira e onde o 'defer' PROMETE rodar: a saida da acao, e —
    #: para quem dispara trabalho — a saida da thread ou da tarefa, que
    #: e quando o recurso daquele trabalho deixa de ser usado.
    _FRONTEIRAS_DE_DEFER = ("<action ", "<thread>", "<parallel>", "<global>")

    def _escopo_do_defer(self, env):
        """O escopo que vai rodar este 'defer'."""
        atual = env
        while atual is not None:
            nome = getattr(atual, "name", "") or ""
            if nome.startswith(self._FRONTEIRAS_DE_DEFER):
                return atual
            if atual.parent is None:
                return atual          # o global, com qualquer nome
            atual = atual.parent
        return env

    def exec_DeferStatement(self, node: ast.DeferStatement, env):
        """Agenda o bloco para a saida da acao (ou da thread, ou do programa).

        O bloco roda no escopo em que foi ESCRITO — e por isso o par
        guardado leva 'env', e nao a fronteira: um 'defer' dentro de um
        laco precisa ver o 'i' daquela volta.
        """
        alvo = self._escopo_do_defer(env)
        if alvo._deferred is None:
            alvo._deferred = []
        alvo._deferred.append((node.body, env))

    def exec_ObserveBlock(self, node: ast.ObserveBlock, env):
        """observe var in fonte: reage a cada item que chega.

        A fonte pode ser um Cluster, um DFStream (de um 'stream action'), ou o
        vault {"__type__": "Stream"} produzido por stream(colecao).
        """
        source = self.evaluate(node.source, env)

        if isinstance(source, DFStream):
            itens = source
        elif isinstance(source, (list, tuple)):
            itens = source
        elif isinstance(source, dict) and source.get("__type__") == "Stream":
            itens = source.get("data", [])
        elif isinstance(source, dict):
            itens = list(source.keys())
        elif isinstance(source, str):
            itens = source
        else:
            raise TypeError_(
                f"Cannot observe a value of type {self._type_of(source)}: "
                f"expected a Cluster, a Vault, a String or a stream",
                node.line, node.column)

        for item in itens:
            obs_env = env.child("<observe>")
            obs_env.set_local(node.var, item)
            try:
                self.exec_block(node.body, obs_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue

    def eval_StreamExpression(self, node: ast.StreamExpression, env):
        """Create a reactive stream from data."""
        data = self.evaluate(node.source, env)
        return {"__type__": "Stream", "data": data if isinstance(data, list) else [data]}

    def exec_ParallelBlock(self, node: ast.ParallelBlock, env):
        """Roda cada TAREFA numa thread, espera TODAS, e so entao segue.

        Uma tarefa e uma instrucao solta, ou um bloco 'thread:' inteiro:

            parallel:
                thread:
                    dados := baixar("a")
                    salvar(dados)          em ordem, na mesma thread
                thread:
                    dados := baixar("b")
                    salvar(dados)
                registrar("inicio")        uma tarefa sozinha


        Um erro numa das instrucoes era IMPRESSO e engolido:
        o 'except Exception' imprimia '[Parallel Error] …', e o programa
        seguia. O codigo de saida era 0, 'monitor/handle' nao conseguia
        pegar o erro, e um CI rodando o arquivo passava verde. Era a unica
        construcao da linguagem em que um erro nao chegava a quem escreveu.

        'parallel' e ESTRUTURADO — o bloco so termina quando todas terminam
        —, entao o erro tem para onde voltar: ele e levantado aqui, na
        linha do bloco, depois que as outras instrucoes terminam. Esperar
        as outras antes de levantar e o que impede uma thread de continuar
        escrevendo depois que o 'handle' de fora ja rodou.

        Com mais de um erro, o primeiro viaja e os outros pegam carona em
        '.outros' — o mesmo mecanismo da leva de erros de sintaxe, e o
        'render' desenha todos.

        Duas coisas sairam junto:

        - o 'join(timeout=30)'. Depois de 30 s ele ABANDONAVA as threads e
          seguia, calado, com o trabalho pela metade. Uma instrucao que
          nao termina e um bug de quem escreveu, igual a um laco infinito
          em serie — e trava-lo e mais honesto que perder o resultado.
        - 'halt', 'skip' e 'yield' dentro de uma das instrucoes morriam
          como traceback do Python na thread. Eles nao podem sair do bloco
          — cada instrucao roda na propria thread, e nao ha um laco ou uma
          acao para eles encerrarem —, entao viram erro da linguagem.
        """
        threads = []
        falhas = []
        trava = threading.Lock()

        def rodar(stmt, escopo, ordem):
            try:
                try:
                    _rodar_tarefa(stmt, escopo)
                finally:
                    self._run_deferred(escopo)
            except DataForgeError as erro:
                self._attach_stack(erro)
                with trava:
                    falhas.append((ordem, erro))
            except ControlSignal as sinal:
                erro = RuntimeError_(
                    f"'{self._palavra_do_sinal(sinal)}' cannot leave a "
                    f"'parallel' block.",
                    getattr(stmt, 'line', 0), getattr(stmt, 'column', 0),
                    nota="each statement of 'parallel' runs in its own "
                         "thread, so there is no loop or action around it "
                         "to end",
                    dica="decide inside the statement, or move the loop "
                         "out of 'parallel'",
                    doc="tecnicas/concorrencia")
                erro.filename = self.filename
                with trava:
                    falhas.append((ordem, erro))
            except Exception as ex:                       # noqa: BLE001
                erro = self._traduzir_excecao(ex, stmt)
                self._attach_stack(erro)
                with trava:
                    falhas.append((ordem, erro))

        def _rodar_tarefa(stmt, escopo):
            if isinstance(stmt, ast.ThreadBlock):
                # Um 'thread:' DENTRO de 'parallel' e uma TAREFA: o bloco
                # inteiro roda nesta thread, em sequencia, e e esperado como
                # as outras. Fora do 'parallel', 'thread:' continua
                # disparando e seguindo.
                self.exec_block(stmt.body, escopo)
            else:
                self.execute(stmt, escopo)

        for ordem, stmt in enumerate(node.blocks):
            t = threading.Thread(
                target=rodar, args=(stmt, env.child("<parallel>"), ordem),
                daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if falhas:
            # A ordem das INSTRUCOES, e nao a de termino: qual thread
            # falhou primeiro e sorteio do escalonador, e um relatorio que
            # muda de ordem a cada execucao parece dois bugs diferentes.
            falhas.sort(key=lambda par: par[0])
            primeiro = falhas[0][1]
            primeiro.outros = list(getattr(primeiro, "outros", [])) + [
                erro for _, erro in falhas[1:]]
            raise primeiro

    # ═══════════════════════════════════════════════════════
    #  INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════

    #: Como cada tipo do runtime se chama em DataForge.
    _NOMES_DE_TIPO = {
        int: "an Integer", float: "a Float", str: "a String",
        bool: "a Boolean", list: "a Cluster", dict: "a Vault",
        type(None): "void",
    }

    def _erro_de_tarefa(self, tarefa, node):
        """Usou o resultado de uma acao 'async' sem 'await'.

        E o engano mais comum de quem escreve codigo assincrono, em
        qualquer linguagem: a chamada devolve o TRABALHO, nao o
        resultado dele. Dizer 'nao da para indexar isto' esta correto e
        nao ajuda em nada — o que a pessoa precisa ouvir e a palavra que
        faltou.
        """
        return TypeError_(
            f"'{tarefa.nome}' is an 'async' action: calling it starts the "
            f"work and hands back the task, not the value.",
            node.line, node.column,
            nota="'await' waits for it to finish and gives you the value",
            dica=(f"    result := await {tarefa.nome}(...)\n"
                  f"\n"
                  f"To run several at once, start them all before "
                  f"awaiting:\n"
                  f"    tasks := [{tarefa.nome}(x) cycle x in source]\n"
                  f"    values := await tasks"),
            doc="tecnicas/concorrencia")

    def _nome_do_tipo(self, valor):
        """Descreve o tipo de um valor com o vocabulario da linguagem."""
        if isinstance(valor, DFInstance):
            return f"an instance of '{valor.blueprint.name}'"
        if isinstance(valor, DFBlueprint):
            return f"the blueprint '{valor.name}'"
        if isinstance(valor, DFRecord):
            return f"the record type '{valor.name}'"
        if isinstance(valor, DFRecordInstance):
            return f"a '{valor.record.name}' record"
        if isinstance(valor, DFEnum):
            return f"the enum '{valor.name}'"
        if isinstance(valor, DFAction):
            return f"the action '{valor.name}'"
        if isinstance(valor, BuiltinFunction):
            return f"the builtin '{valor.name}'"
        if isinstance(valor, DFTarefa):
            return f"the running task '{valor.nome}'"
        if isinstance(valor, DFError):
            # Era "DFError", a classe do Python — o mesmo vazamento que a
            # trava de tipos proibe. Na linguagem, e o valor de um 'handle'.
            return f"a caught error ({valor.type})"
        for tipo, nome in self._NOMES_DE_TIPO.items():
            if type(valor) is tipo:
                return nome
        # Ultimo recurso: um objeto que veio da ponte para o Python nao
        # tem nome NESTA linguagem, e inventar um seria pior. Mas os
        # tipos que TEM nome passam pela traducao — este ramo tambem e
        # alcancado por subclasse ('bool' e 'int', um 'OrderedDict' e
        # 'dict'), e ali o nome do Python nao serve.
        return "a " + _traduzir_tipos(f"'{type(valor).__name__}'").strip("'")

    # ── Visibilidade e diagnostico de membros ────────────────

    def _conferir_acesso(self, blueprint, membro, env, node):
        """'private' so dentro do proprio blueprint; 'protected' tambem nos herdeiros.

        O escopo diz de onde a leitura partiu: um ambiente '<blueprint X>'
        na cadeia significa que estamos dentro de X.
        """
        visib = blueprint.visibilidade_de(membro)
        if visib == "public":
            return

        # Quem manda na visibilidade e o blueprint que DECLAROU o membro,
        # nao o da instancia. Sem isto, um metodo herdado que le um
        # 'private' da propria classe era recusado: 'self' e da subclasse,
        # e a comparacao dava Base != Derivada.
        dono = blueprint.declarante_de(membro)

        if visib == "internal":
            if (dono.arquivo or "") == (self.filename or ""):
                return
            raise InternalAccessError(
                f"'{dono.name}.{membro}' is internal to "
                f"{_curto(dono.arquivo) if dono.arquivo else 'its file'} and was "
                f"accessed from {_curto(self.filename) if self.filename else 'another file'}.",
                node.line, node.column,
                nota="'internal' opens a member to the file that declares the "
                     "blueprint, and to no other",
                dica="expose a public action that does what this file needs",
                doc="oop/modificadores")

        de_dentro = self._blueprint_do_escopo(env)
        if de_dentro is None:
            onde = "outside any blueprint"
        else:
            if visib == "private" and de_dentro == dono.name:
                return
            if visib == "protected" and any(
                    bp.name == de_dentro for bp in dono.linhagem()):
                return
            # 'protected' tambem vale de dentro de uma subclasse: quem
            # herda enxerga o membro do pai.
            if visib == "protected":
                for bp in blueprint.linhagem():
                    if bp.name == de_dentro:
                        return
            onde = f"from '{de_dentro}'"

        dica = (f"Only '{dono.name}' can read it."
                if visib == "private"
                else f"Only '{dono.name}' and its subtypes can read it.")
        raise TypeError_(
            f"'{dono.name}.{membro}' is {visib} and was accessed {onde}. "
            f"{dica}",
            node.line, node.column)

    @staticmethod
    def _blueprint_do_escopo(env):
        """Nome do blueprint em cujo corpo estamos, ou None."""
        atual = env
        while atual is not None:
            nome = getattr(atual, "name", "") or ""
            if nome.startswith("<blueprint "):
                return nome[len("<blueprint "):-1]
            atual = getattr(atual, "parent", None)
        return None

    def _erro_membro_blueprint(self, blueprint, node):
        """Membro inexistente: diz o que existe, e sugere o parecido."""
        import difflib
        disponiveis = sorted(
            set(blueprint.statics) | set(blueprint.methods) |
            set(blueprint.properties) | {c[0] for c in blueprint.fields_decl})
        de_instancia = ({c[0] for c in blueprint.fields_decl}
                        | set(blueprint.constructor_params))
        if node.member in de_instancia:
            # "Did you mean 'classes'?" para quem escreveu 'classes' era a
            # sugestao mais inutil possivel: o nome existe, so que no OBJETO.
            raise NameError_(
                f"'{node.member}' is a field of each '{blueprint.name}' object, "
                f"not of the blueprint itself.",
                node.line, node.column,
                dica=(f"spawn one and read it there:  (spawn {blueprint.name}(…))."
                      f"{node.member}\n    or declare it  static {node.member} := …  "
                      f"if it belongs to the blueprint"),
                doc="oop/estaticos")
        perto = difflib.get_close_matches(node.member, disponiveis, n=1, cutoff=0.6)

        msg = f"Blueprint '{blueprint.name}' has no member '{node.member}'."
        if perto:
            msg += f"\n    Did you mean '{perto[0]}'?"
        elif disponiveis:
            mostra = ", ".join(disponiveis[:8])
            resto = "…" if len(disponiveis) > 8 else ""
            msg += f"\n    It has: {mostra}{resto}"
        raise NameError_(msg, node.line, node.column)

    #: Excecao do Python -> classe do DataForge. O que nao esta aqui
    #: vira RuntimeError_, que e o pai de quase tudo em 02xx.
    _TRADUCAO_PYTHON = None

    @classmethod
    def _tabela_traducao(cls):
        if cls._TRADUCAO_PYTHON is None:
            cls._TRADUCAO_PYTHON = {
                ZeroDivisionError: DivisionByZeroError,
                KeyError: KeyError_,
                IndexError: IndexError_,
                OverflowError: ArithmeticOverflowError,
                RecursionError: StackOverflowError_,
                UnicodeDecodeError: EncodingError,
                UnicodeEncodeError: EncodingError,
                FileNotFoundError: FileNotFoundError_,
                PermissionError: PermissionError_,
                IsADirectoryError: IOError_,
                NotADirectoryError: IOError_,
                FileExistsError: IOError_,
                OSError: IOError_,
                MemoryError: MemoryLimitError,
                AttributeError: UndefinedMemberError,
                NotImplementedError: NotImplementedError_,
                StopIteration: EmptyCollectionError,
            }
        return cls._TRADUCAO_PYTHON

    def _traduzir_excecao(self, e, node, contexto=""):
        """Uma excecao do Python vira um erro do DataForge.

        Sem isto, tudo o que a stdlib do Python levanta atravessava o
        interpretador cru: '[].min()' terminava num 'Internal Error:
        min() iterable argument is empty' que nem 'monitor' capturava,
        e que fala de um Python que quem escreve DataForge nunca viu.

        A traducao faz duas coisas de uma vez: da ao erro um tipo que
        'handle' entende, e troca o vocabulario do Python pelo da
        linguagem.
        """
        if isinstance(e, DataForgeError):
            return e

        classe = None
        for py, df in self._tabela_traducao().items():
            if isinstance(e, py):
                classe = df
                break

        texto = str(e) or type(e).__name__
        nota = ""
        dica = ""

        # Casos em que a mensagem do Python nao ajuda quem le.
        if isinstance(e, ValueError):
            baixo = texto.lower()
            # 'empty separator' vem de 'split("")', e a colecao ali
            # nao tem nada de vazia. Sem esta linha ele caia no ramo
            # abaixo e a mensagem mandava conferir 'len(xs)' de uma
            # string de tres letras — pior que o erro do Python cru,
            # porque nomeia a coisa errada.
            if "separator" in baixo:
                classe = ValueError_
                texto = "The separator is empty."
                nota = "split needs something to split ON"
                dica = ('to get one item per character, use a comprehension:'
                        '  [c cycle c in texto]')
            elif "empty" in baixo:
                classe = EmptyCollectionError
                texto = "This collection is empty."
                nota = "min, max, first, last and mean need at least one item"
                dica = "check with  given len(xs) bigger 0:  before calling"
            elif "invalid literal" in baixo or "could not convert" in baixo:
                classe = ConversionError
                dica = "use int_ou(x, padrao) when the input may not be a number"
            elif "not in list" in baixo or "not in" in baixo:
                classe = ValueNotFoundError
                # A mensagem do CPython aqui e 'list.remove(x): x not in
                # list' — com 'list' NU, e nao entre aspas, que e a
                # forma que '_traduzir_tipos' sabe trocar. Ela chegava
                # inteira a quem escreve DataForge e mandava procurar
                # por 'list' numa documentacao que so fala de Cluster.
                texto = "This item is not in the collection."
                nota = ("remove, index and pop with a value need the item "
                        "to be there")
                dica = "check with  xs.contains(item)  before removing or indexing"
            elif "slice step" in baixo or "step argument" in baixo:
                classe = SliceError
            else:
                classe = classe or ValueError_
        elif isinstance(e, TypeError):
            baixo = texto.lower()
            if "not iterable" in baixo:
                classe = NotIterableError
            elif "not subscriptable" in baixo:
                classe = NotIndexableError
            elif "unhashable" in baixo:
                classe = NotHashableError
                dica = "vault keys must be immutable: text, number or record"
            elif "not callable" in baixo:
                classe = NotCallableError
            elif "argument" in baixo and (
                    "positional" in baixo or "takes" in baixo
                    # Funcao escrita em C ('math.pow', 'len') diz
                    # "expected 2 arguments, got 1" — sem 'positional' e
                    # sem 'takes'. Sem este ramo ela saia como
                    # 'TypeError' generico, e 'handle ArityError' nao
                    # pegava a MESMA falha dependendo de onde a funcao
                    # foi implementada.
                    or "expected" in baixo or "no arguments" in baixo):
                classe = ArityError
                # A mensagem do Python nomeia a IMPLEMENTACAO:
                #   "ArcaneAnalytics._correlation() missing 2 required
                #    positional arguments: 'x' and 'y'"
                # Nem 'ArcaneAnalytics' nem '_correlation' existem no
                # vocabulario do DataForge: quem escreve chamou
                # 'An.correlation'. Trocar pelo nome chamado e pela
                # assinatura de verdade e o que transforma a mensagem em
                # algo acionavel.
                refeita = self._texto_de_aridade(e, contexto)
                if refeita:
                    texto, nota, dica = refeita
                    contexto = ""     # o nome ja esta no texto
            else:
                classe = classe or TypeError_
        elif isinstance(e, OSError):
            # Um caminho com um caractere de CONTROLE no meio nao veio
            # do disco: veio do lexer. Em "C:\temp\dados.csv" o '\t' e
            # uma tabulacao e o '\d' fica como estava, entao o caminho
            # que chega ao sistema e outro — e a mensagem do Windows
            # para isso e 'Invalid argument', que nao aponta para nada.
            #
            # Custou tres testes do repositorio no Windows, e la eu
            # tinha o caminho impresso para comparar. Quem escreve um
            # caminho do Windows numa string nao tem.
            alvo = str(getattr(e, "filename", "") or "")
            if any(ord(c) < 32 for c in alvo):
                classe = classe or IOError_
                visivel = "".join(
                    {"\t": "\\t", "\n": "\\n", "\r": "\\r"}.get(c, c)
                    if ord(c) < 32 else c
                    for c in alvo)
                texto = (f"This path has a control character in it: "
                         f"'{visivel}'.")
                nota = ("in a string, '\\t' is a tab and '\\n' is a line "
                        "break — a Windows path loses its folders this way")
                dica = ('write the path with forward slashes '
                        '("C:/temp/dados.csv"), which Windows accepts, or '
                        'double every backslash')

        if classe is None:
            classe = RuntimeError_

        # O vocabulario, por ultimo e sempre: a mensagem pode ter vindo
        # de qualquer lugar do Python — de uma comparacao, de um 'len',
        # de uma conversao — e nenhum deles conhece as palavras da
        # linguagem. Quem le DataForge nunca viu 'int', 'str', 'dict'
        # nem 'NoneType', e uma mensagem nesses termos manda a pessoa
        # procurar na documentacao errada.
        # A FRASE inteira, antes dos nomes: um recado conhecido do
        # CPython vira mensagem desta linguagem, com dica. O que nao
        # estiver na tabela segue o caminho de sempre.
        refeito = _refazer_recado(texto)
        if refeito:
            texto, dica_nova = refeito
            dica = dica or dica_nova
            # O 'contexto' — o nome que a pessoa chamou — CONTINUA: ele e
            # o que liga a frase a linha que ela escreveu. Sem ele,
            # "esta conta nao tem resposta real" nao diz qual conta.

        texto = _traduzir_tipos(texto)
        if nota:
            nota = _traduzir_tipos(nota)

        if contexto:
            # O CPython abre a mensagem com a IMPLEMENTACAO que falhou:
            #   "strptime() argument 1 must be String, not Integer"
            # Quem escreve DataForge chamou 'Time.parse', nunca ouviu
            # falar de 'strptime', e o nome chamado ja vai no 'contexto'
            # logo abaixo — entao o nome do Python e ruido que manda
            # procurar na documentacao errada, como o nome de tipo.
            texto = _re.sub(r"^\w+\(\)\s+", "", texto)
            texto = f"{contexto}: {texto}"

        linha = getattr(node, "line", 0)
        coluna = getattr(node, "column", 0)
        return classe(texto, linha, coluna, nota=nota, dica=dica)

    def _texto_de_aridade(self, erro, chamado):
        """A mensagem de aridade no vocabulario de quem chamou.

        Devolve `(texto, nota, dica)`, ou `None` quando nao da para
        fazer melhor que o Python — e nesse caso a mensagem original
        fica, porque uma mensagem crua e melhor que uma inventada.

        O `dataforge check` pega isto ANTES de rodar, com a assinatura
        completa. Esta funcao e a rede: o analisador cala quando nao
        consegue provar (uma acao guardada num vault, uma chamada
        montada em execucao), e e exatamente nesses casos que a pessoa
        chega aqui.
        """
        import inspect
        import re

        alvo = getattr(erro, "__df_alvo__", None)
        # A convencao da stdlib e '_nome' na implementacao, 'nome' no
        # modulo. Quando o nome vem do '__name__' do Python — o caso da
        # funcao guardada num vault, em que o programa nao escreveu nome
        # nenhum — o sublinhado tem de cair, senao a mensagem fala de um
        # simbolo que nao existe para quem escreve.
        nome = (chamado or "").lstrip("_") or "this function"

        faltando = re.search(r"missing (\d+) required positional argument",
                             str(erro))
        nomes = re.findall(r"'([^']+)'", str(erro).split(":", 1)[-1]) \
            if ":" in str(erro) else []

        assinatura = ""
        minimo = maximo = None
        if alvo is not None:
            try:
                sig = inspect.signature(alvo)
                partes = []
                minimo = 0
                maximo = 0
                for par in sig.parameters.values():
                    if par.kind is par.VAR_POSITIONAL:
                        partes.append(f"...{par.name}")
                        maximo = None
                        continue
                    if par.kind is par.VAR_KEYWORD:
                        continue
                    if par.default is inspect.Parameter.empty:
                        partes.append(par.name)
                        minimo += 1
                    else:
                        partes.append(f"{par.name} := {par.default!r}")
                    if maximo is not None:
                        maximo += 1
                assinatura = f"{nome}({', '.join(partes)})"
            except (TypeError, ValueError):
                assinatura = ""

        if faltando and nomes:
            quantos = int(faltando.group(1))
            quais = ", ".join(f"'{n}'" for n in nomes)
            plural = "s" if quantos > 1 else ""
            texto = f"'{nome}' needs {quantos} more argument{plural}: {quais}."
        elif minimo is not None:
            texto = f"'{nome}' was called with the wrong number of arguments."
        else:
            return None

        nota = assinatura
        dica = ""
        if maximo == minimo and minimo is not None:
            dica = f"it takes exactly {minimo}"
        elif minimo is not None and maximo is not None:
            dica = f"it takes {minimo} to {maximo}"
        elif minimo is not None:
            dica = f"it takes {minimo} or more"
        return texto, nota, dica

    def _invocar(self, alvo, args, kwargs, node, contexto=""):
        """Chama um callable do host traduzindo o que ele levantar.

        Todo ponto em que o interpretador entrega o controle a codigo
        Python passa por aqui. Deixar um deles de fora reabre o buraco:
        o erro sobe cru e o programa DataForge nao tem como trata-lo.
        """
        try:
            return alvo(*args, **kwargs)
        except (DataForgeError, ControlSignal):
            raise
        except Exception as e:
            # Quem foi chamado, para a mensagem de aridade poder mostrar
            # a assinatura. Carimbado aqui porque este e o unico ponto
            # que ainda sabe disso: mais acima, so resta a excecao.
            try:
                e.__df_alvo__ = getattr(alvo, "func", alvo)
            except Exception:               # noqa: BLE001
                pass
            raise self._traduzir_excecao(e, node, contexto) from None

    def _call(self, callee, args, kwargs, node, env, instancia=None):
        """Call a callable value.

        Com 'instancia', a acao roda como metodo: 'self' aponta para ela.
        """
        if instancia is not None and isinstance(callee, DFAction):
            return self._call_action(callee, args, kwargs, node, env,
                                     instance=instancia)
        if isinstance(callee, BuiltinFunction):
            return self._invocar(callee, args, kwargs, node)

        if isinstance(callee, DFAction):
            return self._call_action(callee, args, kwargs, node, env)

        if isinstance(callee, DFRecord):
            return self._build_record(callee, args, kwargs, node, env)

        if isinstance(callee, DFEnum):
            # Enum(valor) procura o membro por valor
            if len(args) == 1:
                for membro in callee.members.values():
                    if membro.value == args[0] or membro.name == args[0]:
                        return membro
                raise RuntimeError_(
                    f"Enum '{callee.name}' has no member with value {args[0]!r}",
                    node.line, node.column)
            raise TypeError_(
                f"Calling enum '{callee.name}' takes exactly 1 value",
                node.line, node.column)

        # Uma INSTANCIA chamada com parenteses procura '__call__'.
        # E o que permite um objeto que se comporta como acao — um
        # contador, um cache, um decorador com estado.
        if isinstance(callee, DFInstance):
            acao = self._achar_magico(callee, "__call__")
            if acao is not None:
                return self._call_action(acao, list(args), kwargs, node, env,
                                         instance=callee)
            raise NotCallableError(
                f"'{callee.blueprint.name}' is not callable.",
                node.line, node.column,
                dica="declare  action __call__(…):  to make it callable",
                doc="oop/magicos")

        if isinstance(callee, DFBlueprint):
            # Chamar o blueprint e construir — pelo mesmo caminho do 'spawn'.
            return self._instanciar(callee, list(args), dict(kwargs), node, env)

        if callable(callee):
            # Por '_invocar', e nao por um 'try' proprio: este ramo
            # atendia toda funcao do host chamada por um caminho que nao
            # passa pelo acesso a membro — uma funcao guardada num
            # vault, um callback passado adiante — e levantava
            # 'RuntimeError_' com o texto cru do Python.
            #
            # O sintoma: '[].min()' tinha mensagem traduzida, e
            # 'tabela["corr"]()' devolvia "ArcaneAnalytics._correlation()
            # missing 2 required positional arguments" — um nome de
            # classe e um metodo privado que nao existem no vocabulario
            # do DataForge. E 'handle ArityError' nao pegava, porque o
            # tipo saia 'RuntimeError'.
            return self._invocar(callee, args, kwargs, node,
                                 getattr(callee, "__name__", ""))

        raise TypeError_(f"'{callee}' is not callable", node.line, node.column)

    MAX_CALL_DEPTH = 1000

    def _erro_de_pilha(self, action, node):
        """O teto de quadros, e as duas saidas.

        A mensagem nomeava a acao e perguntava "recursao infinita?" —
        e parava ali. Mas o limite e atingido por recursao LEGITIMA com
        frequencia: uma travessia de arvore de cinco mil nos nao tem
        nada de infinita, e a propria doc de 'cauda.py' diz que
        "qualquer travessia sobre dado real bate nisso".

        Sem dizer as saidas, a pessoa conclui que a linguagem nao serve
        para o problema dela.

        Fica num metodo porque HAVIA DUAS COPIAS desta mensagem — uma
        em '_corpo_da_acao' e outra no caminho com instancia — e eu
        corrigi a que nao era usada no teste. Duas copias de uma
        mensagem divergem; a pergunta nao e se, e quando.
        """
        return StackOverflowError_(
            f"Call stack exceeded {self.MAX_CALL_DEPTH} frames in "
            f"'{getattr(action, 'name', '?')}'.",
            getattr(node, "line", 0), getattr(node, "column", 0),
            nota=("if the recursion is infinite, the base case never "
                  "matched; if it is legitimate, a tree this deep needs "
                  "one of the two ways out"),
            dica=("1. make it a TAIL call — 'yield f(…)' as the whole "
                  "return reuses ONE frame and has no ceiling:\n"
                  "       action somar(n, acc):\n"
                  "           given n is 0:\n"
                  "               yield acc\n"
                  "           yield somar(n - 1, acc + n)\n"
                  "    2. or turn it into a 'cycle' with an explicit "
                  "stack — a cluster of what is left to visit"),
            doc="acoes")

    def _call_action(self, action: DFAction, args, kwargs, node, env, instance=None):
        """Call a user-defined action (function)."""
        if instance is None:
            # Metodo de enum lido a partir do membro: o 'self' dele veio
            # junto, porque o caminho da leitura ate a chamada nao tem
            # onde guardar o dono.
            instance = getattr(action, "self_do_enum", None)
        # Sobrecarga, contrato, trava, invariante e metaclasse. Duas
        # leituras de atributo para quem nao usa nada disso — ver objetos.py.
        if action.extras is not None or (
                instance is not None and instance.__class__ in _COM_VIGIAS
                and instance.blueprint.vigias is not None):
            return self._chamada_especial(action, args, kwargs, node, env, instance)
        self._check_arity(action, args, kwargs, node)

        if getattr(action, 'is_generator', False):
            return self._make_stream(action, args, kwargs, node, instance)

        if getattr(action, 'is_async', False):
            return self._iniciar_tarefa(action, args, kwargs, node, instance)

        if action.tem_cauda is None:
            from .cauda import analisar
            action.tem_cauda = analisar(action)
        if action.tem_cauda:
            return self._corpo_com_salto(action, args, kwargs, node, instance)

        return self._corpo_da_acao(action, args, kwargs, node, instance)

    def _despachar_acao(self, action, args, kwargs, node, instance=None):
        """O despacho de '_call_action', sem o desvio do caminho especial."""
        self._check_arity(action, args, kwargs, node)
        if getattr(action, 'is_generator', False):
            return self._make_stream(action, args, kwargs, node, instance)
        if getattr(action, 'is_async', False):
            return self._iniciar_tarefa(action, args, kwargs, node, instance)
        if action.tem_cauda is None:
            from .cauda import analisar
            action.tem_cauda = analisar(action)
        if action.tem_cauda:
            return self._corpo_com_salto(action, args, kwargs, node, instance)
        return self._corpo_da_acao(action, args, kwargs, node, instance)

    def _chamada_especial(self, action, args, kwargs, node, env, instance):
        """A chamada de uma acao com extras, ou num objeto vigiado.

        A ordem importa, e cada passo tem um motivo:

          1. a sobrecarga escolhe a variante — antes de tudo, porque os
             extras que valem sao os DELA;
          2. 'on_call' da metaclasse, so para chamada de fora do objeto;
          3. a trava do 'exclusive', antes de ler o 'before(…)', senao o
             valor de entrada podia ser de outra thread;
          4. o corpo;
          5. as promessas, com 'outcome' e os 'before' guardados;
          6. as invariantes — so quando a chamada mais de fora termina:
             dentro de um metodo o objeto passa por estados intermediarios,
             e cobrar ali recusaria todo metodo que faz duas escritas.
        """
        extras = action.extras
        if extras is not None and extras.variantes:
            action = objetos.resolver_sobrecarga(self, action, args, kwargs, node)
            extras = action.extras

        vigias = None
        if instance is not None and instance.__class__ in _COM_VIGIAS:
            vigias = instance.blueprint.vigias
        if extras is None and vigias is None:
            return self._despachar_acao(action, args, kwargs, node, instance)

        estado = None
        externo = False
        if vigias is not None:
            estado = objetos.estado_de(instance)
            externo = estado.profundidade == 0 and not estado.construindo
            if externo and "on_call" in vigias.ganchos \
                    and not action.name.startswith("__"):
                self._gancho_de_vigia(vigias, "on_call",
                                      [instance, action.name, list(args)], node)

        trava = None
        if extras is not None and extras.exclusivo and instance is not None:
            trava = objetos.trava_de(instance)
            trava.acquire()
        try:
            antes = None
            if extras is not None and extras.antes:
                escopo = self._ligar_parametros(action, args, kwargs, node, instance)
                antes = {id(n): self.evaluate(n.expression, escopo)
                         for n in extras.antes}
            if estado is not None:
                estado.profundidade += 1
            try:
                resultado = self._despachar_acao(action, args, kwargs, node, instance)
            finally:
                if estado is not None:
                    estado.profundidade -= 1
            if extras is not None and extras.promessas:
                self._conferir_promessas(action, extras, args, kwargs, node,
                                         instance, resultado, antes)
            if (externo and vigias.invariantes and not estado.construindo
                    and getattr(action, "visibilidade", "public") == "public"):
                self._conferir_invariantes(instance, node, action.name)
            return resultado
        finally:
            if trava is not None:
                trava.release()

    def _serve_ao_tipo(self, valor, tipo, acao=None):
        """O valor passa pela anotacao? Sem levantar."""
        try:
            self._check_type(valor, tipo, "overload", self._no_interno(),
                             getattr(acao, "type_params", ()),
                             getattr(acao, "type_bounds", None))
            return True
        except TypeError_:
            return False

    def _corpo_com_salto(self, action, args, kwargs, node, instance=None):
        """O corpo de uma acao que chama a si mesma em cauda.

        E um caminho SEPARADO de proposito. A esmagadora maioria das
        acoes nao tem recursao de cauda, e elas nao podem pagar por um
        laco, um 'try' a mais e um estado por thread que nunca vao usar
        — '_corpo_da_acao' continua exatamente como era.

        O que muda aqui: em vez de empilhar um quadro por volta, reusa-se
        UM. O 'yield f(...)' marcado levanta 'ChamadaDeCauda' com os
        argumentos ja avaliados, e o laco abaixo os religa e recomeca.
        """
        self._depth += 1
        if self._depth > self.MAX_CALL_DEPTH:
            self._depth -= 1
            raise self._erro_de_pilha(action, node)

        self._call_stack.append(Frame(
            action.name, getattr(node, 'line', 0), getattr(node, 'column', 0),
            self.filename))

        por_thread = self._por_thread
        anterior = por_thread.acao
        por_thread.acao = action
        call_env = None
        try:
            while True:
                call_env = self._ligar_parametros(action, args, kwargs,
                                                 node, instance)
                try:
                    if self.compilar_corpos:
                        corpo = action.corpo_compilado
                        if corpo is None:
                            from .compilador import compilar_bloco
                            corpo = action.corpo_compilado = compilar_bloco(
                                self, action.body)
                        corpo(call_env)
                    else:
                        self.exec_block(action.body, call_env)
                    result = None
                except ChamadaDeCauda as salto:
                    # A volta terminou e pediu outra. O escopo desta vai
                    # embora aqui, e nao no fim de todas: uma recursao de
                    # um milhao de voltas nao pode guardar um milhao de
                    # escopos vivos.
                    self._run_deferred(call_env)
                    args, kwargs = salto.argumentos, salto.nomeados
                    continue
                except YieldSignal as ys:
                    result = ys.value
                break
        except RecursionError:
            raise StackOverflowError_(
                f"Python recursion limit reached while running '{action.name}'",
                node.line, node.column)
        except DataForgeError as erro:
            self._attach_stack(erro)
            raise
        finally:
            self._depth -= 1
            self._call_stack.pop()
            por_thread.acao = anterior
            if call_env is not None:
                self._run_deferred(call_env)

        if action.return_type:
            self._check_type(
                result, action.return_type,
                f"return value of action '{action.name}'", node,
                getattr(action, "type_params", ()),
                getattr(action, "type_bounds", None))
        return result

    def _ligar_parametros(self, action, args, kwargs, node, instance=None):
        """Um escopo novo com os parametros dentro. Sem rodar o corpo."""
        call_env = action.closure.child(f"<action {action.name}>")
        params = action.params
        for i, param in enumerate(params):
            if i < len(args):
                value = args[i]
            elif param in kwargs:
                value = kwargs[param]
            elif param in action.defaults:
                value = self.evaluate(action.defaults[param], call_env)
            else:
                value = None
            declared = action.param_types.get(param)
            if declared:
                self._check_type(
                    value, declared,
                    f"parameter '{param}' of action '{action.name}'", node,
                    getattr(action, "type_params", ()),
                getattr(action, "type_bounds", None))
            call_env.set_local(param, value)

        if instance is not None:
            call_env.set_local("self", instance)
            call_env.set_local("this", instance)
            if getattr(action, "dono", None) is not None:
                call_env.set_local("__dono__", action.dono)
        return call_env

    def _corpo_da_acao(self, action: DFAction, args, kwargs, node, instance=None):
        """Liga os parametros e roda o corpo. Sem aridade e sem despacho.

        Separado de '_call_action' porque a tarefa 'async' precisa
        exatamente disto, e so disto: a aridade ja foi conferida na
        thread de quem chamou — e e la que o erro faz sentido, com a
        linha da chamada — e chamar '_call_action' de novo cairia no
        despacho e criaria outra tarefa, para sempre.
        """
        nome_do_escopo = action.nome_do_escopo
        if nome_do_escopo is None:
            nome_do_escopo = action.nome_do_escopo = f"<action {action.name}>"
        call_env = Environment(parent=action.closure, name=nome_do_escopo)
        variaveis = call_env.variables

        # Bind parameters
        params = action.params
        if not kwargs and not action.param_types and len(args) == len(params):
            # O caminho de quase toda chamada: posicional, exata e sem
            # tipo declarado. O escopo acabou de nascer, entao nao ha
            # 'steady' nele para 'set_local' conferir, e nenhum padrao a
            # avaliar — atribuir direto e o mesmo resultado sem as tres
            # consultas por parametro.
            for param, value in zip(params, args):
                variaveis[param] = value
        else:
            for i, param in enumerate(params):
                if i < len(args):
                    value = args[i]
                elif param in kwargs:
                    value = kwargs[param]
                elif param in action.defaults:
                    value = self.evaluate(action.defaults[param], call_env)
                else:
                    value = None
                declared = action.param_types.get(param)
                if declared:
                    self._check_type(
                        value, declared,
                        f"parameter '{param}' of action '{action.name}'", node,
                        getattr(action, "type_params", ()),
                        getattr(action, "type_bounds", None))
                variaveis[param] = value

        # Bind 'self' and 'this' for instance methods — direto no dicionario,
        # pela mesma razao dos parametros: o escopo acabou de nascer.
        if instance is not None:
            variaveis["self"] = instance
            variaveis["this"] = instance
            if action.dono is not None:
                variaveis["__dono__"] = action.dono

        # Execute body, guarding against runaway recursion
        self._depth += 1
        if self._depth > self.MAX_CALL_DEPTH:
            self._depth -= 1
            raise self._erro_de_pilha(action, node)
        self._call_stack.append(Frame(
            action.name, getattr(node, 'line', 0), getattr(node, 'column', 0),
            self.filename))
        # Enquanto o corpo roda, o arquivo corrente e o da acao. E o que
        # faz um erro apontar o arquivo onde o codigo esta, e nao o de
        # quem chamou.
        arquivo_de_quem_chamou = self.filename
        if action.arquivo:
            self.filename = action.arquivo
        try:
            if self.compilar_corpos:
                corpo = action.corpo_compilado
                if corpo is None:
                    from .compilador import compilar_bloco
                    corpo = action.corpo_compilado = compilar_bloco(
                        self, action.body)
                corpo(call_env)
            else:
                self.exec_block(action.body, call_env)
            result = None
        except YieldSignal as ys:
            result = ys.value
        except RecursionError:
            raise StackOverflowError_(
                f"Python recursion limit reached while running '{action.name}'",
                node.line, node.column)
        except DataForgeError as erro:
            self._attach_stack(erro)
            raise
        finally:
            self._depth -= 1
            self._call_stack.pop()
            self.filename = arquivo_de_quem_chamou
            # Deferred blocks run on every exit path, including an error —
            # that is the whole point of 'defer'. A leitura direta do slot
            # evita uma chamada de metodo por chamada de acao em quem nunca
            # escreveu 'defer', que e quase todo mundo.
            if call_env._deferred:
                self._run_deferred(call_env)
        if action.return_type:
            self._check_type(
                result, action.return_type,
                f"return value of action '{action.name}'", node,
                getattr(action, "type_params", ()),
                getattr(action, "type_bounds", None))
        return result

    def _iniciar_tarefa(self, action, args, kwargs, node, instance):
        """Poe uma acao 'async' para correr agora, e devolve a tarefa.

        Comecar na hora — e nao no 'await' — e o que da paralelismo de
        verdade a um padrao como

            tarefas := [buscar(u) cycle u in enderecos]
            paginas := await tarefas

        onde as buscas correm juntas e o 'await' so recolhe. Fosse
        preguicoso, cada uma so comecaria quando a anterior acabasse, e
        'async' seria de novo uma palavra sem efeito.
        """
        return DFTarefa(
            action.name,
            lambda: self._corpo_da_acao(action, args, kwargs, node, instance),
            dono=self, no=node)

    def _make_stream(self, action, args, kwargs, node, instance):
        """Um 'stream action' devolve um DFStream verdadeiramente preguiçoso."""
        interpretador = self

        def produzir():
            call_env = action.closure.child(f"<stream {action.name}>")
            for indice, param in enumerate(action.params):
                if indice < len(args):
                    valor = args[indice]
                elif param in kwargs:
                    valor = kwargs[param]
                elif param in action.defaults:
                    valor = interpretador.evaluate(action.defaults[param], call_env)
                else:
                    valor = None
                call_env.set_local(param, valor)
            if instance is not None:
                call_env.set_local("self", instance)
                call_env.set_local("this", instance)
                if getattr(action, "dono", None) is not None:
                    call_env.set_local("__dono__", action.dono)

            try:
                yield from interpretador._lazy_block(action.body, call_env)
            except YieldSignal:
                pass
            finally:
                interpretador._run_deferred(call_env)

        return DFStream(action.name, produzir)

    # ── Executor preguiçoso de generators ──────────────────
    #
    # 'emit' precisa entregar cada valor no instante em que é produzido, mesmo
    # dentro de um laço infinito. Por isso o corpo de um 'stream action' é
    # percorrido por este executor paralelo, que é um gerador Python: ele desce
    # nas estruturas onde 'emit' pode aparecer e delega o resto ao execute()
    # normal. 'emit' fora dessas estruturas (dentro de outra ação, por exemplo)
    # não é preguiçoso — precisa aparecer no corpo do próprio stream.

    def _lazy_block(self, statements, env):
        for stmt in statements:
            yield from self._lazy_stmt(stmt, env)

    def _lazy_stmt(self, node, env):
        if isinstance(node, ast.EmitStatement):
            valores = [self.evaluate(e, env) for e in node.expressions]
            yield valores[0] if len(valores) == 1 else valores
            return

        if isinstance(node, ast.GivenBlock):
            if self.evaluate(node.condition, env):
                yield from self._lazy_block(node.body, env.child("<given>"))
                return
            for cond, corpo in node.orif_blocks:
                if self.evaluate(cond, env):
                    yield from self._lazy_block(corpo, env.child("<orif>"))
                    return
            if node.otherwise_body:
                yield from self._lazy_block(node.otherwise_body, env.child("<otherwise>"))
            return

        if isinstance(node, ast.CycleFromTo):
            inicio = self.evaluate(node.start, env)
            fim = self.evaluate(node.end, env)
            passo = self.evaluate(node.step, env) if node.step else 1
            i = inicio
            while (passo > 0 and i <= fim) or (passo < 0 and i >= fim):
                escopo = env.child("<cycle>")
                escopo.set_local(node.var, i)
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    pass
                i += passo
            return

        if isinstance(node, ast.ObserveBlock):
            fonte = self.evaluate(node.source, env)
            if isinstance(fonte, dict) and fonte.get("__type__") == "Stream":
                fonte = fonte.get("data", [])
            elif isinstance(fonte, dict):
                fonte = list(fonte.keys())
            for item in fonte:
                escopo = env.child("<observe>")
                escopo.set_local(node.var, item)
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    continue
            return

        if isinstance(node, ast.CycleIn):
            colecao = self.evaluate(node.collection, env)
            if isinstance(colecao, DFStream):
                colecao = iter(colecao)
            elif not hasattr(colecao, '__iter__'):
                raise TypeError_(
                    f"Cannot cycle over {self._type_of(colecao)}",
                    node.line, node.column)
            for item in colecao:
                escopo = env.child("<cycle>")
                escopo.set_local(node.var, item)
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    continue
            return

        if isinstance(node, ast.PersistBlock):
            while self._verdade(self.evaluate(node.condition, env), node):
                escopo = env.child("<persist>")
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    continue
            return

        if isinstance(node, ast.PerformBlock):
            while True:
                escopo = env.child("<perform>")
                try:
                    yield from self._lazy_block(node.body, escopo)
                except HaltSignal:
                    return
                except SkipSignal:
                    pass
                if not self.evaluate(node.condition, env):
                    return

        if isinstance(node, ast.MatchBlock):
            valor = self.evaluate(node.expression, env)
            for caso in node.points:
                if isinstance(caso, tuple):
                    alvo, corpo = caso
                    if valor == self.evaluate(alvo, env):
                        yield from self._lazy_block(corpo, env.child("<point>"))
                        return
                    continue
                ligacoes = {}
                if not self._match_pattern(caso.pattern, valor, env, ligacoes):
                    continue
                escopo = env.child("<point>")
                for nome, ligado in ligacoes.items():
                    escopo.set_local(nome, ligado)
                if caso.guard is not None and not self.evaluate(caso.guard, escopo):
                    continue
                yield from self._lazy_block(caso.body, escopo)
                return
            if node.default_body:
                yield from self._lazy_block(node.default_body, env.child("<default>"))
            return

        if isinstance(node, ast.MonitorBlock):
            try:
                yield from self._lazy_block(node.body, env.child("<monitor>"))
            except Exception as e:
                if not node.handle_body or not self._error_matches(e, node.handle_type, env):
                    raise
                escopo = env.child("<handle>")
                escopo.set_local(node.handle_name, self._error_value(e))
                yield from self._lazy_block(node.handle_body, escopo)
            finally:
                if node.ensure_body:
                    self.exec_block(node.ensure_body, env.child("<ensure>"))
            return

        # Qualquer outra instrução roda normalmente (não produz valores).
        self.execute(node, env)

    def _attach_stack(self, erro):
        """Guarda a pilha no erro, uma única vez (a mais interna vence)."""
        if not getattr(erro, 'stack', None):
            erro.stack = list(self._call_stack)
        if not getattr(erro, 'filename', ''):
            erro.filename = self.filename
        return erro

    def _run_deferred(self, env):
        """Roda os 'defer' do escopo, do ultimo para o primeiro.

        Um erro dentro de um 'defer' era ENGOLIDO — 'except Exception:
        pass'. O 'defer' e onde se fecha arquivo, se desfaz transacao e se
        libera trava, entao o erro que sumia era justamente o de uma
        limpeza que nao aconteceu: o arquivo ficava aberto, o programa
        terminava com codigo 0, e nada dizia que a linha seguinte do
        'defer' nunca rodou.

        Tres regras, e a segunda e a que exige cuidado:

        1. TODOS os 'defer' rodam, mesmo que um falhe. Uma limpeza que
           quebra nao pode impedir a seguinte — e o que o 'defer' promete.
        2. Se a acao JA esta saindo por erro, esse erro continua sendo o
           que viaja, e o do 'defer' vai em '.outros'. Levantar o do
           'defer' no lugar apagaria a causa: quem le ve "nao consegui
           fechar o arquivo" e nunca ve por que a gravacao falhou.
        3. Se a acao saiu bem, o erro do 'defer' e levantado. Com mais de
           um, o primeiro a falhar viaja e os demais pegam carona.

        "Saindo por erro" se le em 'sys.exc_info()': os chamadores rodam
        isto dentro de 'finally', e ali ele traz a excecao em voo. Um
        'yield' ja foi capturado antes do 'finally', entao a saida normal
        chega aqui sem excecao nenhuma.
        """
        if not getattr(env, '_deferred', None):
            return
        import sys as _sys

        falhas = []
        for body, defer_env in reversed(env._deferred):
            try:
                self.exec_block(body, defer_env.child("<defer>"))
            except DataForgeError as erro:
                falhas.append(self._attach_stack(erro))
            except ControlSignal:
                # 'halt'/'skip'/'yield' dentro de um 'defer' nao tem para
                # onde ir: a acao ja esta saindo. Ignora-los e o
                # comportamento de sempre, e nao esconde erro nenhum.
                pass
            except Exception as ex:                       # noqa: BLE001
                falhas.append(self._attach_stack(
                    self._traduzir_excecao(ex, body[0] if body else None)))
        env._deferred.clear()
        if not falhas:
            return

        em_voo = _sys.exc_info()[1]
        if isinstance(em_voo, DataForgeError):
            em_voo.outros = list(getattr(em_voo, "outros", [])) + falhas
            return
        if isinstance(em_voo, BaseException) and not isinstance(
                em_voo, ControlSignal):
            # Excecao do Python em voo: ela vira erro da linguagem mais
            # acima, e nao ha onde pendurar as nossas. Nao substituir e o
            # que importa.
            return
        primeiro = falhas[0]
        primeiro.outros = list(getattr(primeiro, "outros", [])) + falhas[1:]
        raise primeiro

    def _eval_lambda(self, param_name, body_expr, value, env):
        """Evaluate a lambda-like expression for pipelines."""
        local = env.child("<lambda>")
        local.set_local(param_name, value)
        return self.evaluate(body_expr, local)

    # ═══════════════════════════════════════════════════════
    #  DataForge 4.0 — EXPRESSÕES NOVAS
    # ═══════════════════════════════════════════════════════

    def eval_InterpolatedString(self, node, env):
        partes = []
        for tipo, conteudo in node.parts:
            if tipo == 'text':
                partes.append(conteudo)
            elif tipo == 'fmt':
                expressao, formato = conteudo
                partes.append(self._formatar(
                    self.evaluate(expressao, env), formato, node))
            else:
                partes.append(self._to_str(self.evaluate(conteudo, env)))
        return ''.join(partes)

    def _formatar(self, valor, formato, node):
        """'{x:.2f}' — o formato depois dos dois-pontos.

        A gramatica e a mesma do 'format' do Python, e isso e
        deliberado: '.2f', '<10', '>8', ',' e '%' sao o que quem escreve
        ja conhece de outra linguagem, e inventar uma notacao propria
        aqui so criaria uma coisa a mais para consultar.
        """
        try:
            return format(valor, formato)
        except (ValueError, TypeError) as erro:
            raise TypeError_(
                f"não dá para formatar {self._nome_do_tipo(valor)} "
                f"com '{formato}'.",
                getattr(node, "line", 0), getattr(node, "column", 0),
                nota=str(erro),
                dica="'.2f' e ',' pedem número; '<10' e '>8' servem para "
                     "qualquer valor",
                doc="fundamentos/interpolacao") from None

    def eval_TernaryExpression(self, node, env):
        if self.evaluate(node.condition, env):
            return self.evaluate(node.then_value, env)
        return self.evaluate(node.else_value, env)

    def eval_CoalesceOp(self, node, env):
        """a ?? b — 'b' quando 'a' e void.

        Quando o lado esquerdo e uma leitura por indice ou chave, a
        ausencia tambem conta como void:

            porta := config["porta"] ?? 8080

        Sem isso, ler chave que nao existe estouraria antes de o '??'
        rodar — e o operador nao serviria justamente para o caso em que
        mais se precisa dele. O escopo e estreito de proposito: so a
        leitura imediata a esquerda, e so o erro de indice. Qualquer
        outra falha continua subindo.
        """
        try:
            esquerda = self.evaluate(node.left, env)
        except IndexError_:
            if isinstance(node.left, (ast.IndexAccess, ast.MemberAccess)):
                return self.evaluate(node.right, env)
            raise
        if esquerda is None:
            return self.evaluate(node.right, env)
        return esquerda

    def eval_MembershipOp(self, node, env):
        return self._pertence(self.evaluate(node.element, env),
                              self.evaluate(node.container, env),
                              node.negated, node)

    def _pertence(self, elemento, recipiente, negado, node):
        """`x in xs` — com os dois valores ja avaliados."""
        if recipiente is None:
            raise TypeError_(
                "Cannot test membership in void", node.line, node.column)
        try:
            if isinstance(recipiente, DFInstance):
                achado = self._chamar_magico(
                    recipiente, "__contains__", [elemento], node)
                if achado is not _SEM_MAGICO:
                    presente = bool(achado)
                else:
                    # Sem '__contains__', percorre — que e o que o
                    # Python faz, e o que quem escreveu '__iter__'
                    # espera.
                    presente = any(item == elemento
                                   for item in self._percorrer(recipiente, node))
            elif isinstance(recipiente, DFRecordInstance):
                presente = elemento in recipiente.values
            elif isinstance(recipiente, DFEnum):
                presente = any(m == elemento or m.value == elemento
                               for m in recipiente.members.values())
            elif isinstance(recipiente, DFStream):
                presente = any(item == elemento for item in recipiente)
            else:
                presente = elemento in recipiente
        except TypeError:
            raise TypeError_(
                f"Cannot test membership in {self._type_of(recipiente)}",
                node.line, node.column)
        return (not presente) if negado else presente

    def eval_SafeMemberAccess(self, node, env):
        obj = self.evaluate(node.object, env)
        if obj is None:
            return None
        return self.eval_MemberAccess(
            ast.MemberAccess(object=ast._Wrapped(value=obj), member=node.member,
                             line=node.line, column=node.column), env)

    def eval_SafeMethodCall(self, node, env):
        obj = self.evaluate(node.object, env)
        if obj is None:
            return None
        return self.eval_MethodCall(
            ast.MethodCall(object=ast._Wrapped(value=obj), method=node.method,
                           args=node.args, kwargs=node.kwargs,
                           line=node.line, column=node.column), env)

    def eval__Wrapped(self, node, env):
        """Nó interno que carrega um valor já avaliado."""
        return node.value

    def eval_SpreadElement(self, node, env):
        # Um spread solto (fora de literal/chamada) não faz sentido.
        raise RuntimeError_(
            "'...' can only be used inside a list, a vault or a call",
            node.line, node.column)

    def _eval_args(self, nodes, env):
        """Avalia argumentos de chamada, expandindo '...expr'."""
        if any(isinstance(a, ast.SpreadElement) for a in nodes):
            return self._expand_elements(nodes, env)
        return [self.evaluate(a, env) for a in nodes]

    def _expand_elements(self, elementos, env):
        """Avalia elementos de literal expandindo os '...expr'."""
        saida = []
        for elemento in elementos:
            if isinstance(elemento, ast.SpreadElement):
                valor = self.evaluate(elemento.value, env)
                if isinstance(valor, DFStream):
                    valor = list(valor)
                if isinstance(valor, dict):
                    saida.extend(valor.keys())
                elif hasattr(valor, '__iter__') and not isinstance(valor, str):
                    saida.extend(valor)
                elif isinstance(valor, str):
                    saida.extend(valor)
                else:
                    raise TypeError_(
                        f"Cannot spread {self._type_of(valor)}: "
                        f"'...' needs a Cluster, Vault or String",
                        elemento.line, elemento.column)
            else:
                saida.append(self.evaluate(elemento, env))
        return saida

    def _run_clauses(self, clauses, indice, env, emitir):
        """Executa as cláusulas de uma comprehension, recursivamente."""
        clause = clauses[indice]
        fonte = self.evaluate(clause.source, env)
        if isinstance(fonte, DFStream):
            fonte = list(fonte)
        if isinstance(fonte, dict):
            fonte = list(fonte.keys())
        # O '__iter__'/'__next__' MAGICO, como no 'cycle' instrucao.
        #
        # Aqui perguntava 'hasattr(fonte, "__iter__")' — o protocolo do
        # PYTHON — e recusava um objeto que declara o metodo magico da
        # linguagem. A mesma frase funcionava como instrucao e falhava
        # dentro de colchetes:
        #
        #   cycle c in bar:          ok
        #   [c cycle c in bar]       Cannot iterate over Baralho
        #
        # Nao e recurso ausente: e o mesmo recurso respondendo
        # diferente conforme onde foi escrito, e quem le conclui que o
        # objeto nao e percorrivel.
        fonte = self._percorrer(fonte, clause)
        if not hasattr(fonte, '__iter__'):
            raise TypeError_(
                f"Cannot iterate over {self._type_of(fonte)} in the comprehension",
                clause.line, clause.column)

        for item in fonte:
            local = env.child("<comprehension>")
            alvos = clause.targets or [clause.var]
            if len(alvos) == 1:
                local.set_local(alvos[0], item)
            else:
                valores = list(item) if hasattr(item, '__iter__') and not isinstance(item, str) else [item]
                if len(valores) != len(alvos):
                    raise RuntimeError_(
                        f"Cannot unpack {len(valores)} value(s) into "
                        f"{len(alvos)} name(s) in the comprehension",
                        clause.line, clause.column)
                for nome, valor in zip(alvos, valores):
                    local.set_local(nome, valor)

            if clause.condition is not None and not self.evaluate(clause.condition, local):
                continue
            if indice + 1 < len(clauses):
                self._run_clauses(clauses, indice + 1, local, emitir)
            else:
                emitir(local)

    def eval_ListComprehension(self, node, env):
        saida = []
        self._run_clauses(node.clauses, 0, env,
                          lambda escopo: saida.append(
                              self.evaluate(node.expression, escopo)))
        return saida

    def eval_VaultComprehension(self, node, env):
        saida = {}
        def registrar(escopo):
            saida[self.evaluate(node.key, escopo)] = self.evaluate(node.value, escopo)
        self._run_clauses(node.clauses, 0, env, registrar)
        return saida

    def eval_WithExpression(self, node, env):
        base = self.evaluate(node.source, env)
        mudancas = self.evaluate(node.changes, env)
        if not isinstance(mudancas, dict):
            raise TypeError_("'with' needs a vault of changes: obj with {\"campo\": valor}",
                             node.line, node.column)
        if isinstance(base, DFRecordInstance):
            return base.replace(mudancas)
        if isinstance(base, dict):
            return {**base, **mudancas}
        if isinstance(base, DFInstance):
            # 'fields' e uma vista: atribuir a ela estourava. A copia nasce
            # pelo mesmo caminho de Objetos.clonar, e as mudancas passam
            # pelas regras de escrita — so o 'readonly' fica livre, porque
            # 'with' e a construcao de um objeto novo.
            copia = copiar_instancia(base)
            estado = objetos.estado_de(copia)
            estado.construindo = True
            try:
                for chave, valor in mudancas.items():
                    self._escrever_membro(copia, chave, valor, node, env)
            finally:
                estado.construindo = False
            return copia
        raise TypeError_(
            f"'with' does not apply to {self._type_of(base)}: "
            f"use it on a record, a vault or a blueprint instance",
            node.line, node.column)

    # ── Type annotations (checked at runtime) ──────────────

    TYPE_ALIASES = {
        "integer": "Integer", "int": "Integer", "Integer": "Integer",
        "float": "Float", "Float": "Float", "number": "Number", "Number": "Number",
        "string": "String", "str": "String", "String": "String", "text": "String",
        "boolean": "Boolean", "bool": "Boolean", "Boolean": "Boolean",
        "cluster": "Cluster", "list": "Cluster", "Cluster": "Cluster", "array": "Cluster",
        "vault": "Vault", "dict": "Vault", "Vault": "Vault", "map": "Vault",
        "void": "Void", "Void": "Void", "none": "Void",
        "action": "Action", "Action": "Action", "function": "Action",
        "set": "Set", "Set": "Set",
        "tuple": "Tuple", "Tuple": "Tuple",
        "frozen": "Frozen", "Frozen": "Frozen",
        "bytes": "Bytes", "Bytes": "Bytes",
        "any": "Any", "Any": "Any",
    }

    def _target_name(self, target) -> str:
        if isinstance(target, ast.Identifier):
            return target.name
        return "<expression>"

    def _type_of(self, value) -> str:
        # Um valor opaco responde pelo NOME do tipo: e o que 'typeof' tem
        # de dizer, e o que faz a mensagem de erro nomear 'Cpf'.
        if isinstance(value, Opaco):
            return value.tipo
        if isinstance(value, bool):
            return "Boolean"
        if isinstance(value, int):
            return "Integer"
        if isinstance(value, float):
            return "Float"
        # Numero que veio do outro lado da ponte. 'np.int64' nao e
        # subclasse de 'int', mas FAZ conta de inteiro — e e isso que
        # 'typeof' responde, senao 'given typeof(x) is "Integer"' seria
        # falso para um valor que soma, divide e compara como um.
        #
        # 'numbers' e o protocolo padrao do Python para isto; nao ha
        # nada de numpy aqui, e 'Fraction' e 'Decimal' entram pela
        # mesma porta.
        if isinstance(value, _numeros.Integral):
            return "Integer"
        if isinstance(value, _numeros.Real):
            return "Float"
        if isinstance(value, str):
            return "String"
        # 'Tupla' e a tupla da linguagem; a 'tuple' crua e o 'Frozen' —
        # um Cluster congelado, que 'freeze' e a ponte devolvem.
        if isinstance(value, _Tupla):
            return "Tuple"
        if isinstance(value, list):
            return "Cluster"
        if isinstance(value, dict):
            return "Vault"
        # Os quatro abaixo caiam no 'type(value).__name__' la embaixo e
        # respondiam com a palavra do PYTHON — 'set', 'tuple', 'bytes'.
        # Nenhuma delas existe nesta linguagem, e quem le nao tem onde
        # procurar. Nao era so o 'typeof': '_check_type' usa esta
        # funcao para dizer o que CHEGOU, entao um erro de tipo tambem
        # dizia 'got tuple'.
        #
        # 'freeze' e EMBUTIDA — nao precisa nem de 'adopt' para chegar
        # la: 'typeof(freeze([1, 2]))' respondia 'tuple'.
        if isinstance(value, (set, frozenset)):
            return "Set"
        if isinstance(value, tuple):
            # O que 'freeze' devolve. A linguagem nao tem tupla; tem um
            # Cluster congelado, e e assim que ele se chama.
            return "Frozen"
        if isinstance(value, (bytes, bytearray)):
            return "Bytes"
        if value is None:
            return "Void"
        if isinstance(value, DFInstance):
            return value.blueprint.name
        if isinstance(value, DFRecordInstance):
            return value.record.name
        if isinstance(value, DFRecord):
            return "Record"
        if isinstance(value, DFEnumMember):
            return value.enum_name
        if isinstance(value, DFEnum):
            return "Enum"
        if isinstance(value, DFStream):
            return "Stream"
        if isinstance(value, DFBlueprint):
            return "Blueprint"
        if isinstance(value, (DFAction, BuiltinFunction)) or callable(value):
            return "Action"
        return type(value).__name__

    def _check_type(self, value, declared: str, what: str, node,
                    parametros_de_tipo=(), limites=None):
        """Enforce a declared type annotation. Unknown names name a blueprint.

        Um parametro de tipo ('T' de 'action primeiro<T>(l) -> T') aceita
        qualquer valor: a linguagem e de tipagem dinamica, e o parametro
        existe para documentar a relacao entre entrada e saida, nao para
        ser verificado em tempo de execucao. E o mesmo que o TypeScript
        faz ao compilar — os tipos somem.
        """
        # Um 'type' declarado vem ANTES de tudo: ele pode dar nome a uma
        # colecao ('type Ids := Cluster<Id>'), e aí quem manda é ele.
        if self.tipos_nomeados and declared not in self.TYPE_ALIASES:
            nomeado, _ = self._tipo_declarado(declared)
            if nomeado is not None:
                return self._checar_tipo_nomeado(
                    nomeado, value, declared, what, node,
                    parametros_de_tipo, limites)
        # 'Integer | String' escrito direto na anotação, sem nome.
        if _TiposNomeados.e_composto(declared):
            return self._checar_composto_anonimo(
                value, declared, what, node, parametros_de_tipo, limites)
        if "<" in declared:
            base_declarada = _partir_tipo(declared)[0]
            if base_declarada not in self.TYPE_ALIASES:
                proprio = self._generico_do_usuario(base_declarada)
                if proprio is not None:
                    return self._conferir_generico_do_usuario(
                        proprio, value, declared, what, node)
            return self._check_conteudo(value, declared, what, node,
                                        parametros_de_tipo, limites)
        expected = self.TYPE_ALIASES.get(declared, declared)
        if expected in parametros_de_tipo:
            limite = (limites or {}).get(expected)
            if not limite:
                return value
            # Um 'T' com limite e verificavel, e por isso e verificado. O
            # '<T>' solto continua aceitando tudo: ele documenta a relacao
            # entre entrada e saida, e nao promete nada sobre o valor.
            try:
                return self._check_type(value, limite, what, node)
            except TypeError_:
                raise TypeError_(
                    f"{what} is a {expected}, and {expected} extends "
                    f"{limite} — but got {self._type_of(value)}",
                    node.line, node.column,
                    nota=f"declared as <{expected} extends {limite}>",
                    dica=f"pass a value that is a {limite}") from None
        if expected == "Any":
            return value
        actual = self._type_of(value)

        # Um tipo QUALIFICADO ('M.Pedido') e o mesmo tipo de sempre
        # visto de outro arquivo. Um record nao carrega o apelido de
        # quem o importou — e nem poderia: o mesmo 'Pedido' e 'M.Pedido'
        # aqui, 'P.Pedido' no vizinho e 'Pedido' em casa. A comparacao
        # e pelo ultimo segmento, que e o nome de verdade.
        if expected not in self.TYPE_ALIASES and "." in expected:
            expected = expected.rsplit(".", 1)[1]

        if expected == "Number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError_(
                    f"{what} declared as Number but got {actual}", node.line, node.column)
            return value
        if expected == "Float" and isinstance(value, int) and not isinstance(value, bool):
            return value  # an Integer widens to Float
        if expected == actual:
            return value
        if isinstance(value, DFInstance) and self._descende_de(value, expected):
            return value
        raise TypeError_(
            f"{what} declared as {expected} but got {actual}", node.line, node.column)

    def _recusar_escrita_em_tupla(self, node):
        raise TypeError_(
            "a Tuple is immutable: it has no item assignment.",
            getattr(node, "line", 0), getattr(node, "column", 0),
            nota="that is what separates a Tuple from a Cluster",
            dica="build another one, or use a Cluster if it has to change",
            doc="tipos/tuplas")

    def _check_conteudo(self, value, declared, what, node,
                        parametros_de_tipo=(), limites=None):
        """'Cluster<T>', 'Vault<K, V>', 'Set<T>': a colecao, e cada item.

        O item errado e nomeado pela POSICAO (ou pela chave): numa lista de
        mil, "got String" sem dizer onde obrigaria a procurar a mao.
        """
        base, argumentos = _partir_tipo(declared)
        esperado_base = self.TYPE_ALIASES.get(base, base)
        try:
            self._check_type(value, esperado_base, what, node)
        except TypeError_:
            raise TypeError_(
                f"{what} declared as {declared} but got {self._type_of(value)}",
                node.line, node.column, doc="tipos") from None

        def conferir(item, tipo, onde):
            try:
                self._check_type(item, tipo, onde, node,
                                 parametros_de_tipo, limites)
            except TypeError_ as erro:
                interno = ("" if "<" not in tipo else f" — {erro.message}")
                raise TypeError_(
                    f"{what} declared as {declared}, but {onde} is "
                    f"{self._type_of(item)}{interno}",
                    node.line, node.column,
                    dica=f"every item has to be a {tipo}; widen the "
                         f"annotation (Any accepts everything) or fix the value",
                    doc="tipos") from None

        if esperado_base == "Tuple":
            # Na tupla, a quantidade de argumentos E o tamanho: um item a
            # mais nao e "um item errado", e uma tupla de outra forma.
            if len(value) != len(argumentos):
                raise TypeError_(
                    f"{what} declared as {declared}, which has "
                    f"{len(argumentos)} place(s), but got {len(value)}",
                    node.line, node.column,
                    nota="the size of a Tuple is part of its type",
                    dica=f"write a Tuple with {len(argumentos)} place(s)",
                    doc="tipos/tuplas")
            for indice, (item, tipo) in enumerate(zip(value, argumentos)):
                if tipo != "Any":
                    conferir(item, tipo, f"place {indice}")
            return value
        if esperado_base in ("Cluster", "Set"):
            if argumentos[0] in ("Any",):
                return value
            for indice, item in enumerate(value):
                conferir(item, argumentos[0],
                         f"item {indice}" if esperado_base == "Cluster" else "an item")
        elif esperado_base == "Vault":
            chave_t, valor_t = argumentos
            for chave, item in value.items():
                if chave_t != "Any":
                    try:
                        self._check_type(chave, chave_t, what, node)
                    except TypeError_:
                        raise TypeError_(
                            f"{what} declared as {declared}, but the key "
                            f"{self._to_repr(chave)} is {self._type_of(chave)}",
                            node.line, node.column,
                            dica=f"every key has to be a {chave_t}",
                            doc="tipos") from None
                if valor_t != "Any":
                    conferir(item, valor_t, f"the value at key {self._to_repr(chave)}")
        return value

    def _texto_de_tupla(self, valor):
        """'(1, "a")' — e '(7,)' com um item, como a linguagem a escreve."""
        dentro = ", ".join(self._to_repr(item) for item in valor)
        if len(valor) == 1:
            dentro += ","
        return f"({dentro})"

    def _to_repr(self, valor):
        """O valor como aparece no codigo: texto entre aspas."""
        return f'"{valor}"' if isinstance(valor, str) else self._to_str(valor)

    @staticmethod
    def _descende_de(instancia, nome):
        """A instancia e daquele blueprint, de uma mae, ou adota o trait?

        So a MRO era olhada, e trait nao esta nela: 'tamanho(m: Medivel)'
        recebendo uma 'Caixa' que adota 'Medivel' levantava "declared as
        Medivel but got Caixa". Um trait como tipo de parametro e o motivo
        de o trait existir, e era o unico uso dele que a execucao recusava.
        """
        for bp in instancia.get_mro():
            if bp.name == nome:
                return True
            for trait in (getattr(bp, "traits", None) or ()):
                if (getattr(trait, "name", trait)) == nome:
                    return True
        # um contrato que o contrato adotado estende tambem vale:
        # 'with Repositorio' onde 'contract Repositorio extends Leitura'
        # serve onde se pede Leitura
        return nome in getattr(instancia.blueprint, "contratos_todos", ())

    def _check_arity(self, action, args, kwargs, node):
        """Reject calls with too few or too many arguments."""
        params = action.params
        # O caso de quase toda chamada: so posicionais, e exatamente um por
        # parametro. Nada falta, nada sobra, nenhum nome desconhecido — e
        # as tres compreensoes abaixo rodavam mesmo assim, em TODA chamada.
        if not kwargs and len(args) == len(params):
            return
        required = [p for p in params if p not in action.defaults]
        supplied = set(params[:len(args)]) | set(kwargs)
        missing = [p for p in required if p not in supplied]
        if missing:
            raise TypeError_(
                f"action '{action.name}' is missing argument(s): {', '.join(missing)}",
                node.line, node.column)
        if len(args) > len(params):
            raise TypeError_(
                f"action '{action.name}' takes {len(params)} argument(s) "
                f"but {len(args)} were given",
                node.line, node.column)
        unknown = [k for k in kwargs if k not in params]
        if unknown:
            raise TypeError_(
                f"action '{action.name}' got unexpected argument(s): {', '.join(unknown)}",
                node.line, node.column)

    def _to_str(self, value) -> str:
        """Convert a DataForge value to its string representation."""
        if value is None:
            return "void"
        if isinstance(value, bool):
            return "yes" if value else "no"
        if isinstance(value, DFInstance):
            # '__str__' primeiro, depois 'toString' — que veio antes e
            # continua valendo — e por fim '__repr__', que serve de
            # reserva como no Python.
            for nome in ("__str__", "toString", "__repr__"):
                acao = self._achar_magico(value, nome)
                if acao is None and nome == "toString":
                    acao = value.get(nome) if value.has_method(nome) else None
                if isinstance(acao, DFAction):
                    return str(self._call_action(
                        acao, [], {}, self._no_interno(), None, instance=value))
            return f"<{value.blueprint.name} instance>"
        if isinstance(value, DFBlueprint):
            return f"<blueprint {value.name}>"
        if isinstance(value, DFAction):
            return f"<action {value.name}>"
        if isinstance(value, DFChannel):
            return f"<channel {value.name}>"
        if isinstance(value, DFError):
            return value.message
        if isinstance(value, DFRecordInstance):
            if 'toString' in value.record.methods:
                no = type('_N', (), {'line': 0, 'column': 0})()
                return str(self._call_action(
                    value.record.methods['toString'], [], {}, no, None,
                    instance=value))
            campos = ', '.join(f"{k}: {self._to_str(v)}"
                               for k, v in value.values.items())
            return f"{value.record.name}({campos})"
        if isinstance(value, DFRecord):
            return f"<record {value.name}>"
        if isinstance(value, DFEnumMember):
            return f"{value.enum_name}.{value.name}"
        if isinstance(value, DFEnum):
            return f"<enum {value.name}>"
        if isinstance(value, DFStream):
            return f"<stream {value.name}>"
        if isinstance(value, _Tupla):
            return self._texto_de_tupla(value)
        if isinstance(value, list):
            items = ', '.join(self._to_str(i) for i in value)
            return f"[{items}]"
        if isinstance(value, dict):
            if "__type__" in value:
                return f"<{value['__type__']}>"
            pairs = ', '.join(f"{self._to_str(k)}: {self._to_str(v)}" for k, v in value.items())
            return '{' + pairs + '}'
        return str(value)

    def _load_module_file(self, path, module_name):
        """Executa um arquivo .df como módulo e devolve o que ele exporta."""
        import os
        from .lexer import tokenize
        from .parser import parse

        real = os.path.abspath(path)
        if real in self._loading:
            cadeia = " → ".join(os.path.basename(p) for p in self._loading)
            raise ImportError_(
                f"Circular import: {cadeia} → {os.path.basename(real)}. "
                f"Break the cycle by moving the shared part into a third module.")

        with open(path, 'r', encoding='utf-8') as f:
            fonte = f.read()

        tokens = tokenize(fonte, path)
        arvore = parse(tokens, path)

        mod_env = self.global_env.child(f"<module {module_name}>")
        arquivo_anterior = self.filename
        self._loading.append(real)
        self.filename = path
        try:
            self.exec_block(arvore.body, mod_env)
        finally:
            self._loading.pop()
            self.filename = arquivo_anterior

        exportados = getattr(mod_env, '_exports', None)
        if exportados:
            objeto = {nome: mod_env.get(nome) for nome in exportados
                      if mod_env.has(nome)}
        else:
            objeto = dict(mod_env.variables)
        objeto["__name__"] = module_name
        objeto["__file__"] = path
        self.modules[module_name] = objeto
        return objeto
