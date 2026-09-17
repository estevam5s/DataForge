"""
Arcane.Injecao — o conteiner que monta o grafo de objetos.

    adopt Arcane.Injecao as DI

    contract Repositorio:
        action salvar(item)

    blueprint RepoSql with Repositorio:
        action salvar(item):
            yield item

    blueprint Cadastro(repo: Repositorio):
        action registrar(nome):
            yield self.repo.salvar(nome)

    c := DI.conteiner()
    c.unico(Repositorio, RepoSql)          // a implementacao do contrato
    c.transitorio(Cadastro)                // um novo a cada pedido
    cadastro := c.resolver(Cadastro)       // o repo chega pelo construtor

O conteiner le o TIPO dos parametros do construtor — os do cabecalho e
os do 'setup' — e resolve cada um. Nao ha anotacao nova: 'repo:
Repositorio' ja dizia do que o objeto precisa, e e isso que o Principio
da Inversao de Dependencia pede — depender do contrato, e deixar que
alguem de fora escolha a implementacao.

─── Tempo de vida ───────────────────────────────────────────────

    unico         uma instancia para o conteiner inteiro (singleton)
    transitorio   uma nova a cada 'resolver'
    por_escopo    uma por escopo: 'c.escopo()' abre um, e ele guarda as suas

Um 'por_escopo' pedido direto ao conteiner raiz e recusado. Resolver
ali o transformaria num 'unico' calado — e o caso real, uma conexao por
pedido HTTP, passaria a compartilhar a conexao entre pedidos.

─── O que o conteiner recusa, e por que ─────────────────────────

- Dependencia circular, com a cadeia inteira na mensagem: A → B → A. A
  saida e 'c.preguicoso(Tipo)', que entrega um objeto que so resolve na
  primeira vez que e usado.
- Um parametro cujo tipo ninguem registrou. Se ele tem PADRAO, e
  opcional, e o padrao vale — a dependencia opcional do documento.
- Um 'unico' que depende de um 'por_escopo'. A instancia unica viveria
  mais que o escopo, e seguraria para sempre um objeto que devia morrer
  com ele — o 'captive dependency', o erro mais comum de todo conteiner.
"""

import threading


def _interp():
    from ..interpreter import DFAction
    return DFAction._interpreter


def _i():
    from .. import interpreter as i
    return i


def _no():
    return _interp()._no_interno()


def _nome_da_chave(chave):
    return getattr(chave, "name", None) or str(chave)


_ESCOPOS = ("unico", "transitorio", "por_escopo")


def _marca(alvo, nome):
    """'@Servico' ou '@DI.Servico' — o decorador pelo ultimo segmento."""
    for marca in getattr(alvo, "__metadados__", None) or []:
        if marca["nome"].rsplit(".", 1)[-1] == nome:
            return marca
    return None


class _Registro:
    __slots__ = ("chave", "implementacao", "escopo", "fabrica", "valor", "tem_valor")

    def __init__(self, chave, implementacao=None, escopo="transitorio",
                 fabrica=None, valor=None, tem_valor=False):
        self.chave = chave
        self.implementacao = implementacao
        self.escopo = escopo
        self.fabrica = fabrica
        self.valor = valor
        self.tem_valor = tem_valor


class Preguicoso:
    """Um objeto que so e resolvido na primeira vez que alguem o usa."""

    def __init__(self, conteiner, chave):
        self._conteiner = conteiner
        self._chave = chave
        self._valor = None
        self._pronto = False
        self._trava = threading.Lock()

    @property
    def valor(self):
        if not self._pronto:
            with self._trava:
                if not self._pronto:
                    self._valor = self._conteiner.resolver(self._chave)
                    self._pronto = True
        return self._valor

    def pronto(self):
        return self._pronto

    def __repr__(self):
        return f"<preguicoso {_nome_da_chave(self._chave)}>"


class Conteiner:
    """Registro de dependencias e montagem do grafo."""

    def __init__(self, pai=None, nome="raiz"):
        self._pai = pai
        self.nome = nome
        self._registros = {} if pai is None else pai._registros
        self._unicos = {} if pai is None else pai._unicos
        self._do_escopo = {}
        self._trava = threading.RLock() if pai is None else pai._trava
        self._resolvendo = threading.local()
        self._fechado = False
        self._criados = []

    # ── registrar ──

    def _registrar(self, chave, registro):
        if self._pai is not None:
            from ..errors import DependencyResolutionError
            raise DependencyResolutionError(
                "Register dependencies in the root container, not in a scope.",
                nota="a scope shares the registrations of its root, and keeps "
                     "only its own instances",
                doc="oop/injecao")
        self._registros[chave] = registro
        return self

    def unico(self, chave, implementacao=None):
        return self._registrar(chave, _Registro(chave, implementacao or chave, "unico"))

    def transitorio(self, chave, implementacao=None):
        return self._registrar(chave, _Registro(chave, implementacao or chave,
                                                "transitorio"))

    def por_escopo(self, chave, implementacao=None):
        return self._registrar(chave, _Registro(chave, implementacao or chave,
                                                "por_escopo"))

    def valor(self, chave, valor):
        """Um objeto pronto: configuracao, conexao aberta, um dublê de teste."""
        return self._registrar(chave, _Registro(chave, None, "unico", valor=valor,
                                                tem_valor=True))

    def fabrica(self, chave, acao, escopo="transitorio"):
        """'acao(conteiner)' constroi o objeto — quando o construtor nao basta."""
        if escopo not in _ESCOPOS:
            from ..errors import ValueError_
            raise ValueError_(f"'{escopo}' is not a lifetime. Use: "
                              f"{', '.join(_ESCOPOS)}.", doc="oop/injecao")
        return self._registrar(chave, _Registro(chave, None, escopo, fabrica=acao))

    def registrar(self, molde):
        """Le '@Servico(escopo)' e '@Fornece(Contrato)' do blueprint."""
        servico = _marca(molde, "Servico")
        fornece = _marca(molde, "Fornece")
        escopo = ((servico or {}).get("args") or [None])[0] or \
            ((servico or {}).get("kwargs") or {}).get("escopo", "transitorio")
        contrato = ((fornece or {}).get("args") or [None])[0] or molde
        if escopo not in _ESCOPOS:
            from ..errors import ValueError_
            raise ValueError_(f"@Servico('{escopo}') is not a lifetime. Use: "
                              f"{', '.join(_ESCOPOS)}.", doc="oop/injecao")
        return self._registrar(contrato, _Registro(contrato, molde, escopo))

    def tem(self, chave):
        return chave in self._registros

    # ── resolver ──

    def _pilha(self):
        pilha = getattr(self._resolvendo, "pilha", None)
        if pilha is None:
            pilha = self._resolvendo.pilha = []
        return pilha

    def resolver(self, chave):
        from ..errors import CircularDependencyError, DependencyResolutionError
        if self._fechado:
            raise DependencyResolutionError(
                f"The scope '{self.nome}' is closed.", doc="oop/injecao")
        registro = self._registros.get(chave)
        if registro is None:
            i = _i()
            if isinstance(chave, i.DFBlueprint) and not chave.is_abstract \
                    and not chave.e_contrato:
                registro = _Registro(chave, chave, "transitorio")
            else:
                raise DependencyResolutionError(
                    f"Nothing is registered for '{_nome_da_chave(chave)}'.",
                    nota=self._cadeia(chave) or "",
                    dica=f"register it:  c.unico({_nome_da_chave(chave)}, "
                         f"Implementacao)",
                    doc="oop/injecao")

        pilha = self._pilha()
        if chave in pilha:
            cadeia = " → ".join(_nome_da_chave(k) for k in pilha[pilha.index(chave):])
            raise CircularDependencyError(
                f"Circular dependency: {cadeia} → {_nome_da_chave(chave)}.",
                dica=f"break the cycle with  c.preguicoso({_nome_da_chave(chave)})  "
                     f"in one of the constructors, or extract what they share",
                doc="oop/injecao")

        if registro.escopo == "unico":
            with self._trava:
                if chave in self._unicos:
                    return self._unicos[chave]
                self._conferir_cativo(chave, registro)
                valor = self._construir(chave, registro)
                self._unicos[chave] = valor
                return valor
        if registro.escopo == "por_escopo":
            if self._pai is None:
                raise DependencyResolutionError(
                    f"'{_nome_da_chave(chave)}' lives per scope and was requested "
                    f"from the root container.",
                    nota="resolving it here would silently make it a singleton",
                    dica="open a scope:  escopo := c.escopo()  then "
                         "escopo.resolver(…)",
                    doc="oop/injecao")
            if chave not in self._do_escopo:
                self._do_escopo[chave] = self._construir(chave, registro)
            return self._do_escopo[chave]
        return self._construir(chave, registro)

    def _cadeia(self, ultimo):
        pilha = self._pilha()
        if not pilha:
            return ""
        return "needed by: " + " → ".join(_nome_da_chave(k) for k in pilha)

    def _conferir_cativo(self, chave, registro):
        """Um 'unico' nao pode depender de algo 'por_escopo'."""
        from ..errors import DependencyResolutionError
        for dependencia in self._dependencias(registro):
            outro = self._registros.get(dependencia)
            if outro is not None and outro.escopo == "por_escopo":
                raise DependencyResolutionError(
                    f"'{_nome_da_chave(chave)}' is a singleton and depends on "
                    f"'{_nome_da_chave(dependencia)}', which lives per scope.",
                    nota="the singleton would outlive the scope and hold its "
                         "object forever",
                    dica="make the dependency a singleton too, or receive a "
                         "c.preguicoso(…) and resolve it inside the scope",
                    doc="oop/injecao")

    def _construir(self, chave, registro):
        interp = _interp()
        if registro.tem_valor:
            return registro.valor
        pilha = self._pilha()
        pilha.append(chave)
        try:
            if registro.fabrica is not None:
                valor = interp._call(registro.fabrica, [self], {}, _no(),
                                     interp.global_env)
            else:
                valor = self._instanciar(registro.implementacao)
        finally:
            pilha.pop()
        self._criados.append(valor)
        return valor

    def _parametros_do_construtor(self, molde):
        """[(nome, tipo, tem_padrao)] — do cabecalho, ou do 'setup'."""
        i = _i()
        if molde.constructor_params:
            return [(p, molde.tipos_do_cabecalho.get(p), p in molde.padroes_do_cabecalho)
                    for p in molde.constructor_params]
        for nome in ("setup", "initiate", "__init__"):
            acao = molde.methods.get(nome)
            if isinstance(acao, i.DFAction):
                return [(p, acao.param_types.get(p), p in acao.defaults)
                        for p in acao.params]
        return []

    def _dependencias(self, registro):
        i = _i()
        molde = registro.implementacao
        if not isinstance(molde, i.DFBlueprint):
            return []
        saida = []
        for _nome, tipo, _padrao in self._parametros_do_construtor(molde):
            chave = self._chave_do_tipo(tipo, molde)
            if chave is not None:
                saida.append(chave)
        return saida

    def _chave_do_tipo(self, tipo, molde):
        """O registro que atende a um nome de tipo: por objeto ou por texto."""
        if not tipo:
            return None
        base = tipo.rsplit(".", 1)[-1]
        for chave in self._registros:
            if _nome_da_chave(chave) == base:
                return chave
        try:
            valor = molde.env.get(base)
        except Exception:
            return None
        i = _i()
        if isinstance(valor, i.DFBlueprint):
            return valor
        return None

    def _instanciar(self, molde):
        from ..errors import DependencyResolutionError
        i = _i()
        interp = _interp()
        if not isinstance(molde, i.DFBlueprint):
            return molde
        argumentos = {}
        for nome, tipo, tem_padrao in self._parametros_do_construtor(molde):
            if tipo == "Preguicoso" or (tipo or "").endswith(".Preguicoso"):
                raise DependencyResolutionError(
                    f"'{molde.name}.{nome}' asks for a Preguicoso without saying of "
                    f"what.", dica="receive the contract type and register "
                                   "c.fabrica(Tipo, lambda c => c.preguicoso(Outro))",
                    doc="oop/injecao")
            chave = self._chave_do_tipo(tipo, molde)
            if chave is not None and (chave in self._registros or (
                    isinstance(chave, i.DFBlueprint) and not chave.is_abstract
                    and not chave.e_contrato)):
                argumentos[nome] = self.resolver(chave)
            elif tem_padrao:
                continue
            else:
                motivo = (f"its type '{tipo}' has nothing registered" if tipo
                          else "it declares no type, so the container cannot "
                               "know what to pass")
                raise DependencyResolutionError(
                    f"Cannot build '{molde.name}': the parameter '{nome}' cannot be "
                    f"resolved — {motivo}.",
                    nota=self._cadeia(molde) or "",
                    dica=(f"register it:  c.unico({tipo}, Implementacao)" if tipo
                          else f"declare the type:  {nome}: Contrato  — or give it "
                               f"a default to make it optional"),
                    doc="oop/injecao")
        objeto = interp._instanciar(molde, [], argumentos, _no(), interp.global_env)
        # injecao por CAMPO: '@Injetar' sobre um campo tipado
        for campo, marcas in molde.metadados_de_campo.items():
            if not any(m["nome"].rsplit(".", 1)[-1] in ("Injetar", "Inject")
                       for m in marcas):
                continue
            tipo = next((t for n, t, _p, _v in molde.fields_decl if n == campo), None)
            chave = self._chave_do_tipo(tipo, molde)
            if chave is None:
                raise DependencyResolutionError(
                    f"'{molde.name}.{campo}' is marked @Injetar but has no type the "
                    f"container knows.", dica=f"declare it  {campo}: Contrato",
                    doc="oop/injecao")
            interp._gravar_campo_cru(objeto, campo, self.resolver(chave))
        return objeto

    def chamar(self, acao, extras=None):
        """Injecao por METODO: resolve os parametros tipados e chama."""
        i = _i()
        interp = _interp()
        nomeados = dict(extras or {})
        for p in acao.params:
            if p in nomeados:
                continue
            tipo = acao.param_types.get(p)
            chave = self._chave_do_tipo(tipo, _Molde(acao.closure))
            if chave is not None:
                nomeados[p] = self.resolver(chave)
        return interp._call(acao, [], nomeados, _no(), interp.global_env)

    def preguicoso(self, chave):
        return Preguicoso(self, chave)

    # ── escopos ──

    def escopo(self, nome="escopo"):
        return Conteiner(pai=self._pai or self, nome=nome)

    def fechar(self):
        """Fecha o escopo: 'fechar()' ou 'teardown()' de cada objeto criado nele."""
        interp = _interp()
        i = _i()
        fechados = 0
        for obj in reversed(list(self._do_escopo.values())):
            if isinstance(obj, i.DFInstance):
                for nome in ("fechar", "teardown"):
                    acao = obj.blueprint.methods.get(nome)
                    if isinstance(acao, i.DFAction):
                        interp._call_action(acao, [], {}, _no(), None, instance=obj)
                        fechados += 1
                        break
        self._do_escopo.clear()
        self._fechado = True
        return fechados

    def abrir(self):
        return self

    # ── diagnostico ──

    def grafo(self):
        """{Tipo: [dependencias]} — o grafo que o conteiner monta."""
        return {_nome_da_chave(k): [_nome_da_chave(d) for d in self._dependencias(r)]
                for k, r in self._registros.items()}

    def conferir(self):
        """Resolve tudo o que esta registrado, sem guardar nada. Lista os problemas.

        Um conteiner que so descobre o registro que falta quando a rota
        e chamada descobre em producao. 'conferir' no teste pega antes.
        """
        from ..errors import DataForgeError
        problemas = []
        for chave, registro in list(self._registros.items()):
            escopo = self if registro.escopo != "por_escopo" else self.escopo("conferencia")
            try:
                if registro.escopo == "unico" and chave not in self._unicos:
                    escopo._conferir_cativo(chave, registro)
                    escopo._construir(chave, registro)
                elif registro.escopo != "unico":
                    escopo.resolver(chave)
            except DataForgeError as erro:
                problemas.append(f"{_nome_da_chave(chave)}: {erro.message}")
        return problemas

    def __repr__(self):
        return f"<conteiner {self.nome}: {len(self._registros)} registro(s)>"


class _Molde:
    """O minimo de um blueprint que '_chave_do_tipo' precisa: um escopo."""

    def __init__(self, env):
        self.env = env


class ArcaneInjecao:
    """Injecao de dependencia e inversao de controle."""

    def __new__(cls):
        def servico(escopo="transitorio"):
            """@Servico("unico") — so anota; 'c.registrar(Bp)' le."""
            def anotar(alvo):
                return None
            return anotar

        def fornece(contrato):
            def anotar(alvo):
                return None
            return anotar

        def injetar(alvo=None):
            return None

        return {
            "__name__": "Arcane.Injecao",
            "conteiner": lambda nome="raiz": Conteiner(nome=nome),
            "Servico": servico,
            "Fornece": fornece,
            "Injetar": injetar,
            "ESCOPOS": list(_ESCOPOS),
        }
