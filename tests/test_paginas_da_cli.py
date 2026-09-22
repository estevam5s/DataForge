"""Todo `dataforge <x>` citado nas páginas da CLI e de DevOps existe.

Uma página que ensina um comando que não existe — ou uma opção que
foi renomeada — manda a pessoa digitar algo que responde *"comando
desconhecido"*. O índice e a referência da CLI saem do catálogo; as
páginas por tema são escritas à mão, e é nelas que isso apodrece.
"""
import os
import re
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))

from dataforge.cli import COMANDOS, GRUPOS  # noqa: E402

MODULOS = ["cli_avancado", "devops_avancado", "testes_avancado",
           "projetos_tipos", "modulos_avancado", "bibliotecas_avancado"]

_NOMES = set(COMANDOS) | {a for c in COMANDOS.values() for a in (c.apelidos or ())}
# Numa linha de comando: começo da linha (ou depois de '$ ', '&&', ';', '|').
_NO_CODIGO = re.compile(r"(?:^\s*(?:\$\s+)?|&&\s*|;\s*|\|\s*)(?:dataforge|df) ([a-z][a-z-]*)(?![a-z<-])", re.M)
# Num parágrafo: só dentro de crases — a prosa diz "o dataforge a cada tecla".
_NA_PROSA = re.compile(r"`(?:dataforge|df) ([a-z][a-z-]*)")


def _blocos(nome):
    mod = __import__(f"conteudo.{nome}", fromlist=["PAGINAS"])
    for p in mod.PAGINAS:
        for b in p["blocos"]:
            yield p["href"], b


@pytest.mark.parametrize("modulo", MODULOS)
def test_todo_comando_citado_existe(modulo):
    ruins = []
    for href, b in _blocos(modulo):
        achados = []
        if b.get("lang") in ("bash", "text", "yaml"):
            achados += _NO_CODIGO.findall(b.get("code", ""))
        for campo in ("p",):
            achados += _NA_PROSA.findall(b.get(campo, "") or "")
        ruins += [f"{href}: dataforge {n}" for n in achados if n not in _NOMES]
    assert not ruins, "comando que não existe:\n  " + "\n  ".join(sorted(set(ruins)))


def test_o_indice_da_cli_lista_todos_os_comandos_do_catalogo():
    from conteudo import cli_avancado
    indice = str(cli_avancado.PAGINAS[0]["blocos"])
    faltando = [c.nome for _g, cmds in GRUPOS for c in cmds if f"`{c.nome}`" not in indice]
    assert not faltando, faltando


def test_a_referencia_tem_uma_secao_por_comando():
    from conteudo import cli_avancado
    ref = cli_avancado.PAGINAS[1]
    assert ref["href"] == "/docs/cli/referencia"
    secoes = {b["h3"] for b in ref["blocos"] if "h3" in b}
    assert secoes == {c.nome for _g, cmds in GRUPOS for c in cmds}


def test_toda_pagina_citada_pelo_indice_da_cli_existe():
    from conteudo import cli_avancado
    paginas_geradas = set()
    for nome in MODULOS:
        mod = __import__(f"conteudo.{nome}", fromlist=["PAGINAS"])
        paginas_geradas |= {p["href"] for p in mod.PAGINAS}
    for href in set(cli_avancado.PAGINA_DE.values()):
        pasta = os.path.join(RAIZ, "site", "app", href.lstrip("/"))
        assert href in paginas_geradas or os.path.isfile(os.path.join(pasta, "page.tsx")), href
