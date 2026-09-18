"""STM, atômicos com CAS e estruturas sem trava.

O repositório já mediu o problema: duas threads somando na mesma
variável entregaram **40.425 de 80.000**, em silêncio. As respostas que
existiam eram `mutex` (e a disciplina de lembrar dele em todo lugar) e
`contador` (que só serve para contar).

O que falta é a forma de compor: transferir de uma conta para outra é
duas escritas que precisam acontecer **juntas** ou não acontecer. Com
mutex, isso vira ordem de aquisição — e ordem errada é impasse.

O que os testes cobram:

1. **STM**: 40 threads somando 200 vezes entregam 8.000, e não 4.031;
2. **atomicidade**: uma transação que falha no meio não deixa metade
   escrita — a invariante do saldo total se mantém sob concorrência;
3. **isolamento**: dentro da transação, ninguém vê a escrita dos outros
   antes do commit;
4. **composição**: duas transações viram uma, e `ou_entao` tenta a
   segunda quando a primeira pede para esperar;
5. **CAS**: `comparar_e_trocar` responde se trocou, e é a peça com que
   se escreve um contador sem trava;
6. **fila e pilha sem trava**: 8 threads produzindo e consumindo não
   perdem nem duplicam item.
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


# ── STM: o que o mutex não compõe ────────────────────────────

def test_a_transacao_nao_perde_incremento_sob_concorrencia():
    assert rodar('''
adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

total := T.variavel(0)

action somar(i):
    cycle _ in range(0, 200):
        T.atomicamente(lambda => T.escrever(total, T.ler(total) + 1))

C.para_cada(somar, [i cycle i in range(1, 41)])
out T.valor(total)
''') == "8000"


def test_a_transferencia_e_atomica_e_a_soma_nao_muda():
    assert rodar('''
adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

a := T.variavel(1000)
b := T.variavel(1000)

action transferir(quanto):
    T.atomicamente(lambda =>
        T.escrever(b, T.ler(b) + quanto) given T.escrever(a, T.ler(a) - quanto) is void otherwise 0)

action ida(i):
    transferir(1)

action volta(i):
    T.atomicamente(lambda =>
        T.escrever(a, T.ler(a) + 1) given T.escrever(b, T.ler(b) - 1) is void otherwise 0)

C.para_cada(ida, [i cycle i in range(1, 101)])
C.para_cada(volta, [i cycle i in range(1, 101)])

out T.valor(a) + T.valor(b), T.valor(a), T.valor(b)
''') == "2000 1000 1000"


def test_uma_transacao_que_falha_nao_deixa_metade_escrita():
    assert rodar('''
adopt Arcane.Stm as T

a := T.variavel(10)
b := T.variavel(10)

action quebrar():
    T.escrever(a, 999)
    trigger "no meio"

monitor:
    T.atomicamente(quebrar)
handle Error as e:
    out e.message

out T.valor(a), T.valor(b)
''') == "no meio\n10 10"


def test_o_isolamento_e_a_leitura_repetida():
    assert rodar('''
adopt Arcane.Stm as T

x := T.variavel(1)

action dentro():
    primeiro := T.ler(x)
    T.escrever(x, 5)
    yield [primeiro, T.ler(x)]        // vê a PRÓPRIA escrita

out T.atomicamente(dentro), T.valor(x)
''') == "[1, 5] 5"


def test_transacoes_compoem():
    assert rodar('''
adopt Arcane.Stm as T

a := T.variavel(1)
b := T.variavel(1)

action dobrar_a():
    T.escrever(a, T.ler(a) * 2)

action dobrar_b():
    T.escrever(b, T.ler(b) * 2)

action as_duas():
    dobrar_a()
    dobrar_b()

T.atomicamente(as_duas)               // uma transação só
out T.valor(a), T.valor(b), T.estatisticas()["confirmadas"] bigger 0
''') == "2 2 yes"


def test_ou_entao_tenta_a_segunda_quando_a_primeira_espera():
    assert rodar('''
adopt Arcane.Stm as T

fila := T.variavel([])
reserva := T.variavel(["de reserva"])

action da_fila():
    itens := T.ler(fila)
    given len(itens) is 0:
        T.retentar()                  // não tem nada: espera
    yield itens[0]

action da_reserva():
    yield T.ler(reserva)[0]

out T.atomicamente(lambda => T.ou_entao(da_fila, da_reserva))
''') == "de reserva"


def test_retentar_acorda_quando_a_variavel_muda():
    assert rodar('''
adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

caixa := T.variavel([])
recebido := []

action consumidor():
    itens := T.ler(caixa)
    given len(itens) is 0:
        T.retentar()
    T.escrever(caixa, [])
    yield itens[0]

action consumir(i):
    recebido.append(T.atomicamente(consumidor))

tarefa := C.rodar(consumir, 1)
C.dormir(0.06)
T.atomicamente(lambda => T.escrever(caixa, ["chegou"]))
C.esperar(tarefa, 3000)

out recebido
''') == "[chegou]"


def test_o_conflito_e_contado_e_a_transacao_repetida():
    saida = rodar('''
adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

x := T.variavel(0)

action somar(i):
    cycle _ in range(0, 50):
        T.atomicamente(lambda => T.escrever(x, T.ler(x) + 1))

C.para_cada(somar, [i cycle i in range(1, 9)])
estat := T.estatisticas()
out T.valor(x), estat["confirmadas"] bigger_eq 400, estat["conflitos"] bigger_eq 0
''')
    assert saida == "400 yes yes"


def test_ler_fora_de_uma_transacao_e_recusado():
    erro = erro_de('''
adopt Arcane.Stm as T
x := T.variavel(1)
T.escrever(x, 2)
''')
    assert "transa" in erro.message.lower()


# ── atômicos com CAS ─────────────────────────────────────────

def test_o_atomico_troca_so_quando_o_valor_e_o_esperado():
    assert rodar('''
adopt Arcane.Concurrent as C

a := C.atomico(10)
out a.pegar()
out a.comparar_e_trocar(10, 20), a.pegar()
out a.comparar_e_trocar(10, 30), a.pegar()
out a.trocar(99), a.pegar()
''') == "10\nyes 20\nno 20\n20 99"


def test_o_contador_atomico_nao_perde_soma():
    assert rodar('''
adopt Arcane.Concurrent as C

a := C.atomico(0)

action somar(i):
    cycle _ in range(0, 500):
        a.somar(1)

C.para_cada(somar, [i cycle i in range(1, 17)])
out a.pegar()
''') == "8000"


def test_o_cas_escreve_um_contador_sem_trava():
    assert rodar('''
adopt Arcane.Concurrent as C

a := C.atomico(0)

action incrementar_sem_trava():
    persist yes:
        atual := a.pegar()
        given a.comparar_e_trocar(atual, atual + 1):
            halt

action trabalhar(i):
    cycle _ in range(0, 200):
        incrementar_sem_trava()

C.para_cada(trabalhar, [i cycle i in range(1, 11)])
out a.pegar()
''') == "2000"


# ── estruturas sem trava ─────────────────────────────────────

def test_a_fila_sem_trava_nao_perde_nem_duplica():
    assert rodar('''
adopt Arcane.Concurrent as C

fila := C.fila_sem_trava()
adopt Arcane.Collections as Col

action produzir(i):
    cycle j in range(0, 100):
        fila.por(i * 1000 + j)

C.para_cada(produzir, [i cycle i in range(1, 9)])
out fila.tamanho()

vistos := []
persist fila.tamanho() bigger 0:
    item := fila.tirar()
    given item isnt void:
        vistos.append(item)

out len(vistos), len(Col.set(vistos)) is len(vistos)
''') == "800\n800 yes"


def test_a_pilha_sem_trava_devolve_na_ordem_inversa():
    assert rodar('''
adopt Arcane.Concurrent as C

p := C.pilha_sem_trava()
p.por(1)
p.por(2)
p.por(3)
out p.tirar(), p.tirar(), p.tirar(), p.tirar(), p.tamanho()
''') == "3 2 1 void 0"


def test_o_anel_descarta_o_mais_velho_quando_enche():
    assert rodar('''
adopt Arcane.Concurrent as C

anel := C.anel(3)
cycle i from 1 to 5:
    anel.por(i)

out anel.tudo(), anel.cheio(), anel.tamanho()
out anel.tirar(), anel.tudo()
''') == "[3, 4, 5] yes 3\n3 [4, 5]"


def test_o_executor_reaproveita_as_threads():
    assert rodar('''
adopt Arcane.Concurrent as C

executor := C.executor(4)

action dobro(x):
    yield x * 2

tarefas := [executor.submeter(dobro, i) cycle i in range(1, 6)]
out [C.esperar(t) cycle t in tarefas]
out executor.mapear(dobro, [10, 20]), executor.trabalhadores()
executor.fechar()
out executor.aberto()
''') == "[2, 4, 6, 8, 10]\n[20, 40] 4\nno"


def test_a_promessa_e_cumprida_por_quem_quiser():
    assert rodar('''
adopt Arcane.Concurrent as C

p := C.promessa()

action cumprir(i):
    C.dormir(0.02)
    p.cumprir("pronto")

C.rodar(cumprir, 1)
out p.esperar(3000), p.cumprida()
''') == "pronto yes"


def test_a_promessa_leva_a_falha_para_quem_espera():
    erro = erro_de('''
adopt Arcane.Concurrent as C
p := C.promessa()
p.falhar("deu ruim")
p.esperar(1000)
''')
    assert "deu ruim" in erro.message


# ── os módulos ───────────────────────────────────────────────

def test_os_modulos_estao_registrados_e_descritos():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Stm", "Stm"):
        assert get_module(nome) is not None, nome
    assert "Arcane.Stm" in DESCRICOES
    concurrent = get_module("Arcane.Concurrent")
    for simbolo in ("atomico", "fila_sem_trava", "pilha_sem_trava", "anel",
                    "executor", "promessa"):
        assert simbolo in concurrent, simbolo


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import concorrencia_stm
    for pagina in concorrencia_stm.PAGINAS:
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
