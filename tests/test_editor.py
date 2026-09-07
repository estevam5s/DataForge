"""
Testes da extensao do VS Code.

A gramatica e gerada de tokens.py por tools/gerar_gramatica.py. Estes
testes garantem que ela nao fique atrasada em relacao a linguagem — foi
exatamente o que aconteceu com a versao 3.0, que nao conhecia 'record'
nem 'enum'.
"""

import json
import os
import re
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.tokens import (  # noqa: E402
    CONTEXTUAIS_BLUEPRINT, CONTEXTUAIS_KILN, KEYWORDS,
)

EXTENSAO = os.path.join(RAIZ, "editor", "vscode")


def carregar(*partes):
    with open(os.path.join(EXTENSAO, *partes), encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def gramatica():
    return carregar("syntaxes", "dataforge.tmLanguage.json")


# ── A extensao esta completa ─────────────────────────────────

@pytest.mark.parametrize("arquivo", [
    ("package.json",),
    ("language-configuration.json",),
    ("syntaxes", "dataforge.tmLanguage.json"),
    ("snippets", "dataforge.json"),
])
def test_arquivo_existe_e_e_json_valido(arquivo):
    assert carregar(*arquivo)


def test_manifesto_declara_a_extensao_df():
    pkg = carregar("package.json")
    lingua = pkg["contributes"]["languages"][0]
    assert lingua["id"] == "dataforge"
    assert ".df" in lingua["extensions"]


def test_manifesto_aponta_para_arquivos_que_existem():
    pkg = carregar("package.json")
    caminhos = [pkg["contributes"]["languages"][0]["configuration"],
                pkg["contributes"]["grammars"][0]["path"],
                pkg["contributes"]["snippets"][0]["path"],
                pkg["icon"]]
    for relativo in caminhos:
        alvo = os.path.join(EXTENSAO, relativo.lstrip("./"))
        assert os.path.isfile(alvo), f"{relativo} nao existe"


def test_manifesto_forca_espacos_na_indentacao():
    """Tab e SyncError na linguagem; o editor precisa cooperar."""
    padroes = carregar("package.json")["contributes"] \
        ["configurationDefaults"]["[dataforge]"]
    assert padroes["editor.insertSpaces"] is True
    assert padroes["editor.tabSize"] == 4
    assert padroes["editor.detectIndentation"] is False


def test_versao_do_manifesto_acompanha_a_da_linguagem():
    from dataforge import __version__
    pkg = carregar("package.json")
    assert pkg["version"].split(".")[:2] == __version__.split(".")[:2]


# ── Toda palavra reservada tem cor ───────────────────────────

def _palavras_da_gramatica(gramatica):
    """Extrai as palavras dos padroes \\b(a|b|c)\\b."""
    achadas = set()
    for regra in gramatica["repository"]["palavras"]["patterns"]:
        grupo = re.match(r"\\b\((.+)\)\\b$", regra["match"])
        if grupo:
            achadas.update(grupo.group(1).split("|"))
    return achadas


def test_toda_palavra_reservada_recebe_cor(gramatica):
    """Uma palavra sem cor passa despercebida: o codigo so fica cinza."""
    todas = set(KEYWORDS) | set(CONTEXTUAIS_BLUEPRINT) | set(CONTEXTUAIS_KILN)
    sem_cor = todas - _palavras_da_gramatica(gramatica)
    assert not sem_cor, (
        f"sem cor na gramatica: {sorted(sem_cor)} — "
        f"rode 'python3 tools/gerar_gramatica.py'")


def test_gramatica_nao_pinta_palavra_inexistente(gramatica):
    todas = set(KEYWORDS) | set(CONTEXTUAIS_BLUEPRINT) | set(CONTEXTUAIS_KILN)
    inventadas = _palavras_da_gramatica(gramatica) - todas
    assert not inventadas, f"a linguagem nao tem: {sorted(inventadas)}"


@pytest.mark.parametrize("palavra", sorted(CONTEXTUAIS_KILN))
def test_palavra_do_kiln_tem_cor(palavra, gramatica):
    assert palavra in _palavras_da_gramatica(gramatica)


@pytest.mark.parametrize("palavra", [
    "record", "enum", "trait", "match", "point", "spawn", "blueprint",
])
def test_palavras_que_a_versao_3_esquecia(palavra, gramatica):
    assert palavra in _palavras_da_gramatica(gramatica)


# ── A gramatica esta em dia ──────────────────────────────────

def test_gerador_produz_exatamente_o_arquivo_versionado(tmp_path):
    """Se falhar, alguem editou a gramatica a mao ou mudou tokens.py
    sem regerar. A correcao e rodar o gerador."""
    antes = open(os.path.join(EXTENSAO, "syntaxes",
                              "dataforge.tmLanguage.json"),
                 encoding="utf-8").read()
    resultado = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "tools", "gerar_gramatica.py")],
        capture_output=True, text=True, cwd=RAIZ)
    assert resultado.returncode == 0, resultado.stderr
    depois = open(os.path.join(EXTENSAO, "syntaxes",
                               "dataforge.tmLanguage.json"),
                  encoding="utf-8").read()
    assert antes == depois, (
        "a gramatica versionada difere da gerada — "
        "rode 'python3 tools/gerar_gramatica.py' e versione o resultado")


def test_todo_regex_da_gramatica_compila(gramatica):
    """Um regex torto nao da erro no VS Code: a regra so nunca casa."""
    def visitar(no):
        if isinstance(no, dict):
            for chave in ("match", "begin", "end"):
                if chave in no:
                    re.compile(no[chave])
            for valor in no.values():
                visitar(valor)
        elif isinstance(no, list):
            for item in no:
                visitar(item)
    visitar(gramatica)


# ── Snippets ─────────────────────────────────────────────────

def test_snippets_tem_prefixo_corpo_e_descricao():
    for nome, dados in carregar("snippets", "dataforge.json").items():
        assert dados.get("prefix"), f"{nome} sem prefixo"
        assert dados.get("body"), f"{nome} sem corpo"
        assert dados.get("description"), f"{nome} sem descricao"


def test_snippets_nao_repetem_prefixo():
    prefixos = [d["prefix"]
                for d in carregar("snippets", "dataforge.json").values()]
    repetidos = {p for p in prefixos if prefixos.count(p) > 1}
    assert not repetidos, f"prefixos repetidos: {repetidos}"


def test_snippets_usam_a_sintaxe_da_linguagem():
    """Um snippet que nao roda ensina errado."""
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    snippets = carregar("snippets", "dataforge.json")
    for nome, dados in snippets.items():
        fonte = "\n".join(dados["body"])
        # tira os marcadores do VS Code: ${1:x}, ${1|a,b|}, $0
        fonte = re.sub(r"\$\{\d+\|([^,|]+)[^}]*\}", r"\1", fonte)
        fonte = re.sub(r"\$\{\d+:([^}]*)\}", r"\1", fonte)
        fonte = re.sub(r"\$\{?\d+\}?", "", fonte)
        fonte = fonte.replace("\t", "    ")
        # Onde o snippet deixa o lugar do usuario — o cursor final ($0)
        # numa linha propria, ou um '...' de marcador — poe-se algo
        # inocente: para o parser, um corpo vazio e erro de sintaxe.
        fonte = "\n".join(
            (linha[:len(linha) - len(linha.lstrip())] + "out 1")
            if linha.startswith(" ") and linha.strip() in ("", "...")
            else linha
            for linha in fonte.split("\n"))
        # 'route', 'respond' e 'render' sao contextuais: valem dentro de
        # um bloco 'server'. Um snippet desses e um fragmento, e e assim
        # que ele sera usado.
        if fonte.lstrip().startswith(("route ", "respond ", "render ")):
            recuado = "\n".join("    " + l for l in fonte.split("\n"))
            fonte = 'server s on 0:\n' + recuado

        try:
            parse(tokenize(fonte))
        except Exception as erro:
            pytest.fail(f"o snippet '{nome}' nao e DataForge valido: {erro}\n"
                        f"---\n{fonte}\n---")


# ── Empacotamento ────────────────────────────────────────────

def test_extensao_entra_no_tarball_que_o_site_serve():
    """Sem isto, 'dataforge editor' falharia em quem instalou por curl."""
    import importlib.util
    caminho = os.path.join(RAIZ, "scripts", "gerar_tarball.py")
    spec = importlib.util.spec_from_file_location("gerar_tarball", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    destinos = [dentro for _, dentro in modulo.EMBUTIR]
    assert "dataforge/editor/vscode" in destinos


def test_pyproject_empacota_os_arquivos_da_extensao():
    conteudo = open(os.path.join(RAIZ, "pyproject.toml"),
                    encoding="utf-8").read()
    assert "editor/vscode/*" in conteudo
    assert "editor/vscode/*/*" in conteudo      # snippets/ e syntaxes/


def test_o_comando_editor_esta_na_ajuda():
    from dataforge.cli import COMANDOS
    assert "editor" in COMANDOS


# ── O destacador do site acompanha a linguagem ───────────────

SITE_HIGHLIGHT = os.path.join(RAIZ, "site", "lib", "highlight.ts")


def _palavras_do_site():
    """Tudo o que o destacador do site pinta.

    Sao tres conjuntos: KEYWORDS, LITERALS ('yes', 'no', 'void') e
    DECLARATIONS. Uma palavra em qualquer um deles ganha cor.
    """
    fonte = open(SITE_HIGHLIGHT, encoding="utf-8").read()
    achadas = set()
    for nome in ("KEYWORDS", "LITERALS", "DECLARATIONS"):
        inicio = fonte.index(f"const {nome} = new Set([")
        fim = fonte.index("]);", inicio)
        # tira os comentarios antes de ler as strings
        trecho = re.sub(r"//[^\n]*", "", fonte[inicio:fim])
        achadas.update(re.findall(r"'([a-z_]+)'", trecho))
    return achadas


@pytest.mark.skipif(not os.path.isfile(SITE_HIGHLIGHT),
                    reason="o site nao esta neste checkout")
def test_o_destacador_do_site_conhece_toda_palavra_reservada():
    """Uma palavra que o site nao conhece aparece cinza na doc — e o
    exemplo deixa de ensinar justamente o que veio ensinar."""
    todas = set(KEYWORDS) | set(CONTEXTUAIS_KILN)
    faltando = todas - _palavras_do_site()
    assert not faltando, (
        f"site/lib/highlight.ts nao colore: {sorted(faltando)}")


@pytest.mark.skipif(not os.path.isfile(SITE_HIGHLIGHT),
                    reason="o site nao esta neste checkout")
def test_o_destacador_do_site_nao_inventa_palavra():
    todas = (set(KEYWORDS) | set(CONTEXTUAIS_KILN)
             | set(CONTEXTUAIS_BLUEPRINT))
    inventadas = _palavras_do_site() - todas
    assert not inventadas, f"a linguagem nao tem: {sorted(inventadas)}"
