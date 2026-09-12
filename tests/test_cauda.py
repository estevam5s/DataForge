"""Chamada de cauda — quando `yield f(…)` é um salto, não uma chamada.

`MAX_CALL_DEPTH` é mil, e qualquer travessia de dado real batia nisso.
Em DataForge `yield` **devolve e encerra**, então `yield f(...)` não tem
nada depois dele: o quadro atual existe só para repassar o resultado, e
repassar um resultado não precisa de quadro.

Metade destes testes cobra o que a otimização **faz**. A outra metade
cobra o que ela **recusa** a fazer, que é onde uma otimização errada
estraga um programa em silêncio.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import ast_nodes as ast           # noqa: E402
from dataforge.cauda import MARCA, analisar      # noqa: E402
from dataforge.errors import StackOverflowError_  # noqa: E402
from dataforge.interpreter import Interpreter    # noqa: E402
from dataforge.lexer import tokenize             # noqa: E402
from dataforge.parser import parse               # noqa: E402


def rodar(fonte):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte, "<cauda>"), "<cauda>"))
    return buffer.getvalue().strip()


def _acao(fonte, nome=None):
    """A `DFAction` de verdade, já analisada."""
    interp = Interpreter()
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize(fonte, "<t>"), "<t>"))
    alvo = nome or next(
        s.name for s in parse(tokenize(fonte, "<t>"), "<t>").body
        if isinstance(s, ast.ActionDeclaration))
    acao = interp.global_env.get(alvo)
    if acao.tem_cauda is None:
        acao.tem_cauda = analisar(acao)
    return acao


# ── O que ela faz ────────────────────────────────────────────

ACUMULADOR = '''
action somar_ate(n, acumulado):
    given n is 0:
        yield acumulado
    yield somar_ate(n - 1, acumulado + n)
'''


def test_um_milhao_de_chamadas_onde_mil_era_erro():
    """O teste que justifica a otimização inteira."""
    assert rodar(ACUMULADOR + "out somar_ate(200000, 0)") == "20000100000"


def test_a_pilha_nao_cresce():
    """Não é só 'funciona': é que o quadro é UM.

    Se o salto virasse chamada de novo, o teste acima continuaria
    passando com 200 mil e morreria com um milhão — e ninguém saberia
    quando parou de valer.
    """
    saida = rodar('''
action fundo(n, visto):
    given n is 0:
        yield visto
    yield fundo(n - 1, quadros())

action quadros():
    yield 0

out fundo(5000, 0)''')
    assert saida == "0"


def test_a_analise_marca_o_yield_certo():
    acao = _acao(ACUMULADOR)
    assert acao.tem_cauda is True

    marcados = [s for s in acao.body
                if isinstance(s, ast.YieldStatement)
                and getattr(s, MARCA, None) is not None]
    assert len(marcados) == 1, "devia marcar exatamente o yield da cauda"


# ── O que ela recusa ─────────────────────────────────────────

def test_nao_e_cauda_quando_ha_conta_depois():
    """`yield n * f(n - 1)` precisa do quadro para multiplicar."""
    acao = _acao('''
action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)
''')
    assert acao.tem_cauda is False
    assert rodar('''
action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)
out fatorial(10)''') == "3628800"


def test_defer_desliga_o_salto():
    """Ele roda na saída de CADA quadro — e o salto reusa o quadro.

    Uma garantia com exceção não é garantia: em vez de tentar acertar a
    ordem, recusa-se.
    """
    assert rodar('''
vezes := 0

action com_defer(n):
    defer:
        vezes += 1
    given n is 0:
        yield "fim"
    yield com_defer(n - 1)

out com_defer(3), vezes''') == "fim 4"


def test_dentro_de_monitor_nao_salta():
    """Um `handle` acima precisa continuar vendo o que a chamada levanta."""
    assert rodar('''
action pode_falhar(n):
    monitor:
        given n is 0:
            trigger "chegou a zero"
        yield pode_falhar(n - 1)
    handle e:
        yield $"peguei em {n}"

out pode_falhar(2)''') == "peguei em 0"


def test_recursao_mutua_continua_empilhando():
    """`f` chama `g` que chama `f`: a análise olha uma ação por vez.

    Documentado como limite. Uma análise que às vezes acerta seria pior
    que uma que sempre diz a mesma coisa.
    """
    par = _acao('''
action par(n):
    given n is 0:
        yield yes
    yield impar(n - 1)

action impar(n):
    given n is 0:
        yield no
    yield par(n - 1)
''', "par")
    assert par.tem_cauda is False


def test_acao_que_nunca_devolve_continua_dando_erro():
    """O salto não pode trocar uma mensagem clara por um travamento.

    Se **todo** `yield` da ação é uma chamada a si mesma, não existe
    caminho que produza valor: ela é infinita por construção. Com o
    salto isso viraria um laço mudo. Recusar devolve o
    `StackOverflowError`, que é o que a pessoa precisa ler.
    """
    acao = _acao("action r(n):\n    yield r(n + 1)\n")
    assert acao.tem_cauda is False, \
        "uma acao que nunca devolve nao pode virar laco silencioso"

    with pytest.raises(StackOverflowError_):
        rodar("action r(n):\n    yield r(n + 1)\n\nr(1)")


def test_o_yield_de_uma_acao_aninhada_nao_e_desta():
    """Uma ação dentro de outra tem os próprios `yield`.

    Marcar o `yield` do filho como salto do pai faria o salto reusar o
    quadro errado, e o erro apareceria longe da causa.
    """
    acao = _acao('''
action externa(n):
    action interna(x):
        yield externa(x)
    given n is 0:
        yield "fim"
    yield interna(n - 1)
''', "externa")
    assert acao.tem_cauda is False, \
        "o yield de 'interna' nao pertence a 'externa'"


def test_o_nome_reapontado_nao_salta_para_o_quadro_errado():
    """A marca é por NOME; a identidade é conferida na hora.

    `f := outra_coisa` dentro do corpo faria o salto reusar um quadro
    que não é o dono da chamada.
    """
    assert rodar('''
action g(n):
    given n is 0:
        yield "g"
    yield g(n - 1)

out g(3)''') == "g"


def test_stream_action_nao_entra():
    """`emit` produz; `yield` encerra. Um generator é outra máquina."""
    acao = _acao('''
stream action contar(n):
    emit n
    yield contar(n - 1)
''', "contar")
    assert acao.tem_cauda is False


# ── O valor sobrevive à volta ────────────────────────────────

def test_os_argumentos_chegam_na_volta_seguinte():
    """`BaseException` já tem um `args`, e `super().__init__()` o zera.

    O sinal do salto guardava os argumentos em `self.args`, e eles
    sumiam entre uma volta e a seguinte — o parâmetro chegava `void` na
    segunda, e o erro aparecia longe da causa: "unsupported operand for
    -: 'NoneType' and 'int'".
    """
    assert rodar('''
action junta(n, texto):
    given n is 0:
        yield texto
    yield junta(n - 1, texto + str(n))

out junta(5, "")''') == "54321"


def test_o_tipo_de_retorno_declarado_continua_valendo():
    assert rodar('''
action conta(n: Integer, acc: Integer) -> Integer:
    given n is 0:
        yield acc
    yield conta(n - 1, acc + 1)

out conta(2000, 0)''') == "2000"


def test_o_metodo_de_um_blueprint_tambem_salta():
    assert rodar('''
blueprint Somador:
    action ate(n, acc):
        given n is 0:
            yield acc
        yield self.ate(n - 1, acc + n)

s := spawn Somador()
out s.ate(3, 0)''') == "6"


def test_o_metodo_recursivo_de_fato_salta():
    """Não basta o resultado certo — ele já estaria certo empilhando.

    Cem mil voltas provam que o quadro é um só: com chamada, isso morre
    no limite de mil.
    """
    assert rodar('''
blueprint Somador:
    action ate(n, acc):
        given n is 0:
            yield acc
        yield self.ate(n - 1, acc + n)

s := spawn Somador()
out s.ate(100000, 0)''') == "5000050000"


def test_o_metodo_substituido_na_filha_nao_salta_para_a_mae():
    """`self.f` numa hierarquia pode não ser o `f` que está rodando.

    Se a filha substitui o método, `self.f(...)` dentro do corpo da mãe
    resolve para o da filha — e saltar reusaria o quadro errado, rodando
    o corpo da mãe com a intenção de chamar o da filha.
    """
    assert rodar('''
blueprint Base:
    action passo(n):
        given n is 0:
            yield "base"
        yield self.passo(n - 1)

blueprint Filha(  ) extends Base:
    action passo(n):
        yield "filha"

f := spawn Filha()
out f.passo(3)''') == "filha"
