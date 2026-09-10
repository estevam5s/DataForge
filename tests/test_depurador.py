# -*- coding: utf-8 -*-
"""O depurador: onde ele para, o que mostra, e o que não custa.

Os testes conversam com ele como uma pessoa conversaria — mandando
comandos por stdin e lendo o que saiu.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.depurador import Depurador, depurar                # noqa: E402
from dataforge.interpreter import Interpreter                     # noqa: E402


PROGRAMA = '''action dobrar(n):
    resultado := n * 2
    yield resultado

total := 0
cycle i from 1 to 3:
    total += dobrar(i)
out total
'''


def _depurar(tmp_path, comandos, fonte=PROGRAMA, paradas=()):
    """Roda sob o depurador, respondendo com estes comandos."""
    arquivo = tmp_path / "p.df"
    arquivo.write_text(fonte, encoding="utf-8")

    entrada = sys.stdin
    saida = sys.stdout
    sys.stdin = io.StringIO("\n".join(comandos) + "\n")
    sys.stdout = io.StringIO()
    try:
        codigo = depurar(str(arquivo), paradas)
        return sys.stdout.getvalue(), codigo
    finally:
        sys.stdin = entrada
        sys.stdout = saida


# ═══════════════════════════════════════════════════════════
#  Custo zero quando desligado
# ═══════════════════════════════════════════════════════════

def test_desligado_o_interpretador_e_o_de_sempre():
    """Um 'if depurando:' em 'execute' custaria em TODA execução.

    'execute' roda mais de um milhão de vezes num programa médio. Por
    isso o depurador substitui o método em vez de ser consultado — e
    'desligar' precisa devolver exatamente o que estava lá.
    """
    interp = Interpreter()
    antes = Interpreter.execute
    assert "execute" not in interp.__dict__, "já havia sombra antes de ligar"

    d = Depurador(interp, "p.df", "x := 1\n")
    d.ligar()
    assert "execute" in interp.__dict__, "não sombreou"

    d.desligar()
    assert "execute" not in interp.__dict__, "a sombra ficou depois de desligar"
    # e o método volta a ser exatamente o da classe
    assert interp.execute.__func__ is antes


# ═══════════════════════════════════════════════════════════
#  Onde ele para
# ═══════════════════════════════════════════════════════════

def test_para_na_linha_pedida(tmp_path):
    saida, codigo = _depurar(tmp_path, ["c"] * 5, paradas=[2])
    assert codigo == 0
    assert "p.df:2" in saida


def test_sem_parada_para_na_primeira_instrucao(tmp_path):
    saida, _ = _depurar(tmp_path, ["c"])
    assert "p.df:1" in saida


def test_a_parada_dispara_a_cada_volta(tmp_path):
    """O laço chama 'dobrar' três vezes; a parada é dentro dela."""
    saida, _ = _depurar(tmp_path, ["c"] * 5, paradas=[2])
    assert saida.count("p.df:2") == 3


def test_o_programa_roda_ate_o_fim(tmp_path):
    saida, codigo = _depurar(tmp_path, ["c"] * 5, paradas=[2])
    assert "12" in saida, "o resultado não saiu"
    assert "programa terminou" in saida
    assert codigo == 0


# ═══════════════════════════════════════════════════════════
#  O que ele mostra
# ═══════════════════════════════════════════════════════════

def test_vars_mostra_o_escopo_da_acao(tmp_path):
    saida, _ = _depurar(tmp_path, ["vars", "c", "c", "c", "c"], paradas=[2])
    assert "dobrar" in saida
    assert "\n    n " in saida or " n   " in saida


def test_vars_nao_despeja_as_embutidas(tmp_path):
    """Elas vivem no escopo global e enterrariam o que se pediu."""
    saida, _ = _depurar(tmp_path, ["vars", "c", "c", "c", "c"], paradas=[2])
    assert "builtin action" not in saida
    assert "MAX_INT" not in saida


def test_expressao_e_avaliada_no_quadro_onde_parou(tmp_path):
    """No escopo global, 'n' nem existiria."""
    saida, _ = _depurar(tmp_path, ["v n * 10", "c", "c", "c", "c"], paradas=[2])
    assert "n * 10 = 10" in saida


def test_expressao_sem_comando_tambem_vale(tmp_path):
    """É o que se quer nove em dez vezes."""
    saida, _ = _depurar(tmp_path, ["resultado", "c", "c", "c", "c"],
                        paradas=[3])
    assert "resultado = 2" in saida


def test_nome_de_uma_letra_que_e_comando_vale_como_comando(tmp_path):
    """'n' é 'próximo', mesmo havendo uma variável chamada 'n'.

    A colisão é real e não tem saída boa: quem digita 'n' quase sempre
    quer andar. Por isso 'v n' existe — e a ajuda diz isso.
    """
    saida, _ = _depurar(tmp_path, ["v n", "c", "c", "c", "c"], paradas=[2])
    assert "n = 1" in saida


def test_expressao_errada_nao_derruba(tmp_path):
    saida, codigo = _depurar(tmp_path, ["v naoexiste", "c", "c", "c", "c"],
                             paradas=[2])
    assert codigo == 0
    assert "programa terminou" in saida


def test_pilha_mostra_quem_chamou(tmp_path):
    saida, _ = _depurar(tmp_path, ["pilha", "c", "c", "c", "c"], paradas=[2])
    assert "dobrar" in saida


def test_listar_marca_a_linha_atual(tmp_path):
    saida, _ = _depurar(tmp_path, ["l", "c", "c", "c", "c"], paradas=[2])
    assert "→" in saida


def test_olho_repete_a_expressao_a_cada_parada(tmp_path):
    saida, _ = _depurar(tmp_path, ["olho n", "c", "c", "c", "c"], paradas=[2])
    assert saida.count("olho") >= 2      # o comando, e ao menos uma repetição


# ═══════════════════════════════════════════════════════════
#  Andar
# ═══════════════════════════════════════════════════════════

def test_fora_volta_para_quem_chamou(tmp_path):
    """'f' roda até a ação retornar — e o laço continua."""
    saida, _ = _depurar(tmp_path, ["f", "vars", "c", "c", "c"], paradas=[2])
    assert "p.df:7" in saida, "não voltou para a linha da chamada"


def test_parada_pode_ser_ligada_de_dentro(tmp_path):
    saida, _ = _depurar(tmp_path, ["b 8", "c", "c", "c", "c", "c"], paradas=[2])
    assert "p.df:8" in saida


def test_sair_encerra_sem_erro(tmp_path):
    saida, codigo = _depurar(tmp_path, ["q"], paradas=[2])
    assert codigo == 0
    assert "encerrando" in saida


def test_ajuda_lista_os_comandos(tmp_path):
    saida, _ = _depurar(tmp_path, ["h", "q"], paradas=[2])
    for palavra in ("passo", "próximo", "vars", "pilha"):
        assert palavra in saida


# ═══════════════════════════════════════════════════════════
#  Casos que não podem quebrar
# ═══════════════════════════════════════════════════════════

def test_arquivo_que_nao_existe():
    assert depurar("/nao/existe/x.df") == 1


def test_erro_de_sintaxe_e_relatado_sem_entrar_no_depurador(tmp_path):
    arquivo = tmp_path / "ruim.df"
    arquivo.write_text("action f(\n", encoding="utf-8")
    assert depurar(str(arquivo)) == 1


def test_erro_em_execucao_mostra_o_erro_e_desliga(tmp_path):
    """O depurador não pode ficar instalado depois de o programa cair."""
    saida, codigo = _depurar(tmp_path, ["c", "c"], fonte="x := 1 / 0\n")
    assert codigo == 1
