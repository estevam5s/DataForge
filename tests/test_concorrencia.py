"""Threads, processos e sincronizacao.

Bug de concorrencia nao aparece numa execucao: ele aparece na
milesima, sob carga, no servidor de producao. Por isso os testes aqui
FORCAM a corrida — muitas threads sobre o mesmo dado — em vez de
conferir que a chamada nao estourou.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import ConcurrencyError, TimeoutError_  # noqa: E402
from dataforge.stdlib.arcane_paralelo import ArcaneConcurrent  # noqa: E402

P = ArcaneConcurrent()


# ═══ Paralelismo de verdade ════════════════════════════════

def test_map_roda_junto_e_nao_em_serie():
    """Se rodasse em serie, cinco esperas de 60ms levariam 300ms."""
    inicio = time.perf_counter()
    r = P["map"](lambda x: (time.sleep(0.06), x * 2)[1], range(5), 5)
    levou = time.perf_counter() - inicio

    assert r == [0, 2, 4, 6, 8]
    assert levou < 0.20, f"levou {levou:.2f}s — parece serie"


def test_map_preserva_a_ordem_da_entrada():
    """Fora de ordem, quem chama tem de reassociar item e resultado —
    e e ai que se erra."""
    # O primeiro demora mais: sem garantia de ordem, ele sairia por último.
    def acao(x):
        time.sleep(0.05 if x == 0 else 0.01)
        return x
    assert P["map"](acao, range(6), 6) == [0, 1, 2, 3, 4, 5]


def test_map_com_lista_vazia():
    assert P["map"](lambda x: x, []) == []


def test_erro_dentro_da_thread_sobe():
    """Sem isto, a excecao morre na thread e o programa segue como se
    tudo tivesse dado certo — o modo mais silencioso de perder dado."""
    def explode(x):
        if x == 2:
            raise ValueError("estourou no 2")
        return x

    with pytest.raises(ValueError, match="estourou no 2"):
        P["map"](explode, range(5), 5)


# ═══ Sincronizacao ═════════════════════════════════════════

def test_contador_nao_perde_atualizacao():
    """'x := x + 1' em duas threads perde somas: as duas leem o mesmo
    valor antes de qualquer uma gravar."""
    c = P["contador"](0)
    P["map"](lambda _: c.somar(), range(2000), 16)
    assert c.valor() == 2000


def test_sem_trava_a_conta_erra():
    """A prova de que a trava e necessaria, e nao decoracao."""
    estado = {"n": 0}

    def somar_sem_trava(_):
        for _ in range(200):
            atual = estado["n"]
            time.sleep(0)          # força a troca de thread
            estado["n"] = atual + 1

    P["map"](somar_sem_trava, range(8), 8)
    # Não afirmamos que ERROU — a corrida é probabilística. Afirmamos
    # que nunca passa do certo, e que a versão com trava acerta sempre.
    assert estado["n"] <= 1600

    c = P["contador"](0)

    def somar_com_trava(_):
        for _ in range(200):
            c.somar()

    P["map"](somar_com_trava, range(8), 8)
    assert c.valor() == 1600


def test_com_trava_solta_mesmo_com_erro():
    """Tomar e soltar a mao funciona ate o corpo estourar: aí a trava
    fica tomada para sempre."""
    trava = P["mutex"]()

    with pytest.raises(ValueError):
        P["com_trava"](trava, lambda: (_ for _ in ()).throw(ValueError("x")))

    # Se ela tivesse ficado tomada, isto travaria para sempre.
    assert P["com_trava"](trava, lambda: "passou") == "passou"


def test_mutex_e_reentrante():
    """A nao reentrante trava quando uma acao com trava chama outra
    com a MESMA trava — e isso acontece por engano com facilidade."""
    trava = P["mutex"]()
    assert P["com_trava"](trava,
                          lambda: P["com_trava"](trava, lambda: "ok")) == "ok"


def test_semaforo_limita_quantos_passam():
    juntos = P["contador"](0)
    pico = P["contador"](0)
    limite = P["semaforo"](3)

    def tarefa(_):
        limite.acquire()
        try:
            n = juntos.somar()
            if n > pico.valor():
                pico.zerar()
                pico.somar(n)
            time.sleep(0.01)
        finally:
            juntos.subtrair()
            limite.release()

    P["map"](tarefa, range(20), 20)
    assert pico.valor() <= 3, f"passaram {pico.valor()} juntos, com limite 3"


def test_barreira_libera_todas_juntas():
    barreira = P["barreira"](4)
    chegadas = P["contador"](0)

    def tarefa(_):
        chegadas.somar()
        barreira.wait(timeout=3)
        # Depois da barreira, todas as quatro já chegaram.
        return chegadas.valor()

    assert P["map"](tarefa, range(4), 4) == [4, 4, 4, 4]


def test_trava_de_leitura_deixa_ler_junto():
    """Muitos leitores ao mesmo tempo; um mutex comum os serializaria."""
    trava = P["trava_leitura_escrita"]()
    juntos = P["contador"](0)
    pico = P["contador"](0)

    def ler(_):
        def corpo():
            n = juntos.somar()
            if n > pico.valor():
                pico.zerar()
                pico.somar(n)
            time.sleep(0.02)
            juntos.subtrair()
            return n
        return trava.ler(corpo)

    P["map"](ler, range(6), 6)
    assert pico.valor() > 1, "os leitores foram serializados"


# ═══ Canal ═════════════════════════════════════════════════

def test_canal_bloqueia_ate_chegar():
    """O 'channel' da linguagem devolve void na hora; o consumidor
    precisava girar num laco perguntando."""
    canal = P["canal"]()

    def produtor():
        time.sleep(0.05)
        canal.enviar("chegou")

    P["rodar"](produtor)
    inicio = time.perf_counter()
    assert canal.receber() == "chegou"
    assert time.perf_counter() - inicio >= 0.04, "não esperou"


def test_canal_fechado_encerra_o_percurso():
    canal = P["canal"]()

    def produtor():
        for i in range(3):
            canal.enviar(i)
        canal.fechar()

    P["rodar"](produtor)
    assert list(canal) == [0, 1, 2]


def test_enviar_em_canal_fechado_e_recusado():
    canal = P["canal"]()
    canal.fechar()
    with pytest.raises(ConcurrencyError):
        canal.enviar(1)


def test_canal_com_prazo_desiste():
    canal = P["canal"]()
    with pytest.raises(TimeoutError_):
        canal.receber(prazo=0.05)


def test_tentar_receber_nao_espera():
    canal = P["canal"]()
    assert canal.tentar_receber() is None
    canal.enviar(7)
    assert canal.tentar_receber() == 7


# ═══ Tarefas e grupos ══════════════════════════════════════

def test_tarefa_guarda_o_resultado():
    t = P["rodar"](lambda: 6 * 7)
    assert t.esperar() == 42
    assert t.pronta()
    assert t.erro() is None


def test_tarefa_guarda_o_erro_sem_levantar():
    t = P["rodar"](lambda: (_ for _ in ()).throw(ValueError("falhou")))
    time.sleep(0.05)
    assert t.erro() is not None
    with pytest.raises(ValueError):
        t.esperar()


def test_grupo_espera_todas_e_mantem_a_ordem():
    with P["grupo"](4) as g:
        g.rodar(lambda: 1)
        g.rodar(lambda: 2)
        g.rodar(lambda: 3)
        assert g.esperar_todas() == [1, 2, 3]


def test_grupo_relata_sem_levantar():
    g = P["grupo"](2)
    g.rodar(lambda: "ok")
    g.rodar(lambda: (_ for _ in ()).throw(ValueError("x")))
    time.sleep(0.05)
    estados = [r["estado"] for r in g.resultados()]
    assert "ok" in estados and "erro" in estados
    g.fechar()


def test_esperar_primeira():
    with P["grupo"](3) as g:
        lenta = g.rodar(lambda: (time.sleep(0.3), "lenta")[1])
        rapida = g.rodar(lambda: "rápida")
        assert P["esperar_primeira"]([lenta, rapida], prazo=1) == "rápida"


# ═══ para_cada e lotes ═════════════════════════════════════

def test_para_cada_segue_depois_do_erro():
    """Para efeito colateral em lote, parar na primeira falha costuma
    ser pior que seguir e relatar."""
    def acao(x):
        if x % 2 == 0:
            raise ValueError(f"par: {x}")
        return x

    r = P["para_cada"](acao, range(10), 5)
    assert r["ok"] == 5
    assert len(r["erros"]) == 5


def test_lotes_agrupa_antes_de_chamar():
    """Mil itens em lotes de cem custam dez chamadas, não mil."""
    chamadas = P["contador"](0)

    def acao(lote):
        chamadas.somar()
        return sum(lote)

    total = sum(P["lotes"](acao, range(100), 10, 4))
    assert total == sum(range(100))
    assert chamadas.valor() == 10


# ═══ Prazo ═════════════════════════════════════════════════

def test_com_prazo_nao_prende_quem_chamou():
    inicio = time.perf_counter()
    with pytest.raises(TimeoutError_) as exc:
        P["com_prazo"](lambda: time.sleep(2), 0.1)
    assert time.perf_counter() - inicio < 0.5
    # A mensagem tem de ser honesta sobre o que o prazo garante.
    assert "background" in exc.value.nota


def test_com_prazo_deixa_passar_o_que_cabe():
    assert P["com_prazo"](lambda: 42, 1) == 42


def test_repetir_a_cada_e_para_quando_mandam():
    contagem = P["contador"](0)
    ctrl = P["repetir_a_cada"](lambda: contagem.somar(), 0.02)
    time.sleep(0.12)
    ctrl["parar"]()
    parou_em = contagem.valor()
    time.sleep(0.08)
    assert contagem.valor() == parou_em, "continuou depois de parar"
    assert parou_em >= 2


# ═══ Processos ═════════════════════════════════════════════

def _quadrado(n):
    """No topo do módulo: uma closure não atravessa para outro processo."""
    return n * n


def test_map_processos_calcula_certo():
    assert P["map_processos"](_quadrado, [1, 2, 3, 4], 2) == [1, 4, 9, 16]


def test_map_processos_explica_o_que_nao_atravessa():
    """Uma lambda local não pode ser serializada — e a mensagem tem de
    dizer isso, não 'cannot pickle'."""
    with pytest.raises(ConcurrencyError) as exc:
        P["map_processos"](lambda x: x, [1, 2])
    assert "another process" in str(exc.value)
    assert "top level" in exc.value.dica


# ═══ Informacao ════════════════════════════════════════════

def test_nucleos_e_thread_atual():
    assert P["nucleos"]() >= 1
    atual = P["thread_atual"]()
    assert atual["principal"] is True
    assert P["sou_principal"]() is True
