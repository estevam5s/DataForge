"""`Arcane.C` — falar com biblioteca nativa, de verdade.

A ponte para o Python (`adopt Python.numpy`) resolve "preciso de uma
biblioteca que alguém já escreveu **em Python**". O que faltava é o
degrau de baixo: chamar uma função de uma biblioteca **C** — a `libm`, a
`libz`, o `.so` que a empresa mantém há quinze anos — sem escrever um
módulo de extensão e sem trazer dependência.

O que os testes cobram:

1. abrir a biblioteca e chamar função com tipos declarados;
2. ponteiro cru: ler, escrever, andar, e o nulo que se reconhece;
3. estrutura com **layout real** — tamanho, alinhamento e deslocamento
   de cada campo, que é a parte que ninguém acerta de cabeça;
4. callback: uma ação DataForge chamada de dentro do C (`qsort`);
5. a mensagem quando a biblioteca não existe — o erro mais comum de FFI,
   e o que costuma vir ilegível.
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout
from ctypes.util import find_library

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                  # noqa: E402
from dataforge.interpreter import Interpreter                 # noqa: E402
from dataforge.lexer import tokenize                          # noqa: E402
from dataforge.parser import parse                            # noqa: E402
from dataforge.stdlib import get_module                       # noqa: E402

#: Sem libc/libm não há o que testar — e num sistema assim o módulo
#: também não serve para nada. Pular é honesto; falhar seria ruído.
TEM_LIBC = find_library("c") is not None
TEM_LIBM = find_library("m") is not None or sys.platform == "darwin"
precisa_c = pytest.mark.skipif(not TEM_LIBC, reason="sem libc neste sistema")
precisa_m = pytest.mark.skipif(not TEM_LIBM, reason="sem libm neste sistema")


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


# ── abrir e chamar ───────────────────────────────────────────

@precisa_m
def test_chamar_uma_funcao_de_biblioteca():
    assert rodar('''
adopt Arcane.C as C

libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
potencia := libm.funcao("pow", ["f64", "f64"], "f64")

out raiz(16.0), potencia(2.0, 10.0)
''') == "4.0 1024.0"


@precisa_c
def test_texto_e_inteiro_atravessam():
    assert rodar('''
adopt Arcane.C as C

libc := C.padrao()
tamanho := libc.funcao("strlen", ["texto"], "tamanho")
absoluto := libc.funcao("abs", ["i32"], "i32")

out tamanho("dataforge"), absoluto(-42)
''') == "9 42"


@precisa_c
def test_a_biblioteca_diz_o_que_ela_tem():
    assert rodar('''
adopt Arcane.C as C
libc := C.padrao()
out libc.tem("strlen"), libc.tem("nao_existe_mesmo"), libc.nome() isnt ""
''') == "yes no yes"


def test_biblioteca_que_nao_existe_tem_mensagem_util():
    erro = erro_de('adopt Arcane.C as C\nC.carregar("libnaoexisteaqui")\n')
    assert "libnaoexisteaqui" in erro.message
    assert (erro.dica or "") != ""
    for palavra in ("OSError", "Traceback"):
        assert palavra not in erro.message


@precisa_c
def test_simbolo_que_nao_existe_diz_o_nome():
    erro = erro_de('''
adopt Arcane.C as C
libc := C.padrao()
libc.funcao("funcao_que_nao_existe", [], "i32")
''')
    assert "funcao_que_nao_existe" in erro.message


def test_um_tipo_inventado_e_recusado_com_a_lista():
    erro = erro_de('''
adopt Arcane.C as C
C.tamanho_de("inteirao")
''')
    assert "inteirao" in erro.message
    assert "i32" in erro.message or "i32" in (erro.nota or "")


# ── tipos, tamanho e layout ──────────────────────────────────

def test_os_tamanhos_sao_os_do_sistema():
    assert rodar('''
adopt Arcane.C as C
out C.tamanho_de("i8"), C.tamanho_de("i32"), C.tamanho_de("f64")
out C.tamanho_de("ponteiro") in [4, 8], C.endianness() in ["little", "big"]
''') == "1 4 8\nyes yes"


def test_a_estrutura_tem_layout_de_verdade():
    assert rodar('''
adopt Arcane.C as C

Ponto := C.estrutura([["x", "f64"], ["y", "f64"]])
out Ponto.tamanho(), Ponto.deslocamentos()

// o padding aparece: um i8 antes de um i32 nao ocupa 5 bytes
Mista := C.estrutura([["flag", "i8"], ["valor", "i32"]])
out Mista.tamanho(), Mista.deslocamentos()["valor"], Mista.alinhamento()
''') == "16 {x: 0, y: 8}\n8 4 4"


def test_a_estrutura_vai_e_volta():
    assert rodar('''
adopt Arcane.C as C

Ponto := C.estrutura([["x", "i32"], ["y", "i32"]])
p := Ponto.criar({"x": 3, "y": 4})

out p.ler("x"), p.ler("y")
p.escrever("x", 30)
out p.tudo()
''') == "3 4\n{x: 30, y: 4}"


def test_a_uniao_ocupa_o_maior_campo():
    assert rodar('''
adopt Arcane.C as C
U := C.uniao([["i", "i32"], ["f", "f64"]])
out U.tamanho(), U.tamanho() is C.tamanho_de("f64")
''') == "8 yes"


# ── ponteiros crus ───────────────────────────────────────────

def test_o_ponteiro_le_escreve_e_anda():
    assert rodar('''
adopt Arcane.C as C

bloco := C.alocar(4 * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")

cycle i from 0 to 3:
    p.deslocar(i).escrever(i * 10)

out p.ler(), p.deslocar(2).ler(), p.endereco() bigger 0
out [p.deslocar(i).ler() cycle i in range(0, 4)]
C.liberar(bloco)
''') == "0 20 yes\n[0, 10, 20, 30]"


def test_o_ponteiro_nulo_se_reconhece():
    assert rodar('''
adopt Arcane.C as C
nulo := C.nulo()
out nulo.e_nulo(), nulo.endereco()
''') == "yes 0"


def test_ler_ponteiro_nulo_e_recusado_antes_de_quebrar_o_processo():
    erro = erro_de('adopt Arcane.C as C\nC.nulo().ler()\n')
    assert "nulo" in erro.message.lower()


def test_bytes_vao_e_voltam_sem_copia_escondida():
    assert rodar('''
adopt Arcane.C as C
adopt Arcane.Bytes as B

dados := C.de_bytes("dataforge")
out B.para_texto(C.para_bytes(dados, 9))
out len(C.para_bytes(dados, 4)), dados.tamanho()
''') == "dataforge\n4 10"


# ── callbacks ────────────────────────────────────────────────

@precisa_c
def test_o_c_chama_uma_acao_do_dataforge():
    assert rodar('''
adopt Arcane.C as C

libc := C.padrao()
qsort := libc.funcao("qsort", ["ponteiro", "tamanho", "tamanho", "ponteiro"], "void")

numeros := [42, 7, 19, 3]
bloco := C.alocar(len(numeros) * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")
cycle i in range(0, len(numeros)):
    p.deslocar(i).escrever(numeros[i])

action comparar(a, b):
    yield C.ponteiro(a, "i32").ler() - C.ponteiro(b, "i32").ler()

comparador := C.retorno_de_chamada(comparar, ["ponteiro", "ponteiro"], "i32")
qsort(bloco, 4, C.tamanho_de("i32"), comparador)

out [p.deslocar(i).ler() cycle i in range(0, 4)]
C.liberar(bloco)
''') == "[3, 7, 19, 42]"


def test_o_callback_vive_enquanto_alguem_o_segura():
    assert rodar('''
adopt Arcane.C as C

action dobro(x):
    yield x * 2

cb := C.retorno_de_chamada(dobro, ["i32"], "i32")
out cb.vivo(), cb.chamar(21)
cb.soltar()
out cb.vivo()
''') == "yes 42\nno"


# ── o módulo ─────────────────────────────────────────────────

def test_o_modulo_esta_registrado_e_descrito():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.C", "C"):
        assert get_module(nome) is not None, nome
    assert "Arcane.C" in DESCRICOES


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import ffi_c
    for pagina in ffi_c.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda(onde, codigo):
    rodar(codigo)


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
