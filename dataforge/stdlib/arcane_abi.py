# -*- coding: utf-8 -*-
"""Arcane.Abi — a superfície de um módulo é o contrato dele.

O que faltava
-------------
Numa linguagem compilada, quebrar a ABI é trocar o layout de uma struct
ou a convenção de chamada, e o sintoma é um programa que **carrega** e
corrompe memória. Aqui não há layout binário a quebrar — e há
exatamente o mesmo problema com outro nome.

A **superfície** de um módulo (o que ele exporta, com que aridade, com
que tipos) é o contrato dele. Mudá-la quebra quem depende, em silêncio,
no dia da atualização — e o gerenciador de pacotes desta linguagem já
tinha semver, `forge.lock` e verificação de integridade, mas **nada
conferia se a versão nova quebra a anterior**. O número da versão era
escolhido a olho.

    adopt Arcane.Abi as Abi

    r := Abi.comparar("v1/lib.df", "v2/lib.df")
    given r["veredito"] is "maior":
        out "isto exige subir a versao MAIOR"

E na linha de comando, para o CI:

    dataforge abi antes.df depois.df     # sai com 1 se quebrou

Por que isto é a mesma coisa que ABI
------------------------------------
| Na linguagem compilada | Aqui |
|---|---|
| símbolo removido do `.so` | símbolo tirado do `relay` |
| assinatura trocada | aridade ou tipo de parâmetro trocado |
| layout de struct mudado | campo acrescentado a um `record` |
| `soname` bump | versão **maior** no `forge.toml` |

O sintoma também é o mesmo: **não é um erro de compilação de quem
publicou**. É um erro de quem consome, depois, e longe da causa.

Três decisões
-------------
1. **A conta sai de `superficie.py`**, o mesmo módulo que o `check` usa
   para atravessar arquivos. Uma segunda leitura da superfície
   divergiria da primeira, e aí o `check` e o `abi` discordariam sobre o
   que um módulo oferece.

2. **Uma superfície que não compila não julga.** `veredito` devolve
   `"desconhecido"` com o motivo, em vez de acusar quebra. Um falso
   alarme aqui reprova um release que está certo — e a segunda vez que
   isso acontece, a conferência é desligada.

3. **Renomear um parâmetro é quebra.** Nesta linguagem a chamada com
   nome existe (`somar(a := 1, b := 2)`), então o nome do parâmetro é
   parte do contrato — e não apenas a posição. É a diferença que uma
   ferramenta feita para C não precisaria fazer.
"""

from .. import superficie as _superficie
from ..errors import RuntimeError_

#: As regras, nomeadas. Cada quebra carrega um destes tipos, e a lista é
#: a documentação — há teste cobrando o tamanho de cada explicação.
REGRAS = {
    "simbolo-removido":
        "um nome que o módulo exportava deixou de existir; quem o "
        "adotava para de compilar no dia da atualização",
    "especie-trocada":
        "o nome continua, e virou outra coisa (uma ação virou record): "
        "toda forma de uso muda junto",
    "aridade-incompativel":
        "uma chamada que era válida deixou de ser — mais argumento "
        "exigido, ou menos argumento aceito",
    "parametro-renomeado":
        "a chamada com nome existe nesta linguagem, então o nome do "
        "parâmetro é parte do contrato e não só a posição",
    "tipo-de-parametro":
        "o tipo declarado de um parâmetro mudou; quem passava o tipo "
        "antigo passa a ser recusado pelo 'check'",
    "retorno-trocado":
        "o tipo de retorno mudou, e ele ATRAVESSA a fronteira do "
        "'adopt': quem usava o valor perde a conferência ou é acusado",
    "campo-novo-em-record":
        "um campo foi acrescentado a um record. Quebra SE ele nao tiver "
        "valor padrao — e a superficie nao carrega padroes, entao esta e "
        "uma decisao que so quem escreveu pode tomar",
    "campo-removido":
        "um campo que existia sumiu; todo acesso a ele passa a ser erro",
    "simbolo-novo":
        "um nome novo foi exportado: ninguém depende dele ainda, e nada "
        "quebra",
    "parametro-opcional-novo":
        "um parâmetro com valor padrão foi acrescentado; quem chamava "
        "com os antigos continua chamando igual",
    "campo-novo-opcional":
        "um campo com padrão foi acrescentado a um blueprint, e a "
        "construção antiga continua valendo",
}

#: Que veredito cada tipo força. 'maior' vence 'menor', que vence
#: 'correcao' — é a ordem do semver, e ela não é negociável.
_PESO = {"correcao": 0, "menor": 1, "maior": 2}
_QUEBRAS = {
    "simbolo-removido", "especie-trocada", "aridade-incompativel",
    "parametro-renomeado", "tipo-de-parametro", "retorno-trocado",
    "campo-removido",
}

#: O que a superficie NAO consegue decidir sozinha. Nao reprova por
#: padrao — um falso alarme aqui reprovaria um release correto —, e
#: aparece em destaque no relatorio. `--estrito` o trata como quebra.
_ATENCAO = {"campo-novo-em-record"}

_DICAS = {
    "simbolo-removido":
        "mantenha o nome como casca que chama o novo, ou suba a versão maior",
    "especie-trocada":
        "publique o novo com outro nome, e deixe o antigo por um ciclo",
    "aridade-incompativel":
        "dê valor padrão ao parâmetro novo, e a mudança vira compatível",
    "parametro-renomeado":
        "volte o nome antigo; se ele estava errado, troque na versão maior",
    "tipo-de-parametro":
        "aceite os dois tipos por um ciclo, ou suba a versão maior",
    "retorno-trocado":
        "devolva o tipo antigo, ou suba a versão maior",
    "campo-novo-em-record":
        "se o campo tem valor padrão, é compatível; se não tem, dê um — "
        "ou suba a versão maior",
    "campo-removido":
        "mantenha o campo com um valor de compatibilidade por um ciclo",
}


def _ler(caminho):
    """A superfície de um arquivo, com o motivo quando não dá."""
    try:
        superf = _superficie.de_arquivo(str(caminho))
    except Exception as erro:                   # pragma: no cover
        return None, f"não consegui ler '{caminho}': {erro}"
    if superf is None:
        return None, f"'{caminho}' não existe ou não é um .df"
    if superf.aberta:
        return None, (superf.motivo
                      or f"'{caminho}' não compila, então a superfície "
                         f"dele não se conhece")
    return superf, ""


def _como_dado(membro):
    return {
        "nome": membro.nome,
        "especie": membro.especie,
        "minimo": membro.minimo,
        "maximo": membro.maximo,
        "parametros": list(membro.parametros or ()),
        "tipos": dict(membro.tipos or {}),
        "retorno": membro.retorno or "",
        "campos": sorted(membro.campos or ()),
        "linha": membro.linha,
    }


def superficie(caminho):
    """O contrato público de um `.df`, como vault.

    Respeita o `relay`: um módulo que declara o que exporta está dizendo
    que o resto é interno, e o que é interno **não é contrato**.
    """
    superf, motivo = _ler(caminho)
    if superf is None:
        raise RuntimeError_(motivo, doc="abi/superficie")
    return {nome: _como_dado(superf.obter(nome)) for nome in superf.nomes()}


# ── a comparação ──────────────────────────────────────────────

def _achado(tipo, nome, **extra):
    achado = {"tipo": tipo, "nome": nome,
              "explica": REGRAS.get(tipo, ""),
              "dica": _DICAS.get(tipo, "nada a fazer: é compatível")}
    achado.update(extra)
    return achado


def _comparar_membro(nome, antes, depois, quebras, compativeis, atencao):
    if antes["especie"] != depois["especie"]:
        quebras.append(_achado("especie-trocada", nome,
                               antes=antes["especie"],
                               depois=depois["especie"]))
        return

    # Num record a aridade É a lista de campos: compará-la além dos
    # campos contaria a mesma mudança duas vezes, e com dois nomes
    # diferentes — foi o que a primeira versão fez.
    if antes["especie"] != "record":
        _comparar_aridade(nome, antes, depois, quebras, compativeis)

    _comparar_assinatura(nome, antes, depois, quebras)

    sumidos = set(antes["campos"]) - set(depois["campos"])
    if sumidos:
        quebras.append(_achado("campo-removido", nome,
                               campos=sorted(sumidos)))
    ganhos = set(depois["campos"]) - set(antes["campos"])
    if ganhos:
        if antes["especie"] == "record":
            atencao.append(_achado("campo-novo-em-record", nome,
                                   campos=sorted(ganhos)))
        else:
            compativeis.append(_achado("campo-novo-opcional", nome,
                                       campos=sorted(ganhos)))


def _comparar_aridade(nome, antes, depois, quebras, compativeis):
    """O que era chamável tem de continuar sendo."""
    if depois["minimo"] > antes["minimo"] or \
            (antes["maximo"] is not None and depois["maximo"] is not None
             and depois["maximo"] < antes["maximo"]) or \
            (antes["maximo"] is None and depois["maximo"] is not None):
        quebras.append(_achado(
            "aridade-incompativel", nome,
            antes=f"{antes['minimo']}..{_texto_max(antes['maximo'])}",
            depois=f"{depois['minimo']}..{_texto_max(depois['maximo'])}"))
    elif (depois["maximo"] is None and antes["maximo"] is not None) or \
            (antes["maximo"] is not None and depois["maximo"] is not None
             and depois["maximo"] > antes["maximo"]):
        compativeis.append(_achado(
            "parametro-opcional-novo", nome,
            antes=f"{antes['minimo']}..{_texto_max(antes['maximo'])}",
            depois=f"{depois['minimo']}..{_texto_max(depois['maximo'])}"))


def _comparar_assinatura(nome, antes, depois, quebras):
    """Nome de parâmetro, tipo e retorno — os três são contrato."""
    # A chamada com nome existe nesta linguagem, então o NOME do
    # parâmetro é contrato, e não só a posição.
    antigos, novos = antes["parametros"], depois["parametros"]
    for posicao, velho in enumerate(antigos):
        if posicao < len(novos) and novos[posicao] != velho:
            quebras.append(_achado("parametro-renomeado", nome,
                                   posicao=posicao, antes=velho,
                                   depois=novos[posicao]))

    for parametro, tipo in (antes["tipos"] or {}).items():
        agora = (depois["tipos"] or {}).get(parametro)
        if agora is not None and agora != tipo:
            quebras.append(_achado("tipo-de-parametro", nome,
                                   parametro=parametro, antes=tipo,
                                   depois=agora))

    if antes["retorno"] and depois["retorno"] != antes["retorno"]:
        quebras.append(_achado("retorno-trocado", nome,
                               antes=antes["retorno"],
                               depois=depois["retorno"] or "(nenhum)"))


def _texto_max(valor):
    return "∞" if valor is None else str(valor)


def comparar(antes, depois):
    """O que mudou entre duas versões do mesmo módulo, e o que isso exige."""
    um, motivo_um = _ler(antes)
    outro, motivo_dois = _ler(depois)
    if um is None or outro is None:
        return {
            "veredito": "desconhecido",
            "motivo": motivo_um or motivo_dois,
            "quebras": [], "compativeis": [], "atencao": [],
            "antes": str(antes), "depois": str(depois),
        }

    velhos = {n: _como_dado(um.obter(n)) for n in um.nomes()}
    novos = {n: _como_dado(outro.obter(n)) for n in outro.nomes()}
    quebras, compativeis, atencao = [], [], []

    for nome, membro in sorted(velhos.items()):
        if nome not in novos:
            quebras.append(_achado("simbolo-removido", nome,
                                   especie=membro["especie"],
                                   linha=membro["linha"]))
            continue
        _comparar_membro(nome, membro, novos[nome], quebras, compativeis,
                         atencao)

    for nome in sorted(set(novos) - set(velhos)):
        compativeis.append(_achado("simbolo-novo", nome,
                                   especie=novos[nome]["especie"],
                                   linha=novos[nome]["linha"]))

    if quebras:
        veredito = "maior"
    elif compativeis:
        veredito = "menor"
    else:
        veredito = "correcao"

    return {
        "veredito": veredito,
        "motivo": "",
        "quebras": quebras,
        "compativeis": compativeis,
        "atencao": atencao,
        "antes": str(antes),
        "depois": str(depois),
        "simbolos_antes": len(velhos),
        "simbolos_depois": len(novos),
    }


def quebras(antes, depois):
    """Só o que quebra — o que o CI precisa saber."""
    return comparar(antes, depois)["quebras"]


def veredito(antes, depois):
    """`maior`, `menor`, `correcao` — ou `desconhecido`."""
    return comparar(antes, depois)["veredito"]


def compativel(antes, depois):
    """A versão nova serve para quem usava a antiga?"""
    return comparar(antes, depois)["veredito"] in ("correcao", "menor")


def regras():
    """As regras de compatibilidade, com o que cada uma significa."""
    return dict(REGRAS)


def _versao(texto):
    import re
    casou = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", str(texto).strip())
    if not casou:
        raise RuntimeError_(
            f"'{texto}' nao e uma versao X.Y.Z.",
            nota="pre-lancamento (1.0.0-rc.1) e metadado (+build) ficam de "
                 "fora: a proxima versao de um rc e decisao de quem lanca",
            dica='Abi.proxima_versao("1.4.2", antes, depois)',
            doc="abi/versao")
    return tuple(int(g) for g in casou.groups())


def proxima_versao(atual, antes, depois):
    """A versao que o release deve ter, calculada — e nao escolhida a olho.

    `{atual, proxima, veredito, porque}`. Antes do 1.0 vale a convencao
    do Cargo e do npm: **quebra sobe o MENOR** (0.4 → 0.5) e acrescimo
    sobe a correcao, porque o 0.x anuncia que a API ainda nao assentou —
    e pular para 1.0 por causa de uma quebra seria prometer estabilidade
    sem querer.
    """
    maior, menor, correcao = _versao(atual)
    resultado = comparar(antes, depois)
    veredito_ = resultado["veredito"]
    if veredito_ == "desconhecido":
        return {"atual": str(atual), "proxima": None, "veredito": veredito_,
                "porque": resultado["motivo"]}
    if maior == 0:
        if veredito_ == "maior":
            nova = (0, menor + 1, 0)
        else:
            nova = (0, menor, correcao + 1)
    elif veredito_ == "maior":
        nova = (maior + 1, 0, 0)
    elif veredito_ == "menor":
        nova = (maior, menor + 1, 0)
    else:
        nova = (maior, menor, correcao + 1)
    quantos = {"maior": len(resultado["quebras"]),
               "menor": len(resultado["compativeis"]),
               "correcao": 0}[veredito_]
    porque = {
        "maior": f"{quantos} quebra(s) de contrato",
        "menor": f"{quantos} acrescimo(s) compativel(is)",
        "correcao": "a superficie nao mudou",
    }[veredito_]
    return {"atual": str(atual), "proxima": ".".join(map(str, nova)),
            "veredito": veredito_, "porque": porque}


def changelog(antes, depois, versao=""):
    """A secao do CHANGELOG que a superficie consegue escrever.

    So o que e **visivel de fora**: simbolo novo, removido, parametro
    trocado. O porque de cada mudanca continua sendo trabalho de quem
    escreveu — o texto aqui e o esqueleto, e nao a nota inteira.
    """
    r = comparar(antes, depois)
    titulo = f"## {versao}" if versao else "## Nao lancado"
    if r["veredito"] == "desconhecido":
        return f"{titulo}\n\nNao foi possivel comparar: {r['motivo']}\n"
    partes = [titulo, ""]

    def item(a):
        extra = ""
        if a.get("campos"):
            extra = " (" + ", ".join(a["campos"]) + ")"
        elif a.get("antes") is not None and a.get("depois") is not None:
            extra = f" ({a['antes']} → {a['depois']})"
        return f"- `{a['nome']}`: {a['explica'] or a['tipo']}{extra}"

    if r["quebras"]:
        partes += ["### Quebra compatibilidade", ""]
        partes += [item(a) + f" — {a['dica']}" for a in r["quebras"]]
        partes.append("")
    if r["compativeis"]:
        partes += ["### Adicionado", ""]
        partes += [item(a) for a in r["compativeis"]]
        partes.append("")
    if r["atencao"]:
        partes += ["### Confira", ""]
        partes += [item(a) for a in r["atencao"]]
        partes.append("")
    if len(partes) == 2:
        partes += ["Nenhuma mudanca na superficie publica.", ""]
    return "\n".join(partes)


def relatorio(resultado):
    """O veredito escrito, com cada quebra e o que fazer."""
    if resultado["veredito"] == "desconhecido":
        return (f"  nao da para julgar: {resultado['motivo']}\n"
                f"  (uma superficie que nao compila nao e comparada — um "
                f"falso alarme aqui reprovaria um release correto)")

    linhas = [f"  {resultado['antes']}  →  {resultado['depois']}", ""]
    if resultado["quebras"]:
        linhas.append(f"  {len(resultado['quebras'])} QUEBRA(S):")
        for q in resultado["quebras"]:
            linhas.append(f"   ✗ {q['nome']}  [{q['tipo']}]")
            linhas.append(f"      {q['explica']}")
            if "antes" in q:
                linhas.append(f"      antes: {q['antes']}   "
                              f"depois: {q['depois']}")
            linhas.append(f"      → {q['dica']}")
        linhas.append("")
    if resultado.get("atencao"):
        linhas.append(f"  {len(resultado['atencao'])} ponto(s) que a "
                      f"superficie NAO decide sozinha:")
        for a in resultado["atencao"]:
            linhas.append(f"   ? {a['nome']}  [{a['tipo']}]")
            linhas.append(f"      {a['explica']}")
            linhas.append(f"      → {a['dica']}")
        linhas.append("")
    if resultado["compativeis"]:
        linhas.append(f"  {len(resultado['compativeis'])} acrescimo(s) "
                      f"compativel(is):")
        for c in resultado["compativeis"]:
            linhas.append(f"   + {c['nome']}  [{c['tipo']}]")
        linhas.append("")
    linhas.append(f"  veredito: versao {resultado['veredito'].upper()}")
    return "\n".join(linhas)


# ── o mapa de símbolos ────────────────────────────────────────

def mapa(caminho):
    """De onde vem cada nome — o análogo do mapa que um ligador escreve.

    Num projeto de duzentos arquivos, "de onde vem este nome?" é a
    pergunta que mais custa a responder à mão. O ligador de uma
    linguagem compilada escreve isso num arquivo de mapa; aqui ele sai
    do mesmo caminho que o `check` usa.
    """
    import os

    from .. import ast_nodes as ast
    from .. import hir as _hir
    from ..builtins import get_builtins
    from ..lexer import tokenize
    from ..parser import parse

    alvo = str(caminho)
    if not os.path.isfile(alvo):
        raise RuntimeError_(f"'{alvo}' não existe.", doc="abi/simbolos")
    fonte = open(alvo, encoding="utf-8").read()
    try:
        arvore = parse(tokenize(fonte, alvo), alvo)
    except Exception as erro:
        raise RuntimeError_(f"'{alvo}' não compila: {erro}",
                            doc="abi/simbolos")

    modulos = {}
    for no in _hir._percorrer(arvore):
        if isinstance(no, ast.AdoptStatement):
            apelido = getattr(no, "alias", "") or no.module.split(".")[-1]
            modulos[apelido] = (no.module, no.line)
            for nome, como in (getattr(no, "selection", None) or ()):
                modulos[como or nome] = (f"{no.module}.{nome}", no.line)

    locais = {}
    for no in arvore.body:
        nome = getattr(no, "name", "")
        if nome:
            locais[nome] = getattr(no, "line", 0)
        if isinstance(no, ast.Assignment) and isinstance(no.target,
                                                         ast.Identifier):
            locais.setdefault(no.target.name, no.line)
        elif isinstance(no, ast.SteadyDeclaration):
            locais.setdefault(no.name, no.line)

    embutidos = set(get_builtins())
    vistos = {}
    for no in _hir._percorrer(arvore):
        if isinstance(no, ast.Identifier):
            vistos.setdefault(no.name, no.line)
        elif isinstance(no, ast.MemberAccess) and isinstance(no.object,
                                                             ast.Identifier):
            vistos.setdefault(no.object.name, no.line)

    saida = []
    for nome in sorted(set(vistos) | set(modulos) | set(locais)):
        if nome in modulos:
            origem, de, linha = "modulo", modulos[nome][0], modulos[nome][1]
        elif nome in locais:
            origem, de, linha = "local", alvo, locais[nome]
        elif nome in embutidos:
            origem, de, linha = "embutido", "builtins", vistos.get(nome, 0)
        elif nome in ("self", "this", "root", "error", "outcome"):
            continue                        # ligados pelo contexto
        else:
            origem, de, linha = "desconhecido", "", vistos.get(nome, 0)
        saida.append({"nome": nome, "origem": origem, "de": de,
                      "linha": linha})
    return saida


class ArcaneAbi:
    """O dicionário que `adopt Arcane.Abi` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Abi",
            "superficie": superficie,
            "comparar": comparar,
            "quebras": quebras,
            "veredito": veredito,
            "compativel": compativel,
            "regras": regras,
            "relatorio": relatorio,
            "mapa": mapa,
            "proxima_versao": proxima_versao,
            "changelog": changelog,
        }
