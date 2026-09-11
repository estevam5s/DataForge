"""O ponto de entrada do executável empacotado.

Um arquivo só, e trivial, de propósito: o PyInstaller precisa de um
*script*, e apontá-lo para `dataforge/cli.py` faria o módulo ser
carregado como `__main__` — com isso `from .marca import ...` quebra,
porque um script não tem pacote. Este arquivo importa pelo nome
completo, que é como o resto do programa espera ser importado.
"""

from dataforge.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
