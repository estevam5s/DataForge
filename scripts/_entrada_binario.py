"""O ponto de entrada do executável empacotado.

Um arquivo só, e trivial, de propósito: o PyInstaller precisa de um
*script*, e apontá-lo para `dataforge/cli.py` faria o módulo ser
carregado como `__main__` — com isso `from .marca import ...` quebra,
porque um script não tem pacote. Este arquivo importa pelo nome
completo, que é como o resto do programa espera ser importado.
"""

import multiprocessing

from dataforge.cli import main

if __name__ == "__main__":
    # Num executavel congelado, o filho de um 'spawn' RE-EXECUTA o
    # proprio .exe: sem 'freeze_support' ele reentra na CLI e o
    # programa roda de novo dentro de cada trabalhador, em vez de
    # executar a tarefa. E a primeira linha por exigencia do
    # multiprocessing — depois dela ja seria tarde.
    #
    # 'map_processos' usa spawn nos tres sistemas desde que o fork do
    # Linux passou a entregar ao filho uma conexao SQLite herdada por
    # memoria; foi a correcao que trouxe esta exigencia junto.
    multiprocessing.freeze_support()
    raise SystemExit(main())
