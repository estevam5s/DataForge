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
""") == "DivisionByZeroError Division by zero."


def test_erro_especifico_ainda_e_pego_pela_familia():
    """O tipo ficou especifico; 'handle RuntimeError' nao pode ter parado.

    Se a especializacao dos erros quebrasse a captura pela familia,
    todo 'handle' escrito antes dela deixaria de funcionar em silencio.
    """
    assert run("""
monitor:
    x := 1 / 0
handle RuntimeError as e:
    out "peguei"
""") == "peguei"


def test_excecao_do_python_vira_erro_capturavel():
    """Regressao: '[].min()' subia como 'Internal Error' incapturavel.

    A mensagem vinha do Python ('min() iterable argument is empty') e
    'monitor' nao a via, porque nao era um erro da linguagem.
    """
    assert run("""
monitor:
    out [].min()
handle EmptyCollectionError as e:
    out "capturado"
""") == "capturado"


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

# 'abstract' saiu desta lista no 4.1: agora e consumida por
# 'abstract action' e 'abstract blueprint'.
@pytest.mark.parametrize("nome", ["each", "link", "listen", "claim"])
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
    # Nomes com '__' sao do runtime, nao da linguagem: '__expect__' e o
    # alvo interno de 'expect(x).to_be(y)', e quem escreve DataForge
    # nunca o digita.
    reais = {n for n in get_builtins() if not n.startswith("__")}
    assert not (reais - listadas), f"não documentadas: {sorted(reais - listadas)}"
    assert not (listadas - reais), f"documentadas mas inexistentes: {sorted(listadas - reais)}"


# ─── CLI: check/fmt/lint sobre pastas ──────────────────────────
# Bugs encontrados ao conferir os comandos que a doc manda rodar:
# 'dataforge check .' estourava IsADirectoryError, e fmt/lint
# derrubavam a execucao inteira ao topar num .df fora de UTF-8.

def test_check_aceita_diretorio(tmp_path):
    """'dataforge check <pasta>' analisa todos os .df, sem estourar."""
    from dataforge.cli import check_command

    (tmp_path / "bom.df").write_text("x := 1\nout x\n", encoding='utf-8')
    (tmp_path / "outro.df").write_text("y := 2\nout y\n", encoding='utf-8')

    saida = io.StringIO()
    with redirect_stdout(saida):
        check_command([str(tmp_path)])
    assert "2 arquivo(s) sem erros" in saida.getvalue()


def test_check_em_diretorio_falha_quando_ha_erro(tmp_path):
    """Com erro de verdade, sai com codigo 1 — serve para a esteira."""
    from dataforge.cli import check_command

    (tmp_path / "bom.df").write_text("x := 1\nout x\n", encoding='utf-8')
    (tmp_path / "ruim.df").write_text(
        "action f(a, b):\n    yield a + b\n\nout f(1)\n", encoding='utf-8')

    with pytest.raises(SystemExit) as exc:
        with redirect_stdout(io.StringIO()):
            check_command([str(tmp_path)])
    assert exc.value.code == 1


def test_arquivo_ilegivel_nao_derruba_a_execucao(tmp_path):
    """Um .df fora de UTF-8 e reportado; os outros seguem sendo lidos."""
    from dataforge.cli import fmt_command, lint_command

    (tmp_path / "bom.df").write_text("x := 1\nout x\n", encoding='utf-8')
    (tmp_path / "torto.df").write_bytes(b'out "caf\xe9"\n')  # latin-1

    saida = io.StringIO()
    with pytest.raises(SystemExit):   # --check sai 1 quando ha pendencia
        with redirect_stdout(saida):
            fmt_command([str(tmp_path)], checar=True)
    assert "UTF-8" in saida.getvalue()

    saida = io.StringIO()
    with redirect_stdout(saida):
        lint_command([str(tmp_path)])
    assert "UTF-8" in saida.getvalue()


def test_pacote_nao_tem_df_fora_de_utf8():
    """Nenhum .df do repositorio pode estar fora de UTF-8."""
    import glob
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruins = []
    for f in glob.glob(os.path.join(raiz, "**", "*.df"), recursive=True):
        try:
            open(f, encoding='utf-8').read()
        except UnicodeDecodeError:
            ruins.append(os.path.relpath(f, raiz))
    assert ruins == [], f"arquivos fora de UTF-8: {ruins}"


# ─── '??' cobre indice ausente ─────────────────────────────
# A mensagem do DF0601 sugere 'valor ?? padrao'. Antes isso nao
# funcionava: ler chave inexistente estourava antes de o '??' rodar,
# e a dica mandava o usuario para um caminho que nao existia.

def test_coalesce_cobre_chave_ausente():
    assert run('v := {"a": 1}\nout v["b"] ?? 99\n') == "99"


def test_coalesce_cobre_indice_fora_da_faixa():
    assert run('l := [10]\nout l[5] ?? 0\n') == "0"


def test_coalesce_nao_engole_erro_de_verdade():
    """So o erro de indice vira void; o resto continua subindo."""
    saida = run('''
monitor:
    out naoexiste ?? 1
handle e:
    out e.type
''')
    assert "NameError" in saida


def test_coalesce_preserva_valor_existente():
    assert run('v := {"a": 5}\nout v["a"] ?? 99\n') == "5"


# ─── Interpolacao: posicao dos nos ─────────────────────────
# As expressoes de dentro de $"{...}" eram compiladas isoladas e nasciam
# na linha 1. So a raiz era reposicionada, entao qualquer ferramenta que
# descesse na arvore via linha 1 nos filhos — o linter media uma acao de
# duas linhas como tendo 197.

def test_no_de_interpolacao_fica_na_linha_certa():
    from dataforge import ast_nodes as ast
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    fonte = "\n\n\nnome := \"ana\"\nout $\"ola, {nome}\"\n"
    arvore = parse(tokenize(fonte, "t.df"), "t.df")

    linhas = []

    def descer(n):
        if not isinstance(n, ast.ASTNode):
            return
        linhas.append(getattr(n, "line", 0))
        for campo, valor in vars(n).items():
            if campo in ("line", "column"):
                continue
            if isinstance(valor, ast.ASTNode):
                descer(valor)
            elif isinstance(valor, list):
                for i in valor:
                    descer(i)

    interp = arvore.body[-1]
    descer(interp)
    # tudo na linha 5, nada na 1
    assert all(l == 5 for l in linhas if l), linhas


def test_acao_curta_nao_e_reportada_como_longa():
    """Uma acao de duas linhas com interpolacao nao pode virar 'has 197 lines'."""
    from dataforge.lexer import tokenize
    from dataforge.linter import lint_program
    from dataforge.parser import parse

    fonte = "steady X := 1\n" + "\n" * 190 + (
        "action curta(d):\n    yield $\"valor {X}\"\n")
    arvore = parse(tokenize(fonte, "t.df"), "t.df")
    avisos = lint_program(arvore, "t.df", fonte)
    longas = [d for d in avisos if d.code == "long-action"]
    assert longas == [], [d.message for d in longas]


# ─── Atribuicao composta avalia o alvo uma vez ─────────────
# 'v[f()] += 1' chamava f() duas vezes: o parser reusava o mesmo no como
# alvo e como operando esquerdo. Num sorteio, isso consumia dois numeros
# e gravava numa chave diferente da lida — a distribuicao saia errada e
# nada denunciava.

def test_indice_de_atribuicao_composta_avalia_uma_vez():
    saida = run('''
chamadas := []
action indice():
    chamadas.append(1)
    yield "k"

v := {"k": 0}
v[indice()] += 5
out v["k"], len(chamadas)
''')
    assert saida == "5 1"


def test_compostas_em_todas_as_formas():
    assert run('x := 1\nx += 2\nx *= 3\nout x\n') == "9"
    assert run('l := [1, 2]\nl[0] += 10\nout l\n') == "[11, 2]"
    assert run('v := {"a": 1}\nv["a"] += 4\nout v["a"]\n') == "5"


def test_composta_em_campo_de_instancia():
    assert run('''
blueprint C:
    action setup():
        self.n := 0
c := spawn C()
c.n += 7
out c.n
''') == "7"


def test_composta_em_chave_ausente_da_erro_util():
    from dataforge.errors import IndexError_
    with pytest.raises(IndexError_) as exc:
        run('v := {}\nv["x"] += 1\n')
    assert "x" in str(exc.value)


# ─── Sinal de controle solto vira erro da linguagem ────────
# 'halt', 'skip' e 'yield' derivam de BaseException para que 'monitor'
# nao os engula. O preco era que, soltos no topo, escapavam como
# traceback do Python — inutil para quem escreve .df.

@pytest.mark.parametrize("codigo,palavra,contexto", [
    ("halt\n", "halt", "loop"),
    ("skip\n", "skip", "loop"),
    ("yield 1\n", "yield", "action"),
])
def test_sinal_solto_vira_erro_da_linguagem(codigo, palavra, contexto):
    from dataforge.errors import RuntimeError_
    with pytest.raises(RuntimeError_) as exc:
        run(codigo)
    msg = str(exc.value)
    assert palavra in msg
    assert contexto in msg


def test_skip_dentro_de_handle_fora_de_laco():
    """O caso real: 'handle e: skip' num teste, sem laco em volta."""
    from dataforge.errors import RuntimeError_
    with pytest.raises(RuntimeError_):
        run('monitor:\n    trigger "x"\nhandle e:\n    skip\n')


def test_sinal_dentro_do_laco_continua_funcionando():
    """A correcao nao pode quebrar o uso legitimo."""
    assert run('''
cycle i from 1 to 5:
    given i is 3:
        skip
    given i is 5:
        halt
    out i
''') == "1\n2\n4"


# ─── 'monitor' nao cria escopo proprio ─────────────────────
# O corpo rodava num escopo filho, entao o padrao mais comum de
# try/catch — atribuir dentro e usar depois — nao funcionava, e a
# variavel sumia sem explicacao. Em Python, Java e JavaScript, 'try'
# nao cria escopo; essa e a expectativa de quem chega de qualquer uma.

def test_variavel_do_monitor_existe_depois():
    assert run('''
monitor:
    x := 42
handle e:
    x := 0
out x
''') == "42"


def test_monitor_que_falha_deixa_o_handle_atribuir():
    assert run('''
monitor:
    valor := 10 / 0
handle e:
    valor := -1
out valor
''') == "-1"


def test_retry_tambem_compartilha_o_escopo():
    assert run('retry 2:\n    y := 7\nout y\n') == "7"


def test_handle_nao_vaza_o_nome_do_erro():
    """'e' existe so dentro do handle — senao poluiria o escopo de fora."""
    from dataforge.errors import NameError_
    with pytest.raises(NameError_):
        run('monitor:\n    trigger "x"\nhandle e:\n    out e.message\nout e\n')


def test_analisador_concorda_com_o_runtime():
    """O check nao pode reprovar o que o interpretador aceita."""
    from dataforge.lexer import tokenize
    from dataforge.parser import parse
    from dataforge.typechecker import check_program

    fonte = 'monitor:\n    x := 1\nhandle e:\n    x := 2\nout x\n'
    diagnosticos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    erros = [d for d in diagnosticos if d.severity == 'error']
    assert erros == [], [d.message for d in erros]


# ─── Continuacao de linha apos operador ────────────────────
# Uma linha que termina em operador esta incompleta — nao ha o que ela
# possa significar sozinha. O lexer tratava o recuo da linha seguinte
# como INDENT, e o parser via um bloco onde havia uma expressao.

def test_continuacao_apos_mais():
    assert run('a := "um " +\n     "dois"\nout a\n') == "um dois"


def test_continuacao_apos_operadores_variados():
    assert run('n := 1 +\n     2 *\n     3\nout n\n') == "7"
    assert run('b := yes and\n     no\nout b\n') == "no"
    assert run('v := void ??\n     42\nout v\n') == "42"


def test_continuacao_apos_virgula():
    assert run('l := [1,\n      2,\n      3]\nout l\n') == "[1, 2, 3]"


def test_continuacao_dentro_de_acao():
    assert run('''
action junta(a, b):
    yield a +
          " " +
          b

out junta("oi", "mundo")
''') == "oi mundo"


def test_bloco_normal_continua_funcionando():
    """A correcao nao pode confundir bloco com continuacao."""
    assert run('''
given yes:
    x := 1
    out x
''') == "1"


def test_linha_apos_operador_nao_quebra_indentacao_seguinte():
    assert run('''
total := 10 +
         20

cycle i from 1 to 2:
    out i
out total
''') == "1\n2\n30"


# ─── Arcane.Http: json_response e aridade do handler ───────
# 'json_response' montava um envelope {__json__, data, status} que
# ninguem desembrulhava: o cliente recebia a estrutura interna e o
# status era sempre 200. E o handler era chamado com (req, res), o que
# obrigava a declarar um parametro que a maioria nao usa.

def test_json_response_devolve_envelope():
    from dataforge.stdlib import get_module
    http = get_module("Arcane.Http")
    envelope = http["json_response"]({"a": 1}, 201)
    assert envelope["__json__"] is True
    assert envelope["data"] == {"a": 1}
    assert envelope["status"] == 201


def test_servidor_desembrulha_e_preserva_status():
    """O envelope precisa virar corpo e status de verdade."""
    import inspect

    from dataforge.stdlib import arcane_http
    fonte = inspect.getsource(arcane_http)
    # o desembrulho existe e passa o status adiante
    assert 'result.get("__json__")' in fonte
    assert 'send_json(result.get("data"), int(result.get("status"' in fonte


def test_handler_de_um_argumento_e_aceito():
    """Um handler que so monta a resposta nao precisa do 'res'."""
    import inspect

    from dataforge.stdlib import arcane_http
    fonte = inspect.getsource(arcane_http)
    assert "result = handler(req)" in fonte, \
        "o servidor precisa tentar chamar o handler com um argumento so"


def test_erro_no_handler_vai_para_o_terminal():
    """Depurar handler nao pode depender de adivinhar."""
    import inspect

    from dataforge.stdlib import arcane_http
    fonte = inspect.getsource(arcane_http)
    assert "[http]" in fonte, "o erro do handler precisa ser impresso"


# ─── Instalador publicado bate com o do repositorio ────────
# Havia duas copias do instalar.sh: scripts/ e site/public/. No 4.1.0 so
# uma foi atualizada, e quem rodou 'curl | sh' baixou um tarball 4.0.0
# que nao existia mais. Agora gerar_tarball.py copia uma na outra.

def _raiz():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize("nome", ["instalar.sh", "instalar.ps1"])
def test_instalador_publicado_e_igual_ao_do_repositorio(nome):
    raiz = _raiz()
    origem = os.path.join(raiz, "scripts", nome)
    publicado = os.path.join(raiz, "site", "public", nome)
    if not os.path.exists(origem):
        pytest.skip(f"{nome} nao existe")
    assert os.path.exists(publicado), f"site/public/{nome} nao foi gerado"
    assert open(origem, encoding="utf-8").read() == \
           open(publicado, encoding="utf-8").read(), \
        f"{nome} divergiu — rode 'python3 scripts/gerar_tarball.py'"


def test_instalador_aponta_para_a_versao_atual():
    """O curl precisa baixar um tarball que existe."""
    from dataforge import __version__

    raiz = _raiz()
    instalador = open(os.path.join(raiz, "scripts", "instalar.sh"),
                      encoding="utf-8").read()
    assert f"DATAFORGE_VERSION:-{__version__}" in instalador, \
        f"instalar.sh nao aponta para {__version__}"


def test_tarball_da_versao_atual_existe():
    from dataforge import __version__

    caminho = os.path.join(_raiz(), "site", "public", "dist",
                           f"dataforge-{__version__}.tar.gz")
    assert os.path.exists(caminho), \
        f"falta o tarball {__version__} — rode 'python3 scripts/gerar_tarball.py'"


# ── Aspas dentro de interpolacao ─────────────────────────────

def test_interpolacao_aceita_string_com_aspas_normais():
    """Dentro de {...} as aspas sao normais, nao escapadas.

    Escrever \\" ali quebra o lexer, e a mensagem ("Unterminated
    interpolation") nao aponta para a causa. Este teste fixa a forma que
    funciona, que e tambem a que a doc ensina.
    """
    assert run('v := {"id": 7}\nout $"item {v["id"]}"') == "item 7"
    assert run('out $"{pad_start(str(5), 2, "0")}"') == "05"


def test_metodos_de_texto_seguem_snake_case():
    """Regressao: 'starts_with' nao existia — so 'startswith', do Python.

    O resto da linguagem e snake_case ('index_of', 'char_at', 'pad_start'),
    entao quem escrevia o nome coerente recebia "membro nao existe".
    """
    assert run('out "abacate".starts_with("aba")') == "yes"
    assert run('out "abacate".ends_with("ate")') == "yes"
    assert run('out "abc".is_alpha(), "".is_empty()') == "yes yes"
    assert run('out "a-b".to_upper()') == "A-B"


def test_sort_da_lista_aceita_chave():
    """Sem 'chave', ordenar records ou vaults pela lista era impossivel."""
    assert run('''
pessoas := [{"n": "Ana", "i": 30}, {"n": "Bia", "i": 25}]
out pessoas.sorted(lambda p: p["i"]).map(lambda p: p["n"])
''') == "[Bia, Ana]"


def test_agrupamento_e_particao():
    assert run('out [1, 2, 3, 4].partition(lambda n: n % 2 is 0)') == "[[2, 4], [1, 3]]"
    assert run('out [1, 1, 2].tally()') == "{1: 2, 2: 1}"


def test_cycle_desestrutura_cada_item():
    """'cycle i, item in enumerate(xs)' — o padrão mais comum que existe.

    A linguagem já desestruturava em atribuição; não aceitar aqui
    obrigava a três linhas para percorrer com índice.
    """
    assert run('''
cycle i, x in enumerate(["a", "b"]):
    out i, x
''') == "0 a\n1 b"


def test_cycle_desestrutura_pares():
    assert run('''
cycle n, nome in [[1, "um"], [2, "dois"]]:
    out $"{n}={nome}"
''') == "1=um\n2=dois"


def test_cycle_com_um_nome_continua_valendo():
    assert run('''
cycle x in [1, 2]:
    out x
''') == "1\n2"


def test_cycle_desestruturado_recusa_o_que_nao_reparte():
    """O erro tem de aparecer no laço, não mais tarde num nome ausente."""
    saida = run('''
monitor:
    cycle a, b in [1, 2]:
        out a
handle e:
    out e.message
''')
    assert "across 2 names" in saida


def test_travessao_depois_de_numero_e_comentario():
    """'// 10 — o dobro' é prosa, e era lido como divisão.

    O erro saía no travessão — um caractere que o lexer não conhece —
    e apontava para longe da causa.
    """
    assert run('out 3      // 10 — o dobro de 5') == "3"
    assert run('out 3      // 404, — não achei') == "3"


def test_dois_pontos_depois_do_numero_continua_sendo_divisao():
    """A guarda do travessão quase quebrou isto.

    Em Python, uma string VAZIA é subcadeia de qualquer outra: sem a
    verificação, `n // 20:` — onde nada segue os dois pontos — virava
    comentário e o laço perdia o limite.
    """
    assert run('''
cycle i from 1 to 60 // 20:
    out i
''') == "1\n2\n3"


def test_lambda_aceita_out_e_trigger():
    """Callback que só age não deveria exigir uma ação declarada."""
    assert run('''
f := lambda p => out $"recebi: {p}"
f("oi")
''') == "recebi: oi"
    assert run('''
g := lambda => trigger "falhou"
monitor:
    g()
handle e:
    out e.message
''') == "falhou"


def test_out_dentro_de_lambda_para_na_primeira_expressao():
    """Senão o primeiro 'out' engole a vírgula do cluster."""
    assert run('''
acoes := [lambda => out "a", lambda => out "b"]
out len(acoes)
cycle a in acoes:
    a()
''') == "2\na\nb"


def test_out_fora_de_lambda_continua_aceitando_varias():
    assert run('out "x", "y", "z"') == "x y z"


def test_with_fecha_o_recurso_mesmo_com_erro():
    """'defer' limpa na saída do ESCOPO; 'with' limpa no fim do BLOCO."""
    assert run('''
adopt Forge

pool := Forge.pool(":memory:", 1)

monitor:
    with Forge.conexao(pool) as db:
        trigger "erro no meio"
handle e:
    out "capturado"

out pool.estado()["livres"]
''') == "capturado\n1"


def test_with_liga_o_nome_e_devolve_no_fim():
    assert run('''
adopt Forge

pool := Forge.pool(":memory:", 2)
with Forge.conexao(pool) as db:
    out Forge.tabelas(db)
out pool.estado()["livres"]
''') == "[]\n1"


def test_versao_por_flag_nao_imprime_a_ajuda_inteira():
    """'--version' é o que todo script chama para conferir a instalação.

    Ele caía no ramo "sem argumentos" e imprimia a ajuda inteira — que
    nem o instalador, nem o CI, nem a extensão do editor sabem ler.
    """
    import subprocess
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for flag in ("--version", "-V"):
        r = subprocess.run([_sys.executable, "-m", "dataforge", flag],
                           capture_output=True, text=True, encoding="utf-8", cwd=raiz)
        primeira = r.stdout.strip().split("\n")[0]
        assert primeira.startswith("DataForge v"), f"{flag}: {primeira!r}"
        assert len(r.stdout.split("\n")) < 6, f"{flag} imprimiu demais"


def test_tarball_publicado_traz_os_exemplos():
    """O instalador oferece baixá-los; sem eles no pacote, a opção mente."""
    import tarfile

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "public", "dist",
                           "dataforge-1.0.0.tar.gz")
    if not os.path.isfile(caminho):
        pytest.skip("tarball ainda não foi gerado")

    with tarfile.open(caminho) as t:
        nomes = t.getnames()
    assert any("/examples/" in n for n in nomes), "sem examples/"
    assert any("/exercicios/" in n for n in nomes), "sem exercicios/"


def test_instalador_aceita_as_opcoes_que_o_site_monta():
    """O assistente do site monta o comando com estas flags."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sh = open(os.path.join(raiz, "scripts", "instalar.sh"),
              encoding="utf-8").read()
    ps = open(os.path.join(raiz, "scripts", "instalar.ps1"),
              encoding="utf-8").read()

    for opcao in ("--com-editor", "--sem-editor", "--com-exemplos",
                  "--abrir-docs"):
        assert opcao in sh, f"instalar.sh não conhece {opcao}"
        assert opcao in ps, f"instalar.ps1 não conhece {opcao}"

    # `curl | sh` e `irm | iex` não repassam argumentos: as opções
    # precisam chegar por variável de ambiente também.
    assert "DATAFORGE_EXTRAS" in sh
    assert "DATAFORGE_EXTRAS" in ps


def test_indice_dos_exercicios_esta_em_dia():
    """O README lista o que existe na pasta.

    Escrito à mão, ele envelhece: os módulos 21 a 26 existiam e o índice
    parava no 20 — porque conferir 216 linhas à mão não é algo que se
    faça duas vezes.
    """
    import subprocess
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run(
        [_sys.executable, "tools/gerar_indice_exercicios.py", "--check"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz)
    assert r.returncode == 0, (
        f"{r.stdout}{r.stderr}\n"
        "rode: python3 tools/gerar_indice_exercicios.py")


def test_todo_exercicio_tem_explicacao_a_partir_do_modulo_11():
    """Do 11 em diante, cada exercício traz um .md ao lado."""
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faltando = []
    for pasta in sorted(glob.glob(os.path.join(raiz, "exercicios", "*"))):
        nome = os.path.basename(pasta)
        if not os.path.isdir(pasta) or not nome[:2].isdigit():
            continue
        if int(nome[:2]) < 11:
            continue
        for df in sorted(glob.glob(os.path.join(pasta, "*.df"))):
            if not os.path.basename(df)[0].isdigit():
                continue
            if not os.path.isfile(df.replace(".df", ".md")):
                faltando.append(os.path.relpath(df, raiz))
    assert not faltando, f"sem .md: {faltando}"


def test_todo_modulo_da_stdlib_se_identifica_como_modulo():
    """Sem '__name__', o interpretador o trata como vault comum.

    E aí um símbolo chamado 'set', 'get' ou 'keys' é engolido pelo
    método de vault de mesmo nome — com uma mensagem sobre argumento
    faltando, que não dá nenhuma pista da causa.
    """
    from dataforge.stdlib import get_module, list_modules

    for nome in sorted(set(list_modules())):
        modulo = get_module(nome)
        assert modulo is not None, nome
        assert "__name__" in modulo, f"'{nome}' não se identifica"


def test_simbolo_do_modulo_vence_o_metodo_de_vault():
    """'Collections.set' é o conjunto, não o 'set' de vault."""
    assert run('''
adopt Arcane.Collections as C
out len(C.union(C.set([1, 2]), C.set([2, 3])))
''') == "3"


def test_todo_doc_de_erro_aponta_para_uma_rota_que_existe():
    """O 'doc:' das mensagens vira URL — e URL quebrada é pior que nenhuma.

    Três âncoras já nasceram inventadas ('cofre', 'concorrencia',
    'terminal'), escritas de memória junto com o módulo. Quem seguisse
    o link caía num 404 no momento em que mais precisava da página.
    Aqui a âncora é conferida contra as pastas reais do site.
    """
    import glob
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs = os.path.join(raiz, "site", "app", "docs")
    if not os.path.isdir(docs):
        pytest.skip("o site não está neste checkout")

    rotas = {
        os.path.relpath(os.path.dirname(p), docs).replace(os.sep, "/")
        for p in glob.glob(os.path.join(docs, "**", "page.tsx"), recursive=True)
    }

    quebradas = []
    alvos = (glob.glob(os.path.join(raiz, "dataforge", "*.py")) +
             glob.glob(os.path.join(raiz, "dataforge", "stdlib", "*.py")))
    for arquivo in sorted(alvos):
        fonte = open(arquivo, encoding="utf-8").read()
        for ancora in set(re.findall(r'doc="([^"]+)"', fonte)):
            if ancora.startswith("http"):
                continue
            if ancora.strip("/") not in rotas:
                quebradas.append(f"{os.path.basename(arquivo)}: /docs/{ancora}")

    assert not quebradas, "doc: aponta para rota inexistente: " + ", ".join(quebradas)


def test_apelido_de_modulo_carimba_o_nome_oficial():
    """'Zip', 'Archive' e 'Arcane.Archive' são o MESMO módulo.

    O carimbo de '__name__' usava o nome PEDIDO, então o mesmo módulo
    se apresentava com um nome diferente por apelido. O site contava 33
    módulos onde há 29, e a descrição do catálogo — indexada pelo nome
    oficial — não era encontrada para nenhum apelido.
    """
    from dataforge.stdlib import get_module

    for apelidos in (("Arcane.Archive", "Archive", "Zip"),
                     ("Arcane.Color", "Color", "Cor"),
                     ("Arcane.Concurrent", "Concurrent", "Paralelo"),
                     ("Arcane.Forge", "Forge", "Banco"),
                     ("Arcane.Database", "Database", "DB")):
        nomes = {get_module(a)["__name__"] for a in apelidos}
        assert len(nomes) == 1, f"{apelidos} se apresentam como {nomes}"


def test_apelido_traz_o_modulo_inteiro():
    """'Crypto' e 'Arcane.Crypto' precisam ter os mesmos símbolos.

    Os complementos eram listados apelido por apelido — o módulo saía
    completo por um nome e pela metade por outro.
    """
    from dataforge.stdlib import get_module

    for a, b in (("Crypto", "Arcane.Crypto"),
                 ("Collections", "Arcane.Collections")):
        assert set(get_module(a)) == set(get_module(b)), f"{a} != {b}"

    # O complemento é o que traz a cifragem de arquivo.
    assert "cifrar_arquivo" in get_module("Crypto")


def test_todo_modulo_registrado_esta_no_catalogo():
    """Sem a descrição, o módulo some da doc e da tabela do site.

    Cinco já ficaram de fora assim — Iter, Color, Concurrent, Forge e
    Crucible existiam no código e não apareciam em lugar nenhum.
    """
    from dataforge.stdlib import get_module, list_modules
    from dataforge.stdlib.catalogo import DESCRICOES

    faltando = sorted({get_module(n)["__name__"] for n in set(list_modules())}
                      - set(DESCRICOES))
    assert not faltando, (
        f"sem descrição em stdlib/catalogo.py: {faltando}")


def test_is_not_e_um_operador_so():
    """'5 is not 3' precisa ser 'yes'.

    Sem isto, 'is not' era lido como 'is' aplicado a '(not x)':
    '5 is not 3' virava '5 is no' e respondia 'no'. Compilava, rodava,
    passava no analisador e no lint, e dava a resposta errada em
    silêncio — o pior tipo de defeito. Quem vem do Python escreve
    'is not' sem pensar.
    """
    assert run("out 5 is not 3") == "yes"
    assert run("out 5 is not 5") == "no"
    assert run('out "x" is not ""') == "yes"
    assert run("out yes is not no") == "yes"

    # 'isnt' e 'is not' são o mesmo operador.
    assert run("out 5 isnt 3") == run("out 5 is not 3")

    # E 'not' sozinho continua sendo negação.
    assert run('out not ""') == "yes"
    assert run("out 5 is (not 3)") == "no"


def test_is_not_encadeia_como_as_outras_comparacoes():
    """'1 smaller x is not 9' encadeia como qualquer comparação."""
    assert run("x := 5\nout 1 smaller x is not 9") == "yes"
    assert run("x := 9\nout 1 smaller x is not 9") == "no"


def test_membro_ausente_em_modulo_sugere_o_nome_certo():
    """'Iter.chunks' precisa apontar para 'chunk'.

    A mensagem era 'Vault has no key' — chamava um módulo de vault e
    não sugeria nada, enquanto uma variável errada já ganhava
    'did you mean'. Quem erra o nome de uma função da stdlib fica sem
    pista nenhuma, e são 1016 símbolos.
    """
    with pytest.raises(DataForgeError) as e:
        run("adopt Arcane.Iter as I\nout I.chunks([1, 2], 2)")
    texto = str(e.value)
    assert "chunk" in texto
    assert "Arcane.Iter" in texto
    assert "Vault" not in texto


def test_membro_ausente_em_vault_continua_dizendo_vault():
    """Um vault comum não vira módulo na mensagem."""
    with pytest.raises(DataForgeError) as e:
        run('v := {"nome": "x"}\nout v.nomes')
    assert "nome" in str(e.value)


def test_monitor_aceita_varios_handle():
    """Um 'handle' por tipo de erro, como todo try/except tipado.

    O parser aceitava exatamente UM. Com 177 tipos de erro e 'handle'
    tipado, ter uma só cláusula obriga a capturar 'Error' e despachar
    na mão — que é justamente o que o handle tipado existe para evitar.
    """
    fonte = '''
action classificar(f):
    monitor:
        f()
    handle DivisionByZeroError:
        yield "zero"
    handle KeyError as e:
        yield "chave"
    handle Error as e:
        yield "outro: " + e.type

out classificar(lambda => 1 / 0)
out classificar(lambda => {"a": 1}["b"])
out classificar(lambda => trigger "x")
'''
    assert run(fonte).splitlines() == ["zero", "chave", "outro: TriggerError"]


def test_o_primeiro_handle_que_casa_vence():
    """A ordem manda, como nos 'point' do match."""
    fonte = '''
monitor:
    1 / 0
handle Error:
    out "generico"
handle DivisionByZeroError:
    out "especifico"
'''
    assert run(fonte) == "generico"


def test_varios_handle_com_ensure_e_sem_casar():
    """O 'ensure' roda; um erro que não casa com nenhum handle sobe."""
    fonte = '''
monitor:
    trigger "x"
handle DivisionByZeroError:
    out "zero"
ensure:
    out "ensure"
'''
    with pytest.raises(DataForgeError):
        run(fonte)

    # e o ensure roda mesmo assim
    fonte_ok = '''
monitor:
    monitor:
        trigger "x"
    handle KeyError:
        out "nao"
    ensure:
        out "ensure"
handle Error:
    out "subiu"
'''
    assert run(fonte_ok).splitlines() == ["ensure", "subiu"]


def test_nome_do_erro_nao_vaza_de_nenhum_handle():
    fonte = '''
e := "original"
monitor:
    1 / 0
handle KeyError as e:
    out "nao"
handle DivisionByZeroError as e:
    out e.type
out e
'''
    assert run(fonte).splitlines() == ["DivisionByZeroError", "original"]


def test_a_tabela_da_stdlib_no_readme_esta_em_dia():
    """Ela é gerada; o README versionado tem de bater com o gerador.

    Escrita à mão, divergiu: anunciava 22 módulos com 753 símbolos e um
    'Arcane.Crypto' com 38, quando eram 29, 1016 e 48.
    """
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme = os.path.join(raiz, "README.md")
    antes = open(readme, encoding="utf-8").read()

    r = subprocess.run([sys.executable, "tools/gerar_doc_stdlib.py"],
                       cwd=raiz, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    depois = open(readme, encoding="utf-8").read()

    if antes != depois:                      # restaura antes de falhar
        open(readme, "w", encoding="utf-8").write(antes)
    assert antes == depois, (
        "README fora de sincronia — rode: python3 tools/gerar_doc_stdlib.py")


def test_todo_modulo_de_exercicio_tem_pagina_no_site():
    """Os 26 módulos precisam estar em /docs/exercicios.

    Escritas à mão, as páginas pararam no 23: os módulos 24 (banco de
    dados), 25 (Crucible) e 26 (complexidade) existiam no repositório e
    não apareciam no site. E o índice ainda dizia "os vinte módulos" e
    "todos os 180" quando já eram 26 e 216.
    """
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs = os.path.join(raiz, "site", "app", "docs", "exercicios")
    if not os.path.isdir(docs):
        pytest.skip("o site não está neste checkout")

    modulos = {
        os.path.basename(p)
        for p in glob.glob(os.path.join(raiz, "exercicios", "*"))
        if os.path.isdir(p) and os.path.basename(p)[:2].isdigit()
        and glob.glob(os.path.join(p, "[0-9]*.df"))
    }
    publicados = {
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(docs, "*", "page.tsx"))
    }
    faltando = sorted(modulos - publicados)
    assert not faltando, (
        f"sem página no site: {faltando} — rode: "
        "python3 site/scripts/gerar_conteudo.py")


def test_o_indice_de_exercicios_mostra_a_contagem_real():
    """Nem '180', nem 'os vinte módulos': os números saem dos arquivos."""
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pagina = os.path.join(raiz, "site", "app", "docs", "exercicios", "page.tsx")
    if not os.path.isfile(pagina):
        pytest.skip("o site não está neste checkout")

    total = len(glob.glob(os.path.join(raiz, "exercicios", "*", "[0-9]*.df")))
    texto = open(pagina, encoding="utf-8").read()
    assert str(total) in texto, f"o índice não cita os {total} exercícios"


def test_bigo_ve_o_acumulo_por_spread_no_espaco():
    """'p := [...p, x]' num laço é O(n) de espaço, não O(1).

    O detector de acúmulo só conhecia 'append/push/extend/insert/add' e
    'xs[i] := v'. Mas a forma idiomática de crescer uma coleção em
    DataForge é o spread — é o que os exercícios usam — e uma ação que
    monta uma lista inteira era relatada como O(1) de espaço.
    """
    from dataforge.complexidade import analisar_fonte, para_json

    fonte = '''
action juntar(xs):
    p := []
    cycle x in xs:
        p := [...p, x * 2]
    yield p
'''
    r = {a["nome"]: a for a in para_json(analisar_fonte(fonte, "t.df"))["acoes"]}
    assert r["juntar"]["espaco"]["notacao"] != "O(1)", (
        f"espaço relatado: {r['juntar']['espaco']['notacao']}")


def test_bigo_nao_confunde_reatribuicao_com_acumulo():
    """'x := x + 1' num laço continua sendo O(1) de espaço.

    A distinção é o ponto: uma variável reatribuída não acumula. Contar
    tudo como O(n) tornaria o relatório inútil.
    """
    from dataforge.complexidade import analisar_fonte, para_json

    fonte = '''
action somar(xs):
    t := 0
    cycle x in xs:
        t := t + x
    yield t
'''
    r = {a["nome"]: a for a in para_json(analisar_fonte(fonte, "t.df"))["acoes"]}
    assert r["somar"]["espaco"]["notacao"] == "O(1)"


def _avisos(fonte):
    """Os avisos do analisador sobre uma fonte."""
    from dataforge.typechecker import check_program
    programa = parse(tokenize(fonte, "t.df"), "t.df")
    return [d for d in check_program(programa, "t.df") if d.severity == "warning"]


def test_match_avisa_o_membro_de_enum_que_ficou_de_fora():
    """Sem 'default', um membro esquecido devolve void em silêncio.

    É a promessa quebrada mais visível da linguagem: o pattern matching
    é vendido como recurso central, o typechecker JÁ conhece os membros
    do enum, e mesmo assim 'f(C.B)' devolvia void sem ninguém avisar.
    """
    fonte = '''
enum Cor:
    Vermelho
    Verde
    Azul

action nome(c):
    match c:
        point Cor.Vermelho:
            yield "vermelho"
        point Cor.Verde:
            yield "verde"
'''
    avisos = [a for a in _avisos(fonte) if "Azul" in a.message]
    assert avisos, "não avisou sobre o membro que ficou de fora"
    assert avisos[0].code == "match-incompleto"


def test_match_completo_nao_avisa():
    """Falso alarme ensina o usuário a ignorar mensagem."""
    fonte = '''
enum Cor:
    Vermelho
    Azul

action nome(c):
    match c:
        point Cor.Vermelho:
            yield "vermelho"
        point Cor.Azul:
            yield "azul"
'''
    assert not [a for a in _avisos(fonte) if a.code == "match-incompleto"]


def test_default_cobre_o_resto():
    """Quem escreveu 'default' já disse o que fazer com o resto."""
    fonte = '''
enum Cor:
    Vermelho
    Verde
    Azul

action nome(c):
    match c:
        point Cor.Vermelho:
            yield "vermelho"
        default:
            yield "outra"
'''
    assert not [a for a in _avisos(fonte) if a.code == "match-incompleto"]


def test_captura_solta_tambem_cobre():
    """'point n' casa com tudo — é um default com outro nome."""
    fonte = '''
enum Cor:
    Vermelho
    Azul

action nome(c):
    match c:
        point Cor.Vermelho:
            yield "vermelho"
        point outra:
            yield "outra"
'''
    assert not [a for a in _avisos(fonte) if a.code == "match-incompleto"]


def test_match_que_nao_e_sobre_enum_fica_calado():
    """O analisador só fala quando consegue provar."""
    fonte = '''
action classificar(v):
    match v:
        point Integer:
            yield "inteiro"
        point [a, b]:
            yield "par"
'''
    assert not [a for a in _avisos(fonte) if a.code == "match-incompleto"]


def test_avisa_uma_vez_com_todos_os_membros_faltando():
    """Um aviso por membro viraria ruído num enum de dez."""
    fonte = '''
enum Bicho:
    Gato
    Cao
    Ave
    Peixe

action som(b):
    match b:
        point Bicho.Gato:
            yield "miau"
'''
    avisos = [a for a in _avisos(fonte) if a.code == "match-incompleto"]
    assert len(avisos) == 1
    for membro in ("Cao", "Ave", "Peixe"):
        assert membro in avisos[0].message


def test_o_formato_da_interpolacao_e_aplicado():
    """'$"{x:.2f}"' precisa arredondar, não imprimir tudo.

    O formato era engolido em silêncio: o lexer o incluía na expressão,
    o parser o descartava, e a saída vinha sem formato nenhum. Compilava,
    rodava e produzia o texto errado — a mesma família do 'is not'.

    E não era teórico: alinhamentos com ':<10' escritos em exemplos
    desta própria documentação saíam desalinhados.
    """
    assert run('x := 3.14159\nout $"{x:.2f}"') == "3.14"
    assert run('out $"[{"ab":<6}]"') == "[ab    ]"
    assert run('out $"[{42:>6}]"') == "[    42]"
    assert run('out $"{1234567:,}"') == "1,234,567"
    assert run('out $"{0.5:.1%}"') == "50.0%"


def test_o_dois_pontos_de_vault_nao_e_confundido_com_formato():
    """'{v["a"]}' e '{ {"a":1}["a"] }' têm ':' que NÃO é formato.

    Cortar no primeiro ':' quebraria toda leitura de vault dentro de
    interpolação — que é o uso mais comum que existe.
    """
    assert run('v := {"id": 7}\nout $"item {v["id"]}"') == "item 7"
    assert run('out $"{ {"a": 1}["a"] }"') == "1"


def test_o_ternario_dentro_da_interpolacao_continua_valendo():
    """'given/otherwise' não tem ':', mas o lambda tem."""
    assert run('x := 10\nout $"{"alto" given x bigger 5 otherwise "baixo"}"') \
        == "alto"


def test_formato_invalido_diz_o_que_houve():
    with pytest.raises(DataForgeError) as e:
        run('out $"{"texto":.2f}"')
    assert "formato" in str(e.value).lower() or "format" in str(e.value).lower()


def test_o_analisador_ve_a_expressao_dentro_do_formato():
    """'{naoexiste:.2f}' precisa ser apanhado como nome indefinido.

    O analisador só olhava as partes 'expr'. Com o formato numa parte
    própria, um nome errado ali passaria despercebido — e o erro só
    apareceria em execução, que é justamente o que o 'check' existe
    para evitar.
    """
    fonte = 'x := 1\nout $"{naoexiste:.2f}"'
    programa = parse(tokenize(fonte, "t.df"), "t.df")
    from dataforge.typechecker import check_program
    erros = [d for d in check_program(programa, "t.df")
             if d.severity == "error" and "naoexiste" in d.message]
    assert erros, "o nome indefinido dentro do formato não foi visto"


def test_o_lint_ve_o_uso_dentro_do_formato():
    """Um módulo usado só em '{M.pi():.2f}' não é 'importado sem uso'.

    O linter também só olhava as partes 'expr'. Acusar um import que
    ESTÁ sendo usado é o tipo de falso alarme que ensina a ignorar o
    lint inteiro.
    """
    from dataforge.linter import lint_program

    fonte = 'adopt Arcane.Math as M\nout $"{M.sqrt(2):.3f}"\n'
    programa = parse(tokenize(fonte, "t.df"), "t.df")
    avisos = [a for a in lint_program(programa, "t.df", fonte)
              if "never used" in a.message or "sem uso" in a.message]
    assert not avisos, f"acusou um import que está em uso: {avisos}"


def test_o_dois_pontos_do_pipeline_nao_e_formato():
    """'{xs >> morph p: p["n"]}' tem ':' que é do lambda.

    O separador procura o ':' fora de parêntese e colchete — mas o
    corpo de um 'morph' fica solto, sem delimitador nenhum. Cortar ali
    partiria a expressão no meio, e o 'p' do corpo virava nome
    indefinido: o exercício 165 quebrou exatamente assim.
    """
    fonte = ('xs := [{"n": "a"}, {"n": "b"}]\n'
             'out $"nomes: {xs >> morph p: p["n"]}"')
    assert "a" in run(fonte) and "b" in run(fonte)


def test_o_dois_pontos_do_lambda_tambem_nao_e_formato():
    assert run('f := lambda x: x * 2\nout $"{f(21)}"') == "42"
    assert run('out $"{[1, 2, 3] >> sift n: n bigger 1}"') == "[2, 3]"


def _contagens_reais():
    """Os números que o site anuncia, tirados do código."""
    import glob
    from dataforge.builtins import get_builtins
    from dataforge.stdlib import get_module, list_modules

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modulos = {get_module(n)["__name__"] for n in set(list_modules())}
    return {
        "modulos": len(modulos),
        "simbolos": sum(len([k for k in get_module(n) if not k.startswith("__")])
                        for n in modulos),
        "builtins": len(get_builtins()),
        "exercicios": len(glob.glob(os.path.join(raiz, "exercicios",
                                                 "*", "[0-9]*.df"))),
        "exemplos": len(glob.glob(os.path.join(raiz, "examples", "*.df"))),
        "areas": len([
            d for d in glob.glob(os.path.join(raiz, "exercicios", "*"))
            if os.path.isdir(d) and os.path.basename(d)[:2].isdigit()
            and glob.glob(os.path.join(d, "[0-9]*.df"))]),
        "testes": _quantos_testes(raiz),
        "blocos": _quantos_blocos_de_doc(raiz),
    }


def _quantos_testes(raiz):
    """Quantos testes o pytest coleta — a mesma conta que o CI faz."""
    import re
    import subprocess
    import sys as _sys

    r = subprocess.run([_sys.executable, "-m", "pytest", "tests/", "-q",
                        "--collect-only"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=raiz)
    achado = re.search(r"(\d+) tests collected", r.stdout or "")
    return int(achado.group(1)) if achado else 0


def _quantos_blocos_de_doc(raiz):
    import re
    import subprocess
    import sys as _sys

    r = subprocess.run([_sys.executable, "tools/verificar_docs.py"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=raiz)
    achado = re.search(r"os (\d+) blocos", r.stdout or "")
    return int(achado.group(1)) if achado else 0


def test_a_pagina_docs_anuncia_os_numeros_reais():
    """Ela dizia '20 módulos, 675 símbolos, 190 exercícios'.

    Eram 34, 1132 e 216. Número escrito à mão numa página envelhece em
    silêncio — e a primeira página que alguém lê é a que mais custa
    estar errada.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pagina = os.path.join(raiz, "site", "app", "docs", "page.tsx")
    if not os.path.isfile(pagina):
        pytest.skip("o site não está neste checkout")

    import re

    texto = open(pagina, encoding="utf-8").read()
    real = _contagens_reais()

    # O que é estrutural muda raramente, e uma divergência ali é rot:
    # cobrado exato.
    for chave in ("modulos", "simbolos", "exercicios", "areas"):
        assert str(real[chave]) in texto, (
            f"a página /docs não cita os {real[chave]} {chave} reais")

    # Testes e blocos de doc crescem a cada mudança, e cobrar o número
    # exato faria de cada teste novo uma edição em dois arquivos — o
    # tipo de atrito que se resolve desligando a trava. Cobrada a ordem
    # de grandeza: "1858" onde são 2171 falha (17%), dois testes novos
    # não.
    for chave, padrao in (("testes", r"<strong>(\d+) testes</strong>"),
                          ("blocos", r"compilados a cada mudança — (\d+) deles")):
        if not real[chave]:
            continue        # a ferramenta não rodou neste ambiente
        achado = re.search(padrao, texto)
        assert achado, (
            f"a página /docs não anuncia mais os {chave} no formato que "
            f"este teste conhece — ajuste o padrão: {padrao}")
        dito = int(achado.group(1))
        desvio = abs(dito - real[chave]) / real[chave]
        assert desvio <= 0.05, (
            f"a página /docs diz {dito} {chave}, e são {real[chave]} "
            f"({desvio:.0%} de diferença)")


def test_a_home_lista_todos_os_modulos():
    """Catorze módulos ficaram invisíveis na home — Kiln entre eles.

    A contagem era gerada e estava certa; a LISTA era escrita à mão e
    parou em 20. Um módulo que existe e não aparece é trabalho que
    ninguém encontra.
    """
    import json
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    componente = os.path.join(raiz, "site", "components", "landing",
                              "Arcane.tsx")
    dados = os.path.join(raiz, "site", "lib", "dados-gerados.json")
    if not os.path.isfile(componente):
        pytest.skip("o site não está neste checkout")

    texto = open(componente, encoding="utf-8").read()
    bloco = texto[texto.index("const grupos"):texto.index("];",
                                                          texto.index("const grupos"))]
    listados = set(re.findall(r"'([a-z_]+)'", bloco))
    todos = set(json.load(open(dados, encoding="utf-8"))["modulos"])

    faltando = sorted(todos - listados)
    assert not faltando, f"não aparecem na home: {faltando}"


def test_os_trechos_da_home_compilam():
    """Eles são a primeira coisa que alguém lê da linguagem."""
    import json

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo = os.path.join(raiz, "site", "lib", "trechos-landing.json")
    if not os.path.isfile(arquivo):
        pytest.skip("o site não está neste checkout")

    for trecho in json.load(open(arquivo, encoding="utf-8")):
        parse(tokenize(trecho["codigo"], trecho["titulo"]), trecho["titulo"])


def test_o_formatador_nao_separa_o_menos_unario():
    """'-2' é um número negativo; '- 2' parece uma subtração sem termo.

    O formatador espaçava TODO '-', inclusive o unário — e com isso 93
    dos 216 exercícios ficavam permanentemente 'fora do formato'. Rodar
    'fmt' os pioraria, então ninguém rodava, e o 'fmt --check' era
    inútil no CI.
    """
    from dataforge.formatter import format_source

    for fonte, esperado in [
        ("x := -5", "x := -5"),
        ("out -2 ** 2", "out -2 ** 2"),
        ("z := -x + 1", "z := -x + 1"),
        ("w := [-1, -2]", "w := [-1, -2]"),
        ("f(-3)", "f(-3)"),
    ]:
        assert format_source(fonte).strip() == esperado


def test_o_formatador_preserva_a_subtracao_binaria():
    """'a - b' não pode virar 'a -b': ali o espaço é o que separa."""
    from dataforge.formatter import format_source

    for fonte in ("y := a - b", "out 10 - 3", "z := (a) - (b)"):
        assert format_source(fonte).strip() == fonte


def test_o_menos_unario_sobrevive_a_ida_e_volta():
    """Formatar não pode mudar o que o programa faz."""
    fonte = "out -2 ** 2\nout 10 - 3\nout -(4 + 1)\n"
    from dataforge.formatter import format_source
    assert run(fonte) == run(format_source(fonte))


def test_o_formatador_preserva_o_formato_da_interpolacao():
    """'{x:.2f}' não pode virar '{x}' — nem derrubar o formatador.

    A parte com formato traz uma tupla, não um texto: o formatador
    estourava com 'can only concatenate str (not tuple)' ao tocar em
    qualquer arquivo que usasse formato.
    """
    from dataforge.formatter import format_source

    fonte = 'x := 3.14159\nout $"{x:.2f} e {x}"\n'
    formatado = format_source(fonte)
    assert "{x:.2f}" in formatado
    assert run(fonte) == run(formatado)


def test_o_formatador_nao_separa_a_chamada_de_palavra_reservada():
    """'typeof(1)' não vira 'typeof (1)'.

    A regra de 'nome(' olhava só IDENTIFIER — mas 'typeof', 'delete',
    'len' e outras são palavras reservadas que CHAMAM como função. O
    espaço as fazia parecer outra coisa.
    """
    from dataforge.formatter import format_source

    for fonte in ('out typeof(1)', 'v.delete("k")', 'out len([1, 2])'):
        assert format_source(fonte).strip() == fonte


def test_o_formatador_nao_espaca_a_fatia():
    """'xs[1:4]' não vira 'xs[1: 4]'.

    O ':' de fatia não é o de vault nem o de bloco. Espaçá-lo faz a
    fatia parecer um par chave-valor.
    """
    from dataforge.formatter import format_source

    for fonte in ("out xs[1:4]", "out xs[:3]", "out xs[::2]", "out xs[-2:]"):
        assert format_source(fonte).strip() == fonte


def test_o_formatador_continua_espacando_o_vault():
    """Ali o ':' separa chave de valor, e o espaço ajuda a ler."""
    from dataforge.formatter import format_source
    assert format_source('v := {"a": 1, "b": 2}').strip() == 'v := {"a": 1, "b": 2}'


def test_o_formatador_indenta_a_continuacao_dentro_de_colchete():
    """Uma lista multilinha não pode perder o recuo.

    O lexer não emite INDENT dentro de colchete aberto — e a
    profundidade do formatador vem dali. Sem tratar a continuação, um
    literal bem escrito voltava encostado na margem: ainda compila, e
    fica ilegível.
    """
    from dataforge.formatter import format_source

    fonte = 'dados := [\n    ["Ana", 25],\n    ["Bo", 30],\n]\nout len(dados)\n'
    saida = format_source(fonte)
    for linha in saida.split("\n"):
        if linha.strip().startswith('["'):
            assert linha.startswith("    "), f"perdeu o recuo: {linha!r}"


def test_o_formatador_continua_idempotente_com_continuacao():
    """format(format(x)) == format(x) — inclusive com multilinha."""
    from dataforge.formatter import format_source

    fonte = ('v := {\n    "a": 1,\n    "b": [\n        1,\n        2,\n    ],\n}\n'
             'out v\n')
    uma = format_source(fonte)
    assert format_source(uma) == uma


def test_o_formatador_nao_toca_no_conteudo_de_string_multilinha():
    """Formatar não pode MUDAR o que o programa faz.

    O formatador trata cada linha do arquivo como código. Uma string
    de três aspas ocupa várias linhas — e as de dentro eram
    reformatadas: '<h1>' virava '< h1 >', dois espaços viravam um, e um
    template HTML dentro do programa chegava corrompido ao navegador.

    O exercício 194 quebrou exatamente assim.
    """
    from dataforge.formatter import format_source

    html = '<h1>{{titulo}}</h1>\n{{#itens}}<li>x</li>{{/itens}}\ndois  espacos'
    fonte = f'x := """{html}"""\nout x\n'
    assert html in format_source(fonte), "o conteúdo da string foi alterado"
    assert run(fonte) == run(format_source(fonte))


def test_string_multilinha_com_codigo_dentro_sobrevive():
    """SQL e HTML dentro de string têm ':' e '(' que não são código."""
    from dataforge.formatter import format_source

    sql = 'SELECT *\n  FROM t\n WHERE a = 1  AND b = 2'
    fonte = f'q := """{sql}"""\nout q\n'
    assert sql in format_source(fonte)


def test_a_linguagem_le_notacao_cientifica():
    """'6.022e23' é literal de ponto flutuante em qualquer linguagem.

    O lexer o partia em '6.022', 'e', '23' — e o 'e' virava nome
    indefinido. Não era só uma falta: o FORMATADOR emitia essa notação,
    porque o 'repr' do Python usa ela para número pequeno. Ele gerava
    sintaxe que a própria linguagem não conseguia ler de volta.
    """
    assert run("out 1e3") == "1000.0"
    assert run("out 1.5e2") == "150.0"
    assert run("out 2e-3") == "0.002"
    assert run("out 6.022e23") == "6.022e+23"
    assert run("out 1E3") == "1000.0"


def test_o_e_de_nome_continua_sendo_nome():
    """'2 e 3' não existe, mas 'e := 1' e 'x e' precisam continuar."""
    assert run("e := 5\nout e * 2") == "10"
    assert run("epsilon := 0.1\nout epsilon") == "0.1"


def test_o_formatador_nao_gera_float_que_o_lexer_nao_le():
    """Ele emite 'repr' do float, e o repr usa notação científica.

    Um formatador que produz sintaxe não-parseável é pior que nenhum: o
    arquivo passa a não compilar depois de formatado. Foi o que
    aconteceu com o pacote 'aleatorio'.
    """
    from dataforge.formatter import format_source

    for valor in ("0.0000001", "1e-07", "6.022e23", "1.5e10"):
        fonte = f"x := {valor}\nout x\n"
        formatado = format_source(fonte)
        # o formatado precisa COMPILAR e dar o mesmo resultado
        assert run(formatado) == run(fonte), f"{valor}: {formatado!r}"


def test_o_formatador_preserva_a_barra_r():
    """'\\r' virava um retorno de carro de verdade dentro da string.

    O pacote 'progresso' usa '\\r' para reescrever a linha do terminal;
    formatá-lo transformava o escape no caractere, e o arquivo deixava
    de ter uma string terminada.
    """
    from dataforge.formatter import format_source

    fonte = 'x := "linha\\r"\nout len(x)\n'
    assert run(format_source(fonte)) == run(fonte)


def test_todo_arquivo_python_compila_na_versao_minima():
    """A linguagem promete Python 3.10+ — e o código precisa caber lá.

    Cinco f-strings usavam recursos que só o 3.12 aceita: expressão
    quebrada em várias linhas dentro das chaves, e a mesma aspa reusada
    dentro da interpolação. O arquivo inteiro deixava de importar no
    3.10 — não era um teste que falhava, era a CLI que não carregava.

    ``ast.parse(feature_version=)`` NÃO serve aqui: ela não volta atrás
    na gramática de f-string, e aceitaria os cinco casos. A única forma
    honesta de saber é compilar com o interpretador da versão mínima —
    então o teste pula quando ele não está na máquina, e o CI, que tem
    a matriz, é quem realmente cobra.
    """
    import glob
    import shutil
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    minima = "3.10"

    executavel = shutil.which(f"python{minima}")
    if executavel is None:
        pytest.skip(f"python{minima} não está nesta máquina — "
                    f"o CI cobre com a matriz")

    arquivos = [c for c in glob.glob(os.path.join(raiz, "**", "*.py"),
                                     recursive=True)
                if not any(parte in c for parte in
                           (".venv", "node_modules", "build",
                            "site-packages", ".git"))]

    programa = (
        "import sys\n"
        "ruins = []\n"
        "for caminho in sys.argv[1:]:\n"
        "    with open(caminho, encoding='utf-8') as f:\n"
        "        fonte = f.read()\n"
        "    try:\n"
        "        compile(fonte, caminho, 'exec')\n"
        "    except SyntaxError as e:\n"
        "        ruins.append(f'{caminho}:{e.lineno}')\n"
        "print(chr(10).join(ruins))\n")

    r = subprocess.run([executavel, "-c", programa] + arquivos,
                       capture_output=True, text=True, encoding="utf-8", timeout=180)
    ruins = [linha for linha in r.stdout.split("\n") if linha.strip()]
    assert not ruins, f"não compila em Python {minima}: {ruins}"


# ── A CLI num terminal que nao fala UTF-8 ────────────────────

def test_a_amostra_de_encoding_reprova_cp1252():
    """'cp1252' e o que o Windows da a uma saida redirecionada.

    E ela nao tem nenhum dos tracos que a CLI usa para desenhar tabela.
    """
    from dataforge import marca

    assert marca._cabe(_FluxoFalso("utf-8"))
    assert not marca._cabe(_FluxoFalso("cp1252"))
    assert not marca._cabe(_FluxoFalso("cp850"))
    assert not marca._cabe(_FluxoFalso("ascii"))
    # Um fluxo sem codificacao declarada (substituto de teste, bytes)
    # nao e problema nosso.
    assert marca._cabe(_FluxoFalso(None))


class _FluxoFalso:
    """Um destino de texto com codificacao fixa e sem 'reconfigure'."""

    def __init__(self, encoding):
        self.encoding = encoding
        self.escrito = []

    def write(self, texto):
        if self.encoding:
            # O ponto do teste: um destino de verdade recusaria.
            texto.encode(self.encoding)
        self.escrito.append(texto)
        return len(texto)


def test_saida_traduz_o_desenho_quando_nao_da_para_reconfigurar():
    """Sem UTF-8 possivel, a tabela vira ASCII em vez de estourar.

    'errors=replace' devolveria uma fileira de '?' no lugar da tabela e
    'backslashreplace' devolveria '\\u2500', que e pior de ler que o
    traco que substitui.
    """
    from dataforge import marca

    falso = _FluxoFalso("cp1252")
    original = sys.stdout
    sys.stdout = falso
    try:
        marca.preparar_saida()
        # Nao explode — era isto que quebrava no Windows.
        sys.stdout.write("─" * 3 + " ✓ pronto → 100% █")
        escrito = "".join(falso.escrito)
    finally:
        sys.stdout = original

    assert escrito == "--- v pronto -> 100% #"


def test_a_cli_inteira_roda_com_a_saida_em_cp1252():
    """O teste que teria apanhado o bug: a CLI num cano do Windows.

    Metade dos comandos morria com UnicodeEncodeError antes de imprimir
    a primeira linha util — 'help', 'check', 'lint', 'stats' e
    'run --time'. Nao era o comando que falhava: era o traco do
    cabecalho que nao cabia no cano.

    Reproduzir isto no Linux e no macOS exige forcar a codificacao pela
    variavel de ambiente; e o que o Windows faz sozinho.
    """
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ambiente = {**os.environ, "PYTHONIOENCODING": "cp1252",
                "PYTHONPATH": raiz, "NO_COLOR": "1"}
    pasta = os.path.join(raiz, "exercicios", "01-fundamentos")

    comandos = [
        ["help"],
        ["version"],
        ["check", pasta],
        ["lint", pasta],
        ["stats", pasta],
        ["fmt", pasta, "--check"],
    ]
    for comando in comandos:
        r = subprocess.run([sys.executable, "-m", "dataforge"] + comando,
                           cwd=raiz, capture_output=True, env=ambiente,
                           timeout=120)
        erro = r.stderr.decode("utf-8", errors="replace")
        assert "UnicodeEncodeError" not in erro, (
            f"'dataforge {' '.join(comando)}' nao sobrevive a uma saida "
            f"em cp1252:\n{erro[-600:]}")
        assert r.returncode == 0, (
            f"'dataforge {' '.join(comando)}' saiu {r.returncode}:\n"
            f"{erro[-600:]}")


def test_nenhum_subprocess_decide_a_codificacao_pelo_sistema():
    """`text=True` sozinho decodifica com a codificação do SISTEMA.

    No Linux e no macOS isso é UTF-8 e ninguém percebe. No Windows é
    `cp1252`, e a saída da CLI — que é UTF-8 — chega embaralhada: o teste
    falha comparando um texto que está certo do outro lado do cano.

    Metade dos exercícios desenha tabela com `─` e `═`. Foi assim que
    duas execuções da matriz caíram sem nada na mensagem explicando por
    quê.

    A varredura é pela árvore, e não por texto: procurar `text=True` com
    expressão regular encontra o próprio regex deste teste.
    """
    import ast as pyast
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pastas = ("tests", "exercicios", "tools", "scripts", "dataforge")
    ruins = []
    frageis = []
    for pasta in pastas:
        for caminho in glob.glob(os.path.join(raiz, pasta, "**", "*.py"),
                                 recursive=True):
            arvore = pyast.parse(open(caminho, encoding="utf-8").read(), caminho)
            for no in pyast.walk(arvore):
                if not isinstance(no, pyast.Call):
                    continue
                nomes = {k.arg for k in no.keywords if k.arg}
                tem_texto = any(
                    k.arg in ("text", "universal_newlines")
                    and isinstance(k.value, pyast.Constant)
                    and k.value.value is True
                    for k in no.keywords)
                if tem_texto and "encoding" not in nomes:
                    ruins.append(f"{os.path.relpath(caminho, raiz)}:{no.lineno}")
                # E, quando o filho e de TERCEIRO — 'git', 'docker',
                # 'npm' —, 'encoding' sozinho nao basta: eles escrevem
                # na codificacao do console, e um byte fora do UTF-8
                # DERRUBA a thread que le a saida. O pytest reporta
                # isso como um aviso solto que nao diz de onde vem.
                if (tem_texto and "encoding" in nomes
                        and "errors" not in nomes
                        and _chama_programa_de_terceiro(no, pyast)):
                    frageis.append(
                        f"{os.path.relpath(caminho, raiz)}:{no.lineno}")
    assert not ruins, (
        "subprocess com 'text=True' e sem 'encoding' — no Windows isso lê "
        "cp1252 em vez do UTF-8 que o filho escreveu:\n  "
        + "\n  ".join(sorted(ruins)))
    assert not frageis, (
        "subprocess de programa de TERCEIRO com 'encoding' e sem "
        "'errors' — no Windows o git e o docker escrevem cp1252, e um "
        "byte fora do UTF-8 derruba a thread que lê a saída:\n  "
        + "\n  ".join(sorted(frageis)))


#: Programas que NAO escrevem UTF-8 no Windows. A lista e curta de
#: proposito: exigir 'errors' de todo subprocesso esconderia o caso em
#: que a saida e nossa e a codificacao esta sob controle.
_DE_TERCEIRO = ("git", "docker", "npm", "npx", "node", "kubectl", "helm",
                "sh", "bash", "cmd", "powershell")


def _chama_programa_de_terceiro(no, pyast):
    """O primeiro argumento da chamada nomeia um programa de terceiro?"""
    if not no.args:
        return False
    alvo = no.args[0]
    candidatos = []
    if isinstance(alvo, pyast.Constant) and isinstance(alvo.value, str):
        candidatos.append(alvo.value)
    elif isinstance(alvo, (pyast.List, pyast.Tuple)):
        for item in alvo.elts:
            if isinstance(item, pyast.Constant) and isinstance(item.value, str):
                candidatos.append(item.value)
                break
    return any(
        os.path.basename(c).split(".")[0] in _DE_TERCEIRO
        for c in candidatos)


def test_encurtar_caminho_nunca_custa_a_mensagem():
    """No Windows, `relpath` entre unidades diferentes LEVANTA.

    Quase todo uso aqui está dentro da construção de uma mensagem, para
    encurtar um caminho longo. Quando ele levanta ali, o erro que chega
    ao usuário não é o dele: `adopt ./lib/naoexiste` num projeto em
    `D:` com o terminal em `C:` devolvia "path is on mount 'C:', start
    on mount 'D:'" no lugar de "não achei o módulo".
    """
    from dataforge.caminhos import curto

    class _Explode:
        """O `os.path.relpath` do Windows entre unidades."""

        def __call__(self, *args):
            raise ValueError("path is on mount 'C:', start on mount 'D:'")

    import dataforge.caminhos as mod
    original = mod.os.path.relpath
    mod.os.path.relpath = _Explode()
    try:
        assert curto("/algum/lugar/app.df") == "/algum/lugar/app.df"
    finally:
        mod.os.path.relpath = original

    # E o encurtamento normal continua encurtando.
    aqui = os.path.join(os.getcwd(), "app.df")
    assert curto(aqui) == "app.df"

    # Mas nao quando o "curto" fica mais longo que o original.
    assert not curto("/x").startswith("..")


def test_nenhuma_mensagem_usa_relpath_cru():
    """`os.path.relpath(x)` com UM argumento é o que quebra no Windows.

    Com um argumento só, a referência é o diretório atual — e a unidade
    dele é arbitrária: nada garante que o terminal esteja no mesmo disco
    do arquivo. Com dois argumentos onde quem chama garante uma raiz
    comum (percorrer uma pasta, nomear a entrada de um zip) não há
    risco, e ali o relativo é o DADO, não um enfeite de mensagem — cair
    para o caminho absoluto gravaria caminho absoluto dentro do
    arquivo compactado.
    """
    import ast as pyast
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruins = []
    for caminho in glob.glob(os.path.join(raiz, "dataforge", "**", "*.py"),
                             recursive=True):
        if os.path.basename(caminho) == "caminhos.py":
            continue
        arvore = pyast.parse(open(caminho, encoding="utf-8").read(), caminho)
        for no in pyast.walk(arvore):
            if not isinstance(no, pyast.Call) or len(no.args) != 1:
                continue
            alvo = no.func
            if (isinstance(alvo, pyast.Attribute) and alvo.attr == "relpath"):
                ruins.append(f"{os.path.relpath(caminho, raiz)}:{no.lineno}")
    assert not ruins, (
        "use 'caminhos.curto()' — 'os.path.relpath' com um argumento se "
        "apoia no diretorio atual e levanta no Windows quando ele esta "
        "noutra unidade:\n  " + "\n  ".join(ruins))


def test_a_doc_gerada_nao_depende_da_versao_do_python():
    """`math.factorial(x)` no Python 3.12, `math.factorial(n)` no 3.13.

    `Arcane.Math` publica `math.factorial` sem envolvê-la, então
    `inspect.signature` vazava o nome interno do CPython para dentro de
    `doc/BIBLIOTECA_PADRAO.md`. Duas máquinas certas geravam arquivos
    diferentes, e o CI cobrava a diferença sem que ninguém tivesse
    errado — o pior tipo de falha de esteira, a que não aponta culpado.

    A tabela `ASSINATURAS` faz o DataForge nomear a própria interface.
    Este teste cobra que ela esteja completa: um símbolo novo que
    ficasse de fora voltaria a herdar o nome do CPython em silêncio.
    """
    import inspect

    from dataforge.stdlib import get_module, list_modules
    from dataforge.stdlib.catalogo import ASSINATURAS

    def do_c(valor):
        return (inspect.isbuiltin(valor)
                or type(valor).__name__ in ("builtin_function_or_method",
                                            "method_descriptor"))

    faltando = {}
    for nome in sorted(set(list_modules())):
        modulo = get_module(nome)
        if not isinstance(modulo, dict):
            continue
        for simbolo, valor in modulo.items():
            if simbolo.startswith("__") or not callable(valor):
                continue
            if do_c(valor) and simbolo not in ASSINATURAS:
                faltando.setdefault(simbolo, []).append(nome)

    assert not faltando, (
        "funcoes C do Python sem assinatura fixa em "
        "'dataforge/stdlib/catalogo.py' — a doc gerada volta a depender "
        f"da versao: {sorted(faltando)}")


def test_a_tabela_de_assinaturas_nao_tem_entrada_morta():
    """Uma entrada que não corresponde a nada é ruído que envelhece."""
    import inspect

    from dataforge.stdlib import get_module, list_modules
    from dataforge.stdlib.catalogo import ASSINATURAS

    expostos = set()
    for nome in sorted(set(list_modules())):
        modulo = get_module(nome)
        if isinstance(modulo, dict):
            expostos.update(k for k, v in modulo.items() if callable(v))

    from dataforge.builtins import get_builtins
    expostos.update(k for k, v in get_builtins().items()
                    if callable(v) and inspect.isbuiltin(v))

    mortas = sorted(set(ASSINATURAS) - expostos)
    assert not mortas, f"entradas que nao correspondem a nenhum simbolo: {mortas}"


def test_todo_script_que_desenha_prepara_a_saida():
    """Quem imprime traço de tabela precisa sobreviver ao cp1252.

    A CLI faz isso no começo de `main`. `exercicios/run_all.py` não
    fazia: no Windows, o relatório de falha — que repete a última linha
    do exercício, com acento e com os traços das tabelas — estourava com
    `UnicodeEncodeError` **antes** de dizer qual exercício falhou. O
    resultado era uma esteira vermelha sem nenhuma informação.
    """
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    amostra = "─═│█✓✗→●…"

    ruins = []
    for caminho in (glob.glob(os.path.join(raiz, "tools", "*.py"))
                    + glob.glob(os.path.join(raiz, "scripts", "*.py"))
                    + glob.glob(os.path.join(raiz, "exercicios", "*.py"))):
        fonte = open(caminho, encoding="utf-8").read()
        if '__name__ == "__main__"' not in fonte and \
                "__name__ == '__main__'" not in fonte:
            continue
        if not any(c in fonte for c in amostra):
            continue
        if "preparar_saida" in fonte:
            continue
        ruins.append(os.path.relpath(caminho, raiz))

    assert not ruins, (
        "script que desenha e nao chama 'marca.preparar_saida()' — no "
        "Windows ele morre ao imprimir:\n  " + "\n  ".join(ruins))


# ── A expressao do objeto e avaliada UMA vez ────────────────

def test_chamada_de_metodo_nao_avalia_o_objeto_duas_vezes():
    """`dar_lista().count(1)` chamava `dar_lista()` DUAS vezes.

    Quando o método não era de nenhum tipo que o interpretador conhece
    por nome, o último recurso montava um nó `MemberAccess` apontando
    para a expressão do objeto e mandava avaliá-la de novo — sendo que
    o objeto já estava ali, avaliado, na variável ao lado.

    Não era um erro visível: o resultado saía certo. O que se repetia
    era o **efeito colateral** — uma consulta ao banco, uma escrita em
    arquivo, um contador. Exatamente o tipo de bug que compila, roda e
    mente.
    """
    assert run('''
vezes := 0

action dar_lista():
    vezes += 1
    yield [1, 2, 3]

quantos := dar_lista().count(1)
out vezes, quantos''') == "1 1"


def test_o_objeto_de_um_metodo_encadeado_tambem_conta_uma_vez():
    """A mesma garantia com o objeto vindo de um atributo caro."""
    assert run('''
chamadas := 0

blueprint Fonte:
    get itens():
        chamadas += 1
        yield ["a", "b", "a"]

f := spawn Fonte()
n := f.itens.count("a")
out chamadas, n''') == "1 2"


# ── Um interpretador novo comeca limpo ─────────────────────

def test_dois_programas_no_mesmo_processo_nao_compartilham_o_crucible():
    """O registro de testes era um objeto de MÓDULO, um por processo.

    `crucible`/`trial` registram e `Crucible.run()` executa o que foi
    registrado. Como o registro vivia no módulo, dois programas no mesmo
    processo o compartilhavam — e `dataforge test` cria um interpretador
    **por arquivo**: o segundo arquivo via os trials do primeiro.

    O efeito é o pior possível num framework de teste: contagem errada,
    e a falha de um arquivo reaparecendo no relatório do outro. Nada
    quebrava; o relatório é que mentia.
    """
    fonte = '''adopt Crucible

crucible "Contas":
    trial "soma":
        expect(1 + 1).to_be(2)

resumo := Crucible.run()
out resumo["passou"]'''

    primeiro = run(fonte)
    segundo = run(fonte)
    assert primeiro == "1", f"o primeiro ja veio errado: {primeiro}"
    assert segundo == "1", (
        f"o segundo programa contou {segundo} trials — esta vendo os do "
        f"primeiro")


def test_o_registro_nao_e_zerado_entre_linhas_do_mesmo_interpretador():
    """O contrapeso: no REPL, a suíte da linha 3 vale na linha 4.

    Zerar a cada `run` consertaria o teste acima e quebraria o console
    interativo, onde cada linha é um `run` sobre o mesmo interpretador.
    """
    interp = Interpreter()
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize('''adopt Crucible

crucible "Contas":
    trial "soma":
        expect(1 + 1).to_be(2)''')))

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        interp.run(parse(tokenize('out Crucible.run()["passou"]')))
    assert buffer.getvalue().strip() == "1", \
        "a suite montada na execucao anterior sumiu"


# ── Todo documento diz o que e ────────────────────────────

def test_cada_documento_de_doc_esta_classificado():
    """`doc/` mistura três coisas, e confundi-las sai caro.

    Há a documentação **atual**, há **documento histórico** — versões
    anteriores e direções abandonadas — e há **material de origem**, os
    textos que serviram de fonte para o que foi implementado.

    `DATAFORGE_LANGUAGE_SPEC.md` estava fora das três: sem aviso no
    topo, sem entrada no índice. Quem abrisse `doc/` encontraria um
    arquivo chamado "especificação" descrevendo uma linguagem que não é
    esta — 23 das 31 palavras reservadas que ele propõe vêm de Rust ou
    de JavaScript, e prometia interoperabilidade com a ABI C, que não
    existe.

    A regra: ou o arquivo está citado como atual no `doc/README.md`, ou
    carrega o aviso **e** está na lista correspondente.
    """
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    indice = open(os.path.join(raiz, "doc", "README.md"),
                  encoding="utf-8").read()

    atuais = indice.split("## Documentos históricos")[0]
    resto = indice.split("## Documentos históricos")[1]

    ruins = []
    for caminho in sorted(glob.glob(os.path.join(raiz, "doc", "*.md"))):
        nome = os.path.basename(caminho)
        if nome == "README.md":
            continue

        if nome in atuais:
            continue                       # documentação atual

        if nome not in resto:
            ruins.append(f"{nome}: nao aparece no indice de doc/README.md")
            continue

        # Histórico precisa do aviso no topo; material de origem, não —
        # ele nunca se apresentou como documentação.
        origem = nome in resto.split("## Material de origem")[-1] \
            if "## Material de origem" in resto else False
        if origem:
            continue

        cabeca = open(caminho, encoding="utf-8").read()[:500]
        if "DOCUMENTO HISTÓRICO" not in cabeca:
            ruins.append(f"{nome}: listado como historico e sem o aviso no topo")

    assert not ruins, (
        "documento de 'doc/' que nao diz o que e — quem abrir a pasta nao "
        "consegue saber se pode confiar nele:\n  " + "\n  ".join(ruins))


def test_nenhum_lockfile_guarda_o_caminho_de_quem_instalou():
    """Três `forge.lock` versionados traziam o meu diretório pessoal.

        "registro": "file:///Users/<nome>/.../site/public/registry"

    Apontar o registro para uma pasta local é conveniência de quem
    desenvolve — um `DATAFORGE_REGISTRY=./site/public/registry` para
    testar um pacote antes de publicar. Ele acabava gravado no lock, que
    é versionado e público.

    Dois problemas de uma vez: o caminho da casa de alguém num
    repositório aberto, e um lockfile que **não é reproduzível** — duas
    pessoas instalando o mesmo projeto geravam arquivos diferentes, e o
    lock deixava de ser o que promete: o registro exato do que foi
    instalado, igual para todos.
    """
    import glob
    import json

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruins = []
    for caminho in sorted(glob.glob(os.path.join(raiz, "**", "forge.lock"),
                                    recursive=True)):
        if "forge_modules" in caminho:
            continue
        with open(caminho, encoding="utf-8") as f:
            registro = json.load(f).get("registro", "")
        if registro and not registro.startswith(("http://", "https://")):
            ruins.append(f"{os.path.relpath(caminho, raiz)}: {registro}")

    assert not ruins, (
        "lockfile com registro local — so registro remoto entra no "
        "arquivo versionado:\n  " + "\n  ".join(ruins))


def test_o_lock_recusa_gravar_um_registro_local():
    """A trava do lado de quem escreve, e não só do que está no disco."""
    import json
    import tempfile

    from dataforge.packages import Lock

    with tempfile.TemporaryDirectory() as pasta:
        # 'Lock' recebe a RAIZ do projeto e monta o nome do arquivo.
        caminho = os.path.join(pasta, "forge.lock")

        lock = Lock(pasta)
        lock.registrar("x", "1.0.0", "registro", "abc")
        lock.gravar("file:///Users/alguem/projeto/registry")
        with open(caminho, encoding="utf-8") as f:
            assert json.load(f)["registro"] == "", \
                "o caminho local entrou no lock"

        lock.gravar("https://dataforge-lang.vercel.app/registry")
        with open(caminho, encoding="utf-8") as f:
            assert json.load(f)["registro"] == \
                "https://dataforge-lang.vercel.app/registry", \
                "o registro remoto precisa ser preservado"


def test_nenhum_df_do_repositorio_crava_caminho_de_um_sistema_so():
    """`/tmp` não existe no Windows — e estava em 12 lugares.

    Foi corrigido três vezes, em três rodadas: primeiro nos exercícios,
    depois no modelo de projeto do `dataforge new`, e só agora nos
    projetos e nos pacotes. Cada rodada consertou o que o CI alcançava
    naquele momento, porque o job parava no primeiro passo vermelho e o
    seguinte nem chegava a rodar.

    Este teste fecha a classe inteira de uma vez, em vez de esperar o
    próximo passo da esteira revelar o próximo arquivo.

    A forma certa é `IO.join(OS.temp_dir(), …)`, que pergunta ao sistema
    onde fica a pasta temporária.
    """
    import glob
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cravados = re.compile(r'"(/tmp/|/var/|/usr/|/etc/|/home/|C:\\\\)')

    ruins = []
    for caminho in sorted(glob.glob(os.path.join(raiz, "**", "*.df"),
                                    recursive=True)):
        if "forge_modules" in caminho or "/dist/" in caminho:
            continue
        for numero, linha in enumerate(
                open(caminho, encoding="utf-8").read().split("\n"), 1):
            # Comentário é prosa: citar '/tmp' ao explicar é legítimo.
            if linha.lstrip().startswith("//"):
                continue
            if cravados.search(linha):
                ruins.append(
                    f"{os.path.relpath(caminho, raiz)}:{numero}: "
                    f"{linha.strip()[:70]}")

    assert not ruins, (
        "caminho de um sistema so num '.df' — use "
        "IO.join(OS.temp_dir(), …):\n  " + "\n  ".join(ruins))


def test_nenhum_teste_de_paralelismo_usa_limite_absoluto():
    """Um limite fixo mede a MÁQUINA, não o paralelismo.

    `assert levou < 0.20` para cinco esperas de 60 ms passa aqui e falha
    no CI do macOS — que rodou perfeitamente em paralelo, em 0,21 s,
    porque cinco threads disputando uma CPU compartilhada demoram mais
    que cinco threads sozinhas.

    Um teste que falha por máquina lenta ensina a ignorar a suíte, que é
    o pior que pode acontecer com ela. A comparação tem de ser com a
    **série medida no mesmo lugar**.

    O guarda procura o padrão exato: uma função que mede tempo **e**
    compara o resultado com um número solto. Um teste que só verifica
    que algo *esperou* (`>= 0.04`) não está no alvo — ali o piso é a
    afirmação, e máquina lenta só o reforça.
    """
    import ast as pyast
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    relogios = ("perf_counter", "monotonic", "time")

    def mede_tempo(no):
        for filho in pyast.walk(no):
            if (isinstance(filho, pyast.Attribute)
                    and filho.attr in relogios
                    and isinstance(filho.value, pyast.Name)
                    and filho.value.id == "time"):
                return True
        return False

    def compara_com_constante(no):
        """`x < 0.2` — teto fixo. `x >= 0.04` é piso, e piso pode ficar."""
        for filho in pyast.walk(no):
            if not isinstance(filho, pyast.Compare):
                continue
            for op, direita in zip(filho.ops, filho.comparators):
                if not isinstance(op, (pyast.Lt, pyast.LtE)):
                    continue
                if (isinstance(direita, pyast.Constant)
                        and isinstance(direita.value, (int, float))):
                    return True
        return False

    suspeitos = []
    for caminho in sorted(glob.glob(os.path.join(raiz, "tests", "*.py"))):
        arvore = pyast.parse(open(caminho, encoding="utf-8").read(), caminho)
        for no in pyast.walk(arvore):
            if not isinstance(no, pyast.FunctionDef):
                continue
            if not mede_tempo(no) or not compara_com_constante(no):
                continue
            # Com uma série de referência no corpo, o teto fixo é só uma
            # rede a mais — o que decide é a razão.
            fonte_da_funcao = pyast.dump(no)
            if any(palavra in fonte_da_funcao
                   for palavra in ("serie", "referencia", "trabalho")):
                continue
            # E um teste de PRAZO é o caso legítimo: o limite não é a
            # velocidade da máquina, é o prazo que o próprio teste
            # configurou. "esperou menos que o dobro do prazo de 0,3 s"
            # é uma afirmação sobre o código, e máquina lenta a reforça.
            if "prazo" in fonte_da_funcao or "timeout" in fonte_da_funcao:
                continue
            suspeitos.append(f"{os.path.basename(caminho)}::{no.name}")

    assert not suspeitos, (
        "teste que mede tempo e compara com numero fixo — ele mede a "
        "maquina, nao o codigo:\n  " + "\n  ".join(suspeitos))


# ── O formatador não pode alterar dados ──────────────────────

@pytest.mark.parametrize("fonte", [
    'out "com :id aqui"',
    'out "{{ id }}"',
    'out "a : b"',
    'out "chave : valor"',
    'out "10 : 30"',
    'msg := "erro , grave"',
    'out "lista [ 1 , 2 ]"',
    'out "vault { a : 1 }"',
    'out "chamada ( x )"',
])
def test_o_fmt_nao_mexe_no_conteudo_das_strings(fonte):
    """`out "com :id"` virava `out "com:id"`.

    As limpezas de espaço em volta da pontuação rodavam sobre a linha
    **montada**, sem distinguir código de conteúdo de string. Uma
    ferramenta que promete não mudar semântica estava **alterando
    dados**.

    Apareceu num exercício sobre exportar API: o `{{ id }}` do Insomnia
    é significativo, e o `fmt` o destruía em silêncio — e o exercício
    passou a falhar por um motivo que não tinha nada a ver com ele.
    """
    from dataforge.formatter import format_source

    assert format_source(fonte).strip() == fonte, \
        "o conteudo da string mudou"


@pytest.mark.parametrize("fonte,esperado", [
    ('v := { "a" : 1 , "b" : 2 }', 'v := {"a": 1, "b": 2}'),
    ("f( a , b )", "f(a, b)"),
    ("xs[ 1 , 2 ]", "xs[1, 2]"),
])
def test_o_fmt_continua_normalizando_o_codigo(fonte, esperado):
    """O contrapeso: preservar string não pode virar preservar tudo."""
    from dataforge.formatter import format_source

    assert format_source(fonte).strip() == esperado


def test_o_fmt_acerta_string_com_aspas_escapadas():
    """`"ele disse \\"oi : tudo\\""` — a aspa escapada não fecha a string.

    Uma expressão regular sobre aspas erraria aqui, e a limpeza voltaria
    a rodar dentro do texto.
    """
    from dataforge.formatter import format_source

    fonte = 'out "ele disse \\"oi : tudo bem\\""'
    saida = format_source(fonte).strip()
    assert "oi : tudo bem" in saida, f"a string foi alterada: {saida}"


def test_a_pagina_da_biblioteca_lista_todos_os_modulos():
    """Seis módulos não apareciam nela: API, Decimal, Observar, Ponte,
    Stream e Vitrine.

    A tabela era escrita à mão, e a contagem no título dizia "trinta e
    sete" quando já eram trinta e oito. Um módulo que existe e não
    aparece é trabalho que ninguém encontra — e foi o mesmo defeito que
    já tinha atingido a home.

    Agora ela é gerada; este teste garante que o arquivo versionado é o
    que o gerador produz hoje.
    """
    import subprocess
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "site", "app", "docs", "biblioteca",
                           "page.tsx")
    if not os.path.isfile(destino):
        pytest.skip("o site não está neste checkout")

    antes = open(destino, encoding="utf-8").read()
    saida = subprocess.run(
        [_sys.executable,
         os.path.join(raiz, "tools", "gerar_pagina_biblioteca.py")],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz)
    assert saida.returncode == 0, saida.stdout + saida.stderr
    depois = open(destino, encoding="utf-8").read()
    assert antes == depois, (
        "site/app/docs/biblioteca/page.tsx está desatualizado — "
        "rode  python3 tools/gerar_pagina_biblioteca.py")

    # E, independentemente do gerador: todo módulo aparece.
    sys.path.insert(0, raiz)
    from dataforge.stdlib import get_module, list_modules
    oficiais = {get_module(m)["__name__"] for m in list_modules()}
    faltando = sorted(n for n in oficiais if f"`{n}`" not in depois)
    assert not faltando, f"não aparecem em /docs/biblioteca: {faltando}"


# ═══════════════════════════════════════════════════════════
#  'remove' e 'pop' num vault
#
#  Não havia como apagar uma chave de um vault no lugar. `omit`
#  devolve uma cópia, e `delete` só existia como método — a
#  forma função `remove(v, "k")` estourava
#  "list.remove(x): x not in list", uma mensagem sobre lista
#  para quem passou um vault.
#
#  Apareceu escrevendo uma saga: a compensação recebe o vault
#  compartilhado entre ações e precisa mudá-lo, não copiá-lo.
# ═══════════════════════════════════════════════════════════

def test_remove_apaga_a_chave_de_um_vault_no_lugar():
    saida = run('''
v := {"a": 1, "b": 2}
mesmo := v
remove(v, "a")
out v
out mesmo
''')
    # 'no lugar' é o ponto: quem guardou uma referência vê a mudança.
    assert saida.strip().splitlines() == ["{b: 2}", "{b: 2}"]


def test_remove_num_vault_sem_a_chave_e_silencioso():
    """Quem remove quer o estado final, e nesse ponto já não importa se
    estava lá. Levantar obrigaria todo chamador a checar antes."""
    saida = run('''
v := {"a": 1}
remove(v, "nao-existe")
out v
''')
    assert saida.strip() == "{a: 1}"


def test_remove_num_cluster_sem_o_item_tambem_e_silencioso():
    """Era a única das duas que levantava, e a assimetria não tinha
    razão: o `ValueError` cru do Python vazava como erro de runtime."""
    saida = run('''
c := [1, 2, 3]
remove(c, 99)
out c
remove(c, 2)
out c
''')
    assert saida.strip().splitlines() == ["[1, 2, 3]", "[1, 3]"]


def test_pop_de_vault_tira_pela_chave_e_devolve_o_valor():
    saida = run('''
v := {"a": 1, "b": 2}
out pop(v, "a")
out v
''')
    assert saida.strip().splitlines() == ["1", "{b: 2}"]


def test_pop_de_vault_sem_a_chave_levanta():
    """Ao contrário de `remove`: `pop` devolve o valor, e devolver
    `void` calado esconderia a diferença entre "a chave valia void" e
    "a chave não estava lá"."""
    saida = run('''
monitor:
    pop({"a": 1}, "z")
    out "nao devia chegar aqui"
handle Error as e:
    out e.type
''')
    assert saida.strip() == "KeyError"


def test_pop_de_vault_sem_chave_nenhuma_explica_o_que_fazer():
    saida = run('''
monitor:
    pop({"a": 1})
handle Error as e:
    out e.message
''')
    assert "precisa da chave" in saida


def test_pop_de_cluster_continua_pela_posicao():
    """A polimorfia não pode mudar o caso que já funcionava."""
    saida = run('''
c := [1, 2, 3]
out pop(c)
out pop(c, 0)
out c
''')
    assert saida.strip().splitlines() == ["3", "1", "[2]"]


def test_nenhuma_ferramenta_estoura_traceback_em_arquivo_do_repositorio():
    """Um analisador estático que morre com traceback do Python é pior
    que um que erra: não diz nada sobre o código, e o usuário não tem
    como saber se o problema é dele.

    Aconteceu de verdade. `superficie.py` lia os membros de um `enum`
    como se fossem um dicionário, mas o parser os guarda como pares
    `(nome, valor)`. Um par com valor carrega um nó da árvore, que não
    é hashável, e `set(campos)` estourava — em cinco arquivos de
    `projetos/gestor-tarefas`, os únicos do repositório com import
    relativo entre arquivos, que é o caminho que chega lá.

    E passou meses sem aparecer porque `scripts/verificar_tudo.sh`
    rodava `check` em `exercicios/`, `examples/` e `packages/` — não em
    `projetos/`.
    """
    import glob
    import subprocess
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvos = [d for d in ("exercicios", "examples", "packages", "projetos",
                         "modelos")
             if os.path.isdir(os.path.join(raiz, d))]
    assert alvos

    for ferramenta in ("check", "lint", "fmt"):
        cmd = [_sys.executable, "-m", "dataforge", ferramenta] + alvos
        if ferramenta == "fmt":
            cmd.append("--check")
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=raiz)
        saida = (r.stdout or "") + (r.stderr or "")
        assert "Traceback (most recent call last)" not in saida, (
            f"'dataforge {ferramenta}' estourou traceback:\n{saida[-2000:]}")


def test_a_superficie_le_um_enum_com_e_sem_valor(tmp_path):
    """O caso mínimo do bug acima, sem passar pela CLI."""
    from dataforge.superficie import de_arquivo

    arquivo = tmp_path / "x.df"
    arquivo.write_text('''
enum Status:
    Ativo
    Inativo := "off"
    Contagem := 3

    action ligado():
        yield self is Status.Ativo

relay Status
''', encoding="utf-8")

    membro = de_arquivo(str(arquivo)).membros["Status"]
    assert membro.especie == "enum"
    assert membro.campos == {"Ativo", "Inativo", "Contagem", "ligado"}


# ═══════════════════════════════════════════════════════════
#  A pilha de chamadas, alcançável pelo programa
#
#  Ela já era guardada no erro (`_attach_stack`) e desenhada
#  no stack trace, mas era invisível de dentro do programa: um
#  `handle` via a mensagem e nada sobre o caminho. Numa ação
#  chamada de cinco lugares, "deu erro em media()" não ajuda —
#  o que importa é QUAL das cinco chamadas, e essa informação
#  existia e ficava guardada.
# ═══════════════════════════════════════════════════════════

def test_o_handle_alcanca_a_pilha_de_chamadas():
    saida = run('''
action fundo():
    yield 1 / 0

action meio():
    yield fundo()

monitor:
    meio()
handle Error as e:
    out [q["name"] cycle q in e.pilha]
''')
    # Do mais externo para o mais interno: a ordem em que se lê "quem
    # chamou quem", e a mesma em que o stack trace desenha. Inverter
    # faria o programa e a tela discordarem sobre a mesma pilha.
    assert saida.strip() == "[meio, fundo]"


def test_stack_e_o_mesmo_que_pilha():
    """O nome em inglês, para quem já conhece a palavra."""
    saida = run('''
action f():
    yield 1 / 0

monitor:
    f()
handle Error as e:
    out len(e.pilha) is len(e.stack)
    out e.pilha is e.stack
''')
    assert saida.strip().splitlines() == ["yes", "yes"]


def test_cada_quadro_traz_nome_linha_coluna_e_arquivo():
    """O `file` é o que faz a pilha servir num projeto de 200
    arquivos: sem ele, dois `processar` em módulos diferentes são
    indistinguíveis."""
    saida = run('''
action f():
    yield 1 / 0

monitor:
    f()
handle Error as e:
    q := e.pilha[0]
    out sorted(keys(q))
    out q["name"], q["line"] bigger 0, q["column"] bigger 0
''')
    linhas = saida.strip().splitlines()
    assert linhas[0] == "[column, file, line, name]"
    assert linhas[1] == "f yes yes"


def test_a_pilha_e_dado_e_nao_objeto_do_python():
    """Entregar os `Frame` funcionaria por protocolo, mas não seria
    dado que se possa serializar, comparar ou mandar para um log — e
    mandar a pilha para um log é o caso de uso inteiro."""
    saida = run('''
adopt Arcane.Serialization as Serde

action f():
    yield 1 / 0

monitor:
    f()
handle Error as e:
    out typeof(e.pilha)
    out typeof(e.pilha[0])
    out len(Serde.to_json(e.pilha)) bigger 10
''')
    assert saida.strip().splitlines() == ["Cluster", "Vault", "yes"]


def test_a_linha_do_erro_e_a_do_quadro_sao_diferentes():
    """A confusão mais comum ao ler uma pilha.

    `e.line` é onde o erro nasceu; `quadro["line"]` é onde a chamada
    foi feita. Colapsar as duas perderia justamente a informação de
    por que aquela ação recebeu aquele argumento.
    """
    saida = run('''
action f(n):
    yield 10 / n

monitor:
    f(0)
handle Error as e:
    out e.line
    out e.pilha[0]["line"]
''')
    nascimento, chamada = [int(x) for x in saida.strip().splitlines()]
    assert nascimento == 3       # o 'yield 10 / n'
    assert chamada == 6          # o 'f(0)'


def test_a_pilha_de_um_erro_sem_acao_nenhuma_e_vazia():
    """No topo do programa não há quadro, e devolver uma lista vazia é
    diferente de levantar — quem lê a pilha não deveria precisar de um
    `monitor` em volta da leitura."""
    saida = run('''
monitor:
    1 / 0
handle Error as e:
    out e.pilha
''')
    assert saida.strip() == "[]"


# ═══════════════════════════════════════════════════════════
#  A mensagem de aridade não pode falar de Python
#
#  O `dataforge check` pega aridade errada antes de rodar,
#  com a assinatura completa. Mas ele cala quando não
#  consegue provar — uma ação guardada num vault, um callback
#  passado adiante — e é exatamente nesses casos que a pessoa
#  chega em execução.
# ═══════════════════════════════════════════════════════════

def test_aridade_errada_nao_nomeia_a_implementacao_em_python():
    """A mensagem era:

        ArcaneAnalytics._correlation() missing 2 required positional
        arguments: 'x' and 'y'

    Nem `ArcaneAnalytics` nem `_correlation` existem no vocabulário do
    DataForge: quem escreve chamou `An.correlation`. Uma mensagem que
    nomeia a implementação manda a pessoa procurar um símbolo que ela
    não tem como encontrar.
    """
    saida = run('''
adopt Arcane.Analytics as An

// Guardada num vault: o analisador não consegue provar, e cala.
tabela := {"corr": An.correlation}

monitor:
    tabela["corr"]()
handle Error as e:
    out e.type
    out e.message
    out e.nota
''')
    linhas = saida.strip().splitlines()
    assert linhas[0] == "ArityError"
    assert "correlation" in linhas[1]
    assert "ArcaneAnalytics" not in saida
    assert "_correlation" not in saida
    assert "positional" not in saida
    # A assinatura de verdade, que é o que torna a mensagem acionável.
    assert linhas[2] == "correlation(x, y)"


def test_aridade_errada_e_capturavel_como_arity_error():
    """O tipo saía `RuntimeError`, então `handle ArityError` não pegava.

    A causa: um ramo de `_call` chamava a função do host com um `try`
    próprio e levantava `RuntimeError_(str(e))` — passando por fora de
    `_invocar`, que é o único ponto que traduz. A docstring de
    `_invocar` avisava exatamente disso: "deixar um deles de fora
    reabre o buraco".
    """
    saida = run('''
adopt Arcane.Math as Math
f := Math.pow

monitor:
    f(2)
handle ArityError as e:
    out "pegou"
''')
    assert saida.strip() == "pegou"


def test_a_dica_diz_quantos_argumentos_a_funcao_aceita():
    saida = run('''
adopt Arcane.Text as Text
f := Text.slug

monitor:
    f()
handle Error as e:
    out e.dica
''')
    assert "takes" in saida


def test_toda_funcao_do_host_passa_por_invocar():
    """A trava da causa, e não do sintoma.

    `_call` tinha um ramo com `try/except` próprio. Qualquer ramo novo
    assim reabre o buraco para um caminho de chamada diferente, e o
    sintoma aparece só nesse caminho — foi por isso que passou tanto
    tempo: `[].min()` tinha mensagem traduzida e `tabela["f"]()` não.
    """
    import inspect
    import re

    from dataforge.interpreter import Interpreter

    fonte = inspect.getsource(Interpreter._call)
    suspeitos = re.findall(r"raise RuntimeError_\(str\(e\)", fonte)
    assert not suspeitos, (
        "'_call' voltou a levantar o texto cru do Python em vez de "
        "passar por '_invocar'")


def test_o_alvo_carimbado_na_excecao_nao_derruba_nada():
    """`_invocar` escreve `__df_alvo__` na exceção para a mensagem
    poder mostrar a assinatura. Uma exceção com `__slots__` recusa o
    atributo, e isso não pode virar um erro diferente do original."""
    saida = run('''
monitor:
    1 / 0
handle Error as e:
    out e.type
''')
    assert saida.strip() == "DivisionByZeroError"


def test_aridade_de_funcao_em_c_tambem_e_arity_error():
    """`math.pow` diz "expected 2 arguments, got 1" — sem `positional`
    e sem `takes`.

    Sem cobrir essa forma, a MESMA falha saía com tipo diferente
    conforme a função tivesse sido escrita em Python ou em C: `handle
    ArityError` pegava uma e não a outra, e nada na linguagem explica
    por quê.
    """
    saida = run('''
adopt Arcane.Math as Math

monitor:
    Math.pow(2)
handle ArityError as e:
    out "pegou"
''')
    assert saida.strip() == "pegou"


# ═══════════════════════════════════════════════════════════
#  'point' inalcançável, e o escape para silenciá-lo
#
#  A armadilha 10 da linguagem — "uma captura no topo torna
#  tudo abaixo inalcançável" — era a única documentada como
#  armadilha que o analisador não pegava. O código compila,
#  roda e devolve o ramo errado, sem uma palavra.
# ═══════════════════════════════════════════════════════════

def _diag(fonte, arquivo="x.df"):
    from dataforge.typechecker import check_program
    return check_program(parse(tokenize(fonte, arquivo), arquivo), arquivo,
                         source=fonte)


def test_um_point_depois_de_captura_e_acusado():
    ds = _diag('''
action f(x):
    match x:
        point n:
            yield "qualquer"
        point Integer:
            yield "inteiro"
''')
    erros = [d for d in ds if d.severity == "error"]
    assert len(erros) == 1
    assert "nunca casa" in erros[0].message
    assert erros[0].code == "point-inalcancavel"
    # A linha do ponto morto, e a dica apontando a captura.
    assert erros[0].line == 6
    assert "linha 4" in erros[0].hint


def test_uma_captura_com_guarda_nao_torna_o_resto_inalcancavel():
    """`point n when n bigger 100:` casa com tudo **se a condição
    valer** — o que vem abaixo continua alcançável. Sem essa distinção,
    a checagem acusaria o padrão mais útil do `match`."""
    ds = _diag('''
action f(n):
    match n:
        point x when x bigger 100:
            yield "grande"
        point Integer:
            yield "inteiro"
        default:
            yield "outro"
''')
    assert [d for d in ds if d.code == "point-inalcancavel"] == []


def test_uma_captura_no_fim_e_legitima():
    ds = _diag('''
action f(v):
    match v:
        point Integer:
            yield "int"
        point resto:
            yield resto
''')
    assert [d for d in ds if d.code == "point-inalcancavel"] == []


def test_um_default_no_fim_nao_e_acusado():
    """`default` é a captura escrita como tal, e o parser não deixa pôr
    nada depois dele."""
    ds = _diag('''
action f(v):
    match v:
        point 1:
            yield "um"
        default:
            yield "outro"
''')
    assert [d for d in ds if d.code == "point-inalcancavel"] == []


def test_um_aviso_basta_mesmo_com_tres_pontos_mortos():
    """Um por ponto viraria três mensagens sobre a mesma causa."""
    ds = _diag('''
action f(x):
    match x:
        point n:
            yield 0
        point 1:
            yield 1
        point 2:
            yield 2
        point 3:
            yield 3
''')
    assert len([d for d in ds if d.code == "point-inalcancavel"]) == 1


def test_df_permitir_silencia_a_regra_nomeada():
    """Um analisador sem escape obriga a escolher entre conviver com um
    alarme e desligar a verificação inteira — e a segunda é o que
    acontece.

    O caso que provou a necessidade está no repositório: o exercício 139
    **demonstra** a armadilha, com um `assert` provando o comportamento.
    O analisador estava certo, e o exercício também.
    """
    ds = _diag('''
action f(x):
    match x:
        point n:
            yield "qualquer"
        // df: permitir point-inalcancavel
        point Integer:
            yield "inteiro"
''')
    assert [d for d in ds if d.code == "point-inalcancavel"] == []


def test_df_permitir_na_mesma_linha_tambem_vale():
    ds = _diag('''
action f(x):
    match x:
        point n:
            yield "qualquer"
        point Integer:    // df: permitir point-inalcancavel
            yield "inteiro"
''')
    assert [d for d in ds if d.code == "point-inalcancavel"] == []


def test_df_permitir_nao_silencia_a_regra_que_ninguem_nomeou():
    """Um `permitir` que silenciasse tudo naquela linha esconderia o
    erro seguinte, que ninguém pediu para esconder."""
    ds = _diag('''
// df: permitir point-inalcancavel
out nao_existe_isto
''')
    erros = [d for d in ds if d.severity == "error"]
    assert len(erros) == 1
    assert "nao_existe_isto" in erros[0].message


def test_df_permitir_com_regra_inexistente_nao_silencia_nada():
    ds = _diag('''
action f(x):
    match x:
        point n:
            yield 1
        // df: permitir regra-que-nao-existe
        point 5:
            yield 2
''')
    assert [d for d in ds if d.code == "point-inalcancavel"]


def test_df_permitir_aceita_varias_regras_numa_linha():
    ds = _diag('''
action f(x):
    match x:
        point n:
            yield 1
        // df: permitir point-inalcancavel, match-incompleto
        point 5:
            yield 2
''')
    assert [d for d in ds if d.code == "point-inalcancavel"] == []


def test_o_lsp_le_o_permitir_do_texto_do_editor_e_nao_do_disco(tmp_path):
    """Num arquivo não salvo, ler do disco silenciaria a regra errada —
    ou nenhuma. O LSP reanalisa a cada tecla."""
    from dataforge.lsp import analisar

    arquivo = tmp_path / "a.df"
    # No disco, SEM o permitir.
    arquivo.write_text('''action f(x):
    match x:
        point n:
            yield 1
        point 5:
            yield 2
''', encoding="utf-8")

    # No editor, COM o permitir — é este que vale.
    do_editor = '''action f(x):
    match x:
        point n:
            yield 1
        // df: permitir point-inalcancavel
        point 5:
            yield 2
'''
    a = analisar(do_editor, arquivo.as_uri())
    mortos = [d for d in a.diagnosticos if "nunca casa" in d["message"]]
    assert mortos == []


def test_a_verificacao_local_roda_todo_gerador_do_repositorio():
    """`scripts/verificar_tudo.sh` existe para rodar o que o CI roda.

    A lista de geradores nele é escrita à mão, e um gerador novo que
    fique de fora recria o problema que o script veio resolver: o CI
    reprova com "gerado desatualizado" e a verificação local diz que
    está tudo bem.

    Já aconteceu de outra forma nesta sessão: eu regenerei à mão com uma
    lista mais curta que a do script, concluí "geradores estáveis" e o
    CI acusou `doc/superficie.json`. A lição é a mesma — quem confere
    precisa usar a lista de um lugar só.

    Três geradores ficam de fora de propósito: `gerar_paginas.py` é
    biblioteca do `gerar_conteudo.py` (não roda sozinho), e
    `gerar_tarball.py`, `gerar_binario.py`, `gerar_runtime_web.py` e
    `gerar_problemas.py` produzem artefatos de release, não arquivos
    versionados que possam ficar atrasados.
    """
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(raiz, "scripts", "verificar_tudo.sh")
    if not os.path.isfile(script):
        pytest.skip("o script não está neste checkout")

    texto = open(script, encoding="utf-8").read()

    #: Não são geradores de arquivo versionado.
    fora = {
        "gerar_paginas.py",        # biblioteca do gerar_conteudo
        "gerar_tarball.py",        # artefato de release
        "gerar_binario.py",        # artefato de release
        "gerar_runtime_web.py",    # artefato de release
        "gerar_problemas.py",      # artefato de release
    }

    faltando = []
    for padrao in ("tools/gerar_*.py", "scripts/gerar_*.py",
                   "site/scripts/gerar_*.py"):
        for caminho in glob.glob(os.path.join(raiz, padrao)):
            nome = os.path.basename(caminho)
            if nome in fora:
                continue
            relativo = os.path.relpath(caminho, raiz).replace(os.sep, "/")
            if relativo not in texto:
                faltando.append(relativo)

    assert not faltando, (
        f"gerador(es) fora de verificar_tudo.sh: {sorted(faltando)} — "
        f"o CI vai acusar 'gerado desatualizado' e a verificação local "
        f"vai passar")


def test_o_dockerfile_copia_todo_pacote_que_o_pyproject_declara():
    """O `pip install` dentro do Docker falha com "package directory
    'editor' does not exist" se o `COPY` não trouxer a pasta.

    E falha **só na CI**: no repositório a pasta existe, e o
    `pip install -e .` local nunca reclama. Foi exatamente o que
    aconteceu ao declarar `dataforge.editor`.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        import tomllib
    except ImportError:
        pytest.skip("tomllib só existe a partir do 3.11")

    with open(os.path.join(raiz, "pyproject.toml"), "rb") as f:
        dados = tomllib.load(f)
    setup = dados["tool"]["setuptools"]
    mapa = setup.get("package-dir", {})

    dockerfile = open(os.path.join(raiz, "Dockerfile"), encoding="utf-8").read()

    # A pasta de cada pacote, no nível de cima.
    pastas = set()
    for nome in setup["packages"]:
        caminho = mapa.get(nome) or nome.replace(".", "/")
        pastas.add(caminho.split("/")[0])

    faltando = [p for p in sorted(pastas)
                if f"COPY {p} " not in dockerfile
                and f"COPY {p}/" not in dockerfile]
    assert not faltando, (
        f"o Dockerfile não copia {faltando}, e o 'pip install' dele vai "
        f"falhar com \"package directory does not exist\"")


# ═══════════════════════════════════════════════════════════
#  Nenhuma mensagem fala de tipos do Python
#
#  `int`, `str`, `list`, `dict`, `NoneType` não existem
#  nesta linguagem. Uma mensagem nesses termos manda a pessoa
#  procurar na documentação errada — e ela não tem como saber
#  que `list` é `Cluster`.
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("fonte, proibido, esperado", [
    ('out 1 smaller "a"', "'str'", "String"),
    ('out 1 + [2]', "'list'", "Cluster"),
    ('out len(5)', "'int'", "Integer"),
    ('out int({"a": 1})', "'dict'", "Vault"),
    ('out {"a": 1} + {"b": 2}', "'dict'", "Vault"),
    ('out "x" - 1', "'str'", "String"),
])
def test_a_mensagem_usa_o_vocabulario_da_linguagem(fonte, proibido, esperado):
    saida = run(f'''
monitor:
    {fonte}
handle Error as e:
    out $"{{e.message}} || {{e.nota}}"
''')
    assert proibido not in saida, f"a mensagem fala de {proibido}"
    assert esperado in saida


def test_o_nome_de_tipo_e_trocado_so_entre_aspas():
    """Conservador de propósito: trocar a palavra solta estragaria um
    texto legítimo — uma mensagem sobre um arquivo chamado `list`, ou
    sobre a função `set` da própria stdlib."""
    from dataforge.interpreter import _traduzir_tipos

    assert _traduzir_tipos("type 'int' is wrong") == "type 'Integer' is wrong"
    # Sem aspas, fica: pode ser o nome de uma variável, de um arquivo,
    # de uma função.
    assert _traduzir_tipos("the file list.df is missing") == \
        "the file list.df is missing"
    assert _traduzir_tipos("") == ""
    assert _traduzir_tipos(None) is None


def test_acessar_membro_de_void_diz_o_que_fazer():
    """O caso mais comum: uma busca que não achou, um campo que não
    veio, uma chamada que devolveu `void`. A mensagem era "Cannot
    access member 'campo' on NoneType" — e `NoneType` não existe aqui.
    """
    saida = run('''
monitor:
    x := void
    out x.campo
handle Error as e:
    out e.message
    out e.dica
''')
    assert "NoneType" not in saida
    assert "Void" in saida
    # A saída: os dois operadores que existem para isso.
    assert "?." in saida
    assert "??" in saida


def test_o_caminho_seguro_continua_funcionando():
    """A mensagem nova não pode ter vindo de uma mudança que quebre
    `?.` — que é justamente o que ela recomenda."""
    saida = run('''
y := void
out y?.campo
out (y ?? {"campo": 7})["campo"]
''')
    assert saida.strip().splitlines() == ["void", "7"]


def test_a_dica_de_operacao_so_fala_quando_sabe():
    """Uma dica errada é pior que nenhuma."""
    saida = run('''
monitor:
    out 1 + [2]
handle Error as e:
    out e.dica
''')
    assert "append" in saida or "..." in saida

    # Um caso sem intenção óbvia não recebe dica inventada.
    outra = run('''
record P:
    x: Integer

monitor:
    out P(1) - P(2)
handle Error as e:
    out $"[{e.dica}]"
''')
    assert outra.strip() == "[]"


def test_ordenar_tipos_diferentes_aponta_is_e_isnt():
    """`is` e `isnt` comparam qualquer coisa; ordenar não tem resposta
    entre um texto e um número — e é essa a saída."""
    saida = run('''
monitor:
    out [1, "a"] >> sift x: x bigger 0
handle Error as e:
    out e.message
    out e.dica
''')
    assert "has no answer" in saida
    assert "'is'" in saida


def test_nenhuma_mensagem_de_erro_do_interpretador_cita_tipo_do_python():
    """A trava da causa.

    Uma mensagem escrita à mão com `type(x).__name__` volta a falar
    `NoneType` ou `dict` sem nada denunciar — foi assim que as cinco
    que este bloco corrigiu chegaram lá. Quem quiser o nome do tipo tem
    `_nome_do_tipo`, que responde no vocabulário da linguagem.
    """
    import re

    fonte = open("dataforge/interpreter.py", encoding="utf-8").read()

    # `type(...).__name__` dentro de uma f-string de mensagem.
    suspeitos = []
    for numero, linha in enumerate(fonte.split("\n"), 1):
        if "#" in linha.split("type(")[0]:
            continue        # comentário
        if "type(" in linha and "__name__" in linha:
            # O uso legítimo: comparar, registrar, despachar. O que não
            # vale é ir para o texto de um erro.
            if not re.search(r'f"[^"]*\{type\([^)]*\)\.__name__\}', linha):
                continue
            # A própria tradutora é o único uso legítimo: ela recebe o
            # nome do Python justamente para trocá-lo. Reconhecer a
            # chamada, e não a linha, mantém a trava fechada.
            if "_traduzir_tipos(" in linha:
                continue
            suspeitos.append(f"{numero}: {linha.strip()[:70]}")

    assert not suspeitos, (
        "mensagem de erro usando o nome do tipo do Python — use "
        "'self._nome_do_tipo(valor)':\n  " + "\n  ".join(suspeitos))


@pytest.mark.parametrize("fonte, esperado", [
    ("out 5[1:2]", "an Integer"),
    ("out 5.metodo()", "an Integer"),
    ("x := yes\nout x + [1]", "a Boolean"),
])
def test_o_nome_do_tipo_chega_a_toda_mensagem(fonte, esperado):
    """`Boolean` é o caso que prova o caminho por subclasse: `bool` é
    `int` em Python, então ele cai no último recurso de
    `_nome_do_tipo` — e ali o nome do Python não serve."""
    saida = run(f'''
monitor:
    {fonte.replace(chr(10), chr(10) + "    ")}
handle Error as e:
    out e.message
''')
    assert esperado in saida
    for py in ("'int'", "'bool'", "'str'", "'dict'", "'list'", "NoneType"):
        assert py not in saida


def test_chamar_metodo_de_void_tambem_aponta_o_operador_seguro():
    saida = run('''
monitor:
    x := void
    out x.buscar()
handle Error as e:
    out e.message
    out e.dica
''')
    assert "Void" in saida
    assert "?." in saida


def test_nenhum_exercicio_compara_dois_tempos_sem_margem():
    """`assert a_ms bigger b_ms` é um sorteio quando os dois lados são
    microssegundos.

    O exercício 215 comparava uma busca O(n) num cluster de **3 mil**
    itens com uma busca O(1) num vault, e a razão medida era de ~2x —
    com uma volta em cinco dando 1,3x. Reprovou a CI num macOS
    carregado, no teste que compara a saída com a compilação ligada e
    desligada.

    A causa não era a medição: o `in` de um cluster é um laço em C,
    rápido o bastante para o **custo de despacho do interpretador**
    dominar os dois lados e mascarar a diferença assintótica. Medido:
    2,7x com 3 mil, 9x com 20 mil, 43x com 100 mil, 127x com 300 mil.

    A correção é medir onde a diferença aparece e cobrar uma **margem**:
    `razao bigger 5` é verdadeiro com folga e falha alto se a medição
    quebrar — `bigger` sozinho passa por acidente.
    """
    import glob
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suspeitos = []

    # Um 'assert' que compara dois campos de tempo, sem divisão nem
    # margem: os dois lados são medidas, e o resultado é ruído.
    padrao = re.compile(
        r'assert\s+\w+\[\"(?:total_ms|media_ms|mediana_ms|p95_ms)\"\]\s*'
        r'(?:bigger|smaller)(?:_eq)?\s+\w+\[\"(?:total_ms|media_ms|'
        r'mediana_ms|p95_ms)\"\]')

    for caminho in glob.glob(os.path.join(raiz, "exercicios", "*", "*.df")):
        fonte = open(caminho, encoding="utf-8").read()
        for achado in padrao.finditer(fonte):
            linha = fonte[:achado.start()].count("\n") + 1
            suspeitos.append(
                f"{os.path.relpath(caminho, raiz)}:{linha}")

    assert not suspeitos, (
        "exercício comparando dois tempos medidos sem margem — divida e "
        "cobre um fator:\n  " + "\n  ".join(suspeitos))


# ═══════════════════════════════════════════════════════════
#  'dataforge test' não podia reportar verde num trial que
#  falha
#
#  Um arquivo com `crucible`/`trial` REGISTRA as suites e não
#  as roda — quem as roda é `Crucible.run()`. O corredor caía
#  no caso "sem ações test_, o próprio arquivo é o caso" e
#  contava o arquivo como UM TESTE QUE PASSOU.
#
#  Um teste que falha reportando "Tudo verde" é a pior falha
#  possível num corredor de testes: a suíte fica vermelha e o
#  CI passa. Um arquivo com dez trials, um deles quebrado,
#  saía com código 0.
# ═══════════════════════════════════════════════════════════

def _projeto_com_crucible(tmp_path, corpo):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "x_test.df").write_text(corpo, encoding="utf-8")
    (tmp_path / "forge.toml").write_text(
        '[projeto]\nnome = "x"\nversao = "1.0.0"\n', encoding="utf-8")
    return tmp_path


def _rodar_test(pasta, *extra):
    import subprocess
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run(
        [_sys.executable, "-m", "dataforge", "test", *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(pasta), env={**os.environ, "PYTHONPATH": raiz,
                             "NO_COLOR": "1"})
    return r


def test_dataforge_test_reprova_um_trial_que_falha(tmp_path):
    pasta = _projeto_com_crucible(tmp_path, '''adopt Crucible

crucible "suite":
    trial "este falha":
        expect 1 is 2

    trial "este passa":
        expect 1 is 1
''')
    r = _rodar_test(pasta)
    assert r.returncode == 1, (
        f"código 0 com um trial quebrado:\n{r.stdout}{r.stderr}")
    assert "falharam" in r.stdout
    # E nomeia QUAL: "1 de 2 falhou" sem dizer qual não serve.
    assert "este falha" in r.stdout


def test_dataforge_test_conta_os_trials_e_nao_os_arquivos(tmp_path):
    """Um arquivo com dois trials contava como **um** teste. Num projeto
    de 30 arquivos com 2 trials cada, o relatório dizia 30 onde eram
    60 — e um número de testes errado é o começo da desconfiança."""
    pasta = _projeto_com_crucible(tmp_path, '''adopt Crucible

crucible "suite":
    trial "um":
        expect 1 is 1

    trial "dois":
        expect 2 is 2

    trial "tres":
        expect 3 is 3
''')
    r = _rodar_test(pasta)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "3 passaram" in r.stdout


def test_dataforge_test_e_dataforge_crucible_concordam(tmp_path):
    """Os dois comandos veem a mesma suíte, e discordavam: `crucible`
    reprovava e `test` passava. O mais óbvio dos dois nomes era o que
    mentia."""
    import subprocess
    import sys as _sys

    pasta = _projeto_com_crucible(tmp_path, '''adopt Crucible

crucible "suite":
    trial "quebrado":
        expect yes is no
''')
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ambiente = {**os.environ, "PYTHONPATH": raiz, "NO_COLOR": "1"}
    codigos = {}
    for comando in ("test", "crucible"):
        r = subprocess.run([_sys.executable, "-m", "dataforge", comando],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=str(pasta), env=ambiente)
        codigos[comando] = r.returncode
    assert codigos["test"] == codigos["crucible"] == 1, codigos


def test_um_trial_pendente_nao_conta_como_falha(tmp_path):
    pasta = _projeto_com_crucible(tmp_path, '''adopt Crucible

crucible "suite":
    trial "feito":
        expect 1 is 1

    trial "ainda nao" pending "amanha":
        expect 1 is 2
''')
    r = _rodar_test(pasta)
    assert r.returncode == 0, r.stdout + r.stderr


def test_um_arquivo_sem_crucible_continua_como_antes(tmp_path):
    """A correção não podia mudar o caminho das ações `test_`, que é
    como os quatro projetos do repositório escrevem os seus."""
    pasta = _projeto_com_crucible(tmp_path, '''adopt Arcane.Test as T

action test_soma():
    T.assert_equal(2 + 2, 4)

action test_falha():
    T.assert_equal(1, 2)
''')
    r = _rodar_test(pasta)
    assert r.returncode == 1
    assert "test_falha" in r.stdout
    assert "test_soma" in r.stdout or "1 passaram" in r.stdout


def test_um_arquivo_que_nao_e_teste_nenhum_continua_passando(tmp_path):
    """Um `.df` dentro de `tests/` que só define coisas — um helper —
    não pode virar falha."""
    pasta = _projeto_com_crucible(tmp_path, '''action ajudar(x):
    yield x * 2
''')
    r = _rodar_test(pasta)
    assert r.returncode == 0, r.stdout + r.stderr
