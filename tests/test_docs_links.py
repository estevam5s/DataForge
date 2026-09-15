"""Os links do hover apontam para páginas que existem.

Um link quebrado num cartão de hover é pior que nenhum link: ele gasta a
confiança de quem clicou, e ninguém descobre até um usuário reclamar — o
editor não confere destino, e a doc muda sem avisar quem a referencia.

Estes testes comparam a tabela de `dataforge/docs_links.py` com
`site/app/docs/`, que é a fonte de verdade. As duas listas escritas à mão
(`MODULOS_COM_PAGINA`, `COMANDOS_COM_PAGINA`) existem porque o LSP roda a
partir do wheel instalado, onde não há pasta `site/` — o preço de uma
lista à mão é envelhecer, e é isso que estes testes cobram.
"""

import glob
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import docs_links as dl                       # noqa: E402
from dataforge.exemplos_palavras import PALAVRAS             # noqa: E402
from dataforge.stdlib.catalogo import DESCRICOES             # noqa: E402


def _paginas_do_site():
    """Todo caminho de `/docs` que tem um `page.tsx`."""
    raiz = os.path.join(RAIZ, "site", "app", "docs")
    saida = set()
    for caminho in glob.glob(os.path.join(raiz, "**", "page.tsx"),
                             recursive=True):
        relativo = os.path.relpath(os.path.dirname(caminho), raiz)
        saida.add("" if relativo == "." else relativo.replace(os.sep, "/"))
    return saida


@pytest.fixture(scope="module")
def paginas():
    achadas = _paginas_do_site()
    if not achadas:
        pytest.skip("a pasta do site nao esta neste checkout")
    return achadas


# ── A tabela de palavras ───────────────────────────────────

def test_toda_pagina_de_palavra_existe(paginas):
    quebrados = sorted({
        f"{palavra} -> /docs/{pagina}"
        for palavra, pagina in dl.PAGINA_DE_PALAVRA.items()
        if pagina not in paginas})
    assert not quebrados, (
        "o hover manda para pagina que nao existe:\n  "
        + "\n  ".join(quebrados))


def test_toda_palavra_com_ficha_tem_para_onde_ir():
    """Uma palavra que o hover explica e não deixa ler é meio caminho.

    A cobertura é cobrada contra `PALAVRAS`, que é a tabela do hover: se
    uma palavra nova ganha ficha e não ganha destino, este teste avisa
    antes de alguém notar o cartão sem link.
    """
    sem_destino = sorted(set(PALAVRAS) - set(dl.PAGINA_DE_PALAVRA))
    assert not sem_destino, (
        f"palavras com ficha e sem link: {sem_destino}\n"
        "  acrescente em 'dataforge/docs_links.py'")


def test_nenhuma_palavra_sobra_na_tabela_de_links():
    """Um destino para algo que não é palavra da linguagem é ruído."""
    sobrando = sorted(set(dl.PAGINA_DE_PALAVRA) - set(PALAVRAS))
    assert not sobrando, f"links para o que nao e palavra: {sobrando}"


# ── Os módulos ─────────────────────────────────────────────

def test_a_lista_de_modulos_com_pagina_esta_em_dia(paginas):
    """A lista escrita à mão contra o disco."""
    no_disco = {p.split("/", 1)[1] for p in paginas
                if p.startswith("biblioteca/")}
    assert dl.MODULOS_COM_PAGINA == no_disco, (
        f"faltam na lista: {sorted(no_disco - dl.MODULOS_COM_PAGINA)}\n"
        f"sobram na lista: {sorted(dl.MODULOS_COM_PAGINA - no_disco)}")


def test_a_lista_de_comandos_com_pagina_esta_em_dia(paginas):
    no_disco = {p.split("/", 1)[1] for p in paginas if p.startswith("cli/")}
    assert dl.COMANDOS_COM_PAGINA == no_disco, (
        f"faltam na lista: {sorted(no_disco - dl.COMANDOS_COM_PAGINA)}\n"
        f"sobram na lista: {sorted(dl.COMANDOS_COM_PAGINA - no_disco)}")


def test_todo_modulo_da_stdlib_tem_para_onde_ir(paginas):
    """Inclusive os 19 sem página própria — eles caem no índice.

    Cair no índice é um destino honesto; inventar `biblioteca/malha`
    porque o padrão *parece* certo daria 404, e é justamente o erro que
    ninguém vê até alguém clicar.
    """
    quebrados = []
    for oficial in sorted(DESCRICOES):
        pagina = dl.pagina_de_modulo(oficial)
        if pagina not in paginas:
            quebrados.append(f"{oficial} -> /docs/{pagina}")
    assert not quebrados, quebrados


def test_as_paginas_proprias_existem(paginas):
    quebrados = [f"{m} -> /docs/{p}" for m, p in dl.PAGINA_PROPRIA.items()
                 if p not in paginas]
    assert not quebrados, quebrados


# ── A forma do link ────────────────────────────────────────

def test_a_url_nao_duplica_a_barra():
    assert dl.url("kiln").endswith("/docs/kiln")
    assert dl.url("/kiln").endswith("/docs/kiln")
    assert dl.url("") == dl.URL_BASE


def test_sem_destino_nao_ha_link():
    """Um link vazio no cartão é pior que a ausência dele."""
    assert dl.link_markdown(None) == ""
    assert dl.link_markdown("") == ""
    assert "](https://" in dl.link_markdown("kiln")


def test_o_dominio_do_link_e_o_que_responde():
    """`dataforge-lang.dev` não responde, e já esteve no repositório.

    Era o único lugar que citava aquele domínio, e todo canônico e todo
    Open Graph iam para um endereço inexistente.
    """
    assert "dataforge-lang.dev" not in dl.URL_BASE
    assert dl.URL_BASE.startswith("https://")
