"""Tuplas: a sequência de tamanho fixo, imutável, de tipos diferentes.

A linguagem tinha `Cluster` (lista) e `Vault` (mapa), e não tinha como
dizer "dois valores, nesta ordem, cada um do seu tipo". O contorno era um
cluster de dois itens — que aceita três, aceita zero, e deixa a leitura
por índice sem nenhuma garantia.

O que os testes cobram:

1. `(1, "a")` é uma tupla; `(1)` continua sendo agrupamento — e essa é a
   única ambiguidade que existe. `(1,)` é a tupla de um;
2. ela é **imutável**: escrever num índice é recusado;
3. `Tuple<Integer, String>` confere a POSIÇÃO e o TAMANHO;
4. desestruturação, `cycle`, `len`, `in`, igualdade estrutural e
   `typeof` funcionam sem que nada disso saiba que é tupla;
5. ela atravessa JSON e processo — e volta como tupla.
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError, ParseError      # noqa: E402
from dataforge.formatter import format_source                # noqa: E402
from dataforge.interpreter import Interpreter                # noqa: E402
from dataforge.lexer import tokenize                         # noqa: E402
from dataforge.parser import parse                           # noqa: E402
from dataforge.typechecker import check_program              # noqa: E402


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


def erros(fonte):
    return [d for d in diagnosticos(fonte) if d.severity == "error"]


# ── a forma ──────────────────────────────────────────────────

def test_a_tupla_e_o_agrupamento_nao_se_confundem():
    assert rodar('t := (1, "a")\nout t, typeof(t)') == '(1, "a") Tuple'
    assert rodar('x := (2 + 3) * 2\nout x, typeof(x)') == "10 Integer"
    assert rodar('um := (7,)\nout um, len(um), typeof(um)') == "(7,) 1 Tuple"
    assert rodar('vazia := ()\nout vazia, len(vazia)') == "() 0"


def test_a_tupla_le_por_indice_e_por_fatia():
    assert rodar('''
t := (10, "vinte", 30.0)
out t[0], t[1], t[2], t[-1]
out t[0:2], typeof(t[0:2])
''') == '10 vinte 30.0 30.0\n(10, "vinte") Tuple'


def test_a_tupla_e_imutavel():
    erro = erro_de('t := (1, 2)\nt[0] := 9\n')
    assert "Tuple" in erro.message
    assert "immutable" in erro.message.lower() or "imutáv" in erro.message.lower()
    assert erro.line == 2


def test_desestruturacao_cycle_len_e_pertencimento():
    assert rodar('''
t := (1, 2, 3)
a, b, c := t
soma := 0
cycle item in t:
    soma += item
out a, b, c, soma, len(t), 2 in t, 9 in t
''') == "1 2 3 6 3 yes no"


def test_igualdade_e_uso_como_chave():
    assert rodar('''
adopt Arcane.Collections as C
a := (1, "x")
b := (1, "x")
grade := {}
grade[a] := "achei"
out a is b, a isnt (1, "y"), grade[b], len(C.set([a, b]))
''') == "yes yes achei 1"


def test_a_tupla_dentro_de_colecao_e_de_record():
    assert rodar('''
record Ponto:
    lugar: Tuple<Float, Float>
pares := [(1, "um"), (2, "dois")]
p := Ponto((1.0, 2.0))
out len(pares), pares[1][1], p.lugar[0]
''') == "2 dois 1.0"


# ── o tipo ───────────────────────────────────────────────────

def test_tuple_confere_posicao_e_tamanho():
    assert rodar('t: Tuple<Integer, String> := (1, "a")\nout t[1]') == "a"
    erro = erro_de('t: Tuple<Integer, String> := ("a", 1)\n')
    assert "Tuple<Integer, String>" in erro.message
    assert "0" in erro.message and "String" in erro.message
    erro = erro_de('t: Tuple<Integer, String> := (1, "a", 2)\n')
    assert "3" in erro.message and "2" in erro.message


def test_tuple_em_parametro_e_retorno():
    assert rodar('''
action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield (a ~/ b, a % b)

inteiro, resto := dividir(17, 5)
out inteiro, resto
''') == "3 2"
    erro = erro_de('''
action f() -> Tuple<Integer, Integer>:
    yield (1, "dois")
f()
''')
    assert "return value" in erro.message


def test_tuple_aninhada_e_com_alias():
    assert rodar('''
type Coordenada := Tuple<Float, Float>
type Segmento := Tuple<Coordenada, Coordenada>
s: Segmento := ((0.0, 0.0), (1.0, 1.0))
out s[1][0]
''') == "1.0"
    assert "Coordenada" in erro_de('''
type Coordenada := Tuple<Float, Float>
c: Coordenada := (1.0, "dois")
''').message


def test_o_check_prova_o_que_o_literal_diz():
    assert diagnosticos('t: Tuple<Integer, String> := ("a", 1)\n', "tipo-do-conteudo")
    assert diagnosticos('t: Tuple<Integer, String> := (1, "a", 2)\n', "tipo-do-conteudo")
    assert not erros('''
action ler() -> Tuple<Integer, String>:
    yield (1, "a")
t: Tuple<Integer, String> := ler()
u: Tuple<Integer, String> := (2, "b")
out t[0] + u[0]
''')


# ── conviver com o resto ─────────────────────────────────────

def test_json_e_a_travessia_de_processo():
    assert rodar('''
adopt Arcane.Serialization as S
t := (1, "a")
out S.to_json(t)
''') == '[1, "a"]'


def test_a_tupla_atravessa_processo():
    assert rodar('''
adopt Arcane.Concurrent as P
action dobrar(par):
    yield (par[0] * 2, par[1])
saida := P.map_processos(dobrar, [(1, "a"), (2, "b")])
out saida[0][0], saida[1][1]
''') == "2 b"


def test_o_formatador_e_o_lint():
    fonte = 't := (1, "a")\nvazia := ()\num := (7,)\nx := (2 + 3) * 2\n'
    formatado = format_source(fonte)
    assert '(1, "a")' in formatado
    assert "(7,)" in formatado
    assert "()" in formatado
    assert format_source(formatado) == formatado


def test_a_mensagem_nao_cita_tipo_do_python():
    erro = erro_de('t: Tuple<Integer, String> := (1, 2)\n')
    for palavra in ("tuple", "int", "str"):
        assert f"'{palavra}'" not in erro.message


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import tipos_tuplas
    for pagina in tipos_tuplas.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda_e_passa_no_check(onde, codigo):
    rodar(codigo)
    ruins = [d for d in diagnosticos(codigo) if d.severity == "error"]
    assert not ruins, f"{onde}: {[d.message for d in ruins]}"


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
