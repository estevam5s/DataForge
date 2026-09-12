"""A ponte para o Python — `adopt Python.numpy as np`.

Por que ela existe
------------------
Sem ela, toda capacidade nova precisa ser reescrita do zero na
biblioteca padrão. Foi assim que este repositório ganhou um Parquet
próprio, um ChaCha20 próprio e 25 algoritmos de aprendizado próprios —
cada um correto, cada um a uma fração do que existe pronto lá fora. Isso
não escala: o numpy tem vinte anos de otimização numérica que nenhuma
stdlib artesanal alcança.

A ironia é que o DataForge **roda sobre Python** e não alcançava nada
dele. Esta é a porta.

Onde fica a linha da promessa
-----------------------------
O projeto promete **zero dependências no runtime**, e essa promessa
continua inteira: nada em `dataforge/` importa nada de fora. O que muda
é que o *programa de quem escreve* passa a poder escolher as suas.

A distinção é a mesma que separa "o Python não depende do numpy" de
"o seu script pode depender". `adopt Python.x` é a declaração explícita
de que, a partir dali, o programa deixou de ser portátil por conta
própria — e é por isso que a palavra `Python` aparece na linha. Quem lê
o código sabe exatamente onde a fronteira foi cruzada.

O que atravessa, e como
-----------------------
**A ponte não converte.** Um `ndarray` continua um `ndarray`, e é
justamente por isso que `a * 2 + 1` faz a conta vetorizada do numpy em
vez de virar um laço sobre um cluster de um milhão de posições.

Isso funciona porque o interpretador já trata objeto estranho pelo que
ele *faz*, e não pelo que ele é: membro, método, índice, `len`,
iteração, aritmética, texto e verdade já passavam por protocolo. A ponte
não reimplementa nada disso.

O preço é que o vocabulário vaza em dois lugares, e os dois estão
documentados: uma tupla do Python não é um `Cluster` (use
`Ponte.cluster`), e `typeof` de um `ndarray` diz `ndarray`, porque é o
que ele é.

O que ela NÃO protege
---------------------
`adopt Python.os` roda o código de inicialização do pacote, exatamente
como um `import` faria. Não há sandbox aqui, e fingir que há seria pior
que não ter: a linguagem já permite `Arcane.Process.run` e escrita em
disco. A ponte não acrescenta uma categoria de risco — ela a torna
visível na linha do `adopt`.
"""

import difflib
import importlib
import os
import sys

from .errors import ImportError_, NameError_

#: O prefixo que abre a ponte: `adopt Python.<o que for>`.
PREFIXO = "Python"


def empacotado() -> bool:
    """O DataForge está rodando de dentro do executável único?

    Importa muito para a mensagem de erro: o executável traz um Python
    próprio, **sem pip**, e nunca vai conseguir instalar pacote nenhum.
    Mandar o usuário rodar `pip install numpy` ali é mandá-lo a lugar
    nenhum, e ele levaria um tempo até desconfiar do conselho.
    """
    return getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS")


def onde() -> str:
    """O Python que está por trás — e é nele que o pacote precisa estar.

    O instalador do DataForge cria uma venv em `~/.dataforge`. Quem roda
    `pip install numpy` no terminal instala no Python do SISTEMA, que é
    outro, e o `adopt` continua falhando sem que nada explique por quê.
    Por isso a mensagem sempre nomeia o interpretador exato.
    """
    return sys.executable or "<desconhecido>"


def _comando_de_instalacao(pacote: str) -> str:
    return f"{onde()} -m pip install {pacote}"


def _raiz_do_caminho(nome: str) -> str:
    """'Python.numpy.linalg' → 'numpy' — o pacote que se instala."""
    resto = nome[len(PREFIXO) + 1:] if nome.startswith(PREFIXO + ".") else nome
    return resto.split(".")[0]


def _erro_de_ausencia(nome_df, pacote, node, causa=""):
    """A mensagem de quando o pacote não está instalado.

    Ela responde as três perguntas que a pessoa vai ter, nesta ordem: o
    que faltou, **em qual Python** faltou, e o comando exato para aquele
    Python — não o `pip` genérico, que provavelmente é de outro.
    """
    linha = getattr(node, "line", 0)
    coluna = getattr(node, "column", 0)

    if empacotado():
        return ImportError_(
            f"o pacote Python '{pacote}' nao esta disponivel.",
            linha, coluna,
            nota="este e o executavel do DataForge, que traz um Python "
                 "proprio e nao tem 'pip' — ele nao instala pacote nenhum",
            dica="para usar bibliotecas Python, instale o DataForge pelo "
                 "pip em vez do executavel:\n"
                 "    pip install dataforge-lang",
            doc="tecnicas/ponte")

    extra = f"\n{causa}" if causa else ""
    return ImportError_(
        f"o pacote Python '{pacote}' nao esta instalado.{extra}",
        linha, coluna,
        nota=f"o DataForge roda sobre {onde()} — "
             f"e e NESSE Python que o pacote precisa estar",
        dica=_comando_de_instalacao(pacote),
        doc="tecnicas/ponte")


class ModuloPython:
    """Um módulo do Python visto de dentro do DataForge.

    É uma casca fina, e de propósito: ela **não** embrulha o que
    devolve. `np.array` entrega a função de verdade, e o array que sai
    dela é o array do numpy. Embrulhar tudo custaria uma cópia por
    valor e mataria a razão de existir da ponte.

    O que a casca acrescenta é o que só ela pode acrescentar: um nome
    legível em `typeof` e no `out`, e uma mensagem decente quando o
    atributo não existe — `np.arrray` sugere `array`, em vez de dizer
    "Cannot access member 'arrray' on module".
    """

    __slots__ = ("_modulo", "_nome")

    def __init__(self, modulo, nome):
        object.__setattr__(self, "_modulo", modulo)
        object.__setattr__(self, "_nome", nome)

    # ── Leitura de nomes ─────────────────────────────────────

    def __getattr__(self, nome):
        # Nome com '__' volta como AttributeError normal. É deliberado:
        # o interpretador pergunta '__iter__', '__len__' e afins com
        # 'hasattr', e 'hasattr' só engole AttributeError — um erro da
        # linguagem levantado aqui escaparia de uma checagem interna e
        # derrubaria o programa por uma pergunta que era só uma consulta.
        if nome.startswith("__"):
            raise AttributeError(nome)

        modulo = object.__getattribute__(self, "_modulo")
        try:
            valor = getattr(modulo, nome)
        except AttributeError:
            raise self._nao_tem(nome) from None

        # Submódulo continua sendo ponte, para que a mensagem boa valha
        # também em 'np.linalg.invv'. Qualquer outro valor passa cru.
        if type(valor).__name__ == "module":
            proprio = object.__getattribute__(self, "_nome")
            return ModuloPython(valor, f"{proprio}.{nome}")
        return valor

    def _nao_tem(self, nome):
        proprio = object.__getattribute__(self, "_nome")
        modulo = object.__getattribute__(self, "_modulo")
        publicos = [n for n in dir(modulo) if not n.startswith("_")]
        parecidos = difflib.get_close_matches(nome, publicos, n=3, cutoff=0.7)

        dica = ""
        if parecidos:
            dica = ("voce quis dizer " +
                    " ou ".join(f"'{p}'" for p in parecidos) + "?")
        elif publicos:
            amostra = ", ".join(sorted(publicos)[:8])
            dica = (f"'Ponte.atributos({proprio.split('.')[-1]})' lista os "
                    f"{len(publicos)} nomes. Comecam com: {amostra}…")

        return NameError_(
            f"o modulo '{proprio}' nao tem '{nome}'.",
            0, 0, dica=dica, doc="tecnicas/ponte")

    # ── O que 'adopt M.{a, b}' precisa ───────────────────────

    def __contains__(self, nome):
        return hasattr(object.__getattribute__(self, "_modulo"), nome)

    def __getitem__(self, nome):
        return getattr(self, nome)

    def __iter__(self):
        modulo = object.__getattribute__(self, "_modulo")
        return iter(n for n in dir(modulo) if not n.startswith("_"))

    # ── Apresentação ─────────────────────────────────────────

    def __repr__(self):
        return f"<modulo Python '{object.__getattribute__(self, '_nome')}'>"

    __str__ = __repr__

    @property
    def nome(self):
        return object.__getattribute__(self, "_nome")

    @property
    def cru(self):
        """O módulo do Python, sem a casca."""
        return object.__getattribute__(self, "_modulo")


def e_caminho_de_ponte(nome_modulo: str) -> bool:
    """'Python.numpy' abre a ponte; 'Pythonico' não."""
    return nome_modulo == PREFIXO or nome_modulo.startswith(PREFIXO + ".")


def importar(nome_modulo: str, node=None):
    """`adopt Python.numpy` → o módulo, embrulhado.

    Separa dois casos que o Python junta num `ModuleNotFoundError` só, e
    que pedem respostas opostas: o pacote **não está instalado** (a
    pessoa precisa instalar) e o pacote **existe mas explodiu ao
    carregar** (a pessoa precisa ver o erro dele, não um conselho de
    instalação).
    """
    if nome_modulo == PREFIXO:
        raise ImportError_(
            "'adopt Python' sozinho nao importa nada.",
            getattr(node, "line", 0), getattr(node, "column", 0),
            nota="e preciso dizer QUAL modulo",
            dica="adopt Python.numpy as np\n"
                 "adopt Python.json.{loads, dumps}",
            doc="tecnicas/ponte")

    caminho = nome_modulo[len(PREFIXO) + 1:]
    pacote = _raiz_do_caminho(nome_modulo)

    try:
        modulo = importlib.import_module(caminho)
    except ModuleNotFoundError as erro:
        # O que faltou foi o pacote pedido, ou uma dependência DELE?
        ausente = getattr(erro, "name", "") or pacote
        if ausente.split(".")[0] == pacote:
            raise _erro_de_ausencia(nome_modulo, pacote, node) from None
        raise _erro_de_ausencia(
            nome_modulo, ausente.split(".")[0], node,
            causa=f"(pedido por '{pacote}')") from None
    except ImportError_:
        raise
    except Exception as erro:                    # noqa: BLE001
        # O pacote existe e falhou ao carregar. Mandar instalar seria o
        # conselho errado, e mandaria a pessoa procurar no lugar errado.
        raise ImportError_(
            f"o pacote Python '{pacote}' esta instalado, mas falhou ao "
            f"carregar.",
            getattr(node, "line", 0), getattr(node, "column", 0),
            nota=f"{type(erro).__name__}: {erro}",
            dica=f"o erro e do proprio pacote, nao do DataForge. "
                 f"Confira a instalacao dele:\n"
                 f"    {onde()} -c \"import {pacote}\"",
            doc="tecnicas/ponte") from None

    return ModuloPython(modulo, nome_modulo)


# ── Conversões explícitas ────────────────────────────────────
#
# A ponte não converte sozinha, então estas existem para quando a pessoa
# QUER o valor no vocabulário da linguagem. Serem explícitas é o ponto:
# `Ponte.cluster(arr)` diz, na linha, que ali se paga uma cópia.

def para_cluster(valor):
    """Qualquer coisa percorrível do Python vira um `Cluster`."""
    if isinstance(valor, list):
        return valor
    try:
        return list(valor)
    except TypeError:
        raise NameError_(
            f"'{tipo_de(valor)}' nao e percorrivel — nao da para virar "
            f"um Cluster.", 0, 0,
            dica="so vale para o que o Python sabe percorrer: tupla, "
                 "conjunto, gerador, array…",
            doc="tecnicas/ponte") from None


def para_vault(valor):
    """Qualquer mapa do Python vira um `Vault`."""
    if isinstance(valor, dict):
        return valor
    try:
        return dict(valor)
    except (TypeError, ValueError):
        raise NameError_(
            f"'{tipo_de(valor)}' nao vira um Vault.", 0, 0,
            dica="precisa ser um mapa, ou uma sequencia de pares",
            doc="tecnicas/ponte") from None


def tipo_de(valor) -> str:
    """O nome do tipo do lado do Python — `ndarray`, `DataFrame`, `int64`.

    Existe porque `typeof` responde no vocabulário do DataForge, e
    às vezes a pergunta é justamente a outra: *o que isto é lá do outro
    lado?*
    """
    if isinstance(valor, ModuloPython):
        return "module"
    return type(valor).__name__


def atributos(valor):
    """Os nomes públicos de um objeto ou módulo Python, ordenados.

    É a ferramenta de exploração da ponte: sem ela, descobrir o que um
    pacote oferece exige sair da linguagem e abrir a documentação dele.
    """
    alvo = valor.cru if isinstance(valor, ModuloPython) else valor
    return sorted(n for n in dir(alvo) if not n.startswith("_"))


def tem(nome: str) -> bool:
    """O pacote está instalado? Responde sem levantar erro.

    É o que permite um programa se adaptar:

        given Ponte.tem("numpy"):
            adopt Python.numpy as np
    """
    try:
        return importlib.util.find_spec(nome.split(".")[0]) is not None
    except (ImportError, ValueError, AttributeError):
        return False


def versao(nome: str):
    """A versão instalada do pacote, ou `void`."""
    raiz = nome.split(".")[0]
    try:
        from importlib import metadata
        return metadata.version(raiz)
    except Exception:                            # noqa: BLE001
        pass
    try:
        modulo = importlib.import_module(raiz)
    except Exception:                            # noqa: BLE001
        return None
    v = getattr(modulo, "__version__", None)
    return str(v) if v is not None else None
