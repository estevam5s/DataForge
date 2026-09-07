"""Testes de regressao do DataForge (pytest).

Cobre os pontos que ja quebraram: sinais de controle, precedencia, escopo,
tipos, aridade, o operador '//' ambiguo e a integridade da stdlib.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import (  # noqa: E402
    DataForgeError, ImportError_, ParseError, StackOverflowError_,
    TriggerError, TypeError_,
)
from dataforge.interpreter import Interpreter  # noqa: E402
from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.tokens import TokenType  # noqa: E402


def run(source: str) -> str:
    """Executa codigo DataForge e devolve o que foi impresso."""
    interp = Interpreter()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        interp.run(parse(tokenize(source)))
    return buffer.getvalue().strip()


def env_of(source: str) -> dict:
    interp = Interpreter()
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize(source)))
    return interp.global_env.variables


# ── Sinais de controle nao sao erros ───────────────────────

def test_yield_atravessa_monitor():
    """'yield' dentro de monitor retorna da acao, nao vira erro capturado."""
    assert run("""
action f():
    monitor:
        yield 42
    handle e:
        out "nao deveria"
out f()
""") == "42"


def test_skip_e_halt_atravessam_monitor():
    assert run("""
cycle i from 1 to 3:
    monitor:
        given i is 2:
            skip
        out i
    handle e:
        out "erro"
""") == "1\n3"


def test_monitor_sem_handle_propaga():
    with pytest.raises(TriggerError):
        run("""
monitor:
    trigger "boom"
ensure:
    out "limpou"
""")


# ── handle tipado e objeto de erro ─────────────────────────

def test_handle_tipado_filtra():
    saida = run("""
monitor:
    monitor:
        trigger "do usuario"
    handle RuntimeError as e:
        out "errado"
handle e:
    out e.type
""")
    assert saida == "TriggerError"


def test_erro_expoe_tipo_e_mensagem():
    assert run("""
monitor:
    x := 1 / 0
handle e:
    out e.type, e.message
""") == "RuntimeError Division by zero"


# ── Precedencia e associatividade ──────────────────────────

@pytest.mark.parametrize("expr,esperado", [
    ("2 ** 3 ** 2", 512),
    ("-2 ** 2", -4),
    ("2 + 3 * 4", 14),
    ("(2 + 3) * 4", 20),
    ("2 ** -1", 0.5),
    ("+7", 7),
])
def test_precedencia(expr, esperado):
    assert env_of(f"x := {expr}")["x"] == esperado


def test_comparacao_encadeada():
    assert env_of("a := 1 smaller 5 smaller 10")["a"] is True
    assert env_of("b := 10 < 5 < 20")["b"] is False


def test_aliases_de_comparacao():
    assert env_of("a := 3 > 2")["a"] is True
    assert env_of("b := 2 >= 2")["b"] is True
    assert env_of("c := 1 <= 0")["c"] is False


# ── O operador '//' ambiguo ────────────────────────────────

@pytest.mark.parametrize("linha,eh_divisao", [
    ("x := 7 // 2", True),
    ("x := 7 ~/ 2", True),
    ("x := (a + b) // 2", True),
    ("x := 3  // marcar como caminho", False),
    ("x := 3  // isso e um comentario", False),
])
def test_barra_dupla(linha, eh_divisao):
    tipos = [t.type for t in tokenize(linha)]
    assert (TokenType.FLOOR_DIV in tipos) is eh_divisao


def test_divisao_inteira_resultado():
    assert env_of("x := 17 ~/ 5")["x"] == 3
    assert env_of("y := 17 // 5")["y"] == 3


# ── Fatiamento e encadeamento ──────────────────────────────

def test_fatiamento():
    vars = env_of("""
l := [1, 2, 3, 4, 5]
a := l[1:3]
b := l[:2]
c := l[3:]
d := l[::2]
e := l[::-1]
f := "DataForge"[0:4]
""")
    assert vars["a"] == [2, 3]
    assert vars["b"] == [1, 2]
    assert vars["c"] == [4, 5]
    assert vars["d"] == [1, 3, 5]
    assert vars["e"] == [5, 4, 3, 2, 1]
    assert vars["f"] == "Data"


def test_chamada_encadeada():
    assert run("""
action fabrica(n):
    action interna(x):
        yield x + n
    yield interna
out fabrica(5)(3)
""") == "8"


# ── Lambdas e decoradores ──────────────────────────────────

def test_lambda_tres_formas():
    vars = env_of("""
a := lambda x: x * 2
b := lambda p, q => p + q
c := lambda: 42
r1 := a(21)
r2 := b(2, 3)
r3 := c()
""")
    assert (vars["r1"], vars["r2"], vars["r3"]) == (42, 5, 42)


def test_defer_roda_mesmo_quando_a_acao_falha():
    """'defer' precisa rodar em todo caminho de saida, inclusive por erro."""
    assert run("""
ordem := []
action falha():
    defer:
        ordem.append("defer")
    ordem.append("antes")
    trigger "boom"

monitor:
    falha()
handle e:
    ordem.append("tratado")
out ordem
""") == "[antes, defer, tratado]"


def test_defer_lifo():
    assert run("""
ordem := []
action f():
    defer:
        ordem.append("primeiro")
    defer:
        ordem.append("segundo")
    yield void
f()
out ordem
""") == "[segundo, primeiro]"


def test_decorador_mark():
    assert run("""
action dobrar_saida(fn):
    action envolvida(x):
        yield fn(x) * 2
    yield envolvida

mark @dobrar_saida
action id(x):
    yield x
out id(10)
""") == "20"


# ── Atribuicao composta ────────────────────────────────────

def test_atribuicao_composta():
    vars = env_of("""
x := 10
x += 5
x *= 2
x -= 10
x %= 7
""")
    # 10 +5 = 15, *2 = 30, -10 = 20, %7 = 6
    assert vars["x"] == 6


# ── Tipos e aridade ────────────────────────────────────────

def test_anotacao_de_tipo_aceita_valor_correto():
    assert env_of('n: Integer := 5')["n"] == 5


def test_anotacao_de_tipo_rejeita_valor_errado():
    with pytest.raises(TypeError_):
        run('n: Integer := "cinco"')


def test_parametro_tipado():
    with pytest.raises(TypeError_):
        run("""
action f(n: Integer):
    yield n
f("x")
""")


def test_retorno_tipado():
    with pytest.raises(TypeError_):
        run("""
action f() -> Integer:
    yield "texto"
f()
""")


def test_integer_aceito_onde_float_e_esperado():
    assert run("""
action f(x: Float) -> Float:
    yield x
out f(3)
""") == "3"


def test_argumento_faltando():
    with pytest.raises(TypeError_):
        run("""
action f(a, b):
    yield a + b
f(1)
""")


def test_argumento_sobrando():
    with pytest.raises(TypeError_):
        run("""
action f(a):
    yield a
f(1, 2)
""")


def test_argumento_desconhecido():
    with pytest.raises(TypeError_):
        run("""
action f(a):
    yield a
f(z := 1)
""")


# ── Recursao ───────────────────────────────────────────────

def test_recursao_infinita_vira_erro_do_dataforge():
    with pytest.raises(StackOverflowError_):
        run("""
action r(n):
    yield r(n + 1)
r(1)
""")


def test_recursao_profunda_legitima():
    assert run("""
action contar(n):
    given n smaller_eq 0:
        yield 0
    yield 1 + contar(n - 1)
out contar(500)
""") == "500"


# ── Imports ────────────────────────────────────────────────

def test_import_inexistente_dispara():
    with pytest.raises(ImportError_):
        run("adopt Arcane.NaoExiste as X")


def test_import_valido():
    assert run("""
adopt Arcane.Math as M
out M.sqrt(16)
""") == "4.0"


@pytest.mark.parametrize("nome", [
    "Arcane.IO", "Arcane.Math", "Arcane.Web", "Arcane.Cortex", "Arcane.Data",
    "Arcane.Regex", "Arcane.Test", "Arcane.Functional", "Arcane.Async",
    "Arcane.Text", "Arcane.Analytics", "Arcane.Database", "Arcane.Http",
])
def test_todos_os_modulos_da_stdlib_carregam(nome):
    from dataforge.stdlib import get_module
    modulo = get_module(nome)
    assert isinstance(modulo, dict) and len(modulo) > 1


# ── Blueprints ─────────────────────────────────────────────

def test_setup_roda_junto_com_parametros_de_construtor():
    assert run("""
blueprint P(nome):
    action setup(nome):
        self.itens := []
    action add(x):
        self.itens.append(x)
        yield len(self.itens)
p := spawn P("a")
p.add(1)
p.add(2)
out p.nome, len(p.itens)
""") == "a 2"


def test_str_usa_to_string_do_blueprint():
    assert run("""
blueprint V(x):
    action toString():
        yield "V(" + str(self.x) + ")"
out str(spawn V(7))
""") == "V(7)"


def test_sobrecarga_de_operador():
    assert run("""
blueprint N(v):
    action add(o):
        yield spawn N(self.v + o.v)
    action toString():
        yield str(self.v)
out str(spawn N(2) + spawn N(3))
""") == "5"


# ── Palavras reservadas ────────────────────────────────────

@pytest.mark.parametrize("nome", ["each", "link", "listen", "claim", "abstract"])
def test_palavras_liberadas_sao_identificadores(nome):
    assert env_of(f"{nome} := 1")[nome] == 1


@pytest.mark.parametrize("codigo", ["no := 1", "frame := 2", "stream := 3"])
def test_palavra_reservada_tem_mensagem_clara(codigo):
    with pytest.raises(ParseError) as exc:
        run(codigo)
    assert "reserved keyword" in str(exc.value)


@pytest.mark.parametrize("nome", ["cluster", "vault", "range"])
def test_builtins_com_nome_de_tipo_sao_chamaveis(nome):
    """Estes eram reservados e nao podiam ser chamados apesar de serem builtins."""
    assert run(f'out {nome}') != ""


def test_cluster_vault_range_funcionam():
    assert env_of('a := cluster(["a", "b"])')["a"] == ["a", "b"]
    assert env_of('b := vault({"k": 1})')["b"] == {"k": 1}
    assert env_of("c := range(1, 4)")["c"] == [1, 2, 3]


# ── Erros de Python nao vazam ──────────────────────────────

@pytest.mark.parametrize("codigo", [
    "cycle x in 5:\n    out x",
    "cycle x in void:\n    out x",
    "x := 5\nout x[0]",
    "observe x in 5:\n    out x",
])
def test_erro_de_tipo_e_do_dataforge_nao_do_python(codigo):
    with pytest.raises(TypeError_):
        run(codigo)


# ── Pipelines ──────────────────────────────────────────────

def test_pipeline_multilinha():
    assert env_of("""
r := [1, 2, 3, 4, 5, 6]
    >> sift n: n % 2 is 0
    >> morph n: n * 10
""")["r"] == [20, 40, 60]


def test_pipeline_distill_com_inicial():
    assert env_of("x := [1, 2, 3] >> distill a, v: a + v 100")["x"] == 106


# ── Erros de sintaxe reportam posicao ──────────────────────

def test_erro_de_sintaxe_tem_linha():
    with pytest.raises(DataForgeError) as exc:
        run("action f(\nout 1")
    assert exc.value.line > 0


# ── Documentação em sincronia com o código ─────────────────

def test_referencia_lista_exatamente_as_palavras_reservadas():
    """doc/REFERENCIA.md §1.6 precisa bater com KEYWORDS."""
    import re
    from dataforge.tokens import KEYWORDS

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc = open(os.path.join(raiz, "doc", "REFERENCIA.md"), encoding="utf-8").read()
    bloco = re.search(r"### 1\.6 Palavras reservadas \(\d+\)\n\n```\n(.*?)```",
                      doc, re.S)
    assert bloco, "seção 1.6 não encontrada em doc/REFERENCIA.md"
    listadas = set(bloco.group(1).split())
    assert listadas == set(KEYWORDS), (
        f"faltando no doc: {sorted(set(KEYWORDS) - listadas)}; "
        f"a mais no doc: {sorted(listadas - set(KEYWORDS))}")


def test_referencia_lista_todas_as_funcoes_embutidas():
    """doc/REFERENCIA.md §13 precisa cobrir builtins.py."""
    import re
    from dataforge.builtins import get_builtins

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc = open(os.path.join(raiz, "doc", "REFERENCIA.md"), encoding="utf-8").read()
    secao = doc[doc.index("## 13. Funções embutidas"):doc.index("## 14.")]
    listadas = set(re.findall(r"`([A-Za-z_0-9]+)`", secao)) - {"adopt"}
    reais = set(get_builtins())
    assert not (reais - listadas), f"não documentadas: {sorted(reais - listadas)}"
    assert not (listadas - reais), f"documentadas mas inexistentes: {sorted(listadas - reais)}"
