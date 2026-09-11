"""Caminhos como eles aparecem para quem lê a mensagem.

Existe por um motivo só, e ele é específico: no Windows,
`os.path.relpath` **levanta** quando os dois caminhos estão em unidades
diferentes — não há caminho relativo de `D:\\tmp\\app.df` para `C:\\`,
e a biblioteca diz isso com um `ValueError`.

Quase todo uso de `relpath` aqui está dentro da construção de uma
mensagem, para encurtar um caminho longo. Quando ele levanta ali, o erro
que o usuário recebe não é o dele: é um `ValueError` sobre montagem de
disco, no lugar de "não achei o módulo". Foi exatamente o que aconteceu
com `adopt ./lib/naoexiste` num projeto fora da unidade do sistema.

Encurtar é um enfeite. Falhar em encurtar não pode custar a mensagem.
"""

import os


def curto(caminho: str, base: str = None) -> str:
    """O caminho relativo quando faz sentido; o original quando não faz.

    Também recusa o relativo quando ele fica mais longo que o absoluto —
    `../../../../outro/lugar/arquivo.df` não ajuda ninguém a se
    localizar, e o caminho inteiro ajuda.
    """
    if not caminho:
        return caminho
    try:
        relativo = os.path.relpath(caminho, base) if base \
            else os.path.relpath(caminho)
    except (ValueError, OSError):
        # Unidades diferentes no Windows, ou um caminho que o sistema
        # nao consegue resolver.
        return caminho
    return relativo if len(relativo) <= len(caminho) else caminho
