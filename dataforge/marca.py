"""
A marca do DataForge no terminal.

A arte veio de logo.png por `tools/vetorizar_logo.py --ascii`: cada
caractere é um bloco de pixels da pantera, com a proporção corrigida
(um caractere de terminal é cerca de duas vezes mais alto que largo).

Usar isto em vez do nome escrito é o que faz a CLI parecer a mesma
coisa que o site — a marca é a mesma, em outro meio.
"""

import os
import shutil
import sys

#: A pantera, em 40 colunas. Gerada de logo.png; não edite à mão.
PANTERA = r"""
                   ████████
                 █  ████  ██████
            ████████████████████████
         ███████████████████████   ██
      ██████████████ ██████████████████
    ███████████████  ██████████ ████████
  █████████    █████  ████████ █    ██
 ████████████████  ██      █████
████████████████████ ███      ████
██          ██████████████    ███
█             ██████████ ███
               █████████   █
               ██████████
      ███     ██████ ███  █████
      ████████████   ██  ██████████
                    █   █████████████
                            █████ █
                              ███
"""

#: Uma versão de uma linha, para caber num prompt ou num cabeçalho.
PANTERA_MINIMA = "▟█▛"


def _cores_ligadas() -> bool:
    """Cor faz sentido aqui?

    NO_COLOR é o padrão de fato para desligar; saída redirecionada não
    deve receber código de escape, senão o log vira lixo.
    """
    if os.environ.get("NO_COLOR") or "--no-color" in sys.argv:
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


def cor(texto: str, codigo: str) -> str:
    if not _cores_ligadas():
        return texto
    return f"\033[{codigo}m{texto}\033[0m"


def largura_terminal(padrao: int = 80) -> int:
    try:
        return shutil.get_terminal_size((padrao, 24)).columns
    except OSError:
        return padrao


#: O amarelo da marca em 256 cores. O terminal nao entende hex, e o
#: amarelo padrao do ANSI (33) e mostarda em quase todo tema — 220 e o
#: que mais se aproxima do #FED403 do logo.
AMARELO = "38;5;220"


def marca(compacta: bool = False, codigo_cor: str = AMARELO) -> str:
    """A pantera pronta para imprimir.

    Num terminal estreito a arte não cabe e ficaria picotada, então a
    versão compacta entra sozinha — um logo quebrado é pior que nenhum.
    """
    if compacta or largura_terminal() < 52:
        return cor(PANTERA_MINIMA, codigo_cor)

    linhas = [l for l in PANTERA.split("\n") if l.strip()]
    return "\n".join(cor("  " + l, codigo_cor) for l in linhas)


def suporta_cor_verdadeira() -> bool:
    """O terminal aceita 24 bits?

    Quase todo terminal moderno aceita, e ai a marca sai no tom exato
    do logo em vez do mais proximo da paleta de 256.
    """
    return os.environ.get("COLORTERM", "") in ("truecolor", "24bit")


def marca_colorida(compacta: bool = False) -> str:
    """A marca no amarelo exato do logo, quando o terminal permite."""
    codigo = "38;2;254;212;3" if suporta_cor_verdadeira() else AMARELO
    return marca(compacta, codigo)


def cabecalho(subtitulo: str = "", versao: str = "") -> str:
    """A marca com o nome e a versão ao lado, para abrir um comando."""
    from dataforge import __version__

    partes = [marca_colorida(), ""]
    nome = cor("DataForge", "1;37")
    v = cor(f"v{versao or __version__}", "0;90")
    partes.append(f"  {nome} {v}")
    if subtitulo:
        partes.append("  " + cor(subtitulo, "0;90"))
    partes.append("")
    return "\n".join(partes)


# ── A saída sobrevive a um terminal que não fala UTF-8 ──────────

#: O desenho da CLI reescrito em ASCII.
#:
#: Só entra em uso quando o destino não aceita o original. A tradução é
#: por aparência, não por significado: o que importa é que uma tabela
#: continue parecendo uma tabela.
_ASCII = {
    "─": "-", "━": "-", "═": "=", "│": "|", "┃": "|", "║": "|",
    "┌": "+", "┐": "+", "└": "+", "┘": "+", "├": "+", "┤": "+",
    "┬": "+", "┴": "+", "┼": "+", "╭": "+", "╮": "+", "╰": "+",
    "╯": "+", "╔": "+", "╗": "+", "╚": "+", "╝": "+", "╠": "+",
    "╣": "+", "╦": "+", "╩": "+", "╬": "+",
    "█": "#", "▉": "#", "▊": "#", "▋": "#", "▌": "#", "▍": "#",
    "▎": "#", "▏": "#", "▀": "#", "▄": "#", "▟": "#", "▛": "#",
    "▙": "#", "▜": "#", "░": ".", "▒": ":", "▓": "#", "■": "#",
    "□": "-", "▪": "*", "▸": ">", "▾": "v", "▲": "^", "▼": "v",
    "✓": "v", "✔": "v", "✗": "x", "✘": "x", "✅": "ok", "❌": "x",
    "→": "->", "←": "<-", "↑": "^", "↓": "v", "⇒": "=>", "↳": "->",
    "●": "*", "○": "o", "•": "*", "◆": "*", "◦": "-", "·": ".",
    "⚡": "!", "⚠": "!", "★": "*", "☆": "*", "✦": "*", "❯": ">",
    "…": "...", "—": "-", "–": "-", "‑": "-",
    "“": '"', "”": '"', "„": '"', "‘": "'", "’": "'",
    "×": "x", "÷": "/", "≥": ">=", "≤": "<=", "≠": "!=", "≈": "~",
}

#: A amostra que decide se o destino serve.
#:
#: Não adianta perguntar o nome da codificação: 'cp1252', 'cp850' e
#: 'ascii' falham por motivos diferentes e a lista nunca fica completa.
#: Pergunta-se ao codec, com os caracteres que a CLI realmente usa.
_AMOSTRA = "─═│█✓✗→●…"


class _Transliterada:
    """Um fluxo de texto que troca o que o destino não sabe escrever.

    Existe porque no Windows a saída redirecionada para um cano não é
    UTF-8: o Python escolhe a codificação do sistema, que é 'cp1252', e
    ela não tem uma única das linhas que desenham as tabelas da CLI.
    'dataforge help', 'check', 'lint', 'stats' e 'run --time' morriam
    com um UnicodeEncodeError cru — não porque o comando falhou, mas
    porque o traço que separa o cabeçalho não cabia no cano.

    Traduzir é melhor que 'errors="replace"': o segundo devolve uma
    fileira de '?' onde havia uma tabela, e melhor que
    'errors="backslashreplace"', que devolve '\\u2500' e é pior de ler
    que o desenho que substitui.
    """

    __slots__ = ("_destino", "_tabela")

    def __init__(self, destino, tabela):
        self._destino = destino
        self._tabela = tabela

    def write(self, texto):
        if isinstance(texto, str):
            texto = texto.translate(self._tabela)
        return self._destino.write(texto)

    def writelines(self, linhas):
        for linha in linhas:
            self.write(linha)

    def __getattr__(self, nome):
        # 'isatty', 'flush', 'encoding', 'fileno', 'buffer' — tudo o
        # que o resto do programa pergunta continua vindo do original.
        return getattr(self._destino, nome)


def _cabe(fluxo) -> bool:
    """O fluxo consegue escrever a amostra?"""
    codificacao = getattr(fluxo, "encoding", None)
    if not codificacao:
        # Sem codificação declarada é um fluxo de bytes ou um substituto
        # de teste; nesse caso não há o que consertar.
        return True
    try:
        _AMOSTRA.encode(codificacao)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def preparar_saida() -> None:
    """Garante que a CLI consiga imprimir o que desenha.

    Duas tentativas, nesta ordem, porque só a segunda perde informação:

    1. Pedir UTF-8 ao fluxo. É o certo para um cano, e o console do
       Windows moderno também aceita.
    2. Não sendo possível, traduzir o desenho para ASCII na saída.

    Chamada uma vez, no começo de 'main'. Em UTF-8 — Linux, macOS, e o
    Windows com o cano já reconfigurado — nada disso acontece e não há
    custo nenhum depois.
    """
    tabela = None
    for nome in ("stdout", "stderr"):
        fluxo = getattr(sys, nome, None)
        if fluxo is None or _cabe(fluxo):
            continue

        reconfigurar = getattr(fluxo, "reconfigure", None)
        if reconfigurar is not None:
            try:
                reconfigurar(encoding="utf-8")
            except (ValueError, OSError, AttributeError):
                pass
            else:
                if _cabe(fluxo):
                    continue

        if tabela is None:
            tabela = str.maketrans(_ASCII)
        setattr(sys, nome, _Transliterada(fluxo, tabela))
