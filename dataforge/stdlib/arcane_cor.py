"""
Arcane.Color — cor e formatacao no terminal.

    adopt Arcane.Color as C

    out C.red("falhou")
    out C.bold(C.green("ok"))
    out C.rgb("gradiente", 255, 100, 0)
    out C.table([["nome", "idade"], ["Ana", 30]])

─── Quando NAO colorir ─────────────────────────────────────

Cor num arquivo de log e lixo: os codigos de escape viram '\\x1b[31m' no
meio do texto, e quem le depois nao entende. Este modulo detecta:

  - saida redirecionada para arquivo ou cano
  - a variavel NO_COLOR, que e o padrao combinado entre ferramentas
  - TERM=dumb

e desliga a cor sozinho. 'C.force(yes)' liga de volta para quem
realmente quer, e 'C.strip' tira as cores de um texto que ja as tem.

Sem dependencia: os codigos ANSI sao os mesmos desde os anos 70, e
cabem numa tabela.
"""

import os
import re
import sys


#: Os 16 basicos. O primeiro numero e a cor da frente, o segundo do fundo.
BASICAS = {
    "black": 30, "red": 31, "green": 32, "yellow": 33,
    "blue": 34, "magenta": 35, "cyan": 36, "white": 37,
    "gray": 90, "grey": 90,
    "bright_red": 91, "bright_green": 92, "bright_yellow": 93,
    "bright_blue": 94, "bright_magenta": 95, "bright_cyan": 96,
    "bright_white": 97,
}

#: Estilos. 'blink' esta aqui por completude, e nao porque alguem deva usar.
ESTILOS = {
    "bold": 1, "dim": 2, "italic": 3, "underline": 4,
    "blink": 5, "reverse": 7, "hidden": 8, "strike": 9,
}

RESET = "\033[0m"

#: Tira os codigos de escape de um texto.
_ESCAPES = re.compile(r"\033\[[0-9;]*m")


class _Estado:
    """Ligado ou desligado, e o motivo — para 'C.info()' poder dizer."""

    __slots__ = ("forcado", "motivo")

    def __init__(self):
        self.forcado = None
        self.motivo = ""


_ESTADO = _Estado()


def _suporta_cor():
    """A saida aceita cor?

    A ordem das checagens importa: NO_COLOR vence tudo, porque e uma
    escolha explicita de quem roda. FORCE_COLOR vem depois, para o CI
    conseguir cor mesmo com a saida redirecionada.
    """
    if _ESTADO.forcado is not None:
        _ESTADO.motivo = "forcado por C.force()"
        return _ESTADO.forcado

    if os.environ.get("NO_COLOR") is not None:
        _ESTADO.motivo = "NO_COLOR esta definida"
        return False
    if os.environ.get("FORCE_COLOR"):
        _ESTADO.motivo = "FORCE_COLOR esta definida"
        return True
    if os.environ.get("TERM") == "dumb":
        _ESTADO.motivo = "TERM=dumb"
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        _ESTADO.motivo = "a saida nao e um terminal"
        return False
    _ESTADO.motivo = "terminal interativo"
    return True


def _pintar(texto, *codigos):
    if not codigos or not _suporta_cor():
        return str(texto)
    prefixo = "".join(f"\033[{c}m" for c in codigos)
    # Reset ANTES do proximo, e nao so no fim: sem isso, texto colorido
    # dentro de texto colorido perde a cor de fora ao terminar o de
    # dentro.
    corpo = str(texto).replace(RESET, RESET + prefixo)
    return f"{prefixo}{corpo}{RESET}"


class ArcaneColor(dict):
    """Cor, estilo e desenho no terminal."""

    def __new__(cls):
        modulo = {
            # ── controle ──
            "supports": lambda: _suporta_cor(),
            "force": cls._force,
            "auto": cls._auto,
            "strip": cls._strip,
            "info": cls._info,
            "width": cls._width,

            # ── composicao ──
            "paint": cls._paint,
            "rgb": cls._rgb,
            "bg_rgb": cls._bg_rgb,
            "hex": cls._hex,
            "gradient": cls._gradient,
            "rainbow": cls._rainbow,

            # ── desenho ──
            "table": cls._table,
            "box": cls._box,
            "rule": cls._rule,
            "bar": cls._bar,
            "spinner_frames": cls._spinner_frames,
            "badge": cls._badge,
            "tree": cls._tree,

            # ── semantico ──
            "success": cls._success,
            "error": cls._error,
            "warning": cls._warning,
            "info_msg": cls._info_msg,
            "muted": cls._muted,
        }
        # Uma acao por cor e por estilo, geradas da tabela: escrever 25
        # metodos identicos a mao seria 25 chances de errar um numero.
        for nome, codigo in BASICAS.items():
            modulo[nome] = cls._fazer_cor(codigo)
            modulo[f"on_{nome}"] = cls._fazer_cor(codigo + 10)
        for nome, codigo in ESTILOS.items():
            modulo[nome] = cls._fazer_cor(codigo)
        return modulo

    @staticmethod
    def _fazer_cor(codigo):
        return lambda texto: _pintar(texto, codigo)

    # ── controle ────────────────────────────────────────────

    @staticmethod
    def _force(ligado=True):
        _ESTADO.forcado = bool(ligado)
        return _ESTADO.forcado

    @staticmethod
    def _auto():
        """Volta a decidir sozinho."""
        _ESTADO.forcado = None
        return True

    @staticmethod
    def _strip(texto):
        """Tira as cores. Para gravar em arquivo o que foi colorido."""
        return _ESCAPES.sub("", str(texto))

    @staticmethod
    def _info():
        ligado = _suporta_cor()
        return {"colorido": ligado, "motivo": _ESTADO.motivo,
                "largura": ArcaneColor._width()}

    @staticmethod
    def _width(padrao=80):
        """A largura do terminal, ou o padrao quando nao da para saber."""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return padrao

    # ── composicao ──────────────────────────────────────────

    @staticmethod
    def _paint(texto, *nomes):
        """Aplica varias cores e estilos de uma vez: paint(t, "red", "bold")."""
        codigos = []
        for nome in nomes:
            if nome in BASICAS:
                codigos.append(BASICAS[nome])
            elif nome in ESTILOS:
                codigos.append(ESTILOS[nome])
            elif nome.startswith("on_") and nome[3:] in BASICAS:
                codigos.append(BASICAS[nome[3:]] + 10)
        return _pintar(texto, *codigos)

    @staticmethod
    def _rgb(texto, r, g, b):
        """Cor exata, em 24 bits. Quase todo terminal atual aceita."""
        return _pintar(texto, f"38;2;{int(r)};{int(g)};{int(b)}")

    @staticmethod
    def _bg_rgb(texto, r, g, b):
        return _pintar(texto, f"48;2;{int(r)};{int(g)};{int(b)}")

    @staticmethod
    def _hex(texto, cor):
        """Cor por codigo hexadecimal: hex(t, "#FED403")."""
        c = str(cor).lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        if len(c) != 6:
            from ...errors import FormatError
            raise FormatError(
                f"'{cor}' is not a hex color.",
                dica="use  #RGB  or  #RRGGBB", doc="tecnicas/editor")
        return ArcaneColor._rgb(texto, int(c[0:2], 16), int(c[2:4], 16),
                                int(c[4:6], 16))

    @staticmethod
    def _gradient(texto, de, para):
        """Cada letra num ponto entre as duas cores."""
        def ler(c):
            c = str(c).lstrip("#")
            if len(c) == 3:
                c = "".join(ch * 2 for ch in c)
            return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

        r1, g1, b1 = ler(de)
        r2, g2, b2 = ler(para)
        letras = str(texto)
        n = max(len(letras) - 1, 1)
        return "".join(
            ArcaneColor._rgb(ch,
                             r1 + (r2 - r1) * i / n,
                             g1 + (g2 - g1) * i / n,
                             b1 + (b2 - b1) * i / n)
            for i, ch in enumerate(letras))

    @staticmethod
    def _rainbow(texto):
        cores = [196, 208, 226, 46, 21, 93]
        return "".join(_pintar(ch, f"38;5;{cores[i % len(cores)]}")
                       for i, ch in enumerate(str(texto)))

    # ── desenho ─────────────────────────────────────────────

    @staticmethod
    def _table(linhas, cabecalho=True, cor="cyan"):
        """Uma tabela alinhada, com a largura de cada coluna medida.

        A largura sai do texto SEM as cores: contar os codigos de escape
        desalinharia tudo o que fosse colorido.
        """
        if not linhas:
            return ""
        dados = [[str(c) for c in linha] for linha in linhas]
        n = max(len(l) for l in dados)
        dados = [l + [""] * (n - len(l)) for l in dados]

        larguras = [
            max(len(ArcaneColor._strip(l[i])) for l in dados)
            for i in range(n)
        ]

        def formatar(linha, pintar=False):
            partes = []
            for i, celula in enumerate(linha):
                visivel = len(ArcaneColor._strip(celula))
                enchimento = " " * (larguras[i] - visivel)
                texto = celula + enchimento
                partes.append(ArcaneColor._paint(texto, cor, "bold")
                              if pintar else texto)
            return "  " + "  ".join(partes)

        saida = []
        if cabecalho:
            saida.append(formatar(dados[0], pintar=True))
            saida.append("  " + "  ".join("─" * w for w in larguras))
            dados = dados[1:]
        saida.extend(formatar(l) for l in dados)
        return "\n".join(saida)

    @staticmethod
    def _box(texto, titulo="", cor="cyan", largura=0):
        """Uma moldura em volta do texto."""
        linhas = str(texto).split("\n")
        interna = largura or max(
            [len(ArcaneColor._strip(l)) for l in linhas] +
            [len(titulo) + 2])
        pintar = lambda t: ArcaneColor._paint(t, cor)

        topo = pintar(f"┌─{titulo}" + "─" * (interna - len(titulo)) + "─┐") \
            if titulo else pintar("┌" + "─" * (interna + 2) + "┐")
        saida = [topo]
        for l in linhas:
            visivel = len(ArcaneColor._strip(l))
            saida.append(f"{pintar('│')} {l}{' ' * (interna - visivel)} "
                         f"{pintar('│')}")
        saida.append(pintar("└" + "─" * (interna + 2) + "┘"))
        return "\n".join(saida)

    @staticmethod
    def _rule(titulo="", cor="gray", largura=0):
        """Uma linha horizontal, com titulo opcional no meio."""
        w = largura or ArcaneColor._width()
        if not titulo:
            return ArcaneColor._paint("─" * w, cor)
        rotulo = f" {titulo} "
        sobra = max(w - len(rotulo), 2)
        esquerda = sobra // 2
        return (ArcaneColor._paint("─" * esquerda, cor) + rotulo +
                ArcaneColor._paint("─" * (sobra - esquerda), cor))

    @staticmethod
    def _bar(valor, total, largura=30, cor="green", mostrar_numero=True):
        """Uma barra de progresso."""
        if total <= 0:
            fracao = 0.0
        else:
            fracao = max(0.0, min(1.0, valor / total))
        cheias = int(fracao * largura)
        barra = (ArcaneColor._paint("█" * cheias, cor) +
                 ArcaneColor._paint("░" * (largura - cheias), "gray"))
        if not mostrar_numero:
            return barra
        return f"{barra} {ArcaneColor._paint(f'{fracao*100:.0f}%', 'bold')}"

    @staticmethod
    def _spinner_frames(estilo="pontos"):
        """Os quadros de um girador, para animar em laco."""
        return {
            "pontos": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "linha": ["|", "/", "-", "\\"],
            "barra": ["▁", "▃", "▄", "▅", "▆", "▇", "▆", "▅", "▄", "▃"],
            "circulo": ["◐", "◓", "◑", "◒"],
            "seta": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        }.get(estilo, ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])

    @staticmethod
    def _badge(texto, cor="blue"):
        """Um rotulo com fundo colorido."""
        return ArcaneColor._paint(f" {texto} ", f"on_{cor}", "bold", "white")

    @staticmethod
    def _tree(no, prefixo="", ultimo=True):
        """Desenha uma arvore a partir de um vault aninhado.

            {"raiz": {"a": {}, "b": {"c": {}}}}
        """
        saida = []
        itens = list(no.items()) if isinstance(no, dict) else []
        for i, (nome, filhos) in enumerate(itens):
            e_ultimo = i == len(itens) - 1
            galho = "└── " if e_ultimo else "├── "
            saida.append(prefixo + ArcaneColor._paint(galho, "gray") + str(nome))
            if isinstance(filhos, dict) and filhos:
                seguinte = prefixo + ("    " if e_ultimo else
                                      ArcaneColor._paint("│   ", "gray"))
                saida.append(ArcaneColor._tree(filhos, seguinte, e_ultimo))
        return "\n".join(l for l in saida if l)

    # ── semantico ───────────────────────────────────────────
    #
    # O simbolo vem junto da cor de proposito: quem nao distingue verde
    # de vermelho — 8% dos homens — depende dele para ler a saida.

    @staticmethod
    def _success(texto):
        return ArcaneColor._paint("✓ ", "green", "bold") + str(texto)

    @staticmethod
    def _error(texto):
        return ArcaneColor._paint("✗ ", "red", "bold") + str(texto)

    @staticmethod
    def _warning(texto):
        return ArcaneColor._paint("! ", "yellow", "bold") + str(texto)

    @staticmethod
    def _info_msg(texto):
        return ArcaneColor._paint("→ ", "cyan", "bold") + str(texto)

    @staticmethod
    def _muted(texto):
        return ArcaneColor._paint(texto, "gray")
