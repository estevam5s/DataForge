"""
Testes de desempenho e das otimizações que o motivaram.

Não medem tempo absoluto — isso varia com a máquina e tornaria o teste
instável. Medem o que **causava** a lentidão: alocação de escopo por
volta de laço e construção de nós de AST em tempo de execução.

Junto vão os testes de correção das otimizações. Uma otimização que
muda o resultado não é otimização, é bug.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import ast_nodes as ast                           # noqa: E402
from dataforge.environment import Environment                    # noqa: E402
from dataforge.interpreter import Interpreter                    # noqa: E402
from dataforge.lexer import tokenize                             # noqa: E402
from dataforge.parser import parse                               # noqa: E402


def run(fonte):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte)))
    return buffer.getvalue().strip()


# ── Despacho por tabela ──────────────────────────────────────

def test_o_despacho_memoriza_por_classe():
    """Montar f"exec_{nome}" a cada nó era 15% do tempo de execução."""
    interpretador = Interpreter()
    assert interpretador._tabela_exec == {}

    with redirect_stdout(io.StringIO()):
        interpretador.run(parse(tokenize("x := 1\nout x + 1")))

    assert interpretador._tabela_eval, "a tabela de eval ficou vazia"
    # A tabela é indexada pela classe, não pelo nome.
    assert all(isinstance(c, type) for c in interpretador._tabela_eval)


def test_no_desconhecido_ainda_da_erro_claro():
    from dataforge.errors import DataForgeError

    class NoInventado(ast.ASTNode):
        pass

    with pytest.raises(DataForgeError, match="Cannot evaluate"):
        Interpreter().evaluate(NoInventado(), Environment())


# ── Escopo reaproveitado ─────────────────────────────────────

def test_laco_simples_reaproveita_o_escopo():
    """Sem captura, uma volta não precisa de escopo novo."""
    no = parse(tokenize("cycle i from 1 to 3:\n    x := i")).body[0]
    assert Interpreter._corpo_captura_escopo(no.body) is False


@pytest.mark.parametrize("corpo,motivo", [
    ("    action f():\n        yield i", "ação declarada"),
    ("    lista.append(lambda => i)", "lambda numa expressão"),
    ("    lista.append({\"f\": lambda => i})", "lambda aninhado num vault"),
    ("    blueprint B:\n        action f():\n            yield 1", "blueprint"),
    ("    thread:\n        out i", "thread"),
])
def test_corpo_que_captura_ganha_escopo_proprio(corpo, motivo):
    """Reaproveitar o escopo aqui daria 'todas veem o último valor'."""
    fonte = f"lista := []\ncycle i from 1 to 3:\n{corpo}"
    no = parse(tokenize(fonte)).body[1]
    assert Interpreter._corpo_captura_escopo(no.body) is True, motivo


def test_acao_dentro_do_laco_captura_cada_volta():
    assert run('''
acoes := []
cycle i from 1 to 3:
    action guardar():
        yield i
    acoes.append(guardar)
out [f() cycle f in acoes]''') == "[1, 2, 3]"


def test_lambda_dentro_do_laco_captura_cada_volta():
    """Foi uma regressão real: o lambda vive dentro de uma expressão,
    e olhar só as instruções o deixava passar."""
    assert run('''
fs := []
cycle j from 1 to 3:
    fs.append(lambda => j)
out [f() cycle f in fs]''') == "[1, 2, 3]"


def test_lambda_aninhado_fundo_tambem_captura():
    assert run('''
gs := []
cycle k from 1 to 3:
    gs.append({"f": lambda => k}["f"])
out [g() cycle g in gs]''') == "[1, 2, 3]"


def test_cycle_in_tambem_captura():
    assert run('''
fs := []
cycle x in [1, 2, 3]:
    fs.append(lambda => x)
out [f() cycle f in fs]''') == "[1, 2, 3]"


def test_persist_tambem_captura():
    assert run('''
fs := []
n := 1
persist n smaller_eq 3:
    m := n
    fs.append(lambda => m)
    n += 1
out [f() cycle f in fs]''') == "[1, 2, 3]"


def test_variavel_do_laco_nao_vaza_entre_voltas():
    """Reaproveitar o escopo não pode deixar lixo da volta anterior.

    Uma variável criada dentro de um 'given' fica no escopo do bloco,
    não no do laço — por isso o teste usa uma criada direto no corpo,
    que é onde o reaproveitamento poderia vazar.
    """
    assert run('''
cycle i from 1 to 3:
    given i is 1:
        marca := "primeira"
        out marca
    otherwise:
        out "sem marca"''') == "primeira\nsem marca\nsem marca"


def test_o_escopo_reaproveitado_e_limpo_a_cada_volta():
    """A limpeza acontece — o que a variável faz depois é outra coisa.

    Uma variável atribuída no corpo do laço **sobrevive** entre voltas
    mas **não escapa** do laço: ela vive no escopo da iteração, que é o
    mesmo objeto reaproveitado, e some quando o laço acaba.

    Isso vale desde antes desta otimização e não mudou com ela — o
    teste fixa o comportamento para que uma mudança futura no
    reaproveitamento não o altere sem querer.
    """
    assert run('''
cycle i from 1 to 3:
    out exists("marca")
    marca := i''') == "yes\nyes\nyes"

    # E não escapa do laço.
    from dataforge.errors import DataForgeError
    with pytest.raises(DataForgeError, match="marca"):
        run('''
cycle i from 1 to 3:
    marca := i
out marca''')


def test_a_limpeza_do_escopo_reaproveitado_de_fato_ocorre():
    """No nível do Environment, onde não há cadeia para atrapalhar."""
    escopo = Environment()
    filho = escopo.child("<cycle>")
    filho.set_local("i", 1)
    filho.set_local("temporario", "lixo")
    filho.limpar()
    assert filho.variables == {}


# ── Atribuição composta sem construir AST ────────────────────

def test_alvo_da_atribuicao_composta_e_avaliado_uma_vez():
    """'v[f()] += 1' chamando f() duas vezes foi um bug real, achado
    porque uma amostragem ponderada dava 50/50 em vez de 10/90."""
    assert run('''
chamadas := 0
action indice():
    chamadas += 1
    yield 0

v := [10]
v[indice()] += 5
out v[0], chamadas''') == "15 1"


@pytest.mark.parametrize("fonte,esperado", [
    ("x := 10\nx += 5\nout x", "15"),
    ("x := 10\nx -= 3\nout x", "7"),
    ("x := 10\nx *= 3\nout x", "30"),
    ("x := 10\nx /= 4\nout x", "2.5"),
    ("x := 10\nx %= 3\nout x", "1"),
    ('s := "a"\ns += "b"\nout s', "ab"),
    ("l := [1]\nl += [2]\nout l", "[1, 2]"),
])
def test_toda_forma_de_atribuicao_composta(fonte, esperado):
    assert run(fonte) == esperado


def test_atribuicao_composta_em_campo_e_indice():
    assert run('''
blueprint C:
    n: Integer := 10
c := spawn C()
c.n += 5

m := {"k": 1}
m["k"] += 41

out c.n, m["k"]''') == "15 42"


def test_sobrecarga_de_operador_vale_na_atribuicao_composta():
    """'+=' passa pelo mesmo caminho de '+', inclusive a sobrecarga."""
    assert run('''
blueprint Dinheiro(valor):
    operator +(outro):
        yield spawn Dinheiro(self.valor + outro.valor)

d := spawn Dinheiro(10)
d += spawn Dinheiro(32)
out d.valor''') == "42"


# ── Environment com __slots__ ────────────────────────────────

def test_environment_usa_slots():
    """Um laço de 200 mil voltas criava 200 mil dicts de atributo."""
    assert hasattr(Environment, "__slots__")
    with pytest.raises(AttributeError):
        Environment().atributo_qualquer = 1


def test_os_atributos_dinamicos_continuam_permitidos():
    """'defer' e 'relay' anexam campos ao escopo; com __slots__ eles
    precisam estar declarados, senão o erro aparece longe da causa."""
    escopo = Environment()
    escopo._deferred = []
    escopo._exports = {}
    assert escopo._deferred == []


def test_limpar_esvazia_o_escopo():
    escopo = Environment()
    escopo.set_local("x", 1)
    escopo.limpar()
    assert escopo.variables == {}


# ── O programa de carga roda certo ───────────────────────────

def test_a_carga_de_referencia_da_o_resultado_certo():
    """Se uma otimização mudar o resultado, este teste pega."""
    assert run('''
action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

soma := 0
cycle i from 1 to 1000:
    soma += i

nums := [i cycle i in range(0, 500)]
total := 0
cycle n in nums:
    total += n

contagem := {}
cycle i from 0 to 500:
    chave := str(i % 10)
    contagem[chave] := (contagem[chave] ?? 0) + 1

out soma, fib(15), total, len(contagem)''') == "500500 610 124750 10"


# ── Compilação para closures ─────────────────────────────────

def test_o_corpo_compilado_e_montado_uma_vez_so():
    """Recompilar a cada chamada apagaria o ganho inteiro.

    O fechamento fica guardado na `DFAction`, e não no nó da árvore: o
    interpretador que compilou está amarrado dentro dos fechamentos, e
    dois interpretadores sobre a mesma árvore — o REPL, os testes — não
    podem herdar o compilado um do outro.
    """
    from dataforge.interpreter import Interpreter

    interp = Interpreter()
    interp.run(parse(tokenize('''
action dobro(n):
    yield n * 2

dobro(1)
dobro(2)
dobro(3)''', "t"), "t"), "t")

    acao = interp.global_env.get("dobro")
    assert acao.corpo_compilado is not None, "o corpo nao foi compilado"

    primeiro = acao.corpo_compilado
    interp.run(parse(tokenize("dobro(4)", "t"), "t"), "t")
    assert acao.corpo_compilado is primeiro, "recompilou"


def test_o_depurador_desliga_a_compilacao():
    """Um depurador que enxerga metade das instruções é pior que lento.

    O corpo compilado passa **por fora** de `execute` — é assim que ele
    economiza o despacho. O depurador para em cada linha sombreando
    justamente `execute`: com a compilação ligada, ele veria as
    instruções de topo e nenhuma de dentro de ação.
    """
    from dataforge.depurador import Depurador
    from dataforge.interpreter import Interpreter

    interp = Interpreter()
    assert interp.compilar_corpos is True

    dep = Depurador(interp, "t.df", "out 1")
    dep.ligar()
    assert interp.compilar_corpos is False, \
        "o depurador nao desligou a compilacao"

    dep.desligar()
    assert interp.compilar_corpos is True, "e nao religou depois"


def test_o_que_o_compilador_nao_conhece_recua_para_o_interpretador():
    """A garantia que torna o compilador seguro.

    Um nó sem construtor próprio vira `interp.execute(no, env)` — o
    comportamento de hoje, byte por byte. É o que permite acrescentar
    recursos à linguagem sem tocar no compilador: eles continuam
    funcionando, só não ficam mais rápidos.
    """
    from dataforge import ast_nodes as df_ast
    from dataforge.compilador import _EXPRESSOES, _INSTRUCOES
    from dataforge.interpreter import Interpreter

    interp = Interpreter()

    # 'match' nao esta em nenhuma das tabelas — e roda igual.
    assert df_ast.MatchBlock not in _INSTRUCOES
    assert df_ast.MatchBlock not in _EXPRESSOES
    assert run('''
action rotular(n):
    match n:
        point 0:
            yield "zero"
        default:
            yield "outro"

out rotular(0), rotular(7)''') == "zero outro"


def test_a_compilacao_nao_muda_o_resultado_de_nenhum_exercicio():
    """A prova de que 'mais rapido' nao virou 'diferente'.

    Roda uma amostra dos exercícios com a compilação ligada e desligada
    e compara a saída caractere por caractere. Se algum fechamento
    divergir do método que ele espelha, a diferença aparece aqui.
    """
    import glob
    import io as _io
    import re as _re
    from contextlib import redirect_stdout

    from dataforge.interpreter import Interpreter

    #: Um exercicio que MEDE tempo imprime um numero diferente a cada
    #: execucao, e isso nao e divergencia de semantica. So o que vem
    #: colado numa unidade de tempo e neutralizado — um numero solto
    #: continua sendo comparado.
    tempo = _re.compile(r"\d+(?:[.,]\d+)?\s*(ms|µs|us|s)\b")

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivos = sorted(glob.glob(os.path.join(
        raiz, "exercicios", "*", "[0-9]*.df")))
    assert arquivos, "nenhum exercicio encontrado"

    # Um de cada cinco: cobre os 26 módulos sem custar a suíte inteira.
    for caminho in arquivos[::5]:
        fonte = open(caminho, encoding="utf-8").read()
        arvore = parse(tokenize(fonte, caminho), caminho)

        saidas = []
        for compilar in (True, False):
            interp = Interpreter()
            interp.compilar_corpos = compilar
            buffer = _io.StringIO()
            try:
                with redirect_stdout(buffer):
                    interp.run(arvore, caminho)
            except Exception as erro:            # noqa: BLE001
                buffer.write(f"\n<erro> {type(erro).__name__}: {erro}")
            saidas.append(buffer.getvalue())

        saidas = [tempo.sub("<tempo>", t) for t in saidas]
        assert saidas[0] == saidas[1], (
            f"{os.path.relpath(caminho, raiz)} muda de resultado com a "
            f"compilacao ligada")
