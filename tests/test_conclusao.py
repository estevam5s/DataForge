"""`doc/conclusao.html` — o relatório do estado da linguagem.

Ele era escrito à mão, e envelheceu exatamente como este repositório
documenta que acontece: anunciava **48 módulos** onde há 86, **1.529
símbolos** onde há 2.308, a versão **1.0.0**, e listava como "falta"
quatro coisas que passaram a existir — watchpoint no depurador, sessão
da Vitrine fora do processo, fila com persistência e literal decimal.

Um relatório sobre o estado do projeto que descreve um estado que já não
é o do projeto é **pior que nenhum relatório**: ele é lido como verdade,
e cada número errado vira uma decisão errada.

Esta suíte cobra três coisas:

1. o arquivo **é o que o gerador produz** (a mesma trava da gramática do
   editor e das páginas de doc);
2. os números dele **batem com o código**, medidos agora;
3. o que ele diz que **não existe** vem de `Arcane.Ecossistema`, que é
   conferido contra o disco — e não de uma lista escrita na página.
"""
import json
import os
import re
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAIZ, "doc", "conclusao.html")
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "tools"))
sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))


@pytest.fixture(scope="module")
def html():
    with open(PAGINA, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def dados(html):
    """Os blocos `const NOME = […];` do `<script>`, como dado Python.

    Eles são emitidos com `json.dumps`, então JSON inválido aqui é uma
    página que não desenha nada no navegador — e uma página em branco
    não tem como ser notada por um teste que só olhe o tamanho.
    """
    marca = "não lembrados.\n   ═══════════════════════════════════════════════════════════════ */\n"
    bloco = html.split(marca, 1)[1].split("/* ═══", 1)[0]
    saida = {}
    for parte in re.split(r"^const ", bloco, flags=re.M):
        if not parte.strip():
            continue
        nome, resto = parte.split(" = ", 1)
        saida[nome] = json.loads(resto.rstrip().rstrip(";"))
    return saida


def test_a_pagina_e_o_que_o_gerador_produz():
    """A mesma trava da gramática do editor: o gerado não pode divergir.

    Editar o `.html` à mão funciona até alguém rodar o gerador — e aí a
    correção some sem nada explicando.
    """
    saida = subprocess.run([sys.executable, "tools/gerar_conclusao.py", "--check"],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    assert saida.returncode == 0, saida.stdout + saida.stderr


def test_o_arquivo_avisa_que_e_gerado(html):
    assert "GERADO por tools/gerar_conclusao.py" in html
    assert "Não edite este arquivo à mão" in html


def test_os_numeros_do_topo_batem_com_o_codigo(dados):
    """O defeito que matou a versão anterior, agora com trava."""
    from dataforge.stdlib import get_module, list_modules

    oficiais = {get_module(m)["__name__"] for m in list_modules()}
    simbolos = sum(len([k for k in get_module(n) if not k.startswith("__")])
                   for n in oficiais)

    n = dados["N"]
    assert n["modulos"] == len(oficiais)
    assert n["simbolos"] == simbolos

    rotulos = " ".join(f"{x['v']} {x['r']}" for x in dados["NUMEROS"])
    assert str(len(oficiais)) in rotulos, "o painel não cita o número de módulos"


def test_a_versao_e_a_de_agora(html):
    """Ela dizia 1.0.0 com a linguagem em 1.1.1."""
    from dataforge import __version__

    assert f"DataForge v{__version__}" in html


def test_os_exercicios_e_os_testes_sao_os_de_agora(dados):
    import glob

    with open(os.path.join(RAIZ, "site", "lib", "dados-gerados.json"),
              encoding="utf-8") as f:
        gerados = json.load(f)

    n = dados["N"]
    assert n["exercicios"] == sum(len(v) for v in gerados["exercicios"].values())
    assert n["testes"] == gerados["contagem"]["testes"]
    assert n["exemplos"] == len(glob.glob(os.path.join(RAIZ, "examples", "*.df")))


def test_o_que_nao_existe_vem_do_ECOSSISTEMA_e_nao_da_pagina(dados):
    """A lista de ausências é **lida do código**, e ele é conferido
    contra o disco. Escrita na página, ela mentiria no dia em que
    alguém implementasse um item — que foi o que aconteceu."""
    from dataforge.stdlib import get_module

    eco = get_module("Arcane.Ecossistema")
    fora = eco["o_que_nao_existe"]()
    assert len(dados["DECISAO"]) == len(fora)
    nomes = " ".join(linha[0] for linha in dados["DECISAO"])
    for no in fora:
        assert no["no"] in nomes, f"{no['no']} sumiu da página"


def test_a_pagina_nao_lista_como_falta_algo_que_existe(dados):
    """Os quatro casos concretos que a versão anterior errava."""
    texto = json.dumps(dados["CABE"], ensure_ascii=False).lower()
    proibidos = {
        "watchpoint": "a vigia de escrita existe (dataforge debug, w)",
        "literal decimal": "19.99d existe",
        "fila com persist": "Eventos.fila_persistente existe",
        "sessão da vitrine entre processos": "V.sessoes_em_banco existe",
    }
    for termo, porque in proibidos.items():
        assert termo not in texto, f"'{termo}' está listado como falta, e {porque}"


def test_os_principios_vem_do_modulo_com_o_veredito(dados):
    from dataforge.stdlib import get_module

    pr = get_module("Arcane.Principios")
    vivos = pr["principios"]()
    assert len(dados["PRINCIPIOS"]) == len(vivos) == 10
    for lido, vivo in zip(dados["PRINCIPIOS"], vivos):
        assert lido["v"] == vivo["veredito"]

    # E o veredito nao pode ser dez de dez: um relatorio que aprovasse
    # os dez seria a prova de que ninguem o leu.
    assert any(p["v"] != "cumprido" for p in dados["PRINCIPIOS"])


def test_as_areas_da_stdlib_saem_dos_MESMOS_grupos_da_landing(dados):
    """Uma terceira divisão do mesmo conjunto divergiria no primeiro
    módulo novo, e três telas passariam a discordar sobre onde ele mora."""
    from gerar_roadmap import GRUPOS_DE_MODULO

    rotulos = [linha[0] for linha in dados["AREAS_STDLIB"]]
    for rotulo, _ in GRUPOS_DE_MODULO:
        assert rotulo in rotulos, f"o grupo '{rotulo}' sumiu da conclusão"

    total = sum(int(linha[2]) for linha in dados["AREAS_STDLIB"])
    assert total == dados["N"]["simbolos"], (
        "a soma das áreas não fecha com o total — um módulo ficou fora")


def test_todo_bug_da_pagina_tem_familia_conhecida(dados):
    """A família é o filtro da tela: uma família nova sem botão deixa o
    bug invisível quando alguém filtra."""
    conhecidas = {"silencio", "nome", "mensagem", "classe", "dado"}
    for b in dados["BUGS"]:
        assert b["fam"] in conhecidas, b["t"]
        assert b["antes"] and b["depois"] and b["p"]


def test_nenhuma_dependencia_externa_na_pagina(html):
    """A linguagem promete zero dependência, e o relatório sobre ela não
    ia desmentir — nem com uma fonte remota.

    A busca é pelo que **carrega**, e não pela palavra: a própria página
    CITA a regra da Vitrine ("proibindo 'http://' … no CSS e no JS"), e
    um teste que procurasse o texto acusaria a frase que explica a
    proibição. É o mesmo formato do falso alarme que a varredura de
    segredo teve de aprender a calar.
    """
    for proibido in ("<script src", "<link rel=\"stylesheet\"", "@import",
                     "url(http", "src=\"http", "href=\"http"):
        assert proibido not in html, f"a página carrega algo de fora: {proibido}"


def test_a_pagina_abre_sem_javascript_quebrado(html):
    """As abas são montadas por JS; um `hidden` faltando deixaria duas
    seções visíveis ao mesmo tempo, e um id a mais deixaria uma aba
    apontando para nada."""
    ids = set(re.findall(r'<section id="([^"]+)" role="tabpanel"', html))
    marca = "não lembrados.\n   ═══════════════════════════════════════════════════════════════ */\n"
    bloco = html.split(marca, 1)[1].split("/* ═══", 1)[0]
    abas = json.loads(re.search(r"const ABAS = (\[.*?\]);", bloco, re.S).group(1))
    assert {a[0] for a in abas} == ids
    assert html.count('role="tabpanel" hidden') == len(ids) - 1
