"""O laço de eventos, o escalonador e as fibras — com o número medido.

O `async/await` da linguagem é **thread por tarefa**: serve para sobrepor
entrada e saída, e não escala. Mil conexões simultâneas são mil threads
do sistema, e a conta aparece na memória e no escalonador do SO antes de
aparecer no programa.

A parte 12 de uma referência Deep Tech pede o outro modelo: um laço de
eventos, um escalonador cooperativo e fibras. O que os testes cobram:

1. **O laço é um reator de verdade** — ele dorme no `selectors` (epoll,
   kqueue ou select, conforme o sistema) até haver o que fazer. Há teste
   provando que ele **não gira em vão**: com um temporizador a 200 ms, o
   número de voltas tem de ser pequeno.
2. **O escalonador** — ordem, prazo, cancelamento, contrapressão, e um
   erro num retorno de chamada que não derruba o laço.
3. **As fibras são reais.** Um `stream action` da linguagem já é um
   gerador Python que suspende em cada `emit`: é esse o ponto de parada,
   e a troca de contexto é o quadro do gerador. Não é aproximação — e a
   limitação (um `emit` dentro de uma ação chamada **não** suspende) é a
   de toda corrotina sem pilha, e está documentada com esse nome.
4. **O número.** N conexões simultâneas atendidas por **uma** thread,
   comparado com uma thread por conexão. Sem essa medida, o laço seria
   só mais um jeito de escrever a mesma coisa.
"""

import io
import os
import socket
import subprocess
import sys
import threading
import time
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
def L():
    return get_module("Arcane.Laco")


# ══════════════════════════════════════════════════════════════
#  O laço
# ══════════════════════════════════════════════════════════════

def test_o_laco_roda_e_para_sozinho_quando_nao_ha_mais_nada(L):
    laco = L["novo"]()
    visto = []
    L["agendar"](laco, lambda: visto.append("a"))
    L["agendar"](laco, lambda: visto.append("b"))
    L["rodar"](laco)
    assert visto == ["a", "b"]


def test_a_ordem_da_fila_e_a_da_chegada(L):
    laco = L["novo"]()
    visto = []
    for i in range(5):
        L["agendar"](laco, (lambda n: lambda: visto.append(n))(i))
    L["rodar"](laco)
    assert visto == [0, 1, 2, 3, 4]


def test_o_temporizador_espera_de_verdade(L):
    laco = L["novo"]()
    marca = []
    inicio = time.perf_counter()
    L["apos"](laco, 60, lambda: marca.append(time.perf_counter() - inicio))
    L["rodar"](laco)
    assert len(marca) == 1
    assert marca[0] >= 0.05, f"disparou cedo demais: {marca[0]:.3f}s"


def test_os_temporizadores_disparam_em_ordem_de_prazo(L):
    """Quem foi agendado depois, mas para antes, roda antes."""
    laco = L["novo"]()
    ordem = []
    L["apos"](laco, 80, lambda: ordem.append("tarde"))
    L["apos"](laco, 10, lambda: ordem.append("cedo"))
    L["apos"](laco, 40, lambda: ordem.append("meio"))
    L["rodar"](laco)
    assert ordem == ["cedo", "meio", "tarde"]


def test_o_laco_nao_gira_em_vao(L):
    """A diferença entre um reator e um laço de espera ocupada.

    Com um único temporizador a 200 ms, um laço que dorme no seletor dá
    **poucas** voltas. Um que faz espera ocupada dá milhões — e queima
    um núcleo sem fazer nada.
    """
    laco = L["novo"]()
    L["apos"](laco, 200, lambda: None)
    L["rodar"](laco)
    voltas = L["estatisticas"](laco)["voltas"]
    assert voltas < 50, (
        f"{voltas} voltas para esperar 200 ms: isto é espera ocupada, "
        f"não um laço de eventos")


def test_o_repetidor_repete_e_se_cancela(L):
    laco = L["novo"]()
    contagem = {"n": 0}

    def tique():
        contagem["n"] += 1
        if contagem["n"] >= 3:
            L["parar"](laco)

    L["a_cada"](laco, 5, tique)
    L["rodar"](laco)
    assert contagem["n"] == 3


def test_uma_tarefa_cancelada_nao_roda(L):
    laco = L["novo"]()
    visto = []
    tarefa = L["apos"](laco, 10, lambda: visto.append("nao devia"))
    L["cancelar"](tarefa)
    L["apos"](laco, 30, lambda: visto.append("esta sim"))
    L["rodar"](laco)
    assert visto == ["esta sim"]
    assert L["cancelada"](tarefa)


def test_um_erro_num_retorno_de_chamada_nao_derruba_o_laco(L):
    """Um laço que morre no primeiro erro derruba o servidor inteiro."""
    laco = L["novo"]()
    visto = []

    def explode():
        raise ValueError("de propósito")

    L["agendar"](laco, explode)
    L["agendar"](laco, lambda: visto.append("continuei"))
    L["rodar"](laco)
    assert visto == ["continuei"]
    assert L["estatisticas"](laco)["erros"] == 1


def test_os_erros_ficam_guardados_e_nomeados(L):
    laco = L["novo"]()
    L["agendar"](laco, lambda: 1 / 0)
    L["rodar"](laco)
    falhas = L["falhas"](laco)
    assert len(falhas) == 1
    assert "zero" in falhas[0]["erro"].lower() or "division" in falhas[0]["erro"].lower()


def test_o_mecanismo_e_o_do_sistema(L):
    laco = L["novo"]()
    assert L["mecanismo"](laco) in ("epoll", "kqueue", "devpoll", "poll",
                                    "select")


# ══════════════════════════════════════════════════════════════
#  Entrada e saída
# ══════════════════════════════════════════════════════════════

def test_o_laco_acorda_quando_o_soquete_tem_dado(L):
    a, b = socket.socketpair()
    a.setblocking(False)
    laco = L["novo"]()
    recebido = []

    def ao_ler(soquete):
        recebido.append(soquete.recv(64))
        L["parar"](laco)

    L["quando_ler"](laco, a, ao_ler)
    L["apos"](laco, 10, lambda: b.sendall(b"ola"))
    L["rodar"](laco)
    a.close()
    b.close()
    assert recebido == [b"ola"]


def test_esquecer_tira_o_soquete_do_laco(L):
    a, b = socket.socketpair()
    a.setblocking(False)
    laco = L["novo"]()
    visto = []
    L["quando_ler"](laco, a, lambda s: visto.append(s.recv(64)))
    L["esquecer"](laco, a)
    L["apos"](laco, 10, lambda: b.sendall(b"ola"))
    L["apos"](laco, 40, lambda: L["parar"](laco))
    L["rodar"](laco)
    a.close()
    b.close()
    assert visto == []


def test_o_trabalho_bloqueante_vai_para_o_pool_e_o_laco_continua(L):
    """Um `sleep` dentro do laço trava tudo. `executar` existe por isso."""
    laco = L["novo"]()
    marcas = []

    def pesado():
        time.sleep(0.08)
        return "pronto"

    L["executar"](laco, pesado, lambda r: marcas.append(r))
    for i in range(4):
        L["apos"](laco, 10 * (i + 1), lambda: marcas.append("tique"))
    L["rodar"](laco)
    assert marcas.count("tique") == 4
    assert "pronto" in marcas
    # os tiques rodaram ENQUANTO o trabalho pesado corria
    assert marcas.index("tique") < marcas.index("pronto")


def test_agendar_de_outra_thread_acorda_o_laco(L):
    """Sem o truque do autocano, o laço dorme no seletor e ninguém o acorda."""
    laco = L["novo"]()
    visto = []

    def de_fora():
        time.sleep(0.03)
        L["agendar"](laco, lambda: visto.append("de outra thread"))
        L["agendar"](laco, lambda: L["parar"](laco))

    threading.Thread(target=de_fora, daemon=True).start()

    # A prova não é o relógio — um limite fixo mediria a máquina. É a
    # REDE DE SEGURANÇA: se o laço só parar por causa dela, é porque
    # dormiu no seletor e ninguém o acordou.
    socorro = {"usado": False}

    def rede_de_seguranca():
        socorro["usado"] = True
        L["parar"](laco)

    L["apos"](laco, 5000, rede_de_seguranca)
    L["rodar"](laco)
    assert visto == ["de outra thread"]
    assert not socorro["usado"], (
        "o laço só parou pela rede de segurança: ele dormiu no seletor "
        "e o 'agendar' de outra thread não o acordou")


# ══════════════════════════════════════════════════════════════
#  Contrapressão
# ══════════════════════════════════════════════════════════════

def test_o_teto_da_fila_recusa_em_vez_de_crescer_sem_limite(L):
    """Uma fila sem teto troca falha por travamento e morte por memória."""
    laco = L["novo"](2)
    assert L["agendar"](laco, lambda: None)
    assert L["agendar"](laco, lambda: None)
    assert not L["agendar"](laco, lambda: None), "a terceira devia ser recusada"
    assert L["estatisticas"](laco)["recusadas"] == 1


def test_sem_teto_a_fila_aceita_o_que_vier(L):
    laco = L["novo"]()
    for _ in range(500):
        assert L["agendar"](laco, lambda: None)
    L["rodar"](laco)
    assert L["estatisticas"](laco)["tarefas"] == 500


# ══════════════════════════════════════════════════════════════
#  Fibras — §56
# ══════════════════════════════════════════════════════════════

def test_a_fibra_para_em_cada_emit_e_retoma(L):
    assert rodar('''
adopt Arcane.Laco as L

stream action trabalhador(nome):
    out $"{nome}: um"
    emit L.dormir(5)
    out $"{nome}: dois"
    emit L.dormir(5)
    out $"{nome}: tres"

laco := L.novo()
L.fibra(laco, trabalhador, ["A"])
L.rodar(laco)
''') == "A: um\nA: dois\nA: tres\n"


def test_duas_fibras_se_intercalam(L):
    """É o que prova que o escalonamento é cooperativo, e não sequencial."""
    saida = rodar('''
adopt Arcane.Laco as L

stream action trabalhador(nome):
    cycle i from 1 to 3:
        out $"{nome}{i}"
        emit L.ceder()

laco := L.novo()
L.fibra(laco, trabalhador, ["A"])
L.fibra(laco, trabalhador, ["B"])
L.rodar(laco)
''')
    assert saida == "A1\nB1\nA2\nB2\nA3\nB3\n", saida


def test_a_fibra_que_dorme_deixa_a_outra_andar(L):
    saida = rodar('''
adopt Arcane.Laco as L

stream action lenta():
    out "lenta: comecei"
    emit L.dormir(60)
    out "lenta: terminei"

stream action rapida():
    cycle i from 1 to 3:
        out $"rapida {i}"
        emit L.dormir(5)

laco := L.novo()
L.fibra(laco, lenta, [])
L.fibra(laco, rapida, [])
L.rodar(laco)
''')
    linhas = saida.strip().split("\n")
    assert linhas[0] == "lenta: comecei"
    assert linhas[-1] == "lenta: terminei"
    assert linhas.count("rapida 1") == 1


def test_a_conta_de_fibras_vivas(L):
    assert rodar('''
adopt Arcane.Laco as L

stream action dorme():
    emit L.dormir(20)

laco := L.novo()
L.fibra(laco, dorme, [])
L.fibra(laco, dorme, [])
out L.fibras(laco)
L.rodar(laco)
out L.fibras(laco)
''') == "2\n0\n"


def test_a_fibra_pode_ser_cancelada(L):
    assert rodar('''
adopt Arcane.Laco as L

stream action longa():
    out "comecei"
    emit L.dormir(30)
    out "NAO DEVIA CHEGAR AQUI"

laco := L.novo()
f := L.fibra(laco, longa, [])
L.apos(laco, 5, lambda => L.cancelar(f))
L.rodar(laco)
out "fim"
''') == "comecei\nfim\n"


def test_um_erro_dentro_da_fibra_nao_derruba_o_laco(L):
    saida = rodar('''
adopt Arcane.Laco as L

stream action quebra():
    out "antes"
    emit L.ceder()
    x := 1 / 0
    emit L.ceder()

stream action segue():
    emit L.ceder()
    out "a outra seguiu"

laco := L.novo()
L.fibra(laco, quebra, [])
L.fibra(laco, segue, [])
L.rodar(laco)
out len(L.falhas(laco))
''')
    assert "a outra seguiu" in saida
    assert saida.strip().endswith("1")


def test_a_fibra_recebe_o_que_o_laco_pos_na_caixa(L):
    """Um `emit` não devolve valor: o laço entrega pela caixa.

    É a consequência de a corrotina ser **sem pilha** — e a forma
    explícita é melhor que fingir que `emit` é uma expressão.
    """
    assert rodar('''
adopt Arcane.Laco as L

stream action espera(caixa):
    emit L.depois_de(30, caixa, "resposta")
    out caixa["resposta"]

laco := L.novo()
caixa := {"resposta": void}
L.fibra(laco, espera, [caixa])
L.rodar(laco)
''') == "pronto\n"


# ══════════════════════════════════════════════════════════════
#  O número: N conexões, UMA thread
# ══════════════════════════════════════════════════════════════

def test_uma_thread_atende_muitas_conexoes_ao_mesmo_tempo(L):
    """O que o laço existe para fazer, e a prova de que ele faz.

    Cento e vinte conexões abertas ao mesmo tempo, atendidas por **uma**
    thread. Com `thread por pedido` seriam cento e vinte threads do
    sistema — e o Kiln faz exatamente isso.
    """
    QUANTAS = 120
    laco = L["novo"]()
    ouvinte = socket.socket()
    ouvinte.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ouvinte.bind(("127.0.0.1", 0))
    ouvinte.listen(256)
    ouvinte.setblocking(False)
    porta = ouvinte.getsockname()[1]

    atendidas = {"n": 0}
    threads_usadas = set()

    def ao_conectar(servidor):
        cliente, _ = servidor.accept()
        cliente.setblocking(False)

        def ao_ler(soquete):
            dado = soquete.recv(256)
            threads_usadas.add(threading.get_ident())
            if not dado:
                L["esquecer"](laco, soquete)
                soquete.close()
                return
            soquete.sendall(dado.upper())
            atendidas["n"] += 1
            if atendidas["n"] >= QUANTAS:
                L["parar"](laco)

        L["quando_ler"](laco, cliente, ao_ler)

    L["quando_ler"](laco, ouvinte, ao_conectar)

    clientes = []
    for _ in range(QUANTAS):
        c = socket.create_connection(("127.0.0.1", porta))
        c.sendall(b"ola")
        clientes.append(c)

    L["apos"](laco, 8000, lambda: L["parar"](laco))
    inicio = time.perf_counter()
    L["rodar"](laco)
    gasto = time.perf_counter() - inicio

    respostas = []
    for c in clientes:
        c.settimeout(2)
        try:
            respostas.append(c.recv(256))
        except OSError:
            respostas.append(None)
        c.close()
    ouvinte.close()

    assert atendidas["n"] == QUANTAS, f"atendeu {atendidas['n']} de {QUANTAS}"
    assert respostas.count(b"OLA") == QUANTAS
    assert len(threads_usadas) == 1, (
        f"{len(threads_usadas)} threads atenderam — o laço devia usar uma")
    assert gasto < 5.0, f"{gasto:.1f}s para {QUANTAS} conexões"


def test_as_estatisticas_dizem_o_que_aconteceu(L):
    laco = L["novo"]()
    L["agendar"](laco, lambda: None)
    L["apos"](laco, 5, lambda: None)
    L["rodar"](laco)
    e = L["estatisticas"](laco)
    for chave in ("voltas", "tarefas", "temporizadores", "es", "erros",
                  "recusadas", "fibras", "maior_atraso_ms"):
        assert chave in e, chave
    assert e["tarefas"] >= 1
    assert e["temporizadores"] >= 1


# ══════════════════════════════════════════════════════════════
#  O módulo, a doc e o repositório
# ══════════════════════════════════════════════════════════════

def test_o_modulo_esta_registrado_e_descrito():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Laco", "Laco"):
        assert get_module(nome) is not None, nome
    assert "Arcane.Laco" in DESCRICOES


def test_o_laco_nao_usa_asyncio():
    """O escalonador é o ponto da parte; herdá-lo seria não a ter feito.

    E há um motivo prático: uma ação DataForge não é uma corrotina do
    Python, então o `await` do asyncio não a alcança. O ponto de parada
    aqui é o `emit` de um `stream action`.
    """
    fonte = open(os.path.join(RAIZ, "dataforge", "stdlib", "arcane_laco.py"),
                 encoding="utf-8").read()
    assert "import asyncio" not in fonte
    assert "selectors" in fonte, "o poller tem de ser o do sistema"


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import runtime_laco
    for pagina in runtime_laco.PAGINAS:
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
