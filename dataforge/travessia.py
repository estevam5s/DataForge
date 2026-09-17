"""
A travessia de processo — o que uma acao leva consigo para outro nucleo.

    somas := P.map_processos(calcular, blocos)

Essa linha e a unica forma de usar mais de um nucleo: duas threads
Python nunca executam bytecode ao mesmo tempo, e para trabalho que
CALCULA oito threads levam o mesmo tempo que uma. E ela nao funcionava.

─── Por que nao funcionava ─────────────────────────────────

Um processo recebe o trabalho por copia, e a copia e feita pelo
'pickle'. Uma acao de DataForge e uma 'DFAction', e ela guarda o
FECHAMENTO — o escopo onde nasceu. No topo de um arquivo esse escopo e
o global, e o global tem os 228 embutidos, os modulos ja adotados e,
dentro deles, funcoes anonimas. Nada disso atravessa.

O resultado era que 'map_processos' falhava SEMPRE, com uma mensagem
que culpava quem escreveu:

    erro: this action cannot cross into another process:
          Can't get local object 'ArcaneConcurrent.__new__.<locals>.<lambda>'
    dica: declare a acao no topo do arquivo

A acao ESTAVA no topo do arquivo. O objeto que o pickle nao conseguia
copiar era um lambda da propria biblioteca, alcancado pela cadeia de
escopos. A dica mandava consertar o que ja estava certo.

─── O que este arquivo faz ─────────────────────────────────

Nao copia o fechamento: copia a DECLARACAO.

O que atravessa e a arvore da acao, mais os nomes que ela LE e nao
declara, mais as declaracoes que esses nomes alcancam — records, enums,
blueprints e outras acoes, recursivamente. Do outro lado, um
interpretador novo remonta tudo num escopo proprio e chama a acao.

    parent                          filho
    ──────                          ─────
    DFAction 'cpu'                  Interpreter()          (uma vez)
      fechamento -> global    ✗       raiz = global.child()
      corpo (arvore)          ✓  ->   DFAction('cpu', corpo, raiz)
      livres: {taxa: 0.2}     ✓  ->   raiz['taxa'] = 0.2
      livres: {Pedido: rec}   ✓  ->   raiz['Pedido'] = DFRecord(...)

Os VALORES seguem pelo mesmo caminho: um record que vai como argumento
carrega o indice do tipo, e nao o tipo inteiro por item.

─── O que nao atravessa, e como isso e dito ────────────────

Uma conexao de banco, um arquivo aberto, um socket, um mutex, um canal
e uma tarefa existem no processo que os abriu. Copia-los nao faria
sentido: o outro lado ganharia um numero de descritor que la nao aponta
para nada.

Quando um nome livre e um desses, ele NAO viaja — e tambem nao levanta
na hora. O motivo fica guardado, e so aparece se a acao realmente
usar o nome:

    erro: 'conexao' cannot cross into another process
    nota: it holds a Database connection, which exists only in the
          process that opened it

Levantar na hora seria falso alarme: a varredura de nomes livres e
generosa de proposito — ela prefere capturar demais a capturar de menos
— e um nome capturado sem necessidade nao pode derrubar um programa que
funciona.
"""

import pickle
from .builtins import _df_type as _nome_do_tipo

#: O que ja e um valor, e nao precisa de traducao.
_SIMPLES = (type(None), bool, int, float, complex, str, bytes, bytearray)


class NaoAtravessa(Exception):
    """Algo que o processo filho nao teria como receber."""

    def __init__(self, mensagem, nota="", dica=""):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.nota = nota
        self.dica = dica


class _Ref:
    """Um valor que do outro lado precisa ser remontado, e nao copiado."""

    __slots__ = ("especie", "indice", "dados")

    def __init__(self, especie, indice=-1, dados=None):
        self.especie = especie
        self.indice = indice
        self.dados = dados

    def __reduce__(self):
        return (_Ref, (self.especie, self.indice, self.dados))

    def __repr__(self):
        return f"<_Ref {self.especie}:{self.indice}>"


class _Declaracao:
    """Uma acao, record, enum ou blueprint na forma que atravessa."""

    __slots__ = ("especie", "campos")

    def __init__(self, especie, campos):
        self.especie = especie
        self.campos = campos

    def __reduce__(self):
        return (_Declaracao, (self.especie, self.campos))


# ═══════════════════════════════════════════════════════════
#  Os nomes que um corpo LE e nao declara
# ═══════════════════════════════════════════════════════════

def nomes_livres(corpo, ligados):
    """Os nomes que este corpo usa e nao cria, na ordem em que aparecem.

    A varredura e GENEROSA: na duvida, captura. Um nome capturado sem
    necessidade custa uma copia a mais; um nome esquecido vira
    "'x' is not defined" dentro do processo filho, longe da causa.

    O que a torna precisa o bastante para nao capturar toda variavel
    local e a ORDEM: 'total := 0' antes de 'total + x' liga o nome, e
    dali em diante ele e local. Uma atribuicao COMPOSTA ('total += x')
    le antes de ligar, e por isso conta como leitura.
    """
    from . import ast_nodes as ast

    livres = []
    vistos = set()

    def ler(nome):
        if not nome or nome in ligados or nome in vistos:
            return
        vistos.add(nome)
        livres.append(nome)

    def ler_tipo(texto):
        """'Pedido' numa anotacao e um nome como outro qualquer.

        Sem isto, 'action total(p: Pedido)' atravessava sem o record, e
        a conferencia de tipo do filho nao achava 'Pedido' — um erro
        sobre a anotacao, e nao sobre o que a acao faz.
        """
        if not texto or not isinstance(texto, str):
            return
        # 'Cluster<Pedido>' e 'Pedido?' tambem nomeiam o record.
        for parte in texto.replace("<", " ").replace(">", " ") \
                          .replace("?", " ").replace(",", " ").split():
            raiz = parte.split(".")[0].strip()
            if raiz and (raiz[0].isalpha() or raiz[0] == "_"):
                ler(raiz)

    def ligar(alvo):
        if isinstance(alvo, str):
            ligados.add(alvo)
        elif isinstance(alvo, (list, tuple)):
            for x in alvo:
                ligar(x[0] if isinstance(x, tuple) else x)

    def padrao(p):
        """Um padrao LIGA nomes e LE tipos."""
        if not isinstance(p, ast.ASTNode):
            return
        ligar(getattr(p, "binding", ""))
        if isinstance(p, ast.CapturePattern):
            ligar(p.name)
        elif isinstance(p, ast.TypePattern):
            ler(p.type_name.split(".")[0])
            for sub in p.sub_patterns:
                padrao(sub)
            for sub in p.field_patterns.values():
                padrao(sub)
        elif isinstance(p, ast.SequencePattern):
            ligar(p.rest_name)
            for sub in p.elements:
                padrao(sub)
        elif isinstance(p, ast.MappingPattern):
            ligar(p.rest_name)
            for chave, sub in p.pairs:
                anda(chave)
                padrao(sub)
        elif isinstance(p, ast.ValuePattern):
            anda(p.expression)
        elif isinstance(p, ast.OrPattern):
            for sub in p.options:
                padrao(sub)

    def anda(no):
        if isinstance(no, (list, tuple)):
            for x in no:
                anda(x)
            return
        if isinstance(no, dict):
            for x in no.values():
                anda(x)
            return
        if not isinstance(no, ast.ASTNode):
            return

        if isinstance(no, ast.Identifier):
            ler(no.name)
            return

        if isinstance(no, ast.MemberAccess):
            anda(no.object)              # 'member' e texto, nao nome
            return

        if isinstance(no, ast.Assignment):
            anda(no.value)
            ler_tipo(getattr(no, "declared_type", ""))
            alvo = no.target
            if isinstance(alvo, ast.Identifier):
                # 'x += 1' LE antes de escrever.
                if getattr(no, "compound_op", ""):
                    ler(alvo.name)
                ligar(alvo.name)
            else:
                anda(alvo)
            return

        if isinstance(no, ast.DestructuringAssignment):
            anda(no.value)
            ligar(no.targets)
            return

        if isinstance(no, ast.CycleFromTo):
            anda(no.start); anda(no.end); anda(no.step)
            ligar(no.var)
            anda(no.body)
            return

        if isinstance(no, ast.CycleIn):
            anda(no.collection)
            ligar(no.var)
            ligar(no.vars)
            anda(no.body)
            return

        if isinstance(no, ast.MonitorBlock):
            anda(no.body)
            for h in no.handles:
                ler(h.error_type.split(".")[0] if h.error_type else "")
                ligar(h.error_name)
                anda(h.body)
            anda(no.ensure_body)
            return

        if isinstance(no, ast.HandleClause):
            ligar(no.error_name)
            anda(no.body)
            return

        if isinstance(no, ast.Pattern):
            padrao(no)
            return

        if isinstance(no, ast.LambdaExpression):
            anda(no.defaults)
            dentro = set(ligados)
            ligar_em(dentro, no.params)
            livres.extend(_livres_aninhados(no.body, dentro, vistos, livres))
            return

        if isinstance(no, ast.ActionDeclaration):
            anda(no.defaults)
            for t in no.param_types.values():
                ler_tipo(t)
            ler_tipo(no.return_type)
            ligar(no.name)
            dentro = set(ligados)
            dentro.add(no.name)
            ligar_em(dentro, no.params)
            livres.extend(_livres_aninhados(no.body, dentro, vistos, livres))
            return

        if isinstance(no, ast.AdoptStatement):
            # 'adopt' dentro da acao roda no filho como aqui.
            if no.alias:
                ligar(no.alias)
            elif no.selection:
                ligar([(a or n) for n, a in no.selection])
            else:
                ligar(no.module.split(".")[-1])
            return

        if isinstance(no, (ast.RecordDeclaration, ast.EnumDeclaration,
                           ast.BlueprintDeclaration)):
            ligar(no.name)
            # O corpo de uma declaracao aninhada e varrido com o nome
            # dela ja ligado: um metodo que se chama de volta nao pode
            # virar nome livre.
            for campo in getattr(no, "__dataclass_fields__", ()):
                if campo == "name":
                    continue
                anda(getattr(no, campo, None))
            return

        for campo in getattr(no, "__dataclass_fields__", ()):
            valor = getattr(no, campo, None)
            if campo in ("declared_type", "return_type"):
                ler_tipo(valor)
            elif campo == "param_types" and isinstance(valor, dict):
                for t in valor.values():
                    ler_tipo(t)
            elif isinstance(valor, (ast.ASTNode, list, tuple, dict)):
                anda(valor)

    def ligar_em(conjunto, params):
        for p in params:
            conjunto.add(p[0] if isinstance(p, (list, tuple)) else p)

    anda(corpo)
    return livres


def _livres_aninhados(corpo, ligados, vistos, ja):
    """Os livres de um corpo aninhado, sem repetir o que ja saiu."""
    novos = []
    for nome in nomes_livres(corpo, set(ligados)):
        if nome not in vistos:
            vistos.add(nome)
            novos.append(nome)
    return novos


def _nomes_dos_params(params):
    return {p[0] if isinstance(p, (list, tuple)) else p for p in params}


# ═══════════════════════════════════════════════════════════
#  Empacotar: do processo que tem, para o que vai receber
# ═══════════════════════════════════════════════════════════

class Empacotador:
    """Traduz valores e declaracoes para a forma que atravessa.

    As tabelas sao COMPARTILHADAS entre a acao e os itens: um record
    que aparece em mil pedidos e copiado uma vez, e cada pedido leva
    so o indice.
    """

    def __init__(self, declaracoes=None, indice=None):
        self.declaracoes = declaracoes if declaracoes is not None else []
        self._por_id = indice if indice is not None else {}
        #: indice -> o objeto original. Ele fica guardado por dois
        #: motivos: para o resultado que volta do filho apontar para o
        #: MESMO record daqui, e porque 'id()' so e unico entre objetos
        #: VIVOS — sem esta referencia, um record coletado cederia o
        #: endereco a outro, e o indice passaria a nomear o errado.
        self._objetos = {}
        #: nome livre -> motivo, para quando o filho reclamar dele.
        self.faltas = {}
        self._memo = {}

    def originais(self):
        """Indice -> o objeto deste processo, para decodificar a volta."""
        return dict(self._objetos)

    # ── valores ──────────────────────────────────────────

    def valor(self, v):
        from .interpreter import (DFAction, DFBlueprint, DFEnum,
                                  DFEnumMember, DFInstance, DFRecord,
                                  DFRecordInstance)

        if isinstance(v, _SIMPLES):
            return v

        chave = id(v)
        if chave in self._memo:
            return self._memo[chave]

        if isinstance(v, DFAction):
            return _Ref("decl", self.declaracao(v))
        if isinstance(v, (DFRecord, DFEnum, DFBlueprint)):
            return _Ref("decl", self.declaracao(v))
        if isinstance(v, DFRecordInstance):
            return _Ref("rec", self.declaracao(v.record),
                        {k: self.valor(x) for k, x in v.values.items()})
        if isinstance(v, DFInstance):
            return _Ref("inst", self.declaracao(v.blueprint),
                        {k: self.valor(x) for k, x in v.fields.items()})
        if isinstance(v, DFEnumMember):
            # Pelo ENUM e pelo nome, e nao por copia. Um membro copiado
            # chega do outro lado sem o enum a que pertence, e o metodo
            # declarado nele fica inalcancavel — 'Faixa.Alta.dobro()'
            # respondia "has no member 'dobro'" DEPOIS de atravessar, e
            # so depois.
            #
            # Pelo enum, os dois lados devolvem o membro de verdade: o
            # mesmo objeto no processo que o declarou.
            enum = getattr(v, "enum", None)
            if enum is not None:
                return _Ref("membro", self.declaracao(enum), v.name)

        if isinstance(v, dict):
            nome = v.get("__name__")
            if isinstance(nome, str) and _e_modulo(nome, v):
                return _Ref("modulo", -1, nome)
            saida = {}
            self._memo[chave] = saida
            for k, x in v.items():
                saida[self.valor(k)] = self.valor(x)
            return saida

        if isinstance(v, list):
            saida = []
            self._memo[chave] = saida
            saida.extend(self.valor(x) for x in v)
            return saida

        if isinstance(v, tuple):
            return tuple(self.valor(x) for x in v)
        if isinstance(v, (set, frozenset)):
            return type(v)(self.valor(x) for x in v)

        # O resto: se o pickle da conta sozinho, esta bom — e por aqui
        # que passam datetime, Decimal, Fraction, um ndarray do numpy.
        try:
            pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:                    # noqa: BLE001
            raise NaoAtravessa(_motivo(v), dica=_dica(v)) from None
        return v

    # ── declaracoes ──────────────────────────────────────

    def declaracao(self, obj):
        """O indice desta declaracao na tabela, empacotando-a se preciso."""
        chave = id(obj)
        if chave in self._por_id:
            return self._por_id[chave]

        # Reservar o indice ANTES de empacotar: uma acao que chama a si
        # mesma, ou dois records que se citam, entrariam em recursao
        # infinita se o indice so existisse no fim.
        indice = len(self.declaracoes)
        self._por_id[chave] = indice
        self._objetos[indice] = obj
        self.declaracoes.append(None)
        self.declaracoes[indice] = self._empacotar(obj)
        return indice

    def _empacotar(self, obj):
        from .interpreter import DFAction, DFBlueprint, DFEnum, DFRecord

        if isinstance(obj, DFAction):
            return _Declaracao("acao", self._acao(obj))
        if isinstance(obj, DFRecord):
            return _Declaracao("record", self._record(obj))
        if isinstance(obj, DFEnum):
            return _Declaracao("enum", self._enum(obj))
        if isinstance(obj, DFBlueprint):
            return _Declaracao("blueprint", self._blueprint(obj))
        raise NaoAtravessa(_motivo(obj))

    def _acao(self, a):
        ligados = _nomes_dos_params(a.params)
        ligados.add(a.name)
        return {
            "nome": a.name,
            "params": a.params,
            "defaults": a.defaults,
            "body": a.body,
            "is_async": a.is_async,
            "param_types": a.param_types,
            "return_type": a.return_type,
            "is_generator": a.is_generator,
            "type_params": a.type_params,
            "arquivo": a.arquivo,
            "livres": self._livres(a.body, ligados, a.closure,
                                   extra=a.defaults),
            # sobrecarga, promessas e trava viajam: sem eles um grupo de
            # 'overload' chegaria do outro lado como uma acao de corpo vazio
            "extras": self._extras(a),
            "visibilidade": getattr(a, "visibilidade", "public"),
        }

    def _extras(self, a):
        extras = getattr(a, "extras", None)
        if extras is None:
            return None
        return {
            "variantes": ([self.declaracao(v) for v in extras.variantes]
                          if extras.variantes else None),
            "promessas": list(extras.promessas),
            "exclusivo": extras.exclusivo,
            "grupo": extras.grupo,
        }

    def _record(self, r):
        ligados = {r.name, "self"}
        return {
            "nome": r.name,
            "fields": r.fields,
            "metodos": {n: self.declaracao(m) for n, m in r.methods.items()},
            "livres": self._livres(
                [f[2] for f in r.fields if f[2] is not None],
                ligados, r.env),
        }

    def _enum(self, e):
        return {
            "nome": e.name,
            "membros": [(m.name, self.valor(m.value), m.index)
                        for m in e.members.values()],
            "metodos": {n: self.declaracao(m) for n, m in e.methods.items()},
        }

    def _blueprint(self, b):
        ligados = {b.name, "self", "root"}
        ligados.update(_nomes_dos_params(b.constructor_params))
        return {
            "nome": b.name,
            "pais": [self.declaracao(p) for p in b.parents],
            "metodos": {n: self.declaracao(m) for n, m in b.methods.items()},
            "statics": {n: self.valor(v) for n, v in b.statics.items()},
            "constructor_params": b.constructor_params,
            "constructor_body": b.constructor_body,
            "properties": {n: {k: (self.declaracao(v) if k in ("get", "set") else v)
                               for k, v in p.items()}
                           for n, p in b.properties.items()},
            "operators": {n: self.declaracao(v)
                          for n, v in b.operators.items()},
            "fields_decl": b.fields_decl,
            "visibility": b.visibility,
            "is_abstract": b.is_abstract,
            "abstract_methods": set(b.abstract_methods),
            "static_methods": set(b.static_methods),
            "final_methods": set(b.final_methods),
            "traits": list(b.traits),
            "slots": list(b.slots) if b.slots is not None else None,
            "livres": self._livres(b.constructor_body, ligados, b.env),
            "oop": {
                "somente_leitura": set(b.somente_leitura),
                "nao_publicos": set(b.nao_publicos),
                "constantes": set(b.constantes),
                "e_final": b.e_final, "e_selado": b.e_selado,
                "arquivo": b.arquivo,
                "contratos_todos": set(b.contratos_todos),
                "tipos_do_cabecalho": dict(b.tipos_do_cabecalho),
                "padroes_do_cabecalho": dict(b.padroes_do_cabecalho),
            },
        }

    def _livres(self, corpo, ligados, escopo, extra=None):
        """Os nomes livres deste corpo, ja traduzidos.

        Um nome que o escopo nao tem e local de um bloco interno, ou
        vem de um embutido — nos dois casos o filho o resolve sozinho.
        Um nome cujo valor nao atravessa fica de fora, com o motivo
        guardado: so vira erro se a acao realmente o usar.
        """
        from .errors import NameError_

        alvo = list(corpo)
        if extra:
            alvo.extend(extra.values() if isinstance(extra, dict) else extra)

        saida = {}
        for nome in nomes_livres(alvo, set(ligados)):
            if escopo is None:
                continue
            try:
                v = escopo.get(nome)
            except NameError_:
                continue
            except Exception:                     # noqa: BLE001
                continue
            if _e_embutida(escopo, nome):
                continue                          # o filho ja tem
            try:
                saida[nome] = self.valor(v)
            except NaoAtravessa as e:
                self.faltas[nome] = (e.mensagem, e.nota, e.dica)
        return saida


def _e_modulo(nome, v):
    from .stdlib import get_module
    try:
        return get_module(nome) is not None
    except Exception:                             # noqa: BLE001
        return False


def _e_embutida(escopo, nome):
    e = escopo
    while e is not None:
        if nome in e.embutidas:
            return True
        if nome in e.variables:
            return False
        e = e.parent
    return False


#: O que existe so no processo que abriu, e o motivo em uma linha.
#:
#: A chave e procurada DENTRO do nome da classe, em minusculas, porque
#: o nome varia: uma conexao de banco chega como '_ConexaoSerial' pelo
#: 'Arcane.Database' e como 'Connection' pelo sqlite3 direto, e as
#: duas sao a mesma coisa para quem le a mensagem.
_SO_AQUI = (
    ("conexaoserial", "a connection to a database"),
    ("connection", "a connection"),
    ("cursor", "a cursor of a database"),
    ("socket", "a network socket"),
    ("tarefa", "a task that is already running in this process"),
    ("canal", "a channel between the threads of this process"),
    ("dfstream", "a lazy sequence, which is consumed as it is read"),
    ("generator", "a sequence that is consumed as it is read"),
    ("lock", "a lock, which coordinates the threads of THIS process"),
    ("semaphore", "a semaphore, which counts inside THIS process"),
    ("condition", "a condition, which wakes the threads of THIS process"),
    ("barrier", "a barrier, which holds the threads of THIS process"),
    ("event", "an event, which is set inside THIS process"),
    ("thread", "a thread of this process"),
    ("textiowrapper", "an open file"),
    ("bufferedreader", "an open file"),
    ("bufferedwriter", "an open file"),
    ("fileio", "an open file"),
    ("module", "a Python module"),
)


def _recurso(v):
    """A frase que descreve este valor, se ele existe so neste processo."""
    nome = type(v).__name__.lower()
    for chave, texto in _SO_AQUI:
        if chave in nome:
            return texto
    return ""


def _motivo(v):
    texto = _recurso(v)
    if texto:
        return (f"it holds {texto}, which exists only in the process "
                f"that opened it")
    if callable(v):
        return ("it holds a function built at run time, and a function "
                "like that has no name the other process could look up")
    return f"it holds a value that cannot be copied ({_nome_do_tipo(v)})"


def _dica(v):
    if _recurso(v):
        return ("open it INSIDE the action — each process opens its own — "
                "or use 'map', which uses threads and shares memory")
    return ("pass it as an argument, or use 'map', which uses threads "
            "and shares memory")


# ═══════════════════════════════════════════════════════════
#  Abrir: do outro lado
# ═══════════════════════════════════════════════════════════

class Abridor:
    """Remonta, num processo novo, o que o Empacotador traduziu."""

    def __init__(self, declaracoes, faltas, interp):
        from .environment import Environment
        self.tabela = declaracoes
        self.faltas = faltas
        self.interp = interp
        # Sem interpretador nao ha embutidas para herdar — e e o caso
        # legitimo de quem so DECODIFICA um resultado que nao tem
        # declaracao nenhuma dentro. Remontar uma acao exige um, e
        # '_abrir' garante isso do lado do filho.
        raiz_pai = interp.global_env if interp is not None else None
        self.raiz = Environment(parent=raiz_pai, name="<processo>")
        self._pronto = {}

    # ── valores ──────────────────────────────────────────

    def valor(self, v):
        if isinstance(v, _SIMPLES):
            return v
        if isinstance(v, _Ref):
            return self._ref(v)
        if isinstance(v, dict):
            return {self.valor(k): self.valor(x) for k, x in v.items()}
        if isinstance(v, list):
            return [self.valor(x) for x in v]
        if isinstance(v, tuple):
            return tuple(self.valor(x) for x in v)
        if isinstance(v, (set, frozenset)):
            return type(v)(self.valor(x) for x in v)
        return v

    def indice_por_id(self):
        """O caminho de volta: o objeto remontado aqui, e o indice dele.

        E ele que faz o resultado voltar pela MESMA tabela: um record
        que veio do pai volta como indice, e nao como uma declaracao
        nova que o pai teria de remontar.
        """
        return {id(obj): i for i, obj in self._pronto.items()}

    def _ref(self, r):
        from .interpreter import DFInstance, DFRecordInstance
        from .stdlib import get_module

        if r.especie == "modulo":
            return get_module(r.dados)
        if r.especie == "decl":
            return self.declaracao(r.indice)
        if r.especie == "rec":
            tipo = self.declaracao(r.indice)
            return DFRecordInstance(
                tipo, {k: self.valor(x) for k, x in r.dados.items()})
        if r.especie == "membro":
            enum = self.declaracao(r.indice)
            return enum.members[r.dados]
        if r.especie == "inst":
            bp = self.declaracao(r.indice)
            inst = DFInstance(bp)
            for k, x in r.dados.items():
                inst.set(k, self.valor(x))
            return inst
        raise RuntimeError(f"unknown reference: {r.especie}")

    # ── declaracoes ──────────────────────────────────────

    def declaracao(self, indice):
        if indice in self._pronto:
            return self._pronto[indice]
        d = self.tabela[indice]
        montador = getattr(self, f"_montar_{d.especie}")
        return montador(indice, d.campos)

    def _escopo(self, nome, livres):
        """Um escopo por declaracao, e nao um so compartilhado.

        Duas acoes podem ter um nome livre igual valendo coisas
        diferentes — cada uma nasceu num bloco. Um escopo unico faria a
        segunda sobrescrever a primeira, calada.
        """
        env = self.raiz.child(nome)
        for n, v in livres.items():
            env.variables[n] = self.valor(v)
        return env

    def _montar_acao(self, indice, c):
        from .interpreter import DFAction
        env = self.raiz.child(c["nome"])
        acao = DFAction(
            name=c["nome"], params=c["params"], defaults=c["defaults"],
            body=c["body"], closure=env, is_async=c["is_async"],
            param_types=c["param_types"], return_type=c["return_type"],
            is_generator=c["is_generator"], type_params=c["type_params"])
        acao.arquivo = c["arquivo"]
        acao.visibilidade = c.get("visibilidade", "public")
        self._pronto[indice] = acao
        env.variables[c["nome"]] = acao
        for n, v in c["livres"].items():
            env.variables[n] = self.valor(v)
        extras = c.get("extras")
        if extras is not None:
            from .objetos import Extras, nos_before
            e = Extras()
            e.variantes = ([self.declaracao(i) for i in extras["variantes"]]
                           if extras["variantes"] else None)
            e.promessas = extras["promessas"]
            e.antes = [n for p in e.promessas for n in nos_before(p)]
            e.exclusivo = extras["exclusivo"]
            e.grupo = extras["grupo"]
            acao.extras = e
        return acao

    def _montar_record(self, indice, c):
        from .interpreter import DFRecord
        env = self._escopo(c["nome"], {})
        rec = DFRecord(c["nome"], c["fields"], {}, env)
        self._pronto[indice] = rec
        env.variables[c["nome"]] = rec
        self.raiz.variables.setdefault(c["nome"], rec)
        for n, i in c["metodos"].items():
            rec.methods[n] = self.declaracao(i)
        for n, v in c["livres"].items():
            env.variables[n] = self.valor(v)
        return rec

    def _montar_enum(self, indice, c):
        from .interpreter import DFEnum, DFEnumMember
        env = self.raiz.child(c["nome"])
        membros = {}
        enum = DFEnum(c["nome"], membros, {}, env)
        self._pronto[indice] = enum
        env.variables[c["nome"]] = enum
        self.raiz.variables.setdefault(c["nome"], enum)
        for nome, valor, i in c["membros"]:
            membros[nome] = DFEnumMember(c["nome"], nome, self.valor(valor), i,
                                         enum)
        for n, i in c["metodos"].items():
            enum.methods[n] = self.declaracao(i)
        return enum

    def _montar_blueprint(self, indice, c):
        from .interpreter import DFBlueprint
        env = self.raiz.child(c["nome"])
        bp = DFBlueprint(
            name=c["nome"], parents=[], methods={}, statics={}, env=env,
            constructor_params=c["constructor_params"],
            constructor_body=c["constructor_body"],
            properties={}, operators={}, fields_decl=c["fields_decl"],
            visibility=c["visibility"], is_abstract=c["is_abstract"],
            abstract_methods=c["abstract_methods"],
            static_methods=c["static_methods"],
            final_methods=c["final_methods"], traits=c["traits"],
            slots=c["slots"])
        self._pronto[indice] = bp
        env.variables[c["nome"]] = bp
        self.raiz.variables.setdefault(c["nome"], bp)
        bp.parents = [self.declaracao(i) for i in c["pais"]]
        for n, i in c["metodos"].items():
            bp.methods[n] = self.declaracao(i)
        for n, i in c["operators"].items():
            bp.operators[n] = self.declaracao(i)
        for n, p in c["properties"].items():
            bp.properties[n] = {k: (self.declaracao(i) if k in ("get", "set") else i)
                                for k, i in p.items()}
        for n, v in c["statics"].items():
            bp.statics[n] = self.valor(v)
        for n, v in c["livres"].items():
            env.variables[n] = self.valor(v)
        oop = c.get("oop") or {}
        bp.somente_leitura = frozenset(oop.get("somente_leitura", ()))
        bp.nao_publicos = frozenset(oop.get("nao_publicos", ()))
        bp.constantes = set(oop.get("constantes", ()))
        bp.e_final = oop.get("e_final", False)
        bp.e_selado = oop.get("e_selado", False)
        bp.arquivo = oop.get("arquivo", "")
        bp.contratos_todos = frozenset(oop.get("contratos_todos", ()))
        bp.tipos_do_cabecalho = oop.get("tipos_do_cabecalho", {})
        bp.padroes_do_cabecalho = oop.get("padroes_do_cabecalho", {})
        for acao in bp.methods.values():
            if getattr(acao, "dono", None) is None:
                acao.dono = bp
        bp.finalizador = next((bp.methods[n] for n in ("teardown", "__del__")
                               if n in bp.methods), None)
        bp.recalcular_acesso()
        return bp


# ═══════════════════════════════════════════════════════════
#  O pacote, e o que acontece no outro processo
# ═══════════════════════════════════════════════════════════

class Pacote:
    """Uma acao de DataForge, e tudo o que ela alcanca, pronta para ir.

    E o unico objeto que atravessa a fronteira, e ele vai UMA vez por
    processo — no 'initializer' do pool, e nao junto de cada item.
    Mandado por item, um record de mil campos seria copiado mil vezes.
    """

    __slots__ = ("marca", "alvo", "declaracoes", "faltas")

    def __init__(self, marca, alvo, declaracoes, faltas):
        self.marca = marca
        self.alvo = alvo              # indice na tabela, ou o proprio callable
        self.declaracoes = declaracoes
        self.faltas = faltas

    def __reduce__(self):
        return (Pacote, (self.marca, self.alvo, self.declaracoes,
                         self.faltas))


class _ErroDoFilho(Exception):
    """O erro que aconteceu no outro processo, na forma que volta.

    Um erro de DataForge carrega a pilha, a linha de codigo e o arquivo,
    e nada disso sobrevive a copia inteiro. O que volta e o texto ja
    montado — e ele nomeia o processo, senao a mensagem parece ter
    acontecido aqui, numa linha que aqui nao existe.
    """

    def __init__(self, tipo, texto, nota="", dica=""):
        super().__init__(texto)
        self.tipo = tipo
        self.texto = texto
        self.nota = nota
        self.dica = dica

    def __reduce__(self):
        return (_ErroDoFilho, (self.tipo, self.texto, self.nota, self.dica))


def empacotar(acao, itens):
    """A acao e os itens na forma que atravessa — ou NaoAtravessa.

    Devolve '(pacote, itens_traduzidos, empacotador)'. O empacotador
    volta porque e ele quem sabe o indice de cada declaracao: o
    resultado que chega do filho vem nesses mesmos indices, e decodifica-lo
    com outra tabela devolveria o record errado.
    """
    import uuid
    from .interpreter import DFAction

    emp = Empacotador()
    if isinstance(acao, DFAction):
        alvo = emp.declaracao(acao)
    else:
        # Uma embutida, ou uma funcao da biblioteca: se o pickle a
        # alcanca pelo nome, ela vai como esta.
        try:
            pickle.dumps(acao, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:                         # noqa: BLE001
            raise NaoAtravessa(
                _motivo(acao),
                nota="only an action declared in a file, or a function of "
                     "the library, can be looked up by the other process",
                dica="wrap it in an action") from None
        alvo = acao

    traduzidos = [emp.valor(x) for x in itens]
    pacote = Pacote(uuid.uuid4().hex, alvo, emp.declaracoes, dict(emp.faltas))
    return pacote, traduzidos, emp


def desempacotar(emp, codificado):
    """O que voltou do filho, com as declaracoes DESTE processo.

    O filho pode ter acrescentado declaracoes a tabela — um record
    declarado dentro da propria acao. Por isso o abridor daqui nasce
    com os indices que ja existem apontando para os objetos originais:
    sem isso, o record que foi daqui voltaria como uma copia, e
    'p is q' passaria a ser 'no' para o mesmo tipo.
    """
    from .interpreter import DFAction

    abridor = Abridor(emp.declaracoes, emp.faltas, DFAction._interpreter)
    abridor._pronto.update(emp.originais())
    return abridor.valor(codificado)


# ── O estado de UM processo filho ────────────────────────

#: marca -> (abridor, acao, faltas). Um processo atende varios itens,
#: e remontar o interpretador a cada item custaria mais que o trabalho.
_ABERTOS = {}


def instalar(pacote):
    """Roda uma vez em cada processo do pool, antes do primeiro item."""
    _ABERTOS[pacote.marca] = _abrir(pacote)


def _abrir(pacote):
    from .interpreter import DFAction, Interpreter

    interp = DFAction._interpreter
    if interp is None:
        interp = Interpreter()
    abridor = Abridor(pacote.declaracoes, pacote.faltas, interp)
    if isinstance(pacote.alvo, int):
        acao = abridor.declaracao(pacote.alvo)
    else:
        acao = pacote.alvo
    return abridor, acao, pacote.faltas


class Chamada:
    """O que o pool mapeia sobre os itens: uma marca, e nada mais.

    O pacote inteiro ja foi para cada processo pelo 'initializer'.
    Mandar de novo junto de cada lote copiaria a tabela de declaracoes
    tantas vezes quantos forem os lotes — com mil itens e um record de
    trinta campos, isso e mais dado atravessando do que trabalho sendo
    feito.
    """

    __slots__ = ("marca", "pacote")

    def __init__(self, marca, pacote=None):
        self.marca = marca
        #: So o pool REAPROVEITADO leva o pacote junto.
        #:
        #: 'map_processos' abre o proprio pool e manda o pacote pelo
        #: 'initializer', que roda uma vez por processo. Um pool que
        #: sobrevive entre chamadas nao pode: ele ja esta de pe quando
        #: a proxima acao aparece, e 'initializer' nao roda de novo.
        #: Entao o pacote viaja com o lote — e o filho o ABRE uma vez
        #: so, porque '_ABERTOS' e por marca.
        self.pacote = pacote

    def __reduce__(self):
        return (Chamada, (self.marca, self.pacote))

    def __call__(self, item):
        if self.pacote is not None and self.marca not in _ABERTOS:
            _ABERTOS[self.marca] = _abrir(self.pacote)
        return aplicar(self.marca, item)


def aplicar(marca, item):
    """Chama a acao com um item, do outro lado da fronteira."""
    from .errors import DataForgeError, NameError_

    aberto = _ABERTOS.get(marca)
    if aberto is None:
        raise _ErroDoFilho(
            "ConcurrencyError",
            "this process was started without the action",
            nota="the pool replaced a worker after it was set up")
    abridor, acao, faltas = aberto

    try:
        valor = acao(abridor.valor(item))
    except NameError_ as e:
        citada = _falta_citada(faltas, e)
        if citada:
            mensagem, nota, dica = citada
            raise _ErroDoFilho("ConcurrencyError", mensagem, nota,
                               dica) from None
        raise _ErroDoFilho(e.friendly_name(), e.message, e.nota,
                           e.dica) from None
    except DataForgeError as e:
        raise _ErroDoFilho(e.friendly_name(), e.message, e.nota,
                           e.dica) from None

    saida = Empacotador(abridor.tabela, abridor.indice_por_id())
    return saida.valor(valor)


def _falta_citada(faltas, erro):
    """O nome que o filho nao achou e um que ficou para tras?

    E aqui que a mensagem honesta aparece. A varredura de nomes livres
    captura de mais de proposito, entao um nome que nao atravessou so
    vira erro quando a acao realmente o usa — e nesse momento se sabe
    que ele fazia falta.
    """
    for nome, motivo in faltas.items():
        if f"'{nome}'" in (erro.message or ""):
            texto, nota, dica = motivo
            return (f"'{nome}' cannot cross into another process", texto,
                    dica or "open it inside the action, or use 'map', "
                            "which uses threads and shares memory")
    return None
