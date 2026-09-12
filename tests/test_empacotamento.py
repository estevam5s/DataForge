"""O que entra no wheel.

Este arquivo existe por causa de um bug que passou despercebido por
versões: **a extensão do VS Code não entrava no pacote**. Os globs de
`package-data` viviam sob a chave `dataforge` e eram relativos à pasta
do pacote — `dataforge/editor/vscode/*`, que não existe; a extensão mora
em `editor/vscode/` na raiz.

O resultado era silencioso e total: o wheel saía com **zero** arquivo da
extensão, e `dataforge editor` instalado por pip respondia "os arquivos
da extensao nao foram encontrados". Tudo que a extensão faz — cores,
snippets, LSP, depurador, os comandos — não chegava a ninguém que
instalasse pela forma recomendada.

Nenhum teste podia pegar isso sem **construir o wheel**. É o que estes
testes fazem: a caixa que o usuário recebe é a única fonte de verdade
sobre o que ele recebe.
"""

import glob
import os
import subprocess
import sys
import zipfile

import pytest

sys.path.insert(0, ".")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════
#  A lista explícita de pacotes não pode envelhecer
# ═══════════════════════════════════════════════════════════

def _pyproject():
    caminho = os.path.join(RAIZ, "pyproject.toml")
    try:
        import tomllib
    except ImportError:                                 # 3.10
        pytest.skip("tomllib só existe a partir do 3.11")
    with open(caminho, "rb") as f:
        return tomllib.load(f)


def test_a_lista_de_pacotes_tem_todos_os_subpacotes_do_disco():
    """A lista é explícita — 'find' não acha `dataforge.editor`, que
    mora fora da pasta do pacote.

    O preço de uma lista explícita é envelhecer: um subpacote novo fica
    fora do wheel, e o sintoma é um `ImportError` que só aparece na
    instalação por pip, nunca no repositório.
    """
    declarados = set(_pyproject()["tool"]["setuptools"]["packages"])
    no_disco = {
        os.path.relpath(os.path.dirname(p), RAIZ).replace(os.sep, ".")
        for p in glob.glob(os.path.join(RAIZ, "dataforge", "**",
                                        "__init__.py"), recursive=True)
    }
    faltando = sorted(no_disco - declarados)
    assert not faltando, (
        f"subpacote(s) fora do wheel: {faltando} — acrescente a "
        f"'packages' em pyproject.toml")


def test_nenhum_pacote_declarado_deixou_de_existir():
    declarados = set(_pyproject()["tool"]["setuptools"]["packages"])
    mapa = _pyproject()["tool"]["setuptools"].get("package-dir", {})
    for nome in declarados:
        if nome in mapa:
            caminho = os.path.join(RAIZ, mapa[nome])
        else:
            caminho = os.path.join(RAIZ, nome.replace(".", os.sep))
        assert os.path.isdir(caminho), f"'{nome}' não existe em {caminho}"


# ═══════════════════════════════════════════════════════════
#  O wheel de verdade
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def wheel(tmp_path_factory):
    """Constrói o wheel. É lento, e é o único jeito de saber."""
    try:
        import build                                    # noqa: F401
    except ImportError:
        pytest.skip("o módulo 'build' não está instalado")

    destino = tmp_path_factory.mktemp("wheel")
    r = subprocess.run([sys.executable, "-m", "build", "--wheel",
                        "-o", str(destino)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ)
    assert r.returncode == 0, r.stdout + r.stderr
    achados = glob.glob(os.path.join(str(destino), "*.whl"))
    assert achados, "nenhum .whl foi produzido"
    with zipfile.ZipFile(achados[0]) as z:
        return set(z.namelist())


def test_o_interpretador_inteiro_entra(wheel):
    """Todo módulo de `dataforge/` tem de estar lá.

    Um que falte não dá erro no repositório — o `sys.path` acha o
    arquivo local. Só quebra para quem instalou.
    """
    faltando = []
    for caminho in glob.glob(os.path.join(RAIZ, "dataforge", "**", "*.py"),
                             recursive=True):
        relativo = os.path.relpath(caminho, RAIZ).replace(os.sep, "/")
        if "/editor/" in relativo:
            continue
        if relativo not in wheel:
            faltando.append(relativo)
    assert not faltando, f"fora do wheel: {sorted(faltando)[:10]}"


def test_a_extensao_do_vscode_entra_no_wheel(wheel):
    """O bug que este arquivo existe para não deixar voltar."""
    da_extensao = [n for n in wheel if "editor/vscode" in n]
    assert len(da_extensao) > 100, (
        f"só {len(da_extensao)} arquivo(s) da extensão no wheel — "
        f"'dataforge editor' vai dizer que não os encontrou")


@pytest.mark.parametrize("arquivo, porque", [
    ("dataforge/editor/vscode/package.json",
     "é o manifesto: sem ele o editor não reconhece a extensão"),
    ("dataforge/editor/vscode/out/extension.js",
     "é o JavaScript compilado: sem ele a extensão instala e não ativa"),
    ("dataforge/editor/vscode/out/depuracao.js",
     "é o provedor de depuração: sem ele o F5 não acha o adaptador"),
    ("dataforge/editor/vscode/out/servidor.js",
     "é o cliente do LSP"),
    ("dataforge/editor/vscode/syntaxes/dataforge.tmLanguage.json",
     "é a gramática das cores"),
    ("dataforge/editor/vscode/language-configuration.json",
     "é a indentação e a dobra de blocos"),
    ("dataforge/editor/vscode/icone.png",
     "é o ícone da extensão"),
])
def test_a_peca_da_extensao_esta_no_wheel(wheel, arquivo, porque):
    assert arquivo in wheel, f"'{arquivo}' não entrou, e {porque}"


def test_o_cliente_lsp_entra_com_a_biblioteca_dele(wheel):
    """Ele vive fundo em `node_modules/<pacote>/lib/...`, e um glob de
    dois níveis para antes. Sem esta parte, o servidor de linguagem não
    subia em NENHUMA instalação por pip — só na cópia de
    desenvolvimento que tinha rodado `npm install`."""
    biblioteca = [n for n in wheel
                  if "node_modules/vscode-languageclient" in n]
    assert biblioteca, "a extensão entrou sem a biblioteca que ela carrega"


def test_todo_snippet_entra(wheel):
    locais = glob.glob(os.path.join(RAIZ, "editor", "vscode", "snippets",
                                    "*.json"))
    assert locais
    for caminho in locais:
        nome = os.path.basename(caminho)
        assert f"dataforge/editor/vscode/snippets/{nome}" in wheel, nome


# ═══════════════════════════════════════════════════════════
#  O comando que depende disso
# ═══════════════════════════════════════════════════════════

def test_a_extensao_e_encontrada_pelo_caminho_que_o_comando_procura():
    """`_origem_da_extensao` olha dois lugares: dentro do pacote (a
    instalação) e um nível acima (o repositório). O segundo é o que vale
    aqui; o primeiro é coberto pelos testes do wheel."""
    from dataforge.cli import _origem_da_extensao

    origem = _origem_da_extensao()
    assert origem is not None
    assert os.path.isfile(os.path.join(origem, "package.json"))


def test_o_comando_editor_lista_o_que_realmente_instala():
    """A mensagem dizia apenas "cores, snippets, indentação e dobra".

    Ela foi escrita quando a extensão era só uma gramática. Hoje ela
    traz LSP, depurador e dezenas de comandos, e prometer menos do que
    se entrega faz a pessoa não procurar o que está lá.
    """
    import inspect

    from dataforge import cli

    fonte = inspect.getsource(cli.editor_command)
    for palavra in ("erro", "depura", "comando"):
        assert palavra in fonte.lower(), (
            f"a mensagem de 'dataforge editor' não menciona '{palavra}'")
