"""
Testes do DataForge 4.0 — recursos do roadmap (Fase 1: núcleo).

Cobre interpolação, ternário, pertinência, coalescência, acesso seguro,
comprehensions, spread, desestruturação, records, enums, pattern matching,
generators, stack traces e o analisador estático.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import (  # noqa: E402
    NameError_, RuntimeError_, TypeError_,
)
from dataforge.interpreter import Interpreter  # noqa: E402
from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.tokens import TokenType  # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402


def run(source: str) -> str:
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


def diagnostics(source: str, filename="t.df"):
    return check_program(parse(tokenize(source)), filename)


def errors(source: str):
    return [d for d in diagnostics(source) if d.severity == 'error']


# ═══════════════════════════════════════════════════════════
#  Interpolação de strings
# ═══════════════════════════════════════════════════════════

def test_interpolacao_simples():
    assert run('nome := "Ana"\nout $"Ola {nome}"') == "Ola Ana"


def test_interpolacao_com_expressao():
    assert run('a := 2\nb := 3\nout $"{a} + {b} = {a + b}"') == "2 + 3 = 5"


def test_interpolacao_chama_acao():
    assert run("""
action dobro(n):
    yield n * 2
out $"dobro de 4 e {dobro(4)}"
""") == "dobro de 4 e 8"


def test_interpolacao_chaves_literais():
    assert run('x := 1\nout $"{{chave}} vale {x}"') == "{chave} vale 1"


def test_interpolacao_respeita_to_string():
    assert run('out $"{yes} {no} {void}"') == "yes no void"


def test_interpolacao_com_string_dentro():
    assert run('v := {"k": 7}\nout $"valor {v["k"]}"') == "valor 7"


def test_interpolacao_vazia_e_erro():
    from dataforge.errors import LexError
    with pytest.raises(LexError):
        run('out $"{}"')


# ═══════════════════════════════════════════════════════════
#  Ternário, pertinência, coalescência, acesso seguro
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("expr,esperado", [
    ('"par" given 4 % 2 is 0 otherwise "impar"', "par"),
    ('"par" given 3 % 2 is 0 otherwise "impar"', "impar"),
    ('1 given yes otherwise 2', 1),
])
def test_ternario(expr, esperado):
    assert env_of(f"x := {expr}")["x"] == esperado


def test_ternario_aninhado():
    assert env_of('''
n := 0
x := "positivo" given n bigger 0 otherwise "zero" given n is 0 otherwise "negativo"
''')["x"] == "zero"


@pytest.mark.parametrize("expr,esperado", [
    ("2 in [1, 2, 3]", True),
    ("9 in [1, 2, 3]", False),
    ("9 not in [1, 2, 3]", True),
    ('"a" in "casa"', True),
    ('"k" in {"k": 1}', True),
    ('"z" not in {"k": 1}', True),
])
def test_pertinencia(expr, esperado):
    assert env_of(f"x := {expr}")["x"] is esperado


def test_pertinencia_em_tipo_errado():
    with pytest.raises(TypeError_):
        run("out 1 in 5")


def test_coalescencia():
    assert env_of('a := void\nx := a ?? "padrao"')["x"] == "padrao"
    assert env_of('a := "tem"\nx := a ?? "padrao"')["x"] == "tem"
    # no e 0 sao valores, nao ausencia
    assert env_of('a := no\nx := a ?? "padrao"')["x"] is False
    assert env_of("a := 0\nx := a ?? 99")["x"] == 0


def test_acesso_seguro():
    assert run("""
record U:
    nome: String
u := void
out u?.nome ?? "sem nome"
u2 := U("Ana")
out u2?.nome
""") == "sem nome\nAna"


def test_chamada_segura():
    assert run('x := void\nout x?.upper() ?? "vazio"') == "vazio"


# ═══════════════════════════════════════════════════════════
#  Comprehensions
# ═══════════════════════════════════════════════════════════

def test_comprehension_lista():
    assert env_of("x := [n * 2 cycle n in [1, 2, 3]]")["x"] == [2, 4, 6]


def test_comprehension_com_filtro():
    assert env_of("x := [n cycle n in [1,2,3,4,5,6] given n % 2 is 0]")["x"] == [2, 4, 6]


def test_comprehension_aninhada():
    assert env_of("x := [a + b cycle a in [1,2] cycle b in [10,20]]")["x"] == [11, 21, 12, 22]


def test_comprehension_vault():
    assert env_of("x := {n: n * n cycle n in [1,2,3]}")["x"] == {1: 1, 2: 4, 3: 9}


def test_comprehension_sobre_string():
    assert env_of('x := [c.upper() cycle c in "abc"]')["x"] == ["A", "B", "C"]


def test_comprehension_sobre_vault_itera_chaves():
    assert env_of('x := [k cycle k in {"a": 1, "b": 2}]')["x"] == ["a", "b"]


def test_comprehension_nao_vaza_variavel():
    ambiente = env_of("y := [n cycle n in [1,2]]")
    assert "n" not in ambiente


# ═══════════════════════════════════════════════════════════
#  Spread e desestruturação
# ═══════════════════════════════════════════════════════════

def test_spread_em_lista():
    assert env_of("a := [1,2]\nb := [3]\nx := [...a, ...b, 4]")["x"] == [1, 2, 3, 4]


def test_spread_em_vault():
    assert env_of('x := {...{"a": 1}, "b": 2}')["x"] == {"a": 1, "b": 2}


def test_spread_em_chamada():
    assert run("""
action somar(a, b, c):
    yield a + b + c
args := [1, 2, 3]
out somar(...args)
""") == "6"


def test_spread_de_tipo_invalido():
    with pytest.raises(TypeError_):
        run("x := [...5]")


def test_desestruturacao_lista():
    ambiente = env_of("a, b := [1, 2]")
    assert (ambiente["a"], ambiente["b"]) == (1, 2)


def test_desestruturacao_com_resto():
    ambiente = env_of("a, ...r := [1, 2, 3, 4]")
    assert ambiente["a"] == 1 and ambiente["r"] == [2, 3, 4]


def test_desestruturacao_resto_no_meio():
    ambiente = env_of("a, ...meio, z := [1, 2, 3, 4, 5]")
    assert ambiente["a"] == 1 and ambiente["meio"] == [2, 3, 4] and ambiente["z"] == 5


def test_troca_de_valores():
    ambiente = env_of("a := 1\nb := 2\na, b := b, a")
    assert (ambiente["a"], ambiente["b"]) == (2, 1)


def test_desestruturacao_de_vault():
    ambiente = env_of('{nome, idade} := {"nome": "Ana", "idade": 30}')
    assert ambiente["nome"] == "Ana" and ambiente["idade"] == 30


def test_desestruturacao_quantidade_errada():
    with pytest.raises(RuntimeError_):
        run("a, b, c := [1, 2]")


# ═══════════════════════════════════════════════════════════
#  Records
# ═══════════════════════════════════════════════════════════

RECORD_BASE = """
record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"
"""


def test_record_construcao_posicional_e_nomeada():
    assert run(RECORD_BASE + '''
out Usuario("Ana", 30).nome
out Usuario(nome := "Bruno", idade := 25).idade
''') == "Ana\n25"


def test_record_valor_padrao():
    assert run(RECORD_BASE + 'out Usuario("Ana", 30).email') == "sem@email"


def test_record_igualdade_estrutural():
    assert env_of(RECORD_BASE + 'x := Usuario("Ana", 30) is Usuario("Ana", 30)')["x"] is True
    assert env_of(RECORD_BASE + 'x := Usuario("Ana", 30) is Usuario("Ana", 31)')["x"] is False


def test_record_e_imutavel():
    with pytest.raises(RuntimeError_):
        run(RECORD_BASE + 'u := Usuario("Ana", 30)\nu.idade := 31')


def test_record_with_gera_copia():
    assert run(RECORD_BASE + '''
u := Usuario("Ana", 30)
u2 := u with {"idade": 31}
out u.idade, u2.idade
''') == "30 31"


def test_record_with_campo_inexistente():
    with pytest.raises(NameError_):
        run(RECORD_BASE + 'u := Usuario("Ana", 30)\nu with {"salario": 1}')


def test_record_verifica_tipo_do_campo():
    with pytest.raises(TypeError_):
        run(RECORD_BASE + 'Usuario(42, 30)')


def test_record_campo_faltando():
    with pytest.raises(TypeError_):
        run(RECORD_BASE + 'Usuario("Ana")')


def test_record_typeof_e_o_nome():
    assert run(RECORD_BASE + 'out typeof(Usuario("Ana", 30))') == "Usuario"


def test_record_com_metodo():
    assert run('''
record Retangulo:
    largura: Number
    altura: Number

    action area():
        yield self.largura * self.altura

out Retangulo(3, 4).area()
''') == "12"


def test_record_desestruturado():
    ambiente = env_of(RECORD_BASE + 'u := Usuario("Ana", 30)\n{nome, idade} := u')
    assert ambiente["nome"] == "Ana" and ambiente["idade"] == 30


# ═══════════════════════════════════════════════════════════
#  Enums
# ═══════════════════════════════════════════════════════════

ENUM_BASE = """
enum Status:
    Ativo
    Inativo
    Pendente := "pend"
"""


def test_enum_acesso_e_valor():
    assert run(ENUM_BASE + '''
out Status.Ativo
out Status.Ativo.name, Status.Ativo.value, Status.Ativo.index
out Status.Pendente.value
''') == "Status.Ativo\nAtivo Ativo 0\npend"


def test_enum_igualdade():
    assert env_of(ENUM_BASE + "x := Status.Ativo is Status.Ativo")["x"] is True
    assert env_of(ENUM_BASE + "x := Status.Ativo is Status.Inativo")["x"] is False


def test_enum_utilitarios():
    assert run(ENUM_BASE + '''
out Status.names()
out Status.count()
out Status.has("Ativo"), Status.has("Nao")
out Status.from_value("pend").name
''') == "[Ativo, Inativo, Pendente]\n3\nyes no\nPendente"


def test_enum_membro_inexistente():
    with pytest.raises(NameError_):
        run(ENUM_BASE + "out Status.Cancelado")


def test_enum_typeof():
    assert run(ENUM_BASE + "out typeof(Status.Ativo)") == "Status"


# ═══════════════════════════════════════════════════════════
#  Pattern matching
# ═══════════════════════════════════════════════════════════

MATCH_BASE = """
record Ponto:
    x: Integer
    y: Integer

action classificar(v):
    match v:
        point 0:
            yield "zero"
        point Integer as n when n bigger 100:
            yield "grande"
        point Integer:
            yield "inteiro"
        point String as s:
            yield "texto:" + s
        point [a, b]:
            yield "par"
        point [primeiro, ...resto]:
            yield "lista de " + str(len(resto) + 1)
        point Ponto(x, y):
            yield "ponto " + str(x) + "," + str(y)
        point {"tipo": t}:
            yield "vault " + t
        point _:
            yield "outro"
"""


@pytest.mark.parametrize("entrada,esperado", [
    ("0", "zero"),
    ("7", "inteiro"),
    ("500", "grande"),
    ('"ab"', "texto:ab"),
    ("[1, 2]", "par"),
    ("[1, 2, 3]", "lista de 3"),
    ("Ponto(3, 4)", "ponto 3,4"),
    ('{"tipo": "x"}', "vault x"),
    ("3.5", "outro"),
])
def test_pattern_matching(entrada, esperado):
    assert run(MATCH_BASE + f"out classificar({entrada})") == esperado


def test_pattern_or():
    assert run("""
action f(v):
    match v:
        point 1 or 2 or 3:
            yield "pequeno"
        default:
            yield "outro"
out f(2), f(9)
""") == "pequeno outro"


def test_pattern_guarda_falha_cai_no_proximo():
    assert run("""
action f(n):
    match n:
        point x when x bigger 10:
            yield "grande"
        point x:
            yield "pequeno"
out f(5), f(50)
""") == "pequeno grande"


def test_pattern_vault_nao_casa_com_sequencia():
    assert run("""
action f(v):
    match v:
        point [a]:
            yield "lista"
        point {"k": x}:
            yield "vault"
        default:
            yield "outro"
out f({"k": 1})
""") == "vault"


def test_pattern_enum():
    assert run(ENUM_BASE + """
action f(s):
    match s:
        point Status.Ativo:
            yield "ligado"
        point Status.Inativo:
            yield "desligado"
        default:
            yield "?"
out f(Status.Ativo), f(Status.Inativo), f(Status.Pendente)
""") == "ligado desligado ?"


def test_pattern_campos_nomeados():
    assert run(MATCH_BASE + """
action g(p):
    match p:
        point Ponto(y := 0):
            yield "no eixo x"
        point Ponto:
            yield "fora do eixo"
        default:
            yield "?"
out g(Ponto(5, 0)), g(Ponto(5, 2))
""") == "no eixo x fora do eixo"


# ═══════════════════════════════════════════════════════════
#  Generators (stream action + emit)
# ═══════════════════════════════════════════════════════════

def test_generator_finito():
    assert run("""
stream action contar(ate):
    cycle i from 1 to ate:
        emit i
out contar(4).to_cluster()
""") == "[1, 2, 3, 4]"


def test_generator_infinito_e_preguicoso():
    assert run("""
stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1
out naturais().take(5)
""") == "[0, 1, 2, 3, 4]"


def test_generator_fibonacci():
    assert run("""
stream action fib():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b
out fib().take(8)
""") == "[0, 1, 1, 2, 3, 5, 8, 13]"


def test_generator_consumido_por_cycle():
    assert run("""
stream action g():
    emit 1
    emit 2
cycle v in g():
    out v
""") == "1\n2"


def test_generator_em_comprehension():
    assert run("""
stream action g():
    cycle i from 1 to 3:
        emit i
out [x * 10 cycle x in g()]
""") == "[10, 20, 30]"


def test_generator_next_incremental():
    assert run("""
stream action g():
    emit "a"
    emit "b"
s := g()
out s.next(), s.next(), s.next()
""") == "a b void"


def test_generator_com_halt():
    assert run("""
stream action g():
    cycle i from 1 to 100:
        given i bigger 3:
            halt
        emit i
out g().to_cluster()
""") == "[1, 2, 3]"


def test_emit_fora_de_generator_imprime():
    assert run('emit "legado"') == "legado"


def test_observe_aceita_stream():
    """'observe' precisa consumir o DFStream de um 'stream action'."""
    assert run("""
stream action g():
    emit 1
    emit 2
total := 0
observe v in g():
    total += v
out total
""") == "3"


@pytest.mark.parametrize("fonte,esperado", [
    ("[1, 2, 3]", "6"),
    ('{"a": 1, "b": 2}', "ab"),
    ("stream([1, 2, 3])", "6"),
])
def test_observe_sobre_varias_fontes(fonte, esperado):
    corpo = "total += v" if esperado == "6" else "total += v"
    inicial = "0" if esperado == "6" else '""'
    assert run(f"""
total := {inicial}
observe v in {fonte}:
    {corpo}
out total
""") == esperado


def test_observe_recusa_tipo_invalido():
    with pytest.raises(TypeError_):
        run("observe v in 5:\n    out v")


def test_typeof_de_stream():
    assert run("""
stream action g():
    emit 1
out typeof(g())
""") == "Stream"


# ═══════════════════════════════════════════════════════════
#  Stack traces
# ═══════════════════════════════════════════════════════════

def test_stack_trace_registra_cadeia():
    fonte = """
action c(v):
    yield 100 / v
action b(v):
    yield c(v)
action a(v):
    yield b(v)
a(0)
"""
    interp = Interpreter()
    with pytest.raises(RuntimeError_) as exc:
        with redirect_stdout(io.StringIO()):
            interp.run(parse(tokenize(fonte)), filename="t.df")
    nomes = [q.name for q in exc.value.stack]
    assert nomes == ["a", "b", "c"]


def test_render_do_erro_mostra_linha_e_pilha():
    fonte = "action f():\n    yield 1 / 0\nf()"
    interp = Interpreter()
    with pytest.raises(RuntimeError_) as exc:
        interp.run(parse(tokenize(fonte)), filename="t.df")
    texto = exc.value.render(color=False, source_lines=fonte.splitlines())
    assert "Division by zero" in texto
    assert "pilha de chamadas" in texto
    assert "em f" in texto
    assert "yield 1 / 0" in texto


# ═══════════════════════════════════════════════════════════
#  Analisador estático
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("fonte,codigo", [
    ("out naoExiste", "undefined-name"),
    ("action f(a, b):\n    yield a\nf(1)", "arity"),
    ("action f(a):\n    yield a\nf(1, 2)", "arity"),
    ("x: Integer := \"texto\"", "type-mismatch"),
    ("x: Intger := 1", "unknown-type"),
    ("steady A := 1\nA := 2", "steady-reassign"),
    ("out 1 + [2]", "operator-types"),
    ("out \"a\" - 1", "operator-types"),
    ("record R:\n    a: Integer\nR()", "record-arity"),
    ("record R:\n    a: Integer\nR(1).b", "unknown-field"),
    ("enum E:\n    A\nout E.B", "unknown-member"),
    ("halt", "halt-outside-loop"),
    ("yield 1", "yield-outside-action"),
    ("cycle x in 5:\n    out x", "cycle-not-iterable"),
])
def test_checker_detecta(fonte, codigo):
    achados = [d.code for d in errors(fonte)]
    assert codigo in achados, f"esperava {codigo}, obtive {achados}"


@pytest.mark.parametrize("fonte", [
    'nome := "Ana"\nout $"Ola {nome}"',
    "x := [n cycle n in [1,2] given n bigger 0]",
    "a, b := [1, 2]\nout a + b",
    "record R:\n    a: Integer\nout R(1).a",
    "enum E:\n    A\nout E.A.name",
    "stream action g():\n    emit 1\nout g().to_cluster()",
    "action f(n: Integer) -> Integer:\n    yield n * 2\nout f(3)",
    'out "x" + 1',
    "out 1.5 + 2",
    "blueprint V(x):\n    action add(o):\n        yield spawn V(self.x + o.x)\nout spawn V(1) + spawn V(2)",
])
def test_checker_nao_reclama_de_codigo_valido(fonte):
    assert errors(fonte) == [], [d.message for d in errors(fonte)]


def test_checker_sugere_nome_parecido():
    achados = errors("action somar(a, b):\n    yield a + b\nsommar(1, 2)")
    assert any("somar" in d.hint for d in achados)


def test_checker_avisa_codigo_inalcancavel():
    avisos = [d.code for d in diagnostics(
        "action f():\n    yield 1\n    out 2") if d.severity == 'warning']
    assert "unreachable" in avisos


def test_checker_avisa_retorno_ausente():
    avisos = [d.code for d in diagnostics(
        'action f() -> Integer:\n    out "nada"') if d.severity == 'warning']
    assert "missing-return" in avisos


def test_checker_rebaixa_erros_dentro_de_monitor():
    fonte = "monitor:\n    x := 1 / 0\nhandle e:\n    out e"
    assert errors(fonte) == []
    assert any(d.severity == 'warning' for d in diagnostics(fonte))


# ═══════════════════════════════════════════════════════════
#  O operador '//' e a alternativa '~/'
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("linha,eh_divisao", [
    ("x := 7 // 2", True),
    ("x := 7 ~/ 2", True),
    ("x := (a + b) // 2", True),
    ("x := (a * b) // mdc(a, b)", True),
    ("x := total // len(itens)", True),
    ("x := 3  // backtrack", False),
    ("x := 3  // marcar como caminho", False),
    ("x := a // b", False),
    ("x := 1 // TODO rever", False),
])
def test_barra_dupla_e_comentario_por_padrao(linha, eh_divisao):
    tipos = [t.type for t in tokenize(linha)]
    assert (TokenType.FLOOR_DIV in tipos) is eh_divisao


# ═══════════════════════════════════════════════════════════
#  Biblioteca padrão 4.0
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("nome", [
    "Arcane.Time", "Arcane.OS", "Arcane.Process", "Arcane.Logging",
    "Arcane.Crypto", "Arcane.Collections", "Arcane.Serialization",
])
def test_modulos_novos_carregam(nome):
    from dataforge.stdlib import get_module
    modulo = get_module(nome)
    assert isinstance(modulo, dict) and len(modulo) > 5


def test_transacao_rollback_desfaz():
    """'execute' não pode confirmar sozinho dentro de uma transação."""
    from dataforge.stdlib import get_module
    DB = get_module("Arcane.Database")
    conn = DB["memory"]()
    DB["execute"](conn, "CREATE TABLE t (n INTEGER)")
    DB["execute"](conn, "INSERT INTO t VALUES (1)")

    DB["begin"](conn)
    DB["execute"](conn, "INSERT INTO t VALUES (2)")
    assert DB["count"](conn, "t") == 2
    DB["rollback"](conn)
    assert DB["count"](conn, "t") == 1, "o rollback precisa desfazer"

    DB["begin"](conn)
    DB["execute"](conn, "INSERT INTO t VALUES (3)")
    DB["commit"](conn)
    assert DB["count"](conn, "t") == 2, "o commit precisa manter"
    DB["close"](conn)


def test_crypto_verifica_senha():
    from dataforge.stdlib import get_module
    C = get_module("Arcane.Crypto")
    guardada = C["hash_password"]("segredo")
    assert C["verify_password"]("segredo", guardada) is True
    assert C["verify_password"]("outra", guardada) is False


def test_time_arredonda_mes_curto():
    from dataforge.stdlib import get_module
    T = get_module("Arcane.Time")
    fevereiro = T["add_months"](T["date"](2026, 1, 31), 1)
    assert fevereiro["day"] == 28, "31/01 + 1 mês grampeia em 28/02"


def test_serialization_toml_roundtrip():
    from dataforge.stdlib import get_module
    S = get_module("Arcane.Serialization")
    dados = {"app": "x", "n": 4, "sec": {"a": True}}
    assert S["from_toml"](S["to_toml"](dados)) == dados


def test_collections_dijkstra():
    from dataforge.stdlib import get_module
    C = get_module("Arcane.Collections")
    g = C["graph"]()
    g.add_edge("a", "b", 1)
    g.add_edge("b", "c", 2)
    g.add_edge("a", "c", 5)
    rota = g.shortest_path("a", "c")
    assert rota["path"] == ["a", "b", "c"] and rota["cost"] == 3


# ═══════════════════════════════════════════════════════════
#  Módulos e imports seletivos
# ═══════════════════════════════════════════════════════════

def test_import_seletivo_da_stdlib():
    assert run("""
adopt Arcane.Math.{sqrt, factorial}
out sqrt(16), factorial(4)
""") == "4.0 24"


def test_import_com_apelido():
    assert run("""
adopt {sqrt as raiz} from Arcane.Math
out raiz(25)
""") == "5.0"


def test_import_de_simbolo_inexistente():
    from dataforge.errors import ImportError_
    with pytest.raises(ImportError_):
        run("adopt Arcane.Math.{nao_existe}")


# ═══════════════════════════════════════════════════════════
#  Ferramentas
# ═══════════════════════════════════════════════════════════

def test_formatter_e_idempotente():
    from dataforge.formatter import format_source
    fonte = "action  f( a,b ):\n      yield a+b\nx:=f( 1,2 )\n"
    uma = format_source(fonte)
    assert format_source(uma) == uma
    assert "action f(a, b):" in uma
    assert "x := f(1, 2)" in uma


def test_formatter_preserva_semantica():
    from dataforge.formatter import format_source
    fonte = 'action dobro(n):\n    yield n * 2\nout dobro(21)\n'
    assert run(format_source(fonte)) == run(fonte)


def test_linter_encontra_variavel_sem_uso():
    from dataforge.linter import lint_program
    fonte = "action f():\n    sobrando := 1\n    yield 2\nout f()"
    codigos = [d.code for d in lint_program(parse(tokenize(fonte)), "t.df", fonte)]
    assert "unused-variable" in codigos


def test_linter_nao_reclama_de_codigo_limpo():
    from dataforge.linter import lint_program
    fonte = 'action dobro(n):\n    yield n * 2\nout dobro(21)\n'
    assert lint_program(parse(tokenize(fonte)), "t.df", fonte) == []


def test_docgen_extrai_declaracoes(tmp_path):
    from dataforge.docgen import gerar_doc
    arquivo = tmp_path / "m.df"
    arquivo.write_text(
        "// Uma biblioteca.\n\n"
        "// Soma dois numeros.\n"
        "action somar(a: Integer, b: Integer) -> Integer:\n"
        "    yield a + b\n\n"
        "record P:\n    x: Integer\n",
        encoding="utf-8")
    texto = gerar_doc(str(arquivo))
    assert "somar" in texto
    assert "Soma dois numeros." in texto
    assert "`P`" in texto


def test_project_manifest(tmp_path):
    from dataforge import project
    project.criar(str(tmp_path), "app", "desc", "autor")
    m = project.carregar(str(tmp_path))
    assert m.name == "app"
    assert m.entry == "src/main.df"
    assert m.scripts["test"] == "test tests/"
    ok, _ = m.requires("4.0.0")
    assert ok


def test_collections_ordena_records():
    """sort_by_field precisa ler campos de records, não só de vaults."""
    assert run("""
adopt Arcane.Collections as Col
record P:
    nome: String
    n: Integer
itens := [P("c", 3), P("a", 1), P("b", 2)]
out Col.sort_by_field(itens, "n") >> morph p: p.nome
out Col.sort_by_field(itens, "n", yes) >> morph p: p.nome
""") == "[a, b, c]\n[c, b, a]"


def test_collections_agrupa_records():
    assert run("""
adopt Arcane.Collections as Col
record P:
    tipo: String
    v: Integer
g := Col.group_by([P("a", 1), P("b", 2), P("a", 3)], "tipo")
out len(g["a"]), len(g["b"])
""") == "2 1"


def test_analytics_agrupa_records():
    assert run("""
adopt Arcane.Analytics as An
record P:
    setor: String
    v: Integer
g := An.group_by([P("x", 1), P("y", 2), P("x", 3)], "setor")
out len(g["x"])
""") == "2"


def test_ordenacao_tolera_valores_mistos():
    """Ordenar com void ou tipos misturados não pode estourar."""
    assert run("""
adopt Arcane.Collections as Col
itens := [{"n": 3}, {"n": void}, {"n": 1}]
out len(Col.sort_by_field(itens, "n"))
""") == "3"


# ═══════════════════════════════════════════════════════════
#  Regressões encontradas ao escrever os exercícios 4.0
# ═══════════════════════════════════════════════════════════

def test_checker_conhece_import_seletivo():
    """Nomes de 'adopt M.{a}' precisam existir para o analisador."""
    from dataforge.typechecker import check_program
    fonte = "adopt Arcane.Math.{sqrt}\nout sqrt(16)"
    erros = [d for d in check_program(parse(tokenize(fonte)), "t.df")
             if d.severity == 'error']
    assert erros == [], [d.message for d in erros]


def test_checker_nao_confunde_metodo_com_acao_global():
    """Um método 'descrever()' não é a ação global 'descrever(v)'."""
    from dataforge.typechecker import check_program
    fonte = """
blueprint Forma:
    action descrever():
        yield "forma"

action descrever(v):
    yield str(v)

out descrever(42)
"""
    erros = [d for d in check_program(parse(tokenize(fonte)), "t.df")
             if d.severity == 'error']
    assert erros == [], [d.message for d in erros]


@pytest.mark.parametrize("fonte", ["x := 7 // 2\n", "x := a ~/ b\n",
                                   "x := total // len(xs)\n"])
def test_formatter_reimprime_floor_div_como_til_barra(fonte):
    """Reimprimir '//' faria a linha virar comentário na próxima passagem."""
    from dataforge.formatter import format_source
    saida = format_source(fonte)
    assert "~/" in saida, saida
    assert "//" not in saida, saida
    assert format_source(saida) == saida


def test_formatter_mantem_comentario_com_barra_dupla():
    """'a // b' é comentário pela regra do 4.0 — deve continuar comentário."""
    from dataforge.formatter import format_source
    saida = format_source("x := a  // b\n")
    assert "// b" in saida
    assert format_source(saida) == saida


def test_formatter_preserva_string_interpolada_com_cerquilha():
    """'#' dentro de $"..." não é comentário."""
    from dataforge.formatter import format_source
    fonte = 'n := 3\nout $"{"#".repeat(n)} ({n})"\n'
    uma = format_source(fonte)
    assert format_source(uma) == uma
    assert run(uma) == run(fonte) == "### (3)"


def test_formatter_preserva_quebra_em_interpolada():
    from dataforge.formatter import format_source
    fonte = 'action f(t):\n    yield $"{t}\\nfim"\nout f("a")\n'
    uma = format_source(fonte)
    assert format_source(uma) == uma
    assert run(uma) == run(fonte)


@pytest.mark.parametrize("linha,esperado", [
    ('out "x", y   // comentario', '// comentario'),
    ('x := 7 // 2', ''),
    ('y := a  // nota', '// nota'),
    ('out $"{a}"  # real', '# real'),
    ('out "tem # dentro"  // com', '// com'),
])
def test_formatter_extrai_comentario_corretamente(linha, esperado):
    from dataforge.formatter import Formatter
    assert Formatter('')._extrair_comentario(linha) == esperado


# ── lint: caminho do Windows entre aspas ──────────────────────

def _codigos_de_lint(fonte):
    from dataforge.linter import lint_program
    return [d.code for d in lint_program(parse(tokenize(fonte)), "t.df", fonte)]


def test_lint_avisa_caminho_de_windows_com_escape():
    r"""`"C:\temp\notas"` não é o que está escrito.

    `\t` é uma tabulação e `\n` é uma quebra de linha, então o texto
    chega ao programa como `C:<TAB>emp<NL>otas`. Nada reclama — o
    arquivo simplesmente não é encontrado, e a mensagem fala do caminho
    deformado, que ninguém reconhece.

    Foi assim que um teste do Kiln caiu só no Windows: a pasta de
    templates entrava num literal.
    """
    assert "windows-path" in _codigos_de_lint(r'pasta := "C:\temp\notas"')


def test_lint_nao_avisa_com_barra_normal():
    """A forma certa não pode ser marcada — o Windows aceita as duas."""
    assert "windows-path" not in _codigos_de_lint('pasta := "C:/temp/notas"')


def test_lint_nao_avisa_contrabarra_dobrada():
    r"""Quem escreveu `\\` já sabe o que está fazendo.

    Marcar isso seria um falso alarme, e falso alarme ensina a ignorar a
    regra inteira.
    """
    assert "windows-path" not in _codigos_de_lint(r'pasta := "C:\\temp\\notas"')


def test_lint_nao_confunde_texto_comum_com_caminho():
    """`\n` num texto qualquer é exatamente o que se quis dizer."""
    assert "windows-path" not in _codigos_de_lint(
        r'msg := "linha um\nlinha dois"')
    assert "windows-path" not in _codigos_de_lint(r'sep := "a\tb"')


def test_a_mensagem_mostra_a_correcao():
    from dataforge.linter import lint_program

    fonte = r'pasta := "C:\temp\notas"'
    avisos = [d for d in lint_program(parse(tokenize(fonte)), "t.df", fonte)
              if d.code == "windows-path"]
    assert len(avisos) == 1
    assert "C:/temp/notas" in avisos[0].hint, "a dica precisa trazer a forma certa"
