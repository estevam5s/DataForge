# -*- coding: utf-8 -*-
"""O cache de árvores: parse uma vez, releia nas próximas execuções.

O que ele NÃO é
---------------
Não é um cache de **fechamentos**. `compilador.py` transforma a árvore em
funções Python, e função não atravessa processo — não há o que guardar.
O que se guarda é a **árvore**, que é o trabalho repetido de verdade: o
lexer e o parser refazem, a cada execução, exatamente a mesma coisa a
partir de um arquivo que não mudou.

O número, medido
----------------
269 arquivos do repositório:

    lex + parse ............ 258,7 ms
    pickle.loads ............ 17,9 ms      **93% menos**
    tamanho do cache ....... 1553 KB

E o número desconfortável, que também é o número: num arquivo só de 383
linhas, o ganho ponta a ponta de `dataforge run` é de **4,4%** — porque
76 ms dos 132 ms do comando são o `import` do próprio Python. O cache
vale onde há MUITOS arquivos (o `check` de um projeto, a CI), e quase não
aparece num script pequeno. Publicar só a primeira medida seria escolher
a medida.

A chave é o que impede o desastre
---------------------------------
Um cache que devolve a árvore errada é pior que nenhum cache: o programa
roda, e roda outra coisa. A chave carrega:

* o caminho absoluto;
* o `mtime_ns` e o tamanho do arquivo;
* a versão da linguagem;
* e um **resumo da própria implementação** — `lexer.py`, `parser.py`,
  `ast_nodes.py` e `tokens.py`.

O último é o que importa durante o desenvolvimento: mexer no parser sem
subir a versão invalidaria nada, e a execução seguinte leria uma árvore
que o parser de hoje não produziria mais.

Qualquer falha — cache corrompido, disco cheio, versão de pickle
diferente — cai no caminho normal e refaz o parse. O cache é uma
otimização, e uma otimização nunca pode ser um motivo de erro.
"""

import hashlib
import os
import pickle

from . import __version__

#: `DATAFORGE_SEM_CACHE=1` desliga. Serve para medir, e para o dia em que
#: alguém precisa provar que um defeito não é do cache.
DESLIGADO = os.environ.get("DATAFORGE_SEM_CACHE", "") not in ("", "0")

#: Formato do que é guardado. Subir isto invalida tudo de uma vez.
FORMATO = 1

_resumo_da_implementacao = None


def _implementacao():
    """Um resumo de quem PRODUZ a árvore — o parser, o lexer, os nós.

    Sem ele, mexer no parser durante o desenvolvimento deixaria árvores
    velhas no cache, e a execução seguinte leria uma forma que o código
    de hoje não produz mais. É o erro mais difícil de diagnosticar que um
    cache pode causar, porque nada acusa: o programa roda.
    """
    global _resumo_da_implementacao
    if _resumo_da_implementacao is not None:
        return _resumo_da_implementacao
    aqui = os.path.dirname(os.path.abspath(__file__))
    resumo = hashlib.sha256()
    resumo.update(f"{__version__}|{FORMATO}|".encode("utf-8"))
    for nome in ("lexer.py", "parser.py", "ast_nodes.py", "tokens.py",
                 "tipos_nomeados.py"):
        caminho = os.path.join(aqui, nome)
        try:
            st = os.stat(caminho)
            resumo.update(f"{nome}:{st.st_mtime_ns}:{st.st_size}|"
                          .encode("utf-8"))
        except OSError:                                # pragma: no cover
            resumo.update(f"{nome}:?|".encode("utf-8"))
    _resumo_da_implementacao = resumo.hexdigest()[:16]
    return _resumo_da_implementacao


def pasta():
    """Onde o cache mora. `~/.dataforge/cache/arvores`, por padrão."""
    raiz = os.environ.get("DATAFORGE_CACHE") or os.path.join(
        os.path.expanduser("~"), ".dataforge", "cache")
    return os.path.join(raiz, "arvores")


def _chave(caminho):
    try:
        st = os.stat(caminho)
    except OSError:
        return None
    alvo = os.path.abspath(caminho)
    cru = f"{_implementacao()}|{alvo}|{st.st_mtime_ns}|{st.st_size}"
    return hashlib.sha256(cru.encode("utf-8")).hexdigest()


def _arquivo_de(chave):
    # Duas letras de prefixo: um diretório com dez mil arquivos fica lento
    # de listar em alguns sistemas, e o cache de um monorepo chega lá.
    return os.path.join(pasta(), chave[:2], chave[2:] + ".arv")


def ler(caminho):
    """A árvore guardada para este arquivo, ou `None`."""
    if DESLIGADO:
        return None
    chave = _chave(caminho)
    if chave is None:
        return None
    try:
        with open(_arquivo_de(chave), "rb") as arquivo:
            return pickle.loads(arquivo.read())
    except Exception:                                  # noqa: BLE001
        # Corrompido, versão de pickle diferente, sem permissão: refaz.
        return None


def guardar(caminho, arvore):
    """Guarda a árvore. Falhar aqui não pode interromper nada."""
    if DESLIGADO:
        return False
    chave = _chave(caminho)
    if chave is None:
        return False
    destino = _arquivo_de(chave)
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        # Escreve ao lado e renomeia: um processo interrompido no meio
        # deixaria um arquivo pela metade, e o `ler` seguinte o leria.
        # `os.replace` é atômico no POSIX e no Windows.
        temporario = destino + f".{os.getpid()}.parcial"
        with open(temporario, "wb") as arquivo:
            arquivo.write(pickle.dumps(arvore,
                                       protocol=pickle.HIGHEST_PROTOCOL))
        os.replace(temporario, destino)
        return True
    except Exception:                                  # noqa: BLE001
        return False


def arvore(caminho, fonte, parse, tokenize):
    """A árvore deste arquivo — do cache, ou feita e guardada.

    `parse` e `tokenize` entram por argumento para este módulo não
    importar o parser: ele é carregado por `cli.py` na partida, e um
    import a mais aqui custaria em toda execução, inclusive nas que não
    usam cache.
    """
    guardada = ler(caminho)
    if guardada is not None:
        return guardada
    feita = parse(tokenize(fonte, caminho), caminho)
    guardar(caminho, feita)
    return feita


def limpar():
    """Apaga o cache. Devolve (arquivos, bytes)."""
    import shutil

    alvo = pasta()
    if not os.path.isdir(alvo):
        return 0, 0
    quantos = tamanho = 0
    for raiz, _pastas, arquivos in os.walk(alvo):
        for nome in arquivos:
            try:
                tamanho += os.path.getsize(os.path.join(raiz, nome))
                quantos += 1
            except OSError:                            # pragma: no cover
                pass
    shutil.rmtree(alvo, ignore_errors=True)
    return quantos, tamanho


def estado():
    """Quantos arquivos e quantos bytes o cache tem agora."""
    alvo = pasta()
    quantos = tamanho = 0
    for raiz, _pastas, arquivos in os.walk(alvo) if os.path.isdir(alvo) else ():
        for nome in arquivos:
            try:
                tamanho += os.path.getsize(os.path.join(raiz, nome))
                quantos += 1
            except OSError:                            # pragma: no cover
                pass
    return {"pasta": alvo, "arquivos": quantos, "bytes": tamanho,
            "ligado": not DESLIGADO}
