# -*- coding: utf-8 -*-
"""Versões instaladas lado a lado, e a versão que o projeto exige.

O problema
----------
Havia um jeito de instalar e nenhum de **escolher**: trocar de versão era
reinstalar por cima, e não havia como dizer "este projeto roda na 1.0.0".
O campo `project.dataforge` do `forge.toml` já existia e já sabia ler
`>=`, `^` e `~` — e **ninguém o cobrava**: `dataforge info` o mostrava, e
era tudo.

Como funciona
-------------
    <raiz>/versoes/<versao>/      uma venv por versão
    <raiz>/atual                  a versão escolhida globalmente

`<raiz>` é `~/.dataforge`, ou `DATAFORGE_RAIZ` — é o que torna isto
testável sem tocar na instalação de quem está rodando.

E o que faz a escolha valer: `dataforge run` **confere o pino do
projeto** e, quando ele aponta outra versão que está instalada, entrega a
execução a ela. Sem essa troca, `use` escreveria num arquivo e nada
aconteceria — um comando que finge.

Os limites, escritos
--------------------
* A troca acontece no `run` e no `test`. Não há um *shim* no PATH: o
  `dataforge` que você chama é o que está instalado, e é ele que
  redireciona.
* Instalar uma versão precisa de rede e de `pip`. `upgrade` faz isso; sem
  rede, ele diz o que faria.
* Um pino que aponta versão **não instalada** é erro, com o comando que a
  instala — e não um aviso que se ignora.
"""

import os
import subprocess
import sys

from . import __version__
from .errors import RuntimeError_

#: A marca que impede a troca de acontecer duas vezes. Sem ela, um
#: executável mal configurado que apontasse para si mesmo entraria em
#: laço — e um laço na partida é o defeito mais difícil de interromper.
MARCA_DE_TROCA = "DATAFORGE_VERSAO_TROCADA"


def raiz():
    return os.environ.get("DATAFORGE_RAIZ") or os.path.join(
        os.path.expanduser("~"), ".dataforge")


def pasta_de_versoes():
    return os.path.join(raiz(), "versoes")


def _marcador():
    return os.path.join(raiz(), "atual")


def instaladas():
    """As versões que existem em disco, da mais nova para a mais velha."""
    alvo = pasta_de_versoes()
    if not os.path.isdir(alvo):
        return []
    achadas = []
    for nome in os.listdir(alvo):
        if os.path.isdir(os.path.join(alvo, nome)):
            achadas.append(nome)
    return sorted(achadas, key=_ordem, reverse=True)


def _ordem(versao):
    partes = []
    for pedaco in str(versao).replace("-", ".").split("."):
        partes.append(int(pedaco) if pedaco.isdigit() else 0)
    return tuple(partes + [0, 0, 0])[:4]


def executavel_de(versao):
    """O `dataforge` daquela versão, ou `None` se ela não está instalada."""
    base = os.path.join(pasta_de_versoes(), str(versao))
    for relativo in (("bin", "dataforge"), ("Scripts", "dataforge.exe"),
                     ("Scripts", "dataforge")):
        candidato = os.path.join(base, *relativo)
        if os.path.isfile(candidato):
            return candidato
    return None


def ativa():
    """A versão escolhida globalmente, ou a que está rodando."""
    try:
        with open(_marcador(), encoding="utf-8") as arquivo:
            escolhida = arquivo.read().strip()
        if escolhida:
            return escolhida
    except OSError:
        pass
    return __version__


def fixada(inicio="."):
    """O que o `forge.toml` deste projeto exige, e o manifesto."""
    from . import project

    manifesto = project.carregar(inicio)
    if manifesto is None:
        return "", None
    exigido = str(manifesto.dados["project"].get("dataforge", "")).strip()
    return exigido, manifesto


def _so_numero(exigido):
    """'>=1.0.0' -> '1.0.0'. Vazio quando não é um pino exato."""
    texto = str(exigido).strip()
    for operador in (">=", "<=", "==", ">", "<", "^", "~"):
        if texto.startswith(operador):
            texto = texto[len(operador):].strip()
            break
    return texto


def usar(versao, global_=False, projeto="."):
    """Escolhe a versão: no projeto (padrão) ou globalmente.

    No projeto ela vira `project.dataforge` do `forge.toml` — o mesmo
    campo que o manifesto já lia. Globalmente, um arquivo `atual` na raiz.
    """
    alvo = str(versao).strip()
    if not alvo:
        raise RuntimeError_("diga a versão: 'dataforge use 1.0.0'",
                            doc="cli/versoes")
    if global_:
        os.makedirs(raiz(), exist_ok=True)
        with open(_marcador(), "w", encoding="utf-8") as arquivo:
            arquivo.write(alvo + "\n")
        return {"onde": "global", "versao": alvo,
                "arquivo": _marcador(),
                "instalada": executavel_de(alvo) is not None}

    from . import project

    manifesto = project.carregar(projeto)
    if manifesto is None:
        raise RuntimeError_(
            "nenhum forge.toml aqui nem acima: o pino de versão é do "
            "PROJETO.",
            dica="crie um com 'dataforge init', ou use "
                 "'dataforge use <versao> --global'",
            doc="cli/versoes")
    _escrever_pino(manifesto.caminho, alvo)
    return {"onde": "projeto", "versao": alvo, "arquivo": manifesto.caminho,
            "instalada": executavel_de(alvo) is not None}


def _escrever_pino(caminho, versao):
    """Troca (ou acrescenta) `dataforge = "…"` na seção `[project]`.

    Reescreve LINHA A LINHA em vez de serializar o TOML de novo: o
    manifesto é escrito por uma pessoa, e regravá-lo a partir da estrutura
    apagaria comentários e a ordem dos campos. Um comando que mexe num
    arquivo de configuração não pode reformatá-lo por baixo.

    O campo novo entra depois da ÚLTIMA linha com conteúdo da seção, e não
    no fim dela: uma linha em branco separa as seções, e inserir depois
    dela punha o campo do `[project]` visualmente na seção seguinte.
    """
    with open(caminho, encoding="utf-8") as arquivo:
        bruto = arquivo.read()
    terminava_com_quebra = bruto.endswith("\n")
    linhas = bruto.split("\n")

    saida = []
    dentro = False
    trocada = False
    ultima_com_conteudo = None
    for linha in linhas:
        nu = linha.strip()
        if nu.startswith("[") and nu.endswith("]"):
            dentro = nu == "[project]"
        if dentro and nu.replace(" ", "").startswith("dataforge="):
            saida.append(f'dataforge = "{versao}"')
            trocada = True
            ultima_com_conteudo = len(saida)
            continue
        saida.append(linha)
        if dentro and nu:
            ultima_com_conteudo = len(saida)

    if not trocada:
        posicao = (ultima_com_conteudo if ultima_com_conteudo is not None
                   else len(saida))
        saida.insert(posicao, f'dataforge = "{versao}"')

    texto = "\n".join(saida)
    if terminava_com_quebra and not texto.endswith("\n"):
        texto += "\n"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)


def precisa_trocar(inicio="."):
    """A execução deveria passar para outra versão? Devolve (versão, motivo).

    Devolve `("", "")` quando não há o que trocar — que é o caso comum, e
    por isso ele custa uma leitura de `forge.toml` e nada mais.
    """
    if os.environ.get(MARCA_DE_TROCA) or os.environ.get("DATAFORGE_SEM_TROCA"):
        return "", ""
    exigido, manifesto = fixada(inicio)
    if not exigido or manifesto is None:
        return "", ""
    ok, _ = manifesto.requires(__version__)
    if ok:
        return "", ""
    alvo = _so_numero(exigido)
    if not alvo or alvo == __version__:
        return "", ""
    return alvo, (f"o projeto exige DataForge {exigido}, e esta é a "
                  f"{__version__}")


def trocar(versao, argv):
    """Entrega a execução à outra versão. Só volta se não der.

    Ela não é opcional: sem a troca, `use` escreveria num arquivo e nada
    aconteceria — e um comando que finge é pior que um comando que falta.
    """
    executavel = executavel_de(versao)
    if executavel is None:
        return False
    ambiente = {**os.environ, MARCA_DE_TROCA: versao}
    os.execve(executavel, [executavel] + list(argv), ambiente)
    return True                                        # pragma: no cover


def disponiveis(prazo=10):
    """As versões publicadas, lidas do site. Lista vazia sem rede."""
    import json
    import urllib.request

    endereco = os.environ.get(
        "DATAFORGE_VERSOES_URL",
        "https://dataforge-lang.vercel.app/api/index.json")
    try:
        with urllib.request.urlopen(endereco, timeout=prazo) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
    except Exception:                                  # noqa: BLE001
        return []
    versao = str(dados.get("versao") or dados.get("version") or "").strip()
    return [versao] if versao else []


def instalar(versao, executar=True):
    """Instala uma versão numa venv própria, com `pip`.

    `executar := no` devolve os comandos sem rodá-los — é o que deixa
    `upgrade --check` dizer o que faria sem mexer em nada, e o que torna
    isto testável sem rede.
    """
    alvo = os.path.join(pasta_de_versoes(), str(versao))
    passos = [
        [sys.executable, "-m", "venv", alvo],
        [os.path.join(alvo, "bin", "pip"), "install",
         f"dataforge-lang=={versao}"],
    ]
    if not executar:
        return {"versao": str(versao), "pasta": alvo, "passos": passos,
                "feito": False}
    os.makedirs(pasta_de_versoes(), exist_ok=True)
    for passo in passos:
        r = subprocess.run(passo, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            return {"versao": str(versao), "pasta": alvo, "passos": passos,
                    "feito": False,
                    "erro": (r.stderr or r.stdout or "")[-400:]}
    return {"versao": str(versao), "pasta": alvo, "passos": passos,
            "feito": True}


def relatorio():
    """O que está instalado, o que está ativo, o que o projeto exige."""
    exigido, manifesto = fixada(".")
    return {
        "rodando": __version__,
        "ativa": ativa(),
        "instaladas": instaladas(),
        "raiz": raiz(),
        "projeto": manifesto.caminho if manifesto else "",
        "exigido": exigido,
        "satisfeito": (manifesto.requires(__version__)[0]
                       if manifesto else True),
    }


# ═══ O workspace: vários pacotes numa árvore ═══════════════
#
# O que não existia: um comando que olhasse a árvore INTEIRA. Cada pacote
# tinha o seu `forge.toml`, e a única forma de saber se dois deles pediam
# faixas incompatíveis do mesmo terceiro era instalar os dois e esperar o
# erro — que aparece no dia da instalação, na máquina de quem consome.
#
# Ele não INSTALA por padrão: lê, resolve e relata. Instalar a árvore
# inteira de um comando que a pessoa rodou para "ver o que tem" é mexer
# em disco sem ser pedido.

#: Pastas que não são pacote do projeto, e varrer não ajuda.
IGNORADAS = ("forge_modules", "node_modules", ".git", "dist", "out",
             "__pycache__", ".venv", "venv", "site")


def pacotes_da_arvore(raiz_da_arvore="."):
    """Todo `forge.toml` abaixo daqui, com nome, versão e dependências."""
    from . import project

    base = os.path.abspath(raiz_da_arvore)
    achados = []
    for pasta, subpastas, arquivos in os.walk(base):
        subpastas[:] = [s for s in subpastas
                        if s not in IGNORADAS and not s.startswith(".")]
        if project.ARQUIVO not in arquivos:
            continue
        caminho = os.path.join(pasta, project.ARQUIVO)
        manifesto = project.carregar(caminho)
        if manifesto is None:
            continue
        achados.append({
            "nome": manifesto.name or os.path.basename(pasta),
            "versao": manifesto.version,
            "caminho": os.path.relpath(caminho, base),
            "pasta": pasta,
            "dependencias": dict(manifesto.dados.get("dependencies") or {}),
            "exige_dataforge": str(
                manifesto.dados["project"].get("dataforge", "")).strip(),
        })
    return sorted(achados, key=lambda p: p["caminho"])


def conflitos_da_arvore(pacotes):
    """Dois pacotes pedindo faixas incompatíveis do mesmo terceiro.

    A interseção é feita pela MESMA classe que o `resolver` usa: uma
    segunda noção de "estas faixas se cruzam?" divergiria da instalação,
    e aí o relatório aprovaria o que o `add` recusa.
    """
    from .packages import Requisito

    pedidos = {}
    for pacote in pacotes:
        for nome, faixa in pacote["dependencias"].items():
            pedidos.setdefault(nome, []).append((pacote["nome"], str(faixa)))

    achados = []
    for nome, quem in sorted(pedidos.items()):
        if len(quem) < 2:
            continue
        requisitos = [(autor, Requisito(faixa)) for autor, faixa in quem]
        cruzam = True
        for i in range(len(requisitos)):
            for j in range(i + 1, len(requisitos)):
                if not _cruzam(requisitos[i][1], requisitos[j][1]):
                    cruzam = False
        if not cruzam:
            achados.append({"pacote": nome,
                            "pedidos": [{"quem": a, "faixa": f}
                                        for a, f in quem]})
    return achados


def _cruzam(um, outro):
    """Há alguma versão que sirva aos dois requisitos?

    Sem uma lista de versões publicadas não há como decidir por
    enumeração, então a pergunta é feita sobre os PINOS EXATOS: se um dos
    dois exige `==X` e o outro recusa o `X`, o conflito está provado. Fora
    disso, cala — é a mesma prudência do analisador estático, e um falso
    conflito faria o comando ser ignorado.

    Os pinos saem de `Requisito.clausulas`, que é a MESMA estrutura que o
    `resolver` usa. Uma segunda noção de "estas faixas se cruzam?"
    divergiria da instalação, e aí o relatório aprovaria o que o `add`
    recusa.
    """
    for candidato in (um, outro):
        for operador, alvo in getattr(candidato, "clausulas", ()) or ():
            if operador != "==":
                continue
            if not (um.aceita(alvo) and outro.aceita(alvo)):
                return False
    return True


def relatorio_do_workspace(raiz_da_arvore="."):
    pacotes = pacotes_da_arvore(raiz_da_arvore)
    exigencias = sorted({p["exige_dataforge"] for p in pacotes
                         if p["exige_dataforge"]})
    return {
        "raiz": os.path.abspath(raiz_da_arvore),
        "pacotes": pacotes,
        "conflitos": conflitos_da_arvore(pacotes),
        "exigencias_de_dataforge": exigencias,
        "dependencias": sorted({nome for p in pacotes
                                for nome in p["dependencias"]}),
    }
