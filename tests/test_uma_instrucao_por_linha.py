"""Depois de uma instrução completa, a linha tem de acabar.

O parser aceitava duas instruções coladas: `x := 1 vazios` virava
`x := 1` e depois `vazios`. O caso que custou caro foi o comentário que
começa com número — `// 1 + 3 vazios` é DIVISÃO, e o resto da linha
virava uma segunda instrução. Dezessete blocos da documentação só
"compilavam" por causa disso.
"""
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import ParseError  # noqa: E402
from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402


def _ler(fonte):
    return parse(tokenize(fonte + "\n", "t.df"), "t.df")


@pytest.mark.parametrize("fonte", [
    "x := 1 vazios",
    "out 1 out 2",
    "assert yes vazios",
    "x := 12 // 1 + 3 vazios",
])
def test_duas_instrucoes_na_mesma_linha_sao_recusadas(fonte):
    with pytest.raises(ParseError, match="same line"):
        _ler(fonte)


def test_a_dica_fala_do_comentario_quando_ha_divisao():
    with pytest.raises(ParseError) as info:
        _ler("x := 12 // 1 + 3 vazios")
    assert "integer division, not a comment" in str(info.value)


@pytest.mark.parametrize("fonte", [
    "x := 12 // 3",
    "x := 1 // comentario de verdade",
    "x := 1 # comentario",
    "given yes:\n    out 1\nout 2",
    "action f():\n    yield 1\nout f()",
])
def test_o_que_era_valido_continua(fonte):
    _ler(fonte)


def test_nenhum_df_do_repositorio_tem_duas_instrucoes_numa_linha():
    arquivos = subprocess.run(["git", "ls-files", "*.df"], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              cwd=RAIZ).stdout.split()
    ruins = []
    for f in arquivos:
        try:
            fonte = open(os.path.join(RAIZ, f), encoding="utf-8").read()
            parse(tokenize(fonte, f), f)
        except ParseError as erro:
            for e in [erro] + list(getattr(erro, "outros", [])):
                if "same line" in str(e):
                    ruins.append(f"{f}: {e}")
        except Exception:                                  # noqa: BLE001
            pass
    assert not ruins, "\n".join(ruins[:10])
