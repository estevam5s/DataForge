"""Cluster<T>, Vault<K, V> e Set<T>: o tipo do CONTEUDO.

Ate aqui o parser recusava 'Cluster<Integer>' com a frase "o tipo do que
esta DENTRO de uma colecao nao e verificado". Agora e, em tres momentos:

1. na FRONTEIRA — declaracao, parametro, retorno, campo — todo item e
   conferido, como qualquer anotacao;
2. na INSERCAO — uma colecao que NASCE numa declaracao tipada (literal,
   compreensao, padrao de campo) recusa 'append', 'insert', 'xs[i] :=' e
   companhia fora do tipo;
3. ANTES DE RODAR — o 'check' prova o que um literal garante.

A guarda do item 2 so vale para a colecao que nasce ali, e isso e de
proposito: uma colecao que ja existia e conferida na entrada e continua
sendo o MESMO objeto. Copia-la para guardar quebraria, em silencio, toda
acao que recebe uma lista para modificar.
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError, ParseError   # noqa: E402
from dataforge.formatter import format_source             # noqa: E402
from dataforge.interpreter import Interpreter              # noqa: E402
from dataforge.lexer import tokenize                       # noqa: E402
from dataforge.parser import parse                         # noqa: E402
from dataforge.typechecker import check_program            # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue().strip()


def erro_de(fonte):
    try:
        rodar(fonte)
    except DataForgeError as erro:
        return erro
    raise AssertionError("era para dar erro, e rodou")


def diagnosticos(fonte, codigo=None):
    todos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    return [d for d in todos if codigo is None or d.code == codigo]


# ── sintaxe ──────────────────────────────────────────────────

@pytest.mark.parametrize("anotacao", [
    "Cluster<Integer>", "Vault<String, Integer>", "Set<String>",
    "Cluster<Vault<String, Float>>", "Vault<String, Cluster<Integer>>",
    "Cluster<Cluster<Integer>>",
])
def test_a_anotacao_compila_em_todo_lugar(anotacao):
    fonte = f'''
action f(x: {anotacao}) -> {anotacao}:
    yield x
record R:
    campo: {anotacao}
blueprint B(c: {anotacao}):
    d: {anotacao} := void
'''
    parse(tokenize(fonte, "t"), "t")


def test_tipo_que_nao_e_colecao_nao_aceita_conteudo():
    with pytest.raises(ParseError) as erro:
        parse(tokenize("x: Integer<String> := 1\n", "t"), "t")
    assert "Cluster<T>" in erro.value.message


def test_aridade_do_conteudo():
    with pytest.raises(ParseError) as erro:
        parse(tokenize("x: Vault<String> := {}\n", "t"), "t")
    assert "Vault<K, V>" in erro.value.message
    with pytest.raises(ParseError):
        parse(tokenize("x: Cluster<Integer, String> := []\n", "t"), "t")


def test_o_formatador_nao_espaca_o_generico():
    fonte = "xs: Cluster<Vault<String, Integer>> := []\n"
    formatado = format_source(fonte)
    assert "Cluster<Vault<String, Integer>>" in formatado
    assert format_source(formatado) == formatado


# ── fronteira ────────────────────────────────────────────────

def test_declaracao_confere_cada_item_e_diz_qual():
    erro = erro_de('xs: Cluster<Integer> := [1, 2, "tres", 4]\n')
    assert erro.line == 1
    assert "Cluster<Integer>" in erro.message
    assert "2" in erro.message and "String" in erro.message


def test_vault_confere_chave_e_valor():
    assert "chave" in erro_de('v: Vault<String, Integer> := {1: 2}\n').message.lower() \
        or "key" in erro_de('v: Vault<String, Integer> := {1: 2}\n').message.lower()
    erro = erro_de('v: Vault<String, Integer> := {"a": 1, "b": "x"}\n')
    assert '"b"' in erro.message or "'b'" in erro.message


def test_parametro_e_retorno():
    erro = erro_de('''
action soma(v: Cluster<Integer>) -> Integer:
    yield sum(v)
soma([1, "2"])
''')
    assert "parameter 'v'" in erro.message
    erro = erro_de('''
action nomes() -> Cluster<String>:
    yield ["ana", 7]
nomes()
''')
    assert "return value" in erro.message


def test_aninhado():
    assert rodar('''
m: Vault<String, Cluster<Integer>> := {"a": [1, 2], "b": []}
out len(m["a"])
''') == "2"
    erro = erro_de('m: Vault<String, Cluster<Integer>> := {"a": [1, "x"]}\n')
    assert "Cluster<Integer>" in erro.message


def test_integer_serve_onde_se_pede_float_e_any_aceita_tudo():
    assert rodar('xs: Cluster<Float> := [1, 2.5]\nys: Cluster<Any> := [1, "a"]\nout len(xs) + len(ys)') == "4"


def test_conteudo_de_blueprint_e_de_record():
    assert rodar('''
record Item:
    nome: String
blueprint Pedido:
    itens: Cluster<Item> := []
p := spawn Pedido()
p.itens.append(Item("caneta"))
out len(p.itens)
''') == "1"
    erro = erro_de('''
record Item:
    nome: String
blueprint Pedido:
    itens: Cluster<Item> := []
(spawn Pedido()).itens.append("caneta")
''')
    assert "Item" in erro.message and "String" in erro.message


# ── insercao ─────────────────────────────────────────────────

@pytest.mark.parametrize("operacao", [
    'xs.append("x")',
    'xs.insert(0, "x")',
    'xs.extend([4, "x"])',
    'xs[0] := "x"',
    'xs += ["x"]',
])
def test_cluster_tipado_recusa_insercao_fora_do_tipo(operacao):
    erro = erro_de(f"xs: Cluster<Integer> := [1, 2, 3]\n{operacao}\n")
    assert erro.line == 2, f"sem a linha certa: {erro.line}"
    assert "Cluster<Integer>" in erro.message


@pytest.mark.parametrize("operacao", [
    'v["b"] := "x"',
    'v[2] := 3',
    'v.set("b", "x")',
    'v.update({"b": "x"})',
])
def test_vault_tipado_recusa_insercao_fora_do_tipo(operacao):
    erro = erro_de(f'v: Vault<String, Integer> := {{"a": 1}}\n{operacao}\n')
    assert erro.line == 2
    assert "Vault<String, Integer>" in erro.message


def test_insercao_certa_passa_e_o_valor_continua_um_cluster():
    assert rodar('''
xs: Cluster<Integer> := []
xs.append(1)
xs.insert(0, 0)
xs.extend([2, 3])
xs[0] := 9
xs += [4]
out xs, typeof(xs), xs is [9, 1, 2, 3, 4]
''') == "[9, 1, 2, 3, 4] Cluster yes"


def test_compreensao_nasce_tipada():
    erro = erro_de('''
xs: Cluster<Integer> := [i * 2 cycle i in [1, 2]]
xs.append("x")
''')
    assert erro.line == 3


def test_colecao_que_ja_existia_e_conferida_e_continua_a_mesma():
    """Copiar para guardar quebraria quem passa uma lista para modificar."""
    assert rodar('''
original := [1, 2]
action acrescentar(xs: Cluster<Integer>, n: Integer):
    xs.append(n)
acrescentar(original, 3)
alias: Cluster<Integer> := original
alias.append(4)
out original
''') == "[1, 2, 3, 4]"


def test_cada_instancia_tem_a_sua_colecao_tipada():
    assert rodar('''
blueprint Caixa:
    itens: Cluster<Integer> := []
a := spawn Caixa()
b := spawn Caixa()
a.itens.append(1)
out len(a.itens), len(b.itens)
''') == "1 0"


def test_set_tipado():
    erro = erro_de('adopt Arcane.Collections as C\n'
                   's: Set<String> := C.set(["a"])\ns.add(1)\n')
    assert erro.line == 3 and "Set<String>" in erro.message


def test_mensagem_nao_cita_tipo_do_python():
    erro = erro_de('xs: Cluster<Integer> := []\nxs.append([1])\n')
    for palavra in ("list", "int", "ClusterTipado", "dict"):
        assert f"'{palavra}'" not in erro.message and f" {palavra} " not in erro.message


def test_json_e_igualdade_continuam():
    assert rodar('''
adopt Arcane.Serialization as S
xs: Cluster<Integer> := [1, 2]
v: Vault<String, Integer> := {"a": 1}
out S.to_json(xs), S.to_json(v), xs is [1, 2], v is {"a": 1}
''') == '[1, 2] {"a": 1} yes yes'


# ── antes de rodar ───────────────────────────────────────────

def test_check_prova_o_conteudo_de_um_literal():
    assert diagnosticos('xs: Cluster<Integer> := [1, "dois"]\n', "tipo-do-conteudo")
    assert diagnosticos('v: Vault<String, Integer> := {"a": "x"}\n', "tipo-do-conteudo")
    assert diagnosticos('xs: Cluster<Integer> := []\nxs.append("x")\n', "tipo-do-conteudo")
    assert diagnosticos('''
action soma(v: Cluster<Integer>) -> Integer:
    yield 0
soma([1, "2"])
''', "tipo-do-conteudo")


def test_check_cala_quando_nao_prova():
    fonte = '''
action ler():
    yield []
xs: Cluster<Integer> := ler()
ys: Cluster<Integer> := [1, 2]
ys.append(len(xs))
x := ys[0]
z: Integer := x
out z
'''
    assert not [d for d in diagnosticos(fonte) if d.severity == "error"]


def test_check_tipo_interno_desconhecido():
    erros = diagnosticos("xs: Cluster<Inteiro> := []\n", "unknown-type")
    assert erros and "Integer" in (erros[0].hint or "")


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
