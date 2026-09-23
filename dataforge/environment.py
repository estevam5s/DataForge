"""
DataForge Environment (Scope Manager)
Manages variable scopes, constants, and name resolution.
"""

from .errors import NameError_, RuntimeError_


#: O conjunto vazio que todo escopo novo compartilha.
#:
#: Cada 'Environment' alocava DOIS sets vazios no construtor — 'constants'
#: e 'embutidas' — e escopo nasce em toda chamada de acao e em todo laco.
#: Medido no 'fib(24)': 150 mil chamadas, 300 mil sets que quase nunca
#: recebem nada. Imutavel de proposito: quem precisar escrever troca pelo
#: seu proprio set antes (ver 'define_steady'), e um 'add' esquecido falha
#: alto em vez de escrever no conjunto de todos.
_VAZIO = frozenset()

#: O que `get` devolve quando o nome nao esta NAQUELE escopo.
#:
#: Um sentinela, e nao `None`: `void` e um valor legitimo da linguagem,
#: e `variaveis.get(nome)` devolvendo `None` nao distingue "nao existe"
#: de "existe e vale void" — a diferenca que um `??` inteiro depende.
_FALTA = object()


class Environment:
    """A scope environment for variable/function lookups."""

    # __slots__ economiza o dict de atributos de cada escopo. Um laco de
    # 200 mil voltas cria 200 mil escopos, e cada um custava um dict a
    # mais so para guardar quatro campos.
    # '_deferred' e '_exports' sao anexados pelo interpretador em
    # escopos especificos (blocos com 'defer', modulos com 'relay'). Com
    # __slots__ eles precisam ser declarados aqui, senao o Python recusa
    # a atribuicao — e o erro aparece longe da causa.
    __slots__ = ("parent", "name", "variables", "constants", "embutidas",
                 "_deferred", "_exports", "_export_de")

    def __init__(self, parent=None, name: str = "<global>"):
        self.parent = parent
        self.name = name
        self.variables: dict = {}
        self.constants = _VAZIO     # Names that are immutable (steady)
        #: Os nomes que a LINGUAGEM pos aqui, e nao quem escreve.
        #:
        #: Eles vivem no mesmo dicionario do escopo global, e por isso
        #: um 'len := 42' dentro de uma acao os encontrava ao subir a
        #: cadeia e os SOBRESCREVIA — para o programa inteiro:
        #:
        #:     action c():
        #:         len := 42          # parece uma variavel local
        #:         yield len
        #:     out c()                # 42
        #:     out len([1, 2, 3])     # '42' is not callable
        #:
        #: Sao 228 nomes, e entre eles estao 'id', 'len', 'type', 'str',
        #: 'sum', 'min', 'max', 'count', 'round', 'first', 'last' —
        #: exatamente os que alguem usa como variavel local sem pensar.
        #: A falha aparece longe: a acao funciona, e o programa quebra
        #: na proxima vez que alguem chamar a embutida.
        self.embutidas = _VAZIO
        #: Os 'defer' deste escopo, criada no primeiro. Inicializado aqui
        #: porque ler um slot NUNCA atribuido levanta por dentro — e a
        #: chamada de acao pergunta isto em toda saida.
        self._deferred = None

    def get(self, name: str):
        """Procura o nome, subindo a cadeia de escopos.

        Em LACO, e nao em recursao, e com UMA consulta por escopo.

        A versao recursiva custava uma chamada de funcao do Python por
        nivel da cadeia — e a cadeia de um metodo dentro de um laco
        dentro de uma acao tem quatro. Medido com cProfile numa carga
        de referencia: 2,47 milhoes de chamadas a `get`, das quais
        700 mil eram so o salto para o escopo de cima.

        A busca continua sendo `in` seguido de `[]`, e NAO um
        `variaveis.get(nome, sentinela)`: medido, a versao com `get` e
        mais LENTA. Sao duas operacoes rapidas de dicionario contra uma
        chamada de metodo, e a chamada custa mais que a segunda busca.
        """
        escopo = self
        while escopo is not None:
            variaveis = escopo.variables
            if name in variaveis:
                return variaveis[name]
            escopo = escopo.parent
        raise self._erro_de_nome(name)

    # ── Diagnostico ──────────────────────────────────────────

    def nomes_visiveis(self):
        """Tudo o que este escopo enxerga, do mais proximo ao mais distante."""
        vistos, escopo = [], self
        while escopo is not None:
            for nome in escopo.variables:
                if not nome.startswith('__') and nome not in vistos:
                    vistos.append(nome)
            escopo = escopo.parent
        return vistos

    def _erro_de_nome(self, name):
        """'x nao existe' e pouco. Sugerir o parecido resolve a maioria.

        A sugestao e ADIADA: `difflib` compara o nome pedido com TODOS
        os nomes visiveis — e no escopo global sao mais de 230, so de
        embutidas. Ha caminhos em que este erro nasce e morre sem
        ninguem le-lo (`x ?? padrao`, um `monitor` que espera a falta),
        e ali o texto nunca chega a ser preciso.
        """
        def _perto():
            import difflib
            return difflib.get_close_matches(name, self.nomes_visiveis(),
                                             n=3, cutoff=0.7)

        def nota():
            # Escrito depois de usado? Ou so nao existe mesmo?
            return ("" if _perto()
                    else "this name was never assigned in any enclosing scope")

        def dica():
            perto = _perto()
            if not perto:
                return (f"assign it before using:  {name} := …\n"
                        "remember DataForge assigns with ':=', not '='")
            if len(perto) == 1:
                return f"did you mean '{perto[0]}'?"
            return ("did you mean one of: "
                    + ", ".join(f"'{p}'" for p in perto) + "?")

        return NameError_(f"'{name}' is not defined.",
                          nota=nota, dica=dica, doc="variaveis",
                          rotulo="used here")

    def set(self, name: str, value):
        """Set a variable in the current scope."""
        if name in self.constants:
            raise RuntimeError_(
                f"'{name}' is steady and cannot be reassigned.",
                nota="'steady' declares a value that never changes",
                dica=(f"use a different name for the new value, or declare "
                      f"'{name}' with ':=' instead of 'steady' if it does "
                      f"need to change"),
                doc="variaveis")

        # Walk up to find existing variable to update
        env = self
        while env is not None:
            # Uma EMBUTIDA nao e uma variavel de quem escreve: subir ate
            # ela e reescreve-la apaga a funcao para o programa todo.
            # Aqui a atribuicao para, e o nome vira local — que e o que
            # toda linguagem com escopo de embutidas faz.
            if name in env.embutidas:
                if env is self:
                    # A atribuicao acontece NO MESMO escopo onde a
                    # embutida vive: quem escreve esta tomando o nome
                    # para si, ali, de proposito. A marca sai junto.
                    #
                    # Sem esta saida, 'count := 5' no topo do arquivo
                    # gravava o 5 e continuava marcado como embutida —
                    # e entao 'count := count - 1' dentro de um
                    # 'persist' nao achava o nome ao subir, criava um
                    # 'count' local do bloco, e o de fora ficava em 5
                    # PARA SEMPRE. O laco nunca terminava, sem nenhum
                    # erro: 'examples/04_loops.df' imprimia '5' ate a
                    # maquina ser desligada.
                    #
                    # Sao 228 nomes, e 'count', 'sum', 'min', 'max',
                    # 'first' e 'last' sao justamente os que alguem usa
                    # como contador ou acumulador sem pensar.
                    env.embutidas.discard(name)
                    env.variables[name] = value
                    return
                break
            if name in env.variables:
                if name in env.constants:
                    raise RuntimeError_(
                        f"'{name}' is steady and cannot be reassigned.",
                        nota="'steady' declares a value that never changes",
                        dica=(f"pick another name, or declare '{name}' with "
                              f"':=' if it needs to change"),
                        doc="variaveis")
                env.variables[name] = value
                return
            env = env.parent

        # New variable in current scope
        self.variables[name] = value

    def set_local(self, name: str, value):
        """Define/set a variable strictly in the current scope."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot reassign steady (constant) '{name}'")
        self.variables[name] = value

    def define_steady(self, name: str, value):
        """Define an immutable constant."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot reassign steady (constant) '{name}'")
        self.variables[name] = value
        if self.constants is _VAZIO:
            self.constants = set()
        self.constants.add(name)

    def define_shadow(self, name: str, value):
        """Define a local shadow variable that overrides parent scope."""
        self.variables[name] = value

    def has(self, name: str) -> bool:
        """Check if a name exists in any scope."""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

    def has_local(self, name: str) -> bool:
        """Check if a name exists in the current scope only."""
        return name in self.variables

    def delete(self, name: str):
        """Remove a variable from the current or parent scope."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot delete steady (constant) '{name}'")
        if name in self.variables:
            del self.variables[name]
            return
        if self.parent:
            self.parent.delete(name)
            return
        raise NameError_(f"Cannot delete undefined name: '{name}'")

    def child(self, name: str = "<block>"):
        """Create a child scope."""
        return Environment(parent=self, name=name)

    def limpar(self):
        """Esvazia o escopo para reutiliza-lo.

        Um laco cria um escopo por volta. Reaproveitar o mesmo objeto,
        limpando-o, evita alocar um Environment por iteracao — desde
        que ninguem tenha guardado uma referencia a ele, o que so
        acontece quando o corpo declara uma acao (que captura o escopo
        no fechamento).
        """
        self.variables.clear()
        if self.constants:
            self.constants.clear()

    def __repr__(self):
        keys = list(self.variables.keys())
        return f"Environment({self.name}, vars={keys})"
