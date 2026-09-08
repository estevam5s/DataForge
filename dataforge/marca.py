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


def marca(compacta: bool = False, codigo_cor: str = "1;31") -> str:
    """A pantera pronta para imprimir.

    Num terminal estreito a arte não cabe e ficaria picotada, então a
    versão compacta entra sozinha — um logo quebrado é pior que nenhum.
    """
    if compacta or largura_terminal() < 52:
        return cor(PANTERA_MINIMA, codigo_cor)

    linhas = [l for l in PANTERA.split("\n") if l.strip()]
    return "\n".join(cor("  " + l, codigo_cor) for l in linhas)


def cabecalho(subtitulo: str = "", versao: str = "") -> str:
    """A marca com o nome e a versão ao lado, para abrir um comando."""
    from dataforge import __version__

    partes = [marca(), ""]
    nome = cor("DataForge", "1;37")
    v = cor(f"v{versao or __version__}", "0;90")
    partes.append(f"  {nome} {v}")
    if subtitulo:
        partes.append("  " + cor(subtitulo, "0;90"))
    partes.append("")
    return "\n".join(partes)
