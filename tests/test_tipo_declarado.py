"""O tipo declarado vale DEPOIS da declaração, e não só nela.

`x: Integer := 1` seguido de `x := "a"` passava — no `check` e na
execução. A anotação era conferida no instante em que era escrita e
depois esquecida; o mesmo valia para o parâmetro tipado dentro do corpo
(`a := "s"` em `action f(a: Integer)`), para a variável
`Cluster<Integer>` reatribuída e para o campo tipado de um blueprint
(`b.n := "texto"` num `blueprint B(n: Integer)`).

A incoerência era interna: `xs.append("x")` num `Cluster<Integer>` já era
recusado, e `xs := ["x"]` não.

O tipo mora no `Environment` (`tipos`), no escopo onde o nome mora, e
`set` o confere — é o que faz todo caminho de escrita passar por ele sem
repetir a regra. O analisador guarda o tipo ANOTADO separado do inferido
(`Scope.declarados`).
"""

import io
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, ".")

from dataforge.errors import DataForgeError  # noqa: E402
from dataforge.interpreter import Interpreter  # noqa: E402
from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402

MODOS = [True, False]


def rodar(fonte, compilar=True):
    interp = Interpreter()
    interp.compilar_corpos = compilar
    saida = io.StringIO()
    with redirect_stdout(saida):
        interp.run(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    return saida.getvalue()


def recusa(fonte, compilar=True):
    """O erro que a execução levanta, com a linha em que ele aparece."""
    with pytest.raises(DataForgeError) as erro:
        rodar(fonte, compilar)
    return erro.value


def codigos(fonte):
    arvore = parse(tokenize(fonte, "t.df"), "t.df")
    return [(d.code, d.line) for d in check_program(arvore, "t.df")
            if d.severity == "error"]


# ═══════════════════════════════════════════════════════════
#  Execução
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("compilar", MODOS)
def test_a_variavel_anotada_recusa_outro_tipo_na_reatribuicao(compilar):
    erro = recusa("x: Integer := 1\nx := 2\nx := \"a\"\n", compilar)
    assert "Integer" in erro.message and "String" in erro.message
    assert erro.line == 3


@pytest.mark.parametrize("compilar", MODOS)
def test_o_parametro_tipado_continua_tipado_no_corpo(compilar):
    erro = recusa(
        "action f(a: Integer):\n    a := \"s\"\n    yield a\nout f(1)\n",
        compilar)
    assert "parameter 'a'" in erro.message
    assert erro.line == 2


@pytest.mark.parametrize("compilar", MODOS)
def test_a_escrita_vinda_de_dentro_de_uma_acao_tambem_e_conferida(compilar):
    """`:=` numa ação escreve o nome de fora — e o tipo é o de fora."""
    erro = recusa("x: Integer := 1\naction g():\n    x := \"fora\"\ng()\n",
                  compilar)
    assert erro.line == 3


@pytest.mark.parametrize("compilar", MODOS)
def test_a_atribuicao_composta_confere_o_resultado(compilar):
    assert recusa("n: Integer := 1\nn += 1.5\n", compilar).line == 2
    # 's += 1' num String é concatenação: o RESULTADO é String.
    assert rodar("s: String := \"a\"\ns += 1\nout s\n", compilar).strip() == "a1"


@pytest.mark.parametrize("compilar", MODOS)
def test_o_conteudo_da_colecao_reatribuida_e_conferido(compilar):
    erro = recusa("xs: Cluster<Integer> := [1]\nxs := [\"a\"]\n", compilar)
    assert erro.line == 2
    # E o literal novo volta a ser uma coleção tipada: o 'append'
    # seguinte continua recusado, como era antes da reatribuição.
    erro = recusa("xs: Cluster<Integer> := [1]\nxs := [2]\nxs.append(\"x\")\n",
                  compilar)
    assert erro.line == 3


@pytest.mark.parametrize("compilar", MODOS)
def test_o_que_respeita_o_tipo_continua_funcionando(compilar):
    fonte = """
x: Integer := 1
x := 2
x += 3
f: Float := 1.0
f := 2
n: Number := 1
n := 2.5
qualquer: Any := 1
qualquer := "texto"
xs: Cluster<Integer> := [1]
xs := [4, 5]
out x, f, n, qualquer, xs
"""
    assert rodar(fonte, compilar).strip() == "5 2 2.5 texto [4, 5]"


@pytest.mark.parametrize("compilar", MODOS)
def test_uma_redeclaracao_troca_o_tipo(compilar):
    assert rodar("x: Integer := 1\nx: String := \"a\"\nout x\n",
                 compilar).strip() == "a"


@pytest.mark.parametrize("compilar", MODOS)
def test_a_redeclaracao_de_um_parametro_nao_vaza_para_a_proxima_chamada(compilar):
    """Cada chamada recebe uma CÓPIA dos conferidores: esquecer o tipo
    numa chamada não pode apagá-lo das seguintes."""
    fonte = """
action f(a: Integer, trocar):
    given trocar:
        a: String := "livre"
    otherwise:
        a := "recusado"
    yield a
out f(1, yes)
out f(1, no)
"""
    with pytest.raises(DataForgeError) as erro:
        rodar(fonte, compilar)
    assert "parameter 'a'" in erro.value.message


@pytest.mark.parametrize("compilar", MODOS)
def test_o_campo_tipado_do_cabecalho_e_conferido_na_escrita(compilar):
    base = "blueprint B(n: Integer):\n    action f():\n        yield 1\nb := spawn B(1)\n"
    assert recusa(base + "b.n := \"texto\"\n", compilar).line == 5
    assert rodar(base + "b.n := 7\nout b.n\n", compilar).strip() == "7"


@pytest.mark.parametrize("compilar", MODOS)
def test_o_campo_tipado_do_corpo_e_conferido_dentro_e_fora(compilar):
    base = "blueprint C:\n    n: Integer := 0\n    action muda():\n        self.n := \"y\"\nc := spawn C()\n"
    assert recusa(base + "c.n := \"x\"\n", compilar).line == 6
    assert recusa(base + "c.muda()\n", compilar).line == 4


@pytest.mark.parametrize("compilar", MODOS)
def test_o_campo_herdado_e_conferido(compilar):
    fonte = ("blueprint M(n: Integer):\n    action f():\n        yield 1\n"
             "blueprint F extends M:\n    action g():\n        yield 2\n"
             "f := spawn F(1)\nf.n := \"herdado\"\n")
    assert recusa(fonte, compilar).line == 8


@pytest.mark.parametrize("compilar", MODOS)
def test_void_num_campo_tipado_passa(compilar):
    """O campo "sem valor": 'self.conexao := void' ao fechar é o padrão
    comum, e recusá-lo seria o falso alarme — o mesmo preço que a
    conferência genérica paga."""
    fonte = "blueprint C:\n    conexao: String := \"x\"\nc := spawn C()\nc.conexao := void\nout c.conexao\n"
    assert rodar(fonte, compilar).strip() == "void"


@pytest.mark.parametrize("compilar", MODOS)
def test_o_campo_sem_tipo_continua_livre(compilar):
    fonte = "blueprint L(n):\n    action f():\n        yield 1\nl := spawn L(1)\nl.n := \"ok\"\nout l.n\n"
    assert rodar(fonte, compilar).strip() == "ok"


def test_o_padrao_do_campo_e_conferido_na_declaracao():
    """'n: Integer := "a"' criava todo objeto com um campo que contradiz a
    própria declaração. O erro sai na linha do CAMPO."""
    erro = recusa("blueprint C:\n    n: Integer := \"a\"\nc := spawn C()\n")
    assert erro.line == 2


# ═══════════════════════════════════════════════════════════
#  O atalho de desempenho não muda resposta nenhuma
# ═══════════════════════════════════════════════════════════

def test_o_atalho_so_aceita_o_que_o_check_type_aceita():
    """`_ACEITOS_POR_TIPO` é condição SUFICIENTE: todo tipo listado ali
    precisa passar no `_check_type` completo. Um tipo a mais no atalho
    aceitaria calado o que a conferência recusa."""
    from dataforge.interpreter import _ACEITOS_POR_TIPO, _SEM_POSICAO

    interp = Interpreter()
    amostras = {int: 3, bool: True, float: 1.5, str: "a"}
    for tipo, aceitos in _ACEITOS_POR_TIPO.items():
        for classe in aceitos:
            interp._check_type(amostras[classe], tipo, "x", _SEM_POSICAO)


def test_bool_nao_passa_pelo_atalho_de_integer():
    """Em Python 'True' é um 'int'. O atalho compara o tipo EXATO, e por
    isso 'yes' num Integer continua recusado."""
    erro = recusa("x: Integer := 1\nx := yes\n")
    assert "Boolean" in erro.message


# ═══════════════════════════════════════════════════════════
#  O analisador acusa antes de rodar
# ═══════════════════════════════════════════════════════════

def test_o_check_acusa_a_reatribuicao_com_outro_tipo():
    assert ("tipo-na-reatribuicao", 3) in codigos("x: Integer := 1\nx := 2\nx := \"a\"\n")


def test_o_check_acusa_o_parametro_reatribuido():
    assert ("tipo-na-reatribuicao", 2) in codigos(
        "action f(a: Integer):\n    a := \"s\"\n    yield a\n")


def test_o_check_confere_o_resultado_da_composta():
    assert ("tipo-na-reatribuicao", 2) in codigos("n: Integer := 1\nn += 1.5\n")
    assert codigos("s: String := \"\"\ns += 1\n") == []


def test_o_check_acusa_o_campo_tipado():
    fonte = ("blueprint B(k: Integer):\n    action f():\n        self.k := \"t\"\n"
             "        yield 1\nb := spawn B(1)\nb.k := \"texto\"\nb.k := void\n")
    achados = codigos(fonte)
    assert ("tipo-do-campo", 3) in achados
    assert ("tipo-do-campo", 6) in achados
    assert len(achados) == 2, achados


def test_o_campo_generico_do_cabecalho_chega_ao_analisador():
    """O analisador lia 'tipos_do_cabecalho' do nó, e o nó chama isso de
    'constructor_types': os campos do cabeçalho nunca chegavam."""
    fonte = ("blueprint Caixa<T>(v: T):\n    action f():\n        yield 1\n"
             "c: Caixa<Integer> := spawn Caixa(1)\nc.v := \"t\"\n")
    assert ("generic-field", 5) in codigos(fonte)


def test_o_check_cala_no_que_e_legitimo():
    fonte = """
x: Integer := 1
x := 2
f: Float := 1.0
f := 2
y: Integer := 1
y: String := "redeclarado"
action g():
    shadow x := "sombra"
    yield x
action sem_tipo(a):
    a := "livre"
    yield a
"""
    assert codigos(fonte) == []
