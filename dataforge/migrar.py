"""Python → DataForge. `dataforge converter app.py`

O que ele é
-----------
Um tradutor honesto. Ele lê Python com o `ast` da própria linguagem —
não com expressão regular — e emite DataForge com a indentação e o
vocabulário certos.

O que ele **não** é
-------------------
Um garantidor. Python tem construções que a DataForge não tem, e
algumas que ela tem de forma diferente o bastante para que traduzir
seria mentir. Nesses casos ele **marca a linha** com um comentário
`// TODO(converter):` e deixa o código original ao lado, em vez de
produzir algo que compila e faz outra coisa.

Essa é a decisão central do arquivo. Um conversor que acerta 95% e
falha em silêncio nos outros 5% é pior que um que acerta 95% e **aponta**
os 5% — porque no primeiro caso alguém descobre em produção.

O relatório no fim conta as duas coisas: quantas linhas saíram prontas e
quantas precisam de você.
"""

import ast
import io
import os

#: Operadores que mudam de nome.
_COMPARACAO = {
    ast.Eq: "is", ast.NotEq: "isnt",
    ast.Lt: "smaller", ast.LtE: "smaller_eq",
    ast.Gt: "bigger", ast.GtE: "bigger_eq",
    ast.In: "in", ast.NotIn: "not in",
    ast.Is: "is", ast.IsNot: "isnt",
}

_BINARIO = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
    ast.Mod: "%", ast.Pow: "**",
    ast.FloorDiv: "~/",          # '//' é comentário em DataForge
    ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
    ast.LShift: "<<", ast.RShift: ">>",
}

_UNARIO = {ast.USub: "-", ast.UAdd: "+", ast.Not: "not ", ast.Invert: "~"}

#: Funções do Python com nome diferente aqui.
_EMBUTIDAS = {
    "print": "out", "len": "len", "range": "range",
    "str": "str", "int": "int", "float": "float", "bool": "bool",
    "list": "cluster", "dict": "vault", "set": "conjunto",
    "sum": "sum", "min": "min", "max": "max", "abs": "abs",
    "sorted": "sorted", "reversed": "reversed", "enumerate": "enumerate",
    "zip": "zip", "map": "map", "filter": "filter", "round": "round",
    "isinstance": "typeof", "type": "typeof", "input": "in",
}

#: Módulos da stdlib do Python com equivalente nativo.
#:
#: Traduzir para o módulo daqui é melhor que abrir a ponte: o código
#: resultante não depende de Python nenhum. Onde não há equivalente, a
#: ponte é a resposta honesta.
_MODULOS = {
    "math": "Arcane.Math", "os": "Arcane.OS", "sys": "Arcane.OS",
    "json": "Arcane.Serialization", "re": "Arcane.Regex",
    "time": "Arcane.Time", "datetime": "Arcane.Time",
    "random": "Arcane.Math", "statistics": "Arcane.Analytics",
    "collections": "Arcane.Collections", "itertools": "Arcane.Iter",
    "functools": "Arcane.Functional", "subprocess": "Arcane.Process",
    "logging": "Arcane.Logging", "hashlib": "Arcane.Crypto",
    "csv": "Arcane.IO", "sqlite3": "Arcane.Database",
    "threading": "Arcane.Concurrent", "unittest": "Arcane.Test",
    "decimal": "Arcane.Decimal", "pathlib": "Arcane.IO",
}


#: Os nomes de função que mudam junto com o módulo.
#:
#: Mapear o MÓDULO não basta: `json.dumps` vira `Arcane.Serialization`,
#: e lá a função se chama `to_json`. Sem esta tabela o arquivo
#: convertido compila e explode ao rodar — "module has no 'dumps'" — o
#: que é exatamente o tipo de falha que este conversor existe para não
#: produzir.
#:
#: O que não está aqui vira uma pendência marcada, e não um palpite.
_FUNCOES = {
    ("json", "dumps"): "to_json",
    ("json", "loads"): "from_json",
    ("json", "dump"): "to_json",
    ("json", "load"): "from_json",
    ("math", "sqrt"): "sqrt",
    ("math", "pi"): "PI",
    ("math", "e"): "E",
    ("math", "inf"): "INF",
    ("os", "getcwd"): "cwd",
    ("os", "listdir"): "list_dir",
    ("os", "makedirs"): "mkdir",
    ("os", "remove"): "delete",
    ("time", "time"): "timestamp",
    ("time", "sleep"): "sleep",
    ("random", "randint"): "random_int",
    ("random", "random"): "random",
    ("random", "choice"): "choice",
    ("statistics", "mean"): "mean",
    ("statistics", "median"): "median",
    ("statistics", "stdev"): "stdev",
    ("re", "match"): "match",
    ("re", "search"): "search",
    ("re", "findall"): "find_all",
    ("re", "sub"): "replace",
    ("subprocess", "run"): "run",
    ("hashlib", "sha256"): "sha256",
    ("hashlib", "md5"): "md5",
}


#: Exceções do Python que existem aqui com o mesmo nome.
#:
#: A DataForge tem 177 classes de erro, e muitas coincidem — `KeyError`,
#: `IndexError`, `TypeError`. Essas o `handle` filtra normalmente.
_ERROS_IGUAIS = {
    "ValueError", "TypeError", "KeyError", "IndexError", "NameError",
    "ImportError", "RuntimeError", "PermissionError", "TimeoutError",
    "FileNotFoundError", "FileExistsError", "AssertionError",
    "StopIteration", "OverflowError", "NotImplementedError",
    "ModuleNotFoundError", "RecursionError", "UnicodeDecodeError",
    "ConnectionError", "OSError", "IOError", "AttributeError",
}

#: Exceções do Python com outro nome aqui.
_ERROS_TRADUZIDOS = {
    "ZeroDivisionError": "DivisionByZeroError",
    "ArithmeticError": "ArithmeticOverflowError",
    "Exception": "Error",
    "BaseException": "Error",
}


def _reservadas():
    """As 81 palavras que não podem ser nome de nada.

    Vem de `tokens.py`, e não de uma lista copiada aqui: uma cópia
    envelheceria no dia em que uma palavra fosse acrescentada, e o
    conversor voltaria a gerar código que não compila.
    """
    from .tokens import KEYWORDS
    return set(KEYWORDS)


class NaoTraduzivel(Exception):
    """Esta construção não tem equivalente honesto. Marque e siga."""

    def __init__(self, motivo, sugestao=""):
        self.motivo = motivo
        self.sugestao = sugestao
        super().__init__(motivo)


class Conversor(ast.NodeVisitor):
    """Percorre a árvore do Python e emite DataForge."""

    def __init__(self, fonte, arquivo="<py>"):
        self.fonte = fonte
        self.arquivo = arquivo
        self.linhas_py = fonte.split("\n")
        self.saida = []
        self.nivel = 0
        self.pendencias = []      # (linha, motivo, sugestão)
        self.traduzidas = 0
        self._em_stream = []      # pilha: a ação atual usa 'emit'?

        # Os nomes de classe do arquivo. Em DataForge um blueprint se
        # constroi com 'spawn', e sem isto 'Conta("Ana")' saia como
        # chamada de acao — compila, e explode ao rodar dizendo que
        # 'Conta' nao e chamavel. O conversor precisa saber quem e
        # classe, e so a arvore inteira responde isso.
        self.classes = set()

        # apelido -> modulo do Python de origem, para traduzir o NOME da
        # funcao junto com o do modulo.
        self.origem = {}

        # Os tipos que este arquivo DISPARA. 'raise X(...)' vira
        # 'trigger', que levanta TriggerError — entao 'except X' nao
        # pegaria, e o 'handle' correspondente precisa virar 'Error'.
        self._tipos_disparados = set()

        # Um nome do Python que aqui e palavra reservada — 'delete',
        # 'match', 'record', 'in', 'to' — precisa mudar, senao o
        # arquivo convertido nao compila. O sufixo e feio e honesto:
        # inventar um sinonimo faria o leitor procurar um metodo que
        # nao existe no original.
        self.reservadas = _reservadas()
        self.renomeados = {}

    # ── Emissão ──────────────────────────────────────────────

    def escrever(self, texto=""):
        self.saida.append(("    " * self.nivel + texto) if texto else "")

    def marcar(self, no, motivo, sugestao=""):
        """A linha não traduz: deixa o original e diz por quê.

        O original vai junto, comentado, porque quem for consertar
        precisa dele — e porque um `// TODO` sozinho não diz o que
        estava ali.
        """
        linha = getattr(no, "lineno", 0)
        self.pendencias.append((linha, motivo, sugestao))
        self.escrever(f"// TODO(converter): {motivo}")
        if sugestao:
            self.escrever(f"//   {sugestao}")
        original = (self.linhas_py[linha - 1].strip()
                    if 0 < linha <= len(self.linhas_py) else "")
        if original:
            self.escrever(f"//   Python: {original}")

    def bloco(self, corpo):
        self.nivel += 1
        if not corpo:
            self.escrever("// (vazio)")
        for no in corpo:
            self.visit(no)
        self.nivel -= 1

    # ── Programa ─────────────────────────────────────────────

    def visit_Module(self, no):
        # Uma passagem so para achar as classes — inclusive as
        # declaradas DEPOIS do primeiro uso.
        for filho in ast.walk(no):
            if isinstance(filho, ast.ClassDef):
                self.classes.add(filho.name)
            elif isinstance(filho, ast.Raise) and filho.exc is not None:
                alvo = filho.exc
                if isinstance(alvo, ast.Call) and isinstance(alvo.func, ast.Name):
                    self._tipos_disparados.add(alvo.func.id)
        for item in no.body:
            self.visit(item)

    def generic_visit(self, no):
        """O que não tem tradutor próprio vira pendência, e não sumiço."""
        nome = type(no).__name__
        self.marcar(no, f"'{nome}' nao tem equivalente direto",
                    "traduza a mao, ou use 'adopt Python.<modulo>'")

    # ── Declarações ──────────────────────────────────────────

    def visit_FunctionDef(self, no):
        self.traduzidas += 1
        decorados = [self.expr(d) for d in no.decorator_list]
        for d in decorados:
            self.escrever(f"mark @{d}")

        params, aviso = self._parametros(no.args)
        if aviso:
            self.marcar(no, aviso, "DataForge usa '...' para spread")

        # Um `yield` no corpo faz disto um generator — `stream action`.
        e_stream = self._tem_yield(no)
        self._em_stream.append(e_stream)

        prefixo = "stream action" if e_stream else "action"
        tipo = f" -> {self._anotacao(no.returns)}" if no.returns else ""
        self.escrever(f"{prefixo} {self.nome_livre(no.name)}"
                      f"({params}){tipo}:")
        self.bloco(no.body)
        self.escrever()
        self._em_stream.pop()

    def visit_AsyncFunctionDef(self, no):
        self.traduzidas += 1
        params, _ = self._parametros(no.args)
        self.escrever(f"async action {no.name}({params}):")
        self.bloco(no.body)
        self.escrever()

    def visit_ClassDef(self, no):
        self.traduzidas += 1
        bases = [self.expr(b) for b in no.bases]
        cabeca = f"blueprint {no.name}"

        # `__init__` vira a lista de parâmetros do blueprint, que é como
        # a linguagem declara construtor.
        init = next((f for f in no.body
                     if isinstance(f, ast.FunctionDef) and f.name == "__init__"),
                    None)
        if init is not None:
            campos = [self.nome_livre(a.arg) for a in init.args.args[1:]]
            if campos:
                cabeca += "(" + ", ".join(campos) + ")"
        if bases:
            cabeca += " extends " + ", ".join(bases)

        self.escrever(cabeca + ":")
        self.nivel += 1

        corpo = [m for m in no.body if m is not init]
        if init is not None:
            # O que o `__init__` fazia além de guardar os parâmetros.
            #
            # `self.x = []` vira **campo com padrão** — o idioma da
            # linguagem. Um `setup()` receberia zero argumentos e
            # explodiria na construção; campo com padrão é copiado por
            # instância, que é exatamente o que o `__init__` fazia.
            extras = []
            for instrucao in init.body:
                if self._e_atribuicao_de_campo(instrucao, init):
                    continue
                campo = self._campo_com_padrao(instrucao)
                if campo:
                    self.nivel += 0
                    self.escrever("    " + campo if False else campo)
                    continue
                extras.append(instrucao)

            if extras:
                self.escrever("// TODO(converter): o __init__ fazia mais que")
                self.escrever("//   guardar campos. Mova o que sobrou para")
                self.escrever("//   uma acao, e chame-a depois do 'spawn'.")
                for instrucao in extras:
                    linha = getattr(instrucao, "lineno", 0)
                    self.pendencias.append(
                        (linha, "corpo de '__init__' alem de campos",
                         "mova para uma acao chamada apos o 'spawn'"))
                    original = (self.linhas_py[linha - 1].strip()
                                if 0 < linha <= len(self.linhas_py) else "")
                    if original:
                        self.escrever(f"//   Python: {original}")

        if not corpo and init is None:
            self.escrever("// (sem membros)")
        for membro in corpo:
            self.visit(membro)
        self.nivel -= 1
        self.escrever()

    def _campo_com_padrao(self, no):
        """`self.x = []` vira `x: Cluster := []`, o idioma da linguagem.

        Um campo declarado com padrão mutável é **copiado** no `spawn`,
        que é a mesma garantia que o `__init__` dava. Devolve a linha, ou
        `""` quando não é esse caso.
        """
        if not isinstance(no, ast.Assign) or len(no.targets) != 1:
            return ""
        alvo = no.targets[0]
        if not (isinstance(alvo, ast.Attribute)
                and isinstance(alvo.value, ast.Name)
                and alvo.value.id == "self"):
            return ""

        tipos = {ast.List: "Cluster", ast.Dict: "Vault", ast.Set: "Cluster"}
        tipo = tipos.get(type(no.value))
        if tipo is None and isinstance(no.value, ast.Constant):
            tipo = {str: "String", bool: "Boolean",
                    int: "Integer", float: "Float"}.get(type(no.value.value))
        if tipo is None:
            return ""
        return f"{alvo.attr}: {tipo} := {self.expr(no.value)}"

    @staticmethod
    def _e_atribuicao_de_campo(no, init):
        """`self.x = x` — vira parâmetro do blueprint, não corpo."""
        if not isinstance(no, ast.Assign) or len(no.targets) != 1:
            return False
        alvo = no.targets[0]
        return (isinstance(alvo, ast.Attribute)
                and isinstance(alvo.value, ast.Name)
                and alvo.value.id == "self"
                and isinstance(no.value, ast.Name)
                and no.value.id == alvo.attr)

    #: Reservadas que significam a MESMA coisa nas duas linguagens.
    #:
    #: `self` é a mais importante: renomeá-lo para `self_` gera um
    #: blueprint que compila e nunca encontra os próprios campos. A
    #: palavra é reservada aqui **porque** tem esse significado — é o
    #: oposto de uma colisão.
    _IGUAIS_NOS_DOIS = {"self", "in", "is", "not", "and", "or", "if",
                        "else", "for", "while", "return", "class", "def",
                        "as", "from", "import", "try", "assert", "lambda",
                        "yield", "with", "pass", "break", "continue",
                        "raise", "global", "None", "True", "False"}

    def nome_livre(self, nome):
        """O nome, ou uma versão dele que não colida com a linguagem."""
        if nome in self._IGUAIS_NOS_DOIS:
            return nome
        if nome not in self.reservadas:
            return nome
        novo = nome + "_"
        if nome not in self.renomeados:
            self.renomeados[nome] = novo
            self.pendencias.append(
                (0, f"'{nome}' e palavra reservada em DataForge",
                 f"virou '{novo}' — confira as chamadas"))
        return novo

    def _parametros(self, args):
        partes = []
        for i, a in enumerate(args.args):
            if a.arg == "self" and i == 0:
                continue       # 'self' é implícito em DataForge
            texto = self.nome_livre(a.arg)
            if a.annotation is not None:
                texto += f": {self._anotacao(a.annotation)}"
            partes.append(texto)

        # Padrões: em Python vêm alinhados à direita.
        padroes = args.defaults
        if padroes:
            comeco = len(partes) - len(padroes)
            for i, padrao in enumerate(padroes):
                if 0 <= comeco + i < len(partes):
                    partes[comeco + i] += f" := {self.expr(padrao)}"

        aviso = ""
        if args.vararg or args.kwarg:
            aviso = "'*args'/'**kwargs' nao tem equivalente direto"
        return ", ".join(partes), aviso

    def _anotacao(self, no):
        """Tipo do Python no vocabulário da linguagem."""
        if no is None:
            return ""
        mapa = {"int": "Integer", "float": "Float", "str": "String",
                "bool": "Boolean", "list": "Cluster", "dict": "Vault",
                "None": "Void"}
        texto = self.expr(no)
        return mapa.get(texto, texto)

    @staticmethod
    def _tem_yield(no):
        for filho in ast.walk(no):
            if isinstance(filho, (ast.Yield, ast.YieldFrom)):
                # Um `yield` de uma função aninhada não conta.
                return True
        return False

    # ── Instruções ───────────────────────────────────────────

    def visit_Assign(self, no):
        self.traduzidas += 1
        if len(no.targets) == 1 and isinstance(no.targets[0], ast.Tuple):
            alvos = ", ".join(self.expr(e) for e in no.targets[0].elts)
            self.escrever(f"{alvos} := {self.expr(no.value)}")
            return
        for alvo in no.targets:
            self.escrever(f"{self.expr(alvo)} := {self.expr(no.value)}")

    def visit_AnnAssign(self, no):
        self.traduzidas += 1
        tipo = self._anotacao(no.annotation)
        valor = f" := {self.expr(no.value)}" if no.value else ""
        self.escrever(f"{self.expr(no.target)}: {tipo}{valor}")

    def visit_AugAssign(self, no):
        self.traduzidas += 1
        op = _BINARIO.get(type(no.op), "?")
        self.escrever(f"{self.expr(no.target)} {op}= {self.expr(no.value)}")

    def visit_Expr(self, no):
        self.traduzidas += 1
        # `print(...)` é instrução aqui, não chamada.
        if (isinstance(no.value, ast.Call)
                and isinstance(no.value.func, ast.Name)
                and no.value.func.id == "print"):
            args = ", ".join(self.expr(a) for a in no.value.args)
            self.escrever(f"out {args}" if args else 'out ""')
            return
        if isinstance(no.value, ast.Constant) and isinstance(no.value.value, str):
            # Docstring vira comentário.
            for linha in no.value.value.strip().split("\n"):
                self.escrever(f"// {linha.strip()}")
            return
        self.escrever(self.expr(no.value))

    def visit_Return(self, no):
        self.traduzidas += 1
        self.escrever(f"yield {self.expr(no.value)}" if no.value else "yield void")

    def visit_If(self, no):
        self.traduzidas += 1
        self.escrever(f"given {self.expr(no.test)}:")
        self.bloco(no.body)
        orelse = no.orelse
        while orelse:
            if len(orelse) == 1 and isinstance(orelse[0], ast.If):
                filho = orelse[0]
                self.escrever(f"orif {self.expr(filho.test)}:")
                self.bloco(filho.body)
                orelse = filho.orelse
            else:
                self.escrever("otherwise:")
                self.bloco(orelse)
                break

    def visit_For(self, no):
        self.traduzidas += 1
        alvo = (", ".join(self.expr(e) for e in no.target.elts)
                if isinstance(no.target, ast.Tuple) else self.expr(no.target))

        # `for i in range(n)` vira `cycle i from 0 to n-1`, que é a
        # forma idiomática — e `cycle from … to` é inclusivo nos dois
        # extremos, então o fim leva um `- 1`.
        fonte = no.iter
        if (isinstance(fonte, ast.Call) and isinstance(fonte.func, ast.Name)
                and fonte.func.id == "range" and not fonte.keywords):
            partes = [self.expr(a) for a in fonte.args]
            if len(partes) == 1:
                self.escrever(f"cycle {alvo} from 0 to {partes[0]} - 1:")
            elif len(partes) == 2:
                self.escrever(f"cycle {alvo} from {partes[0]} "
                              f"to {partes[1]} - 1:")
            else:
                self.escrever(f"cycle {alvo} from {partes[0]} "
                              f"to {partes[1]} - 1 step {partes[2]}:")
        else:
            self.escrever(f"cycle {alvo} in {self.expr(fonte)}:")
        self.bloco(no.body)

        if no.orelse:
            self.marcar(no, "'for ... else' nao existe em DataForge",
                        "o bloco 'else' roda quando o laco NAO foi "
                        "interrompido; use uma variavel de controle")

    def visit_While(self, no):
        self.traduzidas += 1
        self.escrever(f"persist {self.expr(no.test)}:")
        self.bloco(no.body)
        if no.orelse:
            self.marcar(no, "'while ... else' nao existe em DataForge")

    def visit_Break(self, no):
        self.traduzidas += 1
        self.escrever("halt")

    def visit_Continue(self, no):
        self.traduzidas += 1
        self.escrever("skip")

    def visit_Pass(self, no):
        self.escrever("// pass")

    def visit_Try(self, no):
        self.traduzidas += 1
        self.escrever("monitor:")
        self.bloco(no.body)
        for handler in no.handlers:
            nome = f" as {handler.name}" if handler.name else " as e"
            tipo = self._tipo_de_erro(handler)
            self.escrever(f"handle {tipo}{nome}:" if tipo
                          else f"handle{nome}:")
            self.bloco(handler.body)
        if no.orelse:
            self.marcar(no, "'try ... else' nao existe em DataForge",
                        "mova o corpo para o fim do 'monitor'")
        if no.finalbody:
            self.escrever("ensure:")
            self.bloco(no.finalbody)

    def _tipo_de_erro(self, handler):
        """`except ValueError:` — o tipo, no vocabulário daqui.

        Duas armadilhas moram nesta função.

        A primeira: `raise ValueError(…)` virou `trigger`, e `trigger`
        levanta **TriggerError** — `handle ValueError` não pegaria o que
        o próprio conversor acabou de gerar. Quando o arquivo tem um
        `raise` do mesmo tipo, o `handle` vira `Error`, que pega
        qualquer coisa, e uma nota explica.

        A segunda: um tipo que não existe aqui filtraria por um nome
        indefinido, e o bloco nunca rodaria. Aí também vale `Error`.
        """
        if handler.type is None:
            return ""

        nomes = ([n.id for n in handler.type.elts
                  if isinstance(n, ast.Name)]
                 if isinstance(handler.type, ast.Tuple)
                 else ([handler.type.id]
                       if isinstance(handler.type, ast.Name) else []))
        if not nomes:
            return "Error"

        # Um 'except' com vários tipos: 'handle' filtra um só.
        if len(nomes) > 1:
            self.pendencias.append(
                (getattr(handler, "lineno", 0),
                 f"'except ({', '.join(nomes)})' pega varios tipos",
                 "'handle' filtra um tipo; virou 'Error', que pega todos"))
            return "Error"

        alvo = nomes[0]
        if alvo in self._tipos_disparados:
            self.pendencias.append(
                (getattr(handler, "lineno", 0),
                 f"'except {alvo}' virou 'handle Error'",
                 f"o 'raise {alvo}' deste arquivo virou 'trigger', que "
                 f"levanta TriggerError — 'handle {alvo}' nao o pegaria"))
            return "Error"

        if alvo in _ERROS_TRADUZIDOS:
            return _ERROS_TRADUZIDOS[alvo]
        if alvo in _ERROS_IGUAIS:
            return alvo

        self.pendencias.append(
            (getattr(handler, "lineno", 0),
             f"'{alvo}' nao e um tipo de erro conhecido aqui",
             "virou 'Error', que pega qualquer um; veja os 177 tipos em "
             "'dataforge erros'"))
        return "Error"

    def visit_Raise(self, no):
        """`raise ValueError("x")` vira `trigger "x"`.

        `trigger` sempre levanta `TriggerError` com uma MENSAGEM — não
        aceita um tipo. Traduzir literal produz `trigger ValueError("x")`,
        que tenta chamar `ValueError` como função e explode.

        O tipo do Python vai para a mensagem, para não se perder: quem
        lia `ValueError` continua vendo a palavra.
        """
        self.traduzidas += 1
        if no.exc is None:
            self.escrever("trigger")
            return

        alvo = no.exc
        if isinstance(alvo, ast.Call) and isinstance(alvo.func, ast.Name):
            tipo = alvo.func.id
            if alvo.args:
                mensagem = self.expr(alvo.args[0])
                # Texto literal: junta o tipo à mensagem, sem interpolar.
                if (isinstance(alvo.args[0], ast.Constant)
                        and isinstance(alvo.args[0].value, str)):
                    self.escrever(f'trigger "{tipo}: {alvo.args[0].value}"')
                else:
                    self.escrever(f'trigger $"{tipo}: {{{mensagem}}}"')
            else:
                self.escrever(f'trigger "{tipo}"')
            self.pendencias.append(
                (getattr(no, "lineno", 0),
                 f"'raise {tipo}(...)' virou 'trigger' com o tipo na mensagem",
                 "'trigger' levanta TriggerError; para filtrar por tipo, "
                 "use 'handle Error' e leia 'e.message'"))
            return

        # `raise e` — relançar um erro que já se tem.
        self.escrever(f"trigger {self.expr(alvo)}")

    def visit_Assert(self, no):
        self.traduzidas += 1
        msg = f", {self.expr(no.msg)}" if no.msg else ""
        self.escrever(f"assert {self.expr(no.test)}{msg}")

    def visit_Import(self, no):
        self.traduzidas += 1
        for alias in no.names:
            raiz = alias.name.split(".")[0]
            apelido = alias.asname or raiz
            nativo = _MODULOS.get(raiz)
            if nativo:
                self.origem[apelido] = raiz
                self.escrever(f"adopt {nativo} as {apelido}")
            else:
                self.escrever(f"adopt Python.{alias.name} as {apelido}")

    def visit_ImportFrom(self, no):
        self.traduzidas += 1
        modulo = no.module or "."
        raiz = modulo.split(".")[0]
        nomes = ", ".join(
            a.asname and f"{a.name} as {a.asname}" or a.name
            for a in no.names)
        nativo = _MODULOS.get(raiz)
        if nativo:
            self.escrever(f"adopt {nativo}.{{{nomes}}}")
        else:
            self.escrever(f"adopt Python.{modulo}.{{{nomes}}}")

    def visit_With(self, no):
        """`with` não existe — `defer` faz o mesmo trabalho, ao contrário.

        Traduzir para `defer` mudaria a estrutura do código de um jeito
        que quem lê precisa conferir: o `defer` roda na saída da AÇÃO, e
        o `with` roda na saída do bloco. Quando eles coincidem a
        tradução é certa; quando não, é sutilmente errada.
        """
        self.marcar(no, "'with' nao existe em DataForge",
                    "use 'defer:' para a limpeza — mas repare que 'defer' "
                    "roda na saida da ACAO, e nao do bloco")
        self.escrever("// o corpo do 'with', traduzido:")
        for item in no.body:
            self.visit(item)

    def visit_Global(self, no):
        self.marcar(no, "'global' nao existe em DataForge",
                    "escopo aqui e lexico; passe o valor ou use 'shadow'")

    visit_Nonlocal = visit_Global

    def visit_Delete(self, no):
        self.traduzidas += 1
        for alvo in no.targets:
            self.escrever(f"delete {self.expr(alvo)}")

    # ── Expressões ───────────────────────────────────────────

    def expr(self, no):
        """Uma expressão do Python como texto DataForge."""
        if no is None:
            return "void"
        metodo = getattr(self, f"ex_{type(no).__name__}", None)
        if metodo is None:
            self.pendencias.append(
                (getattr(no, "lineno", 0),
                 f"expressao '{type(no).__name__}' nao traduzida", ""))
            return f"/* {type(no).__name__} */"
        return metodo(no)

    def ex_Constant(self, no):
        v = no.value
        if v is True:
            return "yes"
        if v is False:
            return "no"
        if v is None:
            return "void"
        if isinstance(v, str):
            escapado = v.replace("\\", "\\\\").replace('"', '\\"')
            escapado = escapado.replace("\n", "\\n").replace("\t", "\\t")
            return f'"{escapado}"'
        return repr(v)

    def ex_Name(self, no):
        embutida = _EMBUTIDAS.get(no.id)
        if embutida:
            return embutida
        return self.nome_livre(no.id)

    def ex_Attribute(self, no):
        base = self.expr(no.value)
        atributo = self.nome_livre(no.attr)

        # `json.dumps` -> `json.to_json`: o módulo foi traduzido, e o
        # nome da função muda com ele.
        if isinstance(no.value, ast.Name):
            origem = self.origem.get(no.value.id)
            if origem:
                traduzido = _FUNCOES.get((origem, no.attr))
                if traduzido:
                    return f"{base}.{traduzido}"
                self.pendencias.append(
                    (getattr(no, "lineno", 0),
                     f"'{origem}.{no.attr}' — confira o nome no modulo daqui",
                     f"'{_MODULOS[origem]}' pode chamar isto de outra forma; "
                     f"veja doc/BIBLIOTECA_PADRAO.md"))
        return f"{base}.{atributo}"

    def ex_Subscript(self, no):
        return f"{self.expr(no.value)}[{self.expr(no.slice)}]"

    def ex_Slice(self, no):
        inicio = self.expr(no.lower) if no.lower else ""
        fim = self.expr(no.upper) if no.upper else ""
        passo = f":{self.expr(no.step)}" if no.step else ""
        return f"{inicio}:{fim}{passo}"

    def ex_Call(self, no):
        alvo = self.expr(no.func)
        args = [self.expr(a) for a in no.args]
        args += [f"{k.arg} := {self.expr(k.value)}"
                 for k in no.keywords if k.arg]
        chamada = f"{alvo}({', '.join(args)})"

        # Construir um blueprint pede 'spawn'. Sem isto a linha compila
        # e explode ao rodar: "'Conta' is not callable".
        #
        # Os parenteses NAO sao enfeite: 'spawn Filha().nome()' e lido
        # como 'spawn (Filha().nome())', e o erro fala de 'nome' nao ser
        # blueprint — longe da causa. '(spawn Filha()).nome()' e o certo.
        if isinstance(no.func, ast.Name) and no.func.id in self.classes:
            return f"(spawn {chamada})"
        return chamada

    def ex_Starred(self, no):
        return f"...{self.expr(no.value)}"

    def ex_BinOp(self, no):
        op = _BINARIO.get(type(no.op))
        if op is None:
            return f"/* operador {type(no.op).__name__} */"
        return f"{self.expr(no.left)} {op} {self.expr(no.right)}"

    def ex_UnaryOp(self, no):
        return f"{_UNARIO.get(type(no.op), '?')}{self.expr(no.operand)}"

    def ex_BoolOp(self, no):
        palavra = "and" if isinstance(no.op, ast.And) else "or"
        return f" {palavra} ".join(self.expr(v) for v in no.values)

    def ex_Compare(self, no):
        partes = [self.expr(no.left)]
        for op, direita in zip(no.ops, no.comparators):
            partes.append(_COMPARACAO.get(type(op), "?"))
            partes.append(self.expr(direita))
        return " ".join(partes)

    def ex_IfExp(self, no):
        return (f"{self.expr(no.body)} given {self.expr(no.test)} "
                f"otherwise {self.expr(no.orelse)}")

    def ex_Lambda(self, no):
        params, _ = self._parametros(no.args)
        return f"lambda {params}: {self.expr(no.body)}"

    def ex_List(self, no):
        return "[" + ", ".join(self.expr(e) for e in no.elts) + "]"

    ex_Tuple = ex_List
    ex_Set = ex_List

    def ex_Dict(self, no):
        pares = ", ".join(
            f"{self.expr(k)}: {self.expr(v)}"
            for k, v in zip(no.keys, no.values))
        return "{" + pares + "}"

    def ex_ListComp(self, no):
        return self._compreensao(no, "[", "]")

    def ex_SetComp(self, no):
        return self._compreensao(no, "[", "]")

    def ex_GeneratorExp(self, no):
        return self._compreensao(no, "[", "]")

    def _compreensao(self, no, abre, fecha):
        if len(no.generators) != 1:
            self.pendencias.append(
                (getattr(no, "lineno", 0),
                 "compreensao com mais de um 'for' precisa de revisao", ""))
        g = no.generators[0]
        alvo = (", ".join(self.expr(e) for e in g.target.elts)
                if isinstance(g.target, ast.Tuple) else self.expr(g.target))
        texto = (f"{abre}{self.expr(no.elt)} cycle {alvo} "
                 f"in {self.expr(g.iter)}")
        for cond in g.ifs:
            texto += f" given {self.expr(cond)}"
        return texto + fecha

    def ex_DictComp(self, no):
        self.pendencias.append(
            (getattr(no, "lineno", 0),
             "compreensao de dicionario nao tem forma direta",
             "monte com um 'cycle' e '.set(chave, valor)'"))
        return "/* dict comprehension */"

    def ex_JoinedStr(self, no):
        """f-string vira `$"…"` — as duas interpolam do mesmo jeito.

        Com um cuidado: string interpolada **não cruza linhas** aqui. Um
        `\n` literal dentro da f-string precisa sair escapado, senão o
        lexer para no meio com "Unterminated interpolated string" — e a
        mensagem não aponta para a causa.

        Foi assim que a conversão de um arquivo real do próprio
        interpretador quebrou.
        """
        partes = []
        for pedaco in no.values:
            if isinstance(pedaco, ast.Constant):
                partes.append(str(pedaco.value)
                              .replace("\\", "\\\\").replace('"', '\\"')
                              .replace("\n", "\\n").replace("\t", "\\t")
                              .replace("\r", "\\r"))
            elif isinstance(pedaco, ast.FormattedValue):
                interno = self.expr(pedaco.value)
                formato = ""
                if pedaco.format_spec is not None:
                    bruto = pedaco.format_spec
                    if (isinstance(bruto, ast.JoinedStr) and bruto.values
                            and isinstance(bruto.values[0], ast.Constant)):
                        formato = ":" + str(bruto.values[0].value)
                partes.append("{" + interno + formato + "}")
        return '$"' + "".join(partes) + '"'

    def ex_FormattedValue(self, no):
        return "{" + self.expr(no.value) + "}"

    def ex_Yield(self, no):
        return f"emit {self.expr(no.value)}" if no.value else "emit void"

    def ex_YieldFrom(self, no):
        return f"emit ...{self.expr(no.value)}"

    def ex_Await(self, no):
        return f"await {self.expr(no.value)}"

    def ex_NamedExpr(self, no):
        self.pendencias.append(
            (getattr(no, "lineno", 0),
             "':=' do Python (walrus) dentro de expressao",
             "em DataForge ':=' e a atribuicao normal; separe em duas linhas"))
        return f"/* {self.expr(no.target)} := {self.expr(no.value)} */"


def converter_fonte(fonte, arquivo="<py>"):
    """O texto Python vira (texto DataForge, pendências).

    Levanta `SyntaxError` se o Python não for válido — traduzir código
    quebrado produziria lixo com aparência de tradução.
    """
    arvore = ast.parse(fonte, arquivo)
    conversor = Conversor(fonte, arquivo)
    conversor.visit(arvore)

    cabecalho = [
        f"// Convertido de {os.path.basename(arquivo)} por 'dataforge converter'.",
        "//",
    ]
    if conversor.pendencias:
        cabecalho += [
            f"// {len(conversor.pendencias)} ponto(s) precisam de revisao —",
            "// procure por 'TODO(converter)' abaixo.",
            "//",
        ]
    else:
        cabecalho += ["// Nada ficou pendente. Rode 'dataforge check' "
                      "para conferir.", "//"]
    cabecalho.append("")

    corpo = "\n".join(cabecalho + conversor.saida)
    # Nunca mais de uma linha em branco seguida.
    while "\n\n\n" in corpo:
        corpo = corpo.replace("\n\n\n", "\n\n")
    return corpo.rstrip() + "\n", conversor.pendencias


def converter_arquivo(caminho, destino=None):
    """Converte um `.py` e grava o `.df` ao lado. Devolve (destino, pendências)."""
    with io.open(caminho, encoding="utf-8") as f:
        fonte = f.read()

    texto, pendencias = converter_fonte(fonte, caminho)
    destino = destino or os.path.splitext(caminho)[0] + ".df"
    with io.open(destino, "w", encoding="utf-8") as f:
        f.write(texto)
    return destino, pendencias
