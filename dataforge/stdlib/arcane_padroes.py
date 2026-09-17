"""
Arcane.Padroes — os padroes de projeto que precisam de MECANISMO.

A maioria dos padroes do catalogo classico ja e a propria linguagem:
Template Method e um 'abstract blueprint', Strategy e um contrato com
duas implementacoes, Decorator e 'mark @…', Iterator e 'stream action',
Adapter e um blueprint que embrulha outro. Escrever uma biblioteca para
eles seria cerimonia.

Este modulo traz os que pedem ESTADO ou CONTROLE que ninguem deveria
reescrever a cada projeto:

    criacionais     unico, pool, construtor, prototipos, compartilhado
    estruturais     proxy, adaptar, composto
    comportamentais comandos (desfazer/refazer), cadeia, especificacao,
                    maquina (de estados), memento, visitar, observavel,
                    mediador, estrategias
    dominio         repositorio (em memoria), barramento (de comandos)

─── Duas decisoes ──────────────────────────────────────────────

1. **O 'unico' e por CHAVE, e nao por tipo global.** Um singleton de
   verdade — um por processo, para sempre — e o padrao que mais atrapalha
   teste. 'Padroes.unico(fabrica)' devolve um provedor: quem o guarda
   decide quanto ele vive, e o teste cria o seu.

2. **O pool DEVOLVE na saida, mesmo com erro.** 'pool.usar(acao)' pega,
   roda e devolve num 'finally'. Um pool em que o objeto so volta no
   caminho feliz esgota no primeiro erro, e o sintoma — o programa para
   de responder — aparece longe da causa.
"""

import threading


def _ler_opcoes(opcoes, padroes, onde):
    """Recusa a chave desconhecida E aplica os padroes."""
    from .opcoes import ler
    return {**padroes, **ler(dict(opcoes or {}), padroes, onde)}


def _interp():
    from ..interpreter import DFAction
    return DFAction._interpreter


def _i():
    from .. import interpreter as i
    return i


def _no():
    return _interp()._no_interno()


def _chamar(acao, *args):
    interp = _interp()
    return interp._call(acao, list(args), {}, _no(), interp.global_env)


def _erro(mensagem, **kw):
    from ..errors import StateError
    return StateError(mensagem, doc="oop/padroes", **kw)


# ── criacionais ──────────────────────────────────────────────

class Unico:
    """Um provedor que constroi uma vez, na primeira chamada, com trava."""

    def __init__(self, fabrica):
        self._fabrica = fabrica
        self._valor = None
        self._pronto = False
        self._trava = threading.Lock()

    def __call__(self):
        return self.obter()

    def obter(self):
        if not self._pronto:
            with self._trava:
                if not self._pronto:
                    i = _i()
                    if isinstance(self._fabrica, i.DFBlueprint):
                        interp = _interp()
                        self._valor = interp._instanciar(self._fabrica, [], {}, _no(),
                                                         interp.global_env)
                    else:
                        self._valor = _chamar(self._fabrica)
                    self._pronto = True
        return self._valor

    def pronto(self):
        return self._pronto

    def reiniciar(self):
        with self._trava:
            self._valor, self._pronto = None, False


class Pool:
    """Um conjunto de objetos reaproveitaveis, com teto e devolucao garantida."""

    def __init__(self, fabrica, tamanho=4, limpar=None):
        if int(tamanho) < 1:
            from ..errors import ValueError_
            raise ValueError_("A pool needs a size of at least 1.", doc="oop/padroes")
        self._fabrica = fabrica
        self._limpar = limpar
        self.tamanho = int(tamanho)
        self._livres = []
        self._emprestados = 0
        self._cond = threading.Condition()
        self.criados = 0

    def pegar(self, espera=None):
        with self._cond:
            while not self._livres and self._emprestados + len(self._livres) >= self.tamanho \
                    and self.criados >= self.tamanho:
                if not self._cond.wait(timeout=espera):
                    from ..errors import PoolExhaustedError
                    raise PoolExhaustedError(
                        f"The pool of {self.tamanho} is exhausted.",
                        nota=f"{self._emprestados} object(s) borrowed and not returned",
                        dica="return objects with pool.devolver(obj), or use "
                             "pool.usar(acao), which always returns",
                        doc="oop/padroes")
            if self._livres:
                obj = self._livres.pop()
            else:
                obj = _chamar(self._fabrica)
                self.criados += 1
            self._emprestados += 1
            return obj

    def devolver(self, obj):
        if self._limpar is not None:
            _chamar(self._limpar, obj)
        with self._cond:
            self._emprestados = max(0, self._emprestados - 1)
            self._livres.append(obj)
            self._cond.notify()
        return True

    def usar(self, acao):
        obj = self.pegar()
        try:
            return _chamar(acao, obj)
        finally:
            self.devolver(obj)

    @property
    def livres(self):
        return len(self._livres)

    @property
    def emprestados(self):
        return self._emprestados


class Construtor:
    """Builder: acumula campos com nome, confere e constroi no fim."""

    def __init__(self, molde, obrigatorios=None):
        self._molde = molde
        self._valores = {}
        self._obrigatorios = list(obrigatorios or [])

    def com(self, campo, valor):
        self._valores[campo] = valor
        return self

    def construir(self):
        faltando = [c for c in self._obrigatorios if c not in self._valores]
        if faltando:
            from ..errors import ValueError_
            raise ValueError_(
                f"The builder for '{getattr(self._molde, 'name', '?')}' is missing: "
                f"{', '.join(faltando)}.",
                dica="call .com(campo, valor) for each one before .construir()",
                doc="oop/padroes")
        i = _i()
        interp = _interp()
        if isinstance(self._molde, i.DFBlueprint):
            parametros = set(self._molde.constructor_params)
            nomeados = {k: v for k, v in self._valores.items() if k in parametros}
            obj = interp._instanciar(self._molde, [], nomeados, _no(), interp.global_env)
            for k, v in self._valores.items():
                if k not in parametros:
                    interp._escrever_membro(obj, k, v, _no(), interp.global_env)
            return obj
        return interp._call(self._molde, [], dict(self._valores), _no(),
                            interp.global_env)


class Prototipos:
    """Prototype: um registro de modelos, e copias fundas com alteracoes."""

    def __init__(self):
        self._modelos = {}

    def registrar(self, nome, modelo):
        self._modelos[nome] = modelo
        return self

    def criar(self, nome, alteracoes=None):
        import copy
        if nome not in self._modelos:
            raise _erro(f"There is no prototype named '{nome}'.",
                        nota="registered: " + ", ".join(sorted(self._modelos)))
        copia = copy.deepcopy(self._modelos[nome])
        interp = _interp()
        for campo, valor in (alteracoes or {}).items():
            interp._escrever_membro(copia, campo, valor, _no(), interp.global_env)
        return copia

    def nomes(self):
        return sorted(self._modelos)


class Compartilhado:
    """Flyweight: um objeto por conjunto de argumentos, reaproveitado."""

    def __init__(self, fabrica):
        self._fabrica = fabrica
        self._cache = {}
        self._trava = threading.Lock()

    def obter(self, *args):
        chave = tuple(_chave(a) for a in args)
        with self._trava:
            if chave not in self._cache:
                self._cache[chave] = _chamar(self._fabrica, *args)
            return self._cache[chave]

    def __call__(self, *args):
        return self.obter(*args)

    @property
    def tamanho(self):
        return len(self._cache)


def _chave(valor):
    if isinstance(valor, list):
        return ("L",) + tuple(_chave(v) for v in valor)
    if isinstance(valor, dict):
        return ("V",) + tuple(sorted((str(k), _chave(v)) for k, v in valor.items()))
    try:
        hash(valor)
        return valor
    except TypeError:
        return id(valor)


# ── estruturais ──────────────────────────────────────────────

class Proxy:
    """Intercepta as chamadas a um objeto: 'interceptar(nome, args, seguir)'."""

    def __init__(self, alvo, interceptar):
        self.__dict__["_alvo"] = alvo
        self.__dict__["_interceptar"] = interceptar

    def __getattr__(self, nome):
        if nome.startswith("__"):
            raise AttributeError(nome)
        interp = _interp()
        alvo = self.__dict__["_alvo"]
        valor = interp._ler_membro(alvo, _membro(nome), interp.global_env, membro=nome)
        i = _i()
        if not isinstance(valor, i.DFAction) and not callable(valor):
            return valor

        def chamar(*args):
            def seguir(novos=None):
                usados = list(args) if novos is None else list(novos)
                from .. import ast_nodes as ast
                no = ast.MethodCall(object=None, method=nome, args=[], kwargs={})
                return interp._chamar_metodo(alvo, usados, {}, no, interp.global_env)
            return _chamar(self.__dict__["_interceptar"], nome, list(args), seguir)
        return chamar


def _membro(nome):
    from .. import ast_nodes as ast
    return ast.MemberAccess(object=None, member=nome)


class Adaptador:
    """Adapter por mapa: {"nome_novo": "nome_antigo"}, o resto passa direto."""

    def __init__(self, alvo, mapa):
        self._alvo = alvo
        self._mapa = dict(mapa)

    def __getattr__(self, nome):
        if nome.startswith("_"):
            raise AttributeError(nome)
        interp = _interp()
        real = self._mapa.get(nome, nome)
        valor = interp._ler_membro(self._alvo, _membro(real), interp.global_env,
                                   membro=real)
        i = _i()
        if isinstance(valor, i.DFAction):
            alvo = self._alvo

            def chamar(*args):
                from .. import ast_nodes as ast
                no = ast.MethodCall(object=None, method=real, args=[], kwargs={})
                return interp._chamar_metodo(alvo, list(args), {}, no, interp.global_env)
            return chamar
        return valor


class Composto:
    """Composite: uma arvore em que folha e galho respondem a mesma operacao."""

    def __init__(self, valor=None):
        self.valor = valor
        self.filhos = []

    def acrescentar(self, filho):
        self.filhos.append(filho if isinstance(filho, Composto) else Composto(filho))
        return self

    def percorrer(self, acao, profundidade=0):
        resultados = [_chamar(acao, self.valor, profundidade)]
        for filho in self.filhos:
            resultados.extend(filho.percorrer(acao, profundidade + 1))
        return resultados

    def reduzir(self, acao, inicial=0):
        total = _chamar(acao, inicial, self.valor)
        for filho in self.filhos:
            total = filho.reduzir(acao, total)
        return total

    def tamanho(self):
        return 1 + sum(f.tamanho() for f in self.filhos)


# ── comportamentais ──────────────────────────────────────────

class Comandos:
    """Command com historico: executar, desfazer, refazer."""

    def __init__(self, limite=100):
        self._feitos = []
        self._desfeitos = []
        self.limite = int(limite)

    def executar(self, comando):
        resultado = _metodo(comando, "executar")
        self._feitos.append(comando)
        if len(self._feitos) > self.limite:
            self._feitos.pop(0)
        self._desfeitos.clear()
        return resultado

    def desfazer(self):
        if not self._feitos:
            return False
        comando = self._feitos.pop()
        _metodo(comando, "desfazer")
        self._desfeitos.append(comando)
        return True

    def refazer(self):
        if not self._desfeitos:
            return False
        comando = self._desfeitos.pop()
        _metodo(comando, "executar")
        self._feitos.append(comando)
        return True

    @property
    def historico(self):
        return list(self._feitos)

    def pode_desfazer(self):
        return bool(self._feitos)

    def pode_refazer(self):
        return bool(self._desfeitos)


def _metodo(obj, nome, *args):
    interp = _interp()
    from .. import ast_nodes as ast
    no = ast.MethodCall(object=None, method=nome, args=[], kwargs={})
    return interp._chamar_metodo(obj, list(args), {}, no, interp.global_env)


def _cadeia(manipuladores):
    """Chain of Responsibility: 'm(pedido, proximo)' — cada um decide se passa."""
    lista = list(manipuladores)

    def rodar(pedido, indice=0):
        if indice >= len(lista):
            return None
        return _chamar(lista[indice], pedido, lambda p=pedido: rodar(p, indice + 1))
    return lambda pedido: rodar(pedido)


class Especificacao:
    """Specification: uma regra de negocio combinavel e testavel."""

    def __init__(self, predicado, nome="especificacao"):
        self._predicado = predicado
        self.nome = nome

    def satisfeita(self, candidato):
        return bool(_chamar(self._predicado, candidato))

    def e(self, outra):
        return Especificacao(lambda c: self.satisfeita(c) and outra.satisfeita(c),
                             f"({self.nome} e {outra.nome})")

    def ou(self, outra):
        return Especificacao(lambda c: self.satisfeita(c) or outra.satisfeita(c),
                             f"({self.nome} ou {outra.nome})")

    def nao(self):
        return Especificacao(lambda c: not self.satisfeita(c), f"nao {self.nome}")

    def filtrar(self, itens):
        return [x for x in itens if self.satisfeita(x)]

    def __repr__(self):
        return f"<especificacao {self.nome}>"


class Maquina:
    """State: estados, transicoes por evento, guardas e reacoes.

        m := Padroes.maquina("rascunho", {
            "enviar":  {"de": ["rascunho"], "para": "enviado"},
            "aprovar": {"de": ["enviado"],  "para": "aprovado"},
        })
        m.ir("enviar")
    """

    def __init__(self, inicial, transicoes):
        self.estado = inicial
        self._transicoes = {}
        for evento, regra in dict(transicoes).items():
            regra = _ler_opcoes(regra, {"de": [], "para": None, "guarda": None,
                                        "ao_entrar": None}, f"Padroes.maquina({evento})")
            de = regra["de"]
            regra["de"] = [de] if isinstance(de, str) else list(de)
            self._transicoes[evento] = regra
        self.historico = [inicial]

    def pode(self, evento, contexto=None):
        regra = self._transicoes.get(evento)
        if regra is None or (regra["de"] and self.estado not in regra["de"]):
            return False
        if regra["guarda"] is not None and not _chamar(regra["guarda"], contexto):
            return False
        return True

    def ir(self, evento, contexto=None):
        regra = self._transicoes.get(evento)
        if regra is None:
            raise _erro(f"The state machine has no event '{evento}'.",
                        nota="events: " + ", ".join(sorted(self._transicoes)))
        if not self.pode(evento, contexto):
            raise _erro(f"The event '{evento}' is not allowed in the state "
                        f"'{self.estado}'.",
                        nota=f"it is allowed from: {', '.join(regra['de']) or 'any state'}")
        anterior = self.estado
        self.estado = regra["para"]
        self.historico.append(self.estado)
        if regra["ao_entrar"] is not None:
            _chamar(regra["ao_entrar"], anterior, self.estado, contexto)
        return self.estado

    def eventos(self):
        return sorted(e for e in self._transicoes if self.pode(e))


def _memento(obj):
    """Uma foto dos campos do objeto, para restaurar depois."""
    import copy
    i = _i()
    if not isinstance(obj, i.DFInstance):
        raise _erro("Padroes.memento takes a blueprint instance.")
    return {"$tipo": obj.blueprint.name, "campos": copy.deepcopy(dict(obj.fields))}


def _restaurar(obj, memento):
    i = _i()
    if not isinstance(obj, i.DFInstance) or memento.get("$tipo") != obj.blueprint.name:
        raise _erro("This memento belongs to another type.",
                    nota=f"memento of '{memento.get('$tipo')}'")
    import copy
    interp = _interp()
    for campo, valor in memento["campos"].items():
        interp._escrever_membro(obj, campo, copy.deepcopy(valor), _no(), interp.global_env)
    return obj


def _visitar(obj, visitante):
    """Visitor: chama 'visitar_<Blueprint>' subindo a MRO, ou 'visitar_padrao'."""
    i = _i()
    molde = getattr(obj, "blueprint", None) or getattr(obj, "record", None)
    nomes = [bp.name for bp in molde.linhagem()] if hasattr(molde, "linhagem") else \
        ([molde.name] if molde is not None else [])
    metodos = getattr(getattr(visitante, "blueprint", None), "methods", {}) or {}
    for nome in nomes:
        alvo = f"visitar_{nome}"
        if alvo in metodos or any(alvo in bp.methods
                                  for bp in visitante.blueprint.linhagem()):
            return _metodo(visitante, alvo, obj)
    if "visitar_padrao" in metodos:
        return _metodo(visitante, "visitar_padrao", obj)
    raise _erro(f"The visitor has no 'visitar_{nomes[0] if nomes else '?'}' and no "
                f"'visitar_padrao'.",
                dica=f"declare  action visitar_{nomes[0] if nomes else 'Tipo'}(no):")


class Observavel:
    """Observer com prioridade, filtro e cancelamento da propagacao."""

    def __init__(self):
        self._assinantes = []
        self._trava = threading.Lock()
        self._sequencia = 0

    def assinar(self, acao, prioridade=0, filtro=None):
        with self._trava:
            self._sequencia += 1
            self._assinantes.append((-int(prioridade), self._sequencia, acao, filtro))
            self._assinantes.sort(key=lambda t: (t[0], t[1]))
        return acao

    def cancelar(self, acao):
        with self._trava:
            antes = len(self._assinantes)
            self._assinantes = [t for t in self._assinantes if t[2] is not acao]
            return antes != len(self._assinantes)

    def notificar(self, dados=None):
        """Avisa em ordem de prioridade. Um ouvinte que devolve 'parar' encerra."""
        entregues = 0
        for _p, _s, acao, filtro in list(self._assinantes):
            if filtro is not None and not _chamar(filtro, dados):
                continue
            entregues += 1
            if _chamar(acao, dados) == "parar":
                break
        return entregues

    @property
    def total(self):
        return len(self._assinantes)


class Mediador:
    """Mediator: participantes conversam por nome, sem se conhecerem."""

    def __init__(self):
        self._participantes = {}
        self.mensagens = 0

    def registrar(self, nome, receber):
        self._participantes[nome] = receber
        return self

    def enviar(self, de, para, mensagem):
        if para not in self._participantes:
            raise _erro(f"There is no participant named '{para}'.",
                        nota="registered: " + ", ".join(sorted(self._participantes)))
        self.mensagens += 1
        return _chamar(self._participantes[para], de, mensagem)

    def difundir(self, de, mensagem):
        entregues = 0
        for nome, receber in list(self._participantes.items()):
            if nome != de:
                _chamar(receber, de, mensagem)
                entregues += 1
        self.mensagens += entregues
        return entregues


class Estrategias:
    """Strategy por nome, para quando a escolha vem de configuracao."""

    def __init__(self, padrao=None):
        self._estrategias = {}
        self._padrao = padrao

    def registrar(self, nome, acao):
        self._estrategias[nome] = acao
        return self

    def usar(self, nome, *args):
        acao = self._estrategias.get(nome)
        if acao is None:
            if self._padrao is None:
                raise _erro(f"There is no strategy named '{nome}'.",
                            nota="registered: " + ", ".join(sorted(self._estrategias)))
            acao = self._estrategias[self._padrao]
        return _chamar(acao, *args)

    def nomes(self):
        return sorted(self._estrategias)


# ── dominio ──────────────────────────────────────────────────

class Repositorio:
    """Repositorio em memoria: o dublê certo para testar servico de dominio."""

    def __init__(self, campo_id="id"):
        self._campo = campo_id
        self._itens = {}
        self._proximo = 1
        self._trava = threading.Lock()

    def _id_de(self, item):
        from .arcane_collections import _campo_de
        return _campo_de(item, self._campo)

    def salvar(self, item):
        interp = _interp()
        with self._trava:
            ident = self._id_de(item)
            if ident is None:
                ident = self._proximo
                self._proximo += 1
                if isinstance(item, dict):
                    item[self._campo] = ident
                else:
                    interp._escrever_membro(item, self._campo, ident, _no(),
                                            interp.global_env)
            else:
                if isinstance(ident, int):
                    self._proximo = max(self._proximo, ident + 1)
            self._itens[ident] = item
        return item

    def buscar(self, ident):
        return self._itens.get(ident)

    def remover(self, ident):
        with self._trava:
            return self._itens.pop(ident, None) is not None

    def listar(self):
        return list(self._itens.values())

    def filtrar(self, especificacao):
        if isinstance(especificacao, Especificacao):
            return especificacao.filtrar(self.listar())
        return [x for x in self.listar() if _chamar(especificacao, x)]

    @property
    def total(self):
        return len(self._itens)


class Barramento:
    """CQRS: cada tipo de comando tem UM manipulador; o envio nao sabe qual."""

    def __init__(self):
        self._manipuladores = {}
        self.enviados = 0

    def manipular(self, tipo, acao):
        nome = getattr(tipo, "name", tipo)
        if nome in self._manipuladores:
            raise _erro(f"'{nome}' already has a handler.",
                        nota="a command has exactly one handler; events are for many")
        self._manipuladores[nome] = acao
        return self

    def enviar(self, comando):
        from ..builtins import _df_type
        nome = _df_type(comando)
        acao = self._manipuladores.get(nome)
        if acao is None:
            raise _erro(f"No handler for the command '{nome}'.",
                        dica=f"barramento.manipular({nome}, acao)")
        self.enviados += 1
        return _chamar(acao, comando)


class ArcanePadroes:
    """Padroes de projeto com mecanismo de verdade."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Padroes",
            # criacionais
            "unico": lambda fabrica: Unico(fabrica),
            "pool": lambda fabrica, tamanho=4, limpar=None: Pool(fabrica, tamanho, limpar),
            "construtor": lambda molde, obrigatorios=None: Construtor(molde, obrigatorios),
            "prototipos": lambda: Prototipos(),
            "compartilhado": lambda fabrica: Compartilhado(fabrica),
            # estruturais
            "proxy": lambda alvo, interceptar: Proxy(alvo, interceptar),
            "adaptar": lambda alvo, mapa: Adaptador(alvo, mapa),
            "composto": lambda valor=None: Composto(valor),
            # comportamentais
            "comandos": lambda limite=100: Comandos(limite),
            "cadeia": _cadeia,
            "especificacao": lambda predicado, nome="especificacao":
                Especificacao(predicado, nome),
            "maquina": lambda inicial, transicoes: Maquina(inicial, transicoes),
            "memento": _memento,
            "restaurar": _restaurar,
            "visitar": _visitar,
            "observavel": lambda: Observavel(),
            "mediador": lambda: Mediador(),
            "estrategias": lambda padrao=None: Estrategias(padrao),
            # dominio
            "repositorio": lambda campo_id="id": Repositorio(campo_id),
            "barramento": lambda: Barramento(),
        }
