"""`Arcane.Posse` — posse, empréstimo e liberação determinística.

Numa linguagem com coleta automática, "vazar memória" não é o problema:
o problema é o **recurso** — o arquivo que não fecha, a conexão que fica
aberta, o cadeado que ninguém solta. E o defeito irmão: duas partes do
programa escrevendo no mesmo objeto porque nenhuma delas sabe quem é o
dono.

Este módulo traz a disciplina de posse para um mundo com coletor. O que
ele NÃO faz é fingir ser Rust: não há ponteiro cru, não há região
inferida em tempo de compilação, e um objeto nunca vira endereço
inválido — o coletor impede. O que dá para garantir, e o que os testes
cobram:

1. **posse exclusiva**: quem move perde; usar depois de mover é erro com
   as duas linhas (onde moveu, onde usou);
2. **liberação determinística**: `soltar()` roda o finalizador AGORA, e
   uma vez só — é o `close()` que ninguém esquece, porque o `com(…)` o
   chama até quando o corpo falha;
3. **empréstimo**: leitura compartilhada OU escrita exclusiva, nunca as
   duas — a regra do borrow checker, cobrada quando roda;
4. **contagem de referência determinística**: o finalizador do
   compartilhado roda quando o ÚLTIMO dono solta, e não quando o coletor
   resolve passar;
5. **o ciclo vaza, e a referência fraca o quebra** — o mesmo problema do
   `Rc` de qualquer linguagem, demonstrado e resolvido;
6. **o `check` acusa o que prova**: uso depois de mover, recurso que
   ninguém solta, e empréstimo que escapa do escopo.
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                  # noqa: E402
from dataforge.interpreter import Interpreter                 # noqa: E402
from dataforge.lexer import tokenize                          # noqa: E402
from dataforge.parser import parse                            # noqa: E402
from dataforge.stdlib import get_module                       # noqa: E402
from dataforge.typechecker import check_program               # noqa: E402


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


# ── posse exclusiva ──────────────────────────────────────────

def test_o_dono_usa_e_solta():
    assert rodar('''
adopt Arcane.Posse as P

fechados := []
d := P.dono("conexao", lambda x => fechados.append(x))

out d.usar(lambda x => len(x)), d.vivo()
d.soltar()
out d.vivo(), fechados
''') == "7 yes\nno [conexao]"


def test_soltar_e_idempotente_e_o_finalizador_roda_uma_vez():
    assert rodar('''
adopt Arcane.Posse as P
vezes := []
d := P.dono(1, lambda x => vezes.append(x))
d.soltar()
d.soltar()
d.soltar()
out len(vezes)
''') == "1"


def test_usar_depois_de_soltar_diz_o_que_aconteceu():
    erro = erro_de('''
adopt Arcane.Posse as P
d := P.dono("arquivo")
d.soltar()
d.usar(lambda x => x)
''')
    assert "soltou" in erro.message or "released" in erro.message.lower()
    assert erro.line == 5


def test_mover_transfere_e_quem_moveu_perde():
    assert rodar('''
adopt Arcane.Posse as P
a := P.dono([1, 2])
b := a.mover()
out a.movido(), b.vivo(), b.usar(lambda x => len(x))
''') == "yes yes 2"
    erro = erro_de('''
adopt Arcane.Posse as P
a := P.dono([1, 2])
b := a.mover()
a.usar(lambda x => len(x))
''')
    assert "moveu" in erro.message or "moved" in erro.message.lower()
    assert erro.line == 5


def test_copia_e_clone_sao_coisas_diferentes():
    assert rodar('''
adopt Arcane.Posse as P
original := P.dono([1, 2])

rasa := original.copiar()
rasa.mudar(lambda x => x.append(3))

funda := original.clonar(lambda x => [...x])
funda.mudar(lambda x => x.append(9))

out original.usar(lambda x => len(x)), rasa.usar(lambda x => len(x))
out funda.usar(lambda x => len(x))
''') == "3 3\n4"


def test_com_solta_no_fim_mesmo_quando_o_corpo_falha():
    assert rodar('''
adopt Arcane.Posse as P
fechados := []

valor := P.com(P.dono("a", lambda x => fechados.append(x)),
               lambda x => len(x))
out valor, fechados

monitor:
    P.com(P.dono("b", lambda x => fechados.append(x)),
          lambda x => trigger "falhou no meio")
handle Error as e:
    out e.message, fechados
''') == "1 [a]\nfalhou no meio [a, b]"


# ── empréstimo ───────────────────────────────────────────────

def test_a_celula_deixa_muitos_lerem_ou_um_escrever():
    assert rodar('''
adopt Arcane.Posse as P
c := P.celula({"n": 0})

out c.ler(lambda v => v["n"])
c.escrever(lambda v => v.set("n", 5))
out c.ler(lambda v => v["n"]), c.emprestimos()
''') == "0\n5 0"


def test_escrever_durante_uma_leitura_e_recusado():
    erro = erro_de('''
adopt Arcane.Posse as P
c := P.celula([1])
c.ler(lambda v => c.escrever(lambda w => w.append(2)))
''')
    assert "lendo" in erro.message and "escrever" in erro.message
    assert "empréstimo" in (erro.nota or "")


def test_duas_leituras_ao_mesmo_tempo_passam():
    assert rodar('''
adopt Arcane.Posse as P
c := P.celula([1, 2])
out c.ler(lambda v => c.ler(lambda w => len(v) + len(w)))
out c.emprestimos()
''') == "4\n0"


def test_o_emprestimo_nao_sobrevive_ao_escopo():
    erro = erro_de('''
adopt Arcane.Posse as P
d := P.dono([1, 2])
fugitivo := d.emprestar()
fugitivo.ler()
''')
    assert "escopo" in erro.message or "scope" in erro.message.lower()


def test_o_dono_continua_dono_depois_do_emprestimo():
    assert rodar('''
adopt Arcane.Posse as P
d := P.dono([1])
d.usar(lambda x => len(x))
d.mudar(lambda x => x.append(2))
out d.vivo(), d.usar(lambda x => len(x))
''') == "yes 2"


def test_o_escopo_solta_tudo_na_ordem_inversa():
    assert rodar('''
adopt Arcane.Posse as P
saida := []

e := P.escopo()
e.dono("conexao", lambda x => saida.append(x))
e.dono("transacao", lambda x => saida.append(x))
arquivo := e.guardar(P.dono("arquivo", lambda x => saida.append(x)))

out e.quantos(), arquivo.usar(lambda x => len(x))
out e.soltar(), saida
out e.vivo(), e.soltar()
''') == "3 7\n3 [arquivo, transacao, conexao]\nno 0"


def test_com_escopo_solta_ate_quando_o_corpo_falha():
    assert rodar('''
adopt Arcane.Posse as P
saida := []

monitor:
    P.com_escopo(lambda e => e.dono("a", lambda x => saida.append(x))
                              .usar(lambda x => trigger "no meio"))
handle Error as e:
    out e.message, saida
''') == "no meio [a]"


# ── contagem de referência ───────────────────────────────────

def test_o_compartilhado_solta_quando_o_ultimo_sai():
    assert rodar('''
adopt Arcane.Posse as P
fechados := []
a := P.compartilhado("cache", lambda x => fechados.append(x))
b := a.clonar()
c := a.clonar()

out a.contar()
b.soltar()
out a.contar(), fechados
c.soltar()
a.soltar()
out a.contar(), fechados
''') == "3\n2 []\n0 [cache]"


def test_o_atomico_conta_certo_com_threads():
    assert rodar('''
adopt Arcane.Posse as P
adopt Arcane.Concurrent as C

fechados := []
raiz := P.atomico("recurso", lambda x => fechados.append(x))
copias := []

action clonar_uma(i):
    copias.append(raiz.clonar())

C.para_cada(clonar_uma, [i cycle i in range(1, 51)])
out raiz.contar()

cycle copia in copias:
    copia.soltar()
out raiz.contar(), fechados
raiz.soltar()
out fechados
''') == "51\n1 []\n[recurso]"


def test_a_referencia_fraca_nao_segura_e_diz_quando_morreu():
    assert rodar('''
adopt Arcane.Posse as P
forte := P.compartilhado({"id": 1})
fraca := P.fraco(forte)

out fraca.vivo(), fraca.obter().tem()
forte.soltar()
out fraca.vivo(), fraca.obter().tem()
''') == "yes yes\nno no"


def test_o_ciclo_vaza_e_a_fraca_o_quebra():
    assert rodar('''
adopt Arcane.Posse as P

fechados := []
pai := P.compartilhado({"nome": "pai"}, lambda x => fechados.append("pai"))
filho := P.compartilhado({"nome": "filho"}, lambda x => fechados.append("filho"))

// o ciclo: cada um guarda uma referência FORTE do outro
pai.usar(lambda v => v.set("filho", filho.clonar()))
filho.usar(lambda v => v.set("pai", pai.clonar()))

pai.soltar()
filho.soltar()
out fechados, pai.contar(), filho.contar()
''') == "[] 1 1"
    assert rodar('''
adopt Arcane.Posse as P

fechados := []
pai := P.compartilhado({"nome": "pai"}, lambda x => fechados.append("pai"))
filho := P.compartilhado({"nome": "filho"}, lambda x => fechados.append("filho"))

// a volta é FRACA: ela não conta
pai.usar(lambda v => v.set("filho", filho.clonar()))
filho.usar(lambda v => v.set("pai", P.fraco(pai)))

filho.soltar()
pai.soltar()
// o de fora solta primeiro, e leva junto o que ele possuia
out fechados
''') == "[pai, filho]"


# ── o que o analisador prova ─────────────────────────────────

def test_check_acusa_uso_depois_de_mover():
    d = diagnosticos('''
adopt Arcane.Posse as P
a := P.dono([1])
b := a.mover()
a.usar(lambda x => len(x))
''', "posse-movida")
    assert d and "mover" in d[0].message
    assert "3" in (d[0].hint or "") or "linha" in (d[0].hint or "").lower()


def test_check_avisa_recurso_que_ninguem_solta():
    d = diagnosticos('''
adopt Arcane.Posse as P
action carregar():
    d := P.dono("arquivo")
    yield 1
carregar()
''', "recurso-vazado")
    assert d and d[0].severity == "warning"


def test_check_cala_quando_o_recurso_sai_da_acao():
    assert not diagnosticos('''
adopt Arcane.Posse as P
action abrir():
    d := P.dono("arquivo")
    yield d
action usar():
    d := P.dono("arquivo")
    P.com(d, lambda x => len(x))
action passa():
    d := P.dono("arquivo")
    guardar(d)
action guardar(x):
    yield x
usar()
''', "recurso-vazado")


def test_check_avisa_emprestimo_que_escapa():
    d = diagnosticos('''
adopt Arcane.Posse as P
d := P.dono([1])
fugitivo := d.usar(lambda x => x)
''', "emprestimo-escapa")
    assert d and d[0].severity == "warning"


def test_check_nao_reclama_do_uso_normal():
    assert not erros('''
adopt Arcane.Posse as P
d := P.dono("arquivo", lambda x => x)
tamanho := d.usar(lambda x => len(x))
d.mudar(lambda x => x)
d.soltar()
out tamanho
''')


# ── layout e medida ──────────────────────────────────────────

def test_o_layout_mede_o_custo_de_um_objeto():
    saida = rodar('''
adopt Arcane.Memoria as Mem

blueprint Compacta:
    slots x, y
    x := 1
    y := 2

blueprint Solta:
    x := 1
    y := 2

com := Mem.layout(Compacta)
sem := Mem.layout(Solta)
out com["slots"], sem["slots"]
out com["campos"], com["bytes"] smaller sem["bytes"]
out Mem.comparar_layout(Compacta, Solta)["economia_percentual"] bigger 20
''')
    assert saida == "yes no\n[x, y] yes\nyes"


def test_o_tamanho_conta_o_que_esta_dentro():
    assert rodar('''
adopt Arcane.Memoria as Mem
pequeno := Mem.tamanho([1, 2])
grande := Mem.tamanho([1, 2, "um texto bem maior para ocupar espaco"])
out grande bigger pequeno
''') == "yes"


# ── o módulo ─────────────────────────────────────────────────

def test_o_modulo_esta_registrado_e_descrito():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Posse", "Posse"):
        assert get_module(nome) is not None, nome
    assert get_module("Arcane.Posse")["__name__"] == "Arcane.Posse"
    assert "Arcane.Posse" in DESCRICOES


def test_a_mensagem_nao_cita_tipo_do_python():
    erro = erro_de('adopt Arcane.Posse as P\nd := P.dono(1)\nd.soltar()\nd.usar(lambda x => x)\n')
    for palavra in ("list", "int", "dict", "NoneType", "Dono object"):
        assert f"'{palavra}'" not in erro.message


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import memoria_posse
    for pagina in memoria_posse.PAGINAS:
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


# ═══════════════════════════════════════════════════════════
#  Uma escrita que não escreve
# ═══════════════════════════════════════════════════════════

def _posse():
    from dataforge.stdlib import get_module
    return get_module("Arcane.Posse")


def test_escrever_num_valor_IMUTAVEL_realmente_escreve():
    """`Celula.escrever` entregava o valor para a ação mexer no lugar e
    **descartava** o retorno.

    Num cluster ou num vault isso funciona por acidente — mexer no
    lugar muda o mesmo objeto. Num número ou num texto não há como
    mexer no lugar, e `escrever(lambda v => v + 1)` não escrevia nada:
    o programa seguia com o valor velho, calado. Uma escrita que não
    escreve é o pior desfecho possível numa peça chamada `escrever`.
    """
    P = _posse()

    cel = P["celula"](10)
    cel.escrever(lambda v: v + 1)
    assert cel.ler(lambda v: v) == 11

    texto = P["celula"]("a")
    texto.escrever(lambda v: v + "b")
    assert texto.ler(lambda v: v) == "ab"


def test_mudar_num_dono_tambem_escreve():
    P = _posse()

    d = P["dono"](5)
    d.mudar(lambda v: v * 2)
    assert d.usar(lambda v: v) == 10


def test_devolver_void_continua_sendo_mexer_no_lugar():
    """Quem escreve `cel.escrever(lambda v => out v)` não está pedindo
    para guardar `void` — e um cluster mexido no lugar continua sendo o
    mesmo objeto."""
    P = _posse()

    cel = P["celula"]([1, 2])
    cel.escrever(lambda v: v.append(3))       # append devolve None aqui
    assert cel.ler(lambda v: list(v)) == [1, 2, 3]
