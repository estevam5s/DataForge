"""O que roda antes da primeira linha, e a fronteira de capacidade.

**Parte 13 — bootstrapping.** Um programa não começa na primeira linha:
antes dela o `comptime` rodou, os `adopt` carregaram e as declarações
foram içadas. Nada disso era **visível**, e "por que a partida demora
400 ms?" não tinha como ser respondido sem cronometrar à mão.

Mais duas peças que faltavam de verdade:

* **armazenamento por thread**, com inicialização por thread e
  finalizador — `threading.local` dá o armazém e não dá o resto;
* **a pilha**, que tinha limite e não tinha como ser perguntada.

**Parte 15 — `unsafe` e capacidade.** O `comptime` já recusava `out`,
`adopt` e `thread`: é uma fronteira de capacidade, escrita à mão, para
um caso só. `Arcane.Capacidade` generaliza — e a honestidade importa mais que
o mecanismo: **capacidade é o que o código pode ALCANÇAR, não o que lhe
foi entregue**. Um cofre que prometesse conter um programa hostil
mentiria, e o teste que prova o limite está aqui.
"""

import io
import os
import subprocess
import sys
import threading
import time
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                    # noqa: E402
from dataforge.interpreter import Interpreter                  # noqa: E402
from dataforge.lexer import tokenize                           # noqa: E402
from dataforge.parser import parse                             # noqa: E402
from dataforge.stdlib import get_module                        # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue()


def erro_de(fonte):
    try:
        rodar(fonte)
    except DataForgeError as erro:
        return erro
    raise AssertionError("era para dar erro, e rodou")


@pytest.fixture
def I():
    return get_module("Arcane.Inicio")


@pytest.fixture
def C():
    return get_module("Arcane.Capacidade")


# ══════════════════════════════════════════════════════════════
#  Parte 13 — a partida
# ══════════════════════════════════════════════════════════════

def test_as_fases_da_partida_estao_nomeadas_e_em_ordem(I):
    fases = I["fases"]()
    assert len(fases) >= 5
    nomes = [f["fase"] for f in fases]
    assert nomes.index("lexer") < nomes.index("parser")
    assert nomes.index("parser") < nomes.index("comptime")
    assert nomes.index("comptime") < nomes.index("programa")
    for f in fases:
        assert len(f["o_que"]) > 20, f


def test_a_partida_e_cronometrada_por_modulo_adotado():
    """"Por que a partida demora?" sem cronometrar à mão."""
    saida = rodar('''
adopt Arcane.Math as M
adopt Arcane.Text as T
adopt Arcane.Inicio as I

registro := I.adocoes()
out len(registro) bigger_eq 3
out "modulo" in registro[0] and "ms" in registro[0]
''')
    assert saida == "yes\nyes\n"


def test_o_relatorio_da_partida_soma_o_tempo():
    saida = rodar('''
adopt Arcane.Math as M
adopt Arcane.Inicio as I

r := I.relatorio()
out r["adocoes"] bigger_eq 2
out r["total_ms"] bigger_eq 0.0
out "mais_caro" in r
''')
    assert saida == "yes\nyes\nyes\n"


# ── armazenamento por thread ──────────────────────────────────

def test_cada_thread_ve_o_proprio_valor(I):
    local = I["local"](lambda: {"conta": 0})
    vistos = {}

    def trabalhar(qual):
        caixa = I["meu"](local)
        caixa["conta"] += qual
        time.sleep(0.01)
        vistos[qual] = I["meu"](local)["conta"]

    fios = [threading.Thread(target=trabalhar, args=(n,)) for n in (1, 2, 3)]
    for f in fios:
        f.start()
    for f in fios:
        f.join()
    assert vistos == {1: 1, 2: 2, 3: 3}, \
        "uma thread viu o valor de outra"


def test_a_inicializacao_roda_uma_vez_por_thread(I):
    contagem = {"n": 0}

    def nascer():
        contagem["n"] += 1
        return {"id": contagem["n"]}

    local = I["local"](nascer)
    for _ in range(4):
        I["meu"](local)          # mesma thread: uma só inicialização
    assert contagem["n"] == 1

    def outra():
        I["meu"](local)

    fio = threading.Thread(target=outra)
    fio.start()
    fio.join()
    assert contagem["n"] == 2


def test_o_valor_pode_ser_trocado_e_limpo(I):
    local = I["local"](lambda: 0)
    I["definir"](local, 7)
    assert I["meu"](local) == 7
    I["limpar"](local)
    assert I["meu"](local) == 0, "depois de limpar, nasce de novo"


def test_o_finalizador_de_thread_e_chamado(I):
    """`threading.local` dá o armazém e não dá o fim."""
    mortos = []
    local = I["local"](lambda: {"n": 1},
                       ao_terminar=lambda v: mortos.append(v["n"]))

    def trabalhar():
        I["meu"](local)

    fio = threading.Thread(target=trabalhar)
    fio.start()
    fio.join()
    del fio
    import gc
    for _ in range(3):
        gc.collect()
    assert mortos == [1], "o finalizador não rodou quando a thread saiu"


def test_quantas_threads_tem_valor(I):
    local = I["local"](lambda: 1)
    I["meu"](local)
    assert I["threads_com_valor"](local) >= 1


# ── a pilha ───────────────────────────────────────────────────

def test_a_pilha_se_pergunta():
    saida = rodar('''
adopt Arcane.Inicio as I

action fundo():
    yield I.pilha()

action meio():
    yield fundo()

p := meio()
out p["profundidade"] bigger_eq 2
out p["limite"] bigger 100
out p["restante"] is p["limite"] - p["profundidade"]
''')
    assert saida == "yes\nyes\nyes\n"


def test_os_quadros_trazem_os_nomes():
    saida = rodar('''
adopt Arcane.Inicio as I

action folha():
    yield [q["acao"] cycle q in I.quadros()]

action tronco():
    yield folha()

nomes := tronco()
out "folha" in nomes, "tronco" in nomes
''')
    assert saida == "yes yes\n"


def test_o_limite_da_pilha_se_ajusta_e_volta():
    saida = rodar('''
adopt Arcane.Inicio as I

antes := I.pilha()["limite"]
I.limite_da_pilha(300)
out I.pilha()["limite"]
I.limite_da_pilha(antes)
out I.pilha()["limite"] is antes
''')
    assert saida == "300\nyes\n"


def test_um_limite_absurdo_e_recusado_com_o_motivo(I):
    erro = erro_de('''
adopt Arcane.Inicio as I
I.limite_da_pilha(10000000)
''')
    assert "recursion" in erro.message.lower() or "Python" in erro.message


def test_o_limite_baixado_vale_de_verdade():
    """Sem isso o ajuste seria decoração."""
    erro = erro_de('''
adopt Arcane.Inicio as I
I.limite_da_pilha(40)

action fundo(n):
    yield fundo(n + 1) given n smaller 500 otherwise n

fundo(0)
''')
    assert "profund" in erro.message.lower() or "deep" in erro.message.lower() \
        or "stack" in erro.message.lower()


# ══════════════════════════════════════════════════════════════
#  Parte 15 — a fronteira de capacidade
# ══════════════════════════════════════════════════════════════

def test_as_capacidades_estao_nomeadas_e_descritas(C):
    capacidades = C["capacidades"]()
    for nome in ("arquivos", "rede", "processo", "nativo", "python",
                 "ambiente"):
        assert nome in capacidades, nome
        assert len(capacidades[nome]) > 20, nome


def test_sem_permissao_o_adopt_e_recusado_com_o_nome_dela():
    erro = erro_de('''
adopt Arcane.Capacidade as Cap

action ler_disco():
    adopt Arcane.IO as IO
    yield IO.exists(".")

Cap.executar(ler_disco, [])
''')
    assert "arquivos" in erro.message
    assert "Arcane.IO" in erro.message


def test_com_permissao_o_mesmo_adopt_passa():
    assert rodar('''
adopt Arcane.Capacidade as Cap

action ler_disco():
    adopt Arcane.IO as IO
    yield IO.exists(".")

out Cap.executar(ler_disco, ["arquivos"])
''') == "yes\n"


def test_a_ponte_para_o_python_exige_permissao_propria():
    erro = erro_de('''
adopt Arcane.Capacidade as Cap

action escapar():
    adopt Python.os as os
    yield os.getcwd()

Cap.executar(escapar, ["arquivos", "rede", "processo"])
''')
    assert "python" in erro.message.lower()


def test_o_que_e_puro_roda_sem_permissao_nenhuma():
    assert rodar('''
adopt Arcane.Capacidade as Cap

action contas():
    adopt Arcane.Math as M
    yield M.sqrt(16) + len("abc")

out Cap.executar(contas, [])
''') == "7.0\n"


def test_a_fronteira_volta_ao_normal_depois(C):
    """Uma fronteira que não se desfaz trava o programa inteiro."""
    assert rodar('''
adopt Arcane.Capacidade as Cap

action nada():
    yield 1

Cap.executar(nada, [])

// fora da fronteira, o adopt volta a funcionar
adopt Arcane.IO as IO
out IO.exists(".")
''') == "yes\n"


def test_a_fronteira_se_desfaz_mesmo_quando_o_corpo_falha():
    assert rodar('''
adopt Arcane.Capacidade as Cap

action quebra():
    yield 1 / 0     // df: permitir division-by-zero

monitor:
    Cap.executar(quebra, [])
handle Error:
    out "capturado"

adopt Arcane.IO as IO
out IO.exists(".")
''') == "capturado\nyes\n"


def test_uma_capacidade_inventada_e_recusada_com_a_lista():
    erro = erro_de('''
adopt Arcane.Capacidade as Cap

action nada():
    yield 1

Cap.executar(nada, ["superpoderes"])
''')
    assert "superpoderes" in erro.message
    assert "arquivos" in erro.message or "rede" in erro.message


def test_o_relatorio_diz_o_que_foi_pedido_e_negado(C):
    saida = rodar('''
adopt Arcane.Capacidade as Cap

action tenta():
    monitor:
        adopt Arcane.OS as OS
        yield OS.name()
    handle Error:
        yield "negado"

r := Cap.observar(tenta, [])
out r["resultado"], len(r["negados"]) bigger 0, r["negados"][0]["capacidade"]
''')
    assert saida == "negado yes processo\n"


def test_a_fronteira_nao_tira_o_que_foi_ENTREGUE(C):
    """O limite honesto, e ele é o modelo — não um defeito.

    Capacidade é o que o código pode **alcançar**, e não o que lhe foi
    passado. Um cofre que prometesse o contrário mentiria: quem entrega
    o módulo entrega o poder junto.
    """
    assert rodar('''
adopt Arcane.Capacidade as Cap
adopt Arcane.IO as IO

// IO foi ENTREGUE por quem chamou: a fronteira nao o retira
action com_o_que_recebeu(ferramenta):
    yield ferramenta.exists(".")

out Cap.executar(com_o_que_recebeu, [], [IO])
''') == "yes\n"


def test_o_modulo_diz_na_cara_que_nao_e_sandbox(C):
    """Se a documentação prometesse contenção, o teste seria uma mentira."""
    aviso = C["limites"]()
    assert isinstance(aviso, list) and len(aviso) >= 3
    inteiro = " ".join(aviso).lower()
    assert "não é" in inteiro or "nao e" in inteiro
    assert "hostil" in inteiro or "malicioso" in inteiro


def test_os_modulos_estao_registrados_e_descritos():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Inicio", "Inicio", "Arcane.Capacidade", "Capacidade"):
        assert get_module(nome) is not None, nome
    for nome in ("Arcane.Inicio", "Arcane.Capacidade"):
        assert nome in DESCRICOES


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import partida_e_seguranca
    for pagina in partida_e_seguranca.PAGINAS:
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
