"""`total := 0` numa ação, quando existe um `total` no topo do arquivo.

Dentro de uma ação, `:=` escreve o nome de FORA quando ele existe. É o
que faz `contador := contador + 1` atualizar a global — e é o que faz
`total := 0`, escrito como acumulador local, zerar a global de mesmo
nome, sem erro. Com os módulos isolados, a colisão só acontece dentro
de um arquivo, e é ali que o `check` avisa (`atribuicao-escreve-global`).

O que separa as duas intenções é a leitura: quem atualiza a global lê
antes de escrever; quem quer um local começa escrevendo.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, ".")

from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODIGO = "atribuicao-escreve-global"


def avisos(fonte):
    arvore = parse(tokenize(fonte, "t.df"), "t.df")
    return [d.line for d in check_program(arvore, "t.df", source=fonte)
            if d.code == CODIGO]


def test_o_acumulador_local_que_zera_a_global_e_avisado():
    fonte = ("total := 100\n"
             "action calcula(xs):\n"
             "    total := 0\n"
             "    cycle x in xs:\n"
             "        total += x\n"
             "    yield total\n")
    assert avisos(fonte) == [3]


def test_o_aviso_descreve_um_efeito_que_existe():
    """A execução confirma o que o aviso diz: a global muda."""
    from test_tipo_declarado import rodar
    saida = rodar("total := 100\n"
                  "action calcula(xs):\n"
                  "    total := 0\n"
                  "    cycle x in xs:\n"
                  "        total += x\n"
                  "    yield total\n"
                  "calcula([1, 2])\n"
                  "out total\n")
    assert saida.strip() == "3"


def test_um_metodo_tambem_e_olhado():
    assert avisos("contador := 0\nblueprint B:\n    action m():\n"
                  "        contador := 9\n") == [4]


@pytest.mark.parametrize("corpo", [
    "    contador := contador + 1\n",           # lê antes: atualiza a global
    "    contador += 1\n",                      # composta: lê antes
    "    shadow contador := 1\n    contador := 2\n",   # local de propósito
    "    novo := 1\n",                          # nome que não existe no topo
    "    _ := 1\n",                             # o nome de descarte
    "    contador := 1   // df: permitir atribuicao-escreve-global\n",
])
def test_os_usos_legitimos_ficam_calados(corpo):
    fonte = "contador := 0\n_ := 0\naction f():\n" + corpo
    assert avisos(fonte) == []


def test_o_parametro_de_mesmo_nome_nao_e_a_global():
    assert avisos("total := 0\naction f(total):\n    total := 5\n    yield total\n") == []


def test_uma_acao_aninhada_nao_e_contada_como_a_de_fora():
    """A ação de dentro tem escopo próprio: o que ela escreve é dela, ou
    da ação que a contém — nunca é olhado aqui."""
    fonte = ("app := 0\n"
             "action montar():\n"
             "    action dentro():\n"
             "        app := 1\n"
             "    yield dentro\n")
    assert avisos(fonte) == []


def test_o_repositorio_nao_tem_acao_escrevendo_global_por_acidente():
    """Os 20 casos que existiam foram renomeados: o código de referência
    ensina a forma segura, e o aviso não vira ruído que se aprende a
    ignorar."""
    achados = []
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        saida = subprocess.run(
            [sys.executable, "-m", "dataforge", "check", pasta, "--no-color"],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
            errors="replace", env={**os.environ, "PYTHONPATH": RAIZ})
        achados += [l for l in saida.stdout.splitlines()
                    if "existe no topo deste arquivo" in l]
    assert achados == [], "\n".join(achados)
