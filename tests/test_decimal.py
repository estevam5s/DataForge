"""`Arcane.Decimal` — quando 0,1 + 0,2 precisa dar 0,3.

`Float` é IEEE 754, e ele não representa 0,1. Isso é o certo para
física, estatística e gráficos; é errado para dinheiro, imposto e todo
número que uma pessoa vai conferir na mão. Um centavo que some numa
linha some de novo num milhão de linhas.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError       # noqa: E402
from dataforge.interpreter import Interpreter     # noqa: E402
from dataforge.lexer import tokenize              # noqa: E402
from dataforge.parser import parse                # noqa: E402

CABECA = "adopt Arcane.Decimal as Dec\n"


def rodar(fonte):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(CABECA + fonte, "<d>"), "<d>"))
    return buffer.getvalue().strip()


# ── O que ele resolve ────────────────────────────────────────

def test_a_soma_que_o_float_erra():
    assert rodar('out Dec.de("0.1") + Dec.de("0.2")') == "0.3"
    # E o float continua errando, que é o motivo de o módulo existir.
    assert rodar("out 0.1 + 0.2") == "0.30000000000000004"


def test_a_aritmetica_e_a_da_linguagem():
    """`+ - * /` e comparação funcionam sem função nenhuma.

    Só é possível porque o interpretador trata valor por protocolo. Se
    alguém trocar protocolo por `isinstance`, isto quebra.
    """
    assert rodar('out Dec.de("19.99") * 3') == "59.97"
    assert rodar('out Dec.de("10") / 4') == "2.5"
    assert rodar('out Dec.de("1.10") bigger Dec.de("1.09")') == "yes"
    assert rodar('out Dec.de("1.5") is Dec.de("1.5")') == "yes"


def test_typeof_responde_Decimal():
    assert rodar('out typeof(Dec.de("1.5"))') == "Decimal"


def test_ordenar_e_somar_um_cluster():
    assert rodar('''
v := [Dec.de("3.10"), Dec.de("1.05"), Dec.de("2.50")]
out max(v), Dec.soma(v)''') == "3.10 6.65"


# ── As duas decisões que precisam de justificativa ───────────

def test_de_um_float_devolve_o_que_a_pessoa_escreveu():
    """`Dec.de(0.1)` é `0.1`, e não `0.1000000000000000055…`.

    Converter o binário cru seria tecnicamente mais fiel e praticamente
    inútil: ninguém digita 0.1 querendo o binário mais próximo dele.
    """
    assert rodar("out Dec.de(0.1)") == "0.1"


def test_arredonda_meio_para_cima_e_nao_bancario():
    """2,5 centavos precisam virar 3, sempre, ou o cliente reclama.

    O `round` embutido faz arredondamento bancário — o certo para
    estatística, porque não enviesa uma série longa. É a mesma decisão
    que o pacote `moeda` já tinha tomado.
    """
    assert rodar('out Dec.arredondar(Dec.de("2.5"))') == "3"
    assert rodar('out Dec.arredondar(Dec.de("0.5"))') == "1"
    assert rodar("out round(2.5)") == "2.0", \
        "o embutido continua bancario, e e o certo para ele"

    # E o outro modo continua disponível para quem precisa dele.
    assert rodar('out Dec.arredondar(Dec.de("2.5"), 0, "MEIO_PAR")') == "2"


# ── Repartir sem perder centavo ──────────────────────────────

def test_repartir_nao_perde_centavo():
    """Três vezes 3,33 são 9,99, e o décimo real sumiu.

    Dividir dinheiro em partes iguais quase nunca dá partes iguais, e
    quem paga percebe.
    """
    assert rodar('out Dec.repartir(Dec.de("10.00"), 3)') == "[3.34, 3.33, 3.33]"
    assert rodar('out Dec.soma(Dec.repartir(Dec.de("10.00"), 3))') == "10.00"


@pytest.mark.parametrize("total,partes", [
    ("100.00", 3), ("0.05", 3), ("7.00", 7), ("1.00", 6), ("999.99", 11),
])
def test_a_soma_das_partes_e_sempre_o_total(total, partes):
    assert rodar(f'''
p := Dec.repartir(Dec.de("{total}"), {partes})
out Dec.soma(p) is Dec.de("{total}"), len(p)''') == f"yes {partes}"


def test_repartir_valor_negativo_tambem_fecha():
    assert rodar('''
p := Dec.repartir(Dec.de("-10.00"), 3)
out Dec.soma(p)''') == "-10.00"


# ── Centavos, que é como dinheiro costuma ser guardado ───────

def test_ida_e_volta_por_centavos():
    assert rodar("out Dec.texto(Dec.de_centavos(1999), 2)") == "19.99"
    assert rodar('out Dec.centavos(Dec.de("19.99"))') == "1999"
    assert rodar('out Dec.centavos(Dec.de("19.995"))') == "2000", \
        "arredonda meio-para-cima, como o resto do modulo"


# ── Misturar exato com aproximado é recusado ─────────────────

def test_somar_decimal_com_float_explica_a_recusa():
    """A mensagem crua do Python está certa e não diz nada do que importa."""
    with pytest.raises(DataForgeError) as capturado:
        rodar('out Dec.de("1.5") + 0.5')

    erro = capturado.value
    texto = str(erro) + str(getattr(erro, "nota", "")) + \
        str(getattr(erro, "dica", ""))
    assert "Decimal" in texto and "Float" in texto
    assert "Decimal.de" in texto, "precisa dizer como consertar"
    assert "unsupported operand" not in str(erro), \
        "a mensagem do Python vazou"


def test_o_float_do_outro_lado_tambem():
    with pytest.raises(DataForgeError):
        rodar('out 0.5 * Dec.de("2")')


def test_com_inteiro_funciona():
    """Inteiro é exato, então misturar não perde nada."""
    assert rodar('out Dec.de("1.5") * 2') == "3.0"


# ── Mensagens de uso errado ──────────────────────────────────

def test_texto_que_nao_e_numero_explica():
    with pytest.raises(DataForgeError) as capturado:
        rodar('out Dec.de("dezenove reais")')
    assert "nao e um numero decimal" in str(capturado.value)


def test_aceita_virgula_como_separador():
    """Quem escreve em português digita vírgula."""
    assert rodar('out Dec.de("19,99")') == "19.99"


def test_modo_de_arredondamento_errado_lista_os_certos():
    with pytest.raises(DataForgeError) as capturado:
        rodar('out Dec.arredondar(Dec.de("1.5"), 0, "PRA_CIMA_MESMO")')
    assert "MEIO_PARA_CIMA" in str(getattr(capturado.value, "dica", ""))


def test_funcao_que_precisa_de_decimal_diz_quando_nao_vem():
    with pytest.raises(DataForgeError) as capturado:
        rodar("out Dec.arredondar(1.5)")
    assert "Decimal.de" in str(getattr(capturado.value, "dica", ""))


def test_casas_conta_como_foi_escrito():
    assert rodar('out Dec.casas(Dec.de("19.99")), Dec.casas(Dec.de("5"))') \
        == "2 0"
