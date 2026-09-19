"""O coletor sob controle, e a arena — a parte 10, no que dela transfere.

Uma referência Deep Tech descreve allocator global, bump, slab e
`#[no_std]`. Nada disso se aplica a uma linguagem sobre o CPython: quem
aloca é o Python, e não há como trocá-lo por dentro.

O que **transfere**, e é onde estes testes moram:

1. **O coletor é controlável.** O CPython libera por contagem de
   referência na hora; o *coletor* existe só para o **ciclo**. Desligá-lo
   numa fase sensível à latência é a técnica clássica — e aqui ela é
   medida, não afirmada.
2. **`congelar` existe** (`gc.freeze`): o que já está vivo depois da
   carga sai das varreduras para sempre. É o que um servidor faz antes
   de aceitar o primeiro pedido.
3. **Arena**: um lote de objetos preparado de uma vez e reaproveitado,
   em vez de alocar e descartar por volta.
4. **Nada é afirmado sem medida.** O teste que diz "desligar o coletor
   reduz pausa" só vale se ele **medir** a pausa.
"""

import gc
import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.interpreter import Interpreter                  # noqa: E402
from dataforge.lexer import tokenize                           # noqa: E402
from dataforge.parser import parse                             # noqa: E402
from dataforge.stdlib import get_module                        # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue()


@pytest.fixture
def M():
    return get_module("Arcane.Memoria")


@pytest.fixture(autouse=True)
def coletor_intacto():
    """Nenhum teste daqui pode deixar o coletor desligado para os outros."""
    ligado = gc.isenabled()
    limiares = gc.get_threshold()
    yield
    gc.set_threshold(*limiares)
    if ligado and not gc.isenabled():
        gc.enable()
    elif not ligado and gc.isenabled():         # pragma: no cover
        gc.disable()


# ══════════════════════════════════════════════════════════════
#  Controle do coletor
# ══════════════════════════════════════════════════════════════

def test_o_coletor_liga_e_desliga(M):
    assert M["gc_ligado"]()
    M["gc_desligar"]()
    assert not M["gc_ligado"]()
    M["gc_ligar"]()
    assert M["gc_ligado"]()


def test_desligado_o_ciclo_sobrevive_e_o_resto_nao(M):
    """A distinção que quase todo mundo erra.

    Desligar o coletor **não** vaza memória em geral: a contagem de
    referência continua liberando na hora. Só o **ciclo** fica para
    trás — e é por isso que a técnica é segura num trecho curto.
    """
    M["gc_desligar"]()
    try:
        gc.collect()
        antes = len(gc.get_objects())
        for _ in range(200):
            a = {"x": None}
            b = {"y": a}
            a["x"] = b                       # ciclo
        sem_ciclo = [object() for _ in range(200)]
        del sem_ciclo                        # refcount: some na hora
        depois = len(gc.get_objects())
        assert depois > antes, "o ciclo devia ter ficado"
    finally:
        M["gc_ligar"]()
    assert M["coletar"]() >= 0


def test_o_escopo_sem_gc_religa_mesmo_se_o_corpo_falhar(M):
    """Deixar o coletor desligado por causa de um erro é pior que a pausa."""
    with pytest.raises(Exception):
        M["sem_gc"](lambda: 1 / 0)
    assert M["gc_ligado"](), "o coletor tinha de voltar"


def test_sem_gc_devolve_o_valor_do_corpo(M):
    assert M["sem_gc"](lambda: 7 * 6) == 42


def test_os_limiares_sao_lidos_e_ajustados(M):
    original = M["gc_limiares"]()
    assert len(original) == 3
    M["gc_limiares"](5000, 20, 20)
    assert M["gc_limiares"]()[0] == 5000
    M["gc_limiares"](*original)
    assert M["gc_limiares"]() == original


def test_congelar_tira_o_que_ja_vive_das_varreduras(M):
    """É o que um servidor faz antes de aceitar o primeiro pedido."""
    antes = M["gc_congelados"]()
    M["gc_congelar"]()
    depois = M["gc_congelados"]()
    assert depois > antes
    M["gc_descongelar"]()
    assert M["gc_congelados"] () == 0


def test_as_geracoes_sao_relatadas(M):
    contas = M["gc_geracoes"]()
    assert len(contas) == 3
    for geracao in contas:
        assert "coletas" in geracao
        assert "colecionados" in geracao


# ══════════════════════════════════════════════════════════════
#  A medida — nada é afirmado sem ela
# ══════════════════════════════════════════════════════════════

def test_desligar_o_coletor_reduz_a_pausa_medida(M):
    """A afirmação da documentação, conferida.

    Sem esta medida, "desligar o coletor reduz pausa" seria fé. A
    comparação é da MESMA carga, e o que se mede é o tempo que o
    coletor passou parando o programa.
    """
    P = get_module("Arcane.Perfil")

    def churn():
        for _ in range(6000):
            a = {"x": None}
            b = {"y": a}
            a["x"] = b
        return "ok"

    gc.collect()
    com = P["gc_pausas"](churn)
    sem = P["gc_pausas"](lambda: M["sem_gc"](churn))
    M["gc_ligar"]()
    gc.collect()

    assert com["resultado"] == "ok" and sem["resultado"] == "ok"
    assert sem["pausas"] == 0, "com o coletor desligado não há pausa"
    assert sem["total_ms"] <= com["total_ms"]


# ══════════════════════════════════════════════════════════════
#  Arena
# ══════════════════════════════════════════════════════════════

def test_a_arena_entrega_o_que_preparou(M):
    arena = M["arena"](4, lambda: {"usos": 0})
    pegos = [M["pegar"](arena) for _ in range(4)]
    assert len(pegos) == 4
    assert all(isinstance(p, dict) for p in pegos)
    assert M["arena_estatisticas"](arena)["entregues"] == 4


def test_a_arena_reaproveita_em_vez_de_alocar(M):
    """O ponto da arena: o mesmo objeto volta, e não outro igual."""
    arena = M["arena"](2, lambda: {"n": 0})
    a = M["pegar"](arena)
    b = M["pegar"](arena)
    identidades = {id(a), id(b)}

    M["devolver"](arena, a)
    M["devolver"](arena, b)

    c = M["pegar"](arena)
    d = M["pegar"](arena)
    assert {id(c), id(d)} == identidades, "a arena alocou de novo"
    assert M["arena_estatisticas"](arena)["reaproveitados"] == 2


def test_a_arena_cresce_quando_acaba_e_diz_que_cresceu(M):
    """Travar seria pior; crescer calado esconderia o dimensionamento."""
    arena = M["arena"](1, lambda: {"n": 0})
    M["pegar"](arena)
    M["pegar"](arena)
    e = M["arena_estatisticas"](arena)
    assert e["entregues"] == 2
    assert e["criados"] == 2
    assert e["cresceu"] >= 1


def test_limpar_devolve_tudo_de_uma_vez(M):
    """É a operação que a arena existe para ter: soltar o lote inteiro."""
    arena = M["arena"](3, lambda: {"n": 0})
    for _ in range(3):
        M["pegar"](arena)
    assert M["arena_estatisticas"](arena)["em_uso"] == 3
    M["limpar"](arena)
    assert M["arena_estatisticas"](arena)["em_uso"] == 0
    assert M["arena_estatisticas"](arena)["disponiveis"] == 3


def test_devolver_o_que_nao_e_da_arena_e_recusado(M):
    from dataforge.errors import DataForgeError
    arena = M["arena"](1, lambda: {"n": 0})
    with pytest.raises(DataForgeError):
        M["devolver"](arena, {"estranho": True})


# ══════════════════════════════════════════════════════════════
#  Da linguagem
# ══════════════════════════════════════════════════════════════

def test_o_controle_do_coletor_funciona_da_linguagem():
    assert rodar('''
adopt Arcane.Memoria as Mem

out Mem.gc_ligado()

action critico():
    total := 0
    cycle i from 1 to 100:
        total += i
    yield total

// sem coletor no trecho sensivel a latencia — e ele volta depois
out Mem.sem_gc(critico)
out Mem.gc_ligado()
''') == "yes\n5050\nyes\n"


def test_a_arena_funciona_da_linguagem():
    assert rodar('''
adopt Arcane.Memoria as Mem

arena := Mem.arena(2, lambda => {"n": 0})
a := Mem.pegar(arena)
b := Mem.pegar(arena)
Mem.devolver(arena, a)
Mem.devolver(arena, b)
Mem.pegar(arena)

e := Mem.arena_estatisticas(arena)
out e["criados"], e["reaproveitados"], e["em_uso"]
''') == "2 2 1\n"


def test_o_modulo_continua_descrito():
    from dataforge.stdlib.catalogo import DESCRICOES
    assert "Arcane.Memoria" in DESCRICOES
    assert "coletor" in DESCRICOES["Arcane.Memoria"][0].lower()


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
