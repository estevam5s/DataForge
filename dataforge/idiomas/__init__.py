# -*- coding: utf-8 -*-
"""Os catalogos de traducao, um por arquivo.

A camada de idioma nasceu binaria — 'pt' ou 'en' — e binaria ela nao
tinha como receber uma traducao de fora: quem quisesse espanhol teria
de editar o nucleo, e uma traducao que exige um pull request na
linguagem nao acontece.

Cada modulo daqui expoe 'INTEIRAS' e 'PEDACOS'. O nome do arquivo e o
codigo do idioma ('pt.py' -> 'pt'), e 'DF_IDIOMA_CAMINHO' aponta uma
pasta com catalogos de FORA, que entram no registro pelo mesmo caminho.

Tres decisoes:

1. **Um catalogo quebrado nao derruba nada.** Ele e ignorado, e o
   motivo fica guardado para o 'dataforge idioma' mostrar. Um erro de
   sintaxe num arquivo de traducao nao pode impedir um programa de
   rodar: a traducao e conforto, e o ingles e o piso.

2. **O ingles NAO e um catalogo.** Ele e o texto como nasce, e por isso
   nao ha 'en.py': ter um seria manter uma copia identidade de 115
   entradas, que divergiria na primeira mensagem nova.

3. **A descoberta e por arquivo, e nao por uma lista.** Uma lista
   escrita aqui envelheceria no primeiro idioma novo — e a falta nao
   daria erro, so faria a traducao nao aparecer.
"""

import glob
import os

#: O ingles e o original, e nao uma traducao.
ORIGINAL = "en"

#: A pasta de fora, quando existe.
VARIAVEL_DE_CAMINHO = "DF_IDIOMA_CAMINHO"

_CACHE = {}
_PROBLEMAS = {}


def _carregar_de(caminho, nome):
    """Um catalogo de um arquivo — ou None, com o motivo guardado."""
    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location(
            f"_df_idioma_{nome}", caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
    except Exception as erro:                              # noqa: BLE001
        _PROBLEMAS[nome] = f"{type(erro).__name__}: {erro}"
        return None
    inteiras = getattr(modulo, "INTEIRAS", None)
    pedacos = getattr(modulo, "PEDACOS", ())
    if inteiras is None:
        _PROBLEMAS[nome] = "o arquivo nao define INTEIRAS"
        return None
    return {"inteiras": tuple(inteiras), "pedacos": tuple(pedacos),
            "arquivo": caminho}


def _pastas():
    yield os.path.dirname(os.path.abspath(__file__))
    de_fora = os.environ.get(VARIAVEL_DE_CAMINHO)
    if de_fora and os.path.isdir(de_fora):
        yield de_fora


def registro(recarregar=False):
    """{codigo: catalogo} — os idiomas que existem agora.

    O cache e por processo. `recarregar` existe para o teste que planta
    um catalogo numa pasta temporaria: sem ele, o primeiro acesso
    congelaria o registro antes de a pasta existir.
    """
    if _CACHE and not recarregar:
        return _CACHE
    _CACHE.clear()
    _PROBLEMAS.clear()
    for pasta in _pastas():
        for caminho in sorted(glob.glob(os.path.join(pasta, "*.py"))):
            nome = os.path.basename(caminho)[:-3]
            if nome.startswith("_") or nome == ORIGINAL:
                continue
            catalogo = _carregar_de(caminho, nome)
            if catalogo is not None:
                # A pasta de fora vem depois, e por isso VENCE: e o que
                # permite corrigir uma traducao sem reinstalar nada.
                _CACHE[nome] = catalogo
    return _CACHE


def problemas():
    """Os catalogos que nao carregaram, com o motivo."""
    registro()
    return dict(_PROBLEMAS)


def codigos():
    """Os idiomas para os quais ha traducao, mais o original."""
    return sorted(registro()) + [ORIGINAL]
