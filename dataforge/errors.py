"""
DataForge Custom Error Types
"""


class Frame:
    """Um quadro da pilha de chamadas do DataForge."""

    __slots__ = ('name', 'line', 'column', 'filename', 'kind')

    def __init__(self, name, line=0, column=0, filename="", kind="action"):
        self.name = name
        self.line = line
        self.column = column
        self.filename = filename
        self.kind = kind

    def __repr__(self):
        return f"<frame {self.name} L{self.line}>"


class DataForgeError(Exception):
    """Erro do DataForge, com tudo o que o relatorio precisa.

    Alem da mensagem, um erro pode carregar:

        nota    contexto que ajuda a entender o que houve
        dica    o que fazer para resolver
        codigo  identificador estavel (DF0042), para procurar na doc
        doc     ancora na documentacao
        span    quantas colunas sublinhar, quando o erro cobre um trecho
        rotulo  o que escrever sob o sublinhado

    A separacao importa: a mensagem diz o que houve, a dica diz o que
    fazer. Misturar as duas produz mensagens longas que ninguem le.
    """

    #: Codigo padrao da classe; cada erro pode sobrepor.
    CODIGO = "DF0000"

    def __init__(self, message: str, line: int = 0, column: int = 0,
                 nota: str = "", dica: str = "", codigo: str = "",
                 doc: str = "", span: int = 0, rotulo: str = ""):
        self.message = message
        self.line = line
        self.column = column
        self.nota = nota
        self.dica = dica
        self.codigo = codigo or self.CODIGO
        self.doc = doc
        self.span = span
        self.rotulo = rotulo
        self.stack = []        # list[Frame], preenchida pelo interpretador
        self.source_line = ""  # texto da linha que falhou
        self.filename = ""
        super().__init__(self.format())

    def format(self):
        loc = ""
        if self.line:
            loc = f" [line {self.line}"
            if self.column:
                loc += f", col {self.column}"
            loc += "]"
        return f"{self.__class__.__name__}{loc}: {self.message}"

    def friendly_name(self):
        """Nome do erro sem o sublinhado interno."""
        return self.__class__.__name__.rstrip('_')

    @staticmethod
    def _curto(caminho):
        """Caminho relativo ao diretório atual, quando isso encurta."""
        import os
        if not caminho or caminho.startswith('<'):
            return caminho or "<stdin>"
        from .caminhos import curto
        relativo = curto(caminho)
        return relativo if len(relativo) < len(caminho) else caminho

    # ── Relatorio ────────────────────────────────────────────

    #: Quantas linhas de contexto mostrar antes e depois da que falhou.
    CONTEXTO = 2

    def render(self, color=True, source_lines=None, debug=False):
        """Relatorio completo do erro.

            erro[DF0201]: a chave 'b' nao existe neste vault
              ┌─ exemplo.df:2:5
              │
            1 │ v := {"a": 1}
            2 │ out v["b"]
              │     ^^^^^^ esta leitura falhou
              │
              = nota: o vault tem 1 chave: "a"
              = dica: use v["b"] ?? padrao, ou v.has("b") antes de ler
              = doc:  https://dataforge-lang.vercel.app/docs/colecoes
        """
        def tinta(texto, codigo):
            return f"\033[{codigo}m{texto}\033[0m" if color else texto

        VERMELHO, AZUL, CIANO = '1;31', '1;34', '1;36'
        AMARELO, APAGADO = '1;33', '0;90'

        linhas = []
        local = self._curto(self.filename)

        # ── Cabecalho ──
        titulo = tinta(f"erro[{self.codigo}]", VERMELHO)
        primeira, *resto_msg = self.message.split("\n")
        linhas.append(f"{titulo}: {tinta(primeira, '1;37')}")

        # ── Onde ──
        larg = len(str(self.line + self.CONTEXTO)) if self.line else 1
        margem = " " * larg
        seta = tinta("┌─", AZUL)
        linhas.append(f"{margem} {seta} {local}:{self.line}:{self.column}")

        # ── Trecho do codigo, com contexto ──
        if source_lines and 0 < self.line <= len(source_lines):
            barra = tinta("│", AZUL)
            linhas.append(f"{margem} {barra}")

            inicio = max(1, self.line - self.CONTEXTO)
            fim = min(len(source_lines), self.line + self.CONTEXTO)

            for n in range(inicio, fim + 1):
                texto = source_lines[n - 1].rstrip("\n").rstrip()
                numero = str(n).rjust(larg)
                if n == self.line:
                    linhas.append(
                        f"{tinta(numero, VERMELHO)} {barra} {texto}")
                    if self.column:
                        largura = max(1, self.span or 1)
                        marca = ' ' * (self.column - 1) + '^' * largura
                        rotulo = f" {self.rotulo}" if self.rotulo else ""
                        linhas.append(
                            f"{margem} {barra} "
                            f"{tinta(marca + rotulo, VERMELHO)}")
                else:
                    linhas.append(
                        f"{tinta(numero, APAGADO)} {barra} "
                        f"{tinta(texto, APAGADO)}")

            linhas.append(f"{margem} {barra}")

        # ── Linhas extras da mensagem ──
        for linha in resto_msg:
            if linha.strip():
                linhas.append(f"{margem} {tinta('=', AZUL)} {linha.strip()}")

        # ── Nota, dica e doc ──
        if self.nota:
            for i, parte in enumerate(self.nota.split("\n")):
                marcador = tinta("nota:", CIANO) if i == 0 else "     "
                linhas.append(f"{margem} {tinta('=', AZUL)} {marcador} {parte}")
        if self.dica:
            for i, parte in enumerate(self.dica.split("\n")):
                marcador = tinta("dica:", AMARELO) if i == 0 else "     "
                linhas.append(f"{margem} {tinta('=', AZUL)} {marcador} {parte}")
        if self.doc:
            url = self.doc if self.doc.startswith("http") else (
                f"https://dataforge-lang.vercel.app/docs/{self.doc.lstrip('/')}")
            linhas.append(
                f"{margem} {tinta('=', AZUL)} {tinta('doc: ', APAGADO)}"
                f"{tinta(url, APAGADO)}")

        # ── Pilha de chamadas ──
        if self.stack:
            linhas.append("")
            linhas.append(tinta("  pilha de chamadas (mais recente primeiro):",
                                CIANO))
            for quadro in reversed(self.stack):
                arquivo = self._curto(quadro.filename) if quadro.filename else local
                linhas.append(
                    f"    em {tinta(quadro.name, '1;37'):<30} "
                    f"{tinta(f'{arquivo}:{quadro.line}', APAGADO)}")

        return "\n".join(linhas)


# ═══════════════════════════════════════════════════════════
#  As classes de erro
# ═══════════════════════════════════════════════════════════
#
# Elas nao sao escritas a mao: nascem da tabela em
# 'catalogo_erros.py', a mesma de onde sai o texto de
# 'dataforge explain'. Escrever as duas listas separadamente
# garantia divergencia — um erro com classe e sem explicacao, ou
# com explicacao sob o codigo errado.
#
# O que se ganha alem de nao divergir: a hierarquia fica
# declarada num lugar so, e e ela que 'handle' usa para decidir o
# que captura. 'handle RuntimeError' pega DivisionByZeroError
# porque a tabela diz que uma deriva da outra.

def _construir_classes():
    """Cria uma classe por entrada do catalogo, respeitando a heranca.

    Percorre em rodadas: numa passada so, uma classe cuja mae ainda
    nao existe ficaria de fora. Poucas rodadas bastam — a hierarquia
    tem tres niveis.
    """
    from .catalogo_erros import ERROS

    criadas = {"DataForgeError": DataForgeError}
    pendentes = [e for e in ERROS if e["classe"]]

    while pendentes:
        avancou = False
        restantes = []
        for entrada in pendentes:
            mae = criadas.get(entrada["pai"])
            if mae is None:
                restantes.append(entrada)
                continue
            classe = type(entrada["classe"], (mae,), {
                "CODIGO": entrada["codigo"],
                "__doc__": entrada["titulo"],
                "__module__": __name__,
            })
            criadas[entrada["classe"]] = classe
            avancou = True
        if not avancou:
            faltando = ", ".join(f'{e["classe"]}<-{e["pai"]}' for e in restantes)
            raise RuntimeError(f"catalogo de erros com mae inexistente: {faltando}")
        pendentes = restantes

    return criadas


ERROS_POR_NOME = _construir_classes()
globals().update(ERROS_POR_NOME)

#: Todo nome de erro que 'handle' aceita, incluindo a forma sem
#: sublinhado ('TypeError' para a classe 'TypeError_'). O sublinhado
#: existe so para nao colidir com o builtin do Python; quem escreve
#: DataForge nunca o ve.
ALIAS_DE_ERRO = {}
for _nome, _classe in ERROS_POR_NOME.items():
    ALIAS_DE_ERRO[_nome] = _classe
    if _nome.endswith("_"):
        ALIAS_DE_ERRO[_nome[:-1]] = _classe
del _nome, _classe


def erro_por_nome(nome):
    """A classe de erro com este nome, ou None.

    Aceita 'TypeError' e 'TypeError_' indistintamente.
    """
    return ALIAS_DE_ERRO.get(nome)


def nomes_de_erro():
    """Todo nome capturavel por 'handle', em ordem."""
    return sorted(ALIAS_DE_ERRO)


class ControlSignal(BaseException):
    """Base for internal control-flow signals.

    Derives from BaseException (not Exception) on purpose: 'halt', 'skip' and
    'yield' are control flow, not errors, so a 'monitor/handle' block must never
    swallow them.
    """
    pass


class HaltSignal(ControlSignal):
    """Internal signal for 'halt' (break)."""
    pass


class SkipSignal(ControlSignal):
    """Internal signal for 'skip' (continue)."""
    pass


class YieldSignal(ControlSignal):
    """Internal signal for 'yield' (return)."""

    def __init__(self, value=None):
        self.value = value
        super().__init__()


class ChamadaDeCauda(ControlSignal):
    """'yield f(...)' onde 'f' e a propria acao — um salto, nao uma chamada.

    'yield' devolve e encerra. Se o que ele devolve e uma chamada a
    propria acao, nada mais acontece depois dela: o quadro atual so
    existe para repassar o resultado. Reusa-lo em vez de empilhar outro
    e o que permite recursao de acumulador sobre dado de qualquer
    tamanho, em vez de morrer no limite de mil.

    Deriva de 'ControlSignal', como 'yield' e 'halt': e desvio de fluxo,
    e 'monitor' nao pode engoli-lo.
    """

    #: Os campos NAO se chamam 'args'.
    #:
    #: 'BaseException' ja tem um 'args', e 'super().__init__()' o zera —
    #: os argumentos do salto sumiam entre uma volta e a seguinte, e o
    #: parametro chegava 'void' na segunda. O erro aparecia longe da
    #: causa: "unsupported operand for -: 'NoneType' and 'int'".
    def __init__(self, argumentos=None, nomeados=None):
        self.argumentos = argumentos if argumentos is not None else []
        self.nomeados = nomeados if nomeados is not None else {}
        super().__init__()
